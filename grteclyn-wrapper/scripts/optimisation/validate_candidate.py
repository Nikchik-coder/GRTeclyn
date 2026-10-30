#!/usr/bin/env python
"""Refine one saved search candidate before a matched evolution.

Physical size is reconstructed from the fields, not old radius metadata.
Only two successive PASS grids with consistent exoticity produce a handoff.
An optional radius change is an exact similarity scaling, including V and J.
"""
from __future__ import annotations

import argparse
import dataclasses
import gc
import json
from pathlib import Path
import time

import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("seed")
    ap.add_argument("--grids", default="150x30,180x36,210x42")
    ap.add_argument("--radius", type=float, help="rescale to this physical R_e before refinement")
    ap.add_argument("--gpu", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    grids = [tuple(map(int, g.split("x"))) for g in args.grids.split(",")]
    if len(grids) < 2 or any(a >= c or b >= d for (a,b),(c,d) in zip(grids,grids[1:])):
        ap.error("need at least two grids, refining both directions")
    if args.radius is not None and args.radius <= 0:
        ap.error("radius must be positive")
    from grteclyn_wrapper.optimisation.solver.device import select_device
    select_device(args.gpu, 512)
    import jax
    from grteclyn_wrapper.optimisation.exploration import (
        FIELDS, load_seed, physical_throat, save_trial, solve_trial,
    )
    from grteclyn_wrapper.optimisation.potentials import PolynomialPotential

    args.out.mkdir(parents=True, exist_ok=False)
    state, meta = load_seed(args.seed)
    radius = physical_throat(state)["R_e"]
    scale = 1.0 if args.radius is None else args.radius/radius
    # Similarity scaling: lengths * scale, J * scale^2, V / scale^2.
    state["sigma"] *= scale
    config = dict(m=meta["m"]/scale, q=meta["q"], gamma=meta["gamma"], J=meta["J"]*scale**2)
    pin = ("R_e", radius*scale)
    d2 = (state["psim"]*state["sigma"]/np.pi)**2
    manifest = dict(source=Path(args.seed).name, grids=grids, config=config,
                    pin=pin, rescale=scale, stability="not_assessed")
    (args.out/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    records = []
    for nx,ny in grids:
        started = time.monotonic()
        print(f"Solving {nx}x{ny}: J={config['J']:.12g}, R_e={pin[1]:.12g}", flush=True)
        state, row = solve_trial(state, config, nx, ny, pin, d2, max_iter=24)
        row["seconds"] = time.monotonic()-started
        print(json.dumps(row), flush=True)
        with (args.out/"checks.jsonl").open("a") as f:
            f.write(json.dumps(row)+"\n")
        save_trial(args.out/f"diagnostic_{nx}x{ny}.npz", state, config, row, pin)
        records.append(row)
        gc.collect()
        jax.clear_caches()
    previous, final = records[-2:]
    drift = abs(final["X"]/previous["X"]-1)
    if any(r["verdict"] != "PASS" for r in (previous, final)) or drift > 1e-6:
        print(f"NOT CLEARED: last two grids must PASS; relative X drift={drift:.3e}", flush=True)
        return 2
    potential = PolynomialPotential.kink_q(config["m"], state["psim"], tuple(config["q"]))
    export = dict(member=meta["member"], slot="validated", nx=final["nx"], ny=final["ny"],
                  member_eta0=meta["member_eta0"], **config,
                  radial_map={"class":type(state["map"]).__name__, **dataclasses.asdict(state["map"])},
                  potential_coeffs=list(map(float,potential.coeffs)),
                  **{k:float(state[k]) for k in ("omega","psim","sigma","xi_t")},
                  **{k:final[k] for k in ("X","R_e","R_A","R_pol","E19","E_c","verdict")},
                  X_v0=meta.get("X_v0"), stability="not_assessed", relative_X_drift=drift)
    np.savez_compressed(args.out/"handoff.npz", meta=json.dumps(export),
                        **{k:state[k] for k in (*FIELDS,"sx","sy")})
    print(f"CLEARED BACKGROUND: {args.out/'handoff.npz'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
