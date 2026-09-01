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
- [x] **M2 — validation restart** *(done 2026-09-01; GATE for everything below)*.
  The t = 30 checkpoint no longer existed on scratch, so M2 and M3 were run as **one
  undamped restart from chk 04000 (t = 40)** to the natural death — which covers the
  two-wells-in-one-sphere regime the artefact lived in and reaches the real horizon
  in the same pass (`merger_fix/val_ahfix_r04000`, 39 min, 18.2 units/h).
  - [x] **PASS — specificity:** the fixed scan is **silent** over t = 40 → 51.02
    (min θ = **+0.158**), where the old scan reported continuous trapping. The
    artefact is gone.
  - [x] **PASS — regression:** evolution columns bit-identical to r03000 through
    t ≈ 44.9 — the kernel change is diagnostic-only, as claimed.
- [x] **M3 — Run B, phase 1: certify the horizon** *(done 2026-09-01, same run)*.
  - [x] **PASS:** first θ < 0 at **t = 51.03, r = 1.0625**; sustained from t = 51.47.
    Offline `ah_radial_scan.py` on this run's own plotfiles gives r = 1.070 at
    t = 51.5 — **0.7 %** apart, inside one grid cell (dx = 0.03125). The required
    agreement was 10 %.
  - [x] The old scan found **nothing** anywhere over t = 40–52: it missed this real
    horizon as well as inventing the false one.
  - [x] Died `NaN in post_timestep`, component K, level 3, at **t = 51.71**
    (r03000 died 52.06) — the expected undamped death, not a new failure.
- [x] **M4 — Run B, phase 2: the sealed window** *(ran 2026-09-01 — **FAILED, and
  the failure is itself the decisive measurement**)*. From certification, engage
  radius-window damping strictly inside the horizon: full below r = 0.8, cosine-off
  by 0.95. Causally sealed while the horizon covers it, so the collapse waveform —
  already emitted — reaches R = 14 uncontaminated. `merger_fix/m4_sealed_r04000`,
  GPU 0, to stop_time = 66.
  - [x] **Restarts from chk 04000 (t = 40), not 05000.** Chk05000 carries r04000's
    *lapse-window* damping straight through the collapse at t = 44–47 — the very
    burst M7 must record. Restarting undamped at t = 40 with the radius window gated
    to t = 51.2 buys a clean collapse and a sealed core both. Costs ≈ 36 min.
  - [x] **The lapse window is switched off** (`core_damping_lapse_start = 0`).
    `CoreMatterDamping` combines the windows as `w = max(w_lapse, w_radius)` and the
    lapse branch is live whenever damping is on, so leaving it at 3e-2 would damp
    cells *wherever they sit* and r_damp,max would not be a constant — the causal-seal
    proof below would have nothing constant to compare against.
  - [x] **Result: died t = 51.6925, NaN in h11, level 3 — 0.015 units before the
    undamped validation death (51.7075). The certified seal bought zero time.** The
    damping itself demonstrably engaged and worked where it reached: |φ|max fell
    0.82 → 0.57 at exactly t = 51.2, then stalled — two e-folding times of
    full-weight damping (τ = 0.25) producing only 1.5× total decay — while max|Π|
    kept growing 0.64 → 0.74 to the end. The surviving driver therefore sits where
    the window's weight is small or zero: the ring r ≈ 0.95–1.3, at and outside the
    horizon. Issue 8's law holds exactly — the death sits at the edge of what was
    cleaned.
  - [x] **Why rw (t = 55.00) beat the certified seal (t = 51.69): engagement time
    is load-bearing.** rw's window ran from t = 50 on a core the r04000 lapse
    window had already cleaned; the seal engaged at t = 51.2 on a full-strength
    scalar with 0.5 units left to the crisis. Certification-gated engagement is too
    late *by construction* — the cure must be in place before the ring goes
    hypercritical, and publishability must be recovered through the M6 overlap
    test instead of the engagement clock.
  - **The freeze question — measure it, don't assume it.** External hypothesis: the
    damping deletes the phantom that drives the shrinkage, so r_AH freezes at ≈ 1.0
    and the window is sealed forever. The counterargument is the seal itself, which
    cuts both ways: nothing strictly inside the horizon can influence the horizon,
    so a window at r < 0.95 cannot stop the flux crossing at r ≈ 1.0 from *outside* —
    and r04000/rw dissolved 1.07 → 0.59 with damping active. The now-trustworthy
    r_AH(t) track decides it: **frozen ⇒ the interior phantom was the driver and M4
    wins outright; on the 1.07 → 0.59 curve ⇒ exterior accretion drives it, the seal
    fails by ≈ 54, and M4b is next.** Either outcome is a measurement worth having.
    - **First evidence, from M3 (2026-09-01): the horizon is contracting from the
      moment it forms**, with no damping anywhere in the run — r = 1.110 (t = 50.5),
      1.090 (51.0), 1.070 (51.5), i.e. ≈ 0.04 per code unit. Extrapolated linearly it
      crosses M4's r = 0.95 edge at **t ≈ 54.5**: that is the measured lifetime of the
      seal, and it is against the freeze hypothesis. M4's own r_AH(t) track is the
      decider; this only says the null hypothesis is already in trouble.
    - [x] **Answered by M4 (2026-09-01): not frozen — the contraction accelerates.**
      With the seal active, the in-code scan tracked r_AH = 1.0625 (t = 51.5) →
      1.0000 (t = 51.65–51.69): ≈ 0.3 per code unit against 0.04 at birth. The
      offline scanner on M4's own plotfiles reproduces the birth curve
      (1.110 / 1.090 / 1.070 at 50.5 / 51.0 / 51.5) to the same shells as the
      validation run — the physics repeats across restarts even though trajectories
      don't. Interior damping does not halt the shrinkage: the driver crosses from
      outside, exactly as the causal-seal argument said it must, and the linear
      t ≈ 54.5 seal-lifetime estimate was optimistic by ≈ 3 units. A static radius
      strictly inside this horizon has no runway at all.
  - [x] **Post-floor trajectories are not run-to-run reproducible** — measured on
    M2/M3 against r03000. Streams are bit-identical from the restart until χ first
    touches min_chi at t ≈ 44.9, then decohere (separation 0.477 vs 0.569 at t = 48;
    the two deaths 0.35 units apart). Floor clipping plus non-deterministic GPU
    reductions. The *physics* repeats (horizon ≈ 51, death ≈ 52); the trajectory does
    not. **No convergence or overlap claim — M6 included — may be stated tighter than
    that**, and per-run numbers must be quoted per run, never averaged as if replicas.
  - **Causal-seal record for the paper:** r_damp,max is a build-time constant and
    r_AH(t) streams from the fixed scan, so the published proof of purity is one
    plot — r_AH(t) − r_damp,max staying strictly > 0 over the whole window the
    waveform is claimed from. No new code; if the window is ever slaved to the AH
    track, the moving edge must be logged too.
- [ ] **M4b — the four-arm sweep** *(LAUNCHED 2026-09-01, one arm per GPU, in
  flight)*. M4 measured that (a) the killer lives at r ≈ 0.95–1.3, (b) engagement at
  certification is too late, and (c) the horizon overruns any static inside-horizon
  edge — so the old "steepen the ramp" M4b is superseded: a sharper edge at 0.95
  seals faster what already bought nothing. All four arms restart from m4_sealed's
  own Chk05000 (t = 50, clean — its damping never fired before 51.2), engage at
  t = 50.0, run with **checkpoints off** to stop_time = 66:

  | arm | GPU | window (full/zero radii) | what it tests |
  | --- | --- | --- | --- |
  | `m4b_wide` | 0 | radius 1.00 / 1.30, τ = 0.25 | the ring itself |
  | `m4b_combo` | 1 | lapse 3e-2 → 1e-3 **and** radius 1.00 / 1.30 | rw's best-ever lapse window with its one escape route (re-inflated pockets at r ≈ 0.3) covered by the radius window |
  | `m4b_fast` | 2 | radius 1.00 / 1.30, τ = 0.05 | window right but rate losing to the growth? |
  | `m4b_sledge` | 3 | radius 2.00 / 2.50, τ = 0.25 | existence proof: full damping over the *whole* merged object (trapped-shell mean radius 1.63, equator max 2.3) — if even this dies, matter surgery is the wrong knife |

  - Engagement at t = 50.0 predates horizon certification (51.03), so every arm is
    diagnostic in old-M5's sense: publishable only through the M6 overlap test. The
    collapse burst (source 44–47) predates t = 50 and stays clean in all arms.
  - Resolution is **not** an arm: the ladder is closed (ml2 died 9.42, base ≈ 52,
    n160 53.61 — a 25 % refinement bought 1.55 units, log-fit says t = 60 undamped
    needs ~90× the compute), and this death sits at r ≈ 1.0, spanning ~32 finest
    cells — not a resolution-starved feature. Neither is Kreiss–Oliger dissipation
    (sg10 died *earlier*, 51.68).
  - **Read-out:** survivors past t = 56 graduate to M6/M7. wide vs fast splits
    window-vs-rate; combo vs wide isolates the lapse window's contribution; sledge
    failing falsifies matter surgery entirely → the gauge route (lapse-freeze
    fallback below) or accept that the record ends at horizon formation.
  - [x] **Wave-1 result (2026-09-01): the rate is the control variable; window
    shape and size are irrelevant.** wide 51.94, combo 51.94, sledge 51.91 — the
    three τ = 0.25 arms died together (scatter below the 0.35 reproducibility
    floor) regardless of whether the window covered the ring, added the lapse
    branch, or swallowed the whole object. fast — identical to wide except
    τ = 0.05 — outlived all of them and the undamped arm, dying at **52.42**. All
    four: NaN in h11, level 3. 5× the rate bought 0.5 units: damping helps at the
    rate axis and only there, and at τ = 0.25 it loses the race outright.
  - [x] **The mechanism, imaged** (fast arm frames at t = 52.0, 0.4 before its
    death): φ cleaned white inside r ≈ 1 with saturated crescents pinned at the
    window edge; **wrong-sign K pockets (K ≈ −0.07) wrapped around the bar ends at
    r ≈ 1–2** exactly where the crescents sit — the rw re-inflation loop
    photographed; and Weyl4 showing the whirling bar radiating a clean quadrupole
    spiral — **the collapse signature is being emitted and is in flight**; the
    campaign needs only a run that survives long enough for it to arrive.
- [x] **M4b wave 2** *(2026-09-01: all three arms dead in 8 minutes — the
  (window, rate) plane is exhausted)*. The winning rate pushed and crossed with
  the windows; same restart, engagement and checkpoints-off as wave 1:

  | arm | GPU | window (full/zero) | τ | died | NaN |
  | --- | --- | --- | --- | --- | --- |
  | `m4b2_vfast` | 0 | radius 1.00 / 1.30 | **0.02** | **51.88** | **K**, level 3 |
  | `m4b2_fastsledge` | 1 | radius 2.00 / 2.50 | 0.05 | **52.55** | h11, level 3 |
  | `m4b2_fastcombo` | 3 | lapse 3e-2/1e-3 + radius 1.00 / 1.30 | 0.05 | **52.42** | h11, level 3 |

  - [x] **The rate axis is non-monotonic and its peak is measured.** τ = 0.25 →
    ~51.9, τ = 0.05 → 52.42, τ = 0.02 → 51.88: pushing 2.5× past the winner gave
    *all* the gain back, and vfast alone died in **K** rather than h11 —
    removing matter that violently shocks the gauge itself. The optimum sits at
    τ ≈ 0.05 and buys ~0.5 units, full stop.
  - [x] **Coverage and lapse-selection add nothing even at the winning rate.**
    fastsledge (K-pockets fully inside the window) 52.55 = fast + 0.13, inside
    the ±0.35 scatter; fastcombo 52.42 = fast exactly.
  - [x] **Verdict: post-collapse matter surgery is falsified at every point of
    the (window, rate) plane.** Best achievable ≈ 52.5 against a target of 66.
    The killer the frames imaged — wrong-sign-K lapse re-inflation at the bar
    ends — is a *gauge* instability that matter deletion can delay by half a
    unit and no more.
- [ ] **M4b wave 3a — attack the gauge** *(LAUNCHED 2026-09-01, four arms on
  all four GPUs; go-ahead given with tactical direction)*. New module
  `CoreLapseFreeze.hpp` (own default-off flag, per the SOLID rule): the
  Bona-Masso *source* of the lapse is tapered to zero inside a central window —
  ∂ₜα = advec − (1 − W(r))·c·αᵖ·(K − 2Θ) — so the imaged K < 0 pockets lose
  their re-inflation motor. Three design constraints, all deliberate:
  - **Source-only, advection intact.** Killing the whole lapse RHS while the
    shift keeps moving the grid creates a lapse-vs-shift shear boundary; the
    taper touches only the −2αK term, exactly cancelled from the same solution
    array the gauge RHS read.
  - **C² smooth in space.** W(r) is a quintic smootherstep (continuous first
    *and* second derivatives), one degree smoother than the matter window's
    cosine ramp, because this weight multiplies a RHS the finite differencing
    then differentiates. A boolean freeze would NaN on the spot.
  - **Gamma-driver guard pre-built.** `core_freeze_shift` scales the shift and
    B RHS by (1 − W) in the same window — default off, flipped without a
    rebuild if the shift tears the grid over the tapered core.

  All arms restart from Chk05000 (t = 50), engage at 50.0, checkpoints off:

  | arm | GPU | matter damping | freeze window (full/zero) | shift guard |
  | --- | --- | --- | --- | --- |
  | `m4c_freeze` | 0 | τ 0.05 ring | 1.00 / 1.30 (= matter ring) | off |
  | `m4c_freezewide` | 1 | τ 0.05 ring | 2.00 / 2.50 (covers imaged pockets) | off |
  | `m4c_freezeonly` | 2 | **none** | 2.00 / 2.50 | off |
  | `m4c_freezeshift` | 3 | τ 0.05 ring | 2.00 / 2.50 | **on** |

  `freezeonly` is the clean experiment: if the gauge fix alone survives, the
  scalar was never the killer. Publishability of every freeze arm rests on the
  M6 overlap — the window is *not* strictly inside the trapped surface.
  - [x] **First result, minutes in: the shift guard is fatal, not protective.**
    `m4c_freezeshift` died at **50.24** (NaN in K) — 0.24 units after
    engagement, faster than any arm has ever died. Scaling the shift/B RHS by
    (1 − W), even C²-smoothly, strangles the Gamma-driver mid-collapse; the
    guard stays off everywhere. The three guard-less arms run on.
  - [x] **Final result: all four dead — gauge-source surgery is falsified
    alongside matter surgery.** freeze **52.04** (h11), freezewide **52.03**
    (h12 — first off-diagonal death), freezeonly **52.12** (h11).
    - **freezeonly ≈ the undamped baseline** (52.12 vs r05000's 52.09):
      cancelling the Bona-Masso source in the core changed *nothing*. The
      K → lapse re-inflation loop is not the load-bearing mechanism — the
      conformal metric h_ij blows up at the bar ends regardless of what the
      slicing source does.
    - **Taper + matter < matter alone** (52.04/52.03 vs fast's 52.42): the
      taper engaged (measurable −0.4 shift against its exact matter-only twin
      — that shift is the proof of engagement) and was mildly harmful.
  - [x] **The wall verdict.** The t ≈ 52 death (Chk05000 cohort) has now
    survived every interior intervention: resolution (+1.55 per 25%),
    dissipation (−0.4), matter deletion at every window and rate (+0.5 max),
    slicing-source cancellation (0), shift freezing (−1.8). It is
    intervention-independent. Causal arithmetic: capturing the full burst at
    radius R needs survival to ≈ 51.5 + R; the all-time record is 55.0 → R ≈
    3.5, inside the near zone. The gap to R = 14 is ~13 units and no measured
    knob moves it more than half a unit. **The wall is a property of the
    phantom dissolution in moving-puncture CCZ4, not of any tunable.** The
    remaining moves are formulation-level (true excision; a different slicing
    family) or an M8 pivot: publish the convergent wall itself — inspiral
    waveform clean at R = 14 to t ≈ 52, the dissolution and its falsification
    table as the discovery.
- [x] **M4b wave 3b — damp through the collapse: VETOED before launch**
  *(causality trap, caught in review 2026-09-01)*. The collapse at t ≈ 44–51.5
  is the physical *source* of the burst; matter damping during that window
  alters the stress-energy actively sourcing Ψ₄, so a 3b arm would fail the M6
  overlap by construction — it deletes the physics it is trying to record. rw's
  55.00 stands as evidence about engagement timing, not as a recipe. Chk04000
  stays in scratch as a fallback restart point only.
- [ ] **M4b wave 4 — the last interior knobs: timestep and dissipation
  direction** *(LAUNCHED 2026-09-01, user-proposed)*. The proposal was
  dt_multiplier = 0.02 and sigma = 0.1 — both turn out to be the campaign
  baseline already, in every run. So wave 4 tests the two *live* directions:
  dt LOWER than baseline (a genuinely unmeasured axis), and sigma LOWER
  (following the measured trend: sigma 1.0 died at 51.68, 0.1 at 52.09 — more
  dissipation is worse, so less might be better). Same restart (Chk05000),
  engagement 50.0, checkpoints off:

  | arm | GPU | change vs baseline | matter damping | tests |
  | --- | --- | --- | --- | --- |
  | `m4d_dt001_fast` | 0 | dt_multiplier 0.02 → **0.01** | τ 0.05 ring | dt axis at the best-known config |
  | `m4d_dt001_plain` | 1 | dt_multiplier 0.02 → **0.01** | none | dt axis in isolation vs undamped 52.09 |
  | `m4d_dt0005_fast` | 2 | dt_multiplier 0.02 → **0.005** | τ 0.05 ring | 4× cut — amplifies any dt signal |
  | `m4d_sig002_fast` | 3 | sigma 0.1 → **0.02** | τ 0.05 ring | dissipation lowered along the trend |

  If the deaths sit at 52.0–52.6 again, the wall is confirmed
  timestep-independent and the interior-knob space is exhausted in full; the
  campaign decision (formulation-level move vs M8 pivot) is then forced.
- [x] **M5 — Run B2, the wide window** *(folded into the sweep as `m4b_sledge`,
  same publishable-only-via-M6 status)*.
  - **Fallback inside the sweep** if 1+log re-inflation again lifts sick cells out of
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
  - **Framing (from review, 2026-09-01):** present the M4/M4b failure as a
    physical discovery, not a failed numerical trick — standard interior matter
    excision could not stabilise the spacetime post-merger because phantom
    accretion drives extrinsic-curvature shocks (K < 0) in the surrounding
    geometry faster than the interior can be excised, forcing an explicit
    freeze of the slicing source to extract the final wave. The extremity of
    the matter is the story; the gauge surgery is its measurement.

Standing instrumentation for every launch from M2 on: full plot list including h_ij
and A_ij (their absence made r03000/headon/p045/n160 permanently unmeasurable
offline), NaN coordinates printed at abort, checkpoints every 5 units near the death
window, frame plane chosen from the arm's motion.

Checkpoints every 5 units is affordable only because of `checkpoint_keep` (added
2026-09-01): a checkpoint of this grid is ≈ 10 GB, so a clean pass to t = 66 would
otherwise strand ~50 GB nobody restarts from. `GRAMR::checkPoint()` writes through
AMReX as before and then drops all but the newest N — **after** the write returns, so
a run killed mid-write still has its predecessor. Default `0` keeps every checkpoint,
so no archived run changes meaning; the merger templates set `1`. Two guards beyond
that: a directory is a candidate only if it holds a complete `Header`, and the
checkpoint a run was **restarted from** is never deleted. Verified end to end on a
32³ smoke run — eight written, seven deleted, one on disk throughout.

The M4b sweep itself runs with checkpoints **off** entirely (user call, 2026-09-01):
four concurrent arms × 10 GB, all short and all restartable from the one kept parent
— m4_sealed's Chk05000 (t = 50), which stays on scratch until the sweep concludes.
M4's death-window plotfiles were pruned (7.2 GB) once the offline horizon scan on
them was recorded.

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
| 51.03–51.5 | **first genuine common trapped surface**, r = 1.0625 → 1.070 (sustained from 51.47) | fixed in-code scan (M3); offline scanner on the same run's plotfiles, 0.7 % apart |
| 51.5–55 | horizon dissolves 1.07 → 0.59, accelerating; extrapolated gone ≈ 56 | two damped arms, one curve; sampling-doubling moves crossings ≤ 0.01 |
| 51.69–55.0 | NaN deaths (m4_sealed 51.69, val 51.71, r03000 52.06, n160 53.61, rw 55.00) | abort logs + last stream rows agree |
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
| Interior damping halts the accretion ⇒ horizon freezes at ≈ 1.0, M4 risk "actually zero" | **Testable, not assumable — folded into M4, and the first evidence is against it.** The causal seal cuts both ways: a window strictly inside the horizon cannot influence the flux crossing it from outside, and r04000/rw dissolved with damping active. M3 now measures the horizon *contracting from birth with no damping in the run at all* — 1.110 → 1.070 over t = 50.5–51.5, ≈ 0.04/unit, crossing M4's edge at t ≈ 54.5. M4's own r_AH(t) track is still the decider; both outcomes are physics. **Answered by M4 itself (2026-09-01): on the curve and accelerating** — 1.0625 → 1.000 over t = 51.5 → 51.69 with the seal active. The freeze hypothesis is dead, and M4 died with it |
| Steepen the ramp (tanh, zero by r = 1.0) before widening the window | ~~Adopted as M4b~~ **Superseded by the M4 measurement**: the 0.95 seal bought 0.015 units, so a sharper edge at the same radius seals nothing. M4b became the four-arm sweep |
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
| `merger_fix/val_ahfix_r04000` | fixed θ kernel, **no damping**, from t = 40 | 51.71 | the M2+M3 gate: artefact gone, real horizon found at 51.03/r = 1.0625, evolution bit-identical to r03000 to t ≈ 44.9 |
| `merger_fix/m4_sealed_r04000` | radius window r < 0.80/0.95, engaging t = 51.2, lapse window off | 51.69 | M4 FAIL: the certified seal bought 0.015 units; killer measured at r ≈ 0.95–1.3, outside the window; NaN in h11 |
| `merger_fix/m4b_wide_r05000` | radius 1.00/1.30 from t = 50, τ 0.25 — from M4's clean Chk05000 | 51.94 | NaN in h11 — window over the ring bought 0.25 units |
| `merger_fix/m4b_combo_r05000` | lapse 3e-2/1e-3 **+** radius 1.00/1.30 from t = 50 | 51.94 | NaN in h11 — identical to wide: the lapse window added nothing |
| `merger_fix/m4b_fast_r05000` | radius 1.00/1.30 from t = 50, **τ 0.05** | **52.42** | NaN in h11 — outlived every τ = 0.25 arm and the undamped arm: **the rate is the control variable** |
| `merger_fix/m4b_sledge_r05000` | radius 2.00/2.50 from t = 50, τ 0.25 | 51.91 | NaN in h11 — damping the *whole object* at τ 0.25 changed nothing: window size falsified |
| `merger_fix/m4b2_vfast_r05000` | radius 1.00/1.30 from t = 50, τ 0.02 | 51.88 | NaN in **K** — 2.5× past the optimum gave all the gain back and shocked the gauge: rate axis peaked at τ ≈ 0.05 |
| `merger_fix/m4b2_fastsledge_r05000` | radius 2.00/2.50 from t = 50, τ 0.05 | **52.55** | NaN in h11 — nominal record among damped arms, but +0.13 over fast is inside the scatter: coverage falsified at the winning rate too |
| `merger_fix/m4b2_fastcombo_r05000` | lapse 3e-2/1e-3 + radius 1.00/1.30 from t = 50, τ 0.05 | 52.42 | NaN in h11 — identical to fast: lapse selection adds nothing at any rate |
| `merger_fix/m4c_freeze_r05000` | matter τ 0.05 ring + lapse-source taper 1.00/1.30, from t = 50 | 52.04 | NaN in h11 — taper negated the matter gain: −0.4 vs its matter-only twin |
| `merger_fix/m4c_freezewide_r05000` | matter τ 0.05 ring + lapse-source taper 2.00/2.50, from t = 50 | 52.03 | NaN in **h12** — first off-diagonal death; covering the pockets changed nothing |
| `merger_fix/m4c_freezeonly_r05000` | **no matter damping**, lapse-source taper 2.00/2.50, from t = 50 | 52.12 | NaN in h11 — ≈ undamped baseline (52.09): slicing source is not the killer |
| `merger_fix/m4d_dt001_fast_r05000` | dt_multiplier 0.01 (2× cut) + matter τ 0.05 ring | *(live)* | wave 4: dt axis, best-known config |
| `merger_fix/m4d_dt001_plain_r05000` | dt_multiplier 0.01, no damping | *(live)* | wave 4: dt axis in isolation |
| `merger_fix/m4d_dt0005_fast_r05000` | dt_multiplier 0.005 (4× cut) + matter τ 0.05 ring | *(live)* | wave 4: amplified dt signal |
| `merger_fix/m4d_sig002_fast_r05000` | sigma 0.02 (5× down) + matter τ 0.05 ring | *(live)* | wave 4: dissipation lowered along the measured trend |
| `merger_fix/m4c_freezeshift_r05000` | matter τ 0.05 ring + taper 2.00/2.50 + shift/B RHS × (1−W), from t = 50 | 50.24 | NaN in K — the shift guard is fatal: strangling the Gamma-driver mid-collapse kills in 0.24 units, the fastest death on record |

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
    2026-09-01; all pre-fix θ columns tainted; timeline rewritten. **Fix validated
    the same day** on a dedicated undamped restart (M2+M3): silent through t = 51.02
    where the old scan cried merger, first genuine trapped surface at t = 51.03 and
    r = 1.0625 — 0.7 % from the offline scanner, inside one cell — and the evolution
    bit-identical to the pre-fix run. The old scan had also missed the *real* horizon
    entirely; the instrument was wrong in both directions.
12. **Post-floor, the run is not reproducible from its own checkpoint.** Restarts
    agree to every printed digit until χ first touches min_chi (t ≈ 44.9), then
    diverge: separation 0.477 vs 0.569 at t = 48, deaths 0.35 units apart. Floor
    clipping plus non-deterministic GPU reductions; there is no bug to fix. **Effect
    on claims:** the physics repeats (horizon ≈ 51, death ≈ 52) but the trajectory is
    a sample, not a replica — quote per-run numbers per run, and pitch no overlap or
    convergence claim tighter than the scatter between two restarts of one arm.
13. **Checkpoints were never being deleted and ~10 GB each.** `--keep-last` only ever
    covered plotfiles, so the death-window cadence the plan now requires would strand
    ~50 GB per run. **Fix:** `checkpoint_keep` in `GRAMR::checkPoint()` (own module,
    `Source/GRTeclynCore/CheckpointRetention.hpp`), pruning only after a successful
    write, never a checkpoint lacking a complete `Header`, never the one the run was
    restarted from, and default 0 = keep everything so no archived run is touched.
14. **A causally sealed window engaged at certification buys nothing.** M4: the
    r < 0.95 seal, gated to t = 51.2, died at 51.6925 (NaN in h11) — 0.015 units
    before the undamped death — while the damping demonstrably worked where it
    reached (|φ|max 0.82 → 0.57 at engagement, then stalled; |Π|max grew to the
    end). Two lessons, both measured: the killer sits at r ≈ 0.95–1.3, outside any
    inside-horizon window; and rw's 55.00 came from *early* engagement (t = 50, on
    an inherited-clean core), not from its window's shape. Certification-first
    sequencing sacrifices the run to save the proof — the M4b sweep inverts that
    and buys the proof back through the M6 overlap test.

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
| damping windows combine as `max(w_lapse, w_radius)` | the lapse branch fires whenever damping is on, so a radius-only window needs `core_damping_lapse_start = 0` — otherwise the damped region is not bounded by a constant radius and the causal-seal proof has nothing to stand on |
| restarting from a checkpoint that already carries damping | Chk05000 damps straight through the collapse M7 must record; restart earlier and gate the window by time instead |
| relative paths handed to `run_single.sh` | it `cd`s into the run directory and uses `WHM_EXE`/`WHM_RUNS_DIR` verbatim — a relative value dies as exit 127 or `Couldn't open …/params.txt`, and the stub run directory must be removed before retrying |
| comparing two restarts of one arm past the floor | they decohere at t ≈ 44.9 by construction — no claim tighter than the run-to-run scatter |
| certification-gated damping engagement | engaging at t = 51.2 on a full-strength scalar reproduced the undamped death to 0.015 units; the cure must precede the crisis (engage ≤ t = 50) and publishability is recovered through the M6 overlap test, not the engagement clock |
| re-opening closed cures | resolution (ml2/base/n160 ladder, ~90× compute for t = 60) and Kreiss–Oliger dissipation (sg10 died earlier) are both measured dead ends — spend GPUs on window shape, rate and engagement time instead |

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
