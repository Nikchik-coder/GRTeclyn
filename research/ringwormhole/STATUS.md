# Ring–wormhole campaign — status

Updated **2026-11-05 (MSK)**. Branch: `feature/optimisation`.
Current findings only; detailed run records and numerical checks are in
[optimisation STATUS](../optimisation/STATUS.md).

## Live

**Running: `ringwormhole-cont108-20261105T074046`**, first node/card 0.
Frozen source `e9b8aa2d1`; started **Nov 5 10:40:46 MSK**.
Physical amplitude continuation from the accepted weak ring: 0.0284222725
at the CMA-derived anchor toward 0.2846529189, at most 32 attempts plus
three final validation solves. No evolution time; solve speed not yet measured.
One hour / four threads / 160 GiB, checkpoints OFF; hard stop **11:40:46 MSK**.
Estimated duration **0.25–0.75 h (10:56–11:26 MSK)**, pending first steps.
Startup storage: scratch clean, **4 KB cache / 302 GB free**;
second node not listed. Output `runs/ringwormhole/ergoregion108_continuation_20261105/`;
log under the job name in `runs/capped_jobs/`. No follow-on queued.

## Planned (nothing launches without the go)

November 5 clarification: **matter may overlap the throat**. The running
job retains its original exterior-ring rejection record. A separate
[CPU assessment](../../grteclyn-wrapper/src/grteclyn_wrapper/optimisation/ringwormhole_overlap.py)
will remove only that preference from saved three-grid checks; all equation,
energy, minimal-surface, symmetry, volume and tidal gates remain. Six policy
tests pass. No ergoregion is inherited from the CMA source or assumed.


**Retry running: continuation toward the CMA-derived amplitude border.**
[Retry configuration](ergoregion108_continuation.json),
[dispatcher](run_ergoregion108_continuation.sh). Start at the accepted weak-ring
fields, reanchor the same solution at xi=0.4877785081 (amplitude 0.0284222725),
and raise amplitude toward 0.2846529189. At most 32 continuation attempts
(20% initial growth, adaptive halving, minimum absolute step 1e-5), then
three perturbed validation solves of the target or strongest converged point.
109 CPU regression tests pass. Each solve retains the 24-update cap;
backtracking may reach 1/4096. Keep failed raw iterates/history and each
converged intermediate field. Total cap 1 h / four threads / 160 GiB,
GPU 0, checkpoints OFF. This follows the weak-ring branch; sharing a scalar
amplitude with the CMA seed does not identify the resulting spacetime with it.

**Original target and unchanged qualification:**
[Configuration](ergoregion108.json), [preview/dispatcher](run_ergoregion108.sh).
Reuse the accepted CMA-ES finalist at source shift/lapse **1.080970704**,
frequency **0.655065086594** and maximum g_tt **+0.0150110091**; its original
128x16 / 160x20 / 192x24 stationary checks passed. No new CMA search.
Insert the same R_A=2 throat with matching ring lobes, V=0, nonrotating
infinities; re-solve all fields on **210x36 / 224x38 / 240x40**.

The **unsolved mapped seed** has throat shift/lapse **1.04182**, g_tt
**+0.00869976**, E_b/R_A **1.65786**, and its density peak on the throat.
These seed values establish no coupled solution. Retain the existing
E_b/R_A<=1, exterior-ring, equation, geometry and tidal acceptance gates;
converged diagnostic fields are retained even if a policy gate rejects them.
The source's earlier Cartesian-origin certificate failed; this experiment
requires a new throat solution and independent checks, with no evolution export.

The ergoregion target samples the actual deformed minimal surface at 129
angles and requires positive g_tt on all three accepted solutions, exceeding
both 1e-8 and the three-grid spread. An outer ergoregion alone does not meet
the throat target. **102 CPU tests pass**; shell and no-GPU previews pass.
Approved first node/card 0, three solves only, 24 Newton updates each,
1 h / four threads / 160 GiB, float64/platform allocator, chunk 256,
checkpoints OFF, fields/logs retained. Original attempt failed as recorded above.
Retry output: `runs/ringwormhole/ergoregion108_continuation_20261105/`.

- Continue the coupled ring branch toward stronger measured dragging, then
  repeat three-grid validation and the same-spin comparison at the new J.
  The present ring already uses **97.2%** of the ordinary-matter energy allowance.
- Test qualified configurations in time evolution before making a stability claim.

## Main results

**Model:** a two-ended wormhole surrounded by matching ordinary scalar rings,
adapted from the weak railgun ring. True minimal throat area **16 pi (R_A=2)**,
gamma=0, massless phantom potential V=0; free canonical scalar with mass=1
and winding k=+1. The ring sources dragging with both infinities nonrotating.
The ring-free control has the same area and **J+=-0.9477747390613108**;
its spin is carried by the wormhole and its far-end rotating frame can differ.

X_full is the integrated phantom-field exoticity measure used in these solves.

| Configuration | X_full | Reduction against static Ellis |
|---|---:|---:|
| Static Ellis reference | 3.141592654 | — |
| Weak ring around the wormhole | 3.106532920 | **1.115986%** |
| Ring-free rotating control, same area and J | 1.734504204 | **44.789016%** |

**The weak-ring reduction against static Ellis is confirmed, but this ring
requires 79.1021% more phantom support than the matched rotating control.**
It establishes no extra exoticity benefit over that control. The ring has
lower peak tide (0.08423 versus 0.19132); both satisfy the 0.33333 ceiling.
No sampled equatorial ergoregion in the ring case. Stability is unassessed.

**Validation:** both configurations pass **210x36 / 224x38 / 240x40**, including
fresh perturbed Newton recoveries and independent Einstein/scalar equations
on 49x21 points. All original geometry, volume, energy and tidal gates remain.
Finest-pair X_full drift: ring **4.89e-14**, control **9.51e-14**.
The ring passed 99 CUDA regressions; the control passed 70, ten continuation
steps and three final re-solves. GPU matrix-copy and LU compilation memory
failures were fixed before these successful runs; operational notes are in
the local `CLUSTER_GPU.local.md` runbook.

## Saved evidence

Previous direct CMA-seed insertion `ringwormhole-ergo108-20261105T072903`
ended **Nov 5 10:33:09 MSK**, exit 2, after 0.068 h on first node/card 0.
The first 210x36 solve stalled before any accepted Newton update at residual
**3.492e-3** (25.62 s); finer grids did not run. 102 CUDA tests passed.
No coupled ergoregion or exoticity result. Saved mapped seed, static reference,
checks and log remain in `runs/ringwormhole/ergoregion108_20261105/` and
its `runs/capped_jobs/` directory. Sampled GPU peak **34487 MiB**.
Both cards idle; scratch clean, **4 KB cache / 303 GB free**;
second node not listed. No remaining ETA.



| Study | Frozen source | Finished MSK | Output on persistent storage |
|---|---|---|---|
| Weak ring, three grids | `f9f29a566` | Nov 5 09:40:51 | `runs/optimisation/railgun_throat_validation_20261105_r3/` |
| Matched-spin control | `bb0b68851` | Nov 5 10:01:55 | `runs/optimisation/railgun_matched_control_20261105/` |

Accepted fields: `accepted_ring.npz` and `matched_spin.npz`, respectively.
Arrays, checks and logs remain on NFS; these numerical archives are not yet
published in the tracked results pack. Configurations:
[ring validation](../optimisation/studies/railgun_throat_validation.json),
[matched control](../optimisation/studies/railgun_matched_control.json).
