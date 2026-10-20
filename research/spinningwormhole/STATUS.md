# Spinning-wormhole campaign — status

Compacted 2026-10-19 ≈ 18:30 MSK. The full earlier text (run-by-run start checks, the bug hunt step by step, the
pre-fix ledger) is `git show 57c23b77:research/spinningwormhole/STATUS.md`. Plans: [`SpinningWormhole.md`](SpinningWormhole.md)
(paper), [`SpinningSolver.md`](SpinningSolver.md) (solver, done). Code: `Examples/SpinningWormhole/`,
`grteclyn-wrapper/scripts/campaigns/spinning_wormhole/`. Runs: `runs/spinning_wormhole/drainhole/00_paper_runs/`
(launch `--subdir drainhole/00_paper_runs`, pack `research/spinningwormhole/pack_run.sh drainhole/00_paper_runs <run>`).
Packs: `results/spinningwormhole/` (`runs_registry.tsv`: one outcome line per run; `trust_windows.tsv`). Branch
`feature/spinning`, pushed to `myfork`.

## RESULTS SO FAR (2026-10-20)

Spin slows the instability and the 0.9c is stable. Up to the 0.40c (24 % of extremal) the unperturbed throat
collapses into a black hole. At the 0.46c (29 %) and the 0.5c (33 %, N 128) it shrinks a little, turns, and then
inflates, growing as e^(t/τ) with τ ≈ 10–12: the instability's other branch, not its end. Where it ends lies between
33 % and 81 %; the 0.6c / 0.7c runs on the fast recipe broke down numerically at the far-side centre — not the
box: σ 0.4 kills these negative-mass centres (with min_chi 1e-4 slowly, deaths at 85–136; with 1e-8 by t ≈ 33).
The 0.6c and the 0.7c rerun on the slow recipe (σ 0.1, min_chi 1e-8) on L 128 (LIVE since 10-20 17:43).
Correction (10-20): on 10-19 the 0.46c's turn at t 83 was read as the end of the instability near Azad's ≈ 30 %; the
t 150 run shows its throat inflating from t 101.

- **Collapse is delayed by spin.** The throat reaches −1 % at t 43.7 (static), 46.9 (0.2c), 51.4 (0.30c) and 60.2
  (0.40c); the 0.5c on N 192 (drive on) reached −1 % at t 99.4, and the 0.9c stays flat to t 150 at all three
  resolutions.
- **The 0.46c and the 0.5c inflate.** The 0.46c's areal throat radius peaked at −1.12 % at t 83, crossed zero at
  t 101 and grew to +6.8 % at t 121 (its trust window; +15 % at t 130, NaN at 130.23); the 0.5c on N 128 turned at −0.30 % (t 65–68) and grew to +1.98 / +3.86 /
  +6.89 % at t 90 / 95 / 100. Their growth from the throat's speed dR/dt: τ ≈ 8–12 (0.46c) and 9–11.5 (0.5c); the
  0.40c's collapse 12–13.6 on the same measure. The MOTS is lost once a throat expands (0.46c from t 104, 0.5c from
  t 78). The N 192 / drive-on 0.5c went the collapse way: the seed's sign picks the branch (the kicks' sign rule).
- **Instability curve** (`figures/instability_curve.png`, `plot_instability_curve`; remeasured 10-20, models D0–D90):
  every τ is now the offset-free fit, the slope of ln|dR_A/dt| over the first 0.2–1 % pass of the deficit (collapse)
  or growth (expansion). The old deficit-band fit carried the early transient's baseline (1e-4 at N 96 vs 4e-6 at
  N 192), biased τ short by a resolution-dependent amount and failed to self-converge (Q_meas < 0); the offset-free
  fit gives τ 7.8 / 6.6 / 6.1 on the 0.2c triplet, Q_meas 2.3 between the order-3/4 expectations 1.95 / 2.69,
  continuum 5.9 (Richardson AT the measured order p 3.5; extrapolating at p 2 gives the earlier 5.5–5.7, wrong
  order), and sits on a band plateau (< 4 % between 0.2–1 % and 0.5–2 %). Collapse dots τ 5.4 / 6.6 /
  8.3 / 13.3 (D0–D40), expansion triangles 12.1 / 8.8 (D46, D51). The fit a − b(J/A)² now goes through the collapse
  branch ALONE (rms 2e-3): zero at 32 %; one curve through both branches described neither. The D59 / D70 rungs
  point at the σ 0.1 L 128 reruns (`sig01_mc8`) and the curve refills as they land.
- **Against Azad et al.** (Azad, Blázquez-Salcedo, Khoo, Kunz, arXiv:2301.05243; their C = 1 row — our family):
  where 2nd order should hold the methods are close — D21 continuum 5.9 within 8 % of their 5.46, static 5.4
  (N 128) beside the linear 5.13; at intermediate spin ours is slower beyond the ~13 % resolution bias (8.3 vs 6.1
  at 0.30c, 13.3 vs 8.0 at 0.40c), as expected if the dropped O(J⁴) terms matter. The collapse-branch fit
  extrapolates to zero at 32 % (last collapsing model 24 %), beside their J_c
  (33 %) and conjectured crossing (≈ 30 %); the 0.46c / 0.5c expand with RISING rates (τ 12.1 → 8.8), consistent
  with their second mode taking over, not the modes merging away. The old "matches within 3 %" was the deficit-fit
  bias cancelling their truncation. Kleihaus & Kunz (2014) left 4D stability open; our 0.9c is stable.
- **End state.** The low spins collapse into a black hole: the horizon settles at R 2.52 (0.2c) and 2.57 (0.30c,
  2.567 at t 130); the 0.40c's MOTS leaves the throat at t 92 and reads R 3.22 at t 100, still shrinking. The static
  died just after its horizon formed, the 0.40c at t 100.7 in its collapse.
- **Gravitational waves.** The 0.2c's collapse emits a (2,0) burst, r·Δψ4 ≈ 2e-4: one waveform from R 14 to 45, at
  the speed of light, ring-down period ≈ 24 (the L 128 far-zone run, `figures/farzone_wave_02c.png`).
- **Larger spin, stronger wave, same shape.** Aligned on each run's own collapse (u = t − R − t₁₀, t₁₀ when R_eq is
  −10 %), the 0.2c N 128 / N 192 / L 128 overlap at R 10 / 14 / 18 (at R 14: trough −1.47e-4 at u ≈ 13, peak +2.3e-4
  at u ≈ 24). The 0.30c has the same shape and timing, bigger: its first lobe ≈ 1.5×, its R 14 trough −1.9e-4 and
  still deepening when it stops at t 100. The first lobe falls with R (near field); the trough is flat from R 14
  (the radiation). The static is flat at ≤ 3e-8 (a spherical collapse emits no quadrupole wave). No burst in the
  rest: the 0.2c N 96 and the push-out died before theirs reached R 10, the 0.40c t 150 at t 100.7 in its collapse.
  The 0.30c t 130 caught its whole burst: at R 14 trough −1.9e-4 (u ≈ 14), peak +3.4e-4 (u ≈ 26), second trough
  ≈ −1.4e-4; identical to the t 100 run up to t 100.
- **Radiated energy grows with spin** (10-20): E₂₀ = 1/(16π)∫|∫r ψ4 dt′|² dt over the aligned burst (u 0–45),
  per M_ADM: 0.2c 3.3e-7, 0.30c 8.0e-7 at R 18 (R 14: 2.5e-7 / 7.5e-7) — 2.6–2.8×, the square of the 1.5×
  amplitude; the static is zero by spherical symmetry (its run: ≤ 4.2e-9 to its death). `farzone_wave_02c.png`
  redesigned 10-20: (a) the 0.2c wave at R 14–45, (b) the wave against spin aligned on each collapse, (c) E₂₀/M_ADM
  against 8πJ/A, (d) the extrema's speed against light; axis labels carry only the quantity, the dropped panels'
  numbers (throat–box agreement ≤ 3.2e-4, extrema flat in R to 1.5 % over R 30–45) go to the caption.
- **Kicks.** The sign of the push decides the fate, the merger paper's rule: pushed in, the throat inflates; pushed
  out, it collapses. Both pass 1 % at t ≈ 25, 21.5 before the unkicked 0.2c, at the same rate. No more kicks.
- **Numerics.** The 0.2c triplet converges at 3rd–4th order, the 0.9c triplet is stable at every resolution, and the
  code review (10-19) found nothing that changes these results.
- **The far-side centre (10-20).** σ 0.4 kills the centre of the negative-mass far sides (0.46c–0.7c: μ₋ −0.72 …
  −0.11, central χ ≈ 4e-7 at t 0); the 0.9c survives it because its far side has positive mass (+2.09): its central
  lapse collapses gently and freezes the centre. With min_chi 1e-4 the floor slows the damage — the central lapse
  falls 0.21 → 0.04 → 0.003 by t 40 / 80 on the same curve at L 64 and L 128, the constraints grow ×100 from t ≈ 40–50,
  deaths at 84.81 / 99.16 / 136 (0.5c / 0.6c L 128, 0.7c L 64). With min_chi 1e-8 it is fast: χ on the floor by t 5,
  |K| at r ≈ 0.2 growing from 9e-4 (t 5) to 0.4, the lapse on its floor at t 27–30, NaN at 32.36 / 34.33 (0.7c /
  0.6c). Every healthy centre ran σ 0.1 (0.2c–0.5c: χ ~ 1e-6, K ~ 5e-3 at t 30); the old 0.5c with σ 0.4 + 1e-8
  had χ on the floor and K 0.2 by t 30. The throat never moved in any of these (≤ 0.006 % before the breakdown).
  The paper's recipe F (and its box explanation) holds for the 0.9c only.

## MAIN RESULTS TABLE

L 64, N 128, slow recipe unless noted. −1 %: the equatorial throat radius R_eq (`throat_geometry`; the kicks against
the unperturbed throat). τ_A: the curve's fit to the areal-radius deficit over 0.2–1 %. τ_p: the proper time on the
throat's equatorial ring (∫α dt, lapse from the slice cache) over R_eq −1 → −10 %. Azad's τ at the rungs (their C = 1
row): 5.13 / 5.46 / 6.1 / 8.0 / 13.2 (static → 0.46c), zero at J 4.03 (33 %).

| rung | J/A (% ext.) | −1 % at t | τ_A | τ_p | end | trust |
|---|---|---|---|---|---|---|
| static | 0 | 43.7 | 4.4 | 2.96 | DIED 62.67, after its horizon formed | 60 |
| 0.2c (N 96 / 192: 3.57 / 3.13 τ_p) | 12.3 | 46.9 (N 192: 57.8) | 5.0 | 3.28 | horizon R 2.524, M_MS 1.262 | 100 |
| 0.2c push out (l 0, ε +1e-3) | 12.3 | 25.3 | – | 3.03 | DIED 44.08, after its horizon formed | 42 |
| 0.2c push in (l 0, ε −1e-3) | 12.3 | +1 % at 25.6 | – | 3.06 | inflates, +105 % at t 60 | 61 |
| 0.30c | 18.3 | 51.4 | 5.9 | 3.76 | horizon R 2.571, M_MS 1.286, settling | 100 |
| 0.30c to t 130 `spin_hold_L64_ml3_ve030a_spdrv0_farfix_t130` | 18.3 | – | – | – | FINISHED t 130 (10-20 ≈ 07:12): the whole burst (R 14: trough t 98, peak t 110, second trough ≈ 120); horizon R 2.567 at t 130. Not packed (value check) | – |
| 0.40c | 24.4 | 60.2 | 8.0 | 5.03 | horizon forming: MOTS off the throat from t 92, R 3.223 (M_MS 1.612) at t 100 | 100 |
| 0.40c to t 150 `spin_hold_L64_ml3_ve040a_spdrv0_farfix_t150` | 24.4 | – | – | – | DIED 100.72 (h11 NaN, finest level) in its collapse, before its burst reached R 14. Decided 10-20: no third wave point needed (the 0.2c and 0.30c carry the wave claim); not packed, nothing beyond the t 100 run | – |
| 0.46c | 28.8 | never (−0.92 % at 82) | 15.2 (the early shrink) | – | no collapse to t 100: areal −1.12 % at t 83, −0.21 % at t 100; then inflates (t 150 run) | 100 |
| 0.46c to t 150 `spin_hold_L64_ml3_ve045a_spdrv0_farfix_t150` | 28.8 | – | – | – | DIED 130.23 (10-20 09:01; h11 NaN, finest level): inflated from t 101 to +1.8 / +6.2 / +15 % at t 110 / 120 / 130 (τ 12.1); the finest level's Mom leaves its 1.9e-3 plateau at t 121.4, the lapse on its floor from t 127. Packed, trust 121 | 121 |
| 0.5c (N 192, drive on) | 33.3 | 99.4 | 13.6 | – | clean t 100, MOTS −1.3 %, no horizon | 100 |
| 0.5c on N 128, drive off, to t 150 `spin_hold_L64_ml3_ve050a_spdrv0_farfix_t150` | 33.3 | – | – | – | DIED 100.10 (K NaN, finest level): inflated from t ≈ 70 to +6.9 % at t 100 (τ 9–11.5 from dR/dt), MOTS lost from t 78. Packed, trust 95 | 95 |
| 0.5c on L 128 `spin_hold_L128_ml3_ve050a_spdrv1_sig04_farfix_t150` | 33.3 | – | – | – | DIED 84.81 (10-20 13:32; h11 NaN, finest level): the χ floor (min_chi 1e-4) — central lapse 0.003, constraints ×100 from t 50, throat flat (≤ 0.14 %) to t 69 then a shrink 3–5× faster than the mode (−4.4 % areal at t 84): numerical. Not packed, not usable; not rerun (decided 10-20: the L 64 runs cover the rung) | – |
| 0.6c (fast) `spin_hold_L64_ml3_ve060a_spdrv0_mc4_sig04_farfix_t150` | 40.3 | – | – | – | DIED 98.99 (K NaN, finest level): the χ floor (read on 10-19 as the box) — central lapse ≈ 0 from t 38, throat flat (≤ 0.2 %) only to t 75. Not packed, not usable | – |
| 0.6c on L 128 `spin_hold_L128_ml3_ve060a_spdrv1_sig04_farfix_t150` | 40.3 | – | – | – | DIED 99.16 (10-20 14:09; h11 NaN, finest level): the χ floor, as the 0.5c L 128 — central lapse 0.003 and constraints 2e-3 at t 80, throat −2.1 % areal / −47 % R_eq at the end. Not packed, not usable; rerun below | – |
| 0.6c on L 128, min_chi 1e-8 `spin_hold_L128_ml3_ve060a_spdrv1_sig04_mc8_farfix_t150` | 40.3 | – | – | – | DIED 34.33 (10-20 17:27; h11 NaN): σ 0.4 at the far-side centre — χ on the 1e-8 floor from t 5, |K| there 9e-4 → 0.4, the lapse on its floor at t 30; throat flat (≤ 0.0033 %). Not packed, not usable | – |
| 0.6c on L 128, σ 0.1 `spin_hold_L128_ml3_ve060a_spdrv1_sig01_mc8_farfix_t150` | 40.3 | – | – | – | LIVE since 10-20 17:43 (1st / 0, alone): the slow recipe (σ 0.1, min_chi 1e-8) on the L 128 setup; only σ 0.4 → 0.1 vs the dead run (diffed) | – |
| 0.7c (fast) `spin_hold_L64_ml3_ve070a_spdrv0_mc4_sig04_farfix_t150` | 51.4 | – | – | – | DIED 136.03 (h11 NaN, finest level), as the archived 0.7c (135.85): the χ floor (read on 10-19 as the box) — central lapse ≈ 0 from t 39.5, throat ±0.8 % to t 124. Not packed, not usable | – |
| 0.7c on L 128 `spin_hold_L128_ml3_ve070a_spdrv1_sig04_farfix_t150` | 51.4 | – | – | – | STOPPED 107.65 (10-20 15:27, on the word): the χ floor, as the 0.5c / 0.6c L 128 — throat flat (≤ 0.006 %) to t 70, then the central lapse reached 0, the finest-level constraints 1.6e-3 (100× the 0.9c's) and the throat swung +0.18 % (t 100) → +0.03 % (t 106). Not packed, not usable; rerun below | – |
| 0.7c on L 128, min_chi 1e-8 `spin_hold_L128_ml3_ve070a_spdrv1_sig04_mc8_farfix_t150` | 51.4 | – | – | – | DIED 32.36 (10-20 17:33; A11 NaN): σ 0.4 at the far-side centre, as the 0.6c — the lapse on its floor at t 27, |K| there 4.2 at the end; throat flat (≤ 0.0006 %). Not packed, not usable | – |
| 0.7c on L 128, σ 0.1 `spin_hold_L128_ml3_ve070a_spdrv1_sig01_mc8_farfix_t150` | 51.4 | – | – | – | LIVE since 10-20 17:43 (1st / 1, alone): the slow recipe on the L 128 setup; only σ 0.4 → 0.1 vs the dead run (diffed) | – |
| 0.9c (L 128 triplet, fast) | 80.8 | flat to t 150 | ∞ | – | stable: areal R drift ≤ 7e-5, no MOTS | 150 |

ψ4 (2,0), r·Δψ4 at R 14 (u as above): 0.2c trough −1.47e-4 (u 13), peak +2.3e-4 (u 24), ring-down period ≈ 24 (L 128,
flat in R to 1.3 % over R 30–45); 0.30c first lobe 1.0e-4 (0.2c 6.5e-5), trough ≤ −1.9e-4 (cut at t 100); static
≤ 3e-8.

## LIVE (MSK; no checkpoints)

| run | node / card | t | stop | speed | ETA |
|---|---|---|---|---|---|
| 0.6c L 128, σ 0.1 `spin_hold_L128_ml3_ve060a_spdrv1_sig01_mc8_farfix_t150` | 1st / 0, alone | 0 @ 17:43 | 150 | ≈ 15.5 t/h | 10-21 ≈ 03:30 |
| 0.7c L 128, σ 0.1 `spin_hold_L128_ml3_ve070a_spdrv1_sig01_mc8_farfix_t150` | 1st / 1, alone | 0 @ 17:43 | 150 | ≈ 15.5 t/h | 10-21 ≈ 03:30 |

- The σ 0.1 reruns (go 10-20 ≈ 17:40, no checkpoints): the dead min_chi 1e-8 reruns' templates with only the name and
  σ 0.4 → 0.1 changed (diffed); preflights pass, t 0 constraints identical to every earlier run of each rung. The
  centre's fate shows by t 5–10 (the σ 0.4 + 1e-8 runs had χ on the floor by t 5). Consumer args as before (ψ4 R 14
  18 30 40 45, MOTS steps 150). The second node's card is idle.

- The L 128 reruns (go 10-20 ≈ 07:30, no checkpoints; decided: the 0.7c shares card 1 with the 0.46c now): preflights
  pass, t 0 constraints at N 256 (Ham 5.1e-4 / 6.1e-4) below the L 64 runs' (2.1e-3), consumer args the 0.9c's
  (ψ4 R 14 18 30 40 45, MOTS steps 150).
- Ended 10-20: the 0.6c / 0.7c L 128 σ 0.4 + min_chi 1e-8 reruns (DIED 34.33 / 32.36 at 17:27 / 17:33, the far-side
  centre; not packed; scratch pruned ≈ 17:45), the 0.7c L 128 (STOPPED 107.65 at 15:27 on the word, the χ floor; not
  packed; scratch pruned ≈ 15:30), the 0.5c / 0.6c L 128 (DIED 84.81 / 99.16 at 13:32 / 14:09, the χ floor; not packed; the 0.6c's
  scratch pruned ≈ 15:20, the 0.5c's 15 GB still on the second node's scratch), the 0.46c t 150 (DIED 130.23 at 09:01, inflating, h11 NaN on the finest level; packed, trust 121;
  scratch pruned ≈ 11:15), the 0.30c t 130
  (FINISHED, packed, trust 130), the 0.5c t 150 (DIED 100.10 inflating, packed, trust
  95), the 0.40c t 150 (DIED 100.72, not packed: no third wave point needed), the 0.6c / 0.7c L 64 (DIED 98.99 /
  136.03, not packed: the χ floor, read then as the box). First-node scratch pruned of the three dead L 64 runs'
  plotfiles (21 GB, ≈ 07:50); the second node's (0.30c t 130, 0.40c t 150, 14 GB) wiped ≈ 08:00 before the 0.5c L 128
  launch. The keepers' movies (0.30c t 130 to t ≤ 130, 0.5c t 150 to t ≤ 95; full + core) rendered on the second
  node and checked on contact sheets 10-20 ≈ 08:40: one fixed scale per field, none blank, both stop at their
  trust windows.
- The 0.5c L 128 (go 10-20 ≈ 08:00, no checkpoints — the 0.9c settings as given): preflight pass, t 0 constraints
  Ham 5.0e-4 / Mom 4.5e-5 (the L 128 family's level), ≈ 13–15 t/h alone on the second node's card.
- The 0.46c t 150's consumer lagged while its MOTS search fails on the growing throat; restarted 10-20 ≈ 07:35 with
  `--mots-spectral-steps 150` (`restart_consumer.sh --busy`).
- Level 1 rises from t ≈ 90 in every L 64 run (the 0.30c t 130: 3.7e-6 at t 130, still clean); in the fast 0.6c /
  0.7c the finest level ran away first, after the central lapse had sat at ≈ 0 since t ≈ 40.
- Done and packed 10-19: the static, the 0.30c, both 0.2c kicks, the 0.2c N 192, the L 128 far-zone run, the 0.5c
  N 192, the 0.40c and 0.46c t 100 (19:54). Every movie of these and of the static and 0.30c checked on contact
  sheets (10-19 ≈ 21:30): fixed scales, none blank. The first node's scratch was pruned of the 0.40c / 0.46c last
  plotfiles (14 GB, ≈ 20:10).
- The 0.30c t 130 and 0.40c t 150 (go 10-19 ≈ 18:40; decided: both on the second node's card now rather than the
  0.40c alone on the first node's card 1 from 19:50) are the 0.30c / 0.40c rungs' own params with only the name and
  the stop changed (diffed); t 0 constraints and R_eq identical to the t 100 runs. The second node's scratch was
  wiped of the kicks' last plotfiles (14 GB, 10-19 ≈ 18:40).
- The 0.5c N 128 drive off to t 150 (go 10-19 ≈ 19:10, no checkpoints) started at 19:54 on the first node's card 1,
  launched by a watcher the moment the 0.40c / 0.46c t 100 exited. Template: the 0.40c t 150's params with the 0.5c
  table (diffed: against the N 192 run only N, plot_interval, drive, name and stop differ). t 150 rather than 100: the
  0.46c's throat turned at t 83, so t 100 may not show whether the 0.5c collapses.
- The 0.46c to t 150 (go 10-19 ≈ 20:13, no checkpoints) is the 0.46c rung's own params with only the name and the
  stop changed (diffed). Decided 10-19: it shares card 1 with the 0.5c now rather than starting alone after it (that
  would have ended the 0.5c ≈ 03:15 and the 0.46c ≈ 10:35).
- Queue: empty. Cancelled 10-19: the 0.2c bar and the three 0.30c kicks (both rungs collapse anyway; templates stay).

## RUNS FOR THE PAPER (proposed, no go yet)

No proposed run (decided 10-20: keep and pack the 0.30c t 130, the 0.5c t 150 and the 0.46c t 150; no 0.40c wave
rerun — the 0.2c and 0.30c carry the wave claim). The 0.46c t 150 is packed (died 130.23, trust 121). Decided 10-20
after the far-side-centre deaths: the 0.6c and 0.7c rerun on L 128 with the slow recipe (σ 0.1, min_chi 1e-8; LIVE
since 17:43, after their σ 0.4 + 1e-8 reruns died at 34.33 / 32.36) for "flat to t 150" points beside the fit's zero;
the 0.5c is not rerun (its L 64 runs cover the rung); the dead L 128 rows leave the paper's table.
Free analyses:

| analysis | what it settles | cost |
|---|---|---|
| two-mode refit of the 0.46c / 0.5c | Azad's second mode near the mode crossing | free |
| horizon mass integral | the 0.2c's settled M_irr 1.262 against the exterior's ≈ 1.16 | free |

## THE PAPER

Claims (decided 10-18):
1. **Stability at fast spin**: the 0.9c farfix triplet holds to t 150.
2. **Stability grows with spin**: the ladder static → 0.9c; τ(J) against Azad et al.
3. **A GW signal with no nonspherical perturbation**: the rotating collapse radiates (2,0) from unperturbed data (the
   far-zone 0.2c), more with more spin; the static radiates nothing.

Paper notes:
- **τ**: quote one definition, the areal-radius fit over 0.2–1 %. The coordinate rate depends on the throat lapse at
  the collapse (0.52–0.56), so the coordinate τ of the triplet does not converge and the proper one does. Azad's τ is
  a linear mode in Killing time: the comparison is close, not like for like.
- **Azad's numbers**: J/A from each table's meta, as a fraction of extremal Kerr's 1/(8π). Their second-order zero is
  J 4.03 = 33 % on this axis; their "≈ 50 %" uses their approximate throat area. Their ≈ 30 % end is a conjecture.
- **Physicality**: J/M² bulges mid-family (0.5c 1.19, 0.7c 1.11, 0.9c 1.013); only J/M² < 1 is astrophysical,
  v_e < 0.29c on this family.
- **Exotic matter**: D/M falls 2.22 → 1.07 → 0.52 → 0.09 → 0.02 at v_e 0.06 / 0.51 / 0.70 / 0.90 / 0.96 (family (a)
  tables): rotation replaces the phantom field as what holds the throat open. The scalar charge is measured on the
  grid (t 0 to 2e-4; the static drains D by 38 % by t 64, pre-fix: requote).
- **Speed-up research** (dt × σ, 10-16, "goes fully to the article"): the dt ceiling was an AMR interface mode on
  the coarse–fine edges, where bugs 2–3 acted; retest dt 0.05 on the fixed binary before quoting it.
- **Figures**: all four are cited since the 10-20 rewrite — `instability_curve` (Fig. in Sec. V),
  `farzone_wave_02c` (claim 3, figure*), `convergence_02c` / `convergence_09c` (Appendix B). The wave-against-spin
  panel lives inside `farzone_wave_02c` (panel b).
- **Figure data** (10-20): every figure rebuilds from tracked `results/` (pixel-identical, checked). The eight table
  headers are in `results/spinningwormhole/backgrounds/` (`headers`), and Fig. 5's light speed is in the far-zone
  pack's `light_speed_equator.dat` (`plot_farzone_wave --light-from-cache` rebuilds it). Fig. 4's live rungs
  (0.6c, 0.7c) arrive with their packs at close-out; the 0.46c is packed.
- **`article/research.tex` rewrite 10-20** (the structure the draft now has): Sec. IV = "Numerical setup" with
  subsections (3D initial data / Evolution scheme / Long evolutions: the outer boundary / The runs); tab:ladder is
  the full 13-row run table (settings + trust + outcome, live runs marked "running"); Table I (backgrounds) moved
  to Appendix A; Appendix B = the two convergence figures; Sec. V requoted from the farfix runs (τ 4.4/5.0/5.9/8.0,
  the two branches, Azad comparison, GW energies); acknowledgments carry the Gravity Frontiers note. Text states:
  no speed-up adopted — dt 0.02 Δx everywhere, only σ varies (0.1 slow / 0.4 fast); the sponge-zone updates
  (background-relative Sommerfeld + damping layer) are what carry the L 64 runs past t ≈ 64.
- **`article/research.tex` fixes** (code review 10-19): the dropped 1/η₀ in ψ — FIXED 10-20; the pseudo-arclength
  fallback the code does not have — REMOVED 10-20; the two double-rounded Table I digits — still open (the table
  now sits in Appendix A; recheck against the family TSV legs when the ledger is built). Every evolution number is
  requoted from the farfix runs; the pre-fix numbers are archived.

## SETTINGS

- Grid: L 64, N 128, max_level 3 (dx 0.5 → 0.0625), centre 32, KO sponge 24–32, dt_multiplier 0.02. The sponge drive
  is off for every run since 10-18 (`sponge_drive_strength = 0`).
- SLOW (≤ 0.5c): σ 0.1, min_chi 1e-8, stop 100. FAST (> 0.5c): σ 0.4, min_chi 1e-4, `constraint_norms_mask_radius =
  0.75`, stop 150; the 1e-4 floor is what carries > 0.5c.
- **A rung's box is picked by its M_ADM, not by habit** (10-20, after the L 64 0.6c / 0.7c died of central gauge
  collapse): M_ADM triples along the family (0.2c 1.26 → 0.6c 2.30 → 0.7c 3.31 → 0.9c 11.7), so the L 64 face falls
  from 25 M of clearance at the 0.2c to 13.9 / 9.7 M at the 0.6c / 0.7c, while the L 64 recipes were validated only
  at ≥ 17 M (0.2c–0.5c). From the 0.6c up, a run gets the 0.9c's convergence grid — L 128, N 256 (same dx), drive
  on over 48–64 — never the 0.2c family's box; but its recipe follows the far side (10-20): σ 0.1 + min_chi 1e-8 on
  the negative-mass far sides (≤ 0.7c, under test), σ 0.4 + 1e-4 on the 0.9c's positive one.
- Binary `main3d_farfix_891d817d_2026-10-17.ex` (kicks: `main3d_kick_af28ad29_2026-10-18.ex`) with
  `exact_quartic_interp = 1`, `rk_stage_refill = 0`, `shift_advec_coeff = 0`, `sommerfeld_relative_to_background = 1`,
  `constraint_norms_edge_cells = 3`.
- Consumer (`--consume-args`): the 14-field frame set (zoom 64, centre 32, slice cache, `--frames-blank-edge 2`),
  `--mots-spectral --mots-spectral-center 32 32 32 --throat-spheres --radii 10 14 18 30`, keep-last 3,
  `GRTECLYN_FRAMES_BUFF_CAP=2048`. R 14 / 18 are the trusted waves (wholly on level 1), R 10 is near field, R 30 is in
  the sponge.
- Templates carry absolute `output_path` and `spinning_background_file`; packs scrub them to repo-relative, so a
  template built from a pack must restore them (the 0.6c's first launch was refused for it).
- A rerun is its old run: the packed params plus the fix keys, diffed. Checkpoints are asked per run (none so far).
- One card does ≈ 20 t/h of L 64 N 128 however it is split (two runs ≈ 9.5 each).
- Stability protocol (Evstafyeva–Siemonsen–East, arXiv:2508.11527): a growth is physical only if its τ converges to
  a nonzero value while the finest-level constraints converge, and the areal radius or MOTS moves with it.

## DEBUGGING NOTES

- **Three numerics bugs (10-17)**, found because the per-level constraints (`constraint_norms_levels.dat`) did not
  converge: the table was interpolated bilinearly (→ C2 spline); AMReX's `cell_quartic_interp` stores its weights
  rounded to 8 decimals, so every coarse–fine ghost was 6e-8 low (→ exact weights, `exact_quartic_interp = 1`); the
  example re-filled the whole RK stage from StateData (→ `rk_stage_refill = 0`). Every earlier run is archived
  (`00_archive/superseded_2026-10-17/`).
- **Far-zone junk (10-17)**: the Γ-driver advected the rotating background shift (β·∇β = −ω²r from t 0 →
  `shift_advec_coeff = 0`); the flat-space Sommerfeld faces sat at 5.5 M (→ relative to the background); Weyl4's
  stencil reads extrapolated ghosts in the outer 2 cells (→ blanked in frames).
- **The sponge drive (10-18)** pulls the shell back to the t 0 data, which is not Einstein evolution once a pulse
  arrives: 48× more face junk. Drive off.
- **CKK's eq. (12) is wrong** (Step 2): the unimposed constraints flagged it at O(J⁴); extremal Kerr closes four
  equations to 160 digits and leaves a residue in eq. (12) alone.
- **Above 0.5c**: with min_chi 1e-8 the 0.7c died at the far-side puncture (t 42.6, floored from t 2.3); σ ≥ 0.2 kills
  that puncture on the 1e-8 floor; dt 0.05 has a K instability on spin data that σ 0.4 + floor only delay. So: floor
  1e-4 on the fast runs, dt 0.02 everywhere. 10-20: the 1e-4 floor only delays σ 0.4's damage on the negative-mass
  far sides (deaths at 85–136; the "far-side centre" bullet above); they rerun on σ 0.1 + 1e-8.
- **Measuring the throat**: never quote R_pol_min (coordinate-dependent). `throat_geometry` reads the box edge once the
  throat leaves the finest box (the push-in after t 61.4): use `throat_spheres` there; it reads small deficits ≈ 20 %
  high. The MOTS stream is the most accurate (3e-6). ψ4 has no matter term (`G_newton` unset → 0): ≤ 0.4 % at
  R ≥ 30, up to 17 % at R 10.
- **Consumer cost**: the spectral MOTS search grows as N³ when it finds nothing (the 0.9c N 192: 22 min a plotfile
  against one every 12) → `restart_consumer.sh <run> --mots-spectral-steps 150` (`--busy`).
- **Collapse deaths**: a NaN in h11 on level 3 after the horizon forms is the collapse's end, not a failure (static,
  0.2c N 96, push-out); trust ends at the χ floor.

## OPEN

- Horizon mass budget: the settled 0.2c horizon (M_irr 1.262) is heavier than the exterior mass fitted from χ at
  r 26–58 (≈ 1.16 at t 150). Settle it with a mass integral before quoting a horizon mass.
- Level 0's box face (Sommerfeld on a non-flat background); dt 0.05 / σ on the fixed binary; waveform extrapolation
  in 1/R; the upstream AMReX PR for the rounded weights; the RK re-fill in the merger, RadialRecipe and
  SupportedWormholeCollapse examples (their campaigns' call).
- The 0.9c polar radius grows 1e-3 after t 110 at every N (coordinates: the areal radius is flat).
- Older numbers that did not reproduce in the code review: the 0.9c minimum orders, the troughs' flatness in R, the
  N 192 ring lapse (0.508, not 0.529), the order of the proper τ (≈ 2, not 3).

## DECISIONS

- 10-13: every quoted run is a triplet member or licensed by one; per-level masked constraint norms in every run.
- 10-15: the paper is the drainhole's alone. Campaign A (family (b) evolutions) dropped: every hold died at its
  far-side positive-mass puncture at t ≈ 23, whatever the numerics.
- 10-16: two recipes (slow ≤ 0.5c, fast above), dt 0.02.
- 10-17: the numerics and far-zone fixes; every paper run reran on them.
- 10-18: the drive off for new runs; the kick is the merger's conformal-factor shell, momentum-exact, no constraint
  solve; the 0.9c kicks dropped (far from physical spins).
- 10-19: no kicks beyond the 0.2c pair; the 0.6c / 0.7c threshold rungs added (J/M² peaks at the 0.5c, so the fast
  end is not the unphysical one); τ is the areal-radius fit over 0.2–1 %.

## DONE BEFORE THE FIXES

Step 0 (10-11): the static hold twins the merger's `single_hold`. Step 1 (10-12): the O(J²) holds' push was the
data's error (∝ J⁴). Step 2 (10-13): the full solver, both families to v_e 0.99, tables in `runs/spinning_p3/tables/`
(≤ 1e-7 to v_e 0.9). Step 3 (10-13 → 10-15): t 0 checks, the L 64 holds, the A1 ladder (the 3D ADM mass equals the
table's to 1e-12). Assets: B1's Chk10000 in its `nfs_chk/`; `fam_a_ve020.spinbg` (a J = 1 cross-check).

## RULES

CLAUDE.md's launch discipline: go first, checkpoints asked per run, full frame set, STATUS pushed at every launch,
stop or wipe. ψ4 radii 10 / 14 / 18 / 30 on every spinning launch.
