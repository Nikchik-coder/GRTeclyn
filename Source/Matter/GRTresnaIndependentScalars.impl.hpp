#if !defined(GRTRESNA_INDEPENDENT_SCALARS_HPP_)
#error "This file should only be included through GRTresnaIndependentScalars.hpp"
#endif

#ifndef GRTRESNA_INDEPENDENT_SCALARS_IMPL_HPP_
#define GRTRESNA_INDEPENDENT_SCALARS_IMPL_HPP_

template <class deriv_t>
AMREX_GPU_DEVICE AMREX_FORCE_INLINE emtensor_t
GRTresnaIndependentScalars::compute_emtensor(
    const int ix, const int iy, const int iz,
    const amrex::Array4<const amrex::Real> &state, const deriv_t &a_deriv,
    const Tensor::Rank2 &h_UU) const
{
    const amrex::CellData<const amrex::Real> &state_cell_data =
        state.cellData(ix, iy, iz);
    const Vars vars(state_cell_data);

    emtensor_t out;
    ScalarFieldKernels::zero(out);

    for (int k = 0; k < m_num_fields; ++k)
    {
        const amrex::Real sign = static_cast<amrex::Real>(m_signs[k]);
        const Tensor::Rank1 d1_phi =
            a_deriv.d1_scalar(ix, iy, iz, state, c_phi_lump_index(k));
        const amrex::Real Pi_k = vars.Pi(k);

        const amrex::Real Vt_k =
            ScalarFieldKernels::kinetic_invariant(vars, h_UU, Pi_k, d1_phi);

        out.rho += sign * (0.5 * Pi_k * Pi_k + 0.5 * Vt_k);
        FOR (i)
        {
            out.j(i) += sign * (-d1_phi(i) * Pi_k);
        }
        FOR (i, j)
        {
            out.S(i, j) += sign * (-0.5 * vars.h(i, j) * Vt_k / vars.chi() +
                                   d1_phi(i) * d1_phi(j));
        }
    }

    amrex::Real V_of_phi = 0.0;
    amrex::Real dVdphi   = 0.0;
    m_potential.compute_potential(V_of_phi, dVdphi, phi_sum(vars));
    out.rho += V_of_phi;
    FOR (i, j)
    {
        out.S(i, j) -= vars.h(i, j) * V_of_phi / vars.chi();
    }
    out.trS = vars.chi() * TensorAlgebra::compute_trace(out.S, h_UU);

    return out;
}

template <class deriv_t>
AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
GRTresnaIndependentScalars::add_matter_rhs(
    const int ix, const int iy, const int iz,
    const amrex::Array4<amrex::Real> &rhs_state,
    const amrex::Array4<const amrex::Real> &state, const deriv_t &a_deriv) const
{
    const amrex::CellData<amrex::Real> &rhs = rhs_state.cellData(ix, iy, iz);
    const amrex::CellData<const amrex::Real> &state_cell_data =
        state.cellData(ix, iy, iz);
    const Vars vars(state_cell_data);

    const auto h_UU  = CCZ4Geometry::compute_inverse_metric(vars);
    const auto d1_h  = a_deriv.d1_sym_tensor(ix, iy, iz, state, c_h11);
    const auto chris = CCZ4Geometry::compute_christoffel(d1_h, h_UU);

    const Tensor::Rank1 d1_chi   = a_deriv.d1_scalar(ix, iy, iz, state, c_chi);
    const Tensor::Rank1 d1_lapse = a_deriv.d1_scalar(ix, iy, iz, state, c_lapse);

    const Tensor::Rank1 shift_vector{vars.shift(0), vars.shift(1),
                                     vars.shift(2)};

    amrex::Real V_of_phi = 0.0;
    amrex::Real dVdphi   = 0.0;
    m_potential.compute_potential(V_of_phi, dVdphi, phi_sum(vars));

    for (int k = 0; k < m_num_fields; ++k)
    {
        const int c_phi_k = c_phi_lump_index(k);
        const int c_Pi_k  = c_Pi_lump_index(k);

        const Tensor::Rank1 d1_phi =
            a_deriv.d1_scalar(ix, iy, iz, state, c_phi_k);
        const Tensor::Sym12Rank2 d2_phi =
            a_deriv.d2_scalar(ix, iy, iz, state, c_phi_k);
        const amrex::Real advec_phi =
            a_deriv.advec_scalar(ix, iy, iz, state, shift_vector, c_phi_k);
        const amrex::Real advec_Pi =
            a_deriv.advec_scalar(ix, iy, iz, state, shift_vector, c_Pi_k);

        rhs[c_phi_k] = vars.lapse() * vars.Pi(k) + advec_phi;
        rhs[c_Pi_k] =
            vars.lapse() * (vars.K() * vars.Pi(k) - dVdphi) + advec_Pi +
            ScalarFieldKernels::Pi_gradient_terms(vars, h_UU, chris, d1_chi,
                                                  d1_lapse, d1_phi, d2_phi);
    }
}

template <class deriv_t>
AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
GRTresnaIndependentScalars::add_matter_rhs(
    const int ix, const int iy, const int iz,
    const amrex::Array4<amrex::Real> &rhs_state,
    const amrex::Array4<const amrex::Real> &state, const deriv_t &a_deriv,
    const Coordinates &coords, const amrex::Real time) const
{
    add_matter_rhs(ix, iy, iz, rhs_state, state, a_deriv);

    if (m_pump.num_sites < 1)
    {
        return;
    }

    const amrex::CellData<amrex::Real> &rhs = rhs_state.cellData(ix, iy, iz);

    // One spotlight per lump: site s drives lump s's conjugate momentum.
    const amrex::Real governor = m_pump.governor;
    const int n_sites =
        (m_pump.num_sites < m_num_fields) ? m_pump.num_sites : m_num_fields;
    for (int s = 0; s < n_sites; ++s)
    {
        const amrex::Real base = RLRuntime::compute_site_base(
            coords.x, coords.y, coords.z, m_pump.sites[s], m_pump.width,
            governor);
        if (base <= 0.0)
        {
            continue;
        }
        const amrex::Real arg =
            m_pump.sites[s].frequency * time + m_pump.sites[s].phase;
        rhs[c_Pi_lump_index(s)] += base * std::cos(arg);
    }
}

#endif /* GRTRESNA_INDEPENDENT_SCALARS_IMPL_HPP_ */
