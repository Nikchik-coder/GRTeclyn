/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef CELLQUARTICEXACT_HPP_
#define CELLQUARTICEXACT_HPP_

#include <AMReX_Array.H>
#include <AMReX_FArrayBox.H>
#include <AMReX_Interpolater.H>
#include <AMReX_ParmParse.H>

static_assert(AMREX_SPACEDIM == 3, "CellQuarticExact is written for 3D");

//! AMReX's CellQuartic (cell-centred quartic, refinement ratio 2) with exact
//! weights.  amrex::cell_quartic_interp stores its weights rounded to eight
//! decimals (0.01708984, -0.12304688, 0.92285156, 0.20507812, -0.02197266),
//! which sum to 1 - 2e-8: each of its three sweeps scales the data by that
//! sum, so every fine ghost value it fills at a coarse-fine boundary is
//! 1 - 6e-8 times the field, constants included.  A fixed jump of 6e-8
//! under a second derivative is 6e-8 / h^2, so the constraint violation in
//! the layer along every fine level's boundary grows with resolution (the
//! level's L2 at order -1.5 on the spinning wormhole's t = 0 data).  The exact
//! weights are the Lagrange weights of the five coarse cells at the fine
//! cell centre, (35, -252, 1890, 420, -45) / 2048, exact in binary floating
//! point.  Stencils, sweep order and coarse box are AMReX's.
namespace cell_quartic_exact
{
// c(m): weight of coarse cell ii + m for the child at +1/4 of cell ii; the
// child at -1/4 reads it mirrored, c(-m).
AMREX_GPU_HOST_DEVICE AMREX_FORCE_INLINE amrex::Real
weight(int m) noexcept
{
    constexpr amrex::Array1D<amrex::Real, -2, 2> c = {
        amrex::Real(35.0 / 2048.0), amrex::Real(-252.0 / 2048.0),
        amrex::Real(1890.0 / 2048.0), amrex::Real(420.0 / 2048.0),
        amrex::Real(-45.0 / 2048.0)};
    return c(m);
}

AMREX_GPU_HOST_DEVICE AMREX_FORCE_INLINE void
interp_x(int i, int j, int k, int n, amrex::Array4<amrex::Real> const &fine,
         amrex::Array4<amrex::Real const> const &crse) noexcept
{
    const int ii = amrex::coarsen(i, 2);
    const int s  = 2 * (i - ii * 2) - 1; // -1 for the left child, +1 right
    fine(i, j, k, n) = weight(-2 * s) * crse(ii - 2, j, k, n) +
                       weight(-s) * crse(ii - 1, j, k, n) +
                       weight(0) * crse(ii, j, k, n) +
                       weight(s) * crse(ii + 1, j, k, n) +
                       weight(2 * s) * crse(ii + 2, j, k, n);
}

AMREX_GPU_HOST_DEVICE AMREX_FORCE_INLINE void
interp_y(int i, int j, int k, int n, amrex::Array4<amrex::Real> const &fine,
         amrex::Array4<amrex::Real const> const &crse) noexcept
{
    const int jj = amrex::coarsen(j, 2);
    const int s  = 2 * (j - jj * 2) - 1;
    fine(i, j, k, n) = weight(-2 * s) * crse(i, jj - 2, k, n) +
                       weight(-s) * crse(i, jj - 1, k, n) +
                       weight(0) * crse(i, jj, k, n) +
                       weight(s) * crse(i, jj + 1, k, n) +
                       weight(2 * s) * crse(i, jj + 2, k, n);
}

AMREX_GPU_HOST_DEVICE AMREX_FORCE_INLINE void
interp_z(int i, int j, int k, int n, amrex::Array4<amrex::Real> const &fine,
         amrex::Array4<amrex::Real const> const &crse) noexcept
{
    const int kk = amrex::coarsen(k, 2);
    const int s  = 2 * (k - kk * 2) - 1;
    fine(i, j, k, n) = weight(-2 * s) * crse(i, j, kk - 2, n) +
                       weight(-s) * crse(i, j, kk - 1, n) +
                       weight(0) * crse(i, j, kk, n) +
                       weight(s) * crse(i, j, kk + 1, n) +
                       weight(2 * s) * crse(i, j, kk + 2, n);
}
} // namespace cell_quartic_exact

class CellQuarticExact : public amrex::Interpolater
{
  public:
    amrex::Box CoarseBox(const amrex::Box &fine, int ratio) override
    {
        amrex::Box crse = amrex::coarsen(fine, ratio);
        crse.grow(2);
        return crse;
    }

    amrex::Box CoarseBox(const amrex::Box &fine,
                         const amrex::IntVect &ratio) override
    {
        amrex::Box crse = amrex::coarsen(fine, ratio);
        crse.grow(2);
        return crse;
    }

    void interp(const amrex::FArrayBox &crse, int crse_comp,
                amrex::FArrayBox &fine, int fine_comp, int ncomp,
                const amrex::Box &fine_region, const amrex::IntVect &ratio,
                const amrex::Geometry & /*crse_geom*/,
                const amrex::Geometry & /*fine_geom*/,
                amrex::Vector<amrex::BCRec> const & /*bcr*/,
                int /*actual_comp*/, int /*actual_state*/,
                amrex::RunOn runon) override
    {
        BL_PROFILE("CellQuarticExact::interp()");
        amrex::ignore_unused(ratio);
        AMREX_ASSERT(ratio == 2);

        const amrex::Box target_fine_region = fine_region & fine.box();

        const bool run_on_gpu =
            (runon == amrex::RunOn::Gpu && amrex::Gpu::inLaunchRegion());

        amrex::Array4<amrex::Real const> const &crsearr =
            crse.const_array(crse_comp);
        amrex::Array4<amrex::Real> const &finearr = fine.array(fine_comp);

        // z on the coarse x-y columns, then y, then x, as AMReX's CellQuartic
        amrex::Box bz =
            amrex::coarsen(target_fine_region, amrex::IntVect(2, 2, 1));
        bz.grow(amrex::IntVect(2, 2, 0));
        amrex::FArrayBox tmpz(bz, ncomp);
#ifdef AMREX_USE_GPU
        amrex::Elixir tmpz_eli;
        if (run_on_gpu)
        {
            tmpz_eli = tmpz.elixir();
        }
#endif
        amrex::Array4<amrex::Real> const &tmpzarr = tmpz.array();
        parallel_for(run_on_gpu, bz, ncomp,
                     [=] AMREX_GPU_HOST_DEVICE(int i, int j, int k,
                                               int n) noexcept {
                         cell_quartic_exact::interp_z(i, j, k, n, tmpzarr,
                                                      crsearr);
                     });

        amrex::Box by =
            amrex::coarsen(target_fine_region, amrex::IntVect(2, 1, 1));
        by.grow(amrex::IntVect(2, 0, 0));
        amrex::FArrayBox tmpy(by, ncomp);
#ifdef AMREX_USE_GPU
        amrex::Elixir tmpy_eli;
        if (run_on_gpu)
        {
            tmpy_eli = tmpy.elixir();
        }
#endif
        amrex::Array4<amrex::Real> const &tmpyarr = tmpy.array();
        amrex::Array4<amrex::Real const> const tmpzc = tmpz.const_array();
        parallel_for(run_on_gpu, by, ncomp,
                     [=] AMREX_GPU_HOST_DEVICE(int i, int j, int k,
                                               int n) noexcept {
                         cell_quartic_exact::interp_y(i, j, k, n, tmpyarr,
                                                      tmpzc);
                     });

        amrex::Array4<amrex::Real const> const tmpyc = tmpy.const_array();
        parallel_for(run_on_gpu, target_fine_region, ncomp,
                     [=] AMREX_GPU_HOST_DEVICE(int i, int j, int k,
                                               int n) noexcept {
                         cell_quartic_exact::interp_x(i, j, k, n, finearr,
                                                      tmpyc);
                     });
    }

  private:
    // What AMREX_HOST_DEVICE_PARALLEL_FOR_4D_FLAG does; the macro names
    // RunOn and Gpu unqualified, so it only compiles inside namespace amrex.
    template <class F>
    static void parallel_for(bool a_on_gpu, const amrex::Box &a_box,
                             int a_ncomp, F const &a_f)
    {
        if (a_on_gpu)
        {
            amrex::ParallelFor(a_box, a_ncomp, a_f);
        }
        else
        {
            amrex::LoopConcurrentOnCpu(a_box, a_ncomp, a_f);
        }
    }
};

//! The one instance, as AMReX's global interpolaters.
inline CellQuarticExact cell_quartic_exact_interp;

//! The cell-centred coarse-to-fine interpolater of the evolved state and of
//! every derived plot variable: the exact-weight quartic when the params set
//! exact_quartic_interp = 1, AMReX's own (rounded weights, the default)
//! otherwise.
inline amrex::Interpolater *grteclyn_cell_interp()
{
    static const bool exact = []
    {
        int flag = 0;
        amrex::ParmParse pp;
        pp.query("exact_quartic_interp", flag);
        return flag != 0;
    }();
    if (exact)
    {
        return &cell_quartic_exact_interp;
    }
    return &amrex::cell_quartic_interp;
}

#endif /* CELLQUARTICEXACT_HPP_ */
