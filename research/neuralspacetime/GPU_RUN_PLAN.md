# GPU run plan — the v2 rerun, from zero

**Goal.** Produce every campaign number for this paper on the corrected code
path. Everything measured before 2026-08-26 is **discarded**: the Bondi-dipole
debugging (`../bondi_dipole/docs/MatterDebugg.md`, wrapper README rules
1/3/8/9/10) found five defects that predate and invalidate every campaign —
MAP-Elites, CMA-ES, HQ promotion, the matrix, all of it. Old genomes survive
only as warm-start seeds (`SEED_EVAL_DIRS`); old scores never mix with new
ones, and no old ruling (memory ceilings at a given t, window choices,
"clipped sweep") is trusted until re-measured.

**Method — the bondi run-book style.** One phase at a time. Each phase has a
launch command, a cost, and a pass gate; nothing in the next phase starts
until the gate is green. **Phase 1 is a hard GO/NO-GO: if the pipeline cannot
reproduce bondi-quality initial data and stable matter with every fix in
place, no campaign launches.**

Nothing runs from this laptop. Code reaches the cluster by
commit → push → pull only.

---

## The scoreboard

- [x] **Phase 0** — cluster preflight: env, tests, binary (2026-08-26)
- [x] **Phase 1** — stable-matter gate (**GO/NO-GO**) — **GO**, 2026-08-26,
      all boxes green (A/B vs old binary impossible: `.pre_trsfix` deleted)
- [ ] **Phase 2** — MAP-Elites `qball_traj_fgeo_v2` (200 evals) — **launched
      2026-08-26 ~12:45, unseeded** (v1 tree gone from disk)
- [ ] **Phase 3** — CMA-ES `qball_traj_fgeo_max_cmaes_v2` (200 evals)
- [ ] **Phase 4** — freeze the champion + HQ promotion (FMAX-RM v2)
- [ ] **Phase 5** — refinement matrix (convergence + domain + controls)
- [ ] **Phase 6** — canonical-only control v2
- [ ] **Phase 7** — optional: depth lineage v2 · FRONTIER-1
- [ ] **Phase 8** — packs + paper gate

---

## Why everything re-runs — the five defects

1. **`trS` double-counted the potential** in every matter class (fixed
   `92e2d3a6`, 2026-08-21). Invisible to the constraint monitor, fed only
   `rhs[c_K]`. Every observed dispersal, collapse, retention number and score
   was artefact-contaminated.
2. **The solve grid never landed on the evolution grid.** Search solves ran
   at dx 2.0 (+3 solve AMR levels) against evolution dx 0.5; the metric is
   copied last-source-wins while matter is repainted analytically, so every
   lump was born off the centre of its own well — a directional drift that
   mimics physics.
3. **Two construction methods in one archive.** K=0 maximal slicing switched
   on per candidate iff exotic lumps were present; canonical-only candidates
   got the CTTK `K∝√ρ` birth kick (~4 orders above the K=0 value) and were
   born mid-collapse.
4. **The solve exit door was never checked.** GRTresna prints `Converged!`
   unconditionally; the search tolerance was 1%. Initial-data quality was
   asserted, not verified.
5. **The dispersal gate was absolute** (`final_confined_frac < 0.5` against a
   constant, the run's own t=0 fraction discarded), tilting every score
   toward high-absolute-confinement families.

**What survives:** the infrastructure (queue, MPI verification, launch
conventions), the hardware facts (memory ceilings, solve timings), the packs
as historical record, and old genomes as seeds. Nothing else.

---

## What changed in the wiring (2026-08-26, this branch)

The campaign libs now carry the corrected **defaults** — overriding any of
them back to a pre-fix value is a deliberate, visible act:

| knob | old (silent) | new default | env |
|---|---|---|---|
| Solve grid (search) | 64³ over L=128, ml=3 | computed aligned `N_full·L_dom/L_full` = 256³, ml=0 | `GRTRESNA_DOMAIN_NX/NY/NZ`, `GRTRESNA_MAX_LEVEL` |
| Solve grid (HQ) | ml=3, `--grtresna-n` unset | aligned N, ml=0, forwarded by `run_batch.sh` | `GRTRESNA_N`, `GRTRESNA_MAX_LEVEL` |
| Alignment rail | none | misaligned solve **refuses to launch**; the paint path warns | `GRTRESNA_REQUIRE_ALIGNED_SOLVE=1` |
| Slicing | K=0 iff exotic | **K=0 for every candidate** (+ exotic-safe relaxation) | `GRTRESNA_MAXIMAL_SLICING=1` / `--grtresna-maximal-slicing` |
| Solve tolerance | 1.0% / 0.005 | **0.1% / 0.002** (bondi-tightened) | `GRTRESNA_NL_EXIT_TOLERANCE`, `GRTRESNA_NL_STALL_TOLERANCE` |
| Exit door | unchecked | classified (`converged/stalled/cap`), recorded in `metadata.json`, wrong door **rejected** pre-GPU | `GRTRESNA_REQUIRE_CONVERGED=1` / `--grtresna-require-converged` |
| Solve cores | 1 rank (~46 min at 256³) | **8 ranks** (~7 min, digit-identical, re-verified 2026-08-19) | `RANKS` (search) / `GRTRESNA_RANKS` (promote) |
| Solve timeout | 900 s | 2400 s (search) | `GRTRESNA_TIMEOUT` |
| Dispersal gate | absolute final frac | **relative to the run's own t=0** | `SCORE_CONFINEMENT_BASELINE=absolute` restores old |

The aligned 256³ solves are heavier than the old loose 64³ ones — that is what
the `RANKS` knob pays for. Mind README rule 10: `RANKS ×
MAX_CONCURRENT_GRTRESNA` cores compete with live evolutions; with no evolution
in flight, solves may run freely.

---

## Standing constraints (every run below)

- **GPU ownership flips.** Check `nvidia-smi` for foreign processes before
  every launch wave; commands assume 4 cards (`GPU_IDS="0 1 2 3"`) — drop a
  card from the list if it is reserved that week.
- **A number enters the paper only** with a production-tier run, an acceptance
  criterion fixed before the run, and a pack under `results/` that
  regenerates it.
- Old genomes: `SEED_EVAL_DIRS` only — **never `QD_RESUME` into an old
  archive**, never compare v1 and v2 scores.
- Composite constraint norms only (`L2_Ham_amr` etc.), never the diluted
  cols 2–3.
- Frames on for every HQ/production run (`grteclyn_frames: 1` in manifests);
  no checkpoints (9.6 GB each; re-running is cheaper).
- Pump convention is launcher-enforced: `RL_PUMP_STOP_TIME=-1` paired with
  `GEODESIC_EMIT_MIN_TIME=4`; a non-negative value only for a declared
  pump-off control.
- Runs to t ≥ 40: `GRTECLYN_METRIC_STACK_N_SPACE=257`, and the
  `cache_fidelity` gate is never `--force`d.
- Stop campaigns only via `bash scripts/campaigns/stop_campaign.sh <run dir>`
  (orchestrator first), then verify with `pgrep`.
- Packs scrub machine identity; grep for host paths before committing.

---

## Phase 0 — cluster preflight (no GPU time)

- [x] `git pull` this branch on the cluster; `uv sync` (Python 3.12 — 3.14
      breaks lalsuite); full `pytest tests/ -q` in `grteclyn-wrapper/` passes
      with only the 4 known environmental failures.
      *(2026-08-26: pytest had to be installed into the wrapper venv — it is
      not a declared dependency. 1043 passed + the 4 documented failures; a
      5th failure was a stale test asserting the pre-`08a3dcf5` unigrid
      `regrid_interval` — test fixed. Two launch-blocking regressions found
      and fixed on the way: the campaign's exported
      `GRTRESNA_REQUIRE_ALIGNED_SOLVE=1` leaked into the pytest gate's
      fixture tests (now stripped by `tests/grtresna/conftest.py`), and the
      fresh-run QD driver refused the dir pre-created by
      `campaign_register_launcher` for `launcher.pid` (driver now tolerates
      exactly that one artifact).)*
- [x] **Evolution binary post-dates `92e2d3a6`** (the trS fix). Rebuild if in
      doubt; `main3d.gnu.MPI.CUDA.ex.pre_trsfix` is the broken binary kept
      for A/B — verify no launcher can pick it up:

      ```bash
      git merge-base --is-ancestor 92e2d3a6 HEAD && echo binary-branch-ok
      ls -l Examples/*/main3d.gnu.MPI.CUDA.ex        # mtime after the pull that brought 92e2d3a6
      ```

- [x] GRTresna needs **no rebuild**: `maximal_slicing` is a params.txt key of
      the CTTKHybrid method the BosonStarBH example is already compiled with.
      Confirm the sibling checkout is on `feature/grteclyn-wrapper` (the
      2026-08-26 rewrite; ex-`feature/interstellar`), pulled.
      *(Verified: content byte-identical to the compiled Aug 6 binary's
      source, Q-torus work committed.)*
- [x] Disk: ≥ 150 GB free under `runs/` *(3.5 TB free)*.
- [x] No orphaned orchestrators or solvers alive from earlier sessions
      (`pgrep -af "grteclyn_wrapper|grtresna|main3d|gpu_queue"`).
      *(One caveat found during 0: `main3d...ex.pre_trsfix` no longer exists
      anywhere — the optional Phase 1b A/B is impossible.)*

---

## Phase 1 — the stable-matter gate (GO/NO-GO)

The point of this phase: demonstrate, on one candidate, that the pipeline now
constructs initial data the way the bondi campaign does — aligned, converged
by the right door, one slicing, matter born centred and at rest — and that
the evolved matter behaves like matter, not like the old artefact (immediate
directional drift + dispersal from birth). **If any check fails, everything
stops here until it is fixed. No campaign launches on a red Phase 1.**

### 1a — one throwaway eval through the campaign path (~20 min, 1 GPU)

```bash
cd grteclyn-wrapper
QD_NAME=preflight_stable_v2 QD_TARGET_EVALS=1 GPU_IDS="0" \
SEED_EVAL_DIRS="$(ls -d ../runs/neuralspacetime/search/map_elites/qball_traj_fgeo_v1/eval_000322 2>/dev/null)" \
  bash scripts/campaigns/qball_trajectory/run_fgeo.sh
```

(The seed pins the eval to a known genome — the old gated champion — so the
result is interpretable. If the v1 tree is gone, run unseeded; the checks
below do not depend on which genome ran.)

### 1b — the checks, every one green

- [x] **Solve params as intended** — in `eval_*/grtresna/params.txt`:
      `N = 256 256 256`, `max_level = 0`, `NL_exit_tolerance = 0.1`,
      `maximal_slicing = 1`. *(All exact, plus `NL_stall_tolerance = 0.002`.)*
- [x] **Exit door** — `metadata.json` →
      `grtresna_convergence.exit_door == "converged"`, and the standalone
      twin agrees: *(converged at iteration 8/50, Ham 0.029% / Mom 0.054%,
      1.8× headroom; checker PASS, exit 0.)*

      ```bash
      .venv/bin/python ../research/bondi_dipole/check_solve_exit.py <eval dir>   # exit 0
      ```

- [x] **Alignment** — no `Chombo level ... does not match target dx` warning
      anywhere in the eval log (the rail refuses misaligned solves outright,
      the paint path warns if anything still slips through);
      `check_gridinit_alignment.py` on the gridinit reports centroid offset
      0.0000. *(Zero warnings; solve dx 0.5 == gridinit dx 0.5, straight
      copy. Caveat learned here: the centroid script's symmetry premise only
      holds for the Bondi pair geometry — on an asymmetric search genome it
      reports superposed-well physics, not the transfer bug. For campaign
      evals the rail + equal-dx + born-centred are the check.)*
- [x] **Born at rest** — `collapse_diagnostics.dat` col 4: `max|K| ~ 1e-5`
      at t=0. A value ~1e-1 is the CTTK birth kick — the slicing fix is not
      reaching the solve. *(Better: K, shift, B identically ZERO in the
      gridinit; lapse ≡ 1. The .dat starts at t=0.01 already gauge-evolved
      (7.6e-3), so read birth-K from the gridinit, not the file.)*
- [x] **Born centred** — t=0 row of `small_data/sector_barycenters.dat`
      matches the painted lump positions; no directional drift in the first
      few code units that all lumps share (the rule-1 artefact signature).
      *(This campaign's consumer does not pass `--sector-barycenters`, so the
      .dat does not exist; measured instead from `initial_data.gridinit` +
      `initial_data.matter.json`: phantom sector barycentre within 0.04 of
      painted, per-lump windows ≤ 0.4 with each residual pointing at its
      same-sector neighbour (tail contamination) — no shared direction.)*
- [x] **Matter behaves** — confinement is scored relative to the run's own
      t=0 (`metadata.json` score components carry
      `confinement_final_frac` + the initial→final note); any DISPERSED
      verdict quotes t=0-relative retention, not the absolute constant.
      *(Verdict text: "confined fraction fell to 18% of its t=0 value" —
      the fixed wording. The throwaway genome dispersed 74%→13% and
      late-collapsed (trapped surface t=25.6); rails all fired: 4D trace
      flagged unreliable and zeroed, coordinate-FTL down-gated for
      dispersal.)*
- [ ] ~~**Old binary A/B (optional but cheap)**~~ — impossible: no
      `*.pre_trsfix` binary survives anywhere on this machine (verified in
      Phase 0). The "as in bondi" one-picture demonstration cannot be made.

### 1c — 5-eval smoke of the full campaign loop (~2 h, 4 GPUs)

```bash
QD_NAME=preflight_smoke_v2 QD_TARGET_EVALS=5 GPU_IDS="0 1 2 3" \
  bash scripts/campaigns/qball_trajectory/run_fgeo.sh
```

- [x] All 5 evals: exit door `converged`, no alignment warnings, sane scores.
      *(5/5 converged in 8–9 iterations, Ham ≤ 0.063% / Mom ≤ 0.084%,
      postload gates PASS, scores 27.7–646.5, 4 elites, tiers up to
      "operational". Whole smoke: ~35 min on 4 GPUs.)*
- [x] Solve wall time ~7 min at `RANKS=8` (if ~46 min, the ranks knob is not
      reaching mpirun; if mpirun segfaults at DVM start-up, fall back
      `RANKS=1` and accept the cost). *(7:40–9:20 per solve.)*
- [x] Delete both preflight run dirs afterwards. *(Done 2026-08-26 ~12:40.)*

**NO-GO:** any red box above. Do not tune around a failure — find it. The v1
campaigns are what "tune around it" produces.

---

## Phase 2 — MAP-Elites `qball_traj_fgeo_v2` (200 evals, 4 GPUs, ~2–3 days)

> **Launched 2026-08-26 ~12:45**, detached, **unseeded** — the v1 tree no
> longer exists on disk, so `SEED_EVAL_DIRS` expanded empty (the sanctioned
> fallback below). Measured Phase-1 cost basis: ~8.5 min solve + ~10 min
> evolution ≈ 21 min/eval end-to-end.

The paper's gated lineage (`f_geo_max`: evolving-geodesic shortcut ×
persistence), re-run from scratch on the corrected physics, seeded from the
v1 elites (re-evaluated and re-scored — their old scores are void).

**What this campaign optimizes — precisely** (`objectives.py::_f_geo_max_total`):

```
score = 10000 · ftl_geo_evolving            ← squash(f_geo_evol) × structural_persistence
      +   100 · operational_ftl_geodesic    ← frozen-geodesic credit (zero when 4D trace ran)
      +    60 · ftl_persistence  +  40 · curvature_activity
      + gate · (30·survival + 10·stability + 5·constraint_health)
      +    40 · pump_energy_penalty  (≤ 0)  +  200 · horizon_penalty  (≤ 0)
```

- The **only first-order reward** is the 4D evolving-geodesic shortcut: null
  rays traced through the live evolving metric, scored by fractional
  arrival-time advantage over flat space (1% shortcut = 100 pts), squashed
  toward saturation and **multiplied by matter survival** — a dissolved
  star's shortcut keeps only its persistence fraction.
- **Exotic matter is deliberately free fuel**: there is NO exotic_penalty
  term in this mode (`SCORE_EXOTIC_PENALTY_WEIGHT` is ignored by
  construction). Phantom-heavy genomes pay nothing here. The exotic-penalty
  components are still *computed and stored* in every `score.json`, so
  champions can be ranked by exoticity post-hoc; the reckoning is deferred
  to the refinement matrix (Phase 5) and the paper's framing — these are
  shortcut-depth candidates fueled by phantom matter, not
  energy-condition-respecting solutions.
- **Not a naked maximization**: collapse can't fake a shortcut (graded
  horizon penalty ×200), pump inflation is taxed, and the hard gates sit
  upstream of scoring entirely (require-converged solve, post-load
  constraint gate Ham L2 < 3e-2, 4D-trace h_rel honesty rail, frozen
  credit zeroed when the evolving trace is authoritative,
  coordinate-speed channels down-gated on dispersal).
- **MAP-Elites, not a single optimizer**: elites are kept per cell of an
  8×8 archive over shortcut-strength × shortcut-lifetime descriptors —
  it maps the territory rather than climbing one number.

```bash
cd grteclyn-wrapper
setsid nohup /usr/bin/env \
  QD_NAME=qball_traj_fgeo_v2 \
  QD_TARGET_EVALS=200 SEED=21 \
  SEED_EVAL_DIRS="$(ls -d ../runs/neuralspacetime/search/map_elites/qball_traj_fgeo_v1/eval_* 2>/dev/null | tr '\n' ' ')" \
  GPU_IDS="0 1 2 3" MAX_CONCURRENT_GRTRESNA=2 \
  bash scripts/campaigns/qball_trajectory/run_fgeo.sh \
  > ../runs/neuralspacetime/search/map_elites/qball_traj_fgeo_v2_launch.log 2>&1 < /dev/null & disown
pgrep -f qball_traj_fgeo_v2    # verify the detached launch took
```

Everything else — aligned 256³ solve, 0.1%/0.002 tolerances, maximal slicing,
require-converged, `RANKS=8`, `STOP_TIME=26`, pump on + emit floor 4 — is the
launcher default now. `MAX_CONCURRENT_GRTRESNA=2` keeps 8-rank solves from
starving the four live evolutions (rule 10); raise it if cards sit idle
waiting on solves.

Monitor / stop:

```bash
grep -a "^\[qd\]" ../runs/neuralspacetime/search/map_elites/qball_traj_fgeo_v2_launch.log | tail
bash scripts/campaigns/stop_campaign.sh ../runs/neuralspacetime/search/map_elites/qball_traj_fgeo_v2
```

**Pass gate:**

- [ ] Watch the require-converged rejection rate over the first ~20 evals.
      Rejections are the gate working — but if a large fraction of the space
      stalls at 0.1%, record the fraction and decide *by hand* whether the
      genome region or the tolerance is at fault. Never silently loosen.
- [ ] Spot-check 3 random evals: exit door, `max|K|` at birth, no alignment
      warnings.
- [ ] Archive has a filled front (coverage comparable to v1's shape — not
      its scores).
- [ ] Champion identified; its eval dir preserved.

---

## Phase 3 — CMA-ES `qball_traj_fgeo_max_cmaes_v2` (200 evals, 4 GPUs, ~1–2 days)

Covariance refinement of the Phase-2 champion under the same gated objective,
same window, same gates — the ladder rung the paper reads as "QD finds the
basin, CMA-ES climbs it".

```bash
cd grteclyn-wrapper
setsid nohup /usr/bin/env \
  RUN_NAME=qball_traj_fgeo_max_cmaes_v2 \
  OBJECTIVE_MODE=f_geo_max \
  WARM_START_TRAJECTORY="$PWD/../runs/neuralspacetime/search/map_elites/qball_traj_fgeo_v2/trajectory.jsonl" \
  WARM_START_TOP_K=1 WARM_START_JITTER=0.05 \
  POPULATION=16 MAX_GENERATIONS=13 TARGET_EVALS=200 \
  SIGMA0=0.05 SEED=22 \
  GPU_IDS="0 1 2 3" MAX_CONCURRENT_GRTRESNA=2 \
  STOP_TIME=26 \
  RL_PUMP_STOP_TIME=-1 GEODESIC_EMIT_MIN_TIME=4 \
  SCORE_EXOTIC_PENALTY_WEIGHT=0 \
  POSTLOAD_MAX_HAM_L2=3e-2 POSTLOAD_MAX_MOM_L2=1e-2 \
  bash scripts/campaigns/qball_trajectory/cmaes_run.sh \
  > ../runs/neuralspacetime/search/cma_es/qball_traj_fgeo_max_cmaes_v2_launch.log 2>&1 < /dev/null & disown
```

The three pins that must stay spelled out (`cmaes_run.sh` carries
bicomplex-era defaults that differ from the fgeo parent): `RL_PUMP_STOP_TIME`
+ `GEODESIC_EMIT_MIN_TIME` (launcher refuses to run without them),
`SCORE_EXOTIC_PENALTY_WEIGHT=0`, `STOP_TIME=26`. Population 16 = 4× GPU
slots, never = GPU count.

Resume repeats the same env block with `RESUME=1`.

**Pass gate:**

- [ ] Gate-rejection rate below ~15% (else shrink `SIGMA0` to 0.03 — never
      loosen the Hamiltonian gate).
- [ ] Improvement over the Phase-2 champion, or an honest "eval-N of QD is
      already the optimum" — either closes the ladder.
- [ ] **Freeze the champion**: copy its eval dir to
      `runs/neuralspacetime/hq/sources/qball_traj_fgeo_max_cmaes_v2/` before
      anything else runs.

---

## Phase 4 — HQ promotion: FMAX-RM v2 (1–3 GPUs, ~1 day + analysis)

- [ ] Clone the promotion campaign:
      `scripts/campaigns/promote/fgeo_max_cmaes_v1` →
      `.../fgeo_max_cmaes_v2`. In the clone's `campaign.env.sh`: point the
      source at the v2 freeze, and **delete the `GRTRESNA_RANKS=1` pin**
      (the lib default is now 8). Manifests: `grteclyn_frames: 1` on every
      cell — check it, there is no env override.
- [ ] Launch the headline cell through the framework (it forwards all solve
      knobs and sets HQ geodesic mode itself):

```bash
cd grteclyn-wrapper
bash scripts/campaigns/promote/fgeo_max_cmaes_v2/freeze.sh
DRY_RUN=1 GPU_ID=0 bash scripts/campaigns/promote/fgeo_max_cmaes_v2/run.sh FMAX-RM   # inspect first
GPU_ID=0 bash scripts/campaigns/promote/fgeo_max_cmaes_v2/run.sh FMAX-RM
```

If a run must go through `replay_eval.py` directly instead, two things are
mandatory — the HQ trace mode (the default is `search`: 3 rays, strided
slices, wrong for anything quotable) and the paper-tier env:

```bash
setsid nohup /usr/bin/env \
  GRTECLYN_EVOLVING_GEODESIC_MODE=hq \
  GRTECLYN_GEO_EMIT_INTERVAL=2 GRTECLYN_GEO_MAX_EMISSIONS=25 \
  GRTECLYN_METRIC_STACK_N_SPACE=257 GRTECLYN_FREEFALL_OBSERVER_TIMING=1 \
  GEODESIC_EMIT_MIN_TIME=4 \
  .venv/bin/python scripts/campaigns/hq/replay_eval.py \
  ../runs/neuralspacetime/hq/sources/qball_traj_fgeo_max_cmaes_v2/eval_<N> \
  --name fmax_rm_v2_L128_N256 --runs-dir ../runs/neuralspacetime/hq \
  --gpu 0 --n-full 256 --l-full 128 --max-level 3 --regrid-threshold 0.02 \
  --stop-time 64 --plot-interval 72 \
  --objective-mode f_geo_max --evolving-geodesic \
  --consumer-radii 12 18 24 \
  > ../runs/neuralspacetime/hq/fmax_rm_v2.launch.log 2>&1 < /dev/null & disown
```

(`replay_eval.py` now defaults to the aligned solve N, `max_level 0` on the
solve, 0.1%/0.002 tolerances, maximal slicing and require-converged — no
flags needed; `--grtresna-ranks 8` is worth stating on a busy node.)

**Priors, not rulings — re-measure on this run:** the t≈51 memory ceiling,
the ~2 GB/card/unit growth rate, and the t=32 matrix window were all measured
on trS-biased dispersal. Log `nvidia-smi` every 10 min and re-derive the
ceiling and the matrix window from *this* run's memory and transport curves
before fixing Phase 5.

**Pass gate:**

- [ ] Solve: `converged` door, alignment clean (same checks as Phase 1b).
- [ ] `cache_fidelity` PASS; 4D trace reports `mode=hq` on its first stdout
      line; 5/5 rays at the quoted launch.
- [ ] Memory curve + transport curve extracted → matrix window decided and
      written into the manifest before Phase 5.

---

## Phase 5 — the refinement matrix (~2 days, one card per cell)

Convergence + domain matrix on the frozen v2 champion, through the Phase-4
clone. The grid ladder is a hardware fact that survives the reset: **N =
192 / 240 / 256** at max_level 3 (N=240 → 49.8 GB, N=256 → ~62 GB, N=288 →
OOM; measured 2026-08-18). The window comes from Phase 4, not from the old
plan.

```bash
cd grteclyn-wrapper
GPU_ID=0 bash scripts/campaigns/promote/fgeo_max_cmaes_v2/run.sh FMAX-RC    # L=128 N=192
GPU_ID=1 bash scripts/campaigns/promote/fgeo_max_cmaes_v2/run.sh FMAX-RI    # L=128 N=240
GPU_ID=2 bash scripts/campaigns/promote/fgeo_max_cmaes_v2/run.sh FMAX-DS    # L=96  N=192
GPU_ID=3 bash scripts/campaigns/promote/fgeo_max_cmaes_v2/run.sh FMAX-DS2   # L=112 N=224
# FMAX-RM (L=128 N=256) is the Phase-4 run, reused as the reference rung.

# pump-free twin + free-fall companions — same runner, their own manifests
# (MANIFEST must be absolute; the campaign shells cd to GRTECLYN_ROOT):
MANIFEST="$PWD/scripts/campaigns/promote/fgeo_max_cmaes_v2/manifest_pumpfree.json" \
  GPU_ID=0 bash scripts/campaigns/promote/fgeo_max_cmaes_v2/run.sh --list
MANIFEST="$PWD/scripts/campaigns/promote/fgeo_max_cmaes_v2/manifest_freefall.json" \
  GPU_ID=1 bash scripts/campaigns/promote/fgeo_max_cmaes_v2/run.sh --list
```

**The 4D trace is never run by the campaign** — every cell needs the post-hoc
pass, and the post-hoc script silently degrades to search mode without its
exports:

```bash
export GRTECLYN_EVOLVING_GEODESIC_MODE=hq
export GRTECLYN_GEO_EMIT_INTERVAL=2.0
export GRTECLYN_GEO_MAX_EMISSIONS=<from the manifest — matches the window>
grteclyn-wrapper/.venv/bin/python \
  grteclyn-wrapper/scripts/campaigns/rl/score_evolving_geodesic.py \
  runs/neuralspacetime/hq/<run> --ftl-l 8
# verify the first stdout line says mode=hq; use --dry-run for any
# --max-time comparison, or the truncated result overwrites the full one.
```

**Pre-registered acceptance (fixed now, before launch):**

- [ ] Fine–medium relative difference ≤ 10% on peak f_geo; full ray bundles
      at the quoted launch; grid-to-grid **spread** quoted as the error bar
      (no order fit on f_geo — measure observed order on composite
      constraint norms instead).
- [ ] Compare cells at a common launch time safely inside every cell's
      window — never at each cell's own peak.
- [ ] If AMR regridding noise spoils the ladder: fall back to the
      bondi-proven unigrid methodology (max_level 0, three cell sizes).

---

## Phase 6 — canonical-only control v2 (4 GPUs, ~1 day)

Same gated objective, every per-lump exotic dial pinned to 0. With maximal
slicing now unconditional this is finally a *matched* control — same
construction method as the headline, which the v1 control never had.
`PIN_DIMS` replaces the launcher default, so the physics pins are restated:

```bash
cd grteclyn-wrapper
setsid nohup /usr/bin/env \
  QD_NAME=qball_traj_fgeo_canonical_v2 \
  QD_TARGET_EVALS=200 SEED=23 \
  PIN_DIMS="grtresna_scalar_mass=1.0 grtresna_scalar_lambda=640 grtresna_bs_omega=0.8 \
trajectory_lump0_well_depth=0.15 trajectory_lump1_well_depth=0.15 trajectory_lump2_well_depth=0.15 \
trajectory_lump3_well_depth=0.15 trajectory_lump4_well_depth=0.15 trajectory_well_width=1.667 \
trajectory_lump0_exotic=0 trajectory_lump1_exotic=0 trajectory_lump2_exotic=0 \
trajectory_lump3_exotic=0 trajectory_lump4_exotic=0" \
  GPU_IDS="0 1 2 3" MAX_CONCURRENT_GRTRESNA=2 \
  bash scripts/campaigns/qball_trajectory/run_fgeo.sh \
  > ../runs/neuralspacetime/search/map_elites/qball_traj_fgeo_canonical_v2_launch.log 2>&1 < /dev/null & disown
```

- [ ] **Verify the pin on the first completed evals, as a command** (the
      automated sign rail cannot fail for this model):

```bash
grep -H "recipe_scalar_field_signs" \
  ../runs/neuralspacetime/search/map_elites/qball_traj_fgeo_canonical_v2/eval_*/params.txt \
  | grep -v "= 1 1 1 1 1" && echo "SIGN PIN FAILED — stop the campaign" || echo signs-ok
```

- [ ] Exotic-energy integral 0 on the same evals.

---

## Phase 7 — optional exhibits (run only if the paper keeps them)

**Depth lineage v2** (`f_geo_depth`, ungated): re-run only if the paper keeps
the strength-vs-persistence Pareto frontier as result 2. Same two-stage
pattern as Phases 2–3 with `OBJECTIVE_MODE=f_geo_depth` and the depth
window; then one HQ replay of its champion (`--objective-mode f_geo_depth`).
Remember the v1 verdict "the sweep is clipped at every window" was measured
on broken physics — it is a question again, not an answer.

**FRONTIER-1** (efficiency frontier, descriptor axes f_geo × exotic budget):
requires the `exotic_frontier` descriptor mode first — a code task, not a
launch: axis 2 must be `log10` of `integral_negative_rho` (the POSITIVE
magnitude, constraint_norms col 6; template `search/geometry_atlas/score.py`).
Do **not** wire it to warpfactory's signed `total_negative_energy` — log10 of
a ≤0 value is NaN and the archive silently collapses into one column. Unit
test with a negative-input case, smoke with `QD_TARGET_EVALS=2`, then:

```bash
setsid nohup /usr/bin/env \
  QD_NAME=qball_traj_fgeo_frontier_v2 \
  OBJECTIVE_MODE=f_geo_max DESCRIPTOR_MODE=exotic_frontier \
  QD_TARGET_EVALS=200 SEED=24 \
  SEED_EVAL_DIRS="<v2 champion eval dirs — both lineages' corners>" \
  GPU_IDS="0 1 2 3" MAX_CONCURRENT_GRTRESNA=2 \
  bash scripts/campaigns/qball_trajectory/run_fgeo.sh \
  > ../runs/neuralspacetime/search/map_elites/qball_traj_fgeo_frontier_v2_launch.log 2>&1 < /dev/null & disown
```

---

## Phase 8 — packs + paper gate

- [ ] One pack per campaign under `results/`, each regenerating its tables by
      script; scrub check before committing:

```bash
grep -rnE "/(home|users)/|$(whoami)" results/<new-pack>/ && echo "SCRUB FAILED" || echo clean
```

- [ ] Every quoted number names its source run and pack.
- [ ] Only v2 numbers appear anywhere in the paper; no v1 number survives
      even as a comparison (the scoring baseline changed too — they are not
      commensurable).
- [ ] The rewrite of `article/research.tex` starts only after Phases 2–5
      land; the current text is a corrupted record of the invalidated
      campaigns and is not edited until then.

---

## Appendix — operational reference (kept because it still applies)

**Conventions that bite.** Detached launches spell out `/usr/bin/env` (a bare
`env` is shadowed on this node by a snippet that exits 0 silently). Verify
every detached launch with `pgrep -f <run name>` before trusting its log.
`ps`/`top`/`pgrep`/`free` are unreliable on this node —
`scripts/ops/sweep_ranks.py` walks `/proc` directly; use it to find and kill
leftovers (orchestrator first, then workers).

**The queue (press and forget).** For replay-shaped work, prefer
`scripts/campaigns/lib/gpu_queue.sh`: one detached runner per pool, jobs
claimed atomically from `pending/`, failures isolated in `failed/`. Prestage
every constraint solve on CPU (`--solve-only` on `replay_eval.py`,
`SOLVE_ONLY=1` through the promote framework), and let the solve job `mv` the
staged evolve job into the GPU pool — the GPU never waits on a solve. Jobs
run in their worker's foreground; the runner is the only thing detached.
Stop dispatch with `touch <pool>/STOP`.

```bash
QROOT="$PWD/../runs/neuralspacetime/_queue"
mkdir -p "$QROOT/gpu/pending" "$QROOT/solve/pending"
setsid nohup /usr/bin/env QUEUE_GPU_MEM_MAX_MB=2000 \
  bash scripts/campaigns/lib/gpu_queue.sh "$QROOT/gpu" 0 1 2 3 \
  > "$QROOT/gpu_runner.log" 2>&1 < /dev/null & disown
setsid nohup /usr/bin/env \
  bash scripts/campaigns/lib/gpu_queue.sh "$QROOT/solve" s1 s2 \
  > "$QROOT/solve_runner.log" 2>&1 < /dev/null & disown
```

**Hardware facts (measured, still valid).** Single-GPU ceiling at max_level 3
is N=256 (~62 GB at start); N=240 → 49.8 GB; N=288 → OOM. Multi-GPU
evolution works and buys **headroom, not speed** (per-card memory splits;
throughput unchanged). 8-rank GRTresna solves at 256³: digit-identical to 1
rank, 6.6× faster (~7 min). Memory grows as matter disperses (AMR tags more
cells) — the growth *rate* is genome- and physics-dependent, so re-measure it
per champion (Phase 4) before believing any ceiling.

**Disk.** Delete a run's `initial_data.gridinit` once its score is packed
(regenerable in ~7 min); delete `small_data/metric_stack` once the 4D trace
is scored and packed (~15–30 GB per long run). No checkpoints, ever.

**Run tree.** Everything lands under `runs/neuralspacetime/`
(`search/map_elites/`, `search/cma_es/`, `hq/` + `hq/sources/`,
`experiments/`, `pilots/`, `_logs/`, `_queue/`). `runs/bondi_rerun` and
`runs/rotating_wormhole` are separate projects — untouched.

**History.** The v1 plan/debug log this file replaces, and the two retired
debug logs (`Debug.md`, `DebugPreGPU.md`), live in git history; the v1
campaign packs under `results/` remain the record of the superseded
iteration. Nothing in them is load-bearing for v2.
