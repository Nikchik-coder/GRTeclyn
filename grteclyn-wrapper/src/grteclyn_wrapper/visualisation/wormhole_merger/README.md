# `wormhole_merger/` — every figure and movie of the merger campaign

One package. Until 2026-09-10 this was two, `merger/` and `merger_ladder/`,
which were the same campaign under two names; they were merged and renamed to
match the campaign's other two directories, `runs/wormhole_merger/` and
`scripts/campaigns/wormhole_merger/`.

Every module runs the same way:

```bash
PYTHONPATH=grteclyn-wrapper/src .venv/bin/python \
    -m grteclyn_wrapper.visualisation.wormhole_merger.<module> --help
```

and `python -m grteclyn_wrapper.visualisation.wormhole_merger` on its own lists
them.

## The scripts

| module | what it draws | reads | writes |
| --- | --- | --- | --- |
| `plot_psi4_modes` | one gravitational-wave mode of several runs overlaid at every extraction sphere, plus a table of every pairwise difference as a percentage of the peak | the run tree, or the thinned pack copy | `figures/04_binary_headon/` |
| `plot_psi4_analysis` | **the six-panel analysis of one arm**: waveform, retarded time and the ringdown fit, power spectrum, propagation speed, spectrogram, strain against Advanced LIGO | the pack | `figures/<group>/psi4_analysis_*` |
| `plot_ladder_psi4` | one panel: the refinement-ladder arms and the freeze arms at one detector — do finer grids change the wave, or only how long the run survives | either tree | `figures/05_binary_spiral/` |
| `plot_bbh_vs_wormhole_psi4` | same masses, same orbit, different object: the p = 0.12 wormhole pair against the vacuum black-hole control | the pack | `figures/05_binary_spiral/` |
| `plot_bbh_ringdown` | the vacuum control's ringdown and its quasi-normal fit — the known answer every instrument is calibrated against | the pack | `figures/07_bbh_control/` |
| `plot_merger_constraints` | how well the equations are actually satisfied, stitched across a restart chain | the pack | wherever `--out` says |
| `plot_separation` | one binary arm's separation and throat monitors: does it merge, or fly by | the pack | `figures/06_binary_flyby/` |
| `plot_placement_curve` | what two throats read simply by being placed near each other, and the throats' own response once that is subtracted | the two tables `analysis/placement_curve.py` writes | `figures/04_binary_headon/` |
| `plot_branches` | **the lone throat's two fates across resolution** — level 3 collapses, level 4 inflates, at the same rate. Also writes the note `BRANCHES.md` | the pack | `BRANCHES.md` + `figures/01_single_throat/` |
| `plot_seed_branches` | **the same two fates chosen on purpose** — one resolution, one knob: the sign and size of a declared kick laid on the throat at t = 0 | the run tree, live runs included | `figures/01_single_throat/` |
| `stitch_movies` | several runs played as one movie per field on a single colour scale | each run's cached slices | the run tree (never `results/`) |
| `style` | not a figure — the palette, the typography and `save()` | — | — |
| `streams` | not a figure — one loader per data-file shape | — | — |
| `run_tree` | not a figure — find a run **by name**, in either tree | — | — |

## The house style

`style.py` holds it; nothing else picks a colour. It follows the campaign's
plotting rules: **line plots are told apart by dash pattern first and colour
second**, so a figure survives a greyscale printer and a colour-blind reader.

```python
from grteclyn_wrapper.visualisation.wormhole_merger import style

style.paper()                       # once, before any figure is created
ax.plot(t, y, **style.series(0))    # ink, solid      — the subject
ax.plot(t, z, **style.series(1))    # deep blue, dashed — what it is compared with
style.save(fig, out)                # PNG + PDF, same stem
```

| helper | for | what it gives |
| --- | --- | --- |
| `series(i)` | an **unordered** family (this run against that one) | four fixed slots — ink, deep blue, burgundy, warm grey — each with its own dash. It raises on a fifth rather than inventing a hue. |
| `ordinal(n)` / `ordinal_series(n)` | an **ordered** family (refinement levels, extraction radii, kick amplitudes) | `cividis` reversed, light → dark, cut before the pale end so the lightest line still clears 4.2:1 on white. `dash_offset` starts the dash cycle further along, which is how a figure draws an ordered family and a categorical curve on the same axes without the two reading as one |
| `family(n)` | either | the fixed slots up to four, the ramp beyond |
| `signed(label)` | a signed quantity (the declared kick) | deep blue for negative, burgundy for positive, shade by magnitude |
| `SEQUENTIAL` | 2D magnitude | `cividis` (`SEQUENTIAL_HOT` = `inferno` when the top end needs contrast) |
| `DIVERGING` | 2D data centred on zero | `RdBu_r` — two hues, neutral midpoint, never a rainbow |

The four categorical slots were checked, not eyeballed: worst pair 21.7 OKLab
ΔE under normal vision and 13.4 under simulated protanopia, against thresholds
of 15 and 8. Both signed pairs clear the same bars.

**Axis labels are symbols.** `$d$`, `$R_{\mathrm{min}}$`, `$t - R_{\mathrm{ext}}$`
— never a sentence. What the symbol means goes in the panel title, once.

## Nothing is placed by hand

A figure is only as good as the least legible thing on it, and the thing that
goes illegible first is a key or a value label dropped on top of a curve. No
module calls `ax.legend` or `ax.annotate` any more:

| helper | what it does |
| --- | --- |
| `style.legend(ax, …)` | tries each corner, measures what is drawn there **and what text is already placed there**, and takes the emptiest; if every corner is occupied it extends the axis to open room rather than covering a curve |
| `style.callout(ax, x, y, text, above=…)` | a value label on an opaque patch, leaning *away* from its own curve — above a maximum, below a minimum — and flipped to the other side rather than pushed out of the frame |
| `style.note(ax, text, loc=…)` | the one-line caption inside a panel, on an opaque patch, anchored to the frame so it cannot run off the edge |

Two of the three exist because of specific bugs: labels keyed off the sign of
the *value* instead of the type of the extremum lay across every swing they
named, and a caption centred on the band it described was wider than the band
and ran off the panel.

## Four rules that keep biting

**Never hard-code a run's path.** Runs are refiled by question as the campaign
grows (`05_binary_spiral/p012/…`, `01_single_throat/hold/…`). `find_run` and
`find_packed` resolve a bare name wherever it sits. Two of these modules were
silently broken for a day because they reached for `campaign/<run>/` directly.

**Never read a column by its index.** `streams.py` reads the header. The
ringdown figure was pointing at column 7 of a file that had been repacked in a
different shape.

**Never a second y-axis.** Two quantities of different scale go in two stacked
panels sharing the time axis. On a twin axis the crossing point of the two
curves reads as an event, and it is an artefact of where the axes were put.

**Movies stay in the run tree.** `stitch_movies` writes into the run directory
and nothing copies its output into `results/` or into git.

## Where the reductions live

Three scripts under `results/merger/analysis/` do reductions and write the
generated notes (`INSTABILITY.md`, `PLACEMENT_CURVE.md`, `CLOCK_COMPARISON.md`,
`summary.md`). They stay there and stay figure-free, because a copy of the pack
has to be runnable with nothing but a stock Python. Where a figure needs their
numbers, they write a small table beside the note and the figure module reads
it — that is how `plot_placement_curve` gets its curve.

## The two branch figures are a pair

`plot_branches` shows that the isolated throat's fate — collapse or inflation —
is decided by the truncation error's seed: change only the refinement level and
the sign of the outcome flips, at the same growth rate. That is a problem, not a
result: nobody chose that seed. Two panels: the radius, and its logarithmic
deviation with each arm's fitted rate written into the key rather than beside
the line it measures. It had a third panel of shell profiles whose own key
covered its curves; the scans are a table in `BRANCHES.md`, which is where a
reader can actually use them.

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
Identity is in the line itself: the colour and the dash pattern are the sign of
the kick, the weight is its size, and each arm is named in the right margin
with a leader back to its own end. Pale grey marks the part of a curve the ray
scan can no longer measure (its minimum has reached the scan's inner cutoff).
