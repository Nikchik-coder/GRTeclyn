#!/usr/bin/env python3
r"""The Hamiltonian constraint near the collapse horizon, computed directly (task C(c)(iii)).

The global norm the runs write (constraint_norms.dat) is an L2 average over the
level-0 grid (dx = 0.5, the whole box): a violation confined to the horizon
region is diluted by the volume ratio and hidden under the level-0 floor.
This computes the ADM Hamiltonian constraint of the plotfile state on a
covering grid about the throat,

    H = R[gamma] + K^2 - K_ij K^ij - 16 pi rho,   gamma_ij = h_ij / chi,
    K_ij = (A_ij + h_ij K / 3) / chi,   rho = -(Pi^2 + gamma^ij d_i phi d_j phi) / 2

(R[gamma] from the Christoffels of gamma_ij with fourth-order centred stencils),
and prints its shell averages against 16 pi |rho| on the same shells.
Validation: on the closed-form eps = 0 data H must vanish to truncation, on
eps = +1e-2 data it must reproduce the analytic seed violation (c_seed_constraints.py).

    OMP_NUM_THREADS=4 nice -n 19 grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/analysis/merger_feedback/c_local_hamiltonian.py \
        [--analytic EPS | PLT --centre X Y Z] [--level 4] [--half 2.3]
"""

from __future__ import annotations

import argparse
import math
import sys
import pathlib
import warnings

import numpy as np

warnings.filterwarnings("ignore")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c_horizon_first_law as fl  # noqa: E402

SYM = fl.SYM


def d1(f, h, ax):
    return (-np.roll(f, -2, ax) + 8 * np.roll(f, -1, ax) - 8 * np.roll(f, 1, ax) + np.roll(f, 2, ax)) / (12 * h)


def analytic(eps: float, half: float, dx: float) -> dict:
    A_, M_ = 2.0, 1.0
    rt = 0.5 * (M_ + math.sqrt(M_ * M_ + A_ * A_))
    C = math.sqrt(A_ * A_ + M_ * M_) / (A_ * math.sqrt(4 * math.pi))
    N = int(round(2 * half / dx))
    ax = np.arange(N) * dx + dx / 2 - half
    X, Y, Z = np.meshgrid(ax, ax, ax, indexing="ij")
    r = np.sqrt(X * X + Y * Y + Z * Z)
    Xx = (r - A_ * A_ / (4 * r)) / A_
    u = (M_ / A_) * (np.arctan(Xx) - math.pi / 2)
    om = 1 + A_ * A_ / (4 * r * r)
    g = np.exp(-((r - rt) / 0.5) ** 2)
    psi = np.sqrt(om) * (1 + eps * g)
    F = dict(chi=np.exp(2 * u) / psi**4, K=0 * r, lapse=np.exp(u), phi=C * np.arctan(Xx), Pi=0 * r)
    for a, b in SYM:
        F[f"h{a+1}{b+1}"] = (1.0 if a == b else 0.0) + 0 * r
        F[f"A{a+1}{b+1}"] = 0 * r
    return F


def hamiltonian(F: dict, dx: float) -> tuple[np.ndarray, np.ndarray]:
    chi = np.clip(F["chi"], 1e-12, None)
    g = np.empty((3, 3) + chi.shape)
    for a, b in SYM:
        g[a, b] = g[b, a] = F[f"h{a+1}{b+1}"] / chi
    gi = np.linalg.inv(np.moveaxis(g, (0, 1), (-2, -1)))
    gi = np.moveaxis(gi, (-2, -1), (0, 1))
    dg = np.stack([d1(g, dx, 2 + c) for c in range(3)])          # dg[c,a,b] = d_c g_ab
    # Gamma^k_ij = 1/2 g^kl (d_i g_jl + d_j g_il - d_l g_ij)
    low = 0.5 * (np.einsum("ijl...->lij...", dg) + np.einsum("jil...->lij...", dg) - dg)  # low[l,i,j]
    Gam = np.einsum("kl...,lij...->kij...", gi, low)
    del low
    dGam = np.stack([d1(Gam, dx, 3 + c) for c in range(3)])      # dGam[c,k,i,j]
    Ric = (np.einsum("kkij...->ij...", dGam) - np.einsum("jkik...->ij...", dGam)
           + np.einsum("kkl...,lij...->ij...", Gam, Gam) - np.einsum("kjl...,lik...->ij...", Gam, Gam))
    del dGam
    Rs = np.einsum("ij...,ij...->...", gi, Ric)
    Kt = F["K"]
    Kij = np.empty_like(g)
    for a, b in SYM:
        Kij[a, b] = Kij[b, a] = (F[f"A{a+1}{b+1}"] + F[f"h{a+1}{b+1}"] * Kt / 3.0) / chi
    KUU = np.einsum("ia...,jb...,ab...->ij...", gi, gi, Kij)
    trK = np.einsum("ij...,ij...->...", gi, Kij)
    dphi = np.stack([d1(F["phi"], dx, c) for c in range(3)])
    gphi2 = np.einsum("ab...,a...,b...->...", gi, dphi, dphi)
    rho = -0.5 * (F["Pi"] ** 2 + gphi2)
    H = Rs + trK**2 - np.einsum("ij...,ij...->...", Kij, KUU) - 16 * math.pi * rho
    return H, rho


def shell_avg(q: np.ndarray, dx: float, half: float, rs: np.ndarray) -> np.ndarray:
    N = q.shape[0]
    ax = np.arange(N) * dx + dx / 2 - half
    X, Y, Z = np.meshgrid(ax, ax, ax, indexing="ij")
    r = np.sqrt(X * X + Y * Y + Z * Z)
    out = np.empty(rs.size)
    for k, r0 in enumerate(rs):
        sel = np.abs(r - r0) < 0.5 * dx
        sel[:3] = sel[-3:] = False; sel[:, :3] = sel[:, -3:] = False; sel[:, :, :3] = sel[:, :, -3:] = False
        out[k] = q[sel].mean() if sel.any() else np.nan
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plt", nargs="?")
    ap.add_argument("--analytic", type=float, default=None)
    ap.add_argument("--centre", nargs=3, type=float, default=[64, 64, 64])
    ap.add_argument("--level", type=int, default=4)
    ap.add_argument("--half", type=float, default=2.3)
    ap.add_argument("--dx", type=float, default=1 / 32)
    ap.add_argument("--rmin", type=float, default=0.8)
    ap.add_argument("--rstep", type=float, default=0.1)
    args = ap.parse_args()
    if args.analytic is not None:
        dx, t = args.dx, 0.0
        F = analytic(args.analytic, args.half, dx)
        label = f"closed form eps={args.analytic:+g}"
    else:
        F, dx, t = fl.load(args.plt, np.array(args.centre), args.half, args.level)
        label = f"{args.plt.rstrip('/').split('/')[-1]} level {args.level}"
    H, rho = hamiltonian(F, dx)
    rs = np.arange(args.rmin, args.half - 0.2, args.rstep)
    Hs = shell_avg(H, dx, args.half, rs)
    Ha = shell_avg(np.abs(H), dx, args.half, rs)
    src = shell_avg(16 * math.pi * np.abs(rho), dx, args.half, rs)
    print(f"{label}  t={t:.2f}  dx={dx}")
    print("   r     <H>          <|H|>        <16 pi |rho|>   <H>/<16pi|rho|>")
    for k in range(rs.size):
        print(f"   {rs[k]:.2f}  {Hs[k]:+.4e}  {Ha[k]:.4e}   {src[k]:.4e}     {Hs[k]/src[k]:+.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
