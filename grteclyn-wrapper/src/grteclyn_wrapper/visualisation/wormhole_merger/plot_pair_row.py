#!/usr/bin/env python3
r"""The pair interaction on one strip: sign rule, force law and width ladder (matched pairs).

The article's two single-column pair figures merged into one two-column
``figure*`` at the top of the page (the user, 2026-09-18): panels (a)/(b)
are ``plot_sign_rule``'s three-pairs-one-knob-apart story with the 3/2
ratio, panel (c) is ``plot_force_law``'s separation ladder (added
2026-09-25, when the user asked where Sec. V B's four displacements are
drawn).  The placement panels (d)/(e) left with the superposed campaign
(the user, 2026-10-05), and panel (d) became ``plot_width_ladder``'s width
ladder the same day, once the matched a = 1/1.5/3 pairs were reduced into
the pack.  Each panel is drawn by ITS OWN module
(``figure_panels`` / ``figure_panel``), so this module owns nothing but the
canvas, the lettering and the file; any change to what a panel says belongs
in its home module, and lands here on the next run.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_pair_row

The file lives under ``figures/03_two_throats/``.

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
    plot_force_law, plot_sign_rule, plot_width_ladder, style,
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
    # 1.43 in per panel, as the three-panel strip had; the keys sit above the
    # frames (the paper's rule: no names inside a frame).  2.0 in tall, near-
    # square frames: at 3.0 in they were tall slivers (the user, 2026-10-07:
    # "too tall for no reason").
    fig, (axA, axB, axF, axW) = plt.subplots(1, 4, figsize=(5.7, 2.0),
                                             constrained_layout=True)
    plot_sign_rule.figure_panels(axA, axB, pack_root=args.pack_root, stacked=False,
                                 keys=True)
    plot_force_law.figure_panel(axF, pack_root=args.pack_root, keys=True)
    plot_width_ladder.figure_panel(axW, pack_root=args.pack_root, keys=True)
    style.tag_keys(fig, (axA, axB, axF, axW), [f"({c})" for c in "abcd"], row="last")
    problems = style.label_audit(fig)
    print(f"[pair row] label audit: {len(problems)} problem(s) {problems[:3]}")

    out = (pathlib.Path(args.out) if args.out else
           figure_dir("03_two_throats", args.pack_root) / "pair_interaction.png")
    png = style.save(fig, out)
    print(f"[pair row] wrote {png} (+pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
