#!/usr/bin/env python3
"""Audit of the waveform gallery (article Fig. 10, plot_psi4_gallery): what
grows in the right-hand column, on which sphere, and why.

Reads only the tracked pack (results/merger/campaign) through the gallery's own
ARMS table and loaders, so every number here is the figure's.  Prints a report;
writes nothing.

    grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/analysis/merger_feedback/waves_gallery_audit.py

Sections
  A  per row and sphere: the record, its |r Psi4| maximum and where it sits in
     retarded time, whether an m = 0 mode is real (then |r Psi4| is the
     rectified wave, not an envelope);
  B  the correlated-lag speeds (psi4_math.wavefront_speeds_xcorr) as the ledger
     computes them, and under the gates a clean record would use;
  C  contamination clocks per row: the lone throat's numerical floor (level-3
     and level-4 spherical controls), the head-on against its level-5 twin,
     the spiral's grid-scale noise and the fill's causal clock, the fly-by's
     trough (burst meets contaminant) per sphere, the vacuum twin's junk;
  D  the vacuum twin's peak timing against its lag.
"""

from __future__ import annotations

import pathlib

import numpy as np
from scipy.signal import butter, hilbert, sosfiltfilt

from grteclyn_wrapper.visualisation.wormhole_merger import plot_psi4_gallery as G
from grteclyn_wrapper.visualisation.wormhole_merger import streams
from grteclyn_wrapper.visualisation.wormhole_merger.psi4_math import wavefront_speeds_xcorr
from grteclyn_wrapper.visualisation.wormhole_merger.run_tree import PACK_ROOT

PACK = PACK_ROOT
CAMP = PACK / "campaign"
SEED = CAMP / "01_single_throat" / "seed"


def arms():
    out = {}
    for name, knob, mode, rel, m, R0, t_max, note in G.ARMS:
        got = G.load(PACK, rel, m)
        t, s = got
        out[name] = dict(rel=rel, mode=mode, R0=R0, t_max=t_max, t=t, s=s)
    return out


def uniform(t, y, dt):
    tu = np.arange(t[0], t[-1] + 1e-9, dt)
    return tu, np.interp(tu, t, y.real) + 1j * np.interp(tu, t, y.imag)


def hf_rms(t, y, fc=0.25, win=2.0):
    """Rolling rms (over `win` units) of the part of y above fc (1/M)."""
    dt = float(np.median(np.diff(t)))
    sos = butter(4, fc, fs=1.0 / dt, output="sos")
    lo = sosfiltfilt(sos, y.real) + 1j * sosfiltfilt(sos, y.imag)
    h = y - lo
    w = max(1, int(round(win / dt)))
    return np.sqrt(np.convolve(np.abs(h) ** 2, np.ones(w) / w, mode="same"))


def speeds(t, s, radii=None):
    radii = sorted(s) if radii is None else radii
    return [(a, b, v) for a, b, v, _ in wavefront_speeds_xcorr(t, s, radii)]


def fmt_sp(sp):
    return "  ".join(f"{a:g}->{b:g}: {v:.3f}" for a, b, v in sp)


def gate_coord(t, s, t_max):
    keep = t <= t_max + 1e-9
    return t[keep], {R: y[keep] for R, y in s.items()}


def gate_retarded(t, s, u_max):
    """Zero every sphere past u = t - R > u_max (same retarded window at all spheres)."""
    return t, {R: np.where(t - R <= u_max + 1e-9, y, 0.0) for R, y in s.items()}


def section_a(A):
    print("\n=== A. records, maxima, reality of the m = 0 rows")
    for name, a in A.items():
        t, s = a["t"], a["s"]
        if a["t_max"] is not None:
            t, s = gate_coord(t, s, a["t_max"])
        print(f"-- {name} {a['mode']}  t = {t[0]:.2f}-{t[-1]:.2f}  n = {t.size}  "
              f"gate t_max = {a['t_max']}")
        for R in sorted(s):
            tt, yy = G.trim_zeros_tail(t, s[R])
            e = np.abs(yy)
            i = int(np.argmax(e))
            re_ratio = np.abs(yy.imag).max() / max(np.abs(yy.real).max(), 1e-300)
            extra = ""
            if a["mode"] == "(2,0)":
                env = np.abs(hilbert(yy.real))
                extra = f"  analytic-envelope max {env.max():.3e} at u = {tt[np.argmax(env)] - R:.2f}"
            print(f"   R = {R:4g}: last t {tt[-1]:7.2f} (u {tt[-1] - R:6.2f})  max|y| {e[i]:.3e} "
                  f"at t = {tt[i]:.2f} (u = {tt[i] - R:.2f})  max|Im|/max|Re| = {re_ratio:.1e}{extra}")


def section_b(A):
    print("\n=== B. correlated-lag speeds under different gates")
    for name, a in A.items():
        t, s = a["t"], a["s"]
        radii = sorted(s)
        R_in = min(radii, key=lambda r: abs(r - a["R0"]))
        print(f"-- {name}")
        if a["t_max"] is not None:
            tg, sg = gate_coord(t, s, a["t_max"])
            print(f"   ledger (coordinate gate t <= {a['t_max']:g}): {fmt_sp(speeds(tg, sg))}")
            u_max = a["t_max"] - R_in
            tr, sr = gate_retarded(t, s, u_max)
            print(f"   retarded gate u <= {u_max:g} at every sphere:     {fmt_sp(speeds(tr, sr))}")
        else:
            print(f"   ledger (whole record):                          {fmt_sp(speeds(t, s))}")
        if name == "spiral":
            # the fill's causal clock t = 57 + (R - 1.9): past it the record is
            # the frozen core's transport
            for u_max in (55.1, 50.0, 45.0):
                tr, sr = gate_retarded(t, s, u_max)
                print(f"   retarded gate u <= {u_max:g}:                        {fmt_sp(speeds(tr, sr))}")
        if name == "head-on":
            for u_max in (75.0, 70.0, 60.0):
                tr, sr = gate_retarded(t, s, u_max)
                print(f"   retarded gate u <= {u_max:g}:                        {fmt_sp(speeds(tr, sr))}")
        if name == "collapsing throat":
            # the queue-2e per-sphere junk cuts are already zeros in the gated file;
            # also try the floor-limited window
            for u_max in (45.0, 40.0, 35.0):
                tg, sg = gate_coord(t, s, a["t_max"])
                tr, sr = gate_retarded(tg, sg, u_max)
                print(f"   + retarded gate u <= {u_max:g}:                      {fmt_sp(speeds(tr, sr))}")


def first_cross(t, y, thr, t_from=None):
    m = np.nonzero(y > thr)[0]
    if t_from is not None:
        m = m[t[m] >= t_from]
    return float(t[m[0]]) if m.size else None


def section_c(A):
    print("\n=== C. contamination clocks")
    # ---- lone throat: the floor, level 3 and level 4 --------------------------
    a = A["collapsing throat"]
    pk = np.abs(a["s"][10.0][a["t"] <= 70]).max()
    print(f"-- collapsing throat: burst peak at R = 10 = {pk:.3e}")
    ctl3_t, ctl3 = streams.load_mode(SEED / "single_eps_p1e2_t100" / "psi4_mode_l2m0.dat")
    ctl4_t, ctl4 = streams.load_mode(SEED / "single_eps_p1e2_q1e2_ml4_scalar_t100" / "psi4_mode_l2m0.dat")
    raw_t, raw = streams.load_mode(SEED / "single_eps_p1e2_q5e2_ml4_t100" / "psi4_mode_l2m0.dat")
    print("   floor = max |r Psi4^20| of the spherical +0.01 control in each window "
          "(L3 = single_eps_p1e2_t100, level 3, R = 14/30; "
          "L4 = single_eps_p1e2_q1e2_ml4_scalar_t100, level 4, seed NOT applied = exact level-4 control)")
    for lo, hi in ((0, 30), (30, 40), (40, 50), (50, 55), (55, 60), (60, 65), (65, 70), (70, 80)):
        row = [f"   t = {lo:3d}-{hi:3d}"]
        for lab, tt, ss in (("L3", ctl3_t, ctl3), ("L4", ctl4_t, ctl4)):
            m = (tt >= lo) & (tt < hi)
            row.append(lab + " " + " ".join(f"R{R:g} {np.abs(ss[R][m]).max():.1e}" for R in sorted(ss)))
        m = (raw_t >= lo) & (raw_t < hi)
        row.append("arm " + " ".join(f"R{R:g} {np.abs(raw[R][m]).max():.1e}" for R in sorted(raw)))
        print("  |  ".join(row))
    for frac in (0.1, 0.3, 1.0):
        row = []
        for R in sorted(ctl4):
            row.append(f"R{R:g} t={first_cross(ctl4_t, np.abs(ctl4[R]), frac * pk)}")
        print(f"   level-4 floor first exceeds {frac:.0%} of the burst peak: " + ", ".join(row))
    # the strong arm minus the exact level-4 control: is the late junk common?
    for R in sorted(ctl4):
        n = min(raw_t.size, ctl4_t.size)
        d = raw[R][:n] - ctl4[R][:n]
        for lo, hi in ((55, 60), (60, 65), (65, 70), (70, 80), (80, 100)):
            m = (raw_t[:n] >= lo) & (raw_t[:n] < hi)
            print(f"   R = {R:g} t = {lo}-{hi}: max|arm| {np.abs(raw[R][:n][m]).max():.2e}  "
                  f"max|control| {np.abs(ctl4[R][:n][m]).max():.2e}  max|arm - control| {np.abs(d[m]).max():.2e}")

    # ---- head-on: level 3 (the gallery's V1c) against the clean level-5 arm ----
    print("-- head-on: gallery stream (V1c, level 3, core frozen from t = 26.5) vs the level-5 "
          "no-fill arm (in-code Weyl4, the text's source)")
    a = A["head-on"]
    t5, s5 = streams.load_mode(CAMP / "04_binary_headon" / "merge_headon_flip_d8_v1_lvl5from0_scalar_t100" /
                               "Weyl4_mode_20.dat")
    for R in sorted(a["s"]):
        y5 = np.interp(a["t"], t5, s5[R].real)
        d = np.abs(a["s"][R].real - y5) / np.abs(s5[R]).max()
        for thr in (0.01, 0.03, 0.1):
            tc = first_cross(a["t"], d, thr)
            print(f"   R = {R:g}: |V1c - L5| first exceeds {thr:.0%} of peak at t = {tc}"
                  + (f" (u = {tc - R:.0f})" if tc is not None else ""))

    # ---- spiral: grid-scale noise and the fill's clock ------------------------
    print("-- spiral: grid-scale noise (|r Psi4| above f = 0.25/M, 2-unit rolling rms) "
          "and the fill's causal clock t = 57 + (R - 1.9)")
    a = A["spiral"]
    tu, _ = uniform(a["t"], a["s"][20.0], 0.01)
    pk = np.abs(a["s"][20.0]).max()
    for R in sorted(a["s"]):
        _, yu = uniform(a["t"], a["s"][R], 0.01)
        r = hf_rms(tu, yu)
        cl = 57.0 + R - 1.9
        c = [first_cross(tu, r / pk, thr, t_from=3.0) for thr in (1e-3, 3e-3, 1e-2, 3e-2)]
        i = np.searchsorted(tu, cl)
        print(f"   R = {R:g}: HF/peak first > 1e-3 / 3e-3 / 1e-2 / 3e-2 at t = "
              + " / ".join("-" if x is None else f"{x:.1f}" for x in c)
              + f";  at the fill clock t = {cl:.1f} (u = {cl - R:.1f}) HF/peak = {r[i] / pk:.1e};"
              f"  max HF/peak to t = 100: {r.max() / pk:.1e}")
        # dominant frequency of the late noise
        m = tu >= max(cl, 60.0)
        if m.sum() > 400:
            sos = butter(4, 0.25, fs=100.0, output="sos")
            h = yu[m] - (sosfiltfilt(sos, yu[m].real) + 1j * sosfiltfilt(sos, yu[m].imag))
            F = np.abs(np.fft.fft(h * np.hanning(h.size))) ** 2
            f = np.fft.fftfreq(h.size, 0.01)
            print(f"            late-noise dominant |f| = {abs(f[np.argmax(F)]):.2f} /M")

    # ---- fly-by: where the burst meets the contaminant, per sphere ------------
    print("-- fly-by: per-sphere burst peak and trough (min |r Psi4| after the peak, "
          "where the growing contaminant equals the decaying burst), whole record to t = 100")
    a = A["fly-by"]
    t, s = a["t"], a["s"]
    for R in sorted(s):
        e = np.abs(s[R])
        # burst peak: max over u <= 45 (the burst is at u ~ 34.5 on every sphere)
        mb = (t - R) <= 45.0
        ip = int(np.argmax(np.where(mb, e, -1)))
        after = np.arange(t.size) > ip
        it = int(np.argmin(np.where(after, e, np.inf)))
        mu = (t - R) <= 50.0
        print(f"   R = {R:g}: burst peak {e[ip]:.3e} at t = {t[ip]:.2f} (u = {t[ip] - R:.2f});  "
              f"trough {e[it]:.3e} at t = {t[it]:.2f} (u = {t[it] - R:.2f});  "
              f"|y| at record end {e[-1]:.3e} ({e[-1] / e[ip]:.2f} x burst);  "
              f"coordinate gate t <= 70 keeps u <= {70 - R:.0f}"
              f"{' -- CUTS THE BURST PEAK' if t[ip] > 70 else ''};  retarded gate u <= 50 ends at "
              f"t = {50 + R:.0f}, |y| there {e[np.argmin(abs(t - (50 + R)))]:.3e} "
              f"(trough {'after' if t[it] - R > 50 else 'BEFORE'} the gate)")
    tu, _ = uniform(t, s[20.0], 0.01)
    for R in sorted(s):
        _, yu = uniform(t, s[R], 0.01)
        r = hf_rms(tu, yu)
        pkR = np.abs(yu[(tu - R) <= 45]).max()
        m = (tu - R) <= 50
        print(f"   R = {R:g}: grid-scale noise within u <= 50: max HF rms / burst peak = "
              f"{r[m].max() / pkR:.1e}")

    # ---- vacuum twin ----------------------------------------------------------
    a = A["vacuum BBH twin"]
    t, s = a["t"], a["s"]
    print("-- vacuum BBH twin (m = 2): junk and merger")
    for R in sorted(s):
        e = np.abs(s[R])
        early = (t - R) <= 30
        print(f"   R = {R:g}: initial-data junk max (u <= 30) {e[early].max():.3e};  merger max "
              f"{e.max():.3e} at t = {t[np.argmax(e)]:.1f} (u = {t[np.argmax(e)] - R:.1f});  "
              f"plateau above 95 % of max: u = {t[e >= 0.95 * e.max()][0] - R:.1f}-"
              f"{t[e >= 0.95 * e.max()][-1] - R:.1f}")


def section_d(A):
    a = A["vacuum BBH twin"]
    t, s = a["t"], a["s"]
    R1, R2 = sorted(s)
    t1 = t[np.argmax(np.abs(s[R1]))]
    t2 = t[np.argmax(np.abs(s[R2]))]
    print("\n=== D. vacuum twin: peak timing vs correlated lag")
    print(f"   peak times t = {t1:.1f} (R = {R1:g}) and {t2:.1f} (R = {R2:g}): "
          f"v = {(R2 - R1) / (t2 - t1):.3f};  correlated lag: {fmt_sp(speeds(t, s))}")


def main():
    A = arms()
    section_a(A)
    section_b(A)
    section_c(A)
    section_d(A)


if __name__ == "__main__":
    main()
