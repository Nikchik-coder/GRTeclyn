#!/usr/bin/env python3
"""Pre-launch check: does the binary read every key, and does the seed take?

Run by run_single.sh once the params are cloned and every override applied,
before the run is registered or started.  Standalone:

    preflight.py --exe BIN --params params.txt --gpu 1 --workdir DIR \
                 [--mode full|static] [--restart] [--json OUT] [--argv0 NAME]

WHY.  AMReX's ParmParse ignores a key that nothing reads.  On 2026-09-23 the
campaign pin turned out to predate the quadrupole seed, so four arms launched
with wormhole_seed_l2_amplitude_A = 0.01 ran without a quadrupole and nothing
said so for a week (research/merger/GPU_PLAN.md, 2026-09-23 evening).  This
turns that into a refusal at launch, in seconds.

WHAT IT CHECKS
  0. intent (no GPU, instant).  Settings that contradict each other, so the run
     would silently not do what its params say.  Refused:
       - checkpoint_interval > 0 or checkpoint_keep > 0 with
         amr.checkpoint_files_output = 0: AMReX's checkPoint() returns at once
         when output is off, so NO checkpoint is ever written.  This is how
         single_eps_p1e2_t250 died of a NaN at t = 145.8 (2026-09-24, 8 GPU-h
         in) with nothing to restart from, although its template asked for a
         rolling ladder of three; 19 templates in templates_scan/ carry the
         same contradiction.
       - plot_interval > 0 with amr.plot_files_output = 0 (no plotfiles: no
         frames, no consumer extractions).
     Warned: a run that writes no checkpoints at all cannot be restarted.
     Also the plotfile consumer's flags ($WHM_CONSUME_ARGS, as run_single.sh
     gets them; --consume-args standalone) against what the plotfiles carry:
       - refused: --areal-full-metric (the areal radius from the full metric,
         r (h22 h33)^(1/4)/sqrt(chi); opt-in since 2026-09-25) with h22, h33
         or chi missing from amr.plot_vars, or without --areal-radius.
       - warned: --areal-radius alone -- r/sqrt(chi), exact at t = 0 and a
         lower bound once the Gamma-driver shift has moved the grid (h22 =
         1.45 at the F1b neck at t = 90: 10.08 read for a true 12.17).
  1. static (no GPU, seconds).  Every key of the params file must appear as a
     string inside the binary: a binary that does not contain a key's name
     cannot read it.  Advisory in full mode (a key can be present but unread
     on this code path); decisive in static mode, less the dead keys that
     preflight_allow.txt names (no code reads them, so no binary contains them).
  2. unread keys (GPU, one start-up).  The binary starts on a copy of the params
     with max_steps = 0, all output off, amrex.abort_on_unused_inputs = 1 and
     amrex.verbose = 1.  It builds the whole initial hierarchy, writes its t = 0
     diagnostics (BinaryWormholeLevel::specific_post_init) and at exit AMReX
     lists every key nothing read.  Any such key refuses the launch, unless it
     is in preflight_allow.txt (keys read only when a plotfile is written, which
     the probe skips, and dead keys no code reads -- each entry says why).
  3. seed effect (GPU, a second start-up; only when a seed amplitude is non-zero
     and the run is not a restart).  The same start-up with every seed amplitude
     set to 0.  If no t = 0 diagnostic differs by more than 1e-10 (relative),
     the seed did nothing and the launch is refused.  This is the H(t = 0)
     comparison that exposed the 2026-09-23 trap, made automatic.

Exit status: 0 pass, 1 refused, 2 could not run (a failed start-up, a timeout).
A report goes to --json; run_single.sh folds it into run_manifest.json.

Python 3.9+, standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pathlib
import re
import shlex
import shutil
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ALLOW_FILE = HERE / "preflight_allow.txt"
SEED_KEY_RE = re.compile(r"^wormhole_seed(?:_l2)?_amplitude_[AB]$")
KEY_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_.]*)\s*=(.*)$")
UNUSED_RE = re.compile(r"\[TOP\]::([A-Za-z_][A-Za-z0-9_.]*)\(nvals")
VERSION_RE = re.compile(r"Using GRTeclyn version \((.*)\)")
REL_TOL = 1e-10


# ---------------------------------------------------------------- params file
def strip_comment(line: str) -> str:
    """Drop a # comment that is not inside double quotes."""
    out, quoted = [], False
    for ch in line:
        if ch == '"':
            quoted = not quoted
        if ch == "#" and not quoted:
            break
        out.append(ch)
    return "".join(out)


def parse_params(text: str) -> dict[str, str]:
    """key -> raw value text (last definition wins, as in ParmParse queries)."""
    params: dict[str, str] = {}
    for line in text.splitlines():
        m = KEY_RE.match(strip_comment(line))
        if m:
            params[m.group(1)] = m.group(2).strip()
    return params


def rewrite_params(text: str, overrides: dict[str, str]) -> str:
    """Set each override key exactly once: replace its definition line(s) in
    place, append the ones the file does not define."""
    seen: set[str] = set()
    out = []
    for line in text.splitlines():
        m = KEY_RE.match(strip_comment(line))
        if m and m.group(1) in overrides:
            key = m.group(1)
            if key in seen:
                continue                      # drop duplicate definitions
            seen.add(key)
            out.append(f"{key} = {overrides[key]}")
        else:
            out.append(line)
    missing = [k for k in overrides if k not in seen]
    if missing:
        out.append("")
        out.append("# ---- set by preflight.py ----")
        out.extend(f"{k} = {overrides[k]}" for k in missing)
    return "\n".join(out) + "\n"


def as_float(raw: str) -> float | None:
    try:
        return float(raw.split()[0].strip('"'))
    except (ValueError, IndexError):
        return None


# ---------------------------------------------------------------- 0. intent
def intent_check(params: dict[str, str]) -> tuple[list[str], list[str]]:
    """(errors, warnings) for settings that contradict each other.  Defaults as
    in the code: GRTeclyn checkpoint_interval 1, plot_interval 0; AMReX
    checkpoint_files_output and plot_files_output 1."""
    def num(key: str, default: float) -> float:
        v = as_float(params[key]) if key in params else None
        return default if v is None else v

    errors, warnings = [], []
    ci, keep = num("checkpoint_interval", 1), num("checkpoint_keep", 0)
    cout = num("amr.checkpoint_files_output", 1)
    asked = [f"{k} = {params[k].split()[0]}" for k, v in (("checkpoint_interval", ci), ("checkpoint_keep", keep))
             if k in params and v > 0]
    if cout == 0 and asked:
        errors.append(f"checkpoints requested ({', '.join(asked)}) but amr.checkpoint_files_output = 0: "
                      "AMReX writes NO checkpoint when output is off.  Set amr.checkpoint_files_output = 1, "
                      "or checkpoint_interval = -1 and drop checkpoint_keep to say 'no checkpoints'")
    pi, pout = num("plot_interval", 0), num("amr.plot_files_output", 1)
    if pout == 0 and pi > 0:
        errors.append(f"plot_interval = {params['plot_interval'].split()[0]} but amr.plot_files_output = 0: "
                      "no plotfile will be written (no frames, no consumer extractions)")
    if cout == 0 or ci <= 0:
        warnings.append("this run writes no checkpoints: if it dies, it cannot be restarted")
    return errors, warnings


def consumer_check(params: dict[str, str], consume_args: str, consume_on: bool
                   ) -> tuple[list[str], list[str], dict]:
    """(errors, warnings, summary) for what the plotfile consumer is asked to
    extract against what the plotfiles will carry.  The areal radius is the one
    extraction checked: its full-metric form is opt-in and needs h22 and h33."""
    try:
        toks = shlex.split(consume_args or "")
    except ValueError:
        toks = (consume_args or "").split()
    summary = {"consume": consume_on, "areal_radius": "off"}
    errors, warnings = [], []
    if not consume_on:
        return errors, warnings, summary
    areal, full = "--areal-radius" in toks, "--areal-full-metric" in toks
    if full and not areal:
        errors.append("--areal-full-metric without --areal-radius: the consumer extracts no areal radius at all")
    if not areal:
        return errors, warnings, summary
    summary["areal_radius"] = ("full metric, r (h22 h33)^(1/4)/sqrt(chi)" if full
                               else "flat conformal metric, r/sqrt(chi)")
    need = ["chi", "h22", "h33"] if full else ["chi"]
    if "amr.plot_vars" in params:
        have = set(params["amr.plot_vars"].split())
        lacking = [v for v in need if v not in have]
        if lacking:
            errors.append(f"the consumer's areal radius ({'--areal-full-metric' if full else '--areal-radius'}) "
                          f"needs {', '.join(lacking)} in amr.plot_vars, which the plotfiles will not carry")
    else:
        warnings.append(f"amr.plot_vars not set: the areal radius's fields ({', '.join(need)}) are not checked")
    if not full:
        warnings.append("areal radius is r/sqrt(chi) (flat conformal metric): exact at t = 0, a lower bound once "
                        "the Gamma-driver shift has moved the grid; --areal-full-metric uses h22, h33")
    return errors, warnings, summary


# ---------------------------------------------------------------- 1. static
_BLOBS: dict[pathlib.Path, bytes] = {}


def static_check(exe: pathlib.Path, keys: list[str]) -> list[str]:
    """Keys whose name (or, for a prefixed key, its last component) does not
    occur anywhere in the binary.  ParmParse("amr").query("plot_file") stores
    "plot_file", so amr.plot_file is looked up by its last component."""
    exe = pathlib.Path(exe).resolve()
    if exe not in _BLOBS:                 # backfill checks ~150 runs against 4 binaries
        _BLOBS[exe] = exe.read_bytes()
    blob = _BLOBS[exe]
    missing = []
    for key in keys:
        candidates = {key.encode(), key.rsplit(".", 1)[-1].encode()}
        if not any(c in blob for c in candidates):
            missing.append(key)
    return missing


# ---------------------------------------------------------------- 2./3. probes
def load_allow() -> dict[str, tuple[tuple[str, str] | None, str]]:
    """key -> (condition, why) from preflight_allow.txt.  A line is `key  # why`, or
    `key when other = value  # why` for a key read only inside a feature the params
    can switch off: it is then allowed only while the params hold other = value.  An
    absent `other` counts as that value, so a condition must name the code default."""
    allow: dict[str, tuple[tuple[str, str] | None, str]] = {}
    if ALLOW_FILE.exists():
        for line in ALLOW_FILE.read_text(encoding="utf-8").splitlines():
            body = line.split("#", 1)
            head, _, cond = body[0].partition(" when ")
            key = head.strip()
            if not key:
                continue
            other, _, value = cond.partition("=")
            allow[key] = (((other.strip(), value.strip()) if cond.strip() else None),
                          body[1].strip() if len(body) > 1 else "")
    return allow


def _flag(v: str) -> str:
    v = v.strip().strip('"').lower()
    return {"false": "0", "true": "1"}.get(v, v)


def is_allowed(key: str, allow: dict, params: dict[str, str]) -> bool:
    """Whether an unread (or absent) key is covered by preflight_allow.txt here."""
    if key not in allow:
        return False
    cond = allow[key][0]
    if cond is None:
        return True
    other, value = cond
    return _flag(params.get(other, value)) == _flag(value)


def t0_rows(data_dir: pathlib.Path) -> dict[str, dict[str, float]]:
    """First data row of every .dat stream the start-up wrote, by column name."""
    rows: dict[str, dict[str, float]] = {}
    for f in sorted(data_dir.rglob("*.dat")):
        names: list[str] = []
        with f.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if line.startswith("#"):
                    names = line.lstrip("#").split()
                    continue
                vals = line.split()
                if not vals:
                    continue
                try:
                    nums = [float(v) for v in vals]
                except ValueError:
                    break
                if len(names) != len(nums):
                    names = [f"c{i}" for i in range(len(nums))]
                rows[f.name] = dict(zip(names, nums))
                break
    return rows


def probe(exe_run: pathlib.Path, argv0: str, params_text: str, overrides: dict[str, str],
          workdir: pathlib.Path, gpu: str, timeout: float) -> dict:
    """One 0-step start-up in <workdir>; returns what it read and wrote."""
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True)
    ov = dict(overrides)
    ov.update({
        "output_path": f'"{workdir}"',
        "amr.plot_file": f'"{workdir}/plt"',
        "amr.check_file": f'"{workdir}/chk"',
    })
    (workdir / "params.txt").write_text(rewrite_params(params_text, ov), encoding="utf-8")
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(gpu))
    log = workdir / "probe.log"
    t0 = time.time()
    status = "ok"
    with log.open("w", encoding="utf-8") as fh:
        try:
            proc = subprocess.run([argv0, "params.txt"], executable=str(exe_run), cwd=workdir,
                                  env=env, stdout=fh, stderr=subprocess.STDOUT,
                                  stdin=subprocess.DEVNULL, timeout=timeout, check=False)
            code = proc.returncode
        except subprocess.TimeoutExpired:
            code, status = None, "timeout"
    text = log.read_text(encoding="utf-8", errors="replace")
    unused = sorted(set(UNUSED_RE.findall(text)))
    version = None
    pv = workdir / "parameters_and_version.txt"
    if pv.exists():
        m = VERSION_RE.search(pv.read_text(encoding="utf-8", errors="replace"))
        version = m.group(1) if m else None
    rows = t0_rows(workdir)
    if status == "ok" and code != 0 and not unused:
        status = "crashed"
    return {"status": status, "exit_code": code, "unused": unused, "version": version,
            "t0": rows, "seconds": round(time.time() - t0, 1),
            "log_tail": text.splitlines()[-25:] if status != "ok" else []}


def max_rel_diff(a: dict[str, dict[str, float]], b: dict[str, dict[str, float]]) -> tuple[float, str]:
    worst, where = 0.0, ""
    for fname in sorted(set(a) & set(b)):
        for col in sorted(set(a[fname]) & set(b[fname])):
            if col.lower() in ("time", "t", "c0"):
                continue
            x, y = a[fname][col], b[fname][col]
            if math.isnan(x) or math.isnan(y):
                continue
            scale = max(abs(x), abs(y), 1e-300)
            d = abs(x - y) / scale if (x or y) else 0.0
            if d > worst:
                worst, where = d, f"{fname}:{col}"
    return worst, where


# ---------------------------------------------------------------- driver
def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--exe", required=True, help="the binary the run will use")
    ap.add_argument("--exe-run", help="copy actually executed (process-table alias); default --exe")
    ap.add_argument("--exe-name", default=os.environ.get("WHM_EXE_NAME"),
                    help="the binary's real file name for the report (default: --exe's)")
    ap.add_argument("--argv0", default="test", help="process name for the start-ups")
    ap.add_argument("--params", required=True, help="the run's final params file")
    ap.add_argument("--gpu", default="0", help="CUDA device for the start-ups")
    ap.add_argument("--workdir", required=True, help="scratch directory for the start-ups")
    ap.add_argument("--mode", choices=("full", "static"), default="full")
    ap.add_argument("--restart", action="store_true", help="the run restarts from a checkpoint")
    ap.add_argument("--timeout", type=float, default=1800.0, help="seconds per start-up")
    ap.add_argument("--json", help="write the report here")
    ap.add_argument("--keep", action="store_true", help="keep the workdir even on success")
    ap.add_argument("--consume-args", default=os.environ.get("WHM_CONSUME_ARGS", ""),
                    help="the plotfile consumer's flags (default: $WHM_CONSUME_ARGS, as run_single.sh has them)")
    a = ap.parse_args(argv)

    exe = pathlib.Path(a.exe).resolve()
    exe_run = pathlib.Path(a.exe_run or a.exe).resolve()
    params_path = pathlib.Path(a.params).resolve()
    workdir = pathlib.Path(a.workdir).resolve()
    text = params_path.read_text(encoding="utf-8")
    params = parse_params(text)
    report: dict = {
        "schema": 1, "mode": a.mode, "restart": a.restart,
        "exe": a.exe_name or exe.name, "exe_sha256": sha256(exe), "params_sha256": sha256(params_path),
        "verdict": None, "reasons": [],
    }

    def finish(verdict: str, code: int) -> int:
        report["verdict"] = verdict
        if a.json:
            pathlib.Path(a.json).write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
        for r in report["reasons"]:
            print(f"[preflight]   - {r}")
        print(f"[preflight] verdict: {verdict.upper()}")
        return code

    errors, warnings = intent_check(params)
    report["intent"] = {"errors": errors, "warnings": warnings}
    c_err, c_warn, c_sum = consumer_check(params, a.consume_args,
                                          os.environ.get("WHM_CONSUME", "1") != "0")
    report["consumer"] = dict(c_sum, errors=c_err, warnings=c_warn)
    print(f"[preflight] consumer: areal radius {c_sum['areal_radius']}"
          + ("" if c_sum["consume"] else " (no consumer: WHM_CONSUME=0)"))
    errors, warnings = errors + c_err, warnings + c_warn
    for w in warnings:
        print(f"[preflight] WARNING: {w}")
    if errors:
        report["reasons"].extend(errors)
        return finish("refused", 1)

    missing = static_check(exe, list(params))
    allow = load_allow()
    blocking = [k for k in missing if not is_allowed(k, allow, params)]
    report["static"] = {"keys": len(params), "absent_from_binary": missing,
                        "allowed_absent": [k for k in missing if is_allowed(k, allow, params)]}
    print(f"[preflight] static : {len(params)} keys, {len(missing)} absent from {a.exe_name or exe.name}"
          + (f": {', '.join(missing)}" if missing else "")
          + (f" ({len(missing) - len(blocking)} of them dead keys preflight_allow.txt names)"
             if len(blocking) < len(missing) else ""))
    if a.mode == "static":
        if blocking:
            report["reasons"].append(f"keys the binary cannot read: {', '.join(blocking)}")
            return finish("refused", 1)
        return finish("pass", 0)

    probe_ov = {
        "max_steps": "0", "plot_interval": "-1", "checkpoint_interval": "-1",
        "amr.plot_files_output": "0", "amr.checkpoint_files_output": "0",
        "amrex.abort_on_unused_inputs": "1", "amrex.verbose": "1",
    }
    print(f"[preflight] start-up with every key checked (gpu {a.gpu}, 0 steps) ...")
    run = probe(exe_run, a.argv0, text, probe_ov, workdir / "run", a.gpu, a.timeout)
    report["probe"] = {k: run[k] for k in ("status", "exit_code", "unused", "version", "seconds", "log_tail")}
    report["t0"] = run["t0"]
    report["grteclyn_version"] = run["version"]
    unread = [k for k in run["unused"] if not is_allowed(k, allow, params)]
    report["probe"]["allowed_unused"] = [k for k in run["unused"] if is_allowed(k, allow, params)]
    print(f"[preflight] probe  : {run['status']} in {run['seconds']} s; binary version "
          f"({run['version'] or 'not reported'}); {len(run['unused'])} unread key(s)")
    if unread:
        report["reasons"].append(
            "keys the binary did not read (ParmParse would have ignored them): " + ", ".join(unread))
        return finish("refused", 1)
    if run["status"] != "ok":
        report["reasons"].append(f"the start-up did not complete ({run['status']}, exit {run['exit_code']}); "
                                 f"log: {workdir / 'run' / 'probe.log'}")
        for line in run["log_tail"][-8:]:
            print(f"[preflight]   | {line}")
        return finish("error", 2)
    ham = run["t0"].get("constraint_norms.dat", {})
    if ham:
        print("[preflight] t = 0  : " + "  ".join(f"{k} {v:.10e}" for k, v in ham.items() if k != "time"))
    elif not a.restart:
        print("[preflight] WARNING: the start-up wrote no t = 0 diagnostics (calculate_constraint_norms off?)")

    seeds = {k: v for k, v in params.items() if SEED_KEY_RE.match(k) and (as_float(v) or 0.0) != 0.0}
    report["seed"] = {"requested": seeds}
    if seeds and not a.restart and not run["t0"]:
        report["seed"]["verdict"] = "not checked (no t = 0 diagnostics to compare)"
        print("[preflight] WARNING: seed set but no t = 0 diagnostics -- its effect is NOT checked")
    elif seeds and not a.restart:
        ctrl_ov = dict(probe_ov)
        ctrl_ov.update({k: "0.0" for k in params if SEED_KEY_RE.match(k)})
        ctrl_ov["amrex.abort_on_unused_inputs"] = "0"
        print(f"[preflight] seed   : {', '.join(f'{k}={v}' for k, v in seeds.items())} -- "
              "start-up with the seed off, for comparison ...")
        ctrl = probe(exe_run, a.argv0, text, ctrl_ov, workdir / "control", a.gpu, a.timeout)
        if ctrl["status"] != "ok":
            report["reasons"].append(f"the seed-off comparison did not complete ({ctrl['status']})")
            return finish("error", 2)
        diff, where = max_rel_diff(run["t0"], ctrl["t0"])
        report["seed"].update({"control_t0": ctrl["t0"], "max_rel_diff": diff, "at": where,
                               "seconds": ctrl["seconds"]})
        if diff <= REL_TOL:
            report["seed"]["verdict"] = "no effect"
            report["reasons"].append(
                f"the seed changed nothing: every t = 0 diagnostic matches the seed-off start-up "
                f"(max relative difference {diff:.1e}) -- the binary ignores the seed")
            return finish("refused", 1)
        report["seed"]["verdict"] = "took"
        print(f"[preflight] seed   : took (largest t = 0 change {diff:.2e}, relative, in {where})")
    elif seeds:
        report["seed"]["verdict"] = "not checked (restart)"

    if not a.keep:
        shutil.rmtree(workdir, ignore_errors=True)
    return finish("pass", 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
