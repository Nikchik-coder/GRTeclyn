# Fixed-area extension validation, October 31

The `factored` recheck (code 6020e9f7) validates potential-only candidate
00071 on 150x30, 180x36 and 210x42 grids. Each deliberately perturbed seed
requires two Newton updates and reaches about 1e-15. Full exoticity is
2.188430376060 versus massless reference 4.684238262942 at fixed minimal
throat area, J and asymmetry; peak tides are 2.593 times the reference,
inside the prescribed four-times cap. All independent constraints, off-grid,
surface and integral checks pass. Radial stability remains not assessed.

`strict`, `refinement`, `derivatives` and `linear_step.json` preserve the
failed investigations leading to the fix. Expanded polynomial evaluation
lost the double zero at the nonzero vacuum through cancellation. Factored
evaluation retains the same polynomial and removes the amplified far-end
residual. Refreshing Jacobians or subtracting linear differentiation
backgrounds alone did not fix refinement.

`boson-k0` is the first nonrotating pilot (code fd81f1d5): 40 seed combinations,
three numerically solved finite seeds and nine CMA proposals; no accepted
model. Candidate 00046 is bound and localized but violates the ordinary
energy budget and stationary constraints. It is retained only as a warm
seed requiring a fresh solve and every acceptance check. Constant scores
for infeasible proposals ended this pilot early; subsequent searches use
constraint-sensitive scores without relaxing any gate.

Fields and numerical records are retained; text deployment prefixes are
made repository-relative. No evolution plotfiles or checkpoints are included.

`boson-k1` (code 6020e9f7) completed at 15:51 MSK: 40 linear-mode
attempts unresolved and 40 finite-seed solves failed, across two backgrounds,
five masses and four amplitudes. No nonzero solution or CMA evaluation;
this is initialization failure, not evidence that the branch cannot exist.
The opposite signed winding is tested separately.

`boson-k0-local` (code cb72d5a3) was stopped after 58 local Nelder-Mead
proposals to replace sequential rejection scoring with simultaneous energy
and tidal penalties. The launcher defaulted to NM because `--engine cma`
was omitted. Candidate 00053 has X_full=1.904439, E_b/R_A=0.994685, and
peak tide 0.256794 versus cap 0.128492: it is rejected, not a winner.
Only the starting matter seed, this diagnostic candidate, reference fields
and complete trace/log are archived; other provisional fields remain in the
stopped cluster run. The new CMA run re-solves 00053 before using it.
