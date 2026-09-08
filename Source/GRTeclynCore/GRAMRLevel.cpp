/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#include "GRAMRLevel.hpp"
#include "NullBCFill.hpp"
#include "StateTypes.hpp"

#include <AMReX_FArrayBox.H>
#include <AMReX_ParmParse.H>

#include <cmath>
#include <iomanip>
#include <sstream>

void GRAMRLevel::stateVariableSetUp()
{
    GRParmParse pp;
    int nghost{};
    pp.get("evolution.num_ghosts", nghost);
    desc_lst.addDescriptor(state_index, amrex::IndexType::TheCellType(),
                           amrex::StateDescriptor::Point, nghost, NUM_VARS,
                           &amrex::cell_quartic_interp);

    BoundaryConditions boundary_conditions;
    boundary_conditions.define(amrex::DefaultGeometry());

    amrex::Vector<amrex::BCRec> bcs(NUM_VARS);
    for (int icomp = 0; icomp < NUM_VARS; ++icomp)
    {
        auto &bc = bcs[icomp];
        for (amrex::OrientationIter oit; oit.isValid(); ++oit)
        {
            amrex::Orientation face = oit();
            const int idim          = face.coordDir();
            const int bctype = boundary_conditions.get_boundary_condition(face);
            if (boundary_conditions.is_periodic(idim))
            {
                bc.set(face, amrex::BCType::int_dir);
            }
            else if (bctype ==
                         BoundaryConditions::FIRST_ORDER_EXTRAPOLATION_BC ||
                     bctype == BoundaryConditions::SOMMERFELD_BC)
            {
                bc.set(face, amrex::BCType::foextrap);
            }
            else if (bctype == BoundaryConditions::REFLECTIVE_BC)
            {
                int parity =
                    BoundaryConditions::get_state_var_parity(icomp, idim);
                if (parity == 1)
                {
                    bc.set(face, amrex::BCType::reflect_even);
                }
                else
                {
                    bc.set(face, amrex::BCType::reflect_odd);
                }
            }
            else
            {
                amrex::Abort("Unknown boundary condition type " +
                             std::to_string(bctype));
            }
        }
    }

    amrex::StateDescriptor::BndryFunc boundary_function(null_bc_fill);
    boundary_function.setRunOnGPU(true); // Run the bc function on gpu.

    desc_lst.setComponent(state_index, 0, StateVariables::names, bcs,
                          boundary_function);
}

void GRAMRLevel::variableCleanUp()
{
    desc_lst.clear();
    derive_lst.clear();
}

GRAMRLevel::GRAMRLevel() = default;

GRAMRLevel::GRAMRLevel(amrex::Amr &papa, int lev, const amrex::Geometry &geom,
                       const amrex::BoxArray &box_array,
                       const amrex::DistributionMapping &distribution_mapping,
                       amrex::Real time)
    : amrex::AmrLevel(papa, lev, geom, box_array, distribution_mapping, time)
{
    GRParmParse pp;
    pp.get("evolution.nan_check", nan_check);
    pp.query("evolution.nan_autopsy", nan_autopsy);
    m_boundaries.define(geom);
}

GRAMRLevel::~GRAMRLevel() = default;

GRAMR *GRAMRLevel::get_gramr_ptr()
{
    if (m_gramr_ptr == nullptr)
    {
        if (parent == nullptr)
        {
            amrex::Abort("AmrLevel::parent is null");
        }
        m_gramr_ptr = dynamic_cast<GRAMR *>(parent);
    }
    return m_gramr_ptr;
}

void GRAMRLevel::computeInitialDt(
    int finest_level, int /*sub_cycle*/, amrex::Vector<int> & /*n_cycle*/,
    const amrex::Vector<amrex::IntVect> & /*ref_ratio*/,
    amrex::Vector<amrex::Real> &dt_level, amrex::Real /*stop_time*/)
{
    // Level 0 will do it for all levels
    if (Level() == 0)
    {
        GRParmParse pp;
        amrex::Real dt_multiplier{};
        pp.get("evolution.dt_multiplier", dt_multiplier);
        for (int i = 0; i <= finest_level; ++i)
        {
            dt_level[i] = dt_multiplier * parent->Geom(i).CellSize(0);
        }
    }
}

// NOLINTBEGIN(bugprone-easily-swappable-parameters)
void GRAMRLevel::computeNewDt(
    int finest_level, int /*sub_cycle*/, amrex::Vector<int> & /*n_cycle*/,
    const amrex::Vector<amrex::IntVect> & /*ref_ratio*/,
    amrex::Vector<amrex::Real> &dt_min, amrex::Vector<amrex::Real> &dt_level,
    amrex::Real /*stop_time*/, int /*post_regrid_flag*/)
// NOLINTEND(bugprone-easily-swappable-parameters)
{
    // This is called at the end of a coarse time step
    // Level 0 will do it for all levels
    if (Level() == 0)
    {
        GRParmParse pp;
        amrex::Real dt_multiplier{};
        pp.get("evolution.dt_multiplier", dt_multiplier);

        for (int i = 0; i <= finest_level; ++i)
        {
            dt_min[i] = dt_level[i] =
                dt_multiplier * parent->Geom(i).CellSize(0);
        }
    }
}

amrex::Real GRAMRLevel::advance(amrex::Real time, amrex::Real dt, int iteration,
                                int ncycle)
{
    BL_PROFILE("GRAMRLevel::advance()");
    amrex::Real seconds_per_hour = 3600.;
    amrex::Real evolution_speed = (time - get_gramr_ptr()->get_restart_time()) *
                                  seconds_per_hour /
                                  get_gramr_ptr()->get_walltime_since_start();
    amrex::Print() << "[Level " << Level() << " step "
                   << parent->levelSteps(Level()) + 1
                   << "] average evolution speed = " << evolution_speed
                   << " code units/h\n";

    for (int k = 0; k < NUM_STATE_TYPE; k++)
    {
        state[k].allocOldData();
        state[k].swapTimeLevels(dt);
    }

    amrex::AmrLevel::RK(
        4, state_index, time, dt, iteration, ncycle,
        [&](int /*stage*/, amrex::MultiFab &rhs, const amrex::MultiFab &soln,
            amrex::Real t, amrex::Real /*dtsub*/)
        {
            // NOLINTNEXTLINE(cppcoreguidelines-pro-type-const-cast)
            specificEvalRHS(const_cast<amrex::MultiFab &>(soln), rhs, t);
            m_boundaries.apply_sommerfeld_boundaries(rhs, soln);
        },
        [&](int /*stage*/, amrex::MultiFab &soln) { specificUpdateODE(soln); });

    specificAdvance();

    return dt;
}

void GRAMRLevel::post_timestep(int /*iteration*/)
{
    BL_PROFILE("GRAMRLevel::post_timestep()");
    const int lev = Level();
    if (lev < parent->finestLevel())
    {
        auto &fine_level              = parent->getLevel(Level() + 1);
        amrex::MultiFab &state_fine   = fine_level.get_new_data(state_index);
        amrex::MultiFab &state_coarse = this->get_new_data(state_index);
        amrex::Real t                 = get_state_data(state_index).curTime();

        amrex::IntVect ratio = parent->refRatio(lev);
        AMREX_ASSERT(ratio == 2 || ratio == 4);
        if (ratio == 2)
        {
            // Need to fill one ghost cell for the high-order interpolation
            // below
            FillPatch(fine_level, state_fine, 1, t, state_index, 0,
                      state_fine.nComp());
        }

        FourthOrderInterpFromFineToCoarse(state_coarse, 0, NUM_VARS, state_fine,
                                          ratio);
    }

    if (nan_check)
    {
        amrex::MultiFab &state_new = get_new_data(state_index);
        if (state_new.contains_nan(0, state_new.nComp(), amrex::IntVect(0),
                                   true))
        {
            for (int icomp = 0; icomp < state_new.nComp(); ++icomp)
            {
                if (state_new.contains_nan(icomp, 1, amrex::IntVect(0), true))
                {
                    amrex::AllPrint()
                        << "NaN diagnostic: rank="
                        << amrex::ParallelDescriptor::MyProc()
                        << " level=" << lev << " component=" << icomp
                        << " name=" << StateVariables::names[icomp]
                        << std::endl;
                    break;
                }
            }
            if (nan_autopsy)
            {
                nan_autopsy_report(state_new);
            }
            amrex::Abort("NaN in GRAMRLevel::post_timestep");
        }
    }

    specificPostTimeStep();
}

void GRAMRLevel::nan_autopsy_report(amrex::MultiFab &a_state_new)
{
    // Abort path only.  Each box is copied to pinned host memory and scanned
    // there: at this point nothing may be asked of a device kernel that has
    // to survive the NaN itself.
    const int lev             = Level();
    const int ncomp           = a_state_new.nComp();
    const auto dx             = Geom().CellSizeArray();
    const auto prob_lo        = Geom().ProbLoArray();
    const amrex::Box domain   = Geom().Domain();
    const amrex::BoxArray &ba = a_state_new.boxArray();
    amrex::MultiFab &state_old = get_old_data(state_index);
    const amrex::Real t_new   = get_state_data(state_index).curTime();
    const amrex::Real t_old   = get_state_data(state_index).prevTime();
    const amrex::Real dt      = t_new - t_old;
    const int step            = parent->levelSteps(lev);

    amrex::Real min_chi = -1.0, min_lapse = -1.0;
    {
        amrex::ParmParse ccz4_pp("ccz4");
        ccz4_pp.query("min_chi", min_chi);
        ccz4_pp.query("min_lapse", min_lapse);
    }
    int c_chi_idx = -1, c_lapse_idx = -1;
    for (int c = 0; c < ncomp; ++c)
    {
        if (StateVariables::names[c] == "chi")
        {
            c_chi_idx = c;
        }
        if (StateVariables::names[c] == "lapse")
        {
            c_lapse_idx = c;
        }
    }

    constexpr int max_reports = 3;
    constexpr int max_probe   = 16;
    int reports               = 0;
    for (amrex::MFIter mfi(a_state_new); mfi.isValid() && reports < max_reports;
         ++mfi)
    {
        const amrex::Box &bx = mfi.validbox();
        amrex::FArrayBox hnew(bx, ncomp, amrex::The_Pinned_Arena());
        amrex::FArrayBox hold(bx, ncomp, amrex::The_Pinned_Arena());
        hnew.copy<amrex::RunOn::Device>(a_state_new[mfi], bx, 0, bx, 0, ncomp);
        hold.copy<amrex::RunOn::Device>(state_old[mfi], bx, 0, bx, 0, ncomp);
        amrex::Gpu::streamSynchronize();
        const auto anew = hnew.const_array();
        const auto aold = hold.const_array();
        const auto lo   = amrex::lbound(bx);
        const auto hi   = amrex::ubound(bx);
        for (int k = lo.z; k <= hi.z && reports < max_reports; ++k)
        {
            for (int j = lo.y; j <= hi.y && reports < max_reports; ++j)
            {
                for (int i = lo.x; i <= hi.x && reports < max_reports; ++i)
                {
                    bool bad = false;
                    for (int c = 0; c < ncomp; ++c)
                    {
                        if (!std::isfinite(anew(i, j, k, c)))
                        {
                            bad = true;
                            break;
                        }
                    }
                    if (!bad)
                    {
                        continue;
                    }
                    ++reports;
                    const amrex::IntVect iv(AMREX_D_DECL(i, j, k));
                    std::ostringstream os;
                    os << std::setprecision(10);
                    os << "NaN autopsy [rank "
                       << amrex::ParallelDescriptor::MyProc() << "]: level "
                       << lev << " step " << step << " ("
                       << step - m_last_regrid_step
                       << " steps since this level was last regridded)"
                       << " t_old " << t_old << " -> t_new " << t_new
                       << " dt " << dt << "\n";
                    os << "  cell (" << i << "," << j << "," << k << ") at x = ("
                       << prob_lo[0] + (i + 0.5) * dx[0] << ", "
                       << prob_lo[1] + (j + 0.5) * dx[1] << ", "
                       << prob_lo[2] + (k + 0.5) * dx[2] << "), dx = " << dx[0]
                       << "\n";
                    os << "  cells to the edge of this level's grids "
                          "(+x -x +y -y +z -z; c/f = coarse-fine, dom = "
                          "domain):";
                    for (int d = 0; d < AMREX_SPACEDIM; ++d)
                    {
                        for (int sgn : {+1, -1})
                        {
                            int n = 0;
                            amrex::IntVect p = iv;
                            while (n < max_probe)
                            {
                                p[d] += sgn;
                                if (!ba.contains(p))
                                {
                                    break;
                                }
                                ++n;
                            }
                            os << " " << n;
                            if (n < max_probe)
                            {
                                os << (domain.contains(p) ? "(c/f)" : "(dom)");
                            }
                            else
                            {
                                os << "(+)";
                            }
                        }
                    }
                    os << "\n  floors: min_chi " << min_chi << " min_lapse "
                       << min_lapse << "\n";
                    os << "  variable: old -> new   [|new-old|/dt when both "
                          "finite]\n";
                    for (int c = 0; c < ncomp; ++c)
                    {
                        const amrex::Real o  = aold(i, j, k, c);
                        const amrex::Real nn = anew(i, j, k, c);
                        os << "    " << std::setw(8) << StateVariables::names[c]
                           << ": " << o << " -> " << nn;
                        if (std::isfinite(o) && std::isfinite(nn) && dt > 0.0)
                        {
                            os << "   [" << std::abs(nn - o) / dt << "]";
                        }
                        else if (!std::isfinite(nn))
                        {
                            os << "   <-- NON-FINITE";
                        }
                        os << "\n";
                    }
                    if (c_chi_idx >= 0 && c_lapse_idx >= 0)
                    {
                        os << "  old chi/lapse at the six neighbours "
                              "(-x +x -y +y -z +z; '-' = outside this box):";
                        for (int d = 0; d < AMREX_SPACEDIM; ++d)
                        {
                            for (int sgn : {-1, +1})
                            {
                                amrex::IntVect p = iv;
                                p[d] += sgn;
                                if (bx.contains(p))
                                {
                                    os << " " << aold(p, c_chi_idx) << "/"
                                       << aold(p, c_lapse_idx);
                                }
                                else
                                {
                                    os << " -/-";
                                }
                            }
                        }
                        os << "\n";
                    }
                    amrex::AllPrint() << os.str() << std::flush;
                }
            }
        }
    }
    if (reports == 0)
    {
        amrex::AllPrint() << "NaN autopsy [rank "
                          << amrex::ParallelDescriptor::MyProc()
                          << "]: no non-finite cell in this rank's boxes on "
                             "level "
                          << lev << " (it is on another rank)\n";
    }
}

void GRAMRLevel::post_regrid(int a_lbase, int a_new_finest)
{
    m_last_regrid_step = parent->levelSteps(Level());
    specific_post_regrid(a_lbase, a_new_finest);
}

void GRAMRLevel::post_init(amrex::Real /*stop_time*/)
{
    if (Level() == 0)
    {
        get_gramr_ptr()->set_restart_time(get_gramr_ptr()->cumTime());
    }
    specific_post_init();
}

void GRAMRLevel::post_restart()
{
    if (Level() == 0)
    {
        get_gramr_ptr()->set_restart_time(get_gramr_ptr()->cumTime());
    }
    specific_post_restart();
}

void GRAMRLevel::init(amrex::AmrLevel &old)
{
    BL_PROFILE("GRAMRLevel::init()");
    amrex::Real dt_new    = parent->dtLevel(level);
    amrex::Real cur_time  = old.get_state_data(state_index).curTime();
    amrex::Real prev_time = old.get_state_data(state_index).prevTime();
    amrex::Real dt_old    = cur_time - prev_time;
    setTimeLevel(cur_time, dt_old, dt_new);

    amrex::MultiFab &S_new = get_new_data(state_index);
    FillPatch(old, S_new, 0, cur_time, state_index, 0, S_new.nComp());
}

void GRAMRLevel::init()
{
    BL_PROFILE("GRAMRLevel::init()");
    amrex::Real dt = parent->dtLevel(level);
    const auto &coarse_state =
        parent->getLevel(level - 1).get_state_data(state_index);
    amrex::Real cur_time  = coarse_state.curTime();
    amrex::Real prev_time = coarse_state.prevTime();
    amrex::Real dt_old =
        (cur_time - prev_time) /
        static_cast<amrex::Real>(parent->MaxRefRatio(level - 1));
    setTimeLevel(cur_time, dt_old, dt);

    amrex::MultiFab &S_new = get_new_data(state_index);
    FillCoarsePatch(S_new, 0, cur_time, state_index, 0, S_new.nComp());
}

void GRAMRLevel::errorEst(amrex::TagBoxArray &a_tag_box_array,
                          int /*a_clearval*/, int /*a_tagval*/,
                          amrex::Real /*a_time*/, int /*a_n_error_buf*/,
                          int /*a_ngrow*/)
{
    BL_PROFILE("GRAMRLevel::errorEst()");

    pre_tag_cells();

    // It is up to the derived class to use regrid_threshold in tag_cells()
    amrex::Vector<double> regrid_thresholds;
    GRParmParse pp;
    pp.getarr("tagging.thresholds", regrid_thresholds);
    amrex::Real regrid_threshold = regrid_thresholds[Level()];
    tag_cells(a_tag_box_array, regrid_threshold);
}

void GRAMRLevel::writePlotFilePre(const std::string &a_dir, std::ostream &a_os)
{
    specific_pre_plotfile(a_dir, a_os);
}

void GRAMRLevel::writePlotFilePost(const std::string &a_dir, std::ostream &a_os)
{
    specific_post_plotfile(a_dir, a_os);
}

void GRAMRLevel::checkPointPre(const std::string &a_dir, std::ostream &a_os)
{
    specific_pre_checkpoint(a_dir, a_os);
}

void GRAMRLevel::checkPointPost(const std::string &a_dir, std::ostream &a_os)
{
    specific_post_checkpoint(a_dir, a_os);
}

bool GRAMRLevel::at_level_timestep_multiple(int a_level)
{
    // handle both the case a_level < Level() and a_level >= Level()
    int coarser_level     = std::min(a_level, Level());
    int finer_level       = std::max(a_level, Level());
    int finer_level_steps = get_gramr_ptr()->levelSteps(finer_level);

    // work out what the coarser level step number corresponds to on the finer
    // level
    int coarser_level_steps_at_finer_level =
        get_gramr_ptr()->levelSteps(coarser_level);

    for (int ilev = coarser_level + 1; ilev <= finer_level; ++ilev)
    {
        coarser_level_steps_at_finer_level *= get_gramr_ptr()->nCycle(ilev);
    }
    // finer_level_steps will be > coarser_level_steps
    return (finer_level_steps == coarser_level_steps_at_finer_level);
}
