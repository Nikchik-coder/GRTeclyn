# Ring spacetimes and spin transport — status

Updated **2026-11-01 (MSK)**. Branch: `feature/optimisation`.

**Decision:** pause the minimal-exotic-matter optimisation campaign and develop
this separate ring-spacetime study using its JAX/Newton infrastructure. The
implementation is now present; numerical GPU validation is pending. The previous text in
this file was a research proposal; it supplied no validated solutions, timing
measurements or evidence of a jet, a hidden vortex or a finite Tipler tube.

## Live and queue

**Authorised November 1:** GPU 0 regression tests, followed by the spherical
reference pilot on 40x6, 56x8 and 72x10, at most 30 Newton iterations per grid.
Each job has four CPU threads, 160 GiB host address space and a 0.5 h timeout;
Jacobian chunks are 128. No AMR checkpoints. Logs and solved fields are retained.
`railgun-regression-20261101` launched **10:05 MSK**, second node/card 0,
commit `fad3d846`. It aborted at **10:05 MSK**, exit 134, during CUDA backend
initialisation after 16 algebra tests; no GPU numerical result was produced.
The platform allocator with preallocation disabled works under the same cap:
`railgun-regression-platform-20261101` ran **10:06–10:07 MSK**, 22.80 s,
40 passed / one failed. Flat, Schwarzschild, Kerr, TD-MPD, parity and existing
solver/winding tests passed. The Gaussian analytic-charge fixture missed its
2e-8 tolerance by a 2.60e-8 interpolation error on 64 radial points; its grid
is being refined to 96 without relaxing the tolerance. Both
cards are idle; scratch remains 47 MB cache / 546 GB free. Persistent log:
`runs/capped_jobs/railgun-regression-20261101/log`. No job is live; ETA none.
The spherical pilot waits for passing regressions. No single-ring, counter-rotation, stacked-ring or
transport experiment is authorised by this go. Speed is unmeasured; the
timeout is a budget, not an ETA. Numerical experiments belong on cluster GPUs.

The designated second GPU node was inspected over SSH on November 1: both
H100 80 GB cards had no compute processes and zero reported utilisation.
Scratch was clean: **47 MB**, entirely `_cache/`, with **547 GB free** on its
filesystem; no run folders, plotfiles or AMR checkpoints were present.
Availability must be checked again before launching. The first node was not
listed in this session.

The cluster checkout is also on `feature/optimisation`, at `485f8d443`; the
workstation baseline inspected here is `ec12706e`. Sync the intended tested
commit before any experiment. The SSH alias and checkout path are recorded
in the untracked `runs/railgun/NODES.local.md`; keep machine identity out of
tracked files. No cluster checkout or environment was changed in this audit.

## Questions to test

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

**Implemented November 1, awaiting numerical acceptance:**
`railgun/model.py` and `problem.py` provide the regular-centre domain, separate
winding fields, analytic parity factors, frequency borders and optional total-J
condition. `geometry.py` reconstructs Cartesian curvature and all Einstein/KG
residuals. `diagnostics.py` and `workflow.py` implement charge/mass balances,
doubled quadrature and three-grid Newton recovery. `reference.py` supplies an
independent spherical BVP. `transport.py` implements TD-MPD motion and matched
energy spin controls; `profiles.py` measures axial magnetic tidal curvature.
`commands/railgun.py` exposes solve/profile/transport, with four study configs
under `studies/`. See [equations](EQUATIONS.md) and [execution](RUNNING.md).
The 17 local algebra/policy tests pass; no GPU or physical acceptance is claimed.
Exact-origin Cartesian interpolation and through-centre trajectories remain
excluded, with an explicit inner stopping sphere. Stability is unassessed.

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

**Next deliverable:** GPU regression results and the independent spherical
three-grid pilot, with any failed gates diagnosed before a ring experiment.
No railgun physics result has yet been established.
