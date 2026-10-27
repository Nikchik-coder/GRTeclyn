"""Walk the saved solution legs and build the F(v_e) table.

The source of truth is results/spinningwormhole/solutions/<leg>/ (one
continuation branch per leg, .npz + .json per converged step; its README
has the v_e ranges).  The static members are not on disk -- the legs start
at finite spin -- so static_anchor() synthesizes them in closed form
(f linear in x, omega = nu = 0) and they run through the same evaluator,
anchoring the curve at v_e = 0 against conventions.static_ellis_fhat.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from ..spinning_wormhole import conventions as spin_cv
from ..spinning_wormhole import spectral
from ..spinning_wormhole.solution import Solution
from . import conventions as cv
from .compliance import ComplianceEvaluator

__all__ = ["solution_paths", "static_anchor", "measure_solution",
           "measure_catalogue", "ROW_FIELDS"]

ROW_FIELDS = [
    "leg", "step", "family", "eta0", "gamma", "v_e", "J", "M_ADM", "R_eq",
    "D", "fhat", "fhat_conv", "fhat_over_Req2", "fhat_over_M2",
    "log10_F_1m", "max_planck_throat", "rho_min", "eta_star", "theta_star",
    "ell_c_star", "ell_k_star", "tau0_star", "fhat_field_max",
    "eta_field_max", "ricci_defect", "nx", "ny",
]


def solution_paths(root: Path, leg: str) -> list[Path]:
    return sorted((Path(root) / leg).glob(f"{leg}_*.npz"))


def static_anchor(eta0: float, gamma: float, nx: int = 96,
                  ny: int = 24) -> Solution:
    """The v_e = 0 member of a family, in closed form (solver P0 gate)."""
    sx, _ = spectral.lobatto(nx)
    f = spin_cv.static_f_of_x(sx, gamma)[:, None] * np.ones((1, ny + 1))
    zeros = np.zeros_like(f)
    sol = Solution(eta0=eta0, gamma=gamma, omega_inf=0.0, map_name="arctan",
                   map_params={}, F=f, W=zeros.copy(), N=zeros.copy())
    obs = spin_cv.static_member(eta0, gamma)
    eta_t = obs["eta_throat"]
    x_t = (2.0 / math.pi) * math.atan2(eta_t, eta0)
    f_t = spin_cv.static_f_of_x(x_t, gamma)
    obs["R_eq"] = math.exp(-0.5 * f_t) * math.sqrt(eta_t**2 + eta0**2)
    sol.observables = obs
    sol.gates = {"D2_median": obs["D"] ** 2}
    return sol


def measure_solution(sol: Solution, evaluator: ComplianceEvaluator,
                     leg: str, step: int) -> dict:
    res = evaluator.measure(sol)
    obs = sol.observables
    r_eq = float(obs.get("R_eq", math.nan))
    m_adm = float(obs.get("M_ADM", math.nan))
    per_req2 = res.fhat / r_eq**2
    row = {
        "leg": leg, "step": step,
        "family": "b" if abs(sol.gamma) < 1e-12 else "a",
        "eta0": sol.eta0, "gamma": sol.gamma,
        "v_e": float(obs.get("v_e", math.nan)),
        "J": float(obs.get("J", math.nan)),
        "M_ADM": m_adm, "R_eq": r_eq,
        "D": math.sqrt(float(sol.gates.get("D2_median",
                                           float(obs.get("D", math.nan))**2))),
        "fhat_over_Req2": per_req2,
        "fhat_over_M2": res.fhat / m_adm**2 if m_adm else math.nan,
        "log10_F_1m": math.log10(cv.f_physical(per_req2, 1.0)),
        "max_planck_throat": cv.max_planck_throat(per_req2),
        "nx": sol.nx, "ny": sol.ny,
    }
    row.update(res.as_row())
    return row


def measure_catalogue(root: Path, legs: list[str],
                      evaluator: ComplianceEvaluator,
                      static_anchors: bool = True,
                      log=print) -> list[dict]:
    rows = []
    if static_anchors:
        for eta0, gamma in ((2.0, -math.pi), (1.0, 0.0)):
            sol = static_anchor(eta0, gamma)
            rows.append(measure_solution(sol, evaluator, "static", -1))
            log(f"static eta0 {eta0} gamma {gamma:.4f}: "
                f"fhat {rows[-1]['fhat']:.6g} conv {rows[-1]['fhat_conv']:.1e}")
    for leg in legs:
        paths = solution_paths(root, leg)
        for path in paths:
            step = int(path.stem.rsplit("_", 1)[1])
            sol = Solution.load(path)
            rows.append(measure_solution(sol, evaluator, leg, step))
        if paths:
            log(f"{leg}: {len(paths)} solutions, v_e "
                f"{min(r['v_e'] for r in rows if r['leg'] == leg):.3f}"
                f"-{max(r['v_e'] for r in rows if r['leg'] == leg):.3f}")
    return rows
