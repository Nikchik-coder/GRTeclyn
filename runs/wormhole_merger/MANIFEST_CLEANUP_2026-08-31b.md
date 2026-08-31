# wormhole_merger cleanup — 2026-08-31 (second pass)

The morning pass (`MANIFEST_CLEANUP_2026-08-31.md`) restructured the folder. This one
compacts what the Stage 3 runs left behind, and was done alongside building
[`results/merger/`](../../results/merger/) — nothing was deleted that the pack does not
already hold, or that was not a byte-for-byte duplicate.

Tree size: **1 563 MB → 1 476 MB**, ~90 MB reclaimed while the one live run kept
growing. No run directory was deleted and no `.dat` stream, frame, slice cache or movie
was touched.

## Duplicate launcher logs removed (~40 MB)

Every detached run wrote two copies of the same evolution log: `run.log` inside the run
directory, and `detached_gpu<N>*.log` at the top level. The comparison, per pair:

| file | lines | lines not also in `run.log` |
| --- | --- | --- |
| `detached_gpu0.log` (r03000) | 116 879 | 13 |
| `detached_gpu0_r04000.log` | 68 179 | 13 |
| `detached_gpu0_rw_r05000.log` | 26 547 | 13 |
| `detached_gpu0_sg10_r05000.log` | 8 993 | 14 |
| `detached_gpu1.log` (headon) | 233 013 | 12 |
| `detached_gpu3.log` (p045) | 317 746 | 14 |

The ~13 unique lines are the launcher banner — template, binary, GPU, run and scratch
directories, restart checkpoint, consumer pid and arguments. That is real provenance, so
it was written into each run as `launch_banner.txt` **before** the bulk was dropped, the
same policy as the 2026-08-28 pass.

`detached_gpu2.log` was **kept**: `merge_orbit_flip_d12_n160` is still running and still
writing it. Fold it in the same way when that run finishes.

## Finished-run logs gzipped (50 MB → 4.9 MB)

`run.log` (and `run__part1.log`) in the seven finished Stage 3 runs. Nothing is lost —
read them with `zgrep`/`zcat`. `n160`'s log was left uncompressed because it is live.

## The orphaned arm, given a home

`merge_orbit_flip_d12_r05000` — the narrow-lapse-window arm — had no run directory: it
went in the morning disk sweep before anything was extracted from it, and only its
detached log survived. That log is now `merge_orbit_flip_d12_r05000/run.log.gz` beside a
[`LOST.md`](merge_orbit_flip_d12_r05000/LOST.md) recording what the arm was, what it
measured (NaN in `h11` at t = 52.09, damping at the 1e-6/1e-8 defaults), and what can no
longer be recovered from it.

## Small things

Eight empty `pout/` directories and seven zero-byte `launcher.pid` files from finished
runs. Both are written at launch and never cleaned up; neither carries information once
the run has exited. `n160`'s were left alone.

## Checks run before deleting

One simulation is live — `merge_orbit_flip_d12_n160` on GPU 2, pid confirmed by
`pgrep`, untouched throughout. Every deletion above was either a verified duplicate (line
counts in the table) or an empty file. The `.dat` streams every Plan.md number rests on
were copied into `results/merger/` and committed to git first.
