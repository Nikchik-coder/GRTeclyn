#!/usr/bin/env python3
"""CPU-only checks of halo, light-speed and Penrose claims for the 3.72 ring.

Reads immutable accepted fields and completed validation records. No JAX,
new field solve, geodesic integration or decay experiment is performed.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from numpy.polynomial.chebyshev import chebval
from scipy.optimize import minimize_scalar

from grteclyn_stationary.numerics.spectral import cheb_coeffs
from grteclyn_stationary.railgun.gap import equatorial_densities


def audit():
    root = Path('results/railgun')
    study = root/'studies/ergoregion-max-validate271'
    source = study/'finalists/01/accepted.npz'
    with np.load(source, allow_pickle=False) as data:
        meta = json.loads(str(data['metadata']))
        u = np.array(data['u'])
    if not meta['validated']:
        raise ValueError('three-grid accepted field required')
    n = (meta['nx']+1)*(meta['ny']+1)
    arrays = u[:5*n].reshape(5, meta['nx']+1, meta['ny']+1)
    coeff = [cheb_coeffs(a[:, -1], 0) for a in arrays]
    profiles = json.loads((root/'reports/ergoregion-comparison/validated-comparison.json').read_text())
    case = next(c for c in profiles['cases'] if c['title'] == 'New accepted best')
    if hashlib.sha256(source.read_bytes()).hexdigest() != case['source_sha256']:
        raise ValueError('figure and accepted field hashes differ')

    def point(r):
        s = (r-meta['length'])/(r+meta['length'])
        f, w, _, b = [float(chebval(s, c)) for c in coeff[:4]]
        alpha = np.exp(f/2)
        H = (1+b)*np.exp(-f/2)*r  # sqrt(g_phiphi), not a coordinate radius
        shift = H*abs(w)
        gtt = shift*shift-alpha*alpha
        # (t, phi) block and Eulerian-frame photons of unit local energy.
        g = np.array([[gtt, -H*H*w], [-H*H*w, H*H]])
        normal = np.array([1/alpha, w/alpha])
        direction = np.array([0., np.sign(w)/H])
        photons = []
        for sign in (-1, 1):
            p = normal+sign*direction
            local_velocity = H*(p[1]/p[0]-w)/alpha
            residual = float(p@g@p)
            assert abs(residual) < 1e-11 and abs(abs(local_velocity)-1) < 1e-12
            photons.append(dict(local_direction='against dragging' if sign < 0 else 'with dragging',
                local_speed_c=float(abs(local_velocity)), null_norm=residual,
                E_infinity_per_E_local=float(-(g@p)[0]),
                angular_coordinate_rate_with_dragging=float(np.sign(w)*p[1]/p[0]),
                projected_grid_rate_per_asymptotic_t=float(H*np.sign(w)*p[1]/p[0])))
        energy = float(equatorial_densities(meta, u, np.array([r]))[0, 0])
        return dict(radius=r, lapse=float(alpha), shift_norm=float(shift),
            drag_ratio=float(shift/alpha), gtt=float(gtt),
            matter_energy_relative_to_peak=energy/case['density_peak']['value'],
            photons=photons, negative_energy_condition_v_parallel_less_than=float(-alpha/shift))

    radii = [.06, .08, .12, .23, .4, .45, .5, .55, .6, .7, .8, .85]
    samples = [point(r) for r in radii]
    halo = []
    for name, a, b in [('inner', case['ergoregion_edges'][0], case['half_peak_edges'][0]),
                       ('outer', case['half_peak_edges'][1], case['ergoregion_edges'][1])]:
        r = np.linspace(a, b, 2001)
        energy = equatorial_densities(meta, u, r)[0]/case['density_peak']['value']
        halo.append(dict(side=name, interval=[a, b], minimum_relative_density=float(energy.min()),
                         maximum_relative_density=float(energy.max()), cutoff=1e-6,
                         negligible_tails=bool(np.max(energy) < 1e-6)))
    at_ratio = point(case['drag_max']['radius'])
    at_gtt = point(case['gtt_max']['radius'])
    maximum_retrograde = minimize_scalar(lambda r: -point(r)['photons'][0][
        'projected_grid_rate_per_asymptotic_t'], bounds=case['ergoregion_edges'], method='bounded')
    completed = json.loads((study/'finalists/01/outcome.json').read_text())
    common = completed['additional_acceptance']['common_point_extrema']
    shift_spread = float(np.ptp([x['shift_norm_over_lapse_max'] for x in common]))
    rejected = json.loads((root/'studies/ergoregion-max-validate272/finalists/01/grid_160x20.json').read_text())
    # For a parent of rest mass m and specific Killing energy eps, decompose
    # xi=eps*u+zeta in its rest frame. zeta^2=eps^2+gtt. In a two-photon decay
    # p_+-=(m/2)(u+-e), giving E_out/E_in <= (1+sqrt(1+gtt/eps^2))/2.
    # eps>=1 for an unpowered massive parent arriving from infinity; eps=1
    # gives the largest such local bound. Escape can only reduce this bound.
    gain_bound = .5*(np.sqrt(1+case['gtt_max']['value'])-1)
    return dict(source=str(source), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        units='G=c=scalar mass=1; rho is coordinate radius; density is Eulerian matter energy density.',
        independent_equations_not_recomputed=True, gpu_started=False, new_tracks=0,
        claims={
            'ergoregion_extent': dict(status='SUPPORTED', equatorial_interval=case['ergoregion_edges'],
                half_peak_matter_edges=case['half_peak_edges'], density_peak=case['density_peak'],
                interpretation='Ergoregion extends beyond the half-peak contour, which is not a material surface.'),
            'near_empty_halo_or_hole': dict(status='REJECTED', intervals=halo,
                centre_energy_fraction=case['profile']['density'][0]/case['density_peak']['value']),
            'local_speeds_3p72_4p72_2p72_c': dict(status='REJECTED',
                interpretation='Shift/lapse and grid-coordinate rates are not locally measured velocities; both photons have local speed c.'),
            'boomerang_ray': dict(status='NOT_DEMONSTRATED',
                interpretation='All future causal directions corotate in coordinate angle inside the ergoregion. No integrated path or escaping ray is established; light never stops locally.'),
            'negative_killing_energy': dict(status='SUPPORTED_LOCALLY',
                equation='E_inf = alpha * E_local * (1 + drag_ratio * v_parallel)',
                interpretation='v_parallel is local velocity along the dragging direction in units of c. Negative Killing energy is not negative local energy and cannot arrive from infinity on one conserved-energy geodesic.'),
            'penrose_35_percent_gain': dict(status='UNSUPPORTED',
                local_single_decay_gain_bound=float(gain_bound),
                assumptions='Neutral unpowered two-body decay; incoming massive parent from infinity, E0/m0>=1. Photon limit gives an upper bound before escape tests.',
                interpretation='Need four-momentum conservation, allowed fragment masses, negative-energy confinement and positive-energy escape. Energy and speed gains are distinct; fuel/rest-mass conversion must be counted.'),
            'frequency_turning_point_confirmed_100_percent': dict(status='OVERSTATED',
                accepted_endpoint_frequencies=[profiles['cases'][0]['frequency'], float(u[-1])],
                interpretation='Rise from 0.6551 to 0.6741 supports a turn along the continued branch, but endpoints alone neither locate a minimum nor exclude a branch jump.'),
            'twelve_decimal_places_physical_accuracy': dict(status='OVERSTATED',
                sampled_ratio_spread=shift_spread,
                sampled_finest_ratio=common[-1]['shift_norm_over_lapse_max'],
                refined_equatorial_ratio=case['drag_max']['value'],
                interpretation='Close inter-grid agreement at common sample points is not a twelve-digit error bound on the continuum peak or every physical quantity.'),
            '5p21_roundoff_and_ceiling': dict(status='UNPROVEN',
                rejection_reasons=rejected['reasons'], newton=rejected['newton'],
                interpretation='Roundoff-scale Newton stalling is observed; a universal precision wall or maximum physical spin is not established by one failed correction.')},
        ratio_maximum_point=at_ratio, gtt_maximum_point=at_gtt,
        maximum_retrograde_projected_grid_rate=dict(radius=float(maximum_retrograde.x),
            value=float(-maximum_retrograde.fun), physical_local_speed=False),
        samples=samples,
        sources=dict(local_velocity='https://luth2.obspm.fr/~luthier/gourgoulhon/pdf/form3p1.pdf',
            horizonless_penrose='https://arxiv.org/abs/2608.08711',
            original_energy_bounds='https://doi.org/10.1086/152959'))


if __name__ == '__main__':
    result = audit()
    out = Path('results/railgun/reports/ergoregion-comparison/claims-audit.json')
    out.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(report=str(out), claims={k:v['status'] for k,v in result['claims'].items()}), indent=2))
