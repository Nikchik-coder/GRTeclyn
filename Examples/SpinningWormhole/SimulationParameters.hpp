#ifndef SIMULATIONPARAMETERS_HPP
#define SIMULATIONPARAMETERS_HPP

#include "CoreRadialProfile.hpp"
#include "GRParmParse.hpp"
#include "SimulationParametersBase.hpp"
#include "SpinningThroatDiagnostics.hpp"
#include "SpinningWormholeInitialData.hpp"
#include "SpongeZone.hpp"

#include <array>
#include <fstream>
#include <string>

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
    }

    void read_spinning_params(GRParmParse &pp)
    {
        // The whole physics input is one tabulated stationary background
        // (RotatingBackgroundTable.hpp): static, slowly rotating O(J^2) and
        // full numerical backgrounds all arrive through the same file format,
        // generated offline by the wrapper.  No analytic in-code family.
        pp.load("spinning_background_file", spinning_background_file,
                std::string(""));

        pp.load("center", spinning_params.grid_center, center);

        // 0 keeps the background's stationary lapse e^{f/2}; 1-3 are the
        // usual precollapsed variants (sqrt(chi), 1 - 3 ln chi, chi).
        pp.load("spinning_initial_lapse_type",
                spinning_params.initial_lapse_type, 0);

        // ell = 0 Pi shell seed (both signs through the amplitude); like the
        // merger campaign's seeds it violates the constraints at O(A).
        pp.load("spinning_seed_amplitude", spinning_params.seed_amplitude,
                0.0);
        pp.load("spinning_seed_width", spinning_params.seed_width, 1.0);
        pp.load("spinning_seed_radius", spinning_params.seed_radius, 0.0);

        // Potential mass of the phantom scalar (0 = the Ellis-Bronnikov
        // massless field that supports the throat).
        pp.load("phantom_mass", phantom_mass, 0.0);
    }

    void read_diagnostics_params(GRParmParse &pp)
    {
        // Throat radii + ergoregion monitor, one row per coarse step
        // (SpinningThroatDiagnostics.hpp).  Own module, own file, default
        // off; every campaign template turns it on.
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
        // (Source/Grids/SpongeZone.hpp), same geometry defaults as the merger
        // campaign: sponge the outer quarter of the half-width.
        const double half_L = 0.5 * L;
        pp.load("sponge_enabled", sponge_params.enabled, false);
        pp.load("sponge_inner_radius", sponge_params.inner_radius,
                0.75 * half_L);
        pp.load("sponge_outer_radius", sponge_params.outer_radius, half_L);
        pp.load("sponge_strength", sponge_params.strength, 4.0);
        pp.load("sponge_ramp_power", sponge_params.ramp_power, 4);
        pp.load("sponge_center", sponge_params.center,
                spinning_params.grid_center);
    }

    void read_tagging_params(GRParmParse &pp)
    {
        // 0 = chi-gradient tagging (plus optional phi/K weights);
        // 1 = fixed nested boxes about tagging_center, composed with the
        // ExtractionTagger (the merger campaign's production choice for a
        // single centred throat: the resolution demand is static -- the
        // throat and the compactified far universe both sit at the centre).
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
        if (tagging_phi_weight < 0.0 || tagging_K_weight < 0.0)
        {
            amrex::Abort("tagging_phi_weight / tagging_K_weight must be >= 0");
        }
    }

    bool calculate_constraint_norms{};

    std::string spinning_background_file;
    SpinningWormholeInitialData::params_t spinning_params{};
    double phantom_mass{};

    SpinningThroatDiagnostics::params_t spinning_diag_params{};
    CoreRadialProfile::params_t core_profile_params{};
    SpongeZoneParams sponge_params{};

    int tagging_type{};
    double tagging_L{};
    std::array<double, AMREX_SPACEDIM> tagging_center{};
    double tagging_phi_weight{};
    double tagging_K_weight{};
    int rescale_det_h{};
};

#endif /* SIMULATIONPARAMETERS_HPP */
