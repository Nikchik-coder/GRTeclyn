#!/usr/bin/env python3
"""run_manifest.json: what a run IS, written by the launcher, not by hand.

    run_manifest.py start  --run-dir DIR --name NAME --template T --exe BIN \
                           --gpu ID [--preflight JSON] [--restart CHK] [--what TEXT]
    run_manifest.py finish --run-dir DIR --status N
    run_manifest.py backfill --run-dir DIR [--exe BIN] [--launch-log LOG]

WHY.  Until 2026-09-24 a run's identity was its NAME plus a prose line in
results/merger/runs_registry.tsv, and nothing checked either against what ran:
four arms named q1e2 ran without their quadrupole, two arms described as
"scalar-damped" ran with damping 0.  The manifest records the facts at launch --
the exact params, the binary and the commit it carries, the source commit of
the launcher, the node and card, the preflight verdict and the t = 0
diagnostics -- and the run's end state at exit.  results/merger/analysis/
run_index.py turns the packed manifests into runs_index.tsv and checks every
name against its params.

`backfill` reconstructs a manifest for a run launched before this existed, from
its params.txt, parameters_and_version.txt, launcher log and streams; it is
marked "reconstructed": true and says what it could not recover.

Paths are stored relative to the repo; the node is stored as its label from
runs/wormhole_merger/NODES.local.md ("the first GPU node"), never its hostname,
because the pack is committed.  Python 3.9+, standard library only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import socket
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[3]
RUNS = REPO / "runs" / "wormhole_merger"
BINARIES_TSV = REPO / "results" / "merger" / "binaries.tsv"
NODES_MD = RUNS / "NODES.local.md"
sys.path.insert(0, str(HERE))
from preflight import parse_params, static_check, t0_rows  # noqa: E402

# Launcher knobs that rewrite the cloned params (run_single.sh, "Overrides").
OVERRIDE_KNOBS = ("WHM_BARE_MASS", "WHM_SIGMA", "WHM_LAPSE_TYPE", "WHM_TAGGING_TYPE",
                  "WHM_TAGGING_L", "WHM_MAX_LEVEL", "WHM_RESTART", "WHM_KEEP_LAST",
                  "WHM_CONSUME", "WHM_CONSUME_ARGS", "WHM_PREFLIGHT", "WHM_RANKS")


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rel(path: str | os.PathLike | None) -> str | None:
    if not path:
        return None
    p = pathlib.Path(path).resolve()
    try:
        return str(p.relative_to(REPO.resolve()))
    except ValueError:
        return p.name              # outside the repo: keep the name only


def sha256(path: pathlib.Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def node_label() -> str:
    """This machine's label from NODES.local.md, else an opaque tag."""
    host = socket.gethostname()
    if NODES_MD.exists():
        for line in NODES_MD.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*-\s*(the \w+ GPU node)\s*=\s*(\S+)", line)
            if m and m.group(2) == host:
                return m.group(1)
    return "node-" + hashlib.sha1(host.encode()).hexdigest()[:8]


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True,
                              check=False).stdout.strip()
    except OSError:
        return ""


def binary_row(name: str, sha: str | None) -> dict | None:
    """The binaries.tsv row for this binary, by file name or by sha256 prefix."""
    if not BINARIES_TSV.exists():
        return None
    cols = None
    for line in BINARIES_TSV.read_text(encoding="utf-8").splitlines():
        if line.startswith("#file"):
            cols = line[1:].split("\t")
            continue
        if not line.strip() or line.startswith("#") or cols is None:
            continue
        vals = line.split("\t")
        row = dict(zip(cols, vals))
        if row.get("file") == name or (sha and row.get("sha256_16") == sha[:16]):
            return row
    return None


def binary_block(exe: pathlib.Path, version: str | None) -> dict:
    sha = sha256(exe)
    return {"file": exe.name, "path": rel(exe), "sha256": sha,
            "grteclyn_version": version or "unstamped",
            "binaries_tsv": binary_row(exe.name, sha)}


def last_row(path: pathlib.Path) -> list[float] | None:
    if not path.exists():
        return None
    last = None
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            last = line
    try:
        return [float(v) for v in last.split()] if last else None
    except ValueError:
        return None


def write(run_dir: pathlib.Path, manifest: dict) -> None:
    out = run_dir / "run_manifest.json"
    tmp = out.with_suffix(".json.part")
    tmp.write_text(json.dumps(manifest, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    tmp.replace(out)


# ---------------------------------------------------------------- commands
def cmd_start(a) -> int:
    run_dir = pathlib.Path(a.run_dir).resolve()
    params_path = run_dir / "params.txt"
    params = parse_params(params_path.read_text(encoding="utf-8"))
    pf = {}
    if a.preflight and pathlib.Path(a.preflight).exists():
        pf = json.loads(pathlib.Path(a.preflight).read_text(encoding="utf-8"))
    exe = pathlib.Path(a.exe).resolve()
    dirty = git("status", "--porcelain", "--untracked-files=no", "--", "Source", "Examples",
                "Tools/GNUMake", "grteclyn-wrapper/scripts")
    manifest = {
        "schema": 1,
        "run": a.name,
        "reconstructed": False,
        "launched_utc": now(),
        "what": a.what or None,
        "template": rel(a.template), "template_sha256": sha256(pathlib.Path(a.template)),
        "params_sha256": sha256(params_path),
        "params": params,
        "overrides": {k: os.environ[k] for k in OVERRIDE_KNOBS if os.environ.get(k)},
        "restart_from": rel(a.restart) if a.restart else None,
        "binary": binary_block(exe, pf.get("grteclyn_version")),
        "launcher": {"commit": git("rev-parse", "--short=8", "HEAD"), "dirty": bool(dirty)},
        "node": node_label(), "gpu": a.gpu,
        "paths": {"run_dir": rel(run_dir), "scratch": "$GRTECLYN_SCRATCH/" + run_dir.name},
        "preflight": pf or {"verdict": "none"},
        "t0": (pf.get("t0") or {}).get("constraint_norms.dat"),
        "seed": (pf.get("seed") or {}).get("verdict"),
        "status": "running",
    }
    write(run_dir, manifest)
    print(f"[manifest] {rel(run_dir / 'run_manifest.json')}: binary {exe.name} "
          f"({manifest['binary']['grteclyn_version']}), preflight {manifest['preflight'].get('verdict')}")
    return 0


def cmd_finish(a) -> int:
    run_dir = pathlib.Path(a.run_dir).resolve()
    path = run_dir / "run_manifest.json"
    if not path.exists():
        print(f"[manifest] no {path.name} to finish in {rel(run_dir)}", file=sys.stderr)
        return 1
    m = json.loads(path.read_text(encoding="utf-8"))
    row = last_row(run_dir / "data" / "constraint_norms.dat")
    m.update({"status": "finished" if a.status == 0 else "failed", "exit_status": a.status,
              "finished_utc": now(), "t_end": row[0] if row else None})
    log = run_dir / "run.log"
    if log.exists():
        tail = log.read_bytes()[-200_000:].decode("utf-8", errors="replace")
        nan = re.findall(r"NaN diagnostic: .*", tail)
        if nan:
            m["death"] = nan[-1].strip()
    write(run_dir, m)
    print(f"[manifest] finished: status {m['status']} (exit {a.status}), t_end {m['t_end']}")
    return 0


def cmd_backfill(a) -> int:
    """Reconstruct a manifest for a run launched before 2026-09-24."""
    run_dir = pathlib.Path(a.run_dir).resolve()
    out = run_dir / "run_manifest.json"
    if out.exists() and not json.loads(out.read_text(encoding="utf-8")).get("reconstructed"):
        print(f"[manifest] {rel(out)} was written at launch -- left alone")
        return 0
    params_path = run_dir / "params.txt"
    if not params_path.exists():
        print(f"[manifest] {rel(run_dir)}: no params.txt -- nothing to reconstruct", file=sys.stderr)
        return 1
    params = parse_params(params_path.read_text(encoding="utf-8"))
    missing: list[str] = []
    # The binary: the launcher log names it ("[launch] binary : ..." / "[whm] binary : ...").
    exe_path = pathlib.Path(a.exe) if a.exe else None
    if exe_path is None and a.launch_log and pathlib.Path(a.launch_log).exists():
        m = re.search(r"\[(?:launch|whm)\] binary\s*:\s*(\S+)",
                      pathlib.Path(a.launch_log).read_text(encoding="utf-8", errors="replace"))
        if m:
            exe_path = pathlib.Path(m.group(1))
            if not exe_path.is_absolute():
                exe_path = REPO / exe_path
    version = None
    pv = run_dir / "parameters_and_version.txt"
    if pv.exists():
        vm = re.search(r"Using GRTeclyn version \((.*)\)", pv.read_text(encoding="utf-8", errors="replace"))
        version = vm.group(1) if vm and vm.group(1) != "unknown" else None
    binary = None
    if exe_path is not None:
        frozen = (RUNS / "bin") in exe_path.parents
        binary = {"file": exe_path.name, "path": rel(exe_path),
                  "grteclyn_version": version or "unstamped", "frozen_copy": frozen}
        if frozen and exe_path.is_file():
            binary["sha256"] = sha256(exe_path)
            binary["binaries_tsv"] = binary_row(exe_path.name, binary["sha256"])
            binary["absent_keys"] = static_check(exe_path, list(params))
        elif frozen:
            binary["binaries_tsv"] = binary_row(exe_path.name, None)
            binary["absent_keys"] = None
            missing.append("binary file deleted: which keys it read is unknown")
        else:
            # The example's live build product: rebuilt many times since, so the
            # file on disk now is not the one that ran.
            binary["absent_keys"] = None
            missing.append("binary was the example's live build product (rebuilt since): "
                           "which keys it read is unknown")
    else:
        missing.append("binary: no launcher log names it")
    t0 = t0_rows(run_dir / "data").get("constraint_norms.dat")
    row = last_row(run_dir / "data" / "constraint_norms.dat")
    manifest = {
        "schema": 1, "run": run_dir.name, "reconstructed": True, "reconstructed_utc": now(),
        "unrecoverable": missing,
        "params_sha256": sha256(params_path), "params": params,
        "restart_from": params.get("amr.restart", "").strip('"') or None,
        "binary": binary,
        "preflight": {"verdict": "none (launched before 2026-09-24)"},
        "t0": t0, "t_end": row[0] if row else None,
        "status": "unknown",
    }
    if manifest["restart_from"]:
        manifest["restart_from"] = pathlib.Path(manifest["restart_from"]).name
    write(run_dir, manifest)
    absent = (binary or {}).get("absent_keys")
    print(f"[manifest] {run_dir.name}: reconstructed; binary "
          f"{(binary or {}).get('file', '?')}; keys absent from it: {absent if absent is not None else 'unknown'}")
    return 0


SKIP_DIRS = {"00_archive", "90_probes", "templates_scan", "bin", "logs"}


def cmd_backfill_all(a) -> int:
    """backfill every run in the run tree that has params.txt and no launch-time
    manifest; the binary comes from logs/<run>.log or the run's launch_banner.txt."""
    done = 0
    for params_txt in sorted(RUNS.glob("**/params.txt")):
        run_dir = params_txt.parent
        parts = run_dir.relative_to(RUNS).parts
        if not parts or parts[0] in SKIP_DIRS or len(parts) > 3:
            continue
        log = RUNS / "logs" / f"{run_dir.name}.log"
        if not log.exists():
            log = run_dir / "launch_banner.txt"
        sub = argparse.Namespace(run_dir=str(run_dir), exe=None,
                                 launch_log=str(log) if log.exists() else None)
        done += cmd_backfill(sub) == 0
    print(f"[manifest] backfill-all: {done} run(s) handled")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    # run_single.sh passes the revealing values through the environment: the
    # process table is public and shows arguments, not environments.
    env = os.environ.get
    s.add_argument("--run-dir", required=True)
    s.add_argument("--name", default=env("WHM_MANIFEST_NAME"))
    s.add_argument("--template", default=env("WHM_MANIFEST_TEMPLATE"))
    s.add_argument("--exe", default=env("WHM_MANIFEST_EXE"))
    s.add_argument("--gpu", default=env("WHM_GPU"))
    s.add_argument("--preflight")
    s.add_argument("--restart", default=env("WHM_RESTART"))
    s.add_argument("--what", default=env("WHM_WHAT"))
    f = sub.add_parser("finish")
    f.add_argument("--run-dir", required=True)
    f.add_argument("--status", type=int, required=True)
    b = sub.add_parser("backfill")
    b.add_argument("--run-dir", required=True)
    b.add_argument("--exe")
    b.add_argument("--launch-log")
    sub.add_parser("backfill-all")
    a = ap.parse_args(argv)
    if a.cmd == "start":
        absent = [k for k in ("name", "template", "exe", "gpu") if not getattr(a, k)]
        if absent:
            ap.error("start needs " + ", ".join(f"--{k}" for k in absent))
    return {"start": cmd_start, "finish": cmd_finish, "backfill": cmd_backfill,
            "backfill-all": cmd_backfill_all}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
