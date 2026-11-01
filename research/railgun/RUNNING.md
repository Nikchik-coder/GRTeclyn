# Running ring studies

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

From the repository root:

```bash
PY=grteclyn-wrapper/.venv/bin/python
MOD=grteclyn_wrapper.optimisation.commands.railgun

# Does not initialise JAX.
$PY -m "$MOD" solve research/railgun/studies/single_ring.json \
  --gpu 0 --out runs/railgun/single-pilot --dry-run

# Run only after the named pilot has a go and nvidia-smi/storage are checked.
bash grteclyn-wrapper/scripts/ops/capped_job.sh start railgun-spherical-pilot \
  --threads 4 --mem 160 --timeout 1800 --gpu -- \
  "$PY" -m "$MOD" solve research/railgun/studies/spherical_reference.json \
  --gpu 0 --jac-chunk 128 --out runs/railgun/spherical-pilot
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
$PY -m "$MOD" profile runs/railgun/single-pilot/accepted.npz \
  --gpu 0 --out runs/railgun/single-axis --z-min .1 --z-max 30 --samples 101
$PY -m "$MOD" transport runs/railgun/single-pilot/accepted.npz \
  --gpu 0 --out runs/railgun/single-tracks --z 5 --spin .001 --speed .2 \
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
  --gpu 0 --out runs/railgun/spherical-to-ring --dry-run
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
  --gpu 0 --jac-chunk 128 --out runs/railgun/spherical-to-ring-refined --dry-run
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
  --out runs/railgun/annular-recovery-k12 --gpu 0 --dry-run
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
  --out runs/railgun/uphill --gpu 0 --dry-run
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
  --out runs/railgun/compactness --gpu 0 --dry-run
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
  --out runs/railgun/frequency-scan --gpu 0 --dry-run
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
  --out runs/railgun/frequency-073-refined-20261101 --gpu 0 --jac-chunk 128
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
