#!/usr/bin/env python3
r"""Upload-ready 1080p videos of the wormhole-merger campaign.

The campaign's movies are one field per file, 628x538, 10 fps, drawn for
reading a diagnostic -- not for watching.  This builds the watchable version:
the fields that carry each encounter, side by side and in sync, on one 1920x1080
canvas with a header, per-panel labels, a caption saying what is happening, and
an ownership mark inside the plot area of every panel (cropping one away crops
the data with it).

    python -m grteclyn_wrapper.visualisation.wormhole_merger.make_youtube
    python -m grteclyn_wrapper.visualisation.wormhole_merger.make_youtube --only headon

It is the merger campaign's counterpart to ``scripts/plot/youtube_sidebyside.sh``
(the Bondi set), and deliberately NOT a copy of it: that one pairs matter
against geometry for a single physical story, while this one carries five
different encounters whose readable fields differ, so the panel list is per
campaign and lives in ``PANELS`` below.

PLAYBACK IS 1x.  The Bondi videos run at 2x and say so on every frame, because
their frames are one per plotfile over a long quiet record.  These records are
100 units in 101 frames and the interesting part -- contact, merger, ringdown --
takes ten of them, so at 2x the merger is over in a second.  ``--speed`` is
there if a particular upload wants it, and the on-frame note follows it
automatically, but the default is real time.  "Real time" means one code unit
per frame at 10 fps; an entry whose frames are further apart says so with
``dt_frame`` and its note follows (F4's inflation record: frames 2 units apart,
t = 0-218 in 11 s, "2x speed").

WHICH FIELDS, AND WHY THOSE.  Chosen for what reads on screen at a glance,
which is not the same as what the paper measures from:

* chi, the conformal factor -- where the throats ARE.  Dark pits that move,
  merge, and either deepen (collapse) or fill in (inflation).  It is the one
  field a viewer can follow without being told what to look at.
* lapse -- where the geometry is collapsing.  It goes to zero over a forming
  horizon, so on the head-on it does the thing the paper's whole Sec. VII is
  about, visibly.  It also falls on the inflating throat, where 1+log freezes
  the clock at the neck with no horizon, and that video's caption says so.
* phi, the phantom scalar -- the inflating throat's field.  Its dark core
  widens from t = 0, where chi on its fixed scale stays black until t ~ 80.
* K, the trace of the extrinsic curvature -- the fly-by's field, because its
  mouths EXPAND and K shows the expansion where chi's pits only get shallower.
* |Psi_4| and Re(Psi_4) -- the radiation.  Only on the arms whose burst is the
  point: the spiral, the one encounter that merges without ever making a
  horizon, and the vacuum controls, where the wave is textbook and the
  comparison IS the result.

A CAVEAT THAT HAS TO TRAVEL ON THE FRAME, not only in a description a viewer
may not open: past t = 59.94 the spiral is the frozen-core arm, so its dark
centre stops evolving BY CONSTRUCTION.  ``caption2`` says so for that video.
The same goes for the late grid-scale speckle documented in the movies README --
the last third of any Weyl panel is below the campaign's own noise floor, and
the caption says to read it as noise rather than structure.

Sources are the curated masters in ``results/merger/movies/<group>/<run>/``,
never a run's scratch copy, so what is published is what is filed.

OUTPUT NAMES SAY WHAT HAPPENS, not which run produced it.  The movie tree keeps
run names so a file can be traced to its registry line; these are for a viewer
choosing what to watch, so they are numbered in viewing order -- one throat,
then two, then the vacuum controls -- and named for the physics.  The run each
came from is the key in ``PANELS`` and is recorded in the folder's README.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# --------------------------------------------------------------------------
# Canvas.  1920x1080 with a dark ground that matches the movies' own figure
# background, so the margins a 2x2 grid leaves read as deliberate rather than
# as letterboxing.
GROUND = "0x0E1216"
# Panels are padded to their common box with the frames' own white, so a 2x2
# grid is one clean rectangle.  Padding with GROUND left dark notches wherever
# two frames differed in width (the colourbar label sets it) -- the ragged
# corners the user flagged on 2026-10-05.
PANEL_BG = "0xFFFFFF"
W_OUT, H_OUT = 1920, 1080
HEAD_H = 118          # header band of a one-row layout: title + speed note + panel labels
HEAD_H_GRID = 84      # a 2x2 grid's header holds the title only; everything else is in the side column
MARGIN = 40           # left/right text margin, and the gutter the captions wrap in
SIDE_GAP = 36         # gap between the 2x2 grid and the side column
# A 2x2 grid sits at the LEFT edge, as tall as the canvas allows, and every word
# of text except the title goes in a column to its right: the panel key, the
# captions, the sponsor and the credit (the user's design, 2026-10-05).  Under
# the grid, the captions ran as two full-width lines a viewer could not read in
# one pass, and they cost the panels 130 px of height.
GRID_X0 = 24          # left margin of a 2x2 grid
GRID_PAD_B = 20       # space under a 2x2 grid
SIDE_MIN_W = 600      # the side column is never narrower than this
SIDE_PAD_R = 28       # right margin of the side column

# Caption typography.  ffmpeg's drawtext does NOT wrap, so a caption longer than
# the canvas is silently cut off at BOTH ends (it centres, then overflows) and
# anything drawn under it is pushed off the frame entirely.  That is what the
# spiral's first build did: its 230-character opening line ran off each side and
# its second line vanished.  So captions are wrapped here, and the footer's
# height is computed from how many lines they actually take.
CAP1_SIZE, CAP2_SIZE, CREDIT_SIZE = 20, 18, 16
CAP1_LEAD, CAP2_LEAD = 26, 24
# The side column's sizes: captions larger than the footer's (the lines are
# short now, so they can be), the panel key small -- it names the panels, it is
# not the thing to read.
SIDE_CAP1, SIDE_CAP2, SIDE_CREDIT = 23, 20, 15
SIDE_LEAD1, SIDE_LEAD2, SIDE_LEAD_CREDIT = 31, 27, 20
KEY_ROLE, KEY_NAME, KEY_CELL_H = 15, 17, 60
# DejaVu Sans averages ~0.55 em per character over mixed-case prose; that is an
# estimate, so the usable width is taken conservatively.
_EM = 0.55

# EVERY drawtext carries expansion=none.  drawtext expands %{...} in its text by
# default, and it does that to a textfile too, so a caption containing a bare
# per-cent sign -- "certified ... to 0.1%" -- silently drops the WHOLE line
# rather than failing.  The spiral's second caption line vanished that way and
# the build reported success (2026-09-21).  These captions are literal prose;
# nothing in them is ever a format string.

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Branding (the user's word, 2026-10-05).  The CHANNEL is First Interstellar
# Institute: its mark "FII" is printed inside every panel's plot area, so it
# cannot be cropped away without cropping the data; the channel's name is not
# spelled out on the frame (it is where the video is published).  Gravity
# Frontiers is the research SPONSOR, named in full beside the 2x2 grid
# (BRAND_RIGHT) and in the credit line.
MARK = "FII"
BRAND_RIGHT = ("Research sponsored by", "GRAVITY FRONTIERS")
CREDIT = ("First Interstellar Institute  ·  research sponsored by Gravity Frontiers  ·  "
          "GRTeclyn  ·  3+1 numerical relativity on GPUs")
CREDIT_SEP = "  ·  "

# Per-panel label colours: one hue per physical role, kept across every video so
# a viewer who watches two of them learns the code once.
ROLE = {
    "chi":        ("GEOMETRY  ·  conformal factor χ", "0x8FB8E8"),
    "phi":        ("MATTER  ·  phantom scalar φ", "0xE58C8C"),
    "Pi":         ("MATTER  ·  scalar momentum Π", "0xEBA07E"),
    "lapse":      ("GAUGE  ·  lapse α", "0x7FD4A8"),
    "K":          ("CURVATURE  ·  trace K", "0xE0A3D6"),
    "Weyl4_Mag":  ("RADIATION  ·  |Ψ₄|", "0xE8B44A"),
    "Weyl4_Re":   ("RADIATION  ·  Re(Ψ₄)", "0xD08A5A"),
}

# --------------------------------------------------------------------------
# What to build.  The panel list per campaign is the user's choice of what reads
# well; the layout code handles 2 or 4, and every entry currently takes 4.  The
# single throat gets exactly two videos, the two FATES -- the other seed arms
# look almost identical on screen and add nothing for a viewer.  Captions are
# the paper's own numbers: nothing is rounded further than the article rounds
# it, and nothing is claimed that the article does not.
PANELS: dict[str, dict] = {
    "01_single_throat/single_eps_m1e2_L512_ml5_oct_t400": dict(
        out="01_wormhole_throat_inflates.mp4",
        fields=["K", "lapse", "chi", "phi"],
        sub="youtube",
        dt_frame=2.0,
        title="A lone wormhole throat inflates  \u2014  declared kick \u03b5 = \u22120.01",
        cap1="One drainhole throat, given a small inward kick. It does not collapse: it "
             "keeps opening, 3.8\u00d7 in areal radius by t = 218, and no trapped surface forms.",
        cap2="Until t \u2248 40 it grows at the Shinkai\u2013Hayward rate. Then the lapse (top right) "
             "freezes the clock at the throat, and its growth per unit t slows: the slicing, "
             "not the throat.",
    ),
    "01_single_throat/single_pureq_q1e2_ml4_t100": dict(
        out="02_wormhole_throat_collapses.mp4",
        fields=["K", "lapse", "chi", "Pi"],
        t_end=60.0,
        title="The same throat collapses  \u2014  a quadrupole seed",
        cap1="The mirror of the inflating run: the same throat, given a quadrupole instead "
             "of an inward kick. It closes, and a horizon forms at t = 33.",
        cap2="A wormhole throat is an unstable fixed point. Which way it falls is set by "
             "the perturbation it is given \u2014 and a quadrupole, unlike a spherical kick, "
             "also leaves it something to radiate.",
    ),
    "04_binary_headon/headon_csm_L128_stitched_t0_t100": dict(
        out="03_headon_collision_makes_black_hole.mp4",
        fields=["K", "lapse", "chi", "Weyl4_Re"],
        sub="youtube_zoom2",
        title="Two wormholes collide head-on  \u2014  and make a black hole",
        cap1="Released from rest at separation 8, on constraint-solved initial data. They "
             "touch while both mouths are still open wormholes, and one trapped surface "
             "closes over BOTH at t = 18 (R = 5.63).",
        cap2="Neither mouth ever has a horizon of its own \u2014 it is born common or not at "
             "all. The remnant then LOSES mass to the phantom field it swallows, 2.82 "
             "\u2192 2.39 by t = 100 (the 3D horizon finder's full history).",
    ),
    "05_binary_spiral/spiral_d6_p010_L128_csm_stitched_t0_t100": dict(
        out="04_spiral_merger_makes_black_hole.mp4",
        fields=["K", "lapse", "chi", "Weyl4_Re"],
        sub="youtube_zoom2",
        title="Two wormholes spiral in and merge  \u2014  and a horizon forms",
        cap1="Separation 6, tangential momentum 0.10, constraint-solved data. The pair "
             "merges in half an orbit, and a common trapped surface closes over both "
             "mouths at t = 13 (R = 5.60): the orbital merger makes a black hole.",
        cap2="The remnant settles to R = 4.88, losing mass to the phantom it swallows "
             "(2.80 \u2192 2.44 by t = 100). One chain of certified restarts through two "
             "numerical walls; the seams sit at t = 25, 30 and 35.",
    ),
    "06_binary_flyby/merge_orbit_flip_d12_p025_L128_lvl5_t100_lbf_csm": dict(
        out="05_wormhole_flyby_no_merger_mouths_inflate.mp4",
        fields=["K", "lapse", "chi", "Weyl4_Re"],
        sub="youtube_zoom2",
        title="A wormhole fly-by  \u2014  no merger, and both mouths inflate",
        cap1="Separation 12, momentum 0.25 per mouth, constraint-solved boosted data. The "
             "pair swings past (closest approach 2.33 at t \u2248 47) and separates \u2014 nothing "
             "merges, no horizon ever \u2014 and both mouths INFLATE as it goes.",
        cap2="In vacuum, black holes with even more momentum just coast apart (video 09): "
             "the phantom field's pull is what drags this pair in, and the pass radiates a "
             "phantom-scalar burst a vacuum binary has no analogue for.",
    ),
    "06_binary_flyby/merge_orbit_flip_d12_p060_L128_csm_stitched_t0_t80": dict(
        out="06_plunge_merger_no_horizon_yet.mp4",
        fields=["K", "lapse", "chi", "Weyl4_Re"],
        title="A deeper plunge  \u2014  the mouths merge, and the horizon stalls",
        cap1="The fly-by's momentum raised to 0.60: the pair now PLUNGES \u2014 separation "
             "3.5 \u2192 0 over t = 36\u201340 \u2014 and merges as wormholes. This is the campaign's "
             "loudest gravitational-wave source.",
        cap2="No trapped surface converges by t = 100: the finder's surface stays "
             "marginally untrapped, a pinched peanut rounding toward closure at t \u2248 "
             "110\u2013115. A finer grid agrees \u2014 the stall is physics, not resolution.",
    ),
    "06_binary_flyby/merge_orbit_flip_d12_p090_L128_csm_stitched_t0_t45": dict(
        out="07_hardest_plunge_mouths_inflate.mp4",
        fields=["K", "lapse", "chi", "Weyl4_Re"],
        sub="youtube_zoom2",
        title="The hardest plunge  \u2014  the mouths inflate as they merge",
        cap1="Momentum 0.90 per mouth: the pair falls from separation 11.8 to 2.6 in forty "
             "units. On the approach both mouths visibly INFLATE, and the merging core "
             "starts to inflate too.",
        cap2="No horizon is found at any time. The record ends at t = 45.3, where this "
             "simulation stops: the inflating core outruns the grid's resolution.",
    ),
    "07_bbh_control/bbh_control_d12_p012_t150": dict(
        out="08_control_two_black_holes_merge.mp4",
        fields=["Weyl4_Mag", "lapse", "chi", "Weyl4_Re"],
        title="Control  \u2014  two black holes, same separation and momentum, no scalar",
        cap1="The vacuum comparison: the d = 12 spiral's separation and momentum, with "
             "the ghost scalar removed. Two black holes merge and ring down.",
        cap2="This is what a textbook merger looks like on the same grid \u2014 the chirp the "
             "wormhole channels never produce.",
    ),
    "07_bbh_control/bbh_headon_d8_L128_lvl5_t100": dict(
        out="10_control_two_black_holes_collide_headon.mp4",
        fields=["K", "lapse", "chi", "Weyl4_Re"],
        sub="youtube",
        dt_frame=0.5,
        title="Control  —  the head-on collision in vacuum",
        cap1="The wormhole head-on's vacuum twin: two bare black holes of the same mass "
             "released from rest at the same separation, on the same grid. They fall "
             "together, merge, and ring down.",
        cap2="Watch it beside the wormhole head-on (video 03): there the horizon closes "
             "over two still-open wormholes and the remnant then LOSES mass to the "
             "phantom field it swallows — a vacuum remnant can only grow.",
    ),
    "07_bbh_control/bbh_control_d12_p045_t100": dict(
        out="09_control_two_black_holes_fly_apart.mp4",
        fields=["Weyl4_Mag", "lapse", "chi", "Weyl4_Re"],
        title="Control  \u2014  the fly-by's own momentum, in vacuum",
        cap1="Two black holes at the fly-bys' separation, 12, with momentum 0.45 each and "
             "no scalar field. In vacuum that momentum is unbound: they start at closest "
             "approach and coast apart, 12 \u2192 21.",
        cap2="Watch it beside the wormhole fly-by (video 05): with the phantom field the "
             "pull is several times stronger, so even at momentum 0.25 the pair falls in "
             "to 2.33, and the mouths inflate as they pass.",
    ),
}


def _probe_size(path: Path) -> tuple[int, int]:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True)
    w, h = r.stdout.strip().split(",")[:2]
    return int(w), int(h)


def _wrap(text: str, fontsize: int, width: int = W_OUT - 2 * MARGIN,
          font: str = FONT, sep: str = " ") -> list[str]:
    """Greedy wrap to ``width`` pixels, since drawtext will not do it.

    Measured with the font itself when Pillow is there (it is, in the wrapper's
    venv: matplotlib needs it); the per-character estimate is the fallback.
    ``sep`` is what a line may break at -- the credit breaks only between its
    segments, so no line starts with a dot.
    """
    try:
        from PIL import ImageFont
        face = ImageFont.truetype(font, fontsize)
        fits = lambda line: face.getlength(line) <= width
    except (ImportError, OSError):
        budget = max(int(width / (_EM * fontsize)), 20)
        fits = lambda line: len(line) <= budget
    words, lines, cur = text.split() if sep == " " else text.split(sep), [], ""
    for w in words:
        trial = f"{cur}{sep}{w}" if cur else w
        if fits(trial) or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _footer_height(cap1: list[str], cap2: list[str]) -> int:
    return (len(cap1) * CAP1_LEAD + len(cap2) * CAP2_LEAD
            + CREDIT_SIZE + 34)


def _panel_chain(sizes: list[tuple[int, int]], speed: float,
                 grid: tuple[int, int], foot_h: int) -> tuple[str, int, int]:
    """Filter chain that lays the panels out on ``grid`` = (cols, rows).

    Every panel is fitted into ONE common box and padded to it, rather than
    scaled by height alone.  The campaign's frames are not all the same width --
    636 to 662 across the spiral's four fields, because a longer colourbar label
    makes a wider figure -- so height-only scaling leaves panels of unequal
    width, and ``vstack`` then refuses two rows that do not match.  That is what
    broke the spiral's 2x2 the first time this ran.  Padding inside the box
    keeps every aspect ratio exact and turns the difference into a few pixels of
    background at the panel edge.
    """
    cols, rows = grid
    head_h = HEAD_H if rows == 1 else HEAD_H_GRID
    free_h = H_OUT - head_h - foot_h
    # A one-row layout is centred; a 2x2 grid is pinned to the left edge and
    # leaves the side column at least SIDE_MIN_W.
    free_w = W_OUT - 40 if rows == 1 else W_OUT - GRID_X0 - SIDE_GAP - SIDE_MIN_W - SIDE_PAD_R
    # Height per panel before the grid-level fit, generous so the final scale
    # is a reduction (sharper) rather than an enlargement.
    panel_h = 900 if rows == 1 else 620
    box_w = max(int(round(w * panel_h / h)) for w, h in sizes)
    box_w += box_w % 2                       # libx264 wants even dimensions
    box_h = panel_h + panel_h % 2
    parts = []
    for i in range(len(sizes)):
        parts.append(
            f"[{i}:v]setpts=PTS/{speed},"
            f"scale={box_w}:{box_h}:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad={box_w}:{box_h}:(ow-iw)/2:(oh-ih)/2:color={PANEL_BG}[p{i}]")
    n_inputs = len(sizes)
    if rows == 1:
        parts.append("".join(f"[p{i}]" for i in range(n_inputs))
                     + f"hstack=inputs={n_inputs}[grid]")
    else:
        for r in range(rows):
            row_in = "".join(f"[p{r * cols + c}]" for c in range(cols))
            parts.append(f"{row_in}hstack=inputs={cols}[row{r}]")
        parts.append("".join(f"[row{r}]" for r in range(rows))
                     + f"vstack=inputs={rows}[grid]")
    # Fit the grid inside the free canvas, never upscaling past the canvas.
    parts.append(f"[grid]scale=w=min(iw*{free_h}/ih\\,{free_w}):h=-2:flags=lanczos[fit]")
    x_pad = "(ow-iw)/2" if rows == 1 else str(GRID_X0)
    parts.append(f"[fit]pad={W_OUT}:{H_OUT}:{x_pad}:{head_h}:color={GROUND}[canvas]")
    # The fitted grid's true geometry, so labels and marks land ON the panels.
    # A 2x2 grid is much narrower than the canvas, and placing text by canvas
    # fractions put the ownership marks in the dark margins OUTSIDE the plots
    # -- trivially croppable, which defeats them (the user, 2026-10-05).
    grid_w, grid_h = box_w * cols, box_h * rows
    s = min(free_h / grid_h, free_w / grid_w)
    fit_w = int(grid_w * s) & ~1
    fit_h = int(round(grid_h * (fit_w / grid_w)))
    x0 = (W_OUT - fit_w) // 2 if rows == 1 else GRID_X0
    geom = {"x0": x0, "y0": head_h, "w": fit_w, "h": fit_h}
    return ";".join(parts), cols, rows, geom


def _side_column(geom: dict) -> tuple[int, int]:
    """(x, width) of the text column right of a 2x2 grid."""
    x = geom["x0"] + geom["w"] + SIDE_GAP
    return x, W_OUT - SIDE_PAD_R - x


def _text_chain(tmp: Path, spec: dict, cols: int, rows: int, speed: float,
                cap1: list[str], cap2: list[str], geom: dict) -> str:
    """Header, per-panel labels, watermarks, branding and captions, all from text files.

    Everything goes through ``textfile=`` rather than ``text=``: the captions
    carry colons, commas, apostrophes and en-dashes, and escaping those through
    two levels of shell and ffmpeg quoting is how a caption silently truncates.
    Every position on a panel comes from ``geom``, the grid's real placement.
    """
    fields = spec["fields"]
    files = {}

    def put(name: str, value: str) -> str:
        (tmp / name).write_text(value, encoding="utf-8")
        files[name] = str(tmp / name)
        return files[name]

    def text(key: str, font: str, colour: str, size: int, x: str, y: float) -> str:
        return (f"drawtext=expansion=none:fontfile={font}:textfile={files[key]}:"
                f"fontcolor={colour}:fontsize={size}:x={x}:y={y:.0f}")

    put("title", spec["title"])
    rate = speed * spec.get("dt_frame", 1.0)
    put("speed", "real time" if abs(rate - 1.0) < 1e-9 else f"{rate:g}× speed")
    put("credit", CREDIT)
    put("mark", MARK)

    gx0, gy0, gw, gh = geom["x0"], geom["y0"], geom["w"], geom["h"]
    pw, ph = gw / cols, gh / rows
    sx, sw = _side_column(geom)

    # A 2x2 grid's title is left-aligned with the grid it heads.
    title_x = "(w-tw)/2" if rows == 1 else str(gx0)
    draw = [text("title", FONTB, "white", 34, title_x, 22),
            text("speed", FONTB, "0xE8B44A", 21, f"w-tw-{SIDE_PAD_R}", 26)]

    # Panel labels.  One row: centred over each panel in the header.  2x2: a
    # small key at the top of the side column, its four cells laid out as the
    # panels are, each outlined in its role's colour -- so "top left" needs no
    # words.  The grid's left edge has no margin left to hang a label in.
    cell_gap = 12
    cell_w = (sw - cell_gap * (cols - 1)) / cols
    for idx, field in enumerate(fields):
        r, c = divmod(idx, cols)
        role, colour = ROLE[field]
        head, _, name = role.partition("  ·  ")
        put(f"lab{idx}", role)
        put(f"role{idx}", head)
        put(f"name{idx}", name)
        if rows == 1:
            draw.append(text(f"lab{idx}", FONTB, colour, 19,
                             f"{gx0 + (c + 0.5) * pw:.0f}-tw/2", 78))
            continue
        x = sx + c * (cell_w + cell_gap)
        y = gy0 + r * (KEY_CELL_H + cell_gap)
        draw.append(f"drawbox=x={x:.0f}:y={y:.0f}:w={cell_w:.0f}:h={KEY_CELL_H}:"
                    f"color={colour}@0.55:t=2")
        draw.append(text(f"role{idx}", FONTB, colour, KEY_ROLE, f"{x + 14:.0f}", y + 10))
        draw.append(text(f"name{idx}", FONT, colour, KEY_NAME, f"{x + 14:.0f}", y + 31))

    # The ownership mark inside each panel's PLOT area: left of the panel's
    # centre (a panel is plot + colourbar, so its centre is on the colourbar)
    # and low in the plot, where the far field is quiet.  Outlined, so it reads
    # on a near-white panel and a near-black one alike.
    for idx in range(len(fields)):
        r, c = divmod(idx, cols)
        size = int(0.075 * ph) if rows > 1 else 30
        draw.append(
            f"drawtext=expansion=none:fontfile={FONTB}:textfile={files['mark']}:"
            f"fontcolor=white@0.45:bordercolor=black@0.40:borderw=1:fontsize={size}:"
            f"x={gx0 + (c + 0.40) * pw:.0f}-tw/2:y={gy0 + (r + 0.76) * ph:.0f}")

    if rows > 1:
        # The side column, top down: captions under the key; sponsor and credit
        # at the foot, level with the bottom of the grid.
        y = gy0 + rows * (KEY_CELL_H + cell_gap) + 26
        for tag, lines, size, lead, colour in (("c1", cap1, SIDE_CAP1, SIDE_LEAD1, "0xD5DEE7"),
                                               ("c2", cap2, SIDE_CAP2, SIDE_LEAD2, "0x9FB0C0")):
            for i, line in enumerate(lines):
                put(f"{tag}_{i}", line)
                draw.append(text(f"{tag}_{i}", FONT, colour, size, str(sx), y))
                y += lead
            y += 18
        cap_bottom = y - 18

        credit = _wrap(CREDIT, SIDE_CREDIT, sw, sep=CREDIT_SEP)
        base = gy0 + gh - SIDE_CREDIT
        for i, line in reversed(list(enumerate(credit))):
            put(f"cr_{i}", line)
            draw.append(text(f"cr_{i}", FONT, "0x9AA6B2", SIDE_CREDIT, str(sx), base))
            base -= SIDE_LEAD_CREDIT
        put("br0", BRAND_RIGHT[0])
        put("br1", BRAND_RIGHT[1])
        draw += [text("br0", FONT, "0xB8C2CC", 20, str(sx), base - 60),
                 text("br1", FONTB, "white", 27, str(sx), base - 30)]
        if cap_bottom > base - 60 - 24:
            print(f"[warn] {spec['out']}: captions reach the sponsor block "
                  f"({cap_bottom:.0f} > {base - 84:.0f} px)", file=sys.stderr)
        return "[canvas]" + ",".join(draw) + "[v]"

    # Footer, laid out UPWARDS from the credit so a wrapped caption grows into
    # the space the panel fit already gave up for it.
    y = H_OUT - CREDIT_SIZE - 14
    draw.append(text("credit", FONT, "0x9AA6B2", CREDIT_SIZE, "(w-tw)/2", y))
    for i, line in reversed(list(enumerate(cap2))):
        y -= CAP2_LEAD
        key = put(f"c2_{i}", line)
        draw.append(f"drawtext=expansion=none:fontfile={FONT}:textfile={key}:fontcolor=0x9FB0C0:"
                    f"fontsize={CAP2_SIZE}:x=(w-tw)/2:y={y}")
    for i, line in reversed(list(enumerate(cap1))):
        y -= CAP1_LEAD
        key = put(f"c1_{i}", line)
        draw.append(f"drawtext=expansion=none:fontfile={FONT}:textfile={key}:fontcolor=0xD5DEE7:"
                    f"fontsize={CAP1_SIZE}:x=(w-tw)/2:y={y}")
    return "[canvas]" + ",".join(draw) + "[v]"


def build(run_key: str, spec: dict, movies: Path, dest: Path,
          speed: float, fps: float, overwrite: bool) -> bool:
    # ``sub`` names a source subset filed beside the curated set (the zoomed or
    # re-scaled episodes zoom_frames.py draws for these videos).
    src = movies / run_key / spec.get("sub", "")
    fields = spec["fields"]
    inputs = [src / f"movie_{f}_z.mp4" for f in fields]
    missing = [p.name for p in inputs if not p.is_file()]
    if missing:
        print(f"[skip] {run_key}: missing {', '.join(missing)}", file=sys.stderr)
        return False

    out = dest / spec["out"]
    if out.exists() and not overwrite:
        print(f"[have] {out.name}")
        return True

    grid = (len(fields), 1) if len(fields) <= 2 else (2, (len(fields) + 1) // 2)
    if grid[1] == 1:
        # One row: captions in a footer under the panels, its height set by
        # how many lines they wrap to.
        cap1 = _wrap(spec["cap1"], CAP1_SIZE)
        cap2 = _wrap(spec["cap2"], CAP2_SIZE)
        chain, cols, rows, geom = _panel_chain([_probe_size(p) for p in inputs], speed, grid,
                                               _footer_height(cap1, cap2))
    else:
        # 2x2: the grid takes the full height, and the captions wrap to the
        # side column it leaves.
        chain, cols, rows, geom = _panel_chain([_probe_size(p) for p in inputs], speed, grid,
                                               GRID_PAD_B)
        _, sw = _side_column(geom)
        cap1 = _wrap(spec["cap1"], SIDE_CAP1, sw)
        cap2 = _wrap(spec["cap2"], SIDE_CAP2, sw)

    # ``t_end`` cuts a source with no slice cache at its trust window: keep the
    # frames t <= t_end (one frame per dt_frame code units at fps).
    trim = []
    if "t_end" in spec:
        n_keep = int(round(spec["t_end"] / spec.get("dt_frame", 1.0))) + 1
        trim = ["-t", f"{(n_keep - 0.5) / fps:.4f}"]

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        filt = chain + ";" + _text_chain(tmp, spec, cols, rows, speed, cap1, cap2, geom)
        cmd = ["ffmpeg", "-v", "error", "-y"]
        for p in inputs:
            cmd += trim + ["-i", str(p)]
        cmd += ["-filter_complex", filt, "-map", "[v]",
                "-r", f"{fps * speed:g}", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-crf", "18", "-preset", "slow", "-movflags", "+faststart", str(out)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"[fail] {run_key}: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else 'ffmpeg failed'}",
                  file=sys.stderr)
            return False
    print(f"[ok]   {out.name}  ({cols}x{rows} panels: {', '.join(fields)})")
    return True


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve()
    root = here.parents[5]                       # .../GRTeclyn
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--movies", type=Path, default=root / "results/merger/movies",
                    help="the curated movie tree (default: results/merger/movies)")
    ap.add_argument("--dest", type=Path, default=None,
                    help="output directory (default: <movies>/_youtube)")
    ap.add_argument("--only", default=None,
                    help="build only entries whose key contains this substring")
    ap.add_argument("--speed", type=float, default=1.0,
                    help="playback multiplier; the on-frame note follows it (default 1, real time)")
    ap.add_argument("--fps", type=float, default=10.0,
                    help="source frame rate (default 10, the campaign's cadence)")
    ap.add_argument("--force", action="store_true", help="rebuild files that already exist")
    args = ap.parse_args(argv)

    if shutil.which("ffmpeg") is None:
        print("ffmpeg not found", file=sys.stderr)
        return 2

    dest = args.dest or (args.movies / "_youtube")
    dest.mkdir(parents=True, exist_ok=True)

    made = failed = 0
    for key, spec in PANELS.items():
        if args.only and args.only not in key:
            continue
        if build(key, spec, args.movies, dest, args.speed, args.fps, args.force):
            made += 1
        else:
            failed += 1
    print(f"[all] {made} written to {dest}, {failed} skipped or failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
