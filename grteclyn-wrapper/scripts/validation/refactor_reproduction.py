#!/usr/bin/env python3
"""Compare pre-extraction code and installed wheels using real bounded workflows.

Run each case in a fresh, externally capped process. PYTHONPATH selects either
the original source archive or a directory containing installed wheels. No
legacy import aliases or numerical tolerances are patched into either version.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import importlib
import importlib.abc
import importlib.metadata
import json
import math
from pathlib import Path
import sys
import time

import numpy as np

CASES = ("spin", "spherical", "accepted_ring", "rejected_ring", "boson", "application")
CONSTRAINTS = "results/merger/campaign/08_convergence/farzone_headon_flip_d8_L512_lvl7_t100_csm/constraint_norms.dat"


class NoWrapper(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in {"grteclyn_wrapper", "grteclyn_workflows"}:
            raise ImportError(f"standalone solver attempted wrapper import: {fullname}")


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def worker(args):
    out = args.out / args.version / args.case
    out.mkdir(parents=True, exist_ok=False)
    modern = args.version == "wheel"
    if modern and args.case != "application":
        sys.meta_path.insert(0, NoWrapper())
    roots = {
        "spin": "grteclyn_stationary.spinning_wormhole" if modern else "grteclyn_wrapper.analysis.spinning_wormhole",
        "ring": "grteclyn_stationary.railgun" if modern else "grteclyn_wrapper.optimisation.railgun",
        "profiles": "grteclyn_stationary.profiles" if modern else "grteclyn_wrapper.grtresna.profiles",
        "newton": "grteclyn_stationary.numerics.newton" if modern else "grteclyn_wrapper.optimisation.solver.newton",
    }
    def module(group, suffix=""):
        return importlib.import_module(roots[group] + ("." + suffix if suffix else ""))

    inputs = {}
    def source(relative):
        path = args.repo / relative
        inputs[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        return path

    started = time.monotonic()
    record, arrays = {}, {}
    if args.case == "spin":
        continuation = module("spin", "continuation")
        backgrounds = module("spin", "backgrounds")
        solution = module("spin", "solution").Solution
        for j, nx, ny in ((.25, 48, 12), (1., 64, 16)):
            label = f"J{j}"
            sol, info = continuation.solve_point(eta0=2., gamma=-math.pi, J=j, nx=nx, ny=ny, verbose=True)
            assert info["converged"] and info["iters"] > 0, info
            gates = sol.gates
            for key, limit in {"Ec_rel": 5e-9, "D2_spread": 1e-10, "J_spread": 5e-9,
                               "smarr_rel": 1e-10, "tail_max": 1e-11}.items():
                assert gates[key] <= limit, (label, key, gates[key])
            assert abs(gates["J_flux"] - j) <= 1e-10
            path = out / label
            sol.save(path)
            restored = solution.load(path)
            for name in ("F", "W", "N"):
                np.testing.assert_array_equal(getattr(sol, name), getattr(restored, name))
                arrays[label + "/" + name] = getattr(restored, name)
            x, mu, components, table_info = backgrounds.full_background(path, 129, 33)
            table = out / (label + ".spinbg")
            backgrounds.write_spinbg(table, table_info["table_eta0"], x, mu, components)
            _, body = backgrounds.read_spinbg(table)
            np.testing.assert_array_equal(body, np.stack([components[k] for k in backgrounds.COMPONENT_NAMES], axis=-1))
            arrays[label + "/table"] = body
            record[label] = dict(gates=gates, observables=sol.observables, meta=sol.meta,
                                 export=table_info)
    elif args.case in ("spherical", "accepted_ring", "rejected_ring"):
        workflow = module("ring", "workflow")
        diagnostics = module("ring", "diagnostics")
        names = {"spherical": "spherical-validated/accepted", "accepted_ring": "spherical-to-ring-first/attempt_005",
                 "rejected_ring": "spherical-to-ring-resumed/attempt_017"}
        relative = "results/railgun/studies/" + names[args.case]
        p, u, _ = workflow.load_state(source(relative + ".npz"))
        if args.case == "spherical":
            seed = u.copy()
            # Perturb an interior scalar coefficient; require actual Newton corrections.
            u0 = u.copy()
            u0[4 * p.n + p.n // 2] += 1e-5
            u, info = module("newton").newton(p.residual, p.jacobian, u0, tol=1e-12,
                                               max_iter=12, min_updates=2, verbose=True)
            assert info["converged"] and info["iters"] >= 2, info
            error = float(np.max(np.abs(u - seed)))
            assert error < 1e-8, error
            record["archive_max_abs_error"] = error
            workflow.save_state(out / "recovered.npz", p, u)
            _, restored, _ = workflow.load_state(out / "recovered.npz")
            np.testing.assert_array_equal(u, restored)
        else:
            info = json.loads(source(relative + ".json").read_text())["newton"]
        validation = diagnostics.validate(p, u, info)
        expected = "REJECT" if args.case == "rejected_ring" else "PASS"
        assert validation["verdict"] == expected, validation
        if expected == "REJECT":
            assert {"independent_equations", "intrinsic_kg_crosscheck", "angular_momentum_balance"} <= set(validation["reasons"])
        record["validation"] = validation
        arrays["u"] = u
    elif args.case == "boson":
        couplings = module("profiles", "qball_couplings").QBallCouplings.free_field(mass=1., omega=.5)
        profile = module("profiles", "boson_star_ode").solve_selfgrav_boson_star(couplings, phi_c=.1)
        assert 0 < profile.omega < profile.mass
        assert abs(profile.phi0[-1] / profile.phi0[0]) < 1e-5
        for key in ("r", "phi0", "psi", "alpha"):
            arrays[key] = getattr(profile, key)
        for key in ("mass", "lam", "mu", "omega", "phi_c", "adm_mass", "compactness"):
            record[key] = getattr(profile, key)
    else:
        prefix = "grteclyn_workflows" if modern else "grteclyn_wrapper"
        diagnostics = importlib.import_module(prefix + (".diagnostics.measurements.constraints" if modern else ".metrics.diagnostics.constraints"))
        plotter = importlib.import_module(prefix + (".plotting" if modern else ".visualisation") + ".wormhole_merger.plot_merger_constraints")
        path = source(CONSTRAINTS)
        record["metrics"] = dataclasses.asdict(diagnostics.read_constraint_metrics(path))
        arrays["stream"] = plotter.stitch([str(path)])
        sys.argv = ["plot_merger_constraints", "--run", f"reference:{path}", "--out", str(out / "constraints.png")]
        plotter.main()
        from PIL import Image
        with Image.open(out / "constraints.png") as img:
            arrays["pixels"] = np.asarray(img)
        assert (out / "constraints.pdf").stat().st_size > 1000
    for key, value in arrays.items():
        assert np.isfinite(value).all(), key
    np.savez_compressed(out / "arrays.npz", **arrays)
    write_json(out / "values.json", record)
    write_json(out / "run.json", dict(case=args.case, version=args.version, revision=args.revision,
        inputs=inputs, seconds=time.monotonic()-started, python=sys.version.split()[0],
        dependencies={p: importlib.metadata.version(p) for p in ("jax", "jaxlib", "numpy", "scipy", "matplotlib")},
        wrapper_imports_blocked=modern and args.case != "application", backend="cpu"))
    print(f"PASS {args.version} {args.case}", flush=True)


def compare(args):
    summary = {}
    for case in CASES:
        before, after = (args.out / version / case for version in ("legacy", "wheel"))
        left_run, right_run = (json.loads((path / "run.json").read_text()) for path in (before, after))
        for key in ("inputs", "dependencies", "python"):
            assert left_run[key] == right_run[key], (case, key)
        diffs = []
        def check(a, b, key):
            if isinstance(a, dict):
                assert a.keys() == b.keys(), key
                for k in a:
                    check(a[k], b[k], key + "/" + k)
            elif isinstance(a, list):
                assert len(a) == len(b), key
                for i, (x, y) in enumerate(zip(a, b)):
                    check(x, y, key + f"/{i}")
            elif isinstance(a, float):
                assert math.isfinite(a) and math.isfinite(b), key
                assert math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-12), (key, a, b)
                diffs.append(abs(a - b))
            else:
                assert a == b, (key, a, b)
        check(json.loads((before / "values.json").read_text()), json.loads((after / "values.json").read_text()), case)
        array_diffs = {}
        with np.load(before / "arrays.npz") as a, np.load(after / "arrays.npz") as b:
            assert set(a.files) == set(b.files)
            for key in a.files:
                np.testing.assert_allclose(a[key], b[key], rtol=1e-10, atol=1e-12, equal_nan=False, err_msg=case + "/" + key)
                array_diffs[key] = float(np.max(np.abs(a[key].astype(float) - b[key].astype(float))))
        summary[case] = dict(verdict="PASS", array_max_abs_errors=array_diffs,
            scalar_max_abs_error=max(diffs, default=0.), before=left_run, after=right_run,
            values=json.loads((after / "values.json").read_text()))
    write_json(args.out / "comparison.json", dict(rtol=1e-10, atol=1e-12, cases=summary))
    print("PASS: all six before/after workflows agree", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=("run", "compare"))
    ap.add_argument("--version", choices=("legacy", "wheel"))
    ap.add_argument("--case", choices=CASES)
    ap.add_argument("--repo", type=Path)
    ap.add_argument("--revision")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if args.action == "run":
        if not all((args.version, args.case, args.repo, args.revision)):
            ap.error("run requires --version, --case, --repo and --revision")
        worker(args)
    else:
        compare(args)


if __name__ == "__main__":
    main()
