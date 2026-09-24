#!/usr/bin/env python3
"""Build runs_index.tsv -- the machine half of the run registry -- and check
every run's NAME and seeds against what it actually ran.

One row per packed run, from its run_manifest.json (written by run_single.sh
at launch since 2026-09-24, or reconstructed afterwards by `run_manifest.py
backfill-all`) and its packed streams.  Nothing here is typed by hand: the
prose stays in runs_registry.tsv, the facts come from here.

Three checks, each of which would have caught a real error:
  seed      a seed requested in the params that did not take -- the binary
            lacks the key, the launch-time preflight said "no effect", or the
            run's t = 0 constraint norms are bit-identical to an unseeded run's
            (how the 2026-09-23 audit found four quadrupole arms without their
            quadrupole);
  name      each token of the run name that name_grammar.tsv knows (q1e2, ml4,
            p012, eta4, ...) against the params the run used;
  binary    keys in the params that the binary does not contain (frozen binaries
            only -- the live build product has been rebuilt since).

Usage: run_index.py [<pack-root>]      (default: this file's parent's parent)
Exit status 0 always (a report, not a gate); the problem count is printed.
Standard library + numpy only, reading nothing outside the pack.
"""

from __future__ import annotations

import csv
import json
import math
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pack_paths import iter_runs  # noqa: E402

SEED_KEYS = ("wormhole_seed_amplitude_A", "wormhole_seed_l2_amplitude_A")
FIELDS = ["run", "group", "provenance", "binary", "binary_version", "preflight",
          "eps", "eps2", "max_level", "L", "N1", "stop_time", "restart", "H0",
          "seed_check", "name_check", "binary_check"]


def parse_params(path: pathlib.Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"\s*([A-Za-z_][\w.]*)\s*=(.*)$", line.split("#", 1)[0])
            if m:
                out[m.group(1)] = m.group(2).strip()
    return out


def num(params: dict[str, str], key: str, index: int = 0) -> float | None:
    try:
        return float(params[key].split()[index].strip('"'))
    except (KeyError, IndexError, ValueError):
        return None


def vec(params: dict[str, str], key: str) -> list[float] | None:
    try:
        v = [float(x) for x in params[key].split()[:3]]
        return v if len(v) == 3 else None
    except (KeyError, ValueError):
        return None


def derived(params: dict[str, str], what: str) -> float | None:
    """Quantities a name token encodes that are not one key."""
    if what == "separation":
        a, b = vec(params, "wormhole_centerA"), vec(params, "wormhole_centerB")
        return math.dist(a, b) if a and b else None
    if what == "momentum":
        p = vec(params, "wormhole_momentumA")
        return math.hypot(*p) if p else None
    if what == "restart_step":
        r = params.get("amr.restart", "").strip('"')
        m = re.search(r"Chk0*(\d+)$", r)
        return float(m.group(1)) if m else None
    return None


# The initial-data setup a seed perturbs; two runs with the same values here
# start from the same t = 0 data unless a seed differs (constraint norms are
# level-0 reductions, so max_level does not enter).
SETUP_KEYS = ("L", "N1", "wormhole_id_type", "wormhole_initial_lapse_type",
              "wormhole_throat_radius_A", "wormhole_throat_radius_B",
              "wormhole_drainhole_mass_A", "wormhole_drainhole_mass_B",
              "wormhole_bare_mass_A", "wormhole_bare_mass_B", "wormhole_centerA",
              "wormhole_centerB", "wormhole_momentumA", "wormhole_momentumB",
              "wormhole_phi_sign_B", "wormhole_helfer_correction",
              "wormhole_support_strength", "phantom_mass", "center")


def signature(params: dict[str, str]) -> tuple:
    return tuple(" ".join(params.get(k, "").split()) for k in SETUP_KEYS)


def load_grammar(path: pathlib.Path) -> list[dict]:
    """name_grammar.tsv: token_regex, param, expected, compare, note (+ counts)."""
    rules = []
    if not path.exists():
        return rules
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader((l for l in fh if l.strip() and not l.startswith("#")),
                                delimiter="\t", quoting=csv.QUOTE_NONE)
        for row in reader:
            try:
                row["rx"] = re.compile(row["token_regex"])
            except re.error as e:
                print(f"[run-index] bad regex {row.get('token_regex')!r}: {e}")
                continue
            rules.append(row)
    return rules


def check_name(name: str, params: dict[str, str], rules: list[dict]) -> list[str]:
    problems = []
    for rule in rules:
        m = rule["rx"].search(name)
        if not m:
            continue
        param = rule["param"].strip()
        if param.startswith("(") or not param:
            continue                                   # consumer-side or informational
        groups = {f"g{i}": g for i, g in enumerate(m.groups(), start=1)}
        try:
            want = eval(rule["expected"], {"__builtins__": {}, "float": float, "int": int,
                                           "abs": abs}, groups)
        except Exception as e:  # noqa: BLE001
            problems.append(f"{m.group(0)}: bad rule ({e})")
            continue
        have = derived(params, param.split(":", 1)[1]) if param.startswith("derived:") \
            else num(params, param)
        if have is None:
            problems.append(f"{m.group(0)} says {param} = {want:g}, params have no {param}")
            continue
        tol = 1e-9 * max(1.0, abs(want))
        if abs(have - want) > tol:
            problems.append(f"{m.group(0)} says {param} = {want:g}, params say {have:g}")
    return problems


def first_row(path: pathlib.Path) -> tuple[list[str], list[str]] | None:
    """(header names, first data row as printed strings) of a stream."""
    if not path.exists():
        return None
    names: list[str] = []
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("#"):
                toks = line.lstrip("#").split()
                if toks and all(re.fullmatch(r"[A-Za-z_]\w*", t) for t in toks):
                    names = toks
                continue
            vals = line.split()
            if vals:
                return names, vals
    return None


def main(argv: list[str]) -> int:
    root = pathlib.Path(argv[0]) if argv else pathlib.Path(__file__).resolve().parents[1]
    rules = load_grammar(root / "name_grammar.tsv")
    rows, h0_by_value = [], {}
    for group, d in iter_runs(root):
        man_path = d / "run_manifest.json"
        man = json.loads(man_path.read_text(encoding="utf-8")) if man_path.exists() else {}
        params = man.get("params") or parse_params(d / "evolution_params.txt")
        binary = man.get("binary") or {}
        pf = man.get("preflight") or {}
        seeds = {k: num(params, k) or 0.0 for k in SEED_KEYS}
        fr = first_row(d / "constraint_norms.dat")
        h0 = ""
        if fr and fr[1] and abs(float(fr[1][0])) < 1e-12 and len(fr[1]) > 1:
            h0 = fr[1][1]                                # the printed t = 0 L2_Ham
        row = {
            "run": d.name, "group": group,
            "provenance": ("none" if not man else "reconstructed" if man.get("reconstructed")
                           else "launch manifest"),
            "binary": binary.get("file", ""), "binary_version": binary.get("grteclyn_version", ""),
            "preflight": str(pf.get("verdict", "")) if man else "",
            "eps": f"{seeds[SEED_KEYS[0]]:g}", "eps2": f"{seeds[SEED_KEYS[1]]:g}",
            "max_level": params.get("max_level", ""), "L": params.get("L", ""),
            "N1": params.get("N1", ""), "stop_time": params.get("stop_time", ""),
            "restart": "yes" if params.get("amr.restart") else "",
            "H0": h0,
            "_seeds": seeds, "_absent": binary.get("absent_keys"), "_man": man,
            "_params": params,
        }
        if h0 and not row["restart"]:
            h0_by_value.setdefault(h0, []).append(row)
        rows.append(row)

    n_seed = n_name = n_bin = 0
    for row in rows:
        seeds, absent, man = row["_seeds"], row["_absent"], row["_man"]
        asked = {k: v for k, v in seeds.items() if v}
        notes = []
        if asked and not row["restart"]:
            if absent:
                lost = [k for k in asked if k in absent]
                if lost:
                    notes.append("NOT APPLIED: the binary does not contain " + ", ".join(lost))
            if (man.get("seed") or "") == "no effect":
                notes.append("NOT APPLIED: launch preflight found no effect")
            # Identical t = 0 data under DIFFERENT seeds: some seed did nothing.
            # Blame the seeds this run has and the twin lacks.
            twins = [(r["run"], [k for k in asked if seeds[k] != r["_seeds"][k]])
                     for r in h0_by_value.get(row["H0"], [])
                     if r is not row and r["_seeds"] != seeds]
            twins = [(name, keys) for name, keys in twins if keys]
            if twins:
                name, keys = twins[0]
                notes.append(f"NOT APPLIED: t=0 data identical to {name}, which lacks "
                             f"{', '.join(k.replace('wormhole_seed_', '') for k in keys)}"
                             + (f" (+{len(twins) - 1} more)" if len(twins) > 1 else ""))
            if not notes and man.get("seed") == "took":
                notes.append("took (launch preflight)")
            if not notes:
                # Positive evidence: the same setup without the seeds starts from
                # different t = 0 data.
                base = signature(row["_params"])
                twin = next((r for r in rows if r is not row and not r["restart"]
                             and not any(r["_seeds"].values()) and r["H0"]
                             and signature(r["_params"]) == base), None)
                if twin and twin["H0"] != row["H0"]:
                    notes.append(f"took (t=0 data differs from unseeded {twin['run']})")
                else:
                    notes.append("unverified")
        row["seed_check"] = "; ".join(notes) if notes else ("n/a" if not asked else "restart")
        n_seed += row["seed_check"].startswith("NOT APPLIED")

        problems = check_name(row["run"], row["_params"], rules)
        row["name_check"] = "MISMATCH: " + "; ".join(problems) if problems else "ok"
        n_name += bool(problems)

        real_absent = [k for k in (absent or []) if k not in ALLOW_DEAD]
        row["binary_check"] = ("unknown" if absent is None else
                               "lacks: " + ", ".join(real_absent) if real_absent else "ok")
        n_bin += bool(real_absent)

    out = root / "runs_index.tsv"
    with out.open("w", encoding="utf-8", newline="") as fh:
        fh.write("# GENERATED by analysis/run_index.py from the packed run_manifest.json files and streams"
                 " -- do not edit.\n# The prose half of the registry is runs_registry.tsv.\n")
        w = csv.DictWriter(fh, fieldnames=FIELDS, delimiter="\t", extrasaction="ignore",
                           quoting=csv.QUOTE_NONE, escapechar="\\")
        w.writeheader()
        for row in rows:
            w.writerow(row)
    n_man = sum(r["provenance"] != "none" for r in rows)
    print(f"[run-index] {len(rows)} runs ({n_man} with a manifest): {n_seed} seed(s) not applied, "
          f"{n_name} name mismatch(es), {n_bin} run(s) whose binary lacks a params key "
          f"-> {out.name}")
    for row in rows:
        if row["seed_check"].startswith("NOT APPLIED") or row["name_check"] != "ok":
            print(f"  {row['run']}: seed {row['seed_check']}; name {row['name_check']}")
    return 0


# Keys no binary reads, by design (see preflight_allow.txt): not a finding.
ALLOW_DEAD = {"hdf5_subpath", "nonzero_asymptotic_vars", "nonzero_asymptotic_values",
              "amr.plot_vars", "amr.derive_plot_vars"}

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
