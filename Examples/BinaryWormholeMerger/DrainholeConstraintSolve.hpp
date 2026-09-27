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
*/
struct ConstraintSolveParams
{
    bool enabled{false};
    //! 0 = the superposition, 1 = bare punctures (validation).
    int background{0};
    //! 0 = superposed c (default), 1 = isolated c, 2 = explicit c_A, c_B.
    int puncture_mode{0};
    double puncture_A{0.0};
    double puncture_B{0.0};
    //! MLMG relative / absolute tolerance of each linear solve.
    double tolerance_rel{1.0e-10};
    double tolerance_abs{0.0};
    int max_iter{200};
    //! Newton: stop once max |w_{k+1} - w_k| falls below this.
    int max_newton{30};
    double newton_tolerance{1.0e-10};
    int verbose{1};
};

struct ConstraintSolveReport
{
    int newton_iterations{0};
    double last_update{0.0};
    double c_A{0.0}, c_B{0.0};
    double c_superposed_A{0.0}, c_superposed_B{0.0};
    //! max |w| per level (valid cells) and the monopole of w read off the
    //! level-0 boundary cells, W = <r w>: M_ADM ~ M_bg + 2 W.
    amrex::Vector<double> max_w;
    double boundary_monopole{0.0};
    double background_mass{0.0};
};

//! Solve on levels 0..finest of a_amr and return the correction per level
//! (one component, one ghost cell, averaged down).
ConstraintSolveReport
solve_drainhole_constraint(amrex::Amr &a_amr,
                           const BinaryWormholeInitialData::params_t &a_id,
                           const ConstraintSolveParams &a_params,
                           amrex::Vector<amrex::MultiFab> &a_w);

#endif /* DRAINHOLECONSTRAINTSOLVE_HPP_ */
