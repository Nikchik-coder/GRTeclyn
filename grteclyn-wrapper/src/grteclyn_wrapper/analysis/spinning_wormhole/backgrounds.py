"""Stationary rotating Ellis-Bronnikov backgrounds as .spinbg tables.

The table is the ONE physics input of Examples/SpinningWormhole
(RotatingBackgroundTable.hpp): every background family -- static, slowly
rotating O(J^2), full numerical -- reaches the evolution through this file,
so the C++ never changes when the family does.

Format (SPINBG_V1)
------------------
Text header of ``key value ...`` lines, then ``END_HEADER\\n``, then the body:
float64[n_mu][n_x][6], C order.  Grids are uniform in

    x  = (2/pi) atan(eta / eta0)   on [x_min, x_max]  (both ends compactified)
    mu = cos(theta)                on [0, 1]          (equatorial symmetry)

Components, in this exact order (the loader refuses any other):

    f        alpha = e^{f/2}
    nu_bar   nu / sin^2(theta)              (0 when static; regular on axis)
    omega    frame dragging, beta^phi = -omega
    domega_deta
    domega_dtheta_over_sintheta             (odd under mu -> -mu)
    phi      phantom scalar, eta -> +infinity asymptote subtracted

Derivatives are stored so a spectral generator hands over exact ones.

The static family
-----------------
The v_e = 0 member is the massive drainhole of the merger campaign
(f = 2u, u = (m/a)(atan(eta/a) - pi/2), nu = omega = 0, a = eta0).  On the
x grid atan(eta/eta0) = pi x / 2 EXACTLY, so f and phi are linear in x and
the C++ bilinear interpolation reproduces them to machine precision -- the
static table is not an approximation.  This is the cross-check against the
merger drainhole's t = 0 constraint norms (plan Step 0).
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np

COMPONENT_NAMES = (
    "f",
    "nu_bar",
    "omega",
    "domega_deta",
    "domega_dtheta_over_sintheta",
    "phi",
)

MAGIC = "SPINBG_V1"


def write_spinbg(
    path: str | Path,
    eta0: float,
    x: np.ndarray,
    mu: np.ndarray,
    components: dict[str, np.ndarray],
    meta: list[str] | None = None,
) -> None:
    """Write a SPINBG_V1 table.

    ``components`` maps each name in COMPONENT_NAMES to an array of shape
    (n_mu, n_x).  ``x`` and ``mu`` must be uniform grids (the loader assumes
    it); this is checked here.
    """
    x = np.asarray(x, dtype=np.float64)
    mu = np.asarray(mu, dtype=np.float64)
    for grid, name in ((x, "x"), (mu, "mu")):
        if grid.ndim != 1 or grid.size < 2:
            raise ValueError(f"{name} grid must be 1D with >= 2 points")
        steps = np.diff(grid)
        if not np.allclose(steps, steps[0], rtol=0, atol=1e-13):
            raise ValueError(f"{name} grid must be uniform")
    if not (mu[0] == 0.0 and abs(mu[-1] - 1.0) < 1e-15):
        raise ValueError("mu grid must span [0, 1]")
    if eta0 <= 0.0:
        raise ValueError("eta0 must be > 0")

    missing = [n for n in COMPONENT_NAMES if n not in components]
    if missing:
        raise ValueError(f"missing components: {missing}")
    body = np.stack(
        [np.asarray(components[n], dtype=np.float64) for n in COMPONENT_NAMES],
        axis=-1,
    )
    if body.shape != (mu.size, x.size, len(COMPONENT_NAMES)):
        raise ValueError(
            f"component arrays must have shape (n_mu, n_x) = "
            f"({mu.size}, {x.size}); stacked shape is {body.shape}"
        )

    header_lines = [
        MAGIC,
        f"eta0 {float(eta0)!r}",
        f"n_x {x.size}",
        f"n_mu {mu.size}",
        f"x_min {float(x[0])!r}",
        f"x_max {float(x[-1])!r}",
        f"num_components {len(COMPONENT_NAMES)}",
        "component_names " + " ".join(COMPONENT_NAMES),
    ]
    for line in meta or []:
        header_lines.append(f"meta {line}")
    header_lines.append("END_HEADER")

    path = Path(path)
    with path.open("wb") as fh:
        fh.write(("\n".join(header_lines) + "\n").encode("ascii"))
        body.tofile(fh)


def read_spinbg(path: str | Path):
    """Read a SPINBG_V1 table back: (header dict, array[n_mu, n_x, 6])."""
    path = Path(path)
    header: dict[str, object] = {"meta": []}
    with path.open("rb") as fh:
        first = fh.readline().decode("ascii").strip()
        if first != MAGIC:
            raise ValueError(f"{path}: not a {MAGIC} file (got {first!r})")
        while True:
            line = fh.readline().decode("ascii").strip()
            if line == "END_HEADER":
                break
            if not line:
                raise ValueError(f"{path}: truncated header")
            key, _, value = line.partition(" ")
            if key == "meta":
                header["meta"].append(value)  # type: ignore[union-attr]
            elif key in ("n_x", "n_mu", "num_components"):
                header[key] = int(value)
            elif key in ("eta0", "x_min", "x_max"):
                header[key] = float(value)
            elif key == "component_names":
                header[key] = tuple(value.split())
            else:
                header[key] = value
        n_x = header["n_x"]
        n_mu = header["n_mu"]
        ncomp = header["num_components"]
        body = np.fromfile(fh, dtype=np.float64, count=n_mu * n_x * ncomp)
    if body.size != n_mu * n_x * ncomp:
        raise ValueError(f"{path}: body has {body.size} values, "
                         f"expected {n_mu * n_x * ncomp}")
    return header, body.reshape(n_mu, n_x, ncomp)


def static_background(
    eta0: float, mass: float, n_x: int, n_mu: int
) -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    """The static (v_e = 0) member: the massive drainhole, exact in x.

    u = (m/eta0)(atan(eta/eta0) - pi/2) = (m/eta0)(pi/2)(x - 1),
    f = 2u, nu = omega = 0,
    phi = sqrt(eta0^2 + m^2)/(eta0 sqrt(4 pi)) * (pi/2)(x - 1).
    """
    x = np.linspace(-1.0, 1.0, n_x)
    mu = np.linspace(0.0, 1.0, n_mu)

    half_pi_xm1 = 0.5 * math.pi * (x - 1.0)
    f_1d = 2.0 * (mass / eta0) * half_pi_xm1
    phi_1d = (
        math.sqrt(eta0 * eta0 + mass * mass)
        / (eta0 * math.sqrt(4.0 * math.pi))
    ) * half_pi_xm1

    ones = np.ones((n_mu, 1))
    zeros = np.zeros((n_mu, n_x))
    comps = {
        "f": ones * f_1d[None, :],
        "nu_bar": zeros,
        "omega": zeros.copy(),
        "domega_deta": zeros.copy(),
        "domega_dtheta_over_sintheta": zeros.copy(),
        "phi": ones * phi_1d[None, :],
    }
    return x, mu, comps


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="backgrounds",
        description="Generate / inspect .spinbg background tables "
        "(format: module docstring).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_static = sub.add_parser(
        "static", help="the v_e = 0 drainhole (exact under interpolation)"
    )
    p_static.add_argument("--eta0", type=float, default=1.0,
                          help="throat scale a (default 1.0)")
    p_static.add_argument("--mass", type=float, default=0.0,
                          help="drainhole mass m (default 0: the massless "
                          "symmetric throat, M_ADM = 0)")
    p_static.add_argument("--n-x", type=int, default=1025)
    p_static.add_argument("--n-mu", type=int, default=65)
    p_static.add_argument("--out", required=True, help="output .spinbg path")

    p_info = sub.add_parser("info", help="print a table's header and ranges")
    p_info.add_argument("file")

    args = parser.parse_args(argv)

    if args.command == "static":
        x, mu, comps = static_background(args.eta0, args.mass, args.n_x,
                                         args.n_mu)
        meta = [
            f"family static drainhole mass {args.mass!r} (v_e = 0)",
            "generator grteclyn_wrapper.analysis.spinning_wormhole."
            "backgrounds",
        ]
        write_spinbg(args.out, args.eta0, x, mu, comps, meta)
        print(f"wrote {args.out}: static eta0={args.eta0} mass={args.mass} "
              f"({args.n_x} x {args.n_mu})")
        return 0

    if args.command == "info":
        header, body = read_spinbg(args.file)
        print({k: v for k, v in header.items() if k != "meta"})
        for line in header["meta"]:
            print(f"meta: {line}")
        for c, name in enumerate(header["component_names"]):
            col = body[:, :, c]
            print(f"{name:>28s}  min {col.min(): .6e}  max {col.max(): .6e}")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
