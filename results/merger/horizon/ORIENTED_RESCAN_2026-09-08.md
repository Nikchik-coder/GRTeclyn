# Oriented common-surface rescan of the held death stacks (2026-09-08)

**Claim:** none of the 21 held death-stack plotfiles contains a marginally
outer-trapped surface (MOTS) around the grid centre in r = 0.3–5.8. Every
"trapped shell" the old consumer reported is the naive +r orientation reading
the throat's compactified interior. Defect 2 (no horizon ever formed) holds on
every arm, not only on cf08.

**How measured.** `grteclyn-wrapper/scripts/validation/ah_oriented_scan.py` on
level 3 (dx = 0.0625) with `--half 6.0 --rmin 0.3 --table 0.5`: areal radius
R(r) of each coordinate sphere from its induced 2-metric, outward taken as the
direction of increasing R, both null expansions θ_out/θ_in, Misner–Sharp mass
per shell. A MOTS would show as θ_out = 0 with θ_in < 0. Raw per-shell tables:
`oriented_rescan_death_stacks_2026-09-08.txt` in this directory.
Plotfile number × 0.01 = code time (coarse dt = 0.01).

| arm | plotfile | t | throat r (coord) | R at throat | naive "trapped" r-range | corrected verdict |
|---|---|---|---|---|---|---|
| nodamp (p012) | Plt05050 | 50.5 | 1.18 | 4.297 | 0.44–1.12 | no MOTS |
| nodamp (p012) | Plt05100 | 51.0 | 1.16 | 4.275 | 0.42–1.08 | no MOTS |
| nodamp (p012) | Plt05150 | 51.5 | 1.14 | 4.253 | 0.46–1.06 | no MOTS |
| p015_rr (= p015_nofill, see note) | Plt05200 | 52.0 | 1.48 | 4.441 | 0.40–1.38 | no MOTS |
| p015_rr | Plt05250 | 52.5 | 1.48 | 4.425 | 0.40–1.36 | no MOTS |
| p015_rr | Plt05300 | 53.0 | 1.48 | 4.410 | 0.38–1.36 | no MOTS |
| p020_nofill | Plt05100 | 51.0 | 2.20 | 4.971 | 0.62–2.06 | no MOTS |
| p020_nofill | Plt05150 | 51.5 | 2.22 | 4.961 | 0.62–2.10 | no MOTS |
| p020_nofill | Plt05200 | 52.0 | 2.26 | 4.951 | 0.62–2.14 | no MOTS |
| cf08 (record arm) | Plt05450 | 54.5 | 1.02 | 4.129 | 0.32–0.94 | no MOTS |
| cf08 | Plt05500 | 55.0 | 1.00 | 4.108 | 0.32–0.94 | no MOTS |
| cf08 | Plt05550 | 55.5 | 0.98 | 4.086 | 0.32–0.90 | no MOTS |
| lc1 | Plt04250 | 42.5 | 1.60 | 4.421 | 0.40–1.40 | no MOTS |
| lc1 | Plt04300 | 43.0 | 1.56 | 4.388 | 0.38–1.38 | no MOTS |
| lc1 | Plt04350 | 43.5 | 1.52 | 4.355 | 0.38–1.38 | no MOTS |
| nodamp_cf10 | Plt04350 | 43.5 | 1.60 | 4.694 | 0.44–1.36 | no MOTS |
| nodamp_cf10 | Plt04400 | 44.0 | 1.56 | 4.661 | 0.42–1.34 | no MOTS |
| nodamp_cf10 | Plt04450 | 44.5 | 1.52 | 4.628 | 0.42–1.34 | no MOTS |
| single_hold_t100 (Stage 0) | Plt10000 | 100 | — | — | — | not scannable: 7-variable plotfile, no h_ij/A_ij |

Notes.
- The p015_nofill and p015_rr Plt05200 stacks are byte-identical on level 3
  (same md5, same size): the rerun reproduced the original evolution exactly, so
  they count as one stack. Their three verdicts are listed once.
- On every arm the throat's areal radius shrinks slowly across the death window
  (about −0.02 per 0.5 time units, ≈ −1 %/unit, the rate already measured on
  cf08) and the throat's coordinate radius drifts inward. That is the
  compactified origin closing, not a horizon.
- Entries the scanner labels "areal-radius minimum at r = 0.32, R ≈ 30" (lc1,
  nodamp_cf10) are the inner scan edge, where χ → 0 makes R blow up; they are
  not surfaces.
- The consumer's r/√χ areal-radius proxy reads ≈ 20 % high at the throat on
  every arm (h_ij ≠ δ_ij there); INSTABILITY.md's radii use that proxy.
