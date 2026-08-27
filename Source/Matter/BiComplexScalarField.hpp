#ifndef BICOMPLEXSCALARFIELD_HPP_
#define BICOMPLEXSCALARFIELD_HPP_

#include "BiComplexScalarFieldVars.hpp"
#include "CCZ4Geometry.hpp"
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

//! Two coupled complex scalar fields: a CANONICAL field Phi+ (sign +1) and a
//! PHANTOM field Phi- (sign -1).  All canonical lumps are superposed into Phi+
//! and all exotic (negative-energy) lumps into Phi-, so a single config can
//! carry mixed-sign matter -- the structure the warp/wormhole FTL geometry
//! needs -- while keeping a fixed, small state-variable footprint (8 matter
//! components) independent of the lump count.  Each field is U(1)-symmetric
//! (boson-star binding); only the gravitational coupling sign differs.
class BiComplexScalarField
{
  public:
    BiComplexScalarField() { load_from_inputs(); }

    explicit BiComplexScalarField(double a_mass, double a_lambda,
                                  double a_mu = 0.0,
                                  RLMatterPumpParams a_pump = {})
        : m_potential(a_mass, a_lambda, a_mu), m_pump(a_pump)
    {
    }

    void load_from_inputs()
    {
        GRParmParse pp;
        std::string model;
        pp.load("recipe_matter_model", model, std::string(""));
        if (model != "grtresna_bicomplex_scalar")
        {
            return;
        }
        double mass = 0.0;
        double lam  = 0.0;
        double mu   = 0.0;
        pp.load("recipe_scalar_mass", mass, 0.0);
        pp.load("recipe_scalar_lambda", lam, 0.0);
        pp.load("recipe_scalar_mu", mu, 0.0);
        m_potential = ComplexScalarPotential(mass, lam, mu);
    }

    using Vars = BiComplexScalarFieldVars;

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
    RLMatterPumpParams m_pump{};
};

#include "BiComplexScalarField.impl.hpp"

#endif /* BICOMPLEXSCALARFIELD_HPP_ */
