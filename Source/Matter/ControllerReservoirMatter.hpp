#ifndef CONTROLLER_RESERVOIR_MATTER_HPP_
#define CONTROLLER_RESERVOIR_MATTER_HPP_

#include "CCZ4Geometry.hpp"
#include "Coordinates.hpp"
#include "DimensionDefinitions.hpp"
#include "FourthOrderDerivatives.hpp"
#include "MatterDispatch.hpp"
#include "RLMatterPumpParams.hpp"
#include "RLPumpForce.hpp"
#include "StateVariables.hpp"
#include "Tensor.hpp"

#include <AMReX_GpuQualifiers.H>
#include <AMReX_REAL.H>

//! Decorator: wraps an InnerMatter and adds a controller energy-momentum
//! reservoir (ρ_c, j_{c i}) that absorbs the PD-pump 4-force, so that
//! ∇_μ (T_matter + T_c)^{μν} = 0 up to truncation error.
//!
//! Modes (controller_reservoir_mode):
//!   0 — inactive (this decorator is not instantiated at all)
//!   1 — ledger: evolve reservoir; include in the constraint EMT only
//!   2 — backreaction: as 1, and also source the CCZ4 RHS from it
//! The mode-1 / mode-2 distinction is made by the CALLER, which passes
//! include_emtensor = (mode >= 1) on the constraints path and
//! include_emtensor = (mode >= 2) on the RHS path.
//!
//! Sign conventions (this codebase, verified against the scalar EMT):
//!   ρ      = ½ Σ_A s_A (Π_A² + |∇φ_A|²) + V     [BiComplexScalarField.impl]
//!   j_i    = Σ_A s_A (−Π_A ∂_i φ_A)
//! The pump adds S_A to ∂_t Π_A (a coordinate-time rate, no lapse), hence
//!   ∂_t ρ|_pump   = + Σ_A s_A Π_A S_A       ≡ +f_⊥
//!   ∂_t j_i|_pump = − Σ_A s_A S_A ∂_i φ_A   ≡ −f_i
//! Note the OPPOSITE relative sign: the reservoir must therefore absorb
//! −f_⊥ in the energy equation and +f_i in the momentum equation, and
//! neither source carries a lapse factor.
//!
//! Transport (S_c^{ij} = 0, i.e. a pressureless ledger):
//!   ∂_t ρ_c    = β^k∂_k ρ_c + αKρ_c − α D_i j_c^i − 2 j_c^i ∂_i α − f_⊥
//!   ∂_t j_{ci} = β^k∂_k j_{ci} + αK j_{ci} + j_{ck} ∂_i β^k − ρ_c ∂_i α + f_i
//! which is the standard 3+1 matter conservation system with the pump force
//! as source. Dropping the transport terms (as an earlier revision did) makes
//! ∇_μ T_c^{μν} = −f^ν false and the mode-2 Bianchi argument invalid.
//!
//! IsBicomplex selects the field layout / force-density accessors at
//! compile time.  Derivatives are fetched on demand from the deriv_t object
//! (upstream matter interface), so no nested D1Vars/AdvecVars are needed.
//! Both the plain and the (coords, time) overloads are provided and forward
//! to the inner matter through MatterDispatch, so the inner class need not
//! implement the time-dependent overloads itself.
template <class InnerMatter, bool IsBicomplex>
class ControllerReservoirMatter
{
  public:
    using Vars = typename InnerMatter::Vars;

    ControllerReservoirMatter(InnerMatter a_inner, RLMatterPumpParams a_pump,
                              int a_mode, bool a_include_emtensor)
        : m_inner(a_inner), m_pump(a_pump), m_mode(a_mode),
          m_include_emtensor(a_include_emtensor)
    {
    }

    template <class deriv_t>
    [[nodiscard]] AMREX_GPU_DEVICE emtensor_t compute_emtensor(
        const int ix, const int iy, const int iz,
        const amrex::Array4<const amrex::Real> &state, const deriv_t &a_deriv,
        const Tensor::Rank2 &h_UU) const
    {
        emtensor_t em =
            m_inner.compute_emtensor(ix, iy, iz, state, a_deriv, h_UU);
        add_reservoir_to_emtensor(em, state.cellData(ix, iy, iz));
        return em;
    }

    template <class deriv_t>
    [[nodiscard]] AMREX_GPU_DEVICE emtensor_t compute_emtensor(
        const int ix, const int iy, const int iz,
        const amrex::Array4<const amrex::Real> &state, const deriv_t &a_deriv,
        const Tensor::Rank2 &h_UU, const Coordinates &coords,
        amrex::Real time) const
    {
        emtensor_t em = MatterDispatch::compute_emtensor(
            m_inner, ix, iy, iz, state, a_deriv, h_UU, coords, time);
        add_reservoir_to_emtensor(em, state.cellData(ix, iy, iz));
        return em;
    }

    template <class deriv_t>
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
    add_matter_rhs(const int ix, const int iy, const int iz,
                   const amrex::Array4<amrex::Real> &rhs_state,
                   const amrex::Array4<const amrex::Real> &state,
                   const deriv_t &a_deriv) const
    {
        m_inner.add_matter_rhs(ix, iy, iz, rhs_state, state, a_deriv);
    }

    template <class deriv_t>
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
    add_matter_rhs(const int ix, const int iy, const int iz,
                   const amrex::Array4<amrex::Real> &rhs_state,
                   const amrex::Array4<const amrex::Real> &state,
                   const deriv_t &a_deriv, const Coordinates &coords,
                   amrex::Real time) const
    {
        MatterDispatch::add_matter_rhs(m_inner, ix, iy, iz, rhs_state, state,
                                       a_deriv, coords, time);
        if (m_mode < 1)
        {
            return;
        }
        add_reservoir_rhs(ix, iy, iz, rhs_state, state, a_deriv, coords, time);
    }

  private:
    InnerMatter m_inner;
    RLMatterPumpParams m_pump{};
    int m_mode{0};
    bool m_include_emtensor{false};

    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void add_reservoir_to_emtensor(
        emtensor_t &em,
        const amrex::CellData<const amrex::Real> &cell_data) const
    {
        if (!m_include_emtensor || m_mode < 1)
        {
            return;
        }
        // S_c^{ij} = 0, so only rho and j_i are contributed (trS untouched).
        em.rho += cell_data[c_rho_ctrl];
        em.j(0) += cell_data[c_jctrl1];
        em.j(1) += cell_data[c_jctrl2];
        em.j(2) += cell_data[c_jctrl3];
    }

    //! Reservoir evolution: standard 3+1 conservation with S_c^{ij} = 0 and
    //! the pump 4-force as source. See the class comment for the derivation
    //! and for why the momentum source is +f_i while the energy source is
    //! −f_⊥, and why neither carries a lapse.
    template <class deriv_t>
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
    add_reservoir_rhs(const int ix, const int iy, const int iz,
                      const amrex::Array4<amrex::Real> &rhs_state,
                      const amrex::Array4<const amrex::Real> &state,
                      const deriv_t &a_deriv, const Coordinates &coords,
                      amrex::Real time) const
    {
        const amrex::CellData<amrex::Real> &rhs =
            rhs_state.cellData(ix, iy, iz);
        const amrex::CellData<const amrex::Real> &cell_data =
            state.cellData(ix, iy, iz);
        const Vars vars(cell_data);

        const amrex::Real lapse = vars.lapse();
        const amrex::Real K     = vars.K();
        const amrex::Real chi   = vars.chi();
        const amrex::Real rho_c = cell_data[c_rho_ctrl];

        constexpr int j_comps[3] = {c_jctrl1, c_jctrl2, c_jctrl3};
        const Tensor::Rank1 j_c{cell_data[c_jctrl1], cell_data[c_jctrl2],
                                cell_data[c_jctrl3]};

        const auto h_UU = CCZ4Geometry::compute_inverse_metric(vars);

        // Derivatives of the geometry: d1_shift(k, i) = ∂_i β^k,
        // d1_h(k, l, i) = ∂_i h_{kl}.
        const Tensor::Rank1 d1_chi = a_deriv.d1_scalar(ix, iy, iz, state, c_chi);
        const Tensor::Rank1 d1_lapse =
            a_deriv.d1_scalar(ix, iy, iz, state, c_lapse);
        const Tensor::Rank2 d1_shift =
            a_deriv.d1_vector(ix, iy, iz, state, c_shift1);
        const Tensor::Sym12Rank3 d1_h =
            a_deriv.d1_sym_tensor(ix, iy, iz, state, c_h11);

        // d1_j[k](i) = ∂_i j_{ck}
        const Tensor::Rank1 d1_j[3] = {
            a_deriv.d1_scalar(ix, iy, iz, state, c_jctrl1),
            a_deriv.d1_scalar(ix, iy, iz, state, c_jctrl2),
            a_deriv.d1_scalar(ix, iy, iz, state, c_jctrl3)};

        const Tensor::Rank1 shift_vector{vars.shift(0), vars.shift(1),
                                         vars.shift(2)};
        const amrex::Real advec_rho =
            a_deriv.advec_scalar(ix, iy, iz, state, shift_vector, c_rho_ctrl);
        const amrex::Real advec_j[3] = {
            a_deriv.advec_scalar(ix, iy, iz, state, shift_vector, c_jctrl1),
            a_deriv.advec_scalar(ix, iy, iz, state, shift_vector, c_jctrl2),
            a_deriv.advec_scalar(ix, iy, iz, state, shift_vector, c_jctrl3)};

        // Physical inverse spatial metric γ^{ij} = χ h^{ij}; raise the index.
        Tensor::Rank1 j_cU;
        FOR (i)
        {
            j_cU(i) = 0.0;
            FOR (j) { j_cU(i) += chi * h_UU(i, j) * j_c(j); }
        }

        // D_i j_c^i = ∂_i j_c^i + j_c^i ∂_i ln√γ, with √γ = χ^{-3/2}
        // (det h = 1), so ∂_i ln√γ = −(3/2) ∂_i χ / χ.
        // ∂_i j_c^i = (∂_i χ) h^{ij} j_{cj} + χ (∂_i h^{ij}) j_{cj}
        //             + χ h^{ij} ∂_i j_{cj},
        // and ∂_i h^{ij} = − h^{ik} h^{jl} ∂_i h_{kl}.
        amrex::Real div_j = 0.0;
        FOR (i, j)
        {
            div_j += d1_chi(i) * h_UU(i, j) * j_c(j);
            div_j += chi * h_UU(i, j) * d1_j[j](i);
        }
        FOR (i, j)
        {
            FOR (k, l)
            {
                div_j +=
                    -chi * h_UU(i, k) * h_UU(j, l) * d1_h(k, l, i) * j_c(j);
            }
        }
        const amrex::Real inv_chi = 1.0 / chi;
        FOR (i) { div_j += -1.5 * j_cU(i) * d1_chi(i) * inv_chi; }

        amrex::Real j_dot_dalpha = 0.0;
        FOR (i) { j_dot_dalpha += j_cU(i) * d1_lapse(i); }

        // Pump 4-force from the shared RLPumpForce law (same source as the RHS).
        const RLPumpForceDensity force =
            compute_force(ix, iy, iz, state, a_deriv, cell_data, coords, time);

        rhs[c_rho_ctrl] += advec_rho + lapse * K * rho_c - lapse * div_j -
                           2.0 * j_dot_dalpha - force.f_perp;

        const amrex::Real f_i[3] = {force.f_x, force.f_y, force.f_z};

        FOR (i)
        {
            amrex::Real shift_term = 0.0;
            // j_{ck} ∂_i β^k
            FOR (k) { shift_term += j_c(k) * d1_shift(k, i); }
            rhs[j_comps[i]] += advec_j[i] + lapse * K * j_c(i) + shift_term -
                               rho_c * d1_lapse(i) + f_i[i];
        }
    }

    template <class deriv_t>
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE RLPumpForceDensity
    compute_force(const int ix, const int iy, const int iz,
                  const amrex::Array4<const amrex::Real> &state,
                  const deriv_t &a_deriv,
                  const amrex::CellData<const amrex::Real> &cell_data,
                  const Coordinates &coords, amrex::Real time) const
    {
        const amrex::Real lapse = cell_data[c_lapse];
        if constexpr (IsBicomplex)
        {
            const amrex::Real phi1p = cell_data[c_phi];
            const amrex::Real Pi1p  = cell_data[c_Pi];
            const amrex::Real phi2p = cell_data[c_phi2];
            const amrex::Real Pi2p  = cell_data[c_Pi2];
            const amrex::Real phi1m = cell_data[c_phi_m];
            const amrex::Real Pi1m  = cell_data[c_Pi_m];
            const amrex::Real phi2m = cell_data[c_phi2_m];
            const amrex::Real Pi2m  = cell_data[c_Pi2_m];
            const Tensor::Rank1 d1_phi1p =
                a_deriv.d1_scalar(ix, iy, iz, state, c_phi);
            const Tensor::Rank1 d1_phi2p =
                a_deriv.d1_scalar(ix, iy, iz, state, c_phi2);
            const Tensor::Rank1 d1_phi1m =
                a_deriv.d1_scalar(ix, iy, iz, state, c_phi_m);
            const Tensor::Rank1 d1_phi2m =
                a_deriv.d1_scalar(ix, iy, iz, state, c_phi2_m);
            const RLPumpSources src = RLPumpForce::compute_bicomplex_sources(
                m_pump, coords.x, coords.y, coords.z, time, lapse, phi1p, phi2p,
                Pi1p, Pi2p, phi1m, phi2m, Pi1m, Pi2m);
            return RLPumpForce::force_density_from_sources(
                src, 1.0, Pi1p, Pi2p, d1_phi1p(0), d1_phi1p(1), d1_phi1p(2),
                d1_phi2p(0), d1_phi2p(1), d1_phi2p(2), -1.0, Pi1m, Pi2m,
                d1_phi1m(0), d1_phi1m(1), d1_phi1m(2), d1_phi2m(0),
                d1_phi2m(1), d1_phi2m(2));
        }
        else
        {
            const amrex::Real phi1 = cell_data[c_phi];
            const amrex::Real Pi1  = cell_data[c_Pi];
            const amrex::Real phi2 = cell_data[c_phi2];
            const amrex::Real Pi2  = cell_data[c_Pi2];
            const Tensor::Rank1 d1_phi1 =
                a_deriv.d1_scalar(ix, iy, iz, state, c_phi);
            const Tensor::Rank1 d1_phi2 =
                a_deriv.d1_scalar(ix, iy, iz, state, c_phi2);
            const RLPumpSources src = RLPumpForce::compute_single_field_sources(
                m_pump, coords.x, coords.y, coords.z, time, lapse, phi1, phi2,
                Pi1, Pi2);
            return RLPumpForce::force_density_single(
                src, 1.0, Pi1, Pi2, d1_phi1(0), d1_phi1(1), d1_phi1(2),
                d1_phi2(0), d1_phi2(1), d1_phi2(2));
        }
    }
};

#endif /* CONTROLLER_RESERVOIR_MATTER_HPP_ */
