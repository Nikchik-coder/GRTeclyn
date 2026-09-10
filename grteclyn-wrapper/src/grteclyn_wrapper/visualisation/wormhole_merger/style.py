"""Journal typography and the colour rules for every figure in this package.

There is no TeX on this machine and nothing may be installed on it, so
``text.usetex`` is not an option.  It is also not needed: matplotlib ships the
**STIX** fonts, which are the Times-family faces the APS and AIP journals set
their text in, together with a matching ``stix`` math font set.  Turning both on
gives a figure whose text sits beside the body of a paper without looking
pasted in, and whose symbols match the ones in the equations.

    from grteclyn_wrapper.visualisation.wormhole_merger import style

    style.paper()                       # once, before any figure is created
    ax.plot(t, y, **style.series(0))    # first series: ink, solid
    ax.plot(t, z, **style.series(1))    # second: deep blue, dashed
    style.save(fig, out)                # PNG + PDF, same basename

Write labels as mathtext -- ``r"$R_{\\mathrm{min}}$"``, ``r"$\\varepsilon$"`` --
and they render in the same face as the surrounding prose.

THE COLOUR RULES
----------------
Print, not a dashboard.  A line is identified by its *dash pattern* first and
its colour second, so the figure survives a greyscale printer and a
colour-blind reader; colour is the redundant channel, never the only one.

``series(i)``   unordered families (this run against that one).  Four slots, in
                a FIXED order -- ink, deep blue, burgundy, warm grey -- each
                with its own dash.  There is no fifth: a fifth series means the
                family is ordered (use ``ordinal``) or the figure is doing two
                jobs.  The four were checked, not eyeballed: worst pair 21.7
                OKLab dE under normal vision and 13.4 under simulated
                protanopia, against thresholds of 15 and 8.

``ordinal(n)``  ORDERED families -- refinement levels, extraction radii, kick
                amplitudes.  ``cividis`` reversed and cut off before its pale
                end, so the ramp runs light-to-dark with the lightest step
                still at 3.1:1 against white.  Reading order is the lightness,
                which is what an ordered family should be read by.

``SEQUENTIAL``  2D magnitude (a slice of chi, a norm): perceptually uniform,
                monotone in brightness.  ``cividis`` is the colour-blind
                optimised one; ``inferno``/``magma`` when the figure wants more
                contrast at the top end.

``DIVERGING``   2D data centred on zero (Weyl4, a residual, a difference):
                two hues meeting at a neutral midpoint.  Never a rainbow, and
                never a hue at the midpoint.
"""

from __future__ import annotations

import pathlib

import matplotlib
import numpy as np

__all__ = [
    "BURGUNDY", "CONTEXT", "DEEP_BLUE", "DIVERGING", "FAINT", "GRID", "GROUND",
    "INK", "MUTED", "SEQUENTIAL", "SEQUENTIAL_HOT", "SIGNED", "signed",
    "family", "ordinal", "ordinal_series", "paper", "save", "series",
]

# Ink, not black: pure black on white is harsher than print and reads as heavier
# than the curves it labels.
INK = "#1a1a18"
MUTED = "#5f5d57"
FAINT = "#a5a29a"
GRID = "#e8e6e0"
GROUND = "#ffffff"

# The three dark hues the recommendation asks for, plus one recessive slot for
# the curve that is context rather than a result.
DEEP_BLUE = "#1f4e79"
BURGUNDY = "#9b2226"
CONTEXT = "#8f8b81"

# Fixed order, never cycled.  (colour, dash, linewidth) -- the dash is the
# primary channel, so the order is chosen to keep adjacent series apart in
# pattern as well as in hue.
_SERIES = (
    (INK, (0, ()), 1.4),
    (DEEP_BLUE, (0, (6.5, 2.2)), 1.5),
    (BURGUNDY, (0, (1.3, 1.7)), 1.7),
    (CONTEXT, (0, (7.0, 2.0, 1.3, 2.0)), 1.5),
)

# The SIGN of a declared kick is the thing the eye must read first on the seed
# scan, so it takes the two poles of the campaign's own palette -- deep blue for
# a negative kick, burgundy for a positive one -- and the shade tracks the
# amplitude.  Same-magnitude pairs, which are the comparison the figure exists
# to make, separate by 23 (deep) and 17 (pale) OKLab dE under normal vision and
# 13 / 12 under simulated protanopia.
SIGNED = {
    "-0.1": "#0f3355", "-0.01": DEEP_BLUE, "-0.001": "#6a93bd",
    "+0.001": "#c9706f", "+0.01": BURGUNDY, "+0.1": "#5f1214",
}


def signed(label: str) -> str:
    """The colour for a kick written as a signed decimal, e.g. ``"+0.01"``."""
    if label in SIGNED:
        return SIGNED[label]
    # An amplitude the table does not name: fall back to the pole of its sign.
    return BURGUNDY if label.lstrip().startswith("+") else DEEP_BLUE

# 2D fields.  Named here so no module picks a colormap by hand.
SEQUENTIAL = "cividis"       # magnitude, colour-blind optimised
SEQUENTIAL_HOT = "inferno"   # magnitude, when the top end needs more contrast
DIVERGING = "RdBu_r"         # signed about zero, neutral at the middle

# The ordinal ramp: cividis from its dark end up to, but not into, the pale
# yellow that a 1-pt line cannot hold on white.  0.62 is where the lightest
# step still clears 3:1 against white (3.12), which a line needs and a heatmap
# cell does not -- the cut is for LINES.
_ORDINAL_CUT = 0.62


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
        "lines.dash_capstyle": "round",
        "axes.axisbelow": True,
        "image.cmap": SEQUENTIAL,
    })


def series(i: int, lw: float | None = None, **kw) -> dict:
    """Plot kwargs for the i-th member of an UNORDERED family.

    Raises past the fourth slot rather than inventing a fifth hue: a fifth
    curve means either an ordered family (``ordinal``) or a figure that has
    stopped saying one thing.
    """
    if not 0 <= i < len(_SERIES):
        raise IndexError(
            f"series slot {i}: the palette has {len(_SERIES)}. An ordered family "
            "belongs in ordinal(); an unordered one this large needs splitting."
        )
    colour, dash, width = _SERIES[i]
    out = {"color": colour, "linestyle": dash, "linewidth": lw if lw is not None else width}
    out.update(kw)
    return out


def family(n: int, lw: float | None = None) -> list[dict]:
    """Plot kwargs for ``n`` curves, whatever kind of family they are.

    Up to four: the fixed categorical slots, which is what an unordered family
    should be.  Beyond four there is no fifth hue to give, so the ramp takes
    over -- a family that large is nearly always ordered anyway (a refinement
    ladder, a chain of restarts, a set of radii) and the ramp says so.
    """
    if n <= len(_SERIES):
        return [series(i, lw=lw) for i in range(n)]
    return ordinal_series(n, lw=lw if lw is not None else 1.4)


def ordinal(n: int) -> list[str]:
    """``n`` colours for an ORDERED family, light (first) to dark (last)."""
    if n < 1:
        return []
    if n == 1:
        return [DEEP_BLUE]
    cmap = matplotlib.colormaps[SEQUENTIAL]
    return [matplotlib.colors.to_hex(cmap(x))
            for x in np.linspace(_ORDINAL_CUT, 0.0, n)]


def ordinal_series(n: int, lw: float = 1.4) -> list[dict]:
    """``ordinal`` colours carrying the dash cycle too, so an ordered family is
    still readable in greyscale."""
    dashes = [(0, ()), (0, (6.5, 2.2)), (0, (1.3, 1.7)), (0, (7.0, 2.0, 1.3, 2.0)),
              (0, (3.0, 1.6)), (0, (1.0, 1.4, 4.0, 1.4))]
    return [{"color": c, "linestyle": dashes[i % len(dashes)], "linewidth": lw}
            for i, c in enumerate(ordinal(n))]


def save(fig, path, dpi: int = 300, exts=("png", "pdf")) -> pathlib.Path:
    """Write the figure once per extension, same stem, and return the PNG path.

    Every figure in this package ships a PDF beside its PNG: the PNG is what a
    note or a chat window shows, the PDF is what goes into the paper.
    """
    path = pathlib.Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    for ext in exts:
        fig.savefig(path.with_suffix(f".{ext}"), dpi=dpi)
    return path.with_suffix(f".{exts[0]}")
