"""Solve metric coefficients directly to retain small angular variations.

Nodal f and b contain a large angle-independent background. Rounding their
small angular variations before differentiating twice creates curvature
noise near the axis. Keep their full tensor-product coefficients, together
with N, as Newton unknowns. No coefficient is removed or filtered. The
cubic dragging representation and every interior field equation remain.
"""
from __future__ import annotations

import numpy as np

from grteclyn_stationary.railgun.geometry import interpolation_coefficients
from grteclyn_stationary.railgun.smooth_cubic import SmoothCubicProblem

REPRESENTATION = 'spectral_metric_cubic_dragging_smooth_origin_v1'


class SmoothSpectralProblem(SmoothCubicProblem):
    discretisation = REPRESENTATION
    spectral_metric_tags = ('f','N','b')

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.representation = REPRESENTATION
        self.angular_basis = np.polynomial.chebyshev.chebvander(self.y,self.ny)
        identity = np.eye(self.ny+1)
        self.angular_first = np.column_stack([
            np.polynomial.chebyshev.chebval(self.y,np.polynomial.chebyshev.chebder(c))
            for c in identity])
        self.angular_second = np.column_stack([
            np.polynomial.chebyshev.chebval(self.y,np.polynomial.chebyshev.chebder(c,2))
            for c in identity])

    def raw_metric(self,u,name):
        index = self.tags.index(name)
        return u[index*self.n:(index+1)*self.n].reshape(self.shape)

    def unpack(self,u):
        arrays,frequencies = super().unpack(u)
        xp = np if isinstance(u,np.ndarray) else self.xp
        for name in self.spectral_metric_tags:
            arrays[name] = xp.asarray(self.h_basis)@self.raw_metric(u,name)@xp.asarray(self.angular_basis).T
        return arrays,frequencies

    def pack(self,arrays,frequencies):
        result = super().pack(arrays,frequencies)
        for name in self.spectral_metric_tags:
            index = self.tags.index(name)
            result[index*self.n:(index+1)*self.n] = interpolation_coefficients(arrays[name]).ravel()
        return result

    def metric_derivative(self,u,name,radial=0,angular=0,xp=np):
        bx = (self.h_basis,self.h_first,self.h_second)[radial]
        by = (self.angular_basis,self.angular_first,self.angular_second)[angular]
        return xp.asarray(bx)@self.raw_metric(u,name)@xp.asarray(by).T

    def state_jets(self,u,xp=np):
        arrays,_ = self.unpack(u)
        jets = self.jets(arrays,xp)
        for name in self.spectral_metric_tags:
            key = 'B' if name=='b' else name
            for suffix,radial,angular in (('_x',1,0),('_xx',2,0),('_y',0,1),('_yy',0,2)):
                jets[key+suffix] = self.metric_derivative(u,name,radial,angular,xp)[1:-1]
        jets['B_xy'] = self.metric_derivative(u,'b',1,1,xp)[1:-1]
        return jets

    def infinity_metric_derivatives(self,u,arrays,xp=np):
        return tuple(self.metric_derivative(u,name,1,0,xp)[0] for name in ('f','b'))

    def origin_block(self,u,arrays,name,xp):
        if name not in self.spectral_metric_tags:
            return super().origin_block(u,arrays,name,xp)
        derivative = self.metric_derivative(u,name,1,0,xp)[-1:]
        if name=='N':
            return derivative
        # Isolate nonconstant angular modes before adding the O(1) mean.
        # The constraint is identical to origin_rows, without cancellation.
        angular = xp.asarray(self.h_basis[-1])@self.raw_metric(u,name)
        anisotropy = xp.asarray(self.angular_basis[:,1:])@angular[1:]
        return (anisotropy-xp.mean(anisotropy)+xp.mean(derivative))[None,:]

    def transfer(self,old,u,*,perturb=0.):
        result = super().transfer(old,u,perturb=0.)
        if isinstance(old,SmoothSpectralProblem) and old.length==self.length:
            for name in self.spectral_metric_tags:
                target = np.zeros(self.shape)
                nr,na = min(self.nx,old.nx)+1,min(self.ny,old.ny)+1
                target[:nr,:na] = old.raw_metric(np.asarray(u),name)[:nr,:na]
                index = self.tags.index(name)
                result[index*self.n:(index+1)*self.n] = target.ravel()
        if perturb:
            shape = ((1-self.s[:,None]**2)**2*(1-self.y[None,:]**2)**2)
            coefficients = interpolation_coefficients(shape)
            for name in self.spectral_metric_tags:
                index = self.tags.index(name)
                result[index*self.n:(index+1)*self.n] += perturb*coefficients.ravel()
        return result
