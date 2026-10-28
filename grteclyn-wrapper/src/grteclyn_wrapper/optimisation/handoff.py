"""The hand-off of a solved matter background to the evolution (step 7).

``optimize_potential.py`` saves each best point as .npz (the solved
collocation fields in grid units, eta0 = 1, plus sigma, psi_minus, the map
and the potential's coefficients; its ``conventions`` meta string).  This
module writes it as a background table for Examples/SpinningWormhole: the
published SPINBG_V1 format (analysis/spinning_wormhole/backgrounds.py) with
two additions the reader takes as optional --

    B                  a 7th column after the six published ones: the
                       fourth metric function, p = B^2 on the spatial
                       metric (a 6-column table means B == 1);
    potential_coeffs   a header line ``potential_coeffs a0 a1 ... an``:
                       the evolution's V(phi) = sum a_k phi^k in the
                       table's units (absent means no potential term).

Units.  Physical lengths are sigma times the grid's, so the table's eta0 is
sigma, omega = W / sigma, d_eta omega = d_eta W / sigma^2 and
(d_theta omega) / sin theta = (d_theta W) / (sigma sin theta).  The scalar
is phi = psi / sqrt(4 pi) and V = cal V / (8 pi), so the solver's physical
cal V(psi) = sum c_k psi^k gives a_k = c_k (4 pi)^(k/2) / (8 pi).
``rescale`` = lambda maps eta -> lambda eta as in backgrounds.full_background
(omega / lambda, d_eta omega / lambda^2, eta0, R_e and J by lambda,
lambda^2), and a_k / lambda^2: cal V is a curvature.

    python -m grteclyn_wrapper.optimisation.handoff <npz> --out <table>
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole.backgrounds import (
    COMPONENT_NAMES,
    MAGIC,
    read_spinbg,
)
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import (
    MAPS,
    cheb_eval,
    lobatto,
)

#: the published six columns, then B
MATTER_COMPONENTS = COMPONENT_NAMES + ("B",)


def write_matter_spinbg(path, eta0, x, mu, components, meta=None,
                        potential_coeffs=None) -> None:
    """A 7-column SPINBG_V1 table (module docstring); the grid and shape
    checks of backgrounds.write_spinbg."""
    x = np.asarray(x, dtype=np.float64)
    mu = np.asarray(mu, dtype=np.float64)
    for grid, name in ((x, "x"), (mu, "mu")):
        steps = np.diff(grid)
        if grid.ndim != 1 or grid.size < 2 or not np.allclose(
                steps, steps[0], rtol=0, atol=1e-13):
            raise ValueError(f"{name} grid must be uniform, 1D, >= 2 points")
    if not (mu[0] == 0.0 and abs(mu[-1] - 1.0) < 1e-15):
        raise ValueError("mu grid must span [0, 1]")
    if eta0 <= 0.0:
        raise ValueError("eta0 must be > 0")
    if set(components) != set(MATTER_COMPONENTS):
        raise ValueError(f"components must be exactly {MATTER_COMPONENTS}")
    body = np.stack([np.asarray(components[n], dtype=np.float64)
                     for n in MATTER_COMPONENTS], axis=-1)
    if body.shape != (mu.size, x.size, len(MATTER_COMPONENTS)):
        raise ValueError(f"component arrays must be (n_mu, n_x); stacked "
                         f"shape is {body.shape}")
    header = [
        MAGIC,
        f"eta0 {float(eta0)!r}",
        f"n_x {x.size}",
        f"n_mu {mu.size}",
        f"x_min {float(x[0])!r}",
        f"x_max {float(x[-1])!r}",
        f"num_components {len(MATTER_COMPONENTS)}",
        "component_names " + " ".join(MATTER_COMPONENTS),
    ]
    if potential_coeffs is not None:
        header.append("potential_coeffs " + " ".join(
            repr(float(c)) for c in potential_coeffs))
    header += [f"meta {line}" for line in meta or []]
    header.append("END_HEADER")
    with Path(path).open("wb") as fh:
        fh.write(("\n".join(header) + "\n").encode("ascii"))
        body.tofile(fh)


def matter_background(solution_path, n_x: int, n_mu: int,
                      rescale: float = 1.0):
    """The saved solve on the table grid: (x, mu, the seven columns, the
    evolution's potential coefficients, the solve's numbers)."""
    z = np.load(solution_path)
    meta = json.loads(str(z["meta"]))
    sx, sy = np.asarray(z["sx"]), np.asarray(z["sy"])
    _, dx = lobatto(sx.size - 1)
    _, dy = lobatto(sy.size - 1)
    params = dict(meta["radial_map"])
    name = params.pop("name")
    params.pop("class", None)
    params.pop("eta0", None)
    grid = MAPS[name](eta0=1.0, **params)

    x = np.linspace(-1.0, 1.0, n_x)
    mu = np.linspace(0.0, 1.0, n_mu)
    y = 2.0 * mu * mu - 1.0
    xi = grid.xi_of_eta(
        np.tan(0.5 * math.pi * np.clip(x, -1 + 1e-16, 1 - 1e-16)))
    xi[0], xi[-1] = -1.0, 1.0

    def on_table(a, xi=xi, y=y):
        rows = cheb_eval(sx, np.asarray(a), xi)      # (n_xi, ny + 1)
        return cheb_eval(sy, rows.T, y)              # (n_y, n_xi)

    W = np.asarray(z["W"])
    with np.errstate(divide="ignore", invalid="ignore"):
        deta = grid.deta(xi)[None, :]
        dw_deta = np.where(np.isfinite(deta), on_table(dx @ W) / deta, 0.0)
    dw_dth_over_s = -4.0 * mu[:, None] * on_table(W @ dy.T)

    lam = float(rescale)
    scale = lam * float(meta["sigma"])
    comps = {
        "f": on_table(z["F"]),
        "nu_bar": on_table(z["N"]),
        "omega": on_table(W) / scale,
        "domega_deta": dw_deta / scale**2,
        "domega_dtheta_over_sintheta": dw_dth_over_s / scale,
        "phi": on_table(z["PSI"]) / math.sqrt(4.0 * math.pi),
        "B": on_table(z["B"]),
    }
    coeffs = [c * (4.0 * math.pi) ** (0.5 * k) / (8.0 * math.pi) / lam**2
              for k, c in enumerate(meta["potential_coeffs"])]

    phi_minus = float(meta["psim"]) / math.sqrt(4.0 * math.pi)
    xm = 0.5 * (x[:-1] + x[1:])
    ym = 0.5 * (y[:-1] + y[1:])
    xim = grid.xi_of_eta(np.tan(0.5 * math.pi * xm))
    f_tab = comps["f"]
    bilin = 0.25 * (f_tab[:-1, :-1] + f_tab[:-1, 1:]
                    + f_tab[1:, :-1] + f_tab[1:, 1:])
    info = {
        "table_eta0": scale,
        "sigma": float(meta["sigma"]),
        "table_R_e": lam * float(meta["R_e"]),
        "table_J": lam * lam * float(meta["J"]),
        "X": float(meta["X"]),
        "X_v0": meta.get("X_v0"),
        "E19": float(meta["E19"]),
        "E_c": float(meta["E_c"]),
        "m": float(meta["m"]),
        "psi_minus": float(meta["psim"]),
        "phi_minus": phi_minus,
        "V_at_phi_minus": sum(a * phi_minus**k for k, a in enumerate(coeffs)),
        "B_min": float(comps["B"].min()),
        "B_max": float(comps["B"].max()),
        "midpoint_err_f_bilinear": float(np.max(np.abs(
            on_table(z["F"], xim, ym) - bilin))),
        "lam_eta0_J0": meta.get("lam_eta0"),
    }
    return x, mu, comps, coeffs, info


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("solution", help="optimize_potential.py .npz path")
    ap.add_argument("--n-x", type=int, default=2049)
    ap.add_argument("--n-mu", type=int, default=129)
    ap.add_argument("--rescale", type=float, default=1.0,
                    help="lambda of eta -> lambda eta at write time "
                         "(default 1: the solve's physical scale)")
    ap.add_argument("--out", help="output .spinbg path (omit: numbers only)")
    args = ap.parse_args(argv)

    x, mu, comps, coeffs, info = matter_background(
        args.solution, args.n_x, args.n_mu, args.rescale)
    lines = [f"{k} {v!r}" for k, v in info.items()]
    for line in lines:
        print(line)
    print("potential_coeffs " + " ".join(f"{c:.6e}" for c in coeffs))
    if args.out:
        meta = [f"family campaign-M matter background "
                f"{Path(args.solution).name}, rescale {args.rescale!r}",
                "generator grteclyn_wrapper.optimisation.handoff"] + lines
        write_matter_spinbg(args.out, info["table_eta0"], x, mu, comps,
                            meta, potential_coeffs=coeffs)
        header, body = read_spinbg(args.out)
        if body.shape != (args.n_mu, args.n_x, len(MATTER_COMPONENTS)):
            raise RuntimeError(f"{args.out}: read back {body.shape}")
        print(f"wrote {args.out} ({args.n_x} x {args.n_mu}, read back "
              f"{header['component_names']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
