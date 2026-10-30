"""Optional search knobs stay off the default four-knob walk."""

import numpy as np
import pytest

from grteclyn_wrapper.optimisation.knobs import bill_name, knob_vector, pin_held


def test_default_pin_is_equatorial():
    th = {"R_e": 4.06, "area_throat": 200.0}
    assert pin_held("R_e", th) == ("R_e", 4.06)
    assert bill_name("R_e") == "X"


def test_area_pin_scores_per_areal_radius():
    th = {"R_e": 4.06, "area_throat": 200.0}
    assert pin_held("area", th) == ("area", 200.0)
    assert bill_name("area") == "X_A"


def test_knob_vector_default_is_four():
    x = knob_vector([0.3, 0.0, 0.0, 0.0], free_j=False, j_start=1.2)
    np.testing.assert_array_equal(x, [0.3, 0.0, 0.0, 0.0])


def test_knob_vector_appends_j_when_free():
    x = knob_vector([0.3, 0.0, 0.0, 0.0], free_j=True, j_start=1.2)
    np.testing.assert_allclose(x, [0.3, 0.0, 0.0, 0.0, 1.2])


def test_knob_vector_keeps_explicit_j():
    x = knob_vector([0.3, 0.1, 0.0, 0.0, 0.8], free_j=True, j_start=1.2)
    np.testing.assert_allclose(x, [0.3, 0.1, 0.0, 0.0, 0.8])


def test_knob_vector_rejects_j_without_flag():
    with pytest.raises(ValueError):
        knob_vector([0.3, 0.0, 0.0, 0.0, 0.8], free_j=False, j_start=1.2)
