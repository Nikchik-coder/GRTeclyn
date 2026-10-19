#!/usr/bin/env python3
r"""The throat instability against spin: the measured growth rate of each rung's
unstable mode, on Azad et al.'s axes (arXiv:2301.05243).

One panel.  x is the angular momentum over the throat area, J/A, as a
percentage of the extremal-Kerr limit 1/(8 pi) -- read from each rung's
background table (``meta J_over_A_extremal_frac``).  y is the dimensionless
growth rate |omega_I| sqrt(A): 1/tau from a log-linear fit of the equatorial
deficit 1 - R_eq/R_eq(0) (``throat_geometry.dat``) over the band 0.2-10 %,
times sqrt(A) with A = 4 pi R_A(0)^2 from the throat sphere's areal radius
(``throat_spheres.dat``).  A rung whose deficit never reaches the band is
stable on its window and sits at zero (open marker).

Against it, Azad et al.'s second-order rates at the ladder's middle rungs
(their tau 6.1 / 8.0 / 13 at 0.30c / 0.40c / 0.46c, the values quoted in
STATUS), and their two thresholds: the mode crossing at ~30 % of the limit,
where they conjecture the two radial modes merge and the instability dies,
and their quadratic J_c at ~50 %.

A rung is drawn when its pack (or live run dir) holds the two streams, so the
curve fills by itself as the ladder lands: rerun after each close-out.

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.plot_instability_curve
    ... plot_instability_curve --palette house

Writes ``results/spinningwormhole/figures/instability_curve`` (PNG + PDF) and
prints each rung's numbers.
"""

from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.lines as mlines  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from grteclyn_wrapper.visualisation.spinning_wormhole import solutions  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402

PACKED = solutions.REPO / "results" / "spinningwormhole" / "campaign" / "drainhole" / "00_paper_runs"
LIVE = solutions.REPO / "runs" / "spinning_wormhole" / "drainhole" / "00_paper_runs"
TABLES = solutions.REPO / "runs" / "spinning_p3" / "tables"
BACKGROUNDS = solutions.REPO / "runs" / "spinning_wormhole" / "backgrounds"
FIGURES = solutions.REPO / "results" / "spinningwormhole" / "figures"

# The ladder, slowest first.  Each rung names its background table (the x value
# comes from its meta) and its hold run; the static anchor sits at J = 0.
RUNS = (
    dict(label="0c", table=None, run="static_hold_L64_ml3_spdrv0_farfix_t100"),
    dict(label="0.2c", table=BACKGROUNDS / "full_eta2_m1_J100.spinbg",
         run="spin_hold_L64_ml3_J100_full_spdrv1_farfix_t100"),
    dict(label="0.30c", table=TABLES / "fam_a_ve030.spinbg",
         run="spin_hold_L64_ml3_ve030a_spdrv0_farfix_t100"),
    dict(label="0.40c", table=TABLES / "fam_a_ve040.spinbg",
         run="spin_hold_L64_ml3_ve040a_spdrv0_farfix_t100"),
    dict(label="0.46c", table=TABLES / "fam_a_ve045.spinbg",
         run="spin_hold_L64_ml3_ve045a_spdrv0_farfix_t100"),
    dict(label="0.5c", table=TABLES / "fam_a_ve050.spinbg",
         run="spin_hold_L64_N192_ml3_ve050a_spdrv1_farfix_t100"),
    dict(label="0.6c", table=TABLES / "fam_a_ve060.spinbg",
         run="spin_hold_L64_ml3_ve060a_spdrv0_mc4_sig04_farfix_t150"),
    dict(label="0.7c", table=TABLES / "fam_a_ve070.spinbg",
         run="spin_hold_L64_ml3_ve070a_spdrv0_mc4_sig04_farfix_t150"),
    dict(label="0.9c", table=TABLES / "fam_a_ve090.spinbg",
         run="spin_hold_L128_ml3_ve090a_spdrv1_sig04_farfix_t150"),
)

# Azad et al.'s second-order rates at the middle rungs: their tau in code
# units at our 0.30c / 0.40c / 0.46c (STATUS run matrix, 2026-10-18).
AZAD_TAU = {"0.30c": 6.1, "0.40c": 8.0, "0.46c": 13.0}
AZAD_CROSSING = 30.0      # their mode crossing: the conjectured threshold (% of extremal)
AZAD_QUADRATIC = 50.0     # their second-order J_c (% of extremal)
BAND = (2e-3, 0.1)        # the deficit band the growth rate is fitted over
SPIN_BLUE, SPIN_RED = "#1f77b4", "#d62728"
PALETTES = {
    "rgb": dict(measured=SPIN_RED, azad=SPIN_BLUE, stable="#1a1a18"),
    "house": dict(measured=style.INK, azad="#8a8a86", stable="#1a1a18"),
}


def table_frac(table) -> float:
    """J/A as a percentage of the extremal limit, from the table's meta line."""
    if table is None:
        return 0.0
    head = open(table, "rb").read(1200).decode("latin-1")
    key = "meta J_over_A_extremal_frac "
    return 100.0 * float(head[head.index(key) + len(key):].split()[0])


def streams(run: str):
    """The run's throat geometry and spheres, packed first, else live."""
    for base in (PACKED, LIVE):
        g = base / run / "throat_geometry.dat"
        s = (base / run / "throat_spheres.dat"
             if base is PACKED else base / run / "small_data" / "throat_spheres.dat")
        if g.exists() and s.exists():
            return np.loadtxt(g, ndmin=2), np.loadtxt(s, ndmin=2)
    return None, None


def measure(run: str):
    """(R_A(0), tau, fit band, flatness): tau is None where the deficit never
    enters the band -- stable on the run's window."""
    g, s = streams(run)
    if g is None or g.shape[0] < 20:
        return None
    t, d = g[:, 0], 1.0 - g[:, 1] / g[0, 1]
    r_a = s[0, 2]
    sel = (d >= BAND[0]) & (d <= BAND[1])
    if sel.sum() < 5:
        return dict(r_a=r_a, tau=None, span=None, flat=float(np.nanmax(np.abs(d))), t_end=t[-1])
    slope = np.polyfit(t[sel], np.log(d[sel]), 1)[0]
    return dict(r_a=r_a, tau=1.0 / slope, span=(t[sel][0], t[sel][-1]),
                flat=None, t_end=t[-1])


def rate(tau: float, r_a: float) -> float:
    """|omega_I| sqrt(A) = sqrt(4 pi) R_A / tau."""
    return np.sqrt(4.0 * np.pi) * r_a / tau


def draw(points, pal) -> None:
    fig, ax = plt.subplots(figsize=(4.0, 3.0), layout="constrained")
    for x, tag, y, ha, dx in ((AZAD_CROSSING, "merger conjecture, 30 %", 0.25, "right", -1.2),
                              (AZAD_QUADRATIC, "quadratic $J_c$, 50 %", 0.40, "left", 1.2)):
        ax.axvline(x, color="#b5b5b2", lw=0.8, ls=":")
        ax.text(x + dx, y, tag, fontsize=6.0, color="#8a8a86", va="top", ha=ha)
    az_x = [p["frac"] for p in points if p["label"] in AZAD_TAU and p["r_a"]]
    az_y = [rate(AZAD_TAU[p["label"]], p["r_a"]) for p in points
            if p["label"] in AZAD_TAU and p["r_a"]]
    ax.plot(az_x, az_y, "D", ms=4.5, mfc="none", mec=pal["azad"], mew=1.1, zorder=3)
    for p in points:
        if p["r_a"] is None:
            continue
        if p["tau"] is not None:
            ax.plot(p["frac"], rate(p["tau"], p["r_a"]), "o", ms=5.0,
                    color=pal["measured"], zorder=4)
            ax.annotate(f"{p['label']}\n$\\tau$ {p['tau']:.1f}",
                        (p["frac"], rate(p["tau"], p["r_a"])),
                        textcoords="offset points", xytext=(6, -12), fontsize=6.5)
        else:
            ax.plot(p["frac"], 0.0, "o", ms=5.5, mfc="none", mec=pal["stable"],
                    mew=1.2, zorder=4)
            ax.annotate(f"{p['label']}: flat to t {p['t_end']:.0f}",
                        (p["frac"], 0.0), textcoords="offset points",
                        xytext=(-4, 7), fontsize=6.5, ha="right")
    ax.set_xlim(0.0, 100.0)
    ax.set_ylim(-0.12, 2.6)
    ax.set_xlabel(r"$J/A$, % of the extremal limit $1/8\pi$")
    ax.set_ylabel(r"growth rate $|\omega_I|\sqrt{A}$")
    entries = [
        (mlines.Line2D([], [], marker="o", ls="none", ms=5, color=pal["measured"]),
         "measured ($R_{\\mathrm{eq}}$ deficit fit)"),
        (mlines.Line2D([], [], marker="o", ls="none", ms=5.5, mfc="none",
                       mec=pal["stable"], mew=1.2), "stable on its window"),
    ]
    if az_x:
        entries.append((mlines.Line2D([], [], marker="D", ls="none", ms=4.5, mfc="none",
                                      mec=pal["azad"], mew=1.1), "Azad et al., 2nd order"))
    style.legend_top(ax, entries, ncol=1, borderpad=0.6)
    for ext in ("png", "pdf"):
        fig.savefig(FIGURES / f"instability_curve.{ext}", dpi=300)
    bad = style.label_audit(fig)
    print("label audit:", bad if bad else "clean")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--palette", choices=sorted(PALETTES), default="rgb")
    args = ap.parse_args()
    points, pending = [], []
    for rung in RUNS:
        m = measure(rung["run"])
        if m is None:
            pending.append(rung["label"])
            continue
        points.append(dict(label=rung["label"], frac=table_frac(rung["table"]), **m))
    for p in points:
        if p["tau"] is not None:
            print(f"{p['label']:6s} J/A {p['frac']:5.1f} %  R_A {p['r_a']:.3f}  "
                  f"tau {p['tau']:6.2f} (fit t {p['span'][0]:.1f}-{p['span'][1]:.1f})  "
                  f"rate {rate(p['tau'], p['r_a']):.3f}")
        else:
            print(f"{p['label']:6s} J/A {p['frac']:5.1f} %  R_A {p['r_a']:.3f}  "
                  f"stable: |deficit| <= {p['flat']:.1e} to t {p['t_end']:.0f}")
    if pending:
        print("pending rungs (no data yet):", ", ".join(pending))
    draw(points, PALETTES[args.palette])
    print("wrote", FIGURES / "instability_curve.png")


if __name__ == "__main__":
    main()
