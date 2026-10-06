from __future__ import annotations

import math
import os

from .types import ScoringContext

# Below this peak matter energy density there is effectively no structure to
# persist, so the structural-persistence ratio is left undefined (survival is
# not persistence-gated) rather than dividing by numerical noise.
_RHO_PERSISTENCE_FLOOR: float = 1.0e-8

# The trajectory pump injects energy, so some rho growth is physical.  Only
# penalise when final peak rho exceeds initial by more than this factor.
_RHO_GROWTH_TOLERANCE: float = 3.0

# Baseline for the confinement-retention gate (README rule 3).  "t0" judges
# dispersal against the run's OWN initial confined fraction; "absolute" is the
# pre-2026-08-26 behaviour (raw final fraction vs a fixed threshold), kept
# reachable for A/B against old campaigns.  A t=0 fraction below this floor
# means the profile never was confined and the ratio would divide noise.
_CONFINEMENT_BASELINE_ENV = "SCORE_CONFINEMENT_BASELINE"
_CONFINEMENT_INITIAL_FLOOR: float = 1.0e-6


def _confinement_baseline_is_t0() -> bool:
    return os.environ.get(_CONFINEMENT_BASELINE_ENV, "t0").lower() != "absolute"


def compute_survival_components(ctx: ScoringContext) -> None:
    metrics = ctx.metrics
    components = ctx.components
    notes = ctx.notes
    final_time = ctx.final_time

    # Numerical survival: did the integrator reach the configured stop time
    # without crashing?  This is a *necessary* condition but NOT sufficient --
    # empty/dissipated space is the easiest thing to march to the end, so on its
    # own this perversely rewards junk (a candidate whose matter completely
    # disperses still scores 1.0).  We therefore gate it by structural
    # persistence below.
    if ctx.target_stop_time and ctx.target_stop_time > 0 and final_time is not None:
        numerical_survival = min(final_time / ctx.target_stop_time, 1.0)
    elif final_time is not None:
        numerical_survival = 1.0
    else:
        numerical_survival = 0.0
        notes.append("no time-series diagnostics were found")

    # Structural persistence has two independent failure modes, both of which
    # must cost the candidate its "survived" credit:
    #
    #   1. DENSITY RETENTION -- how stable the peak matter energy density is
    #      between the start and end of the run.  We compare the final peak
    #      rho to the *initial* peak rho rather than the all-time maximum.
    #      This catches BOTH failure modes:
    #        - Dispersion: final << initial  (matter spreads/dissipates)
    #        - Collapse / constraint blow-up: final >> initial  (runaway
    #          growth of rho from numerical noise or gravitational collapse)
    #      The trajectory pump injects energy so modest growth (up to
    #      ``_RHO_GROWTH_TOLERANCE`` x) is tolerated.  Beyond that the
    #      retention drops as tolerance / ratio.
    #
    #   2. MORPHOLOGICAL COHERENCE -- whether the matter that *is* still dense
    #      remains a single coherent structure or has fragmented into several
    #      lobes.  Density retention alone is blind to this: a coherent bubble
    #      that shatters into two equally-dense counter-rotating lobes keeps its
    #      peak density (retention ~1.0) yet is no longer the localized warp
    #      structure we are searching for.  ``structure_coherence`` (computed on
    #      the evolved matter slice) is ~1/k for a structure split into k
    #      comparable pieces, so it gates the survived-credit accordingly.
    #
    # Persistence is the product of the two and defaults to 1.0 when the
    # underlying series/slice is unavailable, leaving survival un-gated.
    density_retention = 1.0
    if metrics.constraints is not None:
        initial_rho = metrics.constraints.initial_peak_rho_required
        final_rho = metrics.constraints.final_peak_rho_required
        if (
            initial_rho is not None
            and final_rho is not None
            and initial_rho > _RHO_PERSISTENCE_FLOOR
        ):
            ratio = final_rho / initial_rho
            if not math.isfinite(ratio) or ratio <= 0.0:
                density_retention = 0.0
            elif ratio <= 1.0:
                # Dispersion: rho dropped.
                density_retention = float(ratio)
            elif ratio <= _RHO_GROWTH_TOLERANCE:
                # Modest growth within tolerance (pump-driven).
                density_retention = 1.0
            else:
                # Runaway growth: constraint blow-up or collapse.
                density_retention = float(_RHO_GROWTH_TOLERANCE / ratio)
            density_retention = min(max(density_retention, 0.0), 1.0)
        else:
            notes.append("matter-density time series unavailable; survival not density-gated")

    coherence = 1.0
    if (
        metrics.general_ftl_evolved is not None
        and metrics.general_ftl_evolved.structure_coherence is not None
    ):
        raw_coherence = metrics.general_ftl_evolved.structure_coherence
        if not math.isfinite(raw_coherence):
            raw_coherence = 0.0
            notes.append("structure_coherence was NaN/inf; treating as fully fragmented")
        coherence = float(min(max(raw_coherence, 0.0), 1.0))
        if coherence < 0.95:
            notes.append(
                f"matter fragmented into ~{round(1.0 / max(coherence, 1e-6))} lobes "
                f"(coherence={coherence:.2f}); survival/shaping rewards gated down"
            )

    # CONFINEMENT RETENTION -- the trustworthy "matter dispersed / flew away"
    # gate.  density_retention (peak rho) is spatially blind: a lump can spray
    # into a ragged halo while peak/total density RISES under pump injection, so
    # peak-based persistence reported "good" while the frames showed the matter
    # blowing apart.  confined_frac is the mass fraction still inside the lump
    # scale (4*well_width of the true matter barycentre); it falls precisely when
    # the matter de-localizes, regardless of peak.  Defaults to 1.0 (un-gated)
    # when confinement.dat is unavailable, so older episodes are unaffected.
    #
    # Rule 3 (wrapper README / bondi 2026-08-21): retention is judged against
    # the run's OWN t=0 confined fraction, not an absolute threshold.  A star
    # family that sits at 27% confinement by construction is perfectly stable
    # at 27%; the old absolute gate flagged it DISPERSED while letting a
    # 99%->55% collapse pass untouched.  Falls back to the absolute fraction
    # when t=0 is unavailable (older confinement.dat) or itself ~0, and the
    # old behaviour stays reachable via SCORE_CONFINEMENT_BASELINE=absolute.
    confinement_retention = 1.0
    confinement = metrics.confinement
    if confinement is not None and confinement.final_confined_frac is not None:
        final_frac = float(min(max(confinement.final_confined_frac, 0.0), 1.0))
        initial_frac = confinement.initial_confined_frac
        if (
            _confinement_baseline_is_t0()
            and initial_frac is not None
            and initial_frac > _CONFINEMENT_INITIAL_FLOOR
        ):
            confinement_retention = float(
                min(max(final_frac / float(initial_frac), 0.0), 1.0)
            )
        else:
            confinement_retention = final_frac
        components["confinement_final_frac"] = final_frac
        if confinement.spread_ratio is not None:
            components["confinement_spread_ratio"] = float(confinement.spread_ratio)
        if confinement.min_confined_frac is not None:
            components["confinement_min_frac"] = float(
                min(max(confinement.min_confined_frac, 0.0), 1.0)
            )

    structural_persistence = density_retention * coherence * confinement_retention

    components["numerical_survival"] = numerical_survival
    components["confinement_retention"] = confinement_retention
    components["structural_persistence"] = structural_persistence
    components["survival"] = numerical_survival * structural_persistence
    if confinement is not None and confinement_retention < 0.5:
        spread = (
            f", spread x{confinement.spread_ratio:.2f}"
            if confinement.spread_ratio is not None
            else ""
        )
        notes.append(
            f"matter DISPERSED: confined fraction fell to "
            f"{confinement_retention:.0%} of its t=0 value by "
            f"t={confinement.final_time}{spread} "
            f"(confined {confinement.initial_confined_frac}->"
            f"{confinement.final_confined_frac}, "
            f"rms {confinement.initial_rms_radius}->{confinement.final_rms_radius})"
        )
    if structural_persistence < 0.5:
        notes.append(
            f"matter structure lost (persistence={structural_persistence:.0%},"
            f" density_retention={density_retention:.2f}, coherence={coherence:.2f},"
            f" confinement={confinement_retention:.2f})"
        )
