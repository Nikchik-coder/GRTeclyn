# Completed high-spin and geometry experiments

All five stationary searches and the dispatcher finished. This pack contains
three independently refined backgrounds, but **no new demonstrated reduction
relative to V=0 at matched size and spin**. No evolution was run and stability
remains unassessed. Exact values and checks are in `summary.json`.

## Fixed-size, fixed-spin D90

The two positive-family restarts stopped normally on CMA's function tolerance:
744 evaluations for the warm restart and 768 for the weak-kink restart. Both
reached provisional X=0.564945, below the massless X=0.599549, but these fields
failed the acceptance checks. The warm restart's only screened finalist refines
to X=0.623381857, **3.98% above V=0**; its three grids take 4/2/3 Newton updates.
The weak restart has no screened or validated finalist. The earlier low-mass
campaign's X=0.611923754 remains the better validated D90 potential candidate,
and also remains above V=0.

The signed-interior search completed 400 proposals and found provisional
X=0.203862059, **66.00% below V=0**. Its Q minimum is -0.885797, while
Q(1)=3.719669 remains positive. This is a rejected numerical candidate, not a
physical result: all 42 search-grid PASS candidates failed finer-grid screening.
There is no screened or validated finalist. Keep `signed/d90_best_frontier.npz`
for resolution diagnosis, not for article points or evolution initial data.
The dispatcher marked this job failed because no validated finalist existed;
its own exit 0 means only that it finished processing the queue.

## Fixed true area with variable spin

Both geometry searches completed 200 proposals. Their finalists pass perturbed
150x30, 180x36 and 210x42 re-solves, with two Newton corrections on every grid
and last-pair relative X drift about 2.1e-12. Unused Einstein equations,
off-grid equations, minimal-surface checks and the fixed tidal ceiling pass.
The objective here is **X_full normalized by R_A**, including angular gradients;
it is different from the fixed-R_e D90 objective above.

The positive-family search gives X_full=0.785362378 at J=6.441851. The relaxed
endpoint-positive search gives X_full=0.767319886 at J=6.483804. Both hold
area 204.026798 and asymptotic redshift fixed. Their initial massless reference
has X_full=4.684238263 at J=1.013800, so the joint spin-and-potential reductions
are 83.23% and 83.62%. **Those percentages do not isolate the potential.**
Both massless continuations to the winning spin failed Newton convergence
(residuals about 2e-4); matched-spin reductions remain null in the outcomes.

The relaxed search's winner has min Q=0.821613, still positive everywhere.
It therefore does not demonstrate a benefit from a negative potential. Four
negative-interior proposals passed the coarse checks; the lowest had
X_full=2.557900 and was not selected for final refinement. Its fields are kept
alongside the winning coarse and fine fields.

## Archive and completion

D90 weak/warm ended October 31 at 22:48:20/22:48:54 MSK. Signed D90 ended at
23:34:40, relaxed geometry at 23:52:00, and positive geometry on November 1
at 00:52:54 MSK. No job hit its hard timeout. The searches have no plotfiles,
AMR checkpoints, frames or consumer; scratch needs no pruning.

`d90-extension/`, `geometry-positive/`, and `signed/` retain all evaluation
traces, acceptance decisions, source manifests and selected fields. `jobs/`
contains the original commands, logs and termination records. All final-grid
fields, their coarse parents and references are included, as are selected
rejected fields; other coarse candidates remain on persistent cluster storage.
The original geometry and signed-search source commits are recorded in the
launch/dispatch manifests; the legacy D90 commands and the previous campaign
status identify their source as 87d52379.

`archive_manifest.json` records source paths, original hashes and packed hashes.
Numerical arrays are losslessly compressed; deployment prefixes in text and
metadata are removed. `SHA256SUMS` covers every archived file except itself.
The archive check confirmed finite selected fields and agreement between saved
finalist metadata and outcome records. Paper figures and tables are unchanged.
