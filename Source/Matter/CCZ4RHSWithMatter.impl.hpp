/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#if !defined(CCZ4RHSWITHMATTER_HPP_)
#error "This file should only be included through MatterCCZ4RHS.hpp"
#endif

#ifndef CCZ4RHSWITHMATTER_IMPL_HPP_
#define CCZ4RHSWITHMATTER_IMPL_HPP_
#include "DimensionDefinitions.hpp"

template <class matter_t, class gauge_t, class deriv_t>
CCZ4RHSWithMatter<matter_t, gauge_t, deriv_t>::CCZ4RHSWithMatter(
    CCZ4_params_t<typename gauge_t::params_t> a_params, double a_dx,
    double a_sigma, int a_formulation, double a_G_Newton,
    std::array<double, AMREX_SPACEDIM> a_center, amrex::Real a_time)
    : CCZ4RHS<gauge_t, deriv_t>(a_params, a_dx, a_sigma, a_formulation,
                                0.0 /*No cosmological constant*/),
      m_matter(matter_t()), m_G_Newton(a_G_Newton), m_dx(a_dx),
      m_center(a_center), m_time(a_time)
{
}

template <class matter_t, class gauge_t, class deriv_t>
CCZ4RHSWithMatter<matter_t, gauge_t, deriv_t>::CCZ4RHSWithMatter(
    matter_t a_matter, CCZ4_params_t<typename gauge_t::params_t> a_params,
    double a_dx, double a_sigma, int a_formulation, double a_G_Newton,
    std::array<double, AMREX_SPACEDIM> a_center, amrex::Real a_time)
    : CCZ4RHS<gauge_t, deriv_t>(a_params, a_dx, a_sigma, a_formulation,
                                0.0 /*No cosmological constant*/),
      m_matter(a_matter), m_G_Newton(a_G_Newton), m_dx(a_dx),
      m_center(a_center), m_time(a_time)
{
}

template <class matter_t, class gauge_t, class deriv_t>
template <int formulation, int use_covariant_Z4>
AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
CCZ4RHSWithMatter<matter_t, gauge_t, deriv_t>::operator()(
    const int ix, const int iy, const int iz,
    const amrex::Array4<amrex::Real> &rhs_state,
    const amrex::Array4<amrex::Real const> &state) const
{
    // NB: the vacuum solution needs to be computed elsewhere!
    // This will only compute the matter contribution
    add_matter_contribution(ix, iy, iz, rhs_state, state);
}

template <class matter_t, class gauge_t, class deriv_t>
AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
CCZ4RHSWithMatter<matter_t, gauge_t, deriv_t>::compute_full_rhs(
    const int ix, const int iy, const int iz,
    const amrex::Array4<amrex::Real> &rhs_state,
    const amrex::Array4<amrex::Real const> &state) const
{
    // Vacuum part: the three CCZ4RHS kernels, in the order of
    // Tests/BSSNMatterTest.  compute_A_ij_and_Theta_and_Gamma is templated on
    // the formulation and on covariantZ4, so select the instantiation from the
    // runtime parameters here.  The branch is uniform across a kernel launch.
    this->compute_chi_and_h_ij(ix, iy, iz, rhs_state, state);

    const bool use_bssn     = (this->m_formulation == CCZ4::USE_BSSN);
    const bool covariant_Z4 = this->m_params.covariantZ4;
    if (use_bssn)
    {
        if (covariant_Z4)
        {
            this->template compute_A_ij_and_Theta_and_Gamma<CCZ4::USE_BSSN, 1>(
                ix, iy, iz, rhs_state, state);
        }
        else
        {
            this->template compute_A_ij_and_Theta_and_Gamma<CCZ4::USE_BSSN, 0>(
                ix, iy, iz, rhs_state, state);
        }
    }
    else
    {
        if (covariant_Z4)
        {
            this->template compute_A_ij_and_Theta_and_Gamma<CCZ4::USE_CCZ4, 1>(
                ix, iy, iz, rhs_state, state);
        }
        else
        {
            this->template compute_A_ij_and_Theta_and_Gamma<CCZ4::USE_CCZ4, 0>(
                ix, iy, iz, rhs_state, state);
        }
    }

    this->calculate_gauge_rhs(ix, iy, iz, rhs_state, state);

    // Matter part.  This also applies the Kreiss-Oliger dissipation to every
    // variable, so CCZ4RHS::apply_dissipation must NOT be called as well.
    add_matter_contribution(ix, iy, iz, rhs_state, state);
}

template <class matter_t, class gauge_t, class deriv_t>
AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
CCZ4RHSWithMatter<matter_t, gauge_t, deriv_t>::add_matter_contribution(
    const int ix, const int iy, const int iz,
    const amrex::Array4<amrex::Real> &rhs_state,
    const amrex::Array4<const amrex::Real> &state) const
{
    const amrex::CellData<amrex::Real> &rhs_cell_data =
        rhs_state.cellData(ix, iy, iz);

    const Coordinates coords(amrex::IntVect{AMREX_D_DECL(ix, iy, iz)}, m_dx,
                             m_center);

    // add RHS matter terms from EM Tensor
    add_emtensor_rhs(ix, iy, iz, rhs_state, state);

    // add evolution of matter fields themselves
    MatterDispatch::add_matter_rhs(m_matter, ix, iy, iz, rhs_state, state,
                                   this->m_deriv, coords, m_time);

    // Add dissipation to all terms
    this->m_deriv.add_dissipation(ix, iy, iz, rhs_cell_data, state,
                                  this->m_sigma, NUM_VARS);
}

// Function to add in EM Tensor matter terms to CCZ4 rhs
template <class matter_t, class gauge_t, class deriv_t>
AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
CCZ4RHSWithMatter<matter_t, gauge_t, deriv_t>::add_emtensor_rhs(
    const int ix, const int iy, const int iz,
    const amrex::Array4<amrex::Real> &rhs_state,
    const amrex::Array4<const amrex::Real> &state) const
{
    const amrex::CellData<amrex::Real> &rhs_cell_data =
        rhs_state.cellData(ix, iy, iz);
    const amrex::CellData<const amrex::Real> &state_cell_data =
        state.cellData(ix, iy, iz);

    const typename matter_t::Vars vars(state_cell_data);

    const auto h_UU = CCZ4Geometry::compute_inverse_metric(vars);

    const Coordinates coords(amrex::IntVect{AMREX_D_DECL(ix, iy, iz)}, m_dx,
                             m_center);

    // Calculate elements of the decomposed stress energy tensor
    const auto emtensor = MatterDispatch::compute_emtensor(
        m_matter, ix, iy, iz, state, this->m_deriv, h_UU, coords, m_time);

    // Update RHS for K and Theta depending on formulation
    if (this->m_formulation == CCZ4RHS<>::USE_BSSN)
    {
        rhs_cell_data[c_K] += 4.0 * M_PI * m_G_Newton * vars.lapse() *
                              (emtensor.trS + emtensor.rho);
        rhs_cell_data[c_Theta] = 0.0;
    }
    else
    {
        rhs_cell_data[c_K] += 4.0 * M_PI * m_G_Newton * vars.lapse() *
                              (emtensor.trS - 3 * emtensor.rho);
        rhs_cell_data[c_Theta] +=
            -8.0 * M_PI * m_G_Newton * vars.lapse() * emtensor.rho;
    }

    // Update RHS for other variables
    Tensor::Rank2 S_TF = emtensor.S;

    CCZ4Geometry::make_trace_free(S_TF, vars, h_UU);

    FOR2_SYM(i, j)
    {

        rhs_cell_data[sym_var_idx(c_A11, i, j)] +=
            -8.0 * M_PI * m_G_Newton * vars.chi() * vars.lapse() * S_TF(i, j);
    }

    FOR (i)
    {
        amrex::Real matter_term_Gamma = 0.0;
        FOR (j)
        {
            matter_term_Gamma += -16.0 * M_PI * m_G_Newton * vars.lapse() *
                                 h_UU(i, j) * emtensor.j(j);
        }
        rhs_cell_data[c_Gamma1 + i] += matter_term_Gamma;
    }

    // Add matter contribution to RHS of gauge evolution
    this->m_gauge.rhs_gauge_add_matter_terms(rhs_cell_data, vars, h_UU,
                                             emtensor, m_G_Newton);
}

#endif /* CCZ4RHSWITHMATTER_IMPL_HPP_ */
