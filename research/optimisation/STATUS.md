# Campaign M — status

What is live, what is planned, the main results — nothing else. Plan:
[`Minimal Exotic Wormhole Search.md`](Minimal%20Exotic%20Wormhole%20Search.md).
Code: `grteclyn-wrapper/src/grteclyn_wrapper/optimisation/`
(commands, workflows, checks and derivations; layout in its
[README](../../grteclyn-wrapper/src/grteclyn_wrapper/optimisation/README.md)).
The page before this compaction (the campaign diary to 2026-10-29) is
`git show 96c177ee1:research/optimisation/STATUS.md`.

Priority: **repair and revalidate the radial stability screen** (pending).

**Instability screening is NOT FIXED (2026-10-30).** The current CMA-ES
search disables the radial screen: `--stability` is refused and new results
record `stability = not_assessed`. The new finer-grid checks validate the
stationary background only; they do not measure instability or establish
dynamical stability. Earlier zero-instability labels remain withdrawn.
The potential's sigma² scaling, unmatched-eigenmode handling and independent
background/eigenmode constraint checks still need repair and revalidation
before instability screening can be enabled again.

The stationary extension trials are complete and archived as exploratory work;
their small validated gain does not warrant inclusion in the paper (2026-10-30).
No further extension runs are planned. D30 evolution authorization was withdrawn
on 2026-10-30 at about 22:26 MSK: stopped at t = 0.54. A fresh D30 CMA-ES
search is authorized: cheap finer-grid screening of each new best, then a
full independent re-solve of the finalist (choice confirmed at 22:34 MSK). D0 ended with a NaN at t = 88.4175. Evolution of the validated D30 e0316 winner is authorized on 2026-10-31, N128 on card 1, checkpoints off. The 2026-10-30
audit withdraws the zero-instability labels; physical stability is unresolved.
The D21 3+1 triplet ended in NaNs at every resolution. D40, D46 and D51 fresh searches and subsequent validated N128 evolutions
are authorized (2026-10-31), checkpoints off for each. The old D51 export
remains rejected; only a newly validated winner can be evolved.

## Live

Checked 2026-10-31 at 09:53 MSK: **D30 and D40 evolving; D46 searching; D51 failed its initial continuation.**

The module entry point is
`python -m grteclyn_wrapper.optimisation.commands.optimize_potential`.
D40 uses `fam_a_r1_0008`, seed 104; D46 uses `fam_a_r1_0010`, seed 146;
D51 uses `fam_a_log_0017`, seed 151, matching the plotted classical members.
All searches: 400 evaluations, 150x30, fixed reference R_e/J, cheap checks per
new best, full 150/180/210 finalist refinement, no radial stability screen.
Both nodes pulled refactor `1d934551` before the searches; the shared checkout
pulled `c6ec2e76` before the D40 evolution launch.

D40 completed all 400 evaluations at 09:43 MSK, exit 0. Finalist e0362
passes 150x30, 180x36 and 210x42: X = **1.820747219398**, versus V=0
4.014901700046 (**54.65% less**). Its final E19/E_c are 9.19e-10/4.24e-9;
R_e = 4.583555081219 and J = 2.407781150213 match the exact classical
reference. Refinement needed zero Newton updates; stability is unassessed.
The completed search, screens and final fields are archived under
`results/optimisation/completed/2026-10-31/d40/` (1.6 MB), with source and
archive hashes. No scratch plotfiles were produced by this search.

D46 retry `opt-d46-resolution-cma-r2` remains alive on first/card 0:
169/400 evaluations at 09:53 MSK, recent speed about 262 evaluations/h;
about 0.9 h remaining plus final validation (approximately 10:46 MSK).
Its initial attempt failed before evaluations because the 160 GiB virtual
cap blocked CUDA pool reservation. The retry uses 220 GiB, 4 threads and
a 4-hour cap; actual resident memory is about 2.9 GiB.

D51's detached queue launched the search on second/card 0 at 09:44 MSK,
after D40 finished. Initial continuation failed at m = 0.01875 after six
bisections (Newton residual 2.7e-7, max_iter); exit 1 at 09:45 MSK.
**No CMA evaluations or validated winner were produced.** The queue's JSON
says `search_launched`, not success; the capped-job exit code and log are
final. A revised retry is authorized (09:57 MSK): 60 mass increments to
m = 0.3 (step 0.005), 48 Newton iterations per initialization solve and
24 total bisections per leg. These replace 3/12/6 only for initialization;
fixed R_e/J, seed 151, search bounds, 400 evaluations, Newton acceptance
1e-9, independent constraints and finalist validation remain unchanged.
The new CLI options are covered by bounded-failure, seed-reuse and acceptance
regressions; 46 search/solver tests pass. The retry will use a fresh r2
output prefix and wait for D46 to release first/card 0. No GPU is free:
second/card 0 now runs the already-authorized D40 evolution. No dynamical
instability conclusion follows from this initialization failure.

D40 `D40_cma20261031_L64_N128_ml3_spdrv0_t100` started at 09:49:56 MSK,
second/card 0, checkpoints off. Its 2049x129 background was exported from
the validated finalist. The template was compared with the exact classical
D40 run: only background/deployment paths and explicit checkpoint-off keys
differ. Numerical controls remain N128/L64/ml3, drive 0, dt multiplier 0.02,
stop t = 100 and plot interval 100. Same matter binary 16460fb0, full 14-field
hold consumer, keep-last 3. Full preflight passed with all 14 fields rendered;
initial R_eq = 4.58284 versus spectral 4.58356. At 09:53 MSK t is about 1,
about 20 units/h, provisional ETA 4.9 h (14:50 MSK). GPU memory 22.4 GiB.
The initial chi frame was visually compared with the classical frame (the
saved images have different zoom widths); both are centered and nonblank.
All 14 frame-zero fields and throat/MOTS/wave rows are present. The first
consumer pass took 157 seconds from plot Header to diagnostic rows, within
the roughly 180-second plot cadence; subsequent horizon searches can warm
start. Keep-last 3 is configured; two plotfiles are currently present. D46/D51 evolutions remain authorized after valid finalists;
D51 currently has none. All these runs start from stationary fields, so no
queued evolution requires a restart checkpoint.

Run `D30_e0316_L64_N128_ml3_spdrv0_t100` uses the validated e0316
210x42 background exported to 2049x129. Diff against the previous D30
template changes only the background and run paths: N128, L64, max_level 3,
drive 0, dt multiplier 0.02, stop t = 100, plot interval 100. Checkpoints off;
full 14-field hold consumer with keep-last 3. Same matter binary (16460fb0).
Code/results pushed as `00ac13e3`, pulled on the node before launch.
Full preflight passed; frame 0 compared against the old D30 image, all 14
fields rendered, throat/MOTS/wave rows present. Consumer keeps up and prunes
to three plotfiles. At 09:53 MSK: t = 22.97, about 20 units/h, ETA 3.9 h
(13:44 MSK). GPU memory 22.9 GiB.

D30 `opt-d30-resolution-cma` finished all 400 evaluations at 23:15 MSK,
October 30 (exit 0). Finalist e0316 passes 150x30, 180x36 and 210x42:
X = **1.918733359440**, versus V=0 X = 4.375652217610 (**56.15% less**),
at J = 1.605934192814 and R_e = 4.268787555383. Final E19 = 4.16e-9,
E_c = 3.75e-9; relative X drift = 2.51e-14. The full Newton checks required
zero updates: each interpolated field already met the 1e-9 residual tolerance.
This is stationary numerical clearance, **not a repaired instability screen**.
The accepted fields are in `completed/2026-10-31/d30/` under the results pack.

D0 reached t = 88.4175, then aborted with NaN in K on level 3 (exit 6);
manifest completion 02:24 MSK, October 31. Last finite diagnostics are at
88.41; stop t = 100 was not reached. Mean late speed was 19.9 units/h.
The throat contracts by 0.2% at t = 47.35, 1% at 59.96 and 10% at 78.18.
The classical D0 reference reaches the same fractions at 36.66, 43.71 and
56.58. These are finite-N128 contraction times, not a continuum growth-rate
comparison. The areal-radius derivative fit over 0.2–1% contraction gives
tau = 7.770715 (t = 48–60), versus classical D0 tau = 5.439145 (t = 37–43):
a 30.00% lower finite-N128 growth rate. This new point is in the article figure.
The final Hamiltonian/momentum norms blow up; the terminal data
must not be presented as an accurate late-time solution or survival time.
Consumer diagnostics and all 14 field frames reach t = 88; checkpoints off.
Seven lossless diagnostic streams, parameters and failure evidence are archived
under `results/optimisation/completed/2026-10-31/d0/`. The archive is 2.9 MB
including D30's final fields, trace, log and all screening decisions.

Scratch clean at 09:53 MSK: second node D30 7.1 GB (three plotfiles),
D40 4.8 GB (two plotfiles), cache 47 MB, 451 GB free; first node cache 46 MB, 633 GB free. No checkpoints.
Deleted only the finished D0 and aborted D30 plotfiles (9.5 GB); no checkpoints.
Cleanup recorded in the October 31 scratch manifest.
Frames, slice caches and movies are retained on persistent storage.

| run | card | t | speed | ETA |
|---|---|---|---|---|
| `D30_e0316_L64_N128_ml3_spdrv0_t100` | second / 1 | 22.97 / 100, alive | 20.0 units/h | 3.9 h; Oct 31 13:44 MSK |
| `opt-d40-resolution-cma` | second / 0 | 400/400; three-grid PASS | done | ended Oct 31 09:43 MSK |
| `D40_cma20261031_L64_N128_ml3_spdrv0_t100` | second / 0 | about 1 / 100, alive | about 20 units/h | provisional 4.9 h; Oct 31 14:50 MSK |
| `opt-d46-resolution-cma-r2` | first / 0 | 169/400, alive | 262 evaluations/h | about 0.9 h; Oct 31 10:46 MSK plus final checks |
| `opt-d46-resolution-cma` | first / 0 | CUDA pool startup failure, no evaluations | ended | exit 134 |
| `opt-d51-resolution-cma` | second / 0 | initial continuation failed; no CMA evaluations | ended | exit 1, Oct 31 09:45 MSK |
| D46/D51 N128 evolutions | available cards | pending validated finalists; checkpoints off | — | D46 searching; D51 needs continuation repair |
| `D0_potential_L64_N128_ml3_spdrv0_t100` | — | NaN at 88.4175 / 100 | ended; 19.9 units/h | ended Oct 31 02:24 MSK |
| `opt-select-d0` | — | e0211 cleared 150/180/210; ended 21:56 MSK | done | — |
| `D30_potential_L64_N128_ml3_spdrv0_t100` | — | stopped at 0.54 on explicit abort | stopped | — |
| `opt-d30-resolution-cma` | — | 400 / 400; final three-grid PASS | done | ended Oct 30 23:15 MSK |
| `opt-select-d30-rest` | — | e0137 cleared all three grids; 9 alternatives checked | ended 22:21 MSK | — |
| `opt-d30-e0374-recheck` | — | both finer grids fail | ended 22:15 MSK | — |
| `opt-select-d30` | — | 30/30; no clearance with oversolving | ended 22:12 MSK | — |
| `opt-validate-d0` | — | 150x30 above gate; 180x36 Newton stalled | ended 21:43 MSK | — |
| `opt-validate-d30` | — | 180x36 and 210x42 above gate | ended 21:43 MSK | — |
| `D21_X1p829_L64_N096_ml3_spdrv0_t150` | — | 87.5, NaN in h11 (level 3) | dead | — |
| `D21_X1p829_L64_N128_ml3_spdrv0_t150` | — | 97.7, NaN in A11 (level 3) | dead | — |
| `D21_X1p829_L64_N192_ml3_spdrv0_t150` | — | 112.2, NaN in h11 (level 3) | dead | — |
| `opt-d90` | — | 400/400, finished 16:43 MSK | done | — |
| `opt-s0` | — | 400/400, finished 18:04 MSK | done | — |

N 96 / N 128 / N 192 all died mid-plunge (R_eq −24% / −27% / −30%; MOTS R settled ~3.49, not the classical 2.52). Onset later at higher N (−1% at t=58 / 67 / 81).

## Drainhole CMA queue

D0 finished 09:06 MSK. `opt-d30` finished 12:17 MSK. `opt-d80` finished 14:15 MSK.
`opt-d90` finished 16:43 MSK. The D30 screened rerun also finished. D40 passed and its evolution is running; D46 is live; D51 initial continuation failed.
`opt-s0` finished 18:04 MSK. Symmetric queue empty.

## Planned (nothing launches without the go)

Completed D30 protocol: 400 CMA-ES evaluations, seed 103, kink x0=(0.3,0,0,0),
at the same classical R_e/J and bounds. New bests get cheap equation checks
on 150x30, 180x36 and 210x42; only the finalist gets full Newton re-solves.
This replaces the earlier proposal to fully re-solve every new best, explicitly
confirmed on 2026-10-30. The coarse search and screened best remain provisional.
The final result requires all three grids PASS, last-two relative X drift <=1e-6,
Newton acceptance 1e-9 and independent constraints 1e-8. Failed screens penalize
CMA proposals; failed final refinement produces no validated best or evolution.
No radial stability penalty: that screen is under repair. D30 e0316 evolution is authorized on card 1, N128, checkpoints off. D0 e0211 is finished; no rerun or restart is authorized.

**Cost/necessity audit (22:30 MSK).** Evaluating the original e0374 polynomial
on 150x30, 180x36, 210x42 and 174x35 takes 0.6-0.8 seconds per CPU grid.
All five imposed equations are below 6.0e-9 in the existing monitored region;
both independent constraints stay below 2.0e-9. Full re-solving introduces
larger errors (up to E19=1.11e-4). This supports cheap screening first, not
calling interpolation a convergence study. e0391 still misses the 1e-8 gate
under interpolation (E19 up to 3.03e-8). The 3D N128 initial Hamiltonian norms
use different units/weights from these stationary monitors; their magnitudes
cannot justify dropping the latter's threshold. Audit records are packed in
`results/optimisation/validation/2026-10-30-resolution-audit/`.

D40/D46 had no saved candidates before this campaign; D51's old export is rejected.
The new validator reconstructs physical radii from fields and records stability
as unassessed. It never exports a failed background or fabricates a zero rate.

**Earlier D0/D30 validation outcome (21:43 MSK, 2026-10-30).** The original conditional
N128 launches are blocked; checkpoints remain off if subsequently cleared.
D0 at the matched radius already fails E19 on 150x30 (7.94e-5), despite
a Newton residual of 3.22e-13. The 180x36 solve stalls at 1.055e-9,
above the 1e-9 Newton acceptance threshold; no 210x42 solve was attempted.
D30 passes 150x30, then fails both finer grids: E19/E_c are
1.65e-6/4.89e-6 at 180x36 and 1.23e-5/3.02e-6 at 210x42
(gates 1e-8). Its tiny relative X drift (1.50e-9) does not override
these failures. No handoff was produced for either model. These checks
establish a failed numerical clearance, not its cause or physical stability.
These failed candidates were not evolved; the subsequent authorized scan
selects alternatives without changing the gates. Completed diagnostics,
fields, configurations and logs are packed in
`results/optimisation/validation/2026-10-30-d0-d30/` (under 1 MB),
using validator commit `e5b046d5`.

**Validator correction (22:14 MSK).** The validator previously demanded
Newton residual 1e-14 before accepting a stall below 1e-9. On D30 e0374,
those extra steps damage a field whose independent constraints already pass:
direct interpolation gives E19/E_c = 9.84e-10/1.61e-9 at 180x36 and
9.71e-10/2.00e-9 at 210x42, whereas the extra Newton steps raise them
above the gate. Stop Newton at the existing accepted 1e-9 tolerance;
the residual acceptance, independent 1e-8 constraints and 1e-6 X drift
are unchanged. A fresh full validator run must still clear the candidate
before any export/launch. Earlier rejected outputs remain archived as
numerical failures of that procedure, not evidence against the potentials.
Eight existing exploration/potential tests pass after this correction.
The fresh e0374 run still requires Newton updates on 180x36 and fails
E19/E_c at 3.19e-5/1.39e-5; 210x42 also fails. Stopping consistently
therefore does not by itself clear this candidate; it remains unexported.

**D0 alternative cleared (21:56 MSK).** Search e0211, ninth alternative
checked: X = 1.841676813964, J = 0, R_e = 3.889549398712 after consistent
similarity scaling. All three grids PASS; at 210x42 E19 = 1.11e-9,
E_c = 2.50e-9, relative X drift = 8.66e-15. Exported as
`D0_validated_2049x129.spinbg`; matched N128 launch at 21:57 MSK, using
`main3d_matter_16460fb0_2026-10-29.ex`. Full hold consumer, keep-last 3,
checkpoints off. This is background clearance only; stability is unassessed.
Seed, selected grid fields, checks and all attempted-candidate logs are packed
in `results/optimisation/validation/2026-10-30-alternatives/d0/`.

**D30 alternative cleared (22:21 MSK).** Search e0137: X = 2.184602703634,
J = 1.605934192814, R_e = 4.268787555383, matching the classical D30
control. All three grids PASS; at 210x42 E19 = 6.42e-10,
E_c = 4.60e-9, relative X drift = 4.22e-15. Selected after 30 initial
alternatives and nine further candidates; e0374's separate recheck failed.
Exported `D30_validated_2049x129.spinbg`, matched N128 launch 22:22 MSK
on the same matter binary and full hold profile as D0. Checkpoints off.
The selected candidate has higher X than the search minimum. Its evolution
was aborted at t = 0.54; a fresh resolution-gated search supersedes it. Selected fields,
seed and check logs are packed under
`results/optimisation/validation/2026-10-30-alternatives/d30/`; the first
batch and the oversolving diagnostic are in adjacent `d30_audit/`.

D51 X 1.606 triplet stays written, not launched. Its previous clearance is withdrawn.

**D21 comparison audit (2026-10-30).** Compare the recorded evolutions at
N = 128, the resolution used for D21 in the spinning instability figure.
Using its same fit of ln|dR_A/dt| over a 0.2–1% radius decrease gives
classical tau = 6.59223 (t = 39–46), potential tau = 9.49047 (t = 54–66):
a 30.54% lower measured growth rate. The new optimisation figure shows
this point on the classical curve; an optional second panel compares histories.
It replaces the standalone CMA-progress figure in the article. This is a
finite-resolution comparison, not a continuum rate or proof of an isolated
potential effect. Later onset under refinement occurs in both models;
that behavior alone does not invalidate comparison at the same resolution.

The settings choice is now traced: commit `0f2951fa` prepared a drive-off
D51 triplet; `0b80c60c` explicitly gave D21 the same outer-boundary setup as
spinning D51. The classical D21 reference retained drive strength 1.
Optimisation did not require this change. The spinning campaign's 10-18
notes favored drive off to reduce outer-boundary disturbances.

An existing controlled N96 test under `results/spinningwormhole/campaign/
drainhole/10_sponge_test/` changes only the drive and stop time relative to
the classical N96 reference. Through t = 55, the maximum areal-radius
difference divided by its initial value is 7.83e-7. Its fitted tau changes
from 7.8190406 (drive 1) to 7.8190341 (drive 0), and both reach a 1% areal-radius
decrease at the same sampled t = 42. Thus the sponge difference does not
explain the classical N96 growth fit; it is not a late-time validation for
the other resolutions or the potential background.

Classical D21 has J = 1, R_e = 4.05962747; the potential has J = 1.0138,
R_e = 4.06383050, inherited from the search reference `fam_a_r1_0000`.
Their binaries also differ (`farfix_891d817d` versus `matter_16460fb0`).
The explicit evolution settings otherwise agree apart from output paths,
background, checkpoint-off bookkeeping and stop time. Both have no imposed
perturbation, so numerical errors supply the initial disturbance. A controlled
collapse-time comparison would also fix that perturbation. For a stricter
rate comparison, use the same binary, drive and exactly matched R_e/J.
No new evolution was launched during that comparison audit. Second-node scratch rechecked:
47 MB cache only, 473 GB free; all three D21 logs have no checkpoint writes.

## Stationary extensions — 2026-10-30 (excluded from the paper)

Implemented and tested after push → cluster pull: positive degree-six Bernstein
potentials, amplitude-pinned canonical clouds, rotating clouds, fixed-area
shape and asymmetry. All retain physical J; the potential/matter arms retain
R_e, the shape/asymmetry arms retain area. No stability penalty or old-family
CMA restarts. **32 regression tests passed** on the node.

- **Confirmed fixed-area potential gain:** D21 X_A 1.8410621350 → 1.8383247213
  (−0.1487%); 150×30 and 180×36 pass the independent constraints, grid drift
  3.4e-13. Only Bernstein control b1 was increased; shape was allowed to respond.
- **Promising fixed-radius potential:** D21 X 1.8287958015 → 1.8207149850
  (−0.4419%). The new trial passes at both grids, but this batch's 180×36
  reference solve fails its constraints. The comparison remains provisional
  despite agreement with the previously audited 210×42 reference value.
- **Asymmetry:** gamma shifted by +0.1 suggests −1.84% at fixed area, but the
  fine trial fails E19 (1.8e-4); not a validated gain.
- **Ordinary/rotating bosons:** nonzero S0 clouds solve with mass 3 and amplitudes
  0.005/0.02; no lower bill in these trials. The S0 references and matter trials
  fail the independent-constraint gate, so no physical conclusion. D21's
  linear seed search finds no localized mode in both asymptotic mass gaps for
  the tested masses; this does not exclude finite-amplitude branches.
- **Reproducibility:** inputs, configurations, all trial records and fields are
  tracked in `results/optimisation/extensions/2026-10-30/` (about 5 MB).
  Code `5db53c14` introduced the tests; `15fbbf7c` improved the tail check and
  accepted Newton's observed 1e-9 floor while keeping independent gates at 1e-8.
  Jobs `opt-ext-{d21,s0}` and `opt-ext-{d21,s0}-r2` all finished normally.
- **Disposition:** retain the code and data as exploratory research; exclude
  these trials from the paper because the validated incremental gain is small.
  No follow-up extension runs are planned. Stability remains unassessed.
  Dzhunushaliev et al., PRD 90, 124038 (2014),
  is cited in the article; both LaTeX engines build and the in-place PDF is rebuilt.

## Validation audit — 2026-10-30

The findings below describe the original audit. Subsequent background-check
changes are recorded above; they have not repaired the instability screen.

- **Background equations and bill:** 27 package tests pass. The independent symbolic
  Einstein/KG transcription, V = 0 reduction and N-row identity pass. D21 e140
  reproduces X = 1.828795801462 on a fresh 210×42 GPU solve, with E19 1.7e-10
  and E_c 5.3e-10; denser quadrature changes X by less than 5e-14. Off-grid
  constraint residuals remain small. The additional 220×44 solve stalled;
  240×48 exceeded GPU memory, so this audit adds no finer-grid clearance.
- **Stability labels withdrawn:** `optimize_potential.py` and `stability_screen.py`
  pass the physical potential to grid-unit backgrounds without multiplying V,
  V′ and V″ by the static solution's sigma². Restoring this factor makes the
  S0 screen return positive growth λη₀ ≈ 0.80 through nx = 300. Its mode still
  has substantial unused-constraint residuals (tt ≈ 0.11, tη ≈ 0.044 at nx 300);
  this is not yet a verified physical instability, nor evidence that every winner
  is unstable. `growth_rate` treats no matched eigenvalue as `stable=True`, and
  the optimizer ignores the static background's constraint verdict. Both must
  return an unresolved result when their checks fail.
- **Acceptance and export:** finer-grid checking is a separate script, not an
  automatic gate before `best_clean`/`best_stable` are saved. `grid_check.py`
  exports ABOVE-GATE solutions and unconditionally writes `lam_eta0 = 0` without
  a stability calculation. The D51 `evolution/verified/*smoke_210x42.npz` is such
  a file: X = 1.6061750110, E19 = 1.13e-4 and E_c = 1.56e-5. It must not be
  used as a cleared background. Newer optimizer dumps also store grid-unit
  R_e/R_A/R_pol as though physical; the radii need sigma before hand-off metadata.
- **Next:** correct the potential scaling and unresolved-mode handling; gate static
  backgrounds and eigenmodes on their unused equations; remove fabricated zero
  rates; gate exports and enforce separate grid checks; then rerun stability
  validation. Code is unchanged by this audit. Logs are under
  `runs/capped_jobs/opt-audit-*` on the second GPU node.
- **Paper scope revised:** the updated tables distinguish nine search-grid minima
  from the selected D21 e140 210×42 solution. The old claims of eliminated
  radial instability, every model passing all four criteria, and sustained
  throat survival are removed. The appendix uses the final N96/N128/N192
  diagnostic streams, with measured early constraint orders and later
  resolution-dependent contraction. The new N128 rate comparison is
  descriptive; an exactly matched control remains deferred as noted above.
  The stability-code repairs remain pending.

## Article figures and tables — 2026-10-30

The article selection ledger is `results/optimisation/article/ledger_models.tsv`;
`research/optimisation/article/claims/claims.py` checks the selected raw trace
records, fine D21 field data, stream hashes and constraint orders, then generates
both tables and numerical macros. Search-grid rows use the same background-only
selection throughout; S50 is now X = 1.47714. D51 has no qualifying row. The
separate D21 search minimum is not the evolved candidate. The spin plot reads
the same ledger. The appendix figure uses blue/light blue/black and labels
refinement levels only once above the Hamiltonian/momentum columns. Its inputs
are packed under `results/optimisation/campaign/` for local rebuilding.
Both LaTeX engines build the article. The selection/stream checker
passes for ten table entries and forty constraint-order pairs; all revised
figure label audits pass. Tables I and II share aligned model rows, and the
S85 label is clear of its marker and the classical curves.

The readability revision explains the potential, Newton solve and CMA-ES
search in connected prose before the technical details. Detailed residuals
and contraction times are retained in the appendix; the main results lead
with their physical interpretation. Tables, figures and measured values are
unchanged. The shared writing standards now require this explanation-first
pass and a check for numerical clutter and repetitive prose.

## Main results

**Symmetric family, joint bill + radial-screen CMA-ES** (2026-10-28; search-grid
clean candidates, all stability labels withdrawn), vs classical V = 0:

| v_e | X | vs V = 0 | knobs (m, q₁, q₂, q₃) |
|---|---|---|---|
| 0 | 1.62676341 | −48.2 % | 1.198, 2.433, −0.046, 1.197 |
| 0.27 | 1.63372 | −45.4 % | 0.855, 3.232, 3.776, −0.256 |
| 0.50 | 1.47714 | −43.7 % | 0.962, 3.739, 0.922, −0.828 |
| 0.85 | 1.09759 | −24.9 % | 0.425, 2.438, 4.267, 0.445 |

Classical X: π / 2.99352 / 2.62527 / 1.46184. The v_e 0 search (2026-10-30, seed 111) frontier is 1.60271 (E19 5.6e-7); family 43 PASS, 142 FRONTIER. Not grid-checked. Frontiers at the three spins −47.8 / −45.6 / −27.0 %.
The v_e 0.50 selection now uses the background-only minimum (X 1.47714,
−43.7 %), replacing the old radial-screen-filtered X 1.49461. Bill-only Nelder–Mead was −32.0 / −35.4 / −26.2 %. Family-(b)
holds die at the far-side puncture at t ≈ 23, so these are not the 3+1 targets.

**Drainhole (the 3+1 family).** Classical spinning X: D21 4.64453, D51 3.39986,
D90 0.59955. Classical static (D0, J = 0) X 4.89835.
D0 CMA-ES (2026-10-30; kink x0, 400 evals, seed 101): search-best clean
X **1.83872766** (−62.5 % vs V = 0) at m 1.199, q (0.227, 0.485, 0.275),
E19 1.2e-10. Frontier 1.83854 (E19 7.9e-7). Family: 91 PASS, 54
FRONTIER (145 accepted npz). Not grid-checked.
D21 CMA-ES (pure kink start, 400 evals): search-best X 1.78483 (−61.6 %) did
not clear. Winner after the finer-grid check: e140 X **1.8287958015** (−60.6 %
vs $V = 0$) at m 1.023, q (0.672, 0.048, 0.310), 210×42 PASS, E19 1.6e-10.
Also clean: e5 X 2.357928 (−49.2 %). A new CMA best needs a separate finer-grid
re-solve before clearance; the optimizer does not enforce it. The 1e-8 cutoff
on the search grid is insufficient (the failed 1.785 was already 1e-10 there).
D21 area-pin + free-J CMA-ES (2026-10-30; 400 evals, seed 113, $J\in[0,4.13]$):
search-best clean X_A **1.78089377** (−62.0 % vs V = 0; −3.5 % vs the
4-knob D21 walk-in) at m 0.152, q (0.790, −1.199, 2.922), J 4.125,
$R_e/R_{\mathrm{pol}}$ 1.189, E19 1.2e-9. Frontier X_A 1.53867
(E19 8.2e-7). Family: 12 PASS, 146 FRONTIER. Not grid-checked.
D30 CMA-ES (2026-10-30; kink x0, 400 evals, seed 103): search-best clean
X **1.88040565** (−57.0 % vs V = 0) at m 0.740, q (0.607, 0.201, −0.664),
E19 1.3e-9. Frontier 1.84808 (E19 3.0e-9). Not grid-checked.
D80 CMA-ES (2026-10-30; kink x0, 400 evals, seed 105): search-best clean
X **1.10469483** (−22.2 % vs V = 0) at m 0.234, q (0.083, 0.504, 1.187),
E19 2.6e-10. Frontier 1.10396 (E19 1.1e-7). Family: 69 PASS, 72
FRONTIER. Not grid-checked. Classical V = 0 X 1.41924.
D90 CMA-ES (2026-10-30; kink x0, 400 evals, seed 107): search-best clean
X **0.787086131** (+31.3 % vs V = 0) at m 0.150, q (−0.337, 0.366, 0.445),
E19 8.7e-9. Frontier 0.78449 (E19 4.5e-8). Family: 71 PASS, 61
FRONTIER. Not grid-checked. Classical V = 0 X 0.59955. The kink search
did not beat V = 0.
**D51 clearance withdrawn:** the earlier smoke check reported X **1.6061738698**
(−52.8 %), unchanged to 4e-15 over 150×30 → 180×36 → 210×42, but both finer
rows took zero Newton iterations and were FRONTIER (E19 3e-8). The later
exported 210×42 file is ABOVE-GATE (audit above). Earlier D30 clean X 1.693
and D51 frontier X 1.505 also remain uncleared. Drainhole CMA queue is done.

**Potential landscape.** Not flat. Shape + rays at m 0.3: best clean −27.3 /
−26.9 / −20.6 % at v_e 0.27 / 0.50 / 0.85 vs V = 0; no bottom found (Newton or
the monitor ceiling stopped every ray). γ to −π costs ≈ +42 % at every spin.
The 4-knob optimizer then the joint CMA-ES produced the table above.

**Radial screen** (J = 0, m = 0; two-grid match; rotating 2D dropped). Drainhole
gate λη₀ = 0.3898 vs published 0.390. Classical symmetric Ellis λη₀ = 1.182.
The V = 0 drainhole gate reproduces 0.389823 in the audit. The potential-bearing
screen has the scaling and acceptance errors above; all previous zero rates
and the claim of no unstable mode up to nx 300 are withdrawn.

**Hand-off.** Seven-column table (B + `potential_coeffs`) and the kink potential
are in. N 96 / 128 / 192 t = 0 contract: Hamiltonian and momentum fourth order
after a derived-field Ham bug (plotfile `Ham` omitted V; fixed in
`main3d_matter_9c16a55b_2026-10-29.ex`). Validation holds to t = 1: throat
transfer improves with N, M to ≤ 1.2e-5, J to ≤ 1.2e-6.

## Steps

- [x] 1. Phantom unknown with a potential (V → 0 reproduces KK).
- [x] 2. Pin R_e and J; bill matches Fig. 3e; tidal gated. Transit/blueshift are not search gates; stationary comparisons measured below.
- [x] 3. Potential-only science run at three spins; landscape not flat.
- [x] 4–8. Dropped 2026-10-29 except the bare-field hand-off, which is done.
- [ ] Revalidate stability and exported backgrounds — **priority; see audit above.**
- [ ] 9. Evolve the winners. D21 X 1.829 triplet dead (N 192 NaN at t 112); D51 parked and uncleared.
- [ ] 10. Publish.

## Stationary mechanism and trade-offs — measured 2026-10-31

**Completed on CPU from saved D0 e0211, D21 e140 and D30 e0316 fields.**
Optimisation concentrates the scalar variation into a narrower region near
the throat. Total exoticity falls, but local NEC violation and peak tides
increase. This is a physical trade-off, not evidence that all measures of
traversability improve.

Each comparison fixes R_e, J and asymmetry to its exact massless reference.
The stationary D21 reference has J = 1.0138; it is not the J = 1 evolution
used in the growth-rate figure. D0 uses its analytic static reference.
No new search or GPU evolution was needed.

- **Mechanism:** X decreases by 56–62% across the three models. The proper
  width containing the central 90% of X is only 2–4% of the classical width,
  including both complete tails. Peak radial NEC violation rises by factors
  2.5–3.7. Angular gradients remain small; the violation forms a thin radial
  region rather than an equatorial ring.
- **Geometry and redshift:** throat areas differ by less than 0.6% at fixed
  R_e; the rotating throats become slightly less oblate. The interior lapse
  changes while the asymptotic redshift remains fixed by the asymmetry.
- **Tides and null NEC:** over proper distances ±10 R_e, the peak equatorial
  tidal eigenvalue at local speed v = 0.5 rises by factors 3.9–6.6. The
  magnitude of the complete equatorial null-ray NEC integral rises 33–42%,
  despite the smaller volume integral. Local NEC and ray integrals use
  different, explicitly recorded null-energy normalizations.
- **Light transit:** zero-angular-momentum axis/equator rays now have a
  separate flight-time calculation. Equatorial transit is 15–18% longer
  between proper-distance endpoints ±10 R_e, using the positive-infinity
  clock in both models. It is also longer at ±5 and ±20 R_e; the percentage
  depends on the endpoints. This is not a flat-space shortcut comparison.

Data, definitions, source hashes and reproducible commands:
[`results/optimisation/physics/README.md`](../../results/optimisation/physics/README.md).
The article now has a dedicated physics section, the blue/black
`mechanism_d21` figure, and a comparison table generated from
`article/ledger_physics.tsv`, with V=0 and optimized values side by side. The redundant `nec_distribution_d21` map and
`stationary_tradeoffs` plot were removed in both PNG and PDF form, and the
plotter no longer regenerates them. Numerical inputs stay under `physics/`,
not `figures/`. The text distinguishes the selected fine-grid D0/D21/D30
solutions from the earlier search minima and records the stationary trade-offs.

Checks cover radial/angular quadrature, profile sampling, physical scaling,
exact Ellis limits, independent drainhole transit and an independent
proper-distance check of D0 tides. The existing exact-limit tidal checks
pass. Archived D0/D30 grid comparisons agree, but those refinements accepted
interpolated fields without Newton updates: this is not an independent
continuum-convergence demonstration. D21 uses its selected fine-grid field.
**The instability screen remains unresolved; these diagnostics do not fix it.**
Add D40/D46/D51 after validated finalists exist. Tides along general
trajectories and time-dependent exposure during collapse remain separate work.

## Future directions

- **Oblate throat and free spin (in, opt-in).** `optimize_potential.py --pin area` holds $A$ so $R_e/R_{\mathrm{pol}}$ can grow; `--free-J` adds $J$ as a fifth CMA-ES knob. Defaults stay the published 4-knob $R_e$+$J$ walk. Still open: $\theta$-dependent scalar profiles / equatorial focusing so the NEC violation is a ring, not a shell.
- **Driving $X \to 0$.** Topological censorship forbids $X = 0$ in classical GR, but $X$ can be pushed arbitrarily small toward the thin-shell limit ($m R_e \gg 1$) on finer spectral grids (bounded only by Chebyshev resolution and Ford–Roman quantum inequalities), or cut further by restoring canonical / winding partner fields ($\chi, \Lambda$) to carry mass and angular momentum while the phantom pays solely for the throat flare-out.
- **Pins.** Throat size ($R_e$ or $R_A$) must stay pinned, otherwise the optimizer shrinks the throat toward a black hole. $J$ stays pinned to isolate the potential's gain at each $v_e$, unless `--free-J` is on.

## Rules

- Evolutions: nothing starts without the go; `nvidia-smi` first; no checkpoints
  unless asked; frames are never deleted.
- CMA-ES: a search-grid best is provisional until a separate finer-grid re-solve.
  The search-grid residual alone does not clear it. A missing or rejected mode
  is unresolved stability, never a zero growth rate.
- Solver jobs (if any) go through `capped_job.sh`. Code reaches the node through
  git (`myfork`, branch `feature/optimisation`).
- `develop` does not import this package.
