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
