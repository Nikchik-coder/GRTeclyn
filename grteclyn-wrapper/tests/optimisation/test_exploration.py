"""Saved grid-unit fields, not radius metadata, define physical comparisons."""
import numpy as np
import pytest
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import ArctanMap, lobatto
from grteclyn_wrapper.optimisation.exploration import physical_throat, interpolate


def test_physical_ellis_throat_uses_sigma():
    sx, _ = lobatto(12)
    sy, _ = lobatto(6)
    zeros = np.zeros((13, 7))
    state = dict(sx=sx, sy=sy, F=zeros, N=zeros, B=zeros+1., sigma=3., map=ArctanMap(eta0=1.))
    th = physical_throat(state)
    assert th["R_e"] == pytest.approx(3.)
    assert th["R_A"] == pytest.approx(3.)
    assert th["area_throat"] == pytest.approx(36*np.pi)
    state["cloud"] = (1-sx[:, None]**2)*(1+.2*sy[None, :])
    tx, ty = lobatto(16)[0], lobatto(8)[0]
    np.testing.assert_allclose(interpolate(state, tx, ty, "cloud"),
                               (1-tx[:, None]**2)*(1+.2*ty[None, :]), atol=1e-13)
