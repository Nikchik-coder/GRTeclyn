#!/usr/bin/env python3
"""The fill-window twin (article Fig. 13, plot_fill_insensitivity): verify its
numbers and whether the difference fronts arrive on the fill's causal clock
t = 57 + (R - 1.9).

Reads only the tracked pack; prints a report; writes nothing.

    grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/analysis/merger_feedback/waves_fill_twin.py
"""

from __future__ import annotations

import numpy as np

from grteclyn_wrapper.visualisation.wormhole_merger import plot_fill_insensitivity as F
from grteclyn_wrapper.visualisation.wormhole_merger import streams
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import PACK_ROOT

P = PACK_ROOT / "campaign" / F.GROUP
T0, SKIN = 57.0, 1.9          # core_fill_from_time, core_fill_radius_start of the freeze arm


def main():
    ta, ya = streams.load_mode(P / F.ARM_A / "Weyl4_mode_22.dat", list(F.RADII))
    tb, yb = streams.load_mode(P / F.ARM_B / "Weyl4_mode_22.dat", list(F.RADII))
    n = min(ta.size, tb.size)
    assert np.allclose(ta[:n], tb[:n])
    t = ta[:n]
    keep = t >= F.T_ENGAGE
    print(f"shared record t = {t[keep][0]:.2f}-{t[keep][-1]:.2f}, dt = {np.median(np.diff(t)):.3f}")
    for R in F.RADII:
        a, b = ya[R][:n], yb[R][:n]
        d = np.abs(a - b)[keep]
        pk = np.abs(a[keep]).max()
        frac = d / pk
        clock = T0 + (R - SKIN)
        arr = {}
        for thr in (1e-9, 1e-8, 1e-7, 1e-6, 1e-5):
            i = np.nonzero(frac > thr)[0]
            arr[thr] = t[keep][i[0]] if i.size else None
        ov = np.abs(np.vdot(a[keep], b[keep])) / np.sqrt(np.vdot(a[keep], a[keep]).real *
                                                          np.vdot(b[keep], b[keep]).real)
        print(f"R = {R:g}: max|dPsi4|/peak = {100 * frac.max():.4f} % (peak {pk:.3e});  overlap {ov:.9f};  "
              f"causal clock t = {clock:.1f}")
        print("        first t with |dPsi4|/peak > 1e-9 / 1e-8 / 1e-7 / 1e-6 / 1e-5: "
              + " / ".join("-" if v is None else f"{v:.2f}" for v in arr.values())
              + "   (minus clock: " + " / ".join("-" if v is None else f"{v - clock:+.2f}" for v in arr.values()) + ")")
        # the largest difference reached BEFORE the light cone
        pre = t[keep] < clock
        if pre.any():
            print(f"        max |dPsi4|/peak before the clock: {frac[pre].max():.1e}")
    # arrival speed of the 1e-7 front between the spheres
    fr = []
    for R in F.RADII:
        a, b = ya[R][:n], yb[R][:n]
        frac = (np.abs(a - b) / np.abs(a[keep]).max())[keep]
        i = np.nonzero(frac > 1e-7)[0]
        fr.append((R, t[keep][i[0]]))
    print("1e-7 front speeds between spheres: " + ", ".join(
        f"{R1:g}->{R2:g}: {(R2 - R1) / (t2 - t1):.2f} c" for (R1, t1), (R2, t2) in zip(fr[:-1], fr[1:])))
    # panel (a)'s amplitude: the stream is already r*Psi4 -- check across spheres
    pk = {R: np.abs(ya[R][:n][keep]).max() for R in F.RADII}
    print("peak |stream| per sphere (r*Psi4 if already radius-folded):",
          ", ".join(f"R{R:g} {v:.4f}" for R, v in pk.items()),
          f"-> R*stream at R=20 would be {20 * pk[20.0]:.3f}")


if __name__ == "__main__":
    main()
