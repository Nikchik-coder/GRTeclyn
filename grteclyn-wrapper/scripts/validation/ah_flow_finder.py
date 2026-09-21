"""Shape-free MOTS hunt: a spectral fast-flow finder on plotfile data.

Why this exists (referee queue R0, 2026-09-21).  Every horizon statement in
the article comes from the oriented STAR-SHAPED scan (extraction/horizon.py):
coordinate spheres about chosen centres.  Item 8 of the article's open list
says exactly that, and the referee's Major D presses it: a common surface
deformed beyond star-shapedness would evade the scan.  This script hunts for
such a surface with an instrument that is not star-shaped-about-a-scan-ray:
the trial surface is r = h(theta, phi) about a centre, h expanded in real
spherical harmonics to --lmax, and the expansion of THAT surface (level-set
normal, not the radial one) is driven to zero by a Gundlach-style fast flow.

    F(x)      = r(x) - h(theta(x), phi(x));  the surface is F = 0
    s_a       propto  D_a F  (unit gamma-normal of the level set)
    theta_pm  = +- div(s) + K_ab s^a s^b - K   on the physical gamma = h / chi
    flow      a_lm <- a_lm - step / (1 + damp * l(l+1)) * Theta_lm

Orientation is by areal radius, as in the star-shaped scan: the outward side
of the surface is the side on which the area of the scaled surface (1+eps) h
grows, so theta_out is theta_+ when that side is +F and theta_- otherwise --
the same correction that killed the naive-orientation "dissolving horizon".

A converged flow (rms theta_out -> 0 with theta_in < 0) is a MOTS whatever
its shape; a flow that dives to the inner floor, runs out of the box or
stalls at finite rms theta has found nothing.  Absence-of-evidence caveat:
the flow is local -- a seed family (--seeds) stands in for a global search,
and lmax bounds the deformations reachable.  Both bounds are printed.

Self-tests (no plotfile, run first, --analytic all):
  schw    Kerr-Schild Schwarzschild, M = 0.5: must converge to R = 2M = 1,
          M_MS = M, from spherical AND deformed seeds, at lmax 0 and 4.
  ellis   time-symmetric Ellis throat, b = 1: every seed must FAIL to
          converge (no MOTS exists), the classic naive-orientation trap.

Plotfile validation (referee queue R0, before the spiral slice is read):
  the head-on remnant at t = 100 (merge_headon_flip_d8_v1_lvl5from0_scalar
  Plt10000) carries a known, star-shaped-scan-confirmed MOTS; the finder
  must reproduce its areal radius and Misner-Sharp mass.

Usage:
  python ah_flow_finder.py --analytic all
  python ah_flow_finder.py --plotfile PLT --centre 64 64 64 [--centre-snap]
         [--level 3] [--half 3.0] [--lmax 4] [--seeds 0.6 1.0 1.5 2.2 3.0]
         [--deformed-seeds]
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass

import numpy as np

sys.path.insert(
    0,
    str(__import__("pathlib").Path(__file__).resolve().parents[1] / "src"),
)

from grteclyn_wrapper.visualisation.process_wave.consume_plotfiles.extraction.horizon import (  # noqa: E402
    STATE_FIELDS,
    covering_fields,
)

_SYM = ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))


# --------------------------------------------------------------------------
# real spherical harmonics on (theta, phi) grids and on the covering grid
# --------------------------------------------------------------------------


def _real_ylm_pairs(lmax: int) -> list[tuple[int, int]]:
    return [(l, m) for l in range(lmax + 1) for m in range(-l, l + 1)]


def _real_ylm(l: int, m: int, th: np.ndarray, ph: np.ndarray) -> np.ndarray:
    """Real orthonormal spherical harmonic (Condon-Shortley absorbed)."""
    from scipy.special import sph_harm_y  # scipy >= 1.15: (l, m, theta, phi)

    if m == 0:
        return np.real(sph_harm_y(l, 0, th, ph))
    if m > 0:
        return math.sqrt(2.0) * np.real(sph_harm_y(l, m, th, ph))
    return math.sqrt(2.0) * np.imag(sph_harm_y(l, -m, th, ph))


@dataclass
class Box:
    """Precomputed geometry of one covering box (centre-relative coords)."""

    dx: float
    half: float
    gam_inv: np.ndarray  # (3, 3, N, N, N)
    Kphys: np.ndarray  # (3, 3, N, N, N)
    K: np.ndarray
    chi: np.ndarray
    h: np.ndarray  # (3, 3, N, N, N) conformal metric
    sqg: np.ndarray
    r: np.ndarray
    ylm_grid: np.ndarray  # (n_lm, N, N, N): Y_lm(theta(x), phi(x))
    pairs: list[tuple[int, int]]


def build_box(fields: dict[str, np.ndarray], dx: float, half: float, lmax: int) -> Box:
    chi = np.clip(np.asarray(fields["chi"], dtype=np.float64), 1.0e-12, None)
    K = np.asarray(fields["K"], dtype=np.float64)
    N = chi.shape[0]
    h = np.empty((3, 3) + chi.shape)
    A = np.empty_like(h)
    for a, b in _SYM:
        h[a, b] = h[b, a] = np.asarray(fields[f"h{a + 1}{b + 1}"], dtype=np.float64)
        A[a, b] = A[b, a] = np.asarray(fields[f"A{a + 1}{b + 1}"], dtype=np.float64)
    hi = np.empty_like(h)
    for a in range(3):
        for b in range(3):
            hi[a, b] = (
                h[(a + 1) % 3, (b + 1) % 3] * h[(a + 2) % 3, (b + 2) % 3]
                - h[(a + 1) % 3, (b + 2) % 3] * h[(a + 2) % 3, (b + 1) % 3]
            )
    gam_inv = chi * hi
    Kphys = (A + h * (K / 3.0)) / chi
    ax = np.arange(N) * dx + dx / 2.0 - half
    X = np.stack(np.meshgrid(ax, ax, ax, indexing="ij"))
    r = np.clip(np.sqrt((X**2).sum(0)), 1.0e-10, None)
    theta = np.arccos(np.clip(X[2] / r, -1.0, 1.0))
    phi = np.mod(np.arctan2(X[1], X[0]), 2.0 * math.pi)
    pairs = _real_ylm_pairs(lmax)
    ylm_grid = np.stack([_real_ylm(l, m, theta, phi) for l, m in pairs])
    return Box(
        dx=dx,
        half=half,
        gam_inv=gam_inv,
        Kphys=Kphys,
        K=K,
        chi=chi,
        h=h,
        sqg=chi**-1.5,
        r=r,
        ylm_grid=ylm_grid,
        pairs=pairs,
    )


# --------------------------------------------------------------------------
# expansion of the level-set surface F = r - h(theta, phi)
# --------------------------------------------------------------------------


@dataclass
class SurfaceState:
    theta_out: np.ndarray  # (nth, nph) on the quadrature grid
    theta_in: np.ndarray
    R_areal: float
    M_MS: float
    h_min: float
    h_max: float
    outward_is_plus_F: bool


def _quadrature(nth: int, nph: int):
    th = np.linspace(0.02, math.pi - 0.02, nth)
    ph = np.linspace(0.0, 2.0 * math.pi, nph, endpoint=False)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    nvec = np.stack([np.sin(TH) * np.cos(PH), np.sin(TH) * np.sin(PH), np.cos(TH)])
    return th, ph, TH, PH, nvec


def _surface_area(box: Box, hgrid: np.ndarray, th, ph, nvec) -> float:
    """Area of r = h(theta, phi) with the induced physical 2-metric."""
    from scipy.ndimage import map_coordinates

    pts = nvec * hgrid[None, :, :]
    idx = (pts + box.half) / box.dx - 0.5
    flat = idx.reshape(3, -1)
    chi_s = map_coordinates(box.chi, flat, order=1).reshape(hgrid.shape)
    gS = np.empty((3, 3) + hgrid.shape)
    for a, b in _SYM:
        gS[a, b] = gS[b, a] = (
            map_coordinates(box.h[a, b], flat, order=1).reshape(hgrid.shape) / chi_s
        )
    dth = np.gradient(pts, th, axis=1)
    dph = np.gradient(pts, ph, axis=2)
    E = np.einsum("abtp,atp,btp->tp", gS, dth, dth)
    F2 = np.einsum("abtp,atp,btp->tp", gS, dth, dph)
    G = np.einsum("abtp,atp,btp->tp", gS, dph, dph)
    dA = np.sqrt(np.clip(E * G - F2 * F2, 0.0, None))
    return float(dA.sum() * (th[1] - th[0]) * (ph[1] - ph[0]))


def surface_expansion(
    box: Box, a_lm: np.ndarray, nth: int = 32, nph: int = 64
) -> SurfaceState:
    from scipy.ndimage import map_coordinates

    th, ph, TH, PH, nvec = _quadrature(nth, nph)
    ylm_q = np.stack([_real_ylm(l, m, TH, PH) for l, m in box.pairs])
    hgrid = np.einsum("k,ktp->tp", a_lm, ylm_q)
    if hgrid.min() <= 3.0 * box.dx or hgrid.max() >= box.half - 2.0 * box.dx:
        raise FloatingPointError("surface left the box or hit the inner floor")

    # F = r - h(theta, phi) as a 3D field; its level set F = 0 is the surface
    hfield = np.einsum("k,kxyz->xyz", a_lm, box.ylm_grid)
    F = box.r - hfield
    dF = np.stack(np.gradient(F, box.dx))
    si = np.einsum("ab...,b...->a...", box.gam_inv, dF)
    lam = np.sqrt(np.clip(np.einsum("a...,a...->...", si, dF), 1.0e-30, None))
    si = si / lam
    div = sum(np.gradient(box.sqg * si[a], box.dx, axis=a) for a in range(3)) / box.sqg
    KSS = np.einsum("ab...,a...,b...->...", box.Kphys, si, si)
    theta_plus = div + KSS - box.K  # l = n + s(+F)
    theta_minus = -div + KSS - box.K  # k = n - s(+F)

    pts = nvec * hgrid[None, :, :]
    idx = (pts + box.half) / box.dx - 0.5
    flat = idx.reshape(3, -1)
    Tp = map_coordinates(theta_plus, flat, order=1).reshape(hgrid.shape)
    Tm = map_coordinates(theta_minus, flat, order=1).reshape(hgrid.shape)

    # orientation: outward = the side on which the areal radius grows
    area = _surface_area(box, hgrid, th, ph, nvec)
    area_out = _surface_area(box, hgrid * 1.02, th, ph, nvec)
    outward_is_plus_F = bool(area_out >= area)
    T_out = Tp if outward_is_plus_F else Tm
    T_in = Tm if outward_is_plus_F else Tp

    R_areal = math.sqrt(area / (4.0 * math.pi))
    M_MS = 0.5 * R_areal * (1.0 + R_areal**2 * float((Tp * Tm).mean()) / 4.0)
    return SurfaceState(
        theta_out=T_out,
        theta_in=T_in,
        R_areal=R_areal,
        M_MS=M_MS,
        h_min=float(hgrid.min()),
        h_max=float(hgrid.max()),
        outward_is_plus_F=outward_is_plus_F,
    )


# --------------------------------------------------------------------------
# the fast flow
# --------------------------------------------------------------------------


@dataclass
class FlowResult:
    converged: bool
    reason: str
    steps: int
    rms_theta: float
    max_abs_theta: float
    theta_in_max: float
    R_areal: float
    M_MS: float
    h_min: float
    h_max: float
    deform: float  # max |a_lm| over l >= 1, in units of a_00 Y_00 (the radius)
    a_lm: np.ndarray


def flow(
    box: Box,
    r_seed: float,
    seed_deform: float = 0.0,
    nth: int = 32,
    nph: int = 64,
    steps: int = 400,
    step_size: float = 0.15,
    damp: float = 0.5,
    tol: float = 2.0e-3,
) -> FlowResult:
    """Drive r = h(theta, phi) toward theta_out = 0 by the smoothed flow."""
    th, ph, TH, PH, _ = _quadrature(nth, nph)
    ylm_q = np.stack([_real_ylm(l, m, TH, PH) for l, m in box.pairs])
    w = np.sin(TH) * (th[1] - th[0]) * (ph[1] - ph[0])  # quadrature weights

    a = np.zeros(len(box.pairs))
    a[0] = r_seed * math.sqrt(4.0 * math.pi)  # a_00 Y_00 = r_seed
    if seed_deform != 0.0 and len(a) > 4:
        a[4] = seed_deform * a[0]  # an l = 2 dent to break sphericity

    ls = np.array([l for l, _ in box.pairs], dtype=float)
    gain = step_size / (1.0 + damp * ls * (ls + 1.0))
    state = None
    for k in range(steps):
        try:
            state = surface_expansion(box, a, nth, nph)
        except FloatingPointError as err:
            return FlowResult(
                False, str(err), k, math.nan, math.nan, math.nan,
                math.nan, math.nan, math.nan, math.nan, math.nan, a,
            )
        rms = float(np.sqrt(np.mean(state.theta_out**2)))
        scale = float(np.mean(np.abs(state.theta_out))) + 1.0e-12
        if rms < tol:
            deform = float(np.max(np.abs(a[1:]))) / abs(a[0]) if a.size > 1 else 0.0
            return FlowResult(
                bool(float(state.theta_in.max()) < 0.0),
                "theta_out -> 0"
                + ("" if float(state.theta_in.max()) < 0.0 else " but theta_in >= 0"),
                k, rms, float(np.max(np.abs(state.theta_out))),
                float(state.theta_in.max()), state.R_areal, state.M_MS,
                state.h_min, state.h_max, deform, a,
            )
        # project theta_out on the basis and step against it; the sign is
        # fixed by the orientation so the flow always moves the surface
        # toward the trapped side
        T_lm = np.einsum("tp,ktp->k", state.theta_out * w, ylm_q)
        sgn = 1.0 if state.outward_is_plus_F else -1.0
        a = a - sgn * gain * T_lm * min(1.0, 0.5 / scale)
    deform = float(np.max(np.abs(a[1:]))) / abs(a[0]) if a.size > 1 else 0.0
    rms = float(np.sqrt(np.mean(state.theta_out**2))) if state else math.nan
    return FlowResult(
        False, "flow stalled (no MOTS reached)", steps, rms,
        float(np.max(np.abs(state.theta_out))) if state else math.nan,
        float(state.theta_in.max()) if state else math.nan,
        state.R_areal if state else math.nan, state.M_MS if state else math.nan,
        state.h_min if state else math.nan, state.h_max if state else math.nan,
        deform, a,
    )


# --------------------------------------------------------------------------
# analytic self-tests (mirrors tests/visualisation/test_horizon_scan.py)
# --------------------------------------------------------------------------


def _conformal_fields(gamma: np.ndarray, Kij: np.ndarray) -> dict:
    det = np.linalg.det(np.moveaxis(gamma, (0, 1), (-2, -1)))
    chi = det ** (-1.0 / 3.0)
    h = chi * gamma
    ginv = np.moveaxis(np.linalg.inv(np.moveaxis(gamma, (0, 1), (-2, -1))), (-2, -1), (0, 1))
    K = np.einsum("ab...,ab...->...", ginv, Kij)
    A = chi * (Kij - gamma * (K / 3.0))
    f = {"chi": chi, "K": K}
    for a in range(3):
        for b in range(a, 3):
            f[f"h{a + 1}{b + 1}"] = h[a, b]
            f[f"A{a + 1}{b + 1}"] = A[a, b]
    assert set(f) == set(STATE_FIELDS)
    return f


def _grid(half: float, dx: float):
    N = int(round(2 * half / dx))
    ax = np.arange(N) * dx + dx / 2 - half
    X = np.stack(np.meshgrid(ax, ax, ax, indexing="ij"))
    r = np.clip(np.sqrt((X**2).sum(0)), 1e-6, None)
    return X, r


def analytic_schwarzschild(lmax: int) -> list[str]:
    M, half, dx = 0.5, 1.6, 0.04
    X, r = _grid(half, dx)
    n = X / r
    delta = np.eye(3)[:, :, None, None, None]
    nn = n[:, None] * n[None, :]
    gamma = delta + (2 * M / r) * nn
    alpha = 1.0 / np.sqrt(1.0 + 2 * M / r)
    Kij = (2 * M * alpha / r**2) * (delta - (2 + M / r) * nn)
    box = build_box(_conformal_fields(gamma, Kij), dx, half, lmax)
    out = []
    for r0, dent in ((1.3, 0.0), (0.8, 0.0), (1.2, 0.12)):
        res = flow(box, r0, seed_deform=dent)
        ok = res.converged and abs(res.R_areal - 2 * M) < 0.05 and abs(res.M_MS - M) < 0.04
        out.append(
            f"schw lmax={lmax} seed r0={r0} dent={dent}: "
            f"{'PASS' if ok else 'FAIL'} ({res.reason}, steps={res.steps}, "
            f"R={res.R_areal:.4f} vs 1.0, M_MS={res.M_MS:.4f} vs 0.5, "
            f"deform={res.deform:.2e}, theta_in_max={res.theta_in_max:+.3f})"
        )
        if not ok:
            out.append("  ** SELF-TEST FAILED **")
    return out


def analytic_ellis(lmax: int) -> list[str]:
    b, half, dx = 1.0, 1.6, 0.04
    X, r = _grid(half, dx)
    psi2 = 1.0 + b * b / (4.0 * r * r)
    chi = np.asarray(psi2**-2, dtype=np.float64)
    f = {k: np.zeros_like(chi) for k in STATE_FIELDS}
    f["chi"] = chi
    for k in ("h11", "h22", "h33"):
        f[k] = np.ones_like(chi)
    box = build_box(f, dx, half, lmax)
    out = []
    for r0 in (0.4, 0.7, 1.1):
        res = flow(box, r0)
        ok = not res.converged
        out.append(
            f"ellis lmax={lmax} seed r0={r0}: {'PASS (no MOTS)' if ok else 'FAIL'} "
            f"({res.reason}, steps={res.steps}, rms={res.rms_theta:.2e}, "
            f"h=[{res.h_min:.3f},{res.h_max:.3f}])"
        )
        if not ok:
            out.append("  ** SELF-TEST FAILED: found a MOTS on an Ellis throat **")
    return out


# --------------------------------------------------------------------------
# plotfile mode
# --------------------------------------------------------------------------


def snap_centre(ds, centre, level: int, half: float) -> np.ndarray:
    """Move the centre to the chi minimum of the surrounding box (the pit)."""
    fields, dx = covering_fields(ds, centre, half, level)
    chi = fields["chi"]
    k = np.unravel_index(int(np.argmin(chi)), chi.shape)
    off = (np.asarray(k, dtype=float) + 0.5) * dx - half
    return np.asarray(centre, dtype=float) + off


def run_plotfile(args) -> None:
    import yt

    yt.set_log_level(40)
    ds = yt.load(args.plotfile)
    t = float(ds.current_time)
    centre = np.asarray(args.centre, dtype=float)
    if args.centre_snap:
        centre = snap_centre(ds, centre, args.level, args.half)
        print(f"# centre snapped to the chi pit: {centre[0]:.4f} {centre[1]:.4f} {centre[2]:.4f}")
    fields, dx = covering_fields(ds, centre, args.half, args.level)
    box = build_box(fields, dx, args.half, args.lmax)
    print(
        f"# {args.plotfile}\n# t = {t:.4f}  centre = {centre.tolist()}  "
        f"level = {args.level} (dx = {dx:.5f})  half = {args.half}  lmax = {args.lmax}"
    )
    found = 0
    for r0 in args.seeds:
        variants = [(r0, 0.0)] + ([(r0, 0.12), (r0, -0.12)] if args.deformed_seeds else [])
        for rr, dent in variants:
            res = flow(box, rr, seed_deform=dent)
            tag = "MOTS" if res.converged else "none"
            print(
                f"seed r0={rr:<5} dent={dent:+.2f}: {tag:<4} {res.reason}; "
                f"steps={res.steps} rms_theta={res.rms_theta:.2e} "
                f"R_areal={res.R_areal:.4f} M_MS={res.M_MS:.4f} "
                f"h=[{res.h_min:.3f},{res.h_max:.3f}] deform={res.deform:.2e} "
                f"theta_in_max={res.theta_in_max:+.4f}"
            )
            found += int(res.converged)
    print(f"# surfaces found: {found} (seeds x variants exhausted; lmax = {args.lmax})")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--analytic", choices=["schw", "ellis", "all"], default=None)
    p.add_argument("--plotfile")
    p.add_argument("--centre", nargs=3, type=float, default=[64.0, 64.0, 64.0])
    p.add_argument("--centre-snap", action="store_true")
    p.add_argument("--level", type=int, default=3)
    p.add_argument("--half", type=float, default=3.0)
    p.add_argument("--lmax", type=int, default=4)
    p.add_argument("--seeds", nargs="+", type=float, default=[0.6, 1.0, 1.5, 2.2, 3.0])
    p.add_argument("--deformed-seeds", action="store_true")
    args = p.parse_args()
    if args.analytic:
        if args.analytic in ("schw", "all"):
            for line in analytic_schwarzschild(0) + analytic_schwarzschild(4):
                print(line)
        if args.analytic in ("ellis", "all"):
            for line in analytic_ellis(4):
                print(line)
        return
    if not args.plotfile:
        p.error("either --analytic or --plotfile is required")
    run_plotfile(args)


if __name__ == "__main__":
    main()
