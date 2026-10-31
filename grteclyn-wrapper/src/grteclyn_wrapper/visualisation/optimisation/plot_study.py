"""Rebuild comparison plots from a study's persisted diagnostics."""
import json
from pathlib import Path


def plot_comparison(directory):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    directory=Path(directory)
    data=json.loads((directory/'outcome.json').read_text())
    rows=[json.loads(line) for line in (directory/'evaluations.jsonl').read_text().splitlines()]
    ref=data['reference']
    fig,ax=plt.subplots(1,2,figsize=(9,3.5),constrained_layout=True)
    for ok,label,color in ((False,'Rejected','#a6a6a6'),(True,'Provisional','#2374ab')):
        subset=[r for r in rows if (r.get('verdict')=='PASS')==ok and
                r.get('X_full') is not None and r.get('tidal_peak') is not None]
        ax[0].scatter([r['tidal_peak']/ref['tidal_peak'] for r in subset],
                      [r['X_full']/ref['X_full'] for r in subset],c=color,label=label,s=15)
        ax[1].scatter([r.get('E_b_over_R_A',0.) for r in subset],
                      [r['X_full']/ref['X_full'] for r in subset],c=color,label=label,s=15)
    for a,x in zip(ax,[1.,0.]): a.scatter([x],[1.],marker='x',c='black',label='Massless reference')
    if data.get('winner'):
        r=data['winner']
        for a,x in zip(ax,[r['tidal_peak']/ref['tidal_peak'],r.get('E_b_over_R_A',0.)]):
            a.scatter([x],[r['X_full']/ref['X_full']],marker='*',s=90,c='#aa3322',label='Refined candidate')
    yvals=[1.]+[r['X_full']/ref['X_full'] for r in rows if r.get('X_full') is not None]
    xvals=[1.]+[r['tidal_peak']/ref['tidal_peak'] for r in rows if r.get('tidal_peak') is not None]
    evals=[0.]+[r['E_b_over_R_A'] for r in rows if r.get('E_b_over_R_A') is not None]
    ax[0].set_xlim(-.03*max(xvals),max(xvals)*1.1)
    ax[1].set_xlim(-.03*max(.1,max(evals)),max(.1,max(evals)*1.1))
    for a in ax:
        a.set_ylim(0.,max(yvals)*1.1)
        a.ticklabel_format(style='plain',useOffset=False)
        a.set_ylabel('Full phantom integral / reference')
        a.legend(loc='lower left',bbox_to_anchor=(0,1),fontsize=7,ncol=2)
    ax[0].set_xlabel('Peak tidal eigenvalue / reference')
    ax[1].set_xlabel('Ordinary energy / throat areal radius')
    fig.savefig(directory/'comparison.png',dpi=180)
    fig.savefig(directory/'comparison.pdf')
    plt.close(fig)
