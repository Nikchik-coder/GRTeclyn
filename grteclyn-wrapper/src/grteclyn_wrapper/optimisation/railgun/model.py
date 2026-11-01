"""Canonical Einstein--Klein--Gordon model and regular scalar source terms.

G=c=1, signature -+++, chi=sqrt(4*pi)*phi. The action is
(16*pi)^-1 integral sqrt(-g) [R-2 sum(|d chi|^2+U)] d^4x.
Thus R_ab=2 sum Re(d_a chi d_b chi*)+sum(U) g_ab and
box chi=(dU/d|chi|)/(2|chi|) chi. Independent fields do not interfere.

The quasi-isotropic metric is -exp(f)dt^2+B^2 exp(-f)[exp(nu)
(dr^2+r^2 dtheta^2)+r^2 sin^2(theta)(dphi-w dt)^2], nu=N sin^2(theta).
Amplitude A=sin^abs(k)(theta)*cos^parity(theta)*q(r,cos(2theta)).
The parity factor is differentiated analytically, including its equatorial
limit. The regular q has neither a centrifugal nor a parity singularity.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math


@dataclass(frozen=True)
class ScalarField:
    winding: int = 1
    mass: float = 1.0
    amplitude: float = 0.05
    parity: str = 'even'
    anchor_radius: float = 5.0
    quartic: float = 0.0
    sextic: float = 0.0

    def __post_init__(self):
        if isinstance(self.winding, bool) or int(self.winding) != self.winding:
            raise ValueError('winding must be an integer')
        if self.parity not in ('even', 'odd'):
            raise ValueError('parity must be even or odd')
        for key in ('mass', 'amplitude', 'anchor_radius'):
            if not math.isfinite(getattr(self, key)) or getattr(self, key) <= 0:
                raise ValueError(f'{key} must be finite and positive')
        for key in ('quartic', 'sextic'):
            if not math.isfinite(getattr(self, key)) or getattr(self, key) < 0:
                raise ValueError(f'{key} must be finite and nonnegative')

    @property
    def degree(self):
        return abs(self.winding) + int(self.parity == 'odd')

    def to_dict(self):
        return asdict(self)


def exprel(x, xp):
    """(exp(x)-1)/x with a differentiable, cancellation-free zero limit."""
    small = xp.abs(x) < 1e-5
    safe = xp.where(small, 1., x)
    series = 1+x/2+x*x/6+x**3/24+x**4/120
    return xp.where(small, series, xp.expm1(safe)/safe)


def canonical_rows(jets, fields, frequencies, *, r, dr, ddr, y, xp):
    """Four metric equations, each regular KG equation and two unused constraints.

    Vacuum rows are the already derived general quasi-isotropic equations at
    eta0=0. Canonical sources are added field by field. z*q products below
    denote z=cos(theta)*q for odd parity; combinations are polynomial in y.
    No products of different scalar fields occur.
    """
    from ..matter_equations import MATTER_JET_NAMES, matter_residual_forms
    full = {name: xp.zeros_like(jets['f']) for name in MATTER_JET_NAMES}
    full.update(jets)
    base = matter_residual_forms(xp.exp, eta0=0., eta=r, deta=dr,
                                d2eta=ddr, y=y, jets=full, V=0., dV=0.)
    out = {key: base[key] for key in ('E_f', 'E_w', 'E_B', 'E_Nr', 'E_c', 'E19')}
    f, w, n, b = (jets[t] for t in ('f', 'w', 'N', 'B'))
    sk, oy = (1-y)/2, 1-y*y
    nu = n*sk
    env, enu, ef = xp.exp(nu-f), xp.exp(nu), xp.exp(-f)
    a2, a1 = r*r/dr**2, 2*r/dr-r*r*ddr/dr**3
    w2 = (r*r/dr)**2
    bx, by = jets['B_x']/b, jets['B_y']/b
    for index, (field, frequency) in enumerate(zip(fields, frequencies)):
        tag = f'q{index}'
        q, qx, qxx, qy, qyy = (jets[tag+s] for s in ('', '_x', '_xx', '_y', '_yy'))
        k, ka = field.winding, abs(field.winding)
        odd = field.parity == 'odd'
        p2 = (1+y)/2 if odd else xp.ones_like(y)
        skk = sk**ka
        skm = sk**(ka-1) if ka else xp.zeros_like(y)
        zz = p2*q*q
        zzx = p2*q*qx
        zzy = p2*q*qy + (q*q/4 if odd else 0.)
        zxzy = p2*qx*qy + (q*qx/4 if odd else 0.)
        oyzy2 = p2*oy*qy*qy
        ypzy2 = p2*(1+y)*qy*qy
        if odd:
            oyzy2 = oyzy2 + oy*q*qy/2 + (1-y)*q*q/8
            ypzy2 = ypzy2 + (1+y)*q*qy/2 + q*q/8
        amp2 = skk*zz
        potential = field.mass**2*amp2+field.quartic*amp2**2+field.sextic*amp2**3
        mass_eff = field.mass**2+2*field.quartic*amp2+3*field.sextic*amp2**2
        om = frequency+k*w
        harmonic = om*om*ef*amp2
        out['E_f'] = out['E_f'] - 2*(-potential+2*harmonic)*b*b*r*r*env
        out['E_w'] = out['E_w'] - 4*k*om*enu*skm*zz
        out['E_B'] = out['E_B'] - 2*(-potential+harmonic)*b**3*r*r*env+2*k*k*skm*zz*b*enu
        out['E_Nr'] = (out['E_Nr']+16*skk*ypzy2-8*ka*(1+y)*skm*zzy
                        -2*k*k*skm*zz*(1+n*exprel(nu, xp)))
        out['E_c'] = out['E_c']+16*skk*zxzy-4*ka*skm*zzx
        out['E19'] = (out['E19']+w2*skk*p2*qx*qx-4*r*r*skk*oyzy2
                      +2*ka*r*r*oy*skm*zzy-k*k*r*r*(1+y)*skm*zz/2)
        ell = ka+int(odd)
        # Parity changes the angular indicial degree ka -> ka+1.
        angular_first = ((4*ka+10)*y+4*ka-2 if odd
                         else (4*ka+6)*y+4*ka+2)
        parity_b = 2*(1-y)*by*q if odd else 0.
        out[f'E_q{index}'] = (
            a2*(qxx+bx*qx)+a1*qx+4*oy*qyy-angular_first*qy
            +4*oy*by*qy-ell*(ell+1)*q-2*ka*(1+y)*by*q+parity_b
            -k*k*n*exprel(nu, xp)*q+(om*om*ef-mass_eff)*b*b*r*r*env*q)
    return out
