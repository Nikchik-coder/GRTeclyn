# Regular-centre scalar rings: equations and numerical contract

## Matter and metric

Use G=c=1, signature (-+++), and independent complex fields
`chi_a = A_a(r,theta) exp(i omega_a t + i k_a phi)`. Their action is

```text
S = (16 pi)^-1 integral sqrt(-g) [R - 2 sum_a (|d chi_a|^2 + U_a)] d^4x
U_a = m_a^2 |chi_a|^2 + lambda4_a |chi_a|^4 + lambda6_a |chi_a|^6.
```

The implemented self-interactions have nonnegative coefficients. Variation gives

```text
R_mn = 2 sum_a Re(d_m chi_a d_n chi_a*) + sum_a U_a g_mn
box chi_a = (m_a^2 + 2 lambda4_a A_a^2 + 3 lambda6_a A_a^4) chi_a.
```

There is no phantom scalar. The domain has one regular centre and one flat end.
The metric is

```text
ds^2 = -exp(f) dt^2 + B^2 exp(-f) [exp(nu) (dr^2+r^2 dtheta^2)
                                  + r^2 sin^2(theta) (dphi-w dt)^2]
nu = N sin^2(theta), B=1+b.
```

Its elementary-flatness condition is automatic on the axis. This is the
regular-centre counterpart of the existing general quasi-isotropic ansatz;
the interior vacuum equations are `matter_residual_forms` at `eta0=0`. Its
canonical sources are independently transcribed for each field, and checked
against the existing equations before coupling them. The chosen imposed rows
are `E_f, E_w, E_B, E_Nr` and one KG row per field. `E_c` and `E19` are left
unimposed everywhere. A separate Cartesian reconstruction checks **all**
Ricci components and each covariant KG equation, independent of these rows.

This coordinate ansatz is also used for regular rotating boson stars in
[Kleihaus, Kunz and List (2005)](https://arxiv.org/abs/gr-qc/0505143).
Its metric-function names differ; the implementation uses the definitions above.

## Regular scalar amplitudes and parity

Let `s=(r-L)/(r+L)` and `y=cos(2 theta)`. The unknown field is

```text
A = sin^a(theta) cos^p(theta) q(s,y), a=|k|, p=0 (even) or 1 (odd).
```

Its regular centre behaviour is `q=O(r^(a+p))`. The scalar amplitude is pinned
at a stated finite radius in q, including for odd parity. Each pin adds one
unknown frequency. The equations do not fix the position of a density maximum.

For single-field frequency continuation, replace the amplitude border by
`omega - omega_target = 0`, keeping the same unknowns and differential
equations. The amplitude at the anchor is then measured. Require positive
component charge above the declared branch floor and no resolved scalar
nodes, in addition to every independent equation and three-grid gate;
otherwise the trivial vacuum could pass at any imposed frequency.

For even parity the angular KG operator, without the B-gradient terms, is

```text
4(1-y^2) q_yy - [(4a+6)y+4a+2] q_y - a(a+1) q.
```

For odd parity, analytically factoring `cos(theta)` gives

```text
4(1-y^2) q_yy - [(4a+10)y+4a-2] q_y - (a+1)(a+2) q.
```

The odd row also gains `2(1-y)(B_y/B)q`. Sources use polynomial combinations
of `cos(theta)q`, so neither the axis nor equator requires division by a
vanishing parity factor. For example, with z=cos(theta)q,

```text
z^2 = (1+y) q^2/2
z z_y = (1+y) q q_y/2 + q^2/4
(1-y^2) z_y^2 = (1+y)(1-y^2) q_y^2/2
                + (1-y^2) q q_y/2 + (1-y) q^2/8.
```

The implementation includes mass-only and positive quartic/sextic interactions;
it makes no assertion that a stacked equilibrium exists.

## Grid, boundaries and equation count

Tensor Chebyshev–Lobatto grids cover `s,y in [-1,1]`. At infinity,
`f=w=N=b=q_a=0`. At the centre, `f_s=w_s=b_s=0`, `N=0`; a nonzero-degree
scalar has `q=0`, and an even k=0 scalar has `q_s=0`. Angular smoothness and
parity are encoded in y and the factors above; regular PDE limits are imposed
at both angular endpoints. Centre isotropy and higher-order smoothness are
checked through near-centre off-grid Einstein residuals, not inferred merely
from the boundary rows.

With F scalar fields and P=(nx+1)(ny+1) nodes, there are `(4+F)P+F` unknowns
and equations. The F borders determine frequencies. An optional total-J
condition adds one unknown, the final field's log amplitude, and one J row.
This requires at least two fields; J=0 requires opposite winding signs.

## Charges and validation

Define `Omega_a=omega_a+k_a w`. In this normalisation the positive-frequency
Noether charge and angular momentum are

```text
Q_a = (4 pi)^-1 integral Omega_a A_a^2 / alpha dV
J_a = -k_a Q_a.
```

For a regular centre there is no throat contribution. The independent exterior
check is `w=2J/r^3+O(r^-4)`. Finite-radius spatial and lapse coefficient fits
are reported as diagnostics. Acceptance uses the endpoint ADM/lapse masses
and exact angular-momentum surface integrals derived below. The Komar volume
integrand, after full-sphere angular integration, is

```text
B^3 exp(nu-f) r^2 [sum_a (2 omega_a Omega_a exp(-f) A_a^2 - U_a)] dr dmu.
```

The workflow compares volume/asymptotic J, volume/spatial mass and doubled
quadrature. It checks bound frequencies, tails, spectral coefficients,
boundary rows, unused constraints and off-grid Einstein/KG equations. Finer
grids require two actual Newton corrections from perturbed metric data.
Only three passing grids and converged observables produce `accepted.npz`.
The word accepted denotes these finite numerical tests, not a stability proof.

The independent spherical reference solves the areal-radius mass, lapse and
KG ODEs as a boundary-value problem and converts its seed to isotropic radius.
It is a k=0 numerical cross-check, not a rotating solution. Its finite exterior
error still needs an extent comparison; no published rotating branch has yet
been reproduced by this implementation.

## Curvature, axial profiles and spin transport

Off-grid fields use differentiable Chebyshev interpolation. The metric is
reconstructed in Cartesian coordinates. The combination
`(1-exp(N rho^2/r^2))/rho^2` is evaluated using its analytic axis limit.
Scalar components use `[(x+i sign(k)y)/r]^abs(k)` rather than an azimuthal
angle, preserving their Cartesian derivatives on the axis. The base interpolant excludes the exact origin. Ordinary profiles start at
positive radius and trajectories retain an inner stop. The separately
certified Cartesian core described below can extend a trajectory through it.

The Riemann convention is
`R^a_bcd=partial_c Gamma^a_bd-partial_d Gamma^a_bc+Gamma^a_ec Gamma^e_bd-Gamma^a_ed Gamma^e_bc`.
Flat, Schwarzschild and rotating Kerr curvature provide analytic benchmarks.
Axial profiles report the Eulerian electric and magnetic tidal components;
`H_zz=R_(z)(0)(x)(y)` gives `F_z/S_z=-H_zz` at linear spin for unit test mass.
This definition avoids treating a coordinate dragging gradient as an exact force.

The MPD integrator evolves x, p and the antisymmetric spin tensor with the
Tulczyjew–Dixon condition `p_m S^mn=0` and its full momentum–velocity relation.
Its Killing integral is `p_m xi^m + S^mn partial_m xi_n/2`.
See the [MPD formulation](https://link.springer.com/article/10.1140/epjc/s10052-023-11970-5).
It monitors mass, spin, supplementary condition, Killing energy/angular momentum
and timelike velocity. A spin/curvature bound and an inner/outer radius stop
the integration. Controls have equal spin-corrected launch energy. Reaching a
finite outer radius is labelled as such, not as escape to infinity.

## Three safeguards added after the spherical benchmark

### Angular momentum at finite radius

The exact surface integral for the stated metric and phase convention is

```text
J(R) = -R^4/4 integral_0^1 B^3 exp(-2f) (1-mu^2) partial_R w dmu,
mu=cos(theta).
```

It follows from `(8 pi)^-1 integral K_ij phi^i s^j dA`, with
`K_rphi=-gamma_phiphi partial_r w/(2 alpha)`. The nu factors cancel between
the unit normal and area element. For `w=2J/r^3` in the asymptotic flat
limit the integral gives J, including its sign. All four outer spheres
R/L=22,30,42,60 must agree with the independently integrated matter J
within the existing 1e-8 gate; doubled angular quadrature must also agree.
Nonnegligible matter tails or unresolved flux therefore still fail.

The three-term fit to `w=sum_(n=3)^5 c_n/r^n` is retained as a diagnostic,
but is no longer used as the angular-momentum balance gate. Its truncation
error rejected the first ring continuation even though the exact surface
flux and matter charge agreed. The original rejected records are preserved.

### Mass at compactified infinity

Write the spatial metric as `gamma_ij=C delta_ij+D(delta_ij-e_phi_i e_phi_j)`,
where `C=B^2 exp(-f)` and `D=C(exp(nu)-1)`. The Cartesian ADM surface integral
on a coordinate sphere reduces to

```text
M_ADM(R) = R^2/4 integral_0^1 [-2 partial_R C - partial_R D + D/R] dmu.
```

If f,b,N vanish at s=1, their leading 1/r coefficients are -2L times
their first s derivatives. Taking the limit gives

```text
M_ADM = L integral_0^1 [f_s - 2 b_s - (1-mu^2) N_s]_(s=1) dmu,
M_lapse = L integral_0^1 [f_s]_(s=1) dmu.
```

The N term is retained rather than assuming it has no 1/r contribution.
Endpoint ADM mass must agree with the independently integrated Komar mass,
and with the lapse mass, at the existing 1e-6 tolerance. Doubled angular
quadrature is checked too. The old finite-radius fits and their drift stay
in the reports, but fit truncation error is no longer an acceptance gate.
An independent regression evaluates the literal Cartesian ADM integrand
from differentiated metric components and extrapolates its finite-radius
values to compare with the endpoint formula. Saved ring states that fail
KG or surface-J checks remain rejected after this measurement correction.

### KG, winding and the regular core

Every off-grid maximum now carries its radius and polar angle. A separate
intrinsic KG calculation evaluates

```text
[partial_r(B r² sin(theta) partial_r A)
 + partial_theta(B sin(theta) partial_theta A)] / [B³ exp(nu-f) r² sin(theta)]
+ [(omega+k w)² exp(-f) - k² exp(f)/(B² r² sin²(theta)) - U'(A)/(2A)] A.
```

This is compared with the Cartesian covariant KG residual, including the phase
and odd-parity sign. The intrinsic check is used off-axis; the Cartesian check
retains the analytic axis limit. Neither is substituted for a failing result.

Winding is a discrete model choice. A k=0 amplitude is never relabelled as a
k=1 amplitude. The two-field initializer solves a nodeless, bound radial KG
eigenmode of integer degree on the accepted spherical background. The coupled
homotopy then uses separate amplitude/frequency borders. A bound linear mode
and a connected nonlinear path both need to exist; neither follows just from
adding a second field. Hydrogenic states are not exact self-consistent
Schrödinger–Poisson seeds. The final small k=0 block is removed together with
its eigenfrequency before a pure-ring solve. The broader multistate setting
has precedents, e.g. [rotating multistate boson stars](https://arxiv.org/abs/1906.00420).

For transport across the centre, the regular core fits f, C=B²exp(-f), w and
H=C*N*exprel(nu)/r², as functions of (rho²,z²). It reconstructs

```text
g_ij = (C+H rho²) delta_ij - H v_i v_j, v=(-y,x,0),
g_ti = -C w v_i, g_tt=-exp(f)+C w² rho².
```

Scalar coefficients q/r^(|k|+parity) multiply the Cartesian polynomial
`(x+i sign(k)y)^|k| z^parity`. Thus both transverse and axial derivatives exist
at the origin. A smooth join alone does not solve Einstein's equations:
independent equations, curvature matching, polynomial-order comparison and
metric signature are checked on the centre, axis and joining region. A failed
certificate retains the inner stopping sphere. This is more information than
a one-dimensional signed-z metric curve, which cannot determine all MPD forces.

### Rotating two-field seed and zero-J border

The second field on a rotating background does not separate into a radial
spherical eigenproblem. With its metric held fixed and its amplitude
linearised at zero, the parity-factored KG equation has the discrete form

```text
[A0 + diag(2 k w) omega + I omega^2] q = 0.
```

Here A0 contains the full radial/angular differentiation, metric gradients,
mass and k²w² terms; every row is divided by its positive omega² coefficient
`B² r² exp(nu-2f)`. Radial endpoint values vanish for nonzero regular degree.
The companion matrix `[0,I; -A0,-diag(2kw)]` supplies real, positive,
sub-mass-frequency candidates. Reject sign-changing resolved modes and
require both a relative eigen-residual below 1e-8 and agreement with the
printed two-dimensional KG equation. A constant-w manufactured metric tests
the exact frequency shift `delta omega=-k delta w`; an angular perturbation
tests coupling that a radial-only seed would miss.

Nonlinear continuation holds the k1=1 amplitude fixed while increasing the
k2=-2 pin. Both individual charges change with the metric. Near zero total
J, promote the second pin to an unknown log amplitude and impose
`-k1 Q1-k2 Q2=0`. Three fresh perturbed Newton recoveries then recheck all
independent equations and both individual charges. Exterior projection onto
`1` and `5 mu²-1`, with weight `(1-mu²) dmu`, measures coordinate dipole and
octupole angular coefficients. Their radial decay is reported rather than
assumed; these coefficients are not labelled invariant multipole moments.

### Concentric annular channel

The required study geometry has two coplanar rings around the same centre.
An axial trajectory through the central hole does not test the annulus
between them. Define each effective matter edge using its own Eulerian
energy-density peak and the agreed relative cutoff 1e-6. Let R1_out be the
last outward crossing for field 1, and R2_in the first inward crossing for
field 2 on the equatorial radial profile. Require R1_out < R2_in and both
densities below their separate cutoffs throughout the intervening interval.
Using the first/last crossings also rejects a spurious gap at a radial node.
Missing tail crossings, boundary peaks, nonfinite data and unresolved gap
sampling fail the screen. Three-dimensional channel checks and full off-axis
particle tracks follow only after a suitable self-consistent background.

These are effective edges, not compact support. Ordinary massive boson-star
fields have exponential tails; see the asymptotic scalar behaviour in
[the rotating-boson-star study](https://link.springer.com/article/10.1140/epjc/s10052-024-12664-2).
The accepted 1e-6 tolerance allows these tails. No field clipping, radial
translation of a solved field or redrawn surface can create a physical gap.

The proposed higher-winding screen solves only linear modes on the fixed
accepted inner metric. It scales each outer mode's charge to cancel the fixed
inner J, then measures the density-edge gap on two grids. Those seeds remain
`validated=False`; their backreaction and two-field field equations are not
solved. The explicit GPU eigensolver uses
[`jax.lax.linalg.eig` with cuSOLVER](https://docs.jax.dev/en/latest/_autosummary/jax.lax.linalg.eig.html),
with right eigenvectors only. CPU-reference agreement is a regression check;
the screen requires GPU eigendecomposition.

### Experimental cubic dragging falloff

`dragging_falloff.py` represents w=(1-s)^3 H(s,y), with H of radial degree
nx-3. The physical w still has degree nx. Three zero auxiliary coordinates
preserve the vector size. They replace the infinity and two outermost
interior w-PDE rows; the regular-origin derivative condition remains.
All printed PDEs, including the two omitted rows, must pass independently.
This is a spectral tau boundary treatment, not an accepted repair yet.

Finite-sphere angular momentum uses the original Komar formula, with an
analytic derivative of the factored polynomial, and a separate Cartesian
metric-ratio AD derivative. At phi=0, w=-g_ty/(rho*g_yy) and the integrand
factor B^3 exp(-2f)=g_yy^(3/2)/alpha. Require their agreement, every sphere's
balance with volume J, and the original 1e-8 limit. The leading coefficient
at literal infinity must also give the same J and have no anisotropic r^-3
part. Cartesian curvature and intrinsic KG checks use the factored metric.
Use 1-s=2L/(r+L) directly when evaluating the far tail.

The explicit factored state format has its own model identifier and loader;
the standard loader refuses it. It retains both the factored coordinates
and physical nodal vector. No prior rejected archive is changed. The
planned recovery retains the original three grids, density gap and finite
height channel, and all earlier acceptance limits.
