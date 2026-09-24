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

WHAT IS *NOT* COUNTED, and why the number used to be too high.  This walks
directories, and the pack holds directories that are not evolutions:

* ``<run>.__keep`` -- a byte-identical second copy of a run, left by the
  prune when a plotfile was held back.  Counting it charged the campaign
  twice for the same GPU time: ten of them, **187 h**, a fifth of the old
  total, and ten evolutions that never ran.  A copy is dropped only when the
  run it copies is still beside it; a lone ``X.__keep`` is the last record of
  a real evolution and is COUNTED, with a warning.
* ``*_HOOKFAIL*``, ``*_OLD``, ``*_BAD``, ``*.bak`` -- a launch that failed in
  the harness and was relaunched under the real name.  Always dropped: there
  is no original to point back to, and it evolved nothing.

Both are *dropped and named* in the report, never silently.  The shakedown
stage (``01_single_throat/gauge`` and ``grid``) is counted but reported on its
own line: the article declares it archived and not used for physics, so the
cost of the cited physics is the total minus that line.

Usage:  python analysis/gpu_hours.py [--root campaign] [--per-run]
"""

import argparse
import re
from pathlib import Path

# Directory names that are a COPY or a dead launch, not an evolution of their
# own.  A run matching any of these is dropped from the accounting and listed.
# A COPY: the prune's held-back duplicate.  Its name is the run's name plus a
# suffix, so the original is findable and the guard below can insist it exists.
A_COPY = re.compile(r"\.__keep$")
# A DEAD LAUNCH: relaunched under the real name, never a record of anything.
# Its name carries a marker anywhere, so there is no original to point back to.
A_DEAD_LAUNCH = re.compile(r"(HOOKFAIL|_OLD$|_BAD$|\.bak$)")

# The archived shakedown: counted, but reported apart -- the article declares
# it fixed the gauge/dissipation/tagging choices and is not used for physics.
SHAKEDOWN = ("01_single_throat/gauge/", "01_single_throat/grid/")

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


def restart_time(run_dir):
    """Code time of the checkpoint the run restarted from, or None.

    ChkNNNNN is the parent's coarse step, so t = NNNNN * dt0 with the run's
    own dt0 = dt_multiplier * L / N1 (every restart keeps its parent's box).
    Read from the params' amr.restart, else the launch banner."""
    params = {}
    pf = run_dir / "evolution_params.txt"
    if pf.exists():
        for line in pf.read_text(errors="replace").splitlines():
            m = re.match(r"\s*([A-Za-z_][\w.]*)\s*=(.*)$", line.split("#", 1)[0])
            if m:
                params[m.group(1)] = m.group(2).strip()
    texts = [params.get("amr.restart", "")]
    banner = run_dir / "launch_banner.txt"
    if banner.exists():
        texts += [l for l in banner.read_text(errors="replace").splitlines() if "restart" in l]
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


def leg_start(run_dir, suffix):
    """First recorded time of the leg run_tail{suffix}.log belongs to.

    A leg with no packed stream starts at its restart time, not at 0: GRTeclyn
    logs speed = (t - t_restart) / wall time (GRAMRLevel.cpp), so the t = 0
    fallback charged a restarted leg for its parent's whole history too --
    ten restart legs from the t = 50 checkpoint whose streams are not packed,
    160.7 h in all (ladder_L7: 49.6 h charged for 5.5 h run).  Found by the
    claims ledger, 2026-09-24."""
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
    if not suffix:
        t_restart = restart_time(run_dir)
        if t_restart is not None:
            return t_restart
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
    shakedown = [0, 0.0]
    dropped = []
    n_runs = 0

    for run_dir in sorted({p.parent for p in args.root.rglob("run_tail*.log")}):
        rel = run_dir.relative_to(args.root)
        if A_DEAD_LAUNCH.search(run_dir.name):
            dropped.append(f"{rel}  (dead launch)")
            continue
        if A_COPY.search(run_dir.name):
            # Drop the copy -- but only if the run it copies is still here.  A
            # lone ``X.__keep`` with no ``X`` beside it is the only surviving
            # record of a real evolution, and dropping it would lose the hours
            # silently, which is the failure this whole block exists to stop.
            twin = run_dir.parent / A_COPY.sub("", run_dir.name)
            if twin.is_dir():
                dropped.append(f"{rel}  (copy of {twin.name})")
                continue
            warnings.append(f"KEPT {rel}: named like a copy, but no "
                            f"{twin.name} is beside it -- counted as a run")
        group = rel.parts[0]
        is_shakedown = str(rel).startswith(SHAKEDOWN)
        n_runs += 1
        if is_shakedown:
            shakedown[0] += 1
        main_speed = None

        for tail in sorted(run_dir.glob("run_tail*.log")):
            suffix = tail.name[len("run_tail"):-len(".log")]
            speed, t_end = parse_tail(tail)
            if speed is not None and speed <= 0.0:
                # died in start-up (the OOMFAIL stubs): no time evolved, nothing to divide
                warnings.append(f"speed 0 (no step completed), counted 0 h: {tail.relative_to(args.root)}")
                continue
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
            if is_shakedown:
                shakedown[1] += hours
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
    print(f"{'  of which shakedown':<24}{shakedown[0]:>6}{shakedown[1]:>12.1f}"
          "   (archived, not used for physics)")
    print(f"{'  CITED PHYSICS':<24}{n_runs - shakedown[0]:>6}"
          f"{total - shakedown[1]:>12.1f}   <- the article's number")

    if dropped:
        print(f"\nnot evolutions, dropped ({len(dropped)}) -- copies and dead "
              f"launches, see A_COPY / A_DEAD_LAUNCH:")
        print("\n".join("  " + d for d in sorted(dropped)))
    if estimated:
        print(f"\nestimated legs (no tail of their own, {len(estimated)}):")
        print("\n".join("  " + e for e in estimated))
    if warnings:
        print(f"\nwarnings ({len(warnings)}):")
        print("\n".join("  " + w for w in warnings))


if __name__ == "__main__":
    main()
