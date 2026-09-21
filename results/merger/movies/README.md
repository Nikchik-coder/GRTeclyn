# The campaign's movies

Every movie the merger campaign keeps, in one place. They used to sit in each
run's `campaign/<group>/<run>/movies/` — 200 files across 32 runs, most of them
scouts and restarts that no result rests on. This folder holds the arms that
answer a question; the rest were pruned (`runs/wormhole_merger/MANIFEST_CLEANUP_2026-09-16.md`,
and every file is recoverable from git history).

Layout mirrors `campaign/` and `figures/`: `<group>/<run>/movie_<field>_z.mp4`.
All are x–y slices through the midplane at one fixed colour scale per field —
a colour means the same value in every frame, which is what makes a movie
readable as physics rather than as a light show. Frames are ~650x540 (some
~900x815); no run outside `01_single_throat/hold_*` still has cached frames, so
these cannot be re-rendered larger.

| set | what it shows |
|---|---|
| `01_single_throat/hold_branch_expansion_ml4` | the isolated throat at level 4: it **expands**, R +122 % by t = 100. `movie_chi_z__lowfloor_twin.mp4` is the min_chi 5e-10 twin — the two are byte-identical, which is how we know the floor is not load-bearing |
| `01_single_throat/hold_branch_collapse_lvl3` | the same throat at level 3: it **collapses**, R −51 %. Two resolutions, two fates — `campaign/01_single_throat/BRANCHES.md` |
| `01_single_throat/single_eps_p1e2_t100` | the seeded throat, ε = +0.01: χ, K, lapse, φ, Π |
| `04_binary_headon/merge_headon_flip_d8_v1_lvl5_t100_r02200_stitched_from_t0` | the head-on merger **with no freeze and no fill** (`core_freeze_fill = 0`): level 5 alone carries it through the wall. Stitched across the t = 22 restart, so it runs t = 0–100 (179 frames) |
| `04_binary_headon/merge_headon_flip_d8_v1_lvl5from0_scalar_t100` | **the head-on arm the paper now quotes** — maximum level 5 from t = 0, so there is no restart to stitch across and no seam anywhere in the record: one grid, t = 0–100, 0 aborts. Six fields (χ, K, lapse, φ, Π, Weyl4_Re). It supersedes the stitched entry above, which it reproduces to 2.9–5.4 % of peak on the (2,0) wave; keep that one only as the seam's own record |
| `05_binary_spiral/v2_spiral_d12_p012_L128_SERIES` | the paper's d = 12, p = 0.12 spiral as ONE history: level 3 for t < 36, level 5 for t ≥ 36, to t = 57 |
| `05_binary_spiral/v2_spiral_d12_p012_L128_lvl3_t050` | the same series' first leg alone (level 3, t = 0–50) |
| `05_binary_spiral/v2_spiral_d12_p012_L128_lvl5_t150_prof_r03600` | its second leg alone (level 5, t = 36–60.44, to the NaN) |
| `06_binary_flyby/merge_orbit_flip_d12_p045_t200` | the p = 0.45 flyby to t = 200 — the pair that does not merge |
| `01_single_throat/single_eps_p1e2_q5e3_ml4_t100` | the halved quadrupole seed (gate 3's lower point), level 4, t = 0–100 |
| `01_single_throat/single_pureq_q1e2_ml4_t100` | the pure quadrupole — no radial kick, and it still collapses and radiates |
| `06_binary_flyby/merge_orbit_flip_d12_p045_L128_lvl5_t100` | the fly-by at level 5 on L = 128, t = 0–100 — both mouths expand, no horizon ever |
| `07_bbh_control/bbh_control_d12_p012_t150` | the black-hole binary control at the same separation and momentum, to t = 150 |
| `07_bbh_control/bbh_control_d12_p045_t100` | the momentum-matched control: the SAME initial data as the p = 0.45 fly-by, minus the scalar. Two black holes swing past each other and separate -- no merger, no close pass -- because without the ghost field the pull is 6x weaker. Watch it beside `06_binary_flyby/merge_orbit_flip_d12_p045_L128_lvl5_t100`, where the same momentum falls to 4.8 and the mouths inflate: the pair of movies is the 70x energy ratio, visible. To t = 100 |
| `05_binary_spiral/v2_spiral_d12_p012_L128_lvl3_t050_mouths` | the production spiral's stage 1 re-run with the mouth instruments on, t = 0–50 — the two throats swell +12 % and coalesce with no horizon |

## Remaking one

Movies are stitched from cached frames, never from plotfiles directly:

```
.venv/bin/python grteclyn-wrapper/scripts/plot/rerender_frames.py <run>/frames --movies
```

which redraws every cached slice on one fixed colour scale and then calls
`make_movies.sh`. A run whose `frames/` is gone cannot be remade — check before
deleting frames, not after.
