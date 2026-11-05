# Ring–wormhole campaign — status

Updated **2026-11-05 (MSK)**. Branch: `feature/optimisation`.
Launchers, workers and run configurations live in the wrapper's
[campaign directory](../../grteclyn-wrapper/scripts/campaigns/ringwormhole/README.md).
This directory holds STATUS and research writing. Earlier weak-ring records:
[optimisation STATUS](../optimisation/STATUS.md).

## Live

No live or queued runs. The original paired spin+ring experiment is complete:
**14 solves total**, seven for the coupled arm and seven for its unchanged
ring-free control. Last job finished **Nov 5 12:24:38 MSK**, before the original
13:07:01 deadline. Both GPUs on the first node are idle; checkpoints OFF;
fields/logs retained on NFS. Scratch clean: **4 KB cache / 302 GB free**.
Second node not listed. No remaining ETA or automatic follow-on.

## Planned (nothing launches without the go)

- Obtain co-rotation at the specified mouth by controlling the measured
  geometric flux, rather than assuming that more negative total J+ selects
  that orientation. The completed pilot reached the opposite orientation;
  a different control choice needs a new bounded go.
- Try slightly less throat matter to retain g_tt > 0 while bringing peak tide
  below 0.333333. The present ergoregion solution exceeds that ceiling by 6.22%.
- Compare a qualified new point with a ring-free control at its own area and J.
  The older matched-spin control applies only to the weak ring.
- Test stationary qualified configurations in evolution before assessing stability.

## Main results

**Independent wormhole rotation + rotating matter: the completed pilot
counter-rotates at the specified xi=0 cut.** Both arms reproduce the same
true R_A=2 and J+ **-0.7963901140** on 210x36 / 224x38 / 240x40, with total-J
match error **1.55e-15**. The coupled configuration has X_full
**2.498042477464** (**20.484838% below static**); its ring-free rotating control
has **2.051637544074** (**34.694349% below static**). The combined configuration
therefore requires **21.758470% more exotic support than that control**.
It establishes no additional benefit from matter in this counter-rotating case.

All physical gates pass. The coupled geometric flux at xi=0 **+0.09154397967**
opposes matter flux **-0.8879340937**; their sum gives the total J+ above.
Relative end angular velocity is **+0.04068994820**. This specified-cut flux
is not a unique global split into object spins. Original rows retain the
sole rejection `fluxes_not_co_rotating`; the co-rotation target remains failed.
The originally approved unstarted control arm was completed separately,
without another coupled solve or an increase in the total 14-solve budget.

Coupled/control independent Einstein defects: **6.30e-12 / 4.27e-12**;
scalar defects: **8.33e-12 / 2.89e-12**, all on 49x21 points.
Finest-pair X_full drifts: **2.03e-13 / 6.15e-14**. Coupled E_b/R_A
**0.8983325013**; peak tides **0.2292231669 / 0.1336938905**, both below
0.3333333333. Actual coupled throat g_tt **-0.1134992190**, shift/lapse
**0.6590485977**: no throat ergoregion in the plus-end inertial frame.
Large far-side coordinate g_tt is not a throat-ergoregion detection: the
opposite infinity rotates in these coordinates.

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

**Model:** a two-ended wormhole with canonical rotating scalar matter,
free mass=1, winding k=+1. True minimal area **16 pi (R_A=2)**, gamma=0,
massless phantom potential V=0. Ring-driven cases keep both infinities
nonrotating. The independent-spin pilot permits relative end-frame rotation
and two-ended asymmetry. X_full measures integrated phantom-field exoticity.
No stability result is established by these stationary solves.

| Configuration | X_full | Reduction against static Ellis | Outcome |
|---|---:|---:|---|
| Static Ellis | 3.141592654 | — | reference |
| Weak exterior ring | 3.106532920 | 1.115986% | three grids pass |
| Stronger matter overlapping throat | 2.491951888 | 20.678708% | three grids pass with overlap allowed |
| Throat ergoregion | 2.422262173 | 22.897000% | equations pass; tide exceeds cap |
| Independent spin + matter, opposite fluxes | 2.498042477 | 20.484838% | physical gates pass; intended co-rotation fails |
| Ring-free control matched to opposite-flux pilot J | 2.051637544 | 34.694349% | three grids pass |
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
| Independent-spin coupled arm | `985121bb7` | Nov 5 12:12:33 | `runs/ringwormhole/spin_ring_co_rotating_20261105/` |
| Original independent-spin control remainder | `1f693f484` | Nov 5 12:24:38 | `runs/ringwormhole/spin_ring_control_20261105/` |

The independent-spin coupled arm ran **12:07:01–12:12:33 MSK**, exit 2
(orientation target); its original control remainder ran **12:22:25–12:24:38**,
exit 0. Four continuation steps and three perturbed final solves per arm:
**14 total**. 125/133 CUDA tests passed; the guarded remainder passed 140 CPU
tests. Parent rejection records remain unchanged, and a one-shot marker
prevents repeating the control. No NaN/OOM/traceback in either log.
Sampled GPU peaks: **54663 / 38255 MiB**; retained outputs **2.5 / 1.5 MB**.
Coupled finest fields SHA256:
`1c9d32f165b8bdfc51eac32777d3eb2b18dd8b3e13fc7a65568aa85b77bdeb25`;
`control_accepted.npz` SHA256:
`42ea87d72d2e43f1e7904619a753ff825515bb1578c6d254cefe710fa251b52c`.
Paired numbers are in the control directory's `outcome.json`;
[original configuration](../../grteclyn-wrapper/scripts/campaigns/ringwormhole/configs/spin_ring_co_rotating.json).

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
