"""Search scalar potentials at fixed throat size, with fixed or variable spin.

Input: a massless member (.json/.npz) and four potential knobs (optionally J).
Output: TSV evaluations, provisional NPZ candidates and independently refined
best_clean fields. X = |VIQ|/R_e, or X_A = |VIQ|/R_A for --pin area.
No stability certification is produced; --stability remains disabled.

    python -m grteclyn_wrapper.optimisation.commands.optimize_potential --help
"""
from __future__ import annotations
import argparse
from ..search.state import SCALES, STALL_OK


def positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("solution", help=".npz / .json path of a V = 0 member")
    ap.add_argument("--x0", default="0.3,0,0,0",
                    help="start (m, q1, q2, q3); the pure kink at the "
                         "mass this grid resolves (2026-10-29: not the "
                         "shape-scan best point)")
    ap.add_argument("--m-min", type=float, default=0.15,
                    help="smallest kink mass the grid resolves (m = 0.1 "
                         "misses the gate below 240x48, step-2 record)")
    ap.add_argument("--m-max", type=float, default=1.2)
    ap.add_argument("--q-min", type=float, default=-2.0,
                    help="lower bound on each of q1, q2, q3 (the step-3 "
                         "shape box, with room for a mild negative q3)")
    ap.add_argument("--q-max", type=float, default=8.0,
                    help="upper bound on each of q1, q2, q3 (the step-3 "
                         "shape box; D51's rejected basin sat at q3 ~ 17)")
    ap.add_argument("--m-step", type=float, default=SCALES[0],
                    help="the mass knob's scale (CMA step, simplex edge, "
                         "seed metric); m is physical, its stiffness is "
                         "m R_e, so a member with a larger throat takes "
                         "m, its bounds and this step scaled by 1/R_e")
    ap.add_argument("--engine", choices=["nm", "cma"], default="nm",
                    help="nm: scipy Nelder-Mead (one basin, the first "
                         "pass); cma: CMA-ES (population-based, escapes "
                         "a collapsed simplex, the better engine for "
                         "fresh starts)")
    ap.add_argument("--sigma0", type=float, default=1.0,
                    help="cma: global step multiplier on the per-knob "
                         "SCALES")
    ap.add_argument("--popsize", type=int, default=None,
                    help="cma population (default 4 + 3 ln n = 8)")
    ap.add_argument("--seed", type=int, default=7,
                    help="cma RNG seed (D21 used 7; a new member needs a "
                         "fresh seed or it replays D21's knob sequence)")
    ap.add_argument("--stability", action="store_true",
                    help="score stability too: every evaluation also "
                         "solves the knobs at J = 0 (from its own "
                         "continuation cache, else by spinning the "
                         "evaluation's solve down in J), runs the gated "
                         "radial screen on the twin and pays stab-weight * "
                         "lam*eta0 (decided 2026-10-28: one score in "
                         "the loop, two axes on the frontier)")
    ap.add_argument("--stab-weight", type=float, default=1.0,
                    help="price of the growth rate (classical lam*eta0 "
                         "is 1.18 against X ~ 2-3)")
    ap.add_argument("--stab-nx", type=int, default=150,
                    help="screen grid inside the loop (its internal "
                         "0.7-coarse match grid comes free)")
    ap.add_argument("--stall-ok", type=float, default=STALL_OK,
                    help="the bill solve's Newton stall cut (default: the "
                         "step-1 gate); the drainhole (gamma = -pi) floors "
                         "at 1e-11 to 2e-10 on stiff shapes, a line-search "
                         "stall bisection does not lift, and the identity "
                         "monitors gate every accepted solve regardless")
    ap.add_argument("--twin-stall-ok", type=float, default=1e-10,
                    help="the twin branch's Newton stall cut (the bill "
                         "solve keeps the step-1 gate 1e-11): stiff J = 0 "
                         "shapes stall at 1e-11 to 1e-10 at 150x30, and "
                         "the twin only feeds the radial screen, whose "
                         "two-grid match tolerates far larger background "
                         "errors")
    ap.add_argument("--stab-fail-pen", type=float, default=0.25,
                    help="penalty when the J = 0 twin solves by neither "
                         "route: stability uncertifiable, not "
                         "disqualifying")
    ap.add_argument("--maxfev", type=int, default=200)
    ap.add_argument("--walk-m-steps", type=positive_int, default=3,
                    help="mass increments from V=0 to x0 during initialization")
    ap.add_argument("--walk-max-splits", type=positive_int, default=6,
                    help="total bisection budget per initial continuation leg")
    ap.add_argument("--walk-max-iter", type=positive_int, default=12,
                    help="Newton iteration budget during initialization only; "
                         "acceptance thresholds and search solves are unchanged")
    ap.add_argument("--fatol", type=float, default=2e-5,
                    help="X tolerance of the simplex stop")
    ap.add_argument("--nx", type=int, default=None)
    ap.add_argument("--ny", type=int, default=None)
    ap.add_argument("--gpu", type=int, default=None, metavar="CARD")
    ap.add_argument("--jac-chunk", type=int, default=None)
    ap.add_argument("--J", type=float, default=None, dest="J_pin",
                    help="optimize at this J instead of the member's "
                         "(0 is the static drainhole of the same family); "
                         "with --free-J this is only the walk-in start")
    ap.add_argument("--pin", choices=["R_e", "area"], default="R_e",
                    help="throat size held by Newton (default R_e, the "
                         "Fig. 3e pin; area frees oblateness R_e/R_pol)")
    ap.add_argument("--free-J", action="store_true", dest="free_J",
                    help="add J as a fifth search knob at the pinned "
                         "throat size (default: J held)")
    ap.add_argument("--J-min", type=float, default=0.0, dest="J_min",
                    help="lower J bound when --free-J (default 0)")
    ap.add_argument("--J-max", type=float, default=None, dest="J_max",
                    help="upper J bound when --free-J (default: the "
                         "member's |J|; required on a static member)")
    ap.add_argument("--J-step", type=float, default=None, dest="J_step",
                    help="J knob scale when --free-J (default a tenth of "
                         "the J window)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-save", action="store_true",
                    help="skip the .npz of each best slot's solved fields "
                         "(written next to the TSV by default)")
    ap.add_argument("--save-accepted", action="store_true", default=True,
                    help="also write a .npz for every PASS and FRONTIER "
                         "evaluation (the family a later grid-check reads; "
                         "on by default)")
    ap.add_argument("--no-save-accepted", action="store_false",
                    dest="save_accepted")
    ap.add_argument("--refine-best", choices=("final", "each"), default="final",
                    help="screen every new best on finer grids; independently "
                         "re-solve only the finalist (default), or every new best")
    return ap


def main(argv: list[str] | None = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    from ..search.driver import run
    return run(args, error=ap.error)


if __name__ == "__main__":
    raise SystemExit(main())
