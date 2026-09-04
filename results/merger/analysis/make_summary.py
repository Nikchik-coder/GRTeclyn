#!/usr/bin/env python3
"""Build summary.csv and summary.md from the packed merger campaign streams.

One row per run.  Every number is read out of the packed `.dat` files, so the
table cannot drift away from the data beside it.

The *last clean* columns are deliberately not the final row: a run that dies of
a NaN writes one last step in which the fields have already blown up (max |K| of
3648, an L2 Hamiltonian of 4.4).  Quoting that row as the state of the spacetime
would be quoting the crash.  These columns come from the row half a time unit
earlier, which is the last state the run actually computed.

Usage: make_summary.py <pack-root>          (default: this file's parent's parent)
"""

from __future__ import annotations

import csv
import pathlib
import re
import sys

import numpy as np

# What each run changes relative to the main arm.  Kept in step with
# runs/wormhole_merger/README.md, which explains them at length.
WHAT = {
    "merge_orbit_flip_d12_r03000": "main arm, no damping (its __part1 files are t = 0 -> 30.5)",
    "merge_orbit_flip_d12_r05000": "narrow lapse window (1e-6 -> 1e-8, the built-in default)",
    "merge_orbit_flip_d12_r04000": "wide lapse window (3e-2 -> 1e-3), full metric plotted",
    "merge_orbit_flip_d12_sg10_r05000": "wide lapse window, dissipation sigma 0.1 -> 1.0",
    "merge_orbit_flip_d12_rw_r05000": "radius window: full inside r = 0.5, off by 0.7, from t = 33",
    "merge_headon_flip_d12": "head-on: no orbital momentum",
    "merge_orbit_flip_d12_p045": "momentum 0.45 instead of 0.12",
    "merge_orbit_flip_d12_n160": "160 cells per side instead of 128",
    "merge_orbit_flip_d12_ml2": "max_level = 2 instead of 3",
    # The capture scan (2026-09-02): same template, damping on, stop_time 200.
    "merge_orbit_flip_d12_p020_t200": "scout p = 0.20: captured, stopped by hand at t = 47.8",
    "merge_orbit_flip_d12_p025_t200": "scout p = 0.25: captured to sep 1.5, h11 NaN",
    "merge_orbit_flip_d12_p035_t200": "scout p = 0.35: fly-by (min sep 2.75), stopped by hand",
    "merge_orbit_flip_d12_p045_t200": "scout p = 0.45: fly-by, the healthy control at t200",
    # The Helfer twins (2026-09-02/03): p = 0.12, identical but for initial data.
    "merge_twin_p012_plain_t100": "p = 0.12 twin, plain superposition: merged, stopped by hand at t = 44",
    "merge_twin_p012_helfer_t100": "p = 0.12 twin, Helfer correction (auto width 4): stalled, zombie, stopped at t = 60.3",
    "merge_twin_p012_helfer_lvl4_t100": "Helfer twin at max_level = 4: reproduces the stall, stopped by hand",
    "merge_twin_p012_helfer_lvl5_t100": "Helfer twin at max_level = 5: stalled the same, stopped at t = 31.5",
    "merge_twin_p012_helfer_w2_t060": "Helfer twin, window halved to 2.0: stalled worse (sep 5.10 at t = 32 gate), stopped at t = 33.1",
    # The unmasked wall probes (2026-09-03).
    "merge_orbit_flip_d12_p020_nofill_t060": "p = 0.20 unmasked, damping off: hovered at sep 1.08 from t = 46, NaN at t = 52.08",
    "merge_orbit_flip_d12_p020_lvl5_t200": "scout p = 0.20 at max_level = 5: same wall as level 3, NaN (h11) at t = 52.07",
    "merge_orbit_flip_d12_p025_lvl5_t200": "scout p = 0.25 at max_level = 5: same wall as level 3, NaN (h11) at t = 52.79",
    "merge_orbit_flip_d12_p015_nofill_t060": "scout p = 0.15 unmasked: fusing branch (plateau 0.816, dive to 0.70, core lapse rising) but pits not coincident when the wall hit at t = 53.35",
    "merge_twin_p012_lc1_t060": "gauge arm (#15), lapse_coeff 2 -> 1: blob and plunge intact (sep 0.442) but the wall moved to t = 43.64 -- wall time is gauge, not physics",
    "merge_twin_p012_nodamp_t060": "damping-off arm (#14): blob nucleates identically without damping (t = 32 slices match plain to 3 decimals); wall at t = 51.53 vs plain 52.06 -- damping neither causes nor delays the wall",
    "merge_orbit_flip_d12_p015_rr_t060": "p = 0.15 rerun with insured checkpoints: wall reproduced at the same step (t = 53.35); the t = 50 seed for the phase-2 refinement is held",
    "merge_orbit_flip_d12_p015_lvl5_t060_r05000": "p = 0.15 refined restart (max_level 5 from the t = 50 seed): wall pushed only +0.88 (h11 NaN t = 54.23), no trapped surface at death, waveform still rising at 3.14e-2 -- wall-cut mid-fusion a third time",
    # The floor ladder (#16, 2026-09-04): chi_floor rungs restarted from the t = 50 seed.
    "merge_twin_p012_cf08_t060_r05000": "floor ladder rung chi_floor 1e-8 (the reference control), restart from t = 50 with levels 4-5: healthy to t = 55.53 (h11 NaN, level 5) -- longest-lived p012 arm; level-5 scan holds a trapped shell r = 0.94 -> 0.90 over its last unit",
    "merge_twin_p012_cf10_t060_r05000": "floor ladder rung chi_floor 1e-10: NaN 0.006 after restart -- the t = 50 state is floor-regularized, restarts cannot certify floor-independence",
    "merge_twin_p012_cf12_t060_r05000": "floor ladder rung chi_floor 1e-12: NaN 0.049 after restart -- same verdict as cf10",
    "merge_twin_p012_nodamp_cf10_t060": "the decisive floor test: damping off AND min_chi 1e-10 from t = 0 (not a restart) -- IN FLIGHT",
    "bbh_control_d12_p012": "vacuum BBH control, same ADM masses/d/p as p012: merged t ~ 70, clean to t = 100",
    "bbh_control_d12_p012_t150": "BBH control rerun to t = 150, fixed-center consumer: full ringdown in hand, instruments agree to 0.3 %, QNM fit consistent with a Kerr remnant (~15.6M / ~14.2M at R = 30)",
}
# The order the campaign reads in: the restart chain, then the probes.
ORDER = [
    "merge_orbit_flip_d12_r03000",
    "merge_orbit_flip_d12_r05000",
    "merge_orbit_flip_d12_r04000",
    "merge_orbit_flip_d12_sg10_r05000",
    "merge_orbit_flip_d12_rw_r05000",
    "merge_headon_flip_d12",
    "merge_orbit_flip_d12_p045",
    "merge_orbit_flip_d12_n160",
    "merge_orbit_flip_d12_ml2",
    "merge_orbit_flip_d12_p020_t200",
    "merge_orbit_flip_d12_p025_t200",
    "merge_orbit_flip_d12_p035_t200",
    "merge_orbit_flip_d12_p045_t200",
    "merge_twin_p012_plain_t100",
    "merge_twin_p012_helfer_t100",
    "merge_twin_p012_helfer_lvl4_t100",
    "merge_twin_p012_helfer_lvl5_t100",
    "merge_twin_p012_helfer_w2_t060",
    "merge_orbit_flip_d12_p020_nofill_t060",
    "merge_orbit_flip_d12_p020_lvl5_t200",
    "merge_orbit_flip_d12_p025_lvl5_t200",
    "merge_orbit_flip_d12_p015_nofill_t060",
    "merge_orbit_flip_d12_p015_rr_t060",
    "merge_orbit_flip_d12_p015_lvl5_t060_r05000",
    "merge_twin_p012_cf08_t060_r05000",
    "merge_twin_p012_cf10_t060_r05000",
    "merge_twin_p012_cf12_t060_r05000",
    "merge_twin_p012_nodamp_cf10_t060",
]
CLEAN_BACK = 0.5   # how far before the end the "last clean" row is taken

FIELDS = [
    "run", "what_is_different", "t_start", "t_end", "outcome",
    "min_lapse", "min_chi", "max_abs_K", "L2_Ham", "L2_Mom",
    "sep_start", "sep_min", "t_sep_min", "sep_end",
    "t_common_ah", "ah_r_max_incode",
]


def load(path: pathlib.Path):
    if not path.exists():
        return None
    try:
        a = np.loadtxt(path)
    except Exception:
        return None
    return a if a.ndim == 2 and a.size else None


def outcome(run_dir: pathlib.Path, t_end) -> str:
    tail = run_dir / "run_tail.log"
    if tail.exists():
        text = tail.read_text(errors="replace")
        if "NaN" in text:
            return f"NaN at t = {t_end:.2f}"
        if "stop_time" in text or "Run time" in text:
            return f"finished clean at t = {t_end:.2f}"
    if t_end is not None and t_end >= 59.9:
        return f"finished clean at t = {t_end:.2f}"
    return "still running" if t_end is not None else "no time series"


def summarise(run_dir: pathlib.Path) -> dict:
    run = run_dir.name
    row = {k: "" for k in FIELDS}
    row["run"] = run
    row["what_is_different"] = WHAT.get(run, "")

    coll = load(run_dir / "collapse_diagnostics.dat")
    if coll is None:
        # A log-only arm: the death time is all that survives it.
        tail = run_dir / "run_tail.log"
        times = ([float(m) for m in re.findall(r"TIME = ([\d.]+)", tail.read_text(errors="replace"))]
                 if tail.exists() else [])
        t_end = max(times) if times else None
        if t_end is not None:
            row["t_end"] = f"{t_end:.2f}"
            # vacuum controls never write collapse diagnostics but do carry
            # their waveform streams; only call the streams lost if they are
            if (run_dir / "weyl_extraction_mode_22.dat").exists():
                row["outcome"] = outcome(run_dir, t_end) + " (vacuum control: waveform streams in hand)"
            else:
                row["outcome"] = outcome(run_dir, t_end) + " (streams lost, log only)"
        else:
            row["outcome"] = "data lost"
        return row

    t = coll[:, 0]
    row["t_start"], row["t_end"] = f"{t[0]:.2f}", f"{t[-1]:.2f}"
    row["outcome"] = outcome(run_dir, t[-1])
    # min_lapse min_chi max_abs_K sit in columns 1..3.
    i = int(np.argmin(np.abs(t - (t[-1] - CLEAN_BACK))))
    row["min_lapse"] = f"{coll[i, 1]:.3e}"
    row["min_chi"] = f"{coll[i, 2]:.3e}"
    row["max_abs_K"] = f"{coll[i, 3]:.3f}"

    cons = load(run_dir / "constraint_norms.dat")
    if cons is not None:
        j = int(np.argmin(np.abs(cons[:, 0] - (cons[-1, 0] - CLEAN_BACK))))
        row["L2_Ham"] = f"{cons[j, 1]:.3e}"
        row["L2_Mom"] = f"{cons[j, 2]:.3e}"

    bt = load(run_dir / "binary_throat_diagnostics.dat")
    if bt is not None:
        sep, ah = bt[:, 1], bt[:, 17]
        tb = bt[:, 0]
        # One-sample tracker glitches: when the throats swap sides both finders
        # can latch onto the same one for a single row, reporting sep ~ 0
        # between neighbours of ~4.  Drop rows that disagree with both
        # neighbours by more than half the local scale.
        good = np.ones(sep.size, bool)
        if sep.size > 2:
            nb = 0.5 * (sep[:-2] + sep[2:])
            good[1:-1] = np.abs(sep[1:-1] - nb) < 0.5 * np.maximum(nb, 1e-9)
        s = sep[good]
        tg = tb[good]
        row["sep_start"] = f"{sep[0]:.2f}"
        row["sep_min"] = f"{s.min():.2f}"
        row["t_sep_min"] = f"{tg[int(np.argmin(s))]:.2f}"
        row["sep_end"] = f"{s[-1]:.2f}"
        hit = np.where(ah > 0)[0]
        row["t_common_ah"] = f"{tb[hit[0]]:.2f}" if hit.size else "-"
        row["ah_r_max_incode"] = f"{ah.max():.2f}" if hit.size else "-"
    return row


def main(argv: list[str]) -> int:
    root = pathlib.Path(argv[1]) if len(argv) > 1 else pathlib.Path(__file__).resolve().parents[1]
    camp = root / "campaign"
    dirs = {d.name: d for d in camp.iterdir() if d.is_dir()}
    ordered = [dirs[n] for n in ORDER if n in dirs]
    ordered += [d for n, d in sorted(dirs.items()) if n not in ORDER]
    rows = [summarise(d) for d in ordered]

    with open(root / "summary.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    show = ["run", "what_is_different", "t_start", "t_end", "outcome",
            "sep_min", "t_common_ah", "min_lapse", "L2_Ham"]
    head = {"run": "run", "what_is_different": "what is different", "t_start": "from",
            "t_end": "to", "outcome": "outcome", "sep_min": "min throat sep",
            "t_common_ah": "common horizon at", "min_lapse": "min lapse*",
            "L2_Ham": "L2 Ham*"}
    with open(root / "summary.md", "w", encoding="utf-8") as fh:
        fh.write("# Merger campaign — one row per run\n\n")
        fh.write("Generated by `analysis/make_summary.py` from the packed streams; do not\n"
                 "hand-edit. Columns marked \\* are read half a time unit before the end, so a\n"
                 "dead run is described by its last computed state rather than by its crash.\n"
                 "Times are quantised to the packed dt = 0.05. `min throat sep` is the closest\n"
                 "the two throat finders ever came; once the throats have merged they are both\n"
                 "reading structure inside one collapsed core, so on the restart arms that\n"
                 "number describes the core, not an approach. `common horizon at` is the\n"
                 "IN-CODE radial proxy and fires spuriously on the collapsing inter-throat\n"
                 "midpoint: every level-3 twin reports t = 29-31 — including the stalled\n"
                 "Helfer runs with throats 5 apart, where no horizon is possible. Only hits\n"
                 "corroborated by the offline scan in `horizon/` (the headline arms,\n"
                 "t = 51.4+) are evidence of a common horizon.\n\n")
        fh.write("| " + " | ".join(head[c] for c in show) + " |\n")
        fh.write("|" + "|".join(["---"] * len(show)) + "|\n")
        for r in rows:
            fh.write("| " + " | ".join(r[c] or "-" for c in show) + " |\n")
        fh.write("\nFull column set, including the constraint and geometry extrema, is in\n"
                 "`summary.csv`.\n")
    print(f"[pack-merger] analysis: summary.csv, summary.md ({len(rows)} runs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
