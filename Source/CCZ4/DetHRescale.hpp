/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef DETHRESCALE_HPP_
#define DETHRESCALE_HPP_

#include "CCZ4Vars.hpp"
#include "StateVariables.hpp"
#include "Tensor.hpp"

#include <cmath>

/// Enforces det(h~_ij) = 1 algebraically, h~_ij -> h~_ij det^(-1/3), the way
/// McLachlan's enforce step does beside its trace-A~ removal.  chi and A~_ij
/// are left alone: the deviation from unit determinant is a truncation error
/// of the same order as the rescale, and touching chi would move the physical
/// metric.  Meant to run immediately before TraceARemoval so the trace is
/// removed against the rescaled metric.  Opt-in from the example (default off).
class DetHRescale
{
  public:
    DetHRescale() = default;

    AMREX_GPU_DEVICE void
    operator()(int ix, int iy, int iz,
               const amrex::Array4<amrex::Real> &state) const
    {
        const amrex::CellData<amrex::Real> &cd = state.cellData(ix, iy, iz);
        const amrex::Real h11 = cd[c_h11], h12 = cd[c_h12], h13 = cd[c_h13];
        const amrex::Real h22 = cd[c_h22], h23 = cd[c_h23], h33 = cd[c_h33];
        const amrex::Real det = h11 * (h22 * h33 - h23 * h23) -
                                h12 * (h12 * h33 - h23 * h13) +
                                h13 * (h12 * h23 - h22 * h13);
        if (det > 0.0)
        {
            const amrex::Real s = std::pow(det, -1.0 / 3.0);
            cd[c_h11] *= s;
            cd[c_h12] *= s;
            cd[c_h13] *= s;
            cd[c_h22] *= s;
            cd[c_h23] *= s;
            cd[c_h33] *= s;
        }
    }
};

#endif /* DETHRESCALE_HPP_ */
