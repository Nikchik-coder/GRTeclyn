# GPU plan for the paper runs

Companion to `Plan.md`, which holds the campaign record; this file holds the
design and the decision ledger for the production data behind the article.
**Nothing here launches without a by-hand approval, one run at a time,
through `run_single.sh`.**  Rewritten 2026-09-03: compacted, duplications
removed; the full narrative history is in this file's git history.

*Second external review absorbed 2026-09-03.  Adopted: the credibility batch
(#13-#17, runs before production), the fast-characteristic ceiling (§6), the
restart-recipe documentation (§5), the Helfer mechanism (§1), the BBH
known-answer calibration (§7.8).  Checked against the tree and REJECTED — do
not re-import: "p020's Chk05000 exists, 2 GPU-h restart" (the sweeper took
every p020_nofill and plain-twin checkpoint — uninsured names; only the 3
held plotfiles survive); "Plan.md states the sqrt(2) characteristic" (no such
line exists — the physics is adopted on its own merit); the hardcoded
x>0 / x<0 tracker split (the binary's axis rotates with the orbit — the
argmin-neighbourhood fix of §9 stands).*

---

## 0. The plan

**In flight**

- [x] **#1 p015 scout — ANSWERED 2026-09-03: p = 0.15 is on the FUSING
  branch, but the wall cut it short of coincidence.**  Died t = 53.35 (h11
  NaN, level 3 — the wall, slightly late).  The sequence, slice-audited
  (tracker + slices agree): plateau at pit sep 0.816 (p012's plateau was
  0.815), dive to 0.69–0.70 by t = 50.5–53.0, core lapse RISING 0.13 → 0.21
  (p012's endgame signature; p020 never showed any of this — it hovered at
  1.08 with falling pit lapse), χ on the floor from t = 50.5.  But the pits
  never closed to p012's 0.2–0.6 coincidence: fusion was in progress, not
  complete, when the wall hit.  Production implication: p = 0.15 is a real
  candidate but needs the restart-refinement recipe (#17-style, wall
  pushed ~+1.4/level) or a later-armed fill to finish; p = 0.12 remains the
  proven IVP.  Checkpoints were LOST (uninsured name — sweeper rule now
  fixed to cover all p-scan names); the last 3 plotfiles (t = 52.0/52.5/
  53.0, post-dive) are HELD on scratch for the horizon scan alongside
  p020's.  **RERUN with insurance (2026-09-04):**
  `merge_orbit_flip_d12_p015_rr_t060` (card 0, identical template)
  reproduced the wall at **t = 53.35 — the very same step (5335) as the
  original: the wall is deterministic at this resolution** — and this
  time the checkpoints survived:
  **Chk05000 (t = 50) held** plus a sweeper-proof `hold_seed_t50` hardlink
  copy — the seed for phase 2 (restart at max_level 5, ~+1.4 wall units
  per level, aiming the wall past the ~53–54 fusion completion).  Its own
  death plotfiles (t = 52.0/52.5/53.0) held too.
  (Superseded queue text kept below for the record.)
- [~] *(was)* **p015 scout** — `merge_orbit_flip_d12_p015_nofill_t060`, card 0.
  Does p = 0.15 fuse before the t ≈ 52 wall?  Fuse → production-p candidate
  (~10–15 % more m = ±2 signal, longer whirl); hover like p020 → the
  "captures but cannot fuse" boundary moves down to 0.15 and p = 0.12
  stands.  Reference marks: p012 crossed sep 2.0 at t ≈ 32 and fused by
  48–51; p020 hovered at 1.08; the wall ≈ 52.  Sub-2 separations are a
  tracker artifact — read the slices.  Last read t = 34.3, sep 1.69: no
  call yet.
- [x] **#2 BBH control to t = 150 — DONE (2026-09-03), all four close-out
  checks pass.**  `bbh_control_d12_p012_t150` reached t = 150 on card 2.
  (1) Instruments agree: Python consumer (plotfiles, fixed center) vs
  in-code stream match to 0.31 % / 0.35 % of peak (R = 14 / 30), corr
  0.999999 — the center bug is retired.  (2) Known-answer ringdown: fitted
  period 28.8–29.7, damping tau 25–27 (late-window 28.9 / 22.9), i.e.
  ~15.2 M / ~12.1 M for M_f ≈ 1.9 — consistent with a Kerr remnant of
  M ≈ 1.9–2.0 with modest spin (Schwarzschild reference 16.8 M / 11.2 M;
  spin shortens the period exactly as seen).  Both radii agree within
  3–7 %.  (3) Boundary audit at t = 150 (full-domain plotfile scan +
  slice-cache time series): chi scatter *decreases* outward (0.33 % →
  0.26 %), max |K| in the outer shells 4e-4, no growing ripples —
  Sommerfeld held for 150 units with no sponge; pre-signal junk floor at
  R = 30 is 12 % of peak but sits entirely before the chirp, and R20→R30
  envelope coherence bounds in-band contamination at ~3.5 %.  (4) Signal
  comparison at equal R = 14: BBH peak (2,2) 1.08e-2 vs wormhole p012
  2.49e-2 — the wormhole is ~2.3x louder (understated: the twin stream
  cut at t = 44, before collapse finished radiating).  Remaining: repack
  + paper figures with R = 30 (after the drain completes).

**Next — cheap, no GPU conflict, one approval each**

- [x] **#3 p012 horizon re-check — ANSWERED (2026-09-04): the offline scan
  confirms the trapped shell at r ≈ 1.**  Run on the nodamp twin's held
  death plotfiles (twin ≡ plain per #14; level 3): outermost fully-trapped
  shell r = 1.11 / 1.09 / 1.07 at t = 50.5 / 51.0 / 51.5, vs the in-code
  refined-run r = 1.0 at t = 51.06 — a different run, different resolution,
  different implementation, same verdict.  The standing caveat stands
  unchanged: both instruments read the same chi-clipped state, so this is
  supporting, not decisive — the decisive word is the from-t = 0 low-floor
  twin (nodamp_cf10, in flight).
- [x] **#4 p020 horizon scan — ANSWERED (2026-09-04): p = 0.20 has a
  credible common trapped surface, larger than p012's.**  All 3 held
  plotfiles scanned (CLI variant of `ah_radial_scan.py` added:
  `--center/--half/--level`, defaults unchanged for the pack script):
  outermost fully-trapped shell r = 2.07 / 2.11 / 2.13 at
  t = 51.0 / 51.5 / 52.0 (ray-mean r_AH 2.72–2.74, 78 % of rays).
  Credibility checks PASS where helfer/p035 failed: K on the r = 2.1 shell
  is 0.04 mean / 0.13 max — nowhere near the K ≈ 1 blob rim — and the
  shell sits in healthy data (chi ≥ 0.10, lapse ≥ 0.09, five orders above
  the floor), unlike p012's shell.  Plotfiles NOT deleted yet: #13
  explicitly needs these same 3 files — delete after #13 runs.
- [ ] **#5 L = 128 / N = 256 smoke test** — t = 5; measures memory (~75 GB
  estimate, tight) and speed; decides L = 128 vs the L = 96 fallback (§4).
- [x] **#6 Production templates — DONE (2026-09-04, params-only, nothing
  launched).**  `templates_scan/params_prod_L128_p012_t060.txt` (headline)
  and `params_prod_L96_p012_t060.txt` (s4 fallback: sponge 40→48, radii
  20/26/32/38), both derived from the smoke template whose extraction
  block (radii 20/28/36/44, levels 0, l ≤ 4 all m, points 24/37) the live
  smoke run is validating right now; production deltas: stop_time 60,
  checkpoints ON every 10 units keep 3, probe key dropped.
  `launch_production_L128.sh` carries `--scalar-modes 0 1 2` in
  `WHM_CONSUME_ARGS` (the s4 non-vacuum-exterior defence) and a VARIANT=L96
  switch; both variants dry-run clean.  Launch gated on the #5 memory
  number and explicit approval.
- [ ] **#7 Launcher hardening** — `run_single.sh` falls back to the grid
  centre or refuses to start when the params has no `center` key (the
  consumer-junk bug, §1).  Only after the current runs end — the script is
  live under two launchers.
- [ ] **#8 Repulsion a-points** — a = 1.5 and 3 at rest, level 3–4, t ≈ 20,
  initial acceleration; scalar-charge prediction F ∝ q_A·q_B attached
  (§7.6).  Hours.
- [x] **#9 Wave-8 close-out checks — ANSWERED (2026-09-04): the second
  peak is a real outgoing wave, and the tail past the ceiling is clean.**
  (a) The R = 14 second peak (t = 75.1, rΨ₄ = +1.63e-2) reappears at
  R = 30 at t = 94.0 — delay 18.9 vs the wave-7 main-signal lag 18.0 —
  with rΨ₄ ratio 1.085 vs 1.0 for pure 1/R (R = 30 is in-sponge; shape
  and timing only, per the wave-8 caveat).  Identical in both arms.
  (b) Tail past the causal ceiling 84.5: the seam-radius twins (fill vs
  fillwide) agree to 0.09 % of the tail peak, corr 1.000000 — the tail is
  not seam-written; the R = 30 late data is usable.

**Credibility tests — run BEFORE any production launch.**  They decide
what the production arms are allowed to claim.  All level-3 runs or short
restart segments, ~1 day of one card total.  (2026-09-04: two t = 50 seeds
now exist — nodamp Chk05000 for #16, p015_rr Chk05000 for the p015
phase-2 refinement — both with sweeper-proof hold copies on scratch.)

- [ ] **#13 Blob nature test — no GPU.**  Gauge-invariant scalars at the
  inter-throat midpoint from existing plotfiles (the 3 held p020 files of
  #4, plus packed p012/helfer ones): the Hamiltonian-constraint field, the
  energy density (its sign!), the areal radius of small spheres about the
  midpoint; Kretschmann if derivable.  Curvature bounded while the lapse
  runs to 1e-10 = slicing; curvature and constraint growing together =
  constraint mode.  Hypothesis to test, not assume: the phantom gradient
  peaks at the φ = 0 midpoint, so the blob may be a genuine negative-energy
  sink the throats dug between themselves — a paper paragraph if measured,
  a retraction risk if asserted.
- [x] **#14 Damping-off p012 plain twin — ANSWERED (2026-09-04): damping
  changes nothing that matters.**  `merge_twin_p012_nodamp_t060` died at
  **t = 51.53** (h11 NaN, level 3) vs the plain twin's 52.06 — the wall
  moved by 0.5 units (~1 %), within the arm-pair noise floor, so damping
  neither causes nor delays the wall.  Pre-collapse the twins are
  numerically indistinguishable: at t = 32 sep/mid-lapse/|φ|/activity all
  match plain to 3 decimals (files verifiably different, max |Δφ| = 0.0056).
  Verdict: every scan/twin result stands as-is with damping off, and the
  production config (damping off) is now measured, not assumed.  Assets
  held: **Chk05000 (t = 50) — the #16 ladder base** — plus a sweeper-proof
  `hold_seed_t50` hardlink copy; death plotfiles t = 50.5/51.0/51.5 on
  scratch; in-code streams complete to 51.53.
- [x] **#15 Gauge-change arm — ANSWERED (2026-09-03): the physics
  survives the slicing change, the WALL TIME does not.**
  `merge_twin_p012_lc1_t060` (single knob: lapse_coeff 2.0 → 1.0) died at
  **t = 43.64** (K NaN, level 3) vs the plain wall at 52.06 — the wall
  moved **8.4 units earlier**, which is the pre-registered "gauge" branch
  of the test.  But the physics sequence held: blob nucleated on schedule
  (t = 32 slice: mid lapse 0.009, |phi| 0.53 — deeper/stronger than
  plain, as a slower lapse response should give), capture and plunge
  proceeded, sep 0.442 at death.  Reading: the crash is the slicing
  losing its singularity-avoidance race (halving lapse_coeff weakens the
  gauge's protective collapse, so the code meets the forming singularity
  ~8 units sooner) — **the t ≈ 52 number is a property of gauge +
  resolution, not a physical event, and the paper must never present it
  as one.**  The physical claims (blob, capture, fusion sequence) are
  what survived; p012's headline is untouched (its fusion completed at
  48–51, before its wall).  Assets held: Chk04000 (t = 40), death
  plotfiles t = 42.5/43.0/43.5, in-code stream complete to 43.64.
  (Wave 3a tested the source term, not the slicing — different question.
  The shock-avoiding lapse f = 1 + kappa/alpha^2 would need code; not
  worth it now that the params-only arm has answered.)
- [ ] **#16 χ-floor ladder** — `min_chi` is a flat params key (production
  value 1.0e-8): restart segments t = 50 → ~53 from the #14 base **(in
  hand: nodamp Chk05000, t = 50, hold copy on scratch)** with levels 4–5
  added, at min_chi 1e-8 / 1e-10 / 1e-12 (~1–2 h each).  A
  horizon that moves with the floor is the floor.  Extend the ladder read
  to the R = 14 waveform over the shared window — floor-independence of
  the signal is the check a referee will demand on seeing "χ clipped at
  t = 44.9".  This ladder, not the author, answers §8 decision 7 (whether
  the horizon sentence is in the paper).
- [ ] **#17 p020 restart-refinement** — the only version of "does p = 0.20
  fuse" that tests what it claims: fresh L3 p020 to t ≈ 50 with insured
  checkpoints (~5.5 h), then levels 4–5 added at the checkpoint — the m4e
  recipe that bought the p012 family +1.4 units of wall per level.  The
  from-t = 0 L5 arm got none of that gain (χ clipped at the pits at t = 0,
  §9).  This run rescues — or honestly kills — the capture-boundary
  figure; same recipe p015 needs if it hovers.  (2026-09-04: #4's offline
  scan already finds a credible L3 common trapped shell at r ≈ 2.1 in
  p020 — the boundary figure starts from strength.)

**Production — blocked on the open decisions (§8)**

- [ ] **#10 Headline arm** — p = 0.12 plunge at L = 128, max_level 5,
  extraction per #6; plus seam twin, third-fill-radius arm, level-6
  companion (§4–6).
- [ ] **#11 Comparison arms** — head-on freeze arm (§7.1); N = 192 wave-zone
  twin (§7.3) and the +150 tail if taken (§8).

**Analysis once the data lands**

- [ ] **#12** 4-radius extrapolation in retarded time (measured speed
  1.125×); **proper separation** — integrate ~χ^(-1/2) along the pit axis
  from the slice cache, the invariant answer to "static or still closing"
  that coordinate sep 1.08 cannot give; energy/mass balance with the
  negative scalar flux (§7.2);
  remnant-mass QNM discriminator (§7.4); dissolution re-measured on the
  undamped arm (§7.5); frames re-rendered with colour limits taken outside
  r = 3 (Plan.md issue 17); pack + push.

**Minimum publishable set** if the clock runs short: headline arm + seam
twin + level-6 twin + BBH control (done) + head-on.

---

## 1. Decision ledger — settled, with the number that settled it

- [x] **Production p = 0.12** (user, 2026-09-03).  Only p that completes a
  merger: p020_nofill died at t = 52.08 with the throats pinned at sep 1.08
  from t = 46, never fused (slices at t = 46/49.5: two intact cores,
  |φ| = 0.87, midpoint collapse deepening).  p015 (#1) is the one live
  challenger — a fusing p015 upgrades the choice, a hovering one confirms it.
- [x] **The t ≈ 52–53 wall is resolution-independent.**  Level-5 vs level-3
  deaths: p020 52.07 / 52.08, p025 52.79 / 52.98 — same h11 NaN, and the L5
  slices show two intact throats (|φ| ≈ 0.92, pit lapse ~0.18) with the
  inter-throat midpoint collapsing (lapse ~3.5e-3, max|K| 0.6–0.7).
  From-t = 0 depth does not move the wall; "p ≥ 0.20 does not fuse before
  the wall" is established on two independent p's.  Validated per arm:
  monitor death event + the run's own abort log + stream last row.
  **Caveat (second-pass review, adopted):** the from-t = 0 L5 arms are not
  a clean refinement rung (χ clipped at the pits at t = 0) and both died
  with the NaN on level 4, not the finest level; the restart-refinement
  recipe that bought the p012 family +1.4 units/level was never applied to
  p020.  Until #17 runs, "captures but cannot fuse" describes a NaN, not
  physics, and the capture-boundary figure is not publishable as a
  boundary.
- [x] **Helfer/Ning correction REJECTED for production.**  The decisive
  twin: plain merged (retraced the p012 record, sep 0.81 by t = 44); helfer
  stalled at sep ≈ 4.7 (7° of orbit over t = 26–34 vs plain's 35°),
  converged at L3 = L4 (< 2 % lapse-trace agreement).  Mechanism (§9): the
  midpoint lapse-collapse blob nucleates 5 units earlier (3e-2 at t = 25.4
  vs 30.4) and the throats stall against it.  The w = 2 window test killed
  the placement excuse (sep 5.22 at t = 32.0 — worse than the wide window);
  helfer_lvl5 was stopped at t = 31.5, stalled like L3/L4.  The flag stays
  in the code, default off.  Production runs plain superposition; the
  measured +8–11 % initial-size artefact is the price of an evolution that
  evolves.  Static trade recorded in §4.  **Mechanism (second pass):**
  du = −0.0834 = −M_B/d — the subtracted "constant" is the companion's
  Newtonian potential at the throat, so the windowed subtraction leaves a
  spurious potential shell at r ≈ w around each body, and the stall
  follows; w = 2 braking *earlier* than w = 4 fits (closer shell).  Paper
  wording: a correction designed for conformal-factor mass is inapplicable
  when the mass lives in the lapse; the honest alternative is a
  constraint-solved IVP, and the affordable substitute is the d = 16–18
  robustness arm (§8 decision 8).
- [x] **BBH vacuum control FINISHED CLEAN** (`bbh_control_d12_p012`,
  t = 100, no NaN; matched IVP: ADM ≈ 1 each, d = 12, p = ±0.12, wormhole
  box and spheres).  Vs the wormhole p012 twin: punctures met at t ≈ 70 vs
  throats fusing 48–51 — the scalar clouds buy ~20 units of faster infall
  (sep at t = 30: 10.3 vs 2.7); l = 2 m = 2 peak at r = 14: 0.0108 vs
  0.0249 (wormhole 2.3× brighter); m = 0: 0.0032 vs 0.0176 (5.5×); the
  Newtonian pericenter-at-43 guess was wrong — the plunge steepened through
  it.  Ringdown only ~4 % decayed by t = 100 → the t150 rerun (#2).
  Packed; figures from the C++ in-code streams (merger peak propagates at
  0.906c): `psi4_analysis_bbh_control{,_m2}` and the object-vs-object
  `bbh_vs_wormhole_psi4` from the new `grteclyn_wrapper.visualisation.merger`
  module.
- [x] **The consumer center bug — found and fixed.**  The BinaryBH params
  had no flat `center =` key; `run_single.sh` greps exactly that key for
  the consumer's `--center`, whose silent default is the DOMAIN CORNER
  (0,0,0) — the t100 consumer psi4 files are junk (static ~0.006 "modes",
  no rotating phase).  The C++ in-code stream is unaffected
  (`weyl_extraction.center` defaults to the grid centre), so every figure
  and quoted number stands.  Wormhole-side control on p020_nofill: C++ vs
  Python agree to 0.2 % (complex ratio 1.0022 − 0.0072i) — the chain is
  sound.  Both BBH params files now carry `center = 32.0 32.0 32.0`; the
  t150 run was killed 20 min in (user's word) and relaunched on the fixed
  params.  Launcher-side fix is #7.
- [x] **In-code extraction is the primary waveform instrument.**  Two ghost
  bugs fixed (interpolator ghost count 2 → 3; matter-sector derived
  functions never filled ghost cells — stale arena memory on ~55 % of
  sphere points), validated by a kernel printf count and a 1 776-point
  plotfile cross-check (0 plateaus, 0 NaN); mode integrals reproduce an
  independent Simpson quadrature to 1e-8 at both radii.  50× finer sampling
  than plotfiles (every coarse step, dt = 0.01).  The consumer Ψ₄ is
  demoted to cross-check; the code-only fix subset is submitted upstream
  from `fix/derived-ghost-cells`.
- [x] **Check E on the drainhole branch: d = 12 needs no apology, but the
  defect is real.**  d/b = 6 costs 1.58× the old d/b = 8 gate on a smooth
  A ~ d^-1.6 power law (no cliff in 4 ≤ d/b ≤ 12); Bowen–York momenta add
  1.9 %.  But the superposition defect (2.87e-4 at d = 12) sits 100–600×
  above the discretisation floor at every separation — over the refined
  region it, not truncation, is the dominant t = 0 error.  Table in §4.
- [x] **Capture boundary between p = 0.25 and 0.35.**  p ≤ 0.25 is captured
  (then hits the wall); p035 (min sep 2.75 at t = 42.4) and p045 (min sep
  3.95 at t = 40) are fly-bys with surviving throats (§3).
- [x] **max_level 5 for production, 6 as companion, 7 never by default**
  (m4e ladder, §5): pair-mean death ladder linear at +1.43/level against a
  ±0.35 reproducibility floor; refinement priced out as a route; damping's
  effect on death time is zero — production runs the clean config.
- [x] **Wording rule: "core freeze" → "inter-throat lapse collapse".**  The
  throats never collapse (pit lapse 0.05–0.24, |φ| 0.79–0.92, every run,
  every epoch); what collapses is the midpoint blob (§9).  The freeze
  module keeps its name; the physics claim changes.

**Withdrawn — do not re-import:** the 1/dx² initial-data-noise argument
(n160's own t = 0 row refutes it); the whole-domain `L2_Ham` as a
convergence metric (93.7–99.98 % of it lives in the 2-cell boundary-ghost
layer, §4); "death time bounded 56–57 over levels 5–7"; per-throat scalar
charge from check F (single throat, angular-mean estimator — cancels on the
flipped binary); the lighthouse mechanism (m = ±2 rings at 17.3, not 2× the
dipole precession, §6); "the cores collapse" (it is the midpoint, §9); the
p045 "common horizon at t = 43.3" (documented theta false positive).

---

## 2. Results in hand (the paper's spine)

| Result | Status |
|---|---|
| **Like-oriented throats repel** — 5× gravity at a = 2, m = 1; push scales with throat width, not mass; pull/push 1.50 vs 6/4 predicted | three control arms, 2026-08-31 |
| **Opposite-oriented throats attract and merge** — gravity-driven; common trapped surface at r ≈ 1.0 confirmed by two instruments (in-code refined run + offline twin scan, #3); p = 0.20 has its own, larger one at r ≈ 2.1 that passes the K-rim filter (#4) | #3/#4 closed 2026-09-04; floor-independence pending nodamp_cf10 |
| **The wall (t ≈ 52 death) is gauge + resolution, not physics** — one gauge knob moves it 8.4 units (#15); it reproduces on the identical step (#1 rerun); refinement pushes it +1.4 units/level; damping does not touch it (#14, Δ 0.5 units ≈ noise) | credibility batch, 2026-09-03/04 |
| **The merger's true peak is measured: \|rΨ₄\| (2,2) = 2.96e-2 at R = 14, t = 55.5** — ~3 units past the wall, via the freeze; R = 30 confirms (2.996e-2 at t = 73.5, lag 18, 1/R to 1.3 %); freeze arm matches the unfrozen twin to 0.7 % pre-wall.  L = 64 box — production re-measures clean | freeze chain, computed 2026-09-04 |
| **The interior freeze survives the merger; the signal is a genuine GW** — speed, 1/R falloff, static-offset and not-freeze-junk checks; second peak propagates 14 → 30 with the measured lag and clean post-ceiling tail (#9) | closed 2026-09-02; #9 2026-09-04 |
| **Same IVP, different object** — the wormhole merger beats the vacuum BBH by ~20 units of infall and 2.3× (m = 2) / 5.5× (m = 0) in brightness | BBH control, 2026-09-03 |
| **Flybys radiate a real GW burst, louder in raw peak than the merger** — p035 4.5e-2, p045 5.6e-2 (rΨ₄ (2,2), R = 14), both propagating 14 → 30 with the right delay; merger peak 2.96e-2.  Faster encounter, stronger bremsstrahlung burst; the merger's edge is the chirp + ringdown, not the peak.  Caveats: p045 R = 14 past t ≈ 70 is ejected phantom crescents crossing the sphere, not GW; t = 10–20 bumps are ID junk | computed 2026-09-04 |
| **p = 0.15 outradiates p = 0.12** — 3.05e-2 at its wall and still rising, already above p012's *complete* peak (2.96e-2); the fusing branch is the louder merger | partial (wall-cut); p015_lvl5 in flight |

Freeze-method validation (the method section): the seam-radius twins agree
to 5 digits at every shared waveform sample; the frozen arm is bit-identical
to its unfrozen twin beyond r = 6 at t = 55; late engagement (55.5 vs 53)
moves the R = 14 window ≤ 0.003 % (m = 2) / 0.022 % (m = 0); constraints
stay flat for 27 units post-freeze.

---

## 3. The p-scan record

IVP family: d = 12, opposite orientation, tangential momenta ±p.  Circular
at d = 12 needs p ≈ 0.5 (measured 6× coupling); Newtonian escape ~0.7.

| p | run(s) | outcome |
|---|---|---|
| 0.12 | production family | merges: sep 2.0 at t ≈ 32, fusion 48–51 — the headline plunge |
| 0.15 | p015_nofill, p015_rr | fusing branch, wall-cut mid-fusion (dive to 0.69, lapse rising); wall at 53.35 in both, same step — needs the #17 recipe to finish (#1) |
| 0.20 | p020_nofill, p020_lvl5 | captured; hovered at sep 1.08–1.19; wall at 52.08 / 52.07 — cannot fuse |
| 0.25 | p025, p025_lvl5 | captured to sep ~1.5–1.9; wall at 52.98 / 52.79 — cannot fuse |
| 0.35 | p035 | fly-by: min sep 2.75 at t = 42.4, receding when stopped |
| 0.45 | p045 | fly-by: min sep 3.95 at t = 40, outbound at stop (t = 84); no checkpoints, not resumable |

p045 post-encounter physics (kept for the paper): the throats survive the
pass (φ lobes −2.5 % over 84 units; the χ wells relax, not collapse); two
χ > 1 phantom crescents are ejected; the cores deflect a quarter-turn.  The
transient stretch passes in ~10 units — the collapse branch wants the
sustained squeeze only a capture delivers.  Its `theta_common`/`ah_r_common`
columns carry the documented false positive; trajectory + matter + log-χ
frames are the instruments.  Figures: `results/merger/figures/p045_flyby_*`.

**Fuse audit — a scout qualifies its p only if both throats are still
throats at periapsis**, read from the slice cache, never the tracker (it
under-reads speeds up to 4× and degenerates below sep 2, §9).  The
single-throat growing mode makes the 40 M window a fuse; a spiral IVP would
sit 3–4 fuses deep, so throat integrity through the orbit is the gate, not
trajectory alone.

stop_time is set per-IVP: t_collapse (from the scout) + 100, or + 150 if
the §8 tail decision is taken.

---

## 4. Production grid and extraction (the L = 128 proposal)

Current geometry: L = 64, N = 128 (base dx = 0.5), max_level 5 (finest
dx = 1/64); slice caches store only the central 32-wide window.  Wrong for a
paper waveform: R = 30 sits inside the sponge (24 → 32, ~13× base
dissipation, Plan.md issue 15); two radii cannot extrapolate R → ∞;
0.5-unit plotfile sampling aliased once already (the QNM comb).

**Proposal — same dx, twice the room:** L = 128, N = 256; sponge 48 → 64;
spheres at R = 20/28/36/44, all in un-sponged vacuum, ~30 base points per
dominant wavelength.  In-code extraction ON (#6) supersedes plot-cadence
sampling; plotfiles stay at interval 50 so the consumer remains a free
second source, plus its exclusive jobs (frames, scalar modes, kinematic
flux).  Cost estimate: 3.5–4.0 u/h at level 5 (vs 4.3 today); memory
~75 GB of 80 — the smoke test (#5) decides.  Fallback: L = 96 / N = 192
(sponge 40 → 48, radii 20/26/32/38).  MPI note: the known AMR crash is
radial-recipe-specific and the merger tags type 2; a 2-rank smoke test is
worth a slot — if it holds, the level-6 companion halves to ~3 days.

**Ψ₄ in a non-vacuum exterior** (|φ| ~ 6e-3 at R = 14): defend with the
measured 1/R falloff and the scalar-to-GW flux ratio per radius from
`--scalar-modes`; if that ratio is small and falls with R, extraction
stands on measurement, not assumption.

**Check E (drainhole branch, b = 2, 2026-09-02).**  Defect A from the
L2_Ham(N) = A + B·N^-p fit, N = 192/288/384, on the repaired metric — the
2-cell boundary layer dropped, because the whole-domain norm is unusable
(93.7–99.98 % of Ham² lives in the ghost-reading outer layer; with it
dropped, the exact single throat converges at 4th order to A ≈ 8e-7):

| ladder | A (defect) | vs error bar |
|---|---|---|
| single throat (exact zero control) | ~0 (8e-7) | — |
| d = 8 (d/b = 4) | 4.92e-4 | 603× |
| **d = 12 (d/b = 6, production)** | **2.87e-4** | **352×** |
| d = 16 (d/b = 8, old gate) | 1.82e-4 | 223× |
| d = 24 (d/b = 12) | 8.61e-5 | 106× |
| d = 12 + p = 0.35 momenta | 2.92e-4 | 359× |

Smooth A ~ d^-1.6, no threshold; momenta +1.9 % — the orbit parameters are
exonerated.  The defect does not converge away with refinement.  Validated
on two independent cell sets (ghost-drop vs r < 24: identical ratios).
Caveat: A is an unnormalised RMS — relative statements are solid; absolute
size needs Ham/Ham_abs_terms.  Trap: `amr.derive_plot_vars = constraints`
aborts unless `G_Newton` is in the params.  Runs:
`runs/wormhole_merger/checkE/`.

**Helfer correction, static trade** (a = 2, m = 1, d = 12, N = 192).  Plain
superposition starts each throat +8.1 % (away) / +10.9 % (toward) too large
(the companion's du = −0.0834 dominates dpsi by 24×), so it rings.  The
windowed subtraction (`wormhole_helfer_correction`, default off) repairs the
size at the price of window curvature (~1/w²) in Ham:

| window w / p | size error | L2_Ham vs plain |
|---|---|---|
| plain superposition | +8.1 % / +10.9 % | 1.00× |
| 0.4d / 6 (literal Helfer Eq. 45) | −1.1 % / +1.5 % | 9.02× |
| **d/3 / 2 (the default)** | **+0.2 % / +2.8 %** | **1.84×** |
| d/6 / 2 | +3.1 % / +5.6 % | 1.53× |

The dynamics verdict (§1) rejects the correction regardless; this table is
the method-section record of the trade.  Regression: flag off reproduces
the pre-change baseline bit for bit.  Operational: N = 384 needs
`WHM_RANKS=2` (55.5 GB/card, binding per the wrapper README); probe
templates carry `amr.checkpoint_files_output = 0`.

---

## 5. Resolution and freeze engagement

The m4e ladder (pair means, p012 family):

| max_level | u/h (one card) | death, pair mean |
|---|---|---|
| 3 | — | 52.26 |
| 4 | 9.0 | 53.43 |
| 5 | 4.3 | 55.18 |
| 6 | 2.2 | 56.42 |
| 7 | 1.1 | 56.20 (one arm, no twin) |

Linear at +1.43/level, scatter at the ±0.35 floor; level 7 is consistent
with saturation within noise but single-arm.  "The NaN lands on each newly
created finest level every time" held for every m4e (restart) arm — but
both from-t = 0 L5 binary arms died on **level 4**, and their death-step
plotfiles are deleted, so box coverage of the death site is unverified (at
t ≈ 29 the L5 boxes covered only the pits).  Treat the finest-level claim
as restart-recipe-specific until re-checked on #17.  Caveat (2026-09-03):
the p020/p025 level-5 arms died on the level-3 clock (52.07 / 52.79) — the
ladder's gain did not transfer to from-t = 0 launches; treat +1.4/level as
the restart recipe's, p012-family.

Production: **max_level 5** (cheapest grid that reliably reaches
engagement; level 4 is a coin flip against its own death); one **level-6
twin** of the headline arm as the convergence companion; level 7 only as a
paired restart segment around collapse if a referee demands it.

**The production recipe, explicitly:** level 3 from t = 0 through the
orbit, levels 4–5 added at a pre-collapse checkpoint, then the freeze —
the validated m4e path.  A from-t = 0 max_level-5 launch clips χ at the
pits at t = 0 and forfeits the ladder's gain (§9, the L5 arms).  The
paper's resolution study is therefore a restart-refinement study and must
say so.

**Engagement is a criterion, not a constant:** the collapse sources the
burst until ~51.5 (freezing earlier deletes signal); the arm must reach
t_e under its own power (level 5 clears it by ~2 units); and t_e sets the
contamination ceiling at every radius (§6).  For production: read
t_collapse and the burst end from the level-3 scout, confirm at level 5,
engage after the burst closes, print the ceilings next to the windows
before launch.  Fill 1.5 / 2.0-wide twin, seam twin, and one
late-engagement control re-run once at L = 128, unchanged from M9b.

---

## 6. Ringdown physics (m9b chain, R = 14, window t = 60–91)

**Established, each with its test:**
- The remnant is hairy: a dipolar phantom halo (|φ| ~ 6e-3 at R = 14) rings
  with the metric at one period; the trap is that an angular mean cancels
  the dipole to 1e-10 — the power is in the m = 1 azimuthal harmonic.

| signal at R = 14 | period |
|---|---|
| Ψ₄ (l = 2, m = 0) | ~17.3 |
| φ, m = 1 ring amplitude | ~17.0 |
| ∂t φ, m = 1 ring amplitude | ~17.7 |

- Phase-locked channels: |r| = 0.95 at lag +0.5 units (a quarter-period
  would be 4.3) — one coupled Einstein–Klein–Gordon eigenmode.
- Long-lived but decaying: τ ≈ 150, Q ≈ 28 — 10× a vacuum Schwarzschild
  l = 2 ringdown; τ from 1.8 cycles carries large error bars.
- Not a freeze artifact: 15 % change in fill radius moves the period ~2 %
  (fill 17.3/17.0/17.7 vs fillwide 17.7/17.7/18.0) and the dipole
  precession rate 0.2 % (0.1537 vs 0.1540 rad/unit).
- The story closes on the initial data: merging a ± scalar pair is exactly
  what leaves a scalar dipole on the remnant.

**Refuted — keep out of the paper:** the lighthouse mechanism.  Prediction
m = ±2 period π/0.1537 = 20.4; measured 17.3, same as m = 0, phase drift
0.187 rad/u ≠ 2 × 0.154.  The ~41-unit dipole precession is a separate,
slower clock; the driver is the halo's amplitude breathing.

**The causal budget:** the burst arrives at ≈ t_c + 1.125·R; freeze
contamination from r_s = 2 arrives at ≈ t_e + 1.125·(R − 2).  Every radius
gets the same ~6–8 freeze-clean units — pushing spheres out buys
sponge-clean amplitude, not freeze-clean time.  **Fast-characteristic
caveat (second pass, adopted):** the seam is a constraint source and CCZ4
gauge/constraint modes run up to ~sqrt(2)× local light, so the conservative
ceiling at R = 14 is ≈ 62.5, not 66.5 — inside the burst window.  The real
defence is empirical (the late-engagement control moved the window
≤ 0.003 %): quote that, and print the ceilings at the fast characteristic.  **The whole 17-unit-period
ringdown sits inside the freeze's causal cone at every radius**; its
credibility rests on freeze-insensitivity.  Hence, on the production arm: a
third fill radius (a flat trend, not a two-point difference); the
engagement pair re-run at L = 128; and the causal-arrival plot printed
under every published waveform, clean window shaded per radius.

Standing caveats: the azimuthal ring harmonic is not a proper l = 1 mode
(production's scalar-mode spheres fix this); phantom matter means
"signature of this class of exotic matter", not an astrophysical
prediction; no ringdown convergence point exists until the level-6 twin.
Figure + script: `runs/wormhole_merger/merger_fix/plots/scalar_vs_psi4_R14.*`.

---

## 7. Comparison arms and analysis items

1. **Head-on freeze arm** — the only configuration with a literature number
   (BBH head-on from rest radiates ≈ 0.055 % of M, l = 2 m = 0); with the
   BBH control it makes the paper's energy-budget table.  Shortest
   production run on the list.
2. **Energy/mass balance** — M_ADM(t) at the boundary vs E_GW from the
   in-code Ψ₄ (double-integrated, static offset removed) plus the
   *negative* scalar kinematic flux.  Either the sum closes or its failure
   is a finding.  Consumer-side; no new runs.
3. **Wave-zone convergence** — R = 20–44 sit on level 0 at dx = 0.5 in
   every arm; the extracted waveform has no convergence factor of its own.
   The N = 192 twin is a *coarse* rung (dx = 2/3, ~22 points per dominant
   wavelength at 4th order) — legitimate, but the plan must call it a
   coarsening.  The cheaper refined third point is a static level-1 box
   tagged out to R = 44 inside the headline arm (decision §8).
4. **Remnant-mass QNM discriminator** — the 17.3-unit period is what a
   vacuum BH of M ≈ 1.03 rings at; this system's ADM ≈ 2 would ring at
   ~34.  If M_remnant ≈ 2 (from item 2), "it's just a BH ringdown" dies by
   a factor of two in one line.  No new runs.
5. **Dissolution re-measured** — the quoted 1.07 → 0.59 curve splices in
   the disqualified `rw` arm; re-measure on the undamped level-5 headline
   arm with the offline theta+ scan.  Agreed phrasing: *the merger produces
   a short-lived black hole that dissolves by swallowing its own exotic
   matter* — classical negative-energy accretion, not Hawking radiation.
   A true MOTS finder (BHaHAHA) stays on the infrastructure list, not
   load-bearing.
6. **Scalar-charge prediction** — read q per throat from the l = 1
   `--scalar-modes` stream (per-throat spheres; the check-F angular mean
   cancels on the flipped binary), predict F ∝ q_A·q_B beside gravity; the
   6/4 pull/push ratio and the 5× at a = 2 should both follow.  The
   cleanest analytic check, for the price of a side figure (#8).
7. **Reproducibility bar** — no deterministic-reductions build flag exists
   in this tree (the Ψ₄ integral is already serial-deterministic; the
   non-deterministic sums live in diagnostics kernels).  The bar is the
   measured ±0.35 twin floor; a per-waveform number costs a twin-from-t = 0
   (decision §8).
8. **BBH known-answer calibration — RUN DONE (2026-09-03), QNM leg
   passed; E_rad closure still owed.**  The t150 ringdown fits period
   28.8–29.7, tau 25–27 (damped-sinusoid fit on the tail; late-window
   28.9 / 22.9), i.e. ≈ 15.2–15.6 M / ≈ 12.1–14.2 M for M_f ≈ 1.9.
   That is the Kerr (2,2,0) of a modestly spinning remnant — the
   Schwarzschild reference (16.8 M / 11.2 M) is approached from exactly
   the spin-shifted side it should be, and the two spheres (R = 14, 30)
   agree within 3–7 %.  Instruments cross-checked: Python consumer
   (plotfiles, fixed center) vs in-code stream match to 0.31 % / 0.35 %
   of peak — the extraction chain is calibrated end to end.  Figures in
   the pack: `bbh_t150_ringdown` (QNM fit overlay), `bbh_vs_wormhole_psi4`
   (now sourced from t150).  Still owed for the paper: E_rad vs
   ADM-minus-horizon-mass closure, and a paired tau error bar (the tail
   sub-windows drift 38 → 30 → 23, so quote the late window with the
   drift as the systematic).  Standing caveats unchanged: R = 14 ≈ 7 M is
   near-zone for the BBH; the "2.3× brighter" claim must become an
   *energy* ratio; a phantom halo radiates negative energy, so the
   wormhole remnant's ADM may legitimately exceed 2.

   **Boundary & extraction facts for the methods section (audited
   2026-09-03 on the t150 run):**
   - Extraction spheres r = 14, 20, 26, 30 in both campaigns; box faces
     at 32 from center.  In the *wormhole* runs the sponge ramp starts at
     r = 24, so r = 26/30 sit inside it — r = 14/20 are the quoted
     instruments there; in the BBH all four are clean.
   - The BBH has **no sponge by construction, not omission**: the sponge
     is extra dissipation inside the wormhole *matter* dispatch
     (`SpongeZone.hpp`, ramp r = 24 → 32, strength 4), built because the
     phantom scalar reflects badly off radiative boundaries.  Vacuum GW
     + Sommerfeld is the standard treatment and holds here.
   - Reflection audit, four independent checks: (1) the initial-junk echo
     transits the spheres by t ≈ 60, the signal reaches R = 30 only after
     t ≈ 95 — wrong time to contaminate; (2) pre-signal ambient floor at
     R = 30 is 12 % of peak but entirely before the chirp; in-band, the
     R20→R30 envelope coherence bounds contamination at ~3.5 % of peak;
     (3) independent ringdown fits at r = 14 and r = 30 agree to 3–7 %;
     (4) full-domain scan of the t = 150 plotfile: chi scatter *falls*
     outward (0.33 % → 0.26 %), max |K| in the outer shells 4e-4, no
     standing ripples after 150 units.

**Scalar-mode module** (in hand): consumer-side
`extraction/scalar_modes.py`, own stream, default off, enabled per launch
via `--scalar-modes`.  Validated three ways: orthonormality/round-trip
selftest; p045 dipole physics (|l1 m±1| = 0.76 dominating by 4 orders,
exact ± symmetry); 7 % match vs the independent slice-cache ring harmonic.

---

## 8. Open decisions before production (author's call)

1. **L = 128 vs L = 96** — the smoke test (#5) supplies the memory number;
   say now if 2.5–3 days per arm is too slow regardless.  (Review: take 128.)
2. **Tail +150** for the headline arm — τ ≈ 150 needs ~1 e-fold ≈ 150 units
   past merger; baseline +100 gives 0.6 e-folds.  ~+12 h at level-5 speed.
   (Review: yes.)
3. **Head-on freeze arm** (§7.1).  (Review: yes, with the BBH control.)
4. **Repulsion a-points** for the power-law panel (#8).  (Review: yes.)
5. **N = 192 wave-zone twin** (§7.3).
6. **Twin-from-t = 0** of the headline arm (§7.7) — only if a per-waveform
   reproducibility bar is wanted beyond the quoted ±0.35 floor.
7. **The horizon sentence** — is it in the paper at all?  Answered by the
   #16 floor ladder, not by the author.  Until it passes, "a short-lived
   black hole that dissolves" is written as contingent and the Letter
   framing does not lean on it.
8. **Initial-separation robustness arm** — one plunge from d = 16–18 at
   rescaled p (superposition defect 0.63× per the d^-1.6 law; ~1 day at
   level 3 + restart).  If the collapse sequence, wall and waveform shape
   reproduce, the superposition defect is exonerated by measurement — the
   affordable substitute for a constraint-solved IVP (§1 Helfer entry).
9. **Wave-zone third point** — the level-1 box to R = 44 in the headline
   arm vs the N = 192 coarse twin (§7.3): pick one.

Answered by events: scan values — run; headline intent — plunge-led,
p = 0.12 decided; BBH control — done; the damping-off control is no longer
deferred — it is #14 in the credibility batch.  Nothing above launches
until answered; every launch is one by-hand approval.

---

## 9. Validation pass 2026-09-03 (C++ audit, build, slices)

Method: read-through of the example's C++; a clean scratch rebuild; direct
z = 0 slice reads of nine runs at 2–6 epochs, cross-checked against the
`.dat` streams (independent instruments).

**The lapse never collapses at the throats.**  Every binary run, every
epoch: the χ pits keep lapse 0.05–0.24 and |φ| 0.79–0.92.  The
3e-2 → 1e-3 → 1e-10 collapse sits at the **inter-throat midpoint** (φ ≡ 0
by symmetry, K > 0, shift ≈ 0); the isolated throat never shows it.  The
midpoint value is identical at L3/L4/L5 (1.08e-2 at t = 28, helfer) —
converged: a property of the equations, gauge and data, not the grid.

| run | t | lapse at pits | lapse at midpoint | \|φ\| at pits | K |
|---|---|---|---|---|---|
| p020 L3 | 47.5 | 0.125 | 3.0e-3 | 0.87 | +0.20, no K < 0 core |
| plain p012 L3 | 43.5 | 0.134 | 1.9e-3 | 0.86 | — |
| helfer L3 | 60.0 | 0.073 | 1e-10 (floor) | 0.89 | +1.0 |
| helfer L4 | 48.0 | 0.177 | 3.1e-5 | 0.91 | +1.59 |
| helfer L5 | 28.0 | 0.209 | 1.08e-2 | 0.92 | +0.18 |
| p035 L3 | 73.5 | 0.046 | 1e-3 | — | +1.6 |
| p012 r03000 | 51.0 | 0.15–0.24 (rising) | shell at r ≈ 0.5–0.85 | 0.79–0.83 | −1.5 at the core |

Consequences:
- **"Zombie" explained**: at α = 1e-10 every α-proportional RHS term
  vanishes — the floored midpoint blob is static and NaN-free.  The
  h11-NaN deaths (the wall) happen with the midpoint near 3e-3, never
  floored: reaching the floor is not the trigger.
- **p012 endgame**: pits coincide within 0.2–0.6 by t = 48–51.5, core
  lapse *rises* (0.14 → 0.24) with K < 0, and the collapsed-lapse region
  becomes a shell at r ≈ 0.5–0.85.  The reported trapped surface at
  r = 1.0 (t = 51.06) sits on that shell — consistent with BH formation in
  1+log slicing, but #3 must run before the article says "common horizon"
  unhedged.  Large-radius trapped verdicts in helfer/p035/p025 coincide
  with the K ≈ 1 rim of the blob and are not credible.
- **Finest-level-only diagnostics are blind to the midpoint** until
  sep < 2.5 (`finest_lev` reductions in `BinaryWormholeLevel.cpp`);
  half-space throat positions stay valid but cell-quantised.  The tracker
  degenerates below sep 2 (pass 2 averages both pits); fix: restrict
  pass 2 to the pass-1 argmin neighbourhood.
- **CoreMatterDamping engages on the midpoint blob** (~t = 30) with no
  trapped surface — the template's rationale is false; its measured effect
  on death time is zero (§5), production runs clean.
- **Build**: clean scratch rebuild, 114 units, 0 errors; no sign or
  coupling error found (phantom sign only in T_μν, standard KG/1+log/
  Gamma-driver, floors at every RK stage).  Hygiene: `Make.package` omits
  two headers; `parameters_and_version.txt` records "(unknown)";
  `collapse_diagnostics` writes floors into state before reducing.

---

## 10. Housekeeping (2026-09-03)

- Results pack: **23 runs** (~67 MB) including the BBH control;
  `summary.md`/`.csv` regenerated; `results/merger/README.md` opens with
  the claim-by-claim map (paper subsection → backing runs → numbers).

## 10b. Audit after the credibility batch (2026-09-04)

- **All cards idle; every queued run finished.**  Walls this batch: nodamp
  51.53, lc1 43.64, p015_rr 53.35 (all h11/K NaN on the finest level);
  BBH control reached t = 150 clean.  Verdicts folded into #1/#2/#14/#15.
- **Scratch pruned to intent** (~75 GB): per run, only the held seeds
  (nodamp + p015_rr Chk05000 with `hold_seed_t50` hardlink copies), the
  held death plotfiles (p015 52.0–53.0, p015_rr 52.0–53.0, p020 51.0–52.0,
  nodamp 50.5–51.5, lc1 42.5–43.5), lc1's Chk04000 (t = 40, only gauge-arm
  checkpoint), and the BBH final Chk01200.  Superseded t = 40 checkpoints
  and the consumed BBH plotfiles deleted.
- **Logs packed**: all nine top-level `detached_gpu*.log` gzipped into
  their run directories, `run.log` gzipped in every finished run, sweeper
  log archived — `runs/wormhole_merger` top level holds only tooling,
  manifests and run dirs (~11 GB).
- **Every run directory kept** — each is packed or cited; the folder audit
  and keep-rationale are in `runs/wormhole_merger/MANIFEST_CLEANUP_2026-09-04.md`.
  `pack_results.sh` now sweeps `bbh_control_*` too.
- Figures in `results/merger/figures/`: `psi4_analysis_bbh_control{,_m2}`,
  `bbh_vs_wormhole_psi4`, the p045 fly-by set.  The comparison plotter is
  a package: `python -m grteclyn_wrapper.visualisation.merger`.
- `prune_checkpoints.sh` MAIN_RE now insures `bbh_control_*` — the t100
  final checkpoint was swept after the clean finish, which is why the t150
  rerun starts from scratch.
- Scratch cleanup: dead p020_lvl5 (26 G), p025_lvl5 (26 G) and the t100
  BBH (3.5 G) removed; scratch holds the two live runs, `_cache`, and
  p020_nofill's 3 held plotfiles (#4).  Run dirs keep params/logs/data
  streams only — the packed campaign is thinned from them; never delete.
- Earlier clean-up ledger: `runs/wormhole_merger/MANIFEST_CLEANUP_2026-09-03.md`.
