# Cartesian 3+1 evolution of the stronger scalar ring

The first experiment is a completed **unperturbed import and short-evolution
pilot**, not a long-time stability test. Its exact bounded scope is in
[studies/evolution_pilot_070.json](studies/evolution_pilot_070.json).
The separate go for GPU tests, two production exports/core certificates,
four zero-step preflights and two t<=2 evolutions was received November 2.
Both exports, four zero-step startups and two evolutions are now spent.
A separate November 2 go authorised the matching 192^3 completion
described below. Perturbations and longer evolutions remain outside scope.

The subsequent **96^3 / 128^3 / 192^3 Richardson study is complete**;
its separate scope is [studies/evolution_richardson_070.json](studies/evolution_richardson_070.json).
The final member reached t=2 and finished processing at 10:24:52 MSK on
November 2, exit 0. Every approved budget is now spent.
Measured orders and extrapolations are in
[the report](../../results/railgun/reports/evolution-richardson-070.json).

## Source and physical model

Use `results/railgun/studies/frequency-deep/frequency_01/accepted.npz`,
SHA256 `bf92fd0c8a9be3bb75481e693f6927ea82757e30f843d06305e053a77280d82e`.
This is the accepted omega=0.70, k=+1, m=1 single canonical complex-scalar
ring on the 160x20 stationary grid. It has the strongest accepted local
frame dragging (shift norm/lapse 0.51034); this is not a maximum-J claim.
The omega=0.73 transport/core certificate does not certify this source.
The entire containing archive and its three-grid outcome are hash checked.

Evolve with `Examples/RadialRecipe`, `grtresna_complex_scalar`, scalar sign
**+1**, zero quartic/sextic interactions and G=1. No phantom matter, matter
pump, reservoir, superposed throat or new constraint solve is introduced.

## Initial-data conversion

`optimisation/railgun/evolution.py` evaluates the differentiable Cartesian
four-metric and scalar at actual cell centres and writes named-component
Gridinit V2. Each run uses a matching uniform grid with four extra cells
on each face. All valid cells therefore sample an exact file node rather
than a second trilinear interpolation. The physical box is [0,32]^3,
with the ring at (16,16,16). No reflection boundary or axisymmetry is imposed.
First grids are 96^3 and 128^3 (dx=1/3 and 1/4), max_level=0.

For gamma_ij=g_ij, beta_i=g_0i and alpha=(-g^00)^(-1/2), export

```text
K_ij = (-partial_t gamma_ij + D_i beta_j + D_j beta_i)/(2 alpha)
chi_CCZ4 = det(gamma)^(-1/3)
h_ij = chi_CCZ4 gamma_ij
K = gamma^ij K_ij
A_ij = chi_CCZ4 (K_ij-gamma_ij K/3)
Gamma^i = h^jk Gamma[h]^i_jk
```

Metric derivatives are taken before sampling the grid. Theta and the
Gamma-driver auxiliary B^i start at zero. Initial lapse and shift are the
stationary solution's values. The subsequent 1+log/Gamma-driver gauge is
allowed to evolve; coordinate motion alone is not an instability diagnosis.

The stationary action uses a dimensionless complex scalar chi_complex;
GRTeclyn uses two canonically normalized real fields. The conversion is

```text
Phi = chi_complex/sqrt(4 pi)
Pi = + (partial_t Phi - beta^i partial_i Phi)/alpha
   = i(omega+k w) Phi/alpha
```

The real fields use `phi,Pi`, the imaginary fields use
`phi_lump0,Pi_lump0`. Setting the imaginary part or K_ij to zero, dropping
the normal derivative, or using the opposite Pi convention would change
the initial spacetime. The exporter independently checks positive spatial
metric/lapse, det(h)=1, tr_h(A)=0 and finite-box J=-k Q at 1e-10.
It reports finite-box charge/J without equating them with an infinite-domain
measurement or a finite-difference evolution measurement.

The exact centre uses a newly fitted Cartesian corridor: radius 0.4,
degrees 6/8, independent Einstein/KG/curvature agreement at the existing
1e-8 gate. Evolution replaces the transport core's C2 join with a C6
degree-13 Bernstein step, preserving six continuous derivatives needed by
fourth-order second-derivative stencils. The fresh certificate checks both
the metric and scalar with this join. Failure stops export; there is no
fallback to an uncertified origin.
Partial exports keep a `.partial` suffix and cannot launch an evolution.
Inactive branches are bounded before batched evaluation: the outer metric
never sees r=0, and the core polynomial is never extrapolated to a distant
grid cell. Flat-space batch tests cover the exact origin and far field.

## Diagnostics and first pilot

The optional `calculate_complex_scalar_diagnostics=1` writes t=0 and evolving
constraint/collapse streams, plus `complex_scalar_diagnostics.dat`:
finite-box Q, matter J_z, integral |Phi|^2, normalized real/imaginary m=2
scalar-shape moments, and peak |Phi|^2. Charge uses
`(Phi_re Pi_im-Phi_im Pi_re) sqrt(gamma) d^3x`; matter J_z uses the actual
fourth-order field derivatives. Composite sums exclude covered coarse cells.
The m=2 moments are coordinate shape diagnostics, not conserved charges.
The feature defaults off so earlier campaigns keep their original cadence.

Both proposed runs stop at **t=2**, dt=0.02 dx, fourth spatial derivatives,
RK4, covariant CCZ4 with kappa1=0.1 and sigma=0.1. All six outer faces use
Sommerfeld conditions. This short box/time is for checking the handoff;
boundary extent, three-resolution convergence and many dynamical times are
separate requirements for a physical stability result.
The first 96^3 run wrote one extra step at t=2.0066667 because the floating
time remained just below the stop boundary. Its analysis is restricted to
t<=2. The template now additionally limits the step count (300/400) without
changing dt, stopping the 128^3 run at its approved duration.

Run sequentially and stop on failed core, import, preflight or nonfinite
state. First use `--preflight-only` on each grid and inspect its retained
report and frames before the actual pilot. This allows **four zero-step
preflight startups and two evolutions** in total; the actual launcher repeats
the full preflight. Compare the C++ t=0 charge against the export and its finite-difference
matter J against -k Q; inspect initial constraints at both resolutions,
their change during t<=2, amplitude, lapse and m=2 evolution. A large initial
constraint defect or worsening refinement blocks longer evolution.
No claim that spectral 1e-8 residuals survive a much coarser Cartesian grid.

The launcher reuses the established spinning-wormhole supervisor, full
binary/read-key/frame preflight and live consumer, with a ring-specific
required-file and frame contract. All previous default frames plus both
complex components are retained, including slice caches; keep-last is 3.
No AMR checkpoint is configured. Ask explicitly about checkpoint policy
with the run proposal. GPU jobs are capped at 4 CPU threads, 160 GiB host
address space and 1800 seconds each. No SCP; sync through Git only.

## Prepared commands (do not start GPU work without the go)

Use the wrapper venv and the capped-job supervisor. Build on the cluster
with the existing provenance-preserving build script via its ring wrapper:

```bash
bash grteclyn-wrapper/scripts/ops/capped_job.sh start railgun-evolution-build \
  --threads 4 --mem 160 --timeout 3600 -- \
  bash grteclyn-wrapper/scripts/campaigns/railgun/build_binary.sh --tag ring070
```

This is CPU compilation, with no CUDA context or GPU test. The frozen binary,
source stamp and build hash go under `runs/railgun/evolution/bin/` and
`results/railgun/reports/evolution_binaries.tsv`. It never overwrites the
wormhole campaign pin. The first successful binary is
`main3d_ring070r2_3e6466ed_2026-11-02.ex`, source `3e6466ed`, SHA256
`14c6dadf61899ad21773f8cbe9df589f2745b0907d3779218b9d890c7d8019bc`.
Compilation completed 2026-11-02 at 08:51:40 MSK, exit 0, using four CPU
threads and a 160 GiB cap in 0.0456 h. No GPU context was started.
Check GPU occupancy and storage before each actual
GPU job. After approval, first run the targeted exporter/corridor regression
tests on the selected card, then for each approved N:

```bash
# Set N=96, then N=128 only within the approved two-export budget.
# Run this command inside capped_job.sh, --threads 4 --mem 160 --timeout 1800 --gpu.
env XLA_PYTHON_CLIENT_ALLOCATOR=platform XLA_PYTHON_CLIENT_PREALLOCATE=false \
  grteclyn-wrapper/.venv/bin/python -u -m \
  grteclyn_wrapper.optimisation.railgun.evolution \
  --source results/railgun/studies/frequency-deep/frequency_01/accepted.npz \
  --out runs/railgun/evolution/initial-070-n${N} --n ${N} --length 32 --gpu 0

# Then use the actual frozen binary from the build manifest. First add
# --preflight-only, inspect its report/frames and t=0 constraints, and only
# then repeat the same command without that flag to evolve. An identical
# generated template is reused; changing an existing template is refused.
# This wrapper stays foreground so capped_job.sh contains all children.
bash grteclyn-wrapper/scripts/campaigns/railgun/launch.sh \
  --data-dir runs/railgun/evolution/initial-070-n${N} \
  --name ring070-n${N}-t2 --gpu 0 --binary "$RING_BINARY" --checkpoints off
```

Both GPU commands must be wrapped by their own capped jobs. The launcher
also checks the grid SHA256, certificate, frequency, layout and checkpoint
choice before starting anything. No optional `--preflight off` escape is
exposed by the ring wrapper.

## Local checks and remaining work

Fourteen local tests pass: ten ring-export/pilot tests and four shared
preflight tests. Analytic cases cover flat harmonic phase/normalization,
spatially varying rotation and the sign of K_ij, J=-k Q, nonflat conformal
connections, a time-dependent metric's K sign, exact cell/ghost alignment,
the C6 join and its batch derivatives, and rejection of unarchived/uncertified
or mismatched inputs. Shell syntax
checks pass. The stamped CUDA executable compiles successfully; 22 GPU
regressions pass. Both exports and short GRTeclyn evolutions are complete.
The initial unused `hdf5_subpath` key was removed after a refused startup;
that refusal remains archived separately, with no relaxed check.

Through saved t<=2 the coarse/fine maximum charge drift is
0.068895% / 0.017787% (3.8734-fold reduction). Interior Hamiltonian L2 is
1.0334e-4 / 3.4831e-5 at t=0 and 2.4758e-4 / 8.2997e-5 at t=2;
the errors grow during each short run but remain about three times smaller
on the finer grid. Whole-box boundary contamination is retained separately.
Both run logs are finite, all default frames are saved and three plotfiles
per run remain. Archives and portable slice inputs are in
`results/railgun/studies/evolution-070-n96/` and `evolution-070-n128/`.
Summary: `results/railgun/reports/evolution-pilot-070.json`.

## Completed three-resolution Richardson study

The spinning paper's appendix uses N=96/128/192 and
Q_p=(h96^p-h128^p)/(h128^p-h192^p); the Bondi appendix measures constraint
orders in fixed physical interiors, avoiding the absorbing boundary layer.
This study follows those methods with the existing 96^3 and 128^3 archives
and the new **192^3** run. It retains box 32, t<=2, every physical/gauge setting, the
frozen binary and exact source. Only N, its corresponding max_steps=600,
and run/data paths change. The template regression diffs against the actual
archived 128^3 parameters and refuses any further changed key.

The separately approved budget is one targeted regression job, one 192^3
export/core certification, two zero-step startups (inspectable preflight
and actual launch preflight), and one evolution. Each job has four threads,
160 GiB and 1800 seconds, on the second node/card 0 only; checkpoints off,
all frames and slice caches retained, at most three plotfiles. No new GPU
work starts before its separate run-specific go. Stop on failed checks.
The 200^3 padded initial cube is approximately 1.86 GB; it stays on NFS.

`optimisation/railgun/evolution_convergence.py` validates every archive's
checksums, matching source/core contract, frozen binary, physics and gauge.
It selects actual samples at **t=0/0.5/1/1.5/2**, without time interpolation
or using the coarse pilot's t>2 row. For Ham and Mom, whose exact continuum
values are zero, report the two adjacent-grid orders at each time, L0 only,
over the same physical sphere r<8. Do not extrapolate their norms as if
they were a nonzero physical observable.

For finite-box Q, Q(t)-Q(0), matter Jz and integral |Phi|^2, fit the signed
three-grid differences to f(h)=f(0)+C h^p with the unequal spacing ratios.
Print measured p, the extrapolated continuum value and estimated fine-grid
error. Differences <=1e-9 (above the diagnostic printing uncertainty),
nonmonotone triples and orders outside 0<p<=12 remain explicitly unresolved;
there is no assumed p=4 fallback. Fourth-order difference scaling is only a
comparison curve. Q(t)-Q(0) at t=0 is identically zero and has no order.
Raw grid-maximum scalar amplitudes are not used for Richardson fitting,
since the maximizing physical cell changes with resolution.

Nine manufactured-solution and identity regressions pass, covering fractional
orders, either error sign, unequal spacing, exact shared times, noisy and
oscillatory rejection, checksum/gauge/binary mismatches, and the 192^3
template diff. The analysis and plot require all three finished members;
no missing member is synthesized. Rebuild the completed comparison:

```bash
grteclyn-wrapper/.venv/bin/python -m \
  grteclyn_wrapper.optimisation.railgun.evolution_convergence \
  results/railgun/studies/evolution-070-n96 \
  results/railgun/studies/evolution-070-n128 \
  results/railgun/studies/evolution-070-n192 \
  --out results/railgun/reports/evolution-richardson-070.json
grteclyn-wrapper/.venv/bin/python -m \
  grteclyn_wrapper.visualisation.optimisation.plot_ring_convergence \
  results/railgun/studies/evolution-070-n96 \
  results/railgun/studies/evolution-070-n128 \
  results/railgun/studies/evolution-070-n192
```

The JSON has a companion Markdown order table; figures go under figures/,
reports under reports/. Three-grid estimates through t=2 validate the
short-duration numerical handoff, not long-time dynamical stability.

The finer pair's t=2 Ham/Mom orders are **4.01 / 3.83** (coarser pair
3.80 / 3.62). Three-grid charge-change order is **4.677**, matter-J order
**4.269**. Finest maximum charge drift is **0.0024917%**. The estimated
fine-grid Q error is 3.529e-5; the three-point continuum charge-change
estimate is +2.745e-6, rather than exact conservation. Estimates from a
single triplet are not independent error bounds. The original two-grid
comparison remains a historical pilot figure. All 31 targeted GPU tests
passed; all three archives and their matching physics contracts verify.
Both GPUs are idle, three plotfiles per run remain, and every original frame
and slice cache is retained. Commands above do not authorise any repeat run.

After this triplet, choose a sufficiently large domain and three resolutions,
then compare an unperturbed control with explicit small nonaxisymmetric
perturbations. Measure constraint convergence, charge loss/boundary flux,
shape-mode growth and, if collapse occurs, 3D MOTS. A finite quiet run bounds
growth over its tested interval; it does not prove indefinite stability.

## Requested N=192 evolution through t=50

The November 2 request extends the same 192^3 run to t=50 in its original
box. No checkpoint exists at t=2, so reuse the accepted, hash-matched t=0
cube. `evolution_long.py` starts from the actual packed 192^3 params and
changes only stop_time=50, max_steps=15000, run/data paths and the explicit
checkpoint policy. Source, binary, grid, matter, gauge, timestep and output
cadence are verified against the earlier run. No new production export or
JAX startup is needed. A full launch preflight is still mandatory.

The generated consumer entry point now has a multiprocessing main guard;
two spawned workers can process the unchanged 25-step plot cadence. Each
consumer worker uses one CPU thread, while AMReX retains four. The local
regression actually starts spawned children through the generated entry
point. Eleven duration/identity/spawn/shared-preflight checks pass. All default
frames and caches remain mandatory, keep-last is three, host address-space
cap is 160 GiB per process, and the complete foreground job has a 3 h cap.

Before GPU startup the checkpoint choice must be answered explicitly for
this run: off, or on every 1500 steps (5 time units), keep three. The latter
requires `amr.checkpoint_files_output=1`, `checkpoint_interval=1500` and
`checkpoint_keep=3`; both choices are covered by the preparer tests.
The run definition is [studies/evolution_long_070.json](studies/evolution_long_070.json).

The box is only 32 wide and already has boundary-dominated whole-box
constraint norms. Boundary effects can reach the interior before t=50.
The requested run measures longer behaviour in that box; it does not add
long-time Richardson convergence or establish isolated-ring stability.
