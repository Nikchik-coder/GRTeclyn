"""Read-only extended-precision curvature audit on the rotation axis.

Reconstruct analytic Cartesian metric derivatives from the saved polynomial
and compare with the degree-12 core. No solve, filtering or CUDA startup.
The rotating-flat-metric check exercises the connection-product terms.
"""
import json
from pathlib import Path
import numpy as np
from scipy.fft import dct
LD=np.longdouble

def transform(a):
 a=np.asarray(a,dtype=LD)
 for axis in (0,1):
  a=dct(a,type=1,axis=axis)/(a.shape[axis]-1)
  idx=[slice(None)]*2;idx[axis]=[0,-1];a[tuple(idx)]*=LD('.5')
 return a.astype(float).astype(LD)

def val(c,s,y,ds=0,dy=0):
 c=np.polynomial.chebyshev.chebder(c,m=ds,axis=0)
 c=np.polynomial.chebyshev.chebder(c,m=dy,axis=1)
 return np.polynomial.chebyshev.chebval2d(s,y,c)

def metric_jets(f,c,w,h):
 # Each scalar tuple: value, z derivative, xx derivative, zz derivative.
 F,Fz,Fxx,Fzz=f;C,Cz,Cxx,Czz=c;W,Wz,_,_=w
 A=np.exp(F);g=np.diag(np.array([-A,C,C,C],dtype=LD));dg=np.zeros((4,4,4),dtype=LD);dd=np.zeros((4,4,4,4),dtype=LD)
 dg[0,0,3]=-A*Fz;dd[0,0,3,3]=-A*(Fzz+Fz**2)
 for i in (1,2):dd[0,0,i,i]=-A*Fxx+2*C*W*W
 for i in (1,2,3):
  dg[i,i,3]=Cz;dd[i,i,3,3]=Czz
  for j in (1,2):dd[i,i,j,j]=Cxx+2*h
 dd[1,1,2,2]-=2*h;dd[2,2,1,1]-=2*h
 for a,b in ((1,2),(2,1)):
  dd[a,b,1,2]=h;dd[a,b,2,1]=h
 for i,j,sign in ((1,2,1),(2,1,-1)):
  dg[0,i,j]=dg[i,0,j]=sign*C*W
  for a,b in ((0,i),(i,0)):
   dd[a,b,j,3]=dd[a,b,3,j]=sign*(Cz*W+C*Wz)
 return g,dg,dd

def riemann(jets):
 g,dg,dd=jets;iv=np.diag(1/np.diag(g))
 div=-np.einsum('ai,ijk,jb->abk',iv,dg,iv)
 term=dg.transpose(0,2,1)+dg-dg.transpose(2,0,1)
 dt=dd.transpose(0,2,1,3)+dd-dd.transpose(2,0,1,3)
 gam=LD('.5')*np.einsum('ad,dbc->abc',iv,term)
 dgam=LD('.5')*(np.einsum('adk,dbc->abck',div,term)+np.einsum('ad,dbck->abck',iv,dt))
 return dgam.transpose(0,1,3,2)-dgam+np.einsum('aec,ebd->abcd',gam,gam)-np.einsum('aed,ebc->abcd',gam,gam)

def core_coefficients(coeff,length,radius,degree):
 pi=np.arccos(LD(-1));nodes=np.cos(pi*(np.arange(degree+1,dtype=LD)+LD('.5'))/(degree+1))
 squared=(nodes+1)/2*radius**2;rho,z=np.meshgrid(np.sqrt(squared),np.sqrt(squared),indexing='ij');r2=rho*rho+z*z;r=np.sqrt(r2);s=(r-length)/(r+length);y=2*z*z/r2-1
 f,w,n,b=[val(coeff[k],s,y) for k in ('f','w','N','b')];c=(1+b)**2*np.exp(-f);nu=n*rho*rho/r2
 exprel=np.divide(np.expm1(nu),nu,out=np.ones_like(nu),where=nu!=0)
 samples=dict(f=f,C=c,w=w,H=c*n/r2*exprel)
 out={}
 for key,a in samples.items():
  for axis in (0,1):
   a=dct(a,type=2,axis=axis)/(degree+1);idx=[slice(None)]*2;idx[axis]=0;a[tuple(idx)]*=LD('.5')
  out[key]=a.astype(float).astype(LD)
 return out

def audit(path):
 with np.load(path,allow_pickle=False) as saved:
  meta=json.loads(str(saved['metadata']));nx,ny=meta['nx'],meta['ny'];n=(nx+1)*(ny+1)
  coeff={key:transform(saved['u'][i*n:(i+1)*n].reshape(nx+1,ny+1)) for i,key in enumerate(('f','w','N','b'))}
  if meta.get('representation')=='spectral_metric_cubic_dragging_smooth_origin_v1':
   for i,key in ((0,'f'),(2,'N'),(3,'b')):
    coeff[key]=saved['solver_u'][i*n:(i+1)*n].reshape(nx+1,ny+1).astype(LD)
  h=dct(saved['solver_u'][n:2*n].reshape(nx+1,ny+1).astype(LD),type=1,axis=1)/ny;h[:,[0,-1]]*=LD('.5')
  wc=np.zeros((nx+4,ny+1),dtype=LD)
  for j in range(ny+1):
   a=np.polynomial.chebyshev.chebmul([LD('2.5'),LD('-3.75'),LD('1.5'),LD('-.25')],h[:,j]);wc[:len(a),j]=a
  coeff['w']=wc.astype(float).astype(LD)
 length=LD(meta['length']);radius=LD('.08');core=core_coefficients(coeff,length,radius,12)
 reports=[]
 for r in map(LD,('.004','.016','.0392','.0408','.056','.0792')):
  s=(r-length)/(r+length);sr=2*length/(r+length)**2;srr=-4*length/(r+length)**3
  def parent(key):
   a=coeff[key];ps=val(a,s,LD(1),1);return (val(a,s,LD(1)),ps*sr,ps*sr/r-4*val(a,s,LD(1),dy=1)/r**2,val(a,s,LD(1),2)*sr**2+ps*srr)
  f=parent('f');w=parent('w');b=parent('b');nv=parent('N')[0]
  C=(1+b[0])**2*np.exp(-f[0]);logz=2*b[1]/(1+b[0])-f[1]
  c=(C,C*logz,C*(2*b[2]/(1+b[0])-f[2]),C*(logz**2+2*b[3]/(1+b[0])-2*b[1]**2/(1+b[0])**2-f[3]))
  rp=riemann(metric_jets(f,c,w,C*nv/r**2))
  def inner(key):
   a=core[key];u=LD(-1);v=2*r*r/radius**2-1
   return (val(a,u,v),val(a,u,v,dy=1)*4*r/radius**2,val(a,u,v,ds=1)*4/radius**2,val(a,u,v,dy=2)*16*r*r/radius**4+val(a,u,v,dy=1)*4/radius**2)
  rc=riemann(metric_jets(inner('f'),inner('C'),inner('w'),inner('H')[0]))
  diff=abs(rp-rc);idx=np.unravel_index(np.argmax(diff),diff.shape)
  reports.append(dict(radius=float(r),maximum=float(diff[idx]),component=list(map(int,idx)),parent=float(rp[idx]),core=float(rc[idx])))
 return reports

if __name__=='__main__':
 import sys
 flat=riemann(metric_jets((LD(0),)*4,(LD(1),LD(0),LD(0),LD(0)),(LD('.4'),LD(0),LD(0),LD(0)),LD(0)))
 assert np.max(abs(flat))<1e-18,np.max(abs(flat))
 print(json.dumps(audit(Path(sys.argv[1])),indent=2))
