/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef DRAINHOLECONSTRAINTSOLVE_HPP_
#define DRAINHOLECONSTRAINTSOLVE_HPP_

#include "BinaryWormholeInitialData.hpp"

#include <AMReX_Amr.H>
#include <AMReX_MultiFab.H>
#include <AMReX_Vector.H>

#include <array>

//! Hamiltonian-constraint solve for the drainhole binary's t = 0 slice.
/*!
    Solves, on the whole initial AMR hierarchy at once,

        lap Psi - V Psi + (1/8) Ahat.Ahat Psi^{-7} = 0,   Psi = Psi_bg + w,

    for w, with phi and Ahat_ij held at their superposed values (so the
    momentum constraint stays exact) and w ~ M/r at the outer boundary (Robin
    a w + dw/dn = 0 with a = |n.x|/r^2, exact for a monopole).  The
    background, its closed-form Laplacian, V and Ahat.Ahat come from
    BinaryWormholeInitialData::constraint_background; see that class comment
    for the physics and the puncture-coefficient choice.

    The operator is AMReX's MLABecLaplacian, (A - lap) w = f with A >= 0: a
    single linear solve for a head-on (Ahat = 0) and a Newton iteration of
    the same solve otherwise,

        A_k = V + (7/8) Ahat.Ahat Psi_k^{-8},
        f_k = (lap Psi_bg - V Psi_bg) + (1/8) Ahat.Ahat Psi_k^{-7}
              + (7/8) Ahat.Ahat Psi_k^{-8} w_k,

    solved for w_{k+1} directly.  The background residual is analytic, so the
    exact single throat gives w = 0 identically, and the solve's own error is
    the second-order error of the 7-point operator acting on w alone.  After
    the solve w is averaged down, so a covered coarse cell carries its fine
    cells' mean correction.

    ---- Each mouth's far side (measured after every solve) ----------------
    Near throat X, Psi = c_X / r + d_X + O(r): the inversion r' = c_X^2 / r
    turns that into Psi' = 1 + c_X d_X / r' + ..., so the ADM mass of the
    throat's own compactified infinity is

        M_far = 2 c_X d_X,      d_X = d_bg (closed form) + w0,

    with w0 the monopole of w at the centre (a linear fit in r on the finest
    level that covers a small ball there).  The scalar has phi = phi_0 +
    (4 C / a) r + (l = 1) near the centre, so the far side also carries a
    scalar charge Q_far = 4 C c_X^2 / a.  The isolated drainhole (a, m) has
    M_far = -m e^{pi m/a} and Q_far = sqrt(a^2 + m^2) e^{pi m/a} / sqrt(4 pi)
    (-4.8105 and 3.0344 for a = 2, m = 1); both are frozen asymptotic
    quantities, the drainhole analogue of a puncture's individual mass.
    (M_far, Q_far) pick one isolated drainhole (a', m'), whose near-side mass
    m' is the mouth's one-body mass: E_b = M_ADM - m'_A - m'_B.

    ---- Far-side matching (puncture mode 3) -------------------------------
    The superposition hands each throat the companion's constants, which
    rescale it: at d = 8 each mouth of the superposed pair has 1.115 x the
    isolated far-side mass, 1.132 x its far-side charge and 1.148 x its
    minimal areal radius.  The solve at the superposition's c keeps the
    charge exactly and the mass to 0.1 % (its R_min grows another 1.3 %).
    With phi held fixed, c alone cannot undo a rescaling: the
    static throat's coordinate size is set by phi.  Mode 3 therefore gives
    each throat a coordinate scale sigma_X (a -> sigma a, m -> sigma m in phi,
    the lapse exponent and Omega; C is scale-free) and iterates c_X, with
    sigma_X = (c_X / c_iso)^2 holding Q_far at the isolated value, until
    M_far is the isolated value too.  Near the throat that is the static
    drainhole's own shape at its isolated size (see the class comment of
    BinaryWormholeInitialData).  match_charge = 0 keeps sigma = 1 and matches
    M_far with c alone, for comparison.  Each iteration is one full solve;
    the Jacobian is a finite difference at the start, then Broyden.
*/
struct ConstraintSolveParams
{
    bool enabled{false};
    //! 0 = the superposition, 1 = bare punctures (validation).
    int background{0};
    //! 0 = superposed c (default), 1 = isolated c, 2 = explicit c_A, c_B,
    //! 3 = far-side matched (iterated; see match_charge).
    int puncture_mode{0};
    double puncture_A{0.0};
    double puncture_B{0.0};
    //! Mode 3: 1 = also hold each mouth's far-side scalar charge at the
    //! isolated throat's, through its coordinate scale (default);
    //! 0 = the far-side mass alone, through c.
    int match_charge{1};
    //! Mode 3: stop once every |M_far / M_far(isolated) - 1| is below this.
    double match_tolerance{1.0e-6};
    int match_max_iter{10};
    //! MLMG relative / absolute tolerance of each linear solve.
    double tolerance_rel{1.0e-10};
    double tolerance_abs{0.0};
    int max_iter{200};
    int max_newton{30};
    //! Newton: stop once max |w_{k+1} - w_k| falls below this.
    double newton_tolerance{1.0e-10};
    int verbose{1};
};

//! One mouth's far side (see the class comment above).
struct MouthReport
{
    bool present{false};
    //! The throat asked for (the params) and the coordinate scale used.
    double a{0.0}, m{0.0}, sigma{1.0};
    double c{0.0};
    //! Psi -> c / r + d at the centre: d = d_bg + w0.
    double d_bg{0.0}, w0{0.0}, w_slope{0.0};
    int level{-1};
    double fit_radius{0.0};
    long ncells{0};
    double M_far{0.0}, Q_far{0.0};
    //! The isolated (a, m) drainhole's values, and the (a', m') one that
    //! has this mouth's (M_far, Q_far).
    double M_far_iso{0.0}, Q_far_iso{0.0};
    double a_equiv{0.0}, m_equiv{0.0};
};

struct ConstraintSolveReport
{
    int newton_iterations{0};
    double last_update{0.0};
    double c_A{0.0}, c_B{0.0};
    double c_superposed_A{0.0}, c_superposed_B{0.0};
    //! max |w| per level (valid cells) and the monopole of w read off the
    //! level-0 boundary cells, W = <r w>: M_ADM ~ M_bg + 2 W.  The outer Robin
    //! condition leaves w a small constant at the face, which biases this
    //! estimate low (2.58 against 2.74 for the d = 8 head-on).
    amrex::Vector<double> max_w;
    double boundary_monopole{0.0};
    double background_mass{0.0};
    //! momentum_model = 1: what M_bg leaves out of the boosted background's
    //! ADM energy.  Each throat integrates to gamma sigma m (M_bg counts
    //! sigma m) and a shift s / r_rest to 2 s asinh(gamma v) / (gamma v)
    //! (M_bg counts 2 s): sum (gamma - 1) sigma m + 2 s [asinh(gamma v) /
    //! (gamma v) - 1].  0 without the boost.
    double boost_mass_correction{0.0};
    //! M_ADM = 2 sum c - (1/2 pi) int [V Psi - (1/8) Ahat.Ahat Psi^-7] dV,
    //! exact for a solution (the box integral is composite, the tail outside
    //! the box analytic with Psi = 1 + M/2r).  Insensitive to the Robin
    //! face: 1.0014 on the exact single throat at L = 64.
    double adm_mass_volume{0.0};
    double tail_integral{0.0};
    bool adm_mass_volume_valid{false};
    std::array<MouthReport, 2> mouth;
    //! Mode 3: outer iterations and full solves spent, final max residual.
    int match_iterations{0};
    int solves{0};
    double match_residual{0.0};
    //! momentum_model = 1: both constraints solved (w and W), the last
    //! pass's max |dW| and max |W| per level (valid cells).
    bool boosted{false};
    double last_W_update{0.0};
    amrex::Vector<double> max_W;
};

//! Solve on levels 0..finest of a_amr and return the correction per level
//! (one component, one ghost cell, averaged down).  a_id is the throat pair
//! the params ask for on entry and the background the returned w belongs to
//! on exit: puncture mode 3 rescales each throat and sets its c, so the
//! caller must rebuild the data from the returned a_id.
//!
//! momentum_model = 1 (the exact boost): the background is the superposed
//! Lorentz-boosted throats, not conformally flat and with K, Pi != 0, and
//! BOTH constraints are solved, for w and a vector potential W with
//! Ahat^ij = Ahat_bg^ij + (L_G W)^ij (see solve_once_boosted).  a_lw returns
//! (L_G W)^ij on every level's valid cells (six components, 11 12 13 22 23
//! 33) for the rebuild; it is left empty for momentum_model = 0.  The
//! far-side matching reads each mouth in its own rest frame: Psi = c / r +
//! d with r the rest-frame radius, since at the puncture G -> delta +
//! gamma^2 v^2 e e, which is flat in rest-frame coordinates.  The volume
//! identity for M_ADM needs K = 0 and a flat conformal metric, so it is
//! skipped (adm_mass_volume_valid stays false).
ConstraintSolveReport
solve_drainhole_constraint(amrex::Amr &a_amr,
                           BinaryWormholeInitialData::params_t &a_id,
                           const ConstraintSolveParams &a_params,
                           amrex::Vector<amrex::MultiFab> &a_w,
                           amrex::Vector<amrex::MultiFab> &a_lw);

//! Each mouth's far side for data with w = 0 everywhere, i.e. the analytic
//! superposition (constraint_solve = 0): the closed-form d, no measurement.
std::array<MouthReport, 2>
superposed_mouths(const BinaryWormholeInitialData::params_t &a_id);

#endif /* DRAINHOLECONSTRAINTSOLVE_HPP_ */
