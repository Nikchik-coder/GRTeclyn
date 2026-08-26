/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#if !defined(COMPLEXEXOTICSCALARFIELD_HPP_)
#error "This file should only be included through ComplexExoticScalarField.hpp"
#endif

#ifndef COMPLEXEXOTICSCALARFIELD_IMPL_HPP_
#define COMPLEXEXOTICSCALARFIELD_IMPL_HPP_

template <class potential_t>
template <class deriv_t>
AMREX_GPU_DEVICE emtensor_t
ComplexExoticScalarField<potential_t>::compute_emtensor(
    const int ix, const int iy, const int iz,
    const amrex::Array4<const amrex::Real> &state, const deriv_t &a_deriv,
    const Tensor::Rank2 &h_UU) const
{
    const amrex::CellData<const amrex::Real> &state_cell_data =
        state.cellData(ix, iy, iz);
    const Vars vars(state_cell_data);

    const Tensor::Rank1 d1_phi1 = a_deriv.d1_scalar(ix, iy, iz, state, c_phi);
    const Tensor::Rank1 d1_phi2 = a_deriv.d1_scalar(ix, iy, iz, state, c_phi2);

    const double support_strength = m_support_strength;
    emtensor_t out;

    // Useful quantity Vt per component
    const amrex::Real Vt1 =
        ScalarFieldKernels::kinetic_invariant(vars, h_UU, vars.Pi1(), d1_phi1);
    const amrex::Real Vt2 =
        ScalarFieldKernels::kinetic_invariant(vars, h_UU, vars.Pi2(), d1_phi2);
    const amrex::Real Vt = Vt1 + Vt2;

    // Potential, evaluated on the full complex modulus (coupled).  This is
    // exact for a self-interacting potential V(|Phi|^2) = V(phi1^2 + phi2^2);
    // a per-component evaluation would break the U(1) symmetry (and destroy the
    // conserved Noether charge) for the quartic/sextic Q-ball terms.
    amrex::Real V_of_phi = 0.0, dV1 = 0.0, dV2 = 0.0;
    m_potential.compute_potential(V_of_phi, dV1, dV2, vars.phi1(), vars.phi2());

    // S = T_ij (sum of both components, phantom-flipped)
    FOR (i, j)
    {
        out.S(i, j) =
            -support_strength *
            (-0.5 * vars.h(i, j) * Vt / vars.chi() +
             d1_phi1(i) * d1_phi1(j) + d1_phi2(i) * d1_phi2(j) -
             vars.h(i, j) * V_of_phi / vars.chi());
    }

    // rho = n^a n^b T_ab
    out.rho = -support_strength * (vars.Pi1() * vars.Pi1() +
                                   vars.Pi2() * vars.Pi2() + 0.5 * Vt +
                                   V_of_phi);

    // trS: out.S already carries the potential term (scaled by
    // support_strength), so its trace supplies it; adding it again double-counts.
    out.trS = vars.chi() * TensorAlgebra::compute_trace(out.S, h_UU);

    // j_i (lower index) = - n^a T_ai
    FOR (i)
    {
        out.j(i) = -support_strength *
                   (-(d1_phi1(i) * vars.Pi1() + d1_phi2(i) * vars.Pi2()));
    }

    return out;
}

template <class potential_t>
template <class deriv_t>
AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
ComplexExoticScalarField<potential_t>::add_matter_rhs(
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

    amrex::Real V_of_phi = 0.0, dV1 = 0.0, dV2 = 0.0;
    m_potential.compute_potential(V_of_phi, dV1, dV2, vars.phi1(), vars.phi2());

    // Component 1: Phi real part
    rhs[c_phi] = vars.lapse() * vars.Pi1() + advec_phi1;
    rhs[c_Pi]  = vars.lapse() * (vars.K() * vars.Pi1() - dV1) + advec_Pi1 +
                ScalarFieldKernels::Pi_gradient_terms(
                    vars, h_UU, chris, d1_chi, d1_lapse, d1_phi1, d2_phi1);

    // Component 2: Phi imaginary part
    rhs[c_phi2] = vars.lapse() * vars.Pi2() + advec_phi2;
    rhs[c_Pi2]  = vars.lapse() * (vars.K() * vars.Pi2() - dV2) + advec_Pi2 +
                 ScalarFieldKernels::Pi_gradient_terms(
                     vars, h_UU, chris, d1_chi, d1_lapse, d1_phi2, d2_phi2);
}

template <class potential_t>
template <class deriv_t>
AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
ComplexExoticScalarField<potential_t>::add_matter_rhs(
    const int ix, const int iy, const int iz,
    const amrex::Array4<amrex::Real> &rhs_state,
    const amrex::Array4<const amrex::Real> &state, const deriv_t &a_deriv,
    const Coordinates &coords, const amrex::Real time) const
{
    // Phantom-sign caveat: the exotic class flips the *stress tensor* sign
    // (compute_emtensor), NOT the field EOM sign.  The pump drives the field
    // EOM (Pi/Pi2), so the source term is identical to ComplexScalarField --
    // do NOT add an extra sign flip here.
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

#endif /* COMPLEXEXOTICSCALARFIELD_IMPL_HPP_ */
