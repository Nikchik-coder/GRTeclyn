# t = 0 parameter matching (2026-09-27)

Initial-data measurements, no evolution: which throats a binary is made of, and what the pair
weighs. CPU (OpenMP) build of commit 5955760 in a cloud container; the story is the plan entry
"2026-09-27 (12:15 UTC) — parameter matching and the energy check" in `research/merger/GPU_PLAN.md`.

- `t0_checks.tsv` — the three checks: the single throat, each mouth of the superposed and the solved
  d = 8 pair (every puncture mode), and the d = 12 spiral pair. R_min: minimal coordinate sphere about
  the centre; M_far, Q_far: ADM mass and scalar charge of the mouth's own far side; m1: the isolated
  drainhole with that (M_far, Q_far), i.e. the one-body mass; M_ADM: the volume identity.
- `energy_scan.tsv` — the energy check: far-side-matched pairs (mode 3) at d = 8–48, both scalar signs,
  one grid; E_b = M_ADM − 2 M1 with M1 the single throat on that grid.

Recompute any row with `Examples/BinaryWormholeMerger` (`constraint_solve = 1`, `max_steps = 0`) and
`grteclyn-wrapper/scripts/validation/constraint_solve_t0_check.py --mass`. The paper reads these files
through the claims ledger (`t0_matching` extractor).
