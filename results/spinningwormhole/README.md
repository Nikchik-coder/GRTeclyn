# Spinning-wormhole campaign — packed results

Nonlinear evolutions of rotating Ellis–Bronnikov wormholes, slow spin to the
extremal Kerr limit. Plan: `research/spinningwormhole/SpinningWormhole.md`;
live state: `research/spinningwormhole/STATUS.md`; code:
`Examples/SpinningWormhole/` (launcher:
`grteclyn-wrapper/scripts/campaigns/spinning_wormhole/`).

- `binaries.tsv` — the record of every frozen campaign binary (the bin/
  directory itself is untracked).
- `runs_registry.tsv` — one line per run: what it is for, outcome.
- `campaign/` — packed runs (thinned streams, `evolution_params.txt`,
  `run_manifest.json`), created by the campaign's pack step when the first
  runs close out.

No runs yet (2026-10-10): the campaign scaffold landed, the first binary and
the Step 0 checks are next.
