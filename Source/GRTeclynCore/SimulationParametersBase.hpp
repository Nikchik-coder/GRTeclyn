/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef SIMULATIONPARAMETERSBASE_HPP_
#define SIMULATIONPARAMETERSBASE_HPP_

// General includes
#include "AMReXParameters.hpp"
#include "CCZ4RHS.hpp"
#include "GRParmParse.hpp"
#include "SphericalExtractionParameters.hpp"
#include <limits>

// -----------------------------------------------------------------------------
// Fork-local compatibility shim (kept after the 2026-08 upstream merge).
//
// Upstream PR #215 deleted this class: the merged core now reads its own
// parameters from the ParmParse table under new key names (evolution.*,
// ccz4.*, gauge.*, weyl_extraction.*).  This restored version keeps reading
// the ORIGINAL flat keys our params files use and injects the values under
// the new names (see inject_new_scheme_params below), so no params file has
// to change.  Injections are guarded: a params file that already provides a
// new-scheme key wins over the legacy one.
// -----------------------------------------------------------------------------

//! Holds the gauge and damping values read from the original flat keys.  The
//! merged core no longer takes these as constructor arguments - it reads them
//! back from the ParmParse table itself - so this struct only feeds the
//! injection and the parameter checks below.
struct legacy_ccz4_params_t
{
    double lapse_advec_coeff{};
    double lapse_coeff{};
    double lapse_power{};
    double shift_advec_coeff{};
    double shift_Gamma_coeff{};
    double eta{};
    double kappa1{};
    double kappa2{};
    double kappa3{};
    bool covariantZ4{};
};

class SimulationParametersBase : public AMReXParameters
{
  public:
    SimulationParametersBase(GRParmParse &pp) : AMReXParameters(pp)
    {
        read_params(pp);
        check_params();
        // must run after check_params: the BSSN branch zeroes the kappas and
        // the injected values must match what the solver used before
        inject_new_scheme_params();
    }

  private:
    void read_params(GRParmParse &pp)
    {
        // Lapse evolution
        pp.load("lapse_advec_coeff", ccz4_params.lapse_advec_coeff, 1.0);
        pp.load("lapse_coeff", ccz4_params.lapse_coeff, 2.0);
        pp.load("lapse_power", ccz4_params.lapse_power, 1.0);

        // Shift Evolution
        pp.load("shift_advec_coeff", ccz4_params.shift_advec_coeff, 0.0);
        pp.load("shift_Gamma_coeff", ccz4_params.shift_Gamma_coeff, 0.75);
        pp.load("eta", ccz4_params.eta, 1.0);

        // CCZ4 parameters
        pp.load("formulation", formulation, 0);
        pp.load("kappa1", ccz4_params.kappa1, 0.1);
        pp.load("kappa2", ccz4_params.kappa2, 0.0);
        pp.load("kappa3", ccz4_params.kappa3, 1.0);
        pp.load("covariantZ4", ccz4_params.covariantZ4, true);

        // Dissipation
        pp.load("sigma", sigma, 0.1);

        // Nan Check and min chi and lapse values
        pp.load("nan_check", nan_check, true);
        pp.load("min_chi", min_chi, 1e-4);
        pp.load("min_lapse", min_lapse, 1e-4);

        // directory to store data (extraction files, puncture data, constraint
        // norms)
        pp.load("data_subpath", data_path, std::string(""));
        if (!data_path.empty() && data_path.back() != '/')
        {
            data_path += "/";
        }
        if (output_path != "./" && !output_path.empty())
        {
            data_path = output_path + data_path;
        }

        // Extraction params
        pp.load("activate_extraction", activate_extraction, false);
        extraction_params.enabled = activate_extraction;

        if (activate_extraction)
        {
            pp.load("num_extraction_radii",
                    extraction_params.num_extraction_radii(), 1);

            // Check for multiple extraction radii, otherwise load single
            // radius/level (for backwards compatibility).
            std::vector<int> extraction_levels_stdvect;
            if (pp.contains("extraction_levels"))
            {
                pp.load("extraction_levels", extraction_levels_stdvect,
                        extraction_params.num_extraction_radii());
            }
            else
            {
                pp.load("extraction_level", extraction_levels_stdvect, 1, 0);
            }
            extraction_params.extraction_levels.resize(
                extraction_params.num_extraction_radii());
            std::copy(extraction_levels_stdvect.begin(),
                      extraction_levels_stdvect.end(),
                      extraction_params.extraction_levels.begin());

            std::vector<double> extraction_radii_stdvect;
            if (pp.contains("extraction_radii"))
            {
                pp.load("extraction_radii", extraction_radii_stdvect,
                        extraction_params.num_extraction_radii());
            }
            else
            {
                pp.load("extraction_radius", extraction_radii_stdvect, 1, 0.1);
            }
            extraction_params.extraction_radii().resize(
                extraction_params.num_extraction_radii());
            std::copy(extraction_radii_stdvect.begin(),
                      extraction_radii_stdvect.end(),
                      extraction_params.extraction_radii().begin());

            pp.load("num_points_phi", extraction_params.num_points_phi(), 2);
            pp.load("num_points_theta", extraction_params.num_points_theta(),
                    5);
            if (extraction_params.num_points_theta() % 2 == 0)
            {
                extraction_params.num_points_theta() += 1;
                amrex::Print()
                    << "Parameter: num_points_theta incompatible with "
                       "Simpson's "
                    << "rule so increased by 1.\n";
            }
            pp.load("extraction_center", extraction_params.center, center);

            if (pp.contains("modes"))
            {
                pp.load("num_modes", extraction_params.num_modes);
                std::vector<int> extraction_modes_vect(
                    static_cast<size_t>(2 * extraction_params.num_modes));
                pp.load("modes", extraction_modes_vect,
                        2 * extraction_params.num_modes);
                extraction_params.modes.resize(extraction_params.num_modes);
                for (size_t i = 0; i < extraction_params.num_modes; ++i)
                {
                    extraction_params.modes[i].first =
                        extraction_modes_vect[2 * i];
                    extraction_params.modes[i].second =
                        extraction_modes_vect[2 * i + 1];
                }
            }
            else
            {
                // by default extraction (l,m) = (2,0), (2,1) and (2,2)
                extraction_params.num_modes = 3;
                extraction_params.modes.resize(3);
                for (size_t i = 0; i < 3; ++i)
                {
                    extraction_params.modes[i].first  = 2;
                    extraction_params.modes[i].second = static_cast<int>(i);
                }
            }

            pp.load("write_extraction", extraction_params.write_extraction,
                    false);

            std::string extraction_path;
            pp.load("extraction_subpath", extraction_path, data_path);
            if (!extraction_path.empty() && extraction_path.back() != '/')
            {
                extraction_path += "/";
            }
            if (output_path != "./" && !output_path.empty())
            {
                extraction_path = output_path + extraction_path;
            }

            extraction_params.data_path       = data_path;
            extraction_params.extraction_path = extraction_path;

            // default names to Weyl extraction
            pp.load("extraction_file_prefix",
                    extraction_params.extraction_file_prefix,
                    std::string("Weyl4_extraction_"));
            pp.load("integral_file_prefix",
                    extraction_params.integral_file_prefix,
                    std::string("Weyl4_mode_"));
        }
    }

    //! Publish the legacy values under the new key names the merged core
    //! reads directly from the ParmParse table.
    void inject_new_scheme_params()
    {
        inject("evolution.sigma", sigma);
        inject("evolution.nan_check", nan_check);

        inject("ccz4.formulation", formulation);
        inject("ccz4.kappa1", ccz4_params.kappa1);
        inject("ccz4.kappa2", ccz4_params.kappa2);
        inject("ccz4.kappa3", ccz4_params.kappa3);
        inject("ccz4.covariantZ4", ccz4_params.covariantZ4);
        inject("ccz4.min_chi", min_chi);
        inject("ccz4.min_lapse", min_lapse);

        inject("gauge.lapse_advec_coeff", ccz4_params.lapse_advec_coeff);
        inject("gauge.lapse_power", ccz4_params.lapse_power);
        inject("gauge.lapse_coeff", ccz4_params.lapse_coeff);
        inject("gauge.shift_Gamma_coeff", ccz4_params.shift_Gamma_coeff);
        inject("gauge.shift_advec_coeff", ccz4_params.shift_advec_coeff);
        inject("gauge.eta", ccz4_params.eta);

        // Weyl4's base constructor requires weyl_extraction.center whenever a
        // Weyl4 compute class is built, extraction active or not.  Use the
        // old flat extraction_center key when present, the grid center
        // otherwise (the old default).
        amrex::ParmParse table_pp;
        if (!table_pp.contains("weyl_extraction.center"))
        {
            std::array<double, AMREX_SPACEDIM> weyl_center = center;
            GRParmParse flat_pp;
            flat_pp.load("extraction_center", weyl_center, center);
            table_pp.addarr("weyl_extraction.center",
                            std::vector<double>{weyl_center[0], weyl_center[1],
                                                weyl_center[2]});
        }
    }

    void check_params()
    {
        check_parameter("dt_multiplier", dt_multiplier, dt_multiplier < 1.0,
                        "must be < 1.0 for stability");
        warn_parameter("dt_multiplier", dt_multiplier, dt_multiplier <= 0.5,
                       "is unlikely to be stable for > 0.5");

        check_parameter("sigma", sigma,
                        (sigma >= 0.0) && (sigma <= 2.0 / dt_multiplier),
                        "must be >= 0.0 and <= 2 / dt_multiplier for stability "
                        "(see Alcubierre p344)");
        warn_parameter("nan_check", nan_check, nan_check,
                       "should not normally be disabled");
        check_parameter("formulation", formulation,
                        (formulation == CCZ4RHS<>::USE_CCZ4) ||
                            (formulation == CCZ4RHS<>::USE_BSSN),
                        "must be 0 or 1");
        // NOLINTBEGIN(bugprone-branch-clone)
        if (formulation == CCZ4RHS<>::USE_CCZ4)
        {
            warn_parameter(
                "kappa1", ccz4_params.kappa1, ccz4_params.kappa1 > 0.0,
                "should be greater than 0.0 to damp constraints (see "
                "arXiv:1106.2254).");
            warn_parameter("kappa2", ccz4_params.kappa2,
                           ccz4_params.kappa2 > -1.0,
                           "should be greater than -1.0 to damp constraints "
                           "(see arXiv:1106.2254)");
        }
        // NOLINTEND(bugprone-branch-clone)
        else if (formulation == CCZ4RHS<>::USE_BSSN)
        {
            // maybe we should just set these to zero and print a warning
            // in the BSSN case
            warn_parameter("kappa1", ccz4_params.kappa1,
                           ccz4_params.kappa1 == 0.0,
                           "setting to 0.0 as required for BSSN");
            warn_parameter("kappa2", ccz4_params.kappa2,
                           ccz4_params.kappa2 == 0.0,
                           "setting to 0.0 as required for BSSN");
            warn_parameter("kappa3", ccz4_params.kappa3,
                           ccz4_params.kappa3 == 0.0,
                           "setting to 0.0 as required for BSSN");
            // no warning necessary for ccz4_params.covariantZ4
            ccz4_params.kappa1 = 0.0;
            ccz4_params.kappa2 = 0.0;
            ccz4_params.kappa3 = 0.0;
        }

        // only warn for gauge parameters as there are legitimate cases you may
        // want to deviate from the norm
        warn_parameter("lapse_advec_coeff", ccz4_params.lapse_advec_coeff,
                       std::min(std::abs(ccz4_params.lapse_advec_coeff),
                                std::abs(ccz4_params.lapse_advec_coeff - 1.0)) <
                           std::numeric_limits<double>::epsilon(),
                       "usually set to 0.0 or 1.0");
        warn_parameter("lapse_power", ccz4_params.lapse_power,
                       std::abs(ccz4_params.lapse_power - 1.0) <
                           std::numeric_limits<double>::epsilon(),
                       "set to 1.0 for 1+log slicing");
        warn_parameter("lapse_coeff", ccz4_params.lapse_coeff,
                       std::abs(ccz4_params.lapse_coeff - 2.0) <
                           std::numeric_limits<double>::epsilon(),
                       "set to 2.0 for 1+log slicing");
        warn_parameter("shift_Gamma_coeff", ccz4_params.shift_Gamma_coeff,
                       std::abs(ccz4_params.shift_Gamma_coeff - 0.75) <
                           std::numeric_limits<double>::epsilon(),
                       "usually set to 0.75");
        warn_parameter("shift_advec_coeff", ccz4_params.shift_advec_coeff,
                       std::min(std::abs(ccz4_params.shift_advec_coeff),
                                std::abs(ccz4_params.shift_advec_coeff - 1.0)) <
                           std::numeric_limits<double>::epsilon(),
                       "usually set to 0.0 or 1.0");
        warn_parameter("eta", ccz4_params.eta,
                       ccz4_params.eta > 0.1 && ccz4_params.eta < 10,
                       "usually O(1/M_ADM) so typically O(1) in code units");

        // Now extraction parameters
        if (activate_extraction)
        {
            check_parameter(
                "num_extraction_radii",
                extraction_params.num_extraction_radii(),
                extraction_params.num_extraction_radii() > 0,
                "must be bigger than 0 when activate_extraction = 1");

            FOR (idir)
            {
                std::string center_name =
                    "extraction_center[" + std::to_string(idir) + "]";
                // NOLINTNEXTLINE(cppcoreguidelines-init-variables)
                double center_in_dir = extraction_params.center[idir];
                check_parameter(
                    center_name, center_in_dir,
                    (center_in_dir >= reflective_domain_lo[idir]) &&
                        (center_in_dir <= reflective_domain_hi[idir]),
                    "must be in the computational domain after "
                    "applying reflective symmetry");
                for (int iradius = 0;
                     iradius < extraction_params.num_extraction_radii();
                     ++iradius)
                {
                    std::string radius_name =
                        "extraction_radii[" + std::to_string(iradius) + "]";
                    // NOLINTNEXTLINE(cppcoreguidelines-init-variables)
                    double radius =
                        extraction_params.extraction_radii()[iradius];
                    if (idir == 0)
                    {
                        check_parameter(radius_name, radius, radius >= 0.0,
                                        "must be >= 0.0");
                    }
                    check_parameter(
                        radius_name, radius,
                        (center_in_dir - radius >=
                         reflective_domain_lo[idir]) &&
                            (center_in_dir + radius <=
                             reflective_domain_hi[idir]),
                        "extraction sphere must lie within the computational "
                        "domain after applying reflective symmetry");
                }
            }
            for (int imode = 0; imode < extraction_params.num_modes; ++imode)
            {
                auto &mode            = extraction_params.modes[imode];
                int l                 = mode.first;
                int m                 = mode.second;
                std::string mode_name = "modes[" + std::to_string(imode) + "]";
                std::string value_str = "(" + std::to_string(mode.first) +
                                        ", " + std::to_string(mode.second) +
                                        ")";
                check_parameter(
                    mode_name, value_str, (l >= 2) && (std::abs(m) <= l),
                    "l must be >= 2 and m must satisfy -l <= m <= l");
            }
        }
    }

  public:
    double sigma{}; // Kreiss-Oliger dissipation parameter

    bool nan_check{};

    double min_chi{}, min_lapse{};

    int formulation{}; // Whether to use BSSN or CCZ4

    // Gauge and damping values read from the original keys (see
    // legacy_ccz4_params_t above)
    legacy_ccz4_params_t ccz4_params{};

    bool activate_extraction{};
    spherical_extraction_params_t extraction_params{"weyl_extraction"};

    std::string data_path;
};

#endif /* SIMULATIONPARAMETERSBASE_HPP_ */
