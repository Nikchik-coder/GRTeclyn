# Running ring studies

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

### Prepared resolution recovery at omega=0.73

The frequency scan stopped on the 72x10 unimposed constraint at omega=0.73.
`studies/frequency_073_refined.json` changes only the grids to 96x12 / 128x16 /
160x20, keeping frequency, model, branch guards and tolerances. Seed from the
converged but rejected 72x10 field; its use as an initial guess does not accept
its constraint error. Every new grid must make at least two real corrections
and pass independently; the three-grid observable test remains mandatory.

Prepared command, **not authorised or launched** (fresh run-specific go required):

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
