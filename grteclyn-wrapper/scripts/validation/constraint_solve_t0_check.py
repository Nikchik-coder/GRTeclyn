#!/usr/bin/env python3
"""Read the t = 0 plotfile of a BinaryWormholeMerger run and grade its
initial data: the Hamiltonian constraint per level about the throats, the ADM
mass, and each mouth's minimal areal radius, far-side mass and far-side charge.

Why this exists
---------------
The base-grid ``L2_Ham`` the code logs does not resolve a throat (the paper
says so), so it cannot tell constraint-solved data (``constraint_solve = 1``,
``Examples/BinaryWormholeMerger/DrainholeConstraintSolve.hpp``) from the
superposition: at dx = 0.5 both sit on the same discretisation floor.  The
finest level can.  This script reads ``Ham`` from a plotfile written with
``amr.derive_plot_vars = constraints`` (which needs ``G_Newton = 1.0`` in the
params -- the derived field's ParmParse has no default) and reports, per level
and over the cells that level owns:

  * rms and max |Ham| on the throat shell, 1.2 < r_throat < 3.0;
  * rms and max |Ham| outside, r_throat >= 3.0.

Without ``Ham`` in the plotfile that table is skipped; ``--mass`` needs only
``chi``.

With ``--mass`` it also reports, from ``chi`` alone:

  * M_ADM three ways.  (1) The volume identity M = 2 sum c - (1/2 pi) int
    [V Psi - (1/8) Ahat.Ahat Psi^-7] dV, exact for a solution with
    Psi -> 1 + M/2r (V from the analytic scalar; composite box integral plus
    an analytic tail).  It gives 1.0014 on the exact throat and 1.0007 on the
    throat rebuilt from bare punctures, so it is the number to quote for
    solved data; for the superposition, which is not a solution, it does not
    apply.  (2) The monopole of Psi on spheres r = 12..27 fitted to
    A0 + A/r + B/r^2 + C/r^3, M = 2A.  (3) The same without A0, the fit this
    script used before 2026-09-27: the outer Robin condition leaves the
    solve's w a constant ~ -1e-3 inside the box, and forcing A0 = 0 reads
    that as mass (2.63 instead of 2.74 for the d = 8 head-on; 1.050 instead
    of 1.001 for the rebuilt throat).
  * each mouth's minimal areal radius: the minimum over coordinate spheres
    about its centre of sqrt(A / 4 pi), A = oint Psi^4 r^2 dOmega, on the
    finest level;
  * each mouth's far side.  Near the centre Psi = c/r + d + O(r), and the
    inversion r' = c^2/r makes the throat's own compactified infinity
    asymptotically flat with ADM mass M_far = 2 c d and scalar charge
    Q_far = 4 C c^2 / a.  d is the closed-form regular part of the solve's
    background plus w0, the monopole of w = Psi - Psi_bg at the centre
    (least squares on the finest level's cells, r < a/4, with l = 1 and
    l = 2 terms).  The isolated drainhole has M_far = -m e^{pi m/a},
    Q_far = sqrt(a^2 + m^2) e^{pi m/a} / sqrt(4 pi): -4.8105 and 3.0344 for
    a = 2, m = 1.  (M_far, Q_far) name one isolated drainhole (a', m'); m'
    is the mouth's one-body mass.

Measured on 2026-09-27 (L = 64, N = 128, level 3, d = 8 head-on from rest):
the superposition's throat-shell rms is 9.7e-3; the solve brings it to
5.1e-6, against 2.1e-6 for the exact single throat on the same grid.  Each
superposed mouth: R_min 4.466, M_far -5.363 (1.115 x isolated); solved at the
superposition's c: R_min 4.523, M_far -5.368, M_ADM 2.738 (volume).

Usage
-----
    constraint_solve_t0_check.py <plotfile> --params <run>/params.txt [--mass]
        [--solve-data <run>/data/constraint_solve.dat]
    constraint_solve_t0_check.py <plotfile> --centers="-4,0,0;4,0,0" [--box-center 32,32,32]

``--params`` reads ``center``, the throats and the solve's keys;
``--solve-data`` gives the puncture coefficients and coordinate scales the
solve used (required for puncture mode 3, which chooses them at run time;
the run writes them to ``constraint_solve.dat`` in its data directory).
``--centers`` gives the offsets from the box centre by hand (Ham and R_min
only), ``;``-separated, and needs the ``=`` because a leading minus looks
like an option to argparse.  Runs in the wrapper venv (yt, scipy).
"""

from __future__ import annotations

import argparse
import math

import numpy as np

PI = math.pi


def parse_vec(text: str) -> np.ndarray:
    return np.array([float(v) for v in text.replace(",", " ").split()], dtype=float)


def read_params(path: str) -> dict:
    """The keys this script needs from an AMReX params file (values as text)."""
    out: dict = {}
    for line in open(path, encoding="utf-8"):
        line = line.split("#", 1)[0].strip()
        if "=" not in line:
            continue
        key, val = (t.strip() for t in line.split("=", 1))
        out[key] = val.strip('"')
    return out


def read_solve_data(path: str) -> dict:
    """First data row of constraint_solve.dat, by column name."""
    names: list = []
    for line in open(path, encoding="utf-8"):
        if line.startswith("#"):
            names = line.lstrip("#").split()
            continue
        vals = line.split()
        if vals:
            return dict(zip(names, (float(v) for v in vals)))
    raise SystemExit(f"{path}: no data row")


# ------------------------------------------------------------------ background
def drainhole_u(r, a, m):
    """Static lapse exponent u = (m/a)(atan X - pi/2), X = (r - a^2/4r)/a."""
    x = (r - a * a / (4.0 * r)) / a
    return (m / a) * (np.arctan(x) - PI / 2)


class Background:
    """The analytic background the run's data were built on (id_type 1),
    as BinaryWormholeInitialData writes it: throats, puncture coefficients,
    the scalar's gradient and the Bowen-York Ahat.Ahat.  Positions are
    offsets from ``center``."""

    def __init__(self, prm: dict, solve: dict | None = None):
        self.box = parse_vec(prm.get("center", "32 32 32"))
        a_t = [float(prm.get("wormhole_throat_radius_A", 1.0))]
        a_t.append(float(prm.get("wormhole_throat_radius_B", a_t[0])))
        m_t = [float(prm.get("wormhole_drainhole_mass_A", 0.0))]
        m_t.append(float(prm.get("wormhole_drainhole_mass_B", m_t[0])))
        self.a_target, self.m_target = a_t, m_t
        off_a = parse_vec(prm.get("wormhole_centerA", "0 0 0"))
        off_b = parse_vec(prm["wormhole_centerB"]) if "wormhole_centerB" in prm else -off_a
        self.off = [off_a, off_b]
        self.present = [a_t[0] > 0.0, a_t[1] > 0.0]
        self.sign = [1.0, float(prm.get("wormhole_phi_sign_B", 1.0))]
        self.s = float(prm.get("wormhole_support_strength", 1.0))
        p_a = parse_vec(prm.get("wormhole_momentumA", "0 0 0"))
        p_b = parse_vec(prm["wormhole_momentumB"]) if "wormhole_momentumB" in prm else -p_a
        self.mom = [p_a, p_b]
        self.dist = float(np.linalg.norm(off_a - off_b))
        self.solved = int(prm.get("constraint_solve", 0)) != 0
        self.bg = int(prm.get("constraint_solve_background", 0)) if self.solved else 0
        mode = int(prm.get("constraint_solve_puncture_mode", 0)) if self.solved else 0
        self.sigma = [1.0, 1.0]
        if solve is not None:
            for x, tag in ((0, "A"), (1, "B")):
                if self.present[x] and f"sigma_{tag}" in solve:
                    self.sigma[x] = solve[f"sigma_{tag}"]
        elif mode == 3:
            raise SystemExit("puncture mode 3 chooses c and the coordinate scale at run time: "
                             "pass --solve-data <run>/data/constraint_solve.dat")
        self.a = [self.sigma[x] * a_t[x] for x in (0, 1)]
        self.m = [self.sigma[x] * m_t[x] for x in (0, 1)]
        c = [self.c_superposed(x) if self.present[x] else 0.0 for x in (0, 1)]
        if solve is not None:
            c = [solve.get(f"c_{tag}", c[x]) if self.present[x] else 0.0
                 for x, tag in ((0, "A"), (1, "B"))]
        elif mode == 1:
            c = [0.5 * self.a[x] * math.exp(0.5 * PI * self.m[x] / self.a[x])
                 if self.present[x] else 0.0 for x in (0, 1)]
        elif mode == 2:
            ca = float(prm.get("constraint_solve_puncture_coefficient_A", 0.0))
            c = [ca, float(prm.get("constraint_solve_puncture_coefficient_B", ca))]
        self.c = c
        self.shift = [(c[x] - self.c_superposed(x)) if self.present[x] else 0.0 for x in (0, 1)]

    def c_superposed(self, x: int) -> float:
        y = 1 - x
        c = 0.5 * self.a[x] * math.exp(0.5 * PI * self.m[x] / self.a[x])
        if self.present[y] and self.m[y] != 0.0:
            c *= math.exp(-0.5 * float(drainhole_u(self.dist, self.a[y], self.m[y])))
        return c

    def amplitude(self, x: int) -> float:
        a, m = self.a[x], self.m[x]
        return math.sqrt(a * a + m * m) / (a * math.sqrt(4 * PI))

    def radius(self, x: int, px, py, pz):
        return np.sqrt((px - self.off[x][0]) ** 2 + (py - self.off[x][1]) ** 2
                       + (pz - self.off[x][2]) ** 2)

    def psi(self, px, py, pz):
        """Psi_bg (the unsolved data's Psi exactly)."""
        u_sum, psi, shift, sing = 0.0, 1.0, 0.0, 0.0
        for x in (0, 1):
            if not self.present[x]:
                continue
            r = np.maximum(self.radius(x, px, py, pz), 1e-12)
            u_sum = u_sum + drainhole_u(r, self.a[x], self.m[x])
            psi = psi + np.sqrt(1.0 + self.a[x] ** 2 / (4.0 * r * r)) - 1.0
            shift = shift + self.shift[x] / r
            sing = sing + self.c[x] / r
        if self.bg == 1:
            return 1.0 + sing
        return np.exp(-0.5 * u_sum) * psi + shift

    def potential(self, px, py, pz):
        """V = pi s |grad phi|^2 of the superposed scalar."""
        g = [0.0, 0.0, 0.0]
        for x in (0, 1):
            if not self.present[x]:
                continue
            dx, dy, dz = px - self.off[x][0], py - self.off[x][1], pz - self.off[x][2]
            r2 = np.maximum(dx * dx + dy * dy + dz * dz, 1e-24)
            r = np.sqrt(r2)
            f = self.sign[x] * self.amplitude(x) * self.a[x] / ((r2 + 0.25 * self.a[x] ** 2) * r)
            g = [g[0] + f * dx, g[1] + f * dy, g[2] + f * dz]
        return PI * self.s * (g[0] ** 2 + g[1] ** 2 + g[2] ** 2)

    def aa(self, px, py, pz):
        """Ahat_ij Ahat^ij of the summed Bowen-York terms (flat indices)."""
        comp = {k: 0.0 for k in ("11", "12", "13", "22", "23", "33")}
        any_p = False
        for x in (0, 1):
            p = self.mom[x]
            if not self.present[x] or not np.any(p):
                continue
            any_p = True
            dx, dy, dz = px - self.off[x][0], py - self.off[x][1], pz - self.off[x][2]
            r2 = np.maximum(dx * dx + dy * dy + dz * dz, 1e-24)
            r = np.sqrt(r2)
            n = (dx / r, dy / r, dz / r)
            pn = n[0] * p[0] + n[1] * p[1] + n[2] * p[2]
            f = 1.5 / r2
            for i in range(3):
                for j in range(i, 3):
                    val = f * (p[i] * n[j] + p[j] * n[i] - ((1.0 if i == j else 0.0) - n[i] * n[j]) * pn)
                    comp[f"{i + 1}{j + 1}"] = comp[f"{i + 1}{j + 1}"] + val
        if not any_p:
            return 0.0
        return (comp["11"] ** 2 + comp["22"] ** 2 + comp["33"] ** 2
                + 2 * (comp["12"] ** 2 + comp["13"] ** 2 + comp["23"] ** 2))

    def regular_part(self, x: int) -> float:
        """d_bg: Psi_bg -> c_x/r + d_bg at centre x (monopole; closed form)."""
        y = 1 - x
        if self.bg == 1:
            return 1.0 + (self.c[y] / self.dist if self.present[y] else 0.0)
        e_y, delta_y, s_y = 1.0, 0.0, 0.0
        if self.present[y]:
            if self.m[y] != 0.0:
                e_y = math.exp(-0.5 * float(drainhole_u(self.dist, self.a[y], self.m[y])))
            delta_y = math.sqrt(1.0 + self.a[y] ** 2 / (4.0 * self.dist ** 2)) - 1.0
            s_y = self.shift[y] / self.dist
        a, m = self.a[x], self.m[x]
        return e_y * math.exp(0.5 * PI * m / a) * (delta_y - m / a) + s_y


# ------------------------------------------------------------------ Ham
def ham_stats(ds, centres, shell=(1.2, 3.0)):
    """Per (level, region): (rms, max) of Ham over the cells the level owns."""
    acc: dict = {}
    for grid in ds.index.grids:
        lev = grid.Level
        ham = np.asarray(grid["boxlib", "Ham"])
        own = np.asarray(grid.child_mask, dtype=bool)
        x, y, z = (np.asarray(grid["index", a]) for a in ("x", "y", "z"))
        rmin = np.full(ham.shape, np.inf)
        for c in centres:
            rmin = np.minimum(
                rmin, np.sqrt((x - c[0]) ** 2 + (y - c[1]) ** 2 + (z - c[2]) ** 2)
            )
        dv = float(np.prod(np.asarray(grid.dds)))
        regions = {
            "shell": (rmin > shell[0]) & (rmin < shell[1]),
            "outer": rmin >= shell[1],
        }
        for key, sel in regions.items():
            s = own & sel
            a = acc.setdefault((lev, key), [0.0, 0.0, 0.0])
            a[0] += float(np.sum(ham[s] ** 2) * dv)
            a[1] += float(s.sum() * dv)
            if s.any():
                a[2] = max(a[2], float(np.abs(ham[s]).max()))
    return {
        k: (math.sqrt(v[0] / v[1]) if v[1] > 0 else float("nan"), v[2])
        for k, v in acc.items()
    }


# ------------------------------------------------------------------ mass
def covering_psi(ds, lev, lo, hi):
    """Psi = chi^{-1/4} on a covering grid of level `lev` over [lo, hi]."""
    dx = float(ds.index.get_smallest_dx()) * 2 ** (ds.index.max_level - lev)
    n = np.round((np.asarray(hi) - np.asarray(lo)) / dx).astype(int)
    cg = ds.covering_grid(lev, left_edge=lo, dims=n)
    chi = np.asarray(cg["boxlib", "chi"])
    axes = [lo[i] + (np.arange(n[i]) + 0.5) * dx for i in range(3)]
    return axes, chi ** -0.25


def adm_mass_fits(ds, box_center, radii=(12, 15, 18, 21, 24, 27)):
    """M = 2A from the monopole of Psi - 1 on spheres, with and without a
    constant term: (with A0, without A0, A0)."""
    from scipy.interpolate import RegularGridInterpolator

    left = np.asarray(ds.domain_left_edge, dtype=float)
    right = np.asarray(ds.domain_right_edge, dtype=float)
    axes, psi = covering_psi(ds, 0, left, right)
    f = RegularGridInterpolator(axes, psi)
    nth, nph = 48, 96
    th = (np.arange(nth) + 0.5) * math.pi / nth
    ph = np.arange(nph) * 2 * math.pi / nph
    T, P = np.meshgrid(th, ph, indexing="ij")
    wgt = np.sin(T) / np.sin(T).sum()
    rs = np.asarray(radii, dtype=float)
    mono = []
    for r in rs:
        pts = np.stack(
            [
                box_center[0] + r * np.sin(T) * np.cos(P),
                box_center[1] + r * np.sin(T) * np.sin(P),
                box_center[2] + r * np.cos(T),
            ],
            -1,
        )
        mono.append(float(np.sum(f(pts) * wgt)) - 1.0)
    mono = np.asarray(mono)
    with_c = np.linalg.lstsq(np.stack([np.ones_like(rs), 1 / rs, 1 / rs**2, 1 / rs**3], 1),
                             mono, rcond=None)[0]
    no_c = np.linalg.lstsq(np.stack([1 / rs, 1 / rs**2, 1 / rs**3], 1), mono, rcond=None)[0]
    return 2.0 * with_c[1], 2.0 * no_c[0], with_c[0]


def gauss_legendre_sphere(nth=32, nph=64):
    x, w = np.polynomial.legendre.leggauss(nth)
    ph = (np.arange(nph) + 0.5) * 2 * PI / nph
    ct, phg = np.meshgrid(x, ph, indexing="ij")
    st = np.sqrt(1 - ct * ct)
    n = np.stack([st * np.cos(phg), st * np.sin(phg), ct], -1)
    domega = np.outer(w, np.full(nph, 2 * PI / nph))
    return n, domega


def adm_mass_volume(ds, bg: Background):
    """M = 2 sum c - (1/2 pi) int [V Psi - Ahat.Ahat / (8 Psi^7)] dV: the box
    integral over the cells each level owns, the tail outside the box with
    Psi = 1 + M/2r.  Returns (M, box integral, tail)."""
    integral = 0.0
    for g in ds.index.grids:
        own = np.asarray(g.child_mask, dtype=bool)
        x = np.asarray(g["index", "x"]) - bg.box[0]
        y = np.asarray(g["index", "y"]) - bg.box[1]
        z = np.asarray(g["index", "z"]) - bg.box[2]
        psi = np.asarray(g["boxlib", "chi"]) ** -0.25
        src = bg.potential(x, y, z) * psi - bg.aa(x, y, z) / (8.0 * psi**7)
        integral += float(np.sum(src[own])) * float(np.prod(np.asarray(g.dds)))
    two_c = 2.0 * sum(bg.c[x] for x in (0, 1) if bg.present[x])
    mass_box = two_c - integral / (2 * PI)
    left = np.asarray(ds.domain_left_edge, dtype=float)
    right = np.asarray(ds.domain_right_edge, dtype=float)
    mid = 0.5 * (left + right) - bg.box
    half = 0.5 * (right - left)
    n, domega = gauss_legendre_sphere()
    with np.errstate(divide="ignore"):
        r0 = np.min(np.where(np.abs(n) > 1e-12, half / np.abs(n), np.inf), axis=-1)
    s = np.linspace(0.0, math.log(1e4), 241)
    r = r0[..., None] * np.exp(s)                          # (nth, nph, nr)
    px = mid[0] + r * n[..., 0:1]
    py = mid[1] + r * n[..., 1:2]
    pz = mid[2] + r * n[..., 2:3]
    psi = 1.0 + 0.5 * mass_box / r
    f = (bg.potential(px, py, pz) * psi - bg.aa(px, py, pz) / (8.0 * psi**7)) * r**3
    tail = float(np.sum(np.trapezoid(f, s, axis=-1) * domega))
    return two_c - (integral + tail) / (2 * PI), integral, tail


def throat_rmin(ds, centre, r_range=(1.0, 3.2), dr=0.01, half=4.0):
    """Minimum over coordinate spheres about `centre` of sqrt(A / 4 pi),
    A = oint Psi^4 r^2 dOmega, on the finest level."""
    from scipy.interpolate import RegularGridInterpolator

    lev = ds.index.max_level
    axes, psi = covering_psi(ds, lev, list(centre - half), list(centre + half))
    f = RegularGridInterpolator(axes, psi, bounds_error=False, fill_value=None)
    nth, nph = 40, 80
    th = (np.arange(nth) + 0.5) * math.pi / nth
    ph = np.arange(nph) * 2 * math.pi / nph
    T, P = np.meshgrid(th, ph, indexing="ij")
    d_omega = np.sin(T) * (math.pi / nth) * (2 * math.pi / nph)
    best = (np.inf, 0.0)
    for r in np.arange(r_range[0], r_range[1], dr):
        pts = np.stack(
            [
                centre[0] + r * np.sin(T) * np.cos(P),
                centre[1] + r * np.sin(T) * np.sin(P),
                centre[2] + r * np.cos(T),
            ],
            -1,
        )
        area = float(np.sum(f(pts) ** 4 * d_omega)) * r * r
        areal = math.sqrt(area / (4 * math.pi))
        if areal < best[0]:
            best = (areal, float(r))
    return best


# ------------------------------------------------------------------ far side
def far_side(ds, bg: Background, x: int):
    """The mouth's far side from the finest level's cells near its centre:
    w = Psi - Psi_bg fitted to w0 + w1 r + w2 r^2 + (l = 1: n, r n) +
    (l = 2: q, r q) for r < a/4; d = d_bg + w0, M_far = 2 c d."""
    centre = bg.box + bg.off[x]
    rmax = 0.25 * bg.a[x]
    rows = []
    for g in ds.index.grids:
        le, re_ = np.asarray(g.LeftEdge), np.asarray(g.RightEdge)
        if np.any(le > centre + rmax) or np.any(re_ < centre - rmax):
            continue
        own = np.asarray(g.child_mask, dtype=bool)
        gx, gy, gz = (np.asarray(g["index", a]) for a in ("x", "y", "z"))
        dx, dy, dz = gx - centre[0], gy - centre[1], gz - centre[2]
        r = np.sqrt(dx * dx + dy * dy + dz * dz)
        sel = own & (r < rmax) & (r > 0.0)
        if not sel.any():
            continue
        w = (np.asarray(g["boxlib", "chi"])[sel] ** -0.25
             - bg.psi(gx[sel] - bg.box[0], gy[sel] - bg.box[1], gz[sel] - bg.box[2]))
        rows.append(np.stack([dx[sel], dy[sel], dz[sel], r[sel], w,
                              np.full(sel.sum(), g.Level)], 1))
    data = np.concatenate(rows)
    lev = data[:, 5].max()
    data = data[data[:, 5] == lev]
    dx, dy, dz, r, w = (data[:, i] for i in range(5))
    n = (dx / r, dy / r, dz / r)
    cols = [np.ones_like(r), r, r * r, *n, *(r * c for c in n)]
    for i, j in ((0, 0), (1, 1), (0, 1), (0, 2), (1, 2)):
        q = n[i] * n[j] - (1.0 / 3.0 if i == j else 0.0)
        cols += [q, r * q]
    coef = np.linalg.lstsq(np.stack(cols, 1), w, rcond=None)[0]
    w0 = float(coef[0])
    c = bg.c[x]
    d_bg = bg.regular_part(x)
    m_far = 2.0 * c * (d_bg + w0)
    q_far = 4.0 * bg.amplitude(x) * c * c / bg.a[x]
    a_t, m_t = bg.a_target[x], bg.m_target[x]
    m_iso = -m_t * math.exp(PI * m_t / a_t)
    q_iso = math.sqrt(a_t**2 + m_t**2) * math.exp(PI * m_t / a_t) / math.sqrt(4 * PI)
    a_eq = m_eq = float("nan")
    am2 = 4 * PI * (q_far / abs(m_far)) ** 2 - 1.0
    if m_far < 0 and am2 > 0:
        a_over_m = math.sqrt(am2)
        m_eq = abs(m_far) * math.exp(-PI / a_over_m)
        a_eq = a_over_m * m_eq
    return dict(c=c, sigma=bg.sigma[x], d_bg=d_bg, w0=w0, level=int(lev), ncells=len(r),
                M_far=m_far, M_iso=m_iso, Q_far=q_far, Q_iso=q_iso, a_eq=a_eq, m_eq=m_eq)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("plotfile")
    ap.add_argument("--params", help="the run's params.txt: center, throats, solve keys")
    ap.add_argument("--solve-data", help="the run's data/constraint_solve.dat (c, sigma per mouth)")
    ap.add_argument(
        "--centers", help='throat centres as offsets from the box centre, "-4,0,0;4,0,0"',
    )
    ap.add_argument("--box-center", default=None, help="default 32,32,32, or the params' center")
    ap.add_argument("--mass", action="store_true",
                    help="M_ADM, and each mouth's R_min, far-side mass and charge")
    args = ap.parse_args()

    box_center = np.array([32.0, 32.0, 32.0])
    offsets: list = []
    prm: dict = {}
    if args.params:
        prm = read_params(args.params)
        if "center" in prm:
            box_center = parse_vec(prm["center"])
        offsets.append(parse_vec(prm.get("wormhole_centerA", "0 0 0")))
        if float(prm.get("wormhole_throat_radius_B", "1")) > 0.0:
            offsets.append(parse_vec(prm.get("wormhole_centerB", "0 0 0"))
                           if "wormhole_centerB" in prm else -offsets[0])
    if args.centers:
        offsets = [parse_vec(c) for c in args.centers.split(";") if c.strip()]
    if args.box_center:
        box_center = parse_vec(args.box_center)
    if not offsets:
        ap.error("give --params or --centers")

    import yt

    yt.set_log_level(50)
    ds = yt.load(args.plotfile)
    centres = [box_center + off for off in offsets]

    print(f"{args.plotfile}: time {float(ds.current_time):.4f}, "
          f"levels 0-{ds.index.max_level}")
    if ("boxlib", "Ham") in ds.field_list:
        stats = ham_stats(ds, centres)
        for lev in range(ds.index.max_level + 1):
            sh = stats.get((lev, "shell"), (float("nan"), 0.0))
            ou = stats.get((lev, "outer"), (float("nan"), 0.0))
            print(f"  level {lev}: throat shell rms {sh[0]:.3e} max {sh[1]:.3e} | "
                  f"r >= 3 rms {ou[0]:.3e} max {ou[1]:.3e}")
    else:
        print("  (no Ham in the plotfile: constraint table skipped)")

    if args.mass:
        with_c, no_c, a0 = adm_mass_fits(ds, box_center)
        bg = None
        if prm:
            solve = read_solve_data(args.solve_data) if args.solve_data else None
            bg = Background(prm, solve)
        if bg is not None and bg.solved:
            m_vol, integral, tail = adm_mass_volume(ds, bg)
            print(f"  M_ADM (volume identity): {m_vol:.4f}  "
                  f"[2 sum c = {2 * sum(bg.c[x] for x in (0, 1) if bg.present[x]):.4f}, "
                  f"box integral {integral:.4f}, tail {tail:.4f}]")
        elif bg is not None:
            print("  M_ADM (volume identity): n/a -- the superposition is not a solution")
        print(f"  M_ADM (monopole fit, r = 12-27): {with_c:.4f} with a constant "
              f"(A0 = {a0:+.2e}); {no_c:.4f} without (the pre-2026-09-27 reading)")
        one_body = 0.0
        for i, c in enumerate(centres):
            areal, r = throat_rmin(ds, c)
            line = f"  mouth {'AB'[i] if i < 2 else i}: R_min {areal:.4f} at r = {r:.2f}"
            if bg is not None and i < 2 and bg.present[i]:
                fs = far_side(ds, bg, i)
                one_body += fs["m_eq"]
                line += (f"; far-side mass {fs['M_far']:.4f} ({fs['M_far'] / fs['M_iso']:.4f} x "
                         f"{fs['M_iso']:.4f}), charge {fs['Q_far']:.4f} "
                         f"({fs['Q_far'] / fs['Q_iso']:.4f} x {fs['Q_iso']:.4f}); "
                         f"c {fs['c']:.6f}, sigma {fs['sigma']:.6f}, w0 {fs['w0']:+.2e} "
                         f"[level {fs['level']}, {fs['ncells']} cells]; "
                         f"one-body drainhole a {fs['a_eq']:.4f}, m {fs['m_eq']:.4f}")
            print(line)
        if bg is not None and bg.solved and one_body > 0:
            print(f"  one-body masses {one_body:.4f}; M_ADM (volume) - their sum = "
                  f"{m_vol - one_body:+.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
