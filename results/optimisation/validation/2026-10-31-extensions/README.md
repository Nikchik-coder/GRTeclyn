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

`boson-kminus1` (code d9a1044d) was stopped after all 40 seed combinations.
38 finite solves failed. Two numerical fields are unbound, nonlocalized and
violate the unused equations by orders of magnitude. They are diagnostic
failures, not wormhole solutions, and were not passed to a production search.
A separate continuation route starts from the saved symmetric winding seed.

`boson-k0-joint` (code ea97e390) was stopped after 32 CMA proposals to
replace fixed off-grid rejection penalties with measured residual excesses.
No candidate passed. The complete trace and two contrasting fields (tidal
failure and off-grid failure), plus reference fields, are retained. The next
run uses the graded checks and a lower initial phantom mass.

`s0-continuation` (code 8264945e) re-solved the old symmetric winding
seed and reached the target J at fixed true area, then gamma=-0.883573.
It was stopped after 55 attempts to test whether a tighter Newton stopping
target would resolve the unused-equation rejections. All successful fields
are retained; the strict repeat below does not establish that stopping error
caused those rejections.
The restart uses a 1e-14 target from step_0052. These intermediate models
have different asymmetry from D21 and are not matched D21 results.

`boson-k0-cma-r2` (code 8264945e) finished at 16:31:21 MSK, exit 2.
All 96 proposals were rejected: 94 ABOVE_GATE and two FAILED. Overlapping
reasons include energy budget (87), tides (46), stationary constraints,
quadrature and localization (22 each), off-grid equations (14) and
positivity (two). No validated improvement was obtained. The complete trace,
all returned fields, reference checks, outcome and job log are archived.
Rejected low-X proposals do not replace the potential-only finalist.

`s0-continuation-strict` (code 932053bd) finished at 16:16:40 MSK, exit 2.
It retains the 1e-14 Newton target and all physical gates. The last passing
asymmetry is gamma=-0.915914362, short of the D21 target -pi. The next trial
has Newton residual 8.92e-16 but E19=1.00734e-8 exceeds the unchanged 1e-8
limit. This is an independent-constraint rejection, not Newton failure or
proof that the rotating branch does not exist. All passing fields, attempted
step diagnostics, manifest and job log are retained. No D21 boson winner.

The current validated extension remains the potential-only fixed-area result
at the top of this file. It uses a different geometric normalization from
the fixed-equatorial-radius article search and is not a new record in that
comparison. Radial instability screening remains disabled and unvalidated.
