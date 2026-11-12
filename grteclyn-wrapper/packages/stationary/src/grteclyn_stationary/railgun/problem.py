"""One-ended regular-centre collocation; no phantom field or throat boundary.

r=L(1+s)/(1-s), s in [-1,1], y=cos(2theta). Only interior radial
rows evaluate the PDE; infinity and the centre have their own boundary rows.
Angular factors encode regularity and parity, so the regular PDE is evaluated
at axis and equator too. Every field adds one amplitude border and frequency.
A total-J condition adds one unknown log amplitude of the final field.
"""
from __future__ import annotations

import numpy as np

from grteclyn_stationary.railgun.model import canonical_rows
from grteclyn_stationary.numerics.device import configure_jax
from grteclyn_stationary.numerics.jacobian import dense_jacobian
from grteclyn_stationary.numerics.spectral import cheb_eval
from grteclyn_stationary.numerics.spectral import lobatto


class RingProblem:
    def __init__(self, fields=(), *, nx=32, ny=8, length=6., target_j=None, quadrature_order=None,
                 frequency_targets=None, central_lapse=None):
        self.fields = tuple(fields)
        self.frequency_targets=tuple(frequency_targets) if frequency_targets is not None else (None,)*len(fields)
        self.central_lapse = central_lapse
        if central_lapse is not None:
            if (len(fields) != 1 or target_j is not None
                    or any(value is not None for value in self.frequency_targets)
                    or not np.isfinite(central_lapse) or not 0 < central_lapse < 1):
                raise ValueError('central lapse control requires one field, no other border, and 0<lapse<1')
        if len(self.frequency_targets)!=len(fields):raise ValueError('one frequency target per field required')
        if any(value is not None for value in self.frequency_targets):
            if len(fields)!=1 or target_j is not None:
                raise ValueError('frequency control currently requires one field and no total-J border')
            if any(value is not None and (not np.isfinite(value) or not 0<value<field.mass)
                   for value,field in zip(self.frequency_targets,fields)):
                raise ValueError('fixed frequency must lie strictly between zero and field mass')
        if isinstance(nx, bool) or int(nx) != nx or nx < 6:
            raise ValueError('nx must be an integer >= 6')
        if isinstance(ny, bool) or int(ny) != ny or ny < 3:
            raise ValueError('ny must be an integer >= 3')
        if not np.isfinite(length) or length <= 0:
            raise ValueError('length must be finite and positive')
        if target_j is not None:
            if len(fields) < 2 or not np.isfinite(target_j):
                raise ValueError('target_j needs at least two fields and a finite target')
            if target_j == 0 and not (any(f.winding > 0 for f in fields)
                                       and any(f.winding < 0 for f in fields)):
                raise ValueError('zero total J needs opposite winding signs')
        self.nx, self.ny, self.length, self.target_j = int(nx), int(ny), float(length), target_j
        self.s, self.dx = lobatto(self.nx)
        self.y, self.dy = lobatto(self.ny)
        self.dxx, self.dyy = self.dx@self.dx, self.dy@self.dy
        self.shape = (self.nx+1, self.ny+1)
        self.n = int(np.prod(self.shape))
        self.tags = ('f', 'w', 'N', 'b')+tuple(f'q{i}' for i in range(len(fields)))
        self.n_unknowns = len(self.tags)*self.n+len(fields)+int(target_j is not None)
        self.r = np.empty(self.nx+1)
        self.r[0] = np.inf
        self.r[1:] = self.length*(1+self.s[1:])/(1-self.s[1:])
        si = self.s[1:-1, None]
        self.ri = self.length*(1+si)/(1-si)
        self.dr = 2*self.length/(1-si)**2
        self.ddr = 4*self.length/(1-si)**3
        self.anchors = [cheb_eval(self.s, np.eye(self.nx+1),
                        np.array([(f.anchor_radius-self.length)/(f.anchor_radius+self.length)]))[0]
                        for f in fields]
        # Positive quadrature weights; neither compactified endpoint is sampled.
        nr, nm = quadrature_order or (max(48, 2*self.nx), max(24, 2*self.ny))
        self.quadrature_order = (nr, nm)
        sg, wg = np.polynomial.legendre.leggauss(nr)
        mg, wm = np.polynomial.legendre.leggauss(nm)
        self.mg, self.wm = (mg+1)/2, wm/2
        self.rg = self.length*(1+sg)/(1-sg)
        self.wr = wg*2*self.length/(1-sg)**2
        self.qx = cheb_eval(self.s, np.eye(self.nx+1), sg)
        self.qy = cheb_eval(self.y, np.eye(self.ny+1), 2*self.mg**2-1)
        self.jax = configure_jax()
        self.xp = self.jax.numpy
        self.residual = self.jax.jit(self._residual)
        self.jacobian = dense_jacobian(self.residual, self.n_unknowns)

    def unpack(self, u):
        arrays = {tag: u[i*self.n:(i+1)*self.n].reshape(self.shape)
                  for i, tag in enumerate(self.tags)}
        start = len(self.tags)*self.n
        frequencies = u[start:start+len(self.fields)]
        return arrays, frequencies

    def jets(self, arrays, xp=np):
        jets = {}
        for tag, a in arrays.items():
            tag = 'B' if tag == 'b' else tag
            # Derivatives of the correction avoid cancellation on B=1.
            for suffix, value in (('', a+1 if tag == 'B' else a),
                                  ('_x', self.dx@a), ('_xx', self.dxx@a),
                                  ('_y', a@self.dy.T), ('_yy', a@self.dyy.T)):
                jets[tag+suffix] = value[1:-1]
        jets['B_xy'] = (self.dx@arrays['b']@self.dy.T)[1:-1]
        return jets

    def rows(self, u, xp=np):
        arrays, frequencies = self.unpack(u)
        return canonical_rows(self.jets(arrays, xp), self.fields, frequencies,
                              r=self.ri, dr=self.dr, ddr=self.ddr,
                              y=self.y[None, :], xp=xp)

    def charge_integrals(self, u, xp=np):
        arrays, frequencies = self.unpack(u)
        sample = lambda a: self.qx@a@self.qy.T
        f, w, n, b = (sample(arrays[t]) for t in ('f', 'w', 'N', 'b'))
        b = 1+b
        sk = 1-self.mg[None, :]**2
        measure = (self.wr[:, None]*self.wm[None, :]*self.rg[:, None]**2
                   *b**3*xp.exp(n*sk-2*f))
        charges = []
        for i, (field, frequency) in enumerate(zip(self.fields, frequencies)):
            amp2 = sk**abs(field.winding)*sample(arrays[f'q{i}'])**2
            if field.parity == 'odd':
                amp2 = amp2*self.mg[None, :]**2
            charges.append(xp.sum(measure*(frequency+field.winding*w)*amp2))
        return xp.stack(charges) if charges else xp.zeros(0)

    def _residual(self, u):
        xp = self.xp
        arrays, frequencies = self.unpack(u)
        rows = self.rows(u, xp)
        blocks = []
        for tag in self.tags:
            a = arrays[tag]
            if tag.startswith('q'):
                field = self.fields[int(tag[1:])]
                origin = a[-1:] if field.degree else (self.dx@a)[-1:]
            else:
                origin = a[-1:] if tag == 'N' else (self.dx@a)[-1:]
            key = {'f': 'E_f', 'w': 'E_w', 'N': 'E_Nr', 'b': 'E_B'}.get(tag, f'E_{tag}')
            blocks.append(xp.concatenate((a[:1], rows[key], origin)).ravel())
        for i, field in enumerate(self.fields):
            if self.central_lapse is not None:
                # Subtract first: averaging 33 equal nonzero values can lose
                # one ulp, amplified by 33 during Jacobian row equilibration.
                blocks.append(xp.atleast_1d(xp.mean(arrays['f'][-1, :]-2*xp.log(self.central_lapse))))
                continue
            if self.frequency_targets[i] is not None:
                blocks.append(xp.atleast_1d(frequencies[i]-self.frequency_targets[i]))
                continue
            held = self.anchors[i]@arrays[f'q{i}'][:, -1]
            # q is the parity-factored amplitude, including for an odd field.
            amp = (xp.exp(u[-1]) if self.target_j is not None and i == len(self.fields)-1
                   else field.amplitude)
            blocks.append(xp.atleast_1d(held-amp))
        if self.target_j is not None:
            charges = self.charge_integrals(u, xp)
            total = sum(-f.winding*charges[i] for i, f in enumerate(self.fields))
            blocks.append(xp.atleast_1d(total-self.target_j))
        return xp.concatenate(blocks)

    def seed(self):
        arrays = {tag: np.zeros(self.shape) for tag in self.tags}
        finite_r = self.r[1:, None]
        strength = sum(f.amplitude for f in self.fields)
        arrays['f'][1:] = -4*strength/np.sqrt(1+(finite_r/self.length)**2)
        arrays['b'][1:] = -strength**2/(1+(finite_r/self.length)**2)
        frequencies = []
        for i, field in enumerate(self.fields):
            width, ell = field.anchor_radius, field.degree
            radial = (finite_r/width)**ell*np.exp(-(finite_r/width)**2/2+.5)
            arrays[f'q{i}'][1:] = field.amplitude*radial*np.ones((1, self.ny+1))
            frequencies.append(field.mass*(1-min(.2, 2*field.amplitude)))
        return self.pack(arrays, frequencies)

    def pack(self, arrays, frequencies):
        if set(arrays) != set(self.tags) or any(np.shape(arrays[t]) != self.shape for t in self.tags):
            raise ValueError('field arrays must match problem tags and grid')
        if len(frequencies) != len(self.fields):
            raise ValueError('one frequency per scalar field is required')
        parts = [np.asarray(arrays[t]).ravel() for t in self.tags]+[np.asarray(frequencies)]
        if self.target_j is not None:
            parts.append(np.array([np.log(self.fields[-1].amplitude)]))
        return np.concatenate(parts)

    def transfer(self, old, u, *, perturb=0.):
        arrays, frequencies = old.unpack(np.asarray(u))
        bx = cheb_eval(old.s, np.eye(old.nx+1), self.s)
        by = cheb_eval(old.y, np.eye(old.ny+1), self.y)
        new = {t: bx@a@by.T for t, a in arrays.items()}
        if perturb:
            shape = ((1-self.s[:, None]**2)**2*(1-self.y[None, :]**2)**2)
            for tag in ('f', 'w', 'N', 'b'):
                new[tag] = new[tag]+perturb*shape
        out = self.pack(new, frequencies)
        if self.target_j is not None:
            out[-1] = u[-1]
        return out
