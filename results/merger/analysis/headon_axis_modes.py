#!/usr/bin/env python3
r"""The head-on's quadrupole about its own axis, from the in-code z-based modes.

Both head-ons -- the drainhole chain and its vacuum BBH control -- fall along
x (mouths / punctures at x = -+4), but the in-code extraction decomposes Psi_4
about z.  A quadrupole axisymmetric about x splits over the z-based modes as

    h_20 = -h'_20 / 2,    h_2,+-2 = sqrt(3/8) h'_20,    h_2,+-1 = 0

(Wigner d^2_{m0}(pi/2); h' about the collision axis), so the z-based (2,0)
carries a QUARTER of the l = 2 power and half the amplitude of the mode about
the collision axis.  Until 2026-10-05 every head-on number read that (2,0)
as the whole channel: energies 4x low, amplitudes 2x low.  The check: times
four, the vacuum control's E/M = 1.4e-4 becomes 5.6e-4 against the published
5.5e-4 for equal-mass head-on infall.

This writes ``<stem>_axis.dat`` beside each (2,0) stream: the same columns and
headers, the data times 2 -- h'_20 = -2 h_20, with the sign kept from the
z-based record (the overall sign of a rotated mode is a choice of polarisation
basis).  It refuses unless the (2,2) partner stands at sqrt(3/2) of the (2,0)
on every sphere, which is what axisymmetry about x requires.

    python results/merger/analysis/headon_axis_modes.py [pack]   # pack = results/merger
"""

from __future__ import annotations

import pathlib
import sys

import numpy as np

RATIO = np.sqrt(1.5)
TOL = 0.10

STREAMS = (   # (run dir under campaign/, (2,0) file, (2,2) file)
    ("04_binary_headon/csm/merge_headon_flip_d8_v1_L128_SERIES",
     "Weyl4_mode_20.dat", "Weyl4_mode_22.dat"),
    ("07_bbh_control/bbh_headon_d8_L128_lvl5_t100",
     "weyl_extraction_mode_20.dat", "weyl_extraction_mode_22.dat"),
    # FARZONE-ho: the same head-on in an L = 512 box, spheres to R = 180, t = 250
    # (2026-10-08: the gallery's head-on row).
    ("08_convergence/farzone_headon_flip_d8_L512_lvl6_t250_csm",
     "Weyl4_mode_20.dat", "Weyl4_mode_22.dat"),
    # CONV-fz: FARZONE-ho one level coarser and one finer, to t = 100 (2026-10-08: Fig.
    # convergence (d)).
    ("08_convergence/farzone_headon_flip_d8_L512_lvl5_t100_csm",
     "Weyl4_mode_20.dat", "Weyl4_mode_22.dat"),
    ("08_convergence/farzone_headon_flip_d8_L512_lvl7_t100_csm",
     "Weyl4_mode_20.dat", "Weyl4_mode_22.dat"),
)


def _read(path: pathlib.Path):
    head, rows = [], []
    with open(path) as fh:
        for line in fh:
            (head if line.startswith("#") else rows).append(line)
    data = np.loadtxt(rows) if rows else np.empty((0, 0))
    radii = None
    for line in head:
        if "r =" in line:
            radii = [float(x) for x in line.split("=", 1)[1].split()][::2]
    return head, data, radii


BURST = 60.0    # the burst passes each sphere within this many units of R
BODY = 0.25     # ...and its body is where |h_20| is above this of its peak


def ratios(d20: np.ndarray, d22: np.ndarray, radii) -> list[float]:
    """rms |h_22| / rms |h_20| per sphere, over the burst's body.

    Over the whole record a late noise floor can take the peak: R = 28 cuts
    the level-1 refinement cube's corners, and past t ~ 90 its (2,0) noise
    outgrows the burst (peak ratio 0.87 over t = 28-100, 1.224 on the body).
    """
    t = d20[:, 0]
    out = []
    for k, R in enumerate(radii):
        a20 = np.hypot(d20[:, 1 + 2 * k], d20[:, 2 + 2 * k])
        a22 = np.hypot(d22[:, 1 + 2 * k], d22[:, 2 + 2 * k])
        win = (t >= R) & (t <= R + BURST)
        if not win.any():    # the record stops before the burst reaches this sphere
            out.append(float("nan"))
            continue
        body = win & (a20 >= BODY * a20[win].max())
        out.append(float(np.sqrt((a22[body] ** 2).sum()
                                 / (a20[body] ** 2).sum())))
    return out


def main(argv: list[str]) -> int:
    pack = pathlib.Path(argv[1] if len(argv) > 1 else "results/merger")
    for run, f20, f22 in STREAMS:
        d = pack / "campaign" / run
        head, d20, radii = _read(d / f20)
        _, d22, radii22 = _read(d / f22)
        if radii != radii22 or d20.shape != d22.shape:
            raise SystemExit(f"{run}: {f20} and {f22} do not share spheres/rows")
        r = ratios(d20, d22, radii)
        bad = [(R, x) for R, x in zip(radii, r) if abs(x / RATIO - 1.0) > TOL]
        if bad:
            raise SystemExit(f"{run}: |h22/h20| off sqrt(3/2) at {bad} -- "
                             f"not axisymmetric about x; nothing written")
        out = d.joinpath(f20.replace(".dat", "_axis.dat"))
        cols = d20.copy()
        cols[:, 1:] *= 2.0
        note = ("# collision-axis quadrupole: h'_20 = -2 h_20 (x-axis source; the z-based (2,0) "
                "carries a quarter of the l = 2 power), sign kept from the z-based record; "
                "written by results/merger/analysis/headon_axis_modes.py from " + f20 + "\n",
                "# check, burst-body rms |h22|/|h20| per sphere against sqrt(3/2) = 1.2247: "
                + " ".join(f"{R:g}:{x:.4f}" for R, x in zip(radii, r)) + "\n")
        with open(out, "w") as fh:
            fh.writelines(note)
            fh.writelines(head)
            np.savetxt(fh, cols, fmt="%.10e", delimiter="    ")
        print(f"{run}: wrote {out.name}; |h22/h20| "
              + " ".join(f"{x:.3f}" for x in r))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
