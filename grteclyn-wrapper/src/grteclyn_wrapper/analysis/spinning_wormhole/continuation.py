"""Solve one background; step families in J (SpinningSolver.md P2-P3).

``solve_point`` is the unit step: seed from the O(J^2) member (or a given
Solution / unknown vector), Newton on (f, omega), the linear N solve, then
observables and identity gates attached.  Families are labelled by J, not
omega_{-inf}: omega_0 turns over along a family while J grows monotonically
to the extremal end, so prescribing J steps straight past that fold
(section 4); J's own monotonicity is checked by the driver, never assumed.
"""

from __future__ import annotations

import math

import numpy as np

from .backgrounds import slow_rotation_omega, slow_rotation_solution
from .equations import CollocationProblem
from .newton import newton
from .observables import identity_gates, observables
from .solution import Solution
from .spectral import ArctanMap, cheb_eval

__all__ = ["solve_point", "seed_from_slowspin"]


def seed_from_slowspin(problem: CollocationProblem, J: float,
                       n_cheb: int = 96):
    """The O(J^2) member as a Newton start: df = J^2 (A + B P2(y)) with
    P2 = (3y + 1)/4, dw = 0 (omega = J w1 IS omega_inf q by construction),
    omega_inf = J w1(-inf)."""
    sol = slow_rotation_solution(problem.eta0, problem.gamma, n_cheb)
    x = problem.map.xi_of_eta(
        np.concatenate([[math.inf], problem.eta_i[:, 0], [-math.inf]]))
    if problem.map.name == "arctan":
        x = problem.sx                   # exact, not just the map round trip
    A = cheb_eval(sol["s"], sol["A"], x)
    B = cheb_eval(sol["s"], sol["B"], x)
    p2 = (3.0 * problem.sy + 1.0) / 4.0
    df = J * J * (A[:, None] + np.outer(B, p2))
    dw = np.zeros_like(df)
    w1_inf = float(slow_rotation_omega(problem.eta0, problem.gamma,
                                       np.array([-0.5 * math.pi]))[0])
    return df, dw, J * w1_inf


def solve_point(*, eta0: float, gamma: float, J: float | None = None,
                omega_inf: float | None = None, nx: int = 64, ny: int = 16,
                radial_map=None, tol: float = 1e-12, u0=None,
                problem: CollocationProblem | None = None,
                with_observables: bool = True, verbose: bool = False):
    """One converged Solution (or a diagnosable failure).

    Exactly one of J (the bordered system) and omega_inf must be given.
    ``u0`` reuses a Newton start (continuation); default is the O(J^2) seed.
    Returns (solution, info); info carries the Newton record and, on
    success, the identity gates.
    """
    if (J is None) == (omega_inf is None):
        raise ValueError("prescribe exactly one of J and omega_inf")
    prescribe = ("J", J) if J is not None else ("omega_inf", omega_inf)
    if problem is None:
        problem = CollocationProblem(eta0=eta0, gamma=gamma,
                                     radial_map=radial_map, nx=nx, ny=ny,
                                     prescribe=prescribe)
    else:
        if (problem.mode, problem.value) != prescribe:
            raise ValueError("problem/prescribe mismatch")
    if u0 is None:
        w1_inf = float(slow_rotation_omega(eta0, gamma,
                                           np.array([-0.5 * math.pi]))[0])
        J_seed = J if J is not None else omega_inf / w1_inf
        df, dw, winf0 = seed_from_slowspin(problem, J_seed)
        u0 = problem.pack(df, dw, winf0 if J is not None else None)
    u, info = newton(problem.residual, problem.jacobian, u0, tol=tol,
                     verbose=verbose)
    if not info["converged"]:
        return None, info
    F, W = problem.fields(u)
    F, W = np.asarray(F), np.asarray(W)
    _, _, winf = problem.unpack(u)
    # N and D^2 from the constraint sector (eqs 13 + 19), NOT the printed
    # eq. 12: extremal Kerr satisfies 10, 11, 13, 19 exactly but violates
    # the published eq. 12 at 1e-2 (2026-10-12, derive_xy_equations.py
    # --stage kerr), and the elliptic eq.-12 N leaves a J^4-sized
    # constraint violation that no resolution removes.
    Nf, d2_solved, n_info = problem.solve_N_constrained(F, W)
    m = problem.map
    sol = Solution(
        eta0=eta0, gamma=gamma, omega_inf=float(winf),
        map_name=m.name,
        map_params={k: v for k, v in vars(m).items()
                    if k not in ("eta0", "name")},
        F=F, W=W, N=Nf,
        meta={"newton": {k: info[k] for k in
                         ("iters", "res_scaled_inf", "jacobian_evals")},
              "n_solve": n_info,
              "prescribed": {prescribe[0]: prescribe[1]},
              "nx": problem.nx, "ny": problem.ny},
    )
    if with_observables:
        sol.gates = identity_gates(sol)
        sol.observables = observables(sol)
    info = dict(info)
    info["u"] = u
    return sol, info


def _regrid(u, p_old, p_new):
    """Spectral re-seed of an unknown vector onto a finer grid."""
    df, dw, winf = p_old.unpack(u)
    def lift(a):
        rows = cheb_eval(p_old.sx, a, p_new.sx)
        return cheb_eval(p_old.sy, rows.T, p_new.sy).T
    return p_new.pack(lift(df), lift(dw),
                      winf if p_new.mode == "J" else None)


def run_family(*, eta0: float, gamma: float, j_start: float,
               nx: int = 64, ny: int = 16, radial_map=None,
               ve_stop: float = 0.9, j_stop: float | None = None,
               du0: float = 0.08, du_min: float = 1e-4, du_max: float = 0.5,
               tol: float = 1e-12, tail_gate: float = 1e-11,
               nx_max: int = 192, max_steps: int = 500,
               out_dir=None, name: str = "family", log=print,
               stop_fn=None, seed_npz=None) -> dict:
    """Continuation in log(J/eta0^2) along one fixed-gamma family
    (SpinningSolver.md section 4).

    J is the label (it grows monotonically to the extremal end, while
    omega_inf turns over); the predictor is a secant through the last two
    unknown vectors; the step grows x1.5 after <= 3 Newton iterations and
    halves after >= 7 or a failure; above the tail gate the grid grows
    x1.5 and the point is re-solved.  Every converged step is saved
    (Solution .npz + .json) plus one TSV row, so any J can be re-seeded
    or re-tabled without re-running the family.
    """
    from pathlib import Path

    out = Path(out_dir) if out_dir is not None else None
    if out is not None:
        out.mkdir(parents=True, exist_ok=True)
    problem = CollocationProblem(eta0=eta0, gamma=gamma,
                                 radial_map=radial_map, nx=nx, ny=ny,
                                 prescribe=("J", j_start))
    lj = math.log(j_start / eta0**2)
    du = du0
    state = []                     # (lj, u) on the CURRENT grid
    if seed_npz is not None:
        # Exact restart: a saved J-prescribed Solution becomes the first
        # state entry, and stepping continues one du beyond its J.
        from .solution import Solution
        s0 = Solution.load(seed_npz)
        if s0.F.shape != (nx + 1, ny + 1):
            raise ValueError(
                f"seed grid {s0.F.shape} != requested {(nx + 1, ny + 1)}")
        lj = math.log(s0.observables["J"] / eta0**2)
        df = s0.F - problem.f_bg
        dw = s0.W - s0.omega_inf * problem.q
        state = [(lj, problem.pack(df, dw, s0.omega_inf))]
        lj += du0
    rows = []
    reason = "max_steps"
    slope_sign = None
    tsv = (out / f"{name}.tsv").open("w") if out is not None else None
    if tsv:
        tsv.write("step\tJ\tomega_inf\tv_e\tD\tM_ADM\tR_eq\tR_pol\t"
                  "eta_throat\tEc\tD2sp\tJsp\tsmarr\ttails\tnx\tny\titers\n")
    step = 0
    while step < max_steps:
        J = eta0**2 * math.exp(lj)
        problem.set_prescribed(J)
        if len(state) >= 2:
            (l0, u0v), (l1, u1v) = state[-2], state[-1]
            u0 = u1v + (u1v - u0v) * ((lj - l1) / max(l1 - l0, 1e-300))
        elif state:
            u0 = state[-1][1]
        else:
            df, dw, winf0 = seed_from_slowspin(problem, J)
            u0 = problem.pack(df, dw, winf0)
        sol, info = solve_point(eta0=eta0, gamma=gamma, J=J,
                                problem=problem, u0=u0, tol=tol)
        if sol is None:
            du *= 0.5
            if du < du_min:
                reason = "step collapsed"
                break
            lj = state[-1][0] + du if state else math.log(j_start / eta0**2)
            log(f"[{name}] J {J:.5g} failed ({info.get('reason')}); "
                f"du -> {du:.3g}")
            continue
        if sol.gates["tail_max"] > tail_gate and problem.nx < nx_max:
            nx2 = min(int(math.ceil(problem.nx * 1.5 / 2)) * 2, nx_max)
            ny2 = int(math.ceil(problem.ny * 1.5 / 2)) * 2
            log(f"[{name}] tails {sol.gates['tail_max']:.1e} at J {J:.5g}: "
                f"grid {problem.nx}x{problem.ny} -> {nx2}x{ny2}")
            p_new = CollocationProblem(eta0=eta0, gamma=gamma,
                                       radial_map=radial_map, nx=nx2,
                                       ny=ny2, prescribe=("J", J))
            state = [(l, _regrid(u, problem, p_new)) for l, u in state]
            problem = p_new
            continue                      # re-solve the same J on the new grid
        o, g = sol.observables, sol.gates
        row = {"step": step, "J": J, "omega_inf": sol.omega_inf,
               "v_e": o["v_e"], "D": o["D"], "M_ADM": o["M_ADM"],
               "R_eq": o["R_eq"], "R_pol": o["R_pol"],
               "eta_throat": o["eta_throat"], "nx": problem.nx,
               "ny": problem.ny, "iters": info["iters"], "gates": g}
        rows.append(row)
        if tsv:
            tsv.write("\t".join(str(v) for v in (
                step, f"{J:.10g}", f"{sol.omega_inf:.10g}",
                f"{o['v_e']:.8g}", f"{o['D']:.10g}", f"{o['M_ADM']:.8g}",
                f"{o['R_eq']:.8g}", f"{o['R_pol']:.8g}",
                f"{o['eta_throat']:.6g}", f"{g['Ec_rel']:.3g}",
                f"{g['D2_spread']:.3g}", f"{g['J_spread']:.3g}",
                f"{g['smarr_rel']:.3g}", f"{g['tail_max']:.3g}",
                problem.nx, problem.ny, info["iters"])) + "\n")
            tsv.flush()
        if out is not None:
            sol.save(out / f"{name}_{step:04d}")
        if len(rows) >= 2:
            dw_dj = (rows[-1]["omega_inf"] - rows[-2]["omega_inf"]) \
                / (rows[-1]["J"] - rows[-2]["J"])
            if slope_sign is not None and dw_dj * slope_sign < 0:
                log(f"[{name}] omega_inf turnover between "
                    f"J {rows[-2]['J']:.5g} and {rows[-1]['J']:.5g}")
                slope_sign = dw_dj
            elif abs(dw_dj) > 0:
                slope_sign = math.copysign(1.0, dw_dj)
        log(f"[{name}] {step:3d}: J {J:.6g} w_inf {sol.omega_inf:.6g} "
            f"v_e {o['v_e']:.4f} D {o['D']:.6f} M {o['M_ADM']:.5f} "
            f"({problem.nx}x{problem.ny}, {info['iters']} it, "
            f"tails {g['tail_max']:.1e})")
        state.append((lj, np.asarray(info["u"])))
        state = state[-2:]
        if o["v_e"] >= ve_stop:
            reason = f"v_e {o['v_e']:.4f} >= {ve_stop}"
            break
        if stop_fn is not None and stop_fn(rows):
            reason = "stop_fn"
            break
        if j_stop is not None and J >= j_stop:
            reason = f"J {J:.5g} >= {j_stop}"
            break
        du = min(du * 1.5, du_max) if info["iters"] <= 3 else (
            du * 0.5 if info["iters"] >= 7 else du)
        lj += du
        step += 1
    if tsv:
        tsv.close()
    log(f"[{name}] stopped: {reason} ({len(rows)} converged points)")
    return {"rows": rows, "reason": reason, "name": name,
            "nx": problem.nx, "ny": problem.ny}


def solve_at_omega_inf(*, eta0: float, gamma: float, omega_inf: float,
                       near, tol: float = 1e-12):
    """One omega_inf-prescribed solve seeded from a nearby bordered
    Solution ``near`` (anchor runs: each omega_inf can have TWO solutions,
    one per branch, so the seed picks which one)."""
    problem = CollocationProblem(
        eta0=eta0, gamma=gamma, nx=near.nx, ny=near.ny,
        prescribe=("omega_inf", omega_inf))
    df = near.F - problem.f_bg
    dw = near.W - omega_inf * problem.q
    u0 = problem.pack(df, dw)
    return solve_point(eta0=eta0, gamma=gamma, omega_inf=omega_inf,
                       problem=problem, u0=u0, tol=tol)
