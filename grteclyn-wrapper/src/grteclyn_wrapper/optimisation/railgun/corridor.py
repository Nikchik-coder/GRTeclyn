"""A regular Cartesian core retaining transverse curvature for through-axis motion.

A signed-axis curve alone cannot determine Riemann: transverse derivatives are
needed by MPD. Fit smooth metric/scalar coefficients in (rho^2,z^2) on a small
cylinder instead, and join to the original metric with a C2 partition. Values,
curvature, independent field equations and polynomial-order agreement must be
certified before the inner stopping sphere can be removed.
"""
from __future__ import annotations

import numpy as np

from .geometry import RingGeometry, chebyshev_basis, curvature
from .model import exprel


class CartesianCorridor(RingGeometry):
    regular_origin = True

    def __init__(self, parent, *, radius=None, degree=6):
        self.parent = parent
        self.jax, self.xp = parent.jax,parent.xp
        self.fields,self.frequencies,self.length = parent.fields,parent.frequencies,parent.length
        self.radius = float(radius if radius is not None else .05*parent.length)
        self.degree=int(degree)
        if not np.isfinite(self.radius) or self.radius <= 0 or self.degree != degree or degree < 3:
            raise ValueError('positive radius and integer degree>=3 required')
        self.names=('f','C','w','H')+tuple(f'h{i}' for i in range(len(self.fields)))
        self.coefficients=self._fit(self.degree)
        self.finer_coefficients=self._fit(self.degree+2)
        self.metric=self.jax.jit(self._metric)
        self.tensors=self.jax.jit(curvature(self._metric,self.jax))
        self._einstein=self.jax.jit(self._independent)
        # Compare against the intrinsic spherical equation too, wherever r>0.
        self._intrinsic_jit=parent._intrinsic_jit
        self.sample=parent.sample
        self.certificate=None

    def _fit(self, degree):
        # Curvature differentiates these coefficients twice. Computing C at
        # O(100) in float64 and solving a Vandermonde system left O(1e-7)
        # artificial curvature in small, strongly redshifted cores. Evaluate
        # the same parent polynomial and its Gauss transform in long double;
        # no smoothing, regularity projection or mode removal is applied.
        from scipy.fft import dct
        pi=np.arccos(np.longdouble(-1))
        nodes=np.cos(pi*(np.arange(degree+1,dtype=np.longdouble)+.5)/(degree+1))
        squared=(nodes+1)/2*self.radius**2
        rho,z=np.meshgrid(np.sqrt(squared),np.sqrt(squared),indexing='ij')
        r2=rho*rho+z*z
        r=np.sqrt(r2)
        s=(r-self.length)/(r+self.length)
        y=2*z*z/r2-1
        def sample(name):
            coefficients=np.asarray(self.parent.coefficients[name],dtype=np.longdouble)
            return np.polynomial.chebyshev.chebval2d(s,y,coefficients)
        f,w,n,b=(sample(name) for name in ('f','w','N','b'))
        c=(1+b)**2*np.exp(-f)
        nu=n*rho*rho/r2
        samples=[f,c,w,c*n/r2*exprel(nu,np)]
        samples.extend(sample(f'q{i}')/r**field.degree for i,field in enumerate(self.fields))
        result={}
        for i,name in enumerate(self.names):
            data=samples[i]
            for axis in (0,1):
                data=dct(data,type=2,axis=axis)/(degree+1)
                first=[slice(None),slice(None)];first[axis]=0
                data[tuple(first)] *= .5
            result[name]=self.xp.asarray(np.asarray(data,dtype=float))
        return result

    def core_sample(self,name,x,*,finer=False):
        coeff=(self.finer_coefficients if finer else self.coefficients)[name]
        u=2*(x[1]**2+x[2]**2)/self.radius**2-1
        v=2*x[3]**2/self.radius**2-1
        return self.xp.einsum('i,ij,j->',chebyshev_basis(u,coeff.shape[0]-1,self.xp),
                             coeff,chebyshev_basis(v,coeff.shape[1]-1,self.xp))

    def core_metric(self,x,*,finer=False):
        xp=self.xp
        f,c,w,h=(self.core_sample(key,x,finer=finer) for key in ('f','C','w','H'))
        rho2=x[1]**2+x[2]**2
        v=xp.array([-x[2],x[1],0.])
        g=xp.zeros((4,4)).at[0,0].set(-xp.exp(f)+c*w*w*rho2)
        g=g.at[0,1:].set(-c*w*v).at[1:,0].set(-c*w*v)
        return g.at[1:,1:].set((c+h*rho2)*xp.eye(3)-h*xp.outer(v,v))

    def _join(self,x,core,outer):
        r2=self.xp.sum(x[1:]**2)
        inner2=(.5*self.radius)**2
        def overlap(point):
            t=(r2-inner2)/(self.radius**2-inner2)
            w=t**3*(10-15*t+6*t*t)
            return (1-w)*core(point)+w*outer(point)
        return self.jax.lax.cond(r2 <= inner2,core,
                    lambda point:self.jax.lax.cond(r2 >= self.radius**2,outer,overlap,point),x)

    def _metric(self,x):
        return self._join(x,self.core_metric,self.parent.metric)

    def scalar(self,x,index):
        xp=self.xp
        field=self.fields[index]
        def core(point):
            amp=self.core_sample(f'h{index}',point)
            if field.parity=='odd':amp=amp*point[3]
            real,imag=xp.ones(()),xp.zeros(())
            sign=1 if field.winding >= 0 else -1
            for _ in range(abs(field.winding)):
                real,imag=real*point[1]-imag*sign*point[2],real*sign*point[2]+imag*point[1]
            phase=self.frequencies[index]*point[0]
            return amp*xp.array([real*xp.cos(phase)-imag*xp.sin(phase),
                                 real*xp.sin(phase)+imag*xp.cos(phase)])
        return self._join(x,core,lambda point:self.parent.scalar(point,index))

    def certify(self,*,tolerance=1e-8):
        if not np.isfinite(tolerance) or tolerance <= 0:
            raise ValueError('positive certification tolerance required')
        finer_tensors=self.jax.jit(curvature(lambda x:self.core_metric(x,finer=True),self.jax))
        core_tensors=self.jax.jit(curvature(self.core_metric,self.jax))
        points=[np.zeros(4)]
        for rr in self.radius*np.array([.05,.2,.49,.51,.7,.99,1.01]):
            for theta in (0.,.4,np.pi/2):
                for sign in (-1,1):
                    points.append(np.array([0.,rr*np.sin(theta),0.,sign*rr*np.cos(theta)]))
        rows=[]
        for point in points:
            r=float(np.linalg.norm(point[1:]))
            row=dict(self.independent(point),radius=r,position=point[1:].tolist())
            g=np.asarray(self.metric(point))
            row['positive_spatial_metric']=bool(np.min(np.linalg.eigvalsh(g[1:,1:])) > 0)
            row['timelike_normal']=bool(np.linalg.inv(g)[0,0] < 0)
            if r <= self.radius:
                coarse=core_tensors(point);fine=finer_tensors(point)
                row['order_metric_difference']=float(np.max(abs(np.asarray(coarse[0])-np.asarray(fine[0]))))
                row['order_curvature_difference']=float(np.max(abs(np.asarray(coarse[2])-np.asarray(fine[2]))))
            if r > 0:
                own=self.tensors(point);parent=self.parent.tensors(point)
                row['parent_metric_difference']=float(np.max(abs(np.asarray(own[0])-np.asarray(parent[0]))))
                row['parent_curvature_difference']=float(np.max(abs(np.asarray(own[2])-np.asarray(parent[2]))))
            rows.append(row)
        keys=('einstein_max','kg_max','kg_intrinsic_max','kg_coordinate_difference',
              'order_metric_difference','order_curvature_difference',
              'parent_metric_difference','parent_curvature_difference')
        maxima={key:float(np.max([row.get(key,0.) for row in rows])) for key in keys}
        accepted=(all(np.isfinite(value) and value <= tolerance for value in maxima.values())
                  and all(row['positive_spatial_metric'] and row['timelike_normal'] for row in rows))
        self.certificate=dict(accepted=bool(accepted),radius=self.radius,degree=self.degree,
                              comparison_degree=self.degree+2,tolerance=tolerance,maxima=maxima,points=rows)
        return self.certificate
