"""Extractors for the ledger's 'detector' area (ledger_detector.tsv).

What they cover in research.tex: Table I (tab:matrix) -- its run counts and the
totals 144 / 12 / 132, recounted from claims/table1_groups.tsv against the pack
(an unclassified packed run is an ERROR), and its knob column read back from
the group's evolution_params.txt; Sec. "Pattern matching against detector
data" (strain pedestal, IMRPhenomD validation, fitting factors, the O3b
matched-filter search, ringdown discriminators, burst energies); the
Discussion's own arithmetic (the no-inspiral e-fold budget, the heavy-seed
channel and its LISA background, the Limitations' scalar-spread numbers); and
Sec. "Reproducibility and cost" (GPU-hours -- restart-aware, see _leg_start --
memory, AMReX version).

Sources, all tracked:
  * results/merger/campaign/...          the pack (streams, run_tail*.log)
  * results/merger/gw_search/*.json      the frozen outputs of the O3b search
    (o3b_scan.json, injections.json, fitting_factors.json): the search itself
    needs GWOSC strain (runs/gw_search/strain_cache, untracked, network), so
    those numbers are READ from the committed JSON, not re-run
  * claims/table1_groups.tsv             Table I's run -> group map (committed)
  * grteclyn_wrapper's figure and search code, imported LAZILY (so a Python
    without the package can still load this module and check other areas):
    plot_psi4_ligo (energies, frequency tracks), gw_search.templates (strain
    pedestal, template durations), gw_search.analysis.validation (re-runs the
    IMRPhenomD validation, ~15 s, needs pycbc), plot_mouth_growth (tau, seed),
    plot_heavy_seeds (the seed race's inputs, cosmology, LISA curve),
    plot_headon_collapse / plot_scalar_* (their loaders only).
Never a figure script's main(): those write figures.

Conventions.  Every extractor takes keyword arguments and returns one float.
Order-of-magnitude claims ("~10^{-11}") are compared in log10: the extractor
returns log10 of the quantity and the ledger row carries the exponent in num
with tol abs:0.5 (half a decade), stated in the row's note.
"""

from __future__ import annotations

import collections
import functools
import json
import math
import pathlib
import re
import statistics

import numpy as np

from lib import EXTRACTORS, PACK, extractor, run_dir
from pack_paths import iter_runs

HERE = pathlib.Path(__file__).resolve().parent
TABLE1 = HERE / "table1_groups.tsv"
GW = PACK / "gw_search"

# Table I's groups, in the table's order (left column, then right).
TABLE1_GROUPS = (
    "lone throat", "spherical kicks", "quadrupolar kicks", "scalar-stream re-runs",
    "two throats at rest", "placement probes", "head-on, d=8", "half-mass, m=0.5",
    "vacuum BBH", "constraint-solved data",
    "momentum scan", "fly-by, p=0.45", "orbital chain, p=0.12", "refinement ladder",
    "interior freeze, L=64", "wall probes", "production spiral, L=128", "Helfer twins",
    "gauge arms", "shakedown (archived)",
)
SHAKEDOWN = "shakedown (archived)"
EXCLUDED = "-"

# The five radiating channels, as named in the search and figure code (ARMS).
CHANNELS = ("collapsing throat", "head-on", "spiral", "fly-by")
CONTROL = "vacuum BBH twin"
ARM_ALIAS = {"throat": "collapsing throat", "collapsing throat": "collapsing throat",
             "head-on": "head-on", "headon": "head-on", "spiral": "spiral",
             "fly-by": "fly-by", "flyby": "fly-by", "twin": CONTROL, "control": CONTROL,
             "vacuum BBH twin": CONTROL}


def _arms(arms) -> list[str]:
    if arms in (None, "channels"):
        return list(CHANNELS)
    if arms == "control":
        return [CONTROL]
    if arms == "all":
        return list(CHANNELS) + [CONTROL]
    if isinstance(arms, str):
        arms = [arms]
    return [ARM_ALIAS[a] for a in arms]


def _stat(values, stat: str) -> float:
    v = [float(x) for x in values]
    if not v:
        raise ValueError("no values")
    return {"min": min, "max": max, "median": statistics.median,
            "abs_max": lambda z: max(abs(x) for x in z),
            "count": len}[stat](v)


# =============================================================== Table I
@functools.lru_cache(maxsize=1)
def _table1() -> dict[str, str]:
    """run name -> Table I group ('-' = not counted), from table1_groups.tsv."""
    out: dict[str, str] = {}
    for n, line in enumerate(TABLE1.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip() or line.startswith("#") or line.startswith("run\t"):
            continue
        cells = line.split("\t")
        run, group = cells[0].strip(), cells[1].strip()
        if group not in TABLE1_GROUPS and group != EXCLUDED:
            raise ValueError(f"table1_groups.tsv:{n}: unknown group {group!r}")
        if run in out and out[run] != group:
            raise ValueError(f"table1_groups.tsv:{n}: {run} mapped to both {out[run]!r} and {group!r}")
        out[run] = group
    return out


@functools.lru_cache(maxsize=1)
def _packed() -> dict[str, list[pathlib.Path]]:
    """run name -> packed directories (a name can be packed twice)."""
    out: dict[str, list[pathlib.Path]] = collections.defaultdict(list)
    for _, d in iter_runs(PACK):
        out[d.name].append(d)
    return dict(out)


def _group_runs(group: str) -> list[str]:
    if group not in TABLE1_GROUPS:
        raise KeyError(f"no Table I group {group!r}; groups are {TABLE1_GROUPS}")
    names = sorted(n for n, g in _table1().items() if g == group)
    packed = _packed()
    gone = [n for n in names if n not in packed]
    twice = [n for n in names if len(packed.get(n, ())) > 1]
    if gone:
        raise LookupError(f"{group}: counted in table1_groups.tsv but not packed: {gone}")
    if twice:
        raise LookupError(f"{group}: name matches more than one packed directory: {twice}")
    return names


def _audit_table1() -> None:
    """Every packed run directory must be classified in table1_groups.tsv."""
    unassigned = sorted(n for n in _packed() if n not in _table1())
    if unassigned:
        raise LookupError(f"{len(unassigned)} packed run(s) have no Table I group -- add them to "
                          f"claims/table1_groups.tsv: {unassigned}")


def _counted(which: str) -> list[str]:
    _audit_table1()
    groups = {"all": [g for g in TABLE1_GROUPS],
              "physics": [g for g in TABLE1_GROUPS if g != SHAKEDOWN],
              "shakedown": [SHAKEDOWN]}[which]
    return [n for g in groups for n in _group_runs(g)]


@extractor
def detector_table1_runs(group: str) -> float:
    """Runs in one Table I group: the committed map, checked against the pack."""
    return float(len(_group_runs(group)))


@extractor
def detector_table1_total(which: str = "all") -> float:
    """Table I total: 'all' (the 144), 'physics' (the 132), 'shakedown' (the 12).
    Fails if any packed run is missing from table1_groups.tsv."""
    return float(len(_counted(which)))


def _knob(p: dict[str, str], key: str) -> float | None:
    """One knob of a run's evolution_params.txt; derived keys: separation
    (|centre A - centre B|), momentum (|p_A|), eps (radial seed), eps2 (l=2 seed)."""
    def vec(k):
        return [float(x) for x in p[k].strip('"').split()] if k in p else None
    if key == "separation":
        a, b = vec("wormhole_centerA"), vec("wormhole_centerB")
        return math.dist(a, b) if a and b else None
    if key == "momentum":
        v = vec("wormhole_momentumA")
        return math.hypot(*v) if v else None
    key = {"eps": "wormhole_seed_amplitude_A", "eps2": "wormhole_seed_l2_amplitude_A",
           "a": "wormhole_throat_radius_A", "m": "wormhole_drainhole_mass_A"}.get(key, key)
    return float(p[key].strip('"').split()[0]) if key in p else None


@extractor
def detector_table1_param(group: str, key: str, stat: str, log10: bool = False) -> float:
    """A knob of Table I read back from the group's runs' evolution_params.txt:
    stat min / max / min_abs / max_abs / min_nonzero over the runs that carry it
    (runs without a params file or without the key are skipped); 'only' requires
    every run to agree.  log10: return log10 of the result (knobs printed 10^k)."""
    from lib import params
    vals = []
    for n in _group_runs(group):
        try:
            v = _knob(params(n), key)
        except FileNotFoundError:
            continue
        if v is not None:
            vals.append(v)
    if not vals:
        raise ValueError(f"{group}: no run carries {key}")
    if stat == "only":
        if max(vals) - min(vals) > 1e-12:
            raise ValueError(f"{group}: {key} is not one value: {sorted(set(vals))}")
        out = vals[0]
    else:
        out = {"min": min(vals), "max": max(vals),
               "min_abs": min(abs(v) for v in vals), "max_abs": max(abs(v) for v in vals),
               "min_nonzero": min(v for v in vals if v != 0)}[stat]
    return math.log10(out) if log10 else float(out)


# =============================================================== cost (run_tail logs)
def _gh():
    import gpu_hours  # results/merger/analysis/gpu_hours.py, on sys.path via lib
    return gpu_hours


COARSE_DT = 0.01   # 0.02 x dx0 = 0.02 x 0.5: every restart parent in the campaign (L/N1 = 0.5)


def _restart_time(d: pathlib.Path) -> float | None:
    """Code time of the checkpoint a run restarted from (ChkNNNNN -> NNNNN x
    COARSE_DT), from run_manifest.json 'restart_from', else the params'
    amr.restart, else the launch banner.  None for a run from t = 0."""
    texts = []
    man = d / "run_manifest.json"
    if man.exists():
        texts.append(str(json.loads(man.read_text(encoding="utf-8")).get("restart_from") or ""))
    for f in ("evolution_params.txt", "launch_banner.txt"):
        if (d / f).exists():
            texts += [ln.split("#", 1)[0] for ln in (d / f).read_text(errors="replace").splitlines()
                      if "restart" in ln and "Chk" in ln]
    for t in texts:
        m = re.search(r"Chk(\d+)", t)
        if m:
            return int(m.group(1)) * COARSE_DT
    return None


def _leg_start(d: pathlib.Path, suffix: str, restart_aware: bool) -> float:
    """gpu_hours.leg_start (first row of the leg's stream), except that a leg with
    NO stream falls back to its restart time instead of t = 0 when restart_aware.
    GRTeclyn logs speed = (t - t_restart) / wall time (Source/GRTeclynCore/
    GRAMRLevel.cpp, advance()), so a restarted leg's wall time is
    (t_end - t_restart) / speed; the t = 0 fallback charges it for the parent's
    whole history as well."""
    gh = _gh()
    for stem in gh.START_STREAMS:
        hits = sorted(d.glob(f"{stem}{suffix}*.dat")) if suffix else (
            [d / f"{stem}.dat"] if (d / f"{stem}.dat").exists() else [])
        for p in hits:
            t0, _ = gh.first_and_last_time(p)
            if t0 is not None:
                return t0
    if restart_aware and not suffix:
        rt = _restart_time(d)
        if rt is not None:
            return rt
    return 0.0


def _run_hours(d: pathlib.Path, restart_aware: bool = True) -> float:
    """gpu_hours.py's arithmetic for one run: per leg (t_end - t_start)/speed,
    plus __part legs at the main leg's speed.  Legs with speed 0 (a launch that
    died at t = 0) are skipped; the tracked script divides by them and crashes.
    restart_aware=False reproduces the tracked script's t = 0 fallback exactly."""
    gh = _gh()
    tot, main_speed = 0.0, None
    for tail in sorted(d.glob("run_tail*.log")):
        suffix = tail.name[len("run_tail"):-len(".log")]
        speed, t_end = gh.parse_tail(tail)
        if not speed or t_end is None:
            continue
        if not suffix:
            main_speed = speed
        tot += max(t_end - _leg_start(d, suffix, restart_aware), 0.0) / speed
    for part in sorted(d.glob("constraint_norms__part*.dat")):
        t0, t1 = gh.first_and_last_time(part)
        if t0 is not None and main_speed:
            tot += (t1 - t0) / main_speed
    return tot


@extractor
def detector_gpu_hours(which: str | None = None, runs: list[str] | None = None,
                       restart_aware: bool = True) -> float:
    """GPU-hours from the packed logs: a Table I set ('physics', 'shakedown',
    'all') or an explicit list of packed run names.  restart_aware (default)
    dates a restarted leg that has no packed stream from its checkpoint; False
    is the tracked gpu_hours.py arithmetic (t = 0 fallback), the one the
    article's 810 was computed with."""
    if (which is None) == (runs is None):
        raise ValueError("give exactly one of which= or runs=")
    names = _counted(which) if which else runs
    return float(sum(_run_hours(run_dir(n), restart_aware) for n in names))


def _tail_ints(run: str, pattern: str) -> list[int]:
    out = []
    for tail in sorted(run_dir(run).glob("run_tail*.log")):
        for m in re.finditer(pattern, tail.read_text(errors="replace")):
            out.append(int(m.group(1)))
    return out


@extractor
def detector_arena_peak_gib(run: str) -> float:
    """Peak device memory the AMReX arena held (its 'max space allocated', MB =
    2^20 bytes as AMReX prints it), in GiB, from the run's own log."""
    vals = _tail_ints(run, r"\[The\s+Arena\] max space \(MB\) allocated spread across MPI: \[(\d+)")
    if not vals:
        raise ValueError(f"{run}: no arena line in run_tail*.log")
    return max(vals) / 1024.0


@extractor
def detector_amrex_version(which: str = "all") -> float:
    """The AMReX release every counted run reports at finalize ('AMReX (26.02-...)
    finalized'), as a float; fails if two releases appear."""
    seen: dict[str, list[str]] = collections.defaultdict(list)
    for n in _counted(which):
        for tail in sorted(run_dir(n).glob("run_tail*.log")):
            for m in re.finditer(r"AMReX \((\d+\.\d+)[^)]*\) finalized", tail.read_text(errors="replace")):
                seen[m.group(1)].append(n)
    if len(seen) != 1:
        raise ValueError(f"AMReX releases in the counted runs' logs: "
                         f"{ {k: len(v) for k, v in seen.items()} }")
    return float(next(iter(seen)))


# =============================================================== the O3b search (frozen JSON)
@functools.lru_cache(maxsize=None)
def _json(name: str):
    return json.loads((GW / name).read_text(encoding="utf-8"))


@extractor
def detector_scan(key: str, scale: float = 1.0) -> float:
    """A number from gw_search/o3b_scan.json by dotted key (x scale)."""
    node = _json("o3b_scan.json")
    for part in key.split("."):
        node = node[part]
    return float(node) * scale


@extractor
def detector_scan_sky_factor() -> float:
    """Optimal / sky-averaged horizon, identical for every channel in the scan."""
    s = _json("o3b_scan.json")
    opt, sky = s["horizon_mpc_optimal_snr8_single_ifo"], s["horizon_mpc_sky_averaged_snr8_single_ifo"]
    r = {k: opt[k] / sky[k] for k in opt}
    if max(r.values()) - min(r.values()) > 1e-9:
        raise ValueError(f"sky factor differs between channels: {r}")
    return float(next(iter(r.values())))


@extractor
def detector_scan_snr_threshold() -> float:
    """The single-detector SNR the horizons are quoted at (the scan's horizon_note)."""
    m = re.search(r"single-detector SNR (\d+(?:\.\d+)?)", _json("o3b_scan.json")["horizon_note"])
    if not m:
        raise ValueError("horizon_note does not state the SNR")
    return float(m.group(1))


def _injections(arm=None, pick: str | None = None) -> list[dict]:
    rows = _json("injections.json")
    if arm:
        rows = [r for r in rows if r["arm"] == ARM_ALIAS.get(arm, arm)]
    if pick == "min_mass":
        rows = [min(rows, key=lambda r: r["mass_msun"])]
    elif pick == "max_chisq":
        rows = [max(rows, key=lambda r: r["chisq_r"])]
    if not rows:
        raise ValueError("no injection selected")
    return rows


@extractor
def detector_injections(stat: str, field: str | None = None, arm: str | None = None,
                        pick: str | None = None, scale: float = 1.0) -> float:
    """gw_search/injections.json: stat (count/min/max/median/abs_max) of a field,
    optionally for one arm or one picked row (min_mass, max_chisq)."""
    rows = _injections(arm, pick)
    if stat == "count":
        return float(len(rows))
    if stat == "found":
        return float(sum(bool(r["found"]) for r in rows))
    return _stat([r[field] for r in rows], stat) * scale


@extractor
def detector_ff(field: str, stat: str, arms="channels") -> float:
    """gw_search/fitting_factors.json over arms (channels / control / names).
    field: ff_bank, ff_window, or mass_recovered (best_total_mass / mass_msun)."""
    want = set(_arms(arms))
    rows = [r for r in _json("fitting_factors.json") if r["arm"] in want]
    if {r["arm"] for r in rows} != want:
        raise ValueError(f"fitting_factors.json lacks {want - {r['arm'] for r in rows}}")
    if field == "mass_recovered":
        vals = [r["best_total_mass"] / r["mass_msun"] for r in rows]
    else:
        vals = [r[field] for r in rows]
    return _stat(vals, stat)


# =============================================================== search code: bank and templates
@extractor
def detector_bank_param(name: str) -> float:
    """A setting of the search code: the fitting-factor BBH bank and cutoff
    (analysis/fitting_factor.py) or the NR bank spacing (templates/bank.py)."""
    import importlib
    # by module path: the analysis package re-exports a FUNCTION called fitting_factor
    ff = importlib.import_module("grteclyn_wrapper.gw_search.analysis.fitting_factor")
    bank = importlib.import_module("grteclyn_wrapper.gw_search.templates.bank")
    b = ff.BBH_BANK
    table = {
        "total_mass_min": min(b["total_mass"]), "total_mass_max": max(b["total_mass"]),
        "mass_ratio_min": min(b["mass_ratio"]), "mass_ratio_max": max(b["mass_ratio"]),
        "chi_eff_min": min(b["chi_eff"]), "chi_eff_max": max(b["chi_eff"]),
        "f_lower": ff.F_LOWER, "min_match": bank.MIN_MATCH,
        "band_lo_hz": bank.F_BAND_LO, "band_hi_hz": bank.F_BAND_HI,
    }
    return float(table[name])


@functools.lru_cache(maxsize=1)
def _templates() -> dict:
    import warnings
    warnings.filterwarnings("ignore")
    from grteclyn_wrapper.gw_search.templates.nr import load_all_arms
    return {wf.name: wf for wf in load_all_arms(pack=PACK)}


@extractor
def detector_template_drift(stat: str, arms="channels") -> float:
    """Strain pedestal |h|(ends)/|h|(peak) of the search templates (templates/nr.py)."""
    wfs = _templates()
    return _stat([wfs[a].drift for a in _arms(arms)], stat)


@extractor
def detector_bank_duration_ms(stat: str) -> float:
    """Shortest ('min', each arm at its lightest rung) or longest ('max', at its
    heaviest) template in the bank, ms.  The ladder's end rungs are
    templates/bank.py's mass_range, which needs no noise curve; only the rungs in
    between (and so the count, 127) depend on the live PSD."""
    from grteclyn_wrapper.gw_search.templates.bank import mass_range
    wfs = _templates().values()
    if stat == "min":
        return 1e3 * min(wf.duration_s(mass_range(wf)[0]) for wf in wfs)
    if stat == "max":
        return 1e3 * max(wf.duration_s(mass_range(wf)[1]) for wf in wfs)
    raise ValueError(stat)


def _injected_mass(arm: str, pick: str) -> float:
    return float(_injections(arm, pick)[0]["mass_msun"])


@extractor
def detector_template_duration_ms(arm: str, mass: float | None = None, pick: str | None = None) -> float:
    """One template's record length in ms at a mass (or at an injection's mass)."""
    a = ARM_ALIAS[arm]
    m = mass if mass is not None else _injected_mass(a, pick)
    return 1e3 * _templates()[a].duration_s(m)


@extractor
def detector_chisq_bins(arm: str, mass: float | None = None, pick: str | None = None) -> float:
    """Allen chi^2 bin count the search gives one template (pipeline/triggers.py)."""
    from grteclyn_wrapper.gw_search.pipeline.triggers import chisq_bins
    from grteclyn_wrapper.gw_search.templates.bank import BankTemplate
    from grteclyn_wrapper.gw_search.cli import SAMPLE_RATE
    a = ARM_ALIAS[arm]
    wf = _templates()[a]
    m = mass if mass is not None else _injected_mass(a, pick)
    bt = BankTemplate(arm=a, mode=wf.mode, mass_msun=m, waveform=wf)
    return float(chisq_bins(bt.series(SAMPLE_RATE), bt.f_lower_hz(), SAMPLE_RATE))


@functools.lru_cache(maxsize=1)
def _validation():
    """gws validate: the BBH twin through the search's template chain against
    IMRPhenomD at aLIGO design sensitivity (pycbc; ~15 s, no network)."""
    import contextlib
    import io
    import warnings
    warnings.filterwarnings("ignore")
    from grteclyn_wrapper.gw_search.analysis.validation import validate_bbh_twin
    from grteclyn_wrapper.gw_search.strain import DesignNoise
    with contextlib.redirect_stdout(io.StringIO()):
        rows, _ = validate_bbh_twin(DesignNoise(), 4096)
    return rows


@extractor
def detector_validation(what: str, mass: float | None = None, upto: float | None = None,
                        pct: float | None = None) -> float:
    """The IMRPhenomD validation of the BBH twin, re-run:
    ff_window_min/max, mass_min/max (the masses tested), mass_err_pct (at mass),
    mass_err_absmax_pct (largest |error| for masses <= upto),
    mass_max_within_pct (largest mass up to which every |error| <= pct %)."""
    rows = sorted(_validation(), key=lambda r: r.mass_nr)
    if what == "mass_max_within_pct":
        ok = None
        for r in rows:
            if abs(r.mass_error) * 100.0 > pct + 1e-9:
                break
            ok = r.mass_nr
        if ok is None:
            raise ValueError(f"no tested mass within {pct} %")
        return ok
    if what == "ff_window_min":
        return min(r.ff_window for r in rows)
    if what == "ff_window_max":
        return max(r.ff_window for r in rows)
    if what == "mass_min":
        return min(r.mass_nr for r in rows)
    if what == "mass_max":
        return max(r.mass_nr for r in rows)
    if what == "mass_err_pct":
        return 100.0 * next(r.mass_error for r in rows if abs(r.mass_nr - mass) < 1e-9)
    if what == "mass_err_absmax_pct":
        return 100.0 * max(abs(r.mass_error) for r in rows if r.mass_nr <= upto + 1e-9)
    raise ValueError(what)


# =============================================================== the detector figure's analysis
@functools.lru_cache(maxsize=1)
def _ligo() -> dict:
    """plot_psi4_ligo's numbers per arm: energy and sphere spread, the resolved
    Psi_4 band peak, and the gated instantaneous-frequency track (Hz at the
    figure's 30 Msun calibration) -- the figure's own code, not a copy."""
    from grteclyn_wrapper.visualisation.wormhole_merger import plot_psi4_ligo as L
    from grteclyn_wrapper.visualisation.wormhole_merger.psi4_math import (
        M_SUN_SEC, _burst_psd, _smooth_psd)
    to_hz = 1.0 / (L.MASS_MSUN * M_SUN_SEC)
    out = {}
    for a in L.prepare(PACK):
        f, S = _burst_psd(a["y"], 1.0 / a["dt"])
        f_pk = float(f[1:][np.argmax(_smooth_psd(S, L._smooth_window(S.size), 5)[1:])])
        env, fM = L.envelope_and_frequency(a["y"], a["dt"], f_pk)
        keep = L.body(env, L.GATE) & (fM * a["dt"] <= 1.0 / L.MIN_SPP)
        k = int(np.argmax(env))
        hz = fM[keep] * to_hz
        out[a["name"]] = dict(E=a["E"], spread=(a["E_hi"] - a["E_lo"]) / a["E"], f_pk=f_pk,
                              fM_peak=float(fM[k]), hz_peak=float(fM[k] * to_hz),
                              first=float(hz[0]), last=float(hz[-1]),
                              lo=float(hz.min()), hi=float(hz.max()))
    out["_qnm_hz"] = L.f_qnm_M() * to_hz
    out["_qnm_fM"] = L.f_qnm_M()
    return out


@extractor
def detector_gw_energy(arm: str, what: str = "E") -> float:
    """Dominant-multipole E_rad/M ('E') or its spread over spheres in % ('spread_pct')."""
    a = _ligo()[ARM_ALIAS[arm]]
    return a["E"] if what == "E" else 100.0 * a["spread"]


@extractor
def detector_freq(arm: str, what: str) -> float:
    """The frequency track of Fig. psi4_ligo(c): first/last/lo/hi (Hz over the
    gated body), hz_peak / fM_peak (at the envelope peak), f_pk (resolved Psi_4
    band peak, fM), lo_over_first, peak_over_qnm."""
    a = _ligo()[ARM_ALIAS[arm]]
    if what == "lo_over_first":
        return a["lo"] / a["first"]
    if what == "peak_over_qnm":
        return a["hz_peak"] / _ligo()["_qnm_hz"]
    return float(a[what])


@extractor
def detector_qnm_fM() -> float:
    """f M of the equal-mass remnant's (2,2,0) mode (Berti-Cardoso-Will fit at
    a_f = 0.6864, M_f = 0.9516 M, plot_psi4_ligo.f_qnm_M)."""
    return float(_ligo()["_qnm_fM"])


@extractor
def detector_fpk_range(stat: str, arms="channels") -> float:
    """min/max resolved Psi_4 band peak (fM) over the drainhole channels."""
    return _stat([_ligo()[a]["f_pk"] for a in _arms(arms)], stat)


@extractor
def detector_headon_mms_ratio() -> float:
    """Head-on remnant: M_MS at common-MOTS formation (offline scan, t = 22) over
    M_MS at the end of the level-3 down-step arm's live track (t = 99) -- the
    factor by which a Kerr frequency ~ 1/M would rise as the remnant shrinks."""
    from grteclyn_wrapper.visualisation.wormhole_merger import plot_headon_collapse as H
    g = PACK / "campaign" / H.GROUP
    form = H._offline_formation(g / H.SCOUT / "horizon_offline_scan.dat")
    c = H._live_scan(g / H.DOWN / "horizon_scan.dat")
    m = c["n_mots"] > 0
    return float(form[0, 3] / c["M_MS"][m][-1])


# =============================================================== mouth growth and the no-inspiral budget
@functools.lru_cache(maxsize=None)
def _mouth(arm: str) -> tuple[float, float]:
    from grteclyn_wrapper.visualisation.wormhole_merger import plot_mouth_growth as MG
    rel = {"merger": MG.MERGER[0], "flyby": MG.FLYBY[0]}[arm]
    tau, seed, _ = MG._tau(MG._scan(PACK / "campaign" / rel / "horizon_scan.dat"))
    return float(tau), float(seed)


@extractor
def detector_mouth_tau(arm: str) -> float:
    """E-fold time of the mouths' growth excess, fitted t = 8-25 (plot_mouth_growth)."""
    return _mouth(arm)[0]


@extractor
def detector_mouth_seed(arm: str) -> float:
    """The same fit back-extrapolated to t = 0: the effective seed of the mode."""
    return _mouth(arm)[1]


def _tau(tau) -> float:
    return _mouth("flyby")[0] if tau in (None, "flyby") else (
        _mouth("merger")[0] if tau == "merger" else float(tau))


def _t_insp(d_over_M: float, M: float, eta: float) -> float:
    return 5.0 / 256.0 * d_over_M ** 4 * M / eta


def _t_orb(d_over_M: float, M: float) -> float:
    d = d_over_M * M
    return 2.0 * math.pi * math.sqrt(d ** 3 / M)


@extractor
def detector_insp_time(d_over_M: float, M: float = 2.0, eta: float = 0.25) -> float:
    """Peters quasi-circular inspiral time (5/256)(d/M)^4 M/eta, code units (M = total mass)."""
    return _t_insp(d_over_M, M, eta)


@extractor
def detector_insp_orbits(d_over_M: float, M: float = 2.0, eta: float = 0.25) -> float:
    """That time in orbits of the initial period 2 pi sqrt(d^3/M)."""
    return _t_insp(d_over_M, M, eta) / _t_orb(d_over_M, M)


@extractor
def detector_insp_efolds(d_over_M: float, tau=None, factor: float = 1.0, log10_seed: bool = False,
                         M: float = 2.0, eta: float = 0.25) -> float:
    """t_insp / (factor * tau): e-folds the throat mode gets during the inspiral
    (factor > 1 = a reaction that many times stronger).  tau: 'flyby' (default,
    the fitted mouth clock), 'merger', or a number.  log10_seed: return instead
    log10 of the largest seed that survives, e^{-N}."""
    n = _t_insp(d_over_M, M, eta) / (factor * _tau(tau))
    return -n / math.log(10.0) if log10_seed else n


@extractor
def detector_lifetime_orbits(log10_eps: float, tau=None, d_over_M: float = 6.0, M: float = 2.0) -> float:
    """tau ln(1/eps) in orbits of the ISCO period."""
    return _tau(tau) * math.log(10.0) * (-log10_eps) / _t_orb(d_over_M, M)


@extractor
def detector_seed_budget(ratio: float, tau=None) -> float:
    """tau ln(ratio): the time a seed lowered by ratio buys, code units."""
    return _tau(tau) * math.log(ratio)


@extractor
def detector_seed_budget_measured(what: str = "units", tau=None, d_over_M: float = 6.0,
                                  M: float = 2.0) -> float:
    """What constraint-solved data could buy, from the paper's own seeds: the seed
    lowered from the superposition defect's effective seed (the fly-by's mouth fit,
    detector_mouth_seed) to the level-3 truncation seed (single_noise_seed, itself a
    lower bound, so the ratio is an upper bound).  what = 'ratio', 'units'
    (tau ln ratio) or 'orbits' (units over the ISCO orbital period)."""
    ratio = detector_mouth_seed(arm="flyby") / EXTRACTORS["single_noise_seed"]()
    if what == "ratio":
        return ratio
    units = _tau(tau) * math.log(ratio)
    return units if what == "units" else units / _t_orb(d_over_M, M)


# =============================================================== the heavy-seed channel
def _hs():
    from grteclyn_wrapper.visualisation.wormhole_merger import plot_heavy_seeds as H
    return H


RHO_DM_PLANCK = 0.1200 * 2.775e11   # Omega_c h^2 (Planck 2018) x rho_crit/h^2, Msun Mpc^-3


@extractor
def detector_seed_input(name: str) -> float:
    """An input of the seed race / conversion background as plot_heavy_seeds sets it."""
    H = _hs()
    table = {"z_emit": H.Z_EMIT, "salpeter_myr": H.SALPETER_MYR,
             "seed_min": H.SEED_RANGE[0], "seed_max": H.SEED_RANGE[1],
             "n_min": H.N_RANGE[0], "n_max": H.N_RANGE[1],
             "J1342_z": H.J1342[0], "UHZ1_z": H.UHZ1[0]}
    return float(table[name])


@extractor
def detector_log10_input(name: str) -> float:
    """log10 of a plot_heavy_seeds input (masses and densities printed as 10^k)."""
    return math.log10(detector_seed_input(name=name))


@extractor
def detector_seed_efolds(m_seed: float, m_target: float = 1e9) -> float:
    """Eddington e-folds from m_seed to m_target."""
    return math.log(m_target / m_seed)


@extractor
def detector_seed_growth_myr(m_seed: float, m_target: float = 1e9) -> float:
    """Those e-folds at the Salpeter time plot_heavy_seeds uses, Myr."""
    return _hs().SALPETER_MYR * math.log(m_target / m_seed)


@extractor
def detector_cosmic_time_myr(z_from: float, z_to: float) -> float:
    """Cosmic time elapsed between two redshifts (plot_heavy_seeds' flat LCDM), Myr."""
    t = _hs().t_of_z
    return float(t(z_to) - t(z_from))


@extractor
def detector_light_seed_gap(m0: float = 100.0, z0: float = 25.0) -> float:
    """Decades by which an Eddington-limited light seed (m0 at z0) misses UHZ1."""
    H = _hs()
    z, m_obs = H.UHZ1[0], H.UHZ1[1]
    grown = m0 * math.exp((H.t_of_z(z) - H.t_of_z(z0)) / H.SALPETER_MYR)
    return math.log10(m_obs / grown)


@extractor
def detector_dm_fraction(n: float, m: float, log10: bool = False) -> float:
    """f = n M / rho_DM with rho_DM from Planck 2018 (Omega_c h^2 = 0.1200)."""
    f = n * m / RHO_DM_PLANCK
    return math.log10(f) if log10 else f


def _fM(fM) -> float:
    if fM in ("min", "max"):
        return detector_fpk_range(stat=fM)
    return float(fM)


@extractor
def detector_f_obs(m: float, fM="min", z: float = 20.0, unit: str = "mHz") -> float:
    """Observed frequency (fM)/[M(1+z)] of a conversion of mass m (Msun); fM
    'min'/'max' = the measured drainhole band peaks."""
    f = _fM(fM) / (m * _hs().MSUN_S * (1.0 + z))
    return f * {"Hz": 1.0, "mHz": 1e3, "uHz": 1e6}[unit]


def _energy(E) -> float:
    if isinstance(E, str):
        return detector_gw_energy(arm=E)
    return float(E)


@extractor
def detector_omega_log10(n: float, m: float, E="flyby", z: float = 20.0) -> float:
    """log10 Omega_GW = log10[n E_rad / (rho_c (1+z))], E_rad = E m; E an arm name
    (its measured E_rad/M) or a number; rho_c from plot_heavy_seeds (H0 = 67.7)."""
    return math.log10(n * _energy(E) * m / (_hs().RHO_C_MSUN_MPC3 * (1.0 + z)))


@extractor
def detector_lisa_log10(f_lo: float, f_hi: float | None = None, stat: str = "min") -> float:
    """log10 of the 4-yr power-law-integrated LISA sensitivity (plot_heavy_seeds,
    Robson-Cornish-Liu 2019 noise, SNR 10): at f_lo, or min/max over [f_lo, f_hi]."""
    H = _hs()
    f = np.logspace(-5.0, -0.5, 400)
    p = H.lisa_pls(f)
    if f_hi is None:
        return math.log10(float(np.interp(f_lo, f, p)))
    sel = (f >= f_lo) & (f <= f_hi)
    return math.log10(float(p[sel].min() if stat == "min" else p[sel].max()))


def _lisa():
    """gw_search.lisa and its arms {name: (waveform, spectrum, F99)} on the pack."""
    import warnings
    warnings.filterwarnings("ignore")
    from grteclyn_wrapper.gw_search import lisa as L
    return L, L.arms(str(PACK))


@extractor
def detector_lisa_snr(arms, masses, variant: str = "nominal", stat: str = "min",
                      z: float = 20.0) -> float:
    """min/max LISA burst SNR over arms x source-frame masses (gw_search.lisa:
    'nominal' = optimal orientation, instrument noise, whole record;
    'conservative' = inclination-averaged, confusion noise, resolved band)."""
    L, A = _lisa()
    arms = [arms] if isinstance(arms, str) else arms
    masses = [masses] if isinstance(masses, (int, float)) else masses
    v = [L.snr(*A[ARM_ALIAS[a]][:2], m, z, variant, A[ARM_ALIAS[a]][2])
         for a in arms for m in masses]
    return min(v) if stat == "min" else max(v)


@extractor
def detector_lisa_snr_peak(arm: str, variant: str = "conservative", z: float = 20.0) -> float:
    """The largest burst SNR over source-frame mass (1e2-1e9 Msun grid)."""
    L, A = _lisa()
    wf, spec, f99 = A[ARM_ALIAS[arm]]
    return L.mass_range(wf, spec, z, variant, f99)[3]


@extractor
def detector_lisa_mass_edge(arms, end: str, variant: str = "conservative",
                            z: float = 20.0) -> float:
    """Lightest ('lo') or heaviest ('hi') source-frame mass at which EVERY arm
    listed is at SNR >= 8 (the intersection of their mass ranges)."""
    L, A = _lisa()
    arms = [arms] if isinstance(arms, str) else arms
    r = [L.mass_range(A[ARM_ALIAS[a]][0], A[ARM_ALIAS[a]][1], z, variant,
                      A[ARM_ALIAS[a]][2]) for a in arms]
    if any(x[0] is None for x in r):
        raise ValueError("an arm never reaches SNR 8")
    return max(x[0] for x in r) if end == "lo" else min(x[1] for x in r)


@extractor
def detector_lisa_input(name: str) -> float:
    """A setting of gw_search.lisa / plot_heavy_seeds: 'f_min_mHz' (the SNR
    integral's lower edge, LISA's band floor), 'track_share_pct' (the share of
    int h_c^2 dln f each track of Fig. heavy_seeds(b) is drawn over)."""
    from grteclyn_wrapper.gw_search import lisa as L
    H = _hs()
    if name == "f_min_mHz":
        return 1e3 * L.F_MIN
    if name == "track_share_pct":
        import inspect
        return 100.0 * inspect.signature(H._track).parameters["share"].default
    raise KeyError(name)


@extractor
def detector_pls_n_threshold(m: float, arm: str = "spiral", z: float = 20.0) -> float:
    """n [Mpc^-3] above which conversions radiating like ``arm`` make a
    time-averaged Omega_GW above the 4-yr power-law-integrated sensitivity at
    their observed frequency (fM)_peak/[M(1+z)] (the ticks of Fig. heavy_seeds(c))."""
    H = _hs()
    f = H.f_obs(H.conversion_fM(), m, z)
    fg = np.logspace(-5.0, -0.5, 400)
    pls = float(np.exp(np.interp(math.log(f), np.log(fg), np.log(H.lisa_pls(fg)))))
    return pls / (detector_gw_energy(arm=arm) * m / (H.RHO_C_MSUN_MPC3 * (1.0 + z)))


@extractor
def detector_bursts(n: float, years: float = 4.0, z: float = 20.0) -> float:
    """Bursts LISA records in ``years`` from one-off conversions of comoving
    density n (Mpc^-3) at z: n 4 pi D_c(z)^2 c T."""
    return detector_burst_rate(n=n, z=z) * years


def _comoving_distance_mpc(z: float) -> float:
    H = _hs()
    zz = np.linspace(0.0, z, 200001)
    e = np.sqrt(H.OMEGA_M * (1.0 + zz) ** 3 + H.OMEGA_L)
    return 299792.458 / H.H0_KMSMPC * float(np.trapezoid(1.0 / e, zz))


@extractor
def detector_burst_rate(n: float, z: float = 20.0) -> float:
    """Observed rate of one-off conversions per year: every seed converts once,
    so dN/dt_obs = n * 4 pi D_c(z)^2 * c (comoving), independent of how the
    conversions are spread in time."""
    c_mpc_per_yr = 299792.458 * 3.15576e7 / 3.0857e19
    return n * 4.0 * math.pi * _comoving_distance_mpc(z) ** 2 * c_mpc_per_yr


@extractor
def detector_burst_duration_s(m: float, arms=("spiral", "fly-by"), z: float = 20.0) -> float:
    """Burst duration in s at mass m (Msun) and redshift z: the geometric mean
    of the arms' record lengths (the search templates' T/M)."""
    return 10.0 ** detector_burst_duration_log10(m=m, arms=arms, z=z)


@extractor
def detector_burst_duration_log10(m: float, arms=("spiral", "fly-by"), z: float = 20.0) -> float:
    """log10 of the burst duration in s at mass m (Msun) and redshift z: the
    geometric mean of the arms' record lengths (the search templates' T/M)."""
    H = _hs()
    wfs = _templates()
    d = [wfs[ARM_ALIAS[a]].duration_M * m * H.MSUN_S * (1.0 + z) for a in arms]
    return float(np.mean(np.log10(d)))


# =============================================================== Limitations: the scalar energies' sphere spread
@extractor
def detector_scalar_ratio_spread_pct(t_cut: float = 60.0) -> float:
    """Fly-by: |E_phi|/E_GW to t_cut on the inner sphere (R = 14) over the outer
    (R = 30), minus one, in % (plot_scalar_channel's integrals)."""
    from grteclyn_wrapper.visualisation.wormhole_merger import plot_scalar_channel as S
    run = PACK / "campaign" / S.FLYBY[0]
    ratio = {}
    for R in (14, 30):
        tg, fg = S._gw_flux(run / "psi4_mode_l2_all.dat", R)
        ts, kin, _ = S._scalar(run / "scalar_modes.dat", R)
        ratio[R] = abs(S._at(ts, S._cum(ts, kin), t_cut)) / S._at(tg, S._cum(tg, fg), t_cut)
    return 100.0 * (ratio[14] / ratio[30] - 1.0)


@extractor
def detector_ephi_sphere_ratio(run: str, t0: float, radii: list[int] = (10, 14, 18),
                               t1: float | None = None) -> float:
    """max|E_phi| / min|E_phi| across spheres, E_phi = integral of the physical
    flux -F_kin from t0 (horizon formation) to t1 (default: the record's end)."""
    from grteclyn_wrapper.visualisation.wormhole_merger import plot_scalar_censorship as C
    path = run_dir(run) / "scalar_modes.dat"
    vals = []
    for R in radii:
        t, k = C._flux(path, R)
        m = t >= t0
        if t1 is not None:
            m &= t <= t1
        vals.append(abs(float(np.trapezoid(-k[m], t[m]))))
    return max(vals) / min(vals)
