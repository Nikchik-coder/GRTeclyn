"""The confinement gate is the trustworthy 'matter dispersed' detector.

Regression guard: peak/total density is spatially blind (it can RISE under pump
injection while the lump sprays apart), so survival must be gated by the
mass-weighted confined fraction from confinement.dat.
"""

from __future__ import annotations

from grteclyn_wrapper.metrics.diagnostics.confinement import read_confinement_metrics
from grteclyn_wrapper.metrics.types.diagnostics import ConfinementMetrics
from grteclyn_wrapper.metrics.types.episode import EpisodeMetrics
from grteclyn_wrapper.metrics.score.survival import compute_survival_components
from grteclyn_wrapper.metrics.score.types import ScoringContext


def _ctx(confinement: ConfinementMetrics | None) -> ScoringContext:
    em = EpisodeMetrics(
        collapse=None,
        constraints=None,
        stability=None,
        comoving=None,
        ftl=None,
        termination_reason="x",
        confinement=confinement,
    )
    return ScoringContext(
        metrics=em, target_stop_time=16.0, domain_half_width=None, weights={}
    )


def test_confinement_absent_leaves_persistence_ungated() -> None:
    ctx = _ctx(None)
    compute_survival_components(ctx)
    assert ctx.components["confinement_retention"] == 1.0
    assert ctx.components["structural_persistence"] == 1.0


def _cm(initial: float | None, final: float) -> ConfinementMetrics:
    return ConfinementMetrics(
        n_frames=2,
        final_time=3.2,
        initial_rms_radius=4.78,
        final_rms_radius=7.04,
        max_rms_radius=7.04,
        initial_confined_frac=initial,
        final_confined_frac=final,
        min_confined_frac=final,
        spread_ratio=7.04 / 4.78,
        initial_total=208.0,
        final_total=1499.0,
    )


def test_dispersed_matter_gates_persistence_and_notes() -> None:
    # 83% -> 40% confined, spread almost doubled: clearly dispersed.
    # Rule 3: retention is judged against the run's OWN t=0 fraction.
    cm = _cm(0.83, 0.40)
    ctx = _ctx(cm)
    compute_survival_components(ctx)
    expected = 0.40 / 0.83
    assert abs(ctx.components["confinement_retention"] - expected) < 1e-9
    # density_retention is 1.0 (no constraints series), so persistence == retention.
    assert abs(ctx.components["structural_persistence"] - expected) < 1e-9
    # The absolute final fraction stays exposed for objectives that consume it.
    assert ctx.components["confinement_final_frac"] == 0.40
    assert any("DISPERSED" in n for n in ctx.notes)


def test_low_absolute_but_stable_family_is_not_dispersed() -> None:
    # A profile family that sits at 27% confinement by construction and HOLDS
    # it is perfectly stable -- the old absolute 0.5 threshold flagged exactly
    # this case DISPERSED (README rule 3, bondi 2026-08-21).
    cm = _cm(0.27, 0.27)
    ctx = _ctx(cm)
    compute_survival_components(ctx)
    assert ctx.components["confinement_retention"] == 1.0
    assert not any("DISPERSED" in n for n in ctx.notes)


def test_missing_initial_frac_falls_back_to_absolute() -> None:
    cm = _cm(None, 0.40)
    ctx = _ctx(cm)
    compute_survival_components(ctx)
    assert ctx.components["confinement_retention"] == 0.40
    assert any("DISPERSED" in n for n in ctx.notes)


def test_absolute_baseline_env_restores_old_behaviour(monkeypatch) -> None:
    monkeypatch.setenv("SCORE_CONFINEMENT_BASELINE", "absolute")
    cm = _cm(0.83, 0.40)
    ctx = _ctx(cm)
    compute_survival_components(ctx)
    assert ctx.components["confinement_retention"] == 0.40


def test_reader_round_trip(tmp_path) -> None:
    p = tmp_path / "confinement.dat"
    p.write_text(
        "# time  total_activity  peak_activity  rms_radius  confined_frac  "
        "bary_x  bary_y  bary_z  r_conf\n"
        "0.0  208.0  0.16  4.78  0.83  34.0  32.0  29.0  6.0\n"
        "3.2  1499.0  0.22  7.04  0.40  33.0  32.0  33.0  6.0\n",
        encoding="utf-8",
    )
    cm = read_confinement_metrics(p)
    assert cm is not None
    assert cm.n_frames == 2
    assert abs(cm.final_confined_frac - 0.40) < 1e-9
    assert abs(cm.spread_ratio - 7.04 / 4.78) < 1e-6
