"""Orientation-corrected marginal-surface scan on GRTeclyn full-state plotfiles.

The historic scan (ah_radial_scan.py) takes "outward" to be +d/dr on every
coordinate sphere.  Inside a wormhole throat that points toward the OTHER
mouth, where the areal radius DEcreases, so it computes the ingoing expansion
and labels every throat interior "trapped" (GPU_PLAN, CRITICAL BUG, Defect 2).

This scan fixes the orientation by construction and reports both expansions:

  R(r)        areal radius of the coordinate sphere r, sqrt(Area / 4 pi), with
              the area integrated with the FULL induced 2-metric of the sphere
              (gamma_ij = h_ij / chi, det h = 1)
  outward     the side on which R increases: +d/dr where dR/dr > 0, -d/dr
              where dR/dr < 0 (inside a throat)
  theta_out   expansion of the outgoing null normal l = n + s_out
  theta_in    expansion of the ingoing  null normal k = n - s_out
  M_MS(r)     Misner-Sharp mass of the sphere, 2 M/R = 1 + R^2 theta_l theta_k / 4
              (orientation-independent: the product is symmetric under s -> -s)

Per-shell classification (shell statistics: max over the sphere for "<= 0
everywhere", i.e. the in-code convention):
  trapped        theta_out <= 0 and theta_in <= 0 everywhere   (inside a BH)
  MOTS           outermost shell where max(theta_out) crosses 0 with theta_in < 0
  throat         dR/dr changes sign (minimal surface) -- both expansions ~ 0
  anti-trapped   theta_out >= 0 and theta_in >= 0 everywhere   (white-hole side)
  normal         theta_out > 0, theta_in < 0

Also prints, for the same rays, the proxy r / sqrt(chi) along +-x that the
areal-radius consumer uses, against the true R(r), so the size of the h_ij != delta
correction to INSTABILITY.md's radius can be read off.

Needs plotfiles that carry chi, h_ij, K, A_ij (the binary arms' and the
2026-09-08 ladder arms' do; the Stage-0 single_hold_t100 plotfiles do NOT).
"""
import argparse, sys, warnings
import numpy as np
warnings.filterwarnings('ignore')
import yt
yt.set_log_level(50)
from scipy.ndimage import map_coordinates

ap = argparse.ArgumentParser(description=__doc__,
                             formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('plt_path')
ap.add_argument('--center', nargs=3, type=float, default=[32.0, 32.0, 32.0],
                metavar=('X', 'Y', 'Z'))
ap.add_argument('--half', type=float, default=2.5,
                help='half-width of the covering box (also the ray ceiling)')
ap.add_argument('--level', type=int, default=3,
                help='covering-grid level (capped at the finest in the file)')
ap.add_argument('--rmin', type=float, default=0.25)
ap.add_argument('--dr', type=float, default=0.02)
ap.add_argument('--table', type=float, default=0.25,
                help='print one table row every this many units of r')
args = ap.parse_args()
plt_path = args.plt_path
CEN = np.array(args.center)
HALF, LEVEL = args.half, args.level

ds = yt.load(plt_path)
LEVEL = min(LEVEL, ds.index.max_level)
# dx MUST be the requested level's cell size (ah_radial_scan.py, 2026-09-04).
dx = float(ds.index.get_smallest_dx()) * 2 ** (ds.index.max_level - LEVEL)
N = int(round(2 * HALF / dx))
cg = ds.covering_grid(LEVEL, left_edge=CEN - HALF, dims=[N] * 3)
have = {f[1] for f in ds.field_list}
need = ['chi', 'K'] + [f'h{a}{b}' for a in (1, 2, 3) for b in (a, a + 1, a + 2) if b <= 3] \
       + [f'A{a}{b}' for a in (1, 2, 3) for b in (a, a + 1, a + 2) if b <= 3]
missing = [v for v in need if v not in have]
if missing:
    sys.exit(f'{plt_path}: plotfile lacks {missing} -- this scan needs the full state')

def f(name): return np.asarray(cg[('boxlib', name)], dtype=np.float64)

chi = np.clip(f('chi'), 1e-12, None)
K = f('K')
h = np.empty((3, 3) + chi.shape)
A = np.empty_like(h)
for a in range(3):
    for b in range(a, 3):
        h[a, b] = h[b, a] = f(f'h{a+1}{b+1}')
        A[a, b] = A[b, a] = f(f'A{a+1}{b+1}')
hi = np.empty_like(h)                      # inverse of h via the adjugate (det h = 1)
for a in range(3):
    for b in range(3):
        hi[a, b] = (h[(a+1)%3, (b+1)%3] * h[(a+2)%3, (b+2)%3]
                    - h[(a+1)%3, (b+2)%3] * h[(a+2)%3, (b+1)%3])
gam_inv = chi * hi
gam = h / chi
Kphys = (A + h * (K / 3.0)) / chi

ax = np.arange(N) * dx + dx / 2 - HALF
X = np.stack(np.meshgrid(ax, ax, ax, indexing='ij'))
r = np.clip(np.sqrt((X ** 2).sum(0)), 1e-10, None)
dr = X / r
si = np.einsum('ab...,b...->a...', gam_inv, dr)
lam = np.sqrt(np.clip(np.einsum('a...,a...->...', si, dr), 1e-30, None))
si /= lam                                   # unit gamma-normal of r = const, pointing +r
sqg = chi ** -1.5
div = sum(np.gradient(sqg * si[a], dx, axis=a) for a in range(3)) / sqg
KSS = np.einsum('ab...,a...,b...->...', Kphys, si, si)
theta_plus_r = div + KSS - K                # l = n + s(+r)
theta_minus_r = -div + KSS - K              # k = n - s(+r)

# ---- shells -----------------------------------------------------------------
nth, nph = 25, 48
th = np.linspace(0.02, np.pi - 0.02, nth)
ph = np.linspace(0, 2 * np.pi, nph, endpoint=False)
TH, PH = np.meshgrid(th, ph, indexing='ij')
nvec = np.stack([np.sin(TH) * np.cos(PH), np.sin(TH) * np.sin(PH), np.cos(TH)])
rs = np.arange(args.rmin, HALF - 0.2, args.dr)
pts = nvec[:, None] * rs[None, :, None, None]         # (3, nr, nth, nph)
idx = (pts + HALF) / dx - 0.5
flat = idx.reshape(3, -1)

def on_rays(field):
    return map_coordinates(field, flat, order=1).reshape(rs.size, nth, nph)

Tp = on_rays(theta_plus_r)
Tm = on_rays(theta_minus_r)
chi_r = on_rays(chi)
gS = np.empty((3, 3, rs.size, nth, nph))
for a in range(3):
    for b in range(a, 3):
        gS[a, b] = gS[b, a] = on_rays(gam[a, b])

# area of each coordinate sphere from its induced metric
dth = np.gradient(pts, th, axis=2)
dph = np.gradient(pts, ph, axis=3)
E = np.einsum('abrtp,artp,brtp->rtp', gS, dth, dth)
F = np.einsum('abrtp,artp,brtp->rtp', gS, dth, dph)
G = np.einsum('abrtp,artp,brtp->rtp', gS, dph, dph)
dA = np.sqrt(np.clip(E * G - F * F, 0, None))
area = dA.sum(axis=(1, 2)) * (th[1] - th[0]) * (ph[1] - ph[0])
R = np.sqrt(area / (4 * np.pi))
dRdr = np.gradient(R, rs)
outward_is_plus_r = dRdr >= 0

# orientation-corrected expansions per shell
theta_out = np.where(outward_is_plus_r[:, None, None], Tp, Tm)
theta_in = np.where(outward_is_plus_r[:, None, None], Tm, Tp)
prod = (Tp * Tm).mean(axis=(1, 2))
M_MS = 0.5 * R * (1.0 + R ** 2 * prod / 4.0)

out_max = theta_out.max(axis=(1, 2)); out_min = theta_out.min(axis=(1, 2))
in_max = theta_in.max(axis=(1, 2));   in_min = theta_in.min(axis=(1, 2))

def classify(k):
    if out_max[k] <= 0 and in_max[k] <= 0: return 'TRAPPED'
    if out_min[k] >= 0 and in_min[k] >= 0: return 'anti-trapped'
    if out_min[k] > 0 and in_max[k] < 0: return 'normal'
    return 'mixed'

# proxy the consumer uses: r / sqrt(chi) along +x and -x (theta = pi/2, phi = 0 / pi)
ieq = nth // 2
Rproxy_px = rs / np.sqrt(chi_r[:, ieq, 0])
Rproxy_mx = rs / np.sqrt(chi_r[:, ieq, nph // 2])

name = plt_path.rstrip('/').split('/')[-1]
print(f'{name}  t={float(ds.current_time):.2f}  centre={CEN.tolist()}  level={LEVEL} dx={dx:.4f}  half={HALF}')
# minimal surfaces (throats): sign changes of dR/dr
sc = np.where(np.diff(np.sign(dRdr)) != 0)[0]
for k in sc:
    kind = 'minimum (throat)' if dRdr[k] < 0 <= dRdr[k+1] else 'maximum'
    print(f'  areal-radius {kind} at r = {rs[k]:.3f}: R = {R[k]:.3f}, '
          f'theta_out max {out_max[k]:+.3f} / theta_in max {in_max[k]:+.3f}')
# MOTS: outermost shell where max(theta_out) goes from <= 0 to > 0 with theta_in < 0
mots = [k for k in range(rs.size - 1) if out_max[k] <= 0 < out_max[k+1] and in_max[k] < 0]
if mots:
    k = mots[-1]
    rr = rs[k] + args.dr * (-out_max[k]) / (out_max[k+1] - out_max[k])
    print(f'  MOTS (outermost, corrected orientation): r = {rr:.3f}, R = {np.interp(rr, rs, R):.3f}, '
          f'M_MS = {np.interp(rr, rs, M_MS):.3f}; shells inside classified '
          f'{classify(max(k-1,0))}, outside {classify(min(k+2, rs.size-1))}')
else:
    print('  no MOTS with the corrected orientation')
trap = np.where((out_max <= 0) & (in_max <= 0))[0]
if trap.size:
    print(f'  fully trapped shells: r = {rs[trap[0]]:.3f} .. {rs[trap[-1]]:.3f}')
anti = np.where((out_min >= 0) & (in_min >= 0))[0]
if anti.size:
    print(f'  anti-trapped shells: r = {rs[anti[0]]:.3f} .. {rs[anti[-1]]:.3f}')
naive = np.where(Tp.max(axis=(1, 2)) <= 0)[0]
if naive.size:
    print(f'  (naive +r orientation would call r = {rs[naive[0]]:.3f} .. {rs[naive[-1]]:.3f} trapped)')

print('     r      R     dR/dr  out:min   max    in:min    max   M_MS   class      r/sqrt(chi) +x  -x')
step = max(1, int(round(args.table / args.dr)))
for k in range(0, rs.size, step):
    print(f'  {rs[k]:5.2f} {R[k]:6.3f} {dRdr[k]:+7.3f} {out_min[k]:+7.3f} {out_max[k]:+7.3f} '
          f'{in_min[k]:+7.3f} {in_max[k]:+7.3f} {M_MS[k]:6.3f}  {classify(k):12s} '
          f'{Rproxy_px[k]:6.3f} {Rproxy_mx[k]:6.3f}')
