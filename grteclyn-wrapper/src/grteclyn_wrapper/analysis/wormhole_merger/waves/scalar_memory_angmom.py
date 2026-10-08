r"""Nonlinear memory and angular momentum carried by BOTH radiation channels
of the ghost-supported binaries -- gravitational waves and the phantom scalar
-- through one extraction sphere, from the packed l <= 2 mode streams.  Numpy
only; reads results/merger/campaign, writes nothing.

budget(run, R, t0, t1) is the entry point (the claims ledger's
extract_waves.waves_memory_ratio calls it).  Two observables follow from the
same two streams as the paper's energy statement (the ghost radiates negative
energy):

  (7) the nonlinear (Christodoulou) memory.  Every massless flux sources it
      through its energy per solid angle (Thorne 1992 PRD 45, 520; Favata
      2009), so the ghost's flux enters with its PHYSICAL (negative) sign --
      and whether it reverses, cancels or enhances the gravitational memory
      is set by its angular pattern as much as by that sign;
  (8) the angular momentum each channel carries: whether the ghost's J flux
      is opposite to the orbit's, i.e. whether the scalar channel pumps
      angular momentum INTO the orbit as it pumps energy in.

CONVENTIONS

  scalar_modes.dat   A_lm = R phi_lm, complex orthonormal Y_lm with the
                     Condon-Shortley phase and e^{+i m phi} (the dipole's phase
                     turns with the throat track); a real field has
                     A_{l,-m} = (-1)^m conj(A_lm) -- bit-exact in the stream,
                     so the consumer writes -m from +m.  The columns named Pi
                     hold R Pi_lm, not Pi_lm.  flux_kin = -R^2 oint Pi d_r phi
                     is CANONICAL (> 0 out).
  ghost sign         gravity couples to MINUS the canonical stress tensor, so
                     physical energy and J fluxes are minus the canonical ones.
  scalar, wave zone  canonical dE/du dOmega = (dA/du)^2 (the paper's
                     "wave-zone mode sum"); canonical J_z carried out
                         dJ_z/du = oint d_r A d_phi A dOmega
                                 = -oint (dA/du)(d_phi A) dOmega  (outgoing)
                                 = sum_lm m Im(conj(dA_lm/du) A_lm),
                     positive for a pattern turning toward +phi; the static
                     part of d_r phi, -A/r^2, drops out (oint A d_phi A = 0).
  psi4_mode_l2_all   R Psi4_2m in spin-weight -2 harmonics.  News
                     N_2m = int_0^t R Psi4_2m dt' by plot_scalar_channel's
                     rule (cumsum with np.gradient(t) weights), so the energies
                     are the paper's; dE/du dOmega = |sum_m N_2m _{-2}Y_2m|^2
                     / 16 pi.  J (Ruiz, Alcubierre, Nunez, Takahashi 2008):
                     dJ_z/dt = (1/16 pi) sum_m m Im(H_2m conj(N_2m)),
                     H_2m = int N_2m dt, so a mode ~ e^{-i omega t} carries
                     dJ/dE = m/omega.
  memory             R h_lm = 16 pi sqrt((l-2)!/(l+2)!) int du oint dOmega
                     (dE/du dOmega) conj(Y_lm) = 16 pi/sqrt(24) (...) at l = 2,
                     on the source's axis: z (orbital) for the orbits, x (the
                     collision axis) for the head-on, whose z-frame m = 0, +-2
                     are one pattern axisymmetric about x.  Angular integrals:
                     Gauss-Legendre(cos theta) x uniform(phi), 40 x 80, exact
                     for these band limits.  Per unit energy the (2,0)
                     projection of an equatorial m = +-1 dipole flux is
                     -(2/5)sqrt(5/16 pi) and of an m = +-2 GW flux
                     +(4/7)sqrt(5/16 pi): a NEGATIVE-energy dipole adds to the
                     GW memory (x 16 pi/sqrt 24: +1.294 |E_phi| against
                     +1.849 E_GW); about the head-on's axis, cos^2 against
                     sin^4: -2.589 |E_phi|, -1.849 E_GW.

ESTIMATORS.  E_phi twice: the kinematic flux (the paper's primary) and the
wave-zone sum.  The memory uses the wave-zone angular pattern; h_kin rescales
it to the kinematic energy, which brackets the estimator.  A window where the
kinematic flux is net INGOING (canonical) is flagged: there the wave-zone sums
read near-zone field changes as radiation.  Nothing is extrapolated: the
spread between spheres is the near-zone error bar.

THE RADIATIVE DIPOLE.  The spheres sit at omega R ~ 1-3, so every
finite-sphere scalar reading mixes radiation with the rotating, growing near
field of the mouths' hair.  For l = 1 the flat-space outgoing solution is
exact, A_1m = F'(u) + F(u)/R, and solving it on each sphere separately
(dipole_radiative) leaves the part that reaches infinity.
"""
from __future__ import annotations

import math
import pathlib
from functools import lru_cache

import numpy as np

from grteclyn_wrapper.analysis.wormhole_merger.pack.paths import PACK_ROOT
from grteclyn_wrapper.analysis.wormhole_merger.pack.readers import read_columns

PACK = PACK_ROOT / "campaign"
ELLS = (0, 1, 2)
N_THETA, N_PHI = 40, 80
MEM = 16.0 * math.pi / math.sqrt(24.0)      # 16 pi sqrt((l-2)!/(l+2)!) at l = 2
FRAMES = {"z": ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
          "x": ((0.0, 1.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0))}


# ------------------------------------------------------------------ reading
@lru_cache(maxsize=None)
def stream(path: pathlib.Path) -> dict:
    return read_columns(path)


def scalar_sphere(run: str, R: int):
    """t, A_lm = R phi_lm and flux_kin through sphere R (run = its path under campaign/)."""
    s = stream(PACK / run / "scalar_modes.dat")
    A = {}
    for l in ELLS:
        for m in range(-l, l + 1):
            A[l, m] = s[f"R{R}_phi_l{l}_m{m}_re"] + 1j * s[f"R{R}_phi_l{l}_m{m}_im"]
    return s["time"], A, s[f"R{R}_scalar_flux_kin"]


def psi4_sphere(run: str, R: int):
    p = stream(PACK / run / "psi4_mode_l2_all.dat")
    return p["time"], {m: p[f"Re_m{m}(R={R})"] + 1j * p[f"Im_m{m}(R={R})"] for m in range(-2, 3)}


# ------------------------------------------------------------------ harmonics
def ylm(l: int, m: int, th, ph):
    """Orthonormal complex Y_lm, Condon-Shortley phase, l <= 2."""
    if m < 0:
        return (-1) ** m * np.conj(ylm(l, -m, th, ph))
    c, s = np.cos(th), np.sin(th)
    amp = {(0, 0): np.full_like(c, 0.5 / math.sqrt(math.pi)),
           (1, 0): math.sqrt(3.0 / (4.0 * math.pi)) * c,
           (1, 1): -math.sqrt(3.0 / (8.0 * math.pi)) * s,
           (2, 0): math.sqrt(5.0 / (16.0 * math.pi)) * (3.0 * c * c - 1.0),
           (2, 1): -math.sqrt(15.0 / (8.0 * math.pi)) * s * c,
           (2, 2): math.sqrt(15.0 / (32.0 * math.pi)) * s * s}[(l, m)]
    return amp * np.exp(1j * m * ph)


def sylm2(m: int, th, ph):
    """Spin-weight -2, l = 2 harmonics (Ajith et al. 2007; Ruiz et al. 2008)."""
    c, s = np.cos(th), np.sin(th)
    amp = {2: math.sqrt(5.0 / (64.0 * math.pi)) * (1.0 + c) ** 2,
           1: math.sqrt(5.0 / (16.0 * math.pi)) * s * (1.0 + c),
           0: math.sqrt(15.0 / (32.0 * math.pi)) * s * s,
           -1: math.sqrt(5.0 / (16.0 * math.pi)) * s * (1.0 - c),
           -2: math.sqrt(5.0 / (64.0 * math.pi)) * (1.0 - c) ** 2}[m]
    return amp * np.exp(1j * m * ph)


@lru_cache(maxsize=None)
def grid(n_theta: int = N_THETA, n_phi: int = N_PHI):
    """Gauss-Legendre in cos(theta) x uniform phi: nodes and dOmega weights."""
    x, w = np.polynomial.legendre.leggauss(n_theta)
    ph = 2.0 * math.pi * np.arange(n_phi) / n_phi
    TH, PH = np.meshgrid(np.arccos(x), ph, indexing="ij")
    W = np.outer(w, np.full(n_phi, 2.0 * math.pi / n_phi))
    return TH.ravel(), PH.ravel(), W.ravel()


@lru_cache(maxsize=None)
def frame_y2(frame: str):
    """Y_2m on the grid in a frame whose polar axis is the source's axis."""
    th, ph, _ = grid()
    n = np.stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)], -1)
    e1, e2, e3 = (np.array(v) for v in FRAMES[frame])
    x, y, z = n @ e1, n @ e2, n @ e3
    return {m: ylm(2, m, np.arccos(np.clip(z, -1.0, 1.0)), np.arctan2(y, x)) for m in range(-2, 3)}


# ------------------------------------------------------------------ calculus
def ddt(t, y):
    """d/dt on the stream's cadence, np.gradient (the paper's rule)."""
    return np.gradient(y, t)


def integ(t, y, rule: str = "paper"):
    """Running int_0^t: plot_scalar_channel._gw_flux's cumsum rule, or trapezoid."""
    if rule == "paper":
        return np.cumsum(y * np.gradient(t))
    return np.concatenate([[0.0], np.cumsum(0.5 * (y[1:] + y[:-1]) * np.diff(t))])


def window(t, rate, t0: float, t1: float):
    """int_t0^t1 rate dt (trapezoid, ends interpolated like plot_scalar_channel._at)."""
    if np.iscomplexobj(rate):
        return complex(window(t, rate.real, t0, t1), window(t, rate.imag, t0, t1))
    c = integ(t, rate, "trapezoid")
    return float(np.interp(t1, t, c) - np.interp(t0, t, c))


# ------------------------------------------------------------------ the two channels
@lru_cache(maxsize=None)
def scalar_rates(run: str, R: int, frame: str = "z") -> dict:
    """PHYSICAL (ghost-signed) rates through sphere R: the kinematic energy flux,
    the wave-zone energy flux W, W's memory R dh_2m/du in the frame, and J_z."""
    th, ph, w = grid()
    Yp = frame_y2(frame)
    t, A, kin = scalar_sphere(run, R)
    Ad = {k: ddt(t, v) for k, v in A.items()}
    Y = {k: ylm(*k, th, ph) for k in A}
    dA = sum(np.outer(Ad[k], Y[k]) for k in Ad).real
    dphiA = sum(np.outer(1j * k[1] * A[k], Y[k]) for k in A).real
    F = dA ** 2
    return {"t": t, "E_kin": -kin, "E_W": -(F @ w),
            "mem_W": {m: -MEM * (F @ (w * np.conj(Yp[m]))) for m in range(-2, 3)},
            "J": (dA * dphiA) @ w}                                  # physical: +oint dA d_phi A


@lru_cache(maxsize=None)
def dipole_radiative(run: str, R: int, frame: str = "z") -> dict:
    """The radiative part of the l = 1 channel.  Outside the source the
    flat-space outgoing dipole is exactly phi_1m = F'(u)/r + F(u)/r^2, i.e.
    A_1m(t) = F'(u) + F(u)/R on the sphere.  Solving F' = A_1m - F/R (exact for
    piecewise-linear A; F(0) = R A_1m(0), the static time-symmetric data)
    leaves A_inf = sum_m F'_1m Y_1m, the field that reaches infinity.  PHYSICAL
    rates as in scalar_rates, from F'' = dA/dt - F'/R.  Assumes flat space and
    coordinate R between source and sphere (alpha, chi enter at O(M/R));
    tested by the agreement of the spheres at equal u."""
    th, ph, w = grid()
    Yp = frame_y2(frame)
    t, F1, F2 = _dipole(run, R)
    Y = {m: ylm(1, m, th, ph) for m in F1}
    d2 = sum(np.outer(F2[m], Y[m]) for m in F2).real
    dphi = sum(np.outer(1j * m * F1[m], Y[m]) for m in F1).real
    F = d2 ** 2
    return {"t": t, "E": -(F @ w), "J": (d2 * dphi) @ w,
            "mem": {m: -MEM * (F @ (w * np.conj(Yp[m]))) for m in range(-2, 3)}}


def _dipole(run: str, R: int):
    """F'_1m and F''_1m of the outgoing dipole on sphere R (dipole_radiative)."""
    t, A, _ = scalar_sphere(run, R)
    F1, F2 = {}, {}
    for m in (-1, 0, 1):
        a, F = A[1, m], np.zeros_like(A[1, m])
        F[0] = R * a[0]
        for i in range(t.size - 1):
            h = t[i + 1] - t[i]
            s = (a[i + 1] - a[i]) / h
            p0, p1 = R * a[i] - R * R * s, R * (a[i] + s * h) - R * R * s
            F[i + 1] = p1 + (F[i] - p0) * math.exp(-h / R)
        F1[m] = a - F / R
        F2[m] = ddt(t, a) - F1[m] / R
    return t, F1, F2


@lru_cache(maxsize=None)
def gw_rates(run: str, R: int, frame: str = "z") -> dict:
    """GW rates through sphere R: energy, memory R dh_2m/du in the frame, J_z."""
    th, ph, w = grid()
    Yp = frame_y2(frame)
    t, psi = psi4_sphere(run, R)
    N = {m: integ(t, psi[m]) for m in psi}
    H = {m: integ(t, N[m]) for m in psi}
    F = np.abs(sum(np.outer(N[m], sylm2(m, th, ph)) for m in N)) ** 2 / (16.0 * math.pi)
    return {"t": t, "E": F @ w,
            "mem": {m: MEM * (F @ (w * np.conj(Yp[m]))) for m in range(-2, 3)},
            "J": sum(m * np.imag(H[m] * np.conj(N[m])) for m in N) / (16.0 * math.pi)}


# ------------------------------------------------------------------ one window
def budget(run: str, R: int, t0: float, t1: float, frame: str = "z") -> dict:
    """Both channels through sphere R over [t0, t1], the GW news running from t = 0:

      E_GW, h_GW, J_GW          energy, R h_2m (frame) and J_z of the waves;
      E_kin, E_W, h_W, J_phi    the scalar's kinematic and wave-zone energy, its
                                wave-zone R h_2m and its J_z, all PHYSICAL;
      h_kin                     h_W's (2,0) rescaled to the kinematic energy;
      E_rad, J_rad, h_rad       the radiative dipole's energy, J_z and (2,0);
      inflow                    the kinematic flux is net INGOING (canonical)."""
    s, g = scalar_rates(run, R, frame), gw_rates(run, R, frame)
    ts, tg = s["t"], g["t"]
    b = {"E_GW": window(tg, g["E"], t0, t1), "J_GW": window(tg, g["J"], t0, t1),
         "h_GW": {m: window(tg, g["mem"][m], t0, t1) for m in range(-2, 3)},
         "E_kin": window(ts, s["E_kin"], t0, t1), "J_phi": window(ts, s["J"], t0, t1),
         "E_W": window(ts, s["E_W"], t0, t1),
         "h_W": {m: window(ts, s["mem_W"][m], t0, t1) for m in range(-2, 3)}}
    b["h_kin"] = b["h_W"][0].real * b["E_kin"] / b["E_W"]
    d = dipole_radiative(run, R, frame)
    b["E_rad"], b["J_rad"] = window(d["t"], d["E"], t0, t1), window(d["t"], d["J"], t0, t1)
    b["h_rad"] = window(d["t"], d["mem"][0], t0, t1).real
    b["inflow"] = b["E_kin"] > 0.0          # net canonical INflow through the sphere
    return b
