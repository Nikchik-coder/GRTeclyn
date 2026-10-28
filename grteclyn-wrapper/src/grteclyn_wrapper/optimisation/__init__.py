"""Campaign M: rotating wormholes held open by an exotic scalar with a
potential, and the search for the cheapest one in exotic matter.

  matter_equations   the matter field forms and MatterCollocationProblem
                     (the J, R_e and area pins)
  potentials         scalar potentials, every one a kink
                     psi^2 (psi - psi_minus)^2 Q(psi)
  exoticity          the bill X = |VIQ| / R_e, the throat, NEC along rays,
                     the tidal tensor at the throat
  solver/            Newton, the Jacobians, the jax device (physics-free)

Reads the published spinning package (analysis/spinning_wormhole: its
spectral pieces, Solution, and the V = 0 solver as the reference); nothing
outside this package imports it, because develop ships without it.
Scripts: grteclyn-wrapper/scripts/optimisation/.  Plan and record:
research/optimisation/.
"""
