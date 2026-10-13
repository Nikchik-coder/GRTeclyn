"""ADM mass and angular momentum of 3D data on coordinate spheres.

Step 3, check A1: the mass and spin of the 3D t = 0 data against the
background table and the solver's values (STATUS.md, Phase A).

    M(R) = (1/16 pi) oint (d_j gamma_ij - d_i gamma_jj) s^i R^2 dOmega
    J(R) = (1/8 pi)  oint (K^j_i - delta^j_i K) phi^i n_j dA

M uses the asymptotic (flat normal, flat area) formula, so at finite R it
carries O(1/R) terms from the metric's nonlinearity and the phantom
field's energy outside R (the symmetric static throat gives
eta0^2 / (2R), not 0).  Two ways around that:
  - fit M(R) = M_inf + a/R + b/R^2 + c/R^3 over several spheres (a
    check of the table's M at the ~1e-3 level on an L = 64 box);
  - take the same integral, on the same grid, of the table's own metric
    (table_gamma): the difference 3D - table is the data's error, free
    of finite-R terms, and must converge with resolution.
J uses the proper unit normal and area.  The momentum constraint with
j_phi = 0 (the phantom field carries no angular momentum) makes that flux
the same on every sphere, so J(R) is J itself at any R, with no fit.

Sphere quadrature: Gauss-Legendre in mu = cos(theta) times uniform phi.
Fields come as arrays on one uniform cell-centred grid; values and first
derivatives at the sphere nodes are taken by cubic spline interpolation
(derivatives as 4th-order differences of interpolated values, step dx).
Rotation is about z, phi^i = (-y, x, 0) relative to the centre; with the
initial data's K_ij = -(w_i m_j + w_j m_i) / (2 alpha) (beta^phi = -omega),
omega -> 2 J / r^3 gives J > 0, the solver's sign.
"""

from __future__ import annotations

import math
import re

import numpy as np

__all__ = ["UniformGrid", "adm_angular_momentum", "adm_mass", "fit_mass",
           "sphere_nodes", "table_gamma", "table_reference"]

PAIRS = ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))
SYM = {(i, j): k for k, (i, j) in enumerate(PAIRS)}
SYM.update({(j, i): k for (i, j), k in list(SYM.items())})


class UniformGrid:
    """Cell-centred arrays on one uniform grid: ``lower`` is the lower
    corner of cell (0, 0, 0), ``dx`` the spacing; ``fields`` maps a name to
    an (nx, ny, nz) array."""

    def __init__(self, lower, dx: float, fields: dict[str, np.ndarray]):
        self.lower = np.asarray(lower, dtype=float)
        self.dx = float(dx)
        self.fields = fields
        self._coef: dict[str, np.ndarray] = {}

    def interp(self, name: str, pts: np.ndarray) -> np.ndarray:
        """Cubic spline values; the spline is fitted once per field."""
        from scipy.ndimage import map_coordinates, spline_filter

        if name not in self._coef:
            self._coef[name] = spline_filter(self.fields[name], order=3,
                                             mode="nearest")
        idx = (pts - self.lower[None, :]) / self.dx - 0.5
        return map_coordinates(self._coef[name], idx.T, order=3,
                               mode="nearest", prefilter=False)

    def grad(self, name: str, pts: np.ndarray) -> np.ndarray:
        """(n, 3) first derivatives, 4th-order differences of the spline."""
        h = self.dx
        out = np.empty((len(pts), 3))
        for k in range(3):
            e = np.zeros(3)
            e[k] = h
            f = [self.interp(name, pts + s * e[None, :]) for s in (2, 1, -1, -2)]
            out[:, k] = (-f[0] + 8 * f[1] - 8 * f[2] + f[3]) / (12 * h)
        return out

    def covers(self, centre: np.ndarray, radius: float) -> bool:
        n = np.array(next(iter(self.fields.values())).shape)
        lo = self.lower + 3.5 * self.dx
        hi = self.lower + (n - 3.5) * self.dx
        return bool(np.all(centre - radius >= lo) and np.all(centre + radius <= hi))


def sphere_nodes(n_mu: int = 32, n_phi: int = 64):
    """Unit-sphere nodes (n, 3), the dmu dphi weights, and (mu, phi)."""
    mu, w_mu = np.polynomial.legendre.leggauss(n_mu)
    phi = 2 * math.pi * np.arange(n_phi) / n_phi
    MU, PHI = np.meshgrid(mu, phi, indexing="ij")
    W = np.outer(w_mu, np.full(n_phi, 2 * math.pi / n_phi))
    s = np.sqrt(1 - MU**2)
    xyz = np.stack([s * np.cos(PHI), s * np.sin(PHI), MU], axis=-1)
    return xyz.reshape(-1, 3), W.ravel(), MU.ravel(), PHI.ravel()


def _gamma_at(grid: UniformGrid, pts, names) -> np.ndarray:
    g = np.empty((len(pts), 3, 3))
    for (i, j), k in SYM.items():
        g[:, i, j] = grid.interp(names[k], pts)
    return g


def adm_mass(grid: UniformGrid, centre, radius: float,
             gamma_names=("g11", "g12", "g13", "g22", "g23", "g33"),
             n_mu: int = 32, n_phi: int = 64) -> float:
    """M(R): the asymptotic ADM surface integral on the coordinate sphere."""
    centre = np.asarray(centre, dtype=float)
    unit, w, _, _ = sphere_nodes(n_mu, n_phi)
    pts = centre[None, :] + radius * unit
    dg = {}                                   # dg[(i, j)][:, k] = d_k gamma_ij
    for (i, j), k in SYM.items():
        if (i, j) in PAIRS:
            dg[(i, j)] = grid.grad(gamma_names[k], pts)
    D = lambda i, j, k: dg[(i, j) if (i, j) in dg else (j, i)][:, k]
    integrand = np.zeros(len(pts))
    for i in range(3):
        term = sum(D(i, j, j) for j in range(3)) - sum(D(j, j, i) for j in range(3))
        integrand += term * unit[:, i]
    return float(np.sum(w * integrand) * radius**2 / (16 * math.pi))


def adm_angular_momentum(grid: UniformGrid, centre, radius: float,
                         gamma_names=("g11", "g12", "g13", "g22", "g23", "g33"),
                         k_names=("K11", "K12", "K13", "K22", "K23", "K33"),
                         n_mu: int = 32, n_phi: int = 64) -> float:
    """J(R) about z, with the proper unit normal and area element."""
    centre = np.asarray(centre, dtype=float)
    unit, w, mu, phi = sphere_nodes(n_mu, n_phi)
    pts = centre[None, :] + radius * unit
    g = _gamma_at(grid, pts, gamma_names)
    kk = _gamma_at(grid, pts, k_names)
    gi = np.linalg.inv(g)
    s = unit                                   # covector d_i r on the sphere
    n = s / np.sqrt(np.einsum("pi,pij,pj->p", s, gi, s))[:, None]
    rel = pts - centre[None, :]
    ph = np.stack([-rel[:, 1], rel[:, 0], np.zeros(len(pts))], axis=1)
    trace_k = np.einsum("pij,pij->p", gi, kk)
    flux = (np.einsum("pj,pjk,pki,pi->p", n, gi, kk, ph)
            - trace_k * np.einsum("pi,pi->p", n, ph))
    sin_t = np.sqrt(1 - mu**2)
    e_t = radius * np.stack([mu * np.cos(phi), mu * np.sin(phi), -sin_t], axis=1)
    e_p = radius * np.stack([-sin_t * np.sin(phi), sin_t * np.cos(phi),
                             np.zeros_like(mu)], axis=1)
    s_tt = np.einsum("pi,pij,pj->p", e_t, g, e_t)
    s_tp = np.einsum("pi,pij,pj->p", e_t, g, e_p)
    s_pp = np.einsum("pi,pij,pj->p", e_p, g, e_p)
    da = np.sqrt(s_tt * s_pp - s_tp**2) / sin_t        # dA per dmu dphi
    return float(np.sum(w * flux * da) / (8 * math.pi))


def fit_mass(radii, masses) -> tuple[float, float]:
    """M_inf from M(R) = M_inf + a/R + b/R^2 + c/R^3 (least squares), and
    the largest fit residual."""
    r = np.asarray(radii, dtype=float)
    a = np.stack([np.ones_like(r), 1 / r, 1 / r**2, 1 / r**3], axis=1)
    coef, *_ = np.linalg.lstsq(a, np.asarray(masses, dtype=float), rcond=None)
    return float(coef[0]), float(np.max(np.abs(a @ coef - masses)))


def table_gamma(header: dict, body: np.ndarray, X, Y, Z) -> dict[str, np.ndarray]:
    """The table's spatial metric at coordinates (X, Y, Z) relative to the
    centre, as the initial data builds it (SpinningWormholeInitialData.hpp):
    eta = r - eta0^2 / (4 r), Omega = 1 + eta0^2 / (4 r^2), f and nu_bar by
    bilinear interpolation in (x, |mu|), and

        gamma_ij = a delta_ij + c p_i p_j,   p = (-y, x, 0),
        a = e^{-f} Omega^2 e^{nu},  c = -e^{-f} Omega^2 nu_bar S(nu) / r^2,

    S(u) = expm1(u) / u, regular on the axis."""
    eta0 = float(header["eta0"])
    r = np.sqrt(X * X + Y * Y + Z * Z)
    eta = r - eta0**2 / (4 * r)
    omega2 = (1 + eta0**2 / (4 * r * r)) ** 2
    x = (2 / math.pi) * np.arctan(eta / eta0)
    mu = np.abs(Z) / r
    x_min, x_max = float(header["x_min"]), float(header["x_max"])
    n_mu, n_x = body.shape[0], body.shape[1]
    fx = np.clip((x - x_min) / (x_max - x_min) * (n_x - 1), 0, n_x - 1 - 1e-12)
    fm = np.clip(mu * (n_mu - 1), 0, n_mu - 1 - 1e-12)
    ix, im = np.floor(fx).astype(int), np.floor(fm).astype(int)
    tx, tm = fx - ix, fm - im

    def bilinear(c):
        v = body[..., c]
        return ((1 - tm) * ((1 - tx) * v[im, ix] + tx * v[im, ix + 1])
                + tm * ((1 - tx) * v[im + 1, ix] + tx * v[im + 1, ix + 1]))

    f, nu_bar = bilinear(0), bilinear(1)
    sin2 = (X * X + Y * Y) / (r * r)
    u = nu_bar * sin2
    s_u = np.where(np.abs(u) > 1e-12, np.expm1(u) / np.where(u == 0, 1, u), 1.0)
    base = np.exp(-f) * omega2
    a = base * np.exp(u)
    c = -base * nu_bar * s_u / (r * r)
    p = (-Y, X, np.zeros_like(X))
    return {f"g{i + 1}{j + 1}": (a if i == j else 0.0) + c * p[i] * p[j]
            for i, j in PAIRS}


def table_reference(header: dict) -> dict[str, float | None]:
    """The table's own M and J from its meta lines (the solver's numbers,
    rescaled to the table's eta0); static tables carry their mass in the
    family line and have J = 0."""
    meta = {}
    family = ""
    for line in header.get("meta", []):
        parts = str(line).split(None, 1)
        if len(parts) == 2:
            meta[parts[0]] = parts[1]
        if str(line).startswith("family"):
            family = str(line)

    def num(*keys):
        for k in keys:
            if k in meta:
                try:
                    return float(meta[k].split()[0])
                except ValueError:
                    pass
        return None

    m, j = num("table_M_ADM", "M_ADM"), num("table_J", "J")
    if m is None and "static" in family:
        hit = re.search(r"mass\s+([-+0-9.eE]+)", family)
        m, j = (float(hit.group(1)) if hit else None), 0.0
    return {"M": m, "J": j}
