#!/usr/bin/env python3
"""Does more orbital momentum make a stronger curvature wall?  (2026-09-24)

The reviewer on Sec. X (Limitations): "why [is the wall unexplained]? we have
higher momentum and therefore stronger curvature that goes NaN".  This reads
the packed streams of every arm that died at (or ran through) a merger core --
the head-ons (p = 0) and the orbital family at d = 12 -- and tabulates, per arm:

  t_death     last 'ADVANCE at time' before the NaN in run_tail*.log ('-' if none)
  t_floor     first row with min(chi) on the clamp (<= 1.01 x min_chi)
  K@floor     max|K| (collapse_diagnostics, global) at t_floor
  K-2/K-1/K-.5/K-.1   max|K| that long before the death
  K_last      the last row's max|K| (the thinned streams keep the final unit whole)
  lnK rate    d ln max|K| / dt over the last two units before the death
  a_min       min lapse at the death (or the end)
  d_min       smallest pit separation on record (binary_throat_diagnostics)
  t(d<1)      first time the pit separation falls below 1 (contact); dt_wall the
              death minus that time (the wall's clock from contact)

numpy only, reads results/merger/campaign via the wrapper's run_tree resolver.

    grteclyn-wrapper/.venv/bin/python grteclyn-wrapper/scripts/analysis/merger_feedback/wall_vs_momentum.py
"""

from __future__ import annotations

import pathlib
import re
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "grteclyn-wrapper" / "src"))
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import find_packed  # noqa: E402

# (run, p, d, note)
ARMS = [
    ("merge_headon_flip_d8_v1_t100", 0.00, 8, "head-on scout"),
    ("merge_headon_flip_d8_v1_lvl5from0_scalar_t100", 0.00, 8, "head-on, level 5 from 0"),
    ("merge_headon_flip_d12", 0.00, 12, "head-on at d = 12"),
    ("merge_orbit_flip_d12_r03000", 0.12, 12, "production L=64 chain"),
    ("merge_twin_p012_plain_t100", 0.12, 12, "damped twin from 0"),
    ("v2_spiral_d12_p012_L128_lvl5from0_t100", 0.12, 12, "L=128 level 5 from 0"),
    ("v2_spiral_d12_p012_L128_lvl5_t150_prof_r03600", 0.12, 12, "L=128 level 5 from 36"),
    ("merge_orbit_flip_d12_p015_nofill_t060", 0.15, 12, ""),
    ("merge_orbit_flip_d12_p015_lvl5_t060_r05000", 0.15, 12, "level 5 from 50"),
    ("merge_orbit_flip_d12_p020_nofill_t060", 0.20, 12, ""),
    ("merge_orbit_flip_d12_p020_lvl5_t200", 0.20, 12, "level 5 from 0"),
    ("merge_orbit_flip_d12_p025_t200", 0.25, 12, ""),
    ("merge_orbit_flip_d12_p025_lvl5_t200", 0.25, 12, "level 5 from 0"),
    ("merge_orbit_flip_d12_p035_t200", 0.35, 12, "passes, recedes"),
]

_ADV = re.compile(r"ADVANCE at time\s*=?\s*([0-9.eE+-]+)")
_NAN = re.compile(r"NaN (diagnostic|in )")


def params(d: pathlib.Path) -> dict[str, str]:
    out = {}
    for ln in (d / "evolution_params.txt").read_text().splitlines():
        ln = ln.split("#", 1)[0].strip()
        if "=" in ln:
            k, v = ln.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def death(d: pathlib.Path) -> tuple[float | None, float]:
    last, dead = None, None
    for tail in sorted(d.glob("run_tail*.log")):
        for ln in tail.read_text(errors="replace").splitlines():
            m = _ADV.search(ln)
            if m:
                last = float(m.group(1))
            elif _NAN.search(ln) and dead is None:
                dead = last
    return dead, (last if last is not None else float("nan"))


def load(path: pathlib.Path) -> np.ndarray:
    rows = [l.split() for l in path.read_text().splitlines()
            if l.strip() and not l.lstrip().startswith("#")]
    a = np.array([[float(x) for x in r[:11]] for r in rows if len(r) >= 4])
    a = a[np.argsort(a[:, 0], kind="stable")]
    _, keep = np.unique(a[:, 0], return_index=True)
    return a[keep]


def main() -> int:
    hdr = (f"{'run':46s} {'p':>4s} {'d':>3s} {'lev':>3s} {'L':>4s} {'t_death':>8s} "
           f"{'t_floor':>7s} {'K@floor':>8s} {'K-2':>7s} {'K-1':>7s} {'K-.5':>7s} "
           f"{'K-.1':>7s} {'K_last':>8s} {'lnK/dt':>7s} {'a_min':>8s} {'d_min':>6s} "
           f"{'t(d<1)':>6s} {'dt_wall':>7s}")
    print(hdr)
    for run, p, dsep, note in ARMS:
        d = find_packed(run)
        par = params(d)
        lev = int(par.get("max_level", "0").split()[0])
        L = float(par.get("L", "nan").split()[0])
        floor = float(par.get("min_chi", "1e-8").split()[0])
        cd = load(d / "collapse_diagnostics.dat")
        t, amin, cmin, K = cd[:, 0], cd[:, 1], cd[:, 2], cd[:, 3]
        td, tlast = death(d)
        tend = td if td is not None else tlast
        m = t <= tend + 1e-9
        t, amin, cmin, K = t[m], amin[m], cmin[m], K[m]
        on = np.where(cmin <= floor * 1.01)[0]
        tf = float(t[on[0]]) if on.size else float("nan")
        Kf = float(K[on[0]]) if on.size else float("nan")

        def at(dt):
            if td is None:
                return float("nan")
            k = np.searchsorted(t, td - dt)
            return float(K[min(k, len(K) - 1)])

        if td is not None:
            w = (t >= td - 2.0) & (K > 0)
            rate = float(np.polyfit(t[w], np.log(K[w]), 1)[0]) if w.sum() > 3 else float("nan")
        else:
            rate = float("nan")
        try:
            bt = load(d / "binary_throat_diagnostics.dat")
            bt = bt[bt[:, 0] <= tend + 1e-9]
            good = bt[:, 1] < 1e20
            dmin = float(bt[good, 1].min())
            below = np.where(good & (bt[:, 1] < 1.0) & (bt[:, 0] > 1.0))[0]
            tc = float(bt[below[0], 0]) if below.size else float("nan")
        except Exception:
            dmin, tc = float("nan"), float("nan")
        tds = f"{td:8.2f}" if td is not None else f"  ({tlast:.1f})"
        print(f"{run:46s} {p:4.2f} {dsep:3d} {lev:3d} {L:4.0f} {tds:>8s} {tf:7.2f} {Kf:8.3f} "
              f"{at(2):7.3f} {at(1):7.3f} {at(.5):7.3f} {at(.1):7.3f} {K[-1]:8.3g} "
              f"{rate:7.2f} {amin[-1]:8.2e} {dmin:6.3f} {tc:6.2f} "
              f"{(td - tc) if td is not None else float('nan'):7.2f}  {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
