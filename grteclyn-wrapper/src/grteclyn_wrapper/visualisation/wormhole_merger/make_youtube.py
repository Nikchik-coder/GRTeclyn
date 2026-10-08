#!/usr/bin/env python3
r"""Upload-ready 1080p videos of the wormhole-merger campaign.

The campaign's movies are one field per file, 628x538, 10 fps, drawn for
reading a diagnostic -- not for watching.  This builds the watchable version:
the fields that carry each encounter, 2x2 and in sync, on the left of one
1920x1080 canvas; on the right, a caption saying what is
happening, and the credits, all set in Computer Modern like the paper; and an
ownership mark inside the plot area of every panel (cropping one away crops
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
automatically, but the default is real time.  "Real time" means ten code units
per second of video; an entry whose frames are further apart than one unit says
so with ``dt_frame`` and its note follows (F4's inflation record: frames 2 units
apart, t = 0-218 in 11 s, "2x speed").  One whose frames are closer together
plays them at a higher frame rate instead and stays real time: the vacuum
controls save one every half unit and play at 20 fps (2026-10-05:
"bbh should be real time").

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
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# --------------------------------------------------------------------------
# Canvas.  1920x1080 with a dark ground that matches the movies' own figure
# background, so the margins the grid leaves read as deliberate rather than
# as letterboxing.
GROUND = "0x0E1216"
# Panels are padded to their common box with the frames' own white, so a 2x2
# grid is one clean rectangle.  Padding with GROUND left dark notches wherever
# two frames differed in width (the colourbar label sets it) -- the ragged
# corners flagged in review on 2026-10-05.
PANEL_BG = "0xFFFFFF"
W_OUT, H_OUT = 1920, 1080
# The grid sits at the LEFT edge, as tall as the canvas allows, and every word
# of text except the title goes in a column to its right: the
# captions, the sponsor and the credit (the chosen design, 2026-10-05).  Under
# the grid, the captions ran as two full-width lines a viewer could not read in
# one pass, and they cost the panels 130 px of height.
HEAD_H = 74           # header band: the title and the speed note
LABEL_H = 32          # the band above each row of panels that carries their labels
GRID_X0 = 24          # left margin of the grid
GRID_PAD_B = 20       # space under the grid
SIDE_GAP = 36         # gap between the grid and the side column
SIDE_MIN_W = 600      # the side column is never narrower than this
SIDE_PAD_R = 28       # right margin of the side column

# --------------------------------------------------------------------------
# Typography: the paper's, not a broadcast's (2026-10-05: "latex
# format", "PRD style", no colour coding).  Every word is Computer Modern --
# roman cmr10, bold cmb10, $...$ in matplotlib's "cm" maths, the set the
# panels' own maths is in -- in one ink, at three greys.  No TeX engine is
# needed: the fonts ship with matplotlib.  It is all set once per video into a
# transparent PNG that ffmpeg lays over the panels; nothing in it moves.
#
# Titles, captions and labels are written in a small LaTeX subset: $...$ is
# maths, --- and -- are the em and en dash, \emph{...} is italic.  The bundled
# fonts are OT1-encoded -- the dashes sit where ASCII has | and {, the curly
# apostrophe where it has ' -- so _tex() maps the subset onto those slots as
# TeX does, and refuses any character outside $...$ that would draw as some
# other glyph or none (a Unicode dash, arrow or Greek letter).  ffmpeg's
# drawtext, which set the text before, wrapped nothing and dropped a whole line
# at a bare per-cent sign (2026-09-21); none of that applies here.
INK = "#F0F0F0"         # title, first caption, label names, sponsor
INK_SOFT = "#B6BCC2"    # second caption, label roles, "Research sponsored by"
INK_FAINT = "#89929B"   # speed note, credit
RULE = "#3E464E"        # the side column's hairlines
TITLE_PX, SPEED_PX = 36, 22
LABEL_ROLE_PX, LABEL_NAME_PX = 15, 20
CAP1_PX, CAP2_PX, CREDIT_PX = 27, 24, 16
LEAD = 1.32             # baseline to baseline, in font sizes
DPI = 120               # the overlay: 16 x 9 in at 120 dpi is exactly 1920 x 1080
_OT1_TRAPS = set('"<>\\_^`{|}~')

# Branding (decided 2026-10-05).  The CHANNEL is First Interstellar
# Institute: its mark "FII" is printed inside every panel's plot area, so it
# cannot be cropped away without cropping the data; the channel's name is not
# spelled out on the frame (it is where the video is published).  Gravity
# Frontiers is the research SPONSOR, named in full at the foot of the side
# column (BRAND_RIGHT) and in the credit line.
MARK = "FII"
BRAND_RIGHT = ("Research sponsored by", "GRAVITY FRONTIERS")
CREDIT = ("First Interstellar Institute", "research sponsored by Gravity Frontiers",
          "GRTeclyn", "3+1 numerical relativity on GPUs")
CREDIT_SEP = r" $\cdot$ "

# Per-panel labels, role then name, each on the band right above its panel:
# a label hangs on what it names.  A key of the four in the side column, laid
# out as the panels are, made the viewer map positions by eye -- "hard to
# associate to frames" (2026-10-05).  The same in every video, so a
# viewer who watches two of them learns the roles once.
ROLE = {
    "chi":        ("GEOMETRY", r"conformal factor $\chi$"),
    "phi":        ("MATTER", r"phantom scalar $\phi$"),
    "Pi":         ("MATTER", r"scalar momentum $\Pi$"),
    "lapse":      ("GAUGE", r"lapse $\alpha$"),
    "K":          ("CURVATURE", r"trace $K$"),
    "Weyl4_Mag":  ("RADIATION", r"$|\Psi_4|$"),
    "Weyl4_Re":   ("RADIATION", r"$\mathrm{Re}(\Psi_4)$"),
}

# --------------------------------------------------------------------------
# What to build.  The panel list per campaign is a deliberate choice of what reads
# well; the layout code handles 2 or 4, and every entry currently takes 4.  The
# single throat gets exactly two videos, the two FATES -- the other seed arms
# look almost identical on screen and add nothing for a viewer.  Captions are
# the paper's own numbers: nothing is rounded further than the article rounds
# it, and nothing is claimed that the article does not.  Titles and captions
# are in the LaTeX subset described under Typography.
PANELS: dict[str, dict] = {
    "01_single_throat/single_eps_m1e2_L512_ml5_oct_t400": dict(
        out="01_wormhole_throat_inflates.mp4",
        fields=["K", "lapse", "chi", "phi"],
        sub="youtube",
        dt_frame=2.0,
        title=r"A lone wormhole throat inflates --- declared kick $\varepsilon=-0.01$",
        cap1=r"One drainhole throat, given a small inward kick. It does not collapse: it "
             r"keeps opening, $3.8{\times}$ in areal radius by $t=218$, and no trapped "
             r"surface forms.",
        cap2=r"Until $t\approx40$ it grows exponentially in its own proper time, 6% below "
             r"its unstable mode's linear rate. Then the lapse (top right) freezes the "
             r"clock at the throat, and its growth per unit $t$ slows: the slicing, not "
             r"the throat.",
    ),
    "01_single_throat/single_pureq_q1e2_ml4_t100": dict(
        out="02_wormhole_throat_collapses.mp4",
        fields=["K", "lapse", "chi", "Pi"],
        t_end=60.0,
        title=r"The same throat collapses --- a quadrupole seed",
        cap1=r"The mirror of the inflating run: the same throat, given a quadrupole instead "
             r"of an inward kick. It closes, and a horizon forms at $t=33$.",
        cap2=r"A wormhole throat is an unstable fixed point. Which way it falls is set by "
             r"the perturbation it is given --- and a quadrupole, unlike a spherical kick, "
             r"also leaves it something to radiate.",
    ),
    "04_binary_headon/headon_csm_L128_stitched_t0_t100": dict(
        out="03_headon_collision_makes_black_hole.mp4",
        fields=["K", "lapse", "chi", "Weyl4_Re"],
        sub="youtube_zoom2",
        title=r"Two wormholes collide head-on --- and make a black hole",
        cap1=r"Released from rest at separation 8, on constraint-solved initial data. They "
             r"touch while both mouths are still open wormholes, and one trapped surface "
             r"closes over \emph{both} at $t=18$ ($R=5.63$).",
        cap2=r"Neither mouth ever has a horizon of its own --- it is born common or not at "
             r"all. The remnant then \emph{loses} mass to the phantom field it swallows, "
             r"$2.82\to2.39$ by $t=100$ (the 3D horizon finder's full history).",
    ),
    "05_binary_spiral/spiral_d6_p010_L128_csm_stitched_t0_t100": dict(
        out="04_spiral_merger_makes_black_hole.mp4",
        fields=["K", "lapse", "chi", "Weyl4_Re"],
        sub="youtube_zoom2",
        title=r"Two wormholes with orbital momentum merge --- and a horizon forms",
        cap1=r"Separation 6, tangential momentum 0.10, constraint-solved data. The pair "
             r"turns only $15^{\circ}$ before a common trapped surface closes over both "
             r"mouths at $t=13$ ($R=5.60$): the orbital merger makes a black hole.",
        cap2=r"The remnant settles to $R=4.88$, losing mass to the phantom it swallows "
             r"($2.80\to2.44$ by $t=100$). One chain of certified restarts through two "
             r"numerical walls; the seams sit at $t=25$, 30 and 35.",
    ),
    "06_binary_flyby/merge_orbit_flip_d12_p025_L128_lvl5_t100_lbf_csm": dict(
        out="05_wormhole_flyby_no_merger_mouths_inflate.mp4",
        fields=["K", "lapse", "chi", "Weyl4_Re"],
        sub="youtube_zoom2",
        title=r"A wormhole fly-by --- no merger, and both mouths inflate",
        cap1=r"Separation 12, momentum 0.25 per mouth, constraint-solved boosted data. The "
             r"pair swings past (closest approach 2.32 at $t\approx48$) and separates --- "
             r"nothing merges, no horizon ever --- and both mouths \emph{inflate} as it goes.",
        cap2=r"In vacuum, black holes with even more momentum just coast apart (video 09): "
             r"the phantom field's pull is what drags this pair in, and the pass radiates a "
             r"phantom-scalar burst a vacuum binary has no analogue for.",
    ),
    "06_binary_flyby/merge_orbit_flip_d12_p060_L128_csm_stitched_t0_t80": dict(
        out="06_plunge_merger_no_horizon_yet.mp4",
        # Held back 2026-10-05 until P060-EXT; released 2026-10-06
        # with the captions rewritten after it (no MOTS at level 5 either):
        # contact at t ~ 40, no horizon through the t = 80 trust window, and the
        # p = 0.45 fly-by, not this plunge, radiates hardest (research.tex).
        fields=["K", "lapse", "chi", "Weyl4_Re"],
        title=r"A deeper plunge --- the mouths merge, and no horizon closes",
        cap1=r"The fly-by's momentum raised to 0.60 per mouth, past the circular value: the "
             r"pair now \emph{plunges}, reaches contact at $t\approx40$ and merges as "
             r"wormholes. It is not the loudest encounter: the $p=0.45$ fly-by, which "
             r"just escapes, radiates more.",
        cap2=r"No trapped surface converges on the merged core through $t=80$, the end of "
             r"the trustworthy record, on either of two grids. Unlike the head-on (03) and "
             r"the close orbit (04), this merger is not hidden behind a horizon as far as "
             r"the simulation can see.",
    ),
    "06_binary_flyby/merge_orbit_flip_d12_p090_L128_csm_stitched_t0_t45": dict(
        out="07_hardest_plunge_mouths_inflate.mp4",
        fields=["K", "lapse", "chi", "Weyl4_Re"],
        sub="youtube_zoom2",
        title=r"The hardest plunge --- the mouths inflate as they merge",
        cap1=r"Momentum 0.90 per mouth: the pair falls from separation 12 to 2.4 by "
             r"$t=40$. On the approach both mouths visibly \emph{inflate}, and the merging "
             r"core starts to inflate too.",
        cap2=r"No horizon is found at any time. The simulation stops at $t=45.3$, just "
             r"after the last frame, as the curvature at the merging core runs away; a run "
             r"at twice the resolution stops at the same instant.",
    ),
    # Separations and angles of the controls are from their punctures.dat.  The
    # d = 12 wormhole spiral this run is the twin of is not in this set, so the
    # captions do not lean on it.
    "07_bbh_control/bbh_control_d12_p012_t150": dict(
        out="08_control_two_black_holes_merge.mp4",
        fields=["Weyl4_Mag", "lapse", "chi", "Weyl4_Re"],
        dt_frame=0.5,
        title=r"Control --- two black holes plunge and merge, no scalar",
        cap1=r"The vacuum control: two black holes at separation 12, momentum 0.12 each, "
             r"and no scalar field. They plunge rather than spiral --- by $t=60$, 2.3 "
             r"apart, they have turned only $75^{\circ}$ --- then merge and ring down.",
        cap2=r"Its wave still climbs the point-mass track in frequency, then turns toward "
             r"the Kerr ringdown tone: a monotone rise, then a fixed frequency. No wormhole "
             r"channel follows that track.",
    ),
    "07_bbh_control/bbh_headon_d8_L128_lvl5_t100": dict(
        out="10_control_two_black_holes_collide_headon.mp4",
        fields=["K", "lapse", "chi", "Weyl4_Re"],
        sub="youtube",
        dt_frame=0.5,
        title=r"Control --- the head-on collision in vacuum",
        cap1=r"The wormhole head-on's vacuum twin: two bare black holes of the same mass, "
             r"released from rest at the same separation and base resolution, in a box "
             r"half the size. They fall together, merge, and ring down.",
        cap2=r"Watch it beside the wormhole head-on (video 03): there the horizon closes "
             r"over two still-open wormholes and the remnant then \emph{loses} mass to the "
             r"phantom field it swallows --- a vacuum remnant can only grow.",
    ),
    "07_bbh_control/bbh_control_d12_p045_t100": dict(
        out="09_control_two_black_holes_fly_apart.mp4",
        fields=["Weyl4_Mag", "lapse", "chi", "Weyl4_Re"],
        dt_frame=0.5,
        title=r"Control --- two black holes fly apart, no scalar",
        cap1=r"Two black holes at separation 12, momentum 0.45 each, and no scalar field. "
             r"In vacuum that momentum is unbound: they start at closest approach and "
             r"coast apart, to separation 27 by $t=100$.",
        cap2=r"Watch it beside the wormhole fly-by (video 05): with the phantom field the "
             r"pull is several times stronger, so even at momentum 0.25 the pair falls in "
             r"to 2.32, and the mouths inflate as they pass.",
    ),
    # 11 and 12 (2026-10-08): the referee pass's far-zone head-on and the like-signed pair's fate.
    # Their numbers are the registry's (FARZONE-ho, SCATTER-fate); the far-zone energy itself is not on the
    # frame until the article quotes it.  Both keep their runs' own windows: +-32 about the centre, which is
    # the whole box for SCATTER-fate (the mouths must stay in view as they fly apart).
    "08_convergence/farzone_headon_flip_d8_L512_lvl6_t250_csm": dict(
        out="11_headon_collision_far_zone_waves.mp4",
        fields=["K", "lapse", "chi", "Weyl4_Re"],
        title=r"The head-on collision in a box four times wider --- run to $t=250$",
        cap1=r"The head-on of video 03 again, in a box of side 512 instead of 128, with wave "
             r"detectors out to $R=180$ (76 masses). Released from rest at separation 8, the "
             r"throats touch and one trapped surface closes over both at $t=18$, as in the "
             r"smaller box.",
        cap2=r"This run is for the waves: on spheres from $R=10$ out to 180 the radiated "
             r"energy settles as the sphere moves out, and the near spheres agree with the "
             r"production run to 1%. The frame shows the central $\pm32$; the wave leaves it "
             r"and travels on to the far spheres.",
    ),
    "03_two_throats/csm/ctrl_rest_d12_csm_t100": dict(
        out="12_wormholes_push_apart_mouths_inflate.mp4",
        fields=["K", "lapse", "chi", "phi"],
        dt_frame=0.5,
        title=r"Two like-signed wormholes push apart --- and both mouths inflate",
        cap1=r"Two identical wormholes released from rest at separation 12, on "
             r"constraint-solved data. Like-signed phantom fields repel: the pair flies "
             r"apart, to separation 26 by $t=60$, and both mouths \emph{inflate} as they go "
             r"--- each throat's areal radius grows from 3.88 to 4.78 by $t=30$ and keeps "
             r"growing.",
        cap2=r"Both light-ray expansions are positive at each throat: the mouths are "
             r"anti-trapped, on the inflating branch of the lone throat (video 01), and no "
             r"horizon forms. The video stops at $t=80$; later frames are spoiled by the "
             r"box's edge.",
    ),
}


def _probe_size(path: Path) -> tuple[int, int]:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True)
    w, h = r.stdout.strip().split(",")[:2]
    return int(w), int(h)


def _panel_chain(sizes: list[tuple[int, int]], speed: float,
                 grid: tuple[int, int]) -> tuple[str, int, int, dict]:
    """Filter chain that lays the panels out on ``grid`` = (cols, rows).

    Every panel is fitted into ONE common box and padded to it, rather than
    scaled by height alone.  The campaign's frames are not all the same width --
    636 to 662 across the spiral's four fields, because a longer colourbar label
    makes a wider figure -- so height-only scaling leaves panels of unequal
    width, and ``vstack`` then refuses two rows that do not match.  That is what
    broke the spiral's 2x2 the first time this ran.  Padding inside the box
    keeps every aspect ratio exact and turns the difference into a few pixels of
    background at the panel edge.  The box is sized for the canvas up front, so
    each frame is resampled once, and each row of panels sits under a LABEL_H
    band of ground for its labels.
    """
    cols, rows = grid
    aspect = max(w / h for w, h in sizes)
    free_h = H_OUT - HEAD_H - GRID_PAD_B - rows * LABEL_H
    free_w = W_OUT - GRID_X0 - SIDE_GAP - SIDE_MIN_W - SIDE_PAD_R
    ph = int(min(free_h / rows, free_w / cols / aspect)) & ~1   # libx264 wants even sizes
    pw = int(ph * aspect) & ~1

    def stack(kind: str, labels: list[str]) -> str:
        return "".join(labels) + (f"{kind}=inputs={len(labels)}" if len(labels) > 1 else "null")

    parts = []
    for i in range(len(sizes)):
        parts.append(
            f"[{i}:v]setpts=PTS/{speed},"
            f"scale={pw}:{ph}:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad={pw}:{ph}:(ow-iw)/2:(oh-ih)/2:color={PANEL_BG}[p{i}]")
    for r in range(rows):
        parts.append(stack("hstack", [f"[p{r * cols + c}]" for c in range(cols)])
                     + f",pad=iw:ih+{LABEL_H}:0:{LABEL_H}:color={GROUND}[row{r}]")
    parts.append(stack("vstack", [f"[row{r}]" for r in range(rows)])
                 + f",pad={W_OUT}:{H_OUT}:{GRID_X0}:{HEAD_H}:color={GROUND}[canvas]")
    # The grid's true geometry, so labels and marks land ON the panels.  Placing
    # text by canvas fractions once put the ownership marks in the dark margins
    # OUTSIDE the plots -- trivially croppable, which defeats them
    # (2026-10-05).
    geom = {"x0": GRID_X0, "y0": HEAD_H, "w": pw * cols, "h": rows * (LABEL_H + ph),
            "pw": pw, "ph": ph}
    return ";".join(parts), cols, rows, geom


def _side_column(geom: dict) -> tuple[int, int]:
    """(x, width) of the text column right of the grid."""
    x = geom["x0"] + geom["w"] + SIDE_GAP
    return x, W_OUT - SIDE_PAD_R - x


def _tex(s: str) -> str:
    """Map the LaTeX subset onto what matplotlib draws in the OT1 fonts."""
    s = re.sub(r"\\emph\{([^}]*)\}",
               lambda m: " ".join(rf"$\mathit{{{w}}}$" for w in m.group(1).split()), s)
    parts = s.split("$")
    if len(parts) % 2 == 0:
        raise ValueError(f"unbalanced $ in {s!r}")
    for i in range(0, len(parts), 2):            # the text between the maths
        bad = sorted({c for c in parts[i] if not " " <= c <= "~" or c in _OT1_TRAPS})
        if bad:
            raise ValueError(f"{''.join(bad)!r} outside $...$ would not draw as itself "
                             f"in Computer Modern; write it in the LaTeX subset: {s!r}")
        parts[i] = parts[i].replace("---", "|").replace("--", "{")
    return "$".join(parts)


def _words(s: str) -> list[str]:
    """Split at the spaces outside $...$; a space inside maths is no break."""
    out, cur, maths = [], "", False
    for ch in s:
        if ch == "$":
            maths = not maths
        if ch == " " and not maths:
            if cur:
                out.append(cur)
            cur = ""
        else:
            cur += ch
    return out + [cur] if cur else out


def _pieces(s: str) -> list[tuple[str, bool]]:
    """A paragraph's break points: (piece, a space follows).  A word also
    breaks after a hyphen between letters, as TeX's does, so a compound like
    "constraint-solved" does not have to fit a narrow line whole."""
    out = []
    for w in _words(s):
        if w == "|" and out:                      # an em dash never starts a line
            out[-1] = (out[-1][0] + " |", True)   # (TeX's ~---)
            continue
        parts = [w] if "$" in w else re.split(r"(?<=[A-Za-z]-)(?=[A-Za-z])", w)
        out += [(part, False) for part in parts[:-1]] + [(parts[-1], True)]
    return out


class _Page:
    """A transparent 1920x1080 sheet, set in Computer Modern."""

    def __init__(self) -> None:
        import matplotlib
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.figure import Figure
        self._ttf = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
        self.fig = Figure(figsize=(W_OUT / DPI, H_OUT / DPI), dpi=DPI)
        FigureCanvasAgg(self.fig)
        self._renderer = self.fig.canvas.get_renderer()

    def _prop(self, px: float, bold: bool):
        from matplotlib.font_manager import FontProperties
        return FontProperties(fname=str(self._ttf / ("cmb10.ttf" if bold else "cmr10.ttf")),
                              size=px * 72 / DPI, math_fontfamily="cm")

    def _width(self, s: str, px: float, bold: bool = False) -> float:
        w, _, _ = self._renderer.get_text_width_height_descent(
            s, self._prop(px, bold), ismath="$" in s)
        return w

    def _set(self, x: float, y: float, s: str, px: float, ink, bold: bool = False,
             ha: str = "left"):
        return self.fig.text(x / W_OUT, 1 - y / H_OUT, s, fontproperties=self._prop(px, bold),
                             color=ink, ha=ha, va="baseline")

    def width(self, s: str, px: float, bold: bool = False) -> float:
        return self._width(_tex(s), px, bold)

    def text(self, x: float, y: float, s: str, px: float, ink, bold: bool = False,
             ha: str = "left"):
        """Set ``s`` with its baseline on pixel row ``y``, counted from the top."""
        return self._set(x, y, _tex(s), px, ink, bold, ha)

    def rule(self, x0: float, x1: float, y: float) -> None:
        from matplotlib.lines import Line2D
        self.fig.add_artist(Line2D([x0 / W_OUT, x1 / W_OUT], [1 - y / H_OUT] * 2,
                                   transform=self.fig.transFigure, color=RULE, linewidth=0.8))

    def paragraph(self, x: float, y: float, width: float, s: str, px: float, ink) -> float:
        """Set ``s`` justified to ``width`` px, first baseline at ``y``.

        TeX's way, minus its dictionary hyphenation: the breaks are chosen for
        the whole paragraph at once, keeping every line's spaces near their
        natural width (squared deviation, summed), with spaces free to shrink
        to 80 % and a small charge for breaking at a hyphen.  A greedy fill
        justified a 600 px column into visible holes.  A line that would still
        stretch past 2.2 spaces is left ragged, and so is the last.  Returns
        the baseline a next line would take.
        """
        pieces = [(w, self._width(w, px), sp) for w, sp in _pieces(_tex(s))]
        space = px / 3                           # cmr10's interword space, 1/3 em
        n = len(pieces)

        def fill(i: int, j: int) -> tuple[float, int]:   # pieces i..j-1 as a line
            line = pieces[i:j]
            return sum(wd for _, wd, _ in line), sum(sp for _, _, sp in line[:-1])

        best = [0.0] + [float("inf")] * n        # best[j]: the cheapest set of pieces[:j]
        cut = [0] * (n + 1)
        for j in range(1, n + 1):
            for i in range(j - 1, -1, -1):
                ink_w, gaps = fill(i, j)
                if j - i > 1 and ink_w + 0.8 * space * gaps > width:
                    break                        # a longer line is only tighter
                if j == n or ink_w >= width:
                    cost = 0.0
                elif gaps == 0:
                    cost = 25.0                  # one word alone on a full line
                else:
                    cost = ((width - ink_w) / gaps / space - 1) ** 2
                if not pieces[j - 1][2]:
                    cost += 0.5                  # a break at a hyphen
                if best[i] + cost < best[j]:
                    best[j], cut[j] = best[i] + cost, i
        lines, j = [], n
        while j > 0:
            lines.append((cut[j], j))
            j = cut[j]
        for i, j in reversed(lines):
            ink_w, gaps = fill(i, j)
            gap = space
            if j < n and gaps and (width - ink_w) / gaps <= 2.2 * space:
                gap = (width - ink_w) / gaps
            xx = x
            for w, wd, sp in pieces[i:j]:
                self._set(xx, y, w, px, ink)
                xx += wd + (gap if sp else 0.0)
            y += LEAD * px
        return y

    def segments(self, segs: tuple[str, ...], sep: str, px: float, width: float) -> list[str]:
        """Join ``segs`` with ``sep`` into lines no wider than ``width``,
        breaking only between segments."""
        lines, cur = [], ""
        for seg in segs:
            trial = f"{cur}{sep}{seg}" if cur else seg
            if cur and self.width(trial, px) > width:
                lines.append(cur)
                cur = seg
            else:
                cur = trial
        return lines + [cur]

    def save(self, path: Path) -> None:
        self.fig.savefig(path, dpi=DPI, transparent=True)


def _overlay(path: Path, spec: dict, cols: int, rows: int, speed: float, geom: dict) -> None:
    """Every word on the frame, set once into a transparent PNG at ``path``.

    Every position on a panel comes from ``geom``, the grid's real placement.
    """
    page = _Page()
    pw, ph = geom["pw"], geom["ph"]
    sx, sw = _side_column(geom)

    def corner(r: int, c: int) -> tuple[float, float]:     # a panel's top left
        return geom["x0"] + c * pw, geom["y0"] + LABEL_H + r * (LABEL_H + ph)

    rate = speed * spec.get("dt_frame", 1.0)
    note = "real time" if abs(rate - 1.0) < 1e-9 else rf"${rate:g}{{\times}}$ speed"
    page.text(geom["x0"], HEAD_H - 24, spec["title"], TITLE_PX, INK, bold=True)
    page.text(W_OUT - SIDE_PAD_R, HEAD_H - 24, note, SPEED_PX, INK_FAINT, ha="right")
    room = W_OUT - SIDE_PAD_R - page.width(note, SPEED_PX) - 30 - geom["x0"]
    if page.width(spec["title"], TITLE_PX, bold=True) > room:
        print(f"[warn] {spec['out']}: the title runs into the speed note", file=sys.stderr)

    # Each panel's label on the band right above it, flush with its left edge.
    for idx, field in enumerate(spec["fields"]):
        x, top = corner(*divmod(idx, cols))
        role, name = ROLE[field]
        page.text(x, top - 9, role, LABEL_ROLE_PX, INK_SOFT, bold=True)
        page.text(x + page.width(role, LABEL_ROLE_PX, bold=True) + 10, top - 9, name,
                  LABEL_NAME_PX, INK)

    # The captions, justified to the side column, level with the panels' top.
    y = page.paragraph(sx, geom["y0"] + LABEL_H + 0.7 * CAP1_PX, sw, spec["cap1"], CAP1_PX, INK)
    y = page.paragraph(sx, y + 10, sw, spec["cap2"], CAP2_PX, INK_SOFT)
    cap_bottom = y - (LEAD - 0.3) * CAP2_PX

    # Sponsor and credit at the foot, level with the bottom of the grid.
    base = geom["y0"] + geom["h"] - 6
    for line in reversed(page.segments(CREDIT, CREDIT_SEP, CREDIT_PX, sw)):
        page.text(sx, base, line, CREDIT_PX, INK_FAINT)
        base -= LEAD * CREDIT_PX
    base -= 12
    page.text(sx, base, BRAND_RIGHT[1], 28, INK, bold=True)
    page.text(sx, base - 36, BRAND_RIGHT[0], 20, INK_SOFT)
    top_rule = base - 36 - 20 - 16
    page.rule(sx, sx + sw, top_rule)
    if cap_bottom + 16 > top_rule:
        print(f"[warn] {spec['out']}: the captions reach the sponsor block "
              f"({cap_bottom:.0f} > {top_rule - 16:.0f} px)", file=sys.stderr)

    # The ownership mark inside each panel's PLOT area: left of the panel's
    # centre (a panel is plot + colourbar, so its centre is on the colourbar)
    # and low in the plot, where the far field is quiet.  Outlined, so it reads
    # on a near-white panel and a near-black one alike.
    from matplotlib import patheffects
    size = 0.075 * ph
    for idx in range(len(spec["fields"])):
        x, top = corner(*divmod(idx, cols))
        mark = page.text(x + 0.40 * pw, top + 0.76 * ph + 0.7 * size, MARK, size,
                         (1, 1, 1, 0.45), bold=True, ha="center")
        mark.set_path_effects([patheffects.withStroke(linewidth=1.5,
                                                      foreground=(0, 0, 0, 0.40))])
    page.save(path)


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

    # A held entry builds into held_back/, out of the upload set.
    out = dest / ("held_back" if spec.get("hold") else "") / spec["out"]
    out.parent.mkdir(exist_ok=True)
    if out.exists() and not overwrite:
        print(f"[have] {out.name}")
        return True

    # Frames closer than one code unit apart play at a higher frame rate, so the
    # video stays real time; frames further apart play fast, and say so.  An
    # entry's own ``speed`` scales that, and the on-frame note follows it.
    speed = speed * spec.get("speed", 1.0) / min(spec.get("dt_frame", 1.0), 1.0)

    grid = (len(fields), 1) if len(fields) <= 2 else (2, (len(fields) + 1) // 2)
    chain, cols, rows, geom = _panel_chain([_probe_size(p) for p in inputs], speed, grid)

    # ``t_end`` cuts a source with no slice cache at its trust window: keep the
    # frames t <= t_end (one frame per dt_frame code units at fps).
    trim = []
    if "t_end" in spec:
        n_keep = int(round(spec["t_end"] / spec.get("dt_frame", 1.0))) + 1
        trim = ["-t", f"{(n_keep - 0.5) / fps:.4f}"]

    with tempfile.TemporaryDirectory() as td:
        text_png = Path(td) / "text.png"
        _overlay(text_png, spec, cols, rows, speed, geom)
        # The text is one still image; overlay repeats it over every frame.
        filt = chain + f";[canvas][{len(inputs)}:v]overlay=0:0[v]"
        cmd = ["ffmpeg", "-v", "error", "-y"]
        for p in inputs:
            cmd += trim + ["-i", str(p)]
        cmd += ["-i", str(text_png), "-filter_complex", filt, "-map", "[v]",
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
        if spec.get("hold") and not args.only:
            print(f"[hold] {spec['out']}: {spec['hold']}")
            continue
        if build(key, spec, args.movies, dest, args.speed, args.fps, args.force):
            made += 1
        else:
            failed += 1
    print(f"[all] {made} written to {dest}, {failed} skipped or failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
