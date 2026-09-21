# The campaign's movies

Every movie the merger campaign keeps, in one place. They used to sit in each
run's `campaign/<group>/<run>/movies/` — 200 files across 32 runs, most of them
scouts and restarts that no result rests on. This folder holds the arms that
answer a question; the rest were pruned (`runs/wormhole_merger/MANIFEST_CLEANUP_2026-09-16.md`
and `_2026-09-21.md`, and every file is recoverable from git history).

Layout mirrors `campaign/` and `figures/`: `<group>/<run>/movie_<field>_z.mp4`.
All are x–y slices through the midplane at one fixed colour scale per field —
a colour means the same value in every frame, which is what makes a movie
readable as physics rather than as a light show.

## The rule: one folder, one whole run

**A set is kept only if it shows a run's WHOLE history** — from its initial data
to wherever that run's own history ends. Legs of a restart chain, stitches
across a seam, and arms cut short for reasons outside the physics are not kept,
however pretty: a viewer cannot tell a leg from a run once the file is on its
own, and a partial record invites exactly the misreading the article spends
paragraphs undoing. Where a seamless arm exists it replaces the chain it
supersedes; the chain's *numbers* stay in the pack and the agreement is quoted
in the text, which is where that evidence belongs.

**Reaching the end of the record is not the same as reaching `stop_time`.** An
arm that hits a curvature wall and NaNs has shown its whole history — the wall
is the result — and it is kept. An arm that was stopped by hand, or that a
later arm supersedes at higher resolution, has not, and it is not. This is why
the spiral below ends at t = 59.94 and stays, while the level-3 fly-by that
stopped at t = 91 of a requested 200 does not.

Pruned under this rule on 2026-09-21: the head-on's stitched-across-t=22 set
(superseded by the level-5-from-zero arm), the spiral's two separate legs and
the SERIES stitch of them (same reason), the level-3 fly-by (stopped short, and
superseded by the L = 128 level-5 arm), and the two `hold_branch_*` pairs, which
carried two fields each rather than a run.

## Reading the folder names

Folder names are the run names, so a movie can always be traced to its line in
`runs_registry.tsv` and its pack under `campaign/`. They decode:

| part | means |
|---|---|
| `eps_p1e2` / `eps_m1e2` | the declared spherical kick, ε = **+0.01** / **−0.01**. The sign picks the branch: `p` collapses, `m` inflates |
| `q1e2`, `q5e3`, `pureq` | the quadrupolar kick ε₂ = 0.01, 0.005, and `pureq` = quadrupole only, no radial kick |
| `ml4`, `lvl5`, `lvl3` | maximum refinement level |
| `lvl5from0` | level 5 from t = 0 — no restart, no mesh seam anywhere in the record |
| `d8`, `d12` | initial separation |
| `p012`, `p045` | initial momentum per hole, 0.12 / 0.45 |
| `L128` | box half-width 128 (the doubled box) |
| **`t100`, `t150`, `t200`** | **the stop_time REQUESTED, not necessarily the one reached.** A run that hit a curvature wall stops where it stopped; the "ends at" column below is the truth |

| set | what it shows | ends at |
|---|---|---|
| `01_single_throat/single_eps_m1e2_ml4_t100` | **The throat that INFLATES.** The ε = −0.01 kick at level 4 — article Fig. 3. Areal radius grows ×3.0 and no trapped surface ever forms; what it carries instead is that surface's mirror, an anti-trapped shell. Six fields | t = 100 |
| `01_single_throat/single_pureq_q1e2_ml4_t100` | **The throat that COLLAPSES.** Pure quadrupole, no radial kick — and it still collapses and radiates. Watch it beside the inflating arm above: same throat, same level, opposite fates | t = 100 |
| `01_single_throat/single_eps_p1e2_t100` | the seeded throat, ε = +0.01, at level 3: χ, K, lapse, φ, Π | t = 100 |
| `01_single_throat/single_eps_p1e2_q5e3_ml4_t100` | the halved quadrupole seed (gate 3's lower point), level 4 | t = 100 |
| `04_binary_headon/merge_headon_flip_d8_v1_lvl5from0_scalar_t100` | **The head-on merger the paper quotes.** Two throats fall together from rest and make a black hole. Level 5 from t = 0, so no restart, no seam and no interior device anywhere in the record — one grid, 0 aborts. Six fields | t = 100 |
| `05_binary_spiral/v2_spiral_d12_p012_L128_lvl5from0_t100` | **The spiral merger the paper quotes, and it does not reach t = 100.** The d = 12, p = 0.12 pair whole at level 5 from t = 0, one grid, and it **dies at the curvature wall** — which is the result, not a failure: run from zero it hits the same wall as the seamed chain, to 0.8 %, so the wall is the merger's own dynamics and not the grid's seed. Twelve fields | **t = 59.94 (NaN at the wall)** |
| `05_binary_spiral/v2_spiral_d12_p012_L128_lvl3_t050_mouths` | the mouth-instrumented arm — the two throats swell +12 % and coalesce with no horizon. Backs `figures/05_binary_spiral/p012_paper/mouth_growth` | t = 50 |
| `06_binary_flyby/merge_orbit_flip_d12_p045_L128_lvl5_t100` | **The pair that does NOT merge.** The p = 0.45 fly-by at level 5 on the doubled box: both mouths expand, no horizon ever | t = 100 |
| `07_bbh_control/bbh_control_d12_p012_t150` | the black-hole binary control at the spiral's separation and momentum — what the same encounter looks like with no scalar | t = 150 |
| `07_bbh_control/bbh_control_d12_p045_t100` | the momentum-matched control: the SAME initial data as the p = 0.45 fly-by, minus the scalar. Two black holes swing past each other and separate -- no merger, no close pass -- because without the ghost field the pull is 6x weaker. Watch it beside `06_binary_flyby/merge_orbit_flip_d12_p045_L128_lvl5_t100`, where the same momentum falls to 4.8 and the mouths inflate: the pair of movies is the 70x energy ratio, visible | t = 100 |

## Remaking one

Movies are stitched from cached frames, never from plotfiles directly:

```
.venv/bin/python grteclyn-wrapper/scripts/plot/rerender_frames.py <run>/frames --movies
```

which redraws every cached slice on one fixed colour scale and then calls
`make_movies.sh`. A run whose `frames/` is gone cannot be remade — check before
deleting frames, not after.
