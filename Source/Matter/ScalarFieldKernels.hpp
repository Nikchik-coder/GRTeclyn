/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef SCALARFIELDKERNELS_HPP_
#define SCALARFIELDKERNELS_HPP_

#include "CCZ4Geometry.hpp"
#include "CCZ4Vars.hpp"
#include "DimensionDefinitions.hpp"
#include "Tensor.hpp"

//! Pieces of the Klein-Gordon right-hand side shared by every real scalar
//! component evolved in this fork (single, complex, bi-complex, independent
//! lumps).  Kept as free functions so the matter classes only differ in their
//! field layout and potential.
namespace ScalarFieldKernels
{

//! The spatial-derivative part of d_t Pi for one real component:
//!   h^{ij} ( -1/2 lapse d_j chi d_i phi + chi lapse D_i D_j phi
//!            + chi d_i lapse d_j phi ) - chi lapse h^{ij} Gamma^k_{ij} d_k phi
//! (the non-conformal parts of the Christoffel symbol enter through d1_chi).
[[nodiscard]] AMREX_GPU_DEVICE AMREX_FORCE_INLINE amrex::Real
Pi_gradient_terms(const CCZ4Vars &vars, const Tensor::Rank2 &h_UU,
                  const chris_t &chris, const Tensor::Rank1 &d1_chi,
                  const Tensor::Rank1 &d1_lapse, const Tensor::Rank1 &d1_phi,
                  const Tensor::Sym12Rank2 &d2_phi)
{
    amrex::Real out = 0.0;
    FOR (i, j)
    {
        out += h_UU(i, j) * (-0.5 * d1_chi(j) * vars.lapse() * d1_phi(i) +
                             vars.chi() * vars.lapse() * d2_phi(i, j) +
                             vars.chi() * d1_lapse(i) * d1_phi(j));
        FOR (k)
        {
            out += -vars.chi() * vars.lapse() * h_UU(i, j) *
                   chris.ULL(k, i, j) * d1_phi(k);
        }
    }
    return out;
}

//! Kinetic invariant Vt = -Pi^2 + chi h^{ij} d_i phi d_j phi.
[[nodiscard]] AMREX_GPU_DEVICE AMREX_FORCE_INLINE amrex::Real
kinetic_invariant(const CCZ4Vars &vars, const Tensor::Rank2 &h_UU,
                  const amrex::Real Pi, const Tensor::Rank1 &d1_phi)
{
    amrex::Real Vt = -Pi * Pi;
    FOR (i, j)
    {
        Vt += vars.chi() * h_UU(i, j) * d1_phi(i) * d1_phi(j);
    }
    return Vt;
}

//! Set every component of an emtensor_t to zero.
AMREX_GPU_DEVICE AMREX_FORCE_INLINE void zero(emtensor_t &out)
{
    out.rho = 0.0;
    out.trS = 0.0;
    FOR (i)
    {
        out.j(i) = 0.0;
        FOR (j) { out.S(i, j) = 0.0; }
    }
}

} // namespace ScalarFieldKernels

#endif /* SCALARFIELDKERNELS_HPP_ */
