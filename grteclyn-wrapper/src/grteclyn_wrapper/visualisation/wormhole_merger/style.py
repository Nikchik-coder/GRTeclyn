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
                still at 4.2:1 against white.  Reading order is the lightness,
                which is what an ordered family should be read by.

WHERE THE INK GOES
------------------
A curve the reader cannot see is worse than no curve, and a key sitting on top
of the data is exactly that.  Nothing in this package calls ``ax.legend`` or
``ax.annotate`` directly any more:

``legend(ax)``  tries each corner, measures what is actually drawn there, and
                takes the emptiest one; if every corner is occupied it opens
                room by extending the axis rather than covering a curve.
``callout()``   a value label placed clear of its own curve -- above a maximum,
                below a minimum -- on an opaque patch.
``note()``      the one-line caption inside a panel, likewise on an opaque
                patch so it never reads as struck through.

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
    "callout", "family", "legend", "note", "ordinal", "ordinal_series",
    "paper", "save", "series",
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
# yellow that a 1-pt line cannot hold on white.  The cut is for LINES, not for
# heatmap cells, so it is set by contrast against the page: at 0.50 the
# lightest step is #7d7c78 at 4.2:1, which reads as a line of its own weight.
# It was 0.62 (3.1:1) and the pale arm came out as a washed-out khaki that
# vanished beside the dark end of the same ramp.
_ORDINAL_CUT = 0.50


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


def ordinal_series(n: int, lw: float = 1.4, dash_offset: int = 0) -> list[dict]:
    """``ordinal`` colours carrying the dash cycle too, so an ordered family is
    still readable in greyscale.

    ``dash_offset`` starts the cycle further along.  Its one use is a figure
    that draws an ordered family *and* a categorical curve on the same axes:
    offsetting by one keeps solid free for the categorical one, so the two
    families cannot be confused for each other.
    """
    dashes = [(0, ()), (0, (6.5, 2.2)), (0, (1.3, 1.7)), (0, (7.0, 2.0, 1.3, 2.0)),
              (0, (3.0, 1.6)), (0, (1.0, 1.4, 4.0, 1.4))]
    return [{"color": c, "linestyle": dashes[(i + dash_offset) % len(dashes)],
             "linewidth": lw}
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


# ---------------------------------------------------------------------------
# Placement.  A figure is only as good as the least legible thing on it, and
# the thing that goes illegible first is a key or a value label dropped on top
# of a curve.  These three helpers make that a measured question rather than a
# guess about where the data will end up.
# ---------------------------------------------------------------------------

_CORNERS = ("upper right", "upper left", "lower right", "lower left")


def _drawn(ax) -> np.ndarray:
    """Every plotted vertex of ``ax``, in axes-fraction coordinates.

    Lines and marker collections only.  Shaded bands are deliberately not
    counted: a band is the ruler the curves are read against, and a key may sit
    on it.
    """
    chunks = []
    for line in ax.lines:
        xy = line.get_xydata()
        if xy is not None and len(xy):
            chunks.append(np.asarray(xy, dtype=float))
    for coll in ax.collections:
        try:
            off = np.asarray(coll.get_offsets(), dtype=float)
        except Exception:      # an image or a quadmesh has no offsets
            continue
        if off.ndim == 2 and len(off):
            chunks.append(off)
    if not chunks:
        return np.empty((0, 2))
    pts = (ax.transData + ax.transAxes.inverted()).transform(np.vstack(chunks))
    return pts[np.isfinite(pts).all(axis=1)]


def _text_boxes(ax) -> list:
    """Boxes, in axes fraction, of the labels already placed inside ``ax``.

    A key that lands on a caption is as unreadable as one that lands on a
    curve, and the caption cannot be moved out of the way by growing the axis
    -- it is anchored to the frame -- so this has to steer the choice of
    corner rather than the growth.
    """
    inv = ax.transAxes.inverted()
    boxes = []
    for txt in ax.texts:
        if not txt.get_visible() or not txt.get_text():
            continue
        try:
            boxes.append(txt.get_window_extent().transformed(inv))
        except Exception:
            continue
    return boxes


def _covered(pts: np.ndarray, box, pad: float) -> int:
    if not len(pts):
        return 0
    return int((
        (pts[:, 0] > box.x0 - pad) & (pts[:, 0] < box.x1 + pad)
        & (pts[:, 1] > box.y0 - pad) & (pts[:, 1] < box.y1 + pad)
    ).sum())


def _make_room(ax, corner: str, box, pad: float, max_grow: float) -> None:
    """Extend the y axis until ``box`` sits over empty page."""
    pts = _drawn(ax)
    if not len(pts):
        return
    pts = pts[(pts[:, 0] > box.x0 - pad) & (pts[:, 0] < box.x1 + pad)]
    if not len(pts):
        return
    lo, hi = ax.get_ylim()
    log = ax.get_yscale() == "log"
    if log:
        if lo <= 0 or hi <= 0:
            return
        lo, hi = np.log10(lo), np.log10(hi)
    span = hi - lo
    if span <= 0:
        return
    if corner.startswith("upper"):
        top = float(pts[:, 1].max())
        edge = box.y0 - pad
        if edge <= 0 or top <= edge:
            return
        hi = lo + min(top / edge, max_grow) * span
    else:
        bot = float(pts[:, 1].min())
        edge = box.y1 + pad
        if edge >= 1 or bot >= edge:
            return
        lo -= min(span * (edge - bot) / (1.0 - edge), (max_grow - 1.0) * span)
    ax.set_ylim(10 ** lo, 10 ** hi) if log else ax.set_ylim(lo, hi)


def legend(ax, *args, loc: str | None = None, pad: float = 0.015,
           grow: bool = True, max_grow: float = 2.4, **kw):
    """A key placed where it covers nothing, and room made for it if need be.

    ``loc`` fixes the corner and only the growth is left to do; without it all
    four corners are tried and the one covering the fewest drawn points wins.
    """
    fig = ax.figure
    best = None
    for corner in ((loc,) if loc else _CORNERS):
        leg = ax.legend(*args, loc=corner, **kw)
        fig.canvas.draw()
        box = leg.get_window_extent().transformed(ax.transAxes.inverted())
        on_data = _covered(_drawn(ax), box, pad)
        on_text = sum(1 for b in _text_boxes(ax) if box.overlaps(b))
        # A curve underneath can be moved out of the way; a caption cannot, so
        # it outweighs any amount of data.
        score = on_data + 1000 * on_text
        if best is None or score < best[0]:
            best = (score, corner, on_data)
        if score == 0:
            break
    _, corner, hit = best
    leg = ax.legend(*args, loc=corner, **kw)
    if grow and hit:
        fig.canvas.draw()
        box = leg.get_window_extent().transformed(ax.transAxes.inverted())
        _make_room(ax, corner, box, pad, max_grow)
        fig.canvas.draw()
    return leg


def _y_fraction(ax, y: float) -> float:
    """Where ``y`` will sit in the frame, allowing for autoscaling still to come.

    Called while a figure is being built, ``get_ylim`` may still hold the
    default 0..1: the real limits are not settled until the draw.  So the
    estimate comes from the data limits and the axes' own margins whenever the
    y axis is still on autoscale.
    """
    log = ax.get_yscale() == "log"
    lo, hi = ax.get_ylim()
    if ax.get_autoscaley_on():
        d0, d1 = ax.dataLim.y0, ax.dataLim.y1
        if np.isfinite(d0) and np.isfinite(d1) and d1 > d0:
            if log and d0 > 0:
                d0, d1 = np.log10(d0), np.log10(d1)
                lo, hi = (np.log10(lo), np.log10(hi)) if lo > 0 else (d0, d1)
            pad = ax.margins()[1] * (d1 - d0)
            lo, hi = d0 - pad, d1 + pad
            return float((np.log10(y) - lo) / (hi - lo)) if log else float((y - lo) / (hi - lo))
    if log:
        if lo <= 0 or hi <= 0 or y <= 0:
            return 0.5
        lo, hi, y = np.log10(lo), np.log10(hi), np.log10(y)
    return float((y - lo) / (hi - lo)) if hi > lo else 0.5


def callout(ax, x: float, y: float, text: str, *, above: bool = True,
            color: str | None = None, dx: float = 0.0, gap: float = 12.0,
            fontsize: float = 8.0, **kw):
    """A value label set clear of its own curve, on an opaque patch.

    ``above`` is the side to put it on: above a maximum, below a minimum, so
    the label leans away from the curve instead of lying across it.  A label
    for a point already at the top of the frame is flipped to the other side
    rather than pushed out of the axes -- put above the highest peak in the
    panel it landed on the panel's own title and printed through it.
    """
    frac = _y_fraction(ax, y)
    if above and frac > 0.87:
        above = False
    elif not above and frac < 0.13:
        above = True
    ax.annotate(
        text, (x, y), xytext=(dx, gap if above else -gap),
        textcoords="offset points", ha="center",
        va="bottom" if above else "top", fontsize=fontsize,
        color=color if color is not None else MUTED, zorder=7,
        bbox=dict(boxstyle="round,pad=0.15", fc=GROUND, ec="none"),
        **kw)


def note(ax, text: str, *, loc: str = "upper left", color: str | None = None,
         fontsize: float = 8.0, **kw):
    """The one-line caption inside a panel, on an opaque patch."""
    x, ha = (0.015, "left") if "left" in loc else (0.985, "right")
    y, va = (0.975, "top") if "upper" in loc else (0.025, "bottom")
    return ax.text(
        x, y, text, transform=ax.transAxes, ha=ha, va=va, fontsize=fontsize,
        color=color if color is not None else MUTED, zorder=7, linespacing=1.45,
        bbox=dict(boxstyle="round,pad=0.25", fc=GROUND, ec="none", alpha=0.85),
        **kw)
