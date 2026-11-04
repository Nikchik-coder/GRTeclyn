# Ring spacetimes and spin transport — status

Updated **2026-11-04 (MSK)**. Branch: `feature/optimisation`.

The minimal-exotic-matter wormhole optimisation campaign remains paused.
This separate regular-centre scalar-ring study reuses its JAX/Newton core.
**The stronger-ring timing audit, concentric gapped field recovery and
between-ring particle experiment are complete and accepted.** Every original
physical acceptance limit is unchanged. Earlier failed studies remain rejected
in their immutable archives.

**The omega=0.70 single ring has now been interpolated onto Cartesian
GRTeclyn grids and evolved in full 3+1.** The three-resolution Richardson
study through t=2 is complete; no long-time stability claim. See [EVOLUTION.md](EVOLUTION.md).

## Live and queue

**LIVE: `railgun-ergo372-origin-recovery-r2-resume-20261104`**, card 0,
started **08:47:13 MSK**, source `86f491c52`. GPU regressions, then only
the unfinished 288x36 solve, reusing the two passing grids byte for byte,
then the unchanged centre certificate. Same three-grid budget and original
**09:38:51 MSK deadline** (remaining cap 0.861 h at launch); checkpoints OFF.
No evolution time/speed yet; ETA awaits the finest solve and certificate.
Card 1 idle. Scratch clean: **4 KiB / 329 GB free**.

**Earlier process interrupted by GPU memory allocation**,
`railgun-ergo372-origin-recovery-r2-20261104`, card 0,
**08:38:51–08:42:14 MSK**, source `2c79ccec7`, exit 1.
All **69 GPU regressions passed**. Both 224x28 and 256x32 passed all
physical checks; each converged in two updates (1.28e-15 / 2.55e-15).
The rounding fix is GPU-confirmed. The first 288x36 LU factorisation
failed to allocate another 21.31 GiB; **zero finest-grid updates** occurred.
The two passing fields are preserved. Fixing matrix lifetime/donation and
preparing continuation of only the unfinished third solve; no extra physical
candidate or changed tolerance. The original one-hour deadline is
**09:38:51 MSK**. Centre qualification and evolutions remain pending.
Both cards idle. Scratch clean: **4 KiB / 329 GB free**.
Memory repair: release the previous LU before the next Jacobian, release the
unscaled Jacobian before factorisation, and donate the scaled matrix buffer
to CUDA LU. No equation, matrix entry, precision or tolerance changes.
Twenty-three targeted CPU checks pass. Resume support accepts only an
identical configuration, two passing saved grids and zero updates on the
unfinished third grid; it copies/hashes the retained evidence. It refuses
rejected grids, changed tolerances and any saved third-grid state.
Continue only 288x36 under the existing go, then the unchanged centre check;
retain the original 09:38:51 MSK deadline and all original evidence.

**Earlier recovery stopped rejected** on card 0,
**08:21:47–08:25:17 MSK, November 4**. All **55 GPU regressions passed**.
224x28 passed; 256x32 passed the physical equation and origin checks but
Newton stalled at **2.93e-14**, above its unchanged **1e-14** target.
The run stopped before 288x36 and the centre certificate, as required.
No exports, preflights or evolutions started. Both cards are idle.
Scratch clean: **4 KiB retained / 329 GB free** (08:31 MSK).
[Recovery evidence](../../results/railgun/studies/ergo372-origin-recovery-20261104/).
**Numerical fix prepared, GPU qualification pending.** Subtract the fixed
lapse target before averaging, and subtract a reference angular value before
forming the origin isotropy rows. Both equations and their Jacobians are
unchanged mathematically. Compiled arithmetic on CPU reproduced a nonzero
old border for equal values; the new form returns exact zero and resolves
one-ulp offsets. CUDA reproduction/recovery remains to be checked.
Newton now records its worst equation, raw residual and row scale.
All **45 targeted local checks passed**, including source/export contracts,
small-device boundary/Jacobian tests and refusal to launch on a busy card.
The evolution launcher now checks card occupancy before preparing data.

[Read-only interpolation audit](../../results/railgun/reports/ergo372-origin-roundoff.json)
shows the corrected 256x32 state reduces the origin f angular spread from
9.41e-14 to exact zero and the interpolated N radial slope coefficient from
1.14e-9 to 1.21e-15. These are diagnostic improvements, not a curvature pass.
The saved 256x32 state remains rejected. Rebuild this audit with
`grteclyn-wrapper/scripts/campaigns/railgun/audit_origin_interpolation.py`.
Prepared rerun: `grteclyn-wrapper/scripts/campaigns/railgun/run_origin_recovery.sh`,
card 0, fresh directory `ergo372-origin-recovery-r2-20261104`; regressions,
at most three 224x28 / 256x32 / 288x36 solves and the radius-0.08,
degrees-12/14 certificate. Same 30 iterations, minimum two updates, fresh
Jacobians, 1e-14 Newton target and all physical gates; stop on rejection.
Four threads, 160 GiB, one hour total, chunks 128, checkpoints OFF.
Renewed run-specific go granted November 4; the corrected recovery was interrupted as above.

**Preferred first evolution target: accepted shift/lapse 3.720789536602**,
following the request to use a less compact ring. Source:
`results/railgun/studies/ergoregion-max-validate271/finalists/01/accepted.npz`,
SHA256 `dea15224bb7e97be5a1d8528a828886b6ba3e4cbf3c8cae66d88abc8cf4207cd`.
Its three stationary grids pass and g_tt is positive. Matter peaks at
coordinate radius 0.234 instead of 0.165 for the 5.23 source; minimum
lapse is 0.118 instead of 0.089. Easier evolution remains a hypothesis.
A fresh Cartesian-origin check is required before export. The prepared
substitution keeps L_full=64, max_level=6, N=96/128/192, card assignment
0:(96,128), 1:(192), t=50 and checkpoints OFF. The centre check uses
radius 0.08 and degrees 12/14, with the unchanged 1e-8 limits.
**Centre qualification COMPLETE, REJECTED**, job
`railgun-ergo372-core-20261104`, first two-GPU node/card 0,
**08:09:37-08:16:01 MSK, November 4**, source `e3ddfc860`, exit 2.
All **41 GPU regressions passed**. Einstein/scalar checks passed
(3.81e-10 / 8.30e-13), but curvature agreement failed the unchanged
1e-8 gate: **5.03e-8** between degrees 12/14 at equatorial r=0.0792,
and **7.92e-8** against the parent on the axis at r=0.004.
The stationary three-grid acceptance of the 3.72 ring remains intact;
its Cartesian origin is not qualified for evolution.
**No exports, preflights or evolutions started. Both GPUs are idle.**
Scratch clean: **4 KiB retained / 329 GB free**, cache only.
[Complete evidence](../../results/railgun/studies/evolution-ergo372-core-20261104/).

**Conditional evolution queue remains blocked:** N96 then N128/card 0,
N192/card 1, t=50, L_full=64, max_level=6, checkpoints OFF, full frames
and last three plotfiles. A passing origin certificate is required.
The original origin correction is implemented and tested; its first approved
recovery budget is closed on rejection. The 256x32 independent mixed Einstein
constraint is 6.43e-10 and physical origin error is 9.53e-12, both passing.
Next: diagnose the Newton rounding floor and the centre interpolation, then
re-run only after the numerical correction is tested. The conditional
three-resolution evolution configuration and checkpoint choice remain intact.
Recovery configuration: [ergoregion_origin_recovery_372.json](studies/ergoregion_origin_recovery_372.json).
The November 3 interrupted check remains in the
[paused archive](../../results/railgun/studies/evolution-ergo372-core-paused-20261103/).
The 5.23 origin-recovery implementation is saved as a draft, unlaunched.
Its four CPU manufactured checks passed earlier; no GPU validation or
stationary recovery was run. Defaults of the established solver are unchanged.
The substituted source is defined in
[evolution_ergoregion_372.json](studies/evolution_ergoregion_372.json).
Nineteen CPU source-identity, phase, layout and unchanged-limit checks pass.
The candidate reuses the completed CUDA binary; no new stationary solve is
needed for its first origin check. Only a passing certificate permits export.


**Earlier finer stationary study COMPLETE, REJECTED**, source
`87f30015f`, job `railgun-ergo523-source-refined-20261103`, card 1,
**17:49:49-17:52:26 MSK**, exit 2. All 26 regressions passed.
224x28 passed; 256x32 Newton converged but its unimposed mixed Einstein
constraint is **1.44799e-8**, above the unchanged **1e-8** gate. The study
stopped correctly before 288x36 or any origin certificate. No export or
evolution started from that source. Its evolution remains blocked.
Scratch is clean: **4 KiB retained / 329 GB free**, cache only; no plotfiles
or checkpoints. [Refinement archive](../../results/railgun/studies/ergoregion-source-refined-20261103/).

The failed constraint peaks on the axis at **r=9.41262e-5**. Re-evaluation
with long-double arithmetic and differentiation still gives **1.35e-8**;
it is not merely float64 reporting noise. Numerical correction in progress:
exclude the local homogeneous N~r mode and impose angularly constant
metric values at the centre. Every original canonical equation and
constraint remains an independent acceptance test. No renewed GPU run
yet; original accepted stationary source retained unchanged.

**CUDA rebuild COMPLETE**, source `86d1e98be`, job
`railgun-ergo523-amr-build-r2-20261103`, **17:41:45–17:44:20 MSK**, exit 0.
Binary `main3d_ergo523amr_86d1e98b_2026-11-03.ex`, SHA256
`647a00124aa1eaa24a64e17a65c5ace1d754b15621c5f565b8d01a0e565502f7`.
No GRTeclyn evolution has started. Scratch is clean, **4 KiB / 329 GB free**.

**The corrected-fit origin check is COMPLETE, REJECTED**, source
`437072396`, card 0, **17:35:51–17:41:13 MSK**, exit 2.
Einstein/KG still pass (4.54e-10 / 2.81e-11); curvature agreement is
1.76e-7 between degrees 8/10 and 2.88e-7 against the parent, above 1e-8.
This blocks export. The original stationary ring's three-grid acceptance
is unchanged, but its origin is not yet qualified for the 3+1 handoff.
The companion card-1 GPU regressions finished **17:36:55 MSK**, exit 0:
**35 passed** in 60.97 seconds. The CPU boundary test passed all 368640
assertions. Checkpoints remain OFF. Scratch: **4 KiB / 329 GB free**, clean.

**Approved finer study:** refine the SAME stationary ring on
224x28 / 256x32 / 288x36, at most three solves and 30 iterations each,
with two fresh updates, Newton 1e-14, and all original physical gates.
The central lapse, matter model and radial map remain fixed; frequency
is solved. Compare against the original source as well as across the
three new grids. Test the final Cartesian core with degrees 12/14 and
unchanged 1e-8 equation/curvature limits before qualifying it for export.
No new search or automatic evolution from a failed candidate. Seven
CPU plan/layout checks pass. Definition:
[studies/ergoregion_source_refined.json](studies/ergoregion_source_refined.json).

**Repeat origin certification finished REJECTED**, job
`railgun-ergo523-core-dct-20261103`, source `71b2cabb8`, card 0,
**17:24:36–17:30:21 MSK**, exit 2. DCT-I improves parent curvature
agreement to 2.88e-7 and order agreement to 5.75e-7; both still exceed
1e-8. The equations pass (Einstein 4.78e-10, KG 2.71e-11).
Next numerical correction: extended-precision evaluation and DCT-II of
the local Cartesian fit, replacing float64 sampling and a Vandermonde
solve. Neither spectral modes nor acceptance limits are changed.

**Implementation prepared:** seven aligned import cubes, fixed physical
refinement radii, phase-correct background Sommerfeld/damping and per-level
constraint streams. Thirteen CPU layout/contract/transform checks pass.
The C++ manufactured boundary test passes all 368640 assertions, including
exact time-dependent backgrounds, static backgrounds and nonzero deviations.
The production CUDA binary and 35 GPU regressions passed; no
Cartesian export, preflight or evolution has started. Both cards are idle.
Scratch is clean: **4 KiB used / 329 GB free**.

**Origin certification finished REJECTED**, job
`railgun-ergo523-core-20261103`, source `574f1a6ac`, card 0,
**17:03:03–17:08:47 MSK on November 3**, exit 2. Independent Einstein
and scalar defects passed (4.55e-10 and 1.48e-10); absolute curvature
agreement failed: 3.00e-6 between core orders and 6.09e-6 against the
parent spectral metric. No export or evolution started. The next check
replaces the cancellation-prone cosine matrix with an extended-precision
DCT-I; no modes are filtered and no acceptance limits change. Both CPU
manufactured-transform checks must pass before repeating certification.
Both cards are idle. Scratch: **4 KiB retained, 329 GB free**; only the
new cache directory. Persistent source fields and frames remain intact.

**Three evolutions authorised through t=50**, checkpoints **OFF**, on the
two-GPU node only. The two lower members run sequentially on card 0; the
finest on card 1. The clarified box is **L_full=64**, boundaries 32 units
from the centre, and **max_level=6**. Use the spinning-wormhole paper's
background-relative Sommerfeld condition and outer damping treatment,
adapted to the ring's canonical complex scalar. Numerical implementation
and regressions precede export, preflight and evolution; none of those
three evolutions has started yet. The launch pause for script relocation
was explicitly revoked by the new t=50 request.

Select the strongest three-grid accepted ring, shift/lapse **5.231237832496**:
`results/railgun/studies/ergoregion-max-r2-seed272/finalists/04/accepted.npz`,
SHA256 `918323cc935ae66dce851af294fe7c6fbea0e4adbef16e40b43db6e4e4fc425f`.
Frequency **0.708142291115**, mass 1, winding +1, stationary grid 224x28.
Base N=96/128/192, identical fixed physical refinement radii, finest dx
**0.0104167 / 0.0078125 / 0.00520833**. The matter peak is at coordinate
radius about **0.166**. Each level must import independently sampled,
aligned Cartesian data from the same spectral field, preserving extrinsic
curvature, scalar phase and normal momentum. No interpolation of a coarse
cube is accepted as resolved fine initial data.

The origin check uses radius 0.04, degrees 8/10, a C6 join and unchanged
1e-8 tolerances. Rejection blocks export and evolution. Retain every
default frame and slice cache and the last three plotfiles per member.
Each evolution is supervised with four CPU threads and a 160 GiB host cap;
its wall budget will be recorded with the finished launcher. No added
perturbation; no automatic renewed stationary search. Definition:
[studies/evolution_ergoregion_best.json](studies/evolution_ergoregion_best.json).

**Script relocation complete:** operational runners and archive tools are in
`grteclyn-wrapper/scripts/campaigns/railgun/`; numerical commands and the
claims audit are in `grteclyn_wrapper.optimisation.railgun`. No Python or
shell script remains here. Both layout tests, moved-script syntax/import
checks and exact CPU audit reproduction pass. All 1450 package files and
immutable study checksums verify. The layout commit is `574f1a6ac`.

**Both verified maximisation searches are COMPLETE**, source `6a9da2844`.
Card 0 finished **20:23:38 MSK on November 2**, exit 0, after exhausting
32 proposals: **74 search solves and five verification solves**, accepted
best **5.134883762021**. Its outcome and finest accepted source were checked
read-only on November 3; its completed archive is still to be packed.
Card 1 finished **20:10:18 MSK on November 2**, exit 0: nine completed
proposals, **18 search solves and ten verification solves**, four promotion
attempts; accepted best **5.231237832496**. It stopped normally when fewer
than three verification calls remained. All card-1 evidence is archived in
`results/railgun/studies/ergoregion-max-r2-seed272/`.
Both jobs passed all 55 GPU regressions and retained checkpoints OFF.
Every promoted best passed 160x20 / 192x24 / 224x28 immediately, with the
original acceptance limits unchanged. No renewed search is authorised.
Neither a global maximum nor dynamical stability has been established.

**Physical-interpretation audit:** the saved 3.72 ring does have an
equatorial ergoregion at coordinate radii **0.0583–0.8525**, but shift/lapse
is not a locally measured speed. Explicit metric contractions give local
photon speed c in both directions. The half-peak matter contour is not a
surface: matter energy density is **24%** of peak at radius 0.50 and **46%**
at 0.08, so the claimed near-empty halo and hole fail the 1e-6 criterion.
Negative energy relative to infinity is locally possible; an escaping
Penrose split and a boomerang photon trajectory have not been integrated.
The asserted 35% gain is unsupported. For one neutral unpowered two-body
decay of a massive particle arriving from infinity, the photon-limit local
gain bound is **5.83%**, before escape restrictions; this is not a measured
gain or a bound on powered/collisional processes. Frequency endpoints support
a turn but do not locate it. Close three-grid agreement is not a twelve-digit
bound on every physical quantity, and one stalled Newton correction does not
establish a universal floating-point limit. The new accepted 5.13 result
already exceeds the proposed 4.3–4.8 ceiling. Reproduce this CPU-only audit
with `python -m grteclyn_wrapper.optimisation.railgun.audit_ring_claims`; its hash-checked field results
are in `results/railgun/reports/ergoregion-comparison/claims-audit.json`.
No new field solves or particle tracks were run for the audit.

**Saved-candidate validation COMPLETE: 3.72 accepted, 5.21 rejected**,
source `a9eb87a8a`:
`railgun-ergoregion-max-validate271-20261102` on two-GPU node/card 0
(candidate 3.72), and `railgun-ergoregion-max-validate272-20261102` on
card 1 (candidate 5.21). Both started **19:40:02 MSK** after the explicit
go for both jobs and checkpoints **OFF**. Card 0 finished **19:43:40 MSK**,
exit 0, **0.0606 h** including tests: all three fresh solves on
160x20 / 192x24 / 224x28 and all acceptance checks PASS. New accepted
peak shift/lapse **3.720789536602**, g_tt **+0.246798092848**, central lapse
**0.129930664**, minimum lapse **0.117744628**, frequency **0.674100187700**.
Final-pair observable/frequency differences are below **2.63e-12**;
three-grid g_tt spread **7.14e-13**. No evolution time or new proposals.
Original cap **0.5 h**, deadline **20:10:02 MSK**. Four threads,
160 GiB per job, chunks 128, max 30 iterations/minimum two fresh updates;
all original acceptance limits unchanged. Stop on rejection and retain
every field/log. Both H100s were free before launch. Scratch: **14 GB
retained, 544 GB free**, three plotfiles per old evolution, zero checkpoints;
no scratch/frame removal. Both GPUs idle. The best accepted result is now
**3.720789536602**. Its accepted field SHA256 is
`dea15224bb7e97be5a1d8528a828886b6ba3e4cbf3c8cae66d88abc8cf4207cd`.
Card 1 stopped **19:42:03 MSK**, exit 2, after its
first 160x20 solve: fresh Newton stalled at scaled residual **1.865e-14**,
above the unchanged 1e-14 target. Its equation checks passed, but this is
not a complete passing resolution study: **5.21 is rejected as a new best**.
One of its three permitted solves was used; no automatic correction rerun.
All **53 GPU regressions pass on each card**, in **70.79 / 69.37 s**.
The requested conditional renewed search will start from the accepted 3.72
ring and immediately verify every potential new best; no deferred checks.
Its run-specific scope and checkpoints OFF were confirmed; it is live above.
Both completed studies are archived as `ergoregion-max-validate271` and
`ergoregion-max-validate272`; all archive checksums pass. Worst independent
Einstein/KG over the passing three grids: **5.18e-10 / 8.28e-11**;
surface-J error **8.76e-11**, all below the original 1e-8 limits.

**Verified restart scope, approved and live above:** independent seeds 271/272 on
cards 0/1, from the new hash-checked 224x28 accepted field. Initial CMA
mean **0.129930664**, width **0.025**; physical central-lapse bounds stay
**0.08–0.32**. Same k=1, m=1 physics; no tolerance changes. Every potential
new best must pass 160x20 / 192x24 / 224x28 before receiving a successful
CMA score. Missing, failed or skipped checks reject promotion. Up to four
promotion attempts per run; stop before a new proposal if fewer than three
refinement calls remain. Per job: 32 proposals, 80 search + 12 refinement
solves, max 30 iterations/minimum two fresh corrections, Newton 1e-14;
four threads, 160 GiB, one hour including tests, chunks 128. Combined ceiling
64 proposals/184 solves. Checkpoints OFF confirmed, retain all evidence.
**37 CPU tests pass**; both new source-hash profiles pass CPU-only planning.
Runner/configs and exact commands: RUNNING.md.

**Validated ergoregion found:** `railgun-ergoregion-cma-20261102`, two-GPU
node/card 0, source `052487e5d`, **18:38:03–18:44:52 MSK**, exit 0,
**0.1136 h** including all 41 passing GPU regressions. CMA-ES stopped at the
validated target after **five proposals, 11 search solves and three fresh
refinement solves**. All original gates pass on **128x16 / 160x20 / 192x24**.
On the finest grid: frequency **0.655065086594**, central lapse **0.297290525**,
minimum lapse **0.282624975**, maximum shift/lapse **1.080970704**, maximum
**g_tt=+0.0150110091**, at the sampled equatorial rho **0.7513443**.
The positive sign exceeds the three-grid spread **2.88e-13** by many orders.
Final-pair strong-field observable/frequency differences are below **4.08e-13**.
M_ADM=1.140069720430, J=-1.126588475994. Worst off-grid Einstein/KG across
all three: **5.04e-10 / 3.74e-11**, below 1e-8; surface J error <=1.92e-11.

This establishes a stationary ergoregion on the fixed canonical k=1, m=1
branch. Dynamical stability of this new ring has not been tested. The previous
3+1 evolutions used the weaker omega=0.70 ring. Accepted field:
`runs/railgun/single-ring/scans/ergoregion-cma-20261102/accepted_ergoregion.npz`.
Discovery completed with checkpoints OFF; all fields and logs retained. Scratch:
14 GB retained, **544 GB free**, three plotfiles per old evolution, zero
checkpoints. No scratch or frame removal. Discovery and both preceding
amplitude studies are archived in results/railgun/studies/; **1278** package
files and every per-study checksum pass verification.

**Maximisation campaign stopped on a CMA library error:** two independent searches,
`railgun-ergoregion-max-seed271-20261102` on card 0 and
`railgun-ergoregion-max-seed272-20261102` on card 1 of the authorised
two-GPU node only. Both started **19:09:13 MSK**, source `a3d410421`.
Seed 271 stopped **19:15:53 MSK**, exit 1, after 27 search solves and
four completed proposals. The one-dimensional CMA library raised
`ValueError: not yet initialized (dimension needed)` during its first
population update. No refinement solve ran. Its strongest independently
passing 160x20 candidate has shift/lapse **3.72079**, central lapse
**0.129931**, and g_tt **+0.246798**; it remains provisional. All fields
and records are retained; no automatic restart. Seed 272 stopped
**19:21:32 MSK**, exit 1, after **46 search solves and 12 completed proposals**,
with the same exception. It found an independently passing 160x20 candidate
with refined equatorial peak shift/lapse **5.20846**, central clock about
**6.0 minutes per distant hour**. It remains provisional. Both cards idle;
no finalist refinement ran, and the best three-grid validated ring remains
**1.080970704**. No physical maximum is established by these stopped searches.

**Promotion rule corrected; the approved GPU validation jobs are complete above:**
every improving proposal now runs 160x20 / 192x24 / 224x28 **before** receiving
a successful CMA score. Only complete three-grid equation, flux, tail and
common-point convergence checks permit promotion. Failed or skipped refinement
means rejection, not a provisional leader; the accepted best stays unchanged.
If three refinement calls cannot be reserved, search stops before new work.
The old deferred finalist phase is removed for maximisation. The scalar pycma
failure is reproduced after 4/12 proposals and avoided with explicit unlimited
internal standard deviation; the original physical lapse bounds stay enforced.
Both seeded CPU searches finish their full 32-proposal tests. **35 CPU tests
pass**, covering rejected leaders, missing finest grids, budget exhaustion,
hash-checked saved-candidate plans and preservation of the accepted best.

The completed validation jobs tested only the saved **3.72 / 5.21** candidates,
one per card, with no new CMA proposal or source-reproduction solve.
Three fresh solves each, six total maximum; original grids and 1e-8/1e-6
gates, max 30 iterations/minimum two updates, fresh Jacobians, Newton 1e-14.
Approved resources: four threads, 160 GiB, 0.5 h per job including GPU
regressions, chunks 128, checkpoints OFF, retain fields/logs. Source and
record hashes are fixed by the figure snapshot. Run-specific go and
checkpoints OFF were explicitly confirmed for both jobs. RUNNING.md
contains the concrete commands. The stopped raw evidence stays immutable.

All **45 GPU regressions passed on each card**, in 75.86/74.67 seconds.
Both source-reproduction solves pass independent equation checks, reproducing
shift/lapse **1.080970704**. No evolution time applies. The one-hour cap
was not reached: wall durations **0.1111 / 0.2053 h**, including regressions.
The original deadline was **20:09:13 MSK**; neither run remains live.
Start from archived `ergoregion-cma/finalists/01/accepted.npz`, SHA256
`a173848c072ce0e618a6995b8b13154570a2a94f2fc58fd1845795ad853cbb52`.
Maximise peak shift/lapse on the same canonical k=1, m=1 branch. Central
lapse 0.08–0.32; frequency and amplitude free. Continue after the first
positive g_tt, preserve the incumbent and strongest validated field, and
record the bounds with `global_maximum_established=false`.

Per run: 32 proposals, maximum 80 search + 12 refinement solves; four
finalists separated by >=0.02 in log lapse. Search 160x20; final grids
160x20 / 192x24 / 224x28. Newton 1e-14, max 30 iterations, minimum two
updates, fresh Jacobians. Original 1e-8/1e-6 gates unchanged. Rejections
receive penalties; automatic smaller steps remain within the budget.
Four CPU threads, 160 GiB and one-hour cap per job, chunks 128. Combined
maximum 64 proposals/184 solves, eight CPU threads/320 GiB; the node quota
is 24 CPUs/488 GiB. GPU regression checks ran on each card first. The
checkpoint choice is explicitly **OFF** for both runs; no AMR evolution is proposed.
Twenty-seven CPU preparation tests pass, including continuation after finding
an ergoregion and preservation of a stronger field against a weaker finalist.
Both H100s were idle immediately before launch. Scratch: **14 GB retained,
544 GB free** in the four finished evolution folders and cache; three plotfiles
per evolution, zero checkpoints, no scratch or frame removal. Commands/configs:
RUNNING.md.

**Measured explanatory comparison complete:**
`results/railgun/figures/single-ring/ergoregion-comparison.png` and `.svg`
compare the previous accepted ring with the strongest single-grid candidates
from both searches, **1.08 / 3.72 / 5.21**, at the same coordinate scale.
Blue matter, half-peak outlines, orange g_tt>0 boundaries and centre-clock
leaders come from saved fields. The two current candidates are explicitly
labelled as pending refinement. Immutable numeric profiles and source hashes
are in `results/railgun/reports/ergoregion-comparison/`, snapshot 19:22 MSK;
the figure rebuilds locally without JAX, a GPU or raw cluster files.
Visual inspection and the label audit pass. This small figure snapshot is
separate from a completed campaign archive. No new solve or trajectory ran.

Completed discovery scope:
[ergoregion_cma.json](studies/ergoregion_cma.json). The central-lapse border
replaces the amplitude border without changing the field equations or the
number of unknowns. It explores the same canonical free scalar model.

CMA seed 171, population four, at most **32 proposals**. Nearest solved
fields, bounded secant predictions, automatic log-lapse steps <=0.04 and
at most four failed-step bisections per proposal replace hand-chosen steps.
Individual failed trials receive penalties; they do not stop the search.
Maximum **80 search Newton solves**, including source reproduction, plus
**nine** reserved for at most three three-grid finalists: **89 total**.
Search grid 128x16; finalists 128x16 / 160x20 / 192x24; map scale 2.5,
30 iterations per solve, minimum two corrections, fresh Jacobians, Newton
1e-14. Original equation/flux 1e-8 and tail/observable 1e-6 gates unchanged.
Bridge states have algebraic, unused-equation, flux and branch screens;
only independently checked final proposals receive feasible CMA scores.
Every search state remains provisional. A three-grid positive-g_tt sign
with the existing margin checks is required for `accepted_ergoregion.npz`.
The completed discovery stopped on the validated ergoregion target.
No new matter potential, winding, 3+1 evolution or physical stability claim.

Twenty-three CPU preparation/engine/acceptance tests pass, including actual
bounded CMA generations, failure ranking and automatic bisection. The new
CUDA border/recovery tests passed as part of the 41-test suite. Card 0 on the authorised
two-GPU node only, four CPU threads, 160 GiB, chunks 128, **one-hour** job
cap including regressions and search. The stationary search writes fields/logs,
not AMR evolution checkpoints. Both H100s were free before launch. Scratch
at launch: 14 GB retained, **541 GB free**, three plotfiles per old evolution,
zero checkpoints; no scratch or frame removal.

**Stopped:** `railgun-ergoregion-amplitude-20261102`, second GPU node/card 0,
**17:56:39–17:59:36 MSK**, exit 2, 0.0492 h including tests. All **23 GPU
regressions pass**. All three initial reproduction solves converge in two
updates and pass every original field gate; recovered frequencies are
0.700000000000697 / 0.700000000000676 / 0.700000000000639. The added
strong-field comparison rejected differing sampled extrema (shift/lapse
change 1.15e-5): those samples are at different positions on each grid.
This is an error in the new comparison, not evidence of inconsistent fields.
No amplitude increase was attempted. Three solves spent; all provisional
fields retained, no accepted file written. Both GPUs idle. The stopped run
stays unchanged. Prepare a common-physical-point comparison and a separately
approved continuation reusing these three solves; no automatic restart.
Checkpoints **OFF**. Scratch: 14 GB retained, 531 GB free, unchanged.

**Stopped, stronger ring accepted:** `railgun-ergoregion-amplitude-r2-20261102`,
two-GPU node/card 0, source `ec9b26998`, **18:10:04–18:13:36 MSK**, exit 2,
**0.0589 h** including tests. All **25 GPU regressions pass** in 37.77 s.
The first 6% amplitude increase passes all three grids and every original
and added acceptance check: pin **0.325842588**, frequency **0.685955820263**,
minimum lapse **0.384575**, maximum shift/lapse **0.617781** (previously
0.510390), maximum g_tt **-0.0964122**. No sampled ergoregion. Common-point
observable differences across the final pair are below 1.25e-13. Its saved
accepted field is `runs/railgun/single-ring/scans/ergoregion-amplitude-20261102-r2/amplitude_01/accepted.npz`.

The next 6% increase, pin 0.345393143, fails Newton on 128x16: one damped
update, then a fresh-Jacobian line-search stall at scaled residual 2.95e-4.
It also fails independent equation checks and remains rejected. Its frequency
0.6750508 is provisional, not a physical branch result. This does not locate
a turning point or a maximum spin. The approved stop-on-rejection rule ends
the sequence: **four new solves**, **seven cumulative** including the reused
three. No further amplitude or k=2 solve is queued. Both GPUs idle. Checkpoints
**OFF**; all fields and logs retained. Scratch **14 GB retained, 531 GB free**,
three plotfiles per old evolution, zero checkpoints. No scratch/frame removal.
A smaller-step or arclength continuation requires a new bounded proposal/go.

All states are compared at the same 385 radial by 50 angular physical points,
including the origin, axis and equator. Nine CPU preparation tests cover the
comparison and three-solve reuse. The actual saved reproduction states agree
at common points to **7.37e-14**; mass/J/frequency source drift **2.88e-12**.
The original rejected directory stays unchanged; the new run records hashes,
copies its passing grid evidence and saves `outcome.original.json`. Three
prior solves count toward the original 27-solve ceiling; four new solves were
used before rejection closed the run. No reproduction solve was repeated.
All thresholds and stop-on-rejection conditions remain. Four CPU threads,
160 GiB, chunks 128, 0.5 h total including tests; retain all fields/logs.
Scratch at startup: 14 GB retained, 531 GB free, three plotfiles per old
evolution, zero checkpoints. No scratch or frame was removed.

Single-ring ergoregion search,
[ergoregion_amplitude.json](studies/ergoregion_amplitude.json). Start from the
hash-checked accepted omega=0.70 state; k=1, m=1 and the matter model stay fixed.
First reproduce it on radial scale 2.5, with the amplitude pinned at its scalar
maximum: radius 1.202893, amplitude 0.307398668. The old radius-5 pin measured
only 0.015689536; it is not the scalar peak. Then take eight 6% pin increases,
up to 0.489946775, solving frequency as an unknown. The radius stays fixed.
Use secant guesses after two accepted points, fresh Jacobians, Newton 1e-14,
at least two updates and at most 30 iterations per solve. Three grids per
point: 128x16 / 160x20 / 192x24; maximum 27 solves, including the initial
three-grid reproduction. Stop at rejection or a resolved sampled ergoregion.
Original 1e-8 equation/flux and 1e-6 tail/observable checks stay unchanged;
additional lapse/g_tt/shift/frequency convergence checks run before writing
an accepted state. Positive g_tt must occur on all three grids with a margin
larger than their spread and 1e-8. No automatic k=2 branch or extra solves.
Eleven CPU-only new/existing preparation and guard checks pass;
the new CUDA border test and existing field tests passed in the stopped job.
Four CPU threads, 160 GiB, 0.5 h total, Jacobian chunks 128; retain logs
and all attempted fields. Scratch at launch: 14 GB retained in four finished
evolutions plus the 47 MB cache; 531 GB free, three plotfiles per evolution,
zero checkpoints. No scratch removal. A frequency
turning point is a hypothesis, not established by the rejected omega=0.67
Newton solve. A fixed-radius amplitude pin can turn too; no guaranteed
ergoregion or nonsingular Jacobian is assumed.

**GPU evolution complete:** `railgun-ring070-evolve-n192-t50-20261102`,
second GPU node/card 0, source `b64bf13ff`, ran from **11:13:00 to
12:56:40 MSK** (1.728 h including final image processing), exit 0,
exactly **t=50**, 15000 steps. Final evolution speed **29.36 code units/h**.
No evolution is queued; the new stationary job is listed above. Its own log contains no NaN/Inf
or fatal error. **Checkpoints OFF**, explicitly chosen November 2.

Same certified t=0 cube and frozen binary, N=192, box 32. Physics, timestep,
gauge and 25-step plot cadence unchanged; only duration/step limit and paths
change. Two single-thread image workers, four evolution CPU threads, 160 GiB
address-space cap per process, keep-last three plotfiles. No evolution is queued.
Eleven local preparation/spawn/preflight regressions pass; actual-cube
CPU-only preparation passes both checkpoint policies. The image-worker
entry point guards spawn and waits for workers before the final drain.
Scope: [evolution_long_070.json](studies/evolution_long_070.json).
The original box can affect the ring before t=50; this is exploratory,
not a new long-time Richardson or isolated-ring stability result.

**Movie processing:** replacement CPU job `railgun-ring070-t50-movies-r2-20261102`
follows the successful finished manifest and final consumer drain.
It requires all 601 slices in each of the 16 fields and finite, complete
diagnostics through t=50. It redraws into `movie_render/frames` using fixed
colour scales, then encodes the full set into the run's `movies/`; every
original frame and cache remains untouched. Two CPU cores, 16 GiB address-space
cap, three-hour render timeout; no GPU work.
Encoded frame counts/durations are checked and consecutive decoded contact
sheets are saved in `movie_render/qa` for visual review. These are exploratory
finite-box movies, not an isolated-ring stability certification. The first job
stopped at a filename-order check after step 9999, with all 601 slices present.
Numeric sorting fixes the check; four CPU completion/cadence/invalid-data
tests pass, including the five-digit step case. Full result packing and movie
visual review follow the rendering job.

**Previous run complete:** the final 192^3 Richardson job finished at
**10:24:52 MSK**, exit 0, exactly **t=2**, all frames processed. Evolution
speed was approximately **30.4 code units/h**. All authorised budgets are
spent. Its budget is closed; the t=50 run has its separate go.

Last scratch check, second GPU node, **2026-11-02 12:56 MSK**: `_cache/`
**47 MB**, old 96^3 **709 MB**, 128^3 **1.7 GB**, 192^3/t2 **5.6 GB**,
completed 192^3/t50 **5.6 GB**; **532 GB free**. All four runs retain three
plotfiles. Zero checkpoints. No plotfile or frame was removed manually.
All original frames and caches stay on NFS; first node not listed.

**Start verified:** full preflight passed, imported Q/J match the original
192^3 t=0 values. Actual preflight and live frame 0 are byte-identical to the
previously inspected reference PNG, SHA256
`c876db701540a2fe40d941ccc0d8467fafb0d68a6b1e5ea3ee0522a1fd9790c1`.
Both spawned image workers are active; 45 plotfiles processed through step
1100, boundary-flux rows advancing. Recent throughput 9.85 s/plot versus
production about 10.4 s/plot; the initial processing lag remains bounded.
See `results/railgun/reports/evolution-long-startup.json`.

**192^3 sequence:** 31 GPU regressions passed in 24.63 s; certified export
**10:05:32–10:12:36 MSK**, eight million padded cells / 1.856 GB; inspectable
t=0 preflight **10:14:34–10:14:59 MSK**; full-preflight/evolution/drain
**10:17:54–10:24:52 MSK (0.1161 h)**. The initial ring/hole image was checked.
Export det(h)/tr A defects 1.12e-15 / 4.67e-17; imported Q matches its export
within 1.27e-11. The source, frozen binary, core and physics are unchanged.
Actual template differences are only N=192, max_steps=600 and run/data paths.
Grid SHA256 `64a606f3f248ecd939d4088c28116776847c2a6b0831d572b0d8ef67ec61bd58`.
No NaN/Inf in its own evolution log; every matter diagnostic is finite.

## Spatial interpretation of the initial omega=0.70 ring

The completed spatial guide is `results/railgun/figures/single-ring/ring070-physics.png`
and `.svg`; profiles/extrema are in `reports/ring070-physics.json` and `.tsv`.
NumPy/SciPy analysis of the existing accepted state, no new solve or GPU work.
The origin lapse is **0.434391**, verified directly against every angular
endpoint node: **26.06 minutes per distant hour**, not the previously quoted
minimum-lapse value. The minimum lapse **0.421456** is at rho=0.8193.
For clocks held at fixed coordinates the rate is sqrt(-g_tt), with a smaller
minimum **0.369727** at rho=1.06354: **22.18 minutes per distant hour**.
Angular dragging peaks at the origin, whereas |shift|/lapse peaks at
rho=1.23702, value **0.510407**. Maximum g_tt=-0.136698; no sampled ergoregion.
The search covers the compactified radial domain and refines the extrema;
coordinates are not proper distances. One equatorial ring map attaches the
clock/dragging measurements to each named location. The central particle
route is described as axial, perpendicular to the map. Render checked.

## Three-grid Richardson result: 96^3 / 128^3 / 192^3

Completed at fixed box 32, source omega=0.70, t<=2, no perturbation.
[Measured order table](../../results/railgun/reports/evolution-richardson-070.md)
and [full extrapolations](../../results/railgun/reports/evolution-richardson-070.json)
come from actual matched t=0/0.5/1/1.5/2 samples. Ham/Mom are L0 L2 norms
inside the same physical r<8 sphere; whole-box boundary-contaminated norms
remain in every archive and are not used for the interior convergence claim.

- At t=2 the Ham order is **3.80 / 4.01** and Mom **3.62 / 3.83**
  for 96→128 / 128→192. The finer pair moves toward fourth order.
- Signed three-grid charge-change differences give **p=4.677** at t=2
  (4.689→4.677 over t=0.5→2). Matter J gives **p=4.269** at t=2.
  Orders use the unequal spacings, not a fixed ratio or assumed p=4.
- Maximum charge drift is **0.068895% / 0.017787% / 0.0024917%**.
  Finest final interior Ham/Mom L2=**1.63065e-5 / 1.10072e-5**.
- The estimated fine-grid Q error at t=2 is 3.529e-5; extrapolated
  Q=1.3063251693. The three-point continuum charge-change estimate is
  +2.745e-6, not exact conservation. These are asymptotic estimates,
  not independent error bounds. Initial charge/amplitude differences at
  t=0 are below the diagnostic precision gate and have no fitted order.
- All three finished archives pass matching source/binary/core/parameter
  and checksum checks. Nine manufactured/identity tests and 31 GPU checks
  pass. No missing data or unresolved order is filled with synthetic values.

Archive: `results/railgun/studies/evolution-070-n192/`, alongside the original
two immutable pilot archives. Three-grid figure: `figures/evolution/ring070-evolution-convergence.png`
under results/railgun, rebuilt from the portable diagnostics. The completed
budget is [evolution_richardson_070.json](studies/evolution_richardson_070.json).
This establishes short-duration numerical convergence of the import/evolution;
long-time stability remains untested. A larger-domain, longer, explicitly
perturbed three-resolution study requires a separate proposal and go.

## Cartesian ring evolution: first two-grid pilot complete

Source: accepted `frequency-deep/frequency_01/accepted.npz`, omega=0.70,
k=+1, m=1. Evolved with **RadialRecipe's canonical complex scalar**, sign +1,
Phi=chi_complex/sqrt(4 pi), Pi=+n.partial(Phi), correct rotational K_ij and
conformal connections. Box 32, no reflection symmetry or added perturbation,
fourth spatial derivatives, RK4, CCZ4, initial stationary lapse/shift followed
by 1+log/Gamma-driver gauge. Four CPU threads, 160 GiB, 0.5 h per GPU job.

- **96^3:** `ring070-n96-t2-r2-20261102`, **09:21:00–09:23:10 MSK
  (0.0361 h)**, exit 0, all frames rendered. One floating-point stop-boundary
  step reached 2.0066667; trust and figures use saved **t<=2** only.
- **128^3:** `ring070-n128-t2-20261102`, **09:35:54–09:39:05 MSK
  (0.0531 h)**, exit 0, exactly **t=2**, max_steps=400. All frames rendered.
- Both exports pass the new C6 core certificate and algebraic CCZ4 checks.
  Core Einstein/KG maxima 1.70e-10 / 1.13e-10; degree-comparison curvature
  8.60e-9, below the unchanged 1e-8 gate. Export det(h)/trace-A defects
  below 8.89e-16 / 4.05e-17. C++ t=0 charges match each export within 1e-10.
- Maximum finite-box charge drift through t=2: **0.068895% / 0.017787%**,
  a **3.8734-fold** reduction on refinement. Initial interior Hamiltonian
  L2: **1.0334e-4 / 3.4831e-5**; final: **2.4758e-4 / 8.2997e-5**.
  These interior errors shrink by **2.97 / 2.98**. Momentum errors also shrink.
  Boundary-contaminated whole-box norms are retained, not used for this claim.
- No NaN in either run's own evolution log; finite matter diagnostics.
  The imported ring and centre hole are visible in frame 0. The m=2 shape
  diagnostic stays below 7.1e-17 in these unperturbed, symmetric-grid tests;
  this does not excite or bound an unstable mode's growth rate.
- **22 GPU regressions pass** (including CUDA/float64 assertions), plus 14
  local analytic/preflight checks. Two exports, four zero-step startups and
  two evolutions consumed. The first startup remains explicitly refused for
  obsolete `hdf5_subpath`; removing it changed no physics or tolerances.

The portable archives are `studies/evolution-070-n96/` and
`studies/evolution-070-n128/`, under results/railgun. They contain actual
params, logs, t=0 preflight reports, source/core hashes, diagnostics and
selected numeric slice inputs. The refused startup has a separate immutable
archive. Summary: `reports/evolution-pilot-070.json`; comparison figure:
`figures/evolution/ring070-evolution-pilot.png`. Large initial cubes and the approved
last three plotfiles stay in the run/scratch tree; no frame was deleted.

Frozen CUDA binary: `main3d_ring070r2_3e6466ed_2026-11-02.ex`, source
`3e6466ed`, SHA256
`14c6dadf61899ad21773f8cbe9df589f2745b0907d3779218b9d890c7d8019bc`.
The four-thread CPU build finished at **08:51:40 MSK**, exit 0.
Git push/pull through `myfork` only; no SCP.

The final 192^3 completion and generalized Richardson analysis are now done,
as reported above. Every earlier stationary/particle result remains below.

The November 1 field/particle close-out also passed **45 targeted CUDA
tests** (6+39), following the preceding 37-test correction suite. Their
reports and execution evidence remain in the immutable result package.

## Primary target: concentric rings with a clear annular channel

**Accepted:** independent fields k1=+1, k2=-12, equal particle masses m=1,
even parity, one common centre and equatorial plane, zero total angular
momentum. These are diffuse scalar fields, not solid torus walls.
Effective edges use **Eulerian energy density below 1e-6 of each component's
own peak**. No exact-vacuum claim.

Three fresh grids **192x16 / 224x18 / 256x20** pass the coupled field,
unused Einstein, intrinsic/Cartesian Klein–Gordon, boundary, tail, quadrature,
charge/flux and observable-convergence checks. Maximum finite-sphere J error
across the grids is **7.19e-14**, against the unchanged **1e-8** gate.
On the finest grid:

- M_ADM=1.053808110837; component angular momenta
  **-0.991960985480 / +0.991960985480**.
- J_volume=-4.44e-16; independently measured J_infinity=-1.09e-14.
  Interior max |w|=0.00435161: zero net spin does not remove local dragging.
- Density peaks near rho=6.22088 and 150.83809. The effective matter gap is
  **33.297341139 < rho < 40.908024688**, width **7.610683549**.
- The sampled common three-grid tube is
  **35.200012026 < rho < 39.005353801**, **-10 <= z <= +10**.
- Finest off-grid Einstein/KG maxima: **5.08e-13 / 2.83e-14**.
  Final observable drift 7.26e-10; charge/edge drifts 1.16e-13 / 1.04e-12.

Archive: [annular-validated-k12](../../results/railgun/studies/annular-validated-k12/).
Figure: [validated rings and gap](../../results/railgun/figures/two-rings/annular-rings-validated.png).

## Particles between the two rings

**Accepted:** all **eight** full TD-MPD tracks reach z=-10 from z=+10.
Launch rho=37.102682914, reference axial speed -0.5, spin 0/+0.001/-0.001
and a background/spin reversal, each at RK tolerances 2e-11 / 2e-12.
All controls have the same spin-corrected Killing energy
**E=1.125108820447**; launch energy mismatch is 2.22e-16.

Every one of 1001 samples per track stays in the validated annular tube.
Actual path rho ranges **36.404424334–37.102682914**. Maximum component
densities relative to their own source peaks are **9.42e-8 / 1.74e-7**,
both below 1e-6. Density is reconstructed from Cartesian scalar derivatives
and the actual factored metric, independently of the equatorial screen.

Worst normalised invariant drift: **4.11e-13**, against 1e-9.
Maximum RK timing/position differences: **5.69e-14 / 2.85e-14**, against
1e-7. Background/spin reversal passes. Finest coordinate arrival times:
zero spin 42.12626592286; +z spin 42.12626771656; -z spin 42.12626412917.
The +z minus -z timing split is **3.58739e-6**.

This establishes finite passage through the matter gap. It does not establish
asymptotic escape, long-term trapping, energy gain or dynamical stability.

Archive: [annular-transit-k12](../../results/railgun/studies/annular-transit-k12/).
Figure: [actual paths and matter exposure](../../results/railgun/figures/particles/annular-transit-k12.png).

## Stronger single-ring finite spin selection

**Accepted:** the omega=0.73 source and Cartesian core certificate are
hash-checked and reused. At equal **E=0.880293764772**, launch z=+1 toward
z=-10, spin magnitude 0.001: +z spin reaches the target, -z spin first turns
at **z=-9.999842477545**, and zero spin reaches the target. The ring has
negative J, so +z is against its spin and -z is with it.

All saved full-track conservation gates pass. The initial two-RK comparison
was insufficient for two near-threshold arrival times; the original failed
studies remain unchanged. The independent axial first-integral audit now
passes all **656 full Cartesian MPD substitution/invariant checks**. Its
maximum equation defect is **1.32e-14**. Every nonmarginal saved finest
track agrees with the independent phase time within **5.29e-8**, below 1e-7.
The last two order-16/order-32 phase comparisons are **4.512e-12**.

Cumulative evidence: **34 MPD tracks**, **34 scalar phase quadratures**,
656 full MPD substitution points. The last polish adds only two scalar
integrals, no new MPD track or substitution point. Exact-threshold marginal
contacts retain height/conservation checks but carry no arrival-time claim.
The accepted result is finite target-versus-turnaround selection, not a
spin-selective escape result.

Archive: [strong-uphill-073-validated](../../results/railgun/studies/strong-uphill-073-validated/).
Figure: [strong-ring finite selection](../../results/railgun/figures/particles/strong-uphill-073.png).

## Numerical fixes and unchanged acceptance contract

- `regular_dragging.py` solves **w=(1-s)^3 H**, H degree nx, with all
  interior momentum equations retained and analytically divided by (1-s)^3.
  The angular infinity condition and its projected next-order radial condition
  remove uncontrolled endpoint modes. Direct H-coefficient transfer preserves
  infinity information during refinement. Fresh Jacobians and Newton 1e-14
  are used. Zero J is measured independently at infinity and in the volume;
  it is not hardcoded through a quintic falloff. Cartesian metric-ratio AD
  verifies every finite-sphere flux. Actual factored-field volume charges are
  cross-checked against nodal quadrature before acceptance.
- `axial_reduction.py` supplies the aligned-axis TD-MPD first integrals.
  Extended-precision spectral evaluation and cancellation-free turning
  differences allow an independent phase calculation. Full Cartesian MPD
  substitution verifies the reduction, including transverse curvature.
  `axial_phase_polish.py` refines only the two inadequate coarse quadratures.
- `annular_transit.py` refuses an unvalidated or non-archived field, checks the
  common three-grid tube, matches Killing energies and records actual
  per-component matter exposure along each path. Off-axis motion keeps an
  inner stopping radius; it does not require a Cartesian origin patch.
- Through-centre axial motion uses `corridor.py`: a certified two-dimensional
  fit in rho^2,z^2, a C2 join, degree comparison and independent curvature/KG
  checks. A signed-axis curve alone is not used to infer transverse curvature.

Field equations/unused constraints/charge and flux: **1e-8**. Spectral tails,
three-grid observable/component-charge/edge drift and matter cutoff:
**1e-6**. Particle invariant/SSC/timelike checks: **1e-9**. Nonmarginal axial
timing: **1e-7**, height **1e-8**. Annular timing/position/reversal: **1e-7**.
Failed checks stop a recovery; no acceptance limit was relaxed.

Equations and definitions: [EQUATIONS.md](EQUATIONS.md).
Commands, budgets and reproduction: [RUNNING.md](RUNNING.md).
Source: `grteclyn-wrapper/src/grteclyn_wrapper/optimisation/railgun/`;
shared device/Jacobian/Newton core: `optimisation/solver/`.

## Earlier accepted baselines and remaining research

- Spherical baseline: 56x8/72x10/96x12, independent areal-radius ODE agreement
  in mass/frequency 5.48e-8 / 1.12e-8. Archive: `spherical-validated/`.
- Weak pure k=1 ring: 72x10/96x12/128x16, M=0.971450813143,
  J=-0.992014330336, omega=0.932692332164. Integer-winding two-field homotopy
  removes the k=0 component before pure-ring validation. Archives:
  `ring-validated/`, `ring-profile/`, `ring-transit/`, `uphill-transit/`.
- Overlapping zero-J k1=+1/k2=-2 baseline is accepted as a stationary field,
  but fails the annular-gap geometry. Archive: `counter-rotation/`.
- Single-ring frequency continuation accepts omega=0.70 on
  96x12/128x16/160x20: minimum lapse 0.42146, maximum shift/lapse 0.51034,
  maximum g_tt=-0.136716. No sampled ergoregion. Omega=0.67 fails Newton on
  the first grid; no physical maximum spin or branch termination is established.
  Archives: `frequency-073-refined/`, `frequency-deep/`.
- Six linear seeds pass two-grid tests: new k=+2,m=2.5 and m=3 even fields,
  and a k=+1,m=1 odd field, on the weak k=1 metric. These are separate-field
  homotopy starts, **not accepted mixed-mass or stacked spacetimes**.
  Archive: `branch-seeds/`. No nonlinear seed recovery is authorised.

Next work requires a separately bounded proposal and go: nonlinear heavy-inner
or odd-parity homotopy, subsequent outer -6/-8 seeding only after a pure heavy
inner ring passes, stronger compactness continuation, asymptotic scattering
or dynamical stability. No automatic lower-frequency, higher-grid or new-field
run is queued. Winding remains integer; no fractional-k interpolation.

These are regular-centre, one-ended Einstein–complex-scalar configurations
with canonical independent matter fields and no phantom support. The phase
convention is exp(i omega t+i k phi), giving J_i=-k_i Q_i. Independent fields
add stress tensors without harmonic interference. Zero total J removes the
leading exterior spin term, not all exterior rotational multipoles. An
axis-touching ergoregion is excluded by a regular positive lapse; ergoregions
must be tested off axis. A stationary metric supplies no unspecified source
of Killing-energy gain. Scalar modes are not polarised spinning wavepackets.
Stability remains `not_assessed`.

## Saved evidence and packaging

`results/railgun/figures/` groups images into `single-ring/`, `two-rings/`,
`particles/` and `evolution/`, with a linked README index. Earlier overlapping
and provisional results have separate subfolders. `reports/` contains standalone
JSON/TSV and regression reports; `studies/` contains self-contained numerical
archives, execution logs, configurations and SHA-256 manifests. The current
summary is [completed-experiments.json](../../results/railgun/reports/completed-experiments.json).
The [package README](../../results/railgun/README.md) indexes accepted and
rejected studies and supplies figure commands. Earlier cubic-tau, quintic and
precision failures stay explicitly rejected; none is promoted retrospectively.

Run `grteclyn-wrapper/.venv/bin/python grteclyn-wrapper/scripts/campaigns/railgun/verify_pack.py` to
check the complete inventory and every immutable per-study checksum.
