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
A failed gate stops the study and returns exit code 2. Only a passing
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
  grteclyn-wrapper/tests/optimisation/test_railgun_transport.py \
  grteclyn-wrapper/tests/optimisation/test_solver_core.py \
  grteclyn-wrapper/tests/optimisation/test_winding_field.py \
  grteclyn-wrapper/tests/optimisation/test_layout.py
```

Preserve NFS logs, configs, manifests, rejected diagnostics and accepted fields.
Pack verified results into `results/railgun/` only after reviewing their gates.
Do not prune scratch or discard frames as part of a test run.
