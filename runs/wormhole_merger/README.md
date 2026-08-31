# `runs/wormhole_merger` — what each run is

Working output of the wormhole-merger campaign. Every cell here was produced by
`scripts/campaigns/wormhole_merger/run_single.sh`, and every one is cited by a numbered
section of [`research/merger/Plan.md`](../../research/merger/Plan.md) — that document is the
argument, this folder is the evidence behind it.

The campaign in one line: **put a real wormhole throat on the grid, prove one throat holds
still, prove a moving throat survives, then find out what two of them do to each other.**
The answer to the last part is that two identical throats *repel*, and that reversing the
field direction of one of them is the only gravity-driven route to a merger.

## Live

| run | what it is | state |
| --- | --- | --- |
| `merge_orbit_flip_d12` | **Stage 2.7, the merger run.** The like-charge baseline orbit with exactly one line changed — throat B's field direction reversed. Everything else (masses, widths, separation, orbital push, grid, binary) is identical, so any difference in outcome is the sign and nothing else. | in flight, `stop_time = 60`, contact expected near t ≈ 30 |

## The two-throat result — Plan.md §8

These four are the load-bearing evidence that same-sign throats repel and opposite-sign
throats attract. Do not delete them.

| run | question it answers | result |
| --- | --- | --- |
| `orbit_d12_p012` | Do two identical throats on a bound orbit fall together? | **No.** Stopped at t = 20 having opened 2.02 units and still accelerating apart. The like-charge baseline. |
| `ctrl_rest_d12` | Is that separation just the initial sideways push? | **No.** Released from rest with zero momentum, they still separate: +0.0127 outward, +0.47 by t = 11.5. |
| `ctrl_rest_a1` | Does the push scale with throat *width* or with mass? | **Width.** Halving the radius cut the push 3.0×; a mass-tracking force would not have changed at all. |
| `ctrl_flip_d12` | Does reversing one throat's field turn the push into a pull? | **Yes.** −0.0196 inward, −0.56 by t = 10.5. Infall-to-escape ratio 1.511 ± 0.033 against 1.500 predicted. |

All four use the same body: drainhole data (`wormhole_id_type = 1`, mass in the lapse),
a = 2, m = 1, d = 12, L = 64, N = 128, `max_level = 3`, lapse type 5, sigma 0.1, moving
refinement boxes. `ctrl_rest_a1` differs only in a = 1; `ctrl_flip_d12` only in
`wormhole_phi_sign_B = -1`; `orbit_d12_p012` only in the tangential momenta P = ±0.12.

## One throat, and one moving throat — Plan.md §1–§7

| run | stage | what it asked | how it ended |
| --- | --- | --- | --- |
| `s20_boost_p02` | 2.0 | Does a *moving* throat survive? | **Completed t = 40.** Crossed 3.3 grid units, no lost rows, no NaN. The shakedown the two-throat work is built on. |
| `s16ml3_lapse5_sg01_fg` | 1.6 | Does the throat survive with three refinement levels? | **Completed t = 40.** The 40 M stability record. |
| `stage1_lapse5` | 1 | Baseline: does one throat hold still? | Completed t = 40 with the inherited sigma = 2.0. |
| `stage1_lapse5_sg00` | 1.2 | Sigma ladder: 0.0 | Died t = 35.2 |
| `stage1_lapse5_sg01` | 1.2 | Sigma ladder: 0.1 | Died t = 24.2 |
| `stage1_lapse6` | 1.3 | Collar lapse, sigma 2.0 | Died t = 21.7 |
| `stage1_lapse6_sg01` | 1.3 | Collar lapse, sigma 0.1 | Died t = 31.4 |
| `s15_lapse5_sg00_fg` | 1.5 | Fixed boxes, lapse 5, sigma 0.0 | Died t = 23.5 |
| `s15_lapse5_sg01_fg` | 1.5 | Fixed boxes, lapse 5, sigma 0.1 | Died t = 24.2 |
| `s15_lapse6_sg00_fg` | 1.5 | Fixed boxes, collar lapse | Died t = 26.2 |
| `s1uni128_lapse5_sg01` | 1.4 | Is the blow-up the mesh or the wormhole? Uniform grid, N = 128 | Died t = 6.6 |
| `s1uni256_lapse5_sg01` | 1.4 | Same, N = 256 | Died t = 1.2 |

**The deaths are the result, not a failure.** The Stage 1.2–1.5 ladder exists to show that
moving the refinement boundary, changing the dissipation, or removing the mesh entirely does
*not* move the blow-up — which is how the campaign established that something physical is
growing rather than something numerical. Deleting them would delete the evidence for
Plan.md §2–§5.

`archive/` holds the earlier dead ends kept for the record: `phase2_puncture/` (the puncture
route, which destroys the throat it is meant to weigh), `stage0_t0/` (t = 0 grid checks) and
`stage1_probes/` (short single-level probes).

## Housekeeping

**Nothing in this folder is worth deleting.** The whole tree is ~375 MB, and every cell is
either live, load-bearing for a Plan.md section, or already archived. The large data does
not live here — plotfiles and checkpoints go to node-local scratch, which is where the
hundreds of GB are. Checkpoints are ~7.7 GB each.

Safe to delete *in the scratch tree*, with no loss of any extracted result:

| scratch cell | size | why it is safe |
| --- | --- | --- |
| `s20_boost_p02` | ~60 GB | 81 plotfiles; its frames and movies are already extracted here |
| `stage1_lapse5_sg00` | ~30 GB | 71 plotfiles from a superseded 2026-08-28 probe |

Before deleting anything: confirm nothing is running, and write a manifest of what went.

## Conventions

- **Never run the binary directly.** AMReX writes `parameters_and_version.txt` with absolute
  paths into the working directory; the launcher clones the params and `cd`s somewhere
  harmless. It also registers `launcher.pid` so the run can be stopped cleanly.
- **Name the frame fields at launch.** `WHM_CONSUME_ARGS` controls which fields become
  pictures; its default is empty, so a run launched without it renders nothing at all and
  writes no slice cache.
- **Ask the slice cache, not the tracker.** `frames/_slice_cache/` holds each 2-D slice as a
  small array. Throat positions are measured from those, sub-cell and smooth at 1e-4;
  `throat_track.dat` has a quantum of ~0.03 and exists only to aim refinement boxes.
- **Redraw before making movies.** Live frames are scaled per frame, so the colour bar moves.
  `scripts/plot/rerender_frames.py <run>/frames --movies` redraws the whole series against
  one fixed scale.

Per-run layout: `params.txt` (the exact input, paths rewritten), `run.log`, `data/` and
`small_data/` (the `.dat` streams), `frames/` (pictures plus `_slice_cache/`), `movies/`.
