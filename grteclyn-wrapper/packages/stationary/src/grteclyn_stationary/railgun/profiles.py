"""Observer-defined axial curvature and spin-force diagnostics, not a force ansatz."""
from __future__ import annotations

from grteclyn_stationary.provenance import source_revision
import numpy as np
from scipy.integrate import cumulative_trapezoid


def matter_sampler(geometry):
    """Eulerian energy density and scalar amplitude, including axis gradients."""
    jax,xp=geometry.jax,geometry.xp
    def sample(point):
        g=geometry.metric(point)
        alpha=1/xp.sqrt(-xp.linalg.inv(g)[0,0])
        beta=xp.linalg.solve(g[1:,1:],g[0,1:])
        normal=xp.concatenate((xp.ones(1),-beta))/alpha
        inverse=xp.linalg.inv(g[1:,1:])
        density,amplitude=xp.zeros(()),xp.zeros(())
        for i,field in enumerate(geometry.fields):
            scalar=lambda x:geometry.scalar(x,i)
            value=scalar(point)
            gradient=jax.jacfwd(scalar)(point)
            a2=xp.sum(value*value)
            potential=field.mass**2*a2+field.quartic*a2*a2+field.sextic*a2**3
            density+=(xp.sum((gradient@normal)**2)
                     +xp.einsum('ij,ai,aj->',inverse,gradient[:,1:],gradient[:,1:])+potential)/(8*xp.pi)
            amplitude+=a2
        return xp.array([amplitude,density])
    return jax.jit(sample)


def axial_profile(geometry, *, z_min=.1, z_max=30., samples=101):
    if not (np.isfinite([z_min,z_max]).all() and z_min < z_max and samples >= 3):
        raise ValueError('finite z_min<z_max and at least three samples required')
    if z_min<=0<=z_max and not getattr(geometry,'regular_origin',False):
        raise ValueError('a signed profile through zero requires a certified regular core')
    rows=[]
    sample_matter=matter_sampler(geometry)
    for z in np.linspace(z_min,z_max,samples):
        point=np.array([0.,0.,0.,z])
        g,_,riem,_=map(np.asarray,geometry.tensors(point))
        low=np.einsum('ae,ebcd->abcd',g,riem)
        alpha=np.sqrt(-1/np.linalg.inv(g)[0,0])
        beta=np.linalg.solve(g[1:,1:],g[0,1:])
        tetrad=np.zeros((4,4))
        tetrad[0]=np.r_[1.,-beta]/alpha
        tetrad[1:,1:]=np.linalg.inv(np.linalg.cholesky(g[1:,1:]))
        orth=np.einsum('ia,jb,kc,ld,abcd->ijkl',tetrad,tetrad,tetrad,tetrad,low)
        # H_zz = R_(z)(0)(x)(y), because epsilon_xyz=+1.
        # The linear-in-spin MPD force is F_z/S_z=-H_zz for unit test mass.
        einstein=geometry.independent(point)
        radius=abs(z)
        s=(radius-geometry.length)/(radius+geometry.length)
        amplitude,density=map(float,np.asarray(sample_matter(point)))
        shift=np.sqrt(max(0.,float(beta@g[1:,1:]@beta)))/alpha
        rows.append([z,np.sqrt(g[3,3]),alpha,g[0,0],
                     float(geometry.sample('w',s,1.)),orth[3,0,3,0],orth[3,0,1,2],
                     -orth[3,0,1,2],einstein['einstein_max'],einstein['kg_max'],
                     amplitude,density,shift])
    data=np.array(rows)
    proper=cumulative_trapezoid(data[:,1],data[:,0],initial=0.)
    return np.column_stack((data[:,0],proper,data[:,2:])), dict(
        columns=['z','proper_distance_from_z_min','lapse','g_tt','coordinate_dragging_omega',
                 'electric_tidal_zz','magnetic_tidal_zz','linear_spin_force_z_per_spin',
                 'independent_einstein_max','independent_kg_max',
                 'scalar_amplitude_squared','Eulerian_matter_energy_density','shift_norm_over_lapse'],
        observer='Eulerian orthonormal frame; right-handed Cartesian spatial triad',
        spin_force='Pole-dipole, linear spin, instantaneously comoving, unit test mass',
        range=[z_min,z_max],samples=samples,
        scope='Signed axis; the origin requires a certified regular core; no vacuum assumption')


def run_profile(source,directory,*,z_min=-15.,z_max=15.,samples=301,
                certify_core=True,corridor_radius=.4,corridor_degree=6):
    """Bounded stage A: certify the core, then save signed axial/equatorial data."""
    import hashlib
    import time
    from pathlib import Path
    from grteclyn_stationary.railgun.workflow import load_state, write_json
    from grteclyn_stationary.railgun.geometry import RingGeometry
    from grteclyn_stationary.railgun.corridor import CartesianCorridor
    from grteclyn_stationary.railgun.diagnostics import observables
    p,u,metadata=load_state(source)
    if not metadata.get('validated') or p.jax.devices()[0].platform!='gpu':
        raise ValueError('profile requires an accepted background and GPU')
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    started=time.monotonic()
    manifest=dict(source_sha256=hashlib.sha256(Path(source).read_bytes()).hexdigest(),
                  commit=source_revision(),
                  platform='gpu',float64=bool(p.jax.config.jax_enable_x64),
                  z_min=z_min,z_max=z_max,samples=samples,certify_core=certify_core,
                  corridor_radius=corridor_radius,corridor_degree=corridor_degree,
                  stability='not_assessed')
    write_json(directory/'manifest.json',manifest)
    print(f'[profile] GPU={p.jax.devices()[0]} float64={manifest["float64"]}; measuring observables',flush=True)
    summary=observables(p,u)
    geometry=RingGeometry(p,u)
    if certify_core:
        print('[profile] fitting and certifying Cartesian core',flush=True)
        geometry=CartesianCorridor(geometry,radius=corridor_radius,degree=corridor_degree)
        certificate=geometry.certify()
        write_json(directory/'corridor.json',certificate)
        print(f'[profile] core accepted={certificate["accepted"]} maxima={certificate["maxima"]}',flush=True)
        if not certificate['accepted']:
            outcome=dict(accepted=False,reason='core_certification',observables=summary,
                         seconds=time.monotonic()-started)
            write_json(directory/'outcome.json',outcome);return outcome
    print('[profile] sampling signed axial curvature',flush=True)
    data,description=axial_profile(geometry,z_min=z_min,z_max=z_max,samples=samples)
    np.savetxt(directory/'axis.tsv',data,delimiter='\t',header='\t'.join(description['columns']))
    write_json(directory/'profile.json',description)
    # A direct Cartesian derivative also captures nonzero gradient energy on
    # the k=1 axis; vanishing scalar amplitude does not define an empty bore.
    sampler=matter_sampler(geometry)
    radii=np.linspace(0. if certify_core else .01,2*max(abs(z_min),abs(z_max)),601)
    equator=np.array([[r,*np.asarray(sampler(np.array([0.,r,0.,0.])))] for r in radii])
    np.savetxt(directory/'equator.tsv',equator,delimiter='\t',
               header='rho\tscalar_amplitude_squared\tEulerian_matter_energy_density')
    peak=int(np.argmax(equator[:,2]))
    outcome=dict(accepted=bool(np.isfinite(data).all() and np.isfinite(equator).all()
                              and np.max(data[:,8:10])<=1e-8),
                 observables=summary,equatorial_density_peak=dict(radius=float(equator[peak,0]),
                 density=float(equator[peak,2]),radial_sampling=float(radii[1]-radii[0])),
                 axis_equation_max=float(np.max(data[:,8:10])),
                 axis_lapse_min=float(np.min(data[:,2])),axis_lapse_at_zero=float(np.interp(0.,data[:,0],data[:,2])) if z_min<=0<=z_max else None,
                 ergoregion_sampled=summary['gtt_max']>0,
                 interpretation='A spin-selective valve is an untested hypothesis; matched-energy asymptotic speeds agree.',
                 seconds=time.monotonic()-started)
    write_json(directory/'outcome.json',outcome)
    print(f'[profile] accepted={outcome["accepted"]} seconds={outcome["seconds"]:.2f}',flush=True)
    return outcome
