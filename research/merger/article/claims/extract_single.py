"""Extractors for the ledger area 'single': the model, the numerical setup, the
single wormhole and two throats at rest (research.tex Secs. II-V).

Every function registered here returns ONE float recomputed from the tracked
pack (results/merger), never from the run tree.  Runs are named, and resolved
through lib.run_dir; the few group-level reduced tables (the level-3 shell
scans, the sign-rule table, the two ladder notes) are
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
  sign_rule                 the sign-rule table and its ratio
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
M_SUN_KG = 1.3271244e20 / 6.67430e-11                # G M_sun / G (CODATA 2018): 1.98841e30 kg
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


# The small-amplitude windows of the unkicked arms (validation A10, 2026-10-06):
# |R/R(0) - 1| stays below 4 % there (level 3: 0.4-2.9 %, level 4: 0.1-3.9 %),
# where the mode is linear.  The plateau above (centres t = 49-61) reaches 19 %
# at level 3, where the collapse slows (tau 5.9-6.1), so it is no linear rate.
SMALL_AMP = {LEVEL3: (40.0, 50.0), LEVEL4: (40.0, 60.0)}


@extractor
def single_efold(run: str, t0: float | None = None, t1: float | None = None) -> float:
    """The unstable mode's e-fold at small amplitude: 1 / the least-squares
    slope of ln |R - R(0)| over the unit-cadence samples in [t0, t1]
    (default: the run's SMALL_AMP window)."""
    if t0 is None or t1 is None:
        t0, t1 = SMALL_AMP[run]
    a = _areal(run)
    m = _sel(a[:, 0], t0, t1)
    return float(1.0 / np.polyfit(a[m, 0], np.log(np.abs(a[m, 1] - a[0, 1])), 1)[0])


@extractor
def single_proper_efold(run: str) -> float:
    """T = tau alpha_th / R_star, tau the small-amplitude e-fold (single_efold):
    the proper-time e-fold in light-crossing units."""
    dh = _drainhole(*_am(run))
    return single_efold(run=run) * dh["alpha_th"] / dh["R_min"]


@extractor
def single_ggs_excess(runs: list[str], t_ggs: float | None = None) -> float:
    """Largest |T / t_ggs - 1|, in percent, over the runs: the measured
    small-amplitude T against the linear T (default: the top of the
    Gonzalez-Guzman-Sarbach prediction interpolated to m/a = 0.5, T_PREDICTED
    of analysis/wormhole_merger/single_throat/instability.py)."""
    if t_ggs is None:
        from grteclyn_wrapper.analysis.wormhole_merger.single_throat import instability as sti
        t_ggs = float(sti.T_PREDICTED[1])
    return max(100.0 * abs(single_proper_efold(run=r) / t_ggs - 1.0) for r in runs)


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
def single_mots(run: str, what: str, centre: str | None = "A", t_max: float | None = None) -> float:
    """One number of a run's MOTS history on the oriented scan (centre A = the
    throat-centred fine scan, as plot_horizon_regrowth; None = any centre):
    first_time / first_R / first_M, last_time / last_R / last_M, floor_time /
    floor_R / floor_M (at the radius minimum), regrowth_R / regrowth_M
    (100 (last/floor - 1), plot_horizon_regrowth._gain).  t_max cuts the
    history there (a run's trust window, trust_windows.tsv)."""
    a = _mots(run, centre)
    if t_max is not None:
        a = a[_sel(a[:, 0], None, t_max)]
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


def _free_offset_efold(t: np.ndarray, r: np.ndarray) -> float:
    """tau of the least-squares R = c + B exp(t/tau), c and B free (tau on a 0.005 grid)."""
    best = (math.inf, math.nan)
    for tau in np.arange(2.0, 12.0, 0.005):
        x = np.c_[np.ones_like(t), np.exp((t - t[0]) / tau)]
        res = float(np.sum((x @ np.linalg.lstsq(x, r, rcond=None)[0] - r) ** 2))
        best = min(best, (res, float(tau)))
    return best[1]


@extractor
def single_boost_record(what: str, run: str = "single_boost_p045_lbf_t050") -> float:
    """The exact-boost throat of Sec. IV D on its round-scan A rows, one-sample
    scan glitches dropped by plot_single_throat_row.moving_record (the rule is
    stated there): hold_max (largest rise above R(0) before the fall, percent),
    peak_time, one_pct (first fall 1 % below R(0), interpolated), tau_lo /
    tau_hi (the collapse e-fold, free-offset fits R = c + B e^(t/tau) over
    [t0, t1], t0 = 28, 30, ..., 36, t1 = 42, 44: inside its t = 44.5 trust window)."""
    wm = __import__("grteclyn_wrapper.visualisation.wormhole_merger.plot_single_throat_row",
                    fromlist=["moving_record"])
    a = wm.moving_record(lib.PACK, run)
    t, r = a[:, 0], a[:, 1]
    x = r / r[0] - 1.0
    i_pk = int(np.argmax(np.where(t <= 40.0, r, -np.inf)))
    if what == "hold_max":
        return float(100.0 * x[i_pk])
    if what == "peak_time":
        return float(t[i_pk])
    if what == "one_pct":
        i = int(np.nonzero((x < -0.01) & (t > t[i_pk]))[0][0])
        return float(np.interp(-0.01, [x[i], x[i - 1]], [t[i], t[i - 1]]))
    taus = [_free_offset_efold(t[_sel(t, t0, t1)], r[_sel(t, t0, t1)])
            for t0 in (28, 30, 32, 34, 36) for t1 in (42, 44)]
    return {"tau_lo": min(taus), "tau_hi": max(taus)}[what]


@extractor
def single_seed_floor_ratio(eps2: float = 0.01) -> float:
    """Fig. 11(b)'s own measure (plot_seed_linearity): rms Re Psi4^{2,0} over its
    WINDOW at R_SHOW for the eps2 kicked arm, over the level-4 spherical control's."""
    m = __import__("grteclyn_wrapper.visualisation.wormhole_merger.plot_seed_linearity",
                   fromlist=["_l2m0"])
    seed = lib.PACK / "campaign" / m.GROUP / m.SEED_DIR
    t, y = m._l2m0(seed / m.ARMS[eps2] / "psi4_mode_l2m0.dat")
    tc, yc = m._l2m0(seed / m.CONTROL / "psi4_mode_l2m0.dat")
    return float(m._rms(t, y[m.R_SHOW]) / m._rms(tc, yc[m.R_SHOW]))


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
    the production throat), tau (the level-3 small-amplitude e-fold, unrounded;
    the clock's arms are level 3), t_eps2 / t_eps3 (first MOTS of the +1e-2 /
    +1e-3 arms), t_noise (the unkicked level-3 throat's first scanned MOTS)."""
    if quantity == "Rstar":
        return single_drainhole(quantity="R_min", run=LEVEL3)
    if quantity == "tau":
        return single_efold(run=LEVEL3)
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
def single_traveller(mass_kg: float, mass_msun: float, unit: str = "M") -> float:
    """The traversal budget of Sec. IV F: a traveller of mass_kg seeding the
    mode at eps = m/M, put through the Table II law t_BH = t_eps2 + tau
    ln(1e-2/eps); unit "M" gives it in units of the throat's mass, otherwise
    in physical units (single_quiet_lifetime)."""
    eps = mass_kg / (mass_msun * M_SUN_KG)
    if unit == "M":
        return _clock("t_eps2") + _clock("tau") * math.log(1e-2 / eps)
    return single_quiet_lifetime(mass_msun=mass_msun, eps=eps, unit=unit)


@extractor
def single_noise_seed() -> float:
    """The truncation seed the unkicked level-3 horizon implies: 1e-2
    exp(-(t_noise - t_eps2)/tau), tau the level-3 small-amplitude e-fold."""
    tau = _clock("tau")
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


@functools.lru_cache(maxsize=None)
def _matched_table() -> tuple[tuple[str, ...], "np.ndarray"]:
    """matched_rest_displacement.dat: the mode-3 (csm) rest pairs' separation changes."""
    path = _campaign_file("matched_rest_displacement.dat")
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
def single_matched_sign_rule(what: str) -> float:
    """The mode-3 rest pairs' pull-to-push ratio -dsep_flip_d12/dsep_like_d12
    over the sign-rule window t = 3.5..10.5 -- mean, sd (ddof 1), n --
    recomputed from the table's 4-decimal dsep columns (matched_rest.py's
    header states 1.463 +/- 0.023 from its unrounded stream)."""
    names, a = _matched_table()
    t = a[:, names.index("time")]
    like = a[:, names.index("dsep_like_d12")]
    flip = a[:, names.index("dsep_flip_d12")]
    win = (t >= 3.5) & (t <= 10.5)
    r = -flip[win] / like[win]
    return {"mean": float(r.mean()), "sd": float(r.std(ddof=1)), "n": float(r.size)}[what]


@extractor
def single_matched_closed(t: float) -> float:
    """How much of its gap the opposite-signed d = 12 rest pair has closed by time
    t, in percent: -dsep_flip_d12(t) / sep(0), sep(0) from the table's header."""
    names, a = _matched_table()
    head = _campaign_file("matched_rest_displacement.dat").read_text(encoding="utf-8")
    sep0 = float(re.search(r"ctrl_flip_d12_csm: .*?sep\(0\) = ([\d.]+)", head).group(1))
    flip = np.interp(t, a[:, names.index("time")], a[:, names.index("dsep_flip_d12")])
    return float(-100.0 * flip / sep0)


@extractor
def single_matched_dsep(d: int, t: float) -> float:
    """A mode-3 like pair's separation change at time t."""
    names, a = _matched_table()
    return float(np.interp(t, a[:, names.index("time")], a[:, names.index(f"dsep_like_d{d}")]))


@extractor
def single_matched_ladder_dev(t: float) -> float:
    """Largest deviation (%) of the mode-3 like-pair ladder from the superposed
    one at time t, over d = 12/14/16/18 (the superposed values from _dladder)."""
    old = _dladder()
    devs = [abs(single_matched_dsep(d=int(d), t=t) / old[d] - 1.0) for d in (12.0, 14.0, 16.0, 18.0)]
    return 100.0 * max(devs)


def _offset_fit_delta(vals: dict) -> float:
    """delta of the least-squares A/(d + delta)^2 through {d: dsep}."""
    from scipy.optimize import curve_fit

    ds = np.array(sorted(vals), dtype=float)
    y = np.array([vals[d] for d in ds])
    popt, _ = curve_fit(lambda d, A, dl: A / (d + dl) ** 2, ds, y, p0=(100.0, 3.0))
    return float(popt[1])


@extractor
def single_matched_offset_delta(which: str) -> float:
    """delta of A/(d + delta)^2 over the full d = 12..18 ladder at t = 11.5:
    'matched' (the mode-3 pairs) or 'superposed' (the old ladder, same fit --
    NOT the d = 12..16 fit of clmOffsetPrediction, whose delta is 3.69)."""
    if which == "matched":
        vals = {d: single_matched_dsep(d=d, t=11.5) for d in (12, 14, 16, 18)}
    else:
        vals = _dladder()
    return _offset_fit_delta(vals)


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


def _ladder_vals(source: str) -> dict:
    """d -> displacement at t = 11.5: 'superposed' (the old ladder file) or
    'matched' (the mode-3 pairs, from matched_rest_displacement.dat)."""
    if source == "matched":
        return {float(d): single_matched_dsep(d=d, t=11.5) for d in (12, 14, 16, 18)}
    return _dladder()


@extractor
def single_dladder(d: float, what: str = "displ", source: str = "superposed") -> float:
    """The separation ladder at t = 11.5: displacement, or F d^2 (displacement x d^2)."""
    x = _ladder_vals(source)[float(d)]
    return x if what == "displ" else x * float(d) ** 2


@extractor
def single_offset_delta(kind: str, source: str = "superposed") -> float:
    """delta of F ~ (d + delta)^-2 solved from each pair of rungs; min or max."""
    lad = _ladder_vals(source)
    vals = []
    for (d1, f1), (d2, f2) in itertools.combinations(sorted(lad.items()), 2):
        q = math.sqrt(f1 / f2)
        vals.append((d2 - q * d1) / (q - 1.0))
    return _pick(vals, kind)


@extractor
def single_offset_prediction(d: float, model: str, fit: tuple[float, ...] = (12.0, 14.0, 16.0),
                             source: str = "superposed") -> float:
    """Displacement predicted at d: model 'offset' = A/(d+delta)^2 least-squares
    fitted on the fit rungs, 'inverse_square' = scaled from the first rung as d^-2."""
    lad = _ladder_vals(source)
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


# The width ladder on matched data (2026-10-05): the mode-3 like pairs at d = 12, a = 2 being
# the separation ladder's d = 12 rung (matched_rest.py; Fig. 4(d), plot_width_ladder).
_MATCHED_WIDTHS = {1.0: "dsep_like_a1", 1.5: "dsep_like_a15", 2.0: "dsep_like_d12", 3.0: "dsep_like_a3"}


def _matched_aladder(t: float) -> dict[float, float]:
    """a -> the mode-3 like pair's displacement at time t (matched_rest_displacement.dat)."""
    names, arr = _matched_table()
    tt = arr[:, names.index("time")]
    return {a: float(np.interp(t, tt, arr[:, names.index(c)])) for a, c in _MATCHED_WIDTHS.items()}


@extractor
def single_matched_aladder(a: float, t: float = 11.5) -> float:
    """The matched width ladder: the d = 12 like pair of throat width a, its displacement at t."""
    return _matched_aladder(t)[float(a)]


@extractor
def single_matched_width_exponent(kind: str, times: tuple[float, ...] = (8.0, 10.0, 11.5)) -> float:
    """Effective exponent n of displacement ~ a^n on the matched width ladder: least squares in
    log-log over a = 1/1.5/2/3 at each time (at t = 11.5 the gold line of Fig. 4(d)); min or
    max over times."""
    vals = []
    for t in times:
        row = _matched_aladder(float(t))
        widths = sorted(row)
        vals.append(float(np.polyfit(np.log(widths), np.log([row[a] for a in widths]), 1)[0]))
    return _pick(vals, kind)


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


@extractor
def single_f4_pop(what: str, run: str = F4) -> float:
    """The inflating branch as a population member (Secs. IV.D and X): areal
    e-folds accumulated in the record, ln(R_wall/R0) for the neck ('efold_neck')
    and ln(R_hk/R0) for the theta_k = 0 boundary at its last clean sample
    ('efold_boundary'); the boundary's mean areal speed d(R_hk)/dt over the
    record ('speed') and over its last 50 units ('speed_late'); and the
    negative energy shed through the coordinate-60 sphere by T_WALL,
    |int -flux_kin dt| raw ('shed_kin') and with the alpha^2 chi^-1/2 factor of
    Sec. VIII.F taken from the packed shell profiles at r = 60 ('shed_geo').
    The kin/geo pair brackets the true outflow: the 1+log front has collapsed
    the lapse at the sphere before the monopole grows."""
    d = _f4(run)
    if what == "efold_neck":
        return math.log(d["R_wall"] / d["R0"])
    if what == "efold_boundary":
        return math.log(d["horizon_R"] / d["R0"])
    names, rows = stream(run, "neck_horizons.dat")
    c = {n: i for i, n in enumerate(names)}
    t, r_hk = rows[:, c["time"]], rows[:, c["R_hk"]]
    i = int(np.argmin(np.abs(t - d["horizon_t"])))
    if what == "speed":
        return (r_hk[i] - r_hk[0]) / t[i]
    if what == "speed_late":
        sel = (t >= t[i] - 50.0) & (t <= t[i])
        return float(np.polyfit(t[sel], r_hk[sel], 1)[0])
    if what in ("shed_kin", "shed_geo"):
        sn, sm = stream(run, "scalar_modes.dat")
        sc = {n: i for i, n in enumerate(sn)}
        ts, flux = sm[:, sc["time"]], sm[:, sc["R60_scalar_flux_kin"]]
        if what == "shed_geo":
            pn, prof = stream(run, "core_radial_profile.dat")
            pc = {n: i for i, n in enumerate(pn)}
            tp = prof[:, pc["time"]]
            alpha = np.interp(ts, tp, prof[:, pc["lapse_min_r60.25"]])
            chi = np.interp(ts, tp, prof[:, pc["chi_min_r60.25"]])
            flux = flux * alpha ** 2 / np.sqrt(chi)
        from grteclyn_wrapper.visualisation.wormhole_merger import plot_single_inflation_L512 as m
        k = ts <= m.T_WALL + 1e-9
        return float(abs(np.trapezoid(-flux[k], ts[k])))
    raise ValueError(f"single_f4_pop: unknown what={what!r}")


@extractor
def single_identical_rows(a: str, b: str, files: list) -> float:
    """Byte identity of two runs' streams: the data-row count of files[0] when every
    listed file holds the same data rows, byte for byte, in both runs (else an error).
    Added 2026-10-06: the Sec. XI bit-reproducibility pair."""
    n = None
    for f in files:
        rows = [[ln for ln in (run_dir(r) / f).read_text().splitlines()
                 if ln.strip() and not ln.startswith("#")] for r in (a, b)]
        if rows[0] != rows[1]:
            raise ValueError(f"{f}: {a} and {b} differ")
        n = len(rows[0]) if n is None else n
    return float(n)
