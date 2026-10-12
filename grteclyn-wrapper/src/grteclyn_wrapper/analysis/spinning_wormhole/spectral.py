"""Chebyshev-Lobatto collocation and radial maps for the fast-spin solver.

The solver (research/spinningwormhole/SpinningSolver.md) discretizes the
two-universe wormhole strip xi in [-1, 1] (radial, both infinities
compactified) x y in [-1, 1] (angular, y = cos 2 theta) on tensor Lobatto
nodes.  This module holds the 1-D spectral pieces -- nodes, differentiation
matrices, the coefficient transform, the tail-ratio resolution monitor,
barycentric evaluation -- and the radial maps eta(xi).  Each map exposes
(eta, eta', eta'') at the nodes, so the field equations (equations.py)
never hard-code a map: switching to a stretched grid near extremality is a
configuration change, not a rewrite.

``lobatto`` and ``cheb_eval`` are the former ``backgrounds._cheb`` and
``backgrounds._cheb_eval``, moved here so the O(J^2) generator and the full
solver share one implementation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


def lobatto(n: int) -> tuple[np.ndarray, np.ndarray]:
    """Chebyshev-Lobatto nodes s_j = cos(pi j / n) and the derivative matrix.

    Nodes run from +1 down to -1 (s[0] = +1).
    """
    j = np.arange(n + 1)
    s = np.cos(math.pi * j / n)
    c = np.where((j == 0) | (j == n), 2.0, 1.0) * (-1.0) ** j
    ds = s[:, None] - s[None, :]
    d = np.outer(c, 1.0 / c) / (ds + np.eye(n + 1))
    d -= np.diag(d.sum(axis=1))
    return s, d


def cheb_eval(nodes: np.ndarray, vals: np.ndarray, s) -> np.ndarray:
    """Barycentric interpolation from Chebyshev-Lobatto nodes (spectral).

    ``vals`` may be (n+1,) or (n+1, m); evaluation is along the first axis.
    """
    s = np.atleast_1d(np.asarray(s, dtype=np.float64))
    w = (-1.0) ** np.arange(nodes.size)
    w[0] *= 0.5
    w[-1] *= 0.5
    diff = s[:, None] - nodes[None, :]
    hit = diff == 0.0
    diff[hit] = 1.0
    tmp = w / diff
    out = (tmp @ vals) / tmp.sum(axis=1).reshape((-1,) + (1,) * (vals.ndim - 1))
    rows, cols = np.nonzero(hit)
    out[rows] = vals[cols]
    return out


def cheb_coeffs(vals: np.ndarray, axis: int = 0) -> np.ndarray:
    """Chebyshev coefficients a_k (sum a_k T_k) from Lobatto node values.

    ``vals`` holds values at s_j = cos(pi j / n) along ``axis``.  Direct
    cosine-matrix transform: exact, and cheap at the solver's sizes.
    """
    vals = np.asarray(vals, dtype=np.float64)
    n = vals.shape[axis] - 1
    j = np.arange(n + 1)
    cosm = np.cos(math.pi * np.outer(j, j) / n)
    wj = np.ones(n + 1)
    wj[0] = wj[-1] = 0.5
    ck = np.where((j == 0) | (j == n), 2.0, 1.0)
    moved = np.moveaxis(vals, axis, 0)
    a = (2.0 / n) * np.einsum("kj,j,j...->k...", cosm, wj, moved) / ck.reshape(
        (-1,) + (1,) * (moved.ndim - 1)
    )
    return np.moveaxis(a, 0, axis)


def tail_ratio(vals: np.ndarray, axis: int = 0, n_tail: int = 3) -> float:
    """Resolution monitor: max of the last ``n_tail`` Chebyshev coefficients
    over the largest, along ``axis`` (SpinningSolver.md gate: <= 1e-11)."""
    a = np.abs(cheb_coeffs(vals, axis=axis))
    a = np.moveaxis(a, axis, 0)
    top = float(a.max())
    if top == 0.0:
        return 0.0
    return float(a[-n_tail:].max()) / top


@dataclass(frozen=True)
class ArctanMap:
    """eta = eta0 tan(pi xi / 2): the table grid's map, uniform resolution in
    chi = atan(eta/eta0).  eta'/h = pi/(2 eta0) exactly, so the operator
    coefficients of equations.py reduce to the closed (x, y) forms of
    SpinningSolver.md section 2 (checked by derive_xy_equations.py)."""

    eta0: float
    name: str = "arctan"

    def eta(self, xi: np.ndarray) -> np.ndarray:
        return self.eta0 * np.tan(0.5 * math.pi * np.asarray(xi, float))

    def deta(self, xi: np.ndarray) -> np.ndarray:
        return 0.5 * math.pi * self.eta0 / np.cos(0.5 * math.pi * np.asarray(xi, float)) ** 2

    def d2eta(self, xi: np.ndarray) -> np.ndarray:
        u = 0.5 * math.pi * np.asarray(xi, float)
        return 0.5 * math.pi**2 * self.eta0 * np.tan(u) / np.cos(u) ** 2

    def xi_of_eta(self, eta: np.ndarray) -> np.ndarray:
        return (2.0 / math.pi) * np.arctan(np.asarray(eta, float) / self.eta0)

    def describe(self) -> str:
        return f"arctan eta0={self.eta0!r}"


@dataclass(frozen=True)
class LogStretchMap:
    """eta = eta0 sinh(L atanh xi), L a positive even integer.

    Spreads nodes evenly in log|eta| out to eta ~ eta0 e^{2L}/2 while both
    ends stay spectrally clean: for even L, 1/eta is analytic in (1 - xi)
    at xi = 1 (odd L gives half-integer powers; both checked by
    derive_xy_equations.py --check-maps).  L = 2 is xi = eta/(eta0 +
    sqrt(h)), the same end character as the arctan map.
    """

    eta0: float
    L: int = 4
    name: str = "logstretch"

    def __post_init__(self):
        if self.L < 2 or self.L % 2:
            raise ValueError("L must be a positive even integer "
                             "(odd L loses end analyticity)")

    def eta(self, xi: np.ndarray) -> np.ndarray:
        return self.eta0 * np.sinh(self.L * np.arctanh(np.asarray(xi, float)))

    def deta(self, xi: np.ndarray) -> np.ndarray:
        xi = np.asarray(xi, float)
        return self.eta0 * self.L * np.cosh(self.L * np.arctanh(xi)) / (1.0 - xi * xi)

    def d2eta(self, xi: np.ndarray) -> np.ndarray:
        xi = np.asarray(xi, float)
        u = self.L * np.arctanh(xi)
        return (self.eta0 * self.L * (self.L * np.sinh(u) + 2.0 * xi * np.cosh(u))
                / (1.0 - xi * xi) ** 2)

    def xi_of_eta(self, eta: np.ndarray) -> np.ndarray:
        return np.tanh(np.arcsinh(np.asarray(eta, float) / self.eta0) / self.L)

    def describe(self) -> str:
        return f"logstretch eta0={self.eta0!r} L={self.L}"


MAPS = {"arctan": ArctanMap, "logstretch": LogStretchMap}
