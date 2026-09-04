"""Offline apparent-horizon scan on GRTeclyn full-state plotfiles.

Radial-scan approximation: expansion Theta of coordinate spheres about a
centre, per direction; the outermost Theta=0 crossing is the AH radius in
that direction.  Physical metric gamma_ij = h_ij/chi (det h = 1), physical
K_ij = (A_ij + h_ij K/3)/chi, sqrt(gamma) = chi^-1.5.
Theta = div_gamma(s) + K_ij s^i s^j - K,  s = unit gamma-normal of r=const.
"""
import argparse, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
import yt
yt.set_log_level(50)
from scipy.ndimage import map_coordinates

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('plt_path')
ap.add_argument('--center', nargs=3, type=float, default=[32.0, 32.0, 32.0],
                metavar=('X', 'Y', 'Z'))
ap.add_argument('--half', type=float, default=2.5,
                help='half-width of the covering box (also the ray ceiling)')
ap.add_argument('--level', type=int, default=3,
                help='covering-grid level (capped at the finest in the file)')
args = ap.parse_args()
plt_path = args.plt_path
CEN = np.array(args.center)
HALF, LEVEL = args.half, args.level

ds = yt.load(plt_path)
LEVEL = min(LEVEL, ds.index.max_level)
dx = float(ds.index.get_smallest_dx())
N = int(round(2 * HALF / dx))
cg = ds.covering_grid(LEVEL, left_edge=CEN - HALF, dims=[N] * 3)

def f(name): return np.asarray(cg[('boxlib', name)], dtype=np.float64)

chi = np.clip(f('chi'), 1e-12, None)
K = f('K')
h = np.empty((3, 3) + chi.shape)
A = np.empty_like(h)
for a in range(3):
    for b in range(a, 3):
        h[a, b] = h[b, a] = f(f'h{a+1}{b+1}')
        A[a, b] = A[b, a] = f(f'A{a+1}{b+1}')

# inverse of h (det h = 1): adjugate
hi = np.empty_like(h)
for a in range(3):
    for b in range(3):
        hi[a, b] = (h[(a+1)%3, (b+1)%3] * h[(a+2)%3, (b+2)%3]
                    - h[(a+1)%3, (b+2)%3] * h[(a+2)%3, (b+1)%3])
# hi as written is the cofactor matrix transposed for symmetric h -> equals inverse
gam_inv = chi * hi          # gamma^ab
Kphys = (A + h * (K / 3.0)) / chi   # K_ij physical

ax = np.arange(N) * dx + dx / 2 - HALF
X = np.stack(np.meshgrid(ax, ax, ax, indexing='ij'))
r = np.sqrt((X ** 2).sum(0))
r = np.clip(r, 1e-10, None)
dr = X / r                  # partial_i r

# s^i = gamma^ij dr_j / lam
si = np.einsum('ab...,b...->a...', gam_inv, dr)
lam = np.sqrt(np.clip(np.einsum('a...,a...->...', si, dr), 1e-30, None))
si /= lam

sqg = chi ** -1.5
div = sum(np.gradient(sqg * si[a], dx, axis=a) for a in range(3)) / sqg
KSS = np.einsum('ab...,a...,b...->...', Kphys, si, si)
Theta = div + KSS - K

# ray scan
nth, nph = 25, 48
th = np.linspace(0.02, np.pi - 0.02, nth)
ph = np.linspace(0, 2 * np.pi, nph, endpoint=False)
TH, PH = np.meshgrid(th, ph, indexing='ij')
nvec = np.stack([np.sin(TH) * np.cos(PH), np.sin(TH) * np.sin(PH), np.cos(TH)])
rs = np.arange(0.25, HALF - 0.2, 0.02)
pts = nvec[:, None] * rs[None, :, None, None]        # (3, nr, nth, nph)
idx = (pts + HALF) / dx - 0.5
Tray = map_coordinates(Theta, idx.reshape(3, -1), order=1).reshape(rs.size, nth, nph)

print(f'{plt_path.split("/")[-1]}  t={float(ds.current_time):.2f}')
# shell-max statistic (the in-code scan's convention): a sphere is trapped
# only when Theta <= 0 everywhere on it; the AH estimate is the outermost
# trapped shell.
shell_max = Tray.max(axis=(1, 2))
trapped_shells = np.where(shell_max <= 0)[0]
if trapped_shells.size:
    k = trapped_shells[-1]
    print(f'  shell-max crossing (in-code convention): r = {rs[k]:.3f} '
          f'(shell max there {shell_max[k]:+.3f}; next shell {shell_max[min(k+1,rs.size-1)]:+.3f})')
else:
    print('  no fully-trapped shell')

r_ah = np.full((nth, nph), np.nan)
for i in range(nth):
    for j in range(nph):
        t = Tray[:, i, j]
        neg = np.where((t[:-1] < 0) & (t[1:] >= 0))[0]
        if neg.size:
            k = neg[-1]
            r_ah[i, j] = rs[k] + 0.02 * (-t[k]) / (t[k + 1] - t[k])

found = np.isfinite(r_ah)
if not found.any():
    print('  NO trapped surface found on any ray')
    sys.exit()
frac = found.mean()
print(f'  rays trapped: {100*frac:.0f}%   r_AH min/mean/max = '
      f'{np.nanmin(r_ah):.3f} / {np.nanmean(r_ah):.3f} / {np.nanmax(r_ah):.3f}')
ieq = nth // 2
print(f'  along +z: {r_ah[0, 0]:.3f}   along -z: {r_ah[-1, 0]:.3f}   '
      f'equator min/max: {np.nanmin(r_ah[ieq]):.3f}/{np.nanmax(r_ah[ieq]):.3f}')
# area and irreducible mass (embed surface, induced 2-metric)
if frac > 0.999:
    surf = CEN[:, None, None] + nvec * r_ah          # (3, nth, nph)
    p = surf - CEN[:, None, None]
    dth = np.gradient(p, th, axis=1)
    dph = np.gradient(p, ph, axis=2)
    idxs = (p + HALF) / dx - 0.5
    gam = h / chi                                     # gamma_ij grid
    gS = np.empty((3, 3, nth, nph))
    for a in range(3):
        for b in range(3):
            gS[a, b] = map_coordinates(gam[a, b], idxs.reshape(3, -1),
                                       order=1).reshape(nth, nph)
    E = np.einsum('ab...,a...,b...->...', gS, dth, dth)
    F = np.einsum('ab...,a...,b...->...', gS, dth, dph)
    G = np.einsum('ab...,a...,b...->...', gS, dph, dph)
    dA = np.sqrt(np.clip(E * G - F * F, 0, None))
    area = (dA.sum() * (th[1]-th[0]) * (ph[1]-ph[0]))
    M_irr = np.sqrt(area / (16 * np.pi))
    print(f'  area = {area:.3f}   M_irr = {M_irr:.3f}')
