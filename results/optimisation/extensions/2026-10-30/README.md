# Stationary extension tests, 2026-10-30

These are bounded exploratory tests, not a completed optimisation or a
stability study. No GRTeclyn evolutions were run. The cluster regression suite
passed all 32 tests before the trials.

Paper scope decision, 2026-10-30: exclude these extension trials because the
validated incremental reduction is small. The code and data remain archived
as exploratory research; no follow-up extension runs are planned.

## Result

The D21 fixed-area potential perturbation `shape_b1_plus` reduces X_A from
1.8410621350 to 1.8383247213 (0.1487%). Both the reference and trial pass the
independent constraints at 150×30 and 180×36; the summed grid drift in X_A is
3.4e-13. This changes a potential control while allowing the shape to respond;
it does not isolate a shape-only effect.

The fixed-radius `potential_b3_plus` trial gives X = 1.8207149850, 0.4419%
below the previous D21 value. Its two grids pass, but the new fine-grid
reference solve is ABOVE_GATE, so the automated comparison is UNCONFIRMED.
The shifted-asymmetry trial is also UNCONFIRMED: its fine-grid E19 fails.

S0 ordinary and rotating clouds solve at nonzero amplitude but give no lower
bill in this sample; both the references and the clouds fail the independent
constraint gate. The D21 linear bound-mode search found no suitable seed at
the tested masses. Neither outcome rules out a different mass, self-interaction
or finite-amplitude branch. All stability statuses are `not_assessed`.

## Contents and provenance

- `inputs/d21.npz`: saved D21 e140, 210×42. Original input:
  `runs/optimisation/evolution/verified/fam_a_r1_0000_e140_210x42.npz`.
- `inputs/s0.npz`: saved S0 search candidate. Original input:
  `runs/optimisation/opt/fam_b_0000_opt4s_kink_150x30_s0_best_clean.npz`.
  Historical filenames and metadata are not clearance certificates.
- Each experiment directory contains the exact `manifest.json`, every
  `results.jsonl` record (including failures), and all successfully solved
  trial NPZ files. Records include ABOVE_GATE fields for diagnosis, never
  as accepted backgrounds. Their schema is distinct from evolution exports.
- First batch: `5db53c14`; follow-up: `15fbbf7c`. The follow-up accepts a
  Newton stall below 1e-9 but retains E19/E_c <= 1e-8, the physical-size
  check, total-J bookkeeping, and both asymptotic matter mass gaps. It
  checks cloud decay beyond |xi| > 0.99 instead of the first batch's 0.9.
- Each process used six CPU threads, a 200 GB address-space cap and a 1 h
  timeout. All four jobs exited normally. The first low-mass S0 batch has
  no nonzero cloud solutions; the follow-up uses boson mass 3.

## Reproduce on a GPU node

Use `grteclyn-wrapper/scripts/ops/capped_job.sh`, check that the card is free,
and select a new output directory. On the current code, the follow-up D21
command is:

```sh
bash grteclyn-wrapper/scripts/ops/capped_job.sh start ext-reproduce-d21 \
  --threads 6 --mem 200 --gpu --timeout 3600 -- \
  taskset -c 0-5 grteclyn-wrapper/.venv/bin/python \
  grteclyn-wrapper/scripts/optimisation/explore_extensions.py \
  results/optimisation/extensions/2026-10-30/inputs/d21.npz \
  --stages potential,cloud,winding,asymmetry --indices 1,3,6 \
  --grid 150x30 --fine-grid 180x36 --gpu 0 \
  --out runs/optimisation/extensions/reproduce-d21
```

For S0, use `inputs/s0.npz`, `--stages cloud,winding --matter-mass 3`,
and another output directory. Run the first-batch manifests at their recorded
commit to reproduce the original localization filter and Newton cutoff.

A confirmed reduction requires reference and trial to pass on both grids,
a negative change on both, and a fine-grid reduction larger than five times
the summed reference/trial grid drift (and larger than 1e-6). This is a test
of the stated phantom-only radial volume integral, not a proof of stability
or of a global minimum.
