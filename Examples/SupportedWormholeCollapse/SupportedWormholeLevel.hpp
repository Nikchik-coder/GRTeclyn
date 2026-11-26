#ifndef SUPPORTEDWORMHOLELEVEL_HPP_
#define SUPPORTEDWORMHOLELEVEL_HPP_

#include "DefaultLevelBld.hpp"
#include "GRAmrLevel.hpp"

class SimulationParameters;

class SupportedWormholeLevel : public GRAmrLevel
{
  public:
    static void variableSetUp();

    using GRAmrLevel::GRAmrLevel;

    //! Fork-local replacement for the GRAmr simulation-parameters store that
    //! upstream deleted: main() hands this class a pointer to its
    //! SimulationParameters before Amr::init.  Pointer semantics preserve the
    //! old behaviour where runtime updates made in main (RL pump state) are
    //! visible from the levels.
    static void set_sim_params(const SimulationParameters *a_sim_params);
    static const SimulationParameters &simParams();


    void specific_advance() override;
    void initData() override;
    void specific_eval_rhs(amrex::MultiFab &a_soln, amrex::MultiFab &a_rhs,
                         const double a_time) override;
    void specific_update_ode(amrex::MultiFab &a_soln) override;
    void pre_tag_cells() final;
    void tag_cells(amrex::TagBoxArray &a_tag_box_array,
                   amrex::Real a_regrid_threshold) final;
    void specific_post_timestep() override;
};

#endif /* SUPPORTEDWORMHOLELEVEL_HPP_ */