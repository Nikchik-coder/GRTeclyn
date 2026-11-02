"""Stationary scalar-ring data to the Cartesian RadialRecipe CCZ4 state.

The two real evolution fields are chi_complex/sqrt(4*pi). GRTeclyn defines
Pi=+n^a partial_a phi. Its imaginary component occupies phi_lump0/Pi_lump0.
Importing only the amplitude, setting K_ij=0, or reversing Pi changes the
initial spacetime. No constraint solve or perturbation is applied here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

import numpy as np

COMPONENTS = [
    'chi', 'h11', 'h12', 'h13', 'h22', 'h23', 'h33', 'K',
    'A11', 'A12', 'A13', 'A22', 'A23', 'A33', 'Theta',
    'Gamma1', 'Gamma2', 'Gamma3', 'lapse', 'shift1', 'shift2', 'shift3',
    'B1', 'B2', 'B3', 'phi', 'Pi', 'phi_lump0', 'Pi_lump0',
]
SYMMETRIC = ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def grid_layout(path):
    """Read and bound the binary layout without loading a three-dimensional cube."""
    with Path(path).open('rb') as stream:
        if stream.readline() != b'GRTECLYN_GRID_INIT_V2\n':
            raise ValueError('named-component Gridinit V2 required')
        values = {}
        while stream.tell() < 65536:
            raw = stream.readline()
            if raw == b'END_HEADER\n':
                break
            tokens = raw.decode('ascii').split()
            if not tokens or tokens[0] in values:
                raise ValueError('invalid or duplicated grid header')
            values[tokens[0]] = tokens[1:]
        else:
            raise ValueError('grid header is too long')
        offset = stream.tell()
    try:
        shape = [int(v) for v in values['nx_ny_nz']]
        count = int(values['num_components'][0])
        spacing = [float(v) for v in values['dx']]
        origin = [float(v) for v in values['origin']]
        names = values['component_names']
    except (KeyError, IndexError, ValueError) as error:
        raise ValueError('incomplete grid header') from error
    if (len(shape) != 3 or min(shape) < 2 or len(spacing) != 3 or min(spacing) <= 0
            or len(origin) != 3 or not np.isfinite(spacing + origin).all()
            or count != len(names) or count < 1 or len(set(names)) != count
            or Path(path).stat().st_size != offset + int(np.prod(shape))*count*8):
        raise ValueError('invalid grid layout or payload size')
    return dict(shape=shape, spacing=spacing, origin=origin, components=names)


def source_contract(source):
    """Read-only archive validation, without importing JAX or starting CUDA."""
    source = Path(source).resolve()
    root = source.parent
    while not (root / 'sha256sums.txt').is_file():
        if root == root.parent:
            raise ValueError('an archived, checksummed source study is required')
        root = root.parent
    listed = set()
    for line in (root / 'sha256sums.txt').read_text().splitlines():
        expected, name = line.split('  ', 1)
        path = (root / name).resolve()
        if not path.is_relative_to(root) or digest(path) != expected:
            raise ValueError('source archive checksum mismatch')
        listed.add(path)
    if source not in listed or source.parent / 'outcome.json' not in listed:
        raise ValueError('source and acceptance outcome must both be checksummed')
    result = json.loads((source.parent / 'outcome.json').read_text())
    with np.load(source, allow_pickle=False) as data:
        metadata = json.loads(str(data['metadata']))
    fields = metadata.get('fields', [])
    if (not result.get('accepted') or not metadata.get('validated')
            or metadata.get('model') != 'canonical_regular_centre'
            or len(fields) != 1 or abs(fields[0]['winding']) != 1
            or fields[0]['parity'] != 'even'
            or fields[0]['quartic'] != 0 or fields[0]['sextic'] != 0
            or len(result.get('records', [])) != 3
            or any(r.get('verdict') != 'PASS' for r in result['records'])):
        raise ValueError('accepted three-grid, single free massive |k|=1 ring required')
    return dict(source_sha256=digest(source), mass=fields[0]['mass'],
                winding=fields[0]['winding'], source_grid=[metadata['nx'], metadata['ny']],
                source_stability=metadata.get('stability', 'not_assessed'))


def state_evaluator(metric, scalar, jax):
    """Build the ADM/CCZ4 conversion from independent four-metric derivatives.

    Derivatives have their coordinate index last. K_ij follows
    (-partial_t gamma_ij + D_i beta_j + D_j beta_i)/(2 alpha).
    Gamma^i is computed from h_ij, not set to zero for a rotating ring.
    """
    xp = jax.numpy
    dmetric, dscalar = jax.jacfwd(metric), jax.jacfwd(scalar)

    def evaluate(x):
        g, dg = metric(x), dmetric(x)
        spatial, dgamma = g[1:, 1:], dg[1:, 1:, 1:]
        inverse = xp.linalg.inv(spatial)
        beta = inverse @ g[0, 1:]
        alpha = xp.sqrt(-g[0, 0] + g[0, 1:] @ beta)
        chi = xp.linalg.det(spatial)**(-1 / 3)
        h = chi * spatial
        dchi = -chi / 3 * xp.einsum('ij,ijk->k', inverse, dgamma)
        dh = chi * dgamma + xp.einsum('ij,k->ijk', spatial, dchi)
        # Gamma_{l i j} = (gamma_{l j,i}+gamma_{l i,j}-gamma_{i j,l})/2.
        lower_connection = .5 * (dgamma.transpose(0, 2, 1) + dgamma
                                 - dgamma.transpose(2, 0, 1))
        connection = xp.einsum('kl,lij->kij', inverse, lower_connection)
        cov_derivative = dg[0, 1:, 1:] - xp.einsum('kij,k->ij', connection, g[0, 1:])
        kij = (cov_derivative + cov_derivative.T - dg[1:, 1:, 0]) / (2 * alpha)
        trace = xp.einsum('ij,ij->', inverse, kij)
        aij = chi * (kij - spatial * trace / 3)
        lower_h = .5 * (dh.transpose(0, 2, 1) + dh - dh.transpose(2, 0, 1))
        hinverse = inverse / chi
        gamma = xp.einsum('il,jk,ljk->i', hinverse, hinverse, lower_h)
        phi = scalar(x) / xp.sqrt(4 * xp.pi)
        derivative = dscalar(x) / xp.sqrt(4 * xp.pi)
        pi = (derivative[:, 0] - derivative[:, 1:] @ beta) / alpha
        state = xp.concatenate((xp.array([chi]), xp.stack([h[i, j] for i, j in SYMMETRIC]),
            xp.array([trace]), xp.stack([aij[i, j] for i, j in SYMMETRIC]),
            xp.zeros(1), gamma, xp.array([alpha]), beta, xp.zeros(3),
            xp.array([phi[0], pi[0], phi[1], pi[1]])))
        # Charge and matter angular momentum: independent checks of Pi's sign
        # and the normalization. The third value is the proper volume element.
        volume = xp.sqrt(xp.linalg.det(spatial))
        current = -pi @ derivative[:, 1:]
        charge = (phi[0] * pi[1] - phi[1] * pi[0]) * volume
        angular = (-x[2] * current[0] + x[1] * current[1]) * volume
        return state, xp.array([charge, angular, volume])
    return jax.jit(jax.vmap(evaluate))


def grid_points(n, length, ghosts, start, stop):
    """Cell centres in the file's z,y,x order, translated to the ring centre."""
    width = n + 2 * ghosts
    index = np.arange(start, stop)
    k, j, i = index // (width * width), (index // width) % width, index % width
    coords = np.stack((i, j, k), axis=1)
    spatial = (coords - ghosts + .5) * (length / n) - length / 2
    return np.column_stack((np.zeros(len(index)), spatial)), coords


def algebraic_checks(state):
    state = np.asarray(state)
    h = np.zeros((len(state), 3, 3)); a = np.zeros_like(h)
    for c, (i, j) in enumerate(SYMMETRIC):
        h[:, i, j] = h[:, j, i] = state[:, 1 + c]
        a[:, i, j] = a[:, j, i] = state[:, 8 + c]
    determinant_error = float(np.max(abs(np.linalg.det(h) - 1)))
    trace_error = float(np.max(abs(np.einsum('nij,nij->n', np.linalg.inv(h), a))))
    positive = bool(np.all(np.linalg.eigvalsh(h) > 0)
                    and np.all(state[:, 0] > 0) and np.all(state[:, 18] > 0))
    return dict(accepted=bool(np.isfinite(state).all() and positive
                             and max(determinant_error, trace_error) < 1e-10),
                determinant_error=determinant_error, trace_A_error=trace_error,
                positive_spatial_metric_and_lapse=positive)


def export_grid(source, directory, *, n=96, length=32., ghosts=4, batch=256,
                core_radius=.4, core_degree=6):
    plan = source_contract(source)
    if n < 16 or n % 2 or not np.isfinite(length) or length <= 0 or ghosts < 4 or batch < 1:
        raise ValueError('even N>=16, positive box length, >=4 ghost cells and positive batch required')
    from .workflow import load_state, write_json
    from .geometry import RingGeometry
    from .corridor import CartesianCorridor
    problem, u, _ = load_state(source)
    jax = problem.jax
    if jax.devices()[0].platform != 'gpu':
        raise ValueError('production Cartesian export and core certification require GPU')
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    geometry = CartesianCorridor(RingGeometry(problem, u), radius=core_radius, degree=core_degree)
    certificate = geometry.certify(tolerance=1e-8)
    write_json(directory / 'corridor.json', certificate)
    if not certificate['accepted']:
        write_json(directory / 'outcome.json', dict(accepted=False, reason='core_certification'))
        raise ValueError('Cartesian core rejected; no grid exported')
    evaluate = state_evaluator(geometry.metric, lambda x: geometry.scalar(x, 0), jax)
    width = n + 2 * ghosts
    header = ('GRTECLYN_GRID_INIT_V2\n'
              f'num_components {len(COMPONENTS)}\ncomponent_names {" ".join(COMPONENTS)}\n'
              f'nx_ny_nz {width} {width} {width}\n'
              f'dx {length/n:.17e} {length/n:.17e} {length/n:.17e}\n'
              f'origin {-ghosts*length/n:.17e} {-ghosts*length/n:.17e} {-ghosts*length/n:.17e}\n'
              'END_HEADER\n').encode('ascii')
    path = directory / 'initial.gridinit'
    partial = directory / 'initial.gridinit.partial'
    sums = np.zeros(2); maxima = dict(determinant_error=0., trace_A_error=0.)
    minimum_lapse = np.inf
    manifest = dict(**plan, n=n, length=length, ghosts=ghosts, batch=batch,
        frequency=float(geometry.frequencies[0]), components=COMPONENTS,
        commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        platform='gpu', float64=bool(jax.config.jax_enable_x64),
        normalization='Phi=chi_complex/sqrt(4*pi); Pi=+n^a partial_a Phi',
        coordinates='File and evolution box [0,L]^3; ring centre (L/2,L/2,L/2).',
        matter_model='grtresna_complex_scalar', perturbation='none', stability='not_assessed')
    write_json(directory / 'manifest.json', manifest)
    with partial.open('xb') as stream:
        stream.write(header)
        for start in range(0, width**3, batch):
            stop = min(start + batch, width**3)
            points, indices = grid_points(n, length, ghosts, start, stop)
            padded = np.pad(points, ((0, batch-len(points)), (0, 0)), mode='edge')
            states, densities = map(np.asarray, evaluate(jax.numpy.asarray(padded)))
            states, densities = states[:stop-start], densities[:stop-start]
            check = algebraic_checks(states)
            if not check['accepted']:
                raise ValueError(f'nonphysical CCZ4 export at cell offset {start}')
            for key in maxima:
                maxima[key] = max(maxima[key], check[key])
            inside = np.all((indices >= ghosts) & (indices < ghosts+n), axis=1)
            sums += densities[inside, :2].sum(axis=0) * (length/n)**3
            minimum_lapse = min(minimum_lapse, float(states[inside, 18].min())) if inside.any() else minimum_lapse
            stream.write(np.asarray(states, dtype='<f8').tobytes())
            if start == 0 or stop == width**3 or start // batch % 512 == 0:
                write_json(directory / 'progress.json', dict(cells=stop, total=width**3,
                    seconds=time.monotonic()-started))
                print(f'[ring-export] {stop}/{width**3} cells', flush=True)
    relative_balance = abs(sums[1] + plan['winding']*sums[0]) / max(abs(sums[0]), 1e-30)
    if sums[0] <= 0 or relative_balance > 1e-10:
        raise ValueError('exported charge/angular momentum violates J=-k Q')
    partial.rename(path)
    result = dict(accepted=True, export_only=True, **maxima,
        finite_box_charge=float(sums[0]), finite_box_matter_J=float(sums[1]),
        charge_angular_relative_error=float(relative_balance), minimum_lapse=minimum_lapse,
        gridinit_sha256=digest(path), bytes=path.stat().st_size, cells=width**3,
        seconds=time.monotonic()-started, stability='not_assessed',
        scope='Validated conversion and core; Cartesian finite-difference constraints and evolution remain to be tested.')
    write_json(directory / 'outcome.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--n', type=int, default=96)
    parser.add_argument('--length', type=float, default=32.)
    parser.add_argument('--batch', type=int, default=256)
    parser.add_argument('--gpu', type=int, required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps(source_contract(args.source), indent=2)); return
    if args.gpu < 0:
        parser.error('nonnegative GPU card required')
    from ..solver.device import select_device
    select_device(args.gpu)
    print(json.dumps(export_grid(args.source, args.out, n=args.n, length=args.length, batch=args.batch), indent=2))


if __name__ == '__main__':
    main()
