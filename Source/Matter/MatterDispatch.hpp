/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef MATTERDISPATCH_HPP_
#define MATTERDISPATCH_HPP_

#include "CCZ4Geometry.hpp"
#include "Coordinates.hpp"
#include "Tensor.hpp"

#include <AMReX_Array4.H>
#include <AMReX_REAL.H>

#include <type_traits>
#include <utility>

//! Compile-time dispatch between the upstream matter interface and the
//! extended (coords, time) interface used by the pump / trajectory / support
//! matter classes of this fork.
//!
//! Upstream (PR #172) contract every matter class must provide:
//!
//!   emtensor_t compute_emtensor(ix, iy, iz, state, deriv, h_UU) const;
//!   void add_matter_rhs(ix, iy, iz, rhs_state, state, deriv) const;
//!
//! Optional extension, detected here and preferred when present:
//!
//!   emtensor_t compute_emtensor(ix, iy, iz, state, deriv, h_UU,
//!                               const Coordinates &coords, Real time) const;
//!   void add_matter_rhs(ix, iy, iz, rhs_state, state, deriv,
//!                       const Coordinates &coords, Real time) const;
//!
//! The drivers (CCZ4RHSWithMatter, ConstraintsWithMatter, Weyl4WithMatter)
//! always go through these helpers, so upstream's own matter classes
//! (ScalarField) compile untouched while ours keep their time dependence.
namespace MatterDispatch
{

template <class matter_t, class deriv_t, class = void>
struct has_time_emtensor : std::false_type
{
};

template <class matter_t, class deriv_t>
struct has_time_emtensor<
    matter_t, deriv_t,
    std::void_t<decltype(std::declval<const matter_t &>().compute_emtensor(
        0, 0, 0, std::declval<const amrex::Array4<const amrex::Real> &>(),
        std::declval<const deriv_t &>(), std::declval<const Tensor::Rank2 &>(),
        std::declval<const Coordinates &>(), std::declval<amrex::Real>()))>>
    : std::true_type
{
};

template <class matter_t, class deriv_t>
inline constexpr bool has_time_emtensor_v =
    has_time_emtensor<matter_t, deriv_t>::value;

template <class matter_t, class deriv_t, class = void>
struct has_time_rhs : std::false_type
{
};

template <class matter_t, class deriv_t>
struct has_time_rhs<
    matter_t, deriv_t,
    std::void_t<decltype(std::declval<const matter_t &>().add_matter_rhs(
        0, 0, 0, std::declval<const amrex::Array4<amrex::Real> &>(),
        std::declval<const amrex::Array4<const amrex::Real> &>(),
        std::declval<const deriv_t &>(), std::declval<const Coordinates &>(),
        std::declval<amrex::Real>()))>> : std::true_type
{
};

template <class matter_t, class deriv_t>
inline constexpr bool has_time_rhs_v = has_time_rhs<matter_t, deriv_t>::value;

//! Energy-momentum tensor, using the (coords, time) overload when the matter
//! class has one.
template <class matter_t, class deriv_t>
[[nodiscard]] AMREX_GPU_DEVICE AMREX_FORCE_INLINE emtensor_t
compute_emtensor(const matter_t &matter, const int ix, const int iy,
                 const int iz, const amrex::Array4<const amrex::Real> &state,
                 const deriv_t &a_deriv, const Tensor::Rank2 &h_UU,
                 const Coordinates &coords, const amrex::Real time)
{
    if constexpr (has_time_emtensor_v<matter_t, deriv_t>)
    {
        return matter.compute_emtensor(ix, iy, iz, state, a_deriv, h_UU,
                                       coords, time);
    }
    else
    {
        return matter.compute_emtensor(ix, iy, iz, state, a_deriv, h_UU);
    }
}

//! Matter-field evolution, using the (coords, time) overload when the matter
//! class has one.
template <class matter_t, class deriv_t>
AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
add_matter_rhs(const matter_t &matter, const int ix, const int iy,
               const int iz, const amrex::Array4<amrex::Real> &rhs_state,
               const amrex::Array4<const amrex::Real> &state,
               const deriv_t &a_deriv, const Coordinates &coords,
               const amrex::Real time)
{
    if constexpr (has_time_rhs_v<matter_t, deriv_t>)
    {
        matter.add_matter_rhs(ix, iy, iz, rhs_state, state, a_deriv, coords,
                              time);
    }
    else
    {
        matter.add_matter_rhs(ix, iy, iz, rhs_state, state, a_deriv);
    }
}

} // namespace MatterDispatch

#endif /* MATTERDISPATCH_HPP_ */
