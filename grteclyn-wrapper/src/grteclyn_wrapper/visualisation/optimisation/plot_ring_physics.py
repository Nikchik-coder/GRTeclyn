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
            self.u = data['physical_u' if 'physical_u' in data else 'u'].copy()
        if not self.meta.get('validated'):
            raise ValueError('an accepted scalar-field solution is required')
        nx, ny = self.meta['nx'], self.meta['ny']
        n = (nx + 1) * (ny + 1)
        count = 4+len(self.meta['fields'])
        arrays = self.u[:count*n].reshape(count, nx+1, ny+1)
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
    support = np.flatnonzero(energy >= .5*energy.max())
    def edge(a, b):
        return float(samples[a]+(samples[b]-samples[a])*(.5*energy.max()-energy[a])/(energy[b]-energy[a]))
    inner_edge = edge(support[0]-1, support[0])
    outer_edge = edge(support[-1], support[-1]+1)
    x = np.linspace(-3.1, 3.1, 701)
    xx, yy = np.meshgrid(x, x)
    relative = np.interp(np.hypot(xx, yy), samples, energy/energy.max())
    ink, purple, red, teal, blue = '#253445', '#7549a2', '#be4b3b', '#008579', '#3179a5'
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'text.color': ink, 'axes.labelcolor': ink})
    fig = plt.figure(figsize=(16, 10), facecolor='#fcfcfa')
    ax = fig.add_axes([.235, .17, .53, .66])
    cmap = LinearSegmentedColormap.from_list('matter', ['#fcfcfa', '#e9f2ff', '#b6d2fa', '#5191d5', '#1c5798'])
    ax.imshow(relative, extent=[x[0], x[-1], x[0], x[-1]], origin='lower', cmap=cmap,
              vmin=0., vmax=1., interpolation='bilinear')
    for radius in (inner_edge, outer_edge):
        ax.add_patch(Circle((0, 0), radius, fill=False, edgecolor='white', linewidth=4., zorder=3))
        ax.add_patch(Circle((0, 0), radius, fill=False, edgecolor='#153d70', linewidth=2.3, zorder=4))
    ax.set(xlim=(-3.1, 3.1), ylim=(-3.1, 3.1), aspect='equal')
    ax.axis('off')
    # Clockwise arrows follow the sign of the saved angular shift. They
    # indicate frame dragging, not a measured orbit or material velocity.
    for radius, angle in [(2.12, 60), (2.12, 240), (.30, 315)]:
        t = np.deg2rad(np.linspace(angle, angle-58, 60))
        ax.plot(radius*np.cos(t), radius*np.sin(t), color=purple, lw=1.8, alpha=.8)
        ax.add_patch(FancyArrowPatch((radius*np.cos(t[-3]), radius*np.sin(t[-3])),
                                    (radius*np.cos(t[-1]), radius*np.sin(t[-1])),
                                    arrowstyle='-|>', mutation_scale=16, color=purple))
    ax.add_patch(Circle((0, 0), .07, facecolor='white', edgecolor=purple, linewidth=1.7, zorder=8))
    ax.plot([-.5, .5], [-2.97, -2.97], color=ink, lw=1.4)
    ax.text(0, -3.08, '1 coordinate unit', ha='center', va='top', fontsize=9, color='#697585')

    fig.text(.045, .945, 'How the rotating ring changes nearby space and time', fontsize=23, weight='bold')
    mass, angular = archive['M_ADM_estimate'], archive['J_volume']
    fig.text(.045, .904, 'Blue shows the matter that forms the ring. Each label points to the place it describes.',
             fontsize=13, color='#586879')
    fig.text(.045, .865, 'View from above. The ring rotates around an axis through the central hole.',
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
    callout('Centre of the hole',
            [f'Clock: {60*centre["fixed_clock"]:.1f} min per distant hour',
             'Space is dragged around fastest here:',
             f'{np.degrees(centre["angular_drag"]):.1f}° per simulation time unit.'],
            (0., 0.), (.045, .815), purple, attach=(.265, .72))
    callout('Inside the ring',
            ['Clocks run slowest here.',
             f'Clock: {60*float(slow["fixed_clock"]):.1f} min per distant hour',
             f'Distance from centre: {slow_r:.2f}',
             f'Space turns at {np.degrees(float(slow["angular_drag"])):.1f}° per time unit.'],
            at(slow_r, 48), (.765, .815), red, attach=(.765, .70))
    callout('Inside the ring',
            ['Strongest sideways dragging.',
             'Holding position means moving against it',
             f'at {100*float(drag["drag_ratio"]):.0f}% of the speed of light.',
             f'Clock: {60*float(drag["fixed_clock"]):.1f} min per distant hour',
             f'Distance from centre: {drag_r:.2f}'],
            at(drag_r, 223), (.045, .43), teal, attach=(.265, .35))
    callout('Outside the ring',
            ['Distance from centre: 3.00', f'Clock: {60*float(outside["fixed_clock"]):.1f} min per distant hour',
             f'Space turns at {np.degrees(float(outside["angular_drag"])):.1f}° per time unit.',
             'Both effects weaken farther away.'],
            at(3., -22), (.765, .43), blue, attach=(.765, .30))
    fig.text(.5, .233, 'Darker blue shows where more matter is concentrated.',
             ha='center', fontsize=11, color='#153d70', bbox=dict(facecolor='#fcfcfa', edgecolor='none', pad=3))
    fig.text(.5, .207, 'Outlines: the matter density is half its maximum here.',
             ha='center', fontsize=10, color='#153d70', bbox=dict(facecolor='#fcfcfa', edgecolor='none', pad=2))
    fig.text(.045, .14, 'Nothing is forced to rotate here', fontsize=13, weight='bold', color=teal)
    fig.text(.045, .108, 'An ergoregion is a region where even light must turn with the ring. None is present.', fontsize=11.5)
    fig.text(.765, .14, 'Far away', fontsize=13, weight='bold', color=ink)
    fig.text(.765, .108, 'Clocks return to 60 min/hour.', fontsize=11.5)
    fig.text(.045, .061, 'Clock rates compare clocks held in place with a clock far away. '
             'Distances and turning rates use simulation units. Faint matter extends beyond the outlines.', fontsize=10, color='#586879')
    fig.text(.045, .033, 'Purple arrows show frame dragging: gravity carries nearby motion around with the ring. '
             'A particle can be sent through the central hole, perpendicular to this image.', fontsize=10, color='#586879')
    fig.savefig(output, dpi=220, facecolor=fig.get_facecolor())
    fig.savefig(output.with_suffix('.svg'), facecolor=fig.get_facecolor())
    svg = output.with_suffix('.svg')
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    from grteclyn_wrapper.visualisation.wormhole_merger.style import label_audit
    audit = label_audit(fig)
    plt.close(fig)
    report = dict(source=str(source), source_sha256=hashlib.sha256(Path(source).read_bytes()).hexdigest(),
                  centre=centre, extrema=extrema, mass=mass, angular_momentum=angular,
                  dimensionless_spin_abs=abs(angular)/mass**2, density_peak_radius=peak_radius,
                  outside_rho3={k:float(v) for k,v in outside.items()},
                  clocks='Held fixed: sqrt(-g_tt). Locally nonrotating: lapse exp(f/2). Both relative to asymptotic Killing time.',
                  map='One equatorial spatial view. Leader lines attach each measurement to its own position.',
                  search='Compactified radial scan and multistart location refinement. Coordinate, not proper, radii.',
                  drawn_boundary=dict(relative_density=.5, inner_radius=inner_edge, outer_radius=outer_edge,
                                      meaning='Half-peak equatorial energy-density contour; diffuse matter extends beyond it.'),
                  label_audit=audit,
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
    ap.add_argument('--out', type=Path, default=Path('results/railgun/figures/single-ring/ring070-physics.png'))
    ap.add_argument('--report', type=Path, default=Path('results/railgun/reports/ring070-physics'))
    args = ap.parse_args()
    create(args.source, args.out, args.report)


if __name__ == '__main__':
    main()
