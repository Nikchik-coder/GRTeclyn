"""Field equations of the rotating Ellis-Bronnikov background solver.

Unknowns f (lapse potential), omega (frame dragging) and N = nu / sin^2
theta on the strip (xi, y): xi a radial map coordinate with eta(xi) from
spectral.py, y = cos 2 theta.  The equations are Chew-Kleihaus-Kunz
(arXiv:1608.05253) eqs. (10)-(13) and (19) for the quasi-isotropic ansatz

    ds^2 = -e^f dt^2
           + e^{-f} [e^nu (d eta^2 + h d theta^2)
                     + h sin^2 theta (d phi - omega dt)^2],
    h = eta^2 + eta0^2,

divided by their angular weights so every equation is regular on the axis
(y = 1) and at the equator (y = -1):

    eq.(10) = sin theta       * E_f
    eq.(11) = h sin^3 theta e^{-2f} * E_w
    eq.(12) = sin^3 theta     * E_N        (with nu = N sin^2 theta)
    eq.(13) = sin^2 theta cos theta * (h / eta') * E_c
    eq.(19) rewritten as the D2 expression.

THE PUBLISHED EQ. (12) IS WRONG: closed-form extremal
Kerr (a = M, eta0 = 0, which fits the ansatz exactly) satisfies eqs. 10,
11, 13 and 19 to 1e-160 but leaves 1e-2 in the printed eq. 12, and the
solutions of the printed elliptic system carry a J^4-sized violation of
(13)/(19) at every resolution.  The solver therefore imposes E_f, E_w
(Newton) and obtains N and D^2 from the CONSTRAINTS (solve_N_constrained,
eqs. 13 + 19, linear in both); E_N is only a reported diagnostic of the
paper's equation.  derive_xy_equations.py --stage kerr keeps the finding
as a regression check.

``residual_forms`` below is the one place these forms exist.  It is written
against a generic radial map -- the coefficients take eta(xi), eta'(xi),
eta''(xi) at the nodes -- and uses only arithmetic plus a caller-supplied
``exp``, so the same code runs under numpy / jax.numpy (the solver) and
sympy (scripts/analysis/spinning_wormhole/derive_xy_equations.py, which
machine-checks every form against the CKK originals and emits the arctan
specialization of SpinningSolver.md section 2).

E_f, E_w are imposed nonlinearly on (f, omega); E_c and D2, linear in
(N, D^2), then fix N and D^2; E_N and the spread of D2 are the accuracy
monitors.
"""

from __future__ import annotations

__all__ = ["residual_forms", "JET_NAMES", "CollocationProblem"]

#: Every first/second derivative jet the forms read, per field: value,
#: d/dxi, d2/dxi2, d/dy, d2/dy2.
JET_NAMES = tuple(
    f"{field}{suffix}"
    for field in ("f", "w", "N")
    for suffix in ("", "_x", "_xx", "_y", "_yy")
)


def residual_forms(exp, *, eta0, y, eta, deta, d2eta, jets):
    """The five forms, elementwise, for any backend.

    ``jets`` maps JET_NAMES to values; ``eta, deta, d2eta`` are eta(xi) and
    its first two xi-derivatives; ``y`` is cos 2 theta.  Returns a dict with
    E_f, E_w (Newton), E_c, D2 (the N, D^2 solve) and E_N (diagnostic).
    """
    f, f_x, f_xx, f_y, f_yy = (jets[k] for k in ("f", "f_x", "f_xx", "f_y", "f_yy"))
    w, w_x, w_xx, w_y, w_yy = (jets[k] for k in ("w", "w_x", "w_xx", "w_y", "w_yy"))
    N, N_x, N_xx, N_y, N_yy = (jets[k] for k in ("N", "N_x", "N_xx", "N_y", "N_yy"))

    h = eta * eta + eta0 * eta0
    A2 = h / deta**2                      # radial 2nd-derivative weight
    A1 = 2 * eta / deta - h * d2eta / deta**3
    B1 = 4 * eta / deta - h * d2eta / deta**3
    W2 = (h / deta) ** 2                  # (h d/d eta)^2 weight
    e2f = exp(-2 * f)
    oy2 = 1 - y * y

    E_f = (
        A2 * f_xx + A1 * f_x + 4 * oy2 * f_yy - (6 * y + 2) * f_y
        - (1 - y) / 2 * e2f * (W2 * w_x**2 + 4 * h * oy2 * w_y**2)
    )
    E_w = (
        A2 * (w_xx - 2 * f_x * w_x) + B1 * w_x
        + 4 * oy2 * w_yy - (10 * y + 6) * w_y - 8 * oy2 * f_y * w_y
    )
    E_N = (
        A2 * N_xx + A1 * N_x + 4 * oy2 * N_yy - (10 * y + 6) * N_y - 2 * N
        - e2f * (W2 * w_x**2 - 8 * h * oy2 * w_y**2)
    )
    E_c = (
        4 * f_x * f_y + N_x
        + (2 * eta * deta / h) * (N - (1 - y) * N_y)
        - 2 * h * (1 - y) * e2f * w_x * w_y
    )
    D2 = (
        eta0 * eta0
        + W2 / 4 * f_x**2
        - h * oy2 * f_y**2
        - eta * (1 - y) * h / (4 * deta) * N_x
        - h / 2 * (oy2 * N_y - (1 + y) * N)
        - (1 - y) / 8 * e2f * (h * W2 * w_x**2 - 4 * h * h * oy2 * w_y**2)
    )
    return {"E_f": E_f, "E_w": E_w, "E_N": E_N, "E_c": E_c, "D2": D2}


class CollocationProblem:
    """Tensor Chebyshev-Lobatto collocation of E_f, E_w on (xi, y), with the
    linear constraint solve for (N, D^2) and the E_c / D2 / E_N / J(x)
    diagnostics.

    Unknowns are the corrections (df, dw) about f = (gamma/2)(1 - x) + df
    and omega = omega_inf q(xi) + dw, q = w1 / w1(-inf) from the closed-form
    O(J) profile, so both corrections carry zero boundary data and q already
    has the eta^-3 tails (SpinningSolver.md section 3).  ``prescribe`` picks
    the rotation parameter: ("omega_inf", value) holds omega(-inf), or
    ("J", value) borders the system with the flux row J(xi = 0) = value and
    makes omega_inf the extra unknown (section 4).

    The residual and its exact Jacobian (jax.jacfwd) are jit-compiled,
    float64.  Dense linear algebra; at the planned sizes (<= ~10k unknowns)
    that needs no preconditioning, and the Kronecker-sparse path is the
    documented follow-up if P4 outgrows it.

    Row layout mirrors the unknowns: for each field, radial row 0 and nx are
    the Dirichlet conditions (df = bc, dw = bc), every other row is the PDE
    at that node, including y = +-1 where the angular operator stays regular.
    ``source_f`` / ``source_w`` and the bc arrays exist for manufactured-
    solution tests; physical runs leave them zero.
    """

    def __init__(self, *, eta0: float, gamma: float, radial_map=None,
                 nx: int = 64, ny: int = 16,
                 prescribe: tuple[str, float] = ("omega_inf", 0.0)):
        import os

        # Modest thread pool BEFORE the first jax import: the container
        # advertises 128 CPUs but is quota-capped at 24, and XLA's default
        # one-thread-per-CPU pool both busts a ulimit -v sandbox
        # (pthread_create EAGAIN) and would throttle live runs.
        os.environ.setdefault(
            "XLA_FLAGS",
            "--xla_cpu_multi_thread_eigen=false "
            "intra_op_parallelism_threads=8")

        import jax

        # CPU by default: the cards are shared with live evolutions, and the
        # solver's dense LU wants the host anyway.  JAX_PLATFORMS=cuda (plus
        # CUDA_VISIBLE_DEVICES to pick a free card) opts a run onto a GPU.
        jax.config.update("jax_platforms",
                          os.environ.get("JAX_PLATFORMS", "cpu"))
        jax.config.update("jax_enable_x64", True)
        import jax.numpy as jnp

        from .backgrounds import slow_rotation_omega
        from .spectral import ArctanMap, lobatto

        if nx % 2:
            raise ValueError("nx must be even (the J flux row sits on the "
                             "xi = 0 node)")
        self.eta0, self.gamma = float(eta0), float(gamma)
        self.map = radial_map if radial_map is not None else ArctanMap(eta0=eta0)
        self.nx, self.ny = int(nx), int(ny)
        self.sx, self.Dx = lobatto(nx)
        self.sy, self.Dy = lobatto(ny)
        self.Dxx, self.Dyy = self.Dx @ self.Dx, self.Dy @ self.Dy
        mode, value = prescribe
        if mode not in ("omega_inf", "J"):
            raise ValueError(f"prescribe: {mode!r}")
        self.mode, self.value = mode, float(value)
        self.n = (nx + 1) * (ny + 1)
        self.n_unknowns = 2 * self.n + (1 if mode == "J" else 0)

        xi_i = self.sx[1:-1]
        self.eta_i = self.map.eta(xi_i)[:, None]
        self.deta_i = self.map.deta(xi_i)[:, None]
        self.d2eta_i = self.map.d2eta(xi_i)[:, None]
        self.h_i = self.eta_i**2 + eta0**2
        self.f_bg = 0.5 * gamma * (1.0 - self.sx)[:, None]

        import numpy as np

        chi = np.arctan(np.concatenate([[np.inf], self.eta_i[:, 0],
                                        [-np.inf]]) / eta0)
        w1 = slow_rotation_omega(eta0, gamma, chi)
        self.q = (w1 / w1[-1])[:, None]

        # J flux row: Gauss-Legendre in mu on the xi = 0 column, fields
        # interpolated from the y nodes (y = 2 mu^2 - 1).
        from .spectral import cheb_eval

        n_g = max(4 * (ny + 1), 48)
        mu_g, w_g = np.polynomial.legendre.leggauss(n_g)
        eye = np.eye(ny + 1)
        self.By = cheb_eval(self.sy, eye, 2.0 * mu_g**2 - 1.0)
        self.mu_w = w_g * (1.0 - mu_g**2)
        self.mid = nx // 2
        self.h_mid = float(self.map.eta(0.0) ** 2 + eta0**2)
        self.deta_mid = float(self.map.deta(0.0))

        # Manufactured-solution hooks (zero on physical problems).
        self.source_f = np.zeros((nx + 1, ny + 1))
        self.source_w = np.zeros((nx + 1, ny + 1))
        self.bc_f = np.zeros((2, ny + 1))     # df at xi = +1 / -1
        self.bc_w = np.zeros((2, ny + 1))

        self._jnp = jnp
        # the prescribed value (J or omega_inf) is a TRACED argument, so a
        # continuation driver can step it without retracing or, worse,
        # silently keeping the first compiled constant
        self._jit_residual = jax.jit(self._residual)
        self._jit_jacobian = jax.jit(jax.jacfwd(self._residual, argnums=0))

    # -- packing ------------------------------------------------------------

    def pack(self, df, dw, omega_inf=None):
        import numpy as np

        parts = [np.ravel(df), np.ravel(dw)]
        if self.mode == "J":
            if omega_inf is None:
                raise ValueError("bordered problem: omega_inf is an unknown")
            parts.append(np.atleast_1d(float(omega_inf)))
        return np.concatenate(parts)

    def unpack(self, u):
        shape = (self.nx + 1, self.ny + 1)
        df = u[: self.n].reshape(shape)
        dw = u[self.n: 2 * self.n].reshape(shape)
        omega_inf = float(u[-1]) if self.mode == "J" else self.value
        return df, dw, omega_inf

    def fields(self, u):
        """Total (f, omega) node arrays from the unknown vector."""
        df, dw, omega_inf = self.unpack(u)
        return self.f_bg + df, omega_inf * self.q + dw

    # -- residual -----------------------------------------------------------

    def _jets(self, F, W):
        jnp = self._jnp
        jets = {}
        for tag, A in (("f", F), ("w", W)):
            jets[tag] = A
            jets[f"{tag}_x"] = self.Dx @ A
            jets[f"{tag}_xx"] = self.Dxx @ A
            jets[f"{tag}_y"] = A @ self.Dy.T
            jets[f"{tag}_yy"] = A @ self.Dyy.T
        z = jnp.zeros_like(F)
        for name in ("N", "N_x", "N_xx", "N_y", "N_yy"):
            jets[name] = z
        return jets

    def _residual(self, u, value):
        jnp = self._jnp
        df = u[: self.n].reshape(self.nx + 1, self.ny + 1)
        dw = u[self.n: 2 * self.n].reshape(self.nx + 1, self.ny + 1)
        omega_inf = u[-1] if self.mode == "J" else value
        F = self.f_bg + df
        W = omega_inf * self.q + dw
        jets = self._jets(F, W)
        interior = {k: v[1:-1] for k, v in jets.items()}
        E = residual_forms(jnp.exp, eta0=self.eta0, y=self.sy[None, :],
                           eta=self.eta_i, deta=self.deta_i,
                           d2eta=self.d2eta_i, jets=interior)
        R_f = jnp.concatenate([
            (df[:1] - self.bc_f[:1]),
            E["E_f"] - self.source_f[1:-1],
            (df[-1:] - self.bc_f[1:]),
        ])
        R_w = jnp.concatenate([
            (dw[:1] - self.bc_w[:1]),
            E["E_w"] - self.source_w[1:-1],
            (dw[-1:] - self.bc_w[1:]),
        ])
        out = jnp.concatenate([R_f.ravel(), R_w.ravel()])
        if self.mode == "J":
            out = jnp.concatenate(
                [out, jnp.atleast_1d(self.j_flux(F, self.Dx @ W)) - value])
        return out

    def set_prescribed(self, value: float) -> None:
        """Step the prescribed J (or omega_inf) -- continuation."""
        self.value = float(value)

    def residual(self, u):
        return self._jit_residual(u, self.value)

    def jacobian(self, u):
        return self._jit_jacobian(u, self.value)

    def j_flux(self, F, W_x, column: int | None = None):
        """J measured on one xi column: -(1/8) int (1-mu^2) h^2 e^{-2f}
        w_eta dmu, the conserved flux of CKK eq. (11) (conventions.py)."""
        jnp = self._jnp
        i = self.mid if column is None else column
        if column is None:
            h2_over_deta = self.h_mid**2 / self.deta_mid
        else:
            h2_over_deta = float(self.h_i[i - 1, 0] ** 2 / self.deta_i[i - 1, 0])
        f_g = self.By @ F[i]
        wx_g = self.By @ W_x[i]
        return -(h2_over_deta / 8.0) * jnp.sum(
            self.mu_w * jnp.exp(-2.0 * f_g) * wx_g)

    # -- the printed eq. (12) N solve (comparison only) ----------------------

    def n_operator(self):
        """The dense eq.-(12) operator on N (Dirichlet rows at xi = +-1):
        field-independent, always invertible (angular eigenvalues
        -[2k(2k+3) + 2]), built once and cached."""
        import numpy as np

        if getattr(self, "_n_op", None) is not None:
            return self._n_op
        nx, ny = self.nx, self.ny
        A2 = self.h_i[:, 0] / self.deta_i[:, 0] ** 2
        A1 = (2 * self.eta_i[:, 0] / self.deta_i[:, 0]
              - self.h_i[:, 0] * self.d2eta_i[:, 0] / self.deta_i[:, 0] ** 3)
        rad = np.zeros((nx + 1, nx + 1))
        rad[1:-1] = A2[:, None] * self.Dxx[1:-1] + A1[:, None] * self.Dx[1:-1]
        ang = (4 * (1 - self.sy**2)[:, None] * self.Dyy
               - (10 * self.sy + 6)[:, None] * self.Dy)
        eye_y = np.eye(ny + 1)
        mask = np.ones(nx + 1)
        mask[0] = mask[-1] = 0.0
        L = (np.kron(rad, eye_y) + np.kron(np.diag(mask), ang)
             - 2.0 * np.kron(np.diag(mask), eye_y))
        L[: ny + 1] = 0.0
        L[-(ny + 1):] = 0.0
        idx = np.arange(ny + 1)
        L[idx, idx] = 1.0
        L[-(ny + 1) + idx, -(ny + 1) + idx] = 1.0
        self._n_op = L
        return L

    def solve_N(self, F, W):
        """N from the PRINTED eq. (12) at fixed (f, omega): the paper's
        scheme, kept for comparison only.  Production is
        solve_N_constrained: the printed eq. 12 fails on extremal Kerr, see
        the module docstring."""
        import numpy as np

        nx, ny = self.nx, self.ny
        L = self.n_operator()
        W_x = self.Dx @ W
        W_y = W @ self.Dy.T
        W2 = (self.h_i / self.deta_i) ** 2
        src = np.zeros((nx + 1, ny + 1))
        src[1:-1] = np.exp(-2 * np.asarray(F[1:-1])) * (
            W2 * np.asarray(W_x[1:-1]) ** 2
            - 8 * self.h_i * (1 - self.sy[None, :] ** 2)
            * np.asarray(W_y[1:-1]) ** 2)
        return np.linalg.solve(L, src.ravel()).reshape(nx + 1, ny + 1)

    # -- diagnostics (never imposed) ------------------------------------------

    def diagnostics(self, F, W, N):
        """E_c, D2 and J(x) on the interior nodes: the accuracy monitors of
        SpinningSolver.md section 8 (D2 must be one constant; J(x) too)."""
        import numpy as np

        jets = {}
        for tag, A in (("f", np.asarray(F)), ("w", np.asarray(W)),
                       ("N", np.asarray(N))):
            jets[tag] = A[1:-1]
            jets[f"{tag}_x"] = (self.Dx @ A)[1:-1]
            jets[f"{tag}_xx"] = (self.Dxx @ A)[1:-1]
            jets[f"{tag}_y"] = (A @ self.Dy.T)[1:-1]
            jets[f"{tag}_yy"] = (A @ self.Dyy.T)[1:-1]
        E = residual_forms(np.exp, eta0=self.eta0, y=self.sy[None, :],
                           eta=self.eta_i, deta=self.deta_i,
                           d2eta=self.d2eta_i, jets=jets)
        W_x = self.Dx @ np.asarray(W)
        j_of_x = np.array([self.j_flux(np.asarray(F), W_x, column=i)
                           for i in range(1, self.nx)])
        return {"E_c": E["E_c"], "D2": E["D2"], "E_N": E["E_N"],
                "j_of_x": j_of_x, "C2_i": (self.eta0**2 / self.h_i)[:, 0]}

    def solve_N_constrained(self, F, W):
        """N and D^2 jointly from the CONSTRAINT sector: the eq. (13) rows
        (E_c) and the eq. (19) rows (D^2 minus its field expression), both
        linear in (N, D^2), plus N = 0 at xi = +-1, solved as one
        equilibrated least squares.

        Why: the elliptic eq. (12) solve leaves a J^4-sized violation of (13)/(19) that no resolution
        removes -- the (f, omega) pair is exact (the quadrature nu built
        from the constraints lands on nu(-inf) = 0 to 5e-9 by itself), so
        the constraints, whose geometric content is R_{eta theta} and the
        scalar's R_{eta eta}, are made the DEFINITION of N, and the printed
        eq. (12) residual becomes a reported diagnostic instead of an
        imposed equation.  Gradient data plus one Dirichlet end determine N
        uniquely; D^2 is the one extra unknown and eq. (19) at the far end
        fixes it.

        Returns (N, D2, info) with the per-class residuals.
        """
        import numpy as np

        nx, ny = self.nx, self.ny
        n = self.n
        y = self.sy[None, :]
        F = np.asarray(F)
        W = np.asarray(W)
        F_x, F_y = self.Dx @ F, F @ self.Dy.T
        W_x, W_y = self.Dx @ W, W @ self.Dy.T
        e2f = np.exp(-2.0 * F[1:-1])
        h, eta, ep = self.h_i, self.eta_i, self.deta_i
        W2 = (h / ep) ** 2
        eye_y = np.eye(ny + 1)
        n_int = (nx - 1) * (ny + 1)
        dx_rows = np.kron(self.Dx, eye_y)[(ny + 1):-(ny + 1)]

        def ang_rows(xcoef, ang):
            full = np.concatenate([[0.0], xcoef, [0.0]])
            return np.kron(np.diag(full), ang)[(ny + 1):-(ny + 1)]

        # E_c rows: N_x + (2 eta ep / h)(N - (1 - y) N_y)
        #           = -4 f_x f_y + 2 h (1 - y) e^{-2f} w_x w_y
        ang_c = eye_y - np.diag(1.0 - self.sy) @ self.Dy
        A_c = dx_rows + ang_rows(2 * eta[:, 0] * ep[:, 0] / h[:, 0], ang_c)
        b_c = (-4.0 * F_x[1:-1] * F_y[1:-1]
               + 2.0 * h * (1 - y) * e2f * W_x[1:-1] * W_y[1:-1]).ravel()

        # E19 rows: (eta (1-y) h / (4 ep)) N_x
        #           + (h/2)((1-y^2) N_y - (1+y) N) + D2
        #           = eta0^2 + W2/4 f_x^2 - h (1-y^2) f_y^2
        #             - (1-y)/8 e^{-2f} (h W2 w_x^2 - 4 h^2 (1-y^2) w_y^2)
        v1 = (eta[:, 0] * h[:, 0] / (4 * ep[:, 0]))[:, None] * (1 - y)
        ang_19 = np.diag(1.0 - self.sy**2) @ self.Dy - np.diag(1.0 + self.sy)
        A_19 = v1.ravel()[:, None] * dx_rows + ang_rows(h[:, 0] / 2.0, ang_19)
        b_19 = (self.eta0**2 + W2 / 4 * F_x[1:-1]**2
                - h * (1 - y**2) * F_y[1:-1]**2
                - (1 - y) / 8 * e2f * (h * W2 * W_x[1:-1]**2
                                       - 4 * h * h * (1 - y**2)
                                       * W_y[1:-1]**2)).ravel()

        A_bc = np.zeros((2 * (ny + 1), n))
        for j in range(ny + 1):
            A_bc[j, j] = 1.0
            A_bc[ny + 1 + j, n - (ny + 1) + j] = 1.0
        A = np.vstack([A_c, A_19, A_bc])
        col_d2 = np.concatenate([np.zeros(n_int), np.ones(n_int),
                                 np.zeros(2 * (ny + 1))])
        A = np.hstack([A, col_d2[:, None]])
        b = np.concatenate([b_c, b_19, np.zeros(2 * (ny + 1))])
        scale = 1.0 / np.maximum(np.max(np.abs(A), axis=1), 1e-300)
        sol_vec, *_ = np.linalg.lstsq(scale[:, None] * A, scale * b,
                                      rcond=None)
        Nf = sol_vec[:n].reshape(nx + 1, ny + 1)
        d2 = float(sol_vec[-1])
        res = scale * (A @ sol_vec - b)
        info = {
            "res_Ec": float(np.max(np.abs(res[:n_int]))),
            "res_E19": float(np.max(np.abs(res[n_int:2 * n_int]))),
            "res_bc": float(np.max(np.abs(res[2 * n_int:]))),
            "D2": d2,
        }
        return Nf, d2, info
