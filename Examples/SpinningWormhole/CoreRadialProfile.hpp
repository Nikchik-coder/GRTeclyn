/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef CORERADIALPROFILE_HPP_
#define CORERADIALPROFILE_HPP_

#include "SmallDataIO.hpp"
#include "StateVariables.hpp"

#include <AMReX_Geometry.H>
#include <AMReX_GpuAtomic.H>
#include <AMReX_GpuContainers.H>
#include <AMReX_MultiFab.H>
#include <AMReX_iMultiFab.H>
#include <AMReX_ParallelDescriptor.H>
#include <AMReX_Utility.H>

#include <array>
#include <cmath>
#include <fstream>
#include <string>
#include <vector>

//! Radially binned core profile: where the collapse indicators live.
/*!
    Writes core_radial_profile.dat, behind its own default-off switch.
    collapse_diagnostics.dat reduces min(chi), max(|K|) and min(lapse) over the
    finest level and so says only when something happens; this reduces the
    same three into spherical shells about the centre, every coarse step, and
    so also says where.  It resolves features (e.g. a max|K| spike 0.25 wide on
    the throat) that the plotfile slices cannot, at a few tens of MB per run.

    Coverage: a composite reduction over the whole AMR hierarchy.  A level's
    cell contributes only where no finer level covers it (amrex::makeFineMask),
    so every cell is used once and each shell is taken at the best resolution
    that exists there.  The finest level alone follows the throats as a box,
    not a ball, and would sample the outer shells only partially.

    Each shell carries its cell count and the dx of the finest level that fed
    it.  A shell no level reaches (outside the domain) keeps n = 0 and the
    sentinels.

    The shell width is a parameter, not dx: the column count must not change
    when AMR adds or drops a level mid-run, or the header stops describing the
    file.
*/
class CoreRadialProfile
{
  public:
    struct params_t
    {
        bool enabled            = false;
        amrex::Real r_max       = 2.0;     //!< outer edge of the profile
        amrex::Real dr          = 0.03125; //!< shell width (2 dx at level 5, dx0 = 0.5)
        int interval            = 1;       //!< write every N coarse steps
        std::array<amrex::Real, 3> centre = {0.0, 0.0, 0.0};
    };

    //! Number of shells for these params; fixed for the life of the run.
    static int n_shells(const params_t &a_params)
    {
        const int n = static_cast<int>(std::floor(a_params.r_max / a_params.dr));
        return amrex::max(1, amrex::min(n, s_max_shells));
    }

    //! One entry per AMR level, coarsest first.  ``mask`` is null on the finest
    //! level and otherwise marks cells covered by the next finer one (1 =
    //! covered, skip it) so every cell of the hierarchy is counted exactly once.
    struct level_input_t
    {
        const amrex::MultiFab *state   = nullptr;
        const amrex::Geometry *geom    = nullptr;
        const amrex::iMultiFab *mask   = nullptr;
    };

    static void execute(const std::vector<level_input_t> &a_levels,
                        const params_t &a_params, const std::string &a_out_dir,
                        amrex::Real a_dt, amrex::Real a_time,
                        amrex::Real a_restart_time, bool a_first_step)
    {
        BL_PROFILE("CoreRadialProfile::execute");

        constexpr amrex::Real BIG = 1.0e30;
        const int nsh             = n_shells(a_params);
        const amrex::Real dr      = a_params.dr;
        const amrex::Real cx      = a_params.centre[0];
        const amrex::Real cy      = a_params.centre[1];
        const amrex::Real cz      = a_params.centre[2];

        // Five accumulators per shell: min chi, max |K|, min lapse, count, and
        // the dx of the finest level that fed the shell.
        const int NQ   = 5;
        const int NBIN = NQ * nsh;
        std::vector<amrex::Real> host(NBIN);
        {
            amrex::Gpu::DeviceVector<amrex::Real> d_acc(NBIN);
            amrex::Real *p = d_acc.data();
            amrex::ParallelFor(NBIN,
                               [=] AMREX_GPU_DEVICE(int n)
                               {
                                   const int q = n / nsh;
                                   p[n]        = (q == 1)   ? -BIG
                                                 : (q == 3) ? 0.0
                                                            : BIG;
                               });

            for (const auto &lev : a_levels)
            {
                if (lev.state == nullptr || lev.geom == nullptr)
                {
                    continue;
                }
                const auto prob_lo = lev.geom->ProbLoArray();
                const auto dx_arr  = lev.geom->CellSizeArray();
                const amrex::Real dx_lev = dx_arr[0];
                const amrex::iMultiFab *mask = lev.mask;

                for (amrex::MFIter mfi(*lev.state, amrex::TilingIfNotGPU());
                     mfi.isValid(); ++mfi)
                {
                    const amrex::Box &bx = mfi.validbox();
                    const auto arr       = lev.state->const_array(mfi);
                    // A default Array4 reads as "not covered" when unused.
                    const auto mrr = (mask != nullptr)
                                         ? mask->const_array(mfi)
                                         : amrex::Array4<const int>{};
                    const bool have_mask = (mask != nullptr);
                    amrex::ParallelFor(
                        bx,
                        [=] AMREX_GPU_DEVICE(int i, int j, int k)
                        {
                            // Covered by a finer level -> that level counts it.
                            if (have_mask && mrr(i, j, k) != 0)
                            {
                                return;
                            }
                            const amrex::Real x = prob_lo[0] +
                                                  (amrex::Real(i) + 0.5) *
                                                      dx_arr[0] -
                                                  cx;
                            const amrex::Real y = prob_lo[1] +
                                                  (amrex::Real(j) + 0.5) *
                                                      dx_arr[1] -
                                                  cy;
                            const amrex::Real z = prob_lo[2] +
                                                  (amrex::Real(k) + 0.5) *
                                                      dx_arr[2] -
                                                  cz;
                            const amrex::Real r =
                                std::sqrt(x * x + y * y + z * z);

                            const int ib = static_cast<int>(r / dr);
                            if (ib < 0 || ib >= nsh)
                            {
                                return;
                            }

                            const amrex::Real chi   = arr(i, j, k, c_chi);
                            const amrex::Real K     = arr(i, j, k, c_K);
                            const amrex::Real lapse = arr(i, j, k, c_lapse);

                            amrex::Gpu::Atomic::Min(&p[ib], chi);
                            amrex::Gpu::Atomic::Max(&p[nsh + ib],
                                                    amrex::Math::abs(K));
                            amrex::Gpu::Atomic::Min(&p[2 * nsh + ib], lapse);
                            amrex::Gpu::Atomic::AddNoRet(&p[3 * nsh + ib],
                                                         amrex::Real(1.0));
                            amrex::Gpu::Atomic::Min(&p[4 * nsh + ib], dx_lev);
                        });
                }
            }
            amrex::Gpu::streamSynchronize();
            amrex::Gpu::copy(amrex::Gpu::deviceToHost, d_acc.begin(),
                             d_acc.end(), host.begin());
        }

        // Cross-rank: each quantity with its own operator.
        amrex::ParallelDescriptor::ReduceRealMin(host.data(), nsh);
        amrex::ParallelDescriptor::ReduceRealMax(host.data() + nsh, nsh);
        amrex::ParallelDescriptor::ReduceRealMin(host.data() + 2 * nsh, nsh);
        amrex::ParallelDescriptor::ReduceRealSum(host.data() + 3 * nsh, nsh);
        amrex::ParallelDescriptor::ReduceRealMin(host.data() + 4 * nsh, nsh);

        // ---- Write ----------------------------------------------------------
        if (!a_out_dir.empty())
        {
            amrex::UtilCreateDirectory(a_out_dir, 0755, false);
        }
        const std::string prefix = a_out_dir + "core_radial_profile";

        // SmallDataIO takes first_step to mean "start the file over", so it
        // stays false on a restart.  A restart into a fresh run directory has
        // no file yet, so the header is decided on the file: write it when the
        // file is missing or empty.  Probed on every rank (same filesystem);
        // write_header_line is IOProcessor-guarded.
        bool write_header = a_first_step;
        if (!write_header)
        {
            std::ifstream probe(prefix + ".dat");
            write_header =
                !probe.good() ||
                probe.peek() == std::ifstream::traits_type::eof();
        }

        SmallDataIO out(prefix, a_dt, a_time, a_restart_time,
                        SmallDataIO::APPEND, a_first_step);
        out.remove_duplicate_time_data();
        if (write_header)
        {
            std::vector<std::string> cols;
            cols.reserve(NBIN);
            const char *tag[NQ] = {"chi_min", "absK_max", "lapse_min", "n",
                                   "dx"};
            for (int q = 0; q < NQ; ++q)
            {
                for (int ib = 0; ib < nsh; ++ib)
                {
                    // Shell centre, so a column name is the radius it reports.
                    const amrex::Real rc = (amrex::Real(ib) + 0.5) * dr;
                    std::string r_str     = std::to_string(rc);
                    r_str.erase(r_str.find_last_not_of('0') + 1);
                    if (!r_str.empty() && r_str.back() == '.')
                    {
                        r_str.pop_back();
                    }
                    cols.emplace_back(std::string(tag[q]) + "_r" + r_str);
                }
            }
            out.write_header_line(cols);
        }

        std::vector<double> row(NBIN);
        for (int n = 0; n < NBIN; ++n)
        {
            row[n] = static_cast<double>(host[n]);
        }
        out.write_time_data_line(row);
    }

  private:
    //! Hard cap so a mistyped dr cannot ask for a million columns.
    static constexpr int s_max_shells = 512;
};

#endif /* CORERADIALPROFILE_HPP_ */
