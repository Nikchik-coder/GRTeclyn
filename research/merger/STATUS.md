# Status — 2026-09-25 17:55 UTC

Current state only; the evidence and history are in [`GPU_PLAN.md`](GPU_PLAN.md)
(headings quoted in brackets), the map in [`../../MAP.md`](../../MAP.md).
**Update this page whenever a verdict or the queue changes.**

## Live

**`single_eps_m1e2_L512_ml5_oct_t400`** (F4, the inflation arm on the OCTANT in 1+log: F1b's gauge on F3's grid, mirror planes
x = y = z = 0, rolling checkpoints keep-3, profile `inflation-octant`) — first node, card 1, launched 2026-09-25 16:27 UTC on the
user's word ("switch back now and run full t"). t = 105 at 17:54, 73.5 u/h: causal limit t = 340 ≈ 21:05 UTC (~3.2 h), end
t = 400 ≈ 21:55 UTC (~4 h). No NaN, max|K| flat at 0.03, but L2_Ham doubles every ~15 u (6.4e-3 at t = 105): 0.1 by t ≈ 165
on that rate, so the record is quotable to t ≈ 150, not 400 ["2026-09-25 (17:55 UTC)"]. Agrees with Shinkai–Hayward only at
the onset (t ≤ 38, within 2–8 %); the neck runs 15–33 % slow once 1+log freezes its lapse.

**F5, harmonic slicing with stronger damping** (the user: "model it proper and without nans"):
`single_eps_m1e2_L512_ml5_harm_oct_t400_sg03` and `_sg10` (F3's template, Kreiss–Oliger σ 0.3 / 1.0 instead of 0.1) — card 0,
launched 17:44 UTC, preflight PASS, frame 0 checked. 23.6 u/h each (sharing the card): verdict at t = 46.55, F3's death,
≈ 19:40 UTC (~1.8 h). **F6 queued:** `params_single_eps_m1e2_L512_ml5_harm_oct_zs_t400.txt`, harmonic with zero shift (the
Gamma-driver drags the neck through the box faces), launched when card 0 frees.

F3 and F2 (harmonic, NaN at t = 46.55 on the level-5 box edge) wiped whole at 16:33 on the user's word; F1b wiped (14:15).

Card 0 F5 (two runs), card 1 F4. First node: the long
single-throat arms closed out under `01_single_throat/seed/` ["2026-09-24 (16:15)"]; its
scratch is empty; the paper session's `plt_take2/` plotfile copies (77 GB, G16's input) sit in
that session's scratchpad there.

Second node (one H100): free; the η = 4 level-5 probes are closed out, hunted and filed
["2026-09-25 (morning)"]. Its scratch is empty (205 GB pruned, MANIFEST_CLEANUP_2026-09-25).

Run tree: every plotfile deleted on the user's word; 192 → 52 GB. Two checkpoints remain for
the user's call: Chk05700 (26 GB, G4's input) and Chk03600 (20 GB, the t = 36 seed of G8/G9).

## Queued — nothing launches without the user's word

- **Paper edit (no GPU):** carry the 09-25 η = 4 horizon results into §VII.C (ledger rows, manual, sourced from the plan table).
- **Paper edit (no GPU), PENDING — every areal radius is a lower bound once the grid has moved** ["2026-09-25 (13:30) — F1b at t = 97"]: the campaign's R = r/√χ ignores the conformal metric (h₂₂ = 1.45 at the F1b neck at t = 90: 10.08 for a true 12.17); the t500's "×2.62 by t = 144" and the L128 figure are lower bounds and cannot be recomputed (no plotfiles). The consumer extractor is fixed from 2026-09-25 13:00.
- **Inflation campaign, PROPOSED (the user's call)** [same entry]: corrected R + horizon tracker in the consumer; a slicing that does not freeze at the throat (harmonic / shock-avoiding, C1); refinement following the horizons instead of fixed cubes; the compactified other universe resolved or excised.
- **Paper edit (no GPU), PENDING INSERT — the spherical literature's inflation ending** ["2026-09-25 (06:30) — the t500 turn is the wall"]: Shinkai–Hayward 2002 fit the expanding throat as r/a = 1 + b₄ exp(H(τ − b₅)) with H ≈ 1.1/a in PROPER time, the two trapping horizons become cosmological horizons, "the wormhole has exploded to an inflationary universe", no reversal in their range; GGS II (arXiv 0806.1370) find the areal radius "grows exponentially as a function of proper time" at the linear rate, "at least during the run time of our simulations", no horizon, the scalar amplitude still growing, and place the boundary so the extraction region is causally disconnected. §IV.D's "unbounded coasting, as in the spherical literature" (research.tex ≈ l. 267) misstates this: the literature's ending is exponential inflation in proper time. Our "coasts" is a coordinate-time rate under a collapsing lapse; no stream of ours holds α at the neck, so the proper-time rate is not yet measurable — the fate run must log it.
- **The runs the paper now asks for: G1–G16** ["2026-09-24 (afternoon) — the user's read of the whole paper"], ~300 GPU-h in all; the cheap discriminators first: G14/G15 (what makes the numerical regrowth, ~12 GPU-h each), G13 (the ε₂ decades, ~22), G1 (η = 4 chain on L = 128, ~12), G4 (curvature invariants at the wall, ~1 + code).
- Audit runs A1–A4 below; B1–B4 and C1–C2 are now G8–G11 and G6–G7. They run on the campaign pin, `main3d_guard_7166787a_2026-09-24.ex` since 2026-09-24 06:10 (stamped; reads the seed and the core profile). A restart of an old-pin run keeps the old pin unless `--binary` says otherwise.
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

- **Single throat**: unstable fixed point, one exponential mode; the e-fold is within 2.5 % (level 4) and 15 % (level 3) of the PARAMETER-MATCHED González–Guzmán–Sarbach linear rate (our throat is their γ₁ = 0.5 member: T = 0.758; τ_lin = 5.13 M); truncation noise picks the branch. The collapse horizon SHRINKS 40 % as it swallows the phantom; the 9–11 % REGROWTH in the scans is NUMERICAL (spherical first law forbids it; it tracks a constraint-violation double layer reaching the MOTS; same in purely spherical data; the pure quadrupole never regrows; the head-on horizon never regrows either). The late (t ≳ 75) constraint rise of every single-throat arm is a refinement-boundary grid mode whose onset the L = 128 box does not delay — NOT the t500 wall reflection ["2026-09-25 (09:30)"]. Inflation end state open: the t500 long arm (stopped at t = 195.14) did not close it — its turn at t = 161 is the cube wall's reflection of the 1+log gauge wave reaching the neck (six lobes on the axes from t ≈ 150; the KO-only sponge is transparent to it; the level-1 crossing is ruled out by the diagonal necks) ["2026-09-25 (06:30) — the t500 turn is the wall"]; its radii are r/√χ lower bounds ["2026-09-25 (13:30)"]. F2 (harmonic slicing, causal box, h₂₂-corrected R, horizons from t = 0) is running to settle it; F1b (1+log) was wiped as corrupted ["2026-09-25 (14:00 UTC)"]. (§IV)
- **Seeded throat**: a kick picks the fate opposite to its sign; the seed is not constraint-solved (H defect ∝ ε, 0.93×16π|ρ| on the shell at 1 %); ε = ±0.1 both collapse (+0.1 makes the throat a maximum, trapped at t = 1; −0.1 re-expands, then collapses) and die at the origin, not "from a Hamiltonian violation". (§II.D, §IV.C)
- **Two throats at rest**: like signs repel, opposite attract; force ∝ (d + δ)⁻², δ ≈ 3–4. (§V)
- **Head-on**: η = 4 MOTS located (level 3: R 5.41 at t = 30.0, lead ≥ 4.15; level 5 walks through its wall, R 5.29 → 5.17 over t = 34.2–40) [09-25, not yet in the paper]; common MOTS from t = 22, born with both throats' area (R = 1.01 √2 R⋆), around both throats behind a trapped neck; it never bounces (first law) and shrinks toward the pair's Bondi mass, 2M_B ≈ 4.1 (at t = 97: 1.07 R⋆, 4 % above 2M_ADM); the late decline is not accretion. The level-3 death is the grid's; level 5 runs clean to t = 100. (§VI)
- **Spiral**: every "spiral" is a plunge; a shape-free finder finds a common MOTS 5.4 units before the NaN, with BOTH wormholes inside (pits distinct to the χ floor) behind a common neck (R = 3.87 at t = 60); the wall is censored — under η = 4 too, at levels 5 (MOTS from ≤ 55.2, 0.04 before the 60.04 NaN) and 3 (at 61.5, 0.42 before 61.92), with M_MS within 0.3 % of the standard gauge's (η moves only the coordinate size); harmonic class: a θ_out = 0 surface 0.03 before its NaN, not trapped — open [plan/registry 09-25, not yet in the paper]; not "more momentum → stronger curvature" (max|K| says no); what falls with p is the grid's leverage. (§VII)
- **Fly-by / capture**: p = 0.45 scatters with no trapped surface; every p ≤ 0.25 merges, every p ≥ 0.35 does not — bound passes, not escapes (both start below the circular momentum; a central pull cannot capture without contact); the fly-by's recession after t = 43 is between the pits of two inflating mouths; the level-3 p = 0.45 closest approach (3.95) is a pit hop, level 5 passes at 4.8 ["2026-09-25 (09:30)"]. (§VII.A, new Fig. orbits)
- **Waves**: every channel radiates; the fly-by is loudest; the collapsing throat's wave is linear in ε₂ and the radial kick moves only its phase; it rings at the Schwarzschild period of its late mass (fit drawn); the scalar channel is comparable and negative-energy; the horizon switches it off; each vacuum control is drawn under its drainhole twin at R = 20 (Fig. 11(c,d)): the BBH spiral merges 2.9× lower and 43 units after the drainhole burst; the p = 0.45 BBH fly-by radiates one cycle at periapsis, 4.5× below the fly-by's peak, and nothing at the pass. (§VIII)
- **LIGO**: no candidate in 2.26 h of O3b, and none expected (no throat survives; conversions are at z ≳ 20). (§IX)
- **Astrophysics** (abstract + §X.B re-framed 2026-09-25: LISA is the headline, LIGO the null channel; the fly-by and spiral are the loudest LISA sources, optimal SNR 175–500 at 10⁵–10⁶ M⊙; conservative SNR ≥ 8 for every encounter 3×10⁴–4×10⁶, the fly-by to 2×10⁷; the fly-by marks no seed (its mouths inflate); lone collapse ≤ 6 conservative, ≈10 optimal — was "≈7"; Fig. 17(b) is now one burst's strain against the LISA noise, (c)'s Ω_GW the conversions only (head-on to spiral); the LISA SNRs are ledger rows recomputed by gw_search.lisa): no ghost-scalar wormhole inspiral (rotation is the open exception); collapse is a heavy-seed channel whose conversion bursts LISA would detect ONE BY ONE (SNR 61–500 at 10⁵–10⁶ M⊙, z = 20; > 8 from 3×10⁴ to 4×10⁶ M⊙), limited by abundance; the negative-energy deposit cannot be Λ (w, sign, size: Ω_WH ≈ 60–800 needed). (§X)

**Plan vs paper**: the paper is the current word — 963 ledger rows, 0 problems, 805 recomputed (`claims.py check`, re-run 2026-09-25 17:00 UTC after Fig. 17's new panel (b)) — EXCEPT the 09-25 η = 4 horizon results and the spherical-literature inflation ending (Shinkai–Hayward / GGS II: exponential in proper time), which are in the plan and registry only. The plan's older entries still carry superseded readings (the regrowth as physics, "no horizon ever forms" for the spiral, "+17 %" regrowth, the ×7.8 fly-by growth as a measurement, the "21 % short" ringdown).

## Traps (each has cost a run)

- AMReX ignores keys nothing reads: old binaries run new params without the new
  physics. The launch preflight now refuses this (keys read only inside a switched-off
  feature are allowed by name in `preflight_allow.txt`).
- `amr.checkpoint_files_output = 0` silently disables checkpoints whatever the
  interval (19 templates carry that contradiction): the preflight now refuses it.
- Verify by effect: frame 0 against a reference, the first checkpoint on scratch.
- Norms after a restart and across boxes: compare onset times, never ratios.
- Star scans miss deformed MOTSs and emit scan-edge rows (R ≈ 47.6, 60.6) that are not horizons.
- A horizon hunt whose seeds "leave the box" found a trapped region bigger than the box, not nothing: every η = 4 null to 09-24 (half 3–5) was that. Size the box from a wide radial θ_out profile first (the finder now says LEFT THE BOX).
