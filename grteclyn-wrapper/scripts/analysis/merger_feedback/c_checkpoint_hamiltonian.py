#!/usr/bin/env python3
r"""Hamiltonian constraint and CCZ4 Theta near the throat, read from AMReX CHECKPOINTS.

Checkpoints carry the whole evolved state -- including Theta and Gamma^i, which
the plotfiles do not -- so the constraint history of a live run can be read
from its rolling checkpoints (read-only; nothing on scratch is touched).
Reads one level of Level_<L>/SD_0_New_MF (VisMF: text FAB header + raw doubles,
ghost cells included), assembles the valid boxes into a cube about the centre,
and prints the shell averages of the ADM Hamiltonian constraint (same formula
as c_local_hamiltonian.py), of 16 pi |rho| and of Theta.

Component order (Source/CCZ4/CCZ4StateVariables.hpp + StateVariables.hpp):
chi h11 h12 h13 h22 h23 h33 K A11 A12 A13 A22 A23 A33 Theta Gamma1-3 lapse
shift1-3 B1-3 phi Pi.

    OMP_NUM_THREADS=4 nice -n 19 grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/analysis/merger_feedback/c_checkpoint_hamiltonian.py \
        CHK [CHK ...] --level 4 --centre 64 64 64 --half 2.25
"""

from __future__ import annotations

import argparse
import math
import pathlib
import re
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c_local_hamiltonian as lh  # noqa: E402

NAMES = (["chi", "h11", "h12", "h13", "h22", "h23", "h33", "K", "A11", "A12", "A13", "A22", "A23", "A33",
          "Theta", "Gamma1", "Gamma2", "Gamma3", "lapse", "shift1", "shift2", "shift3", "B1", "B2", "B3",
          "phi", "Pi"])


def read_level(chk: pathlib.Path, level: int, lo_idx: np.ndarray, n: int) -> tuple[np.ndarray, float]:
    """(ncomp, n, n, n) array of the level's valid data in the index cube [lo_idx, lo_idx + n)."""
    hdr = (chk / f"Level_{level}" / "SD_0_New_MF_H").read_text().splitlines()
    ncomp, ngrow = int(hdr[2]), int(hdr[3])
    boxes = [tuple(map(int, re.findall(r"-?\d+", l)[:6])) for l in hdr if l.startswith("((")]
    fods = [(l.split()[1], int(l.split()[2])) for l in hdr if l.startswith("FabOnDisk")]
    out = np.full((ncomp, n, n, n), np.nan)
    for (x0, y0, z0, x1, y1, z1), (fname, off) in zip(boxes, fods):
        with open(chk / f"Level_{level}" / fname, "rb") as fh:
            fh.seek(off)
            line = fh.readline().decode()
            gl = list(map(int, re.findall(r"\((-?\d+),(-?\d+),(-?\d+)\)", line)[0]))
            gh = list(map(int, re.findall(r"\((-?\d+),(-?\d+),(-?\d+)\)", line)[1]))
            nc = int(line.split()[-1])
            shape = [gh[d] - gl[d] + 1 for d in range(3)]
            data = np.fromfile(fh, dtype="<f8", count=nc * shape[0] * shape[1] * shape[2])
        data = data.reshape(nc, shape[2], shape[1], shape[0]).transpose(0, 3, 2, 1)   # (c, x, y, z)
        g = ngrow
        v = data[:, g:-g, g:-g, g:-g]                                                 # valid cells
        vlo = np.array([x0, y0, z0]); vhi = np.array([x1, y1, z1]) + 1
        a = np.maximum(vlo, lo_idx); b = np.minimum(vhi, lo_idx + n)
        if np.any(b <= a):
            continue
        out[:, a[0] - lo_idx[0]:b[0] - lo_idx[0], a[1] - lo_idx[1]:b[1] - lo_idx[1], a[2] - lo_idx[2]:b[2] - lo_idx[2]] = \
            v[:, a[0] - vlo[0]:b[0] - vlo[0], a[1] - vlo[1]:b[1] - vlo[1], a[2] - vlo[2]:b[2] - vlo[2]]
    t = float((chk / "Header").read_text().splitlines()[2])
    return out, t


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("chk", nargs="+")
    ap.add_argument("--level", type=int, default=4)
    ap.add_argument("--dx0", type=float, default=0.5)
    ap.add_argument("--centre", nargs=3, type=float, default=[64, 64, 64])
    ap.add_argument("--half", type=float, default=2.25)
    ap.add_argument("--rmin", type=float, default=0.3)
    ap.add_argument("--rstep", type=float, default=0.3)
    args = ap.parse_args()
    dx = args.dx0 / 2**args.level
    n = int(round(2 * args.half / dx))
    c = np.array(args.centre)
    lo_idx = np.round((c - args.half) / dx).astype(int)
    for p in args.chk:
        arr, t = read_level(pathlib.Path(p), args.level, lo_idx, n)
        if np.isnan(arr).any():
            print(f"{p}: the cube is not covered by level {args.level}"); continue
        F = {nm: arr[i] for i, nm in enumerate(NAMES)}
        H, rho = lh.hamiltonian(F, dx)
        rs = np.arange(args.rmin, args.half - 0.2, args.rstep)
        Hs = lh.shell_avg(H, dx, args.half, rs)
        src = lh.shell_avg(16 * math.pi * np.abs(rho), dx, args.half, rs)
        Th = lh.shell_avg(F["Theta"], dx, args.half, rs)
        al = lh.shell_avg(F["lapse"], dx, args.half, rs)
        # Z4 vector in conformal components: Gamma_hat^k = Gamma_tilde^k(h) + 2 Z~^k.
        # The code's own Hamiltonian (Constraints.impl.hpp) builds its Ricci from
        # the EVOLVED Gamma_hat, i.e. H_code ~ H_ADM + 2 chi d_k Z~^k (flat divergence;
        # a check of where the violation lives, not an exact identity).
        h = np.empty((3, 3) + F["chi"].shape)
        for a, b in lh.SYM:
            h[a, b] = h[b, a] = F[f"h{a+1}{b+1}"]
        hi = np.moveaxis(np.linalg.inv(np.moveaxis(h, (0, 1), (-2, -1))), (-2, -1), (0, 1))
        dh = np.stack([lh.d1(h, dx, 2 + c) for c in range(3)])      # dh[c,a,b]
        low = 0.5 * (np.einsum("ijl...->lij...", dh) + np.einsum("jil...->lij...", dh) - dh)
        GamT = np.einsum("ij...,kl...,lij...->k...", hi, hi, low)    # Gamma~^k = h^ij Gamma~^k_ij
        del low
        Zt = 0.5 * (np.stack([F["Gamma1"], F["Gamma2"], F["Gamma3"]]) - GamT)
        divZ = sum(lh.d1(Zt[k], dx, k) for k in range(3))
        dZ = lh.shell_avg(2 * F["chi"] * divZ, dx, args.half, rs)
        print(f"{pathlib.Path(p).name}  t={t:.2f}  level {args.level} dx={dx}")
        print("   r     <H_ADM>      <16pi|rho|>   ratio     <2chi dZ>    <H_ADM+2chi dZ>  <Theta>      <alpha>")
        for k in range(rs.size):
            print(f"   {rs[k]:.2f}  {Hs[k]:+.4e}  {src[k]:.4e}   {Hs[k]/src[k]:+.3f}   {dZ[k]:+.4e}  {Hs[k]+dZ[k]:+.4e}      {Th[k]:+.4e}  {al[k]:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
