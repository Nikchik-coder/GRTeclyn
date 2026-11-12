"""Saved, accepted off-axis particle paths and their measured matter exposure."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np


def plot(directory,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    directory=Path(directory);result=json.loads((directory/'outcome.json').read_text())
    manifest=json.loads((directory/'manifest.json').read_text());plan=manifest['plan']
    if not result.get('accepted'):raise ValueError('accepted annular transit required')
    fig,(path,exposure)=plt.subplots(1,2,figsize=(11,5))
    fig.subplots_adjust(left=.09,right=.97,bottom=.2,top=.73,wspace=.32)
    path.axvspan(plan['rho_min'],plan['rho_max'],color='#40856b',alpha=.15)
    for label,colour,style,name in [('zero','.3','--','No spin'),('positive','#d56d35','-','+z spin'),('negative','#337ab3',':','−z spin')]:
        with np.load(directory/f'rk1_{label}.npz',allow_pickle=False) as data:
            state=data['state'];density=data['density']
        rho=np.hypot(state[:,1],state[:,2]);z=state[:,3]
        path.plot(rho,z,color=colour,ls=style,lw=1.8,label=name)
        path.plot(rho[-1],z[-1],'o',color=colour,ms=4)
        relative=np.max(density/np.asarray(plan['peak_densities'])[:,None],axis=0)
        exposure.semilogy(z,relative,color=colour,ls=style,lw=1.8)
    path.set(xlabel='Cylindrical radius ρ',ylabel='Signed height z',ylim=(-10.5,10.5),
             xlim=(plan['rho_min'],plan['rho_max']),title='Inside the validated annular tube')
    exposure.axhline(1e-6,color='.4',lw=1.,ls='--')
    exposure.set(xlabel='Signed height z',ylabel='Largest component density / own peak',
                 xlim=(10.,-10.),title='Matter exposure along the actual paths')
    for ax in (path,exposure):ax.grid(alpha=.2)
    handles,labels=path.get_legend_handles_labels()
    fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,.9),ncol=3,frameon=False)
    energy=result['records']['rk1']['controls']['zero']['launch']['energy']
    fig.suptitle('Validated particle passage between concentric rings',fontsize=15,y=.99)
    fig.text(.5,.065,f'Same conserved energy E={energy:.12f}; spin magnitude 0.001. '
             'Green: common three-grid matter channel.\n'
             'All three spins reach z=−10 while both component densities stay below their 10⁻⁶ thresholds.',
             ha='center',fontsize=9)
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,dpi=180);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('directory',type=Path)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();plot(args.directory,args.out)


if __name__=='__main__':main()
