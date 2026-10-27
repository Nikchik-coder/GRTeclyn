#!/usr/bin/env python
"""Derive and machine-check the campaign-M matter forms (p-form ansatz).

A scalar potential sources R^t_t + R^phi_phi = -2 cal V, which the
three-function Kleihaus-Kunz ansatz cannot carry: its rho = sqrt(h) sin
theta solves the rho equation identically only at cal V = 0.  The
generalized quasi-isotropic ansatz is

    ds^2 = -e^f dt^2 + p e^{-f} [e^nu (d eta^2 + h d theta^2)
                                 + h sin^2 theta (d phi - omega dt)^2],
    h = eta^2 + eta0^2,   p = B^2,   B == 1 and the old ansatz at V = 0,

with the exotic scalar of conventions.py (psi = sqrt(4 pi) phi,
cal V = 8 pi V_evo):

    R_ab = -2 psi_a psi_b - cal V g_ab,     box psi = cal V'(psi) / 2.

Ground truth is E_ab = R_ab + 2 psi_a psi_b + cal V g_ab and the KG
residual, built symbolically from the metric; cal V, cal V' enter as the
plain symbols V, Vp (no equation differentiates them in the coordinates).
Every expression is then rationalized exactly -- e^f -> EF, e^nu -> EN,
sin -> SS, cos -> CC -- so all linear algebra runs over the rational
function field, with no floating point anywhere.

Stages:
  rows    derive the five elliptic rows and the two constraints.  The w,
          B (rho equation) and psi (KG) rows are transcribed divergence
          forms; the f and nu rows are computed as the exact nullspace of
          the second-derivative-jet coefficient matrix of the mixed
          Einstein set (keep only that field's second jets); the
          constraints come from anchored elimination of E^eta_theta and
          E^eta_eta - E^theta_theta against the five rows.  B's second
          jets legitimately remain in the constraints: rho = B sqrt(h)
          sin theta is dynamical, so rho_{;ab}/rho enters them (at B = 1
          those were the explicit eta0^2-type constants of CKK eqs.
          13/19).  Everything is printed collected in the jets -- the
          source for matter_equations.matter_residual_forms.
  span    exact rational points: each of the seven rows lies in the span
          of the mixed Einstein + KG set AND the seven together span it
          (rank 7 both ways), so solving the derived system is equivalent
          to Einstein + KG, not merely implied by it.
  v0      at V = 0, B = 1, psi = psi(eta): the f and w rows reduce to CKK
          eqs. (10) and (11) (the machine-checked ground truth of
          derive_xy_equations.py) up to a field-dependent factor that is
          printed, so the matter system contains the V = 0 solver exactly.

Run (repo root, CPU, capped -- a sympy runaway can OOM the node
container, CLAUDE.md "Environment"):

    grteclyn-wrapper/scripts/ops/capped_job.sh start derive-matter \
        --threads 4 --mem 4 --timeout 2400 -- \
        grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/analysis/spinning_wormhole/derive_matter_equations.py
"""

from __future__ import annotations

import argparse
import sys
import time

import sympy as sp

t, eta, th, ph = sp.symbols("t eta theta phi", real=True)
eta0 = sp.Symbol("eta0", positive=True)
V, Vp = sp.symbols("V Vp", real=True)
EF, EN = sp.symbols("EF EN", positive=True)      # e^f, e^nu
SS, CC = sp.symbols("SS CC", positive=True)      # sin theta, cos theta
FIELDS = ("f", "nu", "w", "b", "psi")
ORDERS = [(2, 0), (1, 1), (0, 2), (1, 0), (0, 1), (0, 0)]
SECOND = [(2, 0), (1, 1), (0, 2)]

_cache: dict = {}


def functions():
    return {name: sp.Function(name)(eta, th) for name in FIELDS}


def jet_subs(fn_of):
    """(Derivative -> jet symbol) pairs, highest order first, and the jet
    symbols keyed f_20 style (eta order, theta order)."""
    subs, syms = [], {}
    for name, fn in fn_of.items():
        for i, j in ORDERS:
            expr = fn
            for _ in range(i):
                expr = sp.diff(expr, eta)
            for _ in range(j):
                expr = sp.diff(expr, th)
            sym = sp.Symbol(f"{name}_{i}{j}")
            subs.append((expr, sym))
            syms[f"{name}_{i}{j}"] = sym
    return subs, syms


def to_jets(expr, subs):
    for old, new in subs:
        expr = expr.subs(old, new)
    assert not expr.atoms(sp.Derivative), "unsubstituted derivative"
    return expr


def ratform(expr):
    """Exact rationalization: e^{f_00} -> EF, e^{nu_00} -> EN (through
    log substitution, so e^{2 f_00} and friends evaluate), sin -> SS,
    cos -> CC."""
    syms = _cache["syms"]
    e = expr.subs([(syms["f_00"], sp.log(EF)), (syms["nu_00"], sp.log(EN))])
    e = sp.expand(e, power_exp=True)
    e = e.subs([(sp.sin(th), SS), (sp.cos(th), CC)])
    if e.atoms(sp.exp):
        raise ValueError(f"exp survived rationalization: {e.atoms(sp.exp)}")
    return e


def build_system():
    """Rationalized mixed components E^a_b and the KG residual, in jets."""
    if "G" in _cache:
        return _cache["G"], _cache["syms"]
    t0 = time.time()
    fn = functions()
    F, NU, W, B, PSI = (fn[k] for k in FIELDS)
    h = eta**2 + eta0**2
    s, c = sp.sin(th), sp.cos(th)
    p = B**2
    ef, enu = sp.exp(F), sp.exp(NU)
    X = [t, eta, th, ph]
    g = sp.zeros(4)
    g[0, 0] = -ef + p / ef * h * s**2 * W**2
    g[0, 3] = g[3, 0] = -p / ef * h * s**2 * W
    g[3, 3] = p / ef * h * s**2
    g[1, 1] = p / ef * enu
    g[2, 2] = p / ef * enu * h
    gi = sp.zeros(4)
    gi[0, 0] = -1 / ef
    gi[0, 3] = gi[3, 0] = -W / ef
    gi[3, 3] = ef / (p * h * s**2) - W**2 / ef
    gi[1, 1] = ef / (enu * p)
    gi[2, 2] = ef / (enu * p * h)
    check = sp.expand(g * gi - sp.eye(4)).applyfunc(sp.cancel)
    assert check == sp.zeros(4), "metric inverse"

    gam = [[[sp.cancel(sp.together(sum(
        gi[a, d] * (sp.diff(g[d, bb], X[cc]) + sp.diff(g[d, cc], X[bb])
                    - sp.diff(g[bb, cc], X[d])) for d in range(4)) / 2))
        for cc in range(4)] for bb in range(4)] for a in range(4)]
    print(f"  [build] christoffels {time.time() - t0:.0f}s", flush=True)

    components = {(0, 0): "tt", (0, 3): "tph", (3, 3): "phph",
                  (1, 1): "ee", (2, 2): "thth", (1, 2): "eth"}
    ricci = {}
    for bb, cc in components:
        expr = 0
        for a in range(4):
            expr += sp.diff(gam[a][bb][cc], X[a]) - sp.diff(gam[a][bb][a], X[cc])
            for d in range(4):
                expr += (gam[a][a][d] * gam[d][bb][cc]
                         - gam[a][cc][d] * gam[d][bb][a])
        ricci[(bb, cc)] = sp.expand(expr)
    print(f"  [build] ricci {time.time() - t0:.0f}s", flush=True)

    dpsi = {1: sp.diff(PSI, eta), 2: sp.diff(PSI, th)}
    E = {}
    for (bb, cc), R in ricci.items():
        E[(bb, cc)] = R + 2 * dpsi.get(bb, 0) * dpsi.get(cc, 0) + V * g[bb, cc]
    # Mixed components: the Killing block through gi, the 2D block by its
    # diagonal inverse.  ph_t is a linear combination of the other three
    # Killing rows (4 mixed from 3 covariant), so it is left out.
    mixed = {
        "t_t": gi[0, 0] * E[(0, 0)] + gi[0, 3] * E[(0, 3)],
        "t_ph": gi[0, 0] * E[(0, 3)] + gi[0, 3] * E[(3, 3)],
        "ph_ph": gi[3, 0] * E[(0, 3)] + gi[3, 3] * E[(3, 3)],
        "e_e": gi[1, 1] * E[(1, 1)],
        "th_th": gi[2, 2] * E[(2, 2)],
        "e_th": gi[1, 1] * E[(1, 2)],
    }
    # KG times sqrt(-g) = p^{3/2} h s e^{nu - f}, using
    # sqrt(-g) g^{ee} = B h s and sqrt(-g) g^{thth} = B s.
    mixed["kg"] = (sp.diff(B * h * s * sp.diff(PSI, eta), eta)
                   + sp.diff(B * s * sp.diff(PSI, th), th)
                   - B**3 * h * s * enu / ef * Vp / 2)

    subs, syms = jet_subs(fn)
    _cache["syms"] = syms
    G = {k: ratform(to_jets(sp.expand(v), subs)) for k, v in mixed.items()}
    print(f"  [build] jets rationalized {time.time() - t0:.0f}s", flush=True)
    _cache["G"] = G
    return G, syms


def transcribed_rows(syms):
    """The w, rho and KG rows (span-confirmed divergence forms), in jets."""
    fn = functions()
    F, NU, W, B, PSI = (fn[k] for k in FIELDS)
    h = eta**2 + eta0**2
    s = sp.sin(th)
    d = sp.diff
    subs, _ = jet_subs(fn)
    C = {
        # the twist equation: D.(rho^3 e^{-2f} D omega) = 0
        "w": (d(B**3 * h**2 * s**3 * sp.exp(-2 * F) * d(W, eta), eta)
              + d(B**3 * h * s**3 * sp.exp(-2 * F) * d(W, th), th)) / s,
        # the rho equation D^2 rho = 2 cal V rho, rho = B sqrt(h) s:
        # h B_ee + 3 eta B_e + B_thth + 2 (c/s) B_th = 2 V B^3 h e^{nu-f}
        "B": (d(h**sp.Rational(3, 2) * d(B, eta), eta) / sp.sqrt(h)
              + d(s**2 * d(B, th), th) / s**2
              - 2 * V * B**3 * h * sp.exp(NU - F)),
        # KG times sqrt(-g), divided by s
        "psi": ((d(B * h * s * d(PSI, eta), eta)
                 + d(B * s * d(PSI, th), th)) / s
                - B**3 * h * sp.exp(NU - F) * Vp / 2),
    }
    return {k: ratform(to_jets(sp.expand(v), subs)) for k, v in C.items()}


def second_jet_symbols():
    syms = _cache["syms"]
    return [syms[f"{f}_{i}{j}"] for f in FIELDS for (i, j) in SECOND]


def _iszero(x):
    return sp.cancel(x) == 0


def derive_nullspace_row(G, keep, label):
    """The combination of the mixed set whose only second jets are
    `keep`, as the exact symbolic nullspace of the jet-coefficient
    matrix.  Returns the expanded row (or None)."""
    second = second_jet_symbols()
    kill = [s2 for s2 in second if s2.name not in keep]
    names = list(G)
    M = sp.Matrix([[sp.cancel(sp.diff(G[k], s2)) for k in names]
                   for s2 in kill])
    null = M.nullspace(iszerofunc=_iszero)
    if len(null) != 1:
        print(f"rows[{label}]: nullspace dimension {len(null)} != 1  FAIL")
        return None
    vec = null[0]
    combo = sum(sp.cancel(vec[i]) * G[k] for i, k in enumerate(names))
    row = sp.cancel(sp.together(sp.expand(combo)))
    num, den = sp.fraction(row)
    # normalize away the pure-field denominator
    for s2 in kill:
        assert _iszero(sp.diff(num, s2)), (label, s2)
    kept = [k for k in keep if not _iszero(sp.diff(num, _cache["syms"][k]))]
    print(f"rows[{label}]: combination "
          + ", ".join(f"{k}: {sp.sstr(sp.cancel(vec[i]))}"
                      for i, k in enumerate(names) if sp.cancel(vec[i]) != 0))
    if not kept:
        print(f"rows[{label}]: row lost its own second jets  FAIL")
        return None
    return sp.expand(num)


def eliminate(target, rows, label, allow=()):
    """target - sum a_i rows_i with every second jet outside `allow`
    cancelled; the a_i solved symbolically.  Returns the remainder."""
    second = [s2 for s2 in second_jet_symbols() if s2.name not in allow]
    a = {k: sp.Symbol(f"a_{k}") for k in rows}
    expr = sp.expand(target - sum(a[k] * rows[k] for k in rows))
    eqs = [co for s2 in second
           if (co := sp.cancel(sp.diff(expr, s2))) != 0]
    sol = sp.solve(eqs, list(a.values()), dict=True) if eqs else [{}]
    if not sol:
        bad = [s2.name for s2 in second if sp.cancel(sp.diff(expr, s2)) != 0]
        print(f"rows[{label}]: second jets do not cancel: {bad}  FAIL")
        return None
    out = sp.expand(expr.subs(sol[0]).subs(
        {v: 0 for v in a.values() if v not in sol[0]}))
    for s2 in second:
        left = sp.cancel(sp.diff(out, s2))
        assert left == 0, (label, s2, left)
    used = {k: sp.cancel(sol[0][v]) for k, v in a.items()
            if sol[0].get(v, 0) != 0}
    print(f"rows[{label}]: multipliers "
          + (", ".join(f"{k}: {sp.sstr(v)}" for k, v in used.items())
             or "none"))
    num, _ = sp.fraction(sp.cancel(sp.together(out)))
    return sp.expand(num)


def derive_all():
    """All seven rows, cached: w, B, psi transcribed; f, nu nullspace;
    c13, c19 anchored elimination."""
    if "rows" in _cache:
        return _cache["rows"]
    G, syms = build_system()
    rows = transcribed_rows(syms)
    t0 = time.time()
    rows["f"] = derive_nullspace_row(G, ("f_20", "f_02"), "f")
    print(f"  [rows] f {time.time() - t0:.0f}s", flush=True)
    rows["nu"] = derive_nullspace_row(G, ("nu_20", "nu_02"), "nu")
    print(f"  [rows] nu {time.time() - t0:.0f}s", flush=True)
    if rows["f"] is None or rows["nu"] is None:
        _cache["rows"] = rows
        return rows
    h = eta**2 + eta0**2
    pref = syms["b_00"] ** 2 * h * EN / EF
    allow_b = ("b_20", "b_11", "b_02")
    elim_rows = {k: v for k, v in rows.items() if v is not None}
    rows["c13"] = eliminate(sp.expand(pref * h * G["e_th"]), elim_rows,
                            "c13", allow=allow_b)
    rows["c19"] = eliminate(sp.expand(pref * (G["e_e"] - G["th_th"])),
                            elim_rows, "c19", allow=allow_b)
    print(f"  [rows] constraints {time.time() - t0:.0f}s", flush=True)
    _cache["rows"] = rows
    return rows


def stage_rows() -> bool:
    rows = derive_all()
    syms = _cache["syms"]
    ok = True
    for label in ("f", "nu", "w", "B", "psi", "c13", "c19"):
        out = rows.get(label)
        if out is None:
            ok = False
            continue
        num = sp.collect(sp.expand(out), list(syms.values()))
        print(f"\nrows[{label}]:")
        print(sp.sstr(num, order="lex"))
        print(flush=True)
    return ok


def rational_point(seed):
    """Exact substitution for the rationalized expressions."""
    import random

    rng = random.Random(seed)

    def q(lo=-4, hi=4):
        while True:
            val = sp.Rational(rng.randint(lo * 7, hi * 7), rng.randint(1, 7))
            if val != 0:
                return val

    at = {eta: q(), eta0: sp.Rational(2), V: q(), Vp: q(),
          SS: sp.Rational(3, 5), CC: sp.Rational(4, 5),
          EF: sp.Rational(2, 3), EN: sp.Rational(5, 7)}
    for name, sym in _cache["syms"].items():
        if name in ("f_00", "nu_00"):
            continue
        at[sym] = sp.Rational(4, 3) if name == "b_00" else q()
    return at


def affine_vector(expr, at, second_syms):
    """[coefficients of the 15 second jets, remainder] at the point,
    exact rationals (expressions are linear in the second jets)."""
    out = []
    pieces = [sp.diff(expr, s2) for s2 in second_syms]
    rem = expr
    for s2 in second_syms:
        rem = rem.subs(s2, 0)
    for e in pieces + [rem]:
        val = sp.cancel(e.subs(at))
        if not val.is_Rational:
            raise ValueError(f"non-rational evaluation: {val}")
        out.append(sp.Rational(val))
    return out


def stage_span() -> bool:
    rows = derive_all()
    if any(v is None for v in rows.values()):
        print("span: rows incomplete, skipping")
        return False
    G, _ = build_system()
    second = second_jet_symbols()
    ok = True
    for seed in (2, 3, 4):
        at = rational_point(seed)
        Gm = sp.Matrix([affine_vector(G[k], at, second) for k in G])
        Rm = sp.Matrix([affine_vector(v, at, second) for v in rows.values()])
        rank_g, rank_r = Gm.rank(), Rm.rank()
        both = sp.Matrix.vstack(Gm, Rm).rank()
        good = rank_g == rank_r == both == 7
        ok = ok and good
        print(f"span[seed {seed}]: rank(G) = {rank_g}, rank(rows) = {rank_r},"
              f" rank(G + rows) = {both}  "
              f"{'PASS (equivalent systems)' if good else 'FAIL'}",
              flush=True)
    return ok


def stage_v0() -> bool:
    """At V = 0, B = 1 the f and w rows reduce to CKK eqs. (10), (11) up
    to a field-dependent factor."""
    rows = derive_all()
    syms = _cache["syms"]
    if rows.get("f") is None or rows.get("w") is None:
        print("v0: rows incomplete, skipping")
        return False
    h = eta**2 + eta0**2
    at0 = {syms["b_00"]: 1, V: 0, Vp: 0}
    for i, j in ORDERS[:-1]:
        at0[syms[f"b_{i}{j}"]] = 0
    eq10 = (h * SS * syms["f_20"] + 2 * eta * SS * syms["f_10"]
            + SS * syms["f_02"] + CC * syms["f_01"]
            - h * SS**3 / EF**2 * (h * syms["w_10"]**2 + syms["w_01"]**2))
    eq11 = (h**2 * SS**3 / EF**2
            * (syms["w_20"] - 2 * syms["f_10"] * syms["w_10"])
            + 4 * eta * h * SS**3 / EF**2 * syms["w_10"]
            + h * SS**3 / EF**2
            * (syms["w_02"] - 2 * syms["f_01"] * syms["w_01"])
            + 3 * h * SS**2 * CC / EF**2 * syms["w_01"])
    ok = True
    for label, ref in (("f", eq10), ("w", eq11 / SS)):
        fac = sp.cancel(rows[label].subs(at0) / ref)
        jets = [s for s in fac.free_symbols
                if s.name.split("_")[0] in FIELDS and s.name != "f_00"]
        good = not jets
        ok = ok and good
        print(f"v0[{label}]: factor {sp.sstr(fac) if good else 'NOT pure'}"
              f" {'' if good else sp.sstr(fac)}")
    return ok


# Generic test fields in (ETA, Y) for the forms check: nonzero mixed
# derivatives everywhere, B near 1 and positive.
ETA_S, Y_S = sp.symbols("ETAS YS", real=True)
TEST_FIELDS = {
    "f": (sp.sin(ETA_S / 2 + sp.Rational(1, 5)) * (1 + Y_S / 3)
          + sp.exp(-ETA_S**2 / 9) * Y_S**2 / 4),
    "w": (sp.cos(ETA_S / 3) * (Y_S / 2 + sp.Rational(2, 7))
          + sp.exp(-ETA_S**2 / 16) * Y_S**2 / 11),
    "N": (sp.sin(ETA_S / 4 + 1) * (1 - Y_S / 5)
          + Y_S * sp.exp(-(ETA_S - 1)**2 / 25) / 3),
    "B": (1 + sp.cos(ETA_S / 5) * (1 + Y_S / 4) / 10
          + sp.exp(-ETA_S**2 / 12) * Y_S / 9),
    "psi": (sp.sin(ETA_S / 6 + sp.Rational(1, 3)) * (1 + Y_S / 6)
            + sp.exp(-ETA_S**2 / 20) * Y_S**2 / 7),
}

#: printed row == PREFACTOR * matter_residual_forms[...], fixed by the
#: leading-jet coefficients of the derived rows (h = eta^2 + eta0^2,
#: dη = eta'(xi), b = B at the node).
PREFACTORS = {
    ("f", "E_f"): lambda b, h, dn: -EF**2 * SS * b,
    ("w", "E_w"): lambda b, h, dn: SS**2 * b**3 * h / EF**2,
    ("B", "E_B"): lambda b, h, dn: sp.Integer(1),
    ("psi", "E_psi"): lambda b, h, dn: b,
    ("nu", "E_N"): lambda b, h, dn: -2 * EF**2 * SS * b**2 * h,
    ("c13", "E_c"): lambda b, h, dn: EF**2 * SS**2 * CC * b**2 * h**2 / dn,
    ("c19", "E19"): lambda b, h, dn: -4 * EF**2 * SS * b**2,
}


def stage_forms() -> bool:
    """matter_residual_forms against the derived rows, 50 digits, on the
    generic test fields under the arctan and log-stretch maps."""
    from grteclyn_wrapper.analysis.spinning_wormhole.matter_equations import (
        matter_residual_forms,
    )

    rows = derive_all()
    if any(v is None for v in rows.values()):
        print("forms: rows incomplete, skipping")
        return False
    syms = _cache["syms"]
    XI = sp.Symbol("XIv", real=True)
    Yv = sp.Symbol("Yv", real=True)
    THv = sp.Symbol("THv", positive=True)
    maps = {
        "arctan": eta0 * sp.tan(sp.pi * XI / 2),
        "logstretch4": eta0 * sp.sinh(4 * sp.atanh(XI)),
    }
    worst = 0.0
    for mname, eta_of in maps.items():
        deta_of, d2eta_of = sp.diff(eta_of, XI), sp.diff(eta_of, XI, 2)
        comp = {k: e.subs([(ETA_S, eta_of), (Y_S, Yv)])
                for k, e in TEST_FIELDS.items()}
        jets = {}
        for tag, e in comp.items():
            jets[tag] = e
            jets[f"{tag}_x"] = sp.diff(e, XI)
            jets[f"{tag}_xx"] = sp.diff(e, XI, 2)
            jets[f"{tag}_y"] = sp.diff(e, Yv)
            jets[f"{tag}_yy"] = sp.diff(e, Yv, 2)
        jets["B_xy"] = sp.diff(comp["B"], XI, Yv)
        E = matter_residual_forms(sp.exp, eta0=eta0, y=Yv, eta=eta_of,
                                  deta=deta_of, d2eta=d2eta_of, jets=jets,
                                  V=V, dV=Vp)

        # The same fields as functions of (eta, theta) for the rows side:
        # nu = N sin^2 theta, y = cos 2 theta.
        y_th = sp.cos(2 * THv)
        et = {k: e.subs(Y_S, y_th) for k, e in TEST_FIELDS.items()}
        et["nu"] = et.pop("N") * sp.sin(THv)**2
        et["b"] = et.pop("B")
        rowsub = []
        for name in FIELDS:
            if name in ("f",):
                base = et["f"]
            else:
                base = et[name]
            for i, j in ORDERS:
                if name == "f" and (i, j) == (0, 0):
                    continue
                if name == "nu" and (i, j) == (0, 0):
                    continue
                val = sp.diff(base, ETA_S, i) if j == 0 else \
                    sp.diff(sp.diff(base, ETA_S, i), THv, j)
                rowsub.append((syms[f"{name}_{i}{j}"], val))
        rowsub += [(EF, sp.exp(et["f"])), (EN, sp.exp(et["nu"])),
                   (SS, sp.sin(THv)), (CC, sp.cos(THv))]

        xis = [sp.Rational(-7, 10), sp.Rational(1, 5), sp.Rational(3, 5)]
        if mname == "logstretch4":
            xis = [sp.Rational(-2, 5), sp.Rational(1, 10), sp.Rational(3, 10)]
        for xi_val in xis:
            for th_val in (sp.Rational(2, 5), sp.Rational(13, 10)):
                at_xy = {XI: xi_val, Yv: sp.cos(2 * th_val), eta0: 2,
                         V: sp.Rational(5, 11), Vp: sp.Rational(7, 13)}
                eta_val = eta_of.subs({XI: xi_val, eta0: 2})
                at_et = {ETA_S: eta_val, THv: th_val, eta: eta_val,
                         eta0: 2, V: sp.Rational(5, 11),
                         Vp: sp.Rational(7, 13)}
                b_val = TEST_FIELDS["B"].subs(
                    [(ETA_S, eta_val), (Y_S, sp.cos(2 * th_val))])
                h_val = eta_val**2 + 4
                dn_val = deta_of.subs({XI: xi_val, eta0: 2})
                for (rkey, fkey), P in PREFACTORS.items():
                    lhs = rows[rkey].subs(rowsub).subs(at_et).evalf(50)
                    pref = P(b_val, h_val, dn_val).subs(rowsub) \
                        .subs(at_et).evalf(50)
                    rhs = (E[fkey].subs(at_xy).evalf(50)) * pref
                    scale = max(1, abs(lhs), abs(rhs))
                    rel = float(abs(lhs - rhs) / scale)
                    worst = max(worst, rel)
                    if rel > 1e-30:
                        print(f"  forms[{mname}] {rkey} vs {fkey} at "
                              f"xi={xi_val} th={th_val}: rel {rel:.2e} FAIL")
        print(f"  forms[{mname}]: max rel diff so far {worst:.3e}",
              flush=True)
    print(f"forms: max relative difference {worst:.3e} (gate 1e-30): "
          f"{'PASS' if worst <= 1e-30 else 'FAIL'}")
    return worst <= 1e-30


def stage_v0forms() -> bool:
    """matter_residual_forms at V = 0, B = 1 reduces symbolically to
    equations.residual_forms (E_c and E19 gain only their psi terms)."""
    from grteclyn_wrapper.analysis.spinning_wormhole.equations import (
        residual_forms,
    )
    from grteclyn_wrapper.analysis.spinning_wormhole.matter_equations import (
        MATTER_JET_NAMES,
        matter_residual_forms,
    )

    y, et, dn, dnn = sp.symbols("yv etav detav d2etav", real=True)
    jets = {k: sp.Symbol(k) for k in MATTER_JET_NAMES}
    jets.update(B=sp.Integer(1), B_x=0, B_xx=0, B_y=0, B_yy=0, B_xy=0)
    new = matter_residual_forms(sp.exp, eta0=eta0, y=y, eta=et, deta=dn,
                                d2eta=dnn, jets=jets, V=0, dV=0)
    old = residual_forms(sp.exp, eta0=eta0, y=y, eta=et, deta=dn,
                         d2eta=dnn,
                         jets={k: jets[k] for k in jets
                               if not k.startswith(("B", "psi"))})
    h = et**2 + eta0**2
    W2 = (h / dn) ** 2
    oy2 = 1 - y**2
    checks = {
        "E_f": new["E_f"] - old["E_f"],
        "E_w": new["E_w"] - old["E_w"],
        "E_c": new["E_c"] - old["E_c"]
        + 16 * jets["psi_x"] * jets["psi_y"],
        "E19": new["E19"] - (old["D2"] - W2 * jets["psi_x"]**2
                             + 4 * h * oy2 * jets["psi_y"]**2),
    }
    ok = True
    for key, expr in checks.items():
        diff = sp.simplify(expr)
        good = diff == 0
        ok = ok and good
        print(f"v0forms[{key}]: {'identical' if good else f'DIFFERS: {diff}'}")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stage", choices=["rows", "span", "v0", "forms",
                                        "v0forms"], action="append")
    args = ap.parse_args()
    stages = args.stage or ["rows", "span", "v0", "forms", "v0forms"]
    failed = []
    for name, fun in (("rows", stage_rows), ("span", stage_span),
                      ("v0", stage_v0), ("forms", stage_forms),
                      ("v0forms", stage_v0forms)):
        if name in stages:
            print(f"== {name} ==", flush=True)
            if not fun():
                failed.append(name)
    print("ALL PASS" if not failed else f"FAILED: {', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
