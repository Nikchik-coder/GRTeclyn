"""One acceptance policy shared by searching and final refinement."""
import dataclasses
import numpy as np
from .study_diagnostics import volume_budgets, tidal_envelope, independent_equations
from .surfaces import verify_surface


def validate(state, config, row, *, reference_peak, tidal_factor, energy_budget=None,
             detailed=False):
    out=dict(row); reasons=[]
    if row.get('verdict')!='PASS': reasons.append('stationary_constraints')
    coarse=volume_budgets(state,config)
    fine=volume_budgets(state,config,n_x=384,n_mu=128)
    out.update(fine)
    if not all(np.isfinite(v) for v in fine.values()):
        out.update(verdict='ABOVE_GATE',rejection_reasons=['nonfinite_diagnostics'])
        return out
    if (fine['X_full']<=0 or fine['E_b']<0 or fine['B_min']<=0 or
            fine['lapse_min']<=0 or fine['R_A']<=0):
        out.update(verdict='ABOVE_GATE',rejection_reasons=['invalid_geometry_or_energy'])
        return out
    drift=max(abs(fine[k]-coarse[k])/max(abs(fine[k]),1e-14)
              for k in ('X_full','E_b'))
    out['volume_relative_drift']=float(drift)
    if drift>1e-6: reasons.append('volume_quadrature')
    if energy_budget is not None:
        out['ordinary_energy_limit'] = float(energy_budget)
        if fine['E_b_over_R_A']>energy_budget:
            reasons.append('ordinary_energy_budget')
    if config.get('matter'):
        from .exoticity import _grid_eval
        key='CHI' if config['matter']=='cloud' else 'Z'
        peak=float(np.max(abs(state[key])))
        shells=[]
        for sign in (-1,1):
            values=_grid_eval(state['sx'],state['sy'],state[key],
                              sign*np.array([.99,.995,.999]),np.linspace(-1,1,33))
            shells.append(np.max(abs(values),axis=1)/max(peak,1e-300))
        localized=all(c<1e-6 and c<=b+1e-12 and b<=a+1e-12 for a,b,c in shells)
        out.update(boson_tail_ratios=[v.tolist() for v in shells],boson_localized=bool(localized))
        if not localized: reasons.append('boson_localization')
    if not reasons:
        surface=verify_surface(1.,state['map'],state['sx'],state['sy'],state['F'],
                               state['N'],state['B'],state['surface_coefficients'])
        out.update(surface)
        if not surface['surface_verified']: reasons.append('minimal_surface')
    if not reasons:
        off=independent_equations(state,config,
              radial_points=max(17,len(state['sx'])//4) if detailed else 17,
              angular_points=max(9,len(state['sy'])//2) if detailed else 9)
        out.update(off)
        if not off['offgrid_pass']: reasons.append('offgrid_equations')
    if not reasons:
        tides=tidal_envelope(state)
        out.update(tides)
        if not tides['tidal_converged']: reasons.append('tidal_sampling')
        if reference_peak is not None:
            out['tidal_limit']=float(reference_peak*tidal_factor)
            # Conservative allowance for the measured peak uncertainty.
            uncertainty=max(tides['tidal_drift'],1e-6)
            if tides['tidal_peak']*(1+uncertainty)>out['tidal_limit']:
                reasons.append('tidal_limit')
    if detailed and not reasons:
        from .diagnostics import Background
        sig=state['sigma']
        bg=Background(sig,dataclasses.replace(state['map'],eta0=state['map'].eta0*sig),
                      state['F'],state['W']/sig,state['N'],state['B'],state['PSI'],config['J'])
        x=np.linspace(-.995,.995,161); mu=np.linspace(0.,1.,65)
        local=bg.local(x,mu)
        out['local_nec_peak']=bg.local_peak(x,mu,'nec_max',local['nec_max'])
        for name,mu in (('axis',1.),('equator',0.)):
            bg.xi_t=float(np.polynomial.chebyshev.chebval(2*mu*mu-1,state['surface_coefficients']))
            _,times=bg.crossing(np.array([-10.,10.])*fine['R_A'],mu)
            out[f'transit_{name}']=float(times[1]-times[0])
        out.update(asymptotic_masses(state))
    out['rejection_reasons']=reasons
    out['verdict']='PASS' if not reasons else 'ABOVE_GATE'
    out['stability']='not_assessed'
    return out


def asymptotic_masses(state):
    """Spatial ADM 1/r fits in each end's own asymptotic length units."""
    from .exoticity import _grid_eval
    out={}
    for name,sign,gamma in (('plus',1,0.),('minus',-1,state['gamma'])):
        x=sign*np.array([.98,.99,.995,.9975,.99875])
        radius=abs(state['map'].eta(x))*state['sigma']*np.exp(-gamma/2)
        f,b=(_grid_eval(state['sx'],state['sy'],state[key],x,[0.])[:,0]
             for key in ('F','B'))
        asym=(b-1)-(f-gamma)/2
        fits=[float(np.linalg.lstsq(np.stack([1/radius[i:],1/radius[i:]**2],axis=1),
                                    asym[i:],rcond=None)[0][0]) for i in (0,1)]
        out[f'M_ADM_{name}_estimate']=fits[1]
        out[f'M_ADM_{name}_fit_drift']=abs(fits[1]-fits[0])
    return out
