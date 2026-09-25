"""gw_search.lisa: the strain a figure draws carries the SNR the text quotes."""

from __future__ import annotations

import dataclasses
import math

import numpy as np
import pytest

from grteclyn_wrapper.gw_search import lisa


@dataclasses.dataclass
class _Burst:
    """The fields of templates.nr.NRWaveform that lisa reads."""

    H: np.ndarray
    dt_M: float
    f0: float
    mode: str = "(2,2)"


def _burst() -> _Burst:
    u = np.arange(-200.0, 200.0, 0.25)
    H = np.exp(-(u / 15.0) ** 2) * np.exp(2j * math.pi * 0.05 * u)
    return _Burst(H=H, dt_M=0.25, f0=0.02)


@pytest.mark.parametrize("variant", ["nominal", "conservative"])
@pytest.mark.parametrize("mass", [1e4, 1e5, 1e6])
def test_characteristic_strain_integrates_to_snr(variant, mass):
    """int (h_c / h_n)^2 dln f over the drawn track is snr^2 with the same arguments."""
    wf = _burst()
    spec = lisa.spectrum(wf)
    f99 = lisa.energy_quantile(spec, 0.99)
    rho = lisa.snr(wf, spec, mass, 20.0, variant, f99)
    f, hc = lisa.characteristic_strain(wf, spec, mass, 20.0, variant, f99)
    area = np.trapezoid((hc / lisa.noise_strain(f, variant)) ** 2, np.log(f))
    assert rho > 0.0
    assert math.sqrt(area) == pytest.approx(rho, rel=0.02)


def test_snr_scales_with_distance_at_fixed_frequency():
    """At fixed observed frequencies the SNR is amplitude over noise: halving
    D_c at the same M(1+z) doubles it (the M / D_c scaling of the module)."""
    wf = _burst()
    spec = lisa.spectrum(wf)
    f99 = lisa.energy_quantile(spec, 0.99)
    z1, z2 = 20.0, 10.0
    m1 = 1e5
    m2 = m1 * (1.0 + z1) / (1.0 + z2)            # same M_z: same frequencies
    r1 = lisa.snr(wf, spec, m1, z1, "nominal", f99)
    r2 = lisa.snr(wf, spec, m2, z2, "nominal", f99)
    dc1, dc2 = lisa.comoving_distance_mpc(z1), lisa.comoving_distance_mpc(z2)
    assert r2 / r1 == pytest.approx((m2 / dc2) / (m1 / dc1), rel=1e-6)
