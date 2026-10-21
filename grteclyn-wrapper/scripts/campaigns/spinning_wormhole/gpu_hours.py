#!/usr/bin/env python
"""GPU-hours of the packed spinning-wormhole campaign, by the merger paper's method.

Each run's wall time is (t_end - t_start) / speed from its own logs, through
the merger accounting (grteclyn_wrapper.analysis.wormhole_merger.pack.gpu_hours):
AMReX's last "average evolution speed" and "ADVANCE at time" in run_tail.log,
the start from the first row of the run's constraint stream, a restart dated
from its checkpoint.  The merger walker stops at campaign/<group>/<sub>/<run>;
this pack nests a family level deeper (campaign/<family>/<group>/[<sub>/]<run>),
so here every directory holding a run_tail.log is a run.

Prints the GPU-hours per group and in total, then the paper's runs
(00_paper_runs) by box and grid: speed, cost and peak device memory (AMReX's
"[The Arena] max space (MB) used"): the numbers of the article's
reproducibility and cost paragraph.  Live runs are never packed, so a run in
flight is not counted.

    grteclyn-wrapper/.venv/bin/python \\
        grteclyn-wrapper/scripts/campaigns/spinning_wormhole/gpu_hours.py [--per-run]
"""

from __future__ import annotations

import argparse
import pathlib
import re

from grteclyn_wrapper.analysis.wormhole_merger.pack.gpu_hours import leg_start, parse_tail
from grteclyn_wrapper.analysis.wormhole_merger.pack.readers import parse_params

REPO = pathlib.Path(__file__).resolve().parents[4]
CAMPAIGN = REPO / "results" / "spinningwormhole" / "campaign"
PAPER = "00_paper_runs"
ARENA_RE = re.compile(r"\[The\s+Arena\] max space \(MB\) used\s+spread across MPI: \[(\d+)")


def cost(run_dir: pathlib.Path) -> dict | None:
    """Hours, speed, time span, box, grid and peak memory of one packed run;
    None for a run that never completed a step."""
    speed, t_end = parse_tail(run_dir / "run_tail.log")
    if not speed or t_end is None:
        return None
    t_start = leg_start(run_dir)
    params = parse_params(run_dir / "evolution_params.txt")
    mem = ARENA_RE.findall((run_dir / "run_tail.log").read_text(errors="replace"))
    return dict(hours=max(t_end - t_start, 0.0) / speed, speed=speed, t_start=t_start,
                t_end=t_end, L=float(params["L"]), N=int(params["N1"].split()[0]),
                mem_mb=int(mem[-1]) if mem else None)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--per-run", action="store_true", help="one line per run as well")
    args = ap.parse_args()

    groups: dict[str, list[float]] = {}
    paper: list[dict] = []
    skipped = []
    for tail in sorted(CAMPAIGN.rglob("run_tail.log")):
        run_dir = tail.parent
        rel = run_dir.relative_to(CAMPAIGN)
        c = cost(run_dir)
        if c is None:
            skipped.append(str(rel))
            continue
        g = groups.setdefault("/".join(rel.parts[:2]), [0, 0.0])
        g[0] += 1
        g[1] += c["hours"]
        if rel.parts[1] == PAPER:
            paper.append(c)
        if args.per_run:
            print(f"{c['hours']:7.2f} h  {c['speed']:7.2f} u/h  t={c['t_start']:g}->{c['t_end']:g}  {rel}")

    n = sum(g[0] for g in groups.values())
    total = sum(g[1] for g in groups.values())
    print(f"\n{'group':<36}{'runs':>6}{'GPU-hours':>12}")
    for name in sorted(groups):
        print(f"{name:<36}{groups[name][0]:>6}{groups[name][1]:>12.1f}")
    print(f"{'TOTAL':<36}{n:>6}{total:>12.1f}")

    print(f"\npaper runs ({PAPER}): {len(paper)} runs, {sum(c['hours'] for c in paper):.1f} GPU-hours")
    for box in sorted({(c["L"], c["N"]) for c in paper}):
        rows = [c for c in paper if (c["L"], c["N"]) == box]
        sp = [c["speed"] for c in rows]
        h = [c["hours"] for c in rows]
        mem = [c["mem_mb"] for c in rows if c["mem_mb"]]
        print(f"  L {box[0]:g}, N {box[1]}: {len(rows)} runs, {min(sp):.1f}-{max(sp):.1f} u/h, "
              f"{min(h):.1f}-{max(h):.1f} h per run"
              + (f", peak {max(mem) / 1024:.1f} GiB" if mem else ""))
    if skipped:
        print(f"\nno completed step, counted 0 h ({len(skipped)}): " + ", ".join(skipped))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
