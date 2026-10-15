#ifndef SPONGEDRIVE_HPP_
#define SPONGEDRIVE_HPP_

#include <AMReX_Array4.H>
#include <AMReX_REAL.H>
#include <array>
#include <cmath>

/// Damping sponge: drive the state back to the stationary background in the
/// outer shell.
///
/// The existing SpongeZone adds extra Kreiss-Oliger dissipation, which damps
/// at (k dx)^6 and is nearly transparent to the long-wavelength gauge pulse;
/// the Sommerfeld boundary then assumes flat asymptotics the wormhole does
/// not have (M_ADM ~ 2 at the box edge), and the pulse returns at t ~ L.
/// This operator absorbs ALL wavelengths by adding, inside the same shell
/// and with the same ramp profile as the sponge,
///
///   rhs_n -= A * f(r) * (state_n - ref_n)        for every component n,
///
/// where ref is the run's own t = 0 background (table data + InitialGammas,
/// rebuilt exactly on restart or regrid).  For a hold around a stationary
/// solution this is the physical statement that the far zone stays the
/// background.  A = 0 reproduces the old evolution bit for bit.  Explicit
/// stability needs A * dt < ~1; the quartic ramp keeps the drive smooth at
/// the inner edge.  2026-10-15: every L64 trust window died at the t ~ 62
/// boundary return and L128 would die at t ~ 120, which walls off the
/// late-time hold physics.
struct SpongeDrive
{
    bool enabled{false};
    double inner_radius{};
    double inv_width{};
    double strength{}; //!< A: inverse damping time at full ramp
    int ramp_power{};
    double dx{};
    std::array<double, AMREX_SPACEDIM> center{};

    AMREX_GPU_DEVICE AMREX_FORCE_INLINE void
    apply(int i, int j, int k, const amrex::Array4<amrex::Real> &rhs,
          const amrex::Array4<amrex::Real const> &state,
          const amrex::Array4<amrex::Real const> &ref) const
    {
        if (!enabled)
        {
            return;
        }

        double x = (static_cast<double>(i) + 0.5) * dx - center[0];
        double y = (static_cast<double>(j) + 0.5) * dx - center[1];
        double z = (static_cast<double>(k) + 0.5) * dx - center[2];
        double r = std::sqrt(x * x + y * y + z * z);

        if (r <= inner_radius)
        {
            return;
        }

        double s = (r - inner_radius) * inv_width;
        if (s > 1.0)
        {
            s = 1.0;
        }
        double damp = strength * std::pow(s, ramp_power);

        const int ncomp = rhs.nComp();
        for (int n = 0; n < ncomp; ++n)
        {
            rhs(i, j, k, n) -= damp * (state(i, j, k, n) - ref(i, j, k, n));
        }
    }
};

#endif /* SPONGEDRIVE_HPP_ */
