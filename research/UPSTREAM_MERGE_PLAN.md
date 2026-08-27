# Upstream merge plan — GRTLCollaboration/GRTeclyn:develop → `feature/grteclyn-wrapper`

**Written:** 2026-08-17
**Target branch:** `feature/grteclyn-wrapper` (was `feature/interstellar` until 2026-08-26 — see §0)
**Author:** analysis session on the authoring workstation — **nothing was compiled. Every claim below
comes from source inspection and `git merge-tree`, not from a build.**
**Validated:** 2026-08-17 — SHAs, divergence counts, conflict sets (both directions), commit split,
§6 quotes, §7 traps, §8 inventory, and §9 API re-checked against fresh fetches of both remotes.
**Purpose:** hand-off so the merge + port can be done on a machine with CPUs and AMReX.

> **Re-verified on the GPU build node, 2026-08-17.** Collaboration tip is still `7dc7c8b5` — upstream has
> not moved. A real trial merge (not `merge-tree`) reproduced **exactly the 7 conflicts** in §6, same file
> set. The 4 commits added to `feature/interstellar` since the §2 baseline `48aa5a44` touch only
> `research/bondi_dipole/**` and this file, so every source-level claim below still holds.
>
> **Decision: the merge is deferred until after the Bondi-dipole paper is submitted.** Nothing on the
> rerun list (`research/bondi_dipole/Debug.md` §3) needs anything from the 76 upstream commits, whereas
> §7.4 would force a full revalidation of results that already exist. Do not start the port without
> re-reading that decision.
>
> **REMOTE NAMES DIFFER BY MACHINE — CHECK BEFORE RUNNING ANY COMMAND HERE.** This document was written
> where `origin` was the personal fork and `upstream` was the collaboration. On the GPU build node the
> naming is inverted: `origin` **is** `GRTLCollaboration/GRTeclyn` and the fork is `myfork`. Read §4
> before copy-pasting anything — the commands there are written for the authoring machine's naming and
> will merge the wrong branch on the build node.

---

## 0. Re-assessment 2026-08-26 — READ THIS FIRST, it supersedes §1–§4 and §11

**Written:** 2026-08-26 on the authoring workstation (`origin` = fork, `upstream` = collaboration).
**Nothing was compiled.** Every claim comes from `git merge-tree` dry runs and source inspection.
**Validated against:** `origin/feature/grteclyn-wrapper` = `29880500`, `upstream/develop` = `e90fb604`.

### 0.1 What changed since 2026-08-17

| Thing | 2026-08-17 | 2026-08-26 |
|---|---|---|
| Merge target | `feature/interstellar` @ `48aa5a44` | **`feature/grteclyn-wrapper` @ `29880500`** (`feature/interstellar` is gone; its work reached the wrapper branch via `develop`, plus +21 files: `GridTreadmill`, `SpongeZone`, `VarsTools`, `RecentringBox`, `SectorCoreTracker`, `GridTreadmillTest`) |
| `upstream/develop` tip | `7dc7c8b5` (PR #195) | **`e90fb604`** (PR #224) |
| Divergence | 499 ahead / 76 behind | **648 ahead / 243 behind** |
| Merge base | `2bfd19ea` | `2bfd19ea` (unchanged) |
| Conflicting files (one-shot merge) | 7 | **11** — the same 7 + 4 modify/delete |
| Deferral | until Bondi-dipole submitted | **Bondi paper is out** (`69c9d808` rebuilt the arXiv bundle from the published source) — the deferral condition in the 08-17 note is satisfied |

The 167 new upstream commits (PR-level, newest first):

| PR | What | Impact on us |
|---|---|---|
| #224 `remove_make_package` | deletes every `Make.package`; makefiles glob `*.cpp/*.hpp` per `src_dirs` | 4 modify/delete conflicts; our `Source/GRTeclynCore/RL/` subdir is **not** globbed (§0.4) |
| #209 `double_to_real` | `double` → `amrex::Real`, 84 files | mechanical, but re-touches all 7 matter driver files → expect the same 7 files to conflict again in stage 2 |
| #215 `refactor_params2` | **every runtime parameter renamed into scopes**, `SimulationParametersBase.hpp` / `AMReXParameters.hpp` deleted, `GRAMR::set_simulation_parameters` / `simParams()` removed, `CCZ4RHS(dx, Λ)` and `CCZ4RHSWithMatter(dx, G)` constructors, params read via `params_t::fill_params()` from `GRParmParse("scope")` | **second interface break**, and the only one that reaches the Python wrapper (§0.3) |
| #226, #222 | mkdocs site (`docs/**`, ~3,000 lines) | none |
| #208 `sixth_order_derivatives` | real `SixthOrderDerivatives` + `DerivativeBase.hpp` | matter classes must instantiate for both `deriv_t` (already in §9) |
| #211 `bugfix/issue-210` | `ParticleInterpolator` fixes | none for the port |
| #220 | CI workflow | none |

Upstream `Examples/ScalarField` is **still** dead GRChombo code (`GNUmakefile.old`, `BoxLoops`, `MatterCCZ4RHS`). §7.2 stands: `Tests/BSSNMatterTest` remains the only reference caller.

### 0.2 Decision: merge in two stages, not one

Do **not** merge `upstream/develop` in one shot. Merge `7dc7c8b5` first, then `upstream/develop`.

* **Stage 1 — `git merge 7dc7c8b5`** (76 commits, PR #172 + followers). Dry run today: **exactly the 7 conflicts of §6**, nothing else. §5–§10 apply verbatim. Parameter names, `SimulationParameters`, `Main_*.cpp`, and the wrapper are untouched, so **the existing campaign `params*.txt` files and a known-good checkpoint can be replayed unchanged** to validate the numerics port (§7.4). This isolates the physics revalidation from everything else.
* **Stage 2 — `git merge upstream/develop`** (167 commits). Dry run today (from a stage-1 tree): the **4 modify/delete** conflicts (`Examples/BinaryBH/params.txt`, `Source/{GRTeclynCore,Grids,Matter}/Make.package`) plus the 7 matter files again (`double`→`Real` and `params_t` edits land on the hunks we resolve in stage 1). Everything else is plumbing: parameter scopes, constructors, build globs. With stage 1 already validated, any regression here points at plumbing, not at numerics.

One-shot merging produces the same 11 conflicts but forces the matter port, the parameter rewrite, and the wrapper rename to be debugged together against a binary whose params files no longer parse. Not worth it.

**Do not rebase** (§11 still holds — 648 commits over two changed interfaces).

### 0.3 New trap: the parameter rename reaches the wrapper

#215 renamed every key. Old → new, for the keys our files actually use:

| Old (ours) | New (upstream, verified against the `GRParmParse` reads in `Source/**`) |
|---|---|
| `N_full`, `L_full`, `isPeriodic`, `center` | `amr.n_cell`, `geometry.prob_extent`, `geometry.is_periodic`, `geometry.center` |
| `max_level`, `regrid_interval`, `regrid_threshold` | `amr.max_level`, `amr.regrid_int`, `tagging.threshold` (or `tagging.thresholds` per level) |
| `max_box_size`, `min_box_size` | `amr.max_grid_size`, `amr.blocking_factor` |
| `checkpoint_interval`, `plot_interval`, `chk_prefix`, `plot_prefix` | `amr.check_int`, `amr.plot_int`, `amr.check_file`, `amr.plot_file` |
| `plot_vars`, `num_plot_vars` | `amr.plot_vars` / `amr.derive_plot_vars` (no count) |
| `output_path`, `verbosity` | `grteclyn.output_path`, `grteclyn.verbosity` (+ `amr.verbose`, `particle_interpolator.verbosity`) |
| `stop_time`, `dt_multiplier`, `sigma`, `max_spatial_derivative_order`, `nan_check` | `evolution.stop_time`, `evolution.dt_multiplier`, `evolution.sigma`, `evolution.spatial_derivative_order`, `evolution.nan_check` (+ `evolution.num_ghosts`, and **`evolution.max_steps`, which upstream `Main` reads with `get` — required**) |
| `formulation`, `kappa1..3`, `covariantZ4`, `min_chi`, `min_lapse` | `ccz4.formulation`, `ccz4.kappa1..3`, `ccz4.covariantZ4`, `ccz4.min_chi`, `ccz4.min_lapse` |
| `lapse_advec_coeff`, `lapse_coeff`, `lapse_power`, `shift_advec_coeff`, `shift_Gamma_coeff`, `eta` | `gauge.*`, same leaf names (`MovingPunctureGauge::params_t::fill_params`) |
| `hi_boundary`, `lo_boundary` | `boundary.hi_condition`, `boundary.lo_condition` (string names, e.g. `SOMMERFELD_BC`) |
| `activate_extraction`, `extraction_center`, `extraction_levels`, `extraction_radii`, `num_extraction_radii`, `num_points_phi/theta`, `modes`, `num_modes`, `write_extraction`, `extraction_subpath` | `weyl_extraction.{enabled,center,levels,radii,num_radii,num_points_phi,num_points_theta,modes,num_modes,write,path,file_prefix,integral_file_prefix}` (scope name is whatever the example passes to `spherical_extraction_params_t::check_params("…")`) |
| `data_subpath`, `hdf5_subpath`, `pout_subpath`, `print_progress_only_to_rank_0`, `nonzero_asymptotic_vars/values` | **no reader upstream any more.** Sommerfeld asymptotics now come from `StateVariables::asymptotic_values` / `BoundaryConditions::set_vars_asymptotic_values()` — our `nonzero_asymptotic_*` inputs must become code. |
| `G_Newton` (ours: constructor argument) | upstream reads it **unscoped and inconsistently**: `pp.get("G_Newton", …)` in `ConstraintsWithMatter.impl.hpp` with a default of **0**, `pp.queryAdd("G_newton", …)` in `Weyl4WithMatter.impl.hpp`. A missing key silently zeroes the matter contribution to the constraints. Pin this down in the port (one scoped key, one spelling) and raise it upstream (§12.4). |

The table was checked against every `GRParmParse` read in `upstream/develop:Source/**` on 2026-08-26; re-grep (`git grep -E '(queryAdd|get|query)\("' upstream/develop -- Source`) before stage 2 in case upstream moves again. Our own keys (`recipe_*`, `rl_*`, `trajectory_*`, `calculate_*`, `write_extraction`, `extraction_center`, …) are read by our classes and can keep their names, but they must be re-plumbed: `SimulationParametersBase` is gone, so each of our six `Examples/*/SimulationParameters.hpp` becomes a static `check_params()` (pattern: `upstream/develop:Examples/BinaryBH/SimulationParameters.hpp`), and every `sim_params.x` / `m_p.x` read (40 in `Main_RadialRecipe.cpp`, 23 in `Main_SupportedWormhole.cpp`, 13 in `ScalarFieldLevel.cpp`, …) becomes a `GRParmParse` read or a `params_t::fill_params()`.

**Blast radius outside C++** (counted today, `_archive/` excluded): **16 `params*.txt`** under `Examples/` and **69 wrapper files** that hard-code unscoped keys (`grteclyn-wrapper/scripts/campaigns/**`, `scripts/radial/**`, `scripts/wormhole/**`, `src/grteclyn_wrapper/core/params.py`, `core/plot_consumer.py`, `grtresna/solver/{config,params}.py`, `visualisation/**`). `core/params.py` is template-based (it rewrites `output_path`, `amr.check_file`, `amr.plot_file` into a copied `params.txt`), so the templates and the campaign shell overrides are where the rename lands. Every result under `results/` and `research/` was produced with the old keys — **keep the old-key files as they are; they document how those runs were made.** A converter script (old→new) is the right tool; hand-editing 85 files is not.

Also gone in #215: `GRAMR::set_simulation_parameters()`, `GRAMRLevel::simParams()`, `sim_params.just_check_params` (now the free function `just_check_params()` in `SetupFunctions.hpp`), `m_verbosity` / `m_num_ghosts` members on `GRAMRLevel`.

### 0.4 New trap: the glob build misses `Source/GRTeclynCore/RL/`

After #224 a makefile finds sources with `$(wildcard $(dir)/*.cpp)` over `src_dirs` — **one level, no recursion**. Our RL headers live in `Source/GRTeclynCore/RL/` and are listed by hand in our `Source/GRTeclynCore/Make.package` (which the merge deletes). Resolution for all four modify/delete conflicts: **accept upstream's deletion**, then in every one of our `Examples/*/GNUmakefile` and in `Tests/GNUmakefile`:

* drop `include ./Make.package`, `src_pack`, `GRTECLYN_CEXE_*`;
* add `$(realpath .)` and `$(GRTECLYN_SOURCE)/GRTeclynCore/RL` to `src_dirs` (the RL dir is header-only, so listing it only affects `CEXE_headers` and `INCLUDE_LOCATIONS` — the existing `INCLUDE_LOCATIONS += …/RL` lines become redundant);
* switch `include $(AMREX_HOME)/Tools/GNUMake/Make.defs` → `include $(GRTECLYN_HOME)/Tools/GNUMake/Make.defs` (upstream added that file plus `Tools/GNUMake/packages/`; diff `Examples/BinaryBH/GNUmakefile` between `7dc7c8b5` and `upstream/develop` for the exact shape);
* delete `Examples/*/Make.package` and `Tests/*/Make.package` (ours included: `RadialRecipe`, `GridTreadmillTest`).

`Source/Grids/Make.package` and `Source/Matter/Make.package` carry nothing but file lists — nothing to preserve once the globs are in place.

### 0.5 Commands (authoring machine naming: `upstream` = collaboration)

```bash
# 0. discard the stale 08-17 worktree — it holds a conflicted merge of the *old* target
git worktree remove ../GRTeclyn-merge --force && git branch -D chore/merge-upstream

# 1. pin the pre-merge state — every published number was produced from here
git tag pre-upstream-merge-2026-08-26 29880500

# 2. stage 1
git fetch --all --prune
git worktree add ../GRTeclyn-merge -b chore/merge-upstream-2026-08 feature/grteclyn-wrapper
cd ../GRTeclyn-merge && git branch --unset-upstream
git merge 7dc7c8b5            # → the 7 conflicts of §6, resolve per §6–§10
# build Tests, port matter classes + Levels, regression vs a known-good checkpoint with UNCHANGED params files
git commit                    # stage-1 merge commit

# 3. stage 2 — only after the stage-1 regression passes
git merge upstream/develop    # → 4 modify/delete + the 7 matter files again
# accept Make.package deletions (§0.4), re-resolve matter hunks, port params (§0.3), run the key converter
# build Tests + Examples, rerun the same regression with CONVERTED params files

# 4. merge back (§11): only once both stages are green
```

Escape hatches unchanged: `git merge --abort`, `git worktree remove ../GRTeclyn-merge --force`.
On the GPU build node replace `upstream` with `origin` (§4) — and `7dc7c8b5` is a SHA, so it needs no remote name.

### 0.6 Still true from 08-17

§5 (the architectural change), §6 (the 7 resolutions), §7 (the vacuum/matter split trap — still the highest-priority correctness item), §8 (port inventory, now +`GridTreadmill.hpp`, `SpongeZone.hpp`, `VarsTools.hpp` as extra callers), §9 (derivative API), §10 (toolchain trap on the build node, `env.sh` is for running not building), §12.2–12.3 (open questions for upstream).

### 0.7 Stage-1 execution log (2026-08-26, authoring machine) — what is on the branch

**State.** Branch `chore/merge-upstream-2026-08` = `9c18b6b5` (tag
`pre-upstream-merge-2026-08-26`) + the merge of `7dc7c8b5` + the port below,
committed as ONE merge commit and pushed to the fork. **Nothing has been
compiled.** A CPU build of `Tests/` was started on the authoring machine and
killed after 62 AMReX objects — it never reached a GRTeclyn source file, so it
proves nothing. The build/fix loop moves to the GPU node.

**Design chosen for the 7 conflicts (§6).** Rather than force `(coords, time)`
overloads onto every matter class, the drivers dispatch at compile time:

| File | What it is now |
|---|---|
| `Source/Matter/MatterDispatch.hpp` (**new**) | `MatterDispatch::compute_emtensor(matter, ix,iy,iz, state, deriv, h_UU, coords, time)` and `MatterDispatch::add_matter_rhs(matter, …, coords, time)`. Detects via SFINAE whether `matter_t` has the 8-arg / 8-arg `(coords, time)` overload and calls it, else calls the plain upstream 6-arg / 6-arg one. Upstream's `ScalarField` therefore stays byte-identical; our pump/support classes keep their time-dependent physics. |
| `Source/Matter/ScalarFieldKernels.hpp` (**new**) | `Pi_gradient_terms(vars, h_UU, chris, d1_chi, d1_lapse, d1_phi, d2_phi)` (the h^{ij}(…) + Christoffel term of the Π equation), `kinetic_invariant(vars, h_UU, Pi, d1_phi)` (= −Π² + χ h^{ij}∂φ∂φ), `zero(emtensor_t&)`. Shared by every scalar class so the Klein–Gordon RHS is written once. |
| `CCZ4RHSWithMatter.hpp/.impl.hpp` | Upstream's `operator()<formulation, covZ4>(ix,iy,iz, rhs, state)` kept with upstream semantics: **matter contribution only** (§7.1). Added `compute_full_rhs(ix,iy,iz, rhs, state)` = `compute_chi_and_h_ij` + runtime switch on `m_formulation`/`m_params.covariantZ4` into `compute_A_ij_and_Theta_and_Gamma<…>` + `calculate_gauge_rhs` + matter (via `MatterDispatch`, with `Coordinates(IntVect, m_dx, m_center)` and `m_time`) + `add_dissipation` — i.e. the pre-#172 one-kernel semantics. Our constructors `(params, dx, sigma, formulation, G_Newton, center, time)` and `(matter, params, …)` are unchanged, so Level classes only rename the call. |
| `ConstraintsWithMatter.hpp/.impl.hpp` | Upstream structure; `chris = compute_christoffel(d1_h, h_UU)`, EMT via `MatterDispatch::compute_emtensor(my_matter, …, m_deriv, h_UU, coords, m_time)`. Our `(center, time)` constructors kept. `compute_mf` is upstream's (`pp.get("G_Newton", …, 0)` — see §12.4). |
| `Weyl4WithMatter.hpp/.impl.hpp` | `add_matter_EB(EBFields_t&, ix,iy,iz, state, epsilon3_LUU, h_UU, chris)`; EMT via `MatterDispatch` with `m_time`. `compute_mf` still reads `extraction_center`, `formulation`, `G_newton`. |
| `ScalarField.hpp/.impl.hpp` | Upstream (`template <potential_t, deriv_t>`), plus our `trS` fix (`chi * trace(S)`, no extra `−3V`). |

**Matter classes ported to `template <class deriv_t> … (ix,iy,iz, state, a_deriv, h_UU)`**, each keeping its own EMT convention verbatim (phantom sign, `−support_strength`, `½Π²` in GRTresna, U(1)-coupled potentials):

| Class | plain overloads | `(coords, time)` overloads | why |
|---|---|---|---|
| `ExoticScalarField<potential_t>` | EMT, RHS | EMT | `local_support_strength(coords, time)` ramp |
| `ComplexScalarField` | EMT, RHS | RHS | pump `compute_single_field_sources` |
| `ComplexExoticScalarField<potential_t>` | EMT, RHS | RHS | pump |
| `BiComplexScalarField` | EMT, RHS | RHS | pump `compute_bicomplex_sources` |
| `GRTresnaIndependentScalars` | EMT, RHS | RHS | per-lump spotlight pump |
| `ControllerReservoirMatter<Inner, IsBicomplex>` | EMT, RHS | EMT, RHS | reservoir transport needs `d1_vector(c_shift1)` = ∂_iβ^k as `(k,i)`, `d1_sym_tensor(c_h11)` as `(k,l,i)`, advection of ρ_c/j_c; forwards to `Inner` through `MatterDispatch`, so `Inner` needs no time overloads. Nested `D1Vars/AdvecVars` gone. |
| `NoMatter`, `DustMatter`, `EffectiveTeoMatter` | EMT, RHS | — | trivial |

Deleted (9 files, `git rm`): `ComplexScalarField{D1,D2,Advec}Vars.hpp`,
`BiComplexScalarField{D1,D2,Advec}Vars.hpp`,
`GRTresnaIndependentScalars{D1,D2,Advec}Vars.hpp`. Upstream already deleted
`ScalarField{D1,D2,Advec}Vars.hpp` and `CCZ4{D1,D2,Advec}Vars.hpp`.
`Source/Matter/Make.package` was regenerated from the directory (37 headers;
the old one listed the deleted files and a `MovingPunctureGaugeWithMatter`
entry without `.hpp`). Stage 2 deletes Make.package anyway (§0.4).

**Callers.** 14 sites `ccz4rhs(i, j, k, rhs, state)` →
`ccz4rhs.compute_full_rhs(i, j, k, rhs, state)`:
`Examples/RadialRecipe/RadialRecipeMatterDispatch.hpp` (7),
`Examples/RotatingWormholeCollapse/SupportedWormholeLevel.cpp` (6),
`Examples/SupportedWormholeCollapse/SupportedWormholeLevel.cpp` (1).
`Examples/RadialRecipe/RadialRecipeLevel.cpp`: `reduce_ec_margins` EMT now
`matter.compute_emtensor(i,j,k, st, deriv, h_UU)` with `emt.j(i)`/`emt.S(i,j)`;
the curvature-invariant diagnostic (~line 1540) fetches `d1_chi, d1_Gamma
(d1_vector c_Gamma1), d1_h, d2_chi, d2_h (d2_sym_tensor)` and calls the 8-arg
`CCZ4Geometry::compute_ricci(vars, d1_chi, d1_Gamma, d1_h, d2_chi, d2_h, h_UU, chris)`
(`CCZ4Geometry.hpp:400`), `ricci.LL(a,b)`. `SpongeZone.hpp` needs nothing
(`add_dissipation(i,j,k, rhs_cell, state, sigma)` — `num_vars` defaults to
`NUM_VARS`). `Source/Grids/VarsTools.hpp` (namespace `Old`, self-contained) was
left alone.

A `grep` for the old API outside `Source/Matter/` (`D1Vars|AdvecVars|diff1_|diff2_|\.ULL\[|h_UU\[|Tensor<[123],`)
now only hits `Tests/CCZ4RHSTest/*-fdf5a7a.*` (frozen old-code copies the test
compares against — intended) and `INFO(...)` strings in `CCZ4GeometryUnitTest`.

**Where the compiler will complain first (guesses, in order of likelihood; `d1_vector` = `(icomp, idir)`, the `MatterDispatch` `Coordinates` construction and `ScalarFieldVars` were verified by reading the headers).**
1. `Tensor::Rank1 x{a, b, c}` brace-init — used because upstream's
   `ScalarField.impl.hpp:95` does it; if `Rank1` is not an aggregate on the
   node's compiler, switch to element assignment.
2. `constexpr int j_comps[3] = {c_jctrl1, …}` and `const Tensor::Rank1 d1_j[3] = {…}`
   inside a device lambda path (`ControllerReservoirMatter::add_reservoir_rhs`).
3. The anonymous-namespace `AMREX_GPU_DEVICE` helper in
   `BiComplexScalarField.impl.hpp` (fine for nvcc as inline, but check `-Wunused`
   under host-only builds).
4. `emtensor_t` members: upstream's struct is `{Tensor::Rank2 S; Tensor::Rank1 j; Real trS, rho}`;
   classes that accumulate call `ScalarFieldKernels::zero(out)` first — the ones
   that assign every component (`Exotic*`, `Dust`, `Teo`) do not, on purpose.

**On the node (node naming: fork = `myfork`, collaboration = `origin`).**

A campaign may be running from the node checkout, and its wrapper scripts,
params files and executable all live inside that tree — so never `git checkout`
or `make` there while it runs. Work in a second worktree instead (own HEAD,
index and build dirs; shared object store, so commits are visible everywhere):

```bash
cd <campaign checkout>            # campaign tree: fetch only, no checkout, no make
git fetch myfork --tags
git worktree add ../GRTeclyn-merge chore/merge-upstream-2026-08
cd ../GRTeclyn-merge
# 1. drivers first — Tests/ instantiates CCZ4RHSWithMatter/ConstraintsWithMatter/Weyl4WithMatter with ScalarField
cd Tests && nice make -j8 USE_MPI=FALSE USE_CUDA=FALSE && ./Tests3d.gnu.ex   # BSSNMatterTest, EMTensorTest, Weyl4WithMatterTest
# 2. then our classes — RadialRecipe instantiates all of them through RadialRecipeMatterDispatch
cd ../Examples/RadialRecipe && nice make -j8 USE_CUDA=TRUE ...               # the campaign build line
# 3. wormhole examples, 4. regression vs a known-good checkpoint with UNCHANGED params (§7.4)
#    — on a GPU the campaign is not using (CUDA_VISIBLE_DEVICES), 5. stage 2 (§0.5 step 3)
```

`nice -j8` rather than `-j16` so the nvcc build does not starve the campaign's
host threads. Already-running processes are safe from a rebuild either way
(Linux keeps the old inode); the danger is the campaign wrapper's *next*
launch picking up a new executable — which the separate worktree prevents.
When done: `git worktree remove ../GRTeclyn-merge`.

Fix compile errors on this branch and commit them as ordinary commits on top
of the merge commit (no need to amend it). Escape hatch unchanged:
`git checkout feature/grteclyn-wrapper` — the tag pins the pre-merge state and
nothing on the research branch was touched.

### 0.8 Stage-1 execution log (2026-08-27, node) — DONE: one real bug found and fixed, regression PASSED

Worktree recipe above followed as written; the campaign ran uninterrupted
throughout (tree, executables and orchestrator verified untouched after every
step, and it advanced evals while the builds ran).

**Builds — all four targets link.** Toolchain: CUDA 12.1 + the local
OpenMPI 5.0.8 prefix from the wrapper `.env` + system g++ 11.4 (per the
wrapper README: never build with the GRTresna conda env's gcc 15).

| Target | Result | Fix needed |
|---|---|---|
| `Tests/` CPU (`USE_MPI=FALSE USE_CUDA=FALSE`) | clean first pass | none — none of §0.7's four predicted error classes fired |
| `Examples/RadialRecipe` MPI+CUDA (campaign line, `CUDA_ARCH=90`) | links, 157 MB | dead `#include "Cell.hpp"` ×4 (`d7109f27`) |
| `Examples/RotatingWormholeCollapse` MPI+CUDA | links | `VAR_IDX` — macro deleted upstream; its packed-symmetric-index arithmetic is now inlined at the single remaining use, `EffectiveTeoMatter.hpp` (`faf209c7`) |
| `Examples/SupportedWormholeCollapse` MPI+CUDA | links | same commit: GNUmakefile dropped the deleted `Source/AMRInterpolator` src_dir (nothing in the example includes it) |

`Examples/ScalarField` still includes the deleted `Cell.hpp` **on purpose** —
upstream itself only fixed that example after the stage-1 merge point, so the
fix arrives with stage 2; it is not in our build (§7.2).

**Test suite — 16/16 pass, and the h5diff checks are real.** Two traps worth
recording for whoever reruns this:

1. The five matter-critical cases (`BSSNMatter`, `Constraints`, `EMTensor`,
   `Weyl4`, `Weyl4WithMatter`) are doctest **skip-by-default** — a green
   default run proves nothing about the port. Run with `--dt-no-skip=true`
   (the binary uses `--dt-`-prefixed doctest options; bare `-ltc`/`-tc` are
   silently ignored).
2. Their real assertions — `h5diff` vs the stored GRChombo reference files at
   `1e-10` — are compiled out entirely without `USE_HDF5=TRUE`. The build
   needs a **serial** HDF5 (`HDF5_HOME=<serial hdf5 prefix>`; the GRTresna
   env's HDF5 is MPI-flavoured and will not link a serial test build), and the
   run needs `h5diff` on `PATH` plus that prefix's `lib` on `LD_LIBRARY_PATH`.

With both in place: 16/16 cases, 13,327 assertions, including all five h5diff
comparisons — the ported drivers reproduce GRChombo numerics to 1e-10 with
upstream's `ScalarField` (zero-potential caveat stands: these tests say
nothing about potential-dependent matter terms).

**§7.1 verified statically.** `compute_full_rhs` composes
`compute_chi_and_h_ij` → `compute_A_ij_and_Theta_and_Gamma<…>` (runtime switch
on formulation/covariantZ4) → `calculate_gauge_rhs` → matter contribution,
which applies dissipation once at the end; no matter Level calls
`apply_dissipation` (the only caller is vacuum BinaryBH), and all 14 call
sites use `compute_full_rhs` (7 RadialRecipe dispatch + 6 Rotating + 1
Supported).

**Regression (§7.4) — found a real port bug, fixed it, regression now PASSES.**

The first full replays NaN-aborted in `phi_lump3` / `jctrl1` one step after the
first mid-run plotfile (or after level-1 creation), while replays with plots
and derives disabled ran fine — and `compute-sanitizer memcheck` was clean.
Diagnosis chain: `amrex.init_snan=1` (signalling-NaN fill of every FAB
allocation) made the failure deterministic at step 1 even with plots, derives
and regridding all off — pure evolution was reading uninitialized memory; the
same poisoned config on the pre-merge campaign binary ran clean, pinning it on
the port. Root cause: `compute_full_rhs` builds the RHS componentwise — the
vacuum and gauge kernels assign every CCZ4 component, but the matter kernels
only assign the components the active model evolves, while `add_dissipation`
accumulates (`+=`) into all `NUM_VARS`. Matter components the active model
does not evolve (with the bicomplex model: `phi_lump3/4`, `Pi_lump3/4`; plus
`rho_ctrl`/`jctrl1-3`, which `ControllerReservoirMatter` itself writes with
`+=`) therefore integrated whatever the rhs MultiFab allocation happened to
contain. The pre-#172 code was immune: it built the RHS in a zero-initialized
`Vars` struct and `store_vars` wrote every component — implicit zeros for
inactive slots. GPU arena recycling usually returns near-zero garbage, which
is why short replays matched the reference bit-for-bit, why the trigger looked
like "plotfiles + derives" (they churn the arena into returning poison), and
why the sanitizer (which perturbs allocation) saw nothing.

Fix (`29c060e5`): `compute_full_rhs` zero-fills components
`[NUM_CCZ4_VARS, NUM_VARS)` before any kernel runs — 11 lines in
`Source/Matter/CCZ4RHSWithMatter.impl.hpp`, restoring the old implicit-zero
semantics for all 14 call sites and the Tests. Verified: the three
formerly-failing `init_snan` configs now run clean, Tests still 16/16 (13,327
assertions incl. the h5diff comparisons), both wormhole examples rebuild and
run (exit 0).

Reference switched to the campaign's **top-score eval** (`eval_000100`) after
retention (`--keep-top-eval-dirs 3`) deleted `eval_000123` mid-diagnosis; its
params, gridinit, matter json and diagnostics are snapshotted under
`runs/merge_regression/ref_eval_000100/` so no future replay can lose its
reference. Verdict on the full replay with ORIGINAL params (stop_time 26, AMR
to level 1, regrid every 16, plotfiles + `Weyl4 rho_req` derives — through
every previous crash point): exit 0, zero NaNs, all four `.dat` diagnostics
complete at 2600/2600 rows, max relative difference ~1e-10 against the
reference and `energy_conditions.dat` bit-identical. That is GPU run-to-run
noise: **stage 1 passes §7.4**.

**Left to do, in order.**
1. Stage 2 (§0.5 step 3): merge `upstream/develop` (167 commits) — expect the
   4 modify/delete `Make.package` conflicts + the same 7 driver files; then
   the PR #215 params port (`params_t::fill_params`, key-rename converter over
   the params files and the wrapper's param writers, `GRTeclynCore/RL` into
   `src_dirs`). `Examples/ScalarField`'s `Cell.hpp` fix arrives with this
   merge.
2. Rerun the same regression with CONVERTED params (reference stays
   `ref_eval_000100/`).
3. Fast-forward `feature/grteclyn-wrapper` only after both regressions pass.

### 0.9 Stage-2 execution log (2026-08-27, node) — merge + PR #215 params port

Merge commit `04026918` (`origin/develop`, 167 commits) on
`chore/merge-upstream-2026-08`. The campaign ran uninterrupted throughout: its
tree, executables and orchestrator were verified untouched after every step and
it advanced evals (150 → 153) while the builds and replays ran on other cards.

**Design deviation from §0.5 step 3: no params converter.** The plan called for
a key-rename converter run over the params files and the wrapper's param
writers. That was dropped in favour of **injection shims**, because a converter
would have forced a lockstep change to the live wrapper, every stored campaign
params file, and every archived reproduction — for no numerical gain.

Instead, two fork-local headers restored under `Source/GRTeclynCore/`:

| Header | Role |
|---|---|
| `AMReXParameters.hpp` | reads the ORIGINAL flat grid/boundary/output keys |
| `SimulationParametersBase.hpp` | reads the ORIGINAL CCZ4, gauge, dissipation and extraction keys |

Both then **inject** the new-scheme keys into the ParmParse table
(`pp.add`/`pp.addarr`) so upstream's self-reading constructors find what they
now require: `evolution.{sigma,nan_check,num_ghosts,dt_multiplier}`,
`ccz4.{formulation,kappa1,kappa2,kappa3,covariantZ4,min_chi,min_lapse}`,
`gauge.{lapse_advec_coeff,lapse_power,lapse_coeff,shift_Gamma_coeff,shift_advec_coeff,eta}`,
`tagging.thresholds`, `grteclyn.output_path`, `geometry.center`,
`boundary.{hi,lo}_condition` and `weyl_extraction.center`. Consequences:

* **Params files, the wrapper and the campaign are unchanged.** The stage-2
  regression replays the *identical* params file as stage 1 — only the three
  path lines (`output_path`, `amr.check_file`, `amr.plot_file`) are rewritten
  so the replay does not write into a live eval directory.
* Every injection is **guarded on the key being absent**, so a params file
  written in the new style wins and the fork can migrate file-by-file later.
* Injection runs **after** `check_params()`, deliberately: the BSSN branch
  zeroes the kappas, and the injected values must be the ones the solver
  actually used before.

Three port details worth recording, all traps if you redo this:

1. **The boundary enum shifted.** Upstream's new `BoundaryConditions` moved
   `REFLECTIVE_BC` from 2 to 3, so the shim carries the ORIGINAL integer codes
   and maps them to the new *name strings* (`1 → SOMMERFELD_BC`,
   `2 → REFLECTIVE_BC`, `3 → FIRST_ORDER_EXTRAPOLATION_BC`, periodic
   directions → `UNSET_BC`; the old `0`/`4` codes abort). Reading the old
   integers straight into the new enum would have silently changed the
   boundary condition.
2. **Sommerfeld asymptotics are now compile-time.** `nonzero_asymptotic_vars`
   / `_values` no longer exist; the values come from
   `StateVariables::asymptotic_values`. `CCZ4StateVariables` supplies
   `chi = h11 = h22 = h33 = lapse = 1`, everything else 0 — value-identical to
   what the campaign params set, so the boundary is bit-for-bit unchanged. The
   three examples gained a zero-filled `additional_asymptotic_values` for their
   own variables. The old keys are accepted and ignored.
3. **`GRAMR::set_simulation_parameters` is gone.** Each Level class now owns a
   file-scope `const SimulationParameters *` set from its Main
   (`<Level>::set_sim_params(&sim_params)`). Pointer, not copy — the RL bridge
   mutates `sim_params` at runtime and the levels must see it.

`RLActionApplier` was ported the same way: `MovingPunctureGauge` is now
constructed per RHS evaluation and self-reads `gauge.*`, so the applier's EMA
reads the current value out of ParmParse and `add`s the update back (ParmParse
returns the last entry, so `add` overrides).

**Builds — all four targets link.** Same toolchain as stage 1.

| Target | Result | Fix needed |
|---|---|---|
| `Tests/` CPU + HDF5 | links | `rm -rf tmp_build_dir` first — see trap below |
| `Examples/RadialRecipe` MPI+CUDA | links, 157 MB | the four API classes below |
| `Examples/RotatingWormholeCollapse` MPI+CUDA | links | same |
| `Examples/SupportedWormholeCollapse` MPI+CUDA | links | same + a missing `DimensionDefinitions.hpp` include in the shim (`FOR` was only reaching it transitively via RadialRecipe's include order) |

Four upstream API changes account for every build error:

* `FilesystemTools::directory_exists` / `mkdir_recursive` are gone; only
  `ensure_directory_exists(path)` remains.
* `SmallDataIO::write_time_data_line` is now a template — a braced initialiser
  list can no longer deduce its argument, so all 9 call sites pass an explicit
  `std::vector<double>{…}`.
* `PositiveChiAndLapse` self-reads `ccz4.min_chi` / `ccz4.min_lapse` from a
  default constructor; the two-argument form is gone (12 call sites).
* `SimulationParameters::check_params` is now a **static** callback handed to
  `amrex::Initialize`. Legacy-scheme examples validate in their constructor and
  have only a member function of that name, so `SetupFunctions.hpp` now detects
  a static `check_params()` and passes no callback when there isn't one —
  upstream's own examples keep theirs.

**Build trap: stale objects survive a source rename.** `Tests/tmp_build_dir`
held pre-merge `.o` files that make did not rebuild, so the suite aborted on a
params filename that no longer exists in the merged source. Delete
`tmp_build_dir` before trusting any post-merge build.

**Test suite — 16/16 cases, 24,591 assertions, with real h5diff checks**
(`--dt-no-skip=true`, `USE_HDF5=TRUE` against a serial HDF5, `h5diff` on
`PATH`). Up from 13,327 assertions at stage 1 — upstream added coverage. The
five matter-critical cases still compare against the stored GRChombo reference
files at 1e-10.

**Regression (§7.4) — PASSED, and `init_snan` is clean.**

Reference: `runs/merge_regression/ref_eval_000100/` (unchanged from stage 1).

Two runs against it, both on GPU 3 with the merged
`main3d.gnu.MPI.CUDA.ex`, params identical to the reference apart from output
paths (a diff confirmed it):

- **Poisoned-allocation smoke test** (`amrex.init_snan=1`,
  `amrex.fpe_trap_invalid=1`, 200 steps): exit 0, no FPE trap, results match
  the reference to 7.2e-11 with three of four `.dat` files bit-identical. This
  is the technique that exposed the uninitialized-RHS bug at stage 1; the new
  parameter path is clean under it.
- **Full replay** (2600 steps, the campaign's exact top-elite params): exit 0,
  all four diagnostic files complete at 2600/2600 rows.

| file | max rel diff vs reference |
|---|---|
| collapse_diagnostics.dat | 9.8e-11 |
| curvature_invariants.dat | 6.3e-11 |
| constraint_norms.dat | 1.2e-11 |
| energy_conditions.dat | identical |

NaN patterns match row-for-row (the NaNs in `collapse_diagnostics` column 9
are pre-existing in the reference, not a merge artifact). Differences are GPU
run-to-run noise — the same magnitude two runs of the *pre-merge* binary show
against each other.

### What's left after stage 2

1. **Merge back into `feature/grteclyn-wrapper`** (§11 — note the branch name
   there is stale; the target is `feature/grteclyn-wrapper`, not
   `feature/interstellar`). Blocked on purpose: that branch is checked out in
   the main tree, which the live MAP-Elites campaign runs from. Merging now
   would rewrite the campaign's source tree mid-run. Do it after the campaign
   stops, or from a fresh checkout once the user gives the word.
2. **Rebuild the campaign executables from the merged branch** after the merge
   back, and rerun the wrapper's `check_params=1` gate (already verified to
   exit 0 against the merged binary).
3. Optional cleanup: drop the `runs/merge_regression/stage2_*` scratch outputs
   once nothing refers to them (`ref_eval_000100` stays — it is the packed
   reference).

---

## 1. TL;DR

* Syncing means taking **upstream PR #172**, which **replaced the entire matter interface**.
* Textual conflicts are small: **7 files** — identical set whether you merge into `develop` or
  `feature/interstellar` (verified both ways with `git merge-tree`).
* The real work is the **semantic port: 20 files, ~2,650 lines** of matter code that auto-merges cleanly
  and then **fails to compile**. Plus ~423 lines of now-obsolete `*Vars` helpers to delete, and 8 caller
  files to update.
* **Upstream ships no working example of the new matter interface** (§7.2). You are porting against an API
  with no reference caller. Biggest risk in the job.
* There is **no cheap middle path**: the 76 commits are one architectural change plus dependent work.

---

## 2. Reference SHAs

| Thing | SHA | Note |
|---|---|---|
| `upstream/develop` tip | `7dc7c8b5` | Merge PR #195 |
| `origin/feature/interstellar` | `48aa5a44` | **merge target** |
| `origin/develop` tip | `6c8e648a` | |
| merge base | `2bfd19ea` | common ancestor |
| **PR #172 merge commit** | `e5f8b380` | the architectural rewrite |

Divergence `feature/interstellar` ↔ `upstream/develop`: **499 ahead / 76 behind**.
(`feature/interstellar` is 73 ahead / 18 behind `origin/develop`.)

Commit split of the 76:

| Group | Count |
|---|---|
| Inside PR #172 (`Tensor`→`amrex::Array` + kernel fission) | **41** |
| After #172 (TwoPunctures #194, cleanup #204, lint #189, git-SHA #195, derivs fix #213, clang-tools #197) | **35** |

The 35 are **not** independent — e.g. `45b6996b BinaryBH: Update for tensor refactoring` assumes the new
API. Only a handful (git-SHA printing, lint config, clang-tools automation) are truly standalone.

---

## 3. State left on the authoring machine

* Added a remote pointing at `https://github.com/GRTLCollaboration/GRTeclyn.git`
* A sibling worktree on branch `chore/merge-upstream`, based on **`feature/interstellar`**, with
  upstream-tracking unset so a stray `git push` can't hit a real branch.
* That worktree holds a **paused, conflicted merge**. It is disposable — recreate it, don't transfer it.
* `feature/interstellar` and the main working tree were **never modified**.

Discard that state (run from the authoring machine's clone):

```bash
git worktree remove ../GRTeclyn-merge --force
git branch -D chore/merge-upstream
```

Nothing was carried over to the GPU build node — the 2026-08-17 re-verification there used a throwaway
worktree that was removed immediately afterwards.

---

## 4. Reproducing the merge on the build machine

Deterministic — same 7 conflicts every time. **Confirmed by a real trial merge on 2026-08-17.**

**First, resolve the remote names — they are not the same on every machine:**

```bash
git remote -v
# Authoring machine: origin = personal fork, upstream = GRTLCollaboration
# GPU build node:    origin = GRTLCollaboration, myfork = personal fork
```

Set these two once, then the rest of the section is machine-independent:

```bash
COLLAB=origin        # on the GPU build node; use 'upstream' on the authoring machine
git fetch --all --prune
```

```bash
git worktree add ../GRTeclyn-merge -b chore/merge-upstream feature/interstellar
cd ../GRTeclyn-merge
git branch --unset-upstream          # avoid an accidental push to feature/interstellar

git merge "${COLLAB}/develop"        # → the 7 conflicts in §6
```

Escape hatches: `git merge --abort`, or `git worktree remove ../GRTeclyn-merge --force`.

Preview conflicts without touching any tree (needs git ≥ 2.38 — the GPU build node has 2.34, where this
form is unsupported and a throwaway worktree is the only option):

```bash
git merge-tree --write-tree --name-only feature/interstellar "${COLLAB}/develop"
```

---

## 5. The architectural change (this is the whole job)

### Old (your code)

Driver pre-computes `Vars` / `D1Vars` / `D2Vars` / `AdvecVars` and passes them in:

```cpp
compute_emtensor(const Vars &vars, const D1Vars &d1,
                 const Tensor<2, amrex::Real> &h_UU,
                 const Tensor<3, amrex::Real> &chris_ULL) const;

add_matter_rhs(const amrex::CellData<amrex::Real> &rhs, const Vars &vars,
               const D1Vars &d1, const D2Vars &d2, const AdvecVars &advec) const;
```

Plus **your** addition — a coords/time overload threaded through all three drivers:

```cpp
compute_emtensor(const Vars &vars, const D1Vars &d1,
                 const Tensor<2, amrex::Real> &h_UU,
                 const Tensor<3, amrex::Real> &chris_ULL,
                 const Coordinates &coords, amrex::Real time) const;
```

### New (upstream)

Matter class receives **raw grid indices + `Array4` + a derivative object** and computes its own
derivatives. `D1Vars`/`D2Vars`/`AdvecVars` are gone; `chris_ULL` dropped from `compute_emtensor`;
`Tensor<2,Real>` → `Tensor::Rank2`. The class is now templated on `deriv_t` as well.

```cpp
template <class potential_t = DefaultPotential,
          class deriv_t     = FourthOrderDerivatives>
class ScalarField
{
    using Vars = ScalarFieldVars;          // only Vars survives

    emtensor_t compute_emtensor(
        const int ix, const int iy, const int iz,
        const amrex::Array4<const amrex::Real> &state,
        const deriv_t &a_deriv,
        const Tensor::Rank2 &h_UU) const;

    void add_matter_rhs(
        const int ix, const int iy, const int iz,
        const amrex::Array4<amrex::Real> &rhs_state,
        const amrex::Array4<const amrex::Real> &state,
        const deriv_t &a_deriv) const;
};
```

Derivatives are fetched inside the body:

```cpp
const amrex::CellData<const amrex::Real> &state_cell_data = state.cellData(ix, iy, iz);
const Vars vars(state_cell_data);
auto d1_phi = a_deriv.d1_scalar(ix, iy, iz, state, c_phi);
```

### Why a "keep our version" shim is impossible

`CCZ4RHSWithMatter : public CCZ4RHS<gauge_t, deriv_t>`, and upstream replaced `CCZ4RHS`'s whole evaluation
model with index-based kernel fission (`compute_chi_and_h_ij(int ix,int iy,int iz,…)`,
`compute_A_ij_and_Theta_and_Gamma(…)`). Keeping your matter driver means rejecting #172 — the bulk of the
76 commits. Verified, not assumed.

---

## 6. The 7 conflicts, with resolution guidance

All 7 are the **same collision**: you thread `Coordinates &coords` + `m_time`; upstream removed that in
favour of indices + `Array4`. General rule: **take upstream's shape, then re-add `coords`/`time` as extra
trailing parameters.**

### 6.1 `Source/Matter/ScalarField.hpp`
Your side adds a coords/time `compute_emtensor` overload; upstream replaced the base signature.
→ Keep upstream's new signature, add your overload with `(…, const Coordinates &coords, amrex::Real time)`
appended. Keep `#include "Coordinates.hpp"`.

### 6.2 `Source/Matter/CCZ4RHSWithMatter.hpp`
Hunk 1: your `#include "Cell.hpp"` / `"Coordinates.hpp"` vs upstream removing them → keep `Coordinates.hpp`.
Hunk 2: `add_emtensor_rhs` signature, old Vars+coords vs new indices+Array4 → upstream shape + `coords`.

### 6.3 `Source/Matter/CCZ4RHSWithMatter.impl.hpp` — **most dangerous file**

Four hunks; two need real thought.

**(a) RHS zeroing — SILENT-WRONG-RESULTS TRAP.** Your side zeroes the RHS:
```cpp
for (int n = 0; n < rhs_cell_data.nComp(); ++n) { rhs_cell_data[n] = 0.0; }
```
Upstream's side does **not**, and states:
```cpp
// NB: the vacuum solution needs to be computed elsewhere!
// This will only compute the matter contribution
```
This is commit `0bfb08fa Matter: Split out vacuum solution from RHS`. **The matter driver no longer
computes the vacuum CCZ4 evolution.** Each `*Level.cpp` must now run the vacuum RHS and the matter
contribution and combine them. Take upstream's hunk without fixing every Level class and the code compiles
while silently producing wrong physics. **Highest-priority item in the port.** Composition recipe: §7.1.

**(b) your dispatch trait must survive:**
```cpp
if constexpr (std::is_same_v<matter_t, GRTresnaIndependentScalars> ||
              std::is_same_v<matter_t, ComplexScalarField> ||
              detail_matter::has_time_rhs_v<matter_t>)
{ m_matter.add_matter_rhs(rhs_cell_data, vars, d1, d2, advec, coords, m_time); }
else
{ m_matter.add_matter_rhs(rhs_cell_data, vars, d1, d2, advec); }
```
Re-express against the new signature:
`add_matter_rhs(ix, iy, iz, rhs_state, state, this->m_deriv[, coords, m_time])`.

### 6.4 `Source/Matter/ConstraintsWithMatter.hpp`
Include-only conflict. Keep `Coordinates.hpp`.

### 6.5 `Source/Matter/ConstraintsWithMatter.impl.hpp`
Upstream renamed the christoffel argument `d1` → `d1_h`:
```cpp
const auto chris = CCZ4Geometry::compute_christoffel(d1_h, h_UU);
```
and calls `compute_emtensor(ix, iy, iz, state, m_deriv, h_UU)`. Take upstream, re-append `coords, m_time`.

### 6.6 `Source/Matter/Weyl4WithMatter.hpp`
Hunk 1: your `m_time` member init vs upstream's added
`// NOLINTEND(bugprone-easily-swappable-parameters)` → **keep both**.
Hunk 2: `add_matter_EB` signature → upstream shape (`ix,iy,iz,state`, `Tensor::Rank3`, `Tensor::Rank2`)
plus your `coords`.

### 6.7 `Source/Matter/Weyl4WithMatter.impl.hpp`
Matching call-site + definition changes for `add_matter_EB`. Same rule.

---

## 7. Traps

### 7.1 Vacuum/matter RHS split
See §6.3(a). Compiles fine, wrong answers. Affects every `*Level.cpp`. **Verify explicitly.**

The intended composition is demonstrated in `Tests/BSSNMatterTest/BSSNMatterTest.cpp` (~lines 138–170) —
this answers former open question §12.1. Per cell, in order:

1. `compute_chi_and_h_ij(ix, iy, iz, rhs, state)` — vacuum
2. `compute_A_ij_and_Theta_and_Gamma<formulation, covariantZ4>(…)` — vacuum
3. `calculate_gauge_rhs(…)` — vacuum
4. `CCZ4RHSWithMatter::operator()<formulation, covariantZ4>(…)` — matter contribution

Two landmines in that recipe:

* **Dissipation.** The vacuum path keeps `add_dissipation` in a separate `apply_dissipation` kernel
  (`Source/CCZ4/CCZ4RHS.impl.hpp`), which the matter composition **skips** — the matter `operator()` adds
  dissipation itself, once, at the end. A Level class that calls `apply_dissipation` *and* the matter
  operator applies dissipation twice; one that calls neither gets none.
* **Ordering.** Upstream's `add_emtensor_rhs` **assigns** (`=`, not `+=`) `rhs[c_Theta] = 0.0` in BSSN
  mode, so the matter kernel must run *after* the vacuum kernels, as in the test. (The assignment itself
  mirrors pre-split behaviour — BSSN doesn't evolve Theta — but it now stomps whatever the vacuum kernels
  wrote there.)

### 7.2 Upstream has NO working matter example — verify before trusting anything
* `Examples/ScalarField/` upstream still ships sources, but its only makefile is `GNUmakefile.old` →
  **not in the build**, and its `ScalarFieldLevel.cpp` still uses GRChombo idioms (`GRLevelData`,
  `BoxLoops::loop`, `MatterCCZ4RHS.hpp`). Dead code.
* `Examples/KleinGordon/` is a standalone wave solver — greps for `CCZ4RHS` / `add_matter_rhs` /
  `compute_emtensor` return **nothing**. Not a matter example.
* `Examples/BinaryBH/` is vacuum (+TwoPunctures).

The **only** references for the new interface are `Source/Matter/ScalarField.impl.hpp` and the tests
(`Tests/BSSNMatterTest`, `Tests/EMTensorTest`, `Tests/Weyl4WithMatterTest`). Read those first. The
vacuum + matter composition question is answered by `BSSNMatterTest` — see §7.1.

### 7.3 Dormant numerics bugfix
`57c4eb0e Derivs: Fix d1_tensor and d2_tensor` — `d1_tensor` wrongly assumed symmetric indices;
`d2_tensor` initialised `ivar{0}` instead of `ivar{ivar_0}`. **Dormant for you**: in your tree those names
occur only as local variables inside `Source/Grids/FourthOrderDerivatives.hpp` (6 hits, no external
callers). After the port, if matter classes start calling `a_deriv.d1_tensor(...)`, it goes live.

### 7.4 Revalidation
The port rewrites the numerics path of every matter class. Results must be re-validated against a
known-good checkpoint before any paper numbers are regenerated. **Do not treat the merged
`feature/interstellar` as paper-ready until that regression passes.**

---

## 8. Port inventory (from `feature/interstellar`)

Order: drivers → base `ScalarField` → derived matter classes → `*Vars` cleanup → Examples.
Line counts are `wc -l` on `origin/feature/interstellar` (an earlier draft measured the conflicted merge
worktree, which inflated the files touched by the merge).

### 8a. Drivers (do first; these are the conflicted files)
| Lines | File |
|---|---|
| 173 | `Source/Matter/CCZ4RHSWithMatter.impl.hpp` |
| 150 | `Source/Matter/ConstraintsWithMatter.impl.hpp` |
| 127 | `Source/Matter/Weyl4WithMatter.impl.hpp` |
| 92 | `Source/Matter/CCZ4RHSWithMatter.hpp` |
| 74 | `Source/Matter/ConstraintsWithMatter.hpp` (include-only conflict) |
| 67 | `Source/Matter/Weyl4WithMatter.hpp` |

### 8b. Matter classes — auto-merge clean, will NOT compile (**2,653 lines total**)
| Lines | File |
|---|---|
| 320 | `ControllerReservoirMatter.hpp` ← **only on `feature/interstellar`, absent from `develop`** |
| 203 | `ExoticScalarField.impl.hpp` |
| 178 | `BiComplexScalarField.impl.hpp` |
| 173 | `CCZ4RHSWithMatter.impl.hpp` |
| 158 | `ComplexScalarField.impl.hpp` |
| 150 | `ConstraintsWithMatter.impl.hpp` |
| 143 | `ComplexExoticScalarField.impl.hpp` |
| 135 | `GRTresnaIndependentScalars.impl.hpp` |
| 130 | `EMTensor.impl.hpp` |
| 128 | `GRTresnaIndependentScalars.hpp` |
| 127 | `Weyl4WithMatter.impl.hpp` |
| 122 | `ExoticScalarField.hpp` |
| 106 | `ScalarField.impl.hpp` |
| 99 | `EffectiveTeoMatter.hpp` |
| 92 | `BiComplexScalarField.hpp` |
| 91 | `ComplexScalarField.hpp` |
| 91 | `ComplexExoticScalarField.hpp` |
| 79 | `ScalarField.hpp` |
| 72 | `DustMatter.hpp` |
| 56 | `NoMatter.hpp` |

### 8c. `*Vars` helpers — likely **deletable** (423 lines)
`D1Vars` / `D2Vars` / `AdvecVars` no longer exist in the upstream interface:

| Lines | File |
|---|---|
| 66 | `ComplexScalarFieldAdvecVars.hpp` |
| 63 | `BiComplexScalarFieldAdvecVars.hpp` |
| 49 | `GRTresnaIndependentScalarsD1Vars.hpp` |
| 48 | `BiComplexScalarFieldD1Vars.hpp` |
| 46 | `GRTresnaIndependentScalarsAdvecVars.hpp` |
| 46 | `ComplexScalarFieldD1Vars.hpp` |
| 37 | `GRTresnaIndependentScalarsD2Vars.hpp` |
| 36 | `BiComplexScalarFieldD2Vars.hpp` |
| 32 | `ComplexScalarFieldD2Vars.hpp` |

Keep the plain `*Vars.hpp` (constructed from `CellData`) — those survive upstream.

### 8d. Callers to update (vacuum/matter split + signatures)
```
Examples/RadialRecipe/RadialRecipeLevel.cpp
Examples/RadialRecipe/RadialRecipeMatterConstraints.hpp
Examples/RadialRecipe/RadialRecipeMatterDispatch.hpp
Examples/RotatingWormholeCollapse/SupportedWormholeLevel.cpp
Examples/SupportedWormholeCollapse/SupportedWormholeLevel.cpp
Source/Grids/SpongeZone.hpp
Source/Matter/EMTensor.hpp
Source/Matter/MovingPunctureGaugeWithMatter.hpp
```

---

## 9. New derivative API (`Source/Grids/FourthOrderDerivatives.hpp`, upstream)

All take `(int ix, int iy, int iz, const amrex::Array4<const amrex::Real> &state, …)`.

| Method | Returns |
|---|---|
| `d1_scalar` | `Tensor::Rank1` |
| `d1_vector` | `Tensor::Rank2` |
| `d1_sym_tensor` | `Tensor::Sym12Rank3` |
| `d1_tensor` | `Tensor::Rank3` |
| `d2_scalar` | `Tensor::Sym12Rank2` |
| `d2_vector` | `Tensor::Sym23Rank3` |
| `d2_tensor` | `Tensor::Sym34Rank4` |
| `d2_sym_tensor` | `Tensor::Sym12Sym34Rank4` |
| `advection` (+ scalar/vector/tensor overloads) | scalar / `Tensor::Rank1` / `Tensor::Rank2` / `Sym12Rank2` |

`SixthOrderDerivatives` also exists upstream — matter classes are templated on `deriv_t`, so both must
instantiate.

---

## 10. Build

Do this on the GPU build node. AMReX is the sibling `../amrex`, so `AMREX_HOME` resolves on its own from
every `Examples/*/GNUmakefile`.

**Toolchain trap — verified 2026-08-17.** Do **not** `source grteclyn-wrapper/scripts/lib/env.sh` before
building. That script prepends the conda `grtresna` environment to `PATH`, which shadows the system
`g++ 11.4` with a conda `gcc 15.2` (unsupported as a CUDA 12.1 host compiler) and puts **no `nvcc` on
`PATH` at all**. The failure is silent: AMReX loads `nvcc.mak`, every `nvcc` probe returns "not found",
and `make` reports the target *up to date* while compiling nothing. `env.sh` is for **running**, not for
building.

The production artifact is `main3d.gnu.MPI.CUDA.ex` (MPI-linked, launched single-rank as an OpenMPI
singleton — see `grteclyn_wrapper/core/config.py::resolve_executable`), built `USE_RL=FALSE`:

```bash
export CUDA_HOME=/usr/local/cuda
export PATH="${CUDA_HOME}/bin:<sim_root>/local/openmpi-5.0.8/bin:/usr/bin:/bin"
export LD_LIBRARY_PATH="<sim_root>/local/openmpi-5.0.8/lib:${CUDA_HOME}/lib64"

cd Tests && make -j48                # port the tests FIRST — smallest surface, real reference
cd ../Examples/<target> && make -j48 USE_MPI=TRUE USE_CUDA=TRUE USE_RL=FALSE COMP=gnu DIM=3
```

Sanity-check the toolchain before trusting a build — `nvcc` must resolve and `g++` must be the system
11.4.0, not the conda 15.2.0. Back up the working `.ex` first; `make` overwrites it in place.

Suggested order:
1. Resolve the 7 conflicts (§6).
2. Build `Tests/` and fix until green. `BSSNMatterTest`, `EMTensorTest`, `Weyl4WithMatterTest` are your
   reference implementations of the new interface.
3. Port matter classes one at a time (§8b), rebuilding tests after each.
4. Port the Level classes (§8d) — mind §7.1.
5. Delete the obsolete `*Vars` helpers (§8c).
6. Build the Examples.
7. Regression-run against a known-good checkpoint before trusting any number.

---

## 11. Merging back

```bash
# only once tests are green AND a regression run matches a known-good checkpoint
# (branch names updated 2026-08-27: the target is feature/grteclyn-wrapper;
#  feature/interstellar no longer exists)
git checkout feature/grteclyn-wrapper
git merge chore/merge-upstream-2026-08
```

Merging `develop` is a separate, optional exercise — it produces the same 7 conflicts but does **not**
exercise `ControllerReservoirMatter.hpp`, so a green `develop` build would not prove the port complete.

Do **not** rebase — 499 commits replayed over a changed interface means resolving these conflicts hundreds
of times. Merge is the only sane option.

---

## 12. Open questions for upstream

1. ~~How are Level classes meant to compose vacuum RHS + matter contribution after `0bfb08fa`?~~
   **Answered** — `Tests/BSSNMatterTest` demonstrates the composition; recipe and landmines in §7.1.
2. Is `Examples/ScalarField` intentionally dead, or is a ported version coming?
3. Is there a migration guide for out-of-tree matter classes? You are almost certainly not the only
   downstream fork hit by #172.
4. (2026-08-26) `G_Newton` is read unscoped as `"G_Newton"` (default 0) in `ConstraintsWithMatter.impl.hpp`
   and as `"G_newton"` in `Weyl4WithMatter.impl.hpp`. Intended scope and spelling? A run that forgets the key
   gets vacuum constraints with matter evolution.
