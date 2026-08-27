#ifndef SUPPORTEDWORMHOLELEVEL_HPP_
#define SUPPORTEDWORMHOLELEVEL_HPP_

#include "DefaultLevelFactory.hpp"
#include "GRAMRLevel.hpp"

class SimulationParameters;

class SupportedWormholeLevel : public GRAMRLevel
{
  public:
    static void variableSetUp();

    using GRAMRLevel::GRAMRLevel;

    //! Fork-local replacement for the GRAMR simulation-parameters store that
    //! upstream deleted: main() hands this class a pointer to its
    //! SimulationParameters before Amr::init.  Pointer semantics preserve the
    //! old behaviour where runtime updates made in main (RL pump state) are
    //! visible from the levels.
    static void set_sim_params(const SimulationParameters *a_sim_params);
    static const SimulationParameters &simParams();


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

#endif /* SUPPORTEDWORMHOLELEVEL_HPP_ */