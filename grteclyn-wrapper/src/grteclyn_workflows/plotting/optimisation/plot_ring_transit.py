"""Plot saved axial trajectories and their finite-radius timing difference."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicSpline


def plot_transit(source,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    source=Path(source);fig,axs=plt.subplots(1,2,figsize=(11,4.3),layout='constrained')
    times={}
    for name,label,colour,style in (('zero','No spin','#555555','-'),
                  ('positive','Spin +z','#b84a30','--'),('negative','Spin −z','#246a96',':')):
        with np.load(source/f'fast_rk1_{name}.npz') as track:
            states=track['state'];t,z=states[:,0],states[:,3]
        axs[0].plot(t,z,label=label,color=colour,linestyle=style)
        if np.any(np.diff(z)>=0):raise ValueError('the timing plot requires monotonic through-transit')
        times[name]=CubicSpline(z[::-1],t[::-1])
    axs[0].axhline(0.,color='.7',linewidth=.7)
    axs[0].set(xlabel='Coordinate time',ylabel='Signed axial position z')
    z=np.linspace(10.,-10.,501)
    axs[1].plot(z,times['positive'](z)-times['negative'](z),color='#663e88',
                label='t(+z spin) − t(−z spin), matched energy')
    axs[1].set(xlabel='Signed axial position z',ylabel='Finite-radius time difference')
    axs[1].invert_xaxis()
    for ax in axs:
        ax.legend(loc='lower center',bbox_to_anchor=(.5,1.02),frameon=False,fontsize=9)
        ax.grid(alpha=.2)
    fig.suptitle('Spinning test bodies through the certified ring centre',fontsize=14)
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,dpi=180);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();plot_transit(args.source,args.out)


if __name__=='__main__':main()
