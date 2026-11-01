"""Pole--dipole MPD motion with the Tulczyjew--Dixon spin condition.

The momentum--velocity relation is used without a linear-spin truncation.
A stationary background conserves spin-corrected Killing energy; this module
neither injects energy nor treats a scalar wave as a polarised spinning body.
Trajectories stop before the unresolved exact-origin interpolation point.
"""
from __future__ import annotations

import itertools
import numpy as np
from scipy.integrate import solve_ivp

from .geometry import curvature
from ..solver.device import configure_jax


class MPDSystem:
    def __init__(self, metric, *, spin_limit=0.1):
        self.jax = configure_jax()
        self.xp = self.jax.numpy
        self.metric = metric
        if not np.isfinite(spin_limit) or spin_limit <= 0:
            raise ValueError('spin_limit must be positive')
        self.spin_limit = spin_limit
        self.geometry = curvature(metric, self.jax)
        self._rhs_jit = self.jax.jit(self._rhs)
        self._invariants_jit = self.jax.jit(self._invariants)

    def _velocity(self, g, riemann, p, spin):
        xp = self.xp
        mass2 = -p@g@p
        lower = xp.einsum('ae,ebcd->abcd', g, riemann)
        denominator = 4*mass2+xp.einsum('abcd,ab,cd->', lower, spin, spin)
        v = p+2*xp.einsum('ab,becd,e,cd->a', spin, lower, p, spin)/denominator
        norm = -v@g@v
        return v/xp.sqrt(norm), norm, denominator

    def _rhs(self, state):
        xp = self.xp
        x, p, spin = state[:4], state[4:8], state[8:].reshape(4, 4)
        g, gam, riem, _ = self.geometry(x)
        u, _, _ = self._velocity(g, riem, p, spin)
        dp = (-xp.einsum('abc,b,c->a', gam, u, p)
              -.5*xp.einsum('abcd,b,cd->a', riem, u, spin))
        ds = (xp.outer(p, u)-xp.outer(u, p)
              -xp.einsum('abc,b,cd->ad', gam, u, spin)
              -xp.einsum('dbc,b,ac->ad', gam, u, spin))
        return xp.concatenate((u, dp, ds.ravel()))

    def _invariants(self, state):
        xp = self.xp
        x, p, spin = state[:4], state[4:8], state[8:].reshape(4, 4)
        g, _, riem, _ = self.geometry(x)
        pcov = g@p
        lowspin = g@spin@g
        mass2 = -p@pcov
        spin2 = xp.sum(spin*lowspin)/2
        ssc = pcov@spin
        def killing(vector):
            covector = lambda point: self.metric(point)@vector(point)
            return pcov@vector(x)+.5*xp.einsum('ab,ba->', spin, self.jax.jacfwd(covector)(x))
        energy = -killing(lambda point: xp.array([1., 0., 0., 0.]))
        angular = killing(lambda point: xp.array([0., -point[2], point[1], 0.]))
        u, norm, denom = self._velocity(g, riem, p, spin)
        # A frame-independent scale based on the positive sum of curvature
        # components in the Eulerian orthonormal tetrad, rather than a Lorentz
        # contraction which can vanish in a nonflat geometry.
        alpha = 1/xp.sqrt(-xp.linalg.inv(g)[0, 0])
        beta = xp.linalg.solve(g[1:, 1:], g[0, 1:])
        tetrad = xp.zeros((4, 4)).at[0].set(xp.concatenate((xp.ones(1), -beta))/alpha)
        tetrad = tetrad.at[1:, 1:].set(xp.linalg.inv(xp.linalg.cholesky(g[1:, 1:])))
        lower = xp.einsum('ae,ebcd->abcd', g, riem)
        orth = xp.einsum('ia,jb,kc,ld,abcd->ijkl', tetrad, tetrad, tetrad, tetrad, lower)
        spin_ratio = xp.sqrt(xp.abs(spin2)/mass2*xp.max(xp.abs(orth)))
        return xp.array([mass2, spin2, xp.max(xp.abs(ssc)), energy, angular,
                         u@g@u, norm, denom, spin_ratio])

    def invariants(self, state):
        keys = ('mass2', 'spin2', 'ssc_max', 'energy', 'angular_momentum',
                'velocity_norm', 'velocity_normalizer', 'velocity_denominator', 'spin_curvature_ratio')
        return dict(zip(keys, map(float, np.asarray(self._invariants_jit(self.xp.asarray(state))))))

    def initial_state(self, position, *, mass=1., spin=0., speed=0.):
        if mass <= 0 or not np.isfinite([mass, spin, speed]).all() or abs(speed) >= 1:
            raise ValueError('finite mass>0, spin and |speed|<1 required')
        position = np.asarray(position, float)
        if position.shape != (3,) or not np.isfinite(position).all() or np.linalg.norm(position) == 0:
            raise ValueError('finite position away from origin required')
        x = np.r_[0., position]
        g = np.asarray(self.metric(self.xp.asarray(x)))
        alpha = np.sqrt(-1/np.linalg.inv(g)[0, 0])
        beta = np.linalg.solve(g[1:, 1:], g[0, 1:])
        normal = np.r_[1., -beta]/alpha
        direction = np.array([0., 0., 0., 1.])/np.sqrt(g[3, 3])
        p = mass*(normal+speed*direction)/np.sqrt(1-speed**2)
        sv = direction+p*(p@g@direction)/mass**2
        sv *= spin/np.sqrt(sv@g@sv)
        eps = np.zeros((4, 4, 4, 4))
        for perm in itertools.permutations(range(4)):
            inversions = sum(perm[i]>perm[j] for i in range(4) for j in range(i+1, 4))
            eps[perm] = (-1.)**inversions/np.sqrt(-np.linalg.det(g))
        spin_tensor = -np.einsum('abcd,c,d->ab', eps, g@p, g@sv)/mass
        state = np.r_[x, p, spin_tensor.ravel()]
        inv = self.invariants(state)
        if inv['spin_curvature_ratio'] > self.spin_limit:
            raise ValueError('spin is outside the configured pole--dipole test-body limit')
        return state

    def integrate(self, state, *, duration=20., rtol=1e-9, atol=1e-11,
                  max_step=.2, outer_radius=100., inner_radius=1e-4):
        if not (duration > 0 and 0 < inner_radius < outer_radius and max_step > 0
                and rtol > 0 and atol > 0):
            raise ValueError('positive time/tolerances/step and ordered radii required')
        state = np.asarray(state, float)
        if state.shape != (24,) or not np.isfinite(state).all():
            raise ValueError('a finite 24-component MPD state is required')
        radius = np.linalg.norm(state[1:4])
        if not inner_radius < radius < outer_radius:
            raise ValueError('initial position must lie between the stopping radii')
        def rhs(t, y):
            out = np.asarray(self._rhs_jit(self.xp.asarray(y)))
            if not np.isfinite(out).all():
                raise FloatingPointError('nonfinite MPD derivative or non-timelike velocity')
            return out
        def outside(t, y): return outer_radius-np.linalg.norm(y[1:4])
        def centre(t, y): return np.linalg.norm(y[1:4])-inner_radius
        def spin_bound(t, y): return self.spin_limit-self.invariants(y)['spin_curvature_ratio']
        for event in (outside, centre, spin_bound):
            event.terminal, event.direction = True, -1
        result = solve_ivp(rhs, (0., duration), state, method='DOP853', rtol=rtol,
                           atol=atol, max_step=max_step, events=(outside, centre, spin_bound))
        history = [self.invariants(y) for y in result.y.T]
        first = history[0]
        drifts = {k: max(abs(row[k]-first[k]) for row in history)
                  for k in ('mass2', 'spin2', 'energy', 'angular_momentum')}
        conservation_ok = all(error <= 1e-7*max(abs(first[k]),1e-12)
                              for k,error in drifts.items())
        conservation_ok = conservation_ok and max(row['ssc_max'] for row in history) <= 1e-8
        stop = next((label for label, hits in zip(('outer_radius', 'inner_radius', 'spin_limit'),
                                                result.t_events) if len(hits)), 'duration')
        return dict(time=result.t, state=result.y.T, invariants=history,
                    success=bool(result.success and conservation_ok),
                    integrator_success=bool(result.success), conservation_ok=bool(conservation_ok),
                    stop=stop, message=result.message,
                    absolute_drift=drifts,
                    ssc_max=max(row['ssc_max'] for row in history),
                    norm_error=max(abs(row['velocity_norm']+1) for row in history))


def matched_controls(system, position, *, spin=1e-3, speed=.2):
    """Positive/negative/zero spin with the same spin-corrected Killing energy.

    Match the outward-speed root. A missing root is reported, rather than
    comparing unequal launch energies and calling the difference an accelerator.
    """
    from scipy.optimize import brentq
    reference = system.initial_state(position, spin=0., speed=speed)
    target = system.invariants(reference)['energy']
    states = {'zero': reference}
    for label, value in (('positive', abs(spin)), ('negative', -abs(spin))):
        def energy_error(v):
            state = system.initial_state(position, spin=value, speed=v)
            return system.invariants(state)['energy']-target
        root = brentq(energy_error, 0., .95, xtol=1e-13)
        states[label] = system.initial_state(position, spin=value, speed=root)
    return states
