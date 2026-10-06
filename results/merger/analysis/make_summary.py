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

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pack_paths import iter_runs  # noqa: E402

# What each run changes, the order the campaign reads in, the caveat attached to
# a finished-clean outcome and the stopped-by-hand notes all live in ONE file
# beside the packs, runs_registry.tsv, so registering a run is one appended line
# (the launcher writes it when WHM_WHAT is set) and never a code edit.
REGISTRY = "runs_registry.tsv"
WHAT: dict[str, str] = {}
ORDER: list[str] = []
STOPPED: dict[str, str] = {}
CAVEAT: dict[str, str] = {}


def load_registry(path: pathlib.Path) -> None:
    """Fill WHAT / ORDER / STOPPED / CAVEAT from the tab-separated registry."""
    WHAT.clear(); ORDER.clear(); STOPPED.clear(); CAVEAT.clear()
    if not path.exists():
        print(f"[pack-merger] WARNING: no {path.name} -- every run is unregistered")
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("\t")]
        parts += [""] * (4 - len(parts))
        run, what, caveat, stopped = parts[:4]
        if run in WHAT:
            raise SystemExit(f"{path.name}: {run} registered twice")
        ORDER.append(run)
        WHAT[run] = what
        if caveat:
            CAVEAT[run] = " " + caveat
        if stopped:
            STOPPED[run] = stopped


CLEAN_BACK = 0.5   # how far before the end the "last clean" row is taken

FIELDS = [
    "run", "what_is_different", "t_start", "t_end", "outcome",
    "min_lapse", "min_chi", "max_abs_K", "L2_Ham", "L2_Mom",
    "sep_start", "sep_min", "t_sep_min", "sep_end",
    "t_common_ah", "ah_r_max_incode", "group",
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
    stopped = STOPPED.get(run_dir.name)
    if stopped is not None and t_end is not None:
        return stopped.format(t=t_end)
    return _outcome(run_dir, t_end) + CAVEAT.get(run_dir.name, "")


def _outcome(run_dir: pathlib.Path, t_end) -> str:
    tail = run_dir / "run_tail.log"
    if tail.exists():
        text = tail.read_text(errors="replace")
        if "NaN" in text:
            return f"NaN at t = {t_end:.2f}"
        # "AMReX ... finalized" is printed only on a normal shutdown; a NaN
        # abort never reaches it (checked across the campaign, 2026-09-04), and
        # the NaN test above wins anyway.  Without this, any run that simply
        # reached its stop_time short of t = 59.9 was mislabelled "still
        # running" -- which is how the finished a-points first showed up.
        if ("stop_time" in text or "Run time" in text
                or "finalized" in text):
            return f"finished clean at t = {t_end:.2f}"
    if t_end is not None and t_end >= 59.9:
        return f"finished clean at t = {t_end:.2f}"
    return "still running" if t_end is not None else "no time series"


def summarise(run_dir: pathlib.Path) -> dict:
    run = run_dir.name
    row = {k: "" for k in FIELDS}
    row["run"] = run
    row["what_is_different"] = WHAT.get(run, "(not in runs_registry.tsv)")

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
    load_registry(root / REGISTRY)
    # The pack is filed by physics (campaign/<group>/<run>); the table is one
    # block per group, and inside a group the registry order.
    groups: dict[str, dict[str, pathlib.Path]] = {}
    for g, d in iter_runs(root):
        groups.setdefault(g, {})[d.name] = d
    rows = []
    for g in sorted(groups):
        dirs = groups[g]
        ordered = [dirs[n] for n in ORDER if n in dirs]
        ordered += [d for n, d in sorted(dirs.items()) if n not in ORDER]
        for d in ordered:
            r = summarise(d)
            r["group"] = g
            rows.append(r)

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
        current = None
        for r in rows:
            if r["group"] != current:
                current = r["group"]
                fh.write(f"\n## `{current or '(unfiled, still on a card)'}`\n\n")
                fh.write("| " + " | ".join(head[c] for c in show) + " |\n")
                fh.write("|" + "|".join(["---"] * len(show)) + "|\n")
            fh.write("| " + " | ".join(r[c] or "-" for c in show) + " |\n")
        fh.write("\nFull column set, including the constraint and geometry extrema, is in\n"
                 "`summary.csv`.\n")
    print(f"[pack-merger] analysis: summary.csv, summary.md ({len(rows)} runs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
