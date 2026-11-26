#ifndef BINARYWORMHOLELEVEL_HPP_
#define BINARYWORMHOLELEVEL_HPP_

#include "BHAmr.hpp"
#include "DefaultLevelBld.hpp"
#include "GRAmrLevel.hpp"

class SimulationParameters;

class BinaryWormholeLevel : public GRAmrLevel
{
  public:
    //! There are two throats, but they are not punctures and puncture tracking
    //! stays disabled (puncture_tracking.enabled = 0).  The AMR container is a
    //! BHAmr (a GRAmr child) purely to reuse the ParticleInterpolator that
    //! BHAmr::init() sets up for in-code Weyl4 / Psi4 spherical-harmonic
    //! extraction - see specific_post_timestep.
    static constexpr int num_punctures = 2;

    static void variableSetUp();

    using GRAmrLevel::GRAmrLevel;

    //! Fork-local replacement for the GRAmr simulation-parameters store that
    //! upstream deleted: main() hands this class a pointer to its
    //! SimulationParameters before Amr::init.
    static void set_sim_params(const SimulationParameters *a_sim_params);
    static const SimulationParameters &simParams();

    //! Access the owning BHAmr (for its m_weyl_interpolator).
    BHAmr<num_punctures> *get_bhamr_ptr();

    void specific_advance() override;
    void initData() override;
    void specific_eval_rhs(amrex::MultiFab &a_soln, amrex::MultiFab &a_rhs,
                         const double a_time) override;
    void specific_update_ode(amrex::MultiFab &a_soln) override;
    void pre_tag_cells() final;
    void tag_cells(amrex::TagBoxArray &a_tag_box_array,
                   amrex::Real a_regrid_threshold) final;
    void specific_post_timestep() override;

    //! Write the t = 0 row of every scalar diagnostic stream.
    /*!
        specific_post_timestep first runs at t = dt, so without this the .dat
        files begin one step in - and their `first_step = (time == 0)` test
        never fires, so they never get a header line either.  Several checks
        are statements about the INITIAL data (the momentum constraint is
        analytically zero at t = 0, the Hamiltonian defect scales as 1/d^2 at
        t = 0), so a t = 0 row is not a nicety here, it is the measurement.
    */
    void specific_post_init() override;

    //! Hamiltonian-constraint solve of the t = 0 slice over the whole
    //! hierarchy (constraint_solve = 1; DrainholeConstraintSolve.hpp), then
    //! every level rebuilt from the solved conformal factor.  Level 0 only.
    //! Public for the same nvcc reason as write_scalar_diagnostics.
    void solve_initial_constraints();

    //! Constraint norms + collapse + two-throat diagnostics.  Shared by
    //! specific_post_init (t = 0) and specific_post_timestep (t > 0) so that both
    //! write identical columns to the same files.  Public only because nvcc
    //! refuses extended __device__ lambdas inside a private member function.
    void write_scalar_diagnostics();

    //! ABSOLUTE coordinates of the tracked throat centres, A then B, seeded
    //! from the params-file positions by set_sim_params and updated every
    //! coarse step by ThroatTracker (when throat_tracking = 1).  Static
    //! because tag_cells needs them on every level and the tracker updates
    //! them on level 0 only; every MPI rank computes the same reduced values,
    //! so no broadcast is needed.
    static std::array<amrex::Real, 2 * AMREX_SPACEDIM> s_throat_centers;
};

#endif /* BINARYWORMHOLELEVEL_HPP_ */
