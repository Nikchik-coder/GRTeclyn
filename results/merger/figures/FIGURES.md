# The paper's figures, and how each is drawn

**This folder holds the article's figures and nothing else** (2026-09-26, the
user: "wipe out figures that are not present in the paper ... check the packing
scripts so they do not regenerate them"). Every file here is included by
`research/merger/article/research.tex`; nothing else is kept, and
`research/merger/pack_results.sh` draws no figure (it runs `plot_branches
--no-figure` for `campaign/01_single_throat/BRANCHES.md` only). When a figure
leaves the paper, delete its PNG/PDF here and its row below; its script stays in
`grteclyn-wrapper/src/grteclyn_wrapper/visualisation/wormhole_merger/`.
**Add the row when you add a figure to the paper.**

Run each command from the repository root with the wrapper's venv; every one
takes no arguments (`--pack-root` defaults to `results/merger`) and writes the
PNG + PDF pair named in the table. Numbers are the article's as of 2026-09-26.

```
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.<module>
```

| Fig. | label | file | module |
|---|---|---|---|
| 1 | `fig:single_throat` | `01_single_throat/single_throat_instability` | `plot_single_throat_row` |
| 2 | `fig:single_collapse` | `01_single_throat/single_throat_collapse` | `plot_single_collapse` |
| 3 | `fig:single_inflation` | `01_single_throat/single_throat_inflation` | `plot_single_inflation` |
| 4 | `fig:pair` | `03_two_throats/pair_interaction` | `plot_pair_row` |
| 5 | `fig:headon_collapse` | `04_binary_headon/headon_collapse_diagnostics` | `plot_headon_collapse` |
| 6 | `fig:orbits` | `05_binary_spiral/momentum_scan_orbits` | `plot_momentum_orbits` |
| 7 | `fig:spiral_collapse` | `05_binary_spiral/p012_collapse_diagnostics` | `plot_spiral_collapse` |
| 8 | `fig:gw_gallery` | `08_waves/psi4_gallery` | `plot_psi4_gallery` |
| 9 | `fig:gw_ligo` | `08_waves/psi4_ligo` | `plot_psi4_ligo` |
| 10 | `fig:scalar_channel` | `08_waves/scalar_channel` | `plot_scalar_channel` |
| 11 | `fig:heavy_seeds` | `08_waves/heavy_seeds` | `plot_heavy_seeds` |
| 12 (App. A) | `fig:constraints` | `00_code_health/constraint_evolution` | `plot_constraint_evolution` |
| 13 (App. A) | `fig:single_regrowth` | `01_single_throat/single_horizon_regrowth` | `plot_horizon_regrowth` |
| 14 (App. A) | `fig:spiral_ladder` | `05_binary_spiral/spiral_refinement_ladder` | `plot_spiral_ladder` |
| 15 (App. A) | `fig:fill_insensitivity` | `05_binary_spiral/fill_insensitivity` | `plot_fill_insensitivity` |
| 16 (App. B) | `fig:mouth_growth` | `05_binary_spiral/mouth_growth` | `plot_mouth_growth` |
| 17 (App. B) | `fig:seed_linearity` | `01_single_throat/seed_linearity` | `plot_seed_linearity` |
| 18 (App. B) | `fig:scalar_censorship` | `08_waves/scalar_censorship` | `plot_scalar_censorship` |

## Main text shows physics; code health is Appendix A (2026-09-26)

The user, on a referee-style read ("move the figures that focus strictly on
numerical validation, code health and error systematics to the appendices"):

* **The constraint panels left the physics figures** and became one appendix
  figure, `00_code_health/constraint_evolution` (`fig:constraints`, six
  panels, a key on top of each naming the run and its refinement level):
  (a)/(b) the lone throat's H and M, every seed amplitude at the HIGHEST level
  it was run at (level 4 for no kick and +-0.01 -- +0.01 was stopped by hand at
  t = 13.5 -- level 3 for +-0.001 and +-0.1, never run at level 4); (c) the
  pure quadrupole (was Fig. 2(g)); (d) F4, level 5, to t = 218 (was Fig. 3(i));
  (e) the head-on's H on its three arms (was Fig. 5(e)); (f) the spiral's
  level-5 and level-3 norms (was Fig. 7(d), there normalised against max|K|).
  Fig. 1 is one row now (its (d)/(e) were the level-3 seed scan's norms);
  Fig. 2's bottom row is (e)/(f) at half width each; Fig. 3's last row is
  (f)-(h); Fig. 5's (f) became (e) and spans the right half; Fig. 7's (e)
  became (d), and max|K| joined the core extrema in (c).
* **Six figures moved to the appendices**: Appendix A (code health) takes
  `single_horizon_regrowth`, `spiral_refinement_ladder` and
  `fill_insensitivity` after `constraint_evolution`; Appendix B
  (supplementary measurements) takes `mouth_growth`, `seed_linearity` and
  `scalar_censorship`.
* **`05_binary_spiral/p012_paper/` is gone**: its three paper figures sit in
  `05_binary_spiral/` (the run group `campaign/05_binary_spiral/p012_paper/`
  is unchanged).
* **17 figures not in the paper were deleted** (PNG + PDF, 34 files): every
  `psi4_analysis_*` six-panel wave page (single throat, head-on, spiral
  series, fly-by, BBH control), `single_throat_branches`,
  `single_throat_seed_branches`, `single_throat_inflation_L128`,
  `single_throat_inflation_L512`, `sign_rule`, `placement_curve`, the two
  head-on `*_psi4_20_R10_14_18_t100` pages and `bbh_t150_ringdown`; the
  `06_binary_flyby/` and `07_bbh_control/` folders went with them. Their
  commands and redraw notes (the `psi4_analysis` table, "How the commands were
  recovered", "What changed in the redraw") are in this file's git history
  before 2026-09-26; the scripts remain and still draw them on demand.

## The validation figures (2026-09-19)

Two figures certify the 2026-09-18/19 validation arms; both are drawn with
no arguments:

```
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_seed_linearity
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_fill_insensitivity
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_mouth_growth
```

`01_single_throat/seed_linearity` — queue 2e gate 3: the (2,0) wave divided
by its seed collapses across eps2 = 0.005/0.01/0.05 (linear to 1-16 %, the
worst point the 0.05 arm's R = 10), the pure-quadrupole arm sits on the
kicked one to 2-3 % (the radial kick contributes nothing to the wave), and
the spherical control rules the floor.

`01_single_throat/single_throat_collapse` — the single-throat analogue of
the spiral collapse page, drawn from the pure-quadrupole arm by
`plot_single_collapse` (no arguments): areal radius + MOTS strip over a 2×3
grid of min α / min χ / max |K| / the radial shells (t = 33–55) / the
constraints (since 2026-09-26 the constraints are `constraint_evolution` (c) and
the shells are the bottom row's two panels). MOTS from t = 33, R 3.80 → 2.41, M_MS 1.90 → 1.24.
Names hang on what they name (2026-09-23, the user: "to what exactly is it
connected?"): the MOTS clock and the 10 % departure clock are flags at the
top of their own rules (left / right of the rule, the inflation page's
grammar); the twin is named beside its RISE, anchored on the data; (g)'s H
and M sit just above their own curves on the quiet stretch, in data
coordinates, not floating in axes fractions.

`01_single_throat/single_horizon_regrowth` — the remnant horizon that
shrinks and grows back, by `plot_horizon_regrowth` (no arguments): MOTS areal
radius and Misner–Sharp mass for the three eps = +0.01 collapse arms (level 3;
level 4 + eps2 = 0.005; level 4 + eps2 = 0.05 -- none carries matter damping,
core_matter_damping = 0), floors marked. REDRAWN 2026-09-23 (article audit)
from the throat-centred centre-A scan: the coarse common centre C used before
reads M_MS/(R/2) up to 1.15 at the floor, i.e. not a MOTS. Floors 2.337/2.334/2.321
at t = 47/47/43, regrowth +9.7/+8.8/+10.6 % in R and +10.2/+10.5/+12.0 % in
M_MS by t = 100 (article Sec. IV D, fig:single_regrowth).

`01_single_throat/single_throat_inflation` — its mirror, by
`plot_single_inflation` (no arguments). SINCE 2026-09-26 IT IS F4 ALONE
(`single_eps_m1e2_L512_ml5_oct_t400`, level 5, L = 512, quoted to t = 218; see
its module's docstring) in eight panels, the norms moved to `constraint_evolution`
(d). The note below is the retired level-4 page: the ε = −0.01 level-4 arm to t = 100
on the same 1 + 2×3 grammar, with the unkicked level-4 twin drawn beside it
in (a) and the anti-trapped rows (θ₊ > 0 and θ₋ > 0, the MOTS's mirror)
marked in gold over t = 1–35. R 3.81 → 11.39 (×3.0) against the twin's ×2.2,
parting by 10 % at t = 25. Panels (e)/(f) lead with χ, not |K|: the signature
of this branch is the compactified inner sheet's χ-trough marching outward
(r = 0.016 → 2.9), and |K| never leaves 0.06. That march is also why the
θ₊ = 0 rows at R ≈ 60.7 after t = 85 are not a horizon and are not drawn.

`05_binary_spiral/fill_insensitivity` — queue 5 (f): the freeze
twin (fill 1.25/1.75) against the freeze arm (1.40/1.90), same t = 57 seed,
same binary. Max |dPsi4|/peak 0.385/0.370/0.024/0.013 % at R = 20/28/36/44
over t = 57-100; panel (b)'s onsets sit on the causal clock t = 57 + (R - 1.9)
= 75/83/91/99. The fill is not in the physics; it certifies inertness, not a
remnant ringdown.

`05_binary_spiral/mouth_growth` — the queue-8 gap closed: the
mouths of the arm that MERGES, measured for the first time, against the
fly-by's. Three stacked panels on one clock — per-mouth areal radius, the
separation, and the growth excess on a log axis with both exponential fits.
Merger +12.2 % by t = 28 with e-fold tau = 3.70; fly-by tau = 4.39 over the
identical fitted window t = 8-25. Read the dash language: SOLID is a
per-mouth measurement, DOTTED is the same scan after its sphere has
swallowed the other mouth (t > 28 merger, t > 36 fly-by -- the apparent peak
5.549 at t = 34 is that overlap, not a throat), and the long dash is the
common-centre scan, a different instrument. No MOTS and no trapped surface
in either arm.

## The paper's `08_waves` figures (2026-09-16)

The article's five wave figures live in `08_waves/`, cross-cutting because they
belong to no single group. All are drawn with no arguments:

```
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_psi4_gallery
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_psi4_ligo
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_scalar_channel
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_scalar_censorship
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_heavy_seeds
```

`08_waves/heavy_seeds` (2026-09-21; labels and one error bar fixed 2026-09-23 --
UHZ1's name had printed UNDER the Eddington label's opaque patch and never
showed, that patch also cut the heavy ceiling, the light-seed name floated
700 Myr from its line, (b)'s note clipped the 1e4 box, the tags sat inside
the frames on the Eddington label; J1342+0928's lower bound 4.5e8 -> 5.9e8,
Banados et al. 2018's 7.8 (+3.3, -1.9) e8; GN-z11 and J1342 now cited in the
caption, maiolino2024 / banados2018; panel (b) REPLACED 2026-09-25, see below) —
article Sec. X B, the heavy-seed channel and its LISA bursts. (a) the seed
race: the drainhole reachable region (seeds 10^4-10^6 M_sun at z ~ 20,
converted at full mass in minutes — Table II — then bounded by the 45-Myr
Eddington ceiling) against UHZ1, GN-z11, J1342+0928 and the little-red-dot
box, with the 10^2 M_sun light-seed ceiling missing UHZ1 by two decades.
(b) since 2026-09-25 ONE BURST AGAINST LISA (it was the conversion-background
boxes, a time average the text says never forms at these rates, and the
per-burst SNR of the abstract appeared in no figure): characteristic strain
h_c = 2 f |h~| of the fly-by at 10^4-10^8 M_sun and of the spiral and lone
collapse at 10^5, z_e = 20, conservative (inclination-averaged), against
sqrt(f S_n) of the Robson-Cornish-Liu noise with the 4-yr confusion; READS
THE PACK through gw_search.lisa (the search templates' strain), and the area
between track and noise in ln f is the quoted SNR^2 (tests/gw_search/
test_lisa.py). Tracks drawn over the band holding 90 % of int h_c^2 dln f
(whole tracks one decade apart fuse into one line); hatched below 0.1 mHz.
Labels placed by style.legend / note / callout and style.declutter, checked by
style.label_audit (which since 2026-09-25 also reports text on text and on the
key). (c) the population curve: Omega_GW of the CONVERSIONS (E/M head-on to
spiral, read from the pack; it ran to the fly-by's, which converts nothing)
and the scalar deposit (E_GW spiral to fly-by, every encounter, the case
most favourable to Lambda); ticks = the PLS at each mass's conversion
frequency. Astrophysical points carry their references in
the article's bibliography; cosmology flat LCDM H0 = 67.7, Om = 0.31.

`08_waves/scalar_channel` (2026-09-19) — the SECOND radiation channel, the one
Psi4 cannot see. Full-page row of three panels. (a) REDRAWN 2026-09-23
(article audit): the fly-by alone, energy through R = 30 to t = 80 in units
of E_GW(t = 80), with |E_phi|/E_GW printed at each cut -- 3.2 / 2.3 / 1.1 / 0.8
at t = 50 / 60 / 70 / 80: the ratio is cut-dependent (the gravitational burst
peaks at R = 30 near t = 65) and past t ~ 80 the mouths reach the sphere. The
spiral is no longer drawn: its level-3 scalar record ends at t = 50, before
its burst reaches R = 30, so its "-2.4" divided by a pre-burst E_GW.
The scalar curve is NEGATIVE because gravity couples to minus this field's
stress tensor, so the stream's canonical-signed `flux_kin` has to be negated
before it is energy. (b) the multipole decomposition of the scalar sector:
l = 1 sits 10^7 above l = 0 and l = 2 -- two opposite scalar charges radiate
at DIPOLE order, which a vacuum binary has no analogue for. (c) the
systematic: |F_phi| at both spheres, with rules where the inflating mouths'
areal radius passes each sphere's own radius, and the blue rule where the
quoted numbers are taken. Reads `scalar_modes.dat` and `psi4_mode_l2_all.dat`
from the same run so the two channels share their extraction spheres; no run
was launched for it, the `orbit-modes` consumer profile has been writing the
scalar stream since 2026-09-15. The head-on gap it used to declare is closed --
see `scalar_censorship` below; the single throat's is not.

`08_waves/scalar_censorship` (2026-09-21; restyled MONOCHROME 2026-09-23 on
the user's word -- the scenario colours read as a rainbow; identity now rides
grey level + line style with the top key naming every curve) -- the horizon
shuts the ghost dipole off, and nothing else does. Two panels, drawn as ENVELOPES: a running MAXIMUM
of |F_phi| over 25 units (one period of the dipole's own oscillation), then a
Gaussian in LOG amplitude. The raw flux changes sign every ~20 units and dives
to the log floor at each zero, which on a log axis hides the one thing the
figure is about. A running r.m.s. was tried and is NOT enough: shorter than a
period it still carries the oscillation, longer and it smears the decay.
(a) the head-on arm `merge_headon_flip_d8_v1_lvl5from0_scalar_t100` (level 5
from t = 0, scalar stream on -- the re-run that closed the gap) at R = 10/14/18.
Common MOTS at t = 21.5 (dotted grey rule); the remaining hair leaves as one l = 1,
m = 0 pulse cresting later at each sphere, then decays: log-linear fits over
t = 30-95 give tau = 19/23/29 (dashed), comparable to the tau = 19.4 +- 0.8 on
which the scan's M_MS levels off (Fig. headon_collapse (b); part of that
levelling is the star-scan shape systematic -- the area keeps shrinking).
CORRECTED 2026-09-23: the two lone-throat curves of (b) are the eps = +0.01
level-4 collapse and the UNKICKED level-4 throat -- neither scalar re-run
carried its quadrupole seed (GPU_PLAN, 2026-09-23 evening).
Post-horizon E_phi = -0.056/-0.071/-0.075. THE PRE-HORIZON RISE AT R = 10 IS
NOT RADIATION: it is the two open mouths' static hair superposing, canonically
INGOING and inside the near zone, which is why no full-record head-on integral
is quoted anywhere.
(b) the control, one outer sphere per fate: the fly-by (no horizon, no merger)
GROWS to the end of its record; the p = 0.12 spiral (merges, 0 MOTS on every
scan) is still CLIMBING at its t = 59.9 wall. Horizon or no horizon is the only
variable that separates them from the head-on.
PAST THE WALL THE SPIRAL IS THE FROZEN-CORE ARM (`..._freeze_r05700`, dashed at
half weight) AND MUST NOT BE READ AS PHYSICS. Its exterior is certified -- it
agrees with the free arm to 0.1 % on this very flux over their t = 58-59
overlap, and the two freeze twins to 0.01 % -- but a frozen source region cannot
be asked how its radiation decays. The claim stops at the wall.
The single-throat collapse is absent for the same reason the head-on used to be:
no single-throat arm ever carried the scalar stream, so it is a re-run and not a
re-read -- one was launched 2026-09-21.

LEGEND IDIOM, learned the hard way on this figure: `constrained_layout` does NOT
reserve space for a FIGURE legend -- both `bbox_to_anchor` and
`loc="outside upper center"` drew the key over the frames. Use fixed margins and
no layout engine: `fig.subplots_adjust(left=0.088, right=0.988, top=0.745,
bottom=0.145, wspace=0.17)` with `fig.legend(..., loc="upper center",
bbox_to_anchor=(0.5, 1.0), ncols=4, frameon=False)`. Every note lives in that
legend or in the caption; there is no in-frame prose at all.

The scenario table (stream, mode, innermost sphere, gate) is `ARMS` in
`plot_psi4_gallery.py` and the LIGO figure imports it, so the two figures
cannot disagree about what a scenario is. The gates: the collapsing throat's
stream is the queue-2e gated file clipped at t = 70 (QUEUE2E_GATES.md); the
fly-by row is now the L = 128 level-5 arm
(`campaign/06_binary_flyby/p045/merge_orbit_flip_d12_p045_L128_lvl5_t100`,
(2,2) single-mode file; finished t = 100 clean on 2026-09-18). It is gated at t = 76: no horizon ever
forms (horizon_scan n_mots = 0 throughout), both mouths expand (areal R
4.2 → 33 by t = 97, corr(log R, log L2_Ham) = 0.92 — the expansion drives the
constraint growth), and that expansion's disturbance lifts |rΨ4| at R = 20
off its post-burst trough at t = 76.1, ending 1.7× the burst peak, while
R = 36/44 decay monotonically to the record's end.

The quoted v/c are **not** the dashboards' peak-to-peak numbers: they are the
lag of the whole complex waveform between neighbouring spheres, correlated
over the common retarded window (`psi4_math.wavefront_speeds_xcorr`). Peak
timing fails twice here — the BBH control's merger envelope is a ~15-unit
plateau at both spheres (peaks alone read v = 0.57 where the waveform lag
reads 0.82), and the spiral's outer spheres have no peak inside the record at
all (peak matching returned v = −0.90; the windowed lag reads 1.00). Measured:
throat 0.91/0.95/0.98, head-on 0.96/0.90, spiral 0.95/1.00/1.00, fly-by
1.00/1.00/1.00, BBH twin 0.82. Both figures are re-drawn at the spiral and fly-by close-outs.

**Gallery redrawn 2026-09-24 (first-author review: "why do the right-column
hills grow in (c)-(e) when (a)-(b) touch the x axis?").** The paragraph above is
the old state. (1) The right column is now an ENVELOPE in every row: the (2,0)
modes are real, so |rΨ4| was the rectified wave; they get the analytic-signal
envelope (drawn to each record's last crest), the (2,2) rows keep |rΨ4|. The
rising hills are the bursts themselves. (2) The gallery draws with
`DRAW_GATES`/`drawn()` (per sphere, retarded where it matters), not with
`ARMS.t_max` (still the LIGO figure's and the ledger's): throat to where the
exact level-4 spherical control's floor passes 10 % of the burst peak
(t = 54/52/52 at R = 14/18/22; R = 10 to the ringdown fit's end t = 58); spiral
to the fill's light cone t = 57 + (R − 1.9) (past it: frozen-core transport and
grid noise at f ≈ 2/M reaching 9–15 % of peak by t = 95 at R = 20/28); fly-by
to t − R = 50 on every sphere (the coordinate t ≤ 70 cut R = 36 at its peak
and R = 44 before it). (3) Row (a) carries queue-2e gate 4's damped sinusoid
(t = 26–58, period 20.6). (4) 7.05 × 5.6 in. Speeds on the drawn records:
throat 0.95/0.97/0.95, spiral 1.00/1.00/1.00 (the 0.95 came from the spiral's
post-light-cone stretch alone), the rest unchanged. The numbers behind all of
this: `grteclyn-wrapper/scripts/analysis/merger_feedback/waves_gallery_audit.py`.
Same day: `seed_linearity` reads its floor from the level-4 control
(`single_eps_p1e2_q1e2_ml4_scalar_t100`, seed not applied; 6.75e-5 at R = 14
against the level-3 6.79e-5), spans the decade 1e-3–1e-1 in (b) and names the
arms at their ends in (a); `fill_insensitivity` (a) no longer multiplies the
r·Ψ4 stream by R again (it drew 20 r·Ψ4), and (b) ticks the causal clock per
sphere: R = 20 on it, R = 28/36/44 ahead of it by 1.0/2.9/4.7 units below
1.5e-5 of peak (a gauge-speed front).

### psi4_ligo rebuilt: four panels, and two bugs it had carried (2026-09-18)

`psi4_ligo` is now a two-column strip (`figure*`, 7.05 x 2.75): (a) the
records' envelopes on a common merger clock, (b) strain over the aLIGO floor,
(c) instantaneous frequency against the Newtonian point-mass chirp, (d) the
radiated-energy ranking. It briefly had the |rPsi4|^2 power spectrum as (a),
which is (b) times (2 pi f)^4 — one plot drawn twice; the time domain is what
the strip was missing.

**The calibration was not shared.** The caption says "total mass M = 30 Msun"
and the conversion mapped ONE CODE UNIT to 30 Msun for every arm. Four of the
five sources are binaries carrying M_ADM = 1 per body — 2 code units — and
only the lone throat is a single unit mass (each run's `evolution_params.txt`;
the BBH's bare 0.9615 gives per-hole ADM ~ 1.00). The binaries were therefore
drawn as 60 Msun systems at half their frequency and 2.8x their strain, beside
a 30 Msun throat. Every record is now reduced to units of its OWN total mass
first (`M_CODE`). The check that settles it: the BBH control's peak |rPsi4|
lands at f M = 0.065, the textbook merger value.

**The wavelet ridge hid the chirp.** The old panel (b) drew the Morlet ridge,
which needs the cone of influence trimmed off both ends — half of these short
records — and smears a sweep into its own measurement band. The BBH twin,
whose phase sweeps through a factor of 80, came out as a FLAT 227 Hz shelf.
The frequency is now the phase derivative on the analytic signal,
ENERGY-WEIGHTED over a cycle: the spiral's (2,2) envelope swings 2x within a
carrier period, so its bare derivative swings 3 Hz to 7.6 kHz, and weighting
by |A|^2 puts that variance at the nulls where it belongs. Also: |y| is not an
envelope for the real (2,0) records (it is the rectified wave), so an
amplitude gate on it kept one half-cycle lobe.

**Radiated energy, and the two traps in it.** `psi4_math._compute_radiated_energy`
squared Psi4 as it stood. Psi4 is h-double-dot, so it is integrated ONCE
before squaring; the old form is not an energy and read an order low (the
throat's burst was quoted at 2.3e-6 M and is 3.2e-5 M — the article carried
the wrong number). The integral is done in the frequency domain, where the
1/f^2 weight makes the one dangerous knob explicit; fixed-frequency
integration is NOT used, because it CLAMPS the sub-corner band instead of
removing it and let the fly-by's mouth expansion grow without bound as the
gate opened. Every arm has a flat plateau in that cut over 0.02-0.45 of its
peak. The second trap: the ARMS gate is a COORDINATE-time cap chosen at the
innermost sphere, and the same physics reaches R later, so comparing spheres
under it gave R = 44 sixteen masses of record against R = 20's twenty-eight
and read a factor of twenty between them. Gate in RETARDED time and the
fly-by's spread falls from 316 % to 40 %.

Measured E_rad/M (dominant multipole, +-m doubled, sphere spread in brackets):
fly-by 9.3e-2 [5.6-9.3e-2], spiral 2.2e-2 [1.7-2.2e-2], head-on 3.3e-3
[2.9-3.3e-3], BBH twin 2.6e-3 [2.4-2.6e-3], throat 3.2e-5 [2.6-3.2e-5]. The
two open gold bars in (d) are NOT runs of this campaign and NOT closed
forms: they are the published equal-mass non-spinning vacuum results from rest
at infinity, head-on 5.5e-4 and quasi-circular 1 - M_f/M = 4.84e-2. The twin
sits just above the head-on end because its momentum is 59 % of circular
(p = 0.12 against 0.204 at d = 12) — it is an eccentric plunge, not an
inspiral, which is why its 0.26 % is nowhere near the textbook 4.8 %.

### psi4_ligo panel (b): every quoted peak frequency was 1/T_record (2026-09-18)

Panel (b) ran from 20 Hz and quoted the maximum of each curve. Measured
against the records themselves, those five "peak frequencies" were the
inverse record lengths to two digits:

| arm | quoted peak | 1/T_record | ratio |
|---|---|---|---|
| collapsing throat | 95.3 Hz | 96.7 Hz | 0.99 |
| head-on | 135.3 | 136.7 | 0.99 |
| spiral | 135.3 | 135.3 | 1.00 |
| fly-by | **178.0** | **178.1** | 1.00 |
| vacuum BBH twin | 89.9 | 90.2 | 1.00 |

The cause is structural, not a typo. Psi_4 is h-double-dot, so the strain PSD
carries a 1/f^4 weight, and after it *every one of these bursts still rises
monotonically toward low frequency*. The plotted curve therefore peaks
wherever the high-pass guard stops it, and that guard is one cycle per record
(`_psd_psi4_to_strain`, 2026-09-16). The quoted AMPLITUDES were read at the
same place, so they were knee values too, and both numbers moved whenever a
record was lengthened or a gate was changed. The article carried
"the fly-by peaks at 6.0e-21 Hz^-1/2 (178 Hz)" on that basis.

Fixed: each curve now STARTS at its own corner, with the corner ticked on the
curve, and nothing is quoted as a peak. What is quoted is the strain at the
one frequency these records genuinely resolve -- the Psi_4 band peak, bins
3-5 rather than bin 1 -- and the logarithmic slope, so the panel reads as a
falling power law with a stated left edge:

fly-by 1.21e-21 at 193 Hz (slope -4.9), head-on 1.10e-21 at 406 Hz (-5.5),
spiral 9.25e-22 at 406 Hz (-5.7), BBH twin 3.00e-22 at 450 Hz (-5.9),
throat 1.53e-22 at 286 Hz (-3.4). The BBH twin's Psi_4 peak at f M = 0.0664
is the textbook equal-mass merger value, which is the check that the
reduction to each source's own total mass is right.

Also fixed in the same pass: `_smooth_psd(S, 21, 5)` was one hard-coded
Savitzky-Golay width for five records differing by two orders of magnitude in
length -- a light touch on the spiral's ~5000-bin spectrum and most of the
band on the throat's 36. It is now a fifth of the spectrum, odd, at least 5
(`_smooth_window`).

### The fly-by row is gated at t = 70, not 76 (2026-09-18)

t = 76.08 is where |rPsi4| at R = 20 TURNS BACK UP. That is the trough --
the point where the mouths' expansion has grown to EQUAL the decaying burst,
not where it arrives -- and by t = 100 the contaminant is 2.0x the burst
peak. The gate is now set ahead of it at t = 70, which still keeps 15.5 units
(7.8 M) past the R = 20 burst peak at t = 54.5. Consequences: E_rad/M falls
9.3e-2 -> 7.4e-2 (sphere spread 43 %, the widest in the campaign), the
fly-by's lead over the vacuum twin 36x -> 29x, and its band peak moves
f M = 0.0263 -> 0.0286. The |rPsi4| peak itself (4.1e-2) does not move: it is
at t = 54.5, far inside both gates.

The retired note on this row claimed "R = 36/44 decay monotonically to the
record's end". **They do not.** That reading normalised each sphere by its
maximum over t <= 60, which truncates the OUTER spheres' bursts before they
peak -- light travel puts the R = 44 burst at t ~ 78, not 60. In retarded
time all four spheres peak together at t - R ~ 34.5, as radiation must.

## The paper's spiral collapse page (2026-09-18)

`05_binary_spiral/p012_collapse_diagnostics` is the article's
spiral collapse figure (sec:spiral:inspiral), drawn with no arguments:

```
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_spiral_collapse
```

**REDRAWN 2026-09-24** (the user's read of the paper: "it shouldn't span the whole page"; "we extended the run after death with freeze, why is this not shown on (a)"): a `figure*[t]` strip, 7.05 x 4.3 in, five panels. (a) pit separation over the whole history t = 0-100, the frozen era from t = 57 shaded and labelled (no core quantity drawn inside the fill), gold rug on the slices carrying a common MOTS (55-57, 59, 98-100); (b) areal radius of the common MOTS (incl. the remnant R = 4.15 at t = 98-100) and of the common NECK (the smallest sphere about the pits' midpoint, enclosing BOTH pits), against R_star and sqrt(2) R_star; (c) core extrema; (d) constraint norms against max|K|; (e) the |K| spike and edge against the neck. SINCE 2026-09-26 four panels: (d) went to `constraint_evolution` (f) as plain norms, max|K| joined (c), and (e) is (d). Old (a)->(a), (g)->(b), (b)+(c)+(d)->(c), (e)->(d), (f)->(e); (h)-(j) dropped. The two chi pits stay distinct until chi floors at t = 58.43 (0.31 apart at t = 57): both wormholes are inside the MOTS (`scripts/analysis/merger_feedback/pit_throats.py`). The older notes below describe the ten-panel page.

Panel (g) REDRAWN 2026-09-23 (article audit): besides the star-scan throat
radii (no MOTS -- a blindness about the merged pit, not an absence) it now
carries the shape-free flow finder's common MOTS, R = 4.83/4.80/4.77 at
t = 55/56/57 on this chain (filled diamonds) and 4.72 at t = 59 on the
level-5-from-t = 0 arm (open), with its labels kept left of the chi-floor rule.

It REPLACED the generic dashboard render of the same name (2026-09-16, Computer
Modern, 9 boxed panels) with the seed-branches-grammar page: the inspiral strip
(SERIES `binary_throat_diagnostics`, restart-settle rows t = 36.0-36.4 masked),
the level-5 clocks and radial anatomy (the profiled arm's own streams), the
level-3 constraint overlay (median 3.5 % / 0.7 % of the level-5 H / M over the
shared t = 36-50 window; all 22 of leg 1's regrid spikes sit before t = 36),
and the two oriented horizon scans as the only horizon instrument — throat
r = 0.99 -> 0.73, areal R = 4.104 -> 3.872 (levels 3/5 within 0.2 %), **no MOTS
at any of t = 55-60**. The in-code theta_common columns are deliberately not
drawn (naive +r orientation; the withdrawn t = 30.77 "common horizon" was
exactly that artefact). Validated at draw time against the pack READMEs:
transient peak t = 41.21 (H 1.57e-2, M 4.06e-2), chi floor t = 58.43, min
lapse 2.0e-3, max|K| 6.10, spike real from t = 49.09, edge widest 1.359 at
t = 51.42, corr(K,H) = -0.35 / corr(K,M) = +0.04 after t = 40. Redraw only if
the p012 series gains legs or the scan table gains rows.

## The paper's head-on collapse page (2026-09-18)

`04_binary_headon/headon_collapse_diagnostics` is the article's
head-on figure (sec:headon:contact), drawn with no arguments:

```
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_headon_collapse
```

**REDRAWN 2026-09-24** (the user: "what happens to the formed black hole ... the plot is junk, why is there no solid line ... how the radius compares to the initial 2 wormholes"): a `figure*[t]` strip, 7.05 x 4.3 in, six panels. (a) horizon areal radius and (b) M_MS fill the left half, rows joined by solid lines within contiguous runs, rules at R_star, sqrt(2) R_star (both throats' area) and 2 M_ADM = 4 (M_ADM = 2 in b); (c) pit separation, (d) max|K|, (e) Hamiltonian norm, (f) grid max|phi|, max|Pi|. SINCE 2026-09-26 five panels: (e) went to `constraint_evolution` (e), and (f) is (e), spanning the right half's bottom row. The (2,0) wave panel is gone (waves have their own section). Old (f)->(a), (g)->(b), (a)->(c), (d)->(d), (e)->(e), (i)->(f). Numbers: `scripts/analysis/merger_feedback/headon_remnant.py` (born with both throats' area, R = 1.01 sqrt(2) R_star; M_MS never rises after t = 36). The older notes below describe the ten-panel page.

The spiral collapse page's counterpart with the opposite verdict: the pair
MAKES a black hole, and every horizon point is the corrected orientation
(the oriented scan landed 2026-09-09 00:11, one hour before the head-on
scout launched — the whole campaign ran it live; it is the SPIRAL p012 legs
that lack the live flag, not the head-on). Reads the scout
(`merge_headon_flip_d8_v1_t100`, level 3, dies at the wall t = 26.91), the
paper's arm (`..._v1_lvl5from0_scalar_t100`, LEVEL 5 FROM t = 0 -- no restart,
no mesh seam, no interior device, t = 0-100 clean, 0 aborts) and the down-step
(`..._v1_lvl3down_t100_r03500`). The seamless arm SUPERSEDES the lvl3 -> lvl5
chain `..._v1_lvl5_t100_r02200`, which stays in the script as `SEAMED` for the
late offline anchors only. It reproduces that chain: the (2,0) waveforms agree
to 2.9-5.4 % of peak over the burst window t = 23-70 at R = 10/14/18 and the
radiated energies to 3-8 %; only the post-burst tail diverges (up to 62 % at
R = 18, both amplitudes < 4e-4, both arms noisy there). The seam was never
carrying the result. Horizon record: offline
corrected scans (dx 0.0625) find formation at t = 22 (r = 3.171, R = 5.564,
M_MS = 2.991), growth to R = 5.713 (t = 24), then 4.722 (26) and 4.915/4.874
(42.5/43); the live scans' gaps are APERTURE (shells reach 0.5 sep + 2.3;
once the pits merge the MOTS at r ~ 2.7-3.3 is outside while every shell
inside reports trapped — 125 of 155 level-5 scans); where two arms see the
surface at once they agree (t = 36: R 4.461/4.441, M_MS 2.736/2.737). Mass
FALLS AND SETTLES, 2.99 at formation -> 2.17 at t = 99: phantom infall removes
mass, but not without end. FITS (panels f/g, added 2026-09-21): R_MOTS is
LINEAR, slope -0.00658/unit, rms 0.0324 -- an exponential does NOT converge on
this record, so no asymptotic radius is resolvable and none is drawn. M_MS
settles, a + b*exp(-(t-36)/tau) -> M_inf = 2.160 +- 0.006, tau = 19.4 +- 0.8,
rms 0.0113, a factor 4.8 better than the straight line (dotted asymptote). That
tau is the SAME CLOCK as the scalar channel's shut-off, tau = 19-28 in
`08_waves/scalar_censorship` -- hair shed, source quiet, mass stopped, one
timescale. theta_+ at the common areal minimum
crosses zero between t = 20 and 21; no mouth ever has its own MOTS.

**Trap, do not draw:** V1c's (`..._v1c_latefreeze_t100`) common-scan rows
from t ~ 29 sit at r = 1.15 — INSIDE its own frozen fill (r_full = 1.2) —
and its A/B rows claim "own MOTS" from t = 40 for the same reason. Fill
artefacts, excluded by design here, like theta_common on the spiral page.

Other validated numbers (all re-measured on the SEAMLESS arm 2026-09-21): level
5 walks the wall (scout max|K| 18.1 and H = 13.6 at death vs level-5 max|K|
peak 1.36 at t = 31.55, end 0.13, H falling 4.82e-3 -> 2.70e-3); lapse rides
the 1e-10 clamp t = 38.15-41.50, ends 1.36e-3; chi hits 1e-20 at t = 30.60
(scout: 24.40), ends 2.0e-5; field swallowed, max|phi| 0.90 -> 0.008 with |Pi|
peak 0.069 at t = 42.35;
CAREFUL -- the down-step's old "0.08 % (H) / 1.48 % (M)" was measured against
the SEAMED chain it restarts from and is true of that pair only. Against the
seamless arm drawn here its H sits a constant ~0.2 dex BELOW (its own coarser
truncation history; median |dH|/H = 66 %) while M agrees to 1.30 %. The panel
(e) label says "from the seamed chain" for exactly this reason; (2,0) ringdown swings at t = 28.2/43.6/
63.0/81.7, amplitude x0.6-0.8 per half-swing. Redraw only if a head-on arm
is re-run with the scan aperture widened or new offline scans land.

**Where the names sit, and why (the 2026-09-18 pass).** Five names on this
page were struck through by what they named. The placements below are each
the answer to a measurement, not a guess, and three of them cost frame:

* (a) the black curve's name is under its own descent, on TWO lines. On one
  line it is 23 t-units wide and no clear stretch of this strip is that wide:
  over the curve it was struck through, above the flat start it ran through
  the t = 22 rule AND out of the top.
* (b) "level 3" is left-anchored at t = 1.5. Centred on 13.5 the name is 18
  t-units wide and its tail crossed the MOTS rule.
* (c) "onto the 1e-20 clamp" is right-anchored: left-anchored it ended half a
  point from the right spine.
* (e) the floor drops to 5e-5 (from 2.5e-4) and each norm is named off its
  OWN curve at t = 52 / 62, where the two are furthest apart, with the
  clearance in POINTS. H bottoms at 6.1e-4, which on the old floor left less
  room under it than its own name needed, so the name printed through the
  spine and through both H curves at once.
* (h) the top goes to 0.86 and both thetas are named 4 pt above their own
  curve on the flat left stretch, where they are 0.36 apart.

A label inset given as a fraction of the axis is a different physical gap in
every panel; every gap on this page is now in points. The check is
mechanical, not visual -- a scratchpad probe walks every ax.text box against
every drawn SEGMENT, the spines, the tick labels and the sibling labels, and
this page is clean at 1.5 pt of demanded clearance. Careful: the probe pads
in display pixels at the FIGURE's dpi (100), not at savefig's 300, so a pad
of 5 "px" is 3.6 pt and lights up every deliberate 3 pt gap on the page.

## The paper's refinement-ladder figure (2026-09-18; two panels since 2026-09-23)

`05_binary_spiral/spiral_refinement_ladder` is the article's sec:spiral:wall
figure, a two-column `figure*` since 2026-09-23 (the user: the gauge arms
have a different start time, so a second panel, two columns like the other
figures), drawn with no arguments:

```
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_spiral_ladder
```

(a) reads `campaign/05_binary_spiral/refinement_ladder.dat` (levels 3-7 from
one t = 50 state; plain and damped families kept separate per that file's
own warning — an earlier "turns over at level 7" quote that averaged them is
withdrawn). Plain deaths 52.07 / 53.10 / 55.60 / 56.13 / 56.20
(+1.03/+2.51/+0.53/+0.06 per doubling), halfstep control +0.36 on its level-5
twin; a key names the three kinds of death point. (b) reads
`campaign/05_binary_spiral/wall_clocks.dat`: one row per gauge condition on a
common death clock -- level 3 from t = 0 (d_t alpha = -alpha K 43.65, K NaN;
-2 alpha^2 K 49.03; standard 52.07; eta = 4 61.92) and level 5 tagged by the
time t0 it was switched on (standard L = 128: 59.94 / 60.45 from t0 = 0 / 36;
standard L = 64: 55.60 from 50; eta 4: 60.04 / 60.05 from 50 / 60). The
L = 128 t = 36 arm was (a)'s faint rule until 2026-09-23 and is a point of
(b) now. No gold on this figure.

**Re-read 2026-09-23 against every run log and evolution_params.txt** (all
death times agree to the digits given). Two corrections to the data file,
neither moving a plain number: (1) the damped line used to start at level 3
on `merge_orbit_flip_d12_r05000`, which ran the BUILT-IN window (1e-6 ->
1e-8, never engaged) -- a different configuration from levels 4-6 (radius
1.30/1.00 from t = 50, tau 0.05). It is now `damped_default` and not joined;
the matching level-3 arm (`merger_fix/m4b_fast_r05000`, 52.42 in the archived
fix table) is pruned. (2) The level 4-7 rungs restart
`merger_fix/m4_sealed_r04000`'s Chk05000 (their amr.restart), not r03000's;
that arm evolved undamped to t = 51.2, so the state is r03000's path and the
level-3 reference 52.07 stands. The two 08-31 level-3 probes
`_sg10_r05000` / `_rw_r05000` restart r04000's t = 50 state (damped from
t = 40) -- a different parent, listed in the file's notes, not drawn.
Redraw if the ladder gains rungs or a gauge arm lands.

Same day, the article's gallery/ligo captions were synced to the current
draws (fly-by close-out): gate t = 76, strain peak 1.7e-20 at 89 Hz, spiral
speeds 0.95/1.00/1.00, fly-by ridge 134 Hz.

## The paper's two combined strips (2026-09-18)

The article's first four single-column figures became two two-column strips
at the tops of their pages (the user: "combine fig 1 with fig 2 ... make the
horizontal layout ... and do the same with fig 3 and fig 4 cause now they
span too much space"):

```
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_single_throat_row
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_pair_row
```

`01_single_throat/single_throat_instability` (7.05 x 2.75 since 2026-09-26, one
row: its (d)/(e) norms are `constraint_evolution` (a)/(b); before, 7.05 x 4.35; (c)/(d)/(e) cleaned
2026-09-23 on the user's marks: the t_x crossing rule is drawn only up to 6 pt
above R_star, where the crossing is -- full height it ran through the
"epsilon = -0.01" and gold-fit names; and a dying arm's norms end on their
last FINITE step, the cross there -- the one-step overflow before each NaN
(+0.1: 3.1e-3 -> 56 over 0.02 units) drew a vertical line the height of the
panel) is the undeclared
seed's two panels plus the declared-seed panel; `03_two_throats/
pair_interaction` (7.05 x 2.4) is the sign rule's two panels plus the
placement curve's two. **Neither composer draws anything itself.** Each
panel is still drawn by its home module — `plot_branches.figure_panels`,
`plot_seed_branches.figure_panel`, `plot_sign_rule.figure_panels`,
`plot_placement_curve.figure_panels` — which the standalone single-column
figures also call, so the two renderings of a panel can never drift apart.
A change to what a panel says goes in its home module, where its provenance
notes are; the composer owns only the canvas, the (a)...(d) lettering and
the file. The four standalone figures were deleted on 2026-09-26 (not in the
paper); their modules still draw them on demand.

**What a quarter-page panel needed that a single column did not.** Every
label placed as a fraction of the axis is a different gap at strip width,
and three of them broke: the `R_star` rule names printed across the right
spine (now `style.edge_label`, which anchors to the spine and insets in
POINTS — used in all three modules); the seed panel's two collapse-arm
names met on the stalled line (now on opposite sides of it, with headroom
opened below the lowest curve); the `a = 1` name had no room inside the
frame at all (the like pair's curve passes a hair above it everywhere), so
that panel carries a 1.22 -> 1.35 right margin and names the arm in it.
The placement panel's narrow form (`stacked=False`) also thins the log
decade from eight tick numbers to five (3/6/12/24/48, the user asked for
fewer), drops "below probed d" to the caption and shortens the held-band
note. Read the narrow branches only as a **placement** difference: the
data, the ink and every number are the same objects the stacked form draws.

**Float placement.** `\usepackage[section]{placeins}` had to go with them.
A `figure*` can never be set on the page it is declared on, so a
per-section barrier strands any two-column figure whose section runs less
than a page: Fig. 2's section ends on the page before the earliest page the
figure could take, and the next section's barrier flushed it to a float
page of its own, half white. The article now loads plain `placeins` with
one explicit `\FloatBarrier` before the bibliography — which is the only
thing `[section]` was ever bought for (the LIGO figure printing after the
references) — plus raised `\dbltopfraction` / `\dblfloatpagefraction` in an
`\AtBeginDocument` hook, because REVTeX resets float parameters as the
document opens. 13 pages, both engines, every figure inside the body.

## The momentum-scan orbits, the force-law panel, the regrowth band (2026-09-25)

Three changes from the user's read of the paper, each drawn with no arguments.

**`05_binary_spiral/momentum_scan_orbits`** (new, `plot_momentum_orbits`; the
article's `fig:orbits`, top of sec:spiral:capture). Every sigma = -1 pair
from d = 12, p = 0 (the d = 12 head-on) to 0.45: (a) both throats in the
orbital plane, (b) their separation. The tracks are the chi-pit barycentres
of `binary_throat_diagnostics.dat`, equal to the tracker's centres until the
tracker fuses them (separation ~ 2, t = 31-38) and the only record after;
the pits come from two half-spaces of a FIXED plane, so each track is
followed by continuity. Plunges end (dot) where chi first touches its 1e-8
floor (p = 0: 39.8, 0.12: 44.85, 0.15: 47.0) or the run ends (0.20: 47.85,
0.25: 53.0); p = 0.12 is the production chain's level-3 leg (its pits equal
the L = 64 arm's to every digit through t = 44). All level 3 except p = 0.45,
which is the level-5 L = 128 fly-by the text quotes: its level-3 twin's pit
hops six cells toward the companion at t = 34.75 (1.5c), which alone makes
its closest approach 3.95 instead of ~4.8 -- not drawn. Tracks are averaged
over two time units (level-3 pits sit on 1/16 cells). The fly-by is faint
from t = 43, where its per-mouth scan's areal minimum reaches the window
edge: past it the separation is between the pits of two inflating mouths.
Minima as drawn: p = 0.35 2.80 (raw tracker 2.746), p = 0.45 4.815 (4.797).

**`03_two_throats/pair_interaction`** is five panels now: (c) is the force
law (`plot_force_law`, which reads the RESULT table of
`campaign/03_two_throats/separation_ladder_2026-09-04.txt`, the rows the
ledger quotes): delta d at t = 11.5 for d = 12/14/16/18 against d^-2 through
d = 12 (grey dashed) and A/(d + delta)^2 fitted on d = 12-16 (A = 115.6,
delta = 3.69; gold, dotted past d = 16, where it predicts 0.246 against the
measured 0.2438). The placement panels became (d, e); on the narrower panel
the "scout" name moved left of the probe curve (label audit).

**`01_single_throat/single_horizon_regrowth`**: every legend entry names the
radial kick ("eps = +1e-2 with eps_2 = 0.005, level 4") -- written
"+ eps_2 = 0.005" it read as a pure-quadrupole arm, which the text says only
shrinks -- and the stretch past the first floor (t = 43) is shaded,
"numerical: not a measurement", each curve faint after its own floor.

## The vacuum controls under rows (c) and (d) (2026-09-25, afternoon)

**`08_waves/psi4_gallery`** is four rows now. Rows (c) and (d) carry, in grey
under the ink, each drainhole binary's black-hole twin -- same d and p, bare
punctures, no scalar -- from the control's in-code extraction
`weyl_extraction_mode_22.dat` at the row's own sphere R = 20, on the row's
scale (`VACUUM_OVERLAY` / `overlay_record`, which the ledger reads too):
(c) `bbh_control_d12_p012_t150`, drawn whole -- its merger peaks at 1.02e-2,
t - R = 84.8, 2.9x below and 43 units after the spiral's burst; it was row (e)
and stays in `ARMS` for the LIGO figure and the ledger (`OVERLAID`);
(d) `bbh_control_d12_p045_t100`, cut to the fly-by's window (t - R <= 50):
one cycle at periapsis, peak 9.0e-3, 4.5x below the fly-by, nothing at the
pass. Each is named on its own curve; the spiral's cap note rises to the top
of its cap over the twin's swing. Row (a)'s dashed curve is named "ringdown
fit". Left panels only (CONTEXT is also a sphere of the envelope ramp). Row
titles print p (was P). Drawn with no arguments.
