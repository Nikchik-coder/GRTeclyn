#!/usr/bin/env python
"""Job F1: measure the Ford-Roman compliance factor over the saved families.

Runs the quantum_budget evaluator over every solution leg in
results/spinningwormhole/solutions/ plus the two synthesized static
anchors, and writes one TSV row per solution (fhat, its grid convergence,
the normalizations, the tail-illegality probe and the ricci-defect gate)
under results/optimisation/fcurve/.

CPU only, one process; the sympy build of the frame-Riemann lambdas runs
once (~minutes) under the address-space cap that the standing cluster rule
requires for sympy work.

Run (repo root):

    grteclyn-wrapper/.venv/bin/python \\
        grteclyn-wrapper/scripts/analysis/quantum_budget/measure_f.py \\
        [--legs fam_a_r1 fam_a_log ...] [--out results/optimisation/fcurve]
"""

from __future__ import annotations

import argparse
import json
import resource
import sys
import time
from pathlib import Path


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    def fmt(v):
        if isinstance(v, float):
            return f"{v:.8g}"
        return str(v)

    with path.open("w", encoding="ascii") as fh:
        fh.write("\t".join(fields) + "\n")
        for row in rows:
            fh.write("\t".join(fmt(row[k]) for k in fields) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--solutions-root",
                    default="results/spinningwormhole/solutions")
    ap.add_argument("--legs", nargs="*", default=None,
                    help="default: every leg directory under the root")
    ap.add_argument("--out", default="results/optimisation/fcurve")
    ap.add_argument("--fraction", type=float, default=1.0,
                    help="sampling fraction f_s in tau0 = f_s ell_c")
    ap.add_argument("--refinements", default="1,1.5,2",
                    help="grid factors for the self-convergence gate")
    ap.add_argument("--no-static-anchors", action="store_true")
    ap.add_argument("--rlimit-gb", type=float, default=16.0)
    args = ap.parse_args()

    cap = int(args.rlimit_gb * 2**30)
    resource.setrlimit(resource.RLIMIT_AS, (cap, cap))

    from grteclyn_wrapper.analysis.quantum_budget import conventions as cv
    from grteclyn_wrapper.analysis.quantum_budget.catalogue import (
        ROW_FIELDS, measure_catalogue,
    )
    from grteclyn_wrapper.analysis.quantum_budget.compliance import (
        ComplianceEvaluator, CurvatureSampling,
    )

    root = Path(args.solutions_root)
    legs = args.legs or sorted(p.name for p in root.iterdir() if p.is_dir())
    evaluator = ComplianceEvaluator(
        sampling=CurvatureSampling(fraction=args.fraction),
        refinements=tuple(float(v) for v in args.refinements.split(",")))

    t0 = time.time()
    rows = measure_catalogue(root, legs, evaluator,
                             static_anchors=not args.no_static_anchors)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    write_tsv(out / "f_curve.tsv", rows, ROW_FIELDS)
    with (out / "measurement.json").open("w", encoding="ascii") as fh:
        json.dump({
            "solutions_root": str(root), "legs": legs,
            "sampling_fraction": args.fraction,
            "refinements": evaluator.refinements,
            "bound": "Ford-Roman Lorentzian, massless scalar, "
                     "3/(32 pi^2 tau0^4)",
            "observer_class": "stationary (u^eta = 0)",
            "n_rows": len(rows),
            "wall_seconds": round(time.time() - t0, 1),
        }, fh, indent=1, sort_keys=True)

    worst_gate = max(r["ricci_defect"] for r in rows)
    worst_conv = max(r["fhat_conv"] for r in rows)
    anchors = [r for r in rows if r["leg"] == "static"]
    for r in anchors:
        tag = f"static family ({r['family']})"
        print(f"{tag}: fhat {r['fhat']:.6g}, F(R_eq = 1 m) 1e{r['log10_F_1m']:.2f}, "
              f"F <= 1 needs R_eq <= {r['max_planck_throat']:.3g} l_p")
    b_anchor = cv.static_ellis_fhat(1.0)
    print(f"closed-form massless-Ellis anchor (eta0 1): fhat {b_anchor:.6g}")
    print(f"{len(rows)} rows; worst fhat_conv {worst_conv:.2e}, "
          f"worst ricci_defect {worst_gate:.2e}; "
          f"{(out / 'f_curve.tsv')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
