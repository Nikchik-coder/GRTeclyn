#!/usr/bin/env python3
r"""The head-on remnant's horizon against the spherical first law (HFL-ho, 2026-10-01).

Sec. VI says the phantom can only shrink a horizon (the spherical first law,
verified symbolically in c_spherical_horizon_law.py), yet the mode-3 head-on's
star scan reads the common horizon GROWING over t = 51-60 (leg 3,
horizon_scan.dat, centre C: R 4.247 -> 4.580, M_MS 2.300 -> 2.362).  The scan's
round sphere only bounds a still-unround MOTS from inside (2 M_MS / R = 1.08 at
t = 51, 1.03 at t = 60), so the rise may be the surface rounding.  This script
settles it on the full-state plotfiles of HFL-ho (leg 3 replayed over
t = 50-60 with every plotfile kept):

  1. the MOTS of each plotfile by the spectral flow finder (ah_flow_finder.py:
     r = h(theta, phi) in real harmonics to --lmax, no star-shaped assumption);
  2. MEASURED: its areal radius R(t) from the found surface's area, and dR/dt
     by central differences between consecutive plotfiles;
  3. PREDICTED from one slice, c_horizon_first_law.py's law with averages over
     the found surface instead of a round shell:
         dR/dt = 2 pi R^3 < alpha f theta_in > / (1 + q),   q = 4 pi R^2 < f >,
         f = (Pi + s.grad phi)^2      (l = n + s, k = n - s, theta_in that of k)
     -- the phantom's influx alone, never positive;
  4. the influx the spherical law leaves out, gravitational: the shear of l on
     the surface enters Raychaudhuri as f -> f - |sigma|^2 / (8 pi); printed as
     its own rate so the two can be read apart.

Exact in spherical symmetry.  On the head-on's late, nearly round remnant the
surface averages are the quasi-spherical approximation; the surface's
deformation (max |a_lm| / a_00 over l >= 1) is printed beside every row.
Measured = predicted means the evolved horizon obeys Einstein + phantom there;
a measured rate above the prediction is positive null energy the numerical
solution carries at its horizon, or a surface not yet round enough for the law.

Runs on full-state plotfiles (chi, h, A, K, lapse, phi, Pi): one covering grid
per plotfile, cached per plotfile in --json, so a re-run does only new ones.
Background and niced:

    OMP_NUM_THREADS=8 nice -n 19 grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/analysis/merger_feedback/headon_first_law.py \
        --json OUT.json [--level 3] [--half 4.5] [--lmax 6] PLT [PLT ...]
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys
import warnings

import numpy as np

warnings.filterwarnings("ignore")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "validation"))

import ah_flow_finder as aff  # noqa: E402

SYM = ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))
EXTRA = ("lapse", "phi", "Pi")


def load(plt: str, centre: np.ndarray, half: float, level: int) -> tuple[dict, float, float, int]:
    """The flow finder's full state plus lapse, phi and Pi, all on one covering grid."""
    import yt

    yt.set_log_level(40)
    ds = yt.load(plt)
    lev = int(min(level, ds.index.max_level))
    # A covering grid fills what its level does not cover by injecting coarser cells, whose
    # finite differences are staircases: the head-on's level 4 is the cube +-2.5 about the
    # centre, its horizon at r = 3.0-3.4 (2026-10-01).  Refuse a box the level does not cover.
    grids = [g for g in ds.index.grids if g.Level == lev]
    lo = np.min([g.LeftEdge.d for g in grids], axis=0)
    hi = np.max([g.RightEdge.d for g in grids], axis=0)
    if np.any(centre - half < lo - 1.0e-9) or np.any(centre + half > hi + 1.0e-9):
        raise SystemExit(f"level {lev} covers {np.round(lo - centre, 3)} .. {np.round(hi - centre, 3)} about the "
                         f"centre, not the box +-{half}: take a coarser --level or a smaller --half")
    fields, dx = aff.covering_fields(ds, centre, half, level)
    N = fields["chi"].shape[0]
    cg = ds.covering_grid(lev, left_edge=centre - half, dims=[N] * 3)
    for name in EXTRA:
        fields[name] = np.asarray(cg[("boxlib", name)], dtype=np.float64)
    return fields, dx, float(ds.current_time), lev


def find_mots(box: aff.Box, seeds: list[float], steps: int) -> aff.FlowResult | None:
    """The outermost converged surface over the seeds (outer seeds flow onto the apparent horizon)."""
    best = None
    for r0 in seeds:
        res = aff.flow(box, r0, steps=steps)
        print(f"    seed r0 = {r0:.3f}: {res.reason}; steps {res.steps}, rms theta_out {res.rms_theta:.2e},"
              f" R {res.R_areal:.5f}, h [{res.h_min:.3f}, {res.h_max:.3f}], deform {res.deform:.3f}", flush=True)
        if res.converged and (best is None or res.R_areal > best.R_areal):
            best = res
    return best


def refine(box: aff.Box, a_lm: np.ndarray, tol: float, iters: int = 40, nth: int = 32, nph: int = 64):
    """Newton on the flow's own residual: theta_out projected on the box's harmonics.

    The flow stops at rms theta_out < 2e-3, which leaves R uncertain by ~0.02 here
    (two seeds of one plotfile, 2026-10-01) -- ten times the rate the law predicts
    per unit.  Near round, the MOTS stability operator is diagonal in l, so its
    eigenvalue per l, read off the m = 0 mode by one finite difference, gives a
    Newton step for every a_lm.  Stops when every projected harmonic of theta_out
    is below tol: a MOTS to the resolved harmonics."""
    th, ph, TH, PH, _ = aff._quadrature(nth, nph)
    ylm_q = np.stack([aff._real_ylm(l, m, TH, PH) for l, m in box.pairs])
    w = np.sin(TH) * (th[1] - th[0]) * (ph[1] - ph[0])

    def resid(a):
        st = aff.surface_expansion(box, a, nth, nph)
        return np.einsum("tp,ktp->k", st.theta_out * w, ylm_q)

    a = np.array(a_lm, dtype=float)
    T = resid(a)
    ls = np.array([l for l, _ in box.pairs])
    lam = {}
    for l in sorted(set(ls.tolist())):
        k = box.pairs.index((l, 0))
        eps = 1.0e-3 * a[0]
        ap = a.copy()
        ap[k] += eps
        lam[l] = (resid(ap)[k] - T[k]) / eps
    J = np.array([lam[l] for l in ls])
    it = 0
    for it in range(1, iters + 1):
        if np.max(np.abs(T)) < tol:
            break
        step = T / J
        for _ in range(6):      # backtrack if a full Newton step makes the residual worse
            try:
                Tn = resid(a - step)
            except FloatingPointError:
                step *= 0.5
                continue
            if np.max(np.abs(Tn)) < np.max(np.abs(T)):
                break
            step *= 0.5
        else:
            break
        a, T = a - step, Tn
    return a, it, float(np.max(np.abs(T)))


def surface_terms(box: aff.Box, F3: dict, a_lm: np.ndarray, nth: int = 48, nph: int = 96) -> dict:
    """Area-weighted averages over r = h(theta, phi) of everything the law needs."""
    from scipy.ndimage import map_coordinates

    th, ph, TH, PH, nvec = aff._quadrature(nth, nph)
    ylm_q = np.stack([aff._real_ylm(l, m, TH, PH) for l, m in box.pairs])
    hgrid = np.einsum("k,ktp->tp", a_lm, ylm_q)
    area = aff._surface_area(box, hgrid, th, ph, nvec)
    sgn = 1.0 if aff._surface_area(box, hgrid * 1.02, th, ph, nvec) >= area else -1.0

    # the level set's outward unit normal, covariant and contravariant
    F = box.r - np.einsum("k,kxyz->xyz", a_lm, box.ylm_grid)
    dF = np.stack(np.gradient(F, box.dx))
    s_up = np.einsum("ab...,b...->a...", box.gam_inv, dF)
    lam = np.sqrt(np.clip(np.einsum("a...,a...->...", s_up, dF), 1.0e-30, None))
    s_up *= sgn / lam
    s_dn = dF * (sgn / lam)
    div = sum(np.gradient(box.sqg * s_up[a], box.dx, axis=a) for a in range(3)) / box.sqg
    KSS = np.einsum("ab...,a...,b...->...", box.Kphys, s_up, s_up)
    th_out = div + KSS - box.K          # l = n + s
    th_in = -div + KSS - box.K          # k = n - s

    dphi = np.stack(np.gradient(F3["phi"], box.dx))
    flux = (F3["Pi"] + np.einsum("a...,a...->...", s_up, dphi)) ** 2

    # shear of l: Theta_ij = D_i s_j - K_ij projected on the surface, |sigma|^2 = |Theta|^2 - theta^2 / 2
    gam = box.h / box.chi
    dgam = np.stack([np.gradient(gam[a, b], box.dx) for a in range(3) for b in range(3)]).reshape(3, 3, 3, *gam.shape[2:])
    # dgam[a, b, k] = d_k gamma_ab;  Gamma^c_ij s_c = gamma^{cl} Gamma_lij s_c,  Gamma_lij = (d_i g_jl + d_j g_il - d_l g_ij) / 2
    Gam_l = 0.5 * (np.einsum("jli...->lij...", dgam) + np.einsum("ilj...->lij...", dgam) - np.einsum("ijl...->lij...", dgam))
    Gs = np.einsum("lij...,l...->ij...", Gam_l, s_up)
    Ds = np.stack([np.gradient(s_dn[b], box.dx) for b in range(3)])          # [b, i] = d_i s_b
    Theta = np.einsum("bi...->ib...", Ds) - Gs - box.Kphys                  # [i, j] = D_i s_j - K_ij
    P = np.eye(3)[:, :, None, None, None] - np.einsum("i...,k...->ik...", s_dn, s_up)   # P_i^k
    ThS = np.einsum("ik...,jl...,kl...->ij...", P, P, Theta)
    ThS = 0.5 * (ThS + np.einsum("ij...->ji...", ThS))
    tr = np.einsum("ij...,ij...->...", box.gam_inv, ThS)
    sig2 = np.einsum("ik...,jl...,ij...,kl...->...", box.gam_inv, box.gam_inv, ThS, ThS) - 0.5 * tr**2

    pts = nvec * hgrid[None, :, :]
    flat = ((pts + box.half) / box.dx - 0.5).reshape(3, -1)
    on = lambda f: map_coordinates(f, flat, order=1).reshape(hgrid.shape)  # noqa: E731
    S = {k: on(v) for k, v in dict(th_out=th_out, th_in=th_in, alpha=F3["lapse"], flux=flux, sig2=sig2).items()}

    # the induced area element, as aff._surface_area
    chi_s = on(box.chi)
    gS = np.empty((3, 3) + hgrid.shape)
    for a, b in SYM:
        gS[a, b] = gS[b, a] = on(box.h[a, b]) / chi_s
    dth = np.gradient(pts, th, axis=1)
    dph = np.gradient(pts, ph, axis=2)
    E = np.einsum("abtp,atp,btp->tp", gS, dth, dth)
    F2 = np.einsum("abtp,atp,btp->tp", gS, dth, dph)
    G = np.einsum("abtp,atp,btp->tp", gS, dph, dph)
    dA = np.sqrt(np.clip(E * G - F2 * F2, 0.0, None)) * (th[1] - th[0]) * (ph[1] - ph[0])
    A = float(dA.sum())
    avg = lambda q: float((q * dA).sum() / A)  # noqa: E731

    # the shape: coordinate extent along each axis (mean of the two poles), so the ringing's
    # prolate-oblate swing between the axes shows from row to row
    axes = {}
    for name, (t1, p1, t2, p2) in dict(x=(0.5 * math.pi, 0.0, 0.5 * math.pi, math.pi),
                                       y=(0.5 * math.pi, 0.5 * math.pi, 0.5 * math.pi, 1.5 * math.pi),
                                       z=(0.0, 0.0, math.pi, 0.0)).items():
        hh = [sum(c * aff._real_ylm(l, m, np.array(tt), np.array(pp)) for c, (l, m) in zip(a_lm, box.pairs))
              for tt, pp in ((t1, p1), (t2, p2))]
        axes[f"h{name}"] = float(0.5 * (hh[0] + hh[1]))

    R = math.sqrt(A / (4.0 * math.pi))
    f_eff = S["flux"] - S["sig2"] / (8.0 * math.pi)
    q = 4.0 * math.pi * R**2 * avg(S["flux"])
    q_eff = 4.0 * math.pi * R**2 * avg(f_eff)
    pred_phantom = 2.0 * math.pi * R**3 * avg(S["alpha"] * S["flux"] * S["th_in"]) / (1.0 + q)
    pred_total = 2.0 * math.pi * R**3 * avg(S["alpha"] * f_eff * S["th_in"]) / (1.0 + q_eff)
    return dict(
        R=R, area=A, M_MS=0.5 * R * (1.0 + R**2 * avg(S["th_out"] * S["th_in"]) / 4.0),
        th_out_rms=math.sqrt(avg(S["th_out"] ** 2)), th_in_mean=avg(S["th_in"]), th_in_max=float(S["th_in"].max()),
        alpha=avg(S["alpha"]), flux=avg(S["flux"]), sig2=avg(S["sig2"]), q=q, q_eff=q_eff,
        dRdt_phantom=pred_phantom, dRdt_total=pred_total, dRdt_shear=pred_total - pred_phantom,
        h_min=float(hgrid.min()), h_max=float(hgrid.max()), **axes,
    )


def analyse(plt: str, args, warm: list[float] | None) -> dict | None:
    """warm: a_lm of a nearby MOTS (the previous plotfile's, or this one's at another level).
    Newton from it is ~20 residual evaluations where the flow from round seeds is ~400;
    the flow is the fallback, and the first plotfile's only start."""
    centre = np.asarray(args.centre, dtype=float)
    fields, dx, t, lev = load(plt, centre, args.half, args.level)
    print(f"  {pathlib.Path(plt).name}: t = {t:.3f}, level {lev} (dx {dx:.5f}), half {args.half}, lmax {args.lmax}",
          flush=True)
    box = aff.build_box({k: fields[k] for k in aff.STATE_FIELDS}, dx, args.half, args.lmax)
    a_lm = None
    steps, rms_flow, R_flow = 0, math.nan, math.nan
    if warm is not None:
        a0 = np.zeros(len(box.pairs))   # pairs run l = 0..lmax, so another lmax's a_lm pads or truncates
        a0[:min(a0.size, len(warm))] = warm[:a0.size]
        try:
            a_lm, its, resid = refine(box, a0, args.tol)
            print(f"    warm start: Newton {its} iterations, max |theta_out_lm| {resid:.1e}", flush=True)
            if resid >= args.tol:
                a_lm = None
        except FloatingPointError as err:
            print(f"    warm start failed ({err}); flowing from seeds", flush=True)
    if a_lm is None:
        res = find_mots(box, sorted(args.seeds, reverse=True), args.steps)
        if res is None:
            print("    no MOTS found from any seed", flush=True)
            return None
        steps, rms_flow, R_flow = res.steps, res.rms_theta, res.R_areal
        a_lm, its, resid = refine(box, res.a_lm, args.tol)
        print(f"    Newton refinement: {its} iterations, max |theta_out_lm| {resid:.1e} (tol {args.tol:.0e})",
              flush=True)
    out = surface_terms(box, {k: fields[k] for k in EXTRA}, a_lm)
    out.update(t=t, level=lev, dx=dx, lmax=args.lmax, steps=steps, rms_flow=rms_flow,
               newton_iters=its, newton_resid=resid, R_flow=R_flow,
               deform=float(np.max(np.abs(a_lm[1:])) / abs(a_lm[0])),
               r_mean=float(a_lm[0] / math.sqrt(4.0 * math.pi)), a_lm=[float(x) for x in a_lm])
    return out


def report(rows: list[dict]) -> None:
    rows = sorted(rows, key=lambda r: r["t"])
    t = np.array([r["t"] for r in rows])
    R = np.array([r["R"] for r in rows])
    meas = np.gradient(R, t) if len(rows) > 1 else np.full(1, np.nan)
    print("\n    t      R_mots    M_MS    h_x    h_y    h_z   rms_th_out   alpha     <f>        <sig2>     "
          "dR/dt meas   pred phantom   pred +shear")
    for r, m in zip(rows, meas):
        print(f"  {r['t']:6.2f}  {r['R']:.5f}  {r['M_MS']:.5f}  {r.get('hx', math.nan):.3f}  {r.get('hy', math.nan):.3f}"
              f"  {r.get('hz', math.nan):.3f}  {r['th_out_rms']:.2e}  {r['alpha']:.4f}  {r['flux']:.3e}  {r['sig2']:.3e}  "
              f"{m:+.3e}    {r['dRdt_phantom']:+.3e}     {r['dRdt_total']:+.3e}")
    if len(rows) > 1:
        trap = lambda y: float(np.sum(0.5 * (y[1:] + y[:-1]) * np.diff(t)))  # noqa: E731
        ph = np.array([r["dRdt_phantom"] for r in rows])
        tot = np.array([r["dRdt_total"] for r in rows])
        print(f"\n  over t = {t[0]:.2f}-{t[-1]:.2f}: R measured {R[-1] - R[0]:+.5f};"
              f" predicted by the phantom {trap(ph):+.5f}, with the shear {trap(tot):+.5f}"
              f"  (M = R/2: halve these)")


def selftest() -> int:
    """surface_terms against two analytic answers; run before trusting a plotfile row."""
    trap = getattr(np, "trapezoid", None) or np.trapz
    fails = 0

    # 1. Kerr-Schild Schwarzschild, M = 0.5: the flow finds R = 2M = 1, where
    #    theta_in = -(2 alpha / r)(1 + 2M/r) = -2 sqrt 2; no shear, no flux, zero predicted rate
    M, half, dx = 0.5, 1.6, 0.025
    X, r = aff._grid(half, dx)
    n = X / r
    delta = np.eye(3)[:, :, None, None, None]
    nn = n[:, None] * n[None, :]
    alpha = 1.0 / np.sqrt(1.0 + 2 * M / r)
    box = aff.build_box(aff._conformal_fields(delta + (2 * M / r) * nn,
                                              (2 * M * alpha / r**2) * (delta - (2 + M / r) * nn)), dx, half, 4)
    res = aff.flow(box, 1.3)
    zero = np.zeros_like(alpha)
    S = surface_terms(box, dict(lapse=alpha, phi=zero, Pi=zero), res.a_lm)
    exact = -2.0 * math.sqrt(2.0)
    ok = (res.converged and abs(S["R"] - 1.0) < 0.01 and abs(S["th_in_mean"] / exact - 1.0) < 0.02
          and S["sig2"] < 1.0e-3 * exact**2 and abs(S["dRdt_total"]) < 1.0e-3)
    fails += not ok
    print(f"schwarzschild: {'PASS' if ok else 'FAIL'}  R {S['R']:.5f} (1)  <theta_in> {S['th_in_mean']:.4f} ({exact:.4f})"
          f"  <|sigma|^2> {S['sig2']:.2e} (0)  dR/dt pred {S['dRdt_total']:+.2e} (0)")

    # 2. flat space, a prolate spheroid (a, a, c): with K = 0, Theta_ab is the surface's extrinsic curvature,
    #    so <theta_out^2> = <(k_m + k_p)^2> and <|sigma|^2> = <(k_m - k_p)^2 / 2>, area-weighted
    aa, cc, half, dx, lmax = 1.0, 1.15, 1.6, 0.025, 6
    N = int(round(2 * half / dx))
    one, zero = np.ones((N, N, N)), np.zeros((N, N, N))
    f = {k: zero for k in aff.STATE_FIELDS}
    f.update(chi=one, h11=one, h22=one, h33=one)
    box = aff.build_box(f, dx, half, lmax)
    th = np.linspace(0.005, math.pi - 0.005, 240)
    ph = np.linspace(0.0, 2.0 * math.pi, 240, endpoint=False)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    hs = 1.0 / np.sqrt(np.sin(TH) ** 2 / aa**2 + np.cos(TH) ** 2 / cc**2)
    Y = np.stack([aff._real_ylm(l, m, TH, PH) for l, m in box.pairs]).reshape(len(box.pairs), -1)
    w = np.sqrt(np.sin(TH).ravel())
    a_lm = np.linalg.lstsq((Y * w).T, hs.ravel() * w, rcond=None)[0]
    S = surface_terms(box, dict(lapse=one, phi=zero, Pi=zero), a_lm)
    u = np.linspace(0.0, math.pi, 20001)
    W = np.sqrt(aa**2 * np.cos(u) ** 2 + cc**2 * np.sin(u) ** 2)
    km, kp = aa * cc / W**3, cc / (aa * W)
    dA = aa * np.sin(u) * W
    mean = lambda q: float(trap(q * dA, u) / trap(dA, u))  # noqa: E731
    area_x, H2_x, sig2_x = 2.0 * math.pi * float(trap(dA, u)), mean((km + kp) ** 2), mean(0.5 * (km - kp) ** 2)
    ok = (abs(S["area"] / area_x - 1.0) < 2.0e-3 and abs(S["th_out_rms"] ** 2 / H2_x - 1.0) < 0.02
          and abs(S["sig2"] / sig2_x - 1.0) < 0.05)
    fails += not ok
    print(f"flat spheroid c/a = {cc}: {'PASS' if ok else 'FAIL'}  area {S['area']:.5f} ({area_x:.5f})"
          f"  <theta_out^2> {S['th_out_rms']**2:.5f} ({H2_x:.5f})  <|sigma|^2> {S['sig2']:.5f} ({sig2_x:.5f})")
    return int(fails > 0)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plt", nargs="*")
    ap.add_argument("--selftest", action="store_true", help="the two analytic checks of the surface terms, then exit")
    ap.add_argument("--json", help="per-plotfile cache; a re-run analyses only plotfiles not in it")
    ap.add_argument("--centre", nargs=3, type=float, default=[64.0, 64.0, 64.0])
    ap.add_argument("--level", type=int, default=3)
    ap.add_argument("--half", type=float, default=4.5)
    ap.add_argument("--lmax", type=int, default=6)
    ap.add_argument("--seeds", nargs="+", type=float, default=[3.2, 2.6])
    ap.add_argument("--steps", type=int, default=400)
    ap.add_argument("--tol", type=float, default=1.0e-6,
                    help="Newton refinement: every projected harmonic of theta_out below this")
    ap.add_argument("--warm-json", help="start each plotfile from its surface in this cache (another level), "
                                        "not from the previous plotfile's")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not (args.plt and args.json):
        ap.error("plotfiles and --json are required (or --selftest)")

    path = pathlib.Path(args.json)
    cache = json.loads(path.read_text()) if path.exists() else {}
    other = json.loads(pathlib.Path(args.warm_json).read_text()) if args.warm_json else {}
    tag = f"|L{args.level}|lmax{args.lmax}|half{args.half}|tol{args.tol:.0e}"
    key = lambda p: pathlib.Path(p.rstrip("/")).name + tag  # noqa: E731
    warm = None
    for p in sorted(args.plt):
        k = key(p)
        if k in cache:
            warm = cache[k]["a_lm"]
            continue
        name = pathlib.Path(p.rstrip("/")).name + "|"
        same = [v["a_lm"] for kk, v in other.items() if kk.startswith(name)]
        row = analyse(p, args, same[0] if same else warm)
        if row is None:
            continue
        cache[k] = row
        warm = row["a_lm"]
        path.write_text(json.dumps(cache, indent=1))
    rows = [v for k, v in cache.items() if k.endswith(tag)]
    report(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
