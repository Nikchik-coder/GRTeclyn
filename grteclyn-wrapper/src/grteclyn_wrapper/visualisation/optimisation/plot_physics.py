"""Mechanism profiles from archived stationary fields."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

from grteclyn_wrapper.core.config import resolve_repo_root
from grteclyn_wrapper.visualisation.wormhole_merger import style
from .palette import BLUE, INK

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


def main():
    style.prd(8.)
    for name, maker in [('mechanism_d21', profiles)]:
        fig = maker()
        print(style.save(fig, OUT/name))
        problems = style.label_audit(fig)
        print(name, 'label audit:', problems or 'clean')
        plt.close(fig)
        if problems:
            raise RuntimeError(problems)


if __name__ == '__main__':
    main()
