#!/usr/bin/env python3
r"""The throat instability against spin: the measured growth rate of each rung's
unstable mode, on Azad et al.'s axes (arXiv:2301.05243).

One panel.  x is the angular momentum over the throat area, J/A, as a
percentage of the extremal-Kerr limit 1/(8 pi) -- read from each rung's
background table header (``meta J_over_A_extremal_frac``; tracked under
``results/spinningwormhole/backgrounds/``, see ``headers``).  y is the growth rate
1/tau in code units; the right edge relabels the same scale in tau.

tau is measured the same way on every rung (decided 2026-10-19, after the
throat-radius check): a log-linear fit of the areal-radius deficit
1 - R_A(t)/R_A(0) (``throat_spheres.dat``, the minimal coordinate sphere) on
its first pass through 0.2-1 %, the band every rung crosses (the 0.5c reaches
1.3 % by t 100).  The areal radius is the size of the l = 0 mode Azad et al.
compute.  Two choices move tau and are printed, not drawn: the equatorial
radius (``throat_geometry.dat``) runs 10-30 % slower at 0.46c-0.5c, and a
wider band lengthens tau as the collapse turns nonlinear (0.2c: 5.0 over
0.2-1 %, 6.5 over 1-10 %).  The MOTS (``mots_spectral.dat``) is printed as
a check: it sits on the throat through the band.  A rung is drawn once its
deficit has crossed the band on either side; a finished run that never enters
it is stable on its window and sits at zero (open marker).

The mode has two fates, one rate (10-20).  A rung whose radius grows through
the +0.2-1 % band is on the inflating branch (the 0.46c after a -1.1 % swing,
the 0.5c N 128 directly); its tau comes from ln |dR_A/dt| fitted over that
band -- dR/dt is offset-free, so the fit stands although the mode grows atop
the swing's finite radius, and on a pure exponential it equals the
deficit-band fit.  Inflating rungs draw as triangles and join the fit: the
same unstable mode, the seed's sign picking the side (the kicks' rule).

Against it, Azad et al.'s second-order rate for this family (their C = 1
row: |omega_I| eta0 = 0.390 - 0.384 (J/eta0^2)^2) at every rung where it is
positive, and two rules: where that rate vanishes on this axis (J_c 4.03,
33 %; their "about 50 %" uses their second-order throat area), and their
conjectured end of the instability, about 30 %.

A rung is drawn when its pack (or live run dir) holds the streams, so the
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

from grteclyn_wrapper.visualisation.spinning_wormhole import headers, solutions  # noqa: E402
from grteclyn_wrapper.visualisation.wormhole_merger import style  # noqa: E402

PACKED = solutions.REPO / "results" / "spinningwormhole" / "campaign" / "drainhole" / "00_paper_runs"
LIVE = solutions.REPO / "runs" / "spinning_wormhole" / "drainhole" / "00_paper_runs"
FIGURES = solutions.REPO / "results" / "spinningwormhole" / "figures"

# The ladder, slowest first.  Each rung names its background table (x and J
# come from its packed header) and its hold run; the static anchor sits at J = 0.
# The L 64 rungs are the N 128 paper runs; the 0.5c exists at N 192 only.
RUNS = (
    dict(label="D0", table=None, run="static_hold_L64_ml3_spdrv0_farfix_t100"),
    dict(label="D21", table="full_eta2_m1_J100",
         run="spin_hold_L64_ml3_J100_full_spdrv1_farfix_t100"),
    dict(label="D30", table="fam_a_ve030",
         run="spin_hold_L64_ml3_ve030a_spdrv0_farfix_t100"),
    dict(label="D40", table="fam_a_ve040",
         run="spin_hold_L64_ml3_ve040a_spdrv0_farfix_t100"),
    # 10-20: the 0.46c / 0.5c point at their t 150 / N 128 runs (both inflate).  The
    # 0.6c / 0.7c point at their L 128 runs with min_chi 1e-8: with the fast recipe's
    # 1e-4 the floor rewrote the negative-mass far side's centre and the throat's late
    # motion was numerical (the 0.5c / 0.6c L 128 DIED 84.81 / 99.16, the 0.7c was
    # stopped at 107.65).
    dict(label="D46", table="fam_a_ve045",
         run="spin_hold_L64_ml3_ve045a_spdrv0_farfix_t150"),
    dict(label="D51", table="fam_a_ve050",
         run="spin_hold_L64_ml3_ve050a_spdrv0_farfix_t150"),
    dict(label="D59", table="fam_a_ve060",
         run="spin_hold_L128_ml3_ve060a_spdrv1_sig04_mc8_farfix_t150"),
    dict(label="D70", table="fam_a_ve070",
         run="spin_hold_L128_ml3_ve070a_spdrv1_sig04_mc8_farfix_t150"),
    dict(label="D90", table="fam_a_ve090",
         run="spin_hold_L128_ml3_ve090a_spdrv1_sig04_farfix_t150"),
)

# Azad et al.'s second-order unstable mode for this family (their C = 1 row,
# Table 1): |omega_I| eta0 = W0 - DW2 (J/eta0^2)^2, eta0 = 2 here.
AZAD_W0, AZAD_DW2, ETA0 = 0.390, 0.384, 2.0
AZAD_CONJECTURE = 30.0    # their conjectured end of the instability (% of extremal)
BAND = (2e-3, 1e-2)       # the deficit band every rung's tau is fitted over
WIDE_BANDS = ((3e-3, 3e-2), (1e-2, 1e-1))   # printed for comparison only
# Per-rung tag offsets (points) and anchors: above-right where the falling fit
# leaves that side free, below-left where a tag there would reach the rules.
TAG_SIDES = {
    "D0": (4, 11, "left", "bottom"),
    "D21": (-6, -9, "right", "top"),
    "D30": (-5, -4, "right", "top"),
    "D40": (-10, -9, "right", "top"),
    "D46": (12, 0, "left", "center"),
}
SPIN_BLUE, SPIN_RED = "#1f77b4", "#d62728"
PALETTES = {
    "rgb": dict(measured=SPIN_RED, azad=SPIN_BLUE, stable="#1a1a18"),
    "house": dict(measured=style.INK, azad="#8a8a86", stable="#1a1a18"),
}


def table_meta(table) -> tuple[float, float]:
    """(J, J/A as a percentage of the extremal limit) from the table's packed header."""
    if table is None:
        return 0.0, 0.0
    meta = headers.meta(table)
    return float(meta["J"]), 100.0 * float(meta["J_over_A_extremal_frac"])


def azad_rate(j: float) -> float:
    """Azad et al.'s second-order growth rate 1/tau at angular momentum J."""
    return (AZAD_W0 - AZAD_DW2 * (j / ETA0 ** 2) ** 2) / ETA0


def streams(run: str):
    """The run's spheres, geometry and MOTS streams (packed first, else live),
    and whether the run has ended; None when it has no spheres yet."""
    for base, data, small in ((PACKED, "", ""), (LIVE, "data", "small_data")):
        spheres = base / run / small / "throat_spheres.dat"
        if not spheres.exists():
            continue
        geom = base / run / data / "throat_geometry.dat"
        mots = base / run / small / "mots_spectral.dat"
        log = base / run / "run.log"
        ended = base is PACKED or (log.exists() and "finalized" in log.read_text()[-4000:])
        return dict(
            spheres=np.loadtxt(spheres, ndmin=2),
            geom=np.loadtxt(geom, ndmin=2) if geom.exists() else None,
            mots=np.genfromtxt(mots, invalid_raise=False) if mots.exists() else None,
            ended=ended)
    return None


def rate_tau(t, radius, band=BAND, collapse=False):
    """tau of the offset-free fit, both branches: ln |d(R/R(0))/dt| fitted over
    the first span where the areal deficit 1 - R/R(0) (collapse) or the growth
    R/R(0) - 1 (expansion) rises through the band.  dR/dt carries no offset, so
    neither the early transient (collapse) nor the turn's finite radius
    (expansion) biases the slope; on a pure exponential it equals a log-linear
    fit of the deficit itself.  2026-10-20: the deficit-band fit, used for the
    collapse side until now, inherits the transient's offset, which is larger
    at lower resolution (1e-4 at N 96 against 4e-6 at N 192) and steepens the
    slope -- it failed to self-converge on the D21 triplet (Q_meas < 0), while
    this fit gives tau 7.8 / 6.6 / 6.1 there, Q_meas 2.3 between the order-3/4
    expectations 1.95 and 2.69.  (None, max |deviation|) while the band is not
    crossed."""
    ok = np.isfinite(radius) & (radius > 0)
    t, radius = t[ok], radius[ok]
    if t.size < 5:
        return None, 0.0
    g = 1.0 - radius / radius[0] if collapse else radius / radius[0] - 1.0
    above = np.flatnonzero(g > band[1])
    if above.size == 0:
        return None, float(np.max(np.abs(g)))
    sel = np.flatnonzero(g[:above[0]] >= band[0])
    if sel.size < 4:
        return None, float(np.max(np.abs(g)))
    v = np.gradient(radius, t) / radius[0]
    tt, vv = t[sel], (-v[sel] if collapse else v[sel])
    if np.any(vv <= 0):
        return None, float(np.max(np.abs(g)))
    return 1.0 / np.polyfit(tt, np.log(vv), 1)[0], (tt[0], tt[-1])


def measure(run: str):
    """The rung's tau from the areal radius (None while its deficit has not
    crossed a band on either side), its branch, and the printed comparisons."""
    s = streams(run)
    if s is None or s["spheres"].shape[0] < 5:
        return None
    sph = s["spheres"]
    tau, span = rate_tau(sph[:, 0], sph[:, 2], collapse=True)
    g_tau, g_span = rate_tau(sph[:, 0], sph[:, 2])
    m = dict(r_a=sph[0, 2], t_end=sph[-1, 0], ended=s["ended"], tau_shrink=tau)
    if g_tau is not None:
        # the terminal behaviour wins: a shrink that turned and grew through the
        # band is the inflating branch (0.46c: -1.1 % at t 83, +1 % at t 107)
        m.update(tau=g_tau, span=g_span, branch="inflates", flat=None)
    elif tau is not None:
        m.update(tau=tau, span=span, branch="collapses", flat=None)
    else:
        m.update(tau=None, span=None, branch=None, flat=span)
    m["stable"] = m["tau"] is None and s["ended"] and abs(m["flat"]) < BAND[0]
    m["tau_eq"] = (rate_tau(s["geom"][:, 0], s["geom"][:, 1], collapse=True)[0]
                   if s["geom"] is not None else None)
    m["tau_mots"] = (rate_tau(s["mots"][:, 0], s["mots"][:, 1], collapse=True)[0]
                     if s["mots"] is not None and s["mots"].ndim == 2 else None)
    m["tau_wide"] = [rate_tau(sph[:, 0], sph[:, 2], b, collapse=True)[0] for b in WIDE_BANDS]
    return m


def rate(tau: float) -> float:
    """The growth rate 1/tau, code units."""
    return 1.0 / tau


def fit_zero(points, key="tau"):
    """Azad's form through the collapse branch, rate = a - b (J/A)^2: (a, b, the
    zero sqrt(a/b) or None).  2026-10-20: the collapse branch alone -- with the
    offset-free rates it follows the parabola to rms 2e-3 and dies at 32 %,
    beside the second-order zero (33 %), while the expansion rates RISE with
    spin past the crossing; one curve through both branches described neither."""
    pts = [p for p in points if p.get(key) is not None and p.get("branch") == "collapses"]
    if len(pts) < 2:
        return None
    mx = np.array([p["frac"] for p in pts])
    my = np.array([rate(p[key]) for p in pts])
    b, a = np.linalg.lstsq(np.stack([-mx ** 2, np.ones_like(mx)], 1), my, rcond=None)[0]
    return a, b, (float(np.sqrt(a / b)) if b > 0 else None)


def azad_jc_frac(points) -> float | None:
    """Where Azad's second-order rate vanishes on this axis: J_c = eta0^2
    sqrt(W0/DW2), mapped to J/A along the family's tables."""
    jc = ETA0 ** 2 * np.sqrt(AZAD_W0 / AZAD_DW2)
    js = np.array([p["j"] for p in points])
    xs = np.array([p["frac"] for p in points])
    if js.size < 2 or js.max() < jc:
        return None
    order = np.argsort(js)
    return float(np.interp(jc, js[order], xs[order]))


def draw(points, pal, jc_frac) -> None:
    style.prd(8.0)
    # 2026-10-20: the house typography (it drew in matplotlib's default sans), at the
    # column width it is printed at; 2.3 in tall since its key went to two columns
    fig, ax = plt.subplots(figsize=(3.4, 2.3), layout="constrained")
    # The two thresholds are named in the key, not inside the frame (their
    # in-frame tags kept colliding with the rules and the fit, 2026-10-19).
    rules = [AZAD_CONJECTURE] + ([jc_frac] if jc_frac else [])
    for x in rules:
        ax.axvline(x, color="#b5b5b2", lw=0.8, ls=":")
    drawn = [p for p in points if p["tau"] is not None or p["stable"]]
    az = [(p["frac"], azad_rate(p["j"])) for p in drawn if azad_rate(p["j"]) > 0]
    if az:
        # Open diamonds over smaller dots: where a rung matches Azad the dot
        # shows inside its diamond instead of hiding it.
        ax.plot(*zip(*az), "D", ms=6.5, mfc="none", mec=pal["azad"], mew=1.0, zorder=5)
    fit = fit_zero(drawn)
    x0 = None
    if fit is not None:
        a, b, x0 = fit
        xs = np.linspace(0.0, x0 if x0 else 100.0, 400)
        fit_line, = ax.plot(xs, np.clip(a - b * xs ** 2, 0.0, None), ls="--",
                            lw=1.0, color=pal["measured"], zorder=2)
    for p in drawn:
        if p["tau"] is not None:
            # one rate, two fates: the collapsing branch is the dot, the
            # inflating branch the triangle (10-20: the 0.46c and 0.5c grow)
            ax.plot(p["frac"], rate(p["tau"]), "^" if p["branch"] == "inflates" else "o",
                    ms=4.6 if p["branch"] == "inflates" else 3.8,
                    color=pal["measured"], zorder=4)
            dx, dy, ha, va = TAG_SIDES.get(p["label"], (5, 3, "left", "bottom"))
            ax.annotate(p["label"],
                        (p["frac"], rate(p["tau"])),
                        textcoords="offset points", xytext=(dx, dy), fontsize=6.5,
                        ha=ha, va=va)
        else:
            ax.plot(p["frac"], 0.0, "o", ms=5.5, mfc="none", mec=pal["stable"],
                    mew=1.2, zorder=4)
            ax.annotate(f"{p['label']}: flat to $t={p['t_end']:.0f}$",
                        (p["frac"], 0.0), textcoords="offset points",
                        xytext=(0, 7), fontsize=6.5, ha="center", va="bottom")
    ax.set_xlim(-2.0, 100.0)   # the static rung sits at 0: keep its marker whole
    ax.set_ylim(-0.012, 0.26)
    ax.set_xlabel(r"$8\pi J/A$ [%]")
    ax.set_ylabel(r"$1/\tau$")
    # The same scale relabelled in tau on the right edge: one axis, two units.
    right = ax.secondary_yaxis("right")
    ax.tick_params(axis="y", which="both", right=False)   # the right edge is tau's alone
    right.minorticks_off()
    taus = (5.0, 10.0, 20.0, 50.0)
    right.set_yticks([0.0] + [1.0 / v for v in taus])
    right.set_yticklabels([r"$\infty$"] + [f"{v:g}" for v in taus])
    right.set_ylabel(r"$\tau$", rotation=0, labelpad=8.0)
    entries = [
        (mlines.Line2D([], [], marker="o", ls="none", ms=3.8, color=pal["measured"]),
         "measured $\\tau$, collapse"),
    ]
    if any(p["branch"] == "inflates" for p in drawn):
        entries.append((mlines.Line2D([], [], marker="^", ls="none", ms=4.6,
                                      color=pal["measured"]),
                        "measured $\\tau$, expansion"))
    if any(p["stable"] for p in drawn):
        entries.append((mlines.Line2D([], [], marker="o", ls="none", ms=5.5, mfc="none",
                                      mec=pal["stable"], mew=1.2), "stable over the run"))
    if fit is not None:
        tag = "collapse fit" + (f": zero at {x0:.0f} %" if x0 else "")
        entries.append((fit_line, tag))
    if az:
        entries.append((mlines.Line2D([], [], marker="D", ls="none", ms=6.5, mfc="none",
                                      mec=pal["azad"], mew=1.0), "Azad et al., 2nd order"))
    entries.append((mlines.Line2D([], [], ls=":", lw=0.8, color="#b5b5b2"),
                    "Azad: end (30 %)" + (f", $J_c$ ({jc_frac:.0f} %)" if jc_frac else "")))
    # 2026-10-20: two columns, read row by row (one entry a row took a third of the
    # figure); the caption spells out what the two Azad rules are; rows opened so the large
    # open markers do not touch
    style.legend_top(ax, entries, ncol=2, borderpad=0.6, handlelength=1.8, columnspacing=0.8,
                     labelspacing=0.65)
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
        j, frac = table_meta(rung["table"])
        m = measure(rung["run"])
        if m is None or (m["tau"] is None and not m["stable"]):
            pending.append(rung["label"] + ("" if m is None else
                                            f" (|deficit| {m['flat']:.1e} at t {m['t_end']:.0f})"))
        if m is not None:
            points.append(dict(label=rung["label"], j=j, frac=frac, **m))

    def fmt(v):
        return f"{v:6.2f}" if v is not None else "     -"

    print(f"tau over {100 * BAND[0]:g}-{100 * BAND[1]:g} %: areal (drawn) | equatorial | MOTS"
          " || areal over " + " / ".join(f"{100 * lo:g}-{100 * hi:g} %" for lo, hi in WIDE_BANDS))
    for p in points:
        if p["tau"] is not None:
            print(f"{p['label']:6s} J/A {p['frac']:5.1f} %  R_A {p['r_a']:.3f}  tau {fmt(p['tau'])}"
                  f" | {fmt(p['tau_eq'])} | {fmt(p['tau_mots'])} || "
                  + " / ".join(fmt(v) for v in p["tau_wide"])
                  + f"   (fit t {p['span'][0]:.1f}-{p['span'][1]:.1f}; Azad"
                  f" {fmt(1 / azad_rate(p['j']) if azad_rate(p['j']) > 0 else None)}; {p['branch']}"
                  + (f", early shrink {p['tau_shrink']:.1f}"
                     if p["branch"] == "inflates" and p["tau_shrink"] is not None else "") + ")")
        elif p["stable"]:
            print(f"{p['label']:6s} J/A {p['frac']:5.1f} %  R_A {p['r_a']:.3f}  "
                  f"stable: |deficit| <= {p['flat']:.1e} to t {p['t_end']:.0f}")
    for key, name in (("tau", "areal"), ("tau_eq", "equatorial"), ("tau_mots", "MOTS")):
        fit = fit_zero([p for p in points if p["tau"] is not None], key)
        if fit is not None:
            print(f"fit a - b (J/A)^2 on the {name} tau: a {fit[0]:.4f}, b {fit[1]:.3e}"
                  + (f", zero at {fit[2]:.1f} % of extremal" if fit[2] else ""))
    jc_frac = azad_jc_frac(points)
    if jc_frac:
        print(f"Azad's 2nd-order J_c {ETA0 ** 2 * np.sqrt(AZAD_W0 / AZAD_DW2):.3f} "
              f"sits at {jc_frac:.1f} % on this axis")
    if pending:
        print("pending rungs (deficit not yet through the band, or no data):", ", ".join(pending))
    draw(points, PALETTES[args.palette], jc_frac)
    print("wrote", FIGURES / "instability_curve.png")


if __name__ == "__main__":
    main()
