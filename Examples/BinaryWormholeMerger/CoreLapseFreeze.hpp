/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef CORELAPSEFREEZE_HPP_
#define CORELAPSEFREEZE_HPP_

#include "StateVariables.hpp"

#include <AMReX_Array.H>
#include <AMReX_Array4.H>
#include <AMReX_GpuQualifiers.H>
#include <AMReX_Math.H>

#include <array>
#include <cmath>

/* Taper the Bona-Masso source of the lapse to zero inside a central window:

     d/dt alpha = advection - (1 - W(r)) * c * alpha^p * (K - 2 Theta)

   Companion to CoreMatterDamping.hpp, attacking the other half of the
   post-collapse instability.  The matter-damping sweep (M4b waves 1-2,
   research/merger/Plan.md) exhausted the (window, rate) plane: the damping
   rate has a measured optimum (tau ~ 0.05) worth ~0.5 code units and no
   window geometry adds anything; best survival 52.55 against a NaN that
   must be held off until the burst reaches the extraction sphere.  The
   killer, photographed in the fast-arm frames at t = 52.0, is a GAUGE
   loop: wrong-sign K pockets (K ~ -0.07) wrap the ends of the collapsed
   bar at r ~ 1-2, 1+log slicing re-inflates the lapse there
   (d/dt alpha = -2 alpha K), and the re-inflated cells steepen until h11
   or K leaves the representable range.  Matter deletion only starves that
   loop; it cannot stop it.

   This module removes the loop's motor.  Only the slicing SOURCE term is
   tapered -- the advection term is left intact, so the lapse still rides
   the shift and no shear boundary forms between a frozen lapse and a
   moving grid.  The taper W(r) is a C^2 quintic smootherstep (W = 1
   inside radius_full, 0 at and outside radius_start, first AND second
   derivatives continuous at both ends), one degree smoother than the
   matter window's cosine ramp because this one multiplies a RHS the
   finite differencing then differentiates; a hard boolean freeze would
   hand it a discontinuous RHS and die on the spot.  The cancellation is
   exact by construction: the pass adds back
   W * c * alpha^p * (K - 2 Theta) computed from the same solution array
   the gauge RHS just read.

   Secondary guard (freeze_shift, separately default off): if the
   Gamma-driver still tears the grid over the tapered-slicing core, the
   same W scales the full shift and B right-hand sides by (1 - W).

   Honesty note: unlike the matter window, this window is NOT strictly
   inside the trapped surface (the shell is aspherical: r_AH min/mean/max
   ~ 1.07/1.63/2.3 with 27-30% of rays trapped), so in principle the
   altered slicing can influence the exterior.  A run using this module is
   publishable only through the M6 overlap test: its Psi4 at the
   extraction radii must match the undamped arms over the shared window.

   Own module, default off: no archived run changes behaviour. */
struct CoreLapseFreeze
{
    struct params_t
    {
        bool enabled{false};
        //! Zero weight at and outside this radius (0 = module inert).
        double radius_start{0.0};
        //! Full weight (source fully cancelled) at and inside this radius.
        double radius_full{0.0};
        //! Window engages only at t >= from_time: before the collapse the
        //! centre is live inter-throat spacetime that must keep slicing.
        double from_time{0.0};
        //! Guard: also scale the shift and B RHS by (1 - W) in the window.
        bool freeze_shift{false};
        //! Centre of the window (wired to the grid centre).
        std::array<double, AMREX_SPACEDIM> grid_center{};
        //! Copies of gauge.lapse_coeff / gauge.lapse_power, so the add-back
        //! cancels the exact source term the gauge wrote.
        double lapse_coeff{2.0};
        double lapse_power{1.0};
    };

    params_t m_params;
    bool m_active{false};
    amrex::GpuArray<amrex::Real, AMREX_SPACEDIM> m_dx{};
    amrex::GpuArray<amrex::Real, AMREX_SPACEDIM> m_prob_lo{};
    amrex::GpuArray<amrex::Real, AMREX_SPACEDIM> m_center{};

    CoreLapseFreeze(const params_t &a_params,
                    const amrex::GpuArray<amrex::Real, AMREX_SPACEDIM> &a_dx,
                    const amrex::GpuArray<amrex::Real, AMREX_SPACEDIM> &a_prob_lo,
                    amrex::Real a_time)
        : m_params(a_params), m_dx(a_dx), m_prob_lo(a_prob_lo)
    {
        m_active = a_params.enabled && (a_params.radius_start > 0.0) &&
                   (a_time >= a_params.from_time);
        for (int d = 0; d < AMREX_SPACEDIM; ++d)
        {
            m_center[d] = amrex::Real(a_params.grid_center[d]);
        }
    }

    //! C^2 quintic smootherstep: 6w^5 - 15w^4 + 10w^3.
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE static amrex::Real
    smooth_ramp(amrex::Real w)
    {
        w = amrex::min(amrex::max(w, amrex::Real(0.0)), amrex::Real(1.0));
        return w * w * w *
               (w * (amrex::Real(6.0) * w - amrex::Real(15.0)) +
                amrex::Real(10.0));
    }

    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
    operator()(int i, int j, int k, const amrex::Array4<amrex::Real> &rhs,
               const amrex::Array4<const amrex::Real> &soln) const
    {
        if (!m_active)
        {
            return;
        }
        amrex::Real r2 = 0.0;
        const int idx[AMREX_SPACEDIM] = {AMREX_D_DECL(i, j, k)};
        for (int d = 0; d < AMREX_SPACEDIM; ++d)
        {
            const amrex::Real xd =
                m_prob_lo[d] +
                (amrex::Real(idx[d]) + amrex::Real(0.5)) * m_dx[d] -
                m_center[d];
            r2 += xd * xd;
        }
        const amrex::Real r     = std::sqrt(r2);
        const amrex::Real start = amrex::Real(m_params.radius_start);
        const amrex::Real full  = amrex::Real(m_params.radius_full);
        const amrex::Real w     = smooth_ramp(
            (start - r) / amrex::max(start - full, amrex::Real(1.0e-30)));
        if (w <= amrex::Real(0.0))
        {
            return;
        }

        const amrex::Real lapse = soln(i, j, k, c_lapse);
        const amrex::Real K     = soln(i, j, k, c_K);
        const amrex::Real Theta = soln(i, j, k, c_Theta);
        const amrex::Real source =
            -amrex::Real(m_params.lapse_coeff) *
            std::pow(lapse, amrex::Real(m_params.lapse_power)) *
            (K - amrex::Real(2.0) * Theta);
        rhs(i, j, k, c_lapse) -= w * source;

        if (m_params.freeze_shift)
        {
            const amrex::Real keep = amrex::Real(1.0) - w;
            for (int d = 0; d < AMREX_SPACEDIM; ++d)
            {
                rhs(i, j, k, c_shift1 + d) *= keep;
                rhs(i, j, k, c_B1 + d) *= keep;
            }
        }
    }
};

#endif /* CORELAPSEFREEZE_HPP_ */
