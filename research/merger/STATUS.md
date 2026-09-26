# Status — 2026-09-26 05:00 UTC

Current state only; the evidence and history are in [`GPU_PLAN.md`](GPU_PLAN.md)
(headings quoted in brackets), the map in [`../../MAP.md`](../../MAP.md).
**Update this page whenever a verdict or the queue changes.**

## Live

Nothing. Both cards on the first node are free.

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
scratch is empty; the paper session's `plt_take2/` plotfile copies (77 GB, G16's input) sit in
that session's scratchpad there.

Second node (one H100): free; the η = 4 level-5 probes are closed out, hunted and filed
["2026-09-25 (morning)"]. Its scratch is empty (205 GB pruned, MANIFEST_CLEANUP_2026-09-25).

Run tree: every plotfile deleted on the user's word; 192 → 52 GB. Two checkpoints remain for
the user's call: Chk05700 (26 GB, G4's input) and Chk03600 (20 GB, the t = 36 seed of G8/G9).

## Queued — nothing launches without the user's word

- **Paper edit (no GPU):** carry the 09-25 η = 4 horizon results into §VII.C (ledger rows, manual, sourced from the plan table).
- **Paper edit, DONE 2026-09-26 — the inflation radii** ["2026-09-25 (13:30)", "2026-09-26 (05:00 UTC)"]: the level-4 / L = 64 / L = 128 inflation radii are r/√χ lower bounds. The user's decision (2026-09-26): "they are no go for the paper — only L512 lvl5 is proper". Fig. `single_throat_inflation` and §IV's inflation text are being rebuilt on F4 alone (full-metric R, quoted to t = 218), and the level-4 radius claims are removed.
- **Inflation campaign, PROPOSED (the user's call)** [same entry]: corrected R + horizon tracker in the consumer; a slicing that does not freeze at the throat (harmonic / shock-avoiding, C1); refinement following the horizons instead of fixed cubes; the compactified other universe resolved or excised.
- **Paper edit, DONE 2026-09-26 — the inflation ending** ["2026-09-25 (06:30)", "2026-09-26 (05:00 UTC)"]: §IV.D's "unbounded coasting, as in the spherical literature" (research.tex ≈ l. 267) misstates Shinkai–Hayward and GGS II, whose ending is exponential inflation in PROPER time. Replace it with F4's measurement: exponential in the neck's proper time at H R0 = 1.22 over t = 16–40 (SH 1.1, linear 1.30), with the coordinate-time slowdown being 1+log freezing the neck's clock. It goes in with the paper figure's rework (caption and a concise text edit).
- **The runs the paper now asks for: G1–G16** ["2026-09-24 (afternoon) — the user's read of the whole paper"], ~300 GPU-h in all; the cheap discriminators first: G14/G15 (what makes the numerical regrowth, ~12 GPU-h each), G13 (the ε₂ decades, ~22), G1 (η = 4 chain on L = 128, ~12), G4 (curvature invariants at the wall, ~1 + code).
- Audit runs A1–A4 below; B1–B4 and C1–C2 are now G8–G11 and G6–G7. They run on the campaign pin, `main3d_guard_7166787a_2026-09-24.ex` since 2026-09-24 06:10 (stamped; reads the seed and the core profile). A restart of an old-pin run keeps the old pin unless `--binary` says otherwise.
- Ambiguous: the lp2 level-5 head-on is "CANCELLED" [REFEREE-QUEUE CLOSEOUT] but listed as queued [evening audit]; treat as cancelled.

## Open questions → the runs that settle them  ["2026-09-23 (evening) — the article audit…"]

| id | question | cost |
|---|---|---|
| A1 | pure-quadrupole collapse on a seeded binary: does it reproduce? its scalar record | ~10 h |
| A2 | kicked-quadrupole lone collapse, scalar decay (now a spherical-kick stand-in) | ~10 h |
| A3 | unkicked throat's horizon time (t = 61 is only an upper bound) | ~6 h |
| A4 | p = 0.35: escape or turn back? (pins 0.25 < p < 0.35) | ~8 h |
| B1 | spiral scalar/GW ratio through the burst | ~24 h |
| B2 | first resolution test of the spiral burst | ~15–20 h |
| B3 | half-mass head-on at level 5 past its censored wall? | ~12–18 h |
| B4 | fly-by mouths after t ≈ 43 (R = 33 is a window edge); needs a re-run, no plotfile survives | ~47 h |
| C1 | the wall: slicing shock or physical? (shock-avoiding slicing) | code + ~12 h |
| C2 | close Ṁ_ADM = −F_GW − F_φ (surface ADM mass, flux shift terms) | code + ~28 h |

## Verdicts (the paper's wording; paper section in parentheses)

- **Single throat**: unstable fixed point, one exponential mode; the e-fold is within 2.5 % (level 4) and 15 % (level 3) of the PARAMETER-MATCHED González–Guzmán–Sarbach linear rate (our throat is their γ₁ = 0.5 member: T = 0.758; τ_lin = 5.13 M); truncation noise picks the branch. The collapse horizon SHRINKS 40 % as it swallows the phantom; the 9–11 % REGROWTH in the scans is NUMERICAL (spherical first law forbids it; it tracks a constraint-violation double layer reaching the MOTS; same in purely spherical data; the pure quadrupole never regrows; the head-on horizon never regrows either). The late (t ≳ 75) constraint rise of every single-throat arm is a refinement-boundary grid mode whose onset the L = 128 box does not delay — NOT the t500 wall reflection ["2026-09-25 (09:30)"]. **Inflation, the verdict (F4: L = 512, level 5, 1+log, quotable to t = 218)** ["2026-09-26 (05:00 UTC)"]: the kicked throat keeps growing, at every sample to t = 218 (3.81 → 14.5) and on to t = 390, with no trapped surface. It stays anti-trapped. θ_l = 0 sits on the neck and θ_k = 0 runs outward (R = 73 by t = 212): Shinkai–Hayward's trapping horizons turning cosmological. Over t = 16–40 it grows at the Shinkai–Hayward rate in its own proper time: local H R0 = 1.0–1.3, and a fit gives 1.22 (SH's massless 1.1, our linear mode 1.30). It leaves that rate at t ≈ 40 because 1+log freezes the lapse at the neck (α 0.57 → 0.02 by t = 100), so the neck's proper time nearly stops: only ~5 units pass between t = 40 and 218. The growth per unit t then falls (dR/dt 0.08 → 0.015). That is the slicing, not the throat. The neck also leaves the finest box at t = 44. No end state is measured: the record ends when the gauge wave reaches the wall. Only the onset is clean, because grid noise grows on the neck from t ≈ 120, after it leaves level 3. The t500 arm's turn at t = 161 was the same wall ["2026-09-25 (06:30)"]. (§IV)
- **Seeded throat**: a kick picks the fate opposite to its sign; the seed is not constraint-solved (H defect ∝ ε, 0.93×16π|ρ| on the shell at 1 %); ε = ±0.1 both collapse (+0.1 makes the throat a maximum, trapped at t = 1; −0.1 re-expands, then collapses) and die at the origin, not "from a Hamiltonian violation". (§II.D, §IV.C)
- **Two throats at rest**: like signs repel, opposite attract; force ∝ (d + δ)⁻², δ ≈ 3–4. (§V)
- **Head-on**: η = 4 MOTS located (level 3: R 5.41 at t = 30.0, lead ≥ 4.15; level 5 walks through its wall, R 5.29 → 5.17 over t = 34.2–40) [09-25, not yet in the paper]; common MOTS from t = 22, born with both throats' area (R = 1.01 √2 R⋆), around both throats behind a trapped neck; it never bounces (first law) and shrinks toward the pair's Bondi mass, 2M_B ≈ 4.1 (at t = 97: 1.07 R⋆, 4 % above 2M_ADM); the late decline is not accretion. The level-3 death is the grid's; level 5 runs clean to t = 100. (§VI)
- **Spiral**: every "spiral" is a plunge; a shape-free finder finds a common MOTS 5.4 units before the NaN, with BOTH wormholes inside (pits distinct to the χ floor) behind a common neck (R = 3.87 at t = 60); the wall is censored — under η = 4 too, at levels 5 (MOTS from ≤ 55.2, 0.04 before the 60.04 NaN) and 3 (at 61.5, 0.42 before 61.92), with M_MS within 0.3 % of the standard gauge's (η moves only the coordinate size); harmonic class: a θ_out = 0 surface 0.03 before its NaN, not trapped — open [plan/registry 09-25, not yet in the paper]; not "more momentum → stronger curvature" (max|K| says no); what falls with p is the grid's leverage. (§VII)
- **Fly-by / capture**: p = 0.45 scatters with no trapped surface; every p ≤ 0.25 merges, every p ≥ 0.35 does not — bound passes, not escapes (both start below the circular momentum; a central pull cannot capture without contact); the fly-by's recession after t = 43 is between the pits of two inflating mouths; the level-3 p = 0.45 closest approach (3.95) is a pit hop, level 5 passes at 4.8 ["2026-09-25 (09:30)"]. (§VII.A, new Fig. orbits)
- **Waves**: every channel radiates; the fly-by is loudest; the collapsing throat's wave is linear in ε₂ and the radial kick moves only its phase; it rings at the Schwarzschild period of its late mass (fit drawn); the scalar channel is comparable and negative-energy; the horizon switches it off; each vacuum control is drawn under its drainhole twin at R = 20 (Fig. 11(c,d)): the BBH spiral merges 2.9× lower and 43 units after the drainhole burst; the p = 0.45 BBH fly-by radiates one cycle at periapsis, 4.5× below the fly-by's peak, and nothing at the pass. (§VIII)
- **LIGO**: no candidate in 2.26 h of O3b, and none expected (no throat survives; conversions are at z ≳ 20). (§IX)
- **Astrophysics** (abstract + §X.B re-framed 2026-09-25: LISA is the headline, LIGO the null channel; the fly-by and spiral are the loudest LISA sources, optimal SNR 175–500 at 10⁵–10⁶ M⊙; conservative SNR ≥ 8 for every encounter 3×10⁴–4×10⁶, the fly-by to 2×10⁷; the fly-by marks no seed (its mouths inflate); lone collapse ≤ 6 conservative, ≈10 optimal — was "≈7"; Fig. 17(b) is now one burst's strain against the LISA noise, (c)'s Ω_GW the conversions only (head-on to spiral); the LISA SNRs are ledger rows recomputed by gw_search.lisa): no ghost-scalar wormhole inspiral (rotation is the open exception); collapse is a heavy-seed channel whose conversion bursts LISA would detect ONE BY ONE (SNR 61–500 at 10⁵–10⁶ M⊙, z = 20; > 8 from 3×10⁴ to 4×10⁶ M⊙), limited by abundance; the negative-energy deposit cannot be Λ (w, sign, size: Ω_WH ≈ 60–800 needed). (§X)

**Plan vs paper**: the paper is the current word — 963 ledger rows, 0 problems, 805 recomputed (`claims.py check`, re-run 2026-09-25 17:00 UTC after Fig. 17's new panel (b)) — EXCEPT the 09-25 η = 4 horizon results and the spherical-literature inflation ending (Shinkai–Hayward / GGS II: exponential in proper time), which are in the plan and registry only. The plan's older entries still carry superseded readings (the regrowth as physics, "no horizon ever forms" for the spiral, "+17 %" regrowth, the ×7.8 fly-by growth as a measurement, the "21 % short" ringdown).

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
