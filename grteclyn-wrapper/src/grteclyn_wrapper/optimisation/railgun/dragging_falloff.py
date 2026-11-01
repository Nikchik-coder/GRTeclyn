"""Experimental Frobenius boundary representation for asymptotic dragging.

w=(1-s)^p H(s,y), deg_s H=nx-p. For p=3 or zero-J p=5, p auxiliary coordinates preserve the
standard vector size and are set to zero by tau rows. The p-1 outermost
interior w equations are not imposed; every printed PDE, including those
rows, remains an independent acceptance check. No physical tolerance changes.
"""
from __future__ import annotations
import numpy as np
from .problem import RingProblem
from .model import canonical_rows,exprel
from .geometry import RingGeometry,chebyshev_basis
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import cheb_coeffs

REPRESENTATION='dragging_cubic_frobenius_tau_v1'
MODEL='canonical_regular_centre_factored_dragging_v1'
CUBIC=np.array([2.5,-3.75,1.5,-.25])


def project_coefficients(values,*,power=3):
    """Polynomial division removes only the degree-two remainder at infinity."""
    values=np.asarray(values)
    if power==5:
        # Repeated endpoint deflation amplifies roundoff as nx^10. Fit the
        # physical values in the constrained basis, truncating only singular
        # directions below 1e-12 of the largest singular value. Every physical
        # equation and asymptotic diagnostic remains an acceptance gate.
        nx=values.shape[0]-1;s=np.cos(np.pi*np.arange(nx+1)/nx)
        basis=(1-s[:,None])**5*np.polynomial.chebyshev.chebvander(s,nx-5)
        return np.linalg.lstsq(basis,values,rcond=1e-12)[0]
    if power!=3:raise ValueError('only cubic or zero-J quintic falloff is supported')
    coeff=cheb_coeffs(values,0)
    result=np.zeros((coeff.shape[0]-3,coeff.shape[1]))
    for i in range(coeff.shape[1]):
        q=np.polynomial.chebyshev.chebdiv(coeff[:,i],CUBIC)[0]
        result[:len(q),i]=q
    return result


class FactoredDraggingProblem(RingProblem):
    representation=REPRESENTATION

    def __init__(self,*args,power=3,**kwargs):
        if power not in (3,5) or (power==5 and kwargs.get('target_j')!=0.):
            raise ValueError('quintic dragging requires a zero-total-J border')
        self.power=power
        self.representation=REPRESENTATION if power==3 else 'dragging_quintic_zeroJ_tau_v1'
        super().__init__(*args,**kwargs)
        self.h_count=self.nx+1-power
        self.h_degree=self.nx-power
        eye=np.eye(self.h_count)
        self.h_basis=np.polynomial.chebyshev.chebvander(self.s,self.nx-self.power)
        self.h_first=np.column_stack([np.polynomial.chebyshev.chebval(self.s,
            np.polynomial.chebyshev.chebder(c)) for c in eye])
        self.h_second=np.column_stack([np.polynomial.chebyshev.chebval(self.s,
            np.polynomial.chebyshev.chebder(c,2)) for c in eye])

    def raw_dragging(self,u):
        return u[self.n:2*self.n].reshape(self.shape)

    def unpack(self,u):
        arrays,freq=super().unpack(u)
        xp=np if isinstance(u,np.ndarray) else self.xp
        h=xp.asarray(self.h_basis)@self.raw_dragging(u)[:self.h_count]
        arrays['w']=(1-xp.asarray(self.s[:,None]))**self.power*h
        return arrays,freq

    def pack(self,arrays,frequencies):
        value=super().pack(arrays,frequencies)
        raw=np.zeros(self.shape);raw[:self.h_count]=project_coefficients(arrays['w'],power=self.power)
        value[self.n:2*self.n]=raw.ravel()
        return value

    def physical_vector(self,u):
        arrays,frequencies=self.unpack(np.asarray(u))
        base=RingProblem(self.fields,nx=self.nx,ny=self.ny,length=self.length,target_j=self.target_j)
        value=base.pack(arrays,frequencies)
        if self.target_j is not None:value[-1]=u[-1]
        return base,value

    def dragging_jets(self,u,xp=np):
        coeff=self.raw_dragging(u)[:self.h_count]
        h=xp.asarray(self.h_basis)@coeff
        hx=xp.asarray(self.h_first)@coeff;hxx=xp.asarray(self.h_second)@coeff
        t=1-xp.asarray(self.s[:,None]);dy=xp.asarray(self.dy)
        k=self.power
        return dict(w=t**k*h,w_x=t**k*hx-k*t**(k-1)*h,
                    w_xx=t**k*hxx-2*k*t**(k-1)*hx+k*(k-1)*t**(k-2)*h,
                    w_y=t**k*(h@dy.T),w_yy=t**k*(h@xp.asarray(self.dyy).T))

    def rows(self,u,xp=np):
        arrays,frequencies=self.unpack(u)
        jets=super().jets(arrays,xp)
        jets.update({k:v[1:-1] for k,v in self.dragging_jets(u,xp).items()})
        return canonical_rows(jets,self.fields,frequencies,r=self.ri,dr=self.dr,
                              ddr=self.ddr,y=self.y[None,:],xp=xp)

    def _residual(self,u):
        xp=self.xp
        value=super()._residual(u)
        raw=self.raw_dragging(u)
        # p algebraic zero rows replace infinity and the p-1 outermost
        # w-PDE rows. Their omitted PDE values remain in rows(u) for validation.
        block=xp.concatenate((raw[-self.power:],self.rows(u,xp)['E_w'][self.power-1:],
                              self.dragging_jets(u,xp)['w_x'][-1:])).ravel()
        return value.at[self.n:2*self.n].set(block)

    def dragging_sample(self,u,s,y,*,derivative=False,one_minus_s=None):
        s=np.atleast_1d(np.asarray(s,float));y=np.atleast_1d(np.asarray(y,float))
        c=np.asarray(self.raw_dragging(np.asarray(u))[:self.h_count])
        from grteclyn_wrapper.analysis.spinning_wormhole.spectral import cheb_eval
        by=cheb_eval(self.y,np.eye(self.ny+1),y)
        h=np.polynomial.chebyshev.chebvander(s,self.h_degree)@c@by.T
        t=(1-s if one_minus_s is None else np.atleast_1d(one_minus_s))[:,None]
        if not derivative:return t**self.power*h
        dc=np.polynomial.chebyshev.chebder(c,axis=0)
        hx=np.polynomial.chebyshev.chebvander(s,self.h_degree-1)@dc@by.T
        return t**self.power*hx-self.power*t**(self.power-1)*h


class FactoredDraggingGeometry(RingGeometry):
    def __init__(self,problem,u):
        self.power=problem.power
        self.h_degree=problem.h_degree
        super().__init__(problem,u)
        self.h_coefficients=self.xp.asarray(cheb_coeffs(
            np.asarray(problem.raw_dragging(np.asarray(u))[:problem.h_count]),1))

    def sample(self,name,s,y):
        if name!='w':return super().sample(name,s,y)
        return (1-s)**self.power*self.xp.einsum('i,ij,j->',chebyshev_basis(s,self.h_degree,self.xp),
            self.h_coefficients,chebyshev_basis(y,self.ny,self.xp))


    def _metric(self,x):
        # Compute 1-s directly: subtracting two near-unit numbers loses the
        # very tail digits that the representation is intended to retain.
        xp=self.xp;r2=xp.sum(x[1:]**2);r=xp.sqrt(r2)
        t=2*self.length/(r+self.length);s=1-t;y=2*x[3]**2/r2-1
        f,n,b=(self.sample(k,s,y) for k in ('f','N','b'))
        w=t**self.power*xp.einsum('i,ij,j->',chebyshev_basis(s,self.h_degree,xp),
                          self.h_coefficients,chebyshev_basis(y,self.ny,xp))
        rho2=x[1]**2+x[2]**2;nu=n*rho2/r2
        c=(1+b)**2*xp.exp(-f);a=c*xp.exp(nu);v=xp.array([-x[2],x[1],0.])
        spatial=a*xp.eye(3)-c*n/r2*exprel(nu,xp)*xp.outer(v,v)
        g=xp.zeros((4,4));g=g.at[0,0].set(-xp.exp(f)+c*w*w*rho2)
        g=g.at[0,1:].set(-c*w*v);g=g.at[1:,0].set(-c*w*v)
        return g.at[1:,1:].set(spatial)


def surface_flux(problem,u,radii,*,order=96):
    """Original finite-sphere Komar integral, differentiated in factored form."""
    from grteclyn_wrapper.analysis.spinning_wormhole.spectral import cheb_eval
    radii=np.atleast_1d(np.asarray(radii,float))
    if np.any(radii<=0) or not np.isfinite(radii).all():raise ValueError('positive radii required')
    mu,weights=np.polynomial.legendre.leggauss(order);mu=(mu+1)/2;weights=weights/2
    s=(radii-problem.length)/(radii+problem.length);y=2*mu*mu-1
    bx=cheb_eval(problem.s,np.eye(problem.nx+1),s)
    by=cheb_eval(problem.y,np.eye(problem.ny+1),y)
    arrays,_=problem.unpack(np.asarray(u));f=bx@arrays['f']@by.T;b=1+bx@arrays['b']@by.T
    wr=problem.dragging_sample(u,s,y,derivative=True,one_minus_s=2*problem.length/(radii+problem.length))*2*problem.length/(radii[:,None]+problem.length)**2
    return -radii**4/4*np.sum(weights*(1-mu*mu)*b**3*np.exp(-2*f)*wr,axis=1)


def cartesian_surface_flux(problem,u,radii,*,order=48):
    """Independent metric-ratio AD derivative in Cartesian coordinates."""
    geometry=FactoredDraggingGeometry(problem,u);jax,xp=problem.jax,problem.xp
    def omega(point):
        g=geometry.metric(point)
        return -g[0,2]/(point[1]*g[2,2])
    derivative=jax.jacfwd(omega)
    def integrand(point):
        g=geometry.metric(point);alpha=1/xp.sqrt(-xp.linalg.inv(g)[0,0])
        radial=point[1:]/xp.linalg.norm(point[1:])
        return g[2,2]**1.5/alpha*xp.dot(derivative(point)[1:],radial)
    evaluate=jax.jit(jax.vmap(integrand))
    mu,weights=np.polynomial.legendre.leggauss(order);mu=(mu+1)/2;weights=weights/2
    result=[]
    for r in np.atleast_1d(radii):
        points=np.column_stack((np.zeros_like(mu),r*np.sqrt(1-mu*mu),np.zeros_like(mu),r*mu))
        result.append(-r**4/4*np.sum(weights*(1-mu*mu)*np.asarray(evaluate(xp.asarray(points)))))
    return np.array(result)


def save_state(path,problem,u,*,validated=False):
    import json
    base,physical=problem.physical_vector(u)
    metadata=dict(schema=1,model=MODEL,representation=problem.representation,falloff_power=problem.power,nx=problem.nx,ny=problem.ny,
                  length=problem.length,target_j=problem.target_j,fields=[f.to_dict() for f in problem.fields],
                  validated=bool(validated),stability='not_assessed')
    np.savez_compressed(path,metadata=json.dumps(metadata),u=np.asarray(u),physical_u=physical)


def load_state(path):
    import json
    from .model import ScalarField
    with np.load(path,allow_pickle=False) as data:
        metadata=json.loads(str(data['metadata']));value=np.array(data['u'])
        physical=np.array(data['physical_u'])
    if metadata.get('model')!=MODEL or metadata.get('representation') not in (REPRESENTATION,'dragging_quintic_zeroJ_tau_v1','dragging_quintic_regular_operator_v2','dragging_cubic_regular_operator_v2'):
        raise ValueError('explicit factored-dragging format required')
    cls=FactoredDraggingProblem
    if metadata['representation'] in ('dragging_quintic_regular_operator_v2','dragging_cubic_regular_operator_v2'):
        from .regular_dragging import RegularDraggingProblem
        cls=RegularDraggingProblem
    problem=cls([ScalarField(**f) for f in metadata['fields']],
        nx=metadata['nx'],ny=metadata['ny'],length=metadata['length'],target_j=metadata['target_j'],power=metadata.get('falloff_power',3))
    if problem.representation!=metadata['representation']:raise ValueError('falloff representation mismatch')
    if value.shape!=(problem.n_unknowns,) or not np.isfinite(value).all():raise ValueError('invalid factored state')
    _,reconstructed=problem.physical_vector(value)
    if physical.shape!=reconstructed.shape or not np.allclose(physical,reconstructed,rtol=0.,atol=64*np.finfo(float).eps*max(1.,float(np.max(abs(physical))))):
        raise ValueError('physical state does not match factored coordinates')
    return problem,value,metadata


def validate(problem,u,info,*,equation_tol=1e-8,tail_tol=1e-6):
    """Retain original gates, full omitted PDEs and independent Cartesian flux."""
    from .diagnostics import validate as canonical_validate
    base,physical=problem.physical_vector(u)
    row=canonical_validate(base,physical,info,equation_tol=equation_tol,tail_tol=tail_tol,independent=False)
    reasons=[r for r in row['reasons'] if r!='angular_momentum_balance']
    # The stored physical nodal field has a lower polynomial degree than
    # t^p H. Independently check the volume charge on the actual factored
    # field before comparing it with the surface flux.
    arrays,frequencies=problem.unpack(np.asarray(u))
    sample=lambda a:problem.qx@a@problem.qy.T
    f,n,b=(sample(arrays[k]) for k in ('f','N','b'))
    radii=problem.rg;s=(radii-problem.length)/(radii+problem.length)
    w=problem.dragging_sample(u,s,2*problem.mg**2-1,one_minus_s=2*problem.length/(radii+problem.length))
    sk=1-problem.mg[None,:]**2
    measure=problem.wr[:,None]*problem.wm[None,:]*radii[:,None]**2*(1+b)**3*np.exp(n*sk-2*f)
    charges=[]
    for i,(field,omega) in enumerate(zip(problem.fields,frequencies)):
        amp2=sk**abs(field.winding)*sample(arrays[f'q{i}'])**2
        if field.parity=='odd':amp2=amp2*problem.mg[None,:]**2
        charges.append(float(np.sum(measure*(omega+field.winding*w)*amp2)))
    charge_error=float(np.max(abs(np.asarray(charges)-row['charges'])))
    row['nodal_volume_J']=row['J_volume'];row['factored_charge_crosscheck']=charge_error
    row['charges']=charges;row['matter_J']=[-f.winding*q for f,q in zip(problem.fields,charges)]
    row['J_volume']=float(sum(row['matter_J']))
    if not np.isfinite(charge_error) or charge_error>equation_tol:reasons.append('factored_volume_charge')
    row['physical_nodal_interpolation_J_surfaces']=row['J_surfaces']
    radii=np.array(row['J_surface_radii']);flux=surface_flux(problem,u,radii)
    coarse=surface_flux(problem,u,radii,order=48)
    independent=cartesian_surface_flux(problem,u,radii)
    error=float(np.max(abs(flux-row['J_volume'])))
    cross=float(np.max(abs(flux-independent)))
    quadrature=float(np.max(abs(flux-coarse)))
    scale=max(1.,abs(row['J_volume']))
    if (not np.isfinite([*flux,*independent,error,cross,quadrature]).all()
            or max(error,quadrature,cross)>equation_tol*scale):reasons.append('angular_momentum_balance')
    row.update(J_surfaces=flux.tolist(),J_surface_estimate=float(flux[-1]),
        J_surface_quadrature_drift=quadrature,angular_momentum_surface_error=error,
        Cartesian_J_surfaces=independent.tolist(),Cartesian_J_surface_crosscheck=cross,
        representation=problem.representation)
    residual=np.asarray(problem.residual(u));rows=problem.rows(u)
    omitted_count=getattr(problem,'omitted_row_count',problem.power-1)
    omitted=float(np.max(abs(rows['E_w'][:omitted_count])/(1+problem.ri[:omitted_count]**2))) if omitted_count else 0.
    row['omitted_outer_w_equation_count']=omitted_count
    row['omitted_outer_w_equation_max']=omitted
    row['factored_tau_residual_max']=float(np.max(abs(residual)))
    if not np.isfinite(omitted) or omitted>equation_tol:reasons.append('omitted_outer_w_equations')
    if not np.isfinite(residual).all() or np.max(abs(residual))>equation_tol:reasons.append('factored_tau_residual')
    # The monopole coefficient must agree with volume J at literal infinity;
    # anisotropic r^-3 terms are disallowed independently of the finite spheres.
    c=np.asarray(problem.raw_dragging(u)[:problem.h_count]);h_inf=np.sum(c,axis=0)
    mu,weights=np.polynomial.legendre.leggauss(96);mu=(mu+1)/2;weights=weights/2
    from grteclyn_wrapper.analysis.spinning_wormhole.spectral import cheb_eval
    by=cheb_eval(problem.y,np.eye(problem.ny+1),2*mu*mu-1);h=by@h_inf
    if problem.power==3:
        j_inf=float(6*problem.length**3*np.sum(weights*(1-mu*mu)*h))
        anisotropy=float(4*problem.length**3*np.max(abs(h-j_inf/(4*problem.length**3))))
    else:
        j_inf,anisotropy=0.,0.
        # With J=0 and equatorial reflection the leading permitted mode is
        # r^-5 P'_3(mu). Check its flat asymptotic angular equation separately.
        angular=4*(1-problem.y**2)*(problem.dyy@h_inf)-(10*problem.y+6)*(problem.dy@h_inf)+10*h_inf
        peak=float(np.max(abs(h_inf)))
        angular_error=max(0.,float(np.max(abs(angular)))-64*np.finfo(float).eps)/max(peak,1e-300)
        row['leading_angular_relative_error']=angular_error
        if not np.isfinite(angular_error) or angular_error>1e-6:reasons.append('leading_asymptotic_angular_mode')
    row.update(J_infinity_factored=j_inf,J_infinity_anisotropy=anisotropy,falloff_power=problem.power)
    if max(abs(j_inf-row['J_volume']),anisotropy)>equation_tol*scale:reasons.append('asymptotic_dragging_modes')
    geometry=FactoredDraggingGeometry(problem,u);checks=[]
    for radius in problem.length*np.array([.02,.05,.15,.5,1.,2.,4.]):
        for theta in (.25,.8,1.3):checks.append(geometry.independent([0.,radius*np.sin(theta),0.,radius*np.cos(theta)]))
        checks.append(geometry.independent([0.,0.,0.,radius]))
    row['offgrid_einstein_max']=max(r['einstein_max'] for r in checks)
    row['offgrid_kg_max']=max(r['kg_max'] for r in checks)
    row['offgrid_intrinsic_kg_max']=max(r.get('kg_intrinsic_max',0.) for r in checks)
    row['kg_coordinate_difference']=max(r.get('kg_coordinate_difference',0.) for r in checks)
    if max(row[k] for k in ('offgrid_einstein_max','offgrid_kg_max'))>equation_tol:reasons.append('independent_equations')
    if max(row[k] for k in ('offgrid_intrinsic_kg_max','kg_coordinate_difference'))>equation_tol:reasons.append('intrinsic_kg_crosscheck')
    row.update(verdict='PASS' if not reasons else 'REJECT',reasons=reasons)
    return row
