/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef CHIPHIKTAGGER_HPP_
#define CHIPHIKTAGGER_HPP_

#include "DimensionDefinitions.hpp"
#include "FourthOrderDerivatives.hpp"
#include "Tensor.hpp"

#include <AMReX_Array4.H>
#include <AMReX_Gpu.H>
#include <AMReX_REAL.H>
#include <AMReX_TagBox.H>

/// Solution-following tagger: ChiTagger's criterion dx*|d2 chi| extended with
/// weighted second derivatives of a scalar field and of K, so a steepening
/// front in the matter or in the extrinsic curvature is refined before it
/// outruns the mesh.  Criterion:
///     dx * sqrt(|d2 chi|^2 + w_phi^2 |d2 phi|^2 + w_K^2 |d2 K|^2) >= threshold
/// With both weights 0 this is exactly ChiTagger.  The component indices are
/// constructor arguments so this header does not depend on any example's
/// state-variable enum.
class ChiPhiKTagger
{
  protected:
    amrex::Real m_dx;
    FourthOrderDerivatives m_deriv;
    amrex::Real m_threshold;
    amrex::Real m_w_phi;
    amrex::Real m_w_K;
    int m_c_chi;
    int m_c_phi;
    int m_c_K;

  public:
    // NOLINTNEXTLINE(bugprone-easily-swappable-parameters)
    ChiPhiKTagger(const amrex::Real dx, const amrex::Real a_threshold,
                  const amrex::Real a_w_phi, const amrex::Real a_w_K,
                  const int a_c_chi, const int a_c_phi, const int a_c_K)
        : m_dx(dx), m_deriv(dx), m_threshold(a_threshold), m_w_phi(a_w_phi),
          m_w_K(a_w_K), m_c_chi(a_c_chi), m_c_phi(a_c_phi), m_c_K(a_c_K)
    {
    }

    // NOLINTBEGIN(bugprone-easily-swappable-parameters)
    AMREX_GPU_DEVICE void
    operator()(int i, int j, int k,
               const amrex::Array4<amrex::TagBox::TagType> &tags,
               const amrex::Array4<amrex::Real const> &state) const
    // NOLINTEND(bugprone-easily-swappable-parameters)
    {
        amrex::Real mod2 = 0;
        const auto d2_chi = m_deriv.d2_scalar(i, j, k, state, m_c_chi);
        FOR (idir, jdir)
        {
            mod2 += d2_chi(idir, jdir) * d2_chi(idir, jdir);
        }
        if (m_w_phi != 0.0)
        {
            const auto d2_phi = m_deriv.d2_scalar(i, j, k, state, m_c_phi);
            amrex::Real m     = 0;
            FOR (idir, jdir)
            {
                m += d2_phi(idir, jdir) * d2_phi(idir, jdir);
            }
            mod2 += m_w_phi * m_w_phi * m;
        }
        if (m_w_K != 0.0)
        {
            const auto d2_K = m_deriv.d2_scalar(i, j, k, state, m_c_K);
            amrex::Real m   = 0;
            FOR (idir, jdir)
            {
                m += d2_K(idir, jdir) * d2_K(idir, jdir);
            }
            mod2 += m_w_K * m_w_K * m;
        }
        if (m_dx * std::sqrt(mod2) >= m_threshold)
        {
            tags(i, j, k) = amrex::TagBox::SET;
        }
    }
};

#endif /* CHIPHIKTAGGER_HPP_ */
