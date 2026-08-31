#ifndef BINARYWORMHOLELEVEL_HPP_
#define BINARYWORMHOLELEVEL_HPP_

#include "BHAMR.hpp"
#include "DefaultLevelFactory.hpp"
#include "GRAMRLevel.hpp"

class SimulationParameters;

class BinaryWormholeLevel : public GRAMRLevel
{
  public:
    //! There are two throats, but they are not punctures and puncture tracking
    //! stays disabled (puncture_tracking.enabled = 0).  The AMR container is a
    //! BHAMR (a GRAMR child) purely to reuse the ParticleInterpolator that
    //! BHAMR::init() sets up for in-code Weyl4 / Psi4 spherical-harmonic
    //! extraction - see specificPostTimeStep.
    static constexpr int num_punctures = 2;

    static void variableSetUp();

    using GRAMRLevel::GRAMRLevel;

    //! Fork-local replacement for the GRAMR simulation-parameters store that
    //! upstream deleted: main() hands this class a pointer to its
    //! SimulationParameters before Amr::init.
    static void set_sim_params(const SimulationParameters *a_sim_params);
    static const SimulationParameters &simParams();

    //! Access the owning BHAMR (for its m_weyl_interpolator).
    BHAMR<num_punctures> *get_bhamr_ptr();

    void specificAdvance() override;
    void initData() override;
    void specificEvalRHS(amrex::MultiFab &a_soln, amrex::MultiFab &a_rhs,
                         const double a_time) override;
    void specificUpdateODE(amrex::MultiFab &a_soln) override;
    void pre_tag_cells() final;
    void tag_cells(amrex::TagBoxArray &a_tag_box_array,
                   amrex::Real a_regrid_threshold) final;
    void specificPostTimeStep() override;

    //! Write the t = 0 row of every scalar diagnostic stream.
    /*!
        specificPostTimeStep first runs at t = dt, so without this the .dat
        files begin one step in - and their `first_step = (time == 0)` test
        never fires, so they never get a header line either.  Phase 1 of
        research/merger/Reference.md is entirely a set of statements about the
        INITIAL data (the momentum constraint is analytically zero at t = 0,
        the Hamiltonian defect scales as 1/d^2 at t = 0), so a t = 0 row is
        not a nicety here, it is the measurement.
    */
    void specific_post_init() override;

    //! Constraint norms + collapse + two-throat diagnostics.  Shared by
    //! specific_post_init (t = 0) and specificPostTimeStep (t > 0) so that both
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
