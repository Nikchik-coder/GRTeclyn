"""Derivative-free engines sharing one gated objective and evaluation trace."""
from __future__ import annotations

from .state import SearchContext
import numpy as np
from . import objective


def run_engine(ctx: SearchContext, x0):
    """Run Nelder-Mead or CMA-ES with the established bounds and budgets."""
    if ctx.args.engine == "cma":
        import cma

        lo = [ctx.args.m_min, ctx.args.q_min, ctx.args.q_min, ctx.args.q_min]
        hi = [ctx.args.m_max, ctx.args.q_max, ctx.args.q_max, ctx.args.q_max]
        if ctx.args.free_J:
            lo.append(ctx.J_min)
            hi.append(ctx.J_max)
        es = cma.CMAEvolutionStrategy(
            list(x0), ctx.args.sigma0,
            {"CMA_stds": list(ctx.scales),
             "bounds": [lo, hi],
             "popsize": ctx.args.popsize, "maxfevals": ctx.args.maxfev,
             "tolfun": ctx.args.fatol, "verbose": -9, "seed": ctx.args.seed})
        while not es.stop() and ctx.state["nfev"] < ctx.args.maxfev:
            xs = es.ask()
            es.tell(xs, [objective.objective(ctx, np.asarray(xv)) for xv in xs])
        print(f"\ncma stopped: {dict(es.stop()) or 'maxfev'} after "
              f"{ctx.state['nfev']} evaluations", flush=True)
    else:
        from scipy.optimize import minimize

        n = int(x0.size)
        simplex = np.vstack([x0] + [x0 + ctx.scales[i] * np.eye(n)[i]
                                    for i in range(n)])
        res = minimize(lambda x: objective.objective(ctx, x), x0, method="Nelder-Mead",
                       options={"maxfev": ctx.args.maxfev, "fatol": ctx.args.fatol,
                                "xatol": 1e-3, "initial_simplex": simplex,
                                "adaptive": True})
        print(f"\nsimplex stopped: {res.message} after {ctx.state['nfev']} "
              f"evaluations", flush=True)
