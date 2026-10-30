"""Classical spin curves and the article's explicitly selected candidates."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from grteclyn_wrapper.visualisation.spinning_wormhole.plot_spin_trends import FAMILIES, family
from grteclyn_wrapper.visualisation.spinning_wormhole.solutions import load as load_solutions
from grteclyn_wrapper.visualisation.wormhole_merger import style
from .palette import BLUE, LIGHT_BLUE, INK
from .paper_results import REPO, load_models
OUT = REPO / 'results/optimisation/figures'

def plot(out=OUT):
    style.prd(8.)
    rows=load_solutions()
    fams=[family(rows,eta0,gamma) for eta0,gamma,*_ in FAMILIES]
    x0={name:fam['static']['X'] for fam,(*_,name,_) in zip(fams,FAMILIES)}
    fig,ax=plt.subplots(figsize=(3.4,2.55),layout='constrained')
    entries=[]
    for fam,(*_,name,ls) in zip(fams,FAMILIES):
        v=np.r_[0.,fam['v']]; y=np.r_[1.,fam['Xrel']];good=np.isfinite(y)
        ln,=ax.plot(v[good],y[good],color=INK,ls=ls,lw=1.2)
        entries.append((ln,('D' if name=='drainhole' else 'S')+r' ($\mathcal{V}=0$)'))
    for family_name,colour,marker in (('Drainhole',BLUE,'s'),('Symmetric',LIGHT_BLUE,'o')):
        fmt=dict(marker=marker,ms=4.,mfc='white',mec=colour,mew=1.,ls='none')
        entries.append((Line2D([],[],**fmt),('D' if family_name=='Drainhole' else 'S')+' (search grid)'))
        for r in load_models():
            if r['family']!=family_name or r['stage']!='search':continue
            y=r['X']/x0[family_name.lower()]
            ax.plot(r['ve'],y,**fmt,zorder=3)
            if r['id']=='D21':continue  # the nearby fine solution carries the label
            dy,va=(-5,'top') if family_name=='Drainhole' else (4,'bottom')
            if r['id']=='D90': dy,va=-8,'top'
            dx,ha=(3,'left') if r['ve']==0 else (0,'center')
            if r['id']=='D90': dx=-8
            if r['id']=='S85': dx,dy,ha,va=2,-4,'center','top'
            ax.annotate(r['model'],(r['ve'],y),xytext=(dx,dy),textcoords='offset points',fontsize=6.2,ha=ha,va=va)
    r=next(r for r in load_models() if r['stage']=='fine')
    fmt=dict(marker='D',ms=4.3,mfc=BLUE,mec=INK,mew=.5,ls='none')
    ax.plot(r['ve'],r['X']/x0['drainhole'],**fmt,zorder=4)
    ax.annotate(r'D21$^\star$',(r['ve'],r['X']/x0['drainhole']),xytext=(0,-6),textcoords='offset points',fontsize=6.2,ha='center',va='top')
    entries.append((Line2D([],[],**fmt),r'D21$^\star$ ($210\times42$)'))
    ax.set(xlabel=r'$v_e$',ylabel=r'$X/X_{\rm static}$',xlim=(-.04,1.),ylim=(0,1.12))
    style.legend_top(ax,entries,ncol=2,fontsize=7,mode=None,loc="lower center",bbox_to_anchor=(.5,1.02),handlelength=1.5,handletextpad=.4,columnspacing=.8,labelspacing=.3,borderpad=.55)
    problems=style.label_audit(fig)
    print(style.save(fig,out/'exotic_spin'))
    plt.close(fig)
    if problems:raise SystemExit(problems)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,default=OUT)
    plot(ap.parse_args().out)
if __name__=='__main__':main()
