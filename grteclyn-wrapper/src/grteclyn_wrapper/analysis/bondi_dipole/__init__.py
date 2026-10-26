"""Reductions behind the Bondi dipole pack (results/bondi-dipole-runaway).

Each module runs from the wrapper's environment as
``python -m grteclyn_wrapper.analysis.bondi_dipole.<module>`` and writes into the pack:

  star_family_scan            stars/star_family.csv: M(omega) of the dressed stars of
                              both signs, the table the matched pairing was chosen from
  star_family_massratio_scan  stars/star_family_massratio.csv: both branches out to
                              omega 1.0, for the mass-ratio runs
  fit_mass_law                campaign/06_mass/mass_law.csv: a against the partner's
                              mass at d 20
  track_wells                 a same-sign pair's two stars from its chi slice cache
                              (well_tracking.dat; pack_runaway.sh runs it at packing)

The figures drawn from the pack are in ``grteclyn_wrapper.visualisation.bondi_dipole``;
the reruns' convergence and constraint checks are the scripts in
``grteclyn-wrapper/scripts/analysis/bondi_dipole/``.
"""

import pathlib

REPO = pathlib.Path(__file__).resolve().parents[5]
PACK = REPO / "results" / "bondi-dipole-runaway"
