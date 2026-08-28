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
        check_parameter("wormhole_initial_lapse_type",
                        wormhole_params.initial_lapse_type,
                        (wormhole_params.initial_lapse_type >= 0) &&
                            (wormhole_params.initial_lapse_type <= 4),
                        "must be 0 (flat), 1 (sqrt(chi)), 2 (1-3ln(chi)), "
                        "3 (chi) or 4 (origin-isolating).  Type 4 is the one "
                        "to use with AMR: a flat lapse NaNs at max_level >= 3 "
                        "because refining the throat drags cells into the "
                        "compactified origin where chi ~ r^4.");

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
                                     (wormhole_params.bare_mass_B == 0.0);

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
        const double b_max =
            std::max(wormhole_params.b0_A, wormhole_params.b0_B);
        warn_parameter("wormhole_centerA/B", separation,
                       object_B_absent || (separation > 4.0 * b_max),
                       "throats are close enough that the analytic "
                       "superposition error (O(b^2/d^2)) is no longer small; "
                       "prefer constraint-solved initial data at this "
                       "separation");

        // Bare masses reintroduce a BBH-like O(m/d) superposition error.
        const double m_total =
            wormhole_params.bare_mass_A + wormhole_params.bare_mass_B;
        warn_parameter("wormhole_bare_mass_A/B", m_total,
                       object_B_absent || (m_total < 0.2 * separation),
                       "bare masses are large enough that the O(m/d) "
                       "superposition error is no longer small; prefer "
                       "constraint-solved initial data (Route B)");

        // A massless throat is ultrastatic (M_ADM = 0): two of them do not
        // attract, so with no bare mass, no momenta and full support the run
        // shows nothing but the throats' own unstable modes.
        const bool any_momentum = (wormhole_params.momentumA[0] != 0.0) ||
                                  (wormhole_params.momentumA[1] != 0.0) ||
                                  (wormhole_params.momentumA[2] != 0.0) ||
                                  (wormhole_params.momentumB[0] != 0.0) ||
                                  (wormhole_params.momentumB[1] != 0.0) ||
                                  (wormhole_params.momentumB[2] != 0.0);
        warn_parameter("wormhole_bare_mass_A/B", m_total,
                       (m_total > 0.0) || any_momentum ||
                           (wormhole_params.support_strength != 1.0),
                       "both bare masses are zero, all momenta are zero and "
                       "the support is at full strength: massless throats do "
                       "not attract, so the pair will not fall together.  Set "
                       "wormhole_bare_mass_A/B > 0 for a gravity-driven "
                       "merger.");

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
