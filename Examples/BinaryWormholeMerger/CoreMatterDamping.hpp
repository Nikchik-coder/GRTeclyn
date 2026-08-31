/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef COREMATTERDAMPING_HPP_
#define COREMATTERDAMPING_HPP_

#include "StateVariables.hpp"

#include <AMReX_Array4.H>
#include <AMReX_GpuQualifiers.H>
#include <AMReX_Math.H>

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
   collapsed region, drive phi and Pi exponentially to zero.  The region is
   identified by the LAPSE, and the window must reach the scalar bulk: a
   first attempt with lapse_start = 1e-6 covered only ~3 finest cells and
   moved the death from t = 52.07 to t = 52.09.  Measured on the same
   merger at t = 51.5, the collapsed scalar (|phi| up to 0.53) sits at
   lapse 1e-6..3e-2, and the lapse < 3e-2 contour reaches r = 0.63 while
   the common apparent horizon sits at r = 0.875 -- so the default window
   (3e-2 -> 1e-3) is strictly inside the trapped surface: no signal from
   the damped region can reach the wave zone, and the exterior is untouched
   by construction.  Uncollapsed throats sit at lapse ~ 2e-1, still an
   order of magnitude above the ramp start.  The ramp is smooth (cosine in
   log10 lapse) so the damping boundary does not itself become a new sharp
   edge.

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
    };

    params_t m_params;
    amrex::Real m_dt{0.0};

    CoreMatterDamping(const params_t &a_params, amrex::Real a_dt)
        : m_params(a_params), m_dt(a_dt)
    {
    }

    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
    operator()(int i, int j, int k,
               const amrex::Array4<amrex::Real> &state) const
    {
        const amrex::Real lapse = state(i, j, k, c_lapse);
        if (lapse >= amrex::Real(m_params.lapse_start))
        {
            return;
        }
        const amrex::Real hi =
            std::log10(amrex::Real(m_params.lapse_start));
        const amrex::Real lo = std::log10(amrex::Real(m_params.lapse_full));
        const amrex::Real l10 =
            std::log10(amrex::max(lapse, amrex::Real(1.0e-300)));
        amrex::Real w = (hi - l10) / amrex::max(hi - lo, amrex::Real(1.0e-30));
        w = amrex::min(amrex::max(w, amrex::Real(0.0)), amrex::Real(1.0));
        w = amrex::Real(0.5) * (amrex::Real(1.0) - std::cos(amrex::Real(M_PI) * w));
        const amrex::Real f =
            std::exp(-w * m_dt / amrex::Real(m_params.tau));
        state(i, j, k, c_phi) *= f;
        state(i, j, k, c_Pi) *= f;
    }
};

#endif /* COREMATTERDAMPING_HPP_ */
