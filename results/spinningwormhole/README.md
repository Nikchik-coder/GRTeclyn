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
  The merger's production `single_hold_t100` ran on this exact grid (L = 64,
  N = 128, ml3), and the new table-driven pipeline reproduces it as a
  numerical twin over the FULL record: t = 0 bit-identical, L2_Ham within
  5e-7 (median 0) for all t ≤ 100, collapse milestones within one time unit;
  τ(δR) = 5.27 vs the merger's 5.12 fit; MOTS on every plotfile, horizon
  detaches at t ≈ 61 and shrinks under the phantom flux.  The t > 80
  constraint growth is the same in both runs — a property of this grid, not
  of the new code.  Trust window t ≤ 64.  Constraint overlay:
  the run's `figures/constraint_norms.png` (both curves within linewidth).
