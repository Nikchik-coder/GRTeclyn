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
    for values,colour,label in zip(amplitudes,colours,labels):
        level=.5*np.max(values)
        contour=cross.contour(rho,z,values,levels=[level],colors=[colour],linewidths=2.)
        for points in contour.allsegs[0]:
            rr,zz=points.T
            x=rr[:,None]*np.cos(phi);yy=rr[:,None]*np.sin(phi)
            ax.plot_surface(x,yy,np.broadcast_to(zz[:,None],x.shape),color=colour,alpha=.65,
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
    status='Validated' if accepted else 'Single-grid candidate'
    fig.suptitle(f'{status} counter-rotating scalar rings · {nx}×{ny}',y=.995)
    fig.text(.5,.045,'Each surface is 50% of its own field’s peak |χ|²; dots mark equatorial peaks.\n'
             'Diffuse fields can overlap. These contours are not solid walls or certified particle corridors.',
             ha='center',fontsize=10)
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,dpi=180);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--extent',type=float,default=25.)
    parser.add_argument('--diagnostic',action='store_true',help='label a passing single-grid candidate explicitly')
    args=parser.parse_args();plot_two_rings(args.source,args.out,extent=args.extent,diagnostic=args.diagnostic)


if __name__=='__main__':main()
