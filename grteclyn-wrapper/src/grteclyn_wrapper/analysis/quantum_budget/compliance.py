"""The compliance-factor evaluator: F of one saved Solution.

Composition over inheritance: the evaluator takes a quantum inequality and
a sampling policy as small strategy objects, so a tighter bound
(Fewster-Eveson) or another validity scale slots in without touching the
measurement; the observer class is stress.rho_stationary (see its
docstring for why the stationary class is the rigorous v1).

Two numbers per solution, deliberately distinct:

- fhat: the Ford-Roman accounting -- the bound at the WORST-DENSITY point,
  with the sampling window set by the local curvature scale there.  Finite,
  anchor-comparable, the F(v_e) curve's ordinate.
- fhat_field_max: max over the grid of the pointwise rho ell_c^4 budget.
  For these phantom-supported families rho < 0 all the way out while
  ell_c grows, so this DIVERGES with the sampled volume: every member is
  tail-illegal, which is the standing argument for the thin-band brick
  (job F4).  It is reported (with its location) to document that, never
  as the curve.

Self-convergence (job F1's acceptance): the worst-density point is
polished off the grid (Nelder-Mead on the spectral evaluation), then fhat
is re-measured starting from refined interior Chebyshev grids; the change
between the last two passes gates the search's robustness.  The solution
grid itself drops out of point values, so the physical grid-change test is
cross-leg agreement at equal v_e (fam_a_r1 against fam_a_log: different
maps AND different solver grids).  ricci_defect is carried as the
independent correctness gate on the curvature lambdas.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from ..spinning_wormhole.observables import C_GATE
from ..spinning_wormhole.solution import Solution
from . import conventions as cv
from . import curvature, stress

__all__ = ["FordRomanScalar", "CurvatureSampling", "ComplianceEvaluator",
           "ComplianceResult"]


@dataclass(frozen=True)
class FordRomanScalar:
    """rho >= -coeff * hbar / tau0^4 (massless scalar, Lorentzian window);
    hbar = 1 with the code length unit read as one Planck length."""

    coeff: float = cv.BOUND_COEFF

    def rho_bound(self, tau0: np.ndarray) -> np.ndarray:
        return -self.coeff / tau0**4


@dataclass(frozen=True)
class CurvatureSampling:
    """tau0 = fraction * ell_c; fraction = 1 is the anchor convention and
    cancels from every F(v_e) / F(0) ratio (conventions.py)."""

    fraction: float = 1.0

    def tau0(self, work: dict) -> np.ndarray:
        return self.fraction * curvature.ell_curvature(work["R"])


@dataclass(frozen=True)
class ComplianceResult:
    fhat: float                    # Ford-Roman accounting at the worst density
    fhat_refinements: tuple[float, ...]
    fhat_conv: float               # |last - previous| / last
    rho_min: float
    eta_star: float                # where the worst density sits
    theta_star: float
    ell_c_star: float
    ell_k_star: float              # Kretschmann^(-1/4) there (cross-check)
    tau0_star: float
    fhat_field_max: float          # pointwise budget max on the masked grid
    eta_field_max: float           # ... and where (the tail-illegality probe)
    ricci_defect: float

    def as_row(self) -> dict:
        return {k: getattr(self, k) for k in (
            "fhat", "fhat_conv", "rho_min", "eta_star", "theta_star",
            "ell_c_star", "ell_k_star", "tau0_star", "fhat_field_max",
            "eta_field_max", "ricci_defect")}


@dataclass
class ComplianceEvaluator:
    qi: FordRomanScalar = field(default_factory=FordRomanScalar)
    sampling: CurvatureSampling = field(default_factory=CurvatureSampling)
    refinements: tuple[float, ...] = (1.0, 1.5, 2.0)
    min_nodes: tuple[int, int] = (96, 24)
    c_gate: float = C_GATE

    def _grid(self, sol: Solution, factor: float) -> tuple[np.ndarray, np.ndarray]:
        """Interior Chebyshev points, denser than the solution's nodes."""
        mx = max(int(round(factor * (sol.nx + 1))), self.min_nodes[0])
        my = max(int(round(factor * (sol.ny + 1))), self.min_nodes[1])
        xi = np.cos(np.pi * np.arange(1, mx) / mx)[::-1]
        y = np.cos(np.pi * np.arange(1, my) / my)[::-1]
        return xi, y

    def _point(self, sol: Solution, d2: float, xi: float, y: float) -> dict:
        """The full set at one (xi, y): the spectral solution evaluates
        anywhere, so point values are grid-free."""
        work = curvature.frame_riemann(sol, np.array([xi]), np.array([y]))
        rho = float(stress.rho_stationary(work, d2)[0, 0])
        tau0 = float(self.sampling.tau0(work)[0, 0])
        return {
            "fhat": max(0.0, -rho) / abs(float(self.qi.rho_bound(tau0))),
            "rho_min": rho,
            "eta_star": float(work["eta"][0, 0]),
            "theta_star": float(work["theta"][0, 0]),
            "ell_c_star": tau0 / self.sampling.fraction,
            "ell_k_star": float(kretschmann_scale(work)[0, 0]),
            "tau0_star": tau0,
        }

    def _measure_once(self, sol: Solution, d2: float, factor: float) -> dict:
        from scipy.optimize import minimize

        xi, y = self._grid(sol, factor)
        work = curvature.frame_riemann(sol, xi, y)
        rho = stress.rho_stationary(work, d2)
        tau0 = self.sampling.tau0(work)
        fhat_grid = np.maximum(0.0, -rho) / np.abs(self.qi.rho_bound(tau0))
        mask = sol.eta0**2 / work["h"] >= self.c_gate**2
        rho_m = np.where(mask, rho, np.inf)
        i, j = np.unravel_index(np.argmin(rho_m), rho.shape)
        fhat_m = np.where(mask, fhat_grid, -np.inf)
        k, l = np.unravel_index(np.argmax(fhat_m), fhat_grid.shape)
        # Polish the worst-density point off the grid (the node nearest the
        # extremum moves with the grid and costs ~1e-2 in fhat if kept).
        m = sol.radial_map
        eta_max = sol.eta0 * math.sqrt(1.0 / self.c_gate**2 - 1.0)
        xi_hi = float(m.xi_of_eta(np.array([eta_max]))[0])
        opt = minimize(
            lambda p: float(stress.rho_stationary(
                curvature.frame_riemann(sol, np.array([p[0]]),
                                        np.array([p[1]])), d2)[0, 0]),
            [float(xi[i]), float(y[j])], method="Nelder-Mead",
            bounds=[(-xi_hi, xi_hi), (-0.9999, 0.9999)],
            options={"xatol": 1e-9, "fatol": 1e-18})
        out = self._point(sol, d2, float(opt.x[0]), float(opt.x[1]))
        out["fhat_field_max"] = float(fhat_grid[k, l])
        out["eta_field_max"] = float(work["eta"][k, l])
        out["ricci_defect"] = curvature.ricci_defect(work, d2, mask)
        return out

    def measure(self, sol: Solution) -> ComplianceResult:
        d2 = stress.d_charge_sq(sol)
        passes = [self._measure_once(sol, d2, f) for f in self.refinements]
        fhats = tuple(p["fhat"] for p in passes)
        conv = (abs(fhats[-1] - fhats[-2]) / abs(fhats[-1])
                if len(fhats) > 1 else math.nan)
        last = passes[-1]
        return ComplianceResult(
            fhat=fhats[-1], fhat_refinements=fhats, fhat_conv=conv,
            **{k: last[k] for k in last if k != "fhat"})


def kretschmann_scale(work: dict) -> np.ndarray:
    """|K|^(-1/4): the one-scalar curvature scale, reported beside ell_c
    (K is a Lorentzian contraction, so its sign is not fixed)."""
    k = np.abs(curvature.kretschmann(work["R"]))
    return np.maximum(k, 1e-300) ** -0.25
