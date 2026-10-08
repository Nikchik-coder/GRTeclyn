# Drainhole merger — packed campaign results

> Current state: [`research/merger/STATUS.md`](../../research/merger/STATUS.md). What each run
> actually ran (binary, seeds, name check): [`runs_index.tsv`](runs_index.tsv), generated;
> which binary is which: [`binaries.tsv`](binaries.tsv). Map: [`MAP.md`](../../MAP.md).

Two exotic-matter (phantom scalar) drainhole throats, given a gentle orbital push,
spiralling together in full 3+1 numerical relativity. This directory is the light
extract of that campaign: every number the analysis rests on, the movies, a thinned set
of stills, and enough provenance to rebuild any run. It is what survives if the machine
that produced it does not.

> **Data note (2026-10-06).** The pack now holds the production campaign only: constraint-solved
> (mode-3 `csm`) initial data, exact-boost momentum (`lbf`), plus its verification and
> convergence arms. The earlier superposed / Bowen-York campaign does not satisfy the
> Hamiltonian constraint; it left the paper on 2026-10-05 and left this pack on
> 2026-10-02 / 2026-10-06. Its run directories live untracked in `campaign/00_archive/`
> (pack extracts) and `runs/wormhole_merger/00_archive/` (raw), on the production machine
> only. The single-throat results stand as is: the isolated drainhole is an exact solution.
> `runs_registry.tsv` still registers every run ever launched; which packed run Table I of
> the paper counts, run by run, is `research/merger/article/claims/table1_groups.tsv`.

- The reasoning and the full argument: [`research/merger/Plan.md`](../../research/merger/Plan.md)
- The article in preparation: [`research/merger/article/research.tex`](../../research/merger/article/research.tex)
- The campaign's history and verdicts: [`research/merger/STATUS.md`](../../research/merger/STATUS.md)
- The working run tree, **not in git** (~14 GB, on the machine that produced it):
  `runs/wormhole_merger/`, filed by physics since 2026-09-10 into the same
  `NN_group/` folders as `campaign/` here; its README is the run inventory
- Rebuild this directory: `bash research/merger/pack_results.sh`

## Where everything is

- `campaign/<NN_group>/<run>/` — one directory per production run; Table I of the paper counts
  exactly these (per-run map: `research/merger/article/claims/table1_groups.tsv`).
  - `01_single_throat/` — the lone throat: `hold/` (levels, floors, Δt, box), `seed/` (declared
    kicks, quadrupoles, the scalar-stream re-runs), the generated notes (INSTABILITY, BRANCHES,
    QUEUE2E_GATES).
  - `02_moving_throat/` — the boosted throat: `contraction_t0/` (the 1/γ contraction at t = 0),
    `exact_boost/` (one exact-boost throat on the production box, and the MASS-t0 fly-by pairs at
    t = 0 whose ADM surface integrals measure the moving pairs' mass), `csm/` (the Bowen–York
    momentum probes that ruled that route out).
  - `03_two_throats/csm/` — the matched rest pairs: width and separation ladders, the sign rule, and
    SCATTER-fate (the d = 12 rest pair to t = 95: the mouths recede and both inflate).
  - `04_binary_headon/` — `csm/` (the mode-3 head-on legs), `placement_csm/` (the 18 one-step
    placement probes), `first_law/`, `mots/`, and the CS-1 solve scout.
  - `05_binary_spiral/` — `merger_d6/` (the d = 6 merger chain), `csm/` + `lbf/` (the d = 12
    arms), `verify_p012/`, `scout_merger/`, `horizon/` (the retracted scan record).
  - `06_binary_flyby/` — the fly-by and E_GW scan, p = 0.25–0.90, with `verify_p025/`.
  - `07_bbh_control/` — the vacuum BBH controls.
  - `08_convergence/` — the referee's convergence arms (no frames, no movies, by design — except
    CONV-fz, the head-on's three-level set lvl5 / FARZONE-ho / lvl7 on the L = 512 box, which keeps
    its frames on the user's word, 10-07; FARZONE-ho itself runs to t = 250 with spheres to R = 180).
  - `00_archive/` (untracked) — the superseded superposed / Bowen-York campaign; see the data
    note above.
- `figures/<group>/` (index: `figures/FIGURES.md`), `movies/<group>/`, `gw_search/` (the
  LIGO/LISA search JSONs), `analysis/` (stock-Python reductions), `t0_matching/`.
- One line per run: `runs_registry.tsv`. What each run actually ran: `runs_index.tsv`.
  Binary → commit: `binaries.tsv`. Last trustworthy time per run: `trust_windows.tsv`.
  Per-run summaries: `summary.md`, `summary.csv`.


## `figures/` — the paper's figures

`figures/<group>/` holds the article's figures and nothing else (the user's rule,
2026-09-26): every PNG/PDF pair there is included by `research/merger/article/research.tex`,
and [`figures/FIGURES.md`](figures/FIGURES.md) maps each file to its figure number, label and
the wrapper module that redraws it (one command each, no arguments). Every figure is drawn by
`grteclyn_wrapper.visualisation.wormhole_merger` in one house style; when a figure leaves the
paper its files are deleted and its script stays in the wrapper.

## Layout

The pack mirrors the run tree: one folder per physics group, the groups being
the sections of the paper, and inside a group one directory per run. A run that
is still on a card sits at the top of `campaign/` until close-out files it.

```
campaign/                         (as of 2026-10-06; the superposed-era subfolders gauge/,
                                  grid/, placement/, p012/, p012_ladder/, p012_freeze/ and
                                  their runs are in the untracked 00_archive/)
  01_single_throat/               one throat, filed by question:
    hold/<run>/                     the production hold single_hold_t100 and its one-knob
                                    twins (resolution, chi floor, time step, the L = 128
                                    box), and the half-mass lone throat single_m05_t040
    seed/<run>/                     the declared-kick scan, the +-0.01 pair at level 4, the
                                    quadrupolar kicks, the scalar-stream re-runs, the L = 512
                                    octant inflation arm
    INSTABILITY.md                  the isolated-throat systematics, generated
    QUEUE2E_GATES.md                the five gates of the wave from one throat, generated
    BRANCHES.md                     the level-3 / level-4 ladder read (two fates), generated
    CLOCK_COMPARISON.md             the throat clocks across arms, generated
    NOTES.md                        the Stage-1 working notes, copied from the run tree
  02_moving_throat/               the boosted throat:
    contraction_t0/<run>/           the 1/γ Lorentz contraction at t = 0, p = 0 -> 0.45
    exact_boost/<run>/              the moving exact-boost throat (the collapse twins, levels
                                    3/4) and its t = 0 solve check on the production box;
                                    the MASS-t0 pairs (p = 0.25 / 0.45 / 0.60 at t = 0: ADM
                                    energy 2.304 / 2.317 / 2.282, flat in p)
    csm/<run>/                      the Bowen-York momentum probes (2026-09-29) that ruled
                                    that route out: one throat at p = 0, 0.12, 0.45
    boost_contraction_t0.tsv        the measured contraction against 1/γ, reduced
  03_two_throats/
    csm/<run>/                      the matched rest pairs: width rungs a = 1/1.5/2/3,
                                    separation rungs d = 12/14/16/18, the flip control,
                                    SCATTER-fate (d = 12 to t = 95: both mouths inflate)
    matched_rest_displacement.dat   the width/separation ladder, reduced
    sign_rule_displacement.dat      the sign rule (pull/push), reduced
  04_binary_headon/
    csm/<run>/                      the mode-3 head-on legs to t = 100
    placement_csm/<run>/            the eighteen one-step placement probes (d = 6 -> 75)
    first_law/, mots/               the first-law window and the MOTS replay legs
    merge_headon_flip_d8_cs_lvl3_t030/  CS-1, the in-code constraint-solve scout
  05_binary_spiral/
    merger_d6/<run>/                the d = 6 merger chain (p = 0.10 tangential) and its
                                    level / sigma / chi-floor / settle legs
    csm/, lbf/<run>/                the d = 12 arms on solved data (tangential and inward)
    verify_p012/, scout_merger/     solve verifications and the merger scout
    horizon/                        the offline Theta = 0 scans: the naive-orientation
                                    "dissolution" record (retracted) and the oriented
                                    rescan that overturned it (ORIENTED_RESCAN_2026-09-08.md)
  06_binary_flyby/<run>/          the fly-by and E_GW scan: p = 0.25 (level 5), 0.45 (t = 100,
                                  the no-damp twin), 0.60 (plunge series + extensions), 0.90;
                                  verify_p025/ holds the t = 0 and t = 20 solve checks
  07_bbh_control/<run>/           the vacuum binary-black-hole controls: same d and p, no
                                  scalar, no sponge (d = 12 p = 0.12/0.45, d = 6, head-on)
  08_convergence/<run>/           the convergence study for the referee: each arm is its
                                  partner's params with one knob changed (max_level from 0,
                                  the wave zone's level, the dissipation); no movies, no
                                  frames kept (the user's word) -- except CONV-fz, which
                                  keeps them (the user, 10-07)
  00_archive/                     UNTRACKED: the superseded superposed / Bowen-York campaign
                                  (pack extracts, moved 2026-10-02 / 2026-10-06)
  <group>/NOTES.md                the group's working notes, copied from the run tree

campaign/<group>/<run>/           what every run directory holds
  collapse_diagnostics.dat        lapse, chi, K and scalar-field extrema
  constraint_norms.dat            Hamiltonian and momentum L2
  binary_throat_diagnostics.dat   separation, per-throat position and minima,
                                  the in-code Theta scan
  throat_track.dat                the tracker that aims the refinement boxes
  psi4_*.dat, Weyl4_*.dat         the extracted waveform (consumer; in-code where on)
  areal_radius.dat, horizon_*.dat the throat radius and the horizon scans, where on
  evolution_params.txt            the exact input the run was given
  launch_banner.txt               what the launcher resolved: template, binary,
                                  GPU, restart checkpoint, consumer arguments
  run_tail.log, backtrace.txt     the last 200 log lines and where it aborted
  (movies are no longer kept per run: the sets worth keeping are filed
   together under results/merger/movies/, see its README)
  frames/                         thinned stills, where the pictures carry a result
  part1/, *__part1*.dat           the pre-restart episode of the same run

figures/<group>/                  the paper's figures (index: figures/FIGURES.md)
runs_registry.tsv                 ONE line per run: what is different, caveat, stopped
                                  note -- the only place a run is registered (the
                                  launcher appends it when WHM_WHAT is set)
analysis/pack_paths.py            how every script here finds a run by name, wherever filed
analysis/make_summary.py          builds the two summary tables, one block per group
analysis/*.py                     the REDUCTIONS: they write the generated notes above
                                  (INSTABILITY.md, BRANCHES.md, QUEUE2E_GATES.md) and the
                                  small .dat tables a figure needs, from the packed
                                  streams alone, with a stock Python.  The FIGURES all
                                  live in grteclyn_wrapper.visualisation.wormhole_merger
summary.md, summary.csv           one row per run (csv: plus a `group` column), generated
```

The four evolution streams are written every step (dt = 0.01) and thinned here to
dt = 0.05 — **except the last time unit of each run, kept at full cadence**, because that
is where a dying run does everything interesting. The `psi4` streams are one row per
plotfile and are packed whole.

Not packed, and not recoverable from here: plotfiles, checkpoints, the full frame series
(~250 per field) and the slice caches (7–620 MB per run). Those live in the run tree —
and, since 2026-09-10, only on the runs whose pictures matter (the run tree's README
says which).

## Reading these files without being fooled

- **The last row of a dead run is the crash, not the spacetime.** A huge `max|K|` or
  constraint norm on the final row is the NaN arriving. `summary.md` quotes the row
  half a unit earlier for exactly this reason; do the same.
- **Separation can glitch to ~0 for a single row** when both trackers latch onto the
  same throat as the pair swaps sides. `make_summary.py` drops rows that disagree with
  both neighbours by more than half; read the stream the same way.
- **Horizon numbers come from the spectral MOTS finder** (`small_data/mots_spectral.dat`,
  written on every plotfile of every binary profile), never from the in-code θ/AH scan
  in `binary_throat_diagnostics.dat` or the round/oriented sphere scans: a scan sphere
  under-reads a deformed horizon by 3–11 %, and on a binary it is only an inner bound
  and a live monitor. A `nan` row means no MOTS on that plotfile, not a failure.
- **Movies and figures stop at the run's trust window** (`trust_windows.tsv`): frames
  past it exist on disk but show a solution past a wall reflection, a blow-up or lost
  resolution, and nothing after it is quoted.
- **Waveforms across a restart.** The interior of a restart restores exactly; the outer
  boundary does not, and the error walks inward at roughly the speed of light. Do not
  read `psi4` at large R across a restart boundary without allowing for it.
- **The first ~5 time units are gauge settling.** Nothing measured there means what it
  appears to mean.
