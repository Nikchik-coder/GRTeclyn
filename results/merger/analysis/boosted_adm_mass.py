#!/usr/bin/env python3
r"""The boosted pairs' ADM mass: the solve's face estimate plus what it leaves out.

The mode-3 solve prints ``M_ADM_face = M_bg + 2 <r w>`` (constraint_solve.dat),
with the background mass ``M_bg = sum_X [sigma_X m_X + 2 s_X]``: each throat's
rescaled drainhole mass and twice its puncture shift ``s_X = c_X - c_sup,X``.
That is the ADM mass of a conformally flat background ``Psi_bg -> 1 + M_bg/2r``.
The exact-boost background (momentum_model = 1) is neither: each throat is the
static drainhole seen from a frame moving at v (gamma v = p / m, set from the
UNSCALED m; the solve rescales a and m by sigma and keeps v), so its conformal
factor falls off with the Lorentz-contracted radius and its metric carries the
anisotropy eps e_i e_j ~ 4 gamma^2 v^2 m / r.  The full surface integral

    E = (1/16 pi) oint (d_j g_ij - d_i g_jj) dS^i

of one such throat is gamma sigma m (its rest mass times gamma, as a Lorentz
boost must give), and a shift s / r_rest contributes 2 s asinh(gamma v) /
(gamma v), not 2 s.  So, with w's monopole unchanged,

    M_ADM = M_ADM_face + sum_X (gamma_X - 1) sigma_X m_X
                       + 2 sum_X s_X [asinh(gamma_X v_X) / (gamma_X v_X) - 1].

The first term is the throats' kinetic energy: 3-17 % of the pair's mass at
p = 0.25-0.60, which the face estimate dropped (2026-10-06; until then the
boosted pairs' quoted mass FELL with p, 2.18 / 2.08 / 1.91).  The script checks
both closed-form statements on each run's own (sigma, p, s) by the full
surface integral of the background's closed forms (BinaryWormholeInitialData::
boost_background, one throat, two radii extrapolated in 1/R) and refuses if
either is off by more than 1e-4.

c_sup is rebuilt from the pack (superposed_puncture_coefficient on the rescaled
throats, the companion at its rest-frame distance); for the three fly-by/plunge
pairs it reproduces the run logs' "superposed" values to 1e-9.

Writes ``boosted_adm_mass.tsv`` beside this script, one row per packed
exact-boost solve.  The ledger's ``mergers_solved_madm(col="M_ADM_boost")`` and
the figures read it.  Binaries built from 2026-10-06 on print the same sum as
constraint_solve.dat's ``M_ADM_boost`` column; where a run has it, the two must
agree to 1e-6.

What it does not fix: ``2 <r w>`` is read on the level-0 boundary cells, where
the Robin condition leaves w a small offset, so the face estimate sits below the
volume identity wherever both exist -- 2.8 % for the d = 12, p = 0.12
Bowen-York pair on the production box (2.2107 against 2.2748; L = 128), whose
exact-boost twin reads 2.2127 here.

    python results/merger/analysis/boosted_adm_mass.py [pack]   # pack = results/merger
"""

from __future__ import annotations

import math
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "boosted_adm_mass.tsv"
TOL = 1.0e-4


def _params(path: pathlib.Path) -> dict[str, list[float]]:
    out: dict[str, list[float]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if "=" not in line:
            continue
        key, val = (s.strip() for s in line.split("=", 1))
        try:
            out[key] = [float(x) for x in val.split()]
        except ValueError:
            continue
    return out


def _solve_row(path: pathlib.Path) -> dict[str, float]:
    names = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            toks = line.lstrip("#").split()
            if toks and toks[0] == "time":
                names = toks
            continue
        if names and line.strip():
            return dict(zip(names, (float(x) for x in line.split())))
    raise ValueError(f"{path}: no data row")


def _u(r, a, m):
    """drainhole_u: the static lapse exponent, u -> -m / r."""
    X = (r - a * a / (4.0 * r)) / a
    return (m / a) * (np.arctan(X) - np.pi / 2.0)


def _c_sup(a, m, a_Y, m_Y, dist):
    """superposed_puncture_coefficient: (a/2) e^{pi m/2a} e^{-u_Y(dist)/2}."""
    c = 0.5 * a * math.exp(0.5 * math.pi * m / a)
    if a_Y > 0.0 and m_Y != 0.0:
        c *= math.exp(-0.5 * float(_u(dist, a_Y, m_Y)))
    return c


def _rest_distance(d, vY):
    """companion_distance: |d + (gamma - 1)(e.d) e| for the companion's boost."""
    speed = float(np.linalg.norm(vY))
    if speed <= 0.0:
        return float(np.linalg.norm(d))
    e = np.asarray(vY) / speed
    g = 1.0 / math.sqrt(1.0 - speed * speed)
    return float(np.linalg.norm(d + (g - 1.0) * (e @ d) * e))


def _metric(pts, a, m, gv, s):
    """One exact-boost throat's spatial metric (boost along y), shift s / r_rest."""
    e = np.array([0.0, 1.0, 0.0])
    g = math.sqrt(1.0 + gv * gv)
    v = gv / g
    xr = pts + (g - 1.0) * (pts @ e)[:, None] * e
    r = np.linalg.norm(xr, axis=-1)
    u = _u(r, a, m)
    Om = 1.0 + a * a / (4.0 * r * r)
    Psi = np.exp(-0.5 * u) * np.sqrt(Om) + s / r
    eps = g * g * v * v * (1.0 - np.exp(4.0 * u) / Om ** 2)
    G = np.eye(3)[None] + eps[:, None, None] * np.outer(e, e)[None]
    return Psi[:, None, None] ** 4 * G


def _adm(a, m, gv, s, R, nmu=48, nph=96, h=0.25):
    mu, w = np.polynomial.legendre.leggauss(nmu)
    ph = np.arange(nph) * 2.0 * np.pi / nph
    MU, PH = np.meshgrid(mu, ph, indexing="ij")
    st = np.sqrt(1.0 - MU ** 2)
    n = np.stack([st * np.cos(PH), st * np.sin(PH), MU], -1).reshape(-1, 3)
    W = (np.repeat(w[:, None], nph, 1) * (2.0 * np.pi / nph)).reshape(-1) * R * R
    dg = []
    for k in range(3):
        dk = np.zeros(3)
        dk[k] = h
        dg.append((_metric(R * n + dk, a, m, gv, s) - _metric(R * n - dk, a, m, gv, s))
                  / (2.0 * h))
    dg = np.stack(dg, 1)
    flux = np.einsum("pjij->pi", dg) - np.einsum("pijj->pi", dg)
    return float(np.sum(W * np.einsum("pi,pi->p", flux, n)) / (16.0 * np.pi))


def _adm_inf(a, m, gv, s, R1=2000.0, R2=8000.0):
    """E(R) = E_inf + k / R from two radii."""
    E1, E2 = _adm(a, m, gv, s, R1), _adm(a, m, gv, s, R2)
    return (R2 * E2 - R1 * E1) / (R2 - R1)


def main(argv: list[str]) -> int:
    pack = pathlib.Path(argv[1]) if len(argv) > 1 else HERE.parent
    campaign = pack / "campaign"
    rows = []
    for cs in sorted(campaign.rglob("constraint_solve.dat")):
        rel = cs.parent.relative_to(campaign)
        if rel.parts[0] == "00_archive":
            continue
        pfile = cs.parent / "evolution_params.txt"
        if not pfile.exists():
            continue
        p = _params(pfile)
        if p.get("wormhole_momentum_model", [0])[0] != 1:
            continue
        r = _solve_row(cs)
        b0 = [p["wormhole_throat_radius_A"][0], p["wormhole_throat_radius_B"][0]]
        m0 = [p["wormhole_drainhole_mass_A"][0], p["wormhole_drainhole_mass_B"][0]]
        ctr = [np.array(p["wormhole_centerA"]), np.array(p["wormhole_centerB"])]
        P = [np.array(p["wormhole_momentumA"]), np.array(p["wormhole_momentumB"])]
        sig = [r["sigma_A"], r["sigma_B"]]
        c = [r["c_A"], r["c_B"]]
        vel = []
        for X in range(2):
            pp = float(np.linalg.norm(P[X]))
            v = pp / math.sqrt(m0[X] ** 2 + pp ** 2) if pp > 0 else 0.0
            vel.append(v * P[X] / pp if pp > 0 else np.zeros(3))
        kinetic, shift_corr, csup, gammas = 0.0, 0.0, [], []
        for X in range(2):
            Y = 1 - X
            a, m = sig[X] * b0[X], sig[X] * m0[X]
            dist = _rest_distance(ctr[X] - ctr[Y], vel[Y])
            cs_X = _c_sup(a, m, sig[Y] * b0[Y], sig[Y] * m0[Y], dist)
            s = c[X] - cs_X
            speed = float(np.linalg.norm(vel[X]))
            g = 1.0 / math.sqrt(1.0 - speed * speed)
            gv = g * speed
            factor = math.asinh(gv) / gv if gv > 0 else 1.0
            kinetic += (g - 1.0) * m
            shift_corr += 2.0 * s * (factor - 1.0)
            csup.append(cs_X)
            gammas.append(g)
            if gv > 0:   # the two closed-form statements, on this throat
                E0 = _adm_inf(a, m, gv, 0.0)
                Es = _adm_inf(a, m, gv, s) - E0
                if abs(E0 / (g * m) - 1.0) > TOL:
                    raise SystemExit(f"{rel}: one throat integrates to {E0:.6f}, "
                                     f"not gamma sigma m = {g * m:.6f}")
                if abs(Es - 2.0 * s * factor) > TOL * max(1.0, abs(Es)):
                    raise SystemExit(f"{rel}: the shift integrates to {Es:.6f}, "
                                     f"not 2 s asinh(gv)/gv = {2 * s * factor:.6f}")
        face = r["M_ADM_face"]
        total = face + kinetic + shift_corr
        # Binaries built after 2026-10-06 print the same sum (M_ADM_boost).
        if "M_ADM_boost" in r and abs(r["M_ADM_boost"] - total) > 1e-6:
            raise SystemExit(f"{rel}: the run's M_ADM_boost {r['M_ADM_boost']:.8f} is not "
                             f"face + correction = {total:.8f}")
        rows.append((str(rel), float(np.linalg.norm(P[0])), gammas[0], sig[0], sig[1],
                     c[0], csup[0], c[1], csup[1], face, kinetic, shift_corr, total))

    header = ("run\tp\tgamma\tsigma_A\tsigma_B\tc_A\tc_sup_A\tc_B\tc_sup_B\t"
              "M_ADM_face\tkinetic\tshift_corr\tM_ADM_boost")
    lines = ["# The exact-boost pairs' ADM mass (boosted_adm_mass.py): M_ADM_boost = "
             "M_ADM_face + kinetic + shift_corr.",
             "# kinetic = sum (gamma - 1) sigma m; shift_corr = 2 sum s [asinh(gamma v)/"
             "(gamma v) - 1], s = c - c_sup.  Inputs: each run's packed",
             "# constraint_solve.dat (first row) and evolution_params.txt.",
             header]
    for row in rows:
        lines.append("\t".join([row[0], f"{row[1]:.4g}"] +
                               [f"{x:.10g}" for x in row[2:]]))
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for row in rows:
        print(f"{row[0]:<80s} p {row[1]:.3g}  face {row[9]:.5f}  + kin {row[10]:.5f}"
              f"  + shift {row[11]:+.5f}  = {row[12]:.5f}")
    print(f"wrote {OUT} ({len(rows)} runs)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
