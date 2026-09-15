#!/usr/bin/env python3
"""Gate late-time constraint junk out of a psi4 mode .dat, per extraction sphere.

The junk (non-propagating, high-frequency, arrives near-simultaneously at all
spheres) is detected per sphere as the first time the second difference of
Re(r*psi4) exceeds ``--nsigma`` times its clean-window rms.  Everything before
the onset is kept UNTOUCHED -- no filtering, no smoothing, zero distortion of
the measurement -- then a ``--taper``-long cosine roll-off takes the record to
zero.  The output is a valid mode .dat (header preserved) that the standard
plotting tools accept.

Why not a low-pass filter: zero-phase filtering bleeds the (much larger) junk
backwards into the clean window, and the junk has power inside the physical
band.  Measured on single_eps_p1e2_q5e2_ml4_t100 (2026-09-15): 12-38 %%
distortion of the clean wave, junk at R=18 not reduced at all.

Usage:
  gate_psi4_junk.py <psi4_mode_*.dat> [--nsigma 8] [--taper 4]
                    [--clean-window 15 55] [--search-after 40] [--out PATH]
"""
import argparse
import numpy as np


def _taper_ending_at(t: np.ndarray, cut: float, taper: float) -> np.ndarray:
    """Weight 1 up to cut-taper, cosine roll-off, exactly 0 at and after cut.
    The taper ends AT the cut: nothing at or past the cut survives.  (The
    first version started the taper at the cut and let the leading junk
    cycles through at near-full weight.)"""
    w = np.ones_like(t)
    ramp = (t > cut - taper) & (t < cut)
    w[ramp] = 0.5 * (1.0 - np.cos(np.pi * (cut - t[ramp]) / taper))
    w[t >= cut] = 0.0
    return w


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dat")
    ap.add_argument("--nsigma", type=float, default=8.0)
    ap.add_argument("--taper", type=float, default=4.0)
    ap.add_argument("--clean-window", type=float, nargs=2, default=(15.0, 55.0))
    ap.add_argument("--search-after", type=float, default=40.0)
    ap.add_argument("--pad", type=float, default=2.0,
                    help="start the taper this long BEFORE the detected onset")
    ap.add_argument("--cuts", type=float, nargs="+", default=None,
                    help="explicit per-sphere cut times (coordinate t, one per "
                         "radius, in header order); overrides detection and --u-max")
    ap.add_argument("--u-max", type=float, default=None,
                    help="instead of auto-detection, cut every sphere at the "
                         "same retarded time u = t - R (radii from the header)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    with open(args.dat) as fh:
        header = [ln for ln in fh if ln.startswith("#")]
    d = np.loadtxt(args.dat)
    t = d[:, 0]
    n_r = (d.shape[1] - 1) // 2

    radii = None
    if args.u_max is not None:
        import re
        radii = [float(m) for m in re.findall(r"R=([0-9.]+)\)\s+Im", "".join(header))]
        if len(radii) != n_r:
            raise SystemExit(f"--u-max needs radii in the header; parsed {radii}")

    if args.cuts is not None and len(args.cuts) != n_r:
        raise SystemExit(f"--cuts needs {n_r} values")

    for i in range(n_r):
        if args.cuts is not None:
            cut = float(args.cuts[i])
            d[:, 1 + 2 * i] *= _taper_ending_at(t, cut, args.taper)
            d[:, 2 + 2 * i] *= _taper_ending_at(t, cut, args.taper)
            print(f"col pair {i}: zero from t={cut:.1f} (explicit)")
            continue
        if radii is not None:
            cut = radii[i] + args.u_max
            d[:, 1 + 2 * i] *= _taper_ending_at(t, cut, args.taper)
            d[:, 2 + 2 * i] *= _taper_ending_at(t, cut, args.taper)
            print(f"col pair {i}: R={radii[i]:g}, zero from t={cut:.1f} (u={args.u_max:g})")
            continue
        x = d[:, 1 + 2 * i]
        d2 = np.abs(np.diff(x, 2))
        tc = t[1:-1]
        mc = (tc >= args.clean_window[0]) & (tc <= args.clean_window[1])
        rms = float(np.sqrt(np.mean(d2[mc] ** 2)))
        bad = np.where((d2 > args.nsigma * rms) & (tc > args.search_after))[0]
        if not len(bad):
            print(f"col pair {i}: no junk found, kept whole record")
            continue
        cut = float(tc[bad[0]]) - args.pad
        d[:, 1 + 2 * i] *= _taper_ending_at(t, cut, args.taper)
        d[:, 2 + 2 * i] *= _taper_ending_at(t, cut, args.taper)
        print(f"col pair {i}: junk onset t={cut + args.pad:.1f}, zero from t={cut:.1f}")

    out = args.out or args.dat.replace(".dat", "_gated.dat")
    with open(out, "w") as fh:
        fh.writelines(header)
        fh.write("# late-time junk gated per sphere by gate_psi4_junk.py "
                 f"(nsigma={args.nsigma}, taper={args.taper}); clean part untouched\n")
        np.savetxt(fh, d, fmt="%.16e")
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
