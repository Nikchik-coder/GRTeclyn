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
The v_e = 0 member is the massive drainhole of the wormhole-merger runs
(f = 2u, u = (m/a)(atan(eta/a) - pi/2), nu = omega = 0, a = eta0).  On the
x grid atan(eta/eta0) = pi x / 2 EXACTLY, so f and phi are linear in x and
the C++ bilinear interpolation reproduces them to machine precision -- the
static table is not an approximation, and its t = 0 constraint norms match
the merger runs' drainhole.

The slowly rotating family, O(J^2)
----------------------------------
Solved directly in the table's (Kleihaus-Kunz) gauge, from the field
equations of Chew, Kleihaus & Kunz (arXiv:1608.05253), eqs. (10)-(13) and
(19), expanded about the static member.  With chi = atan(eta/eta0) = (pi/2) x,
(h y')' = cos^2(chi) y_chichi, and f0 = (gamma/2)(1 - x):

    omega  = J w1(eta),        h^2 e^{-2 f0} w1' = -6        (w1(+inf) = 0)
    f      = f0 + J^2 [A(eta) + B(eta) P2(cos theta)]
    nu     = J^2 n(eta) sin^2 theta          (so nu_bar = J^2 n, mu-free)
    psi    = (D/eta0)(atan(eta/eta0) - pi/2),  D^2 = eta0^2 + M0^2 + J^2 dD2

    (h A')'      = (2/3) S,   (h B')' - 6 B = -(2/3) S,   (h n')' - 2 n = S,
    S = h^2 e^{-2 f0} w1'^2 = 36 e^{2 f0} / h^2,

with A, B, n -> 0 at both infinities (f(-inf) = gamma held fixed; an extra
O(J^2) shift of f(-inf) is the homogeneous solution, ``dgamma``).  The
eta-theta constraint (13) and the constancy of D^2 (19) are not imposed:
they are checked, and hold to the collocation error.  w1 is in closed form
and equals Azad et al. (arXiv:2301.05243) eq. (2.6) to 1e-15; the
symmetric member (gamma = 0) has n = -9/(eta0^2 h), dD2 = -9/eta0^2 and
M = 3 pi J^2 / eta0^3 = 2 omega_0 J (Kleihaus-Kunz Smarr relation).
Checked against the full Einstein equations, independently of these
perturbation equations (scripts/analysis/spinning_wormhole/
check_slowspin_einstein.py: sympy Ricci tensor of the ansatz): every
R_mn + 2 d_m psi d_n psi falls as J^4, and t-phi as J^3, the first
neglected orders.

Units: G = c = 1 and R_mn = -8 pi d_m phi d_n phi (the evolution's
convention), so phi = psi / sqrt(4 pi).
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np

from .spectral import cheb_eval as _cheb_eval
from .spectral import lobatto as _cheb

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


# --- slow rotation, O(J^2) (module docstring) ------------------------------


def slow_rotation_omega(eta0: float, gamma: float, chi: np.ndarray) -> np.ndarray:
    """w1 = omega / J in closed form: 6 int_eta^inf e^{2 f0} / h^2 d eta.

    = (6 e^gamma / eta0^3) int_chi^{pi/2} e^{-k c} cos^2 c dc, k = 2 gamma/pi,
    written with expm1 so k -> 0 (the symmetric family) is not a 0/0.
    """
    chi = np.asarray(chi, dtype=np.float64)
    k = 2.0 * gamma / math.pi
    span = 0.5 * math.pi - chi
    if k == 0.0:
        lin = span
    else:
        lin = -np.expm1(-k * span) / k
    first = 0.5 * np.exp(-k * chi) * lin
    second = 0.5 * (
        k * math.exp(-k * 0.5 * math.pi)
        - np.exp(-k * chi) * (-k * np.cos(2 * chi) + 2 * np.sin(2 * chi))
    ) / (k * k + 4.0)
    return 6.0 * math.exp(gamma) / eta0 ** 3 * (first + second)


def slow_rotation_solution(eta0: float, gamma: float, n_cheb: int = 96) -> dict:
    """The O(J^2) radial functions per unit J^2, on Chebyshev nodes in x.

    Returns s (= x nodes, s[0] = +1), chi, the derivative matrix in chi,
    A, B, n, Ahom (the unit f(-inf) shift), S, f0, w1, the O(J^2) mass and
    D^2 coefficients, and two consistency residuals (constraint (13) and
    the spread of D^2 (19)), both relative.
    """
    if eta0 <= 0.0:
        raise ValueError("eta0 must be > 0")
    s, d = _cheb(n_cheb)
    chi = 0.5 * math.pi * s
    c2 = np.cos(chi) ** 2
    dchi = (2.0 / math.pi) * d
    d2 = dchi @ dchi
    f0 = 0.5 * gamma * (1.0 - s)
    src = 36.0 * np.exp(2.0 * f0) * c2 ** 2 / eta0 ** 4

    def bvp(k: float, rhs: np.ndarray) -> np.ndarray:
        # cos^2(chi) y'' - k y = rhs; the rows at the infinities are y = 0.
        lhs = c2[:, None] * d2 - k * np.eye(s.size)
        lhs[0, :] = 0.0
        lhs[0, 0] = 1.0
        lhs[-1, :] = 0.0
        lhs[-1, -1] = 1.0
        b = rhs.copy()
        b[0] = b[-1] = 0.0
        return np.linalg.solve(lhs, b)

    A = bvp(0.0, (2.0 / 3.0) * src)
    B = bvp(6.0, -(2.0 / 3.0) * src)
    n = bvp(2.0, src)
    a_hom = 0.5 * (1.0 - s)
    w1 = slow_rotation_omega(eta0, gamma, chi)

    # f -> -2 dM / eta  =>  dM = eta0 A_chi(+inf) / 2 (and -eta0/(2 pi) per
    # unit dgamma).
    A_chi, B_chi, n_chi = dchi @ A, dchi @ B, dchi @ n
    dmass = 0.5 * eta0 * A_chi[0]
    dmass_per_dgamma = -eta0 / (2.0 * math.pi)

    # Consistency on the interior nodes, a theta sample.
    inner = slice(1, -1)
    tan_c = np.tan(chi[inner])
    hfp = -gamma * eta0 / math.pi                # h f0' (constant)
    res13 = (eta0 * n_chi[inner] + 2.0 * eta0 * tan_c * n[inner]
             + 3.0 * hfp * B[inner])
    scale13 = np.max(np.abs(eta0 * n_chi[inner])) + 1e-300
    mu_s = np.linspace(0.0, 0.999, 41)
    p2 = 0.5 * (3.0 * mu_s ** 2 - 1.0)
    st2 = 1.0 - mu_s ** 2
    cc2 = c2[inner][:, None]
    sc = (np.sin(chi[inner]) * np.cos(chi[inner]))[:, None]
    dD2 = (0.5 * hfp * eta0 * (A_chi[inner][:, None]
                               + B_chi[inner][:, None] * p2[None, :])
           - 0.5 * eta0 ** 2 / cc2 * (sc * n_chi[inner][:, None] * st2[None, :]
                                      - 2.0 * mu_s[None, :] ** 2
                                      * n[inner][:, None])
           - 0.25 * eta0 ** 2 / cc2 * st2[None, :] * src[inner][:, None])
    dD2_value = float(np.median(dD2))
    dD2_spread = float(np.max(np.abs(dD2 - dD2_value))
                       / max(abs(dD2_value), 1e-300))
    # A dgamma shift enters (19) through the h^2 f0' A_hom' cross term
    # (= d(M0^2)/d gamma per unit shift; zero for the symmetric family).
    dD2_per_dgamma = 0.5 * hfp * eta0 * float((dchi @ a_hom)[n_cheb // 2])

    return {
        "s": s, "chi": chi, "dchi": dchi, "A": A, "B": B, "n": n,
        "Ahom": a_hom, "S": src, "f0": f0, "w1": w1,
        "dmass": dmass, "dmass_per_dgamma": dmass_per_dgamma,
        "dD2": dD2_value, "dD2_per_dgamma": dD2_per_dgamma,
        "res13": float(np.max(np.abs(res13)) / scale13),
        "dD2_spread": dD2_spread,
    }


def slow_rotation_background(
    eta0: float,
    gamma: float,
    J: float,
    n_x: int,
    n_mu: int,
    dgamma: float = 0.0,
    n_cheb: int = 96,
) -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray], dict]:
    """The O(J^2) slowly rotating member on the table grid, plus its numbers.

    gamma = f(-inf) of the static member (0: symmetric, massless; the
    drainhole of mass m has gamma = -2 pi m / eta0).  ``dgamma`` is an extra
    f(-inf) shift in units of J^2 / eta0^4 (0 holds f(-inf) = gamma).
    """
    sol = slow_rotation_solution(eta0, gamma, n_cheb)
    x = np.linspace(-1.0, 1.0, n_x)
    mu = np.linspace(0.0, 1.0, n_mu)
    nodes = sol["s"]
    J2 = J * J
    dg = dgamma / eta0 ** 4
    chi_x = 0.5 * math.pi * x

    f0_x = 0.5 * gamma * (1.0 - x)
    A_x = _cheb_eval(nodes, sol["A"] + dg * sol["Ahom"], x)
    B_x = _cheb_eval(nodes, sol["B"], x)
    n_x_vals = _cheb_eval(nodes, sol["n"], x)
    w1_x = slow_rotation_omega(eta0, gamma, chi_x)
    # d omega / d eta = -6 J e^{2 f0} cos^4(chi) / eta0^4, exact.
    dw_x = -6.0 * J * np.exp(2.0 * f0_x) * np.cos(chi_x) ** 4 / eta0 ** 4

    p2 = 0.5 * (3.0 * mu ** 2 - 1.0)
    f = (f0_x + J2 * A_x)[None, :] + J2 * p2[:, None] * B_x[None, :]
    ones = np.ones((n_mu, 1))

    mass0 = -gamma * eta0 / (2.0 * math.pi)
    mass = mass0 + J2 * (sol["dmass"] + dg * sol["dmass_per_dgamma"])
    D2 = eta0 ** 2 + mass0 ** 2 + J2 * (sol["dD2"] + dg * sol["dD2_per_dgamma"])
    D = math.sqrt(D2)
    phi_x = (D / eta0) * 0.5 * math.pi * (x - 1.0) / math.sqrt(4.0 * math.pi)

    comps = {
        "f": f,
        "nu_bar": ones * (J2 * n_x_vals)[None, :],
        "omega": ones * (J * w1_x)[None, :],
        "domega_deta": ones * dw_x[None, :],
        "domega_dtheta_over_sintheta": np.zeros((n_mu, n_x)),
        "phi": ones * phi_x[None, :],
    }

    info = _throat_numbers(sol, eta0, gamma, J, dg)
    info.update({
        "eta0": eta0, "gamma": gamma, "J": J, "dgamma": dgamma,
        "M_ADM": mass, "M0": mass0, "dM_over_J2": sol["dmass"],
        "D": D, "omega_minus_inf": J * float(slow_rotation_omega(
            eta0, gamma, np.array([-0.5 * math.pi]))[0]),
        "J_over_M2": J / mass ** 2 if mass != 0.0 else math.inf,
        "res13": sol["res13"], "dD2_spread": sol["dD2_spread"],
    })
    info["J_over_A"] = J / (4.0 * math.pi * info["R_A"] ** 2)
    # Rotating EB wormholes end in extremal Kerr at J/A = 1/(8 pi).
    info["J_over_A_extremal_frac"] = 8.0 * math.pi * info["J_over_A"]
    return x, mu, comps, info


def _throat_numbers(sol: dict, eta0: float, gamma: float, J: float,
                    dg: float) -> dict:
    """Throat (area minimum) location, R_A, R_eq, R_pol, Omega, v_e."""
    nodes = sol["s"]
    J2 = J * J
    a_tot = sol["A"] + dg * sol["Ahom"]

    def fields(eta: np.ndarray, mu: np.ndarray):
        x = (2.0 / math.pi) * np.arctan(eta / eta0)
        f0 = 0.5 * gamma * (1.0 - x)
        A = _cheb_eval(nodes, a_tot, x)
        B = _cheb_eval(nodes, sol["B"], x)
        n = _cheb_eval(nodes, sol["n"], x)
        p2 = 0.5 * (3.0 * mu ** 2 - 1.0)
        f = (f0 + J2 * A)[:, None] + J2 * B[:, None] * p2[None, :]
        nu = J2 * n[:, None] * (1.0 - mu ** 2)[None, :]
        return f, nu, eta ** 2 + eta0 ** 2

    mu_g, w_g = np.polynomial.legendre.leggauss(48)

    def area(eta: np.ndarray) -> np.ndarray:
        f, nu, h = fields(eta, mu_g)
        return 2.0 * math.pi * h * (np.exp(-f + 0.5 * nu) @ w_g)

    # The static throat sits at eta = M0; dense bracket, then golden section.
    centre = -gamma * eta0 / (2.0 * math.pi)
    grid = centre + eta0 * np.linspace(-1.0, 1.0, 401)
    i = int(np.argmin(area(grid)))
    lo, hi = grid[max(i - 1, 0)], grid[min(i + 1, grid.size - 1)]
    g = 0.5 * (math.sqrt(5.0) - 1.0)
    for _ in range(80):
        a1, a2 = hi - g * (hi - lo), lo + g * (hi - lo)
        if area(np.array([a1]))[0] < area(np.array([a2]))[0]:
            hi = a2
        else:
            lo = a1
    eta_t = 0.5 * (lo + hi)
    area_t = float(area(np.array([eta_t]))[0])

    f_eq, _, h_t = fields(np.array([eta_t]), np.array([0.0]))
    r_eq = math.exp(-0.5 * float(f_eq[0, 0])) * math.sqrt(float(h_t[0]))
    # R_pol (KK eq. 6): the meridian's half length / pi, quadrature in theta.
    th_g, wth = np.polynomial.legendre.leggauss(64)
    th = 0.5 * math.pi * (th_g + 1.0)
    f_m, nu_m, _ = fields(np.array([eta_t]), np.cos(th))
    r_pol = math.sqrt(float(h_t[0])) / math.pi * 0.5 * math.pi * float(
        np.exp(0.5 * (nu_m[0] - f_m[0])) @ wth)
    omega_t = J * float(slow_rotation_omega(
        eta0, gamma, np.array([math.atan(eta_t / eta0)]))[0])
    return {
        "eta_throat": eta_t, "R_A": math.sqrt(area_t / (4.0 * math.pi)),
        "R_eq": r_eq, "R_pol": r_pol, "Omega_throat": omega_t,
        "v_e": r_eq * omega_t,
    }


def full_background(
    solution_path: str | Path,
    n_x: int,
    n_mu: int,
    rescale: float = 1.0,
) -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray], dict]:
    """A fast-spin Solution (solution.py) on the table grid, plus numbers.

    The six columns follow SpinningSolver.md section 2; ``rescale`` = lambda
    applies eta -> lambda eta at write time (f, N, phi, x unchanged;
    omega -> omega/lambda, d_eta omega -> /lambda^2, (d_theta omega)/sin
    -> /lambda; header eta0 -> lambda eta0; D -> lambda D, M -> lambda M).
    """
    from .observables import identity_gates, observables as sol_observables
    from .solution import Solution

    sol = Solution.load(solution_path)
    if not sol.gates:
        sol.gates = identity_gates(sol)
    if not sol.observables:
        sol.observables = sol_observables(sol)

    x = np.linspace(-1.0, 1.0, n_x)
    mu = np.linspace(0.0, 1.0, n_mu)
    y = 2.0 * mu * mu - 1.0
    m = sol.radial_map
    eta_tab = sol.eta0 * np.tan(0.5 * math.pi * np.clip(x, -1 + 1e-16, 1 - 1e-16))
    xi = m.xi_of_eta(eta_tab)
    xi[0], xi[-1] = -1.0, 1.0

    f = sol.eval_grid("f", xi, y).T              # -> (n_mu, n_x)
    nf = sol.eval_grid("N", xi, y).T
    w = sol.eval_grid("w", xi, y).T
    w_x = sol.eval_grid("w", xi, y, dx_order=1).T
    w_y = sol.eval_grid("w", xi, y, dy_order=1).T
    deta = m.deta(xi)[None, :]
    dw_deta = w_x / deta
    dw_dth_over_s = -4.0 * mu[:, None] * w_y

    d = sol.observables["D"]
    phi = np.ones((n_mu, 1)) * (
        (d / sol.eta0) * 0.5 * math.pi * (x - 1.0) / math.sqrt(4.0 * math.pi)
    )[None, :]

    lam = float(rescale)
    comps = {
        "f": f,
        "nu_bar": nf,
        "omega": w / lam,
        "domega_deta": dw_deta / lam**2,
        "domega_dtheta_over_sintheta": dw_dth_over_s / lam,
        "phi": phi,
    }
    info = dict(sol.observables)
    info["table_eta0"] = lam * sol.eta0
    info["table_D"] = lam * d
    info["table_M_ADM"] = lam * info["M_ADM"]
    info["table_J"] = lam * lam * info["J"]
    info["gates"] = sol.gates
    info["midpoint_err_f"] = _table_midpoint_error(sol, xi, x, y, f)
    return x, mu, comps, info


def _table_midpoint_error(sol, xi, x, y, f_tab) -> float:
    """Bilinear-vs-spectral error of f at the table cell centres (the
    fidelity gate: <= 1e-7 in f, SpinningSolver.md P5)."""
    xm = 0.5 * (x[:-1] + x[1:])
    ym = 0.5 * (y[:-1] + y[1:])
    m = sol.radial_map
    eta_m = sol.eta0 * np.tan(0.5 * math.pi * xm)
    xi_m = m.xi_of_eta(eta_m)
    exact = sol.eval_grid("f", xi_m, ym)                       # (nx-1, nmu-1)
    bilin = 0.25 * (f_tab[:-1, :-1] + f_tab[:-1, 1:]
                    + f_tab[1:, :-1] + f_tab[1:, 1:]).T
    return float(np.max(np.abs(exact - bilin)))


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

    p_slow = sub.add_parser(
        "slowspin", help="the O(J^2) slowly rotating member (module "
        "docstring); prints its global and throat numbers"
    )
    p_slow.add_argument("--eta0", type=float, default=1.0,
                        help="throat scale a (default 1.0)")
    p_slow.add_argument("--mass", type=float, default=0.0,
                        help="static drainhole mass m it rotates "
                        "(gamma = -2 pi m / eta0; default 0: symmetric)")
    p_slow.add_argument("--J", type=float, required=True,
                        help="angular momentum (omega -> 2 J / eta^3)")
    p_slow.add_argument("--dgamma", type=float, default=0.0,
                        help="extra f(-inf) shift in units of J^2/eta0^4 "
                        "(default 0: f(-inf) held at its static value)")
    p_slow.add_argument("--n-x", type=int, default=1025)
    p_slow.add_argument("--n-mu", type=int, default=65)
    p_slow.add_argument("--n-cheb", type=int, default=96)
    p_slow.add_argument("--out", help="output .spinbg path (omit: numbers "
                        "only)")

    p_full = sub.add_parser(
        "full", help="write a .spinbg from a saved fast-spin Solution "
        "(solution.py .npz; solver: SpinningSolver.md)"
    )
    p_full.add_argument("solution", help="Solution .npz path")
    p_full.add_argument("--n-x", type=int, default=1025)
    p_full.add_argument("--n-mu", type=int, default=65)
    p_full.add_argument("--rescale", type=float, default=1.0,
                        help="lambda of eta -> lambda eta at write time "
                        "(default 1: the solution's own eta0)")
    p_full.add_argument("--out", help="output .spinbg path (omit: numbers "
                        "only)")

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

    if args.command == "slowspin":
        gamma = -2.0 * math.pi * args.mass / args.eta0
        x, mu, comps, info = slow_rotation_background(
            args.eta0, gamma, args.J, args.n_x, args.n_mu, args.dgamma,
            args.n_cheb)
        lines = [f"{k} {float(v)!r}" for k, v in info.items()]
        for line in lines:
            print(line)
        if args.out:
            meta = [
                f"family slow rotation O(J^2) on the drainhole mass "
                f"{args.mass!r}, J {args.J!r}, dgamma {args.dgamma!r}",
                "generator grteclyn_wrapper.analysis.spinning_wormhole."
                "backgrounds slowspin",
            ] + lines
            write_spinbg(args.out, args.eta0, x, mu, comps, meta)
            print(f"wrote {args.out} ({args.n_x} x {args.n_mu})")
        return 0

    if args.command == "full":
        x, mu, comps, info = full_background(args.solution, args.n_x,
                                             args.n_mu, args.rescale)
        gates = info.pop("gates")
        lines = [f"{k} {v!r}" for k, v in info.items()
                 if isinstance(v, (int, float))]
        lines += [f"gate_{k} {v!r}" for k, v in gates.items()
                  if isinstance(v, (int, float))]
        for line in lines:
            print(line)
        if args.out:
            meta = [
                f"family full fast-spin solution {Path(args.solution).name}, "
                f"rescale {args.rescale!r}",
                "generator grteclyn_wrapper.analysis.spinning_wormhole."
                "backgrounds full",
            ] + lines
            write_spinbg(args.out, info["table_eta0"], x, mu, comps, meta)
            print(f"wrote {args.out} ({args.n_x} x {args.n_mu})")
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
