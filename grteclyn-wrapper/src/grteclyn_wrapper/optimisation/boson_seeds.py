"""Positive Bondi-sector profiles used only as coupled-solve initial guesses."""
from functools import lru_cache
import math
import numpy as np


@lru_cache(maxsize=16)
def unit_mass_profile(amplitude):
    from grteclyn_wrapper.grtresna.profiles.qball_couplings import QBallCouplings
    from grteclyn_wrapper.grtresna.profiles.boson_star_ode import solve_selfgrav_boson_star
    # Bondi: V=.5*m^2*phi^2; here chi=sqrt(4pi)*phi and U=8pi*V=m^2*chi^2.
    return solve_selfgrav_boson_star(QBallCouplings.mini_selfgrav(mass=1.),
                                    phi_c=amplitude/math.sqrt(4*math.pi))


def finite_amplitude_seed(state, config):
    """Map an isolated star onto both ends; winding supplies sin^|k|(theta).

    The metric remains the wormhole seed. Neither this map nor its frequency
    is an equilibrium on that metric: only the subsequent coupled solve can
    establish a stationary solution.
    """
    a=config['amplitude']; m=config['matter_mass']
    star=unit_mass_profile(float(a))
    eta=state['map'].eta(state['sx'])
    r=abs(eta)*state['sigma']*m
    values=np.asarray(star.eval_phi0(r))*math.sqrt(4*math.pi)
    far=r>star.r[-1]
    decay=np.sqrt(max(0.,1-star.omega**2))
    with np.errstate(invalid='ignore',over='ignore'):
        values[far]=(math.sqrt(4*math.pi)*star.phi0[-1]*star.r[-1]/r[far]
                     *np.exp(-decay*(r[far]-star.r[-1])))
    values[[0,-1]]=0.
    values*=a/values[len(values)//2]
    seed=dict(state)
    key='CHI' if config['matter']=='cloud' else 'Z'
    seed.pop('CHI' if key=='Z' else 'Z',None)
    seed[key]=values[:,None]*np.ones(len(state['sy']))
    seed['frequency']=float(star.omega*m)
    return seed
