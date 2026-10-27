"""The exotic-matter bill of a matter-solver solution (campaign M, step 2).

The bill is the published Fig. 3e quantity X = |VIQ| / R_e: the phantom's
volume integral quantifier (Visser, Kar & Dadhich, PRL 90, 201102) over
the throat's equatorial radius.  For the matter ansatz

    ds^2 = -e^f dt^2 + B^2 e^{-f} [e^nu (d eta^2 + h d theta^2)
                                   + h sin^2 theta (d phi - omega dt)^2]

rho + p_eta = -g^{eta eta} psi_eta^2 in the solver's psi normalization
(the potential cancels between rho and p_eta) and the slice's volume
element is B^3 e^{-3f/2 + nu} h sin theta, so nu drops out and

    VIQ = -(1/2) int d eta int d mu  B e^{-f/2} h psi_eta^2,   mu = cos theta,

which at B = 1, psi_eta = D/h is observables.exotic_matter's
-(D^2/2) int d eta/h int d mu e^{-f/2}.  The throat is the minimum of the
eta = const area 2 pi h int d mu B^2 e^{-f + nu/2}, and R_e = B e^{-f/2}
sqrt(h) on its equator (observables._throat's R_eq at B = 1, which
places the minimum by golden section, to about 1e-8).

Fields are node arrays on the solver's tensor Chebyshev-Lobatto grid,
evaluated off the nodes by spectral.cheb_eval (which returns the node
value on an exact hit, so a throat on the xi = 0 node is safe).  numpy
only.
"""

from __future__ import annotations

import math

import numpy as np

from .spectral import cheb_eval

__all__ = ["bill", "throat", "nec_rays", "exotic_x"]


def _grid_eval(sx, sy, A, xi, y):
    """A on the tensor grid xi x y, shape (len(xi), len(y))."""
    rows = cheb_eval(sx, np.asarray(A), np.atleast_1d(xi))
    return cheb_eval(sy, rows.T, np.atleast_1d(y)).T


def bill(eta0, rmap, sx, sy, Dx, F, B, PSI, n_x: int = 96,
         n_mu: int = 48) -> float:
    """VIQ (negative), Gauss-Legendre in xi on the solver's radial map and
    in mu, the quadrature of observables.exotic_matter."""
    xg, wx = np.polynomial.legendre.leggauss(n_x)
    mg, wm = np.polynomial.legendre.leggauss(n_mu)
    y = 2.0 * mg**2 - 1.0
    f = _grid_eval(sx, sy, F, xg, y)
    b = _grid_eval(sx, sy, B, xg, y)
    psi_x = _grid_eval(sx, sy, Dx @ np.asarray(PSI), xg, y)
    h = rmap.eta(xg) ** 2 + eta0**2
    # d eta = eta' d xi and psi_eta = psi_x / eta'
    weight = (h / rmap.deta(xg))[:, None]
    integ = b * np.exp(-0.5 * f) * weight * psi_x**2
    return float(-0.5 * np.einsum("i,j,ij->", wx, wm, integ))


def throat(eta0, rmap, sx, sy, Dx, F, N, B, n_mu: int = 64) -> dict:
    """The area-minimizing eta = const surface: eta_t, its area and R_e.
    A node scan brackets the minimum and the root of dA/dxi, from the
    spectral xi-derivatives, places it to round-off (a golden section on
    A itself stops near 1e-8: the minimum is flat, and R_e is not)."""
    from scipy.optimize import brentq

    mu, wmu = np.polynomial.legendre.leggauss(n_mu)
    y = 2.0 * mu**2 - 1.0
    sin2 = 1.0 - mu**2
    F, N, B = (np.asarray(a) for a in (F, N, B))
    jets = (F, N, B, Dx @ F, Dx @ N, Dx @ B)

    def parts(xi):
        xi = np.atleast_1d(np.asarray(xi, float))
        f, nn, b, f_x, n_x, b_x = (_grid_eval(sx, sy, A, xi, y)
                                   for A in jets)
        g = b**2 * np.exp(-f + 0.5 * nn * sin2)
        eta = rmap.eta(xi)
        return eta, eta**2 + eta0**2, g, g * (2.0 * b_x / b - f_x
                                             + 0.5 * n_x * sin2)

    def area(xi):
        _, h, g, _ = parts(xi)
        return 2.0 * math.pi * h * (g @ wmu)

    def darea(xi):
        eta, h, g, g_x = parts(xi)
        return float((2.0 * math.pi * (2.0 * eta * rmap.deta(xi) * (g @ wmu)
                                       + h * (g_x @ wmu)))[0])

    xi_i = sx[1:-1]
    k = int(np.argmin(area(xi_i)))
    lo = xi_i[min(k + 1, xi_i.size - 1)]       # xi falls with node index
    hi = xi_i[max(k - 1, 0)]
    xi_t = brentq(darea, lo, hi, xtol=1e-15, rtol=4.0 * np.finfo(float).eps)
    eta_t = float(rmap.eta(np.array([xi_t]))[0])
    xi_v, y_eq = np.array([xi_t]), np.array([-1.0])
    f_eq = _grid_eval(sx, sy, F, xi_v, y_eq)[0, 0]
    b_eq = _grid_eval(sx, sy, B, xi_v, y_eq)[0, 0]
    return {"eta_throat": eta_t, "area_throat": float(area(xi_t)[0]),
            "R_e": float(b_eq * math.exp(-0.5 * f_eq)
                         * math.sqrt(eta_t**2 + eta0**2))}


def nec_rays(eta0, rmap, sx, sy, Dx, N, B, PSI, n_x: int = 96) -> dict:
    """The NEC integral int T_ab k^a k^b d lambda along the two radial null
    geodesics through the throat with zero angular momentum: the axis
    (y = 1) and the equator (y = -1), the only places such a ray keeps
    theta.  With unit energy at infinity, t' = e^{-f} and eta' =
    e^{-nu/2} / B (the ray co-rotates, phi' = omega t'); the potential
    drops out on a null vector and T_ab k^a k^b = -(k.d psi)^2 / (4 pi), so

        I = -(1/(4 pi)) int d eta e^{-nu/2} psi_eta^2 / B,

    -D^2 / (8 eta0^3) for the static Ellis throat."""
    xg, wx = np.polynomial.legendre.leggauss(n_x)
    deta = rmap.deta(xg)
    out = {}
    for name, yv in (("axis", 1.0), ("equator", -1.0)):
        y = np.array([yv])
        nu = _grid_eval(sx, sy, N, xg, y)[:, 0] * (1.0 - yv) / 2.0
        b = _grid_eval(sx, sy, B, xg, y)[:, 0]
        psi_x = _grid_eval(sx, sy, Dx @ np.asarray(PSI), xg, y)[:, 0]
        # d eta = eta' d xi and psi_eta = psi_x / eta'
        integ = np.exp(-0.5 * nu) * psi_x**2 / (b * deta)
        out[name] = float(-(wx @ integ) / (4.0 * math.pi))
    return out


def exotic_x(eta0, rmap, sx, sy, Dx, F, N, B, PSI) -> dict:
    """The Fig. 3e quantity X = |VIQ| / R_e, with VIQ and the throat."""
    viq = bill(eta0, rmap, sx, sy, Dx, F, B, PSI)
    th = throat(eta0, rmap, sx, sy, Dx, F, N, B)
    return {"VIQ": viq, **th, "X": abs(viq) / th["R_e"]}
