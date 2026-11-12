#include "MatterDispatchTest.hpp"
#include "ScalarField.hpp"
#include "Weyl4WithMatter.hpp"
#include "doctest.h"
#include "doctestCLIArgs.hpp"
#include <AMReX.H>
#include <AMReX_MFIter.H>

namespace
{
struct AnisotropicTimedMatter
{
    using Vars = CCZ4Vars;
    template <class deriv_t>
    AMREX_GPU_DEVICE emtensor_t
    compute_emtensor(int, int, int, const amrex::Array4<const amrex::Real> &,
                     const deriv_t &, const Tensor::Rank2 &,
                     const Coordinates &, amrex::Real time) const
    {
        emtensor_t em;
        em.S(0, 0) = 2.0 * (1.0 + time);
        em.S(1, 1) = 1.0 + time;
        em.S(2, 2) = 3.0 * (1.0 + time);
        em.S(1, 2) = em.S(2, 1) = 0.25 * (1.0 + time);
        em.trS                  = 6.0 * (1.0 + time);
        return em;
    }
};

template <class matter_t>
void check_callback(amrex::MultiFab &out, const amrex::MultiFab &state,
                    const amrex::Geometry &geom, amrex::Real time,
                    amrex::Real expected_re, amrex::Real expected_im)
{
    out.setVal(12345.0);
    Weyl4WithMatter<matter_t>::compute_mf(out, 1, 2, state, geom, time, nullptr,
                                          0);
    amrex::Gpu::streamSynchronize();
    for (amrex::MFIter mfi(out); mfi.isValid(); ++mfi)
    {
        const auto a = out.const_array(mfi);
        // The valid cell and two ghost cells lie on the positive x axis.
        // Flat-space tetrad: u=x, v=y, w=-z. Hence, with B=0,
        // Re(Psi4)=(Ezz-Eyy)/2 and Im(Psi4)=Ezy, E=-4*pi*G*STF(S).
        for (int i = -1; i <= 1; ++i)
        {
            CAPTURE(i);
            CHECK(a(i, 0, 0, 1) == doctest::Approx(expected_re).epsilon(1e-12));
            CHECK(a(i, 0, 0, 2) == doctest::Approx(expected_im).epsilon(1e-12));
            CHECK(a(i, 0, 0, 0) == 12345.0);
            CHECK(a(i, 0, 0, 3) == 12345.0);
        }
    }
}
} // namespace

void run_weyl_matter_coupling_test()
{
    int argc    = doctest::cli_args.argc();
    char **argv = doctest::cli_args.argv();
    amrex::Initialize(argc, argv);
    {
        GRParmParse pp;
        pp.add("ccz4.formulation", 0);
        std::array<amrex::Real, 3> center{-3.0, 0.5, 0.5};
        pp.queryAdd("weyl_extraction.center", center);
        const amrex::Box box(amrex::IntVect(0), amrex::IntVect(0));
        const amrex::BoxArray boxes(box);
        const amrex::DistributionMapping mapping(boxes);
        const amrex::RealVect dx(1.0);
        const amrex::RealBox real_box(box, dx.dataPtr(),
                                      amrex::RealVect::Zero.dataPtr());
        const amrex::Geometry geom(box, &real_box, 0);
        amrex::MFInfo info;
        info.SetArena(amrex::The_Managed_Arena());
        amrex::MultiFab state(boxes, mapping, NUM_VARS, 3, info);
        amrex::MultiFab out(boxes, mapping, 4, 1, info);
        const auto arrays = state.arrays();
        amrex::ParallelFor(state, state.nGrowVect(),
                           [=] AMREX_GPU_DEVICE(int b, int i, int j, int k)
                           {
                               const auto a = arrays[b];
                               for (int n = 0; n < NUM_VARS; ++n)
                                   a(i, j, k, n) = 0.0;
                               a(i, j, k, c_chi) = a(i, j, k, c_lapse) = 1.0;
                               a(i, j, k, c_h11)     = a(i, j, k, c_h22) =
                                   a(i, j, k, c_h33) = 1.0;
                               // Linear phi has exact fourth-order derivatives
                               // (0,1,2).
                               a(i, j, k, c_phi) = j + 2.0 * k;
                           });

        // No global G: research fallback must be G=1, not the old zero.
        check_callback<AnisotropicTimedMatter>(out, state, geom, 0.5,
                                               -6.0 * M_PI, -1.5 * M_PI);
        // Native source already contains 8*pi*G. For this scalar gradient,
        // Szz-Syy=3 and Szy=2; no second coupling factor may be applied.
        pp.add("scalar_field.G_Newton", 0.3);
        check_callback<ScalarField<>>(out, state, geom, 0.0, -1.8 * M_PI,
                                      -2.4 * M_PI);
        // Explicit research coupling overrides the native setting once.
        pp.add("G_Newton", 2.0);
        check_callback<AnisotropicTimedMatter>(out, state, geom, 1.5,
                                               -20.0 * M_PI, -5.0 * M_PI);
        check_callback<ScalarField<>>(out, state, geom, 0.0, -12.0 * M_PI,
                                      -16.0 * M_PI);
        pp.add("G_Newton", 0.0);
        check_callback<AnisotropicTimedMatter>(out, state, geom, 0.5, 0.0, 0.0);
    }
    amrex::Finalize();
}
