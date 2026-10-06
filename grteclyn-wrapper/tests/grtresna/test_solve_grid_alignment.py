"""Rule 1: the solve grid must land exactly on the evolution grid.

The solved metric is copied onto the gridinit grid piecewise-constant with
last-source-wins while the matter is repainted analytically, so any spacing
mismatch (or solve refinement) displaces the metric by a fraction of a cell
and every lump is born off the centre of its own well.  These tests pin the
alignment rail and the campaign-CLI wiring that steers into the aligned copy.
"""

from __future__ import annotations

import argparse

from grteclyn_wrapper.grtresna.domain.export import GridinitExportSpec
from grteclyn_wrapper.grtresna.solver import (
    GRTresnaConfig,
    aligned_solve_enforced,
    solve_grid_alignment_error,
)


def _aligned_cfg() -> GRTresnaConfig:
    # The bondi-standard solve: L=128 box at 256^3 (dx 0.5), no refinement,
    # exported over the L=64 evolution box at 128^3 (dx 0.5).
    return GRTresnaConfig(
        N=(256, 256, 256),
        L=128.0,
        max_level=0,
        gridinit_nx=128,
        gridinit_ny=128,
        gridinit_nz=128,
        gridinit_export=GridinitExportSpec(
            nx=128,
            ny=128,
            nz=128,
            lx=64.0,
            ly=64.0,
            lz=64.0,
            target_center=(32.0, 32.0, 32.0),
            source_origin=(32.0, 32.0, 32.0),
        ),
    )


def test_aligned_solve_passes() -> None:
    assert solve_grid_alignment_error(_aligned_cfg()) is None


def test_coarse_solve_cell_is_rejected() -> None:
    # The pre-2026-08-26 search default: 64^3 over L=128 -> solve dx 2.0
    # against a gridinit dx of 0.5.
    cfg = _aligned_cfg()
    cfg.N = (64, 64, 64)
    error = solve_grid_alignment_error(cfg)
    assert error is not None
    assert "axis x" in error and "dx=2" in error


def test_refined_solve_is_rejected() -> None:
    cfg = _aligned_cfg()
    cfg.max_level = 3
    error = solve_grid_alignment_error(cfg)
    assert error is not None
    assert "max_level=3" in error


def test_no_export_falls_back_to_gridinit_over_solve_box() -> None:
    cfg = _aligned_cfg()
    cfg.gridinit_export = None
    # gridinit 128^3 over the solve box L=128 -> dx 1.0 vs solve dx 0.5.
    error = solve_grid_alignment_error(cfg)
    assert error is not None
    cfg.N = (128, 128, 128)
    assert solve_grid_alignment_error(cfg) is None


def test_enforcement_env(monkeypatch) -> None:
    monkeypatch.delenv("GRTRESNA_REQUIRE_ALIGNED_SOLVE", raising=False)
    assert not aligned_solve_enforced()
    monkeypatch.setenv("GRTRESNA_REQUIRE_ALIGNED_SOLVE", "1")
    assert aligned_solve_enforced()


def _search_args(**overrides) -> argparse.Namespace:
    ns = argparse.Namespace(
        grtresna=True,
        grtresna_lumps=5,
        grtresna_ansatz="shell",
        grtresna_shell_profile="compact",
        pin_dimension=[],
        grtresna_full_z=True,
        grtresna_evolution_l_full=64.0,
        grtresna_evolution_n_full=128,
        grtresna_domain_l=128.0,
        grtresna_domain_nx=256,
        grtresna_domain_ny=256,
        grtresna_domain_nz=None,
        grtresna_gridinit_nx=128,
        grtresna_gridinit_ny=128,
        grtresna_gridinit_nz=128,
        grtresna_max_level=0,
    )
    for key, value in overrides.items():
        setattr(ns, key, value)
    return ns


def test_context_maximal_slicing_flag_reaches_base_config(monkeypatch) -> None:
    monkeypatch.delenv("GRTRESNA_REQUIRE_ALIGNED_SOLVE", raising=False)
    from grteclyn_wrapper.cli.grtresna_context import build_grtresna_search_context

    context = build_grtresna_search_context(
        _search_args(grtresna_maximal_slicing=True, grtresna_require_converged=True),
        {},
    )
    cfg = context.grtresna_config
    assert cfg is not None
    # One construction method for every candidate: K=0 with the exotic-safe
    # relaxation, identical to what a phantom-bearing candidate would get.
    assert cfg.maximal_slicing is True
    assert cfg.psi_relaxation == 0.6
    assert cfg.psi_floor == 0.1
    assert cfg.coefficient_average_type == "arithmetic"
    assert context.grtresna_convergence_config is not None
    assert context.grtresna_convergence_config.require_converged is True
    # And the aligned-grid defaults really are aligned.
    assert solve_grid_alignment_error(cfg) is None


def test_context_misaligned_raises_when_enforced(monkeypatch) -> None:
    monkeypatch.setenv("GRTRESNA_REQUIRE_ALIGNED_SOLVE", "1")
    from grteclyn_wrapper.cli.grtresna_context import build_grtresna_search_context

    args = _search_args(
        grtresna_domain_nx=64, grtresna_domain_ny=64, grtresna_max_level=3
    )
    try:
        build_grtresna_search_context(args, {})
    except ValueError as exc:
        assert "misaligned" in str(exc)
    else:
        raise AssertionError("misaligned solve grid was not refused")


def test_context_misaligned_only_warns_when_not_enforced(monkeypatch) -> None:
    monkeypatch.delenv("GRTRESNA_REQUIRE_ALIGNED_SOLVE", raising=False)
    from grteclyn_wrapper.cli.grtresna_context import build_grtresna_search_context

    args = _search_args(
        grtresna_domain_nx=64, grtresna_domain_ny=64, grtresna_max_level=3
    )
    context = build_grtresna_search_context(args, {})
    assert context.grtresna_config is not None
