"""Actual finite uphill tracks, with a zoom on the endpoint/turnaround split."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np


def plot(directory,out,*,title=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    directory=Path(directory);result=json.loads((directory/'outcome.json').read_text())
    if not result.get('accepted'):raise ValueError('accepted uphill integration study required')
    regime='requested_offset'
    if result['selection_regimes'] and regime not in result['selection_regimes']:regime=result['selection_regimes'][0]
    controls=result['records'][regime+'_rk1']['controls']
    manifest=json.loads((directory/'manifest.json').read_text())
    config=manifest['config']
    if 'target_z' not in config:
        config=json.loads((directory/'original/manifest.json').read_text())['config']
    target=config['target_z']
    fig,(overview,zoom)=plt.subplots(1,2,figsize=(11,4.8));fig.subplots_adjust(left=.09,right=.98,bottom=.22,top=.74,wspace=.3)
    curves=[]
    for label,colour,style in [('zero','.3','--'),('positive','#d56d35','-'),('negative','#337ab3','-')]:
        with np.load(directory/f'{regime}_rk1_{label}.npz') as data:state=data['state']
        t,z=state[:,0],state[:,3];curves.append((t,z))
        description={'zero':'No spin','positive':'+z spin (against ring)',
                     'negative':'−z spin (with ring)'}[label]+': '+controls[label]['classification']
        overview.plot(t,z,color=colour,ls=style,label=description)
        zoom.plot(t,z-target,color=colour,ls=style)
        marker='s' if controls[label]['classification']=='reflected' else 'o'
        zoom.plot(t[-1],z[-1]-target,marker,color=colour,ms=5)
    overview.axhline(target,color='.6',lw=.8);zoom.axhline(0.,color='.6',lw=.8)
    overview.set(xlabel='Coordinate time t',ylabel='Signed height z',title='Launch z=+1 toward z=−10')
    end=max(t[-1] for t,z in curves)
    zoom.set(xlabel='Coordinate time t',ylabel='Height above target: z+10',xlim=(.95*end,1.01*end),
             yscale='symlog',title='Endpoint and first turnaround')
    zoom.set_yscale('symlog',linthresh=1e-8)
    zoom.set_ylim(-1e-9,2.)
    zoom.set_yticks([0.,1e-6,1e-4,1e-2,1.])
    for ax in (overview,zoom):ax.grid(alpha=.2)
    handles,labels=overview.get_legend_handles_labels()
    fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,.9),ncol=3,frameon=False)
    title=title or ('Spin-selective finite uphill transit' if result['spin_selective_finite_transit'] else 'Matched-energy uphill transit')
    fig.suptitle(title,y=.99,fontsize=15)
    energy=result['energies'][regime]
    fig.text(.5,.065,f'Same conserved energy E={energy:.12f}; spin magnitude 0.001. '
             f'Energy case: {regime.replace("_"," ")}.\n'
             'Squares mark first turnarounds; circles mark target arrivals. '
             'Finite transit does not demonstrate escape or long-term trapping.',ha='center',fontsize=9)
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,dpi=180);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('directory',type=Path)
    parser.add_argument('--out',type=Path,required=True);parser.add_argument('--title')
    args=parser.parse_args();plot(args.directory,args.out,title=args.title)


if __name__=='__main__':main()
