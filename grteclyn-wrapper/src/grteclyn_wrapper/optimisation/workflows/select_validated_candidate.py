"""Find the first saved candidate that clears independent refinement.

Input: an NPZ glob, optional excluded slots and a candidate-count limit.
Output: an ordered manifest, attempt logs and selected.json on success.
Candidates are ordered by finite X = |VIQ|/R_e, with filename breaking ties.
Each validator runs in a fresh process to release GPU allocations. Selection
requires both a successful exit and handoff.npz; unexpected failures stop the
batch. Numerical clearance is not a physical stability certificate.

    python -m grteclyn_wrapper.optimisation.commands.select_validated_candidate --help
"""
from __future__ import annotations

import glob
import json
from pathlib import Path
import subprocess
import sys

import numpy as np


def run(args, *, error):
    """Execute parsed options; report invalid requests through ``error``."""
    if args.limit < 1:
        error("limit must be positive")
    candidates = []
    for filename in glob.glob(args.pattern):
        with np.load(filename, allow_pickle=False) as z:
            meta = json.loads(str(z["meta"]))
        if meta.get("slot") not in args.skip and np.isfinite(meta["X"]):
            candidates.append((meta["X"], filename, meta))
    candidates.sort(key=lambda entry: (entry[0], entry[1]))
    if not candidates:
        error("no candidates matched")
    args.out.mkdir(parents=True, exist_ok=False)
    selected = candidates[:args.limit]
    manifest = [dict(source=Path(f).name, X=x, slot=m["slot"], J=m["J"],
                     m=m["m"], q=m["q"]) for x, f, m in selected]
    (args.out/"candidates.json").write_text(json.dumps(manifest, indent=2)+"\n")
    for rank, (x, filename, meta) in enumerate(selected, 1):
        dest = args.out/f"{rank:03d}_{meta['slot']}"
        cmd = [sys.executable, "-m",
               "grteclyn_wrapper.optimisation.commands.validate_candidate", filename, "--gpu", str(args.gpu),
               "--out", str(dest)]
        if args.radius is not None:
            cmd += ["--radius", str(args.radius)]
        print(f"CHECK {rank}/{len(selected)} {Path(filename).name} X={x:.12g}", flush=True)
        with (args.out/f"{dest.name}.log").open("w") as log:
            code = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT).returncode
        row = dict(rank=rank, source=Path(filename).name, search_X=x, exit_code=code)
        with (args.out/"attempts.jsonl").open("a") as log:
            log.write(json.dumps(row)+"\n")
        print(json.dumps(row), flush=True)
        if code == 0 and (dest/"handoff.npz").is_file():
            row["handoff"] = str((dest/"handoff.npz").relative_to(args.out))
            (args.out/"selected.json").write_text(json.dumps(row, indent=2)+"\n")
            print(f"SELECTED {dest/'handoff.npz'}", flush=True)
            return 0
        if code < 0 or code not in (1, 2):
            print("Unexpected process failure; stopping the batch", flush=True)
            return 3
    print("No candidate cleared this batch", flush=True)
    return 2
