#!/usr/bin/env python3
"""Campaign M solver pipeline: the entry point over the capped jobs.

One place to see and drive the campaign's compute:

    pipeline.py plan                 the ten steps + what is next (STATUS.md)
    pipeline.py list                 stages from pipeline.toml, live state
    pipeline.py run <stage>          launch on CPU through capped_job.sh
    pipeline.py run <stage> --gpu N  the same solve on CUDA card N
    pipeline.py status [<stage>] | tail <stage> [n] | stop <stage>

Stages live in pipeline.toml next to this file; the record of what ran
and what it showed lives in STATUS.md.  Everything runs through
capped_job.sh (session-tracked, ulimit -v, hard timeout), because one
runaway process restarts the whole node container.

GPU: a run with --gpu N passes the card to the solver script's --gpu
flag and checks first that card N is idle (the cards are shared); the
standing rule is that nothing starts on a card without the go.
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]          # grteclyn-wrapper/scripts/optimisation


def load():
    cfg = tomllib.loads((HERE / "pipeline.toml").read_text())
    return cfg, {s["name"]: s for s in cfg.get("stage", [])}


def job_state(runner_cfg, name):
    d = REPO / "runs" / "capped_jobs" / name
    if not d.is_dir():
        return "-"
    out = subprocess.run(
        ["bash", str(REPO / runner_cfg), "status", name],
        capture_output=True, text=True).stdout.strip()
    return out.split()[1] if out else "?"


def cmd_plan(cfg):
    status = (REPO / cfg["campaign"]["status"]).read_text().splitlines()
    take, section = False, ("## Steps", "## Now", "## Next")
    for line in status:
        if line.startswith("## "):
            take = line.startswith(section)
        if take:
            print(line)
    return 0


def cmd_list(cfg, stages):
    print(f"campaign {cfg['campaign']['name']}  "
          f"[branch {cfg['campaign']['branch']}]")
    for s in stages.values():
        state = job_state(cfg["campaign"]["runner"], s["name"])
        print(f"  {s['name']:24s} {state:14s} step {s['step']:8s} {s['title']}")
    print(f"record: {cfg['campaign']['status']}")
    return 0


def cmd_run(cfg, stages, name, gpu, dry, force):
    if name not in stages:
        sys.exit(f"pipeline: no stage '{name}' (see: pipeline.py list)")
    s = stages[name]
    d = cfg["defaults"]
    mem = s.get("gpu_mem_gb" if gpu is not None else "mem_gb",
                d["gpu_mem_gb" if gpu is not None else "mem_gb"])
    cmd = ["bash", str(REPO / cfg["campaign"]["runner"]), "start", s["name"],
           "--threads", str(s.get("threads", d["threads"])),
           "--mem", str(mem),
           "--timeout", str(s.get("timeout_s", d["timeout_s"]))]
    if gpu is not None:
        cmd.append("--gpu")
    cmd += ["--", str(REPO / cfg["campaign"]["python"]),
            str(REPO / s["script"]), *s["args"]]
    if gpu is not None:
        cmd += ["--gpu", str(gpu)]
        q = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,memory.used,utilization.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True).stdout
        print(q.strip() or "nvidia-smi gave nothing")
        for row in q.strip().splitlines():
            idx, used_mb, util = (int(v) for v in row.split(","))
            if idx == gpu and (used_mb > 5000 or util > 5) and not force:
                sys.exit(f"pipeline: card {gpu} is busy ({used_mb} MiB, "
                         f"{util}% util); pick another or --force")
    print(" ".join(cmd))
    if dry:
        return 0
    return subprocess.run(cmd, cwd=REPO).returncode


def passthrough(cfg, verb, rest):
    return subprocess.run(
        ["bash", str(REPO / cfg["campaign"]["runner"]), verb, *rest],
        cwd=REPO).returncode


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="verb", required=True)
    sub.add_parser("plan")
    sub.add_parser("list")
    p_run = sub.add_parser("run")
    p_run.add_argument("stage")
    p_run.add_argument("--gpu", type=int, default=None, metavar="CARD")
    p_run.add_argument("--dry-run", action="store_true")
    p_run.add_argument("--force", action="store_true",
                       help="launch even if the card looks busy")
    for v in ("status", "tail", "stop"):
        p = sub.add_parser(v)
        p.add_argument("rest", nargs="*")
    args = ap.parse_args()

    cfg, stages = load()
    if args.verb == "plan":
        return cmd_plan(cfg)
    if args.verb == "list":
        return cmd_list(cfg, stages)
    if args.verb == "run":
        return cmd_run(cfg, stages, args.stage, args.gpu,
                       args.dry_run, args.force)
    return passthrough(cfg, args.verb, args.rest)


if __name__ == "__main__":
    sys.exit(main())
