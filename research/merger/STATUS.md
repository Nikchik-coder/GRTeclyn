# Status — 2026-10-08 ~05:50 UTC

What is live, what is planned, the main results — nothing else. Run-by-run outcomes are in
`results/merger/runs_registry.tsv`, cleanups in `runs/wormhole_merger/manifests/`, the map in
[`../../MAP.md`](../../MAP.md). The page before this compaction (the campaign diary to 10-08) is
`git show f2c4caa9:research/merger/STATUS.md`. **When a run ends, its row leaves Live and its result goes into
Main results in a line or two; the details go to the registry.**

## Live

| run | node / card | t | stop | speed | ETA | checkpoints |
|---|---|---|---|---|---|---|
| CONV-fz lvl7 `farzone_headon_flip_d8_L512_lvl7_t100_csm` | second / 0 | 68.3 (05:45 UTC; launched 07:34 UTC 10-07) | 100 | 3.9 u/h | ~8.2 h → ~13:55 UTC 10-08 | every 25 units, keep 3 (the user): t = 0 / 25 / 50 written |

- The first node (two H100s) is idle since 03:10 UTC 10-08; its scratch is empty (1.1T free).
- NFS checkpoints: only CONV-fz's two t = 100 states, lvl5's and FARZONE-ho's `Chk02500` (64G, in their
  `08_convergence/` run dirs), kept for the three-level constraint check (the user, 10-08); lvl7's joins them at its
  close-out. The second node also keeps the HFL cell (60G, deliberate).

## Planned (nothing launches without the go)

**Next: CONV-fz, the head-on's three-level convergence set (REQUIRED).** lvl5 / FARZONE-ho / lvl7 = Δx 1/16, 1/32,
1/64, all on FARZONE-ho's L = 512 box. When lvl7 lands:
1. Copy its Chk02500 to its NFS run dir. Its scratch is on the second node, so the copy runs there. Close it out
   as lvl5 was: into `08_convergence/`, frames kept, no movies.
2. Read the three levels to t = 100: Richardson on the common MOTS (birth t, R, M_MS), the throat tracks and
   r Ψ4 / E/M at R = 10–44.
3. Read H outside the MOTS from the three Chk02500 with
   `grteclyn-wrapper/scripts/analysis/merger_feedback/c_checkpoint_hamiltonian.py` (level 4, `--dx0 2.0 --centre
   256 256 256 --half 7.9 --rmin 3.7 --rstep 0.3`; it reads H and Θ, not Mom). Then wipe the three checkpoints.
4. Table III already counts it, as an in-flight estimate (+1 run, +30.31 GPU-h: 22.18 h to t = 68.3, then 8.13 h at
   3.9 u/h). At its pack: list it in `table1_groups.tsv` as `convergence, mode 3`, then drop the constants from
   `clmDetRunsTotal`, `clmDetRunsConvergence` and `clmDetGpuHours` (ledger_detector.tsv). Until then the claims
   check fails on those rows (it double-counts the run).
5. Fig. 11(d) draws lvl5 and FARZONE-ho; its caption quotes the interim read below as manual rows (`clmConvFzDxHi`,
   `clmConvFzFineTime`, `clmConvFzOrder`). At its pack: add lvl7 to `results/merger/analysis/headon_axis_modes.py`'s
   STREAMS and run it (its `_axis.dat`), then re-render `plot_convergence`, which already lists lvl7 in `CONV_FZ`:
   (d) then draws 1/64 and the 1/32 − 1/64 difference. Make the three rows def / auto, and drop the caption's "so
   far run to t = 67".

At t = 100 every fine level is one cube about the centre: level 4 ±10, level 5 ±5, level 6 ±2.5 (level 7 ±1.25
expected). The MOTS has coordinate radius 3.48–3.53, so level 6 pokes out of it only in its cube's corners
(r ≤ 4.33). The checkpoints hold 27 components in the code's order, with 3 ghost cells, as little-endian doubles.
So outside the MOTS the three levels share one grid: this read checks that the interior's resolution does not leak
out, and cannot give a convergence order (that needs the static throat's levels 2/3/4, ~3 GPU-h, no go).

**The H table for Fig. 11(e): do it now on the finished runs (CPU, on the node).** `plot_convergence` (e) draws
⟨H_ADM⟩ against r outside the MOTS, one curve per level, from `results/merger/analysis/convfz_constraints_t100.tsv`.
Its caption sentence and ledger row (max |H_1/16 / H_1/32 − 1|, `conv_farzone` `ham`) go in once the table is
pushed. Until then `plot_convergence` cannot render, because it needs the table.
1. Give `c_checkpoint_hamiltonian.py` an `--out TSV` option.
   - Start the file with `#` lines: what it is, the exact command, the date.
   - Then the header `run	t	level	r	H_ADM	rho16pi	Theta	alpha	dZ`, and one row per checkpoint and shell, with `run` = the
     checkpoint's parent dir name.
   - A rerun keeps the rows of the runs it is not given.
   - Write only the shells clear of the 4-cell stencil band at the cube's edge (`np.roll` wraps there): r ≤ 7.3 at
     `--half 7.9`.
2. Run it on lvl5's and FARZONE-ho's Chk02500 with step 3's arguments, plus
   `--out results/merger/analysis/convfz_constraints_t100.tsv`. Commit the script and the table, and push.
3. lvl7: the same once its Chk02500 is in its run dir (step 1). Commit and push the updated table, then re-render
   `plot_convergence`.

Interim (lvl7 to t = 67, and H from lvl5's and FARZONE-ho's Chk02500):
- E/M at R = 10 converges (C = 3.2, order ~1.7); FARZONE-ho is within 0.1 % of the extrapolated value.
- The MOTS R and M_MS agree across the levels to ≤ 6e-4.
- The r Ψ4 differences (~1e-3 of peak) shrink more slowly than second order: the χ-floored core.
- ⟨H_ADM⟩ on level 4 outside the MOTS (r = 3.7–7.3): −4.9e-4 falling to −2.3e-4, the same in lvl5 and FARZONE-ho
  to 0.6–1.4 % (FARZONE-ho ~1 % larger). Θ agrees to ~1.5 %. So the exterior violation does not move when the finest
  level goes from 5 to 6. The r = 7.6 shell is the cube's edge and is not read.

**Paper updates waiting on the user's call:**
- FARZONE-ho's far-zone energy: Sec. VIII and Fig. `convergence`(c). (Fig. 8's head-on row is FARZONE-ho since 10-08;
  Fig. 9 and every quoted energy still read the production chain.)
- CONV-fz: App. A's text.
- Done 10-08: Fig. 11(d), CONV-fz at Δx 1/16 and 1/32, with lvl7's interim order in the caption (step 5 above).
- Done 10-08: SCATTER-fate in Fig. 1 (the like-signed branch ends in inflation) and Sec. V C (Video 12).
- Done 10-08: Table III counts the convergence set (6 runs, lvl7 in flight) and SCATTER-fate: 103 runs, 592 GPU-h.

**arXiv submission (decided 10-08).** After lvl7's close-out and the final PDF:
- Merge feature/merger into develop, keeping research/ off develop as on 10-06. Tag the merge `v1.0-wormhole-merger`.
- Publish a GitHub release on the tag (public, not a draft). No Zenodo DOI: there is no Zenodo account (10-08). The
  cost section's code statement cites the tag since 10-08.
- `CITATION.cff`, `README.md` and `results/README.md` describe this paper since 10-08, with arXiv placeholders
  `XXXX.XXXXX`. Set `date-released` in `CITATION.cff` at the release. (`.zenodo.json` describes it too, unused.)
- arXiv: gr-qc primary, cross-lists astro-ph.HE and astro-ph.CO. The abstract is cut to ~1,760 rendered characters
  (the form takes 1,920).
- The source package is research.tex, numbers.tex and the 15 figure PDFs under `figures/`, which the graphicspath
  searches first. A clean-copy pdfLaTeX build passes (26 pages). Still to fix: the overfull line at tex line 167
  (10.6 pt) and the 0.6 pt float overrun at line 379.
- Before submitting: Videos 1–12 public, and both authors' sign-off.
- After the number: fill the placeholders (README, results/README.md, CITATION.cff) and the release notes.

RUNS FOR THE PAPER — proposed, no go yet (CLAUDE.md: anything a run or an analysis could settle goes here, with a cost):

| id | what | cost |
|---|---|---|
| CONV-lbf-w (recommended) | the wave-zone test on exact-boost data: CONV-csm-w's recipe (`extraction_levels 0 1 0 0`) on P045-T100's params, t = 0–40 | ~11 GPU-h, a whole card |
| HARM-oct (referee 1, recommended) | the ε = −10⁻² inflating throat in harmonic slicing (octant, F3's template, stop 45): does 1+log shape the inflation? | ~1 GPU-h |
| SCATTER-box | SCATTER-fate in a bigger box, to follow the inflated mouths past t ≈ 50, where the L = 64 box's collapsed lapse reaches the sponge (a box change: the user's call) | ~25–30 GPU-h (L = 128, N = 256) |
| SIGN-d (referee minor 2) | flipped rest pairs at d = 14 / 16 / 18 (+ d = 12 at level 4): does pull/push 1.462 tend to 3/2? | ~1–2 GPU-h |
| FLIP-a | flipped pairs at a = 1.5 / 3: the coordinate under-read against finite size (predicted 1.889 / 1.222) | ~1 GPU-h each |
| KRETSCH (referee 4) | curvature invariants (R, I, J) at a dying core, from plotfiles every step over a leg's last unit; no death checkpoint is kept, so it reruns to the death | ~1 GPU-h + the rerun |
| SOLVE-t0 (optional) | the mode-3 d = 8 head-on at t = 0 (`constraint_solve_t0_check.py`) | CPU minutes |
| PALETTE (no GPU) | a greyscale-safe accent: GOLD and FAINT print as the same grey; re-render every figure | CPU |

Analysis only: E_GW(p = 0.12) on SPIRAL-lbf's packed streams (a fourth point for Sec. VIII D).

## Main results (the paper's wording; every quoted number is a ledger row)

**Method:**
- Every binary starts from matched mode-3 initial data (`constraint_solve_puncture_mode = 3`).
- A moving throat is the exact Lorentz-boosted drainhole (momentum model 1), with a per-throat slicing freeze and the
  boosted-pair solve. Its t = 0 axis ratios sit on 1/γ to 6e-5.
- Every horizon number comes from the 3D MOTS finder (`mots_spectral.dat`).
- The superposed and Bowen–York campaigns are archived in `00_archive/`.

**Single throat** (§III–IV):
- It is an unstable fixed point with one exponential mode. At small amplitude, τ = 5.12 / 5.23 at levels 3 / 4,
  against the linear 5.13. Truncation noise picks the branch.
- Collapse: the horizon shrinks 40 %. The 9–11 % "regrowth" is numerical.
- Inflation (F4, to t = 218): the throat keeps growing, anti-trapped, at the Shinkai–Hayward rate in proper time.
- A seeded throat goes opposite to its kick. On solved data the ε = 0.1 seed is born trapped (SEED-csm).

**A moving throat** (p = 0.45, v = 0.41; Fig. 2(d)): it collapses on the resting throat's own mode (τ = 5.0–6.1,
against 5.12), at levels 3 and 4.

**Two throats at rest** (§V, Fig. 4):
- Like signs repel and opposite signs attract.
- Pull/push is 1.462 ± 0.022, the fixed-scalar-potential value of 3/2.
- The force goes as (d + δ)⁻² with δ = 2.65.
- The push grows with the width as a^1.2–1.4, not the point-charge a².

**SCATTER-fate** (NEW 10-08, in the paper: Fig. 1, Sec. V C; packed `03_two_throats/csm/ctrl_rest_d12_csm_t100`): the
like-signed d = 12 rest pair recedes, and both mouths inflate, mirror-symmetric.
- The separation grows from 11.94 to 26.4 by t = 60.
- The throat R grows from 3.88 to 4.78 by t = 30 (the per-mouth scan; anti-trapped), then to 7.7 by t ≈ 48 (χ
  slices).
- There is no MOTS about either mouth after t = 16.5.
- The constraints sit at their t = 0 level to t = 50. Then the L = 64 box's collapsed lapse reaches the sponge.
- Trust t ≤ 80 (the user); the run died at t = 95.08.
- No GW burst: the l = 2 Ψ4 at R = 14 and 30 is a smooth, single-signed drift that grows with the inflation (e-fold
  ~5 at R = 30), the same in every like-signed rest pair from t = 0 (d = 12/14/18 alike); the box (L = 64) cannot
  split it into near field and radiation.

**Head-on** (d = 8, t = 0–100; §VI, Fig. 5):
- A common MOTS forms at t = 18.0 (R 5.634, M_MS 2.817 > M_ADM 2.357) and holds to the end (R 4.779, M_MS 2.389 at
  t = 100).
- It never bounces, and R settles toward 2 M_ADM.
- After it forms, the ℓ = 1 scalar rings at ω = 0.122–0.124, against the final mass's QNM of 0.1226.

**FARZONE-ho** (NEW 10-08; packed `08_convergence/`; Fig. 8's head-on row, Video 11): the head-on in an L = 512 box with spheres to R = 180
(R/M = 76), clean over t = 0–250.
- The near zone reproduces production: E/M at R = 10 / 18 / 44 within −0.3 / −0.1 / +1.0 %.
- On windows aligned with the burst, E/M converges outward: 7.66e-3 (R = 44), 6.98e-3 (90), 6.82e-3 (150), 6.81e-3
  (180). So E∞ ≈ 6.8e-3, 20 % below the quoted 8.5e-3.
- Half of that gap is the pre-arrival content the paper's window keeps; half is the fall from R = 44 outward.
- The paper's fixed window, t − R ≤ 56, does not follow the burst's tortoise drift, and on it E/M rises past R = 60.

**Orbits on boosted data** (d = 12, §VII):
- p = 0.12 spirals in but never merges (died t = 71.78, trust 56.5; level 4 agrees).
- p = 0.25 and 0.45 scatter: no wall, no MOTS.
- p = 0.60 and 0.90 plunge. At p = 0.60 there is no MOTS at level 4 or 5: the stall is physical. At p = 0.90 the run
  dies at t = 45.28 at both levels.
- So the capture boundary sits in (0.45, 0.60).
- The d = 6, p = 0.10 design point merges (common MOTS from t = 13; t = 0–100).
- Each companion is a −ε kick (−0.4 % at d = 12, −1.2 % at d = 8) that seeds inflation, so a merger is a race to
  contact.

**Masses:**
- A moving pair's mass is M_ADM_boost; the face estimate drops Σ(γ−1)σm.
- The measured t = 0 ADM energies are 2.304 / 2.317 / 2.282 at p = 0.25 / 0.45 / 0.60, flat in p.
- The paper quotes the d = 12 pairs' E/M per this measured mass.

**Waves** (§VIII):
- Every channel radiates.
- E_GW(p) turns over between p = 0.45 and 0.60; the p = 0.45 fly-by radiates the most.
- The scalar channel is comparable and negative-energy, and the horizon switches it off.
- The core damping does not shape the fly-by's waves (DAMP-off, to 1e-7).

**Searches** (§IX–X): LIGO O3b (2.25 h, 154 templates) finds no candidate, and none is expected. LISA is the
headline channel.

**Convergence** (App. A):
- The static throat at levels 2 / 3 / 4 against the exact solution: order ~2.2 early, ~3 later.
- The wave zone is resolved (CONV-csm-w: 0.01–0.15 % of peak).
- CONV-fz, the binary three-level set (Fig. 11(d), lvl7 in flight): Δx 1/16 and 1/32 agree in r Ψ4 at R = 10 to
  0.55 % of the peak and in E at R = 10 to 0.29 %, and both find the common MOTS from t = 18, R and M_MS equal to
  0.084 %.

## Traps (each has cost a run)

- The logged L2 constraint norms are level 0 only (Δx = 0.5 on L = 128, 2 on L = 512). A moving pit spikes them
  while the fine solution is clean, and they cannot show convergence. Read the finest level (`ham_level_map.py`)
  before calling a run unconstrained.
- Level-1 noise grows at σ = 0.1, doubling every ~6 units on the ±20 cube; σ = 0.3 cures it. Wave spheres inside
  level 1 (R ≤ 20) or across its corners (R = 28, 30) are contaminated late. Use the symmetry-forbidden modes as the
  monitor.
- Compare norms across restarts and boxes by onset times, never by ratios.
- A relative path in `--consume-args` (e.g. `--horizon-track`) resolves from the run dir, the consumer's cwd, and
  fails silently. Pass absolute paths.
