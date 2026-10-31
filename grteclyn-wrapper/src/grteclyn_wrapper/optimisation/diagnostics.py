"""Stationary physical diagnostics on saved fields; no solves or JAX required.

All backgrounds here use physical eta and omega. NEC directions have unit
energy in the local zero-angular-momentum frame. Ray integrals instead use
unit Killing energy at the positive infinity; these normalisations differ.
"""
from dataclasses import dataclass
import json

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq, minimize, minimize_scalar

from grteclyn_wrapper.analysis.spinning_wormhole.solution import Solution
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import ArctanMap, MAPS, lobatto
from .exoticity import _grid_eval, nec_rays, throat, tidal


@dataclass
class Background:
    eta0: float
    rmap: object
    F: np.ndarray
    W: np.ndarray
    N: np.ndarray
    B: np.ndarray
    PSI: np.ndarray
    J: float = 0.

    def __post_init__(self):
        self.sx, self.dx = lobatto(self.F.shape[0]-1)
        self.sy, self.dy = lobatto(self.F.shape[1]-1)
        self.psi_x = self.dx @ self.PSI
        self.psi_y = self.PSI @ self.dy.T
        self.geometry = throat(self.eta0, self.rmap, self.sx, self.sy,
                               self.dx, self.F, self.N, self.B)
        self.xi_t = float(self.rmap.xi_of_eta(self.geometry['eta_throat']))

    def sample(self, field, xi, y):
        return _grid_eval(self.sx, self.sy, field, xi, y)

    def local(self, xi, mu):
        """Tensor samples: physical gradients, positive NEC deficits and lapse."""
        xi, mu = np.atleast_1d(xi), np.atleast_1d(mu)
        y = 2*mu**2-1
        f, n, b = (self.sample(a, xi, y) for a in (self.F, self.N, self.B))
        nu = n*(1-mu**2)[None, :]
        eta, ep = self.rmap.eta(xi), self.rmap.deta(xi)
        h = eta**2+self.eta0**2
        radial = self.sample(self.psi_x, xi, y)/ep[:, None]
        angular = -4*mu[None, :]*np.sqrt(1-mu**2)[None, :]*self.sample(self.psi_y, xi, y)
        radial *= np.exp((f-nu)/2)/b
        angular *= np.exp((f-nu)/2)/(b*np.sqrt(h[:, None]))
        return dict(grad_r=radial, grad_theta=angular,
                    nec_r=radial**2/(4*np.pi), nec_theta=angular**2/(4*np.pi),
                    nec_max=(radial**2+angular**2)/(4*np.pi),
                    lapse=np.exp(f/2), proper_x=b*np.exp((nu-f)/2)*ep[:, None])

    def shell(self, xi, n_mu=64):
        """Positive radial VIQ density per xi and area of eta-constant spheres."""
        xi = np.atleast_1d(xi)
        mu, wm = np.polynomial.legendre.leggauss(n_mu)
        y = 2*mu**2-1
        f, n, b = (self.sample(a, xi, y) for a in (self.F, self.N, self.B))
        psi_x = self.sample(self.psi_x, xi, y)
        h = self.rmap.eta(xi)**2+self.eta0**2
        density = .5*h/self.rmap.deta(xi)*((b*np.exp(-f/2)*psi_x**2)@wm)
        area = 2*np.pi*h*((b**2*np.exp(-f+n*(1-mu**2)[None, :]/2))@wm)
        return density, np.sqrt(area/(4*np.pi))

    def integral(self, lo=-1., hi=1., order=384):
        q, w = np.polynomial.legendre.leggauss(order)
        xi = (hi+lo)/2+(hi-lo)*q/2
        return float((hi-lo)/2*(w @ self.shell(xi)[0]))

    def proper_distance(self, xi, mu=0., order=384):
        q, w = np.polynomial.legendre.leggauss(order)
        x = (xi+self.xi_t)/2+(xi-self.xi_t)*q/2
        return float((xi-self.xi_t)/2*(w@self.local(x, [mu])['proper_x'][:, 0]))

    def crossing(self, ell, mu=0., rtol=1e-10):
        """Zero-L null ray at fixed theta: xi(ell), t(ell), throat at ell=t=0.

        Only axis/equator rays keep theta. Endpoints are specified by signed
        proper radial distance on this ray, not by a common coordinate eta.
        t uses the positive-infinity clock; d t / d ell = 1 / lapse.
        """
        if mu not in (0., 1.):
            raise ValueError('Only axis and equator are constant-theta null geodesics')
        ell = np.asarray(ell)
        if ell.min() >= 0 or ell.max() <= 0:
            raise ValueError('Crossing endpoints must straddle the throat')
        def rhs(l, z):
            a = self.local([z[0]], [mu])
            return [1/a['proper_x'][0, 0], 1/a['lapse'][0, 0]]
        out = np.empty((2, len(ell)))
        for side, end in ((ell <= 0, ell.min()), (ell > 0, ell.max())):
            sol = solve_ivp(rhs, [0., end], [self.xi_t, 0.], rtol=rtol,
                            atol=rtol*.01, dense_output=True)
            if not sol.success:
                raise RuntimeError(sol.message)
            out[:, side] = sol.sol(ell[side])
        return out

    def tide(self, xi, v):
        return tidal(self.eta0, self.rmap, self.sx, self.sy, self.dx, self.dy,
                     self.F, self.W, self.N, self.B, xi, v=v)['max_abs']

    def tidal_peak(self, xi, v):
        """Sample and refine every local maximum, including endpoint maxima."""
        values = np.array([self.tide(x, v) for x in xi])
        best = float(values.max())
        for k in range(1, len(xi)-1):
            if values[k] >= max(values[k-1], values[k+1]):
                opt = minimize_scalar(lambda x: -self.tide(x, v),
                                      bounds=(xi[k-1], xi[k+1]), method='bounded',
                                      options={'xatol': 1e-10})
                if not opt.success:
                    raise RuntimeError('Tidal peak refinement failed')
                best = max(best, -float(opt.fun))
        return best, values

    def local_peak(self, xi, mu, key, values):
        """Refine the sampled peak in radius and angle, retaining boundaries."""
        best = float(values.max())
        for i, j in [np.unravel_index(k, values.shape)
                     for k in np.argsort(values.ravel())[-3:]]:
            scale = max(best, 1e-30)
            fit = minimize(lambda z: -self.local([z[0]], [z[1]])[key][0, 0]/scale,
                           [xi[i], mu[j]], bounds=[(xi[0], xi[-1]), (0., 1.)],
                           method='L-BFGS-B', options={'ftol': 1e-12, 'gtol': 1e-7})
            best = max(best, -float(fit.fun)*scale)
        return best


def potential(path):
    with np.load(path, allow_pickle=False) as z:
        m = json.loads(str(z['meta']))
        arrays = {k: np.array(z[k]) for k in ('F', 'W', 'N', 'B', 'PSI')}
    # Independent refinement diagnostics retain nested metadata.
    if 'diagnostics' in m:
        m = dict(m, **m['config'], **m['diagnostics'])
    scale = m['sigma']
    params = dict(m['radial_map']); name = params.pop('name')
    params.pop('class', None); params['eta0'] = scale
    arrays['W'] /= scale
    bg = Background(scale, MAPS[name](**params), **arrays, J=m['J'])
    np.testing.assert_allclose(bg.geometry['R_e'], m['R_e'], rtol=1e-9)
    return bg


def classical(path):
    s = Solution.load(path)
    eta = s.radial_map.eta(np.clip(s.sx, -1+1e-15, 1-1e-15))
    psi = s.observables['D']/s.eta0*(np.arctan(eta/s.eta0)-np.pi/2)
    psi[0], psi[-1] = 0., -np.pi*s.observables['D']/s.eta0
    return Background(s.eta0, s.radial_map, s.F, s.W, s.N, np.ones_like(s.F),
                      np.broadcast_to(psi[:, None], s.F.shape).copy(), s.observables['J'])


def static(eta0=2., gamma=-np.pi, nx=210, ny=42):
    sx, _ = lobatto(nx); sy, _ = lobatto(ny)
    zero = np.zeros((len(sx), len(sy)))
    f = .5*gamma*(1-sx[:, None])+zero
    d = eta0*np.sqrt(1+(gamma/(2*np.pi))**2)
    psi = -np.pi*d/(2*eta0)*(1-sx[:, None])+zero
    return Background(eta0, ArctanMap(eta0), f, zero, zero, zero+1, psi)


def analyse(bg, order=384, samples=161, extent=10., rtol=1e-10):
    """Diagnostics over +/- extent R_e; total VIQ/ray NEC span both infinities."""
    re = bg.geometry['R_e']
    # Dense near the throat without losing the two outer endpoints.
    u = np.linspace(-np.arcsinh(extent), np.arcsinh(extent), samples)
    ell = re*np.sinh(u)
    xi, t = bg.crossing(ell, rtol=rtol)
    mu = np.linspace(0., 1., 65)
    local = bg.local(xi, mu)
    density, ra = bg.shell(xi)
    viq = bg.integral(order=order)
    # Central 90% of the radial bill, including tails outside the plot window.
    quantiles = [brentq(lambda x: bg.integral(hi=x, order=order)/viq-q,
                       -.999999, .999999, xtol=1e-11) for q in (.05, .95)]
    width = (bg.proper_distance(quantiles[1], order=order)
             - bg.proper_distance(quantiles[0], order=order))
    rays = nec_rays(bg.eta0, bg.rmap, bg.sx, bg.sy, bg.dx, bg.N, bg.B, bg.PSI, n_x=order)
    summary = dict(**bg.geometry, J=bg.J, VIQ=-viq, X=viq/re,
                   scalar_excursion=float(abs(bg.PSI[-1, 0]-bg.PSI[0, 0])),
                   bill_fraction_in_window=bg.integral(lo=xi[0], hi=xi[-1], order=order)/viq,
                   bill_width90_over_Re=width/re,
                   nec_peak_Re2=bg.local_peak(xi, mu, 'nec_max', local['nec_max'])*re**2,
                   radial_nec_peak_Re2=bg.local_peak(xi, mu, 'nec_r', local['nec_r'])*re**2,
                   angular_nec_peak_Re2=bg.local_peak(xi, mu, 'nec_theta', local['nec_theta'])*re**2,
                   oblateness=re/bg.geometry['R_pol'],
                   lapse_min=float(local['lapse'].min()),
                   photon_energy_max=float(1/local['lapse'].min()),
                   transit_equator_over_Re=float((t[-1]-t[0])/re),
                   nec_ray_equator_Re=-rays['equator']*re,
                   nec_ray_axis_Re=-rays['axis']*re)
    for velocity, key in ((0., 'tidal_v0_Re2'), (.5, 'tidal_v05_Re2')):
        peak, values = bg.tidal_peak(xi, velocity)
        summary[key] = peak*re**2
        if velocity == .5:
            tides = values
    _, ta = bg.crossing(ell, mu=1., rtol=rtol)
    summary['transit_axis_over_Re'] = float((ta[-1]-ta[0])/re)
    profile = dict(ell_over_Re=ell/re, xi=xi, mu=mu, areal_radius_over_Re=ra/re,
                   bill_per_ell=density/local['proper_x'][:, 0],
                   grad_r_Re=local['grad_r']*re, grad_theta_Re=local['grad_theta']*re,
                   nec_r_Re2=local['nec_r']*re**2, nec_theta_Re2=local['nec_theta']*re**2,
                   nec_max_Re2=local['nec_max']*re**2, lapse=local['lapse'],
                   tidal_v05_Re2=tides*re**2, time_over_Re=t/re)
    return summary, profile


def spherical_tidal_check(bg, h_fraction=.005):
    """Independent proper-distance finite differences for a spherical metric.

    E_rad = alpha''/alpha; E_lat(v) = gamma_v^2 [alpha' R'/(alpha R)
    - v^2 R''/R]. Five-point differences avoid the spectral Riemann code.
    """
    if bg.J != 0:
        raise ValueError('Spherical check requires J=0')
    re = bg.geometry['R_e']; step = h_fraction*re
    rows = []
    for center in (-.5*re, 0., .5*re):
        ell = np.r_[[-2*re], center+step*np.arange(-2, 3), [2*re]]
        xi, _ = bg.crossing(ell, rtol=2e-13)
        x = xi[1:-1]
        f, b = (bg.sample(a, x, [-1.])[:, 0] for a in (bg.F, bg.B))
        alpha = np.exp(f/2)
        radius = b*np.exp(-f/2)*np.sqrt(bg.rmap.eta(x)**2+bg.eta0**2)
        def first(v): return (v[0]-8*v[1]+8*v[3]-v[4])/(12*step)
        def second(v): return (-v[0]+16*v[1]-30*v[2]+16*v[3]-v[4])/(12*step**2)
        radial = second(alpha)/alpha[2]
        for v in (0., .5):
            lateral = (first(alpha)*first(radius)/(alpha[2]*radius[2])
                       - v*v*second(radius)/radius[2])/(1-v*v)
            expected = max(abs(radial), abs(lateral))
            actual = bg.tide(x[2], v)
            rows.append(dict(ell_over_Re=center/re, speed=v, spectral=actual,
                             finite_difference=expected,
                             scaled_error=abs(actual-expected)/max(abs(actual), 1/re**2)))
    return rows
