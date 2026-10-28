#ifndef SIMULATIONPARAMETERS_HPP
#define SIMULATIONPARAMETERS_HPP

#include "CoreRadialProfile.hpp"
#include "GRParmParse.hpp"
#include "SimulationParametersBase.hpp"
#include "SpinningThroatDiagnostics.hpp"
#include "SpinningWormholeInitialData.hpp"
#include "SpongeZone.hpp"

#include <AMReX_Print.H>

#include <array>
#include <cmath>
#include <exception>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <string>
#include <vector>

class SimulationParameters : public SimulationParametersBase
{
  public:
    SimulationParameters(GRParmParse &pp) : SimulationParametersBase(pp)
    {
        read_shared_params(pp);
        read_spinning_params(pp);
        read_diagnostics_params(pp);
        read_sponge_params(pp);
        read_tagging_params(pp);
        check_params();
    }

    void read_shared_params(GRParmParse &pp)
    {
        pp.load("calculate_constraint_norms", calculate_constraint_norms,
                false);

        // Per-level masked norms (constraint_norms_levels.dat): each level's
        // cells where no finer level covers them, outside mask_radius of the
        // centre.  The compactified far end is a puncture at r = 0 whose
        // floor-limited cells dominate an unmasked norm without converging.
        // The default 0.125 is the innermost shell edge of the offline checks
        // (t0_checks.py).
        pp.load("constraint_norms_levels", constraint_norms_levels, false);
        pp.load("constraint_norms_mask_radius", constraint_norms_mask_radius,
                0.125);
        // Cells within this many cells of the domain boundary are left out of
        // the per-level norms too: they evolve under the Sommerfeld condition,
        // not Einstein's equations, and the constraint stencil there reaches
        // the extrapolated ghosts.  0 = the whole level.
        pp.load("constraint_norms_edge_cells", constraint_norms_edge_cells, 0);
    }

    void read_spinning_params(GRParmParse &pp)
    {
        // The whole physics input is one tabulated stationary background
        // (RotatingBackgroundTable.hpp): static, slowly rotating O(J^2) and
        // full numerical backgrounds all arrive through the same file format,
        // generated offline by the wrapper.  No analytic in-code family.
        pp.load("spinning_background_file", spinning_background_file,
                std::string(""));
        // 1 (default): C2 cubic-spline interpolation of the table; 0: bilinear,
        // whose kinks make the constraints grow with resolution
        // (RotatingBackgroundTable.hpp).
        pp.load("spinning_background_interp", spinning_background_interp, 1);
        pp.load("rk_stage_refill", rk_stage_refill, 1);

        pp.load("center", spinning_params.grid_center, center);

        // 0 keeps the background's stationary lapse e^{f/2}; 1-3 are the
        // usual precollapsed variants (sqrt(chi), 1 - 3 ln chi, chi).
        pp.load("spinning_initial_lapse_type",
                spinning_params.initial_lapse_type, 0);

        // ell = 0 Pi shell seed (both signs through the amplitude); it
        // violates the constraints at O(A).
        pp.load("spinning_seed_amplitude", spinning_params.seed_amplitude,
                0.0);
        pp.load("spinning_seed_width", spinning_params.seed_width, 1.0);
        pp.load("spinning_seed_radius", spinning_params.seed_radius, 0.0);

        // The kick (SpinningWormholeInitialData.hpp): a conformal-factor shell
        // on the throat with an angular profile, to seed sectors the
        // background does not.  m alone picks the sectoral (m, m); l = 2 alone
        // the axisymmetric P2.  Amplitude 0 = off.
        pp.load("spinning_kick_amplitude", spinning_params.kick_amplitude,
                0.0);
        pp.load("spinning_kick_m", spinning_params.kick_m, 0);
        pp.load("spinning_kick_l", spinning_params.kick_l,
                spinning_params.kick_m);
        pp.load("spinning_kick_width", spinning_params.kick_width, 0.0);
        // No default centre: a shell off the throat leaves the throat alone.
        // The throat's eta is r - eta0^2/(4 r) at throat_spheres.dat's
        // r_throat.
        kick_radius_given = pp.contains("spinning_kick_radius");
        pp.load("spinning_kick_radius", spinning_params.kick_radius, 0.0);

        // Potential mass of the phantom scalar (0 = the Ellis-Bronnikov
        // massless field that supports the throat).  The table's
        // potential_coeffs add to it (check_params reads them).
        pp.load("phantom_mass", phantom_mass, 0.0);
    }

    void read_diagnostics_params(GRParmParse &pp)
    {
        // Throat radii + ergoregion monitor, one row per coarse step
        // (SpinningThroatDiagnostics.hpp).  Own file, default off.
        pp.load("spinning_diagnostics", spinning_diag_params.enabled, false);
        spinning_diag_params.grid_center = spinning_params.grid_center;
        // Negative (the default) means 0.3 eta0, taken from the loaded table
        // at run time (eta0 lives in the .spinbg header, not in the params).
        pp.load("spinning_diag_min_radius", spinning_diag_params.min_radius,
                -1.0);

        // Radially binned min/max profile about the centre, shared with the
        // merger example (CoreRadialProfile.hpp).
        pp.load("core_radial_profile", core_profile_params.enabled, false);
        pp.load("core_profile_r_max", core_profile_params.r_max,
                amrex::Real(2.0));
        pp.load("core_profile_dr", core_profile_params.dr,
                amrex::Real(0.03125));
        pp.load("core_profile_interval", core_profile_params.interval, 1);
        for (int d = 0; d < AMREX_SPACEDIM; ++d)
        {
            core_profile_params.centre[d] =
                static_cast<amrex::Real>(spinning_params.grid_center[d]);
        }
    }

    void read_sponge_params(GRParmParse &pp)
    {
        // Radially-ramped extra Kreiss-Oliger dissipation in an outer shell
        // (Source/Grids/SpongeZone.hpp); by default the outer quarter of the
        // half-width.
        const double half_L = 0.5 * L;
        pp.load("sponge_enabled", sponge_params.enabled, false);
        pp.load("sponge_inner_radius", sponge_params.inner_radius,
                0.75 * half_L);
        pp.load("sponge_outer_radius", sponge_params.outer_radius, half_L);
        pp.load("sponge_strength", sponge_params.strength, 4.0);
        pp.load("sponge_ramp_power", sponge_params.ramp_power, 4);
        pp.load("sponge_center", sponge_params.center,
                spinning_params.grid_center);
        // Damping sponge (SpongeDrive.hpp): drive the state back to the
        // stationary background in the same shell, absorbing the
        // long-wavelength gauge pulse the KO sponge passes.  0 = off;
        // explicit stability needs strength * dt < ~1.
        pp.load("sponge_drive_strength", sponge_drive_strength, 0.0);
        // Sommerfeld boundaries on the deviation from the t = 0 background
        // (the drive's reference) instead of on the state, for box faces where
        // the background is far from flat and the flat-space condition injects
        // junk from t ~ 1.  0 = off.
        pp.load("sommerfeld_relative_to_background",
                sommerfeld_relative_to_background, 0);
    }

    void read_tagging_params(GRParmParse &pp)
    {
        // 0 = chi-gradient tagging (plus optional phi/K weights);
        // 1 = fixed nested boxes about tagging_center, composed with the
        // ExtractionTagger (for a single centred throat the resolution demand
        // is static: the throat and the compactified far universe both sit at
        // the centre).
        pp.load("tagging_type", tagging_type, 0);
        pp.load("tagging_L", tagging_L, L);
        pp.load("tagging_center", tagging_center, center);
        pp.load("tagging_phi_weight", tagging_phi_weight, 0.0);
        pp.load("tagging_K_weight", tagging_K_weight, 0.0);
        pp.load("rescale_det_h", rescale_det_h, 0);
    }

    void check_params()
    {
        if (spinning_background_file.empty())
        {
            amrex::Abort("spinning_background_file must name a .spinbg "
                         "background table; there is no analytic in-code "
                         "initial-data family in this example");
        }
        {
            std::ifstream probe(spinning_background_file);
            if (!probe.good())
            {
                amrex::Abort("spinning_background_file does not exist or is "
                             "not readable: " +
                             spinning_background_file);
            }
        }
        // The potential's polynomial lives in the table header, beside the
        // background it was solved with; every potential site reads this copy.
        try
        {
            potential_coeffs =
                RotatingBackgroundTable::read_header(spinning_background_file)
                    .potential_coeffs;
        }
        catch (const std::exception &e)
        {
            amrex::Abort(e.what());
        }
        if (!potential_coeffs.empty())
        {
            std::ostringstream msg;
            msg << std::setprecision(17)
                << "SpinningWormhole potential: V = 1/2 m^2 phi^2 + sum_k a_k "
                   "phi^k, m = "
                << phantom_mass << ", a_0.. =";
            for (const double a : potential_coeffs)
            {
                msg << " " << a;
            }
            amrex::Print() << msg.str() << "\n";
        }
        if (tagging_type != 0 && tagging_type != 1)
        {
            amrex::Abort("tagging_type must be 0 (chi) or 1 (fixed boxes)");
        }
        if (tagging_L <= 0.0)
        {
            amrex::Abort("tagging_L must be > 0");
        }
        if (spinning_params.seed_amplitude != 0.0 &&
            spinning_params.seed_width <= 0.0)
        {
            amrex::Abort("spinning_seed_width must be > 0 when "
                         "spinning_seed_amplitude != 0");
        }
        if (spinning_params.kick_amplitude != 0.0)
        {
            const int l = spinning_params.kick_l;
            const int m = spinning_params.kick_m;
            const bool axisymmetric = (m == 0 && (l == 0 || l == 2));
            const bool sectoral     = (m >= 1 && m <= 8 && l == m);
            if (!axisymmetric && !sectoral)
            {
                amrex::Abort("spinning_kick (l, m) must be (0, 0), (2, 0) or "
                             "(m, m) with 1 <= m <= 8");
            }
            if (!kick_radius_given)
            {
                amrex::Abort("spinning_kick_radius must be given with the "
                             "kick: the throat's eta, r - eta0^2/(4 r) at "
                             "throat_spheres.dat's r_throat");
            }
            if (std::abs(spinning_params.kick_amplitude) >= 1.0)
            {
                amrex::Abort("|spinning_kick_amplitude| must be < 1 "
                             "(psi_k > 0)");
            }
            amrex::Print() << "SpinningWormhole kick: eps "
                           << spinning_params.kick_amplitude << ", (l, m) = ("
                           << l << ", " << m << "), eta_c "
                           << spinning_params.kick_radius << ", width "
                           << spinning_params.kick_width
                           << " (<= 0: eta0/4)\n";
        }
        if (tagging_phi_weight < 0.0 || tagging_K_weight < 0.0)
        {
            amrex::Abort("tagging_phi_weight / tagging_K_weight must be >= 0");
        }
        if (constraint_norms_mask_radius < 0.0)
        {
            amrex::Abort("constraint_norms_mask_radius must be >= 0");
        }
        if (constraint_norms_edge_cells < 0)
        {
            amrex::Abort("constraint_norms_edge_cells must be >= 0");
        }
    }

    bool calculate_constraint_norms{};
    bool constraint_norms_levels{};
    double constraint_norms_mask_radius{};
    int constraint_norms_edge_cells{};

    std::string spinning_background_file;
    int spinning_background_interp = 1;
    //! 1: specificEvalRHS re-fills each RK stage from StateData (see there)
    int rk_stage_refill = 1;
    SpinningWormholeInitialData::params_t spinning_params{};
    bool kick_radius_given{};
    double phantom_mass{};
    //! a_0 .. a_n of the table header's potential_coeffs (empty: none)
    std::vector<double> potential_coeffs;

    SpinningThroatDiagnostics::params_t spinning_diag_params{};
    CoreRadialProfile::params_t core_profile_params{};
    SpongeZoneParams sponge_params{};
    double sponge_drive_strength{0.0};
    int sommerfeld_relative_to_background{0};

    int tagging_type{};
    double tagging_L{};
    std::array<double, AMREX_SPACEDIM> tagging_center{};
    double tagging_phi_weight{};
    double tagging_K_weight{};
    int rescale_det_h{};
};

#endif /* SIMULATIONPARAMETERS_HPP */
