"""Read-only Cartesian curvature audit using extended-precision analytic jets.

The replacement comparisons isolate a discrepancy; they do not modify the
saved solution or qualify a field for evolution. No CUDA or solve is used.
"""

import importlib.util
import json
import sys
from pathlib import Path
import numpy as np
from scipy.fft import dct

spec = importlib.util.spec_from_file_location(
    "axis", Path(__file__).with_name("audit_axis_curvature.py")
)
axis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(axis)
D = np.longdouble


class Jet:
    def __init__(self, v, d=None, h=None):
        self.v = D(v)
        self.d = np.zeros(4, dtype=D) if d is None else d
        self.h = np.zeros((4, 4), dtype=D) if h is None else h

    def __add__(self, b):
        b = asjet(b)
        return Jet(self.v + b.v, self.d + b.d, self.h + b.h)

    __radd__ = __add__

    def __neg__(self):
        return Jet(-self.v, -self.d, -self.h)

    def __sub__(self, b):
        return self + -asjet(b)

    def __rsub__(self, b):
        return asjet(b) + -self

    def __mul__(self, b):
        b = asjet(b)
        return Jet(
            self.v * b.v,
            self.d * b.v + self.v * b.d,
            self.h * b.v + self.v * b.h + np.outer(self.d, b.d) + np.outer(b.d, self.d),
        )

    __rmul__ = __mul__

    def fun(self, v, d, h):
        return Jet(v, d * self.d, d * self.h + h * np.outer(self.d, self.d))

    def __pow__(self, p):
        return self.fun(
            self.v**p, p * self.v ** (p - 1), p * (p - 1) * self.v ** (p - 2)
        )

    def __truediv__(self, b):
        return self * asjet(b) ** -1

    def __rtruediv__(self, b):
        return asjet(b) * self**-1

    def exp(self):
        return self.fun(*([np.exp(self.v)] * 3))


def asjet(x):
    return x if isinstance(x, Jet) else Jet(x)


def metric_array(g):
    return tuple(
        np.array([[getattr(t, k) for t in row] for row in g]) for k in ("v", "d", "h")
    )


def cheb(c, s, y):
    v = axis.val(c, s.v, y.v)
    vs = axis.val(c, s.v, y.v, 1)
    vy = axis.val(c, s.v, y.v, dy=1)
    h = (
        vs * s.h
        + vy * y.h
        + axis.val(c, s.v, y.v, 2) * np.outer(s.d, s.d)
        + axis.val(c, s.v, y.v, dy=2) * np.outer(y.d, y.d)
        + axis.val(c, s.v, y.v, 1, 1) * (np.outer(s.d, y.d) + np.outer(y.d, s.d))
    )
    return Jet(v, vs * s.d + vy * y.d, h)


def jets(coeff, point, length, core=False, replace=None):
    x = [Jet(v, np.eye(4, dtype=D)[i]) for i, v in enumerate(point)]
    rho2 = x[1] ** 2 + x[2] ** 2
    r2 = rho2 + x[3] ** 2
    if core:
        u = 2 * rho2 / D(".08") ** 2 - 1
        v = 2 * x[3] ** 2 / D(".08") ** 2 - 1
        f, c, w, h = [cheb(coeff[k], u, v) for k in ("f", "C", "w", "H")]
        a = c + h * rho2
    else:
        r = r2 ** D(".5")
        s = (r - length) / (r + length)
        y = 2 * x[3] ** 2 / r2 - 1
        f, w, n, b = [cheb(coeff[k], s, y) for k in ("f", "w", "N", "b")]
        c = (1 + b) ** 2 * (-f).exp()
        nu = n * rho2 / r2
        a = c * nu.exp()
        h = (a - c) / rho2
    if replace:
        key, value = replace
        fields = dict(f=f, C=c, w=w, H=h)
        fields[key] = value
        f, c, w, h = [fields[k] for k in ("f", "C", "w", "H")]
        a = c + h * rho2
    v = [-x[2], x[1], Jet(0)]
    g = [[Jet(0) for _ in range(4)] for _ in range(4)]
    g[0][0] = -f.exp() + c * w * w * rho2
    for i in range(3):
        g[0][i + 1] = g[i + 1][0] = -c * w * v[i]
        for j in range(3):
            g[i + 1][j + 1] = a * (i == j) - h * v[i] * v[j]
    return metric_array(g)


def inverse(g):
    a = np.concatenate((g.copy(), np.eye(4, dtype=D)), axis=1)
    for i in range(4):
        p = i + np.argmax(abs(a[i:, i]))
        a[[i, p]] = a[[p, i]]
        a[i] /= a[i, i]
        for j in range(4):
            if j != i:
                a[j] -= a[j, i] * a[i]
    return a[:, 4:]


def riemann(j):
    g, dg, dd = j
    iv = inverse(g)
    div = -np.einsum("ai,ijk,jb->abk", iv, dg, iv)
    term = dg.transpose(0, 2, 1) + dg - dg.transpose(2, 0, 1)
    dt = dd.transpose(0, 2, 1, 3) + dd - dd.transpose(2, 0, 1, 3)
    gam = D(".5") * np.einsum("ad,dbc->abc", iv, term)
    dgam = D(".5") * (
        np.einsum("adk,dbc->abck", div, term) + np.einsum("ad,dbck->abck", iv, dt)
    )
    return (
        dgam.transpose(0, 1, 3, 2)
        - dgam
        + np.einsum("aec,ebd->abcd", gam, gam)
        - np.einsum("aed,ebc->abcd", gam, gam)
    )


def load(path):
    with np.load(path, allow_pickle=False) as z:
        meta = json.loads(str(z["metadata"]))
        nx, ny = meta["nx"], meta["ny"]
        n = (nx + 1) * (ny + 1)
        representations = (
            "spectral_metric_cubic_dragging_smooth_origin_v1",
            "spectral_all_metric_cubic_dragging_smooth_origin_v2",
        )
        if meta.get("representation") not in representations:
            raise ValueError("full metric-coefficient archive required")
        coeff = {
            k: z["solver_u"][i * n : (i + 1) * n].reshape(nx + 1, ny + 1).astype(D)
            for i, k in ((0, "f"), (2, "N"), (3, "b"))
        }
        h = z["solver_u"][n : 2 * n].reshape(nx + 1, ny + 1).astype(D)
        if meta["representation"] == representations[0]:
            h = dct(h, type=1, axis=1) / ny
            h[:, [0, -1]] *= D(".5")
        w = np.zeros((nx + 4, ny + 1), dtype=D)
        for j in range(ny + 1):
            p = np.polynomial.chebyshev.chebmul(
                [D("2.5"), D("-3.75"), D("1.5"), D("-.25")], h[:, j]
            )
            w[: len(p), j] = p
        coeff["w"] = w.astype(float).astype(D)
    return coeff, D(meta["length"])


def audit(path):
    coeff, L = load(path)
    core = axis.core_coefficients(coeff, L, D(".08"), 12)
    rows = []
    for r in (".004", ".016", ".0392"):
        point = [D(0), D(r), D(0), D(0)]
        rp = riemann(jets(coeff, point, L))
        rc = riemann(jets(core, point, L, True))
        diff = abs(rp - rc)
        idx = np.unravel_index(np.argmax(diff), diff.shape)
        rows.append(
            dict(
                radius=float(r),
                maximum=float(diff[idx]),
                component=list(map(int, idx)),
                parent=float(rp[idx]),
                core=float(rc[idx]),
            )
        )

    point = [D(0), D(".004"), D(0), D(0)]
    x = [Jet(v, np.eye(4, dtype=D)[i]) for i, v in enumerate(point)]
    u = 2 * (x[1] ** 2 + x[2] ** 2) / D(".08") ** 2 - 1
    v = 2 * x[3] ** 2 / D(".08") ** 2 - 1
    rc = riemann(jets(core, point, L, True))
    replacements = {}
    for key in ("f", "C", "w", "H"):
        rp = riemann(jets(coeff, point, L, replace=(key, cheb(core[key], u, v))))
        replacements[key] = float(np.max(abs(rp - rc)))

    return dict(equatorial_points=rows, diagnostic_replacement_remaining=replacements)


if __name__ == "__main__":
    import hashlib

    path = Path(sys.argv[1])
    report = audit(path)
    report.update(
        source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        method="Analytic second-order Cartesian jets in numpy long double; no field changes.",
    )
    print(json.dumps(report, indent=2))
