"""Assess saved three-grid checks allowing matter to overlap the throat.

This CPU-only assessment changes only the exterior-ring preference. It never
re-solves fields or removes equation, energy, symmetry, geometry or tide gates.
Original diagnostics and rejection records remain unchanged.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from .railgun_wormhole import throat_ergoregion_convergence
from .resolution import consistent


def assess(records):
    rows=[]
    expected=[(210,36),(224,38),(240,40)]
    if [(r.get('nx'),r.get('ny')) for r in records]!=expected:
        return dict(passed=False,reason='missing_three_grid_checks')
    for original in records:
        r=dict(original)
        if r.get('verdict') not in ('PASS','ABOVE_GATE') or 'rejection_reasons' not in r:
            return dict(passed=False,reason='failed_or_incomplete_validation')
        reasons=[s for s in r['rejection_reasons'] if s!='ring_does_not_surround_throat']
        r.update(rejection_reasons=reasons,verdict='ABOVE_GATE' if reasons else 'PASS')
        if (not r.get('offgrid_pass') or not r.get('surface_verified')
                or not r.get('tidal_converged')):
            return dict(passed=False,reason='independent_checks_missing_or_failed')
        rows.append(r)
    ok,xdrift=consistent(rows,'X_full')
    keys=('E_b','Q_b','J_measured','ring_peak_radius','equatorial_shift_over_lapse_max')
    drift=max(abs(rows[-1][k]-rows[-2][k])/max(abs(rows[-1][k]),1e-12) for k in keys)
    passed=bool(ok and np.isfinite(drift) and drift<=1e-6)
    result=dict(passed=passed,model='matter may overlap the throat',method='refine',
        relative_bill_drift=xdrift,ring_observable_relative_drift=drift,records=rows,
        throat_ergoregion_resolved=False,stability='not_assessed')
    if passed:result.update(throat_ergoregion_convergence(rows))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path);a=p.parse_args()
    from .exploration import load_seed
    from .resolution import save_checked
    from .study import write_json
    raw=json.loads((a.run/'ring/result.json').read_text());result=assess(raw['records'])
    if result['passed']:
        row=result['records'][-1]
        state,meta=load_seed(a.run/'ring/diagnostic_240x40.npz')
        baseline,base=load_seed(a.run/'static_reference.npz')
        config=dict(meta['config'],J=row['J_measured'])
        result.update(X_full=row['X_full'],X_static=base['diagnostics']['X_full'],
            static_fractional_reduction=1-row['X_full']/base['diagnostics']['X_full'])
        save_checked(a.run/'accepted_overlap.npz',state,config,
            dict(pin=meta['pin'],matter_may_overlap_throat=True),result)
    write_json(a.run/'overlap_assessment.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='records'}),flush=True)
    return 0 if result['passed'] else 2

if __name__=='__main__':raise SystemExit(main())
