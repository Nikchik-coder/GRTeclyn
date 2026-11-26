"""Rebuild ring-frame and initial constraint comparisons from frozen slices."""
from pathlib import Path
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patches import Circle, Rectangle
import numpy as np

ROOT = Path('results/railgun')
DATA = ROOT/'reports/ergoregion372-startup'
OUT = ROOT/'figures/evolution'


def read_slice(path, centre):
    with np.load(path, allow_pickle=False) as z:
        return z['arr'].copy(), z['extent'].copy()-centre, float(z['time'])


def decorate(ax, limit):
    ax.set(xlim=(-limit, limit), ylim=(-limit, limit), aspect='equal',
           xlabel='x from centre', ylabel='y from centre')
    ax.tick_params(labelsize=9)


def current():
    fig, axes = plt.subplots(2, 3, figsize=(12.5, 8.4))
    fig.subplots_adjust(left=.065, right=.97, top=.84, bottom=.17, wspace=.3, hspace=.40)
    images = []
    for row, n in enumerate((96, 192)):
        ring, extent, t = read_slice(DATA/f'ring-t0-n{n}.npz', 32)
        with np.load(DATA/f'constraints-t0-n{n}.npz', allow_pickle=False) as z:
            ham = abs(z['Ham'])
            mom = np.sqrt(z['Mom1']**2+z['Mom2']**2+z['Mom3']**2)
            edge = z['level_bounds'][6, 1]
        arrays = (ring/ring.max(), ham, mom)
        for col, (ax, a) in enumerate(zip(axes[row], arrays)):
            kw = dict(vmin=0, vmax=1, cmap='Blues') if col == 0 else dict(
                norm=LogNorm(1e-8, 1e-3 if col == 1 else 2e-4), cmap='magma')
            image = ax.imshow(a, origin='lower', extent=extent if col == 0 else (-1, 1, -1, 1),
                              interpolation='nearest', **kw)
            if row == 0:
                images.append(image)
            ax.add_patch(Circle((0, 0), .2335923253, fill=False, ec='#1f9eaa', lw=1, ls=':'))
            ax.add_patch(Rectangle((-edge, -edge), 2*edge, 2*edge,
                                   fill=False, ec='#2aa9d2', lw=1.4, ls='--'))
            decorate(ax, .65)
        axes[row, 0].set_title(f'N={n} · finest spacing {64/(n*64):.5f}', fontsize=11, pad=8)
        axes[row, 1].set_title('Hamiltonian error |H|', fontsize=11, pad=8)
        axes[row, 2].set_title('Momentum error magnitude', fontsize=11, pad=8)
    for col, label in enumerate(('Scalar activity / its peak', '|H|', 'Momentum magnitude')):
        fig.colorbar(images[col], ax=list(axes[:, col]), orientation='horizontal',
                     fraction=.035, pad=.12, label=label)
    fig.suptitle('Initial ergoregion ring and its constraint errors', fontsize=17, weight='bold', y=.975)
    fig.text(.5, .922, 'Both rows: t=0, outer box L=64, six refinement levels. N128 has not started.',
             ha='center', fontsize=11)
    fig.text(.5, .888, 'Dashed square: finest-grid edge. Dotted circle: radius of peak matter density.',
             ha='center', fontsize=10, color='#39546a')
    fig.text(.5, .036, 'Inside r<0.3 in this plane, halving the spacing reduces Ham and Mom by about 16×.\n'
             'The larger errors at grid transitions prevent a full evolution-convergence claim.',
             ha='center', fontsize=10)
    fig.savefig(OUT/'ergoregion372-grid-and-constraints.png', dpi=190)
    plt.close(fig)


def earlier():
    cases = [(96, 300), (128, 400), (192, 600), (192, None)]
    fig, axes = plt.subplots(2, 2, figsize=(10, 9))
    fig.subplots_adjust(left=.08, right=.86, bottom=.09, top=.85, hspace=.28, wspace=.24)
    for ax, (n, step) in zip(axes.flat, cases):
        path = (ROOT/f'studies/evolution-070-n{n}/slices/scalar_activity_{step:04d}.npz'
                if step is not None else DATA/'earlier-ring070-n192-t50.npz')
        a, extent, t = read_slice(path, 16)
        image = ax.imshow(a/a.max(), origin='lower', extent=extent, vmin=0, vmax=1,
                          cmap='Blues', interpolation='nearest')
        decorate(ax, 3)
        ax.set_title(f'N={n} · t={t:.0f}'+(' · longer run' if step is None else ''), fontsize=12)
    cax = fig.add_axes([.89, .21, .02, .52])
    fig.colorbar(image, cax=cax, label='Scalar activity / its peak')
    fig.suptitle('Earlier ω=0.70 ring: frames from every evolution', fontsize=16, weight='bold', y=.965)
    fig.text(.5, .915, 'N96 / N128 / N192 at t=2 form the completed Richardson study.', ha='center', fontsize=11)
    fig.text(.5, .883, 'The fourth panel is the separate N192 run to t=50 in the same L=32 box.',
             ha='center', fontsize=10)
    fig.text(.5, .025, 'Original cell values are shown without image smoothing; each panel is normalized to its own peak.',
             ha='center', fontsize=10)
    fig.savefig(OUT/'ring070-all-evolution-frames.png', dpi=180)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
    current()
    earlier()
    report = json.loads((DATA/'constraints.json').read_text())
    print(json.dumps(report['plane_core_orders']))


if __name__ == '__main__':
    main()
