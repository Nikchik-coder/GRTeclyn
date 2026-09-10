"""Journal typography for every figure in this package.

There is no TeX on this machine and nothing may be installed on it, so
``text.usetex`` is not an option.  It is also not needed: matplotlib ships the
**STIX** fonts, which are the Times-family faces the APS and AIP journals set
their text in, together with a matching ``stix`` math font set.  Turning both on
gives a figure whose text sits beside the body of a paper without looking
pasted in, and whose symbols match the ones in the equations.

    from grteclyn_wrapper.visualisation.wormhole_merger.style import paper, INK, MUTED

    paper()          # once, before any pyplot call that creates a figure

Write labels as mathtext -- ``r"$R_{\\mathrm{min}}$"``, ``r"$\\varepsilon$"`` --
and they render in the same face as the surrounding prose.
"""

from __future__ import annotations

import matplotlib

# Ink, not black: pure black on white is harsher than print and reads as heavier
# than the curves it labels.
INK = "#1a1a18"
MUTED = "#5f5d57"
FAINT = "#a5a29a"
GRID = "#e8e6e0"
GROUND = "#ffffff"

# One cool, one warm, with a neutral between: on the seed scan the SIGN of the
# kick is the thing the eye must read first, so the palette diverges on sign and
# the shade tracks the amplitude.
SIGNED = {
    "-0.1": "#123a5e", "-0.01": "#2a78d6", "-0.001": "#7fb2e8",
    "+0.001": "#f2ab84", "+0.01": "#e2622c", "+0.1": "#8a3210",
}


def paper(base: float = 10.0) -> None:
    """Set journal typography and a recessive frame. Call before plotting."""
    matplotlib.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIXGeneral", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": base,
        "axes.titlesize": base * 1.0,
        "axes.labelsize": base * 1.0,
        "xtick.labelsize": base * 0.9,
        "ytick.labelsize": base * 0.9,
        "legend.fontsize": base * 0.9,
        "figure.facecolor": GROUND,
        "axes.facecolor": GROUND,
        "savefig.facecolor": GROUND,
        # The frame is scaffolding: it should be visible only when looked for.
        "axes.edgecolor": FAINT,
        "axes.linewidth": 0.7,
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "xtick.color": FAINT,
        "ytick.color": FAINT,
        "xtick.labelcolor": MUTED,
        "ytick.labelcolor": MUTED,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 3.0,
        "ytick.major.size": 3.0,
        "legend.frameon": False,
        "lines.solid_capstyle": "round",
        "axes.axisbelow": True,
    })
