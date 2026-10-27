"""Field equations of the campaign-M matter background solver.

The generalization of equations.py to a self-gravitating exotic scalar
WITH a potential.  A potential sources R^t_t + R^phi_phi = -2 cal V,
which the three-function Kleihaus-Kunz ansatz cannot carry (its
rho = sqrt(h) sin theta solves the rho equation identically only at
cal V = 0), so a fourth metric function joins:

    ds^2 = -e^f dt^2 + B^2 e^{-f} [e^nu (d eta^2 + h d theta^2)
                                   + h sin^2 theta (d phi - omega dt)^2],
    h = eta^2 + eta0^2,      B == 1 and the old ansatz at cal V = 0,

with the exotic scalar of conventions.py (psi = sqrt(4 pi) phi,
cal V = 8 pi V_evo; R_ab = -2 psi_a psi_b - cal V g_ab,
box psi = cal V'/2).  nu couples to every equation through e^{nu - f}
once cal V != 0, so N = nu / sin^2 theta joins the Newton unknowns --
unlike the V = 0 solver, where (f, omega) close by themselves and N is
recovered from the constraints afterwards.

The five imposed rows and the two first-order monitors are derived and
machine-checked by
scripts/analysis/spinning_wormhole/derive_matter_equations.py: the mixed
combinations (f: E^t_t + omega E^t_phi; nu: -E^t_t + 2 omega E^t_phi
- 3 E^phi_phi + E^eta_eta + E^theta_theta; w: E^t_phi; B: the rho
equation; psi: KG; c13: E^eta_theta; c19: E^eta_eta - E^theta_theta) are
proved EQUIVALENT to the Einstein + KG set -- rank 7 both ways at exact
rational points -- and the forms below are checked against them to 50
digits on generic test fields (stage `forms`).  At cal V = 0, B = 1 they
reduce symbolically to equations.residual_forms, so the matter solver
contains the published V = 0 solver exactly.

B's second derivatives legitimately appear in the monitors (rho is
dynamical, so rho_{;ab}/rho enters them; at B = 1 those terms were the
explicit eta0^2-type constants of CKK eqs. 13/19), including the one
mixed jet B_xy of E_c.

``matter_residual_forms`` follows the residual_forms contract: generic
radial map, arithmetic plus a caller-supplied ``exp`` only, so the same
code runs under numpy / jax.numpy (the solver) and sympy (the derivation
check).  The potential enters as node VALUES V = cal V(psi) and
dV = cal V'(psi), evaluated by the caller (potentials.py), so the forms
stay potential-agnostic.
"""

from __future__ import annotations

__all__ = ["matter_residual_forms", "MATTER_JET_NAMES",
           "MatterCollocationProblem"]

#: Every jet the matter forms read: value, d/dxi, d2/dxi2, d/dy, d2/dy2
#: per field, plus the one mixed jet of E_c.
MATTER_JET_NAMES = tuple(
    f"{field}{suffix}"
    for field in ("f", "w", "N", "B", "psi")
    for suffix in ("", "_x", "_xx", "_y", "_yy")
) + ("B_xy",)


def matter_residual_forms(exp, *, eta0, y, eta, deta, d2eta, jets, V, dV):
    """The seven matter forms, elementwise, for any backend.

    ``jets`` maps MATTER_JET_NAMES to values; ``eta, deta, d2eta`` are
    eta(xi) and its first two xi-derivatives; ``y`` is cos 2 theta;
    ``V, dV`` are cal V(psi), cal V'(psi) at the nodes.  Returns a dict
    with E_f, E_w, E_N, E_B, E_psi (imposed by Newton) and E_c, E19
    (first-order constraints, monitored -- E19 is the pointwise
    generalization of the V = 0 solver's D2 identity, normalized so that
    at B = 1, psi_y = 0 it equals  D2_expression - W2 psi_x^2).
    """
    f, f_x, f_xx, f_y, f_yy = (jets[k] for k in ("f", "f_x", "f_xx", "f_y", "f_yy"))
    w, w_x, w_xx, w_y, w_yy = (jets[k] for k in ("w", "w_x", "w_xx", "w_y", "w_yy"))
    N, N_x, N_xx, N_y, N_yy = (jets[k] for k in ("N", "N_x", "N_xx", "N_y", "N_yy"))
    B, B_x, B_xx, B_y, B_yy = (jets[k] for k in ("B", "B_x", "B_xx", "B_y", "B_yy"))
    psi, psi_x, psi_xx, psi_y, psi_yy = (
        jets[k] for k in ("psi", "psi_x", "psi_xx", "psi_y", "psi_yy"))
    B_xy = jets["B_xy"]

    h = eta * eta + eta0 * eta0
    A2 = h / deta**2                      # radial 2nd-derivative weight
    A1 = 2 * eta / deta - h * d2eta / deta**3
    B1 = 4 * eta / deta - h * d2eta / deta**3
    C1 = 3 * eta / deta - h * d2eta / deta**3   # the rho equation's weight
    D1 = eta / deta - h * d2eta / deta**3       # the nu row's weight
    W2 = (h / deta) ** 2                  # (h d/d eta)^2 weight
    e2f = exp(-2 * f)
    oy2 = 1 - y * y
    # e^{nu - f} with nu = N sin^2 theta = N (1 - y) / 2
    env = exp(N * (1 - y) / 2 - f)
    B2 = B * B

    E_f = (
        A2 * f_xx + A1 * f_x + 4 * oy2 * f_yy - (6 * y + 2) * f_y
        + A2 * (B_x / B) * f_x + 4 * oy2 * (B_y / B) * f_y
        - (1 - y) / 2 * B2 * e2f * (W2 * w_x**2 + 4 * h * oy2 * w_y**2)
        - 2 * V * B2 * h * env
    )
    E_w = (
        A2 * (w_xx - 2 * f_x * w_x + 3 * (B_x / B) * w_x) + B1 * w_x
        + 4 * oy2 * w_yy - (10 * y + 6) * w_y - 8 * oy2 * f_y * w_y
        + 12 * oy2 * (B_y / B) * w_y
    )
    E_B = (
        A2 * B_xx + C1 * B_x + 4 * oy2 * B_yy - (8 * y + 4) * B_y
        - 2 * V * B2 * B * h * env
    )
    E_psi = (
        A2 * psi_xx + A1 * psi_x + A2 * (B_x / B) * psi_x
        + 4 * oy2 * psi_yy - (6 * y + 2) * psi_y
        + 4 * oy2 * (B_y / B) * psi_y
        - dV / 2 * B2 * h * env
    )
    E_N = (
        (1 - y) / 2 * (A2 * N_xx + D1 * N_x)
        + (1 - y) * (2 * oy2 * N_yy - (6 * y + 4) * N_y) + 2 * y * N
        - (4 * eta / deta) * (B_x / B) + 8 * (1 + y) * (B_y / B)
        - 2 * A2 * (B_x / B) ** 2 - 8 * oy2 * (B_y / B) ** 2
        + A2 / 2 * f_x**2 + 2 * oy2 * f_y**2
        - 3 * (1 - y) / 4 * B2 * e2f * (W2 * w_x**2 + 4 * h * oy2 * w_y**2)
        - 2 * A2 * psi_x**2 - 8 * oy2 * psi_y**2
        + 2 * eta0 * eta0 / h + 2 * V * B2 * h * env
    )
    E_c = (
        4 * f_x * f_y - 16 * psi_x * psi_y
        + N_x * (1 - 2 * (1 - y) * (B_y / B))
        + (2 * eta * deta / h + 2 * B_x / B) * (N - (1 - y) * N_y)
        - 2 * h * (1 - y) * B2 * e2f * w_x * w_y
        - 8 * eta * deta / h * (B_y / B) - 16 * (B_x / B) * (B_y / B)
        + 8 * B_xy / B
    )
    E19 = (
        eta0 * eta0
        + W2 / 4 * f_x**2
        - h * oy2 * f_y**2
        - eta * (1 - y) * h / (4 * deta) * N_x
        - (1 - y) / 4 * W2 * (B_x / B) * N_x
        + h / 2 * ((1 + y) - 2 * oy2 * (B_y / B)) * (N - (1 - y) * N_y)
        - (1 - y) / 8 * B2 * e2f * (h * W2 * w_x**2
                                    - 4 * h * h * oy2 * w_y**2)
        - W2 * psi_x**2 + 4 * h * oy2 * psi_y**2
        + 4 * h * oy2 * (B_y / B) ** 2
        - 2 * h / B * (oy2 * B_yy - y * B_y)
        - W2 * (B_x / B) ** 2 - eta * h / (2 * deta) * (B_x / B)
        + h / (2 * B) * (A2 * B_xx - (h * d2eta / deta**3) * B_x)
    )
    return {"E_f": E_f, "E_w": E_w, "E_N": E_N, "E_B": E_B,
            "E_psi": E_psi, "E_c": E_c, "E19": E19}


class MatterCollocationProblem:
    """Tensor Chebyshev-Lobatto collocation of the five matter rows on
    (xi, y), bordered by the scalar boundary value.

    Unknowns are the corrections about the V = 0 backgrounds --
    f = (gamma/2)(1 - x) + df, omega = omega_inf q(xi) + dw, N = dN,
    B = 1 + dB, psi = psi_minus pr(eta) + dpsi with
    pr = (1 - (2/pi) atan(eta/eta0)) / 2 the map-free static profile --
    so every grid correction carries zero Dirichlet data at xi = +-1.

    ``prescribe`` picks the rotation parameter exactly as in
    equations.CollocationProblem: ("omega_inf", value) or ("J", value),
    the latter bordering the system with the flux row (the conserved flux
    of the twist equation now carries B^3).

    The elliptic system leaves exactly one global constant undetermined
    (the D^2 mismatch of the V = 0 solver), so the scalar boundary value
    psi(-inf) = psi_minus is an extra unknown bordered by one constraint
    row: E19 at the (xi = 0, y = -1) node, the pointwise D^2 identity at
    the throat's equator.  Passing ``psi_minus`` as a float instead holds
    it fixed and drops the row (diagnostics and manufactured tests).

    The potential is a potentials.PolynomialPotential (solver
    normalization); the default ZERO gives the pure V = 0 system, whose
    converged solutions must match equations.CollocationProblem's -- the
    step-1 gate of the campaign brief.
    """

    def __init__(self, *, eta0: float, gamma: float, potential=None,
                 radial_map=None, nx: int = 64, ny: int = 16,
                 prescribe: tuple[str, float] = ("omega_inf", 0.0),
                 psi_minus: float | None = None):
        import os

        # Modest thread pool BEFORE the first jax import (see
        # equations.CollocationProblem: the container advertises 128 CPUs
        # but is quota-capped, and XLA's default pool busts ulimit -v).
        os.environ.setdefault(
            "XLA_FLAGS",
            "--xla_cpu_multi_thread_eigen=false "
            "intra_op_parallelism_threads=8")

        import jax

        jax.config.update("jax_platforms",
                          os.environ.get("JAX_PLATFORMS", "cpu"))
        jax.config.update("jax_enable_x64", True)
        import jax.numpy as jnp
        import numpy as np

        from .backgrounds import slow_rotation_omega
        from .potentials import ZERO
        from .spectral import ArctanMap, cheb_eval, lobatto

        if nx % 2:
            raise ValueError("nx must be even (the J flux row and the E19 "
                             "row sit on the xi = 0 node)")
        self.eta0, self.gamma = float(eta0), float(gamma)
        self.pot = potential if potential is not None else ZERO
        self.map = radial_map if radial_map is not None else ArctanMap(eta0=eta0)
        self.nx, self.ny = int(nx), int(ny)
        self.sx, self.Dx = lobatto(nx)
        self.sy, self.Dy = lobatto(ny)
        self.Dxx, self.Dyy = self.Dx @ self.Dx, self.Dy @ self.Dy
        mode, value = prescribe
        if mode not in ("omega_inf", "J"):
            raise ValueError(f"prescribe: {mode!r}")
        self.mode, self.value = mode, float(value)
        self.border_psi = psi_minus is None
        self.psi_minus_fixed = 0.0 if psi_minus is None else float(psi_minus)
        self.n = (nx + 1) * (ny + 1)
        self.n_unknowns = (5 * self.n + (1 if mode == "J" else 0)
                           + (1 if self.border_psi else 0))

        xi_i = self.sx[1:-1]
        self.eta_i = self.map.eta(xi_i)[:, None]
        self.deta_i = self.map.deta(xi_i)[:, None]
        self.d2eta_i = self.map.d2eta(xi_i)[:, None]
        self.h_i = self.eta_i**2 + eta0**2
        self.f_bg = 0.5 * gamma * (1.0 - self.sx)[:, None]

        eta_all = self.map.eta(self.sx)
        with np.errstate(invalid="ignore"):
            x_arc = (2.0 / np.pi) * np.arctan(eta_all / eta0)
        x_arc[0], x_arc[-1] = 1.0, -1.0
        self.psi_prof = (0.5 * (1.0 - x_arc))[:, None] * np.ones(ny + 1)

        chi = np.arctan(np.concatenate([[np.inf], self.eta_i[:, 0],
                                        [-np.inf]]) / eta0)
        w1 = slow_rotation_omega(eta0, gamma, chi)
        self.q = (w1 / w1[-1])[:, None]

        # J flux row: Gauss-Legendre in mu on one xi column (see
        # CollocationProblem.j_flux), with the B^3 weight of the matter
        # twist equation.
        n_g = max(4 * (ny + 1), 48)
        mu_g, w_g = np.polynomial.legendre.leggauss(n_g)
        eye = np.eye(ny + 1)
        self.By = cheb_eval(self.sy, eye, 2.0 * mu_g**2 - 1.0)
        self.mu_w = w_g * (1.0 - mu_g**2)
        self.mid = nx // 2
        self.h_mid = float(self.map.eta(0.0) ** 2 + eta0**2)
        self.deta_mid = float(self.map.deta(0.0))

        self._jnp = jnp
        self._jit_residual = jax.jit(self._residual)
        self._jit_jacobian = jax.jit(jax.jacfwd(self._residual, argnums=0))

    # -- packing --------------------------------------------------------------

    def pack(self, df, dw, dN, dB, dpsi, omega_inf=None, psi_minus=None):
        import numpy as np

        parts = [np.ravel(df), np.ravel(dw), np.ravel(dN), np.ravel(dB),
                 np.ravel(dpsi)]
        if self.mode == "J":
            if omega_inf is None:
                raise ValueError("bordered problem: omega_inf is an unknown")
            parts.append(np.atleast_1d(float(omega_inf)))
        if self.border_psi:
            if psi_minus is None:
                raise ValueError("bordered problem: psi_minus is an unknown")
            parts.append(np.atleast_1d(float(psi_minus)))
        return np.concatenate(parts)

    def unpack(self, u):
        shape = (self.nx + 1, self.ny + 1)
        grids = [u[k * self.n: (k + 1) * self.n].reshape(shape)
                 for k in range(5)]
        tail = 5 * self.n
        if self.mode == "J":
            omega_inf = float(u[tail])
            tail += 1
        else:
            omega_inf = self.value
        psi_minus = (float(u[tail]) if self.border_psi
                     else self.psi_minus_fixed)
        return (*grids, omega_inf, psi_minus)

    def fields(self, u):
        """Total (F, W, N, B, psi) node arrays from the unknown vector."""
        df, dw, dN, dB, dpsi, omega_inf, psi_minus = self.unpack(u)
        return (self.f_bg + df, omega_inf * self.q + dw, dN, 1.0 + dB,
                psi_minus * self.psi_prof + dpsi)

    # -- residual -------------------------------------------------------------

    def _jets(self, fields_by_tag):
        jets = {}
        for tag, A in fields_by_tag.items():
            jets[tag] = A
            jets[f"{tag}_x"] = self.Dx @ A
            jets[f"{tag}_xx"] = self.Dxx @ A
            jets[f"{tag}_y"] = A @ self.Dy.T
            jets[f"{tag}_yy"] = A @ self.Dyy.T
        jets["B_xy"] = (self.Dx @ fields_by_tag["B"]) @ self.Dy.T
        return jets

    def _residual(self, u, value):
        jnp = self._jnp
        shape = (self.nx + 1, self.ny + 1)
        d = {tag: u[k * self.n: (k + 1) * self.n].reshape(shape)
             for k, tag in enumerate(("f", "w", "N", "B", "psi"))}
        tail = 5 * self.n
        if self.mode == "J":
            omega_inf = u[tail]
            tail += 1
        else:
            omega_inf = value
        psi_minus = u[tail] if self.border_psi else self.psi_minus_fixed
        F = self.f_bg + d["f"]
        W = omega_inf * self.q + d["w"]
        Nf = d["N"]
        B = 1.0 + d["B"]
        PSI = psi_minus * self.psi_prof + d["psi"]
        jets = self._jets({"f": F, "w": W, "N": Nf, "B": B, "psi": PSI})
        interior = {k: v[1:-1] for k, v in jets.items()}
        E = matter_residual_forms(
            jnp.exp, eta0=self.eta0, y=self.sy[None, :], eta=self.eta_i,
            deta=self.deta_i, d2eta=self.d2eta_i, jets=interior,
            V=self.pot.V(interior["psi"]), dV=self.pot.dV(interior["psi"]))
        blocks = []
        for tag, key in (("f", "E_f"), ("w", "E_w"), ("N", "E_N"),
                         ("B", "E_B"), ("psi", "E_psi")):
            blocks.append(jnp.concatenate([
                d[tag][:1], E[key], d[tag][-1:]]).ravel())
        out = jnp.concatenate(blocks)
        if self.mode == "J":
            out = jnp.concatenate(
                [out,
                 jnp.atleast_1d(self.j_flux(F, B, self.Dx @ W)) - value])
        if self.border_psi:
            out = jnp.concatenate(
                [out, jnp.atleast_1d(E["E19"][self.mid - 1, -1])])
        return out

    def set_prescribed(self, value: float) -> None:
        """Step the prescribed J (or omega_inf) -- continuation."""
        self.value = float(value)

    def residual(self, u):
        return self._jit_residual(u, self.value)

    def jacobian(self, u):
        return self._jit_jacobian(u, self.value)

    def j_flux(self, F, B, W_x, column: int | None = None):
        """J on one xi column: -(1/8) int (1-mu^2) B^3 h^2 e^{-2f} w_eta
        dmu, the conserved flux of the matter twist equation (B == 1
        reduces to the V = 0 flux of conventions.py)."""
        jnp = self._jnp
        i = self.mid if column is None else column
        if column is None:
            h2_over_deta = self.h_mid**2 / self.deta_mid
        else:
            h2_over_deta = float(self.h_i[i - 1, 0] ** 2 / self.deta_i[i - 1, 0])
        f_g = self.By @ F[i]
        b_g = self.By @ B[i]
        wx_g = self.By @ W_x[i]
        return -(h2_over_deta / 8.0) * jnp.sum(
            self.mu_w * b_g**3 * jnp.exp(-2.0 * f_g) * wx_g)

    # -- diagnostics (never imposed) ------------------------------------------

    def diagnostics(self, u):
        """The unimposed monitors on the interior nodes: E_c, E19 (its
        spread is the D2_spread analogue), the remaining Einstein row
        residuals, and J(x)."""
        import numpy as np

        F, W, Nf, B, PSI = (np.asarray(a) for a in self.fields(u))
        jets = self._jets({"f": F, "w": W, "N": Nf, "B": B, "psi": PSI})
        interior = {k: np.asarray(v)[1:-1] for k, v in jets.items()}
        E = matter_residual_forms(
            np.exp, eta0=self.eta0, y=self.sy[None, :], eta=self.eta_i,
            deta=self.deta_i, d2eta=self.d2eta_i, jets=interior,
            V=self.pot.V(interior["psi"]), dV=self.pot.dV(interior["psi"]))
        W_x = self.Dx @ W
        j_of_x = np.array([float(self.j_flux(F, B, W_x, column=i))
                           for i in range(1, self.nx)])
        return {"E_c": np.asarray(E["E_c"]), "E19": np.asarray(E["E19"]),
                "E_f": np.asarray(E["E_f"]), "E_N": np.asarray(E["E_N"]),
                "E_B": np.asarray(E["E_B"]), "E_psi": np.asarray(E["E_psi"]),
                "j_of_x": j_of_x,
                "C2_i": (self.eta0**2 / self.h_i)[:, 0]}
