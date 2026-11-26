"""Orientation-corrected marginal-surface scan, one pass per plotfile.

Why this exists (research/merger/archive/GPU_PLAN_UPDATED_2026-09-08.md, Defect 2): the historic
apparent-horizon scan takes "outward" to be +d/dr on every coordinate sphere.
Inside a wormhole throat that direction points toward the OTHER mouth, where
the areal radius DEcreases, so the scan computes the ingoing expansion, calls
every throat interior "trapped", and the black-hole claim built on it is void.

This pass fixes the orientation by construction, on shells about each centre:

  R(r)        areal radius sqrt(Area / 4 pi) of the coordinate sphere r, the
              area integrated with the full induced 2-metric (gamma = h / chi)
  outward     the side on which R increases: +d/dr where dR/dr > 0, -d/dr
              where dR/dr < 0 (inside a throat)
  theta_out   expansion of the outgoing null normal  l = n + s_out
  theta_in    expansion of the ingoing  null normal  k = n - s_out
  M_MS(r)     Misner-Sharp mass, 2 M / R = 1 + R^2 theta_out theta_in / 4
              (orientation-free: the product is symmetric under s -> -s)

and reports, per centre and per plotfile, one row of horizon_scan.dat:

  R_min, r_at_R_min      the corrected areal minimum (the throat radius; the
                         consumer's r / sqrt(chi) proxy reads ~20 % high)
  dev, log10_abs_dev     per-mouth health metric R_min / R_exact - 1, and its
                         decimal log (INSTABILITY.md's deviation, per throat)
  n_mots, r/R/M_MS_mots  outermost marginally outer-trapped surface (MOTS):
                         max theta_out crosses 0 with theta_in < 0
  theta_out/in at R_min  both expansions on the minimal surface: a healthy
                         throat has theta_out * theta_in ~ 0 (Hochberg-Visser
                         anti-trapped, not trapped)
  n_trapped              shells with theta_out <= 0 AND theta_in <= 0 (inside
                         a black hole); n_anti_trapped likewise for >= 0
  n_outermost            outermost-surface count over the whole plotfile:
                         1 when the common (midpoint) scan finds a MOTS
                         enclosing both mouths, else the number of mouths
                         with their own MOTS -- the gauge-free merger
                         criterion is this count going 2 -> 1

Own module, own output file, default off (--horizon-scan); nothing in the
other .dat contracts changes.  The shell mathematics is the validated
scripts/validation/ah_oriented_scan.py (2026-09-08), lifted into functions
so it can be unit-tested on analytic data (Schwarzschild finds its horizon at
R = 2M with M_MS = M; an Ellis throat has no MOTS and no trapped shell).

Needs the full state in the plotfile: chi, K, h_ij, A_ij.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np

HORIZON_HEADER = (
    "# time  centre  cx  cy  cz  R_min  r_at_R_min  dev  log10_abs_dev  "
    "n_mots  r_mots  R_mots  M_MS_mots  theta_out_min_inside  theta_out_max_at_R_min  "
    "theta_in_max_at_R_min  n_trapped  n_anti_trapped  n_outermost"
)

STATE_FIELDS = (
    "chi",
    "K",
    "h11",
    "h12",
    "h13",
    "h22",
    "h23",
    "h33",
    "A11",
    "A12",
    "A13",
    "A22",
    "A23",
    "A33",
)

_SYM = ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))


@dataclass
class ShellScan:
    """Per-shell statistics of one centre (arrays over the shell radii rs)."""

    rs: np.ndarray
    R: np.ndarray
    dRdr: np.ndarray
    out_min: np.ndarray
    out_max: np.ndarray
    in_min: np.ndarray
    in_max: np.ndarray
    M_MS: np.ndarray
    naive_trapped: np.ndarray  # +r orientation would call the shell trapped


@dataclass
class ShellSummary:
    R_min: float
    r_at_min: float
    n_mots: int
    r_mots: float
    R_mots: float
    M_MS_mots: float
    theta_out_min_inside: float  # most negative theta_out inside the MOTS: its depth
    theta_out_max_at_min: float
    theta_in_max_at_min: float
    n_trapped: int
    n_anti_trapped: int


def _shell_geometry(
    rs: np.ndarray, nth: int, nph: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    th = np.linspace(0.02, math.pi - 0.02, nth)
    ph = np.linspace(0.0, 2.0 * math.pi, nph, endpoint=False)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    nvec = np.stack([np.sin(TH) * np.cos(PH), np.sin(TH) * np.sin(PH), np.cos(TH)])
    pts = nvec[:, None] * rs[None, :, None, None]  # (3, nr, nth, nph)
    return th, ph, nvec, pts


def oriented_shell_scan(
    fields: dict[str, np.ndarray],
    dx: float,
    half: float,
    rmin: float = 0.25,
    dr: float = 0.02,
    nth: int = 25,
    nph: int = 48,
) -> ShellScan:
    """Scan coordinate spheres about the box centre with the corrected orientation.

    ``fields`` maps each STATE_FIELDS name to an (N, N, N) array covering the
    cube [-half, half]^3 about the centre, cell centres at -half + (i + 1/2) dx.
    """
    from scipy.ndimage import map_coordinates

    chi = np.clip(np.asarray(fields["chi"], dtype=np.float64), 1.0e-12, None)
    K = np.asarray(fields["K"], dtype=np.float64)
    N = chi.shape[0]
    if chi.shape != (N, N, N):
        raise ValueError("horizon scan needs a cubic covering box")

    h = np.empty((3, 3) + chi.shape)
    A = np.empty_like(h)
    for a, b in _SYM:
        h[a, b] = h[b, a] = np.asarray(fields[f"h{a + 1}{b + 1}"], dtype=np.float64)
        A[a, b] = A[b, a] = np.asarray(fields[f"A{a + 1}{b + 1}"], dtype=np.float64)

    # inverse of h via the adjugate (det h = 1)
    hi = np.empty_like(h)
    for a in range(3):
        for b in range(3):
            hi[a, b] = (
                h[(a + 1) % 3, (b + 1) % 3] * h[(a + 2) % 3, (b + 2) % 3]
                - h[(a + 1) % 3, (b + 2) % 3] * h[(a + 2) % 3, (b + 1) % 3]
            )
    gam_inv = chi * hi
    Kphys = (A + h * (K / 3.0)) / chi
    del A

    ax = np.arange(N) * dx + dx / 2.0 - half
    X = np.stack(np.meshgrid(ax, ax, ax, indexing="ij"))
    r = np.clip(np.sqrt((X**2).sum(0)), 1.0e-10, None)
    drv = X / r
    del X
    si = np.einsum("ab...,b...->a...", gam_inv, drv)
    lam = np.sqrt(np.clip(np.einsum("a...,a...->...", si, drv), 1.0e-30, None))
    si /= lam  # unit gamma-normal of r = const, pointing +r
    del gam_inv, drv, lam
    sqg = chi**-1.5
    div = sum(np.gradient(sqg * si[a], dx, axis=a) for a in range(3)) / sqg
    KSS = np.einsum("ab...,a...,b...->...", Kphys, si, si)
    del Kphys, si, sqg
    theta_plus_r = div + KSS - K  # l = n + s(+r)
    theta_minus_r = -div + KSS - K  # k = n - s(+r)
    del div, KSS

    rs = np.arange(rmin, half - 0.2, dr)
    if rs.size < 3:
        raise ValueError("horizon scan: box too small for the shell range")
    th, ph, _nvec, pts = _shell_geometry(rs, nth, nph)
    idx = (pts + half) / dx - 0.5
    flat = idx.reshape(3, -1)

    def on_rays(field: np.ndarray) -> np.ndarray:
        return map_coordinates(field, flat, order=1).reshape(rs.size, nth, nph)

    Tp = on_rays(theta_plus_r)
    Tm = on_rays(theta_minus_r)
    chi_r = on_rays(chi)
    gS = np.empty((3, 3, rs.size, nth, nph))
    for a, b in _SYM:
        gS[a, b] = gS[b, a] = on_rays(h[a, b]) / chi_r

    # area of each coordinate sphere from its induced metric
    dth = np.gradient(pts, th, axis=2)
    dph = np.gradient(pts, ph, axis=3)
    E = np.einsum("abrtp,artp,brtp->rtp", gS, dth, dth)
    F = np.einsum("abrtp,artp,brtp->rtp", gS, dth, dph)
    G = np.einsum("abrtp,artp,brtp->rtp", gS, dph, dph)
    dA = np.sqrt(np.clip(E * G - F * F, 0.0, None))
    area = dA.sum(axis=(1, 2)) * (th[1] - th[0]) * (ph[1] - ph[0])
    R = np.sqrt(area / (4.0 * math.pi))
    dRdr = np.gradient(R, rs)
    outward_is_plus_r = dRdr >= 0.0

    theta_out = np.where(outward_is_plus_r[:, None, None], Tp, Tm)
    theta_in = np.where(outward_is_plus_r[:, None, None], Tm, Tp)
    prod = (Tp * Tm).mean(axis=(1, 2))
    M_MS = 0.5 * R * (1.0 + R**2 * prod / 4.0)

    return ShellScan(
        rs=rs,
        R=R,
        dRdr=dRdr,
        out_min=theta_out.min(axis=(1, 2)),
        out_max=theta_out.max(axis=(1, 2)),
        in_min=theta_in.min(axis=(1, 2)),
        in_max=theta_in.max(axis=(1, 2)),
        M_MS=M_MS,
        naive_trapped=Tp.max(axis=(1, 2)) <= 0.0,
    )


def summarise(scan: ShellScan) -> ShellSummary:
    """Minimal surface, outermost MOTS and trapped-shell counts of one scan."""
    k_min = int(np.argmin(scan.R))
    # A zero crossing of theta_out counts only where the outward direction is
    # the same on both shells.  Where dR/dr changes sign (a minimum or a
    # maximum of R(r)) the orientation itself flips between k and k + 1, and
    # theta_out flips sign with it whatever the geometry does; the level-4
    # lone throat at t = 100 (2026-09-08) put a fake "MOTS" of Misner-Sharp
    # mass 24 on the local maximum of R at r = 1.2 that way.
    sgn = np.sign(scan.dRdr)

    def same_orientation(k: int) -> bool:
        window = sgn[max(k - 1, 0) : k + 3]
        return bool(np.all(window == window[0]) and window[0] != 0.0)

    mots = [
        k
        for k in range(scan.rs.size - 1)
        if scan.out_max[k] <= 0.0 < scan.out_max[k + 1]
        and scan.in_max[k] < 0.0
        and same_orientation(k)
    ]
    if mots:
        k = mots[-1]
        frac = (-scan.out_max[k]) / (scan.out_max[k + 1] - scan.out_max[k])
        r_mots = float(scan.rs[k] + (scan.rs[k + 1] - scan.rs[k]) * frac)
        R_mots = float(np.interp(r_mots, scan.rs, scan.R))
        M_mots = float(np.interp(r_mots, scan.rs, scan.M_MS))
        # How trapped the inside is.  A crossing whose interior never gets
        # below a few per cent of the scan's typical |theta| is marginal --
        # the level-4 bag maximum read -0.005 against 0.2 elsewhere.
        depth = float(np.min(scan.out_max[: k + 1]))
    else:
        r_mots = R_mots = M_mots = depth = float("nan")
    trapped = (scan.out_max <= 0.0) & (scan.in_max <= 0.0)
    anti = (scan.out_min >= 0.0) & (scan.in_min >= 0.0)
    return ShellSummary(
        R_min=float(scan.R[k_min]),
        r_at_min=float(scan.rs[k_min]),
        n_mots=len(mots),
        r_mots=r_mots,
        R_mots=R_mots,
        M_MS_mots=M_mots,
        theta_out_min_inside=depth,
        theta_out_max_at_min=float(scan.out_max[k_min]),
        theta_in_max_at_min=float(scan.in_max[k_min]),
        n_trapped=int(trapped.sum()),
        n_anti_trapped=int(anti.sum()),
    )


def covering_fields(ds, centre: Sequence[float], half: float, level: int) -> tuple[dict, float]:
    """Full-state arrays on a cubic covering grid about ``centre`` (yt dataset)."""
    have = {f[1] for f in ds.field_list}
    missing = [v for v in STATE_FIELDS if v not in have]
    if missing:
        raise ValueError(f"plotfile lacks {missing}; the horizon scan needs the full state")
    level = int(min(level, ds.index.max_level))
    # dx MUST be the requested level's cell size (ah_radial_scan.py, 2026-09-04):
    # yt sizes a covering grid as dims * dds(level).
    dx = float(ds.index.get_smallest_dx()) * 2 ** (ds.index.max_level - level)
    N = int(round(2.0 * half / dx))
    cen = np.asarray(centre, dtype=float)
    cg = ds.covering_grid(level, left_edge=cen - half, dims=[N] * 3)
    fields = {name: np.asarray(cg[("boxlib", name)], dtype=np.float64) for name in STATE_FIELDS}
    return fields, dx


def scan_centre(
    ds,
    centre: Sequence[float],
    half: float,
    level: int,
    rmin: float,
    dr: float,
) -> ShellSummary:
    fields, dx = covering_fields(ds, centre, half, level)
    scan = oriented_shell_scan(fields, dx=dx, half=half, rmin=rmin, dr=dr)
    return summarise(scan)


def read_tracked_centres(track_path: str, t: float, grid_centre: Sequence[float]) -> list[tuple[str, np.ndarray]]:
    """Mouth positions at time t from binary_throat_diagnostics.dat.

    Column contract (in-code, BinaryWormholeLevel): time separation xA yA zA
    chiA_min lapseA_min xB yB zB chiB_min lapseB_min, positions RELATIVE to the
    grid centre.  Mouth B is dropped when its columns are absent or NaN.
    """
    data = np.loadtxt(track_path, comments="#", ndmin=2)
    if data.size == 0:
        raise ValueError(f"{track_path}: empty")
    i = int(np.argmin(np.abs(data[:, 0] - t)))
    row = data[i]
    gc = np.asarray(grid_centre, dtype=float)
    out = [("A", gc + row[2:5])]
    if row.size >= 10 and np.all(np.isfinite(row[7:10])):
        out.append(("B", gc + row[7:10]))
    return out


def resolve_centres(args_dict: dict, t: float) -> list[tuple[str, np.ndarray]]:
    track = args_dict.get("horizon_track")
    if track:
        return read_tracked_centres(track, t, args_dict["center"])
    explicit = args_dict.get("horizon_centers")
    if explicit:
        vals = [float(v) for v in explicit]
        if len(vals) % 3 != 0:
            raise ValueError("--horizon-centers takes triples x y z")
        labels = "ABCDEFGH"
        return [(labels[k], np.asarray(vals[3 * k : 3 * k + 3])) for k in range(len(vals) // 3)]
    return [("A", np.asarray(args_dict["center"], dtype=float))]


def horizon_block(ds, t: float, args_dict: dict) -> str:
    """All rows of horizon_scan.dat for one plotfile (mouths, then the common scan)."""
    centres = resolve_centres(args_dict, t)
    half = float(args_dict.get("horizon_half", 2.5))
    level = int(args_dict.get("horizon_level", 3))
    rmin = float(args_dict.get("horizon_rmin", 0.25))
    dr = float(args_dict.get("horizon_dr", 0.02))
    r_exact = args_dict.get("horizon_r_exact")

    rows: list[tuple[str, np.ndarray, ShellSummary]] = []
    for label, c in centres:
        rows.append((label, c, scan_centre(ds, c, half, level, rmin, dr)))

    common: ShellSummary | None = None
    common_centre = None
    sep = 0.0
    if len(centres) >= 2:
        (_, cA), (_, cB) = centres[0], centres[1]
        sep = float(np.linalg.norm(cA - cB))
        common_centre = 0.5 * (cA + cB)
        common_half = max(half, 0.5 * sep + half)
        common_level = int(args_dict.get("horizon_common_level", 1))
        common = scan_centre(ds, common_centre, common_half, common_level, max(rmin, 0.5 * sep), dr * 4)

    if common is not None and common.n_mots > 0 and common.r_mots > 0.5 * sep:
        n_outermost = 1
    else:
        n_outermost = sum(1 for _, _, s in rows if s.n_mots > 0)

    def fmt(label: str, c: np.ndarray, s: ShellSummary) -> str:
        if r_exact:
            dev = s.R_min / float(r_exact) - 1.0
            ldev = math.log10(abs(dev)) if dev != 0.0 else float("-inf")
        else:
            dev = ldev = float("nan")
        return (
            f"{t:.16e}  {label}  {c[0]:.6f}  {c[1]:.6f}  {c[2]:.6f}  "
            f"{s.R_min:.10e}  {s.r_at_min:.6f}  {dev:.6e}  {ldev:.4f}  "
            f"{s.n_mots}  {s.r_mots:.6f}  {s.R_mots:.6e}  {s.M_MS_mots:.6e}  {s.theta_out_min_inside:+.6e}  "
            f"{s.theta_out_max_at_min:+.6e}  {s.theta_in_max_at_min:+.6e}  "
            f"{s.n_trapped}  {s.n_anti_trapped}  {n_outermost}\n"
        )

    lines = [fmt(label, c, s) for label, c, s in rows]
    if common is not None:
        lines.append(fmt("C", common_centre, common))
    return "".join(lines)
