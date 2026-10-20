#!/usr/bin/env python3
"""The phantom field's scalar charge D of 3D spinning runs, measured from the slice cache.

The background's field is exactly psi = (D/eta0)(atan(eta/eta0) - pi/2) with
the table's phi = psi / sqrt(4 pi) (analysis/spinning_wormhole/conventions.py),
and the 3D data put it on the isotropic radius r, eta = r - eta0^2/(4 r)
(Examples/SpinningWormhole/SpinningWormholeInitialData.hpp).  So on the
equatorial slice the run's own phi is fitted, by linear least squares, to

    phi(r) = a + D g(r),   g(r) = (atan(eta(r)/eta0) - pi/2) / (eta0 sqrt(4 pi)),

on the annulus between the throat's dynamics (r >= R_IN) and the sponge
(r <= R_OUT_FRAC * L): D is the charge the run actually carries, a the drift
of the field's asymptotic value.  Read per run: the first cached slice (t = 0)
and the last one inside its trust window.

Numpy only, reads the cache and writes nothing but stdout, so it runs on a GPU
node beside the runs:

    python3 measure_scalar_charge.py <runs root> <run>:<t_max> [<run>:<t_max> ...]

prints one TSV row per (run, slice): run, which, t, L, D, a, rms of the fit
relative to the field's range over the annulus, pixels used.
"""

from __future__ import annotations

import glob
import math
import os
import re
import sys

import numpy as np

ETA0 = 2.0              # every drainhole rung: eta0 = 2 (code units)
R_IN = 6.0              # inside this the throat moves
R_OUT_FRAC = 0.35       # of L: the sponge starts at 0.375 L


def box_length(run_dir: str) -> float:
    with open(os.path.join(run_dir, "params.txt")) as fh:
        for line in fh:
            m = re.match(r"\s*L\s*=\s*([0-9.eE+-]+)", line)
            if m:
                return float(m.group(1))
    raise ValueError(f"no L in {run_dir}/params.txt")


def slice_time(path: str) -> float:
    with np.load(path) as z:
        return float(z["time"])


def fit(path: str, L: float) -> tuple[float, float, float, float, int]:
    with np.load(path) as z:
        arr = np.asarray(z["arr"], dtype=np.float64)
        x0, x1, y0, y1 = (float(v) for v in z["extent"])
        t = float(z["time"])
    ny, nx = arr.shape
    x = x0 + (np.arange(nx) + 0.5) * (x1 - x0) / nx - 0.5 * (x0 + x1)
    y = y0 + (np.arange(ny) + 0.5) * (y1 - y0) / ny - 0.5 * (y0 + y1)
    r = np.hypot(x[None, :], y[:, None])
    sel = (r >= R_IN) & (r <= R_OUT_FRAC * L) & np.isfinite(arr)
    rr, phi = r[sel], arr[sel]
    eta = rr - ETA0**2 / (4.0 * rr)
    g = (np.arctan(eta / ETA0) - 0.5 * math.pi) / (ETA0 * math.sqrt(4.0 * math.pi))
    A = np.stack([np.ones_like(g), g], axis=1)
    (a, d), *_ = np.linalg.lstsq(A, phi, rcond=None)
    rms = float(np.sqrt(np.mean((A @ np.array([a, d]) - phi) ** 2)) / max(np.ptp(phi), 1e-300))
    return t, float(d), float(a), rms, int(sel.sum())


def main(argv: list[str]) -> int:
    root, pairs = argv[1], argv[2:]
    print("run\twhich\tt\tL\tD\ta\trms_rel\tpixels")
    for pair in pairs:
        run, t_max = pair.rsplit(":", 1)
        hits = glob.glob(os.path.join(root, "**", run), recursive=True)
        if not hits:
            print(f"# {run}: not found", file=sys.stderr)
            continue
        run_dir = sorted(hits, key=len)[0]
        L = box_length(run_dir)
        paths = sorted(glob.glob(os.path.join(run_dir, "frames", "_slice_cache", "phi_z", "slice_*.npz")))
        if not paths:
            print(f"# {run}: no phi_z slice cache", file=sys.stderr)
            continue
        last = None
        for p in reversed(paths):            # the last slice inside the trust window
            if slice_time(p) <= float(t_max) + 1e-9:
                last = p
                break
        for which, p in (("t0", paths[0]), ("end", last)):
            if p is None:
                continue
            t, d, a, rms, n = fit(p, L)
            print(f"{run}\t{which}\t{t:.4f}\t{L:g}\t{d:.8f}\t{a:.3e}\t{rms:.2e}\t{n}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
