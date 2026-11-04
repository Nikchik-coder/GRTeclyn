"""Regular centre plus explicitly cubic dragging decay, with every PDE retained.

Newton solves for Chebyshev coefficients of H where w=(1-s)^3 H.
The angular/null-mode conditions at infinity determine its smooth falloff;
angular momentum remains free and is measured independently, never imposed.
Archives retain both the physical nodal fields and the exact solver coordinates.
"""
from __future__ import annotations

import numpy as np

from .model import canonical_rows
from .problem import RingProblem
from .regular_dragging import RegularDraggingProblem
from .smooth_origin import centred_jets, origin_rows, physical_origin_checks

REPRESENTATION = 'dragging_cubic_smooth_origin_v1'


class SmoothCubicProblem(RegularDraggingProblem):
    discretisation = REPRESENTATION
    canonical_archive = True

    def __init__(self,*args,**kwargs):
        super().__init__(*args,power=3,**kwargs)
        self.representation = REPRESENTATION

    def jets(self,arrays,xp=np):
        return centred_jets(arrays,self.dx,self.dxx,self.dy,self.dyy)

    def rows(self,u,xp=np):
        arrays,frequencies = self.unpack(u)
        jets = self.jets(arrays,xp)
        jets.update({key:value[1:-1] for key,value in self.dragging_jets(u,xp).items()})
        return canonical_rows(jets,self.fields,frequencies,r=self.ri,dr=self.dr,
                              ddr=self.ddr,y=self.y[None,:],xp=xp)

    def _residual(self,u):
        xp = self.xp
        result = super()._residual(u)
        arrays,_ = self.unpack(u)
        for index,name in enumerate(self.tags):
            if name.startswith('q'):
                continue
            values = arrays[name]
            derivative = (self.dragging_jets(u,xp)['w_x'] if name=='w'
                          else self.dx@(values-values[-1:]))
            rows = origin_rows(values,derivative,anisotropy=name!='N',xp=xp)
            start = (index+1)*self.n-self.ny-1
            result = result.at[start:start+self.ny+1].set(rows.ravel())
        return result

    def physical_vector(self,u):
        arrays,frequencies = self.unpack(np.asarray(u))
        base = RingProblem(self.fields,nx=self.nx,ny=self.ny,length=self.length,
                           target_j=self.target_j,frequency_targets=self.frequency_targets,
                           central_lapse=self.central_lapse)
        return base,base.pack(arrays,frequencies)

    def transfer(self,old,u,*,perturb=0.):
        # Preserve H during refinement; perturb the other metric potentials
        # rather than refitting an already determined, tiny physical w tail.
        result = super().transfer(old,u,perturb=0.)
        if perturb:
            shape = ((1-self.s[:,None]**2)**2*(1-self.y[None,:]**2)**2).ravel()
            for index in (0,2,3):
                result[index*self.n:(index+1)*self.n] += perturb*shape
        return result


def validate(problem,u,info,*,equation_tol=1e-8,tail_tol=1e-6):
    from .dragging_falloff import validate as factored_validate
    result = factored_validate(problem,u,info,equation_tol=equation_tol,tail_tol=tail_tol)
    origin = physical_origin_checks(problem,u)
    result['origin_regularity'] = origin
    if not np.isfinite(origin['maximum']) or origin['maximum'] > equation_tol:
        result['reasons'].append('physical_origin_regularity')
    result['verdict'] = 'PASS' if not result['reasons'] else 'REJECT'
    return result
