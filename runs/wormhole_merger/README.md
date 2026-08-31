# `runs/wormhole_merger`

Working output of the wormhole-merger campaign. Everything here was produced by
`scripts/campaigns/wormhole_merger/run_single.sh`, and the argument it all feeds is
[`research/merger/Plan.md`](../../research/merger/Plan.md) — that document is the
reasoning, this folder is the evidence.

The campaign in one line: **put a real wormhole throat on the grid, prove one throat
holds still, prove a moving throat survives, then find out what two of them do to each
other.** The answer to the last part is that two identical throats *repel*, and that
reversing the field direction of one is the only gravity-driven route to a merger.

## Layout

Grouped by campaign stage, so the folder reads in the order the work happened.

| folder | stage | what it asked | runs |
| --- | --- | --- | --- |
| [`00_archive/`](00_archive/NOTES.md) | pre-history | routes that were tried and abandoned | 3 groups |
| [`01_single_throat/`](01_single_throat/NOTES.md) | 1 | Does one throat just sit still? | 11 |
| [`02_moving_throat/`](02_moving_throat/NOTES.md) | 2.0 | Does a *moving* throat survive? | 1 |
| [`03_two_throats/`](03_two_throats/NOTES.md) | 2.5–2.6 | What do two throats do to each other? | 4 |

Each folder has a `NOTES.md` with its runs, its parameters and its result.

**A live run sits at the top level** until it finishes, then gets filed into a stage
folder. Right now that is `merge_orbit_flip_d12` — Stage 2.7, the merger run: the
like-charge baseline orbit with exactly one line changed, throat B's field direction
reversed. Masses, widths, separation, orbital push, grid and binary are all identical to
the baseline, so any difference in outcome is the sign and nothing else.

## The result so far

| | |
| --- | --- |
| one throat holds still | −0.36 % on the throat radius over 40 M, no NaN |
| a moving throat survives | crossed 3.3 grid units, zero lost rows, no NaN |
| **two identical throats repel** | +0.0127 outward released from rest, no momentum involved |
| the push is set by throat *width*, not mass | halving the radius cut it 3.0× |
| **reversing one throat's field makes them fall together** | −0.0196 inward; infall/escape ratio 1.511 ± 0.033 against 1.500 predicted |

## Housekeeping

**The size is not here.** This whole tree is ~370 MB. Plotfiles and checkpoints go to
node-local scratch, which runs to hundreds of GB — checkpoints alone are ~7.7 GB each.
When reclaiming disk, look there, not here.

**The Stage 1 deaths are results, not junk.** Eleven runs in `01_single_throat/` died
between t = 21 and t = 35. That ladder is how the campaign established the blow-up is
physical rather than numerical — moving the refinement boundary, changing the
dissipation, or removing the mesh entirely does not move it. Deleting them deletes the
evidence for four Plan.md sections.

Cleanups are recorded in `MANIFEST_CLEANUP_*.md`. Before deleting anything: confirm
nothing is running, check the results were extracted, and write a manifest.

## Conventions that keep biting

- **Never run the binary directly.** AMReX writes `parameters_and_version.txt` with
  absolute paths into the working directory; the launcher clones the params and `cd`s
  somewhere harmless, and registers `launcher.pid` so the run can be stopped cleanly.
- **Name the frame fields at launch.** `WHM_CONSUME_ARGS` decides which fields become
  pictures. Its default is empty, so a run launched without it renders nothing at all
  and writes no slice cache — and by the time you notice, the plotfiles are gone.
- **Ask the slice cache, not the tracker.** `frames/_slice_cache/` keeps each 2-D slice
  as a small array. Throat positions come from those, sub-cell and smooth at 1e-4;
  `throat_track.dat` has a quantum of ~0.03 and exists only to aim refinement boxes.
- **Coordinates lag reality** for roughly the first five time units while the gauge
  settles. Nothing measured before then means what it appears to mean.
- **Redraw before making movies.** Live frames are scaled per frame, so the colour bar
  moves. `scripts/plot/rerender_frames.py <run>/frames --movies` redraws the whole
  series against one fixed scale.

Per-run layout: `params.txt` (the exact input, paths rewritten), `run.log`, `data/` and
`small_data/` (the `.dat` streams), `frames/` (pictures plus `_slice_cache/`), `movies/`.
