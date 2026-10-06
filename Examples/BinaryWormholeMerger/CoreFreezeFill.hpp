/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef COREFREEZEFILL_HPP_
#define COREFREEZEFILL_HPP_

#include "StateVariables.hpp"

#include <AMReX_Array.H>
#include <AMReX_Array4.H>
#include <AMReX_GpuQualifiers.H>
#include <AMReX_Math.H>

#include <array>
#include <cmath>

/* Smooth interior fill ("turduckening") for the post-collapse core:

     d/dt u_n  ->  (1 - W(r)) * d/dt u_n     for EVERY evolved variable n

   so the region inside radius_full stops evolving entirely and becomes
   static junk data, while the exterior -- including the whole wave zone --
   evolves untouched.  Third rung of the M9 formulation ladder in
   research/merger/Plan.md, and the one the campaign's own measurements
   point at.

   WHY THIS AND NOT THE EARLIER MODULES.  Three failure modes were measured
   before this module was written, and the design answers each:

     * CoreMatterDamping lost a RACE.  Deleting the phantom at rate 1/tau
       competes with its growth; the whole (window, rate) plane was swept
       and the optimum (tau ~ 0.05) buys ~0.4 code units, full stop.  A
       fill has no rate -- the RHS is multiplied by zero -- so it cannot
       lose a race, and, unlike damping, it may therefore be engaged LATE.
       That asymmetry is what makes the causal budget below close.

     * CoreLapseFreeze with freeze_shift died in 0.24 code units, the
       fastest death on record: it froze the shift and B while the metric
       and matter kept evolving, so the frozen sector was driven by
       neighbours it could not answer.  A PARTIAL freeze is worse than
       none.  This module takes every variable in [0, NUM_VARS) or none.

     * The M4 causal seal missed the killer.  Its radius was chosen from
       the horizon (r < 0.95), but the blowup was then imaged at r ~ 1-2,
       at and OUTSIDE the trapped surface.  This window's radius is set
       from the measured failure site instead -- expect radius_full ~ 1.2
       to 1.5 and radius_start ~ 1.5 to 1.9 -- and is deliberately NOT
       claimed to be causally hidden.

   CAUSALITY, STATED HONESTLY.  The fill is not inside a horizon, so its
   influence propagates outward at the speed of light.  Contamination from
   radius r_s engaged at t_e cannot reach extraction radius R before

       t_contam = t_e + (R - r_s).

   The campaign needs R = 14 clean over t = 58-65.5 (the collapse arrives
   58-61; horizon formation 65.5).  Engaging at t_e = 53.4 with r_s = 1.5
   gives t_contam = 65.9 -- the entire required window is clean, with the
   collapse core clean by ~5 units.  This is why the M4e refinement ladder
   matters even though refinement is not a cure: each extra AMR level pushes
   the wall later, which pushes the latest safe engagement later, which
   widens this margin.  Every run using this module must print the arrival
   plot next to the waveform.

   VALIDATION replaces the (unavailable) horizon-seal argument with the
   standard excision-radius insensitivity test: two arms at different
   (radius_full, radius_start) must agree at R = 14 to the few-% level,
   over and above the M6 overlap against the undamped arms.  If the
   waveform moves when the fill radius moves, the fill is in the physics.

   THE TAPER.  W is the same C^2 quintic smootherstep used by
   CoreLapseFreeze (continuous first and second derivatives at both ends),
   because this weight multiplies a RHS the finite differencing then
   differentiates; a hard boolean cut hands the stencil a discontinuous RHS
   and dies on the spot.  The blend zone -- radius_full to radius_start --
   is where a frozen interior meets a live exterior, and it is the one
   place this scheme can fail.  Keep it wide (many cells: at dx = 0.03125 a
   0.4-wide ramp is ~13 cells) and watch it in the frames.

   No snapshot is stored and no extra state is carried: "frozen" is
   expressed as "zero right-hand side", so the interior holds whatever it
   held when the window engaged, and the module is automatically correct
   across regrids, restarts and checkpoints.

   INTERACTION WITH CoreMatterDamping, stated because it is not obvious.
   The damping is applied in specificAdvance(), to the state, NOT to the
   right-hand side -- so it is outside this module's reach and keeps acting
   inside the fill.  That is deliberate and benign: the intended arm runs
   the tau = 0.05 ring from t = 50 (it is what buys the later wall, hence
   the later safe engagement) and the fill from shortly before that wall,
   after which the core is frozen EXCEPT that the phantom continues to
   decay exponentially towards zero there.  A smooth monotone relaxation
   cannot steepen into the shock this module exists to prevent.  What must
   NOT be done is adding a new RHS contributor after the fill in
   specificEvalRHS -- that would be a partial freeze.  If a strictly frozen
   core is ever wanted, disable the damping rather than reaching across
   module boundaries from here.

   Own module, default off: no archived run changes behaviour. */
struct CoreFreezeFill
{
    struct params_t
    {
        bool enabled{false};
        //! Zero weight at and outside this radius (0 = module inert).  Set
        //! from the measured failure site, not from the horizon.
        double radius_start{0.0};
        //! Full weight (evolution fully stopped) at and inside this radius.
        double radius_full{0.0};
        //! Window engages only at t >= from_time.  Engage LATE -- after the
        //! collapse has finished sourcing the burst, shortly before the
        //! wall -- so the frozen region is as small a lie as possible and
        //! the causal budget above stays wide.
        double from_time{0.0};
        //! Centre of the window (wired to the grid centre).
        std::array<double, AMREX_SPACEDIM> grid_center{};
    };

    params_t m_params;
    bool m_active{false};
    amrex::GpuArray<amrex::Real, AMREX_SPACEDIM> m_dx{};
    amrex::GpuArray<amrex::Real, AMREX_SPACEDIM> m_prob_lo{};
    amrex::GpuArray<amrex::Real, AMREX_SPACEDIM> m_center{};

    CoreFreezeFill(const params_t &a_params,
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
    operator()(int i, int j, int k, const amrex::Array4<amrex::Real> &rhs) const
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

        // Every evolved variable or none: a partial freeze drives the frozen
        // sector with neighbours it cannot answer (measured fatal in 0.24
        // code units by CoreLapseFreeze's freeze_shift guard).
        const amrex::Real keep = amrex::Real(1.0) - w;
        for (int n = 0; n < NUM_VARS; ++n)
        {
            rhs(i, j, k, n) *= keep;
        }
    }
};

#endif /* COREFREEZEFILL_HPP_ */
