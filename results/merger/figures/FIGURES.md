# How each `psi4_analysis_*` figure is drawn

Every six-panel wave figure in this tree, with the command that draws it.
**Add the command here when you draw a figure** — the whole reason this file
exists is that none of them were recorded, and recovering eight command lines
from the pixels of the figures they produced cost a day.

Run each from the repository root, after

```
export PYTHONPATH=$PWD/grteclyn-wrapper/src
alias psi4="grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_psi4_analysis"
```

| figure | command |
|---|---|
| `01_single_throat/psi4_analysis_q1e2_ml4_t50` | `--run single_eps_p1e2_q1e2_ml4_t100_r02500 --group 01_single_throat --t-max 49` |
| `01_single_throat/psi4_analysis_q5e2_gated` | `--run single_eps_p1e2_q5e2_ml4_t100 --group 01_single_throat --stream psi4_mode_l2m0_gated.dat` |
| `04_binary_headon/psi4_analysis_merge_headon_flip_d8_v1c_latefreeze_t100` | `--run merge_headon_flip_d8_v1c_latefreeze_t100 --group 04_binary_headon` |
| `05_binary_spiral/psi4_analysis_freeze_narrow_t100` | `--run campaign/05_binary_spiral/p012/merge_orbit_flip_d12_r03000/part1/psi4_mode_l2m0.dat+merge_orbit_flip_d12_r03000+freeze_narrow_t080_r05000+freeze_narrow_t100_r08000 --group 05_binary_spiral` (first segment as an ABSOLUTE path) |
| `05_binary_spiral/psi4_analysis_freeze_wide_t080_m2` | `--run campaign/05_binary_spiral/psi4_merger_stitched_0_97.dat --group 05_binary_spiral --m 2 --t-max 80` (absolute path) |
| `05_binary_spiral/p012_paper/psi4_analysis_p012_series` | `--run v2_spiral_d12_p012_L128_SERIES --group 05_binary_spiral --name p012_paper/psi4_analysis_p012_series --stream Weyl4_mode_22.dat --m 2 --radii 20 28 36 44 --strain-radius 20` |
| `06_binary_flyby/psi4_analysis_merge_orbit_flip_d12_p045_L128_lvl5_t100` | `--run merge_orbit_flip_d12_p045_L128_lvl5_t100 --group 06_binary_flyby --stream Weyl4_mode_22.dat --m 2 --radii 20 28 36 44 --strain-radius 20` (redrawn at close-out on the full t = 0–100 record) |
| `07_bbh_control/psi4_analysis_bbh_control` | `--run bbh_control_d12_p012_t150 --group 07_bbh_control` |
| `07_bbh_control/psi4_analysis_bbh_control_m2` | `--run bbh_control_d12_p012_t150 --group 07_bbh_control --stream psi4_mode_l2_all.dat --m 2` |

## The validation figures (2026-09-19)

Two figures certify the 2026-09-18/19 validation arms; both are drawn with
no arguments:

```
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_seed_linearity
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_fill_insensitivity
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
constraints. MOTS from t = 33, R 3.80 → 2.41, M_MS 1.90 → 1.24.

`05_binary_spiral/p012_paper/fill_insensitivity` — queue 5 (f): the freeze
twin (fill 1.25/1.75) against the freeze arm (1.40/1.90), same t = 57 seed,
same binary. Max |dPsi4|/peak 0.385/0.370/0.024/0.013 % at R = 20/28/36/44
over t = 57-100; panel (b)'s onsets sit on the causal clock t = 57 + (R - 1.9)
= 75/83/91/99. The fill is not in the physics; it certifies inertness, not a
remnant ringdown.

## The paper's `08_waves` figures (2026-09-16)

The article's two wave figures live in `08_waves/`, cross-cutting because they
belong to no single group. Both are drawn with no arguments:

```
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_psi4_gallery
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_psi4_ligo
```

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
two open burgundy bars in (d) are NOT runs of this campaign and NOT closed
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

`05_binary_spiral/p012_paper/p012_collapse_diagnostics` is the article's
full-page Fig. 5 (`figure*[p]`, sec:spiral:inspiral), drawn with no arguments:

```
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_spiral_collapse
```

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

`04_binary_headon/headon_collapse_diagnostics` is the article's full-page
head-on figure (`figure*[p]`, sec:headon:contact), drawn with no arguments:

```
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_headon_collapse
```

The spiral collapse page's counterpart with the opposite verdict: the pair
MAKES a black hole, and every horizon point is the corrected orientation
(the oriented scan landed 2026-09-09 00:11, one hour before the head-on
scout launched — the whole campaign ran it live; it is the SPIRAL p012 legs
that lack the live flag, not the head-on). Reads the scout
(`merge_headon_flip_d8_v1_t100`, level 3, dies at the wall t = 26.91), the
paper's arm (`..._v1_lvl5_t100_r02200`, level 5, no fill, t = 100 clean) and
the down-step (`..._v1_lvl3down_t100_r03500`). Horizon record: offline
corrected scans (dx 0.0625) find formation at t = 22 (r = 3.171, R = 5.564,
M_MS = 2.991), growth to R = 5.713 (t = 24), then 4.722 (26) and 4.915/4.874
(42.5/43); the live scans' gaps are APERTURE (shells reach 0.5 sep + 2.3;
once the pits merge the MOTS at r ~ 2.7-3.3 is outside while every shell
inside reports trapped — 125 of 155 level-5 scans); where two arms see the
surface at once they agree (t = 36: R 4.461/4.441, M_MS 2.736/2.737). Mass
DRIFTS DOWN, -0.0066/unit on the down-step track (2.99 formation -> 2.17 at
t = 99): phantom infall removes mass. theta_+ at the common areal minimum
crosses zero between t = 20 and 21; no mouth ever has its own MOTS.

**Trap, do not draw:** V1c's (`..._v1c_latefreeze_t100`) common-scan rows
from t ~ 29 sit at r = 1.15 — INSIDE its own frozen fill (r_full = 1.2) —
and its A/B rows claim "own MOTS" from t = 40 for the same reason. Fill
artefacts, excluded by design here, like theta_common on the spiral page.

Other validated numbers: level 5 walks the wall (scout max|K| 18.1 and
H = 13.6 at death vs level-5 max|K| <= 1.34, H falling 4.6e-3 -> 1.4e-3);
down-step lands on level 5 to median 0.08 % (H) / 1.48 % (M) over t = 35-100;
lapse rides the 1e-10 clamp t = 38.5-41.0, ends 1.1e-3; chi clamps at 1e-20
(scout from 24.4, level 5 over 26-38), ends 2.0e-5; field swallowed, max|phi|
0.86 -> 0.008 with |Pi| <= 0.069; (2,0) ringdown swings at t = 28.2/43.6/
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

## The paper's refinement-ladder figure (2026-09-18)

`05_binary_spiral/spiral_refinement_ladder` is the article's sec:spiral:wall
figure, drawn with no arguments:

```
grteclyn-wrapper/.venv/bin/python -m grteclyn_wrapper.visualisation.wormhole_merger.plot_spiral_ladder
```

One data source: `campaign/05_binary_spiral/refinement_ladder.dat` (levels
3-7 from the same t = 50 checkpoint; plain and damped families kept separate
per that file's own warning — an earlier "turns over at level 7" quote that
averaged them is withdrawn). Plain deaths 52.07 / 53.10 / 55.60 / 56.13 /
56.20 (+1.03/+2.51/+0.53/+0.06 per doubling), halfstep control +0.36 on its
level-5 twin, FAINT reference rule at 60.445 = the L = 128 production arm
restarted at t = 36. No horizon at any rung; no burgundy on this figure.
Redraw only if the ladder gains rungs.

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

`01_single_throat/single_throat_instability` (7.05 x 2.5) is the undeclared
seed's two panels plus the declared-seed panel; `03_two_throats/
pair_interaction` (7.05 x 2.4) is the sign rule's two panels plus the
placement curve's two. **Neither composer draws anything itself.** Each
panel is still drawn by its home module — `plot_branches.figure_panels`,
`plot_seed_branches.figure_panel`, `plot_sign_rule.figure_panels`,
`plot_placement_curve.figure_panels` — which the standalone single-column
figures also call, so the two renderings of a panel can never drift apart.
A change to what a panel says goes in its home module, where its provenance
notes are; the composer owns only the canvas, the (a)...(d) lettering and
the file. The four standalone figures are still produced and still correct;
the paper just no longer includes them.

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

## How the commands were recovered, and why it can be trusted

Each candidate was redrawn and compared with the published PNG **panel by
panel**. A command is accepted only when every panel that the intervening code
fixes did not touch comes back pixel-identical — that identity, not plausibility,
is the proof. It caught real mistakes: `--m 2` is inert on a single-mode file and
needs `--stream psi4_mode_l2_all.dat`; the freeze figures need the pre-restart
segment, which was split out of its run's pack as `part1/` after the figures were
drawn; `q1e2_ml4_t50` was drawn while its arm was still running and its stream
ended at t = 49.

## What changed in the redraw, and what it means for reading them

Three fixes landed after most of these figures were first drawn. Panels not
listed here are unchanged.

**Panel (f), the strain against Advanced LIGO — every figure.** The corner of
the 8th-order high-pass in `_psd_psi4_to_strain` was `0.05 × freqs.max()`, i.e.
5 % of the **Nyquist** — a property of how often the waveform was written out,
not of the physics (`b4cc397d`). On the finely-sampled in-code streams that put
the corner at f = 2.5 while the burst sits at f = 0.033, suppressing it by
~1e15. The corner is now `1/T`, set by the record. **Panel (f) of every figure
published before 2026-09-16 understates the strain** — mildly where the stream
was coarse, catastrophically where it was fine.

**Panel (b), the ringdown fit — `bbh_control_m2`, `freeze_wide_t080_m2`,
`q1e2_ml4_t50`.** The fit was reaching its own bounds and being drawn anyway:
`q1e2_ml4_t50` published f = 1.959 1/M and `freeze_wide_t080_m2` f = 2.029 1/M,
both far **above their stream's Nyquist of 0.5 and 1.0** — aliases, not
frequencies. `f303b2a9` capped the fit at Nyquist, which then let it walk to the
LOWER bound instead (`bbh_control_m2`, f = 0.001, tau = 0.0: a flat line drawn
as a fit). It now tries three independent seeds, rejects any solution resting on
a bound, and rejects an e-fold more than 5x the segment it was fitted on —
returning no fit rather than a wrong one. Two figures consequently draw **no
ringdown curve**: `freeze_wide_t080_m2` and `q1e2_ml4_t50`, whose records do not
contain a measurable decay (`GPU_PLAN.md` already says so for the latter).

**Panels (c)-(f) of `freeze_wide_t080_m2`.** `--t-min/--t-max` used to clip the
x-axis of panel (a) only, so a figure captioned "to t = 80" analysed everything
the stream held — one figure describing two different records. They now clip the
record, so panels (c)-(f) of this figure are the t = 0-80 wide arm, as its name
has always claimed.
