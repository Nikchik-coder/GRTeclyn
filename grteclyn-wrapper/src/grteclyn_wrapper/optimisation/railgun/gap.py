"""Effective matter edges for a concentric annular channel, with resolved tails.

The two inputs are nonnegative Eulerian matter energy densities in the same
equatorial plane and around the same coordinate centre. The accepted tail
criterion is relative to each component's own peak. A threshold-defined edge
does not assert compact support or exactly zero matter.
"""
from __future__ import annotations
import numpy as np


def equatorial_densities(metadata,u,radius):
    """Eulerian energy on the even-parity equator, without starting JAX."""
    from grteclyn_wrapper.analysis.spinning_wormhole.spectral import cheb_eval,lobatto
    fields=metadata['fields'];nx,ny,L=metadata['nx'],metadata['ny'],metadata['length']
    r=np.asarray(radius,float);n=(nx+1)*(ny+1)
    if r.ndim!=1 or not np.isfinite(r).all() or np.any(r<=0):raise ValueError('positive finite sample radii required')
    if any(f['parity']!='even' for f in fields):raise ValueError('even-parity fields required')
    a=np.asarray(u)[:(4+len(fields))*n].reshape(4+len(fields),nx+1,ny+1)
    frequency=np.asarray(u)[(4+len(fields))*n:(4+len(fields))*n+len(fields)]
    s,dx=lobatto(nx);bx=cheb_eval(s,np.eye(nx+1),(r-L)/(r+L))
    f,w,N,b=(bx@a[i,:,-1] for i in range(4));b=1+b
    densities=[]
    for i,field in enumerate(fields):
        q=bx@a[4+i,:,-1];qr=(bx@(dx@a[4+i])[:,-1])*2*L/(r+L)**2
        potential=field['mass']**2*q*q+field['quartic']*q**4+field['sextic']*q**6
        densities.append(((frequency[i]+field['winding']*w)**2*np.exp(-f)*q*q
            +np.exp(f-N)/b**2*qr**2+field['winding']**2*np.exp(f)*q*q/(b*b*r*r)+potential)/(8*np.pi))
    return np.array(densities)


def annular_gap(radius,densities,*,relative_cutoff=1e-6,minimum_width=0.):
    r=np.asarray(radius,float);d=np.asarray(densities,float)
    if (r.ndim!=1 or len(r)<5 or d.shape!=(2,len(r)) or not np.isfinite(r).all()
            or not np.isfinite(d).all() or np.any(r<0) or np.any(np.diff(r)<=0)
            or np.any(d<0) or not np.isfinite(relative_cutoff) or not 0<relative_cutoff<1
            or not np.isfinite(minimum_width) or minimum_width<0):
        raise ValueError('ordered nonnegative radii, two finite nonnegative densities and valid gap limits required')
    peaks=np.max(d,axis=1)
    if np.any(peaks<=0):raise ValueError('both rings must have nonzero resolved density')
    normal=d/peaks[:,None];peak_indices=np.argmax(d,axis=1)
    reasons=[];edges=[]
    def crossing(row,a,b,level):
        return float(r[a]+(r[b]-r[a])*(level-row[a])/(row[b]-row[a]))
    for i in range(2):
        support=np.flatnonzero(normal[i]>=relative_cutoff)
        first,last=int(support[0]),int(support[-1])
        edges.append(dict(inner_radius=crossing(normal[i],first-1,first,relative_cutoff) if first>0 else None,
                          outer_radius=crossing(normal[i],last,last+1,relative_cutoff) if last<len(r)-1 else None,
                          peak_radius=float(r[peak_indices[i]]),peak_density=float(peaks[i]),
                          inner_edge_resolved=first>0,outer_edge_resolved=last<len(r)-1))
        if peak_indices[i] in (0,len(r)-1):reasons.append(f'field_{i+1}_peak_at_domain_boundary')
    if peak_indices[0]>=peak_indices[1]:reasons.append('component_order_not_inner_then_outer')
    left,right=edges[0]['outer_radius'],edges[1]['inner_radius']
    if left is None:reasons.append('inner_ring_outer_tail_unresolved')
    if right is None:reasons.append('outer_ring_inner_tail_unresolved')
    width=None if left is None or right is None else right-left
    if width is not None and width<=minimum_width:reasons.append('no_resolved_annular_gap')
    # The entire equatorial interval must clear both separate peak thresholds,
    # not merely have one low-density point or separated density maxima.
    corridor=None
    if width is not None and width>minimum_width:
        middle=(left+right)/2
        inside=(r>left)&(r<right)
        if np.count_nonzero(inside)<3:reasons.append('gap_has_fewer_than_three_interior_samples')
        maxima=np.max(normal[:,inside],axis=1) if np.any(inside) else None
        if maxima is None or not np.isfinite(maxima).all() or np.any(maxima>=relative_cutoff):
            reasons.append('matter_exceeds_gap_cutoff')
        corridor=dict(midpoint_radius=float(middle),sampled_relative_density_max=maxima.tolist() if maxima is not None else None,
                      interior_samples=int(np.count_nonzero(inside)))
    return dict(accepted=not reasons,reasons=reasons,relative_density_cutoff=relative_cutoff,
        edges=edges,inner_ring_outer_radius=left,outer_ring_inner_radius=right,
        gap_width=width,minimum_width=minimum_width,corridor=corridor,
        scope='Equatorial matter-gap screen only. Finite-height corridor and particle transit require separate checks.',
        exact_vacuum_claim=False)
