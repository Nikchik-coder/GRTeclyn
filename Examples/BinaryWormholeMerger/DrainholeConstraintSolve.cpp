/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#include "DrainholeConstraintSolve.hpp"

#include <AMReX_MLABecLaplacian.H>
#include <AMReX_MLMG.H>
#include <AMReX_MultiFabUtil.H>
#include <AMReX_Reduce.H>

#include <algorithm>
#include <cmath>
#include <limits>

namespace
{
using params_t = BinaryWormholeInitialData::params_t;

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

//! The initial hierarchy and everything about the operator that does not
//! depend on the background (the Robin data and the unit B coefficients).
struct Hierarchy
{
    int nlev{0};
    amrex::Vector<amrex::Geometry> geom;
    amrex::Vector<amrex::BoxArray> grids;
    amrex::Vector<amrex::DistributionMapping> dmap;
    amrex::Vector<amrex::IntVect> ref_ratio;
    amrex::Vector<amrex::MultiFab> robin_a, robin_b, robin_f;
    amrex::Vector<amrex::Array<amrex::MultiFab, AMREX_SPACEDIM>> bcoef;

    Hierarchy(amrex::Amr &a_amr, const params_t &a_id)
    {
        nlev = a_amr.finestLevel() + 1;
        geom.resize(nlev);
        grids.resize(nlev);
        dmap.resize(nlev);
        ref_ratio.resize(nlev);
        robin_a.resize(nlev);
        robin_b.resize(nlev);
        robin_f.resize(nlev);
        bcoef.resize(nlev);
        for (int lev = 0; lev < nlev; ++lev)
        {
            geom[lev]  = a_amr.Geom(lev);
            grids[lev] = a_amr.boxArray(lev);
            dmap[lev]  = a_amr.DistributionMap(lev);
            ref_ratio[lev] =
                (lev < nlev - 1) ? a_amr.refRatio(lev) : amrex::IntVect(2);
            robin_a[lev].define(grids[lev], dmap[lev], 1, 1);
            robin_b[lev].define(grids[lev], dmap[lev], 1, 1);
            robin_f[lev].define(grids[lev], dmap[lev], 1, 1);
            fill_robin(geom[lev], a_id.grid_center, robin_a[lev],
                       robin_b[lev], robin_f[lev]);
            for (int idim = 0; idim < AMREX_SPACEDIM; ++idim)
            {
                bcoef[lev][idim].define(
                    amrex::convert(grids[lev],
                                   amrex::IntVect::TheDimensionVector(idim)),
                    dmap[lev], 1, 0);
                bcoef[lev][idim].setVal(1.0);
            }
        }
        amrex::Gpu::streamSynchronize();
    }
};

struct SolveResult
{
    int newton_iterations{0};
    double last_update{0.0};
};

//! One solve for the background a_id.  a_w is the initial guess on entry (a
//! previous solve's w speeds the next one up; MLMG's target is relative to
//! the right-hand side, so the answer does not depend on it) and the
//! solution on exit.  The composite solve leaves the covered coarse cells as
//! MLMG left them; the caller averages down once at the end.
// NOLINTNEXTLINE(readability-function-cognitive-complexity)
SolveResult solve_once(Hierarchy &h, const params_t &a_id,
                       const ConstraintSolveParams &a_params,
                       amrex::Vector<amrex::MultiFab> &a_w)
{
    using amrex::MultiFab;
    SolveResult result;
    const int nlev = h.nlev;

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
    for (int lev = 0; lev < nlev; ++lev)
    {
        psi_bg[lev].define(h.grids[lev], h.dmap[lev], 1, 0);
        res_bg[lev].define(h.grids[lev], h.dmap[lev], 1, 0);
        pot[lev].define(h.grids[lev], h.dmap[lev], 1, 0);
        aa[lev].define(h.grids[lev], h.dmap[lev], 1, 0);
        acoef[lev].define(h.grids[lev], h.dmap[lev], 1, 0);
        rhs[lev].define(h.grids[lev], h.dmap[lev], 1, 0);
        w_old[lev].define(h.grids[lev], h.dmap[lev], 1, 0);

        const BinaryWormholeInitialData background(a_id,
                                                   h.geom[lev].CellSize(0));
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
    }
    amrex::Gpu::streamSynchronize();

    // ---- The operator (A - lap) w = f, Robin on every face ----------------
    amrex::MLABecLaplacian mlabec(h.geom, h.grids, h.dmap, amrex::LPInfo());
    mlabec.setDomainBC(
        {AMREX_D_DECL(amrex::LinOpBCType::Robin, amrex::LinOpBCType::Robin,
                      amrex::LinOpBCType::Robin)},
        {AMREX_D_DECL(amrex::LinOpBCType::Robin, amrex::LinOpBCType::Robin,
                      amrex::LinOpBCType::Robin)});
    for (int lev = 0; lev < nlev; ++lev)
    {
        mlabec.setLevelBC(lev, &a_w[lev], &h.robin_a[lev], &h.robin_b[lev],
                          &h.robin_f[lev]);
    }
    for (int lev = 0; lev < nlev; ++lev)
    {
        mlabec.setBCoeffs(lev, amrex::GetArrOfConstPtrs(h.bcoef[lev]));
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
        result.newton_iterations = it + 1;
        result.last_update       = update;
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
    return result;
}

//! Throat X's far side from a solved w (see the header): w0 is the
//! monopole of w at the centre, from a least-squares fit w0 + w1 r + w2 r^2
//! through the cells of the finest level that covers the ball r < R,
//! R = a / 4 (the coordinate a in use) but at least six of that level's
//! cells.  The throat centres of every campaign run are grid vertices, where
//! the l = 1 part of w (which does not vanish at the centre) cancels between
//! mirror cells and the l = 2 part averages out over the cube-symmetric ball.
MouthReport measure_mouth(const Hierarchy &h, const params_t &a_id,
                          const int which, const double a_target,
                          const double m_target,
                          const amrex::Vector<amrex::MultiFab> &a_w)
{
    MouthReport mouth;
    const double a = (which == 0) ? a_id.b0_A : a_id.b0_B;
    if (a <= 0.0)
    {
        return mouth;
    }
    mouth.present   = true;
    mouth.a         = a_target;
    mouth.m         = m_target;
    mouth.sigma     = a / a_target;
    mouth.c         = (which == 0) ? a_id.solve_puncture_A
                                   : a_id.solve_puncture_B;
    mouth.d_bg      = BinaryWormholeInitialData::background_regular_part(
        a_id, which);
    mouth.M_far_iso =
        BinaryWormholeInitialData::isolated_far_side_mass(a_target, m_target);
    mouth.Q_far_iso = BinaryWormholeInitialData::isolated_far_side_charge(
        a_target, m_target);

    const auto &off = (which == 0) ? a_id.centerA : a_id.centerB;
    double centre[3];
    for (int d = 0; d < 3; ++d)
    {
        centre[d] = a_id.grid_center[d] + off[d];
    }

    // The finest level whose grids hold the whole ball.
    for (int lev = h.nlev - 1; lev >= 0; --lev)
    {
        const auto dx  = h.geom[lev].CellSizeArray();
        const auto plo = h.geom[lev].ProbLoArray();
        const double R = std::max(0.25 * a, 6.0 * dx[0]);
        amrex::IntVect lo, hi;
        for (int d = 0; d < 3; ++d)
        {
            lo[d] = static_cast<int>(std::floor((centre[d] - R - plo[d]) / dx[d]));
            hi[d] = static_cast<int>(std::floor((centre[d] + R - plo[d]) / dx[d]));
        }
        const amrex::Box ball(lo, hi);
        if (!h.geom[lev].Domain().contains(ball) ||
            !h.grids[lev].contains(ball))
        {
            continue;
        }

        const double cx = centre[0], cy = centre[1], cz = centre[2];
        amrex::ReduceOps<amrex::ReduceOpSum, amrex::ReduceOpSum,
                         amrex::ReduceOpSum, amrex::ReduceOpSum,
                         amrex::ReduceOpSum, amrex::ReduceOpSum,
                         amrex::ReduceOpSum, amrex::ReduceOpSum>
            reduce_ops;
        amrex::ReduceData<amrex::Real, amrex::Real, amrex::Real, amrex::Real,
                          amrex::Real, amrex::Real, amrex::Real, amrex::Real>
            reduce_data(reduce_ops);
        using ReduceTuple = typename decltype(reduce_data)::Type;
        for (amrex::MFIter mfi(a_w[lev], amrex::TilingIfNotGPU());
             mfi.isValid(); ++mfi)
        {
            const amrex::Box bx = mfi.tilebox() & ball;
            if (bx.isEmpty())
            {
                continue;
            }
            const auto arr = a_w[lev].const_array(mfi);
            reduce_ops.eval(
                bx, reduce_data,
                [=] AMREX_GPU_DEVICE(int i, int j, int k) -> ReduceTuple
                {
                    const amrex::Real x = plo[0] + (i + 0.5) * dx[0] - cx;
                    const amrex::Real y = plo[1] + (j + 0.5) * dx[1] - cy;
                    const amrex::Real z = plo[2] + (k + 0.5) * dx[2] - cz;
                    const amrex::Real r = std::sqrt(x * x + y * y + z * z);
                    if (r >= R || r <= 0.0)
                    {
                        return {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
                    }
                    const amrex::Real w  = arr(i, j, k);
                    const amrex::Real r2 = r * r;
                    return {1.0, r, r2, r2 * r, r2 * r2, w, r * w, r2 * w};
                });
        }
        auto sums = reduce_data.value();
        double s[8] = {amrex::get<0>(sums), amrex::get<1>(sums),
                       amrex::get<2>(sums), amrex::get<3>(sums),
                       amrex::get<4>(sums), amrex::get<5>(sums),
                       amrex::get<6>(sums), amrex::get<7>(sums)};
        amrex::ParallelDescriptor::ReduceRealSum(s, 8);
        // Normal equations of w = w0 + w1 r + w2 r^2 (Cramer's rule): the
        // quadratic term keeps w0 steady to ~1e-4 as R varies, where a line
        // drifts by 3e-3 (d = 8, level 3).
        const double M[3][3] = {{s[0], s[1], s[2]},
                                {s[1], s[2], s[3]},
                                {s[2], s[3], s[4]}};
        const double b[3]    = {s[5], s[6], s[7]};
        auto det3            = [](const double A[3][3])
        {
            return A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1]) -
                   A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0]) +
                   A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0]);
        };
        const double det = det3(M);
        if (s[0] < 6.0 || !(std::abs(det) > 0.0))
        {
            continue;
        }
        double M0[3][3], M1[3][3];
        for (int i = 0; i < 3; ++i)
        {
            for (int j = 0; j < 3; ++j)
            {
                M0[i][j] = (j == 0) ? b[i] : M[i][j];
                M1[i][j] = (j == 1) ? b[i] : M[i][j];
            }
        }
        mouth.w0         = det3(M0) / det;
        mouth.w_slope    = det3(M1) / det;
        mouth.level      = lev;
        mouth.fit_radius = R;
        mouth.ncells     = static_cast<long>(s[0]);
        break;
    }

    mouth.M_far = 2.0 * mouth.c * (mouth.d_bg + mouth.w0);
    mouth.Q_far =
        BinaryWormholeInitialData::far_side_charge(a_id, which, mouth.c);
    // The isolated drainhole with this (M_far, Q_far): Q/|M| =
    // sqrt(1 + (a/m)^2) / sqrt(4 pi) gives a/m, then m = |M| e^{-pi m/a}.
    const double ratio = mouth.Q_far / std::abs(mouth.M_far);
    const double am2   = 4.0 * M_PI * ratio * ratio - 1.0;
    if (mouth.M_far < 0.0 && am2 > 0.0)
    {
        const double a_over_m = std::sqrt(am2);
        mouth.m_equiv = std::abs(mouth.M_far) * std::exp(-M_PI / a_over_m);
        mouth.a_equiv = a_over_m * mouth.m_equiv;
    }
    return mouth;
}

//! V = pi s |grad phi|^2 at an offset from grid_center (host).
double scalar_potential(const params_t &a_id, const double x, const double y,
                        const double z)
{
    double g[3];
    BinaryWormholeInitialData::scalar_gradient(a_id, x, y, z, g);
    return M_PI * a_id.support_strength * (g[0] * g[0] + g[1] * g[1] + g[2] * g[2]);
}

//! M_ADM = 2 sum c - (1/2 pi) int [V Psi - (1/8) Ahat.Ahat Psi^-7] dV, exact
//! for a solution with Psi -> 1 + M/2r (Gauss on the constraint, whose
//! punctures add -4 pi c_X delta_X to lap Psi).  The box integral runs over each level's cells not
//! covered by the next; outside the box Psi = 1 + M/2r is used, with V from
//! the analytic scalar, on Gauss-Legendre directions and a log-spaced radius.
//! On the exact single throat at L = 64 it gives 1.0014, and 1.0007 for the
//! throat rebuilt from bare punctures, where the monopole fit gives 1.050.
void adm_mass_volume(const Hierarchy &h, const params_t &a_id,
                     const amrex::Vector<amrex::MultiFab> &a_w,
                     ConstraintSolveReport &a_report)
{
    double integral = 0.0;
    for (int lev = 0; lev < h.nlev; ++lev)
    {
        amrex::iMultiFab covered;
        if (lev < h.nlev - 1)
        {
            covered = amrex::makeFineMask(h.grids[lev], h.dmap[lev],
                                          h.grids[lev + 1], h.ref_ratio[lev],
                                          0, 1);
        }
        const bool has_fine = (lev < h.nlev - 1);
        const BinaryWormholeInitialData background(a_id,
                                                   h.geom[lev].CellSize(0));
        const auto dx      = h.geom[lev].CellSizeArray();
        const double dvol  = dx[0] * dx[1] * dx[2];
        amrex::ReduceOps<amrex::ReduceOpSum> reduce_ops;
        amrex::ReduceData<amrex::Real> reduce_data(reduce_ops);
        using ReduceTuple = typename decltype(reduce_data)::Type;
        for (amrex::MFIter mfi(a_w[lev], amrex::TilingIfNotGPU());
             mfi.isValid(); ++mfi)
        {
            const amrex::Box &bx = mfi.tilebox();
            const auto w_arr     = a_w[lev].const_array(mfi);
            const auto mask =
                has_fine ? covered.const_array(mfi) : amrex::Array4<const int>();
            reduce_ops.eval(
                bx, reduce_data,
                [=] AMREX_GPU_DEVICE(int i, int j, int k) -> ReduceTuple
                {
                    if (has_fine && mask(i, j, k) != 0)
                    {
                        return {0.0};
                    }
                    amrex::Real P, L, V, AA;
                    background.constraint_background(i, j, k, P, L, V, AA);
                    const amrex::Real Psi = P + w_arr(i, j, k);
                    amrex::Real src       = V * Psi;
                    if (AA != 0.0)
                    {
                        const amrex::Real ip  = 1.0 / Psi;
                        const amrex::Real ip2 = ip * ip;
                        src -= 0.125 * AA * ip2 * ip2 * ip2 * ip;
                    }
                    return {src * dvol};
                });
        }
        auto [sum] = reduce_data.value();
        amrex::ParallelDescriptor::ReduceRealSum(sum);
        integral += sum;
    }

    double two_c = 0.0;
    if (a_id.b0_A > 0.0)
    {
        two_c += 2.0 * a_id.solve_puncture_A;
    }
    if (a_id.b0_B > 0.0)
    {
        two_c += 2.0 * a_id.solve_puncture_B;
    }
    const double mass_box = two_c - integral / (2.0 * M_PI);

    // Tail: the level-0 box about its own centre, as offsets from grid_center.
    const auto plo = h.geom[0].ProbLoArray();
    const auto phi = h.geom[0].ProbHiArray();
    double mid[3], half[3];
    for (int d = 0; d < 3; ++d)
    {
        mid[d]  = 0.5 * (plo[d] + phi[d]) - a_id.grid_center[d];
        half[d] = 0.5 * (phi[d] - plo[d]);
    }
    constexpr int nth = 32, nph = 64, nrad = 240;
    double xg[nth], wg[nth];
    for (int i = 0; i < nth; ++i)
    {
        // Gauss-Legendre node i on [-1, 1]: Newton on P_n from the usual
        // Chebyshev-like first guess, weight 2 / ((1 - x^2) P_n'(x)^2).
        double x = std::cos(M_PI * (i + 0.75) / (nth + 0.5));
        double dp = 1.0;
        for (int iter = 0; iter < 100; ++iter)
        {
            double p1 = 1.0, p2 = 0.0;
            for (int j = 1; j <= nth; ++j)
            {
                const double p3 = p2;
                p2              = p1;
                p1              = ((2.0 * j - 1.0) * x * p2 - (j - 1.0) * p3) / j;
            }
            dp               = nth * (x * p1 - p2) / (x * x - 1.0);
            const double old = x;
            x                = old - p1 / dp;
            if (std::abs(x - old) < 1.0e-15)
            {
                break;
            }
        }
        xg[i] = x;
        wg[i] = 2.0 / ((1.0 - x * x) * dp * dp);
    }
    double tail = 0.0;
    for (int it = 0; it < nth; ++it)
    {
        const double ct = xg[it];
        const double st = std::sqrt(std::max(0.0, 1.0 - ct * ct));
        for (int ip = 0; ip < nph; ++ip)
        {
            const double ph = 2.0 * M_PI * (ip + 0.5) / nph;
            const double n[3] = {st * std::cos(ph), st * std::sin(ph), ct};
            double r0 = std::numeric_limits<double>::max();
            for (int d = 0; d < 3; ++d)
            {
                if (std::abs(n[d]) > 1.0e-12)
                {
                    r0 = std::min(r0, half[d] / std::abs(n[d]));
                }
            }
            const double r1  = 1.0e4 * r0;
            const double lg  = std::log(r1 / r0);
            double radial    = 0.0;
            for (int ir = 0; ir <= nrad; ++ir)
            {
                const double r = r0 * std::exp(lg * ir / nrad);
                const double x = mid[0] + r * n[0];
                const double y = mid[1] + r * n[1];
                const double z = mid[2] + r * n[2];
                const double V = scalar_potential(a_id, x, y, z);
                const double AA =
                    BinaryWormholeInitialData::bowen_york_square(a_id, x, y, z);
                const double Psi = 1.0 + 0.5 * mass_box / r;
                const double P2  = Psi * Psi;
                // d r = r d(ln r): trapezoid in ln r
                const double f =
                    (V * Psi - 0.125 * AA / (P2 * P2 * P2 * Psi)) * r * r * r;
                radial += ((ir == 0 || ir == nrad) ? 0.5 : 1.0) * f;
            }
            radial *= lg / nrad;
            tail += radial * wg[it] * (2.0 * M_PI / nph);
        }
    }
    a_report.tail_integral         = tail;
    a_report.adm_mass_volume       = two_c - (integral + tail) / (2.0 * M_PI);
    a_report.adm_mass_volume_valid = true;
}

//! Puncture coefficient the solve uses for throat X of a_id, by mode (0-2;
//! mode 3 starts from its own guess).
double chosen_coefficient(const params_t &a_id, const ConstraintSolveParams &p,
                          const int which)
{
    const double a = (which == 0) ? a_id.b0_A : a_id.b0_B;
    const double m = (which == 0) ? a_id.drainhole_mass_A : a_id.drainhole_mass_B;
    if (a <= 0.0)
    {
        return 0.0;
    }
    if (p.puncture_mode == 1)
    {
        return BinaryWormholeInitialData::isolated_puncture_coefficient(a, m);
    }
    if (p.puncture_mode == 2)
    {
        return (which == 0) ? p.puncture_A : p.puncture_B;
    }
    return BinaryWormholeInitialData::superposed_puncture_coefficient(a_id,
                                                                      which);
}
} // namespace

std::array<MouthReport, 2>
superposed_mouths(const BinaryWormholeInitialData::params_t &a_id)
{
    std::array<MouthReport, 2> out;
    params_t p         = a_id;
    p.solve_background = 0;
    for (int which = 0; which < 2; ++which)
    {
        const double a = (which == 0) ? p.b0_A : p.b0_B;
        const double c =
            (a > 0.0)
                ? BinaryWormholeInitialData::superposed_puncture_coefficient(
                      p, which)
                : 0.0;
        ((which == 0) ? p.solve_puncture_A : p.solve_puncture_B) = c;
    }
    for (int which = 0; which < 2; ++which)
    {
        const double a = (which == 0) ? p.b0_A : p.b0_B;
        if (a <= 0.0)
        {
            continue;
        }
        const double m = (which == 0) ? p.drainhole_mass_A : p.drainhole_mass_B;
        MouthReport &mouth = out[which];
        mouth.present      = true;
        mouth.a            = a;
        mouth.m            = m;
        mouth.c = (which == 0) ? p.solve_puncture_A : p.solve_puncture_B;
        mouth.d_bg =
            BinaryWormholeInitialData::background_regular_part(p, which);
        mouth.M_far = 2.0 * mouth.c * mouth.d_bg;
        mouth.Q_far =
            BinaryWormholeInitialData::far_side_charge(p, which, mouth.c);
        mouth.M_far_iso =
            BinaryWormholeInitialData::isolated_far_side_mass(a, m);
        mouth.Q_far_iso =
            BinaryWormholeInitialData::isolated_far_side_charge(a, m);
        const double ratio = mouth.Q_far / std::abs(mouth.M_far);
        const double am2   = 4.0 * M_PI * ratio * ratio - 1.0;
        if (mouth.M_far < 0.0 && am2 > 0.0)
        {
            const double a_over_m = std::sqrt(am2);
            mouth.m_equiv =
                std::abs(mouth.M_far) * std::exp(-M_PI / a_over_m);
            mouth.a_equiv = a_over_m * mouth.m_equiv;
        }
    }
    return out;
}

// NOLINTNEXTLINE(readability-function-cognitive-complexity)
ConstraintSolveReport
solve_drainhole_constraint(amrex::Amr &a_amr,
                           BinaryWormholeInitialData::params_t &a_id,
                           const ConstraintSolveParams &a_params,
                           amrex::Vector<amrex::MultiFab> &a_w)
{
    BL_PROFILE("solve_drainhole_constraint");
    using amrex::MultiFab;

    ConstraintSolveReport report;
    Hierarchy h(a_amr, a_id);
    const int nlev = h.nlev;

    a_w.clear();
    a_w.resize(nlev);
    for (int lev = 0; lev < nlev; ++lev)
    {
        a_w[lev].define(h.grids[lev], h.dmap[lev], 1, 1);
        a_w[lev].setVal(0.0);
    }

    // The throats the params ask for: mode 3 rescales copies of them.
    const params_t target = a_id;
    const bool present[2] = {target.b0_A > 0.0, target.b0_B > 0.0};
    const double a_t[2]   = {target.b0_A, target.b0_B};
    const double m_t[2]   = {target.drainhole_mass_A, target.drainhole_mass_B};
    double c_iso[2]       = {0.0, 0.0};
    double M_target[2]    = {0.0, 0.0};
    for (int X = 0; X < 2; ++X)
    {
        if (present[X])
        {
            c_iso[X] = BinaryWormholeInitialData::isolated_puncture_coefficient(
                a_t[X], m_t[X]);
            M_target[X] =
                BinaryWormholeInitialData::isolated_far_side_mass(a_t[X], m_t[X]);
        }
    }
    const bool scale = (a_params.match_charge != 0);

    // The background for puncture coefficients c (mode 3: throat X at
    // coordinate scale sigma_X = (c_X / c_iso)^2, which holds its far-side
    // charge 4 C c^2 / (sigma a) at the isolated value; otherwise as given).
    auto background_for = [&](const double c[2]) -> params_t
    {
        params_t p = target;
        for (int X = 0; X < 2; ++X)
        {
            if (!present[X])
            {
                continue;
            }
            const double sigma =
                (a_params.puncture_mode == 3 && scale)
                    ? (c[X] / c_iso[X]) * (c[X] / c_iso[X])
                    : 1.0;
            (X == 0 ? p.b0_A : p.b0_B)                         = sigma * a_t[X];
            (X == 0 ? p.drainhole_mass_A : p.drainhole_mass_B) = sigma * m_t[X];
            (X == 0 ? p.solve_puncture_A : p.solve_puncture_B) = c[X];
        }
        return p;
    };

    SolveResult last;
    auto solve_at = [&](const double c[2]) -> params_t
    {
        params_t p = background_for(c);
        last       = solve_once(h, p, a_params, a_w);
        ++report.solves;
        for (int X = 0; X < 2; ++X)
        {
            report.mouth[X] = measure_mouth(h, p, X, a_t[X], m_t[X], a_w);
        }
        return p;
    };

    double c[2] = {0.0, 0.0};
    params_t used;
    if (a_params.puncture_mode != 3)
    {
        for (int X = 0; X < 2; ++X)
        {
            c[X] = present[X] ? chosen_coefficient(target, a_params, X) : 0.0;
        }
        used = solve_at(c);
    }
    else
    {
        // Start where the superposition itself is matched: with the
        // companion's lapse factor E_Y = e^{-u_Y(d)/2} at this centre, the
        // scaled superposition's own c = sigma c_iso E_Y holds Q_far at the
        // isolated value when sigma E_Y^2 = 1, i.e. c = c_iso / E_Y (w0 ~ 0
        // there; it leaves M_far ~1 % short at d = 8).  With match_charge
        // = 0, start from the superposition's c.
        for (int X = 0; X < 2; ++X)
        {
            c[X] = present[X] ? c_iso[X] : 0.0;
        }
        for (int pass = 0; pass < 50; ++pass)
        {
            params_t p = background_for(c);
            double change = 0.0;
            for (int X = 0; X < 2; ++X)
            {
                if (!present[X])
                {
                    continue;
                }
                const double c_sup =
                    BinaryWormholeInitialData::superposed_puncture_coefficient(
                        p, X);
                // c_sup = sigma c_iso E_Y  =>  E_Y = c_sup / (sigma c_iso)
                const double sigma = scale ? (c[X] / c_iso[X]) * (c[X] / c_iso[X])
                                           : 1.0;
                const double E_Y   = c_sup / (sigma * c_iso[X]);
                const double c_new = scale ? c_iso[X] / E_Y : c_sup;
                change = std::max(change, std::abs(c_new - c[X]));
                c[X]   = c_new;
            }
            if (change < 1.0e-14)
            {
                break;
            }
        }

        // Newton on r_X(c) = M_far,X / M_target,X - 1: a finite-difference
        // Jacobian first, Broyden updates after.  Every evaluation is a
        // full solve; w carries over as the next initial guess.
        int idx[2], n = 0;
        for (int X = 0; X < 2; ++X)
        {
            if (present[X])
            {
                idx[n++] = X;
            }
        }
        auto residual = [&](double r[2])
        {
            double worst = 0.0;
            for (int k = 0; k < n; ++k)
            {
                const int X = idx[k];
                r[k]        = report.mouth[X].M_far / M_target[X] - 1.0;
                worst       = std::max(worst, std::abs(r[k]));
            }
            return worst;
        };
        used            = solve_at(c);
        double r[2]     = {0.0, 0.0};
        double worst    = residual(r);
        double J[2][2]  = {{1.0, 0.0}, {0.0, 1.0}};
        bool have_J     = false;
        int iter        = 0;
        if (a_params.verbose >= 1)
        {
            amrex::Print() << "Constraint solve, far-side matching: start c ="
                           << " " << c[0] << " " << c[1] << ", max |M_far/M_iso"
                           << " - 1| = " << worst << "\n";
        }
        while (worst > a_params.match_tolerance &&
               iter < a_params.match_max_iter)
        {
            ++iter;
            if (!have_J)
            {
                for (int k = 0; k < n; ++k)
                {
                    const int Y  = idx[k];
                    double cp[2] = {c[0], c[1]};
                    const double step = 1.0e-3 * c_iso[Y];
                    cp[Y] += step;
                    solve_at(cp);
                    double rp[2] = {0.0, 0.0};
                    residual(rp);
                    for (int i = 0; i < n; ++i)
                    {
                        J[i][k] = (rp[i] - r[i]) / step;
                    }
                }
                have_J = true;
            }
            // dc = -J^{-1} r
            double dc[2] = {0.0, 0.0};
            if (n == 1)
            {
                dc[0] = -r[0] / J[0][0];
            }
            else
            {
                const double det = J[0][0] * J[1][1] - J[0][1] * J[1][0];
                dc[0] = -(J[1][1] * r[0] - J[0][1] * r[1]) / det;
                dc[1] = -(-J[1][0] * r[0] + J[0][0] * r[1]) / det;
            }
            for (int k = 0; k < n; ++k)
            {
                c[idx[k]] += dc[k];
            }
            used = solve_at(c);
            double r_new[2] = {0.0, 0.0};
            worst           = residual(r_new);
            // Broyden: J += (dr - J dc) dc^T / (dc . dc)
            double dcdc = 0.0;
            for (int k = 0; k < n; ++k)
            {
                dcdc += dc[k] * dc[k];
            }
            if (dcdc > 0.0)
            {
                for (int i = 0; i < n; ++i)
                {
                    double Jdc = 0.0;
                    for (int k = 0; k < n; ++k)
                    {
                        Jdc += J[i][k] * dc[k];
                    }
                    const double u = (r_new[i] - r[i]) - Jdc;
                    for (int k = 0; k < n; ++k)
                    {
                        J[i][k] += u * dc[k] / dcdc;
                    }
                }
            }
            for (int k = 0; k < n; ++k)
            {
                r[k] = r_new[k];
            }
            if (a_params.verbose >= 1)
            {
                amrex::Print() << "Constraint solve, far-side matching: pass "
                               << iter << ", c = " << c[0] << " " << c[1]
                               << ", max |M_far/M_iso - 1| = " << worst << "\n";
            }
        }
        report.match_iterations = iter;
        report.match_residual   = worst;
        if (worst > a_params.match_tolerance)
        {
            amrex::Print() << "Constraint solve: WARNING far-side matching "
                              "stopped at max |M_far/M_iso - 1| = "
                           << worst << " after " << iter << " passes\n";
        }
    }
    report.newton_iterations = last.newton_iterations;
    report.last_update       = last.last_update;

    // ---- Covered coarse cells take their fine cells' mean correction ------
    for (int lev = nlev - 1; lev > 0; --lev)
    {
        amrex::average_down(a_w[lev], a_w[lev - 1], h.geom[lev],
                            h.geom[lev - 1], 0, 1, h.ref_ratio[lev - 1]);
    }

    report.max_w.resize(nlev);
    for (int lev = 0; lev < nlev; ++lev)
    {
        report.max_w[lev] = a_w[lev].norm0(0, 0);
    }

    report.c_A = used.solve_puncture_A;
    report.c_B = used.solve_puncture_B;
    if (used.b0_A > 0.0)
    {
        report.c_superposed_A =
            BinaryWormholeInitialData::superposed_puncture_coefficient(used, 0);
    }
    if (used.b0_B > 0.0)
    {
        report.c_superposed_B =
            BinaryWormholeInitialData::superposed_puncture_coefficient(used, 1);
    }

    // ---- Monopole of w on the level-0 boundary cells: W = <r w> -----------
    {
        const amrex::Box domain = h.geom[0].Domain();
        const auto dlo          = amrex::lbound(domain);
        const auto dhi          = amrex::ubound(domain);
        const auto plo          = h.geom[0].ProbLoArray();
        const auto dx           = h.geom[0].CellSizeArray();
        const amrex::Real cx    = used.grid_center[0];
        const amrex::Real cy    = used.grid_center[1];
        const amrex::Real cz    = used.grid_center[2];

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
    if (used.solve_background == 0)
    {
        if (used.b0_A > 0.0)
        {
            mass_bg += used.drainhole_mass_A +
                       2.0 * (report.c_A - report.c_superposed_A);
        }
        if (used.b0_B > 0.0)
        {
            mass_bg += used.drainhole_mass_B +
                       2.0 * (report.c_B - report.c_superposed_B);
        }
    }
    else
    {
        mass_bg = 2.0 * ((used.b0_A > 0.0 ? report.c_A : 0.0) +
                         (used.b0_B > 0.0 ? report.c_B : 0.0));
    }
    report.background_mass = mass_bg;

    adm_mass_volume(h, used, a_w, report);

    a_id = used;
    return report;
}
