"""Map clock rates and frame dragging directly from a saved stationary ring.

NumPy/SciPy interpolation only: no JAX startup, solve or new particle track.
Clock rates refer to stationary observers relative to asymptotic Killing time.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from numpy.polynomial.chebyshev import chebval2d
from scipy.optimize import minimize

from grteclyn_wrapper.analysis.spinning_wormhole.spectral import cheb_coeffs


class SavedRing:
    def __init__(self, source):
        self.source = Path(source)
        with np.load(source, allow_pickle=False) as data:
            self.meta = json.loads(str(data['metadata']))
            self.u = data['u'].copy()
        if not self.meta.get('validated') or len(self.meta['fields']) != 1:
            raise ValueError('one accepted scalar field required')
        nx, ny = self.meta['nx'], self.meta['ny']
        n = (nx + 1) * (ny + 1)
        arrays = self.u[:5*n].reshape(5, nx+1, ny+1)
        self.coeff = [cheb_coeffs(cheb_coeffs(a, 0), 1) for a in arrays]

    def metric(self, rho, z):
        rho, z = np.broadcast_arrays(np.abs(np.asarray(rho)), np.asarray(z))
        radius = np.hypot(rho, z)
        s = (radius-self.meta['length'])/(radius+self.meta['length'])
        mu = np.divide(z, radius, out=np.zeros_like(radius), where=radius > 0)
        y = 2*mu*mu-1
        f, w, _, b = [chebval2d(s, y, c) for c in self.coeff[:4]]
        lapse = np.exp(f/2)
        drag = (1+b)*np.exp(-f)*np.abs(w)*rho
        gtt = -lapse*lapse*(1-drag*drag)
        return dict(lapse=lapse, fixed_clock=np.sqrt(np.maximum(0., -gtt)),
                    angular_drag=np.abs(w), drag_ratio=drag, gtt=gtt)

    def extremum(self, key, maximum=False):
        sign = -1 if maximum else 1
        # Cover the compactified radial domain first, then refine the best
        # candidates in cylindrical coordinates, including the origin/axis.
        radial = np.r_[0., np.geomspace(1e-4, 1e4, 241)]
        theta = np.linspace(0., np.pi/2, 81)
        r, t = np.meshgrid(radial, theta)
        rho, z = r*np.sin(t), r*np.cos(t)
        value = sign*self.metric(rho, z)[key]
        seeds = [np.unravel_index(i, value.shape) for i in np.argsort(value.ravel())[:8]]
        candidates = []
        for index in seeds:
            fit = minimize(lambda x: float(sign*self.metric(*x)[key]),
                           [rho[index], z[index]], method='Nelder-Mead',
                           bounds=[(0., 1e4), (0., 1e4)],
                           options={'xatol': 1e-9, 'fatol': 1e-13, 'maxiter': 600})
            candidates.append(fit)
        best = min(candidates, key=lambda a: a.fun)
        if not best.success:
            raise ValueError(f'location refinement failed: {key}')
        return dict(rho=float(best.x[0]), z=float(best.x[1]),
                    value=float(self.metric(*best.x)[key]))


def create(source, output, reports):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patches import ConnectionPatch, FancyArrowPatch, Circle
    from grteclyn_wrapper.optimisation.railgun.gap import equatorial_densities

    output, reports = Path(output), Path(reports)
    output.parent.mkdir(parents=True, exist_ok=True)
    reports.parent.mkdir(parents=True, exist_ok=True)
    ring = SavedRing(source)
    archive = json.loads(Path(source).with_name('grid_160x20.json').read_text())
    extrema = {key: ring.extremum(key, maximum=key in ('angular_drag', 'drag_ratio', 'gtt'))
               for key in ('lapse', 'fixed_clock', 'angular_drag', 'drag_ratio', 'gtt')}
    centre = {k: float(v) for k, v in ring.metric(0., 0.).items()}
    if abs(extrema['lapse']['value']-archive['lapse_min']) > 2e-5:
        raise ValueError('clock map disagrees with the accepted solution')
    if extrema['gtt']['value'] >= 0:
        raise ValueError('the no-ergoregion diagram does not apply to this state')
    samples = np.linspace(1e-5, 5., 2001)
    energy = equatorial_densities(ring.meta, ring.u, samples)[0]
    peak_radius = float(samples[np.argmax(energy)])
    x = np.linspace(-3.1, 3.1, 701)
    xx, yy = np.meshgrid(x, x)
    relative = np.interp(np.hypot(xx, yy), samples, energy/energy.max())
    ink, purple, red, teal, blue = '#253445', '#7549a2', '#be4b3b', '#008579', '#3179a5'
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'text.color': ink, 'axes.labelcolor': ink})
    fig = plt.figure(figsize=(16, 10), facecolor='#fcfcfa')
    ax = fig.add_axes([.235, .17, .53, .66])
    cmap = LinearSegmentedColormap.from_list('matter', ['#fcfcfa', '#fbefd4', '#efc878', '#c5752d', '#8c441c'])
    ax.imshow(relative, extent=[x[0], x[-1], x[0], x[-1]], origin='lower', cmap=cmap,
              vmin=0., vmax=1., interpolation='bilinear')
    ax.contour(xx, yy, relative, levels=[.5], colors=['#bc7b38'], linewidths=.8, alpha=.8)
    ax.set(xlim=(-3.1, 3.1), ylim=(-3.1, 3.1), aspect='equal')
    ax.axis('off')
    # Clockwise arrows follow the sign of the saved angular shift. They
    # indicate frame dragging, not a measured orbit or material velocity.
    for radius, angle in [(1.9, 60), (1.9, 240), (.52, 315)]:
        t = np.deg2rad(np.linspace(angle, angle-58, 60))
        ax.plot(radius*np.cos(t), radius*np.sin(t), color=purple, lw=1.8, alpha=.8)
        ax.add_patch(FancyArrowPatch((radius*np.cos(t[-3]), radius*np.sin(t[-3])),
                                    (radius*np.cos(t[-1]), radius*np.sin(t[-1])),
                                    arrowstyle='-|>', mutation_scale=16, color=purple))
    ax.add_patch(Circle((0, 0), .07, facecolor='white', edgecolor=purple, linewidth=1.7, zorder=8))
    ax.plot([-.5, .5], [-2.97, -2.97], color=ink, lw=1.4)
    ax.text(0, -3.08, '1 coordinate unit', ha='center', va='top', fontsize=9, color='#697585')

    fig.text(.045, .945, 'Where spacetime changes around the ring', fontsize=25, weight='bold')
    mass, angular = archive['M_ADM_estimate'], archive['J_volume']
    fig.text(.045, .904, f'One rotating scalar ring, ω = 0.70     •     k = +1     •     |J|/M² = {abs(angular)/mass**2:.3f}',
             fontsize=13, color='#586879')
    fig.text(.045, .865, 'TOP VIEW through the equatorial plane  •  Rotation axis points out of the page',
             fontsize=11, color='#586879')

    def callout(title, lines, anchor, corner, color, *, align='left', attach=None):
        # All text stays outside the matter diagram. Each leader names one
        # measured point; leaders never run through another text block.
        fx, fy = corner
        fig.text(fx, fy, title, color=color, fontsize=13, weight='bold', ha=align, va='top')
        fig.text(fx, fy-.032, '\n'.join(lines), fontsize=11.5, color=ink,
                 ha=align, va='top', linespacing=1.45)
        if anchor is not None:
            ax.plot(*anchor, 'o', ms=6, color=color, mec='white', mew=1.2, zorder=10)
            end = attach if attach is not None else (fx, fy-.035)
            line = ConnectionPatch(xyA=anchor, coordsA=ax.transData, xyB=end,
                                   coordsB=fig.transFigure, color=color, lw=1.2,
                                   connectionstyle='angle3,angleA=0,angleB=90', zorder=5)
            fig.add_artist(line)

    def at(radius, degrees):
        a = np.deg2rad(degrees)
        return radius*np.cos(a), radius*np.sin(a)

    slow_r = extrema['fixed_clock']['rho']
    drag_r = extrema['drag_ratio']['rho']
    slow, drag, outside = ring.metric(slow_r, 0.), ring.metric(drag_r, 0.), ring.metric(3., 0.)
    callout('CENTRE OF THE HOLE',
            [f'Clock: {60*centre["fixed_clock"]:.1f} min per distant hour',
             f'Angular dragging: {centre["angular_drag"]:.4f} — MAXIMUM',
             'Drag ratio: 0 exactly on the axis'],
            (0., 0.), (.045, .815), purple, attach=(.265, .72))
    callout('INSIDE THE RING WALL',
            [f'ρ = {slow_r:.2f}  •  slowest fixed clock',
             f'Clock: {60*float(slow["fixed_clock"]):.1f} min per distant hour',
             f'Angular dragging: {float(slow["angular_drag"]):.4f}',
             f'Drag ratio: {float(slow["drag_ratio"]):.3f}'],
            at(slow_r, 48), (.765, .815), red, attach=(.765, .70))
    callout('NEAR THE DENSE WALL',
            [f'ρ = {drag_r:.2f}  •  maximum drag ratio',
             f'Drag ratio: {float(drag["drag_ratio"]):.3f} — MAXIMUM',
             f'Clock: {60*float(drag["fixed_clock"]):.1f} min per distant hour',
             f'Angular dragging: {float(drag["angular_drag"]):.4f}'],
            at(drag_r, 223), (.045, .43), teal, attach=(.265, .35))
    callout('OUTSIDE THE DENSE RING',
            ['ρ = 3.00', f'Clock: {60*float(outside["fixed_clock"]):.1f} min per distant hour',
             f'Angular dragging: {float(outside["angular_drag"]):.4f}',
             f'Drag ratio: {float(outside["drag_ratio"]):.3f}'],
            at(3., -22), (.765, .43), blue, attach=(.765, .30))
    fig.text(.5, .214, f'Orange = matter concentration  •  density peaks at ρ ≈ {peak_radius:.2f}',
             ha='center', fontsize=11, color='#9a5b22', bbox=dict(facecolor='#fcfcfa', edgecolor='none', pad=3))
    fig.text(.045, .14, 'NO ERGOREGION IN THIS STATE', fontsize=13, weight='bold', color=teal)
    fig.text(.045, .108, 'An ergoregion starts where the drag ratio reaches 1. This ring reaches only 0.510.', fontsize=11.5)
    fig.text(.765, .14, 'FAR AWAY', fontsize=13, weight='bold', color=ink)
    fig.text(.765, .108, 'Clock → 60 min/hour; dragging → 0', fontsize=11.5)
    fig.text(.045, .061, 'Clocks are held at fixed spatial positions. Angular dragging Ω is per simulation time; '
             'drag ratio = |shift|/lapse, not matter speed.', fontsize=10, color='#586879')
    fig.text(.045, .033, 'A particle can be aimed along the rotation axis through the central hole. '
             'Purple arrows show frame dragging, not particle trajectories. Matter has diffuse tails.', fontsize=10, color='#586879')
    fig.savefig(output, dpi=220, facecolor=fig.get_facecolor())
    fig.savefig(output.with_suffix('.svg'), facecolor=fig.get_facecolor())
    plt.close(fig)
    report = dict(source=str(source), source_sha256=hashlib.sha256(Path(source).read_bytes()).hexdigest(),
                  centre=centre, extrema=extrema, mass=mass, angular_momentum=angular,
                  dimensionless_spin_abs=abs(angular)/mass**2, density_peak_radius=peak_radius,
                  outside_rho3={k:float(v) for k,v in outside.items()},
                  clocks='Held fixed: sqrt(-g_tt). Locally nonrotating: lapse exp(f/2). Both relative to asymptotic Killing time.',
                  map='One equatorial spatial view. Leader lines attach each measurement to its own position.',
                  search='Compactified radial scan and multistart location refinement. Coordinate, not proper, radii.',
                  no_ergoregion=extrema['gtt']['value'] < 0)
    reports.with_suffix('.json').write_text(json.dumps(report, indent=2)+'\n')
    r = np.linspace(0., 7., 1001)
    equator, axis = ring.metric(r, 0.), ring.metric(0., r)
    np.savetxt(reports.with_suffix('.tsv'), np.column_stack([r, *equator.values(), *axis.values()]),
               header='radius\t'+'\t'.join([f'equator_{k}' for k in equator]+[f'axis_{k}' for k in axis]), delimiter='\t')
    print(json.dumps(report, indent=2))
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, default=Path('results/railgun/studies/frequency-deep/frequency_01/accepted.npz'))
    ap.add_argument('--out', type=Path, default=Path('results/railgun/figures/ring070-physics.png'))
    ap.add_argument('--report', type=Path, default=Path('results/railgun/reports/ring070-physics'))
    args = ap.parse_args()
    create(args.source, args.out, args.report)


if __name__ == '__main__':
    main()
