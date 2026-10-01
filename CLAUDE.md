# Working in this repository

Read [`MAP.md`](MAP.md) (what is where) and, for the merger campaign,
[`research/merger/STATUS.md`](research/merger/STATUS.md) (what is live) first.
Every rule below exists because breaking it cost a run, a result or a day.
Several sessions edit this file every day, so re-read it from disk at the start of every task; the copy loaded at
session start goes stale within hours.

## Replies

- Keep every reply to a few lines, even for results and "explain in plain English". Lead with the answer. No tables,
  caveats, recaps or offers unless asked.
- A status question wants run, t, speed, ETA, whether it is alive, and storage. Nothing else.
- **Every run check includes storage, unasked** (the user, 2026-10-01: "one of the number one questions", so that
  there is no pollution).
  - On each node: the scratch disk's free space (`df -h /tmp/grteclyn_scratch`) and every folder in it.
  - Per run: at most 3 plotfiles (the consumer's `--keep-last 3`). Checkpoints only if the user asked for them, and
    no more than the run's `checkpoint_keep` (its log prints a `[checkpoint_keep] removed` line at every write).
  - No leftovers of finished runs, except the checkpoints a queued run needs.
  - Report it in one line: clean (GB used and free), or what pollutes and how many GB.
  - A node this session cannot list: read its runs' logs for the checkpoint lines, and say its disk was not listed.
- Every ETA is in hours and clock time (UTC).

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

**Before every launch, in this order.** These are the user's standing rules; each one had to be repeated in session
after session because it lived only in one machine's agent memory.
1. **Wait for the go.** A proposed run gets no GPU start-up of any kind, not even `--preflight-only`, until the user
   says go for that run.
2. **A rerun is its old run.** Start from the old run's packed `results/merger/campaign/.../evolution_params.txt` and
   change only the knob under test (for the mode-3 reruns: the constraint-solve block, and the name + `_csm`). The
   plot variables the frame set needs are the only other change. Keep the same L, N, max_level, tagging_L, sponge,
   separation, gauge, dt, stop_time and plot cadence. Diff the template against the old params before launching. If
   the old box cannot hold a new setup, ask the user; never move the whole set to a bigger box.
3. **Ask about checkpoints.** Whether a run writes checkpoints is the user's call, asked directly for each run. They
   are never on by default.
4. **Check the start within minutes.** Read the log's M_ADM and each mouth's far side (mode 3), compare frame 0 with
   the old run's, check the card's memory in `nvidia-smi`, and look for the first checkpoint only if one was asked for.
5. **Update STATUS at once.** Every launch, stop or wipe goes into STATUS.md's Live/Queued tables (run, node/card, t,
   stop time, speed, ETA in hours and clock time). Commit and push it immediately and verify with `git ls-remote`. If
   the push is rejected, fetch, rebase and push again.

- To stop a run now: `grteclyn-wrapper/scripts/campaigns/stop_campaign.sh <run dir>`. To stop it at a given time,
  create `dump_and_stop` in its run dir once its log passes that time. AMReX checks every 10 coarse steps, then
  writes a checkpoint and exits normally.
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
  The one exception, on the user's word: the convergence study (`08_convergence`) keeps no
  frames and no movies. Launch it with `--frames-fields none`, or `--frames-fields chi` for
  the sign-rule arms (the sign rule reads the chi slice cache), plus the reason in
  `WHM_FRAMES_SUBSET`. Close it out with `WHM_MOVIES=0`.
- **A resolution test must refine what it claims to test.** `max_level` refines only the
  boxes on the tracked throats. An extraction sphere is read from the finest level that
  covers it, which is the base grid (Δx = 0.5) for R ≥ 20 on L = 128, whatever `max_level`
  is. To test the wave zone, raise that sphere's `extraction_levels`: the ExtractionTagger
  then refines the whole ball r < 1.2 R. On 2026-09-26 the convergence runs varied
  `max_level` alone, and the wave zone went untested until CONV-3w.
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
- Plotfiles: the consumer keeps the last 3 on scratch (`--keep-last 3`); that is the intended retention.
- Heavy analysis (yt, covering grids) runs in the background with a log; trim the matrix first.
- GWOSC downloads are the slow part of any search: bypass the local proxy, use `--block-s 4096`.

## When a run finishes

Do these steps, in this order and in the same session, without being asked, in one fast pass: batch them, fix only
what the claims check or the identity grep flags, and report in a few lines.
1. **Check it.**
   - It reached its `stop_time`, or record where and why it died. A `stop_time` is a choice, not a survival: before
     calling a run clean or "no wall", compare where it stopped with where the closest earlier arm of its family
     failed, and read the last units of `collapse_diagnostics.dat` and `constraint_norms.dat`.
   - Read the run's own `run.log` for NaN; never infer a death from a sibling. The t ≈ 52 wall belongs to the
     plunging mergers; the p = 0.45 fly-by never NaN'd.
   - No NaN in the death window (`closeout.sh` prints this).
   - Its headline number agrees with its partner run.
   - Its trust window: add a row to `trust_windows.tsv` if the solution stops being trustworthy before the end.
2. **Pack it.**
   - List it in `research/merger/article/claims/table1_groups.tsv`, as `-` until the paper cites it. The claims check
     fails for a packed run that isn't listed.
   - File it: `file_run.sh --group NN_name <run>`. A new study gets its own group folder, so it never mixes into the
     physics groups (the convergence runs: `08_convergence`).
   - Run `research/merger/closeout.sh <run>`: it makes the movies up to the trust window and rebuilds the pack.
     For a run nobody will cite (corrupted, diagnostic, stopped early) use `WHM_MOVIES=0`: the user does not want
     its movies. Its existing frames still stay.
   - Live runs are never packed (`pack_results.sh` skips them), because a partial pack is git pollution.
3. **Document it.** Update:
   - its row in `results/merger/runs_registry.tsv` (outcome);
   - its claim line in `results/merger/README.md`;
   - a dated entry in `research/merger/GPU_PLAN.md`;
   - `research/merger/STATUS.md` (live runs, queue).
4. **Prune.**
   - Delete its scratch plotfiles, and any checkpoints no queued run needs.
   - Log the prune in `runs/wormhole_merger/manifests/MANIFEST_CLEANUP_<date>.md`.
   - Frames are never part of a prune (see Data, above).
5. **Launch the next queued run** on the freed card, if the user has said go for it (otherwise ask: see "Before
   every launch"). Check `nvidia-smi` first; the preflight runs before anything starts. Record the launch in STATUS.
6. **Commit and push** the tracked changes, staging explicit paths.

## The paper

- Every quoted number is a row in `research/merger/article/claims/ledger_*.tsv` and
  reaches the text as a `\clm...` macro from the generated `numbers.tex`. Change the
  ledger, run `claims.py check`, then `claims.py tex` — never edit `numbers.tex`.
- The paper states verified results only. It has no failure narratives, no "not computed / not measured here" and
  no mention of data that was not saved. Anything a simulation or analysis could settle goes into `GPU_PLAN.md`
  with a cost, not into the text. The Scope paragraph keeps only model assumptions.
- Figures are `figure*[t]` strips of at most about half a page, never full-page floats. Every caption ends with its
  outcome.
- Figures: every label hangs on what it names and no line crosses text
  (`style.label_audit` in the wrapper's figure package checks this). Each panel gets a legend above its frame
  naming every line; inside the frame there are at most tiny tags on vertical rules. `style.GOLD` is the one accent
  (the horizon, or the fitted exponential); everything else is ink or grey.
- A figure fix: make the minimal fix, render, run the label audit and show the image first; audits come after.

## Git

- **Commit subjects at most 72 characters**, blank line, then the body; detail goes
  in the body and the narrative in `GPU_PLAN.md` (the `commit-msg` hook enforces it;
  install with `python3 grteclyn-wrapper/scripts/ops/check_commit_msg.py --install-hook`).
- No `Co-Authored-By: Claude` trailers.
- No machine identity in tracked files (user, host, home paths): the `pre-commit`
  hook (`grteclyn-wrapper/scripts/ops/check_machine_paths.py --install-hook`) blocks
  it. Say "the first/second GPU node", never the hostname.
- Several sessions may share this working tree: **stage explicit paths**, never `git add -A`.
- "Commit and push" from the user means now, in one step: stage, commit, push, one `ls-remote` check.
- Push in the background with a timeout (`< /dev/null`), then verify with
  `git ls-remote`; a foreground push can hang the shell.
