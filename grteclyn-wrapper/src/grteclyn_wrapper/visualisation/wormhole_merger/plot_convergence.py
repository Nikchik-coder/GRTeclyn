#!/usr/bin/env python3
r"""Convergence on one strip: the static throat's order, the wave at two resolutions, the extraction radius.

(a) The static throat from exact data at levels 2/3/4 (``single_hold_ml2_t100``,
    ``single_hold_t100``, ``single_hold_ml4_t100``; finest dx = 1/8, 1/16,
    1/32): the three-level factor Q(t) = (R_2 - R_3)/(R_3 - R_4) of the minimal
    areal radius at every dump t = 0-23 (level 2 ends at t = 24.17), on the
    factors 4, 8, 16 of orders n = 2, 3, 4.  To t = 10 the static error of
    reading the exact data dominates: Q = 4.5-5.0, n = 2.2-2.3 (the t = 0
    errors against R_star = sqrt(5) exp(arctan(2)/2) are 2.17e-3, 4.23e-4,
    5.41e-5).  Over t = 12-20 the evolution's own error takes over: Q = 8.1-9.9,
    n = 3.0-3.3, except at the one dump t = 16 (Q = 5.9), where level 2's R
    reads 1.2e-3 below both its neighbours, the dump before its minimum moves
    one coarse cell out (r = 1.565 -> 1.690).  Every dump is drawn; the order
    ranges (``EVOL_SKIP``) leave t = 16 out.
(b) The d = 12, p = 0.12 spiral whose momentum is Bowen-York extrinsic
    curvature (otherwise the paper's setup), L = 128, |r Psi4^22| at R = 20:
    level 5 to t = 56 (the two runs' trust windows are 56.5 and 57.2), its
    difference from level 4, and level 4 with the ball R <= 33.6 refined to
    level 1 (dx = 0.25 instead of 0.5 at R = 20 and 28) minus plain level 4,
    to the refined arm's stop at t = 40.  Both differences are fractions of
    the level-5 burst peak (1.93e-2 at t = 44): 0.38 % and 0.15 %.
(c) The radiated energy E(R) on each sphere over the outermost sphere's,
    against R/M, by the paper's band integral (``psi4_math``'s
    ``_compute_radiated_energy`` with the peak of the smoothed burst PSD, as
    ``plot_psi4_ligo``), over one retarded window t - R <= u_max per record
    (``NEAR_ZONE``): the head-on to 56 (E flat to 1.5 % for R/M >= 12,
    E(10)/E(44) = 1.28), the d = 6 merger to 55.96 (the last u its R = 44
    record covers), the fly-by to 67.6 on R = 20/28 (the outer spheres stop
    short of it), and the two vacuum controls to 70.
(d) CONV-fz: the far-zone head-on (FARZONE-ho, the gallery's head-on row) on
    its L = 512 box at finest dx = 1/16, 1/32, 1/64 (max_level 5 / 6 / 7, its
    params otherwise), to t = 100: the collision-axis |r Psi4^20| at R = 10 of
    the finest level packed and each neighbouring pair's difference.  A level
    joins once its run is packed (``CONV_FZ``; the level-7 twin since its pack,
    2026-10-08).  Levels 5 / 6: the difference peaks at 0.55 % of the level-6
    peak (t = 38); E at R = 10 on (c)'s head-on window differs by 0.29 %; both
    find the common MOTS from t = 18, its R and M_MS equal to 0.084 % (t = 26,
    as it settles; 1e-4 at birth and at t = 100).  Levels 6 / 7: 0.54 % of the
    level-7 peak (t = 39), E by 0.092 %, the MOTS to 0.078 % (t = 27).  So E
    converges at order 1.67, while the pointwise difference does not shrink
    over t = 36-60 (it does before and after).
(e) The same levels' Hamiltonian constraint at t = 100, shell averages of
    H_ADM outside the common MOTS (gold, its largest coordinate extent), read
    on level 4 (dx = 1/8): at t = 100 levels 6 and 7 sit within |x| < 2.5 and
    1.25 of the merged centre, so level 4 is the grid every level shares there.
    The table (``FZ_HAM``) is written on the node from each run's Chk02500 by
    grteclyn-wrapper/scripts/analysis/merger_feedback/c_checkpoint_hamiltonian.py.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_convergence

The file lives under ``figures/00_code_health/``; every number is printed.
The ledger reads (a) through its own recomputation (``extract_single``)
and (b)/(c)/(d) through ``psi_difference``,
``near_zone_ratio``, ``near_zone_spread`` and the ``fz_*`` functions here
(``extract_waves``).

WHY: 2026-10-06, the referee: the paper had no Richardson convergence plot.
2026-10-08: (d), the binary's own three-level set; (e), its constraints.

STYLE: the code-health strip, five panels on 9.4 in set at the full text
width (0.75 scale); a key above every frame names each line, letter tags
level on the keys' last rows; ink for the measurements, grey for the
references and the vacuum controls, gold only for (e)'s horizon.
"""

from __future__ import annotations

import argparse
import functools
import math
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.ticker import NullLocator  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import (  # noqa: E402
    plot_psi4_ligo, psi4_math, streams, style,
)
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import (  # noqa: E402
    PACK_ROOT, figure_dir, pair_mass,
)

TAG = "[convergence]"

# (a) the static throat from exact data, by level (finest dx = 0.5 / 2^level)
HOLD = "01_single_throat/hold"
LEVELS = {2: "single_hold_ml2_t100", 3: "single_hold_t100", 4: "single_hold_ml4_t100"}
R_STAR = math.sqrt(5.0) * math.exp(0.5 * math.atan(2.0))   # 3.88955: the exact throat
DATA_ERA = (0.0, 10.0)      # the static error of reading the exact data dominates
EVOL_ERA = (12.0, 20.0)     # the evolution's own error dominates
EVOL_SKIP = (16.0,)         # level 2's one-dump dip (the docstring)
RULES = ((4.0, 2, (0, (1, 1.6))), (8.0, 3, (0, (4, 2))), (16.0, 4, (0, (7, 2, 1.5, 2))))

# (b) the Bowen-York d = 12, p = 0.12 spiral, L = 128, |r Psi4^22| at R = 20
SPIRAL = {
    "level 5": "05_binary_spiral/csm/v2_spiral_d12_p012_L128_lvl5from0_t100_csm",
    "level 4": "08_convergence/v2_spiral_d12_p012_L128_lvl4from0_t100_csm",
    "wave zone": "08_convergence/v2_spiral_d12_p012_L128_lvl4w_t040_csm",
}
SPHERE = 20.0
T_LEVEL = 56.0              # inside both runs' trust windows (56.5, 57.2)
T_WAVE = 40.0               # the refined arm's stop time
PAIRS = {"level": ("level 4", "level 5", T_LEVEL),
         "wave-zone": ("wave zone", "level 4", T_WAVE)}

# (c) case: (key, stream under campaign/, m, M, spheres, u_max or None = the
# last u the outermost sphere covers, vacuum)
NEAR_ZONE = {
    "headon": ("head-on", "04_binary_headon/csm/merge_headon_flip_d8_v1_L128_SERIES/"
               "Weyl4_mode_20_axis.dat", 0, 2.35731,
               (10.0, 14.0, 18.0, 20.0, 28.0, 36.0, 44.0), 56.0, False),
    "d6": ("$d=6$ merger", "05_binary_spiral/merger_d6/spiral_d6_p010_L128_SERIES/"
           "Weyl4_mode_22.dat", 2, 2.3709, (20.0, 28.0, 36.0, 44.0), None, False),
    "flyby": ("fly-by", "06_binary_flyby/merge_orbit_flip_d12_p045_L128_lvl4_t100_lbf_csm/"
              "Weyl4_mode_22.dat", 2, pair_mass("merge_orbit_flip_d12_p045_L128_lvl4_t100_lbf_csm"),
              (20.0, 28.0), 67.6, False),
    "vac-headon": ("vacuum head-on", "07_bbh_control/bbh_headon_d8_L128_lvl5_t100/"
                   "weyl_extraction_mode_20_axis.dat", 0, 2.0,
                   (14.0, 20.0, 26.0, 30.0), 70.0, True),
    "vac-d6": ("vacuum $d=6$", "07_bbh_control/bbh_control_d6_p010_t100/psi4_mode_l2_all.dat",
               2, 2.0, (14.0, 30.0), 70.0, True),
}
MARKERS = {"headon": "o", "d6": "s", "flyby": "^", "vac-headon": "o", "vac-d6": "s"}

# (d) CONV-fz, coarse to fine: (finest dx, run under campaign/); a level is drawn once packed
CONV_FZ = (
    ("1/16", "08_convergence/farzone_headon_flip_d8_L512_lvl5_t100_csm"),
    ("1/32", "08_convergence/farzone_headon_flip_d8_L512_lvl6_t250_csm"),
    ("1/64", "08_convergence/farzone_headon_flip_d8_L512_lvl7_t100_csm"),
)
FZ_SPHERE = 10.0
FZ_T = 100.0                # the twins' stop time
FZ_PAIRS = ((style.MUTED, "-"), (style.CONTEXT, (0, (3, 1.5))))   # by neighbouring pair

# (e) <H_ADM> at t = 100 on shells outside the common MOTS, read on level 4 (dx = 1/8), the grid
# every CONV-fz level shares there (levels 6 and 7 sit within |x| < 2.5 and 1.25 of the merged
# centre): written on the node from each run's Chk02500 by c_checkpoint_hamiltonian.py
FZ_HAM = "analysis/convfz_constraints_t100.tsv"
FZ_HAM_STYLE = {"1/16": dict(color=style.INK, lw=0.7, marker="o", ms=2.6),
                "1/32": dict(color=style.MUTED, lw=0.9),
                "1/64": dict(color=style.CONTEXT, lw=0.9, ls=(0, (3, 1.5)))}


def _campaign(pack_root) -> pathlib.Path:
    return pathlib.Path(pack_root).expanduser() / "campaign"


# ------------------------------------------------------------------ (a)
@functools.lru_cache(maxsize=None)
def _static(pack_root: str):
    recs = {}
    for lev, run in LEVELS.items():
        a = streams.read_rows(_campaign(pack_root) / HOLD / run / "areal_radius.dat", 3)
        recs[lev] = dict(zip(np.round(a[:, 0], 4), a[:, 1]))
    t = np.array(sorted(set.intersection(*(set(r) for r in recs.values()))))
    return t, {lev: np.array([r[x] for x in t]) for lev, r in recs.items()}


def static_throat(pack_root):
    """(t, {level: R_areal_min(t)}) on the dumps all three levels have."""
    return _static(str(pack_root))


def convergence_factor(pack_root):
    """(t, Q) with Q = (R_2 - R_3)/(R_3 - R_4)."""
    t, R = static_throat(pack_root)
    return t, (R[2] - R[3]) / (R[3] - R[4])


def order_range(pack_root, era, skip=()):
    """(min, max) of n = log2 Q over the dumps in era, less those in skip."""
    t, Q = convergence_factor(pack_root)
    k = (t >= era[0] - 1e-6) & (t <= era[1] + 1e-6) & ~np.isin(t, np.round(skip, 4))
    n = np.log2(Q[k])
    return float(n.min()), float(n.max())


def draw_order(ax, pack_root) -> list:
    """Panel (a); returns its key entries."""
    t, R = static_throat(pack_root)
    _, Q = convergence_factor(pack_root)
    for i in range(0, t.size, 6):
        print(f"{TAG} (a) " + "  ".join(f"Q({x:g}) = {q:.3f} [n {np.log2(q):.3f}]"
                                         for x, q in zip(t[i:i + 6], Q[i:i + 6])))
    err = [abs(float(R[lev][0]) - R_STAR) for lev in (2, 3, 4)]
    print(f"{TAG} (a) R_star = {R_STAR:.6f}; t = 0 errors |R_l - R_star| = "
          f"{err[0]:.3e} / {err[1]:.3e} / {err[2]:.3e} (levels 2/3/4); log2 ratios "
          f"{np.log2(err[0] / err[1]):.3f}, {np.log2(err[1] / err[2]):.3f}")
    for name, era, skip in (("data", DATA_ERA, ()), ("evolution", EVOL_ERA, EVOL_SKIP),
                            ("evolution, every dump", EVOL_ERA, ())):
        lo, hi = order_range(pack_root, era, skip)
        print(f"{TAG} (a) {name} era t = {era[0]:g}-{era[1]:g}"
              f"{' less t = ' + ', '.join(f'{s:g}' for s in skip) if skip else ''}: "
              f"Q = {2 ** lo:.2f}-{2 ** hi:.2f}, n = log2 Q = {lo:.3f}-{hi:.3f}")

    q_line, = ax.plot(t, Q, color=style.INK, lw=0.6, marker="o", ms=2.6, zorder=3)
    entries = [(q_line, "$Q$, levels 2/3/4")]
    for q, n, dash in RULES:
        rule = ax.axhline(q, color=style.MUTED, lw=0.8, ls=dash, zorder=1)
        entries.append((rule, f"$n={n}$"))   # Q = 2^n: the ticks
    ax.set_yscale("log")
    ax.set_ylim(3.3, 20.0)
    ax.set_yticks([4, 8, 16], ["4", "8", "16"])
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_xlim(-0.8, t[-1] + 0.8)
    ax.set_xlabel("$t$")
    ax.set_ylabel("$(R_2-R_3)/(R_3-R_4)$")
    return entries


# ------------------------------------------------------------------ (b)
@functools.lru_cache(maxsize=None)
def _psi(pack_root: str, arm: str) -> dict:
    t, modes = streams.load_mode(_campaign(pack_root) / SPIRAL[arm] / "Weyl4_mode_22.dat")
    return dict(zip(np.round(t, 4), modes[SPHERE]))


def psi_pair(pack_root, a: str, b: str, t_max: float):
    """(t, y_a, y_b): r Psi4^22 at R = 20 of two arms on their common samples t <= t_max."""
    ra, rb = _psi(str(pack_root), a), _psi(str(pack_root), b)
    t = np.array(sorted(set(ra) & set(rb)))
    t = t[t <= t_max + 1e-9]
    return t, np.array([ra[x] for x in t]), np.array([rb[x] for x in t])


def burst_peak(pack_root):
    """(peak |r Psi4^22| of level 5 at R = 20 over t <= T_LEVEL, its time)."""
    t, y, _ = psi_pair(pack_root, "level 5", "level 5", T_LEVEL)
    i = int(np.argmax(np.abs(y)))
    return float(np.abs(y[i])), float(t[i])


def psi_difference(pack_root, pair: str):
    """(t, |difference|, 100 max|difference| / burst_peak, time of the max) of PAIRS[pair]."""
    a, b, t_max = PAIRS[pair]
    t, ya, yb = psi_pair(pack_root, a, b, t_max)
    d = np.abs(ya - yb)
    i = int(np.argmax(d))
    return t, d, 100.0 * float(d[i]) / burst_peak(pack_root)[0], float(t[i])


def draw_wave(ax, pack_root) -> list:
    """Panel (b); returns its key entries."""
    peak, t_peak = burst_peak(pack_root)
    t, y, _ = psi_pair(pack_root, "level 5", "level 5", T_LEVEL)
    print(f"{TAG} (b) level 5 burst peak |r Psi4^22|(R = 20) = {peak:.4e} at t = {t_peak:.2f}")
    entries = [(ax.plot(t, np.abs(y), color=style.INK, lw=0.9, zorder=3)[0], "level 5")]
    for pair, color, dash, label in (
            ("level", style.MUTED, "-", "level 4 $-$ level 5"),
            ("wave-zone", style.CONTEXT, (0, (3, 1.5)), "refined wave zone $-$ level 4")):
        td, d, pct, t_max = psi_difference(pack_root, pair)
        print(f"{TAG} (b) {pair}: max|diff| = {d.max():.3e} at t = {t_max:.2f}, "
              f"{pct:.4f} % of the burst peak (t <= {PAIRS[pair][2]:g})")
        line, = ax.plot(td, np.where(d > 0, d, np.nan), color=color, lw=0.7, ls=dash, zorder=2)
        entries.append((line, label))
    ax.set_yscale("log")
    ax.set_xlim(0.0, T_LEVEL)
    ax.set_xlabel("$t$")
    ax.set_ylabel(r"$|r\Psi_4^{22}|$ at $R=20$")
    return entries


# ------------------------------------------------------------------ (c)
def band_peak(w, dt: float) -> float:
    """The band integral's peak frequency: the maximum of the smoothed burst PSD."""
    f, S = psi4_math._burst_psd(w, 1.0 / dt)
    return float(f[1:][np.argmax(
        psi4_math._smooth_psd(S, plot_psi4_ligo._smooth_window(S.size), 5)[1:])])


def energy(t, y, R: float, M: float, m: int, u_max: float) -> float:
    """E_rad of one mode on the sphere R over t - R <= u_max, in units of M:
    the paper's band integral (plot_psi4_ligo)."""
    k = (t - R) <= u_max + 1e-9
    u, w = (t[k] - R) / M, y[k] * M
    return psi4_math._compute_radiated_energy(
        u, w, m=m, f_peak=band_peak(w, float((u[-1] - u[0]) / (u.size - 1))))


@functools.lru_cache(maxsize=None)
def _near_zone(pack_root: str) -> dict:
    out = {}
    for case, (_, rel, m, M, spheres, u_max, _vac) in NEAR_ZONE.items():
        path = _campaign(pack_root) / rel
        if path.name.endswith("_l2_all.dat"):
            t, modes = streams.load_l2_all(path)
            ser = {R: modes[(m, R)] for R in spheres}
        else:
            t, modes = streams.load_mode(path)
            ser = {R: modes[R] for R in spheres}
        if u_max is None:
            u_max = float(t[-1]) - spheres[-1]
        out[case] = (M, u_max, {R: energy(t, ser[R], R, M, m, u_max) for R in spheres})
    return out


def near_zone_energies(pack_root) -> dict:
    """{case: (M, u_max, {R: E(R)})} for every NEAR_ZONE record."""
    return _near_zone(str(pack_root))


def near_zone_ratio(pack_root, case: str) -> float:
    """E(innermost sphere) / E(outermost sphere)."""
    E = near_zone_energies(pack_root)[case][2]
    return E[min(E)] / E[max(E)]


def near_zone_spread(pack_root, case: str, r_min: float = 0.0) -> float:
    """100 (max - min) / E(outermost) over the spheres R >= r_min, %."""
    E = near_zone_energies(pack_root)[case][2]
    e = [v for R, v in E.items() if R >= r_min - 1e-9]
    return 100.0 * (max(e) - min(e)) / E[max(E)]


def draw_extraction(ax, pack_root) -> list:
    """Panel (c); returns its key entries, wormhole and vacuum twin side by side."""
    handles = {}
    for case, (M, u_max, E) in near_zone_energies(pack_root).items():
        label, vac = NEAR_ZONE[case][0], NEAR_ZONE[case][6]
        R = np.array(sorted(E))
        ratio = np.array([E[r] for r in R]) / E[R[-1]]
        print(f"{TAG} (c) {case} (M = {M:g}, t - R <= {u_max:.2f}): " + "  ".join(
            f"E({r:g}) = {E[r]:.4e} [R/M {r / M:.2f}, {q:.4f}]" for r, q in zip(R, ratio)))
        print(f"{TAG} (c) {case}: E(in)/E(out) = {near_zone_ratio(pack_root, case):.4f}, "
              f"spread {near_zone_spread(pack_root, case):.3f} % (all spheres), "
              f"{near_zone_spread(pack_root, case, 28.0):.3f} % (R >= 28)")
        color = style.MUTED if vac else style.INK
        handles[case], = ax.plot(R / M, ratio, color=color, lw=0.7, marker=MARKERS[case],
                                 ms=3.2, mfc=style.GROUND if vac else color, mec=color,
                                 mew=0.8, zorder=2 if vac else 3)
    ax.axhline(1.0, color=style.FAINT, lw=0.6, zorder=0)
    ax.set_xlabel("$R/M$")
    ax.set_ylabel(r"$E(R)/E(R_{\rm out})$")
    order = ("headon", "vac-headon", "d6", "vac-d6", "flyby")
    return [(handles[c], NEAR_ZONE[c][0]) for c in order]


# ------------------------------------------------------------------ (d)
def fz_levels(pack_root) -> list[str]:
    """The CONV-fz levels packed so far, coarse to fine."""
    return [dx for dx, run in CONV_FZ if (_campaign(pack_root) / run).is_dir()]


@functools.lru_cache(maxsize=None)
def _fz_psi(pack_root: str, dx: str) -> dict:
    t, modes = streams.load_mode(_campaign(pack_root) / dict(CONV_FZ)[dx] / "Weyl4_mode_20_axis.dat")
    return {x: y for x, y in zip(np.round(t, 4), modes[FZ_SPHERE]) if x <= FZ_T + 1e-9}


def fz_psi_difference(pack_root, a: str, b: str):
    """(t, |difference|, 100 max|difference| / the finer level's peak, time of the max):
    the collision-axis r Psi4^20 at R = 10 of levels a and b on their common samples."""
    ra, rb = _fz_psi(str(pack_root), a), _fz_psi(str(pack_root), b)
    t = np.array(sorted(set(ra) & set(rb)))
    d = np.abs(np.array([ra[x] for x in t]) - np.array([rb[x] for x in t]))
    i = int(np.argmax(d))
    return t, d, 100.0 * float(d[i]) / max(abs(v) for v in rb.values()), float(t[i])


@functools.lru_cache(maxsize=None)
def _fz_energy(pack_root: str, dx: str) -> float:
    _, _, m, M, _, u_max, _ = NEAR_ZONE["headon"]
    r = _fz_psi(pack_root, dx)
    t = np.array(sorted(r))
    return energy(t, np.array([r[x] for x in t]), FZ_SPHERE, M, m, u_max)


def fz_energy_difference(pack_root, a: str, b: str) -> float:
    """100 |E_a/E_b - 1|: E at R = 10 by (c)'s band integral on its head-on window."""
    return 100.0 * abs(_fz_energy(str(pack_root), a) / _fz_energy(str(pack_root), b) - 1.0)


def fz_energy_order(pack_root, a: str = "1/16", b: str = "1/32", c: str = "1/64") -> float:
    """log2 of the three-level factor (E_a - E_b) / (E_b - E_c) of E at R = 10."""
    ea, eb, ec = (_fz_energy(str(pack_root), x) for x in (a, b, c))
    return math.log2((ea - eb) / (eb - ec))


@functools.lru_cache(maxsize=None)
def _fz_mots(pack_root: str, dx: str) -> dict:
    """{t: (R, M_MS)} of the common MOTS on the dumps t <= FZ_T that find it."""
    a = streams.read_rows(_campaign(pack_root) / dict(CONV_FZ)[dx] / "mots_spectral.dat", 3)
    return {round(float(t), 3): (float(R), float(M)) for t, R, M in a
            if np.isfinite(R) and t <= FZ_T + 1e-9}


def fz_mots_birth(pack_root) -> float:
    """The common MOTS's first dump, the same at every packed level."""
    births = {dx: min(_fz_mots(str(pack_root), dx)) for dx in fz_levels(pack_root)}
    if len(set(births.values())) > 1:
        raise SystemExit(f"{TAG} (d) the levels' common MOTS first appear apart: {births}")
    return next(iter(births.values()))


def fz_mots_difference(pack_root, a: str, b: str):
    """(100 max(|R_a/R_b - 1|, |M_a/M_b - 1|) over the dumps both levels find the
    common MOTS on, the dump of the max)."""
    ma, mb = _fz_mots(str(pack_root), a), _fz_mots(str(pack_root), b)
    rel = {t: max(abs(ma[t][0] / mb[t][0] - 1.0), abs(ma[t][1] / mb[t][1] - 1.0))
           for t in set(ma) & set(mb)}
    t = max(rel, key=rel.get)
    return 100.0 * rel[t], t


def draw_farzone(ax, pack_root) -> list:
    """Panel (d); returns its key entries."""
    levels = fz_levels(pack_root)
    r = _fz_psi(str(pack_root), levels[-1])
    t = np.array(sorted(r))
    y = np.abs(np.array([r[x] for x in t]))
    print(f"{TAG} (d) levels packed: {', '.join(levels)}; dx = {levels[-1]} peak "
          f"|r Psi4^20|(R = 10) = {y.max():.4e} at t = {t[np.argmax(y)]:.2f}; common MOTS "
          f"from t = {fz_mots_birth(pack_root):g}")
    entries = [(ax.plot(t, y, color=style.INK, lw=0.9, zorder=3)[0], f"$\\Delta x={levels[-1]}$")]
    for (a, b), (color, dash) in zip(zip(levels, levels[1:]), FZ_PAIRS):
        td, d, pct, t_max = fz_psi_difference(pack_root, a, b)
        mots, t_mots = fz_mots_difference(pack_root, a, b)
        print(f"{TAG} (d) {a} - {b}: max|diff| = {d.max():.3e} at t = {t_max:.2f}, {pct:.4f} % "
              f"of the {b} peak; E(R = 10) {_fz_energy(str(pack_root), a):.5e} / "
              f"{_fz_energy(str(pack_root), b):.5e}, {fz_energy_difference(pack_root, a, b):.4f} %; "
              f"MOTS R, M_MS to {mots:.4f} % (t = {t_mots:g})")
        line, = ax.plot(td, np.where(d > 0, d, np.nan), color=color, lw=0.7, ls=dash, zorder=2)
        entries.append((line, f"${a}-{b}$"))
    if len(levels) == 3:
        print(f"{TAG} (d) E(R = 10) three-level order log2[(E_{levels[0]} - E_{levels[1]}) / "
              f"(E_{levels[1]} - E_{levels[2]})] = {fz_energy_order(pack_root, *levels):.4f}")
    ax.set_yscale("log")
    ax.set_xlim(0.0, FZ_T)
    ax.set_xlabel("$t$")
    ax.set_ylabel(r"$|r\Psi_4^{20}|$ at $R=10$")
    return entries


# ------------------------------------------------------------------ (e)
@functools.lru_cache(maxsize=None)
def _fz_ham(pack_root: str) -> dict:
    """{dx: (r, <H_ADM>)} for the CONV-fz levels the table holds, coarse to fine."""
    lines = [l for l in (pathlib.Path(pack_root).expanduser() / FZ_HAM).read_text(
        encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    head = lines[0].split("\t")
    shells: dict[str, list] = {}
    for line in lines[1:]:
        f = dict(zip(head, line.split("\t")))
        shells.setdefault(f["run"], []).append((float(f["r"]), float(f["H_ADM"])))
    return {dx: tuple(np.array(sorted(shells[pathlib.Path(run).name])).T)
            for dx, run in CONV_FZ if pathlib.Path(run).name in shells}


def fz_ham_difference(pack_root, a: str = "1/16", b: str = "1/32") -> float:
    """100 max |H_a/H_b - 1| over the shells both levels have."""
    (ra, Ha), (rb, Hb) = (_fz_ham(str(pack_root))[x] for x in (a, b))
    common = np.intersect1d(np.round(ra, 6), np.round(rb, 6))
    pick = lambda r, H: H[np.isin(np.round(r, 6), common)]   # noqa: E731
    return 100.0 * float(np.max(np.abs(pick(ra, Ha) / pick(rb, Hb) - 1.0)))


def fz_mots_extent(pack_root) -> float:
    """The common MOTS's largest coordinate extent from the centre at t = FZ_T (h_x, h_y, h_z),
    on the finest packed level."""
    run = dict(CONV_FZ)[fz_levels(pack_root)[-1]]
    a = streams.read_rows(_campaign(pack_root) / run / "mots_spectral.dat", 7)
    row = a[np.argmin(np.abs(a[:, 0] - FZ_T))]
    return float(np.max(row[4:7]))


def draw_constraint(ax, pack_root) -> list:
    """Panel (e); returns its key entries."""
    ham = _fz_ham(str(pack_root))
    entries = []
    for dx, (r, H) in ham.items():
        print(f"{TAG} (e) dx = {dx}: <H_ADM>(t = {FZ_T:g}) " + "  ".join(
            f"{x:g}: {h:.4e}" for x, h in zip(r, H)))
        line, = ax.plot(r, -1e4 * H, zorder=3, **FZ_HAM_STYLE[dx])
        entries.append((line, f"$\\Delta x={dx}$"))
    levels = list(ham)
    for a, b in zip(levels, levels[1:]):
        print(f"{TAG} (e) {a} vs {b}: max |H_a/H_b - 1| = {fz_ham_difference(pack_root, a, b):.3f} %")
    r_mots = fz_mots_extent(pack_root)
    print(f"{TAG} (e) the common MOTS reaches r = {r_mots:.3f} from the centre at t = {FZ_T:g}")
    ax.axvline(r_mots, color=style.GOLD, lw=0.9, zorder=2)
    ax.annotate("MOTS", (r_mots, 0.0), xycoords=("data", "axes fraction"), xytext=(2.5, 4.0),
                textcoords="offset points", ha="left", va="bottom", fontsize=7.5, color=style.GOLD)
    ax.set_xlim(r_mots - 0.3, max(float(r.max()) for r, _ in ham.values()) + 0.3)
    ax.set_xlabel("$r$")
    ax.set_ylabel(r"$-10^4\langle\mathcal{H}\rangle$ at $t=100$")
    return entries


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    style.prd(base=10.0)
    fig, axes = plt.subplots(1, 5, figsize=(9.4, 2.6), constrained_layout=True,
                             gridspec_kw={"width_ratios": (1.0, 1.05, 1.35, 0.95, 0.75)})
    axA, axB, axC, axD, axE = axes
    style.legend_top(axA, draw_order(axA, args.pack_root), ncol=2)
    style.legend_top(axB, draw_wave(axB, args.pack_root), ncol=1)
    style.legend_top(axC, draw_extraction(axC, args.pack_root), ncol=2)
    style.legend_top(axD, draw_farzone(axD, args.pack_root), ncol=1)
    style.legend_top(axE, draw_constraint(axE, args.pack_root), ncol=1)
    style.tag_keys(fig, axes, [f"({c})" for c in "abcde"], row="last")
    problems = style.label_audit(fig)
    print(f"{TAG} label audit: {len(problems)} problem(s) {problems[:3]}")

    out = (pathlib.Path(args.out) if args.out else
           figure_dir("00_code_health", args.pack_root) / "convergence.png")
    png = style.save(fig, out)
    print(f"{TAG} wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
