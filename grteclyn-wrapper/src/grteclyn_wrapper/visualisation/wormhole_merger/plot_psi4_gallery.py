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
         where the record ends, with the reason written beside it when the
         reason is not "the run finished";
  right  the envelope |r*Psi4| at EVERY sphere on its own retarded time,
         the correlated wavefront dotted, and the speed it travels between
         neighbouring spheres -- the discriminator that separates radiation
         (v ~ c, envelopes folding onto one curve) from a gauge or
         constraint mode wearing a wave's clothes.

    python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_psi4_gallery

SPEEDS come from ``psi4_math.wavefront_speeds_xcorr``: the lag of the whole
complex waveform between spheres, correlated over the retarded interval both
cover.  Peak-to-peak timing is what the dashboards print, and it fails here
twice over -- the BBH control's merger envelope is a ~15-unit plateau at
both spheres, so its peak times alone read v = 0.57 where the waveform lag
reads 0.82, and the spiral's outer spheres have no peak yet at all.  The
burgundy dots sit where the CORRELATED front lands on each envelope (the
innermost envelope maximum, advanced by the measured lags), so the dots and
the quoted v/c are one measurement; a sphere the front has not yet reached
inside the record gets no dot.

Rows are the ARMS table below; an arm whose stream is missing is skipped
with a note.  Amplitudes are NOT on a shared scale -- the lone throat
radiates 10x below the mergers, and one scale would flatten it to a rule --
so each row states its own scale and the right panel shares it.  The streams
already fold the extraction radius into the amplitude (r*Psi4, see
streams.py); nothing here multiplies by R again.

STYLE (the seed-branches grammar): figure* width, style.prd frame, no boxed
keys, and after 2026-09-16 review NO TEXT INSIDE THE PANELS AT ALL -- the
scenario, its knob, the mode/spheres and the speeds all sit on the strip
above each row's frames, where no waveform can collide with them --
monochrome ink with the grey ramp inner->outer on the envelopes, the
burgundy accent reserved for the wavefront, (a)-(e) tags, semantics in the
caption.
"""

from __future__ import annotations

import argparse
import pathlib
import string

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.signal import find_peaks  # noqa: E402

from grteclyn_wrapper.visualisation.wormhole_merger import streams, style  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger.psi4_math import (  # noqa: E402
    wavefront_speeds_xcorr,
)
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import PACK_ROOT, figure_dir  # noqa: E402

GROUP = "08_waves"   # cross-cutting: the figure belongs to no single group

# One row per scenario: (name, knob, mode label, stream path under campaign/,
# m or None, innermost extraction radius, t_max, end-note).  m=None means a
# single-mode file; an integer selects that m from psi4_mode_l2_all.dat.
# t_max clips the record where the run's own close-out says the stream stops
# being signal, and the end-note is written at the cap so a short row cannot
# be read as a short signal:
#   single  QUEUE2E_GATES.md junk cuts (R=10 from t=70; the gated file holds
#           zeros past each sphere's cut, trimmed per sphere below);
#   fly-by  run in flight (t = 90.5 of 200 packed 2026-09-16) AND R=14 blows
#           up when the core disturbance reaches it -- |rPsi4| crosses 0.1
#           at t = 75.5 and sits 3 orders over the burst by t = 90, while
#           R=30 stays clean throughout -- so the row is gated at t = 70;
#   spiral  record ends t = 60.4 with the freeze arm still running.
ARMS = [
    ("collapsing throat", r"$\varepsilon_2=5\times10^{-2}$", "(2,0)",
     "01_single_throat/seed/single_eps_p1e2_q5e2_ml4_t100/psi4_mode_l2m0_gated.dat",
     None, 10.0, 70.0, r"gated $t{=}70$"),
    ("head-on", r"$\sigma=-1$, $d=8$", "(2,0)",
     "04_binary_headon/merge_headon_flip_d8_v1c_latefreeze_t100/psi4_mode_l2m0.dat",
     None, 10.0, None, ""),
    ("spiral", r"$P=0.12$, $d=12$", "(2,2)",
     "05_binary_spiral/p012_paper/v2_spiral_d12_p012_L128_SERIES/Weyl4_mode_22.dat",
     None, 20.0, None, "run in flight"),
    ("fly-by", r"$P=0.45$, $d=12$", "(2,2)",
     "06_binary_flyby/p045/merge_orbit_flip_d12_p045_t200/psi4_mode_l2_all.dat",
     2, 14.0, 70.0, r"gated $t{=}70$ (run in flight)"),
    ("vacuum BBH twin", r"$P=0.12$, $d=12$", "(2,2)",
     "07_bbh_control/bbh_control_d12_p012_t150/psi4_mode_l2_all.dat",
     2, 14.0, None, ""),
]

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
    for name, knob, mode, rel, m, R0, t_max, note in ARMS:
        got = load(pack, rel, m)
        if got is None:
            print(f"  {name:<18s} PENDING -- no {rel}")
            continue
        t, series = got
        if t_max is not None:
            keep = t <= t_max + 1e-9
            t, series = t[keep], {r: y[keep] for r, y in series.items()}
        radii = sorted(series)
        R_in = min(radii, key=lambda r: abs(r - R0))
        speeds = wavefront_speeds_xcorr(t, series, radii)
        rows.append(dict(name=name, knob=knob, mode=mode, note=note, t=t,
                         series=series, radii=radii, R_in=R_in, speeds=speeds))
        print(f"  {name:<18s} {mode} R={radii}  peak = "
              f"{np.abs(series[R_in]).max():.2e}  v/c = "
              + ", ".join(f"{v:.2f}" for _, _, v, _ in speeds))
    if not rows:
        raise SystemExit("no arm has a packed stream yet")

    style.prd(base=10.0)
    n = len(rows)
    fig, axes = plt.subplots(n, 2, figsize=(7.05, 1.30 * n + 0.5), sharex=True,
                             constrained_layout=True,
                             gridspec_kw=dict(width_ratios=[2.0, 1.0]))
    axes = axes.reshape(n, 2)
    xlo = min(r["t"][0] - r["R_in"] for r in rows) - 3
    xhi = max(r["t"][-1] - r["R_in"] for r in rows) * 1.02

    for i, r in enumerate(rows):
        axL, axR = axes[i]
        t, R_in = r["t"], r["R_in"]
        y_in = r["series"][R_in]
        pk = np.abs(y_in).max()

        # ---- left: the waveform itself ---------------------------------
        axL.axhline(0.0, color=style.FAINT, linewidth=0.6, zorder=1)
        tt, yy = trim_zeros_tail(t, y_in)
        axL.plot(tt - R_in, np.real(yy), color=style.INK, linewidth=0.9, zorder=3)
        axL.set_ylim(-1.3 * pk, 1.3 * pk)
        sci_ticks(axL, pk)
        # The record's end, capped -- so a shared clock cannot sell a gated
        # or in-flight record as a signal that died.
        u_end = tt[-1] - R_in
        if u_end < 0.97 * xhi:
            axL.plot([u_end, u_end], [-0.35 * pk, 0.35 * pk],
                     color=style.MUTED, linewidth=0.7, zorder=2)
            if r["note"]:
                # Above the zero rule, not on it -- the rule runs the full
                # width and strikes through anything centred on it.
                axL.text(u_end + 0.015 * (xhi - xlo), 0.12 * pk, r["note"],
                         fontsize=6.5, color=style.MUTED, ha="left", va="bottom")
        # Row identity on the strip above the frame: nothing inside the
        # panel, so no waveform can ever collide with it.
        axL.text(0.0, 1.06, f"({string.ascii_lowercase[i]})  {r['name']},  {r['knob']}",
                 transform=axL.transAxes, ha="left", va="bottom", fontsize=8,
                 color=style.INK)
        axL.text(1.0, 1.06,
                 rf"$\Psi_4^{{{r['mode'][1]},{r['mode'][3:-1]}}}$,  $R={R_in:g}$",
                 transform=axL.transAxes, ha="right", va="bottom", fontsize=8,
                 color=style.MUTED)

        # ---- right: every sphere's envelope, and the wavefront ----------
        # Envelopes on retarded time fold onto one curve when the burst
        # travels at c and falls as 1/r -- both checks in one panel.  Grey
        # ramp inner (ink) to outer (faint); burgundy dots where the
        # correlated front lands on each envelope.
        for k, R in enumerate(r["radii"]):
            tt_k, yy_k = trim_zeros_tail(t, r["series"][R])
            col = style.INK if RAMP[min(k, 3)] is None else getattr(style, RAMP[min(k, 3)])
            axR.plot(tt_k - R, np.abs(yy_k), color=col,
                     linewidth=1.0 if k == 0 else 0.8, zorder=3 - 0.1 * k)
        # The front: the innermost envelope's tallest INTERIOR crest,
        # advanced sphere to sphere by the correlation lags the quoted
        # speeds come from.  Interior, because a record cut mid-rise (the
        # spiral) has its global maximum at the truncation edge, and a dot
        # there would mark the cut, not a wavefront.  A sphere the front
        # reaches after its record ends gets no dot.
        env_in = np.abs(yy)                     # innermost, zeros trimmed
        crests, _ = find_peaks(env_in)
        i_front = (crests[np.argmax(env_in[crests])] if crests.size
                   else int(np.argmax(env_in)))
        u_front = tt[i_front] - R_in
        for (R1, R2, _v, resid) in [(None, r["radii"][0], None, 0.0)] + r["speeds"]:
            u_front += resid
            tt_k, yy_k = trim_zeros_tail(t, r["series"][R2])
            t_dot = u_front + R2
            if t_dot <= tt_k[-1] + 1e-9:
                a_dot = np.interp(t_dot, tt_k, np.abs(yy_k))
                axR.plot(u_front, a_dot, "o", ms=2.6, color=style.BURGUNDY,
                         markeredgecolor="white", markeredgewidth=0.5, zorder=5)
        axR.set_ylim(0, 1.18 * pk)
        axR.set_yticks(axL.get_yticks()[1:])   # 0 and the round tick
        axR.set_yticklabels([])                # the left panel states the scale
        axR.text(0.0, 1.06, "$v/c$ = " + ", ".join(f"{v:.2f}" for _, _, v, _ in r["speeds"]),
                 transform=axR.transAxes, ha="left", va="bottom", fontsize=7,
                 color=style.MUTED)
        axR.text(1.0, 1.06, rf"$R={r['radii'][0]:g}$--${r['radii'][-1]:g}$",
                 transform=axR.transAxes, ha="right", va="bottom", fontsize=7,
                 color=style.MUTED)

    axes[-1, 0].set_xlim(xlo, xhi)
    axes[-1, 0].set_xlabel(r"$t - R_{\mathrm{ext}}$")
    axes[-1, 1].set_xlabel(r"$t - R_{\mathrm{ext}}$")
    axes[n // 2, 0].set_ylabel(r"$r\,\mathrm{Re}\,\Psi_4^{\ell m}$")
    axes[n // 2, 1].set_ylabel(r"$|r\,\Psi_4^{\ell m}|$")

    out = pathlib.Path(args.out) if args.out else (
        figure_dir(GROUP, args.pack_root) / "psi4_gallery.png")
    png = style.save(fig, out)
    print(f"[gallery] wrote {png} (+pdf); {len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
