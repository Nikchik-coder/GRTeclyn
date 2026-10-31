"""Independent static quadratures and derived timing checks for the article."""
import csv
import json
import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize_scalar


def values(root, data, physics_rows, points, candidates):
    a = .5
    re = np.sqrt(1+a*a)*np.exp(a*(np.pi/2-np.arctan(a)))  # eta0=1
    def f(eta):
        return -2*a*(np.pi/2-np.arctan(eta))
    def gradient2(eta):
        return (1+a*a)/(1+eta*eta)**2
    def peak(eta):
        return re**2*np.exp(f(eta))*gradient2(eta)/(4*np.pi)
    exact = {
        'SzeroX': np.pi,
        'DzeroX': np.sqrt(5)*np.exp(.5*np.arctan(.5))*(np.exp(np.pi/4)-np.exp(-np.pi/4)),
        'DzeroPeak': (20/17)**2*np.exp(np.arctan(.25)-np.arctan(.5))/(4*np.pi),
        'DzeroRay': 5*np.sqrt(5)/64*np.exp(np.pi/4-.5*np.arctan(.5)),
    }
    numerical = {
        'SzeroX': quad(lambda eta: 1/(1+eta*eta), -np.inf, np.inf)[0],
        'DzeroX': quad(lambda eta: np.exp(-f(eta)/2)*(1+eta*eta)*gradient2(eta)/re, -np.inf, np.inf)[0],
        'DzeroPeak': -minimize_scalar(lambda eta: -peak(eta), bounds=(-2,2),method='bounded').fun,
        'DzeroRay': re/(4*np.pi)*quad(gradient2,-np.inf,np.inf)[0],
    }
    for key in exact:
        np.testing.assert_allclose(exact[key],numerical[key],rtol=2e-10)
    # The measured peak is sampled, so test it at the precision printed in the table.
    for key, column, digits in [('DzeroX','X',3),('DzeroPeak','radial_nec_peak_Re2',4),('DzeroRay','nec_ray_equator_Re',3)]:
        assert f'{exact[key]:.{digits}f}' == f'{physics_rows["D0","classical"][column]:.{digits}f}'
    times = []
    for n in (96,128,192):
        g=data[n]['geometry']; first=np.flatnonzero(g[:,1]/g[0,1]<=.99)[0]
        times.append(g[first,0])
    slopes=np.diff(times)/np.log(np.array([128/96,192/128]))
    potential=next(p for p in candidates if p['label']=='D21 potential')
    reference=next(p for p in points if p['label']=='D21')
    collapsed=[p for p in points if p['branch']=='collapses']
    x=np.array([p['frac'] for p in collapsed]); y=np.array([p['rate'] for p in collapsed])
    slope,offset=np.linalg.lstsq(np.stack([x*x,np.ones_like(x)],axis=1),y,rcond=None)[0]
    x0=reference['frac']; x1=x0*potential['j']/reference['j']  # area held fixed, deliberately
    sensitivity=100*abs(slope*(x1*x1-x0*x0)/(offset+slope*x0*x0))
    return dict(exact, OnsetSlopeLow=slopes[0],OnsetSlopeHigh=slopes[1],
                SeedOrderLow=slopes[0]/potential['tau'],SeedOrderHigh=slopes[1]/potential['tau'],
                SpinSensitivity=sensitivity)


def check_ledger(root, measured):
    path=root/'results/optimisation/article/ledger_analytic.tsv'
    with path.open() as stream:
        rows=list(csv.DictReader(stream,delimiter='\t'))
    assert {r['quantity'] for r in rows} == set(measured)
    for row in rows:
        np.testing.assert_allclose(float(row['value']),measured[row['quantity']],rtol=1e-12)
    print('Checked exact static benchmarks, onset slopes and fixed-area spin sensitivity.')
    return rows


def generate(rows, macro):
    for row in rows:
        name=row['quantity']
        prefix='clmAnalytic' if name in ('SzeroX','DzeroX','DzeroPeak','DzeroRay') else 'clm'
        macro(prefix+name, f"{float(row['value']):.{int(row['digits'])}f}")


def selected(root):
    path=root/'results/optimisation/article/ledger_selected.tsv'
    with path.open() as stream:
        rows=list(csv.DictReader(stream,delimiter='\t'))
    expected = {entry['model']: entry['inputs'][0]['path'] for entry in
                json.loads((root/'results/optimisation/physics/sources.json').read_text())}
    assert len(rows) == 3 and {r['model'] for r in rows} == set(expected)
    for row in rows:
        assert row['source'] == expected[row['model']]
        with np.load(root/row['source']) as fields:
            meta=json.loads(str(fields['meta']))
        assert (meta['nx'],meta['ny']) == (210,42)
        for key in ('m','X','E19','E_c'):
            np.testing.assert_allclose(float(row[key]),meta[key],rtol=1e-12)
        for i in range(3):
            np.testing.assert_allclose(float(row[f'q{i+1}']),meta['q'][i],rtol=1e-12)
        assert max(meta['E19'],meta['E_c']) < 1e-8
    return rows


def selected_tex(rows,macro):
    def sci(value):
        v=float(value); power=int(np.floor(np.log10(v)))
        return f'{v/10**power:.1f}\\times10^{{{power}}}'
    lines=[]
    for row in rows:
        numbers=[f"{float(row[k]):.3f}" for k in ('m','q1','q2','q3','X')]
        numbers += [sci(row[k]) for k in ('E19','E_c')]
        lines.append(row['model']+r'$^\star$ & '+' & '.join('$'+x+'$' for x in numbers)+r' \\')
    macro('clmSelectedRows','\n'.join(lines)+'\n')
