"""Plot the measured interior dragging and exterior coordinate octupole tail."""
import argparse
from pathlib import Path
import numpy as np


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    inner=np.loadtxt(args.source/'interior_dragging.tsv')
    outer=np.loadtxt(args.source/'exterior_dragging.tsv')
    fig,axes=plt.subplots(1,2,figsize=(10,4.5),layout='constrained')
    keep=inner[:,0]<=30
    axes[0].plot(inner[keep,0],inner[keep,1],label='Rotation axis')
    axes[0].plot(inner[keep,0],inner[keep,2],label='Equatorial plane')
    axes[0].axhline(0.,color='.7',linewidth=.7)
    axes[0].set(xlabel='Radius r',ylabel='Coordinate dragging w',xlim=(0,30))
    r,coefficient=outer[:,0],abs(outer[:,2])
    axes[1].loglog(r,coefficient,'o-',label='Measured octupole angular coefficient')
    axes[1].loglog(r,coefficient[-1]*(r/r[-1])**-5,'--',label='r⁻⁵ reference')
    axes[1].set(xlabel='Exterior radius r',ylabel='Absolute coordinate harmonic coefficient')
    for ax in axes:
        ax.legend(loc='lower center',bbox_to_anchor=(.5,1.02),frameon=False,fontsize=9)
        ax.grid(alpha=.2)
    fig.suptitle('Zero total spin with nonzero interior frame dragging',fontsize=14)
    args.out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(args.out,dpi=180);plt.close(fig)


if __name__=='__main__':main()
