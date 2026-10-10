#ifndef SPINNINGWORMHOLELEVEL_HPP_
#define SPINNINGWORMHOLELEVEL_HPP_

#include "BHAMR.hpp"
#include "DefaultLevelFactory.hpp"
#include "GRAMRLevel.hpp"

class SimulationParameters;

class SpinningWormholeLevel : public GRAMRLevel
{
  public:
    //! One throat, fixed at the grid centre; it is not a puncture and
    //! puncture tracking stays disabled (puncture_tracking.enabled = 0).
    //! The AMR container is a BHAMR (a GRAMR child) purely to reuse the
    //! ParticleInterpolator that BHAMR::init() sets up for in-code
    //! Weyl4 / Psi4 spherical-harmonic extraction - see
    //! specificPostTimeStep.
    static constexpr int num_punctures = 1;

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
        never fires, so they never get a header line either.  The t = 0 row
        is the measurement for every initial-data check (the background's
        constraint residual, the throat radii against the table's values).
    */
    void specific_post_init() override;

    //! Constraint norms + collapse + throat/ergoregion diagnostics.  Shared
    //! by specific_post_init (t = 0) and specificPostTimeStep (t > 0) so both
    //! write identical columns to the same files.  Public only because nvcc
    //! refuses extended __device__ lambdas inside a private member function.
    void write_scalar_diagnostics();
};

#endif /* SPINNINGWORMHOLELEVEL_HPP_ */
