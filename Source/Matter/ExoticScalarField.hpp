/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef EXOTICSCALARFIELD_HPP_
#define EXOTICSCALARFIELD_HPP_

#include "CCZ4Geometry.hpp"
#include "Coordinates.hpp"
#include "DefaultPotential.hpp"
#include "DimensionDefinitions.hpp"
#include "FourthOrderDerivatives.hpp"
#include "GRParmParse.hpp"
#include "ScalarFieldKernels.hpp"
#include "ScalarFieldVars.hpp"
#include "StateVariables.hpp" //This files needs NUM_VARS, total num of components
#include "Tensor.hpp"
#include "TensorAlgebra.hpp"

#include <array>

//!  Phantom ("exotic") real scalar field supporting a wormhole throat.
/*!
     Same field equations as ScalarField, but the stress-energy tensor enters
     Einstein's equations with the factor -support_strength, i.e. with the
     phantom sign that violates the null energy condition.  The strength can be
     ramped down in time (support_schedule) with an optional causal delay from
     the throat (local_support_strength), which is why the EM tensor also has a
     (coords, time) overload: the drivers pick it through MatterDispatch.
     \sa MatterCCZ4(), ConstraintsMatter()
*/
template <class potential_t = DefaultPotential> class ExoticScalarField
{
  protected:
    potential_t m_potential;
    double m_support_strength;
    double m_support_ramp_start;
    double m_support_ramp_duration;
    double m_support_causal_speed;
    int m_metric_type;
    double m_throat_radius_A;
    double m_throat_radius_B;
    std::array<double, AMREX_SPACEDIM> m_centerA;
    std::array<double, AMREX_SPACEDIM> m_centerB;
    //! The local copy of the potential

    [[nodiscard]] AMREX_GPU_HOST_DEVICE AMREX_FORCE_INLINE double
    support_schedule(amrex::Real time) const;

    [[nodiscard]] AMREX_GPU_HOST_DEVICE AMREX_FORCE_INLINE amrex::Real
    nearest_throat_radius(const Coordinates &coords) const;

    [[nodiscard]] AMREX_GPU_HOST_DEVICE AMREX_FORCE_INLINE double
    local_support_strength(const Coordinates &coords, amrex::Real time) const;

    //! EM tensor for a given (already scheduled) support strength
    template <class deriv_t>
    [[nodiscard]] AMREX_GPU_DEVICE emtensor_t emtensor_with_strength(
        const int ix, const int iy, const int iz,
        const amrex::Array4<const amrex::Real> &state, const deriv_t &a_deriv,
        const Tensor::Rank2 &h_UU, double support_strength) const;

  public:
    //!  Constructor of class ExoticScalarField, inputs are the matter parameters.
    ExoticScalarField(potential_t a_potential = potential_t(),
                      double a_support_strength = 1.0)
        : m_potential(a_potential), m_support_strength(a_support_strength),
          m_support_ramp_start(-1.0), m_support_ramp_duration(5.0),
          m_support_causal_speed(0.0), m_metric_type(1),
          m_throat_radius_A(1.0), m_throat_radius_B(1.0), m_centerA{0.0},
          m_centerB{0.0}
    {
        GRParmParse pp;
        if (a_support_strength == 1.0)
            pp.load("wormhole_support_strength", m_support_strength, 1.0);

        pp.load("wormhole_support_ramp_start", m_support_ramp_start, -1.0);
        pp.load("wormhole_support_ramp_duration", m_support_ramp_duration, 5.0);
        pp.load("wormhole_support_causal_speed", m_support_causal_speed, 0.0);
        pp.load("wormhole_metric_type", m_metric_type, 1);
        pp.load("wormhole_throat_radius_A", m_throat_radius_A, 1.0);
        pp.load("wormhole_throat_radius_B", m_throat_radius_B, m_throat_radius_A);

        std::array<double, AMREX_SPACEDIM> default_centerA = {0.0, 0.0, 0.0};
        pp.load("wormhole_centerA", m_centerA, default_centerA);

        std::array<double, AMREX_SPACEDIM> default_centerB = {
            -m_centerA[0], -m_centerA[1], -m_centerA[2]};
        pp.load("wormhole_centerB", m_centerB, default_centerB);
    }

    using Vars = ScalarFieldVars;

    //! The function which calculates the EM Tensor, given the vars and
    //! derivatives, including the potential (constant support strength)
    template <class deriv_t>
    [[nodiscard]] AMREX_GPU_DEVICE emtensor_t compute_emtensor(
        const int ix, const int iy, const int iz,
        const amrex::Array4<const amrex::Real> &state, const deriv_t &a_deriv,
        const Tensor::Rank2 &h_UU) const;

    //! As above, with the support strength scheduled in time and space
    template <class deriv_t>
    [[nodiscard]] AMREX_GPU_DEVICE emtensor_t compute_emtensor(
        const int ix, const int iy, const int iz,
        const amrex::Array4<const amrex::Real> &state, const deriv_t &a_deriv,
        const Tensor::Rank2 &h_UU, const Coordinates &coords,
        amrex::Real time) const;

    //! The function which adds in the RHS for the matter field vars,
    //! including the potential
    template <class deriv_t>
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
    add_matter_rhs(const int ix, const int iy, const int iz,
                   const amrex::Array4<amrex::Real> &rhs_state,
                   const amrex::Array4<const amrex::Real> &state,
                   const deriv_t &a_deriv) const;
};

#include "ExoticScalarField.impl.hpp"

#endif /* EXOTICSCALARFIELD_HPP_ */
