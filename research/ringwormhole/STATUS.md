# Ring–wormhole campaign — status

Updated **2026-11-05 (MSK)**. Branch: `feature/optimisation`.
Launchers, workers and run configurations live in the wrapper's
[campaign directory](../../grteclyn-wrapper/scripts/campaigns/ringwormhole/README.md).
This directory holds STATUS and research writing. Earlier weak-ring records:
[optimisation STATUS](../optimisation/STATUS.md).

## Live

No live or queued runs. The throat-amplitude job finished **Nov 5 11:13:41 MSK**;
both GPUs on the first node are idle. Checkpoints OFF; fields and logs retained
on persistent storage. Scratch clean: **4 KB cache / 302 GB free**.
Second node not listed. No remaining ETA.

## Planned (nothing launches without the go)

**Prepared: independently spinning wormhole plus co-rotating canonical matter.**
[Configuration](../../grteclyn-wrapper/scripts/campaigns/ringwormhole/configs/spin_ring_co_rotating.json),
[launcher](../../grteclyn-wrapper/scripts/campaigns/ringwormhole/run_spin_ring.sh).
Start from the accepted overlapping-matter point (20.678708% static reduction),
keep true R_A=2, V=0, gamma=0 and scalar normalization at xi=0 fixed, and
continue total J+ from -0.7163901140 to **-0.7963901140** in four steps.
Solve the relative rotation of the two asymptotic frames; allow two-ended
asymmetry. Require nonzero geometric angular-momentum flux across xi=0,
aligned with the matter flux. This specified-cut diagnostic is not a unique
global separation into wormhole and matter spins.

Compare with a ring-free rotating control at the **same minimal area and
final total J+**, continued in four steps from the existing control. Both arms
then get 210x36 / 224x38 / 240x40 perturbed recoveries and independent 49x21
equation checks. Keep the existing energy, surface, volume and tidal gates;
throat overlap remains allowed. The symmetric-family identities (reflection
and J_b/2=J+) are inapplicable here; full angular-momentum conservation and
localization at both ends remain required. A failed arm or mismatched J gives
no matched-spin reduction claim.

Prepared first node/card 0, **14 solves maximum**, 24 Newton updates each,
1 h / four threads / 160 GiB, CUDA float64/platform allocator/chunk 256;
checkpoints proposed OFF, fields/logs retained. **132 CPU tests pass**; shell
syntax checks pass. **No GPU startup; run-specific
go and checkpoint decision pending.** No follow-on or counter-rotating case.

- Try slightly less throat matter to retain g_tt > 0 while bringing peak tide
  below 0.333333. The present ergoregion solution exceeds that ceiling by 6.22%.
- Compare a qualified new point with a ring-free control at its own area and J.
  The older matched-spin control applies only to the weak ring.
- Test stationary qualified configurations in evolution before assessing stability.

## Main results

**A coupled throat ergoregion is solved on all three grids.** The final
210x36 / 224x38 / 240x40 solutions have X_full **2.422262173008**, a
**22.897000% reduction against static Ellis** at the same minimal area.
Throat shift/lapse is **1.1847817219**, maximum throat g_tt **+0.05261772857**;
its three-grid spread is **5.06e-13**. Independent Einstein/scalar errors
on 49x21 points are **7.75e-12 / 8.28e-12** on the finest grid. Each final
solve recovered a 1e-6 perturbation in two Newton updates. Finest-pair
X_full drift is **7.52e-14**. Frequency **0.7416917715**, J+ **-0.7547421096**.

**This point is not fully accepted:** peak tide **0.3540816225** exceeds the
unchanged **0.3333333333** ceiling by **6.22%**. Ordinary-matter energy
**E_b/R_A = 0.9647956677** passes. Matter density peaks on the throat;
this overlap was explicitly allowed on November 5. Original records retain
both `tidal_limit` and `ring_does_not_surround_throat`; the separate overlap
assessment removes only the latter. A positive, resolved g_tt on checked
solutions is distinct from passing every design ceiling.

**The preceding overlapping-matter point passes all remaining gates** on the
same three grids: X_full **2.491951887687**, or **20.678708% below static**;
throat shift/lapse **0.7584879785**, max throat g_tt **-0.0851191289**.
E_b/R_A **0.8883857544**, peak tide **0.2207550586**. Independent Einstein/scalar
errors **6.16e-12 / 1.40e-11**; finest-pair X_full/observable drifts
**6.16e-11 / 8.33e-10**. Saved as `accepted_overlap.npz` after the explicit
geometry clarification; original rejection rows remain unchanged.

**Model:** a two-ended wormhole with matching canonical rotating scalar matter,
free mass=1, winding k=+1. True minimal area **16 pi (R_A=2)**, gamma=0,
massless phantom potential V=0. Both infinities are nonrotating; matter
sources the dragging. X_full measures integrated phantom-field exoticity.
No stability or new matched-spin benefit is established by these stationary solves.

| Configuration | X_full | Reduction against static Ellis | Outcome |
|---|---:|---:|---|
| Static Ellis | 3.141592654 | — | reference |
| Weak exterior ring | 3.106532920 | 1.115986% | three grids pass |
| Stronger matter overlapping throat | 2.491951888 | 20.678708% | three grids pass with overlap allowed |
| Throat ergoregion | 2.422262173 | 22.897000% | equations pass; tide exceeds cap |
| Ring-free control matched to weak-ring J | 1.734504204 | 44.789016% | three grids pass |

The weak ring requires **79.1021% more phantom support** than its same-area,
same-J control (J+ = -0.9477747391). Its smaller reduction against static
therefore establishes no extra benefit over that rotating control.

## Saved evidence

| Study | Frozen source | Finished MSK | Output on persistent storage |
|---|---|---|---|
| Weak ring, three grids | `f9f29a566` | Nov 5 09:40:51 | `runs/optimisation/railgun_throat_validation_20261105_r3/` |
| Matched-spin control | `bb0b68851` | Nov 5 10:01:55 | `runs/optimisation/railgun_matched_control_20261105/` |
| Direct CMA insertion | `7dc132c8d` | Nov 5 10:33:09 | `runs/ringwormhole/ergoregion108_20261105/` |
| Outer-amplitude continuation | `e9b8aa2d1` | Nov 5 11:05:05 | `runs/ringwormhole/ergoregion108_continuation_20261105/` |
| Throat-amplitude continuation | `a8c33d5b8` | Nov 5 11:13:41 | `runs/ringwormhole/ergoregion108_throat_20261105/` |

Direct insertion stalled on 210x36 before an accepted Newton update at residual
3.492e-3; 102 CUDA tests passed. Physical continuation from the accepted weak
ring then used 31 attempts and three final solves (0.405 h; 109 CUDA tests).
Reanchoring the scalar amplitude at the throat bypassed the outer control's
stall: **one continuation solve plus three final solves**, 0.086 h, **116 CUDA
tests passed**. Each continuation's raw exit 2 retains its original rejection policy;
the outer-amplitude overlap assessment passes, while the ergoregion point
retains the tidal rejection. No NaN/OOM/traceback in either continuation log.
Both sampled GPU peaks were **54665 MiB (53.38 GiB)**.

The outer/throat continuation directories occupy **11 MB / 1.7 MB**.
Fields, checks, original plans and capped-job logs remain on NFS; numerical
archives are not yet published in tracked results. Finest throat-ergoregion
fields: `ring/diagnostic_240x40.npz`, SHA256
`0527671f48eb67f8137d7466a5756f725a6f4c716f454d09e5e9e08a9a7b9715`.
Accepted weaker overlap fields: `accepted_overlap.npz`, SHA256
`3db8efad05afbeae9946c784cf82ccabcf2777340e22b5d5fc51ba175cdffa0b`.

Configurations: [direct insertion](../../grteclyn-wrapper/scripts/campaigns/ringwormhole/configs/ergoregion108.json),
[outer continuation](../../grteclyn-wrapper/scripts/campaigns/ringwormhole/configs/ergoregion108_continuation.json),
[throat continuation](../../grteclyn-wrapper/scripts/campaigns/ringwormhole/configs/ergoregion108_throat.json).
The source is the accepted CMA-ES railgun finalist with shift/lapse 1.080970704;
its fields supply an unsolved guess, never an inherited wormhole acceptance.
The earlier Cartesian-origin certificate failed; these independent throat-domain
checks do not qualify a Cartesian export or evolution.
