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
  --source results/railgun/spherical-validated/accepted.npz \
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
  --source results/railgun/spherical-validated/accepted.npz \
  --resume results/railgun/spherical-to-ring-resumed --refine-resume \
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
  --source results/railgun/annular-gap-screen/k12_128x16.npz \
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
