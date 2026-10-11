# Spinning-wormhole campaign — packed results

Nonlinear evolutions of rotating Ellis–Bronnikov wormholes, slow spin to the
extremal Kerr limit. Plan: `research/spinningwormhole/SpinningWormhole.md`;
live state: `research/spinningwormhole/STATUS.md`; code:
`Examples/SpinningWormhole/` (launcher:
`grteclyn-wrapper/scripts/campaigns/spinning_wormhole/`).

- `binaries.tsv` — the record of every frozen campaign binary (the bin/
  directory itself is untracked).
- `runs_registry.tsv` — one line per run: what it is for, outcome.
- `trust_windows.tsv` — the last trustworthy time per run; movies, figures
  and quoted numbers stop there.
- `campaign/` — packed runs (full `.dat` streams, `evolution_params.txt`,
  `run_manifest.json`, `mots_spectral.dat`; paths scrubbed by
  `grteclyn_wrapper.packaging.scrub_paths`).

## Claims

- `01_static_hold/static_hold_L64_t100` (2026-10-11): the Step 0 anchor.
  The table-driven pipeline reproduces the merger campaign's `single_hold`
  drainhole evolution exactly — t = 0 bit-identical, max rel diff 5e-5 over
  the packed overlap, collapse milestones within one time unit (−10 % throat
  at t = 57 vs 58, −25 % at 62.6 vs 63); τ(δR) = 5.27 vs the merger's 5.12
  fit; MOTS on every plotfile, horizon detaches at t ≈ 61 and shrinks under
  the phantom flux.  Trust window t ≤ 64.
