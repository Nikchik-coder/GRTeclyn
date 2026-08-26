/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef DUSTMATTER_HPP_
#define DUSTMATTER_HPP_

#include "CCZ4Geometry.hpp"
#include "DustMatterVars.hpp"
#include "Tensor.hpp"
#include "TensorAlgebra.hpp"

/// Pressureless dust with rest-mass density and 3-velocity (simplified advection).
class DustMatter
{
  public:
    using Vars = DustMatterVars;

    template <class deriv_t>
    [[nodiscard]] AMREX_GPU_DEVICE emtensor_t
    compute_emtensor(const int ix, const int iy, const int iz,
                     const amrex::Array4<const amrex::Real> &state,
                     const deriv_t & /*a_deriv*/, const Tensor::Rank2 &h_UU) const
    {
        const Vars vars(state.cellData(ix, iy, iz));
        emtensor_t out;
        const amrex::Real rho = amrex::max(vars.dust_rho(), amrex::Real(0.0));
        const amrex::Real alpha = vars.lapse();
        const amrex::Real inv_alpha = 1.0 / alpha;
        Tensor::Rank1 u_low;
        FOR (i)
        {
            u_low(i) = alpha * vars.dust_v(i) - vars.shift(i);
        }
        const amrex::Real u0 = -alpha;
        FOR (i, j)
        {
            out.S(i, j) = rho * u_low(i) * u_low(j) / (alpha * alpha);
        }
        out.rho = rho;
        out.trS = vars.chi() * TensorAlgebra::compute_trace(out.S, h_UU);
        FOR (i)
        {
            out.j(i) = rho * u0 * (vars.dust_v(i) + vars.shift(i) * inv_alpha);
        }
        return out;
    }

    template <class deriv_t>
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
    add_matter_rhs(const int /*ix*/, const int /*iy*/, const int /*iz*/,
                   const amrex::Array4<amrex::Real> & /*rhs_state*/,
                   const amrex::Array4<const amrex::Real> & /*state*/,
                   const deriv_t & /*a_deriv*/) const
    {
        // Prescribed/co-moving dust for transport studies; full Valencia
        // conservative hydro evolution is future work.
    }
};

#endif /* DUSTMATTER_HPP_ */
