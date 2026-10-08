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
    mass (the Lanzhou solutions).
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

    ---- ID TYPE 1: THE REGULAR MASSIVE DRAINHOLE (recommended) -------------
    Everything above is id_type = 0, and it has a measured, fatal flaw: the
    bare-mass term is a Brill-Lindquist puncture, so psi -> m/(2r) and chi -> 0
    AT THE THROAT ITSELF.  The minimal surface sits at r = m/2 where chi = 1/16,
    i.e. the proper cell width dx/sqrt(chi) there is 4 dx, and it keeps growing
    inwards - measured 6.2 proper units at dx = 0.5 on an m = 2 solve, against a
    throat of areal radius 4.5.  One cell was wider than the throat, and no
    matter model could be evaluated on the geometry.

    id_type = 1 earns the same ADM mass from the LAPSE instead, and leaves the
    spatial conformal factor bounded.  With the Ellis coordinate

        X     = (r - a^2/(4 r)) / a,        Omega = 1 + a^2/(4 r^2),

    the massive Ellis-Bronnikov drainhole is, exactly,

        u     = (m/a) (atan X - pi/2)                 -> 0 at infinity
        alpha = e^{u}                                 the exact static lapse
        gamma_ij = e^{-2u} Omega^2 delta_ij   =>  chi = e^{2u} / Omega^2
        phi   = sqrt(a^2 + m^2) / (a sqrt(4 pi)) * atan X
        K = 0,  A_ij = 0,  Pi = 0.

    a is `wormhole_throat_radius_X` (at m = 0 it IS the areal throat radius) and
    m is `wormhole_drainhole_mass_X`, which is the ADM mass.  Setting m = 0
    recovers the massless Ellis throat of id_type = 0 with bare_mass = 0, so the
    two branches agree where they overlap.

    This is an exact static solution of Einstein + massless phantom scalar, so
    for a SINGLE throat both constraints hold identically at t = 0 - unlike the
    superposed puncture data, which carried a Hamiltonian defect by construction.

    Properties that are derived, not assumed (verified numerically by
    grteclyn-wrapper/scripts/validation/drainhole_throat_check.py):

      * the minimal surface is at l = m, i.e. r = (m + sqrt(m^2 + a^2)) / 2 -
        NOT at l = 0, which is where the massless case would put it;
      * R_min = e^{-u(m)} sqrt(m^2 + a^2);
      * chi at the throat stays in [0.15, 0.25] for m/a in [0, 1], so the proper
        cell width there is 2.0-2.6 dx whatever the mass.  That is the point of
        the whole exercise: mass no longer costs resolution;
      * the genuinely unresolvable region (chi < 0.01) is the compactified far
        universe and it sits well INSIDE the minimal surface (0.98 against a
        throat at 2.69 for a = 4, m = 1.2), so lapse type 6 can freeze it
        without touching the throat.

    Superposition for two throats, in the same excess form as id_type = 0:

        u_sum = u_A + u_B,        alpha = e^{u_sum}
        psi   = 1 + [sqrt(Omega_A) - 1] + [sqrt(Omega_B) - 1],
        chi   = e^{2 u_sum} psi^{-4},       phi = phi_A + phi_B.

    Each u_X vanishes at infinity, so the ADM masses add.  Exact for one throat;
    for two the error is the usual O(a^2/d^2) plus O(m/d) - the Helfer/Ning
    correction and then a CTTK solve replace it.

    ---- THE HELFER/NING ONE-BODY CORRECTION (helfer_correction = 1) --------
    Plain superposition is not innocent near a throat.  Expand it about throat
    A's centre: the companion's fields are smooth there, so to leading order

        psi   -> psi_A(r_A) + [psi_B(x_A) - 1],     u -> u_A(r_A) + u_B(x_A),

    i.e. throat A is handed two CONSTANTS it did not ask for.  They rescale its
    spatial metric by a uniform factor,

        gamma_ij(near A) = e^{-2 u_B(x_A)} (1 + dpsi / psi_A)^4 x [isolated A],

    which for the production binary (a = 2, m = 1, d = 12) is e^{+0.167} = 1.18
    on lengths and 1.28 on the volume element.  Throat A therefore starts 18%
    larger than the static solution its own field equations support, so it is
    not in equilibrium and it rings - which is precisely the failure Helfer,
    Sperhake, Croft, Radia, Ge & Lim diagnose ("Malaise and remedy of binary
    boson-star initial data", CQG 39, 074001, 2022, arXiv:2108.11995): "the
    spurious alteration of the volume element ... mimics a squeeze", and it is
    WORSE for horizonless objects "due to the lack of a horizon and its
    potentially protective character".  Ning et al. (arXiv:2604.15240) carry
    the same idea to a one-body conformal-factor correction and report that it
    "substantially suppresses these artifacts".

    Their remedy (Helfer Eq. 45) is to subtract the companion's value AT THIS
    BODY'S CENTRE instead of the flat metric,

        gamma_ij = gamma_ij^A + gamma_ij^B - gamma_ij^B(x_A),

    which is exactly "give each throat back its own constants".  Applied
    literally and globally it would leave psi and alpha away from 1 at spatial
    infinity, breaking asymptotic flatness and the Sommerfeld boundary
    condition that reads the asymptotic values off StateVariables.  So the
    subtraction is WINDOWED onto the body it repairs:

        psi   -= W_A dpsi_A + W_B dpsi_B,   u_sum -= W_A du_A + W_B du_B,
        W_X(r_X) = exp[-(r_X / w)^p],
        dpsi_A = psi_B(x_A) - 1,  du_A = u_B(x_A),   (and A <-> B)

    with w = helfer_width (default d/3) and p = helfer_power (default 2).

    THE WINDOW IS NOT FREE, AND ITS SHAPE IS THE WHOLE ENGINEERING PROBLEM.
    A window that turns off over a length w has curvature ~1/w^2, and the
    Hamiltonian constraint sees that curvature multiplied by the constant being
    removed (du = -0.083 at the production binary, which is the DOMINANT piece
    - it is 24x larger than dpsi).  So the correction repairs the throat's size
    by adding a constraint defect of its own.  Both halves of that trade were
    measured, at a = 2, m = 1, d = 12, N = 192, against a plain-superposition
    L2_Ham of 5.22e-4 (throat size from the analytic areal radius, on-axis
    towards and away from the companion; isolated = 3.88955):

       w / p     throat size error      L2_Ham      vs plain
       plain     +8.1% / +10.9%         5.22e-4      1.00x
       0.4d / 6  -1.1% /  +1.5%         4.71e-3      9.02x   <- literal Eq. 45
       0.5d / 3  -0.9% /  +1.6%         1.75e-3      3.36x
       d/3  / 2  +0.2% /  +2.8%         9.60e-4      1.84x   <- default
       d/4  / 2  +1.1% /  +3.7%         8.68e-4      1.66x
       d/6  / 2  +3.1% /  +5.6%         7.97e-4      1.53x

    The default is the knee: it removes 84% of the spurious inflation for less
    than 2x the constraint defect, where insisting on the last 16% costs 9x.
    Both columns are continuum properties - the corrected defect changes by
    1.5% between N = 192 and N = 384, i.e. it does not converge away, exactly
    like the superposition defect it is trading against.

    WHICH COLUMN MATTERS IS AN EMPIRICAL QUESTION AND IS NOT SETTLED HERE.
    Helfer et al.'s claim is about DYNAMICS - a body that starts the wrong size
    rings, and the ringing is what destroys horizonless objects - not about the
    initial constraint norm, which their fix also worsens.  The decisive test
    is an evolution, not this table.  Until that test is run, the honest
    reading is: this flag trades a measured 9.5% error in each throat's initial
    size for a measured 1.8x increase in the initial Hamiltonian violation.

    The SCALAR needs no correction.  The companion leaves a constant offset at
    x_A there too, but for a massless phantom the constraints see only
    (grad phi)^2, so that constant is exactly free - the same argument that
    makes subtract_phi_asymptote free.  It is NOT free at phantom_mass != 0.

    Exact only for equal bodies: the subtracted constant is a one-body value,
    and for unequal masses the weighted-subtraction generalisation of Croft
    et al. is needed instead.  SimulationParameters warns if the two throats
    differ.  This corrects the CONSTANT part of the cross term, i.e. each
    throat's equilibrium size; it does not touch the O(a^2/d^2) gradient part,
    which only a constraint solve (Route B) removes.  Default is 0 = off, and
    with it off not one expression below changes, so archived runs reproduce
    bit for bit.

    Momentum: Bowen-York extrinsic curvature per throat,

        Ahat_ij = (3 / (2 r^2)) [ P_i n_j + P_j n_i - (delta_ij - n_i n_j) P.n ],

    summed over throats and converted to the CCZ4 variable with
    A_ij = chi^{3/2} Ahat_ij (the same convention as BinaryBHInitialData).
    With K = 0 and Pi = 0 the matter momentum density vanishes and Ahat_ij is
    flat-space divergence free, so the MOMENTUM constraint is satisfied
    EXACTLY - only the Hamiltonian constraint is violated at t = 0.

    Boosted scalar (V2 only, default off): a throat profile moving rigidly
    with coordinate velocity v has d_t phi = -v . grad phi, and with the
    evolution convention d_t phi = alpha Pi + beta . grad phi (beta = 0 at
    t = 0) that is

        Pi = -(v_A . grad phi_A + v_B . grad phi_B) / alpha,

    each throat's own analytic gradient, so the scalar starts moving WITH the
    Bowen-York momentum instead of being left behind by it.  This breaks the
    momentum constraint at O(v): the scalar now carries the momentum density
    S_i = -Pi d_i phi (with the phantom sign) that Bowen-York knows nothing
    about, and only a re-solve of the vector Laplacian would absorb it.  The
    residual is measured, not hidden: it is the t = 0 row of
    constraint_norms.dat (L2_Mom, exactly 0 without the boost), repeated in
    the log with a "boost" label.  Pi is finite at the compactified origins
    (grad phi -> 4 C / b there) unless the lapse itself is floored.  It is
    also not the moving throat's Pi: the exact boost below has
    Pi = -(N v / Q) phi' (e.n), smaller by ~alpha^2/Q (1/17 at the a = 2,
    m = 1 throat), because there the slice's shift carries most of the
    motion.

    ---- EXACT BOOST (momentum_model = 1) ----------------------------------
    Bowen-York momentum (momentum_model = 0) moves the METRIC and leaves the
    scalar that holds the throat open at rest.  That is not a moving throat:
    the single-throat probes of 2026-09-29 (L = 64, level 3, mode-3 solve)
    inflate with a kick that grows as p^2 -- at rest flat to 1e-5, p = 0.12
    and 0.45 at +10 % by t = 32 and 20 -- while a uniformly moving exact
    wormhole is the static one seen from another frame and cannot change its
    fate.  momentum_model = 1 lays down that moving exact wormhole.

    The static drainhole is ds^2 = -alpha^2 dt^2 + Q (dx^2 + dy^2 + dz^2),
    alpha = e^u, Q = e^{-2u} Omega^2 (= Psi^4), phi = C atan X, functions of
    the isotropic radius r.  Boost it with velocity v e (gamma^-2 = 1 - v^2)
    and cut it at lab time t' = 0, i.e. at static time t = -v e.x.  A lab
    point at offset d from the throat is the rest-frame point
    x = d + (gamma - 1)(e.d) e, r = |x|, n = x / r; with nt = n +
    (gamma - 1)(e.n) e (the lab gradient of r) the slice carries

        gamma_ij = Q [delta_ij + eps e_i e_j],   eps = gamma^2 v^2 (1 - alpha^2/Q),
        K_ij     = N v { gamma (u' - Q'/2Q) (e_i nt_j + e_j nt_i)
                         + (e.n) (Q'/2Q) delta_ij
                         + (e.n) gamma^2 v^2 (Q'/2Q - alpha^2 u'/Q) e_i e_j },
        Pi       = -(N v / Q) phi' (e.n),    N = alpha / sqrt(1 - v^2 alpha^2/Q),
        lapse    = N / gamma,   shift^i = v (alpha^2/Q - 1) / (1 - v^2 alpha^2/Q) e^i

    (' = d/dr).  Both constraints hold identically: by fourth-order finite
    differences of these closed forms the Hamiltonian and momentum residuals
    are 1e-9 of their terms at v = 0.41, the exact static throat's own
    level, and this lapse and shift carry the slice rigidly (d_t gamma_ij and
    d_t phi from them equal -v e.grad of the same fields to 1e-12).  The
    throat's ADM mass is gamma m and its momentum gamma m v, so
    momentumA/B are read as P = gamma m v: v = |P| / sqrt(m^2 + |P|^2),
    e = P / |P| (m = the drainhole mass, which must be > 0 to move).

    Two throats: U = sum u_X and psi = 1 + sum (sqrt(Omega_X) - 1) at each
    throat's rest-frame radius, Psi = e^{-U/2} psi (the superposition above
    with r_X -> the boosted radius), gamma_ij = Psi^4 [delta_ij + sum eps_X
    e_X e_X], phi summed, the lapse the product of the throats' and the
    shift their sum.  Near throat X the superposition is Psi = F Psi_X with
    F smooth: X's lengths rescaled by F^2, under which its exact data take
    K_ij -> F^2 K_ij and Pi -> Pi / F^2.  So each throat's K_ij and Pi enter
    with that weight, windowed by exp[-(r_X / (d/2))^4] to stay bounded at
    the companion's puncture, and each throat's anisotropy, K_ij and Pi are
    cut inside the companion (collar profile, 0.3 a), so each far side holds
    its own throat only (BoostBackground).  Exact for one throat; for
    two, constraint_solve = 1 removes the rest of the superposition's error
    from BOTH constraints, through w and a vector potential W (Ahat ->
    Ahat + L_G W; DrainholeConstraintSolve.cpp).  The CCZ4 variables
    follow from gamma_ij and K_ij: chi = det(gamma)^{-1/3}, h_ij = chi
    gamma_ij, A_ij = chi (K_ij - gamma_ij K / 3), and Gamma^i from the closed
    form d_k h_ij (h is not flat, so Gamma^i is not zero).  Refused with a
    seed, the Helfer correction, the V2 boost, phantom_mass != 0 and every
    lapse type but 5 and 6 (the boosted lapse, times the collar for 6).

    ---- THE HAMILTONIAN-CONSTRAINT SOLVE (constraint_solve = 1) -----------
    With Pi = 0, K = 0 and conformally flat data, gamma_ij = Psi^4 delta_ij
    (Psi^4 = 1/chi), the Hamiltonian constraint for this matter is

        lap Psi - V Psi + (1/8) Ahat_ij Ahat^ij Psi^{-7} = 0,
        V = pi s |grad phi|^2   (s = support_strength, flat operators).

    The single drainhole solves it exactly with Ahat = 0: its Psi =
    e^{-u/2} sqrt(Omega) satisfies lap Psi = V Psi identically.  The superposed
    Psi_0 = e^{-u_sum/2} psi does not, and DrainholeConstraintSolve.cpp adds a
    correction w so that Psi = Psi_bg + w does, holding phi and Ahat_ij fixed:
    the momentum constraint stays exact, and Pi, K, h_ij and the lapse are
    untouched.  constraint_background() below supplies Psi_bg, its Laplacian
    in closed form, V and Ahat.Ahat; compute(..., solved = true, w) then
    rebuilds chi = (Psi_bg + w)^{-4} and A_ij = chi^{3/2} Ahat_ij from them.

    Near each centre Psi ~ c/r: the throat's far side, a compactified
    infinity.  c is the one free number per throat, the puncture coefficient.
    The isolated drainhole has c = (a/2) e^{pi m / 2a}; the superposition hands
    throat A the factor e^{-u_B(x_A)/2} on top (1.064 at d = 8), exactly the
    uniform rescaling that keeps a static throat static in the companion's
    potential.  The background therefore carries c through
    m_solve_shift_X / r_X.

    WHICH THROAT IS IT?  Its far side says so: Psi = c/r + d near the centre,
    and the inversion r' = c^2/r makes that an asymptotically flat end with
    ADM mass M_far = 2 c d and scalar charge Q_far = 4 C c^2 / a, both frozen
    in time.  The isolated (a, m) throat has M_far = -m e^{pi m/a} and
    Q_far = sqrt(a^2 + m^2) e^{pi m/a} / sqrt(4 pi): -4.8105 and 3.0344 for
    a = 2, m = 1.  (M_far, Q_far) name one isolated drainhole (a', m'), and m'
    is the mouth's one-body mass.  DrainholeConstraintSolve measures all of it
    after every solve.  The d = 8 head-on, L = 64, level 3, t = 0 (CPU,
    2026-09-27; R_min over coordinate spheres, M_ADM from the volume
    identity in DrainholeConstraintSolve.hpp):

                          R_min   M_far    Q_far   m'      M_ADM   M_ADM - sum m'
      isolated throat     3.890   -4.810   3.034   1       1
      superposed pair     4.466   -5.363   3.436   1.149   2.00 (not a solution)
      mode 0 (solved)     4.523   -5.368   3.436   1.148   2.738   +0.44
      mode 1              4.197   -4.60    3.034   1.041   2.434
      mode 3, c alone     4.289   -4.810   3.146   1.071   2.521   +0.38
      mode 3              3.892   -4.810   3.034   1.000   2.362   +0.36

    So the superposition's mouths are not the isolated throat: the
    companion's constants make each one ~1.13 x larger in every length, and
    the solve at the superposition's c keeps them so (M_far moves 0.09 %, what
    the Robin face's constant offset of w accounts for).  phi fixes the static
    throat's coordinate size, so c alone cannot undo that; mode 3 changes the
    coordinate size too.

      mode 0 (superposed, default): c = the superposition's own, shift 0.
             w is bounded at the centres and each throat keeps its superposed
             far side and size.
      mode 1 (isolated): c = (a/2) e^{pi m/2a}.  In the companion's potential
             this is a 6 % smaller c than a static throat wants -- a spherical
             seed of that size.
      mode 2 (explicit): c = constraint_solve_puncture_coefficient_A/B.
      mode 3 (far-side matched): throat X at coordinate scale sigma_X (a ->
             sigma a and m -> sigma m in phi, u and Omega; C is scale-free),
             sigma_X = (c_X / c_iso)^2 so that Q_far is the isolated value,
             and c_X iterated until M_far is too (finite-difference Jacobian,
             then Broyden; 2 passes, 5 solves).  Matching both far-side
             numbers is the local static drainhole at its isolated size: R_min
             comes out 0.06 % from R* = 3.8895 without being asked for.  At
             d = 8, c = 2.0309, sigma = 0.8574.  constraint_solve_match_charge
             = 0 keeps sigma = 1 and matches M_far with c alone: R_min stays
             10 % above R*, Q_far 3.7 %.

    What the pair adds to its mouths' one-body masses: for the flipped pair
    (which attracts) +0.36 at mode 3, for the like pair (which repels) -0.62.
    Their mean, -0.13, is the Newtonian binding -m^2/d = -0.125, as for
    black-hole punctures; half their difference, +-0.49, is the ghost scalar's
    cross energy, -int grad phi_A . grad phi_B = +-(a^2 + m^2)/d = +-0.63 for
    point charges.  It is positive where the throats attract: the pair's mass
    goes the way of its scalar field energy, not of its force.

    Background 1 (constraint_solve_background = 1) replaces Psi_0 by the bare
    punctures 1 + sum c_X / r_X.  It is a validation mode: on one throat the
    solve must rebuild the whole drainhole from it, and on two it must agree
    with background 0 at the same c.

    The solve is refused (SimulationParameters) with a conformal-factor seed,
    the Helfer correction, a boosted scalar, id_type 0, phantom_mass != 0 or
    an external grid: the first is erased by it (at fixed phi and c the
    single throat's solution is unique, and it is the static throat), and the
    others are not the background written here.
*/
class BinaryWormholeInitialData
{
  public:
    struct params_t
    {
        //! Initial lapse selector (same codes as the single-throat example):
        //! 0 = 1, 1 = sqrt(chi), 2 = 1 - 3 ln(chi), 3 = chi
        int initial_lapse_type;

        //! Origin-isolating lapse (type 4) collar: alpha = 1 - exp(-(r/f b)^p)
        //! with f = lapse_core_fraction and p = lapse_core_power.  Defaults
        //! reproduce the published 0.3 / 8; see the type 4 branch below for
        //! why lowering both is what makes the collar resolvable.
        double lapse_core_fraction{0.3};
        double lapse_core_power{8.0};

        //! Grid center used for index -> physical coordinate mapping
        std::array<double, AMREX_SPACEDIM> grid_center;

        //! Initial-data family: 0 = isotropic Ellis + Brill-Lindquist bare
        //! mass (the original, kept so archived runs reproduce), 1 = regular
        //! massive drainhole (see the class comment).  Default 0.
        int id_type;

        //! Throat radii.  b0_B = 0 removes throat B entirely (the
        //! single-throat regression mode).  Under
        //! id_type = 1 this is the drainhole scale a, which at m = 0 is the
        //! areal throat radius exactly.
        double b0_A;
        double b0_B;

        //! Puncture bare masses - the m/(2r) piece of psi.  Zero is the
        //! massless, ultrastatic, NON-attracting throat; nonzero selects the
        //! massive drainhole branch, so the pair genuinely falls together
        //! under its own gravity (see the class comment).
        double bare_mass_A;
        double bare_mass_B;

        //! Drainhole ADM masses (id_type = 1 only).  Unlike bare_mass these
        //! enter through the lapse, not the conformal factor, so raising them
        //! does NOT degrade chi at the throat.
        double drainhole_mass_A;
        double drainhole_mass_B;

        //! Throat positions, as OFFSETS RELATIVE TO grid_center (Coordinates
        //! has already subtracted grid_center by the time these are used).
        std::array<double, AMREX_SPACEDIM> centerA;
        std::array<double, AMREX_SPACEDIM> centerB;

        //! Bowen-York linear momenta.  Head-on: (0,0,-P) and (0,0,+P) with the
        //! throats on the +z / -z axis.  Quasi-circular: transverse momenta.
        std::array<double, AMREX_SPACEDIM> momentumA;
        std::array<double, AMREX_SPACEDIM> momentumB;

        //! Coordinate boost velocity of each throat's scalar profile (V2
        //! only): Pi = -(v . grad phi) / alpha per throat, see the class
        //! comment.  Default 0 = off, bit for bit.  B defaults to -A.
        std::array<double, AMREX_SPACEDIM> boost_velocity_A{{0.0, 0.0, 0.0}};
        std::array<double, AMREX_SPACEDIM> boost_velocity_B{{0.0, 0.0, 0.0}};

        //! How a throat's momentum enters the data: 0 = Bowen-York extrinsic
        //! curvature on the static throat, the scalar at rest (archived, bit
        //! for bit); 1 = the exact Lorentz-boosted drainhole, metric, K_ij,
        //! scalar and Pi together, with momentumA/B read as each throat's
        //! ADM momentum gamma m v (see "EXACT BOOST" in the class comment).
        int momentum_model{0};
        //! momentum_model = 1: 1 = start from the boosted solution's own
        //! shift (the coordinates move with the throat), 0 = zero shift.
        int boost_initial_shift{1};
        //! momentum_model = 1: each throat's velocity v e, from its ADM
        //! momentum gamma m v and its drainhole mass (boost_kinematics, set
        //! once by SimulationParameters).  The solve's coordinate rescaling
        //! of a and m does not touch it: the speed is physical.
        std::array<double, AMREX_SPACEDIM> boost_v_A{{0.0, 0.0, 0.0}};
        std::array<double, AMREX_SPACEDIM> boost_v_B{{0.0, 0.0, 0.0}};

        //! 1 = shift phi so that it tends to 0 at spatial infinity
        int subtract_phi_asymptote;

        //! Sign of throat B's scalar profile (+1.0 or -1.0, default +1.0).
        //! phi -> -phi is exact for a single drainhole (the mirror throat:
        //! same geometry, opposite scalar orientation), so either sign is a
        //! valid body.  The RELATIVE sign sets the scalar force between the
        //! pair: a phantom field REPELS like charges and ATTRACTS opposite
        //! ones, with |F_phi/F_grav| = (a^2+m^2)/m^2 -- always > 1, so
        //! like-charge throats can never merge under their own gravity
        //! (measured on orbit_d12_p012, 2026-08-31).  -1 turns that push
        //! into a pull and is the gravity-driven route to a merger.
        double phi_sign_B;

        //! Helfer/Ning one-body correction: 0 = off (plain superposition, the
        //! archived behaviour, bit for bit), 1 = on.  See the class comment.
        int helfer_correction{0};

        //! Width w of the correction window exp[-(r/w)^p], in code units.
        //! 0 (the default) means auto: 1/3 of the throat separation, which
        //! leaves exp(-9) = 1.2e-4 of the correction at the companion whatever
        //! the separation is.
        double helfer_width{0.0};

        //! Exponent p of the correction window.  Large p buys a flatter core
        //! but a sharper shoulder, and the shoulder is what costs Hamiltonian
        //! constraint - see the trade-off table in the class comment for why
        //! the default is 2 and not the 6 that a flat core would want.
        double helfer_power{2.0};

        double phantom_mass;
        double support_strength;

        //! The perturbation dial (see SimulationParameters): amplitude eps and
        //! width w of a unit Gaussian shell on each throat's minimal surface,
        //! multiplied into psi.  0 = off, bit for bit; width 0 = a/4.
        double seed_amplitude_A{0.0};
        double seed_amplitude_B{0.0};
        double seed_width_A{0.0};
        double seed_width_B{0.0};

        //! The quadrupolar half of the dial: the same shell (same width) times
        //! P2(cos theta) = (3 z^2/r^2 - 1)/2 about the z axis through each
        //! throat's centre.  0 = off, bit for bit.
        double seed_l2_amplitude_A{0.0};
        double seed_l2_amplitude_B{0.0};

        //! Hamiltonian-constraint solve (see the class comment).  These only
        //! shape the background the solve starts from; with the solve off
        //! (the default) none of them is read in compute().
        //! Background: 0 = the superposition, 1 = bare punctures (validation).
        int solve_background{0};
        //! Puncture coefficients c_A, c_B the solved data carry.  Filled on
        //! the host by SimulationParameters from the puncture mode.
        double solve_puncture_A{0.0};
        double solve_puncture_B{0.0};
    };

    BinaryWormholeInitialData(params_t a_params, double a_dx)
        : m_params(a_params), m_dx(a_dx)
    {
        const double bA = m_params.b0_A;
        const double bB = m_params.b0_B;
        for (int idir = 0; idir < AMREX_SPACEDIM; ++idir)
        {
            m_boost_A = m_boost_A || (m_params.boost_velocity_A[idir] != 0.0);
            m_boost_B = m_boost_B || (m_params.boost_velocity_B[idir] != 0.0);
        }
        m_boost_A = m_boost_A && (bA > 0.0);
        m_boost_B = m_boost_B && (bB > 0.0);

        // Exact boost (momentum_model = 1): each throat's speed, Lorentz
        // factor and direction from its velocity, and the half separation
        // that windows the companion's conformal weight.
        if (m_params.momentum_model == 1)
        {
            for (int body = 0; body < 2; ++body)
            {
                const auto &v = (body == 0) ? m_params.boost_v_A
                                            : m_params.boost_v_B;
                const double speed =
                    std::sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
                if (speed > 0.0)
                {
                    m_boost_speed[body] = speed;
                    m_boost_gamma[body] = 1.0 / std::sqrt(1.0 - speed * speed);
                    for (int d = 0; d < 3; ++d)
                    {
                        m_boost_dir[body][d] = v[d] / speed;
                    }
                }
            }
            double d2 = 0.0;
            for (int d = 0; d < 3; ++d)
            {
                const double dd = m_params.centerA[d] - m_params.centerB[d];
                d2 += dd * dd;
            }
            m_boost_window = (d2 > 0.0) ? 0.5 * std::sqrt(d2) : 1.0;
        }

        // Constraint-solve background: how far the chosen puncture
        // coefficients sit from the superposition's own (background 0 adds
        // shift / r per throat; background 1 uses the coefficients as they
        // are).  Zero unless a solve asked for a different c.
        if (m_params.solve_background == 0)
        {
            if (bA > 0.0)
            {
                m_solve_shift_A = m_params.solve_puncture_A -
                                  superposed_puncture_coefficient(m_params, 0);
            }
            if (bB > 0.0)
            {
                m_solve_shift_B = m_params.solve_puncture_B -
                                  superposed_puncture_coefficient(m_params, 1);
            }
        }

        // Precompute the four Helfer constants once on the host: they are
        // pure functions of the parameters, so the device kernel only pays
        // for the two windows.
        if (m_params.helfer_correction == 0 || bA <= 0.0 || bB <= 0.0)
        {
            return; // off, or only one body present - nothing to correct
        }

        double d2 = 0.0;
        for (int idir = 0; idir < AMREX_SPACEDIM; ++idir)
        {
            const double dd = m_params.centerA[idir] - m_params.centerB[idir];
            d2 += dd * dd;
        }
        if (d2 <= 0.0)
        {
            return; // coincident throats: there is no "companion's centre"
        }
        const double d = std::sqrt(d2);

        m_helfer_on = true;
        m_helfer_w  = (m_params.helfer_width > 0.0) ? m_params.helfer_width
                                                    : d / 3.0;

        // dpsi_A is what throat B adds to psi AT throat A's centre, etc.
        m_helfer_dpsi_A = std::sqrt(1.0 + bB * bB / (4.0 * d2)) - 1.0;
        m_helfer_dpsi_B = std::sqrt(1.0 + bA * bA / (4.0 * d2)) - 1.0;

        if (m_params.id_type == 1)
        {
            // The mass rides in u, so that is where its constant lives.
            if (m_params.drainhole_mass_B != 0.0)
            {
                m_helfer_du_A =
                    drainhole_u<double>(d, bB, m_params.drainhole_mass_B);
            }
            if (m_params.drainhole_mass_A != 0.0)
            {
                m_helfer_du_B =
                    drainhole_u<double>(d, bA, m_params.drainhole_mass_A);
            }
        }
        else
        {
            // id_type = 0 puts the mass in psi as a Brill-Lindquist puncture,
            // so the companion's m/(2r) tail is part of the same constant.
            m_helfer_dpsi_A += 0.5 * m_params.bare_mass_B / d;
            m_helfer_dpsi_B += 0.5 * m_params.bare_mass_A / d;
        }
    }

    //! A throat's boost from its ADM momentum P = gamma m v (momentum_model
    //! = 1): v = |P| / sqrt(m^2 + |P|^2), gamma = 1 / sqrt(1 - v^2) and the
    //! direction e = P / |P|.  At rest (or m <= 0, refused with P != 0 by
    //! SimulationParameters) v = 0, gamma = 1, e = 0.
    static void boost_kinematics(const double m,
                                 const std::array<double, AMREX_SPACEDIM> &P,
                                 double &v, double &gamma, double e[3])
    {
        const double p = std::sqrt(P[0] * P[0] + P[1] * P[1] + P[2] * P[2]);
        v              = 0.0;
        gamma          = 1.0;
        e[0] = e[1] = e[2] = 0.0;
        if (p > 0.0 && m > 0.0)
        {
            v     = p / std::sqrt(m * m + p * p);
            gamma = 1.0 / std::sqrt(1.0 - v * v);
            for (int d = 0; d < 3; ++d)
            {
                e[d] = P[d] / p;
            }
        }
    }

    //! The distance from throat Y's centre to throat X's, as Y's closed forms
    //! see it: in Y's rest frame under momentum_model = 1 (the boosted radius
    //! |d + (gamma - 1)(e.d) e|), the plain distance otherwise.
    static double companion_distance(const params_t &p, const int X)
    {
        const int Y       = 1 - X;
        const auto &cX    = (X == 0) ? p.centerA : p.centerB;
        const auto &cY    = (Y == 0) ? p.centerA : p.centerB;
        double d[3], d2   = 0.0;
        for (int idir = 0; idir < 3; ++idir)
        {
            d[idir] = cX[idir] - cY[idir];
            d2 += d[idir] * d[idir];
        }
        const auto &v = (Y == 0) ? p.boost_v_A : p.boost_v_B;
        const double speed2 = v[0] * v[0] + v[1] * v[1] + v[2] * v[2];
        if (p.momentum_model != 1 || speed2 <= 0.0)
        {
            return std::sqrt(d2);
        }
        const double speed = std::sqrt(speed2);
        const double g     = 1.0 / std::sqrt(1.0 - speed2);
        const double ed    = (v[0] * d[0] + v[1] * d[1] + v[2] * d[2]) / speed;
        double r2          = 0.0;
        for (int idir = 0; idir < 3; ++idir)
        {
            const double x = d[idir] + (g - 1.0) * ed * v[idir] / speed;
            r2 += x * x;
        }
        return std::sqrt(r2);
    }

    //! Puncture coefficient of the isolated drainhole: Psi -> c / r at its
    //! centre, c = (a/2) e^{pi m / 2a} (id_type 1; m = 0 gives a/2).
    static double isolated_puncture_coefficient(const double a,
                                                const double m)
    {
        return 0.5 * a * std::exp(0.5 * M_PI * m / a);
    }

    //! Puncture coefficient the superposition hands throat X (0 = A, 1 = B):
    //! the isolated value times e^{-u_Y(x_X)/2}, the companion's lapse
    //! exponent at this centre.  Every other term of Psi_0 is bounded there.
    static double superposed_puncture_coefficient(const params_t &p,
                                                  const int which)
    {
        const double a     = (which == 0) ? p.b0_A : p.b0_B;
        const double m     = (which == 0) ? p.drainhole_mass_A
                                          : p.drainhole_mass_B;
        const double a_Y   = (which == 0) ? p.b0_B : p.b0_A;
        const double m_Y   = (which == 0) ? p.drainhole_mass_B
                                          : p.drainhole_mass_A;
        double c           = isolated_puncture_coefficient(a, m);
        if (a_Y > 0.0 && m_Y != 0.0)
        {
            double d2 = 0.0;
            for (int idir = 0; idir < AMREX_SPACEDIM; ++idir)
            {
                const double dd = p.centerA[idir] - p.centerB[idir];
                d2 += dd * dd;
            }
            const double dist = (p.momentum_model == 1)
                                    ? companion_distance(p, which)
                                    : std::sqrt(d2);
            c *= std::exp(-0.5 * drainhole_u<double>(dist, a_Y, m_Y));
        }
        return c;
    }

    //! Amplitude C of the drainhole scalar phi = C atan X (id_type 1): the
    //! field equations fix 4 pi C^2 a^2 = a^2 + m^2.  Scale-free in (a, m).
    static double scalar_amplitude(const double a, const double m)
    {
        return std::sqrt(a * a + m * m) / (a * std::sqrt(4.0 * M_PI));
    }

    //! The isolated drainhole's far side (Psi -> c/r + d at its centre):
    //! ADM mass 2 c d = -m e^{pi m/a} and scalar charge 4 C c^2 / a =
    //! sqrt(a^2 + m^2) e^{pi m/a} / sqrt(4 pi).
    static double isolated_far_side_mass(const double a, const double m)
    {
        return -m * std::exp(M_PI * m / a);
    }
    static double isolated_far_side_charge(const double a, const double m)
    {
        return std::sqrt(a * a + m * m) * std::exp(M_PI * m / a) /
               std::sqrt(4.0 * M_PI);
    }

    //! Far-side scalar charge of throat X for a puncture coefficient c:
    //! near the centre phi = phi_0 + (4 C / a) r + (l = 1 terms), and the
    //! inversion r' = c^2 / r turns the r term into 4 C c^2 / (a r').
    static double far_side_charge(const params_t &p, const int which,
                                  const double c)
    {
        const double a = (which == 0) ? p.b0_A : p.b0_B;
        const double m = (which == 0) ? p.drainhole_mass_A : p.drainhole_mass_B;
        return 4.0 * scalar_amplitude(a, m) * c * c / a;
    }

    //! Regular part d of the solve's background at throat X's centre,
    //! Psi_bg -> c_X / r + d + O(r) (monopole; the companion's gradient adds
    //! only l = 1).  Background 0 with shift_Y = c_Y - c_superposed,Y:
    //!     d = e^{-u_Y(d_XY)/2} e^{pi m/2a} [ (sqrt(Omega_Y(d_XY)) - 1) - m/a ]
    //!         + shift_Y / d_XY,
    //! background 1: d = 1 + c_Y / d_XY.  A single throat has
    //! -(m/a) e^{pi m/2a}.  Checked against the closed form Psi_bg on spheres
    //! r -> 0 to 1e-8.
    static double background_regular_part(const params_t &p, const int which)
    {
        const double a   = (which == 0) ? p.b0_A : p.b0_B;
        const double m   = (which == 0) ? p.drainhole_mass_A
                                        : p.drainhole_mass_B;
        const double a_Y = (which == 0) ? p.b0_B : p.b0_A;
        const double m_Y = (which == 0) ? p.drainhole_mass_B
                                        : p.drainhole_mass_A;
        const double c_Y = (which == 0) ? p.solve_puncture_B
                                        : p.solve_puncture_A;
        double d2 = 0.0;
        for (int idir = 0; idir < AMREX_SPACEDIM; ++idir)
        {
            const double dd = p.centerA[idir] - p.centerB[idir];
            d2 += dd * dd;
        }
        if (p.momentum_model == 1)
        {
            // The companion's closed forms at its own rest-frame radius.
            const double rest = companion_distance(p, which);
            d2                = rest * rest;
        }
        const double dist = std::sqrt(d2);
        const bool has_Y  = (a_Y > 0.0) && (dist > 0.0);
        if (p.solve_background == 1)
        {
            return 1.0 + (has_Y ? c_Y / dist : 0.0);
        }
        double E_Y = 1.0, delta_Y = 0.0, shift_term = 0.0;
        if (has_Y)
        {
            if (m_Y != 0.0)
            {
                E_Y = std::exp(-0.5 * drainhole_u<double>(dist, a_Y, m_Y));
            }
            delta_Y = std::sqrt(1.0 + a_Y * a_Y / (4.0 * d2)) - 1.0;
            shift_term =
                (c_Y - superposed_puncture_coefficient(p, 1 - which)) / dist;
        }
        return E_Y * std::exp(0.5 * M_PI * m / a) * (delta_Y - m / a) +
               shift_term;
    }

    //! grad phi of the superposed scalar at a point given as an offset from
    //! grid_center (host; the same profiles compute() lays down, id_type 1).
    static void scalar_gradient(const params_t &p, const double x,
                                const double y, const double z, double g[3])
    {
        g[0] = g[1] = g[2] = 0.0;
        for (int body = 0; body < 2; ++body)
        {
            const double a = (body == 0) ? p.b0_A : p.b0_B;
            if (a <= 0.0)
            {
                continue;
            }
            const double m     = (body == 0) ? p.drainhole_mass_A
                                             : p.drainhole_mass_B;
            const auto &centre = (body == 0) ? p.centerA : p.centerB;
            const double sign  = (body == 0) ? 1.0 : p.phi_sign_B;
            const double dx    = x - centre[0];
            const double dy    = y - centre[1];
            const double dz    = z - centre[2];
            const double r2    = std::max(dx * dx + dy * dy + dz * dz, 1.0e-24);
            const double r     = std::sqrt(r2);
            const double q     = r2 + 0.25 * a * a;
            const double f     = sign * scalar_amplitude(a, m) * a / (q * r);
            g[0] += f * dx;
            g[1] += f * dy;
            g[2] += f * dz;
        }
    }

    //! Ahat_ij Ahat^ij of the summed Bowen-York terms at a point given as an
    //! offset from grid_center (host; flat indices, as the solve uses it).
    static double bowen_york_square(const params_t &p, const double x,
                                    const double y, const double z)
    {
        double A11 = 0.0, A12 = 0.0, A13 = 0.0;
        double A22 = 0.0, A23 = 0.0, A33 = 0.0;
        for (int body = 0; body < 2; ++body)
        {
            const double a = (body == 0) ? p.b0_A : p.b0_B;
            const auto &P  = (body == 0) ? p.momentumA : p.momentumB;
            if (a <= 0.0 || (P[0] == 0.0 && P[1] == 0.0 && P[2] == 0.0))
            {
                continue;
            }
            const auto &centre = (body == 0) ? p.centerA : p.centerB;
            const double dx    = x - centre[0];
            const double dy    = y - centre[1];
            const double dz    = z - centre[2];
            const double r2    = std::max(dx * dx + dy * dy + dz * dz, 1.0e-24);
            const double r     = std::sqrt(r2);
            add_bowen_york<double>(dx / r, dy / r, dz / r, r2, P[0], P[1],
                                   P[2], A11, A12, A13, A22, A23, A33);
        }
        return A11 * A11 + A22 * A22 + A33 * A33 +
               2.0 * (A12 * A12 + A13 * A13 + A23 * A23);
    }

    //! Everything the Hamiltonian-constraint solve needs at one cell (see the
    //! class comment): the background conformal factor Psi_bg, its flat
    //! Laplacian in closed form, V = pi s |grad phi|^2 and Ahat_ij Ahat^ij.
    //! Off the centres lap(1/r) = 0, so the puncture shift terms add to
    //! Psi_bg but not to its Laplacian.
    template <class data_t>
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
    constraint_background(int i, int j, int k, data_t &Psi_bg,
                          data_t &lap_Psi_bg, data_t &V, data_t &AA) const
    {
        Coordinates coords(amrex::IntVect(i, j, k), m_dx, m_params.grid_center);

        data_t U = 0.0, lap_U = 0.0, psi = 1.0, lap_psi = 0.0;
        data_t gU[3]   = {0.0, 0.0, 0.0};
        data_t gpsi[3] = {0.0, 0.0, 0.0};
        data_t gphi[3] = {0.0, 0.0, 0.0};
        data_t A11 = 0.0, A12 = 0.0, A13 = 0.0;
        data_t A22 = 0.0, A23 = 0.0, A33 = 0.0;
        data_t shift = 0.0;

        for (int body = 0; body < 2; ++body)
        {
            const double a = (body == 0) ? m_params.b0_A : m_params.b0_B;
            if (a <= 0.0)
            {
                continue;
            }
            const double m     = (body == 0) ? m_params.drainhole_mass_A
                                             : m_params.drainhole_mass_B;
            const auto &centre = (body == 0) ? m_params.centerA
                                             : m_params.centerB;
            const auto &P      = (body == 0) ? m_params.momentumA
                                             : m_params.momentumB;
            const double sign  = (body == 0) ? 1.0 : m_params.phi_sign_B;

            const data_t dx = coords.x - (data_t)centre[0];
            const data_t dy = coords.y - (data_t)centre[1];
            const data_t dz = coords.z - (data_t)centre[2];
            const data_t r2 =
                simd_max(dx * dx + dy * dy + dz * dz, (data_t)1.0e-24);
            const data_t r  = sqrt(r2);
            const data_t n[3] = {dx / r, dy / r, dz / r};

            // 1 + X^2 = (r Omega / a)^2 turns every derivative of atan X
            // into a rational function of q = r^2 + a^2/4 = r^2 Omega.
            const data_t q     = r2 + (data_t)(0.25 * a * a);
            const data_t u     = drainhole_u(r, a, m);
            const data_t du    = (data_t)m / q;
            const data_t ddu   = -2.0 * (data_t)m * r / (q * q);
            const data_t Om    = 1.0 + (data_t)(0.25 * a * a) / r2;
            const data_t s     = sqrt(Om);
            const data_t dOm   = -(data_t)(0.5 * a * a) / (r2 * r);
            const data_t ddOm  = (data_t)(1.5 * a * a) / (r2 * r2);
            const data_t ds    = dOm / (2.0 * s);
            const data_t dds   = ddOm / (2.0 * s) - dOm * dOm / (4.0 * s * s * s);
            const data_t dphi  = (data_t)(sign * phi_norm(a, m) * a) / q;

            U += u;
            lap_U += ddu + 2.0 * du / r;
            psi += s - 1.0;
            lap_psi += dds + 2.0 * ds / r;
            for (int d = 0; d < 3; ++d)
            {
                gU[d] += du * n[d];
                gpsi[d] += ds * n[d];
                gphi[d] += dphi * n[d];
            }

            if (P[0] != 0.0 || P[1] != 0.0 || P[2] != 0.0)
            {
                add_bowen_york(n[0], n[1], n[2], r2, P[0], P[1], P[2], A11,
                               A12, A13, A22, A23, A33);
            }

            const double c = (body == 0) ? m_params.solve_puncture_A
                                         : m_params.solve_puncture_B;
            shift += (m_params.solve_background == 0)
                         ? (data_t)((body == 0) ? m_solve_shift_A
                                                : m_solve_shift_B) / r
                         : (data_t)c / r;
        }

        if (m_params.solve_background == 0)
        {
            // Psi_0 = E psi, E = e^{-U/2}:
            // lap Psi_0 = E [psi (|grad U|^2/4 - lap U/2) - grad U.grad psi
            //                + lap psi].
            const data_t E    = exp(-0.5 * U);
            const data_t gU2  = gU[0] * gU[0] + gU[1] * gU[1] + gU[2] * gU[2];
            const data_t gUgp =
                gU[0] * gpsi[0] + gU[1] * gpsi[1] + gU[2] * gpsi[2];
            Psi_bg     = E * psi + shift;
            lap_Psi_bg = E * (psi * (0.25 * gU2 - 0.5 * lap_U) - gUgp + lap_psi);
        }
        else
        {
            Psi_bg     = 1.0 + shift;
            lap_Psi_bg = 0.0;
        }

        V = (data_t)(M_PI * m_params.support_strength) *
            (gphi[0] * gphi[0] + gphi[1] * gphi[1] + gphi[2] * gphi[2]);
        AA = A11 * A11 + A22 * A22 + A33 * A33 +
             2.0 * (A12 * A12 + A13 * A13 + A23 * A23);
    }

    //! The analytic data, or with solved = true the constraint-solved data:
    //! chi = (Psi_bg + w)^{-4} with w the solve's correction at this cell.
    //! solved = false is the archived code path, bit for bit.
    template <class data_t>
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
    compute(int i, int j, int k, amrex::Array4<data_t> cell,
            const bool solved = false, const data_t w = 0.0,
            const data_t *LW = nullptr) const
    {
        if (m_params.momentum_model == 1)
        {
            compute_boosted(i, j, k, cell, solved, w, LW);
            return;
        }

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

        // u_sum is the drainhole static-lapse exponent and it is what carries
        // the ADM mass under id_type = 1: chi = e^{2 u_sum} psi^{-4} and
        // alpha = e^{u_sum}.  Under id_type = 0 it stays identically zero, so
        // exp(2 u_sum) is exactly 1.0 and every archived run reproduces bit for
        // bit; the bare-mass puncture is added to psi instead, which is what
        // drove chi -> 0 at the throat.
        data_t u_sum = 0.0;
        if (m_params.id_type == 1)
        {
            if (bA > 0.0 && m_params.drainhole_mass_A != 0.0)
            {
                u_sum += drainhole_u(rA, bA, m_params.drainhole_mass_A);
            }
            if (bB > 0.0 && m_params.drainhole_mass_B != 0.0)
            {
                u_sum += drainhole_u(rB, bB, m_params.drainhole_mass_B);
            }
        }
        else
        {
            psi += (data_t)(0.5 * m_params.bare_mass_A) / rA +
                   (data_t)(0.5 * m_params.bare_mass_B) / rB;
        }

        // ---- Helfer/Ning one-body correction --------------------------------
        // Hand each throat back the constants the companion left at its
        // centre, windowed so spatial infinity never sees the subtraction.
        // See the class comment for why this is Helfer Eq. 45 and why the
        // window is needed.  m_helfer_on is false unless BOTH throats are
        // present and the correction was asked for, so the single-throat
        // regression mode and every archived run are untouched.
        if (m_helfer_on)
        {
            const data_t WA = helfer_window(rA);
            const data_t WB = helfer_window(rB);
            psi -= WA * (data_t)m_helfer_dpsi_A + WB * (data_t)m_helfer_dpsi_B;
            u_sum -= WA * (data_t)m_helfer_du_A + WB * (data_t)m_helfer_du_B;
        }

        // ---- Declared perturbation seed ------------------------------------
        // psi -> psi (1 + eps g(r)), g a unit Gaussian shell on the minimal
        // surface, so the throat's areal radius R = r psi^2 e^{-u} moves by
        // ~2 eps with the sign of eps.  The branch is skipped at eps = 0, so
        // every archived run reproduces bit for bit.
        if (bA > 0.0 && m_params.seed_amplitude_A != 0.0)
        {
            psi *= 1.0 + (data_t)m_params.seed_amplitude_A *
                             seed_shell(rA, bA, m_params.drainhole_mass_A,
                                        m_params.seed_width_A);
        }
        if (bB > 0.0 && m_params.seed_amplitude_B != 0.0)
        {
            psi *= 1.0 + (data_t)m_params.seed_amplitude_B *
                             seed_shell(rB, bB, m_params.drainhole_mass_B,
                                        m_params.seed_width_B);
        }

        // ---- Declared quadrupolar seed -------------------------------------
        // The spherical seed above cannot radiate: for a spherical throat and a
        // spherical kick every l >= 2 mode of Psi4 vanishes, black hole or not.
        // This lays the same shell with an l = 2, m = 0 profile about the z
        // axis through the throat,
        //     psi -> psi (1 + eps2 g(r) P2),   P2 = (3 z^2/r^2 - 1)/2,
        // which gives the throat a quadrupole to shed.  It has no spherical
        // part, so on its own it does not choose the collapse or inflation
        // branch -- pair it with the spherical seed for that.  It is a second
        // factor rather than a term inside the first so that eps2 = 0 skips the
        // branch and every existing run reproduces bit for bit; with both on the
        // cross term is O(eps eps2).  K_ij and Pi are untouched, so the momentum
        // constraint stays exact.
        if (bA > 0.0 && m_params.seed_l2_amplitude_A != 0.0)
        {
            const data_t P2A = 1.5 * dzA * dzA / rA2_reg - 0.5;
            psi *= 1.0 + (data_t)m_params.seed_l2_amplitude_A * P2A *
                             seed_shell(rA, bA, m_params.drainhole_mass_A,
                                        m_params.seed_width_A);
        }
        if (bB > 0.0 && m_params.seed_l2_amplitude_B != 0.0)
        {
            const data_t P2B = 1.5 * dzB * dzB / rB2_reg - 0.5;
            psi *= 1.0 + (data_t)m_params.seed_l2_amplitude_B * P2B *
                             seed_shell(rB, bB, m_params.drainhole_mass_B,
                                        m_params.seed_width_B);
        }

        data_t chi;
        if (solved)
        {
            // The same Psi_bg the solve used (seeds and the Helfer
            // correction are refused with the solve, so it is Psi_0 plus
            // the puncture shifts), plus the solve's correction.
            data_t Psi_bg, lap_Psi_bg, V, AA;
            constraint_background(i, j, k, Psi_bg, lap_Psi_bg, V, AA);
            const data_t Psi  = Psi_bg + w;
            const data_t Psi2 = Psi * Psi;
            chi               = 1.0 / (Psi2 * Psi2);
        }
        else
        {
            const data_t psi2 = psi * psi;
            chi               = exp(2.0 * u_sum) / (psi2 * psi2);
        }
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
        // The amplitude is 1/sqrt(4 pi) for a massless throat and
        // sqrt(a^2+m^2)/(a sqrt(4 pi)) for the drainhole - the field-equation
        // constraint 4 pi C^2 = a^2 + m^2 that makes the closed form an exact
        // solution rather than an ansatz.  It reduces to the first at m = 0.
        data_t phi           = 0.0;
        double phi_asymptote = 0.0;
        // v . grad phi summed over boosted throats; turned into Pi once the
        // lapse is known (below).  Stays exactly 0 with the boost off.
        data_t v_dot_grad_phi = 0.0;
        if (bA > 0.0)
        {
            const double normA = phi_norm(bA, m_params.drainhole_mass_A);
            const data_t argA = (rA - (data_t)bA_sq / (4.0 * rA)) / (data_t)bA;
            phi += (data_t)normA * atan(argA);
            phi_asymptote += normA * (M_PI / 2.0);
            if (m_boost_A)
            {
                v_dot_grad_phi += boost_term(
                    normA, argA, bA, bA_sq, rA, dxA, dyA, dzA,
                    m_params.boost_velocity_A[0], m_params.boost_velocity_A[1],
                    m_params.boost_velocity_A[2]);
            }
        }
        if (bB > 0.0)
        {
            // phi_sign_B multiplies the whole profile INCLUDING its
            // asymptote, so with opposite equal throats the two pi/2 tails
            // cancel and phi -> 0 at infinity on its own.  The constraint
            // sees only (grad phi)^2 per body; the cross term changes at
            // the same O(m/d) as the superposition error already present.
            const double normB = m_params.phi_sign_B *
                                 phi_norm(bB, m_params.drainhole_mass_B);
            const data_t argB = (rB - (data_t)bB_sq / (4.0 * rB)) / (data_t)bB;
            phi += (data_t)normB * atan(argB);
            phi_asymptote += normB * (M_PI / 2.0);
            if (m_boost_B)
            {
                v_dot_grad_phi += boost_term(
                    normB, argB, bB, bB_sq, rB, dxB, dyB, dzB,
                    m_params.boost_velocity_B[0], m_params.boost_velocity_B[1],
                    m_params.boost_velocity_B[2]);
            }
        }

        if (m_params.subtract_phi_asymptote != 0)
        {
            // Each atan -> +pi/2 as r -> infinity.
            phi -= (data_t)phi_asymptote;
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
        // constraint exactly.  Overwritten below, after the lapse, when a
        // boost is on.
        data_t Pi = 0.0;

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
            // alpha = prod_c [1 - exp(-(r_c / f b_c)^p)] freezes each origin
            // (alpha -> 0 as r_c -> 0) while a steep enough ramp leaves
            // alpha = 1 at the throat: with the defaults f = 0.3, p = 8 the
            // exponent at r = b/2 is (1/0.6)^8 ~ 60, and exp(-60) is below
            // double precision.  That is what makes this preferable to
            // alpha = sqrt(chi), which suppresses the lapse everywhere
            // chi < 1 -- including at the throat, i.e. exactly where the
            // dynamics under study lives.
            //
            // f and p are tunable because the sharpness that protects the
            // throat is also what makes the collar hard to resolve, and the
            // two requirements pull against each other.  With f = 0.3, p = 8
            // on a b = 0.5 throat, alpha climbs from 0.1 to 0.9 across
            // r in [0.113, 0.167] -- a collar 0.054 wide.  At max_level = 3
            // (dx = 0.0625) that entire transition fits inside ONE cell: the
            // 4th-order stencil sees a step function, and the run NaNs at
            // t ~ 0.2 with K blowing up at the origin.  max_level = 4
            // (dx = 0.03125) gives 1.7 cells and survives to t ~ 2.4.  So the
            // collar, not the depth, is what sets the usable resolution, and
            // coarsening to escape the origin makes things strictly worse.
            //
            // To widen it, lower BOTH f and p: the collar width scales with
            // f, and p controls how abruptly it opens.  Widening is not
            // automatically a trade, because "alpha = 1 at the throat" is a
            // threshold and not a gradient -- once exp(-(b/2f b)^p) is under
            // double precision, making the ramp gentler costs nothing at all.
            // For b = 0.5:
            //
            //   f     p    collar        width   cells@ml4   1 - alpha(throat)
            //   0.3   8    [0.113,0.167] 0.053   1.7         0          <- default
            //   0.2   4    [0.057,0.123] 0.066   2.1         0
            //   0.15  2    [0.024,0.114] 0.090   2.9         1.5e-5
            //
            // f = 0.2, p = 4 is therefore free: 25% more collar for exactly
            // the same untouched throat.  f = 0.15, p = 2 buys another 40%
            // and does cost 1.5e-5 of lapse at the throat -- still three
            // orders of magnitude below the constraint violation the
            // superposed initial data already carries, so it is worth
            // reaching for if the collar is still the binding constraint.
            //
            // A binary needs the product: each throat carries its own
            // compactified origin and neither can be put on a symmetry
            // boundary, which is how the single-throat example avoided this.
            lapse = collar_factor(rA, rB);
        }
        else if (m_params.initial_lapse_type == 5 ||
                 m_params.initial_lapse_type == 6)
        {
            // Type 5: the drainhole's OWN exact static lapse, alpha = e^{u_sum}.
            // This is not a gauge preference, it is part of the solution: the
            // massive drainhole is static only with this lapse, and it is the
            // reason chi can stay O(1) at the throat while the object still has
            // ADM mass.  It tends to 1 at infinity, so 1+log slicing leaves it
            // alone until the geometry actually moves.  Under id_type = 0
            // u_sum is zero and this is just alpha = 1, i.e. type 0.
            //
            // Type 6: the same thing multiplied by the type-4 collar, for AMR.
            // chi still vanishes like r^4 at each compactified origin - that
            // is intrinsic to holding a wormhole in one Cartesian box, not a
            // defect of this branch - so deep refinement still needs the origin
            // frozen.  What HAS changed is that the collar no longer has to
            // fight the throat for room: the region with chi < 0.01 now sits
            // well inside the minimal surface (0.98 against a throat at 2.69
            // for a = 4, m = 1.2), so a collar sized to the throat scale
            // freezes only what is genuinely unresolvable.
            lapse = exp(u_sum);
            if (m_params.initial_lapse_type == 6)
            {
                lapse *= collar_factor(rA, rB);
            }
        }
        if (lapse < (data_t)1.0e-10)
            lapse = (data_t)1.0e-10;

        // ---- Boosted scalar (V2 only): Pi = -(v . grad phi) / alpha -------
        if (m_boost_A || m_boost_B)
        {
            Pi = -v_dot_grad_phi / lapse;
        }

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

    //! One point's exact-boost background (momentum_model = 1; see "EXACT
    //! BOOST" in the class comment).  Psi is the superposed conformal factor
    //! with the solve's puncture shifts (rest-frame radii), G = delta + E
    //! carries both throats' anisotropies, and each throat's K_ij and Pi
    //! enter with the companion's conformal weight: near throat X the
    //! superposition is Psi = F Psi_X with F smooth, a uniform rescaling of
    //! X's lengths by F^2, under which the exact data take K_ij -> F^2 K_ij
    //! and Pi -> Pi / F^2 (both constraints then scale uniformly).  The weight
    //! is 1 + W_X [(Psi / Psi_X)^2 - 1], with the window W_X = exp[-(r_X /
    //! (d/2))^4] keeping it bounded at the companion's puncture; one throat
    //! has weight 1.  In a pair each throat's E, K_ij and Pi are also cut
    //! inside the companion Y by 1 - exp[-(r_Y / (0.3 a_Y))^8] (the collar's
    //! profile; d E carries the cut's gradient), so Y's far side holds Y
    //! alone.  Uncut, the companion's Pi and K reach Y's compactified
    //! infinity, where the constraints weight them by Psi^5 and Psi^6
    //! (pi s Pi^2 Psi^5 ~ r_Y^-5, Psi^6 Pi d phi ~ r_Y^-6).  The cut is 1 to
    //! 5e-5 beyond 0.4 a_Y, far inside the throat (r ~ 0.8 a).  Positions
    //! are offsets from grid_center.
    template <class data_t> struct BoostBackground
    {
        data_t Psi{1.0};
        data_t E[3][3]{};
        data_t dE[3][3][3]{}; //!< dE[c][p][s] = d_c E_ps, closed form
        data_t K[3][3]{};     //!< physical K_ij
        data_t phi{0.0};
        data_t Pi{0.0};
        data_t lapse{1.0};    //!< the throats' boosted lapses, multiplied
        data_t shift[3]{};    //!< the throats' boosted shifts, summed
        data_t r_rest[2]{1.0e30, 1.0e30};
    };

    template <class data_t>
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
    // NOLINTNEXTLINE(readability-function-cognitive-complexity)
    boost_background(const data_t pos[3], BoostBackground<data_t> &b) const
    {
        data_t U = 0.0, psi = 1.0, punct = 0.0;
        double phi_asymptote = 0.0;
        data_t PsiX[2]      = {1.0, 1.0};
        data_t KX[2][3][3]  = {};
        data_t PiX[2]       = {0.0, 0.0};
        data_t epsX[2]      = {0.0, 0.0}; //!< anisotropy eps and d eps / dr
        data_t epsrX[2]     = {0.0, 0.0};
        data_t ntX[2][3]    = {};         //!< gradient of the rest-frame radius
        bool present[2]     = {false, false};

        for (int body = 0; body < 2; ++body)
        {
            const double a = (body == 0) ? m_params.b0_A : m_params.b0_B;
            if (a <= 0.0)
            {
                continue;
            }
            present[body]      = true;
            const double m     = (body == 0) ? m_params.drainhole_mass_A
                                             : m_params.drainhole_mass_B;
            const auto &centre = (body == 0) ? m_params.centerA
                                             : m_params.centerB;
            const double C =
                ((body == 0) ? 1.0 : m_params.phi_sign_B) * phi_norm(a, m);
            const double v  = m_boost_speed[body];
            const double g  = m_boost_gamma[body];
            const double *e = m_boost_dir[body];

            // The rest-frame point this lab point is, and its radius.
            data_t d[3];
            for (int c = 0; c < 3; ++c)
            {
                d[c] = pos[c] - (data_t)centre[c];
            }
            const data_t ed = (data_t)e[0] * d[0] + (data_t)e[1] * d[1] +
                              (data_t)e[2] * d[2];
            data_t xr[3];
            for (int c = 0; c < 3; ++c)
            {
                xr[c] = d[c] + (data_t)(g - 1.0) * ed * (data_t)e[c];
            }
            const data_t r2 = simd_max(
                xr[0] * xr[0] + xr[1] * xr[1] + xr[2] * xr[2], (data_t)1.0e-24);
            const data_t r  = sqrt(r2);
            b.r_rest[body]  = r;

            // The static throat there (the same closed forms as compute()).
            const data_t X  = (r - (data_t)(0.25 * a * a) / r) / (data_t)a;
            const data_t u  = drainhole_u(r, a, m);
            const data_t Om = 1.0 + (data_t)(0.25 * a * a) / r2;
            U += u;
            psi += sqrt(Om) - 1.0;
            PsiX[body] = exp(-0.5 * u) * sqrt(Om);
            b.phi += (data_t)C * atan(X);
            phi_asymptote += C * (M_PI / 2.0);
            punct += (data_t)((body == 0) ? m_solve_shift_A : m_solve_shift_B) /
                     r;

            // n = xr / r, and nt = d r / d x (lab), which the companion cut
            // below needs for a throat at rest too (g = 1: nt = n).
            data_t n[3], nt[3];
            for (int c = 0; c < 3; ++c)
            {
                n[c] = xr[c] / r;
            }
            const data_t en = (data_t)e[0] * n[0] + (data_t)e[1] * n[1] +
                              (data_t)e[2] * n[2];
            for (int c = 0; c < 3; ++c)
            {
                nt[c]        = n[c] + (data_t)(g - 1.0) * en * (data_t)e[c];
                ntX[body][c] = nt[c];
            }
            if (v <= 0.0)
            {
                b.lapse *= exp(u); // at rest: its own static lapse, K = Pi = 0
                continue;
            }

            // u' = m/q, Q = e^{-2u} Omega^2 = Psi_X^4.
            const data_t q    = r2 + (data_t)(0.25 * a * a);
            const data_t ur   = (data_t)m / q;
            const data_t Omr  = -(data_t)(0.5 * a * a) / (r2 * r);
            const data_t QrQ  = -2.0 * ur + 2.0 * Omr / Om; // Q'/Q
            const data_t iQ   = exp(2.0 * u) / (Om * Om);  // 1/Q
            const data_t alQ  = exp(2.0 * u) * iQ;         // alpha^2/Q
            const data_t g2v2 = (data_t)(g * g * v * v);
            const data_t eps  = g2v2 * (1.0 - alQ);
            const data_t epsr = -g2v2 * alQ * (2.0 * ur - QrQ); // eps'
            const data_t den  = 1.0 - (data_t)(v * v) * alQ;
            const data_t N    = exp(u) / sqrt(den);
            const data_t phir = (data_t)(C * a) / q; // phi'

            const data_t c1 = (data_t)g * (ur - 0.5 * QrQ);
            const data_t c2 = 0.5 * QrQ * en;
            const data_t c3 = en * g2v2 * (0.5 * QrQ - alQ * ur);
            epsX[body]      = eps;
            epsrX[body]     = epsr;
            for (int p = 0; p < 3; ++p)
            {
                for (int s = 0; s < 3; ++s)
                {
                    const data_t ee = (data_t)(e[p] * e[s]);
                    KX[body][p][s] = N * (data_t)v *
                                     (c1 * ((data_t)e[p] * nt[s] +
                                            (data_t)e[s] * nt[p]) +
                                      ((p == s) ? c2 : (data_t)0.0) + c3 * ee);
                }
            }
            PiX[body] = -N * (data_t)v * iQ * phir * en;
            b.lapse *= N / (data_t)g;
            for (int c = 0; c < 3; ++c)
            {
                b.shift[c] += (data_t)v * (alQ - 1.0) / den * (data_t)e[c];
            }
        }

        if (m_params.subtract_phi_asymptote != 0)
        {
            b.phi -= (data_t)phi_asymptote;
        }
        b.Psi = exp(-0.5 * U) * psi + punct;

        // Each throat's anisotropy, K_ij and Pi enter cut inside its
        // companion Y by the collar profile 1 - exp[-(r_Y / (0.3 a_Y))^8], so
        // Y's far side holds Y alone (see BoostBackground).
        const bool pair = present[0] && present[1];
        for (int body = 0; body < 2; ++body)
        {
            if (!present[body])
            {
                continue;
            }
            const int other = 1 - body;
            data_t weight = 1.0, cut = 1.0, dcut = 0.0;
            if (pair)
            {
                const data_t ratio = b.Psi / PsiX[body];
                const data_t s     = b.r_rest[body] / (data_t)m_boost_window;
                const data_t s2    = s * s;
                weight = 1.0 + exp(-s2 * s2) * (ratio * ratio - 1.0);

                const data_t rc =
                    (data_t)(m_boost_cut_fraction *
                             ((other == 0) ? m_params.b0_A : m_params.b0_B));
                const data_t q  = b.r_rest[other] / rc;
                const data_t q2 = q * q;
                const data_t q4 = q2 * q2;
                const data_t ex = exp(-q4 * q4);
                cut             = 1.0 - ex;
                dcut            = 8.0 * q4 * q2 * q * ex / rc; // d cut / d r_Y
            }
            const double *e = m_boost_dir[body];
            for (int p = 0; p < 3; ++p)
            {
                for (int s = 0; s < 3; ++s)
                {
                    const data_t ee = (data_t)(e[p] * e[s]);
                    b.E[p][s] += cut * epsX[body] * ee;
                    for (int c = 0; c < 3; ++c)
                    {
                        b.dE[c][p][s] += cut * epsrX[body] * ntX[body][c] * ee;
                        if (pair)
                        {
                            b.dE[c][p][s] +=
                                dcut * epsX[body] * ee * ntX[other][c];
                        }
                    }
                    b.K[p][s] += cut * weight * KX[body][p][s];
                }
            }
            b.Pi += cut * PiX[body] / weight;
        }
    }

    //! The conformal side of a boost background: G = delta + E, its
    //! inverse and determinant, the trace K = Psi^-4 G^ij K_ij and
    //! Ahat^ij = Psi^2 [G^ik G^jl K_kl - G^ij (G^kl K_kl) / 3] (Psi^10 A^ij,
    //! traceless with G).
    template <class data_t>
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE static void
    boost_conformal(const BoostBackground<data_t> &b, data_t G[3][3],
                    data_t Gi[3][3], data_t &det, data_t &trK,
                    data_t Ahat[3][3])
    {
        for (int p = 0; p < 3; ++p)
        {
            for (int s = 0; s < 3; ++s)
            {
                G[p][s] = b.E[p][s] + ((p == s) ? (data_t)1.0 : (data_t)0.0);
            }
        }
        det = G[0][0] * (G[1][1] * G[2][2] - G[1][2] * G[1][2]) -
              G[0][1] * (G[0][1] * G[2][2] - G[1][2] * G[0][2]) +
              G[0][2] * (G[0][1] * G[1][2] - G[1][1] * G[0][2]);
        Gi[0][0] = (G[1][1] * G[2][2] - G[1][2] * G[1][2]) / det;
        Gi[0][1] = (G[0][2] * G[1][2] - G[0][1] * G[2][2]) / det;
        Gi[0][2] = (G[0][1] * G[1][2] - G[0][2] * G[1][1]) / det;
        Gi[1][1] = (G[0][0] * G[2][2] - G[0][2] * G[0][2]) / det;
        Gi[1][2] = (G[0][1] * G[0][2] - G[0][0] * G[1][2]) / det;
        Gi[2][2] = (G[0][0] * G[1][1] - G[0][1] * G[0][1]) / det;
        Gi[1][0] = Gi[0][1];
        Gi[2][0] = Gi[0][2];
        Gi[2][1] = Gi[1][2];
        data_t GK = 0.0; // G^kl K_kl = Psi^4 K
        for (int p = 0; p < 3; ++p)
        {
            for (int s = 0; s < 3; ++s)
            {
                GK += Gi[p][s] * b.K[p][s];
            }
        }
        const data_t Psi2 = b.Psi * b.Psi;
        trK               = GK / (Psi2 * Psi2);
        for (int i = 0; i < 3; ++i)
        {
            for (int j = 0; j < 3; ++j)
            {
                data_t GKG = 0.0;
                for (int k = 0; k < 3; ++k)
                {
                    for (int l = 0; l < 3; ++l)
                    {
                        GKG += Gi[i][k] * Gi[j][l] * b.K[k][l];
                    }
                }
                Ahat[i][j] = Psi2 * (GKG - Gi[i][j] * GK / 3.0);
            }
        }
    }

    //! momentum_model = 1: the exact-boost data in the CCZ4 variables
    //! (Gamma^i included: h_ij is not flat).  With solved = true the solve's
    //! corrections enter as Psi = Psi_bg + w and Ahat^ij = Ahat_bg^ij +
    //! (L W)^ij (LW: its six components 11 12 13 22 23 33), with K, G, phi,
    //! Pi and the gauge held at the background's.  A throat at rest gets the
    //! static drainhole, exactly as in compute().
    template <class data_t>
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
    // NOLINTNEXTLINE(readability-function-cognitive-complexity)
    compute_boosted(int i, int j, int k, amrex::Array4<data_t> cell,
                    const bool solved = false, const data_t w = 0.0,
                    const data_t *LW = nullptr) const
    {
        Coordinates coords(amrex::IntVect(i, j, k), m_dx,
                           m_params.grid_center);
        const data_t pos[3] = {coords.x, coords.y, coords.z};
        BoostBackground<data_t> b;
        boost_background(pos, b);

        data_t G[3][3], Gi[3][3], Ahat[3][3], det, trK;
        boost_conformal(b, G, Gi, det, trK, Ahat);
        data_t Psi = b.Psi;
        if (solved)
        {
            Psi += w;
            if (LW != nullptr)
            {
                const int map[3][3] = {{0, 1, 2}, {1, 3, 4}, {2, 4, 5}};
                for (int p = 0; p < 3; ++p)
                {
                    for (int s = 0; s < 3; ++s)
                    {
                        Ahat[p][s] += LW[map[p][s]];
                    }
                }
            }
        }
        const data_t Psi2 = Psi * Psi;
        const data_t Psi4 = Psi2 * Psi2;
        const data_t D13  = cbrt(det);

        // CCZ4: chi = det(gamma)^{-1/3} = Psi^-4 det(G)^{-1/3}, h = G / det^{1/3},
        // A_ij = chi (K_ij - gamma_ij K / 3) = Psi^-6 det^{-1/3} G_ik G_jl Ahat^kl.
        data_t chi = 1.0 / (Psi4 * D13);
        if (chi < (data_t)1.0e-10)
            chi = (data_t)1.0e-10;
        data_t h[3][3], hU[3][3], A[3][3];
        for (int p = 0; p < 3; ++p)
        {
            for (int s = 0; s < 3; ++s)
            {
                h[p][s]  = G[p][s] / D13;
                hU[p][s] = Gi[p][s] * D13;
                data_t GGA = 0.0;
                for (int kk = 0; kk < 3; ++kk)
                {
                    for (int l = 0; l < 3; ++l)
                    {
                        GGA += G[p][kk] * G[s][l] * Ahat[kk][l];
                    }
                }
                A[p][s] = GGA / (Psi4 * Psi2 * D13);
            }
        }

        // Gamma^i = h^ij h^kl Gamma_jkl, from the closed-form d_c h_ps =
        // (d_c E_ps - G_ps d_c ln det / 3) / det^{1/3}.
        data_t dh[3][3][3];
        for (int c = 0; c < 3; ++c)
        {
            data_t dlnD = 0.0;
            for (int p = 0; p < 3; ++p)
            {
                for (int s = 0; s < 3; ++s)
                {
                    dlnD += Gi[p][s] * b.dE[c][p][s];
                }
            }
            for (int p = 0; p < 3; ++p)
            {
                for (int s = 0; s < 3; ++s)
                {
                    dh[c][p][s] = (b.dE[c][p][s] - G[p][s] * dlnD / 3.0) / D13;
                }
            }
        }
        data_t Gamma[3] = {0.0, 0.0, 0.0};
        for (int l = 0; l < 3; ++l)
        {
            data_t contracted = 0.0; // h^jk Gamma_ljk
            for (int jj = 0; jj < 3; ++jj)
            {
                for (int kk = 0; kk < 3; ++kk)
                {
                    contracted +=
                        hU[jj][kk] * 0.5 *
                        (dh[jj][l][kk] + dh[kk][l][jj] - dh[l][jj][kk]);
                }
            }
            for (int ii = 0; ii < 3; ++ii)
            {
                Gamma[ii] += hU[ii][l] * contracted;
            }
        }

        // Gauge: the product of the throats' boosted lapses (types 5 and 6;
        // 6 adds the collar on each rest-frame radius) and the sum of their
        // shifts, or no shift.
        data_t lapse = b.lapse;
        if (m_params.initial_lapse_type == 6)
        {
            lapse *= collar_factor(b.r_rest[0], b.r_rest[1]);
        }
        if (lapse < (data_t)1.0e-10)
            lapse = (data_t)1.0e-10;
        data_t shift[3] = {b.shift[0], b.shift[1], b.shift[2]};
        if (m_params.boost_initial_shift == 0)
        {
            shift[0] = shift[1] = shift[2] = 0.0;
        }

        cell(i, j, k, c_chi) = chi;
        cell(i, j, k, c_h11) = h[0][0];
        cell(i, j, k, c_h12) = h[0][1];
        cell(i, j, k, c_h13) = h[0][2];
        cell(i, j, k, c_h22) = h[1][1];
        cell(i, j, k, c_h23) = h[1][2];
        cell(i, j, k, c_h33) = h[2][2];

        cell(i, j, k, c_K)   = trK;
        cell(i, j, k, c_A11) = A[0][0];
        cell(i, j, k, c_A12) = A[0][1];
        cell(i, j, k, c_A13) = A[0][2];
        cell(i, j, k, c_A22) = A[1][1];
        cell(i, j, k, c_A23) = A[1][2];
        cell(i, j, k, c_A33) = A[2][2];

        cell(i, j, k, c_Theta)  = 0.0;
        cell(i, j, k, c_Gamma1) = Gamma[0];
        cell(i, j, k, c_Gamma2) = Gamma[1];
        cell(i, j, k, c_Gamma3) = Gamma[2];

        cell(i, j, k, c_lapse)  = lapse;
        cell(i, j, k, c_shift1) = shift[0];
        cell(i, j, k, c_shift2) = shift[1];
        cell(i, j, k, c_shift3) = shift[2];
        cell(i, j, k, c_B1)     = 0.0;
        cell(i, j, k, c_B2)     = 0.0;
        cell(i, j, k, c_B3)     = 0.0;

        cell(i, j, k, c_phi) = b.phi;
        cell(i, j, k, c_Pi)  = b.Pi;
    }

  protected:
    //! Static lapse exponent of one drainhole,
    //!     u = (m/a) [ atan X - pi/2 ],   X = (r - a^2/(4 r)) / a,
    //! which tends to 0 at infinity (so the ADM masses of several throats add)
    //! and to -pi m / a at the compactified far infinity r -> 0.
    template <class data_t>
    AMREX_GPU_HOST_DEVICE AMREX_FORCE_INLINE static data_t
    drainhole_u(const data_t r, const double a, const double m)
    {
        const data_t X = (r - (data_t)(a * a) / (4.0 * r)) / (data_t)a;
        return (data_t)(m / a) * (atan(X) - (data_t)(M_PI / 2.0));
    }

    //! Amplitude of the phantom profile phi = C atan X.  The field equations
    //! fix 4 pi C^2 = a^2 + m^2, so C = sqrt(a^2+m^2)/(a sqrt(4 pi)) once the
    //! argument is written as X = l/a.  m = 0 gives the familiar 1/sqrt(4 pi).
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE double phi_norm(const double a,
                                                        const double m) const
    {
        const double amp =
            (m_params.id_type == 1) ? sqrt(a * a + m * m) / a : 1.0;
        return amp / sqrt(4.0 * M_PI);
    }

    //! Unit Gaussian shell on one throat's minimal surface, for the
    //! perturbation dial.  The minimal surface of the massive drainhole sits
    //! at l = m, i.e. r_t = (m + sqrt(m^2 + a^2))/2 (a/2 for the massless
    //! throat and for id_type = 0).  Width 0 = a/4: 8 cells at the production
    //! dx, and 3e-5 of the shell left at the compactified origin.
    template <class data_t>
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE data_t
    seed_shell(const data_t r, const double a, const double m,
               const double w_in) const
    {
        const double mm  = (m_params.id_type == 1) ? m : 0.0;
        const double r_t = 0.5 * (mm + sqrt(mm * mm + a * a));
        const double w   = (w_in > 0.0) ? w_in : 0.25 * a;
        const data_t s   = (r - (data_t)r_t) / (data_t)w;
        return exp(-s * s);
    }

    //! Correction window W(r) = exp[-(r/w)^p], centred on one throat: unity
    //! across the body it repairs, zero at the companion and at infinity.
    template <class data_t>
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE data_t
    helfer_window(const data_t r) const
    {
        return exp(-pow(r / (data_t)m_helfer_w, (data_t)m_params.helfer_power));
    }

    //! Origin-isolating collar, one factor per object: see lapse type 4 above
    //! for why it exists and how f and p trade collar width against the lapse
    //! left at the throat.  Shared by types 4 and 6.
    template <class data_t>
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE data_t collar_factor(const data_t rA,
                                                             const data_t rB) const
    {
        data_t factor = 1.0;
        if (m_params.b0_A > 0.0 || m_params.bare_mass_A > 0.0)
        {
            const data_t core_A =
                (data_t)(m_params.lapse_core_fraction *
                         (m_params.b0_A > 0.0 ? m_params.b0_A
                                              : m_params.bare_mass_A));
            const data_t s = rA / core_A;
            factor *= 1.0 - exp(-pow(s, (data_t)m_params.lapse_core_power));
        }
        if (m_params.b0_B > 0.0 || m_params.bare_mass_B > 0.0)
        {
            const data_t core_B =
                (data_t)(m_params.lapse_core_fraction *
                         (m_params.b0_B > 0.0 ? m_params.b0_B
                                              : m_params.bare_mass_B));
            const data_t s = rB / core_B;
            factor *= 1.0 - exp(-pow(s, (data_t)m_params.lapse_core_power));
        }
        return factor;
    }

    //! Accumulate one Bowen-York term into the (still conformal-unscaled)
    //! Ahat_ij.  (nx,ny,nz) is the unit radial vector from the throat and r2
    //! the (regularised) squared distance to it.
    template <class data_t>
    AMREX_GPU_HOST_DEVICE AMREX_FORCE_INLINE static void
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

    //! v . grad phi of one drainhole profile phi = C atan(X),
    //! X = (r - b^2 / 4 r) / b: dphi/dr = C (1 + b^2 / 4 r^2) / (b (1 + X^2)),
    //! grad phi = dphi/dr (dx, dy, dz) / r.  C already carries the sign of
    //! the profile (phi_sign_B for throat B).
    template <class data_t>
    AMREX_GPU_DEVICE AMREX_FORCE_INLINE static data_t
    // NOLINTNEXTLINE(bugprone-easily-swappable-parameters)
    boost_term(const double C, const data_t X, const double b,
               const double b_sq, const data_t r, const data_t dx,
               const data_t dy, const data_t dz, const double vx,
               const double vy, const double vz)
    {
        const data_t dphi_dr = (data_t)C * (1.0 + (data_t)b_sq / (4.0 * r * r)) /
                               ((data_t)b * (1.0 + X * X));
        const data_t v_dot_n =
            ((data_t)vx * dx + (data_t)vy * dy + (data_t)vz * dz) / r;
        return dphi_dr * v_dot_n;
    }

    params_t m_params;
    double m_dx;

    //! Boost flags, precomputed in the constructor: a throat is boosted when
    //! it exists (b > 0) and its velocity is nonzero.
    bool m_boost_A{false};
    bool m_boost_B{false};

    //! Exact boost (momentum_model = 1), per throat A, B: speed, Lorentz
    //! factor and unit direction; 0, 1 and 0 otherwise.
    double m_boost_speed[2]{0.0, 0.0};
    double m_boost_gamma[2]{1.0, 1.0};
    double m_boost_dir[2][3]{{0.0, 0.0, 0.0}, {0.0, 0.0, 0.0}};
    //! Half the throat separation: the width of the companion-weight window.
    double m_boost_window{1.0};
    //! The companion cut's radius in units of the throat's a (the collar's
    //! 0.3; boost_background).
    static constexpr double m_boost_cut_fraction = 0.3;

    //! Helfer/Ning correction, precomputed in the constructor.  All zero and
    //! m_helfer_on false unless the correction is on and both throats exist.
    bool m_helfer_on{false};
    double m_helfer_w{1.0};
    double m_helfer_dpsi_A{0.0};
    double m_helfer_dpsi_B{0.0};
    double m_helfer_du_A{0.0};
    double m_helfer_du_B{0.0};

    //! Constraint-solve background: chosen minus superposed puncture
    //! coefficient per throat (background 0 only; zero otherwise).
    double m_solve_shift_A{0.0};
    double m_solve_shift_B{0.0};
};

#endif /* BINARYWORMHOLEINITIALDATA_HPP_ */
