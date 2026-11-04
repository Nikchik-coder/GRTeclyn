"""Differentiable Cartesian metric and independent curvature reconstruction.

No cylindrical coordinate singularity is evaluated on the rotation axis.
The interpolation is defined for r>0: exact-origin curvature is deliberately
excluded until its regular Taylor limit is demonstrated for a saved solution.
R^a_bcd = d_c Gamma^a_bd - d_d Gamma^a_bc + Gamma^a_ec Gamma^e_bd
          - Gamma^a_ed Gamma^e_bc; Ricci_bd=R^a_bad.
"""
from __future__ import annotations

import numpy as np

from .model import exprel
from ..solver.device import configure_jax


def interpolation_coefficients(values):
    """DCT-I coefficients without high-mode cosine-matrix cancellation.

    Extended precision keeps the transform error below the float64 input
    noise. This matters for Cartesian curvature near a regular origin:
    an artificial constant in N is divided by r squared twice by AD.
    """
    from scipy.fft import dct
    coefficients = np.asarray(values, dtype=np.longdouble)
    for axis in (0, 1):
        coefficients = dct(coefficients, type=1, axis=axis)/(coefficients.shape[axis]-1)
        end = [slice(None)]*coefficients.ndim
        end[axis] = [0, -1]
        coefficients[tuple(end)] *= .5
    return np.asarray(coefficients, dtype=float)


def chebyshev_basis(x, degree, xp):
    values = [xp.ones_like(x), x]
    for _ in range(2, degree+1):
        values.append(2*x*values[-1]-values[-2])
    return xp.stack(values[:degree+1])


def connection(metric, jax):
    xp = jax.numpy
    derivative = jax.jacfwd(metric)

    def gamma(x):
        dg = derivative(x)
        terms = dg.transpose(0, 2, 1)+dg-dg.transpose(2, 0, 1)
        return .5*xp.einsum('ad,dbc->abc', xp.linalg.inv(metric(x)), terms)
    return gamma


def curvature(metric, jax):
    """Return a differentiable function yielding (g, Gamma, Riemann, Ricci)."""
    xp = jax.numpy
    gamma = connection(metric, jax)
    derivative = jax.jacfwd(gamma)

    def tensors(x):
        gam = gamma(x)
        dg = derivative(x)
        riem = (dg.transpose(0, 1, 3, 2)-dg
                +xp.einsum('aec,ebd->abcd', gam, gam)
                -xp.einsum('aed,ebc->abcd', gam, gam))
        return metric(x), gam, riem, xp.einsum('abad->bd', riem)
    return tensors


class RingGeometry:
    def __init__(self, problem, u):
        self.jax = configure_jax()
        self.xp = self.jax.numpy
        self.length, self.fields = problem.length, problem.fields
        arrays, freq = problem.unpack(np.asarray(u))
        self.frequencies = np.asarray(freq)
        self.coefficients = {key: self.xp.asarray(interpolation_coefficients(a))
                             for key, a in arrays.items()}
        self.dragging_h = None
        if getattr(problem,'canonical_archive',False):
            # H is already spectral in radius; transform only its angular
            # nodal axis. Retain the exact higher-degree physical polynomial
            # for the long-double core fit, and evaluate the tail factored.
            from scipy.fft import dct
            h = dct(np.asarray(problem.raw_dragging(np.asarray(u)),dtype=np.longdouble),
                    type=1,axis=1)/problem.ny
            h[:,[0,-1]] *= .5
            w = np.zeros((problem.nx+4,problem.ny+1),dtype=np.longdouble)
            for j in range(problem.ny+1):
                product = np.polynomial.chebyshev.chebmul([2.5,-3.75,1.5,-.25],h[:,j])
                w[:len(product),j] = product
            self.dragging_h = self.xp.asarray(np.asarray(h,dtype=float))
            self.coefficients['w'] = self.xp.asarray(np.asarray(w,dtype=float))
        self.nx, self.ny = problem.nx, problem.ny
        self.metric = self.jax.jit(self._metric)
        self.tensors = self.jax.jit(curvature(self._metric, self.jax))
        self._einstein = self.jax.jit(self._independent)
        self._intrinsic_jit = self.jax.jit(self._intrinsic_kg)

    def sample(self, name, s, y):
        xp = self.xp
        coefficients = self.coefficients[name]
        factor = 1.
        if name == 'w' and self.dragging_h is not None:
            coefficients = self.dragging_h
            factor = (1-s)**3
        return factor*xp.einsum('i,ij,j->', chebyshev_basis(s, coefficients.shape[0]-1, xp),
                         coefficients, chebyshev_basis(y, coefficients.shape[1]-1, xp))

    def _coordinates(self, x):
        xp = self.xp
        r2 = xp.sum(x[1:]**2)
        r = xp.sqrt(r2)
        return r2, r, (r-self.length)/(r+self.length), 2*x[3]**2/r2-1

    def _metric(self, x):
        xp = self.xp
        r2, r, s, y = self._coordinates(x)
        f, w, n, b = (self.sample(key, s, y) for key in ('f', 'w', 'N', 'b'))
        rho2 = x[1]**2+x[2]**2
        nu = n*rho2/r2
        c = (1+b)**2*xp.exp(-f)
        a = c*xp.exp(nu)
        v = xp.array([-x[2], x[1], 0.])
        # (C-A)/rho^2 = -C*N/r^2*exprel(nu), finite on the axis.
        spatial = a*xp.eye(3)-c*n/r2*exprel(nu, xp)*xp.outer(v, v)
        g = xp.zeros((4, 4))
        g = g.at[0, 0].set(-xp.exp(f)+c*w*w*rho2)
        g = g.at[0, 1:].set(-c*w*v)
        g = g.at[1:, 0].set(-c*w*v)
        return g.at[1:, 1:].set(spatial)

    def scalar(self, x, index):
        xp = self.xp
        field = self.fields[index]
        r2, r, s, y = self._coordinates(x)
        amp = self.sample(f'q{index}', s, y)
        if field.parity == 'odd':
            amp = amp*x[3]/r
        # sin^|k|(theta) exp(i k phi)=[(x+i sign(k)y)/r]^|k|.
        # This Cartesian polynomial is differentiable on the axis too.
        real, imag = xp.ones(()), xp.zeros(())
        bx, by = x[1]/r, (1 if field.winding >= 0 else -1)*x[2]/r
        for _ in range(abs(field.winding)):
            real, imag = real*bx-imag*by, real*by+imag*bx
        phase = self.frequencies[index]*x[0]
        return amp*xp.array([real*xp.cos(phase)-imag*xp.sin(phase),
                             real*xp.sin(phase)+imag*xp.cos(phase)])

    def _independent(self, x):
        xp = self.xp
        g, gam, riem, ricci = self.tensors(x)
        source = xp.zeros((4, 4))
        kg = []
        for i, field in enumerate(self.fields):
            scalar = lambda point: self.scalar(point, i)
            value = scalar(x)
            first = self.jax.jacfwd(scalar)(x)
            second = self.jax.jacfwd(self.jax.jacfwd(scalar))(x)
            amp2 = xp.sum(value**2)
            pot = field.mass**2*amp2+field.quartic*amp2**2+field.sextic*amp2**3
            eff = field.mass**2+2*field.quartic*amp2+3*field.sextic*amp2**2
            source = source+2*first.T@first+pot*g
            hess = second-xp.einsum('cab,ic->iab', gam, first)
            kg.append(xp.einsum('ab,iab->i', xp.linalg.inv(g), hess)-eff*value)
        return ricci-source, xp.stack(kg) if kg else xp.zeros((0, 2))

    def _intrinsic_kg(self, rt):
        """Covariant divergence-form KG in (r,theta), independent of Cartesian AD."""
        xp = self.xp
        def local(coords):
            r,theta = coords
            s=(r-self.length)/(r+self.length)
            y=xp.cos(2*theta)
            return tuple(self.sample(t,s,y) for t in ('f','w','N','b'))
        r,theta=rt
        f,w,n,b=local(rt);b=1+b
        determinant=b**3*xp.exp(n*xp.sin(theta)**2-f)*r*r*xp.sin(theta)
        rows=[]
        for i,field in enumerate(self.fields):
            def amplitude(coords):
                rr,th=coords
                q=self.sample(f'q{i}',(rr-self.length)/(rr+self.length),xp.cos(2*th))
                return q*xp.sin(th)**abs(field.winding)*(xp.cos(th) if field.parity=='odd' else 1.)
            def flux(coords):
                rr,th=coords
                bb=1+local(coords)[3]
                gradient=self.jax.jacfwd(amplitude)(coords)
                return bb*xp.sin(th)*xp.array([rr*rr*gradient[0],gradient[1]])
            derivative=self.jax.jacfwd(flux)(rt)
            a=amplitude(rt)
            effective=field.mass**2+2*field.quartic*a*a+3*field.sextic*a**4
            harmonic=((self.frequencies[i]+field.winding*w)**2*xp.exp(-f)
                      -field.winding**2*xp.exp(f)/(b*b*r*r*xp.sin(theta)**2))
            rows.append((derivative[0,0]+derivative[1,1])/determinant+(harmonic-effective)*a)
        return xp.stack(rows) if rows else xp.zeros(0)

    def independent(self, point):
        point = np.asarray(point, dtype=float)
        if (point.shape != (4,) or not np.isfinite(point).all()
                or (np.linalg.norm(point[1:]) == 0 and not getattr(self,'regular_origin',False))):
            raise ValueError('a finite Cartesian point away from the origin is required')
        e, kg = self._einstein(self.xp.asarray(point))
        # Cartesian orthonormal projection, independent of collocation row weights.
        g = np.asarray(self.metric(point))
        alpha = np.sqrt(-1/np.linalg.inv(g)[0, 0])
        beta = np.linalg.solve(g[1:, 1:], g[0, 1:])
        tetrad = np.zeros((4, 4))
        tetrad[0] = np.r_[1., -beta]/alpha
        tetrad[1:, 1:] = np.linalg.inv(np.linalg.cholesky(g[1:, 1:]))
        orth = tetrad@np.asarray(e)@tetrad.T
        result=dict(einstein_max=float(np.max(np.abs(orth))),
                    kg_max=float(np.max(np.abs(kg))) if np.size(kg) else 0.)
        rho=np.hypot(point[1],point[2]);r=np.linalg.norm(point[1:])
        if self.fields and rho > 0:
            theta=np.arctan2(rho,abs(point[3]))
            intrinsic=np.asarray(self._intrinsic_jit(self.xp.asarray([r,theta])))
            phase=self.frequencies*point[0]+np.array([f.winding for f in self.fields])*np.arctan2(point[2],point[1])
            # Negative-z odd parity changes the signed amplitude too.
            signs=np.array([-1. if point[3]<0 and f.parity=='odd' else 1. for f in self.fields])
            predicted=intrinsic[:,None]*signs[:,None]*np.stack([np.cos(phase),np.sin(phase)],axis=1)
            result.update(kg_intrinsic_max=float(np.max(abs(intrinsic))),
                          kg_coordinate_difference=float(np.max(abs(np.asarray(kg)-predicted))))
        return result
