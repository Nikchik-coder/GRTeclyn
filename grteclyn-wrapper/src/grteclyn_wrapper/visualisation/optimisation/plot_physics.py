"""Mechanism profiles and physical trade-offs from archived stationary fields."""
import csv

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.lines import Line2D
import numpy as np

from grteclyn_wrapper.core.config import resolve_repo_root
from grteclyn_wrapper.visualisation.wormhole_merger import style
from .palette import BLUE, INK, GREY

ROOT = resolve_repo_root()
DATA = ROOT/'results/optimisation/physics'
OUT = ROOT/'results/optimisation/figures'


def key(ax):
    style.legend_top(ax, [(Line2D([], [], color=INK, lw=1.3), r'$V=0$'),
                         (Line2D([], [], color=BLUE, lw=1.3), 'Optimised')],
                     ncol=2, fontsize=7, columnspacing=1.)


def profiles(model='D21'):
    fig, axes = plt.subplots(2, 2, figsize=(7.05, 4.15), layout='constrained')
    for kind, color in [('classical', INK), ('potential', BLUE)]:
        with np.load(DATA/f'{model}_{kind}_profiles.npz') as p:
            x = p['ell_over_Re']
            values = [abs(p['grad_r_Re'][:, 0]), p['bill_per_ell'],
                      p['areal_radius_over_Re'], 1/p['lapse'][:, 0]]
            for ax, val in zip(axes.flat, values):
                ax.plot(x, val, color=color, lw=1.35)
    labels = [r'$R_e |\nabla_{\hat r}\psi|$', r'$dX/d(\ell/R_e)$',
              r'$R_A(\ell)/R_e$', r'$E_{\rm local}/E_{+\infty}$']
    titles = ['(a) Scalar gradient', '(b) Exoticity density',
              '(c) Areal-radius profile', '(d) Photon energy']
    for i, (ax, label, title) in enumerate(zip(axes.flat, labels, titles)):
        ax.set(xlim=(-3, 3) if i < 2 else (-10, 10), xlabel=r'Proper distance $\ell/R_e$', ylabel=label)
        key(ax)
        ax.set_title(title, fontsize=8, loc='left', pad=22)
    return fig


def tradeoffs():
    with (DATA/'summary.tsv').open() as f:
        rows = {(r['model'], r['kind']): r for r in csv.DictReader(f, delimiter='\t')}
    models = ['D0', 'D21', 'D30']
    metrics = [
        ('X', '(a) Total exoticity'),
        ('radial_nec_peak_Re2', '(b) Peak radial NEC violation'),
        ('bill_width90_over_Re', '(c) Width containing 90% of bill'),
        ('nec_ray_equator_Re', '(d) Integrated null NEC'),
        ('tidal_v05_Re2', r'(e) Peak tides, $v=0.5$'),
        ('transit_equator_over_Re', '(f) Light travel time'),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(7.05, 3.9), layout='constrained')
    for ax, (metric, title) in zip(axes.flat, metrics):
        ratio = [float(rows[m, 'potential'][metric])/float(rows[m, 'classical'][metric]) for m in models]
        ax.axhline(1, color=GREY, ls='--', lw=.9)
        ax.scatter(range(3), ratio, s=30, color=BLUE, zorder=3)
        ax.set(xticks=range(3), xticklabels=models, xlim=(-.4, 2.4), ylabel=r'Ratio to $V=0$')
        if metric == 'bill_width90_over_Re':
            ax.set_yscale('log'); ax.set_ylim(.01, 1.4)
        else:
            ax.set_ylim(0, max(1.2, max(ratio)*1.15))
        style.legend_top(ax, [(Line2D([], [], marker='o', ls='none', color=BLUE, ms=4), 'Potential'),
                              (Line2D([], [], ls='--', color=GREY, lw=.9), r'$V=0$')],
                         ncol=2, fontsize=6.5, columnspacing=.6, handlelength=1.2,
                         borderpad=.45)
        ax.set_title(title, fontsize=7.8, loc='left', pad=22)
    return fig


def nec_map():
    fig, axes = plt.subplots(1, 2, figsize=(7.05, 2.45), layout='constrained', sharey=True)
    for ax, kind, title in zip(axes, ['classical', 'potential'], [r'(a) D21, $V=0$', '(b) D21, optimised']):
        with np.load(DATA/f'D21_{kind}_profiles.npz') as p:
            mesh = ax.pcolormesh(p['ell_over_Re'], p['mu'], p['nec_max_Re2'].T,
                                 cmap='Blues', norm=LogNorm(vmin=1e-5, vmax=.4), shading='auto', rasterized=True)
        ax.set(xlim=(-2, 2), xlabel=r'Equatorial proper distance $\ell/R_e$')
        ax.set_title(title, loc='left', fontsize=8)
    axes[0].set_ylabel(r'$\cos\theta$ (equator $0$, axis $1$)')
    cb = fig.colorbar(mesh, ax=axes, pad=.025, fraction=.04)
    cb.set_label(r'$R_e^2 |\mathrm{NEC}|_{\max}$')
    return fig


def main():
    style.prd(8.)
    for name, maker in [('mechanism_d21', profiles), ('stationary_tradeoffs', tradeoffs),
                        ('nec_distribution_d21', nec_map)]:
        fig = maker()
        print(style.save(fig, OUT/name))
        problems = style.label_audit(fig)
        print(name, 'label audit:', problems or 'clean')
        plt.close(fig)
        if problems:
            raise RuntimeError(problems)


if __name__ == '__main__':
    main()
