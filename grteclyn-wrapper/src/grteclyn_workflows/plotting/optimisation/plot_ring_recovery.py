"""Compare independent residuals before and after a ring resolution recovery."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np


def plot(coarse,recovery,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    result=json.loads((Path(recovery)/'outcome.json').read_text())
    rows=[json.loads(Path(coarse).read_text()),*result['records']]
    if len({tuple(r['grid']) for r in rows})!=len(rows):
        raise ValueError('distinct coarse and recovery grids required')
    rows.sort(key=lambda r:r['grid'][0]);x=np.arange(len(rows))
    fig,axes=plt.subplots(1,2,figsize=(11,4.8))
    fig.subplots_adjust(left=.08,right=.98,bottom=.23,top=.74,wspace=.28)
    specs=[(('constraint_c','constraint_19'),('Unimposed C','Unimposed constraint 19')),
           (('offgrid_einstein_max','offgrid_kg_max'),('Off-grid Einstein','Off-grid Klein–Gordon'))]
    for ax,(keys,labels) in zip(axes,specs):
        for key,label,colour in zip(keys,labels,('#337ab3','#d56d35')):
            values=[r[key] for r in rows]
            if not np.isfinite(values).all() or min(values)<=0:
                raise ValueError('finite positive residual measurements required')
            ax.semilogy(x,values,'o-',color=colour,label=label)
        ax.axhline(1e-8,color='.35',ls='--',lw=1,label='Acceptance limit')
        ax.set_xticks(x,[f"{r['grid'][0]}×{r['grid'][1]}" for r in rows])
        ax.set(xlabel='Radial × angular grid',ylabel='Maximum absolute residual')
        ax.grid(alpha=.2);ax.legend(loc='lower center',bbox_to_anchor=(.5,1.015),ncol=1,frameon=False,fontsize=10)
    fig.suptitle('ω = 0.73 · independent checks under resolution refinement',y=.98,fontsize=15)
    conclusion='All three recovery grids and observable convergence pass.' if result['accepted'] else 'Recovery rejected; no accepted background exported.'
    fig.text(.5,.075,conclusion+'\nThe original 72×10 rejection is retained; every acceptance limit stays unchanged.',ha='center',fontsize=10)
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,dpi=180);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('coarse',type=Path);parser.add_argument('recovery',type=Path)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    plot(args.coarse,args.recovery,args.out)


if __name__=='__main__':main()
