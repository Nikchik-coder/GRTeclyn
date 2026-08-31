# wormhole_merger cleanup -- 2026-08-28

## What was deleted

Only **plotfiles on node-local scratch** (`/tmp/grteclyn_scratch/<run>`), for runs
that are dead or superseded.  Nothing under `runs/wormhole_merger/` was deleted:
every run keeps its `params.txt`, `run.log`, `data/`, `small_data/` and
`consumer.log`, so every number already measured is still on disk.

These runs were launched with `WHM_KEEP_PLOTFILES=1`, which switches OFF the
consumer's `--delete` -- that is why the plotfiles accumulated instead of being
drained as they were written.  It was deliberate (a wrong extraction centre had
to be re-measured), and is no longer needed.

| scratch dir | size | why it went |
| --- | --- | --- |
| stage1_lapse5        | 12 G  | sigma = 2.0 reference, ran to t = 40; superseded by the low-sigma arms |
| stage1_lapse6        | 5.7 G | sigma = 2.0 + collar, NaN at t = 21.7; superseded |
| sig05_lapse5         | 2.3 G | ml0 sigma-probe to t = 2, result already tabulated |
| sig00_lapse5         | 2.3 G | ml0 sigma-probe to t = 2, result already tabulated |
| stage1_ml1_lapse6    | 825 M | refinement-ladder probe, NaN at t = 1 |
| stage1_ml0_lapse5    | 113 M | refinement-ladder probe, NaN at t = 0.22 |

Kept: the three live arms (`stage1_lapse5_sg00`, `stage1_lapse5_sg01`,
`stage1_lapse6_sg01`) and the consumer's `_cache`.

To re-derive a radial profile from a deleted run, re-run that arm -- about 40 min
on one card at max_level = 2, stop_time = 40.

## What was reorganised

Superseded runs moved under `archive/` (see `INDEX.md`).  Nothing renamed, nothing
lost -- just out of the way of the runs that are still current.
