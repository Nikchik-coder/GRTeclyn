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

__all__ = ["observables", "identity_gates", "C_GATE"]

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
    """mu_+ and mu_- from f_x at the end nodes (exact on the arctan grid),
    plus the spread of f_x over y there (must vanish: f is
    theta-independent at the infinities)."""
    if sol.map_name != "arctan":
        raise NotImplementedError(
            "mu_+- from the end nodes is the arctan-grid formula; other "
            "maps read the mass from the far field (P4)")
    fx = sol.jet("f", 1, 0)
    spread = max(float(np.ptp(fx[0])), float(np.ptp(fx[-1])))
    return (cv.mu_plus_from_fx(float(np.mean(fx[0])), sol.eta0),
            cv.mu_minus_from_fx(float(np.mean(fx[-1])), sol.eta0),
            spread)


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
