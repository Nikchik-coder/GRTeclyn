#if !defined(BICOMPLEXSCALARFIELD_HPP_)
#error "This file should only be included through BiComplexScalarField.hpp"
#endif

#ifndef BICOMPLEXSCALARFIELD_IMPL_HPP_
#define BICOMPLEXSCALARFIELD_IMPL_HPP_

namespace
{
//! Accumulate one complex field's (signed) stress-energy into out.  Mirrors
//! the single-field ComplexScalarField math; ``fs`` is the field's
//! gravitational sign (+1 canonical, -1 phantom).
AMREX_GPU_DEVICE AMREX_FORCE_INLINE void accumulate_complex_field(
    emtensor_t &out, amrex::Real fs, amrex::Real Pi1, amrex::Real Pi2,
    const Tensor::Rank1 &d1phi1, const Tensor::Rank1 &d1phi2,
    amrex::Real V_of_phi, amrex::Real chi, const BiComplexScalarFieldVars &vars,
    const Tensor::Rank2 &h_UU)
{
    for (int comp = 0; comp < 2; ++comp)
    {
        const amrex::Real Pi_k       = (comp == 0) ? Pi1 : Pi2;
        const Tensor::Rank1 &dphi    = (comp == 0) ? d1phi1 : d1phi2;

        amrex::Real Vt_k = -Pi_k * Pi_k;
        FOR (i, j)
        {
            Vt_k += chi * h_UU(i, j) * dphi(i) * dphi(j);
        }

        out.rho += fs * (Pi_k * Pi_k + 0.5 * Vt_k);
        FOR (i)
        {
            out.j(i) += fs * (-Pi_k * dphi(i));
        }
        FOR (i, j)
        {
            out.S(i, j) += fs * (-0.5 * vars.h(i, j) * Vt_k / chi +
                                 dphi(i) * dphi(j));
        }
    }

    out.rho += fs * V_of_phi;
    FOR (i, j)
    {
        out.S(i, j) -= fs * vars.h(i, j) * V_of_phi / chi;
    }
}
} // namespace

template <class deriv_t>
AMREX_GPU_DEVICE AMREX_FORCE_INLINE emtensor_t
BiComplexScalarField::compute_emtensor(
    const int ix, const int iy, const int iz,
    const amrex::Array4<const amrex::Real> &state, const deriv_t &a_deriv,
    const Tensor::Rank2 &h_UU) const
{
    const amrex::CellData<const amrex::Real> &state_cell_data =
        state.cellData(ix, iy, iz);
    const Vars vars(state_cell_data);

    const Tensor::Rank1 d1_phi1p = a_deriv.d1_scalar(ix, iy, iz, state, c_phi);
    const Tensor::Rank1 d1_phi2p = a_deriv.d1_scalar(ix, iy, iz, state, c_phi2);
    const Tensor::Rank1 d1_phi1m =
        a_deriv.d1_scalar(ix, iy, iz, state, c_phi_m);
    const Tensor::Rank1 d1_phi2m =
        a_deriv.d1_scalar(ix, iy, iz, state, c_phi2_m);

    emtensor_t out;
    ScalarFieldKernels::zero(out);

    // Canonical (Phi+) field, gravitational sign +1.
    amrex::Real Vp = 0.0, dVp1 = 0.0, dVp2 = 0.0;
    m_potential.compute_potential(Vp, dVp1, dVp2, vars.phi1p(), vars.phi2p());
    accumulate_complex_field(out, +1.0, vars.Pi1p(), vars.Pi2p(), d1_phi1p,
                             d1_phi2p, Vp, vars.chi(), vars, h_UU);

    // Phantom (Phi-) field, gravitational sign -1.
    amrex::Real Vm = 0.0, dVm1 = 0.0, dVm2 = 0.0;
    m_potential.compute_potential(Vm, dVm1, dVm2, vars.phi1m(), vars.phi2m());
    accumulate_complex_field(out, -1.0, vars.Pi1m(), vars.Pi2m(), d1_phi1m,
                             d1_phi2m, Vm, vars.chi(), vars, h_UU);

    // out.S already carries the -gamma_ij V term for both fields, so its trace
    // supplies the -3V; adding that again double-counts the potential.
    out.trS = vars.chi() * TensorAlgebra::compute_trace(out.S, h_UU);
    return out;
}

template <class deriv_t>
AMREX_GPU_DEVICE AMREX_FORCE_INLINE void BiComplexScalarField::add_matter_rhs(
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

    // Potential derivatives for each field (the field EOM is sign-independent;
    // only the gravitational coupling is reversed, so both fields obey the same
    // Klein-Gordon RHS while preserving their own U(1) charge).
    amrex::Real Vp = 0.0, dVp1 = 0.0, dVp2 = 0.0;
    m_potential.compute_potential(Vp, dVp1, dVp2, vars.phi1p(), vars.phi2p());
    amrex::Real Vm = 0.0, dVm1 = 0.0, dVm2 = 0.0;
    m_potential.compute_potential(Vm, dVm1, dVm2, vars.phi1m(), vars.phi2m());

    // One Klein-Gordon component: (c_phi_x, c_Pi_x) with potential slope dV.
    auto evolve_component = [&](const int c_phi_x, const int c_Pi_x,
                                const amrex::Real phi_dot_Pi,
                                const amrex::Real dV)
    {
        const Tensor::Rank1 d1_phi =
            a_deriv.d1_scalar(ix, iy, iz, state, c_phi_x);
        const Tensor::Sym12Rank2 d2_phi =
            a_deriv.d2_scalar(ix, iy, iz, state, c_phi_x);
        const amrex::Real advec_phi =
            a_deriv.advec_scalar(ix, iy, iz, state, shift_vector, c_phi_x);
        const amrex::Real advec_Pi =
            a_deriv.advec_scalar(ix, iy, iz, state, shift_vector, c_Pi_x);

        rhs[c_phi_x] = vars.lapse() * phi_dot_Pi + advec_phi;
        rhs[c_Pi_x]  = vars.lapse() * (vars.K() * phi_dot_Pi - dV) + advec_Pi +
                      ScalarFieldKernels::Pi_gradient_terms(
                          vars, h_UU, chris, d1_chi, d1_lapse, d1_phi, d2_phi);
    };

    // Canonical field Phi+.
    evolve_component(c_phi, c_Pi, vars.Pi1p(), dVp1);
    evolve_component(c_phi2, c_Pi2, vars.Pi2p(), dVp2);

    // Phantom field Phi-.
    evolve_component(c_phi_m, c_Pi_m, vars.Pi1m(), dVm1);
    evolve_component(c_phi2_m, c_Pi2_m, vars.Pi2m(), dVm2);
}

template <class deriv_t>
AMREX_GPU_DEVICE AMREX_FORCE_INLINE void BiComplexScalarField::add_matter_rhs(
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

    // PD / open-loop sources from the single shared implementation.
    const RLPumpSources src = RLPumpForce::compute_bicomplex_sources(
        m_pump, coords.x, coords.y, coords.z, time, vars.lapse(), vars.phi1p(),
        vars.phi2p(), vars.Pi1p(), vars.Pi2p(), vars.phi1m(), vars.phi2m(),
        vars.Pi1m(), vars.Pi2m());
    rhs[c_Pi] += src.s1p;
    rhs[c_Pi2] += src.s2p;
    rhs[c_Pi_m] += src.s1m;
    rhs[c_Pi2_m] += src.s2m;
}

#endif /* BICOMPLEXSCALARFIELD_IMPL_HPP_ */
