"""Plot a completed three-grid ring study and measured Richardson orders."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from grteclyn_wrapper.optimisation.railgun.evolution_convergence import (
    analyse, load_triplet, RESOLUTIONS,
)

COLOURS = ('#b45309', '#2563eb', '#6d28d9')


def plot(folders, output):
    # The analyser validates source/binary/physics and immutable archive hashes
    # before any panel is drawn. A two-grid figure cannot use this entry point.
    report = analyse(folders)
    records = load_triplet(folders)
    fig, axes = plt.subplots(2, 3, figsize=(15, 9), layout='constrained')
    axes = axes.ravel()
    for index, (label, column) in enumerate((('Hamiltonian', 'L2_Ham_int'),
                                           ('Momentum', 'L2_Mom_int'))):
        for record, colour in zip(records, COLOURS):
            data = record['constraints']; mask = data['time'] <= 2+1e-8
            axes[index].semilogy(data['time'][mask], data[column][mask],
                                label=f"{record['n']}³", color=colour)
        finest = records[-1]['constraints']; mask = finest['time'] <= 2+1e-8
        for order, style in ((2, '--'), (4, ':')):
            axes[index].semilogy(finest['time'][mask], finest[column][mask]*2**order,
                                style, color='.35', linewidth=1,
                                label=f'192³ × 2^{order}')
        axes[index].set(title=f'{label} constraint, L0, r < 8', ylabel='L2 norm')
    times = np.array(report['times'])
    for name, colour in zip(('Ham L0', 'Mom L0'), COLOURS):
        values = np.array([[np.nan if p is None else p for p in row['pair_orders']]
                           for row in report['constraints'][name]])
        for index, style in enumerate(('-', '--')):
            axes[2].plot(times, values[:, index], style, color=colour,
                         label=f'{name}, {RESOLUTIONS[index]}→{RESOLUTIONS[index+1]}')
    axes[2].axhline(4, color='.6', linewidth=.8)
    axes[2].set(title='Measured constraint orders', ylabel='Order p')
    for record, colour in zip(records, COLOURS):
        data = record['matter']; mask = data['time'] <= 2+1e-8
        axes[3].plot(data['time'][mask], data['Q_box'][mask]-data['Q_box'][0],
                     label=f"{record['n']}³", color=colour)
    axes[3].set(title='Finite-box charge change', ylabel='Q(t) − Q(0)')
    rows = report['observables']['Q_box_minus_initial']
    differences = np.array([row['differences'] for row in rows])
    q4 = report['expected_difference_factors']['4']
    axes[4].plot(times, differences[:, 0], 'o-', color=COLOURS[0], label='ΔQ96 − ΔQ128')
    axes[4].plot(times, q4*differences[:, 1], 's--', color=COLOURS[2],
                 label=f'{q4:.4f} × (ΔQ128 − ΔQ192)')
    axes[4].set(title='Signed charge differences: fourth-order test', ylabel='Difference')
    for name, label, colour in (('Q_box_minus_initial', 'Charge change', COLOURS[0]),
                                ('Jz_matter_box', 'Matter angular momentum', COLOURS[1])):
        order = [np.nan if row['order'] is None else row['order']
                 for row in report['observables'][name]]
        axes[5].plot(times, order, 'o-', color=colour, label=label)
    axes[5].axhline(4, color='.6', linewidth=.8)
    axes[5].set(title='Richardson orders from three grids', ylabel='Order p; unresolved points omitted')
    axes[5].set_ylim(0, 12.5)
    for ax in axes:
        ax.set_xlim(0, 2); ax.set_xlabel('Coordinate time'); ax.grid(alpha=.2)
        title = ax.get_title()
        ax.set_title('')
        ax.set_title(title, loc='left', pad=53, fontsize=10)
        ax.legend(loc='lower left', bbox_to_anchor=(0, 1.01), fontsize=8,
                  ncol=2, frameon=False, borderaxespad=0)
    fig.suptitle('Scalar ring ω=0.70: 96³ / 128³ / 192³, box 32\n'
                 'Unperturbed convergence through t=2; long-term stability untested', fontsize=14)
    output = Path(output); output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    fig.savefig(output.with_suffix('.pdf'))
    plt.close(fig)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archives', nargs=3, type=Path)
    parser.add_argument('--out', type=Path,
                        default=Path('results/railgun/figures/ring070-evolution-convergence.png'))
    args = parser.parse_args()
    plot(args.archives, args.out)
