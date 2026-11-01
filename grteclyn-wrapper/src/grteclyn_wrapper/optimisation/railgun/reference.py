"""Independent spherical Einstein--KG BVP in areal radius.

Used only to benchmark/seed the k=0 collocation problem. This is not a rotating
ring approximation. The first-order mass/lapse ODEs are independently imposed,
not projections of the quasi-isotropic elliptic rows. Outer-boundary error
must be measured by increasing extent; an analytic tail is only a seed.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import cumulative_trapezoid, solve_bvp


def spherical_reference(central_amplitude=.1, *, mass=1., extent=80., tol=1e-9):
    if not (central_amplitude > 0 and mass > 0 and extent > 10/mass and tol > 0):
        raise ValueError('positive amplitude/mass/tolerance and extent>10/mass required')
    radius = np.geomspace(1e-5/mass, extent, 600)
    width = 1/(mass*np.sqrt(central_amplitude))
    phi = central_amplitude*np.exp(-radius**2/(2*width**2))
    guess_mass = central_amplitude**2*width**3*(1-np.exp(-(radius/width)**3))/2
    guess = np.array([guess_mass, -.2*central_amplitude/np.sqrt(1+(radius/width)**2),
                      phi, -radius/width**2*phi])
    def rhs(r, y, p):
        m, logalpha, chi, dchi = y
        omega = mass/(1+np.exp(-p[0]))
        a2 = 1/(1-2*m/r)
        harmonic = omega**2*np.exp(-2*logalpha)*chi**2
        gradient = dchi*dchi/a2
        pot = mass*mass*chi*chi
        dm = .5*r*r*(harmonic+gradient+pot)
        dlapse = (m+.5*r**3*(harmonic+gradient-pot))/(r*(r-2*m))
        da = a2*(dm/r-m/r**2)
        d2chi = -(2/r+dlapse-da)*dchi+a2*(mass**2-omega**2*np.exp(-2*logalpha))*chi
        return np.array([dm, dlapse, dchi, d2chi])
    def bc(lo, hi, p):
        omega = mass/(1+np.exp(-p[0]))
        kappa = np.sqrt(mass*mass-omega*omega)
        return np.array([lo[0], lo[3], lo[2]-central_amplitude,
                         hi[1]-.5*np.log(1-2*hi[0]/extent),
                         hi[3]+(kappa+1/extent)*hi[2]])
    solution = solve_bvp(rhs, bc, radius, guess, p=[np.log(.95/.05)],
                         tol=tol, max_nodes=12000)
    if not solution.success:
        raise RuntimeError(f'independent spherical BVP failed: {solution.message}')
    sample = np.geomspace(radius[0], extent, 5000)
    m, logalpha, chi, dchi = solution.sol(sample)
    if np.any(2*m >= sample) or np.any(chi < -1e-8):
        raise RuntimeError('spherical BVP found a horizon or an excited/nodal branch')
    total_mass = float(m[-1])
    outer_iso = (extent-total_mass+np.sqrt(extent*(extent-2*total_mass)))/2
    integral = cumulative_trapezoid(1/np.sqrt(1-2*m/sample), np.log(sample), initial=0.)
    iso = outer_iso*np.exp(integral-integral[-1])
    return dict(radius=sample, isotropic_radius=iso, chi=chi, logalpha=logalpha,
                mass=total_mass, omega=float(mass/(1+np.exp(-solution.p[0]))),
                central_amplitude=central_amplitude, scalar_mass=mass, extent=extent,
                bvp_residual=float(np.max(solution.rms_residuals)),
                outer_amplitude=float(abs(chi[-1])))


def reference_seed(problem, reference):
    if len(problem.fields) != 1 or problem.fields[0].degree != 0:
        raise ValueError('spherical seed requires one even k=0 field')
    r = problem.r[1:]
    source_r = reference['isotropic_radius']
    m, omega = reference['mass'], reference['omega']
    values = {tag: np.zeros(problem.shape) for tag in problem.tags}
    alpha = np.exp(np.interp(r, source_r, reference['logalpha']))
    areal = np.interp(r, source_r, reference['radius'])
    chi = np.interp(r, source_r, reference['chi'])
    exterior = r > source_r[-1]
    alpha[exterior] = (1-m/(2*r[exterior]))/(1+m/(2*r[exterior]))
    areal[exterior] = r[exterior]*(1+m/(2*r[exterior]))**2
    kappa = np.sqrt(problem.fields[0].mass**2-omega**2)
    chi[exterior] = reference['chi'][-1]*source_r[-1]/r[exterior]*np.exp(-kappa*(r[exterior]-source_r[-1]))
    conformal = np.empty_like(r)
    conformal[:-1] = areal[:-1]/r[:-1]
    conformal[-1] = source_r[0]**-1*reference['radius'][0]
    for key, val in (('f', 2*np.log(alpha)), ('b', alpha*conformal-1), ('q0', chi)):
        values[key][1:] = val[:, None]
    return problem.pack(values, [omega])
