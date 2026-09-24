# What the ledger found, and how each item was resolved (2026-09-24)

Building the ledger re-read every quantitative claim in `research.tex` against
the pack: 827 rows, 741 recomputed by extractors, 714 agreeing. The rest are
listed below with the fix applied the same day. After it: **852 rows, 773
recomputed, all agree** (`claims.py check` exits 0). What stays open is under
"Still open" at the end: two things need the second GPU node.

## A. Statements the data contradicted: the wording changed

| where | the article said | the data say | now |
|---|---|---|---|
| §VII.C (wall) | "every collapsed single throat runs clean to t = 100 behind its horizon" | at level 3, ε = +10⁻³ (horizon from t = 25) dies at 40.07 and ε = +10⁻² + ε₂ = 10⁻² (horizon from 14) at 27.58; ε = ±0.1 at 14.06 / 15.17. The unkicked and ε = +10⁻² level-3 arms and every level-4 collapse do run clean | lone collapses die behind their horizons at level 3 too, while no level-4 collapse dies: the head-on's pattern |
| §XII (cost) | "810 GPU-hours … recomputed by a script in the pack" | the script crashed (speed-0 stubs) and charged ten restart legs from t = 0: 160.7 h too many | **650** GPU-hours, "a restarted leg from its checkpoint"; `gpu_hours.py` fixed the same way |
| §VI (head-on) | the down-step "agrees on the horizon mass to 1.3 %" | 1.3 % was the median momentum-constraint difference | horizon masses agree to **0.24 %** (level-5 fill twin) |
| §VI (head-on) | χ = 1.2×10⁻⁶ at the midpoint | the superseded seamed arm's value | **6.1×10⁻⁸** (the level-5 arm the sentence names) |
| §VIII.F (scalar) | "at R = 30, α and χ lie within 1 % of unity" | never measured; the initial data give α ≈ 0.93, χ ≈ 0.87 there. Also F_geo = α²χ^(−1/2) F_kin on a conformally flat sphere, so "the conformal factors cancel" was wrong too | both stated: neither is recorded, initial-data values given, α²χ^(−1/2) ≈ 0.94, a **6 %** correction not applied |
| §VIII.F (scalar) | ratio falls to 1.1 and 0.8 at t = 70 / 80 | the running E_GW integral drifts after the burst; band-limited (Fig. gw_ligo(d)) it holds near 1.5 | both conventions stated: running 1.1 / 0.8; band-limited **2.7 / 1.5 / 1.4** at t = 60 / 70 / 80 |
| §VIII.A (collapsing throat) | period "21 % shorter than the Schwarzschild fundamental" | used the fixed M_MS = 1.56 (t ≈ 24); over the fitted window M_MS falls 1.47 → 1.16 → 1.21 | the period is within a few percent of the Schwarzschild fundamental at the late mass (**19.5–20.3 M**); `queue2e_gates.py` now reports both |
| §VIII.D (fly-by) | "15.5 units after the R = 20 peak" (t = 76.1) | 15.5 is the gate's margin 70 − 54.5 | hung on the gate |
| §IV.E (inflation) | the kicked arm grows "at the mode's 0.190 ± 0.002" | that is the unkicked twin's plateau; the kicked arm's deviation crosses zero near t = 14 and has none | 0.190 attributed to the twin; kicked arm "no such plateau", local rate **0.34 → 0.15** over t = 19–31 |
| Limitations | late constraint growth "on both branches from t ≈ 75–80" | the kicked inflation arm grows from t ≈ 55 | added "(from t ≈ 55 on the kicked inflation arm)" |
| Diagnostics vs Limitations | shape systematic "~13 % once settled, 34 % while forming" vs "up to ~10 %" | no source for 13 %; lone throats ≤ 2.8 % (throat-centred scans); level-3 head-on arms 35.6 / 43.7 %; the down-step rounds to 4.2 % | one statement in both places: ≤ **3 %** lone, up to **34 %** forming (**44 %** at level 3), **4 %** rounded |
| Discussion + Controls | τ ln(2×10³) ≃ 33, "a fifth of an orbit" | no source for 2×10³; the paper's seeds give ≤ 350 | **τ ln 350 ≃ 26** units, **0.14** of an orbit (both places) |
| Limitations + §VIII.G | E_φ "carries a 30 % sphere spread"; head-on E_φ unitless | the ratio spreads 30 %; E_φ differs ×12 between R = 14 and 30; head-on E_φ was in single-throat masses | the ratio's 30 %, E_φ's **×12** and the head-on's **35 %** stated; head-on E_φ = **−0.028/−0.036/−0.038 M** (total mass) |
| Controls | the GRTresna bridge "loses the throat at t = 5.3" | its data never contained a throat | "cannot carry the throat … nothing is quoted from that run" |
| Table I | "head-on, d = 8"; ladder "levels 3–7" | the group includes a d = 12 run; the group spans levels 4–7 | "d = **8/12**"; ladder levels **4**–7 |
| §VI | ±ε formation "within 0.5 %", track "~3 %" in "radius" | coordinate radius at formation, areal when tracking | areal throughout: **1.1 %** at formation, **~2 %** tracking; mass 0.5 % / ~1 % |
| §VI | max\|K\| "running away to 18" | 18.1 is the last row; the peak is 209 one row earlier | **209** |
| §VI | down-step within "0.05–0.33 % of peak over t = 45–100" | only within the family restarted from t = 22 | qualified; after t = 70 that family and the level-5 arm part by **4.5–62 %** |
| §VII | one death printed 60.44 and 60.45 | 60.445 | 60.45 in both |

## B. Numbers off by more than their printed precision: the print changed

| id | printed | data | now |
|---|---|---|---|
| clmDetGpuHours | 810 | 649.6 | 650 |
| clmDetKnobHeadonD | 8 | 12 (one run) | clmDetKnobHeadonDLo/Hi: 8/12 |
| clmDetShortestMs / clmDetBankDurLo | 5 ms | 3.2 / 2.5 ms | 3.2 ("the lightest fly-by injection", not "the shortest") / 2.5 |
| clmDetThroatFreq / FM / OverKerr | 335 Hz / 0.050 / 0.56 | 331.8 / 0.0490 / 0.554 | 332 / 0.049 / 0.55 ("at its envelope peak"; "a single" dropped) |
| clmDetEfoldsPosLo | 11 | 11.53 | 12 |
| clmDetGrowthTimeLo | 415 Myr | 414.5 | 414 |
| clmHeadonMidpointChi | 1.2×10⁻⁶ | 6.1×10⁻⁸ | 6.1×10⁻⁸ |
| clmHeadonCompactnessEnd | 1.05 | 1.042 | 1.04 |
| clmHeadonDownStepMass | 1.3 % | 0.24 % | 0.24 |
| clmHalfMassLapseLow | 0.036 at t = 13 | 0.038 | 0.038 |
| clmSpiralMaxKStart | 0.0084 | 0.103 | 0.10 |
| clmSpiralAnatomyFirst | 36.1 | 36.0 | 36.0 |
| clmControlMSixNext | 10⁻¹³ | 5×10⁻¹³ | 5×10⁻¹³ "of peak" |
| clmUnkickedHorizonSpan | 40 | 39 | 39 |
| clmConstraintFloorBothBoxes | t ≳ 80 | 76.8 (L = 128), 82.2 (L = 64) | 77 and 82, per box |
| clmGwSlopeShallow / Steep | −3.3 / −5.9 | −3.35 / −5.85 | −3.4 / −5.8 |
| clmGwHeadonSwingTimeB/C/D | 43.6 / 63.5 / 81.7 | 43.81 / 63.39 / 82.24 | 43.8 / 63.4 / 82.2 ("lengthening" dropped: the periods are not monotone) |
| clmGwScalarMouthReach | t ≈ 80 | 92.45 | 92 |
| clmGwCensTauMid | 23 | 23.50 | 24 |
| clmGwKickedRadiusEnd | 2.45 | 2.54 | 2.54 |
| clmGwKickedEfoldLo | 5 | 5.9 | 6 |

## C. Quoted but not reproducible from anything tracked

- **Flow-finder validation**: re-run (`ah_flow_finder.py --analytic all`, 15 s), log packed at
  `results/merger/campaign/05_binary_spiral/flow_finder_selftest.log`. Worst over six seeds:
  R = 2M to **0.24 %**, M_MS to **0.12 %**; the old "0.03 %" was the best seed. The head-on
  remnant's "2 %" has no record and its plotfile is gone: the number is dropped, the
  qualitative check kept.
- **"In-code and offline pipelines agree to 0.1 %"**: measured. On the head-on they agree to
  **0.2 %** at the burst peak. On the single throats the in-code stream is floor-dominated
  inside the burst window, and the text now says so.
- "past t ≈ 60 separation tracks the pits": the number is removed (tied to the scan-edge time).
- Speeds: **6–18** u/h at production settings; t = 100 single-throat / head-on arms **5–7 h**.
- "four-GPU nodes" and the CPU line: removed (not verifiable from here).
- "χ ∼ 6 by t = 92" (read off a movie frame): kept, with its manual source row.

## D. Stale notes elsewhere (the article was right): fixed

The registry's dx for `ladder_L4`/`L5` (one level off); the registry and results README's
offset-law prediction 0.243 (re-fit 0.246, both now given); `NOTES.md` and the registry's sign
ratio 1.511 ± 0.033 (1.518 ± 0.021 added); the README and registry p = 0.15 plateau 0.816
(0.87); the README's "21 % short" ringdown; `summary.md` regenerated from the registry.

## Still open

- Every shape-free flow-finder result on the spiral (MOTS radii, masses, the 23 % deformation,
  θ values, the seven slices) rests on slices on the second node's scratch: pack the slices or
  the finder's outputs.
- The η = 4 level-5 death (60.04) is readable only from `wall_clocks.dat`: pack that arm's full
  log from the second node.
- Two registered runs are not packed and are not on this node
  (`merge_headon_flip_d8_v1b_freeze_t100`, `v2_spiral_d12_p012_L128_lvl5_t100_r03600`), and
  `single_eps_p1e2_t250` is packed only as a stub.
