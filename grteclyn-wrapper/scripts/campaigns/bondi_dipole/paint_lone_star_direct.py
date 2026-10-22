#!/usr/bin/env python3
"""Paint a lone canonical star's initial data directly from the ODE profile.

No GRTresna, no Chombo conversion: the star's radial ODE solution (phi0, psi,
alpha to ~1e-10) is painted straight onto the evolution grid.  The continuum
data is an exact solution -- conformally flat, K = 0, A_ij = 0, j_i = 0
(Re Pi = Im phi = 0), Ham satisfied by the ODE itself -- so any violation a
run started from it shows is the evolution's own, at its own order.  The
splitter for the lone star's linear Hamiltonian growth (2026-10-22): if a run
from this data still grows at a resolution-independent rate, the defect is in
the GRTeclyn evolution; if it is clean, the growth is seeded by the
second-order elliptic solve's data.

The episode is cloned from a solved reference (its grtresna/ tables,
initial_data.matter.json and metadata.json), with only initial_data.gridinit
replaced; the reference's own gridinit is compared field by field as a check
(phi and Pi must agree to the painters' tolerance, chi and the lapse to the
solve's O(h^2)).

Usage:
  paint_lone_star_direct.py <reference episode dir> <output episode dir>
      [--omega 0.75] [--n N] [--l 64.0]
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np

WRAPPER = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(WRAPPER / "src"))
sys.path.insert(0, str(WRAPPER / "scripts" / "analysis" / "bondi_dipole"))

from t0_constraints import open_gridinit  # noqa: E402

from grteclyn_wrapper.grtresna.io.gridinit import (  # noqa: E402
    GRTECLYN_STATE_VARS,
    write_gridinit,
)
from grteclyn_wrapper.grtresna.profiles.boson_star_ode import (  # noqa: E402
    QBallCouplings,
    solve_selfgrav_at_omega,
)

# The bicomplex state layout the Bondi gridinits carry (33 comps).
COMPS = [
    "chi", "h11", "h12", "h13", "h22", "h23", "h33", "K",
    "A11", "A12", "A13", "A22", "A23", "A33", "Theta",
    "Gamma1", "Gamma2", "Gamma3", "lapse", "shift1", "shift2", "shift3",
    "B1", "B2", "B3",
    "phi", "Pi", "phi2", "Pi2",
    "phi_lump1", "Pi_lump1", "phi_lump2", "Pi_lump2",
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("reference", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--omega", type=float, default=0.75)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--l", type=float, default=64.0)
    args = ap.parse_args()
    ref, out = args.reference.resolve(), args.output.resolve()
    if out.exists():
        raise SystemExit(f"{out} exists; refusing to overwrite")

    meta = json.loads((ref / "initial_data.matter.json").read_text())
    mass = float(meta["scalar_mass"])
    lam = float(meta["scalar_lambda"])
    mu = float(meta["scalar_mu"])
    prof = solve_selfgrav_at_omega(
        QBallCouplings(mass=mass, lam=lam, mu=mu, omega=args.omega, phi_core=0.0),
        omega_phys=args.omega)
    print(f"star: omega {prof.omega:.12f} (asked {args.omega}), phi_c {prof.phi_c:.10f}, "
          f"ADM {prof.adm_mass:.8f}, table r <= {prof.r[-1]:g}")

    n, L = args.n, args.l
    h = L / n
    x = (np.arange(n) + 0.5) * h - 0.5 * L  # centred coordinates
    zz, yy, xx = np.meshgrid(x, x, x, indexing="ij")
    r = np.sqrt(xx**2 + yy**2 + zz**2)
    del xx, yy, zz
    rc = np.clip(r, prof.r[0], prof.r[-1])

    data = np.zeros((n, n, n, len(COMPS)), dtype=np.float64)
    idx = {c: i for i, c in enumerate(COMPS)}
    psi = prof.spline_psi(rc)
    data[..., idx["chi"]] = psi ** -4.0
    del psi
    for c in ("h11", "h22", "h33"):
        data[..., idx[c]] = 1.0
    lapse = prof.spline_alpha(rc)
    data[..., idx["lapse"]] = lapse
    phi = prof.spline_phi0(rc)
    data[..., idx["phi"]] = phi
    data[..., idx["Pi2"]] = -(prof.omega / lapse) * phi
    del rc, lapse, phi, r

    out.mkdir(parents=True)
    shutil.copytree(ref / "grtresna", out / "grtresna")
    for name in ("initial_data.matter.json", "metadata.json"):
        if (ref / name).is_file():
            shutil.copy2(ref / name, out / name)
    origin = np.array([32.0 - 0.5 * L] * 3)
    write_gridinit(data, COMPS, np.array([h, h, h]), origin,
                   out / "initial_data.gridinit")

    # Cross-check against the reference's solved gridinit at the same N.
    names_r, data_r, dx_r, _ = open_gridinit(ref / "initial_data.gridinit")
    if data_r.shape[:3] == (n, n, n) and abs(float(dx_r[0]) - h) < 1e-12:
        for c in ("phi", "Pi2", "chi", "lapse", "K", "A11", "Pi", "phi_lump1"):
            a = data[..., idx[c]]
            b = np.asarray(data_r[..., names_r.index(c)])
            print(f"  vs solved {c:9s}: max |diff| {np.max(np.abs(a - b)):.3e}")
    rec = {"reference": str(ref), "omega": prof.omega, "phi_c": prof.phi_c,
           "adm_mass": prof.adm_mass, "n": n, "l": L,
           "painted": "direct from the ODE profile (no GRTresna)"}
    (out / "direct_paint.json").write_text(json.dumps(rec, indent=2) + "\n")
    print(f"wrote {out / 'initial_data.gridinit'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
