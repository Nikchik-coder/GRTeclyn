# Status — 2026-09-24 06:20 UTC

Current state only; the evidence and history are in [`GPU_PLAN.md`](GPU_PLAN.md)
(headings quoted in brackets), the map in [`../../MAP.md`](../../MAP.md).
**Update this page whenever a verdict or the queue changes.**

## Live

| run | where | progress | ETA (at 6.84 units/h) | answers |
|---|---|---|---|---|
| `single_pureq_q1e2_L128_ml4_scalar_t500` | first GPU node, GPU 0 | t = 126.8 / 500 (06:15) | t = 150 in 3.4 h (09:40 today); t = 300 Fri 07:40; t = 500 Sat 09-26 ~12:50 | where the inflating throat ends: saturation, coast or turnover. Read at t = 100–112: "RUN ON" |

- That arm is **an unkicked L = 128 level-4 throat**, not a pure quadrupole: it was
  launched on the old campaign pin (`main3d_boost_2026-09-08.ex`), which does not read `wormhole_seed_l2_amplitude_A`
  (t = 0 data bit-identical to `single_hold_L128_t100`), nor the four
  `core_profile_*` keys — it writes **no core radial profile**. Still the right arm
  for the inflation question. ["2026-09-23 (evening) — the article audit…"]
- First GPU node, GPU 1: free. Second GPU node: not visible from here; the plan
  says its card is free since 09-23 18:13.

## Dead, not yet filed

- `single_eps_p1e2_t250` — K NaN on level 3 at t = 145.81 (00:54 today). No
  checkpoint was ever written: its params asked for a rolling three
  (`checkpoint_interval = 500`, `checkpoint_keep = 3`) with
  `amr.checkpoint_files_output = 0`, which switches checkpoints off. Plotfiles
  t = 142–145 remain on first-node scratch (9.5 GB). Nothing past t = 100 is
  quotable; "the box, not the throat". [2026-09-24 bullets under "2026-09-23 (afternoon)"]
- `merge_twin_p012_eta4_lvl5_t066_r05000` / `_r06000` (second node) — died at the wall, t = 60.04 / 60.05.

## Queued — nothing launches without the user's word

- **t250 TAKE 2** `single_eps_p1e2_L128_ml4_t250`: L = 128, level 4, ε = +10⁻², checkpoints on; ~37 h. Card: first-node GPU 1. Its template passes the full preflight on the new pin (06:12 today: seed takes, checkpoints on).
- **η = 4 level-5 death-window hunt** (Plt05520–06000): censored or naked. Needs a session on the second node.
- **Probe 2 MOTS location** (η = 4 head-on, level 5): verdict still pending, second node.
- Audit runs A1–C2 below. They run on the campaign pin, `main3d_guard_7166787a_2026-09-24.ex` since 06:10 today (stamped; reads the seed and the core profile). A restart of an old-pin run keeps the old pin unless `--binary` says otherwise.
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

- **Single throat**: unstable fixed point, one exponential mode; truncation noise picks the branch; the collapse horizon regrows 9–11 %, saturation open at t = 100; inflation end state open (t500). (§IV)
- **Seeded throat**: a kick picks the fate opposite to its sign; the "round-off-marginal pure quadrupole" is withdrawn (the seed never applied). (§IV.C)
- **Two throats at rest**: like signs repel, opposite attract; force ∝ (d + δ)⁻², δ ≈ 3–4. (§V)
- **Head-on**: common MOTS from t = 22 around both throats; the level-3 death is the grid's, level 5 runs clean to t = 100. (§VI)
- **Spiral**: every "spiral" is a plunge; a shape-free finder finds a common MOTS 5.4 units before the NaN; the wall is censored, mechanism open. (§VII)
- **Fly-by / capture**: p = 0.45 scatters with no trapped surface; merge/escape boundary between p = 0.25 and 0.35. (§VII.A)
- **Waves**: every channel radiates; the fly-by is loudest; the scalar channel is comparable to the gravitational one (ratio 3.2 → 0.8 with the cut on the running E_GW, 2.7 → 1.4 band-limited) and negative-energy; the horizon switches it off; the collapsing throat rings at the Schwarzschild period of its late mass. (§VIII)
- **LIGO**: no candidate in 2.26 h of O3b; fitting factors track record length, not source. (§X)
- **Astrophysics**: no wormhole inspiral; collapse as a heavy-seed channel is possible, not computed. (§XI)

**Plan vs paper**: the plan still carries superseded readings (spiral "no horizon
ever forms", regrowth "+17 %", spiral scalar ratio 2.41, ×7.8 fly-by growth as a
measurement, a spiral burst resolution check, the ringdown "21 % short"). The paper is the
current word: every number in it passes `claims.py check` (852 rows, 0 problems) since the
[`FINDINGS.md`](article/claims/FINDINGS.md) fixes of 2026-09-24 (27 numbers, ~20 statements).

## Traps (each has cost a run)

- AMReX ignores keys nothing reads: old binaries run new params without the new
  physics. The launch preflight now refuses this (keys read only inside a switched-off
  feature are allowed by name in `preflight_allow.txt`).
- `amr.checkpoint_files_output = 0` silently disables checkpoints whatever the
  interval (19 templates carry that contradiction): the preflight now refuses it.
- Verify by effect: frame 0 against a reference, the first checkpoint on scratch.
- Norms after a restart and across boxes: compare onset times, never ratios.
- Star scans miss deformed MOTSs and emit scan-edge rows (R ≈ 47.6, 60.6) that are not horizons.
