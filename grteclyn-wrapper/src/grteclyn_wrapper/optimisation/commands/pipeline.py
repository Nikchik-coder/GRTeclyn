"""Inspect and run configured optimisation stages under resource caps.

Input: a stage name and an operation such as list, run, status, tail or stop.
Output: stage state, a proposed command, or a capped job's exit status.
The package's pipeline.toml supplies module names, threads, memory in GiB and
timeouts in seconds. Campaign files are resolved through the checkout helper.
A GPU launch requires a successful device query; --force only overrides busy
measurements. --dry-run prints the command without launching the stage.

    python -m grteclyn_wrapper.optimisation.commands.pipeline --help
"""

from __future__ import annotations

import argparse
from importlib.resources import files
import subprocess
import sys
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib

def repo_root():
    """Resolve a checkout only for operations that need campaign files."""
    from grteclyn_wrapper.core.config import resolve_repo_root
    return resolve_repo_root()


def load():
    cfg = tomllib.loads(files("grteclyn_wrapper.optimisation").joinpath("pipeline.toml").read_text())
    return cfg, {s["name"]: s for s in cfg.get("stage", [])}


def job_state(runner_cfg, name):
    d = repo_root() / "runs" / "capped_jobs" / name
    if not d.is_dir():
        return "-"
    out = subprocess.run(
        ["bash", str(repo_root() / runner_cfg), "status", name],
        capture_output=True, text=True).stdout.strip()
    return out.split()[1] if out else "?"


def cmd_plan(cfg):
    status = (repo_root() / cfg["campaign"]["status"]).read_text().splitlines()
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
        sys.exit(f"pipeline: no stage '{name}' (see: python -m grteclyn_wrapper.optimisation.commands.pipeline list)")
    s = stages[name]
    d = cfg["defaults"]
    mem = s.get("gpu_mem_gb" if gpu is not None else "mem_gb",
                d["gpu_mem_gb" if gpu is not None else "mem_gb"])
    cmd = ["bash", str(repo_root() / cfg["campaign"]["runner"]), "start", s["name"],
           "--threads", str(s.get("threads", d["threads"])),
           "--mem", str(mem),
           "--timeout", str(s.get("timeout_s", d["timeout_s"]))]
    if gpu is not None:
        cmd.append("--gpu")
    cmd += ["--", str(repo_root() / cfg["campaign"]["python"]),
            "-m", s["module"], *s["args"]]
    if gpu is not None:
        cmd += ["--gpu", str(gpu)]
        try:
            query = subprocess.run(
                ["nvidia-smi", "--query-gpu=index,memory.used,utilization.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True)
        except OSError as err:
            sys.exit(f"pipeline: cannot query GPU state: {err}")
        if query.returncode != 0:
            sys.exit("pipeline: GPU state query failed")
        try:
            cards = {}
            for row in query.stdout.strip().splitlines():
                idx, used_mb, util = (int(v) for v in row.split(","))
                if idx < 0 or used_mb < 0 or not 0 <= util <= 100 or idx in cards:
                    raise ValueError("invalid GPU measurements")
                cards[idx] = (used_mb, util)
        except ValueError:
            sys.exit("pipeline: malformed GPU state query")
        if gpu not in cards:
            sys.exit(f"pipeline: card {gpu} was not found in GPU state query")
        print(query.stdout.strip())
        used_mb, util = cards[gpu]
        if (used_mb > 5000 or util > 5) and not force:
            sys.exit(f"pipeline: card {gpu} is busy ({used_mb} MiB, "
                     f"{util}% util); pick another or --force")
    print(" ".join(cmd))
    if dry:
        return 0
    return subprocess.run(cmd, cwd=repo_root()).returncode


def passthrough(cfg, verb, rest):
    return subprocess.run(
        ["bash", str(repo_root() / cfg["campaign"]["runner"]), verb, *rest],
        cwd=repo_root()).returncode


def main(argv: list[str] | None = None) -> int:
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
    args = ap.parse_args(argv)

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
