"""Regular cubic/quintic dragging equations, retaining every interior row.

The old tau forms discarded outer PDE rows and constrained physical w,
whose fifth-order zero hides errors in H. Here H has nx+1 radial coefficients,
every interior row imposes E_w/(1-s)^p, and infinity supplies the regular
angular condition plus its null-mode first-order Frobenius condition.
"""
from __future__ import annotations
import numpy as np
from .dragging_falloff import FactoredDraggingProblem
from .problem import RingProblem
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import cheb_eval


def infinity_matrices(y,dy,dyy,*,power=5):
    """Angular operator and its self-adjoint allowed-mode projection."""
    y=np.asarray(y);q=(5*y+3)/2 if power==5 else np.ones_like(y)
    angular=4*(1-y*y)[:,None]*dyy-(10*y+6)[:,None]*dy+power*(power-3)*np.eye(len(y))
    mu,weights=np.polynomial.legendre.leggauss(max(48,3*len(y)))
    mu=(mu+1)/2;weights=weights/2
    basis=cheb_eval(y,np.eye(len(y)),2*mu*mu-1)
    mode=5*mu*mu-1 if power==5 else np.ones_like(mu)
    left=(weights*(1-mu*mu)*mode)@basis
    left=left/(left@q)
    return angular,q,left


def regular_operator(s,y,h,hx,hxx,hy,hyy,fx,fy,b,bx,by,source,*,power=5,xp=np):
    """Algebraic E_w/(1-s)^p, with no subtraction of endpoint zeros."""
    t=1-s;a=(1+s)**2/4;bb=2-t*t/2;c=-2*fx+3*bx/b
    p=power
    return (t*t*a*hxx+(t*(bb-2*p*a)+t*t*a*c)*hx
            +(p*(p-1)*a-p*bb-p*t*a*c)*h+4*(1-y*y)*hyy
            +(-(10*y+6)+(1-y*y)*(-8*fy+12*by/b))*hy-source)


class RegularDraggingProblem(FactoredDraggingProblem):
    omitted_row_count=0

    def __init__(self,*args,power=5,**kwargs):
        if power not in (3,5):raise ValueError('cubic or zero-J quintic regular operator required')
        super().__init__(*args,power=power,**kwargs)
        self.representation=f'dragging_{"quintic" if power==5 else "cubic"}_regular_operator_v2'
        self.h_count=self.nx+1;self.h_degree=self.nx
        eye=np.eye(self.h_count)
        self.h_basis=np.polynomial.chebyshev.chebvander(self.s,self.h_degree)
        self.h_first=np.column_stack([np.polynomial.chebyshev.chebval(self.s,
            np.polynomial.chebyshev.chebder(c)) for c in eye])
        self.h_second=np.column_stack([np.polynomial.chebyshev.chebval(self.s,
            np.polynomial.chebyshev.chebder(c,2)) for c in eye])
        self.angular,self.mode,self.left=infinity_matrices(self.y,self.dy,self.dyy,power=power)

    def pack(self,arrays,frequencies):
        value=RingProblem.pack(self,arrays,frequencies)
        basis=(1-self.s[:,None])**self.power*self.h_basis
        coeff=np.linalg.lstsq(basis,np.asarray(arrays['w']),rcond=1e-12)[0]
        value[self.n:2*self.n]=coeff.ravel()
        return value

    def transfer(self,old,u,*,perturb=0.):
        if isinstance(old,RegularDraggingProblem) and self.length==old.length and self.power==old.power and not perturb:
            if self.shape==old.shape:return np.array(u,copy=True)
            value=RingProblem.transfer(self,old,u,perturb=0.)
            # Transfer H itself. Fitting tiny physical w values again would
            # discard the already determined infinity coefficients.
            by=cheb_eval(old.y,np.eye(old.ny+1),self.y)
            coeff=np.asarray(old.raw_dragging(u))@by.T
            target=np.zeros(self.shape);count=min(len(coeff),len(target))
            target[:count]=coeff[:count]
            value[self.n:2*self.n]=target.ravel()
            return value
        return RingProblem.transfer(self,old,u,perturb=perturb)

    def state_jets(self,u,xp=np):
        arrays,_=self.unpack(u)
        return self.jets(arrays,xp)

    def regular_rows(self,u,xp=np):
        arrays,freq=self.unpack(u);jets=self.state_jets(u,xp)
        c=self.raw_dragging(u);h=xp.asarray(self.h_basis)@c
        hx=xp.asarray(self.h_first)@c;hxx=xp.asarray(self.h_second)@c
        hy=h@xp.asarray(self.dy).T;hyy=h@xp.asarray(self.dyy).T
        t=1-xp.asarray(self.s[1:-1,None]);y=xp.asarray(self.y[None,:]);sk=(1-y)/2
        source=xp.zeros_like(h[1:-1])
        for i,(field,omega) in enumerate(zip(self.fields,freq)):
            ka=abs(field.winding);q=jets[f'q{i}']
            if ka:
                parity=(1+y)/2 if field.parity=='odd' else 1.
                source=source+4*field.winding*(omega+field.winding*arrays['w'][1:-1])*xp.exp(jets['N']*sk)*sk**(ka-1)*parity*q*q/t**self.power
        return regular_operator(xp.asarray(self.s[1:-1,None]),y,
            h[1:-1],hx[1:-1],hxx[1:-1],hy[1:-1],hyy[1:-1],
            jets['f_x'],jets['f_y'],jets['B'],jets['B_x'],jets['B_y'],source,power=self.power,xp=xp)

    def infinity_metric_derivatives(self,u,arrays,xp=np):
        return (xp.asarray(self.dx)@arrays['f'])[0],(xp.asarray(self.dx)@arrays['b'])[0]

    def infinity_boundary(self,u,xp=np):
        arrays,_=self.unpack(u);c=self.raw_dragging(u)
        h=xp.sum(c,axis=0);hs=xp.asarray(self.h_first[0])@c
        fx,bx=self.infinity_metric_derivatives(u,arrays,xp)
        drift=-2*fx+3*bx/(1+arrays['b'][0])
        hy=xp.asarray(self.dy)@h;drifty=xp.asarray(self.dy)@drift
        angular=xp.asarray(self.angular)@h
        q,left=xp.asarray(self.mode),xp.asarray(self.left)
        # The angular operator has one null direction. Its next-order
        # equation fixes the corresponding radial derivative, not its value.
        p=self.power
        robin=left@((2*p-2)*hs+(p*(p-1)+p*drift)*h+4*(1-xp.asarray(self.y)**2)*drifty*hy)
        return angular-q*(left@angular)+q*robin

    def _residual(self,u):
        xp=self.xp;value=RingProblem._residual(self,u)
        block=xp.concatenate((self.infinity_boundary(u,xp)[None,:],self.regular_rows(u,xp),
                              self.dragging_jets(u,xp)['w_x'][-1:])).ravel()
        return value.at[self.n:2*self.n].set(block)
