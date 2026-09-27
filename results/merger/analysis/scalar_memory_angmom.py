#!/usr/bin/env python3
r"""Nonlinear memory and angular momentum carried by BOTH radiation channels
of the ghost-supported binaries -- gravitational waves and the phantom scalar
-- from the packed l <= 2 mode streams.  Numpy/scipy only; reads
results/merger/campaign, writes nothing.

WHY.  The paper's scalar channel (plot_scalar_channel, ledger rows
clmGwScalar*) is an ENERGY statement: the ghost radiates negative energy,
|E_phi| ~ 1-3 E_GW on the fly-by.  Two observables follow from the same two
streams and had not been computed:

  (7) the nonlinear (Christodoulou) memory.  Every massless flux sources it
      through its energy per solid angle (Thorne 1992 PRD 45, 520; Favata
      2009), so the ghost's flux enters with its PHYSICAL (negative) sign --
      and whether it reverses, cancels or enhances the gravitational memory
      is set by its angular pattern as much as by that sign;
  (8) the angular momentum each channel carries: whether the ghost's J flux
      is opposite to the orbit's, i.e. whether the scalar channel pumps
      angular momentum INTO the orbit as it pumps energy in.

CONVENTIONS (each checked on the data by the [check] lines of the report)

  scalar_modes.dat   A_lm = R phi_lm, complex orthonormal Y_lm with the
                     Condon-Shortley phase and e^{+i m phi} (the dipole's phase
                     turns with the throat track); a real field has
                     A_{l,-m} = (-1)^m conj(A_lm) -- bit-exact in the stream,
                     so the consumer writes -m from +m.  The columns named Pi
                     hold R Pi_lm, not Pi_lm: they track dA_lm/dt with a
                     factor ~1/alpha (1.07-1.25 at R = 30, 1.17-1.34 at R = 14).
                     flux_kin = -R^2 oint Pi d_r phi is CANONICAL (> 0 out).
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
                     dJ/dE = m/omega.  Psi4_22's phase turns with the scalar
                     dipole's at twice its rate, so the stream follows the
                     standard h = h_+ - i h_x convention (validated below by
                     the sign of J_GW and by dJ/dE = m/omega on the burst).
  memory             R h_lm = 16 pi sqrt((l-2)!/(l+2)!) int du oint dOmega
                     (dE/du dOmega) conj(Y_lm) = 16 pi/sqrt(24) (...) at l = 2,
                     on the source's axis: z (orbital) for the orbits, x (the
                     collision axis) for the head-on, whose z-frame m = 0, +-2
                     are one pattern axisymmetric about x.  Angular integrals:
                     Gauss-Legendre(cos theta) x uniform(phi), 40 x 80, exact
                     for these band limits; a Wigner-3j (Gaunt) mode sum
                     reproduces them.  Per unit energy the (2,0) projection of
                     an equatorial m = +-1 dipole flux is -(2/5)sqrt(5/16 pi)
                     and of an m = +-2 GW flux +(4/7)sqrt(5/16 pi): a NEGATIVE-
                     energy dipole adds to the GW memory (x 16 pi/sqrt 24:
                     +1.294 |E_phi| against +1.849 E_GW); about the head-on's
                     axis, cos^2 against sin^4: -2.589 |E_phi|, -1.849 E_GW.
  orbit              L_z = sum (x p_y - y p_x) from evolution_params.txt:
                     throats at x = -+d/2 with P = (0, +-p, 0), L_z = -p d.

WINDOWS.  Fly-by: a sphere is read only to u = t - R <= 50 (R = 14 to t = 64,
R = 30 to t = 80; trust_windows.tsv), plus the paper's cut t = 60 and the
u-matched t = 44 at R = 14.  Spiral: to the end of its record, t = 50 (the
burst has not reached R = 30 by then: pre-burst, not a measurement).
Head-on: from the first common MOTS (horizon_scan.dat centre C, t = 21.5 --
waves_post_energy's window) to 70 and to 100 (box-face reflection after 70).
Every window end is also moved by -5 (and +5 where that stays inside it).

ESTIMATORS.  E_phi twice: the kinematic flux (the paper's primary) and the
wave-zone sum.  The memory uses the wave-zone angular pattern; "kin-norm"
rescales it to the kinematic energy, which brackets the estimator.  A window
where the kinematic flux is net INGOING (canonical) is flagged: there the
wave-zone sums read near-zone field changes as radiation.  E_GW is the paper's
running integral, which drifts; the band-limited E_GW of Fig. psi4_ligo(d)
and the matching band-limited J_GW are printed beside it.  Nothing is
extrapolated: the R = 14 / R = 30 spread is the near-zone error bar.

THE RADIATIVE DIPOLE (a diagnostic added here, not a paper estimator).  Both
spheres sit at omega R ~ 1-3, so every finite-sphere scalar reading mixes
radiation with the rotating, growing near field of the mouths' hair.  For
l = 1 the flat-space outgoing solution is exact, A_1m = F'(u) + F(u)/R, and
solving it on each sphere separately (dipole_radiative) leaves the part that
reaches infinity.  It passes the test the raw estimators fail: the static
dipole R A_11(0) agrees across R = 14/30 to 0.5 %, the radiated E and J at
u = 30 to 3 % and 0 % (raw: 1.5-2.6x apart), and on the head-on R = 10/14/18
give -0.045/-0.044/-0.043 to u = 45 (raw wave-zone 1.7x apart, kinematic
changing sign).  It breaks down at R = 14 past u ~ 35, where the inflating
mouth reaches the sphere (t = 63.8).  The same split reproduces the stream's
kinematic integral as radiated + stored near-field energy (within the
Pi/(dA/dt) and O(M/R) metric factors, 1.4 at R = 30, t = 60).  The GW side has
no such cure here: E_GW differs 1.9x between the spheres at equal u, and a
first-order (Nakano) finite-radius correction does not converge at omega R ~ 1.4.

RESULT (2026-09-27; the report prints every number).  (7) The ghost's (2,0)
memory has the SAME sign as the gravitational one on every window where the
scalar energy is negative (28/28 wave-zone, 19/19 radiative dipole): it
ENHANCES the memory, never reverses or cancels it.  Robust: the per-unit-
energy projections are the pure-dipole values (+1.294 orbital, -2.589 head-on)
to 4 digits, against the GW's +1.72..+1.84 / -1.84.  Fragile: the size, set by
|E_phi|/E_GW -- 0.3-2.7x the GW memory on the fly-by with the raw estimators,
0.3-1.0x with the radiative dipole (u <= 35), 2.6-6x on the head-on.  The
radiated scalar energy of the fly-by is 0.030 by u = 30 on both spheres: 35 %
of the paper's kinematic |E_phi| = 0.087 at R = 30, t = 60, the rest being
near-field energy.  (8) J_GW carries the orbit's sign (-z; dJ/dE = m/omega to
10 % on the fly-by burst at R = 30); the ghost's physical J flux is +z,
opposite, on every outflow window and in the radiative dipole: the scalar
channel pumps angular momentum into the orbit.  Its size relative to J_GW
(-0.2 .. -1.9) is fragile.

Run:  grteclyn-wrapper/.venv/bin/python results/merger/analysis/scalar_memory_angmom.py
"""
from __future__ import annotations

import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")      # tiny matrices: threads only cost CPU on a shared node

import math  # noqa: E402
import pathlib  # noqa: E402
import sys  # noqa: E402
from functools import lru_cache  # noqa: E402

import numpy as np  # noqa: E402
from scipy.interpolate import CubicSpline  # noqa: E402
from scipy.signal import savgol_filter  # noqa: E402
from scipy.signal.windows import tukey  # noqa: E402

PACK = pathlib.Path(__file__).resolve().parents[1] / "campaign"
FLYBY = "06_binary_flyby/p045/merge_orbit_flip_d12_p045_L128_lvl5_t100"
SPIRAL = "05_binary_spiral/p012_paper/v2_spiral_d12_p012_L128_lvl3_t050"
HEADON = "04_binary_headon/merge_headon_flip_d8_v1_lvl5from0_scalar_t100"
U_GATE = 50.0          # fly-by: sphere readings to t - R <= 50 (trust_windows.tsv)
U_RAD = 35.0           # fly-by: the radiative dipole agrees across R = 14/30 to here (R = 14 is engulfed by u ~ 50)
T_REFLECT = 70.0       # head-on: box-face reflection spreads the spheres after this
ELLS = (0, 1, 2)
N_THETA, N_PHI = 40, 80
MEM = 16.0 * math.pi / math.sqrt(24.0)      # 16 pi sqrt((l-2)!/(l+2)!) at l = 2
FRAMES = {"z": ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
          "x": ((0.0, 1.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0))}
# What this script must reproduce: ledger_waves.tsv notes of clmGwScalarRatioSixty,
# clmGwScalarRatioWaveZone, clmGwScalarRatioInner, clmGwCensEnergy* (code units).
PAPER_RATIO = {("kin", 30, 60.0): 2.3325, ("wz", 30, 60.0): 1.743, ("kin", 14, 60.0): 3.020}
PAPER_POST = {10: -0.0557, 14: -0.0711, 18: -0.0753}
NOTES = {(SPIRAL, 30): "pre-burst (level-3 record ends before the burst reaches R = 30)",
         (SPIRAL, 14): "pre-merger (the plunge's MOTS is at t = 55 on the level-5 arm)"}


# ------------------------------------------------------------------ reading
@lru_cache(maxsize=None)
def stream(path: pathlib.Path) -> dict:
    names = None
    with path.open() as fh:
        for line in fh:
            if line.startswith("#") and "time" in line:
                names = line.lstrip("#").split()
    data = np.loadtxt(path)
    return {n: data[:, i] for i, n in enumerate(names)}


def params(run: str) -> dict:
    out = {}
    for line in (PACK / run / "evolution_params.txt").open():
        line = line.split("#")[0].strip()
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def orbital_lz(run: str) -> float:
    """L_z = sum over throats of (x p_y - y p_x), offsets from the box centre."""
    p, lz = params(run), 0.0
    for b in ("A", "B"):
        x = [float(v) for v in p[f"wormhole_center{b}"].split()[:3]]
        q = [float(v) for v in p[f"wormhole_momentum{b}"].split()[:3]]
        lz += x[0] * q[1] - x[1] * q[0]
    return lz


def _scan(run: str):
    return np.genfromtxt(PACK / run / "horizon_scan.dat", dtype=None, encoding=None, names=True)


def first_common_mots(run: str) -> float:
    """First horizon_scan row with a MOTS on the common centre C (waves_first_mots)."""
    h = _scan(run)
    return float(h["time"][(h["centre"] == "C") & (h["n_mots"] > 0)][0])


def mouth_crossing(run: str, R: float) -> float | None:
    """When the per-mouth areal radius first passes R (plot_scalar_channel._mouth_crossing)."""
    h = _scan(run)
    a = h[h["centre"] == "A"]
    over = a["R_min"] >= R
    if not over.any():
        return None
    k = int(np.argmax(over))
    return float(a["time"][k]) if k == 0 else float(
        np.interp(R, a["R_min"][k - 1:k + 1], a["time"][k - 1:k + 1]))


def scalar_sphere(run: str, R: int, stride: int = 1):
    """t, A_lm = R phi_lm, P_lm = the stored 'Pi' columns (= R Pi_lm), flux_kin."""
    s = stream(PACK / run / "scalar_modes.dat")
    A, P = {}, {}
    for l in ELLS:
        for m in range(-l, l + 1):
            A[l, m] = (s[f"R{R}_phi_l{l}_m{m}_re"] + 1j * s[f"R{R}_phi_l{l}_m{m}_im"])[::stride]
            P[l, m] = (s[f"R{R}_Pi_l{l}_m{m}_re"] + 1j * s[f"R{R}_Pi_l{l}_m{m}_im"])[::stride]
    return s["time"][::stride], A, P, s[f"R{R}_scalar_flux_kin"][::stride]


def psi4_sphere(run: str, R: int, stride: int = 1):
    p = stream(PACK / run / "psi4_mode_l2_all.dat")
    return p["time"][::stride], {m: (p[f"Re_m{m}(R={R})"] + 1j * p[f"Im_m{m}(R={R})"])[::stride]
                                 for m in range(-2, 3)}


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


def wigner3j(j1, j2, j3, m1, m2, m3) -> float:
    """Racah's formula, integer arguments."""
    if m1 + m2 + m3 != 0 or not abs(j1 - j2) <= j3 <= j1 + j2:
        return 0.0
    if abs(m1) > j1 or abs(m2) > j2 or abs(m3) > j3:
        return 0.0
    f = math.factorial
    tri = f(j1 + j2 - j3) * f(j1 - j2 + j3) * f(-j1 + j2 + j3) / f(j1 + j2 + j3 + 1)
    pre = math.sqrt(tri * f(j1 + m1) * f(j1 - m1) * f(j2 + m2) * f(j2 - m2)
                    * f(j3 + m3) * f(j3 - m3))
    tot = 0.0
    for k in range(0, j1 + j2 + j3 + 1):
        a = (k, j3 - j2 + k + m1, j3 - j1 + k - m2, j1 + j2 - j3 - k, j1 - k - m1, j2 - k + m2)
        if min(a) >= 0:
            tot += (-1) ** k / math.prod(f(x) for x in a)
    return (-1) ** (j1 - j2 - m3) * pre * tot


def gaunt(l1, m1, l2, m2, L, M, s: int = 0) -> float:
    """oint sY_l1m1 conj(sY_l2m2) conj(Y_LM) dOmega (s = 0, or s = -2 at l1 = l2 = 2)."""
    return ((-1) ** (m2 + M) * math.sqrt((2 * l1 + 1) * (2 * l2 + 1) * (2 * L + 1) / (4.0 * math.pi))
            * wigner3j(l1, l2, L, m1, -m2, -M) * wigner3j(l1, l2, L, -s, s, 0))


# ------------------------------------------------------------------ calculus
def ddt(t, y, rule: str = "gradient"):
    """d/dt on the stream's cadence: np.gradient (the paper's) or a cubic spline."""
    if rule == "gradient":
        return np.gradient(y, t)
    return CubicSpline(t, y.real)(t, 1) + 1j * CubicSpline(t, y.imag)(t, 1)


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
def scalar_rates(run: str, R: int, frame: str = "z", deriv: str = "gradient", stride: int = 1) -> dict:
    """PHYSICAL (ghost-signed) rates through sphere R: energy (kin; wave-zone W;
    Pi-based P; mixed X), memory R dh_2m/du in the frame, and J_z."""
    th, ph, w = grid()
    Yp = frame_y2(frame)
    t, A, P, kin = scalar_sphere(run, R, stride)
    Ad = {k: ddt(t, v, deriv) for k, v in A.items()}
    Y = {k: ylm(*k, th, ph) for k in A}

    def field(modes):
        return sum(np.outer(modes[k], Y[k]) for k in modes)

    dA, rP = field(Ad), field(P)
    dphiA = sum(np.outer(1j * k[1] * A[k], Y[k]) for k in A)
    imag = max(np.abs(dA.imag).max(), np.abs(dphiA.imag).max()) / np.abs(dA).max()
    dA, rP, dphiA = dA.real, rP.real, dphiA.real
    out = {"t": t, "E_kin": -kin, "imag": float(imag), "dmodes": Ad,
           "E_W_modes": -sum(np.abs(v) ** 2 for v in Ad.values()),
           "J": (dA * dphiA) @ w,                                   # physical: +oint dA d_phi A
           "J_P": (rP * dphiA) @ w,
           "J_modes": -sum(k[1] * np.imag(np.conj(Ad[k]) * A[k]) for k in A)}
    for e, F in (("W", dA ** 2), ("P", rP ** 2), ("X", dA * rP)):
        out[f"E_{e}"] = -(F @ w)
        out[f"mem_{e}"] = {m: -MEM * (F @ (w * np.conj(Yp[m]))) for m in range(-2, 3)}
    return out


@lru_cache(maxsize=None)
def dipole_radiative(run: str, R: int, frame: str = "z", stride: int = 1) -> dict:
    """DIAGNOSTIC, not the paper's estimator: the radiative part of the l = 1
    channel.  Outside the source the flat-space outgoing dipole is exactly
    phi_1m = F'(u)/r + F(u)/r^2, i.e. A_1m(t) = F'(u) + F(u)/R on the sphere.
    Solving F' = A_1m - F/R (exact for piecewise-linear A; F(0) = R A_1m(0), the
    static time-symmetric data) leaves A_inf = sum_m F'_1m Y_1m, the field that
    reaches infinity.  PHYSICAL rates as in scalar_rates, from F'' = dA/dt - F'/R.
    Assumes flat space and coordinate R between source and sphere (alpha, chi
    enter at O(M/R)); tested by the agreement of the spheres at equal u."""
    th, ph, w = grid()
    Yp = frame_y2(frame)
    t, F0, F1, F2 = _dipole(run, R, stride)
    Y = {m: ylm(1, m, th, ph) for m in F1}
    d2 = sum(np.outer(F2[m], Y[m]) for m in F2).real
    dphi = sum(np.outer(1j * m * F1[m], Y[m]) for m in F1).real
    F = d2 ** 2
    return {"t": t, "E": -(F @ w), "J": (d2 * dphi) @ w, "F0": F0[1][0],
            "mem": {m: -MEM * (F @ (w * np.conj(Yp[m]))) for m in range(-2, 3)}}


def _dipole(run: str, R: int, stride: int = 1):
    """F_1m, F'_1m, F''_1m of the outgoing dipole on sphere R (dipole_radiative)."""
    t, A, _, _ = scalar_sphere(run, R, stride)
    F0, F1, F2 = {}, {}, {}
    for m in (-1, 0, 1):
        a, F = A[1, m], np.zeros_like(A[1, m])
        F[0] = R * a[0]
        for i in range(t.size - 1):
            h = t[i + 1] - t[i]
            s = (a[i + 1] - a[i]) / h
            p0, p1 = R * a[i] - R * R * s, R * (a[i] + s * h) - R * R * s
            F[i + 1] = p1 + (F[i] - p0) * math.exp(-h / R)
        F0[m], F1[m] = F, a - F / R
        F2[m] = ddt(t, a) - F1[m] / R
    return t, F0, F1, F2


def gw_nakano_energy(run: str, R: int, t1: float) -> tuple[float, float]:
    """E_GW to t1 from trapezoid news, raw and with the first-order finite-radius
    correction of Nakano et al. 2015 (l = 2: R Psi4 -> R Psi4 - (2/R) int R Psi4 dt,
    no areal-radius or tortoise terms) -- the GW analogue of dipole_radiative."""
    t, psi = psi4_sphere(run, R)
    raw = cor = 0.0
    for m in psi:
        N = integ(t, psi[m], "trapezoid")
        raw = raw + np.abs(N) ** 2
        cor = cor + np.abs(N - (2.0 / R) * integ(t, N, "trapezoid")) ** 2
    return window(t, raw / (16.0 * np.pi), 0.0, t1), window(t, cor / (16.0 * np.pi), 0.0, t1)


def dipole_kin_split(run: str, R: int, t1: float) -> tuple[float, float, float]:
    """The same model's prediction for the stream's CANONICAL kinematic integral:
    -r^2 oint phi_t phi_r = sum |F''|^2 + d/du[(3/2R)|F'|^2 + (2/R^2)Re(F' F*) + |F|^2/R^3],
    radiated part plus stored near-field change.  Returns (data, radiated, near field)."""
    t, F0, F1, F2 = _dipole(run, R)
    k = scalar_sphere(run, R)[3]
    near = sum(1.5 / R * np.abs(F1[m]) ** 2 + 2.0 / R ** 2 * np.real(F1[m] * np.conj(F0[m]))
               + np.abs(F0[m]) ** 2 / R ** 3 for m in F0)
    rad = window(t, sum(np.abs(F2[m]) ** 2 for m in F2), 0.0, t1)
    return window(t, k, 0.0, t1), rad, float(np.interp(t1, t, near) - near[0])


@lru_cache(maxsize=None)
def gw_rates(run: str, R: int, frame: str = "z", rule: str = "paper", stride: int = 1) -> dict:
    """GW rates through sphere R: energy, memory R dh_2m/du in the frame, J_z."""
    th, ph, w = grid()
    Yp = frame_y2(frame)
    t, psi = psi4_sphere(run, R, stride)
    N = {m: integ(t, psi[m], rule) for m in psi}
    H = {m: integ(t, N[m], rule) for m in psi}
    F = np.abs(sum(np.outer(N[m], sylm2(m, th, ph)) for m in N)) ** 2 / (16.0 * math.pi)
    return {"t": t, "E": F @ w, "N": N, "psi": psi,
            "E_modes": sum(np.abs(v) ** 2 for v in N.values()) / (16.0 * math.pi),
            "mem": {m: MEM * (F @ (w * np.conj(Yp[m]))) for m in range(-2, 3)},
            "J": sum(m * np.imag(H[m] * np.conj(N[m])) for m in N) / (16.0 * math.pi),
            "E22": (np.abs(N[2]) ** 2 + np.abs(N[-2]) ** 2) / (16.0 * math.pi),
            "J22": sum(m * np.imag(H[m] * np.conj(N[m])) for m in (2, -2)) / (16.0 * math.pi),
            "omega22": -np.gradient(np.unwrap(np.angle(psi[2])), t)}   # Psi4_22 ~ e^{-i omega t}


@lru_cache(maxsize=None)
def band_gw(run: str, R: int, t_cut: float) -> dict:
    """E_GW of Fig. psi4_ligo(d) (extract_waves._band_egw) and the matching J_GW,
    numpy/scipy only: Parseval of the (2,2) news above 0.15 of the smoothed
    burst-PSD peak, doubled for +-m -- free of the running integral's drift.
    numpy's FFT puts e^{-i omega t} at f = -omega/2pi, so J = -(m/16pi) sum
    |Psi~|^2/(2 pi f)^3 / T, and J/E = m <1/omega> over the band."""
    t, psi = psi4_sphere(run, R)
    k = t <= t_cut + 1e-9
    t, y = t[k], psi[2][k]
    n, dt = y.size, (t[-1] - t[0]) / (t.size - 1)
    win = tukey(n, alpha=0.25)
    f1 = np.fft.rfftfreq(n, d=dt)
    S = (np.abs(np.fft.rfft(y.real * win)) ** 2 + np.abs(np.fft.rfft(y.imag * win)) ** 2) * dt / n
    S[1:-1] *= 2.0
    wl = max(5, min(21, (S.size // 5) | 1))
    wl = wl if wl <= S.size else (S.size if S.size % 2 else S.size - 1)
    Ss, ok = S.copy(), S > 0
    Ss[ok] = 10 ** savgol_filter(np.log10(S[ok]), wl, min(5, wl - 2), mode="interp")
    f_peak = float(f1[1:][np.argmax(Ss[1:])])
    w = np.ones(n)
    kk = max(2, int(0.05 * n))
    ramp = 0.5 * (1.0 - np.cos(np.pi * np.arange(kk) / kk))
    w[:kk], w[-kk:] = ramp, ramp[::-1]
    Yf, f = np.fft.fft(y * w) * dt, np.fft.fftfreq(n, dt)
    band = np.abs(f) > 0.15 * f_peak
    P, om = np.abs(Yf[band]) ** 2 / (n * dt) / (16.0 * np.pi), 2.0 * np.pi * f[band]
    i_pk = int(np.argmax(np.abs(Yf) * (f != 0)))
    return {"E": 2.0 * float(np.sum(P / om ** 2)), "J": 2.0 * float(-2.0 * np.sum(P / om ** 3)),
            "two_over_omega_peak": 2.0 / (-2.0 * np.pi * f[i_pk])}


def m_over_omega(run: str, R: int, t1: float, frac: float = 0.3) -> tuple[float, float]:
    """Over the burst (|Psi4_22| >= frac of its peak to t1): the (2,+-2) pair's
    sum dJ / sum dE against the median of 2/omega_22 (instantaneous, from
    Psi4_22's phase) -- dJ/dE = m/omega for a monochromatic mode."""
    g = gw_rates(run, R)
    k = g["t"] <= t1 + 1e-9
    a = np.abs(g["psi"][2])
    b = k & (a >= frac * a[k].max())
    return float(g["J22"][b].sum() / g["E22"][b].sum()), float(np.median(2.0 / g["omega22"][b]))


# ------------------------------------------------------------------ one window
def budget(run: str, R: int, t0: float, t1: float, frame: str = "z", deriv: str = "gradient",
           rule: str = "paper", stride: int = 1, t0_gw: float | None = None) -> dict:
    """Energies, R h_2m (frame) and J_z through sphere R over [t0, t1] (the GW
    over [t0_gw, t1] when given; its news always runs from t = 0)."""
    s, g = scalar_rates(run, R, frame, deriv, stride), gw_rates(run, R, frame, rule, stride)
    tg0 = t0 if t0_gw is None else t0_gw
    ts, tg = s["t"], g["t"]
    b = {"E_GW": window(tg, g["E"], tg0, t1), "J_GW": window(tg, g["J"], tg0, t1),
         "h_GW": {m: window(tg, g["mem"][m], tg0, t1) for m in range(-2, 3)},
         "E_kin": window(ts, s["E_kin"], t0, t1), "J_phi": window(ts, s["J"], t0, t1),
         "J_P": window(ts, s["J_P"], t0, t1), "J_modes": window(ts, s["J_modes"], t0, t1)}
    for e in ("W", "P", "X"):
        b[f"E_{e}"] = window(ts, s[f"E_{e}"], t0, t1)
        b[f"h_{e}"] = {m: window(ts, s[f"mem_{e}"][m], t0, t1) for m in range(-2, 3)}
    b["h_kin"] = b["h_W"][0].real * b["E_kin"] / b["E_W"]
    d = dipole_radiative(run, R, frame, stride)
    b["E_rad"], b["J_rad"] = window(d["t"], d["E"], t0, t1), window(d["t"], d["J"], t0, t1)
    b["h_rad"] = window(d["t"], d["mem"][0], t0, t1).real
    b["inflow"] = b["E_kin"] > 0.0          # net canonical INflow through the sphere
    return b


# ------------------------------------------------------------------ checks
def check_orthonormal() -> tuple[float, float, float]:
    """Max Gram-matrix error of Y_lm (l <= 2) and _{-2}Y_2m on the grid, and the
    max quadrature - Gaunt difference over every product integral the memory uses."""
    th, ph, w = grid()
    keys = [(l, m) for l in ELLS for m in range(-l, l + 1)]
    Y = {k: ylm(*k, th, ph) for k in keys}
    sY = {m: sylm2(m, th, ph) for m in range(-2, 3)}
    e_s = max(abs(np.sum(w * Y[a] * np.conj(Y[b])) - (a == b)) for a in keys for b in keys)
    e_t = max(abs(np.sum(w * sY[a] * np.conj(sY[b])) - (a == b)) for a in sY for b in sY)
    Y2, e_g = frame_y2("z"), 0.0
    for M in range(-2, 3):
        for a in keys:
            for b in keys:
                q = np.sum(w * Y[a] * np.conj(Y[b]) * np.conj(Y2[M]))
                e_g = max(e_g, abs(q - gaunt(a[0], a[1], b[0], b[1], 2, M)))
        for a in sY:
            for b in sY:
                q = np.sum(w * sY[a] * np.conj(sY[b]) * np.conj(Y2[M]))
                e_g = max(e_g, abs(q - gaunt(2, a, 2, b, 2, M, s=-2)))
    return float(e_s), float(e_t), float(e_g)


def check_gaunt_memory(run: str, R: int, t1: float) -> tuple[float, float]:
    """R h_20 by the Gaunt mode sum over quadrature, scalar and GW (z frame)."""
    s, g = scalar_rates(run, R), gw_rates(run, R)
    Ad, rs, rg = s["dmodes"], 0.0, 0.0
    for a in Ad:
        for b in Ad:
            rs = rs - MEM * gaunt(a[0], a[1], b[0], b[1], 2, 0) * np.real(Ad[a] * np.conj(Ad[b]))
    for m1 in range(-2, 3):
        for m2 in range(-2, 3):
            rg = rg + MEM * gaunt(2, m1, 2, m2, 2, 0, s=-2) * np.real(
                g["N"][m1] * np.conj(g["N"][m2])) / (16.0 * math.pi)
    return (window(s["t"], rs, 0.0, t1) / window(s["t"], s["mem_W"][0].real, 0.0, t1),
            window(g["t"], rg, 0.0, t1) / window(g["t"], g["mem"][0].real, 0.0, t1))


def check_reality(run: str, radii) -> float:
    """max |A_{l,-m} - (-1)^m conj(A_lm)| / max|A| over the record and spheres."""
    worst = 0.0
    for R in radii:
        _, A, P, _ = scalar_sphere(run, R)
        for D in (A, P):
            top = max(np.abs(v).max() for v in D.values())
            for (l, m), v in D.items():
                worst = max(worst, np.abs(D[l, -m] - (-1) ** m * np.conj(v)).max() / top)
    return worst


def check_psi4_symmetry(run: str, R: int, t1: float) -> float:
    """Equatorial symmetry of the orbits: max |Psi4_{2,-m} - conj(Psi4_2m)| / max|Psi4|."""
    t, psi = psi4_sphere(run, R)
    k = t <= t1
    top = max(np.abs(v[k]).max() for v in psi.values())
    return max(np.abs(psi[-m][k] - np.conj(psi[m][k])).max() for m in (1, 2)) / top


def check_pi(run: str, R: int, t1: float) -> tuple[float, float]:
    """Least-squares c in P_11 = c dA_11/dt to t1, and its relative residual:
    c ~ 1/alpha (order 1) means P = R Pi_lm; c ~ 1/R would mean Pi_lm."""
    t, A, P, _ = scalar_sphere(run, R)
    k = t <= t1
    d = ddt(t, A[1, 1])[k]
    c = np.vdot(d, P[1, 1][k]) / np.vdot(d, d)
    return float(c.real), float(np.linalg.norm(P[1, 1][k] - c * d) / np.linalg.norm(P[1, 1][k]))


def check_dipole_turn(run: str, R: int, t1: float) -> tuple[float, float, float, float]:
    """Net turn to t1 of arg A_11 and arg Psi4_22, and of the throat separation B - A
    to the sphere's retarded time (or the tracker's last fix, returned too): with
    Y_lm ~ e^{+i m phi}, A_11 ~ -(D_x - i D_y) turns OPPOSITE to the dipole D."""
    t, A, _, _ = scalar_sphere(run, R)
    pa = np.unwrap(np.angle(A[1, 1][t <= t1]))
    tr = stream(PACK / run / "throat_track.dat")
    dx, dy = tr["xB"] - tr["xA"], tr["yB"] - tr["yA"]
    ok = (tr["time"] <= t1 - R) & (np.hypot(dx, dy) > 1.0)   # the tracker loses merged throats
    ok &= np.cumsum(~ok) == 0
    sep = np.unwrap(np.arctan2(dy[ok], dx[ok]))
    tg, psi = psi4_sphere(run, R)
    ph = np.unwrap(np.angle(psi[2][tg <= t1]))
    return (float(pa[-1] - pa[0]), float(sep[-1] - sep[0]), float(tr["time"][ok][-1]),
            float(ph[-1] - ph[0]))


def check_axisymmetry_flip(R: int, t1: float) -> float:
    """Head-on: x-frame |h'_22| / |h'_20| of the GW memory with the z-frame m = +-2
    modes sign-flipped -- large means the standard relative sign is the data's."""
    th, ph, w = grid()
    Yx = frame_y2("x")
    t, psi = psi4_sphere(HEADON, R)
    N = {m: integ(t, psi[m]) * (-1.0 if abs(m) == 2 else 1.0) for m in psi}
    F = np.abs(sum(np.outer(N[m], sylm2(m, th, ph)) for m in N)) ** 2
    h = {m: window(t, F @ (w * np.conj(Yx[m])), first_common_mots(HEADON), t1) for m in (0, 2)}
    return abs(h[2]) / abs(h[0])


def paper_ratio(run: str, R: int, t_cut: float, estimator: str) -> float:
    """|E_phi| / E_GW exactly as plot_scalar_channel / waves_scalar_ratio."""
    g, s = gw_rates(run, R), scalar_rates(run, R)
    eg = window(g["t"], g["E_modes"], 0.0, t_cut)
    if estimator == "kin":
        return abs(window(s["t"], s["E_kin"], 0.0, t_cut)) / eg
    k = s["t"] <= t_cut
    return float(np.trapezoid(-s["E_W_modes"][k], s["t"][k]) / eg)


# ------------------------------------------------------------------ report
ROWS: list[dict] = []


def report_window(run: str, R: int, t0: float, t1: float, frame: str = "z", lz: float = 0.0) -> dict:
    b = budget(run, R, t0, t1, frame)
    hg, hw, hk = b["h_GW"][0].real, b["h_W"][0].real, b["h_kin"]
    tag = f"R={R} t<={t1:g} (u<={t1 - R:g})" if t0 == 0.0 else f"R={R} t=[{t0:g},{t1:g}]"
    flag = "  [kinematic flux net INGOING: wave-zone sums are near-zone here]" if b["inflow"] else ""
    note = NOTES.get((run, R), "")
    print(f"  {tag}{flag}" + (f"  [{note}]" if note else ""))
    band = band_gw(run, R, t1) if frame == "z" else None
    print(f"      energy  E_GW {b['E_GW']:.3e}" + (f" (band {band['E']:.3e})" if band else "")
          + f"  E_phi kin {b['E_kin']:+.3e} wz {b['E_W']:+.3e}"
          f"  |E_phi|/E_GW kin {abs(b['E_kin']) / b['E_GW']:.2f} wz {abs(b['E_W']) / b['E_GW']:.2f}"
          + (f" (band: {abs(b['E_kin']) / band['E']:.2f} / {abs(b['E_W']) / band['E']:.2f})" if band else ""))
    print(f"      memory  Rh20 GW {hg:+.3e}  phi wz {hw:+.3e} kin-norm {hk:+.3e}"
          f"  total {hg + hw:+.3e} .. {hg + hk:+.3e}  phi/GW {hw / hg:+.2f} .. {hk / hg:+.2f}"
          f"  per |E|: GW {hg / b['E_GW']:+.3f} phi {hw / abs(b['E_W']):+.3f}")
    h22 = b["h_GW"][2] + b["h_W"][2]
    print(f"              |Rh22| GW {abs(b['h_GW'][2]):.2e} phi {abs(b['h_W'][2]):.2e} total {abs(h22):.2e};"
          f"  |Rh21| GW {abs(b['h_GW'][1]):.0e} phi {abs(b['h_W'][1]):.0e}"
          + ("  (x frame: m' != 0 = axisymmetry residual)" if frame == "x" else ""))
    if lz != 0.0:
        jo, jm = m_over_omega(run, R, t1)
        print(f"      J_z     J_GW {b['J_GW']:+.3e}" + (f" (band {band['J']:+.3e})" if band else "")
              + f"  J_phi {b['J_phi']:+.3e}  J_phi/J_GW {b['J_phi'] / b['J_GW']:+.2f}"
              + (f" (band {b['J_phi'] / band['J']:+.2f})" if band else "")
              + f"  | E_phi/E_GW kin {b['E_kin'] / b['E_GW']:+.2f} wz {b['E_W'] / b['E_GW']:+.2f}"
              f"  | J_phi/L_z {b['J_phi'] / lz:+.3f}")
        print(f"              m/omega: burst dJ22/dE22 {jo:+.1f} vs 2/omega_22 {jm:+.1f} (median),"
              f" {band['two_over_omega_peak']:+.1f} (spectral peak); band J/E {band['J'] / band['E']:+.1f}")
    else:
        print(f"      J_z     null test (axisymmetric about x): J_GW {b['J_GW']:+.1e} J_phi {b['J_phi']:+.1e}")
    print(f"      radiative dipole (diagnostic): E_phi {b['E_rad']:+.3e} ({b['E_rad'] / b['E_W']:.2f} of wz)"
          f"  Rh20_phi {b['h_rad']:+.3e} (phi/GW {b['h_rad'] / hg:+.2f})"
          + (f"  J_phi {b['J_rad']:+.3e} (J_phi/J_GW {b['J_rad'] / b['J_GW']:+.2f})" if lz != 0.0 else "")
          + f"  |E_phi|/E_GW {abs(b['E_rad']) / b['E_GW']:.2f}"
          + (f" (band {abs(b['E_rad']) / band['E']:.2f})" if band else ""))
    row = dict(run=run, R=R, t0=t0, t1=t1, lz=lz, band=band, **b)
    ROWS.append(row)
    return row


def report_sensitivity(run: str, R: int, t1: float, frame: str = "z", t0: float = 0.0) -> None:
    ref = budget(run, R, t0, t1, frame)
    alt = {"spline dA/dt": dict(deriv="spline"), "trapezoid news": dict(rule="trapezoid"),
           "cadence x2": dict(stride=2)}
    keys = (("h_GW", lambda b: b["h_GW"][0].real), ("h_phi", lambda b: b["h_W"][0].real),
            ("E_phi", lambda b: b["E_W"]), ("E_GW", lambda b: b["E_GW"]))
    if frame == "z":            # J_z is a null quantity on the head-on: no relative change
        keys += (("J_GW", lambda b: b["J_GW"]), ("J_phi", lambda b: b["J_phi"]))
    tag = f"{run.split('/')[-1][:12]} R={R} t<={t1:g}"
    for name, kw in alt.items():
        b = budget(run, R, t0, t1, frame, **kw)
        print(f"  {tag} {name:14s}: " + "  ".join(f"{k} {f(b) / f(ref) - 1:+.1%}" for k, f in keys))
    print(f"  {tag} estimators    : E_phi kin {ref['E_kin']:+.3e} W {ref['E_W']:+.3e} X {ref['E_X']:+.3e}"
          f" P {ref['E_P']:+.3e};  Rh20_phi W {ref['h_W'][0].real:+.3e} X {ref['h_X'][0].real:+.3e}"
          f" P {ref['h_P'][0].real:+.3e};  J_phi W {ref['J_phi']:+.3e} P {ref['J_P']:+.3e}")


def verdict() -> None:
    orb = [r for r in ROWS if r["lz"] != 0.0]
    hon = [r for r in ROWS if r["lz"] == 0.0]
    same = lambda a, b: np.sign(a) == np.sign(b)
    n_w = sum(same(r["h_W"][0].real, r["h_GW"][0].real) for r in ROWS)
    bad_k = [f"{r['run'].split('/')[0][3:]} R={r['R']} t<={r['t1']:g}" for r in ROWS
             if not same(r["h_kin"], r["h_GW"][0].real)]
    print(f"\n[verdict 7] scalar (2,0) memory has the GW's sign on {n_w}/{len(ROWS)} windows (wave-zone),"
          f" {len(ROWS) - len(bad_k)}/{len(ROWS)} (kin-norm)"
          + (f"; exceptions {', '.join(bad_k)} -- each a net-INGOING kinematic window" if bad_k else ""))
    for run, rows in ((FLYBY, orb), (SPIRAL, orb), (HEADON, hon)):
        rows = [r for r in rows if r["run"] == run]
        r_w = [r["h_W"][0].real / r["h_GW"][0].real for r in rows]
        r_k = [r["h_kin"] / r["h_GW"][0].real for r in rows if not r["inflow"]]
        print(f"            {run.split('/')[0][3:]:13s}: h_phi/h_GW {min(r_w):+.2f} .. {max(r_w):+.2f} (wz),"
              f" {min(r_k):+.2f} .. {max(r_k):+.2f} (kin-norm, outflow windows only)")
    val = [r for r in ROWS if r["run"] == HEADON or (r["run"] == FLYBY and r["t1"] - r["R"] <= U_RAD)]
    n_rad = sum(same(r["h_rad"], r["h_GW"][0].real) for r in val)
    r_rad = [r["h_rad"] / r["h_GW"][0].real for r in val if r["run"] == FLYBY]
    r_hon = [r["h_rad"] / r["h_GW"][0].real for r in val if r["run"] == HEADON]
    print(f"            radiative dipole, where the spheres validate it (fly-by u <= {U_RAD:g}, head-on):"
          f" same sign on {n_rad}/{len(val)}; h_phi/h_GW fly-by {min(r_rad):+.2f} .. {max(r_rad):+.2f},"
          f" head-on {min(r_hon):+.2f} .. {max(r_hon):+.2f}")
    out = [r for r in orb if not r["inflow"]]
    inf = [r for r in orb if r["inflow"]]
    n_gw = sum(same(r["J_GW"], r["lz"]) for r in orb)
    n_phi = sum(not same(r["J_phi"], r["lz"]) for r in out)
    n_p = sum(not same(r["J_P"], r["lz"]) for r in out)
    vo = [r for r in val if r["lz"] != 0.0]
    n_r = sum(not same(r["J_rad"], r["lz"]) for r in vo)
    n_i = sum(not same(r["J_phi"], r["lz"]) for r in inf)
    print(f"[verdict 8] J_GW has the orbit's sign on {n_gw}/{len(orb)} orbital windows; physical J_phi is"
          f" OPPOSITE to the orbit on {n_phi}/{len(out)} outflow windows (Pi-based {n_p}/{len(out)},"
          f" radiative dipole {n_r}/{len(vo)} validated fly-by windows; on the {len(inf)} net-inflow"
          f" windows {n_i}/{len(inf)}, not a measurement) -> the ghost channel pumps angular momentum"
          f" into the orbit")
    for run in (FLYBY, SPIRAL):
        rows = [r for r in out if r["run"] == run]
        r_j = [r["J_phi"] / r["J_GW"] for r in rows]
        r_l = [r["J_phi"] / r["lz"] for r in rows]
        r_r = [r["J_rad"] / r["J_GW"] for r in vo if r["run"] == run]
        print(f"            {run.split('/')[0][3:]:13s}: J_phi/J_GW {min(r_j):+.2f} .. {max(r_j):+.2f}"
              + (f" (radiative dipole, validated: {min(r_r):+.2f} .. {max(r_r):+.2f})" if r_r else "")
              + f"; J_phi/L_z {min(r_l):+.3f} .. {max(r_l):+.3f}")


def main() -> int:
    print("Nonlinear memory and J_z of the two channels.  Code units (M_throat = 1; the paper's"
          " M = 2).  Every scalar number carries the PHYSICAL (ghost) sign.")

    # -- the conventions, on the data
    e_s, e_t, e_g = check_orthonormal()
    print(f"\n[check] orthonormality on the {N_THETA}x{N_PHI} grid: Y_lm {e_s:.0e}, _-2Y_2m {e_t:.0e};"
          f" every product integral vs its Gaunt/3j value {e_g:.0e}")
    gs, gg = check_gaunt_memory(FLYBY, 30, 60.0)
    print(f"[check] fly-by R=30 t<=60 Rh20 by Gaunt mode sum / quadrature: scalar {gs:.12f}, GW {gg:.12f}")
    for run, radii in ((FLYBY, (14, 30)), (SPIRAL, (14, 30)), (HEADON, (10, 14, 18))):
        print(f"[check] reality A_l,-m = (-1)^m conj(A_lm) (and Pi) on {run.split('/')[-1]}:"
              f" {check_reality(run, radii):.0e} (bit-exact: the consumer writes -m from +m)")
    for run, R, t1 in ((FLYBY, 30, 80.0), (FLYBY, 14, 64.0), (SPIRAL, 30, 50.0), (SPIRAL, 14, 50.0)):
        print(f"[check] equatorial symmetry |Psi4_2,-m - conj(Psi4_2m)|/max, {run.split('/')[0][3:]}"
              f" R={R}: {check_psi4_symmetry(run, R, t1):.0e}")
    for run, R, t1 in ((SPIRAL, 30, 50.0), (SPIRAL, 14, 50.0), (FLYBY, 30, 80.0), (FLYBY, 14, 64.0),
                       (HEADON, 18, 100.0), (HEADON, 10, 100.0)):
        c, res = check_pi(run, R, t1)
        print(f"[check] 'Pi'_11 = c dA_11/dt, {run.split('/')[0][3:]} R={R}: c = {c:.3f}"
              f" (resid {res:.2f}); c ~ 1/alpha, not 1/R: the columns are R Pi_lm")
    for run, R, t1 in ((FLYBY, 30, 80.0), (FLYBY, 14, 64.0), (SPIRAL, 14, 50.0), (SPIRAL, 30, 50.0)):
        ta, ts, t_s, tp = check_dipole_turn(run, R, t1)
        print(f"[check] turn to t={t1:g}, {run.split('/')[0][3:]} R={R}: throat separation"
              f" {math.degrees(ts):+.0f} deg (source to t={t_s:.0f}), arg A_11 {math.degrees(ta):+.0f} deg,"
              f" arg Psi4_22 {math.degrees(tp):+.0f} deg: clockwise orbit, e^(+i m phi) harmonics")
    for key, ref in PAPER_RATIO.items():
        got = paper_ratio(FLYBY, key[1], key[2], key[0])
        print(f"[check] fly-by |E_phi|/E_GW ({key[0]}) R={key[1]} t={key[2]:g}: {got:.4f} (paper {ref})")
    t0 = first_common_mots(HEADON)
    for R, ref in PAPER_POST.items():
        got = window(scalar_rates(HEADON, R)["t"], scalar_rates(HEADON, R)["E_kin"], t0, 100.0)
        print(f"[check] head-on post-horizon E_phi (t >= {t0:g}) R={R}: {got:+.5f} (paper {ref:+.4f})")
    print(f"[check] head-on x-axisymmetry with the m=+-2 sign flipped: |h'22|/|h'20| ="
          f" {check_axisymmetry_flip(14, T_REFLECT):.2f} (unflipped: see the x-frame rows)")
    for R in (14, 30):
        tx = mouth_crossing(FLYBY, R)
        print(f"[check] fly-by mouth areal radius passes R={R} at t = {tx:.1f}")

    # -- (7) and (8) on the orbits
    for name, run, cuts in (("fly-by p = 0.45", FLYBY,
                             {14: (44.0, 59.0, 60.0, 14 + U_GATE), 30: (55.0, 60.0, 65.0, 75.0, 30 + U_GATE)}),
                            ("spiral p = 0.12 (level 3, record to t = 50)", SPIRAL,
                             {14: (45.0, 50.0), 30: (45.0, 50.0)})):
        lz = orbital_lz(run)
        print(f"\n== {name}: L_z = {lz:+.2f} (orbital J along {'-' if lz < 0 else '+'}z)")
        for R, tends in cuts.items():
            for t1 in tends:
                report_window(run, R, 0.0, t1, "z", lz)

    # -- the head-on: memory about the collision axis, post-horizon window
    print(f"\n== head-on d = 8: L_z = {orbital_lz(HEADON):+.2f}; memory about the collision (x) axis;"
          f" both channels from the common MOTS, t0 = {t0:g}")
    for R in (10, 14, 18):
        for t1 in (65.0, T_REFLECT, 75.0, 95.0, 100.0):
            report_window(HEADON, R, t0, t1, "x")
        b = budget(HEADON, R, t0, T_REFLECT, "x", t0_gw=0.0)
        print(f"  R={R}: GW from t = 0 to {T_REFLECT:g} instead: E_GW {b['E_GW']:.3e},"
              f" Rh20_GW {b['h_GW'][0].real:+.3e}")

    # -- the sphere spread at equal retarded time (fly-by)
    print("\n[spread] R=14 / R=30 at equal u = t - R (the paper's near-zone error bar); 'rad' ="
          " the radiative-dipole diagnostic, solved on each sphere independently:")
    for run in (FLYBY, SPIRAL):
        f14, f30 = dipole_radiative(run, 14)["F0"], dipole_radiative(run, 30)["F0"]
        print(f"  {run.split('/')[0][3:]}: static dipole R A_11(0) = {f14.real:.3f} (R=14), {f30.real:.3f} (R=30)")
        for u in ((20.0,) if run == SPIRAL else (20.0, 30.0, 35.0, U_GATE)):
            a, c = budget(run, 14, 0.0, 14 + u), budget(run, 30, 0.0, 30 + u)
            print(f"    u={u:g}: E_GW {a['E_GW'] / c['E_GW']:.2f}  E_phi kin {a['E_kin'] / c['E_kin']:.2f}"
                  f" wz {a['E_W'] / c['E_W']:.2f} rad {a['E_rad'] / c['E_rad']:.2f}"
                  f"  Rh20 GW {a['h_GW'][0].real / c['h_GW'][0].real:.2f} phi {a['h_W'][0].real / c['h_W'][0].real:.2f}"
                  f" rad {a['h_rad'] / c['h_rad']:.2f}  J_GW {a['J_GW'] / c['J_GW']:.2f}"
                  f" J_phi {a['J_phi'] / c['J_phi']:.2f} rad {a['J_rad'] / c['J_rad']:.2f}"
                  f"  [rad at R=30: E_phi {c['E_rad']:+.4f} J_phi {c['J_rad']:+.4f} Rh20 {c['h_rad']:+.4f}]")
    for R, t1 in ((30, 60.0), (30, 80.0), (14, 44.0)):
        data, rad, near = dipole_kin_split(FLYBY, R, t1)
        c, _ = check_pi(FLYBY, R, t1)
        print(f"  fly-by R={R} t<={t1:g}: canonical kinematic integral {data:.4f} = model {rad + near:.4f}"
              f" (radiated {rad:.4f} + stored near field {near:+.4f}) x {data / (rad + near):.2f}"
              f" [the Pi/(dA/dt) factor there: {c:.2f}]")
    for u in (30.0, 40.0):
        (r14, n14), (r30, n30) = gw_nakano_energy(FLYBY, 14, 14 + u), gw_nakano_energy(FLYBY, 30, 30 + u)
        print(f"  fly-by GW u={u:g}: E_GW R=14/R=30 {r14 / r30:.2f} raw, {n14 / n30:.2f} with the first-order"
              f" Nakano correction -- no convergence at omega R ~ 1.4-3, so the GW spread stays")
    hs = {R: budget(HEADON, R, 0.0, R + 45.0, "x") for R in (10, 14, 18)}
    print("  head-on to u = 45 (from t = 0), R = 10/14/18: E_phi wz "
          + "/".join(f"{hs[R]['E_W']:+.4f}" for R in hs) + "  kin " + "/".join(f"{hs[R]['E_kin']:+.4f}" for R in hs)
          + "  rad " + "/".join(f"{hs[R]['E_rad']:+.4f}" for R in hs)
          + "  E_GW " + "/".join(f"{hs[R]['E_GW']:.4f}" for R in hs))

    # -- cadence, integration rule, estimator
    print("\n[sensitivity] change against the reference (np.gradient dA/dt, paper cumsum news, full cadence)")
    for run, R, t1, frame, t_0 in ((FLYBY, 14, 60.0, "z", 0.0), (FLYBY, 14, 64.0, "z", 0.0),
                                   (FLYBY, 30, 60.0, "z", 0.0), (FLYBY, 30, 80.0, "z", 0.0),
                                   (SPIRAL, 14, 50.0, "z", 0.0), (SPIRAL, 30, 50.0, "z", 0.0),
                                   (HEADON, 10, T_REFLECT, "x", t0), (HEADON, 18, T_REFLECT, "x", t0),
                                   (HEADON, 18, 100.0, "x", t0)):
        report_sensitivity(run, R, t1, frame, t_0)
    imag = max(scalar_rates(r, R)["imag"] for r, R in ((FLYBY, 14), (FLYBY, 30), (SPIRAL, 14), (HEADON, 10)))
    jq = max(abs(r["J_phi"] / r["J_modes"] - 1.0) for r in ROWS if r["lz"] != 0.0)
    print(f"  (imaginary residue of the reconstructed fields <= {imag:.0e}; J_phi by quadrature"
          f" -oint dA d_phi A vs the mode sum sum m Im(conj(dA_lm) A_lm): {jq:.0e})")

    verdict()
    return 0


if __name__ == "__main__":
    sys.exit(main())
