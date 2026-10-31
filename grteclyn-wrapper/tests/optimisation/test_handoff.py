"""Synthetic fields independently check table order, normalisation and scaling."""
import dataclasses
import json
import math

import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole.spectral import ArctanMap, lobatto
from grteclyn_wrapper.analysis.spinning_wormhole.backgrounds import read_spinbg
from grteclyn_wrapper.optimisation.handoff import matter_background, write_matter_spinbg, MATTER_COMPONENTS


def test_handoff_normalisation_and_similarity(tmp_path):
    sx, _ = lobatto(4)
    sy, _ = lobatto(2)
    shape = (5, 3)
    fields = {k: np.full(shape, v) for k,v in dict(F=.2, W=.6, N=.1, B=1.1, PSI=-2.).items()}
    meta = dict(radial_map=dataclasses.asdict(ArctanMap(eta0=1.)), sigma=2., psim=-2.,
                potential_coeffs=[1., 2., 3.], R_e=4., J=3., X=2., E19=0., E_c=0., m=.3)
    seed = tmp_path/'seed.npz'
    np.savez(seed, sx=sx, sy=sy, meta=json.dumps(meta), **fields)
    x, mu, comps, coeffs, info = matter_background(seed, 9, 5, 3.)
    assert tuple(comps) == MATTER_COMPONENTS
    np.testing.assert_allclose(comps['phi'], -2/math.sqrt(4*math.pi))
    np.testing.assert_allclose(comps['omega'], .1)
    np.testing.assert_allclose(comps['domega_deta'], 0., atol=1e-14)
    np.testing.assert_allclose(coeffs, [1/(72*math.pi), 2*math.sqrt(4*math.pi)/(72*math.pi), 1/6])
    assert info['table_eta0'] == 6. and info['table_R_e'] == 12. and info['table_J'] == 27.
    path = tmp_path/'background.spinbg'
    write_matter_spinbg(path, info['table_eta0'], x, mu, comps, potential_coeffs=coeffs)
    header, body = read_spinbg(path)
    assert body.shape == (5, 9, 7)
    for i, name in enumerate(MATTER_COMPONENTS):
        np.testing.assert_allclose(body[:,:,i], comps[name])
