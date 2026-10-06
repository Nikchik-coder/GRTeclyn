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

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_convergence

The file lives under ``figures/00_code_health/``; every number is printed.
The ledger reads (a) through its own recomputation (``extract_single``'s
``single_conv_order``) and (b)/(c) through ``psi_difference``,
``near_zone_ratio`` and ``near_zone_spread`` here (``extract_waves``).

WHY: 2026-10-06, the referee: the paper had no Richardson convergence plot.

STYLE: the code-health strip on the full 7.05 in width; a key above every
frame names each line, letter tags level on the keys' last rows; ink for
the measurements, grey for the references and the vacuum controls, no gold
(nothing here is a fitted law or a horizon).
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
from matplotlib.lines import Line2D  # noqa: E402
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
        entries.append((rule, f"$n={n}$ ($Q={q:g}$)"))
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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    style.prd(base=10.0)
    fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(7.05, 2.6), constrained_layout=True)
    style.legend_top(axA, draw_order(axA, args.pack_root), ncol=2)
    style.legend_top(axB, draw_wave(axB, args.pack_root), ncol=1)
    style.legend_top(axC, draw_extraction(axC, args.pack_root), ncol=2)
    style.tag_keys(fig, (axA, axB, axC), [f"({c})" for c in "abc"], row="last")
    problems = style.label_audit(fig)
    print(f"{TAG} label audit: {len(problems)} problem(s) {problems[:3]}")

    out = (pathlib.Path(args.out) if args.out else
           figure_dir("00_code_health", args.pack_root) / "convergence.png")
    png = style.save(fig, out)
    print(f"{TAG} wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
