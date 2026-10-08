#!/usr/bin/env python3
"""Outgoing-null-ray escape probe for wormhole (drainhole) plotfiles.

The apparent-horizon scans (ah_radial_scan / ah_oriented_scan / ah_flow_finder)
find marginally trapped surfaces on one slice: quasi-local and
slicing-dependent.  This probe asks the causal question directly: does an
outgoing null ray launched just outside a mouth (or the common surface) reach a
detector sphere?  On one plotfile it tests the frozen slice; on a stack of >= 3
it traces through the time-interpolated 4D metric (the FTL package's
EvolvingMetricField), optionally sweeping the emission time.  Rays that escape
before merger but stop escaping after it are the event-horizon-style signature
a MOTS alone cannot certify; with a finite stack the statement is "no escape
within the trusted evolution", never a strict event horizon.

Per launch centre, radius and axis direction one ray is traced with the FTL
package's Hamiltonian null integrator pieces (RK4, null re-projection, capture
detection).  Outcomes:

  escaped    reached the detector sphere (arrival coordinate time reported)
  captured   entered a collapsed-lapse (< 0.1) or deep-conformal (chi < 1e-3)
             region.  At t ~ 0 on a wormhole that is the throat funnel -- the
             ray went DOWN THE THROAT toward the other infinity, which is an
             escape route, not a horizon.  Only the lapse channel, or captures
             that switch on at later emission times, indicate trapping.
  outlived   the stack ended (evolving mode) before the ray got out: unknown,
             extend the stack.
  stuck      max_steps without arrival inside a live stack.

The relative null-constraint drift (Hrel) is the same reliability gate as the
FTL probes (H_REL_TOL = 1e-2): a ray above it sampled the metric where the
covering grid cannot represent it (typically r <~ 2 dx from a puncture centre)
and its outcome should not be quoted.

Plotfiles must carry chi h11..h33 lapse shift1 shift2 shift3.  Frames-only
packs do not; this runs on scratch plotfiles or a fresh run.

Examples
--------
  # t = 0 slice, mouths read from the params file (wormhole_centerA/B are
  # offsets from the domain centre; the script adds it)
  wormhole_escape_trace.py OUT/plt00000 --params params.txt

  # merger window, emission-time sweep from just outside the common centre
  wormhole_escape_trace.py plt014* plt015* --centers 32 32 32 \
      --radii 2 3 4 6 --t-emit 14 15 16 17
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from grteclyn_wrapper.metrics.probes.ftl.evolving_geodesic import _hamiltonian_rhs
from grteclyn_wrapper.metrics.probes.ftl.geodesic import (
    H_REL_TOL,
    _null_relative_drift,
    build_metric_3d_from_plotfile,
    future_null_cov,
    null_hamiltonian,
    project_null,
    ray_is_captured,
)
from grteclyn_wrapper.metrics.probes.ftl.metric_field import (
    EvolvingMetricField,
    MetricField,
    StaticMetricField,
    evolving_field_from_plotfiles,
)

_DIRS: tuple[tuple[str, NDArray[np.float64]], ...] = tuple(
    (f"{s}{a}", np.array([sign if i == ax else 0.0 for i in range(3)]))
    for ax, a in enumerate("xyz")
    for s, sign in (("+", 1.0), ("-", -1.0))
)


def trace_outgoing_ray(
    field: MetricField,
    *,
    launch: NDArray[np.float64],
    n_hat: NDArray[np.float64],
    detector_center: NDArray[np.float64],
    detector_radius: float,
    t0: float = 0.0,
    ds: float = 0.02,
    max_steps: int = 400_000,
    h_tol: float = 1.0e-6,
) -> tuple[str, float | None, float]:
    """Trace one outgoing null ray; return (outcome, t_arrival, max_h_rel).

    outcome is 'escaped', 'captured', 'left_grid', 'outlived' or 'stuck'.
    'left_grid' (crossed the covering-grid edge before the detector sphere)
    counts as an escape route only if the detector sphere lies outside the
    grid -- keep detector_radius inside the sampled box.
    """
    x = np.array([t0, launch[0], launch[1], launch[2]], dtype=float)
    g_pt, ginv_pt, _ = field.sample(x)
    k = future_null_cov(g_pt, n_hat)
    max_h_rel = 0.0
    t_stack_end = (
        float(field.times[-1]) if isinstance(field, EvolvingMetricField) else None
    )
    lo = np.asarray(field.origin[:3], dtype=float)
    hi = lo + (np.array(field.spatial_shape) - 1) * np.array(field.spatial_spacing)

    for _ in range(max_steps):
        r = float(np.linalg.norm(x[1:] - detector_center))
        if r >= detector_radius:
            return "escaped", float(x[0]) - t0, max_h_rel
        if t_stack_end is not None and float(x[0]) > t_stack_end + 1.0e-9:
            return "outlived", None, max_h_rel
        g_pt, ginv_pt, dg_pt = field.sample(x)
        if ray_is_captured(g_pt, ginv_pt):
            return "captured", None, max_h_rel
        h = abs(null_hamiltonian(ginv_pt, k))
        max_h_rel = max(max_h_rel, _null_relative_drift(ginv_pt, k))
        if h > h_tol:
            k = project_null(g_pt, ginv_pt, k, dx_ref=(ginv_pt @ k)[1:])

        def rhs(xp: NDArray[np.float64], kp: NDArray[np.float64]):
            _g, ginvp, dgp = field.sample(xp)
            return _hamiltonian_rhs(ginvp, dgp, kp)

        k1x, k1k = rhs(x, k)
        k2x, k2k = rhs(x + 0.5 * ds * k1x, k + 0.5 * ds * k1k)
        k3x, k3k = rhs(x + 0.5 * ds * k2x, k + 0.5 * ds * k2k)
        k4x, k4k = rhs(x + ds * k3x, k + ds * k3k)
        x = x + (ds / 6.0) * (k1x + 2 * k2x + 2 * k3x + k4x)
        k = k + (ds / 6.0) * (k1k + 2 * k2k + 2 * k3k + k4k)
        if np.any(x[1:] <= lo) or np.any(x[1:] >= hi):
            return "left_grid", None, max_h_rel
    return "stuck", None, max_h_rel


def centers_from_params(path: Path) -> list[NDArray[np.float64]]:
    centers: list[NDArray[np.float64]] = []
    for line in path.read_text().splitlines():
        line = line.split("#", 1)[0]
        if "=" not in line:
            continue
        key, val = (s.strip() for s in line.split("=", 1))
        if key in ("wormhole_centerA", "wormhole_centerB"):
            centers.append(np.array([float(v) for v in val.split()]))
    if not centers:
        raise SystemExit(f"no wormhole_centerA/B in {path}")
    return centers


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("plotfiles", nargs="+", help="1 = frozen slice, >= 3 = 4D stack")
    ap.add_argument("--params", type=Path, help="read launch centres from wormhole_centerA/B")
    ap.add_argument("--centers", type=float, nargs="+", metavar="C",
                    help="flat x y z triples of ABSOLUTE launch centres "
                         "(overrides --params)")
    ap.add_argument("--radii", type=float, nargs="+", default=[0.5, 1.0, 2.0, 4.0],
                    help="launch radii around each centre")
    ap.add_argument("--t-emit", type=float, nargs="+", default=None,
                    help="emission coordinate times (evolving mode only)")
    ap.add_argument("--n", type=int, default=129, help="covering grid points per axis")
    ap.add_argument("--half-width", type=float, default=16.0,
                    help="covering grid half-width about the domain centre")
    ap.add_argument("--escape-radius", type=float, default=None,
                    help="detector sphere radius about the domain centre "
                         "(default 0.9 x half-width)")
    ap.add_argument("--ds", type=float, default=0.02, help="affine step")
    args = ap.parse_args()

    centers_relative = False
    if args.centers:
        if len(args.centers) % 3:
            ap.error("--centers takes flat x y z triples")
        centers = [np.array(args.centers[i : i + 3]) for i in range(0, len(args.centers), 3)]
    elif args.params:
        # wormhole_centerA/B are offsets from the domain centre (see
        # BinaryWormholeInitialData); shifted once the grid centre is known.
        centers = centers_from_params(args.params)
        centers_relative = True
    else:
        ap.error("give --params or --centers")

    n_plots = len(args.plotfiles)
    if n_plots == 1:
        g, origin, spacing = build_metric_3d_from_plotfile(
            args.plotfiles[0], n=args.n, half_width=args.half_width
        )
        field: MetricField = StaticMetricField(g=g, origin=origin, spatial_spacing=spacing)
        emits = [0.0]
        mode = "frozen slice"
    elif n_plots >= 3:
        field = evolving_field_from_plotfiles(
            sorted(args.plotfiles), n_space=args.n, half_width=args.half_width
        )
        emits = args.t_emit if args.t_emit else [float(field.times[0])]
        mode = (f"4D stack of {n_plots} slices, "
                f"t in [{field.times[0]:g}, {field.times[-1]:g}]")
    else:
        ap.error("give 1 plotfile (frozen) or >= 3 (evolving)")

    domain_center = np.asarray(field.origin[:3]) + 0.5 * (
        np.array(field.spatial_shape) - 1
    ) * np.array(field.spatial_spacing)
    if centers_relative:
        centers = [c + domain_center for c in centers]
    r_det = args.escape_radius or 0.9 * args.half_width
    print(f"mode: {mode}")
    print(f"grid: n={args.n} half_width={args.half_width} "
          f"dx={field.spatial_spacing[0]:.3f}; detector r={r_det:g} "
          f"about {np.array2string(domain_center, precision=1)}")
    print(f"{'t_emit':>7} {'centre':>18} {'r':>5} {'dir':>4} "
          f"{'outcome':>9} {'t_arr':>8} {'Hrel':>9}")

    worst: dict[float, list[str]] = {}
    for t0 in emits:
        outcomes: list[str] = []
        for c in centers:
            for r in args.radii:
                for name, n_hat in _DIRS:
                    launch = c + r * n_hat
                    if float(np.linalg.norm(launch - domain_center)) >= r_det:
                        print(f"{t0:7.2f} {np.array2string(c, precision=1):>18} "
                              f"{r:5.2f} {name:>4} {'outside':>9}        -         ")
                        continue
                    out, t_arr, hrel = trace_outgoing_ray(
                        field, launch=launch, n_hat=n_hat,
                        detector_center=domain_center, detector_radius=r_det,
                        t0=t0, ds=args.ds,
                    )
                    unreliable = "!" if hrel > H_REL_TOL else " "
                    t_s = f"{t_arr:8.3f}" if t_arr is not None else "       -"
                    print(f"{t0:7.2f} {np.array2string(c, precision=1):>18} "
                          f"{r:5.2f} {name:>4} {out:>9} {t_s} {hrel:8.1e}{unreliable}")
                    if hrel <= H_REL_TOL:
                        outcomes.append(out)
        worst[t0] = outcomes

    print("\nsummary (reliable rays only; captured at t ~ 0 = down the throat):")
    for t0, outs in worst.items():
        n = len(outs)
        esc = outs.count("escaped")
        cap = outs.count("captured")
        rest = n - esc - cap
        verdict = "all escape" if esc == n and n else f"{esc}/{n} escape, {cap} captured, {rest} other"
        print(f"  t_emit {t0:g}: {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
