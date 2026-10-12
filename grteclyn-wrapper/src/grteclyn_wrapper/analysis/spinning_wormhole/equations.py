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

``residual_forms`` below is the one place these forms exist.  It is written
against a generic radial map -- the coefficients take eta(xi), eta'(xi),
eta''(xi) at the nodes -- and uses only arithmetic plus a caller-supplied
``exp``, so the same code runs under numpy / jax.numpy (the solver) and
sympy (scripts/analysis/spinning_wormhole/derive_xy_equations.py, which
machine-checks every form against the CKK originals and emits the arctan
specialization of SpinningSolver.md section 2).

E_f, E_w are imposed nonlinearly on (f, omega); E_N is linear in N and
solved afterwards; E_c and D2 are never imposed -- they are the accuracy
monitors (D2 must come out one constant everywhere).
"""

from __future__ import annotations

__all__ = ["residual_forms", "JET_NAMES"]

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
    E_f, E_w, E_N (imposed), E_c and D2 (monitored).
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
