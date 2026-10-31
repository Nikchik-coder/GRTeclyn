"""Compare measured throat-radius histories and threshold times at N=128.

Thresholds describe contraction, not horizon formation or a mode growth rate.
Each radius is normalized by its own initial value; time is not shifted.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

from .plot_instability_curve import CLASSICAL, POTENTIAL, REPO, RUNS, FIGURES, table_meta
from .palette import BLUE, INK, GREY
from grteclyn_wrapper.visualisation.wormhole_merger import style

TABLE = REPO/'results/optimisation/article/contraction_delay.tsv'
ROOT = REPO/'results/optimisation/completed/2026-10-31'
POTENTIALS = {
    'D0': ROOT/'d0/small_data/throat_spheres.dat.gz',
    'D21': POTENTIAL/'small_data/throat_spheres.dat.gz',
    'D30': ROOT/'d30/evolution/small_data/throat_spheres.dat.gz',
    'D40': ROOT/'d40/evolution/small_data/throat_spheres.dat',
    'D46': ROOT/'d46/evolution/small_data/throat_spheres.dat.gz',
}


def crossing(t, radius, fraction):
    """First threshold crossing, linearly interpolated between saved samples."""
    hit = np.flatnonzero(radius <= 1-fraction)
    if not len(hit):
        return None
    i = int(hit[0])
    if i == 0:
        return float(t[0])
    w = (radius[i-1]-(1-fraction))/(radius[i-1]-radius[i])
    return float(t[i-1]+w*(t[i]-t[i-1]))


def load():
    histories, rows = {}, []
    for model, potential in POTENTIALS.items():
        spec = next(s for s in RUNS if s['label'] == model)
        paths = {'classical': CLASSICAL/spec['run']/'throat_spheres.dat',
                 'potential': potential}
        histories[model] = {}
        for branch, path in paths.items():
            data = np.loadtxt(path)
            # Restrict the D46 potential analysis to the pre-runaway interval.
            # Its classical reference briefly contracts before expanding.
            if model == 'D46' and branch == 'potential':
                data = data[data[:, 0] <= 100]
            t, r = data[:, 0], data[:, 2]
            assert np.isfinite(t).all()
            # The spherical throat finder loses the minimum late in the
            # classical collapse. End there; never bridge missing radii.
            missing = np.flatnonzero(~np.isfinite(r))
            if len(missing):
                end = int(missing[0])
                assert end > 0 and not np.isfinite(r[end:]).any()
                t, r = t[:end], r[:end]
            assert (np.diff(t) > 0).all() and (r > 0).all()
            r = r/r[0]
            histories[model][branch] = (t, r)
            for deficit in (.002, .01, .02):
                rows.append(dict(model=model, branch=branch, deficit=deficit,
                                 time=crossing(t, r, deficit),
                                 source=str(path.relative_to(REPO))))
    return histories, rows


def draw(histories):
    style.prd(8.)
    fig, ax = plt.subplots(figsize=(3.4, 2.3), layout='constrained')
    models = list(histories)
    xs = [table_meta(next(s for s in RUNS if s['label'] == model)['table'])[1]
          for model in models]
    measured = {}
    for branch in ('classical', 'potential'):
        measured[branch] = [crossing(*histories[m][branch], .01) for m in models]
        assert all(t is not None for t in measured[branch])
    for x, early, late in zip(xs, measured['classical'], measured['potential']):
        ax.plot([x, x], [early, late], color=GREY, lw=.7, alpha=.6, zorder=1)
    for branch, color, marker in [('classical', INK, 'o'),
                                  ('potential', BLUE, 's')]:
        ax.plot(xs, measured[branch], color=color, lw=.9, marker=marker,
                ms=4.1, mec=color, mew=.9,
                mfc='white' if branch == 'potential' else color, zorder=3)
    ax.set(xlim=(-1.5, xs[-1]+1.8), ylim=(35, 103),
           xlabel='Reference model', ylabel=r'Time to $1\%$ contraction')
    ax.set_xticks(xs, models)
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    style.legend_top(ax, [
        (Line2D([], [], color=INK, marker='o', lw=.9, ms=4), r'$V=0$'),
        (Line2D([], [], color=BLUE, marker='s', mfc='white',
                lw=.9, ms=4), 'With potential'),
    ], ncol=2, fontsize=7, columnspacing=1., borderpad=.5)
    return fig


def main():
    histories, rows = load()
    fig = draw(histories)
    print(style.save(fig, FIGURES/'contraction_delay'))
    issues = style.label_audit(fig)
    print('label audit:', issues or 'clean')
    plt.close(fig)
    with TABLE.open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t',
                                lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        if row['deficit'] == .01:
            print(row['model'], row['branch'], row['time'])
    return bool(issues)


if __name__ == '__main__':
    raise SystemExit(main())
