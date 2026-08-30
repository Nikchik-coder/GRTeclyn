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
- [x] **Phase 2** — MAP-Elites `qball_traj_fgeo_v2` (200 evals) — **DONE
      2026-08-27 06:00**, 200/200 in 17h15m, unseeded (v1 tree gone from
      disk). Champion `eval_000194`, score 3945.3 (f_geo 15.6%, survival
      0.495); 9 elites, 14% coverage; 59% of evals scored.
- [x] **Phase 3** — CMA-ES `qball_traj_fgeo_max_cmaes_v2` (200 evals) — **DONE 2026-08-28 01:25**, 200/200 in 15h30m. Champion `eval_000187`, score 4169.2 (+5.7% over the Phase-2 champion; f_geo 15.82%, survival 0.516, persistence 0.840); 9.0% gate rejections, 1 solver crash in 200.
- [x] **Phase 4** — freeze the champion + HQ promotion (FMAX-RM v2) — **DONE 2026-08-29**, 6.23 h, solve converged (ham 0.078%, mom 0.085%). **The champion did not survive promotion:** HQ score **26.5** against a search score of 4169.2. Matter dispersed to 18% confined fraction (persistence 0.01), a horizon formed and collapsed at t=34.67/64, and the FTL channel was gated to ×0.01. Ray trace blind for 52% of the run; only t ≤ 26 is quotable.
- [x] **Phase 5** — refinement matrix: 4 cells **DONE 2026-08-30**, all four solves converged. **f_geo spread 1.2% across a 33% change in spacing and box size** (0.1549–0.1568, tolerance 10%) — geometry converged. Critically the **dispersal converges too** (retention 0.429–0.442, spread ×3.01–3.07), so the matter coming apart is physical, not numerical, and the Phase-4 refutation stands. Remaining: pump-free twin + 3 free-fall companions.
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
score = 10000 · ftl_geo_evolving            ← (f_geo_evol − 0.001)/0.199 × structural_persistence
      +   100 · operational_ftl_geodesic    ← frozen-geodesic credit (zero when 4D trace ran)
      +    60 · ftl_persistence  +  40 · curvature_activity
      + gate · (30·survival + 10·stability + 5·constraint_health)
      +    40 · pump_energy_penalty  (≤ 0)  +  200 · horizon_penalty  (≤ 0)
```

- The **only first-order reward** is the 4D evolving-geodesic shortcut: null
  rays traced through the live evolving metric, scored by fractional
  arrival-time advantage over flat space, rescaled so a 20% advantage reads
  as 1.0, and **multiplied by matter survival** — a dissolved star's shortcut
  keeps only its persistence fraction. The scale is **linear and uncapped
  above 20%**: depth beyond the target still pays (`ftl.py::_geo_magnitude`).
  The old saturating form is what turned v1 into a matter-retention contest
  — do not reintroduce a `min(..., 1.0)` here.
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

- [x] Rejection rate recorded and inspected by hand (see below). **Not**
      loosened.
- [x] Spot-checked evals 58 / 131 / 138 (+ the champion, 194): all four exited
      the solver through the `converged` door at NL iteration 8, all passed the
      post-load gate, all evolved to `exit_code 0`. The only warnings in the
      logs are `shell extraction failed ...` from the psi4 shell extractor,
      which the campaign runs with `--no-psi4` — cosmetic, no alignment
      warnings anywhere.
- [x] Archive front filled: 9 elites, all on the `ftl_lifetime = 1.0` edge.
- [x] Champion identified (`eval_000194`) and its directory survived the
      pruner.

### Phase 2 results — COMPLETE 2026-08-27 06:00

200/200 evals in **17h15m** wall (11.6 evals/hour, solve-bound throughout;
the four GPUs were never the bottleneck).

| outcome | n | share |
|---|---|---|
| scored (`gpu_ok`) | 118 | 59.0% |
| post-load constraint gate | 62 | 31.0% |
| GPU evolution failed | 10 | 5.0% |
| solver rejected (not converged) | 7 | 3.5% |
| solver crashed | 3 | 1.5% |

Scored-tier histogram: 64 `operational`, 29 `nontrivial`, 23 `constructed`,
2 `rejected`. Median scored eval 316, mean 744, max 3945.

**Archive:** 9 elites, coverage 9/64 = 14%, flat from ~eval 90 onward. Every
elite sits in the top row of the lifetime axis (`ftl_lifetime = 1.0`) — the
shortcut channel, when it exists at all, is open for the whole 26-unit window.
The strength axis spreads across cells 5–7. The empty 55 cells are short-lived
channels, which this matter model appears not to produce.

**Top elites** (`f_geo` = raw 4D arrival-time advantage; `surv` = matter
survival multiplier; score = 10000 · (f_geo−0.001)/0.199 · surv + shaping):

| rank | eval | score | f_geo | surv | cell |
|---|---|---|---|---|---|
| 1 | **194** | **3945.3** | 0.156 | 0.495 | [6,7] |
| 2 | 100 | 3577.3 | 0.147 | 0.480 | [5,7] |
| 3 | 173 | 3331.4 | 0.176 | 0.371 | [7,7] |
| 4 | 156 | 3310.9 | 0.178 | 0.365 | [7,7] |
| 5 | 24 | 3063.6 | 0.170 | 0.350 | [6,7] |
| 8 | 104 | 2498.1 | **0.200** | 0.246 | [7,7] |

The board is a clean **depth-vs-survival trade**: the deepest shortcut found
(eval 104, 20.0%) ranks 8th because three-quarters of its matter is gone by
t=26. The survival multiplier, not the shortcut term, decides the ranking.

**Champion `eval_000194`** — 15.6% shortcut along the z axis, rays launched at
t=8, arriving t=20.15 against a flat-space reference of 14.4. 3/3 rays reached
the detector, none captured, null condition held to 4.6e-4. Solver exited
`converged` at NL iteration 8 (Ham 0.077% against the 0.1% door, headroom
1.16×); post-load Ham L2 0.0259 against the 0.03 threshold. 498 s of GPU time.

Physically it is a **stationary, continuously pumped cloud**, not a travelling
bubble: activity 67 → 227, rms radius 6.5 → 16.1 (2.5× spread), confined
fraction 0.658 → 0.326 (retention 0.495). The phantom component drains outward
faster than the canonical one — canonical share climbs 0.20 → 0.40 over the
run.

### Caveats carried forward to Phase 5

Three, all recorded rather than acted on:

1. **Most of the shortcut is initial data, not dynamics.** The emission sweep
   fires ray fans at t = 0, 2, … 12. For the champion it reads
   0.137 → 0.141 → 0.147 → 0.155 → **0.156** → 0.145 → 0.000(no rays). So 88%
   of the peak is already present at t=0 and the evolution adds ~14% on top.
   Eval 100 is the same story (0.120 at t=0 vs 0.147 peak, 82%). The frozen
   final-snapshot probe independently returns 0.144 for eval 100 against the
   evolving 0.147 — a 2% difference. The 4D machinery is genuinely dynamical
   (seven launch times give seven different answers, which a static metric
   cannot do), but *these particular solutions are nearly stationary*. Do not
   describe them as dynamically grown corridors.
2. **The champion's well is deepening fast at the end of the window.** min χ
   runs 1.00 → 0.955 → 0.920 → 0.931 → 0.903 → 0.890 → 0.741 → **0.715** over
   t = 0 … 26. No horizon forms inside the window (`horizon_penalty = 0`) but
   the last three samples are a steep dive, and the t=12 ray launch failed to
   reach the detector at all. Phase 5 should re-run this genome past t=26 to
   see whether it collapses just outside the scoring window.
3. **The post-load rejections cluster just above the line.** The 62 rejected
   evals have Ham L2 between 0.0320 and 0.0785, median 0.0380, against a
   0.03 threshold — the median failure is 27% over, not orders of magnitude.
   The population sits *on* the gate rather than far from it, so the 31%
   rejection rate is sensitive to the exact threshold. Left untouched: this is
   a finding about where the genome space lives, not a reason to move a
   tolerance mid-campaign. Revisit only with a deliberate, documented decision.

**Pruning note:** the campaign's own pruner kept 7 eval directories
(3, 58, 100, 131, 138, 173, 194). The top three elites survived; the other six
elites' directories were pruned. Their genomes are preserved in `archive.json`
and `trajectory.jsonl`, so they are reproducible, but their plotfile-derived
`small_data` is gone. Re-solve from the genome if Phase 5 needs them.

---

## Phase 3 — CMA-ES `qball_traj_fgeo_max_cmaes_v2` (200 evals, 4 GPUs, ~1–2 days)

> **Post-merge rebuild, 2026-08-27 09:45.** Work moved to branch
> `feature/merger`, which carries the 167-commit upstream merge (ParmParse
> params rework + `Make.package` removal) plus the BinaryWormholeMerger
> example. `Examples/RadialRecipe/main3d.gnu.MPI.CUDA.ex` was rebuilt from
> scratch (`make -j16 USE_CUDA=TRUE USE_MPI=TRUE COMP=gnu CUDA_ARCH=90`,
> exit 0, 157.7 MB). The champion's `params.txt` re-parses clean under the
> new `BaseParameterChecker` (`check_params=1`, exit 0, no unknown or
> deprecated keys). The pre-merge binary is kept aside for A/B.
>
> **⚠ Binary discontinuity.** Phase 2 ran end-to-end on the *pre-merge*
> binary (2026-08-23). Phase 3 runs on the post-merge one, so the warm-start
> champion's 3945.3 was not scored by the code that will refine it. CMA-ES
> generation 1 re-evaluates genomes jittered around that champion, so
> generation-1 scores are the A/B: if they land near 3900 the merge is
> score-neutral and the ladder is sound; if they collapse, Phase 2 must be
> re-run on the new binary before the ladder means anything. **Check
> generation 1 before trusting anything downstream.**
>
> **RESOLVED 2026-08-27 11:19 — the merge is score-neutral.** Generation 1
> (16 evals, 12 scored) reproduced the Phase 2 champion on the post-merge
> binary at **3945.09 vs 3945.3** (0.005% apart), with the generation top at
> **3949.4**. Eight of twelve scored evals sit in the champion basin
> (3532-3949); the other four collapsed (697, 413, 29, -5), which is normal
> sigma0=0.05 exploration, not a code regression. Phase 2 does **not** need
> re-running; the ladder holds.
>
> Post-load gate rejected 4/16 (25%) in generation 1, all clustered just
> above the 3e-2 threshold (Ham L2 0.0331, 0.0368, 0.0377, 0.0382) - the
> same near-miss band recorded for Phase 2. Recorded, not acted on; the
> threshold stays where it is.

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
  GPU_IDS="0 1 2 3" MAX_CONCURRENT_GRTRESNA=3 \
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

**Solve concurrency raised 2 → 3**, on the Phase-2 measurement rather than a
guess: that campaign was solve-bound for all 17h (11.6 evals/h against a
2-solve ceiling of ~14/h) while the four GPUs idled — the champion's evolution
took only 498 s. Three concurrent 8-rank solves lift the ceiling to ~21/h and
still use just 24 of 128 cores. `USE_PIPELINE=1` (launcher default) streams
candidates within a generation, and population 16 keeps the `tell()` barrier
amortized, so solves run continuously exactly as they did under MAP-Elites —
no batch-wait between generations.

Resume repeats the same env block with `RESUME=1`.

**Pass gate:**

- [x] Gate-rejection rate below ~15% (else shrink `SIGMA0` to 0.03 — never
      loosen the Hamiltonian gate). **9.0%** (18/200) — `SIGMA0` stays 0.05.
- [x] Improvement over the Phase-2 champion, or an honest "eval-N of QD is
      already the optimum" — either closes the ladder. **Improvement: +223.9
      (+5.7%)**, monotonic across 12 of 13 generations.
- [x] **Freeze the champion**: copy its eval dir to
      `runs/neuralspacetime/hq/sources/qball_traj_fgeo_max_cmaes_v2/` before
      anything else runs. **Frozen 2026-08-28 01:45** via
      `scripts/campaigns/promote/lib/freeze_champion.sh` (112 KB:
      `CHAMPION.json` + `eval_000187/` genome + provenance). The tool
      deliberately omits `initial_data.gridinit` — promotion re-solves at the
      HQ resolution, so the 531 MB search-grid file is dead weight.
      **Freeze by hand and you get it wrong twice**: the flattened layout the
      Phase-3 wording implies is not what Phase 4 reads, and `CHAMPION.json`
      takes `matter_model` / `rl_pump_stop_time` from the *shell environment*,
      not from the eval — call the lib without `campaign.env.sh` and it
      silently records `rl_pump_stop_time=4.0` (the `:-4` default) against a
      campaign that ran `-1`. Both were hit and corrected on 2026-08-28;
      verify those two fields after any freeze.

### Phase 3 results — COMPLETE 2026-08-28 01:25:33

Launched 2026-08-27 ~09:55, finished 2026-08-28 01:25:33 — **15 h 30 m**,
200/200 evaluations over 13 generations (generation 13 stopped at 8 of 16 when
the 200-eval target was hit). Ran unattended; nothing was tuned mid-flight.

| outcome | count | share |
|---|---|---|
| scored | 181 | 90.5% |
| post-load gate rejections | 18 | 9.0% |
| solver crashes | 1 | 0.5% |

**Score climbed monotonically in 12 of 13 generations**, then flattened —
the signature of convergence rather than a truncated run:

| gen | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| best | 3949 | 3975 | 3996 | 4023 | 4019 | 4041 | 4093 | 4098 | 4126 | 4142 | 4160 | **4169** | 4168 |

Per-generation gains decayed +18 → +8.8 → 0. Generation 13 produced nothing
above generation 12, so the search had stopped finding new ground; a longer
run would not obviously have helped.

**Champion — `eval_000187`, score 4169.2** (Phase-2 champion 3945.3;
**+223.9, +5.7%**). Frozen to `runs/neuralspacetime/hq/sources/qball_traj_fgeo_max_cmaes_v2/`.

| quantity | Phase 2 champ | Phase 3 champ | change |
|---|---|---|---|
| 4D evolving shortcut `f_geo` | 15.63% | **15.82%** | +1.2% |
| matter survival | 0.495 | **0.516** | +4.2% |
| `ftl_persistence` | 0.673 | **0.840** | **+24.8%** |
| curvature activity | 0.670 | 0.687 | +2.5% |

The score gain is **not** a matter-retention artefact — the concern raised at
generation 2, when depth had dipped to 15.51% while survival rose. Over the
full run all three moved together, and the largest single gain is
`ftl_persistence`: the corridor stays open a quarter longer. Depth itself
improved only marginally (+0.19 points of f_geo), so the honest headline is
**"CMA-ES bought duration, not depth."**

Honesty rails on the champion, all verified from its own record:

- `operational_ftl_geodesic = 0.0` — frozen-snapshot credit zeroed because the
  4D evolving trace ran and is authoritative (`score.json` notes say so
  explicitly: *"frozen f_geo timeavg (6.126e-01) ignored"*). The uncorrected
  frozen number is 4x the honest one; this rail is doing real work.
- Emission sweep genuinely time-dependent: 13.83 / 14.71 / 14.75 / 15.56 /
  **15.82** / 15.07 / 0.00 % at t = 0…12. Peak at t=8; the t=12 fan returns
  zero because those rays would outlive the metric stack — anti-cheat firing
  as designed. Launches at t=0 and t=2 discarded by the emit floor.
- 3/3 rays reached, null-condition drift 5.1e-4, `h_quality_ok = true`.
- `horizon_penalty = 0`, `constraint_spike_penalty = 0`, `boundary_penalty = 0`.
- Coordinate-speed channel down-gated for dispersal (multiplier 0.52), as it
  should be — *"a channel that opens as the matter disperses is not a
  traversable warp"*.
- Solve exited converged at Ham 0.078% (headroom 1.18); post-load gate passed
  at Ham L2 0.0260.

### Caveats carried forward to Phase 5

1. **Champion post-load headroom is thin.** It passed at 0.0260 against the
   0.03 threshold — only 13% of margin. Phase 2's champion had 0.0259. Both
   sit close to the wall, so the gate is materially shaping which genomes
   survive, not merely rejecting broken ones.
2. **The 18 rejections cluster just above the threshold** (Ham L2 0.0313 to
   0.0505, median 0.0376). Same near-miss band as Phase 2. Recorded and *not*
   acted on — the threshold was not touched, and must not be loosened to
   improve the yield. See [[initial-data-noise-scales-as-inverse-dx2]].
3. **Still stationary and dispersing, not a travelling bubble.** Same physical
   character as the Phase-2 champion: a pumped, breathing, slowly dispersing
   cloud. `survival = 0.516` means about half the matter is gone by t=26, and
   the score notes still record *"geometry changes rapidly over the evolution
   window"* with co-moving stability falling back to Eulerian.
4. **Open-system accounting.** The pump runs the full window
   (`RL_PUMP_STOP_TIME=-1`), so this is not a closed GR solution; pump work is
   taxed (`pump_energy_penalty = -0.061`) but the result must never be quoted
   as a self-sustaining spacetime. Exotic matter is required
   (`exotic_penalty = -1.6`, disabled by construction in this objective).

### Throughput notes (for sizing later phases)

Measured, not estimated: **GPU duty cycle ~35%** — confirmed two independent
ways (evolution-seconds vs wall-clock, and a timestamped 15-minute
`nvidia-smi` sample: cards 0/2/3 at 42-44% mean, card 1 at 10%). Cards run at
~85% *when fed*, so the shortfall is starvation, not slow compute. The
campaign stayed **solve-bound even at `MAX_CONCURRENT_GRTRESNA=3`**: three
8-rank solves deliver one candidate every ~147 s while four GPUs can absorb
one every ~118 s (evolution median 470 s). A fourth concurrent solve would
close the gap and still use only 32 of 128 cores — **the single highest-value
change for Phase 4+**. Generations ran ~68 min steady-state.

Two operational findings worth keeping:

- **Failed solves leave large debris.** The one crash (`eval_000032`, exit
  code 2 — the solver converged to 0.41% then diverged to 5.6% at NL step 5)
  left **17 GB** of HDF5 in `grtresna/Outputs`. It was collected at the next
  generation boundary, so there is no leak, but a crash-heavy run could
  transiently need ~17 GB per failure on top of the normal footprint.
- **Retention keeps more than `keep_top_eval_dirs` suggests.** The current
  generation is always protected on top of the top-N, so the tree sawtooths
  between ~26 and ~42 dirs (24-48 GB) rather than sitting at 10. It settled at
  19 dirs / 11 GB after the final prune.

---

## Phase 4 — HQ promotion: FMAX-RM v2 (1–3 GPUs, ~1 day + analysis)

- [x] Clone the promotion campaign:
      `scripts/campaigns/promote/fgeo_max_cmaes_v1` →
      `.../fgeo_max_cmaes_v2`. In the clone's `campaign.env.sh`: point the
      source at the v2 freeze, and **delete the `GRTRESNA_RANKS=1` pin**
      (the lib default is now 8). Manifests: `grteclyn_frames: 1` on every
      cell — check it, there is no env override.
      **Done 2026-08-28.** `CAMPAIGN_NAME`, `LIVE_RUN`, `FREEZE_ROOT` and the
      `source_run` in all three manifests repointed to v2; all 9 cells across
      the three manifests already carry `grteclyn_frames: 1`; all 5 cells of
      `manifest.json` resolve under `DRY_RUN=1`.

      > **⚠ Correction to this step: do NOT delete the rank pin — set it to 8.**
      > `hq/run_batch.sh` runs under `set -euo pipefail` and expands
      > `"${GRTRESNA_RANKS}"` with no `:-` fallback (line 225/251), unlike
      > `EVOLUTION_MPI_RANKS` one line above. An unset value aborts the cell
      > with `unbound variable` on reaching the solve — `replay_eval.py`'s
      > argparse default of 8 never applies, because `run_batch.sh` always
      > passes the flag explicitly. The v2 clone therefore carries
      > `export GRTRESNA_RANKS="${GRTRESNA_RANKS:-8}"`. Latent in the shared
      > lib; left unpatched to keep the blast radius on this campaign only.
- [x] Launch the headline cell through the framework (it forwards all solve
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

- [x] Solve: `converged` door, alignment clean (same checks as Phase 1b).
- [ ] `cache_fidelity` PASS; 4D trace reports `mode=hq` on its first stdout
      line; 5/5 rays at the quoted launch.
- [x] Memory curve + transport curve extracted → matrix window decided and
      written into the manifest before Phase 5.


### Phase 4 results — COMPLETE 2026-08-29, and the champion did not survive it

Run `fmax_rm_L128_N256_t64_hq_eval000187`, one card, 22 442 s = **6.23 h**
wall, evolution exit 0 at t = 64.

**The initial data is sound.** Solve door `converged` at iteration 8,
ham 0.078 %, mom 0.085 % against a 5 % gate — 60× inside it. Nothing below
is an initial-data artefact.

**The evolution refutes the champion.**

| | Phase 3 search | Phase 4 HQ |
|---|---|---|
| score | 4169.20 | **26.53** |

A 157× drop, and the scorer's own diagnosis is specific:

- **Matter dispersed.** Confined fraction fell to **18 %** of its t=0 value,
  spatial spread ×6.16, `structural_persistence` 0.01, `density_retention`
  0.05.
- **A horizon formed and collapsed at t = 34.67 / 64.00** — survived 54.2 %
  of the run; graded horizon penalty −0.458.
- **The FTL channel was gated away.** Verbatim: *"coordinate operational FTL
  down-gated for dispersal (structural_persistence=0.01, gate_strength=1.00,
  multiplier=0.01): a channel that opens as the matter disperses is not a
  traversable warp."*
- Exotic matter still required (matter = 1.60).

This is the standing failure mode — a dissolved star makes every geometry
diagnostic look healthy. `f_geo` peaks at **0.2019 at t = 4.32** and stays
positive, and max coordinate speed reaches 1.46, *because* the matter is no
longer there to constrain them. The geometry headline and the matter state
must be read together or not at all.

**The ray trace goes blind for half the run.** 47 of 90 rows (**52 %**) are
untrusted:

| window | rays | drift | verdict |
|---|---|---|---|
| t = 0 → 26 | 5/5 | ~3e-4 | trusted |
| t = 27 → 59 | 0/5 – 3/5 | → 1.0, once 35.5 | **blind** |
| t = 60.5 → 63.4 | 5/5 | small | trusted |

The blackout begins at t ≈ 27 and the horizon appears at t = 34.67; the χ
movie shows two wells deepening to χ → 0.2 from t ≈ 32. The tracer is not
broken — it is being asked to integrate through a forming horizon. **Only
t ≤ 26 is quotable.**

**Both memory priors are refuted — do not carry them forward.**

| prior | measured here |
|---|---|
| memory ceiling at t ≈ 51 | none; peak 19.2 GB/card from a 15.4 GB floor |
| growth ~2 GB/card/unit | **0.06 GB/unit**, ~30× lower |

Plotfile retention held at exactly `CONSUMER_KEEP_LAST=3` (9.3–12 GB) for the
whole run — no disk risk at this cadence.

**Pass-gate outcome:** solve ✅. `cache_fidelity` and the `mode=hq` stdout
banner ⚠ **not found in the log** — unverified, not failed; check the emitter
before quoting either. Memory and transport curves ✅ extracted (above).

**Ruling for Phase 5:** the matrix stops being a convergence check on a
positive result — there is no positive result to converge. It becomes the
test of whether the dispersal and the t = 34.67 collapse are **numerical or
physical**. If coarser grids disperse worse, resolution is implicated; if all
four disperse alike, the champion genuinely does not hold together. The
comparison window moves from t = 32 to **t ≤ 26**, inside the trusted trace.
The cells' `stop_time = 32` is kept as-is: it covers the trusted window and
additionally brackets the blackout onset, so it also reports whether that
onset moves with resolution.

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

- [x] Fine–medium relative difference ≤ 10% on peak f_geo; full ray bundles
      at the quoted launch; grid-to-grid **spread** quoted as the error bar
      (no order fit on f_geo — measure observed order on composite
      constraint norms instead).
- [x] Compare cells at a common launch time safely inside every cell's
      window — never at each cell's own peak.
- [ ] If AMR regridding noise spoils the ladder: fall back to the
      bondi-proven unigrid methodology (max_level 0, three cell sizes).


### Phase 5 results — matrix COMPLETE 2026-08-30, dispersal is physical

Four cells, one card each, launched 01:02 and all scored by 05:48. Every
solve converged identically (ham 0.077–0.078 %, mom 0.082–0.085 %, iteration
8), so the ladder starts from matched initial data.

| cell | L | N | h | f_geo_evol | max c | retention | spread | persist | horizon |
|---|---|---|---|---|---|---|---|---|---|
| DS  |  96 | 192 | 0.500 | 0.1549 | 1.440 | 0.429 | ×3.06 | 0.026 | 0 |
| RC  | 128 | 192 | 0.667 | 0.1568 | 1.442 | 0.442 | ×3.01 | 0.024 | 0 |
| DS2 | 112 | 224 | 0.500 | 0.1559 | 1.441 | 0.429 | ×3.07 | 0.026 | 0 |
| RI  | 128 | 240 | 0.533 | 0.1565 | 1.442 | 0.431 | ×3.06 | 0.024 | 0 |
| RM  | 128 | 256 | 0.500 | 0.1565 | 1.459 | 0.178 | ×6.16 | 0.009 | −0.46 |

**Convergence: PASS.** `f_geo_evol` spans 0.1549–0.1568 — a **1.2 % spread**
against the pre-registered 10 % tolerance — across a 33 % change in grid
spacing *and* a 33 % change in box size. Max coordinate speed agrees to
0.14 %. RM, at a sixth grid and twice the duration, lands on 0.1565 as well.
Quote the grid-to-grid spread (1.2 %) as the error bar; no order fit on
f_geo, per the pre-registration.

**The decisive result is that the dispersal converges too.** Confinement
retention 0.429–0.442, spread ratio 3.01–3.07, structural persistence
0.024–0.026. Refining the grid does not slow the matter coming apart, and
neither does enlarging the box. **The dispersal is physical, not a numerical
artefact** — which is what the Phase-4 refutation needed in order to stand.

**Dispersal is a function of time, not resolution.** RM shares DS/DS2's
spacing and differs only in running to t=64: retention falls 0.43 → 0.18,
spread doubles ×3.1 → ×6.2, persistence 0.026 → 0.009, and the horizon
penalty switches on. The t=32 cells catch the process halfway; none of them
reaches the t=34.67 collapse, so all four report `horizon_penalty = 0`.

**Do not read the totals as an improvement.** DS 226.1, DS2 228.3, RC 212.6
and RI 212.4 sit far above RM's 26.5 only because they stop at t=32, before
the horizon forms and before dispersal deepens. Same configuration, shorter
window. Every cell repeats Phase 4's verdict verbatim — *a channel that opens
as the matter disperses is not a traversable warp* — with the coordinate FTL
channel down-gated by its own persistence (multiplier 0.02–0.03) and exotic
matter still required (matter = 1.60).

**Disk.** The five `small_data/metric_stack` caches cost 74 GB. The four
matrix stacks were deleted after scoring (score.json and the `.dat` outputs
survive); RM's 34 GB is retained as the only 3D record of the headline run.
Tree went 114 GB → 48 GB, also reclaiming 27.2 GB of `initial_data.gridinit`
that nothing cleans up — `artifact_cleanup.py`'s `full_non_hq` tier removes
exactly these but is never invoked; `evaluation.py` only ever asks for
`plotfiles_only`. Worth wiring up before the next campaign.

**Cost note for sizing Phase 6.** Post-processing dominates, not evolution.
Evolution took 0.9–1.5 h per cell; the geodesic scoring pass took a further
2–2.5 h (RM: 6.2 h evolution, then 5 h scoring on 90 stack files, ~3.3
min/file, single-threaded).

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
