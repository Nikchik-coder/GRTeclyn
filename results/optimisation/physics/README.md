# Stationary mechanism and trade-offs

The saved D0, D21 and D30 solutions reduce the volume-integrated exoticity
by localising the scalar variation near the throat. The violating region
becomes much narrower, but its peak becomes stronger. This lowers the search
objective without improving every measure of traversability.

The comparison holds the equatorial throat radius R_e, angular momentum J
and asymmetry fixed within each pair. D0 uses its analytic static reference;
D21 and D30 use the archived spinning solutions. In particular, this D21
reference has J = 1.0138. It is not the J = 1 classical evolution used in
the instability-growth figure. `sources.json` records the inputs and hashes.
All calculations use the saved stationary fields, with no new GPU evolution.

## Results

Ratios below divide the potential-bearing value by its own V = 0 reference.
Full values and throat geometry are in `summary.tsv`.

| Quantity | D0 | D21 | D30 |
|---|---:|---:|---:|
| Total exoticity X | 0.376 | 0.394 | 0.439 |
| Proper width containing the central 90% of X | 0.0204 | 0.0238 | 0.0377 |
| Peak radial NEC violation | 3.75 | 3.43 | 2.46 |
| Magnitude of equatorial ray-integrated NEC | 1.42 | 1.39 | 1.33 |
| Peak equatorial tides, local speed v = 0.5 | 6.57 | 5.93 | 3.87 |
| Equatorial light transit, endpoints at ±10 R_e | 1.180 | 1.167 | 1.146 |

The scalar excursion between the ends also decreases. Its remaining change
occurs over a short distance, producing steeper gradients. Angular gradients
remain small: these solutions concentrate the violation into a thin radial
region rather than an equatorial ring. The throat area changes by less than
0.6% at fixed R_e, and the rotating throats become slightly less oblate.

Light transit is longer for endpoints at ±5, ±10 and ±20 R_e; the percentage
depends on that choice (`endpoint_checks.json`). These are finite crossing
times, not a comparison with a flat-space shortcut. The asymptotic redshift
is fixed by the common asymmetry. The interior photon-energy profiles differ.

## Definitions

- The throat is the minimum-area constant-eta surface used by `exoticity.throat`.
  The signed equatorial proper distance ell is zero there. In the two-dimensional
  NEC map, ell labels that same eta surface at every angle; it is not the
  proper radial distance at each latitude. R_A is its area radius, sqrt(A/4pi).
- X = |VIQ|/R_e is the existing radial volume-integral objective. The profile
  labelled dX/d(ell/R_e) is the positive, angularly integrated contribution
  per equatorial proper distance. Its integral over ell/R_e equals X.
  The central-90% width runs between the 5% and 95% cumulative contributions
  over both complete ends, including the long classical tails outside the plots.
- Local null energy condition (NEC) deficits are positive magnitudes. The null
  vector has unit energy in the local zero-angular-momentum observer's frame.
  Radial and angular deficits are the squared corresponding orthonormal
  scalar gradients divided by 4pi. The directional maximum is their sum.
  The potential term cancels from a null contraction, so these diagnostics
  measure its indirect effect on the scalar and geometry.
- Ray-integrated NEC instead uses unit conserved Killing energy at positive
  infinity. It integrates along the complete zero-angular-momentum null
  ray, on the equator or axis, and is reported as a positive magnitude times
  R_e. It need not decrease when the volume integral decreases.
- Tides are the largest absolute eigenvalue of the equatorial electric
  Riemann tensor in the radially boosted local observer's frame, multiplied
  by R_e squared. We report the maximum over ell/R_e in [-10, 10] at fixed
  local speeds v = 0 and 0.5. A fixed-speed scan is not a freely falling
  traveller's integrated tidal exposure.
- Flight time integrates dt/dell = 1/alpha along the zero-angular-momentum
  equatorial or axial null geodesic. Each ray has endpoints at its own proper
  distances ±10 R_e from the throat. The coordinate t is normalized to the
  clock at positive infinity in both models; it is not either endpoint's
  local proper time. Photon energy relative to that infinity is 1/alpha.
- Local NEC and tidal peaks are sought within the same radial interval.
  Peak searches refine sampled maxima; photon-energy extrema are sampled
  over radius and latitude. Lengths include the saved physical scale sigma,
  angular velocity scales as 1/sigma, and curvature as 1/sigma squared.

## Checks and scope

`convergence.json` compares doubled radial quadrature and profile sampling,
with tighter null-ray integration tolerances. The integral, transit, width
and refined tidal diagnostics change by less than 2e-4 relative (the
acceptance threshold). `angular_checks.json` checks the volume integral with
32, 64 and 128 angular Gauss points; production uses 64. Near-zero
angular-gradient relative differences are not used as accuracy claims.

`field_checks.json` compares the archived D0/D30 150x30 and 180x36 fields
against the selected 210x42 fields. These refinements accepted interpolated
fields without Newton updates. Their close agreement checks interpolation
and differentiated observables; it is not an independent demonstration of
continuum convergence. D21 has only its selected fine-grid field in this
comparison. These post-processing checks do not replace the background
constraint audits or repair the unresolved stability screening.

The tests cover exact Ellis scalar gradients, null NEC, transit and tides;
dimensional scaling; and drainhole transit by an independent quadrature.
`tidal_crosscheck.json` additionally compares D0 tides against independent
finite differences of the spherical proper-distance metric. Its error is
scaled by max(|tidal eigenvalue|, 1/R_e squared), avoiding division by a
vanishing eigenvalue. The existing exact-limit `check_tidal` also passes.

## Rebuild

From the repository root, using the wrapper environment:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.optimisation.commands.compare_backgrounds
MPLCONFIGDIR=/tmp/grteclyn-mpl grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.optimisation.plot_physics
grteclyn-wrapper/.venv/bin/python -m pytest grteclyn-wrapper/tests/optimisation/test_diagnostics.py -q
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.optimisation.checks.check_tidal
```

The six `*_profiles.npz` files contain dimensionless arrays consumed by the
plotter. Tables, hashes and checks stay in this directory. The article's
physics section uses `../figures/mechanism_d21.{png,pdf}`, in blue and black,
and a comparison table generated from `../article/ledger_physics.tsv`.
The article claims checker compares that ledger against `summary.tsv` and
checks the source hashes and numerical diagnostics before generating macros.
The redundant `nec_distribution_d21` map and `stationary_tradeoffs` plot
were removed; the plotter now produces only the mechanism figure.
