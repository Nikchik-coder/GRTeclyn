"""Plot an accepted single-field ring from its portable array archive.

Only values are interpolated here; curvature and field-equation checks come
from the numerical validation, not from this plotting grid. No JAX is started.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole.spectral import cheb_eval, lobatto


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('solution', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--extent', type=float, default=15.)
    parser.add_argument('--3d', dest='three_dimensional', action='store_true',
                        help='revolve the computed half-maximum scalar contour')
    args = parser.parse_args(argv)
    with np.load(args.solution, allow_pickle=False) as data:
        metadata = json.loads(str(data['metadata']))
        u = np.asarray(data['u'])
    if (metadata.get('model') != 'canonical_regular_centre'
            or not metadata.get('validated') or len(metadata['fields']) != 1
            or not metadata['fields'][0]['winding']):
        parser.error('an accepted single-field ring archive is required')
    if not np.isfinite(args.extent) or args.extent <= 0:
        parser.error('extent must be finite and positive')
    nx, ny, length = metadata['nx'], metadata['ny'], metadata['length']
    n = (nx+1)*(ny+1)
    arrays = u[:5*n].reshape(5, nx+1, ny+1)
    field = metadata['fields'][0]
    s, _ = lobatto(nx)
    y, _ = lobatto(ny)
    rho, z = np.meshgrid(np.linspace(0., args.extent, 181),
                         np.linspace(-args.extent, args.extent, 361))
    radius = np.hypot(rho, z)
    mu = np.divide(z, radius, out=np.zeros_like(z), where=radius > 0)
    bx = cheb_eval(s, np.eye(nx+1), ((radius-length)/(radius+length)).ravel())
    by = cheb_eval(y, np.eye(ny+1), (2*mu*mu-1).ravel())

    def sample(index):
        return np.sum((bx@arrays[index])*by, axis=1).reshape(radius.shape)

    amplitude = sample(4)*np.maximum(0., 1-mu*mu)**(abs(field['winding'])/2)
    if field['parity'] == 'odd':
        amplitude *= mu
    if abs(field['winding']) or field['parity'] == 'odd':
        amplitude[radius == 0] = 0.
    mass = field['mass']
    if args.three_dimensional:
        temporary, contour_ax = plt.subplots()
        contours = contour_ax.contour(rho, z, amplitude**2,
                                       levels=[.5*np.max(amplitude**2)]).allsegs[0]
        plt.close(temporary)
        phi = np.linspace(0., 2*np.pi, 129)
        fig = plt.figure(figsize=(8., 7.))
        fig.subplots_adjust(left=.02, right=.93, bottom=.16, top=.92)
        ax = fig.add_subplot(projection='3d')
        for contour in contours:
            rr, zz = contour[:, 0]*mass, contour[:, 1]*mass
            x = rr[:, None]*np.cos(phi)
            y3 = rr[:, None]*np.sin(phi)
            z3 = np.broadcast_to(zz[:, None], x.shape)
            ax.plot_surface(x, y3, z3, color='#34898f', linewidth=0.,
                            rstride=max(1, len(rr)//180), cstride=2,
                            antialiased=True, shade=True)
        limit = args.extent*mass
        ax.set(xlabel=r'$mx$', ylabel=r'$my$', zlabel=r'$mz$',
               xlim=(-limit, limit), ylim=(-limit, limit),
               zlim=(-.6*limit, .6*limit), box_aspect=(1., 1., .6))
        ax.view_init(elev=45., azim=-55.)
        ax.set_title(f'Computed scalar ring · k={field["winding"]}', pad=15.)
        fig.text(.5, .025, 'Surface at 50% of peak scalar amplitude squared; the field has diffuse tails.',
                 ha='center', fontsize=10)
    else:
        fig, axes = plt.subplots(1, 2, figsize=(9., 4.5), layout='constrained')
        for ax, values, title, cmap in zip(axes,
                (amplitude**2, sample(1)/mass),
                (r'Scalar amplitude $|\chi|^2$', r'Frame dragging $w/m$'),
                ('viridis', 'magma')):
            plot = ax.pcolormesh(mass*rho, mass*z, values, shading='auto', cmap=cmap,
                                 rasterized=True)
            ax.set(xlabel=r'$m\rho$', ylabel=r'$mz$', title=title, aspect='equal')
            fig.colorbar(plot, ax=ax, shrink=.9, pad=.025)
        fig.suptitle(f'Stationary k={field["winding"]} scalar ring · {nx}×{ny}')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=170)
    plt.close(fig)


if __name__ == '__main__':
    main()
