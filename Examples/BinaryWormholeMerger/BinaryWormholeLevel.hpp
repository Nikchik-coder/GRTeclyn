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
};

#endif /* BINARYWORMHOLELEVEL_HPP_ */
