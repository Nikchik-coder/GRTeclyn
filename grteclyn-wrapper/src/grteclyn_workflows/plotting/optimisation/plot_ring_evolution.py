"""Rebuild the two-grid scalar-ring pilot figure from its portable archives."""
from __future__ import annotations
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def table(path):
    for line in path.read_text().splitlines():
        if line.startswith('#'):
            header = line.lstrip('#').split()
        elif line.strip():
            break
    values = np.loadtxt(path, ndmin=2)
    return dict(zip(header, values.T))


def plot(coarse, fine, output):
    fig, axes = plt.subplots(2, 2, figsize=(10, 8), layout='constrained')
    slices = []
    for step in (0, 400):
        with np.load(fine/f'slices/scalar_activity_{step:04d}.npz', allow_pickle=False) as data:
            slices.append((data['arr'].copy(), data['extent'].copy()-16., float(data['time'])))
    vmax = max(float(np.max(item[0])) for item in slices)
    for ax, (array, extent, time) in zip(axes[0], slices):
        image = ax.imshow(array, origin='lower', extent=extent, cmap='viridis', vmin=0, vmax=vmax)
        ax.set(title=f'128³ Cartesian grid, t={time:g}', xlabel='x − centre', ylabel='y − centre')
        ax.set_xlim(-4, 4); ax.set_ylim(-4, 4)
    fig.colorbar(image, ax=axes[0].tolist(), label='Scalar activity (one shared scale)', shrink=.9)
    for folder, label, colour in ((coarse, '96³', '#d97706'), (fine, '128³', '#2563eb')):
        charge = table(folder/'data/complex_scalar_diagnostics.dat')
        constraints = table(folder/'data/constraint_norms.dat')
        use = charge['time'] <= 2+1e-10
        axes[1, 0].plot(charge['time'][use],
            100*abs(charge['Q_box'][use]/charge['Q_box'][0]-1), color=colour, label=label)
        use = constraints['time'] <= 2+1e-10
        axes[1, 1].plot(constraints['time'][use], constraints['L2_Ham_int'][use],
                        color=colour, label=label)
    axes[1, 0].set(title='Finite-box charge drift', xlabel='Coordinate time', ylabel='|Q/Q(0) − 1| [%]')
    axes[1, 1].set(title='Interior Hamiltonian constraint, r < 8',
                   xlabel='Coordinate time', ylabel='L2 residual')
    for ax in axes[1]:
        ax.set_xlim(0, 2); ax.grid(alpha=.2)
        ax.set_title(ax.get_title(), pad=32)
        ax.legend(loc='lower center', bbox_to_anchor=(.5, 1.01), ncol=2, frameon=False)
    fig.suptitle('First 3+1 evolution pilots: scalar ring ω = 0.70\n'
                 'Unperturbed runs through t=2; long-term stability untested', fontsize=13)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--coarse', type=Path, default=Path('results/railgun/studies/evolution-070-n96'))
    parser.add_argument('--fine', type=Path, default=Path('results/railgun/studies/evolution-070-n128'))
    parser.add_argument('--out', type=Path, default=Path('results/railgun/figures/evolution/ring070-evolution-pilot.png'))
    args = parser.parse_args()
    plot(args.coarse, args.fine, args.out)
