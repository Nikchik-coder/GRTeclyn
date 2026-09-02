# GPU plan for the paper runs

*Drafted 2026-09-02, while wave 8 (fill100 / fillwide100 / late6) was still on the
cards.  Companion to `Plan.md`, which holds the campaign record; this file holds
the design for the production data that goes into the article.*

Everything here is a **proposal** — no run in this file starts until it is
approved and launched by hand, one at a time, through `run_single.sh`.

---

## 1. What the paper already has

Three results are in hand and validated; the production runs exist to make them
publication-grade, not to discover them.

| Result | Status | Where recorded |
|---|---|---|
| **Like-oriented throats repel** — 5× gravity at a=2, m=1, and the push scales with throat *width*, not mass; pull/push ratio 1.50 measured vs 6/4 predicted | Measured on three control arms, 2026-08-31 | params header of the merger IVP; Plan.md Stage 2.6 |
| **Opposite-oriented throats attract and merge** — gravity-driven (drainhole mass in the lapse), collapse at t ≈ 45, common horizon | Both freeze arms completed t = 80 | Plan.md M6/M7, results pack |
| **The interior freeze survives the merger** and the recorded signal is a genuine gravitational wave (speed, 1/R falloff, static-offset, not-freeze-junk checks) | Closed 2026-09-02 | Plan.md, "Is the recorded signal a genuine gravitational wave?" |

The freeze method's own validation (seam-radius twins bitwise-identical outside
r = 6, late-engagement control ≤ 0.003%, constraints flat for 27 time units
post-freeze) is also paper material — it is the method section.

---

## 2. The IVP question: how much orbit do we want?

**Where we are.**  The current IVP is d = 12, tangential momenta ±0.12,
opposite orientation.  A Newtonian estimate with the measured 6× coupling says
a *circular* orbit at d = 12 needs p ≈ 0.5 per body (and the period would be
~75 time units).  At p = 0.12 we are at 24% of circular — which is why the
trajectory is a bent plunge, not a spiral.

**The tension.**  More tangential momentum buys a visually and physically
richer inspiral (an l=2, m=2 chirp instead of a near-head-on burst), but past
some threshold the pair does not merge — the observed behaviour is expansion.
The Newtonian escape speed at d = 12 is ~0.7, so somewhere in p ≈ 0.45–0.7 the
capture boundary should sit; below it, eccentric capture with one or two
decaying orbits, then plunge.

**Is the low-p data bad for the paper?**  No — it is the clean baseline: the
first controlled wormhole–anti-wormhole merger does not need an inspiral to be
a result.  But an eccentric-capture arm alongside it is much stronger, and the
capture boundary itself (merge vs escape as a function of p) is a figure no
one has published.  The scan *is* paper content, not just tuning.

**Revised 2026-09-02 — the archive already held the key data point.**  A
p = 0.45 arm ran on 2026-08-31 (`merge_orbit_flip_d12_p045`): separation fell
12 → 3.95 by t = 40, swung back out to 4.61 by t = 60 — and the run *stopped
there*, mid-orbit, on the outbound leg.  Since 0.45 is 90% of circular
momentum for the 6× pull, that is a bound eccentric orbit cut off after one
periapsis, not an observed escape.  The run wrote no checkpoints
(checkpoint_interval = -1), so it cannot be continued — the decisive part,
t > 60, has to be re-simulated from t = 0.

**The ladder as launched** — max_level 3, the campaign's own proven
orbit-phase configuration (levels 4–5 were always added on restart near
collapse; scouts classify trajectories, so no extra refinement):

| Scout | p | Status / expectation |
|---|---|---|
| S1 | 0.12 | plunge, merges at 44.9 — in hand, re-used |
| S2 | 0.25 | queued for the next free card — bent plunge, maybe a half orbit |
| S3 | 0.35 | queued — eccentric-capture candidate |
| S4 | 0.45 | **LAUNCHED 2026-09-02** (t = 0 → 200) — does the swing-out return and merge? |
| S5 | 0.55 | optional, above circular (0.50) — only if the boundary needs bracketing from above |

All scouts: L = 64, **N = 64 (dx = 1)**, max_level 3, stop_time 200,
checkpoints every 20 time units with `checkpoint_keep = 3` — pruned to the
last three, and any arm extends by restart (the p045 lesson).  Measured
speed at launch ~96 u/h → **~2 h worst case** per scout; a merger ends the
run sooner.  Templates live in `runs/wormhole_merger/templates_scan/`; each launch
is one by-hand invocation of `launch_capture_scan.sh <p> <gpu>`.

Caveat: higher p delays collapse by roughly the orbital time — expect
t_collapse ≈ 120–170 for the spiral arm, not 45.  Production stop_time must be
set per-IVP as **t_collapse (from the scout) + 100**.

**Repulsion side-figure (cheap).**  One or two extra throat-width points
(a = 1.5, a = 3 at rest, level 3–4, t ≈ 20, measure the initial acceleration)
turn the three existing control arms into a power-law figure for the
width-scaling claim.  Hours, not days.

---

## 3. Grid design for correct GW extraction

**Current geometry, for the record.**  L = 64 (domain 64³, centre at 32),
**N = 128** base cells — so base dx = 0.5, and max_level 5 puts finest
dx = 1/64 on the throats.  (The plots that "only show 32" are zoomed: the
slice cache stores the central 32-wide window, r ≤ 16 from centre, to keep the
cache small.  The domain is genuinely 64.)

**What is wrong with it for a paper waveform:**
1. The outer detector R = 30 sits *inside* the sponge (24 → 32), soaking ~13×
   base dissipation (Plan.md issue 15).  Amplitude there is timing-grade only.
2. Two radii is not enough for an R → ∞ extrapolation; standard practice is
   4–6.
3. Waveform sampling is 0.5 time units (plot_interval 50) — coarse enough that
   a careless fit aliased (the QNM comb incident).

**Proposal: L = 128, N = 256 — same dx, twice the room.**

- Base dx stays 0.5.  This matters: initial-data noise scales as 1/dx², so
  *refining* would handicap t = 0 constraints, while *widening* at fixed dx
  costs nothing at t = 0.  N = 256 is not "more resolution", it is the same
  resolution with the boundary pushed out.
- Sponge moves to 48 → 64 (radius from centre).  Extraction spheres at
  **R = 20, 28, 36, 44** — four radii, all in clean, un-sponged vacuum, wave
  zone resolved with ~30 base points per dominant wavelength (~15 units).
- Extraction radii are a *consumer-side* (post-processing) choice, so four
  radii cost the run nothing; halve plot_interval to 25 for 0.25-unit waveform
  sampling (2× plotfiles, rolling retention absorbs it).
- stop_time per §2: baseline arm ~150, spiral arm t_collapse + 100 (~250).
  Long enough for the signal, the second peak, and the tail to clear R = 44.

**Cost of the bigger box (estimated, then smoke-tested).**  The AMR hierarchy
currently carries ~4.1 M cells *per level*; fine levels dominate runtime
(level ℓ substeps 2^ℓ times).  Doubling L only grows level 0 (2.1 → 16.8 M
cells, weight 1 of ~62), so the slowdown should be modest — estimate
**3.5–4.0 u/h at level 5**, i.e. ~10–25% below today's 4.3.  Memory is the
real risk: current arms sit at 48–52 GB of 80; +14.7 M base cells adds an
estimated ~25 GB → ~75 GB, tight.  **A t = 5 smoke run measures both numbers
before anything is committed.**  (2026-09-02: if one card is tight, the
declared fallback is MPI multi-rank across cards — the known AMR crash is
specific to the radial regrid recipe, and the merger tags with type 2 — so
memory alone does not force L = 96.)  Fallback if it doesn't fit: L = 96 / N = 192
(sponge 40 → 48, radii 20/26/32/38) — still fixes issues 1–2.

---

## 4. Max level: 5 for production, 6 as the convergence companion, 7 never by default

The question "start at max level 7, run till collapse, then freeze?" has a
measured answer — the m4e ladder:

| max_level | speed (u/h, one card) | what the ladder showed |
|---|---|---|
| 4 | 9.0 | scout grade |
| 5 | 4.3 | **production** — damping crosses from cure to cost here; the validated freeze config |
| 6 | 2.2 | companion — bought +0.53 where the linear law projected +6; the ladder saturates |
| 7 | 1.1 | t = 250 would take ~9.5 days; single-arm increments at this rung are *inside the noise floor* (three wrong "laws" in one day) |

So: **production arms at max_level 5**, one **level-6 twin** of the headline
arm as the convergence/error-bar companion (that pair is also the paper's
resolution study).  Level 7 only if a referee demands it, and then as a short
restart segment around collapse, never from t = 0 (the 1/dx² initial-noise
penalty plus 4× the cost buys nothing the ladder can detect).

Freeze protocol unchanged from M9b: evolve through collapse, engage
`CoreFreezeFill` ~8 units after collapse (t_collapse + 8), fill radius
1.5 / 2.0 wide arm, with the seam twin and one late-engagement control
re-run once at L = 128 to re-validate the method at the production geometry.

---

## 5. GPU schedule (4 × H100 80 GB, one run per card)

| Phase | Runs | Cards | Wall time |
|---|---|---|---|
| 0 (now) | wave 8 drains (fill100/fillwide100 → t = 100, late6 → 80); then the wave-8 checks: second peak at R = 30 near t ≈ 93, late6 no-shift | 3 | ~4 h |
| 1 | p-scan scouts (lvl 3, N = 64, t = 200): S4 live on card 3; S2/S3 follow as wave 8 drains | 3–4 | ~2 h each |
| 1b | L = 128 smoke test (t = 5: memory + speed); repulsion a-points | any free | hours |
| 2 | production: spiral arm (chosen p, L = 128, lvl 5) + its seam twin; baseline p = 0.12 arm at L = 128; level-6 companion of the spiral arm | 4 | lvl-5 arms ~2.5–3 days; lvl-6 companion ~5–6 days |
| 2b | late-engagement control at L = 128 (restart segment, ~40 units) | 1, after a twin frees | ~12 h |
| 3 | analysis: 4-radius extrapolation, speed check at the new radii, constraints, frames re-rendered with colour limits taken outside r = 3 (Plan.md issue 17), pack + push | — | — |

Calendar total: **~1.5 weeks of compute** if phases overlap sensibly.
Checkpoints prune by hand as always (they are never auto-deleted); heavy data
stays on scratch, run dirs keep params/logs/small_data only.

**Multi-GPU note.**  MPI itself works on this node; the known AMR crash is
specific to the radial regrid recipe, and the merger uses tagging_type 2.  A
cheap 2-rank smoke test on the L = 128 box is worth one slot in phase 1b — if
it holds, the level-6 companion halves to ~3 days.  If it crashes, we lose
nothing: the schedule above assumes single-card throughout.

---

## 6. Decisions needed before phase 1

1. **Approve the scan values** p = 0.25 / 0.35 / 0.45 / 0.55 (S1 = 0.12 is
   re-used).
2. **Headline IVP intent**: is the paper led by the eccentric-capture spiral
   (if one merges) with the p = 0.12 plunge as baseline, or the reverse?
   The schedule is the same either way; the writing is not.
3. **L = 128 vs the L = 96 fallback** — decided by the smoke test, but say now
   if 2.5–3 days per arm is too slow regardless.
4. Whether the repulsion a-scan points are wanted for a power-law panel.

Nothing launches until these are answered; every launch goes through the
launcher, by hand, one approval each.
