"""Independently refine a saved candidate before an evolution handoff.

Input: a candidate NPZ, increasing grids and an optional physical radius.
Output: manifests, per-grid diagnostic fields and, only on clearance,
handoff.npz. The last two grids must PASS with finite positive X = |VIQ|/R_e
and relative drift at most 1e-6. Radius rescaling changes lengths by s,
J by s^2 and the potential by 1/s^2. Stability remains unassessed.

    python -m grteclyn_wrapper.optimisation.commands.validate_candidate --help
"""
from __future__ import annotations

import dataclasses
import gc
import json
from pathlib import Path
import time

import numpy as np


def run(args, *, error):
    """Execute parsed options; report invalid requests through ``error``."""
    grids = [tuple(map(int, g.split("x"))) for g in args.grids.split(",")]
    if len(grids) < 2 or any(a >= c or b >= d for (a,b),(c,d) in zip(grids,grids[1:])):
        error("need at least two grids, refining both directions")
    if args.radius is not None and args.radius <= 0:
        error("radius must be positive")
    from grteclyn_wrapper.optimisation.solver.device import select_device
    select_device(args.gpu, 512)
    import jax
    from grteclyn_wrapper.optimisation.exploration import (
        FIELDS, load_seed, physical_throat, save_trial, solve_trial,
    )
    from grteclyn_wrapper.optimisation.potentials import PolynomialPotential
    from grteclyn_wrapper.optimisation.resolution import consistent

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
                    pin=pin, rescale=scale, stability="not_assessed",
                    newton_acceptance=1e-9, independent_constraint_gate=1e-8)
    (args.out/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    records = []
    for nx,ny in grids:
        started = time.monotonic()
        print(f"Solving {nx}x{ny}: J={config['J']:.12g}, R_e={pin[1]:.12g}", flush=True)
        # Stop at the existing acceptance floor. Demanding 1e-14 first can
        # degrade an already accurate field through an ill-conditioned step.
        # Independent constraints still decide clearance at every resolution.
        state, row = solve_trial(state, config, nx, ny, pin, d2, max_iter=24,
                                 newton_tol=1e-9)
        row["seconds"] = time.monotonic()-started
        print(json.dumps(row), flush=True)
        with (args.out/"checks.jsonl").open("a") as f:
            f.write(json.dumps(row)+"\n")
        save_trial(args.out/f"diagnostic_{nx}x{ny}.npz", state, config, row, pin)
        records.append(row)
        gc.collect()
        jax.clear_caches()
    previous, final = records[-2:]
    passed, drift = consistent([previous, final])
    if not passed:
        print(f"NOT CLEARED: last two grids must PASS with finite positive bills; "
              f"relative X drift={drift}", flush=True)
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
