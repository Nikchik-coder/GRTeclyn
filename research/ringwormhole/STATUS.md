# Ring–wormhole campaign — status

Updated **2026-11-05 (MSK)**. Branch: `feature/optimisation`.
Current findings only; detailed run records and numerical checks are in
[optimisation STATUS](../optimisation/STATUS.md).

## Live

No live or queued run. Both completed studies exited successfully on the
first node/card 0, with checkpoints OFF and stationary fields/logs retained.
Last close-out check, November 5: both GPUs idle; scratch clean,
**4 KB cache / 303 GB free**. Second node not listed. No remaining ETA.

## Planned (nothing launches without the go)

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

| Study | Frozen source | Finished MSK | Output on persistent storage |
|---|---|---|---|
| Weak ring, three grids | `f9f29a566` | Nov 5 09:40:51 | `runs/optimisation/railgun_throat_validation_20261105_r3/` |
| Matched-spin control | `bb0b68851` | Nov 5 10:01:55 | `runs/optimisation/railgun_matched_control_20261105/` |

Accepted fields: `accepted_ring.npz` and `matched_spin.npz`, respectively.
Arrays, checks and logs remain on NFS; these numerical archives are not yet
published in the tracked results pack. Configurations:
[ring validation](../optimisation/studies/railgun_throat_validation.json),
[matched control](../optimisation/studies/railgun_matched_control.json).
