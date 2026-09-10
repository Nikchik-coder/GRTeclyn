# `wormhole_merger/` — every figure and movie of the merger campaign

One package. Until 2026-09-10 this was two, `merger/` and `merger_ladder/`,
which were the same campaign under two names; they were merged and renamed to
match the campaign's other two directories, `runs/wormhole_merger/` and
`scripts/campaigns/wormhole_merger/`.

Every module runs the same way:

```bash
python -m grteclyn_wrapper.visualisation.wormhole_merger.<module> --help
```

and `python -m grteclyn_wrapper.visualisation.wormhole_merger` on its own lists
them.

## The scripts

| module | what it draws | reads | writes |
| --- | --- | --- | --- |
| `plot_psi4_modes` | one gravitational-wave mode of several runs overlaid at every extraction sphere, plus a table of every pairwise difference as a percentage of the peak | the run tree (or the thinned pack copy) | `results/merger/figures/` |
| `plot_ladder_psi4` | the refinement-ladder arms overlaid at one detector — do finer grids change the wave, or only how long the run survives | the pack | `results/merger/figures/05_binary_spiral/` |
| `plot_bbh_vs_wormhole_psi4` | same masses, same orbit, different object: the p = 0.12 wormhole pair against the vacuum black-hole control | the pack | `results/merger/figures/05_binary_spiral/` |
| `plot_bbh_ringdown` | the vacuum control's ringdown and its quasi-normal fit — the known answer every instrument is calibrated against | the pack | `results/merger/figures/07_bbh_control/` |
| `plot_merger_constraints` | how well the equations are actually satisfied through the merger, for the interior-freeze arms | the pack | `results/merger/figures/05_binary_spiral/` |
| `plot_branches` | **the lone throat's two fates across resolution** — level 3 collapses, level 4 inflates, at the same rate. Also writes the note `BRANCHES.md` that carries the tables | the pack | `campaign/01_single_throat/BRANCHES.md` + `figures/01_single_throat/single_throat_branches.png` |
| `plot_seed_branches` | **the same two fates chosen on purpose** — one resolution, one knob: the sign and size of a declared kick laid on the throat at t = 0 | the run tree, live runs included | `figures/01_single_throat/single_throat_seed_branches.png` |
| `stitch_movies` | several runs played as one movie per field on a single colour scale, for a run continued by restarts | each run's cached slices | the run tree (never `results/`) |
| `run_tree` | not a figure — the helper the others use to find a run **by name**, wherever it is filed | — | — |

## Two rules that keep biting

**Never hard-code a run's path.** Runs are refiled by question as the campaign
grows (`05_binary_spiral/p012/…`, `01_single_throat/hold/…`). `run_tree.find_run`
resolves a bare name wherever it sits, and every module here goes through it.

**Movies stay in the run tree.** `stitch_movies` writes into the run directory
and nothing copies its output into `results/` or into git.

## The two branch figures are a pair

`plot_branches` shows that the isolated throat's fate — collapse or inflation —
is decided by the truncation error's seed: change only the refinement level and
the sign of the outcome flips, at the same growth rate. That is a problem, not a
result: nobody chose that seed.

`plot_seed_branches` is the controlled version. The resolution is fixed and the
seed is declared: a Gaussian shell on the conformal factor at t = 0, amplitude ε,
with the velocity fields left at zero so the momentum constraint stays exact and
only the Hamiltonian is violated, at order ε. It draws two amplitudes a factor
ten apart (±0.01 and ±0.001) on one panel, and it is built to stop the two
mistakes this measurement invites:

- the arms first separate in the direction of their own kick, then come back,
  cross, and run apart the other way — **the first separation is the transient
  and the second is the branch**, so the crossing is marked with a dotted rule
  rather than hidden. Both pairs cross within 0.03 of each other, which is what
  says the crossing belongs to the throat's transient and not to the kick;
- near that crossing the deviation passes through zero and its logarithmic
  derivative is meaningless, so no rate is drawn on the figure at all. The
  sliding-window rate is printed to the console, and only from two windows past
  each arm's own crossing.

The figure carries no prose — no caption, no worded axis labels, no legend.
Identity is in the line itself: the dash pattern is the sign of the kick, the
weight is its size, and each arm is named in the right margin with a leader back
to its own end. Pale grey marks the part of a curve the ray scan can no longer
measure (its minimum has reached the scan's inner cutoff).
