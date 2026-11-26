# CUDA rebuild and evolution comparison — 2026-11-12

The tested evolution fields reproduce to floating-point roundoff. The Weyl4
diagnostic does not reproduce the old default: the merge restores a matter
contribution that the old callback omitted unless `G_newton` was specified.

The upstream history identifies the change precisely. Commit `d4541f2c1`
introduced Einstein sources containing `8*pi*G`; `7c510350f` switched Weyl4
to those sources and removed the callback's lowercase `G_newton` lookup
with its zero default. Thus `-4*pi*G*STF(S)` became
`-0.5*STF(source.S)`, the same expression when the old coupling is set
correctly. The vacuum electric/magnetic tensors and tetrad projection did
not change. Upstream `4a474a49e` also filled derived ghost cells, a fix
already present in this fork before the merge.

The merged callback retains the upstream source convention, plus the fork's
explicit global `G_Newton` override and coordinate/time-aware matter dispatch.
Without that override, native `ScalarField` uses `scalar_field.G_Newton`;
research classes without native coupled sources use G=1. Restoring the old
zero default would reintroduce the missing matter contribution.

Independent callback regression: `Tests/MatterDispatchTest/WeylMatterCouplingTest.cpp`
checks an analytic anisotropic stress on flat geometry, time-dependent stress,
native ScalarField coupling at G=0.3, explicit G=2 and G=0, output component
offsets and ghost cells. This is an isolated formula fixture, not an Einstein
solution. Its 60 assertions pass; together with MatterDispatch, Weyl4 and
Weyl4WithMatter, the targeted CPU run passes 4 cases / 75 assertions
(`weyl-coupling-tests.txt`). The review required no further production formula
change; the CUDA control above already exercises the corrected implementation.

`builds.json` records six executable hashes: BinaryWormholeMerger,
SpinningWormhole and RadialRecipe before (`66ed1a658`) and after (`ef14909fc`)
the merge. Both arms used the same H100 node, CUDA/MPI flags, compiler and
AMReX revision. The three updated binaries built successfully; production
launcher pins were not changed. SpinningWormhole was built, not evolved here.

The merger comparison reused the archived `place_d8_step1_csm` input:
N128, L64, three refinement levels, mode-3 initial constraint solve, one
coarse step to t=0.01. All 20 stored evolution fields agree within 4.8e-16.
Constraint norms also match the archived research run at printed precision.
Weyl4 differs by up to 0.0371. The control changes only the old callback's
`G_newton` to 1: all 22 plot fields then agree within 7.1e-15.
At R=14, the initial real l=2,m=0 mode changes from 1.4060318e-3 to
1.2134236e-3 (13.7%). This initial near-field difference does not measure
the effect on a published radiated energy or late waveform.

The scalar comparison reused the archived N128 unigrid lone-star t=10
diagnostic and its original initial-data file (hash in `builds.json`). Both
arms completed 1,001 steps to t=10.01. All 20 stored evolution fields agree
within 3.2e-15; `rho_req` agrees within 1.4e-15. Weyl4 differs by up to 7.4e-9.
Both original-input preflights identified the same 47 unread historical keys;
only those inactive lines were removed, identically, before the full runs.
`scalar_unused_keys.json` records them. The initial-data path was relocated
and checkpoint output disabled; active physics and numerical parameters,
stop time and plot cadence were retained. Normalized inputs are identical
between the before/after arms of each case.

`placement_step1.json`, `placement_coupling_control.json` and `scalar_t10.json`
compare every stored cell/field on identical AMR hierarchies, without
interpolation. Maximum differences and unweighted RMS values include all
stored grids, including coarse cells covered by finer levels. The tolerance
is 1e-12 + 1e-9 times each field's maximum reference magnitude. Non-finite
cells fail; time, geometry and field-set differences are refused. Reusable
checker: `grteclyn-wrapper/scripts/validation/compare_evolution_plotfiles.py`.
`streams.json` compares the saved diagnostic streams; expected missing-MOTS
NaNs are compared by their masks. The raw streams and selected frames are
included alongside normalized parameters; output/input path placeholders
must be resolved for a rerun.

All five evolution jobs and full-frame consumers exited successfully. No
checkpoints were written. Completed scratch plotfiles were removed after
packing; all NFS frames and slice caches remain. Logs and binaries remain
under untracked `runs/`; scratch cleanup is logged in the merger manifests.
No long merger/spinning evolution or full-paper reproduction is claimed.
