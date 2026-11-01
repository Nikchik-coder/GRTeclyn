"""Observer-defined axial curvature and spin-force diagnostics, not a force ansatz."""
from __future__ import annotations

import numpy as np
from scipy.integrate import cumulative_trapezoid


def axial_profile(geometry, *, z_min=.1, z_max=30., samples=101):
    if not (0 < z_min < z_max and samples >= 3):
        raise ValueError('0<z_min<z_max and at least three samples required')
    rows=[]
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
        s=(z-geometry.length)/(z+geometry.length)
        rows.append([z,np.sqrt(g[3,3]),alpha,g[0,0],
                     float(geometry.sample('w',s,1.)),orth[3,0,3,0],orth[3,0,1,2],
                     -orth[3,0,1,2],einstein['einstein_max'],einstein['kg_max']])
    data=np.array(rows)
    proper=cumulative_trapezoid(data[:,1],data[:,0],initial=0.)
    return np.column_stack((data[:,0],proper,data[:,2:])), dict(
        columns=['z','proper_distance_from_z_min','lapse','g_tt','coordinate_dragging_omega',
                 'electric_tidal_zz','magnetic_tidal_zz','linear_spin_force_z_per_spin',
                 'independent_einstein_max','independent_kg_max'],
        observer='Eulerian orthonormal frame; right-handed Cartesian spatial triad',
        spin_force='Pole-dipole, linear spin, instantaneously comoving, unit test mass',
        range=[z_min,z_max],samples=samples,
        scope='Positive axis away from origin; no uniform-field or vacuum assumption')
