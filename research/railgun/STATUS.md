# Ring spacetimes and spin transport — status

Updated **2026-11-01 (MSK)**. Branch: `feature/optimisation`.

**Decision:** the minimal-exotic-matter optimisation campaign is paused. This
separate study reuses its JAX/Newton infrastructure for regular-centre scalar
rings. The spherical baseline is validated; ring, counter-rotation, stacked
states and axial spin effects remain hypotheses to test.

## Live and queue

**Live:** `railgun-baseline-guards-20261101`, second node/card 0, started
**10:41 MSK**, code `303bdab5`, four threads, 160 GiB, timeout **0.5 h
(11:11 MSK)**. These are two read-only checks against the saved spherical
solution: intrinsic KG/core certification and the integer-winding bound mode.
Completion ETA is unmeasured. Scratch is clean: **47 MB**, only `_cache/`,
**545 GB free**. No plotfiles or AMR checkpoints. The first node was not listed.
Host/checkout details stay in the
untracked `runs/railgun/NODES.local.md`. Synchronisation is **git push/pull only**,
through `myfork`; code and validation archives were transferred that way.

The authorised regression tests and spherical pilots have completed. No
single-ring, homotopy, counter-rotation, stacked-ring or physical transport
job is authorised or queued for automatic dispatch. Regression work on the
three newly identified safeguards continues under the same four-thread,
160 GiB, 0.5 h job cap, GPU 0 and Jacobian chunks of 128. No AMR checkpoints.

## Completed baseline — November 1

- **45 GPU regression tests passed**, 22.34 s, ending 10:21 MSK, code
  `732ed60e`. CUDA placement and float64 are asserted. The tests include
  canonical sources/parity, charge normalization, flat/Schwarzschild/Kerr
  curvature, TD-MPD conservation, the existing Newton/winding regressions and
  fail-closed validation. Portable report: `results/railgun/gpu_regression.json`.
- **The spherical three-grid pilot passed**, 56x8 / 72x10 / 96x12, code
  `732ed60e`, ending **10:22 MSK**. Actual recovery: 1/2/2 Newton updates;
  full solve/check times 11.88/13.60/15.51 s. Final observable drift 1.18e-13.
  Relative discrepancies with the independently solved areal-radius ODE:
  **mass 5.48e-8, frequency 1.12e-8**. This is a stationary numerical baseline,
  not dynamical stability or evidence of a rotating ring.
- The accepted fields, ODE reference, manifests, diagnostics and checksums are
  tracked in `results/railgun/spherical-validated/`; rejected initial and
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
`fd15f724`, ending **10:37 MSK**. Checks against the saved nonflat baseline are
live as recorded above; no nonlinear ring solve has started.

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

**Implemented November 1; spherical acceptance above, ring acceptance pending:**
`railgun/model.py` and `problem.py` provide the regular-centre domain, separate
winding fields, analytic parity factors, frequency borders and optional total-J
condition. `geometry.py` reconstructs Cartesian curvature and all Einstein/KG
residuals. `diagnostics.py` and `workflow.py` implement charge/mass balances,
doubled quadrature and three-grid Newton recovery. `reference.py` supplies an
independent spherical BVP. `transport.py` implements TD-MPD motion and matched
energy spin controls; `profiles.py` measures axial magnetic tidal curvature.
`commands/railgun.py` exposes solve/profile/transport, with four study configs
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

**Next deliverable:** GPU checks of intrinsic KG, discrete-winding seeding and
the through-origin core; then a bounded single-ring initialization proposal.
No rotating-ring or axial-ejection result has yet been established.
