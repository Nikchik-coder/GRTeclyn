/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef THROATTRACKER_HPP_
#define THROATTRACKER_HPP_

#include "SmallDataIO.hpp"
#include "StateVariables.hpp" // c_chi

#include <AMReX_Geometry.H>
#include <AMReX_MultiFab.H>
#include <AMReX_ParallelDescriptor.H>
#include <AMReX_Reduce.H>

#include <array>
#include <cmath>
#include <string>
#include <vector>

//! Locates each wormhole throat during the evolution and follows it.
/*!
    FIx.md Stage 2.0.  The moving-box tagger needs the CENTRE of each throat
    at regrid time, and a wormhole throat is not a puncture: PunctureTracker
    advects a particle backwards along the shift, which locates a coordinate
    singularity that these data do not have.

    What these data do have is better: in the isotropic chart each throat
    carries its own compactified far universe at its coordinate centre, where
    chi vanishes like rbar^4.  That pit is the deepest, sharpest feature in
    the entire chi field - orders of magnitude below the throat's chi ~ 0.17 -
    and it moves WITH the throat, because it is the centre of the same
    one-body solution.  So the throat centre is located as the argmin of chi
    inside a small search sphere around the last known position.  No ray
    casting, no minimal-surface search: the minimal surface is a diagnostic
    (the consumer's areal-radius extraction), the centre is what the tagger
    needs.

    Robustness of the argmin:

      * chi at the pit can clip the min_chi floor over many cells at once
        (the sigma = 0.1 stage-1 arm clipped 1e-8 in 208 samples), which
        makes a bare argmin degenerate.  The position is therefore the
        CENTROID of every in-sphere cell within a small tolerance of the
        minimum - the same pattern collapse_diagnostics uses for the
        minimum-lapse position.
      * the search sphere is centred on the previous position and the
        tracker runs every coarse step, so the sphere only has to cover one
        step of motion (v dt ~ 2e-3 for v = 0.2, dt = 0.01), not the
        trajectory.  The default radius is the throat scale a, thousands of
        times that margin, while staying far inside the innermost moving box
        (half-width tagging_L / 32 = 2 at max_level = 3, tagging_L = 64).
      * if the sphere contains no finest-level cells at all (the boxes lost
        the throat - which the moving tagger exists to prevent), the centre
        is left where it was and the row records zero cells, so the failure
        is visible in the data rather than silent.

    All MPI ranks compute the same reduced centroid, so the static centre
    array every rank feeds the tagger stays bitwise identical without any
    broadcast.  Restart caveat: the centres are seeded from the params-file
    positions, so a restart mid-flight would re-seed them there; these
    campaigns run with checkpointing disabled, and the first post-restart
    update would re-lock anyway as long as the seed is inside the sphere.

    SOLID: own module, own output file (throat_track.dat), default-off flag
    (`throat_tracking`).  Columns are positions RELATIVE TO grid_center -
    the same convention as wormhole_centerA/B - plus the pit chi and the
    number of cells the centroid averaged:

        time  xA yA zA chiA_pit nA  xB yB zB chiB_pit nB

    chi*_pit is the same "origin health" number binary_throat_diagnostics
    reports globally, now measured per throat and at the tracked position.
*/
class ThroatTracker
{
  public:
    struct params_t
    {
        bool enabled{};
        double search_radius{};
        std::array<double, AMREX_SPACEDIM> grid_center{};
    };

    //! One tracking update + one output row.  `centers` holds the ABSOLUTE
    //! coordinates of throats A and B (A first) and is updated in place;
    //! `present[i]` marks which of the two exist (b0 > 0).
    static void
    execute(const amrex::MultiFab &state_fine, const amrex::Geometry &fine_geom,
            const params_t &a_params, const std::array<bool, 2> &present,
            std::array<amrex::Real, 2 * AMREX_SPACEDIM> &centers,
            const std::string &out_dir, amrex::Real dt, amrex::Real time,
            amrex::Real restart_time, bool first_step)
    {
        const auto prob_lo = fine_geom.ProbLoArray();
        const auto dx_arr  = fine_geom.CellSizeArray();

        const amrex::Real search_r2 = static_cast<amrex::Real>(
            a_params.search_radius * a_params.search_radius);

        std::array<double, 2> pit_chi{0.0, 0.0};
        std::array<double, 2> n_cells{0.0, 0.0};

        for (int obj = 0; obj < 2; ++obj)
        {
            if (!present[obj])
            {
                continue;
            }

            const amrex::Real cx = centers[obj * AMREX_SPACEDIM + 0];
            const amrex::Real cy = centers[obj * AMREX_SPACEDIM + 1];
            const amrex::Real cz = centers[obj * AMREX_SPACEDIM + 2];

            // ---- pass 1: minimum chi inside the search sphere -------------
            amrex::ReduceOps<amrex::ReduceOpMin> min_ops;
            amrex::ReduceData<amrex::Real> min_data(min_ops);
            using MinTuple = typename decltype(min_data)::Type;

            for (amrex::MFIter mfi(state_fine, amrex::TilingIfNotGPU());
                 mfi.isValid(); ++mfi)
            {
                const amrex::Box &bx = mfi.validbox();
                const auto arr       = state_fine.const_array(mfi);
                min_ops.eval(
                    bx, min_data,
                    [=] AMREX_GPU_DEVICE(int i, int j, int k) -> MinTuple
                    {
                        const amrex::Real x =
                            prob_lo[0] + (amrex::Real(i) + 0.5) * dx_arr[0] -
                            cx;
                        const amrex::Real y =
                            prob_lo[1] + (amrex::Real(j) + 0.5) * dx_arr[1] -
                            cy;
                        const amrex::Real z =
                            prob_lo[2] + (amrex::Real(k) + 0.5) * dx_arr[2] -
                            cz;
                        if (x * x + y * y + z * z > search_r2)
                        {
                            return {amrex::Real(1.0e30)};
                        }
                        return {arr(i, j, k, c_chi)};
                    });
            }

            amrex::Real chi_min = amrex::get<0>(min_data.value());
            amrex::ParallelDescriptor::ReduceRealMin(chi_min);

            if (chi_min >= amrex::Real(1.0e29))
            {
                // No finest-level cell inside the sphere: hold position.
                pit_chi[obj] = 0.0;
                n_cells[obj] = 0.0;
                continue;
            }

            // ---- pass 2: centroid of the near-minimum cells ---------------
            // Relative tolerance: wide enough to gather a floor-clipped
            // plateau (every clipped cell equals min_chi exactly), tight
            // enough that chi ~ rbar^4 keeps the gathered set within a
            // fraction of a cell of the pit.
            const amrex::Real tol =
                amrex::max(amrex::Real(1.0e-30),
                           amrex::Real(1.0e-6) * std::abs(chi_min));

            amrex::ReduceOps<amrex::ReduceOpSum, amrex::ReduceOpSum,
                             amrex::ReduceOpSum, amrex::ReduceOpSum>
                sum_ops;
            amrex::ReduceData<amrex::Real, amrex::Real, amrex::Real,
                              amrex::Real>
                sum_data(sum_ops);
            using SumTuple = typename decltype(sum_data)::Type;

            for (amrex::MFIter mfi(state_fine, amrex::TilingIfNotGPU());
                 mfi.isValid(); ++mfi)
            {
                const amrex::Box &bx = mfi.validbox();
                const auto arr       = state_fine.const_array(mfi);
                sum_ops.eval(
                    bx, sum_data,
                    [=] AMREX_GPU_DEVICE(int i, int j, int k) -> SumTuple
                    {
                        const amrex::Real xa =
                            prob_lo[0] + (amrex::Real(i) + 0.5) * dx_arr[0];
                        const amrex::Real ya =
                            prob_lo[1] + (amrex::Real(j) + 0.5) * dx_arr[1];
                        const amrex::Real za =
                            prob_lo[2] + (amrex::Real(k) + 0.5) * dx_arr[2];
                        const amrex::Real x = xa - cx;
                        const amrex::Real y = ya - cy;
                        const amrex::Real z = za - cz;
                        if (x * x + y * y + z * z > search_r2 ||
                            arr(i, j, k, c_chi) > chi_min + tol)
                        {
                            return {0.0, 0.0, 0.0, 0.0};
                        }
                        return {xa, ya, za, 1.0};
                    });
            }

            auto [sum_x, sum_y, sum_z, count] = sum_data.value();
            amrex::ParallelDescriptor::ReduceRealSum(sum_x);
            amrex::ParallelDescriptor::ReduceRealSum(sum_y);
            amrex::ParallelDescriptor::ReduceRealSum(sum_z);
            amrex::ParallelDescriptor::ReduceRealSum(count);

            if (count > 0.0)
            {
                centers[obj * AMREX_SPACEDIM + 0] = sum_x / count;
                centers[obj * AMREX_SPACEDIM + 1] = sum_y / count;
                centers[obj * AMREX_SPACEDIM + 2] = sum_z / count;
            }
            pit_chi[obj] = static_cast<double>(chi_min);
            n_cells[obj] = static_cast<double>(count);
        }

        // ---- output row (rank 0 via SmallDataIO) --------------------------
        const std::string prefix = out_dir + "throat_track";
        SmallDataIO track_file(prefix, dt, time, restart_time,
                               SmallDataIO::APPEND, first_step);
        track_file.remove_duplicate_time_data();
        if (first_step)
        {
            track_file.write_header_line({"xA", "yA", "zA", "chiA_pit", "nA",
                                          "xB", "yB", "zB", "chiB_pit", "nB"});
        }
        std::vector<double> row;
        row.reserve(10);
        for (int obj = 0; obj < 2; ++obj)
        {
            for (int d = 0; d < AMREX_SPACEDIM; ++d)
            {
                row.push_back(centers[obj * AMREX_SPACEDIM + d] -
                              a_params.grid_center[d]);
            }
            row.push_back(pit_chi[obj]);
            row.push_back(n_cells[obj]);
        }
        track_file.write_time_data_line(row);
    }
};

#endif /* THROATTRACKER_HPP_ */
