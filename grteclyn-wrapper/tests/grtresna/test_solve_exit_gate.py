"""Rule 8: the solve's exit door is a verdict, not a label.

GRTresna prints "Converged!" unconditionally -- including after a stall or an
exhausted iteration cap -- so the wrapper reconstructs the exit door from the
two files that survive cleanup (Ham_and_Mom_errors.txt + params.txt) and gates
on it.  These tests pin the classification and the gate.
"""

from __future__ import annotations

from pathlib import Path

from grteclyn_wrapper.grtresna.solver import classify_solve_exit, parse_convergence
from grteclyn_wrapper.search.grtresna_convergence_gate import (
    GRTresnaConvergenceConfig,
    convergence_rejection_reason,
)


def _work_dir(
    tmp_path: Path,
    rows: list[tuple[int, float, float]],
    *,
    exit_tol: float | None = 0.1,
    stall_tol: float | None = 0.002,
    cap: int | None = 50,
) -> Path:
    lines = ["# iteration Ham Mom"]
    lines += [f"{i} {h} {m}" for i, h, m in rows]
    (tmp_path / "Ham_and_Mom_errors.txt").write_text("\n".join(lines) + "\n")
    params = []
    if exit_tol is not None:
        params.append(f"NL_exit_tolerance = {exit_tol}")
    if stall_tol is not None:
        params.append(f"NL_stall_tolerance = {stall_tol}")
    if cap is not None:
        params.append(f"max_NL_iterations = {cap}")
    (tmp_path / "params.txt").write_text("\n".join(params) + "\n")
    return tmp_path


def test_converged_door(tmp_path: Path) -> None:
    wd = _work_dir(tmp_path, [(1, 12.5, 8.0), (12, 0.05, 0.04)])
    result = classify_solve_exit(wd)
    assert result is not None
    assert result["exit_door"] == "converged"
    assert result["tolerance_met"] is True
    assert result["tolerance_headroom"] == 0.1 / 0.05


def test_stalled_door_is_not_converged(tmp_path: Path) -> None:
    # Final residual ABOVE the requested 0.1% with iterations to spare: the
    # loop gave up (stall), whatever the solver printed.
    wd = _work_dir(tmp_path, [(1, 12.5, 8.0), (9, 0.8, 0.3)])
    result = classify_solve_exit(wd)
    assert result is not None
    assert result["exit_door"] == "stalled"
    assert result["tolerance_met"] is False


def test_cap_door(tmp_path: Path) -> None:
    wd = _work_dir(tmp_path, [(1, 12.5, 8.0), (50, 0.8, 0.3)], cap=50)
    result = classify_solve_exit(wd)
    assert result is not None
    assert result["exit_door"] == "cap"


def test_met_on_last_permitted_iteration_is_cap(tmp_path: Path) -> None:
    # Met-by-luck: the tolerance fell only on the final permitted iteration.
    # The next rung of a ladder will not be so lucky (check_solve_exit.py).
    wd = _work_dir(tmp_path, [(1, 12.5, 8.0), (50, 0.05, 0.04)], cap=50)
    result = classify_solve_exit(wd)
    assert result is not None
    assert result["exit_door"] == "cap"
    assert result["tolerance_met"] is True


def test_nan_mom_is_lenient(tmp_path: Path) -> None:
    # Static (Pi=0) data: the momentum solve is skipped and reports NaN; the
    # constraint is satisfied analytically.
    wd = _work_dir(tmp_path, [(1, 12.5, 8.0), (12, 0.05, float("nan"))])
    result = classify_solve_exit(wd)
    assert result is not None
    assert result["mom_pct"] == 0.0
    assert result["exit_door"] == "converged"


def test_no_tolerance_recorded_is_unknown(tmp_path: Path) -> None:
    wd = _work_dir(tmp_path, [(1, 12.5, 8.0), (12, 0.05, 0.04)], exit_tol=None)
    result = classify_solve_exit(wd)
    assert result is not None
    assert result["exit_door"] == "unknown"
    assert result["tolerance_met"] is None


def test_parse_convergence_merges_door(tmp_path: Path) -> None:
    wd = _work_dir(tmp_path, [(1, 12.5, 8.0), (9, 0.8, 0.3)])
    convergence = parse_convergence(wd)
    assert convergence is not None
    assert convergence["iteration"] == 9
    assert convergence["ham_pct"] == 0.8
    assert convergence["exit_door"] == "stalled"
    assert convergence["nl_exit_tolerance"] == 0.1


def test_gate_rejects_wrong_door_only_when_required() -> None:
    stalled = {
        "iteration": 9,
        "ham_pct": 0.8,
        "mom_pct": 0.3,
        "exit_door": "stalled",
        "nl_exit_tolerance": 0.1,
    }
    lax = GRTresnaConvergenceConfig(max_ham_pct=5.0, max_mom_pct=5.0)
    strict = GRTresnaConvergenceConfig(
        max_ham_pct=5.0, max_mom_pct=5.0, require_converged=True
    )
    # Residuals are inside the 5% acceptance band, so the lax gate passes.
    assert convergence_rejection_reason(stalled, config=lax) is None
    reason = convergence_rejection_reason(stalled, config=strict)
    assert reason is not None and "stalled" in reason

    converged = dict(stalled, exit_door="converged", ham_pct=0.05, mom_pct=0.04)
    assert convergence_rejection_reason(converged, config=strict) is None


def test_gate_tolerates_legacy_records_without_door() -> None:
    # Old metadata.json entries carry only iteration/ham/mom; require_converged
    # must not reject them retroactively.
    legacy = {"iteration": 12, "ham_pct": 0.05, "mom_pct": 0.04}
    strict = GRTresnaConvergenceConfig(require_converged=True)
    assert convergence_rejection_reason(legacy, config=strict) is None
