# Ring spacetimes and spin transport — status

Updated **2026-11-02 (MSK)**. Branch: `feature/optimisation`.

The minimal-exotic-matter wormhole optimisation campaign remains paused.
This separate regular-centre scalar-ring study reuses its JAX/Newton core.
**The stronger-ring timing audit, concentric gapped field recovery and
between-ring particle experiment are complete and accepted.** Every original
physical acceptance limit is unchanged. Earlier failed studies remain rejected
in their immutable archives.

**The omega=0.70 single ring has now been interpolated onto Cartesian
GRTeclyn grids and evolved in full 3+1.** Both short, unperturbed pilots
finished; no long-time stability claim. See [EVOLUTION.md](EVOLUTION.md).

## Live and queue

**Live:** `railgun-ring070-export-n192-20261102`, second GPU node/card 0,
source `fcb5ce624`, started **10:05:32 MSK**. Cartesian 200^3 padded cube;
JAX derivative compilation/core certification, no cell rate yet and no
3+1 time yet. ETA **0.20 h, about 10:18 MSK**; hard cap **0.5 h,
10:35:32 MSK**. GPU context present, no other occupant.

**Regressions complete:** `railgun-richardson-regression-20261102`,
**10:03:50–10:04:17 MSK**, exit 0, **31 passed in 24.63 s**.

**Approved queue:** one certified 192^3 export, inspectable t=0 preflight,
then the full launch preflight and one t<=2 evolution. Stop on failed checks.
The final 192^3 Richardson go was received November 2. Same frozen binary
and physics, four threads, 160 GiB, 0.5 h per job; checkpoints OFF, full
frames, keep-last three plotfiles. No other grids or longer runs.

Last scratch check, second GPU node, **2026-11-02 10:06 MSK**: `_cache/`
**47 MB**, 96^3 pilot **709 MB**, 128^3 pilot **1.7 GB**, **545 GB free**.
Exactly three plotfiles per pilot retained as approved. No checkpoints.
All original frames and slice caches remain on NFS; first node not listed.

## Cartesian ring evolution: first two-grid pilot complete

Source: accepted `frequency-deep/frequency_01/accepted.npz`, omega=0.70,
k=+1, m=1. Evolved with **RadialRecipe's canonical complex scalar**, sign +1,
Phi=chi_complex/sqrt(4 pi), Pi=+n.partial(Phi), correct rotational K_ij and
conformal connections. Box 32, no reflection symmetry or added perturbation,
fourth spatial derivatives, RK4, CCZ4, initial stationary lapse/shift followed
by 1+log/Gamma-driver gauge. Four CPU threads, 160 GiB, 0.5 h per GPU job.

- **96^3:** `ring070-n96-t2-r2-20261102`, **09:21:00–09:23:10 MSK
  (0.0361 h)**, exit 0, all frames rendered. One floating-point stop-boundary
  step reached 2.0066667; trust and figures use saved **t<=2** only.
- **128^3:** `ring070-n128-t2-20261102`, **09:35:54–09:39:05 MSK
  (0.0531 h)**, exit 0, exactly **t=2**, max_steps=400. All frames rendered.
- Both exports pass the new C6 core certificate and algebraic CCZ4 checks.
  Core Einstein/KG maxima 1.70e-10 / 1.13e-10; degree-comparison curvature
  8.60e-9, below the unchanged 1e-8 gate. Export det(h)/trace-A defects
  below 8.89e-16 / 4.05e-17. C++ t=0 charges match each export within 1e-10.
- Maximum finite-box charge drift through t=2: **0.068895% / 0.017787%**,
  a **3.8734-fold** reduction on refinement. Initial interior Hamiltonian
  L2: **1.0334e-4 / 3.4831e-5**; final: **2.4758e-4 / 8.2997e-5**.
  These interior errors shrink by **2.97 / 2.98**. Momentum errors also shrink.
  Boundary-contaminated whole-box norms are retained, not used for this claim.
- No NaN in either run's own evolution log; finite matter diagnostics.
  The imported ring and centre hole are visible in frame 0. The m=2 shape
  diagnostic stays below 7.1e-17 in these unperturbed, symmetric-grid tests;
  this does not excite or bound an unstable mode's growth rate.
- **22 GPU regressions pass** (including CUDA/float64 assertions), plus 14
  local analytic/preflight checks. Two exports, four zero-step startups and
  two evolutions consumed. The first startup remains explicitly refused for
  obsolete `hdf5_subpath`; removing it changed no physics or tolerances.

The portable archives are `studies/evolution-070-n96/` and
`studies/evolution-070-n128/`, under results/railgun. They contain actual
params, logs, t=0 preflight reports, source/core hashes, diagnostics and
selected numeric slice inputs. The refused startup has a separate immutable
archive. Summary: `reports/evolution-pilot-070.json`; comparison figure:
`figures/ring070-evolution-pilot.png`. Large initial cubes and the approved
last three plotfiles stay in the run/scratch tree; no frame was deleted.

Frozen CUDA binary: `main3d_ring070r2_3e6466ed_2026-11-02.ex`, source
`3e6466ed`, SHA256
`14c6dadf61899ad21773f8cbe9df589f2745b0907d3779218b9d890c7d8019bc`.
The four-thread CPU build finished at **08:51:40 MSK**, exit 0.
Git push/pull through `myfork` only; no SCP.

**Approved and in progress:** complete the **96^3 /
128^3 / 192^3 Richardson triplet**, following the spinning and Bondi papers.
Only 192^3 needs a new export and evolution. The same frozen binary, source,
box, gauge, timestep multiplier, physical duration and diagnostics are kept;
the prepared template differs from the actual 128^3 params only in N,
max_steps and run/data paths. The nine local convergence regressions pass.
See [studies/evolution_richardson_070.json](studies/evolution_richardson_070.json).

Report Ham/Mom L0 pair orders in the fixed physical sphere r<8 at
t=0/0.5/1/1.5/2, then fit the generalized unequal-ratio Richardson order,
continuum value and estimated finest-grid error for Q, its change, matter J
and integrated scalar amplitude. Same-sign resolved differences are required;
unresolved/oscillatory triples do not get an invented order. **The existing
two-grid improvements are not a Richardson convergence result.** The
three-grid report and figure remain pending, with no fabricated third member.

A larger-domain check, longer evolutions and explicit small nonaxisymmetric
perturbations remain separate requirements for a dynamical-stability study.
Only the bounded 192^3 completion is authorised; no stability-study run
is queued. Earlier stationary/particle results remain below.

The November 1 field/particle close-out also passed **45 targeted CUDA
tests** (6+39), following the preceding 37-test correction suite. Their
reports and execution evidence remain in the immutable result package.

## Primary target: concentric rings with a clear annular channel

**Accepted:** independent fields k1=+1, k2=-12, equal particle masses m=1,
even parity, one common centre and equatorial plane, zero total angular
momentum. These are diffuse scalar fields, not solid torus walls.
Effective edges use **Eulerian energy density below 1e-6 of each component's
own peak**. No exact-vacuum claim.

Three fresh grids **192x16 / 224x18 / 256x20** pass the coupled field,
unused Einstein, intrinsic/Cartesian Klein–Gordon, boundary, tail, quadrature,
charge/flux and observable-convergence checks. Maximum finite-sphere J error
across the grids is **7.19e-14**, against the unchanged **1e-8** gate.
On the finest grid:

- M_ADM=1.053808110837; component angular momenta
  **-0.991960985480 / +0.991960985480**.
- J_volume=-4.44e-16; independently measured J_infinity=-1.09e-14.
  Interior max |w|=0.00435161: zero net spin does not remove local dragging.
- Density peaks near rho=6.22088 and 150.83809. The effective matter gap is
  **33.297341139 < rho < 40.908024688**, width **7.610683549**.
- The sampled common three-grid tube is
  **35.200012026 < rho < 39.005353801**, **-10 <= z <= +10**.
- Finest off-grid Einstein/KG maxima: **5.08e-13 / 2.83e-14**.
  Final observable drift 7.26e-10; charge/edge drifts 1.16e-13 / 1.04e-12.

Archive: [annular-validated-k12](../../results/railgun/studies/annular-validated-k12/).
Figure: [validated rings and gap](../../results/railgun/figures/annular-rings-validated.png).

## Particles between the two rings

**Accepted:** all **eight** full TD-MPD tracks reach z=-10 from z=+10.
Launch rho=37.102682914, reference axial speed -0.5, spin 0/+0.001/-0.001
and a background/spin reversal, each at RK tolerances 2e-11 / 2e-12.
All controls have the same spin-corrected Killing energy
**E=1.125108820447**; launch energy mismatch is 2.22e-16.

Every one of 1001 samples per track stays in the validated annular tube.
Actual path rho ranges **36.404424334–37.102682914**. Maximum component
densities relative to their own source peaks are **9.42e-8 / 1.74e-7**,
both below 1e-6. Density is reconstructed from Cartesian scalar derivatives
and the actual factored metric, independently of the equatorial screen.

Worst normalised invariant drift: **4.11e-13**, against 1e-9.
Maximum RK timing/position differences: **5.69e-14 / 2.85e-14**, against
1e-7. Background/spin reversal passes. Finest coordinate arrival times:
zero spin 42.12626592286; +z spin 42.12626771656; -z spin 42.12626412917.
The +z minus -z timing split is **3.58739e-6**.

This establishes finite passage through the matter gap. It does not establish
asymptotic escape, long-term trapping, energy gain or dynamical stability.

Archive: [annular-transit-k12](../../results/railgun/studies/annular-transit-k12/).
Figure: [actual paths and matter exposure](../../results/railgun/figures/annular-transit-k12.png).

## Stronger single-ring finite spin selection

**Accepted:** the omega=0.73 source and Cartesian core certificate are
hash-checked and reused. At equal **E=0.880293764772**, launch z=+1 toward
z=-10, spin magnitude 0.001: +z spin reaches the target, -z spin first turns
at **z=-9.999842477545**, and zero spin reaches the target. The ring has
negative J, so +z is against its spin and -z is with it.

All saved full-track conservation gates pass. The initial two-RK comparison
was insufficient for two near-threshold arrival times; the original failed
studies remain unchanged. The independent axial first-integral audit now
passes all **656 full Cartesian MPD substitution/invariant checks**. Its
maximum equation defect is **1.32e-14**. Every nonmarginal saved finest
track agrees with the independent phase time within **5.29e-8**, below 1e-7.
The last two order-16/order-32 phase comparisons are **4.512e-12**.

Cumulative evidence: **34 MPD tracks**, **34 scalar phase quadratures**,
656 full MPD substitution points. The last polish adds only two scalar
integrals, no new MPD track or substitution point. Exact-threshold marginal
contacts retain height/conservation checks but carry no arrival-time claim.
The accepted result is finite target-versus-turnaround selection, not a
spin-selective escape result.

Archive: [strong-uphill-073-validated](../../results/railgun/studies/strong-uphill-073-validated/).
Figure: [strong-ring finite selection](../../results/railgun/figures/strong-uphill-073.png).

## Numerical fixes and unchanged acceptance contract

- `regular_dragging.py` solves **w=(1-s)^3 H**, H degree nx, with all
  interior momentum equations retained and analytically divided by (1-s)^3.
  The angular infinity condition and its projected next-order radial condition
  remove uncontrolled endpoint modes. Direct H-coefficient transfer preserves
  infinity information during refinement. Fresh Jacobians and Newton 1e-14
  are used. Zero J is measured independently at infinity and in the volume;
  it is not hardcoded through a quintic falloff. Cartesian metric-ratio AD
  verifies every finite-sphere flux. Actual factored-field volume charges are
  cross-checked against nodal quadrature before acceptance.
- `axial_reduction.py` supplies the aligned-axis TD-MPD first integrals.
  Extended-precision spectral evaluation and cancellation-free turning
  differences allow an independent phase calculation. Full Cartesian MPD
  substitution verifies the reduction, including transverse curvature.
  `axial_phase_polish.py` refines only the two inadequate coarse quadratures.
- `annular_transit.py` refuses an unvalidated or non-archived field, checks the
  common three-grid tube, matches Killing energies and records actual
  per-component matter exposure along each path. Off-axis motion keeps an
  inner stopping radius; it does not require a Cartesian origin patch.
- Through-centre axial motion uses `corridor.py`: a certified two-dimensional
  fit in rho^2,z^2, a C2 join, degree comparison and independent curvature/KG
  checks. A signed-axis curve alone is not used to infer transverse curvature.

Field equations/unused constraints/charge and flux: **1e-8**. Spectral tails,
three-grid observable/component-charge/edge drift and matter cutoff:
**1e-6**. Particle invariant/SSC/timelike checks: **1e-9**. Nonmarginal axial
timing: **1e-7**, height **1e-8**. Annular timing/position/reversal: **1e-7**.
Failed checks stop a recovery; no acceptance limit was relaxed.

Equations and definitions: [EQUATIONS.md](EQUATIONS.md).
Commands, budgets and reproduction: [RUNNING.md](RUNNING.md).
Source: `grteclyn-wrapper/src/grteclyn_wrapper/optimisation/railgun/`;
shared device/Jacobian/Newton core: `optimisation/solver/`.

## Earlier accepted baselines and remaining research

- Spherical baseline: 56x8/72x10/96x12, independent areal-radius ODE agreement
  in mass/frequency 5.48e-8 / 1.12e-8. Archive: `spherical-validated/`.
- Weak pure k=1 ring: 72x10/96x12/128x16, M=0.971450813143,
  J=-0.992014330336, omega=0.932692332164. Integer-winding two-field homotopy
  removes the k=0 component before pure-ring validation. Archives:
  `ring-validated/`, `ring-profile/`, `ring-transit/`, `uphill-transit/`.
- Overlapping zero-J k1=+1/k2=-2 baseline is accepted as a stationary field,
  but fails the annular-gap geometry. Archive: `counter-rotation/`.
- Single-ring frequency continuation accepts omega=0.70 on
  96x12/128x16/160x20: minimum lapse 0.42146, maximum shift/lapse 0.51034,
  maximum g_tt=-0.136716. No sampled ergoregion. Omega=0.67 fails Newton on
  the first grid; no physical maximum spin or branch termination is established.
  Archives: `frequency-073-refined/`, `frequency-deep/`.
- Six linear seeds pass two-grid tests: new k=+2,m=2.5 and m=3 even fields,
  and a k=+1,m=1 odd field, on the weak k=1 metric. These are separate-field
  homotopy starts, **not accepted mixed-mass or stacked spacetimes**.
  Archive: `branch-seeds/`. No nonlinear seed recovery is authorised.

Next work requires a separately bounded proposal and go: nonlinear heavy-inner
or odd-parity homotopy, subsequent outer -6/-8 seeding only after a pure heavy
inner ring passes, stronger compactness continuation, asymptotic scattering
or dynamical stability. No automatic lower-frequency, higher-grid or new-field
run is queued. Winding remains integer; no fractional-k interpolation.

These are regular-centre, one-ended Einstein–complex-scalar configurations
with canonical independent matter fields and no phantom support. The phase
convention is exp(i omega t+i k phi), giving J_i=-k_i Q_i. Independent fields
add stress tensors without harmonic interference. Zero total J removes the
leading exterior spin term, not all exterior rotational multipoles. An
axis-touching ergoregion is excluded by a regular positive lapse; ergoregions
must be tested off axis. A stationary metric supplies no unspecified source
of Killing-energy gain. Scalar modes are not polarised spinning wavepackets.
Stability remains `not_assessed`.

## Saved evidence and packaging

`results/railgun/figures/` contains images only; `reports/` contains standalone
JSON/TSV and regression reports; `studies/` contains self-contained numerical
archives, execution logs, configurations and SHA-256 manifests. The current
summary is [completed-experiments.json](../../results/railgun/reports/completed-experiments.json).
The [package README](../../results/railgun/README.md) indexes accepted and
rejected studies and supplies figure commands. Earlier cubic-tau, quintic and
precision failures stay explicitly rejected; none is promoted retrospectively.

Run `grteclyn-wrapper/.venv/bin/python research/railgun/verify_pack.py` to
check the complete inventory and every immutable per-study checksum.
