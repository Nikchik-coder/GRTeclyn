# Deeper single-ring frequency continuation

Omega=0.70 passes 96x12 / 128x16 / 160x20. Omega=0.67 fails Newton and independent equations on 96x12; the bounded scan stops after four solves. The rejected field is retained, with no accepted export for it. Original validation gates remain unchanged.

Accepted omega=0.70 measurements:

{
  "frequency": 0.7,
  "accepted": true,
  "directory": "frequency_01",
  "amplitude": 0.015689536135570097,
  "M_ADM_estimate": 1.2610721027861238,
  "J_volume": -1.3063224292437658,
  "lapse_min": 0.4214586705249313,
  "dragging_max": 0.13047193758392522,
  "gtt_max": -0.13671602957183288,
  "shift_norm_over_lapse_max": 0.5103411663640276,
  "ergoregion_sampled": false
}

Four threads, 160 GiB, 1800 s cap, chunks 128, no AMR checkpoints. Second GPU node/card 0, 18:12:10–18:14:08 MSK, code 4d1c4d23. This does not establish a physical maximum or branch termination.
