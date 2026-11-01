"""The regular momentum operator retains the physical equation and null mode."""
import numpy as np
from grteclyn_wrapper.optimisation.railgun.regular_dragging import infinity_matrices,regular_operator
from grteclyn_wrapper.analysis.spinning_wormhole.spectral import lobatto


def test_infinity_operator_has_exactly_the_allowed_octupole_null_direction():
    y,dy=lobatto(12);angular,q,left=infinity_matrices(y,dy,dy@dy)
    np.testing.assert_allclose(angular@q,0,atol=2e-11)
    np.testing.assert_allclose(left@angular,0,atol=2e-11)
    assert abs(left@q-1)<1e-14
    assert np.linalg.matrix_rank(angular,tol=1e-8)==12


def test_regular_operator_matches_the_printed_physical_equation():
    from grteclyn_wrapper.optimisation.railgun.model import canonical_rows
    s=np.array([[-.7],[.1],[.85],[.999]])
    y=np.array([[-.9,0.,.9]]);t=1-s;r=3*(1+s)/t;dr=6/t**2;ddr=12/t**3
    h=(1+s+s*s)*(2+y);hx=(1+2*s)*(2+y);hxx=2*(2+y)+np.zeros_like(s)
    hy=(1+s+s*s)+np.zeros_like(y);hyy=np.zeros((4,3))
    shape=(4,3);zero=np.zeros(shape)
    jets={tag+suffix:zero.copy() for tag in ('f','w','B','N') for suffix in ('','_x','_xx','_y','_yy')}
    jets.update(B=np.ones(shape),B_xy=zero,w=t**5*h,w_x=t**5*hx-5*t**4*h,
                w_xx=t**5*hxx-10*t**4*hx+20*t**3*h,w_y=t**5*hy,w_yy=zero)
    physical=canonical_rows(jets,[],[],r=r,dr=dr,ddr=ddr,y=y,xp=np)['E_w']/t**5
    regular=regular_operator(s,y,h,hx,hxx,hy,hyy,zero,zero,np.ones(shape),zero,zero,zero)
    np.testing.assert_allclose(regular,physical,atol=1e-12,rtol=2e-13)


def test_full_regular_block_has_no_auxiliary_or_omitted_pde_rows():
    from grteclyn_wrapper.optimisation.railgun.regular_dragging import RegularDraggingProblem
    from grteclyn_wrapper.optimisation.railgun.model import ScalarField
    p=RegularDraggingProblem([ScalarField(),ScalarField(winding=-2)],nx=12,ny=4,length=3.,target_j=0.)
    u=np.zeros(p.n_unknowns);u[p.n:2*p.n]=1e-6*np.arange(p.n)
    residual=np.asarray(p.residual(u))[p.n:2*p.n].reshape(p.shape)
    assert p.h_count==p.nx+1 and p.omitted_row_count==0
    np.testing.assert_allclose(residual[1:-1],p.regular_rows(u),rtol=1e-11,atol=1e-10)
    np.testing.assert_allclose(residual[0],p.infinity_boundary(u),rtol=1e-11,atol=1e-10)


def test_infinity_null_mode_gets_the_flat_radial_frobenius_condition():
    from grteclyn_wrapper.optimisation.railgun.regular_dragging import RegularDraggingProblem
    from grteclyn_wrapper.optimisation.railgun.model import ScalarField
    p=RegularDraggingProblem([ScalarField(),ScalarField(winding=-2)],nx=12,ny=4,length=3.,target_j=0.)
    u=np.zeros(p.n_unknowns);raw=u[p.n:2*p.n].reshape(p.shape);q=p.mode
    raw[0]=3.5*q;raw[1]=-2.5*q
    np.testing.assert_allclose(p.infinity_boundary(u),0,atol=2e-12)
    raw[0]-=.1*q;raw[1]+=.1*q
    np.testing.assert_allclose(p.infinity_boundary(u),.8*q,atol=2e-12)


def test_regular_state_round_trip_has_an_explicit_distinct_representation(tmp_path):
    from grteclyn_wrapper.optimisation.railgun.regular_dragging import RegularDraggingProblem
    from grteclyn_wrapper.optimisation.railgun.dragging_falloff import save_state,load_state
    from grteclyn_wrapper.optimisation.railgun.model import ScalarField
    p=RegularDraggingProblem([ScalarField(),ScalarField(winding=-2)],nx=12,ny=4,length=3.,target_j=0.)
    u=np.zeros(p.n_unknowns);u[p.n:p.n+5]=1e-5
    path=tmp_path/'state.npz';save_state(path,p,u)
    other,v,m=load_state(path)
    assert m['representation']=='dragging_quintic_regular_operator_v2'
    assert other.h_degree==p.nx
    np.testing.assert_array_equal(v,u)


def test_refinement_preserves_h_coefficients_instead_of_refitting_tiny_w():
    from grteclyn_wrapper.optimisation.railgun.regular_dragging import RegularDraggingProblem
    from grteclyn_wrapper.optimisation.railgun.model import ScalarField
    fields=[ScalarField(),ScalarField(winding=-2)]
    old=RegularDraggingProblem(fields,nx=12,ny=4,length=3.,target_j=0.)
    new=RegularDraggingProblem(fields,nx=16,ny=6,length=3.,target_j=0.)
    u=np.zeros(old.n_unknowns);raw=u[old.n:2*old.n].reshape(old.shape)
    raw[0]=1e-5*(old.y+1);raw[-1]=1e-9*(2-old.y)
    np.testing.assert_array_equal(old.transfer(old,u),u)
    v=new.transfer(old,u);s=np.array([.99,.99999]);y=np.array([-.3,.4])
    np.testing.assert_allclose(new.dragging_sample(v,s,y),old.dragging_sample(u,s,y),rtol=2e-14,atol=0)


def test_cubic_boundary_leaves_total_j_free_for_independent_measurement(tmp_path):
    from grteclyn_wrapper.optimisation.railgun.regular_dragging import RegularDraggingProblem
    from grteclyn_wrapper.optimisation.railgun.dragging_falloff import surface_flux,save_state,load_state
    from grteclyn_wrapper.optimisation.railgun.model import ScalarField
    p=RegularDraggingProblem([ScalarField(),ScalarField(winding=-2)],nx=12,ny=4,length=3.,target_j=0.,power=3)
    u=np.zeros(p.n_unknowns);raw=p.raw_dragging(u);c=1e-5
    raw[0]=2.5*c;raw[1]=-1.5*c
    np.testing.assert_allclose(p.infinity_boundary(u),0,atol=1e-15)
    assert abs(surface_flux(p,u,[1e9])[0]-4*p.length**3*c)<1e-10
    path=tmp_path/'cubic.npz';save_state(path,p,u);other,v,meta=load_state(path)
    assert other.power==3 and meta['representation']=='dragging_cubic_regular_operator_v2'
    np.testing.assert_array_equal(v,u)


def test_printed_momentum_equation_matches_linear_kerr_on_schwarzschild():
    from grteclyn_wrapper.optimisation.railgun.model import canonical_rows
    r=np.array([[4.],[8.],[16.],[32.]])
    y=np.array([[-.9,0.,.9]]);shape=(4,3);zero=np.zeros(shape)
    mass=.7;angular=.13;a=mass/2
    w=2*angular*r**3/(r+a)**6
    logder=3/r-6/(r+a)
    jets={tag+suffix:zero.copy() for tag in ('f','w','B','N') for suffix in ('','_x','_xx','_y','_yy')}
    jets.update(f=2*np.log((r-a)/(r+a))+zero,f_x=4*a/(r*r-a*a)+zero,
                B=1-a*a/r**2+zero,B_x=2*a*a/r**3+zero,B_xy=zero,
                w=w+zero,w_x=w*logder+zero,w_xx=w*(logder**2-3/r**2+6/(r+a)**2)+zero)
    row=canonical_rows(jets,[],[],r=r,dr=np.ones_like(r),ddr=np.zeros_like(r),y=y,xp=np)['E_w']
    np.testing.assert_allclose(row,0,atol=2e-17)
