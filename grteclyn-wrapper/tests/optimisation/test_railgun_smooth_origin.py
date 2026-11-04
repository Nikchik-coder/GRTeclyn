"""Manufactured centre modes and the Einstein equation not imposed by Newton."""
from types import SimpleNamespace

import numpy as np

from grteclyn_wrapper.analysis.spinning_wormhole.spectral import lobatto
from grteclyn_wrapper.optimisation.railgun.model import canonical_rows
from grteclyn_wrapper.optimisation.railgun.smooth_origin import centred_jets,origin_rows


def test_radial_N_mode_solves_imposed_equation_but_violates_spare_constraint():
    # Exact local counterexample: N=c*r in flat f,w,B, with no matter.
    # E_Nr = (r^2 N_rr+2r N_r)/2-N = 0, E_c/dr = 3c.
    # N(0)=0 misses it; N_r(0)=0 excludes it.
    radius = np.array([[.0001],[.1],[2.]])
    length, c = 2.5,.02
    s = (radius-length)/(radius+length)
    dr = 2*length/(1-s)**2
    ddr = 4*length/(1-s)**3
    y = np.array([[-1.,-.3,1.]])
    shape = (3,3)
    jets = {name+suffix:np.zeros(shape) for name in ('f','w','N','B')
            for suffix in ('','_x','_xx','_y','_yy')}
    jets.update(B=np.ones(shape),B_xy=np.zeros(shape),
                N=np.broadcast_to(c*radius,shape),
                N_x=np.broadcast_to(c*dr,shape),N_xx=np.broadcast_to(c*ddr,shape))
    equations = canonical_rows(jets,(),(),r=radius,dr=dr,ddr=ddr,y=y,xp=np)
    np.testing.assert_allclose(equations['E_Nr'],0,atol=1e-16)
    np.testing.assert_allclose(equations['E_c']/dr,3*c,atol=1e-16)
    value = np.zeros((2,3))
    derivative = np.full((2,3),c*length/2)
    assert np.min(abs(origin_rows(value,derivative))) > .01


def test_origin_rows_reject_angular_offsets_and_allow_regular_quadratic_modes():
    s,dx = lobatto(20)
    y,_ = lobatto(8)
    regular = 4.+.2*(1+s[:,None])**2*(1+y[None,:])
    derivative = dx@(regular-regular[-1:])
    np.testing.assert_allclose(origin_rows(regular,derivative,anisotropy=True),0,atol=1e-12)
    irregular = regular+.01*y[None,:]
    derivative = dx@(irregular-irregular[-1:])
    assert np.max(abs(origin_rows(irregular,derivative,anisotropy=True))) > .005


def test_constant_fields_have_exactly_zero_jets_despite_large_offsets():
    _,dx = lobatto(224)
    _,dy = lobatto(28)
    arrays = {tag:np.full((225,29),value) for tag,value in
              [('f',-4.6),('w',.5),('N',0.),('b',.3)]}
    jets = centred_jets(arrays,dx,dx@dx,dy,dy@dy)
    for key,value in jets.items():
        if '_' in key:
            assert np.count_nonzero(value) == 0,key


def test_equal_origin_values_leave_no_artificial_angular_residual():
    target = -4.081508651592244
    values = np.full((2,33),target)
    derivative = np.zeros_like(values)
    # Equal angular values must satisfy isotropy exactly on every backend.
    assert np.count_nonzero(origin_rows(values,derivative,anisotropy=True)) == 0


def test_mixed_jet_matches_polynomial_with_a_large_constant_offset():
    s,dx = lobatto(24)
    y,dy = lobatto(10)
    b = 200.+.125*s[:,None]**2*y[None,:]**2+.25*y[None,:]+.4*s[:,None]
    jets = centred_jets({'b':b},dx,dx@dx,dy,dy@dy)
    np.testing.assert_allclose(jets['B_xy'],.5*s[1:-1,None]*y[None,:],atol=2e-9,rtol=0)
