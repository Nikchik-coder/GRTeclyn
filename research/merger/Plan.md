# Merging two regular exotic-matter drainhole throats in 3D Cartesian CCZ4

Working document: the current plan and the concise log of what broke and what fixed it.
Started 2026-08-28, rewritten 2026-09-01 after the horizon-timing bug was found.
Literature: [background.md](background.md). Design and prior art: [Reference.md](Reference.md).
Runs live under `runs/wormhole_merger/` (not in git, own README); the packed extract is
[`results/merger/`](../../results/merger/README.md).

**The campaign in one line:** two drainhole throats merge only if one field is flipped;
the merged object collapses, briefly holds a horizon, and the phantom scalar then
destroys first the run (NaN at t ≈ 52–55) and then the horizon itself.

---

## NOW — the NaN at t ≈ 52–55, and the plan to get past it

**What is at stake.** The collapse (source time 44–51.5) emits the one waveform this
campaign exists to record. Signal at radius R lags the source by R, so it crosses the
R = 14 extraction sphere at t ≈ 58–65.5 (the t = 44–47 collapse arrives over t = 58–61;
the t = 51.5 horizon formation arrives at 65.5 — that is exactly where the t ≈ 66
stopping requirement comes from) — **after every arm so far has died**. The
recorded burst peaking at t = 37.5 is plunge/whirl radiation (source ≈ 23.5), not the
collapse. To capture the collapse signature the wave zone must survive to **t ≈ 66**
(R = 30 would need t ≈ 82 — optional, not required).

**Why the runs die.** Two mechanisms, both measured: (1) un-damped phantom scalar
sitting on collapsed geometry blows up — four arms, four different treatments, four
deaths at the edge of whatever region was cleaned (§8); (2) the moving-puncture gauge
needs a horizon to hide the floored region, and the phantom dissolves the horizon
(1.07 → 0.59 over t = 51.5–55, gone ≈ 56, §9) — the seal every interior trick relies
on is itself vanishing.

**The plan, with checkpoints.** Each step has a measurable pass condition; nothing
launches without an explicit go-ahead, and no step below its gate starts until the
gate is green.

- [x] **M1 — fix the horizon instrument** *(done 2026-09-01)*. The in-code θ₊ scan
  assumed a conformally flat metric and produced false "merged at t ≈ 30" verdicts
  (see *The timing bug* below). Now evaluates the full-metric expansion, identical in
  convention to the validated offline scanner.
  - [x] full-metric kernel in `BinaryThroatDiagnostics.hpp`, SPD guard, same file contract
  - [x] serial build clean; MPI+CUDA production binary rebuilt
  - [x] old executable preserved as `main3d.gnu.MPI.CUDA.ex.pre_ahfix`
  - [x] tainted-data warning written into Plan + both READMEs
- [ ] **M2 — validation restart** *(~30 min; GATE for everything below)*. Restart
  chk 03000 (t = 30) with the fixed binary to t ≈ 33.
  - **Pass:** the fixed scan reports **no** common trapping over t = 30–33, where the
    old scan reported θ = −0.032 on r ≈ 3 spheres continuously.
  - **Fail:** artefact persists → the fix is wrong or incomplete; back to M1, nothing
    else moves.
- [ ] **M3 — Run B, phase 1: certify the horizon.** Restart chk 05000 (t = 50) with
  the fixed binary, **damping off**.
  - **Pass:** fixed scan certifies a fully-trapped sphere at t ≈ 51.1 ± 0.5 with
    r ≈ 1.0 (offline scanner said 1.07 at t = 51.5 — the two must agree to ~10 %).
  - Also re-records t = 50–52 with trustworthy θ columns at full cadence.
- [ ] **M4 — Run B, phase 2: the sealed window.** From certification, engage
  radius-window damping strictly inside the horizon: full below r = 0.8, cosine-off
  by 0.95. Causally sealed while the horizon covers it, so the collapse waveform —
  already emitted — reaches R = 14 uncontaminated.
  - **Pass:** run alive and NaN-free past t = 56 (the rw death and the extrapolated
    dissolution time both behind it).
  - **Fail (expected risk):** dies ≈ 55 like rw at the un-damped ring r = 0.7–1.1,
    which sits at and *outside* a shrinking horizon → escalate to M4b.
  - **The freeze question — measure it, don't assume it.** External hypothesis: the
    damping deletes the phantom that drives the shrinkage, so r_AH freezes at ≈ 1.0
    and the window is sealed forever. The counterargument is the seal itself, which
    cuts both ways: nothing strictly inside the horizon can influence the horizon,
    so a window at r < 0.95 cannot stop the flux crossing at r ≈ 1.0 from *outside* —
    and r04000/rw dissolved 1.07 → 0.59 with damping active. The now-trustworthy
    r_AH(t) track decides it: **frozen ⇒ the interior phantom was the driver and M4
    wins outright; on the 1.07 → 0.59 curve ⇒ exterior accretion drives it, the seal
    fails by ≈ 54, and M4b is next.** Either outcome is a measurement worth having.
  - **Causal-seal record for the paper:** r_damp,max is a build-time constant and
    r_AH(t) streams from the fixed scan, so the published proof of purity is one
    plot — r_AH(t) − r_damp,max staying strictly > 0 over the whole window the
    waveform is claimed from. No new code; if the window is ever slaved to the AH
    track, the moving edge must be logged too.
- [ ] **M4b — steepen, don't widen** *(only if M4 dies at the ring)*. Swap the cosine
  ramp for a sharp tanh step: full strength to r = 0.95, strictly zero by 1.0 —
  reaches the inner half of the rw killer ring while still inside the certified
  horizon at engagement. A static edge at 1.0 stays covered only until the
  dissolution curve crosses it (≈ 52.5–53 on the measured track): this buys margin,
  not immunity.
  - **Pass:** alive past t = 56 with the causal-seal plot > 0 while the seal is
    claimed. **Fail:** → M5.
- [ ] **M5 — Run B2, the wide window** *(last resort, only if M4 and M4b both fail)*.
  Full damping inside r = 1.5, off by 2.0 — reaches the killer, but the horizon
  never exceeded 1.07, so this *guarantees* damping in the causal exterior. Expect
  Ψ₄ contamination; treat M5 as a diagnostic arm, publishable only if M6 passes
  anyway.
  - **Pass:** alive past t = 56 **and** the M6 overlap test passes.
  - **Fallback inside M4/M4b/M5** if 1+log re-inflation again lifts sick cells out of
    the window: freeze the lapse in the damping zone (∂ₜα = 0 there, own default-off
    flag).
- [ ] **M6 — overlap test** *(validates whichever of M4/M5 survived)*. Ψ₄ at R = 14
  must match the undamped arms (r03000 to 52.06, n160 to 53.61) over the shared
  window to the few-% level. **Fail:** the damping is visible in the wave zone → the
  waveform cannot be published from this arm; tighten the window and rerun.
- [ ] **M7 — the record.** Run B(2) clean through **t ≈ 66**: the collapse signature
  (source 44–51.5) is on disk at R = 14. Optional stretch: t ≈ 82 for R = 30.
- [ ] **M8 — endpoint honesty in the paper.** After engagement the core is a
  numerically sustained ("zombie") black hole — deleting infalling phantom is exactly
  what stops the dissolution. Waveform from Run B; the dissolution claim from the
  damped-arm measurements (§9) plus the undamped deaths; stated explicitly, with the
  causal-seal plot (M4) printed next to the waveform.

Standing instrumentation for every launch from M2 on: full plot list including h_ij
and A_ij (their absence made r03000/headon/p045/n160 permanently unmeasurable
offline), NaN coordinates printed at abort, checkpoints every 5 units near the death
window, frame plane chosen from the arm's motion.

**Success = M7 + M6:** one run whose R = 14 Ψ₄ stream is clean through t ≈ 66, with
an overlap-validated waveform and an honestly-labelled interior.

---

## The timing bug — how the merger got mis-measured, and the fix

**What the code did.** The in-code common-horizon scan
([BinaryThroatDiagnostics.hpp](../../Examples/BinaryWormholeMerger/BinaryThroatDiagnostics.hpp))
evaluated θ₊ with a conformally-flat shortcut: `2√χ/r − ∂ᵣχ/√χ + Ã_rr − (2/3)K`. That
drops the conformal metric h_ij entirely. Between two deep wells h_ij is O(1) far from
flat, so the shortcut's error is O(1) exactly where the scan was asked to judge a
merger — and it judged wrong, in the trapped direction.

**The conviction (each claim has two independent sources):**

- **p045, the healthy control, convicts the instrument.** Same scan, a run with no
  collapse anywhere: it reports *continuous* common trapping over t ≈ 42–60 (437 rows,
  deepest θ = −0.195, spheres out to r = 6.2) while min χ, the lapse and max|K| all
  read healthy and the throats fly *apart*. A 6×-deeper, 18-unit false positive in a
  collapse-free run.
- **The t ≈ 30 "fusion" has no collapse under it.** The signal (t = 29.95–32.71,
  deepest θ = −0.032, spheres r = 2.9–3.4 enclosing both throats at separation
  1.9–3.1) coincides with min χ *rising* (1.3e-5) and max|K| *falling* — no collapse
  indicator moves. It vanishes abruptly when the shrinking scan sphere r < 3.06 no
  longer encloses both wells.
- **The real collapse is at t ≈ 44–47.** `collapse_diagnostics.dat`: min χ crashes
  5.4e-6 → the 1e-8 floor at t = 44.9, max|K| jumps 0.08 → 1.46. The movies show the
  cores crushing together at t ≈ 45 — the "contact at 45" the frames always showed
  was real, and the old §9 explanation ("interior coordinate motion") was wrong.
- **The first genuine trapped surface is t ≈ 51.1–51.5.** Full-metric scan: θ = −0.41
  at r = 1.0 from t = 51.06; the independent offline scanner
  ([ah_radial_scan.py](../../grteclyn-wrapper/scripts/validation/ah_radial_scan.py))
  confirms r = 1.07 at t = 51.5.

**The fix (2026-09-01).** The in-code scan now computes the full expansion
Θ = div_γ(s) + K_ij s^i s^j − K with γ_ij = h_ij/χ, γ^ab = χ·adj(h) (det h = 1),
K^phys = (A + hK/3)/χ — the same formula as the offline scanner, on a 7-point stencil,
with an SPD guard that reports "no verdict" (never "trapped") on broken cells. Output
columns and file contract unchanged.

**Tainted data:** the θ/r columns (13–18) of every `binary_throat_diagnostics.dat`
written before 2026-09-01 carry the artefact wherever two wells sit inside one scan
sphere. Per-throat positions, separations, χ/lapse minima in the same files are
unaffected. The offline scanner was never affected.

**How it survived.** The scan was validated on *single* collapsed objects, where
conformal flatness is a fair late-time approximation — the two-well regime is
precisely where it fails, and the p045 control that exposes it was only run later.

## The corrected merger timeline

| t | what happens | evidence (two sources) |
| --- | --- | --- |
| 0–23 | inspiral, separation 11.94 → ~4 | both trackers; both resolutions agree ≤ 1.8 % |
| ~24–33 | plunge; throats' fields overlap (sep 3.6 → 2.1) | separation streams; Ψ₄ burst at R = 14 peaks t = 37.5 ⇒ source ≈ 23.5 (R = 30 copy lags by exactly 16) |
| 29.95–32.71 | *(artefact — no horizon)* old scan's "fusion" | convicted above |
| 33–43 | horizonless whirling double core, sep 1.8 → 0.8 | slice caches; max\|K\| falling 0.13 → 0.08 |
| 44–47 | **collapse** — the merger proper | min χ → 1e-8 floor at 44.9, max\|K\| ×18; movies' crush at ≈ 45 |
| 51.06–51.5 | **first genuine common trapped surface**, r ≈ 1.0–1.07 | full-metric in-code scan; offline scanner |
| 51.5–55 | horizon dissolves 1.07 → 0.59, accelerating; extrapolated gone ≈ 56 | two damped arms, one curve; sampling-doubling moves crossings ≤ 0.01 |
| 52.06–55.0 | NaN deaths (r03000 52.06, n160 53.61, rw 55.00) | abort logs + last stream rows agree |
| 58–65.5 | collapse signature crosses R = 14 — **never recorded** (44–47 collapse arrives 58–61; the 51.5 horizon formation arrives 65.5 ⇒ `stop_time` must reach ≈ 66) | propagation at v ≈ c (measured on the first burst) |

The black hole lives ~5 units, not the ~26 previously claimed: **it is born at t ≈ 51
already dissolving**, not born at t ≈ 30 and eaten slowly. Downstream corrections:
the headon arm's "horizon at t = 29" is the same artefact (unverifiable — no h_ij
plots; it died t = 44, consistent with dying *at its collapse*); n160's "horizon
formation converged 29.74 vs 29.93" is the artefact converging with the geometry it
is a function of — the inspiral/waveform convergence stands, n160's true horizon time
is unknown; every "merged at t ≈ 30" sentence in the READMEs and the article draft
is wrong and is being corrected with this document.

## Verdicts on the proposed rescue ideas (external suggestions, 2026-09-01)

| idea | verdict |
| --- | --- |
| Damping window slaved to the in-code AH radius | Was unusable while the AH column was the flat proxy; **viable after the fix**, but start static (r < 0.8/0.95) — slave it only if the horizon track proves smooth |
| Freeze the lapse inside the damping zone (∂ₜα = 0) | **Keep as fallback** (step 3): it targets the measured lapse-re-inflation escape, but the radius window already sidesteps that mechanism |
| Zero φ/Π inside r = 1.5 "right after horizon formation (t = 35)" | Right spirit, wrong clock: **no horizon exists at t = 35** — engaging then changes the physics under study (that mistake is already in the rw arm's t = 50–51 window, ~1 unit early). Earliest defensible engagement is horizon certification, t ≈ 51.1 |
| "You already have the main GW burst" | **Half wrong**: the recorded burst is plunge/whirl radiation. The collapse signature (source 44–51.5) has never been recorded — it is the missing piece, and it needs t ≈ 66, not t ≈ 85 |
| Two-run split: pure-physics arm + post-horizon damped arm, causality argument | **Adopted** — it is steps 3–4 above. Corrections: undamped arms cannot supply the dissolution measurement (no h_ij in their plots — that stays with r04000/rw); and interior damping is causally sealed only while the horizon covers the window, which the dissolution itself un-does — hence the B/B2 split and the overlap test |
| Interior damping halts the accretion ⇒ horizon freezes at ≈ 1.0, M4 risk "actually zero" | **Testable, not assumable — folded into M4.** The causal seal cuts both ways: a window strictly inside the horizon cannot influence the flux crossing it from outside, and r04000/rw dissolved with damping active. The r_AH(t) track decides; both outcomes are physics |
| Steepen the ramp (tanh, zero by r = 1.0) before widening the window | **Adopted as M4b** — the intermediate fallback; M5 demoted to last-resort diagnostic |
| `causal_seal.dat` logging r_AH − r_damp | **Adopted as a derived plot, not new code** — the fixed scan already streams r_AH and the static window edge is a constant; a logger is only needed if the window ever moves |

---

## The campaign so far

**Stage 0 — a real throat on the grid (done 2026-08-28).** Massive Ellis–Bronnikov
drainhole in the isotropic chart, ADM mass carried by the lapse, constraints exact at
t = 0, verified to roundoff.
**Stage 1 — one throat holds still (done 2026-08-30).** 40 M with −0.36 % throat
drift; the surviving growing mode identified and rated (e-fold ≈ 4.4 ≈ throat/c).
**Stage 2 — two throats (done 2026-08-31).** Tracker + moving boxes shipped; a
boosted throat survives crossing the grid; like throats **repel** (5× gravity);
flipping one field (`wormhole_phi_sign_B = -1`) is the only gravity-driven merger
route — C/A infall ratio 1.511 ± 0.033 vs 1.500 predicted.
**Stage 3 — the merger (live).** Merger achieved and converged; every merging arm
dies of the phantom-on-collapsed-geometry NaN; the horizon dissolution measured; the
collapse waveform not yet captured — that is the plan above.
**Stage 4 — write.** Blocked on the Run B waveform; the article draft's t ≈ 30
merger claims must be rewritten to this timeline.

### The runs

| run | what is different | ran to | what happened |
| --- | --- | --- | --- |
| `..._r03000` | **main arm**, no damping | 52.06 | inspiral, collapse at ≈ 45, horizon at ≈ 51, NaN 1 unit later |
| `..._r05000` | damping, built-in thresholds (~3 cells) | 52.09 | window too deep, bought 0.02; streams lost pre-extraction |
| `..._r04000` | lapse window ×1000 wider; full plot list | 52.86 | core cleaned to φ ~ 1e-10 and died anyway — sick cells re-inflate their lapse and climb out |
| `..._sg10_r05000` | dissipation σ 0.1 → 1.0 | 51.68 | died *earlier*: dissipation attacks the puncture structure |
| `..._rw_r05000` | radius window (r < 0.5/0.7), from t = 50 | **55.00** | longest survivor; caught the horizon dissolving |
| `merge_headon_...` | head-on, no orbit | 44.00 | dies at its own collapse; old binary, timing unverifiable |
| `..._p045` | momentum 0.45 | **60.01 clean** | never merges (periapsis 3.95 at t = 40) — the healthy control, and the run that convicts the old θ scan |
| `..._n160` | 160³ instead of 128³ | 53.61 | everything pre-collapse converged; death moved +1.55 units and stayed |
| `..._ml2` | max_level 2 | 9.42 | three refinement levels is the floor |

---

## Issues found and what was done — the log

1. **The throat was not on the grid.** Brill–Lindquist puncture mass drove χ → 0 at
   the throat; one cell there was 6.2 proper units wide. **Fix:** massive drainhole
   with the ADM mass in the lapse — χ_throat 0.17, proper cell width 0.31, a ~20×
   resolution gain, constraints exact at t = 0. Cap: m/a ≲ 1 (heavier binary wants a
   *wider* throat, not a heavier one).
2. **σ = 2.0 dissipation ate 34 % of the throat while every norm read flat.** Its
   smoothing lowers the violation it causes — monitors structurally blind. **Fix:**
   σ = 0.1 in drainhole templates.
3. **The origin collar is load-bearing, not decorative** (prediction retracted):
   ×3.5 on origin survival for 20 % of throat radius. Two independent trade-offs.
4. **χ-gradient tagging chased its own noise** to 32.8M cells and OOM. **Fix:**
   geometric taggers only (fixed/moving boxes + extraction shells); memory flat at
   13.32 GB forever, physics unchanged.
5. **The t ≈ 24 wall was a real EB growing mode, not the grid.** Refinement moved the
   wall *later* (excluding the under-resolved-origin theory); e-folding 4.4 ≈
   throat/c as predicted. `max_level = 3` reaches t = 40 clean; ml2 is not viable.
6. **A moving throat survives.** Boosted arm crossed 3.3 grid units, zero lost
   tracker rows. Calibration that matters: **coordinate speed under-reads the
   physical speed by up to ~4×, time-dependently** — trajectories give sign and
   displacement, never velocity. Orbit questions go to the slice cache (1e-4), not
   the tracker (quantum 0.03).
7. **Like throats repel — 5× gravity.** The support field carries scalar charge set
   by throat *width* (halving a halves the push 3.0×); phantom scalars repel like
   charges. Flip one field and the 5× push becomes a pull: measured C/A ratio
   1.511 ± 0.033 vs 1.500. The flip is exact for a single throat (all one-body
   properties depend on (∇φ)²), so the stability record transfers.
8. **Phantom on collapsed geometry kills every run.** Puncture floors protect
   geometry, not matter. Four cures, one law: the death sits at the edge of whatever
   was cleaned, each wider window buys 1–2.5 units. Lapse-defined windows
   self-defeat (wrong-sign K pockets re-inflate the lapse, sick cells climb out);
   the radius window works but was too narrow (killer at r = 0.7–1.1). Extra
   dissipation makes it *worse*.
9. **The horizon is dissolving.** Offline full-metric scan on every death-era
   snapshot with h_ij/A_ij: fully-trapped radius 1.07 (t = 51.5) → 0.59 (t = 55),
   accelerating, two damping schemes on one curve, sampling-doubling converged.
   Phantom accretion (Babichev): negative energy across the horizon shrinks it.
   Damping cannot be blamed — deleting negative energy biases toward *growth*. The
   trapped region is strongly deformed (past r = 2 at the poles, 0.6 equatorial).
10. **Resolution postpones, never cures.** 1.25× finer: +1.55 units (3 %), same NaN;
    log-fit says t = 60 undamped needs N ≈ 400 ≈ 90× the compute. Closed.
11. **The in-code θ scan was conformally flat and invented the t ≈ 30 merger.**
    The headline error of the campaign — see *The timing bug* above. Fixed in code
    2026-09-01; all pre-fix θ columns tainted; timeline rewritten.

## Traps that must not regress

| trap | guard |
| --- | --- |
| flat-conformal θ₊ shortcut | full-metric scan only (2026-09-01); never reduce the h_ij dependence "for speed" |
| σ = 2.0 | 0.1 in all drainhole templates; σ = 2.0 reaches t = 40 by destroying the throat |
| `wormhole_momentumB` default | it is **minus** momentumA — pin `0 0 0` for a single throat |
| puncture route to ADM mass | `wormhole_id_type = 1` + `drainhole_mass`; `ψ += m/2r̄` destroys the throat |
| `tagging_type = 2` without `throat_tracking` | rejected in `check_params` |
| frame slice plane | pick from the arm's motion at launch; the default x-y hides z-motion |
| fixed colour scale on a growing field | per-field auto-zlim at launch; re-fix from the slice cache for paper movies |
| tracker across a late restart | re-seeds from params positions; beyond search radius 2.0 it reads nA = 0 — seed from the last recorded row |
| `checkpoint_interval` after grid changes | counts coarse steps, not code units — recompute |
| root-level `restart_file` | dead key; use `amr.restart` |
| restart outer boundary | interior bit-exact; boundary error walks inward at ~c — no domain-wide norms or waves across a restart window (Ψ₄ at R = 14 clean ~20 units after; R = 30 ~12) |
| plot list | h_ij + A_ij always — their absence is why four runs are offline-unmeasurable forever |

## Dormant traps for Stage 2.2 (file-based initial data)

- Refining below a `.gridinit` solve's own dx **erases the throat before step one**
  (prolongation invents smooth wrong detail). Diagnose at max_level 0 or land the
  split-ID loader first.
- GRTresna can stall and print "Converged" anyway — read the residual, never the word.
- Noether-charge conservation is a resolution diagnostic; −80 % in 14 units on the
  puncture geometry meant nothing was measurable there.
- The areal-radius argmin lands on the innermost unresolved cell without
  `--areal-min-radius`; old `areal_radius.dat` columns are unreliable.
- The Q-ball route was never refuted — the puncture geometry failed, not the matter;
  on the drainhole it is untested.

## Known matter-sector inconsistencies (none affects runs so far; all use `phantom_mass = 0`)

1. `ExoticScalarField` flips the sign of the whole T_μν but not `dVdphi` — fix before
   any massive-phantom or Q-ball work.
2. Two-throat data is plain superposition — no Helfer/Ning correction (Stage 2.1/2.2).
3. `support_strength ≠ 1` breaks ∇·T = 0 — diagnostic knob only.

## Decision gates (unchanged)

- single throat loses charge > few % → instability is physical; reframe as
  collapse/expansion of a two-throat system;
- CTTK returns K² < 0 with two exotic lumps → past the existence boundary; report the
  boundary as a finding;
- excision unstable → abandon true topology for this paper.

**The standing caveat:** the Stage 1 growing mode is still growing at t = 40 and the
40 M window is a fuse, not stability. Budget every arm to finish inside it.
