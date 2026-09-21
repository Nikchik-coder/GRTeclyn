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
to wherever that run's own history ends. Legs of a restart chain and arms cut
short for reasons outside the physics are not kept, however pretty: a viewer
cannot tell a leg from a run once the file is on its own, and a partial record
invites exactly the misreading the article spends paragraphs undoing.

**Reaching the end of the record is not the same as reaching `stop_time`.** An
arm that hits a curvature wall and NaNs has shown its whole history — the wall
is the result. An arm that was stopped by hand, or that a later arm supersedes
at higher resolution, has not.

**A stitch is allowed only where no single arm covers the whole history, and
then it must say so.** Where a seamless arm exists it replaces the chain it
supersedes and the chain's *numbers* stay in the pack, which is where that
evidence belongs — that is why the head-on's stitch and the spiral's SERIES
went. But the spiral has no seamless arm that reaches the end: the free
evolution dies at the wall at t = 59.94 and only the frozen-core arm continues.
There the stitch IS the record, and the row below carries the seam time, what
changes across it, and what may not be read from the second half.

Pruned under this rule on 2026-09-21: the head-on's stitched-across-t=22 set
(superseded by the level-5-from-zero arm, which is one grid over the same span),
the spiral's two separate legs and the SERIES stitch of them (superseded for
t < 60 by the same, and it stopped at t = 57), the level-3 fly-by (stopped at
t = 91 of a requested 200, and superseded by the L = 128 level-5 arm), the
mouth-instrumented spiral arm (t = 0–50, a shorter and coarser record of an
encounter the kept arm shows whole), and the two `hold_branch_*` pairs, which
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
| `then_freeze_t0-100` | a STITCH: the free arm to its wall, then the frozen-core arm to t = 100. Used only where no single arm reaches the end — see the rule above |
| **`t100`, `t150`, `t200`** | **the stop_time REQUESTED, not necessarily the one reached.** A run that hit a curvature wall stops where it stopped; the "ends at" column below is the truth |

| set | what it shows | ends at |
|---|---|---|
| `01_single_throat/single_eps_m1e2_ml4_t100` | **The throat that INFLATES.** The ε = −0.01 kick at level 4 — article Fig. 3. Areal radius grows ×3.0 and no trapped surface ever forms; what it carries instead is that surface's mirror, an anti-trapped shell. Six fields | t = 100 |
| `01_single_throat/single_pureq_q1e2_ml4_t100` | **The throat that COLLAPSES.** Pure quadrupole, no radial kick — and it still collapses and radiates. Watch it beside the inflating arm above: same throat, same level, opposite fates | t = 100 |
| `01_single_throat/single_eps_p1e2_t100` | the seeded throat, ε = +0.01, at level 3: χ, K, lapse, φ, Π | t = 100 |
| `01_single_throat/single_eps_p1e2_q5e3_ml4_t100` | the halved quadrupole seed (gate 3's lower point), level 4 | t = 100 |
| `04_binary_headon/merge_headon_flip_d8_v1_lvl5from0_scalar_t100` | **The head-on merger the paper quotes.** Two throats fall together from rest and make a black hole. Level 5 from t = 0, so no restart, no seam and no interior device anywhere in the record — one grid, 0 aborts. Six fields | t = 100 |
| `05_binary_spiral/v2_spiral_d12_p012_L128_lvl5from0_then_freeze_t0-100` | **The spiral merger, whole.** The d = 12, p = 0.12 pair from its initial data to t = 100, twelve fields, one colour scale over the entire series. It is a STITCH, and it has to be: the free evolution **dies at the curvature wall at t = 59.94** — which is the paper's result, not a failure — and only the frozen-core arm continues. Frames t = 0–59 are `..._lvl5from0_t100`, level 5 from t = 0 with no seam of its own; frames t = 60–100 are `..._lvl5_t100_freeze_r05700`. **Past t = 59 the core is FROZEN and is not physics**: `CoreFreezeFill` holds everything inside coordinate radius 1.40, blending out to 1.90, at its t = 57 state, so the dark centre stops evolving by construction and nothing may be read from it. Outside that ball the evolution is real and certified — the freeze arm agrees with the free arm to 0.1 % on the scalar flux over their overlap. At the join the core's min χ steps 3.46e-4 → 1.89e-4 (the held value), a change confined to r < 1.9 and invisible on the colour scale, while the frame's mean χ agrees to 0.0014 % | **t = 100 (free to 59.94, frozen after)** |
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
