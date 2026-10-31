"""Axisymmetric minimal surfaces on the stationary spatial slice.

The graph is xi(mu) = sum c_l T_l(2 mu**2 - 1). This enforces smoothness
at the axis and reflection at the equator without coordinate boundary rows.
All areas below are in grid units; multiply by sigma**2 for physical area.
"""
from __future__ import annotations

import numpy as np
from numpy.polynomial import chebyshev as ch
from .exoticity import _grid_eval
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import cheb_coeffs, cheb_eval


class SurfaceFunctional:
    def __init__(self, eta0, rmap, sx, sy, order, quadrature=None):
        self.eta0, self.map, self.order = eta0, rmap, order
        self.mu, self.weights = np.polynomial.legendre.leggauss(
            quadrature or max(64, 4 * (order + 1)))
        y = 2 * self.mu**2 - 1
        self.basis = ch.chebvander(y, order)
        self.derivative = np.stack([
            ch.chebval(y, ch.chebder(np.eye(order+1)[k])) * 4*self.mu
            for k in range(order+1)], axis=1)
        self.cx = cheb_coeffs(np.eye(len(sx)), axis=0)
        self.by = cheb_eval(sy, np.eye(len(sy)), y)
        self.sx, self.sy = sx, sy

    def coordinates(self, c, xp=np):
        xi = xp.asarray(self.basis) @ c
        xi_mu = xp.asarray(self.derivative) @ c
        if self.map.name == 'arctan':
            eta = self.map.eta0 * xp.tan(xp.pi*xi/2)
            deriv = self.map.eta0*xp.pi/2 / xp.cos(xp.pi*xi/2)**2
        elif self.map.name == 'logstretch':
            t = self.map.L*xp.arctanh(xi)
            eta = self.map.eta0*xp.sinh(t)
            deriv = self.map.eta0*self.map.L*xp.cosh(t)/(1-xi**2)
        else:
            raise ValueError(f'unsupported surface map: {self.map.name}')
        return xi, eta, deriv*xi_mu

    def area(self, c, F, N, B, xp=np):
        xi, eta, eta_mu = self.coordinates(c, xp)
        t = xp.cos(xp.arccos(xi)[:, None]*xp.arange(len(self.sx))) @ xp.asarray(self.cx)
        f, n, b = (xp.sum((t @ a)*xp.asarray(self.by), axis=1) for a in (F,N,B))
        s2 = 1-self.mu**2
        h = eta**2+self.eta0**2
        density = b**2*xp.exp(-f+n*s2/2)*xp.sqrt(h*(h+s2*eta_mu**2))
        return 2*xp.pi*xp.sum(xp.asarray(self.weights)*density)


def surface_geometry(eta0, rmap, sx, sy, F, N, B, coefficients):
    """Area, circumferences and the graph, evaluated independently of Newton."""
    c = np.asarray(coefficients)
    sf = SurfaceFunctional(eta0, rmap, sx, sy, len(c)-1, max(128,8*len(c)))
    area = float(sf.area(c,F,N,B))
    xe = float(ch.chebval(-1.,c))
    eta_e = float(rmap.eta(xe))
    f, b = (float(_grid_eval(sx,sy,a,[xe],[-1])[0,0]) for a in (F,B))
    re = b*np.exp(-f/2)*np.sqrt(eta_e**2+eta0**2)
    t,w = np.polynomial.legendre.leggauss(128)
    theta = np.pi*(t+1)/2
    y = np.cos(2*theta)
    x = ch.chebval(y,c)
    eta = rmap.eta(x)
    eta_theta = rmap.deta(x)*ch.chebval(y,ch.chebder(c))*(-2*np.sin(2*theta))
    vals = [np.diag(_grid_eval(sx,sy,a,x,y)) for a in (F,N,B)]
    f,n,b = vals
    rp = .5*float(w @ (b*np.exp((-f+n*np.sin(theta)**2)/2)*
                        np.sqrt(eta**2+eta0**2+eta_theta**2)))
    return dict(area_throat=area, R_A=np.sqrt(area/(4*np.pi)), R_e=float(re),
                R_pol=rp, eta_throat=eta_e, surface_coefficients=c.tolist())


def find_surface(eta0,rmap,sx,sy,F,N,B,xi_start=0.):
    """Seed the coupled graph constraint from a frozen reference metric."""
    from scipy.optimize import minimize
    from .solver.device import configure_jax
    jax=configure_jax()
    import jax.numpy as jnp
    sf=SurfaceFunctional(eta0,rmap,sx,sy,len(sy)-1)
    fun=jax.jit(lambda c:sf.area(c,jnp.asarray(F),jnp.asarray(N),jnp.asarray(B),jnp))
    grad=jax.jit(jax.grad(fun))
    seed=np.zeros(len(sy)); seed[0]=xi_start
    norm=float(fun(seed))
    result=minimize(lambda c:float(fun(c))/norm,seed,
                    jac=lambda c:np.asarray(grad(c))/norm,method='SLSQP',
                    constraints={'type':'ineq','fun':lambda c:.999-abs(sf.basis@c)},
                    options={'ftol':1e-14,'maxiter':200})
    if not result.success or not np.isfinite(result.fun):
        raise RuntimeError(f'minimal surface seed failed: {result.message}')
    return result.x


def _polish_minimum(fun, grad, hess, feasible, point):
    """Resolve the gradient after an area-based minimizer stops near roundoff."""
    point = np.asarray(point).copy()
    for _ in range(8):
        g = np.asarray(grad(point))
        if not np.isfinite(g).all() or np.max(abs(g)) < 1e-9:
            break
        h = np.asarray(hess(point))
        if not np.isfinite(h).all() or np.linalg.eigvalsh(h)[0] <= 0:
            break
        step = np.linalg.solve(h, -g)
        value = float(fun(point))
        for scale in 2. ** -np.arange(16):
            trial = point + scale * step
            if not feasible(trial):
                continue
            trial_value = float(fun(trial))
            # Near the minimum, area changes are below floating-point noise;
            # require a smaller gradient as well as no resolved area increase.
            slack = 16 * np.finfo(float).eps * max(1., abs(value))
            if (np.isfinite(trial_value) and trial_value <= value + slack
                    and np.max(abs(np.asarray(grad(trial)))) < np.max(abs(g))):
                point = trial
                break
        else:
            break
    return point


def verify_surface(eta0, rmap, sx, sy, F, N, B, coefficients, *, discover=True):
    """Independent higher-order minimisation, Hessian and extra-throat search.

    A finite collection of starts diagnoses additional graph throats; it is
    not a global topology theorem. Unresolved minima fail the certification.
    """
    from scipy.optimize import minimize
    from .solver.device import configure_jax
    jax = configure_jax()
    import jax.numpy as jnp
    old = np.asarray(coefficients)
    order = max(len(old)+3, 2*(len(old)-1))
    sf = SurfaceFunctional(eta0,rmap,sx,sy,order,max(160,8*(order+1)))
    fun = jax.jit(lambda c: sf.area(c,jnp.asarray(F),jnp.asarray(N),jnp.asarray(B),jnp))
    grad, hess = jax.jit(jax.grad(fun)), jax.jit(jax.hessian(fun))
    start = np.pad(old,(0,order+1-len(old)))
    area0 = float(fun(start))
    # The graph must stay strictly inside the compactified endpoints.
    constraint = {'type':'ineq', 'fun':lambda c: .999-np.abs(sf.basis@c),
                  'jac':lambda c: -np.sign(sf.basis@c)[:,None]*sf.basis}
    starts = [start]
    if discover:
        xs = np.linspace(-.95,.95,49)
        areas = np.array([float(fun(np.r_[x,np.zeros(order)])) for x in xs])
        starts += [np.r_[xs[i],np.zeros(order)] for i in range(1,len(xs)-1)
                   if areas[i]<areas[i-1] and areas[i]<areas[i+1]]
    minima, unresolved = [], False
    for seed in starts:
        result = minimize(lambda c: float(fun(c))/area0,seed,
                          jac=lambda c: np.asarray(grad(c))/area0,
                          constraints=constraint,method='SLSQP',
                          options={'ftol':1e-13,'maxiter':150})
        if result.success:
            result.x = _polish_minimum(
                lambda c: float(fun(c))/area0,
                lambda c: np.asarray(grad(c))/area0,
                lambda c: np.asarray(hess(c))/area0,
                lambda c: bool(np.all(constraint['fun'](c) > 0)), result.x)
        eigen = np.linalg.eigvalsh(np.asarray(hess(result.x))/area0)
        stationarity = float(np.max(abs(np.asarray(grad(result.x))))/area0)
        good = bool(result.success and stationarity<1e-7 and eigen[0]>0)
        if not good:
            unresolved = True
            continue
        if not any(np.max(abs(sf.basis@(result.x-c)))<1e-5 for c in minima):
            minima.append(result.x)
    drift = min((abs(float(fun(c))/area0-1) for c in minima),default=float('inf'))
    gradient=float(np.max(abs(np.asarray(grad(start))))/area0)
    hessian_min=float(np.linalg.eigvalsh(np.asarray(hess(start))/area0)[0])
    return dict(surface_verified=bool(len(minima)==1 and not unresolved and drift<=1e-8
                                      and gradient<1e-7 and hessian_min>0),
                surface_minima=len(minima), surface_unresolved=unresolved,
                surface_area_drift=float(drift) if np.isfinite(drift) else None,
                surface_gradient=gradient, surface_hessian_min=hessian_min)
