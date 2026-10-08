"""GPU-hours accounting for the packed merger campaign.

Every packed run carries the evolution's own clock: AMReX prints a cumulative
"average evolution speed = X code units/h" every step, run_tail.log keeps the
last of them together with the final "ADVANCE at time", and the run's start
time is the first row of its constraint stream (0 for a run from birth, the
checkpoint time for a restart).  Wall hours per run are then

    (t_end - t_start) / speed

which reproduces the hand-recorded numbers (the level-5 head-on: 18.6 h).
This walks every packed run; the article quotes the Table III subset
(claims.py check --id clmDetGpuHours).

    python -m grteclyn_wrapper.analysis.wormhole_merger.pack.gpu_hours [<pack-root>] [--per-run]
"""

import argparse
import pathlib
import re

from grteclyn_wrapper.analysis.wormhole_merger.pack.paths import CAMPAIGN, PACK_ROOT, iter_runs
from grteclyn_wrapper.analysis.wormhole_merger.pack.readers import parse_params

SPEED_RE = re.compile(r"average evolution speed\s*=\s*([0-9.eE+-]+)\s*code units/h")
ADVANCE_RE = re.compile(r"ADVANCE at time\s*([0-9.eE+-]+)")

# Streams whose first data row dates a run's start, in order of preference.
START_STREAMS = ["constraint_norms", "collapse_diagnostics",
                 "binary_throat_diagnostics", "areal_radius", "throat_track"]


def first_and_last_time(path):
    first = last = None
    with open(path, errors="replace") as fh:
        for line in fh:
            tok = line.split()
            if not tok or line.lstrip().startswith("#"):
                continue
            try:
                t = float(tok[0])
            except ValueError:
                continue
            if first is None:
                first = t
            last = t
    return first, last


def restart_time(run_dir):
    """Code time of the checkpoint the run restarted from, or None.

    ChkNNNNN is the parent's coarse step, so t = NNNNN * dt0 with the run's
    own dt0 = dt_multiplier * L / N1 (every restart keeps its parent's box).
    Read from the params' amr.restart, else the launch banner."""
    pf = run_dir / "evolution_params.txt"
    params = parse_params(pf) if pf.exists() else {}
    texts = [params.get("amr.restart", "")]
    banner = run_dir / "launch_banner.txt"
    if banner.exists():
        texts += [ln for ln in banner.read_text(errors="replace").splitlines() if "restart" in ln]
    try:
        dt0 = (float(params["dt_multiplier"]) * float(params["L"])
               / float(params["N1"].split()[0]))
    except (KeyError, ValueError, IndexError):
        dt0 = 0.01                        # every merger run's coarse step
    for t in texts:
        m = re.search(r"Chk0*(\d+)", t)
        if m:
            return int(m.group(1)) * dt0
    return None


def leg_start(run_dir):
    """First recorded time of the run, else its restart time, else 0.

    A restart with no packed stream starts at its checkpoint, not at 0:
    GRTeclyn logs speed = (t - t_restart) / wall time (GRAMRLevel.cpp), so a
    t = 0 start would charge the run for its parent's whole history too."""
    for stem in START_STREAMS:
        p = run_dir / f"{stem}.dat"
        if p.exists():
            t0, _ = first_and_last_time(p)
            if t0 is not None:
                return t0
    t_restart = restart_time(run_dir)
    return 0.0 if t_restart is None else t_restart


def parse_tail(path):
    text = path.read_text(errors="replace")
    speeds = SPEED_RE.findall(text)
    advances = ADVANCE_RE.findall(text)
    speed = float(speeds[-1]) if speeds else None
    t_end = float(advances[-1]) if advances else None
    return speed, t_end


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pack", nargs="?", type=pathlib.Path, default=PACK_ROOT,
                    help="the pack (default: results/merger)")
    ap.add_argument("--per-run", action="store_true",
                    help="print one line per run, not only the group table")
    args = ap.parse_args()
    camp = args.pack / CAMPAIGN

    groups, warnings = {}, []
    n_runs = 0
    for _, run_dir in iter_runs(args.pack):
        tail = run_dir / "run_tail.log"
        if not tail.exists():
            continue
        rel = run_dir.relative_to(camp)
        n_runs += 1
        speed, t_end = parse_tail(tail)
        if speed is not None and speed <= 0.0:
            # died in start-up: no time evolved, nothing to divide
            warnings.append(f"speed 0 (no step completed), counted 0 h: {rel}/run_tail.log")
            continue
        if speed is None or t_end is None:
            warnings.append(f"no speed/ADVANCE line: {rel}/run_tail.log")
            continue
        t_start = leg_start(run_dir)
        hours = max(t_end - t_start, 0.0) / speed
        group = groups.setdefault(rel.parts[0], [0, 0.0])
        group[0] += 1
        group[1] += hours
        if args.per_run:
            print(f"{hours:8.2f} h  {speed:7.2f} u/h  t={t_start:g}->{t_end:g}  {rel}")

    total = sum(h for _, h in groups.values())
    print(f"\n{'group':<24}{'runs':>6}{'GPU-hours':>12}")
    for g in sorted(groups):
        n, h = groups[g]
        print(f"{g:<24}{n:>6}{h:>12.1f}")
    print(f"{'TOTAL':<24}{n_runs:>6}{total:>12.1f}   (every packed run; the article quotes "
          "the Table III subset: claims.py check --id clmDetGpuHours)")
    if warnings:
        print(f"\nwarnings ({len(warnings)}):")
        print("\n".join("  " + w for w in warnings))


if __name__ == "__main__":
    main()
