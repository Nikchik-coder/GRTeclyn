#!/usr/bin/env python3
"""Every saved fast-spin Solution as one row of a tracked table.

The continuation legs write one ``<leg>_NNNN.json`` (+ ``.npz``) per
converged point under ``runs/spinning_p3/<leg>/``, which is untracked.  The
figures need only the global numbers, so ``pack`` collects those from the
JSON files into ``results/spinningwormhole/solver/solutions.tsv``, one row
per solution, and ``load`` reads them back.

Columns: ``leg step`` (provenance: the leg directory and its step), ``eta0
gamma omega_inf`` (the family and its asymptotic rotation), ``map map_L nx
ny`` (radial map, its stretch for ``logstretch``, the grid), the
observables ``J v_e mu_plus mu_minus D R_e R_pol R_A Omega_throat
eta_throat`` (CKK conventions: R_e the throat's equatorial circumferential
radius, Omega_throat = omega at the throat's equator, v_e = R_e
Omega_throat), and the identity gates ``tail_max Ec_rel D2_spread
J_spread smarr_rel``.

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.solutions
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[5]
RUNS = REPO / "runs" / "spinning_p3"
TABLE = REPO / "results" / "spinningwormhole" / "solver" / "solutions.tsv"

COLUMNS = (
    "leg", "step", "eta0", "gamma", "omega_inf", "map", "map_L", "nx", "ny",
    "J", "v_e", "mu_plus", "mu_minus", "D", "R_e", "R_pol", "R_A",
    "Omega_throat", "eta_throat",
    "tail_max", "Ec_rel", "D2_spread", "J_spread", "smarr_rel",
)
_TEXT = {"leg", "map"}
_INT = {"step", "map_L", "nx", "ny"}
_POINT = re.compile(r"^(?P<leg>.+)_(?P<step>\d{4})\.json$")


def _row(path: pathlib.Path) -> dict:
    d = json.loads(path.read_text())
    o, g = d["observables"], d["gates"]
    m = _POINT.match(path.name)
    return {
        "leg": path.parent.name, "step": int(m["step"]),
        "eta0": d["eta0"], "gamma": d["gamma"], "omega_inf": d["omega_inf"],
        "map": d["map_name"], "map_L": d["map_params"].get("L", 0),
        "nx": d["nx"], "ny": d["ny"],
        "J": o["J"], "v_e": o["v_e"], "mu_plus": o["mu_plus"],
        "mu_minus": o["mu_minus"], "D": o["D"], "R_e": o["R_eq"],
        "R_pol": o["R_pol"], "R_A": o["R_A"],
        "Omega_throat": o["Omega_throat"], "eta_throat": o["eta_throat"],
        "tail_max": g["tail_max"], "Ec_rel": g["Ec_rel"],
        "D2_spread": g["D2_spread"], "J_spread": g["J_spread"],
        "smarr_rel": g["smarr_rel"],
    }


def pack(runs: pathlib.Path = RUNS, out: pathlib.Path = TABLE) -> list[dict]:
    """Collect every leg's saved solutions (smoke tests excluded) into
    ``out``, sorted by leg and step; returns the rows."""
    rows = []
    for p in sorted(runs.glob("*/*.json")):
        m = _POINT.match(p.name)
        if m and m["leg"] == p.parent.name and not m["leg"].startswith("smoke"):
            rows.append(_row(p))
    rows.sort(key=lambda r: (r["leg"], r["step"]))
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(COLUMNS)
        for r in rows:
            w.writerow([r[c] if c in _TEXT | _INT else repr(float(r[c]))
                        for c in COLUMNS])
    return rows


def load(path: pathlib.Path = TABLE) -> list[dict]:
    """The packed rows, numbers as numbers."""
    with pathlib.Path(path).open(newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    for r in rows:
        for c in COLUMNS:
            if c in _INT:
                r[c] = int(r[c])
            elif c not in _TEXT:
                r[c] = float(r[c])
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--runs", type=pathlib.Path, default=RUNS,
                    help="directory holding one folder per leg")
    ap.add_argument("--out", type=pathlib.Path, default=TABLE)
    args = ap.parse_args(argv)
    rows = pack(args.runs, args.out)
    legs: dict[str, int] = {}
    for r in rows:
        legs[r["leg"]] = legs.get(r["leg"], 0) + 1
    for leg, n in legs.items():
        print(f"  {leg:16s} {n:4d}")
    print(f"packed {len(rows)} solutions from {len(legs)} legs into "
          f"{args.out.relative_to(REPO) if args.out.is_relative_to(REPO) else args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
