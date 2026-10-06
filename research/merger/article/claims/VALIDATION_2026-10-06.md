# Paper validation — 2026-10-06

Scope: `research.tex` at feature/merger `58f205f3`. Every number, table, figure and method statement was checked
against the results pack (`results/merger/`), the evolution and analysis code, and the run params. Five read-only
agents split the paper by area (model and code / single throat / pairs and mergers / waves / detector and
discussion), and the cross-cutting checks were run separately. Nothing in the paper, the ledger or the figures was
changed.

**Notation.** Line numbers are `research.tex` lines. ✓ marks findings re-verified independently of the agent that
found it; "2×" marks findings two agents reached independently. Severity: **A** = wrong number, or a false or
unsupported statement; **B** = a figure or caption that does not match its data; **C** = imprecise, or weak
provenance; **D** = cosmetic.

## Fix status (2026-10-06, same day)

The fix pass (five agents by area plus the coordinator) settled every A and B finding:
- **Fixed in the paper:** most findings.
- **Fixed by cutting the claim:** A30, the "monotone"/"settled" wording, and the abstract's switch-off timescale.
- **Fixed by recomputing as `auto` ledger rows:** the derived values (race e-folds, GW share, Ω_WH, ratios, gates, speeds).

Measured state after the pass: claims check 905 rows (651 recomputed, 0 problems); both engines build at 26 pages; body
15 299 → 15 212 words. The abstract also now says "first three-dimensional" and carries no citation (the user).

**Second pass (same day, the user's "finish the fixes"):**
- **Fixed.**
  - Figs. 4 and 12: the in-frame names moved into keys above the frames.
  - The idle-solve bounds are re-pointed to the packed L = 128 test (|w0| = 4.5e-6, far side 4e-6; max|W| unquoted).
  - Every waves C item: the head-on E_phi on outgoing windows to the t = 80 noise gate, with tau fits over t = 30-80; the memory range on one window; the BBH head-on per its Brill-Lindquist mass (18x); the amplitude ratio at R = 14; the flux factor from the two-throat formulas; the 14 % floor; Fig. 13 legend styles; M_SUN_SEC; the throat's Fig. 8 track cut at t = 58; the scalar QNM fit ending at t = 80 (damping 10 % slower).
  - Fig. 7 / 8(a): the merger's |rPsi4| beat at 2 omega (counter-rotating content), so complex modes now draw the upper envelope |P+| + |P-|.
- **Literature (24 rows).** 22 are verified against their sources. The FIRAS range is corrected to 1e5-1e12 Msun (Nakama et al. 2018 abstract), and the natarajan2024 title is corrected. The l = 1 scalar QNM is confirmed by a Leaver continued fraction; it is not printed in Berti et al.'s text.
- **Left open.**
  - The moving pairs' flat mass in p is now the REQUIRED run MASS-t0 in STATUS (needs the go).

Final state: claims check 906 rows, 667 recomputed, 0 problems; both engines build at 26 pages; body 15 299 -> 15 214 words.

## Bottom line (as found, before the fixes)

- **The machinery is sound.**
  - Both engines build: LuaLaTeX and pdfLaTeX, 26 pages, no undefined references or citations.
  - All 739 macros the text uses are defined, and `numbers.tex` equals the ledger.
  - `claims.py check` recomputes all 587 auto/def rows.
  - All 15 figures re-render byte- or pixel-identical from the pack, so they are current with their scripts.
  - Tables I, II and IV reproduce cell by cell, and the Table III counts reproduce (96 runs, all packed, all in the
    registry).
  - The O3b search numbers and all 10 video links check out.
- **The open problems are in what the automation does not cover.** These are the 299 manual/lit rows, bare text,
  extractor semantics, and the trust-window rule. About 38 distinct A-level problems, 9 B, about 80 C and about 24 D.
  They cluster in six groups:
  1. **Stale manual rows.** Values were frozen before the 10-05 head-on axis fix (×4 energy), before the switch to
     matched or boosted data, or are read from archived superposed runs.
  2. **Numbers quoted past trust windows.** This breaks the paper's own rule at l.455: fly-by energies and drawn
     records, the pure-quadrupole horizon, separations at t = 100, and the head-on E_GW through its level-1 noise.
  3. **Monotonicity and "settled" claims the MOTS data contradict.** The head-on horizon and the d = 6 remnant both
     regrow.
  4. **The "approaches the GGS rate with resolution" narrative (abstract, Sec. IV.B) is a fit-window artifact.** At
     matched small amplitude both levels sit at τ ≈ 5.1–5.2, which is the linear 5.13.
  5. **Method statements the code does not do.** The MOTS finder is capped at level 2/3. Not every binary is at
     L = 128. The exact-boost runs do not start from zero shift.
  6. **Reproducibility statements in Sec. XI that are not true today.**
     - develop's pack is the pre-cleanup one, and develop has no claims ledger.
     - binaries.tsv is incomplete.
     - "recomputes every number" is false: 299 rows are manual or lit.

---

## A — wrong or unsupported

### Reproducibility and run matrix (Sec. XI, Table III, Sec. III)

**A1 ✓ — l.631, "results pack at …/tree/develop/results/merger".** `origin/develop` (cbd3725b, "Merge feature/merger
into develop, without research/") is behind feature/merger:
- It has 164 packed runs against 109, including 55 that are not in Table III; superseded superposed runs are among them.
- It lacks the DAMP-off run.
- It has no `research/` at all, so the claims ledger the same sentence advertises is not there.

The paper's 15 figure files are identical on both branches.

**A2 ✓ — l.631, "the claims ledger that recomputes every number quoted here".**
- 299 of the 886 rows are manual or lit and are not recomputed.
- Bare numbers in the text are not in the ledger at all.
- 147 ledger rows (71 manual) are no longer used by the text.

**A3 — l.631, "a table in the pack maps every binary to its source commit".** This is false for 13 packed runs, 12 of
them counted:
- `single_hold_t100`, the production reference, ran `main3d.gnu.MPI.CUDA.ex`, which is not in binaries.tsv.
- Seven lone-throat arms ran the "unstamped" stage0/chireg binaries.
- Three BBH runs ran `BinaryBH3d.gnu.MPI.CUDA.ex`, which is not listed.
- Two BBH runs name no binary.
- Some commits in binaries.tsv are `-dirty` builds or "inferred".

**A4 — l.633, production speed and cost.**
- `clmDetSpeedProd` "6–18 u/h": the counted L=64 level-3 legs run at 4.3–18.4 u/h. The rest pairs run at 4.3–4.7.
- "a t=100 single-throat or head-on evolution takes 5–7 h": correct for single throats (5.4–5.6 h). No counted run is
  a head-on at production settings: the head-on chain costs 29.3 h. The 6.6–7 h came from archived superposed L=64
  head-ons.

**A5 (2×) — l.252 vs l.280, box size.**
- Table III says "Unless stated … L = 64".
- Sec. III.B says "every binary … use L = 128".

Both statements are false for part of the matrix:
- 29 counted binaries are at L = 64: the 8 rest pairs, 18 placement probes, 2 scouts and `check_flyby_d12_p025`.
- The head-on (8/8), the merger chain (6/7), the d=12 p=0.12 arm, the fly-by scan, 2 solve verifications and the BBH
  head-on are at L = 128, which the table does not state.
- The lone-throat row also counts `single_m05_t040` (m = 0.5) with no m knob listed.

**A6 — l.252, "constraint-solved initial data, momentum carried by the exact Lorentz boost" for all 96 runs.**
- The 5 vacuum BBH controls use the BinaryBH example's Bowen–York data.
- The 19 seeded singles have no constraint solve; l.246 itself says "Neither seed is constraint-solved".
- All counted wormhole binaries are fine: `constraint_solve=1`, `puncture_mode=3`, `momentum_model=1`.

### Model and method (Secs. II–III)

**A7 ✓ — l.173, "With momentum the iteration converges the same way (d=12, p=0.12: R_min within 0.02 % of R⋆)".**
- `clmMatchedRminDevOrbit` is read from `t0_matching/t0_checks.tsv` (CPU, 2026-09-27). That build had no
  `wormhole_momentum_model`; the exact boost arrived in dc34eb51 on 09-29. So the 0.02 % is the superseded
  Bowen–York pair.
- The exact-boost pair's own t = 0 scan (`t0_v2_spiral_d12_p012_L128_lvl5_lb_csm/horizon_scan.dat`) gives
  R_min = 3.8780. That is 0.02 % from the scan's isolated reading (3.8772) but −0.30 % from R⋆.

**A8 ✓ — l.310, MOTS data "interpolated from the finest refinement level covering the surface".**
- The finder is capped: level 3 over ±4.5 on the head-on, level 2 over ±6 on the orbits (`consumer_profiles.sh`,
  `headon_first_law.fields_on_box`).
- Every row of every packed `mots_spectral.dat` is level 2 (658 rows) or level 3 (277 rows), whatever the run's
  max_level (4–7).
- So the level arms do not change the finder's input.

**A9 — l.296, `clmPsiPipelines` "0.2 %".**
- This manual row was frozen from the archived superposed head-on.
- On the current head-on (in-code `Weyl4_mode_20` against offline `psi4_mode_l2m0`) the agreement is 0.13 / 0.06 /
  0.41 % at R = 10/14/18, so the worst sphere is 0.4 %.

### Single throat (Sec. IV, Sec. VIII.A)

**A10 ✓ — abstract l.90 and l.342, "the e-fold … approaches the [GGS] rate with resolution … 2.5 % at our finest
level".** The printed τ values (5.875 / 5.259) reproduce, but the resolution reading does not.
- The ε = −10⁻² kicked arm has the same τ at both levels: 5.17 against 5.21 (t = 14–22), and 5.29 against 5.33
  (15–24).
- At small deviation, the unkicked throat's local τ is 5.12 at level 3 (t = 40–50) and 5.21–5.24 at level 4.
- The level-3 τ climbs to 5.7–6.1 only because the fixed window (centres t = 49–61) reaches 3–25 % deviation, where
  level 4 is still at 0.5–7 %.
- The L = 512 arm (level-3 resolution) gives 5.14–5.18 at small amplitude.
- So what the data show is agreement with τ_lin = 5.13 to about 1–2 % at small amplitude, at both resolutions, and
  growing nonlinear slowing at larger amplitude. Convergence toward GGS with resolution is not shown.

**A11 — l.372, the L=512 arm's 6 % gap (`clmFourLinearGap`) "consistent with … level-3-class resolution".**
- Its own small-amplitude growth (t = 10–22) gives H R₀ ≈ 1.30, which is the linear value.
- The 1.22 comes from a fixed-R₀ fit that runs to R/R₀ = 2.
- The Fig. 3 caption's "its onset is at the linear rate" sits next to τ = 5.7, against τ_lin = 5.13.

**A12 ✓ — l.357 and Fig. 3 caption (l.365), pure-quadrupole horizon "R 3.80 → 2.41, M_MS 1.90 → 1.24".**
- 2.41 and 1.24 are the t = 100 values. This run's trust window is t ≤ 60 (`trust_windows.tsv`, the user's own call).
- At t = 60 the values are R = 2.50 and M_MS = 1.25.

**A13 ✓ — l.352 and Fig. 2(d), the boosted throat "rising at most 2.0 %" at "t ≈ 29" (manual rows).**
- This is a one-sample scan glitch. All three scan centres jump at t = 29 (R_min 3.919 → 3.953 → 3.912), when the
  scan centre steps.
- The smooth maximum is about +1.2 % at t ≈ 24–26.
- The τ = 5.5–5.7 fit is anchored on the glitch; free-offset fits give 5.0–6.1.

**A14 — l.513, "the ε₂ = 0.01 burst stands only ≈2× above the spherical control's floor (Fig. 11(b))".**
- Fig. 11(b)'s own measure (rms over t = 30–50, R = 14) gives 5.2×, and the paper's gate-5 window gives 8×.
- The 2.1–2.3 comes from a maximum over t = 26–51 that the control's late junk dominates.

### Pairs and mergers (Secs. V–VII)

**A15 ✓ — l.429, l.434 and l.443, the head-on horizon: "from birth the horizon only shrinks", "monotone", "as the
first law … demands".** The joined `mots_spectral.dat` contradicts this:
- R rises 4.7862 → 4.8025 over t = 34–40 (+0.34 %).
- R rises 4.7734 → 4.7873 over t = 58–88 (+0.29 %).
- The end value, 4.7787, is above the t = 58 minimum.

The pack's own `first_law/…hfl…/VALIDATION.md` §5 attributes the t = 58 turn to shear. The per-row bound of
0.08 % is literally true.

**A16 — l.443, `clmHeadonCsmSlope` "by t = 90–100 … drifts at 3.2×10⁻⁴ per unit".** The extractor fits t = 51–100
and returns the absolute value. The signed slope there is +3.18×10⁻⁴, so R grows. Over t = 90–100 the slope is
−7.7×10⁻⁴.

**A17 — l.467 and Fig. 6, the d = 6 remnant "shrinking monotonically … a settled black hole", "settling from
above".**
- R rises over t = 29→36 (+0.21 %) and t = 54→81 (+0.38 %).
- At t = 100 it is still falling at −2×10⁻³ per unit, the steepest since t ≈ 29.
- So the 2.2 % head-on/d6 agreement is a snapshot.

**A18 ✓ — l.443 and l.445, `clmHeadonGwShare` "1.7 %" and `clmHeadonCsmScalarImplied` "0.039".**
- Both manual rows use E_GW = 0.0073, the pre-axis-fix value.
- With the printed E_GW = 1.2×10⁻² M_ADM = 0.029:
  - the GW share is 0.029 / 0.428 = 6.8 %;
  - the implied E_φ is 2.3573 − 2.3894 − 0.029 = −0.061.

**A19 — l.453, separations quoted past their trust windows** (the paper's own rule at l.455):
- p = 0.25 "recedes to 8.5 by t = 100". Its trust ends at 63.3, where the separation is 3.37.
- p = 0.45 "recedes to 5.3". That is the t = 100 value; trust ends at 67.6, where the separation is 2.62.

**A20 — l.460 and l.677, the p = 0.12 arm** (`lbf/…p012…_lb_csm`). Four separate problems:
- **The MOTS claim is unsupported.** "The finder holds no common MOTS on any plotfile" rests on a
  `mots_spectral.dat` that covers only t = 51–71 (21 of 72 plotfiles). Contact and the pit merger (t ≈ 37–38) were
  never searched.
- **The death is misdescribed.** "Dies of the interior failure at t = 71.78" does not fit: it is a global blow-up,
  with L2 H at 0.65 by t = 71 and 6×10¹⁰³ at the end. The NaN is on level 2 and the finest max|K| is 0.09. It comes
  15 units past its trust window (56.5).
- **It plunges.** Its pits close 12 → 2.05 by t = 37 and the trackers merge at t = 38.06. That contradicts
  "Below the plunge boundary the pairs scatter" and "the approach deepens with speed". The sequence is
  plunge (0.12), scatter (0.25, 0.45), plunge (0.60, 0.90).
- **It falls outside the circular-momentum fractions.** These use the unsoftened p_circ = 0.50; agents 3 and 5
  independently get p_circ ≈ 0.41 with the paper's own (d + δ)⁻² law, so "bracketing the circular value" fails too.

**A21 — l.481, the K wall's "knob is resolution".** The packed p = 0.90 level-5 continuation
(`…p090…lvl5from40_chi1e4…`) dies at t = 45.28. That is the same instant as level 4 (45.27): an h11 NaN on level 4,
with max|K| calm at 1.44. `trust_windows.tsv` itself says "level 5 does not move the death". Level 5 removed the K
runaway but not the death, and the paper omits this run. In the same sentence, `clmPNinetyChiMin` 5.4×10⁻³ has no
pack source; the packed global min χ sits on the floor (1.14×10⁻⁴ at the death).

**A22 — l.409, Fig. 4(b), "past t = 10.5, where the closing pair has eaten a tenth of its gap".** At t = 10.5 the
pair has closed 4.6 % of its gap (0.55 of 12.02). A tenth is reached at t ≈ 14.

**A23 — l.460, the inward scout "aimed straight at the companion".** Its params give `wormhole_momentumA = 0.24 0.06
0`, 14° off the line of centres; the params comment calls it a "small tangential twist". It stopped at t = 33.86, not
at its stop time of 40.

### Waves (Sec. VIII, IX.B–C)

**A24 (2×) — l.528, l.578, Figs. 7(d) and 8: fly-by energies and records past the retarded trust gate.** The paper
uses t − R ≤ 67.6 as the fly-by's trusted record (l.548, Fig. 13). But:
- `clmEgwEnergyFortyFive` 8.3×10⁻² is integrated at R = 20 to t = 94.17 (u = 74.2).
- The outer-sphere values run to u ≈ 71, and "the trough" at R = 28 is only the end of the record.
- Values at the gate:

| Quantity | Paper | At the gate |
|---|---|---|
| E(0.45), R = 20 | 8.3×10⁻² | 8.0×10⁻² |
| E(0.45), R = 28 | 8.2×10⁻² | 7.8×10⁻² |
| E(0.25), R = 28 | 3.95×10⁻² | 3.64×10⁻² |
| boundary / scatterer ratio | 2.2 | 2.1 |
| boundary / plunge ratio | 2.0 | 1.9 |

**A25 — l.506, the Fig. 8 caption's "common retarded window" is not common.** Every record ends at t = 100, so R = 44
covers u ≤ 56 while R = 20 covers u ≤ 74. The outer energies and the sphere spreads are therefore truncation
artifacts. On u ≤ 56 the spreads are:

| Record | Spread on u ≤ 56 | Quoted |
|---|---|---|
| Fly-by | 22 % | 41 % |
| Head-on | 23 % | 31 % |
| Merger | 15 % | 25 % |

So "fly-by 41 %, the widest" and "4.9×10⁻² at the outermost sphere" are truncated values.

**A26 ✓ — l.494, "outradiates it by 40–70×".** These manual rows were frozen from the superposed fly-by. On the
current pack the ratio is 8.3×10⁻² / 1.05×10⁻³ = 79 and 4.9×10⁻² / 1.05×10⁻³ = 47, i.e. 47–79.

**A27 ✓ — l.490, "Each record propagates … at v/c = 0.86–1.00".** The paper's own twin (0.82) and plunge (0.83) fall
outside this range. Also, "every speed here is a correlated lag" (l.533) is false for the plunge, which is a peak
lag.

**A28 — l.104 and l.578, "throat-mass units".** Every quoted energy is E / M_ADM of the whole source, which is
2.25–2.37 throat masses, as the Fig. 8 caption says. M also changes meaning within VIII.G–H:
- the fly-by's |E_φ| is in units of 2.2536;
- the head-on E_φ is in m = 1 units;
- the head-on E_GW / M is in units of 2.357.

**A29 — l.518, head-on E_GW is integrated to t = 100, through the level-1 noise the paper gates at t ≈ 80.** On
t ≤ 80 the values are 1.23×10⁻² (unchanged), 1.17×10⁻² and 1.05×10⁻². So "falling from 1.3×10⁻² to 1.1×10⁻²" should
read 1.2 → 1.0.

**A30 — l.573, "the merger's [frequency] … stays below its remnant's mode".** This is an estimator artifact (agent
analysis, not re-checked here). 20 % counter-rotating power biases the phase derivative to about 0.6 of the true
frequency. A co-plus-counter-rotating damped fit gives ω = 0.167–0.173, i.e. 426–443 Hz, at or above the remnant
ℓ = 2 mode (391–405 Hz).

### Detector and discussion (abstract, Secs. IX–X)

**A31 ✓ — l.595, "P ≈ 75–100", "1.8–2.7 periods".** `detector_pull_period(delta="max")` calls `single_offset_delta`
with its default `source="superposed"`, which gives δ = 3.78. With the paper's matched δ (2.2–2.8), P = 75–93 and the
low end becomes 2.0 periods.

**A32 ✓ — l.608, LISA SNRs "sky and inclination averaged … counting only each record's resolved band".** The four
burst-SNR rows use the extractor's default variant `"nominal"`: optimal orientation, instrument noise, whole record.
- Under the method the text states (conservative), the fly-by + merger range is 35–234, not 103–394, and the head-on
  range is 56–84, not 119–159.
- The lone-collapse "≈6" in the same paragraph is conservative. In the nominal convention it is 9.5, above 8.

**A33 — l.588, Fig. 9 caption "Ω_WH ≃ 60–800" (manual).** This is stale (it came from |E_φ|/M = 0.018–0.24). With the
caption's own inputs it is about 47–4600; as drawn, 54–3200.

**A34 — l.610, deposit ceiling "3×10⁻³" (manual).** This is stale. With the stated ratio of 3.7 it is 3.8×10⁻³; with
the figure's 3.2 it is 3.3×10⁻³.

**A35 — abstract l.90, the dipole is "switch[ed] off on the timescale on which the remnant's mass settles".** The body
never makes this comparison, and the data contradict it.
- Head-on: M_MS settles to 0.1 % by t ≈ 33 (e-fold 3–8 M), but the scalar envelope decays with τ = 20–32, 3–6× slower.
- d = 6: the mass settles by t ≈ 29, against τ = 22.

**A36 — abstract l.90, plus l.490 and l.528: "the scatterers … radiate the most … the output peaks at that
boundary".**
- The p = 0.60 plunge energy is a floor: its (2,2) envelope is still at 81 % of peak at the t = 80 cut. So
  E(0.45) > E(0.60) is not established; the body itself calls the ratio a ceiling.
- The plural "the scatterers" is false: p = 0.25 (0.0375) is below the plunge's floor (0.042).

---

## B — figures and captions

- **B1 (2×, ✓) — Fig. 12 (l.677) draws the wrong p = 0.12 run.** `plot_momentum_orbits.py:103` uses
  `05_binary_spiral/csm/v2_spiral_d12_p012_L128_lvl5from0_t100_csm`, the Bowen–York arm. It has no
  `momentum_model` key and is not in Table III (22.5 GPU-h uncounted). The caption says "boosted, solved data", and
  the text's arm is the `lbf/…_lb_csm` run. The drawn track ends at t = 36, while "pits merge near t = 38" is the lb
  run's number. `clmBoostFaceBias` (l.224) is measured on the same Bowen–York run.
- **B2 — Fig. 9(c), `plot_heavy_seeds.py:121`, hard-codes `SCALAR_RATIO = (0.8, 3.2)`.** The caption states 0.56–3.7.
- **B3 — Fig. 7 caption: head-on speeds "0.94 / 0.88 / 0.95", but the figure prints 0.90 / 0.88 / 0.95.**
  `extract_waves._series` correlates R = 10 → 14 → 18 → 20, while the figure uses 10 → 20 → 36 → 44.
- **B4 — Fig. 8(c): the head-on track turns up at its end.** It reaches a minimum of 410 Hz at τ = +10.8 M, then
  climbs to 587 Hz. "Reaches the QNM … by the end of its loud record" uses the minimum. The throat's track also rises
  at its end, and is drawn to t = 70, past its t = 58 gate.
- **B5 — Fig. 7(c), "the merger runs whole".** The d6 SERIES is a straight-line bridge over t = 25.5–30.01 on every
  sphere, and the real R = 28 data there read 29–30 % of peak. The numbers are unaffected (E 5.680 against
  5.668×10⁻³).
- **B6 — Fig. 8(d): the fly-by, head-on and merger spread ticks show the truncation spread** (A25).
- **B7 — Fig. 3 top and Fig. 10(c): the pure-quadrupole arm is drawn to t = 100 with no trust mark** (its t_max is 60).
- **B8 — Fig. 2(d): the moving-arm tag is anchored on the t = 29 glitch** (A13).
- **B9 — Fig. 1: the "throat" contour the module draws is the χ contour through x = 1.55** (`THROAT = 1.55`). The
  throat itself is at r_t = 1.618. The agreement shown is still genuine, because every contour contracts by 1/γ.

---

## C — imprecise or weak provenance

### Method (Secs. II–III)
- **l.275:** "shift started from zero" and "static lapse" are false for every exact-boost run, which starts from the
  boosted shift and lapse; Sec. II.E states this correctly.
- **l.217, the pair's mass:** "the pair's mass is the solve's M_ADM [Eq. madmvol]" is wrong for moving pairs, which
  use the boosted-background prescription.
  - The moving pairs weigh nearly the same at every p (2.233 / 2.254 / 2.229), against an expected 2.33 / 2.46 / 2.60.
    STATUS lists this as OPEN; the paper is silent.
  - "Eq. (madmvol) needs … time-symmetric data" should read "K = 0, Π = 0".
- **l.224:** the idle-solve bounds (`clmBoostSolveW/Wvec/Far`) come from a run that is not packed. The packed L = 128
  test reads max|w| ≤ 1.2×10⁻⁵.
- **MOTS finder:**
  - "rms residual below 10⁻⁶" is really the largest projected θ_out harmonic; the rms θ_out recorded is
    2.4×10⁻⁵ to 1.6×10⁻³.
  - ℓmax = 8 does not hold on orbits: the p060 lvl4 t040 leg ran 40 of 41 rows at ℓmax 6.
  - The Kerr–Schild self-test covers only the flow, at ℓmax 0 and 4.
- **Freeze exceptions:** the five t = 0.1 contraction runs are also unfrozen.
- **Damping exceptions:** `check_flyby_d12_p025` and DAMP-off are undamped.
- **NaN autopsy:** it is opt-in and on in only 31 of 109 runs, none of them orbital.
- **Scan edge:** the 2.79 depends on the consumer profile. The p = 0.45/0.60/0.90 fly-bys have no `horizon_scan.dat`.
- **Ψ4 coverage:** "Ψ4 on every binary" is false for the L = 64 binaries.
- **l.138, "two m = 0 throats do not attract":** for σ = −1, Eq. (force) gives an attraction a²/d². No run tests it.
- **Bit-reproducibility (`clmControlByteRows`):** the evidence is an archived pair. The pack holds only one build
  reproducing itself.
- **Manual sources that point at archived runs:** `clmBigBoxL`, `clmExtractRadius*`, `clmSponge*Big`,
  `clmMergerSign`, `clmFlybyScanEdge`, `clmSpiralMomentum*`, `clmHeadonSeparation`, `clmPairSeparation`,
  `clmCountLikeSignedPairs` and `clmSignSettleWindow`. The values re-verify on current runs.

### Single throat
- **Table IV, the lifetime law and the 22 ms example use τ = 5.9**, the e-fold the paper calls 15 % long. With τ_lin,
  22 ms becomes about 18–19 ms. The race e-fold counts use the level-3 τ for level 4–6 binaries (3.1/2.2/8 become
  3.4/2.5/9.1 with 5.26).
- **"A lighter throat is less stable"** holds only in code units. In its own mass units the hold times are equal
  (34.8 M against 35.3 M).
- **l.561:**
  - "falls by 30–100×": the raw drop is 86–108×; the 30 is a smoothing artifact.
  - "e-fold ≈ 5": the measured value is 4.4–4.6.
  - The box-doubled copy agrees to ≤ 2.7 % only over t = 50–80, and by 14–65 % before that.
  - "R settling 3.88 → 2.54" hides a dip to 2.334 at t = 47.
- **Fig. 2(c):** "Gold: exponential fits" are local e-folds of 3.95 and 4.48.
- **L = 512 arm:** its box H norm crosses 2.5×10⁻² at t = 151.5, and the θ_k claims for t = 162–212 sit on that
  stretch.
- **Pure-quadrupole lead:** 1.0–2.0 M, against the quoted 1.1–1.5.
- **Unkicked level-3 horizon numbers:** they come from the χ-regularised twin's scans.

### Pairs and mergers
- **"The mass is equal in all arms":** the one-body m′ is equal; M_ADM is not (like 1.566, against flip 2.274).
- **ε_eff −0.4 %** is the rest pairs' value. The moving d = 12 arms read −0.8 to −1.8 %.
- **Sign ratio:** 1.462 ± 0.022 comes from rounded columns; the unrounded value is 1.463 ± 0.023. The ± is the SD of
  15 autocorrelated points.
- **Seam "steps":** these are 1-unit row changes across gaps.
- **The scan is "11 % small" at t = 22 against t = 18;** at equal time it is 5.7 % small.
- **`clmHeadonCsmRateFold`:** it uses mean |rate| over a sign change.
- **"σ_KO = 1.0 delays the cell by a unit"** compares level 5 with level 6.
- **"Single-cell" NaN:** the head-on autopsy shows 3 cells, which is its cap; the d = 6 runs have no autopsy.
- **The p = 0.25 finder** covers t = 43–100 only.
- **"Both failures are censored"** is false for p = 0.60 and 0.90; the next paragraph qualifies it.
- **Fig. 10(f) "norms at or below their start"** holds for H only; M rises.
- **Fig. 10(g):** the level-5 "rides clean" while its max|K| climbs ×8.

### Waves
- **Censorship crests:** `clmGwCensCrestOuter` / `clmGwCensMergerCrest` print 39; the recorded extractor gives 38.
- **Head-on R = 10 E_φ:** it includes the t = 18–26 ingoing flux (+0.022) that the text says is excluded. From
  t = 26 the values are −0.052 / −0.060 / −0.064.
- **τ fits past the t ≈ 80 noise:** fitted over 30–80 instead, the τ values are 22 / 38 / 73.
- **Scalar QNM fit:** it is robust only at R = 10; at R = 14/18 the damping is 13–49 % slower.
- **Flux-envelope τ** of 20–32 does not follow from ω_I = 0.037, which predicts about 13.5.
- **"About one dipole period"** for 25 units: the dipole period is about 51.
- **Fly-by scalar crests** imply 1.23c between R = 14 and R = 30.
- **The memory range** mixes windows.
- **BBH normalisation:** E/M uses M = 2.0, not the Brill–Lindquist 1.889 (giving 5.9×10⁻⁴ and a ratio of 20×). The
  twin also uses 2.0, although its caption says "own total ADM mass".
- **`clmBbhHeadonAmpRatio`** compares R = 10 with R = 14.
- **`clmGwScalarFluxFactor` 0.94** comes from an archived run's analytic data.
- **`clmFlybyTrustRetarded`'s source** mis-cites `trust_windows.tsv`.
- **"10 % floor":** the R = 10 record is drawn to t = 58, where the floor is 14 %.
- **"A little above 2M_ADM"** (l.550): it is the mass that is above M_ADM, and the radius that is above 2M_ADM.
- **"Not monotone in p"** rests on the plunge's floor.

### Detector and discussion
- **Ω_GW "10⁻¹³–10⁻¹²":** it pairs n_min with the larger energy; the true span is 2.1×10⁻¹⁴ to 4.6×10⁻¹².
- **PLS threshold:** it holds for 10⁵–10⁶ M⊙ only (71 Mpc⁻³ at 10⁴ M⊙).
- **(fM)_peak 0.042** is the lone throat's; the encounters span 0.048–0.071.
- **"Within 11 ms":** the maximum is 11.47 ms.
- **The plunge horizon "upper bound":** the reason is its trust cut, not the integration.
- **Abstract "born with their combined area":** 1.05×.
- **Abstract "collapse … resolvable by LISA":** a lone collapse reaches SNR 6.4 at most.
- **The Sec. X.C population argument** assumes like-signed pairs meet lone fates, against Sec. VII.B's companion
  squeeze.
- **`clmInfEfoldBoundary`** is read at t = 212 but quoted "by t = 218".
- **GPU-hours provenance:** `gpu_hours.py` prints 608.6 h (109 runs) labelled "the article's number", and the ledger
  source still cites 646 + 349. The 476 itself, the 96-run subset, reproduces.

## D — cosmetic

- **Fig. 2(b):** the caption says "deviation from R⋆", but the axis is |R − R₀|/R₀.
- **l.352** cites Fig. 2(a) for the moving arm, which appears only in panel (d).
- **"+0.1 trapped from the first scan (t = 1)":** a t = 0 scan exists.
- **Table IV** converts the rounded τ.
- **Fig. 2(c):** the ±0.1 crosses sit at the last reading, not at the death times.
- **Fig. 5(c):** the "level 5" tag is clipped by the spine.
- **Figs. 4 and 12** use in-frame keys.
- **Fig. 12:** the scatterer tracks have no end dot.
- **Fig. 10(g):** the level-5 grey dash is hidden under the ink.
- **Rounding:** 36.67 is printed "36.6", 3.453 is printed "~3.4", and the growth time is 520 against a computed 518.
- **"58 of the 80 GB":** this mixes GiB and GB.
- **Fig. 9(c):** the cap is captioned "dashed" but drawn dotted.
- **Fig. 13:**
  - The legend repeats line styles.
  - Panel (c) has a y-axis to 10³ for data ≤ 10⁻².
  - The axis of "ℓ = 1, m = 0" is not stated.
- **Label audits:** `plot_psi4_ligo`, `plot_scalar_channel` and `plot_scalar_censorship` never call `label_audit`.
- **Seed-defect peak:** 0.927 (+10⁻²) against 0.944 (−10⁻²), quoted as one value, 0.93.
- **Layout:** Fig. 3 overflows its page by 0.6 pt in both engines, against the half-page strip rule.
- **Stale notes:** `table1_groups.tsv` (`spiral_d12_pin025` "not counted"), the `extract_detector` docstring
  (144/12/132), the p060 SERIES README ("burst peak" 7.0×10⁻² is post-trust junk), and several "ARCHIVED" notes on
  auto rows.

## Unverifiable or not reached

- **Literature:**
  - 24 lit rows were not fully audited. Witek 2010 (5.5×10⁻⁴), Scheel 2009 and Berti 2009 were checked and are fine.
  - Not checked: the GGS Table I values, Damour 2014, the LRD densities and the FIRAS range.
- **No packed source:**
  - `clmBoostSolveW/Wvec/Far` and `clmBoostRestRepro` (runs not packed);
  - `clmBoostPairShellHam` (no per-level record);
  - `clmControlByteRows` (archived run);
  - `clmNormPitShare`, `clmRaceKickTwelve` and `clmGwSingleCountTime` (all sourced from the deleted GPU_PLAN);
  - `clmPNinetyChiMin`.
- **Search:** "the highest is a plunge recovered by a heavier rung" (`injections.json` does not record the rung).
- **Hardware:** the H100 80 GB device string and the octant speeds 28–74 u/h (the raw logs are not on the
  workstation).
- **Priority claims:** "first NR evolutions of wormhole binaries" and "first GW signal from a wormhole collapse".
- **Needs plotfiles:** "the floor acts only inside the horizon" and "starts on the refinement boundaries".
