# Running the drainhole-merger campaign

Everything in this folder launches, watches, or protects one run of
`Examples/BinaryWormholeMerger`. The reasoning the runs serve is
[`research/merger/GPU_PLAN.md`](../../../../research/merger/GPU_PLAN.md); the
working output lands in `runs/wormhole_merger/` (gitignored) and the committed
extract is [`results/merger/`](../../../../results/merger/).

Before 2026-09-10 each arm had its own `launch_*.sh` in the runs directory —
thirty of them, all the same eight steps with four values changed. They are
archived in `runs/wormhole_merger/00_archive/launch_scripts_2026-09-10.tar.gz`
and replaced by one launcher plus named consumer profiles. **A new arm is a
template, a name, a card and a profile. It is not a new script.**

## The pieces

| file | what it does |
| --- | --- |
| `launch.sh` | The launcher. Resolves the template, the binary, the restart suffix, the consumer flags and the registry line, then hands off. |
| `lib/consumer_profiles.sh` | What the consumer extracts, under a name. Data, not code. |
| `run_single.sh` | The engine: clones the params, rewrites output paths onto node-local scratch, starts the binary and the consumer sidecar, registers `launcher.pid`. Called by `launch.sh`; do not call the binary yourself. |
| `run_spiral.sh` | Thin front-end that sets the orbit defaults and delegates to `run_single.sh`. |
| `phase1_initial_data.sh` | The t = 0 GO/NO-GO gate. Every run in it sets `max_steps = 0`; the measurement is the initial data. |
| `keep_checkpoints.sh` | Copies named checkpoints out of a rolling run before it deletes them. |
| `prune_checkpoints.sh` | Drops restart checkpoints from scratch, per-run policy. |
| `tidy_logs.sh` | Reduces a finished run's launcher log to the provenance banner. |
| `file_run.sh` | Files a closed-out run into its physics group (`--group 04_binary_headon`), repairing the stitched-movie symlinks that point into it. |
| `lib/run_tree.sh` | How every script here finds a run by name, wherever it is filed. The Python side is `grteclyn_wrapper.visualisation.merger.run_tree`; the pack's is `results/merger/analysis/pack_paths.py`. |

## Launching a run

```bash
bash grteclyn-wrapper/scripts/campaigns/wormhole_merger/launch.sh \
    --template params_v1_lvl3down_d8_t100.txt \
    --name merge_headon_flip_d8_v1_lvl3down_t100 \
    --gpu 0 --profile headon --zoom 40 --keep-last 3 \
    --restart /tmp/grteclyn_scratch/_keep_lvl5/BinaryWormholeChk03500
```

That is the whole interface. `--dry-run` resolves everything and touches
nothing — use it every time before a real launch, because it prints the run
directory, the binary and the registry line it is about to commit to.

Templates resolve against `runs/wormhole_merger/templates_scan/` by bare name,
or you can pass a path (the vacuum BBH control's params live under
`Examples/BinaryBH/`). Templates stay in the runs tree on purpose: they carry
absolute output paths, which is machine identity, and the runs tree is
gitignored.

**Every template's first line is a comment saying what the run is for.** The
launcher reads that line into `results/merger/runs_registry.tsv`, which is what
the packed summary table shows. A template without that line produces a run
nobody can identify later.

With `--restart`, `run_single.sh` appends `_r<step>` to the name, so
`--name merge_..._t100` restarted from `Chk03500` becomes
`merge_..._t100_r03500`. The launcher accounts for this when it builds paths
that must point *into* the run directory, which is a thing that used to be got
wrong by hand.

Runs detach by default and survive the shell; `--foreground` attaches, which is
for probes only. Detaching a real run needs the user's word first.

## Consumer profiles

`--profile` names what the consumer should extract. The flags live in
`lib/consumer_profiles.sh`; `--zoom` and `--coord` stay separate because they
are per-run geometry, not per-question.

| profile | for | fields and diagnostics |
| --- | --- | --- |
| `headon` | the Phase-3 head-on arms | psi4 at R = 10/14/18, common horizon on level 3, six fields |
| `headon-scout` | first look at a new head-on setup | horizon tracking, no wave extraction, five fields |
| `orbit` | inspiral twins, capture scan | twelve fields including the matter diagnostics |
| `orbit-modes` | production orbit arms | `orbit` plus the scalar-mode decomposition |
| `bbh` | the vacuum control | seven fields, no matter |
| `chi` | cheap probes and ladders | one field, one question |
| `none` | one-step probes | no consumer at all |

Three rules learned the expensive way, all now built into the profiles:

- **Several fields, every launch.** A chi-only launch on 2026-09-08 lost the
  collapse and inflation movies and could not be re-rendered.
- **The slice plane is not optional.** The consumer's default slice coordinate
  is 0, the domain boundary, thirty units from the physics. Nothing errors; you
  get featureless far-field frames.
- **Cache the slices and let the colours float.** The live watcher locks the
  colour scale on the first plotfile, which under-ranges anything that grows.
  Only a cached slice can be re-scaled over the finished run.

If a one-off needs something no profile covers, `--consume-args` replaces the
profile string wholesale. Reach for it twice and add a profile instead.

## While it runs

Checkpoints roll: `checkpoint_keep = 1` means each new checkpoint deletes the
last. Any arm that will be branched needs its seed copied out **while the run
continues**:

```bash
bash .../keep_checkpoints.sh --run merge_headon_flip_d8_v1_lvl5chk_t100_r02200 \
     --dest /tmp/grteclyn_scratch/_keep_lvl5 --steps "03000 03500 04000"
```

Start it only after `run.log` shows `Level 0 step` advancing. Its "is the run
gone?" test is "no process and no checkpoint line", both true in the seconds
before the binary comes up, so a keeper started too early gives up on
everything and says so quietly. A destination under `_keep_*` is the signal to
every pruner that those checkpoints are not disposable.

Scratch fills fast. Check `du -sh /tmp/grteclyn_scratch` at launch and at
close-out; a consumer that has died stops pruning plotfiles and nothing says so.

## Stopping a run

Kill the orchestrator first, using the run's own `launcher.pid`, then sweep
whatever it started, then verify with `pgrep`. Killing workers alone just
advances the queue. Never use a `pkill -f` pattern: other people's runs share
these cards, and a loose pattern also matches your own shell.

## After it finishes

1. `bash research/merger/closeout.sh <run>` — NaN check, scratch report, movies, pack rebuild.
2. `bash .../tidy_logs.sh --apply` — the launcher log is a second copy of
   `run.log` plus about sixteen lines of provenance; this keeps the provenance
   as `<run>/launch_banner.txt` and drops the duplicate. On 2026-09-10 the
   backlog was 343 MB.
3. `bash .../file_run.sh --group <NN_group> <run>` — a run lives at the top of
   `runs/wormhole_merger/` while it is on a card and is filed with its question
   once it is done: `01_single_throat`, `03_two_throats`, `04_binary_headon`,
   `05_binary_spiral`, `06_binary_flyby`, `07_bbh_control`. Then
   `bash research/merger/pack_results.sh` again, so the pack mirrors the move
   (or `git mv` the packed directory by hand). The groups are the paper's
   sections; the run tree's README describes each.
4. Write the claim line in `results/merger/README.md` and the status row in
   `research/merger/GPU_PLAN.md`.
5. Prune scratch only on the user's word, and log every deletion in
   `runs/wormhole_merger/MANIFEST_CLEANUP_*.md` (append with `cat >>`).
   Frames and the slice cache are kept only on the runs whose pictures carry a
   result (the user's rule, 2026-09-10); the run tree's README says which.

## Where the old scripts went

Each archived `launch_*.sh` maps to one `launch.sh` command. The profile column
is what that script's hand-written consumer string became.

| old script | profile | notes |
| --- | --- | --- |
| `launch_v1_arm.sh`, `launch_v1_freeze.sh` | `headon --zoom 40` | the Phase-3 head-on arms |
| `launch_v1_gauge.sh` | `headon --zoom 40 --restart …` | never launched |
| `launch_v1_scout.sh` | `headon-scout --zoom 24` | |
| `launch_twin_p012.sh`, `launch_cred_twin.sh`, `launch_helfer_w2.sh` | `orbit` | the Helfer/plain twins |
| `launch_capture_scan.sh`, `launch_p015_*.sh`, `launch_p020_*.sh` | `orbit` | the capture ladder |
| `launch_lvl5.sh`, `launch_floor_ladder.sh`, `launch_nodamp_cf10.sh` | `orbit` (`--max-level`, `--restart`) | refinement and floor rungs |
| `launch_production_L128.sh` | `orbit-modes` | |
| `launch_bbh_control.sh`, `launch_bbh_control_t150.sh` | `bbh` | template is a path under `Examples/BinaryBH/` |
| `launch_chireg.sh`, `launch_ladder.sh`, `launch_single_hold.sh` | `chi --zoom 12` | |
| `launch_apoint.sh`, `launch_dpoint.sh` | `chi --zoom 32` | |
| `launch_autopsy.sh` | `chi --zoom 12` | `chi` also records areal radius, which the original did not |
| `launch_smoke_L128.sh` | `headon --coord 64 --zoom 64` | or `--consume-args` for the original's exact set |
| `launch_p045_helfer.sh` | `--consume-args` | its chi/lapse/phi set has no profile |
| `launch_placement_probes.sh` | `none --foreground` | loop over separations in the caller |
| `keep_v1c_checkpoints.sh`, `keep_lvl5_checkpoints.sh` | — | now `keep_checkpoints.sh --run … --dest … --steps …` |
