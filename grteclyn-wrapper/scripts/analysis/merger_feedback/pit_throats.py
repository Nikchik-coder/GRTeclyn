#!/usr/bin/env python3
"""One throat or two?  Areal radius of coordinate spheres about each chi pit
and about their midpoint, on a binary-wormhole plotfile.

Why (2026-09-24, reviewer on Sec. VII.B): the paper's "still-open throat"
(R = 3.87) is the areal minimum of the oriented star scan, whose spheres are
centred on the box centre -- the merged pit.  Each wormhole carries its own
compactified far side at its chi pit (chi ~ r^4), and the in-code half-space
diagnostic still separates two pits at level 5 until chi floors (t ~ 58.4).
This script asks the geometry directly:

  R_mid(r)   spheres about the pits' midpoint: the common neck (the paper's
             number when the midpoint is the box centre)
  R_A(rho)   spheres about pit A alone (rho < |AB| encloses A only): a
             minimum there is a per-mouth throat resolved inside the neck
  L_AB       proper length of the straight segment between the pits (dominated
             by the pits' own depths -- a far side is a truncated infinity --
             so it is printed, not quoted)
  chi(AB)    chi along the segment: two pits are two minima with chi far higher
             between them; one pit would put the minimum at the midpoint
  R_A,off    spheres enclosing pit A but not pit B, centred on A or displaced
             AWAY from B: the smallest is a tighter upper bound on A's own throat

R is sqrt(area / 4 pi) with the area integrated from the FULL induced 2-metric
(gamma_ij = h_ij / chi), as in scripts/validation/ah_oriented_scan.py.  Two
interpolations of gamma onto the sphere are reported, because near a pit chi
changes by decades per cell: 'gam' interpolates gamma_ij linearly (what the
oriented scan does, so R_mid reproduces its numbers) and 'lnchi' interpolates
ln chi and h_ij and rebuilds gamma, which follows chi ~ r^4 far better.  Their
difference is the interpolation systematic of anything read within a few cells
of a pit.

    python pit_throats.py PLT [--level 5] [--half 1.25] [--centre 64 64 64]
                              [--json out.json]

Reads chi and h_ij only (no K, A_ij: no expansions -- areas only).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import warnings

import numpy as np

warnings.filterwarnings("ignore")
import yt  # noqa: E402
from scipy.ndimage import map_coordinates  # noqa: E402

yt.set_log_level(50)


def load(plt: str, level: int, centre: np.ndarray, half: float):
    ds = yt.load(plt)
    level = min(level, ds.index.max_level)
    dx = float(ds.index.get_smallest_dx()) * 2 ** (ds.index.max_level - level)
    n = int(round(2 * half / dx))
    half = n * dx / 2
    cg = ds.covering_grid(level, left_edge=centre - half, dims=[n] * 3)

    def f(name):
        return np.asarray(cg[("boxlib", name)], dtype=np.float64)

    chi = np.clip(f("chi"), 1e-14, None)
    h = {}
    for a in range(3):
        for b in range(a, 3):
            h[(a, b)] = f(f"h{a + 1}{b + 1}")
    return ds, level, dx, n, half, chi, h


def cell_coords(n: int, dx: float, half: float) -> np.ndarray:
    return np.arange(n) * dx + dx / 2 - half


def find_pits(chi: np.ndarray, dx: float, half: float, rmax: float = 0.8):
    """Two pits: the chi minimum in x < 0 and in x > 0 (the in-code binary
    diagnostic's split, binary_diag_axis = 0), within rmax of the centre.
    Floored cells are averaged (centroid of cells within 1 % of the minimum)."""
    ax = cell_coords(chi.shape[0], dx, half)
    X, Y, Z = np.meshgrid(ax, ax, ax, indexing="ij")
    inside = X ** 2 + Y ** 2 + Z ** 2 < rmax ** 2
    pits = []
    for side in (X < 0, X > 0):
        m = inside & side
        v = np.where(m, chi, np.inf)
        cmin = float(v.min())
        sel = m & (chi <= cmin * 1.01)
        pits.append((np.array([X[sel].mean(), Y[sel].mean(), Z[sel].mean()]),
                     cmin, int(sel.sum())))
    return pits


class Sampler:
    """Trilinear sampling of chi and h_ij at arbitrary points (grid-relative)."""

    def __init__(self, chi, h, dx, half):
        self.lnchi = np.log(chi)
        self.chi = chi
        self.h = h
        self.dx, self.half = dx, half
        self.gam = {k: v / chi for k, v in h.items()}

    def _idx(self, pts):
        return (pts + self.half) / self.dx - 0.5

    def gamma(self, pts, mode: str):
        idx = self._idx(pts.reshape(3, -1))
        out = {}
        if mode == "gam":
            for k, v in self.gam.items():
                out[k] = map_coordinates(v, idx, order=1, mode="nearest")
        else:
            c = np.exp(map_coordinates(self.lnchi, idx, order=1, mode="nearest"))
            for k, v in self.h.items():
                out[k] = map_coordinates(v, idx, order=1, mode="nearest") / c
        return {k: v.reshape(pts.shape[1:]) for k, v in out.items()}


def sphere_R(s: Sampler, c: np.ndarray, rs: np.ndarray, mode: str,
             nth: int = 41, nph: int = 80) -> np.ndarray:
    th = np.linspace(0.02, np.pi - 0.02, nth)
    ph = np.linspace(0, 2 * np.pi, nph, endpoint=False)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    nvec = np.stack([np.sin(TH) * np.cos(PH), np.sin(TH) * np.sin(PH), np.cos(TH)])
    out = np.empty(rs.size)
    for i, r in enumerate(rs):
        pts = c[:, None, None] + r * nvec
        g = s.gamma(pts, mode)
        G = np.empty((3, 3) + TH.shape)
        for (a, b), v in g.items():
            G[a, b] = G[b, a] = v
        dth = np.stack([np.cos(TH) * np.cos(PH), np.cos(TH) * np.sin(PH), -np.sin(TH)]) * r
        dph = np.stack([-np.sin(TH) * np.sin(PH), np.sin(TH) * np.cos(PH), 0 * TH]) * r
        E = np.einsum("ab...,a...,b...->...", G, dth, dth)
        F = np.einsum("ab...,a...,b...->...", G, dth, dph)
        Gg = np.einsum("ab...,a...,b...->...", G, dph, dph)
        dA = np.sqrt(np.clip(E * Gg - F * F, 0, None))
        area = dA.sum() * (th[1] - th[0]) * (ph[1] - ph[0])
        out[i] = np.sqrt(area / (4 * np.pi))
    return out


def minima(rs, R):
    d = np.gradient(R, rs)
    return [(float(rs[k]), float(R[k])) for k in range(1, rs.size - 1)
            if d[k - 1] < 0 <= d[k + 1] and R[k] <= R[k - 1] and R[k] <= R[k + 1]]


def proper_length(s: Sampler, a: np.ndarray, b: np.ndarray, mode: str, n: int = 400) -> float:
    u = np.linspace(0.0, 1.0, n)
    pts = a[:, None] + (b - a)[:, None] * u[None, :]
    g = s.gamma(pts[:, :, None], mode)
    t = b - a
    ds2 = sum(g[(i, j)][:, 0] * t[i] * t[j] * (1 if i == j else 2)
              for (i, j) in g)
    return float(np.trapezoid(np.sqrt(np.clip(ds2, 0, None)), u))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plt")
    ap.add_argument("--level", type=int, default=5)
    ap.add_argument("--half", type=float, default=1.25)
    ap.add_argument("--centre", nargs=3, type=float, default=[64.0, 64.0, 64.0])
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)

    t0 = time.time()
    centre = np.array(args.centre)
    ds, level, dx, n, half, chi, h = load(args.plt, args.level, centre, args.half)
    tsim = float(ds.current_time)
    print(f"# {args.plt}\n# t = {tsim:.3f}  level {level}  dx = {dx:.5f}  "
          f"box half-width {half:.3f} ({n}^3)  load {time.time() - t0:.0f} s", flush=True)
    s = Sampler(chi, h, dx, half)
    pits = find_pits(chi, dx, half)
    A, B = pits[0][0], pits[1][0]
    sep = float(np.linalg.norm(A - B))
    mid = 0.5 * (A + B)
    for name, (p, cmin, ncell) in zip("AB", pits):
        print(f"  pit {name}: x = ({p[0]:+.4f}, {p[1]:+.4f}, {p[2]:+.4f}) rel. centre, "
              f"min chi = {cmin:.3e} over {ncell} cells")
    print(f"  coordinate separation |AB| = {sep:.4f} ({sep / dx:.1f} cells); midpoint "
          f"({mid[0]:+.4f}, {mid[1]:+.4f}, {mid[2]:+.4f})")
    res = {"plotfile": args.plt, "t": tsim, "level": level, "dx": dx,
           "pits": [p[0].tolist() for p in pits], "pit_chi": [p[1] for p in pits],
           "sep": sep}
    for mode in ("gam", "lnchi"):
        L = proper_length(s, A, B, mode)
        print(f"  [{mode}] proper length of the segment AB = {L:.3f}")
        res[f"L_AB_{mode}"] = L

    rmax = half - 0.12
    rs_mid = np.arange(dx / 2, rmax, dx / 2)
    for cname, c in (("box centre", np.zeros(3)), ("midpoint", mid)):
        for mode in ("gam", "lnchi"):
            R = sphere_R(s, c, rs_mid, mode)
            mins = minima(rs_mid, R)
            # the common neck: the minimum at the largest r (outermost)
            print(f"  [{mode}] spheres about the {cname}: areal minima "
                  + ", ".join(f"R = {Rm:.3f} at r = {rm:.3f}" for rm, Rm in mins))
            res[f"mid_{cname.replace(' ', '_')}_{mode}"] = {"r": rs_mid.tolist(), "R": R.tolist(),
                                                           "minima": mins}
    for name, p in zip("AB", (A, B)):
        rho_max = min(rmax - np.abs(p).max(), 1.6 * sep)
        rs = np.arange(dx / 4, rho_max, dx / 4)
        for mode in ("gam", "lnchi"):
            R = sphere_R(s, p, rs, mode)
            inside = rs < sep
            mins = [m for m in minima(rs, R) if m[0] < sep]
            k = int(np.argmin(R[inside])) if inside.any() else 0
            print(f"  [{mode}] spheres about pit {name} (rho < |AB| = {sep:.3f} enclose it alone): "
                  f"min R = {R[inside].min():.3f} at rho = {rs[inside][k]:.4f}; interior minima "
                  + (", ".join(f"R = {Rm:.3f} at rho = {rm:.4f}" for rm, Rm in mins) or "none")
                  + f"; R(rho = |AB|/2) = {np.interp(sep / 2, rs, R):.3f}")
            prof = "  ".join(f"{rr:.3f}:{RR:.2f}" for rr, RR in zip(rs[::4], R[::4]))
            print(f"      R(rho) every {dx:.4f}: {prof}")
            res[f"pit{name}_{mode}"] = {"rho": rs.tolist(), "R": R.tolist(), "minima": mins}
    # chi along the segment through both pits
    u = np.linspace(0.0, 1.0, 21)
    seg = A[:, None] + (B - A)[:, None] * u[None, :]
    idx = (seg + half) / dx - 0.5
    cseg = np.exp(map_coordinates(np.log(chi), idx, order=1))
    print(f"  chi along AB (every 0.1 |AB|): " + " ".join(f"{c:.1e}" for c in cseg[::2])
          + f"; midpoint / pit = {cseg[10] / min(pits[0][1], pits[1][1]):.0f}")
    res["chi_AB"] = cseg.tolist()
    # displaced-centre spheres enclosing A alone
    uAB = (A - B) / sep
    best = None
    for sh in (0.0, 0.05, 0.1, 0.2, 0.3, 0.45):
        c = A + sh * uAB
        dB = float(np.linalg.norm(c - B))
        if np.abs(c).max() + dB > half - 0.05:
            continue
        rs = np.arange(sh + dx, dB - dx / 2, dx / 4)
        if rs.size < 3:
            continue
        for mode in ("gam", "lnchi"):
            R = sphere_R(s, c, rs, mode)
            k = int(np.argmin(R))
            print(f"  [{mode}] centre shifted {sh:.2f} from pit A away from B: min R over spheres "
                  f"enclosing A alone = {R[k]:.3f} at rho = {rs[k]:.3f} (companion at {dB:.3f})")
            if mode == "lnchi" and (best is None or R[k] < best[0]):
                best = (float(R[k]), sh, float(rs[k]))
    if best:
        print(f"  => tightest sphere bound on pit A's own throat: R <= {best[0]:.2f} "
              f"(lnchi; shift {best[1]}, rho {best[2]:.3f})")
        res["pitA_offset_bound"] = best
    print(f"# done in {time.time() - t0:.0f} s", flush=True)
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(res, fh)
    return 0


if __name__ == "__main__":
    sys.exit(main())
