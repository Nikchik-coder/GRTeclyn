"""Score admissible potentials and keep screened and refined bests separate.

X = |VIQ|/R_e; the fixed-area alternative uses X_A = |VIQ|/R_A.
Rejected points receive finite death penalties. Continuation uses the
nearest solved point in scaled L1 knob distance. Stability is unassessed.
"""
from __future__ import annotations

from .state import SearchContext
import numpy as np
from . import evaluation, continuation, artifacts
from .scoring import min_q, death, monitor_overflow


def objective(ctx: SearchContext, x):
    ctx.state["nfev"] += 1
    m, q = float(x[0]), tuple(float(v) for v in x[1:4])
    j_try = float(x[4]) if len(x) > 4 else ctx.J0
    if (not (ctx.args.m_min <= m <= ctx.args.m_max)
            or any(not (ctx.args.q_min <= qk <= ctx.args.q_max) for qk in q)
            or (ctx.args.free_J and not (ctx.J_min <= j_try <= ctx.J_max))
            or min_q(q) <= 0.0):
        print(f"  [{ctx.state['nfev']}] m {m:.4f} q "
              f"({', '.join(f'{v:+.3f}' for v in q)}): inadmissible",
              flush=True)
        return death(10.0)
    key = tuple(map(float, x))
    seed = continuation.nearest_seed(ctx.state["solved"], key, ctx.scales, ctx.prev0)
    row, nxt = evaluation.solve_at(ctx, x, seed)
    row["nfev"] = ctx.state["nfev"]
    lam = None
    if nxt is not None and ctx.args.stability:
        lam, row["j0_fail"] = continuation.stab_at(ctx, x, key, nxt)
        row["lam"] = lam
    artifacts.record(ctx, x, row)
    if nxt is None:
        return death(10.0)
    ctx.state["solved"][key] = nxt
    if (ctx.args.save_accepted and not ctx.args.no_save
            and row["verdict"] in ("PASS", "FRONTIER")
            and "nodes" in ctx.state):
        artifacts.dump_npz(ctx, ctx.out.with_name(f"{ctx.out.stem}_e{ctx.state['nfev']:04d}.npz"),
                 key, row, slot=f"e{ctx.state['nfev']:04d}")
    if row["verdict"] == "ABOVE-GATE":
        return death(monitor_overflow(row))
    mon_pen = 0.0 if row["verdict"] == "PASS" else 0.1
    score = row[ctx.score_key]
    val = score + mon_pen
    if ctx.args.stability:
        val += (ctx.args.stab_fail_pen if lam is None
                else ctx.args.stab_weight * lam)
    if ctx.state["best_frontier"] is None or score < ctx.state["best_frontier"][0]:
        ctx.state["best_frontier"] = (score, key, dict(row))
    incumbent = ctx.state["best_clean" if ctx.args.refine_best == "each" else "best_screened"]
    if row["verdict"] == "PASS" and (incumbent is None or score < incumbent[0]):
        checked = evaluation.check_best(ctx, key, row, "screen")
        if checked is None:
            return death(1.0)
        if ctx.args.refine_best == "each":
            checked = evaluation.check_best(ctx, key, row, "refine")
            if checked is None:
                return death(1.0)
        val = checked[ctx.score_key]
    return val
