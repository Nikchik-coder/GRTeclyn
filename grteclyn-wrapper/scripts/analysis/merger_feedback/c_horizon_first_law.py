#!/usr/bin/env python3
r"""Does the numerical collapse horizon obey the spherical first law?  (task C(c)(iii))

Exact spherical GR with the massless phantom (c_spherical_horizon_law.py) fixes
the areal radius of the MOTS tube per unit coordinate time on any slicing:

    dR/dt = 2 pi R^3 < alpha (Pi + s.grad phi)^2 theta_in > / (1 + q),
    q     = 4 pi R^2 < (Pi + s.grad phi)^2 >                          (<= 0)

with l = n + s, k = n - s (the scan's normalisation), Pi = n.grad phi and
theta_in the ingoing expansion on the MOTS.  [Derivation: the tube tangent
X = alpha n + b s has du/dv = 8 pi r^2 e^f phi_v^2, i.e. (alpha - b)/(alpha + b) = q,
and dm/dt = 4 pi r^2 e^f X^v phi_v^2 r_u.]  The phantom influx alone therefore
PREDICTS the shrink rate from one slice; the scan MEASURES it from consecutive
slices.  Agreement = the evolved horizon obeys Einstein + phantom there.
A positive measured rate is impossible for that system; the excess is the
effective null energy the numerical solution carries at its horizon.

A second, slice-local check is the Hamiltonian constraint in Misner-Sharp form
on every shell (spherical symmetry, s.grad m = 4 pi R^2 (rho s.grad R + j_s n.grad R)):

    dm/dr = 4 pi R^2 [ <rho> dR/dr + <j_s> (R/4) <theta_+ + theta_-> / |grad r| ]

with rho = -(Pi^2 + chi h^ij d_i phi d_j phi)/2 and j_i = +Pi d_i phi (phantom,
ExoticScalarField).  Printed: the residual against the source term.

Runs on full-state plotfiles (chi, h, A, K, lapse, phi, Pi), background and
niced -- it builds one covering grid per plotfile and level:

    OMP_NUM_THREADS=4 nice -n 19 grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/analysis/merger_feedback/c_horizon_first_law.py \
        --centre 64.015625 64 64 --levels 3 4 PLT [PLT ...]
"""

from __future__ import annotations

import argparse
import math
import warnings

import numpy as np

warnings.filterwarnings("ignore")

SYM = ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))


def load(plt: str, centre: np.ndarray, half: float, level: int) -> tuple[dict, float, float]:
    import yt
    yt.set_log_level(50)
    ds = yt.load(plt)
    level = int(min(level, ds.index.max_level))
    dx = float(ds.index.get_smallest_dx()) * 2 ** (ds.index.max_level - level)
    N = int(round(2 * half / dx))
    cg = ds.covering_grid(level, left_edge=centre - half, dims=[N] * 3)
    names = ["chi", "K", "lapse", "phi", "Pi"] + [f"h{a+1}{b+1}" for a, b in SYM] + [f"A{a+1}{b+1}" for a, b in SYM]
    out = {n: np.asarray(cg[("boxlib", n)], dtype=np.float64) for n in names}
    return out, dx, float(ds.current_time)


def shells(F: dict, dx: float, half: float, rs: np.ndarray, nth: int = 49, nph: int = 96) -> dict:
    from scipy.ndimage import map_coordinates
    chi = np.clip(F["chi"], 1e-12, None)
    K = F["K"]
    N = chi.shape[0]
    h = np.empty((3, 3) + chi.shape); A = np.empty_like(h)
    for a, b in SYM:
        h[a, b] = h[b, a] = F[f"h{a+1}{b+1}"]
        A[a, b] = A[b, a] = F[f"A{a+1}{b+1}"]
    hi = np.empty_like(h)
    for a in range(3):
        for b in range(3):
            hi[a, b] = (h[(a + 1) % 3, (b + 1) % 3] * h[(a + 2) % 3, (b + 2) % 3]
                        - h[(a + 1) % 3, (b + 2) % 3] * h[(a + 2) % 3, (b + 1) % 3])
    gi = chi * hi
    Kp = (A + h * (K / 3.0)) / chi
    ax = np.arange(N) * dx + dx / 2 - half
    X = np.stack(np.meshgrid(ax, ax, ax, indexing="ij"))
    r = np.clip(np.sqrt((X**2).sum(0)), 1e-10, None)
    dr_ = X / r
    si = np.einsum("ab...,b...->a...", gi, dr_)
    lam = np.sqrt(np.clip(np.einsum("a...,a...->...", si, dr_), 1e-30, None))
    si /= lam
    sqg = chi**-1.5
    div = sum(np.gradient(sqg * si[a], dx, axis=a) for a in range(3)) / sqg
    KSS = np.einsum("ab...,a...,b...->...", Kp, si, si)
    Tp = div + KSS - K
    Tm = -div + KSS - K
    dphi = np.stack([np.gradient(F["phi"], dx, axis=a) for a in range(3)])
    s_dphi = np.einsum("a...,a...->...", si, dphi)
    gphi2 = np.einsum("ab...,a...,b...->...", gi, dphi, dphi)
    Pi = F["Pi"]
    rho = -0.5 * (Pi**2 + gphi2)
    j_s = Pi * s_dphi
    flux = (Pi + s_dphi) ** 2          # (l.grad phi)^2, l = n + s(+r)
    th = np.linspace(0.5 * math.pi / nth, math.pi - 0.5 * math.pi / nth, nth)
    ph = np.linspace(0, 2 * math.pi, nph, endpoint=False)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    nvec = np.stack([np.sin(TH) * np.cos(PH), np.sin(TH) * np.sin(PH), np.cos(TH)])
    pts = nvec[:, None] * rs[None, :, None, None]
    idx = ((pts + half) / dx - 0.5).reshape(3, -1)
    on = lambda f: map_coordinates(f, idx, order=3, mode="nearest").reshape(rs.size, nth, nph)
    ray = {k: on(v) for k, v in dict(Tp=Tp, Tm=Tm, alpha=F["lapse"], flux=flux, rho=rho, j_s=j_s,
                                      lam=lam, chi=chi).items()}
    gS = np.empty((3, 3, rs.size, nth, nph))
    for a, b in SYM:
        gS[a, b] = gS[b, a] = on(h[a, b]) / ray["chi"]
    dth = np.gradient(pts, th, axis=2); dph = np.gradient(pts, ph, axis=3)
    E = np.einsum("abrtp,artp,brtp->rtp", gS, dth, dth)
    Fm = np.einsum("abrtp,artp,brtp->rtp", gS, dth, dph)
    G = np.einsum("abrtp,artp,brtp->rtp", gS, dph, dph)
    dA = np.sqrt(np.clip(E * G - Fm * Fm, 0, None)) * (th[1] - th[0]) * (ph[1] - ph[0])
    area = dA.sum(axis=(1, 2))
    R = np.sqrt(area / (4 * math.pi))
    avg = lambda q: (q * dA).sum(axis=(1, 2)) / area
    out = dict(rs=rs, R=R, dRdr=np.gradient(R, rs), out_max=ray["Tp"].max(axis=(1, 2)),
               in_max=ray["Tm"].max(axis=(1, 2)))
    for k in ("Tp", "Tm", "alpha", "flux", "rho", "j_s", "lam"):
        out[k] = avg(ray[k])
    out["prod"] = avg(ray["Tp"] * ray["Tm"])
    out["prod_plain"] = (ray["Tp"] * ray["Tm"]).mean(axis=(1, 2))      # horizon.py's average
    out["a_flux_thin"] = avg(ray["alpha"] * ray["flux"] * ray["Tm"])
    out["M"] = 0.5 * R * (1 + R**2 * out["prod"] / 4)
    out["M_plain"] = 0.5 * R * (1 + R**2 * out["prod_plain"] / 4)
    return out


def at_mots(S: dict, crit: str = "out_max") -> dict | None:
    """The MOTS shell: 'out_max' = the star scan's rule (outermost sphere with
    theta_out <= 0 everywhere, horizon.py); 'Tp' = where the area-weighted MEAN
    theta_out vanishes (the round MOTS a near-spherical surface approximates)."""
    th = S[crit]
    k = [i for i in range(S["rs"].size - 1)
         if th[i] <= 0 < th[i + 1] and S["in_max"][i] < 0 and S["dRdr"][i] > 0]
    if not k:
        return None
    i = k[-1]
    f = -th[i] / (th[i + 1] - th[i])
    r0 = S["rs"][i] + f * (S["rs"][i + 1] - S["rs"][i])
    val = {key: float(np.interp(r0, S["rs"], S[key])) for key in S if key not in ("rs",)}
    val["r"] = float(r0)
    R = val["R"]
    q = 4 * math.pi * R**2 * val["flux"]
    val["q"] = q
    val["dRdt_pred"] = 2 * math.pi * R**3 * val["a_flux_thin"] / (1 + q)
    # Hamiltonian constraint in Misner-Sharp form, at the MOTS and on its neighbours
    dm = np.gradient(S["M"], S["rs"])
    src = 4 * math.pi * S["R"] ** 2 * (S["rho"] * S["dRdr"] + S["j_s"] * S["R"] / 4 * (S["Tp"] + S["Tm"]) / S["lam"])
    val["dMdr"] = float(np.interp(r0, S["rs"], dm))
    val["src"] = float(np.interp(r0, S["rs"], src))
    val["rho_term"] = float(np.interp(r0, S["rs"], 4 * math.pi * S["R"] ** 2 * S["rho"] * S["dRdr"]))
    return val


def budget(S: dict, r0: float) -> None:
    """M_MS(r) - M_MS(r_mots) = int (phantom source) dr + int (constraint residual) dr."""
    rs = S["rs"]
    dm = np.gradient(S["M"], rs)
    src = 4 * math.pi * S["R"] ** 2 * (S["rho"] * S["dRdr"] + S["j_s"] * S["R"] / 4 * (S["Tp"] + S["Tm"]) / S["lam"])
    res = dm - src
    sel = rs >= r0
    rr = rs[sel]
    cs = np.concatenate([[0.0], np.cumsum(0.5 * (src[sel][1:] + src[sel][:-1]) * np.diff(rr))])
    cr = np.concatenate([[0.0], np.cumsum(0.5 * (res[sel][1:] + res[sel][:-1]) * np.diff(rr))])
    m0 = float(np.interp(r0, rs, S["M"]))
    print("      r      R        M_MS     M-M_mots   int(phantom src)  int(residual)")
    for k in range(0, rr.size, max(1, rr.size // 12)):
        print(f"      {rr[k]:.2f}  {S['R'][sel][k]:.4f}  {S['M'][sel][k]:.5f}  {S['M'][sel][k]-m0:+.5f}"
              f"   {cs[k]:+.5f}          {cr[k]:+.5f}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plt", nargs="+")
    ap.add_argument("--centre", nargs=3, type=float, required=True)
    ap.add_argument("--half", type=float, default=2.3)
    ap.add_argument("--levels", nargs="+", type=int, default=[3])
    ap.add_argument("--dr", type=float, default=0.01)
    ap.add_argument("--profile", action="store_true",
                    help="also print the Misner-Sharp budget outward from the MOTS: "
                         "M(r) - M(r_mots) split into the phantom source and the constraint residual")
    args = ap.parse_args()
    c = np.array(args.centre)
    rs = np.arange(0.6, args.half - 0.15, args.dr)
    print("plt  level  t  r_mots  R_mots  M_MS(area-wtd)  M_MS(plain mean)  2M/R  alpha  q  "
          "dR/dt_pred  dM/dr  src  (dM/dr-src)/rho_term")
    for p in args.plt:
        for lev in args.levels:
            F, dx, t = load(p, c, args.half, lev)
            S = shells(F, dx, args.half, rs)
            name = p.rstrip("/").split("/")[-1]
            for crit in ("out_max", "Tp"):
                v = at_mots(S, crit)
                if v is None:
                    print(f"{name} L{lev} t={t:.2f} [{crit}]: no MOTS")
                    continue
                print(f"{name} L{lev} [{crit:7s}] dx={dx:.5f} t={t:7.3f}  r={v['r']:.4f}  R={v['R']:.5f}"
                      f"  M={v['M']:.5f}  Mplain={v['M_plain']:.5f}  2M/R={2*v['M']/v['R']:.5f}"
                      f"  alpha={v['alpha']:.4f}  q={v['q']:.3e}  dRdt_pred={v['dRdt_pred']:+.3e}"
                      f"  dMdr={v['dMdr']:+.4e}  src={v['src']:+.4e}"
                      f"  resid/rho_term={(v['dMdr']-v['src'])/abs(v['rho_term']):+.3f}", flush=True)
                if args.profile and crit == "Tp":
                    budget(S, v["r"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
