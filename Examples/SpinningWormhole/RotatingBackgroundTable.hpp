/* RotatingBackgroundTable
 * Loads a .spinbg table of a rotating Ellis-Bronnikov background and
 * bilinear-interpolates it on the GPU.
 *
 * The table is 2D: the solutions are stationary and axisymmetric, so the
 * metric functions depend on (eta, theta) only.  The file stores them on a
 * uniform grid in
 *
 *     x  = (2/pi) atan(eta / eta0)   in [x_min, x_max]   (compactifies BOTH
 *                                      asymptotic ends: x -> +-1),
 *     mu = cos(theta)                in [0, 1]           (equatorial
 *                                      reflection symmetry).
 *
 * Components, by name (the header must list exactly these six):
 *     f        metric function: alpha = e^{f/2}, g_tt sector
 *     nu_bar   nu / sin^2(theta)  -- regular on the axis, exactly 0 when
 *              static; nu is the Kleihaus-Kunz quasi-isotropic function
 *     omega    frame dragging: beta^phi = -omega
 *     domega_deta                      d(omega)/d(eta)
 *     domega_dtheta_over_sintheta      d(omega)/d(theta) / sin(theta)
 *     phi      the phantom scalar, with its eta -> +infinity asymptote
 *              already subtracted
 *
 * Derivatives are stored, not recomputed here, so a spectral generator hands
 * over exact ones.  Under mu -> -mu every component is even except
 * domega_dtheta_over_sintheta, which is odd; sample() applies the parity.
 *
 * Header: text lines "key value ...", terminated by END_HEADER; body:
 * float64[n_mu][n_x][ncomp], C order (same conventions as .gridinit files).
 * The heavy data lives in AMReX managed memory so that sampling works on
 * both CPU and GPU builds.
 */

#ifndef ROTATINGBACKGROUNDTABLE_HPP_
#define ROTATINGBACKGROUNDTABLE_HPP_

#include <AMReX_GpuMemory.H>
#include <AMReX_Print.H>
#include <AMReX_REAL.H>

#include <array>
#include <cmath>
#include <fstream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

class RotatingBackgroundTable
{
  public:
    static constexpr int NCOMP = 6;

    //! One sampled point of the background.
    struct Sample
    {
        double f{};
        double nu_bar{};
        double omega{};
        double domega_deta{};
        double domega_dtheta_over_sintheta{};
        double phi{};
    };

    //! Trivially copyable view captured by GPU kernels.
    struct View
    {
        const double *data{nullptr};
        int n_x{0};
        int n_mu{0};
        double x_min{0.0};
        double x_max{1.0};
        double eta0{1.0};

        //! Bilinear sample at compactified radius a_x and SIGNED a_mu
        //! (= cos theta); the mu grid covers [0, 1] and parity supplies the
        //! southern hemisphere.
        AMREX_GPU_DEVICE AMREX_FORCE_INLINE void sample(double a_x,
                                                        double a_mu,
                                                        Sample &out) const
        {
            const double mu_abs  = std::abs(a_mu);
            const double mu_sign = (a_mu < 0.0) ? -1.0 : 1.0;

            const double fx =
                (a_x - x_min) / (x_max - x_min) * (n_x - 1);
            const double fm = mu_abs * (n_mu - 1);

            const int i0 = amrex::max(0, amrex::min(int(fx), n_x - 2));
            const int j0 = amrex::max(0, amrex::min(int(fm), n_mu - 2));
            const double wx = amrex::max(0.0, amrex::min(1.0, fx - i0));
            const double wm = amrex::max(0.0, amrex::min(1.0, fm - j0));

            double vals[NCOMP];
            for (int c = 0; c < NCOMP; ++c)
            {
                const double v00 = data[flat(j0, i0, c)];
                const double v10 = data[flat(j0, i0 + 1, c)];
                const double v01 = data[flat(j0 + 1, i0, c)];
                const double v11 = data[flat(j0 + 1, i0 + 1, c)];
                vals[c] = v00 * (1 - wx) * (1 - wm) + v10 * wx * (1 - wm) +
                          v01 * (1 - wx) * wm + v11 * wx * wm;
            }

            out.f           = vals[0];
            out.nu_bar      = vals[1];
            out.omega       = vals[2];
            out.domega_deta = vals[3];
            // Odd under mu -> -mu (d/dtheta flips across the equator while
            // sin(theta) does not).
            out.domega_dtheta_over_sintheta = mu_sign * vals[4];
            out.phi                         = vals[5];
        }

        AMREX_GPU_DEVICE AMREX_FORCE_INLINE long flat(int j, int i,
                                                      int c) const
        {
            return (static_cast<long>(j) * n_x + i) * NCOMP + c;
        }
    };

    explicit RotatingBackgroundTable(const std::string &a_path)
    {
        load(a_path);
    }

    [[nodiscard]] const View &view() const { return m_view; }
    [[nodiscard]] double eta0() const { return m_view.eta0; }

  private:
    View m_view{};
    std::shared_ptr<double> m_managed;

    void load(const std::string &path)
    {
        std::ifstream fin(path, std::ios::binary);
        if (!fin.is_open())
        {
            throw std::runtime_error("RotatingBackgroundTable: cannot open " +
                                     path);
        }

        std::string line;
        std::getline(fin, line);
        if (line != "SPINBG_V1")
        {
            throw std::runtime_error(
                "RotatingBackgroundTable: " + path +
                " does not start with SPINBG_V1 (got '" + line + "')");
        }

        int ncomp = 0;
        std::vector<std::string> comp_names;
        bool have_eta0 = false;
        while (std::getline(fin, line))
        {
            if (line == "END_HEADER")
            {
                break;
            }
            std::istringstream iss(line);
            std::string key;
            iss >> key;
            if (key == "eta0")
            {
                iss >> m_view.eta0;
                have_eta0 = true;
            }
            else if (key == "n_x")
            {
                iss >> m_view.n_x;
            }
            else if (key == "n_mu")
            {
                iss >> m_view.n_mu;
            }
            else if (key == "x_min")
            {
                iss >> m_view.x_min;
            }
            else if (key == "x_max")
            {
                iss >> m_view.x_max;
            }
            else if (key == "num_components")
            {
                iss >> ncomp;
            }
            else if (key == "component_names")
            {
                std::string name;
                while (iss >> name)
                {
                    comp_names.push_back(name);
                }
            }
            // "meta ..." and unknown keys are documentation; skip them.
        }

        // The component layout is a fixed contract: refuse anything else
        // rather than guess a remap (a silently permuted table would evolve
        // plausibly and wrongly).
        const std::array<std::string, NCOMP> expected = {
            "f",           "nu_bar",
            "omega",       "domega_deta",
            "domega_dtheta_over_sintheta", "phi"};
        if (ncomp != NCOMP ||
            comp_names.size() != static_cast<std::size_t>(NCOMP))
        {
            throw std::runtime_error(
                "RotatingBackgroundTable: " + path + " declares " +
                std::to_string(ncomp) + " components with " +
                std::to_string(comp_names.size()) +
                " names; exactly 6 named components are required");
        }
        for (int c = 0; c < NCOMP; ++c)
        {
            if (comp_names[c] != expected[c])
            {
                throw std::runtime_error(
                    "RotatingBackgroundTable: " + path + " component " +
                    std::to_string(c) + " is '" + comp_names[c] +
                    "', expected '" + expected[c] + "'");
            }
        }
        if (!have_eta0 || m_view.eta0 <= 0.0 || m_view.n_x < 2 ||
            m_view.n_mu < 2 || !(m_view.x_max > m_view.x_min))
        {
            throw std::runtime_error(
                "RotatingBackgroundTable: invalid header in " + path);
        }

        const long total =
            static_cast<long>(m_view.n_mu) * m_view.n_x * NCOMP;
        double *raw = static_cast<double *>(amrex::The_Managed_Arena()->alloc(
            static_cast<std::size_t>(total) * sizeof(double)));
        m_managed = std::shared_ptr<double>(
            raw, [](double *p) { amrex::The_Managed_Arena()->free(p); });
        m_view.data = raw;

        fin.read(reinterpret_cast<char *>(raw),
                 static_cast<std::streamsize>(total * sizeof(double)));
        if (!fin)
        {
            throw std::runtime_error(
                "RotatingBackgroundTable: failed to read " +
                std::to_string(total) + " float64 values from " + path);
        }

        amrex::Print() << "RotatingBackgroundTable: loaded " << path
                       << " (eta0 " << m_view.eta0 << ", " << m_view.n_x
                       << " x-points in [" << m_view.x_min << ", "
                       << m_view.x_max << "], " << m_view.n_mu
                       << " mu-points)\n";
    }
};

#endif /* ROTATINGBACKGROUNDTABLE_HPP_ */
