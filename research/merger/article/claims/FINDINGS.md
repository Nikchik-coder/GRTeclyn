# What the ledger found (2026-09-24)

Building the ledger re-read every quantitative claim in `research.tex` against
the pack: 827 rows, 741 recomputed by extractors, **714 agree**. This page lists
what does not, for a decision; nothing in the text was changed to fix any of it
(the macros print exactly what the article said before). `claims.py check`
lists the 27 numeric mismatches live; a row stops failing when the article or
the analysis is corrected and its `tex`/`num` updated.

## A. Statements the data contradict (the wording must change, not just a number)

| where | the article says | the data say |
|---|---|---|
| §VII.C (wall) | "every collapsed single throat runs clean to t = 100 behind its horizon" | only ε = +10⁻² does. ε = +10⁻³ (horizon from t = 25) dies at 40.07; ε = +10⁻² + ε₂ at 27.58; ε = ±0.1 at 14.06 / 15.17 |
| §XII (cost) | "810 GPU-hours … recomputed by a script in the pack" | the script crashed (speed-0 stubs; fixed) and charged ten restart legs from t = 0: 160.7 h too many. For the 132 evolutions: **649.6 h** |
| §VI (head-on) | the down-step "agrees on the horizon mass to 1.3 %" | 1.3 % is the median difference of the *momentum-constraint* norm; horizon masses agree to 0.24 % (level-5 fill twin), 0.05 % (the level-5 arm) |
| §VI (head-on) | χ = 1.2×10⁻⁶ at the midpoint at t = 26.91 | that value is the superseded restart-chain arm's; the level-5-from-t = 0 arm the paper uses reads 6.1×10⁻⁸ |
| §VIII.F (scalar) | "at R = 30, α and χ lie within 1 % of unity" | never measured; the initial data give α ≈ 0.93, χ ≈ 0.87 there, a 6–13 % flux correction |
| §VIII.F (scalar) | ratio falls to 1.1 and 0.8 at t = 70 / 80 | computed with an unfiltered running E_GW; with the band-limited convention of Fig. gw_ligo(d) both read ≈ 1.5 |
| §VIII (head-on ringdown) | period "21 % shorter than the Schwarzschild fundamental" | uses M_MS = 1.56 at formation; over the fitted window the mass falls to ≈ 1.2, where the Schwarzschild period (20.5 M) matches the measured 20.6 M |
| §VIII | "15.5 units after the R = 20 peak" (t = 76.1) | t = 76.1 is 21.6 units after the peak; 15.5 is the gate margin 70 − 54.5 |
| §IV.E (inflation) | the deviation grows "at the mode's 0.190 ± 0.002" | that is the unkicked level-4 plateau; the kicked arm has none (local rate 0.34 → 0.15 over t = 19–31) |
| Limitations | late constraint growth "on both branches from t ≈ 75–80" | the kicked inflation arm grows from t ≈ 52–55 (its own Fig. 4 caption: norms "hold to t ≃ 50") |
| Diagnostics vs Limitations | shape systematic "~13 % once settled, 34 % while forming" vs "up to ~10 %" | inconsistent; no source for 13 %; 34 % is the level-5 head-on, the level-3 arms reach 35.6 / 43.7 % |
| Discussion | τ ln(2×10³) ≃ 33, "a fifth of an orbit" | no source for 2×10³; the paper's own seeds give ≤ 350 → 26 units, a seventh |
| §VIII.F / Discussion | E_φ "carries a 30 % sphere spread" | the *ratio* spreads 30 %; E_φ itself differs ×12 between R = 14 and 30. Units also differ: head-on E_φ in single-throat masses, fly-by in total mass (M = 2) |
| Controls | the GRTresna bridge "loses the throat at t = 5.3" | its solved data never contained a throat (registry: nothing may be quoted from it) |
| Table I | "head-on, d = 8"; refinement ladder "levels 3–7" | the group includes `merge_headon_flip_d12` (d = 12); the ladder spans 4–7 (level 3 is its parent, in the orbital chain) |
| §VI | ±ε formation "within 0.5 %" and track "~3 %" | each holds for a different radius (coordinate vs areal); under one reading one of them fails |
| §VI | max\|K\| "running away to 18" | peaked at 209 one row earlier (t = 26.90); 18.1 is the last row |
| §VI | down-step within "0.05–0.33 % of peak over t = 45–100" | only against arms restarted from the same t = 22 checkpoint; against the level-5 arm 4.5–62 % |
| §VII | the same death printed 60.44 and 60.45 | 60.445 |

## B. Numbers off by more than their printed precision (27; `claims.py check`)

| id | printed | data | cause (row note has the detail) |
|---|---|---|---|
| clmDetGpuHours | 810 | 649.6 | restart legs overcharged (A) |
| clmDetKnobHeadonD | 8 | 12 | one d = 12 run in the d = 8 group (A) |
| clmDetShortestMs / clmDetBankDurLo | 5 ms | 3.2 / 2.5 ms | the fly-by's light rungs |
| clmDetThroatFreq / FM / OverKerr | 335 Hz / 0.050 / 0.56 | 331.8 / 0.0490 / 0.554 | value at the envelope peak; the track runs 342 → 324 Hz |
| clmDetEfoldsPosLo | 11 | 11.53 | 46.1/4 rounds to 12 |
| clmDetGrowthTimeLo | 415 Myr | 414.5 | 45 Myr × ln 10⁴ |
| clmHeadonMidpointChi | 1.2×10⁻⁶ | 6.1×10⁻⁸ | superseded arm (A) |
| clmHeadonCompactnessEnd | 1.05 | 1.042 | last row of the fit window |
| clmHeadonDownStepMass | 1.3 % | 0.24 % | wrong quantity (A) |
| clmHalfMassLapseLow | 0.036 at t = 13 | 0.038 | 0.036 is reached at t = 13.99, the step before the NaN |
| clmSpiralMaxKStart | 0.0084 | 0.103 | the restart's first row, a coarse-grid artefact the figure masks |
| clmSpiralAnatomyFirst | 36.1 | 36.0 | cosmetic |
| clmControlMSixNext | 10⁻¹³ | 5×10⁻¹³ | rounds to 10⁻¹² |
| clmUnkickedHorizonSpan | 40 | 39 | scans at t = 61 and 100 |
| clmConstraintFloorBothBoxes | t ≳ 80 | 76.8 | the L = 128 box leaves its floor first |
| clmGwSlopeShallow / Steep | −3.3 / −5.9 | −3.35 / −5.85 | round to −3.4 / −5.8 (FIGURES.md says −3.4) |
| clmGwHeadonSwingTimeB/C/D | 43.6 / 63.5 / 81.7 | 43.81 / 63.39 / 82.24 | flat late troughs; no single read reproduces all four |
| clmGwScalarMouthReach | t ≈ 80 | 92.45 | the mouths pass R = 30 where panel (c) draws its rule |
| clmGwCensTauMid | 23 | 23.50 | rounds to 24 |
| clmGwKickedRadiusEnd | 2.45 | 2.54 | 2.45 is the common-centre scan FIGURES.md rejects near the floor |
| clmGwKickedEfoldLo | 5 | 5.9 | no window reproduces "5–7" |

## C. Quoted but not reproducible from anything tracked (manual rows)

- **Every shape-free flow-finder result** (MOTS radii 4.83/4.80/4.77/4.72 and 4.15, masses 2.41/2.36/2.08, the 23 % deformation, θ values, the seven slices): the slices sit on the second node's scratch and were never packed — pack the slices or the finder's outputs.
- The flow finder's validation ("R = 2M to 0.03 %", "head-on remnant to 2 %"), "in-code and offline agree to 0.1 %", "~13 %": no source anywhere.
- "χ ∼ 6 by t = 92" (read off movie frames); "past t ≈ 60 separation tracks the pits" (no recorded criterion); speed claims (12–18 u/h; measured 5.7–18.4); "four-GPU nodes" (this node sees two).
- The η = 4 level-5 death (60.04) is readable only from `wall_clocks.dat`: that arm's packed log and streams stop at t = 55 — pack the full log.

## D. Stale notes elsewhere (the article is right)

The registry's dx for `ladder_L4`/`L5` is one level off; the registry and the
separation note give 0.243 (re-fit: 0.246); NOTES.md gives the sign ratio as
1.511 ± 0.033 (current: 1.518 ± 0.021); the results README's p = 0.15 plateau
0.816 (current: 0.87); two registered runs are not packed
(`merge_headon_flip_d8_v1b_freeze_t100`, `v2_spiral_d12_p012_L128_lvl5_t100_r03600`),
and `single_eps_p1e2_t250` is packed only as a stub.
