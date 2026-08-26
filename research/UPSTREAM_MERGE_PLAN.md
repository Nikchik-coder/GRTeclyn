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
git checkout feature/interstellar
git merge chore/merge-upstream
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
