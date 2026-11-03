"""Origin-sensitive spectral interpolation, independent of a JAX backend."""
import numpy as np

from grteclyn_wrapper.optimisation.railgun.geometry import interpolation_coefficients


def test_constant_has_no_artificial_endpoint_curvature():
    values = np.full((225, 29), -4.614103134949752)
    coefficients = interpolation_coefficients(values)
    for axis in (0, 1):
        for order in (1, 2):
            derivative = np.polynomial.chebyshev.chebder(coefficients, m=order, axis=axis)
            assert np.max(np.abs(derivative)) < 1e-12
    np.testing.assert_allclose(coefficients[0, 0], values[0, 0], atol=1e-15)


def test_tensor_modes_and_endpoints_round_trip_without_filtering():
    x = np.cos(np.pi*np.arange(225)/224)
    y = np.cos(np.pi*np.arange(29)/28)
    coefficients = np.zeros((225, 29))
    coefficients[0, 0] = -4.6
    coefficients[7, 3] = .025
    coefficients[221, 27] = 1e-11
    xx, yy = np.meshgrid(x, y, indexing="ij")
    values = np.polynomial.chebyshev.chebval2d(xx, yy, coefficients)
    result = interpolation_coefficients(values)
    np.testing.assert_allclose(result, coefficients, atol=5e-15, rtol=0)
    np.testing.assert_allclose(np.polynomial.chebyshev.chebval2d(xx, yy, result),
                               values, atol=1e-14, rtol=0)
