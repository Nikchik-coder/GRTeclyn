#ifndef SIMULATIONPARAMETERS_HPP
#define SIMULATIONPARAMETERS_HPP

#include "BinaryThroatDiagnostics.hpp"
#include "CoreFreezeFill.hpp"
#include "CoreLapseFreeze.hpp"
#include "CoreMatterDamping.hpp"
#include "BinaryWormholeInitialData.hpp"
#include "ExternalGridInitialData.hpp"
#include "GRParmParse.hpp"
#include "SimulationParametersBase.hpp"
#include "SpongeZone.hpp"
#include "ThroatTracker.hpp"

#include <array>
#include <string>

class SimulationParameters : public SimulationParametersBase
{
  public:
    SimulationParameters(GRParmParse &pp) : SimulationParametersBase(pp)
    {
        read_shared_params(pp);
        read_wormhole_params(pp);
        read_diagnostics_params(pp);
        read_core_damping_params(pp);
        read_core_lapse_freeze_params(pp);
        read_core_freeze_fill_params(pp);
        read_sponge_params(pp);
        read_tagging_params(pp);
        check_params();
    }

    void read_shared_params(GRParmParse &pp)
    {
        pp.load("calculate_constraint_norms", calculate_constraint_norms,
                false);
    }

    void read_wormhole_params(GRParmParse &pp)
    {
        pp.load("wormhole_initial_lapse_type",
                wormhole_params.initial_lapse_type, 0);

        // Origin-isolating lapse (type 4) collar shape.  Defaults reproduce
        // the published 0.3 / 8; lower BOTH to widen the collar when the grid
        // cannot resolve it (see BinaryWormholeInitialData.hpp, type 4).
        pp.load("wormhole_lapse_core_fraction",
                wormhole_params.lapse_core_fraction, 0.3);
        pp.load("wormhole_lapse_core_power",
                wormhole_params.lapse_core_power, 8.0);

        // Initial-data family.  0 = the original isotropic Ellis throat plus a
        // Brill-Lindquist bare mass; 1 = the regular massive drainhole, which
        // carries its ADM mass in the lapse instead and so keeps chi = O(1) at
        // the throat.  Default 0 so that no archived run changes.
        pp.load("wormhole_id_type", wormhole_params.id_type, 0);

        pp.load("center", wormhole_params.grid_center, center);

        // Throat radii.  B defaults to A (equal-throat binary); B = 0 removes
        // throat B entirely (single-throat regression mode, Reference.md Phase 1-2).
        pp.load("wormhole_throat_radius_A", wormhole_params.b0_A, 1.0);
        pp.load("wormhole_throat_radius_B", wormhole_params.b0_B,
                wormhole_params.b0_A);

        // Puncture bare masses (the m/(2r) piece of psi).  Zero is the
        // massless, ultrastatic throat with M_ADM = 0 - two of those do NOT
        // attract each other.  Nonzero selects the massive drainhole branch,
        // so the pair genuinely falls together under its own gravity.
        // B defaults to A (equal-mass binary).
        pp.load("wormhole_bare_mass_A", wormhole_params.bare_mass_A, 0.0);
        pp.load("wormhole_bare_mass_B", wormhole_params.bare_mass_B,
                wormhole_params.bare_mass_A);

        // Drainhole ADM masses (id_type = 1).  These enter through the lapse,
        // alpha = e^{u}, not through the conformal factor, so unlike
        // wormhole_bare_mass they cost nothing in resolution at the throat.
        // B defaults to A (equal-mass binary).
        pp.load("wormhole_drainhole_mass_A", wormhole_params.drainhole_mass_A,
                0.0);
        pp.load("wormhole_drainhole_mass_B", wormhole_params.drainhole_mass_B,
                wormhole_params.drainhole_mass_A);

        // Throat positions, as offsets relative to `center`.  B defaults to the
        // mirror image of A, which is the symmetric binary.
        std::array<double, AMREX_SPACEDIM> default_centerA = {0.0, 0.0, 5.0};
        pp.load("wormhole_centerA", wormhole_params.centerA, default_centerA);
        std::array<double, AMREX_SPACEDIM> default_centerB = {
            -wormhole_params.centerA[0], -wormhole_params.centerA[1],
            -wormhole_params.centerA[2]};
        pp.load("wormhole_centerB", wormhole_params.centerB, default_centerB);

        // Bowen-York momenta.  B defaults to -A, i.e. zero total momentum.
        //   head-on along z : momentumA = 0 0 -P   (A sits at +z)
        //   spiralling      : momentumA = 0 +Pt 0  (A sits at +z, orbit in y-z)
        std::array<double, AMREX_SPACEDIM> zero3 = {0.0, 0.0, 0.0};
        pp.load("wormhole_momentumA", wormhole_params.momentumA, zero3);
        std::array<double, AMREX_SPACEDIM> default_momentumB = {
            -wormhole_params.momentumA[0], -wormhole_params.momentumA[1],
            -wormhole_params.momentumA[2]};
        pp.load("wormhole_momentumB", wormhole_params.momentumB,
                default_momentumB);

        pp.load("phantom_mass", wormhole_params.phantom_mass, 0.0);
        pp.load("wormhole_support_strength", wormhole_params.support_strength,
                1.0);

        // The seeded Gaussian scalar perturbation of the single-throat example
        // has NO place in a merger: there the point was to pick the
        // Shinkai-Hayward collapse or expansion branch by hand, here the other
        // throat is the perturbation and pre-destabilising the pair would
        // contaminate the result.  Reject stale params files loudly instead of
        // silently ignoring the keys.
        for (const auto *removed_key :
             {"wormhole_phi_monopole_amplitude",
              "wormhole_phi_perturbation_amplitude",
              "wormhole_phi_perturbation_width"})
        {
            check_parameter(removed_key, std::string("<set>"),
                            !pp.contains(removed_key),
                            "no longer exists in BinaryWormholeMerger: the "
                            "throats start in their own exact equilibrium and "
                            "the merger itself provides the perturbation.  "
                            "Delete this key from the params file.");
        }

        pp.load("wormhole_subtract_phi_asymptote",
                wormhole_params.subtract_phi_asymptote, 1);

        // Relative scalar orientation of throat B (+1 or -1; see the
        // params_t comment).  +1 keeps every archived run bit-identical.
        pp.load("wormhole_phi_sign_B", wormhole_params.phi_sign_B, 1.0);
        check_parameter("wormhole_phi_sign_B", wormhole_params.phi_sign_B,
                        wormhole_params.phi_sign_B == 1.0 ||
                            wormhole_params.phi_sign_B == -1.0,
                        "must be +1 or -1: the closed-form drainhole scalar "
                        "is exact only at full amplitude, any other value "
                        "breaks the Hamiltonian constraint at O(1)");

        // Optional GRTresna-solved initial data (Route B).  Empty => use the
        // analytic superposition above.
        pp.load("recipe_initial_data_file", recipe_initial_data_file,
                std::string(""));
        if (!recipe_initial_data_file.empty())
        {
            external_grid_params.gridinit_file = recipe_initial_data_file;
            external_grid_params.grid_center   = center;
        }
    }

    void read_diagnostics_params(GRParmParse &pp)
    {
        // Own module, own output file, default off (see
        // BinaryThroatDiagnostics.hpp).  collapse_diagnostics.dat keeps the
        // single-throat column contract untouched.
        pp.load("binary_throat_diagnostics", binary_diag_params.enabled, false);
        pp.load("binary_diag_axis", binary_diag_params.axis, 2);
        pp.load("binary_diag_split_coord", binary_diag_params.split_coord, 0.0);
        // Default the theta_+ exclusion radius to the larger throat radius:
        // that is 2x the isotropic throat coordinate b/2, which is enough to
        // clear the coordinate-inversion region where theta_+ < 0 always.
        const double default_min_radius =
            std::max(wormhole_params.b0_A, wormhole_params.b0_B);
        pp.load("binary_diag_min_radius", binary_diag_params.min_radius,
                default_min_radius);
        pp.load("binary_diag_collapsed_lapse",
                binary_diag_params.collapsed_lapse, 1.0e-6);
        pp.load("binary_diag_collapsed_min_radius",
                binary_diag_params.collapsed_min_radius, 0.5);
        binary_diag_params.grid_center = wormhole_params.grid_center;
    }

    void read_core_damping_params(GRParmParse &pp)
    {
        // Matter analogue of the puncture trick -- see CoreMatterDamping.hpp.
        // Own module, default off; the damping window sits inside the
        // trapped surface so the exterior is untouched by construction.
        pp.load("core_matter_damping", core_damping_params.enabled, false);
        pp.load("core_damping_lapse_start", core_damping_params.lapse_start,
                3.0e-2);
        pp.load("core_damping_lapse_full", core_damping_params.lapse_full,
                1.0e-3);
        pp.load("core_damping_tau", core_damping_params.tau, 0.25);
        // Radius window (default off): the lapse window defeats itself once
        // wrong-sign K re-inflates the lapse over the sickest cells -- see
        // CoreMatterDamping.hpp.  Set per-run from a measured horizon.
        pp.load("core_damping_radius_start",
                core_damping_params.radius_start, 0.0);
        pp.load("core_damping_radius_full", core_damping_params.radius_full,
                0.0);
        pp.load("core_damping_radius_from_time",
                core_damping_params.from_time, 0.0);
        core_damping_params.grid_center = wormhole_params.grid_center;
    }

    void read_core_lapse_freeze_params(GRParmParse &pp)
    {
        // Gauge half of the post-collapse cure -- see CoreLapseFreeze.hpp.
        // Own module, default off; the window is set per-run from the
        // measured position of the wrong-sign-K re-inflation pockets.
        pp.load("core_lapse_freeze", lapse_freeze_params.enabled, false);
        pp.load("core_freeze_radius_start", lapse_freeze_params.radius_start,
                0.0);
        pp.load("core_freeze_radius_full", lapse_freeze_params.radius_full,
                0.0);
        pp.load("core_freeze_from_time", lapse_freeze_params.from_time, 0.0);
        pp.load("core_freeze_shift", lapse_freeze_params.freeze_shift, false);
        lapse_freeze_params.grid_center = wormhole_params.grid_center;
        // The add-back must cancel the exact Bona-Masso source the gauge
        // wrote, so mirror the gauge block's own coefficients.
        GRParmParse gauge_pp("gauge");
        gauge_pp.load("lapse_coeff", lapse_freeze_params.lapse_coeff, 2.0);
        gauge_pp.load("lapse_power", lapse_freeze_params.lapse_power, 1.0);
    }

    void read_core_freeze_fill_params(GRParmParse &pp)
    {
        // Smooth interior fill -- see CoreFreezeFill.hpp.  Own module,
        // default off.  Unlike the damping window this one is NOT causally
        // sealed: its radius comes from the measured failure site (r ~ 1-2),
        // and purity is established by the causal-arrival budget plus the
        // fill-radius insensitivity ladder, not by a horizon argument.
        pp.load("core_freeze_fill", freeze_fill_params.enabled, false);
        pp.load("core_fill_radius_start", freeze_fill_params.radius_start,
                0.0);
        pp.load("core_fill_radius_full", freeze_fill_params.radius_full, 0.0);
        // Engage LATE: the fill has no rate to lose a race with, so it is
        // spent as late as the wall allows, keeping the contaminated light
        // cone out of the extraction window.
        pp.load("core_fill_from_time", freeze_fill_params.from_time, 0.0);
        freeze_fill_params.grid_center = wormhole_params.grid_center;
    }

    void read_sponge_params(GRParmParse &pp)
    {
        // Radially-ramped extra Kreiss-Oliger dissipation in an outer shell,
        // shared with RadialRecipe via Source/Grids/SpongeZone.hpp.  Off by
        // default so no archived run changes.
        //
        // Defaults are scaled to the box rather than copied from RadialRecipe:
        // that example runs L = 64 with the source at the centre and sponges
        // r in [24, 32], i.e. the outer quarter of the half-width.  Expressing
        // that as fractions of L/2 keeps the same geometry at any box size,
        // which matters here because the merger sweeps L with the separation.
        const double half_L = 0.5 * L; // L: physical sidelength of the box
        pp.load("sponge_enabled", sponge_params.enabled, false);
        pp.load("sponge_inner_radius", sponge_params.inner_radius,
                0.75 * half_L);
        pp.load("sponge_outer_radius", sponge_params.outer_radius, half_L);
        pp.load("sponge_strength", sponge_params.strength, 4.0);
        pp.load("sponge_ramp_power", sponge_params.ramp_power, 4);
        pp.load("sponge_center", sponge_params.center,
                wormhole_params.grid_center);
    }

    void read_tagging_params(GRParmParse &pp)
    {
        // Which criterion decides where to refine.  0 = chi gradients
        // (ChiTagger), the default, and what every archived run used;
        // 1 = static nested boxes about a fixed centre (FixedGridsTagger,
        // shared from Source/Tagging).  Default 0 so no archived run changes.
        //
        // Why the choice matters here.  Chi-gradient tagging follows the
        // *error*, so once a run develops junk the mesh chases it and the
        // footprint runs away: the Stage 1 sigma = 0 arm ended in out-of-
        // memory at t = 35.2 with level 2 covering 24 % of the domain and
        // 32.8M cells, while the throat itself was still healthy to 0.5 %
        // (research/merger/Plan.md, 1.5).  The drainhole's resolution demand
        // is by contrast *static*: it sits at the throat and at the
        // compactified far universe, r -> 0, both fixed at the grid centre
        // for a single throat.  A fixed box asks for resolution where the
        // solution needs it rather than where the error happens to be.
        pp.load("tagging_type", tagging_type, 0);

        // FixedGridsTagger tags |x - tagging_center|_inf < tagging_L *
        // 2^-(level+2): the level-0 boxes have half-width tagging_L / 4 and
        // every finer level halves that again.  Defaulting tagging_L to the
        // domain length L reproduces the stock "refine the inner L/4"
        // behaviour of the KleinGordon example; shrink it to wrap the boxes
        // around the throat instead of a quarter of the box.
        pp.load("tagging_L", tagging_L, L);

        // For a single throat this is the grid centre.  A binary needs boxes
        // on each throat, which tagging_type = 1 cannot express - that is
        // what tagging_type = 2 is for.
        pp.load("tagging_center", tagging_center, center);

        // Throat tracking (Plan.md Stage 2.0): locate each throat as the chi
        // pit it carries at its centre and follow it, one row per coarse step
        // in throat_track.dat.  Default off so no archived run changes.  The
        // moving-box tagger (tagging_type = 2) requires it - the boxes are
        // centred on whatever the tracker last measured.
        pp.load("throat_tracking", throat_tracker_params.enabled, false);

        // The search sphere around the last known position.  It only has to
        // cover one coarse step of motion (~2e-3 for v = 0.2) but must stay
        // small enough to see only its own throat's pit; the throat scale a
        // is a safe default for any sane separation.
        pp.load("throat_track_search_radius",
                throat_tracker_params.search_radius,
                std::max(wormhole_params.b0_A, wormhole_params.b0_B));
        throat_tracker_params.grid_center = wormhole_params.grid_center;
    }

    void check_params()
    {
        check_parameter("tagging_type", tagging_type,
                        (tagging_type >= 0) && (tagging_type <= 2),
                        "must be 0 (refine on chi gradients, the default), "
                        "1 (static nested boxes on tagging_center) or "
                        "2 (moving nested boxes on the tracked throats, plus "
                        "the extraction shells when extraction is on)");

        // The moving boxes are centred on whatever the tracker last measured,
        // so running them without the tracker would freeze them at the t = 0
        // positions - i.e. silently degrade to tagging_type = 1 with worse
        // provenance.
        check_parameter("throat_tracking", throat_tracker_params.enabled,
                        (tagging_type != 2) || throat_tracker_params.enabled,
                        "must be 1 when tagging_type = 2: the moving boxes "
                        "follow the tracked throat positions and are "
                        "meaningless without the tracker");

        check_parameter("throat_track_search_radius",
                        throat_tracker_params.search_radius,
                        !throat_tracker_params.enabled ||
                            (throat_tracker_params.search_radius > 0.0),
                        "must be positive when throat_tracking = 1");

        check_parameter("tagging_L", tagging_L, tagging_L > 0.0,
                        "must be positive: it is the length whose inner "
                        "quarter the level-0 fixed boxes cover");

        // regrid_threshold is ChiTagger's trigger and has no meaning for the
        // fixed tagger.  Silently ignoring it would let someone tune a knob
        // that does nothing and conclude the tagger did not help.
        warn_parameter("tagging_type", tagging_type, tagging_type == 0,
                       "selects a geometric tagger (fixed or moving boxes), "
                       "so regrid_threshold is ignored: refinement no longer "
                       "responds to the solution at all.  Set tagging_L to "
                       "control the boxes.");

        check_parameter("wormhole_id_type", wormhole_params.id_type,
                        (wormhole_params.id_type == 0) ||
                            (wormhole_params.id_type == 1),
                        "must be 0 (isotropic Ellis + Brill-Lindquist bare "
                        "mass, the original) or 1 (regular massive drainhole)");

        check_parameter("wormhole_initial_lapse_type",
                        wormhole_params.initial_lapse_type,
                        (wormhole_params.initial_lapse_type >= 0) &&
                            (wormhole_params.initial_lapse_type <= 6),
                        "must be 0 (flat), 1 (sqrt(chi)), 2 (1-3ln(chi)), "
                        "3 (chi), 4 (origin-isolating), 5 (the drainhole's "
                        "exact static lapse e^u) or 6 (5 x the type-4 collar). "
                        " With id_type = 0 use type 4 for AMR: a flat lapse "
                        "NaNs at max_level >= 3 because refining the throat "
                        "drags cells into the compactified origin where "
                        "chi ~ r^4.  With id_type = 1 use 5, or 6 under AMR.");

        // The two mass knobs belong to different initial-data families and
        // mixing them is always a mistake, not a blend: bare_mass is the very
        // puncture that id_type = 1 exists to remove, and drainhole_mass has no
        // meaning without the e^{2u} conformal factor that id_type = 0 lacks.
        check_parameter("wormhole_bare_mass_A/B",
                        wormhole_params.bare_mass_A + wormhole_params.bare_mass_B,
                        (wormhole_params.id_type == 0) ||
                            ((wormhole_params.bare_mass_A == 0.0) &&
                             (wormhole_params.bare_mass_B == 0.0)),
                        "is a Brill-Lindquist puncture and must be zero when "
                        "wormhole_id_type = 1: adding it drives chi -> 0 at "
                        "the throat, which is exactly the failure the "
                        "drainhole branch exists to remove.  Use "
                        "wormhole_drainhole_mass_A/B instead.");

        check_parameter("wormhole_drainhole_mass_A/B",
                        wormhole_params.drainhole_mass_A +
                            wormhole_params.drainhole_mass_B,
                        (wormhole_params.id_type == 1) ||
                            ((wormhole_params.drainhole_mass_A == 0.0) &&
                             (wormhole_params.drainhole_mass_B == 0.0)),
                        "is ignored unless wormhole_id_type = 1.  Set "
                        "wormhole_id_type = 1, or use wormhole_bare_mass_A/B.");

        check_parameter("wormhole_drainhole_mass_A",
                        wormhole_params.drainhole_mass_A,
                        wormhole_params.drainhole_mass_A >= 0.0,
                        "must be >= 0 (it is the throat's ADM mass)");
        check_parameter("wormhole_drainhole_mass_B",
                        wormhole_params.drainhole_mass_B,
                        wormhole_params.drainhole_mass_B >= 0.0,
                        "must be >= 0 (it is the throat's ADM mass)");

        // alpha = e^{u} is part of the drainhole solution, not a gauge taste:
        // with any other initial lapse the configuration is not static and
        // starts moving for a reason that has nothing to do with the binary.
        warn_parameter("wormhole_initial_lapse_type",
                       wormhole_params.initial_lapse_type,
                       (wormhole_params.id_type == 0) ||
                           (wormhole_params.initial_lapse_type == 5) ||
                           (wormhole_params.initial_lapse_type == 6),
                       "is not the drainhole's own static lapse.  With "
                       "wormhole_id_type = 1 the exact static lapse is "
                       "alpha = e^{u} (type 5, or 6 under AMR); anything else "
                       "makes the initial data non-static by construction.");

        // chi at the throat is e^{2u(m)} / Omega^2 and falls monotonically with
        // m/a: 0.25 at m/a = 0, 0.19 at 0.3, 0.15 at 1.0.  Past about 1 the
        // proper cell width at the throat starts climbing back towards the
        // puncture values this branch exists to escape.
        const double a_max =
            std::max(wormhole_params.b0_A, wormhole_params.b0_B);
        const double m_drain_max = std::max(wormhole_params.drainhole_mass_A,
                                            wormhole_params.drainhole_mass_B);
        warn_parameter("wormhole_drainhole_mass_A/B", m_drain_max,
                       (wormhole_params.id_type == 0) || (a_max <= 0.0) ||
                           (m_drain_max <= a_max),
                       "exceeds the throat radius.  chi at the throat falls "
                       "with m/a (0.25 at 0, 0.19 at 0.3, 0.15 at 1), so a "
                       "large ratio gives back the resolution the drainhole "
                       "branch was adopted to gain.  Prefer a bigger throat "
                       "over a heavier one.");

        check_parameter("wormhole_throat_radius_A", wormhole_params.b0_A,
                        wormhole_params.b0_A > 0.0, "must be positive");

        check_parameter("wormhole_throat_radius_B", wormhole_params.b0_B,
                        wormhole_params.b0_B >= 0.0,
                        "must be >= 0 (0 removes throat B entirely - the "
                        "single-throat regression mode; equal to A is the "
                        "symmetric binary)");

        check_parameter("wormhole_bare_mass_A", wormhole_params.bare_mass_A,
                        wormhole_params.bare_mass_A >= 0.0, "must be >= 0");
        check_parameter("wormhole_bare_mass_B", wormhole_params.bare_mass_B,
                        wormhole_params.bare_mass_B >= 0.0, "must be >= 0");

        check_parameter("binary_diag_axis", binary_diag_params.axis,
                        (binary_diag_params.axis >= 0) &&
                            (binary_diag_params.axis < AMREX_SPACEDIM),
                        "must be 0, 1 or 2");

        // Shifting phi by a constant is exactly free only for a massless field.
        warn_parameter("wormhole_subtract_phi_asymptote",
                       wormhole_params.subtract_phi_asymptote,
                       (wormhole_params.subtract_phi_asymptote == 0) ||
                           (wormhole_params.phantom_mass == 0.0),
                       "shifts phi by a constant, which changes the physics "
                       "when phantom_mass != 0 (V = m^2 phi^2 / 2 is not "
                       "shift invariant).  Set it to 0, or accept that the "
                       "potential is being evaluated about a shifted field.");

        // Object B is absent in the single-throat regression mode (b_B = 0 and
        // no bare mass).  Everything below compares the two centres, and none
        // of it means anything when there is only one object: with centerA at
        // the origin, centerB defaults to its mirror image, which is the SAME
        // point, and a coincidence check would reject a perfectly valid
        // single-throat run.
        const bool object_B_absent = (wormhole_params.b0_B == 0.0) &&
                                     (wormhole_params.bare_mass_B == 0.0) &&
                                     (wormhole_params.drainhole_mass_B == 0.0);

        const double dx_sep = wormhole_params.centerA[0] - wormhole_params.centerB[0];
        const double dy_sep = wormhole_params.centerA[1] - wormhole_params.centerB[1];
        const double dz_sep = wormhole_params.centerA[2] - wormhole_params.centerB[2];
        const double separation =
            std::sqrt(dx_sep * dx_sep + dy_sep * dy_sep + dz_sep * dz_sep);
        check_parameter("wormhole_centerA/B", separation,
                        object_B_absent || (separation > 0.0),
                        "the two throats must be at different positions");

        // The superposition error scales as (b/d)^2; warn once it stops being
        // a small correction.  There is no superposition with one object.
        warn_parameter("wormhole_centerA/B", separation,
                       object_B_absent || (separation > 4.0 * a_max),
                       "throats are close enough that the analytic "
                       "superposition error (O(b^2/d^2)) is no longer small; "
                       "prefer constraint-solved initial data at this "
                       "separation");

        // Mass of either kind reintroduces a BBH-like O(m/d) superposition
        // error, because both give the one-body solution a 1/r tail.
        const double m_total = wormhole_params.bare_mass_A +
                               wormhole_params.bare_mass_B +
                               wormhole_params.drainhole_mass_A +
                               wormhole_params.drainhole_mass_B;
        warn_parameter("wormhole_bare_mass/drainhole_mass_A/B", m_total,
                       object_B_absent || (m_total < 0.2 * separation),
                       "masses are large enough that the O(m/d) superposition "
                       "error is no longer small; prefer the Helfer/Ning "
                       "conformal-factor correction or constraint-solved "
                       "initial data (Route B)");

        // A massless throat is ultrastatic (M_ADM = 0): two of them do not
        // attract, so with no bare mass, no momenta and full support the run
        // shows nothing but the throats' own unstable modes.
        const bool any_momentum = (wormhole_params.momentumA[0] != 0.0) ||
                                  (wormhole_params.momentumA[1] != 0.0) ||
                                  (wormhole_params.momentumA[2] != 0.0) ||
                                  (wormhole_params.momentumB[0] != 0.0) ||
                                  (wormhole_params.momentumB[1] != 0.0) ||
                                  (wormhole_params.momentumB[2] != 0.0);
        warn_parameter("wormhole_bare_mass/drainhole_mass_A/B", m_total,
                       (m_total > 0.0) || any_momentum ||
                           (wormhole_params.support_strength != 1.0),
                       "every mass is zero, all momenta are zero and the "
                       "support is at full strength: massless throats are "
                       "ultrastatic (M_ADM = 0) and do not attract, so the "
                       "pair will not fall together.  Set "
                       "wormhole_drainhole_mass_A/B > 0 (with "
                       "wormhole_id_type = 1) for a gravity-driven merger.");

        // A stray Bowen-York term with nothing at its centre is valid data
        // but pure junk radiation - flag it in the single-throat mode.
        warn_parameter("wormhole_momentumB", wormhole_params.momentumB[0],
                       !object_B_absent ||
                           ((wormhole_params.momentumB[0] == 0.0) &&
                            (wormhole_params.momentumB[1] == 0.0) &&
                            (wormhole_params.momentumB[2] == 0.0)),
                       "nonzero momentum on an absent object B (b0_B = 0, "
                       "bare_mass_B = 0) adds a Bowen-York term with nothing "
                       "at its centre");
    }

    bool calculate_constraint_norms{};

    // Refinement criterion: 0 = ChiTagger (default), 1 = FixedGridsTagger.
    int tagging_type{};
    double tagging_L{};
    std::array<double, AMREX_SPACEDIM> tagging_center{};

    std::string recipe_initial_data_file;
    ExternalGridInitialData::params_t external_grid_params{};

    BinaryWormholeInitialData::params_t wormhole_params{};
    BinaryThroatDiagnostics::params_t binary_diag_params{};
    CoreMatterDamping::params_t core_damping_params{};
    CoreLapseFreeze::params_t lapse_freeze_params{};
    CoreFreezeFill::params_t freeze_fill_params{};
    ThroatTracker::params_t throat_tracker_params{};

    // Numerical sponge zone (radially-ramped extra KO dissipation).
    SpongeZoneParams sponge_params{};
};

#endif /* SIMULATIONPARAMETERS_HPP */
