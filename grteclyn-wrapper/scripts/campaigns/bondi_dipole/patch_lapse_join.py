#!/usr/bin/env python3
"""Join a solved pair's star-table lapse C^1 and write it into a copy of the pair.

Star tables built before 2026-10-22 (profiles/boson_star_ode.py) read the lapse's
alpha_inf as A + B/r at the match radius and gave the exterior lapse the conformal
factor's mass, so the tabulated lapse steps at the match (4e-5 at r = 5.2 for the
w075 pair).  The lapse does not enter the t = 0 constraints, so every t = 0 check
passes, but the evolution's first step turns the step into a momentum-constraint
violation that grows with resolution and caps the convergence order.

This rebuilds each table's lapse with the fixed join (_lapse_join): the interior
scaled by k, the exterior the Schwarzschild lapse with the lapse's own mass, value
and slope continuous.  The output episode's initial_data.gridinit differs from the
source only in its lapse, the superposed spline lapse of the joined tables as
GRTresna's BosonStarParams::total_alpha builds it.  chi, K, A_ij, phi and Pi stay as
solved: scaling a star's interior lapse and frequency by the same k leaves its
Im Pi = -omega phi / alpha unchanged, so only the companion's exterior lapse moves,
by ~(M_alpha - M) / d.  The solve's grtresna/ inputs are copied unchanged (they made
the matter); the joined tables sit beside them as *.lapsefix.dat.

Usage:
  patch_lapse_join.py <source episode dir> <output episode dir>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicSpline

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "analysis" / "bondi_dipole"))
from t0_constraints import open_gridinit, read_solver_params, read_star_table  # noqa: E402

COPIED = ("initial_data.matter.json", "metadata.json")


def lapse_join(alpha_m: float, dalpha_m: float, r_m: float) -> tuple[float, float]:
    """boson_star_ode._lapse_join: alpha_inf and x = M_alpha / (2 r_m)."""
    q = r_m * dalpha_m / (2.0 * alpha_m)
    x = q if abs(q) < 1.0e-12 else (math.sqrt(1.0 + 4.0 * q * q) - 1.0) / (2.0 * q)
    return alpha_m * (1.0 + x) / (1.0 - x), x


def schwarzschild_lapse(r: np.ndarray, mass: float) -> np.ndarray:
    half = 0.5 * mass / r
    return (1.0 - half) / (1.0 + half)


def header_mass(path: Path) -> float:
    for line in path.read_text().splitlines():
        if line.startswith("#") and "ADM_mass=" in line:
            return float(line.split("ADM_mass=")[1].split()[0])
    raise SystemExit(f"{path}: no ADM_mass in the header")


def join_table(r: np.ndarray, alpha: np.ndarray, mass_psi: float) -> dict:
    """The joined lapse of one table and the numbers that describe the join."""
    dr = np.diff(r)
    # The interior is uniform from the second knot (the first is the origin's
    # tiny step); the tail starts where the spacing jumps.
    jumps = np.where(dr[2:] > 1.5 * dr[1:-1])[0]
    if jumps.size == 0:
        raise SystemExit("no interior/tail join in the table")
    i = int(jumps[0]) + 2  # last interior knot
    h_in = float(dr[i - 1])
    if not np.allclose(dr[i - 5:i], h_in, rtol=1e-6):
        raise SystemExit(f"interior spacing not uniform before the join at r = {r[i]}")
    radius = float(r[i])
    a = alpha[i - 4:i + 1]
    slope = (25 * a[4] - 48 * a[3] + 36 * a[2] - 16 * a[1] + 3 * a[0]) / (12.0 * h_in)
    _, x = lapse_join(float(alpha[i]), float(slope), radius)
    k = (1.0 - x) / ((1.0 + x) * float(alpha[i]))
    m_alpha = 2.0 * x * radius
    joined = alpha.copy()
    joined[: i + 1] *= k
    joined[i + 1:] = schwarzschild_lapse(r[i + 1:], m_alpha)
    ext_slope = 2.0 * x / (radius * (1.0 + x) ** 2)
    return {
        "alpha_joined": joined,
        "join_r": radius,
        "step_before": float(schwarzschild_lapse(np.array([radius]), mass_psi)[0] - alpha[i]),
        "slope_gap_after": float(k * slope / ext_slope - 1.0),
        "k": float(k),
        "M_alpha": float(m_alpha),
        "M_psi": float(mass_psi),
    }


def write_table(src: Path, dst: Path, r: np.ndarray, phi0: np.ndarray, alpha: np.ndarray,
                note: str) -> None:
    head = [line for line in src.read_text().splitlines() if line.startswith("#")]
    body = [f"{a:.17g} {b:.17g} {c:.17g}" for a, b, c in zip(r, phi0, alpha)]
    dst.write_text("\n".join(head[:-1] + [note] + head[-1:] + body) + "\n")


def total_alpha(splines, ranges, centres, xyz) -> np.ndarray:
    """BosonStarParams::total_alpha on one slab: 1 + sum(alpha_k - 1), floored."""
    out = np.ones(np.broadcast_shapes(*(c.shape for c in xyz)))
    for spline, (r0, r1), c in zip(splines, ranges, centres):
        rk = np.sqrt((xyz[0] - c[0]) ** 2 + (xyz[1] - c[1]) ** 2 + (xyz[2] - c[2]) ** 2)
        out += spline(np.clip(rk, r0, r1)) - 1.0
    return np.maximum(out, 1.0e-3)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("source", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()
    src, out = args.source.resolve(), args.output.resolve()
    if out.exists():
        raise SystemExit(f"{out} exists; refusing to overwrite")

    params = read_solver_params(src / "grtresna" / "params.txt")
    lumps = []
    for k in range(int(params["num_lumps"][0])):
        table = Path(params[f"lump{k}_profile_path"][0])
        if not table.is_file():
            table = src / "grtresna" / table.name
        r, phi0, alpha = read_star_table(table)
        omega = float(params.get(f"lump{k}_bs_omega", params["bs_omega"])[0])
        lumps.append({"table": table, "r": r, "phi0": phi0, "alpha": alpha, "omega": omega,
                      "centre": np.array([float(v) for v in params[f"lump{k}_center"]]),
                      **join_table(r, alpha, header_mass(table))})

    (out / "grtresna").mkdir(parents=True)
    for name in COPIED:
        if (src / name).is_file():
            shutil.copy2(src / name, out / name)
    for item in (src / "grtresna").iterdir():
        if item.is_file():
            shutil.copy2(item, out / "grtresna" / item.name)
    for lump in lumps:
        note = (f"# lapse joined C^1 at r = {lump['join_r']:.10g} by patch_lapse_join.py: interior x k = "
                f"{lump['k']:.17g}, exterior mass {lump['M_alpha']:.17g}, omega {lump['omega']:.17g} -> "
                f"{lump['k'] * lump['omega']:.17g}")
        write_table(lump["table"], out / "grtresna" / (lump["table"].stem + ".lapsefix.dat"),
                    lump["r"], lump["phi0"], lump["alpha_joined"], note)

    names, data, dx, origin = open_gridinit(src / "initial_data.gridinit")
    il = names.index("lapse")
    dst = out / "initial_data.gridinit"
    shutil.copyfile(src / "initial_data.gridinit", dst)
    patched = np.memmap(dst, dtype=np.float64, mode="r+", offset=data.offset, shape=data.shape)
    nz, ny, nx = data.shape[:3]
    h = float(dx[0])
    centre = origin + 0.5 * h * np.array([nx, ny, nz])
    xs = [origin[a] + (np.arange(n) + 0.5) * h - centre[a] for a, n in enumerate((nx, ny, nz))]
    ranges = [(L["r"][0], L["r"][-1]) for L in lumps]
    centres = [L["centre"] for L in lumps]
    old_s = [CubicSpline(L["r"], L["alpha"], bc_type="natural") for L in lumps]
    new_s = [CubicSpline(L["r"], L["alpha_joined"], bc_type="natural") for L in lumps]
    others = [c for c in range(len(names)) if c != il]
    rebuild = change = 0.0
    for kz in range(nz):
        xyz = (xs[0][None, :], xs[1][:, None], np.full((1, 1), xs[2][kz]))
        lapse = np.asarray(data[kz, :, :, il])
        old = total_alpha(old_s, ranges, centres, xyz)
        if 0 < kz < nz - 1:
            rebuild = max(rebuild, float(np.max(np.abs(old - lapse)[1:-1, 1:-1])))
        # Added as a difference: the solve writes something else into the
        # box's outermost layer of cells (up to 1e-4 off total_alpha), kept.
        delta = total_alpha(new_s, ranges, centres, xyz) - old
        change = max(change, float(np.max(np.abs(delta))))
        patched[kz, :, :, il] = lapse + delta
    patched.flush()
    del patched
    # Inside the outermost layer the source's lapse must be exactly the old
    # tables' total_alpha, or this patch would correct something else.
    if rebuild > 1.0e-12:
        dst.unlink()
        raise SystemExit(f"source lapse is not the tables' total_alpha (max diff {rebuild:.3e})")
    check = np.memmap(dst, dtype=np.float64, mode="r", offset=data.offset, shape=data.shape)
    same = all(np.array_equal(np.asarray(check[kz][..., others]), np.asarray(data[kz][..., others]))
               for kz in range(nz))
    if not same:
        raise SystemExit("a component other than the lapse changed")

    record = {
        "source": str(src),
        "source_gridinit_sha256": sha256(src / "initial_data.gridinit"),
        "gridinit_sha256": sha256(dst),
        "source_lapse_rebuild_max_diff": rebuild,
        "lapse_max_change": change,
        "other_components_identical": same,
        "lumps": [{key: (str(v) if isinstance(v, Path) else v) for key, v in L.items()
                   if key not in ("r", "phi0", "alpha", "alpha_joined", "centre")}
                  | {"centre": L["centre"].tolist(), "omega_joined": L["k"] * L["omega"]}
                  for L in lumps],
    }
    (out / "lapse_patch.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"{out.name} N {nx}: source lapse = old tables' total_alpha to {rebuild:.1e}; "
          f"lapse changed by at most {change:.3e}; other components identical: {same}")
    for k, L in enumerate(lumps):
        print(f"  lump{k}: join r {L['join_r']:.4f}, step before {L['step_before']:+.3e}, "
              f"slope gap after {L['slope_gap_after']:+.1e}, k - 1 {L['k'] - 1:+.3e}, "
              f"M_alpha {L['M_alpha']:+.6f} vs M_psi {L['M_psi']:+.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
