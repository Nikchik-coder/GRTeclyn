#!/usr/bin/env python3
r"""The waveform gallery: every scenario's wave, one row each, one clock.

The six-panel ``plot_psi4_analysis`` dashboards are working diagnostics --
spectra, wavefront speeds, spectrograms, LIGO overlays -- and five of them
side by side is thirty panels no reader will cross.  The paper's question is
simpler: WHAT DID EACH SYSTEM RADIATE, AND IS IT RADIATION?  So each row
keeps exactly two panels:

  left   the real part of the dominant mode's r*Psi4 at the innermost
         extraction sphere, on retarded time, every row on the same clock so
         durations and frequencies compare by eye; a half-height cap marks
         where the drawn record ends, with the reason written beside it when
         the reason is not "the run finished";
  right  the amplitude ENVELOPE of r*Psi4 at EVERY sphere on its own retarded
         time, the correlated wavefront dotted, and the speed it travels
         between neighbouring spheres -- the discriminator that separates
         radiation (v ~ c, envelopes folding onto one curve) from a gauge or
         constraint mode wearing a wave's clothes.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_psi4_gallery

SPEEDS come from ``psi4_math.wavefront_speeds_xcorr``: the lag of the whole
complex waveform between spheres, correlated over the retarded interval both
cover.  Peak-to-peak timing is what the dashboards print, and it fails here
twice over -- the BBH control's merger envelope is a ~15-unit plateau at
both spheres, so its peak times alone read v = 0.57 where the waveform lag
reads 0.82, and the spiral's outer spheres have no peak yet at all.  The
gold dots sit where the CORRELATED front lands on each envelope (the
innermost envelope maximum, advanced by the measured lags), so the dots and
the quoted v/c are one measurement; a sphere the front has not yet reached
inside the drawn record gets no dot.  The speeds are measured on exactly the
records drawn (``drawn`` below), never on a longer one.

THE ENVELOPE (2026-09-24, first-author review: "why do the right-column peaks
in (c)-(e) grow -- the hills grow when (a) and (b) touch the x axis").  Until
then the right column drew |r Psi4| as it stands.  For the (2,2) rows that is
the modulus of a complex mode, an amplitude that rises smoothly toward the
burst; but the (2,0) modes of the axisymmetric throat and head-on are REAL
(Im/Re < 1e-7), so |r Psi4| was the rectified wave, dropping to zero at every
node -- two different quantities in one column, which is exactly what the
reviewer read.  Real records now get the analytic-signal envelope (Hilbert
transform, the record reflected at both ends), the convention
``plot_psi4_ligo.envelope_and_frequency`` already uses for Fig. 11(a), drawn
to each record's last crest: past it no extension knows what the cut removed
and the modulus sags toward |y(cut)|.  The complex rows keep |r Psi4| to the
end; the spiral's swings within a cycle are a counter-rotating (partly
linear) component of its plunge -- 13-15 % of the power sits at the other
sign of frequency -- not noise.

THE DRAWING GATES (``DRAW_GATES``, same review).  What grew in the right
column was, row by row (numbers from
``grteclyn-wrapper/scripts/analysis/merger_feedback/waves_gallery_audit.py``):

  collapsing throat  sphere-local numerical growth.  The exact level-4
         spherical control (``single_eps_p1e2_q1e2_ml4_scalar_t100``: the +0.01
         kick on a binary that ignores the quadrupole key, so its l = 2 content
         is the floor) passes 10 % of the burst peak at t = 55 / 54 / 52
         (R = 10 / 14 / 18) and equals it by t = 72 / 71 / 65; the queue-2e junk
         cuts (70 / 69 / 63 / 61) were set by an 8-sigma outlier test and leave
         those tails in.  Each sphere is drawn to its 10 % crossing, R = 22 on
         R = 18's clock (the junk arrives near-simultaneously, outer spheres
         first); R = 10 to t = 58, the end of the ringdown fit, where the floor
         is still <= 14 % of the burst peak.
  spiral the record past the fill's causal clock t = 57 + (R - 1.9) is the
         frozen-core arm's transport, and grid-scale noise (f ~ 2/M, period
         ~ 0.5 M; common to both fill-window twins, so not the fill's edge)
         grows on R = 20 / 28 from 1e-3 of peak at t ~ 60 to 1e-2 at that
         clock and 0.09 / 0.15 by t = 95.  That late stretch alone produced
         the "0.95" on the 20->28 pair: drawn and correlated to the clock (or
         to any t - R <= 65), every pair reads 1.00.  Each sphere is drawn to
         its clock.
  fly-by the t <= 70 gate was applied in COORDINATE time to every sphere, which
         cut R = 36 exactly at its burst peak (t = 69.97) and R = 44 before its
         peak (t = 76.7): the outer envelopes stopped while still rising.  The
         gate is now retarded, t - R <= 50 at every sphere (t = 70 at R = 20, as
         before): the contaminant from the expanding mouths only equals the
         decaying burst at t - R = 56 (R = 20), 64 (R = 28) and not before the
         record ends at R = 36 / 44.
  vacuum twin, head-on  nothing to gate.  The twin's rise is its chirp, its
         first ~30 units the initial-data burst; the head-on's level-3 frozen
         stream agrees with the level-5 no-fill arm to 1 % of peak at R = 10
         throughout and at R = 14 / 18 to t - R = 60 / 52 (3 % to 72 / 65).

``ARMS`` is untouched by this: it is the scenario table the LIGO figure and
the claims ledger read, and its ``t_max`` is theirs.  The gallery draws with
``DRAW_GATES`` through ``drawn()``; a consumer that wants the gallery's own
numbers (the speeds printed on the strips) should read them through
``drawn()`` too.

Rows are the ARMS table below; an arm whose stream is missing is skipped
with a note.  Amplitudes are NOT on a shared scale -- the lone throat
radiates 10x below the mergers, and one scale would flatten it to a rule --
so each row states its own scale and the right panel shares it.  The streams
already fold the extraction radius into the amplitude (r*Psi4, see
streams.py); nothing here multiplies by R again.

THE RINGDOWN FIT (same review: "this fit should be shown on the GW
pictures").  Row (a) carries the damped sinusoid of queue-2e gate 4 --
``results/merger/analysis/queue2e_gates.py``, recomputed here with the pack's
own routine on the same record and window (R = 10, from the burst peak at
t = 26 to t = 58), drawn dashed over exactly that window.

STYLE (the seed-branches grammar): figure* width, style.prd frame, no boxed
keys, and after 2026-09-16 review NO TEXT INSIDE THE PANELS beyond the cap
notes and, since 2026-09-25, the names of the one fitted model and the vacuum
controls, each on its own curve -- the scenario, its knob, the mode/spheres
and the speeds all sit on the strip above each row's frames, where no
waveform can collide with them -- monochrome ink with the grey ramp
inner->outer on the envelopes, the gold accent reserved for the wavefront,
deep blue for the one fitted model, (a)-(d) tags, semantics in the caption.
7.05 x 4.6 in since 2026-09-25 (was 7.05 x 5.6 with the twin as row (e)).

THE VACUUM CONTROLS UNDER ROWS (c) AND (d) (2026-09-25, the user: "we also
did a BBH fly-by with the same params -- add its extracted signal for
comparison", then "place the BBH spiral into (c) the same way, so it is
compared").  Each drainhole binary's black-hole twin -- same d and p, bare
punctures, no scalar -- in the LIGO figure's vacuum colour (CONTEXT) under the
ink, on the SAME sphere (R = 20, from each control's in-code extraction) and
scale, named on its own curve ("vacuum BBH spiral" / "vacuum BBH fly-by";
"vacuum BBH" alone read as the spiral's twin, the user); left panel only,
since CONTEXT is also a sphere of the envelope ramp.  The spiral's twin was row
(e) until then; it stays in ARMS, which the LIGO figure and the ledger read.
It is drawn whole, its merger (peak 1.02e-2 at t - R = 84.8) 2.9x below and
43 units after the drainhole burst; the vacuum fly-by is drawn over the
fly-by's own window: one cycle as the holes swing off periapsis (peak 9.0e-3,
4.5x below the fly-by) and nothing at the pass.  Row (a)'s dashed curve is
named "ringdown fit" on the curve (the user).  The momentum knob prints as p,
the article's symbol (it printed P).
"""

from __future__ import annotations

import argparse
import importlib
import pathlib
import string
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.signal import find_peaks, hilbert  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import streams, style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.psi4_math import (  # noqa: E402
    wavefront_speeds_xcorr,
)
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import PACK_ROOT, figure_dir  # noqa: E402

GROUP = "08_waves"   # cross-cutting: the figure belongs to no single group

# One row per scenario: (name, knob, mode label, stream path under campaign/,
# m or None, innermost extraction radius, t_max, end-note).  m=None means a
# single-mode file; an integer selects that m from psi4_mode_l2_all.dat.
# t_max is the gate the LIGO figure and the claims ledger apply (a coordinate
# cap at the innermost sphere); the gallery itself draws with DRAW_GATES below,
# which are per-sphere and, where it matters, retarded.
#   single  QUEUE2E_GATES.md junk cuts (R=10 from t=70; the gated file holds
#           zeros past each sphere's cut, trimmed per sphere below);
#   fly-by  the L = 128 level-5 arm, finished t = 100 clean 2026-09-18 and
#           filed under 06_binary_flyby/p045/.  No horizon ever forms: both
#           mouths expand (areal R 4.2 -> 33 by t = 97) and that expansion
#           contaminates the innermost sphere, so the row is gated.
#           GATED t = 70 (was 76 until 2026-09-18).  t = 76.08 is where
#           |rPsi4| at R = 20 TURNS BACK UP -- the trough, i.e. the point
#           where the contaminant has grown to EQUAL the decaying burst, not
#           where it arrives.  It is already comparable well before that, and
#           by t = 100 it is 2.0x the burst peak.  t = 70 keeps 15.5 units
#           (7.8 M) past the R = 20 burst peak at t = 54.5 and leaves the
#           contaminant sub-dominant throughout.
#           The retired note on this row claimed "R = 36/44 decay
#           monotonically to the record's end".  They do not: that reading
#           normalised each sphere by its max over t <= 60, which truncates
#           the OUTER spheres' bursts before they peak (light travel puts the
#           R = 44 burst at t ~ 78, not 60).  In retarded time all four
#           spheres peak together at u = t - R ~ 34.5, as radiation must;
#   spiral  the freeze arm finished t = 100 on 2026-09-16, so the SERIES now
#           runs t = 0-100 in three legs.  Leg 3 holds the core frozen inside
#           r = 1.40 from t = 57, which transports the burst the merger
#           already made rather than evolving a remnant -- so the gallery
#           draws it only to the fill's causal clock (DRAW_GATES).
ARMS = [
    ("collapsing throat", r"$\varepsilon_2=5\times10^{-2}$", "(2,0)",
     "01_single_throat/seed/single_eps_p1e2_q5e2_ml4_t100/psi4_mode_l2m0_gated.dat",
     None, 10.0, 70.0, r"gated $t{=}70$"),
    ("head-on", r"$\sigma=-1$, $d=8$", "(2,0)",
     "04_binary_headon/merge_headon_flip_d8_v1c_latefreeze_t100/psi4_mode_l2m0.dat",
     None, 10.0, None, ""),
    ("spiral", r"$p=0.12$, $d=12$", "(2,2)",
     "05_binary_spiral/p012_paper/v2_spiral_d12_p012_L128_SERIES/Weyl4_mode_22.dat",
     None, 20.0, None, r"core frozen $t{>}57$"),
    ("fly-by", r"$p=0.45$, $d=12$", "(2,2)",
     "06_binary_flyby/p045/merge_orbit_flip_d12_p045_L128_lvl5_t100/Weyl4_mode_22.dat",
     None, 20.0, 70.0, r"gated $t{=}70$ (mouths expand)"),
    # The spiral's vacuum twin: a scenario of the LIGO figure and the ledger,
    # but in the gallery it is drawn UNDER the spiral row (OVERLAID below).
    ("vacuum BBH twin", r"$p=0.12$, $d=12$", "(2,2)",
     "07_bbh_control/bbh_control_d12_p012_t150/psi4_mode_l2_all.dat",
     2, 14.0, None, ""),
    # NOT a row here: bbh_control_d12_p045_t100, the momentum-matched vacuum
    # control (2026-09-19).  Its energy is quoted in Sec. VIII of the article
    # and in the GPU plan, but it cannot join this table, because the table's
    # contract is "innermost sphere, spread over spheres as the error bar" and
    # that arm has two spheres of which one is contaminated: its punctures
    # recede to r = 13.7 by t = 100, almost onto R = 14, whose reading is their
    # own field sweeping past (22x above R = 30, and still growing at the
    # record's end).  One clean sphere cannot form a spread.  Reproduce the
    # number with psi4_math._compute_radiated_energy on R = 30 of
    # campaign/07_bbh_control/bbh_control_d12_p045_t100/psi4_mode_l2_all.dat,
    # m = 2, M = 2.0: E/M = 1.05e-3.  The gallery draws its wave OVER the
    # fly-by row instead (VACUUM_OVERLAY below).
]

# Drawn UNDER a row, not as one (2026-09-25, the user; the docstring's last
# section): each drainhole binary's black-hole twin, the same d and p on bare
# punctures, from the control's in-code extraction at the row's own sphere.
# Per row: (stream under campaign/, sphere, name, cut to the row's drawn
# window?, the t - R span its name covers, and whether it sits above or below
# both curves there).  The spiral's twin is named under its merger trough, so
# the name cannot run on from the spiral's cap note ("fill's light cone").
#   spiral  bbh_control_d12_p012_t150 (the ARMS twin, whose consumer stream
#           has only R = 14/30; the in-code one agrees with it to 0.3 % of
#           peak on both).  Drawn whole: nothing contaminates it, and its
#           merger comes after the spiral's drawn record ends.
#   fly-by  bbh_control_d12_p045_t100 (1.5 % of peak against its consumer at
#           R = 30).  Cut to the fly-by's own window: past t - R ~ 30 its
#           record is no longer radiation but the receding holes' near field,
#           a flat +3e-3 at R = 20 that falls across R = 20/26/30 (on this
#           row's scale a rule), and the holes reach r = 13.7 by t = 100.  Its
#           two lobes fold across R = 20/26/30 at v/c = 0.99/0.96.
VACUUM_OVERLAY = {
    "spiral": ("07_bbh_control/bbh_control_d12_p012_t150/weyl_extraction_mode_22.dat",
               20.0, "vacuum BBH spiral", False, (65.0, 95.0), "below"),
    "fly-by": ("07_bbh_control/bbh_control_d12_p045_t100/weyl_extraction_mode_22.dat",
               20.0, "vacuum BBH fly-by", True, (10.0, 41.0), "above"),
}
# ARMS scenarios the gallery draws only as an overlay, never as a row.
OVERLAID = {"vacuum BBH twin"}

# What the gallery draws, per scenario: the last coordinate time kept at each
# sphere R, and the note written at the innermost sphere's cap.  Absent
# scenario = the whole record.  The reasons are in the module docstring.
_THROAT_END = {10.0: 58.0, 14.0: 54.0, 18.0: 52.0, 22.0: 52.0}
DRAW_GATES = {
    "collapsing throat": (lambda R: _THROAT_END[R], r"numerical floor"),
    "spiral": (lambda R: 57.0 + (R - 1.9), r"fill's light cone"),
    "fly-by": (lambda R: 50.0 + R, r"mouths expand"),
}

RAMP = [None, "MUTED", "CONTEXT", "FAINT"]   # inner -> outer; None = INK


def load(pack: pathlib.Path, rel: str, m: int | None):
    """``(t, {R: complex r*Psi4})`` or None while the stream is not packed."""
    p = pack / "campaign" / rel
    if not p.exists():
        return None
    if m is None:
        t, series = streams.load_mode(p)
        return t, dict(series)
    t, d = streams.load_l2_all(p)
    return t, {r: d[(mm, r)] for (mm, r) in d if mm == m}


def trim_zeros_tail(t: np.ndarray, y: np.ndarray):
    """Drop the run of exact zeros a gated stream writes after its cut."""
    nz = np.nonzero(np.abs(y))[0]
    if nz.size and nz[-1] < y.size - 2:
        return t[:nz[-1] + 1], y[:nz[-1] + 1]
    return t, y


def drawn(name: str, t: np.ndarray, series: dict) -> dict:
    """The records the gallery draws: zero past each sphere's DRAW_GATES end
    (so ``trim_zeros_tail`` drops the rest and the correlation ignores it)."""
    if name not in DRAW_GATES:
        return dict(series)
    end, _ = DRAW_GATES[name]
    return {R: np.where(t <= end(R) + 1e-9, y, 0.0) for R, y in series.items()}


def overlay_record(pack: pathlib.Path, name: str):
    """``(t, r*Psi4, R)`` of the vacuum control drawn under row ``name`` --
    whole, or cut to that row's drawn window where VACUUM_OVERLAY says so;
    None when the row has none or it is not packed."""
    if name not in VACUUM_OVERLAY:
        return None
    rel, R, _label, cut, _span, _side = VACUUM_OVERLAY[name]
    p = pathlib.Path(pack) / "campaign" / rel
    if not p.exists():
        return None
    t, series = streams.load_mode(p)
    y = drawn(name, t, {R: series[R]})[R] if cut else series[R]
    tt, yy = trim_zeros_tail(t, y)
    return tt, yy, R


def envelope(y: np.ndarray) -> tuple[np.ndarray, int]:
    """Amplitude envelope of r*Psi4 and how many samples of it to draw.

    A complex mode carries its own, |y|, drawn to the end.  A real one gets the
    analytic-signal modulus, the record reflected at both ends first so the
    transform does not ring at the start; but no extension knows what follows a
    cut made mid-oscillation, and past the last crest of |y| the modulus sags
    toward |y(cut)| -- a drop that is the cut's, not the wave's.  So a real
    record's envelope is drawn only to its last crest."""
    y = np.asarray(y)
    if np.abs(y.imag).max() > 1e-6 * np.abs(y.real).max():
        return np.abs(y), y.size
    x = np.real(y)
    n = x.size
    env = np.abs(hilbert(np.concatenate([x[::-1], x, x[::-1]])))[n:2 * n]
    crests, _ = find_peaks(np.abs(x))
    return env, (int(crests[-1]) + 1 if crests.size else n)


def throat_ringdown(pack: pathlib.Path):
    """Queue-2e gate 4 on its own record and window, with the pack's own
    routine: ``(t_fine, fit, period, e-fold)`` at R = 10, or None if the pack
    does not carry the run.  The routine returns (period, e-fold, f) only; the
    two linear coefficients are the exact least squares at that (f, e-fold),
    as inside the routine's own scan."""
    ana = pathlib.Path(pack) / "analysis"
    if str(ana) not in sys.path:
        sys.path.insert(0, str(ana))
    try:
        Q = importlib.import_module("queue2e_gates")
    except ImportError:
        return None
    d = Q.find_run(pathlib.Path(pack), Q.STRONG)
    if d is None:
        return None
    t, cols = Q.load(d / "psi4_mode_l2m0.dat")
    m = Q.clean(t, 10.0, Q.T_JUNK_FREE)
    tt, y = Q.after_peak(t[m], cols[10.0][m])
    got = Q.ringdown(tt, y)
    if got is None:
        return None
    period, tau, f = got

    def basis(tq):
        t0 = tq - tt[0]
        e = np.exp(-t0 / tau)
        return np.stack([e * np.cos(2 * np.pi * f * t0), e * np.sin(2 * np.pi * f * t0)], axis=1)

    coef = np.linalg.lstsq(basis(tt), y, rcond=None)[0]
    tf = np.linspace(tt[0], tt[-1], 400)
    return tf, basis(tf) @ coef, period, tau


def sci_ticks(ax, pk: float) -> None:
    """One round tick near the peak, in explicit scientific notation, so
    per-row scales cannot be misread as shared."""
    e = int(np.floor(np.log10(pk)))
    tick = np.floor(pk / 10.0 ** e) * 10.0 ** e
    mant = tick / 10.0 ** e
    body = rf"{mant:.0f}\times10^{{{e}}}" if mant != 1 else rf"10^{{{e}}}"
    ax.set_yticks([-tick, 0, tick])
    ax.set_yticklabels([rf"$-{body}$", "$0$", rf"${body}$"], fontsize=7)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack-root", default=str(PACK_ROOT))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    pack = pathlib.Path(args.pack_root).expanduser()

    rows = []
    for name, knob, mode, rel, m, R0, _t_max, _note in ARMS:
        if name in OVERLAID:
            continue
        got = load(pack, rel, m)
        if got is None:
            print(f"  {name:<18s} PENDING -- no {rel}")
            continue
        t, series = got
        series = drawn(name, t, series)
        radii = sorted(series)
        R_in = min(radii, key=lambda r: abs(r - R0))
        speeds = wavefront_speeds_xcorr(t, series, radii)
        note = DRAW_GATES[name][1] if name in DRAW_GATES else ""
        rows.append(dict(name=name, knob=knob, mode=mode, note=note, t=t,
                         series=series, radii=radii, R_in=R_in, speeds=speeds))
        ends = ", ".join(f"{trim_zeros_tail(t, series[R])[0][-1]:.1f}" for R in radii)
        print(f"  {name:<18s} {mode} R={radii}  peak = "
              f"{np.abs(series[R_in]).max():.2e}  v/c = "
              + ", ".join(f"{v:.3f}" for _, _, v, _ in speeds) + f"  drawn to t = {ends}")
    if not rows:
        raise SystemExit("no arm has a packed stream yet")
    ring = throat_ringdown(pack)
    if ring is not None:
        print(f"  ringdown fit (queue-2e gate 4, R = 10): t = {ring[0][0]:.0f}-{ring[0][-1]:.0f}, "
              f"period {ring[2]:.2f}, e-fold {ring[3]:.1f}")

    style.prd(base=10.0)
    n = len(rows)
    fig, axes = plt.subplots(n, 2, figsize=(7.05, 1.02 * n + 0.5), sharex=True,
                             constrained_layout=True,
                             gridspec_kw=dict(width_ratios=[2.0, 1.0]))
    fig.get_layout_engine().set(h_pad=0.02, hspace=0.06)
    axes = axes.reshape(n, 2)
    xlo = min(r["t"][0] - r["R_in"] for r in rows) - 3
    # The clock runs to the last drawn sample of any row OR of a control drawn
    # under one (the spiral's twin merges after the spiral's record ends).
    overlays = {r["name"]: overlay_record(pack, r["name"]) for r in rows}
    xhi = max([trim_zeros_tail(r["t"], r["series"][r["R_in"]])[0][-1] - r["R_in"]
               for r in rows]
              + [ov[0][-1] - ov[2] for ov in overlays.values() if ov is not None]) * 1.02

    for i, r in enumerate(rows):
        axL, axR = axes[i]
        t, R_in = r["t"], r["R_in"]
        tt, yy = trim_zeros_tail(t, r["series"][R_in])
        pk = np.abs(yy).max()

        # ---- left: the waveform itself ---------------------------------
        axL.axhline(0.0, color=style.FAINT, linewidth=0.6, zorder=1)
        axL.plot(tt - R_in, np.real(yy), color=style.INK, linewidth=0.9, zorder=3)
        if r["name"] == "collapsing throat" and ring is not None:
            # queue-2e gate 4's damped sinusoid, over the window it was fitted on
            axL.plot(ring[0] - R_in, ring[1], color=style.DEEP_BLUE, linewidth=1.1,
                     linestyle=(0, (3.2, 1.8)), zorder=4)
            # Named on the curve (the user, 2026-09-25): under its second
            # trough, below both the fit and the data over the name's width.
            uf = ring[0] - R_in
            kf = np.nonzero((uf > 30) & (uf < 45))[0]
            uc = uf[kf[np.argmin(ring[1][kf])]]
            near = np.abs(uf - uc) < 11.0
            neard = np.abs(tt - R_in - uc) < 11.0
            y_fit = min(ring[1][near].min(), np.real(yy[neard]).min())
            axL.text(uc, y_fit - 0.06 * pk, "ringdown fit", fontsize=6.5,
                     color=style.DEEP_BLUE, ha="center", va="top")
        ov = overlays[r["name"]]
        if ov is not None:
            # The vacuum control on the same sphere and scale, under the ink;
            # its name above the span VACUUM_OVERLAY gives it, clear of both
            # curves over the whole of it.
            to, yo, Ro = ov
            uo, ro = to - Ro, np.real(yo)
            axL.plot(uo, ro, color=style.CONTEXT, linewidth=0.9, zorder=2.5)
            _rel, _R, label, _cut, span, side = VACUUM_OVERLAY[r["name"]]
            k = (uo > span[0]) & (uo < span[1])
            ki = (tt - R_in > span[0]) & (tt - R_in < span[1])
            both = np.concatenate([ro[k], np.real(yy[ki]), [0.0]])
            if side == "above":
                y0, va = both.max() + 0.06 * pk, "bottom"
            else:
                y0, va = both.min() - 0.06 * pk, "top"
            axL.text(0.5 * sum(span), y0, label, fontsize=6.5, color=style.CONTEXT,
                     ha="center", va=va)
            print(f"  {'':<18s} over it: {VACUUM_OVERLAY[r['name']][0].split('/')[1]} at "
                  f"R={Ro:g}, peak {np.abs(yo).max():.2e} (x{pk / np.abs(yo).max():.2f} below), "
                  f"drawn to t = {to[-1]:.1f}")
        axL.set_ylim(-1.3 * pk, 1.3 * pk)
        sci_ticks(axL, pk)
        # The drawn record's end, capped -- so a shared clock cannot sell a
        # gated record as a signal that died.
        u_end = tt[-1] - R_in
        if u_end < 0.97 * xhi:
            axL.plot([u_end, u_end], [-0.35 * pk, 0.35 * pk],
                     color=style.MUTED, linewidth=0.7, zorder=2)
            if r["note"]:
                # Above the zero rule, not on it -- the rule runs the full
                # width and strikes through anything centred on it.  Where a
                # control runs on under the note, the note rises to the top of
                # its cap, over the control's swing.
                y_note = 0.12 * pk
                if ov is not None:
                    kn = (uo > u_end) & (uo < u_end + 0.2 * (xhi - xlo))
                    if kn.any():
                        y_note = max(y_note, ro[kn].max() + 0.06 * pk)
                axL.text(u_end + 0.012 * (xhi - xlo), y_note, r["note"],
                         fontsize=6.5, color=style.MUTED, ha="left", va="bottom")
        # Row identity on the strip above the frame: nothing inside the
        # panel, so no waveform can ever collide with it.
        axL.text(0.0, 1.05, f"({string.ascii_lowercase[i]})  {r['name']},  {r['knob']}",
                 transform=axL.transAxes, ha="left", va="bottom", fontsize=8,
                 color=style.INK)
        axL.text(1.0, 1.05,
                 rf"$\Psi_4^{{{r['mode'][1]},{r['mode'][3:-1]}}}$,  $R={R_in:g}$",
                 transform=axL.transAxes, ha="right", va="bottom", fontsize=8,
                 color=style.MUTED)

        # ---- right: every sphere's envelope, and the wavefront ----------
        # Envelopes on retarded time fold onto one curve when the burst
        # travels at c and falls as 1/r -- both checks in one panel.  Grey
        # ramp inner (ink) to outer (faint); gold dots where the correlated
        # front lands on each envelope.
        env = {}
        for k, R in enumerate(r["radii"]):
            tt_k, yy_k = trim_zeros_tail(t, r["series"][R])
            ee_k, n_k = envelope(yy_k)
            env[R] = (tt_k[:n_k], ee_k[:n_k])
            col = style.INK if RAMP[min(k, 3)] is None else getattr(style, RAMP[min(k, 3)])
            axR.plot(env[R][0] - R, env[R][1], color=col,
                     linewidth=1.0 if k == 0 else 0.8, zorder=3 - 0.1 * k)
        # The front: the innermost envelope's tallest INTERIOR crest,
        # advanced sphere to sphere by the correlation lags the quoted
        # speeds come from.  Interior, because a record cut mid-rise has its
        # global maximum at the truncation edge, and a dot there would mark
        # the cut, not a wavefront.  A sphere the front reaches after its
        # drawn record ends gets no dot.
        env_in = env[R_in][1]
        crests, _ = find_peaks(env_in)
        i_front = (crests[np.argmax(env_in[crests])] if crests.size
                   else int(np.argmax(env_in)))
        u_front = env[R_in][0][i_front] - R_in
        for (R1, R2, _v, resid) in [(None, r["radii"][0], None, 0.0)] + r["speeds"]:
            u_front += resid
            tt_k, ee_k = env[R2]
            t_dot = u_front + R2
            if t_dot <= tt_k[-1] + 1e-9:
                a_dot = np.interp(t_dot, tt_k, ee_k)
                # ms 4.2, not 2.6: at a two-column strip's scale the smaller
                # marker with its white rim read as a speck on the envelope.
                axR.plot(u_front, a_dot, "o", ms=4.0, color=style.GOLD,
                         markeredgecolor="white", markeredgewidth=0.6, zorder=5)
        axR.set_ylim(0, 1.18 * max(pk, max(e.max() for _, e in env.values())))
        axR.set_yticks(axL.get_yticks()[1:])   # 0 and the round tick
        axR.set_yticklabels([])                # the left panel states the scale
        axR.text(0.0, 1.05, "$v/c$ = " + ", ".join(f"{v:.2f}" for _, _, v, _ in r["speeds"]),
                 transform=axR.transAxes, ha="left", va="bottom", fontsize=7,
                 color=style.MUTED)
        axR.text(1.0, 1.05, rf"$R={r['radii'][0]:g}$--${r['radii'][-1]:g}$",
                 transform=axR.transAxes, ha="right", va="bottom", fontsize=7,
                 color=style.MUTED)

    axes[-1, 0].set_xlim(xlo, xhi)
    axes[-1, 0].set_xlabel(r"$t - R_{\mathrm{ext}}$")
    axes[-1, 1].set_xlabel(r"$t - R_{\mathrm{ext}}$")
    axes[n // 2, 0].set_ylabel(r"$r\,\mathrm{Re}\,\Psi_4^{\ell m}$")
    axes[n // 2, 1].set_ylabel(r"envelope $|r\,\Psi_4^{\ell m}|$")

    hits = style.label_audit(fig)
    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "psi4_gallery.png")
    png = style.save(fig, out)
    print(f"[gallery] wrote {png} (+pdf); {len(rows)} rows; label audit: "
          + ("clean" if not hits else f"{len(hits)} hit(s)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
