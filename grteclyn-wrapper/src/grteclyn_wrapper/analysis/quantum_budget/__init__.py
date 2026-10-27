"""Quantum-budget campaign (campaign F): the Ford-Roman compliance factor.

Job F1 of research/optimisation/Quantum Budget Wormhole Search.md: score a
stationary wormhole background against the Ford-Roman quantum inequality --
the compliance factor F, with F <= 1 meaning quantum fields could legally
supply the exotic matter.  The measurement runs on the spinning-wormhole
solver's saved Solutions (results/spinningwormhole/solutions/), so nothing
is re-solved and no GPU is involved.

Module split:

- conventions:  the F definition, the Ford-Roman bound, Planck scaling.
- curvature:    orthonormal Riemann of the Kleihaus-Kunz ansatz (sympy,
                lambdified once per process) -> the validity scale ell_c.
- stress:       the phantom scalar's energy density for stationary observers.
- compliance:   the evaluator (QI bound x sampling policy x observer class).
- catalogue:    walk the saved solution legs, synthesize static anchors.
"""
