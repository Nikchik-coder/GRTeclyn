"""Orthonormal Riemann tensor of the Kleihaus-Kunz ansatz -> ell_c.

The curved-space use of the flat Ford-Roman bound is valid for sampling
times short against the local curvature scale, which Ford-Roman take as
the smallest proper radius of curvature: here

    ell_c = (max_{abcd} |R_(a)(b)(c)(d)|)^(-1/2)

in the ZAMO (locally non-rotating) orthonormal frame

    e_0 = e^{-f/2} (d_t + omega d_phi),   e_1 = e^{(f-nu)/2} d_eta,
    e_2 = e^{(f-nu)/2} h^{-1/2} d_theta,  e_3 = e^{f/2} h^{-1/2} (sin th)^{-1} d_phi.

Built the way check_einstein.py builds its Ricci: sympy once per process
(cached), derivatives of f, nu, omega replaced by jet symbols, lambdified;
evaluation then takes exact spectral jets from a saved Solution.  The
check that convicts a wrong component: contracting the frame Riemann must
return the frame Ricci, which the field equations (never imposed here)
fix to R_(a)(b) = -2 psi_(a) psi_(b); ricci_defect() measures that.
"""

from __future__ import annotations

import numpy as np

from ..spinning_wormhole.solution import Solution

__all__ = [
    "PAIRS", "frame_riemann", "kk_jets", "ell_curvature", "kretschmann",
    "ricci_defect",
]

# Frame index pairs labelling the 21 independent components R_(AB), A <= B.
PAIRS = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]

# (eta order, theta order) of the jets the lambdas take, highest first so
# no derivative is hit by the substitution of its own function.
_ORDERS = [(2, 0), (1, 1), (0, 2), (1, 0), (0, 1), (0, 0)]

_CACHE: tuple[dict, list[str]] | None = None


def _build_lambdas() -> tuple[dict, list[str]]:
    import sympy as sp

    t, eta, th, ph = sp.symbols("t eta theta phi", real=True)
    eta0 = sp.Symbol("eta0", positive=True)
    F = sp.Function("f")(eta, th)
    NU = sp.Function("nu")(eta, th)
    W = sp.Function("omega")(eta, th)
    h = eta**2 + eta0**2
    s = sp.sin(th)
    X = [t, eta, th, ph]

    g = sp.zeros(4)
    g[0, 0] = -sp.exp(F) + sp.exp(-F) * h * s**2 * W**2
    g[0, 3] = g[3, 0] = -sp.exp(-F) * h * s**2 * W
    g[3, 3] = sp.exp(-F) * h * s**2
    g[1, 1] = sp.exp(NU - F)
    g[2, 2] = sp.exp(NU - F) * h
    # The exact inverse (the t-phi block's determinant is -h sin^2 th).
    gi = sp.zeros(4)
    gi[0, 0] = -sp.exp(-F)
    gi[0, 3] = gi[3, 0] = -sp.exp(-F) * W
    gi[3, 3] = sp.exp(F) / (h * s**2) - sp.exp(-F) * W**2
    gi[1, 1] = sp.exp(F - NU)
    gi[2, 2] = sp.exp(F - NU) / h

    gam = [[[sp.cancel(sum(gi[a, d] * (sp.diff(g[d, b], X[c])
                                       + sp.diff(g[d, c], X[b])
                                       - sp.diff(g[b, c], X[d]))
                           for d in range(4)) / 2)
             for c in range(4)] for b in range(4)] for a in range(4)]

    up_cache: dict = {}

    def riemann_up(lam, n, r, c):
        if r == c:
            return sp.Integer(0)
        if r > c:
            return -riemann_up(lam, n, c, r)
        key = (lam, n, r, c)
        if key not in up_cache:
            expr = (sp.diff(gam[lam][n][c], X[r])
                    - sp.diff(gam[lam][n][r], X[c]))
            for d in range(4):
                expr += (gam[lam][r][d] * gam[d][n][c]
                         - gam[lam][c][d] * gam[d][n][r])
            up_cache[key] = sp.cancel(expr)
        return up_cache[key]

    low_cache: dict = {}

    def riemann_low(m, n, r, c):
        key = (m, n, r, c)
        if key not in low_cache:
            expr = sum(g[m, lam] * riemann_up(lam, n, r, c)
                       for lam in range(4) if g[m, lam] != 0)
            low_cache[key] = expr
        return low_cache[key]

    # Tetrad vectors as sparse {coordinate index: component}.
    tet = {
        0: {0: sp.exp(-F / 2), 3: W * sp.exp(-F / 2)},
        1: {1: sp.exp((F - NU) / 2)},
        2: {2: sp.exp((F - NU) / 2) / sp.sqrt(h)},
        3: {3: sp.exp(F / 2) / (sp.sqrt(h) * s)},
    }

    subs, names = [], []
    for fn, tag in ((F, "f"), (NU, "nu"), (W, "w")):
        for i, j in _ORDERS:
            expr = fn
            for _ in range(i):
                expr = sp.diff(expr, eta)
            for _ in range(j):
                expr = sp.diff(expr, th)
            sym = sp.Symbol(f"{tag}_{i}{j}")
            subs.append((expr, sym))
            names.append(sym)

    out = {}
    for ia, (a, b) in enumerate(PAIRS):
        for ib in range(ia, len(PAIRS)):
            c, d = PAIRS[ib]
            expr = sp.Integer(0)
            for m, em in tet[a].items():
                for n, en in tet[b].items():
                    for r, er in tet[c].items():
                        for cc, ec in tet[d].items():
                            expr += (em * en * er * ec
                                     * riemann_low(m, n, r, cc))
            expr = sp.cancel(expr)
            for old, new in subs:
                expr = expr.subs(old, new)
            assert not expr.atoms(sp.Derivative), ((a, b), (c, d))
            out[((a, b), (c, d))] = sp.lambdify(
                [eta, th, eta0] + names, expr, modules="numpy", cse=True)
    return out, [sym.name for sym in names]


def _lambdas() -> tuple[dict, list[str]]:
    global _CACHE
    if _CACHE is None:
        _CACHE = _build_lambdas()
    return _CACHE


def kk_jets(sol: Solution, xi: np.ndarray, y: np.ndarray) -> dict:
    """(eta, theta) jets of f, nu = N sin^2 th, omega on the tensor grid
    xi x y (both strictly interior), from exact spectral jets.  Returns the
    jets plus the grid's eta, theta, h (broadcast to the grid shape)."""
    xi = np.asarray(xi, float)
    y = np.asarray(y, float)
    m = sol.radial_map
    ep = m.deta(xi)[:, None]
    epp = m.d2eta(xi)[:, None]
    th = 0.5 * np.arccos(np.clip(y, -1.0, 1.0))[None, :]
    s2t = np.sqrt(np.clip(1.0 - y * y, 0.0, None))[None, :]
    c2t = y[None, :]
    s2 = np.sin(th) ** 2
    raw = {}
    for tag in ("f", "w", "N"):
        g = {ij: sol.eval_grid(tag, xi, y, dx, dy)
             for ij, (dx, dy) in {"00": (0, 0), "x": (1, 0), "xx": (2, 0),
                                  "y": (0, 1), "yy": (0, 2),
                                  "xy": (1, 1)}.items()}
        raw[tag] = {
            "00": g["00"],
            "10": g["x"] / ep,
            "20": g["xx"] / ep**2 - g["x"] * epp / ep**3,
            "01": -2.0 * s2t * g["y"],
            "02": -4.0 * c2t * g["y"] + 4.0 * s2t**2 * g["yy"],
            "11": -2.0 * s2t * g["xy"] / ep,
        }
    n = raw["N"]
    jets = {}
    for ij in ("00", "10", "20", "01", "02", "11"):
        jets[f"f_{ij}"] = raw["f"][ij]
        jets[f"w_{ij}"] = raw["w"][ij]
    jets["nu_00"] = n["00"] * s2
    jets["nu_10"] = n["10"] * s2
    jets["nu_20"] = n["20"] * s2
    jets["nu_01"] = n["01"] * s2 + n["00"] * s2t
    jets["nu_02"] = n["02"] * s2 + 2.0 * n["01"] * s2t + 2.0 * n["00"] * c2t
    jets["nu_11"] = n["11"] * s2 + n["10"] * s2t
    eta = m.eta(xi)[:, None]
    shape = jets["f_00"].shape
    return {"jets": jets,
            "eta": np.broadcast_to(eta, shape),
            "theta": np.broadcast_to(th, shape),
            "h": np.broadcast_to(eta**2 + sol.eta0**2, shape)}


def frame_riemann(sol: Solution, xi: np.ndarray, y: np.ndarray) -> dict:
    """The 21 independent frame components on the grid, keyed by the frame
    pair-pair, plus the kk_jets() geometry entries."""
    comps, names = _lambdas()
    work = kk_jets(sol, xi, y)
    args = ([work["eta"], work["theta"], sol.eta0]
            + [work["jets"][nm] for nm in names])
    ones = np.ones_like(work["eta"])
    out = dict(work)
    out["R"] = {key: np.asarray(fn(*args)) * ones
                for key, fn in comps.items()}
    return out


def _lookup(R: dict, a: int, b: int, c: int, d: int):
    if a == b or c == d:
        return 0.0
    sign = 1.0
    if a > b:
        a, b, sign = b, a, -sign
    if c > d:
        c, d, sign = d, c, -sign
    if (a, b) > (c, d):
        (a, b), (c, d) = (c, d), (a, b)
    return sign * R[((a, b), (c, d))]


def ell_curvature(R: dict) -> np.ndarray:
    """(max |R_(abcd)|)^(-1/2): the local proper curvature scale."""
    mx = np.max(np.stack([np.abs(v) for v in R.values()]), axis=0)
    return 1.0 / np.sqrt(mx)


def kretschmann(R: dict) -> np.ndarray:
    """R_(abcd) R^(abcd); frame signs: one -1 per 0 index."""
    eta_sign = np.array([-1.0, 1.0, 1.0, 1.0])
    total = 0.0
    for ia, (a, b) in enumerate(PAIRS):
        for ib, (c, d) in enumerate(PAIRS):
            comp = _lookup(R, a, b, c, d)
            total = total + (4.0 * eta_sign[a] * eta_sign[b]
                             * eta_sign[c] * eta_sign[d] * comp * comp)
    return total


def ricci_defect(work: dict, d_charge_sq: float, mask: np.ndarray) -> float:
    """max |R_(ab) + 2 psi_(a) psi_(b)| / max |R_(ab)| on the mask.

    The solver never imposed the frame Riemann, so the contracted field
    equation holding is the check that these lambdas (and the jets fed to
    them) are right; expect the solver's own residual floor, O(1) if a
    component is wrong."""
    R = work["R"]
    eta_sign = [-1.0, 1.0, 1.0, 1.0]
    f00 = work["jets"]["f_00"]
    nu00 = work["jets"]["nu_00"]
    psi1_sq = np.exp(f00 - nu00) * d_charge_sq / work["h"] ** 2
    worst_defect, worst_ricci = 0.0, 0.0
    for a in range(4):
        for b in range(a, 4):
            ric = sum(eta_sign[c] * _lookup(R, c, a, c, b) for c in range(4))
            ric = ric * np.ones_like(work["h"])
            src = 2.0 * psi1_sq if (a, b) == (1, 1) else 0.0
            worst_defect = max(worst_defect,
                               float(np.max(np.abs((ric + src)[mask]))))
            worst_ricci = max(worst_ricci,
                              float(np.max(np.abs(ric[mask]))))
    return worst_defect / max(worst_ricci, 1e-300)
