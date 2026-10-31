"""Physical objectives and hard constraints for the fixed-area studies."""
from __future__ import annotations
import math
import numpy as np
from .exoticity import _grid_eval, tidal, nec_rays
from .surfaces import surface_geometry
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import lobatto


def independent_equations(state, config, *, radial_points=17, angular_points=9):
    """Direct Ricci tensor and divergence-form KG, away from solver nodes.

    Does not call matter_residual_forms or the Newton residual. Errors are
    dimensionless in throat units; curvature is checked in an orthonormal
    frame. The finite point set is recorded and enlarged during refinement.
    """
    from .potentials import PolynomialPotential
    sx,sy=state['sx'],state['sy']; sigma=state['sigma']
    _,dx=lobatto(len(sx)-1); _,dy=lobatto(len(sy)-1)
    x=np.polynomial.legendre.leggauss(radial_points)[0]
    mu=(np.polynomial.legendre.leggauss(angular_points)[0]+1)/2
    y=2*mu**2-1; sn=np.sqrt(1-mu**2); theta=np.arccos(mu)
    eta=state['map'].eta(x)[:,None]; ep=state['map'].deta(x)[:,None]
    epp=state['map'].d2eta(x)[:,None]; h=eta**2+1
    def jets(a):
        def at(a): return _grid_eval(sx,sy,a,x,y)
        ax,ay=at(dx@a),at(a@dy.T)
        yt=-4*mu*sn; ytt=-4*y
        return (at(a),ax/ep,at(dx@(dx@a))/ep**2-ax*epp/ep**3,
                yt*ay,yt**2*at((a@dy.T)@dy.T)+ytt*ay)
    f,*_=jets(state['F']); n,*_=jets(state['N']); b,br,_,bt,_=jets(state['B'])
    w,*_=jets(state['W']); psi,pr,prr,pt,ptt=jets(state['PSI'])
    nu=n*sn**2; inv=np.exp(f-nu)/(sigma*b)**2
    def lap(a,ar,arr,at,att):
        return inv*(arr+(2*eta/h+br/b)*ar+(att+(mu/sn+bt/b)*at)/h)
    pot=PolynomialPotential.kink_q(config['m'],state['psim'],tuple(config['q']))
    kgpsi=lap(psi,pr,prr,pt,ptt)-pot.dV(psi)/2
    ra=volume_budgets(state,config,n_x=64,n_mu=24)['R_A']
    kgmax=float(np.max(abs(kgpsi))*ra**2/max(1.,abs(state['psim'])))
    amplitude=ar=at=phase0=phase3=0.
    U=0.
    if config.get('matter'):
        key='CHI' if config['matter']=='cloud' else 'Z'
        raw,rr,rrr,rt,rtt=jets(state[key]); k=config.get('winding_k',1) if key=='Z' else 0
        ka=abs(k); sk=sn**ka
        amplitude=sk*raw; ar=sk*rr; arr=sk*rrr
        at=sk*(rt+ka*mu/sn*raw)
        att=sk*(rtt+2*ka*mu/sn*rt+(ka*(ka-1)*(mu/sn)**2-ka)*raw)
        freq=(state['frequency']+k*w/sigma)*np.exp(-f/2)
        az=k*np.exp(f/2)/(sigma*b*np.sqrt(h)*sn)
        kg=lap(amplitude,ar,arr,at,att)+(freq**2-az**2-config['matter_mass']**2)*amplitude
        kgmax=max(kgmax,float(np.max(abs(kg))*ra**2/max(config['amplitude'],1e-12)))
        U=config['matter_mass']**2*amplitude**2
        phase0=freq*amplitude; phase3=az*amplitude
    curvature_jets=[(dx@a,a@dy.T,dx@(dx@a),(dx@a)@dy.T,(a@dy.T)@dy.T)
                    for a in (state['F'],state['W'],state['B'],state['N'])]
    riemann_args=(1.,state['map'],sx,sy,dx,dy,state['F'],state['W'],state['N'],state['B'])
    worst=0.; minkowski=np.diag([-1.,1.,1.,1.])
    V=pot.V(psi)
    for i,xx in enumerate(x):
        if 1/(eta[i,0]**2+1)<.05**2:
            continue  # Cartesian-like curvature gate; KG above includes tails.
        for j,tt in enumerate(theta):
            ricci=tidal(*riemann_args,xx,theta=tt,spectral_jets=curvature_jets,
                        return_curvature=True)['ricci_frame']/sigma**2
            dp=np.array([0.,np.sqrt(inv[i,j])*pr[i,j],np.sqrt(inv[i,j]/h[i,0])*pt[i,j],0.])
            source=-2*np.outer(dp,dp)-V[i,j]*minkowski
            if config.get('matter'):
                da=np.array([0.,np.sqrt(inv[i,j])*ar[i,j],np.sqrt(inv[i,j]/h[i,0])*at[i,j],0.])
                phase=np.array([phase0[i,j],0.,0.,phase3[i,j]])
                source+=2*(np.outer(da,da)+np.outer(phase,phase))+U[i,j]*minkowski
            error=np.max(abs(ricci-source))/max(ra**-2,np.max(abs(ricci)),np.max(abs(source)))
            worst=max(worst,float(error))
    return dict(offgrid_einstein=worst,offgrid_scalar=kgmax,
                offgrid_points=len(x)*len(mu),offgrid_pass=bool(max(worst,kgmax)<=1e-8))


def volume_budgets(state, config, *, n_x=192, n_mu=64):
    """Both-end integrals in physical units, with psi,chi = sqrt(4pi) phi.

    Canonical rho = (|Pi|^2+|D chi|^2+U)/(8pi); U=m^2|chi|^2.
    Choose Q with positive density for positive local harmonic frequency;
    with exp(i omega t+i k phi), J_b=-k Q. E_b is not an ADM mass.
    """
    sx,sy=state['sx'],state['sy']
    _,dx=lobatto(len(sx)-1); _,dy=lobatto(len(sy)-1)
    x,wx=np.polynomial.legendre.leggauss(n_x)
    mu,wm=np.polynomial.legendre.leggauss(n_mu)
    y=2*mu**2-1; s2=1-mu**2
    def at(a): return _grid_eval(sx,sy,a,x,y)
    f,n,b,w=(at(state[k]) for k in ('F','N','B','W'))
    sigma=state['sigma']; eta=state['map'].eta(x); ep=state['map'].deta(x)
    h=(eta**2+1)[:,None]; nu=n*s2
    inverse=np.exp(f-nu)/(sigma*b)**2
    volume=sigma**3*b**3*np.exp(-1.5*f+nu)*h*ep[:,None]
    def integral(a): return 2*np.pi*np.einsum('i,j,ij->',wx,wm,volume*a)
    psi=state['PSI']
    radial=inverse*(at(dx@psi)/ep[:,None])**2
    angular=inverse/h*(4*mu*np.sqrt(s2)*at(psi@dy.T))**2
    c=state.get('surface_coefficients', [state['xi_t']])
    th=surface_geometry(1.,state['map'],sx,sy,state['F'],state['N'],state['B'],c)
    ra=sigma*th['R_A']
    xr,xt=integral(radial)/(4*np.pi*ra),integral(angular)/(4*np.pi*ra)
    out=dict(X_full=float(xr+xt), X_radial=float(xr), X_angular=float(xt),
             R_A=float(ra), area=4*np.pi*ra**2,
             R_e=float(sigma*th['R_e']),R_pol=float(sigma*th['R_pol']),
             E_b=0., E_b_over_R_A=0., Q_b=0., J_b=0.,
             B_min=float(np.min(b)),
             local_nec_peak=float(np.max(radial+angular)/(4*np.pi)),
             lapse_min=float(np.exp(min(f.min(),np.min(state['F']))/2)))
    if config.get('matter'):
        key='CHI' if config['matter']=='cloud' else 'Z'
        field=state[key]; k=int(config.get('winding_k',0)) if key=='Z' else 0
        ka=abs(k); raw=at(field); amp=s2**(ka/2)*raw
        dr=s2**(ka/2)*at(dx@field)/ep[:,None]
        dt=(-4*mu*s2**((ka+1)/2)*at(field@dy.T)
            + (ka*mu*s2**((ka-1)/2)*raw if ka else 0))
        local_freq=(state['frequency']+k*w/sigma)*np.exp(-f/2)
        grad=inverse*(dr**2+dt**2/h)
        if k:
            grad+=k*k*amp**2*np.exp(f)/(sigma**2*b*b*h*s2)
        rho=(local_freq**2*amp**2+grad+config['matter_mass']**2*amp**2)/(8*np.pi)
        eb=float(integral(rho)); charge=float(integral(local_freq*amp**2)/(4*np.pi))
        out.update(E_b=eb,E_b_over_R_A=eb/ra,Q_b=charge,J_b=-k*charge)
    rays=nec_rays(1.,state['map'],sx,sy,dx,state['N'],state['B'],psi,n_x=n_x)
    out.update({f'phantom_ray_{k}':v/sigma for k,v in rays.items()})
    return out


def tidal_envelope(state, *, speeds=(0.,-.5,.5), tolerance=1e-3,
                   levels=((33,9),(65,17),(129,33)), refine=True):
    """Adaptive compactified-domain sampling, local maximisation and tail checks.

    Failure to converge or to resolve a decaying tail is a failed constraint,
    never permission to use the best sampled value as an upper bound.
    """
    from scipy.optimize import minimize
    _,dx=lobatto(len(state['sx'])-1); _,dy=lobatto(len(state['sy'])-1)
    args=(1.,state['map'],state['sx'],state['sy'],dx,dy,
          state['F'],state['W'],state['N'],state['B'])
    cache={}; axis_error=0.
    jets=[(dx@a,a@dy.T,dx@(dx@a),(dx@a)@dy.T,(a@dy.T)@dy.T)
          for a in (state['F'],state['W'],state['B'],state['N'])]
    def value(x,t,v):
        nonlocal axis_error
        key=(float(x),float(t),float(v))
        if key not in cache:
            data=tidal(*args,x,v,t,spectral_jets=jets)
            cache[key]=data['max_abs']/state['sigma']**2
            axis_error=max(axis_error,data.get('axis_error',0.)/state['sigma']**2)
        return cache[key]
    previous=None; converged=False; best=(0.,0.,0.,0.); drift=float('inf')
    for nx,nt in levels:
        xs=np.linspace(-.995,.995,nx); ts=np.linspace(0.,math.pi/2,nt)
        for v in speeds:
            a=np.array([[value(x,t,v) for t in ts] for x in xs])
            for i,j in zip(*np.where(a>=np.max(a)*.75)):
                box=a[max(0,i-1):i+2,max(0,j-1):j+2]
                if a[i,j]<box.max(): continue
                candidate=(float(a[i,j]),float(xs[i]),float(ts[j]),float(v))
                if refine:
                    opt=minimize(lambda z:-value(*z,v),[xs[i],ts[j]],
                                 method='Nelder-Mead',bounds=[(-.995,.995),(0.,math.pi/2)],
                                 options={'xatol':1e-8,'fatol':max(a.max()*1e-7,1e-15),'maxiter':120})
                    if opt.success and -opt.fun>candidate[0]:
                        candidate=(-float(opt.fun),*map(float,opt.x),float(v))
                if candidate[0]>best[0]: best=candidate
        if previous is not None:
            drift=abs(best[0]-previous)/max(best[0],1e-300)
            if drift<tolerance:
                converged=True
                break
        previous=best[0]
    tail=[]
    for end in (-1,1):
        shell=[max(value(end*x,t,v) for t in ts for v in speeds)
               for x in (.995,.999,.9999)]
        tail.append(shell)
    tail_ok=all(b<=a*(1+tolerance)+1e-15 and c<=b*(1+tolerance)+1e-15
                and c<=tolerance*best[0]+1e-15 for a,b,c in tail)
    # A peak in an outer shell must not be silently discarded.
    tail_ok=tail_ok and max(max(s) for s in tail)<=best[0]*(1+tolerance)
    axis_ok=axis_error<=tolerance*max(best[0],1e-300)
    return dict(tidal_peak=best[0],tidal_location=list(best[1:]),
                tidal_converged=bool(converged and tail_ok and axis_ok),
                tidal_drift=drift,tidal_tail=tail,tidal_axis_error=axis_error,
                tidal_samples=len(cache),tidal_speeds=list(speeds))
