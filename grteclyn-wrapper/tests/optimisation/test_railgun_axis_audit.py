"""Independent axis derivatives reproduce an exact curvature invariant."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

PATH=Path('grteclyn-wrapper/scripts/campaigns/railgun/audit_axis_curvature.py')
SPEC=importlib.util.spec_from_file_location('axis_audit',PATH)
audit=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def test_rotating_flat_coordinates_have_zero_curvature():
    d=np.longdouble
    jets=audit.metric_jets((d(0),)*4,(d(1),d(0),d(0),d(0)),
                           (d('.4'),d(0),d(0),d(0)),d(0))
    assert np.max(abs(audit.riemann(jets)))<1e-18


def test_schwarzschild_isotropic_axis_has_exact_kretschmann():
    d=np.longdouble;r=d(2);mass=d('.2');u=mass/(2*r)
    f=2*(np.log1p(-u)-np.log1p(u))
    fz=4*u/(r*(1-u*u));fzz=-8*u/(r*r*(1-u*u)**2)
    c=(1+u)**4;cz=-4*u*(1+u)**3/r
    czz=4*u*(1+u)**2*(2+5*u)/(r*r)
    jets=audit.metric_jets((f,fz,fz/r,fzz),(c,cz,cz/r,czz),(d(0),)*4,d(0))
    g=jets[0];riem=audit.riemann(jets);diag=np.diag(g)
    lower=diag[:,None,None,None]*riem
    inverse=1/diag
    contraction=np.einsum('abcd,abcd,a,b,c,d->',lower,lower,inverse,inverse,inverse,inverse)
    areal=r*(1+u)**2
    assert float(contraction)==pytest.approx(float(48*mass*mass/areal**6),rel=2e-15)


def test_saved_field_axis_discrepancy_matches_independent_gpu_certificate():
    import json
    source=Path('results/railgun/studies/ergo372-smooth-cubic-r2-20261104/accepted.npz')
    certificate=json.loads((source.parent/'corridor.json').read_text())
    report=audit.audit(source)
    actual=next(row for row in report if row['radius']==.004)['maximum']
    expected=certificate['maxima']['parent_curvature_difference']
    assert abs(actual-expected)<2e-12
    assert actual>1e-8
