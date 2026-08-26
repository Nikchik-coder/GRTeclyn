/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef NOMATTER_HPP_
#define NOMATTER_HPP_

#include "CCZ4Geometry.hpp"
#include "CCZ4Vars.hpp"
#include "ScalarFieldKernels.hpp"
#include "Tensor.hpp"

//! Matter model for geometry-only controls.
class NoMatter
{
  public:
    using Vars = CCZ4Vars;

    template <class deriv_t>
    [[nodiscard]] AMREX_GPU_DEVICE emtensor_t
    compute_emtensor(const int /*ix*/, const int /*iy*/, const int /*iz*/,
                     const amrex::Array4<const amrex::Real> & /*state*/,
                     const deriv_t & /*a_deriv*/,
                     const Tensor::Rank2 & /*h_UU*/) const
    {
        emtensor_t out;
        ScalarFieldKernels::zero(out);
        return out;
    }

    template <class deriv_t>
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
    add_matter_rhs(const int /*ix*/, const int /*iy*/, const int /*iz*/,
                   const amrex::Array4<amrex::Real> & /*rhs_state*/,
                   const amrex::Array4<const amrex::Real> & /*state*/,
                   const deriv_t & /*a_deriv*/) const
    {
    }
};

#endif /* NOMATTER_HPP_ */
