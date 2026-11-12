"""Regular-centre boundary rows with independent canonical validation.

GPU-tested boundary correction. Three-grid source and Cartesian centre
qualification are required separately before a field can be evolved.

The N equation admits a local homogeneous N~r mode. N(0)=0 alone does
not exclude it, although Cartesian regularity requires N=O(r^2). Use
N_r(0)=0 and check N(0)=0 independently. For scalar metric potentials,
fix the nonconstant angular origin modes to zero and impose the mean
radial Neumann condition. All interior Einstein/KG rows are retained.
The saved vector still contains the original physical nodal fields.
"""
from __future__ import annotations

import numpy as np

from grteclyn_stationary.railgun.problem import RingProblem


def centred_jets(arrays, dx, dxx, dy, dyy):
    """Differentiate corrections, removing exact constants before products."""
    result = {}
    for name, values in arrays.items():
        key = 'B' if name == 'b' else name
        radial = values-values[-1:]
        angular = values-values[:, -1:]
        for suffix, value in (
            ('',values+1 if name == 'b' else values),
            ('_x',dx@radial), ('_xx',dxx@radial),
            ('_y',angular@dy.T), ('_yy',angular@dyy.T),
        ):
            result[key+suffix] = value[1:-1]
    angular_b = arrays['b']-arrays['b'][:, -1:]
    result['B_xy'] = (dx@(angular_b-angular_b[-1:])@dy.T)[1:-1]
    return result


def origin_rows(values, derivative, *, anisotropy=False, xp=np):
    """Zero nonconstant angular value modes, and one mean Neumann row.

    Taking the angular mean of these rows gives mean(derivative)=0;
    subtracting it gives values[-1]-mean(values[-1])=0. No equation
    is discarded or added. N instead uses the full Neumann vector.
    """
    if anisotropy:
        offset = values[-1:]-values[-1:, -1:]
        return offset-xp.mean(offset)+xp.mean(derivative[-1:])
    return derivative[-1:]


class SmoothOriginProblem(RingProblem):
    discretisation = 'isotropic_metric_origin_neumann_N_v1'

    def jets(self, arrays, xp=np):
        return centred_jets(arrays, self.dx, self.dxx, self.dy, self.dyy)

    def _residual(self, u):
        xp = self.xp
        result = super()._residual(u)
        arrays, _ = self.unpack(u)
        for index, name in enumerate(self.tags):
            if name.startswith('q'):
                continue
            values = arrays[name]
            derivative = self.dx@(values-values[-1:])
            rows = origin_rows(values,derivative,anisotropy=name != 'N',xp=xp)
            start = (index+1)*self.n-(self.ny+1)
            result = result.at[start:start+self.ny+1].set(rows.ravel())
        return result


def physical_origin_checks(problem, state):
    """Check all regularity requirements, including those not imposed."""
    arrays, _ = problem.unpack(np.asarray(state))
    dr_ds = problem.length/2
    metric = ('f','w','N','b')
    slopes = {name: float(np.max(abs((problem.dx@(arrays[name]-arrays[name][-1:]))[-1]))/dr_ds)
              for name in metric}
    spreads = {name: float(np.ptp(arrays[name][-1])) for name in ('f','w','b')}
    n0 = float(np.max(abs(arrays['N'][-1])))
    q0 = {name:float(np.max(abs(values[-1]))) for name,values in arrays.items()
          if name.startswith('q') and problem.fields[int(name[1:])].degree}
    return dict(metric_radial_slopes=slopes,metric_angular_spreads=spreads,
                N_at_origin=n0,vanishing_scalars=q0,
                maximum=max([n0]+list(slopes.values())+list(spreads.values())+list(q0.values())))
