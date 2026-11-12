"""Equatorial matter, clocks and dragging of a saved accepted scalar ring.

Rebuild from the tracked spectral field on a CPU; no solve or trajectory.
The radial coordinate is cylindrical radius on z=0, not proper distance.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

from grteclyn_workflows.plotting.optimisation.palette import BLUE, INK, GREY
from grteclyn_workflows.plotting.optimisation.plot_ring_comparison import profile


SOURCE = Path('results/railgun/studies/ergoregion-max-validate271/finalists/01/accepted.npz')
OUTPUT = Path('results/railgun/figures/particles/ergoregion-372-cross-section.png')
REPORT = Path('results/railgun/reports/ergoregion-372-cross-section')


def measurements(source):
    """Use the accepted field and its independent finest-grid record."""
    source = Path(source)
    from grteclyn_workflows.plotting.optimisation.plot_ring_physics import SavedRing

    ring = SavedRing(source)
    if ring.meta['fields'][0]['mass'] != 1:
        raise ValueError('this figure uses the scalar-mass-one convention')
    record = source.with_name(f'grid_{ring.meta["nx"]}x{ring.meta["ny"]}.json')
    checked = json.loads(record.read_text())
    outcome = json.loads(source.with_name('outcome.json').read_text())
    if checked.get('verdict') != 'PASS' or not outcome.get('accepted'):
        raise ValueError('passing finest-grid record and three-grid acceptance required')
    data = profile(source, record, provisional=False)
    p = {key: np.asarray(value) for key, value in data['profile'].items()}
    r = p['radius']
    relative = p['density']/data['density_peak']['value']
    cutoff = 1e-6
    i = np.flatnonzero((relative[:-1] >= cutoff) & (relative[1:] < cutoff))[-1]
    outer = brentq(lambda x: np.interp(x, r, relative)-cutoff, r[i], r[i+1])
    # The independent 2-D metric evaluator checks the 1-D equatorial sampling.
    sample = np.unique(np.r_[0., data['density_peak']['radius'],
                             data['ergoregion_edges'], np.geomspace(1e-4, outer, 101)])
    actual = ring.metric(sample, 0.)
    # Compare at the profile's own nodes to avoid interpolation error.
    select = (r <= outer)
    own = ring.metric(r[select], 0.)
    for key in ('lapse', 'angular_drag', 'drag_ratio', 'gtt'):
        np.testing.assert_allclose(own[key], p[key][select], rtol=2e-10, atol=2e-12)
    if not np.all(actual['lapse'] > 0) or not np.all(np.isfinite(relative)):
        raise ValueError('invalid metric or density')
    data['outer_density_cutoff'] = dict(relative_density=cutoff, radius=float(outer),
        meaning='Equatorial effective matter edge; diffuse tails continue beyond it.')
    data['minimum_lapse_equatorial'] = dict(radius=float(r[np.argmin(p['lapse'])]),
                                          value=float(p['lapse'].min()))
    data['centre_lapse'] = float(p['lapse'][0])
    data['observer_definitions'] = {
        'locally_nonrotating': 'dphi/dt = w = -beta^phi; d_tau/dt = alpha.',
        'fixed_coordinates': 'dphi/dt = 0; d_tau/dt = sqrt(-g_tt), only g_tt < 0.',
        'dragging': '|w| is angular rate; |beta|/alpha is a metric ratio, not local photon speed.',
        'time': 't is Killing time, normalized at infinity; clock minutes are 60 d_tau/dt.',
    }
    return data, p


def create(source=SOURCE, output=OUTPUT, reports=REPORT):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap, Normalize
    from matplotlib.lines import Line2D
    from matplotlib.patches import Circle, Patch
    from grteclyn_workflows.plotting.wormhole_merger.style import prd, label_audit

    data, p = measurements(source)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    outer = data['outer_density_cutoff']['radius']
    peak = data['density_peak']['radius']
    inner_half, outer_half = data['half_peak_edges']
    reference_radii = [('in', inner_half, '--', INK),
                       ('peak', peak, ':', GREY),
                       ('out', outer_half, '-', INK)]
    inner_ergo, outer_ergo = data['ergoregion_edges']
    r = p['radius']
    mask = r <= outer
    # Include exact ergosurfaces: the static-clock curve approaches zero at
    # each edge, but has no real-valued continuation inside the ergoregion.
    rr = np.unique(np.r_[r[mask], inner_ergo, outer_ergo, outer])
    interp = lambda key: np.interp(rr, r, p[key])
    lapse, gtt = interp('lapse'), interp('gtt')
    fixed = np.sqrt(np.maximum(-gtt, 0.))
    fixed[(rr > inner_ergo) & (rr < outer_ergo)] = np.nan
    fixed[np.isin(rr, (inner_ergo, outer_ergo))] = 0.
    prd(9.)
    plt.rcParams.update({'pdf.fonttype': 42, 'svg.fonttype': 'none'})
    fig, axes = plt.subplots(2, 3, figsize=(7.05, 3.55), layout='constrained',
                             gridspec_kw={'width_ratios': [1., 1.15, 1.15]})
    fig.get_layout_engine().set(w_pad=.035, h_pad=.025, wspace=.025, hspace=.035)
    map_ax, density_ax, lapse_ax, clock_ax, angular_ax, ratio_ax = axes.flat
    titles = ('(a) Matter, $z=0$', '(b) Energy density',
              '(c) Lapse', '(d) Clock rates', '(e) Angular frame dragging',
              '(f) Shift relative to lapse')
    for ax, title in zip(axes.flat, titles):
        ax.set_title(title, loc='left', pad=14, fontsize=8.5)

    fig.legend([Line2D([], [], color=colour, lw=.7, ls=linestyle)
                for _, _, linestyle, colour in reference_radii]
               + [Patch(facecolor=BLUE, alpha=.09, edgecolor='none')],
               [rf'$m\rho_{{\rm {name}}}={radius:.3f}$'
                for name, radius, _, _ in reference_radii] + ['Ergoregion'],
               loc='outside upper center', ncol=4,
               frameon=False, fontsize=7.5, handlelength=2., columnspacing=1.7)

    def key(ax, handles=None, labels=None, ncol=1):
        return ax.legend(handles=handles, labels=labels, loc='lower left',
                         bbox_to_anchor=(0, 1.015), borderaxespad=0,
                         handlelength=1.6, handletextpad=.4, labelspacing=.2,
                         fontsize=7.3, ncol=ncol, columnspacing=.8)

    # An equatorial plane is axisymmetric: its density map is exactly the
    # radial profile revolved around the axis. This is a zoom of the same cut.
    extent = 1.4*data['half_peak_edges'][-1]
    xy = np.linspace(-extent, extent, 501)
    xx, yy = np.meshgrid(xy, xy)
    d = np.interp(np.hypot(xx, yy), r, p['density'])/data['density_peak']['value']
    cmap = LinearSegmentedColormap.from_list('railgun_matter', ['#ffffff', '#dcecf6', BLUE, '#102e47'])
    image = map_ax.imshow(d, origin='lower', extent=(-extent, extent, -extent, extent),
                         cmap=cmap, norm=Normalize(vmin=0, vmax=1), rasterized=True)
    for _, radius, linestyle, colour in reference_radii:
        map_ax.add_patch(Circle((0, 0), radius, fill=False,
                                color=colour, lw=.7, ls=linestyle))
    map_ax.set(xlabel=r'$mx$', ylabel=r'$my$', aspect='equal')
    map_ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=3))
    map_ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=3))
    cb_ax = map_ax.inset_axes([1.045, 0, .045, 1])
    cb = fig.colorbar(image, cax=cb_ax, ticks=[0, .5, 1])
    cb.ax.tick_params(labelsize=6., length=2)
    cb.ax.set_title(r'$\epsilon/\epsilon_{\rm peak}$', fontsize=6.5, pad=6)

    density_ax.semilogy(rr, interp('density')/data['density_peak']['value'], color=BLUE,
                        lw=1.35, label=r'$\epsilon/\epsilon_{\rm peak}$')
    density_ax.axhline(1e-6, color=GREY, lw=.75, ls=':')
    density_ax.set(ylabel=r'$\epsilon/\epsilon_{\rm peak}$', ylim=(3e-7, 2))
    key(density_ax)
    lapse_ax.plot(rr, lapse, color=BLUE, lw=1.35, label=r'$\alpha=e^{f/2}$')
    lapse_ax.axhline(1, color=GREY, ls=':', lw=.7)
    lapse_ax.set(ylabel=r'$\alpha$', ylim=(0, 1.05))
    key(lapse_ax)
    clock_ax.plot(rr, 60*lapse, color=BLUE, lw=1.35, label='ZAMO')
    clock_ax.plot(rr, 60*fixed, color=INK, lw=1.1, ls='--', label='Static')
    clock_ax.axhline(60, color=GREY, ls=':', lw=.7)
    clock_ax.set(ylabel=r'$60\,d\tau/dt$', ylim=(0, 63))
    key(clock_ax, ncol=2)
    angular_ax.plot(rr, interp('angular_drag'), color=BLUE, lw=1.35,
                    label=r'$|\Omega_{\rm ZAMO}|=|w|$')
    angular_ax.set(ylabel=r'$|w|/m$', ylim=(0, 1.1*float(p['angular_drag'].max())))
    key(angular_ax)
    ratio_ax.plot(rr, interp('drag_ratio'), color=BLUE, lw=1.35, label=r'$|\beta|/\alpha$')
    ratio_ax.axhline(1, color=INK, lw=.8, ls='--', label=r'$g_{tt}=0$')
    ratio_ax.set(ylabel=r'$|\beta|/\alpha$', ylim=(0, 1.1*data['drag_max']['value']))
    ratio_ax.yaxis.set_major_locator(matplotlib.ticker.FixedLocator([0, 1, 2, 4]))
    key(ratio_ax, ncol=2)

    for ax in (density_ax, lapse_ax, clock_ax, angular_ax, ratio_ax):
        ax.axvspan(inner_ergo, outer_ergo, color=BLUE, alpha=.09, lw=0, zorder=0)
        for _, radius, linestyle, colour in reference_radii:
            ax.axvline(radius, color=colour, lw=.7, ls=linestyle, zorder=1)
        ax.set_xscale('symlog', linthresh=.15, linscale=.65)
        ax.set(xlim=(0, outer), xlabel=r'$m\rho$')
        ax.set_xticks([0, .1, .3, 1, 3], labels=['0', '0.1', '0.3', '1', '3'])
        ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    for ax in (lapse_ax, clock_ax, angular_ax, ratio_ax):
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
            lambda value, _: '' if value == 0 else f'{value:g}'))
    for suffix in ('.png', '.pdf'):
        fig.savefig(output.with_suffix(suffix), dpi=300, bbox_inches='tight', pad_inches=.04)
    audit = label_audit(fig)
    data['label_audit'] = audit
    data['figure_scope'] = 'Stationary equatorial cross-section; no particle trajectory or evolution.'
    data['layout'] = 'Shared radius/ergoregion key above all panels; descriptions in panel headers; mathematical axis labels.'
    data['map_style'] = dict(density_scale='linear', density_limits=[0, 1],
        coordinate_extent=[-extent, extent],
        reference_circles=[dict(name=name, radius=radius, linestyle=linestyle, color=colour)
                           for name, radius, linestyle, colour in reference_radii],
        reference_definition='Inner/outer are half-maximum energy-density radii, not material surfaces; '
                             'all circles match vertical lines in every radial panel.')
    data['profile_columns'] = ['m_rho', 'relative_energy_density', 'lapse',
        'zamo_min_per_distant_hour', 'fixed_min_per_distant_hour', 'abs_w_over_m',
        'shift_over_lapse', 'g_tt']
    reports = Path(reports)
    reports.parent.mkdir(parents=True, exist_ok=True)
    report = reports.with_suffix('.json')
    report.write_text(json.dumps({k: v for k, v in data.items() if k != 'profile'}, indent=2)+'\n')
    np.savetxt(reports.with_suffix('.tsv'), np.column_stack([
        rr, interp('density')/data['density_peak']['value'], lapse,
        60*lapse, 60*fixed, interp('angular_drag'), interp('drag_ratio'), gtt]),
        delimiter='\t', header='\t'.join(data['profile_columns']))
    plt.close(fig)
    if audit:
        raise ValueError('figure label audit failed')
    print(json.dumps(dict(figure=str(output), centre_minutes=60*data['centre_lapse'],
                         ergoregion_edges=data['ergoregion_edges'],
                         effective_outer_radius=outer, label_audit=audit), indent=2))
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
