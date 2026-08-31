# `runs/wormhole_merger`

Working output of the wormhole-merger campaign. Everything here was produced by
`scripts/campaigns/wormhole_merger/run_single.sh`, and the argument it all feeds is
[`research/merger/Plan.md`](../../research/merger/Plan.md) — that document is the
reasoning, this folder is the evidence. The light, git-committed extract of the
numbers is [`results/merger/`](../../results/merger/); rebuild it with
[`research/merger/pack_results.sh`](../../research/merger/pack_results.sh).

The campaign in one line: **put a real wormhole throat on the grid, prove one throat
holds still, prove a moving throat survives, then find out what two of them do to each
other.** Two identical throats repel; reversing the field direction of one is the only
gravity-driven route to a merger; and when they do merge, the thing that breaks is the
black hole they make.

## Layout

Grouped by campaign stage, so the folder reads in the order the work happened.

| folder | stage | what it asked | runs |
| --- | --- | --- | --- |
| [`00_archive/`](00_archive/NOTES.md) | pre-history | routes that were tried and abandoned | 3 groups |
| [`01_single_throat/`](01_single_throat/NOTES.md) | 1 | Does one throat just sit still? | 11 |
| [`02_moving_throat/`](02_moving_throat/NOTES.md) | 2.0 | Does a *moving* throat survive? | 1 |
| [`03_two_throats/`](03_two_throats/NOTES.md) | 2.5–2.6 | What do two throats do to each other? | 4 |
| `merge_*` at this level | 3 | What happens when they actually merge? | 9 |

Each stage folder has a `NOTES.md` with its runs, its parameters and its result. The
Stage 3 runs stay at the top level while the stage is live.

## Reading a run name

`merge_orbit_flip_d12_rw_r05000` = **merge** run, throats on an **orbit** (given
tangential momentum) rather than dropped head-on, one throat's scalar field **flipped**
in sign, started **d = 12** apart, using the **r**adius **w**indow damping, **r**estarted
from checkpoint **05000**.

| suffix | means |
| --- | --- |
| `_headon` / `_orbit` | zero tangential momentum / momentum ±0.12 in y |
| `_flip` | throat B's scalar field reversed — without this the throats repel and nothing merges |
| `_d12` | initial separation 12 (centres at x = ∓6) |
| `_rNNNNN` | restarted from `BinaryWormholeChkNNNNN` of the arm before it |
| `_pNNN` | tangential momentum NNN instead of 0.12 |
| `_nNNN` | NNN cells per side instead of 128 |
| `_mlN` | `max_level = N` instead of 3 |
| `_sgNN` | Kreiss–Oliger dissipation σ = N.N instead of 0.1 |
| `_rw` | the radius-window core damping |

Everything not named in the suffix is identical across the Stage 3 runs: two drainhole
throats, scale `a = 2`, ADM mass 1 each carried by the lapse, box `L = 64`, `N = 128`,
`max_level = 3`, Sommerfeld boundaries, σ = 0.1, run to `stop_time = 60`.

## The Stage 3 runs — what each one is, and what happened

The first five are one chain: each restarts from the previous one's checkpoint, changing
exactly one thing, hunting the same failure. The last four are independent probes.

| run | what is different | ran | what happened |
| --- | --- | --- | --- |
| `merge_orbit_flip_d12_r03000` | **the main arm** — no damping at all. Its `__part1` files are the original t = 0 → 30.5 episode; the restart carries t = 30 → 52 | t = 0 → **52.06** | The throats spiral in and **merge**: a common trapped region at t ≈ 30, and a real radiation burst. Then the phantom scalar sitting in the collapsed core blows up — NaN at t = 52.06. This is the run every later one is trying to save. |
| `merge_orbit_flip_d12_r05000` | first damping attempt: switch it on and take the built-in thresholds (lapse 1e-6 → 1e-8, about three cells wide) | t = 50 → **52.09** | Bought 0.02 units — nothing. The window was aimed so deep it never touched the matter that kills the run. **Its data was deleted before extraction; only the log survives** ([`LOST.md`](merge_orbit_flip_d12_r05000/LOST.md)). |
| `merge_orbit_flip_d12_r04000` | widen the window a thousandfold (lapse 3e-2 → 1e-3), and plot the full metric so the horizon can be measured offline | t = 40 → **52.86** | The core *was* cleaned — φ down to 1e-10 inside the window — and it still died. Reason: 1+log slicing makes the sickest cells re-inflate their own lapse, so they climb **out** of a window defined by lapse. |
| `merge_orbit_flip_d12_sg10_r05000` | same window, dissipation σ raised 0.1 → 1.0 | t = 50 → **51.68** | Backfired. Died *earlier* than the undamped arm: the dissipation attacks the puncture structure itself, the same way σ = 2.0 destroyed single throats in Stage 1. Arm abandoned. |
| `merge_orbit_flip_d12_rw_r05000` | anchor the damping in **radius** instead of lapse: full inside r = 0.5, off by r = 0.7, engaged only after t = 33 | t = 50 → **55.00** | The longest survivor, and the one that found the result. Its snapshots show the common horizon **shrinking** — 1.07 at t = 51.5 down to 0.59 at t = 55, accelerating — as the infalling phantom eats it. |
| `merge_headon_flip_d12` | no orbital momentum: the throats are dropped straight at each other | t = 0 → **44.00** | Merges much harder and sooner (common trapped region at t = 29), then dies the same death at t = 44. Old binary, no damping — awaits a rerun on the settled recipe. |
| `merge_orbit_flip_d12_p045` | momentum 0.45 instead of 0.12 — nearly four times the angular momentum | t = 0 → **60.01, finished clean** | **Never merges.** Closest approach 3.95 at t = 40, then the throats swing back out to 4.61 by t = 60. Nothing collapses, no NaN — the healthy control that shows the instability belongs to the merged core, not to the code. |
| `merge_orbit_flip_d12_n160` | 160 cells per side instead of 128 | t = 0 → running | The convergence check: does the merger era look the same on a finer grid? Still evolving as of 2026-08-31. |
| `merge_orbit_flip_d12_ml2` | one refinement level fewer (`max_level = 2`) | t = 0 → **9.42** | Dies almost immediately, long before the throats meet. Confirms for the binary what Stage 1 found for one throat: three levels is the floor, not a luxury. |

**The story in one paragraph.** When the throats *do* merge, a horizon forms at t ≈ 30
and the phantom scalar then destroys everything — first the runs (a NaN wherever
un-damped phantom sits on collapsed geometry, in four arms with four different
treatments), and then, as the radius-window arm measured, the horizon itself. When the
throats *don't* merge (`p045`, enough angular momentum), the evolution is healthy
indefinitely. The black hole, not the wormhole pair, is the fragile object here.

## Inside a run

```
<run>/params.txt              the exact input, paths rewritten by the launcher
<run>/launch_banner.txt       what the launcher resolved: template, binary, GPU, restart
<run>/run.log.gz              the evolution log -- gzipped once the run is finished
<run>/Backtrace.0             where it aborted, when it aborted
<run>/data/                   the .dat streams written every step by the evolution
<run>/small_data/             the psi4 streams written by the consumer sidecar
<run>/frames/<field>/frames/  per-field PNG frames
<run>/frames/_slice_cache/    the 2-D slice behind each frame, kept so movies can be
                              redrawn on one fixed colour scale
<run>/movies/                 the stitched .mp4s
```

`__part1` inside `merge_orbit_flip_d12_r03000` is the original pre-restart episode
(t = 0 → 30.5), filed under the run that continued it.

The four `data/` streams: `binary_throat_diagnostics.dat` (separation, per-throat
position, χ and lapse minima, the in-code Θ scan), `collapse_diagnostics.dat` (lapse, χ,
K and scalar-field extrema), `constraint_norms.dat` (Hamiltonian and momentum L2),
`throat_track.dat` (the tracker that aims the refinement boxes).

**Finished runs have gzipped logs.** Use `zgrep`/`zcat`, not `grep`/`cat`:
`zgrep -oE "TIME = [0-9.]+" <run>/run.log.gz | tail -1`.

## Reading the numbers without being fooled

- **The last row of a dead run is the death step.** It is already NaN-polluted — `max|K|`
  of 3648 and an L2 Hamiltonian of 4.4 in the `rw` arm are the blow-up, not physics. Quote
  the last clean row, half a unit earlier.
- **The separation can glitch to ~0 for one sample.** When the two throats swap sides,
  both finders can latch onto the same throat for a single row; `p045` shows 0.06 at
  t = 38.46 between neighbouring rows of 4.06. The true minimum there is 3.95 at t = 40,
  and both `binary_throat_diagnostics.dat` and `throat_track.dat` agree on it.
- **The in-code `ah_r_common` is a radial proxy, not a horizon finder.** It reports a
  growing "horizon" out to r = 6.2 in `p045`, a run with no collapse at all — a sphere
  large enough to enclose both deep lapse wells trips it. Trust it only where the offline
  scan (`grteclyn-wrapper/scripts/validation/ah_radial_scan.py`) confirms it, which needs
  the metric components in the plotfiles — only `r04000`, `rw` and `sg10` have them.
- **Ask the slice cache, not the tracker,** for throat positions: `frames/_slice_cache/`
  keeps each 2-D slice as a small array, good to 1e-4. `throat_track.dat` has a quantum
  of ~0.03 and exists only to aim refinement boxes.
- **Coordinates lag reality** for roughly the first five time units while the gauge
  settles. Nothing measured before then means what it appears to mean.

## Housekeeping

**The size is not here.** This tree is ~1.5 GB. Plotfiles and checkpoints go to
node-local scratch, which runs to tens of GB per live run — checkpoints alone are
~15 GB each, and nothing deletes them automatically. When reclaiming disk, look there.

**The Stage 1 deaths are results, not junk.** Eleven runs in `01_single_throat/` died
between t = 21 and t = 35. That ladder is how the campaign established the blow-up is
physical rather than numerical — moving the refinement boundary, changing the
dissipation, or removing the mesh entirely does not move it. Deleting them deletes the
evidence for four Plan.md sections.

**Extract before you delete.** `merge_orbit_flip_d12_r05000` is the cautionary tale: its
run directory went in a disk sweep before anything had been pulled out of it, and that
arm's time series no longer exist anywhere.

Cleanups are recorded in `MANIFEST_CLEANUP_*.md`. Before deleting anything: confirm
nothing is running, check the results were extracted, and write a manifest.

## Conventions that keep biting

- **Never run the binary directly.** AMReX writes `parameters_and_version.txt` with
  absolute paths into the working directory; the launcher clones the params and `cd`s
  somewhere harmless, and registers `launcher.pid` so the run can be stopped cleanly.
- **Name the frame fields at launch.** `WHM_CONSUME_ARGS` decides which fields become
  pictures. Its default is empty, so a run launched without it renders nothing at all
  and writes no slice cache — and by the time you notice, the plotfiles are gone.
- **Decide what to plot at launch too.** `amr.plot_vars` on the first five Stage 3 runs
  omits `h_ij` and `A_ij`, so the offline horizon finder can never be run on them. That
  is permanent: the plotfiles are consumed and deleted as the run goes.
- **Redraw before making movies.** Live frames are scaled per frame, so the colour bar
  moves. `scripts/plot/rerender_frames.py <run>/frames --movies` redraws the whole
  series against one fixed scale.
