"""Candidate validation and selection fail closed without real solves or jobs."""
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import numpy as np
import pytest

from grteclyn_wrapper.analysis.spinning_wormhole.spectral import ArctanMap
from grteclyn_wrapper.optimisation import exploration as e
from grteclyn_wrapper.optimisation.solver import device


@pytest.mark.parametrize('bills,verdicts,expected', [
    ([2., 2.+1e-7], ['PASS', 'PASS'], 0),
    ([2., 2.1], ['PASS', 'PASS'], 2),
    ([2., 2.], ['PASS', 'ABOVE_GATE'], 2),
    ([2., float('nan')], ['PASS', 'PASS'], 2),
    ([float('inf'), float('inf')], ['PASS', 'PASS'], 2),
    ([0., 0.], ['PASS', 'PASS'], 2),
])
def test_validation_export_gate(command, invoke, monkeypatch, tmp_path, bills, verdicts, expected):
    m = command('validate_candidate')
    monkeypatch.setattr(device, 'select_device', lambda *a: None)
    monkeypatch.setitem(sys.modules, 'jax', SimpleNamespace(clear_caches=lambda: None))
    state = dict(F=np.zeros((3, 3)), W=np.zeros((3, 3)), N=np.zeros((3, 3)),
                 B=np.ones((3, 3)), PSI=np.ones((3, 3)), sx=np.arange(3), sy=np.arange(3),
                 sigma=2., omega=.1, psim=-1., xi_t=0., map=ArctanMap(eta0=1.))
    meta = dict(m=.3, q=[0., 0., 0.], gamma=0., J=1., member='synthetic', member_eta0=2.)
    monkeypatch.setattr(e, 'load_seed', lambda path: (state, meta))
    monkeypatch.setattr(e, 'physical_throat', lambda s: dict(R_e=2.))
    calls = []
    def solve(s, config, nx, ny, pin, d2, **kw):
        i = len(calls)
        calls.append((config.copy(), pin, d2))
        assert kw['newton_tol'] == 1e-9
        return s, dict(nx=nx, ny=ny, X=bills[i], R_e=4., R_A=4., R_pol=4.,
                       E19=0., E_c=0., verdict=verdicts[i])
    monkeypatch.setattr(e, 'solve_trial', solve)
    monkeypatch.setattr(e, 'save_trial', lambda *a: None)
    out = tmp_path / 'validation'
    assert invoke(m, 'seed.npz', '--gpu', 0, '--grids', '2x2,4x4', '--radius', 4, '--out', out) == expected
    assert calls[0][0]['m'] == .15 and calls[0][0]['J'] == 4.
    assert calls[0][1] == ('R_e', 4.)
    assert (out / 'handoff.npz').exists() == (expected == 0)
    if expected == 0:
        with np.load(out / 'handoff.npz') as z:
            saved = json.loads(str(z['meta']))
            assert saved['stability'] == 'not_assessed'
            assert saved['sigma'] == 4.
            assert set(e.FIELDS).issubset(z.files)


@pytest.mark.parametrize('codes,handoff,expected', [([2, 0], True, 0), ([2, 1], False, 2),
                                                    ([0], False, 3), ([-9], False, 3), ([3], False, 3)])
def test_selection_order_and_process_failures(command, invoke, monkeypatch, tmp_path, codes, handoff, expected):
    m = command('select_validated_candidate')
    for slot, bill in [('b', 2.), ('a', 1.), ('skip', .1), ('nan', float('nan')), ('c', 3.)]:
        np.savez(tmp_path / f'{slot}.npz', meta=json.dumps(dict(slot=slot, X=bill, J=1., m=.3, q=[0, 0, 0])))
    calls = []
    def run(cmd, **kw):
        code = codes[len(calls)]
        calls.append(cmd)
        if code == 0 and handoff:
            dest = Path(cmd[cmd.index('--out')+1])
            dest.mkdir()
            (dest / 'handoff.npz').write_bytes(b'validated fixture')
        return SimpleNamespace(returncode=code)
    monkeypatch.setattr(m.workflow.subprocess, 'run', run)
    out = tmp_path / 'selection'
    assert invoke(m, tmp_path / '*.npz', '--gpu', 0, '--out', out, '--skip', 'skip', '--limit', 2) == expected
    manifest = json.loads((out / 'candidates.json').read_text())
    assert [r['slot'] for r in manifest] == ['a', 'b']
    assert len(calls) == len(codes)
    assert (out / 'selected.json').exists() == (expected == 0)
    assert len((out / 'attempts.jsonl').read_text().splitlines()) == len(codes)
