"""Plot a completed three-grid ring study and measured Richardson orders."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

from grteclyn_wrapper.optimisation.railgun.evolution_convergence import (
    analyse, load_triplet, RESOLUTIONS,
)
from grteclyn_wrapper.visualisation.wormhole_merger import style
from .palette import BLUE, INK, GREY, RESOLUTIONS as RESOLUTION_COLOURS


def plot(folders, output):
    # Validate archive checksums, physics and completion before drawing.
    report = analyse(folders)
    records = load_triplet(folders)
    style.prd(8.)
    plt.rcParams['pdf.fonttype'] = 42
    fig, grid = plt.subplots(2, 3, figsize=(7.05, 3.55), layout='constrained')
    fig.get_layout_engine().set(w_pad=.035, h_pad=.025, wspace=.025, hspace=.035)
    axes = grid.ravel()
    members = [dict(color=c, lw=1.1, ls=ls)
               for c, ls in zip(RESOLUTION_COLOURS, ('-', '--', '-.'))]
    brackets = [dict(color=GREY, lw=.85, ls=ls) for ls in ('--', ':')]
    pairs = [dict(color=GREY, ls=ls, marker=marker, ms=2.3, lw=.9)
             for ls, marker in (('-', 'o'), ('--', 's'))]
    fig.legend([Line2D([], [], **f) for f in members+brackets+pairs],
               [rf'$N={n}$' for n in RESOLUTIONS]
               + [r'$N=192\times2^2$', r'$N=192\times2^4$',
                  r'$p_{96\to128}$', r'$p_{128\to192}$'],
               loc='outside upper center', ncol=7, frameon=False,
               fontsize=6.6, handlelength=1.8, columnspacing=1.1)

    def key(ax, ncol=1):
        ax.legend(loc='lower left', bbox_to_anchor=(0, 1.015),
                  borderaxespad=0, frameon=False, fontsize=6.5,
                  handlelength=1.7, handletextpad=.4, columnspacing=.8,
                  labelspacing=.15, ncol=ncol)

    for index, column in enumerate(('L2_Ham_int', 'L2_Mom_int')):
        for record, fmt in zip(records, members):
            data = record['constraints']; mask = data['time'] <= 2+1e-8
            axes[index].semilogy(data['time'][mask], data[column][mask], **fmt)
        finest = records[-1]['constraints']; mask = finest['time'] <= 2+1e-8
        for order, fmt in zip((2, 4), brackets):
            axes[index].semilogy(finest['time'][mask], finest[column][mask]*2**order, **fmt)
        axes[index].set_ylabel((r'$\|\mathcal{H}\|_2$', r'$\|\mathcal{M}\|_2$')[index])

    times = np.array(report['times'])
    for name, symbol, colour in (('Ham L0', r'\mathcal{H}', INK),
                                 ('Mom L0', r'\mathcal{M}', BLUE)):
        values = np.array([[np.nan if p is None else p for p in row['pair_orders']]
                           for row in report['constraints'][name]])
        for index, ls in enumerate(('-', '--')):
            axes[2].plot(times, values[:, index], ls=ls, color=colour, lw=1.1,
                         marker=('o', 's')[index], ms=2.3,
                         label=rf'${symbol}$' if index == 0 else '_nolegend_')
    axes[2].axhline(4, color=GREY, lw=.7, zorder=0)
    axes[2].set_ylabel(r'$p$')
    key(axes[2], ncol=2)

    for record, fmt in zip(records, members):
        data = record['matter']; mask = data['time'] <= 2+1e-8
        axes[3].plot(data['time'][mask], 1e3*(data['Q_box'][mask]-data['Q_box'][0]), **fmt)
    axes[3].set_ylabel(r'$10^3\Delta Q$')
    differences = np.array([row['differences']
                            for row in report['observables']['Q_box_minus_initial']])
    q4 = report['expected_difference_factors']['4']
    axes[4].plot(times, 1e3*differences[:, 0], 'o-', color=INK, lw=1.1, ms=2.8,
                 label=r'$D_{96,128}$')
    axes[4].plot(times, 1e3*q4*differences[:, 1], 's--', color=BLUE, lw=1.1, ms=2.8,
                 label=rf'${q4:.3f}D_{{128,192}}$')
    axes[4].set_ylabel(r'$10^3\delta(\Delta Q)$')
    key(axes[4], ncol=2)
    for name, label, colour, marker, ls in (
            ('Q_box_minus_initial', r'$\Delta Q$', INK, 'o', '-'),
            ('Jz_matter_box', r'$J_z$', BLUE, 's', '--')):
        order = [np.nan if row['order'] is None else row['order']
                 for row in report['observables'][name]]
        axes[5].plot(times, order, color=colour, marker=marker, ls=ls,
                     lw=1.1, ms=2.8, label=label)
    axes[5].axhline(4, color=GREY, lw=.7, zorder=0)
    axes[5].set_ylabel(r'$p$')
    key(axes[5], ncol=2)
    shown = [4.] + [row['order']
        for name in ('Q_box_minus_initial', 'Jz_matter_box')
        for row in report['observables'][name] if row['order'] is not None]
    axes[5].set_ylim(max(0, np.floor(min(shown)*2)/2-.25), np.ceil(max(shown)*2)/2+.25)
    titles = ('(a) Hamiltonian, $r<8$', '(b) Momentum, $r<8$',
              '(c) Constraint orders', '(d) Charge change',
              '(e) Charge differences', '(f) Richardson orders')
    for ax, title in zip(axes, titles):
        ax.set(xlim=(0, 2), xlabel=r'$t$', xticks=[0, .5, 1, 1.5, 2])
        ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:g}'))
        ax.set_title(title, loc='left', fontsize=8., pad=14)
    output = Path(output); output.parent.mkdir(parents=True, exist_ok=True)
    for suffix in ('.png', '.pdf'):
        fig.savefig(output.with_suffix(suffix), dpi=300, bbox_inches='tight', pad_inches=.04)
    issues = style.label_audit(fig)
    plt.close(fig)
    if issues:
        raise ValueError('convergence figure label audit failed')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archives', nargs=3, type=Path)
    parser.add_argument('--out', type=Path,
                        default=Path('results/railgun/figures/evolution/ring070-evolution-convergence.png'))
    args = parser.parse_args()
    plot(args.archives, args.out)
