#include "BinaryWormholeLevel.hpp"
#include "BinaryThroatDiagnostics.hpp"
#include "CoreMatterDamping.hpp"
#include "BinaryWormholeInitialData.hpp"
#include "CCZ4RHSWithMatter.hpp"
#include "ChiTagger.hpp"
#include "ConstraintsWithMatter.hpp"
#include "ExoticScalarField.hpp"
#include "ExternalGridInitialData.hpp"
#include "ExtractionTagger.hpp"
#include "FixedGridsTagger.hpp"
#include "GRParmParse.hpp"
#include "PhantomDecayPotential.hpp"
#include "PositiveChiAndLapse.hpp"
#include "SimulationParameters.hpp"
#include "SmallDataIO.hpp"
#include "SpongeZone.hpp"
#include "ThroatTracker.hpp"
#include "TraceARemoval.hpp"
#include "Weyl4WithMatter.hpp"
#include "WeylExtraction.hpp"

#include <AMReX_Reduce.H>
#include <AMReX_Utility.H>
#include <cmath>

namespace
{
const SimulationParameters *s_sim_params = nullptr;

//! Resolve output_path + data_subpath into a single directory prefix and make
//! sure it exists.  Both diagnostics writers below use it.
std::string resolve_out_dir()
{
    GRParmParse pp;
    std::string output_path = "./";
    pp.load("output_path", output_path, std::string("./"));
    std::string data_subpath;
    pp.load("data_subpath", data_subpath, std::string(""));

    if (!output_path.empty() && output_path.back() != '/')
        output_path += "/";
    if (!data_subpath.empty() && data_subpath.back() != '/')
        data_subpath += "/";

    const std::string out_dir = output_path + data_subpath;
    if (!out_dir.empty())
    {
        amrex::UtilCreateDirectory(out_dir, 0755, false);
    }
    return out_dir;
}
} // namespace

std::array<amrex::Real, 2 * AMREX_SPACEDIM>
    BinaryWormholeLevel::s_throat_centers{};

void BinaryWormholeLevel::set_sim_params(
    const SimulationParameters *a_sim_params)
{
    s_sim_params = a_sim_params;

    // Seed the tracked throat centres from the params-file positions
    // (wormhole_centerA/B are offsets relative to the grid centre).  The
    // tracker refines these every coarse step; until it first runs - and
    // whenever it is disabled - the boxes sit exactly where tagging_type = 1
    // would have put them for a centred single throat.
    const auto &wp = a_sim_params->wormhole_params;
    for (int d = 0; d < AMREX_SPACEDIM; ++d)
    {
        s_throat_centers[d] = static_cast<amrex::Real>(wp.grid_center[d]) +
                              static_cast<amrex::Real>(wp.centerA[d]);
        s_throat_centers[AMREX_SPACEDIM + d] =
            static_cast<amrex::Real>(wp.grid_center[d]) +
            static_cast<amrex::Real>(wp.centerB[d]);
    }
}

const SimulationParameters &BinaryWormholeLevel::simParams()
{
    AMREX_ALWAYS_ASSERT_WITH_MESSAGE(
        s_sim_params != nullptr,
        "set_sim_params must be called before simParams");
    return *s_sim_params;
}

BHAMR<BinaryWormholeLevel::num_punctures> *BinaryWormholeLevel::get_bhamr_ptr()
{
    return dynamic_cast<BHAMR<num_punctures> *>(get_gramr_ptr());
}

void BinaryWormholeLevel::variableSetUp()
{
    BL_PROFILE("BinaryWormholeLevel::variableSetUp()");
    stateVariableSetUp();

    PhantomDecayPotential potential;
    ExoticScalarField<PhantomDecayPotential> exotic_scalar(potential);
    ConstraintsWithMatter<
        ExoticScalarField<PhantomDecayPotential>>::set_up(state_index);
    Weyl4WithMatter<ExoticScalarField<PhantomDecayPotential>>::set_up(
        state_index);
}

void BinaryWormholeLevel::specificAdvance()
{
    amrex::MultiFab &S_new = get_new_data(state_index);
    const auto &arrs       = S_new.arrays();
    TraceARemoval trace_A_removal;
    PositiveChiAndLapse positive_chi_lapse;

    amrex::ParallelFor(S_new,
                       [=] AMREX_GPU_DEVICE(int box_no, int i, int j, int k)
                       {
                           trace_A_removal(i, j, k, arrs[box_no]);
                           positive_chi_lapse(i, j, k, arrs[box_no]);
                       });

    // Matter half of the puncture trick (CoreMatterDamping.hpp): damp the
    // scalar deep inside a collapsed core, where the floors above already
    // own the geometry.  Applied here so it runs exactly once per step per
    // level, next to the other interior regularisers.
    if (simParams().core_damping_params.enabled)
    {
        const CoreMatterDamping damp(simParams().core_damping_params,
                                     parent->dtLevel(level));
        amrex::ParallelFor(S_new,
                           [=] AMREX_GPU_DEVICE(int box_no, int i, int j, int k)
                           { damp(i, j, k, arrs[box_no]); });
    }
}

void BinaryWormholeLevel::initData()
{
    BL_PROFILE("BinaryWormholeLevel::initData");

    amrex::MultiFab &state = get_new_data(state_index);
    const auto &arrs       = state.arrays();

    if (!simParams().recipe_initial_data_file.empty())
    {
        // Route B: constraint-solved data produced by the GRTresna bridge.
        // NOTE: the loader interpolates the file on the level-0 grid spacing,
        // so the solved route is currently limited to near-unigrid resolution.
        // See Stage 2.2 of research/merger/Plan.md for the split-ID fix.
        ExternalGridInitialData ext_data(simParams().external_grid_params,
                                         Geom().CellSize(0));

        const int lapse_type = simParams().wormhole_params.initial_lapse_type;

        amrex::ParallelFor(
            state, state.nGrowVect(),
            [=] AMREX_GPU_DEVICE(int box_no, int i, int j, int k)
            {
                for (int n = 0; n < NUM_VARS; ++n)
                {
                    arrs[box_no](i, j, k, n) = 0.;
                }
                ext_data.compute(i, j, k, arrs[box_no]);

                // The maximal-slicing solve writes lapse == 1, which relaxes
                // violently under 1+log.  A precollapsed seed damps that
                // transient; lapse_type 0 keeps the loaded lapse.
                if (lapse_type != 0)
                {
                    const amrex::Real chi = amrex::max(
                        arrs[box_no](i, j, k, c_chi), amrex::Real(1.0e-10));
                    amrex::Real lapse = arrs[box_no](i, j, k, c_lapse);
                    if (lapse_type == 1)
                        lapse = std::sqrt(chi);
                    else if (lapse_type == 2)
                        lapse =
                            amrex::Real(1.0) - amrex::Real(3.0) * std::log(chi);
                    else if (lapse_type == 3)
                        lapse = chi;
                    arrs[box_no](i, j, k, c_lapse) =
                        amrex::max(lapse, amrex::Real(1.0e-10));
                }
            });
    }
    else
    {
        // Route A: analytic superposition of two Ellis-Bronnikov throats.
        BinaryWormholeInitialData binary(simParams().wormhole_params,
                                         Geom().CellSize(0));

        amrex::ParallelFor(state, state.nGrowVect(),
                           [=] AMREX_GPU_DEVICE(int box_no, int i, int j, int k)
                           {
                               amrex::CellData<amrex::Real> cell =
                                   arrs[box_no].cellData(i, j, k);
                               for (int n = 0; n < cell.nComp(); ++n)
                               {
                                   cell[n] = 0.;
                               }
                               binary.compute(i, j, k, arrs[box_no]);
                           });
    }

    amrex::Gpu::streamSynchronize();
}

void BinaryWormholeLevel::specificEvalRHS(amrex::MultiFab &a_soln,
                                          amrex::MultiFab &a_rhs,
                                          const double a_time)
{
    BL_PROFILE("BinaryWormholeLevel::specificEvalRHS()");
    const int soln_ghosts = a_soln.nGrowVect()[0];
    if (soln_ghosts > 0)
    {
        FillPatch(*this, a_soln, soln_ghosts, a_time, state_index, 0,
                  a_soln.nComp());
    }
    const auto &soln_arrs   = a_soln.arrays();
    const auto &soln_c_arrs = a_soln.const_arrays();
    const auto &rhs_arrs    = a_rhs.arrays();
    TraceARemoval trace_A_removal;
    PositiveChiAndLapse positive_chi_lapse;

    amrex::ParallelFor(a_soln, a_soln.nGrowVect(),
                       [=] AMREX_GPU_DEVICE(int box_no, int i, int j, int k)
                       {
                           trace_A_removal(i, j, k, soln_arrs[box_no]);
                           positive_chi_lapse(i, j, k, soln_arrs[box_no]);
                       });

    PhantomDecayPotential potential(simParams().wormhole_params.phantom_mass);
    ExoticScalarField<PhantomDecayPotential> exotic_scalar(
        potential, simParams().wormhole_params.support_strength);
    CCZ4RHSWithMatter<ExoticScalarField<PhantomDecayPotential>,
                      MovingPunctureGaugeWithMatter, FourthOrderDerivatives>
        ccz4rhs(exotic_scalar, Geom().CellSize(0), 1.0,
                simParams().wormhole_params.grid_center, a_time);

    amrex::ParallelFor(a_rhs,
                       [=] AMREX_GPU_DEVICE(int box_no, int i, int j, int k)
                       {
                           ccz4rhs.compute_full_rhs(i, j, k, rhs_arrs[box_no],
                                                    soln_c_arrs[box_no]);
                       });

    // Sponge zone: extra radially-ramped Kreiss-Oliger dissipation in an outer
    // shell, damping outgoing junk before it reaches the Sommerfeld boundary
    // and returns as a reflection.  Superposed initial data is constraint-
    // violating by construction, so the first thing this example emits is a
    // burst of gauge and constraint junk propagating outward from the throat --
    // clearly visible as concentric rings in the chi slices.  Without a sponge
    // that burst reflects and comes back through the throat at t ~ L, which is
    // exactly when the throat's own dynamics are being measured.
    if (simParams().sponge_params.enabled)
    {
        const SpongeZone sponge(simParams().sponge_params,
                                Geom().CellSize(0));
        amrex::ParallelFor(a_rhs,
                           [=] AMREX_GPU_DEVICE(int box_no, int i, int j, int k)
                           {
                               sponge.apply(i, j, k, rhs_arrs[box_no],
                                            soln_c_arrs[box_no]);
                           });
    }

    amrex::Gpu::streamSynchronize();
}

void BinaryWormholeLevel::specificUpdateODE(amrex::MultiFab &a_soln)
{
    const auto &soln_arrs = a_soln.arrays();
    TraceARemoval trace_A_removal;
    PositiveChiAndLapse positive_chi_lapse;
    amrex::ParallelFor(a_soln, amrex::IntVect(0),
                       [=] AMREX_GPU_DEVICE(int box_no, int i, int j, int k)
                       {
                           trace_A_removal(i, j, k, soln_arrs[box_no]);
                           positive_chi_lapse(i, j, k, soln_arrs[box_no]);
                       });

    amrex::Gpu::streamSynchronize();
}

void BinaryWormholeLevel::pre_tag_cells()
{
    // The ghost fill exists solely so ChiTagger can take second derivatives
    // of chi.  The fixed-box tagger never reads the state, so skip it.
    if (simParams().tagging_type != 0)
    {
        return;
    }

    amrex::MultiFab &state_new = get_new_data(state_index);
    const auto cur_time        = get_state_data(state_index).curTime();
    FillPatch(*this, state_new, 2, cur_time, state_index, c_chi, 1);
}

void BinaryWormholeLevel::tag_cells(amrex::TagBoxArray &a_tag_box_array,
                                    amrex::Real a_regrid_threshold)
{
    BL_PROFILE("BinaryWormholeLevel::tag_cells()");
    amrex::MultiFab &state_new = get_new_data(state_index);
    const auto &tag_arrs       = a_tag_box_array.arrays();

    // Moving nested boxes on the tracked throat centres (Plan.md Stage 2.0):
    // the same box arithmetic as tagging_type = 1 - half-width
    // tagging_L * 2^-(level+2) per level, footprint bounded by construction -
    // but centred on wherever ThroatTracker last measured each throat, so
    // the boxes follow the throats instead of pinning them to the grid
    // centre.  The wave zone composes in via the stock ExtractionTagger,
    // which enforces its required level inside 1.2x each extraction radius
    // and compiles to a no-op when extraction is off.
    if (simParams().tagging_type == 2)
    {
        const amrex::Real dx0 = Geom().CellSize(0);
        const std::array<amrex::Real, AMREX_SPACEDIM> center_A{
            s_throat_centers[0], s_throat_centers[1], s_throat_centers[2]};
        const std::array<amrex::Real, AMREX_SPACEDIM> center_B{
            s_throat_centers[3], s_throat_centers[4], s_throat_centers[5]};

        const FixedGridsTagger tagger_A(dx0, Level(), simParams().tagging_L,
                                        center_A);
        const FixedGridsTagger tagger_B(dx0, Level(), simParams().tagging_L,
                                        center_B);
        const bool has_B = simParams().wormhole_params.b0_B > 0.0;

        // simParams() outlives every kernel, as ExtractionTagger requires.
        const ExtractionTagger shell_tagger(dx0, Level(),
                                            simParams().extraction_params);

        amrex::ParallelFor(a_tag_box_array,
                           [=] AMREX_GPU_DEVICE(int box_no, int i, int j, int k)
                           {
                               tagger_A(i, j, k, tag_arrs[box_no]);
                               if (has_B)
                               {
                                   tagger_B(i, j, k, tag_arrs[box_no]);
                               }
                               shell_tagger(i, j, k, tag_arrs[box_no]);
                           });
        amrex::Gpu::streamSynchronize();
        return;
    }

    // Fixed nested boxes on a static centre: refinement does not respond to
    // the solution, so the footprint is bounded by construction and cannot
    // chase growing error out to an out-of-memory death.  See
    // read_tagging_params() for why that is the right trade here.
    if (simParams().tagging_type == 1)
    {
        const std::array<amrex::Real, AMREX_SPACEDIM> tag_center{
            AMREX_D_DECL(simParams().tagging_center[0],
                         simParams().tagging_center[1],
                         simParams().tagging_center[2])};

        FixedGridsTagger fixed_tagger(Geom().CellSize(0), Level(),
                                      simParams().tagging_L, tag_center);

        amrex::ParallelFor(
            a_tag_box_array,
            [=] AMREX_GPU_DEVICE(int box_no, int i, int j, int k)
            { fixed_tagger(i, j, k, tag_arrs[box_no]); });
        amrex::Gpu::streamSynchronize();
        return;
    }

    const auto &state_new_arrs = state_new.const_arrays();

    ChiTagger chi_tagger(Geom().CellSize(0), a_regrid_threshold);

    amrex::ParallelFor(state_new, amrex::IntVect(0),
                       [=] AMREX_GPU_DEVICE(int box_no, int i, int j, int k)
                       {
                           const auto &tags_arr  = tag_arrs[box_no];
                           const auto &state_arr = state_new_arrs[box_no];
                           chi_tagger(i, j, k, tags_arr, state_arr);
                       });
    amrex::Gpu::streamSynchronize();
}

void BinaryWormholeLevel::specific_post_init()
{
    BL_PROFILE("BinaryWormholeLevel::specific_post_init");

    // AMReX builds the whole initial hierarchy and calls computeInitialDt
    // before post_init, so dtLevel(0) and the fine levels are both valid here.
    // Emitting the t = 0 row from this hook is what makes Phase 1 of
    // research/merger/Reference.md measurable at all - see the header comment.
    write_scalar_diagnostics();
}

// NOLINTNEXTLINE(readability-function-cognitive-complexity)
void BinaryWormholeLevel::write_scalar_diagnostics()
{
    BL_PROFILE("BinaryWormholeLevel::write_scalar_diagnostics");

    // ---- Constraint norms -------------------------------------------------
    if (simParams().calculate_constraint_norms && Level() == 0)
    {
        const amrex::Real time         = get_state_data(state_index).curTime();
        const amrex::Real dt           = parent->dtLevel(0);
        const amrex::Real restart_time = get_gramr_ptr()->get_restart_time();
        const bool first_step          = (time == 0.0);

        amrex::MultiFab &state_new = get_new_data(state_index);
        FillPatch(*this, state_new, 2, time, state_index, 0, state_new.nComp());

        amrex::MultiFab cst(state_new.boxArray(), state_new.DistributionMap(),
                            4, 0);
        cst.setVal(0.0);
        PhantomDecayPotential potential(
            simParams().wormhole_params.phantom_mass);
        ExoticScalarField<PhantomDecayPotential> exotic_scalar(
            potential, simParams().wormhole_params.support_strength);
        const auto dx = Geom().CellSizeArray();
        ConstraintsWithMatter<ExoticScalarField<PhantomDecayPotential>>
            my_constraints(exotic_scalar, dx[0], 1.0, 0, Interval(1, 3),
                           simParams().wormhole_params.grid_center, time);

        for (amrex::MFIter mfi(cst, amrex::TilingIfNotGPU()); mfi.isValid();
             ++mfi)
        {
            const amrex::Box &bx = mfi.validbox();
            const auto arr       = cst.array(mfi);
            const auto src_arr   = state_new.const_array(mfi);

            amrex::ParallelFor(bx,
                               [=] AMREX_GPU_DEVICE(int ix, int iy, int iz) noexcept
                               { my_constraints(ix, iy, iz, arr, src_arr); });
        }

        const amrex::Real cell_vol = dx[0] * dx[1] * dx[2];

        amrex::ReduceOps<amrex::ReduceOpSum, amrex::ReduceOpSum,
                         amrex::ReduceOpSum>
            reduce_ops;
        amrex::ReduceData<amrex::Real, amrex::Real, amrex::Real> reduce_data(
            reduce_ops);
        using ReduceTuple = typename decltype(reduce_data)::Type;

        for (amrex::MFIter mfi(cst, amrex::TilingIfNotGPU()); mfi.isValid();
             ++mfi)
        {
            const amrex::Box &bx = mfi.validbox();
            const auto arr       = cst.const_array(mfi);
            reduce_ops.eval(
                bx, reduce_data,
                [=] AMREX_GPU_DEVICE(int i, int j, int k) -> ReduceTuple
                {
                    const amrex::Real ham  = arr(i, j, k, 0);
                    const amrex::Real m1   = arr(i, j, k, 1);
                    const amrex::Real m2   = arr(i, j, k, 2);
                    const amrex::Real m3   = arr(i, j, k, 3);
                    const amrex::Real mom2 = (m1 * m1 + m2 * m2 + m3 * m3);
                    return {ham * ham * cell_vol, mom2 * cell_vol, cell_vol};
                });
        }

        auto [sum_ham2, sum_mom2, sum_vol] = reduce_data.value();
        amrex::ParallelDescriptor::ReduceRealSum(sum_ham2);
        amrex::ParallelDescriptor::ReduceRealSum(sum_mom2);
        amrex::ParallelDescriptor::ReduceRealSum(sum_vol);

        const double L2_Ham =
            (sum_vol > 0.0) ? std::sqrt(sum_ham2 / sum_vol) : 0.0;
        const double L2_Mom =
            (sum_vol > 0.0) ? std::sqrt(sum_mom2 / sum_vol) : 0.0;

        const std::string prefix = resolve_out_dir() + "constraint_norms";

        SmallDataIO constraints_file(prefix, dt, time, restart_time,
                                     SmallDataIO::APPEND, first_step);
        constraints_file.remove_duplicate_time_data();
        if (first_step)
        {
            constraints_file.write_header_line({"L2_Ham", "L2_Mom"});
        }
        constraints_file.write_time_data_line(
            std::vector<double>{L2_Ham, L2_Mom});
    }

    // ---- Global collapse diagnostics (single-centre, unchanged contract) ---
    // Column-for-column identical to Examples/SupportedWormholeCollapse so the
    // existing single-throat analysis scripts read it without modification.
    // Everything two-centre lives in binary_throat_diagnostics.dat instead.
    if (Level() == 0)
    {
        const amrex::Real time         = get_state_data(state_index).curTime();
        const amrex::Real dt           = parent->dtLevel(0);
        const amrex::Real restart_time = get_gramr_ptr()->get_restart_time();
        const bool first_step          = (time == 0.0);

        const int finest_lev        = parent->finestLevel();
        auto &fine_level            = parent->getLevel(finest_lev);
        amrex::MultiFab &state_fine = fine_level.get_new_data(state_index);
        const auto &fine_geom       = parent->Geom(finest_lev);

        FillPatch(fine_level, state_fine, 2, time, state_index, 0,
                  state_fine.nComp());

        {
            const auto &arrs = state_fine.arrays();
            TraceARemoval trace_A_removal;
            PositiveChiAndLapse positive_chi_lapse;
            amrex::ParallelFor(
                state_fine, amrex::IntVect(0),
                [=] AMREX_GPU_DEVICE(int box_no, int i, int j, int k)
                {
                    trace_A_removal(i, j, k, arrs[box_no]);
                    positive_chi_lapse(i, j, k, arrs[box_no]);
                });
            amrex::Gpu::streamSynchronize();
        }

        const auto prob_lo = fine_geom.ProbLoArray();
        const auto dx_arr  = fine_geom.CellSizeArray();

        const amrex::Real cx = simParams().wormhole_params.grid_center[0];
        const amrex::Real cy = simParams().wormhole_params.grid_center[1];
        const amrex::Real cz = simParams().wormhole_params.grid_center[2];

        amrex::ReduceOps<amrex::ReduceOpMin, amrex::ReduceOpMin,
                         amrex::ReduceOpMax, amrex::ReduceOpMax,
                         amrex::ReduceOpMin, amrex::ReduceOpMin,
                         amrex::ReduceOpMax, amrex::ReduceOpMin,
                         amrex::ReduceOpMax>
            reduce_ops;
        amrex::ReduceData<amrex::Real, amrex::Real, amrex::Real, amrex::Real,
                          amrex::Real, amrex::Real, amrex::Real, amrex::Real,
                          amrex::Real>
            reduce_data(reduce_ops);
        using ReduceTuple = typename decltype(reduce_data)::Type;

        for (amrex::MFIter mfi(state_fine, amrex::TilingIfNotGPU());
             mfi.isValid(); ++mfi)
        {
            const amrex::Box &bx = mfi.validbox();
            const auto arr       = state_fine.const_array(mfi);
            reduce_ops.eval(
                bx, reduce_data,
                [=] AMREX_GPU_DEVICE(int i, int j, int k) -> ReduceTuple
                {
                    const amrex::Real lapse = arr(i, j, k, c_lapse);
                    const amrex::Real chi   = arr(i, j, k, c_chi);
                    const amrex::Real K     = arr(i, j, k, c_K);

                    const amrex::Real x =
                        prob_lo[0] + (amrex::Real(i) + 0.5) * dx_arr[0] - cx;
                    const amrex::Real y =
                        prob_lo[1] + (amrex::Real(j) + 0.5) * dx_arr[1] - cy;
                    const amrex::Real z =
                        prob_lo[2] + (amrex::Real(k) + 0.5) * dx_arr[2] - cz;
                    const amrex::Real r2 = x * x + y * y + z * z;
                    const amrex::Real r  = std::sqrt(r2);

                    amrex::Real ah_radius            = 0.0;
                    amrex::Real theta_plus_min_proxy = 1.0e30;
                    if (r > 1e-6)
                    {
                        const amrex::Real A11 = arr(i, j, k, c_A11);
                        const amrex::Real A22 = arr(i, j, k, c_A22);
                        const amrex::Real A33 = arr(i, j, k, c_A33);
                        const amrex::Real A12 = arr(i, j, k, c_A12);
                        const amrex::Real A13 = arr(i, j, k, c_A13);
                        const amrex::Real A23 = arr(i, j, k, c_A23);

                        const amrex::Real Arr =
                            (A11 * x * x + A22 * y * y + A33 * z * z +
                             2.0 * A12 * x * y + 2.0 * A13 * x * z +
                             2.0 * A23 * y * z) /
                            r2;

                        const amrex::Real dx_chi =
                            (arr(i + 1, j, k, c_chi) -
                             arr(i - 1, j, k, c_chi)) /
                            (2.0 * dx_arr[0]);
                        const amrex::Real dy_chi =
                            (arr(i, j + 1, k, c_chi) -
                             arr(i, j - 1, k, c_chi)) /
                            (2.0 * dx_arr[1]);
                        const amrex::Real dz_chi =
                            (arr(i, j, k + 1, c_chi) -
                             arr(i, j, k - 1, c_chi)) /
                            (2.0 * dx_arr[2]);
                        const amrex::Real dchi_dr =
                            (x * dx_chi + y * dy_chi + z * dz_chi) / r;
                        const amrex::Real sqrt_chi =
                            std::sqrt(amrex::max(chi, amrex::Real(1.0e-20)));

                        const amrex::Real theta_plus =
                            2.0 * sqrt_chi / r - dchi_dr / sqrt_chi + Arr -
                            (2.0 / 3.0) * K;
                        theta_plus_min_proxy = theta_plus;

                        if (theta_plus <= 0.0)
                        {
                            ah_radius = r;
                        }
                    }

                    const amrex::Real sf_phi = arr(i, j, k, c_phi);
                    const amrex::Real sf_Pi  = arr(i, j, k, c_Pi);

                    return {lapse,  chi,    amrex::Math::abs(K),
                            ah_radius, theta_plus_min_proxy,
                            sf_phi, sf_phi, sf_Pi, sf_Pi};
                });
        }

        const auto reduce_vals     = reduce_data.value();
        amrex::Real min_lapse      = amrex::get<0>(reduce_vals);
        amrex::Real min_chi        = amrex::get<1>(reduce_vals);
        amrex::Real max_abs_K      = amrex::get<2>(reduce_vals);
        amrex::Real max_ah_r       = amrex::get<3>(reduce_vals);
        amrex::Real min_theta_plus = amrex::get<4>(reduce_vals);
        amrex::Real min_phi        = amrex::get<5>(reduce_vals);
        amrex::Real max_phi        = amrex::get<6>(reduce_vals);
        amrex::Real min_Pi         = amrex::get<7>(reduce_vals);
        amrex::Real max_Pi         = amrex::get<8>(reduce_vals);
        amrex::ParallelDescriptor::ReduceRealMin(min_lapse);
        amrex::ParallelDescriptor::ReduceRealMin(min_chi);
        amrex::ParallelDescriptor::ReduceRealMax(max_abs_K);
        amrex::ParallelDescriptor::ReduceRealMax(max_ah_r);
        amrex::ParallelDescriptor::ReduceRealMin(min_theta_plus);
        amrex::ParallelDescriptor::ReduceRealMin(min_phi);
        amrex::ParallelDescriptor::ReduceRealMax(max_phi);
        amrex::ParallelDescriptor::ReduceRealMin(min_Pi);
        amrex::ParallelDescriptor::ReduceRealMax(max_Pi);

        const amrex::Real tol =
            amrex::max(amrex::Real(1.0e-14),
                       amrex::Real(1.0e-12) * amrex::Math::abs(min_lapse));

        amrex::ReduceOps<amrex::ReduceOpSum, amrex::ReduceOpSum,
                         amrex::ReduceOpSum, amrex::ReduceOpSum>
            reduce_ops_loc;
        amrex::ReduceData<amrex::Real, amrex::Real, amrex::Real, amrex::Real>
            reduce_data_loc(reduce_ops_loc);
        using ReduceTupleLoc = typename decltype(reduce_data_loc)::Type;

        for (amrex::MFIter mfi(state_fine, amrex::TilingIfNotGPU());
             mfi.isValid(); ++mfi)
        {
            const amrex::Box &bx = mfi.validbox();
            const auto arr       = state_fine.const_array(mfi);
            reduce_ops_loc.eval(
                bx, reduce_data_loc,
                [=] AMREX_GPU_DEVICE(int i, int j, int k) -> ReduceTupleLoc
                {
                    const amrex::Real lapse = arr(i, j, k, c_lapse);
                    const bool is_min =
                        (amrex::Math::abs(lapse - min_lapse) <= tol);
                    if (!is_min)
                    {
                        return {0.0, 0.0, 0.0, 0.0};
                    }
                    const amrex::Real x =
                        prob_lo[0] + (amrex::Real(i) + 0.5) * dx_arr[0] - cx;
                    const amrex::Real y =
                        prob_lo[1] + (amrex::Real(j) + 0.5) * dx_arr[1] - cy;
                    const amrex::Real z =
                        prob_lo[2] + (amrex::Real(k) + 0.5) * dx_arr[2] - cz;
                    return {x, y, z, 1.0};
                });
        }

        auto [sum_x, sum_y, sum_z, count] = reduce_data_loc.value();
        amrex::ParallelDescriptor::ReduceRealSum(sum_x);
        amrex::ParallelDescriptor::ReduceRealSum(sum_y);
        amrex::ParallelDescriptor::ReduceRealSum(sum_z);
        amrex::ParallelDescriptor::ReduceRealSum(count);

        const amrex::Real min_lapse_x = (count > 0.0) ? (sum_x / count) : 0.0;
        const amrex::Real min_lapse_y = (count > 0.0) ? (sum_y / count) : 0.0;
        const amrex::Real min_lapse_z = (count > 0.0) ? (sum_z / count) : 0.0;

        const std::string out_dir = resolve_out_dir();
        const std::string prefix  = out_dir + "collapse_diagnostics";
        SmallDataIO diag_file(prefix, dt, time, restart_time,
                              SmallDataIO::APPEND, first_step);
        diag_file.remove_duplicate_time_data();
        if (first_step)
        {
            diag_file.write_header_line({"min_lapse", "min_chi", "max_abs_K",
                                         "min_lapse_x", "min_lapse_y",
                                         "min_lapse_z", "min_phi", "max_phi",
                                         "min_Pi", "max_Pi"});
        }
        diag_file.write_time_data_line(std::vector<double>{
            static_cast<double>(min_lapse), static_cast<double>(min_chi),
            static_cast<double>(max_abs_K), static_cast<double>(min_lapse_x),
            static_cast<double>(min_lapse_y), static_cast<double>(min_lapse_z),
            static_cast<double>(min_phi), static_cast<double>(max_phi),
            static_cast<double>(min_Pi), static_cast<double>(max_Pi)});

        // ---- Two-centre throat diagnostics (own file, own switch) ---------
        if (simParams().binary_diag_params.enabled)
        {
            BinaryThroatDiagnostics::execute(
                state_fine, fine_geom, simParams().binary_diag_params, out_dir,
                dt, time, restart_time, first_step);
        }

        // ---- Throat tracking (own module, own file, own switch) -----------
        // Updates s_throat_centers in place, which is what the moving-box
        // tagger (tagging_type = 2) reads at the next regrid.  state_fine has
        // already been FillPatched and sanitised above.
        if (simParams().throat_tracker_params.enabled)
        {
            const std::array<bool, 2> present = {
                simParams().wormhole_params.b0_A > 0.0,
                simParams().wormhole_params.b0_B > 0.0};
            ThroatTracker::execute(state_fine, fine_geom,
                                   simParams().throat_tracker_params, present,
                                   s_throat_centers, out_dir, dt, time,
                                   restart_time, first_step);
        }
    }
}

void BinaryWormholeLevel::specificPostTimeStep()
{
    BL_PROFILE("BinaryWormholeLevel::specificPostTimeStep");

    write_scalar_diagnostics();

    // ---- In-code Weyl4 / Psi4 spherical-harmonic extraction ---------------
    // SphericalExtraction interpolates the "Weyl4" derived variable onto the
    // configured extraction spheres and writes the requested (l,m) time series
    // every coarse step, decoupled from the plotfile cadence.
    if (simParams().activate_extraction)
    {
        const int min_level =
            simParams().extraction_params.min_extraction_level();
        const bool calculate_weyl = at_level_timestep_multiple(min_level);

        if (calculate_weyl && Level() == min_level)
        {
            const amrex::Real m_time = get_state_data(state_index).curTime();
            const amrex::Real m_dt   = get_gramr_ptr()->dtLevel(Level());
            const amrex::Real restart_time =
                get_gramr_ptr()->get_restart_time();
            const bool first_step = (m_time <= m_dt);

            WeylExtraction my_extraction(simParams().extraction_params, m_dt,
                                         m_time, first_step, restart_time);
            my_extraction.execute_query(&get_bhamr_ptr()->m_weyl_interpolator);
        }
    }
}
