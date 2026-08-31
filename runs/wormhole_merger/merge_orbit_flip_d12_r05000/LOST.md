# `merge_orbit_flip_d12_r05000` — the arm whose data is gone

This is the **narrow lapse window** arm: restarted from `r03000`'s `Chk05000`
(t = 50), with core damping left at its built-in defaults — `lapse_start = 1e-6`,
`lapse_full = 1e-8`, which on this grid is roughly three cells. It died with a
NaN in `h11` at **t = 52.09**, a gain of 0.02 over the undamped arm: the window
was aimed so deep that it never touched the phantom that kills the run.

**Its `.dat` streams, frames and movies no longer exist.** The run directory was
removed together with its scratch cell during the 2026-08-31 disk sweep, before
anything had been extracted from it. What survives is the launcher banner and
the evolution log — which is enough for the two facts the campaign uses it for
(the damping thresholds it ran with, and the death time), and for nothing else.

The result is reproducible: restart from `r03000/BinaryWormholeChk05000` with
`core_damping_enabled = 1` and no `core_damping_lapse_*` overrides. Nobody has
a reason to — the wider window in `r04000` already answered the question.

Read the death out of the log with `zgrep`, not `grep`:

    zgrep -n "NaN" run.log.gz
    zgrep -oE "TIME = [0-9.]+" run.log.gz | tail -1
