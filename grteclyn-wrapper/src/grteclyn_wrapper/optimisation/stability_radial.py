"""The m = 0, J = 0 radial growth rate: the stability screen's first rung.

Linear radial perturbations of a static spherically symmetric phantom
wormhole with potential, in the solver's chart (zero shift, conformal
spatial form -- a complete gauge that is REGULAR through the throat,
where the literature's areal gauge degenerates):

    ds^2 = -e^F dt^2 + P^2 e^{-F} [d eta^2 + h dOmega^2],
    (F, P, psi)(t, eta) = background(eta) + (dF, dP, dpsi)(eta) e^{lam t}.

The five linearized rows are derived and machine-checked by
scripts/optimisation/derive_radial_perturbation.py (its stage `forms`
verifies the transcription here on every run): E_ee, E_thth and the KG
row are imposed -- three equations, three unknowns, lam entering ONLY
as lam^2, the clean quadratic structure rotation breaks -- and E_tt,
E_teta are the unimposed constraint monitors, evaluated on every
eigenmode.  A mode that solves the imposed rows but fails the monitors
is a gauge/constraint artifact and is discarded, never reported as an
instability; a Newton-style failure of the whole pencil is a resolution
verdict (the campaign discipline, applied to eigenmodes).

The discrete problem: Chebyshev-Lobatto collocation in xi with the
arctan map, Dirichlet (decaying) rows at xi = +-1, and the generalized
eigenproblem K u = -lam^2 M u solved dense.

The physical eigenvalue is selected by TWO-GRID MATCHING, not by mode
shape (2026-10-28, the drainhole debug): the pencil keeps exact gauge
solutions -- e.g. (dF, dP) -> (c, c/2), dpsi -> 0 satisfies all five
rows at ANY lam, leaking through the two Dirichlet rows -- so every
eigenvector is gauge-polluted (the drainhole's physical mode carries
dpsi/peak ~ 1e-4) and no localization or constraint filter works:
gauge modes satisfy the monitors too.  What gauge junk cannot do is
hold its eigenvalue still under a grid change; the physical lam^2
agreed to 0.7 % between grids while every spurious value moved by
factors.  The monitors are still reported, but on a polluted vector
they sit at the pollution level (~1e-2), not at round-off: the gate is
eigenvalue convergence plus the published rate, the campaign's
calibration discipline.  Gate: scripts/optimisation/check_growth_rate.py
reproduces the static drainhole rate |omega_I| eta0 = 0.390 (the
published second-order value quoted by plot_instability_curve.py,
arXiv:2301.05243 C = 1 at J = 0).
"""

from __future__ import annotations

import numpy as np

__all__ = ["radial_coefficients", "radial_rows", "growth_rate"]

#: the perturbation jets each row reads
JETS = tuple(f"{f}_{k}" for f in ("dF", "dP", "dpsi") for k in (0, 1, 2))


def radial_coefficients(*, eta, eta0, bg, V0, V1, V2, lam2):
    """Per-jet coefficients of the five linearized rows at the nodes,
    transcribed from derive_radial_perturbation.py (stage rows,
    2026-10-28).  ``bg`` maps F0_0..F0_2, P0_0..P0_2, psi0_1, psi0_2 to
    node values; the teta row is the printed one divided by lam.
    Elementwise in numpy; every absent jet is zero."""
    h = eta * eta + eta0 * eta0
    EF = np.exp(bg["F0_0"])
    F1, F2 = bg["F0_1"], bg["F0_2"]
    P0, P1, P2 = bg["P0_0"], bg["P0_1"], bg["P0_2"]
    s1, s2 = bg["psi0_1"], bg["psi0_2"]
    z = np.zeros_like(h + 0.0 * EF)

    ee = {
        "dF_0": -P0**2 * (2 * EF * V0 + lam2) / (2 * EF**2),
        "dF_1": -(2 * F1 * P0 * h - 2 * P0 * eta - P1 * h)
        / (2 * P0 * h),
        "dF_2": 0.5 + z,
        "dP_0": -(EF**2 * F1 * P0 * P1 * h - 4 * EF**2 * P0 * P1 * eta
                  - 4 * EF**2 * P0 * P2 * h + 8 * EF**2 * P1**2 * h
                  - 4 * EF * P0**4 * V0 * h - 2 * P0**4 * h * lam2)
        / (2 * EF**2 * P0**3 * h),
        "dP_1": (F1 * P0 * h - 4 * P0 * eta + 8 * P1 * h)
        / (2 * P0**2 * h),
        "dP_2": -2.0 / P0,
        "dpsi_0": P0**2 * V1 / EF,
        "dpsi_1": 4.0 * s1,
    }
    thth = {
        "dF_0": -P0**2 * h * (2 * EF * V0 + lam2) / (2 * EF**2),
        "dF_1": (2 * P0 * eta + P1 * h) / (2 * P0),
        "dF_2": h / 2,
        "dP_0": -(EF**2 * F1 * P1 * h - 6 * EF**2 * P1 * eta
                  - 2 * EF**2 * P2 * h - 4 * EF * P0**3 * V0 * h
                  - 2 * P0**3 * h * lam2) / (2 * EF**2 * P0**2),
        "dP_1": (F1 * h - 6 * eta) / (2 * P0),
        "dP_2": -h / P0,
        "dpsi_0": P0**2 * V1 * h / EF,
    }
    kg = {
        "dF_0": P0**3 * V1 * h / (2 * EF),
        "dP_0": (2 * EF * (h * s2 + 2 * eta * s1)
                 - 3 * P0**2 * V1 * h) / (2 * EF),
        "dP_1": s1 * h,
        "dpsi_0": -P0**3 * h * (EF * V2 + 2 * lam2) / (2 * EF**2),
        "dpsi_1": 2 * P0 * eta + P1 * h,
        "dpsi_2": P0 * h,
    }
    tt = {
        "dF_0": (4 * EF**2 * F1 * P0 * eta + 2 * EF**2 * F1 * P1 * h
                 + 2 * EF**2 * F2 * P0 * h - 2 * EF * P0**3 * V0 * h
                 + 3 * P0**3 * h * lam2) / (2 * P0**3 * h),
        "dF_1": EF**2 * (2 * P0 * eta + P1 * h) / (2 * P0**3 * h),
        "dF_2": EF**2 / (2 * P0**2),
        "dP_0": -(4 * EF**2 * F1 * P0 * eta + 3 * EF**2 * F1 * P1 * h
                  + 2 * EF**2 * F2 * P0 * h + 6 * P0**3 * h * lam2)
        / (2 * P0**4 * h),
        "dP_1": EF**2 * F1 / (2 * P0**3),
        "dpsi_0": -EF * V1 + z,
    }
    teta = {
        "dF_0": -F1 / 2,
        "dF_1": 1.0 + z,
        "dP_0": (F1 * P0 + 2 * P1) / P0**2,
        "dP_1": -2.0 / P0,
        "dpsi_0": 2.0 * s1,
    }
    out = {"ee": ee, "thth": thth, "kg": kg, "tt": tt, "teta": teta}
    for row in out.values():
        for jet in JETS:
            row.setdefault(jet, z)
    return out


def radial_rows(*, eta, eta0, bg, pert, V0, V1, V2, lam2):
    """The five rows' values at the nodes (teta divided by lam):
    the coefficients dotted with the perturbation jets."""
    co = radial_coefficients(eta=eta, eta0=eta0, bg=bg,
                             V0=V0, V1=V1, V2=V2, lam2=lam2)
    return {label: sum(c[jet] * pert[jet] for jet in JETS)
            for label, c in co.items()}


def _pencil_lam2(*, eta0, nx, background, radial_map, want_mode=None):
    """All real lam^2 > 0 eigenvalues of the pencil at this grid,
    descending; with ``want_mode`` (a lam^2), also that eigenvalue's
    node-value mode, the node data and the background values."""
    import scipy.linalg as sla

    from grteclyn_wrapper.analysis.spinning_wormhole.spectral import (
        ArctanMap,
        lobatto,
    )

    rmap = radial_map if radial_map is not None else ArctanMap(eta0=eta0)
    sx, Dx = lobatto(nx)
    n = nx + 1
    eta_i = rmap.eta(sx[1:-1])
    deta_i = rmap.deta(sx[1:-1])
    d2eta_i = rmap.d2eta(sx[1:-1])
    bgv = background(eta_i)
    V0, V1, V2 = bgv["V0"], bgv["V1"], bgv["V2"]

    # d/deta and d2/deta2 on node values, interior rows
    D1 = (1.0 / deta_i)[:, None] * Dx[1:-1]
    D2 = ((1.0 / deta_i**2)[:, None] * (Dx @ Dx)[1:-1]
          - (d2eta_i / deta_i**3)[:, None] * Dx[1:-1])
    ops = {0: np.eye(n)[1:-1], 1: D1, 2: D2}

    def block_matrix(rows, lam2):
        co = radial_coefficients(eta=eta_i, eta0=eta0, bg=bgv,
                                 V0=V0, V1=V1, V2=V2, lam2=lam2)
        out = []
        for label in rows:
            blocks = []
            for f in ("dF", "dP", "dpsi"):
                A = sum(np.asarray(co[label][f"{f}_{k}"]
                                   * np.ones(n - 2))[:, None] * ops[k]
                        for k in (0, 1, 2))
                blocks.append(A)
            out.append(np.hstack(blocks))
        return np.vstack(out)

    imposed = ("ee", "thth", "kg")
    K_i = block_matrix(imposed, 0.0)
    M_i = block_matrix(imposed, 1.0) - K_i
    # assemble with Dirichlet rows at xi = +-1 per field
    K = np.zeros((3 * n, 3 * n))
    M = np.zeros((3 * n, 3 * n))
    for r in range(3):
        K[r * n + 1: (r + 1) * n - 1] = K_i[r * (n - 2): (r + 1) * (n - 2)]
        M[r * n + 1: (r + 1) * n - 1] = M_i[r * (n - 2): (r + 1) * (n - 2)]
    for f in range(3):
        for j in (f * n, f * n + n - 1):
            K[j, j] = 1.0
    vals, vecs = sla.eig(K, -M)
    realpos = []
    for i in range(vals.size):
        v = vals[i]
        if (np.isfinite(v) and abs(v.imag) <= 1e-8 * max(1.0, abs(v))
                and v.real > 0.0):
            realpos.append((float(v.real), i))
    realpos.sort(key=lambda t: -t[0])
    lam2s = [v for v, _ in realpos]
    if want_mode is None:
        return lam2s, None
    i = min(realpos, key=lambda t: abs(t[0] - want_mode))[1]
    u = vecs[:, i].real.reshape(3, n)
    u = u / np.abs(u).max()
    node = {"eta_i": eta_i, "deta_i": deta_i, "d2eta_i": d2eta_i,
            "Dx": Dx, "bgv": bgv, "V": (V0, V1, V2)}
    return lam2s, (u, node)


def growth_rate(*, eta0: float, nx: int, background, radial_map=None,
                match_frac: float = 0.7, match_tol: float = 0.05,
                lam2_min: float = 1e-3, n_report: int = 5):
    """The largest radial growth rate of a static background.

    ``background(eta)`` returns the dict radial_coefficients needs
    (F0_0..psi0_2 plus V0, V1, V2) at the given eta nodes.  Solves the
    pencil K u = -lam^2 M u on nx+1 Lobatto nodes under the arctan map
    (or ``radial_map``) AND on the coarser ``match_frac``-grid, keeps
    the real lam^2 > lam2_min values that agree between the two grids
    to ``match_tol`` relative (gauge junk cannot hold an eigenvalue
    still under a grid change -- the module docstring has why mode
    shape cannot be the filter) and returns the largest, with the
    unimposed E_tt and E_teta residuals of its (gauge-polluted) mode
    relative to the row's own coefficient scale."""
    nx2 = max(20, int(round(match_frac * nx)))
    lam2_f, _ = _pencil_lam2(eta0=eta0, nx=nx, background=background,
                             radial_map=radial_map)
    lam2_c, _ = _pencil_lam2(eta0=eta0, nx=nx2, background=background,
                             radial_map=radial_map)
    matched = [v for v in lam2_f
               if v > lam2_min
               and any(abs(v - w) <= match_tol * max(v, w)
                       for w in lam2_c)]
    if not matched:
        return {"lam": 0.0, "lam2_top": [], "stable": True,
                "lam2_unmatched": lam2_f[:n_report]}

    lam2 = matched[0]
    drift = min(abs(lam2 - w) / lam2 for w in lam2_c)
    _, mode = _pencil_lam2(eta0=eta0, nx=nx, background=background,
                           radial_map=radial_map, want_mode=lam2)
    u, node = mode
    eta_i, deta_i, d2eta_i = node["eta_i"], node["deta_i"], node["d2eta_i"]
    Dx, bgv = node["Dx"], node["bgv"]
    V0, V1, V2 = node["V"]
    n = nx + 1
    pert = {}
    for k, f in enumerate(("dF", "dP", "dpsi")):
        arr = u[k]
        pert[f"{f}_0"] = arr[1:-1]
        pert[f"{f}_1"] = ((1.0 / deta_i) * (Dx @ arr)[1:-1])
        pert[f"{f}_2"] = ((1.0 / deta_i**2) * (Dx @ (Dx @ arr))[1:-1]
                          - (d2eta_i / deta_i**3) * (Dx @ arr)[1:-1])
    rows = radial_rows(eta=eta_i, eta0=eta0, bg=bgv, pert=pert,
                       V0=V0, V1=V1, V2=V2, lam2=lam2)
    co = radial_coefficients(eta=eta_i, eta0=eta0, bg=bgv,
                             V0=V0, V1=V1, V2=V2, lam2=lam2)

    def rel(label):
        scale = max(np.max(np.abs(np.asarray(co[label][jet])
                                  * np.ones(n - 2))) for jet in JETS)
        return float(np.max(np.abs(rows[label]))) / max(scale, 1e-300)

    return {"lam": float(np.sqrt(lam2)), "lam2_top": matched[:n_report],
            "stable": False, "mode": u, "match_drift": drift,
            "tt_res": rel("tt"), "teta_res": rel("teta"),
            "imposed_res": max(rel(k) for k in ("ee", "thth", "kg"))}
