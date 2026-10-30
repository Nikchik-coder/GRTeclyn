#!/usr/bin/env python
"""Bounded stationary trials: richer potentials, matter, shape and asymmetry.

Seed from an optimiser NPZ. All comparisons retain the seed's physical J
and throat radius (shape/asymmetry retain its area instead). No stability
penalty, growth-rate labels or GRTeclyn evolutions. Outputs are diagnostic
JSONL and NPZ files, never evolution-cleared exports.
"""
from __future__ import annotations

import argparse
import gc
import json
from pathlib import Path
import subprocess
import time

import numpy as np

from grteclyn_wrapper.optimisation.solver.device import select_device


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("seed")
    ap.add_argument("--stages", default="potential,cloud,winding,shape,asymmetry")
    ap.add_argument("--grid", default="150x30")
    ap.add_argument("--fine-grid", default="180x36")
    ap.add_argument("--degree", type=int, default=6)
    ap.add_argument("--indices", default="1,2,3,4,5,6")
    ap.add_argument("--shape-step", type=float, default=.25,
                    help="multiplicative control perturbation exp(+/- step)")
    ap.add_argument("--amplitudes", default="0.005,0.02")
    ap.add_argument("--matter-mass", type=float, default=.3)
    ap.add_argument("--quartic", type=float, default=0.)
    ap.add_argument("--gamma-offsets", default="-0.1,0.1")
    ap.add_argument("--gpu", type=int)
    ap.add_argument("--jac-chunk", type=int, default=512)
    ap.add_argument("--out", required=True, help="new output directory; refuses overwrite")
    args = ap.parse_args()
    stages = args.stages.split(",")
    if set(stages)-{"potential", "cloud", "winding", "shape", "asymmetry"}:
        ap.error("unknown stage")
    if args.matter_mass <= 0 or args.degree < 3 or args.shape_step <= 0:
        ap.error("positive matter mass/shape step and degree >= 3 required")
    indices = [int(v) for v in args.indices.split(",")]
    if any(i < 1 or i > args.degree for i in indices):
        ap.error("indices must be between 1 and degree")
    amps = [float(v) for v in args.amplitudes.split(",")]
    if any(a <= 0 for a in amps):
        ap.error("cloud amplitudes must be positive")
    nx, ny = map(int, args.grid.split("x"))
    fnx, fny = map(int, args.fine_grid.split("x"))
    if fnx <= nx or fny <= ny:
        ap.error("fine grid must refine both directions")
    select_device(args.gpu, args.jac_chunk)
    from grteclyn_wrapper.optimisation.exploration import (
        bound_mode, load_seed, physical_throat, save_trial, solve_trial)
    from grteclyn_wrapper.optimisation.potentials import BernsteinKinkPotential
    import jax

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    state, meta = load_seed(args.seed)
    config = dict(m=meta["m"], q=meta["q"], gamma=meta["gamma"], J=meta["J"])
    controls = BernsteinKinkPotential.elevate_power_shape(config["q"], args.degree)
    th = physical_throat(state)  # saved radius metadata may be in grid units
    pins = {"R_e": ("R_e", th["R_e"]), "area": ("area", th["area_throat"])}
    d2 = (state["psim"]*state["sigma"]/np.pi)**2
    manifest = dict(arguments=vars(args), physical_throat=th, config=config,
                    commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                    stability="not_assessed", constraints_gate=1e-8,
                    comparison="phantom-only VIQ at matched physical size and J")
    (out/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    rows = []

    def record(row):
        rows.append(row)
        line = json.dumps(row, allow_nan=False)
        with (out/"results.jsonl").open("a") as f:
            f.write(line+"\n")
        print(line, flush=True)

    def run(label, initial, cfg, pin_kind, grid, mode=None):
        t0 = time.monotonic()
        head = dict(label=label, config=cfg, pin=list(pins[pin_kind]))
        try:
            solved, row = solve_trial(initial, cfg, *grid, pins[pin_kind], d2, mode=mode)
            row.update(head, seconds=time.monotonic()-t0)
            save_trial(out/(label+".npz"), solved, cfg, row, pins[pin_kind])
            record(row)
            return solved, row
        except Exception as err:
            record(dict(head, verdict="FAILED", error=str(err), seconds=time.monotonic()-t0))
            return None, None
        finally:
            gc.collect()
            jax.clear_caches()

    baselines, fine_bases = {}, {}
    for stage in stages:
        pin_kind = "area" if stage in ("shape", "asymmetry") else "R_e"
        if pin_kind not in baselines:
            baselines[pin_kind] = run("baseline_"+pin_kind, state, config, pin_kind, (nx, ny))
        base, brow = baselines[pin_kind]
        if base is None:
            record(dict(label=stage, verdict="BLOCKED", error="baseline Newton failed"))
            continue
        trials = []
        mode = None
        if stage in ("potential", "shape"):
            for i in (indices if stage == "potential" else indices[:1]):
                for sign in (-1, 1):
                    cc = list(controls)
                    cc[i] *= np.exp(sign*args.shape_step)
                    trials.append((f"{stage}_b{i}_{'minus' if sign<0 else 'plus'}",
                                   dict(config, controls=cc)))
        elif stage == "asymmetry":
            for i, offset in enumerate(map(float, args.gamma_offsets.split(","))):
                trials.append((f"asymmetry_{i}", dict(config, gamma=config["gamma"]+offset)))
        else:
            matter_cfg = dict(config, matter=stage, matter_mass=args.matter_mass,
                              quartic=args.quartic, winding_k=1)
            try:
                mode = bound_mode(base, matter_cfg, pins[pin_kind])
                record(dict(label=stage+"_seed", verdict="BOUND_MODE",
                            frequency=mode["frequency"], mode_residual=mode["mode_residual"],
                            mode_tail=mode["mode_tail"]))
            except Exception as err:
                record(dict(label=stage+"_seed", verdict="NO_BOUND_MODE", error=str(err)))
                continue
            trials = [(f"{stage}_a{i}", dict(matter_cfg, amplitude=a)) for i,a in enumerate(amps)]
        outcomes = []
        for label, cfg in trials:
            solved, row = run(label, base, cfg, pin_kind, (nx, ny), mode)
            if solved is not None:
                outcomes.append((label, cfg, solved, row))
        score = "X_A" if pin_kind == "area" else "X"
        if not outcomes:
            continue
        label, cfg, solved, row = min(outcomes, key=lambda x:x[3][score])
        # Refine the best trial even if the coarse constraints did not pass.
        # A low coarse value alone is never a confirmed improvement.
        if pin_kind not in fine_bases:
            fine_bases[pin_kind] = run("baseline_"+pin_kind+"_fine", base, config,
                                       pin_kind, (fnx, fny))
        fbase, fbrow = fine_bases[pin_kind]
        if fbase is None:
            continue
        _, frow = run(label+"_fine", solved, cfg, pin_kind, (fnx, fny),
                      solved if cfg.get("matter") else None)
        if frow:
            coarse_gain = row[score]-brow[score]
            fine_gain = frow[score]-fbrow[score]
            drift = abs(frow[score]-row[score])+abs(fbrow[score]-brow[score])
            confirmed = (all(r["verdict"]=="PASS" for r in (brow, row, fbrow, frow))
                         and fine_gain < -max(5*drift, 1e-6) and coarse_gain < 0)
            record(dict(label=stage+"_comparison", verdict="GAIN_CONFIRMED" if confirmed else "UNCONFIRMED",
                        score=score, coarse_gain=coarse_gain, fine_gain=fine_gain,
                        grid_drift=drift, fractional_gain=fine_gain/fbrow[score]))
    print(f"Completed {len(rows)} records in {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
