"""Prepare a member, run the potential search, and independently refine its best.

The command parser supplies options and its error reporter. Outputs retain
existing names and units. A missing validated finalist returns exit code 2;
failed initial continuation returns 1. This module never launches evolutions.
"""
from __future__ import annotations
import dataclasses
import math
import pathlib
import numpy as np
from grteclyn_wrapper.analysis.spinning_wormhole.solution import Solution
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import lobatto
from ..exoticity import throat
from ..knobs import bill_name, knob_vector, pin_held
from ..matter_equations import MatterCollocationProblem
from ..resolution import refinement_grids
from ..solver.device import select_device
from ..solver.newton import newton
from . import artifacts, continuation, evaluation
from .engines import run_engine
from .state import SearchContext, SCALES, TOL


def run(args, *, error):
    """Execute one search with parsed CLI options and no global search state."""
    if args.stability:
        error("the radial stability screen is under repair; omit --stability")
    select_device(args.gpu, args.jac_chunk)
    x0_in = np.array([float(v) for v in args.x0.split(",")])
    assert args.q_min < args.q_max, "--q-min must be < --q-max"
    if x0_in.size not in (4, 5):
        error("--x0 takes m,q1,q2,q3 or m,q1,q2,q3,J")
    if x0_in.size == 5 and not args.free_J:
        error("--x0 with five values needs --free-J")
    if not (args.m_min <= x0_in[0] <= args.m_max) or np.any(
            (x0_in[1:4] < args.q_min) | (x0_in[1:4] > args.q_max)):
        error("--x0 sits outside the m or q bounds")

    sol = Solution.load(args.solution)
    J_member = float(sol.meta["prescribed"]["J"])
    J0 = J_member if args.J_pin is None else float(args.J_pin)
    try:
        x0 = knob_vector(x0_in, free_j=args.free_J, j_start=J0)
    except ValueError as err:
        error(str(err))
    J0 = float(x0[4]) if args.free_J else J0
    J_min, J_max = args.J_min, args.J_max
    if args.free_J:
        if J_max is None:
            span = max(abs(J_member), abs(J0))
            if span <= 0.0:
                error("--free-J on a static start needs --J-max")
            J_max = span
        if not (J_min < J_max):
            error("--J-min must be < --J-max")
        if not (J_min <= J0 <= J_max):
            error("starting J sits outside --J-min/--J-max")
    J_step = args.J_step
    if args.free_J and J_step is None:
        J_step = 0.1 * (J_max - J_min)
    scales = np.array([args.m_step, *SCALES[1:]]
                      + ([J_step] if args.free_J else []))
    score_key = bill_name(args.pin)
    psim0 = -math.pi * sol.observables["D"] / sol.eta0
    nx = args.nx or sol.nx
    ny = args.ny or sol.ny
    name = args.solution.rsplit("/", 1)[-1]
    stem = name.rsplit(".", 1)[0]
    extra = (f"_{args.pin}" if args.pin != "R_e" else "") + (
        "_freeJ" if args.free_J else "")
    out = pathlib.Path(args.out or f"runs/optimisation/opt/{stem}_opt4"
                                   f"{'s' if args.stability else ''}"
                                   f"{extra}_{nx}x{ny}.tsv")
    out.parent.mkdir(parents=True, exist_ok=True)
    wide = args.pin != "R_e" or args.free_J
    extra_head = "\tJ\tR_A\tR_pol\tX_A\tpin" if wide else ""
    if out.exists() or list(out.parent.glob(f"{out.stem}_best*.npz")):
        error("output already exists; choose a fresh prefix for this search")
    if not out.exists():
        out.write_text(
            "member\tnx\tny\tmass\tq1\tq2\tq3\tnewton\titers\tX\tsigma\t"
            "psi_minus\tR_e\tE19\tE_c\ttails\tminQ\tverdict"
            + ("\tlam_eta0" if args.stability else "")
            + extra_head + "\n")

    # the member holding J on its own grid, and its measured throat
    p1 = MatterCollocationProblem(
        eta0=sol.eta0, gamma=sol.gamma, radial_map=sol.radial_map,
        nx=nx, ny=ny, prescribe=("J", J_member))
    F0 = sol.eval_grid("f", p1.sx, p1.sy)
    W0 = sol.eval_grid("w", p1.sx, p1.sy)
    N0 = sol.eval_grid("N", p1.sx, p1.sy)
    zero = np.zeros_like(F0)
    u1, i1 = newton(p1.residual, p1.jacobian,
                    p1.pack(F0 - p1.f_bg, W0 - sol.omega_inf * p1.q,
                            N0, zero, zero, omega_inf=sol.omega_inf,
                            psi_minus=psim0), tol=TOL)
    F1, W1, N1, B1, P1 = (np.asarray(a) for a in p1.fields(u1))
    omega1, psim1 = p1.unpack(u1)[-2:]
    th = throat(p1.eta0, p1.map, p1.sx, p1.sy, p1.Dx, F1, N1, B1)
    pin_row = pin_held(args.pin, th)
    xi1 = float(p1.map.xi_of_eta(th["eta_throat"]))
    print(f"{name} ({nx}x{ny}, eta0 {sol.eta0:g}, gamma {sol.gamma:g}): "
          f"J-held {i1['res_scaled_inf']:.1e}; R_e {th['R_e']:.10f}, "
          f"R_A {th['R_A']:.10f}, R_pol {th['R_pol']:.10f}, "
          f"J {J_member:.6e}; pin {pin_row[0]}={pin_row[1]:.10g}; "
          f"score {score_key}; "
          f"optimize from ({', '.join(f'{v:g}' for v in x0)})",
          flush=True)
    if J0 != J_member:
        print(f"optimize at J {J0:g} (member holds {J_member:g})",
              flush=True)
    if args.free_J:
        print(f"J is a search knob in [{J_min:g}, {J_max:g}]",
              flush=True)

    grid = dataclasses.replace(sol.radial_map, eta0=1.0)
    d2 = (psim1 * sol.eta0 / math.pi) ** 2
    prev0 = {"F": F1, "W": sol.eta0 * W1, "N": N1, "B": B1, "PSI": P1,
             "omega": sol.eta0 * omega1, "psim": psim1,
             "sigma": sol.eta0, "xi_t": xi1}
    state = {"solved": {}, "nfev": 0,
             "best_clean": None, "best_screened": None, "best_frontier": None}
    grids = refinement_grids(nx, ny)
    checks_root = out.with_name(f"{out.stem}_resolution")
    print(f"new-best checks: {grids}; full refinement: {args.refine_best}; "
          "physical stability not assessed", flush=True)

    state["solved_j0"] = {}
    state["best_stable"] = None
    state["twins"] = {"direct": 0, "spun down": 0, "failed": 0}
    sx_all, _ = lobatto(nx)

    ctx = SearchContext(
        J0=J0,
        J_max=J_max,
        J_min=J_min,
        args=args,
        checks_root=checks_root,
        d2=d2,
        grid=grid,
        grids=grids,
        name=name,
        nx=nx,
        ny=ny,
        out=out,
        pin_row=pin_row,
        prev0=prev0,
        scales=scales,
        score_key=score_key,
        sol=sol,
        state=state,
        sx_all=sx_all,
        th=th,
        wide=wide,
    )

    if J0 == 0.0:
        prev0 = ctx.prev0 = continuation.static_seed(ctx)
        print("J = 0: start from the static drainhole seed", flush=True)

    # the walk-in: configurable mass increments, then shape in 0.3 steps. A leg that
    # stalls gets bisected toward the last solved point (the stiff-spin
    # straight line stalls marginally where the step-3 fan got through
    # on another route); capped so a true wall still stops the run
    x_pot = np.asarray(x0[:4], float)
    m0 = float(x_pot[0])
    chain = [np.array([m0 * k / args.walk_m_steps, 0, 0, 0])
             for k in range(args.walk_m_steps + 1)]
    n_q = max(1, int(math.ceil(max(abs(v) for v in x_pot[1:]) / 0.3))
              if np.any(x_pot[1:]) else 1)
    chain += [np.concatenate([[m0], x_pot[1:] * k / n_q])
              for k in range(1, n_q + 1)]

    row_v0, _ = evaluation.solve_at(ctx, np.zeros(4), prev0)
    x_v0 = ctx.x_v0 = row_v0.get(score_key)
    if x_v0 is None:
        print(f"classical (V = 0) FAILED: {row_v0['err']}", flush=True)
        return 1
    print(f"classical (V = 0): X {row_v0['X']:.8e}  "
          f"X_A {row_v0['X_A']:.8e}  E19 {row_v0['e19']:.1e}  "
          f"E_c {row_v0['e_c']:.1e}", flush=True)

    print(f"walk-in budgets: {args.walk_m_steps} mass increments, "
          f"{args.walk_max_iter} Newton iterations/solve, "
          f"{args.walk_max_splits} splits/leg; acceptance unchanged", flush=True)
    prev, row = continuation.walk(ctx, chain, prev0)
    if prev is None:
        return 1
    state["solved"][tuple(np.round(x0, 10))] = prev
    print(f"walk-in done: X {row['X']:.8e} at x0", flush=True)

    if args.stability:
        # the J = 0 branch: J down in thirds at V = 0, then the same
        # knob chain -- its cache seeds every twin solve in the loop
        jprev, why = continuation.spin_down(ctx, np.zeros(4), prev0, cap=6)
        if jprev is None:
            print(f"J walk failed ({why}); J = 0 from the static member",
                  flush=True)
            _, jprev = evaluation.solve_at(ctx, np.zeros(4), continuation.static_seed(ctx), jval=0.0)
            if jprev is None:
                print("J = 0 static seed FAILED", flush=True)
                return 1
        print(f"J = 0 base: sigma {jprev['sigma']:.8f}", flush=True)
        jprev, _ = continuation.walk(ctx, chain, jprev, jval=0.0, what="J0 walk-in")
        if jprev is None:
            return 1
        state["solved_j0"][tuple(np.round(x0, 10))] = jprev
        lam0, _ = continuation.stab_at(ctx, x0, tuple(np.round(x0, 10)), prev)
        print(f"J0 walk-in done: lam*eta0 at x0 "
              f"{lam0 if lam0 is not None else float('nan'):.6f}",
              flush=True)

    run_engine(ctx, x0)
    if args.refine_best == "final" and state["best_screened"] is not None:
        _, key, row = state["best_screened"]
        print("independently refining the screened finalist", flush=True)
        evaluation.check_best(ctx, key, row, "refine")
    slots = [("best_clean", "best resolution-validated background"),
             ("best_screened", "best screened (provisional)"),
             ("best_frontier", "search-grid frontier (provisional)")]
    if args.stability:
        slots.append(("best_stable", "best stable clean (lam = 0)"))
    for slot, label in slots:
        if state[slot] is None:
            print(f"{label}: none", flush=True)
        else:
            xb, key, row = state[slot]
            stab = (f"  lam {row['lam']:.4f}"
                    if row.get("lam") is not None else "")
            jbit = f"  J {key[4]:g}" if len(key) > 4 else ""
            print(f"{label}: {score_key} {xb:.8e} "
                  f"({100 * (xb / x_v0 - 1):+.1f} % "
                  f"vs V = 0) at m {key[0]:g} "
                  f"q ({', '.join(f'{v:g}' for v in key[1:4])}){jbit}  "
                  f"E19 {row['e19']:.1e}  E_c {row['e_c']:.1e}{stab}",
                  flush=True)
    if args.stability:
        tw = state["twins"]
        print(f"J = 0 twins: {tw['direct']} direct, {tw['spun down']} "
              f"spun down, {tw['failed']} failed", flush=True)
    if not args.no_save:
        for slot, _ in slots:
            if state[slot] is not None and slot not in ("best_clean", "best_screened"):
                print(f"saved {slot}: {artifacts.save_solution(ctx, slot)}", flush=True)
    if state["best_clean"] is None:
        print("NO VALIDATED FINAL RESULT; screened candidates remain provisional", flush=True)
        return 2
    return 0
