# Ring spacetimes and spin transport — status

Updated **2026-11-01 (MSK)**. Branch: `feature/optimisation`.

**Decision:** the minimal-exotic-matter optimisation campaign is paused. This
separate study reuses its JAX/Newton infrastructure for regular-centre scalar
rings. The spherical baseline, pure k=1 ring and a zero-net-spin k1=1/k2=-2
state are validated. Single-ring axial spin-dependent transit is validated;
between-ring transport, stacked states and stability remain to test.

**Results packaging:** rendered figures live in `results/railgun/figures/`,
standalone JSON/TSV and regression reports in `results/railgun/reports/`,
and complete self-contained run archives in `results/railgun/studies/`.
`verify_pack.py` checks the package inventory and original study checksums.
The reorganisation preserved every archived file's contents.

**Primary target — clarified November 1:** two coplanar, concentric rings
with a shared centre and a resolved annular matter gap. The particle channel
must lie **outside the inner ring's outer edge and inside the outer ring's
inner edge**, rather than through the central hole. Effective edges use
Eulerian matter energy density at **1e-6 of each component's own peak**;
negligible tails are allowed. Require positive gap width and both component
densities below their separate thresholds across the channel. A finite-height
channel and an actual off-axis trajectory still need verification.
The current k1=1/k2=-2 stationary solution is an **overlapping baseline**:
it passes the field equations but **fails this geometry requirement**.
Its inner-component outer edge is about 29.88; the outer-component inner
edge is about 0.010 on the extended radial sample. Separate density peaks
near 5.89 and 7.77 do not create a gap. The target schematic is
`annular-gap-target.png`; it is not a solved configuration.

## Live and queue

**Live:** targeted GPU regressions started **19:30:01 MSK**, code `e5096e78`:
`railgun-axis-audit-gpu-tests-20261101` on second node/card 0 and
`railgun-regular-gpu-tests-20261101` on card 1. Each 0.5 h cap, hard
deadline **20:00 MSK**. Both corrected numerical jobs have explicit go
and follow only passing tests: at most 32 phase quadratures/656 MPD
substitution points on card 0; at most three 192x16/224x18/256x20 regular
operator recovery solves on card 1. All existing gates unchanged, four
threads/160 GiB/chunks 128/no AMR checkpoints. CPU development suite:
36 passed in 9.15 s. Scratch clean at **19:30 MSK**: 47 MB in `_cache/`,
535 GB free; first node not listed. No measured numerical-job ETA yet.

**Prior correction jobs completed:**

- Card 0: `railgun-strong-uphill-073-precision-20261101`, code `568eaac8`,
  **19:06:19–19:10:14 MSK (0.0653 h)**, exit 2. Exactly two new tracks
  (34 cumulative), rtol=2e-13. Both pass 1e-9 conservation and retain the
  same transmitted classifications, but timing differences from saved 2e-12
  controls are **1.88654e-7 / 2.03222e-7**, above unchanged 1e-7. Study
  **rejected**; no accepted stronger-ring selection or timing claim.
  Archive: `results/railgun/studies/strong-uphill-073-precision/`, including
  all 32 immutable originals under `original/`.
- Card 1: `railgun-annular-quintic-k12-20261101`, code `568eaac8`,
  **19:06:19–19:07:39 MSK (0.0222 h)**, exit 2. First 192x16 solve makes
  two updates. Original field, flux, gap and finite-height channel checks
  pass; finite-sphere J error 4.85538e-9, Cartesian crosscheck 5.86e-15,
  off-grid Einstein/KG maxima 4.57e-13 / 9.10e-14. Added leading infinity
  angular-mode residual **80.57967** exceeds 1e-6. Study **rejected**;
  later grids unattempted, no accepted export or off-axis particles.
  Archive: `results/railgun/studies/annular-quintic-k12/`.

The preceding targeted CUDA suites passed **18 + 34 = 52 tests** (18.02 /
16.63 s), code `153c53c6`; portable reports under `results/railgun/reports/`.
Each job used four CPU threads, 160 GiB, 0.5 h maximum, chunks 128,
no AMR checkpoints. All current approved correction work is finished;
no new GPU run is queued. No ETA. Scratch clean at **19:10 MSK**:
47 MB in `_cache/` only, 535 GB free; first node not listed.

**Next:** diagnose strong-ring timing sensitivity independently before another
track budget, and impose/test the regular infinity angular structure in the
annular solver before proposing another bounded recovery. The Newton residual
alone does not certify the tail: the independently measured leading angular
equation fails despite the tiny collocation residual. Original failed fields
remain rejected; all equation, timing and geometry gates remain
unchanged. No between-ring particle launch until a full background passes.

**Previous:** Strong-ring particles completed all 32
tracks, but the study is **rejected**: two nonmarginal timing comparisons
are 2.70803e-7 / 2.68702e-7 against 1e-7. All track conservation, reversal
and classification checks pass; worst normalised invariant drift 1.55e-10.
Code `0fd3b1e4`, **18:28:40–18:45:49 MSK (0.286 h)**, exit 2.
Archive: `results/railgun/studies/strong-uphill-073-initial/`. The separate
two-control audit is completed above; this original study stays rejected,
and no timing limit is relaxed.

The cubic annular falloff study is also **rejected** at its first 192x16
solve, despite finite-sphere J error 7.01e-10, Cartesian crosscheck 2.55e-14
and all original field/gap/channel checks passing. Its literal-infinity
coefficient gives J=2.32964e-4 and anisotropy=1.60936e-4, failing the added
asymptotic gate. Code `1f32594c`, **18:42:49–18:44:10 MSK (0.0225 h)**,
exit 2, one solve; later grids were not attempted. Archive:
`results/railgun/studies/annular-falloff-k12-cubic/`. Diagnose the correct
zero-total-J asymptotic representation before a new recovery; no particles
on this rejected background. All original constraints stay in force.
The preceding 25 GPU regressions passed in 6.68 s; report under reports/.

Scratch clean at **18:47 MSK**: 47 MB in `_cache/` only, 536 GB free;
first node not listed. No AMR checkpoints or plotfiles created. No ETA.

**Seed screen completed:** `railgun-branch-seeds-20261101`, second node/card 1,
code `dc576c85`, **18:39:30–18:39:42 MSK**, exit 0. All six mode problems
and all three two-grid frequency checks passed (max relative drift 2.62e-14).
Archive: `results/railgun/studies/branch-seeds/`. These are fixed-metric
unaccepted homotopy starts, not final mixed-mass or stacked geometries.

The core/profile passed at radius 0.4, degrees 6/8: code `078ee51f`,
**18:19:33–18:26:09 MSK**, 390 s numerical work. Core order-curvature
difference 2.65e-10, independent Einstein/KG maxima 1.70e-11 / 2.90e-12.
The preceding 21 targeted GPU checks passed in 76.48 s. The completed
profile is packed under `results/railgun/studies/strong-profile-073/`.
Scratch clean: 47 MB in `_cache/` only, 536 GB free at **18:28 MSK**;
first node not listed. No AMR checkpoints or plotfiles created.

**Deep continuation finished:** `railgun-frequency-deep-20261101`, code
`4d1c4d23`, **18:12:10–18:14:08 MSK (0.0328 h)**, exit 2. Omega=0.70
passed all three grids 96x12 / 128x16 / 160x20. Omega=0.67 failed Newton
on 96x12, with independent equation failures, and was retained rejected.
Four solves spent; no extra frequency or resolution attempted.
At 0.70, sampled maximum shift/lapse=0.510341166,
minimum lapse=0.421458671, maximum g_tt=-0.136716030,
M=1.261072102786, J=-1.306322429244; sampled ergoregion:
False. No maximum-spin or branch-termination claim.
Archive: `results/railgun/studies/frequency-deep/`.
Scratch clean at **18:17 MSK**: 47 MB in `_cache/` only, 537 GB free;
first node not listed. No AMR checkpoints or plotfiles created.

**Previous recovery:** `railgun-frequency-073-refined-20261101`, second node/card 0,
code `e7fed22c`, ran **17:45:27–17:47:04 MSK (0.0269 h)**, exit 0.
**omega=0.73 accepted on 96x12 / 128x16 / 160x20.** All three solves made
two fresh corrections; observable drift 1.16e-9 against 1e-6. The unimposed
constraint_c fell from 3.25009e-8 on the old 72x10 grid to 7.78e-10,
6.99e-11 and 2.01e-10 on the new grids, below the unchanged 1e-8 limit.
Only resolution changed. Final M=1.297346776244, J=-1.357170938561,
minimum sampled lapse=0.49280423, maximum shift/lapse=0.35420575 (35.42%),
maximum sampled g_tt=-0.21719481; no sampled ergoregion. Independent
Einstein/KG maxima 3.26e-11 / 1.44e-11 on the finest grid. The density peak
is near rho=1.44861. This is not a maximum-spin or stability result.
Archive: `results/railgun/studies/frequency-073-refined/`, including the
accepted field, all three grid states, provenance, diagnostics and log.
The original coarse rejection remains immutable in `studies/frequency-scan/`.
Figure: `results/railgun/figures/frequency-073-recovery.png`; every original
and refined constraint value is shown, including small nonmonotonic changes.

The separately approved deeper continuation and stronger-ring follow-ons
are recorded in the current live/queue block above.

**Previous frequency scan:** `railgun-frequency-scan-20261101`, second node/card 0,
code `023f4384`, ran **17:35:17–17:40:03 MSK (0.0794 h)**, exit 2.
**Four frequencies 0.85 / 0.82 / 0.79 / 0.76 passed all three grids.**
At 0.73, Newton converged but the unimposed constraint_c was **3.25009e-8
against 1e-8 on 72x10**. The scan stopped as approved; 13 solves spent,
0.70 and 0.67 not attempted. No tolerance was relaxed. This is not a physical
maximum. Last accepted M=1.313890770182, J=-1.379462933768, minimum sampled
lapse=0.55817553, maximum shift/lapse=0.25190704 (25.19%); no sampled
ergoregion. Independent Einstein/KG maxima 2.51e-11 / 2.76e-12 on 128x16.
The fixed-radius amplitude decreases along the stronger branch; it is
measured rather than imposed here. Archive: `results/railgun/studies/frequency-scan/`.
The preceding **31 GPU regressions passed in 24.87 s**
(**17:34:17–17:34:43 MSK**, code `1f4054a0`); portable report:
`results/railgun/reports/gpu_frequency_regression.json`.

**Previous scan:** `railgun-compactness-scan-20261101`, second node/card 0,
code `4445ce44`, ran **17:15:58–17:19:40 MSK (0.0617 h)**, exit 2.
Three pins **0.06 / 0.075 / 0.095 passed all three grids** (nine accepted
solves). The next pin 0.12 failed Newton line search on 72x10 and failed
independent equations; the scan stopped, with ten solves spent. Later
0.15 / 0.19 / 0.23 points were not attempted. This is not a physical maximum.
Last accepted omega=0.874052056468, M=1.198020886933, J=-1.241877125360,
minimum sampled lapse=0.78022047, peak shift/lapse=0.06178653 (6.18%).
No sampled ergoregion among accepted points. Archive:
`results/railgun/studies/compactness-scan/`, including all accepted states
and the rejected 0.12 state. The separately approved frequency continuation
completed with four accepted points, as reported above.

**Uphill experiment accepted after first-crossing audit:** 32 tracks,
raw code `4d40acbc`, **16:52:24–17:07:01 MSK**, followed by the event audit
code `786cf041`, **17:11:52–17:12:10 MSK**. At common energy
E=0.9255355443835863, +z spin reaches z=-10 at t=81.4993862174;
-z spin turns at z=-9.999772414807428, while the no-spin control reaches -10
at t=81.7834142908. The ring's J is negative, so -z is the aligned spin.
This is **finite endpoint selection, not escape or long-term trapping**.
All invariants and reversal/tolerance checks passed: worst normalised drift
1.08e-14; nonmarginal RK timing change 6.68e-10. Four raw destination events
were corrected using degree 5/7 interpolation, verified terminal invariants
and no added ring integrations; all originals remain under `original/`.
Exact-threshold marginal contacts cannot supply a transit-time or selection
claim. Archive: `results/railgun/studies/uphill-transit/`.
37 initial GPU regressions passed in 42.32 s, then five event/CUDA checks in
7.11 s; reports under `results/railgun/reports/`. The direct integrator now
resolves an earlier shallow crossing before its terminal turnaround.

**Requested follow-on experiments (November 1):**

- **Uphill finite-endpoint selection:** completed and accepted after event
  audit, as reported above. Config: `studies/uphill_transit.json`.
  Launch z=+1 toward z=-10 on the accepted pure ring; spin 0,
  +/-0.001, equal full spin-corrected Killing energy. Four energies include
  alpha(-10)+1e-7 and brackets derived from measured spin-dependent resting
  endpoint energies; two RK tolerances and background/spin reversal, 32
  tracks maximum. Stop at destination or the first true dz/dtau turnaround.
  Reaching -10 is a finite transit, not escape or long-term trapping. No
  selection effect is assumed in advance.
- **Compactness continuation:** amplitude scan completed with three accepted
  points and one rejection; the approved frequency scan follows above.
  Original `studies/compactness_scan.json` specified seven increasing
  pins 0.06..0.23, each freshly solved on 72x10 / 96x12 / 128x16, at most
  21 solves and 30 iterations each. Keep the existing equation/convergence
  gates, measure frequency, lapse, dragging and sampled g_tt, stop on failure
  or a validated sampled ergoregion. Neither omega=0.7 nor a particular
  dragging speed or timing enhancement is guaranteed. Stability stays open.
- **Mixed-mass concentric branch:** requested k1=+2, m1=2.5 or 3, outer
  k2=-6 or -8, m2=1, total J=0. Requires a new regular integer-winding
  seed/homotopy and three-grid validation before particles. The proposed
  radii are hypotheses; higher mass does not create compact support.
  Retain the agreed 1e-6 effective matter-gap criterion. Not launchable yet.
- **Stacked odd-parity branch:** existing `studies/stacked_odd.json` specifies
  the model, but needs a bound-mode continuation seed and fresh recovery.
  Odd scalar amplitude vanishes on the equator; its transverse gradient
  generally gives nonzero energy there and on parts of the axis. The new
  cylindrical density checker retains those derivatives. A matter-free
  equatorial slot or axial barrel cannot be inferred from parity alone.

These are separate experiments. The uphill and compactness launches above
now have their own concrete go; the mixed-mass and stacked branches do not.

**Completed:** `railgun-annular-correction-k12-20261101`, second node/card 0,
code `8946f146`, ran **16:27:12–16:28:22 MSK (0.0194 h)**, exit 2.
Two additional Newton updates reduced the scaled residual to 9.95e-17;
**the finest-grid angular-momentum surface check still failed**, 1.36332e-8
against 1e-8 at R=3000. Volume J=2.22e-16. The original and corrected
studies remain rejected; no accepted gapped background or particle launch.
Four cumulative solves; the extra correction budget is spent.
Archive: `results/railgun/studies/annular-correction-k12/`, all corrected fields,
diagnostics, profiles, log and provenance retained. **24 GPU regression checks
passed in 3.37 s**, **16:26:27–16:26:32 MSK**, exit 0; report
`results/railgun/reports/gpu_annular_correction_regression.json`.
Same physics and gates, four threads, 160 GiB, chunks 128, 0.5 h cap,
no AMR checkpoints. Both cards idle, no completion ETA or queued launch.
Scratch clean at **16:31 MSK**: 47 MB in `_cache/` only, 539 GB free;
first node not listed.

Completed `railgun-annular-recovery-k12-20261101`, second node/card 0,
code `121a9ef7`, ran **16:14:11–16:17:10 MSK (0.050 h)**, exit 2.
All three fresh Newton solves converged (6 / 4 / 4 updates). The 192x16 and
224x18 grids passed; **256x20 was rejected** by independent angular-momentum
surface balance: **1.33955e-8 against the unchanged 1e-8 gate**, on the
outermost R=3000 sphere. Volume J=6.69e-14. The discrepancy is under
investigation; no accepted background or particle launch follows from it.

Higher-precision direct barycentric flux evaluation still failed, and extra
Newton corrections did not repair it. Endpoint diagnostics show tiny nonzero
first/second compactified derivatives of w; contamination of its required
r^-3 asymptotics is a hypothesis to test, not an established repair.
Reports: `results/railgun/reports/annular-flux-diagnostic.json` and
`results/railgun/reports/annular-endpoint-diagnostic.json`. No tolerance was changed.

**The annular gap survived nonlinear backreaction on every grid:**
33.29734 < rho < 40.90802, width 7.61068 at the component-wise 1e-6 cutoff.
The sampled finite-height channel rho=35.20..39.01, z=-10..10 also passed;
max component densities below 2.90e-7 / 4.42e-7 of their own equatorial peaks.
Final independent Einstein/KG maxima 5.59e-13 / 2.68e-14. These are promising
provisional fields, not three-grid accepted data. No tolerance was changed.
Archive: `results/railgun/studies/annular-recovery-k12/`, all three states, density
and channel profiles, diagnostics, manifest, log and checksums retained.
Three solves maximum, L=50, total J=0, grids 192x16 / 224x18 / 256x20;
four threads, 160 GiB host cap, 0.5 h, chunks 128; no AMR checkpoints.
No different grid, winding, potential or tolerance is an automatic fallback.

**22 GPU regression checks passed in 3.60 s**, **16:13:51–16:13:57 MSK**,
exit 0, code `121a9ef7`: budgets/provenance/acceptance, correct J-border
promotion, component densities versus independent Cartesian AD, prior gap
tests and CUDA float64 placement. `results/railgun/reports/gpu_annular_regression.json`.
Scratch clean at **16:19 MSK**: 47 MB in `_cache/` only, 539 GB free;
first node not listed. Both cards idle; no ETA or queued physical run.

Completed `railgun-annular-gap-screen-20261101`, second node/card 0,
code `928bde26`, finished **13:22:52 MSK**, exit 0. Eight GPU eigenproblems
completed in 10.28 s (13 s including startup). Its nonlinear follow-on is
the separately approved k2=-12 recovery above.
At the agreed 1e-6 matter cutoff, k2=-4/-8 fail the gap screen; **k2=-12
and k2=-16 pass on 96x12 and 128x16**. Fixed-background candidate intervals:
**33.3107 < rho < 41.1737** (width **7.8630**) and
**33.3107 < rho < 90.9212** (width **57.6105**), respectively.
Frequency relative grid differences are 1.46e-14 / 2.69e-14; edge relative
changes 6.23e-11 / 6.08e-8. These are linear modes on the accepted inner
metric, with charge scaled to cancel the fixed inner spin. **They are not
accepted coupled two-field backgrounds.** Backreaction, three-grid nonlinear
validation and through-annulus particle passage remain uncomputed.
Archive: `results/railgun/studies/annular-gap-screen/`; all eight seeds, density
profiles, manifests, logs and checksums retained. Four threads, 160 GiB,
0.5 h cap; no AMR checkpoints. No scratch plotfiles were created.
Scratch clean at **15:56 MSK**: 47 MB in `_cache/` only, 539 GB free;
first node not listed.

All **nine gap/GPU eigenmode regression checks passed in 2.58 s**, ending
**13:21:02 MSK**, code `928bde26`. The first run had eight passes and one
incorrect fixture expectation about an unresolved boundary crossing; the
fixture was corrected, and the gap criterion stayed unchanged. Both logs
are retained. GPU cuSOLVER agrees with the host reference; spectral matter
density agrees with the independent archived Cartesian-derivative profile.

Run C `railgun-counter-rotation-20261101`, second node/card 0,
implementation `73b2aa30`, ran **12:55:48–13:00:33 MSK (0.079 h)**, exit 0.
**k1=+1, k2=-2, total-J=0 accepted on 72x10 / 96x12 / 128x16.**
Twelve Newton solves total, no amplitude splits; two fresh corrections on
every recovery grid. Final observable drift 7.62e-10; component-charge drift
2.54e-13. M_ADM=1.132946199392, component J=-0.773443320071468 /
+0.773443320071473, total J=4.66e-15. Interior max |w|=0.00225517;
no sampled ergoregion. Independent Einstein/KG maxima 1.86e-11 / 3.69e-12.
The exterior coordinate octupole decay order increases from 4.96 to 4.99;
this is a coordinate harmonic measurement, not an invariant moment claim.
Archive: `results/railgun/studies/counter-rotation/`. Three bound-mode/CUDA tests passed.
Four threads, 160 GiB, chunks 128, 0.5 h cap; no AMR checkpoints.
Scratch clean: 47 MB in `_cache/` only, 543 GB free at 13:00 MSK;
first node not listed. Both cards idle, no ETA or queued physical run.

Run B `railgun-ring-transit-20261101`, second node/card 0,
code `96c81edc`, ran **12:41:00–12:53:33 MSK (0.209 h)**, exit 0.
All **32 tracks reached z=-10 from z=+10**, crossing the certified centre.
Four controls, two RK tolerances, high-speed plus three E~1 cases;
maximum normalised conservation drift 1.90e-13, RK time difference 3.56e-13.
Reversing ring and spin gave zero measured axial/time difference.
At spin magnitude 0.001, fast transit t(+z spin)-t(-z spin)=-0.000581712663.
All sampled near-threshold controls transmitted: no spin valve demonstrated.
These are finite-radius transits, not numerical demonstrations of escape.
Archive: `results/railgun/studies/ring-transit/`; 16 GPU regression checks passed.
Four threads, 160 GiB, 0.5 h cap, no AMR checkpoints.
Scratch clean: 47 MB in `_cache/` only, 543 GB free at 12:54 MSK;
first node not listed.

Run A `railgun-ring-profile-20261101`, second node/card 0,
code `4c1e2085`, passed at **12:37:19 MSK**, after 0.072 h including compilation.
The degree 6/8 Cartesian core at radius 0.4 passed: maximum parent curvature
mismatch 2.88e-10; independent axial Einstein/KG maximum 4.73e-12.
Signed z=-15..15 and equatorial matter profiles are archived in
`results/railgun/studies/ring-profile/`. Density wall rho=6.25 (sampling 0.05),
minimum sampled lapse 0.88496, peak |omega|=0.0043558,
max shift/lapse=0.020482. max(g_tt)=-0.78289: no sampled ergoregion.
The scalar vanishes on the axis, but its transverse gradients carry energy.
All 11 targeted GPU profile/diagnostics/transport tests passed in 53.32 s.
Four threads, 160 GiB, 0.5 h cap; no AMR checkpoints.
Scratch clean: 47 MB in `_cache/` only, 543 GB free at 12:37 MSK;
the first node was not listed.

**Annular work:** diagnose and repair the distant-exterior angular-momentum accuracy
before another coupled recovery. Keep the independent 1e-8 balance gate.
The k2=-12 geometry already has a converged low-density annulus; changing
masses or adding repulsion is not the immediate response to this flux failure.
Then validate the gapped background and run matched off-axis particles within
its finite-height channel. The separately approved falloff recovery is
queued above; off-axis particles still need an accepted gapped field.
The completed screen configuration is `studies/annular_gap_screen.json`.
Off-axis launch/destination support passed four GPU checks in 4.09 s at
13:02:40 MSK: `results/railgun/reports/gpu_offaxis_regression.json`.
No physical between-ring trajectory is authorised or running.

**Completed:** `railgun-ring-refined-20261101`, second node/card 0, code
`58116d7a`, ran **12:03:19–12:06:14 MSK (0.049 h)**, exit 0.
**Pure k=1 ring accepted on 72x10 / 96x12 / 128x16**, with two fresh Newton
updates on each pure-ring grid. Final observable drift **3.52e-10**.
Cumulative work: 22 coupled solves (five in this leg), six bisections and
three pure-ring solves. Four threads, 160 GiB, chunks of 128; no AMR checkpoints.
Single-ring physical trajectories are archived above.

`railgun-refinement-regression-20261101`, second node/card 0,
code `91786ff2`, ran **11:55:53–11:59:39 MSK**: **63 GPU tests passed in
222.93 s**. Includes endpoint mass, independent Cartesian ADM flux,
refined-resume budget checks, fresh small-grid Newton recovery and saved-state
rejection. Four threads, 160 GiB, chunks of 128; no AMR checkpoints.
Its implementation checks completed before the approved refined pilot.

`railgun-ring-resumed-20261101`, second node/card 0, code
`da1280f5`, ran **10:56:58–10:57:42 MSK (0.012 h)**. Seed revalidation and
progress 0.5 passed. Progress 0.625 was rejected: off-grid KG 1.17e-8 at
r=0.25, theta=1.3 (also present intrinsically), surface-J error 2.41e-8,
and mass-fit drift above its gate. Cumulative work: **17 solves, six
bisections**. No pure ring or trajectories from that pilot.
The six targeted GPU flux/resume/device checks
passed in 3.87 s at **10:56:26 MSK**, code `da1280f5`.

`railgun-spherical-to-ring-20261101`, second node/card 0,
code `389c8762`, ran **10:46:17–10:49:52 MSK (0.060 h)**. It stopped normally
with `homotopy_unresolved` after 15 solves and six bisections; last passing
progress 0.40625. The angular-momentum balance gate blocked continuation.
No pure ring or trajectories were produced by that first leg.
Scratch is clean: **47 MB**, only `_cache/`,
**544 GB free** at the 12:07 MSK check. No plotfiles or AMR checkpoints. The first node was not listed.
Host/checkout details stay in the
untracked `runs/railgun/NODES.local.md`. Synchronisation is **git push/pull only**,
through `myfork`; code and validation archives were transferred that way.

The earlier regression tests and spherical pilots have completed. The
spherical-to-ring homotopy completed successfully in the refined pilot.
Stacked-ring and physical between-ring transport jobs are not queued.
Regression work on the
three newly identified safeguards completed under the same four-thread,
160 GiB, 0.5 h job cap, GPU 0 and Jacobian chunks of 128. No AMR checkpoints.

## Completed baseline — November 1

- **Pure rotating k=1 ring accepted**, ending **12:06 MSK**, code `58116d7a`.
  The old k=0 component and its frequency were removed before three-grid
  recovery. On 128x16: M_ADM=0.971450813143, J=-0.992014330336;
  independent Einstein/KG defects **1.58e-11 / 3.92e-12**, final observable
  drift **3.52e-10**. Pure-grid solve/check times **18.86 / 21.50 / 32.53 s**.
  This validates a stationary solution, not dynamical stability or ejection.
  Archive: `results/railgun/studies/ring-validated/`.

- **45 GPU regression tests passed**, 22.34 s, ending 10:21 MSK, code
  `732ed60e`. CUDA placement and float64 are asserted. The tests include
  canonical sources/parity, charge normalization, flat/Schwarzschild/Kerr
  curvature, TD-MPD conservation, the existing Newton/winding regressions and
  fail-closed validation. Portable report: `results/railgun/reports/gpu_regression.json`.
- **The spherical three-grid pilot passed**, 56x8 / 72x10 / 96x12, code
  `732ed60e`, ending **10:22 MSK**. Actual recovery: 1/2/2 Newton updates;
  full solve/check times 11.88/13.60/15.51 s. Final observable drift 1.18e-13.
  Relative discrepancies with the independently solved areal-radius ODE:
  **mass 5.48e-8, frequency 1.12e-8**. This is a stationary numerical baseline,
  not dynamical stability or evidence of a rotating ring.
- The accepted fields, ODE reference, manifests, diagnostics and checksums are
  tracked in `results/railgun/studies/spherical-validated/`; rejected initial and
  diagnostic studies are retained beside it. Archive commit `236aa328`.
- The rejected 40x6 grid's off-grid KG error was 5.23e-8; it shrank to
  1.14e-10 / 1.29e-12 on 56x8 / 72x10. That is radial under-resolution,
  not a measured stability issue. The old failed grid stays rejected.
  Relative spectra of nearly zero fields and sub-threshold tail noise were
  repaired using mixed absolute/relative roundoff handling; physical equation
  gates remain 1e-8 and observable convergence 1e-6. CUDA platform allocation
  without preallocation fits the 160 GiB address-space cap; the async allocator
  aborted during initialisation under that cap.

## Current implementation checks

The November 1 safeguards passed **51 GPU regressions in 55.99 s**, code
`fd15f724`, ending **10:37 MSK**, followed by **two saved-baseline GPU checks
in 140.43 s**, code `303bdab5`, ending **10:43 MSK**. Portable reports are
`results/railgun/reports/gpu_guards_regression.json` and
`results/railgun/reports/gpu_baseline_regression.json`. The subsequent nonlinear ring
attempts and their stopping conditions are recorded in Live and queue above.

1. Off-grid reports include worst KG/Einstein **radius and theta**, with a
   separate intrinsic divergence-form KG evaluation and Cartesian/intrinsic
   discrepancy. The existing spherical convergence result is retained.
2. `continuation.py` supplies a **bound-mode-seeded two-field homotopy**.
   Winding stays integer; the new k=1 component starts from a solved KG
   eigenmode on the spherical metric. Its pin rises as the k=0 pin falls.
   Missing bound states or failed nonlinear steps remain unresolved; no path
   is guaranteed. At the endpoint the residual k=0 field and its frequency
   are explicitly removed, then the pure ring needs fresh three-grid recovery.
   `studies/spherical_to_ring.json` caps this at 24 solves and six bisections.
3. `corridor.py` fits a regular **two-dimensional Cartesian core in rho²,z²**,
   retaining transverse derivatives. A C2 join, polynomial-order comparison,
   independent equations and curvature checks certify it before
   `transport --through-centre` removes the inner stop. Otherwise the stop
   remains. Inward spin controls now retain the inward velocity branch.

## Questions to test

The first homotopy reached converged two-field states, but remains unresolved.
At progress 0.5, off-grid Einstein/KG defects were 9.40e-11 / 6.59e-9;
the volume/infinity angular-momentum difference was 1.20e-7 against a 1e-8
gate. Smaller steps did not remove that limit. The original diagnostics and
all attempted fields are preserved; no tolerance was relaxed. The exact
surface flux at R/L=22,30,42,60 instead agrees with the matter integral
within 4.17e-9 on this same saved state. The finite-order far-field coefficient
fit caused the rejection. A correction uses exact surface integrals at the
unchanged 1e-8 gate, retaining the old fit as a diagnostic. GPU regression
checks passed before resuming this experiment; the corrected run passed
progress 0.5 and reached the resolution defect recorded above at 0.625.

1. **Single ring:** can a self-gravitating canonical complex scalar form a
   resolved stationary ring with appreciable interior frame dragging? Map
   density, lapse, dragging, curvature and any ergoregion.
2. **Counter-rotating rings:** can two independent winding fields produce
   nonzero local dragging while the angular momentum at infinity vanishes?
   Measure the remaining exterior multipoles and internal field; do not infer
   either from the imposed total-spin condition.
3. **Axial spin transport:** on an accepted metric, does reversing a small
   test body's spin change its axial motion or escape threshold? Compare
   matched initial data with positive, negative and zero spin.
4. **Stacked rings, later:** can an actual stationary solution support two
   off-equatorial density peaks and a more uniform interior dragging field?
   Ring positions and separation must emerge from the coupled equations.

These are hypotheses. Existence, dynamical stability, useful ejection and
novelty require separate evidence. A stationary solve alone settles none of
the latter three.

## Existing implementation and its limits

All paths below are relative to
`grteclyn-wrapper/src/grteclyn_wrapper/optimisation/`, unless stated otherwise.
The [package README](../../grteclyn-wrapper/src/grteclyn_wrapper/optimisation/README.md)
explains the existing workflow; the
[optimisation status](../optimisation/STATUS.md) retains its results.

- `solver/device.py`: select the device before importing JAX; float64,
  bounded CPU threading and CUDA selection through `--gpu`. GPU allocation
  uses `cuda_async` by default.
- `solver/jacobian.py`: exact forward-mode Jacobians of a JIT residual;
  GPU default is blocks of 1024 columns. Chunking reduces differentiation
  intermediates, but the final Jacobian and LU remain dense.
- `solver/newton.py`: row equilibration, damped Newton with Armijo
  backtracking and reusable LU factors. CUDA Jacobians select JAX's GPU LU;
  the host path uses NumPy/SciPy. Save damping, iteration and Jacobian counts,
  scaled residual and failure reason. A small scaled residual is only one gate.
- `matter_equations.py`: a two-ended wormhole metric with a phantom scalar,
  optional canonical non-winding field and **one** winding field. The latter
  uses regular amplitude `Z/sin^abs(k)(theta)` and an amplitude pin to solve
  its frequency. The existing total-J row includes the matter source.
  With phase `exp(i omega t + i k phi)`, the code's convention is `J_b=-k Q_b`;
  winding labels alone do not determine the physical rotation direction.
- `analysis/spinning_wormhole/spectral.py` in the wrapper supplies reusable
  Chebyshev operators and maps. Its present radial domain connects two
  infinities; `y=cos(2 theta)` represents equatorially even amplitudes.
- `exoticity.py` and `diagnostics.py`: spectral metric derivatives, tidal
  curvature, axis extrapolation and independent Ricci checks. These are
  starting points, not an implemented general MPD curvature interface.
- `resolution.py`, `study_validation.py` and `study_diagnostics.py`: screening,
  perturbed finer-grid re-solves, off-grid Einstein/scalar checks and physical
  diagnostics. Reuse their validation approach, with equations and boundaries
  appropriate to the new model.

**Implemented November 1; spherical and pure k=1 ring acceptance complete:**
`railgun/model.py` and `problem.py` provide the regular-centre domain, separate
winding fields, analytic parity factors, frequency borders and optional total-J
condition. `geometry.py` reconstructs Cartesian curvature and all Einstein/KG
residuals. `diagnostics.py` and `workflow.py` implement charge/mass balances,
doubled quadrature and three-grid Newton recovery. `reference.py` supplies an
independent spherical BVP. `transport.py` implements TD-MPD motion and matched
energy spin controls; `profiles.py` measures axial magnetic tidal curvature.
`commands/railgun.py` exposes solve/homotopy/profile/transport, with study configs
under `studies/`. See [equations](EQUATIONS.md) and [execution](RUNNING.md).
GPU baseline acceptance is recorded above. Through-centre transport requires
a separately certified Cartesian core; ordinary transport keeps the explicit
inner stop. Stability is unassessed.

Existing bosonic *wormhole* experiments have not certified a nonzero canonical
matter finalist. Their archived failures can guide initialization, but cannot
serve as accepted ring backgrounds. The radial stability screen remains
withdrawn; it must not label these objects stable.

## Physical definitions and claim limits

- **Topology and matter:** the proposed positive-energy ring is a regular-centre,
  one-ended Einstein–complex-scalar problem. Reusing a wormhole grid or setting
  its phantom field to zero does not implement that problem. Start with a
  canonical mass-only scalar and derive the centre, axis, equator and infinity
  boundary conditions. A phantom-supported wormhole plus rings would be a
  separate, explicitly labelled model.
- **Two fields:** use independent complex fields with separate frequencies,
  windings and amplitude conditions. Simply superposing different harmonics
  of one field can introduce time- or azimuth-dependent interference stress.
  Add their stress tensors and derive the full coupled equations and J balance.
- **Ergoregion:** evaluate `g_tt=-alpha^2+gamma_phiphi*(beta^phi)^2` in an
  asymptotically nonrotating frame. In the present ansatz,
  `g_tt=-exp(f)+B^2 exp(-f) (eta^2+eta0^2) sin^2(theta) omega^2`.
  On a regular axis this is `-exp(f)<0` for finite positive lapse. Thus an
  ergoregion touching the axis is excluded by these assumptions; test for an
  off-axis region instead. An ergoregion does not imply local faster-than-light motion.
- **Vacuum and exterior:** massive scalar bound states have tails. Define a
  numerical low-density bore with a reported threshold and convergence check;
  do not call it exactly empty. Setting ADM J to zero removes the leading
  angular-momentum term, not every exterior rotational multipole or dragging
  effect. A wormhole version would also require separate charges at both ends.
- **Force and energy:** use the covariant pole–dipole MPD equations with a
  declared spin supplementary condition, initially Tulczyjew–Dixon
  `p_mu S^(mu nu)=0`. The draft's `-S dB/dz-dalpha/dz` is not an exact force
  law. Specify the observer/tetrad for any gravitomagnetic-field plot and
  regularise curvature on the axis. Monitor the spin-corrected Killing energy
  and angular momentum, mass, spin magnitude and timelike motion; a stationary
  metric does not provide an unspecified energy source. The
  [MPD formulation and Killing integrals](https://link.springer.com/article/10.1140/epjc/s10052-023-11970-5)
  provide one reference for these checks.
- **Waves and stacks:** a scalar mode is not a circularly polarised spinning
  wavepacket. Wave transport needs a separately specified field model.
  Equatorially even amplitudes can have two peaks; odd amplitudes require a
  new parity representation and boundary rows. Neither a seed nor prescribed
  peak locations establish an equilibrium or a uniform tube.

## Implementation and test order

New code lives under `optimisation/railgun/`, with thin commands in
`optimisation/commands/`, tests under `tests/optimisation/` and plots under
`visualisation/optimisation/` reserved for plots. The stages below define the
acceptance order; having implemented a stage does not establish its physics.

1. **Derive the baseline model.** Specify the action, normalisation, metric,
   topology, phase convention and all boundary conditions. Count equations,
   unknowns and frequency/amplitude borders. Independently derive every
   Einstein/Klein–Gordon row, including equations left out of Newton. Keep
   the published spinning-wormhole solver unchanged.
2. **Implement one regular-centre field.** Reuse the generic device, Jacobian
   and Newton core; introduce the correct radial map and boundary rows.
   Verify the zero-field/flat limit and a documented boson-star benchmark,
   then continue to a single winding ring. Reject the trivial zero-field
   branch when a nonzero amplitude is prescribed. Begin with `abs(k)=1`;
   only expand to 2 and 3 after the first branch passes validation.
3. **Implement measurements.** Save density peaks, Noether charge, ADM mass/J,
   their independent volume/asymptotic balance, lapse, `g_tt`, local dragging,
   curvature and tail estimates. Build a differentiable off-grid metric
   interpolant; differentiating a saved array with respect to coordinates
   is not a curvature calculation. Validate flat/static limits, an independent
   rotating-metric curvature benchmark and the regular-axis limit.
4. **Add axial transport.** Implement geodesic and MPD evolution on a fixed,
   validated background. Test zero spin, reversal of spin and background
   rotation, small-spin scaling and convergence of trajectories and conserved
   quantities. Report escape/trapping against the zero-spin control and
   matched launch energy. Start with an axial force profile before long tracks.
5. **Add counter-rotation.** Generalise to two winding fields, each with its
   own frequency/normalisation. Continue from one field, then solve toward
   `J_total=0`, initially with `k1=+1, k2=-2`; `-3` is a later comparison.
   Include all matter and any inner-boundary contribution in the J balance.
   Measure rather than assume radial ordering or substantial interior dragging.
6. **Add stacked states only after the preceding gates.** Implement and test
   parity, nodal structure and any explicitly chosen self-interaction.
   Quantify field uniformity over a stated proper-length interval and compare
   a matched single ring. Do not enlarge to an unrestricted parameter search.

Every accepted background needs finite fields, boundary/regularity checks,
independent unused Einstein and scalar residuals, resolved tails and fresh
Newton recovery from perturbed seeds on **three increasing grids**. Interpolation
screens alone do not qualify. Establish normalised tolerances before the first
scan; start from the existing `1e-8` independent-equation gate and `1e-6`
observable-drift target, and validate their meaning for the new equations.
Do not relax a failed gate to obtain a result. Stability remains `not_assessed`.

## Cluster execution and saved evidence

- Read `AGENTS.md` and this status again; sync the tested commit through
  `myfork`. Run GPU solves and numerical acceptance tests on the designated
  cluster checkout using `grteclyn-wrapper/.venv/bin/python`.
- Check `nvidia-smi`, GPU processes, scratch usage and cgroup limits first.
  Use `scripts/ops/capped_job.sh` with explicit thread, memory and wall-time
  limits and persistent logs. The inspected node has a 24-CPU quota and about
  488 GiB container memory. Host address-space limits are not GPU-memory caps.
- Obtain a go for a concrete bounded pilot, with a selected card, grid,
  Jacobian chunk, tolerance, solve budget and timeout. Ask separately about
  saved restart states; AMR checkpoints do not apply to a stationary solve.
  Verify actual CUDA placement, float64, memory and the first diagnostic rows
  within minutes. Measure compilation and steady-state solve costs separately
  before assigning further run budgets or ETAs.
- Run the existing solver-core, winding-field and validation regressions,
  then the new boundary, two-field, curvature and MPD tests. Compare small-grid
  CPU and CUDA values on the cluster; production solves remain on its GPUs.
- Keep working data under `runs/railgun/` and job logs under `runs/capped_jobs/`.
  Pack reproducible accepted fields, configurations, code/dependency versions,
  residuals, refinement records, timings and diagnostic/trajectory tables into
  `results/railgun/`. Record failures without promoting their fields to results.
  No scratch deletion is authorised here; preserve frames and slice caches.

**Current implementation:** endpoint ADM/lapse mass extraction and an explicit
grid-only refined resume are implemented; all **63 GPU regressions passed**.
Report: `results/railgun/reports/gpu_refinement_regression.json`. The
mass coefficient fit has drift 1.02e-6 at progress 0.625; the endpoint estimate
agrees with the volume mass within 1.73e-8. Original records stay unchanged.
The old KG and exact surface-J failures shrank under the approved refinement;
the original failed records stay rejected. The refined config completed with
unchanged physical amplitudes and 1e-8 equation/charge gates. All three pure-ring
grids passed, as recorded above.

**Figures complete:** overlapping counter-rotating fields and densities are
under `results/railgun/figures/two-rings*.png`, with exterior dragging in
`counter-dragging.png`. Between-ring particle trajectories, asymptotic
ejection and dynamical stability remain untested.

**Cubic falloff experiment completed, rejected:** the separately approved
run stopped after its first grid on the added literal-infinity gate.
The original source and every failed field are retained, as reported above.
No off-axis particle launch follows from this rejected study.

**Seed screen completed and archived:** `studies/branch_seeds.json`,
six full 2D GPU bound-mode pencils on the accepted weak k=1 metric: new
k=2 even fields at masses 2.5 and 3, and a new k=1 odd field, two grids
96x12 / 128x16. Keep the original field as a separate species. These start
a future amplitude homotopy, not a relabelled winding or accepted final
geometry. The outer -6/-8 species can be seeded only after a pure mixed-mass
inner branch is independently recovered. Six-problem go received; no
nonlinear mixed-mass or odd branch recovery is authorised yet.

**Latest approved correction sequences completed:** the two-track precision
audit and first-grid quintic recovery both stopped rejected, as detailed in
Live and queue. Their original budgets are closed. Further numerical runs need
a separately bounded proposal and go; no off-axis trajectory is queued.
