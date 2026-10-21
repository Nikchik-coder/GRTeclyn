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
 * Interpolation: a C2 tensor-product cubic spline by default.  The bilinear
 * sample is continuous but kinked at every table line, so finite-difference
 * second derivatives of the initial data (the constraints, Gamma^i) grow as
 * the grid refines (measured order -0.8 to -2.8 for f and nu_bar); with the
 * spline the same check converges at order +4.  Not-a-knot ends in x; in mu
 * the column is mirrored through the equator with each component's parity,
 * so mu = 0 needs no end condition, and the axis (mu = 1) is not-a-knot.
 * spinning_background_interp = 0 selects the bilinear sample.
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
        //! Spline second derivatives at the nodes, laid out like data:
        //! d2/dx2 along each mu row, d2/dmu2 along each x column, and the
        //! mixed d4/dx2dmu2 (null in bilinear mode).
        const double *d2x{nullptr};
        const double *d2m{nullptr};
        const double *d4xm{nullptr};
        int n_x{0};
        int n_mu{0};
        double x_min{0.0};
        double x_max{1.0};
        double eta0{1.0};
        int interp{1}; //!< 1 = C2 cubic spline, 0 = bilinear

        //! Sample at compactified radius a_x and SIGNED a_mu (= cos theta);
        //! the mu grid covers [0, 1] and parity supplies the southern
        //! hemisphere.
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
            if (interp == 0)
            {
                for (int c = 0; c < NCOMP; ++c)
                {
                    const double v00 = data[flat(j0, i0, c)];
                    const double v10 = data[flat(j0, i0 + 1, c)];
                    const double v01 = data[flat(j0 + 1, i0, c)];
                    const double v11 = data[flat(j0 + 1, i0 + 1, c)];
                    vals[c] = v00 * (1 - wx) * (1 - wm) +
                              v10 * wx * (1 - wm) + v01 * (1 - wx) * wm +
                              v11 * wx * wm;
                }
            }
            else
            {
                // Cubic spline on a cell of width h: A y_i + B y_{i+1} +
                // C y''_i + D y''_{i+1}.  Along x on the two bracketing mu
                // rows, for the value and for its mu-second-derivative, then
                // along mu.
                const double hx = (x_max - x_min) / (n_x - 1);
                const double hm = 1.0 / (n_mu - 1);
                const double ax = 1.0 - wx;
                const double bx = wx;
                const double cx = (ax * ax * ax - ax) * hx * hx / 6.0;
                const double dx = (bx * bx * bx - bx) * hx * hx / 6.0;
                const double am = 1.0 - wm;
                const double bm = wm;
                const double cm = (am * am * am - am) * hm * hm / 6.0;
                const double dm = (bm * bm * bm - bm) * hm * hm / 6.0;
                for (int c = 0; c < NCOMP; ++c)
                {
                    const long k00 = flat(j0, i0, c);
                    const long k10 = flat(j0, i0 + 1, c);
                    const long k01 = flat(j0 + 1, i0, c);
                    const long k11 = flat(j0 + 1, i0 + 1, c);
                    const double f0 = ax * data[k00] + bx * data[k10] +
                                      cx * d2x[k00] + dx * d2x[k10];
                    const double f1 = ax * data[k01] + bx * data[k11] +
                                      cx * d2x[k01] + dx * d2x[k11];
                    const double m0 = ax * d2m[k00] + bx * d2m[k10] +
                                      cx * d4xm[k00] + dx * d4xm[k10];
                    const double m1 = ax * d2m[k01] + bx * d2m[k11] +
                                      cx * d4xm[k01] + dx * d4xm[k11];
                    vals[c] = am * f0 + bm * f1 + cm * m0 + dm * m1;
                }
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

    explicit RotatingBackgroundTable(const std::string &a_path,
                                     int a_interp = 1)
    {
        m_view.interp = a_interp;
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

        if (m_view.interp != 0 && (m_view.n_x < 4 || m_view.n_mu < 3))
        {
            throw std::runtime_error(
                "RotatingBackgroundTable: " + path +
                " is too small for the cubic spline (n_x >= 4, n_mu >= 3); "
                "use spinning_background_interp = 0");
        }

        const long total =
            static_cast<long>(m_view.n_mu) * m_view.n_x * NCOMP;
        // spline mode: data, d2x, d2m, d4xm back to back
        const long n_arrays = (m_view.interp != 0) ? 4 : 1;
        double *raw = static_cast<double *>(amrex::The_Managed_Arena()->alloc(
            static_cast<std::size_t>(n_arrays * total) * sizeof(double)));
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

        if (m_view.interp != 0)
        {
            m_view.d2x  = raw + total;
            m_view.d2m  = raw + 2 * total;
            m_view.d4xm = raw + 3 * total;
            build_spline(raw, raw + total, raw + 2 * total, raw + 3 * total);
        }

        amrex::Print() << "RotatingBackgroundTable: loaded " << path
                       << " (eta0 " << m_view.eta0 << ", " << m_view.n_x
                       << " x-points in [" << m_view.x_min << ", "
                       << m_view.x_max << "], " << m_view.n_mu
                       << " mu-points), "
                       << ((m_view.interp != 0) ? "C2 cubic-spline"
                                                : "bilinear")
                       << " interpolation\n";
    }

    //! Second derivatives of the not-a-knot cubic spline through n >= 4
    //! equally spaced samples y (spacing h), into m.  Uniform spacing makes
    //! not-a-knot (y''' continuous at the second and second-last nodes)
    //! give m_1 = r_1 / 6 and m_{n-2} = r_{n-2} / 6 outright, with
    //! r_i = 6 (y_{i+1} - 2 y_i + y_{i-1}) / h^2; the rest is the usual
    //! m_{i-1} + 4 m_i + m_{i+1} = r_i, solved by the Thomas algorithm.
    static void spline_d2(const std::vector<double> &y, std::vector<double> &m,
                          double h, std::vector<double> &work)
    {
        const int n = static_cast<int>(y.size());
        m.assign(n, 0.0);
        const double s = 6.0 / (h * h);
        auto r = [&](int i) { return s * (y[i + 1] - 2.0 * y[i] + y[i - 1]); };
        m[1]     = r(1) / 6.0;
        m[n - 2] = r(n - 2) / 6.0;
        // unknowns m_2 .. m_{n-3}: forward sweep on (1, 4, 1)
        const int lo = 2;
        const int hi = n - 3;
        if (hi >= lo)
        {
            work.assign(n, 0.0); // modified super-diagonal
            std::vector<double> d(n, 0.0);
            for (int i = lo; i <= hi; ++i)
            {
                double rhs = r(i);
                if (i == lo)
                {
                    rhs -= m[1];
                }
                if (i == hi)
                {
                    rhs -= m[n - 2];
                }
                const double up    = (i < hi) ? 1.0 : 0.0;
                const double denom = (i == lo) ? 4.0 : 4.0 - work[i - 1];
                work[i]            = up / denom;
                d[i] = (i == lo) ? rhs / denom : (rhs - d[i - 1]) / denom;
            }
            m[hi] = d[hi];
            for (int i = hi - 1; i >= lo; --i)
            {
                m[i] = d[i] - work[i] * m[i + 1];
            }
        }
        m[0]     = 2.0 * m[1] - m[2];
        m[n - 1] = 2.0 * m[n - 2] - m[n - 3];
    }

    //! The spline's node second derivatives (host, once at load; the arrays
    //! are managed memory, so the GPU reads them as they are).
    void build_spline(const double *data, double *d2x, double *d2m,
                      double *d4xm) const
    {
        const int nx  = m_view.n_x;
        const int nmu = m_view.n_mu;
        const double hx = (m_view.x_max - m_view.x_min) / (nx - 1);
        const double hm = 1.0 / (nmu - 1);
        auto flat = [&](int j, int i, int c)
        { return (static_cast<long>(j) * nx + i) * NCOMP + c; };
        std::vector<double> y;
        std::vector<double> m;
        std::vector<double> work;

        // along x, every mu row
        y.resize(nx);
        for (int c = 0; c < NCOMP; ++c)
        {
            for (int j = 0; j < nmu; ++j)
            {
                for (int i = 0; i < nx; ++i)
                {
                    y[i] = data[flat(j, i, c)];
                }
                spline_d2(y, m, hx, work);
                for (int i = 0; i < nx; ++i)
                {
                    d2x[flat(j, i, c)] = m[i];
                }
            }
        }

        // along mu, every x column, mirrored through mu = 0 with the
        // component's parity (domega_dtheta_over_sintheta is odd): node k of
        // the 2 nmu - 1 mirrored nodes sits at mu = (k - (nmu - 1)) hm
        const int nm = 2 * nmu - 1;
        y.resize(nm);
        for (int c = 0; c < NCOMP; ++c)
        {
            const double parity = (c == 4) ? -1.0 : 1.0;
            for (int pass = 0; pass < 2; ++pass)
            {
                const double *src = (pass == 0) ? data : d2x;
                double *dst       = (pass == 0) ? d2m : d4xm;
                for (int i = 0; i < nx; ++i)
                {
                    for (int j = 0; j < nmu; ++j)
                    {
                        const double v      = src[flat(j, i, c)];
                        y[nmu - 1 + j]      = v;
                        y[nmu - 1 - j]      = parity * v;
                    }
                    if (parity < 0.0)
                    {
                        y[nmu - 1] = 0.0; // an odd function vanishes at mu = 0
                    }
                    spline_d2(y, m, hm, work);
                    for (int j = 0; j < nmu; ++j)
                    {
                        dst[flat(j, i, c)] = m[nmu - 1 + j];
                    }
                }
            }
        }
    }
};

#endif /* ROTATINGBACKGROUNDTABLE_HPP_ */
