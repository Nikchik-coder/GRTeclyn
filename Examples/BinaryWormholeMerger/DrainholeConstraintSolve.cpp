/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#include "DrainholeConstraintSolve.hpp"

#include <AMReX_MLABecLaplacian.H>
#include <AMReX_MLMG.H>
#include <AMReX_MultiFabUtil.H>
#include <AMReX_Reduce.H>

#include <cmath>

namespace
{
//! Robin coefficients a w + b dw/dn = f for a w ~ M/r tail: on a face with
//! outward normal n, dw/dn = -(n.x / r^2) w, so a = |n.x| / r^2, b = 1, f = 0.
//! AMReX reads them from the ghost cells outside the domain, taken to lie on
//! the face itself; a corner cell takes the larger of its two normals.
void fill_robin(const amrex::Geometry &a_geom,
                const std::array<double, AMREX_SPACEDIM> &a_center,
                amrex::MultiFab &a_ra, amrex::MultiFab &a_rb,
                amrex::MultiFab &a_rf)
{
    const amrex::Box domain = a_geom.Domain();
    const auto dlo          = amrex::lbound(domain);
    const auto dhi          = amrex::ubound(domain);
    const auto plo          = a_geom.ProbLoArray();
    const auto dx           = a_geom.CellSizeArray();
    const amrex::Real cx    = a_center[0];
    const amrex::Real cy    = a_center[1];
    const amrex::Real cz    = a_center[2];

    const auto &ra = a_ra.arrays();
    const auto &rb = a_rb.arrays();
    const auto &rf = a_rf.arrays();
    amrex::ParallelFor(
        a_ra, a_ra.nGrowVect(),
        [=] AMREX_GPU_DEVICE(int box_no, int i, int j, int k) noexcept
        {
            const int iv[3]     = {i, j, k};
            const int lo[3]     = {dlo.x, dlo.y, dlo.z};
            const int hi[3]     = {dhi.x, dhi.y, dhi.z};
            const amrex::Real c[3] = {cx, cy, cz};
            amrex::Real x[3];
            amrex::Real nx = 0.0;
            for (int d = 0; d < 3; ++d)
            {
                bool outside = true;
                amrex::Real xd;
                if (iv[d] < lo[d])
                {
                    xd = plo[d] + lo[d] * dx[d];
                }
                else if (iv[d] > hi[d])
                {
                    xd = plo[d] + (hi[d] + 1) * dx[d];
                }
                else
                {
                    xd      = plo[d] + (iv[d] + 0.5) * dx[d];
                    outside = false;
                }
                x[d] = xd - c[d];
                if (outside)
                {
                    nx = amrex::max(nx, amrex::Math::abs(x[d]));
                }
            }
            const amrex::Real r2 = x[0] * x[0] + x[1] * x[1] + x[2] * x[2];
            ra[box_no](i, j, k) = (r2 > 0.0) ? nx / r2 : 0.0;
            rb[box_no](i, j, k) = 1.0;
            rf[box_no](i, j, k) = 0.0;
        });
}
} // namespace

// NOLINTNEXTLINE(readability-function-cognitive-complexity)
ConstraintSolveReport
solve_drainhole_constraint(amrex::Amr &a_amr,
                           const BinaryWormholeInitialData::params_t &a_id,
                           const ConstraintSolveParams &a_params,
                           amrex::Vector<amrex::MultiFab> &a_w)
{
    BL_PROFILE("solve_drainhole_constraint");
    using amrex::MultiFab;

    ConstraintSolveReport report;
    report.c_A = a_id.solve_puncture_A;
    report.c_B = a_id.solve_puncture_B;
    if (a_id.b0_A > 0.0)
    {
        report.c_superposed_A =
            BinaryWormholeInitialData::superposed_puncture_coefficient(a_id, 0);
    }
    if (a_id.b0_B > 0.0)
    {
        report.c_superposed_B =
            BinaryWormholeInitialData::superposed_puncture_coefficient(a_id, 1);
    }

    const int nlev = a_amr.finestLevel() + 1;
    amrex::Vector<amrex::Geometry> geom(nlev);
    amrex::Vector<amrex::BoxArray> grids(nlev);
    amrex::Vector<amrex::DistributionMapping> dmap(nlev);
    for (int lev = 0; lev < nlev; ++lev)
    {
        geom[lev]  = a_amr.Geom(lev);
        grids[lev] = a_amr.boxArray(lev);
        dmap[lev]  = a_amr.DistributionMap(lev);
    }

    // Is the problem nonlinear?  Only a Bowen-York term makes it so.
    bool has_momentum = false;
    for (int d = 0; d < AMREX_SPACEDIM; ++d)
    {
        has_momentum = has_momentum ||
                       (a_id.b0_A > 0.0 && a_id.momentumA[d] != 0.0) ||
                       (a_id.b0_B > 0.0 && a_id.momentumB[d] != 0.0);
    }

    // ---- Background fields, fixed through the Newton iteration ------------
    amrex::Vector<MultiFab> psi_bg(nlev), res_bg(nlev), pot(nlev), aa(nlev);
    amrex::Vector<MultiFab> acoef(nlev), rhs(nlev), w_old(nlev);
    amrex::Vector<MultiFab> robin_a(nlev), robin_b(nlev), robin_f(nlev);
    amrex::Vector<amrex::Array<MultiFab, AMREX_SPACEDIM>> bcoef(nlev);
    a_w.clear();
    a_w.resize(nlev);

    for (int lev = 0; lev < nlev; ++lev)
    {
        psi_bg[lev].define(grids[lev], dmap[lev], 1, 0);
        res_bg[lev].define(grids[lev], dmap[lev], 1, 0);
        pot[lev].define(grids[lev], dmap[lev], 1, 0);
        aa[lev].define(grids[lev], dmap[lev], 1, 0);
        acoef[lev].define(grids[lev], dmap[lev], 1, 0);
        rhs[lev].define(grids[lev], dmap[lev], 1, 0);
        w_old[lev].define(grids[lev], dmap[lev], 1, 0);
        a_w[lev].define(grids[lev], dmap[lev], 1, 1);
        a_w[lev].setVal(0.0);
        robin_a[lev].define(grids[lev], dmap[lev], 1, 1);
        robin_b[lev].define(grids[lev], dmap[lev], 1, 1);
        robin_f[lev].define(grids[lev], dmap[lev], 1, 1);
        for (int idim = 0; idim < AMREX_SPACEDIM; ++idim)
        {
            bcoef[lev][idim].define(
                amrex::convert(grids[lev],
                               amrex::IntVect::TheDimensionVector(idim)),
                dmap[lev], 1, 0);
            bcoef[lev][idim].setVal(1.0);
        }

        const BinaryWormholeInitialData background(a_id,
                                                   geom[lev].CellSize(0));
        const auto &p_arr = psi_bg[lev].arrays();
        const auto &r_arr = res_bg[lev].arrays();
        const auto &v_arr = pot[lev].arrays();
        const auto &a_arr = aa[lev].arrays();
        amrex::ParallelFor(
            psi_bg[lev],
            [=] AMREX_GPU_DEVICE(int box_no, int i, int j, int k) noexcept
            {
                amrex::Real P, L, V, AA;
                background.constraint_background(i, j, k, P, L, V, AA);
                p_arr[box_no](i, j, k) = P;
                r_arr[box_no](i, j, k) = L - V * P;
                v_arr[box_no](i, j, k) = V;
                a_arr[box_no](i, j, k) = AA;
            });

        fill_robin(geom[lev], a_id.grid_center, robin_a[lev], robin_b[lev],
                   robin_f[lev]);
    }
    amrex::Gpu::streamSynchronize();

    // ---- The operator (A - lap) w = f, Robin on every face ----------------
    amrex::MLABecLaplacian mlabec(geom, grids, dmap, amrex::LPInfo());
    mlabec.setDomainBC(
        {AMREX_D_DECL(amrex::LinOpBCType::Robin, amrex::LinOpBCType::Robin,
                      amrex::LinOpBCType::Robin)},
        {AMREX_D_DECL(amrex::LinOpBCType::Robin, amrex::LinOpBCType::Robin,
                      amrex::LinOpBCType::Robin)});
    for (int lev = 0; lev < nlev; ++lev)
    {
        mlabec.setLevelBC(lev, &a_w[lev], &robin_a[lev], &robin_b[lev],
                          &robin_f[lev]);
    }
    for (int lev = 0; lev < nlev; ++lev)
    {
        mlabec.setBCoeffs(lev, amrex::GetArrOfConstPtrs(bcoef[lev]));
    }

    // ---- Newton on the Bowen-York term (one pass when it is absent) -------
    for (int it = 0; it < a_params.max_newton; ++it)
    {
        // The Robin terms are folded into the A coefficients in place at each
        // solve, so a reused operator needs its scalars and A coefficients
        // set again every pass (AMReX asserts on this).  B is only read.
        mlabec.setScalars(1.0, 1.0);
        for (int lev = 0; lev < nlev; ++lev)
        {
            const auto &p_arr = psi_bg[lev].const_arrays();
            const auto &r_arr = res_bg[lev].const_arrays();
            const auto &v_arr = pot[lev].const_arrays();
            const auto &a_arr = aa[lev].const_arrays();
            const auto &w_arr = a_w[lev].const_arrays();
            const auto &A_arr = acoef[lev].arrays();
            const auto &f_arr = rhs[lev].arrays();
            amrex::ParallelFor(
                acoef[lev],
                [=] AMREX_GPU_DEVICE(int box_no, int i, int j, int k) noexcept
                {
                    const amrex::Real w   = w_arr[box_no](i, j, k);
                    const amrex::Real Psi = p_arr[box_no](i, j, k) + w;
                    const amrex::Real AA  = a_arr[box_no](i, j, k);
                    amrex::Real ip7 = 0.0, ip8 = 0.0;
                    if (AA != 0.0)
                    {
                        const amrex::Real ip  = 1.0 / Psi;
                        const amrex::Real ip2 = ip * ip;
                        const amrex::Real ip4 = ip2 * ip2;
                        ip7                   = ip4 * ip2 * ip;
                        ip8                   = ip4 * ip4;
                    }
                    A_arr[box_no](i, j, k) =
                        v_arr[box_no](i, j, k) + 0.875 * AA * ip8;
                    f_arr[box_no](i, j, k) = r_arr[box_no](i, j, k) +
                                             0.125 * AA * ip7 +
                                             0.875 * AA * ip8 * w;
                });
            mlabec.setACoeffs(lev, acoef[lev]);
            MultiFab::Copy(w_old[lev], a_w[lev], 0, 0, 1, 0);
        }
        amrex::Gpu::streamSynchronize();

        amrex::MLMG mlmg(mlabec);
        mlmg.setMaxIter(a_params.max_iter);
        mlmg.setVerbose(a_params.verbose >= 2 ? 2 : 0);
        mlmg.setBottomVerbose(0);
        const amrex::Real resid =
            mlmg.solve(amrex::GetVecOfPtrs(a_w), amrex::GetVecOfConstPtrs(rhs),
                       a_params.tolerance_rel, a_params.tolerance_abs);

        double update = 0.0;
        for (int lev = 0; lev < nlev; ++lev)
        {
            MultiFab::Subtract(w_old[lev], a_w[lev], 0, 0, 1, 0);
            update = std::max(update, w_old[lev].norm0(0, 0));
        }
        report.newton_iterations = it + 1;
        report.last_update       = update;
        if (a_params.verbose >= 1)
        {
            amrex::Print() << "Constraint solve: Newton " << it + 1
                           << ", MLMG final residual " << resid
                           << ", max |w_new - w_old| = " << update << "\n";
        }
        if (!has_momentum || update < a_params.newton_tolerance)
        {
            break;
        }
    }

    // ---- Covered coarse cells take their fine cells' mean correction ------
    for (int lev = nlev - 1; lev > 0; --lev)
    {
        amrex::average_down(a_w[lev], a_w[lev - 1], geom[lev], geom[lev - 1],
                            0, 1, a_amr.refRatio(lev - 1));
    }

    report.max_w.resize(nlev);
    for (int lev = 0; lev < nlev; ++lev)
    {
        report.max_w[lev] = a_w[lev].norm0(0, 0);
    }

    // ---- Monopole of w on the level-0 boundary cells: W = <r w> -----------
    {
        const amrex::Box domain = geom[0].Domain();
        const auto dlo          = amrex::lbound(domain);
        const auto dhi          = amrex::ubound(domain);
        const auto plo          = geom[0].ProbLoArray();
        const auto dx           = geom[0].CellSizeArray();
        const amrex::Real cx    = a_id.grid_center[0];
        const amrex::Real cy    = a_id.grid_center[1];
        const amrex::Real cz    = a_id.grid_center[2];

        amrex::ReduceOps<amrex::ReduceOpSum, amrex::ReduceOpSum> reduce_ops;
        amrex::ReduceData<amrex::Real, amrex::Real> reduce_data(reduce_ops);
        using ReduceTuple = typename decltype(reduce_data)::Type;
        for (amrex::MFIter mfi(a_w[0], amrex::TilingIfNotGPU()); mfi.isValid();
             ++mfi)
        {
            const amrex::Box &bx = mfi.tilebox();
            const auto arr       = a_w[0].const_array(mfi);
            reduce_ops.eval(
                bx, reduce_data,
                [=] AMREX_GPU_DEVICE(int i, int j, int k) -> ReduceTuple
                {
                    const bool edge = (i == dlo.x || i == dhi.x ||
                                       j == dlo.y || j == dhi.y ||
                                       k == dlo.z || k == dhi.z);
                    if (!edge)
                    {
                        return {0.0, 0.0};
                    }
                    const amrex::Real x = plo[0] + (i + 0.5) * dx[0] - cx;
                    const amrex::Real y = plo[1] + (j + 0.5) * dx[1] - cy;
                    const amrex::Real z = plo[2] + (k + 0.5) * dx[2] - cz;
                    const amrex::Real r = std::sqrt(x * x + y * y + z * z);
                    return {r * arr(i, j, k), 1.0};
                });
        }
        auto [sum_rw, count] = reduce_data.value();
        amrex::ParallelDescriptor::ReduceRealSum(sum_rw);
        amrex::ParallelDescriptor::ReduceRealSum(count);
        report.boundary_monopole = (count > 0.0) ? sum_rw / count : 0.0;
    }

    // Psi_bg -> 1 + M_bg / (2 r): the drainhole masses plus the puncture
    // shifts (background 0), or 2 sum c (bare punctures).
    double mass_bg = 0.0;
    if (a_id.solve_background == 0)
    {
        if (a_id.b0_A > 0.0)
        {
            mass_bg += a_id.drainhole_mass_A +
                       2.0 * (report.c_A - report.c_superposed_A);
        }
        if (a_id.b0_B > 0.0)
        {
            mass_bg += a_id.drainhole_mass_B +
                       2.0 * (report.c_B - report.c_superposed_B);
        }
    }
    else
    {
        mass_bg = 2.0 * ((a_id.b0_A > 0.0 ? report.c_A : 0.0) +
                         (a_id.b0_B > 0.0 ? report.c_B : 0.0));
    }
    report.background_mass = mass_bg;

    return report;
}
