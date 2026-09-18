#!/usr/bin/env python3
r"""The pair interaction on one strip: the sign rule beside the placement curve.

The article's two single-column pair figures merged into one two-column
``figure*`` at the top of the page (the user, 2026-09-18): panels (a)/(b)
are ``plot_sign_rule``'s three-pairs-one-knob-apart story with the 3/2
ratio, panels (c)/(d) are ``plot_placement_curve``'s ruler calibration and
the head-on scout's genuine squeeze.  Each pair of panels is drawn by ITS
OWN module (``figure_panels`` in both), so this module owns nothing but the
canvas, the lettering and the file; any change to what a panel says belongs
in its home module, and lands here on the next run.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_pair_row

The file lives under ``figures/03_two_throats/`` -- the strip leads with the
sign rule -- although panels (c)/(d) read ``campaign/04_binary_headon``.

STYLE: the seed-branches grammar on the full 7.05 in width; letter tags
above the frames, as on the collapse pages; the semantics and every number
stay in the caption and in the home modules' console prints.
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import (  # noqa: E402
    plot_placement_curve, plot_sign_rule, style,
)
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import (  # noqa: E402
    PACK_ROOT, figure_dir,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    style.prd(base=10.0)
    fig, (axA, axB, axC, axD) = plt.subplots(1, 4, figsize=(7.05, 2.4),
                                             constrained_layout=True)
    plot_sign_rule.figure_panels(axA, axB, pack_root=args.pack_root, stacked=False)
    plot_placement_curve.figure_panels(axC, axD, pack_root=args.pack_root,
                                       stacked=False)
    for ax, letter in zip((axA, axB, axC, axD), "abcd"):
        ax.text(0.0, 1.05, f"({letter})", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=9, color=style.INK)

    out = (pathlib.Path(args.out) if args.out else
           figure_dir("03_two_throats", args.pack_root) / "pair_interaction.png")
    png = style.save(fig, out)
    print(f"[pair row] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
