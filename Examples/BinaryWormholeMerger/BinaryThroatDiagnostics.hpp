/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef BINARYTHROATDIAGNOSTICS_HPP_
#define BINARYTHROATDIAGNOSTICS_HPP_

#include "SmallDataIO.hpp"
#include "StateVariables.hpp"

#include <AMReX_Geometry.H>
#include <AMReX_GpuAtomic.H>
#include <AMReX_GpuContainers.H>
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
      * The outgoing null expansion theta_+ of COORDINATE SPHERES about each
        throat and about the midpoint between them, computed with the FULL
        spatial metric (gamma_ij = h_ij/chi, det h = 1):
            theta_+ = div_gamma(s) + K_ij s^i s^j - K,
        s the unit gamma-normal of the sphere -- the same formula as the
        validated offline scanner ah_radial_scan.py.  The midpoint scan is the
        common-horizon detector: theta_+ <= 0 on a sphere enclosing both
        throats is the signature of fusion into a single trapped region.

    HISTORY - until 2026-09-01 this scan used the conformally-flat shortcut
        theta_+ ~ 2 sqrt(chi)/r - (d chi/dr)/sqrt(chi) + A_rr - (2/3) K,
    i.e. it dropped h_ij entirely.  That error is O(1) exactly where two deep
    lapse/chi wells deform the conformal metric, and it produced false trapped
    verdicts there: theta_common < 0 continuously over t = 42.3-60 in p045 (a
    run with no collapse at all, throats receding), and the transient
    t = 29.9-32.7 "fusion" signal on the d12 merger, six times shallower than
    the p045 false positive.  Every binary_throat_diagnostics.dat written
    before this date carries that artefact in its theta columns whenever the
    scan sphere encloses or grazes both throats; per-throat columns far from
    the companion are mildly affected.  The first genuine common trapped
    surface on the d12 merger is t = 51.06 (this scan, full metric, r = 1.0),
    offline-confirmed at t = 51.5 (r = 1.07).

    IMPORTANT - theta_+ is reduced per RADIAL SHELL, taking the MAXIMUM over
    each shell, and the reported horizon radius is the outermost shell whose
    maximum is <= 0.  A surface is trapped only when theta_+ <= 0 everywhere on
    it, so a global minimum over all points is not merely conservative, it is
    wrong: a single point of a large sphere about throat A that grazes throat B
    sits in B's steep chi gradient, which overwhelms the 2 sqrt(chi)/r term of
    the distant centre A and drives theta_+ negative there.  Reducing a minimum
    turns that one point into a phantom trapped surface straddling the whole
    binary at t = 0, at a radius set by the SEPARATION, so no exclusion radius
    can suppress it.  Taking the shell maximum removes it exactly, because the
    rest of that same sphere is far from both throats and expanding.

    A shell the finest level does not cover carries NO verdict - under AMR the
    fine grid is a small patch around the throats.  Coverage is checked against
    the shell volume in cells; if no shell is covered the reported theta is the
    sentinel 1e30, meaning "not measured", and the horizon radius stays 0.

    The min_radius parameter.  For an Ellis-Bronnikov throat the coordinate
    origin r -> 0 is the OTHER asymptotic infinity, not a centre.  For the
    massless throat theta_+ = 2 (1 - u) / (r (1 + u)^2) with u = b^2/(4 r^2), so
    theta_+ < 0 on the WHOLE sphere for r < b/2: a genuine, unavoidable
    coordinate artefact of the inversion rather than a horizon.  min_radius
    excludes it and need only exceed the isotropic throat radius b/2 (the
    default, the throat radius b, is twice that).  The common-horizon scan
    raises its own cut to sep/2 + min_radius automatically, so that a sphere
    only counts as "common" once it encloses both throats.
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
        //! A half-space counts as COLLAPSED once its lapse minimum falls
        //! below this.  Every uncollapsed throat on record sits at
        //! lapse ~ 2e-1; a collapsing core plunges to the min_lapse floor,
        //! so the two regimes are five orders of magnitude apart.
        double collapsed_lapse{1.0e-6};
        //! Scan floor used INSTEAD of min_radius once collapsed.  The r < b/2
        //! inversion region that min_radius protects against belongs to an
        //! uncollapsed throat; after collapse it is trumpet interior and the
        //! artefact is gone, while a genuine horizon's coordinate radius is
        //! small (r ~ 1 on the d12 merger) and would sit below the
        //! uncollapsed cut.  A few finest cells keeps the floored centre
        //! itself out.
        double collapsed_min_radius{0.5};
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

        // ---- Pass 3: theta_+ on radial SHELLS about A, B and their midpoint --
        //
        // A closed surface is trapped when theta_+ <= 0 EVERYWHERE on it, so
        // the statistic that matters per coordinate sphere is the MAXIMUM of
        // theta_+ over that sphere.  Reducing a global minimum over all points
        // instead - the obvious but wrong thing - declares a horizon as soon as
        // a SINGLE point of a large sphere about throat A happens to graze
        // throat B, where B's steep gradients drive theta_+ locally negative.
        // That produces an enormous phantom "trapped surface" straddling
        // the whole binary at t = 0, and no exclusion radius fixes it: the
        // grazing region extends over a distance set by the separation, not by
        // the throat radius.
        //
        // Shells the finest level does not COVER carry no verdict.  Under AMR
        // the fine grid is a small patch around the throats, so most large
        // shells are empty or partial; an unsampled shell must read "unknown",
        // never "trapped".  Coverage is tested against the shell volume in
        // cells; uncovered shells are skipped and, if none is covered, the
        // reported theta is the BIG sentinel (1e30 = no verdict).
        constexpr int NSHELL       = 256;
        const amrex::Real shell_dr = amrex::max(
            dx_arr[0], amrex::max(dx_arr[1], amrex::Real(dx_arr[2])));
        const amrex::Real cell_vol = dx_arr[0] * dx_arr[1] * dx_arr[2];

        // Inner cut per scan centre.  A and B only have to clear their own
        // inversion region (theta_+ < 0 for r < b/2 exactly, see above).  The
        // midpoint scan is the COMMON-horizon detector, so it must additionally
        // enclose both throats to mean anything: r >= sep/2 + min_radius.
        //
        // Once a half-space has collapsed (lapse pinned far below any throat
        // value) its inversion artefact no longer exists and the cut drops to
        // collapsed_min_radius, so the shrinking horizon stays tracked.
        const amrex::Real coll_r = a_params.collapsed_min_radius;
        const amrex::Real cut_A =
            (min_lap_A < a_params.collapsed_lapse) ? coll_r : min_r;
        const amrex::Real cut_B =
            (min_lap_B < a_params.collapsed_lapse) ? coll_r : min_r;
        const amrex::Real floor_C = (min_lap_A < a_params.collapsed_lapse &&
                                     min_lap_B < a_params.collapsed_lapse)
                                        ? coll_r
                                        : min_r;
        const amrex::Real min_r_c[3] = {
            cut_A, cut_B, amrex::max(floor_C, 0.5 * sep + floor_C)};

        amrex::Real theta_shell[3] = {BIG, BIG, BIG};
        amrex::Real ah_r_shell[3]  = {0.0, 0.0, 0.0};
        {
            const amrex::Real aX = posA[0], aY = posA[1], aZ = posA[2];
            const amrex::Real bX = posB[0], bY = posB[1], bZ = posB[2];
            const amrex::Real mX = posC[0], mY = posC[1], mZ = posC[2];
            const amrex::Real cut0 = min_r_c[0], cut1 = min_r_c[1],
                              cut2 = min_r_c[2];

            constexpr int NBIN = 3 * NSHELL;
            amrex::Gpu::DeviceVector<amrex::Real> d_shell_max(NBIN);
            amrex::Gpu::DeviceVector<amrex::Real> d_shell_cnt(NBIN);
            amrex::Real *p_max = d_shell_max.data();
            amrex::Real *p_cnt = d_shell_cnt.data();
            amrex::ParallelFor(NBIN,
                               [=] AMREX_GPU_DEVICE(int n)
                               {
                                   p_max[n] = -BIG;
                                   p_cnt[n] = 0.0;
                               });

            for (amrex::MFIter mfi(a_state, amrex::TilingIfNotGPU());
                 mfi.isValid(); ++mfi)
            {
                const amrex::Box &bx = mfi.validbox();
                const auto arr       = a_state.const_array(mfi);
                amrex::ParallelFor(
                    bx,
                    [=] AMREX_GPU_DEVICE(int i, int j, int k)
                    {
                        const amrex::Real px =
                            prob_lo[0] + (amrex::Real(i) + 0.5) * dx_arr[0] - cx;
                        const amrex::Real py =
                            prob_lo[1] + (amrex::Real(j) + 0.5) * dx_arr[1] - cy;
                        const amrex::Real pz =
                            prob_lo[2] + (amrex::Real(k) + 0.5) * dx_arr[2] - cz;

                        // Full-metric expansion of the coordinate sphere:
                        //   theta_+ = div_gamma(s) + K_ij s^i s^j - K
                        // with gamma_ij = h_ij/chi (det h = 1) and s the unit
                        // gamma-normal of r = const.  Both terms are
                        // homogeneous of degree 0 in the (un-normalised)
                        // direction X_i, so no ray normalisation is needed:
                        //   u^a       = hi^{ab} X_b        (hi = h^{-1} = adj h)
                        //   un        = X_a hi^{ab} X_b    (> 0 for SPD h)
                        //   sqrt(g) s^a = u^a / (chi sqrt(un))     [the "flux"]
                        //   div_gamma(s) = chi^{3/2} d_a(flux^a)
                        //   K_ij s^i s^j - K = A_ab u^a u^b / un - (2/3) K
                        // The divergence needs the flux at the six face
                        // neighbours, so gather chi and adj h on the stencil
                        // once; the adjugates are centre independent.
                        constexpr amrex::Real CHI_FLOOR = 1.0e-12;
                        const int off[7][3] = {{0, 0, 0},  {1, 0, 0}, {-1, 0, 0},
                                               {0, 1, 0},  {0, -1, 0},
                                               {0, 0, 1},  {0, 0, -1}};
                        amrex::Real s_chi[7];
                        // adj h, symmetric storage: 11, 12, 13, 22, 23, 33
                        amrex::Real s_hi[7][6];
                        for (int q = 0; q < 7; ++q)
                        {
                            const int ii = i + off[q][0];
                            const int jj = j + off[q][1];
                            const int kk = k + off[q][2];
                            const amrex::Real h11 = arr(ii, jj, kk, c_h11);
                            const amrex::Real h12 = arr(ii, jj, kk, c_h12);
                            const amrex::Real h13 = arr(ii, jj, kk, c_h13);
                            const amrex::Real h22 = arr(ii, jj, kk, c_h22);
                            const amrex::Real h23 = arr(ii, jj, kk, c_h23);
                            const amrex::Real h33 = arr(ii, jj, kk, c_h33);
                            s_hi[q][0] = h22 * h33 - h23 * h23;
                            s_hi[q][1] = h13 * h23 - h12 * h33;
                            s_hi[q][2] = h12 * h23 - h13 * h22;
                            s_hi[q][3] = h11 * h33 - h13 * h13;
                            s_hi[q][4] = h12 * h13 - h11 * h23;
                            s_hi[q][5] = h11 * h22 - h12 * h12;
                            s_chi[q]   = amrex::max(arr(ii, jj, kk, c_chi),
                                                    CHI_FLOOR);
                        }
                        const amrex::Real K   = arr(i, j, k, c_K);
                        const amrex::Real A11 = arr(i, j, k, c_A11);
                        const amrex::Real A22 = arr(i, j, k, c_A22);
                        const amrex::Real A33 = arr(i, j, k, c_A33);
                        const amrex::Real A12 = arr(i, j, k, c_A12);
                        const amrex::Real A13 = arr(i, j, k, c_A13);
                        const amrex::Real A23 = arr(i, j, k, c_A23);

                        const amrex::Real ox[3]  = {px - aX, px - bX, px - mX};
                        const amrex::Real oy[3]  = {py - aY, py - bY, py - mY};
                        const amrex::Real oz[3]  = {pz - aZ, pz - bZ, pz - mZ};
                        const amrex::Real cut[3] = {cut0, cut1, cut2};

                        for (int c = 0; c < 3; ++c)
                        {
                            const amrex::Real X  = ox[c];
                            const amrex::Real Y  = oy[c];
                            const amrex::Real Z  = oz[c];
                            const amrex::Real r2 = X * X + Y * Y + Z * Z;
                            if (r2 <= 1.0e-12)
                            {
                                continue;
                            }
                            const amrex::Real r = std::sqrt(r2);
                            if (r <= cut[c])
                            {
                                continue;
                            }
                            const int ib = static_cast<int>(r / shell_dr);
                            if (ib >= NSHELL)
                            {
                                continue;
                            }

                            // div_gamma(s): centred difference of the flux.
                            bool ok         = true;
                            amrex::Real div = 0.0;
                            for (int d = 0; d < 3 && ok; ++d)
                            {
                                amrex::Real F[2]; // +, -
                                for (int s = 0; s < 2 && ok; ++s)
                                {
                                    const int q = 1 + 2 * d + s;
                                    const amrex::Real nx =
                                        X + amrex::Real(off[q][0]) * dx_arr[0];
                                    const amrex::Real ny =
                                        Y + amrex::Real(off[q][1]) * dx_arr[1];
                                    const amrex::Real nz =
                                        Z + amrex::Real(off[q][2]) * dx_arr[2];
                                    const amrex::Real u0 = s_hi[q][0] * nx +
                                                           s_hi[q][1] * ny +
                                                           s_hi[q][2] * nz;
                                    const amrex::Real u1 = s_hi[q][1] * nx +
                                                           s_hi[q][3] * ny +
                                                           s_hi[q][4] * nz;
                                    const amrex::Real u2 = s_hi[q][2] * nx +
                                                           s_hi[q][4] * ny +
                                                           s_hi[q][5] * nz;
                                    const amrex::Real un =
                                        u0 * nx + u1 * ny + u2 * nz;
                                    if (un <= 0.0)
                                    {
                                        ok = false; // h not SPD: no verdict
                                        break;
                                    }
                                    const amrex::Real ud =
                                        (d == 0) ? u0 : ((d == 1) ? u1 : u2);
                                    F[s] = ud / (s_chi[q] * std::sqrt(un));
                                }
                                if (ok)
                                {
                                    div += (F[0] - F[1]) / (2.0 * dx_arr[d]);
                                }
                            }

                            // K_ij s^i s^j - K at the centre cell.
                            const amrex::Real u0 = s_hi[0][0] * X +
                                                   s_hi[0][1] * Y +
                                                   s_hi[0][2] * Z;
                            const amrex::Real u1 = s_hi[0][1] * X +
                                                   s_hi[0][3] * Y +
                                                   s_hi[0][4] * Z;
                            const amrex::Real u2 = s_hi[0][2] * X +
                                                   s_hi[0][4] * Y +
                                                   s_hi[0][5] * Z;
                            const amrex::Real un = u0 * X + u1 * Y + u2 * Z;
                            if (un <= 0.0)
                            {
                                ok = false;
                            }

                            // A cell the formula cannot be trusted on (h not
                            // positive definite) must read "not trapped", never
                            // poison a shell into a false horizon: send +BIG.
                            const amrex::Real theta_plus =
                                ok ? std::sqrt(s_chi[0]) * s_chi[0] * div +
                                         (A11 * u0 * u0 + A22 * u1 * u1 +
                                          A33 * u2 * u2 +
                                          2.0 * (A12 * u0 * u1 + A13 * u0 * u2 +
                                                 A23 * u1 * u2)) /
                                             un -
                                         (2.0 / 3.0) * K
                                   : BIG;

                            amrex::Gpu::Atomic::Max(&p_max[c * NSHELL + ib],
                                                    theta_plus);
                            amrex::Gpu::Atomic::AddNoRet(&p_cnt[c * NSHELL + ib],
                                                         amrex::Real(1.0));
                        }
                    });
            }
            amrex::Gpu::streamSynchronize();

            std::vector<amrex::Real> shell_max(NBIN);
            std::vector<amrex::Real> shell_cnt(NBIN);
            amrex::Gpu::copy(amrex::Gpu::deviceToHost, d_shell_max.begin(),
                             d_shell_max.end(), shell_max.begin());
            amrex::Gpu::copy(amrex::Gpu::deviceToHost, d_shell_cnt.begin(),
                             d_shell_cnt.end(), shell_cnt.begin());
            amrex::ParallelDescriptor::ReduceRealMax(shell_max.data(), NBIN);
            amrex::ParallelDescriptor::ReduceRealSum(shell_cnt.data(), NBIN);

            for (int c = 0; c < 3; ++c)
            {
                for (int ib = 0; ib < NSHELL; ++ib)
                {
                    const amrex::Real r_hi = amrex::Real(ib + 1) * shell_dr;
                    const amrex::Real r_lo =
                        amrex::max(amrex::Real(ib) * shell_dr, min_r_c[c]);
                    if (r_hi <= r_lo)
                    {
                        continue;
                    }
                    // Cells the shell would hold if the finest level covered it.
                    const amrex::Real expected =
                        (4.0 / 3.0) * M_PI *
                        (r_hi * r_hi * r_hi - r_lo * r_lo * r_lo) / cell_vol;
                    if (shell_cnt[c * NSHELL + ib] < 0.5 * expected)
                    {
                        continue; // not covered -> no verdict from this shell
                    }
                    const amrex::Real th = shell_max[c * NSHELL + ib];
                    theta_shell[c]       = amrex::min(theta_shell[c], th);
                    if (th <= 0.0)
                    {
                        // Outermost trapped shell wins (apparent horizon).
                        ah_r_shell[c] = amrex::max(ah_r_shell[c], r_hi);
                    }
                }
            }
        }

        const amrex::Real theta_A = theta_shell[0], ah_r_A = ah_r_shell[0];
        const amrex::Real theta_B = theta_shell[1], ah_r_B = ah_r_shell[1];
        const amrex::Real theta_C = theta_shell[2], ah_r_C = ah_r_shell[2];

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
