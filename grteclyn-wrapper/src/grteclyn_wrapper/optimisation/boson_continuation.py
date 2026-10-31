"""Similarity and orientation changes for coupled matter continuation seeds."""
import numpy as np
from .exploration import physical_throat


def prepare_seed(state, config, area, winding):
    """Preserve the solution under scaling and optional azimuthal reflection.

    These exact transformations only prepare a guess. The new minimal-area
    constraint and every subsequent parameter step still require a solve.
    """
    state, config = dict(state), dict(config)
    kind = config.get('matter')
    if kind not in ('cloud', 'winding'):
        raise ValueError('a nonzero canonical-field seed is required')
    old_k = config.get('winding_k', 1) if kind == 'winding' else 0
    if abs(old_k) != abs(winding):
        raise ValueError('azimuthal reflection cannot change winding magnitude')
    if winding != old_k:
        state['W'] = -state['W']
        state['omega'] = -state['omega']
        config['J'] = -config['J']
    config['winding_k'] = winding
    factor = float(np.sqrt(area / physical_throat(state)['area_throat']))
    if not np.isfinite(factor) or factor <= 0:
        raise ValueError('invalid target area')
    state['sigma'] *= factor
    state['frequency'] /= factor
    for key in ('m', 'matter_mass'):
        config[key] /= factor
    if 'quartic' in config:
        config['quartic'] /= factor**2
    config['J'] *= factor**2
    return state, config, factor
