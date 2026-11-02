# Running ring studies

**Completed November 2:** N=192 reached t=50 at 12:56:40 MSK, exit 0.
The 16 movies finished encoding at 14:02:43 MSK; contact sheets await visual
review. Checkpoints OFF. No evolution remains live; the new stationary study
is listed below. See STATUS for storage.
Scope: [studies/evolution_long_070.json](studies/evolution_long_070.json).

**Completed November 2:** the omega=0.70 Cartesian 3+1 import and full
96^3 / 128^3 / 192^3 Richardson study through t=2 finished. All approved
pilot budgets are closed. The finest pair's Ham/Mom orders at
t=2 are 4.01 / 3.83; charge-change Richardson order is 4.677.
See [EVOLUTION.md](EVOLUTION.md) and [STATUS.md](STATUS.md).

**Completed November 1:** both numerical blockers are resolved. Accepted
archives: `studies/strong-uphill-073-validated/`, `studies/annular-validated-k12/`
and `studies/annular-transit-k12/` under results/railgun. All eight annular
tracks pass; no jobs remain live or queued. Earlier commands and proposals
below are retained for reproduction, not as a current launch queue. See
[STATUS.md](STATUS.md) for current outcomes and the unchanged acceptance gates.


Read [STATUS.md](STATUS.md), [EQUATIONS.md](EQUATIONS.md) and the repository
[AGENTS.md](../../AGENTS.md) first. Numerical jobs run on the cluster checkout
identified in the untracked `runs/railgun/NODES.local.md`. No command below
reserves a GPU or grants a launch authorisation.

Raw runs are grouped under `runs/railgun/`:

- `spherical/`: reference solutions.
- `single-ring/`: `construction/`, `profiles/` and `scans/`.
- `two-rings/`: `separated/`, `overlapping/` and `seeds/`.
- `particles/`: `single-ring/` and `two-rings/` experiments.
- `evolution/`: Cartesian imports, binaries, pilots and long evolutions.
- `checks/`, `logs/`, `manifests/`: test reports, operational logs and path mappings.

The root README indexes the groups. Evolution and movie paths stay fixed.
Historical logs and saved JSONs retain their original paths; the layout JSON
in `manifests/` maps each old path to its current location and records checksums.
New output directories belong in the matching group. To preview a legacy
folder reorganisation, run `python3 research/railgun/organize_runs.py`; use
`--apply` only after checking that no running job uses the folders being moved.
The script verifies every moved file and leaves `evolution/` untouched.

## Automatic CMA-ES ergoregion search

Scope: [ergoregion_cma.json](studies/ergoregion_cma.json), approved November 2
with checkpoints OFF; ran 18:38:03–18:44:52 MSK on the two-GPU node/card 0.
It found a three-grid validated ergoregion after five proposals: shift/lapse
1.080970704, g_tt maximum +0.0150110091, omega=0.655065086594. All 41 GPU
regressions pass. The discovery budget is closed. Maximisation is a new study. The same `cma.CMAEvolutionStrategy` ask/tell algorithm as
the wormhole search chooses **central lapse**, the central clock rate relative
to infinity, between 0.14 and 0.41. For this fixed k=1, m=1 free scalar model
there is one continuous branch coordinate; map scale is a numerical choice,
not an extra physical parameter. No interaction or winding changes.

The new equation `mean_y f(r=0,y) = 2 log(alpha_c)` replaces the scalar
amplitude border. Frequency and amplitude are both solved. First reproduce
the last accepted omega=0.685955820263 ring with this new border. Then CMA
chooses up to 32 targets (population four, seed 171), beginning near 0.30.
Each proposal starts from nearby screened fields with a bounded secant guess.
Automatic log-lapse steps <=0.04 and at most four bisections per proposal
handle failed jumps; failed fields never enter the initial-guess cache.
The cache's intermediate states are provisional. All unused-equation, charge,
flux, tail and branch screens run on them. Independently reconstructed
Einstein/KG checks must also pass at the final proposal before it receives
the feasible score `1/(1+max(|shift|/lapse))`; failures score >=2.

Maximum 80 search solves, including the initial reproduction, plus nine
reserved for at most three finalists. Search grid 128x16; every finalist is
solved afresh on 128x16 / 160x20 / 192x24. Newton 1e-14, fresh Jacobians,
two updates minimum, 30 iterations maximum. Original acceptance thresholds
remain unchanged. Only a three-grid positive-g_tt sign with the common-point
margin check produces `accepted_ergoregion.npz`. Single-grid samples remain
provisional; `best_validated.npz` may still be a ring without an ergoregion.
The process stops on full ergoregion acceptance or its work/time cap.

CPU-only preview on the authorised node:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.optimisation.railgun.ergoregion_cma \
  research/railgun/studies/ergoregion_cma.json \
  --source runs/railgun/single-ring/scans/ergoregion-amplitude-20261102-r2/amplitude_01/accepted.npz \
  --out runs/railgun/single-ring/scans/ergoregion-cma-20261102 --gpu 0 --dry-run
```

Prepared launch, only after its go: GPU regression tests, then search,
four CPU threads, 160 GiB, one-hour cap for the whole sequence, chunks 128:

```bash
bash grteclyn-wrapper/scripts/ops/capped_job.sh start railgun-ergoregion-cma-20261102 \
  --threads 4 --mem 160 --timeout 3600 --gpu -- \
  bash research/railgun/run_ergoregion_cma.sh
```

Card 0 on the two-GPU node only. The script checks occupancy and source hash
before GPU tests. Keep every attempt, failed diagnostic, optimiser stop
criterion, configuration and solved field. No automatic 3+1 evolution or AMR
checkpoint is part of this search. Unlike the earlier fixed sequence, individual
rejected proposals do not close the approved search budget.

## Amplitude continuation toward a single-ring ergoregion

Prepared scope: [ergoregion_amplitude.json](studies/ergoregion_amplitude.json).
The stationary study received its go November 2, checkpoints OFF, and started
at 17:56:39 MSK on the second GPU node/card 0. It stopped at 17:59:36 MSK
after all three reproduction grids passed the original checks: the added
extrema comparison used different physical sample positions. See STATUS.
The dry run reads only NumPy data and does not initialise JAX:

```bash
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.optimisation.railgun.ergoregion_scan \
  research/railgun/studies/ergoregion_amplitude.json \
  --source results/railgun/studies/frequency-deep/frequency_01/accepted.npz \
  --out runs/railgun/single-ring/scans/ergoregion-amplitude-20261102 --gpu 0 --dry-run
```

The source hash and the 27-solve profile are checked before JAX starts. First
reproduce omega=0.70 after changing the radial scale to 2.5 and moving the
pin from radius 5 to the source's equatorial scalar peak, radius 1.202893.
Interpolation evaluates the old solution at the new nodes' physical radii;
copying values at equal compactified coordinates would change the geometry.
The initial pinned amplitude is 0.307398668. Eight subsequent steps increase
it by 6% each, up to 0.489946775. Frequency is solved, not prescribed. After
two accepted points, extrapolate every field and frequency with a secant in
the pin value. The pin radius remains fixed throughout the scan.

Every point uses 128x16 / 160x20 / 192x24, fresh Jacobians, Newton 1e-14,
30 iterations maximum and two updates minimum. All original acceptance
checks remain. Extra strong-field observable/frequency checks and the initial
source-reproduction check run before any accepted file is written. A sampled
ergoregion needs positive g_tt on all three grids, exceeding both 1e-8 and
their measured spread, with shift/lapse above one. Stop on a rejected point
or that resolved sign. No automatic retries, k=2 solve or further refinement.
A pin at fixed radius can itself turn; this experiment does not assume a
monotone physical branch, a known frequency floor or guaranteed formation.
Shift/lapse is an observer-dependent metric ratio, not the matter's speed.
Strong-field maxima are now sampled on identical physical points for every
resolution: 385 radial by 50 angular, including the origin, axis and equator.
The raw grid-dependent sampled maxima remain in the original grid reports;
the common-point values and positive-g_tt coordinates go in the added checks.

After a go, run the new test file and the existing frequency, geometry and
diagnostic tests on the named card first. Require CUDA and float64; pass
`JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=0 WH_JAC_CHUNK=128` with platform
allocation and preallocation off. Then run the command above without
`--dry-run`, under `capped_job.sh`, four CPU threads, 160 GiB, 1800 seconds.
Keep every attempted field and log under the grouped paths. No 3+1 evolution
or AMR checkpoints are part of the proposed stationary study.

Original sequential test/scan command, retained for reproduction:

```bash
bash grteclyn-wrapper/scripts/ops/capped_job.sh start railgun-ergoregion-amplitude-20261102 \
  --threads 4 --mem 160 --timeout 1800 --gpu -- \
  bash research/railgun/run_ergoregion_amplitude.sh
```

The script checks card 0 is free again, writes the GPU regression report to
`runs/railgun/checks/`, and starts the scan only if those tests pass. Its
1800-second cap covers tests and continuation together; timeout retains all
completed files and requires a new bounded proposal before any continuation.

The first job stopped after three passing reproduction solves because the
initial extra comparison used different sample positions. It remains rejected.
The corrected continuation received its separate go and started at
18:10:04 MSK on the two-GPU node/card 0, checkpoints OFF. It stopped at
18:13:36 MSK: the first 6% increase passed three grids (omega=0.685956,
shift/lapse=0.617781); the next increase failed Newton on 128x16. This
budget is closed, with four new/seven cumulative solves. No ergoregion:

```bash
bash grteclyn-wrapper/scripts/ops/capped_job.sh start railgun-ergoregion-amplitude-r2-20261102 \
  --threads 4 --mem 160 --timeout 1800 --gpu -- \
  bash research/railgun/run_ergoregion_amplitude.sh --resume-bootstrap
```

Before any GPU startup, preview it with the dry-run command above plus
`--resume-bootstrap runs/railgun/single-ring/scans/ergoregion-amplitude-20261102`.
It checks the existing three passing grid reports, hashes every reused input,
verifies the model/pin and rechecks source reproduction at the unchanged
limits. No old evidence changes. A new `ergoregion-amplitude-20261102-r2/`
directory copies and recertifies those three fields; `outcome.original.json`
preserves the earlier rejection. The remaining eight increases use at most
24 new solves, with three prior solves counted toward the original 27.
Nine CPU tests cover the correction and reuse; GPU tests must pass again
before continuation. The new 1800-second cap includes tests and solves.

From the repository root:

```bash
PY=grteclyn-wrapper/.venv/bin/python
MOD=grteclyn_wrapper.optimisation.commands.railgun

# Does not initialise JAX.
$PY -m "$MOD" solve research/railgun/studies/single_ring.json \
  --gpu 0 --out runs/railgun/single-ring/construction/single-pilot --dry-run

# Run only after the named pilot has a go and nvidia-smi/storage are checked.
bash grteclyn-wrapper/scripts/ops/capped_job.sh start railgun-spherical-pilot \
  --threads 4 --mem 160 --timeout 1800 --gpu -- \
  "$PY" -m "$MOD" solve research/railgun/studies/spherical_reference.json \
  --gpu 0 --jac-chunk 128 --out runs/railgun/spherical/spherical-pilot
```

A new output directory is required. Solved fields on every attempted grid
remain provisional in `grid_NxM.npz`, with Newton history and diagnostics in
the matching JSON. `outcome.json` states acceptance and rejection reasons.
A failed gate stops a normal study and returns exit code 2. The spherical
pilot enables `diagnostic_refinement`: a converged, finite rejected coarse
solution is re-solved on its two already specified finer grids to measure
the defect. The rejected grid stays rejected, and prevents acceptance.
Only a passing
three-grid study writes `accepted.npz`. No AMR checkpoints are written.

The other supplied configurations are single-ring, counter-rotating J=0 and
odd-parity stacked pilots. They are definitions for later tests, not a dispatch
queue. Start from the spherical benchmark and single ring; do not launch all
four together. `--seed` accepts saved matching field content and radial scale
for a warm start. It does not silently change winding, parity or topology.

After an accepted background, separate bounded jobs can call:

```bash
$PY -m "$MOD" profile runs/railgun/single-ring/construction/single-pilot/accepted.npz \
  --gpu 0 --out runs/railgun/single-ring/profiles/single-axis --z-min .1 --z-max 30 --samples 101
$PY -m "$MOD" transport runs/railgun/single-ring/construction/single-pilot/accepted.npz \
  --gpu 0 --out runs/railgun/particles/single-ring/single-tracks --z 5 --spin .001 --speed .2 \
  --duration 10 --max-step .2
```

Both operations require `accepted.npz` and refuse provisional fields. Profile
columns include the observer-defined magnetic tidal force, not a guessed
Newtonian force. Transport compares positive, negative and zero spin at the
same Killing energy; tighten tolerances and step size for convergence before
interpreting differences. No fixed-background result measures nonlinear stability.

Regression tests on a selected cluster card can run as one capped job:

```bash
bash grteclyn-wrapper/scripts/ops/capped_job.sh start railgun-regression \
  --threads 4 --mem 160 --timeout 1800 --gpu -- \
  env JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=0 WH_JAC_CHUNK=128 \
  XLA_PYTHON_CLIENT_ALLOCATOR=platform XLA_PYTHON_CLIENT_PREALLOCATE=false \
  "$PY" -m pytest -q grteclyn-wrapper/tests/optimisation/test_railgun_model.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_geometry.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_diagnostics.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_transport.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_continuation.py \
  grteclyn-wrapper/tests/optimisation/test_railgun_baseline.py \
  grteclyn-wrapper/tests/optimisation/test_solver_core.py \
  grteclyn-wrapper/tests/optimisation/test_winding_field.py \
  grteclyn-wrapper/tests/optimisation/test_layout.py
```

Preserve NFS logs, configs, manifests, rejected diagnostics and accepted fields.
Pack verified results into `results/railgun/` only after reviewing their gates.
Do not prune scratch or discard frames as part of a test run.

The spherical-to-ring branch has a separate bounded initializer:

```bash
$PY -m "$MOD" homotopy research/railgun/studies/spherical_to_ring.json \
  --source results/railgun/studies/spherical-validated/accepted.npz \
  --gpu 0 --out runs/railgun/single-ring/construction/spherical-to-ring --dry-run
```

An actual homotopy requires its own go and capped job. It tests for a bound
linear mode before nonlinear steps, keeps winding integer and stops on a
missing branch or exhausted budget. Intermediate two-field states are not
accepted pure rings.

`homotopy --resume <prior unresolved directory>` requires the identical
configuration and spherical source, rechecks the last passing point, and
carries forward all spent solves and bisections. It neither resets the work
budget nor promotes a previously rejected point. Use a new output directory.

An explicitly approved grid refinement uses `--resume ... --refine-resume`.
Only the three grids may change, and each radial and angular order must
increase. Physical settings, tolerances, solve and bisection budgets must
match. The last passing state is perturbed and freshly solved on the new
first grid with at least two Newton corrections. That recovery consumes a
solve from the existing budget; its independent checks must pass before
continuation proceeds. The proposed refined configuration changes only
the grids to 72x10 / 96x12 / 128x16:

```bash
# Lists the proposal; initialises no GPU. The actual pilot needs its own go.
$PY -m "$MOD" homotopy research/railgun/studies/spherical_to_ring_refined.json \
  --source results/railgun/studies/spherical-validated/accepted.npz \
  --resume results/railgun/studies/spherical-to-ring-resumed --refine-resume \
  --gpu 0 --jac-chunk 128 --out runs/railgun/single-ring/construction/spherical-to-ring-refined --dry-run
```

The saved run has spent 17 of 24 coupled solves and all six bisections.
Expected remaining work is one recovery solve plus four continuation points;
up to seven coupled solves remain, followed by at most three pure-ring solves.
Proposed caps are four threads, 160 GiB, 0.5 h and no AMR checkpoints.

`transport --through-centre --speed -.2` selects an inward launch and requests
a regular Cartesian core. The core must pass independent equations, curvature
matching and polynomial-order checks; otherwise no trajectory starts. Its
certificate is saved as `corridor.json`. Merely removing the inner stop on the
original spherical-coordinate interpolant is refused.

The separated-ring screen has a dedicated nonlinear recovery, with its own go:

```bash
$PY -m grteclyn_wrapper.optimisation.railgun.annular_recovery \
  research/railgun/studies/annular_recovery_k12.json \
  --source results/railgun/studies/annular-gap-screen/k12_128x16.npz \
  --out runs/railgun/two-rings/separated/annular-recovery-k12 --gpu 0 --dry-run
```

The dry run imports no JAX and checks the seed checksum, passing two-grid
screen provenance, three-solve budget and dense storage estimate. Removing
`--dry-run` starts GPU work: use the capped launcher above after its specific
go, with the platform allocator, four threads, 160 GiB, 1800 seconds and chunks
of 128. The configured grids are 192x16, 224x18 and 256x20 at L=50. Promotion
adds the total-J border explicitly; the last unbordered frequency must never
be mistaken for the new logarithmic amplitude unknown.

Each grid requires two fresh corrections, all independent field-equation
checks, total J=0 and the 1e-6 component-wise annular gap. The middle half of
the gap is also sampled on a 21x81 cylindrical mesh over z=-10..10, normalised
to each component's own equatorial peak. Acceptance additionally requires
1e-6 convergence of the separately measured charges and both gap edges on
the last two grids. Failed states and diagnostics remain saved; no overlap,
changed potential or weaker tolerance is an automatic fallback. A certified
sampled channel is still separate from an actual confined particle trajectory.

If only the finest grid's angular-momentum balance fails, an explicitly
approved **one-solve** correction can use `--correct-from
results/railgun/studies/annular-recovery-k12` with a new output directory. It verifies
the original archive checksums and identical configuration, starts from the
saved finest state with a fresh Jacobian and at least two updates, and repeats
all gates. The earlier two passing grids remain evidence. This raises the
cumulative budget from three to four solves; a corrected study cannot reset
that extra budget. No acceptance tolerance changes, and the original rejected
study remains untouched.

The asymmetric uphill experiment uses the already accepted pure ring and
its exact core certificate. The dry run starts no JAX:

```bash
$PY -m grteclyn_wrapper.optimisation.railgun.uphill \
  research/railgun/studies/uphill_transit.json \
  --source results/railgun/studies/ring-validated/accepted.npz \
  --profile results/railgun/studies/ring-profile \
  --out runs/railgun/particles/single-ring/uphill --gpu 0 --dry-run
```

After a run-specific go, use the capped GPU launcher with four threads,
160 GiB, 1800 s, chunks 128 and the platform allocator. The 32-track cap
includes four shared energies, three spin controls plus full background/spin
reversal, and two RK tolerances. Full conserved energy includes the spin
coupling. A turnaround is an event in the actual coordinate velocity, rather
than an inference from not reaching a destination before a timeout. Only
finite endpoint selection can be claimed; no asymptotic escape follows.

The independently gated compactness scan has its own dry run and go:

```bash
$PY -m grteclyn_wrapper.optimisation.railgun.compactness \
  research/railgun/studies/compactness_scan.json \
  --source results/railgun/studies/ring-validated/accepted.npz \
  --out runs/railgun/single-ring/scans/compactness --gpu 0 --dry-run
```

Seven amplitude pins are attempted in order, at most 21 solves. Every point
needs three fresh grids and two corrections per grid before becoming the
next seed. A failed point stops the scan; an accepted sampled ergoregion
also ends it. Each accepted point saves its own fields and diagnostics.
No frequency, maximum spin, stability or particle-selection outcome is
presupposed. Mixed-mass and odd-parity seed work stays separately queued.

The amplitude scan accepted pins through 0.095 and stopped at 0.12. The
separately approved follow-on controls frequency rather than the amplitude
at a fixed coordinate radius:

```bash
$PY -m grteclyn_wrapper.optimisation.railgun.frequency_scan \
  research/railgun/studies/frequency_scan.json \
  --source results/railgun/studies/compactness-scan/amplitude_03/accepted.npz \
  --out runs/railgun/single-ring/scans/frequency-scan --gpu 0 --dry-run
```

The frequency border replaces the pin condition without adding unknowns.
Saved states declare `frequency_targets` and their measured amplitude pins;
older states retain their original amplitude-border interpretation. Every
point still requires three grids, two fresh corrections, independent equations
and the original convergence gates. A charge floor of 0.001 times the source
charge and a nodeless-field check prevent accepting the trivial vacuum or
switching to an excited branch. At most 21 solves; stop on rejection or a
validated sampled ergoregion. Use the same capped GPU execution limits.

### Completed resolution recovery at omega=0.73

The frequency scan stopped on the 72x10 unimposed constraint at omega=0.73.
`studies/frequency_073_refined.json` changes only the grids to 96x12 / 128x16 /
160x20, keeping frequency, model, branch guards and tolerances. Seed from the
converged but rejected 72x10 field; its use as an initial guess does not accept
its constraint error. Every new grid must make at least two real corrections
and pass independently; the three-grid observable test remains mandatory.

Command approved and completed November 1: three passing solves.
Archive: `results/railgun/studies/frequency-073-refined/`. This output directory
already exists; a rerun needs a new run-specific go:

```bash
bash grteclyn-wrapper/scripts/ops/capped_job.sh start railgun-frequency-073-refined-20261101 \
  --threads 4 --mem 160 --timeout 1800 --gpu -- \
  env XLA_PYTHON_CLIENT_ALLOCATOR=platform XLA_PYTHON_CLIENT_PREALLOCATE=false \
  grteclyn-wrapper/.venv/bin/python -u -m grteclyn_wrapper.optimisation.commands.railgun solve \
  research/railgun/studies/frequency_073_refined.json \
  --seed results/railgun/studies/frequency-scan/frequency_05/grid_72x10.npz \
  --out runs/railgun/single-ring/scans/frequency-073-refined-20261101 --gpu 0 --jac-chunk 128
```

Three solves maximum, 30 iterations each, four threads, 160 GiB, 0.5 h.
No AMR checkpoints or automatic lower-frequency follow-on.

### Deep frequency continuation and stronger-ring transport

The November 1 direct instruction authorises `studies/frequency_deep.json`:
omega=0.70 then 0.67, three grids 96x12 / 128x16 / 160x20, at most six
solves, max 30 Newton iterations each, at least two updates per grid. Keep
all independent gates and branch guards. Stop on first rejection or a
three-grid-validated sampled ergoregion. Source is the accepted omega=0.73
recovery. Use the `railgun.frequency_scan` command with that config.

Separate proposed core/profile job for the accepted omega=0.73 source:
signed z=-15..15, 301 samples; equatorial rho=0..30, 601 samples; core
radius 0.4, degree 6 compared against degree 8. Stop on failed certification.
After certification, propose the existing bounded uphill config: at most
32 matched-energy tracks, spin 0 / +/-0.001, z=+1 toward -10, two RK
tolerances and background/spin reversal; duration cap 250 per track.
Exact-threshold marginal contacts remain height/conservation controls and
never timing or selection evidence. Core/profile and conditional tracks received a separate go. Each uses
four threads, 160 GiB, 1800 s, GPU card 0 on the second node; no AMR
checkpoints, retain profiles, tracks and logs.

### Prepared discrete-field seed screen

`railgun.branch_seeds` and `studies/branch_seeds.json` define six GPU linear
mode pencils: k=+2, m=2.5 or 3, even; and k=+1, m=1, odd, each on
96x12 / 128x16. The original accepted weak k=1 species remains field 0;
the new species is field 1 at amplitude 0.001. Fixed-metric seeds are saved
with validated=false. Require printed-PDE residual <=1e-8 and two-grid
frequency drift <=1e-6. No winding or parity interpolation is used.

This is prepared only, with no GPU go. These seeds start a future two-field
amplitude homotopy. A pure heavy k=2 inner ring must pass three-grid
recovery before adding outer k=-6 or -8; the odd seed similarly needs a
pure odd recovery before any stacked-geometry or vacuum-slot claim.
No final mixed-mass two-ring or stacked spacetime is generated by this screen.

### Approved two-control precision audit and zero-J quintic recovery

The initial strong-ring study retains 32 tracks but fails only two timing
comparisons. `railgun.uphill_precision` with
`studies/uphill_precision_073.json` reintegrates just those two controls
at rtol=2e-13, comparing each with its saved 2e-12 track. Initial states
are reused bit for bit; all passing controls and the original failed
archive remain unchanged. The accepted matching source/core certificate
is hash-checked and reused. No timing or conservation limit is relaxed.

The cubic boundary experiment passes finite-sphere flux but fails its
literal-infinity coefficient. The separately prepared
`studies/annular_quintic_k12.json` uses r^-5 falloff appropriate to J=0
and equatorial symmetry. It adds a leading angular-mode test and retains
every original equation/flux/gap/channel/convergence limit. All four
omitted outer PDE rows are checked independently. Three solves maximum,
30 iterations each, minimum two updates per grid; no off-axis tracks.

Both have explicit run-specific approval. Selected
card 0 for the two-track audit, card 1 for the quintic recovery; four
threads, 160 GiB, 1800 s per job, chunks 128, no AMR checkpoints.

Both correction jobs launched on November 1 at 19:06:19 MSK after 52
passing targeted GPU tests; code `568eaac8`. See STATUS for outcomes.

Both jobs have finished rejected: the precision audit retains timing changes
1.88654e-7 and 2.03222e-7 above 1e-7; the quintic study fails its first-grid
leading infinity angular equation (80.57967 above 1e-6). No later grids or
off-axis tracks. Completed archives are under studies/strong-uphill-073-precision
and studies/annular-quintic-k12. No new numerical run is authorised.


### Approved regular-operator recovery and independent phase audit

Configs `studies/annular_regular_k12.json` (card 1) and
`studies/axial_audit_073.json` (card 0) have a separate go. Each follows
its targeted GPU tests, four threads, 160 GiB, 1800 s, chunks 128,
no AMR checkpoints. The former has at most three fresh 192x16/224x18/256x20
solves, max 30 iterations/minimum two updates, stop on rejection. The latter
has at most 32 phase quadratures and 656 full MPD substitution points,
zero new MPD tracks. Source/core hashes and all earlier failed evidence
are preserved. All existing numerical gates remain unchanged.


### Prepared final Newton polish and conditional annular particles

`studies/annular_regular_polish_k12.json` tightens only the Newton solve:
1e-14, a fresh Jacobian every update, minimum two updates; three grids
192x16/224x18/256x20, at most three solves/max 30 iterations. The source,
physics and every original acceptance gate stay unchanged. Direct H-coefficient
transfer preserves the solved infinity data on refinement instead of refitting
tiny physical w values. The previous first-grid flux rejection remains archived.

`studies/annular_transit_k12.json` is a conditional eight-track pilot that
refuses any unvalidated or non-archived background. Launch at the midpoint
of the common three-grid matter channel, z=+10, axial speed -0.5; match the
full Killing energy for spin 0/+0.001/-0.001 and a background/spin reversal,
two RK tolerances 2e-11/2e-12, duration 100, step 0.4, 1001 samples. Require
1e-9 conservation, 1e-7 timing/position/reversal agreement and both actual
Cartesian Eulerian component densities below 1e-6 of their own source peaks
at every sample. Trajectories must remain inside the validated rho interval
and reach z=-10. This is off-axis finite passage, not escape or energy gain.
No core patch is needed for the annular tube. These jobs have a
separate run-specific go; four threads/160 GiB/0.5 h/chunks 128/no AMR
checkpoints per job. GPU regressions precede any production execution.


### Prepared regular-cubic and two-integral phase polish

`studies/annular_regular_cubic_k12.json` changes only the regular operator's
falloff power to 3, allowing independent infinity J measurement; original
source, grids, all physical gates and fresh-Jacobian 1e-14 settings stay fixed.
At most three solves, stop on rejection. `studies/axial_phase_polish_073.json`
adds only two order-32 scalar integrals against saved order-16 values;
all 656 full MPD checks and the existing particle tracks are reused with
hash verification. No new tracks or MPD checks; cumulative phase budget 34.
Both configurations pass non-GPU preflight. Fifteen development tests pass,
including the exact linear-Kerr momentum equation. The separate go for both jobs is received.
The conditional eight-track annular experiment remains approved, and cannot
start before complete three-grid field acceptance.
