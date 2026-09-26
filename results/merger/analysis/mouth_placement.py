#!/usr/bin/env python3
"""The mouths' growth with the companion's field taken off the ruler (2026-09-26,
referee fixes).

``plot_mouth_growth`` (the paper's mouth-growth figure) fits the per-mouth areal
radius growth excess R/R0 - 1 of the merging arm (p = 0.12, level 3,
``v2_spiral_d12_p012_L128_lvl3_t050_mouths``) and of the fly-by (p = 0.45, level
5, ``merge_orbit_flip_d12_p045_L128_lvl5_t100``) with one e-fold over t = 8-25.
But a coordinate sphere about one mouth also reads the companion's field: freshly
PLACED pairs read wider than the isolated throat, the more so the closer they are
(the placement curve of Sec. V C, ``placement_curve.py`` -> campaign/
04_binary_headon/placement_curve.dat: +1.8 % at d = 48 to +20.5 % at d = 6,
falling as d^-1.16).  As an arm's separation closes, that excess grows on its
ruler.  This script reads each arm's R(t) against the curve at the separation the
arm has reached and refits the same window with the same method:

    div   R / R_p(d) - 1           the companion scales the ruler
    sub   (R - R_p(d)) / R_iso     the companion adds its excess

(R_iso = 3.8895, the isolated throat; both vanish at t = 0).  The fit is
plot_mouth_growth._tau's, replicated: a straight line through ln of the POSITIVE
excess at the scan rows with 8 <= t <= 25 -- which on these scans are t = 9-24,
the end rows being stored as 7.99999999999987 and 25.0000000000011.

THE SEPARATION.  The curve's abscissa is the DECLARED centre separation of each
placed pair (|centerB - centerA| of its params, read by placement_curve.py); an
arm's d(t) is its scan-centre separation -- the tracked chi pits, row for row the
separation of binary_throat_diagnostics.dat and of throat_track.dat before the
tracker fuses the centres.  At t = 0 the two differ only by the tracker's grid snap
(level 3: 11.9375 for a declared 12; level 5: 12.0), so each arm's d(t) is shifted
by its own declared - measured offset at t = 0, after which R_p(d(0)) = R0 to 1e-5
(both arms read 4.23855 at t = 0, as place_d12_step1 does); R_p is then scaled by
that residual 1 +- 1e-5 so the corrected excess is exactly 0 at t = 0.

THE CURVE BETWEEN AND BEYOND THE PROBES.  Interpolated as a power law between
neighbouring probes (linear in ln d -> ln(R/R_iso - 1)): leave any interior probe
out and its neighbours predict it to <= 1e-3 in R, where linear interpolation in R
misses by up to 2.4e-2 -- the chord of a convex curve, up to 0.2 % high between the
probes at d = 8, 10 and 12, as large as the corrected signal early in the window.
``--interp linear`` is placement_curve.py's own convention, for comparison.  Outside
the probed range (6 <= d <= 48) the curve is held at its last point, as Fig. 4(e)
and placement_curve.py hold it, so below d = 6 the correction is a LOWER bound on
the companion's field and the corrected growth an upper bound on the throat's own.
The curve is a t = 0 calibration of pairs at rest applied to evolved coordinate
separations, as Sec. V C applies it to the released head-on pair.

    python results/merger/analysis/mouth_placement.py [results/merger] [--interp linear]

Prints only; the claims ledger's mergers_mouth(what = 'tau_placed', ...) calls the
functions below on plot_mouth_growth's own scan reader and fit.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from pack_paths import find_run  # noqa: E402
from placement_curve import ISOLATED  # noqa: E402

ARMS = (("merger", "v2_spiral_d12_p012_L128_lvl3_t050_mouths"),
        ("flyby", "merge_orbit_flip_d12_p045_L128_lvl5_t100"))
FIT = (8.0, 25.0)            # plot_mouth_growth.FIT
CURVE = ("04_binary_headon", "placement_curve.dat")


def load_curve(pack) -> tuple[np.ndarray, np.ndarray]:
    """(separation, mouth radius) of the placement probes, by separation."""
    a = np.loadtxt(pathlib.Path(pack) / "campaign" / CURVE[0] / CURVE[1],
                   usecols=(0, 1), comments="#")
    a = a[np.argsort(a[:, 0])]
    return a[:, 0], a[:, 1]


def placed(d, curve, interp: str = "loglog") -> np.ndarray:
    """R_p(d): a freshly placed pair's per-mouth reading at separation d, held at
    the probed ends; 'loglog' (a power law between neighbouring probes) or
    'linear' (in R, placement_curve.py's np.interp)."""
    ds, Rs = curve
    d = np.clip(np.asarray(d, float), ds[0], ds[-1])
    if interp == "linear":
        return np.interp(d, ds, Rs)
    if interp != "loglog":
        raise ValueError(f"interp {interp!r}: 'loglog' or 'linear'")
    lnE = np.interp(np.log(d), np.log(ds), np.log(Rs / ISOLATED - 1.0))
    return ISOLATED * (1.0 + np.exp(lnE))


def read_scan(path) -> dict[str, np.ndarray]:
    """plot_mouth_growth._scan's per-mouth columns, numpy only: t, R_A, R_B and
    the scan-centre separation in the orbital plane, A and B rows paired in
    file order."""
    rows = {"A": [], "B": []}
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        p = line.split()
        if p[1] in rows:
            rows[p[1]].append((float(p[0]), float(p[2]), float(p[3]), float(p[5])))
    n = min(len(rows["A"]), len(rows["B"]))
    A, B = np.array(rows["A"][:n]), np.array(rows["B"][:n])
    return dict(t=A[:, 0], RA=A[:, 3], RB=B[:, 3],
                sep=np.hypot(A[:, 1] - B[:, 1], A[:, 2] - B[:, 2]))


def declared_separation(params_path) -> float:
    """|centerB - centerA| of a run's params: the separation the curve is read in."""
    txt = pathlib.Path(params_path).read_text(encoding="utf-8")

    def vec(key: str) -> np.ndarray:
        m = re.search(rf"^\s*{key}\s*=\s*([^#\n]+)", txt, re.M)
        return np.array([float(x) for x in m.group(1).replace('"', "").split()])

    return float(np.linalg.norm(vec("wormhole_centerB") - vec("wormhole_centerA")))


def correct(t, R, d, curve, d_declared: float, model: str = "div",
            interp: str = "loglog") -> dict[str, np.ndarray]:
    """One mouth's reading R(t) at scan-centre separation d(t) against the curve.

    Returns t, the separation the curve is read at (d shifted by the t = 0 snap),
    R_p there (scaled so R_p(0) = R(0)), 'raw' = R/R0 - 1, 'ex' = the corrected
    excess of `model`, 'companion' = R_p/R_p(0) - 1 (the field's own growth on the
    ruler) and 'in_range' (inside the probed separations)."""
    t, R, d = (np.asarray(x, float) for x in (t, R, d))
    d_eff = d + (d_declared - d[0])
    Rp = placed(d_eff, curve, interp)
    scale = R[0] / Rp[0]
    Rp = Rp * scale
    if model == "div":
        ex = R / Rp - 1.0
    elif model == "sub":
        ex = (R - Rp) / (ISOLATED * scale)
    else:
        raise ValueError(f"model {model!r}: 'div' or 'sub'")
    ds = curve[0]
    return dict(t=t, d=d_eff, Rp=Rp, raw=R / R[0] - 1.0, ex=ex,
                companion=Rp / Rp[0] - 1.0,
                in_range=(d_eff >= ds[0] - 1e-9) & (d_eff <= ds[-1] + 1e-9))


def fit(t, ex, lo: float = FIT[0], hi: float = FIT[1]) -> tuple[float, float, float, int]:
    """plot_mouth_growth._tau's line through ln(ex) over lo <= t <= hi, positive
    rows only: (tau, seed = the t = 0 amplitude, rms of ln ex about it, rows)."""
    t, ex = np.asarray(t, float), np.asarray(ex, float)
    m = (t >= lo - 1e-6) & (t <= hi + 1e-6) & (ex > 0)
    if m.sum() < 2:
        raise ValueError(f"{int(m.sum())} positive rows in t = {lo:g}-{hi:g}: no e-fold to fit")
    p = np.polyfit(t[m], np.log(ex[m]), 1)
    rms = float(np.sqrt(np.mean((np.log(ex[m]) - np.polyval(p, t[m])) ** 2)))
    return float(1.0 / p[0]), float(np.exp(p[1])), rms, int(m.sum())


def split_index(s: dict, r_at_min=None) -> int:
    """Rows before the two scan spheres overlap (plot_mouth_growth._split) --
    needs the scan's r_at_R_min, so the caller passes it; None = all rows."""
    if r_at_min is None:
        return len(s["t"])
    bad = np.asarray(r_at_min) > s["sep"] / 2.0
    return int(np.argmax(bad)) if bad.any() else len(s["t"])


def _r_at_min(path) -> np.ndarray:
    out = []
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#") and line.split()[1] == "A":
            out.append(float(line.split()[6]))
    return np.array(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pack", nargs="?", default=str(HERE.parent), help="pack root (results/merger)")
    ap.add_argument("--interp", default="loglog", choices=("loglog", "linear"))
    a = ap.parse_args(argv)
    pack = pathlib.Path(a.pack)
    curve = load_curve(pack)
    print(f"[mouth-placement] placement curve: {len(curve[0])} probes, d = {curve[0][0]:g}-"
          f"{curve[0][-1]:g}; interpolation {a.interp}, held outside; fit rows "
          f"{FIT[0]:g} <= t <= {FIT[1]:g}")
    for arm, run in ARMS:
        d = find_run(pack, run)
        s = read_scan(d / "horizon_scan.dat")
        d0 = declared_separation(d / "evolution_params.txt")
        i = split_index(s, _r_at_min(d / "horizon_scan.dat")[: len(s["t"])])
        cd = correct(s["t"], s["RA"], s["sep"], curve, d0, "div", a.interp)
        cs = correct(s["t"], s["RA"], s["sep"], curve, d0, "sub", a.interp)
        t = s["t"]
        print(f"\n== {arm}: {run}  (declared d = {d0:g}, scan d(0) = {s['sep'][0]:.4f}, "
              f"shift {d0 - s['sep'][0]:+.4f})")
        print("     t      d     R_A      R_p     R/R0-1    field    div      sub   in range")
        for k in range(i + 1 if i < len(t) else len(t)):
            print(f"  {t[k]:5.1f} {cd['d'][k]:6.3f} {s['RA'][k]:.5f} {cd['Rp'][k]:.5f} "
                  f"{100 * cd['raw'][k]:+7.3f}% {100 * cd['companion'][k]:+7.3f}% "
                  f"{100 * cd['ex'][k]:+7.3f}% {100 * cs['ex'][k]:+7.3f}%  "
                  f"{'yes' if cd['in_range'][k] else 'held'}")
        w = (t >= FIT[0] - 1e-6) & (t <= FIT[1] + 1e-6)
        out = t[w & ~cd["in_range"]]
        print(f"  fit rows t = {t[w][0]:.0f}-{t[w][-1]:.0f}; d there {cd['d'][w][0]:.3f} -> "
              f"{cd['d'][w][-1]:.3f}; below the probed range: "
              + (", ".join(f"t = {x:.0f}" for x in out) if len(out) else "none"))
        for name, ex in (("R/R0 - 1 (as published)", cd["raw"]), ("div", cd["ex"]), ("sub", cs["ex"])):
            try:
                tau, seed, rms, n = fit(t, ex)
                print(f"  {name:26s} tau = {tau:.3f}  seed = {seed:.3e}  rms(ln) = {rms:.3f}  ({n} rows)")
            except ValueError as err:
                neg = int(np.sum(w & (ex <= 0)))
                print(f"  {name:26s} no fit: {err}; {neg} of {int(w.sum())} window rows <= 0, "
                      f"range {100 * ex[w].min():+.2f}% to {100 * ex[w].max():+.2f}%")
        if i < len(t):
            j = i - 1
            grow = s["RA"][j] / s["RA"][0] - 1.0
            print(f"  at t = {t[j]:.0f} (last disjoint row; d = {s['sep'][j]:.2f}"
                  f"{'' if cd['in_range'][j] else ', curve held at d = %g' % curve[0][0]}): "
                  f"R/R0 - 1 = {100 * grow:+.2f}%, the field's part {100 * cd['companion'][j]:+.2f} "
                  f"points ({100 * cd['companion'][j] / grow:.0f} %), own {100 * cd['ex'][j]:+.2f}% "
                  f"(div) / {100 * cs['ex'][j]:+.2f}% (sub)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
