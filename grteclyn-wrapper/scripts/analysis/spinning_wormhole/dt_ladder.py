"""Where and how fast the dt-dependent mode grows.

Reads the dt-ladder arms (runs/spinning_wormhole/drainhole/06_dt_ladder/) and
prints, per arm against the dt = 0.02 control:

1. max|K|(t) from collapse_diagnostics.dat with sliding-window e-fold times
   over the growth phase (in the merger runs: e-fold ~0.8 at dt_mult 0.1,
   ~1.5 at 0.05, clean at 0.02; growth from t = 0, visible when it crosses
   the smooth background).
2. Per-level masked constraint norms (constraint_norms_levels.dat): the ratio
   arm/control per level at matched times: WHICH level carries the growth.
3. The radial profile (core_radial_profile.dat): the first shell whose
   absK_max exceeds `--shell-factor` x its own t <= 5 baseline: WHERE the
   mode lives (throat ~1, coarse-fine interfaces 4/8/16, sponge 24-32,
   boundary >= 32).
4. Wave-zone psi4 P_total per plotfile (small_data/psi4_directional.dat):
   the earliest discriminator (x100+ by t ~ 10 at dt_mult 0.05 in the merger
   runs).

    python dt_ladder.py [--arms dt005_t070 dt0035_t070] [--control dt002ctl_t100]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parents[4] / "runs/spinning_wormhole/drainhole/06_dt_ladder"
PREFIX = "static_hold_L64_ml3_"


def load(run: str, rel: str) -> np.ndarray | None:
    p = BASE / (PREFIX + run) / rel
    if not p.is_file():
        return None
    try:
        d = np.loadtxt(p, ndmin=2)
    except ValueError:
        return None
    return d if d.size else None


def at(d: np.ndarray, t: float, col: int) -> float:
    i = int(np.argmin(np.abs(d[:, 0] - t)))
    return float(d[i, col]) if abs(d[i, 0] - t) < 0.5 else float("nan")


def efold_windows(d: np.ndarray, col: int, t_lo: float, t_hi: float,
                  width: float = 4.0) -> list[tuple[float, float]]:
    """(t_centre, e-fold time) of log-linear fits in sliding windows."""
    out = []
    for tc in np.arange(t_lo + width / 2, t_hi - width / 2 + 1e-9, width / 2):
        m = (d[:, 0] >= tc - width / 2) & (d[:, 0] <= tc + width / 2)
        y = d[m, col]
        if m.sum() < 8 or np.any(y <= 0):
            continue
        slope = np.polyfit(d[m, 0], np.log(y), 1)[0]
        if slope > 1e-6:
            out.append((float(tc), 1.0 / slope))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--arms", nargs="+",
                    default=["dt005_t070", "dt0035_t070"])
    ap.add_argument("--control", default="dt002ctl_t100")
    ap.add_argument("--shell-factor", type=float, default=10.0)
    args = ap.parse_args()

    ctl_c = load(args.control, "data/collapse_diagnostics.dat")
    ctl_l = load(args.control, "data/constraint_norms_levels.dat")
    ctl_p = load(args.control, "small_data/psi4_directional.dat")

    for arm in args.arms:
        c = load(arm, "data/collapse_diagnostics.dat")
        if c is None:
            print(f"== {arm}: no data yet")
            continue
        t_end = c[-1, 0]
        print(f"\n== {arm}  (t to {t_end:.2f})")

        # 1. max|K| against the control, and its e-folds.
        print("  t     max|K|      ctl         ratio")
        for t in np.arange(5, t_end + 1e-9, 5):
            k = at(c, t, 3)
            kc = at(ctl_c, t, 3) if ctl_c is not None else float("nan")
            print(f"  {t:5.1f} {k:10.4g} {kc:10.4g} {k / kc if kc == kc and kc > 0 else float('nan'):10.3g}")
        ef = efold_windows(c, 3, 5.0, t_end)
        if ef:
            print("  e-folds of max|K|: " +
                  "  ".join(f"t~{tc:.0f}:{tau:.2f}" for tc, tau in ef[-6:]))

        # 2. Per-level norms: arm/control per level.
        lv = load(arm, "data/constraint_norms_levels.dat")
        if lv is not None and ctl_l is not None:
            nlev = (lv.shape[1] - 3) // 2  # minus time and the _all pair
            hdr = "  t    " + "".join(f"  Ham_l{q}/ctl" for q in range(nlev)) + "    Ham_all/ctl"
            print(hdr)
            for t in np.arange(5, t_end + 1e-9, 5):
                cells = []
                for q in range(nlev):
                    a_ = at(lv, t, 1 + 2 * q)
                    b_ = at(ctl_l, t, 1 + 2 * q)
                    cells.append(f"{a_ / b_ if b_ == b_ and b_ > 0 else float('nan'):10.3g}")
                a_ = at(lv, t, lv.shape[1] - 2)
                b_ = at(ctl_l, t, ctl_l.shape[1] - 2)
                cells.append(f"{a_ / b_ if b_ == b_ and b_ > 0 else float('nan'):12.3g}")
                print(f"  {t:4.1f} " + "".join(cells))

        # 3. WHERE: first shells whose absK_max leaves its own baseline.
        pr = load(arm, "data/core_radial_profile.dat")
        if pr is not None:
            with open(BASE / (PREFIX + arm) / "data/core_radial_profile.dat") as f:
                cols = f.readline().split()[1:]
            ik = [i for i, name in enumerate(cols) if name.startswith("absK_max_r")]
            radii = np.array([float(cols[i].split("_r")[1]) for i in ik])
            # Header names map 1:1 onto data columns ('time' is cols[0]).
            base_m = pr[:, 0] <= 5.0
            if base_m.sum() >= 3:
                baseline = np.nanmax(np.abs(pr[np.ix_(base_m, ik)]), axis=0)
                flagged = []
                for i, r in enumerate(radii):
                    col = np.abs(pr[:, ik[i]])
                    hot = pr[col > args.shell_factor * max(baseline[i], 1e-12), 0]
                    if hot.size:
                        flagged.append((float(hot[0]), float(r)))
                flagged.sort()
                if flagged:
                    print(f"  absK_max shells first over {args.shell_factor:g}x baseline "
                          "(t_first, r): " +
                          "  ".join(f"({t:.1f}, {r:g})" for t, r in flagged[:8]))
                else:
                    print("  no shell over baseline yet")

        # 4. Wave-zone psi4 power against the control.
        ps = load(arm, "small_data/psi4_directional.dat")
        if ps is not None and ctl_p is not None:
            print("  t    P_total      ctl        ratio")
            for t in np.arange(2, min(t_end, ps[-1, 0]) + 1e-9, 4):
                a_ = at(ps, t, 1)
                b_ = at(ctl_p, t, 1)
                print(f"  {t:4.1f} {a_:10.3e} {b_:10.3e} {a_ / b_ if b_ == b_ and b_ > 0 else float('nan'):10.3g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
