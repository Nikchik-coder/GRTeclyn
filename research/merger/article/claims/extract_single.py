"""Extractors for the ledger area 'single': the model, the numerical setup, the
single wormhole and two throats at rest (research.tex Secs. II-V).

Every function registered here returns ONE float recomputed from the tracked
pack (results/merger), never from the run tree.  Runs are named, and resolved
through lib.run_dir; the few group-level reduced tables (the level-3 shell
scans, the sign-rule table, the two ladder notes, the placement probes) are
found by file name under results/merger/campaign.

Where a number is a method's output (a plateau rate, a crossing time, a fit),
the method is the one of the figure or analysis script that produced it, and
the docstring names that script, so a disagreement can be traced to a choice
rather than argued about:

  plot_branches.py          plateau rates tau = 5.88 / 5.26, onset shifts
  plot_seed_branches.py     pair crossings, the seed arms' constraint record
  plot_single_collapse.py   the pure-quadrupole MOTS history, 10 % departure
  plot_single_inflation.py  the eps = -0.01 level-4 arm
  plot_horizon_regrowth.py  MOTS floor and regrowth, centre-A rows
  sign_rule.py              the sign-rule table and its ratio
  placement_curve.py        the placement curve and the scout's residual
"""

from __future__ import annotations

import functools
import itertools
import math
import pathlib
import re

import numpy as np

import lib
from lib import column, extractor, params, run_dir, stream, window  # noqa: F401

# --------------------------------------------------------------- constants
# IAU 2015 nominal G M_sun = 1.3271244e20 m^3 s^-2, c = 299 792 458 m/s.
GM_SUN_SECONDS = 1.3271244e20 / 299792458.0 ** 3     # 4.92549e-6 s
GM_SUN_KM = 1.3271244e20 / 299792458.0 ** 2 / 1e3    # 1.476625 km
AU_KM = 1.495978707e8                                # IAU 2012
UNIT_SECONDS = {"ms": 1e-3, "s": 1.0, "min": 60.0, "h": 3600.0, "d": 86400.0}

# The production arms the section quotes, by role.
LEVEL3 = "single_hold_t100"            # unkicked, level 3 (collapses)
LEVEL4 = "single_hold_ml4_t100"        # unkicked, level 4 (inflates)
KICK_P2 = "single_eps_p1e2_t100"       # eps = +1e-2, level 3
KICK_P3 = "single_eps_p1e3_t100"       # eps = +1e-3, level 3
SHELL_SCANS = "branch_shell_scans_2026-09-08.dat"


# --------------------------------------------------------------- helpers
@functools.lru_cache(maxsize=None)
def _campaign_file(name: str) -> pathlib.Path:
    """A group-level file of the pack (not a run's), found by name."""
    hits = sorted((lib.PACK / "campaign").rglob(name))
    if not hits:
        raise LookupError(f"{name} is not in the pack (results/merger/campaign)")
    return hits[0]


def _dedup(a: np.ndarray) -> np.ndarray:
    """Rows sorted by time, one per time (streams re-log a step on restarts)."""
    a = a[np.argsort(a[:, 0], kind="stable")]
    _, i = np.unique(np.round(a[:, 0], 6), return_index=True)
    return a[i]


@functools.lru_cache(maxsize=None)
def _areal(run: str) -> np.ndarray:
    """(t, R_areal_min, r_at_min) of the consumer's ray scan."""
    return _dedup(stream(run, "areal_radius.dat")[1])


def _sel(t: np.ndarray, t0: float | None, t1: float | None) -> np.ndarray:
    """Samples in [t0, t1], inclusive to 1e-6 (the streams stamp 29.9999999...)."""
    keep = np.ones(t.size, bool)
    if t0 is not None:
        keep &= t >= t0 - 1e-6
    if t1 is not None:
        keep &= t <= t1 + 1e-6
    return keep


@functools.lru_cache(maxsize=None)
def _hscan(run: str, file: str = "horizon_scan.dat") -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
    """The oriented scan: (header, rows as string tuples).  Not lib.stream:
    the centre column is a letter and missing values are 'nan'."""
    hdr: list[str] = []
    rows = []
    for line in (run_dir(run) / file).read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            toks = line.lstrip("#").split()
            if "time" in toks and "centre" in toks:
                hdr = toks
            continue
        p = line.split()
        if hdr and len(p) == len(hdr):
            rows.append(tuple(p))
    if not hdr:
        raise ValueError(f"{run}/{file}: no header")
    return tuple(hdr), tuple(rows)


def _mots(run: str, centre: str | None = "A") -> np.ndarray:
    """(t, R_mots, M_MS_mots) of the rows holding a MOTS, sorted by time."""
    hdr, rows = _hscan(run)
    it, ic, i_n, i_r, i_m = (hdr.index(k) for k in ("time", "centre", "n_mots", "R_mots", "M_MS_mots"))
    out = [(float(r[it]), float(r[i_r]), float(r[i_m])) for r in rows
           if int(float(r[i_n])) > 0 and (centre is None or r[ic] == centre)]
    if not out:
        raise ValueError(f"{run}: no MOTS rows (centre {centre})")
    return np.array(sorted(out))


def _drainhole(a: float, m: float) -> dict[str, float]:
    """Closed form of the massive Ellis-Bronnikov drainhole (research.tex Eq. 3)."""
    r_t = 0.5 * (m + math.sqrt(m * m + a * a))
    x = (r_t - a * a / (4.0 * r_t)) / a
    u = (m / a) * (math.atan(x) - 0.5 * math.pi)
    omega = 1.0 + a * a / (4.0 * r_t * r_t)
    q = (a * a + m * m) / (m * m) if m > 0 else math.inf
    return {"r_t": r_t, "alpha_th": math.exp(u), "chi_th": math.exp(2.0 * u) / omega ** 2,
            "R_min": math.exp(-u) * math.sqrt(a * a + m * m), "Q": q,
            "Q_ratio": (q + 1.0) / (q - 1.0)}


def _am(run: str) -> tuple[float, float]:
    p = params(run)
    return float(p["wormhole_throat_radius_A"]), float(p["wormhole_drainhole_mass_A"])


def _crossing(t: np.ndarray, y: np.ndarray, level: float) -> float:
    """First t at which |y| exceeds level, linearly interpolated (plot_branches.crossing)."""
    idx = np.where(np.abs(y) > level)[0]
    if idx.size == 0:
        raise ValueError(f"never exceeds {level}")
    k = int(idx[0])
    if k == 0:
        return float(t[0])
    y0, y1 = abs(y[k - 1]), abs(y[k])
    return float(t[k - 1] + (t[k] - t[k - 1]) * (level - y0) / (y1 - y0))


def _ref_radius(run: str, ref: str | float) -> float:
    if isinstance(ref, (int, float)):
        return float(ref)
    if ref == "R0":
        return float(_areal(run)[0, 1])
    if ref == "Rstar":
        return _drainhole(*_am(run))["R_min"]
    raise ValueError(f"ref must be 'R0', 'Rstar' or a number, not {ref!r}")


def _zero_crossing(t: np.ndarray, d: np.ndarray) -> float:
    k = np.where(np.diff(np.sign(d)) != 0)[0]
    if not k.size:
        raise ValueError("no sign change")
    i = int(k[0])
    return float(t[i] - d[i] * (t[i + 1] - t[i]) / (d[i + 1] - d[i]))


def _pick(values: list[float], kind: str) -> float:
    return float({"min": np.min, "max": np.max, "mean": np.mean, "median": np.median}[kind](values))


# ============================================================== the model
@extractor
def single_drainhole(quantity: str, run: str = LEVEL3, a: float | None = None,
                     m: float | None = None) -> float:
    """A closed-form property of the drainhole, a and m read from the run's
    params unless given: R_min (areal radius of the minimal surface), r_t
    (its isotropic radius), alpha_th (static lapse there), chi_th, Q =
    (a^2+m^2)/m^2, Q_ratio = (Q+1)/(Q-1)."""
    if a is None or m is None:
        a0, m0 = _am(run)
        a = a0 if a is None else a
        m = m0 if m is None else m
    return float(_drainhole(a, m)[quantity])


@extractor
def single_chi_throat_range(kind: str, m_over_a_max: float = 1.0, n: int = 401) -> float:
    """min or max of chi at the throat over 0 <= m/a <= m_over_a_max (closed form)."""
    vals = [_drainhole(1.0, x)["chi_th"] for x in np.linspace(0.0, m_over_a_max, n)]
    return _pick(vals, kind)


@extractor
def single_seed_areal_factor(minus: str = "single_eps_m1e2_t100", plus: str = KICK_P2,
                             unkicked: str = LEVEL3) -> float:
    """Fractional change of the throat's areal radius per unit seed amplitude
    at t = 0: (R0(+eps) - R0(-eps)) / (2 eps R0(unkicked))."""
    eps = float(params(plus)["wormhole_seed_amplitude_A"])
    return float((_areal(plus)[0, 1] - _areal(minus)[0, 1]) / (2.0 * eps * _areal(unkicked)[0, 1]))


# ======================================================== numerical setup
@extractor
def single_grid(run: str, what: str) -> float:
    """dx0 = L/N1; dx_finest = dx0/2^max_level; half_width = the finest level's
    box half-width per throat, tagging_L * 2^-(max_level+1) (FixedGridsTagger
    tags |x| < tagging_L 2^-(l+2) on level l, which lays level l+1)."""
    p = params(run)
    dx0 = float(p["L"]) / float(p["N1"])
    lmax = int(p["max_level"])
    if what == "dx0":
        return dx0
    if what == "dx_finest":
        return dx0 / 2 ** lmax
    if what == "half_width":
        return float(p.get("tagging_L", p["L"])) * 2.0 ** -(lmax + 1)
    raise ValueError(what)


@extractor
def single_pair_separation(run: str) -> float:
    """|x_B - x_A| of the two placed throats (params)."""
    p = params(run)
    return abs(float(p["wormhole_centerB"].split()[0]) - float(p["wormhole_centerA"].split()[0]))


@extractor
def single_mms_excess(run: str, kind: str = "max", centre: str | None = None,
                      t0: float | None = None, t1: float | None = None) -> float:
    """100 (2 M_MS / R - 1) on the scan's MOTS rows: how far the Misner-Sharp
    mass of the star-shaped scan's surface exceeds R/2."""
    a = _mots(run, centre)
    a = a[_sel(a[:, 0], t0, t1)]
    return _pick(list(100.0 * (2.0 * a[:, 2] / a[:, 1] - 1.0)), kind)


# ================================================== the instability mode
def _log_slope(t: np.ndarray, d: np.ndarray, t0: float, hw: float) -> float:
    i0 = int(np.argmin(np.abs(t - (t0 - hw))))
    i1 = int(np.argmin(np.abs(t - (t0 + hw))))
    if d[i0] == 0 or d[i1] == 0 or np.sign(d[i0]) != np.sign(d[i1]):
        return float("nan")
    return float((math.log(abs(d[i1])) - math.log(abs(d[i0]))) / (t[i1] - t[i0]))


def _plateau(run: str, lo: float, hi: float, hw: float = 3.0) -> tuple[float, float]:
    """plot_branches.plateau_rate: the +-3 sliding log-slope of |R - R(0)| on
    centres t = 33, 36, ..., 66, averaged over the centres in [lo, hi]."""
    a = _areal(run)
    d = a[:, 1] - a[0, 1]
    v = np.array([_log_slope(a[:, 0], d, t, hw) for t in range(33, 67, 3) if lo <= t <= hi])
    return float(v.mean()), float(v.std())


@extractor
def single_plateau(run: str, what: str = "tau", lo: float = 49.0, hi: float = 61.0,
                   round_sf: int | None = None) -> float:
    """The unstable mode's plateau rate (plot_branches.plateau_rate): what =
    rate, sd (its spread over the centres) or tau = 1/rate; round_sf rounds
    the result to that many significant figures (the value the article then
    carries forward, e.g. tau = 5.9 in Table II)."""
    rate, sd = _plateau(run, lo, hi)
    val = {"rate": rate, "sd": sd, "tau": 1.0 / rate}[what]
    if round_sf:
        val = float(f"{val:.{round_sf}g}")
    return val


@extractor
def single_proper_efold(run: str) -> float:
    """T = tau alpha_th / R_star: the proper-time e-fold in light-crossing units."""
    dh = _drainhole(*_am(run))
    return single_plateau(run=run, what="tau") * dh["alpha_th"] / dh["R_min"]


@extractor
def single_ggs_excess(runs: list[str], t_ggs: float | None = None) -> float:
    """Largest excess, in percent, of the measured T over the top of the
    Gonzalez-Guzman-Sarbach prediction interpolated to m/a = 0.5 (T_PREDICTED
    of results/merger/analysis/single_throat_instability.py, 0.68-0.76)."""
    if t_ggs is None:
        import single_throat_instability as sti  # the pack's analysis module (lib puts it on the path)
        t_ggs = float(sti.T_PREDICTED[1])
    return max(100.0 * (single_proper_efold(run=r) / t_ggs - 1.0) for r in runs)


@extractor
def single_hold_time(run: str, threshold: float, ref: str | float = "R0") -> float:
    """First time |R/ref - 1| exceeds threshold (plot_branches.crossing); ref =
    R0 (the run's own t = 0 reading, BRANCHES.md), Rstar (closed form) or a number."""
    a = _areal(run)
    r0 = _ref_radius(run, ref)
    return _crossing(a[:, 0], (a[:, 1] - r0) / r0, threshold)


@extractor
def single_max_dev(run: str, t1: float, ref: str | float = "R0", t0: float = 0.0) -> float:
    """max |R/ref - 1| in percent over t0 <= t <= t1."""
    a = _areal(run)
    r0 = _ref_radius(run, ref)
    m = _sel(a[:, 0], t0, t1)
    return float(100.0 * np.max(np.abs(a[m, 1] / r0 - 1.0)))


@extractor
def single_dev_at(run: str, t: float | None = None, ref: str | float = "Rstar",
                  digits: bool = False) -> float:
    """|R(t)/ref - 1| in percent (t = None: the last reading); digits=True
    returns -log10 |R/ref - 1| instead, the number of digits held."""
    a = _areal(run)
    r = float(a[-1, 1]) if t is None else float(np.interp(t, a[:, 0], a[:, 1]))
    dev = abs(r / _ref_radius(run, ref) - 1.0)
    return -math.log10(dev) if digits else 100.0 * dev


@extractor
def single_onset_shift(kind: str, fine: str = LEVEL4, coarse: str = LEVEL3,
                       thresholds: tuple[float, ...] = (1e-3, 1e-2, 1e-1)) -> float:
    """min/max over thresholds of the delay of |R - R0|/R0 crossing the
    threshold from the coarse to the fine level (BRANCHES.md Sec. 4)."""
    shifts = [single_hold_time(run=fine, threshold=th) - single_hold_time(run=coarse, threshold=th)
              for th in thresholds]
    return _pick(shifts, kind)


# ================================================ declared seeds, branching
@extractor
def single_pair_crossing(minus: str, plus: str) -> float:
    """Where the +-eps twins cross each other: first zero of R(-eps) - R(+eps)
    on their common output times (plot_seed_branches)."""
    a, b = _areal(minus), _areal(plus)
    tt = np.intersect1d(np.round(a[:, 0], 6), np.round(b[:, 0], 6))
    return _zero_crossing(tt, np.interp(tt, a[:, 0], a[:, 1]) - np.interp(tt, b[:, 0], b[:, 1]))


@extractor
def single_pair_crossing_mean(pairs: list[list[str]]) -> float:
    return float(np.mean([single_pair_crossing(minus=m, plus=p) for m, p in pairs]))


@extractor
def single_mots(run: str, what: str, centre: str | None = "A") -> float:
    """One number of a run's MOTS history on the oriented scan (centre A = the
    throat-centred fine scan, as plot_horizon_regrowth; None = any centre):
    first_time / first_R / first_M, last_time / last_R / last_M, floor_time /
    floor_R / floor_M (at the radius minimum), regrowth_R / regrowth_M
    (100 (last/floor - 1), plot_horizon_regrowth._gain)."""
    a = _mots(run, centre)
    i = int(np.nanargmin(a[:, 1]))
    col = {"time": 0, "R": 1, "M": 2}
    head, _, tail = what.partition("_")
    if head == "first":
        return float(a[0, col[tail]])
    if head == "last":
        return float(a[-1, col[tail]])
    if head == "floor":
        return float(a[i, col[tail]])
    if head == "regrowth":
        return float(100.0 * (a[-1, col[tail]] / a[i, col[tail]] - 1.0))
    raise ValueError(what)


@extractor
def single_mots_over_runs(runs: list[str], what: str, kind: str, centre: str | None = "A") -> float:
    return _pick([single_mots(run=r, what=what, centre=centre) for r in runs], kind)


@extractor
def single_matched_delay(big: str, small: str, levels: list[float], kind: str) -> float:
    """How much later the smaller kick's horizon reaches each radius the larger
    kick's reached: t_small(R) - t_big(R) at the given MOTS radii, min or max."""
    def t_at(a: np.ndarray, level: float) -> float:
        i = np.where(a[:, 1] <= level)[0]
        if not i.size or i[0] == 0:
            raise ValueError(f"radius {level} not bracketed")
        j = int(i[0])
        return float(a[j - 1, 0] + (level - a[j - 1, 1]) * (a[j, 0] - a[j - 1, 0]) / (a[j, 1] - a[j - 1, 1]))
    hb, hs = _mots(big), _mots(small)
    return _pick([t_at(hs, lv) - t_at(hb, lv) for lv in levels], kind)


@extractor
def single_norm(run: str, col: str, t: float = 0.0) -> float:
    """A constraint norm (L2_Ham / L2_Mom) at time t."""
    tt, y = window(run, "constraint_norms.dat", col, "time")
    return float(np.interp(t, tt, y))


@extractor
def single_norm_over_runs(runs: list[str], col: str, t: float, kind: str) -> float:
    return _pick([single_norm(run=r, col=col, t=t) for r in runs], kind)


@extractor
def single_norm_ratio_over(pairs: list[list[str]], col: str, t: float, kind: str) -> float:
    """min/max over (numerator, denominator) run pairs of norm ratio at t."""
    return _pick([single_norm(run=n, col=col, t=t) / single_norm(run=d, col=col, t=t) for n, d in pairs], kind)


@extractor
def single_norm_growth(run: str, col: str, t0: float, t1: float | None = None) -> float:
    """norm(t1) / norm(t0); t1 = None is the last row."""
    tt, y = window(run, "constraint_norms.dat", col, "time")
    y1 = float(y[-1]) if t1 is None else float(np.interp(t1, tt, y))
    return y1 / float(np.interp(t0, tt, y))


@extractor
def single_constraint_onset(runs: list[str], kind: str = "min", factor: float = 1.5,
                            base: tuple[float, float] = (35.0, 55.0), t_from: float = 55.0) -> float:
    """When L2_Ham leaves its floor: the first t >= t_from with H > factor x
    median(H over base), min/max over runs (the registry's 'L2_Ham leaves floor
    at 76.8' for the L = 128 arm is this definition)."""
    onsets = []
    for r in runs:
        tt, h = window(r, "constraint_norms.dat", "L2_Ham", "time")
        floor = float(np.median(h[(tt > base[0]) & (tt < base[1])]))
        g = np.where((tt >= t_from) & (h > factor * floor))[0]
        if not g.size:
            raise ValueError(f"{r}: L2_Ham never leaves {factor} x its floor")
        onsets.append(float(tt[g[0]]))
    return _pick(onsets, kind)


# ============================================== shell scans (level-3 twin)
@functools.lru_cache(maxsize=None)
def _shell_scans() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for line in _campaign_file(SHELL_SCANS).read_text(encoding="utf-8").splitlines():
        if line.startswith("#S "):
            toks = line.split()
            out[toks[1]] = dict(tok.split("=", 1) for tok in toks[2:])
    return out


@extractor
def single_shell_scan(scan: str, key: str) -> float:
    """A summary value of one oriented shell scan of the kept plotfiles
    (branch_shell_scans_2026-09-08.dat, the level-3 chi-regularised twin and
    the level-4 arm; BRANCHES.md Sec. 5)."""
    return float(_shell_scans()[scan][key])


@extractor
def single_shell_mots_times(prefix: str, what: str = "first") -> float:
    """Over the shell scans named prefix* that hold a MOTS: the earliest time
    (first), the latest (last) or the span between them (span)."""
    ts = sorted(float(s["t"]) for name, s in _shell_scans().items()
                if name.startswith(prefix) and int(s["n_mots"]) > 0)
    return {"first": ts[0], "last": ts[-1], "span": ts[-1] - ts[0]}[what]


@extractor
def single_collapse_diag(run: str, col: str, which: str) -> float:
    """collapse_diagnostics.dat: col (min_lapse, min_chi, max_abs_K) at the
    first / last row, or its max / time of max."""
    tt, y = window(run, "collapse_diagnostics.dat", col, "time")
    if which == "first":
        return float(y[0])
    if which == "last":
        return float(y[-1])
    if which == "max":
        return float(np.max(y))
    if which == "max_time":
        return float(tt[int(np.argmax(y))])
    raise ValueError(which)


# ========================================================= inflation branch
@extractor
def single_areal(run: str, which: str) -> float:
    """The ray scan's minimal-surface areal radius: first, last, or last/first (ratio)."""
    a = _areal(run)
    return {"first": float(a[0, 1]), "last": float(a[-1, 1]),
            "ratio": float(a[-1, 1] / a[0, 1])}[which]


@extractor
def single_departure(run: str, twin: str, frac: float = 0.10) -> float:
    """First output time at which the arm's areal radius differs from its
    twin's by frac (plot_single_collapse / plot_single_inflation)."""
    a, b = _areal(run), _areal(twin)
    dep = np.abs(a[:, 1] / np.interp(a[:, 0], b[:, 0], b[:, 1]) - 1.0) >= frac
    if not dep.any():
        raise ValueError("never departs")
    return float(a[dep, 0][0])


@extractor
def single_anti_trapped(run: str, which: str, centre: str | None = None) -> float:
    """First / last scan time with an anti-trapped shell (theta_+- > 0)."""
    hdr, rows = _hscan(run)
    it, ic, ia = (hdr.index(k) for k in ("time", "centre", "n_anti_trapped"))
    ts = sorted(float(r[it]) for r in rows
                if int(float(r[ia])) > 0 and (centre is None or r[ic] == centre))
    return ts[0] if which == "first" else ts[-1]


@extractor
def single_far_image_rows(run: str, what: str, r_above: float = 30.0) -> float:
    """The late 'theta_+ = 0' rows at large R, the image of the far universe's
    compactified infinity: first_time, or mean_R of those rows."""
    a = _mots(run, None)
    a = a[a[:, 1] > r_above]
    return float(a[0, 0]) if what == "first_time" else float(np.mean(a[:, 1]))


@extractor
def single_profile_trough(run: str, t: float, field: str = "chi_min") -> float:
    """Radius of the minimum of a shell profile (core_radial_profile.dat) at time t."""
    path = run_dir(run) / "core_radial_profile.dat"
    with path.open(encoding="utf-8") as fh:
        names: list[str] = []
        for line in fh:
            if not line.startswith("#"):
                break
            names = line.lstrip("#").split()
    data = np.loadtxt(path, comments="#")
    idx = [i for i, n in enumerate(names) if n.startswith(field + "_r")]
    radii = np.array([float(names[i].split("_r")[-1]) for i in idx])
    row = data[int(np.argmin(np.abs(data[:, 0] - t)))]
    return float(radii[int(np.argmin(row[idx]))])


@extractor
def single_profile_shells(run: str, field: str = "chi_min") -> float:
    """How many radial shells core_radial_profile.dat carries (columns field_r*)."""
    with (run_dir(run) / "core_radial_profile.dat").open(encoding="utf-8") as fh:
        names: list[str] = []
        for line in fh:
            if not line.startswith("#"):
                break
            names = line.lstrip("#").split()
    return float(sum(1 for n in names if n.startswith(field + "_r")))


def _lnr_slope(run: str, t0: float, t1: float) -> float:
    a = _areal(run)
    m = _sel(a[:, 0], t0, t1)
    return float(np.polyfit(a[m, 0], np.log(a[m, 1]), 1)[0])


@extractor
def single_window_rate(run: str, t0: float, t1: float, what: str = "rate") -> float:
    """Least-squares d ln R / dt of the areal radius over [t0, t1] (inclusive
    unit-cadence samples); what = rate or doubling (ln 2 / rate)."""
    s = _lnr_slope(run, t0, t1)
    return s if what == "rate" else math.log(2.0) / s


@extractor
def single_peak_window_rate(run: str, width: float = 10.0, what: str = "rate",
                            t_from: float = 20.0) -> float:
    """The largest d ln R / dt over sliding windows [s, s + width] with integer
    starts s >= t_from: what = rate, doubling (ln 2 / rate) or centre (s + width/2)."""
    a = _areal(run)
    best = None
    for s in range(int(t_from), int(a[-1, 0] - width) + 1):
        k = _lnr_slope(run, s, s + width)
        if best is None or k > best[0]:
            best = (k, s)
    k, s = best
    return {"rate": k, "doubling": math.log(2.0) / k, "centre": s + 0.5 * width}[what]


@extractor
def single_local_rate(run: str, t: float, hw: float = 3.0, ref: str | float = "Rstar") -> float:
    """The +-hw log-slope of |R - ref| at time t -- plot_branches' sliding rate, taken
    about the static R_star rather than R(0), since a kicked arm starts displaced:
    the local growth rate of the deviation, for an arm that shows no plateau."""
    a = _areal(run)
    return _log_slope(a[:, 0], a[:, 1] - _ref_radius(run, ref), t, hw)


@extractor
def single_flow_selftest(what: str) -> float:
    """The shape-free flow finder's analytic self-test, read from its packed log
    (campaign/05_binary_spiral/flow_finder_selftest.log, ah_flow_finder.py --analytic
    all): 'schw_R' / 'schw_M' = the worst percent error of R against 2M = 1 and of
    M_MS against M = 0.5 over every Schwarzschild seed and lmax; 'n_pass' = how many
    of the log's cases passed (Ellis cases pass by finding no surface)."""
    text = _campaign_file("flow_finder_selftest.log").read_text()
    cases = [l for l in text.splitlines() if l.startswith(("schw ", "ellis "))]
    if what == "n_pass":
        return float(sum("PASS" in l for l in cases))
    key, ref = {"schw_R": ("R", 1.0), "schw_M": ("M_MS", 0.5)}[what]
    vals = [float(m.group(1)) for l in cases if l.startswith("schw ")
            for m in [re.search(rf"\b{key}=([0-9.]+) vs", l)] if m]
    if not vals:
        raise ValueError("no Schwarzschild case in the self-test log")
    return float(max(100.0 * abs(v / ref - 1.0) for v in vals))


@extractor
def single_max_rel_diff(run_a: str, run_b: str, file: str = "areal_radius.dat", col: int = 1,
                        t0: float | None = None, t1: float | None = None) -> float:
    """max |b/a - 1| in percent over the two runs' common output times."""
    a = _dedup(stream(run_a, file)[1])
    b = _dedup(stream(run_b, file)[1])
    tt = np.intersect1d(np.round(a[:, 0], 6), np.round(b[:, 0], 6))
    tt = tt[_sel(tt, t0, t1)]
    ya, yb = np.interp(tt, a[:, 0], a[:, col]), np.interp(tt, b[:, 0], b[:, col])
    return float(100.0 * np.max(np.abs(yb / ya - 1.0)))


# ===================================================== lifetime and scale
def _clock(quantity: str) -> float:
    """The drainhole clock in units of M, from the data: Rstar (closed form of
    the production throat), tau (level-3 plateau, rounded to 2 s.f. as Table II
    states tau = 5.9 M), t_eps2 / t_eps3 (first MOTS of the +1e-2 / +1e-3
    arms), t_noise (the unkicked level-3 throat's first scanned MOTS)."""
    if quantity == "Rstar":
        return single_drainhole(quantity="R_min", run=LEVEL3)
    if quantity == "tau":
        return single_plateau(run=LEVEL3, what="tau", round_sf=2)
    if quantity == "t_eps2":
        return single_mots(run=KICK_P2, what="first_time")
    if quantity == "t_eps3":
        return single_mots(run=KICK_P3, what="first_time")
    if quantity == "t_noise":
        return single_shell_mots_times(prefix="ml3", what="first")
    raise ValueError(quantity)


@extractor
def single_physical(quantity: str, mass_msun: float, unit: str) -> float:
    """Table II: a clock entry (see _clock) for a throat of ADM mass mass_msun,
    in km / AU (lengths, G M/c^2) or ms / s / min / h / d (times, G M/c^3)."""
    x = _clock(quantity) * mass_msun
    if unit == "km":
        return x * GM_SUN_KM
    if unit == "AU":
        return x * GM_SUN_KM / AU_KM
    return x * GM_SUN_SECONDS / UNIT_SECONDS[unit]


@extractor
def single_quiet_lifetime(mass_msun: float, eps: float, unit: str = "ms") -> float:
    """t_BH = t_eps2 + tau ln(1e-2/eps) (Table II caption), in physical units."""
    t_bh = _clock("t_eps2") + _clock("tau") * math.log(1e-2 / eps)
    return t_bh * mass_msun * GM_SUN_SECONDS / UNIT_SECONDS[unit]


@extractor
def single_noise_seed() -> float:
    """The truncation seed the unkicked level-3 horizon implies: 1e-2
    exp(-(t_noise - t_eps2)/tau), tau the unrounded level-3 plateau."""
    tau = single_plateau(run=LEVEL3, what="tau")
    return 1e-2 * math.exp(-(_clock("t_noise") - _clock("t_eps2")) / tau)


@extractor
def single_decade_cost() -> float:
    """t_BH(eps = 1e-3) - t_BH(eps = 1e-2)."""
    return _clock("t_eps3") - _clock("t_eps2")


# ==================================================== two throats at rest
@functools.lru_cache(maxsize=None)
def _sign_table() -> tuple[tuple[str, ...], np.ndarray]:
    path = _campaign_file("sign_rule_displacement.dat")
    names: list[str] = []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            toks = line.lstrip("#").split()
            if toks[:1] == ["time"]:
                names = toks
            continue
        if line.strip():
            rows.append([float(v) for v in line.split()])
    return tuple(names), np.array(rows)


@extractor
def single_sign_rule(what: str) -> float:
    """The sign-rule table (sign_rule.py, from the chi_z slice-cache pit
    centroids): the ratio -dsep_flip/dsep_like over its window -- mean, sd
    (ddof 1), n (slices), t_first (the window's first slice) -- recomputed
    from the table's own dsep columns."""
    names, a = _sign_table()
    t = a[:, names.index("time")]
    like, flip = a[:, names.index("dsep_like")], a[:, names.index("dsep_flip")]
    ratio_col = a[:, names.index("ratio")]
    win = np.isfinite(ratio_col)          # the window sign_rule.py wrote (t = 3.5 .. 10.5)
    r = -flip[win] / like[win]
    return {"mean": float(r.mean()), "sd": float(r.std(ddof=1)), "n": float(r.size),
            "t_first": float(t[win][0])}[what]


@extractor
def single_sign_dsep(col: str, t: float) -> float:
    """A separation change of the sign-rule table (dsep_like / dsep_a1 / dsep_flip) at time t."""
    names, a = _sign_table()
    return float(np.interp(t, a[:, names.index("time")], a[:, names.index(col)]))


@extractor
def single_width_ratio(t: float) -> float:
    """dsep(a = 2) / dsep(a = 1) of the like-signed d = 12 pairs at time t."""
    return single_sign_dsep(col="dsep_like", t=t) / single_sign_dsep(col="dsep_a1", t=t)


@functools.lru_cache(maxsize=None)
def _dladder() -> dict[float, float]:
    """d -> displacement at t = 11.5 (separation_ladder_2026-09-04.txt, RESULT)."""
    text = _campaign_file("separation_ladder_2026-09-04.txt").read_text(encoding="utf-8")
    block = text.split("RESULT", 1)[1]
    out = {}
    for line in block.splitlines():
        p = line.split()
        if len(p) >= 3 and re.fullmatch(r"\d+", p[0]) and re.fullmatch(r"\d+\.\d+", p[2]):
            out[float(p[0])] = float(p[2])
        elif out and not p:
            break
    return out


@extractor
def single_dladder(d: float, what: str = "displ") -> float:
    """The separation ladder at t = 11.5: displacement, or F d^2 (displacement x d^2)."""
    x = _dladder()[float(d)]
    return x if what == "displ" else x * float(d) ** 2


@extractor
def single_offset_delta(kind: str) -> float:
    """delta of F ~ (d + delta)^-2 solved from each pair of rungs; min or max."""
    lad = _dladder()
    vals = []
    for (d1, f1), (d2, f2) in itertools.combinations(sorted(lad.items()), 2):
        q = math.sqrt(f1 / f2)
        vals.append((d2 - q * d1) / (q - 1.0))
    return _pick(vals, kind)


@extractor
def single_offset_prediction(d: float, model: str, fit: tuple[float, ...] = (12.0, 14.0, 16.0)) -> float:
    """Displacement predicted at d: model 'offset' = A/(d+delta)^2 least-squares
    fitted on the fit rungs, 'inverse_square' = scaled from the first rung as d^-2."""
    lad = _dladder()
    if model == "inverse_square":
        d0 = fit[0]
        return lad[d0] * (d0 / d) ** 2
    from scipy.optimize import curve_fit
    x = np.array(fit)
    y = np.array([lad[v] for v in fit])
    (amp, delta), _ = curve_fit(lambda s, A, dl: A / (s + dl) ** 2, x, y, p0=(100.0, 3.0))
    return float(amp / (d + delta) ** 2)


@functools.lru_cache(maxsize=None)
def _aladder() -> dict[float, dict[float, float]]:
    """t -> {a: displacement} (scalar_charge_apoints_2026-09-04.txt, 'displacement' table)."""
    text = _campaign_file("scalar_charge_apoints_2026-09-04.txt").read_text(encoding="utf-8")
    block = text.split("displacement (separation minus its t = 0 value)", 1)[1]
    lines = block.splitlines()
    times = [float(x) for x in re.findall(r"t=(\d+(?:\.\d+)?)", lines[1])]
    out: dict[float, dict[float, float]] = {t: {} for t in times}
    for line in lines[2:]:
        p = line.split()
        if len(p) != len(times) + 1:
            break
        for t, v in zip(times, p[1:]):
            out[t][float(p[0])] = float(v)
    return out


@extractor
def single_aladder(a: float, t: float = 11.0) -> float:
    """The width ladder's displacement of the like-signed d = 12 pair of throat
    width a at time t."""
    return _aladder()[float(t)][float(a)]


@extractor
def single_width_exponent(kind: str, times: tuple[float, ...] = (8.0, 10.0, 11.0)) -> float:
    """Effective exponent n of displacement ~ a^n: a power law through the a = 1
    point fitted to the ratios dsep(a)/dsep(1) at each time; min or max over times."""
    vals = []
    for t in times:
        row = _aladder()[float(t)]
        x = np.log(np.array([a for a in sorted(row) if a != 1.0]))
        y = np.log(np.array([row[a] / row[1.0] for a in sorted(row) if a != 1.0]))
        vals.append(float(np.sum(x * y) / np.sum(x * x)))
    return _pick(vals, kind)


@functools.lru_cache(maxsize=None)
def _placement() -> tuple[np.ndarray, np.ndarray]:
    """(d, R_mouth) of the one-step placement probes: mean of the mouth-A/B
    minimum areal radius at t = 0 (placement_curve.py), d = |x_B - x_A|."""
    pts = []
    for _, d in lib.iter_runs(lib.PACK):
        if not re.fullmatch(r"place_d\d+_step1", d.name):
            continue
        hdr, rows = _hscan(d.name)
        it, ic, ir = (hdr.index(k) for k in ("time", "centre", "R_min"))
        mouths = [float(r[ir]) for r in rows if r[ic] in ("A", "B") and float(r[it]) == 0.0]
        if mouths:
            pts.append((single_pair_separation(run=d.name), float(np.mean(mouths))))
    pts.sort()
    return np.array([p[0] for p in pts]), np.array([p[1] for p in pts])


@extractor
def single_placement(d: float | None = None, what: str = "R") -> float:
    """The placement curve: R (per-mouth radius) or excess (percent above the
    isolated R_star) of the probe at separation d; what = slope gives the
    exponent of the excess, -d ln(excess)/d ln d over all probes."""
    ds, rs = _placement()
    rstar = single_drainhole(quantity="R_min", run=LEVEL3)
    if what == "slope":
        return float(-np.polyfit(np.log(ds), np.log(rs / rstar - 1.0), 1)[0])
    r = float(rs[int(np.argmin(np.abs(ds - d)))])
    return r if what == "R" else 100.0 * (r / rstar - 1.0)


@functools.lru_cache(maxsize=None)
def _scout_residual(scout: str = "merge_headon_flip_d8_v1_t100", contact: float = 2.5) -> np.ndarray:
    """(t, sep, response %, in_range) of the head-on scout's mouths against the
    placement curve at the separation reached (placement_curve.py Sec. 2)."""
    ds, rs = _placement()
    sep = {round(t, 3): s for t, s in zip(*window(scout, "binary_throat_diagnostics.dat", "separation", "time"))}
    hdr, rows = _hscan(scout)
    it, ic, ir = (hdr.index(k) for k in ("time", "centre", "R_min"))
    by_t: dict[float, list[float]] = {}
    for r in rows:
        if r[ic] in ("A", "B"):
            by_t.setdefault(float(r[it]), []).append(float(r[ir]))
    out = []
    for t in sorted(by_t):
        s = sep.get(round(t, 3))
        if s is None or s < contact:
            continue
        rp = float(np.interp(s, ds, rs))
        inside = ds.min() - 1e-9 <= s <= ds.max() + 1e-9
        out.append((t, s, 100.0 * (np.mean(by_t[t]) / rp - 1.0), float(inside)))
    return np.array(out)


@extractor
def single_scout(what: str, t: float | None = None) -> float:
    """The scout's own response: response (percent, at time t), plateau_end
    (last time the tracked separation still equals its t = 0 value), or
    last_in_range (last time inside the probed separations)."""
    a = _scout_residual()
    if what == "response":
        return float(a[int(np.argmin(np.abs(a[:, 0] - t))), 2])
    if what == "plateau_end":
        return float(a[a[:, 1] == a[0, 1], 0][-1])
    if what == "last_in_range":
        return float(a[a[:, 3] > 0, 0][-1])
    raise ValueError(what)


# ========================================================= the L = 512 arm (F4)
F4 = "single_eps_m1e2_L512_ml5_oct_t400"


@functools.lru_cache(maxsize=None)
def _f4(run: str = F4) -> dict[str, float]:
    """The L = 512, level-5 kicked arm to T_WALL, by plot_single_inflation_L512's
    own method -- imported, so the page, the paper's figure (plot_single_inflation)
    and the ledger cannot drift apart: the record cut where the crash reaches it,
    the onset fit R0 (1 + A e^(t/T)), Shinkai-Hayward's fit in the neck's proper
    time, and the theta_k = 0 track to its first jump."""
    from grteclyn_wrapper.visualisation.wormhole_merger import plot_single_inflation_L512 as m

    nh = m.record(run_dir(run))["nh"]
    nh = nh[nh[:, 0] <= m.T_WALL + 1e-9]
    t, R, alpha, R_hk = nh[:, 0], nh[:, 2], nh[:, 5], nh[:, 14]
    on = m.onset_fit(t, R)
    sh = m.sh_fit(t, R, alpha)
    kk, _ = m.theta_k_track(R_hk)
    return {"R0": on["R0"], "R_wall": float(np.interp(m.T_WALL, t, R)),
            "alpha0": float(alpha[0]), "alpha_wall": float(np.interp(m.T_WALL, t, alpha)),
            "efold": on["T"], "fit_t0": on["t0"], "fit_t1": on["t1"],
            "sh_rate": sh["H"] * on["R0"], "linear_rate": sh["H_linear"] * on["R0"],
            "sh_t0": sh["t0"], "sh_t1": sh["t1"],
            "sh_local_lo": float(np.nanmin(sh["local"][sh["mask"]])),
            "sh_local_hi": float(np.nanmax(sh["local"][sh["mask"]])),
            "tau_late": float(sh["tau"][-1] - sh["tau1"]),
            "horizon_R": float(R_hk[kk[-1]]), "horizon_t": float(t[kk[-1]])}


@extractor
def single_f4(what: str, run: str = F4) -> float:
    """The L = 512 arm (plot_single_inflation_L512, plot_single_inflation (a)-(c)):
    R0 and R_wall (the neck's full-metric areal radius at t = 0 and at T_WALL),
    alpha0 and alpha_wall (the lapse at the neck, likewise),
    ratio (R_wall / R0), efold (T of the onset fit), fit_t0 / fit_t1 (its window),
    sh_rate (H R0 of Shinkai-Hayward's fit over their window), sh_t0 / sh_t1 (the
    window), sh_local_lo / sh_local_hi (the local H R0 inside it), tau_late (the
    neck's proper time from the window's end to T_WALL), linear_rate (H R0 of the linear mode,
    e-fold 5.13 t at the static throat's lapse), horizon_R / horizon_t (theta_k = 0
    at its last sample before the first jump)."""
    d = _f4(run)
    return d["R_wall"] / d["R0"] if what == "ratio" else float(d[what])
