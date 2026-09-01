# Merging two regular exotic-matter wormhole throats in 3D Cartesian CCZ4

Working document: the plan, and the log of what was broken and what fixed it. Started
2026-08-28. Literature review: [background.md](background.md). Prior art, initial-data
gates and the file-by-file design: [Reference.md](Reference.md).

---

Every run cited below lives under `runs/wormhole_merger/`, which is **not in git** —
it is the working tree on the machine that produced it, grouped by campaign stage
with a `NOTES.md` per stage and a `README.md` explaining each run. What is in git is
the light extract: [`results/merger/`](../../results/merger/README.md).

## The plan

### Stage 0 — put a real throat on the grid — **done 2026-08-28**

- [x] **0.1** Derive the massive Ellis–Bronnikov drainhole in the isotropic chart the code
  already uses; check it solves the constraints exactly
- [x] **0.2** Standalone check, no GPU: interior minimum of R exists, χ at the throat,
  proper cell width, the m/a ceiling, free-fall time
- [x] **0.3** Implement as a **default-off** initial-data mode
  ([BinaryWormholeInitialData.hpp](../../Examples/BinaryWormholeMerger/BinaryWormholeInitialData.hpp));
  no archived run may change
- [x] **0.4** Parameters + sanity net in
  [SimulationParameters.hpp](../../Examples/BinaryWormholeMerger/SimulationParameters.hpp)
- [x] **0.5** Build clean (CPU, then CUDA)
- [x] **0.6** Verify at t = 0 that χ_throat is O(1) and R_min holds at `max_level` 0, 1
  **and** 2 — the refinement test the puncture failed

### Stage 1 — one throat holds still — **exit condition met 2026-08-30**

- [x] **1.1** Params file: one throat, α = e^u exactly, 1+log, Gamma-driver from β = 0,
  `covariantZ4 = 0`, Sommerfeld out —
  [params_stage1_hold.txt](../../Examples/BinaryWormholeMerger/params_stage1_hold.txt)
- [x] **1.2** Run to t ≳ 20–30 M; measure R_min drift and constraint norms — five arms
- [x] **1.3** Decide the collar's fate — **keep it**, and know what it costs
- [x] **1.4** Mesh or wormhole? Two unigrid arms at dx = 0.50 and 0.25
- [x] **1.5** Stop the mesh chasing the error: add `FixedGridsTagger` as a default-off
  tagger choice
- [x] **1.6** Settle the wall at t ≈ 24 — bug or result. One extra refinement level

### Stage 2 — two throats

- [x] **2.0** Throat locator + moving boxes + wave-zone shells — implemented 2026-08-31;
  shakedown (boosted single throat) **passed to t = 40**, zero lost rows, no NaN
- [ ] **2.1** Superposed two-throat data with the Helfer/Ning companion correction, d = 16
- [ ] **2.2** CTTK solve in GRTresna; watch for K² < 0
- [ ] **2.3** Re-measure the growth rate on two-throat data — do not assume Stage 1 carries
- [x] **2.5** Two throats in orbit, gravity-driven, d = 12 — **answered** 2026-08-31:
  they REPEL. The phantom support field out-pushes gravity (a²+m²)/m² = 5× at any
  parameters; like-charge throats never merge (§8)
- [x] **2.6** Repulsion controls A/B (from rest, a = 2 and a = 1) + arm C
  wormhole–anti-wormhole (`wormhole_phi_sign_B = -1`) — **all three passed** 2026-08-31.
  A separates from rest, B's push falls 3.0× at half width, C falls together; the
  C/A ratio is 1.511 ± 0.033 against a predicted 1.500 (§8)
- [x] **2.7** The merger run `merge_orbit_flip_d12`: the baseline orbit with the sign
  flipped, one line different — **merged** 2026-08-31: common trapped surface from
  t = 29.9, single whirling core, endpoint is a black hole (§9)

### Stage 3 — the merger

- [ ] **3.1** Head-on from rest, gravity-driven, no aimed momenta — probe
  `merge_headon_flip_d12` died t = 44, the same core NaN (`h11`, level 3), exactly as
  predicted for its damping-free binary; no checkpoints, so the rerun (once the damping
  recipe settles) is from scratch
- [x] **3.2** Ψ₄ at several radii + the v ≈ c propagation test — **passed** 2026-08-31:
  the R = 30 mode series lags R = 14 by exactly Δr = 16, so the quadrupole burst
  (m = 2 amplitude 2.5e-2 peaking t = 37.5) is real outgoing radiation, not a
  constraint mode. The second, larger swell was truncated by the t = 52 NaN — the
  restarted run records it whole
- [x] **3.3** Convergence and error budget — **n160 done 2026-09-01, and it settles
  the resolution question (§11)**: N = 160 undamped died at t = 53.61 against the
  coarse arm's 52.06, while the inspiral (≤ 1.8 %, two trackers), the common trapped
  region (0.19 units, 1 % in radius) and the Ψ₄ amplitude (0.2–4 %, two radii) all
  converged. Refining postpones the death by 3 % and removes nothing; reaching t = 60
  this way would cost ~90×. **p045 momentum variation COMPLETED t = 60 with zero
  NaN, 2026-08-31 — because it never merges**: it is a periapsis passage. Validated
  against the tracker: separation 11.9 → minimum 3.95 at t = 40 (closest approach)
  → receding to 4.6 by t = 60, with the movie showing the same turn-and-expand.
  Zero NaN over the full span is the clean control: the death is tied to merger +
  core collapse, not to long evolution itself. (Its theta scan reports a
  brief common-trapped flicker at r ≈ 5.1, t ≈ 52 — a sphere grazing both throats,
  the §-documented artefact regime; treat as unverified, the offline finder cannot
  check it since p045 predates the h_ij/A_ij plot list)
- [x] **3.0** Checkpointing switched on and the restart path verified — 2026-08-31, below
- [ ] **3.4** Survive the collapsed core: matter damping inside the horizon (§9) —
  three arms dead (lapse window t = 52.86, dissipation t = 51.68, radius window
  t = 55.00), each cure reaching more matter and buying more time; now entangled
  with the §10 discovery — the horizon the damping hides inside is itself dissolving,
  so no fixed window can stay causally sealed. Strategy decision pending
- [x] **3.5** Offline Θ = 0 horizon finder — **built and validated 2026-08-31**
  (`grteclyn-wrapper/scripts/validation/ah_radial_scan.py`): full-metric radial Θ scan,
  shell-max statistic matches the in-code proxy (1.07 offline vs ≈ 1.0 in-code at
  t = 51.5). Limitation: runs launched before 2026-08-31 did not plot h_ij/A_ij, so
  r03000 and headon snapshots cannot be measured — the truly undamped control is
  unmeasurable, permanently

### Stage 4 — write

- [ ] **4.1** If 1–3 hold: two-throat head-on with Ψ₄
- [ ] **4.2** If 2 or 3 stalls: methods Letter on the regular two-throat data, or the
  exotic-lump head-on

### Open, not blocking

- [ ] Domain control (L = 96 or 128 at the same dx) — rules out the outer boundary and the
  sponge, which mesh-independence alone does not
- [ ] Does the surviving growing mode saturate? No run has gone past 40 M
- [ ] Print the NaN's position before the next arm that dies — the abort gives
  `level=… name=h11` and no coordinates
- [ ] Fix the phantom potential-sign inconsistency **before** any `phantom_mass ≠ 0` work

---

## What happened to each run — in plain words

| Run | What happened |
| --- | --- |
| **r03000** (main arm, no damping) | Throats merge, common horizon at t ≈ 30, radiation burst confirmed real — then the phantom core kills it: NaN at t = 52.07 |
| **r05000** (narrow lapse window) | Damping aimed too deep (covered ~3 cells) — died t = 52.09, no gain. Its streams were deleted before extraction; only the log survives |
| **r04000** (wide lapse window) | Cleaned the core to \|φ\| ~ 1e-10, but the sick cells re-inflate their own lapse and escape the window — died t = 52.86 |
| **sg10** (dissipation σ = 1.0) | Backfired — dissipation attacks the puncture structure itself, died *earlier*, t = 51.68; scratch deleted |
| **rw** (radius window) | Longest survivor, t = 55.00 — and its snapshots caught the discovery: the horizon shrinking 1.07 → 0.59, dissolving under phantom accretion (§10) |
| **headon** probe | Died t = 44 at its own core collapse (old binary, no damping) — awaits rerun once the recipe settles |
| **p045** probe | **Completed t = 60, zero NaN** — never merges: periapsis at t = 40 (separation 3.95), then the throats fly apart again |
| **n160** probe (25 % finer grid) | Died t = 53.61, same NaN — but everything before the collapse converged with the coarse run. Refining buys 1.55 units and removes nothing (§11) |
| **ml2** probe | `max_level = 2`: NaN at t = 9.42, long before the throats meet — three refinement levels is the floor for the binary too |

The packed, git-committed extract of all nine — streams, waveforms, movies, stills,
the horizon scan and generated summary tables — is [`results/merger/`](../../results/merger/),
rebuilt by `research/merger/pack_results.sh`.

The one-paragraph story: when the throats *do* merge (all the orbit-flip arms), a
horizon forms at t ≈ 30 and the phantom scalar then destroys everything — first
the runs (the NaN wherever un-damped phantom sits on collapsed geometry), and, as
the rw measurement shows, the horizon itself, which the infalling phantom eats
toward dissolution around t ≈ 56. When the throats *don't* merge (p045, enough
angular momentum), nothing collapses and the evolution is indefinitely healthy.
The black hole, not the wormhole pair, is the fragile object in this system.

## Status at a glance

| | |
| --- | --- |
| the throat is regular | χ = 0.17 at the minimal surface, against the puncture's ~0.006 |
| the ADM mass goes in the lapse | `wormhole_id_type = 1`; the puncture route destroys the throat it is meant to weigh |
| one throat survives 40 M | −0.36 % on the throat radius, no NaN |
| the mesh is not the killer | fixed boxes hold 13.32 GB flat; moving the refinement boundary moves the death by 0.03 |
| the compactified origin is not the killer | refining it made every error smaller and pushed the wall past 40 M |
| **something real is still growing** | the momentum constraint rises exponentially and is still rising at t = 40 |
| two moving throats are now trackable | locator + moving boxes shipped 2026-08-31 |
| a *moving* throat also survives 40 M | boosted arm crossed 3.3 units of grid, zero lost rows, no NaN |
| that growth may have a ceiling | on the boosted arm L2 Mom flattens after t ≈ 30 (+8 % over the last 10 units, against doubling every ~12 before) — one arm, not yet a result |
| the compactified origin fills in | χ at the pit rises ×400 and the origin lapse falls 0.22 → 0.13 over 40 M; slow, never fatal |
| **the throats repel, and must** | phantom support field carries scalar charge set by throat *width*; push/pull = 1 + a²/m² > 1 always — like-charge pairs are unbound at any parameters (§8) |
| **the merger route is proven** | flipping one throat's field turns the 5× push into a 5× pull: measured C/A ratio 1.511 ± 0.033 vs 1.500 predicted, over 15 matched times (§8) |
| the scalar force scales with *width*, not mass | halving the throat radius cut the push 3.0×; a mass-tracking force would not have moved at all (§8) |
| the flip costs no stability | φ → −φ leaves geometry, ADM mass, supporting energy and the growth mode identical; only the pair interaction sees it (§8) |
| **the horizon is dissolving** | fully-trapped sphere 1.07 → 0.59 over t = 51.5–55.0, accelerating; phantom accretion, two damping arms agree (§10) |
| the offline Θ finder is live | full-metric radial scan, validated 1.07 vs ≈ 1.0 against the in-code proxy at t = 51.5 (§10) |
| p045 never merges | orbit holds at p = 0.45, throats end 4.6 apart, zero NaN to t = 60 — the death is merger + collapse, not evolution length |
| **the horizon fused at t ≈ 30** | shell-max θ₊ ≤ 0 on spheres enclosing both throats from t = 29.93 to 32.74, deepest −0.033; the visual "contact" at t ≈ 45 was interior coordinate motion (§9) |
| **the merger itself is converged** | 25 % finer grid: inspiral within 1.8 % on two trackers, horizon 0.19 units earlier and 1 % in radius, Ψ₄ within 0.2–4 % at two radii (§11) |
| **resolution is not the cure** | 1.25× finer buys 1.55 code units of survival; reaching t = 60 undamped would need ~400 cells per side, ~90× the cost (§11) |
| **the radiation is real** | Ψ₄ at R = 30 is a time-shifted copy of R = 14 with lag Δt = Δr = 16 — outgoing at v ≈ c |
| the collapsed core outlives the vacuum trick | NaN at t = 52.07 with the scalar still at 84 % on the frozen core; the puncture floors protect geometry, not matter (§9) |
| the matter cure must reach the matter | first damping window (lapse < 1e-6) covered ~3 cells and moved the death 0.02; the scalar bulk sits at lapse 1e-6..3e-2, inside the horizon — window retuned, revalidation in flight (§9) |

**What 40 M is:** a fuse length, not stability. The run ends while the growth is
accelerating. Stage 3 can be budgeted against 40 M; it cannot be budgeted against an
unbounded window.

---

## What was broken, and what fixed it

### 1. The throat was not on the grid at all

**Broken.** The ADM mass was earned with a Brill–Lindquist puncture, `ψ += m/(2r̄)`, which
drives χ → 0 **at the throat itself**. Refining then *erased* the throat rather than
sharpening it. One cell at the minimal surface was 6.2 units of proper width — wider than
the throat it was meant to resolve.

**Fixed.** The massive Ellis–Bronnikov drainhole earns the same ADM mass from the **lapse**
and leaves the spatial conformal factor bounded. ~15 lines of initial data, no new chart.
With `X = (r̄ − a²/4r̄)/a` and `Ω = 1 + a²/(4r̄²)`:

| | |
| --- | --- |
| lapse exponent | `u = (m/a)(arctan X − π/2)` → 0 at infinity |
| lapse | `α = e^u` — part of the solution, not a gauge choice |
| conformal factor | `χ = e^{2u} / Ω²` |
| scalar | `φ = √(a²+m²)/(a√(4π)) · arctan X` |
| | `K = 0`, `A_ij = 0`, `Π = 0`, `M_ADM = m` |

The amplitude is fixed by the field equations (`4π C² = a² + m²`), not chosen, which is
what makes both constraints hold identically at t = 0. Verified to roundoff by
[drainhole_throat_check.py](../../grteclyn-wrapper/scripts/validation/drainhole_throat_check.py).

**Measured, 0.6** — a = 2, m = 1, L = 64, N = 128. Analytic: r̄ = 1.6180, R_min = 3.8895,
χ_throat = 0.1731.

| `max_level` | dx at the throat | puncture | drainhole | error |
| --- | --- | --- | --- | --- |
| 0 | 0.5 | present | R = 3.908 | 0.48 % |
| 1 | 0.25 | **gone** | R = 3.890 | **0.01 %** |
| 2 | 0.125 | **gone** | R = 3.892 | 0.06 % |

| at `max_level` 2 | throat areal radius | proper width of one cell there |
| --- | --- | --- |
| Brill–Lindquist puncture | 4.5 | **6.2 — wider than the throat** |
| massive drainhole | 3.89 | **0.31** |

A factor ~20 in proper resolution at the throat, bought with no extra grid.

**Three derived properties, two of them against the obvious guess:**

- the minimal surface is at `l = m`, i.e. `r̄ = (m + √(m²+a²))/2` — *not* at `l = 0`;
- `R_min = e^{−u(m)}√(m²+a²)`;
- **χ at the throat barely moves with mass** (0.25 at m/a = 0, 0.15 at 1.0): the throat
  migrates outward as m grows and the larger Ω⁻² almost cancels the smaller e^{2u}. Proper
  cell width there is 2.0–2.6 dx whatever the mass. **Mass no longer costs resolution.**

**New design constraint, not in the report:** `m/a` is capped near 1 — past that χ_throat
falls back toward puncture values. A heavier binary wants a *bigger* throat, not a heavier
one, and a bigger throat means a longer free-fall time (t_ff ∝ a at fixed m/a).

**Why the report's own fix was not taken.** It said to swap in the proper-radial (Ellis)
chart, whose slice has topology `R × S²` and — as the report itself says — cannot be
embedded in one Cartesian box. The two are related by `l = r̄ − a²/(4r̄)`; the isotropic form
is equally regular at the throat and only *also* compactifies the far universe to r̄ → 0,
unavoidable in a single box. **The chart was never the bug.**

### 2. Dissipation was destroying the throat while every monitor read clean

**Broken.** The inherited default `sigma = 2.0` shrinks the throat by **34 % over 40 M
while every constraint norm sits flat at 1.3e-3.** Smoothing *lowers* the violation it
causes, so the error monitors are structurally unable to see this failure. The overshoot on
the way (R = 4.40 at t = 20, above the initial 3.89) settles the direction — no collapsing
object grows first.

**Fixed.** `sigma = 0.1` in the three drainhole templates, 2026-08-30 — not 0, because a
little dissipation still buys stability at the refinement boundaries for ~0.1 % on R_min.
Puncture-era templates stay at 2.0: silently retuning runs the measurement does not cover
would be worse.

**The five arms** (a = 2, m = 1, `max_level = 2`; exact answer R_min = 3.8895):

| σ | collar | R_min reached | Hamiltonian L2 | ends |
| --- | --- | --- | --- | --- |
| 2.0 | no | **2.578** at t = 40 | 1.3e-3, flat throughout | ran to completion |
| 2.0 | yes | — | — | NaN at 21.7 |
| 0.1 | no | 3.894 — 0.1 % | 2.5e-3 flat, then spikes | NaN at 24.2 |
| 0.1 | yes | 3.127 — 20 % low | 3.7e+12 | NaN at 31.4 |
| 0.0 | no | 3.87–3.95, oscillating | 2e-3 → 1.2e-1, doubling ~5 M | **out of memory** at 35.2 |

The σ = 0 arm is the only one whose norm grows visibly — that growth is the run telling the
truth about an instability σ = 2.0 suppressed into silence.

### 3. The collar: predicted useless, measured load-bearing

**Broken prediction.** The plan said the origin-isolating collar (lapse type 6) was a
needless perturbation once χ was O(1) at the throat. Wrong.

**What the origin monitor shows.** `chiA_min` is the *origin* health monitor, not a throat
tracker, and it is the controlling variable in every arm:

| arm | dx at the origin | χ there at t = 0 | reaches the 1e-8 floor |
| --- | --- | --- | --- |
| unigrid, no collar | 0.5 | 2.44e-3 | **t = 6.6** |
| unigrid, no collar | 0.25 | 1.33e-4 | **t = 1.2** |
| `max_level` 2, no collar, σ = 0.1 | 0.125 | 7.19e-6 | t = 9.0 |
| `max_level` 2, **collar**, σ = 0.1 | 0.125 | 7.19e-6 | **t = 31.4** |
| `max_level` 2, no collar, σ = 0 | 0.125 | 7.19e-6 | **never** |

Collar buys a factor 3.5 in origin survival and costs 20 % of the throat radius. Collar and
dissipation are **two independent trade-offs, not one bad inherited setting**.

**Confirmed at t = 26, after an interim reading doubted it.** At t = 13 the collar arm
looked worst of three; it then outlived both (26.2 against 23.5 and 24.2) and failed the way
1.3 predicted — through the *throat* (−7.3 %, monotone), not the origin. Also corrected: its
lapse sitting at the 1e-10 floor at the origin is **not** a failure — it starts at 2.6e-7 by
construction, since freezing the far universe is what the collar is *for*. The pathological
arm is the collar-free one, whose lapse began at 0.23 and collapsed over t = 18–22.

### 4. The mesh chased its own noise until the card ran out

**Broken.** `ChiTagger` refines on χ gradients. With no dissipation the junk grows and
spreads, and the mesh follows it everywhere: level 2 ended at 1000 grids, 32.8M cells, 24 %
of the domain, 3.9 → 30.6 GB. That is what ended the σ = 0 arm at t = 35.2 — **memory, not
instability**, with the throat still at 3.87–3.95.

**Fixed.** `FixedGridsTagger` (already in `Source/Tagging/`, used unmodified) offered as a
default-off tagger choice. The footprint becomes a property of the *parameters* rather than
of the *error*, so the run can no longer die of its own mesh.

| key | default | meaning |
| --- | --- | --- |
| `tagging_type` | `0` | 0 = `ChiTagger`; 1 = fixed boxes; 2 = moving boxes (Stage 2.0) |
| `tagging_L` | `L` | level 0 tags \|x − centre\|_∞ < `tagging_L`/4, each finer level halves it |
| `tagging_center` | `center` | where the boxes sit |

`pre_tag_cells()` skips the χ ghost-fill under the geometric taggers — it only fed
`ChiTagger`'s second derivatives. `regrid_threshold` then does nothing, and the parameter
reader warns, because a knob that silently does nothing is how someone concludes the tagger
did not help.

**Result, 2026-08-30: the memory failure mode is gone permanently, and the physics is
unchanged.** Levels 1 and 2 froze at 4 096 000 cells each for the whole run, against level 2
climbing to 32.8M under χ tagging; all three arms held 13.32 GB from first step to last. All
three still died, between t = 23.5 and 26.2, every one in `h11` on level 2.

| arm | σ | collar | NaN at | throat at death | how it got there |
| --- | --- | --- | --- | --- | --- |
| `s15_lapse5_sg00_fg` | 0 | no | **23.54** | +0.06 % until the last unit | Mom doubling every ~0.5 from t = 13; origin lapse 0.20 → floor over 18–22 |
| `s15_lapse6_sg00_fg` | 0 | yes | **26.23** | **−7.3 %, monotone** | constraints jump at 17–20, sit at 2–3e-1; throat shrinks throughout |
| `s15_lapse5_sg01_fg` | 0.1 | no | **24.17** | +0.04 % | **constraints flat at 3e-3 to the last step**; sudden and local |

**The tagger is necessary and not sufficient.** Two clean A/Bs against χ tagging:

| σ | collar | χ tagging | fixed boxes | verdict |
| --- | --- | --- | --- | --- |
| 0.1 | no | NaN at **24.2** | NaN at **24.17** | tagger irrelevant — 0.03 apart |
| 0 | no | t = **35.2**, OOM, no NaN | NaN at **23.54** | tagger costs **12 units** |

The σ = 0.1 pair is the sharp one: two runs with the level-2 boundary in completely
different places died at the same instant, in the same variable, throat 0.04 % from its
start. **Whatever kills them is mesh-independent.** The σ = 0 pair explains the rest — with
no dissipation the only thing suppressing the junk *was* the runaway refinement, so removing
it lets Mom run away from t = 13, far too fast for the physical mode. **The junk must be
damped or resolved; χ tagging silently supplied the second at a price it could not afford.**

### 5. The refinement boundary was innocent — and so was the origin

**Suspected.** Both σ = 0.1 arms died on level 2, which reads like a refinement-boundary
failure.

**Measured (1.4).** Two `max_level = 0` arms, no refinement boundary anywhere:

| grid | NaN in | dies |
| --- | --- | --- |
| uniform dx = 0.50 | `K`, level 0 | t = 6.6 |
| uniform dx = 0.25 | `h11`, level 0 | t = 1.2 |

Removing refinement makes it **four times worse**; refining uniformly makes it **twenty
times worse**. Refinement is the protector. The mechanism is in the χ column above: χ
vanishes like r̄⁴ at the compactified far infinity, so halving dx puts the innermost cell
twice as close and drops χ there by 2⁴ (measured ratios 18.4 and 18.5) — and CCZ4 divides by
χ. A uniform grid cannot be refined at the origin without refining it everywhere. Reaching
the floor is a precursor, not the death: the no-collar σ = 0.1 arm floored at t = 9.0 and
ran to 24.2.

**Then the wall at t ≈ 24: bug or result.** Two explanations survived, and they predict
**opposite signs** under one extra refinement level:

| | adding a level predicts | the case for | the case against |
| --- | --- | --- | --- |
| **A — the under-resolved compactified origin** | the wall moves **earlier** | three unrelated levers all buy time and all target that region — dissipation damps it, the collar freezes it, runaway refinement resolves it | the collar arm froze the origin completely and **still died**, at 26.2, through the throat |
| **B — the real Ellis–Bronnikov growing mode** | the wall moves **later**, by ~4·ln(seed ratio) | one growing mode with timescale ~ throat/c ~ 4, so reaching O(1) from the 2e-3 floor takes ≈ 4·ln(500) ≈ 25 — it lands on the wall; and the two σ = 0.1 arms died 0.03 apart with the mesh rearranged | an order-of-magnitude argument: a factor 10 in the seed moves the prediction by 9 units |

**The answer, 2026-08-30** — `s16ml3_lapse5_sg01_fg`, the σ = 0.1 no-collar fixed-box arm
with `max_level = 3` and *nothing else changed*. Level 3 has dx = 0.0625 and covers
|x − c|_∞ < 4, holding both the throat and the compactified origin. 16.5 GB flat, 18.2 code
units/h, 2.2 h wall.

| | `max_level = 2` | `max_level = 3` |
| --- | --- | --- |
| outcome | NaN at 24.17 | **t = 40, clean** |
| R_min at t = 0 | 3.891721 (0.057 % high) | 3.889973 (**0.012 %**) |
| R_min drift at t = 12 | +0.035 % | +0.0005 % |
| L2 Ham at t = 12 | 2.48e-3 | 2.51e-3 |
| L2 Mom at t = 12 | 6.80e-5 | **7.51e-7** |
| χ at the origin | 7.19e-6, floors from t = 9 | 4.11e-7 → 9.95e-6, **rising all run** |
| α at the origin | 0.2315 → 0.2404 | 0.2194 → 0.1322 |

**The wall moved later, which excludes A.** Refining the origin was supposed to poison it —
and χ there did drop exactly as predicted (7.19e-6 → 4.11e-7) while every column got
*better*. The origin is not what was killing these runs.

**What is left is a real growing mode, still growing at the finish.** L2 Mom: 7.5e-7
(t = 12) → 5.1e-6 (17.6) → 1.4e-5 (26) → 3.3e-6 (34) → 3.9e-5 (40). The early e-folding time
is 4.4 against a predicted throat/c ≈ 4 — the one number Explanation B put on the table in
advance. It then dips near t = 34 and returns steeper, doubling every ~1.6, which no single
exponential explains and which no run has been taken far enough to resolve.

The frames say it in another currency: on a log scale (`frames_logscale.py --ring 1.618`)
K at t = 1 is a **square** blob with corners on the grid axes — the cubic mesh's own
signature on a solution that should have K = 0 — and by t = 39.5 it is round, single-signed,
monotone inward and thirty times larger. Grid junk does not become spherically symmetric.

**So Stage 1's benchmark is met in the terms it was written in** — "R_min drift attributable
to the known EB unstable mode rather than to the grid": −0.36 % over 40 M, mode identified,
rate measured.

**Retracted along the way, because both would mislead a reader of the raw tables:** *"B
predicts the wall does not move"* — wrong, a growing mode starts from the discretisation
error and refinement lowers it, so B predicts a **later** wall (seed ratio 90 at t = 12 →
~18 units of delay → wall near 42), and reaching 40 cleanly is a **B outcome**, not evidence
against it. And *"do not run a deep fixed box on the origin"* — written from 1.4, which
halved dx *everywhere*, then wrongly read across to a nested level, where it was the cure.

**What refinement can still buy.** Each level halves dx, so χ at the innermost cell falls
16×: 4.11e-7 at level 3, ~2.6e-8 at 4, ~1.6e-9 at 5. With `min_chi = 1e-8` **level 5 starts
below the floor** and level 4 sits 2.6× above it, at roughly double the wall clock — level 4
is reachable, 5 is not. The fix is the *criterion*: the shell tagger built in 6.

### 6. The fixed box cannot survive two throats

**Broken by construction.** The throats *move*, one box cannot straddle both, and a merger
has to resolve a wave zone a single central box does not cover.

**The tempting wrong answer:** build a smarter criterion that tells junk from real structure.
Of the four taggers in `Source/Tagging/`, exactly one reads the solution — and that is the
field's answer, not an oversight:

| tagger | criterion | reads state? |
| --- | --- | --- |
| `ChiTagger` | \|∂²χ\| above a threshold | **yes** |
| `PunctureTagger` | distance to each tracked centre | no |
| `ExtractionTagger` | distance to each extraction radius, enforces a required level | no |
| `FixedGridsTagger` | distance to a fixed centre | no |

Production black-hole codes refine on **geometry decided before the run starts**. Junk never
gets a vote because the solution never gets one. Underneath: **refining junk feeds junk** —
a finer grid resolves more of the noise spectrum, which pulls in more grid. That loop ended
the σ = 0 arm at 35.2, and no threshold makes a runaway safe; it only sets the fuse length.
Damp the junk; send refinement where it was told to go. (Berger–Oliger truncation-error
tagging fails the same way, harder: junk has enormous truncation error by construction.)

**Fixed, 2026-08-31.** Three pieces, all in the example, none touching shared code:

| piece | where | what it does |
| --- | --- | --- |
| throat locator | [ThroatTracker.hpp](../../Examples/BinaryWormholeMerger/ThroatTracker.hpp) | finds each throat every coarse step, writes `throat_track.dat`; default off (`throat_tracking`) |
| moving boxes | `tagging_type = 2` | the fixed tagger's box arithmetic, centred on the tracked positions |
| wave-zone shells | same branch | the stock `ExtractionTagger`, composed in; a no-op while extraction is off |

**The locator is simpler than planned, and the reason is a wormhole-specific gift.** The plan
said "interior minimum of the areal radius, or the peak of the phantom field" — a 3D
minimal-surface search. Neither is needed for the *boxes*: the tagger wants the throat's
**centre**, and in this chart every throat carries its own compactified far universe exactly
there, where χ falls like r̄⁴ to orders of magnitude below anything else in the field. So the
centre is the χ pit inside a search sphere around the last known position — a min-reduce plus
a centroid over near-minimum cells, which also handles a floor-clipped plateau. **The feature
that makes the origin numerically fragile makes it an unmissable beacon.** The minimal
surface stays a diagnostic, extracted post-hoc. `PunctureTracker` stays off: it advects a
particle backwards along the shift to find a coordinate singularity these data do not have.

### 7. In flight: does a *moving* throat survive?

Every piece of Stage 1's evidence was collected with the throat pinned to the grid centre by
construction. A merger needs it to survive **crossing the grid**.

`s20_boost_p02`, launched 2026-08-31: the Stage 1 baseline (a = 2, m = 1, σ = 0.1, lapse 5,
`max_level = 3`, `tagging_L = 64`) plus one addition — a Bowen–York momentum P = 0.2 along z
([params_stage2_boosted.txt](../../Examples/BinaryWormholeMerger/params_stage2_boosted.txt)).
0.2 is the per-throat Newtonian speed of an equal-mass pair at d = 16, i.e. a genuine
late-inspiral speed. Two questions, in order:

1. **Infrastructure** — do the moving boxes hold the throat as it crosses cells, refinement
   boundaries and box edges? `throat_track.dat` must show `nA > 0` throughout; a zero means
   the boxes lost it — the failure this run exists to catch, visible rather than silent.
2. **Physics** — the boost makes the data inexact, so the mode starts from a larger seed. At
   t = 0, L2 Mom = 4.5e-6 (the discretisation residual of the analytically divergence-free
   Bowen–York term) against the resting arm's **exact zero**, L2 Ham unchanged at 2.10e-3.
   The existing error is ~100× what the boost adds, so the wall may land near 40.

**Answered: it does. Ran to t = 40, 2026-08-31.** No NaN, no abort, and `nA = 4` on every
one of the 4001 rows — the boxes never lost the throat across cells, refinement boundaries
or box edges. The infrastructure question is closed.

| | t = 0 | t = 20 | t = 40 |
| --- | --- | --- | --- |
| L2 Ham | 2.10e-3 | 2.34e-3 | **1.20e-3** |
| L2 Mom | 4.53e-6 | 9.55e-5 | 2.03e-4 |
| origin lapse | 0.219 | 0.197 | 0.130 |
| χ at the pit | 4.1e-7 | 8.3e-6 | 1.6e-4 |
| tracked z | 0 | 1.59 | 3.28 |

Three things in that table are worth more than the pass mark:

1. **The Hamiltonian constraint fell by 43 %.** Every resting arm grew it. Motion is not
   what feeds the mode.
2. **The momentum constraint looks like it saturates.** It doubles every ~7 units to
   t = 20, then adds only 8 % between 30 and 40. That is the first evidence bearing on the
   open question "does the growing mode have a ceiling?" — one arm, so it is a lead, not a
   finding, but it is the first run to even look like a ceiling.
3. **The compactified origin is filling in** — χ at the pit up ×400, origin lapse down to
   0.13. Slow, monotone, never fatal in 40 units, and worth a column in every future run:
   it is the quantity that would eventually end a long merger.

**The coordinate speed under-reads the physical one, badly, and that is now measured.** It
ramps from 0.06 at t = 5 to 0.125 by t = 20, holds to t = 30, then decays to 0.03 — against
a physical speed fixed at 0.2 by construction. So the tracked position lags the object by a
factor that is itself time-dependent: **a coordinate trajectory in this gauge cannot be read
as a velocity measurement.** It can be read for *sign* and for *large* displacements. This
is the single most important calibration for reading §8.

Momentum stays a validation tool. **The merger itself remains gravity-driven** — two throats
released from rest, ADM mass in the lapse, never aimed momenta.

### 8. The throats repel — and reversing one makes them fall

`orbit_d12_p012`, launched 2026-08-31
(run `03_two_throats/orbit_d12_p012`,
[params_orbit_drainhole.txt](../../Examples/BinaryWormholeMerger/params_orbit_drainhole.txt),
entry point [run_spiral.sh](../../grteclyn-wrapper/scripts/campaigns/wormhole_merger/run_spiral.sh)):
two equal drainholes, a = 2, m = 1, at d = 12 on the x-axis, tangential Bowen–York
P = ±0.12 on y — 59 % of the Newtonian circular value 0.204, so the pair is bound and should
plunge rather than circle. `max_level = 3`, L = 64, checkpoints every 20 code units,
`stop_time = 60`.

**The tracker cannot resolve this motion and that is not a bug.** `throat_track.dat` is a
centroid over near-minimum χ cells at dx = 0.0625, so its quantum is ~0.03 — the whole
displacement so far. The numbers below come from the cached χ slices instead
(`frames/_slice_cache/chi_z`, an inverse-χ-weighted centroid of the pit), which is
sub-cell and smooth at the 1e-4 level. **Any future orbit question should be asked of the
slice cache, not of the tracker;** the tracker exists to aim refinement boxes, and 0.03 is
ample for that.

| t | y of throat A | r of throat A | separation |
| --- | --- | --- | --- |
| 0 | 0 | 6.0117 | 12.023 |
| 2 | 0.0037 | 6.0120 | 12.024 |
| 4 | 0.0318 | 6.0201 | 12.040 |
| 7 | 0.0997 | 6.0669 | 12.134 |

**Rotation is real.** Both throats swing the same way, consistently, monotonically — 0.95°
of arc by t = 7. **The separation is going the wrong way**: outward by 0.5 %, accelerating,
where Newtonian gravity on M_tot = 2 at d = 12 asks for 0.17 *inward* per throat by now.

**Answered 2026-08-31, by t = 10: they repel, and the repulsion is the physics, not a
bug.** The measured relative acceleration is +0.0131 *outward* (quadratic fit over t ≥ 4,
slice-cache centroids) against −0.0139 Newtonian inward. The cause is the support field
itself: ρ < 0 at every point of the z = 32 slice (max exactly −0.0, min −2.7e-3,
`ExoticScalarField.impl.hpp:52` carries the phantom sign), and a phantom scalar *repels*
like charges where a normal one attracts. Each drainhole carries scalar charge
q = √(a²+m²)/√(4π) — set by the throat *radius*, not the mass — so

    F_scalar / F_gravity = 4πq²/m² = (a² + m²)/m²  =  5.00  for a = 2, m = 1,

net design acceleration 4× gravity, outward. Measured far-field charge fit: q_tot = 1.55
vs 1.26 predicted. Predicted outward 0.056 vs measured 0.013 — right sign, right shape,
4× down, which is the §7 coordinate under-read. **The ratio is 1 + a²/m² > 1 for every a
and m: like-charge drainholes can never merge under their own gravity**, and the Kepler
timetable that used to sit here (merger t ≈ 37–39) is void — the orbit is unbound.

**Controls, all from rest at d = 12, run 2026-08-31 — all three verdicts in.** Launched on
GPUs 1–3 with the baseline untouched. Each reached t ≈ 11 before an editor restart took the
session down, which is well past the ~5-unit gauge ramp and so deep inside the readable
window.

| arm | run | prediction | measured | verdict |
| --- | --- | --- | --- | --- |
| A `ctrl_rest_d12` | run `03_two_throats/ctrl_rest_d12`, [params](../../Examples/BinaryWormholeMerger/params_ctrl_rest.txt) | separates, net ≈ 4× g outward | **+0.0127 outward**, +0.47 by t = 11.5 | repulsion confirmed at zero momentum |
| B `ctrl_rest_a1` | run `03_two_throats/ctrl_rest_a1`, [params](../../Examples/BinaryWormholeMerger/params_ctrl_rest_a1.txt) | separates ≈ 4× weaker (net 1× g vs 4×) | **+0.0042 outward**, 3.0× weaker | charge set by *width*: confirmed, 25 % under |
| C `ctrl_flip_d12` | run `03_two_throats/ctrl_flip_d12`, [params](../../Examples/BinaryWormholeMerger/params_ctrl_flip.txt) | **falls together, net ≈ 6× g** | **−0.0196 inward**, −0.56 by t = 10.5 | merger route confirmed |

**The sign rule is measured, not assumed.** The decisive number is the ratio of arm C's
infall to arm A's escape at matched times. Same masses, same widths, same separation, same
grid, same binary: the two runs differ in `wormhole_phi_sign_B` and in nothing else, so the
ratio isolates the scalar force from every other effect in the problem — including the
coordinate under-read, which cancels between them.

    |Δd_C| / |Δd_A| = (1 + 5) / (5 − 1) = 1.500        predicted
                    = 1.511 ± 0.033                   measured, 15 matched times, t = 3.5 … 10.5

| t | A: like charges | C: opposite | ratio |
| --- | --- | --- | --- |
| 4.0 | +0.0146 apart | −0.0219 together | 1.49 |
| 6.0 | +0.0679 apart | −0.0998 together | 1.47 |
| 8.0 | +0.1672 apart | −0.2478 together | 1.48 |
| 10.0 | +0.3172 apart | −0.4827 together | 1.52 |

That one number fixes both halves of the claim at once: the scalar force is 5× gravity (not
2×, not 10×), **and it changes sign with the relative field orientation**. Two independent
checks agree. Arm A separates released from rest with no momentum at all, so the baseline's
escape was never a leftover of the initial kick. Arm B's push falls 3.0× when the throat
width halves, where a force tracking *mass* rather than width would not have changed at all
(predicted 4.0×; the 25 % gap is the §7 coordinate under-read, which does *not* cancel here
because the two arms have different throat widths).

**So, on this code and at these parameters: same orientation repels, opposite orientations
attract.** Like-charge throats are unbound at every a and m; the flip is the only
gravity-driven route to a merger.

Arm C rests on new initial-data support: `wormhole_phi_sign_B` (SimulationParameters +
BinaryWormholeInitialData, default +1, so every archived run stays bit-identical) flips
throat B's scalar orientation. Verified in the data, not just the parameter file — on the
t = 0 slice the field is exactly antisymmetric about the midplane (left half −0.9044 …
−0.0002, right half +0.0002 … +0.9044, mirror residual identically zero).

**What an anti-wormhole is, and why it needs no new stability argument.** The drainhole
scalar has a *direction* — the "flow" through the throat that gave Ellis's drainhole its
name — and φ → −φ reverses it. That flip is exact for a single body: every one-throat
property is sign-invariant, because each depends on the field only through its slope
*squared*.

| property of one throat | under φ → −φ |
| --- | --- |
| geometry (throat shape, radius) | identical |
| ADM mass (+1, same far-field pull) | identical |
| supporting energy density ρ ∝ −(∇φ)² | identical |
| equilibrium + growth mode (the 40 M shakedown) | identical |

So an isolated anti-wormhole is *indistinguishable* from the original — no local
measurement can tell which one it is, and the Stage 1/2.0 stability record transfers
wholesale. The orientation only matters between TWO throats, through the overlap of
their fields: same orientation reinforces (the measured 5× push), opposite orientations
cancel between the bodies (a 5× pull on top of gravity). Same rule as charges, sign
flipped because the field's energy is negative.

**Where stability genuinely ends: the merger itself.** Opposite orientations cannot
survive as one throat — the net scalar charge of the merged object is zero, and a
throat cannot stay open without its field. The expected endpoint is collapse to an
ordinary black hole plus radiated scalar, which is not a failure mode but the headline:
*wormhole + anti-wormhole → black hole* is the paper, with the horizon-formation time
and the radiated fraction as its two numbers.

**Stage 2.7 — the merger run.** `merge_orbit_flip_d12`
(run `merge_orbit_flip_d12`,
[params_merge_orbit_flip.txt](../../Examples/BinaryWormholeMerger/params_merge_orbit_flip.txt)),
launched 2026-08-31 on GPU 0 after the like-charge baseline was stopped at t = 20 having
opened by 2.02 units and still accelerating apart. It is `params_orbit_drainhole.txt` with
**one physics line changed** — `wormhole_phi_sign_B = -1` — so masses, widths, separation,
orbital momenta, grid and binary are all identical to the baseline and any difference in
outcome is the sign and nothing else. `stop_time = 60`, checkpoints every 10 code units.

The retained P = 0.12 was tuned against gravity alone and is only ~24 % of the circular
value for a 6× central force (√6 × 0.204 = 0.50), so expect a fast plunging spiral rather
than several wide orbits. The head-on arm C trajectory, extrapolated with the pull growing
as they close, puts contact near t ≈ 29 and coalescence near t ≈ 31; the orbital case
arrives later by whatever the angular momentum buys.

---

### 9. The puncture floors assume vacuum — the phantom core does not comply

The merger run formed its common trapped surface at t ≈ 30 and died at t = 52.07:
`NaN … name=h11` at level 3, in the core. The moving-puncture floors
(`min_chi = 1e-8`, `min_lapse = 1e-10`) keep collapsed *geometry* representable, but
they were built for vacuum interiors. Here the phantom scalar collapses with the
core and keeps sourcing the metric at the edge of the floored region — at death the
scalar still held 84 % of its throat value on a core the lapse had frozen 25 units
earlier. The gradients at the floor boundary steepen step after step until h11
leaves the reals.

The cure is the matter half of the puncture trick: exponentially damp φ and Π deep
inside the collapsed region, identified by the lapse (`CoreMatterDamping`, own
module, default off). The first window — full strength below lapse 1e-8 — was aimed
five orders too deep: it covered ~3 finest cells and moved the death from t = 52.07
to t = 52.09. The slice caches gave the real map: the collapsed scalar (|φ| up to
0.53) sits at lapse 1e-6..3e-2, and the lapse < 3e-2 contour reaches r = 0.63 while
the common apparent horizon sits at r = 0.875. The retuned window (3e-2 → 1e-3,
cosine ramp in log lapse, τ = 0.25) therefore acts strictly inside the horizon: no
damped signal can reach the wave zone, by construction.

The revalidation run cleaned the core to |φ| ~ 1e-10 — and died anyway, t = 52.86,
because the lapse window defeats itself: wrong-sign K pockets (K down to −2, pure
checkerboard) form at the ends of the collapsed bar, 1+log slicing re-inflates the
lapse there (∂ₜα = −2αK), and exactly the sickest cells rise *out* of the window —
measured |φ| = 0.82 surviving at r = 0.30 under lapse up to 0.43, unreachable by any
lapse threshold that spares healthy regions. A Kreiss–Oliger arm (σ 0.1 → 1.0) died
*earlier*, t = 51.68, NaN in K: dissipation attacks the puncture structure itself —
the same failure class as §2, measured again from the other side. The third cure, a
radius window (full damping inside r = 0.5, cosine ramp to zero at r = 0.7, engaging
at t = 33 once the common horizon exists — `core_damping_radius_*`), does not care
what the lapse does and bought the longest life yet: death t = 55.00, NaN in K, at
the *next* ring of un-damped scalar (r = 0.7–1.1, |φ| = 0.5–0.6). Four deaths, one
law: wherever un-damped phantom sits on collapsed geometry, the run dies there —
each window extension pushes the death outward and buys 1–2.5 units. Why the outward
march cannot terminate is §10.

Same session, same failure mode, second fix: the θ₊ scan's inner cut (built to mask
the Ellis–Bronnikov inversion artefact of an *uncollapsed* throat) was excluding the
coordinate-shrinking horizon after collapse. The scan now drops its floor to r = 0.5
once a half-space's minimum lapse falls below 1e-6 — and re-acquired the common
horizon at r ≈ 0.875, right up to the crash. That number is what certified the
damping window as causally safe.

### 10. The horizon is dissolving — phantom accretion is destroying the black hole

The offline Θ = 0 finder (`grteclyn-wrapper/scripts/validation/ah_radial_scan.py`:
full physical-metric radial scan, shell-max statistic, validated against the in-code
proxy — 1.07 offline vs ≈ 1.0 in-code at t = 51.5) measured the fully-trapped
sphere on every death-era snapshot that carries h_ij/A_ij:

| t | arm | trapped-sphere radius |
| --- | --- | --- |
| 51.5 | lapse window | 1.07 |
| 52.0 | lapse window | 1.05 |
| 52.5 | lapse window | 1.03 |
| 54.0 | radius window | 0.89 |
| 54.5 | radius window | 0.83 |
| 55.0 | radius window | 0.59 |

Validation: every snapshot's scan region is free of NaN/inf (the fatal NaN
post-dates the last write), and doubling both the angular and radial sampling of
the scan moves the crossings by ≤ 0.01 — the numbers are converged, the death-step
point included.

Two different damping schemes, one accelerating dissolution curve — the last half
unit loses 0.24 in radius, four times the early rate; extrapolated, the trapped
surface vanishes around t ≈ 56. The trapped *region* is strongly deformed: it
reaches past r = 2 along the poles while pinching to 0.6 in the tightest equatorial
direction — which is also why the in-code proxy (built for near-round geometry)
went blind on the radius-window arm.

This is phantom accretion doing what theory says it does (Babichev et al.: negative
energy crossing a horizon shrinks it). The surviving scalar ring at r = 0.7–1.1
straddles the horizon and falls in; the horizon pays for every unit of it. The
damping cannot be the culprit — deleting *negative*-energy matter pushes the mass
budget toward growth, so the measured shrinkage survives its own systematic. The
p045 arm corroborates from the other side: with enough angular momentum to avoid
merger there is no collapse at all, no NaN, a clean t = 60 — the phantom resists
the black hole by every route it has.

Consequences. (1) The §9 outward march of damping windows cannot terminate: the
causal seal every window relies on is itself shrinking toward zero. (2) The
"endpoint" headline may not be a Schwarzschild remnant plus ringdown but *horizon
formation at t ≈ 30 followed by destruction at t ≈ 56* — with the still-rising
second Ψ₄ swell as its outgoing signature. (3) Watching the dissolution to the end
needs a window that tracks the measured horizon down, accepts visible damping in
the final moments, or accepts the NaN as the end of the record. Not chosen yet.

Limitation for the record: runs launched before 2026-08-31 (r03000, headon, p045,
n160) did not plot h_ij/A_ij, so the finder cannot measure them — the truly
undamped control is unmeasurable, permanently. Every future launch keeps the full
plot list.

### 11. Refining the grid delays the death — it does not remove it

The obvious first answer to a NaN is "resolve it". `merge_orbit_flip_d12_n160`
tests that directly: 160 cells per side instead of 128 (dx 0.4 instead of 0.5,
25 % finer, ×2.4 the cost), everything else identical, **no damping at all**, and
run from t = 0 to death in one piece — the only undamped arm with no restart
boundary anywhere in it.

It died 2026-09-01 with the same NaN in `h11` on level 3, at **t = 53.61**.

| | N = 128, undamped | N = 160, undamped |
| --- | --- | --- |
| death | NaN at **t = 52.06** | NaN at **t = 53.61** (+1.55) |
| separation at t = 0 / 20 / 28 / 32 | 11.938 / 8.256 / 3.611 / 2.063 | 11.950 / 8.330 / 3.612 / 2.070 |
| common trapped region first seen | t = 29.93 | t = 29.74 |
| its largest radius | 3.438 | 3.400 |
| L2 Ham at t = 0 / 20 / 30 | 2.99e-3 / 4.39e-3 / 3.56e-3 | 2.53e-3 / 2.78e-3 / 2.52e-3 |
| min χ at t = 10 / 20 / 30 | 3.58e-6 / 8.05e-6 / 1.28e-5 | 1.71e-6 / 3.47e-6 / 5.67e-6 |
| last clean state (0.5 before the end) | min χ 1.0e-8 (floored), max\|K\| 1.67 | min χ 2.1e-6, max\|K\| 0.92 |

**Everything before the collapse converges.** The inspiral agrees to ≤ 1.8 % at
every matched time out to t = 32 on *both* trackers independently; the common
trapped region appears 0.19 units earlier and reaches within 1 % of the same
radius; the extracted Ψ₄ ℓ = 2, m = 0 amplitude at R = 14 matches the coarse run
to 0.2–4 % over t = 5–30, at both extraction radii. The physics of the merger is
not a resolution artefact.

**The death is not removed, it is postponed.** A 1.25× finer grid buys 1.55 code
units — 3 %. Fitting the two points to a logarithm (which is an extrapolation
from two points, not a measurement) gives ≈ 7 units of survival per e-folding of
resolution, so reaching t = 60 undamped would need N ≈ 400: 3× finer in each of
three dimensions and in time, roughly **90× the cost of the run that already takes
9 hours**. Refinement is not the cure. It is worth saying plainly because it was
the cheapest hypothesis on the list and it is now closed.

**What the finer grid does change** is the character of the death. min χ tracks
lower everywhere on the finer grid — 2.3× lower at matched times, the origin
resolving deeper as it should — and at the end it has *not* reached the 1e-8 floor
that the coarse run sits on from t = 50, while max \|K\| at the last clean step is
0.92 against 1.67. The finer run dies later and dies softer, with the puncture
floors less engaged. That is consistent with §9: the floors protect geometry and
not matter, and postponing the moment the geometry floors postpones the NaN.

Validation. Death time from two sources — the abort line in `run.log` and the last
row of `collapse_diagnostics.dat`, agreeing at 53.61. Inspiral from two independent
trackers (`binary_throat_diagnostics.dat` and `throat_track.dat`), agreeing on both
runs. Waveform at two extraction radii. The horizon numbers are the in-code radial
proxy on both runs — the same instrument on both sides, so the *comparison* is
sound even though the absolute value is not offline-verified: n160 predates the
h_ij/A_ij plot list, so §10's finder cannot be run on it. That gap is now closed
for future launches, not for this one.

## Traps that must not regress

| trap | what happens | guard |
| --- | --- | --- |
| `sigma = 2.0` | eats 34 % of the throat while every norm reads flat | 0.1 in all drainhole templates |
| `wormhole_momentumB` default | it is **minus** `momentumA`; for a single centred throat that plants an equal-and-opposite term at the *same* point and cancels the boost exactly, silently | pin it to `0 0 0` |
| puncture route to ADM mass | destroys the throat it is meant to weigh | `wormhole_id_type = 1` + `drainhole_mass` |
| `regrid_threshold` under a geometric tagger | does nothing at all | the parameter reader warns |
| `tagging_type = 2` without `throat_tracking` | boxes centred on stale positions | rejected in `check_params` |
| frame slice plane | the default cuts the plane the motion is perpendicular to — a moving throat simply fades | pick the plane from the arm's physics at launch |
| a fixed colour scale on a growing field | K grows ~30× over an inspiral; locked at merger amplitude every inspiral frame renders blank white, locked early every late frame saturates. Nothing errors — the movie is simply empty | `GRTECLYN_FRAMES_PER_FRAME_ZLIM=K` (default off, per field); re-fix a stable scale for the paper movie afterwards from the slice cache |
| throat tracker across a restart | the centres re-seed from the **params-file** positions, not from where the throats got to. Inside the search radius (2.0) it re-locks in one step; further out the search finds nothing, `nA` reads 0, and the refinement boxes stay at the seed | safe to restart from t = 20; before restarting from a later checkpoint, check `throat_track.dat` — if a throat has moved more than 2.0 from its params centre, seed the tracker from the last recorded row instead |
| areal radius under drift | it rays from the *static* grid centre, so it under-reads once the throat moves | re-extract post-hoc with the per-time centres in `throat_track.dat` |
| `checkpoint_interval` after a grid change | it counts **coarse steps**, not code units, and nothing re-derives it — `params_headon.txt` carried 2000 against a run only 800 steps long, so it never fired once | recompute `stop_time / (dt_multiplier · L/N1)` whenever any of those change |
| root-level `restart_file` | the key exists in `AMReXParameters.hpp` but the string behind it is never read back, so it aborts on an empty path instead of restarting | `amr.restart` — the key AMReX itself reads |
| a restarted run's outer boundary | the interior restores exactly; the boundary does not, and the error walks inward at ~c | see below — do not quote domain-wide norms or waves across a restart |

**Not a candidate: σ = 2.0 as a stability fix.** It is the only setting that reaches t = 40
at `max_level = 2`, and it gets there by destroying the throat.

### Restarting: exact where it matters, wrong at the boundary

Stage 3 runs are long enough that losing one to a crash is expensive, so checkpointing is
now on in `params_headon.txt` (every 10 code units) and `params_spiral.txt` (every 25).
Measured 2026-08-31 on the smoke-test grid: checkpoints hold all 27 evolved variables plus
3 ghost cells in double precision, and a restart resumes at the right step and runs to
completion.

**Re-verified on the production orbit grid, 2026-08-31.** `orbit_d12_p012` was restarted
from its t = 0 checkpoint and run to t = 1: the log reports the restart time correctly, no
NaN, and the tracked throat positions and pit-χ values are digit-for-digit identical to the
parent run's at t = 0.99 and t = 1.00 — across a regrid. The restart path is production-ready
on the real grid, not just the smoke test. (The tracker's re-seed caveat in the table above
is separate and only bites from *late* checkpoints.)

It is **not** a continuation of the same calculation, though. Comparing one
step taken from a restored checkpoint against the same step in a continuous run:

| region | max ΔK, one step after restart | after 0.2 |
| --- | --- | --- |
| throat, r < 4 | 1.8e-16 — roundoff | 2.0e-12 |
| r = 4–6 | 4.6e-9 | 7.2e-7 |
| outer, r > 6 | **6.9e-3 (1.5 % relative)** | 1.6e-2 |

So the interior — the throat, the merger, everything the physics is about — comes back
bit-exact; the outer boundary does not, and that error walks inward at roughly the speed of
light. The sponge does not suppress it (tested; K unchanged at 1.5 %).

For a Stage 3 box with the boundary at r = 32 and extraction at 12 and 20: the domain-wide
constraint norms are contaminated **immediately**, since they integrate over the boundary,
so a restart puts a step in them and no growth-rate fit may cross one. Ψ₄ at r = 20 stays
clean ~12 units after a restart, at r = 12 ~20, the throat ~30. Restart to recover a crash
and keep the merger going; never inside a window whose waves or norms will be quoted. A
production number should come from a run that went straight through.

## Route B traps — what the 2026-08-28 matter investigation left behind

Folded in when `MatterDebug.md` was retired, 2026-08-31. Its main finding — a puncture
throat cannot be resolved in proper distance — is problem 1 above, and is fixed. These four
are not fixed but *dormant*, and each bites at **Stage 2.2**, the moment initial data starts
coming from a file instead of a formula.

**1. Refining below a file-based solve's own dx destroys the throat.** The `.gridinit`
bridge flattens the solve to level-0 dx; prolongation cannot recover sub-cell structure, so
it fills the interior with a nearly constant χ and the areal radius rises monotonically —
**the throat is gone before the first step**. Measured on identical data: `max_level = 0`
keeps it (interior minimum at r = 1.299, R = 4.507); levels 1 and 2 both lose it, while
level-0 ingestion is byte-exact, so the file is not the problem. Refining does not merely
fail to add detail, it **invents smooth wrong detail** — here, the absence of a wormhole.
Route A is immune (analytic data at each level's own dx; R_min to 0.01 % at level 1). Run
throat diagnostics at `max_level = 0`, or land the split-ID loader first.

**2. The solver can stall and report "Converged" anyway.** At `bh1_bare_mass = 4` the
GRTresna nonlinear solve went from 100 % Hamiltonian residual to **99.08 % in one
iteration** with max|δψ| = 0.005, exited early declaring convergence, and wrote an
`InitialDataFinal` that does not solve the constraints. A clean solve at m = 2 goes
100 % → 0.48 %. **Read the residual, never the word.** The stalled solve was deleted.

**3. Treat matter conservation as a resolution diagnostic, not a physics result.** On the
puncture geometry the Noether charge fell −10.52 → −2.09 (**−80 %**) by t = 14 while the
field amplitude barely moved (max φ 0.0997 → 0.075) and boundary flux was ~1e-11 — destroyed
*in the interior*, fastest over exactly the interval in which the throat closed. Until it
holds to a few per cent, no survival or collapse time from that family means anything.

**4. The areal-radius readout lands on the innermost cell if you let it.** R = r/√χ
*diverges* at the compactified origin, but unresolved inner cells report it small, so a bare
argmin tracks a "collapse" that is not happening — 0.152 against a true 0.498 on a b = 0.5
throat. `--areal-min-radius` excludes an inner ball; **archived `areal_radius.dat` columns
predating that flag are unreliable**, several reporting exactly dx/2.

**And the standing correction:** the Q-ball route (`ComplexExoticScalarField` + complex
sextic, whose conserved charge would give the support a preferred size) was **not refuted —
it was never testable.** Its own numbers were clean: painted amplitude 0.0997 against an
independently solved flat-space eigenstate of 0.0991, Π₂ = −ωφ to every printed digit, Ham
residual → 0.48 %, momentum residual identically zero. The geometry failed, not the matter;
on the drainhole it is testable again, and untested.

## Known inconsistencies in the matter sector

Flagged 2026-08-31 in review; none affects any run so far, all use `phantom_mass = 0`.

1. `ExoticScalarField` multiplies the *entire* T_μν — kinetic **and** potential — by
   −`support_strength`, while `add_matter_rhs` keeps the standard-sign `dVdphi`. Not
   derivable from one action once `phantom_mass ≠ 0`. **Fix before any massive-phantom or
   Q-ball work.**
2. Two-throat data is plain excess-sum superposition — no Helfer/Ning correction, no solve.
   That is exactly Stage 2.1/2.2.
3. `support_strength ≠ 1` scales gravity but not the field equation, so ∇·T ≠ 0. Diagnostic
   knob only.

## Decision gates (from the report, unchanged)

- single throat still loses charge > few % → the instability is *physical*; reframe as
  collapse/expansion of a two-throat system;
- CTTK returns K² < 0 with two exotic lumps → past the existence boundary; reduce ADM mass,
  increase separation, and **report the boundary as a finding**;
- timelike inner boundary (excision) unstable → abandon true topology for this paper.

## What Stage 3 costs, against the 40 M window

| separation d | free-fall time ≈ (π/2)·√(d³/8M) | fits in 40 M? |
| --- | --- | --- |
| 10 | ~12 M | easily — but the throats start close enough that the superposition correction works hard |
| 16 | ~25 M | **yes**, with 15 M of margin for ringdown and extraction |
| 20 | ~35 M | marginal; no room after merger |

The wide separation the superposition error wants (d/b ≥ 8, i.e. d = 16 at b = 2) is
affordable. That is what 1.6 bought.

**The caveat that survives.** The mode is still growing at t = 40 and doubling every ~1.6
there. Two throats seed it harder than one sitting at an exact fixed point, since superposed
data starts well above this run's 2.5e-3 floor. **Budget the merger to finish inside 40 M
rather than to run up to it, and re-measure the growth rate on two-throat data** rather than
assuming this one carries over.
