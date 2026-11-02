# Ring spacetimes and spin transport — status

Updated **2026-11-02 (MSK)**. Branch: `feature/optimisation`.

The minimal-exotic-matter wormhole optimisation campaign remains paused.
This separate regular-centre scalar-ring study reuses its JAX/Newton core.
**The stronger-ring timing audit, concentric gapped field recovery and
between-ring particle experiment are complete and accepted.** Every original
physical acceptance limit is unchanged. Earlier failed studies remain rejected
in their immutable archives.

**The omega=0.70 single ring has now been interpolated onto Cartesian
GRTeclyn grids and evolved in full 3+1.** The three-resolution Richardson
study through t=2 is complete; no long-time stability claim. See [EVOLUTION.md](EVOLUTION.md).

## Live and queue

**Stopped:** `railgun-ergoregion-amplitude-20261102`, second GPU node/card 0,
**17:56:39–17:59:36 MSK**, exit 2, 0.0492 h including tests. All **23 GPU
regressions pass**. All three initial reproduction solves converge in two
updates and pass every original field gate; recovered frequencies are
0.700000000000697 / 0.700000000000676 / 0.700000000000639. The added
strong-field comparison rejected differing sampled extrema (shift/lapse
change 1.15e-5): those samples are at different positions on each grid.
This is an error in the new comparison, not evidence of inconsistent fields.
No amplitude increase was attempted. Three solves spent; all provisional
fields retained, no accepted file written. Both GPUs idle. The stopped run
stays unchanged. Prepare a common-physical-point comparison and a separately
approved continuation reusing these three solves; no automatic restart.
Checkpoints **OFF**. Scratch: 14 GB retained, 531 GB free, unchanged.
Single-ring ergoregion search,
[ergoregion_amplitude.json](studies/ergoregion_amplitude.json). Start from the
hash-checked accepted omega=0.70 state; k=1, m=1 and the matter model stay fixed.
First reproduce it on radial scale 2.5, with the amplitude pinned at its scalar
maximum: radius 1.202893, amplitude 0.307398668. The old radius-5 pin measured
only 0.015689536; it is not the scalar peak. Then take eight 6% pin increases,
up to 0.489946775, solving frequency as an unknown. The radius stays fixed.
Use secant guesses after two accepted points, fresh Jacobians, Newton 1e-14,
at least two updates and at most 30 iterations per solve. Three grids per
point: 128x16 / 160x20 / 192x24; maximum 27 solves, including the initial
three-grid reproduction. Stop at rejection or a resolved sampled ergoregion.
Original 1e-8 equation/flux and 1e-6 tail/observable checks stay unchanged;
additional lapse/g_tt/shift/frequency convergence checks run before writing
an accepted state. Positive g_tt must occur on all three grids with a margin
larger than their spread and 1e-8. No automatic k=2 branch or extra solves.
Eleven CPU-only new/existing preparation and guard checks pass;
the new CUDA border test and existing field tests passed in the stopped job.
Four CPU threads, 160 GiB, 0.5 h total, Jacobian chunks 128; retain logs
and all attempted fields. Scratch at launch: 14 GB retained in four finished
evolutions plus the 47 MB cache; 531 GB free, three plotfiles per evolution,
zero checkpoints. No scratch removal. A frequency
turning point is a hypothesis, not established by the rejected omega=0.67
Newton solve. A fixed-radius amplitude pin can turn too; no guaranteed
ergoregion or nonsingular Jacobian is assumed.

**GPU evolution complete:** `railgun-ring070-evolve-n192-t50-20261102`,
second GPU node/card 0, source `b64bf13ff`, ran from **11:13:00 to
12:56:40 MSK** (1.728 h including final image processing), exit 0,
exactly **t=50**, 15000 steps. Final evolution speed **29.36 code units/h**.
No evolution is queued; the new stationary job is listed above. Its own log contains no NaN/Inf
or fatal error. **Checkpoints OFF**, explicitly chosen November 2.

Same certified t=0 cube and frozen binary, N=192, box 32. Physics, timestep,
gauge and 25-step plot cadence unchanged; only duration/step limit and paths
change. Two single-thread image workers, four evolution CPU threads, 160 GiB
address-space cap per process, keep-last three plotfiles. No evolution is queued.
Eleven local preparation/spawn/preflight regressions pass; actual-cube
CPU-only preparation passes both checkpoint policies. The image-worker
entry point guards spawn and waits for workers before the final drain.
Scope: [evolution_long_070.json](studies/evolution_long_070.json).
The original box can affect the ring before t=50; this is exploratory,
not a new long-time Richardson or isolated-ring stability result.

**Movie processing:** replacement CPU job `railgun-ring070-t50-movies-r2-20261102`
follows the successful finished manifest and final consumer drain.
It requires all 601 slices in each of the 16 fields and finite, complete
diagnostics through t=50. It redraws into `movie_render/frames` using fixed
colour scales, then encodes the full set into the run's `movies/`; every
original frame and cache remains untouched. Two CPU cores, 16 GiB address-space
cap, three-hour render timeout; no GPU work.
Encoded frame counts/durations are checked and consecutive decoded contact
sheets are saved in `movie_render/qa` for visual review. These are exploratory
finite-box movies, not an isolated-ring stability certification. The first job
stopped at a filename-order check after step 9999, with all 601 slices present.
Numeric sorting fixes the check; four CPU completion/cadence/invalid-data
tests pass, including the five-digit step case. Full result packing and movie
visual review follow the rendering job.

**Previous run complete:** the final 192^3 Richardson job finished at
**10:24:52 MSK**, exit 0, exactly **t=2**, all frames processed. Evolution
speed was approximately **30.4 code units/h**. All authorised budgets are
spent. Its budget is closed; the t=50 run has its separate go.

Last scratch check, second GPU node, **2026-11-02 12:56 MSK**: `_cache/`
**47 MB**, old 96^3 **709 MB**, 128^3 **1.7 GB**, 192^3/t2 **5.6 GB**,
completed 192^3/t50 **5.6 GB**; **532 GB free**. All four runs retain three
plotfiles. Zero checkpoints. No plotfile or frame was removed manually.
All original frames and caches stay on NFS; first node not listed.

**Start verified:** full preflight passed, imported Q/J match the original
192^3 t=0 values. Actual preflight and live frame 0 are byte-identical to the
previously inspected reference PNG, SHA256
`c876db701540a2fe40d941ccc0d8467fafb0d68a6b1e5ea3ee0522a1fd9790c1`.
Both spawned image workers are active; 45 plotfiles processed through step
1100, boundary-flux rows advancing. Recent throughput 9.85 s/plot versus
production about 10.4 s/plot; the initial processing lag remains bounded.
See `results/railgun/reports/evolution-long-startup.json`.

**192^3 sequence:** 31 GPU regressions passed in 24.63 s; certified export
**10:05:32–10:12:36 MSK**, eight million padded cells / 1.856 GB; inspectable
t=0 preflight **10:14:34–10:14:59 MSK**; full-preflight/evolution/drain
**10:17:54–10:24:52 MSK (0.1161 h)**. The initial ring/hole image was checked.
Export det(h)/tr A defects 1.12e-15 / 4.67e-17; imported Q matches its export
within 1.27e-11. The source, frozen binary, core and physics are unchanged.
Actual template differences are only N=192, max_steps=600 and run/data paths.
Grid SHA256 `64a606f3f248ecd939d4088c28116776847c2a6b0831d572b0d8ef67ec61bd58`.
No NaN/Inf in its own evolution log; every matter diagnostic is finite.

## Spatial interpretation of the initial omega=0.70 ring

The completed spatial guide is `results/railgun/figures/single-ring/ring070-physics.png`
and `.svg`; profiles/extrema are in `reports/ring070-physics.json` and `.tsv`.
NumPy/SciPy analysis of the existing accepted state, no new solve or GPU work.
The origin lapse is **0.434391**, verified directly against every angular
endpoint node: **26.06 minutes per distant hour**, not the previously quoted
minimum-lapse value. The minimum lapse **0.421456** is at rho=0.8193.
For clocks held at fixed coordinates the rate is sqrt(-g_tt), with a smaller
minimum **0.369727** at rho=1.06354: **22.18 minutes per distant hour**.
Angular dragging peaks at the origin, whereas |shift|/lapse peaks at
rho=1.23702, value **0.510407**. Maximum g_tt=-0.136698; no sampled ergoregion.
The search covers the compactified radial domain and refines the extrema;
coordinates are not proper distances. One equatorial ring map attaches the
clock/dragging measurements to each named location. The central particle
route is described as axial, perpendicular to the map. Render checked.

## Three-grid Richardson result: 96^3 / 128^3 / 192^3

Completed at fixed box 32, source omega=0.70, t<=2, no perturbation.
[Measured order table](../../results/railgun/reports/evolution-richardson-070.md)
and [full extrapolations](../../results/railgun/reports/evolution-richardson-070.json)
come from actual matched t=0/0.5/1/1.5/2 samples. Ham/Mom are L0 L2 norms
inside the same physical r<8 sphere; whole-box boundary-contaminated norms
remain in every archive and are not used for the interior convergence claim.

- At t=2 the Ham order is **3.80 / 4.01** and Mom **3.62 / 3.83**
  for 96→128 / 128→192. The finer pair moves toward fourth order.
- Signed three-grid charge-change differences give **p=4.677** at t=2
  (4.689→4.677 over t=0.5→2). Matter J gives **p=4.269** at t=2.
  Orders use the unequal spacings, not a fixed ratio or assumed p=4.
- Maximum charge drift is **0.068895% / 0.017787% / 0.0024917%**.
  Finest final interior Ham/Mom L2=**1.63065e-5 / 1.10072e-5**.
- The estimated fine-grid Q error at t=2 is 3.529e-5; extrapolated
  Q=1.3063251693. The three-point continuum charge-change estimate is
  +2.745e-6, not exact conservation. These are asymptotic estimates,
  not independent error bounds. Initial charge/amplitude differences at
  t=0 are below the diagnostic precision gate and have no fitted order.
- All three finished archives pass matching source/binary/core/parameter
  and checksum checks. Nine manufactured/identity tests and 31 GPU checks
  pass. No missing data or unresolved order is filled with synthetic values.

Archive: `results/railgun/studies/evolution-070-n192/`, alongside the original
two immutable pilot archives. Three-grid figure: `figures/evolution/ring070-evolution-convergence.png`
under results/railgun, rebuilt from the portable diagnostics. The completed
budget is [evolution_richardson_070.json](studies/evolution_richardson_070.json).
This establishes short-duration numerical convergence of the import/evolution;
long-time stability remains untested. A larger-domain, longer, explicitly
perturbed three-resolution study requires a separate proposal and go.

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
`figures/evolution/ring070-evolution-pilot.png`. Large initial cubes and the approved
last three plotfiles stay in the run/scratch tree; no frame was deleted.

Frozen CUDA binary: `main3d_ring070r2_3e6466ed_2026-11-02.ex`, source
`3e6466ed`, SHA256
`14c6dadf61899ad21773f8cbe9df589f2745b0907d3779218b9d890c7d8019bc`.
The four-thread CPU build finished at **08:51:40 MSK**, exit 0.
Git push/pull through `myfork` only; no SCP.

The final 192^3 completion and generalized Richardson analysis are now done,
as reported above. Every earlier stationary/particle result remains below.

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
Figure: [validated rings and gap](../../results/railgun/figures/two-rings/annular-rings-validated.png).

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
Figure: [actual paths and matter exposure](../../results/railgun/figures/particles/annular-transit-k12.png).

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
Figure: [strong-ring finite selection](../../results/railgun/figures/particles/strong-uphill-073.png).

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

`results/railgun/figures/` groups images into `single-ring/`, `two-rings/`,
`particles/` and `evolution/`, with a linked README index. Earlier overlapping
and provisional results have separate subfolders. `reports/` contains standalone
JSON/TSV and regression reports; `studies/` contains self-contained numerical
archives, execution logs, configurations and SHA-256 manifests. The current
summary is [completed-experiments.json](../../results/railgun/reports/completed-experiments.json).
The [package README](../../results/railgun/README.md) indexes accepted and
rejected studies and supplies figure commands. Earlier cubic-tau, quintic and
precision failures stay explicitly rejected; none is promoted retrospectively.

Run `grteclyn-wrapper/.venv/bin/python research/railgun/verify_pack.py` to
check the complete inventory and every immutable per-study checksum.
