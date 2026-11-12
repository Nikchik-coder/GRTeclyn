"""Ring observables and acceptance checks independent of Newton equilibration."""
from __future__ import annotations

import numpy as np

from grteclyn_stationary.railgun.geometry import RingGeometry
from grteclyn_stationary.numerics.spectral import cheb_eval
from grteclyn_stationary.numerics.spectral import cheb_coeffs
from grteclyn_stationary.numerics.spectral import tail_ratio


def spectral_diagnostics(arrays):
    """Mixed absolute/relative tails; analytically zero fields have no scale.

    Dividing two numbers at roundoff reports O(1) noise for N=0 in a spherical
    spacetime. Subtract a 64 eps absolute coefficient floor before dividing;
    the physical relative tail tolerance and all equation gates are unchanged.
    """
    records = {}
    for tag, a in arrays.items():
        peak = float(np.max(np.abs(a)))
        ratio = max(tail_ratio(a, axis=ax) for ax in (0,1))
        absolute = max(float(np.max(np.abs(np.moveaxis(cheb_coeffs(a,axis=ax),ax,0)[-3:])))
                       for ax in (0,1))
        at_roundoff = peak <= 64*np.finfo(float).eps
        tested = max(0.,absolute-64*np.finfo(float).eps)/max(peak,1e-300)
        records[tag] = dict(peak=peak, relative_tail=ratio, absolute_tail=absolute,
                            roundoff_field=bool(at_roundoff),
                            tested_tail=tested)
    return records


def localized_tail(ratios, tolerance):
    """Require a small last tail and decay wherever the field is measurable."""
    return (np.isfinite(ratios).all() and ratios[-1] <= tolerance
            and all(b <= max(a,tolerance) for a,b in zip(ratios,ratios[1:])))


def angular_momentum_surfaces(problem, u, radii, *, order=48):
    """Exact ADM/Komar surface flux on finite coordinate spheres.

    J(R)=-R^4/4 integral_0^1 B^3 exp(-2f) (1-mu^2) partial_R w dmu.
    The nu factors cancel between the unit normal and area element. This
    approaches total J outside the scalar tail without truncating a 1/r fit.
    """
    arrays,_=problem.unpack(np.asarray(u))
    radii=np.atleast_1d(np.asarray(radii,dtype=float))
    if not np.isfinite(radii).all() or np.any(radii<=0):
        raise ValueError('positive finite surface radii required')
    mu,weights=np.polynomial.legendre.leggauss(order)
    mu,weights=(mu+1)/2,weights/2
    bx=cheb_eval(problem.s,np.eye(problem.nx+1),(radii-problem.length)/(radii+problem.length))
    by=cheb_eval(problem.y,np.eye(problem.ny+1),2*mu*mu-1)
    f=bx@arrays['f']@by.T
    b=1+bx@arrays['b']@by.T
    wr=(bx@(problem.dx@arrays['w'])@by.T)*2*problem.length/(radii[:,None]+problem.length)**2
    return -radii**4/4*np.sum(weights[None,:]*(1-mu[None,:]**2)*b**3*np.exp(-2*f)*wr,axis=1)


def asymptotic_masses(problem, u, *, order=48):
    """ADM and lapse masses from first derivatives at compactified infinity.

    With nu=N(1-mu^2), the Cartesian ADM integral gives
    M=L integral_0^1 [f_s-2 b_s-(1-mu^2) N_s]_(s=1) dmu.
    Keep the N contribution rather than assuming its 1/r coefficient vanishes.
    The asymptotic lapse/Komar mass is L integral f_s dmu.
    """
    arrays,_=problem.unpack(np.asarray(u))
    mu,weights=np.polynomial.legendre.leggauss(order)
    mu,weights=(mu+1)/2,weights/2
    by=cheb_eval(problem.y,np.eye(problem.ny+1),2*mu*mu-1)
    fs,bs,ns=((problem.dx[0]@arrays[tag])@by.T for tag in ('f','b','N'))
    adm=problem.length*np.sum(weights*(fs-2*bs-(1-mu*mu)*ns))
    lapse=problem.length*np.sum(weights*fs)
    return float(adm),float(lapse)


def observables(problem, u):
    arrays, frequencies = problem.unpack(np.asarray(u))
    sample = lambda a: problem.qx@a@problem.qy.T
    f, w, n, b = (sample(arrays[t]) for t in ('f', 'w', 'N', 'b'))
    b = 1+b
    sk = 1-problem.mg[None, :]**2
    r = problem.rg[:, None]
    measure = problem.wr[:, None]*problem.wm[None, :]*r*r*b**3*np.exp(n*sk-f)
    charges = np.asarray(problem.charge_integrals(u))
    komar = 0.
    densities, peaks = [], []
    for i, field in enumerate(problem.fields):
        q = sample(arrays[f'q{i}'])
        mu = problem.mg[None, :]
        factor = sk**(abs(field.winding)/2)*(mu if field.parity == 'odd' else 1.)
        amplitude = factor*q
        amp2 = amplitude**2
        omega = frequencies[i]+field.winding*w
        potential = field.mass**2*amp2+field.quartic*amp2**2+field.sextic*amp2**3
        komar += float(np.sum(measure*(2*frequencies[i]*omega*np.exp(-f)*amp2-potential)))
        qr = (problem.qx@(problem.dx@arrays[f'q{i}'])@problem.qy.T)
        # ds/dr, evaluated at Gaussian radii.
        qr *= 2*problem.length/(problem.rg[:, None]+problem.length)**2
        qy = sample(arrays[f'q{i}']@problem.dy.T)
        ka = abs(field.winding)
        sink = sk**(ka/2)
        # dtheta cos(theta)=-sin(theta), dtheta y=-4 sin(theta)cos(theta).
        atheta = sink*(-4*np.sqrt(sk)*mu*qy)
        if ka:
            atheta += ka*sk**((ka-1)/2)*mu*q
        if field.parity == 'odd':
            atheta = atheta*mu-sink*np.sqrt(sk)*q
        grad2 = np.exp(f-n*sk)/b**2*(factor**2*qr**2+atheta**2/r**2)
        azimuthal = field.winding**2*np.exp(f)*amp2/(b*b*r*r*sk)
        density = (omega**2*np.exp(-f)*amp2+grad2+azimuthal+potential)/(8*np.pi)
        densities.append(density)
        ix, iy = np.unravel_index(np.argmax(density), density.shape)
        peaks.append(dict(radius=float(r[ix, 0]), mu=float(mu[0, iy]),
                          cylindrical_radius=float(r[ix, 0]*np.sqrt(sk[0, iy])),
                          axial_position=float(r[ix, 0]*mu[0, iy]), density=float(density[ix, iy])))
    # Finite-order coefficient fits remain diagnostic estimates. Endpoint
    # derivatives below measure the actual leading terms at infinity.
    shells = problem.length*np.array([12., 16., 22., 30., 42., 60.])
    s = (shells-problem.length)/(shells+problem.length)
    bx = cheb_eval(problem.s, np.eye(problem.nx+1), s)
    by = cheb_eval(problem.y, np.eye(problem.ny+1), np.array([-.8, 0., .8]))
    ff, bb, ww = (bx@arrays[t]@by.T for t in ('f', 'b', 'w'))
    masses, spins, lapse_masses = [], [], []
    for start in (0, 1, 2):
        rr = shells[start:]
        design = np.stack([rr**-1, rr**-2, rr**-3], axis=1)
        masses.append(float(np.mean(np.linalg.lstsq(design, (bb-ff/2)[start:], rcond=None)[0][0])))
        lapse_masses.append(float(np.mean(np.linalg.lstsq(design, (-ff/2)[start:], rcond=None)[0][0])))
        twist = np.stack([rr**-3, rr**-4, rr**-5], axis=1)
        spins.append(float(np.mean(np.linalg.lstsq(twist, ww[start:], rcond=None)[0][0])/2))
    gtt = -np.exp(f)+b*b*np.exp(-f)*r*r*sk*w*w
    surface_radii=shells[2:]
    surface_j=angular_momentum_surfaces(problem,u,surface_radii)
    surface_fine=angular_momentum_surfaces(problem,u,surface_radii,order=96)
    adm_mass,lapse_mass=asymptotic_masses(problem,u)
    endpoint_fine=asymptotic_masses(problem,u,order=96)
    density = sum(densities) if densities else np.zeros_like(gtt)
    maxdensity = float(np.max(density))
    lowdensity = density <= 1e-6*max(maxdensity, 1e-300)
    tails = []
    for i, field in enumerate(problem.fields):
        vals = bx@arrays[f'q{i}']@by.T
        peak = max(float(np.max(np.abs(arrays[f'q{i}']))), 1e-300)
        tails.append((np.max(np.abs(vals), axis=1)/peak).tolist())
    return dict(charges=charges.tolist(), matter_J=[float(-f.winding*q) for f, q in zip(problem.fields, charges)],
                J_volume=float(sum(-f.winding*q for f, q in zip(problem.fields, charges))),
                M_Komar_volume=komar, M_ADM_estimate=adm_mass, M_lapse_estimate=lapse_mass,
                mass_extraction='compactified_endpoint_first_derivatives',
                M_ADM_fit_estimate=masses[-1],M_lapse_fit_estimate=lapse_masses[-1],
                M_endpoint_quadrature_drift=float(max(abs(adm_mass-endpoint_fine[0]),abs(lapse_mass-endpoint_fine[1]))),
                M_fit_drift=max(masses)-min(masses), J_asymptotic_estimate=spins[-1],
                J_fit_drift=max(spins)-min(spins), density_peaks=peaks,
                J_surface_radii=surface_radii.tolist(),J_surfaces=surface_j.tolist(),
                J_surface_estimate=float(surface_j[-1]),
                J_surface_quadrature_drift=float(np.max(abs(surface_j-surface_fine))),
                lapse_min=float(np.min(np.exp(f/2))), B_min=float(np.min(b)),
                dragging_max=float(np.max(np.abs(w))), gtt_max=float(np.max(gtt)),
                gtt_min=float(np.min(gtt)),
                shift_norm_over_lapse_max=float(np.max(b*np.exp(-f)*r*np.sqrt(sk)*np.abs(w))),
                ergoregion_sampled=bool(np.any(gtt>0)),
                low_density_threshold_relative=1e-6,
                low_density_ergoregion_sampled=bool(np.any((gtt>0)&lowdensity)),
                tail_shells=shells.tolist(), scalar_tail_ratios=tails)


def validate(problem, u, info, *, equation_tol=1e-8, tail_tol=1e-6, independent=True):
    u = np.asarray(u)
    reasons = []
    out = dict(grid=[problem.nx, problem.ny], newton=info, length_scale=problem.length,
               stability='not_assessed')
    if not np.isfinite(u).all():
        return dict(out, verdict='REJECT', reasons=['nonfinite_fields'])
    if not info.get('converged'):
        reasons.append('newton')
    arrays, frequencies = problem.unpack(u)
    if any(not 0 < omega < field.mass for omega, field in zip(frequencies, problem.fields)):
        reasons.append('unbound_frequency')
    residual = np.asarray(problem.residual(u))
    if not np.isfinite(residual).all():
        return dict(out, verdict='REJECT', reasons=reasons+['nonfinite_residual'])
    out['raw_residual_max'] = float(np.max(np.abs(residual)))
    rows = problem.rows(u)
    out['constraint_c'] = float(np.max(np.abs(rows['E_c']/problem.dr)))
    out['constraint_19'] = float(np.max(np.abs(rows['E19']/problem.ri**2)))
    out['equation_max'] = max(float(np.max(np.abs(v)/(1+problem.ri**2)))
                              for k, v in rows.items() if k not in ('E_c', 'E19'))
    boundary = np.concatenate([residual[i*problem.n:(i+1)*problem.n].reshape(problem.shape)[[0,-1]].ravel()
                               for i in range(len(problem.tags))])
    borders = residual[len(problem.tags)*problem.n:]
    out['boundary_max'] = float(np.max(np.abs(boundary)))
    out['border_max'] = float(np.max(np.abs(borders))) if len(borders) else 0.
    out['field_spectra'] = spectral_diagnostics(arrays)
    out['spectral_tail'] = max(row['tested_tail'] for row in out['field_spectra'].values())
    for name in ('constraint_c', 'constraint_19', 'equation_max', 'boundary_max', 'border_max'):
        if not np.isfinite(out[name]) or out[name] > equation_tol:
            reasons.append(name)
    if out['spectral_tail'] > tail_tol or not np.isfinite(out['spectral_tail']):
        reasons.append('spectral_tail')
    summary = observables(problem, u)
    out.update(summary)
    if (summary['B_min'] <= 0 or summary['lapse_min'] <= 0
            or np.min(1+arrays['b']) <= 0):
        reasons.append('invalid_metric')
        return dict(out, verdict='REJECT', reasons=reasons)
    from grteclyn_stationary.railgun.problem import RingProblem
    fine = RingProblem(problem.fields, nx=problem.nx, ny=problem.ny,
                       length=problem.length, target_j=problem.target_j,
                       quadrature_order=tuple(2*n for n in problem.quadrature_order))
    finer = observables(fine,u)
    out['quadrature_drift'] = max(abs(finer[k]-summary[k])/max(1.,abs(finer[k]))
                                  for k in ('J_volume','M_Komar_volume'))
    if not np.isfinite(out['quadrature_drift']) or out['quadrature_drift'] > 1e-6:
        reasons.append('volume_quadrature')
    # Every outer sphere must agree, independently of the low-order asymptotic
    # coefficient fit. Matter tails or an unresolved flux still fail this gate.
    jscale=max(1.,abs(summary['J_volume']))
    out['angular_momentum_surface_error']=max(abs(value-summary['J_volume']) for value in summary['J_surfaces'])
    if (not np.isfinite(summary['J_surfaces']).all()
            or not np.isfinite(summary['J_surface_quadrature_drift'])
            or out['angular_momentum_surface_error'] > equation_tol*jscale
            or summary['J_surface_quadrature_drift'] > equation_tol*jscale):
        reasons.append('angular_momentum_balance')
    if abs(summary['M_ADM_estimate']-summary['M_Komar_volume']) > 1e-6*max(1., abs(summary['M_ADM_estimate'])):
        reasons.append('mass_balance')
    # The finite-radius fit has truncation error even for a resolved metric.
    # Compare independent endpoint, lapse and volume masses at the same gate.
    if abs(summary['M_ADM_estimate']-summary['M_lapse_estimate']) > 1e-6*max(1.,abs(summary['M_ADM_estimate'])):
        reasons.append('mass_lapse_balance')
    if not np.isfinite(summary['M_endpoint_quadrature_drift']) or summary['M_endpoint_quadrature_drift'] > 1e-6:
        reasons.append('mass_endpoint_quadrature')
    for ratios in summary['scalar_tail_ratios']:
        if not localized_tail(ratios,tail_tol):
            reasons.append('scalar_localization')
            break
    if independent:
        geom = RingGeometry(problem, u)
        checks = []
        for radius in problem.length*np.array([.02, .05, .15, .5, 1., 2., 4.]):
            for theta in (.25, .8, 1.3):
                checks.append(dict(geom.independent([0., radius*np.sin(theta), 0., radius*np.cos(theta)]),
                                   radius=float(radius),theta=theta))
            checks.append(dict(geom.independent([0.,0.,0.,radius]),radius=float(radius),theta=0.))
        out['offgrid_einstein_max'] = max(v['einstein_max'] for v in checks)
        out['offgrid_kg_max'] = max(v['kg_max'] for v in checks)
        for name,key in (('worst_kg_point','kg_max'),('worst_einstein_point','einstein_max')):
            worst=max(checks,key=lambda row:row[key])
            out[name]={k:worst[k] for k in ('radius','theta',key)}
        out['offgrid_intrinsic_kg_max']=max(v.get('kg_intrinsic_max',0.) for v in checks)
        out['kg_coordinate_difference']=max(v.get('kg_coordinate_difference',0.) for v in checks)
        if max(out['offgrid_einstein_max'], out['offgrid_kg_max']) > equation_tol:
            reasons.append('independent_equations')
        if max(out['offgrid_intrinsic_kg_max'],out['kg_coordinate_difference']) > equation_tol:
            reasons.append('intrinsic_kg_crosscheck')
    if not all(np.isfinite(out[k]) for k in ('M_ADM_estimate', 'M_lapse_estimate', 'M_Komar_volume', 'J_volume', 'J_asymptotic_estimate', 'gtt_max')):
        reasons.append('nonfinite_observables')
    out.update(verdict='PASS' if not reasons else 'REJECT', reasons=reasons)
    return out


def converged_records(records, *, tolerance=1e-6):
    if len(records) != 3 or any(r.get('verdict') != 'PASS' for r in records):
        return False, None
    a, b = records[-2:]
    keys = ('M_ADM_estimate', 'J_volume', 'dragging_max')
    length = max(a.get('length_scale',1.),b.get('length_scale',1.))
    scales = dict(M_ADM_estimate=length,J_volume=length**2,dragging_max=1/length)
    if not all(np.isfinite(r[k]) for r in (a,b) for k in keys):
        return False,None
    # Mixed absolute/relative convergence: a roundoff-sized zero has no useful
    # relative scale. Dimensional floors are 64 eps in the problem's L units.
    drift = max(max(0.,abs(b[k]-a[k])-64*np.finfo(float).eps*scales[k])
                /max(abs(b[k]),abs(a[k]),1e-300) for k in keys)
    return bool(np.isfinite(drift) and drift <= tolerance), float(drift)
