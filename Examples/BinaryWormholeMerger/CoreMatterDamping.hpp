/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef COREMATTERDAMPING_HPP_
#define COREMATTERDAMPING_HPP_

#include "StateVariables.hpp"

#include <AMReX_Array.H>
#include <AMReX_Array4.H>
#include <AMReX_GpuQualifiers.H>
#include <AMReX_Math.H>

#include <array>
#include <cmath>

/* Exponential damping of the scalar field in the deeply collapsed core.

   The moving-puncture floors (min_chi, min_lapse) keep the GEOMETRY of a
   collapsed region representable, but they do nothing for the MATTER that
   collapses with it.  The phantom scalar keeps sourcing the metric equations
   at the edge of the floored region, the gradients there steepen step after
   step, and the run ends in a NaN some tens of code units after horizon
   formation -- measured on the d12 flip merger: common trapped surface at
   t = 29.9, NaN in h11 at t = 52.07 with the scalar still at 84% of its
   throat value on the frozen core.

   The cure is the matter half of the puncture trick: deep inside the
   collapsed region, drive phi and Pi exponentially to zero.  Two windows
   select the region, and a point is damped by whichever gives the larger
   weight:

   1. LAPSE window (lapse_start -> lapse_full, cosine ramp in log10 lapse).
      A first attempt with lapse_start = 1e-6 covered only ~3 finest cells
      and moved the death from t = 52.07 to t = 52.09.  Widened to 3e-2
      (measured strictly inside the apparent horizon) it cleaned the core
      to |phi| ~ 1e-10 -- and the run still died at t = 52.86, because the
      window defeats itself: wrong-sign K pockets (K down to -2) form at
      the ends of the collapsed bar, 1+log slicing re-inflates the lapse
      there (d/dt alpha = -2 alpha K), and exactly the sickest cells rise
      OUT of the window.  Measured at t = 52.5: |phi| = 0.82 surviving at
      r = 0.30 with lapse up to 0.43 -- unreachable by any lapse threshold
      that spares healthy regions (throats sit at lapse ~ 0.2).  A
      Kreiss-Oliger arm (sigma 0.1 -> 1.0) died EARLIER, t = 51.68, NaN in
      K: dissipation attacks the puncture structure itself, the same
      failure class as the Stage 1 sigma = 2.0 throat erosion.

   2. RADIUS window (radius_start -> radius_full, cosine ramp in r about
      grid_center; radius_start = 0 disables it).  Radius does not care
      what the lapse does, so the re-inflation loop cannot lift matter out
      of it.  The default-off window is set per-run from measurement: for
      the d12 flip merger the common apparent horizon sits at r = 0.875
      and the surviving driver at r <= 0.35, so full damping inside 0.5
      ramping to zero at 0.7 stays strictly inside the trapped surface --
      no signal from the damped region can reach the wave zone.  The
      window engages only from `from_time` (default 0): before the merger
      there is no horizon about the centre and a radius window would damp
      live inter-throat field.

   Own module, default off: no archived run changes behaviour.
*/
struct CoreMatterDamping
{
    struct params_t
    {
        bool enabled{false};
        //! Ramp start: damping switches on below this lapse.
        double lapse_start{3.0e-2};
        //! Ramp end: full-strength damping at and below this lapse.
        double lapse_full{1.0e-3};
        //! e-folding time of the damped scalar, in code units.
        double tau{0.25};
        //! Radius window: zero weight at and outside this radius
        //! (0 = radius window disabled).
        double radius_start{0.0};
        //! Radius window: full weight at and inside this radius.
        double radius_full{0.0};
        //! Radius window engages only at t >= from_time (pre-merger it
        //! would damp live inter-throat field; there is no horizon yet).
        double from_time{0.0};
        //! Centre of the radius window (wired to the grid centre).
        std::array<double, AMREX_SPACEDIM> grid_center{};
    };

    params_t m_params;
    amrex::Real m_dt{0.0};
    bool m_radius_active{false};
    amrex::GpuArray<amrex::Real, AMREX_SPACEDIM> m_dx{};
    amrex::GpuArray<amrex::Real, AMREX_SPACEDIM> m_prob_lo{};
    amrex::GpuArray<amrex::Real, AMREX_SPACEDIM> m_center{};

    CoreMatterDamping(
        const params_t &a_params, amrex::Real a_dt,
        const amrex::GpuArray<amrex::Real, AMREX_SPACEDIM> &a_dx,
        const amrex::GpuArray<amrex::Real, AMREX_SPACEDIM> &a_prob_lo,
        amrex::Real a_time)
        : m_params(a_params), m_dt(a_dt), m_dx(a_dx), m_prob_lo(a_prob_lo)
    {
        m_radius_active = (a_params.radius_start > 0.0) &&
                          (a_time >= a_params.from_time);
        for (int d = 0; d < AMREX_SPACEDIM; ++d)
        {
            m_center[d] = amrex::Real(a_params.grid_center[d]);
        }
    }

    AMREX_GPU_DEVICE AMREX_FORCE_INLINE static amrex::Real
    smooth_ramp(amrex::Real w)
    {
        w = amrex::min(amrex::max(w, amrex::Real(0.0)), amrex::Real(1.0));
        return amrex::Real(0.5) *
               (amrex::Real(1.0) - std::cos(amrex::Real(M_PI) * w));
    }

    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
    operator()(int i, int j, int k,
               const amrex::Array4<amrex::Real> &state) const
    {
        amrex::Real w = 0.0;

        const amrex::Real lapse = state(i, j, k, c_lapse);
        if (lapse < amrex::Real(m_params.lapse_start))
        {
            const amrex::Real hi =
                std::log10(amrex::Real(m_params.lapse_start));
            const amrex::Real lo =
                std::log10(amrex::Real(m_params.lapse_full));
            const amrex::Real l10 =
                std::log10(amrex::max(lapse, amrex::Real(1.0e-300)));
            w = smooth_ramp((hi - l10) /
                            amrex::max(hi - lo, amrex::Real(1.0e-30)));
        }

        if (m_radius_active)
        {
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
            const amrex::Real w_r   = smooth_ramp(
                (start - r) / amrex::max(start - full, amrex::Real(1.0e-30)));
            w = amrex::max(w, w_r);
        }

        if (w <= amrex::Real(0.0))
        {
            return;
        }
        const amrex::Real f =
            std::exp(-w * m_dt / amrex::Real(m_params.tau));
        state(i, j, k, c_phi) *= f;
        state(i, j, k, c_Pi) *= f;
    }
};

#endif /* COREMATTERDAMPING_HPP_ */
