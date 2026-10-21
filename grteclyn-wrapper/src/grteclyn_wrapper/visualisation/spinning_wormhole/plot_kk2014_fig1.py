#!/usr/bin/env python3
r"""Kleihaus & Kunz 2014, Fig. 1, as published, with our solutions on it.

AN INTERNAL CHECK, NOT A PAPER FIGURE: the background is their printed
figure, which a paper cannot reuse without the publisher's permission.  The
paper figure is ``plot_kk2014_comparison`` (our curves against their
digitized numbers).

Background: Kleihaus & Kunz, "Rotating Ellis wormholes in four
dimensions", PRD 90, 121503(R) (2014), arXiv:1409.1503.  Our members of the same family (eta0 = 1, gamma = 0 in the packed solver
table) are drawn on top as open circles, at the places the figure's own axes
give them: M/M0 = mu_+/R_e and J/J0 = 2J_+/R_e^2 in (a), R_p/R and R_A/R in
(b) (normalisation and calibration: ``kk2014.py``).  Our
Omega J/(Omega0 J0) equals M/M0 to the packed Smarr gate, so those circles
would sit on the M/M0 ones and are not drawn twice.  ``--check`` overdraws
the closed-form Kerr curves on the printed ones.

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.plot_kk2014_fig1

Writes ``results/spinningwormhole/figures/solver/kk2014_fig1_overlay``
(PNG + PDF).
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from PIL import Image  # noqa: E402

from grteclyn_wrapper.visualisation.spinning_wormhole import kk2014, solutions  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402

OUT = solutions.REPO / "results" / "spinningwormhole" / "figures" / "solver" / "kk2014_fig1_overlay"
OURS = dict(ls="none", marker="o", ms=4.6, mfc="none", mec="black", mew=0.9, clip_on=False,
            zorder=5)


def draw(image: pathlib.Path, fam: dict[str, np.ndarray], sep: float, check: bool):
    img = Image.open(image).convert("RGB")
    w, h = img.size
    boxes = kk2014.frames(np.asarray(img.convert("L"), dtype=float))
    fig = plt.figure(figsize=(w / 100.0, h / 100.0), dpi=100)
    bg = fig.add_axes((0.0, 0.0, 1.0, 1.0))
    bg.imshow(np.asarray(img), interpolation="lanczos", aspect="auto")
    bg.set_xlim(-0.5, w - 0.5)
    bg.set_ylim(h - 0.5, -0.5)
    bg.set_axis_off()

    panels = []
    for (left, right, top, bottom), (xr, yr) in zip(boxes, kk2014.RANGES):
        ax = fig.add_axes(((left + 0.5) / w, 1.0 - (bottom + 0.5) / h,
                           (right - left) / w, (bottom - top) / h))
        ax.set(xlim=xr, ylim=yr)
        ax.set_axis_off()
        ax.patch.set_visible(False)
        panels.append(ax)

    counts = []
    for ax, (xr, yr), keys in zip(panels, kk2014.RANGES, (("M", "J"), ("Rp", "RA"))):
        idx = kk2014.thin(fam["v"], [fam[k] for k in keys], (xr[1] - xr[0], yr[1] - yr[0]), sep)
        for k in keys:
            ax.plot(fam["v"][idx], fam[k][idx], **OURS)
        counts.append(len(idx))

    if check:
        v = np.linspace(0.0, 1.0, 301)
        k = kk2014.kerr(v)
        line = dict(color="black", lw=0.8, ls=(0, (2.0, 2.0)), zorder=6)
        for key in ("J", "OmJ"):
            panels[0].plot(v, k[key], **line)
        for key in ("Rp", "RA"):
            panels[1].plot(v, k[key], **line)

    fig.legend([Line2D([], [], **{**OURS, "clip_on": True})],
               ["this work, same symmetric family: M/M$_0$ and J/J$_0$ in (a), "
                "R$_p$/R and R$_A$/R in (b)"],
               loc="upper center", bbox_to_anchor=(0.5, 0.995), frameon=False,
               fontsize=9.5, handletextpad=0.4)
    return fig, counts, boxes


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--image", type=pathlib.Path, default=kk2014.IMAGE)
    ap.add_argument("--table", type=pathlib.Path, default=solutions.TABLE)
    ap.add_argument("--out", type=pathlib.Path, default=OUT)
    ap.add_argument("--sep", type=float, default=0.035,
                    help="circle spacing along each curve, in frame fractions (0: every point)")
    ap.add_argument("--check", action="store_true",
                    help="overdraw the closed-form Kerr curves to show the axis calibration")
    args = ap.parse_args(argv)

    fam = kk2014.symmetric_family(solutions.load(args.table))
    fig, counts, boxes = draw(args.image, fam, args.sep, args.check)
    problems = style.label_audit(fig)
    png = style.save(fig, args.out, dpi=200)
    print("frames (left, right, top, bottom) px: "
          + "; ".join("(" + ", ".join(f"{b:g}" for b in box) + ")" for box in boxes))
    print(f"symmetric family: {len(fam['v'])} members, v_e {fam['v'][0]:.4f}-{fam['v'][-1]:.4f}; "
          f"circles per curve: {counts[0]} (a), {counts[1]} (b)")
    print(f"label audit: {'clean' if not problems else f'{len(problems)} problem(s)'}")
    print(f"wrote {png}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
