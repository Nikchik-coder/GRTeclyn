"""Actual finite uphill tracks, with a zoom on the endpoint/turnaround split."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np


def plot(directory, out, *, title=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from grteclyn_workflows.plotting.wormhole_merger import style
    from .palette import BLUE, INK, GREY

    directory = Path(directory)
    result = json.loads((directory/'outcome.json').read_text())
    if not result.get('accepted'):
        raise ValueError('accepted uphill integration study required')
    regime = 'requested_offset'
    if result['selection_regimes'] and regime not in result['selection_regimes']:
        regime = result['selection_regimes'][0]
    controls = result['records'][regime+'_rk1']['controls']
    manifest = json.loads((directory/'manifest.json').read_text())
    config = manifest['config']
    if 'target_z' not in config:
        config = manifest.get('physical_config') or json.loads(
            (directory/'original/manifest.json').read_text())['config']
    target = config['target_z']
    style.prd(8.5)
    plt.rcParams['pdf.fonttype'] = 42
    fig, (overview, zoom) = plt.subplots(1, 2, figsize=(7.05, 2.55), layout='constrained')
    fig.get_layout_engine().set(w_pad=.035, h_pad=.025, wspace=.025, hspace=.035)
    formats = [('zero', GREY, '--', r'$S_z=0$'),
               ('positive', BLUE, '-', r'$S_z=+10^{-3}$'),
               ('negative', INK, '-.', r'$S_z=-10^{-3}$')]
    curves = []
    for label, colour, ls, _ in formats:
        with np.load(directory/f'{regime}_rk1_{label}.npz', allow_pickle=False) as data:
            state = data['state']
        t, z = state[:, 0], state[:, 3]
        curves.append((t, z))
        overview.plot(t, z, color=colour, ls=ls, lw=1.2)
        zoom.plot(t, z-target, color=colour, ls=ls, lw=1.2)
        marker = 's' if controls[label]['classification'] == 'reflected' else 'o'
        zoom.plot(t[-1], z[-1]-target, marker=marker, ls='none', color=colour,
                  mfc='white', mew=1., ms=3.6, zorder=5, clip_on=False)
    overview.axhline(target, color=GREY, lw=.65, zorder=0)
    zoom.axhline(0, color=GREY, lw=.65, zorder=0)
    end = max(t[-1] for t, z in curves)
    overview.set(xlabel=r'$t$', ylabel=r'$z$', xlim=(0, 1.02*end))
    zoom.set(xlabel=r'$t$', ylabel=r'$z-z_f$', xlim=(.95*end, 1.01*end))
    zoom.set_yscale('symlog', linthresh=1e-8)
    zoom.set_ylim(-1e-9, 2.)
    zoom.set_yticks([0, 1e-6, 1e-4, 1e-2, 1.])
    for ax, heading in ((overview, '(a) Axial trajectory'), (zoom, '(b) Target approach')):
        ax.set_title(heading, loc='left', fontsize=8.5, pad=4)
    handles = [Line2D([], [], color=colour, ls=ls, lw=1.2)
               for _, colour, ls, _ in formats]
    handles += [Line2D([], [], color=INK, marker=marker, mfc='white',
                       ls='none', ms=3.6, mew=1.) for marker in ('o', 's')]
    fig.legend(handles, [label for _, _, _, label in formats] + ['Arrival', 'Turnaround'],
               loc='outside upper center', ncol=5, frameon=False,
               fontsize=7.5, handlelength=2., columnspacing=1.6)
    # The legacy title argument remains accepted for existing reproduction
    # commands. Model parameters and interpretation belong in the caption.
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    for suffix in ('.png', '.pdf'):
        fig.savefig(out.with_suffix(suffix), dpi=300, bbox_inches='tight', pad_inches=.04)
    issues = style.label_audit(fig)
    plt.close(fig)
    if issues:
        raise ValueError('uphill figure label audit failed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--title')
    args = parser.parse_args()
    plot(args.directory, args.out, title=args.title)


if __name__ == '__main__':
    main()
