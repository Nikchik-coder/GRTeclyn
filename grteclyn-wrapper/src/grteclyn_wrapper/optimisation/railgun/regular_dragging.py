"""Regular zero-J dragging equation, retaining every interior momentum row.

The old tau form discarded four outer PDE rows and constrained physical w,
whose fifth-order zero hides errors in H. Here H has nx+1 radial coefficients,
every interior row imposes E_w/(1-s)^5, and infinity supplies the regular
angular condition plus its null-mode first-order Frobenius condition.
"""
from __future__ import annotations
import numpy as np
from .dragging_falloff import FactoredDraggingProblem
from .problem import RingProblem
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import cheb_eval


def infinity_matrices(y,dy,dyy):
    """Angular operator and its self-adjoint octupole projection."""
    y=np.asarray(y);q=(5*y+3)/2
    angular=4*(1-y*y)[:,None]*dyy-(10*y+6)[:,None]*dy+10*np.eye(len(y))
    mu,weights=np.polynomial.legendre.leggauss(max(48,3*len(y)))
    mu=(mu+1)/2;weights=weights/2
    basis=cheb_eval(y,np.eye(len(y)),2*mu*mu-1)
    left=(weights*(1-mu*mu)*(5*mu*mu-1))@basis
    left=left/(left@q)
    return angular,q,left


def regular_operator(s,y,h,hx,hxx,hy,hyy,fx,fy,b,bx,by,source,*,xp=np):
    """Algebraic E_w/(1-s)^5, with no subtraction of endpoint zeros."""
    t=1-s;a=(1+s)**2/4;bb=2-t*t/2;c=-2*fx+3*bx/b
    return (t*t*a*hxx+(t*(bb-10*a)+t*t*a*c)*hx
            +(20*a-5*bb-5*t*a*c)*h+4*(1-y*y)*hyy
            +(-(10*y+6)+(1-y*y)*(-8*fy+12*by/b))*hy-source)


class RegularDraggingProblem(FactoredDraggingProblem):
    omitted_row_count=0

    def __init__(self,*args,power=5,**kwargs):
        if power!=5:raise ValueError('regular operator requires quintic zero-J falloff')
        super().__init__(*args,power=5,**kwargs)
        self.representation='dragging_quintic_regular_operator_v2'
        self.h_count=self.nx+1;self.h_degree=self.nx
        eye=np.eye(self.h_count)
        self.h_basis=np.polynomial.chebyshev.chebvander(self.s,self.h_degree)
        self.h_first=np.column_stack([np.polynomial.chebyshev.chebval(self.s,
            np.polynomial.chebyshev.chebder(c)) for c in eye])
        self.h_second=np.column_stack([np.polynomial.chebyshev.chebval(self.s,
            np.polynomial.chebyshev.chebder(c,2)) for c in eye])
        self.angular,self.mode,self.left=infinity_matrices(self.y,self.dy,self.dyy)

    def pack(self,arrays,frequencies):
        value=RingProblem.pack(self,arrays,frequencies)
        basis=(1-self.s[:,None])**5*self.h_basis
        coeff=np.linalg.lstsq(basis,np.asarray(arrays['w']),rcond=1e-12)[0]
        value[self.n:2*self.n]=coeff.ravel()
        return value

    def transfer(self,old,u,*,perturb=0.):
        if isinstance(old,RegularDraggingProblem) and self.length==old.length and not perturb:
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

    def regular_rows(self,u,xp=np):
        arrays,freq=self.unpack(u);jets=RingProblem.jets(self,arrays,xp)
        c=self.raw_dragging(u);h=xp.asarray(self.h_basis)@c
        hx=xp.asarray(self.h_first)@c;hxx=xp.asarray(self.h_second)@c
        hy=h@xp.asarray(self.dy).T;hyy=h@xp.asarray(self.dyy).T
        t=1-xp.asarray(self.s[1:-1,None]);y=xp.asarray(self.y[None,:]);sk=(1-y)/2
        source=xp.zeros_like(h[1:-1])
        for i,(field,omega) in enumerate(zip(self.fields,freq)):
            ka=abs(field.winding);q=jets[f'q{i}']
            if ka:
                parity=(1+y)/2 if field.parity=='odd' else 1.
                source=source+4*field.winding*(omega+field.winding*arrays['w'][1:-1])*xp.exp(jets['N']*sk)*sk**(ka-1)*parity*q*q/t**5
        return regular_operator(xp.asarray(self.s[1:-1,None]),y,
            h[1:-1],hx[1:-1],hxx[1:-1],hy[1:-1],hyy[1:-1],
            jets['f_x'],jets['f_y'],jets['B'],jets['B_x'],jets['B_y'],source,xp=xp)

    def infinity_boundary(self,u,xp=np):
        arrays,_=self.unpack(u);c=self.raw_dragging(u)
        h=xp.sum(c,axis=0);hs=xp.asarray(self.h_first[0])@c
        fx=(xp.asarray(self.dx)@arrays['f'])[0]
        bx=(xp.asarray(self.dx)@arrays['b'])[0]
        drift=-2*fx+3*bx/(1+arrays['b'][0])
        hy=xp.asarray(self.dy)@h;drifty=xp.asarray(self.dy)@drift
        angular=xp.asarray(self.angular)@h
        q,left=xp.asarray(self.mode),xp.asarray(self.left)
        # The angular operator has one null direction. Its next-order
        # equation fixes the corresponding radial derivative, not its value.
        robin=left@(8*hs+(20+5*drift)*h+4*(1-xp.asarray(self.y)**2)*drifty*hy)
        return angular-q*(left@angular)+q*robin

    def _residual(self,u):
        xp=self.xp;value=RingProblem._residual(self,u)
        block=xp.concatenate((self.infinity_boundary(u,xp)[None,:],self.regular_rows(u,xp),
                              self.dragging_jets(u,xp)['w_x'][-1:])).ravel()
        return value.at[self.n:2*self.n].set(block)
