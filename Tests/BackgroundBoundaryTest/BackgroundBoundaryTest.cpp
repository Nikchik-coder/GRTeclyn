#include "BackgroundBoundaryTest.hpp"
#include "BoundaryConditions.hpp"
#include "doctest.h"
#include "doctestCLIArgs.hpp"

#include <AMReX.H>
#include <AMReX_Gpu.H>
#include <cmath>

namespace
{
class ManufacturedBoundary : public BoundaryConditions
{
  public:
    explicit ManufacturedBoundary(const amrex::Geometry &geometry)
    {
        m_geom = geometry;
        m_num_ghosts = 4;
        m_center = amrex::RealVect(8.0);
        m_params.lo_condition.fill(SOMMERFELD_BC);
        m_params.hi_condition.fill(SOMMERFELD_BC);
        m_params.is_periodic.fill(false);
    }
};
}

void run_background_boundary_test()
{
    int argc = doctest::cli_args.argc();
    char **argv = doctest::cli_args.argv();
    amrex::Initialize(argc, argv);
    {
        const amrex::Box domain(amrex::IntVect(0), amrex::IntVect(15));
        const amrex::RealBox real_box(0., 0., 0., 16., 16., 16.);
        const amrex::Geometry geometry(domain, &real_box, 0);
        amrex::BoxArray boxes(domain);
        boxes.maxSize(8);
        const amrex::DistributionMapping dm(boxes);
        amrex::MFInfo info;
        info.SetArena(amrex::The_Managed_Arena());
        amrex::MultiFab reference(boxes, dm, NUM_VARS, 4, info);
        amrex::MultiFab derivative(boxes, dm, NUM_VARS, 4, info);
        amrex::MultiFab solution(boxes, dm, NUM_VARS, 4, info);
        amrex::MultiFab rhs(boxes, dm, NUM_VARS, 0, info);
        const auto &ref = reference.arrays();
        const auto &dt = derivative.arrays();
        const double omega = .708, time = 1.2;
        const double co = std::cos(omega*time), si = std::sin(omega*time);
        amrex::ParallelFor(reference, reference.nGrowVect(), NUM_VARS,
            [=] AMREX_GPU_DEVICE(int b, int i, int j, int k, int n)
            {
                const double amplitude = 1.+.01*i+.02*j+.03*k+.001*n;
                const bool real = n%2 == 0;
                ref[b](i,j,k,n) = amplitude*(real ? co : si);
                dt[b](i,j,k,n) = omega*amplitude*(real ? -si : co);
            });
        ManufacturedBoundary boundary(geometry);
        for (int experiment = 0; experiment < 3; ++experiment)
        {
            const double delta = experiment == 2 ? .125 : 0.;
            amrex::MultiFab::Copy(solution, reference, 0, 0, NUM_VARS, 4);
            if (delta != 0.) solution.plus(delta, 0, NUM_VARS, 4);
            rhs.setVal(123.);
            boundary.apply_sommerfeld_boundaries(rhs, solution, &reference,
                experiment == 0 ? nullptr : &derivative);
            amrex::Gpu::streamSynchronize();
            for (amrex::MFIter mfi(rhs); mfi.isValid(); ++mfi)
            {
                const auto actual = rhs.const_array(mfi);
                const auto expected_dt = derivative.const_array(mfi);
                amrex::LoopOnCpu(mfi.validbox(), [&](int i, int j, int k)
                {
                    const bool edge = i<4 || i>=12 || j<4 || j>=12 || k<4 || k>=12;
                    const double radius = std::sqrt(std::pow(i+.5-8.,2)+
                        std::pow(j+.5-8.,2)+std::pow(k+.5-8.,2));
                    for (int n = 0; n < NUM_VARS; ++n)
                    {
                        double expected = 123.;
                        if (edge) expected = (experiment == 0 ? 0. : expected_dt(i,j,k,n))-delta/radius;
                        CHECK(actual(i,j,k,n) == doctest::Approx(expected).epsilon(1e-12));
                    }
                });
            }
        }
    }
    amrex::Finalize();
}
