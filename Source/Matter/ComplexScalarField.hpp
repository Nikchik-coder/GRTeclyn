#ifndef COMPLEXSCALARFIELD_HPP_
#define COMPLEXSCALARFIELD_HPP_

#include "CCZ4Geometry.hpp"
#include "ComplexScalarFieldVars.hpp"
#include "ComplexScalarPotential.hpp"
#include "Coordinates.hpp"
#include "DimensionDefinitions.hpp"
#include "FourthOrderDerivatives.hpp"
#include "GRParmParse.hpp"
#include "RLMatterPumpParams.hpp"
#include "RLPumpForce.hpp"
#include "ScalarFieldKernels.hpp"
#include "StateVariables.hpp"
#include "Tensor.hpp"
#include "TensorAlgebra.hpp"

//! Canonical complex scalar stored as two real components (phi1, Pi1), (phi2, Pi2).
//! Phi = phi1 + i phi2 with coupled potential V(|Phi|^2).
class ComplexScalarField
{
  public:
    ComplexScalarField() { load_from_inputs(); }

    explicit ComplexScalarField(double a_mass, double a_lambda,
                                double a_sign = 1.0, double a_mu = 0.0,
                                RLMatterPumpParams a_pump = {})
        : m_potential(a_mass, a_lambda, a_mu), m_sign(a_sign), m_pump(a_pump)
    {
    }

    void load_from_inputs()
    {
        GRParmParse pp;
        std::string model;
        pp.load("recipe_matter_model", model, std::string(""));
        if (model != "grtresna_complex_scalar")
        {
            return;
        }
        double mass = 0.0;
        double lam  = 0.0;
        double sign = 1.0;
        double mu   = 0.0;
        pp.load("recipe_scalar_mass", mass, 0.0);
        pp.load("recipe_scalar_lambda", lam, 0.0);
        pp.load("recipe_scalar_sign", sign, 1.0);
        pp.load("recipe_scalar_mu", mu, 0.0);
        m_potential = ComplexScalarPotential(mass, lam, mu);
        m_sign = sign;
    }

    using Vars = ComplexScalarFieldVars;

    template <class deriv_t>
    [[nodiscard]] AMREX_GPU_DEVICE emtensor_t compute_emtensor(
        const int ix, const int iy, const int iz,
        const amrex::Array4<const amrex::Real> &state, const deriv_t &a_deriv,
        const Tensor::Rank2 &h_UU) const;

    template <class deriv_t>
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
    add_matter_rhs(const int ix, const int iy, const int iz,
                   const amrex::Array4<amrex::Real> &rhs_state,
                   const amrex::Array4<const amrex::Real> &state,
                   const deriv_t &a_deriv) const;

    //! As above plus the pump source terms, which need position and time.
    template <class deriv_t>
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
    add_matter_rhs(const int ix, const int iy, const int iz,
                   const amrex::Array4<amrex::Real> &rhs_state,
                   const amrex::Array4<const amrex::Real> &state,
                   const deriv_t &a_deriv, const Coordinates &coords,
                   amrex::Real time) const;

  private:
    ComplexScalarPotential m_potential;
    double m_sign{1.0}; // +1 canonical, -1 phantom (flips T_ab)
    RLMatterPumpParams m_pump{};
};

#include "ComplexScalarField.impl.hpp"

#endif /* COMPLEXSCALARFIELD_HPP_ */
