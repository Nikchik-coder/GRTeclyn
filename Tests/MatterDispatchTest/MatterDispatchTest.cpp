#include "MatterDispatchTest.hpp"
#include "AlgebraicConstraintsEnforcer.hpp"
#include "CCZ4RHSWithMatter.hpp"
#include "ConstraintsWithMatter.hpp"
#include "MatterDispatch.hpp"
#include "MovingPunctureGauge.hpp"
#include "doctest.h"
#include "doctestCLIArgs.hpp"
#include <AMReX.H>
#include <AMReX_FArrayBox.H>

namespace
{
// A prescribed source makes the 8 pi G factors independently checkable.
struct TimedMatter
{
    using Vars = CCZ4Vars;
    template <class deriv_t>
    AMREX_GPU_DEVICE emtensor_t
    compute_emtensor(int, int, int, const amrex::Array4<const amrex::Real> &,
                     const deriv_t &, const Tensor::Rank2 &,
                     const Coordinates &, amrex::Real time) const
    {
        emtensor_t em;
        em.rho  = 2.0 + time;
        em.trS  = 3.0;
        em.j(0) = 0.25;
        FOR (i)
        {
            em.S(i, i) = 1.0;
        }
        return em;
    }
    template <class deriv_t>
    AMREX_GPU_DEVICE void
    add_matter_rhs(int i, int j, int k, const amrex::Array4<amrex::Real> &rhs,
                   const amrex::Array4<const amrex::Real> &, const deriv_t &,
                   const Coordinates &, amrex::Real time) const
    {
        rhs(i, j, k, c_phi) = time;
    }
};
struct CoupledMatter : TimedMatter
{
    template <class deriv_t>
    AMREX_GPU_DEVICE einstein_sources_t compute_einstein_sources(
        int, int, int, const amrex::Array4<const amrex::Real> &,
        const deriv_t &, const Tensor::Rank2 &) const
    {
        einstein_sources_t source;
        source.rho = 7.0;
        return source;
    }
};
} // namespace

void run_matter_dispatch_test()
{
    int argc    = doctest::cli_args.argc();
    char **argv = doctest::cli_args.argv();
    amrex::Initialize(argc, argv);
    {
        GRParmParse pp;
        pp.add("ccz4.formulation", 0);
        pp.add("ccz4.kappa1", 0.0);
        pp.add("ccz4.kappa2", 0.0);
        pp.add("ccz4.kappa3", 0.0);
        pp.add("ccz4.covariantZ4", true);
        pp.add("evolution.sigma", 0.0);
        pp.add("gauge.lapse_advec_coeff", 1.0);
        pp.add("gauge.lapse_power", 1.0);
        pp.add("gauge.lapse_coeff", 2.0);
        pp.add("gauge.lapse_shock_kappa", 0.25);
        pp.add("gauge.shift_Gamma_coeff", 0.75);
        pp.add("gauge.shift_advec_coeff", 0.0);
        pp.add("gauge.eta", 1.0);
        amrex::Box point(amrex::IntVect(0), amrex::IntVect(0));
        amrex::Box ghost = amrex::grow(point, 3);
        amrex::FArrayBox state(ghost, NUM_VARS, amrex::The_Managed_Arena());
        amrex::FArrayBox out(point, NUM_VARS, amrex::The_Managed_Arena());
        amrex::FArrayBox checks(point, 8, amrex::The_Managed_Arena());
        const auto a = state.array();
        const auto r = out.array();
        const auto c = checks.array();
        amrex::ParallelFor(ghost,
                           [=] AMREX_GPU_DEVICE(int i, int j, int k)
                           {
                               for (int n = 0; n < NUM_VARS; ++n)
                               {
                                   a(i, j, k, n) = 0.0;
                               }
                               a(i, j, k, c_chi) = a(i, j, k, c_lapse) = 1.0;
                               a(i, j, k, c_h11)     = a(i, j, k, c_h22) =
                                   a(i, j, k, c_h33) = 1.0;
                           });
        const auto src = state.const_array();
        const MovingPunctureGauge<> gauge(1.0);
        const CCZ4RHSWithMatter<TimedMatter> rhs(TimedMatter(), 1.0, 1.0, {},
                                                 0.5);
        const ConstraintsWithMatter<TimedMatter> constraints(
            TimedMatter(), 1.0, 1.0, 0, Interval(1, 3), {}, 0.5);
        const AlgebraicConstraintsEnforcer full;
        const AlgebraicConstraintsEnforcer trace_only(false);
        amrex::ParallelFor(
            point,
            [=] AMREX_GPU_DEVICE(int i, int j, int k)
            {
                rhs.compute_full_rhs(i, j, k, r, src, gauge);
                constraints(i, j, k, c, src);
                const Coordinates coords(amrex::IntVect(i, j, k), 1.0, {});
                const FourthOrderDerivatives deriv(1.0);
                const Tensor::Rank2 inv = CCZ4Geometry::compute_inverse_metric(
                    CCZ4Vars(src.cellData(i, j, k)));
                c(i, j, k, 4) = MatterDispatch::compute_einstein_sources(
                                    CoupledMatter(), i, j, k, src, deriv, inv,
                                    coords, 0.5, 2.0, true)
                                    .rho;
                c(i, j, k, 5) = MatterDispatch::compute_einstein_sources(
                                    CoupledMatter(), i, j, k, src, deriv, inv,
                                    coords, 0.5, 2.0, false)
                                    .rho;
                a(i, j, k, c_h11) = a(i, j, k, c_h22) = a(i, j, k, c_h33) = 2.0;
                trace_only(i, j, k, a);
                c(i, j, k, 6) = a(i, j, k, c_h11);
                full(i, j, k, a);
                c(i, j, k, 7) = a(i, j, k, c_h11);
            });
        amrex::Gpu::streamSynchronize();
        CHECK(r(0, 0, 0, c_K) == doctest::Approx(-18.0 * M_PI));
        CHECK(r(0, 0, 0, c_Theta) == doctest::Approx(-20.0 * M_PI));
        CHECK(r(0, 0, 0, c_Gamma1) == doctest::Approx(-4.0 * M_PI));
        CHECK(r(0, 0, 0, c_B1) == doctest::Approx(-4.0 * M_PI));
        CHECK(r(0, 0, 0, c_phi) == doctest::Approx(0.5));
        CHECK(r(0, 0, 0, c_Pi) == 0.0);
        CHECK(c(0, 0, 0, 0) == doctest::Approx(-40.0 * M_PI));
        CHECK(c(0, 0, 0, 1) == doctest::Approx(-2.0 * M_PI));
        CHECK(c(0, 0, 0, 4) == 7.0);
        CHECK(c(0, 0, 0, 5) == doctest::Approx(40.0 * M_PI));
        CHECK(c(0, 0, 0, 6) == 2.0);
        CHECK(c(0, 0, 0, 7) == doctest::Approx(1.0));
        amrex::ParallelFor(point,
                           [=] AMREX_GPU_DEVICE(int i, int j, int k)
                           {
                               a(i, j, k, c_K) = 2.0;
                               gauge.calculate_rhs(i, j, k, r, src);
                           });
        amrex::Gpu::streamSynchronize();
        CHECK(r(0, 0, 0, c_lapse) == doctest::Approx(-4.5));
    }
    amrex::Finalize();
}
