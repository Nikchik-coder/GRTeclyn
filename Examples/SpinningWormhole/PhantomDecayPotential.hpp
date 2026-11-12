/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef PHANTOMDECAYPOTENTIAL_HPP_
#define PHANTOMDECAYPOTENTIAL_HPP_

#include "ScalarFieldVars.hpp"
#include "Tensor.hpp"
#include "simd.hpp"

#include <AMReX_Array.H>
#include <AMReX_BLassert.H>

#include <vector>

//! V(phi) = 1/2 m^2 phi^2 + sum_{k < n} a_k phi^k, with the a_k from the
//! .spinbg header's potential_coeffs (n = 0: the mass term alone, computed
//! exactly as before the polynomial existed).
class PhantomDecayPotential
{
  public:
    static constexpr int max_num_coeffs = 12;

  protected:
    double m_mass_sq;
    int m_num_coeffs{0};
    amrex::GpuArray<double, max_num_coeffs> m_coeffs{};

  public:
    PhantomDecayPotential(double mass                     = 0.0,
                          const std::vector<double> &coeffs = {})
        : m_mass_sq(mass * mass)
    {
        AMREX_ALWAYS_ASSERT_WITH_MESSAGE(
            coeffs.size() <= static_cast<std::size_t>(max_num_coeffs),
            "PhantomDecayPotential: more than 12 polynomial coefficients");
        m_num_coeffs = static_cast<int>(coeffs.size());
        for (int k = 0; k < m_num_coeffs; ++k)
        {
            m_coeffs[k] = coeffs[k];
        }
    }

    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
    // NOLINTNEXTLINE(bugprone-easily-swappable-parameters)
    compute_potential(amrex::Real &V_of_phi, amrex::Real &dVdphi,
                      const ScalarFieldVars &vars) const
    {
        const amrex::Real phi = vars.phi();

        V_of_phi = 0.5 * m_mass_sq * phi * phi;
        dVdphi   = m_mass_sq * phi;

        if (m_num_coeffs > 0)
        {
            // Horner for the value and the derivative together.
            amrex::Real p  = m_coeffs[m_num_coeffs - 1];
            amrex::Real dp = 0.0;
            for (int k = m_num_coeffs - 2; k >= 0; --k)
            {
                dp = dp * phi + p;
                p  = p * phi + m_coeffs[k];
            }
            V_of_phi += p;
            dVdphi += dp;
        }
    }
};

#endif /* PHANTOMDECAYPOTENTIAL_HPP_ */
