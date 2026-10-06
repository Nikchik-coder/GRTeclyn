/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#include "GRAMR.hpp"
#include "CheckpointRetention.hpp"
#include "GRAMRLevel.hpp"
#include "SimulationParameters.hpp"

#include <AMReX_ParmParse.H>

#include <string>

GRAMR::GRAMR(amrex::LevelBld *a_levelbld) : amrex::Amr(a_levelbld) {}

GRAMR::~GRAMR() = default;

void GRAMR::init(amrex::Real a_strt_time, amrex::Real a_stop_time)
{
    amrex::Amr::init(a_strt_time, a_stop_time);

    m_start_walltime = amrex::second();
}

void GRAMR::checkPoint()
{
    amrex::Amr::checkPoint();

    // Read here rather than plumbing through the constructor: this runs once
    // per checkpoint, and both keys are already in the parameter table.
    int keep = 0;
    {
        amrex::ParmParse pp;
        pp.query("checkpoint_keep", keep);
    }
    std::string restart_file;
    {
        amrex::ParmParse pp("amr");
        pp.query("restart", restart_file);
    }

    CheckpointRetention::prune(check_file_root, keep, restart_file);
}

amrex::Real GRAMR::get_walltime_since_start() const
{
    return amrex::second() - m_start_walltime;
}

amrex::Real GRAMR::get_restart_time() const { return m_restart_time; }

void GRAMR::set_restart_time(amrex::Real a_restart_time)
{
    m_restart_time = a_restart_time;
}