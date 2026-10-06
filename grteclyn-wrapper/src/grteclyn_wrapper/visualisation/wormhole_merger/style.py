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
                a FIXED order -- ink, deep blue, gold, neutral grey -- each
                with its own dash.  There is no fifth: a fifth series means the
                family is ordered (use ``ordinal``) or the figure is doing two
                jobs.  The four were checked, not eyeballed: worst pair 17.2
                OKLab dE under normal vision and 12.7 under simulated
                protanopia (Vienot-Brettel-Mollon), against thresholds of 15
                and 8.  The accent was a burgundy #9b2226 until 2026-09-19:
                21.7 on the first number and only 10.6 on the second, and in
                greyscale it landed at L* 34 -- on top of MUTED (39) and
                DEEP_BLUE (32), an accent with the tone of the context it was
                meant to stand out from.  Gold inverts that: at L* 64 it is
                the LIGHTEST line on the page, and CONTEXT was darkened to
                keep it so.  Gold is also where the yellow stops: it holds
                2.8:1 against white at 1.9 pt, and #e6b800 -- the yellow that
                actually looks like yellow -- holds 1.9:1 and comes out
                lighter in greyscale than the context line it outranks.

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

import io
import pathlib
import re

import matplotlib
import matplotlib.transforms
import numpy as np
from matplotlib.legend import Legend

__all__ = [
    "CONTEXT", "DEEP_BLUE", "DEEP_GREEN", "DIVERGING", "FAINT", "GRID", "GOLD", "GROUND", "INK",
    "KEY_TOP", "MUTED", "SEQUENTIAL", "SEQUENTIAL_HOT", "SIGNED", "signed",
    "callout", "edge_label", "family", "legend", "legend_top", "note", "ordinal",
    "ordinal_series", "paper", "prd", "save", "series", "tag_keys", "typography",
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
GOLD = "#c69214"
# A fourth accent for the page that genuinely has four entities (the censorship
# page's four fates).  Referenced by signed() since its birth but never defined
# -- a latent NameError until 2026-09-21.  Deep and warm-leaning: at L* ~ 46 it
# sits between DEEP_BLUE (33) and GOLD (64) in tone, so the greyscale channel
# keeps all three apart, and the hue is far from both under the red-weak
# confusions that matter here (green vs the warm gold separates on lightness).
DEEP_GREEN = "#3e7a49"
# CONTEXT is NEUTRAL and a shade darker than MUTED's warm grey, and both
# departures are deliberate: it is the only grey that carries DATA, so it is
# the only one that can be mistaken for the accent.  A gold accent is LIGHT
# (L* 64), so the context line has to be the dark one -- at the old warm
# #8f8b81 (L* 58) the two were six points apart in tone and the greyscale
# channel was gone.  #7e838a is L* 55, nine points clear, and the darkening
# stops there: #6f737a would open the gap to sixteen but collapses against
# DEEP_BLUE for a red-weak reader (7.6 OKLab dE, and 4.3 under deuteranopia).
# MUTED and FAINT label and recede, never plot, so they keep the warm cast the
# body text is set in.
CONTEXT = "#7e838a"

# Fixed order, never cycled.  (colour, dash, linewidth) -- the dash is the
# primary channel, so the order is chosen to keep adjacent series apart in
# pattern as well as in hue.
_SERIES = (
    (INK, (0, ()), 1.4),
    (DEEP_BLUE, (0, (6.5, 2.2)), 1.5),
    (GOLD, (0, (1.3, 1.7)), 1.7),
    (CONTEXT, (0, (7.0, 2.0, 1.3, 2.0)), 1.5),
)

# The SIGN of a declared kick is the thing the eye must read first on the seed
# scan, so it takes the two poles of the campaign's own palette -- deep blue for
# a negative kick, gold for a positive one -- and the shade tracks the
# amplitude.  Same-magnitude pairs, which are the comparison the figure exists
# to make, separate by 27 / 36 / 21 OKLab dE from the 0.1 rung to the 0.001 one
# under normal vision and 25 / 35 / 13 under simulated protanopia -- gold
# against blue is the widest pairing any accent tried has given.  The pale rung
# is the weak one, here as in every family: a pale gold against a pale blue is
# two light tints, which is why the seed panel carries the amplitude in
# LINEWIDTH as well and never in shade alone.
SIGNED = {
    "-0.1": "#0f3355", "-0.01": DEEP_BLUE, "-0.001": "#6a93bd",
    "+0.001": "#d5b374", "+0.01": GOLD, "+0.1": "#8b5c00",
}


def signed(label: str) -> str:
    """The colour for a kick written as a signed decimal, e.g. ``"+0.01"``."""
    if label in SIGNED:
        return SIGNED[label]
    # An amplitude the table does not name: fall back to the pole of its sign.
    return DEEP_GREEN if label.lstrip().startswith("+") else DEEP_BLUE

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


def prd(base: float = 10.0) -> None:
    """``paper`` plus the REVTeX frame the user asked for on the seed-branches
    figure (2026-09-16, "PRD review style"), adopted for every article figure:
    full box, inward major+minor ticks on all four sides, ink ticks, no grid.
    Keys go INSIDE the axes, on an opaque patch, placed by ``legend``."""
    paper(base)
    matplotlib.rcParams.update({
        "axes.spines.top": True, "axes.spines.right": True,
        "axes.edgecolor": INK, "axes.linewidth": 0.8,
        "axes.grid": False,
        "xtick.direction": "in", "ytick.direction": "in",
        "xtick.top": True, "ytick.right": True,
        "xtick.color": INK, "ytick.color": INK,
        "xtick.labelcolor": INK, "ytick.labelcolor": INK,
        "xtick.minor.visible": True, "ytick.minor.visible": True,
        "xtick.major.size": 3.4, "ytick.major.size": 3.4,
        "xtick.minor.size": 1.9, "ytick.minor.size": 1.9,
    })


def typography(base: float = 10.0) -> None:
    """The journal faces of ``paper`` WITHOUT its frame and palette.

    ``paper`` does three things at once: it sets the STIX faces, it recedes the
    frame to near-invisible, and it hands out the categorical dash palette.  The
    first is wanted everywhere; the other two are not.  A six-member ORDERED
    family on a log axis drawn in the categorical dashes comes out as grey
    dashes a reader cannot separate, and the receded frame washes out a figure
    whose subject is a single bright curve.  So a module that brings its own
    ink calls this and keeps the typography only.
    """
    matplotlib.rcParams.update({
        "font.family": "serif",
        "font.serif": ["STIXGeneral", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": base,
        "axes.titlesize": base * 1.05,
        "axes.labelsize": base * 1.05,
        "xtick.labelsize": base * 0.9,
        "ytick.labelsize": base * 0.9,
        "legend.fontsize": base * 0.9,
        "figure.facecolor": GROUND,
        "axes.facecolor": GROUND,
        "savefig.facecolor": GROUND,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.axisbelow": True,
        "legend.frameon": False,
        "lines.solid_capstyle": "round",
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

    A figure that has not changed is not rewritten (2026-09-25).  Every repack
    used to redraw pixel-identical figures whose bytes differ only in the PDF's
    creation date and the matplotlib version both formats stamp in, and each
    one showed up in git as a change.  The PNG decides: if it renders to the
    pixels already on disk, none of the files is touched.
    """
    path = pathlib.Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = {}
    for ext in exts:
        buf = io.BytesIO()
        fig.savefig(buf, format=ext, dpi=dpi)
        rendered[ext] = buf.getvalue()
    if not _unchanged(path, rendered):
        for ext, data in rendered.items():
            path.with_suffix(f".{ext}").write_bytes(data)
    return path.with_suffix(f".{exts[0]}")


# The PDF's creation date and producer (which carries the matplotlib version).
_PDF_STAMPS = re.compile(rb"/(?:CreationDate|ModDate|Producer) \([^)]*\)")


def _unchanged(path: pathlib.Path, rendered: dict[str, bytes]) -> bool:
    """True if every file already exists and shows what ``rendered`` shows:
    same PNG pixels when a PNG is among them, else the same bytes once the
    PDF's date and version stamps are set aside."""
    targets = {ext: path.with_suffix(f".{ext}") for ext in rendered}
    if not all(t.is_file() for t in targets.values()):
        return False
    if "png" in rendered:
        from PIL import Image

        try:
            old = np.asarray(Image.open(targets["png"]))
        except OSError:
            return False
        new = np.asarray(Image.open(io.BytesIO(rendered["png"])))
        return old.shape == new.shape and np.array_equal(old, new)
    return all(
        _PDF_STAMPS.sub(b"", targets[ext].read_bytes()) == _PDF_STAMPS.sub(b"", data)
        for ext, data in rendered.items()
    )


# ---------------------------------------------------------------------------
# Placement.  A figure is only as good as the least legible thing on it, and
# the thing that goes illegible first is a key or a value label dropped on top
# of a curve.  These three helpers make that a measured question rather than a
# guess about where the data will end up.
# ---------------------------------------------------------------------------

_CORNERS = ("upper right", "upper left", "lower right", "lower left")


def label_audit(fig, pad: float = 0.004, px_step: float = 3.0) -> list[str]:
    """Every text box a drawn line passes through, named (2026-09-24, on the
    user's mark: 'there should be some instruments in the repo to check
    whether text crosses the lines').

    Unlike ``_drawn`` this walks each line in ITS OWN transform -- an axvline
    is blended (data x, axes y) and would land in the wrong place through
    ``transData`` -- and densifies every segment to ``px_step`` pixels, so a
    text sitting mid-height on a vline is caught even though the vline has
    only two vertices.  Call it after layout, before ``save``; a clean figure
    returns [].  Letter tags above the frames sit outside the axes box and are
    never crossed by clipped curves, so hits on them are real.
    """
    fig.canvas.draw()
    reports: list[str] = []
    for k, ax in enumerate(fig.axes):
        inv = ax.transAxes.inverted()
        pts = _line_points(ax, px_step)
        if not len(pts):
            continue
        for txt in ax.texts:
            if not txt.get_visible() or not txt.get_text():
                continue
            try:
                box = txt.get_window_extent().transformed(inv)
            except Exception:
                continue
            n = _covered(pts, box, pad)
            if n:
                head = txt.get_text().splitlines()[0][:48]
                reports.append(
                    f"[label-audit] axes {k} ({ax.get_ylabel() or 'unnamed'}): "
                    f"{n} samples cross '{head}'")
        # Text on text, and text on the key (2026-09-25: a corner note printed
        # over a legend entry, which the line walk above cannot see).
        named = [(t.get_text().splitlines()[0][:32], t.get_window_extent().transformed(inv))
                 for t in ax.texts if t.get_visible() and t.get_text()]
        if ax.get_legend() is not None:
            named.append(("the key", ax.get_legend().get_window_extent().transformed(inv)))
        for i, (a, ba) in enumerate(named):
            for b, bb in named[i + 1:]:
                if ba.overlaps(bb):
                    reports.append(f"[label-audit] axes {k} ({ax.get_ylabel() or 'unnamed'}): "
                                   f"'{a}' overlaps '{b}'")
    # Entries INSIDE a key (2026-09-26).  An expand-mode key too narrow for its
    # entries packs them with negative spacing -- one entry's text printed over
    # the next column's handle -- or lets a long entry run past the frame it
    # spans, while the key's outer box, all the checks above can see, stays clean.
    for k, ax in enumerate(fig.axes):
        if ax.get_legend() is not None:
            for p in _key_problems(ax.get_legend()):
                reports.append(f"[label-audit] axes {k} ({ax.get_ylabel() or 'unnamed'}): key {p}")
    for leg in fig.legends:
        for p in _key_problems(leg):
            reports.append(f"[label-audit] figure key: {p}")
    for r in reports:
        print(r)
    return reports


def _key_problems(leg) -> list[str]:
    """A key's entries (handle + text) that touch each other, or run past the
    key's own box (an expand-mode key's box is the frame it spans)."""
    renderer = leg.get_figure(root=True).canvas.get_renderer()
    edge = leg.get_window_extent(renderer)
    boxes = []
    for handle, text in zip(leg.legend_handles, leg.get_texts()):
        if not text.get_visible() or not text.get_text():
            continue
        box = text.get_window_extent(renderer)
        try:
            box = matplotlib.transforms.Bbox.union([box, handle.get_window_extent(renderer)])
        except Exception:      # a handle without an extent: the text alone
            pass
        boxes.append((text.get_text()[:32], box))
    out = [f"entries '{a}' and '{b}' touch" for i, (a, ba) in enumerate(boxes)
           for b, bb in boxes[i + 1:] if ba.overlaps(bb)]
    out += [f"entry '{a}' runs past the key's edge" for a, b in boxes
            if b.x0 < edge.x0 - 0.5 or b.x1 > edge.x1 + 0.5]
    return out


def _line_points(ax, px_step: float = 3.0) -> np.ndarray:
    """Every drawn line of ``ax``, densified to ``px_step`` pixels, and every
    marker offset, in axes fraction -- each walked in ITS OWN transform (the
    geometry ``label_audit`` judges by)."""
    chunks = []
    for line in ax.lines:
        xy = line.get_xydata()
        if xy is None or len(xy) < 2 or not line.get_visible():
            continue
        disp = line.get_transform().transform(np.asarray(xy, dtype=float))
        disp = disp[np.isfinite(disp).all(axis=1)]
        for a, b in zip(disp[:-1], disp[1:]):
            n = max(2, int(np.hypot(*(b - a)) / px_step))
            chunks.append(np.linspace(a, b, n))
    for coll in ax.collections:
        try:
            off = np.asarray(coll.get_offsets(), dtype=float)
        except Exception:
            continue
        if off.ndim == 2 and len(off):
            chunks.append(coll.get_offset_transform().transform(off))
    if not chunks:
        return np.empty((0, 2))
    pts = ax.transAxes.inverted().transform(np.vstack(chunks))
    return pts[np.isfinite(pts).all(axis=1)]


def declutter(fig, pad: float = 0.004, max_shift: float = 12.0, step: float = 1.5,
              px_step: float = 3.0) -> list[str]:
    """Move each label ``label_audit`` would report the shortest way off its
    line, or off another label or the key (2026-09-25, on the user's word: the vis package has the tools, use
    them instead of hand-nudging).

    Candidates are shifts of up to ``max_shift`` points, nearest first; the
    first one that leaves the label crossed by no line, clear of every other
    label and of the key, and inside its frame is kept.  A label nothing within
    reach clears stays where it was, for the audit that follows to name.  Call
    after layout and before ``label_audit``; returns what it moved.
    """
    import matplotlib.text as mtext
    from matplotlib.transforms import ScaledTranslation

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    r = np.arange(step, max_shift + 1e-9, step)
    ang = np.deg2rad(np.arange(0.0, 360.0, 22.5))
    cand = sorted({(round(float(a * np.cos(t)), 2), round(float(a * np.sin(t)), 2))
                   for a in r for t in ang}, key=lambda d: (np.hypot(*d), -d[1]))
    moved: list[str] = []
    for ax in fig.axes:
        pts = _line_points(ax, px_step)
        if not len(pts):
            continue
        inv = ax.transAxes.inverted()

        def box_of(artist):
            return artist.get_window_extent(renderer).transformed(inv)

        for txt in list(ax.texts):
            if not txt.get_visible() or not txt.get_text():
                continue
            others = [box_of(t) for t in ax.texts
                      if t is not txt and t.get_visible() and t.get_text()]
            if ax.get_legend() is not None:
                others.append(box_of(ax.get_legend()))
            here = box_of(txt)
            if not _covered(pts, here, pad) and not any(here.overlaps(o) for o in others):
                continue
            if isinstance(txt, mtext.Annotation) and txt.anncoords == "offset points":
                x0, y0 = txt.xyann

                def shift(dx, dy, txt=txt, x0=x0, y0=y0):
                    txt.xyann = (x0 + dx, y0 + dy)
            else:
                base = txt.get_transform()

                def shift(dx, dy, txt=txt, base=base):
                    txt.set_transform(base + ScaledTranslation(dx / 72.0, dy / 72.0,
                                                               fig.dpi_scale_trans))
            for dx, dy in cand:
                shift(dx, dy)
                b = box_of(txt)
                if (not _covered(pts, b, pad) and not any(b.overlaps(o) for o in others)
                        and b.x0 >= 0.0 and b.x1 <= 1.0 and b.y0 >= 0.0 and b.y1 <= 1.0):
                    moved.append(f"[declutter] '{txt.get_text().splitlines()[0][:32]}' "
                                 f"moved ({dx:+.1f}, {dy:+.1f}) pt")
                    break
            else:
                shift(0.0, 0.0)
    for m in moved:
        print(m)
    return moved


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


# ---------------------------------------------------------------------------
# Keys on top (the user's standing rule, 2026-09-26: a key ABOVE every panel
# names each of its lines, and nothing but tiny tags sits inside a frame).
# ---------------------------------------------------------------------------

KEY_TOP = dict(loc="lower left", bbox_to_anchor=(0.0, 1.02, 1.0, 0.1), mode="expand",
               frameon=False, fontsize=6.5, labelcolor=INK, borderaxespad=0.0,
               borderpad=0.2, handlelength=2.0, handletextpad=0.5, columnspacing=1.0,
               labelspacing=0.3)


class _TopKey(Legend):
    """A mode="expand" key that takes its width from its axes whenever it is
    MEASURED, not only when drawn.  Matplotlib sets an expanding key's width in
    ``draw``, and constrained layout measures between draws: after a 300-dpi
    PNG, the PDF's 72-dpi layout saw a full-width key four times too wide and
    gave up ("axes sizes collapsed to zero"), so the PDF silently kept the
    PNG's layout (2026-09-26, the L512 inflation page)."""

    def get_window_extent(self, renderer=None):
        if renderer is None:
            renderer = self.get_figure(root=True)._get_renderer()
        if self._mode == "expand":
            pad = 2 * (self.borderaxespad + self.borderpad) * renderer.points_to_pixels(
                self.prop.get_size_in_points())
            self._legend_box.set_width(self.get_bbox_to_anchor().width - pad)
        return super().get_window_extent(renderer)

    get_tightbbox = get_window_extent


def legend_top(ax, entries, ncol: int = 1, **kw):
    """The panel's key ABOVE its frame, spanning its width, naming every line.

    ``entries`` is [(handle, label)], read ROW BY ROW (matplotlib fills a key
    column by column; the order is rearranged for it).  ``ncol`` sets the
    columns: choose it so every entry fits -- ``label_audit`` names entries
    that touch.  ``kw`` overrides ``KEY_TOP``.  Constrained layout makes room
    for the key; put the letter tags on afterwards with ``tag_keys``.
    """
    n = len(entries)
    nrow = -(-n // ncol)
    order = [entries[r * ncol + c] for c in range(ncol) for r in range(nrow)
             if r * ncol + c < n]
    opts = dict(KEY_TOP)
    opts.update(kw)
    ax.legend_ = _TopKey(ax, [h for h, _ in order], [s for _, s in order], ncol=ncol, **opts)
    return ax.legend_


def tag_keys(fig, axes, tags, *, row: str = "first", fontsize: float = 9.0,
             gap: float = 4.0) -> list:
    """Letter tags at the left end of each panel's key, just left of the frame
    and centred on the key's first row (its title, if it has one) -- or on its
    last row, ``row="last"``, which keeps the tags of a row of panels level
    when their keys differ in height; above the frame's corner for a panel
    without a key.  Call after every key is placed: it draws the figure once
    to measure them, and the offsets are in points from the key's own anchor,
    so the tags hold whatever size the layout later gives the axes."""
    fig.canvas.draw()
    out = []
    for ax, tag in zip(axes, tags):
        leg = ax.get_legend()
        if leg is None or not leg.get_texts():
            out.append(ax.text(0.0, 1.03, tag, transform=ax.transAxes, ha="left",
                               va="bottom", fontsize=fontsize, color=INK))
            continue
        y_anchor = ax.transAxes.inverted().transform(
            (0.0, leg.get_bbox_to_anchor().y0))[1]
        if row == "first":
            box = (leg.get_title() if leg.get_title().get_text()
                   else leg.get_texts()[0]).get_window_extent()
            yc = 0.5 * (box.y0 + box.y1)
        else:
            yc = min(0.5 * (b.y0 + b.y1) for b in
                     (t.get_window_extent() for t in leg.get_texts()))
        dy = (yc - ax.transAxes.transform((0.0, y_anchor))[1]) * 72.0 / fig.dpi
        out.append(ax.annotate(tag, (0.0, y_anchor), xycoords="axes fraction",
                               xytext=(-gap, dy), textcoords="offset points", ha="right",
                               va="center", fontsize=fontsize, color=INK))
    return out


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


def edge_label(ax, y: float, text: str, *, color: str | None = None,
               fontsize: float = 8.0, pad: float = 4.0, **kw):
    """A name at the right edge of the frame, level with ``y``, inset in POINTS.

    For the rule a panel is read against (``R_star``) and for a curve named
    in the margin past its own end.  The x anchor is the spine itself, so
    the text can never straddle it however narrow the panel gets -- which
    is what a fraction of the axis could not promise: ``0.985`` left the
    ``R_star`` subscript a comfortable 3 pt clear on a single column and
    printed it through the spine on a quarter-page panel (2026-09-18, the
    article's combined strips).
    """
    trans = matplotlib.transforms.blended_transform_factory(
        ax.transAxes, ax.transData)
    return ax.annotate(
        text, (1.0, y), xycoords=trans, xytext=(-pad, 1.5),
        textcoords="offset points", ha="right", va="bottom",
        fontsize=fontsize, color=color if color is not None else MUTED, **kw)


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
