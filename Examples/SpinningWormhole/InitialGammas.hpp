/* InitialGammas
 * Fills Gamma^i = h^{jk} Gamma^i_{jk} from the conformal metric by
 * fourth-order finite differences.
 *
 * The rotating background's spatial metric is not conformally flat, so
 * Gamma^i is nonzero at t = 0 and must be consistent with h_ij or the CCZ4
 * Gamma-constraint starts violated (SpinningWormholeInitialData leaves the
 * slots at 0 on purpose: analytic Gammas would need second derivatives of
 * the tabulated background, while this matches the evolution's own stencil).
 *
 * Source/CCZ4/GammaCalculator.hpp does the same job through the unported
 * Cell/BoxLoops API; this is its Array4 twin in the style the fork's
 * examples actually compile.
 *
 * Usage: run over VALID cells only, after the initial data has filled the
 * ghost cells too (the +-2 stencil then never reads garbage).  Reads only
 * c_h11..c_h33 and writes only c_Gamma1..3, so an in-place pass over one
 * MultiFab is safe.
 */

#ifndef INITIALGAMMAS_HPP_
#define INITIALGAMMAS_HPP_

#include "StateVariables.hpp"

#include <AMReX_Array4.H>
#include <AMReX_REAL.H>

class InitialGammas
{
  public:
    explicit InitialGammas(double a_dx) : m_one_over_12dx(1.0 / (12.0 * a_dx))
    {
    }

    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
    compute(int i, int j, int k, amrex::Array4<amrex::Real> cell) const
    {
        // h_ij at the point, as a full 3x3 for index arithmetic.
        double h[3][3];
        load_sym(cell, i, j, k, h);

        // d1[l][a][b] = partial_l h_ab, fourth-order central.
        double d1[3][3][3];
        for (int l = 0; l < 3; ++l)
        {
            const int di = (l == 0) ? 1 : 0;
            const int dj = (l == 1) ? 1 : 0;
            const int dk = (l == 2) ? 1 : 0;
            double hp1[3][3], hp2[3][3], hm1[3][3], hm2[3][3];
            load_sym(cell, i + di, j + dj, k + dk, hp1);
            load_sym(cell, i + 2 * di, j + 2 * dj, k + 2 * dk, hp2);
            load_sym(cell, i - di, j - dj, k - dk, hm1);
            load_sym(cell, i - 2 * di, j - 2 * dj, k - 2 * dk, hm2);
            for (int a = 0; a < 3; ++a)
            {
                for (int b = 0; b < 3; ++b)
                {
                    d1[l][a][b] = (-hp2[a][b] + 8.0 * hp1[a][b] -
                                   8.0 * hm1[a][b] + hm2[a][b]) *
                                  m_one_over_12dx;
                }
            }
        }

        // Inverse of the symmetric h (det h = 1 up to floating point; use the
        // computed determinant anyway).
        const double det = h[0][0] * (h[1][1] * h[2][2] - h[1][2] * h[1][2]) -
                           h[0][1] * (h[0][1] * h[2][2] - h[1][2] * h[0][2]) +
                           h[0][2] * (h[0][1] * h[1][2] - h[1][1] * h[0][2]);
        const double inv_det = 1.0 / det;
        double hUU[3][3];
        hUU[0][0] = (h[1][1] * h[2][2] - h[1][2] * h[1][2]) * inv_det;
        hUU[0][1] = (h[0][2] * h[1][2] - h[0][1] * h[2][2]) * inv_det;
        hUU[0][2] = (h[0][1] * h[1][2] - h[0][2] * h[1][1]) * inv_det;
        hUU[1][1] = (h[0][0] * h[2][2] - h[0][2] * h[0][2]) * inv_det;
        hUU[1][2] = (h[0][1] * h[0][2] - h[0][0] * h[1][2]) * inv_det;
        hUU[2][2] = (h[0][0] * h[1][1] - h[0][1] * h[0][1]) * inv_det;
        hUU[1][0] = hUU[0][1];
        hUU[2][0] = hUU[0][2];
        hUU[2][1] = hUU[1][2];

        // Gamma^i = h^{jk} Gamma^i_{jk},
        // Gamma^i_{jk} = 1/2 h^{il} (d_j h_{lk} + d_k h_{lj} - d_l h_{jk}).
        double Gamma[3] = {0.0, 0.0, 0.0};
        for (int a = 0; a < 3; ++a)
        {
            for (int l = 0; l < 3; ++l)
            {
                for (int b = 0; b < 3; ++b)
                {
                    for (int c = 0; c < 3; ++c)
                    {
                        Gamma[a] += 0.5 * hUU[a][l] * hUU[b][c] *
                                    (d1[b][l][c] + d1[c][l][b] - d1[l][b][c]);
                    }
                }
            }
        }

        cell(i, j, k, c_Gamma1) = static_cast<amrex::Real>(Gamma[0]);
        cell(i, j, k, c_Gamma2) = static_cast<amrex::Real>(Gamma[1]);
        cell(i, j, k, c_Gamma3) = static_cast<amrex::Real>(Gamma[2]);
    }

  private:
    double m_one_over_12dx;

    AMREX_GPU_DEVICE AMREX_FORCE_INLINE static void
    load_sym(const amrex::Array4<amrex::Real> &cell, int i, int j, int k,
             double h[3][3])
    {
        h[0][0] = cell(i, j, k, c_h11);
        h[0][1] = cell(i, j, k, c_h12);
        h[0][2] = cell(i, j, k, c_h13);
        h[1][1] = cell(i, j, k, c_h22);
        h[1][2] = cell(i, j, k, c_h23);
        h[2][2] = cell(i, j, k, c_h33);
        h[1][0] = h[0][1];
        h[2][0] = h[0][2];
        h[2][1] = h[1][2];
    }
};

#endif /* INITIALGAMMAS_HPP_ */
