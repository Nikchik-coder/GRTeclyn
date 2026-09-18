#!/usr/bin/env python3
r"""The single-throat story on one strip: undeclared seed, its rate, declared seed.

The article's first two single-column figures merged into one two-column
``figure*`` at the top of the page (the user, 2026-09-18): panels (a)/(b)
are ``plot_branches``' resolution ladder -- one exact throat, two
resolutions, two fates, and the common exponential mode -- and panel (c) is
``plot_seed_branches``' declared-kick branching at one resolution.  Each
panel is drawn by ITS OWN module (``figure_panels`` / ``figure_panel``), so
this module owns nothing but the canvas, the lettering and the file; any
change to what a panel says belongs in its home module, where the provenance
notes live, and lands here on the next run.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_single_throat_row

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
    plot_branches, plot_seed_branches, style,
)
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import (  # noqa: E402
    PACK_ROOT, RUNS_ROOT, figure_dir,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--runs-root", default=str(RUNS_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    style.prd(base=10.0)
    fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(7.05, 2.5),
                                        constrained_layout=True)
    plot_branches.figure_panels(axA, axB, pathlib.Path(args.pack_root).expanduser())
    plot_seed_branches.figure_panel(axC, runs_root=args.runs_root)
    for ax, letter in zip((axA, axB, axC), "abc"):
        ax.text(0.0, 1.05, f"({letter})", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=9, color=style.INK)

    out = (pathlib.Path(args.out) if args.out else
           figure_dir("01_single_throat", args.pack_root) / "single_throat_instability.png")
    png = style.save(fig, out)
    print(f"[single-throat row] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
