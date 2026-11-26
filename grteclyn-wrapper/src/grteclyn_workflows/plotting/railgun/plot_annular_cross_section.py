"""Equatorial matter and metric profiles of the accepted concentric rings.

Read the portable spectral archive on a CPU; no solve or particle integration.
Radii are cylindrical coordinates, not proper distances. Each matter component
is normalised to its own peak, including in the spatial map.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from numpy.polynomial.chebyshev import chebval2d
from scipy.optimize import brentq

from grteclyn_stationary.numerics.spectral import cheb_coeffs
from grteclyn_workflows.plotting.optimisation.palette import BLUE, GREY, INK
from grteclyn_workflows.plotting.optimisation.plot_ring_physics import SavedRing

SOURCE = Path('results/railgun/studies/annular-validated-k12/accepted.npz')
OUTPUT = Path('results/railgun/figures/two-rings/annular-cross-section.png')
REPORT = Path('results/railgun/reports/annular-cross-section')
GAP_COLOUR = '#40856b'


def measurements(source=SOURCE):
    source = Path(source)
    ring = SavedRing(source)
    meta = ring.meta
    if (len(meta['fields']) != 2 or any(f['mass'] != 1 for f in meta['fields'])
            or meta['representation'] != 'dragging_cubic_regular_operator_v2'):
        raise ValueError('two mass-one fields in the regular cubic representation required')
    outcome_path = source.with_name('outcome.json')
    outcome = json.loads(outcome_path.read_text())
    name = f'grid_{meta["nx"]}x{meta["ny"]}'
    record_path = source.with_name(name+'.json')
    density_path = source.with_name(name+'_density.tsv')
    record = json.loads(record_path.read_text())
    if (not outcome['accepted'] or len(outcome['records']) != 3
            or any(row['verdict'] != 'PASS' for row in outcome['records'])
            or record['verdict'] != 'PASS'):
        raise ValueError('accepted three-grid field required')
    checksums = {line.split()[1].lstrip('*'): line.split()[0]
                 for line in source.with_name('sha256sums.txt').read_text().splitlines()}
    consumed = [source, outcome_path, record_path, density_path]
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in consumed}
    for filename, digest in hashes.items():
        if checksums[filename] != digest:
            raise ValueError(f'archive checksum mismatch: {filename}')
    gap = record['annular_gap']
    if not gap['accepted'] or not record['finite_height_channel']['accepted']:
        raise ValueError('validated annular matter channel required')
    archived = np.loadtxt(density_path)
    peaks = np.array([edge['peak_density'] for edge in gap['edges']])
    relative = archived[:, 1:].T/peaks[:, None]
    np.testing.assert_allclose(relative.max(axis=1), 1, atol=1e-12)
    radii = []
    for i, edge in enumerate(gap['edges']):
        row = relative[i]
        intervals = np.flatnonzero((row[:-1]-.5)*(row[1:]-.5) < 0)
        if len(intervals) != 2:
            raise ValueError('two resolved half-maximum crossings per component required')
        half = [brentq(lambda x: np.interp(x, archived[:, 0], row)-.5,
                       archived[j, 0], archived[j+1, 0]) for j in intervals]
        radii.append(dict(winding=meta['fields'][i]['winding'],
                          inner=half[0], peak=edge['peak_radius'], outer=half[1]))
    outer = 1.1*gap['edges'][1]['outer_radius']
    rr = np.unique(np.r_[0., archived[archived[:, 0] <= outer, 0], outer,
                         *[list(e[k] for k in ('inner', 'peak', 'outer')) for e in radii],
                         gap['inner_ring_outer_radius'], gap['outer_ring_inner_radius']])
    metric = ring.metric(rr, 0.)
    # Evaluate signed w from H itself, retaining the archive's regular
    # factorisation instead of inferring rotation from an absolute value.
    with np.load(source, allow_pickle=False) as saved:
        n = (meta['nx']+1)*(meta['ny']+1)
        h = saved['u'][n:2*n].reshape(meta['nx']+1, meta['ny']+1)
    coeff = cheb_coeffs(h, 1)  # radial entries already are Chebyshev coefficients
    s = (rr-meta['length'])/(rr+meta['length'])
    signed_w = (1-s)**meta['falloff_power']*chebval2d(s, -np.ones_like(s), coeff)
    np.testing.assert_allclose(np.abs(signed_w), metric['angular_drag'], atol=2e-15, rtol=2e-9)
    if np.any(metric['gtt'] >= 0):
        raise ValueError('this layout expects the accepted no-ergoregion case')
    np.testing.assert_allclose(metric['lapse'].min(), record['lapse_min'], atol=2e-6)
    np.testing.assert_allclose(np.abs(signed_w).max(), record['dragging_max'], atol=2e-10)
    np.testing.assert_allclose(metric['drag_ratio'].max(), record['shift_norm_over_lapse_max'], atol=2e-6)
    # The saved density starts at rho=0.001. Evaluate its finite central limit
    # independently; the winding-one field retains a nonzero gradient there.
    from grteclyn_stationary.railgun.gap import equatorial_densities
    central = equatorial_densities(meta, ring.u, np.array([1e-6, 2e-6]))
    np.testing.assert_allclose(central[:, 0], central[:, 1], atol=1e-16)
    density = np.array([np.interp(rr, archived[:, 0], row) for row in relative])
    density[:, 0] = central[:, 0]/peaks
    # Interpolation of the archived screen is only used for the density plot.
    # Validate the actual saved density at its own nodes independently.
    nodes = np.unique(np.linspace(0, len(archived)-1, 71, dtype=int))
    np.testing.assert_allclose(equatorial_densities(meta, ring.u, archived[nodes, 0]),
                               archived[nodes, 1:].T, atol=1e-18, rtol=1e-9)
    crossings = np.flatnonzero(signed_w[:-1]*signed_w[1:] < 0)
    reversal = [brentq(lambda radius: (1-(radius-meta['length'])/(radius+meta['length']))**3
                       *chebval2d((radius-meta['length'])/(radius+meta['length']), -1., coeff),
                       rr[j], rr[j+1]) for j in crossings]
    data = dict(source=str(source), source_sha256=hashes[source.name],
                archive_checksums=hashes, grid=[meta['nx'], meta['ny']],
                reference_radii=radii, annular_gap=gap,
                finite_height_channel=record['finite_height_channel'],
                M_ADM=record['M_ADM_estimate'], J_volume=record['J_volume'],
                component_J=record['matter_J'], density_peak_values=peaks.tolist(),
                no_ergoregion=True, signed_dragging_reversals=reversal,
                radius_limit=outer,
                radius_definition='Equatorial cylindrical radius rho; m=1; not proper distance.',
                reference_definition='Per-component half-maximum inner/outer radii and sampled density peak. '
                                     'Diffuse matter continues beyond the half-maximum contours.',
                gap_definition='Each component is below 1e-6 of its own peak; not exact vacuum.',
                map_definition='Maximum of the two separately peak-normalised component densities; '
                               'true coordinate scale; inset zooms the inner ring.',
                observers=dict(zamo='Omega=w=-beta^phi; d_tau/dt=alpha.',
                               static='Fixed coordinates: d_tau/dt=sqrt(-g_tt).',
                               time='Asymptotically normalised Killing time; 60 d_tau/dt in min per distant hour.'),
                scope='Stationary equatorial profiles; no particle trajectory or evolution.')
    return data, rr, density, metric, signed_w


def create(source=SOURCE, output=OUTPUT, reports=REPORT):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap, Normalize
    from matplotlib.lines import Line2D
    from matplotlib.patches import Circle, Patch, Wedge
    from grteclyn_workflows.plotting.wormhole_merger.style import prd, label_audit

    data, rr, density, metric, signed_w = measurements(source)
    prd(9.)
    plt.rcParams['pdf.fonttype'] = 42
    fig, axes = plt.subplots(2, 3, figsize=(7.05, 3.55), layout='constrained',
                             gridspec_kw={'width_ratios': [1., 1.15, 1.15]})
    fig.get_layout_engine().set(w_pad=.035, h_pad=.025, wspace=.025, hspace=.035)
    map_ax, density_ax, lapse_ax, clock_ax, drag_ax, ratio_ax = axes.flat
    titles = ('(a) Matter, $z=0$', '(b) Energy density', '(c) Lapse',
              '(d) Clock rates', '(e) Angular frame dragging', '(f) Shift relative to lapse')
    for ax, title in zip(axes.flat, titles):
        ax.set_title(title, loc='left', pad=14, fontsize=8.5)
    colours = (INK, BLUE)
    styles = (('inner', '--'), ('peak', ':'), ('outer', '-'))
    gap = data['annular_gap']
    left, right = gap['inner_ring_outer_radius'], gap['outer_ring_inner_radius']
    fig.legend([Line2D([], [], color=colour, lw=1.1) for colour in colours]
               + [Line2D([], [], color=GREY, lw=.7, ls=ls) for _, ls in styles]
               + [Patch(facecolor=GAP_COLOUR, alpha=.16, edgecolor='none')],
               [r'$k=+1$', r'$k=-12$', r'$\rho_{\rm in}$', r'$\rho_{\rm peak}$',
                r'$\rho_{\rm out}$', rf'Gap: ${left:.2f}$--${right:.2f}$'],
               loc='outside upper center', ncol=6, frameon=False,
               fontsize=7.3, handlelength=1.8, columnspacing=1.3)

    def key(ax, ncol=1):
        ax.legend(loc='lower left', bbox_to_anchor=(0, 1.015), borderaxespad=0,
                  handlelength=1.6, handletextpad=.4, labelspacing=.2,
                  fontsize=7.3, ncol=ncol, columnspacing=.8)

    cmap = LinearSegmentedColormap.from_list('annular_matter',
                                            ['#ffffff', '#dcecf6', BLUE, '#102e47'])
    extent = 1.25*data['reference_radii'][1]['outer']
    zoom_extent = 1.4*data['reference_radii'][0]['outer']
    inset = map_ax.inset_axes([.57, .57, .42, .42])
    for ax, limit, count in ((map_ax, extent, 601), (inset, zoom_extent, 251)):
        xy = np.linspace(-limit, limit, count)
        xx, yy = np.meshgrid(xy, xy)
        radius = np.hypot(xx, yy)
        d = np.maximum(*[np.interp(radius, rr, row) for row in density])
        im = ax.imshow(d, origin='lower', extent=(-limit, limit, -limit, limit),
                       cmap=cmap, norm=Normalize(0, 1), rasterized=True)
        if ax is map_ax:
            ax.add_patch(Wedge((0, 0), right, 0, 360, width=right-left,
                               facecolor=GAP_COLOUR, alpha=.16, edgecolor='none'))
            ax.add_patch(Circle((0, 0), right, fill=False, edgecolor=GAP_COLOUR,
                                lw=.6, alpha=.7))
            ax.add_patch(Circle((0, 0), left, fill=False, edgecolor=GAP_COLOUR,
                                lw=.6, alpha=.7))
        for record, colour in zip(data['reference_radii'], colours):
            for name, ls in styles:
                ax.add_patch(Circle((0, 0), record[name], fill=False,
                                    edgecolor=colour, lw=.65, ls=ls))
        ax.set(xlim=(-limit, limit), ylim=(-limit, limit), aspect='equal')
    inset.set_xticks([-10, 0, 10]); inset.set_yticks([-10, 0, 10])
    inset.tick_params(labelsize=4.5, length=1.5, pad=1)
    inset.minorticks_off()
    map_ax.set(xlabel=r'$mx$', ylabel=r'$my$')
    map_ax.set_xticks([-200, 0, 200]); map_ax.set_yticks([-200, 0, 200])
    cb_ax = map_ax.inset_axes([1.045, 0, .045, 1])
    cb = fig.colorbar(im, cax=cb_ax, ticks=[0, .5, 1])
    cb.ax.tick_params(labelsize=6., length=2)
    cb.ax.set_title(r'$\max_i\,\epsilon_i/\epsilon_{i,\rm peak}$', fontsize=6., pad=6)

    for i, colour in enumerate(colours):
        density_ax.semilogy(rr, np.maximum(density[i], 1e-30), color=colour, lw=1.25)
    density_ax.axhline(1e-6, color=GREY, ls=':', lw=.7)
    density_ax.set(ylabel=r'$\epsilon_i/\epsilon_{i,\rm peak}$', ylim=(1e-10, 2))
    lapse_ax.plot(rr, metric['lapse'], color=BLUE, lw=1.35, label=r'$\alpha=e^{f/2}$')
    lapse_ax.axhline(1, color=GREY, ls=':', lw=.7)
    lapse_ax.set(ylabel=r'$\alpha$', ylim=(.875, 1.005), yticks=[.9, .95, 1])
    key(lapse_ax)
    clock_ax.plot(rr, 60*metric['lapse'], color=BLUE, lw=1.35, label='ZAMO')
    clock_ax.plot(rr, 60*metric['fixed_clock'], color=INK, lw=1.1, ls='--', label='Static')
    clock_ax.axhline(60, color=GREY, ls=':', lw=.7)
    clock_ax.set(ylabel=r'$60\,d\tau/dt$', ylim=(52.5, 60.3), yticks=[54, 57, 60])
    key(clock_ax, 2)
    drag_ax.plot(rr, signed_w, color=BLUE, lw=1.35, label=r'$\Omega_{\rm ZAMO}=w$')
    drag_ax.axhline(0, color=GREY, lw=.7)
    drag_ax.set_yscale('symlog', linthresh=1e-8, linscale=.5)
    drag_ax.set(ylabel=r'$w/m$', ylim=(-.007, 2e-7),
                yticks=[-1e-3, -1e-5, -1e-7, 0, 1e-7])
    key(drag_ax)
    ratio_ax.plot(rr, metric['drag_ratio'], color=BLUE, lw=1.35, label=r'$|\beta|/\alpha$')
    ratio_ax.set(ylabel=r'$|\beta|/\alpha$', ylim=(0, .022))
    key(ratio_ax)
    for ax in (density_ax, lapse_ax, clock_ax, drag_ax, ratio_ax):
        ax.axvspan(left, right, color=GAP_COLOUR, alpha=.16, lw=0, zorder=0)
        for record, colour in zip(data['reference_radii'], colours):
            for name, ls in styles:
                ax.axvline(record[name], color=colour, ls=ls, lw=.6, alpha=.65, zorder=1)
        ax.set_xscale('symlog', linthresh=1., linscale=.65)
        ax.set(xlim=(0, data['radius_limit']), xlabel=r'$m\rho$')
        ax.set_xticks([0, 1, 10, 100, 300], labels=['0', '1', '10', '100', '300'])
        ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    for ax in (lapse_ax, clock_ax, ratio_ax):
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
            lambda value, _: '' if value == 0 else f'{value:g}'))
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    for suffix in ('.png', '.pdf'):
        fig.savefig(output.with_suffix(suffix), dpi=300, bbox_inches='tight', pad_inches=.04)
    audit = label_audit(fig)
    plt.close(fig)
    data['label_audit'] = audit
    data['profile_columns'] = ['m_rho', 'relative_density_k1', 'relative_density_kminus12',
                               'lapse', 'zamo_min_per_distant_hour', 'static_min_per_distant_hour',
                               'signed_w_over_m', 'shift_over_lapse', 'g_tt']
    reports = Path(reports)
    reports.parent.mkdir(parents=True, exist_ok=True)
    reports.with_suffix('.json').write_text(json.dumps(data, indent=2)+'\n')
    np.savetxt(reports.with_suffix('.tsv'), np.column_stack([
        rr, density.T, metric['lapse'], 60*metric['lapse'], 60*metric['fixed_clock'],
        signed_w, metric['drag_ratio'], metric['gtt']]),
        delimiter='\t', header='\t'.join(data['profile_columns']))
    if audit:
        raise ValueError('annular cross-section label audit failed')
    print(json.dumps(dict(figure=str(output), reference_radii=data['reference_radii'],
                         signed_dragging_reversals=data['signed_dragging_reversals'],
                         no_ergoregion=data['no_ergoregion'], label_audit=audit), indent=2))
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=SOURCE)
    parser.add_argument('--out', type=Path, default=OUTPUT)
    parser.add_argument('--report', type=Path, default=REPORT)
    args = parser.parse_args()
    create(args.source, args.out, args.report)


if __name__ == '__main__':
    main()
