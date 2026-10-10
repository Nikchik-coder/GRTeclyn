# Running the spinning-wormhole campaign

Everything in this folder launches, watches, or protects one run of
`Examples/SpinningWormhole` (a single spinning Ellis–Bronnikov wormhole,
evolved from a background table).  The working output lands in
`runs/spinning_wormhole/` (gitignored); the committed records are
`results/spinningwormhole/binaries.tsv` and
`results/spinningwormhole/runs_registry.tsv`.

The folder is the merger campaign's proven recipe
(`../wormhole_merger/`, read-only: that campaign is live) with this
campaign's identity: env vars `SWH_*`, log tag `[swh]`, run root
`runs/spinning_wormhole/` (templates in `templates/`, frozen binaries in
`bin/`, logs in `logs/`), plotfile/checkpoint prefixes
`SpinningWormholePlt` / `SpinningWormholeChk`.

## The pipeline

```
launch.sh  ->  run_single.sh  ->  preflight (shared engine)  ->  evolution + consumer sidecar
```

| file | what it does |
| --- | --- |
| `launch.sh` | The launcher.  Resolves the template, the binary, the restart suffix, the consumer flags and the registry line, then hands off.  `--template/--name/--gpu/--profile` are required. |
| `run_single.sh` | The engine: clones the params, rewrites output paths onto node-local scratch, runs the preflight, starts the binary and the consumer sidecar, registers `launcher.pid`, drains the consumer at the end.  Never call the binary yourself. |
| `preflight_campaign.json` | This campaign's facts for the SHARED preflight engine (`../lib/preflight.py`, one engine for every campaign since 2026-10-10): the seed key (`spinning_seed_amplitude`), the run root, the mirror rules (reflective x or y boundaries are refused -- rotation about z breaks those mirrors; a z mirror is allowed), and the required background table (`spinning_background_file` must exist as a file). |
| `preflight_allow.txt` | Keys the preflight may see unread without refusing.  Carried over from the merger's generic entries only; re-audit it against the SpinningWormhole binary at its first build. |
| `frames_default.txt` | The mandatory frame set, identical to the merger's.  A launch that renders less is refused unless `SWH_FRAMES_SUBSET="<reason>"` says why. |
| `lib/consumer_profiles.sh` | What the consumer extracts, under a name: `hold` (full frames + spectral MOTS) and `none`. |
| `run_manifest.py` | Writes `run_manifest.json` at launch and completes it at exit; `backfill` reconstructs one for an older run. |
| `build_binary.sh` | Builds `main3d_<tag>_<commit>_<date>.ex` into `runs/spinning_wormhole/bin/` from a clean tree (`EBASE=pin`, own object dir), stamped with its commit, and appends its row to `results/spinningwormhole/binaries.tsv`. |
| `keep_checkpoints.sh`, `keep_plotfiles.sh`, `prune_checkpoints.sh` | Copy checkpoints out of a rolling run, hard-link plotfiles past `--keep-last`, prune scratch per policy (`MAIN_RE` is empty: no insured run yet). |
| `restart_consumer.sh` | Change a LIVE run's consumer flags without touching the evolution (`--check` first). |
| `tidy_logs.sh` | Reduce a finished run's launcher log to its `[swh]` provenance banner. |
| `lib/run_tree.sh` | How every script here finds a run by name, wherever it is filed. |

## How this differs from wormhole_merger

- **One wormhole, not two**: no throat-pair keys, no bare-mass/sigma/lapse/
  tagging name-suffix knobs in `run_single.sh` (only `SWH_MAX_LEVEL` and the
  `_r<step>` restart suffix remain).
- **Background-table initial data**: every template must set
  `spinning_background_file`; the preflight refuses a missing key or a path
  that is not a file.
- **No pinned binary yet**: `launch.sh`'s `DEFAULT_BINARY` is empty, so every
  launch (except a restart with a parent manifest) must say
  `--binary runs/spinning_wormhole/bin/<build>.ex`.  Pin one once the campaign
  settles on a build.
- **Shared preflight**: the checks run from `../lib/preflight.py` with
  `--campaign-config preflight_campaign.json`; there is no preflight fork in
  this folder.

## SWH_ environment variables

`run_single.sh` reads (launch.sh sets most of them): `SWH_PARAMS`, `SWH_NAME`,
`SWH_GPU`, `SWH_RANKS`, `SWH_RUNS_DIR`, `SWH_EXE`, `SWH_MAX_LEVEL`,
`SWH_RESTART`, `SWH_DRYRUN`, `SWH_CONSUME`, `SWH_CONSUME_ARGS`,
`SWH_KEEP_PLOTFILES`, `SWH_KEEP_LAST`, `SWH_WHAT`, `SWH_REGISTRY`,
`SWH_FRAMES_FIELDS`, `SWH_FRAMES_SUBSET`, `SWH_PROC_LABEL`, `SWH_PROC_ALIAS`,
`SWH_PROC_BIN_DIR`, `SWH_PREFLIGHT`, `SWH_PREFLIGHT_ONLY`.
`SWH_BUILD_FLAGS` overrides `build_binary.sh`'s make flags.

## Building the binary

```bash
bash grteclyn-wrapper/scripts/campaigns/spinning_wormhole/build_binary.sh --tag spin
```

Needs a clean `Source/ Examples/SpinningWormhole Tools/GNUMake` tree (or
`--allow-dirty`).  The build deletes `Main_SpinningWormhole.o` first so the
version stamp is always rebuilt, lands in `runs/spinning_wormhole/bin/`, and
appends to `results/spinningwormhole/binaries.tsv` (commit that row).

## A worked launch

```bash
bash grteclyn-wrapper/scripts/campaigns/spinning_wormhole/launch.sh \
    --template params_equilibrium_L128_t200.txt \
    --name swh_equilibrium_L128_t200 \
    --gpu 0 --profile hold --zoom 32 --keep-last 3 \
    --binary runs/spinning_wormhole/bin/main3d_spin_<commit>_<date>.ex \
    < /dev/null > /tmp/launch_swh.log 2>&1
```

Use `--dry-run` first (resolves everything, runs the no-GPU half of the
preflight), and `--preflight-only` to run the full preflight on the card in
seconds without launching.

## Standing rules that carry over from the merger campaign

- **The full frame set is mandatory, every launch** (`frames_default.txt`).
  The preflight refuses a subset without `SWH_FRAMES_SUBSET="<reason>"`, and
  renders every field from the t = 0 plotfile before anything starts.
  Eyeball frame 0 either way: renderers fail silently.
- **Checkpoints are off by default** and are asked about per run; the
  preflight refuses checkpoints requested with
  `amr.checkpoint_files_output = 0`.
- **`launch.sh` detaches and hangs an agent's shell tool**: redirect its
  output to a file (`< /dev/null > log 2>&1`) and poll.  An interrupted or
  rejected launch may still have started -- check `nvidia-smi` / `ps` after.
- **GPUs are shared**: check `nvidia-smi` before every launch.  Processes are
  camouflaged (`test params.txt`, `test_post post.py ...`, label `--label`).
- **The consumer is part of the start**: `consumer.log` advances, frame 0
  renders, the first rows land in `small_data/`, keep-last pruning runs.  A
  dead consumer is silent while scratch fills.  Fix a live run's consumer only
  via `restart_consumer.sh` (`--check` first).
- **Never delete frames** (`frames/`, `_slice_cache`, `movies/`): no prune or
  close-out covers them.
- Stop a run with `../stop_campaign.sh <run dir>` (its `launcher.pid`), never
  a pkill pattern.
