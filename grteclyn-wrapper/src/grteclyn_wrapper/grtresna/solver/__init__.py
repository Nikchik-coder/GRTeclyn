"""GRTresna elliptic solver orchestration."""

from .config import (
    GRTresnaConfig,
    apply_exotic_safe_solver,
    aligned_solve_enforced,
    config_has_exotic_lump,
    REQUIRE_ALIGNED_SOLVE_ENV,
    solve_grid_alignment_error,
)
from .convergence import CONVERGED_DOOR, classify_solve_exit, parse_convergence
from .params import _lump_lines, write_grtresna_params
from .runner import solve

__all__ = [
    "GRTresnaConfig",
    "apply_exotic_safe_solver",
    "aligned_solve_enforced",
    "classify_solve_exit",
    "config_has_exotic_lump",
    "CONVERGED_DOOR",
    "parse_convergence",
    "REQUIRE_ALIGNED_SOLVE_ENV",
    "solve",
    "solve_grid_alignment_error",
    "write_grtresna_params",
    "_lump_lines",
]
