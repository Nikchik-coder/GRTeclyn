#!/usr/bin/env python3
"""Split the t = 0 constraint violation of a Bondi pair's initial data by cause.

The packed d0 = 10 runs converge at order 1.5 at best, where the evolution's
stencils are fourth order (research/bondi_dipole/STATUS.md, track 2a).  This
reads one cell's t = 0 state -- the ``initial_data.gridinit`` the evolution
starts from -- and the inputs its GRTresna solve was given (``grtresna/params.txt``
and the star tables), and splits the Hamiltonian constraint on the interior
(r <= 24, inside the sponge) into

  solve      H4 - H2 with the solve's own matter: the second-order solve's
             truncation error as the evolution's fourth-order stencils see it;
  Im Pi      16 pi drho from the U(1) momentum: the solve divides by each star's
             own tabulated lapse, the painter by the summed lapse of the grid;
  interp     16 pi drho from the field values: the solve interpolates the star
             table linearly, the painter evaluates a cubic spline;
  table grad 16 pi drho from |grad phi|^2: the solve differences its linear
             interpolant at +-1e-3 width against the profile's exact derivative;
  stencil    the evolution's fourth-order gradient of the painted field against
             the same exact derivative (are the stars resolved on this grid?).

The pieces add up exactly:
  H4[painted] = solve + H2[solver] + Im Pi + interp + table grad + stencil.
H2[solver] is the solve's own discrete residual (GRTresna's Ham / 1.5,
Diagnostics.impl.hpp), so it must sit at the solve tolerance: that checks the
reconstruction of the solve's matter.  The momentum constraint is reported
too.  Run it on the N 128/192/256 cells and read the orders off the last
table.

Formulas: the evolution's constraints (Source/CCZ4/Constraints.impl.hpp,
ConstraintsWithMatter, G = 1) reduce for h_ij = delta_ij, Gamma = 0 to
  H = 2 lap(chi) - 5/2 |grad chi|^2 / chi + 2/3 K^2 - A_ij A_ij - 16 pi rho,
  M_i = d_j A_ij - 3/(2 chi) A_ij d_j chi - 2/3 d_i K - 8 pi j_i,
with the matter of BiComplexScalarField; the solve's matter is GRTresna's
ComplexScalarField::compute_emtensor (one star per lump, no cross terms) with
BosonStarParams' linear table interpolation and lump_grad_phi1.

Usage:
  t0_constraints.py <episode dir> [<episode dir> ...] [--radius 24]
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicSpline

FOUR_PI = 4.0 * math.pi
GHOST = 2  # fourth-order stencils reach two cells
BOUNDARY_SKIP = 4  # cells the evolution's boundary-masked norm drops


# --- gridinit (GRTECLYN_GRID_INIT_V2, grtresna/io/gridinit.py) ---------------

def open_gridinit(path: Path):
    """Header plus a read-only memmap of shape (nz, ny, nx, ncomp)."""
    with open(path, "rb") as fin:
        header = {}
        while True:
            line = fin.readline()
            if not line:
                raise ValueError(f"no END_HEADER in {path}")
            text = line.decode("ascii").strip()
            if text == "END_HEADER":
                break
            parts = text.split()
            if parts:
                header[parts[0]] = parts[1:]
        offset = fin.tell()
    names = header["component_names"]
    nx, ny, nz = (int(v) for v in header["nx_ny_nz"])
    dx = np.array([float(v) for v in header["dx"]])
    origin = np.array([float(v) for v in header["origin"]])
    data = np.memmap(path, dtype=np.float64, mode="r", offset=offset,
                     shape=(nz, ny, nx, len(names)))
    return names, data, dx, origin


# --- solver inputs (grtresna/params.txt, star tables) ------------------------

def read_solver_params(path: Path) -> dict[str, list[str]]:
    params = {}
    for line in path.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if "=" in line:
            key, value = line.split("=", 1)
            params[key.strip()] = value.split()
    return params


def read_star_table(path: Path):
    rows = [line.split() for line in path.read_text().splitlines()
            if line.strip() and not line.lstrip().startswith("#")]
    table = np.array([[float(v) for v in row[:3]] for row in rows])
    return table[:, 0], table[:, 1], table[:, 2]


def solver_lumps(params: dict[str, list[str]], grtresna_dir: Path) -> list[dict]:
    lumps = []
    for k in range(int(params["num_lumps"][0])):
        p = f"lump{k}_"
        if int(params.get(p + "profile", ["0"])[0]) != 3:
            raise SystemExit(f"lump {k}: only the tabulated star (profile 3) is handled")
        table_path = Path(params[p + "profile_path"][0])
        if not table_path.is_file():  # the run dir may have moved
            table_path = grtresna_dir / table_path.name
        r, phi0, alpha = read_star_table(table_path)
        omega = float(params.get(p + "bs_omega", ["0"])[0]) or float(params["bs_omega"][0])
        lumps.append({
            "center": np.array([float(v) for v in params[p + "center"]]),
            "amp": float(params[p + "amp"][0]),
            "width": float(params[p + "width"][0]),
            "omega": omega,
            "sign": -1.0 if int(params[p + "exotic"][0]) else 1.0,
            "r": r, "phi0": phi0, "alpha": alpha,
            # The table's own natural cubic spline stands in for the exact
            # profile; it is checked against the painted field below.
            "spline": CubicSpline(r, phi0, bc_type="natural"),
        })
    return lumps


# --- stencils on the core [GHOST, n - GHOST) of every axis -------------------

def shifted(f: np.ndarray, axis: int, s: int) -> np.ndarray:
    sl = [slice(GHOST, n - GHOST) for n in f.shape]
    sl[axis] = slice(GHOST + s, f.shape[axis] - GHOST + s)
    return f[tuple(sl)]


def d1(f: np.ndarray, axis: int, h: float, order: int) -> np.ndarray:
    if order == 4:
        return (shifted(f, axis, -2) - 8.0 * shifted(f, axis, -1)
                + 8.0 * shifted(f, axis, 1) - shifted(f, axis, 2)) / (12.0 * h)
    return (shifted(f, axis, 1) - shifted(f, axis, -1)) / (2.0 * h)


def d2(f: np.ndarray, axis: int, h: float, order: int) -> np.ndarray:
    if order == 4:
        return (-shifted(f, axis, -2) + 16.0 * shifted(f, axis, -1)
                - 30.0 * shifted(f, axis, 0) + 16.0 * shifted(f, axis, 1)
                - shifted(f, axis, 2)) / (12.0 * h * h)
    return (shifted(f, axis, -1) - 2.0 * shifted(f, axis, 0)
            + shifted(f, axis, 1)) / (h * h)


def core(f: np.ndarray) -> np.ndarray:
    return shifted(f, 0, 0)


def potential(mod2: np.ndarray, mass: float, lam: float, mu: float) -> np.ndarray:
    return 0.5 * mass * mass * mod2 - 0.25 * lam * mod2**2 + mu * mod2**3 / 6.0


# --- one cell ----------------------------------------------------------------

AXES = (2, 1, 0)  # x, y, z -> array axes of (nz, ny, nx)
SYM = {(0, 0): "A11", (0, 1): "A12", (0, 2): "A13", (1, 1): "A22", (1, 2): "A23",
       (2, 2): "A33"}


def a_name(i: int, j: int) -> str:
    return SYM[(min(i, j), max(i, j))]


def analyse(episode: Path, radius: float) -> dict:
    names, data, dx, origin = open_gridinit(episode / "initial_data.gridinit")
    if not np.allclose(dx, dx[0]):
        raise SystemExit(f"{episode}: anisotropic cells {dx}")
    h = float(dx[0])
    idx = {name: c for c, name in enumerate(names)}

    def field(name: str) -> np.ndarray:
        return np.ascontiguousarray(data[..., idx[name]])

    nz, ny, nx = data.shape[:3]
    centre = origin + 0.5 * h * np.array([nx, ny, nz])

    # The reductions below assume conformally flat, Gamma-free data.
    flat = {
        "h-delta": max(float(np.max(np.abs(field(n) - (1.0 if n[1] == n[2] else 0.0))))
                       for n in ("h11", "h12", "h13", "h22", "h23", "h33")),
        "Gamma": max(float(np.max(np.abs(field(n)))) for n in ("Gamma1", "Gamma2", "Gamma3")),
    }
    if flat["h-delta"] > 1e-12 or flat["Gamma"] > 1e-12:
        raise SystemExit(f"{episode}: not conformally flat / Gamma-free: {flat}")

    # Cell-centre coordinates of the core, relative to the grid centre.
    def axis_coords(n: int, a: int) -> np.ndarray:
        return origin[a] + (np.arange(GHOST, n - GHOST) + 0.5) * h - centre[a]
    xc = axis_coords(nx, 0)[None, None, :]
    yc = axis_coords(ny, 1)[None, :, None]
    zc = axis_coords(nz, 2)[:, None, None]
    r_centre = np.sqrt(xc**2 + yc**2 + zc**2)
    interior = r_centre <= radius
    gi = [np.arange(GHOST, n - GHOST) for n in (nz, ny, nx)]
    masked = ((gi[0] >= BOUNDARY_SKIP) & (gi[0] < nz - BOUNDARY_SKIP))[:, None, None] \
        & ((gi[1] >= BOUNDARY_SKIP) & (gi[1] < ny - BOUNDARY_SKIP))[None, :, None] \
        & ((gi[2] >= BOUNDARY_SKIP) & (gi[2] < nx - BOUNDARY_SKIP))[None, None, :]
    masked = np.broadcast_to(masked, r_centre.shape)

    chi = field("chi")
    chi_c = core(chi)
    K = field("K")
    A = {n: field(n) for n in SYM.values()}
    A_c = {n: core(v) for n, v in A.items()}
    AA = sum((1.0 if n[1] == n[2] else 2.0) * A_c[n] ** 2 for n in SYM.values())
    K2 = (2.0 / 3.0) * core(K) ** 2

    # Geometry: fourth order on chi (the evolution), second order on
    # psi = chi^(-1/4) with the 7-point Laplacian (the solve).
    lap4 = sum(d2(chi, a, h, 4) for a in AXES)
    grad4 = sum(d1(chi, a, h, 4) ** 2 for a in AXES)
    geo4 = 2.0 * lap4 - 2.5 * grad4 / chi_c + K2 - AA
    psi = chi ** -0.25
    lap2_psi = sum(d2(psi, a, h, 2) for a in AXES)
    geo2 = -8.0 * core(psi) ** -5 * lap2_psi + K2 - AA
    del lap4, grad4, psi, lap2_psi

    # Matter as the evolution paints and differences it.
    solver_dir = episode / "grtresna"
    params = read_solver_params(solver_dir / "params.txt")
    mass = float(params["scalar_mass"][0])
    lam = float(params["scalar_lambda"][0])
    mu = float(params["scalar_mu"][0])
    sectors = {  # sign -> (Re phi, Im phi, Re Pi, Im Pi); the C++ reader's names
        1.0: ("phi", "phi2", "Pi", "Pi2"),
        -1.0: ("phi_lump1", "phi_lump2", "Pi_lump1", "Pi_lump2"),
    }
    rho_p = np.zeros_like(chi_c)
    j_p = [np.zeros_like(chi_c) for _ in range(3)]
    painted = {}
    for sign, (re_phi, im_phi, re_pi, im_pi) in sectors.items():
        phi_re, phi_im = field(re_phi), field(im_phi)
        pi_re, pi_im = core(field(re_pi)), core(field(im_pi))
        g_re = [d1(phi_re, a, h, 4) for a in AXES]
        g_im = [d1(phi_im, a, h, 4) for a in AXES]
        mod2 = core(phi_re) ** 2 + core(phi_im) ** 2
        rho_p += sign * (0.5 * (pi_re**2 + pi_im**2)
                         + 0.5 * chi_c * sum(g**2 for g in g_re + g_im)
                         + potential(mod2, mass, lam, mu))
        for i in range(3):
            j_p[i] += sign * (-(pi_re * g_re[i] + pi_im * g_im[i]))
        painted[sign] = {
            "phi": core(phi_re), "pi": pi_im, "grad": g_re,
            "max_im_phi": float(np.max(np.abs(phi_im))),
            "max_re_pi": float(np.max(np.abs(pi_re))),
        }
        del phi_re, phi_im, g_im

    # Matter as the solve built it, lump by lump, plus the split of the
    # difference.  The split needs one lump per sector (the mixed pairs).
    lumps = solver_lumps(params, solver_dir)
    by_sector: dict[float, list[dict]] = {}
    for lump in lumps:
        by_sector.setdefault(lump["sign"], []).append(lump)
    split = all(len(v) == 1 for v in by_sector.values())
    lapse_c = core(field("lapse"))
    rho_s = np.zeros_like(chi_c)
    parts = {key: np.zeros_like(chi_c)
             for key in ("impi", "interp", "table_grad", "stencil")}
    checks = {}
    for k, lump in enumerate(lumps):
        rel = [xc - lump["center"][0], yc - lump["center"][1], zc - lump["center"][2]]
        r_k = np.sqrt(rel[0] ** 2 + rel[1] ** 2 + rel[2] ** 2)
        norm = lump["amp"] / lump["phi0"][0]

        def phi_lin(rr, lump=lump, norm=norm):
            return norm * np.interp(rr, lump["r"], lump["phi0"])

        phi_s = phi_lin(r_k)
        alpha_k = np.interp(r_k, lump["r"], lump["alpha"])
        eps = 1.0e-3 * lump["width"]
        g_s = []
        for a in range(3):
            plus = [c + (eps if b == a else 0.0) for b, c in enumerate(rel)]
            minus = [c - (eps if b == a else 0.0) for b, c in enumerate(rel)]
            g_s.append((phi_lin(np.sqrt(sum(c**2 for c in plus)))
                        - phi_lin(np.sqrt(sum(c**2 for c in minus)))) / (2.0 * eps))
        pi_s = -lump["omega"] * phi_s / alpha_k
        sign = lump["sign"]
        rho_s += sign * (0.5 * pi_s**2 + 0.5 * chi_c * sum(g**2 for g in g_s)
                         + potential(phi_s**2, mass, lam, mu))
        if not split:
            continue
        p = painted[sign]
        # Exact profile derivative along the radial unit vector.
        r_safe = np.where(r_k > 0.0, r_k, 1.0)
        dphi = norm * lump["spline"](r_k, 1)
        g_e = [dphi * c / r_safe for c in rel]
        gs2 = sum(g**2 for g in g_s)
        ge2 = sum(g**2 for g in g_e)
        gp2 = sum(g**2 for g in p["grad"])
        parts["impi"] += sign * (0.5 * (lump["omega"] * p["phi"] / alpha_k) ** 2
                                 - 0.5 * p["pi"] ** 2)
        parts["interp"] += sign * (0.5 * lump["omega"] ** 2 * (phi_s**2 - p["phi"] ** 2)
                                   / alpha_k**2
                                   + potential(phi_s**2, mass, lam, mu)
                                   - potential(p["phi"] ** 2, mass, lam, mu))
        parts["table_grad"] += sign * 0.5 * chi_c * (gs2 - ge2)
        parts["stencil"] += sign * 0.5 * chi_c * (ge2 - gp2)
        star = r_k <= 8.0
        checks[f"lump{k}"] = {
            # painted field against the table's spline (same profile?)
            "phi vs spline": float(np.max(np.abs(p["phi"] - norm * lump["spline"](r_k))[star])),
            # painted Im Pi against -omega phi / (grid lapse)
            "Pi vs -w phi/lapse": float(np.max(np.abs(p["pi"] + lump["omega"] * p["phi"]
                                                      / lapse_c)[star])),
            "own lapse - grid lapse (centre)": float(
                (alpha_k - lapse_c)[np.unravel_index(np.argmin(r_k), r_k.shape)]),
            "max |Im phi|": p["max_im_phi"],
            "max |Re Pi|": p["max_re_pi"],
        }

    h4 = geo4 - 4.0 * FOUR_PI * rho_p
    h2s = geo2 - 4.0 * FOUR_PI * rho_s
    h4s = geo4 - 4.0 * FOUR_PI * rho_s
    terms = {
        "H4 painted (evolution, t=0)": h4,
        "H2 solver (solve residual)": h2s,
        "solve: H4-H2, solver matter": h4s - h2s,
        "matter: 16pi(rho_s - rho_p)": 4.0 * FOUR_PI * (rho_s - rho_p),
    }
    if split:
        for key, label in (("impi", "  Im Pi: own vs summed lapse"),
                           ("interp", "  interp: linear vs spline"),
                           ("table_grad", "  table grad: interpolant FD"),
                           ("stencil", "  stencil: 4th-order grad")):
            terms[label] = 4.0 * FOUR_PI * parts[key]
    del geo4, geo2

    # Momentum constraint as the evolution evaluates it.
    g_chi = [d1(chi, a, h, 4) for a in AXES]
    mom2 = np.zeros_like(chi_c)
    for i in range(3):
        m_i = -(2.0 / 3.0) * d1(K, AXES[i], h, 4) - 2.0 * FOUR_PI * j_p[i]
        for j in range(3):
            m_i += d1(A[a_name(i, j)], AXES[j], h, 4) \
                - 1.5 * A_c[a_name(i, j)] * g_chi[j] / chi_c
        mom2 += m_i**2
    sums = {
        "max |A_ij|": max(float(np.max(np.abs(v))) for v in A.values()),
        "max |K|": float(np.max(np.abs(K))),
        "max |j|": float(np.max(np.sqrt(sum(jj**2 for jj in j_p)))),
    }

    def l2(f, mask):
        return float(np.sqrt(np.mean(f[mask] ** 2)))

    out = {
        "N": nx, "dx": h, "flat": flat, "sums": sums, "checks": checks, "split": split,
        "int": {k: l2(v, interior) for k, v in terms.items()},
        "amr": {k: l2(v, masked) for k, v in terms.items()},
        "linf_int": {k: float(np.max(np.abs(v[interior]))) for k, v in terms.items()},
    }
    out["int"]["M4 painted |Mom|"] = float(np.sqrt(np.mean(mom2[interior])))
    out["amr"]["M4 painted |Mom|"] = float(np.sqrt(np.mean(mom2[masked])))
    out["linf_int"]["M4 painted |Mom|"] = float(np.sqrt(np.max(mom2[interior])))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("episodes", nargs="+", type=Path,
                    help="episode dirs holding initial_data.gridinit and grtresna/")
    ap.add_argument("--radius", type=float, default=24.0,
                    help="interior radius about the grid centre (default 24, the sponge's inner edge)")
    args = ap.parse_args()

    results = []
    for ep in args.episodes:
        res = analyse(ep.resolve(), args.radius)
        results.append(res)
        print(f"\n== {ep}  N = {res['N']}, dx = {res['dx']:.6g}")
        print(f"   conformally flat: {res['flat']};  {res['sums']}")
        for lump, c in res["checks"].items():
            print(f"   {lump}: " + ", ".join(f"{k} {v:.3e}" for k, v in c.items()))
        print(f"   {'term':34s} {'L2 r<=' + format(args.radius, 'g'):>12s}"
              f" {'Linf r<=' + format(args.radius, 'g'):>12s} {'L2 bdry-masked':>15s}")
        for key in res["int"]:
            print(f"   {key:34s} {res['int'][key]:12.4e} {res['linf_int'][key]:12.4e}"
                  f" {res['amr'][key]:15.4e}")

    results.sort(key=lambda r: r["N"])
    if len(results) > 1:
        print("\n== orders of the interior L2 norms, p = ln(e1/e2) / ln(N2/N1)")
        pairs = list(zip(results[:-1], results[1:]))
        print(f"   {'term':34s} " + " ".join(f"{a['N']}->{b['N']:>4d}" for a, b in pairs))
        for key in results[0]["int"]:
            row = []
            for a, b in pairs:
                e1, e2 = a["int"].get(key), b["int"].get(key)
                ok = e1 and e2 and e1 > 0 and e2 > 0
                row.append(f"{math.log(e1 / e2) / math.log(b['N'] / a['N']):8.2f}" if ok
                           else f"{'-':>8s}")
            print(f"   {key:34s} " + " ".join(row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
