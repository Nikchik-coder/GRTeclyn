#!/usr/bin/env python3
"""GPU-hours accounting for the packed merger campaign.

Every packed run carries the evolution's own clock: AMReX prints a cumulative
"average evolution speed = X code units/h" every step, run_tail.log keeps the
last of them together with the final "ADVANCE at time", and the leg's start
time is the first row of its constraint stream (0 for a run from birth, the
checkpoint time for a restart).  Wall hours per leg are then

    (t_end - t_start) / speed

which reproduces the hand-recorded numbers (the level-5 head-on: 18.6 h).
Legs that pre-date the pack format (``__partN`` streams with no tail of their
own) get an estimate from the same run's main-leg speed and are reported
separately.  Re-run after filing new runs; the total is what the article's
"Computational cost" section quotes.

Usage:  python analysis/gpu_hours.py [--root campaign] [--per-run]
"""

import argparse
import re
from pathlib import Path

SPEED_RE = re.compile(r"average evolution speed\s*=\s*([0-9.eE+-]+)\s*code units/h")
ADVANCE_RE = re.compile(r"ADVANCE at time\s*([0-9.eE+-]+)")

# Streams whose first data row dates a leg's start, in order of preference.
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


def leg_start(run_dir, suffix):
    """First recorded time of the leg run_tail{suffix}.log belongs to."""
    for stem in START_STREAMS:
        if suffix:
            hits = sorted(run_dir.glob(f"{stem}{suffix}*.dat"))
        else:
            p = run_dir / f"{stem}.dat"
            hits = [p] if p.exists() else []
        for p in hits:
            t0, _ = first_and_last_time(p)
            if t0 is not None:
                return t0
    return 0.0


def parse_tail(path):
    text = path.read_text(errors="replace")
    speeds = SPEED_RE.findall(text)
    advances = ADVANCE_RE.findall(text)
    speed = float(speeds[-1]) if speeds else None
    t_end = float(advances[-1]) if advances else None
    return speed, t_end


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path,
                    default=Path(__file__).resolve().parents[1] / "campaign",
                    help="campaign pack tree (default: ../campaign)")
    ap.add_argument("--per-run", action="store_true",
                    help="print one line per leg, not only the group table")
    args = ap.parse_args()

    groups, warnings, estimated = {}, [], []
    n_runs = 0

    for run_dir in sorted({p.parent for p in args.root.rglob("run_tail*.log")}):
        group = run_dir.relative_to(args.root).parts[0]
        n_runs += 1
        main_speed = None

        for tail in sorted(run_dir.glob("run_tail*.log")):
            suffix = tail.name[len("run_tail"):-len(".log")]
            speed, t_end = parse_tail(tail)
            if speed is None or t_end is None:
                warnings.append(f"no speed/ADVANCE line: {tail.relative_to(args.root)}")
                continue
            if not suffix:
                main_speed = speed
            t_start = leg_start(run_dir, suffix)
            hours = max(t_end - t_start, 0.0) / speed
            groups.setdefault(group, [0, 0.0])
            groups[group][0] += 0 if suffix else 1
            groups[group][1] += hours
            if args.per_run:
                print(f"{hours:8.2f} h  {speed:7.2f} u/h  t={t_start:g}->{t_end:g}"
                      f"  {run_dir.relative_to(args.root)}{suffix}")

        # Streams of legs that have no tail of their own (old __partN merges):
        # estimate from the main leg's speed so nothing is silently dropped.
        for part in sorted(run_dir.glob("constraint_norms__part*.dat")):
            t0, t1 = first_and_last_time(part)
            if t0 is None:
                continue
            if main_speed:
                hours = (t1 - t0) / main_speed
                groups[group][1] += hours
                estimated.append(f"{hours:6.2f} h  (span {t0:g}->{t1:g} at main-leg "
                                 f"speed)  {part.relative_to(args.root)}")
            else:
                warnings.append(f"part leg with no usable main speed: "
                                f"{part.relative_to(args.root)}")

    total = sum(h for _, h in groups.values())
    print(f"\n{'group':<24}{'runs':>6}{'GPU-hours':>12}")
    for g in sorted(groups):
        n, h = groups[g]
        print(f"{g:<24}{n:>6}{h:>12.1f}")
    print(f"{'TOTAL':<24}{n_runs:>6}{total:>12.1f}")

    if estimated:
        print(f"\nestimated legs (no tail of their own, {len(estimated)}):")
        print("\n".join("  " + e for e in estimated))
    if warnings:
        print(f"\nwarnings ({len(warnings)}):")
        print("\n".join("  " + w for w in warnings))


if __name__ == "__main__":
    main()
