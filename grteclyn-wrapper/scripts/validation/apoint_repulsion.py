"""GPU_PLAN #8: the scalar-charge law from the rest-release a-points.

Two like-oriented drainhole throats, equal mass, released from rest at
d = 12.  Gravity pulls them together; the phantom support field pushes them
apart with |F_phi / F_grav| = (a^2 + m^2) / m^2, so the NET acceleration is
outward and scales as (a^2 + m^2)/m^2 - 1 = a^2/m^2 for m = 1.

Measurement, following runs/wormhole_merger/03_two_throats/NOTES.md: the pit
position is an inverse-chi-weighted centroid of the cached chi_z slice, NOT
throat_track.dat (whose 0.03 quantum is the whole early displacement).  The
gauge under-reads motion while it settles, so only t = 3.5 .. 10.5 is fitted.
The acceleration is the quadratic coefficient of the separation change,
d(t) = d0 + v t + a t^2 / 2, which is what the archived +0.0127 (a = 2) and
+0.0042 (a = 1) numbers mean -- run this on those two arms first, it
reproduces them, and that is the validation of everything else it prints.

Usage: apoint_repulsion.py <run_dir> [<run_dir> ...] [--window 3.5 10.5]
"""
import argparse
import glob
import os

import numpy as np

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('run_dirs', nargs='+')
ap.add_argument('--window', nargs=2, type=float, default=[3.5, 10.5],
                metavar=('T0', 'T1'), help='fit window (default 3.5 10.5)')
ap.add_argument('--box', type=float, default=3.0,
                help='half-width of the window around each pit, code units')
ap.add_argument('--split', type=float, default=32.0,
                help='x that separates throat A from throat B')
args = ap.parse_args()


def pit_centroid(arr, extent, xlo, xhi, box):
    """Inverse-chi-weighted centroid of the pit inside [xlo, xhi]."""
    ny, nx = arr.shape
    x = np.linspace(extent[0], extent[1], nx)
    y = np.linspace(extent[2], extent[3], ny)
    X, Y = np.meshgrid(x, y)                      # arr is [y, x]
    sel = (X >= xlo) & (X < xhi)
    if not sel.any():
        return np.nan, np.nan
    a = np.where(sel, arr, np.inf)
    j, i = np.unravel_index(np.argmin(a), a.shape)
    x0, y0 = X[j, i], Y[j, i]
    win = sel & (np.abs(X - x0) <= box) & (np.abs(Y - y0) <= box)
    w = np.where(win, 1.0 / np.clip(arr, 1e-12, None), 0.0)
    s = w.sum()
    return float((w * X).sum() / s), float((w * Y).sum() / s)


def series(run_dir, box):
    files = sorted(glob.glob(os.path.join(
        run_dir, 'frames', '_slice_cache', 'chi_z', '*.npz')))
    rows = []
    for f in files:
        d = np.load(f)
        arr, ext, t = d['arr'], d['extent'], float(d['time'])
        xa, ya = pit_centroid(arr, ext, ext[0], args.split, box)
        xb, yb = pit_centroid(arr, ext, args.split, ext[1], box)
        rows.append((t, xa, ya, xb, yb, xb - xa))
    return np.array(rows)


def accel(t, sep, t0, t1):
    """Quadratic coefficient of the separation change over the window."""
    m = (t >= t0) & (t <= t1)
    if m.sum() < 3:
        return np.nan, np.nan, 0
    c = np.polyfit(t[m], sep[m] - sep[m][0], 2)
    # 1-sigma on the quadratic coefficient from the fit residuals
    resid = sep[m] - sep[m][0] - np.polyval(c, t[m])
    dof = max(m.sum() - 3, 1)
    V = np.linalg.inv(np.vander(t[m], 3).T @ np.vander(t[m], 3))
    sig = np.sqrt((resid @ resid) / dof * V[0, 0])
    return 2.0 * c[0], 2.0 * sig, int(m.sum())


print(f"fit window t = {args.window[0]} .. {args.window[1]}   "
      f"pit box +/-{args.box}   (a = quadratic coefficient of the separation)")
print(f"{'run':<28} {'a_throat':>8} {'n':>3} {'sep(t0)':>9} {'sep(end)':>9} "
      f"{'accel':>12} {'+/-':>9}")
out = {}
for rd in args.run_dirs:
    rd = rd.rstrip('/')
    name = os.path.basename(rd)
    r = series(rd, args.box)
    if not len(r):
        print(f"{name:<28}  no chi_z slice cache")
        continue
    t, sep = r[:, 0], r[:, 5]
    a, sig, n = accel(t, sep, *args.window)
    # throat radius straight from the run's own params
    ar = np.nan
    p = os.path.join(rd, 'params.txt')
    if os.path.exists(p):
        for line in open(p):
            if line.strip().startswith('wormhole_throat_radius_A'):
                ar = float(line.split('=')[1].split('#')[0])
                break
    print(f"{name:<28} {ar:8.2f} {n:3d} {sep[0]:9.4f} {sep[-1]:9.4f} "
          f"{a:+12.5f} {sig:9.5f}")
    out[name] = (ar, a, sig)

if len(out) > 1:
    ref = min(out.values(), key=lambda v: v[0])       # smallest a is the unit
    a0, acc0, _ = ref
    print(f"\nscaling, normalised to a = {a0:g}  "
          f"(prediction: net push ~ (a^2 + m^2)/m^2 - 1 = a^2, m = 1)")
    print(f"{'run':<28} {'a':>6} {'measured':>10} {'predicted':>10} {'ratio':>8}")
    for k, (ar, acc, sig) in sorted(out.items(), key=lambda kv: kv[1][0]):
        pred = (ar ** 2) / (a0 ** 2)
        meas = acc / acc0
        print(f"{k:<28} {ar:6.2f} {meas:10.3f} {pred:10.3f} "
              f"{meas / pred:8.3f}")
