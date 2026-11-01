"""Independent first integrals for aligned TD-MPD motion on the symmetry axis.

On the axis g=diag(-A,C,C,C), S^xy=s/C, E=A p^t+s w and u=p
for unit rest mass. Hence (p^z)^2=((E-s w)^2-A)/(A C). These
relations must pass substitution into the full Cartesian MPD equations;
they are not an approximation in spin. The scalar quadrature is evaluated
with extended-precision spectral values to avoid subtracting turning energies.
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import brentq

LD=np.longdouble


class AxialMetric:
    def __init__(self,parent,core,radius,*,orientation=1):
        self.parent={k:np.asarray(v,dtype=LD) for k,v in parent.items()}
        self.core={k:np.asarray(v,dtype=LD) for k,v in core.items()}
        self.radius=LD(radius);self.length=LD(self.parent.pop('length'))
        self.orientation=orientation

    @classmethod
    def from_corridor(cls,geometry,*,orientation=1):
        parent={k:np.asarray(geometry.parent.coefficients[k]).sum(axis=1) for k in ('f','b','w')}
        parent['length']=geometry.length
        core={}
        for k in ('f','C','w'):
            c=np.asarray(geometry.coefficients[k]);core[k]=((-1.)**np.arange(c.shape[0]))@c
        return cls(parent,core,geometry.radius,orientation=orientation)

    def values(self,z,*,derivative=False):
        z=np.asarray(z,dtype=LD);r=np.abs(z);s=(r-self.length)/(r+self.length)
        ds=2*self.length*np.sign(z)/(r+self.length)**2
        v=2*z*z/self.radius**2-1;dv=4*z/self.radius**2
        cheb=np.polynomial.chebyshev
        outer={k:cheb.chebval(s,c) for k,c in self.parent.items()}
        od={k:cheb.chebval(s,cheb.chebder(c))*ds for k,c in self.parent.items()}
        c=(1+outer['b'])**2*np.exp(-outer['f'])
        cd=c*(2*od['b']/(1+outer['b'])-od['f'])
        outer['C']=c;od['C']=cd
        # Outside the fitting cylinder, evaluate the core only at its edge.
        # This avoids polynomial extrapolation overflow even though its weight
        # would be zero. The exact join agrees with CartesianCorridor._join.
        v=np.minimum(v,LD(1))
        core={k:cheb.chebval(v,c) for k,c in self.core.items()}
        kd={k:cheb.chebval(v,cheb.chebder(c))*dv for k,c in self.core.items()}
        a=(self.radius/2)**2;den=self.radius**2-a
        t=np.clip((z*z-a)/den,0,1)
        weight=t**3*(10-15*t+6*t*t)
        wd=np.where((r>self.radius/2)&(r<self.radius),30*t*t*(1-t)**2*2*z/den,0)
        result={};gradient={}
        for key in ('f','C','w'):
            result[key]=(1-weight)*core[key]+weight*outer[key]
            gradient[key]=(1-weight)*kd[key]+weight*od[key]+wd*(outer[key]-core[key])
        result['w']*=self.orientation;gradient['w']*=self.orientation
        result['A']=np.exp(result['f']);gradient['A']=result['A']*gradient['f']
        return (result,gradient) if derivative else result

    def barrier(self,z,spin):
        v=self.values(z);return np.exp(v['f']/2)+LD(spin)*v['w']

    def first_endpoint(self,energy,spin,launch=1.,target=-10.):
        energy,spin=LD(energy),LD(spin)
        z=np.linspace(launch,target,4097,dtype=LD);f=energy-self.barrier(z,spin)
        if f[0]<=0:raise ValueError('initial inward momentum required')
        hits=np.flatnonzero(f<0)
        if not len(hits):return LD(target),'transmitted'
        i=hits[0]
        root=LD(brentq(lambda x:float(energy-self.barrier(x,spin)),float(z[i]),float(z[i-1]),xtol=1e-14))
        for _ in range(12):
            v,d=self.values(root,derivative=True)
            slope=np.exp(v['f']/2)*d['f']/2+spin*d['w']
            delta=(energy-self.barrier(root,spin))/slope
            root+=delta
            if abs(delta)<LD('1e-18'):break
        return root,'reflected'

    def turning_difference(self,z,endpoint,spin):
        """barrier(endpoint)-barrier(z), without subtracting nearby values."""
        z=np.asarray(z,dtype=LD);endpoint=LD(endpoint)
        result=self.barrier(endpoint,spin)-self.barrier(z,spin)
        if endpoint>=-self.radius:return result
        near=(z< -self.radius)&(abs(z-endpoint)<LD('.01'))
        # np.where evaluates both branches: keep the unused divided-difference
        # evaluation inside its negative-z spectral domain as well.
        safe_z=np.where(near,z,endpoint)
        r=-safe_z;re=-endpoint;s=(r-self.length)/(r+self.length);se=(re-self.length)/(re+self.length)
        ds=2*self.length*(r-re)/((r+self.length)*(re+self.length))
        cheb=np.polynomial.chebyshev
        qf=cheb.chebdiv(self.parent['f'],np.array([-se,LD(1)]))[0]
        qw=cheb.chebdiv(self.parent['w'],np.array([-se,LD(1)]))[0]
        df=ds*cheb.chebval(s,qf);dw=ds*cheb.chebval(s,qw)*self.orientation
        root_lapse=np.exp(cheb.chebval(se,self.parent['f'])/2)
        stable=-root_lapse*np.expm1(df/2)-LD(spin)*dw
        return np.where(near,stable,result)

    def phase(self,energy,spin,*,order=16,segments=256,launch=1.,target=-10.):
        energy,spin=LD(energy),LD(spin)
        endpoint,classification=self.first_endpoint(energy,spin,launch,target)
        umax=np.sqrt(LD(launch)-endpoint)
        edges=np.linspace(0,umax,segments+1,dtype=LD)
        joins=[-self.radius,-self.radius/2,self.radius/2,self.radius]
        extra=[np.sqrt(z-endpoint) for z in joins if endpoint<z<launch]
        edges=np.unique(np.r_[edges,extra]);mid=(edges[:-1]+edges[1:])/2;half=np.diff(edges)/2
        nodes,weights=np.polynomial.legendre.leggauss(order)
        u=mid[:,None]+half[:,None]*nodes.astype(LD);z=endpoint+u*u
        v=self.values(z);lapse=np.exp(v['f']/2);om=energy-spin*v['w']
        first=energy-self.barrier(z,spin)
        if classification=='reflected':first=self.turning_difference(z,endpoint,spin)
        discriminant=first*(om+lapse)
        if not np.isfinite(discriminant).all() or np.any(discriminant<=0):
            raise ValueError('unresolved axial turning discriminant')
        common=2*u*np.sqrt(v['A']*v['C']/discriminant)
        proper=np.sum(half*np.sum(common*weights,axis=1),dtype=LD)
        time=np.sum(half*np.sum(common*om/v['A']*weights,axis=1),dtype=LD)
        return dict(classification=classification,final_z=float(endpoint),coordinate_time=float(time),
                    proper_time=float(proper),order=order,segments=segments)

    def state_and_rhs(self,z,energy,spin):
        """Full 24-component state and its derivative for MPD substitution."""
        z,energy,spin=LD(z),LD(energy),LD(spin)
        v,d=self.values(z,derivative=True);a,c,w=v['A'],v['C'],v['w'];om=energy-spin*w
        disc=(energy-self.barrier(z,spin))*(om+np.sqrt(a))
        if disc<=0:raise ValueError('substitution point must precede first turnaround')
        pt=om/a;pz=-np.sqrt(disc/(a*c));sxy=spin/c
        state=np.zeros(24);state[[3,4,7,14,17]]=[z,pt,pz,sxy,-sxy]
        rhs=np.zeros(24);rhs[[0,3]]=[pt,pz]
        rhs[4]=(-spin*d['w']/a-om*d['A']/a**2)*pz
        rhs[7]=(-2*om*spin*d['w']-d['A'])/(2*a*c)-pz*pz*(d['A']/a+d['C']/c)/2
        rhs[14]=-spin*d['C']/c**2*pz;rhs[17]=-rhs[14]
        return state,rhs
