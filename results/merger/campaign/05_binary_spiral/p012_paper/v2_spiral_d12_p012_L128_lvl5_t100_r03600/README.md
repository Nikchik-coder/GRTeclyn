# v2_spiral_d12_p012_L128_lvl5_t100_r03600 -- stopped by hand at t = 59.81

Queue 5, the arm that went THROUGH the level-3/5 wall of this family.  Level 5
restarted from stage 1's t = 36 checkpoint (`_keep_spiral_premerger_decay/
BinaryWormholeChk03600`), template `params_prod_L128_p012_lvl5_t100.txt`,
binary `main3d_boost_2026-09-08.ex`, 2026-09-15 08:45 - 15:09.

**It did not NaN.**  It was stopped by hand so its card could carry the
replacement arm.  Final state: t = 59.81, zero NaN rows, min_chi pinned on the
1e-8 floor since t = 58.42, max_K 5.66 and still bounded, and L2_Ham FALLING
(1.47e-3 -> 1.25e-3 over the last unit).  For scale, the refinement ladder of
this family dies at 52.07 / 53.10 / 55.60 / 56.13 / 56.20 for max_level
3 / 4 / 5 / 6 / 7 -- every one of those arms was seeded at t = 50, two units in
front of the level-3 wall.  This one was seeded at t = 36, before the merger,
and cleared the whole ladder including the level-7 rung.

## What is in here

Full `data/` streams: in-code Weyl4 (4 spheres, l = 2-4, every step),
`collapse_diagnostics.dat`, `constraint_norms.dat`,
`binary_throat_diagnostics.dat`, `throat_track.dat`, plus the consumer's
`small_data`.  The 191 MB of frames and the 6.2 GB plotfiles are NOT kept; three
plotfiles (t = 55/56/57) survive on scratch at
`/tmp/grteclyn_scratch/_keep_spiral_lvl5_wall_scan/`.

Two files are the evidence behind claims in `research/merger/GPU_PLAN.md`:

* **`horizon_oriented_scan.txt`** -- the orientation-corrected marginal-surface
  scan (`scripts/validation/ah_oriented_scan.py`) over the t = 55/56/57
  plotfiles.  **No MOTS at any of the three times**, at level 3 (dx 0.0625,
  r = 0.15-4.0) and level 5 (dx 0.0156, r = 0.03-1.6): the remnant is still a
  wormhole, throat areal radius 4.104 / 4.062 / 4.018, level 5 reading 4.015
  against level 3's 4.018 so it is resolution-converged to 0.1 %.  The scan also
  reports, at every time, that the naive +r orientation WOULD call r ~ 0.29-0.84
  trapped -- the historic `ah_radial_scan.py` bug, and the source of the
  "common horizon at t = 30.77" claim withdrawn from the plan on 2026-09-15.
  This arm was never scanned live: its consumer profile `orbit-modes` carries no
  `--horizon-scan`.

* **`collapse_region_profiles.png`** and **`core_radial_profile_OFFLINE_t57.dat`**
  -- shell profiles of chi, |K| and lapse from the same plotfiles, produced
  OFFLINE in python (one row per shell; not the in-code
  `core_radial_profile.dat` format, which is one row per time).  They show
  max|K| is not central but a thin spike ON the throat: 0.07 outside, 2.62 at
  r = 1.047, 0.07 again by r = 1.20, growing 0.98 -> 1.53 -> 2.60 over t = 55-57
  while min(chi) and min(lapse) do not move.  That measurement is why
  `CoreRadialProfile.hpp` exists.
