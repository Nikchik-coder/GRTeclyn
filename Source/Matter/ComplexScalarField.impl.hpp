#if !defined(COMPLEXSCALARFIELD_HPP_)
#error "This file should only be included through ComplexScalarField.hpp"
#endif

#ifndef COMPLEXSCALARFIELD_IMPL_HPP_
#define COMPLEXSCALARFIELD_IMPL_HPP_

template <class deriv_t>
AMREX_GPU_DEVICE AMREX_FORCE_INLINE emtensor_t
ComplexScalarField::compute_emtensor(
    const int ix, const int iy, const int iz,
    const amrex::Array4<const amrex::Real> &state, const deriv_t &a_deriv,
    const Tensor::Rank2 &h_UU) const
{
    const amrex::CellData<const amrex::Real> &state_cell_data =
        state.cellData(ix, iy, iz);
    const Vars vars(state_cell_data);

    const Tensor::Rank1 d1_phi1 = a_deriv.d1_scalar(ix, iy, iz, state, c_phi);
    const Tensor::Rank1 d1_phi2 = a_deriv.d1_scalar(ix, iy, iz, state, c_phi2);

    const amrex::Real sign = m_sign;
    emtensor_t out;
    ScalarFieldKernels::zero(out);

    amrex::Real V_of_phi = 0.0;
    amrex::Real dVdphi1  = 0.0;
    amrex::Real dVdphi2  = 0.0;
    m_potential.compute_potential(V_of_phi, dVdphi1, dVdphi2, vars.phi1(),
                                  vars.phi2());

    for (int comp = 0; comp < 2; ++comp)
    {
        const amrex::Real Pi_k       = (comp == 0) ? vars.Pi1() : vars.Pi2();
        const Tensor::Rank1 &d1_phi  = (comp == 0) ? d1_phi1 : d1_phi2;

        const amrex::Real Vt_k =
            ScalarFieldKernels::kinetic_invariant(vars, h_UU, Pi_k, d1_phi);

        out.rho += Pi_k * Pi_k + 0.5 * Vt_k;
        FOR (i)
        {
            out.j(i) += -Pi_k * d1_phi(i);
        }
        FOR (i, j)
        {
            out.S(i, j) += -0.5 * vars.h(i, j) * Vt_k / vars.chi() +
                           d1_phi(i) * d1_phi(j);
        }
    }

    out.rho += V_of_phi;
    FOR (i, j)
    {
        out.S(i, j) -= vars.h(i, j) * V_of_phi / vars.chi();
    }

    // Phantom sign: flip entire T_ab for sign == -1. The field EOM (RHS) is
    // unchanged -- only the gravitational coupling is reversed, giving
    // negative energy density while preserving U(1) charge conservation.
    out.rho *= sign;
    FOR (i)
    {
        out.j(i) *= sign;
    }
    FOR (i, j)
    {
        out.S(i, j) *= sign;
    }
    // out.S already carries the sign-flipped -gamma_ij V term, so its trace
    // supplies the -3V; adding that again double-counts the potential.
    out.trS = vars.chi() * TensorAlgebra::compute_trace(out.S, h_UU);

    return out;
}

template <class deriv_t>
AMREX_GPU_DEVICE AMREX_FORCE_INLINE void ComplexScalarField::add_matter_rhs(
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
    const Tensor::Rank1 d1_phi1  = a_deriv.d1_scalar(ix, iy, iz, state, c_phi);
    const Tensor::Rank1 d1_phi2  = a_deriv.d1_scalar(ix, iy, iz, state, c_phi2);
    const Tensor::Sym12Rank2 d2_phi1 =
        a_deriv.d2_scalar(ix, iy, iz, state, c_phi);
    const Tensor::Sym12Rank2 d2_phi2 =
        a_deriv.d2_scalar(ix, iy, iz, state, c_phi2);

    const Tensor::Rank1 shift_vector{vars.shift(0), vars.shift(1),
                                     vars.shift(2)};
    const amrex::Real advec_phi1 =
        a_deriv.advec_scalar(ix, iy, iz, state, shift_vector, c_phi);
    const amrex::Real advec_Pi1 =
        a_deriv.advec_scalar(ix, iy, iz, state, shift_vector, c_Pi);
    const amrex::Real advec_phi2 =
        a_deriv.advec_scalar(ix, iy, iz, state, shift_vector, c_phi2);
    const amrex::Real advec_Pi2 =
        a_deriv.advec_scalar(ix, iy, iz, state, shift_vector, c_Pi2);

    amrex::Real V_of_phi = 0.0;
    amrex::Real dVdphi1  = 0.0;
    amrex::Real dVdphi2  = 0.0;
    m_potential.compute_potential(V_of_phi, dVdphi1, dVdphi2, vars.phi1(),
                                  vars.phi2());

    rhs[c_phi]  = vars.lapse() * vars.Pi1() + advec_phi1;
    rhs[c_Pi]   = vars.lapse() * (vars.K() * vars.Pi1() - dVdphi1) + advec_Pi1 +
                ScalarFieldKernels::Pi_gradient_terms(
                    vars, h_UU, chris, d1_chi, d1_lapse, d1_phi1, d2_phi1);
    rhs[c_phi2] = vars.lapse() * vars.Pi2() + advec_phi2;
    rhs[c_Pi2]  = vars.lapse() * (vars.K() * vars.Pi2() - dVdphi2) + advec_Pi2 +
                 ScalarFieldKernels::Pi_gradient_terms(
                     vars, h_UU, chris, d1_chi, d1_lapse, d1_phi2, d2_phi2);
}

template <class deriv_t>
AMREX_GPU_DEVICE AMREX_FORCE_INLINE void ComplexScalarField::add_matter_rhs(
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
    const Vars vars(state.cellData(ix, iy, iz));

    const RLPumpSources src = RLPumpForce::compute_single_field_sources(
        m_pump, coords.x, coords.y, coords.z, time, vars.lapse(), vars.phi1(),
        vars.phi2(), vars.Pi1(), vars.Pi2());
    rhs[c_Pi] += src.s1p;
    rhs[c_Pi2] += src.s2p;
}

#endif /* COMPLEXSCALARFIELD_IMPL_HPP_ */
