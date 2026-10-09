# Status — 2026-10-08 ~14:35 UTC

What is live, what is planned, the main results — nothing else. Run-by-run outcomes are in
`results/merger/runs_registry.tsv`, cleanups in `runs/wormhole_merger/manifests/`, the map in
[`../../MAP.md`](../../MAP.md). The page before this compaction (the campaign diary to 10-08) is
`git show f2c4caa9:research/merger/STATUS.md`. **When a run ends, its row leaves Live and its result goes into
Main results in a line or two; the details go to the registry.**

## Live

No run is live. Both nodes are idle: the first node's two H100s since 03:10 UTC 10-08 (scratch empty, 1.1T free),
the second node's card since CONV-fz lvl7 finished at 13:58 UTC 10-08 (scratch: only the HFL cell, 60G, deliberate;
585G free). NFS holds no checkpoints: CONV-fz's three t = 100 states were wiped 10-08 after the constraint check
(`runs/wormhole_merger/manifests/MANIFEST_CLEANUP_2026-10-08.md`).

## Planned (nothing launches without the go)

**CONV-fz: done 10-08.** lvl7 is packed in `08_convergence/` (frames kept, no movies), Table III counts it as measured,
Fig. 11(d) draws Δx 1/64 and both neighbouring differences, and (e) draws ⟨H_ADM⟩ from
`results/merger/analysis/convfz_constraints_t100.tsv` (`checkpoint_hamiltonian.py --out`). The results are under
Main results, Convergence. The paper side is done 10-08 on the workstation: the Fig. 11 caption covers all three
levels and panel (e), with four new ledger rows (`clmConvFzPsiDiffFine` 0.54, `clmConvFzEnergyDiffFine` 0.09,
`clmConvFzHamDiff` 1.4, `clmConvFzHamDiffFine` 0.4; `clmConvFzPsiDiff` prints 0.55 now). The waveform wording
chosen: both pairwise |r Ψ4| differences are quoted (0.55 % / 0.54 % of peak — resolved at the half-percent floor,
not shrinking pointwise), while the energy carries the order (1.7) and the caption/appendix carry the H leak test.
The figure re-render on the workstation is byte-identical to the node's. PDF rebuilt: 26 pages, zero overfull,
both engines, text ends on page 21.

**Paper updates waiting on the user's call:**
- FARZONE-ho's far-zone energy: Sec. VIII and Fig. `convergence`(c). (Fig. 8's head-on row is FARZONE-ho since 10-08;
  Fig. 9 and every quoted energy still read the production chain.)
- CONV-fz: App. A's text, and how to word r Ψ4's non-convergence over t = 36–60 (Main results, Convergence).
- Done 10-08: Fig. 11(d) with all three levels; the caption's order 1.7 is the final three-level value.
- Done 10-08: SCATTER-fate in Fig. 1 (the like-signed branch ends in inflation) and Sec. V C (Video 12).
- Done 10-08: Table III counts the convergence set (6 runs) and SCATTER-fate: 103 runs, 592 GPU-h (lvl7 measured).

**arXiv submission (decided 10-08; submission day is 10-09).** After the final PDF (lvl7 is closed out):
- Done 10-09: the paper is retitled "Binary Ellis–Bronnikov wormholes in 3+1 numerical relativity: mergers,
  fly-bys and gravitational waves" (the old title claimed the seed story and undersold the single-throat half).
  The title is changed in the tex, the root README, `.zenodo.json`, `CITATION.cff`'s preferred-citation and all 12
  paste-ready YouTube descriptions in `results/merger/movies/_youtube/README.md`; pasting those into the 12
  YouTube videos is a by-hand step. The upload zip on the workstation desktop is rebuilt with the new title.
- Done 10-08: feature/merger merged into develop (fbdfa55b), keeping off develop — as on 10-06 — `research/`, the
  matter-first results pack and develop's own `results/README.md`. The merge is tagged `v1.0-wormhole-merger`;
  branch and tag are pushed.
- Done 10-08: the repo is switched ON in Zenodo (GitHub sync page, Nikchik-coder/GRTeclyn toggle confirmed).
- Done 10-08: the GitHub release on the tag is published (public) and Zenodo archived it. Version DOI
  10.5281/zenodo.23245934 (concept 10.5281/zenodo.23245933). The version DOI is in the cost section's code
  statement and in `CITATION.cff`; PDF rebuilt, both engines, 26 pages, zero overfull, text ends p. 21.
- `CITATION.cff`, `.zenodo.json`, `README.md` and `results/README.md` describe this paper since 10-08, with arXiv
  placeholders `XXXX.XXXXX`. `.zenodo.json` has none, because Zenodo validates identifiers: add the arXiv link on the
  Zenodo record once the number exists. `CITATION.cff` carries `date-released: 2026-10-09` and the version DOI
  since 10-08.
- arXiv: gr-qc primary, cross-lists astro-ph.HE and astro-ph.CO. The abstract is cut to ~1,760 rendered characters
  (the form takes 1,920).
- The source package is research.tex, numbers.tex and the 15 figure PDFs under `figures/`, which the graphicspath
  searches first. Clean-copy builds pass on both engines with zero overfull boxes (26 pages; Eq. (force) split
  10-08 fixed the last one).
- Referee-response text added 10-08, existing ledger rows only: the LISA SNRs' near-zone error bound (Sec.
  heavy seeds) and why Fig. 12's L2 norms are large yet the waves clean (Appendix A, the Fig. 11(d) leak test).
  Closed 10-08 with lvl7's pack: the three-level GW order (1.7) and Fig. 11(e)'s H leak test are in the caption
  and Appendix A. All three referee points are now answered in the text.
- Videos 1–12 are unlisted (link-only) — enough, decided 10-08: the paper carries the URLs. Before submitting:
  both authors' sign-off on the final PDF.
- After the number: fill the placeholders (README, results/README.md, CITATION.cff), the release notes and the
  Zenodo record's arXiv link.

RUNS FOR THE PAPER: none, and no new runs (decided 10-09): referee items that a run would settle are answered in the
text only. Earlier proposals were dropped before submission; `git show 2acaa681:research/merger/STATUS.md`.

## Main results (the paper's wording; every quoted number is a ledger row)

**Method:**
- Every binary starts from matched mode-3 initial data (`constraint_solve_puncture_mode = 3`).
- A moving throat is the exact Lorentz-boosted drainhole (momentum model 1), with a per-throat slicing freeze and the
  boosted-pair solve. Its t = 0 axis ratios sit on 1/γ to 6e-5.
- Every horizon number comes from the 3D MOTS finder (`mots_spectral.dat`).
- The superposed and Bowen–York campaigns are archived in `00_archive/`.

**Single throat** (§III–IV):
- It is an unstable fixed point with one exponential mode. At small amplitude, τ = 5.12 / 5.23 at levels 3 / 4,
  against the linear 5.13. Truncation noise picks the branch.
- Collapse: the horizon shrinks 40 %. The 9–11 % "regrowth" is numerical.
- Inflation (F4, to t = 218): the throat keeps growing, anti-trapped, at the Shinkai–Hayward rate in proper time.
- A seeded throat goes opposite to its kick. On solved data the ε = 0.1 seed is born trapped (SEED-csm).

**A moving throat** (p = 0.45, v = 0.41; Fig. 2(d)): it collapses on the resting throat's own mode (τ = 5.0–6.1,
against 5.12), at levels 3 and 4.

**Two throats at rest** (§V, Fig. 4):
- Like signs repel and opposite signs attract.
- Pull/push is 1.462 ± 0.022, the fixed-scalar-potential value of 3/2.
- The force goes as (d + δ)⁻² with δ = 2.65.
- The push grows with the width as a^1.2–1.4, not the point-charge a².

**SCATTER-fate** (NEW 10-08, in the paper: Fig. 1, Sec. V C; packed `03_two_throats/csm/ctrl_rest_d12_csm_t100`): the
like-signed d = 12 rest pair recedes, and both mouths inflate, mirror-symmetric.
- The separation grows from 11.94 to 26.4 by t = 60.
- The throat R grows from 3.88 to 4.78 by t = 30 (the per-mouth scan; anti-trapped), then to 7.7 by t ≈ 48 (χ
  slices).
- There is no MOTS about either mouth after t = 16.5.
- The constraints sit at their t = 0 level to t = 50. Then the L = 64 box's collapsed lapse reaches the sponge.
- Trust t ≤ 80 (the user); the run died at t = 95.08.
- No GW burst: the l = 2 Ψ4 at R = 14 and 30 is a smooth, single-signed drift that grows with the inflation (e-fold
  ~5 at R = 30), the same in every like-signed rest pair from t = 0 (d = 12/14/18 alike); the box (L = 64) cannot
  split it into near field and radiation.

**Head-on** (d = 8, t = 0–100; §VI, Fig. 5):
- A common MOTS forms at t = 18.0 (R 5.634, M_MS 2.817 > M_ADM 2.357) and holds to the end (R 4.779, M_MS 2.389 at
  t = 100).
- It never bounces, and R settles toward 2 M_ADM.
- After it forms, the ℓ = 1 scalar rings at ω = 0.122–0.124, against the final mass's QNM of 0.1226.

**FARZONE-ho** (NEW 10-08; packed `08_convergence/`; Fig. 8's head-on row, Video 11): the head-on in an L = 512 box with spheres to R = 180
(R/M = 76), clean over t = 0–250.
- The near zone reproduces production: E/M at R = 10 / 18 / 44 within −0.3 / −0.1 / +1.0 %.
- On windows aligned with the burst, E/M converges outward: 7.66e-3 (R = 44), 6.98e-3 (90), 6.82e-3 (150), 6.81e-3
  (180). So E∞ ≈ 6.8e-3, 20 % below the quoted 8.5e-3.
- Half of that gap is the pre-arrival content the paper's window keeps; half is the fall from R = 44 outward.
- The paper's fixed window, t − R ≤ 56, does not follow the burst's tortoise drift, and on it E/M rises past R = 60.

**Orbits on boosted data** (d = 12, §VII):
- p = 0.12 spirals in but never merges (died t = 71.78, trust 56.5; level 4 agrees).
- p = 0.25 and 0.45 scatter: no wall, no MOTS.
- p = 0.60 and 0.90 plunge. At p = 0.60 there is no MOTS at level 4 or 5: the stall is physical. At p = 0.90 the run
  dies at t = 45.28 at both levels.
- So the capture boundary sits in (0.45, 0.60).
- The d = 6, p = 0.10 design point merges (common MOTS from t = 13; t = 0–100).
- Each companion is a −ε kick (−0.4 % at d = 12, −1.2 % at d = 8) that seeds inflation, so a merger is a race to
  contact.

**Masses:**
- A moving pair's mass is M_ADM_boost; the face estimate drops Σ(γ−1)σm.
- The measured t = 0 ADM energies are 2.304 / 2.317 / 2.282 at p = 0.25 / 0.45 / 0.60, flat in p.
- The paper quotes the d = 12 pairs' E/M per this measured mass.

**Waves** (§VIII):
- Every channel radiates.
- E_GW(p) turns over between p = 0.45 and 0.60; the p = 0.45 fly-by radiates the most.
- The scalar channel is comparable and negative-energy, and the horizon switches it off.
- The core damping does not shape the fly-by's waves (DAMP-off, to 1e-7).

**Searches** (§IX–X): LIGO O3b (2.25 h, 154 templates) finds no candidate, and none is expected. LISA is the
headline channel.

**Convergence** (App. A):
- The static throat at levels 2 / 3 / 4 against the exact solution: order ~2.2 early, ~3 later.
- The wave zone is resolved (CONV-csm-w: 0.01–0.15 % of peak).
- CONV-fz, the binary three-level set (Δx 1/16, 1/32, 1/64 on FARZONE-ho's L = 512 box, t = 0–100; Fig. 11(d, e)):
  - E at R = 10 converges at order 1.67: the levels differ by 0.29 % and then 0.09 % (C = 3.18).
  - Every level forms the common MOTS at t = 18; R and M_MS agree to 0.084 % and then 0.078 %.
  - r Ψ4 at R = 10 converges before the merger, at the burst peak and in the late ringdown (C = 2.3–3.2), but not
    over t = 36–60 (C = 0.5–1.0), so its largest difference stays 0.54 % of the peak for both pairs.
  - ⟨H_ADM⟩ outside the MOTS at t = 100, read on level 4, which all three share there: 1/16 against 1/32 within
    1.4 %, 1/32 against 1/64 within 0.43 % (C = 2.9–8.4). The interior's resolution does not leak out; an order for
    the exterior violation itself needs the static throat's levels (~3 GPU-h, no go).

## Traps (each has cost a run)

- The logged L2 constraint norms are level 0 only (Δx = 0.5 on L = 128, 2 on L = 512). A moving pit spikes them
  while the fine solution is clean, and they cannot show convergence. Read the finest level (`ham_level_map.py`)
  before calling a run unconstrained.
- Level-1 noise grows at σ = 0.1, doubling every ~6 units on the ±20 cube; σ = 0.3 cures it. Wave spheres inside
  level 1 (R ≤ 20) or across its corners (R = 28, 30) are contaminated late. Use the symmetry-forbidden modes as the
  monitor.
- Compare norms across restarts and boxes by onset times, never by ratios.
- A relative path in `--consume-args` (e.g. `--horizon-track`) resolves from the run dir, the consumer's cwd, and
  fails silently. Pass absolute paths.
