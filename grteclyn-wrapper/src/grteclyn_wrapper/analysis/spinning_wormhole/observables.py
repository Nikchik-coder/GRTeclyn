"""Observables and identity gates of one Solution (SpinningSolver.md P2).

Everything here is independent of the solve: the solver imposes only E_f,
E_w, E_N and the boundary data, so the constraint E_c, the constancy of
D^2 and of the flux J(x), and the Smarr relation all TEST a solution
rather than restate it (section 8's per-solution rows).  Generalizes
backgrounds._throat_numbers to theta-dependent omega and nu.

The 1/C^2 factors amplify round-off near the compactified ends, so the
D^2 / E_c / J gates run on the nodes with C >= C_GATE = 0.05; the
full-grid numbers are reported alongside, never gated.
"""

from __future__ import annotations

import math

import numpy as np

from . import conventions as cv
from .equations import residual_forms
from .solution import Solution
from .spectral import cheb_eval

__all__ = ["observables", "identity_gates", "C_GATE", "exotic_matter",
           "static_exotic_matter"]

C_GATE = 0.05


def _interior(sol: Solution):
    """Geometry and jets on the interior nodes, plus the C mask."""
    m = sol.radial_map
    xi = sol.sx[1:-1]
    eta = m.eta(xi)[:, None]
    deta = m.deta(xi)[:, None]
    d2eta = m.d2eta(xi)[:, None]
    h = eta**2 + sol.eta0**2
    jets = {}
    for tag in ("f", "w", "N"):
        jets[tag] = sol.jet(tag)[1:-1]
        jets[f"{tag}_x"] = sol.jet(tag, 1, 0)[1:-1]
        jets[f"{tag}_xx"] = sol.jet(tag, 2, 0)[1:-1]
        jets[f"{tag}_y"] = sol.jet(tag, 0, 1)[1:-1]
        jets[f"{tag}_yy"] = sol.jet(tag, 0, 2)[1:-1]
    E = residual_forms(np.exp, eta0=sol.eta0, y=sol.sy[None, :], eta=eta,
                       deta=deta, d2eta=d2eta, jets=jets)
    c2 = sol.eta0**2 / h[:, 0]
    return {"eta": eta, "deta": deta, "h": h, "jets": jets, "E": E,
            "mask_x": c2 >= C_GATE**2}


def _quad(sol: Solution, n_g: int = 64):
    """Gauss-Legendre in mu with the y-node interpolation matrix."""
    mu_g, w_g = np.polynomial.legendre.leggauss(n_g)
    by = cheb_eval(sol.sy, np.eye(sol.ny + 1), 2.0 * mu_g**2 - 1.0)
    return mu_g, w_g, by


def j_of_x(sol: Solution, work=None) -> tuple[np.ndarray, np.ndarray]:
    """The flux J on every interior column (conventions: J(x) is constant),
    and the column mask away from the compactified ends."""
    w = work or _interior(sol)
    mu_g, w_g, by = _quad(sol)
    f_g = w["jets"]["f"] @ by.T
    weta_g = (w["jets"]["w_x"] / w["deta"]) @ by.T
    integ = (w_g * (1.0 - mu_g**2))[None, :] * np.exp(-2 * f_g) * weta_g
    return (-(w["h"][:, 0] ** 2 / 8.0) * integ.sum(axis=1), w["mask_x"])


def _mu_ends(sol: Solution) -> tuple[float, float, float]:
    """mu_+ and mu_- from the far field, plus their spread over y (must
    vanish: f is theta-independent at the infinities).

    On the arctan grid the end nodes give mu exactly (f_x(+-1) =
    +-pi mu/eta0).  On other maps the end node can be degenerate
    (logstretch with L >= 4 has eta'/eta^2 -> 0 there), so mu =
    +-eta^2 f_x/(2 eta') is read one node in, where |eta| is already
    huge (~eta0 (nx/pi)^L) and the 1/eta correction sits below
    round-off."""
    fx = sol.jet("f", 1, 0)
    if sol.map_name == "arctan":
        spread = max(float(np.ptp(fx[0])), float(np.ptp(fx[-1])))
        return (cv.mu_plus_from_fx(float(np.mean(fx[0])), sol.eta0),
                cv.mu_minus_from_fx(float(np.mean(fx[-1])), sol.eta0),
                spread)
    m = sol.radial_map
    xp, xm = float(sol.sx[1]), float(sol.sx[-2])
    mu_p = m.eta(xp) ** 2 * fx[1] / (2.0 * m.deta(xp))
    mu_m = -(m.eta(xm) ** 2) * fx[-2] / (2.0 * m.deta(xm))
    spread = max(float(np.ptp(mu_p)), float(np.ptp(mu_m)))
    return float(np.mean(mu_p)), float(np.mean(mu_m)), spread


def _area_of_eta(sol: Solution, eta_vals: np.ndarray) -> np.ndarray:
    """Area of the eta = const surfaces: 2 pi h int e^{-f + nu/2} dmu."""
    mu_g, w_g, _ = _quad(sol)
    m = sol.radial_map
    out = np.empty(np.atleast_1d(eta_vals).size)
    for k, ev in enumerate(np.atleast_1d(eta_vals)):
        xi = np.full(mu_g.size, m.xi_of_eta(ev))
        y = 2.0 * mu_g**2 - 1.0
        f = sol.eval_xy("f", xi, y)
        nham = sol.eval_xy("N", xi, y) * (1.0 - mu_g**2)
        out[k] = (2.0 * math.pi * (ev**2 + sol.eta0**2)
                  * float(w_g @ np.exp(-f + 0.5 * nham)))
    return out


def _throat(sol: Solution) -> dict:
    """The area-minimizing eta = const surface and its numbers."""
    mu_g, w_g, by = _quad(sol)
    F = sol.F[1:-1] @ by.T
    Nf = sol.N[1:-1] @ by.T
    m = sol.radial_map
    eta_i = m.eta(sol.sx[1:-1])
    h_i = eta_i**2 + sol.eta0**2
    area_nodes = (2.0 * math.pi * h_i
                  * (np.exp(-F + 0.5 * Nf * (1.0 - mu_g**2)[None, :]) @ w_g))
    k = int(np.argmin(area_nodes))
    lo = eta_i[min(k + 1, eta_i.size - 1)]   # eta decreases with node index
    hi = eta_i[max(k - 1, 0)]
    g = 0.5 * (math.sqrt(5.0) - 1.0)
    for _ in range(60):
        a1, a2 = hi - g * (hi - lo), lo + g * (hi - lo)
        if _area_of_eta(sol, np.array([a1]))[0] < _area_of_eta(sol, np.array([a2]))[0]:
            hi = a2
        else:
            lo = a1
    eta_t = 0.5 * (lo + hi)
    area_t = float(_area_of_eta(sol, np.array([eta_t]))[0])
    xi_t = float(m.xi_of_eta(eta_t))
    h_t = eta_t**2 + sol.eta0**2

    f_eq = float(sol.eval_xy("f", np.array([xi_t]), np.array([-1.0]))[0])
    r_eq = math.exp(-0.5 * f_eq) * math.sqrt(h_t)
    th_g, th_w = np.polynomial.legendre.leggauss(48)
    th = 0.25 * math.pi * (th_g + 1.0)           # (0, pi/2); mirror-symmetric
    y_th = np.cos(2.0 * th)
    xi_v = np.full(th.size, xi_t)
    f_m = sol.eval_xy("f", xi_v, y_th)
    nu_m = sol.eval_xy("N", xi_v, y_th) * np.sin(th) ** 2
    r_pol = (math.sqrt(h_t) / math.pi) * 2.0 * 0.25 * math.pi * float(
        np.exp(0.5 * (nu_m - f_m)) @ th_w)
    omega_t = float(sol.eval_xy("w", np.array([xi_t]), np.array([-1.0]))[0])
    return {
        "eta_throat": float(eta_t),
        "area_throat": area_t,
        "R_A": math.sqrt(area_t / (4.0 * math.pi)),
        "R_eq": r_eq, "R_pol": r_pol,
        "Omega_throat": omega_t,
        "v_e": cv.v_e(r_eq, omega_t),
    }


def identity_gates(sol: Solution, work=None) -> dict:
    """The per-solution identity rows of section 8 (all relative)."""
    w = work or _interior(sol)
    E, jets, h = w["E"], w["jets"], w["h"]
    mask = w["mask_x"]

    d2 = E["D2"]
    d2_med = float(np.median(d2[mask]))
    d2_spread = float(np.max(np.abs(d2[mask] - d2_med)) / max(abs(d2_med), 1e-300))
    d2_spread_full = float(np.max(np.abs(d2 - d2_med)) / max(abs(d2_med), 1e-300))

    e2f = np.exp(-2 * jets["f"])
    oneminus = 1.0 - sol.sy[None, :]
    term_scale = (np.abs(4 * jets["f_x"] * jets["f_y"]) + np.abs(jets["N_x"])
                  + np.abs(2 * w["eta"] * w["deta"] / h
                           * (jets["N"] - oneminus * jets["N_y"]))
                  + np.abs(2 * h * oneminus * e2f * jets["w_x"] * jets["w_y"]))
    scale_floor = max(float(np.max(term_scale[mask])), 1e-300)
    ec_rel = float(np.max(np.abs(E["E_c"][mask])) / scale_floor)

    j_cols, _ = j_of_x(sol, work=w)
    j_med = float(np.median(j_cols[mask]))
    if max(abs(j_med), float(np.max(np.abs(j_cols[mask])))) < 1e-13:
        j_spread = 0.0          # the static member: no flux anywhere
    else:
        j_spread = float(np.max(np.abs(j_cols[mask] - j_med)) / abs(j_med))

    mu_p, mu_m, mu_spread = _mu_ends(sol)
    smarr = cv.smarr_residual(mu_p, mu_m, sol.omega_inf, j_med)
    tails = sol.tail_ratios()
    return {
        "D2_median": d2_med, "D2_spread": d2_spread,
        "D2_spread_fullgrid": d2_spread_full,
        "Ec_rel": ec_rel,
        "J_flux": j_med, "J_spread": j_spread,
        "smarr_rel": smarr, "mu_end_spread": mu_spread,
        "tail_max": max(tails.values()), "tails": tails,
    }


def observables(sol: Solution) -> dict:
    """Every scalar of section 2's observables list, plus the gates."""
    w = _interior(sol)
    gates = identity_gates(sol, work=w)
    mu_p, mu_m, _ = _mu_ends(sol)
    throat = _throat(sol)
    d = math.sqrt(max(gates["D2_median"], 0.0))
    jets = w["jets"]
    # Ergosurface reach: g_tt = 0 where h sin^2 th omega^2 e^{-2f} = 1.
    ergo = h_ergo = (w["h"] * (1.0 - sol.sy[None, :]) / 2.0
                     * jets["w"] ** 2 * np.exp(-2 * jets["f"]))
    out = {
        "eta0": sol.eta0, "gamma": sol.gamma,
        "omega_inf": sol.omega_inf,
        "mu_plus": mu_p, "mu_minus": mu_m, "M_ADM": mu_p,
        "J": gates["J_flux"], "D": d,
        "omega_throat_eq": throat["Omega_throat"],
        "ergo_max": float(np.max(ergo[w["mask_x"]])),
        **throat,
    }
    if mu_p != 0.0:
        out["J_over_M2"] = out["J"] / mu_p**2
    out["J_over_A"] = out["J"] / max(throat["area_throat"], 1e-300)
    out["J_over_A_extremal_frac"] = 8.0 * math.pi * out["J_over_A"]
    return out


def symmetric_checks(sol: Solution) -> dict:
    """Family (b) extras (gamma = 0), checked and never imposed: mirror
    symmetry f(x) = f(-x), omega(x) + omega(-x) = omega_inf, and
    omega_0 = omega_inf / 2 (CKK's symmetric family)."""
    mirror_f = float(np.max(np.abs(sol.F - sol.F[::-1])))
    mirror_w = float(np.max(np.abs(sol.W + sol.W[::-1] - sol.omega_inf)))
    w0 = float(sol.eval_xy("w", np.array([0.0]), np.array([-1.0]))[0])
    return {"mirror_f": mirror_f, "mirror_w": mirror_w,
            "omega0": w0,
            "omega0_rel_defect": abs(w0 - 0.5 * sol.omega_inf)
            / max(abs(w0), 1e-300)}


def ergosurface_equator(sol: Solution) -> dict:
    """The equatorial ergosurface: g_tt = 0 where e^{2f} = h omega^2 on
    the equator.  Returns the outer root eta_ergo (None without an
    ergoregion) and, for the symmetric family, the deviation from CKK's
    law arctan(eta_ergo/eta0) = arccos(2 omega_0)."""
    m = sol.radial_map
    xi = np.linspace(-0.98, 0.98, 393)
    eta = m.eta(xi)
    f = sol.eval_xy("f", xi, np.full(xi.size, -1.0))
    w = sol.eval_xy("w", xi, np.full(xi.size, -1.0))
    g = np.exp(2 * f) - (eta**2 + sol.eta0**2) * w**2
    sign = np.sign(g)
    flips = np.nonzero(np.diff(sign))[0]
    if flips.size == 0:
        return {"eta_ergo": None}
    from scipy.optimize import brentq

    def gtt(e):
        x = np.atleast_1d(m.xi_of_eta(e))
        y = np.array([-1.0])
        return (float(np.exp(2 * sol.eval_xy("f", x, y)[0]))
                - (e * e + sol.eta0**2)
                * float(sol.eval_xy("w", x, y)[0]) ** 2)

    k = flips[-1]                              # the outer boundary
    eta_ergo = brentq(gtt, eta[k], eta[k + 1], xtol=1e-12)
    out = {"eta_ergo": float(eta_ergo)}
    w0 = float(sol.eval_xy("w", np.array([0.0]), np.array([-1.0]))[0])
    if abs(2 * w0) <= 1.0:
        law = math.acos(2 * w0)
        out["ckk_law_deviation"] = float(
            math.atan(eta_ergo / sol.eta0) - law)
    return out


def exotic_matter(sol: Solution, d: float, n_x: int = 96, n_mu: int = 48) -> float:
    """The phantom field's volume integral quantifier (Visser, Kar & Dadhich,
    PRL 90, 201102), VIQ = int (rho + p_eta) dV over the t = const slice,
    both universes; d is the solution's scalar charge D.

    The field is exactly psi = (D/eta0)(atan(eta/eta0) - pi/2), the table's
    phi = psi / sqrt(4 pi), so rho + p_eta = -g^{eta eta} phi'^2 and, with
    dV = e^{-3f/2 + nu} h sin(theta) deta dtheta dvarphi, nu drops out:
    VIQ = -(D^2/2) int deta/h int dmu e^{-f/2}, mu = cos(theta).  Negative,
    and -pi eta0 for the static Ellis wormhole.  Gauss-Legendre in x on the
    solution's own radial map and in mu."""
    xg, wx = np.polynomial.legendre.leggauss(n_x)
    mg, wm = np.polynomial.legendre.leggauss(n_mu)
    m = sol.radial_map
    jac = m.deta(xg) / (m.eta(xg) ** 2 + sol.eta0**2)          # deta / h per dx
    f = sol.eval_grid("f", xg, 2.0 * mg**2 - 1.0)               # y = cos 2 theta
    return float(-0.5 * d * d * np.einsum("i,i,j,ij->", wx, jac, wm, np.exp(-0.5 * f)))


def static_exotic_matter(eta0: float, gamma: float) -> tuple[float, float]:
    """(VIQ, R_e) of the static member in closed form: f = (gamma/2)(1 - x)
    gives int dx e^{-f/2} = (e^{2k} - 1)/k, k = -gamma/4, and the throat (the
    area minimum, eta = mu_+) has R_e = e^{-f/2} sqrt(mu_+^2 + eta0^2)."""
    st = cv.static_member(eta0, gamma)
    k = -gamma / 4.0
    ix = math.expm1(2.0 * k) / k if k else 2.0
    viq = -math.pi * st["D"] ** 2 * ix / (2.0 * eta0)
    eta_t = st["eta_throat"]
    f_t = cv.static_f_of_x(2.0 / math.pi * math.atan(eta_t / eta0), gamma)
    return viq, math.exp(-0.5 * f_t) * math.hypot(eta_t, eta0)
