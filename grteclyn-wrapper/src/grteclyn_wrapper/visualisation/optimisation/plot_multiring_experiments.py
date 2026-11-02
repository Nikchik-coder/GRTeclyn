"""Spatial explanations of the accepted separated rings and saved particle paths.

Only reads the existing accepted archives. No JAX, solves or integrations.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from .plot_ring_physics import SavedRing
from grteclyn_wrapper.optimisation.railgun.gap import cylindrical_densities


ROOT = Path('results/railgun')
BG, INK = '#fcfcfa', '#253445'
INNER, OUTER, GREEN, PURPLE = '#215a9b', '#219bc0', '#008579', '#7549a2'


def layout(title, subtitle, view, rect=(.235, .18, .53, .64)):
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'text.color': INK})
    fig = plt.figure(figsize=(16, 10), facecolor=BG)
    ax = fig.add_axes(rect)
    fig.text(.045, .945, title, fontsize=24, weight='bold')
    fig.text(.045, .904, subtitle, fontsize=12.5, color='#586879')
    fig.text(.045, .865, view, fontsize=11, color='#586879')
    return fig, ax


def callout(fig, ax, title, lines, point, corner, color, end):
    from matplotlib.patches import ConnectionPatch
    fx, fy = corner
    fig.text(fx, fy, title, fontsize=13, weight='bold', color=color, va='top')
    fig.text(fx, fy-.034, '\n'.join(lines), fontsize=11.2, color=INK,
             va='top', linespacing=1.45)
    ax.plot(*point, 'o', ms=6, color=color, mec='white', mew=1.2, zorder=12)
    fig.add_artist(ConnectionPatch(point, end, coordsA=ax.transData,
                                  coordsB=fig.transFigure, color=color, lw=1.2,
                                  connectionstyle='angle3,angleA=0,angleB=90', zorder=10))


def save(fig, name):
    import matplotlib.pyplot as plt
    from grteclyn_wrapper.visualisation.wormhole_merger.style import label_audit
    folder = 'particles' if name == 'multiring-particles-in-gap' else 'two-rings'
    output = ROOT/'figures'/folder/name
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output.with_suffix('.png'), dpi=220, facecolor=BG)
    fig.savefig(output.with_suffix('.svg'), facecolor=BG)
    svg = output.with_suffix('.svg')
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    audit = label_audit(fig)
    plt.close(fig)
    if audit:
        raise ValueError('figure label audit failed')


def point(radius, angle):
    theta = np.deg2rad(angle)
    return radius*np.cos(theta), radius*np.sin(theta)


def circle(ax, radius, color, *, linewidth=2.):
    from matplotlib.patches import Circle
    ax.add_patch(Circle((0, 0), radius, fill=False, edgecolor='white', lw=linewidth+1.7, zorder=4))
    ax.add_patch(Circle((0, 0), radius, fill=False, edgecolor=color, lw=linewidth, zorder=5))


def ring_map(ring, summary, profile, record):
    from matplotlib.patches import Wedge, FancyArrowPatch
    gap = summary['annular_field']['gap']
    radii = profile[:, 0]
    densities = profile[:, 1:3].T
    normal = densities/np.max(densities, axis=1)[:, None]
    peaks = [float(radii[np.argmax(row)]) for row in densities]
    x = np.linspace(-220., 220., 901)
    xx, yy = np.meshgrid(x, x)
    rho = np.hypot(xx, yy)
    colors = np.array([[.13, .35, .61], [.13, .61, .75]])
    rgb = np.broadcast_to(np.array([252, 252, 250])/255., (*rho.shape, 3)).copy()
    for row, color in zip(normal, colors):
        opacity = .83*np.interp(rho, radii, row)**.65
        rgb = rgb*(1-opacity[..., None])+color*opacity[..., None]
    fig, ax = layout('Two separated rings turning in opposite directions',
                     'Their equal and opposite spins cancel, while nearby space still turns.',
                     'View from above. Both rings have the same centre. Their relative sizes are shown to scale.')
    ax.imshow(rgb, origin='lower', extent=[-220, 220, -220, 220])
    for row, color in zip(normal, (INNER, OUTER)):
        ids = np.flatnonzero(row >= .5)
        for index in (ids[0], ids[-1]):
            circle(ax, radii[index], color, linewidth=1.6)
    left, right = gap['inner_ring_outer_radius'], gap['outer_ring_inner_radius']
    ax.add_patch(Wedge((0, 0), right, 0, 360, width=right-left,
                       facecolor='#85d6b3', edgecolor=GREEN, lw=.8, alpha=.7, zorder=6))
    for radius, angle, direction, color in [(14., 135, -1, INNER), (peaks[1], 75, 1, OUTER)]:
        t = np.deg2rad(np.linspace(angle, angle+direction*45, 61))
        ax.plot(radius*np.cos(t), radius*np.sin(t), color=color, lw=2, zorder=7)
        ax.add_patch(FancyArrowPatch(point(radius, np.degrees(t[-4])), point(radius, np.degrees(t[-1])),
                                    arrowstyle='-|>', mutation_scale=17, color=color, zorder=8))
    ax.set(xlim=(-220, 220), ylim=(-220, 220), aspect='equal')
    ax.axis('off')
    ax.plot(0, 0, '+', color=INK, ms=7, zorder=12)
    ax.plot([-50, 50], [-210, -210], color=INK, lw=1.4)
    ax.text(0, -225, '100 simulation length units', ha='center', va='top', fontsize=9, color='#697585')
    midpoint = gap['corridor']['midpoint_radius']
    inner_clock = float(ring.metric(peaks[0], 0.)['fixed_clock'])*60
    outer_clock = float(ring.metric(peaks[1], 0.)['fixed_clock'])*60
    gap_metric = ring.metric(midpoint, 0.)
    outside = ring.metric(210., 0.)
    callout(fig, ax, 'Small inner ring',
            ['Dark blue, turning clockwise.', 'Matter is most concentrated',
             f'{peaks[0]:.1f} units from the shared centre.', f'Clock: {inner_clock:.1f} min per distant hour.'],
            point(peaks[0], 135), (.045, .815), INNER, (.26, .70))
    callout(fig, ax, 'Large outer ring',
            ['Light blue, turning anticlockwise.', 'Matter is most concentrated',
             f'{peaks[1]:.0f} units from the same centre.', f'Clock: {outer_clock:.1f} min per distant hour.'],
            point(peaks[1], 40), (.765, .815), OUTER, (.765, .70))
    callout(fig, ax, 'Space for the particle experiment',
            ['The green band marks the clear gap.', f'Distance from centre: {left:.1f} to {right:.1f}.',
             'Each ring contributes less than one', 'millionth of its largest matter density.',
             f'Clock near the middle: {60*float(gap_metric["fixed_clock"]):.1f} min/hour.'],
            point(midpoint, 225), (.045, .43), GREEN, (.265, .32))
    callout(fig, ax, 'Farther from the centre',
            ['At distance 210 from the centre:', f'Clock: {60*float(outside["fixed_clock"]):.1f} min per distant hour.',
             'The total spin is zero to the', 'accuracy of the calculation.'],
            point(210., -25), (.765, .43), PURPLE, (.765, .30))
    fig.text(.5, .226, 'Green marks very little matter, not a solid surface.', ha='center', color=GREEN, fontsize=11,
             bbox=dict(facecolor=BG, edgecolor='none', pad=3))
    fig.text(.045, .14, 'Cancelled total spin does not remove local dragging', fontsize=13, weight='bold', color=PURPLE)
    centre = ring.metric(0., 0.)
    fig.text(.045, .108, f'At the common centre, space still turns by {np.degrees(float(centre["angular_drag"])):.3f}° per simulation time unit.',
             fontsize=11.5)
    fig.text(.045, .061, 'Each ring is coloured relative to its own largest density so both are visible. '
             'Outlines mark half that density. Arrows show opposite matter rotation.', fontsize=10, color='#586879')
    fig.text(.045, .033, 'Clock rates are for clocks held in place. The rings have faint tails. '
             'No region forces all light to turn with the rings. This is the saved stationary solution.', fontsize=10, color='#586879')
    save(fig, 'multiring-separated-space')
    record['spatial_map'] = dict(peak_radii=peaks, clocks_minutes_per_distant_hour=dict(
        inner=inner_clock, outer=outer_clock, gap=60*float(gap_metric['fixed_clock']), outside=60*float(outside['fixed_clock'])),
        centre_turning_degrees_per_time=float(np.degrees(centre['angular_drag'])),
        boundary='Half each ring own peak energy density; green uses the separate 1e-6 threshold.',
        scale='True relative coordinate sizes. Each density colour has its own normalisation.')


def particle_map(ring, summary, record):
    from matplotlib.patches import Rectangle
    import matplotlib.patheffects as pe
    directory = ROOT/'studies/annular-transit-k12'
    outcome = json.loads((directory/'outcome.json').read_text())
    if not outcome['accepted']:
        raise ValueError('accepted particle experiment required')
    plan = json.loads((directory/'manifest.json').read_text())['plan']
    peak = np.array(plan['peak_densities'])
    r = np.linspace(31., 43., 161)
    z = np.linspace(-12., 12., 241)
    rr, zz = np.meshgrid(r, z)
    density = cylindrical_densities(ring.meta, ring.u, rr, zz)/peak[:, None, None]
    fig, ax = layout('Spinning particles passed between the two rings',
                     'All three spin choices crossed the same low-matter space and reached the other side.',
                     'Side view of the gap only. The inner ring is to the left; the outer ring is to the right.')
    rgb = np.broadcast_to(np.array([252, 252, 250])/255., (*rr.shape, 3)).copy()
    for row, color in zip(density, ([.13, .35, .61], [.13, .61, .75])):
        alpha = .12+.3*np.clip(np.log10(np.maximum(row, 1e-30)/1e-6)/2, 0, 1)
        alpha = np.where(row >= 1e-6, alpha, 0.)
        rgb = rgb*(1-alpha[..., None])+np.array(color)*alpha[..., None]
    ax.imshow(rgb, origin='lower', extent=[31, 43, -12, 12], aspect='equal')
    for row, color in zip(density, (INNER, OUTER)):
        ax.contour(rr, zz, row, levels=[1e-6], colors=[color], linewidths=2.)
    field = summary['annular_field']['tube']
    ax.add_patch(Rectangle((field['rho_min'], -10), field['rho_max']-field['rho_min'], 20,
                           facecolor='#9fe1c3', edgecolor=GREEN, alpha=.3, lw=1.2, zorder=2))
    endpoints = {}
    for name, color, style in [('zero', INK, '--'), ('positive', '#bc4a3c', '-'), ('negative', PURPLE, ':')]:
        with np.load(directory/f'rk1_{name}.npz') as data:
            states = data['state']
            matter = data['density']/peak[:, None]
        rho = np.hypot(states[:, 1], states[:, 2])
        if name == 'zero':
            no_spin_rho, no_spin_z = rho.copy(), states[:, 3].copy()
        if np.max(matter) >= 1e-6 or abs(states[-1, 3]+10) > 1e-8:
            raise ValueError('saved path does not satisfy the figure claim')
        ax.plot(rho, states[:, 3], color=color, ls=style, lw=1.7,
                path_effects=[pe.Stroke(linewidth=3., foreground='white'), pe.Normal()], zorder=6)
        endpoints[name] = [float(rho[-1]), float(states[-1, 3])]
    launch = (plan['launch_rho'], 10.)
    final = tuple(endpoints['zero'])
    lower = int(np.argmin(abs(no_spin_z+.8)))
    upper = int(np.argmin(abs(no_spin_z-1.)))
    middle = int(np.argmin(abs(no_spin_z)))
    ax.annotate('', xy=(no_spin_rho[lower], no_spin_z[lower]),
                xytext=(no_spin_rho[upper], no_spin_z[upper]),
                arrowprops=dict(arrowstyle='-|>', lw=2, color=INK), zorder=8)
    ax.set(xlim=(31, 43), ylim=(-12, 12), aspect='equal')
    ax.axis('off')
    ax.text(31.2, 11.6, 'Toward the inner ring ←', color=INNER, fontsize=9, ha='left')
    ax.text(42.8, 11.6, '→ Toward the outer ring', color=OUTER, fontsize=9, ha='right')
    ax.plot([35, 39], [-11.5, -11.5], color=INK, lw=1.3)
    ax.text(37, -12.1, '4 simulation length units', ha='center', fontsize=9, color='#697585')
    callout(fig, ax, 'Very little matter along the route',
            ['Green shows the space checked', 'before launching the particles.',
             'Both rings stay below one millionth', 'of their own largest matter density.'],
            (35.7, 4.), (.045, .815), GREEN, (.26, .70))
    callout(fig, ax, 'Same starting conditions',
            ['All three start at the marked point.', 'They have the same total energy.',
             'One has no spin; the other two', 'spin in opposite directions.'],
            launch, (.765, .815), INNER, (.765, .70))
    callout(fig, ax, 'The three paths nearly coincide',
            ['The three spin choices follow', 'almost the same path.',
             'Their separation is too small', 'to see at this scale.'],
            (no_spin_rho[middle], no_spin_z[middle]), (.045, .43), PURPLE, (.26, .32))
    callout(fig, ax, 'All three reached the other side',
            ['No particle was sent back.', 'The two opposite spins arrived',
             'only 0.0000036 simulation time', 'units apart.'],
            final, (.765, .43), GREEN, (.765, .30))
    fig.text(.045, .14, 'Spin changed the arrival time only slightly', fontsize=13, weight='bold', color=PURPLE)
    fig.text(.045, .108, 'All eight paths, including the numerical checks, passed through without leaving the low-matter space.', fontsize=11.5)
    fig.text(.045, .061, 'Blue lines mark where either ring reaches one millionth of its own largest matter density. '
             'Blue shading is toward more matter.', fontsize=10, color='#586879')
    fig.text(.045, .033, 'The starting height is +10 and the final height is −10 simulation length units. '
             'This measures passage through a finite distance, not escape to infinity.', fontsize=10, color='#586879')
    save(fig, 'multiring-particles-in-gap')
    record['particle_map'] = dict(launch=list(launch), endpoints=endpoints,
        matched_energy=summary['annular_transport']['energy'],
        opposite_spin_arrival_difference=summary['annular_transport']['coordinate_time_positive_minus_negative'],
        all_eight_passed=True, paths_shifted_for_display=False,
        scope='Actual saved finite passage, not an escape or net energy gain test.')


def main():
    import matplotlib
    matplotlib.use('Agg')
    source = ROOT/'studies/annular-validated-k12/accepted.npz'
    summary = json.loads((ROOT/'reports/completed-experiments.json').read_text())
    if not summary['all_accepted']:
        raise ValueError('accepted experimental summary required')
    ring = SavedRing(source)
    profile = np.loadtxt(source.with_name('grid_256x20_density.tsv'))
    record = dict(source=str(source), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  overlapping_rings_included=False, style='One spatial view per image; plain descriptions attached to locations.')
    ring_map(ring, summary, profile, record)
    print('[figures] separated-ring map complete', flush=True)
    particle_map(ring, summary, record)
    (ROOT/'reports/multiring-explanatory.json').write_text(json.dumps(record, indent=2)+'\n')
    print('[figures] particle map complete', flush=True)


if __name__ == '__main__':
    main()
