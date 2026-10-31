"""Classical spin curves and the article's explicitly selected candidates."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from scipy.interpolate import PchipInterpolator
from grteclyn_wrapper.visualisation.spinning_wormhole.plot_spin_trends import FAMILIES, family
from grteclyn_wrapper.visualisation.spinning_wormhole.solutions import load as load_solutions
from grteclyn_wrapper.visualisation.wormhole_merger import style
from .palette import BLUE, LIGHT_BLUE, INK
from .paper_results import REPO, load_models
OUT = REPO / 'results/optimisation/figures'
REFINED = {
    'D0': 'validation/2026-10-30-alternatives/d0/009_e0211/handoff.npz',
    'D30': 'completed/2026-10-31/d30/fam_a_r1_0005_cma_resolution_20261030_best_clean.npz',
    'D40': 'completed/2026-10-31/d40/fam_a_r1_0008_cma_resolution_20261031_best_clean.npz',
    'D46': 'completed/2026-10-31/d46/fam_a_r1_0010_cma_resolution_20261031_r2_best_clean.npz',
}


def refined_models():
    """Selected fine-grid fields, plotted at their massless reference spin."""
    rows = [r for r in load_models() if r['stage'] == 'fine']
    for model, source in REFINED.items():
        with np.load(REPO / 'results/optimisation' / source) as z:
            meta = json.loads(str(z['meta']))
        if meta['verdict'] != 'PASS' or (meta['nx'], meta['ny']) != (210, 42):
            raise ValueError(f'{model}: expected a passing 210x42 background')
        if model != 'D0' and not meta.get('resolution_validated'):
            raise ValueError(f'{model}: finalist refinement is missing')
        reference = REPO / 'results/spinningwormhole/solutions/fam_a_r1' / meta['member']
        ve = 0.0 if meta['J'] == 0 else json.loads(reference.read_text())['observables']['v_e']
        rows.append(dict(model=model, ve=ve, X=meta['X']))
    return sorted(rows, key=lambda r: r['ve'])

def potential_points():
    """One selected candidate per reference spin; refined fields take priority."""
    refined = refined_models()
    names = {r['model'] for r in refined}
    selected = [dict(r, refined=False) for r in load_models()
                if r['stage'] == 'search' and r['model'] not in names]
    selected.extend(dict(r, family='Drainhole', refined=True) for r in refined)
    return selected


def trend_guide(v, y):
    """Shape-preserving interpolation through samples, without extrapolation."""
    return PchipInterpolator(v, y, extrapolate=False)


def plot(out=OUT):
    style.prd(8.)
    rows = load_solutions()
    fams = [family(rows, eta0, gamma) for eta0, gamma, *_ in FAMILIES]
    fig, ax = plt.subplots(figsize=(3.4, 2.25), layout='constrained')
    entries = []
    selected = potential_points()
    for fam, (*_, name, ls) in zip(fams, FAMILIES):
        drainhole = name == 'drainhole'
        label, colour, marker = ('D', BLUE, 's') if drainhole else ('S', LIGHT_BLUE, 'o')
        v = np.r_[0., fam['v']]
        y = np.r_[1., fam['Xrel']]
        good = np.isfinite(y)
        vx = np.linspace(v[good].min(), v[good].max(), 300)
        classical, = ax.plot(vx, trend_guide(v[good], y[good])(vx),
                             color=INK, ls=ls, lw=.8)
        entries.append((classical, label + r': $\mathcal{V}=0$'))

        points = sorted((r for r in selected if r['family'].lower() == name),
                        key=lambda r: r['ve'])
        v = np.array([r['ve'] for r in points])
        y = np.array([r['X'] / fam['static']['X'] for r in points])
        guide = trend_guide(v, y)
        vx = np.linspace(v.min(), v.max(), 200)
        ax.plot(vx, guide(vx), color=colour, ls=ls, lw=1.05, zorder=2)
        for r, x, bill in zip(points, v, y):
            ax.plot(x, bill, marker=marker, ms=2.8, ls='none',
                    mfc=colour if r['refined'] else 'white',
                    mec=colour, mew=.7, zorder=3)
        entries.append((Line2D([], [], color=colour, ls=ls, lw=1.05,
                              marker=marker, ms=2.8, mfc='white', mec=colour),
                        label + ': potential'))
        print(f'{label}: shape-preserving guide through {len(points)} points; '
              f'no extrapolation beyond [{v.min():.6g}, {v.max():.6g}]')
    ax.set(xlabel=r'$v_e$', ylabel=r'$X/X_{\rm static}$',
           xlim=(-.035, 1.), ylim=(0, 1.035))
    ax.set_xticks(np.arange(0., 1.01, .2))
    ax.set_yticks(np.arange(0., 1.01, .2))
    style.legend_top(ax, entries, ncol=2, fontsize=6.8, mode=None,
                     loc='lower center', bbox_to_anchor=(.5, 1.005),
                     handlelength=1.8, handletextpad=.45, columnspacing=1.6,
                     labelspacing=.25, borderpad=.2)
    problems = style.label_audit(fig)
    print(style.save(fig, out / 'exotic_spin'))
    plt.close(fig)
    if problems:
        raise SystemExit(problems)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,default=OUT)
    plot(ap.parse_args().out)
if __name__=='__main__':main()
