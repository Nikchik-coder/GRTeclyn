/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef BINARYWORMHOLEINITIALDATA_HPP_
#define BINARYWORMHOLEINITIALDATA_HPP_

#include "CCZ4StateVariables.hpp"
#include "Coordinates.hpp"
#include "Tensor.hpp"
#include "VarsTools.hpp"
#include "simd.hpp"

#include <cmath>

//! Analytic initial data for TWO phantom-supported Ellis-Bronnikov throats.
/*!
    This is the binary generalisation of SupportedWormholeInitialData.  A single
    throat of radius b in isotropic radius rbar has

        gamma_ij = Omega(rbar)^2 delta_ij,   Omega = 1 + b^2 / (4 rbar^2),
        chi      = Omega^{-2},  h_ij = delta_ij,
        phi_EB   = (1/sqrt(4 pi)) atan[ (rbar - b^2/(4 rbar)) / b ].

    Two throats are superposed in the conformal factor in the standard way (the
    same form BinaryBHInitialData uses, psi = 1 + sum of one-body excesses):

        psi = 1 + [psi_A(r_A) - 1] + [psi_B(r_B) - 1] + m_A/(2 r_A) + m_B/(2 r_B),
        psi_X(r) = sqrt(1 + b_X^2 / (4 r^2)),      chi = psi^{-4}.

    ---- WHY THE BARE MASS TERM EXISTS: MASSLESS THROATS DO NOT FALL --------
    The massless Ellis-Bronnikov throat is ULTRASTATIC: its lapse is exactly 1
    everywhere, so ALL of its curvature lives in the spatial metric.  Light
    passing by is deflected, but a test mass at rest feels no pull at any
    distance and stays at rest forever - the phantom scalar's negative energy
    exactly cancels the positive field energy, leaving
    psi = 1 + b^2/(8 r^2) + O(r^-4) with NO 1/r piece and hence M_ADM = 0.
    "Curved" and "attracts" are not the same thing: Newtonian attraction is
    the 1/r piece of the time-time metric, and this solution has neither.
    Two such throats therefore cannot orbit, cannot inspiral, and released
    from rest simply sit there.

    The fix is NOT to push them artificially.  The Ellis drainhole is a
    one-parameter family, and its other branch carries genuine positive ADM
    mass (the Lanzhou solutions quoted in research/merger/Plan.md).
    bare_mass_X adds the puncture-like m/(2r) piece of that branch, so each
    throat has M_ADM ~ m and the pair falls together UNDER ITS OWN GRAVITY -
    released from rest for a head-on, or with transverse Bowen-York momenta
    for an inspiral, exactly as for a binary black hole (where the momenta
    only set up the initial orbit; gravitational-wave emission does the
    inspiralling).  Near a throat the two 1/r behaviours combine
    (psi -> (b + m)/(2 r)), so the coordinate inversion - and hence the
    wormhole topology - survives.  Numerically this is exactly the
    bh1_bare_mass / bh2_bare_mass knob that the GRTresna solver already
    exposes, so Route A and Route B are parameterised the same way.

    Where this ansatz is exact and where it is not:

      * Pure-throat superposition error is O(b^2/d^2) with d the separation -
        parametrically BETTER than black-hole puncture superposition, whose
        error is O(m/d), because a b-throat has no 1/r tail.  For b = 0.5,
        d = 10 the cross term is ~2.5e-3.
      * Turning on bare_mass reintroduces an O(m/d) error, i.e. the same
        superposition quality as a superposed binary black hole, plus a
        Hamiltonian defect because the phantom profile below is the one that
        supports the MASSLESS throat, not the massive one.  Keep m/d small, or
        remove the defect with the GRTresna solve (Route B).
      * For a massless phantom (phantom_mass = 0) the Klein-Gordon operator is
        linear, so the MATTER sector superposes exactly; only the Hamiltonian
        constraint picks up a defect.

    Asymptotics of the scalar: each atan tends to +pi/2 as rbar -> infinity, so
    a plain sum tends to 2 * (1/sqrt(4 pi)) * (pi/2) ~= 0.886, whereas
    StateVariables declares the asymptotic value of phi to be ZERO and the
    Sommerfeld boundary condition uses that declared value.  With
    subtract_phi_asymptote = 1 (the default) the constant is removed so phi -> 0
    at the outer boundary.  Shifting phi by a constant is exactly free for a
    massless field; it is NOT free if phantom_mass != 0, and SimulationParameters
    warns in that case.

    Momentum: Bowen-York extrinsic curvature per throat,

        Ahat_ij = (3 / (2 r^2)) [ P_i n_j + P_j n_i - (delta_ij - n_i n_j) P.n ],

    summed over throats and converted to the CCZ4 variable with
    A_ij = chi^{3/2} Ahat_ij (the same convention as BinaryBHInitialData).
    With K = 0 and Pi = 0 the matter momentum density vanishes and Ahat_ij is
    flat-space divergence free, so the MOMENTUM constraint is satisfied
    EXACTLY - only the Hamiltonian constraint is violated at t = 0.
*/
class BinaryWormholeInitialData
{
  public:
    struct params_t
    {
        //! Initial lapse selector (same codes as the single-throat example):
        //! 0 = 1, 1 = sqrt(chi), 2 = 1 - 3 ln(chi), 3 = chi
        int initial_lapse_type;

        //! Grid center used for index -> physical coordinate mapping
        std::array<double, AMREX_SPACEDIM> grid_center;

        //! Throat radii.  b0_B = 0 removes throat B entirely (the
        //! single-throat regression mode of Plan.md Phases 1-2).
        double b0_A;
        double b0_B;

        //! Puncture bare masses - the m/(2r) piece of psi.  Zero is the
        //! massless, ultrastatic, NON-attracting throat; nonzero selects the
        //! massive drainhole branch, so the pair genuinely falls together
        //! under its own gravity (see the class comment).
        double bare_mass_A;
        double bare_mass_B;

        //! Throat positions, as OFFSETS RELATIVE TO grid_center (Coordinates
        //! has already subtracted grid_center by the time these are used).
        std::array<double, AMREX_SPACEDIM> centerA;
        std::array<double, AMREX_SPACEDIM> centerB;

        //! Bowen-York linear momenta.  Head-on: (0,0,-P) and (0,0,+P) with the
        //! throats on the +z / -z axis.  Quasi-circular: transverse momenta.
        std::array<double, AMREX_SPACEDIM> momentumA;
        std::array<double, AMREX_SPACEDIM> momentumB;

        //! 1 = shift phi so that it tends to 0 at spatial infinity
        int subtract_phi_asymptote;

        double phantom_mass;
        double support_strength;
    };

    BinaryWormholeInitialData(params_t a_params, double a_dx)
        : m_params(a_params), m_dx(a_dx)
    {
    }

    template <class data_t>
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
    compute(int i, int j, int k, amrex::Array4<data_t> cell) const
    {
        amrex::IntVect grid_index(i, j, k);
        Coordinates coords(grid_index, m_dx, m_params.grid_center);

        const data_t x = coords.x;
        const data_t y = coords.y;
        const data_t z = coords.z;

        const double bA    = m_params.b0_A;
        const double bB    = m_params.b0_B;
        const double bA_sq = bA * bA;
        const double bB_sq = bB * bB;

        const data_t dxA = x - (data_t)m_params.centerA[0];
        const data_t dyA = y - (data_t)m_params.centerA[1];
        const data_t dzA = z - (data_t)m_params.centerA[2];
        const data_t rA2 = dxA * dxA + dyA * dyA + dzA * dzA;

        const data_t dxB = x - (data_t)m_params.centerB[0];
        const data_t dyB = y - (data_t)m_params.centerB[1];
        const data_t dzB = z - (data_t)m_params.centerB[2];
        const data_t rB2 = dxB * dxB + dyB * dyB + dzB * dzB;

        const data_t eps2    = (data_t)1.0e-24;
        const data_t rA2_reg = simd_max(rA2, eps2);
        const data_t rB2_reg = simd_max(rB2, eps2);
        const data_t rA      = sqrt(rA2_reg);
        const data_t rB      = sqrt(rB2_reg);

        // ---- Geometry: superposed conformal factor --------------------------
        // psi = 1 + [one-body excesses] + [bare-mass punctures], chi = psi^{-4}
        // (the BinaryBHInitialData convention).  For a single throat with
        // m = 0 this collapses to psi^4 = (1 + b^2/(4 r^2))^2, i.e. exactly
        // the chi of SupportedWormholeInitialData.
        data_t psi = 1.0;
        if (bA > 0.0)
        {
            psi += sqrt(1.0 + (data_t)bA_sq / (4.0 * rA2_reg)) - 1.0;
        }
        if (bB > 0.0)
        {
            psi += sqrt(1.0 + (data_t)bB_sq / (4.0 * rB2_reg)) - 1.0;
        }
        psi += (data_t)(0.5 * m_params.bare_mass_A) / rA +
               (data_t)(0.5 * m_params.bare_mass_B) / rB;

        const data_t psi2 = psi * psi;
        data_t chi        = 1.0 / (psi2 * psi2);
        if (chi < (data_t)1.0e-10)
            chi = (data_t)1.0e-10;

        const data_t h11 = 1.0, h12 = 0.0, h13 = 0.0;
        const data_t h22 = 1.0, h23 = 0.0, h33 = 1.0;

        // ---- Extrinsic curvature: superposed Bowen-York ---------------------
        // K = 0 (maximal), so A_ij carries the whole of K_ij.
        data_t A11 = 0.0, A12 = 0.0, A13 = 0.0;
        data_t A22 = 0.0, A23 = 0.0, A33 = 0.0;

        const bool boostA = (m_params.momentumA[0] != 0.0) ||
                            (m_params.momentumA[1] != 0.0) ||
                            (m_params.momentumA[2] != 0.0);
        const bool boostB = (m_params.momentumB[0] != 0.0) ||
                            (m_params.momentumB[1] != 0.0) ||
                            (m_params.momentumB[2] != 0.0);

        if (boostA)
        {
            add_bowen_york(dxA / rA, dyA / rA, dzA / rA, rA2_reg,
                           m_params.momentumA[0], m_params.momentumA[1],
                           m_params.momentumA[2], A11, A12, A13, A22, A23, A33);
        }
        if (boostB)
        {
            add_bowen_york(dxB / rB, dyB / rB, dzB / rB, rB2_reg,
                           m_params.momentumB[0], m_params.momentumB[1],
                           m_params.momentumB[2], A11, A12, A13, A22, A23, A33);
        }

        if (boostA || boostB)
        {
            // A_ij(CCZ4) = psi^{-6} Ahat_ij = chi^{3/2} Ahat_ij, exactly as in
            // BinaryBHInitialData::compute_A.
            const data_t conv = chi * sqrt(chi);
            A11 *= conv;
            A12 *= conv;
            A13 *= conv;
            A22 *= conv;
            A23 *= conv;
            A33 *= conv;
        }

        // ---- Matter: superposed phantom scalar ------------------------------
        // One atan profile per PRESENT throat (b_X > 0).  A bare-mass-only
        // puncture carries no scalar - it is a plain Brill-Lindquist term.
        const data_t norm = (data_t)(1.0 / sqrt(4.0 * M_PI));
        data_t phi        = 0.0;
        int n_throats     = 0;
        if (bA > 0.0)
        {
            const data_t argA = (rA - (data_t)bA_sq / (4.0 * rA)) / (data_t)bA;
            phi += norm * atan(argA);
            ++n_throats;
        }
        if (bB > 0.0)
        {
            const data_t argB = (rB - (data_t)bB_sq / (4.0 * rB)) / (data_t)bB;
            phi += norm * atan(argB);
            ++n_throats;
        }

        if (m_params.subtract_phi_asymptote != 0)
        {
            // Each atan -> +pi/2 as r -> infinity.
            phi -= (data_t)((double)n_throats * (1.0 / sqrt(4.0 * M_PI)) *
                            (M_PI / 2.0));
        }

        // NOTE: there is deliberately NO seeded Gaussian perturbation here.
        // The single-throat example needs one (its whole point is to pick the
        // Shinkai-Hayward compressive or rarefactive branch); a merger does
        // not.  The other throat IS the perturbation, and pre-destabilising
        // the throats would contaminate the very thing this run measures -
        // whether gravity alone drives them together and what happens when
        // they meet.  Start each throat in its own exact equilibrium.

        // Pi = 0: the scalar is momentarily static, so the matter momentum
        // density vanishes and the Bowen-York A_ij solves the momentum
        // constraint exactly.
        const data_t Pi = 0.0;

        // ---- Gauge ----------------------------------------------------------
        data_t lapse = 1.0;
        if (m_params.initial_lapse_type == 1)
        {
            lapse = sqrt(chi);
        }
        else if (m_params.initial_lapse_type == 2)
        {
            lapse = 1.0 - (data_t)3.0 * log(chi);
        }
        else if (m_params.initial_lapse_type == 3)
        {
            lapse = chi;
        }
        else if (m_params.initial_lapse_type == 4)
        {
            // Origin-isolating lapse, ported from
            // Examples/SupportedWormholeCollapse and generalised to two
            // throats.  This exists because of a specific, reproducible
            // failure: at r -> 0 an Ellis-Bronnikov throat has chi ~ r^4, so
            // the coordinate origin is the OTHER universe's spatial infinity
            // squeezed into a point.  Refining the throat necessarily drags
            // cells into it (the throat sits at r = b/2 and refinement boxes
            // are >= 16 cells), and evolving that region with a flat lapse
            // produces NaN in h_ij at max_level >= 3 within two coarse steps.
            //
            // alpha = prod_c [1 - exp(-(r_c / 0.3 b_c)^8)] freezes each
            // origin (alpha -> 0 as r_c -> 0) while the EIGHTH power makes
            // the cutoff so sharp that alpha = 1 to machine precision by the
            // time it reaches the throat: at r = b/2 the exponent is
            // (1/0.6)^8 ~ 60, and exp(-60) is below double precision.  The
            // published flat-lapse physics is therefore untouched everywhere
            // it is being measured.  That sharpness is the whole point, and
            // it is what makes this preferable to alpha = sqrt(chi), which
            // suppresses the lapse everywhere chi < 1 -- including at the
            // throat, i.e. exactly where the dynamics under study lives.
            //
            // A binary needs the product: each throat carries its own
            // compactified origin and neither can be put on a symmetry
            // boundary, which is how the single-throat example avoided this.
            lapse = 1.0;
            if (m_params.b0_A > 0.0 || m_params.bare_mass_A > 0.0)
            {
                const data_t core_A =
                    (data_t)(0.3 * (m_params.b0_A > 0.0
                                        ? m_params.b0_A
                                        : m_params.bare_mass_A));
                const data_t s2 = (rA / core_A) * (rA / core_A);
                const data_t s8 = s2 * s2 * s2 * s2;
                lapse *= 1.0 - exp(-s8);
            }
            if (m_params.b0_B > 0.0 || m_params.bare_mass_B > 0.0)
            {
                const data_t core_B =
                    (data_t)(0.3 * (m_params.b0_B > 0.0
                                        ? m_params.b0_B
                                        : m_params.bare_mass_B));
                const data_t s2 = (rB / core_B) * (rB / core_B);
                const data_t s8 = s2 * s2 * s2 * s2;
                lapse *= 1.0 - exp(-s8);
            }
        }
        if (lapse < (data_t)1.0e-10)
            lapse = (data_t)1.0e-10;

        cell(i, j, k, c_chi) = chi;
        cell(i, j, k, c_h11) = h11;
        cell(i, j, k, c_h12) = h12;
        cell(i, j, k, c_h13) = h13;
        cell(i, j, k, c_h22) = h22;
        cell(i, j, k, c_h23) = h23;
        cell(i, j, k, c_h33) = h33;

        cell(i, j, k, c_K)   = 0.0;
        cell(i, j, k, c_A11) = A11;
        cell(i, j, k, c_A12) = A12;
        cell(i, j, k, c_A13) = A13;
        cell(i, j, k, c_A22) = A22;
        cell(i, j, k, c_A23) = A23;
        cell(i, j, k, c_A33) = A33;

        cell(i, j, k, c_lapse)  = lapse;
        cell(i, j, k, c_shift1) = 0.0;
        cell(i, j, k, c_shift2) = 0.0;
        cell(i, j, k, c_shift3) = 0.0;
        cell(i, j, k, c_B1)     = 0.0;
        cell(i, j, k, c_B2)     = 0.0;
        cell(i, j, k, c_B3)     = 0.0;

        cell(i, j, k, c_Theta) = 0.0;

        cell(i, j, k, c_phi) = phi;
        cell(i, j, k, c_Pi)  = Pi;
    }

  protected:
    //! Accumulate one Bowen-York term into the (still conformal-unscaled)
    //! Ahat_ij.  (nx,ny,nz) is the unit radial vector from the throat and r2
    //! the (regularised) squared distance to it.
    template <class data_t>
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE static void
    // NOLINTNEXTLINE(bugprone-easily-swappable-parameters)
    add_bowen_york(const data_t nx, const data_t ny, const data_t nz,
                   const data_t r2, const double Px, const double Py,
                   const double Pz, data_t &A11, data_t &A12, data_t &A13,
                   data_t &A22, data_t &A23, data_t &A33)
    {
        const data_t Pn =
            nx * (data_t)Px + ny * (data_t)Py + nz * (data_t)Pz;
        const data_t f = (data_t)1.5 / r2;

        A11 += f * (2.0 * (data_t)Px * nx - (1.0 - nx * nx) * Pn);
        A22 += f * (2.0 * (data_t)Py * ny - (1.0 - ny * ny) * Pn);
        A33 += f * (2.0 * (data_t)Pz * nz - (1.0 - nz * nz) * Pn);
        A12 += f * ((data_t)Px * ny + (data_t)Py * nx + nx * ny * Pn);
        A13 += f * ((data_t)Px * nz + (data_t)Pz * nx + nx * nz * Pn);
        A23 += f * ((data_t)Py * nz + (data_t)Pz * ny + ny * nz * Pn);
    }

    params_t m_params;
    double m_dx;
};

#endif /* BINARYWORMHOLEINITIALDATA_HPP_ */
