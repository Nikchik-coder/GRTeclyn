/* SpinningThroatDiagnostics
 * Cheap per-step monitors of ONE rotating throat, on the finest level:
 *
 *   R_eq_min   min over the +x ray of the circumferential radius
 *              sqrt(gamma_phiphi) -- the equatorial throat radius R_e(t)
 *              whose growth/decay rate the radial-mode fits read.
 *   R_pol_min  min over the +z ray of  z * sqrt(gamma_xx)  (= the meridional
 *              circumferential radius on the axis, gamma_thetatheta / r^2) --
 *              the polar throat radius R_p(t).  Static limit: equals R_eq_min.
 *   ergo_min   min over the level of  alpha^2 - gamma_ij beta^i beta^j
 *              (= -g_tt).  Negative means an ergoregion exists; its depth
 *              tracks the ergoregion's growth.
 *
 * These are coordinate-ray proxies, deliberately cheap: one reduction pass,
 * every coarse step.  Horizon-quality surfaces (MOTS, the ergosurface shape)
 * come from the consumer's spectral finder on the plotfiles instead.
 *
 * The rays are sampled from the cell columns nearest the axes (|transverse| <
 * 0.75 dx_fine), so the numbers are meaningful while the finest level covers
 * the throat region -- which the fixed-grid tagging guarantees at the centre.
 */

#ifndef SPINNINGTHROATDIAGNOSTICS_HPP_
#define SPINNINGTHROATDIAGNOSTICS_HPP_

#include "SmallDataIO.hpp"
#include "StateVariables.hpp"

#include <AMReX_Geometry.H>
#include <AMReX_MultiFab.H>
#include <AMReX_Reduce.H>

#include <array>
#include <cmath>
#include <string>
#include <vector>

struct SpinningThroatDiagnostics
{
    struct params_t
    {
        bool enabled{false};
        std::array<double, AMREX_SPACEDIM> grid_center{};
        //! Cells with r < min_radius are excluded from BOTH ray minima: the
        //! near-axis sampling columns pass within half a cell of the puncture,
        //! where z * sqrt(gamma) of an off-axis cell is finite and small and
        //! polluted the first smoke test's R_pol (0.79 instead of eta0 = 1,
        //! 2026-10-10).  The level sets 0.3 eta0 when the key is negative.
        double min_radius{0.0};
    };

    static void execute(const amrex::MultiFab &a_state,
                        const amrex::Geometry &a_geom, const params_t &a_params,
                        const std::string &a_out_dir, amrex::Real a_dt,
                        amrex::Real a_time, amrex::Real a_restart_time,
                        bool a_first_step)
    {
        const auto prob_lo = a_geom.ProbLoArray();
        const auto dx_arr  = a_geom.CellSizeArray();
        const amrex::Real dx = dx_arr[0];

        const amrex::Real cx = a_params.grid_center[0];
        const amrex::Real cy = a_params.grid_center[1];
        const amrex::Real cz = a_params.grid_center[2];
        const amrex::Real min_r2 =
            static_cast<amrex::Real>(a_params.min_radius *
                                     a_params.min_radius);

        constexpr amrex::Real BIG = 1.0e30;

        amrex::ReduceOps<amrex::ReduceOpMin, amrex::ReduceOpMin,
                         amrex::ReduceOpMin>
            reduce_ops;
        amrex::ReduceData<amrex::Real, amrex::Real, amrex::Real> reduce_data(
            reduce_ops);
        using ReduceTuple = typename decltype(reduce_data)::Type;

        for (amrex::MFIter mfi(a_state, amrex::TilingIfNotGPU()); mfi.isValid();
             ++mfi)
        {
            const amrex::Box &bx = mfi.validbox();
            const auto arr       = a_state.const_array(mfi);
            reduce_ops.eval(
                bx, reduce_data,
                [=] AMREX_GPU_DEVICE(int i, int j, int k) -> ReduceTuple
                {
                    const amrex::Real X =
                        prob_lo[0] + (amrex::Real(i) + 0.5) * dx_arr[0] - cx;
                    const amrex::Real Y =
                        prob_lo[1] + (amrex::Real(j) + 0.5) * dx_arr[1] - cy;
                    const amrex::Real Z =
                        prob_lo[2] + (amrex::Real(k) + 0.5) * dx_arr[2] - cz;

                    const amrex::Real chi = amrex::max(
                        arr(i, j, k, c_chi), amrex::Real(1.0e-10));
                    const amrex::Real h11 = arr(i, j, k, c_h11);
                    const amrex::Real h12 = arr(i, j, k, c_h12);
                    const amrex::Real h13 = arr(i, j, k, c_h13);
                    const amrex::Real h22 = arr(i, j, k, c_h22);
                    const amrex::Real h23 = arr(i, j, k, c_h23);
                    const amrex::Real h33 = arr(i, j, k, c_h33);

                    const amrex::Real r2 = X * X + Y * Y + Z * Z;

                    // Equatorial circumferential radius on the +x ray.
                    amrex::Real r_eq = BIG;
                    if (r2 > min_r2 && X > 0.25 * dx &&
                        amrex::Math::abs(Y) < 0.75 * dx &&
                        amrex::Math::abs(Z) < 0.75 * dx)
                    {
                        const amrex::Real gpp =
                            (Y * Y * h11 - 2.0 * X * Y * h12 + X * X * h22) /
                            chi;
                        r_eq = std::sqrt(amrex::max(gpp, amrex::Real(0.0)));
                    }

                    // Meridional circumferential radius on the +z ray.
                    amrex::Real r_pol = BIG;
                    if (r2 > min_r2 && Z > 0.25 * dx &&
                        amrex::Math::abs(X) < 0.75 * dx &&
                        amrex::Math::abs(Y) < 0.75 * dx)
                    {
                        r_pol = Z * std::sqrt(amrex::max(
                                        h11 / chi, amrex::Real(0.0)));
                    }

                    // -g_tt = alpha^2 - gamma_ij beta^i beta^j; negative
                    // inside an ergoregion.
                    const amrex::Real lapse = arr(i, j, k, c_lapse);
                    const amrex::Real b1    = arr(i, j, k, c_shift1);
                    const amrex::Real b2    = arr(i, j, k, c_shift2);
                    const amrex::Real b3    = arr(i, j, k, c_shift3);
                    const amrex::Real beta2 =
                        (h11 * b1 * b1 + h22 * b2 * b2 + h33 * b3 * b3 +
                         2.0 * (h12 * b1 * b2 + h13 * b1 * b3 +
                                h23 * b2 * b3)) /
                        chi;
                    const amrex::Real ergo = lapse * lapse - beta2;

                    return {r_eq, r_pol, ergo};
                });
        }

        auto reduce_vals     = reduce_data.value();
        amrex::Real r_eq_min = amrex::get<0>(reduce_vals);
        amrex::Real r_pol_min = amrex::get<1>(reduce_vals);
        amrex::Real ergo_min  = amrex::get<2>(reduce_vals);
        amrex::ParallelDescriptor::ReduceRealMin(r_eq_min);
        amrex::ParallelDescriptor::ReduceRealMin(r_pol_min);
        amrex::ParallelDescriptor::ReduceRealMin(ergo_min);

        SmallDataIO file(a_out_dir + "throat_geometry", a_dt, a_time,
                         a_restart_time, SmallDataIO::APPEND, a_first_step);
        file.remove_duplicate_time_data();
        if (a_first_step)
        {
            file.write_header_line({"R_eq_min", "R_pol_min", "ergo_min"});
        }
        file.write_time_data_line(std::vector<double>{
            static_cast<double>(r_eq_min), static_cast<double>(r_pol_min),
            static_cast<double>(ergo_min)});
    }
};

#endif /* SPINNINGTHROATDIAGNOSTICS_HPP_ */
