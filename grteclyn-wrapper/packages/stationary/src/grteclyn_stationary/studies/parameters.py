"""One parameter ordering for potential, spin and canonical-matter searches."""
import numpy as np


def encode(config, *, free_spin, winding, radius):
    values = [config['m'], *config['q']]
    if free_spin:
        values.append(config['J'])
    if winding is not None:
        values.extend([np.log(config['matter_mass'] * radius),
                       np.log(config['amplitude'])])
    return np.asarray(values, dtype=float)


def decode(values, base, *, free_spin, winding, radius):
    values = np.asarray(values, dtype=float)
    size = 4 + int(free_spin) + 2 * (winding is not None)
    if values.shape != (size,) or not np.isfinite(values).all():
        raise ValueError('invalid study parameter vector')
    config = dict(base, m=float(values[0]), q=values[1:4].tolist())
    offset = 4
    if free_spin:
        config['J'] = float(values[offset])
        offset += 1
    if winding is not None:
        config.update(matter='cloud' if winding == 0 else 'winding',
                      winding_k=winding,
                      matter_mass=float(np.exp(values[offset]) / radius),
                      amplitude=float(np.exp(values[offset + 1])))
    return config


def bounds(args, config, *, winding):
    lo = [args.m_min, *([args.q_min] * 3)]
    hi = [args.m_max, *([args.q_max] * 3)]
    scales = [args.m_step, .3, .3, .3]
    if args.free_J:
        lo.append(args.J_min)
        hi.append(args.J_max)
        scales.append(args.J_step)
    if winding is not None:
        lo.extend([np.log(config['mass_range'][0]), np.log(1e-5)])
        hi.extend([np.log(config['mass_range'][1]), np.log(config['amplitude_max'])])
        scales.extend([.3, .3])
    return tuple(np.asarray(v, dtype=float) for v in (lo, hi, scales))
