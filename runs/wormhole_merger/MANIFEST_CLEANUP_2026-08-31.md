# wormhole_merger cleanup — 2026-08-31

Second cleanup (the first is `MANIFEST_CLEANUP_2026-08-28.md`). This one restructured
the folder as well as reclaiming disk.

## Structure

The folder was seventeen sibling run directories with no ordering. It is now grouped by
campaign stage, so the reading order is the order the work happened in:

    00_archive/         dead ends kept for the record (was `archive/`)
    01_single_throat/   Stage 1: does one throat hold still?   (11 runs)
    02_moving_throat/   Stage 2.0: does a moving throat survive? (1 run)
    03_two_throats/     Stage 2.5/2.6: what two throats do      (4 runs)
    <live run>          stays at top level until it finishes, then is filed

No run directory was deleted, and nothing inside one was touched apart from the
duplicate logs below. Each stage folder carries a `NOTES.md`.

The old top-level `INDEX.md` was split into `01_single_throat/NOTES.md` (its Stage 1
bulk), `00_archive/NOTES.md` and `02_moving_throat/NOTES.md`, then removed. Content is
unchanged — it was moved, not rewritten.

**Note:** `output_path` inside each moved run's `params.txt` still records the old
top-level path. These are finished runs, so nothing reads it; it is provenance, not a
live setting.

## Deleted here

| what | size | why safe |
| --- | --- | --- |
| `stage1_lapse5_sg00.launch.log` | 4.8 M | 98 422 lines, of which 98 408 duplicate `run.log` |
| `stage1_lapse5_sg01.launch.log` | 3.3 M | same, 67 549 of 67 563 duplicated |
| `stage1_lapse6_sg01.launch.log` | 4.3 M | same, 87 718 of 87 732 duplicated |

The 14 lines each that were *not* duplicates are the launcher banner — template, binary,
GPU, and the sigma/lapse/refinement overrides actually applied. That is real provenance,
so it was kept as `launch_banner.txt` inside each run before the bulk was dropped.

## Deleted on scratch

| scratch cell | size | why safe |
| --- | --- | --- |
| `s20_boost_p02` | 60 G | 81 raw plotfiles. Everything derived from them is already here: 3 frame series, 4 movies, 4 `.dat` streams and 240 cached slices. Nothing is recoverable only from the plotfiles. |

## Deliberately NOT deleted

`stage1_lapse5_sg00` on scratch, 30 G, 71 plotfiles. It was on the candidate list and was
kept: **no frames were ever extracted from it**, so unlike `s20_boost_p02` its plotfiles
are the only copy of the field data. It is also the most interesting Stage 1 arm — the
sigma = 0 no-collar run that never went unstable and died by running the card out of
memory at t = 35.2. With 893 G free there is no reason to spend it. Delete it only if
disk gets tight and nobody wants pictures of that arm.

## Two zombie processes killed

Consumer sidecars for `stage1_lapse5` and `stage1_lapse6` (pids 768543, 768741) had been
polling `/tmp/grteclyn_scratch/` directories that the 2026-08-28 cleanup deleted — three
days of spinning on paths that no longer existed.

## Checks run before deleting

Only one simulation is live (`merge_orbit_flip_d12`, untouched). Neither scratch cell had
been written to in hours: `s20_boost_p02` last touched 02:00 today, `stage1_lapse5_sg00`
on 2026-08-28.
