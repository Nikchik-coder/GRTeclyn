"""GPU_PLAN #13: what IS the inter-throat blob / collapsed core?

Gauge-invariant(ish) scalars on coordinate shells about a center, computed
offline from a plotfile's raw CCZ4 state (chi h_ij K A_ij lapse phi Pi
Weyl4_Re/Im) with the code's own conventions:

  rho   = -1/2 (Pi^2 + chi hUU^ij d_i phi d_j phi)      phantom, V = 0
          (ExoticScalarField emtensor, support_strength = 1: rho <= 0
          pointwise by construction -- the measurement is WHERE it
          concentrates and how it flows, not whether it can be positive)
  Ham   = R + (2/3) K^2 - A_ij A^ij - 16 pi rho          (ConstraintsWithMatter)
          with R finite-differenced from the physical metric gamma = h/chi
  A2    = htilde^ia htilde^jb A_ij A_ab                   (chi-free identity)
  r_areal(r) = sqrt(Area(coordinate sphere r) / 4 pi)     collapse measure
  Flux(r)    = closed-integral j_i s^i dA_proper,  j_i = Pi d_i phi
          (energy flux seen by normal observers; negative rho flowing
          inward shows as the sign of this integral times the rho sign)

The discriminator the plan names: curvature (|Weyl4|, R) bounded while the
lapse runs to its floor = slicing artefact; curvature AND constraint growing
together = constraint mode; bounded curvature + clean Ham + concentrated
negative rho = a genuine negative-energy structure.

Usage: blob_nature_scan.py <plt> [--center X Y Z] [--half H] [--level L]
Defaults match the merger campaign box (center 32,32,32).
"""
import argparse
import sys
import warnings

import numpy as np

warnings.filterwarnings('ignore')
import yt  # noqa: E402

yt.set_log_level(50)
from scipy.ndimage import map_coordinates  # noqa: E402

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('plt_path')
ap.add_argument('--center', nargs=3, type=float, default=[32.0, 32.0, 32.0],
                metavar=('X', 'Y', 'Z'))
ap.add_argument('--half', type=float, default=3.5,
                help='half-width of the covering box')
ap.add_argument('--level', type=int, default=3,
                help='covering-grid level (capped at the finest in the file); '
                     '3 keeps the Ricci finite-difference affordable')
ap.add_argument('--radii', nargs='+', type=float,
                default=[0.3, 0.6, 0.9, 1.2, 1.5, 2.0, 2.5, 3.0],
                help='shell radii to report')
args = ap.parse_args()

CEN = np.array(args.center)
HALF = args.half

ds = yt.load(args.plt_path)
LEVEL = min(args.level, ds.index.max_level)
dx = float(ds.index.get_smallest_dx()) * 2 ** (ds.index.max_level - LEVEL)
N = int(round(2 * HALF / dx))
cg = ds.covering_grid(LEVEL, left_edge=CEN - HALF, dims=[N] * 3)


def f(name):
    return np.asarray(cg[('boxlib', name)], dtype=np.float64)


chi = np.clip(f('chi'), 1e-12, None)
K = f('K')
lapse, phi, Pi = f('lapse'), f('phi'), f('Pi')
w4 = np.hypot(f('Weyl4_Re'), f('Weyl4_Im'))

h = np.empty((3, 3, N, N, N))
A = np.empty((3, 3, N, N, N))
for a, b, nm in [(0, 0, '11'), (0, 1, '12'), (0, 2, '13'),
                 (1, 1, '22'), (1, 2, '23'), (2, 2, '33')]:
    h[a, b] = h[b, a] = f('h' + nm)
    A[a, b] = A[b, a] = f('A' + nm)

# htilde^ij (unit-determinant conformal metric -> plain 3x3 inverse)
hf = np.moveaxis(h, (0, 1), (-2, -1))
hUU = np.moveaxis(np.linalg.inv(hf), (-2, -1), (0, 1))

# rho (phantom, massless)
d1phi = np.stack(np.gradient(phi, dx))
gradsq = np.einsum('ab...,a...,b...->...', hUU, d1phi, d1phi)
rho = -0.5 * (Pi * Pi + chi * gradsq)

# A_ij A^ij (physical), chi-free
A2 = np.einsum('ia...,jb...,ij...,ab...->...', hUU, hUU, A, A)

# Ricci scalar of gamma_ij = h_ij / chi, by centred differences
gam = h / chi
gam_inv = chi * hUU
dgam = np.stack(
    [np.stack(np.gradient(gam[a, b], dx), axis=0) for a in range(3)
     for b in range(3)], axis=0).reshape(3, 3, 3, N, N, N)  # dgam[a,b,k]=d_k g_ab
# Gamma^k_ij, built explicitly
Gam = np.empty((3, 3, 3, N, N, N))
for k in range(3):
    for i in range(3):
        for j in range(3):
            s = np.zeros((N, N, N))
            for l in range(3):
                s += gam_inv[k, l] * (dgam[l, j, i] + dgam[l, i, j] - dgam[i, j, l])
            Gam[k, i, j] = 0.5 * s
dGam = np.stack(
    [np.stack(np.gradient(Gam[k, i, j], dx), axis=0)
     for k in range(3) for i in range(3) for j in range(3)],
    axis=0).reshape(3, 3, 3, 3, N, N, N)  # dGam[k,i,j,m] = d_m Gamma^k_ij
Ric = np.zeros((3, 3, N, N, N))
for i in range(3):
    for j in range(3):
        term = np.zeros((N, N, N))
        for k in range(3):
            term += dGam[k, i, j, k] - dGam[k, k, j, i]
            for l in range(3):
                term += Gam[k, k, l] * Gam[l, i, j] - Gam[k, i, l] * Gam[l, k, j]
        Ric[i, j] = term
R = np.einsum('ij...,ij...->...', gam_inv, Ric)

Ham = R + (2.0 / 3.0) * K * K - A2 - 16.0 * np.pi * rho
Ham_scale = np.abs(R) + (2.0 / 3.0) * K * K + np.abs(A2) + np.abs(16 * np.pi * rho)

# flux ingredients
j_low = Pi * d1phi                                    # j_i = Pi d_i phi
X = np.stack(np.meshgrid(*[np.arange(N) * dx + dx / 2 - HALF] * 3,
                         indexing='ij'))
r_grid = np.clip(np.sqrt((X ** 2).sum(0)), 1e-10, None)
dr = X / r_grid
si = np.einsum('ab...,b...->a...', gam_inv, dr)
lam = np.sqrt(np.clip(np.einsum('a...,a...->...', si, dr), 1e-30, None))
si /= lam
j_dot_s = np.einsum('a...,a...->...', si, j_low)

nth, nph = 25, 48
th = np.linspace(0.02, np.pi - 0.02, nth)
ph = np.linspace(0, 2 * np.pi, nph, endpoint=False)
TH, PH = np.meshgrid(th, ph, indexing='ij')
nvec = np.stack([np.sin(TH) * np.cos(PH), np.sin(TH) * np.sin(PH), np.cos(TH)])


def shell(field, r):
    pts = nvec * r
    idx = (pts + HALF) / dx - 0.5
    return map_coordinates(field, idx.reshape(3, -1), order=1).reshape(nth, nph)


def shell_area(r):
    """Proper area of the coordinate sphere r (induced 2-metric)."""
    p = nvec * r
    dth = np.gradient(p, th, axis=1)
    dph = np.gradient(p, ph, axis=2)
    idxs = (p + HALF) / dx - 0.5
    gS = np.empty((3, 3, nth, nph))
    for a in range(3):
        for b in range(3):
            gS[a, b] = map_coordinates(gam[a, b], idxs.reshape(3, -1),
                                       order=1).reshape(nth, nph)
    E = np.einsum('ab...,a...,b...->...', gS, dth, dth)
    F = np.einsum('ab...,a...,b...->...', gS, dth, dph)
    G = np.einsum('ab...,a...,b...->...', gS, dph, dph)
    dA = np.sqrt(np.clip(E * G - F * F, 0, None))
    w = (th[1] - th[0]) * (ph[1] - ph[0])
    return dA * w


c = N // 2
print(f"{args.plt_path.rstrip('/').split('/')[-1]}  t={float(ds.current_time):.2f}"
      f"  level {LEVEL}  dx={dx:g}  box half {HALF}")
print(f"  center cell: rho={rho[c,c,c]:+.3e}  R={R[c,c,c]:+.3e}  "
      f"Ham={Ham[c,c,c]:+.3e}  |Weyl4|={w4[c,c,c]:.3e}  "
      f"lapse={lapse[c,c,c]:.2e}  chi={chi[c,c,c]:.2e}  K={K[c,c,c]:+.3f}")
print("    r   rho mean/min      Ham mean    |Ham|/scale  R mean     "
      "|W4| mean  r_areal   Flux(js)   lapse min  chi min   K mean")
for r in args.radii:
    if r >= HALF - 2 * dx:
        continue
    rh, hm, hs = shell(rho, r), shell(Ham, r), shell(Ham_scale, r)
    Rm, wm, Km = shell(R, r), shell(w4, r), shell(K, r)
    lp, ch = shell(lapse, r), shell(chi, r)
    js = shell(j_dot_s, r)
    dA = shell_area(r)
    area = dA.sum()
    r_areal = np.sqrt(area / (4 * np.pi))
    flux = (js * dA).sum()
    rel = np.abs(hm).mean() / max(hs.mean(), 1e-30)
    print(f"  {r:4.1f}  {rh.mean():+9.3e}/{rh.min():+9.3e}  {hm.mean():+9.2e}  "
          f"{rel:9.3f}  {Rm.mean():+9.2e}  {wm.mean():9.3e}  {r_areal:7.3f}  "
          f"{flux:+9.3e}  {lp.min():8.2e}  {ch.min():8.2e}  {Km.mean():+6.3f}")
