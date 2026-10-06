"""Parse GRTresna Ham/Mom convergence diagnostics, including the exit door.

The solver leaves its nonlinear loop by three different doors and only one of
them means the initial data is as good as it was asked to be (wrapper README
rule 8; ``research/bondi_dipole/check_solve_exit.py`` is the standalone twin of
the classification below):

``converged``
    both relative errors fell below ``NL_exit_tolerance`` with iterations to
    spare.
``stalled``
    the per-iteration improvement fell below ``NL_stall_tolerance``, so the
    loop gave up -- it can stop anywhere above the tolerance.
``cap``
    ``max_NL_iterations`` ran out.  GRTresna prints ``Converged!``
    unconditionally on this path, so the residual table is the only evidence.
    Meeting the tolerance exactly on the last permitted iteration is also
    classified ``cap``: that is met-by-luck, and the next rung of a ladder
    will not be so lucky.

The verdict is reconstructed from the two files that survive the wrapper's
cleanup (``Ham_and_Mom_errors.txt`` and the solve's own ``params.txt``); the
per-rank ``pout`` logs are deleted and are never parsed.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

#: Doors that certify the requested tolerance was genuinely met.
CONVERGED_DOOR = "converged"


def _read_solver_tolerances(
    params_path: Path,
) -> tuple[float | None, float | None, int | None]:
    """Read (NL_exit_tolerance, NL_stall_tolerance, max_NL_iterations)."""
    if not params_path.exists():
        return None, None, None
    text = params_path.read_text()

    def _num(key: str) -> str | None:
        hit = re.search(rf"^\s*{key}\s*=\s*(\S+)", text, re.M)
        return hit.group(1) if hit else None

    exit_tol = _num("NL_exit_tolerance")
    stall_tol = _num("NL_stall_tolerance")
    cap = _num("max_NL_iterations")
    return (
        float(exit_tol) if exit_tol else None,
        float(stall_tol) if stall_tol else None,
        int(cap) if cap else None,
    )


def _residual_rows(err_file: Path) -> list[tuple[int, float, float]]:
    rows: list[tuple[int, float, float]] = []
    for line in err_file.read_text().splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0].isdigit():
            try:
                rows.append((int(parts[0]), float(parts[1]), float(parts[2])))
            except ValueError:
                continue
    return rows


def classify_solve_exit(work_dir: Path) -> dict[str, object] | None:
    """Classify which door the nonlinear loop left by (README rule 8).

    Returns ``None`` when the residual table is missing or empty.  Otherwise a
    dict with ``exit_door`` in ``{"converged", "stalled", "cap", "unknown"}``,
    ``tolerance_met`` (bool or ``None`` when no tolerance was recorded), the
    final residuals, the tolerances the solve was actually given, and -- for a
    met tolerance -- ``tolerance_headroom`` (how far inside the request the
    final residual landed; ~1 means met by a whisker).
    """
    err_file = work_dir / "Ham_and_Mom_errors.txt"
    if not err_file.exists():
        return None
    rows = _residual_rows(err_file)
    if not rows:
        return None

    exit_tol, stall_tol, cap = _read_solver_tolerances(work_dir / "params.txt")
    last_iter, ham, mom = rows[-1]
    # Static (Pi=0) data: GRTresna skips the momentum solve and reports NaN;
    # the constraint is satisfied analytically.  Same leniency as
    # parse_convergence and the solver's own mom_ok predicate.
    if math.isfinite(ham) and not math.isfinite(mom):
        mom = 0.0

    result: dict[str, object] = {
        "iteration": last_iter,
        "ham_pct": ham,
        "mom_pct": mom,
        "nl_exit_tolerance": exit_tol,
        "nl_stall_tolerance": stall_tol,
        "max_nl_iterations": cap,
    }

    if (
        exit_tol is None
        or exit_tol <= 0.0
        or not (math.isfinite(ham) and math.isfinite(mom))
    ):
        # No absolute tolerance was requested (or residuals are non-finite):
        # there is nothing to certify against.
        result["exit_door"] = "unknown"
        result["tolerance_met"] = None
        return result

    met = ham < exit_tol and mom < exit_tol
    at_cap = cap is not None and last_iter >= cap
    if met and not at_cap:
        door = CONVERGED_DOOR
    elif at_cap:
        door = "cap"
    else:
        door = "stalled"
    result["exit_door"] = door
    result["tolerance_met"] = met
    worst = max(ham, mom)
    if met and worst > 0.0:
        result["tolerance_headroom"] = exit_tol / worst
    return result


def parse_convergence(work_dir: Path) -> dict[str, object] | None:
    """Read the final Ham/Mom errors from the GRTresna error file.

    The basic keys (``iteration``, ``ham_pct``, ``mom_pct``) are always
    present; when the solve's ``params.txt`` survives beside the table, the
    exit-door classification of :func:`classify_solve_exit` is merged in so
    every consumer (metadata.json, the convergence gate) sees which door the
    solve actually left by.
    """
    err_file = work_dir / "Ham_and_Mom_errors.txt"
    if not err_file.exists():
        return None
    lines = err_file.read_text().strip().splitlines()
    if len(lines) < 2:
        return None
    last = lines[-1].split()
    if len(last) < 3:
        return None
    try:
        ham_pct = float(last[1])
        mom_pct = float(last[2])
    except (ValueError, IndexError):
        return None
    if math.isfinite(ham_pct) and not math.isfinite(mom_pct):
        mom_pct = 0.0
    result: dict[str, object] = {
        "iteration": int(last[0]),
        "ham_pct": ham_pct,
        "mom_pct": mom_pct,
    }
    # Merge the exit-door verdict only when the solve's own params.txt is
    # there to judge against; without it there is nothing to certify and
    # legacy fixtures keep the bare three-key shape.
    door = (
        classify_solve_exit(work_dir)
        if (work_dir / "params.txt").exists()
        else None
    )
    if door is not None:
        for key in (
            "exit_door",
            "tolerance_met",
            "tolerance_headroom",
            "nl_exit_tolerance",
            "nl_stall_tolerance",
            "max_nl_iterations",
        ):
            if key in door:
                result[key] = door[key]
    return result
