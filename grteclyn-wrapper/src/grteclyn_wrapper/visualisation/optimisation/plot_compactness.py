"""Validated points of a bounded compactness continuation, including partial scans."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np


def plot(directory,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    result=json.loads((Path(directory)/'outcome.json').read_text())
    rows=[r for r in result['records'] if r.get('accepted')]
    if not rows:raise ValueError('at least one three-grid accepted point required')
    a=np.array([r['amplitude'] for r in rows])
    fig,axes=plt.subplots(1,3,figsize=(12,4.4));fig.subplots_adjust(left=.07,right=.98,bottom=.23,top=.74,wspace=.4)
    for ax,key,label,colour in zip(axes,('frequency','lapse_min','shift_norm_over_lapse_max'),
            ('Scalar frequency ω','Minimum sampled lapse α','Maximum sampled |β| / α'),
            ('#337ab3','#d56d35','#40856b')):
        ax.plot(a,[r[key] for r in rows],'o-',color=colour,label=label)
        ax.set(xlabel='Matter amplitude pin',ylabel=label)
        ax.legend(loc='lower center',bbox_to_anchor=(.5,1.02),frameon=False);ax.grid(alpha=.2)
    if max(r['shift_norm_over_lapse_max'] for r in rows)>.3:
        axes[-1].axhline(1.,color='.3',ls='--',lw=1.)
    fig.suptitle('Compactness continuation · independently validated stationary points',y=.98,fontsize=14)
    stopping='Scan completed' if result['scan_completed'] else 'Scan stopped at a rejected point; only passing points shown'
    fig.text(.5,.075,stopping+'.\nA sampled ergoregion is a metric diagnostic; stability and particle selection require separate tests.',
             ha='center',fontsize=10)
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,dpi=180);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('directory',type=Path)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();plot(args.directory,args.out)


if __name__=='__main__':main()
