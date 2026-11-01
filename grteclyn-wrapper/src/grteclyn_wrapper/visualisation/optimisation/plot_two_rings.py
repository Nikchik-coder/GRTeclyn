"""Render both computed scalar fields of an accepted counter-rotating solution.

Each surface follows that field's own half-maximum contour. Overlap is
preserved: no empty gap, ordering or idealised torus geometry is imposed.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import cheb_eval,lobatto


def equatorial_density(source,*,extent=25.,samples=2001):
    """Canonical Eulerian energy densities from spectral first derivatives."""
    with np.load(source,allow_pickle=False) as data:
        meta=json.loads(str(data['metadata']));u=np.asarray(data['u'])
    from grteclyn_wrapper.optimisation.railgun.gap import equatorial_densities
    r=np.linspace(.001,extent,samples)
    return r,equatorial_densities(meta,u,r)


def plot_density(source,out,*,extent=25.,data_directory=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    r,density=equatorial_density(source,extent=extent)
    total=np.sum(density,axis=0);peaks=[int(np.argmax(d)) for d in density]
    middle=float(np.mean(r[peaks]));values=[float(np.interp(middle,r,d)) for d in density]
    summary=dict(component_peak_radii=r[peaks].tolist(),midpoint_radius=middle,
        midpoint_component_density=values,midpoint_total_fraction_of_peak=float(sum(values)/np.max(total)),
        radial_sample_spacing=float(r[1]-r[0]),scope='Density overlap only; no between-ring particle path has been integrated.')
    from grteclyn_wrapper.optimisation.railgun.gap import annular_gap
    tail_r,tail_density=equatorial_density(source,extent=max(120.,extent),samples=6001)
    summary['annular_gap']=annular_gap(tail_r,tail_density,relative_cutoff=1e-6)
    fig,ax=plt.subplots(figsize=(8,4.5),layout='constrained')
    for i,(d,c) in enumerate(zip(density,('#d56d35','#337ab3'))):
        ax.plot(r,d,color=c,label=f'Field {i+1}')
    ax.plot(r,total,color='.2',label='Total energy density')
    ax.set(xlabel='Equatorial cylindrical radius ρ',ylabel='Eulerian matter energy density',xlim=(0,extent))
    ax.legend(loc='lower center',bbox_to_anchor=(.5,1.02),ncol=3,frameon=False);ax.grid(alpha=.2)
    fig.suptitle('Annular gap passes the matter screen' if summary['annular_gap']['accepted']
                 else 'No annular gap at the 10⁻⁶ density threshold',fontsize=13)
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,dpi=180);plt.close(fig)
    data=Path(data_directory)/out.stem if data_directory is not None else out.with_suffix('')
    data.parent.mkdir(parents=True,exist_ok=True)
    data.with_suffix('.json').write_text(json.dumps(summary,indent=2)+'\n')
    np.savetxt(data.with_suffix('.tsv'),np.column_stack([r,*density,total]),
               header='rho\tfield1_density\tfield2_density\ttotal_density',delimiter='\t')
    return summary


def plot_two_rings(source,out,*,extent=25.,diagnostic=False):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    source=Path(source)
    with np.load(source,allow_pickle=False) as data:
        metadata=json.loads(str(data['metadata']));u=np.asarray(data['u'])
    fields=metadata['fields']
    accepted=bool(metadata.get('validated'))
    if len(fields)!=2 or fields[0]['winding']*fields[1]['winding']>=0:
        raise ValueError('a two-field counter-rotating archive is required')
    if not accepted:
        record=source.with_suffix('.json')
        if not diagnostic or not record.exists() or json.loads(record.read_text()).get('verdict')!='PASS':
            raise ValueError('an accepted archive or explicitly labelled passing single-grid diagnostic is required')
    nx,ny,L=metadata['nx'],metadata['ny'],metadata['length'];n=(nx+1)*(ny+1)
    arrays=u[:6*n].reshape(6,nx+1,ny+1)
    s,_=lobatto(nx);y,_=lobatto(ny)
    rho,z=np.meshgrid(np.linspace(0.,extent,181),np.linspace(-extent,extent,361))
    r=np.hypot(rho,z);mu=np.divide(z,r,out=np.zeros_like(r),where=r>0)
    bx=cheb_eval(s,np.eye(nx+1),((r-L)/(r+L)).ravel())
    by=cheb_eval(y,np.eye(ny+1),(2*mu*mu-1).ravel())
    amplitudes=[]
    for i,field in enumerate(fields):
        a=np.sum((bx@arrays[4+i])*by,axis=1).reshape(r.shape)
        a*=np.maximum(0.,1-mu*mu)**(abs(field['winding'])/2)
        if field['parity']=='odd':a*=mu
        a[r==0]=0.;amplitudes.append(a*a)
    colours=('#d56d35','#337ab3')
    labels=[f'Field {i+1}: k={f["winding"]:+d}, peak |χ|²={np.max(amplitudes[i]):.3g}' for i,f in enumerate(fields)]
    fig=plt.figure(figsize=(12,6.3));fig.subplots_adjust(left=.05,right=.98,bottom=.18,top=.88,wspace=.15)
    ax=fig.add_subplot(121,projection='3d');cross=fig.add_subplot(122)
    phi=np.linspace(0.,2*np.pi,129)
    for i,(values,colour,label) in enumerate(zip(amplitudes,colours,labels)):
        level=.5*np.max(values)
        contour=cross.contour(rho,z,values,levels=[level],colors=[colour],linewidths=2.)
        for points in contour.allsegs[0]:
            rr,zz=points.T
            x=rr[:,None]*np.cos(phi);yy=rr[:,None]*np.sin(phi)
            ax.plot_surface(x,yy,np.broadcast_to(zz[:,None],x.shape),color=colour,alpha=.8 if i==0 else .25,
                linewidth=0.,rstride=max(1,len(rr)//160),cstride=2,shade=True)
        equatorial=values[len(values)//2]
        peak=int(np.argmax(equatorial))
        cross.plot(rho[0,peak],0.,'o',color=colour)
    ax.set(xlabel='x',ylabel='y',zlabel='z',xlim=(-extent,extent),ylim=(-extent,extent),
           zlim=(-.6*extent,.6*extent),box_aspect=(1,1,.6))
    ax.view_init(elev=45.,azim=-55.)
    cross.set(xlabel='Cylindrical radius ρ',ylabel='Signed height z',aspect='equal',
              xlim=(0,extent),ylim=(-.65*extent,.65*extent))
    cross.axhline(0.,linewidth=.6,color='.7');cross.grid(alpha=.15)
    fig.legend(handles=[Patch(facecolor=c,label=l,alpha=.65) for c,l in zip(colours,labels)],
               loc='upper center',bbox_to_anchor=(.5,.96),ncol=2,frameon=False)
    status='Validated stationary fields' if accepted else 'Single-grid candidate'
    fig.suptitle(f'{status} · counter-rotation · {nx}×{ny}',y=.995)
    fig.text(.5,.045,'Each surface is 50% of its own field’s peak |χ|²; dots mark equatorial peaks.\n'
             'Diffuse fields can overlap. These contours are not solid walls or certified particle corridors.',
             ha='center',fontsize=10)
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,dpi=180);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--extent',type=float,default=25.)
    parser.add_argument('--diagnostic',action='store_true',help='label a passing single-grid candidate explicitly')
    parser.add_argument('--density-out',type=Path,help='also plot the equatorial energy density overlap')
    parser.add_argument('--density-data-dir',type=Path,help='write companion JSON/TSV here, separately from the figure')
    args=parser.parse_args();plot_two_rings(args.source,args.out,extent=args.extent,diagnostic=args.diagnostic)
    if args.density_out:print(json.dumps(plot_density(args.source,args.density_out,extent=args.extent,data_directory=args.density_data_dir)))


if __name__=='__main__':main()
