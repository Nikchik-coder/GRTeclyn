"""Plot an accepted, self-consistent concentric-ring annulus at its true scale."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np


def plot(directory,out,*,diagnostic=False):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from grteclyn_wrapper.optimisation.railgun.gap import cylindrical_densities
    directory=Path(directory);result=json.loads((directory/'outcome.json').read_text())
    accepted=bool(result.get('accepted'))
    passing=[row for row in result['records'] if row.get('verdict')=='PASS']
    if not accepted and (not diagnostic or not passing):
        raise ValueError('accepted three-grid recovery or explicitly labelled passing-grid diagnostic required')
    final=result['records'][-1] if accepted else passing[-1]
    gap=final['annular_gap'];channel=final['finite_height_channel']
    if not gap['accepted'] or not channel['accepted']:raise ValueError('accepted matter channel required')
    name='grid_'+str(final['grid'][0])+'x'+str(final['grid'][1])
    with np.load(directory/('accepted.npz' if accepted else name+'.npz'),allow_pickle=False) as data:
        meta=json.loads(str(data['metadata']));u=np.asarray(data['physical_u'] if 'physical_u' in data else data['u'])
    if accepted and not meta.get('validated'):raise ValueError('accepted fields required')
    profile=np.loadtxt(directory/f'{name}_density.tsv')
    peak=np.array([edge['peak_density'] for edge in gap['edges']])
    extent=1.5*gap['edges'][1]['peak_radius']
    rr=np.unique(np.r_[np.linspace(.001,50.,201),np.linspace(50.,extent,241)])
    zz=np.linspace(-.42*extent,.42*extent,321)
    rho,z=np.meshgrid(rr,zz)
    density=cylindrical_densities(meta,u,rho,z)
    colours=('#d56d35','#337ab3');green='#40856b'
    fig=plt.figure(figsize=(15,5.5));fig.subplots_adjust(left=.04,right=.98,bottom=.19,top=.79,wspace=.32)
    ax=fig.add_subplot(131,projection='3d');cross=fig.add_subplot(132);radial=fig.add_subplot(133)
    phi=np.linspace(0.,2*np.pi,97)
    for i,colour in enumerate(colours):
        contour=cross.contour(rho,z,density[i]/peak[i],levels=[.5],colors=[colour],linewidths=2.)
        for points in contour.allsegs[0]:
            rline,zline=points.T
            x=rline[:,None]*np.cos(phi);y=rline[:,None]*np.sin(phi)
            ax.plot_surface(x,y,np.broadcast_to(zline[:,None],x.shape),color=colour,
                            alpha=.85 if i==0 else .28,linewidth=0.,cstride=2,
                            rstride=max(1,len(rline)//120))
        radial.semilogy(profile[:,0],profile[:,i+1]/peak[i],color=colour,lw=1.8)
    cross.fill_betweenx([channel['z_min'],channel['z_max']],channel['rho_min'],channel['rho_max'],
                        color=green,alpha=.35)
    cross.axhline(0.,color='.8',lw=.6);cross.grid(alpha=.15)
    cross.set(xlabel='Cylindrical radius ρ',ylabel='Signed height z',xlim=(0,extent),
              ylim=(-.42*extent,.42*extent),aspect='equal',title='Common centre · meridional section')
    ax.set(xlabel='x',ylabel='y',zlabel='z',xlim=(-extent,extent),ylim=(-extent,extent),
           zlim=(-.42*extent,.42*extent),box_aspect=(1,1,.6),title='Computed energy half-maximum surfaces')
    ax.view_init(elev=48.,azim=-55.)
    left,right=gap['inner_ring_outer_radius'],gap['outer_ring_inner_radius']
    radial.axvspan(left,right,color=green,alpha=.2)
    radial.axhline(1e-6,color='.3',lw=1.,ls='--')
    radial.set(xscale='log',xlim=(1.,max(profile[-1,0],extent)),ylim=(1e-10,2.),
               xlabel='Equatorial cylindrical radius ρ',ylabel='Density / own component peak',
               title=f'Gap: {left:.2f} < ρ < {right:.2f}')
    radial.grid(alpha=.15,which='both')
    labels=[f'Inner field: k={meta["fields"][0]["winding"]:+d}',
            f'Outer field: k={meta["fields"][1]["winding"]:+d}',
            'Sampled annular channel / gap']
    fig.legend([Patch(facecolor=colours[0]),Patch(facecolor=colours[1]),Patch(facecolor=green,alpha=.35)],
               labels,loc='upper center',bbox_to_anchor=(.5,.92),ncol=3,frameon=False)
    status='Accepted concentric rings' if accepted else 'Provisional concentric rings · full three-grid study rejected'
    fig.suptitle(f'{status} · J total = {final["J_volume"]:.2g}',y=.99,fontsize=15)
    fig.text(.5,.055,'True coordinate scale and shared centre. Each field uses its own peak density. '
             'Dashed line: 10⁻⁶ cutoff.\n'
             f'Green tube: ρ={channel["rho_min"]:.2f}–{channel["rho_max"]:.2f}, '
             f'z={channel["z_min"]:.0f}…{channel["z_max"]:.0f}. '
             'Stationary solution; particle passage and stability remain to test.',ha='center',fontsize=10)
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(out,dpi=180);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--diagnostic',action='store_true',help='explicitly label the last passing grid of a rejected study')
    args=parser.parse_args();plot(args.directory,args.out,diagnostic=args.diagnostic)


if __name__=='__main__':main()
