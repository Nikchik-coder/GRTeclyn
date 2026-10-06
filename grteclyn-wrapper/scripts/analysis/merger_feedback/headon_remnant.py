#!/usr/bin/env python3
r"""The head-on remnant against its initial data (feedback item D1, 2026-09-24).

Numbers for the question "what happens to the black hole the head-on forms, how
does its radius compare with the initial throats and masses, and why does it
shrink without a bounce".  Reads ONLY the tracked pack
(results/merger/campaign/04_binary_headon/...) through the claims ledger's own
loaders (research/merger/article/claims/lib.py, extract_mergers.py,
extract_waves.py), so every value printed here is recomputable the way the
ledger recomputes its rows.  Nothing is written unless --tsv is given.

    grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/analysis/merger_feedback/headon_remnant.py [--tsv OUT]

Sections
  1. formation and end values, and their ratios to one throat (R*), the
     throats' summed area (sqrt2 R*), the ADM mass (2 M_ADM = 4) and the
     throats' Misner-Sharp masses (R*/2 each);
  2. monotonicity of M_MS and R on every arm that tracks the late horizon;
  3. fits of R(t) and M_MS(t): the ledger's line / exponential against the
     alternatives, on the down-step (the paper's arm) and the denser fill-twin
     and V1c tracks; the half-period oscillation of the scan's R;
  4. the energy budget: negative energy outside the horizon at formation
     against what the horizon has swallowed and what was radiated;
  5. the phantom-flux estimate: the flux density the measured dM/dt needs,
     against the field that is left (collapse_diagnostics, scalar_modes).

Conventions: R, M_MS are the oriented star scan's (the scan's sphere bounds the
MOTS from inside, so R is a lower bound on the MOTS areal radius); code units,
throat mass m = 1 each, M_ADM = 2 (clmHeadonADMMass); R* = 3.8895 (clmRstar,
closed form).  Rows of the fill arms whose surface sits inside the fill's taper
(r_mots <= core_fill_radius_start) are surfaces of the device and are dropped.
"""

from __future__ import annotations

import argparse
import math
import pathlib
import sys

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[4]
CLAIMS = REPO / "research" / "merger" / "article" / "claims"
sys.path.insert(0, str(CLAIMS))
import lib  # noqa: E402
import extract_mergers as XM  # noqa: E402
import extract_single as XS  # noqa: E402

SCOUT = "merge_headon_flip_d8_v1_t100"                  # level 3, offline formation scan
ARM = "merge_headon_flip_d8_v1_lvl5from0_scalar_t100"   # level 5 from t = 0 (paper's arm)
DOWN = "merge_headon_flip_d8_v1_lvl3down_t100_r03500"   # level 3 from the level-5 t = 35 chk
FILL = "merge_headon_flip_d8_v1c_fillnarrow_t100_r02200"  # level 3, fill 1.0/1.5, dense scan
V1C = "merge_headon_flip_d8_v1c_latefreeze_t100"        # level 3, fill 1.2/1.8, never restarted
EPSM = "merge_headon_flip_d8_v1c_eps_m1e2_t100"         # V1c + eps = -1e-2 on both throats
SEAMED = "merge_headon_flip_d8_v1_lvl5_t100_r02200"     # offline anchors at t = 42.5 / 43

M_ADM = 2.0                                  # clmHeadonADMMass (params: 1 + 1)
# Schwarzschild l = 1, n = 0 massless-scalar quasinormal frequency, M omega =
# 0.2929 - 0.0977 i (the standard value; numerical and 6th-order WKB agree, e.g.
# the tables in J. Phys. Stud. 8, 93 (2004)).  Used only for an order of magnitude.
QNM_L1 = 0.2929

OUT: list[tuple[str, float, str]] = []


def keep(key: str, value: float, source: str, fmt: str = ".4g") -> float:
    OUT.append((key, float(value), source))
    print(f"  {key:<34s} = {value:{fmt}}    [{source}]")
    return float(value)


def track(run: str, t0: float = 0.0) -> dict[str, np.ndarray]:
    """The run's MOTS rows on the common centre C (live oriented scan), device rows
    dropped: r_mots must exceed the fill's taper start when a fill is on."""
    s = XM._mots(run)
    p = lib.params(run)
    r_cut = float(p["core_fill_radius_start"]) if int(float(p.get("core_freeze_fill", "0"))) else 0.0
    m = (s["time"] >= t0 - 1e-9) & (s["r_mots"] > r_cut)
    return {"t": s["time"][m], "r": s["r_mots"][m], "R": s["R_mots"][m], "M": s["M_MS_mots"][m]}


def aic(rss: float, n: int, k: int) -> float:
    return n * math.log(rss / n) + 2 * k


def fit_models(t: np.ndarray, y: np.ndarray, label: str, t_ref: float) -> dict[str, dict]:
    """Line, parabola, exponential-to-asymptote and line + sinusoid through y(t)."""
    from scipy.optimize import curve_fit

    n = len(t)
    res: dict[str, dict] = {}
    for deg, name in ((1, "line"), (2, "parabola")):
        c = np.polyfit(t, y, deg)
        rss = float(np.sum((y - np.polyval(c, t)) ** 2))
        res[name] = {"p": c, "rss": rss, "k": deg + 1}

    def expo(x, a, b, tau):
        return a + b * np.exp(-(x - t_ref) / tau)

    try:
        p, cov = curve_fit(expo, t, y, p0=(y[-1] - 0.1 * abs(y[0] - y[-1]), y[0] - y[-1], 30.0),
                           bounds=([-np.inf, -np.inf, 0.5], [np.inf, np.inf, 5000.0]),
                           maxfev=200000)
        rss = float(np.sum((y - expo(t, *p)) ** 2))
        res["exp"] = {"p": p, "err": np.sqrt(np.diag(cov)), "rss": rss, "k": 3}
    except Exception as exc:  # noqa: BLE001
        res["exp"] = {"fail": str(exc)}

    def wiggle(x, a, b, amp, per, ph):
        return a + b * (x - t_ref) + amp * np.sin(2 * np.pi * (x - t_ref) / per + ph)

    best = None
    for per0 in (14.0, 18.0, 22.0, 26.0, 30.0, 36.0):
        for ph0 in (0.0, 1.5, 3.0, 4.5):
            try:
                c = np.polyfit(t, y, 1)
                p, _ = curve_fit(wiggle, t, y, p0=(c[1] + c[0] * t_ref, c[0], 0.03, per0, ph0),
                                 bounds=([-np.inf, -1.0, 0.0, 8.0, -np.inf],
                                         [np.inf, 1.0, 1.0, 60.0, np.inf]), maxfev=20000)
                rss = float(np.sum((y - wiggle(t, *p)) ** 2))
                if best is None or rss < best["rss"]:
                    best = {"p": p, "rss": rss, "k": 5}
            except Exception:  # noqa: BLE001
                continue
    if best is not None:
        res["line+sine"] = best

    print(f"  -- {label}: n = {n}, t = {t[0]:.1f}-{t[-1]:.1f}")
    for name, r in res.items():
        if "fail" in r:
            print(f"     {name:<10s} FAILED ({r['fail'][:60]})")
            continue
        rms = math.sqrt(r["rss"] / n)
        r["rms"] = rms
        r["aic"] = aic(r["rss"], n, r["k"]) if n > r["k"] + 1 else float("nan")
        extra = ""
        if name == "line":
            extra = f"slope {r['p'][0]:+.5f}/unit"
        elif name == "parabola":
            extra = f"curvature {2 * r['p'][0]:+.2e}/unit^2, slope at end {np.polyval(np.polyder(r['p']), t[-1]):+.5f}"
        elif name == "exp":
            extra = (f"asymptote {r['p'][0]:.4f} +- {r['err'][0]:.4f}, tau {r['p'][2]:.1f} +- {r['err'][2]:.1f}")
        elif name == "line+sine":
            extra = f"slope {r['p'][1]:+.5f}/unit, amplitude {r['p'][2]:.4f}, period {r['p'][3]:.1f}"
        print(f"     {name:<10s} rms {rms:.4f}  AIC {r['aic']:8.1f}  {extra}")
    return res


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tsv", default=None, help="write key/value/source rows here")
    args = ap.parse_args(argv)

    r_star = XS.single_drainhole(quantity="R_min")          # clmRstar, closed form
    a_throat = 4 * math.pi * r_star ** 2

    # ------------------------------------------------------------ 1. values, ratios
    print("1. FORMATION AND END, AGAINST THE INITIAL DATA")
    keep("R_star", r_star, "clmRstar: closed-form drainhole R_min (extract_single.single_drainhole)", ".5f")
    keep("sqrt2_R_star", math.sqrt(2) * r_star, "two throats' summed area 2*4pi*R*^2 as one sphere", ".4f")
    keep("two_M_ADM", 2 * M_ADM, "clmHeadonADMMass = 2 (params 1 + 1)", ".4g")
    keep("M_MS_one_throat", r_star / 2, "R*/2: theta_+- = 0 on the time-symmetric throat, Eq. misner_sharp", ".4f")
    form = lib.stream(SCOUT, "horizon_offline_scan.dat")[1]
    t_f, R_f, M_f = form[0, 0], form[0, 2], form[0, 3]
    src_f = f"{SCOUT}/horizon_offline_scan.dat, t = {t_f:g} row (clmHeadonMotsRadius/Mass)"
    keep("R_form", R_f, src_f)
    keep("M_form", M_f, src_f)
    R_e = XM.mergers_mots_value(run=DOWN, col="R_mots", t=97)
    M_e = XM.mergers_mots_value(run=DOWN, col="M_MS_mots", t=97)
    R_99 = XM.mergers_mots_value(run=DOWN, col="R_mots", t=99)
    M_99 = XM.mergers_mots_value(run=DOWN, col="M_MS_mots", t=99)
    src_e = f"{DOWN}/horizon_scan.dat, centre C, t = 97 row (clmHeadonRemnantRadius)"
    keep("R_end_t97", R_e, src_e)
    keep("M_end_t97", M_e, src_e)
    keep("R_end_t99", R_99, f"{DOWN}/horizon_scan.dat, t = 99 row (last)")
    keep("M_end_t99", M_99, f"{DOWN}/horizon_scan.dat, t = 99 row (last)")
    for tag, R, M in (("form", R_f, M_f), ("t97", R_e, M_e)):
        keep(f"R_{tag}/R_star", R / r_star, "ratio")
        keep(f"R_{tag}/sqrt2R_star", R / (math.sqrt(2) * r_star), "ratio")
        keep(f"A_{tag}/(2A_throat)", 4 * math.pi * R ** 2 / (2 * a_throat), "(R/R*)^2/2")
        keep(f"R_{tag}/(2M_ADM)", R / (2 * M_ADM), "ratio")
        keep(f"Rhalf_{tag}/M_ADM", R / 2 / M_ADM, "irreducible mass R/2 over M_ADM (Penrose: <= 1)")
        keep(f"M_{tag}/M_ADM", M / M_ADM, "ratio")
        keep(f"M_{tag}/(2*R_star/2)", M / r_star, "over the two throats' summed M_MS")
        keep(f"2M/R_{tag}", 2 * M / R, "shape systematic: 1 on an exact MOTS")
    Minf = XM.mergers_headon_fit(run=DOWN, what="Minf")
    keep("Minf/M_ADM", Minf / M_ADM, "clmHeadonMassAsymptote / clmHeadonADMMass")
    keep("shrink_R_form_to_t97", 1 - R_e / R_f, "clmHeadonShrink")
    # the placed mouths read wide at t = 0 (PLACEMENT_CURVE.md); the pair's own t = 0 reading
    s0 = XM._scan(ARM, "A")
    keep("R_mouth_t0_placed", s0["R_min"][0], f"{ARM}/horizon_scan.dat centre A, t = 0 (placement: +14.4 % at d = 8)")
    keep("R_form/(sqrt2*R_mouth_t0)", R_f / (math.sqrt(2) * s0["R_min"][0]), "ratio against the placed mouths")

    # ------------------------------------------------------------ 2. monotonicity
    print("\n2. MONOTONICITY OF THE LATE TRACKS (consecutive MOTS rows, t >= 36)")
    tracks = {name: track(run, 36.0) for name, run in
              (("down", DOWN), ("fill", FILL), ("v1c", V1C), ("epsm", EPSM))}
    for name, tr in tracks.items():
        dM, dR = np.diff(tr["M"]), np.diff(tr["R"])
        keep(f"{name}_nrows", len(tr["t"]), f"{name}: MOTS rows t >= 36, fill surfaces dropped", ".0f")
        keep(f"{name}_M_rises", int((dM > 0).sum()), "count of consecutive M_MS increases", ".0f")
        keep(f"{name}_R_rises", int((dR > 0).sum()), "count of consecutive R increases", ".0f")
        keep(f"{name}_R_t99", tr["R"][np.argmin(abs(tr["t"] - 99))], "R at t = 99")
        keep(f"{name}_M_t99", tr["M"][np.argmin(abs(tr["t"] - 99))], "M_MS at t = 99")
    # the level-5 arm's live track and the formation scan, for the record
    a5 = track(ARM)
    keep("arm_M_rises_t35_37", int((np.diff(a5["M"][a5["t"] >= 35]) > 0).sum()), f"{ARM} live rows t = 35-37", ".0f")
    d = tracks["down"]
    last = d["t"] >= 88
    inc = np.diff(d["R"][last])
    keep("down_dR_t88_89", inc[0], "first increment of the last cluster")
    keep("down_dR_t98_99", inc[-1], "last increment: the decline is decelerating")

    # ------------------------------------------------------------ 3. fits
    print("\n3. FITS (AIC: lower is better; k = 2/3/3/5 parameters)")
    fits = {}
    for name in ("down", "fill", "v1c"):
        tr = tracks[name]
        fits[(name, "R")] = fit_models(tr["t"], tr["R"], f"{name}: R_MOTS", t_ref=36.0)
        fits[(name, "M")] = fit_models(tr["t"], tr["M"], f"{name}: M_MS", t_ref=36.0)
    lin = fits[("down", "R")]["line"]
    keep("down_R_slope", lin["p"][0], "clmHeadonRadiusSlope (line through the down-step's 24 rows)", "+.5f")
    keep("down_R_line_rms", lin["rms"], "rms of that line")
    for name in ("fill", "v1c"):
        f = fits[(name, "R")]
        keep(f"{name}_R_line_rms", f["line"]["rms"], f"{name}: rms of a line through R")
        if "line+sine" in f:
            keep(f"{name}_R_sine_period", f["line+sine"]["p"][3], "period of the sinusoid on the line")
            keep(f"{name}_R_sine_amp", f["line+sine"]["p"][2], "its amplitude")
            keep(f"{name}_R_sine_rms", f["line+sine"]["rms"], "rms of line + sinusoid")
    # the exponential's asymptote for M_MS on the denser tracks and on later windows
    from scipy.optimize import curve_fit

    def settle(x, a, b, tau, t0):
        return a + b * np.exp(-(x - t0) / tau)

    print("  -- M_MS exponential asymptote against the fitted window")
    for name in ("down", "fill", "v1c"):
        tr = tracks[name]
        for t_lo in (36.0, 44.0, 66.0, 78.0):
            m = tr["t"] >= t_lo
            if m.sum() < 6:
                continue
            t, M = tr["t"][m], tr["M"][m]
            try:
                p, cov = curve_fit(lambda x, a, b, tau: settle(x, a, b, tau, t[0]), t, M,
                                   p0=(M[-1] - 0.05, M[0] - M[-1] + 0.05, 25.0),
                                   bounds=([0.0, -10.0, 0.5], [10.0, 10.0, 5000.0]), maxfev=200000)
                e = np.sqrt(np.diag(cov))
                keep(f"{name}_Minf_from_t{t_lo:.0f}", p[0], f"{name}: M_inf of the exponential over t >= {t_lo:g} "
                     f"(tau {p[2]:.1f} +- {e[2]:.1f}, +- {e[0]:.3f})")
            except Exception as exc:  # noqa: BLE001
                print(f"     {name} t >= {t_lo:g}: exp fit failed ({exc})")
    # local late rates
    for name in ("down", "fill", "v1c"):
        tr = tracks[name]
        m = (tr["t"] >= 88) & (tr["t"] <= 99)
        keep(f"{name}_dMdt_t88_99", np.polyfit(tr["t"][m], tr["M"][m], 1)[0], f"{name}: line through M_MS, t = 88-99", "+.5f")
        keep(f"{name}_dRdt_t88_99", np.polyfit(tr["t"][m], tr["R"][m], 1)[0], f"{name}: line through R, t = 88-99", "+.5f")
        m2 = (tr["t"] >= 95) & (tr["t"] <= 99)
        keep(f"{name}_dRdt_t95_99", np.polyfit(tr["t"][m2], tr["R"][m2], 1)[0], f"{name}: line through R, t = 95-99", "+.5f")
    # the oscillation of R is the scan's inscribed-sphere systematic: its residual runs
    # opposite to the shape excess 2 M_MS / R - 1
    for name in ("fill", "v1c"):
        tr = tracks[name]
        m = tr["t"] >= 44
        t, R, M = tr["t"][m], tr["R"][m], tr["M"][m]
        rR = R - np.polyval(np.polyfit(t, R, 2), t)
        ex = 2 * M / R
        rX = ex - np.polyval(np.polyfit(t, ex, 2), t)
        keep(f"{name}_corr_Rresid_vs_shape", float(np.corrcoef(rR, rX)[0, 1]),
             f"{name}: correlation of detrended R with detrended 2M/R, t >= 44", "+.3f")
    # rate at t = 47-50 (the field still strong) for the flux argument
    m = (d["t"] >= 47) & (d["t"] <= 50)
    dMdt_early = keep("down_dMdt_t47_50", np.polyfit(d["t"][m], d["M"][m], 1)[0], "down: line through M_MS, t = 47-50", "+.5f")
    dRdt_early = keep("down_dRdt_t47_50", np.polyfit(d["t"][m], d["R"][m], 1)[0], "down: line through R, t = 47-50", "+.5f")

    # ------------------------------------------------------------ 4. energy budget
    print("\n4. ENERGY BUDGET (code units; physical signs)")
    import extract_waves as XW
    e_gw = XW.waves_energy(scenario="head-on", which="E") * M_ADM
    e_gw_hi = XW.waves_energy(scenario="head-on", which="hi") * M_ADM
    keep("E_GW", e_gw, "waves_energy('head-on', 'E') x M = 2: dominant multipole, innermost sphere", ".3e")
    keep("E_GW_hi", e_gw_hi, "same, highest over the spheres", ".3e")
    e_phi = [XW.waves_post_energy(run=ARM, R=R, t0=21.5, M=1.0) for R in (10, 14, 18)]
    for R, e in zip((10, 14, 18), e_phi):
        keep(f"E_phi_post_R{R}", e, f"clmGwCensEnergy* x 2: int_(t>=21.5) (-F_kin) dt at R = {R} ({ARM})")
    keep("E_outside_at_formation", M_ADM - R_f / 2,
                      "M_ADM - R_form/2: exterior (phantom) energy if the horizon mass were R/2 (upper bound: R_scan <= R_MOTS)")
    m_b = [M_ADM - e_gw - e for e in (e_phi[0], e_phi[2])]
    keep("M_Bondi_lo", min(m_b), "M_ADM - E_GW - E_phi (R = 10 value)")
    keep("M_Bondi_hi", max(m_b), "M_ADM - E_GW - E_phi (R = 18 value)")
    keep("R_final_lo", 2 * min(m_b), "2 M_Bondi: the Schwarzschild end state once the hair is gone")
    keep("R_final_hi", 2 * max(m_b), "2 M_Bondi")
    keep("swallowed_R/2_form_to_t97", (R_f - R_e) / 2, "drop of R/2, formation (offline) to t = 97 (down-step)")
    keep("swallowed_fraction", ((R_f - R_e) / 2) / (R_f / 2 - min(m_b)),
         "fraction of R_form/2 - M_Bondi already gone by t = 97 (R = 10 value of E_phi)", ".3f")
    keep("t_reach_R_final_at_slope", 97 + (2 * max(m_b) - R_e) / lin["p"][0],
         "when the ledger's line would reach 2 M_Bondi (R = 18 value)", ".4g")
    keep("t_reach_2M_ADM_at_slope", 97 + (2 * M_ADM - R_e) / lin["p"][0], "when the line would cross 2 M_ADM", ".4g")
    # the M_MS profile through the t = 42.5 remnant (offline scan): phantom energy on both sides
    txt = (lib.run_dir(SEAMED) / "horizon_offline_scan_lvl5_t42.5_43.dat").read_text().splitlines()
    prof = []
    for ln in txt[txt.index(next(x for x in txt if "BinaryWormholePlt04250" in x)) + 1:]:
        if ln.startswith("=="):
            break
        p = ln.split()
        if len(p) >= 9 and p[0][0].isdigit() and p[8] in ("TRAPPED", "mixed", "untrapped", "UNTRAPPED"):
            prof.append((float(p[0]), float(p[1]), float(p[7])))
    prof = np.array(prof)
    keep("t42.5_M_MS_innermost_shell", prof[0, 2], f"{SEAMED}/horizon_offline_scan_lvl5_t42.5_43.dat, r = {prof[0, 0]:g}")
    keep("t42.5_M_MS_outermost_shell", prof[-1, 2], f"same file, r = {prof[-1, 0]:g} (outside the MOTS at r = 3.305)")
    keep("t42.5_M_MS_monotone_outward", float(np.all(np.diff(prof[:, 2]) < 0)), "1 if M_MS falls at every shell outward (rho < 0)", ".0f")

    # ------------------------------------------------------------ 5. flux estimate
    print("\n5. PHANTOM FLUX INTO THE HORIZON, ORDER OF MAGNITUDE")
    # spherical first law on the horizon: dM/dv = -A <(d_v phi)^2> (phantom, T_uv = 0)
    for label, (t0, t1), dMdt, R in (("t47_50", (47, 50), dMdt_early, float(np.mean(d["R"][(d["t"] >= 47) & (d["t"] <= 50)]))),
                                     ("t88_99", (88, 99), None, float(np.mean(d["R"][d["t"] >= 88])))):
        if dMdt is None:
            dMdt = [v for k, v, _ in OUT if k == "down_dMdt_t88_99"][0]
        A = 4 * math.pi * R ** 2
        need = abs(dMdt) / A
        keep(f"need_rms_dvphi_{label}", math.sqrt(need), f"sqrt(|dM_MS/dt| / 4 pi R^2), down-step, t = {t0}-{t1}", ".2e")
        for run in (ARM, DOWN):
            cd = XM._table(run, "collapse_diagnostics.dat")[1]
            m = (cd[:, 0] >= t0) & (cd[:, 0] <= t1)
            phi = np.max(np.abs(cd[m][:, 7:9]))
            pi = np.max(np.abs(cd[m][:, 9:11]))
            short = "arm" if run == ARM else "down"
            keep(f"{short}_maxphi_{label}", phi, f"{run}/collapse_diagnostics.dat: grid max |phi|, t = {t0}-{t1}", ".2e")
            keep(f"{short}_maxPi_{label}", pi, f"{run}/collapse_diagnostics.dat: grid max |Pi|, t = {t0}-{t1}", ".2e")
        # ringdown estimate: l = 1 field of peak phi_max oscillating at the QNM frequency,
        # <cos^2> = 1/3 over the sphere
        phi_max = [v for k, v, _ in OUT if k == f"arm_maxphi_{label}"][0]
        omega = QNM_L1 / (R / 2)
        rate = A * (omega * phi_max) ** 2 / 3
        keep(f"ringdown_dMdt_{label}", rate, "4 pi R^2 (omega phi_max)^2/3, omega = 0.2929/(R/2) (Schwarzschild l=1 scalar QNM)", ".2e")
        keep(f"measured_over_ringdown_{label}", abs(dMdt) / rate, "measured |dM_MS/dt| over that estimate", ".3g")
    # the ratio argument: flux proxies fall by far more than the rates
    for proxy in ("maxphi", "maxPi"):
        a = [v for k, v, _ in OUT if k == f"arm_{proxy}_t47_50"][0]
        b = [v for k, v, _ in OUT if k == f"arm_{proxy}_t88_99"][0]
        keep(f"flux_proxy_fall_{proxy}^2", (a / b) ** 2, f"({proxy} t47-50 / t88-99)^2, level-5 arm", ".3g")
    rM = dMdt_early / [v for k, v, _ in OUT if k == "down_dMdt_t88_99"][0]
    rR = dRdt_early / [v for k, v, _ in OUT if k == "down_dRdt_t88_99"][0]
    keep("rate_fall_M", rM, "down-step dM_MS/dt, t47-50 over t88-99", ".3g")
    keep("rate_fall_R", rR, "down-step dR/dt, t47-50 over t88-99", ".3g")
    # scalar energy crossing R = 10 outward, late, against the horizon's loss
    t, k = XW._flux(ARM, 10)
    m = (t >= 88) & (t <= 99.5)
    keep("F_phi_R10_mean_t88_99", -np.trapezoid(k[m], t[m]) / (t[m][-1] - t[m][0]),
         f"{ARM}/scalar_modes.dat: mean physical scalar flux out through R = 10, t = 88-99.5", ".2e")
    # the same ratio test on the EXTERIOR field alone (the grid maxima may sit in the
    # frozen interior): the l = 1 amplitudes and |F_kin| on the innermost sphere
    names, sm = lib.stream(ARM, "scalar_modes.dat")
    ix = {n: i for i, n in enumerate(names)}
    ts = sm[:, 0]

    def l1(field: str) -> np.ndarray:
        return np.sqrt(sum(sm[:, ix[f"R10_{field}_l1_m{mm}_re"]] ** 2 + sm[:, ix[f"R10_{field}_l1_m{mm}_im"]] ** 2
                           for mm in (-1, 0, 1)))

    for field in ("phi", "Pi"):
        a = l1(field)
        e = np.sqrt(np.mean(a[(ts >= 45) & (ts <= 52)] ** 2))
        lt = np.sqrt(np.mean(a[(ts >= 88) & (ts <= 99.5)] ** 2))
        keep(f"R10_{field}_l1_rms_t45_52", e, f"{ARM}/scalar_modes.dat: rms over t = 45-52 of R*|{field}_l1| at R = 10", ".3e")
        keep(f"R10_{field}_l1_rms_t88_99", lt, "same, t = 88-99.5", ".3e")
        keep(f"R10_{field}_l1_fall^2", (e / lt) ** 2, "(early / late)^2: the exterior flux proxy's fall", ".3g")
    fe = np.mean(np.abs(k[(t >= 45) & (t <= 52)]))
    fl = np.mean(np.abs(k[(t >= 88) & (t <= 99.5)]))
    keep("R10_absFkin_fall", fe / fl, "mean |F_kin(R = 10)| over t = 45-52 / over t = 88-99.5", ".3g")

    # ------------------------------------------------------------ 6. constraints
    print("\n6. CONSTRAINT NORMS OF THE NO-FILL ARMS ('falling throughout'?)")
    for run, short in ((ARM, "arm"), (DOWN, "down")):
        c = XM._table(run, "constraint_norms.dat")[1]
        c = c[np.argsort(c[:, 0])]
        post = c[:, 0] > 30
        i = np.argmin(np.where(post, c[:, 1], np.inf))
        keep(f"{short}_H_min_after_30", c[i, 1], f"{run}/constraint_norms.dat: min L2_Ham after t = 30", ".3e")
        keep(f"{short}_H_min_time", c[i, 0], "its time", ".3g")
        keep(f"{short}_H_end", c[-1, 1], "L2_Ham on the last row", ".3e")
        if run == ARM:
            keep("arm_H_at_formation", c[np.argmin(abs(c[:, 0] - 22.0)), 1], "L2_Ham at t = 22", ".3e")
            keep("arm_M_end", c[-1, 2], "L2_Mom on the last row", ".3e")
            j = np.argmin(np.where(post, c[:, 2], np.inf))
            keep("arm_M_min_after_30", c[j, 2], f"min L2_Mom after t = 30 (t = {c[j, 0]:.1f})", ".3e")

    if args.tsv:
        out = pathlib.Path(args.tsv)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as fh:
            fh.write("key\tvalue\tsource\n")
            for key, v, src in OUT:
                fh.write(f"{key}\t{v:.6g}\t{src}\n")
        print(f"\nwrote {out} ({len(OUT)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
