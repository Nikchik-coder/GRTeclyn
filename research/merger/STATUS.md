# Status — 2026-09-24 15:45 UTC

Current state only; the evidence and history are in [`GPU_PLAN.md`](GPU_PLAN.md)
(headings quoted in brackets), the map in [`../../MAP.md`](../../MAP.md).
**Update this page whenever a verdict or the queue changes.**

## Live

| run | where | progress | ETA (at 6.84 units/h) | answers |
|---|---|---|---|---|
| `single_pureq_q1e2_L128_ml4_scalar_t500` | first GPU node, GPU 0 | t = 191.9 / 500 (15:44) | t = 300 in 15.8 h (Fri 07:30); t = 500 in 45 h (Sat 09-26 ~12:45) | where the inflating throat ends: saturation, coast or turnover. Read at t = 100–112: "RUN ON" |
| `single_eps_p1e2_L128_ml4_t250` (t250 TAKE 2) | first GPU node, GPU 1, since 06:26 | t = 70.6 / 250 (15:44), 7.6 u/h | t = 250 in 23.6 h (Fri 09-25 ~15:20) | **its question is gone**: the regrowth it was to follow is numerical (below). Useful to t ≈ 70 for the constraint history at the horizon (rolling Chk, plotfiles) and as a box check (= the L = 64 level-4 arm to 1e-4 in R through t = 41). **Stop now or run on: the user's call** — the remaining ~24 GPU-h would buy G14/G15 instead |

- The t500 arm is **an unkicked L = 128 level-4 throat**, not a pure quadrupole: it was
  launched on the old campaign pin (`main3d_boost_2026-09-08.ex`), which does not read `wormhole_seed_l2_amplitude_A`
  (t = 0 data bit-identical to `single_hold_L128_t100`), nor the four
  `core_profile_*` keys — it writes **no core radial profile**. Still the right arm
  for the inflation question. ["2026-09-23 (evening) — the article audit…"]
- TAKE 2 launched on the user's word ("lets launch this on gpu 1"), new pin, preflight PASS
  (seed takes); consumer `headon-modes`, whole-box frames (zoom 128, coord 64), keep-last 4.
  Watch signal from t ≈ 80: the corners of the refinement square (the mode that killed the
  L = 64 take at 145.8). Second GPU node: not visible from here; the plan says its card is
  free since 09-23 18:13.

## Dead, not yet filed

- `single_eps_p1e2_t250` — K NaN on level 3 at t = 145.81 (00:54 today). No
  checkpoint was ever written: its params asked for a rolling three
  (`checkpoint_interval = 500`, `checkpoint_keep = 3`) with
  `amr.checkpoint_files_output = 0`, which switches checkpoints off. Plotfiles
  t = 142–145 remain on first-node scratch (9.5 GB). Nothing past t = 100 is
  quotable; "the box, not the throat". [2026-09-24 bullets under "2026-09-23 (afternoon)"]
- `merge_twin_p012_eta4_lvl5_t066_r05000` / `_r06000` (second node) — died at the wall, t = 60.04 / 60.05.

## Queued — nothing launches without the user's word

- **η = 4 level-5 death-window hunt** (Plt05520–06000): censored or naked. Needs a session on the second node.
- **Probe 2 MOTS location** (η = 4 head-on, level 5): verdict still pending, second node.
- **The runs the paper now asks for: G1–G16** ["2026-09-24 (afternoon) — the user's read of the whole paper"], ~300 GPU-h in all; the cheap discriminators first: G14/G15 (what makes the numerical regrowth, ~12 GPU-h each), G13 (the ε₂ decades, ~22), G1 (η = 4 chain on L = 128, ~12), G4 (curvature invariants at the wall, ~1 + code).
- Audit runs A1–A4 below; B1–B4 and C1–C2 are now G8–G11 and G6–G7. They run on the campaign pin, `main3d_guard_7166787a_2026-09-24.ex` since 06:10 today (stamped; reads the seed and the core profile). A restart of an old-pin run keeps the old pin unless `--binary` says otherwise.
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

- **Single throat**: unstable fixed point, one exponential mode; the e-fold is within 2.5 % (level 4) and 15 % (level 3) of the PARAMETER-MATCHED González–Guzmán–Sarbach linear rate (our throat is their γ₁ = 0.5 member: T = 0.758; τ_lin = 5.13 M); truncation noise picks the branch. The collapse horizon SHRINKS 40 % as it swallows the phantom; the 9–11 % REGROWTH in the scans is NUMERICAL (spherical first law forbids it; it tracks a constraint-violation double layer reaching the MOTS; same in purely spherical data; the pure quadrupole never regrows). Inflation end state open (t500). (§IV)
- **Seeded throat**: a kick picks the fate opposite to its sign; the seed is not constraint-solved (H defect ∝ ε, 0.93×16π|ρ| on the shell at 1 %); ε = ±0.1 both collapse (+0.1 makes the throat a maximum, trapped at t = 1; −0.1 re-expands, then collapses) and die at the origin, not "from a Hamiltonian violation". (§II.D, §IV.C)
- **Two throats at rest**: like signs repel, opposite attract; force ∝ (d + δ)⁻², δ ≈ 3–4. (§V)
- **Head-on**: common MOTS from t = 22, born with both throats' area (R = 1.01 √2 R⋆), around both throats behind a trapped neck; it never bounces (first law) and shrinks toward the pair's Bondi mass, 2M_B ≈ 4.1 (at t = 97: 1.07 R⋆, 4 % above 2M_ADM); the late decline is not accretion. The level-3 death is the grid's; level 5 runs clean to t = 100. (§VI)
- **Spiral**: every "spiral" is a plunge; a shape-free finder finds a common MOTS 5.4 units before the NaN, with BOTH wormholes inside (pits distinct to the χ floor) behind a common neck (R = 3.87 at t = 60); the wall is censored; not "more momentum → stronger curvature" (max|K| says no); what falls with p is the grid's leverage. (§VII)
- **Fly-by / capture**: p = 0.45 scatters with no trapped surface; every p ≤ 0.25 merges, every p ≥ 0.35 does not. (§VII.A)
- **Waves**: every channel radiates; the fly-by is loudest; the collapsing throat's wave is linear in ε₂ and the radial kick moves only its phase; it rings at the Schwarzschild period of its late mass (fit drawn); the scalar channel is comparable and negative-energy; the horizon switches it off. (§VIII)
- **LIGO**: no candidate in 2.26 h of O3b, and none expected (no throat survives; conversions are at z ≳ 20). (§IX)
- **Astrophysics**: no ghost-scalar wormhole inspiral (rotation is the open exception); collapse is a heavy-seed channel whose conversion bursts LISA would detect ONE BY ONE (SNR 61–500 at 10⁵–10⁶ M⊙, z = 20; > 8 from 3×10⁴ to 4×10⁶ M⊙), limited by abundance; the negative-energy deposit cannot be Λ (w, sign, size: Ω_WH ≈ 60–800 needed). (§X)

**Plan vs paper**: the paper is the current word — 956 ledger rows, 0 problems (`claims.py check`, 2026-09-24 15:40). The plan's older entries still carry superseded readings (the regrowth as physics, "no horizon ever forms" for the spiral, "+17 %" regrowth, the ×7.8 fly-by growth as a measurement, the "21 % short" ringdown).

## Traps (each has cost a run)

- AMReX ignores keys nothing reads: old binaries run new params without the new
  physics. The launch preflight now refuses this (keys read only inside a switched-off
  feature are allowed by name in `preflight_allow.txt`).
- `amr.checkpoint_files_output = 0` silently disables checkpoints whatever the
  interval (19 templates carry that contradiction): the preflight now refuses it.
- Verify by effect: frame 0 against a reference, the first checkpoint on scratch.
- Norms after a restart and across boxes: compare onset times, never ratios.
- Star scans miss deformed MOTSs and emit scan-edge rows (R ≈ 47.6, 60.6) that are not horizons.
