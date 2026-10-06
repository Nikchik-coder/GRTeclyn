#!/usr/bin/env python3
"""The quadrupole-seed ladder (article Fig. 12, plot_seed_linearity) against the
RIGHT floor, and what a decade ladder (eps2 = 1e-3 ... 1e-1) would buy.

Reads only the tracked pack; prints a report; writes nothing.

    grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/analysis/merger_feedback/waves_seed_ladder.py

WHY A NEW FLOOR.  Fig. 12(b)'s dashed "spherical control" is
`single_eps_p1e2_t100`, a LEVEL-3 run, while every eps2 arm on the figure is
level 4 from t = 0 (the 0.01 arm: level 3 to t = 25, then level 4).  A level-4
+0.01 control with no quadrupole exists by accident:
`single_eps_p1e2_q1e2_ml4_scalar_t100` ran on the old pin, which does not read
`wormhole_seed_l2_amplitude_A` (runs_index.tsv: "NOT APPLIED ... t=0 data
identical to single_eps_p1e2_ml4_t060").  Likewise
`single_pureq_q1e2_ml4_scalar_t100` is an exact UNKICKED level-4 throat.

DETERMINISM.  Two runs with identical input give bit-identical r Psi4 (checked
below on the pairs that exist: boost vs boost and boost vs coreprof over
t = 0-13), so the l = 2 "floor" is a deterministic function of the input, and
an arm minus its matched control isolates what the seed did (D = y - y_ctrl).

Sections
  0  determinism checks
  1  rms Re r Psi4^20 over t = 30-50 (plot_seed_linearity.WINDOW): raw, the two
     floors, and control-subtracted
  2  linearity across the decade the level-4 arms span (0.005 -> 0.05), raw and
     control-subtracted, rms and waveform level
  3  the kick's share: pure quadrupole (no kick) against the kicked arms
  4  projections: eps2 = 1e-3 against both floors; eps2 = 1e-1 from the
     measured departure from linearity and the seed's t = 0 constraint cost
"""

from __future__ import annotations

import pathlib

import numpy as np

from grteclyn_wrapper.visualisation.wormhole_merger import plot_seed_linearity as P
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import PACK_ROOT

SEED = PACK_ROOT / "campaign" / "01_single_throat" / "seed"
RADII = (10.0, 14.0, 18.0)
W0, W1 = P.WINDOW

ARMS = {                      # eps2 -> run (all +0.01 kick, level 4 from t = 0 unless noted)
    0.005: "single_eps_p1e2_q5e3_ml4_t100",           # coreprof binary
    0.010: "single_eps_p1e2_q1e2_ml4_t100_r02500",    # seedl2; level 3 to t = 25, then level 4
    0.050: "single_eps_p1e2_q5e2_ml4_t100",           # seedl2
}
PURE = "single_pureq_q1e2_ml4_t100"                   # eps2 = 0.01, NO kick, coreprof
CTRL3 = "single_eps_p1e2_t100"                        # +0.01, level 3 (Fig. 12's floor)
CTRL4 = "single_eps_p1e2_q1e2_ml4_scalar_t100"        # +0.01, level 4, seed NOT applied (boost)
HOLD4 = "single_pureq_q1e2_ml4_scalar_t100"           # unkicked, level 4, seed NOT applied (boost)

# t = 0 Hamiltonian L2 norms (runs_index.tsv, column H0) -- the seed's constraint cost
H0 = {("kick", 0.0): 2.3458350524e-03, ("kick", 0.005): 2.3550419435e-03,
      ("kick", 0.01): 2.3821401328e-03, ("kick", 0.05): 3.0963168923e-03,
      ("radial", 0.0): 2.0955094722e-03, ("radial", 0.1): 7.5746235245e-03,
      ("radial", -0.1): 1.2224198550e-02, ("radial", 0.01): 2.3458350524e-03,
      ("radial", -0.01): 2.2125896694e-03}


def load(run: str):
    p = SEED / run / "psi4_mode_l2m0.dat"
    names = open(p).readline().lstrip("#").split()
    a = np.loadtxt(p)
    cols = {float(n[5:-1]): a[:, i] for i, n in enumerate(names) if n.startswith("Re(R=")}
    return a[:, 0], cols


def on(t_ref, t, y):
    """y sampled on t_ref (the consumer streams share the 1-unit grid)."""
    return np.interp(t_ref, t, y, left=np.nan, right=np.nan)


def rms(t, y, lo=W0, hi=W1):
    m = (t >= lo - 1e-6) & (t <= hi + 1e-6) & np.isfinite(y)
    return float(np.sqrt(np.mean(y[m] ** 2)))


def main():
    arms = {e: load(r) for e, r in ARMS.items()}
    tp, pure = load(PURE)
    t3, c3 = load(CTRL3)
    t4, c4 = load(CTRL4)
    th, h4 = load(HOLD4)

    print("=== 0. determinism: identical input -> identical r Psi4")
    ta, a = load("single_eps_p1e2_ml4_t060")        # boost, +0.01, level 4, to t = 13
    n = min(ta.size, t4.size)
    print(f"   single_eps_p1e2_ml4_t060 vs {CTRL4} (both boost, +0.01, level 4), R = 14, t = 0-{ta[n-1]:.0f}: "
          f"max |diff| = {np.abs(a[14.0][:n] - c4[14.0][:n]).max():.1e}")
    tb, b = load("single_eps_m1e2_ml4_t060")        # boost, -0.01
    tc, c = load("single_eps_m1e2_ml4_t100")        # coreprof, -0.01
    n = min(tb.size, tc.size)
    print(f"   single_eps_m1e2_ml4_t060 (boost) vs single_eps_m1e2_ml4_t100 (coreprof), R = 14, "
          f"t = 0-{tb[n-1]:.0f}: max |diff| = {np.abs(b[14.0][:n] - c[14.0][:n]).max():.1e}")

    print(f"\n=== 1. rms Re r Psi4^20 over t = {W0:g}-{W1:g}")
    print("   floor L3 (Fig. 12's dashed rule, level 3):   R14 %.2e" % rms(t3, c3[14.0]))
    print("   floor L4 (+0.01, level 4, exact control):   " +
          "  ".join(f"R{R:g} {rms(t4, c4[R]):.2e}" for R in RADII))
    print("   unkicked L4 throat (pure arm's control):     " +
          "  ".join(f"R{R:g} {rms(th, h4[R]):.2e}" for R in RADII))
    D = {}
    for e, (t, cols) in arms.items():
        raw = {R: rms(t, cols[R]) for R in RADII}
        d = {R: cols[R] - on(t, t4, c4[R]) for R in RADII}
        D[e] = (t, d)
        sub = {R: rms(t, d[R]) for R in RADII}
        print(f"   eps2 = {e:5.3f}: raw " + "  ".join(f"R{R:g} {raw[R]:.3e}" for R in RADII)
              + "   minus L4 control " + "  ".join(f"R{R:g} {sub[R]:.3e}" for R in RADII)
              + "   raw / L4 floor " + "  ".join(f"{raw[R] / rms(t4, c4[R]):.1f}" for R in RADII)
              + ("   [0.01 arm: level-3 history to t = 25, so its L4 subtraction is NOT exact]"
                 if e == 0.010 else ""))
    dp = {R: pure[R] - on(tp, th, h4[R]) for R in RADII}
    print("   pure 0.01 (no kick): raw " + "  ".join(f"R{R:g} {rms(tp, pure[R]):.3e}" for R in RADII)
          + "   minus unkicked L4 " + "  ".join(f"R{R:g} {rms(tp, dp[R]):.3e}" for R in RADII))

    print("\n=== 2. linearity across 0.005 -> 0.05 (both level 4 from t = 0), expected ratio 10")
    t5, d5 = D[0.005]
    t50, d50 = D[0.050]
    for R in RADII:
        r_raw = rms(t50, arms[0.050][1][R]) / rms(t5, arms[0.005][1][R])
        r_sub = rms(t50, d50[R]) / rms(t5, d5[R])
        m = (t5 >= 20) & (t5 <= W1)
        wave = np.abs(d50[R][m] / 10.0 - d5[R][m]).max() / np.abs(d5[R][m]).max()
        print(f"   R = {R:g}: rms ratio raw {r_raw:.2f}, control-subtracted {r_sub:.2f};  "
              f"waveform residual max|D(0.05)/10 - D(0.005)| / max|D(0.005)| over t = 20-{W1:g}: {wave:.3f}")
    # the figure's own statistic, for reference (relative to the 0.01 arm)
    e0 = 0.010
    for e in (0.005, 0.050):
        dev = [100 * abs(rms(arms[e][0], arms[e][1][R]) /
                         (rms(arms[e0][0], arms[e0][1][R]) * e / e0) - 1) for R in RADII]
        dev_s = [100 * abs(rms(D[e][0], D[e][1][R]) / (rms(D[e0][0], D[e0][1][R]) * e / e0) - 1)
                 for R in RADII]
        print(f"   departure from the line through 0.01 (Fig. 12 statistic), eps2 = {e}: raw "
              + "/".join(f"{x:.1f}" for x in dev) + " %;  control-subtracted "
              + "/".join(f"{x:.1f}" for x in dev_s) + " %")

    print("\n=== 3. the kick's share: pure quadrupole (no kick) vs kicked arms")
    for R in RADII:
        k01 = rms(arms[0.010][0], arms[0.010][1][R])
        print(f"   R = {R:g}: rms pure/kicked-0.01 raw {rms(tp, pure[R]) / k01:.3f};  "
              f"pure(minus unkicked L4) / [2 x (0.005 minus L4)] = "
              f"{rms(tp, dp[R]) / (2 * rms(t5, d5[R])):.3f}")

    print("\n=== 4. projections")
    for R in RADII:
        s1 = rms(t5, d5[R]) / 5.0
        print(f"   eps2 = 1e-3 at R = {R:g}: projected rms {s1:.2e} (linear, from the control-subtracted "
              f"0.005 arm);  L4 floor {rms(t4, c4[R]):.2e} -> S/F = {s1 / rms(t4, c4[R]):.2f}"
              + (f";  L3 floor (Fig. 12) {rms(t3, c3[14.0]):.2e} -> S/F = {s1 / rms(t3, c3[14.0]):.2f}"
                 if R == 14.0 else ""))
    # seed constraint cost: dH added in quadrature to the kick's own violation
    base = H0[("kick", 0.0)]
    for e in (0.005, 0.01, 0.05):
        dh = np.sqrt(H0[("kick", e)] ** 2 - base ** 2)
        print(f"   t = 0 L2 Ham: eps2 = {e}: {H0[('kick', e)]:.3e}  (seed part in quadrature {dh:.3e}, "
              f"/eps2 = {dh / e:.4f})")
    k = np.mean([np.sqrt(H0[("kick", e)] ** 2 - base ** 2) / e for e in (0.005, 0.01, 0.05)])
    for e in (0.001, 0.1):
        print(f"   projected eps2 = {e}: L2 Ham(t=0) = {np.hypot(base, k * e):.2e} "
              f"({np.hypot(base, k * e) / base:.2f} x the kick-only arm)")
    print(f"   radial arms for comparison: eps = +0.1 {H0[('radial', 0.1)]:.2e} "
          f"({H0[('radial', 0.1)] / H0[('radial', 0.0)]:.1f} x unkicked), eps = -0.1 "
          f"{H0[('radial', -0.1)]:.2e} ({H0[('radial', -0.1)] / H0[('radial', 0.0)]:.1f} x) -- both died at t = 14-15")
    print("   areal deformation of the seed at the throat: dR/R = 2 eps (radial), 2 eps2 P2 (quadrupole):"
          " eps2 = 0.1 moves the poles by +20 % and the equator by -10 %; eps = +-0.1 moves the whole throat by +-20 %")

    print("\n=== 5. waveform shape, seed-normalised and floor-subtracted, over t = 20-50")
    tq = np.arange(20.0, W1 + 1e-9, 0.05)

    def match(ta_, a_, tb_, b_, lo, hi):
        q = np.arange(lo, hi + 1e-9, 0.05)
        qa = np.interp(q, ta_, a_)
        best = None
        for s in np.arange(-6.0, 6.0001, 0.05):
            qb = np.interp(q + s, tb_, b_)
            ov = np.dot(qa, qb) / np.sqrt(np.dot(qa, qa) * np.dot(qb, qb))
            if best is None or ov > best[1]:
                best = (s, ov, np.sqrt(np.dot(qb, qb) / np.dot(qa, qa)))
        qb0 = np.interp(q, tb_, b_)
        ov0 = np.dot(qa, qb0) / np.sqrt(np.dot(qa, qa) * np.dot(qb0, qb0))
        return ov0, best

    for R in RADII:
        a5 = d5[R] / 0.005
        a50 = d50[R] / 0.050
        ap = dp[R] / 0.010
        for lab, (tb_, b_) in (("0.05 vs 0.005", (t50, a50)), ("pure 0.01 (no kick) vs kicked 0.005", (tp, ap))):
            for lo, hi in ((20.0, W1), (20.0, 36.0), (36.0, W1)):
                ov0, (s, ov, amp) = match(t5, a5, tb_, b_, lo, hi)
                print(f"   R = {R:g} {lab:<36s} t = {lo:.0f}-{hi:.0f}: overlap {ov0:.3f} unshifted; "
                      f"best with the second arm {'LEADING' if s < 0 else 'lagging'} by {abs(s):.2f}: "
                      f"{ov:.3f}, amplitude ratio {amp:.3f}")
    # does the subtraction remove the floor?  late times, where floor/eps2 is largest for 0.005
    for R in RADII:
        m = (t5 >= 40) & (t5 <= W1)
        raw5 = arms[0.005][1][R][m] / 0.005
        raw50 = np.interp(t5[m], t50, arms[0.050][1][R]) / 0.050
        sub5 = d5[R][m] / 0.005
        sub50 = np.interp(t5[m], t50, d50[R]) / 0.050
        print(f"   R = {R:g}, t = 40-{W1:g}: rms[0.005/eps2 - 0.05/eps2] raw {np.sqrt(np.mean((raw5 - raw50) ** 2)):.4f}"
              f" -> floor-subtracted {np.sqrt(np.mean((sub5 - sub50) ** 2)):.4f}  (signal rms/eps2 "
              f"{np.sqrt(np.mean(sub50 ** 2)):.4f})")


if __name__ == "__main__":
    main()
