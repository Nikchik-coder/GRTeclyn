"""Accepted single-ring frequency sequence, including refined recovery points."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np


def measurements(root):
    root=Path(root);rows=[]
    old=json.loads((root/'studies/frequency-scan/outcome.json').read_text())
    for r in old['records']:
        if r['accepted']:rows.append(r)
    recovered=json.loads((root/'studies/frequency-073-refined/outcome.json').read_text())
    if not recovered['accepted']:raise ValueError('accepted omega=0.73 recovery required')
    rows.append(dict(recovered['records'][-1],frequency=.73))
    deep=json.loads((root/'studies/frequency-deep/outcome.json').read_text())
    rows.extend(r for r in deep['records'] if r['accepted'])
    return sorted(rows,key=lambda r:-r['frequency'])


def plot(root,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows=measurements(root);freq=[r['frequency'] for r in rows]
    fig,axes=plt.subplots(1,3,figsize=(12,4.8))
    fig.subplots_adjust(left=.075,right=.98,bottom=.24,top=.73,wspace=.38)
    for ax,key,label,colour in zip(axes,('J_volume','shift_norm_over_lapse_max','gtt_max'),
            ('Angular momentum magnitude |J|','Maximum sampled |β| / α',r'Maximum sampled $g_{tt}$'),
            ('#337ab3','#40856b','#d56d35')):
        values=np.array([r[key] for r in rows]);values=abs(values) if key=='J_volume' else values
        ax.plot(freq,values,'o-',color=colour,label=label)
        if key=='gtt_max':ax.axhline(0.,color='.35',ls='--',lw=1,label='Ergoregion threshold')
        ax.set(xlabel='Scalar frequency ω',ylabel=label);ax.invert_xaxis();ax.grid(alpha=.2)
        ax.legend(loc='lower center',bbox_to_anchor=(.5,1.02),frameon=False,fontsize=10)
    fig.suptitle('Single-ring branch · three-grid accepted stationary points',y=.98,fontsize=15)
    fig.text(.5,.065,'Dragging continues to grow while |J| turns over; sampled metrics stay below the ergoregion threshold.\n'
        'ω = 0.67 failed Newton and is excluded. No physical maximum or stability claim.',ha='center',fontsize=10)
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,dpi=180);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('root',type=Path)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();plot(args.root,args.out)


if __name__=='__main__':main()
