"""Rebuild the signed-axis and equatorial diagnostics from a saved Run A."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np


def plot_profile(source,out,*,title='Validated k=1 ring: matter wall and signed axial bore'):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    axis=np.loadtxt(Path(source)/'axis.tsv')
    equator=np.loadtxt(Path(source)/'equator.tsv')
    fig,axs=plt.subplots(2,2,figsize=(11,7),layout='constrained')
    ax=axs[0,0]
    ax.plot(equator[:,0],equator[:,2],color='#9a4429',label='Eulerian matter energy density')
    ax.set(xlabel='Cylindrical radius ρ (equatorial plane)',ylabel='Energy density',xlim=(0,20))
    ax=axs[0,1]
    ax.plot(axis[:,0],axis[:,2],label='Eulerian lapse α')
    ax.set(xlabel='Signed axial position z',ylabel='Lapse')
    ax=axs[1,0]
    ax.plot(axis[:,0],axis[:,4],label='Coordinate dragging ω')
    ax.set(xlabel='Signed axial position z',ylabel='Frame-dragging rate')
    ax=axs[1,1]
    ax.plot(axis[:,0],axis[:,6],label='Magnetic tidal curvature Hzz')
    ax.plot(axis[:,0],axis[:,7],linestyle='--',label='Instantaneous linear spin force Fz/Sz')
    ax.set(xlabel='Signed axial position z',ylabel='Curvature / force per unit spin')
    for ax in axs.flat:
        ax.legend(loc='lower center',bbox_to_anchor=(.5,1.01),frameon=False,fontsize=9)
        ax.grid(alpha=.2)
    fig.suptitle(title,fontsize=14)
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(out,dpi=180);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--title',default='Validated k=1 ring: matter wall and signed axial bore')
    args=parser.parse_args();plot_profile(args.source,args.out,title=args.title)


if __name__=='__main__':main()
