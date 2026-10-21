#include "BHAMR.hpp"
#include "DefaultLevelFactory.hpp"
#include "GRAMR.hpp"
#include "GRParmParse.hpp"
#include "SetupFunctions.hpp"
#include "SimulationParameters.hpp"
#include "SpinningWormholeLevel.hpp"

int runGRTeclyn(int /*argc*/, char * /*argv*/[])
{
    BL_PROFILE("runGRTeclyn()");

    GRParmParse pp;
    SimulationParameters sim_params(pp);

    if (sim_params.just_check_params)
        return 0;

    SpinningWormholeLevel::set_sim_params(&sim_params);

    DefaultLevelFactory<SpinningWormholeLevel> swh_level_bld;

    // BHAMR (a GRAMR child) so that BHAMR::init() sets up the Weyl4
    // ParticleInterpolator used for in-code Psi4 spherical-harmonic extraction
    // (see SpinningWormholeLevel::specificPostTimeStep).  Puncture tracking is
    // disabled; the throat sits at the grid centre and is monitored through
    // throat_geometry.dat instead.
    BHAMR<SpinningWormholeLevel::num_punctures> swh_amr(&swh_level_bld);

    swh_amr.init(0., sim_params.stop_time);

    while (
        (swh_amr.okToContinue() != 0) &&
        (swh_amr.levelSteps(0) < sim_params.max_steps ||
         sim_params.max_steps < 0) &&
        (swh_amr.cumTime() < sim_params.stop_time || sim_params.stop_time < 0.0))
    {
        swh_amr.coarseTimeStep(sim_params.stop_time);
    }

    if (swh_amr.stepOfLastCheckPoint() < swh_amr.levelSteps(0) &&
        sim_params.checkpoint_interval >= 0)
    {
        swh_amr.checkPoint();
    }

    if (swh_amr.stepOfLastPlotFile() < swh_amr.levelSteps(0) &&
        sim_params.plot_interval >= 0)
    {
        swh_amr.writePlotFile();
    }

    return 0;
}

int main(int argc, char *argv[])
{
    mainSetup(argc, argv);
    int status = runGRTeclyn(argc, argv);
    mainFinalize();
    return status;
}
