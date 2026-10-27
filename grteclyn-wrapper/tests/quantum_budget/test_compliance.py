"""Job F1 gates: closed forms on the static members, the contracted field
equation on a rotating solution, and the anchor value.

The first call builds the frame-Riemann lambdas (sympy, cached per
process), so this file is minutes-slow on first run by design.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

from grteclyn_wrapper.analysis.quantum_budget import conventions as cv
from grteclyn_wrapper.analysis.quantum_budget import curvature, stress
from grteclyn_wrapper.analysis.quantum_budget.catalogue import (
    measure_solution, static_anchor,
)
from grteclyn_wrapper.analysis.quantum_budget.compliance import (
    ComplianceEvaluator,
)

REPO = Path(__file__).resolve().parents[2].parent
FAM_A_SOLUTION = (REPO / "results/spinningwormhole/solutions/fam_a_r1"
                  / "fam_a_r1_0016.npz")


def _grid(n=24, m=12):
    xi = np.cos(np.pi * np.arange(1, n) / n)[::-1]
    y = np.cos(np.pi * np.arange(1, m) / m)[::-1]
    return xi, y


def test_massless_ellis_frame_riemann_closed_form():
    """eta0 = 1, gamma = 0: R_(1212) = R_(1313) = -a^2/h^2,
    R_(2323) = +a^2/h^2, every other component 0; ell_c = h/a."""
    sol = static_anchor(1.0, 0.0, nx=48, ny=12)
    xi, y = _grid()
    work = curvature.frame_riemann(sol, xi, y)
    h = work["h"]
    expect = {((1, 2), (1, 2)): -1.0 / h**2,
              ((1, 3), (1, 3)): -1.0 / h**2,
              ((2, 3), (2, 3)): 1.0 / h**2}
    for key, comp in work["R"].items():
        want = expect.get(key, np.zeros_like(h))
        assert np.max(np.abs(comp - want) * h**2) < 1e-9, key
    ell = curvature.ell_curvature(work["R"])
    assert np.max(np.abs(ell - h)) < 1e-8
    rho = stress.rho_stationary(work, stress.d_charge_sq(sol))
    assert np.max(np.abs(rho + 1.0 / (8.0 * math.pi * h**2)) * h**2) < 1e-12


def test_static_anchor_fhat_matches_closed_form():
    """The pipeline's massless-Ellis fhat is (4 pi / 3) a^2 at the throat."""
    sol = static_anchor(1.0, 0.0, nx=48, ny=12)
    row = measure_solution(sol, ComplianceEvaluator(), "static", -1)
    assert abs(row["fhat"] - cv.static_ellis_fhat(1.0)) < 1e-6
    assert abs(row["R_eq"] - 1.0) < 1e-12
    assert row["fhat_conv"] < 1e-8
    assert row["ricci_defect"] < 1e-8
    # The tail-illegality probe: the pointwise budget grows off the throat.
    assert row["fhat_field_max"] > 10.0 * row["fhat"]


def test_massive_static_member_field_equation():
    """Family (a)'s static member (gamma = -pi): nontrivial f exercises the
    exp factors; the contracted field equation convicts a wrong lambda."""
    sol = static_anchor(2.0, -math.pi, nx=64, ny=12)
    row = measure_solution(sol, ComplianceEvaluator(), "static", -1)
    assert row["ricci_defect"] < 1e-8
    assert row["fhat_conv"] < 1e-7
    assert row["fhat"] > 0.0


@pytest.mark.skipif(not FAM_A_SOLUTION.exists(),
                    reason="solution catalogue not checked out")
def test_rotating_solution_gates():
    """A mid-spin family (a) solution: omega and nu nonzero, so every
    frame component contributes; the unimposed contraction must still
    close and fhat must self-converge."""
    from grteclyn_wrapper.analysis.spinning_wormhole.solution import Solution

    sol = Solution.load(FAM_A_SOLUTION)
    row = measure_solution(sol, ComplianceEvaluator(), "fam_a_r1", 16)
    assert row["ricci_defect"] < 1e-6
    assert row["fhat_conv"] < 1e-5
    assert row["fhat"] > 0.0
    assert row["rho_min"] < 0.0
