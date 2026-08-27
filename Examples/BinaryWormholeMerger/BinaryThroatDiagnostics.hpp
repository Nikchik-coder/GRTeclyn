/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef BINARYTHROATDIAGNOSTICS_HPP_
#define BINARYTHROATDIAGNOSTICS_HPP_

#include "SmallDataIO.hpp"
#include "StateVariables.hpp"

#include <AMReX_Geometry.H>
#include <AMReX_MultiFab.H>
#include <AMReX_ParallelDescriptor.H>
#include <AMReX_Reduce.H>
#include <AMReX_Utility.H>

#include <array>
#include <cmath>
#include <string>
#include <vector>

//! Two-centre diagnostics for a binary wormhole run.
/*!
    Deliberately a SEPARATE module writing its OWN file
    (binary_throat_diagnostics.dat), behind its own default-off switch.  The
    single-centre collapse_diagnostics.dat contract is left untouched so the
    existing single-throat analysis scripts keep working unchanged.

    What it measures, per coarse step, on the finest level:

      * The location of each throat, taken as the barycentre of the cells where
        chi attains its minimum, computed SEPARATELY in the two half-spaces
        either side of a plane normal to the separation axis.  For a head-on
        run along z this is exact by symmetry; for an orbital run it tracks the
        throats correctly as long as they have not yet crossed the plane.
      * The coordinate separation of those two barycentres.
      * min(chi) and min(lapse) in each half-space - the per-throat collapse
        indicators.
      * The outgoing-null-expansion proxy
            theta_+ = 2 sqrt(chi)/r - (d chi/dr)/sqrt(chi) + A_rr - (2/3) K
        about EACH throat and about the midpoint between them.  The midpoint
        scan is the common-horizon detector: theta_+ <= 0 on a sphere that
        encloses both throats is the signature of fusion into a single trapped
        region.

    IMPORTANT - the min_radius parameter.  For an Ellis-Bronnikov throat the
    coordinate origin r -> 0 is the OTHER asymptotic infinity, not a centre, and
    there theta_+ -> -8 r / b^2 < 0 identically.  A naive scan therefore always
    reports a "trapped surface" hugging each throat, which is a coordinate
    artefact of the inversion, not a horizon.  min_radius excludes that region;
    set it to at least the isotropic throat radius b/2, and for the
    common-horizon scan to something comparable to half the initial separation.
*/
struct BinaryThroatDiagnostics
{
    struct params_t
    {
        bool enabled{false};
        //! Grid centre, so that all radii below are measured from the physics
        //! centre and not from the domain corner.
        std::array<double, AMREX_SPACEDIM> grid_center{};
        //! Separation axis: 0 = x, 1 = y, 2 = z.
        int axis{2};
        //! Coordinate of the dividing plane along that axis, RELATIVE to
        //! grid_center.  Zero for the symmetric configuration.
        double split_coord{0.0};
        //! Radii below this are excluded from every theta_+ scan (see above).
        double min_radius{0.0};
    };

    // NOLINTNEXTLINE(readability-function-cognitive-complexity)
    static void execute(const amrex::MultiFab &a_state,
                        const amrex::Geometry &a_geom, const params_t &a_params,
                        const std::string &a_out_dir, double a_dt,
                        double a_time, double a_restart_time, bool a_first_step)
    {
        BL_PROFILE("BinaryThroatDiagnostics::execute");

        constexpr amrex::Real BIG = 1.0e30;

        const auto prob_lo = a_geom.ProbLoArray();
        const auto dx_arr  = a_geom.CellSizeArray();

        const amrex::Real cx        = a_params.grid_center[0];
        const amrex::Real cy        = a_params.grid_center[1];
        const amrex::Real cz        = a_params.grid_center[2];
        const int axis              = a_params.axis;
        const amrex::Real split     = a_params.split_coord;
        const amrex::Real min_r     = a_params.min_radius;
        const amrex::Real min_r_sq  = min_r * min_r;

        // ---- Pass 1: per-half-space minima of chi and lapse -----------------
        amrex::Real min_chi_A = BIG;
        amrex::Real min_chi_B = BIG;
        amrex::Real min_lap_A = BIG;
        amrex::Real min_lap_B = BIG;
        {
            amrex::ReduceOps<amrex::ReduceOpMin, amrex::ReduceOpMin,
                             amrex::ReduceOpMin, amrex::ReduceOpMin>
                ops;
            amrex::ReduceData<amrex::Real, amrex::Real, amrex::Real, amrex::Real>
                data(ops);
            using Tuple = typename decltype(data)::Type;

            for (amrex::MFIter mfi(a_state, amrex::TilingIfNotGPU());
                 mfi.isValid(); ++mfi)
            {
                const amrex::Box &bx = mfi.validbox();
                const auto arr       = a_state.const_array(mfi);
                ops.eval(bx, data,
                         [=] AMREX_GPU_DEVICE(int i, int j, int k) -> Tuple
                         {
                             const amrex::Real p[3] = {
                                 prob_lo[0] + (amrex::Real(i) + 0.5) * dx_arr[0] - cx,
                                 prob_lo[1] + (amrex::Real(j) + 0.5) * dx_arr[1] - cy,
                                 prob_lo[2] + (amrex::Real(k) + 0.5) * dx_arr[2] - cz};
                             const bool side_A = (p[axis] >= split);

                             const amrex::Real chi   = arr(i, j, k, c_chi);
                             const amrex::Real lapse = arr(i, j, k, c_lapse);

                             return {side_A ? chi : BIG, side_A ? BIG : chi,
                                     side_A ? lapse : BIG, side_A ? BIG : lapse};
                         });
            }
            const auto vals = data.value();
            min_chi_A       = amrex::get<0>(vals);
            min_chi_B       = amrex::get<1>(vals);
            min_lap_A       = amrex::get<2>(vals);
            min_lap_B       = amrex::get<3>(vals);
            amrex::ParallelDescriptor::ReduceRealMin(min_chi_A);
            amrex::ParallelDescriptor::ReduceRealMin(min_chi_B);
            amrex::ParallelDescriptor::ReduceRealMin(min_lap_A);
            amrex::ParallelDescriptor::ReduceRealMin(min_lap_B);
        }

        // ---- Pass 2: barycentre of the chi minimum in each half-space -------
        amrex::Real posA[3] = {0.0, 0.0, 0.0};
        amrex::Real posB[3] = {0.0, 0.0, 0.0};
        {
            const amrex::Real tolA = chi_tolerance(min_chi_A);
            const amrex::Real tolB = chi_tolerance(min_chi_B);

            amrex::ReduceOps<amrex::ReduceOpSum, amrex::ReduceOpSum,
                             amrex::ReduceOpSum, amrex::ReduceOpSum,
                             amrex::ReduceOpSum, amrex::ReduceOpSum,
                             amrex::ReduceOpSum, amrex::ReduceOpSum>
                ops;
            amrex::ReduceData<amrex::Real, amrex::Real, amrex::Real, amrex::Real,
                              amrex::Real, amrex::Real, amrex::Real, amrex::Real>
                data(ops);
            using Tuple = typename decltype(data)::Type;

            for (amrex::MFIter mfi(a_state, amrex::TilingIfNotGPU());
                 mfi.isValid(); ++mfi)
            {
                const amrex::Box &bx = mfi.validbox();
                const auto arr       = a_state.const_array(mfi);
                ops.eval(bx, data,
                         [=] AMREX_GPU_DEVICE(int i, int j, int k) -> Tuple
                         {
                             const amrex::Real px =
                                 prob_lo[0] + (amrex::Real(i) + 0.5) * dx_arr[0] - cx;
                             const amrex::Real py =
                                 prob_lo[1] + (amrex::Real(j) + 0.5) * dx_arr[1] - cy;
                             const amrex::Real pz =
                                 prob_lo[2] + (amrex::Real(k) + 0.5) * dx_arr[2] - cz;
                             const amrex::Real p[3] = {px, py, pz};
                             const bool side_A      = (p[axis] >= split);

                             const amrex::Real chi = arr(i, j, k, c_chi);

                             const bool hitA =
                                 side_A &&
                                 (amrex::Math::abs(chi - min_chi_A) <= tolA);
                             const bool hitB =
                                 (!side_A) &&
                                 (amrex::Math::abs(chi - min_chi_B) <= tolB);

                             return {hitA ? px : 0.0,  hitA ? py : 0.0,
                                     hitA ? pz : 0.0,  hitA ? 1.0 : 0.0,
                                     hitB ? px : 0.0,  hitB ? py : 0.0,
                                     hitB ? pz : 0.0,  hitB ? 1.0 : 0.0};
                         });
            }
            auto vals             = data.value();
            amrex::Real sums[8]   = {amrex::get<0>(vals), amrex::get<1>(vals),
                                     amrex::get<2>(vals), amrex::get<3>(vals),
                                     amrex::get<4>(vals), amrex::get<5>(vals),
                                     amrex::get<6>(vals), amrex::get<7>(vals)};
            amrex::ParallelDescriptor::ReduceRealSum(sums, 8);

            const amrex::Real nA = sums[3];
            const amrex::Real nB = sums[7];
            for (int d = 0; d < 3; ++d)
            {
                posA[d] = (nA > 0.0) ? sums[d] / nA : 0.0;
                posB[d] = (nB > 0.0) ? sums[4 + d] / nB : 0.0;
            }
        }

        const amrex::Real sep =
            std::sqrt((posA[0] - posB[0]) * (posA[0] - posB[0]) +
                      (posA[1] - posB[1]) * (posA[1] - posB[1]) +
                      (posA[2] - posB[2]) * (posA[2] - posB[2]));

        const amrex::Real posC[3] = {0.5 * (posA[0] + posB[0]),
                                     0.5 * (posA[1] + posB[1]),
                                     0.5 * (posA[2] + posB[2])};

        // ---- Pass 3: theta_+ about throat A, throat B and their midpoint ----
        amrex::Real theta_A = BIG, theta_B = BIG, theta_C = BIG;
        amrex::Real ah_r_A = 0.0, ah_r_B = 0.0, ah_r_C = 0.0;
        {
            const amrex::Real aX = posA[0], aY = posA[1], aZ = posA[2];
            const amrex::Real bX = posB[0], bY = posB[1], bZ = posB[2];
            const amrex::Real mX = posC[0], mY = posC[1], mZ = posC[2];

            amrex::ReduceOps<amrex::ReduceOpMin, amrex::ReduceOpMax,
                             amrex::ReduceOpMin, amrex::ReduceOpMax,
                             amrex::ReduceOpMin, amrex::ReduceOpMax>
                ops;
            amrex::ReduceData<amrex::Real, amrex::Real, amrex::Real, amrex::Real,
                              amrex::Real, amrex::Real>
                data(ops);
            using Tuple = typename decltype(data)::Type;

            for (amrex::MFIter mfi(a_state, amrex::TilingIfNotGPU());
                 mfi.isValid(); ++mfi)
            {
                const amrex::Box &bx = mfi.validbox();
                const auto arr       = a_state.const_array(mfi);
                ops.eval(
                    bx, data,
                    [=] AMREX_GPU_DEVICE(int i, int j, int k) -> Tuple
                    {
                        const amrex::Real px =
                            prob_lo[0] + (amrex::Real(i) + 0.5) * dx_arr[0] - cx;
                        const amrex::Real py =
                            prob_lo[1] + (amrex::Real(j) + 0.5) * dx_arr[1] - cy;
                        const amrex::Real pz =
                            prob_lo[2] + (amrex::Real(k) + 0.5) * dx_arr[2] - cz;

                        // The radial derivative of chi is centre independent;
                        // only the direction cosines change, so compute the
                        // Cartesian gradient once.
                        const amrex::Real dchi_dx =
                            (arr(i + 1, j, k, c_chi) - arr(i - 1, j, k, c_chi)) /
                            (2.0 * dx_arr[0]);
                        const amrex::Real dchi_dy =
                            (arr(i, j + 1, k, c_chi) - arr(i, j - 1, k, c_chi)) /
                            (2.0 * dx_arr[1]);
                        const amrex::Real dchi_dz =
                            (arr(i, j, k + 1, c_chi) - arr(i, j, k - 1, c_chi)) /
                            (2.0 * dx_arr[2]);

                        const amrex::Real chi = arr(i, j, k, c_chi);
                        const amrex::Real K   = arr(i, j, k, c_K);
                        const amrex::Real A11 = arr(i, j, k, c_A11);
                        const amrex::Real A22 = arr(i, j, k, c_A22);
                        const amrex::Real A33 = arr(i, j, k, c_A33);
                        const amrex::Real A12 = arr(i, j, k, c_A12);
                        const amrex::Real A13 = arr(i, j, k, c_A13);
                        const amrex::Real A23 = arr(i, j, k, c_A23);
                        const amrex::Real sqrt_chi =
                            std::sqrt(amrex::max(chi, amrex::Real(1.0e-20)));

                        amrex::Real th[3]{BIG, BIG, BIG};
                        amrex::Real ah[3]{0.0, 0.0, 0.0};

                        const amrex::Real ox[3] = {px - aX, px - bX, px - mX};
                        const amrex::Real oy[3] = {py - aY, py - bY, py - mY};
                        const amrex::Real oz[3] = {pz - aZ, pz - bZ, pz - mZ};

                        for (int c = 0; c < 3; ++c)
                        {
                            const amrex::Real X  = ox[c];
                            const amrex::Real Y  = oy[c];
                            const amrex::Real Z  = oz[c];
                            const amrex::Real r2 = X * X + Y * Y + Z * Z;
                            if (r2 <= min_r_sq || r2 <= 1.0e-12)
                            {
                                continue;
                            }
                            const amrex::Real r = std::sqrt(r2);

                            const amrex::Real Arr =
                                (A11 * X * X + A22 * Y * Y + A33 * Z * Z +
                                 2.0 * A12 * X * Y + 2.0 * A13 * X * Z +
                                 2.0 * A23 * Y * Z) /
                                r2;
                            const amrex::Real dchi_dr =
                                (X * dchi_dx + Y * dchi_dy + Z * dchi_dz) / r;

                            const amrex::Real theta_plus =
                                2.0 * sqrt_chi / r - dchi_dr / sqrt_chi + Arr -
                                (2.0 / 3.0) * K;

                            th[c] = theta_plus;
                            ah[c] = (theta_plus <= 0.0) ? r : amrex::Real(0.0);
                        }

                        return {th[0], ah[0], th[1], ah[1], th[2], ah[2]};
                    });
            }
            const auto vals = data.value();
            theta_A         = amrex::get<0>(vals);
            ah_r_A          = amrex::get<1>(vals);
            theta_B         = amrex::get<2>(vals);
            ah_r_B          = amrex::get<3>(vals);
            theta_C         = amrex::get<4>(vals);
            ah_r_C          = amrex::get<5>(vals);
            amrex::ParallelDescriptor::ReduceRealMin(theta_A);
            amrex::ParallelDescriptor::ReduceRealMax(ah_r_A);
            amrex::ParallelDescriptor::ReduceRealMin(theta_B);
            amrex::ParallelDescriptor::ReduceRealMax(ah_r_B);
            amrex::ParallelDescriptor::ReduceRealMin(theta_C);
            amrex::ParallelDescriptor::ReduceRealMax(ah_r_C);
        }

        // ---- Write ----------------------------------------------------------
        if (!a_out_dir.empty())
        {
            amrex::UtilCreateDirectory(a_out_dir, 0755, false);
        }
        const std::string prefix = a_out_dir + "binary_throat_diagnostics";

        SmallDataIO out(prefix, a_dt, a_time, a_restart_time,
                        SmallDataIO::APPEND, a_first_step);
        out.remove_duplicate_time_data();
        if (a_first_step)
        {
            out.write_header_line({"separation", "xA", "yA", "zA", "chiA_min",
                                   "lapseA_min", "xB", "yB", "zB", "chiB_min",
                                   "lapseB_min", "theta_A", "ah_r_A", "theta_B",
                                   "ah_r_B", "theta_common", "ah_r_common"});
        }
        out.write_time_data_line(std::vector<double>{
            static_cast<double>(sep), static_cast<double>(posA[0]),
            static_cast<double>(posA[1]), static_cast<double>(posA[2]),
            static_cast<double>(min_chi_A), static_cast<double>(min_lap_A),
            static_cast<double>(posB[0]), static_cast<double>(posB[1]),
            static_cast<double>(posB[2]), static_cast<double>(min_chi_B),
            static_cast<double>(min_lap_B), static_cast<double>(theta_A),
            static_cast<double>(ah_r_A), static_cast<double>(theta_B),
            static_cast<double>(ah_r_B), static_cast<double>(theta_C),
            static_cast<double>(ah_r_C)});
    }

  private:
    //! Tolerance for "is this cell at the minimum of chi", scaled to the value
    //! so that it works both at chi ~ 1 and deep in a collapsing throat.
    static amrex::Real chi_tolerance(amrex::Real a_min_chi)
    {
        return amrex::max(amrex::Real(1.0e-14),
                          amrex::Real(1.0e-10) * amrex::Math::abs(a_min_chi));
    }
};

#endif /* BINARYTHROATDIAGNOSTICS_HPP_ */
