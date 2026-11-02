"""Compare saved ring profiles without JAX, a new solve or a particle track.

The snapshot command writes only the small, immutable numeric inputs needed by
the figure. Single-grid candidates require a passing independent record and
are explicitly distinguished from the earlier three-grid accepted field.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path

import numpy as np
from numpy.polynomial.chebyshev import chebval, chebder
from scipy.optimize import minimize_scalar, brentq

from grteclyn_wrapper.analysis.spinning_wormhole.spectral import cheb_coeffs


INK, MUTED = '#253445', '#617287'
BLUE, PURPLE, TEAL, ORANGE = '#153d70', '#7549a2', '#008579', '#c46720'
PAPER = '#fcfcfa'


def profile(source, record, *, provisional):
    raw = Path(source).read_bytes()
    row = json.loads(Path(record).read_text())
    with np.load(source, allow_pickle=False) as data:
        meta = json.loads(str(data['metadata']))
        u = np.array(data['physical_u' if 'physical_u' in data else 'u'])
    if provisional:
        if row.get('verdict') != 'PASS' or not row.get('independent'):
            raise ValueError('independently passing candidate required')
    elif not meta.get('validated'):
        raise ValueError('three-grid accepted reference required')
    if len(meta['fields']) != 1 or meta['fields'][0]['winding'] != 1:
        raise ValueError('single k=1 scalar ring required')
    nx, ny = meta['nx'], meta['ny']
    if row['grid'] != [nx, ny]:
        raise ValueError('record grid differs from saved field')
    n = (nx+1)*(ny+1)
    a = u[:5*n].reshape(5, nx+1, ny+1)
    c = [cheb_coeffs(v[:, -1], 0) for v in a]
    length = meta['length']

    def metric(r):
        r = np.asarray(r)
        s = (r-length)/(r+length)
        f, w, _, b = [chebval(s, v) for v in c[:4]]
        lapse = np.exp(f/2)
        ratio = (1+b)*np.exp(-f)*np.abs(w)*r
        return lapse, np.abs(w), ratio, lapse*lapse*(ratio*ratio-1)

    field = meta['fields'][0]
    frequency = float(u[5*n])

    def density(r):
        r = np.asarray(r)
        s = (r-length)/(r+length)
        f, w, N, b, q = [chebval(s, v) for v in c]
        qr = chebval(s, chebder(c[4]))*2*length/(r+length)**2
        potential = field['mass']**2*q*q+field['quartic']*q**4+field['sextic']*q**6
        # Even parity gives zero theta derivative on the equator.
        return ((frequency+w)**2*np.exp(-f)*q*q
                +np.exp(f-N)/(1+b)**2*qr**2
                +np.exp(f)*q*q/((1+b)**2*r*r)+potential)/(8*np.pi)

    radii = np.r_[0., np.geomspace(1e-5, 30., 6000)]
    lapse, angular, ratio, gtt = metric(radii)
    energy = density(radii[1:])

    def extreme(values, function, *, maximum=True, positive=False):
        rr = radii[1:] if positive else radii
        i = int(np.argmax(values) if maximum else np.argmin(values))
        lo, hi = rr[max(0, i-1)], rr[min(len(rr)-1, i+1)]
        sign = -1 if maximum else 1
        fit = minimize_scalar(lambda r: sign*float(function(r)), bounds=(lo, hi),
                              method='bounded', options={'xatol': 1e-12})
        if not fit.success:
            raise ValueError('profile extremum refinement failed')
        candidates = [float(lo), float(hi), float(fit.x)]
        r = min(candidates, key=lambda x: sign*float(function(x)))
        return dict(radius=r, value=float(function(r)))

    peak = extreme(energy, density, positive=True)
    drag = extreme(ratio, lambda r: metric(r)[2])
    gt = extreme(gtt, lambda r: metric(r)[3])
    if abs(drag['value']-row['shift_norm_over_lapse_max']) > .003:
        raise ValueError('profile disagrees with independently checked record')

    def crossings(values, function):
        indices = np.flatnonzero(values[:-1]*values[1:] < 0)
        return [float(brentq(function, radii[i], radii[i+1], xtol=1e-13)) for i in indices]

    # Evaluate the finite central density using its smooth positive-r limit.
    d = np.r_[float(density(1e-6)), energy]
    edges = crossings(d-.5*peak['value'], lambda r: float(density(max(r, 1e-7))-.5*peak['value']))
    ergo = crossings(gtt, lambda r: float(metric(r)[3]))
    if len(edges) != 2 or len(ergo) != 2:
        raise ValueError('two half-density and two ergoregion edges required')
    centre_lapse = float(metric(0.)[0])
    return dict(source=str(source), source_sha256=hashlib.sha256(raw).hexdigest(),
        record=str(record), record_sha256=hashlib.sha256(Path(record).read_bytes()).hexdigest(),
        provisional=provisional, grid=[nx, ny], frequency=frequency,
        mass=row['M_ADM_estimate'], angular_momentum=row['J_volume'],
        centre_clock_minutes_per_distant_hour=60*centre_lapse,
        centre_angular_degrees_per_time_unit=float(np.degrees(metric(0.)[1])),
        density_peak=peak, half_peak_edges=edges, ergoregion_edges=ergo,
        drag_max=drag, gtt_max=gt,
        profile=dict(radius=radii.tolist(), density=d.tolist(), lapse=lapse.tolist(),
                     angular_drag=angular.tolist(), drag_ratio=ratio.tolist(), gtt=gtt.tolist()),
        clock_definition='Held at the coordinate centre, where the shift vanishes: exp(f/2).',
        units='G=c=scalar mass=1; radii are coordinate distances, not proper distances.',
        stability='not_assessed')


def snapshot(out):
    out = Path(out)
    if out.exists():
        raise ValueError('snapshot already exists; keep its inputs immutable')
    baseline = Path('results/railgun/studies/ergoregion-cma/finalists/01')
    cases = [dict(title='Previous validated maximum',
                  **profile(baseline/'accepted.npz', baseline/'grid_192x24.json', provisional=False))]
    for seed in (272, 271):
        directory = Path(f'runs/railgun/single-ring/scans/ergoregion-max-seed{seed}-20261102')
        progress = json.loads((directory/'progress.json').read_text())
        candidates = [r for r in progress['evaluations'] if r.get('passed') and r.get('sample')]
        best = max(candidates, key=lambda r: r['sample']['shift_norm_over_lapse_max'])
        state = Path(best['path'])
        cases.append(dict(title=f'Current search · seed {seed}',
                          **profile(state, state.with_name('record.json'), provisional=True)))
    timestamp = datetime.now(timezone(timedelta(hours=3))).isoformat(timespec='seconds')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(timestamp_msk=timestamp, cases=cases,
        scope='Immutable figure-input snapshot; not a completed campaign archive.'), indent=2)+'\n')
    print(json.dumps(dict(snapshot=str(out), timestamp_msk=timestamp,
                         dragging=[c['drag_max'] for c in cases]), indent=2))


def render(snapshot_path, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patches import Circle, Wedge, FancyArrowPatch, ConnectionPatch
    data = json.loads(Path(snapshot_path).read_text())
    cases = data['cases']
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12,
                         'text.color': INK, 'svg.fonttype': 'none'})
    fig = plt.figure(figsize=(21, 13), facecolor=PAPER)
    fig.text(.045, .953, 'Smaller rings drag space more strongly', fontsize=29, weight='bold')
    fig.text(.045, .913, 'The same rotating matter model, concentrated into a smaller region. '
             'Every ring below uses the same distance scale.', fontsize=14, color=MUTED)
    # One key above all panels; orange encodes the actual g_tt > 0 interval.
    legend_y = .871
    for x, color, text in [(.045, BLUE, 'Blue: matter'), (.245, ORANGE, 'Orange band: everything must rotate'),
                           (.645, PURPLE, 'Purple dot: centre of the hole')]:
        fig.text(x, legend_y, '●', color=color, fontsize=15)
        fig.text(x+.015, legend_y, text, fontsize=12)
    cmap = LinearSegmentedColormap.from_list('ringblue', [PAPER, '#e9f2ff', '#b6d2fa', '#5191d5', '#1c5798'])
    extent = 1.65
    xx = np.linspace(-extent, extent, 901)
    x, y = np.meshgrid(xx, xx)
    rr = np.hypot(x, y)
    for i, case in enumerate(cases):
        left = .045+i*.315
        fig.text(left, .817, case['title'], fontsize=17, weight='bold')
        status = 'Three resolutions passed' if not case['provisional'] else 'Single grid passed · refinement pending'
        fig.text(left, .788, status, fontsize=11, color=TEAL if not case['provisional'] else ORANGE)
        fig.text(left, .739, f'{case["drag_max"]["value"]:.2f}', fontsize=35, weight='bold', color=TEAL)
        fig.text(left+.080, .743, 'peak dragging measure', fontsize=12, color=TEAL)
        ax = fig.add_axes([left-.008, .362, .297, .365])
        profile = case['profile']
        relative = np.interp(rr, profile['radius'], np.array(profile['density'])/case['density_peak']['value'])
        ax.imshow(relative, extent=(-extent, extent, -extent, extent), origin='lower',
                  cmap=cmap, vmin=0, vmax=1, interpolation='bilinear', rasterized=True)
        inner, outer = case['ergoregion_edges']
        ax.add_patch(Wedge((0, 0), outer, 0, 360, width=outer-inner,
                           facecolor='#f2a647', alpha=.23, edgecolor='none', zorder=3))
        for r in (inner, outer):
            ax.add_patch(Circle((0, 0), r, fill=False, color=ORANGE, lw=1.4, ls=(0, (4, 3)), zorder=5))
        for r in case['half_peak_edges']:
            ax.add_patch(Circle((0, 0), r, fill=False, color='white', lw=3.4, zorder=6))
            ax.add_patch(Circle((0, 0), r, fill=False, color=BLUE, lw=1.5, zorder=7))
        ax.plot(0, 0, 'o', ms=6, mfc='white', mec=PURPLE, mew=1.8, zorder=10)
        ax.plot(0, 0, 'o', ms=2.5, color=PURPLE, zorder=11)
        # One point for the density maximum, another for the dragging maximum.
        peak_r = case['density_peak']['radius']
        drag_r = case['drag_max']['radius']
        p_drag = (-drag_r/np.sqrt(2), -drag_r/np.sqrt(2))
        ax.plot(*p_drag, 'o', ms=5, color=TEAL, mec='white', mew=1, zorder=11)
        radius = min(extent*.84, max(case['half_peak_edges'][1], outer)*1.15)
        t = np.deg2rad(np.linspace(65, -10, 80))
        ax.plot(radius*np.cos(t), radius*np.sin(t), color=PURPLE, lw=1.6, alpha=.7)
        ax.add_patch(FancyArrowPatch((radius*np.cos(t[-3]), radius*np.sin(t[-3])),
                                    (radius*np.cos(t[-1]), radius*np.sin(t[-1])),
                                    arrowstyle='-|>', mutation_scale=15, color=PURPLE))
        ax.set(xlim=(-extent, extent), ylim=(-extent, extent), aspect='equal')
        ax.axis('off')
        def leader(point, xy, color):
            fig.add_artist(ConnectionPatch(xyA=point, coordsA=ax.transData, xyB=xy,
                coordsB=fig.transFigure, color=color, lw=1.1,
                connectionstyle='angle3,angleA=0,angleB=90', zorder=12))
        # Leaders terminate at separate labels outside the blue matter.
        leader((0, 0), (left+.018, .393), PURPLE)
        leader(p_drag, (left+.065, .725), TEAL)
        fig.text(left, .374, 'Centre of the hole', fontsize=12, weight='bold', color=PURPLE)
        fig.text(left, .346, f'{case["centre_clock_minutes_per_distant_hour"]:.1f} min per distant hour', fontsize=14, color=PURPLE)
        fig.text(left, .302, 'Where matter is most concentrated', fontsize=12, weight='bold', color=BLUE)
        fig.text(left, .275, f'Radius {peak_r:.2f}  ·  peak density {case["density_peak"]["value"]:.3f}', fontsize=13)
        fig.text(left, .230, 'Region where everything must rotate', fontsize=12, weight='bold', color=ORANGE)
        fig.text(left, .203, f'From radius {inner:.2f} to {outer:.2f} in this view', fontsize=13)
        fig.text(left, .160, f'Mass {case["mass"]:.3f}   |   total spin magnitude {abs(case["angular_momentum"]):.3f}',
                 fontsize=11.5, color=MUTED)
        # Identical scale bars make the contraction visible without rescaling.
        ax.plot([-.5, .5], [-1.50, -1.50], color=INK, lw=1.4)
        ax.text(0, -1.57, '1 coordinate unit', fontsize=9, ha='center', va='top', color=MUTED)
    fig.text(.045, .104, 'Stronger local dragging comes from tighter concentration and slower clocks, '
             'even though total spin decreases.', fontsize=15, weight='bold')
    fig.text(.045, .067, 'Dragging above 1 means holding a fixed position is impossible; it is not a matter speed. '
             'Solid outlines mark half the peak density; faint matter extends beyond them.', fontsize=11, color=MUTED)
    fig.text(.045, .039, 'Clocks shown are held at the centre of the hole. Distances, mass and spin use simulation units. '
             'Dynamical stability is untested.', fontsize=11, color=MUTED)
    stamp = datetime.fromisoformat(data['timestamp_msk']).strftime('%d %b %Y, %H:%M MSK')
    fig.text(.045, .015, f'Saved search snapshot: {stamp}. Blue intensity is relative to each ring’s own peak.',
             fontsize=10, color=MUTED)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=260, facecolor=PAPER)
    fig.savefig(output.with_suffix('.svg'), facecolor=PAPER)
    svg = output.with_suffix('.svg')
    svg.write_text('\n'.join(s.rstrip() for s in svg.read_text().splitlines())+'\n')
    from grteclyn_wrapper.visualisation.wormhole_merger.style import label_audit
    issues = label_audit(fig)
    # Figure-level prose also needs overlap checks (the shared audit covers axes).
    renderer = fig.canvas.get_renderer()
    for i, a in enumerate(fig.texts):
        for b in fig.texts[i+1:]:
            if a.get_window_extent(renderer).overlaps(b.get_window_extent(renderer)):
                issues.append(f'text overlap: {a.get_text()[:45]} / {b.get_text()[:45]}')
    plt.close(fig)
    audit = Path(snapshot_path).with_name('ergoregion-comparison-audit.json')
    audit.write_text(json.dumps(dict(label_audit=issues, input=str(snapshot_path),
                                    input_sha256=hashlib.sha256(Path(snapshot_path).read_bytes()).hexdigest()), indent=2)+'\n')
    print(json.dumps(dict(output=str(output), label_audit=issues), indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--snapshot', type=Path, required=True)
    ap.add_argument('--capture', action='store_true')
    ap.add_argument('--out', type=Path, default=Path('results/railgun/figures/single-ring/ergoregion-comparison.png'))
    args = ap.parse_args()
    if args.capture:
        snapshot(args.snapshot)
    else:
        render(args.snapshot, args.out)


if __name__ == '__main__':
    main()
