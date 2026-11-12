#!/usr/bin/env python3
"""Compare every cell and stored field on identical AMReX hierarchies.

Uses one grid at a time; no uniform covering grid or interpolation. A changed
hierarchy, time, field set or non-finite cell fails the comparison explicitly.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import yt


def compare(before: Path, after: Path, atol: float, rtol: float) -> dict:
    yt.set_log_level(40)
    a, b = yt.load(str(before)), yt.load(str(after))
    fields_a = sorted(f for f in a.field_list if f[0] == "boxlib")
    fields_b = sorted(f for f in b.field_list if f[0] == "boxlib")
    if fields_a != fields_b:
        raise ValueError(f"Stored fields differ: {fields_a} vs {fields_b}")
    if float(a.current_time) != float(b.current_time):
        raise ValueError("Plotfile times differ")
    for attr in ("domain_left_edge", "domain_right_edge", "domain_dimensions"):
        if not np.array_equal(getattr(a, attr), getattr(b, attr)):
            raise ValueError(f"Domain differs: {attr}")
    key = lambda g: (g.Level, *g.LeftEdge.to_value(), *g.ActiveDimensions)
    ga, gb = sorted(a.index.grids, key=key), sorted(b.index.grids, key=key)
    if len(ga) != len(gb):
        raise ValueError("Grid counts differ")
    stats = {
        f[1]: dict(count=0, max_abs_difference=0.0, max_abs_reference=0.0,
                   difference_sum_squares=0.0, reference_sum_squares=0.0,
                   nonfinite_before=0, nonfinite_after=0)
        for f in fields_a
    }
    for x, y in zip(ga, gb):
        if key(x) != key(y) or not np.array_equal(x.RightEdge, y.RightEdge):
            raise ValueError("AMR grid geometry differs")
        for f in fields_a:
            va, vb = np.asarray(x[f]), np.asarray(y[f])
            s = stats[f[1]]
            s["count"] += va.size
            s["nonfinite_before"] += int(np.count_nonzero(~np.isfinite(va)))
            s["nonfinite_after"] += int(np.count_nonzero(~np.isfinite(vb)))
            finite = np.isfinite(va) & np.isfinite(vb)
            ref, delta = va[finite], vb[finite] - va[finite]
            s["max_abs_difference"] = max(s["max_abs_difference"], float(np.max(np.abs(delta), initial=0)))
            s["max_abs_reference"] = max(s["max_abs_reference"], float(np.max(np.abs(ref), initial=0)))
            s["difference_sum_squares"] += float(np.dot(delta, delta))
            s["reference_sum_squares"] += float(np.dot(ref, ref))
        x.clear_data()
        y.clear_data()
    for s in stats.values():
        s["rms_difference"] = float(np.sqrt(s.pop("difference_sum_squares") / s["count"]))
        s["rms_reference"] = float(np.sqrt(s.pop("reference_sum_squares") / s["count"]))
        s["threshold"] = atol + rtol * s["max_abs_reference"]
        s["pass"] = (s["max_abs_difference"] <= s["threshold"] and
                     not s["nonfinite_before"] and not s["nonfinite_after"])
    return dict(before=before.name, after=after.name, time=float(a.current_time),
                grids=len(ga), levels=int(a.index.max_level) + 1,
                atol=atol, rtol=rtol, fields=stats,
                all_fields_match=all(s["pass"] for s in stats.values()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--atol", type=float, default=1e-12)
    parser.add_argument("--rtol", type=float, default=1e-9)
    args = parser.parse_args()
    result = compare(args.before, args.after, args.atol, args.rtol)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    for name, field in result["fields"].items():
        print(f"{name}: max_abs={field['max_abs_difference']:.8g} "
              f"reference={field['max_abs_reference']:.8g} pass={field['pass']}")
    return 0 if result["all_fields_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
