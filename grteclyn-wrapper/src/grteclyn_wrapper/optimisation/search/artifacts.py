"""Write search traces and provisional solved-field archives.

TSV columns and NPZ metadata retain their existing formats. Fields are in
grid units; sigma supplies physical lengths. Independent refinement writes
validated artifacts through resolution.save_checked, never dump_npz.
"""
from __future__ import annotations

from .state import SearchContext
import dataclasses
import json
import numpy as np
from ..potentials import PolynomialPotential
from .scoring import min_q
from .state import FIELDS, SAVE_CONVENTIONS


def extra_cols(ctx: SearchContext, row):
    if not ctx.wide:
        return ""
    if row["verdict"] == "FAILED":
        return "\tnan\tnan\tnan\tnan\t" + ctx.args.pin
    return (f"\t{row['J']:.10g}\t{row['R_A']:.10f}\t"
            f"{row['R_pol']:.10f}\t{row['X_A']:.10e}\t{ctx.args.pin}")


def record(ctx: SearchContext, x, row):
    m, q = float(x[0]), tuple(float(v) for v in x[1:4])
    jtag = (f"  J {float(x[4]):.4g}" if len(x) > 4 else "")
    tag = f"m {m:.4f} q ({', '.join(f'{v:+.3f}' for v in q)}){jtag}"
    qvals = "\t".join(f"{v:.6g}" for v in q)
    stab_col = ""
    stab_tag = ""
    if ctx.args.stability:
        lam = row.get("lam")
        stab_col = (f"\t{lam:.8f}" if lam is not None else "\tnan")
        stab_tag = (f"  lam {lam:.4f}" if lam is not None
                    else f"  J0-FAIL ({row['j0_fail']})"
                    if row.get("j0_fail") else "")
    if row["verdict"] == "FAILED":
        print(f"  [{ctx.state['nfev']}] {tag}: NEWTON FAILED "
              f"({row['err']})  [{row['secs']:.0f}s]", flush=True)
        line = (f"{ctx.name}\t{ctx.nx}\t{ctx.ny}\t{m:.6g}\t{qvals}\tnan\tnan\tnan\t"
                f"nan\tnan\tnan\tnan\tnan\tnan\t{min_q(q):.3f}\t"
                f"FAILED{stab_col}{extra_cols(ctx, row)}\n")
    else:
        print(f"  [{ctx.state['nfev']}] {tag}: newton {row['newton']:.1e} "
              f"({row['iters']} it)  X {row['X']:.8e}  "
              f"X_A {row['X_A']:.8e}  R_e/R_pol "
              f"{row['R_e'] / row['R_pol']:.4f}  "
              f"sigma {row['sigma']:.8f}  E19 {row['e19']:.1e}  "
              f"E_c {row['e_c']:.1e}  tails {row['tails']:.1e}  "
              f"{row['verdict']}{stab_tag}  [{row['secs']:.0f}s]",
              flush=True)
        line = (f"{ctx.name}\t{ctx.nx}\t{ctx.ny}\t{m:.6g}\t{qvals}\t"
                f"{row['newton']:.3e}\t{row['iters']}\t"
                f"{row['X']:.10e}\t{row['sigma']:.10f}\t"
                f"{row['psim']:.10f}\t{row['R_e']:.10f}\t"
                f"{row['e19']:.3e}\t{row['e_c']:.3e}\t"
                f"{row['tails']:.3e}\t{min_q(q):.3f}\t"
                f"{row['verdict']}{stab_col}{extra_cols(ctx, row)}\n")
    with ctx.out.open("a") as fh:
        fh.write(line)


def dump_npz(ctx: SearchContext, path, key, row, slot=None):
    """Solved fields and what rebuilds them: collocation nodes, the
    map, sigma, the potential coefficients, and the J = 0 twin."""
    spin = ctx.state["solved"][key]
    twin = ctx.state["solved_j0"].get(key)
    m, q = float(key[0]), [float(v) for v in key[1:4]]
    pot = PolynomialPotential.kink_q(m, float(spin["psim"]), tuple(q))
    arrays = {k: np.asarray(spin[k]) for k in FIELDS}
    if twin is not None:
        arrays.update({f"j0_{k}": np.asarray(twin[k]) for k in FIELDS})
    scal = ("omega", "psim", "sigma", "xi_t")
    meta = {
        "member": ctx.name, "slot": slot, "nx": ctx.nx, "ny": ctx.ny,
        "nfev": ctx.state["nfev"], "member_eta0": ctx.sol.eta0,
        "gamma": ctx.sol.gamma,
        "radial_map": {"class": type(ctx.grid).__name__,
                       **dataclasses.asdict(ctx.grid)},
        "J": float(row.get("J", ctx.J0)),
        "R_e": float(row.get("R_e", ctx.th["R_e"])),
        "R_A": float(row.get("R_A", ctx.th["R_A"])),
        "pin": ctx.args.pin, "m": m, "q": q,
        "potential_coeffs": [float(c) for c in pot.coeffs],
        **{k: float(spin[k]) for k in scal},
        "X": row["X"], "X_A": row.get("X_A"), "X_v0": ctx.x_v0,
        "E19": row["e19"],
        "E_c": row["e_c"],
        "verdict": row["verdict"], "stability": "not_assessed",
        "resolution_validated": False,
        "j0": (None if twin is None
               else {k: float(twin[k]) for k in scal}),
        "conventions": SAVE_CONVENTIONS,
    }
    np.savez(path, sx=ctx.state["nodes"][0], sy=ctx.state["nodes"][1],
             meta=json.dumps(meta, default=float), **arrays)
    return path


def save_solution(ctx: SearchContext, slot):
    _, key, row = ctx.state[slot]
    path = ctx.out.with_name(f"{ctx.out.stem}_{slot}.npz")
    return dump_npz(ctx, path, key, row, slot=slot)
