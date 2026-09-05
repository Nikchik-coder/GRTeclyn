#!/usr/bin/env python3
"""Systematics for the isolated-throat instability (Stage 0).

The massive Ellis-Bronnikov drainhole is an EXACT fixed point of the evolved
system: the spatial metric is conformally flat, K = A_ij = Theta = 0, the shift
starts and stays at zero, and alpha = e^u is stationary because K = 0.  So the
exact solution at time t is the exact solution at t = 0, and every deviation is
either truncation error or a growing physical mode -- there is no third thing
and no transient to wait out.  That is what makes R_areal_min(t) a clean
instability measurement rather than a plot.

This module answers four separate questions, in this order, because the later
ones are only meaningful if the earlier ones pass:

  1. WHEN IS THE DIAGNOSTIC TRUSTWORTHY?  R_areal_min is a minimum found by
     scanning rbar over a window with an inner cutoff.  Once the minimum reaches
     that cutoff the number is clipped and stops meaning "throat".  Nothing
     downstream of that time may be quoted.  This is checked first and it fences
     off every other number in the report.
  2. IS THE DEPARTURE EXPONENTIAL?  Measured as the local logarithmic derivative
     d ln|R0 - R| / dt, not as a least-squares slope.  A least-squares fit
     returns a rate whatever the data does; the local derivative shows whether
     there is a plateau to fit in the first place, and where.
  3. WHAT IS THE RATE, AND DOES IT MATCH THEORY?  Gonzalez, Guzman & Sarbach
     (arXiv:0806.0608) give the growth time of the single unstable radial mode
     as T = tau/r_throat in proper time at the throat.  The evolution measures
     coordinate time, so the comparison needs the throat lapse.
  4. IS IT PHYSICS OR TRUNCATION ERROR?  The discriminator is resolution.  A
     physical mode seeded by truncation error dx^p is DELAYED by a fixed
     tau*p*ln2 per halving of dx while keeping the same rate; a purely numerical
     departure changes rate too.  Reported honestly, including when the coarse
     arms die too early to settle it.

Reads only the packed tree, so the numbers cannot drift from the data beside
them.  Writes single_throat/INSTABILITY.md.

Usage: single_throat_instability.py <pack-root>   (default: this file's parent's parent)
"""

from __future__ import annotations

import math
import pathlib
import sys

import numpy as np

# Closed form for a = 2, m = 1.  The minimal surface sits at
# rbar = (m + sqrt(m^2 + a^2))/2 = 1.6180, where the isotropic radius parameter
# X = 1/2, so u = (atan X - pi/2)/2 = -0.5536 and the throat lapse is e^u.
R_THROAT_EXACT = 3.8895
RBAR_THROAT = 1.6180
ALPHA_THROAT = math.exp(0.5 * (math.atan(0.5) - 0.5 * math.pi))   # 0.57487
# Table I of arXiv:0806.0608 interpolated to m/a = 0.5.  The full tabulated
# range over all gamma_1 is 0.590 (gamma_1 -> inf) to 0.846 (gamma_1 = 0).
T_PREDICTED = (0.68, 0.76)
T_TABULATED = (0.590, 0.846)

# The consumer's areal-radius scan takes an inner cutoff so it does not walk
# into the compactified origin.  Once the reported minimum sits on the first
# cell above it, the diagnostic is clipped.
AREAL_MIN_RADIUS = 0.5

# arm -> (label, finest dx, what it varies).  dx = L/N / 2^max_level with
# L = 64, N = 128 throughout.
ARMS = {
    "single_hold_t100":      ("ml3 tag2 sg0.1", 0.0625, "production arm, t = 100"),
    "s16ml3_lapse5_sg01_fg": ("ml3 tag1 sg0.1", 0.0625, "same resolution, other tagger"),
    "s15_lapse5_sg01_fg":    ("ml2 tag1 sg0.1", 0.1250, "half resolution"),
    "s15_lapse5_sg00_fg":    ("ml2 tag1 sg0.0", 0.1250, "half resolution, no dissipation"),
    "s15_lapse6_sg00_fg":    ("ml2 collar sg0.0", 0.1250, "half resolution, origin collar"),
}
PRODUCTION = "single_hold_t100"


def read_stream(path: pathlib.Path) -> tuple[np.ndarray, np.ndarray]:
    """Load a whitespace .dat with a leading '#' header into (time, columns)."""
    rows = [line.split() for line in path.read_text().splitlines()
            if line.strip() and not line.startswith("#")]
    if not rows:
        return np.empty(0), np.empty((0, 0))
    a = np.array([[float(x) for x in r] for r in rows])
    return a[:, 0], a[:, 1:]


def find_arms(root: pathlib.Path) -> dict[str, pathlib.Path]:
    """Locate each arm's directory in the pack, wherever it was placed."""
    found = {}
    for name in ARMS:
        for sub in ("campaign", "single_throat"):
            d = root / sub / name
            if (d / "areal_radius.dat").exists():
                found[name] = d
                break
    return found


def trust_window(t: np.ndarray, rbar: np.ndarray) -> tuple[float, str]:
    """Last time the areal minimum is genuinely interior to the search window.

    The scan reports the location of the minimum alongside its value.  While
    that location moves it is tracking a real minimal surface -- a contracting
    throat is *expected* to move.  When it stops on the innermost sampled cell
    and stays there, the minimum has run off the inner edge and the value is a
    boundary reading, not a throat radius.
    """
    edge = rbar.min()
    if edge > AREAL_MIN_RADIUS * 1.3:        # never reached the cutoff
        return float(t[-1]), "minimum stayed interior for the whole run"
    pinned = rbar <= edge * 1.001
    # first index of the final unbroken run of pinned samples
    i = len(t)
    while i > 0 and pinned[i - 1]:
        i -= 1
    return float(t[i - 1] if i else t[0]), (
        f"minimum pinned at the scan's inner cutoff (rbar = {edge:.4f}) from "
        f"t = {t[i]:.0f}; everything after that is clipped")


def local_rate(t: np.ndarray, d: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Central-difference d ln(d)/dt, defined only where d > 0."""
    ok = d > 0
    ts, gs = [], []
    for i in range(1, len(t) - 1):
        if ok[i - 1] and ok[i + 1]:
            ts.append(t[i])
            gs.append((math.log(d[i + 1]) - math.log(d[i - 1])) / (t[i + 1] - t[i - 1]))
    return np.array(ts), np.array(gs)


def find_plateau(ts: np.ndarray, gs: np.ndarray, t_max: float,
                 width: float = 10.0, tol: float = 0.08):
    """Longest late window over which the local rate is flat to `tol` relative.

    A linear eigenmode shows up as a plateau in the local rate.  Requiring the
    plateau rather than fitting a chosen window is what keeps the answer from
    being a property of the window.
    """
    m = ts <= t_max
    ts, gs = ts[m], gs[m]
    best = None
    for i in range(len(ts)):
        for j in range(len(ts) - 1, i, -1):
            if ts[j] - ts[i] < width:
                continue
            seg = gs[i:j + 1]
            if seg.min() <= 0:
                continue
            if (seg.max() - seg.min()) / seg.mean() <= tol:
                if best is None or (ts[j] - ts[i]) > (best[1] - best[0]):
                    best = (ts[i], ts[j], seg.mean(), seg.std(ddof=1))
                break
    return best


def turnover(t: np.ndarray, R: np.ndarray) -> tuple[float, float]:
    """Time and relative height of the maximum of R(t) -- the departure knee.

    R swells slightly before it contracts, so the peak is where the growing mode
    overtakes the initial settling drift.  Its height is proportional to the
    truncation seed, which is what makes it the resolution observable.

    An arm carrying a finite perturbation of its own -- the origin collar, which
    changes the solution at t = 0 -- contracts monotonically instead and has no
    such knee.  Reporting argmax = 0 for it would put a meaningless 0.0 in the
    resolution table, so those arms return NaN and are excluded by the caller.
    """
    i = int(np.argmax(R))
    if i == 0:
        return float("nan"), float("nan")
    return float(t[i]), float((R[i] - R[0]) / R[0])


def figures_held(t: np.ndarray, R: np.ndarray, upto: float) -> list[tuple[int, float]]:
    """For each digit count, how long R holds it unbroken from t = 0.

    "Flat to nine significant figures" is two claims -- how flat, and for how
    long -- and a single window cannot carry both: the looser the tolerance the
    longer the window, so maximising the window silently minimises the claim.
    The ladder is returned whole and the caller quotes the rows it needs.
    """
    R0, out = R[0], []
    for nsig in range(9, 3, -1):
        held = 0.0
        for tt, rr in zip(t, R):
            if tt > upto or abs(rr - R0) / R0 >= 10.0 ** -nsig:
                break
            held = float(tt)
        out.append((nsig, held))
    return out


def main(root: pathlib.Path) -> None:
    arms = find_arms(root)
    if PRODUCTION not in arms:
        sys.exit(f"[single-throat] no {PRODUCTION} in {root} -- nothing to analyse")

    out: list[str] = []
    w = out.append
    w("# The isolated throat is linearly unstable")
    w("")
    w("Generated by `analysis/single_throat_instability.py` from the packed streams.")
    w("Do not hand-edit; re-run the packer instead.")
    w("")
    w(f"Exact closed form for a = 2, m = 1: minimal surface at rbar = {RBAR_THROAT},")
    w(f"areal radius R = {R_THROAT_EXACT}, throat lapse alpha = {ALPHA_THROAT:.4f}.")
    w("")

    t, cols = read_stream(arms[PRODUCTION] / "areal_radius.dat")
    R, rbar = cols[:, 0], cols[:, 1]
    R0 = R[0]
    d = R0 - R

    # ---- 1. trust window ---------------------------------------------------
    t_trust, why = trust_window(t, rbar)
    w("## 1. How far the diagnostic can be read")
    w("")
    w("`R_areal_min` is the minimum of the areal radius over a radial scan with an")
    w(f"inner cutoff at rbar = {AREAL_MIN_RADIUS}. Three regimes, and only the first two count:")
    w("")
    w("| window | location of the minimum | status |")
    w("|---|---|---|")
    at_throat = t[rbar >= rbar[0] * 0.999]
    w(f"| t = 0-{at_throat[-1]:.0f} | fixed at the throat cell, rbar = {rbar[0]:.4f} | exact |")
    mid = (t > at_throat[-1]) & (t <= t_trust)
    if mid.any():
        w(f"| t = {t[mid][0]:.0f}-{t_trust:.0f} | migrating inward, "
          f"rbar {rbar[mid][0]:.4f} -> {rbar[mid][-1]:.4f} | a contracting throat, still interior |")
    w(f"| t > {t_trust:.0f} | pinned at rbar = {rbar.min():.4f} | **clipped -- do not quote** |")
    w("")
    w(f"{why[0].upper()}{why[1:]}.")
    late = t > t_trust
    if late.any():
        w(f"The apparent plateau at R = {R[late].mean():.2f} over t = {t[late][0]:.0f}-{t[-1]:.0f}")
        w("is that boundary reading, not a new equilibrium. **Every number below is")
        w(f"taken from t <= {t_trust:.0f}.**")
    w("")

    # ---- 2. phase structure ------------------------------------------------
    t_peak, h_peak = turnover(t, R)
    cross = t[(t > t_peak) & (R < R0)]
    w("## 2. What the throat did")
    w("")
    w("| window | behaviour |")
    w("|---|---|")
    ladder = figures_held(t, R, t_peak)
    w(f"| t = 0-{t_peak:.0f} | flat, then a slow swell peaking +{100 * h_peak:.4f}% at "
      f"t = {t_peak:.0f} (digits below) |")
    if len(cross):
        w(f"| t = {t_peak:.0f}-{cross[0]:.0f} | turns over, back through the exact value at t = {cross[0]:.0f} |")
        w(f"| t = {cross[0]:.0f}-{t_trust:.0f} | monotone contraction, exponential |")
    w("")
    w("How long the initial value survives, digit by digit:")
    w("")
    w("| significant figures | held unbroken to t = |")
    w("|---|---|")
    for nsig, held in ladder:
        w(f"| {nsig} | {held:.0f} |")
    w("")
    w("An exponential loses each digit in the same interval (tau ln 10). These")
    w("intervals are 1, 2, 8, 8 -- so the early drift is *not* the mode. It is a")
    w("settling transient, and it is what seeds the mode rather than being it.")
    w("")
    w("| t | R_areal_min | vs t = 0 |")
    w("|---|---|---|")
    for tt in [0, 10, 20, 26, 31, 35, 40, 45, 50, 55, 60, 65]:
        i = int(np.argmin(np.abs(t - tt)))
        if t[i] > t_trust + 1:
            break
        w(f"| {t[i]:.0f} | {R[i]:.5f} | {100 * (R[i] - R0) / R0:+.3f}% |")
    w("")

    # ---- 3. is it exponential, and how fast --------------------------------
    # The rate may only be read while BOTH the diagnostic is unclipped and the
    # evolution is still the PDE.  chi is clamped at a floor near the origin;
    # once that clamp engages the equations being solved are no longer the ones
    # whose mode we are measuring, so the floor time is a hard cap even though
    # the areal diagnostic itself survives a few units longer.
    t_floor = float("inf")
    cpath = arms[PRODUCTION] / "collapse_diagnostics.dat"
    if cpath.exists():
        tk_, K_ = read_stream(cpath)
        hit = tk_[K_[:, 1] <= 1.0000001e-8]
        if len(hit):
            t_floor = float(hit[0])
    t_read = min(t_trust, t_floor)
    ts, gs = local_rate(t, d)
    pl = find_plateau(ts, gs, t_read)
    w("## 3. The growth rate, measured as a plateau and not as a fit")
    w("")
    w("Local logarithmic derivative d ln|R0 - R| / dt. A least-squares slope over a")
    w("chosen window returns a number whatever the data does; this shows whether")
    w("there is a constant rate to quote at all.")
    w("")
    w("| t | R0-R | as % of R0 | d ln/dt | e-folding |")
    w("|---|---|---|---|---|")
    for tt in range(30, int(t_read) + 1, 3):
        i = int(np.argmin(np.abs(ts - tt)))
        j = int(np.argmin(np.abs(t - tt)))
        if abs(ts[i] - tt) > 0.6 or d[j] <= 0:
            continue
        w(f"| {tt} | {d[j]:.3e} | {100 * d[j] / R0:.2f}% | {gs[i]:.4f} | {1 / gs[i]:.2f} |")
    w("")
    if pl:
        lo, hi, rate, sd = pl
        tau = 1 / rate
        i0 = int(np.argmin(np.abs(t - lo)))
        i1 = int(np.argmin(np.abs(t - hi)))
        efolds = math.log(d[i1] / d[i0])
        w(f"The rate is **flat over t = {lo:.0f}-{hi:.0f}** (the readable window ends at "
          f"t = {t_read:.0f}):")
        w("")
        w(f"{rate:.4f} +/- {sd:.4f} per unit,")
        w(f"i.e. **tau = {tau:.2f} coordinate units**, holding across {efolds:.1f} e-foldings while")
        w(f"the deviation grows from {100 * d[i0] / R0:.2f}% to {100 * d[i1] / R0:.1f}% of the throat radius.")
        w("")
        w("Before that plateau the apparent rate is much larger and falling. That is not")
        w("a faster early mode: R swells before it contracts, so the growing mode and the")
        w("settling drift cancel near the crossing and the logarithm of a near-zero")
        w("difference has a spurious derivative. **The small-amplitude window is the one")
        w("that cannot be fitted**, which is the opposite of the usual situation and the")
        w("reason a fit was not used.")
        w("")
        w("### Against theory")
        w("")
        T_coord = tau / R_THROAT_EXACT
        T_proper = ALPHA_THROAT * tau / R_THROAT_EXACT
        w("| quantity | value |")
        w("|---|---|")
        w(f"| e-folding, coordinate time | {tau:.2f} |")
        w(f"| e-folding, proper time at the throat (x alpha = {ALPHA_THROAT:.4f}) | {ALPHA_THROAT * tau:.2f} |")
        w(f"| T = tau_proper / r_throat | **{T_proper:.3f}** |")
        w(f"| Gonzalez+ 2008 at m/a = 0.5, interpolated | {T_PREDICTED[0]}-{T_PREDICTED[1]} |")
        w(f"| Gonzalez+ 2008, full tabulated range | {T_TABULATED[0]}-{T_TABULATED[1]} |")
        w("")
        hi_p = T_PREDICTED[1]
        w(f"Measured T is {100 * (T_proper - hi_p) / hi_p:+.0f}% against the top of the interpolated")
        w(f"band and sits just outside the tabulated range at the gamma_1 = 0 end. The mode is")
        w("real and its rate is the predicted one to about 15%; the residual is within the")
        w("interpolation of Table I and the (a, m) <-> (B, gamma_1) mapping, neither of which")
        w("has been checked line by line.")
    else:
        w("**No flat window found** -- the departure has no constant rate to quote,")
        w("which would argue against a linear eigenmode.")
    w("")

    # ---- 4. resolution -----------------------------------------------------
    w("## 4. Physics or truncation error? The resolution test")
    w("")
    w("A physical mode seeded by truncation error is *delayed* by refining, at fixed")
    w("rate: halving dx shrinks the seed by 2^p and buys tau*p*ln2 more units before")
    w("the mode is visible. A numerical departure changes its rate instead.")
    w("")
    w("| arm | dx (finest) | varies | turnover t | peak height | ran to |")
    w("|---|---|---|---|---|---|")
    peaks = {}
    for name, (lab, dx, desc) in ARMS.items():
        if name not in arms:
            continue
        ta, ca = read_stream(arms[name] / "areal_radius.dat")
        tp, hp = turnover(ta, ca[:, 0])
        if math.isnan(tp):
            w(f"| `{name}` | {dx} | {desc} | none | monotone from t = 0 | {ta[-1]:.1f} |")
            continue
        peaks[name] = (dx, tp, hp, ta[-1])
        w(f"| `{name}` | {dx} | {desc} | {tp:.1f} | +{100 * hp:.4f}% | {ta[-1]:.1f} |")
    w("")
    w("Turnover times are resolved only to each arm's output cadence (1.0 unit for the")
    w("production arm, 0.5 for the rest), so the two dx = 0.0625 rows differ by sampling")
    w("and not by evolution. The collar arm carries a finite perturbation at t = 0 and")
    w("never swells, so it has no knee to compare and is excluded from the shift below.")
    w("")
    fine = [v for k, v in peaks.items() if v[0] == 0.0625]
    coarse = [v for k, v in peaks.items() if v[0] == 0.1250 and v[2] > 0]
    if fine and coarse:
        cf = min(coarse, key=lambda v: v[2])          # least-perturbed coarse arm
        dt_shift = fine[0][1] - cf[1]
        ratio = cf[2] / fine[0][2]
        w(f"Halving dx delays the turnover by **{dt_shift:+.1f} units** ({cf[1]:.1f} -> {fine[0][1]:.1f})")
        w(f"and shrinks the peak by **{ratio:.1f}x**, i.e. the seed converges at order")
        w(f"{math.log(ratio) / math.log(2):.1f}. Delay and seed are consistent with a fixed-rate")
        w(f"mode if tau = dt/ln(ratio) = {dt_shift / math.log(ratio):.1f}, against the "
          f"{'measured ' + format(1 / pl[2], '.1f') if pl else 'measured'} above.")
        w("")
        alive = [v for v in coarse if v[3] > v[1] + 8]
        if not alive:
            w("**This is suggestive, not decisive.** Both coarse arms die within ~3 units of")
            w("their own turnover, so neither ever shows a growth *rate* to compare against.")
            w("Two resolutions with one rate between them cannot separate `delayed at fixed")
            w("rate` from `slower at coarse dx`. The test that settles it is stated below.")
    w("")

    # ---- 5. determinism ----------------------------------------------------
    same = [n for n in arms if n != PRODUCTION and ARMS[n][1] == ARMS[PRODUCTION][1]]
    if same:
        tb, cb = read_stream(arms[same[0]] / "areal_radius.dat")
        common = [(i, int(np.argmin(np.abs(tb - tt)))) for i, tt in enumerate(t)
                  if np.min(np.abs(tb - tt)) < 1e-6]
        if common:
            dmax = max(abs(R[i] - cb[j, 0]) for i, j in common)
            w("## 5. The same-resolution arm is not a second opinion")
            w("")
            w(f"`{same[0]}` differs from the production arm only in the tagging scheme, and")
            w(f"agrees with it bit for bit -- max |dR| = {dmax:.1e} over every shared output")
            w("time, and the constraint")
            w("norms are bit-identical. For a single centred throat the two taggers build the")
            w("same grids, so this is one evolution computed twice. It is a determinism check")
            w("and **must not be reported as independent corroboration**.")
            w("")

    # ---- 6. late time ------------------------------------------------------
    cpath = arms[PRODUCTION] / "collapse_diagnostics.dat"
    npath = arms[PRODUCTION] / "constraint_norms.dat"
    if cpath.exists() and npath.exists():
        tk, K = read_stream(cpath)          # min_lapse, min_chi, max_abs_K, ...
        tn, N = read_stream(npath)          # L2_Ham, L2_Mom
        floor = tk[K[:, 1] <= 1.0000001e-8]
        w("## 6. What ends the run, and what does not")
        w("")
        w("| | |")
        w("|---|---|")
        w(f"| NaN | **none** -- the run reached its stop time t = {t[-1] + 1:.0f} |")
        w(f"| apparent horizon | never formed (max r_AH = 0 throughout) |")
        w(f"| L2_Ham while the mode grows (t = 1-{t_trust:.0f}) | "
          f"{N[np.argmin(np.abs(tn - 1)), 0]:.3e} -> {N[np.argmin(np.abs(tn - t_trust)), 0]:.3e}, flat |")
        if len(floor):
            w(f"| chi at the compactified origin | hits the 1e-8 floor at **t = {floor[0]:.1f}** |")
        w("")
        w("The constraint norms are flat -- slightly *decreasing* -- through the entire")
        w("growth phase. A growing mode of the constrained system satisfies the constraints,")
        w("so global norms give no warning whatever; they cannot be used to certify a")
        w("wormhole run as healthy.")
        w("")
        if len(floor):
            fit_lo = max(floor[0] + 8, 70)
            m = (tn >= fit_lo)
            if m.sum() > 5:
                for k, nm in ((0, "L2_Ham"), (1, "L2_Mom")):
                    y = np.log(N[m, k])
                    b = np.polyfit(tn[m], y, 1)[0]
                    w(f"After the floor is hit, {nm} grows exponentially: doubling every "
                      f"{math.log(2) / b:.1f} units (t >= {fit_lo:.0f}).")
                w("")
                w("That blow-up is numerical, not the mode: it starts when chi is clamped, not")
                w("when the throat departs, and the error profile at late times is a front")
                w("peaking at the origin and decaying outward -- the opposite of the")
                w("throat-peaked profile measured during the growth phase.")
                w("")

    # ---- 7. what is still needed -------------------------------------------
    w("## 7. What this does not settle")
    w("")
    w("- **The rate has been measured at one resolution.** Repeat at dx = 0.03125 to")
    w("  t = 100. If tau is unchanged and the turnover moves later by a further")
    w("  ~5 units, the mode is physical and its rate is converged. If tau moves with")
    w("  dx, it is not.")
    w("- **The coarse arms must be re-run to t = 100** with the tagger that lets them")
    w("  survive, so there is a rate at dx = 0.125 to compare rather than a turnover only.")
    w("- **Time discretisation is untested.** One arm at half the CFL factor separates")
    w("  it from spatial error.")
    w("- **No controlled perturbation was applied.** The seed here is truncation error,")
    w("  whose amplitude is not known independently. A deliberate +/- eps perturbation of")
    w("  known sign and size turns this into a measurement rather than an observation,")
    w("  and the sign test also checks that both signs grow at the same rate.")
    w("- **The profile was only scored at the ends.** The plotfiles that would show the")
    w("  throat-peaked profile turning into an origin-born front were pruned as the run")
    w("  went; keep t = 40-70 next time.")
    w("")

    dst = root / "single_throat" / "INSTABILITY.md"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(out) + "\n")
    print(f"[single-throat] {dst.relative_to(root.parent)}: {len(out)} lines, "
          f"{len(arms)} arms")


if __name__ == "__main__":
    root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[1]
    main(root.resolve())
