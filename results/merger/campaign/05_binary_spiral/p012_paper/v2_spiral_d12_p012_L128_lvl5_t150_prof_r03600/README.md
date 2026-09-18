# v2_spiral_d12_p012_L128_lvl5_t150_prof_r03600

**The arm that went furthest, and the first one that says WHERE the wall is.**
Level 5 from stage 1's t = 36 checkpoint, no freeze, with the new in-code radial
core profile on. Launched 2026-09-15 15:35 on the user's word, **died 22:01 at
t = 60.445**: `NaN diagnostic: rank=0 level=5 component=1 name=h11`, clean abort
out of `GRAMRLevel::post_timestep`. 6 h 26 m, 3.80 code units/h, one card.

Binary `main3d_coreprof_2026-09-15.ex` (md5 `32e12cc4`), whose base is the
2026-09-10 seedl2 build with the seed keys absent — so this is the 2026-09-08
boost physics plus one new diagnostic. Seeded from `BinaryWormholeChk03600`
(t = 36, L2_Ham 1.5e-3, L2_Mom 1.9e-3), two levels added at the restart
(dx 0.0625 → 0.0156).

## What it settles

**1. It beat the whole refinement ladder.** t = 60.44 against 52.09 / 53.10 /
55.60 / 56.13 / 56.20 at max_level 3–7, every rung seeded at t = 50. +4.2 units
on the best of them, and the ladder had already SATURATED between levels 6 and 7.

**2. Nothing global failed.** L2_Ham 1.004e-3 and L2_Mom 4.910e-3 at the last
step, both still **falling** (−2.8e-4 and −4.2e-4 per unit over the final two
units). The merger excursion peaked at 1.58e-2 / 4.07e-2 around t = 41.2 and
fully relaxed. This death is a local core failure, not a constraint failure.

**3. The wall has a measured size and a measured shape.** See
`core_radial_profile.png`. `max|K|` does not pile up at the centre: it sits on a
narrow spike that grows and moves **inward**.

| t | peak max\|K\| | r of the peak | outer edge (\|K\| > 0.2) |
|---|---|---|---|
| 51 | 0.22 | 1.141 | 1.172 |
| 53 | 0.42 | 1.266 | 1.328 |
| 55 | 0.97 | 1.172 | 1.266 |
| 57 | 2.62 | 1.047 | **1.172** |
| 58 | 4.26 | 0.984 | 1.109 |
| 60.44 | 6.03 | 0.734 | 1.078 |

The **widest the disturbance ever gets is 1.359, at t = 51.4**; after t ≈ 52 it
contracts monotonically. Meanwhile `min(chi)` reaches the 1e-8 floor at
**t = 58.43**, at r = 0.078, and `min(lapse)` bottoms at 2.0e-3.

*Read the flat region honestly:* before **t = 49.09** the profile is flat at
|K| ≈ 0.08 across r = 0.5–1.3 and there is no spike at all — at t = 45 the
"peak" is 0.0782 against a 0.0781 background, so the peak-radius curve there is
argmax noise, not a feature, and it is greyed out in the figure for that reason.
An earlier reading of the apparent jump at t ≈ 45.3 as a physical event was
wrong.

**4. The new diagnostic is provably non-invasive.** This arm and its predecessor
`v2_spiral_d12_p012_L128_lvl5_t100_r03600` started from the same `Chk03600` and
ran **different binaries** (`32e12cc4` here, `7acbfbd5` there). Over the whole
shared window t = 36.01–59.84, 2384 rows, `collapse_diagnostics.dat`,
`constraint_norms.dat`, `throat_track.dat` and every `Weyl4_mode_*.dat` are
**byte-for-byte identical**. The reduction reads the state and touches nothing,
and the run is bit-reproducible on this hardware.

**5. The instrument agrees with the independent global reductions.** At the last
step the binned composite returns max|K| = 6.030 and min(chi) = 1.0e-8, equal to
`collapse_diagnostics.dat` to every digit printed.

**6. Coverage is complete.** 128/128 shells populated for all but the first four
rows (t = 36.01–36.04, the two innermost shells, while the regrid settled):
8 empty entries out of 312 832. The composite `makeFineMask` walk over all five
levels does what the finest-level-only first cut could not.

## Why this file exists at all

The frames cannot see this. The t = 60 `K_z` frame's colour scale tops out at
8e-3 because the wave zone sets it, so an |K| = 6 spike 0.25 wide is a saturated
dot about 1.5 px across at the slice cache's dx = 0.195. A plotfile at this
resolution is 6.2 GB and the consumer keeps three; the binned reduction is 31 MB
for the whole run at 100× the plotfile time resolution.

## What it does NOT show

No horizon scan was run on this arm live (profile `orbit-modes` carries no
`--horizon-scan`). The oriented scan over the predecessor's t = 55/56/57
plotfiles found **no MOTS**. The t = 58–60 question — whether one forms after
the lapse collapses — was answered by hand afterwards over `Plt05800/05900/06000`
(`horizon_oriented_scan_t58-60.txt`, at level 3 AND level 5): **still no MOTS
at any of them**, throat areal R = 3.97 / 3.93 / 3.87, the two levels within
0.2 %. So the whole measured record, t = 55–60, collapses with no horizon
found; only the final 0.44 units are unscanned.

## Files

| file | what |
|---|---|
| `core_radial_profile.dat.gz` | the headline stream. 2444 rows at dt = 0.01, 641 columns = time + 128 shells × {chi_min, absK_max, lapse_min, n, dx}, header intact. gunzip to 31 MB. |
| `core_radial_profile.png` | the figure above |
| `collapse_diagnostics.dat` | **columns are `min_lapse, min_chi, max_abs_K`, in that order**, then the min-lapse position and the phi/Pi extrema. No header line — `SmallDataIO` does not write one on a restart. |
| `constraint_norms.dat` | L2_Ham, L2_Mom. Same missing-header caveat. |
| `Weyl4_mode_*.dat` | in-code extraction, 4 spheres at R = 20/28/36/44, l = 2–4 all m, 2444 rows at dt = 0.01. **This is the waveform to quote**, not the consumer's `psi4_*`, which samples once per unit and at its python default radii. |
| `throat_track.dat`, `binary_throat_diagnostics.dat` | throat centres and per-side diagnostics. The A/B split degrades after the merger; the sentinels (1e30) in the latter are that, not corruption. |
| `psi4_*.dat`, `scalar_modes.dat`, `boundary_flux.dat` | consumer streams, cross-check only |
| `run_tail.log`, `Backtrace.0` | the death, verbatim (paths and host scrubbed) |
| `params.txt` | exact configuration. (`parameters_and_version.txt` is gitignored campaign-wide and stays in the run directory only — it records no version anyway, just "GRTeclyn version (unknown)".) |
| `horizon_oriented_scan_t55-57.txt` | the oriented marginal-surface scan over the t = 55/56/57 plotfiles: **no MOTS** at level 3 or level 5, throat areal R = 4.104 / 4.062 / 4.018. Folded in 2026-09-16 from the superseded `_t100_r03600` pack. |
| `horizon_oriented_scan_t58-60.txt` | the same scan over t = 58/59/60, level 3 and level 5: **no MOTS**, throat areal R = 3.970 / 3.923 / 3.872 (level 5), levels within 0.2 %. The article's Fig. 5 panels (f)-(g) draw both scan files. |
| `collapse_region_profiles_OFFLINE_t55-57.png`, `core_radial_profile_OFFLINE_t57.dat` | the offline python shell profiles that motivated the in-code module, same provenance. Different layout from `core_radial_profile.dat.gz` — do not mix them. |

**This pack supersedes `v2_spiral_d12_p012_L128_lvl5_t100_r03600`,** which was the same run
killed at t = 59.84 for the rebuild and was dropped 2026-09-16: all 30 of its data files are a
byte-exact prefix of the ones here, and its three unique artefacts were folded in above. The
paper's p012 series is therefore two runs — stage 1 at level 3, and this one.

Movies (12 fields, 24 frames each, t = 37–60) are in the run directory, not
packed. Checkpoints t = 57/58/59/60 were held on scratch at close-out; **t = 57
is the last one in front of the chi floor** and is the only valid seed for a
restart that is meant to survive.
