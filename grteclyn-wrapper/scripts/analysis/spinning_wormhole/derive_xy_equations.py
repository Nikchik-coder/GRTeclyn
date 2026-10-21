#!/usr/bin/env python
"""Machine-check the fast-spin solver's field-equation forms against CKK.

The solver (research/spinningwormhole/SpinningSolver.md) imposes E_f, E_w,
E_N and monitors E_c, D2, all defined ONCE in
grteclyn_wrapper.analysis.spinning_wormhole.equations.residual_forms for a
generic radial map eta(xi).  This script checks that formulation:

  forms    the five forms against Chew-Kleihaus-Kunz (arXiv:1608.05253)
           eqs. (10)-(13) and (19), transcribed in ckk_residuals:
           evaluated on generic test fields at 50 digits, identity /
           arctan / log-stretched maps (gate: max relative difference <= 1e-30)
  doc      the arctan specialization against the closed (x, y) forms of
           SpinningSolver.md section 2, transcribed here (symbolic zero)
  static   the static drainhole satisfies E_f, E_w, E_N, E_c exactly and
           D2 = eta0^2 + mu_+^2, on an UNSPECIFIED map (symbolic zero)
  maps     spectral.py's map derivatives against sympy; log-stretch end
           analyticity: 1/eta analytic in (1 - xi) for even L, not odd;
           L = 2 equals xi = eta/(eta0 + sqrt(h))
  emit     print the generic-map operator coefficients the solver uses

Run (repo root, CPU only, ~2 min, cap it: a sympy runaway can OOM the
container -- CLAUDE.md "Environment"):

    (ulimit -v 16777216; grteclyn-wrapper/.venv/bin/python \
        grteclyn-wrapper/scripts/analysis/spinning_wormhole/derive_xy_equations.py)
"""

from __future__ import annotations

import argparse
import math
import sys

import numpy as np
import sympy as sp

from grteclyn_wrapper.analysis.spinning_wormhole import spectral
from grteclyn_wrapper.analysis.spinning_wormhole.equations import residual_forms

ETA, TH, XI, Y, ETA0 = sp.symbols("eta theta xi y eta0", real=True)


def ckk_residuals(f, nu, w, eta0):
    """CKK eqs. (10)-(13) and the eq.-(19) RHS, transcribed verbatim from
    the solver's research brief (`git show
    f66a10d4:research/spinningwormhole/deep_research_fast_spin_solver.md`);
    f, nu, w are sympy expressions in (ETA, TH)."""
    h = ETA**2 + eta0**2
    s, c = sp.sin(TH), sp.cos(TH)
    e2f = sp.exp(-2 * f)
    d = sp.diff
    eq10 = (d(h * s * d(f, ETA), ETA) + d(s * d(f, TH), TH)
            - h * s**3 * e2f * (h * d(w, ETA)**2 + d(w, TH)**2))
    eq11 = (d(h**2 * s**3 * e2f * d(w, ETA), ETA)
            + d(h * s**3 * e2f * d(w, TH), TH))
    eq12 = (d(h * s * d(nu, ETA), ETA) + s * d(nu, TH, 2) - c * d(nu, TH)
            - h * s**3 * e2f * (h * d(w, ETA)**2 - 2 * d(w, TH)**2))
    eq13 = (-h * s * d(f, ETA) * d(f, TH) + h * c * d(nu, ETA)
            + ETA * s * d(nu, TH)
            + h**2 * s**3 * e2f * d(w, ETA) * d(w, TH))
    d2rhs = (h / 4 * (h * d(f, ETA)**2 - d(f, TH)**2)
             - h / 2 * (ETA * d(nu, ETA) - (c / s) * d(nu, TH))
             - h**2 / 4 * s**2 * e2f * (h * d(w, ETA)**2 - d(w, TH)**2)
             + eta0**2)
    return {"10": eq10, "11": eq11, "12": eq12, "13": eq13, "19": d2rhs}


def jets_of(expr_xy):
    """The jet dict residual_forms reads, from one (XI, Y) expression."""
    d = sp.diff
    return (expr_xy, d(expr_xy, XI), d(expr_xy, XI, 2),
            d(expr_xy, Y), d(expr_xy, Y, 2))


def solver_residuals(fF, wF, NF, eta_of_xi, eta0):
    """residual_forms on test fields given in (ETA, Y), composed with the
    map eta(xi): the jets are exact sympy derivatives in (XI, Y)."""
    comp = {"f": fF.subs(ETA, eta_of_xi), "w": wF.subs(ETA, eta_of_xi),
            "N": NF.subs(ETA, eta_of_xi)}
    jets = {}
    for tag, e in comp.items():
        jets[tag], jets[f"{tag}_x"], jets[f"{tag}_xx"], jets[f"{tag}_y"], \
            jets[f"{tag}_yy"] = jets_of(e)
    return residual_forms(
        sp.exp, eta0=eta0, y=Y, eta=eta_of_xi,
        deta=sp.diff(eta_of_xi, XI), d2eta=sp.diff(eta_of_xi, XI, 2),
        jets=jets)


# Generic test fields in (ETA, Y): nonzero mixed derivatives everywhere,
# omega theta-dependent (the O(J) member's omega is not, so it would not
# exercise the w_y terms).
F_TEST = (sp.sin(ETA / 2 + sp.Rational(1, 5)) * (1 + Y / 3)
          + sp.exp(-ETA**2 / 9) * Y**2 / 4)
W_TEST = (sp.cos(ETA / 3) * (Y / 2 + sp.Rational(2, 7))
          + sp.exp(-ETA**2 / 16) * Y**2 / 11)
N_TEST = (sp.sin(ETA / 4 + 1) * (1 - Y / 5)
          + Y * sp.exp(-(ETA - 1)**2 / 25) / 3)


def check_forms() -> float:
    """Max relative difference, all five forms x three maps x sample points."""
    maps = {
        "identity": XI,
        "arctan": ETA0 * sp.tan(sp.pi * XI / 2),
        "logstretch4": ETA0 * sp.sinh(4 * sp.atanh(XI)),
    }
    nu_test = N_TEST.subs(Y, sp.cos(2 * TH)) * sp.sin(TH)**2
    ckk = ckk_residuals(F_TEST.subs(Y, sp.cos(2 * TH)), nu_test,
                        W_TEST.subs(Y, sp.cos(2 * TH)), ETA0)
    worst = 0.0
    for name, eta_of_xi in maps.items():
        E = solver_residuals(F_TEST, W_TEST, N_TEST, eta_of_xi, ETA0)
        h = eta_of_xi**2 + ETA0**2
        s, c = sp.sin(TH), sp.cos(TH)
        e2f = sp.exp(-2 * F_TEST.subs({ETA: eta_of_xi, Y: sp.cos(2 * TH)}))
        deta = sp.diff(eta_of_xi, XI)
        pairs = {
            "10": s * E["E_f"],
            "11": h * s**3 * e2f * E["E_w"],
            "12": s**3 * E["E_N"],
            "13": (h / deta) * s**2 * c * E["E_c"],
            "19": E["D2"],
        }
        xis = [sp.Rational(-7, 10), sp.Rational(1, 5), sp.Rational(3, 5)]
        if name == "logstretch4":  # keep eta within the test fields' scale
            xis = [sp.Rational(-2, 5), sp.Rational(1, 10), sp.Rational(3, 10)]
        for eta0_val in ([2, 1] if name == "arctan" else [2]):
            for xi_val in xis:
                for th_val in [sp.Rational(2, 5), sp.Rational(13, 10)]:
                    at = {XI: xi_val, TH: th_val, Y: sp.cos(2 * th_val),
                          ETA0: eta0_val}
                    eta_val = eta_of_xi.subs({XI: xi_val, ETA0: eta0_val})
                    for key, mapped in pairs.items():
                        lhs = ckk[key].subs(ETA, eta_val).subs(at).evalf(50)
                        rhs = mapped.subs(at).evalf(50)
                        scale = max(1, abs(lhs), abs(rhs))
                        rel = float(abs(lhs - rhs) / scale)
                        worst = max(worst, rel)
        print(f"  forms[{name}]: max rel diff so far {worst:.3e}")
    return worst


def check_doc() -> bool:
    """Arctan specialization == SpinningSolver.md section 2, symbolically."""
    x = sp.Symbol("x", real=True)
    C, S = sp.cos(sp.pi * x / 2), sp.sin(sp.pi * x / 2)
    jets = {k: sp.Symbol(k) for k in (
        "f", "f_x", "f_xx", "f_y", "f_yy", "w", "w_x", "w_xx", "w_y", "w_yy",
        "N", "N_x", "N_xx", "N_y", "N_yy")}
    g = jets
    E = residual_forms(
        sp.exp, eta0=ETA0, y=Y, eta=ETA0 * S / C,
        deta=sp.pi * ETA0 / (2 * C**2), d2eta=sp.pi**2 * ETA0 * S / (2 * C**3),
        jets=jets)
    e2f = sp.exp(-2 * g["f"])
    doc = {
        "E_f": (4 / sp.pi**2 * C**2 * g["f_xx"] + 4 * (1 - Y**2) * g["f_yy"]
                - (6 * Y + 2) * g["f_y"]
                - ETA0**2 * (1 - Y) / 2 * e2f
                * (4 / sp.pi**2 * g["w_x"]**2
                   + 4 * (1 - Y**2) / C**2 * g["w_y"]**2)),
        "E_w": (4 / sp.pi**2 * (C**2 * (g["w_xx"] - 2 * g["f_x"] * g["w_x"])
                                + sp.pi * S * C * g["w_x"])
                + 4 * (1 - Y**2) * g["w_yy"] - (10 * Y + 6) * g["w_y"]
                - 8 * (1 - Y**2) * g["f_y"] * g["w_y"]),
        "E_N": (4 / sp.pi**2 * C**2 * g["N_xx"] + 4 * (1 - Y**2) * g["N_yy"]
                - (10 * Y + 6) * g["N_y"] - 2 * g["N"]
                - ETA0**2 * e2f * (4 / sp.pi**2 * g["w_x"]**2
                                   - 8 * (1 - Y**2) / C**2 * g["w_y"]**2)),
        "E_c": (4 * g["f_x"] * g["f_y"] + g["N_x"]
                + sp.pi * S / C * (g["N"] - (1 - Y) * g["N_y"])
                - 2 * ETA0**2 * (1 - Y) / C**2 * e2f * g["w_x"] * g["w_y"]),
        "D2": ETA0**2 * (
            1 + g["f_x"]**2 / sp.pi**2 - (1 - Y**2) * g["f_y"]**2 / C**2
            - S * (1 - Y) / (2 * sp.pi * C) * g["N_x"]
            + ((1 + Y) * g["N"] - (1 - Y**2) * g["N_y"]) / (2 * C**2)
            - (1 - Y) * ETA0**2 / (2 * C**2) * e2f
            * (g["w_x"]**2 / sp.pi**2 - (1 - Y**2) * g["w_y"]**2 / C**2)),
    }
    ok = True
    for key in doc:
        diff = sp.simplify(E[key] - doc[key])
        good = diff == 0
        ok = ok and good
        print(f"  doc[{key}]: {'identical' if good else f'DIFFERS: {diff}'}")
    return ok


def check_static() -> bool:
    """The static drainhole on an UNSPECIFIED map eta(xi)."""
    gamma = sp.Symbol("gamma", real=True)
    eta_fn = sp.Function("eta")(XI)
    f = gamma / 2 * (1 - (2 / sp.pi) * sp.atan(eta_fn / ETA0))
    zero = sp.Integer(0)
    jets = dict.fromkeys(
        ("w", "w_x", "w_xx", "w_y", "w_yy", "N", "N_x", "N_xx", "N_y", "N_yy"),
        zero)
    jets.update(f=f, f_x=sp.diff(f, XI), f_xx=sp.diff(f, XI, 2),
                f_y=zero, f_yy=zero)
    E = residual_forms(sp.exp, eta0=ETA0, y=Y, eta=eta_fn,
                       deta=sp.diff(eta_fn, XI), d2eta=sp.diff(eta_fn, XI, 2),
                       jets=jets)
    mu_plus2 = gamma**2 * ETA0**2 / (4 * sp.pi**2)
    checks = {
        "E_f": E["E_f"], "E_w": E["E_w"], "E_N": E["E_N"], "E_c": E["E_c"],
        "D2 - (eta0^2 + mu_+^2)": E["D2"] - ETA0**2 - mu_plus2,
    }
    ok = True
    for key, expr in checks.items():
        diff = sp.simplify(expr)
        good = diff == 0
        ok = ok and good
        print(f"  static[{key}]: {'0 exactly' if good else f'DIFFERS: {diff}'}")
    return ok


def check_maps() -> bool:
    """spectral.py map derivatives vs sympy; log-stretch end analyticity."""
    ok = True
    sym = {"arctan": ETA0 * sp.tan(sp.pi * XI / 2),
           "logstretch": ETA0 * sp.sinh(4 * sp.atanh(XI))}
    mk = {"arctan": spectral.ArctanMap(eta0=2.0),
          "logstretch": spectral.LogStretchMap(eta0=2.0, L=4)}
    for name, expr in sym.items():
        m = mk[name]
        for xi_val in (-0.73, 0.11, 0.62):
            at = {XI: xi_val, ETA0: 2.0}
            for which, code_val in (("eta", m.eta(xi_val)),
                                    ("deta", m.deta(xi_val)),
                                    ("d2eta", m.d2eta(xi_val))):
                order = {"eta": 0, "deta": 1, "d2eta": 2}[which]
                ref = float(sp.diff(expr, XI, order).subs(at).evalf(30))
                rel = abs(code_val - ref) / max(1.0, abs(ref))
                if rel > 5e-14:
                    ok = False
                    print(f"  maps[{name}.{which}] at xi={xi_val}: rel {rel:.2e} FAIL")
            inv = m.xi_of_eta(m.eta(xi_val))
            if abs(inv - xi_val) > 1e-13:
                ok = False
                print(f"  maps[{name}] inverse off by {abs(inv - xi_val):.2e}")
    print("  maps: spectral.py derivatives match sympy" if ok else
          "  maps: FAIL (above)")

    # L = 2 is xi = eta/(eta0 + sqrt(h)).
    t = sp.Symbol("t", positive=True)   # eta/eta0
    l2 = sp.simplify(sp.tanh(sp.asinh(t) / 2).rewrite(sp.exp)
                     .rewrite(sp.log).expand()
                     - t / (1 + sp.sqrt(1 + t**2)))
    good = l2 == 0
    ok = ok and good
    print(f"  maps[L=2 == eta/(eta0+sqrt(h))]: {'identical' if good else l2}")

    # End analyticity: eta0/eta as a series in u = 1 - xi has only integer
    # powers for even L (so 1/eta, h, and the far-field tails stay spectral),
    # and half-integer powers for odd L (the counterexample).
    u = sp.Symbol("u", positive=True)
    for L, want_integer in ((2, True), (4, True), (3, False)):
        eta_u = (sp.Rational(1, 2)
                 * (((2 - u) / u)**sp.Rational(L, 2)
                    - (u / (2 - u))**sp.Rational(L, 2)))  # eta/eta0 at xi=1-u
        series = sp.series(1 / eta_u, u, 0, L + 3).removeO()
        powers = {m.as_base_exp()[1] for m in series.atoms(sp.Pow)
                  if m.as_base_exp()[0] == u}
        integer = all(e.is_integer for e in powers)
        good = integer == want_integer
        ok = ok and good
        print(f"  maps[L={L} end series]: powers of (1-xi) "
              f"{'integer' if integer else 'half-integer'} "
              f"({'as required' if good else 'WRONG'})")
    return ok


def check_kerr() -> bool:
    """Extremal Kerr (a = M) fits the ansatz exactly with eta0 = 0:
    r = eta + M, e^{-f} = g_phph/(eta^2 sin^2 th), omega = -g_tph/g_phph,
    e^{nu} = (Sigma/eta^2) e^{f}.  The imposed forms E_f, E_w and the
    monitors E_c, D2 (D = 0 here) must vanish on it; the PUBLISHED eq. 12
    (= sin^3 th * E_N) must NOT: it leaves ~1e-2, an error in the published
    equation.  Kept as a regression check so the N solve never
    reverts to the printed equation."""
    M = sp.Symbol("M", positive=True)
    eta = XI
    r = eta + M
    c2 = (1 + Y) / 2
    s2v = (1 - Y) / 2
    Sig = r**2 + M**2 * c2
    gpp_over_s2 = r**2 + M**2 + 2 * M**3 * r * s2v / Sig
    F = -sp.log(gpp_over_s2 / eta**2)
    W = 2 * M**2 * r / (Sig * gpp_over_s2)
    NU = sp.log(Sig / eta**2) + F
    Nbar = NU / s2v
    jets = {}
    for tag, e in (("f", F), ("w", W), ("N", Nbar)):
        jets[tag], jets[f"{tag}_x"], jets[f"{tag}_xx"], jets[f"{tag}_y"], \
            jets[f"{tag}_yy"] = jets_of(e)
    E = residual_forms(sp.exp, eta0=0, y=Y, eta=eta, deta=sp.Integer(1),
                       d2eta=sp.Integer(0), jets=jets)
    pts = [{XI: sp.Rational(7, 10), Y: sp.Rational(-1, 3), M: 1},
           {XI: sp.Rational(3, 2), Y: sp.Rational(2, 5), M: 1},
           {XI: 4, Y: sp.Rational(1, 5), M: 2}]
    ok = True
    worst = {k: 0 for k in ("E_f", "E_w", "E_c", "D2")}
    eq12_floor = sp.oo
    for at in pts:
        for k in worst:
            worst[k] = max(worst[k], abs(E[k].subs(at).evalf(50)))
        s3 = ((1 - Y) / 2 * sp.sqrt((1 - Y) / 2)).subs(at)
        eq12_floor = min(eq12_floor, abs((E["E_N"] * s3).subs(at).evalf(50)))
    for k, v in worst.items():
        good = v <= sp.Float(1e-30)
        ok = ok and good
        print(f"  kerr[{k}]: max {sp.N(v, 3)} "
              f"{'(vanishes, as required)' if good else 'FAIL'}")
    good = eq12_floor >= sp.Float(1e-4)
    ok = ok and good
    print(f"  kerr[printed eq12]: min |residual| {sp.N(eq12_floor, 3)} "
          f"{'(nonzero: the published typo, as expected)' if good else 'FAIL'}")
    return ok


def emit() -> None:
    print("""\
  Generic-map operator coefficients (equations.residual_forms), with
  h = eta^2 + eta0^2 and eta', eta'' the xi-derivatives of the map:
    A2 = h / eta'^2                      f_xx, N_xx weight
    A1 = 2 eta / eta' - h eta'' / eta'^3 f_x, N_x weight (0 on arctan)
    B1 = 4 eta / eta' - h eta'' / eta'^3 w_x weight ((4/pi) S C on arctan)
    W2 = (h / eta')^2                    e^{-2f} w_x^2 weight
  Angular pieces are map-free: 4(1-y^2) d_yy, -(6y+2) d_y (f),
  -(10y+6) d_y (w, N), -2 (N).  CKK prefactors:
    eq10 = sin(th) E_f, eq11 = h sin^3(th) e^{-2f} E_w,
    eq12 = sin^3(th) E_N, eq13 = (h/eta') sin^2(th) cos(th) E_c.""")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stage", choices=["forms", "doc", "static", "maps",
                                        "kerr", "emit"], action="append",
                    help="run only these stages (default: all)")
    args = ap.parse_args()
    stages = args.stage or ["forms", "doc", "static", "maps", "kerr",
                            "emit"]
    failed = []
    if "forms" in stages:
        print("forms: residual_forms vs CKK (10)-(13), (19), 50 digits")
        worst = check_forms()
        print(f"forms: max relative difference {worst:.3e} "
              f"(gate 1e-30): {'PASS' if worst <= 1e-30 else 'FAIL'}")
        if worst > 1e-30:
            failed.append("forms")
    if "doc" in stages:
        print("doc: arctan specialization vs SpinningSolver.md section 2")
        if not check_doc():
            failed.append("doc")
    if "static" in stages:
        print("static: the static drainhole on an unspecified map")
        if not check_static():
            failed.append("static")
    if "maps" in stages:
        print("maps: spectral.py derivatives; log-stretch analyticity")
        if not check_maps():
            failed.append("maps")
    if "kerr" in stages:
        print("kerr: extremal Kerr closes every form; the printed eq. 12 fails")
        if not check_kerr():
            failed.append("kerr")
    if "emit" in stages:
        emit()
    print("ALL PASS" if not failed else f"FAILED: {', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
