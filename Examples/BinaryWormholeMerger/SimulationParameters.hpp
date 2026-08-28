#ifndef SIMULATIONPARAMETERS_HPP
#define SIMULATIONPARAMETERS_HPP

#include "BinaryThroatDiagnostics.hpp"
#include "BinaryWormholeInitialData.hpp"
#include "ExternalGridInitialData.hpp"
#include "GRParmParse.hpp"
#include "SimulationParametersBase.hpp"
#include "SpongeZone.hpp"

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
        read_sponge_params(pp);
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
        // throat B entirely (single-throat regression mode, Plan.md Phase 1-2).
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
        binary_diag_params.grid_center = wormhole_params.grid_center;
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

    void check_params()
    {
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

    std::string recipe_initial_data_file;
    ExternalGridInitialData::params_t external_grid_params{};

    BinaryWormholeInitialData::params_t wormhole_params{};
    BinaryThroatDiagnostics::params_t binary_diag_params{};

    // Numerical sponge zone (radially-ramped extra KO dissipation).
    SpongeZoneParams sponge_params{};
};

#endif /* SIMULATIONPARAMETERS_HPP */
