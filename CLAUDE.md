# Working in this repository

Read [`MAP.md`](MAP.md) (what is where) and, for the merger campaign,
[`research/merger/STATUS.md`](research/merger/STATUS.md) (what is live) first.
Every rule below exists because breaking it cost a run, a result or a day.

## Environment

- **LaTeX: the workstation only.** It has TeX Live (`latexmk`, `lualatex`, `pdflatex`);
  the GPU nodes have none. The editor rebuilds the article with `latexmk -lualatex` on
  save, so build test copies with `-outdir` elsewhere, and check that both engines build.
- **Python** is the wrapper's venv: `grteclyn-wrapper/.venv/bin/python` (setup:
  `cd grteclyn-wrapper && uv sync --extra plots --extra visualization --extra gw-search`). System `python3` and the root
  `.venv` do not have `grteclyn_wrapper` installed.
- **Building**: use `grteclyn-wrapper/scripts/campaigns/wormhole_merger/build_binary.sh`.
  By hand you need `/usr/local/cuda/bin` on PATH (it is not by default), the
  campaign OpenMPI on PATH, and the *system* g++ 11 — `scripts/lib/env.sh` puts the
  GRTresna conda env (g++ 15, rejected by nvcc) first unless `GRTRESNA_ENV=""`.
- **GPUs are shared** with other people's jobs: check `nvidia-smi` before every
  launch. Campaign processes are renamed: `test params.txt` (evolution),
  `test_post post.py` (consumer), `test_pre pre.py` (launch checks), `test_job run_single.sh`.

## Launching runs

- Only through `launch.sh`, never the binary directly (AMReX writes
  `parameters_and_version.txt`, with absolute paths, into the working directory).
- `launch.sh` detaches and **hangs the agent's shell tool**: redirect its output to a
  file (`< /dev/null > log 2>&1`) and poll. An interrupted or rejected launch may
  still have started — check `nvidia-smi` / `ps` afterwards.
- **Preflight** (automatic, `run_single.sh`): refuses keys the binary does not read,
  contradictory settings (checkpoints asked for with `amr.checkpoint_files_output = 0`),
  and seeds that do not change the t = 0 data. Ask first with `--preflight-only`.
  `WHM_PREFLIGHT=off` exists; it is recorded in the run's manifest.
- **Frames: the full default set is mandatory** (`frames_default.txt`, every profile):
  preflight refuses a subset without `WHM_FRAMES_SUBSET="<reason>"` and renders each field from t = 0.
- The campaign pin (`launch.sh` DEFAULT_BINARY) is `main3d_guard_7166787a_2026-09-24.ex`
  since 2026-09-24: it reads the quadrupole seed and the core profile, which the old pin
  `main3d_boost_2026-09-08.ex` ignored. A `--restart` continues on its parent run's binary
  (read from its `run_manifest.json`; refused if unknown) unless `--binary` says otherwise.
  Which binary knows what: `results/merger/binaries.tsv`.
- **Verify by effect** within the first minutes: eyeball frame 0 against a reference
  run (renderers fail silently), and see the first checkpoint appear if you asked for one.
- **Never edit a script a live run is executing** in place: bash reads scripts by
  byte offset as it goes. `run_single.sh` and `build_binary.sh` are one `{ ... }`
  block and safe; for any other long-running script, write a new file and `mv` it
  over the old one.

## Data

- `runs/` is untracked and stays so (sizes); what must survive is packed into
  `results/` by `research/merger/pack_results.sh`. Never add `runs/` to git.
- Scratch (`/tmp/grteclyn_scratch/` on each node) holds plotfiles and checkpoints;
  prune only on the user's word and log it in `runs/wormhole_merger/manifests/MANIFEST_CLEANUP_<date>.md`.
- **Never delete frames.** A run's `frames/` (the rendered PNGs, the `_slice_cache`) and
  `movies/` are never removed: not at close-out, not in a prune, not as "leftovers", not
  to save space, not for runs called corrupted or uncited. The slice cache is the only
  source of a run's pictures once its plotfiles are gone, so a deleted frame set cannot
  be rebuilt. "Prune plotfiles/leftovers/scratch" never covers frames; only an explicit
  instruction naming frames and the runs does, and then ask once before deleting.
  (2026-09-25: five runs' frames were deleted as "leftovers", unrecoverable.)
- **Movies stop at the run's trust window.** Put the last trustworthy time in
  `results/merger/trust_windows.tsv` (wall reflection, blow-up, lost resolution) and
  close out: the movies and their colour scales use only frames up to it, and later
  frames stay on disk. Figures and the paper quote nothing after it either.
- Heavy analysis (yt, covering grids) runs in the background with a log; trim the matrix first.
- GWOSC downloads are the slow part of any search: bypass the local proxy, use `--block-s 4096`.

## The paper

- Every quoted number is a row in `research/merger/article/claims/ledger_*.tsv` and
  reaches the text as a `\clm...` macro from the generated `numbers.tex`. Change the
  ledger, run `claims.py check`, then `claims.py tex` — never edit `numbers.tex`.
- Figures: every label hangs on what it names and no line crosses text
  (`style.label_audit` in the wrapper's figure package checks this).

## Git

- **Commit subjects at most 72 characters**, blank line, then the body; detail goes
  in the body and the narrative in `GPU_PLAN.md` (the `commit-msg` hook enforces it;
  install with `python3 grteclyn-wrapper/scripts/ops/check_commit_msg.py --install-hook`).
- No `Co-Authored-By: Claude` trailers.
- No machine identity in tracked files (user, host, home paths): the `pre-commit`
  hook (`grteclyn-wrapper/scripts/ops/check_machine_paths.py --install-hook`) blocks
  it. Say "the first/second GPU node", never the hostname.
- Several sessions may share this working tree: **stage explicit paths**, never `git add -A`.
- Push in the background with a timeout (`< /dev/null`), then verify with
  `git ls-remote`; a foreground push can hang the shell.
