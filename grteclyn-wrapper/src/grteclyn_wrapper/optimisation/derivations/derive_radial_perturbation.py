"""Derive and verify linear radial perturbation equations.

Input: a named symbolic stage; output: derived rows and identity checks.
Conventions are psi = sqrt(4*pi)*phi and cal V = 8*pi*V_evo.
The radial stability screen remains diagnostic and under repair.
Run symbolic calculations under the capped job runner.

    python -m grteclyn_wrapper.optimisation.derivations.derive_radial_perturbation --help

Mathematical conventions and checks
----------------------------------
The stability screen's first rung: linear perturbations of a STATIC
spherically symmetric phantom wormhole with potential, in the solver's
conventions (E_ab = R_ab + 2 psi_a psi_b + cal V g_ab = 0,
box psi = cal V'/2).  The time-dependent ansatz keeps the solver's
chart -- zero shift, conformal spatial form --

    ds^2 = -e^F dt^2 + P^2 e^{-F} [d eta^2 + h dOmega^2],
    h = eta^2 + eta0^2,   F(t, eta), P(t, eta), psi(t, eta),

which is a complete gauge for linear spherical perturbations (two gauge
functions spent on zero shift and spatial conformality) and is REGULAR
through the throat, unlike the areal gauge of the literature.  About a
static background (F0, P0, psi0) the perturbation
(dF, dP, dpsi) e^{lam t} obeys five linearized rows: E_ee, E_thth and
KG are imposed (3 equations, 3 unknowns, lam only as lam^2 -- the
static problem keeps the clean quadratic structure rotation breaks),
and E_tt, E_teta are the unimposed constraint monitors (E_teta carries
one power of lam, printed divided by it).

Stages:
  rows    linearize, rationalize, print the five rows collected in the
          perturbation jets -- the source for
          optimisation/stability_radial.py.
  lam     assert the imposed rows carry lam only as lam^2 and E_teta
          exactly one power.
  forms   the transcribed coefficient builder
          (stability_radial.radial_rows) against the derived rows at 50
          digits on generic backgrounds and perturbations, both maps.

"""

from __future__ import annotations

import argparse
import sys

import sympy as sp

t, eta = sp.symbols("t eta", real=True)
eta0 = sp.Symbol("eta0", positive=True)
LAM = sp.Symbol("lam", positive=True)
EPS = sp.Symbol("eps", real=True)
#: background potential values at psi0: cal V, cal V', cal V''
V0, V1, V2 = sp.symbols("V0 V1 V2", real=True)
EF, EL = sp.symbols("EF EL", positive=True)   # e^{F0}, e^{lam t}

PERT = ("dF", "dP", "dpsi")
BG = ("F0", "P0", "psi0")
ORD2 = (0, 1, 2)

_cache: dict = {}


def build_rows():
    """The five linearized rows, rationalized, in background and
    perturbation jets."""
    if "rows" in _cache:
        return _cache["rows"]
    th, ph = sp.symbols("theta phi", real=True)
    h = eta**2 + eta0**2
    s = sp.sin(th)
    F0, P0, psi0 = (sp.Function(k)(eta) for k in BG)
    dF, dP, dpsi = (sp.Function(k)(eta) for k in PERT)
    Ft = F0 + EPS * sp.exp(LAM * t) * dF
    Pt = P0 + EPS * sp.exp(LAM * t) * dP
    PSIt = psi0 + EPS * sp.exp(LAM * t) * dpsi
    # cal V about psi0, to first order; V2 reaches only the KG row
    Vt = V0 + V1 * (PSIt - psi0)
    Vpt = V1 + V2 * (PSIt - psi0)

    X = [t, eta, th, ph]
    g = sp.diag(-sp.exp(Ft), Pt**2 * sp.exp(-Ft),
                Pt**2 * sp.exp(-Ft) * h, Pt**2 * sp.exp(-Ft) * h * s**2)
    gi = g.inv()
    gam = [[[sp.cancel(sp.together(sum(
        gi[a, d] * (sp.diff(g[d, b], X[c]) + sp.diff(g[d, c], X[b])
                    - sp.diff(g[b, c], X[d])) for d in range(4)) / 2))
        for c in range(4)] for b in range(4)] for a in range(4)]
    comps = {(0, 0): "tt", (0, 1): "teta", (1, 1): "ee", (2, 2): "thth"}
    rows = {}
    for (b, c), label in comps.items():
        R = 0
        for a in range(4):
            R += sp.diff(gam[a][b][c], X[a]) - sp.diff(gam[a][c][a], X[b])
            for d in range(4):
                R += (gam[a][a][d] * gam[d][b][c]
                      - gam[a][c][d] * gam[d][b][a])
        E = (R + 2 * sp.diff(PSIt, X[b]) * sp.diff(PSIt, X[c])
             + Vt * g[b, c])
        rows[label] = E
    # KG times sqrt(-g)/(s P e^{-F}): d/dt and d/deta parts
    sqg = Pt**3 * sp.exp(-Ft) * h * s   # sqrt(-g) = P^3 e^{-F} h s
    kg = (sp.diff(sqg * gi[0, 0] * sp.diff(PSIt, t), t)
          + sp.diff(sqg * gi[1, 1] * sp.diff(PSIt, eta), eta)) / s \
        - sqg / s * Vpt / 2
    rows["kg"] = kg

    out = {}
    for label, E in rows.items():
        lin = sp.diff(sp.expand(E), EPS).subs(EPS, 0)
        lin = sp.expand(lin / sp.exp(LAM * t))
        # jets to symbols
        subs = []
        for name, fn in (("dF", dF), ("dP", dP), ("dpsi", dpsi),
                         ("F0", F0), ("P0", P0), ("psi0", psi0)):
            for k in (2, 1, 0):
                subs.append((sp.diff(fn, eta, k) if k else fn,
                             sp.Symbol(f"{name}_{k}")))
        for old, new in subs:
            lin = lin.subs(old, new)
        assert not lin.atoms(sp.Derivative), (label, "derivative left")
        # rationalize e^{+-F0} exactly, through the log (ratform's trick)
        lin = lin.subs(sp.Symbol("F0_0"), sp.log(EF))
        lin = sp.expand(lin, power_exp=True)
        if lin.atoms(sp.exp):
            raise ValueError(f"{label}: exp survived {lin.atoms(sp.exp)}")
        out[label] = sp.expand(lin)
    _cache["rows"] = out
    return out


def stage_rows() -> bool:
    rows = build_rows()
    jets = [sp.Symbol(f"{n}_{k}") for n in PERT for k in ORD2]
    ok = True
    for label in ("ee", "thth", "kg", "tt", "teta"):
        e = rows[label]
        if label == "teta":
            e = sp.cancel(e / LAM)
        rem = e
        print(f"\nrows[{label}] (per-jet coefficients, cancelled):")
        for jet in jets:
            c = sp.cancel(sp.together(sp.diff(e, jet)))
            rem = rem.subs(jet, 0)
            if c != 0:
                if c.has(*jets):
                    print(f"  {jet}: NONLINEAR  FAIL")
                    ok = False
                print(f"  {jet}: {sp.sstr(sp.factor(c))}")
        rem = sp.cancel(rem)
        if rem != 0:
            print(f"  REMAINDER: {sp.sstr(rem)}  FAIL")
            ok = False
        print(flush=True)
    return ok


def stage_lam() -> bool:
    rows = build_rows()
    ok = True
    for label in ("ee", "thth", "kg", "tt"):
        e = sp.expand(rows[label])
        odd = sp.cancel(sp.diff(e, LAM).subs(LAM, 0))
        good = odd == 0
        ok = ok and good
        print(f"lam[{label}]: {'even in lam' if good else 'ODD TERM'} "
              f"{'PASS' if good else 'FAIL'}")
    e = sp.expand(rows["teta"])
    rem = sp.cancel(e - LAM * sp.cancel(e / LAM))
    good = rem == 0 and sp.cancel(sp.diff(sp.cancel(e / LAM), LAM)) == 0
    ok = ok and good
    print(f"lam[teta]: {'exactly linear in lam' if good else 'NOT'} "
          f"{'PASS' if good else 'FAIL'}")
    return ok


def stage_forms() -> bool:
    """stability_radial.radial_rows against the derived rows, 50 digits,
    on generic backgrounds and perturbations."""
    from grteclyn_wrapper.optimisation.stability_radial import radial_rows

    rows = build_rows()
    ETA = sp.Symbol("ETAv", real=True)
    test = {
        "F0": sp.sin(ETA / 3 + sp.Rational(1, 5)) / 2,
        "P0": 1 + sp.cos(ETA / 4) / 10,
        "psi0": sp.atan(ETA / 2) + sp.exp(-ETA**2 / 9) / 7,
        "dF": sp.sin(ETA / 5 + sp.Rational(2, 7)),
        "dP": sp.cos(ETA / 6 + sp.Rational(1, 3)) / 3,
        "dpsi": sp.sin(ETA / 4 + sp.Rational(3, 5)) / 2,
    }
    pots = {V0: sp.Rational(5, 11), V1: sp.Rational(7, 13),
            V2: sp.Rational(3, 7), LAM: sp.Rational(9, 8), eta0: 2}
    worst = 0.0
    for eta_val in (sp.Rational(-13, 10), sp.Rational(2, 5),
                    sp.Rational(17, 10)):
        at = dict(pots)
        at[eta] = eta_val
        jets = {}
        for name, e in test.items():
            for k in ORD2:
                at[sp.Symbol(f"{name}_{k}")] = sp.diff(e, ETA, k).subs(
                    ETA, eta_val)
                jets[f"{name}_{k}"] = float(
                    sp.diff(e, ETA, k).subs(ETA, eta_val).evalf(30))
        at[EF] = sp.exp(at[sp.Symbol("F0_0")])
        num = radial_rows(
            eta=float(eta_val), eta0=2.0,
            bg={k: jets[k] for k in jets if not k.startswith("d")},
            pert={k: jets[k] for k in jets if k.startswith("d")},
            V0=float(sp.Rational(5, 11)), V1=float(sp.Rational(7, 13)),
            V2=float(sp.Rational(3, 7)), lam2=float(sp.Rational(81, 64)))
        for label in ("ee", "thth", "kg", "tt", "teta"):
            e = rows[label]
            if label == "teta":
                e = sp.cancel(e / LAM)
            # the substituted row is one exact constant; evalf alone,
            # simplify on it is minutes of pure waste
            lhs = e.subs(at).evalf(50)
            rel = float(abs(lhs - num[label])
                        / max(1.0, abs(lhs), abs(num[label])))
            worst = max(worst, rel)
            if rel > 1e-12:
                print(f"  forms[{label}] at eta={eta_val}: rel {rel:.2e} "
                      f"FAIL (sym {lhs:.6e}, num {num[label]:.6e})")
    print(f"forms: max relative difference {worst:.3e} (gate 1e-12, the "
          f"transcription is float): {'PASS' if worst <= 1e-12 else 'FAIL'}")
    return worst <= 1e-12


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stage", choices=["rows", "lam", "forms"],
                    action="append")
    args = ap.parse_args(argv)
    stages = args.stage or ["rows", "lam", "forms"]
    failed = []
    for name, fun in (("rows", stage_rows), ("lam", stage_lam),
                      ("forms", stage_forms)):
        if name in stages:
            print(f"== {name} ==", flush=True)
            if not fun():
                failed.append(name)
    print("ALL PASS" if not failed else f"FAILED: {', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
