"""Resolve the first destination crossing before a terminal turnaround.

Event solvers bracket roots between accepted steps. A destination crossed
twice within one step can be missed even when the first turnaround is found.
Dense sampled states retain the earlier crossing; compare two interpolation
orders and independently recheck its terminal invariants before using it.
"""
from __future__ import annotations
import numpy as np
from scipy.interpolate import BarycentricInterpolator
from scipy.optimize import brentq


def first_crossing(times,states,target):
    t=np.asarray(times,float);u=np.asarray(states,float)
    if (t.ndim!=1 or len(t)<8 or u.shape!=(len(t),24) or not np.isfinite(t).all()
            or not np.isfinite(u).all() or np.any(np.diff(t)<=0) or not np.isfinite(target)):
        raise ValueError('at least eight ordered finite samples of a 24-component trajectory required')
    distance=u[:,3]-target
    hits=np.flatnonzero((distance[:-1]>0)&(distance[1:]<=0))
    if not len(hits):return None
    index=int(hits[0]);evaluations=[]
    for count in (6,8):
        start=max(0,min(index-count//2+1,len(t)-count))
        sl=slice(start,start+count)
        # Fixed weights avoid the interpolator's random permutation and make
        # the audit reproducible for exactly reflected controls.
        nodes=t[sl];diff=nodes[:,None]-nodes[None,:];np.fill_diagonal(diff,1.)
        weights=1/np.prod(diff,axis=1)
        interpolation=BarycentricInterpolator(nodes,u[sl],axis=0,wi=weights)
        root=brentq(lambda value:float(interpolation(value)[3]-target),t[index],t[index+1],xtol=5e-14)
        value=np.asarray(interpolation(root));evaluations.append((root,value))
    (a,ua),(b,ub)=evaluations
    error=dict(proper_time=abs(a-b),state_max=float(np.max(abs(ua-ub))),
               target_residual=abs(float(ub[3]-target)),orders=[5,7],
               coordinate_z_velocity=float(interpolation.derivative(b,der=1)[3]))
    if error['proper_time']>1e-9 or error['state_max']>1e-10 or error['target_residual']>1e-11:
        raise ValueError(f'first-crossing interpolation is unresolved: {error}')
    if error['coordinate_z_velocity']>=0:raise ValueError('crossing must precede the turnaround')
    keep=t<b
    return dict(time=np.r_[t[keep],b],state=np.vstack([u[keep],ub]),audit=error)
