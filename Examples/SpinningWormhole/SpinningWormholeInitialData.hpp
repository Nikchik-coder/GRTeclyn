/* SpinningWormholeInitialData
 * t = 0 data for ONE rotating Ellis-Bronnikov wormhole, built from a
 * tabulated stationary background (RotatingBackgroundTable.hpp).
 *
 * Background ansatz (Kleihaus & Kunz 2014, quasi-isotropic coordinates):
 *
 *   ds^2 = -e^f dt^2
 *          + e^{-f} [ e^nu (d eta^2 + h d theta^2)
 *                     + h sin^2(theta) (d varphi - omega dt)^2 ],
 *   h = eta^2 + eta0^2.
 *
 * The static limit (nu = omega = 0, f = 2u) is exactly the massive drainhole
 * of Examples/BinaryWormholeMerger, with eta0 = a.
 *
 * On the isotropic radius r, with  eta = r - eta0^2/(4r)  (so r -> 0 is the
 * compactified far universe, a puncture at the grid centre) and
 * Omega = 1 + eta0^2/(4 r^2):  h = r^2 Omega^2,  d eta = Omega dr, and the
 * spatial metric becomes
 *
 *   gamma = e^{-f} Omega^2 [ e^nu (dr^2 + r^2 dtheta^2)
 *                            + r^2 sin^2(theta) dvarphi^2 ].
 *
 * In Cartesian components, with  a = e^{-f} Omega^2 e^nu  on the (r, theta)
 * block and  b = e^{-f} Omega^2  on the varphi direction
 * (phihat_i = (-Y, X, 0)/rho):
 *
 *   gamma_ij = a delta_ij + (b - a) phihat_i phihat_j .
 *
 * Axis regularity: nu vanishes like sin^2(theta) on the axis, so the table
 * stores nu_bar = nu / sin^2(theta) and the code evaluates
 * (b - a)/rho^2 = -e^{-f} Omega^2 nu_bar S(nu_bar sin^2 theta) / r^2 with
 * S(u) = expm1(u)/u -- finite everywhere including the axis.
 *
 * Fourth function B(eta, theta) (the table's optional 7th column, else 1):
 * gamma_ij -> B^2 gamma_ij, lapse and shift unchanged.  Then
 * det(gamma) -> B^6 det(gamma), chi -> B^-2 chi, h_ij = chi gamma_ij is
 * unchanged, and so are Gamma^i (from h_ij).  K_ij below scales by B^2 through
 * m_i = gamma_ij (d_varphi)^j: d_varphi stays Killing and
 * beta^k d_k B = -omega d_varphi B = 0 (B depends on rho^2 = X^2 + Y^2 and Z
 * only), so L_beta (B^2 gamma) = B^2 L_beta gamma.  A_ij = chi K_ij is
 * therefore unchanged too: B enters through chi alone.
 *
 * 3+1 split of the stationary metric:
 *   alpha  = e^{f/2},
 *   beta^varphi = -omega   =>  beta^i = omega (Y, -X, 0),
 *   K_ij  = (D_i beta_j + D_j beta_i) / (2 alpha)
 *         = -(w_i m_j + w_j m_i) / (2 alpha),
 *     with  w_i = d_i omega  and  m_i = gamma_ij (d_varphi)^j = b (-Y, X, 0)
 *     (the Killing part of L_beta gamma vanishes).  Its trace is zero, so
 *     K = 0 and  A_ij = chi K_ij  directly.
 *   Gamma^i is NOT written here: the metric is not conformally flat, so
 *   InitialGammas.hpp computes it from h_ij by finite differences right after
 *   this fill (the analytic route would need second derivatives of the
 *   table).
 *
 * Scalar: phi from the table (outer asymptote subtracted by the generator);
 * the stationary field is axisymmetric, so Pi = -(dt phi - beta^i d_i phi) /
 * alpha = 0.  An optional ell = 0 Gaussian shell in Pi,
 * A exp(-(eta - eta_c)^2 / w^2), seeds the radial modes; it violates the
 * constraints at O(A).
 *
 * The kick (after the stability study of Evstafyeva, Siemonsen & East,
 * arXiv:2508.11527): a Gaussian shell in the conformal factor on the throat,
 *
 *   gamma_ij -> psi_k^4 gamma_ij,
 *   psi_k = 1 + eps exp(-((eta - eta_c)/w)^2) S(theta, varphi),
 *
 * with S = 1 (l = 0: the throat's areal radius moves by ~2 eps with the sign
 * of eps, the radial branch), P2(cos theta) (l = 2, m = 0), or
 * sin^m(theta) cos(m varphi) = Re[(X + iY)^m] / r^m (l = m >= 1: m = 1 pushes
 * the throat off centre, m = 2 is the bar, which the unkicked background
 * seeds only at round-off).  K_ij goes with it as psi_k^-2 K_ij
 * (A_ij -> psi_k^-6 A_ij), York's conformal scaling of a traceless K: with
 * K = 0 and Pi = 0 the momentum constraint stays exact for any psi_k, and
 * only the Hamiltonian constraint is violated, at O(eps); it is not solved
 * away.  h_ij, the lapse and the shift keep their background values (lapse
 * types 1-3 read the kicked chi).
 */

#ifndef SPINNINGWORMHOLEINITIALDATA_HPP_
#define SPINNINGWORMHOLEINITIALDATA_HPP_

#include "RotatingBackgroundTable.hpp"
#include "StateVariables.hpp"

#include <AMReX_Array4.H>
#include <AMReX_REAL.H>

#include <array>
#include <cmath>

class SpinningWormholeInitialData
{
  public:
    struct params_t
    {
        std::array<double, AMREX_SPACEDIM> grid_center{};

        //! 0 = the background lapse e^{f/2} (default: the stationary slicing);
        //! 1 = sqrt(chi); 2 = 1 - 3 ln(chi); 3 = chi (precollapsed variants
        //! for runs that relax the gauge from the start).
        int initial_lapse_type{0};

        //! ell = 0 Pi shell: amplitude (either sign), Gaussian width in eta,
        //! and centre eta_c (0 = on the throat).
        double seed_amplitude{0.0};
        double seed_width{1.0};
        double seed_radius{0.0};

        //! The kick (psi_k above): signed amplitude eps, angular profile
        //! (l, m) = (0, 0), (2, 0) or (m, m), shell centre eta_c and width
        //! in eta (<= 0: eta0 / 4).
        double kick_amplitude{0.0};
        int kick_l{0};
        int kick_m{0};
        double kick_radius{0.0};
        double kick_width{0.0};
    };

    SpinningWormholeInitialData(const params_t &a_params,
                                const RotatingBackgroundTable::View &a_table,
                                double a_dx)
        : m_params(a_params), m_table(a_table), m_dx(a_dx)
    {
    }

    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
    compute(int i, int j, int k, amrex::Array4<amrex::Real> cell) const
    {
        // Cell centre relative to the wormhole centre (assumes prob_lo = 0).
        const double X = (i + 0.5) * m_dx - m_params.grid_center[0];
        const double Y = (j + 0.5) * m_dx - m_params.grid_center[1];
        const double Z = (k + 0.5) * m_dx - m_params.grid_center[2];

        const double rho2 = X * X + Y * Y;
        const double r2   = amrex::max(rho2 + Z * Z, 1.0e-24);
        const double r    = std::sqrt(r2);
        const double mu   = Z / r; // cos(theta), signed
        const double s2   = amrex::max(1.0 - mu * mu, 0.0); // sin^2(theta)

        const double eta0 = m_table.eta0;
        const double eta  = r - eta0 * eta0 / (4.0 * r);
        const double Om   = 1.0 + eta0 * eta0 / (4.0 * r2);
        const double xc   = (2.0 / M_PI) * std::atan(eta / eta0);

        RotatingBackgroundTable::Sample bg;
        m_table.sample(xc, mu, bg);

        const double emf = std::exp(-bg.f); // e^{-f}
        const double nu  = bg.nu_bar * s2;

        // The kick's conformal factor; exactly 1 when the kick is off.
        double psi_k = 1.0;
        if (m_params.kick_amplitude != 0.0)
        {
            const double w = (m_params.kick_width > 0.0) ? m_params.kick_width
                                                         : 0.25 * eta0;
            const double d = (eta - m_params.kick_radius) / w;
            psi_k += m_params.kick_amplitude * kick_profile(X, Y, mu, r) *
                     std::exp(-d * d);
        }
        const double psi_k4 = psi_k * psi_k * psi_k * psi_k;

        // gamma_ij = a delta_ij + c (phihat phihat rho^2)_ij
        const double a_coef = emf * Om * Om * std::exp(nu);
        const double b_coef = emf * Om * Om;
        // c = (b - a)/rho^2, regular on the axis via S(u) = expm1(u)/u.
        const double u_arg = bg.nu_bar * s2;
        const double S_u   = (std::abs(u_arg) > 1.0e-8)
                                 ? std::expm1(u_arg) / u_arg
                                 : 1.0 + 0.5 * u_arg;
        const double c_coef = -b_coef * bg.nu_bar * S_u / r2;

        const double g_xx = a_coef + c_coef * Y * Y;
        const double g_yy = a_coef + c_coef * X * X;
        const double g_xy = -c_coef * X * Y;
        const double g_zz = a_coef;

        // det(gamma) = a^2 b exactly (the phihat projector structure), at
        // B = 1: chi, h_ij and A_ij below are the B = 1 ones (see the top).
        const double det_gamma = a_coef * a_coef * b_coef;
        const double chi       = amrex::max(std::pow(det_gamma, -1.0 / 3.0),
                                            1.0e-10);
        // The kick (psi_k^4) and B (B^2) scale the physical metric: chi by
        // psi_k^-4 B^-2, h_ij unchanged.  At B = 1 this divides by psi_k4
        // exactly.
        const double B2    = bg.B * bg.B;
        const double chi_k = amrex::max(chi / (B2 * psi_k4), 1.0e-10);

        cell(i, j, k, c_chi) = static_cast<amrex::Real>(chi_k);
        cell(i, j, k, c_h11) = static_cast<amrex::Real>(chi * g_xx);
        cell(i, j, k, c_h12) = static_cast<amrex::Real>(chi * g_xy);
        cell(i, j, k, c_h13) = 0.0;
        cell(i, j, k, c_h22) = static_cast<amrex::Real>(chi * g_yy);
        cell(i, j, k, c_h23) = 0.0;
        cell(i, j, k, c_h33) = static_cast<amrex::Real>(chi * g_zz);

        // Extrinsic curvature of the stationary slice.
        // w_i = d_i omega = Omega omega_eta n_i + (omega_theta / r) thetahat_i,
        // written with the axis-regular combination
        // sin(theta) thetahat = (Z X, Z Y, -rho^2)/r^2.
        const double alpha = std::exp(0.5 * bg.f);
        const double we    = Om * bg.domega_deta;
        const double wt    = bg.domega_dtheta_over_sintheta;
        const double w1    = we * X / r + wt * Z * X / (r * r2);
        const double w2    = we * Y / r + wt * Z * Y / (r * r2);
        const double w3    = we * Z / r - wt * rho2 / (r * r2);
        // m_i = b (-Y, X, 0)
        const double m1 = -b_coef * Y;
        const double m2 = b_coef * X;

        // A_ij = chi_k K_ij with the kicked K_ij = psi_k^-2 K_ij: psi_k^-6
        // (B^-2 from chi_k and B^2 from K_ij cancel).
        const double pre = -chi / (2.0 * alpha * psi_k4 * psi_k * psi_k);
        cell(i, j, k, c_K)   = 0.0;
        cell(i, j, k, c_A11) = static_cast<amrex::Real>(pre * 2.0 * w1 * m1);
        cell(i, j, k, c_A12) =
            static_cast<amrex::Real>(pre * (w1 * m2 + w2 * m1));
        cell(i, j, k, c_A13) = static_cast<amrex::Real>(pre * w3 * m1);
        cell(i, j, k, c_A22) = static_cast<amrex::Real>(pre * 2.0 * w2 * m2);
        cell(i, j, k, c_A23) = static_cast<amrex::Real>(pre * w3 * m2);
        cell(i, j, k, c_A33) = 0.0;

        cell(i, j, k, c_Theta) = 0.0;
        // Gamma^i stays 0 here; InitialGammas fills it from h_ij.

        double lapse = alpha;
        if (m_params.initial_lapse_type == 1)
        {
            lapse = std::sqrt(chi_k);
        }
        else if (m_params.initial_lapse_type == 2)
        {
            lapse = 1.0 - 3.0 * std::log(chi_k);
        }
        else if (m_params.initial_lapse_type == 3)
        {
            lapse = chi_k;
        }
        cell(i, j, k, c_lapse) =
            amrex::max(static_cast<amrex::Real>(lapse), amrex::Real(1.0e-10));

        // beta^varphi = -omega  =>  beta^i = omega (Y, -X, 0); regular at the
        // puncture, where the frame rotates at omega(-infinity).
        cell(i, j, k, c_shift1) = static_cast<amrex::Real>(bg.omega * Y);
        cell(i, j, k, c_shift2) = static_cast<amrex::Real>(-bg.omega * X);
        cell(i, j, k, c_shift3) = 0.0;
        cell(i, j, k, c_B1)     = 0.0;
        cell(i, j, k, c_B2)     = 0.0;
        cell(i, j, k, c_B3)     = 0.0;

        cell(i, j, k, c_phi) = static_cast<amrex::Real>(bg.phi);

        double Pi = 0.0;
        if (m_params.seed_amplitude != 0.0)
        {
            const double d = (eta - m_params.seed_radius) / m_params.seed_width;
            Pi = m_params.seed_amplitude * std::exp(-d * d);
        }
        cell(i, j, k, c_Pi) = static_cast<amrex::Real>(Pi);
    }

    //! The kick's angular profile S: 1 (l = 0), P2(cos theta) (l = 2, m = 0),
    //! or sin^m(theta) cos(m varphi) = Re[(X + iY)^m] / r^m (l = m >= 1),
    //! regular on the axis.
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE double
    kick_profile(double X, double Y, double mu, double r) const
    {
        if (m_params.kick_m == 0)
        {
            return (m_params.kick_l == 2) ? 1.5 * mu * mu - 0.5 : 1.0;
        }
        const double xh = X / r;
        const double yh = Y / r;
        double re       = 1.0;
        double im       = 0.0;
        for (int n = 0; n < m_params.kick_m; ++n)
        {
            const double t = re * xh - im * yh;
            im             = re * yh + im * xh;
            re             = t;
        }
        return re;
    }

  protected:
    params_t m_params;
    RotatingBackgroundTable::View m_table;
    double m_dx;
};

#endif /* SPINNINGWORMHOLEINITIALDATA_HPP_ */
