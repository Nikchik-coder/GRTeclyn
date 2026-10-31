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
were authorized (2026-10-31), checkpoints off for each. D51 authorization
was withdrawn at 11:03 MSK after its second initialization failure; it is
removed from both queues. The old D51 export remains rejected.

## Live

Checked **2026-10-31 at 15:22 MSK**. **The ordinary-boson pilot is running
on second/card 1; refinement diagnostics are running on second/card 0.**
D46's last evolution check remains the 15:01 snapshot below.
The October 31 instruction to continue exploration, run the required tests
and start the boson search supersedes the previous hold. Routine stationary
diagnostic and search choices are authorised without another confirmation.
No dynamical evolution is part of this extension; no AMR checkpoints.

`opt-boson-k0-t4-e1-20261031` started at **15:22:42 MSK** on second/card 1
after pulling `fd81f1d5` and confirming both cards idle. Case
`boson-k0-t4-e1`: canonical non-winding complex field, four-times-reference
tidal cap, ordinary-energy budget E_b/R_A <= 1, mass/amplitude seeds from
`studies/d21_fixed_area.toml`, 150x30 search and three-grid reference/finalist
validation, 200 CMA evaluations, seed 17. Four threads, 200 GiB virtual-memory
cap, 2 h timeout (**17:22 MSK**); measured ETA pending. Output:
`runs/optimisation/fixed_area/boson_pilot_20261031/boson-k0-t4-e1/`.
Logs persist under `runs/capped_jobs/opt-boson-k0-t4-e1-20261031/`.
The companion diagnostic will compare perturbed/unperturbed seeds and fresh
versus reused Jacobians. Acceptance thresholds remain unchanged.
Second-node scratch: 47 MB cache only; 476 GB free.

`opt-area-refinement-diagnose-20261031` started at **15:26:13 MSK**
on second/card 0 after pulling `922a93a7`; all 162 optimisation tests pass.
It independently tests candidate 00071 on 150x30, 180x36 and 210x42 with
unperturbed and perturbed seeds and fresh versus reused Jacobians. Four
threads, 200 GiB cap, 1 h timeout (**16:26 MSK**). Output:
`runs/optimisation/fixed_area/diagnose_20261031/`.
Newton histories, damping, Jacobian counts and exit reasons are now recorded.
The boson reference passes all three grids; its first finite-amplitude seed
stalled, and the remaining mass/amplitude seeds continue. Both cards are busy.
No extra scratch plotfiles or AMR checkpoints are produced.

The first refinement diagnostic finished normally: interpolation passes all
three grids, but correcting the fine-grid equations can degrade the unused
constraints; refreshing every Jacobian does not resolve it. This points to
numerical solve behavior, not a demonstrated new physical branch failure.

`opt-area-derivative-check-20261031` ran on second/card 0 from 15:31 MSK,
code `163dde5e`, four threads, 200 GiB, 30 min cap. It completed normally.
Removing linear backgrounds from derivative evaluation reduces cancellation
in a manufactured test (164 tests pass), but the 180x36 solves still fail the
unchanged constraints. Output: `runs/optimisation/fixed_area/derivative_check_20261031/`.
It is a numerical improvement, not a repair of the full refinement failure.
The next diagnostic inspects the LU correction and the largest residual rows.

The boson pilot has produced numerical nonzero-field solutions, not physical
clearance: one is bound and localized but has E_b/R_A = 3.015 (limit 1) and
E19 = 6.43e-6. More seeds and the CMA stage continue; no accepted winner yet.

D30 finished at t = 100 (exit 0) at 13:44 MSK. D51 remains removed from
both queues.


D40 reached t = 100 at **14:50:40 MSK**, with normal AMReX finalization and
no NaN in its log; its consumer processed the final plotfile. All four
evolution diagnostic streams are finite. Final global Ham/Mom norms are
2.667e-3/8.950e-4, so reaching the selected endpoint is not a stability or
continuum-accuracy claim. Seven streams, parameters, final logs and hashes
are archived under `results/optimisation/completed/2026-10-31/d40/evolution/`.
The three remaining scratch plotfiles (7.1 GiB) were pruned after archive
verification; no checkpoints or queued restart need them. Frames and slice
caches remain; cleanup is logged in the October 31 scratch manifest.

The t4 pilot ended at **14:57:38 MSK**, exit 2, after 972.8 s and
**88/200 CMA proposals**. Ten candidates passed the search-grid gates; all
ten failed the independent three-grid refinement on stationary constraints.
Search-best full exoticity was 2.188430 versus reference 4.684238, but
**no winner is validated**. The smaller search-grid residuals and almost
unchanged objective do not clear the finer-grid unused Einstein equations.
The exact CMA stop reason was not logged. Full fields, evaluations and
refinement diagnostics are archived under
`results/optimisation/validation/2026-10-31-area-t4/`.
Before more production cases, diagnose the perturbed refinement residuals
and Newton stopping accuracy. The remaining matrix stays queued; no
automatic launch is scheduled. Stability remains unassessed.

`opt-d21-area-t4-pilot-20261031` started at 14:41 MSK on second/card 1,
code `368a445b`, after checking the card was idle. This is the next queued
potential-only pilot: the same area/J/gamma, 150x30 search, seed 7,
200-evaluation cap and three-grid reference/finalist checks, with the
configured four-times-reference tidal cap. Four threads, 220 GiB address-space
limit and 2 h timeout (16:41 MSK); measured completion ETA pending.
Output: `runs/optimisation/fixed_area/pilot_t4_20261031/potential-t4/`.
The t2 candidate 00014 cleared stationary, surface and off-grid checks but
had tidal peak 0.07220 versus its cap 0.06425; it is inside the t4 bound.
This motivates testing the already-queued t4 case, not changing t2's gate.
No evolution plotfiles, AMR checkpoints or consumer are involved.

`opt-d21-area-t2-pilot-r2-20261031` started at 14:34:54 MSK after pulling
surface fix `368a445b`. The same potential-t2 settings and resource caps
are used; output is `runs/optimisation/fixed_area/pilot_r2_20261031/`.
The massless reference passed all three grids. The retry ended at
**14:37:58 MSK**, exit 2, after 181.6 s and **16/200 CMA proposals**:
`no_validated_improvement`. Including the re-pinned existing candidate,
14 rows fail stationary constraints, one fails the tidal cap and two fail
potential positivity. Typical proposals cost 5–9 s; the first cost 23 s.
The re-pinned old D21 seed has E19 = 5.96e-5 against the unchanged 1e-8
limit, despite a small Newton residual. This is not a validated improvement.
The all-infeasible population terminated early; assigning every rejected
solution the same score gives the search no direction toward feasibility.
The exact CMA stop dictionary was not recorded. Before expanding the matrix,
check the rejected seed's unused equations across resolution and provide
constraint-sensitive search scores, retaining the hard final acceptance gates.
The queued t4 pilot has also finished without a validated winner; other cases are not scheduled automatically. Output, fields and
checks (2.9 MB) are archived in
`results/optimisation/validation/2026-10-31-area-pilot/`.
The surface fix passed 29 study tests and all three saved reference regressions.
The original failed attempt stays below.

`opt-d21-area-t2-pilot-20261031` started at 14:29:37 MSK on second/card 1,
after pulling `c604af3f` (study implementation `2ad280e7`) and checking the
card was idle. The authorised first pilot is `potential-t2`: true minimal
area and J fixed, tidal cap twice the matched reference, 150x30 search,
200 CMA evaluations, seed 7, Jacobian chunks 512; reference and finalist
refinement use 150x30, 180x36 and 210x42. Capped runner: four threads,
220 GiB virtual-memory limit, 2 h hard timeout at **16:29 MSK**. This is a
time limit, not a measured completion ETA; reference validation starts first.
Persistent output: `runs/optimisation/fixed_area/pilot_20261031/potential-t2/`.
Stationary fields and diagnostics are saved; this job creates no evolution
plotfiles or AMR checkpoints. No consumer is needed for stationary solves.
The pilot ended at 14:30:26 MSK (exit 2), before any CMA proposals:
150x30 passed, while 180x36 and 210x42 rejected an unresolved extra-start
minimal-surface minimisation. Newton and the independent background residuals
passed; the saved graph has a tiny area gradient and positive Hessian.
The surface failure was repaired and the reference cleared in the retry above.
The remaining potential cap (1) and bosonic cases await a functioning
feasible search; no acceptance threshold has been relaxed.

Surface-gate diagnosis: the auxiliary SLSQP starts reported success on
area stagnation but left normalized gradients 8.7e-7 (180x36) and 8.8e-6
(210x42), above the unchanged 1e-7 gate. The candidate graph itself had
gradient below 5e-13 and positive Hessian. A bounded Newton polishing step
now requires decreasing gradient, positive curvature, interior feasibility
and no resolved area increase; final gate thresholds are unchanged. The
saved three-grid reference passes with this fix. Failure fields, original
checks and the corrected surface checks are archived under
`results/optimisation/validation/2026-10-31-area-reference/`; the 180x36
case is a regression test. The original failed pilot is preserved.

D30's four evolution diagnostic streams are finite through t = 100; its
consumer processed the final plotfile. Reaching the chosen stop time is
not a stability or late-time accuracy claim: final global Ham/Mom norms
are 4.45e-3/1.49e-3 and the throat is contracting. Seven diagnostic streams,
parameters, final log and source hashes are archived under
`results/optimisation/completed/2026-10-31/d30/evolution/` (1.5 MB).
The three finished scratch plotfiles (7.1 GiB) were removed after archiving;
frames, slice caches and movies remain. No checkpoints or queued restart
need this run. Cleanup is logged in the October 31 scratch manifest.

Scratch checked at 15:01 MSK: first node 7.2 GB used / 620 GB free,
with three D46 plotfiles and no checkpoints. The second node's 7.1 GiB
of completed D40 plotfiles was subsequently pruned; only its 47 MB cache
and empty run directories remain (476 GB free). Earlier startup observations
below retain their measurement times.

D30 evolution result (2026-10-31): the fixed 0.2–1% areal-contraction
fit gives tau = 11.873070 (t = 70–83), versus classical tau = 8.314535
(t = 42–50), a 29.97% lower growth rate at N128. The first sampled 1%
contraction occurs at t = 84 versus 51; 5% at 99 versus 64. The potential
run ends with a 5.76% areal-radius decrease at t = 100. Common evolution
parameters agree; only background and deployment paths differ, with explicit
checkpoint-off keys added. Initial equatorial radii differ by 0.00033%.
The figure uses the evolved e0316 field's own stationary throat area for J/A.
This is a finite-resolution contraction-rate comparison, not proof of
stability or a continuum rate. Band sensitivity remains: using 0.3–2%
gives tau = 10.209 versus 8.431 (17.42% lower rate); the figure retains
its original common 0.2–1% definition. D30 is now included in the growth
figure and its checked numerical table.

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

D46 search `opt-d46-resolution-cma-r2` completed all 400 evaluations at
10:44:46 MSK, exit 0. Winner e0065 passes 150x30, 180x36 and 210x42:
X = **1.699350508660**, versus V=0 **3.720579504338** (54.33% less).
Final E19/E_c = 5.58e-9/2.53e-9; R_e = 4.882163848839 and
J = 3.154107711925 match the classical D46 reference. Refinement required
zero Newton updates; physical stability remains unassessed. Completed search
fields, trace, screen/refinement diagnostics and job provenance are archived
in `results/optimisation/completed/2026-10-31/d46/` (5.2 MB, 49 files plus
hash manifest); field finiteness, refinement metadata and archive hashes pass.

D46 `D46_cma20261031_L64_N128_ml3_spdrv0_t150` launched at 11:04:34 MSK
on first/card 0, checkpoints off. Shared checkout pulled `bf11c922` before
launch. Exported the validated 210x42 fields to a 2049x129 seven-component
potential background, with read-back verification. Template diff against the
exact classical D46 run changes only background/deployment paths and explicit
checkpoint-off keys. N128/L64/ml3, drive 0, dt multiplier 0.02, stop t = 150,
plot interval 100; matter binary 16460fb0. Full preflight and 14-field hold
consumer, keep-last 3. Full preflight passed and all 14 initial fields
rendered. Initial R_eq = 4.88266 versus spectral 4.88216 (0.01%); potential
coefficients are read by the evolution. The initial chi frame was compared
visually with the matched classical image (different zooms); both are centered
and nonblank. All 14 frame-zero fields and throat/MOTS/wave diagnostic rows
are saved. The first consumer pass took 456 seconds, but the next pass reused
the surface (two Newton iterations) and took 178 seconds, below the measured
198-second plot interval. The startup backlog is shrinking; keep-last pruning
has run, leaving three plotfiles. Consumer check passes, with no duplicate or
backwards rows. At 11:17 MSK: t = 3.43 / 150, about 18.1 units/h, provisional
ETA 8.1 h (19:23 MSK). GPU allocation about 23 GiB; no checkpoints.


D51 retry `opt-d51-resolution-cma-r2` ran on first/card 0 from 10:44:50
to 10:56:17 MSK, exit 1. Even with 60 mass increments, 48 Newton iterations
and 24 bisections per leg, the initial continuation stalled at the m = 0.005
endpoint (residual 8.4e-7, line-search stall). No CMA evaluations or winner.
This is a stationary initialization failure, not measured instability.
D51 was removed from the search and evolution queue by explicit instruction
at 11:03 MSK. The detached controller has exited; a STOP marker and cancellation
record are saved in `runs/optimisation/queues/d51_retry_after_d46_20261031/`,
and D51 was removed from `matched_20261031.json`. Its failed logs remain.

D40 `D40_cma20261031_L64_N128_ml3_spdrv0_t100` started at 09:49:56 MSK,
second/card 0, checkpoints off. Its 2049x129 background was exported from
the validated finalist. The template was compared with the exact classical
D40 run: only background/deployment paths and explicit checkpoint-off keys
differ. Numerical controls remain N128/L64/ml3, drive 0, dt multiplier 0.02,
stop t = 100 and plot interval 100. Same matter binary 16460fb0, full 14-field
hold consumer, keep-last 3. Full preflight passed with all 14 fields rendered;
initial R_eq = 4.58284 versus spectral 4.58356. At 11:16 MSK t = 28.74,
about 20 units/h, ETA 3.6 h (14:50 MSK). GPU memory 22.4 GiB.
The initial chi frame was visually compared with the classical frame (the
saved images have different zoom widths); both are centered and nonblank.
All 14 frame-zero fields and throat/MOTS/wave rows are present. The first
consumer pass took 157 seconds from plot Header to diagnostic rows, within
the roughly 180-second plot cadence; subsequent horizon searches can warm
start. Keep-last 3 is active, with three plotfiles present. D46 is evolving;
D51 has been removed from the queue. These runs start from stationary fields;
no queued evolution requires a restart checkpoint.

Run `D30_e0316_L64_N128_ml3_spdrv0_t100` uses the validated e0316
210x42 background exported to 2049x129. Diff against the previous D30
template changes only the background and run paths: N128, L64, max_level 3,
drive 0, dt multiplier 0.02, stop t = 100, plot interval 100. Checkpoints off;
full 14-field hold consumer with keep-last 3. Same matter binary (16460fb0).
Code/results pushed as `00ac13e3`, pulled on the node before launch.
Full preflight passed; frame 0 compared against the old D30 image, all 14
fields rendered, throat/MOTS/wave rows present. Consumer keeps up and prunes
to three plotfiles. At 11:16 MSK: t = 50.83, about 20 units/h, ETA 2.5 h
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

Scratch in the supplied 11:56 MSK check: first node 7.1 GB used, about
624 GB free; second node 14.2 GB used, 456 GB free.
Three plotfiles per evolution, no checkpoints or finished-run
scratch leftovers. All three GPUs are occupied; D51 has no queued work.
Deleted only the finished D0 and aborted D30 plotfiles (9.5 GB); no checkpoints.
Cleanup recorded in the October 31 scratch manifest.
Frames, slice caches and movies are retained on persistent storage.

| run | card | t | speed | ETA |
|---|---|---|---|---|
| `opt-area-refinement-diagnose-20261031` | second / 0 | three-grid diagnosis | measuring | hard timeout Oct 31 16:26 MSK |
| `opt-boson-k0-t4-e1-20261031` | second / 1 | reference and seed search starting | measuring | hard timeout Oct 31 17:22 MSK |
| `opt-d21-area-t4-pilot-20261031` | second / 1, finished | 88 proposals; 10 search-grid passes, no validated finalist | exit 2; 972.8 s | finished Oct 31 14:57 MSK |
| `opt-d21-area-t2-pilot-r2-20261031` | second / 1, finished | reference PASS; 16 proposals, no accepted candidate | ended, exit 2; 181.6 s | Oct 31 14:37 MSK |
| `opt-d21-area-t2-pilot-20261031` | second / 1, superseded by r2 | reference_failed; no CMA evaluations | ended, exit 2 | Oct 31 14:30 MSK |
| `D30_e0316_L64_N128_ml3_spdrv0_t100` | second / 1, finished | 100 / 100, exit 0 | 20.0 units/h | finished Oct 31 13:44 MSK |
| `opt-d40-resolution-cma` | second / 0 | 400/400; three-grid PASS | done | ended Oct 31 09:43 MSK |
| `D40_cma20261031_L64_N128_ml3_spdrv0_t100` | second / 0, finished | 100 / 100; normal finalization | 19.97 units/h | finished Oct 31 14:50 MSK |
| `opt-d46-resolution-cma-r2` | first / 0 | 400/400; three-grid PASS | done | ended Oct 31 10:44 MSK |
| `D46_cma20261031_L64_N128_ml3_spdrv0_t150` | first / 0 | 71.20 / 150, alive | 18.13 units/h | 4.35 h; Oct 31 19:22 MSK |
| `opt-d46-resolution-cma` | first / 0 | CUDA pool startup failure, no evaluations | ended | exit 134 |
| `opt-d51-resolution-cma` | second / 0 | initial continuation failed; no CMA evaluations | ended | exit 1, Oct 31 09:45 MSK |
| `opt-d51-resolution-cma-r2` | first / 0 | initial continuation failed; no CMA evaluations | ended | exit 1, Oct 31 10:56 MSK |
| D51 search and evolution | — | removed from queue; no retry authorized | cancelled | Oct 31 11:03 MSK |
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
`opt-d90` finished 16:43 MSK. The D30 screened rerun also finished. D40 passed and its evolution finished at t = 100; D46 passed and its evolution is running; D51 failed initialization again and is removed from the queue.
`opt-s0` finished 18:04 MSK. Symmetric queue empty.

## Planned (nothing launches without the go)

### Queued stationary studies — fixed area and bosonic matter

**Implementation is complete; production studies are queued, not launched.**
The infrastructure passed 158 tests and CPU solve/save/refinement/resume
checks; see [implementation and measured pilot costs](#implementation--fixed-area-studies-2026-10-31).
The first potential pilot was authorised and run on October 31 (Live above).
The queued t4 pilot finished without a validated finalist under the October 31 go;
expanding the matrix awaits a validated pilot and the feasibility diagnosis;
freeing a card does not trigger an automatic launch. No evolution restart
checkpoints are needed for these stationary studies.

1. **D21 reference and fixed-area pilot.** Re-solve the matched massless
   reference with the true minimal throat area, fixing its area, total J and
   asymmetry gamma. Re-pin existing potential candidates to those same
   constraints. Measure wall time and memory, verify the throat is a local
   minimum, and perform independent finer-grid re-solves before expanding.
2. **Potential-only searches:** `potential-t1`, `potential-t2`,
   `potential-t4` in [the study configuration](studies/d21_fixed_area.toml).
   Test whether the full phantom integral, including angular gradients,
   decreases at fixed true area/J/gamma while the maximum tide remains below
   1, 2 or 4 times the matched massless value. Check both ends, all latitudes
   and traveller speeds 0, ±0.5; retain the massless reference as the control.
3. **Mass-only boson pilot, then the 27-case matter matrix:** winding
   k = −1, 0, +1; ordinary-energy budgets E_b/R_A ≤ 0.1, 0.3, 1;
   the same three tidal caps. Test whether canonical bosonic matter reduces
   the phantom integral relative to the matched zero-boson search at the
   same tidal cap. The k = 0 control isolates the benefit of rotation.
   Solve the frequency and require decay at both ends; try linear modes,
   then finite Bondi-profile seeds and amplitude continuation. Record
   ordinary energy separately from asymptotic masses and phantom accounting.

Expand the matrix only after the pilots establish validated solutions and
measured costs; production durations are not yet estimated. Acceptance
requires independent Einstein/scalar checks, true-area and total-J accuracy,
resolved tidal peaks, energy budgets and converged objective quadrature.
Finalists require actual Newton updates on finer grids, with the existing
1e-8 independent-constraint and area gates, 1e-6 J gate and 1e-6 objective-drift
gate. Interpolation alone remains screening. No new exoticity reduction or
nonzero bosonic wormhole has yet been validated by this implementation.
Q-ball self-interactions, multiple throats and dynamical stability remain
later studies; these searches test stationary trade-offs.

### Existing D30/D40/D46 protocol and validation history

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

## Contraction delay and D40 growth — 2026-10-31

The N128 D40 potential run contracts: areal radius decreases 2.539% by
t = 100, versus 30.211% for the classical run. Equatorial and polar radii
also decrease. It is not on the expanding branch. The common 0.2–1%
radius-deficit fit gives tau = 11.07058 versus 13.27262 classically,
a 19.89% higher growth rate despite later contraction.

The new single-panel `contraction_delay` figure compares the time to first
1% contraction, interpolated between saved samples, with no time shifts.
Classical / potential times are D0 43.77 / 60.31, D21 46.77 / 66.85,
D30 50.99 / 83.07, D40 58.72 / 89.42. Its checked table is
`results/optimisation/article/contraction_delay.tsv`; the script is
`visualisation/optimisation/plot_contraction_delay.py`.
All four reach the threshold later; this does not mean all have smaller
growth rates or establish a continuum delay. D21 retains its spin/damping
mismatch. The paper now separates delay from rate and includes D40 in the
rate figure. Both LaTeX engines build; 24 threshold times, ten growth fits
and the label audits pass.

Follow-up searches were authorised, then held by the subsequent wait.
The interrupted call had already started `opt-d21-strict-refine-20261031`
on second/card 0, code `9fa71204`, four threads, 220 GiB, 30 min cap.
It completed at 15:10:17 MSK, exit 2: candidate 00071 still failed the
strict refinement. Output: `runs/optimisation/fixed_area/strict_refine_20261031/`.
The new 1e-14 perturbed-solve target retains every acceptance threshold;
its cause needs further diagnosis. No further search was launched.
At the post-interruption check both second-node GPUs were idle.

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

**Priority agreed 2026-10-31: fixed-area searches with bounded tides, followed
by rotating ordinary bosonic matter.** The stationary comparisons above show
why lowering the volume integral alone is insufficient: peak violation,
tidal forces and null-ray NEC deficit can increase while $X$ decreases.

- **Fixed area, bounded tides.** Minimise the full-direction phantom integral
  $X_{\rm full}=\int |D\Psi|^2 dV/(4\pi R_A)$ at fixed
  throat area, with explicit tidal bounds at specified local speeds and
  monitored passage width, lapse, redshift and light transit. Hold $J$ fixed
  for comparisons that isolate the potential's effect; explore $J/R_A^2$ and
  the asymmetry $\gamma$ separately or jointly with the potential. The current
  `optimisation.commands.optimize_potential` retains legacy `--pin area`
  (constant-eta surfaces) and `--free-J`. The new study configuration below
  fixes the true minimal area and uses explicit reference-relative tidal caps.
- **Shape and angular distribution.** The stationary solver already allows
  angular dependence. Let throat shape respond to the matter and boundary
  parameters through the field equations. Monitor angular as well as radial
  NEC violation so a smaller radial objective cannot hide a redistribution
  into angular gradients. Richer positive potentials are another available
  knob; the small validated extension gain is recorded above.
- **Rotating ordinary bosonic matter.** Use a canonical complex field with
  harmonic time dependence and azimuthal winding. Vary its amplitude, mass,
  self-interaction and integer winding number; solve for the frequency and
  require localisation at both asymptotic ends. Compare at matched area and
  total $J$, tracking the phantom contribution separately from the ordinary
  matter and its mass budget. Cloud and winding equations already exist,
  but the preliminary trials establish no validated exoticity reduction.
  Related stationary solutions: [Hoffmann et al. (2018)](https://arxiv.org/abs/1803.11044).
- **Double throats, later.** Bosonic matter can support two constrictions
  separated by a wider region within the same two-ended geometry. Assess
  both constrictions and the complete exoticity integral. Separate wormhole
  handles require a different topology and solver construction; neither
  extension is known here to lower the total requirement.
- **Scaling and momentum.** For geometrically similar solutions, local
  stress scales as $R^{-2}$, $|\mathrm{VIQ}|$ as $R$, and $X$ is unchanged.
  Similarity with a potential also requires $m\propto R^{-1}$; fixing the
  physical scalar mass breaks that scaling. The stationary phantom has
  $\Pi=0$ and zero momentum density, while its gradients supply stress.
  Nonzero spacetime angular momentum is compatible with the two-ended
  geometry; a winding bosonic field adds actual matter angular momentum.
- **Arbitrarily small $X$ is a conjecture.** No validated sequence establishes
  $X\to0$ in this smooth scalar family while preserving a finite traversable
  throat and bounded tides. Thin-shell arguments and topological censorship
  do not establish that limit for this family. Finer grids can resolve thinner
  structure, but do not by themselves demonstrate physical admissibility or
  stability. Any proposed gain still needs independent background checks and
  finer-grid re-solves; dynamical stability remains a separate question.

### Implementation — fixed-area studies (2026-10-31)

Infrastructure implemented; **the D21 potential-t2 GPU pilot cleared the reference
but ended without a feasible candidate; the t4 pilot also finished without
a validated finalist (Live above). The production matrix and mixed-field evolutions have not launched**. Configuration:
[`studies/d21_fixed_area.toml`](studies/d21_fixed_area.toml); commands and
definitions: [package README](../../grteclyn-wrapper/src/grteclyn_wrapper/optimisation/README.md#fixed-true-area-bounded-tides-and-massive-bosons).

- The minimal-surface graph joins the Newton solve. Independent higher-order
  minimisation checks the area and Hessian; multiple or unresolved graph
  throats are rejected. The full phantom objective includes angular gradients.
- Tidal factors are **1, 2, 4** relative to the matched massless reference,
  sampled across latitude and both ends at local radial speeds **0, ±0.5**.
  Peak refinement, an axis limit and decaying-tail checks gate acceptance.
- Mass-only bosons use **k = −1, 0, +1**, energy budgets **E_b/R_A = 0.1,
  0.3, 1**, mass range **m_b R_A = 0.5–8** and amplitude seeds **0.01, 0.03,
  0.1, 0.3** (upper bound 0.5). Frequency is solved, with both-end mass gaps
  and localisation checks. Failed linear-mode searches still attempt finite
  seeds from Bondi's positive self-gravitating mass-only ODE profiles, on
  both the massless background and re-pinned potential candidates.
- `--study-config` lists the 30 cases without solving; `--study-case` selects
  one. Saved source/code hashes protect `--resume`. Search and final
  refinement share the physical gates; separate reference and candidate
  archives, rejection reasons and rebuildable comparison plots are retained.
- Mixed-field saves/refinement preserve the field, frequency and throat
  shape. Total-J checks include the matter source; SPINBG_V1 export refuses
  canonical fields. Direct off-grid Ricci and scalar checks supplement the
  unused Einstein constraints. Perturbed finer-grid seeds must undergo actual
  Newton updates before certification. Stability remains unassessed.

Validation: the optimisation suite passes **158 tests**. A capped CPU Ellis
12×6 solve plus the full acceptance diagnostics took **13.2 s**; a complete
8×4 → 10×5 → 12×6 command/save/refinement/resume smoke test took **85.4 s**
and correctly reported no exoticity improvement. The actual Bondi ODE seed
adapter at canonical amplitude 0.1 took **13.7 s** and returned a finite,
localised seed. These are infrastructure checks, not D21 cost estimates or
validated nonzero bosonic wormholes. Next: separately authorised, capped D21
reference/potential pilots; measure their costs before the production matrix.

## Rules

- Evolutions: nothing starts without the go; `nvidia-smi` first; no checkpoints
  unless asked; frames are never deleted.
- CMA-ES: a search-grid best is provisional until a separate finer-grid re-solve.
  The search-grid residual alone does not clear it. A missing or rejected mode
  is unresolved stability, never a zero growth rate.
- Solver jobs (if any) go through `capped_job.sh`. Code reaches the node through
  git (`myfork`, branch `feature/optimisation`).
- `develop` does not import this package.
