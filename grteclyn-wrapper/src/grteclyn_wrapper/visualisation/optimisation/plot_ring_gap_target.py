"""Schematic of the required concentric annular channel, not a field solution."""
from pathlib import Path
import argparse
import numpy as np


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle,Wedge
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    R1,a1,R2,a2=4.,.8,8.,.9
    left,right=R1+a1,R2-a2;launch=(left+right)/2
    orange,blue,green='#d56d35','#337ab3','#39734e'
    fig,axes=plt.subplots(1,2,figsize=(11,5.6),layout='constrained')
    ax=axes[0]
    ax.add_patch(Wedge((0,0),R1+a1,0,360,width=2*a1,facecolor=orange,alpha=.85))
    ax.add_patch(Wedge((0,0),R2+a2,0,360,width=2*a2,facecolor=blue,alpha=.85))
    ax.add_patch(Wedge((0,0),right,0,360,width=right-left,facecolor=green,alpha=.1))
    ax.plot(0,0,'ko',ms=4)
    ax.annotate('Common centre',(0,0),xytext=(-1.,1.8),ha='right',arrowprops=dict(arrowstyle='-',color='.3'))
    ax.annotate('',(right,0),(left,0),arrowprops=dict(arrowstyle='<->',color=green,lw=1.5))
    ax.text(launch,1.0,'Gap',ha='center',color=green)
    ax.set(xlabel='x',ylabel='y',xlim=(-10,10),ylim=(-10,10),aspect='equal',title='Top view: concentric rings')
    ax=axes[1]
    ax.axvspan(left,right,color=green,alpha=.1)
    ax.add_patch(Circle((R1,0),a1,facecolor=orange,alpha=.85))
    ax.add_patch(Circle((R2,0),a2,facecolor=blue,alpha=.85))
    ax.axhline(0,color='.7',lw=.8);ax.plot(0,0,'ko',ms=4)
    ax.annotate('',(launch,-2.5),(launch,2.5),arrowprops=dict(arrowstyle='->',color=green,lw=2))
    ax.text(launch,2.8,'Particle launch line',ha='center',color=green)
    ax.annotate('',(right,-1.7),(left,-1.7),arrowprops=dict(arrowstyle='<->',color=green,lw=1.5))
    ax.text(launch,-2.1,'Gap width > 0',ha='center',color=green)
    ax.text(R1,1.2,'Inner ring',ha='center',color=orange)
    ax.text(R2,1.2,'Outer ring',ha='center',color=blue)
    ax.set(xlabel='Cylindrical radius ρ',ylabel='Height z',xlim=(-.5,10),ylim=(-4,4),
           aspect='equal',title='Meridional section: study the annular channel')
    for ax in axes:ax.grid(alpha=.12)
    fig.suptitle('Required geometry — schematic, not a computed solution',fontsize=14)
    fig.supxlabel('Outer edge of inner ring < particle crossing radius < inner edge of outer ring',fontsize=11)
    args.out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(args.out,dpi=180);plt.close(fig)


if __name__=='__main__':main()
