# Status — 2026-09-28 14:25 UTC (queue updated ~11 UTC)

Current state only; the evidence and history are in [`GPU_PLAN.md`](GPU_PLAN.md)
(headings quoted in brackets), the map in [`../../MAP.md`](../../MAP.md).
**Update this page whenever a verdict or the queue changes.**

## CRITICAL: every binary simulation is corrupted by its initial data and must be rerun (the user, 2026-09-28)

Every binary run so far (the pairs at rest, the head-on, the spirals, the fly-by, the scans, the placement probes)
started from the superposition of two throats, which is not a solution of the Hamiltonian constraint
["2026-09-27 (12:15 UTC) — parameter matching and the energy check"]:
- each mouth comes out 9–15 % larger in every length than the isolated throat it is named for (one-body mass 1.149 at
  d = 8, 1.094 at d = 12), so every p is in the wrong unit (p = 0.12 / 0.45 are 0.110 / 0.411 per one-body mass);
- the pair's mass leaves out the interaction energy: M_ADM is 2.00 in the superposition, 2.36 (flipped) and 1.38
  (like) at d = 8 for the same two isolated throats constraint-solved (mode 3).

No binary number is final until it is remeasured on mode-3 data (`constraint_solve = 1`,
`constraint_solve_puncture_mode = 3`, name token `csm`).

**RULE for every rerun (the user, 2026-09-28): the new run's properties must match the corrupted run it replaces,**
so the two differ in the initial data alone and the old result can be tested. Same L, N, max_level, tagging_L,
sponge, separation, gauge, dt_multiplier, stop_time and plot cadence as the old run's `evolution_params.txt`
(`results/merger/campaign/...`); the only changes allowed are the constraint-solve block (mode 3), checkpoints only if the user
says so, and the plot variables the full frame set needs (output only). Diff the new template against the old params before
launching. E.g. the rest pairs are L = 64, N = 128, max_level 3, tagging_L 64, sponge 24/32, t = 15, plots every 0.5. CS-1 (mode 0: the superposition's mouths, solved) is the
old-versus-clean comparison, not a rerun. The binary verdicts below stand only as results on superposed data.

## The plan, in order (the user's, 2026-09-28)

1. **Energy check** (CPU only, about a day). The pair's total mass in mode 3 at d = 8, 12, 16, 24 and 48, attracting
   and repelling: what "M" means in the paper, and whether the extra interaction energy agrees with the attraction or
   is a bug. **Done** 2026-09-27 12:15 UTC (`results/merger/t0_matching/energy_scan.tsv`): not a bug, it agrees only
   if the throats act at fixed scalar potential. The GPU build reproduces it (2026-09-28, below).
2. **First two runs** (about 18 GPU-hours, side by side).
   - Pairs released from rest (~6 h): remeasure the attraction/repulsion ratio (1.518) and the force law for the true
     wormholes. **Done 2026-09-28 09:11 UTC**: the five old rest pairs rerun in mode 3, all clean to t = 15. Pull/push
     1.463 ± 0.023 (superposed 1.518; fixed potential 1.500, fixed charge −0.667 excluded); force-law offset δ = 2.65
     (superposed 3.56). Closed out, below.
   - Head-on to t = 100: does "the horizon shrinks by a quarter" survive, or was it a symptom of the missing
     energy? Moved to the L = 128 production box with the spiral and the fly-by (the user, 08:20 UTC; queued below);
     the L = 64 rerun was stopped at t = 0.6.
   - Decision point: these two show how much of the abstract changes.
3. **The orbits** (about 3 days of GPU).
   - Spiral p = 0.12 (~22 h), plus a finer-grid twin for convergence (~8–10 h).
   - Fly-by p = 0.45 at two resolutions (30–67 h).
   - p = 0.25 and 0.35 (~12 h) to relocate the merger/fly-by boundary.
   - Decision point: if any outcome flips (merger ↔ fly-by), map the boundary more finely.
4. **Single wormhole on clean data** (12–25 h, any time in parallel). The kicked single throats with properly solved
   starting data. This settles the "regrowth" question.
5. **Rewrite.**
   - Every binary number comes from mode-3 runs.
   - The old campaign becomes the systematics study (gauge, grid, freeze tests), with CS-1 as the table showing old
     versus clean starting data.
   - Add the new definitions: each wormhole's mass, the pair's total mass, and p in true units.
   - Update the abstract once step 2's answers are in.
   - Constraint norms are not a paper problem (checked 2026-09-28 06:55 UTC, the rest-pair reruns to t ≈ 5 against
     their old runs). The logged 𝓗 norm reads 9–13 % higher for the like pairs and 21 % for the flipped one, a flat
     offset from t = 0 that does not grow; 𝓜 is 27–59 % lower. That 𝓗 is the base grid's box average (Δx = 0.5),
     which does not resolve the throat cores (3.35e-3 in all four like pairs whatever d): the discretisation floor,
     not the superposition error. Every constraint claim in the paper is relative (growth, onsets, level agreement,
     "below its value at formation"), and the `fig:constraints` caption already says the norms compare only within
     one box. The binary norm values the text quotes (the Helfer fly-by's 3.2e-3 → 1.6e-2, the spiral's 3.5 % level
     agreement) are re-read from their reruns.
   - Re-measure Sec. II D's solve paragraph on mode-3 data. Its numbers are the mode-0 solve's, which keeps the
     superposed mouths: throat-shell 𝓗 9.7e-3 → 5.1e-6, M_far moving 0.1 %, R_min 1.3 % (`clmSolveShellHamSup`,
     `clmSolveShellHamSolved`, `clmSolveKeepsMfar`, `clmSolveKeepsRmin`). M_ADM = 2.738 (`clmSolvedHeadonMadm`) is
     CS-1's, the mode-0 pair's; the mode-3 pair at d = 8 has 2.360.
   - The scalar energies the paper quotes are partly near-field and change: `clmGwScalarEnergyFlyby`, the
     `clmGwScalarRatio*` rows, the head-on E_φ (step 6).
6. **Longer GW runs, with the sponge and the extraction spheres farther out** (the user, 2026-09-28; proposed, not
   queued).
   - Why ["Open, the user's call: the scalar energies the paper quotes are partly near-field"]: the scalar spheres sit
     at ωR ≈ 1–3. Fitting the exact outgoing ℓ = 1 solution on each sphere, only ~35 % of the fly-by's |E_φ| = 0.087
     (R = 30, t = 60) is radiated, so |E_φ|/E_GW ≈ 0.8–0.95, not 2.3. The head-on's E_φ becomes the same on every
     sphere, ≈ −0.044, not −0.056 to −0.075. "Comparable and negative" survives. Not yet checked: the fit is
     flat-space, without the O(M/R) terms. No text changed.
   - Now: the fly-by and the spiral run in L = 128 (sponge from r = 48; Ψ4 spheres 20–44, the scalar only at 14 and 30,
     the consumer's default radii) to t = 100 / 150; the head-on in L = 64 (sponge from 24, spheres 10/14/18) to t = 100.
   - Check (2026-09-28 07:29 UTC): ωR ≈ 1–3 at R = 14–30 means ω ≈ 0.07–0.1, so the wave zone (ωR ≳ 10) starts at
     R ≈ 100–150. Spheres there need the box edge near r = 200 (L = 512: a coarser base and two more levels keep the
     interior's grid) and runs longer by R: the fly-by to t ≈ 220 (it is trusted to t = 70), the head-on to t ≈ 200.
     Roughly 2–3× each old run's GPU time; the memory must be measured first (the old level-5 fly-by peaks at 59 GB of
     80).
   - Farther spheres alone do not clean the raw number: between R = 14 and 30 the stored part falls only about as 1/R
     (the pair is still moving when the window closes), so at R = 150 it would still be ~15–40 % of it (65 % at
     R = 30). They validate the fit and cut the O(M/R) terms from ~7 % to ~1.5 %; the fit stays the estimator.
   - Free, inside the old boxes (output only, so the reruns stay exact): scalar spheres at 14/20/30/44 on the fly-by and
     the spiral, 10/14/18/22 on the head-on (the consumer's `--radii`), for the fit and a 1/R extrapolation over four
     spheres.
   - Decided (the user, 08:20 UTC): the head-on, the spiral and the fly-by all run in the L = 128 box with Ψ4 at
     20/28/36/44 and the scalar at 14/20/30/44 (queued below). Wave-zone twins: not decided.

Along the way:
- Cancel the planned convergence runs on the old data; the finer-grid twins in step 3 replace them (the convergence queue
  below is cancelled).
- For every run: ask the user directly whether it needs checkpoints (the user, 2026-09-28: never on by default;
  the rest-pair reruns keep the last 3), check the starting mass and throat size before walking away, and put "mode 3"
  in the run's name (`csm`) and registry entry.

Total: about 100–170 GPU-hours, roughly 4–5 days on the three free cards.

## Live — first node (two H100s): the fly-by and the spiral (the user's go, 09:48 UTC)

| card | run | p | t now (14:23) | t end | speed | ETA |
|---|---|---|---|---|---|---|
| 0 | `merge_orbit_flip_d12_p045_L128_lvl5_t100_csm` (the fly-by) | 0.45 | 9.75 | 100 | 2.2 u/h | ~41 h, ~07:30 UTC 09-30 |
| 1 | `v2_spiral_d12_p012_L128_lvl5from0_t100_csm` (the merger) | 0.12 | 9.74 | its NaN, ~60 | 2.2 u/h (old run 2.81 average) | ~18–22 h, ~08:30–12:30 UTC 09-29 |

- Launched 09:49 UTC, both exact reruns of their old runs (only the solve block and checkpoints every 5 units, newest
  3), binary `main3d_csmatch_5f988dbc_2026-09-28.ex`, profiles `orbit-modes-scan-prod` / `orbit-modes-prod` (the
  scalar at 14/20/30/44), zoom 64. The fly-by's name keeps its old run's `merge_orbit_` prefix: it is the p = 0.45
  fly-by; the merger is the p = 0.12 spiral.
- t = 0 checked: preflight pass; each mouth's far-side mass −4.81048 and charge 3.03437, one-body mass 1.0000 (match
  8e-10 fly-by, 4e-10 spiral; mode 3 at p = 0.45 converged in 2 matching passes). M_ADM 2.34448 (fly-by), 2.27476
  (spiral; the CPU mode-3 check at p = 0.12 gives 2.27920 on L = 64). Frame 0 (χ) matches the old runs' (pits at ±6).
  Cards at 60 GB of 80 each.
- Checkpoints confirmed: `Chk00500` (t = 5) written 12:12 / 12:14 UTC, Header complete, 36–37 GB each; with the t = 0
  one on scratch, rolling to the newest 3. Plotfiles keep the last 3 (00700–00900 at 14:23). Each run holds 80 GB of
  scratch now, ~135 GB at most; 1.0 TB free. No NaN; consumer errors 0; 10 frames each (t = 0–9).
- **All three production runs verified at 10:15 UTC** (fly-by, spiral, and the second node's head-on):
  - each run's `params.txt` differs from its old run only in the named changes;
  - mode 3 in every `constraint_solve.dat`, converged: every MLMG solve ≤ 4e-9, each mouth's far side matched to
    8e-10 / 4e-10 / 4e-8, one-body mass 1.000000;
  - in-code Ψ4 written every step at 20/28/36/44 (head-on 10/14/18/20/28/36/44);
  - the consumer's scalar and Ψ4 at 14/20/30/44 (head-on 10/14/18/20/30/44), the same small-data files as the old
    runs, horizon scans (fly-by, head-on) with R_min 3.8763 / 3.8786 at t = 0, 15 frame fields, no consumer errors;
  - no NaN.

**The four mode-3 rest-pair reruns are closed out** (09:11–09:30 UTC): `ctrl_rest_d12_csm`, `ctrl_flip_d12_csm`,
`ctrl_rest_d14_csm`, `ctrl_rest_d16_csm`, each its old run's packed params with only the data changed (L = 64, N = 128,
level 3, t = 15), clean to t = 15, no NaN. Filed under `03_two_throats/csm/` with d = 18, packed without movies (frames
kept), scratch pruned (237 GB; MANIFEST_CLEANUP_2026-09-28) ["2026-09-28 (09:30 UTC)"].
- Pull/push at d = 12 over t = 3.5–10.5: 1.463 ± 0.023 (superposed 1.518 ± 0.021; fixed potential 1.500; fixed charge
  −0.667, excluded).
- Like-pair ladder at t = 11.5: +0.4791 / +0.3716 / +0.2963 / +0.2406 at d = 12 / 14 / 16 / 18 (×1.020 / 1.004 / 0.994 /
  0.987 the superposed runs'); A/(d + δ)² gives δ = 2.65 (superposed 3.56). Table:
  `results/merger/campaign/03_two_throats/matched_rest_displacement.dat`.
- t = 0 read at launch: every mouth's far-side mass and charge are the isolated throat's (one-body mass 1.0000); M_ADM
  2.27376 (flipped d = 12), 1.56579 / 1.62149 / 1.66449 / 1.69871 (d = 12 / 14 / 16 / 18).
- The GPU build reproduces the CPU energy scan at d = 8 (preflight-only on the scan's grid): M_ADM 2.3604109 (CPU
  2.36041), λ 0.856614, c 2.029956.
- The L = 128 pair launched first (05:12, `ctrl_{flip,rest}_d16_csm_L128_ml4_t015`) broke the rerun rule; stopped at
  t = 3 and wiped on the user's word, frames included (MANIFEST_CLEANUP_2026-09-28).

## Live — second node (one H100): the production head-on (the user's go, 09:57 UTC)

| card | run | t now (14:23) | t end | speed | ETA |
|---|---|---|---|---|---|
| 0 | `merge_headon_flip_d8_v1_L128_lvl5from0_scalar_t100_csm` | 8.83 | 100 | 2.1 u/h | ~44 h, ~10:00 UTC 09-30 |

- Launched 10:02 UTC (template `params_merge_headon_flip_d8_v1_L128_lvl5from0_scalar_t100_csm.txt`, profile
  `headon-modes-prod`, zoom 40, coord 64, binary `main3d_csmatch_5f988dbc_2026-09-28.ex`). The blessed exception to the
  rerun rule: the old L = 64 physics in the shared L = 128 box (details in the production set below).
- The 09:58 attempt was refused by the preflight: the template still carried the old run's `checkpoint_interval = 100`
  and `checkpoint_keep = 1` with checkpoint output off. Now `checkpoint_interval = -1`: **no checkpoints** (the user's
  word); if it dies it cannot be restarted.
- t = 0 checked: preflight pass; M_ADM 2.35731 (CPU scan 2.3604 on L = 128 level 4; the L = 64 attempt 2.35892),
  m1_A = m1_B = 1.0000000; frame 0 (χ) two pits at ±4; 59 GB on the card, stepping (t = 0.06 at 10:05).
- The L = 64 head-on rerun before it (08:07–08:26 UTC, stopped at t = 0.60) was wiped on the user's word, frames
  included (MANIFEST_CLEANUP_2026-09-28).

## The production set: head-on, spiral, fly-by in one box (the user's final proposal, 2026-09-28 09:00 UTC) — all three live

Shared by all three (the user): L = 128, N = 256 (Δx = 0.5, finest 1/64), max_level 5 from t = 0, tagging_L 64 (the same
refined grids), sponge 48/64, Ψ4 at 20/28/36/44, the scalar at 14/20/30/44 (consumer profiles `*-prod`, output only),
plots every 1.0, mode-3 data, binary `main3d_csmatch_5f988dbc_2026-09-28.ex`. Launched on the user's go.
Order: fly-by → spiral → head-on. **The fly-by and the spiral are live on the first node (09:49 UTC), the head-on on the
second node (10:02 UTC); see Live, above.** Templates in `runs/wormhole_merger/templates_scan/params_<run>.txt`, each
diffed against its old run's packed params (only the named changes):
- **`merge_orbit_flip_d12_p045_L128_lvl5_t100_csm`** (first node, card 0, first): the exact rerun, plus checkpoints
  every 5 units (500 steps), the newest 3 (the old kept 8 at every 1.0). t = 100 (never NaN'd; trusted to t = 70).
  Profile `orbit-modes-scan-prod`, zoom 64, coord 64. 2.17 u/h (old) → ~46 h; 58.8 GB (old). Mode 3 at p = 0.45 is
  new (tested at 0.12): read the Newton passes and each mouth's far side at start-up.
- **`v2_spiral_d12_p012_L128_lvl5from0_t100_csm`** (first node, card 1): the exact rerun, plus checkpoints every 5
  units, the newest 3 (19–26 GB each). To its NaN (old wall t = 59.94; stop_time 100). Profile `orbit-modes-prod`,
  zoom 64, coord 64. 2.81 u/h (old) → ~21 h; ~59 GB. Then the freeze continuation (plan now, launch later): relaunch
  from the last checkpoint ≥ ~55 with the interior fill, armed from THIS run's core profile (the spike time moves with
  the smaller mode-3 throats), not the old t = 57; the validated ratios r_full/r_start = 1.40/1.90.
- **`merge_headon_flip_d8_v1_L128_lvl5from0_scalar_t100_csm`** (second node): **a blessed exception to the rerun rule**
  (the user's word): the old L = 64 physics in the shared geometry, for one geometry and a reflection-free window to
  t ≈ 84 at R = 44 in the shared energy table. Changed: the box keys (identical to the fly-by's), plots every 1.0
  (was 0.5), the solve block, and the old spheres kept (output only): Ψ4 at 10/14/18 + 20/28/36/44, the scalar at
  10/14/18/20/30/44 (profile `headon-modes-prod`). Δx and the finest level are the old run's, so at 10/14/18, before
  any reflection, old vs new is one knob (the data); the box enters only through reflections, which it delays. The
  paper's head-on chain: superposed scout → CS-1 (same grid, one knob) → mode-3 big box (data + box, compared at common
  spheres). **No checkpoints** (the user, 09:00: "it will run smooth"). t = 100, zoom 40, coord 64. Est. 2–2.8 u/h,
  ~36–50 h; ~59 GB (the preflight measures it).
- **Skipped on the user's word (09:20 UTC): per-level + core-excised 𝓗/𝓜 diagnostics.** No claim needs them (every
  constraint statement is relative, the figure calls the norms base-grid box averages); Sec. II D's t = 0 throat-shell
  number is redone on CPU with `constraint_solve_t0_check.py` ["2026-09-28 (09:30 UTC)"].
- Launch checklist: t = 0 far-side mass and charge at the isolated values (~2e-7), R_min ≈ 3.889; each run's M_ADM
  into the registry (head-on 2.360; spiral and fly-by above 2.274 by their kinetic term); frame 0 against an old
  reference; the first checkpoint on scratch (spiral, fly-by). The registry marks the head-on as the blessed exception,
  the spiral and fly-by as exact reruns. No test launches.

From the repo root, `nvidia-smi` first, each redirected (`< /dev/null > <log> 2>&1`):
```
L=grteclyn-wrapper/scripts/campaigns/wormhole_merger/launch.sh; B=runs/wormhole_merger/bin/main3d_csmatch_5f988dbc_2026-09-28.ex
bash $L --gpu 0 --template params_merge_orbit_flip_d12_p045_L128_lvl5_t100_csm.txt --name merge_orbit_flip_d12_p045_L128_lvl5_t100_csm --profile orbit-modes-scan-prod --zoom 64 --coord 64 --binary $B
bash $L --gpu 1 --template params_v2_spiral_d12_p012_L128_lvl5from0_t100_csm.txt --name v2_spiral_d12_p012_L128_lvl5from0_t100_csm --profile orbit-modes-prod --zoom 64 --coord 64 --binary $B
bash $L --gpu G --template params_merge_headon_flip_d8_v1_L128_lvl5from0_scalar_t100_csm.txt --name merge_headon_flip_d8_v1_L128_lvl5from0_scalar_t100_csm --profile headon-modes-prod --zoom 40 --coord 64 --binary $B
```
Then the plan's step 4 (single throats on clean data), each a rerun of its old run by the rule.

## Queued — mode-3 follow-ups: the ladder (Fig. 12a) and a convergence twin (the user, 2026-09-28 ~11 UTC; nothing launches without the go)

Fig. 12 is `fig:spiral_ladder`. Panel (b), the slicing/gauge study, **is done** (the gauge arms on superposed
data); it is a systematics statement and is not rerun. Panel (a), the refinement ladder to the wall, is rerun on
mode-3 data; the paper's framing (the user): the old constraint state is barely mentioned — the headline is that
mode 3 improves the constraints, and the old campaign is the systematics study.

| id | run | what | how | GPU-h |
|---|---|---|---|---|
| LAD-csm | ladder arms `ladder_csm_L{4,6,7}_r0XXXX` | the wall under refinement on mode-3 data (Fig. 12a) | restart from the production spiral's own checkpoint at t ≈ 50 (its every-5 checkpoints exist for this), max_level 4 / 6 / 7; the production run itself is the level-5 rung; ~10–15 units per arm | ~15–25 total |
| CONV-csm | `v2_spiral_d12_p012_L128_lvl4from0_t100_csm` | spiral burst and energy, level 4 vs 5 on mode-3 data (replaces CONV-3's role) | the production spiral's template, max_level 4, from t = 0 | ~8–10 |

- LAD-csm launches only after the spiral passes t ≈ 55 and a checkpoint ≥ 50 is on scratch; convergence-study rules
  apply (no frames: `--frames-fields none` + `WHM_FRAMES_SUBSET`, `WHM_MOVIES=0`, group `08_convergence`).
- max_level alone still leaves the wave zone on the base grid; a wave-zone twin (CONV-3w's role) is contingent on
  the mode-3 waveforms shifting beyond a few % and is not queued.
- Checkpoints: to be asked per run at launch (the standing rule); the ladder arms need none.

## Earlier (2026-09-27)

CONV-1, CONV-2 and CONV-3w were stopped at 08:33 UTC on
2026-09-27 and removed at 08:40 UTC ["2026-09-27 (08:33 UTC)"]. They had reached t = 30.25 / 60, 57.88 / 60 and 58.18 / 100.
Their scratch (38 GB of plotfiles, no checkpoints), run dirs, launcher logs, registry rows and untracked partial packs
are gone. Only their rendered frames are kept, in `runs/wormhole_merger/00_archive/stopped_2026-09-27/`, because frames
are never deleted without the user's explicit word. All three were queued again, and the plan (2026-09-28) cancels them.
- **CONV-3 is closed out** (finished t = 100 at 02:12 UTC; filed under `08_convergence/`, packed, scratch pruned).
  - Its (2,2) burst matches the level-5 chain on every sphere: peak ratio 1.000, waveform within 0.1 % of peak.
  - Both runs extract on the base grid, so this tests the core's resolution, not the wave zone's. CONV-3w tests the
    wave zone ["2026-09-27 (05:00–05:45 UTC)"].
- **Kept on the user's word (2026-09-27, "skip"):** CONV-3's frames (in its run dir) and Chk05700. Chk03600 stays too:
  the queued CONV-3w restarts from it.

- **Second node: free. CS-1 `merge_headon_flip_d8_cs_lvl3_t030` is closed out** (the head-on scout on
  constraint-solved data; finished t = 30 at 08:14 UTC, no NaN; filed under `04_binary_headon/`, packed)
  ["2026-09-27 (08:30 UTC)"].
  - The same merger as the scout, about 2 units later, with a horizon 4–5 % larger: common MOTS born at t = 23
    (scout: present at t = 22), R = 5.84 at birth and 5.94 at its peak (scout 5.56 and 5.71).
  - The pair's M_ADM is 2.74 (corrected 12:15 UTC; the 2.63 read the Robin face's offset of w as mass), not 2.00,
    so R/2 is 7–8 % above it (the paper's 39 % used 2.00). Its mouths are the scout's, to 0.1 % in far-side mass.
  - Trust window t ≤ 29.7: the core's K runaway starts at t = 29.8.
  - One resolution (level 3), one separation. The level-5 head-on, the spiral and the fly-by have no solved twin;
    CS-2 (the p = 0.12 spiral on solved data) was not run (the user: "do not run it").
  - **Scratch pruned at 08:36 UTC on the user's word** (115 GB: its checkpoints, its plotfiles and
    `_keep_cs1_formation/`; MANIFEST_CLEANUP_2026-09-27). CS-1 has no restart state left; its frames and movies
    are in the run tree.
  - The three partial pack copies of the first node's live runs, made by this close-out, were removed at 08:38 UTC
    on the user's word. The pack now skips a run that is live on the other node, the summaries carry no live
    rows, and `claims.py check` passes (833 recomputed, 0 problems).

**Done 2026-09-27 (12:35 UTC, paper session): the paper's rewrite for the matched placement has started** ["2026-09-27 (12:35 UTC, paper session)"]: new Sec. II D (constraint-solved data, far-side identity, matched placement, Eq. (ebind) E_b = −λ²(m²/d)(1 + σQ)), Tables placement and energy, Table I counts CS-1, head-on Penrose and area statements qualified. Ledger 1070 rows, 0 problems. Not built (no LaTeX here). The evolution sections still quote the superposed runs, in the units II D states.

**Done 2026-09-27 (12:15 UTC, CPU only): parameter matching and the energy check** ["2026-09-27 (12:15 UTC) — parameter matching and the energy check"]. Each mouth's far side (ADM mass 2cd and scalar charge at its own compactified infinity) is now measured after every solve. Verdicts:
- The solve did **not** change the throats: CS-1's mouths have the scout's far-side mass to 0.1 % (R_min +1.3 %). CS-1 turned one knob, the data.
- The **superposition** did: every superposed pair's mouths are ~13 % larger in every length than the isolated throat (one-body mass 1.149 at d = 8, 1.094 at d = 12, same for solved mode-0 twins). So p = 0.12 / 0.45 at d = 12 are 0.110 / 0.411 per one-body mass in every run; no rerun is needed for this, only the paper's normalisation.
- CS-1's M_ADM is **2.74**, not 2.63 (the Robin face leaves w a constant −1e-3; the volume identity, 1.0014 on the exact throat, does not see it).
- **Mode 3** (`constraint_solve_puncture_mode = 3`) builds the pair from two isolated throats: c and each throat's coordinate size iterated until its far-side mass and charge are the isolated ones; R_min lands 0.06 % from R⋆. Also with momentum (d = 12, p = 0.12).
- **Energy check** (mode 3, d = 8–48, both signs): M_ADM − 2m = σ²[±(a² + m²) − m²]/d to 3 % (d = 8) and 0.3 % (d = 48): gravity's −m²/d plus the ghost scalar's cross energy, **positive for the attracting pair**. Not a bug. It matches the measured attraction (and its ratio 5 to gravity) only if the throats behave as conductors at fixed scalar potential; at fixed charge it would be repulsion. Open: a dynamical test (initial acceleration in mode-3 data, both signs, GPU minutes). Nothing launched; the code is not yet compiled for CUDA.

**Done 2026-09-27 (05:45–06:00 UTC): constraint-solved initial data** ["2026-09-27 (05:45 UTC) — constraint-solved initial data"]. `constraint_solve = 1` in the merger example solves the Hamiltonian constraint on the initial hierarchy with AMReX MLMG (φ, Â, Π, lapse fixed; momentum constraint stays exact; Newton for p ≠ 0). Validated on CPU at t = 0: rebuilds the exact drainhole from bare punctures (R_min to 5e-4); the d = 8 head-on's finest-level Hamiltonian drops 9.7e-3 → 5.1e-6 (×1900, the exact throat's floor); orbital p = 0.12/0.45 converge in 3 Newton passes. The solve adds the scalar interaction energy: M_ADM 2.00 → 2.63 at d = 8, throats +1.3 %. Base-grid L2_Ham cannot see it (unresolved throat). The test binary is a `-dirty` build; a clean pin from the commit is still to be built. Grader: `scripts/validation/constraint_solve_t0_check.py`. **On the GPU (second node, 06:00 UTC):** the dirty build reproduces the CPU solve digit for digit (max |w|, L2_Ham, the Newton sequence), 3–4 s per start-up; level 5 solves in +2.5 s, 24.6 GB at start-up.

**Done 2026-09-26 (afternoon, not committed): the referee's fixes** ["2026-09-26 (afternoon, paper session)"]. Retitled "The Four Fates of Ghost-Supported Wormholes: Collapse, Inflation, Merger and Scattering in Numerical Relativity"; the abstract is the user's own text (16:00 UTC). Cosmology conditional on z_e; no "baby universe", no percolation bound; "wall" → "interior failure"; no vacuum ISCO (the pull's period P = 75–100; ε = 1e-15 buys 1.8–2.7 periods); η = 4 horizons in §VII C; fly-by trust window t = 70 (new Fig. 10(g); Figs. 14/15/17/18 cut). Re-read on CPU: throat energy 2.6e-5 (to t = 58), 44× the matched control; Kerr rise 1.34; orbit fractions 0.27–0.30; **the mouths' τ with the companion's field removed: the merging arm has no growth of its own, the fly-by τ = 3.9** (the referee's "lower bound" had the wrong sign); the mouth fit had dropped its end rows (τ 3.64/4.33 now). 17 references. Ledger: 1000 rows, 0 problems. Caveats the referee asked for are in the text (Δt, ADM balance, curvature at the failure): G17/G18 queued. The head-on t ≤ 70 sentence was narrowed on the user's word (16:10 UTC): its numbers past t = 70 carry the late spread; no re-gate. No DOI yet (the user will add it).

**F4 `single_eps_m1e2_L512_ml5_oct_t400` is closed out** ["2026-09-26 (05:00 UTC)"]: it died at t = 392.36 (04:22 UTC, NaN in
h11 on level 2, blowing up on the neck sphere r ≈ 60–65). It was closed out with movies (chi K lapse phi Pi), filed under
`01_single_throat/seed/` and packed. **Quotable to t = 218 only**: the 1+log collapse front reaches the outer face at
t = 218, and its reflection runs back in, reaching the neck as the run dies. The far θ_k horizon is lost at t = 212, and L2 𝓗
passes 0.1 at t = 220. Result: R 3.813 → 14.48 (×3.80) by t = 218 with no trapped surface. The onset is exponential,
T = 5.69 over t = 16–28. In proper time it grows at the Shinkai–Hayward rate over t = 16–40: H R0 = 1.22 (their 1.1). The θ_k = 0 horizon
grows to R = 73.4 by t = 212. The launch passed a trimmed frame list, so it has **no Weyl4 or shift frames** (lost). Its
scratch (24 GB) was pruned at 05:53 on the user's word. Figures: the paper's `fig:single_inflation` (the `single_throat_inflation_L512` campaign page was retired from `figures/` on 2026-09-26). The paper's Fig. single_inflation and §IV.D are rebuilt on F4 alone; Table I counts it (145 runs, 663 GPU-hours).

**Wiped on the user's word** (2026-09-26 04:16–04:18, frames included, `manifests/MANIFEST_CLEANUP_2026-09-26.md`): the failed
harmonic retries F5 `…harm_oct_t400_sg03` / `_sg10` (NaN at t = 46.71 / 47.01 on F3's wall) and F6 `…harm_oct_zs_t400`
(zero shift, runaway from t ≈ 29). Earlier: F3 and F2 (16:33), F1b (14:15). No NaN-free re-run (3D harmonic with
solution-following refinement, or a 1D spherical code): the user's no-go, 2026-09-26. The question is only whether the
throat keeps growing, and F4 answers it.

Done 2026-09-26 (not committed): the paper renamed ("… BLACK-HOLE SEEDS AND BABY UNIVERSES: MERGER, SCATTERING, AND
INFLATION …") and the inflating branch made a result instead of a loose end, on the user's direction. New §X
"The inflating half of the population": sign-symmetric seeds send about half of a foam population inflating (large seeds
skew toward collapse); an inflating throat is a Farhi–Guth baby universe — anti-trapped interior, exterior at fixed ADM
mass — with 1.3 (neck) / 3.0 (θ_k boundary) areal e-folds in F4's record against inflation's ~60; the boundary advances
at a steady 0.33c (no slowing over the last 50 units), so non-overlap of mouths today caps the mean comoving speed at
(2.6×10⁻⁴–1.2×10⁻³)c for n = 10⁻⁴–10⁻² Mpc⁻³ — the seed channel is consistent only if the boundary stalls (recorded
speed is 270× the loosest bound) or the inflating half is rare. §IV.D now quantifies the turnover premise: store
R⋆/2 − m = 0.94; shed 0.03 over the quiet window; F4's own spheres only bracket it, 4.1 kinematic vs 0.04 geometric
(the 1+log front collapses the lapse at the spheres first) — ending stays open. Backing: `results/merger/analysis/
inflating_population.py`, extractors `single_f4_pop` / `detector_stall`, 12 ledger rows, three new references
(Farhi–Guth 1987; Blau–Guendelman–Guth 1987; Liddle–Leach 2003). Same session, referee-critique edits: abstract
trimmed 457 → 368 words (incl. one new baby-universe sentence), near-zone extraction now stated in the intro,
a junk-radiation paragraph in §VIII (t=0 defect crosses spheres by t≈R, bursts arrive with their triggers), duplication
trims across §§I–X; 29 rows re-anchored after the trims. Ledger: 963 rows, 802 recomputed, 0 problems, stamped.
The wrapper venv was re-synced (pycbc/astropy had gone missing; full `claims.py check` needs them).

Done 2026-09-26 (not committed): the paper's layout, on a referee-style read. The constraint panels of Figs. 1/2/3/5/7
(old numbers 1/2/4/6/9) became one appendix figure, `fig:constraints` (App. A, "Code Health and Constraint Evolution",
each run at its highest level); regrowth, refinement ladder and fill insensitivity moved to App. A, mouth growth, seed
linearity and scalar censorship to App. B. `results/merger/figures/` now holds the paper's 18 figures only (17 others
deleted, `p012_paper/` flattened) and `pack_results.sh` draws none. Ledger: 951 rows, 0 problems.

Done 2026-09-26 (pushed): the full default frame set (`frames_default.txt`), with a preflight that renders every field
at t = 0 and refuses a subset without `WHM_FRAMES_SUBSET`; movies cut at each run's trust window
(`results/merger/trust_windows.tsv`); the cleanup manifests moved to `runs/wormhole_merger/manifests/`.

First node: the long
single-throat arms closed out under `01_single_throat/seed/` ["2026-09-24 (16:15)"]; its
scratch holds only the live runs. The paper session's `plt_take2/` plotfile copies (77 GB, G16's input) were deleted
on the user's word on 2026-09-27, because G16 was dropped.

Second node (one H100): free since 08:14 UTC on 2026-09-27; CS-1 and the η = 4 level-5 probes are closed out and
filed ["2026-09-27 (08:30 UTC)", "2026-09-25 (morning)"]. Its scratch is empty (115 GB pruned at 08:36 UTC,
MANIFEST_CLEANUP_2026-09-27).

Run tree: every plotfile deleted on the user's word; 192 → 52 GB. Two checkpoints remain: Chk03600 (20 GB, the t = 36 seed of CONV-3) and Chk05700 (26 GB, no queued
use since G4 was dropped; kept on the user's word, 2026-09-27).

## Cancelled — the convergence runs on the old data (the plan, the user's word 2026-09-28)

**Cancelled by the plan above:** they converge superposed-data runs; the finer-grid twins of step 3 replace them.
Kept below as the record of their templates (queued on the user's word, 2026-09-26 17:30 UTC).

Nothing launches without the user's word. Every other option (G1–G18, A1–A4, B/C, the inflation campaign) was dropped
from the queue on the user's word ["2026-09-26 (evening) — the convergence queue"]. Each template is its partner's params
with only the named keys changed, and all nine PASS the full preflight (2026-09-26 16:50 UTC; nothing launched).

| id | run (template in `templates_scan/params_*`) | converges | partner | GPU-h | peak GB |
|---|---|---|---|---|---|
| CONV-1 | `single_eps_m1e2_ml5_t060` (`single_eps_m1e2_ml5_t060`) | τ: third level, a convergence order (abstract) | `single_eps_m1e2_t100` / `_ml4_t100` | 14 | 27 |
| CONV-2 | `single_eps_m1e2_halfstep_t060` (`single_eps_m1e2_halfstep_t060`) | Δt: dt_multiplier 0.01, intervals doubled (§III) | `single_eps_m1e2_t100` | 7 | 20 |
| CONV-3 = G9 **DONE, closed out** | `v2_spiral_d12_p012_L128_lvl4_t100_freeze_r03600` (`prod_L128_p012_lvl4_t100_freeze`) | spiral burst and energy, level 4 vs 5; fill at t = 57 in the same leg | the production chain | 9 | 56 |
| CONV-3w | `v2_spiral_d12_p012_L128_lvl4_wz1_t100_freeze_r03600` (`prod_L128_p012_lvl4_wz1_t100_freeze`) | the WAVE ZONE: R = 20 and its path (r < 24) on level 1, vs CONV-3 on level 0 | CONV-3 | 10 | 62 |
| CONV-4 | `merge_orbit_flip_d12_p045_L128_lvl4_t095` (`flyby_p045_L128_lvl4_t095`) | fly-by energy, scalar, mouths; t = 95 reaches the R = 44 gate | `…p045_L128_lvl5_t100` | 21 | 56 (+1–5 at the pass) |
| CONV-5 | `merge_orbit_flip_d12_p045_L128_lvl3_t095` (`flyby_p045_L128_lvl3_t095`) | the fly-by's third level (order) | same | 11 | 52 (+1–5) |
| CONV-6 = G12 | `merge_headon_flip_d8_lvl5from0_ball4_t100` (`headon_d8_lvl5from0_ball4_t100`) | remnant horizon on level 4, not 3 ("loses a quarter", abstract); since 2026-09-27 also the head-on's wave zone: R = 10 and its path (r < 12) on level 2 | `…v1_lvl5from0_scalar_t100`, `…v1_lvl3down_t100_r03500` | 34 | 60 |
| CONV-7 | `merge_orbit_flip_d12_p035_lvl5_t080` (`scan_p035_lvl5_t080`) | p = 0.35 passes at level 5 (the abstract's 50–70 %) | `…p035_t200` (closest 2.75 at t = 42) | 35 | 47 |
| CONV-8a/b | `ctrl_rest_d12_ml4_t015`, `ctrl_flip_d12_ml4_t015` | the sign ratio 1.52 at level 4 (abstract) | `ctrl_rest_d12`, `ctrl_flip_d12` | 3 + 3 | 41 each |

~140 GPU-h in all. GPU-h are solo speeds (measured for the parent class, level-4 L = 128 estimated at 4.5 u/h). Peak GB =
AMReX arena high-water + ~1.3 GB context, measured on the parent class where one exists; the preflight start-up
footprint × 1.8 reproduces every measured one (level-5 fly-by 34.0 → 58.8; L = 64 level-3 arm 17.8 → ~32). A card has
79.6 GB; most runs peak in step 1.

**Sharing a card buys nothing**: two L = 64 level-4 arms on one card ran 3.9 u/h each against 8.7 alone (GPU_PLAN
Phase 2b). Placement: none. All three cards are free, and nothing launches until the user says go.

Every remaining launch goes without frames: `--frames-fields none` with
`WHM_FRAMES_SUBSET="convergence study: no frames (the user's word, 2026-09-27)"`. CONV-8a/b use `--frames-fields chi`
instead, because the sign rule reads the chi slice cache. Close-outs use `WHM_MOVIES=0`.
The queued templates still write rolling checkpoints. The user's no-checkpoint word was given for CONV-1, CONV-2 and CONV-3w.

Pairs that fit if two must share: CONV-1 + CONV-2 (47 GB), CONV-2 + CONV-8 (61), CONV-1 + CONV-8 (68), CONV-2 +
CONV-7 (67). Never CONV-8a + CONV-8b (82), and nothing beside CONV-3/4/5/6.

Launch from the repo root with `L=grteclyn-wrapper/scripts/campaigns/wormhole_merger/launch.sh`,
`B=runs/wormhole_merger/bin`. Check `nvidia-smi` first, and redirect each launch (`< /dev/null > <log> 2>&1`):
```
WHM_FRAMES_SUBSET="convergence study: no frames (the user's word, 2026-09-27)" bash $L --gpu G --template params_single_eps_m1e2_ml5_t060.txt --name single_eps_m1e2_ml5_t060 --profile headon-scout --frames-fields none
WHM_FRAMES_SUBSET="convergence study: no frames (the user's word, 2026-09-27)" bash $L --gpu G --template params_single_eps_m1e2_halfstep_t060.txt --name single_eps_m1e2_halfstep_t060 --profile headon-scout --frames-fields none --binary $B/main3d_boost_2026-09-08.ex
bash $L --gpu G --template params_prod_L128_p012_lvl4_t100_freeze.txt --name v2_spiral_d12_p012_L128_lvl4_t100_freeze --profile orbit-modes --zoom 64 --coord 64 --binary $B/main3d_coreprof_2026-09-15.ex --restart "$PWD/runs/wormhole_merger/05_binary_spiral/p012/_keep_spiral_premerger_decay/BinaryWormholeChk03600"
WHM_FRAMES_SUBSET="convergence study: no frames (the user's word, 2026-09-27)" bash $L --gpu G --template params_prod_L128_p012_lvl4_wz1_t100_freeze.txt --name v2_spiral_d12_p012_L128_lvl4_wz1_t100_freeze --profile orbit-modes --zoom 64 --coord 64 --frames-fields none --binary $B/main3d_coreprof_2026-09-15.ex --restart "$PWD/runs/wormhole_merger/05_binary_spiral/p012/_keep_spiral_premerger_decay/BinaryWormholeChk03600"
WHM_FRAMES_SUBSET="convergence study: no frames (the user's word, 2026-09-27)" bash $L --gpu G --template params_flyby_p045_L128_lvl4_t095.txt --name merge_orbit_flip_d12_p045_L128_lvl4_t095 --profile orbit-modes-scan --frames-fields none
WHM_FRAMES_SUBSET="convergence study: no frames (the user's word, 2026-09-27)" bash $L --gpu G --template params_flyby_p045_L128_lvl3_t095.txt --name merge_orbit_flip_d12_p045_L128_lvl3_t095 --profile orbit-modes-scan --frames-fields none
WHM_FRAMES_SUBSET="convergence study: no frames (the user's word, 2026-09-27)" bash $L --gpu G --template params_headon_d8_lvl5from0_ball4_t100.txt --name merge_headon_flip_d8_lvl5from0_ball4_t100 --profile headon-modes --frames-fields none --binary $B/main3d_boost_2026-09-08.ex
WHM_FRAMES_SUBSET="convergence study: no frames (the user's word, 2026-09-27)" bash $L --gpu G --template params_scan_p035_lvl5_t080.txt --name merge_orbit_flip_d12_p035_lvl5_t080 --profile orbit-modes --frames-fields none
WHM_FRAMES_SUBSET="convergence study: chi only, for the sign rule (the user's word, 2026-09-27)" bash $L --gpu G --template params_ctrl_rest_d12_ml4_t015.txt --name ctrl_rest_d12_ml4_t015 --profile orbit --frames-fields chi
WHM_FRAMES_SUBSET="convergence study: chi only, for the sign rule (the user's word, 2026-09-27)" bash $L --gpu G --template params_ctrl_flip_d12_ml4_t015.txt --name ctrl_flip_d12_ml4_t015 --profile orbit --frames-fields chi
```
Each `--binary` is the partner's build: CONV-2 and CONV-6 compare against boost-built runs; CONV-3 splices onto the
coreprof-15 legs. The rest run on the pin, which has the same source as the level-4/5 partners.
- CONV-3's `--restart` must be an absolute path: the binary runs from the run dir, and a relative one aborted the first
  preflight. If level 4 dies before t = 57, restart from its last checkpoint ≥ 55 with `core_fill_from_time` there.
- CONV-6's ball is the stock ExtractionTagger: a 4th extraction radius R = 3.0 at level 4 refines r < 3.6. Its R = 3
  Ψ4 is not a wave product.
- CONV-8's parents wrote no shift or h_ij. The full plot list is added (output only), because the frame set needs it.

## Verdicts (the paper's wording; paper section in parentheses)

Every binary verdict below (two throats at rest, head-on, spiral, fly-by, waves and astrophysics from them) is on
superposed initial data: see CRITICAL at the top. Each stands only until its mode-3 rerun.

- **Single throat**: unstable fixed point, one exponential mode; the e-fold is within 2.5 % (level 4) and 15 % (level 3) of the PARAMETER-MATCHED González–Guzmán–Sarbach linear rate (our throat is their γ₁ = 0.5 member: T = 0.758; τ_lin = 5.13 M); truncation noise picks the branch. The collapse horizon SHRINKS 40 % as it swallows the phantom; the 9–11 % REGROWTH in the scans is NUMERICAL (spherical first law forbids it; it tracks a constraint-violation double layer reaching the MOTS; same in purely spherical data; the pure quadrupole never regrows; the head-on horizon never regrows either). The late (t ≳ 75) constraint rise of every single-throat arm is a refinement-boundary grid mode whose onset the L = 128 box does not delay — NOT the t500 wall reflection ["2026-09-25 (09:30)"]. **Inflation, the verdict (F4: L = 512, level 5, 1+log, quotable to t = 218)** ["2026-09-26 (05:00 UTC)"]: the kicked throat keeps growing, at every sample to t = 218 (3.81 → 14.5) and on to t = 390, with no trapped surface. It stays anti-trapped. θ_l = 0 sits on the neck and θ_k = 0 runs outward (R = 73 by t = 212): Shinkai–Hayward's trapping horizons turning cosmological. Over t = 16–40 it grows at the Shinkai–Hayward rate in its own proper time: local H R0 = 1.0–1.3, and a fit gives 1.22 (SH's massless 1.1, our linear mode 1.30). It leaves that rate at t ≈ 40 because 1+log freezes the lapse at the neck (α 0.57 → 0.02 by t = 100), so the neck's proper time nearly stops: only ~5 units pass between t = 40 and 218. The growth per unit t then falls (dR/dt 0.08 → 0.015). That is the slicing, not the throat. The neck also leaves the finest box at t = 44. No end state is measured: the record ends when the gauge wave reaches the wall. Only the onset is clean, because grid noise grows on the neck from t ≈ 120, after it leaves level 3. The t500 arm's turn at t = 161 was the same wall ["2026-09-25 (06:30)"]. (§IV)
- **Seeded throat**: a kick picks the fate opposite to its sign; the seed is not constraint-solved (H defect ∝ ε, 0.93×16π|ρ| on the shell at 1 %); ε = ±0.1 both collapse (+0.1 makes the throat a maximum, trapped at t = 1; −0.1 re-expands, then collapses) and die at the origin, not "from a Hamiltonian violation". (§II.D, §IV.C)
- **Two throats at rest**: like signs repel, opposite attract; force ∝ (d + δ)⁻², δ ≈ 3–4. (§V)
- **Head-on**: η = 4 MOTS located (level 3: R 5.41 at t = 30.0, lead ≥ 4.15; level 5 walks through its wall, R 5.29 → 5.17 over t = 34.2–40) [09-25, not yet in the paper]; common MOTS from t = 22, born with both throats' area (R = 1.01 √2 R⋆), around both throats behind a trapped neck; it never bounces (first law) and shrinks toward the pair's Bondi mass, 2M_B ≈ 4.1 (at t = 97: 1.07 R⋆, 4 % above 2M_ADM); the late decline is not accretion. The level-3 death is the grid's; level 5 runs clean to t = 100. (§VI)
- **Spiral**: every "spiral" is a plunge; a shape-free finder finds a common MOTS 5.4 units before the NaN, with BOTH wormholes inside (pits distinct to the χ floor) behind a common neck (R = 3.87 at t = 60); the wall is censored — under η = 4 too, at levels 5 (MOTS from ≤ 55.2, 0.04 before the 60.04 NaN) and 3 (at 61.5, 0.42 before 61.92), with M_MS within 0.3 % of the standard gauge's (η moves only the coordinate size); harmonic class: a θ_out = 0 surface 0.03 before its NaN, not trapped — open [plan/registry 09-25, not yet in the paper]; not "more momentum → stronger curvature" (max|K| says no); what falls with p is the grid's leverage. (§VII)
- **Fly-by / capture**: p = 0.45 scatters with no trapped surface; every p ≤ 0.25 merges, every p ≥ 0.35 does not — bound passes, not escapes (both start below the circular momentum; a central pull cannot capture without contact); the fly-by's recession after t = 43 is between the pits of two inflating mouths; the level-3 p = 0.45 closest approach (3.95) is a pit hop, level 5 passes at 4.8 ["2026-09-25 (09:30)"]. (§VII.A, new Fig. orbits)
- **Waves**: every channel radiates; the fly-by is loudest; the collapsing throat's wave is linear in ε₂ and the radial kick moves only its phase; it rings at the Schwarzschild period of its late mass (fit drawn); the scalar channel is comparable and negative-energy; the horizon switches it off; each vacuum control is drawn under its drainhole twin at R = 20 (Fig. 11(c,d)): the BBH spiral merges 2.9× lower and 43 units after the drainhole burst; the p = 0.45 BBH fly-by radiates one cycle at periapsis, 4.5× below the fly-by's peak, and nothing at the pass. (§VIII)
- **LIGO**: no candidate in 2.26 h of O3b, and none expected (no throat survives; conversions are at z ≳ 20). (§IX)
- **Astrophysics** (abstract + §X.B re-framed 2026-09-25: LISA is the headline, LIGO the null channel; the fly-by and spiral are the loudest LISA sources, optimal SNR 175–500 at 10⁵–10⁶ M⊙; conservative SNR ≥ 8 for every encounter 3×10⁴–4×10⁶, the fly-by to 2×10⁷; the fly-by marks no seed (its mouths inflate); lone collapse ≤ 6 conservative, ≈10 optimal — was "≈7"; Fig. 17(b) is now one burst's strain against the LISA noise, (c)'s Ω_GW the conversions only (head-on to spiral); the LISA SNRs are ledger rows recomputed by gw_search.lisa): no ghost-scalar wormhole inspiral (rotation is the open exception); collapse is a heavy-seed channel whose conversion bursts LISA would detect ONE BY ONE (SNR 61–500 at 10⁵–10⁶ M⊙, z = 20; > 8 from 3×10⁴ to 4×10⁶ M⊙), limited by abundance; the negative-energy deposit cannot be Λ (w, sign, size: Ω_WH ≈ 60–800 needed). (§X)

**Plan vs paper**: the paper is the current word — 1000 ledger rows, 0 problems, 828 recomputed (`claims.py check`, 2026-09-26 16:00 UTC, after the referee's fixes). Where the verdicts below disagree with the paper (the regrowth "NUMERICAL" → "not a measurement"; "wall" → "interior failure"; the mouths' shared clock; the baby-universe framing; the unconditional LISA headline), the paper wins. The plan's older entries still carry superseded readings (the regrowth as physics, "no horizon ever forms" for the spiral, "+17 %" regrowth, the ×7.8 fly-by growth as a measurement, the "21 % short" ringdown).

## Traps (each has cost a run)

- AMReX ignores keys nothing reads: old binaries run new params without the new
  physics. The launch preflight now refuses this (keys read only inside a switched-off
  feature are allowed by name in `preflight_allow.txt`).
- `amr.checkpoint_files_output = 0` silently disables checkpoints whatever the
  interval (19 templates carry that contradiction): the preflight now refuses it.
- Verify by effect: frame 0 against a reference, the first checkpoint on scratch.
- Norms after a restart and across boxes: compare onset times, never ratios.
- Star scans miss deformed MOTSs and emit scan-edge rows (R ≈ 47.6, 60.6) that are not horizons.
- A horizon hunt whose seeds "leave the box" found a trapped region bigger than the box, not nothing: every η = 4 null to 09-24 (half 3–5) was that. Size the box from a wide radial θ_out profile first (the finder now says LEFT THE BOX).
