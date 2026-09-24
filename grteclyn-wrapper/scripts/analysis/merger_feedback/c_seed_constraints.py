#!/usr/bin/env python3
r"""What the declared seed does to the constraints (task C(b), 2026-09-24).

The paper (Sec. II.D) seeds psi -> psi (1 + eps g), g = exp(-(r - r_t)^2 / w^2),
w = a/4, with K_ij = Pi = 0.  Three questions, three blocks of output:

1. MEASURED, from the pack (constraint_norms.dat: L2 norms of the level-0
   grid, dx = 0.5, BinaryWormholeLevel::write_scalar_diagnostics):
   H and M at the first rows for eps = 0, +-1e-3, +-1e-2, +-0.1, and the
   quadrature test.  With H(eps)^2 = H0^2 + 2 eps C + eps^2 D the sign-averaged
   excess sqrt((H(+)^2 + H(-)^2)/2 - H0^2) must equal sqrt(D)|eps| if the seed's
   violation is linear in eps and adds in quadrature to the unperturbed
   floor; C measures its overlap with the floor.

2. ANALYTIC, the continuum violation.  For K_ij = Pi = 0 and conformally flat
   data, H = R - 16 pi rho with R = -8 Psi^-5 lap Psi, rho = -|d phi|^2/(2 Psi^4)
   (phantom), and the unperturbed drainhole solves lap Psi = pi |d phi|^2 Psi
   (linear in Psi).  Multiplying Psi by (1 + eps g) therefore leaves exactly
       H_seed = -8 eps (Psi lap g + 2 grad Psi . grad g) / (Psi (1 + eps g))^5 * Psi^...
   i.e. H_seed = -8 eps Psi^-4 (1 + eps g)^-5 (lap g + 2 grad ln Psi . grad g):
   linear in eps up to (1 + eps g)^-5.  Printed: its peak against 16 pi |rho|
   there, and its L2 norm over the 64^3 box (the dilution the level-0 norm has).

3. REPRODUCTION of the recorded level-0 H(0): the same fourth-order centred
   stencils on the level-0 cell centres (dx = 0.5, the box centred on a cell
   corner), H = 2 lap chi - (5/2) |grad chi|^2 / chi + 8 pi chi |grad phi|^2.
   If this reproduces the pack's H(0) for every eps, the norm is understood:
   an unperturbed discretisation floor from the steep far-side data plus the
   seed's shell, which is one level-0 cell wide.

    grteclyn-wrapper/.venv/bin/python grteclyn-wrapper/scripts/analysis/merger_feedback/c_seed_constraints.py
"""

from __future__ import annotations

import math
import pathlib
import sys

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "research" / "merger" / "article" / "claims"))
import lib  # noqa: E402  (pack access, same as the ledger)

A, M = 2.0, 1.0                    # production throat (evolution_params.txt)
W = A / 4.0                        # seed width (BinaryWormholeInitialData::seed_shell)
R_T = 0.5 * (M + math.sqrt(M * M + A * A))
C_PHI = math.sqrt(A * A + M * M) / (A * math.sqrt(4.0 * math.pi))

LEVEL3 = {0.0: "single_hold_t100", -1e-3: "single_eps_m1e3_t100", 1e-3: "single_eps_p1e3_t100",
          -1e-2: "single_eps_m1e2_t100", 1e-2: "single_eps_p1e2_t100",
          -1e-1: "single_eps_m1e1_t100", 1e-1: "single_eps_p1e1_t100"}


def norms(run: str) -> np.ndarray:
    names, arr = lib.stream(run, "constraint_norms.dat")
    return arr[:, :3]


def at(a: np.ndarray, t: float, col: int) -> float:
    return float(np.interp(t, a[:, 0], a[:, col]))


# ------------------------------------------------------------------ analytic fields
def fields(r: np.ndarray, eps: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(chi, phi, g) of the seeded one-body drainhole at isotropic radius r."""
    X = (r - A * A / (4.0 * r)) / A
    u = (M / A) * (np.arctan(X) - 0.5 * math.pi)
    omega = 1.0 + A * A / (4.0 * r * r)
    g = np.exp(-((r - R_T) / W) ** 2)
    psi = np.sqrt(omega) * (1.0 + eps * g)
    chi = np.exp(2.0 * u) / psi**4
    phi = C_PHI * np.arctan(X)
    return chi, phi, g


def continuum_seed_H(eps: float, n: int = 400001, rmax: float = 32.0) -> dict:
    """H of the seeded data on a fine radial grid (exact up to the grid)."""
    r = np.linspace(1e-3, rmax, n)
    dr = r[1] - r[0]
    chi, phi, g = fields(r, eps)
    Psi = chi ** -0.25
    d = lambda f: np.gradient(f, dr, edge_order=2)
    lap = lambda f: d(d(f)) + 2.0 / r * d(f)       # flat radial Laplacian
    H = -8.0 * Psi**-5 * lap(Psi) + 8.0 * math.pi * Psi**-4 * d(phi) ** 2
    rho = -0.5 * Psi**-4 * d(phi) ** 2
    # closed form of the seed part, to check the algebra
    chi0, _, _ = fields(r, 0.0)
    Psi0 = chi0 ** -0.25
    Hform = -8.0 * eps * Psi0**-4 * (1.0 + eps * g) ** -5 * (lap(g) + 2.0 * d(np.log(Psi0)) * d(g))
    shell = (r > 0.3) & (r < 6.0)
    k = int(np.argmax(np.abs(H) * shell))
    vol = 64.0**3
    l2 = math.sqrt(np.trapezoid(H[shell] ** 2 * 4 * math.pi * r[shell] ** 2, r[shell]) / vol)
    return dict(r_peak=r[k], H_peak=H[k], rho16=16 * math.pi * abs(rho[k]),
                ratio=abs(H[k]) / (16 * math.pi * abs(rho[k])),
                form_err=float(np.max(np.abs(H - Hform)[shell]) / max(np.max(np.abs(H[shell])), 1e-300)),
                l2_box=l2)


# ------------------------------------------------------------------ level-0 reproduction
def d1(f: np.ndarray, h: float, ax: int) -> np.ndarray:
    return (-np.roll(f, -2, ax) + 8 * np.roll(f, -1, ax) - 8 * np.roll(f, 1, ax) + np.roll(f, 2, ax)) / (12 * h)


def d2(f: np.ndarray, h: float, ax: int) -> np.ndarray:
    return (-np.roll(f, -2, ax) + 16 * np.roll(f, -1, ax) - 30 * f + 16 * np.roll(f, 1, ax)
            - np.roll(f, 2, ax)) / (12 * h * h)


def level0_H(eps: float, L: float = 64.0, N: int = 128) -> float:
    h = L / N
    ng = 2
    x = (np.arange(-ng, N + ng) + 0.5) * h - L / 2.0      # centre on a cell corner
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    r = np.sqrt(X * X + Y * Y + Z * Z)
    chi, phi, _ = fields(r, eps)
    chi = np.maximum(chi, 1e-10)                            # the initial-data clamp
    lap = sum(d2(chi, h, a) for a in range(3))
    gchi2 = sum(d1(chi, h, a) ** 2 for a in range(3))
    gphi2 = sum(d1(phi, h, a) ** 2 for a in range(3))
    H = 2.0 * lap - 2.5 * gchi2 / chi + 8.0 * math.pi * chi * gphi2
    Hv = H[ng:-ng, ng:-ng, ng:-ng]
    return float(math.sqrt(np.mean(Hv * Hv)))


def main() -> int:
    print("1. MEASURED (pack, level-0 L2 norms; level-3 arms)")
    print(f"   {'eps':>7s} {'H(0)':>11s} {'H(0.05)':>11s} {'M(0.05)':>10s} {'M(0.1)':>10s} {'M(0.5)':>10s} {'M(1)':>10s} {'M(0.5)/|eps|':>12s}")
    H0 = {}
    for eps, run in sorted(LEVEL3.items()):
        a = norms(run)
        H0[eps] = a[0, 1]
        mr = at(a, 0.5, 2) / abs(eps) if eps else float("nan")
        print(f"   {eps:+7.0e} {a[0,1]:11.4e} {at(a,.05,1):11.4e} {at(a,.05,2):10.3e} {at(a,.1,2):10.3e}"
              f" {at(a,.5,2):10.3e} {at(a,1.,2):10.3e} {mr:12.4e}   (M(0) = {a[0,2]:.1e})")
    h0 = H0[0.0]
    print(f"   quadrature test, floor H0 = {h0:.4e}:")
    for e in (1e-3, 1e-2, 1e-1):
        hp, hm = H0[e], H0[-e]
        D = ((hp**2 + hm**2) / 2 - h0**2) / e**2
        C = (hp**2 - hm**2) / (4 * e)
        print(f"     |eps| = {e:.0e}:  sqrt(<H^2> - H0^2)/|eps| = {math.sqrt(D):.4f}   overlap C/(H0 sqrt D) = {C/(h0*math.sqrt(D)):+.3f}"
              f"   H(+)/H0 = {hp/h0:.4f}, H(-)/H0 = {hm/h0:.4f}")
    # level-4 twins share H(0) with level 3: the norm lives on level 0
    for run in ("single_eps_p1e2_ml4_t060", "single_eps_m1e2_ml4_t060"):
        print(f"   {run}: H(0) = {norms(run)[0,1]:.10e} (level 4; level-3 twin identical -> level-0 norm)")

    print("\n2. ANALYTIC continuum violation of the seeded data (K_ij = Pi = 0)")
    for eps in (1e-3, 1e-2, -1e-2, 1e-1, -1e-1):
        c = continuum_seed_H(eps)
        print(f"   eps = {eps:+.0e}: peak |H| = {abs(c['H_peak']):.3e} at r = {c['r_peak']:.3f}"
              f" = {c['ratio']:.2f} x 16 pi |rho| there ({c['rho16']:.3e});"
              f" box-L2 = {c['l2_box']:.3e} = {c['l2_box']/abs(eps):.4f}|eps|;"
              f" closed-form residual {c['form_err']:.1e}")
    c0 = continuum_seed_H(0.0)
    print(f"   eps = 0: box-L2 of the exact data on the fine radial grid = {c0['l2_box']:.1e} (the continuum floor)")

    print("\n3. REPRODUCTION of the recorded level-0 H(0) (4th-order stencils, dx = 0.5)")
    for eps, run in sorted(LEVEL3.items()):
        h = level0_H(eps)
        print(f"   eps = {eps:+7.0e}: reproduced {h:.6e}   recorded {H0[eps]:.6e}   ratio {h/H0[eps]:.5f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
