"""Extractors for the claims-ledger area 'mergers' (ledger_mergers.tsv): the head-on
merger, the spiral merger (merger or escape, plunge and collapse, the curvature wall)
and the controls and systematics -- research.tex Secs. headon, spiral, controls.

Every extractor reads ONLY the tracked pack (results/merger/campaign/...), resolving
runs by name through lib.run_dir.  Where a figure script owns a computation
(plot_headon_collapse's horizon fit, plot_spiral_collapse's core profile,
plot_mouth_growth's per-mouth scan, psi4_math's radiated energy) the extractor calls
that script's own helper, so a ledger number and the figure drawn from it cannot drift.
The figure package is imported lazily, so the other areas' checks do not pay for it.

Conventions every row relies on:
* a DEATH time is the last "ADVANCE at time" in the packed run_tail.log before the NaN
  diagnostic -- the rule refinement_ladder.dat and wall_clocks.dat were built by;
* a stream is sorted by time and de-duplicated (restarts append; thinned files join
  at their death window), keeping the later row of a duplicated time;
* a restarted run reports coarse-grid extrema over its first steps, so `settle`
  drops the first `settle` time units (0.1, as plot_spiral_collapse.SETTLE);
* percentages are returned in percent.
"""

from __future__ import annotations

import functools
import math
import re
import warnings

import numpy as np

from lib import PACK, extractor, params, run_dir, stream

# ---------------------------------------------------------------- stream access
# Column names of the diagnostic streams, in their writer's order.  A restarted run
# writes no header (SmallDataIO keys headers off t = 0), so these stand in for it.
_KNOWN = {
    "collapse_diagnostics.dat": ("time", "min_lapse", "min_chi", "max_abs_K",
                                 "min_lapse_x", "min_lapse_y", "min_lapse_z",
                                 "min_phi", "max_phi", "min_Pi", "max_Pi"),
    "constraint_norms.dat": ("time", "L2_Ham", "L2_Mom"),
    "binary_throat_diagnostics.dat": ("time", "separation", "xA", "yA", "zA", "chiA_min",
                                      "lapseA_min", "xB", "yB", "zB", "chiB_min",
                                      "lapseB_min", "theta_A", "ah_r_A", "theta_B",
                                      "ah_r_B", "theta_common", "ah_r_common"),
    "throat_track.dat": ("time", "xA", "yA", "zA", "chiA_pit", "nA",
                         "xB", "yB", "zB", "chiB_pit", "nB"),
}


def _sort_unique(arr: np.ndarray, decimals: int = 6) -> np.ndarray:
    arr = arr[np.isfinite(arr[:, 0])]
    arr = arr[np.argsort(arr[:, 0], kind="stable")]
    t = np.round(arr[:, 0], decimals)
    keep = np.append(t[1:] != t[:-1], True)          # the later row of a repeated time
    return arr[keep]


@functools.lru_cache(maxsize=256)
def _table(run: str, file: str) -> tuple[tuple[str, ...], np.ndarray]:
    names, arr = stream(run, file)
    known = _KNOWN.get(file)
    if known and len(known) == arr.shape[1]:
        names = known
    return tuple(names), _sort_unique(arr)


def _col(run: str, file: str, col: str | int, settle: float = 0.0):
    names, arr = _table(run, file)
    j = col if isinstance(col, int) else names.index(col)
    t, y = arr[:, 0], arr[:, j]
    keep = np.isfinite(y) & (t >= t[0] + settle - 1e-9)
    return t[keep], y[keep]


def _window(t, y, t0=None, t1=None):
    keep = np.ones(len(t), bool)
    if t0 is not None:
        keep &= t >= t0 - 1e-9
    if t1 is not None:
        keep &= t <= t1 + 1e-9
    if not keep.any():
        raise ValueError(f"no rows in [{t0}, {t1}]")
    return t[keep], y[keep]


def _agg(values, agg: str) -> float:
    return float({"max": np.max, "min": np.min, "mean": np.mean}[agg](values))


# ---------------------------------------------------------------- generic, sort-safe
@extractor
def mergers_value(run: str, file: str, col: str | int, t: float | None = None,
                  at: str | None = None, settle: float = 0.0) -> float:
    """col at time t (linear interpolation on the sorted stream), or at the 'first' /
    'last' row; `settle` drops a restart's first time units."""
    tt, y = _col(run, file, col, settle)
    if at == "first":
        return float(y[0])
    if at == "last":
        return float(y[-1])
    if not tt[0] - 1e-9 <= t <= tt[-1] + 1e-9:
        raise ValueError(f"{run}/{file}: t = {t} outside [{tt[0]}, {tt[-1]}]")
    return float(np.interp(t, tt, y))


@extractor
def mergers_extreme(run: str, file: str, col: str | int, kind: str = "max",
                    t0: float | None = None, t1: float | None = None,
                    what: str = "value", settle: float = 0.0) -> float:
    """max/min of col over [t0, t1]; what = 'value' or 'time' (its first occurrence)."""
    tt, y = _window(*_col(run, file, col, settle), t0, t1)
    i = int(np.argmax(y) if kind == "max" else np.argmin(y))
    return float(y[i] if what == "value" else tt[i])


@extractor
def mergers_first_time(run: str, file: str, col: str | int, op: str, threshold: float,
                       t0: float | None = None, settle: float = 0.0) -> float:
    """First time (sorted stream) at which col op threshold holds."""
    tt, y = _window(*_col(run, file, col, settle), t0, None)
    test = {"<": y < threshold, "<=": y <= threshold,
            ">": y > threshold, ">=": y >= threshold}[op]
    if not test.any():
        raise ValueError(f"{run}/{file}:{col} never {op} {threshold}")
    return float(tt[int(np.argmax(test))])


@extractor
def mergers_ratio(run: str, file: str, col: str | int, t_num: float, t_den: float,
                  settle: float = 0.0) -> float:
    """col(t_num) / col(t_den), each interpolated on the sorted stream."""
    tt, y = _col(run, file, col, settle)
    return float(np.interp(t_num, tt, y) / np.interp(t_den, tt, y))


@extractor
def mergers_rows(run: str, file: str, t0: float, t1: float) -> float:
    """How many distinct output times a stream has in (t0, t1]."""
    names, arr = _table(run, file)
    t = arr[:, 0]
    return float(np.sum((t > t0 + 1e-9) & (t <= t1 + 1e-6)))


# ---------------------------------------------------------------- run logs
_ADVANCE = re.compile(r"ADVANCE at time\s+([0-9.eE+-]+)")
_NAN = re.compile(r"NaN (diagnostic|in )")


@functools.lru_cache(maxsize=256)
def _log_times(run: str) -> tuple[float | None, float | None]:
    """(last ADVANCE time, last ADVANCE time before the first NaN line)."""
    last, before_nan = None, None
    text = (run_dir(run) / "run_tail.log").read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        m = _ADVANCE.search(line)
        if m:
            last = float(m.group(1))
        elif before_nan is None and _NAN.search(line) and last is not None:
            before_nan = last
    return last, before_nan


@extractor
def mergers_death_time(run: str) -> float:
    """The NaN death: last 'ADVANCE at time' before the NaN diagnostic in run_tail.log."""
    last, nan = _log_times(run)
    if nan is None:
        raise ValueError(f"{run}: no NaN in its run_tail.log (last ADVANCE at {last})")
    return nan


@extractor
def mergers_end_time(run: str) -> float:
    """Where a run that did NOT die stopped: its last 'ADVANCE at time' (raises if it
    NaN'd, so 'runs to t = 100' cannot silently pass on a dead arm)."""
    last, nan = _log_times(run)
    if nan is not None:
        raise ValueError(f"{run} died on a NaN at t = {nan}")
    return last


@extractor
def mergers_wall_clock(run: str) -> float:
    """A death time as transcribed in the pack table campaign/.../wall_clocks.dat --
    only for an arm whose packed run_tail.log is a partial copy (see that file)."""
    path = next((PACK / "campaign").rglob("wall_clocks.dat"))
    for line in path.read_text(encoding="utf-8").splitlines():
        toks = line.split()
        if toks and not line.lstrip().startswith("#") and toks[-1] == run:
            return float(toks[4])
    raise LookupError(f"{run} is not a row of {path.name}")


# ---------------------------------------------------------------- parameters
def _vec(run: str, key: str) -> np.ndarray:
    return np.array([float(x) for x in params(run)[key].replace('"', "").split()])


def _num(run: str, key: str) -> float:
    return float(params(run)[key].replace('"', "").split()[0])


@extractor
def mergers_separation(run: str) -> float:
    """Initial coordinate separation |centerB - centerA| of the declared throats."""
    return float(np.linalg.norm(_vec(run, "wormhole_centerB") - _vec(run, "wormhole_centerA")))


@extractor
def mergers_momentum(run: str) -> float:
    """Tangential (Bowen-York) momentum per throat, |momentumA|."""
    return float(np.linalg.norm(_vec(run, "wormhole_momentumA")))


@extractor
def mergers_total_mass(run: str) -> float:
    """Initial-data ADM mass of the pair: the two drainhole mass parameters."""
    return _num(run, "wormhole_drainhole_mass_A") + _num(run, "wormhole_drainhole_mass_B")


@extractor
def mergers_circular_fraction(run: str) -> float:
    """p / p_circ in percent, p_circ = m sqrt((1 + Q) m / 2d): the Newtonian circular
    momentum of two equal throats under gravity plus the opposite-sign scalar pull,
    F = (1 + Q) m^2 / d^2 with Q = (a^2 + m^2) / m^2 (Sec. model:binary)."""
    a, m = _num(run, "wormhole_throat_radius_A"), _num(run, "wormhole_drainhole_mass_A")
    q = (a * a + m * m) / (m * m)
    p_circ = m * math.sqrt((1.0 + q) * m / (2.0 * mergers_separation(run=run)))
    return 100.0 * mergers_momentum(run=run) / p_circ


@extractor
def mergers_restart_time(run: str) -> float:
    """The time a restarted arm starts from: its amr.restart checkpoint's coarse step
    number times the coarse step dt_multiplier * L / N1 (0.01 in every parent here)."""
    chk = re.search(r"Chk(\d+)", params(run)["amr.restart"])
    if not chk:
        raise ValueError(f"{run} is not a restart")
    return int(chk.group(1)) * _num(run, "dt_multiplier") * _num(run, "L") / _num(run, "N1")


@extractor
def mergers_figure_constant(module: str, name: str, index: int | None = None) -> float:
    """A constant a figure script fixes and its caption prints (a fit window, a
    threshold): grteclyn_wrapper.visualisation.wormhole_merger.<module>.<name>[index]."""
    import importlib

    value = getattr(importlib.import_module(
        f"grteclyn_wrapper.visualisation.wormhole_merger.{module}"), name)
    return float(value if index is None else value[index])


@extractor
def mergers_level_factor(lo: str, hi: str) -> float:
    """Resolution ratio between two arms: 2 ** (max_level(hi) - max_level(lo))."""
    return float(2 ** (int(_num(hi, "max_level")) - int(_num(lo, "max_level"))))


# ---------------------------------------------------------------- horizon scans
@functools.lru_cache(maxsize=128)
def _scan(run: str, centre: str = "C") -> dict[str, np.ndarray]:
    """One centre's rows of the oriented horizon_scan.dat, sorted, by header name."""
    names, rows = None, []
    for line in (run_dir(run) / "horizon_scan.dat").read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            toks = line.lstrip("#").split()
            if toks and toks[0] == "time":
                names = toks
            continue
        p = line.split()
        if len(p) >= 19 and p[1] == centre:
            rows.append([float(p[0])] + [float(x) for x in p[2:19]])
    if names is None or not rows:
        raise ValueError(f"{run}: no header or no centre-{centre} rows in horizon_scan.dat")
    cols = [names[0]] + names[2:19]
    arr = _sort_unique(np.array(rows), decimals=4)
    return {c: arr[:, i] for i, c in enumerate(cols)}


def _mots(run: str, centre: str = "C") -> dict[str, np.ndarray]:
    s = _scan(run, centre)
    m = s["n_mots"] > 0
    if not m.any():
        raise ValueError(f"{run}: no MOTS row on centre {centre}")
    return {k: v[m] for k, v in s.items()}


@extractor
def mergers_mots_first(run: str, col: str = "time", centre: str = "C",
                       trapped: bool = False) -> float:
    """col on the first scan row carrying a MOTS (n_mots > 0) -- or, trapped = True, the
    first row with any fully trapped sphere (n_trapped > 0)."""
    s = _scan(run, centre)
    m = (s["n_trapped"] > 0) if trapped else (s["n_mots"] > 0)
    if not m.any():
        raise ValueError(f"{run}: no {'trapped' if trapped else 'MOTS'} row on centre {centre}")
    return float(s[col][int(np.argmax(m))])


@extractor
def mergers_mots_first_all(runs: list, centre: str = "C") -> float:
    """The latest of several arms' first-MOTS times (equal when they agree)."""
    return max(mergers_mots_first(run=r, centre=centre) for r in runs)


@extractor
def mergers_mots_value(run: str, col: str, t: float, centre: str = "C") -> float:
    """col on the MOTS row at time t (a scan row, not interpolated)."""
    s = _mots(run, centre)
    i = int(np.argmin(np.abs(s["time"] - t)))
    if abs(s["time"][i] - t) > 1e-3:
        raise ValueError(f"{run}: no MOTS row at t = {t} (nearest {s['time'][i]})")
    return float(s[col][i])


@extractor
def mergers_mots_compactness(run: str, which: str = "first", centre: str = "C") -> float:
    """2 M_MS / R on the first or last MOTS row of a scan (1 on an exact MOTS)."""
    s = _mots(run, centre)
    i = 0 if which == "first" else -1
    return float(2.0 * s["M_MS_mots"][i] / s["R_mots"][i])


@extractor
def mergers_mots_agreement(a: str, b: str, col: str = "M_MS_mots", centre: str = "C") -> float:
    """Worst 100 |a/b - 1| of a MOTS column over the times both scans carry a MOTS."""
    sa, sb = _mots(a, centre), _mots(b, centre)
    ta, tb = np.round(sa["time"], 3), np.round(sb["time"], 3)
    common, ia, ib = np.intersect1d(ta, tb, return_indices=True)
    if not len(common):
        raise ValueError(f"{a} and {b} share no MOTS time")
    return float(100.0 * np.max(np.abs(sa[col][ia] / sb[col][ib] - 1.0)))


@extractor
def mergers_ensemble_at(ref: str, runs: list, t: float, cols: list,
                        centre: str = "C") -> float:
    """Worst 100 |x_run / x_ref - 1| over the ensemble members and MOTS columns at t."""
    worst = 0.0
    for r in runs:
        for c in cols:
            x = mergers_mots_value(run=r, col=c, t=t, centre=centre)
            x0 = mergers_mots_value(run=ref, col=c, t=t, centre=centre)
            worst = max(worst, abs(x / x0 - 1.0))
    return 100.0 * worst


@extractor
def mergers_ensemble_track(ref: str, run: str, col: str, t0: float,
                           centre: str = "C") -> float:
    """Worst 100 |x_run / x_ref - 1| over the MOTS times both scans share after t0,
    skipping reference rows whose surface sits inside the reference's own frozen core
    (r_mots <= core_fill_radius_full: a surface of the fill, not of the physics --
    FIGURES.md, 'Trap, do not draw')."""
    r_fill = _num(ref, "core_fill_radius_full")
    sa, sb = _mots(run, centre), _mots(ref, centre)
    ta, tb = np.round(sa["time"], 3), np.round(sb["time"], 3)
    common, ia, ib = np.intersect1d(ta, tb, return_indices=True)
    keep = (common >= t0 - 1e-9) & (sb["r_mots"][ib] > r_fill)
    if not keep.any():
        raise ValueError(f"{run} and {ref} share no valid MOTS time after {t0}")
    return float(100.0 * np.max(np.abs(sa[col][ia][keep] / sb[col][ib][keep] - 1.0)))


@extractor
def mergers_headon_fit(run: str, what: str) -> float:
    """plot_headon_collapse's fits through a scan's MOTS track (centre C): 'R_slope'
    (linear fit of R), and M_MS = M_inf + b exp(-(t - t0)/tau) with 'Minf',
    'Minf_err', 'tau', 'tau_err', 't0' and 'ratio' (rms of a line / rms of the fit)."""
    from scipy.optimize import curve_fit

    s = _mots(run)
    t, R, M = s["time"], s["R_mots"], s["M_MS_mots"]
    if what == "t0":
        return float(t[0])
    if what == "R_slope":
        return float(np.polyfit(t, R, 1)[0])

    def settle(x, a, b, tau):
        return a + b * np.exp(-(x - t[0]) / tau)

    pm, cm = curve_fit(settle, t, M, p0=(M[-1], M[0] - M[-1], 25.0), maxfev=40000)
    em = np.sqrt(np.diag(cm))
    rms_lin = np.sqrt(np.mean((M - np.polyval(np.polyfit(t, M, 1), t)) ** 2))
    rms_exp = np.sqrt(np.mean((M - settle(t, *pm)) ** 2))
    return float({"Minf": pm[0], "Minf_err": em[0], "tau": pm[2], "tau_err": em[2],
                  "ratio": rms_lin / rms_exp}[what])


@extractor
def mergers_scan_value(run: str, col: str, t: float | None = None, centre: str = "A",
                       what: str = "at") -> float:
    """A column of a scan centre: at time t ('at'), its 'max', its 'last' row, or the
    first time the column reaches its maximum ('t_of_max')."""
    s = _scan(run, centre)
    if what == "max":
        return float(s[col].max())
    if what == "last":
        return float(s[col][-1])
    if what == "t_of_max":
        return float(s["time"][int(np.argmax(s[col] >= s[col].max() - 1e-12))])
    i = int(np.argmin(np.abs(s["time"] - t)))
    if abs(s["time"][i] - t) > 1e-3:
        raise ValueError(f"{run}: no centre-{centre} row at t = {t}")
    return float(s[col][i])


@extractor
def mergers_star_scan(run: str, files: list, what: str = "first") -> float:
    """First/last slice time of the oriented star-shaped scan logs, after checking that
    NO block of them reports a MOTS ('no MOTS with the corrected orientation')."""
    head = re.compile(r"BinaryWormholePlt\d+\s+t=([\d.]+)")
    times, found = [], 0
    for f in files:
        blocks = re.split(r"(?=BinaryWormholePlt\d+\s+t=)",
                          (run_dir(run) / f).read_text(encoding="utf-8"))
        for blk in blocks:
            m = head.match(blk)
            if not m:
                continue
            times.append(float(m.group(1)))
            if "no MOTS" not in blk:
                found += 1
    if found:
        raise ValueError(f"{run}: {found} scan block(s) report a MOTS")
    return float(min(times) if what == "first" else max(times))


# ---------------------------------------------------------------- tracks and orbits
def _track_sep(run: str):
    names, arr = _table(run, "throat_track.dat")
    d = arr[:, 1:4] - arr[:, 6:9]
    return arr[:, 0], np.linalg.norm(d, axis=1), d


def _sep(run: str, source: str):
    if source == "track":
        t, s, _ = _track_sep(run)
        return t, s
    return _col(run, "binary_throat_diagnostics.dat", "separation")


@extractor
def mergers_sep(run: str, what: str, source: str = "btd", t: float | None = None,
                t0: float | None = None, t1: float | None = None,
                lo: float = 0.3, hi: float = 1.5) -> float:
    """Separation of the throats' chi pits: 'btd' = binary_throat_diagnostics (the chi
    pits), 'track' = throat_track (the merging tracker).  what = 'min', 'argmin' (time of
    the minimum), 'first', 'last', 'at' (time t), or 'mode' -- the plateau the snapped
    tracker holds before a dive: the most common value (3-decimal bins) inside (lo, hi),
    returned unrounded (the median of that bin)."""
    tt, s = _window(*_sep(run, source), t0, t1)
    if what == "min":
        return float(s.min())
    if what == "argmin":
        return float(tt[int(np.argmin(s))])
    if what == "first":
        return float(s[0])
    if what == "last":
        return float(s[-1])
    if what == "at":
        return float(np.interp(t, tt, s))
    if what == "mode":
        v = s[(s > lo) & (s < hi)]
        u, c = np.unique(np.round(v, 3), return_counts=True)
        return float(np.median(v[np.round(v, 3) == u[int(np.argmax(c))]]))
    raise ValueError(what)


@extractor
def mergers_tracker_merge_time(run: str) -> float:
    """First time the throat tracker holds ONE centre for both mouths (separation 0)."""
    t, s, _ = _track_sep(run)
    if not (s < 1e-9).any():
        raise ValueError(f"{run}: the tracker never merges the mouths")
    return float(t[int(np.argmax(s < 1e-9))])


@extractor
def mergers_revolutions(run: str, merged: float = 0.3) -> float:
    """Fraction of a revolution the tracked throat axis sweeps before closest approach
    (throat_track; the record is cut where the tracker merges the mouths, sep <= 0.3)."""
    t, s, d = _track_sep(run)
    n = int(np.argmax(s <= merged)) if (s <= merged).any() else len(s)
    ang = np.unwrap(np.arctan2(d[:n, 1], d[:n, 0]))
    i = int(np.argmin(s[:n]))
    return float(abs(ang[i] - ang[0]) / (2.0 * np.pi))


@extractor
def mergers_pit_revolutions(run: str, what: str = "rev", raw: bool = False) -> float:
    """Fig. 14's reading of a momentum-scan arm (plot_momentum_orbits, its own helpers):
    the fraction of a revolution the chi pits' separation vector sweeps from t = 0 to
    closest approach, taken as the minimum pit separation over the arm's drawn record.
    The pits are binary_throat_diagnostics' barycentres FOLLOWED BY CONTINUITY
    (pit_tracks): that stream labels them by a fixed half-space (x > 0 / x < 0), so its
    labels swap once the separation vector turns past 90 degrees, and an angle read from
    the labels folds back to 180 - theta (every such reading <= 0.25).  The record is cut
    where the figure cuts it (chi floor or a pit hop for a plunge, the trust window) and
    averaged over its two time units (smoothed); raw = True reads the cell-snapped pits.
    Unlike mergers_revolutions (throat_track), the plunges are not stopped where the
    tracker fuses the two centres (separation ~2).  what = 'rev', 't' (time of closest
    approach), 'sep' (the separation there)."""
    from grteclyn_wrapper.visualisation.wormhole_merger import plot_momentum_orbits as pmo

    merges = next((a[5] for a in pmo.ARMS if a[1] == run), True)
    t, one, two, _ = pmo.pit_tracks(run, None, merges)
    end = getattr(pmo, "TRUST_END", {}).get(run)
    if end is not None and t[-1] > end:
        keep = t <= end + 1e-6
        t, one, two = t[keep], one[keep], two[keep]
    if not raw:
        t, one, two = pmo.smoothed(t, one, two)
    d = one - two
    s = np.hypot(d[:, 0], d[:, 1])
    ang = np.unwrap(np.arctan2(d[:, 1], d[:, 0]))
    i = int(np.argmin(s))
    return float({"rev": abs(ang[i] - ang[0]) / (2.0 * np.pi), "t": t[i], "sep": s[i]}[what])


@extractor
def mergers_lone_throat_deviation(run: str, t1: float) -> float:
    """Worst 100 |R_min / R_exact - 1| of a lone throat's areal minimum up to t1, R_exact
    = e^{-u(r_t)} sqrt(a^2 + m^2) at r_t = (m + sqrt(m^2 + a^2)) / 2 (Sec. model)."""
    a, m = _num(run, "wormhole_throat_radius_A"), _num(run, "wormhole_drainhole_mass_A")
    rt = 0.5 * (m + math.sqrt(m * m + a * a))
    x = (rt - a * a / (4.0 * rt)) / a
    u = (m / a) * (math.atan(x) - math.pi / 2.0)
    r_exact = math.exp(-u) * math.sqrt(a * a + m * m)
    tt, R = _window(*_col(run, "areal_radius.dat", 1), None, t1)
    return float(100.0 * np.max(np.abs(R / r_exact - 1.0)))


# ---------------------------------------------------------------- mouths (plot_mouth_growth)
@functools.lru_cache(maxsize=32)
def _mouth_placed(run: str, model: str, interp: str):
    """plot_mouth_growth's scan of a run and its reading against the placement curve
    (results/merger/analysis/mouth_placement.correct).  Read-only: do not mutate."""
    import mouth_placement as mp  # the pack's analysis module (lib puts it on the path)
    from grteclyn_wrapper.visualisation.wormhole_merger import plot_mouth_growth as pmg

    d = run_dir(run)
    s = pmg._scan(d / "horizon_scan.dat")
    c = mp.correct(s["t"], s["RA"], s["sep"], mp.load_curve(PACK),
                   mp.declared_separation(d / "evolution_params.txt"), model, interp)
    return s, c


def _mouth_rms(t, ex, tau: float, seed: float, lo: float, hi: float) -> float:
    """rms of ln(ex) about plot_mouth_growth._tau's line, over the rows it fits."""
    m = (t >= lo - 1e-6) & (t <= hi + 1e-6) & (ex > 0)
    return float(np.sqrt(np.mean((np.log(ex[m]) - (math.log(seed) + t[m] / tau)) ** 2)))


@extractor
def mergers_mouth(run: str, what: str, model: str = "div", interp: str = "loglog",
                  t: float | None = None) -> float:
    """plot_mouth_growth's per-mouth reading of a run's oriented scan: 'R0', 'R_split'
    (the last time the two scan spheres are disjoint), 'growth' (percent), 'fraction',
    't_split', 'sep0', 'sep_split', 'tau' (e-fold of R/R0 - 1 fitted over t = 8-25),
    'seed', 'asym' (max |R_A - R_B|), 'min_sep', 't_end' (the scan's last time),
    'rms' (of ln(R/R0 - 1) about the tau fit).

    The same reading with the companion's field taken off the ruler (2026-09-26,
    referee): each row against the placement curve of Sec. V C at the separation
    the arm has reached (results/merger/analysis/mouth_placement.py: the scan-centre
    separation, shifted by the tracker's t = 0 snap; a power law between the probes,
    interp = 'loglog', or placement_curve.py's 'linear'; held at d = 6 below them).
    model 'div' = R/R_p(d) - 1, 'sub' = (R - R_p(d))/R_iso.  'tau_placed',
    'seed_placed', 'rms_placed': _tau's fit of that excess over the same rows (raises
    if none is positive); 'placed' (percent, at t, default the last disjoint row),
    'placed_max' / 'placed_min' (percent, over the fit rows); 'field' (R_p/R_p(0) - 1,
    percent, at t or the last disjoint row) and 'field_share' (percent of R/R0 - 1
    there); 'range_end' (last scan time inside the probed separations) and
    'range_exit' (where d crosses the closest probe, interpolated between rows)."""
    from grteclyn_wrapper.visualisation.wormhole_merger import plot_mouth_growth as pmg

    s = pmg._scan(run_dir(run) / "horizon_scan.dat")
    i = pmg._split(s)
    tau, seed, ex = pmg._tau(s)
    ra = s["RA"]
    base = {"R0": ra[0], "R_split": ra[i - 1], "growth": 100.0 * (ra[i - 1] / ra[0] - 1.0),
            "fraction": ra[i - 1] / ra[0] - 1.0, "t_split": s["t"][i - 1],
            "sep0": s["sep"][0], "sep_split": s["sep"][i - 1], "tau": tau,
            "seed": seed, "asym": np.abs(ra - s["RB"]).max(),
            "min_sep": s["sep"].min(), "t_end": s["t"].max()}
    lo, hi = pmg.FIT
    if what in base:
        return float(base[what])
    if what == "rms":
        return _mouth_rms(s["t"], ex, tau, seed, lo, hi)

    _, c = _mouth_placed(run, model, interp)
    tt = s["t"]
    rows = (tt >= lo - 1e-6) & (tt <= hi + 1e-6)                     # the rows _tau selects from
    if t is None:
        k = i - 1
    else:
        k = int(np.argmin(np.abs(tt - t)))
        if abs(tt[k] - t) > 1e-3:
            raise ValueError(f"{run}: no scan row at t = {t}")
    if what in ("tau_placed", "seed_placed", "rms_placed"):
        if not (rows & (c["ex"] > 0)).any():
            raise ValueError(f"{run}: the {model} placement-corrected excess is <= 0 on every "
                             f"fit row (the mouths read below the placement curve): no e-fold")
        tau_p, seed_p, ex_p = pmg._tau({"t": tt, "RA": ra[0] * (1.0 + c["ex"])})
        return float({"tau_placed": tau_p, "seed_placed": seed_p,
                      "rms_placed": _mouth_rms(tt, ex_p, tau_p, seed_p, lo, hi)}[what])
    if what == "placed":
        return float(100.0 * c["ex"][k])
    if what in ("placed_max", "placed_min"):
        return float(100.0 * (c["ex"][rows].max() if what == "placed_max" else c["ex"][rows].min()))
    if what == "field":
        return float(100.0 * c["companion"][k])
    if what == "field_share":
        return float(100.0 * c["companion"][k] / c["raw"][k])
    if what in ("range_end", "range_exit"):
        out = ~c["in_range"]
        if not out.any():
            return float(tt[-1])
        j = int(np.argmax(out))
        if what == "range_end":
            return float(tt[j - 1])
        import mouth_placement as mp

        d_near = float(mp.load_curve(PACK)[0][0])          # the closest probe, d = 6
        d1, d2 = c["d"][j - 1], c["d"][j]
        return float(tt[j - 1] + (tt[j] - tt[j - 1]) * (d1 - d_near) / (d1 - d2))
    raise ValueError(f"mergers_mouth: unknown what {what!r}")


# ---------------------------------------------------------------- the spiral core (plot_spiral_collapse)
@extractor
def mergers_profile(run: str, what: str) -> float:
    """plot_spiral_collapse's reading of core_radial_profile.dat.gz: 'chi_floor' (first
    time min chi over the shells reaches the 1e-8 floor), 'spike_start' (first time after
    t = 45 the |K| peak stands 2x above the r = 0.4 background), 'first' / 'last' time."""
    from grteclyn_wrapper.visualisation.wormhole_merger import plot_spiral_collapse as psc

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        pt, rr, blk = psc._read_profile(run_dir(run) / "core_radial_profile.dat.gz")
        if what == "first":
            return float(pt[0])
        if what == "last":
            return float(pt[-1])
        if what == "chi_floor":
            i = int(np.argmax(np.nanmin(blk["chi"], axis=1) <= psc.CHI_FLOOR * 1.01))
            return float(pt[i])
        if what == "spike_start":
            K = blk["K"]
            pk = np.nanargmax(np.where(np.isnan(K), -np.inf, K), axis=1)
            vpk = K[np.arange(len(pt)), pk]
            bg = K[:, int(0.4 / float(rr[1] - rr[0]))]
            return float(pt[int(np.argmax((vpk > 2.0 * bg) & (pt > 45.0)))])
    raise ValueError(what)


@extractor
def mergers_norm_median(fine: str, coarse: str, which: str = "L2_Ham",
                        settle: float = 0.1) -> float:
    """plot_spiral_collapse panel (e): median 100 |coarse - fine| / fine of a constraint
    norm over the window both arms cover (the fine arm's settled collapse clock)."""
    t, _ = _col(fine, "collapse_diagnostics.dat", "min_lapse", settle)
    tf, yf = _col(fine, "constraint_norms.dat", which)
    tc, yc = _window(*_col(coarse, "constraint_norms.dat", which), t[0], t[-1])
    ref = np.interp(tc, t, np.interp(t, tf, yf))
    return float(100.0 * np.median(np.abs(yc - ref) / ref))


# ---------------------------------------------------------------- waveforms
_RADII_L64 = [10.0, 14.0, 18.0]
_RADII_L128 = [20.0, 28.0, 36.0, 44.0]


@functools.lru_cache(maxsize=64)
def _mode(run: str, file: str, radii: tuple) -> tuple[np.ndarray, dict]:
    from grteclyn_wrapper.visualisation.wormhole_merger import streams

    t, s = streams.load_mode(run_dir(run) / file, list(radii))
    order = np.argsort(t, kind="stable")
    t = t[order]
    tr = np.round(t, 4)
    keep = np.append(tr[1:] != tr[:-1], True)
    return t[keep], {r: z[order][keep] for r, z in s.items()}


def _part(z: np.ndarray, part: str) -> np.ndarray:
    return z.real if part == "re" else z


@extractor
def mergers_psi4_diff(a: str, b: str, radii: list, lo: float, hi: float,
                      file: str = "Weyl4_mode_20.dat", norm: str | None = None,
                      norm_lo: float | None = None, norm_hi: float | None = None,
                      part: str = "re", agg: str = "max", stream_radii: list | None = None) -> float:
    """100 max|a - b| / peak on the times both arms share in [lo, hi], per sphere, then
    aggregated over `radii` (min / max).  part = 're' compares Re r psi4 and takes the
    peak of |Re| (the head-on seam and fill checks), 'abs' the complex mode (M6).  The
    peak is the `norm` arm's (default a) over [norm_lo, norm_hi] (default: its record)."""
    rr = tuple(stream_radii or (_RADII_L128 if max(radii) > 18 else _RADII_L64))
    ta, sa = _mode(a, file, rr)
    tb, sb = _mode(b, file, rr)
    tn, sn = _mode(norm or a, file, rr)
    common, ia, ib = np.intersect1d(np.round(ta, 4), np.round(tb, 4), return_indices=True)
    w = (common >= lo - 1e-9) & (common <= hi + 1e-9)
    wn = np.ones(len(tn), bool)
    if norm_lo is not None:
        wn &= tn >= norm_lo - 1e-9
    if norm_hi is not None:
        wn &= tn <= norm_hi + 1e-9
    out = []
    for r in radii:
        d = np.abs(_part(sa[r][ia][w], part) - _part(sb[r][ib][w], part)).max()
        pk = np.abs(_part(sn[r][wn], part)).max()
        out.append(100.0 * d / pk)
    return _agg(out, agg)


@extractor
def mergers_pipeline_peak(run: str, radii: list, lo: float, hi: float) -> float:
    """Worst 100 |peak_offline / peak_in-code - 1| over the spheres: the largest
    |r Psi4^20| in [lo, hi] of the consumer's psi4_mode_l2m0.dat (offline, from
    plotfiles) against the in-code Weyl4_mode_20.dat of the same run.  Meaningful
    only where the burst stands above the in-code floor (the head-on; on the single
    throats the in-code stream is floor-dominated inside the burst window)."""
    rr = tuple(_RADII_L64)
    ta, sa = _mode(run, "Weyl4_mode_20.dat", rr)
    tb, sb = _mode(run, "psi4_mode_l2m0.dat", rr)
    wa = (ta >= lo - 1e-9) & (ta <= hi + 1e-9)
    wb = (tb >= lo - 1e-9) & (tb <= hi + 1e-9)
    return float(max(100.0 * abs(np.abs(sb[r][wb]).max() / np.abs(sa[r][wa]).max() - 1.0)
                     for r in radii))


@extractor
def mergers_psi4_m6(a: str, b: str, radius: float, modes: list, fraction: bool = False) -> float:
    """The M6 test (SERIES README): worst over the modes of max|a - b| (complex r psi4)
    on the shared window, over the unfrozen arm a's own peak |r psi4| -- in percent, or
    as a plain fraction with fraction = True."""
    worst = 0.0
    for mode in modes:
        f = f"Weyl4_mode_{mode}.dat"
        ta, sa = _mode(a, f, tuple(_RADII_L128))
        tb, sb = _mode(b, f, tuple(_RADII_L128))
        common, ia, ib = np.intersect1d(np.round(ta, 4), np.round(tb, 4), return_indices=True)
        d = np.abs(sa[radius][ia] - sb[radius][ib]).max()
        worst = max(worst, d / np.abs(sa[radius]).max())
    return float(worst if fraction else 100.0 * worst)


@extractor
def mergers_energy_diff(a: str, b: str, radii: list, file: str = "Weyl4_mode_20.dat",
                        m: int = 0, agg: str = "max") -> float:
    """100 |E_a - E_b| / E_a of psi4_math._compute_radiated_energy (the paper's energy
    function) on each arm's whole record, per sphere, aggregated over the spheres."""
    from grteclyn_wrapper.visualisation.wormhole_merger.psi4_math import _compute_radiated_energy

    rr = tuple(_RADII_L128 if max(radii) > 18 else _RADII_L64)
    ta, sa = _mode(a, file, rr)
    tb, sb = _mode(b, file, rr)
    out = []
    for r in radii:
        ea = _compute_radiated_energy(ta, sa[r], m=m)
        eb = _compute_radiated_energy(tb, sb[r], m=m)
        out.append(100.0 * abs(ea - eb) / ea)
    return _agg(out, agg)


@extractor
def mergers_psi4_level(run: str, radius: float, file: str = "psi4_mode_l2m0.dat",
                       t0: float | None = None, t1: float | None = None) -> float:
    """Largest |r psi4| of a consumer mode stream at one sphere over [t0, t1]."""
    t, s = _mode(run, file, (14.0, 30.0))
    z = s[radius]
    keep = np.ones(len(t), bool)
    if t0 is not None:
        keep &= t > t0 + 1e-9
    if t1 is not None:
        keep &= t <= t1 + 1e-9
    return float(np.abs(z[keep]).max())


@extractor
def mergers_stream_radius(run: str, file: str, index: int) -> float:
    """The index-th extraction sphere a mode stream's own header names."""
    from grteclyn_wrapper.visualisation.wormhole_merger import streams

    _, s = streams.load_mode(run_dir(run) / file)
    return float(sorted(s)[index])


@extractor
def mergers_psi4_decades(run: str, radius: float, early_t1: float, late_t0: float,
                         file: str = "psi4_mode_l2m0.dat") -> float:
    """Decades the sphere-local floor climbs: log10 of the peak |r psi4| after late_t0
    over the peak up to early_t1."""
    late = mergers_psi4_level(run=run, radius=radius, file=file, t0=late_t0)
    early = mergers_psi4_level(run=run, radius=radius, file=file, t1=early_t1)
    return float(math.log10(late / early))


# ---------------------------------------------------------------- controls
@extractor
def mergers_twin_digits(a: str, b: str, t: float) -> float:
    """Digits to which two twins agree at time t: floor(-log10) of the worst relative
    difference over min lapse, min chi, max |K| and both constraint norms."""
    worst = 0.0
    for file, cols in (("collapse_diagnostics.dat", ("min_lapse", "min_chi", "max_abs_K")),
                       ("constraint_norms.dat", ("L2_Ham", "L2_Mom"))):
        for c in cols:
            x = mergers_value(run=a, file=file, col=c, t=t)
            y = mergers_value(run=b, file=file, col=c, t=t)
            worst = max(worst, abs(x - y) / abs(x))
    return float(math.floor(-math.log10(worst)))


@extractor
def mergers_departure_time(ref: str, twin: str, file: str = "constraint_norms.dat",
                           col: str = "L2_Ham", factor: float = 2.0) -> float:
    """First shared output time at which the twin's col is `factor` times the
    reference's, either way (a Delta-t twin leaving the production solution)."""
    ta, ya = _col(ref, file, col)
    tb, yb = _col(twin, file, col)
    common, ia, ib = np.intersect1d(np.round(ta, 4), np.round(tb, 4), return_indices=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = yb[ib] / ya[ia]
    hit = np.isfinite(r) & ((r >= factor) | (r <= 1.0 / factor))
    if not hit.any():
        raise ValueError(f"{twin} never departs from {ref} by x{factor}")
    return float(common[int(np.argmax(hit))])
