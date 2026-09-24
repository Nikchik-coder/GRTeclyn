#!/usr/bin/env python3
"""Check wormhole-merger run NAMES against their packed evolution_params.txt.

    name_check.py [<pack-root>] [--report FILE] [--templates] [--include-copies]

A run's name is the first thing anyone reads about it, and until 2026-09-24
nothing checked it: four arms named q1e2 ran without their quadrupole.  The
grammar -- what each name token claims about the params -- is RULES below; it
is written out as <pack-root>/name_grammar.tsv (the human-readable grammar,
with the holds/fails counts this run measured) and read back from that text,
so the TSV is the contract and this file supplies the derived quantities.
run_index.py calls findings() for its name_check column.  --report writes a
per-run account of every failure.  Written 2026-09-24 from a full sweep of the
pack (95 rules, 149 runs; every failure explained in research/merger/GLOSSARY.md).

TSV columns: token_regex  param  expected  compare  note  holds  fails
  token_regex  fullmatch on ONE underscore-separated name token, unless the
               note says "spans tokens": then re.search on the whole name
               (the regex carries its own (?:^|_) ... (?:_|$) anchors).
               A trailing ".__keep" (a pack copy) is stripped first.
  param        an AMReX key of evolution_params.txt (code default when the
               key is absent -- see DEFAULTS), "key[i]" for a vector
               component, "derived:<name>" (computed below, formula in the
               note), "(consumer)" (visible only in the packed streams) or
               "(none)" (a label with nothing to test).
  expected     Python expression in g1, g2, ... (the regex groups, strings).
  compare      eq | approx (rel 1e-9) | abs_approx (|a-b| <= 1e-6) |
               file_exists (the expected file is in the packed run dir) | -
  holds/fails  counts over the packed runs whose name matches; a run whose
               value cannot be computed (no params, no stream) is counted in
               the report as untestable, not here.

Packed runs are walked with results/merger/analysis/pack_paths.iter_runs.
A "X.__keep" directory with X beside it is a byte-identical pack copy and is
skipped (gpu_hours.py's rule), as is a second directory of the same name;
--include-copies counts them too.
"""

from __future__ import annotations

import argparse
import math
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent

# --------------------------------------------------------------------------
# the rule set
# --------------------------------------------------------------------------
# (token_regex, param, expected, compare, note)
RULES: list[tuple[str, str, str, str, str]] = [
    # ---- geometry: separation, box, resolution, depth ----------------------
    (r"d(?!(?:65|75)$)(\d+)", "derived:separation", "float(g1)", "approx",
     "d<N>: throat separation d = |wormhole_centerA - wormhole_centerB| (offsets from `center`; "
     "centerB defaults to -centerA, centerA to (0,0,5)); BinaryBH-format params (bbh_control_*): "
     "|bh1.offset - bh2.offset|. Integer spelling; the two half-integer probes use the next rule"),
    (r"d([67])5", "derived:separation", "float(g1)+0.5", "approx",
     "d65 / d75 = 6.5 / 7.5: decimal point dropped (placement probes only). The spelling is "
     "ambiguous in general (d15 could be 1.5 or 15); no other half-integer d exists in the pack"),
    (r"p(\d+)", "derived:p_A", "float(g1[0] + '.' + g1[1:])", "approx",
     "p<NNN>: Bowen-York momentum per throat, p_A = |wormhole_momentumA| (B defaults to -A, so net P = 0); "
     "first digit = integer part: p012 = 0.12, p045 = 0.45, p02 = 0.2. Binaries push tangentially (y, "
     "orbit in the x-y plane); s20_boost_p02 pushes one throat along z. BinaryBH: |bh1.momentum|"),
    (r"L(\d{2,})", "L", "float(g1)", "approx",
     "L<NN>: box side L (code units; the cube is [0,L]^3 with the physics at center = L/2). "
     "L64 / L128. BinaryBH alias: geometry.prob_extent[0]"),
    (r"L(\d)", "max_level", "int(g1)", "eq",
     "ladder_L<N> ONLY: L<one digit> is the refinement level of the p012 refinement ladder "
     "(restarted from Chk05000), NOT the box (the box token has >= 2 digits)"),
    (r"(?:s\d+)?ml(\d+)", "max_level", "int(g1)", "eq",
     "ml<N>: max_level N (dx_finest = (L/N1)/2^N). Also inside the stage label s16ml3"),
    (r"lvl(\d+)(?:from0|chk|down)?", "max_level", "int(g1)", "eq",
     "lvl<N>[from0|chk|down]: max_level N (same meaning as ml<N>; lvl is the merger arms' spelling)"),
    (r"lvl\d+from0", "derived:restart_step", "None", "eq",
     "lvl<N>from0: run at max_level N from t = 0, no amr.restart (restart_step None)"),
    (r"lvl\d+chk", "derived:writes_checkpoints", "True", "eq",
     "lvl<N>chk: the checkpointed twin; writes_checkpoints = checkpoint_interval > 0 AND "
     "amr.checkpoint_files_output != 0 (AMReX default 1)"),
    (r"lvl\d+down", "derived:is_restart", "True", "eq",
     "lvl<N>down: down-step -- restarted from a FINER-level checkpoint with max_level lowered to N "
     "(merge_headon_flip_d8_v1_lvl3down_t100_r03500: level-5 Chk03500 -> level 3)"),
    (r"n(\d+)", "N1", "int(g1)", "eq",
     "n<N>: base-grid cells per side N1 (= N2 = N3). BinaryBH alias: amr.n_cell[0]"),
    (r"s1uni(\d+)", "N1", "int(g1)", "eq",
     "s1uni<N>: Stage-1.4 unigrid control with N1 = N"),
    (r"s1uni\d+", "max_level", "0", "eq",
     "s1uni<N>: unigrid, max_level 0"),
    (r"stage1|s15", "max_level", "2", "eq",
     "stage1 / s15: Stage-1 (gauge+dissipation) and Stage-1.5 (fixed-grid tagger) shakedown, "
     "max_level 2 (runs_registry.tsv, 01_single_throat block)"),
    (r"t(\d{3})", "stop_time", "float(g1)", "approx",
     "t<NNN>: stop_time (code units = M). For a restart leg it is the leg's stop_time. BinaryBH "
     "alias: evolution.stop_time. Names without a t token do not encode stop_time"),
    # ---- seeds ------------------------------------------------------------
    (r"(?:^|_)eps_([pm])(\d)e(\d)(?:_|$)", "wormhole_seed_amplitude_A",
     "(1 if g1 == 'p' else -1) * int(g2) * 10.0 ** -int(g3)", "approx",
     "spans tokens (eps + sign-mantissa-exponent): eps_p1e2 = +1e-2, eps_m1e3 = -1e-3. Declared "
     "spherical Gaussian seed psi -> psi(1 + eps g(r)) on the throat (paper Sec. II.D); "
     "B defaults to A, so a two-throat eps run seeds both"),
    (r"(?:^|_)eps_([pm])(\d)e(\d)(?:_|$)", "derived:seed_eps_effective",
     "(1 if g1 == 'p' else -1) * int(g2) * 10.0 ** -int(g3)", "approx",
     "spans tokens. EFFECTIVE seed: the params value, set to 0 if the run's t = 0 L2_Ham is "
     "identical (all printed digits) to a packed run with the same initial-data keys and no eps "
     "(the binary ignored the key). Restart legs: taken from the parent run named in amr.restart"),
    (r"q(\d)e(\d)", "wormhole_seed_l2_amplitude_A", "int(g1) * 10.0 ** -int(g2)", "approx",
     "q<m>e<k>: quadrupolar seed eps2 = m*10^-k (psi -> psi(1 + eps2 g(r) P2(cos theta)) about z; "
     "paper Sec. II.D). q1e2 = 0.01, q5e2 = 0.05, q5e3 = 0.005"),
    (r"q(\d)e(\d)", "derived:seed_l2_effective", "int(g1) * 10.0 ** -int(g2)", "approx",
     "EFFECTIVE quadrupole (same test as seed_eps_effective, against runs with no l2 seed). "
     "Catches the 2026-09-23 trap: the campaign pin main3d_boost_2026-09-08.ex does not read "
     "wormhole_seed_l2_amplitude_* (binaries.tsv), so an eps2 arm launched on it ran with NO "
     "quadrupole although its params say otherwise"),
    (r"pureq", "wormhole_seed_amplitude_A", "0.0", "abs_approx",
     "pureq: pure quadrupole -- spherical seed explicitly 0, q<..> token carries eps2"),
    (r"hold", "derived:any_seed", "False", "eq",
     "hold: one throat held at its exact static data -- no declared seed "
     "(wormhole_seed_amplitude_A = wormhole_seed_l2_amplitude_A = 0)"),
    # ---- gauge / numerics ---------------------------------------------------
    (r"eta(\d+)", "eta", "float(g1)", "approx",
     "eta<N>: Gamma-driver shift damping eta = N (production 1.0)"),
    (r"lp(\d+)", "lapse_power", "float(g1)", "approx",
     "lp<N>: Bona-Masso lapse_power N (1 = 1+log; 2 = harmonic-class d_t alpha = -2 alpha^2 K)"),
    (r"lc(\d+)", "lapse_coeff", "float(g1)", "approx",
     "lc<N>: Bona-Masso lapse_coeff N (production 2.0). lc4 exists only as a template"),
    (r"sg(\d)(\d+)", "sigma", "float(g1 + '.' + g2)", "approx",
     "sg<NN>: Kreiss-Oliger sigma with the '.' deleted by run_single.sh (WHM_SIGMA): "
     "sg00 = 0.0, sg01 = 0.1, sg10 = 1.0"),
    (r"lapse(\d)", "wormhole_initial_lapse_type", "int(g1)", "eq",
     "lapse<N>: initial lapse type (run_single.sh WHM_LAPSE_TYPE): 5 = the drainhole's exact static "
     "lapse e^u, 6 = 5 x the origin-isolating collar"),
    (r"fg", "tagging_type", "1", "eq",
     "fg: fixed nested grids (FixedGridsTagger) -- run_single.sh appends _fg when WHM_TAGGING_TYPE != 0"),
    (r"tl(\d+)", "tagging_L", "float(g1)", "approx",
     "tl<N>: tagging_L with '.' deleted (run_single.sh WHM_TAGGING_L). No packed run uses it"),
    (r"dt0(\d+)", "dt_multiplier", "float('0.' + g1)", "approx",
     "dt0<NN>: Courant factor dt_multiplier = 0.<NN> (dt005 = 0.05, dt01 = 0.1; production 0.02)"),
    (r"halfstep", "dt_multiplier", "0.01", "approx",
     "halfstep: dt_multiplier halved, 0.02 -> 0.01"),
    (r"cf(\d\d)", "min_chi", "10.0 ** -int(g1)", "approx",
     "cf<NN>: chi floor min_chi = 1e-NN (floor ladder: cf08 / cf10 / cf12)"),
    (r"chireg", "chi_rhs_floor", "1e-8", "approx",
     "chireg: chi regularisation on -- chi_rhs_floor 1e-8 (floor applied only where 1/chi is used)"),
    (r"chireg", "min_chi", "1e-20", "approx",
     "chireg: ... with the evolved-chi floor lowered to 1e-20"),
    (r"lowfloor", "min_chi", "5e-10", "approx",
     "lowfloor: min_chi 5e-10 instead of 1e-8"),
    (r"autopsy", "nan_autopsy", "1", "eq",
     "autopsy: per-cell NaN autopsy report armed"),
    (r"step1", "max_steps", "1", "eq",
     "step1: one coarse step only (stop_time is left at the template's value)"),
    (r"chk", "derived:writes_checkpoints", "True", "eq",
     "chk: rolling checkpoints on (checkpoint_interval > 0 and amr.checkpoint_files_output != 0)"),
    (r"r(\d{5})", "derived:restart_step", "int(g1)", "eq",
     "r<NNNNN>: continuation leg restarted from BinaryWormholeChk<NNNNN> (run_single.sh appends "
     "_r<step> from WHM_RESTART). restart_step = digits after 'Chk' in amr.restart; a log-only arm "
     "without params falls back to launch_banner.txt's '[whm] restart' line"),
    (r"r(\d{5})", "derived:t_restart_from_stream", "int(g1) * 0.01", "abs_approx",
     "r<NNNNN>: the step is the PARENT's coarse-step count, so t_restart = NNNNN x 0.01 (every "
     "parent ran dt = 0.02 x L/N1 = 0.01); checked as first stream row minus one coarse step of the "
     "leg (streams restart at t_restart + dt, with no header line)"),
    # ---- initial data -------------------------------------------------------
    (r"a(\d)(\d?)", "wormhole_throat_radius_A", "float(g1 + '.' + (g2 or '0'))", "approx",
     "a<N>[N]: throat scale a with '.' dropped (a1 = 1, a15 = 1.5, a3 = 3; production 2). "
     "Set equal on B in every packed a-arm"),
    (r"m(\d)(\d+)", "wormhole_drainhole_mass_A", "float(g1 + '.' + g2)", "approx",
     "m<NN>: drainhole (ADM) mass m with '.' dropped: m05 = 0.5 (production 1.0); B defaults to A. "
     "COLLISION: run_single.sh's own _m<mass> suffix (WHM_BARE_MASS) means wormhole_bare_mass_A/B; "
     "no packed run used it and bare mass is 0 in all of them"),
    (r"mu(\d+)", "derived:mu", "float(g1)", "approx",
     "mu<N>: mass-to-scale ratio mu = m/a = wormhole_drainhole_mass_A / wormhole_throat_radius_A "
     "(template params_single_mu2_eps_p1e2_t100: a = 1, m = 2). No packed run; that template's "
     "t100 is a-scaled (stop_time 50, 'stop_time 50 here = t 100 at a = 2')"),
    (r"helfer", "wormhole_helfer_correction", "1", "eq",
     "helfer: Helfer/Ning one-body superposition correction on (window auto = d/3 unless w<N>)"),
    (r"plain", "wormhole_helfer_correction", "0", "eq",
     "plain: plain superposition (the Helfer twins' reference)"),
    (r"w(\d+)", "wormhole_helfer_width", "float(g1)", "approx",
     "w<N>: Helfer window width N (auto = d/3 = 4 at d = 12)"),
    (r"single|stage1|s15|s16ml\d+|s1uni\d+|s20", "derived:throat_B_present", "False", "eq",
     "single / stage labels: ONE throat -- throat B removed by wormhole_throat_radius_B = 0 "
     "(B defaults to A, so it must be set; SimulationParameters.hpp)"),
    (r"merge|ctrl|place", "derived:throat_B_present", "True", "eq",
     "merge / ctrl / place: two throats (wormhole_throat_radius_B > 0)"),
    (r"flip", "wormhole_phi_sign_B", "-1.0", "eq",
     "flip: throat B's scalar profile reversed, phi = phi_A + sigma phi_B with sigma = -1 (opposite "
     "scalar charges attract; the merger channel). Default +1 (like charges repel)"),
    (r"twin", "wormhole_phi_sign_B", "-1.0", "eq",
     "twin: the p = 0.12 'twin' series (one-knob twins of the plain flipped merger); the flip is "
     "implied, not spelled"),
    (r"headon", "derived:p_A", "0.0", "abs_approx",
     "headon: no Bowen-York momentum (p_A = |wormhole_momentumA| = 0); pair falls from rest"),
    (r"rest", "derived:p_A", "0.0", "abs_approx",
     "rest: released from rest (p_A = 0)"),
    (r"place", "derived:p_A", "0.0", "abs_approx",
     "place: placement probe -- the head-on scout's pair at rest at separation d, one step (with step1)"),
    (r"orbit|spiral|boost", "derived:p_A_nonzero", "True", "eq",
     "orbit / spiral: tangential push p_A > 0 (value in the p<NNN> token); boost: the single boosted "
     "throat of Stage 2.0 (P along z)"),
    (r"bbh", "derived:is_binarybh_params", "True", "eq",
     "bbh: vacuum binary-black-hole control -- params in the stock BinaryBH format (bh1.* / bh2.*, "
     "amr.*, evolution.*), no scalar; bh1.mass = bh2.mass = 0.9615 (bare puncture mass)"),
    (r"grtresna|bridge", "derived:has_recipe_initial_data", "True", "eq",
     "bridge_grtresna: constraint-solved GRTresna data read through ExternalGridInitialData "
     "(recipe_initial_data_file set)"),
    # ---- interior devices ---------------------------------------------------
    (r"nodamp", "core_matter_damping", "0", "eq",
     "nodamp: core matter damping off"),
    (r"damped", "core_matter_damping", "1", "eq",
     "damped: core matter damping on (ladder twins)"),
    (r"rw", "derived:damping_radius_window", "True", "eq",
     "rw: damping radius window on (core_damping_radius_start > 0 and core_damping_radius_full > 0; "
     "rw_r05000: full inside 0.5, off by 0.7, from t = 33)"),
    (r"nofill", "core_freeze_fill", "0", "eq",
     "nofill: interior fill (CoreFreezeFill) off -- the 'unmasked' wall probes"),
    (r"(?:late)?freeze2?|fill", "core_freeze_fill", "1", "eq",
     "freeze / freeze2 / latefreeze (/ fill, templates only): smooth interior fill on (every RHS x "
     "(1 - W(r)) between core_fill_radius_full and _start from core_fill_from_time). freeze2 = the "
     "fill-window twin"),
    (r"fillnarrow", "core_freeze_fill", "1", "eq",
     "fillnarrow: head-on fill-radius twin, fill on ..."),
    (r"fillnarrow", "core_fill_radius_full", "1.0", "approx",
     "fillnarrow: ... with radii 1.0 / 1.5 instead of V1c's 1.2 / 1.8"),
    (r"narrow", "core_fill_radius_full", "1.3", "approx",
     "narrow: orbital freeze skin r_full 1.3 / r_start 1.8"),
    (r"wide", "core_fill_radius_full", "1.5", "approx",
     "wide: orbital freeze skin one cell wider, r_full 1.5 / r_start 2.0"),
    (r"late", "core_fill_from_time", "55.5", "approx",
     "late: fill armed late, t = 55.5 instead of the programme's 53.0 (freeze_narrow_late)"),
    (r"v1", "core_freeze_fill", "0", "eq",
     "v1: Phase-3 head-on scout family (d = 8 from rest, chi regularisation, autopsy armed) with the "
     "fill OFF (the V1 template)"),
    (r"v1c", "core_freeze_fill", "1", "eq",
     "v1c: the V1c late-freeze template (fill armed, t = 26.5 or 25.0) and its twins"),
    (r"v1c?", "chi_rhs_floor", "1e-8", "approx",
     "v1 / v1c: inherit the scout's chi regularisation (chi_rhs_floor 1e-8, min_chi 1e-20)"),
    (r"v2", "L", "128.0", "approx",
     "v2: the V2 production spiral (L = 128, N = 256; L128 is also spelled out)"),
    # ---- extraction / consumer ---------------------------------------------
    (r"prof|mouths", "core_radial_profile", "1", "eq",
     "prof / mouths: in-code radial core profile on (core_radial_profile.dat)"),
    (r"prof|mouths", "(stream)", "'core_radial_profile.dat'", "file_exists",
     "prof / mouths: the in-code profile was actually written (a binary older than 2026-09-15, e.g. the "
     "campaign pin main3d_boost_2026-09-08.ex, ignores core_radial_profile silently)"),
    (r"mouths", "(consumer)", "'horizon_scan.dat'", "file_exists",
     "mouths: consumer run with per-mouth areal radius + horizon scan (profile headon); proxy: the "
     "packed horizon_scan.dat exists"),
    (r"scalar", "(consumer)", "'scalar_modes.dat'", "file_exists",
     "scalar: consumer flag --scalar-modes (profiles headon-modes / orbit-modes); not in params; "
     "proxy: packed scalar_modes.dat exists (the stream also exists on some runs without the token)"),
    (r"diag", "write_extraction", "1", "eq",
     "diag: Weyl-extraction diagnostic pass -- raw sphere dumps on (Weyl4_extraction_NNNNNN.dat), no consumer"),
    (r"crosscheck|wave", "activate_extraction", "1", "eq",
     "crosscheck / wave: in-code Weyl4 extraction on (validation against the consumer psi4)"),
    # ---- place: the scout's pair ------------------------------------------------
    (r"place", "wormhole_phi_sign_B", "-1.0", "eq",
     "place: the placement probes are the head-on scout's FLIPPED pair; the flip is not spelled"),
    # ---- absence rules: an unnamed knob is at its production value -------------
    # runs/wormhole_merger/README.md 'Reading a run name': "Everything not named in the
    # suffix is identical across the binary runs".  re.search on the whole name.
    (r"^(?!bbh_)(?!.*(?:^|_)(?:(?:s\d+)?ml\d+|lvl\d+[a-z0-9]*|L\d|s1uni\d+|stage1|s15)(?:_|$))",
     "max_level", "3", "eq",
     "spans tokens (ABSENCE rule): no level token (ml/lvl/L<d>/stage label) -> production max_level 3 "
     "(run-tree README: 'Everything not named in the suffix is identical across the binary runs', "
     "max_level = 3). Not applied to bbh_*. Its FAILS are restart legs whose raised max_level (5-6) "
     "sits in the template or the launch (launch.sh --max-level / WHM_MAX_LEVEL add no suffix) and "
     "is NOT in the name"),
    (r"^(?!bbh_)(?!.*(?:^|_)(?:L\d{2,}|v2)(?:_|$))", "L", "64.0", "approx",
     "spans tokens (ABSENCE rule): no L<NN>/v2 token -> box L = 64"),
    (r"^(?!bbh_)(?!.*(?:^|_)(?:n\d+|L\d{2,}|v2|s1uni\d+)(?:_|$))", "N1", "128", "eq",
     "spans tokens (ABSENCE rule): no n<N>/L<NN>/v2/s1uni token -> N1 = 128 (dx0 = L/N1 = 0.5; the L128 "
     "runs keep dx0 = 0.5 with N1 = 256)"),
    (r"^(?!bbh_)(?!stage1_)(?!.*(?:^|_)sg\d+(?:_|$))", "sigma", "0.1", "approx",
     "spans tokens (ABSENCE rule): no sg<NN> token -> Kreiss-Oliger sigma 0.1. stage1_* excluded: "
     "their template default was sigma 2.0 (runs_registry.tsv Stage-1 lines)"),
    (r"^(?!bbh_)(?!.*(?:^|_)(?:dt0\d+|halfstep)(?:_|$))", "dt_multiplier", "0.02", "approx",
     "spans tokens (ABSENCE rule): no dt0<NN>/halfstep token -> dt_multiplier 0.02 (dt = 0.02 dx)"),
    (r"^(?!bbh_)(?!.*(?:^|_)a\d\d?(?:_|$))", "wormhole_throat_radius_A", "2.0", "approx",
     "spans tokens (ABSENCE rule): no a<N> token -> throat scale a = 2"),
    (r"^(?!bbh_)(?!.*(?:^|_)m\d\d+(?:_|$))", "wormhole_drainhole_mass_A", "1.0", "approx",
     "spans tokens (ABSENCE rule): no m<NN> token -> drainhole ADM mass m = 1 (the code unit M)"),
    (r"^(?!bbh_)(?!bridge_)(?!.*(?:^|_)lapse\d(?:_|$))", "wormhole_initial_lapse_type", "5", "eq",
     "spans tokens (ABSENCE rule): no lapse<N> token -> initial lapse type 5 (exact static e^u). "
     "bridge_* excluded: the GRTresna data carry lapse type 1 (sqrt(chi))"),
    (r"^(?!bbh_)(?!.*(?:^|_)eta\d+(?:_|$))", "eta", "1.0", "approx",
     "spans tokens (ABSENCE rule): no eta<N> token -> eta 1.0"),
    (r"^(?!bbh_)(?!.*(?:^|_)(?:lp\d+|lc\d+)(?:_|$))", "lapse_power", "1.0", "approx",
     "spans tokens (ABSENCE rule): no lp/lc token -> 1+log slicing, lapse_power 1.0 ..."),
    (r"^(?!bbh_)(?!.*(?:^|_)(?:lp\d+|lc\d+)(?:_|$))", "lapse_coeff", "2.0", "approx",
     "spans tokens (ABSENCE rule): ... and lapse_coeff 2.0"),
    (r"^(?!.*(?:^|_)p\d+(?:_|$)).*(?:^|_)orbit(?:_|$)", "derived:p_A", "0.12", "approx",
     "spans tokens (ABSENCE rule): an orbit name without a p<NNN> token carries the production push "
     "0.12 (run-tree README: '_orbit: momentum +-0.12 in y', '_pNNN: momentum NNN instead of 0.12')"),
    (r"^(?!.*(?:^|_)(?:flip|twin|place)(?:_|$))(?=.*(?:^|_)(?:ctrl|orbit|merge)(?:_|$))",
     "wormhole_phi_sign_B", "1.0", "eq",
     "spans tokens (ABSENCE rule): a two-throat name with no flip/twin/place token is a LIKE-charge pair "
     "(sigma = +1, the default)"),
    # ---- labels with nothing to test -----------------------------------------
    (r"rr", "(none)", "-", "-",
     "rr: rerun of the same params with checkpoints copied out by hand ('insured'); params identical "
     "to the original apart from paths"),
    (r"ladder", "(none)", "-", "-",
     "ladder: the p012 refinement ladder, every rung restarted from Chk05000 (see L<N>, r05000)"),
    (r"control", "(none)", "-", "-",
     "control: part of bbh_control (see bbh)"),
    (r"HOOKFAIL|OOMFAIL", "(none)", "-", "-",
     "close-out label appended by hand to a failed launch (HOOKFAIL: a params key read without its "
     "evolution. prefix, report silently disarmed; OOMFAIL: out of GPU memory); gpu_hours.py drops HOOKFAIL"),
    (r"20\d\d-\d\d-\d\d", "(none)", "-", "-",
     "date of the failed launch, always after HOOKFAIL/OOMFAIL"),
    (r"(?:^|_)[^_]*\.__keep$", "(none)", "-", "-",
     "spans tokens (suffix): X.__keep = byte-identical pack copy of X left by pack_results.sh; skipped "
     "when X is beside it, so 0 here (10 directories with --include-copies)"),
]

# --------------------------------------------------------------------------
# params parsing, defaults, aliases
# --------------------------------------------------------------------------
# Code defaults for keys a params file may omit (SimulationParameters.hpp,
# SimulationParametersBase.hpp, AMReXParameters.hpp; AMReX Amr for amr.*).
DEFAULTS = {
    "wormhole_phi_sign_B": 1.0,
    "wormhole_helfer_correction": 0,
    "wormhole_helfer_width": 0.0,
    "wormhole_helfer_power": 2.0,
    "core_matter_damping": 0,
    "core_freeze_fill": 0,
    "core_fill_radius_full": 0.0,
    "core_fill_radius_start": 0.0,
    "core_fill_from_time": 0.0,
    "core_damping_radius_start": 0.0,
    "core_damping_radius_full": 0.0,
    "core_damping_radius_from_time": 0.0,
    "core_radial_profile": 0,
    "wormhole_seed_amplitude_A": 0.0,
    "wormhole_seed_l2_amplitude_A": 0.0,
    "wormhole_seed_width_A": 0.0,
    "wormhole_throat_radius_A": 1.0,
    "wormhole_drainhole_mass_A": 0.0,
    "wormhole_bare_mass_A": 0.0,
    "wormhole_initial_lapse_type": 0,
    "wormhole_id_type": 0,
    "wormhole_subtract_phi_asymptote": 1,
    "wormhole_support_strength": 1.0,
    "phantom_mass": 0.0,
    "recipe_initial_data_file": "",
    "tagging_type": 0,
    "nan_autopsy": 0,
    "chi_rhs_floor": 0.0,
    "min_chi": 1e-4,
    "activate_extraction": 0,
    "write_extraction": 0,
    "max_steps": 1000000,
    "checkpoint_interval": 1,
    "amr.checkpoint_files_output": 1,
    "dt_multiplier": 0.25,
    "max_level": 0,
    "stop_time": 1.0,
    "L": 1.0,
    "eta": 1.0,
    "lapse_power": 1.0,
    "lapse_coeff": 2.0,
    "sigma": 0.1,
}
# BinaryBH-format params (the vacuum controls) spell the same things differently.
ALIASES = {
    "max_level": ["amr.max_level"],
    "stop_time": ["evolution.stop_time"],
    "L": ["geometry.prob_extent[0]"],
    "N1": ["amr.n_cell[0]"],
    "dt_multiplier": ["evolution.dt_multiplier"],
    "sigma": ["evolution.sigma"],
}


def parse_params(path: pathlib.Path) -> dict[str, str]:
    """AMReX ParmParse-style: '#' comments, 'key = value', '\\' continuation,
    last definition wins.  Lines whose key contains blanks are not keys."""
    out: dict[str, str] = {}
    pending = ""
    for raw in path.read_text(errors="replace").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if line.endswith("\\"):
            pending += line[:-1] + " "
            continue
        line = pending + line
        pending = ""
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        if not k or re.search(r"\s", k):
            continue
        out[k] = v.strip()
    return out


def _num(s):
    s = str(s).strip().strip('"')
    try:
        return float(s)
    except ValueError:
        return None


def _vec(s):
    if s is None:
        return None
    vals = [_num(x) for x in str(s).split()]
    return None if any(v is None for v in vals) else vals


class Run:
    def __init__(self, group: str, path: pathlib.Path):
        self.group = group
        self.path = path
        self.dirname = path.name
        self.name = re.sub(r"\.__keep$", "", path.name)
        pf = path / "evolution_params.txt"
        self.P = parse_params(pf) if pf.exists() else None
        self._h0 = "unset"
        self.is_template = False

    # -- raw / defaulted lookups ------------------------------------------
    def raw(self, key):
        if self.P is None:
            return None
        m = re.fullmatch(r"(.+)\[(\d+)\]", key)
        if m:
            v = _vec(self.P.get(m.group(1)))
            return None if v is None or int(m.group(2)) >= len(v) else v[int(m.group(2))]
        return self.P.get(key)

    def get(self, key):
        """Value of a key with aliases and code defaults (None if unknowable)."""
        if self.P is None:
            return None
        v = self.raw(key)
        if v is None:
            for alt in ALIASES.get(key, []):
                v = self.raw(alt)
                if v is not None:
                    break
        if v is None:
            if key == "N1":
                return None
            if key == "tagging_L":
                return self.get("L")
            if key == "wormhole_throat_radius_B":
                return self.get("wormhole_throat_radius_A")
            if key == "wormhole_drainhole_mass_B":
                return self.get("wormhole_drainhole_mass_A")
            if key == "wormhole_seed_amplitude_B":
                return self.get("wormhole_seed_amplitude_A")
            if key == "wormhole_seed_l2_amplitude_B":
                return self.get("wormhole_seed_l2_amplitude_A")
            v = DEFAULTS.get(key)
        if isinstance(v, str):
            n = _num(v)
            return n if n is not None else v.strip().strip('"')
        return v

    def vec(self, key, default):
        v = _vec(self.raw(key)) if self.P is not None else None
        return default if v is None else v

    @property
    def binarybh(self):
        return self.P is not None and "bh1.mass" in self.P

    # -- streams ------------------------------------------------------------
    @classmethod
    def from_template(cls, tpl: pathlib.Path):
        r = cls.__new__(cls)
        r.group, r.path = "templates_scan", tpl.parent / ("__template__" + tpl.stem)
        r.dirname = tpl.stem
        r.name = re.sub(r"^params_", "", tpl.stem)
        r.P = parse_params(tpl)
        r._h0 = None
        r.is_template = True
        return r

    def first_row(self):
        for stem in ("constraint_norms", "collapse_diagnostics",
                     "binary_throat_diagnostics", "throat_track"):
            p = self.path / f"{stem}.dat"
            if not p.exists():
                continue
            with p.open(errors="replace") as fh:
                for line in fh:
                    if line.startswith("#") or not line.strip():
                        continue
                    parts = line.split()
                    t = _num(parts[0])
                    if t is not None:
                        return t, parts
        return None, None

    def h0(self):
        """t = 0 L2_Ham exactly as printed, or None."""
        if self._h0 != "unset":
            return self._h0
        self._h0 = None
        p = self.path / "constraint_norms.dat"
        if p.exists():
            with p.open(errors="replace") as fh:
                for line in fh:
                    if line.startswith("#") or not line.strip():
                        continue
                    parts = line.split()
                    if _num(parts[0]) == 0.0 and len(parts) > 1:
                        self._h0 = parts[1]
                    break
        return self._h0

    def banner_restart(self):
        b = self.path / "launch_banner.txt"
        if b.exists():
            m = re.search(r"\[whm\] restart\s*:\s*(\S+)", b.read_text(errors="replace"))
            if m:
                return m.group(1)
        return None

    def restart_path(self):
        v = self.raw("amr.restart") if self.P is not None else None
        if v:
            return v.strip().strip('"')
        return self.banner_restart()


# --------------------------------------------------------------------------
# derived quantities
# --------------------------------------------------------------------------
ID_KEYS = [
    "L", "N1", "center", "wormhole_id_type", "wormhole_initial_lapse_type",
    "wormhole_throat_radius_A", "wormhole_throat_radius_B",
    "wormhole_drainhole_mass_A", "wormhole_drainhole_mass_B",
    "wormhole_bare_mass_A", "wormhole_phi_sign_B", "wormhole_subtract_phi_asymptote",
    "wormhole_support_strength", "phantom_mass", "wormhole_helfer_correction",
    "wormhole_helfer_width", "recipe_initial_data_file", "min_chi", "wormhole_seed_width_A",
    "wormhole_seed_amplitude_A", "wormhole_seed_l2_amplitude_A",
]


def id_signature(run: Run, drop: str, eff_l2=None):
    """Initial-data keys (code defaults applied) minus `drop`.  eff_l2, when
    given, replaces the declared quadrupole by the effective one (so an eps
    test is never made against a twin whose own l2 seed was ignored)."""
    sig = []
    for k in ID_KEYS:
        if k == drop:
            continue
        v = run.get(k)
        if k == "wormhole_seed_l2_amplitude_A" and eff_l2 is not None:
            v = eff_l2(run)
        sig.append((k, v))
    ca = run.vec("wormhole_centerA", [0.0, 0.0, 5.0])
    cb = run.vec("wormhole_centerB", [-x for x in ca])
    pa = run.vec("wormhole_momentumA", [0.0, 0.0, 0.0])
    pb = run.vec("wormhole_momentumB", [-x for x in pa])
    sig += [("cA", tuple(ca)), ("cB", tuple(cb)), ("pA", tuple(pa)), ("pB", tuple(pb))]
    return tuple(sig)


class _Untestable:
    def __repr__(self):
        return "UNTESTABLE"


UNTESTABLE = _Untestable()


class Deriver:
    def __init__(self, runs: list[Run]):
        self.runs = runs
        self.by_name = {r.name: r for r in runs}
        self.notes: dict[tuple[str, str], str] = {}
        self._eff: dict = {}

    def effective_seed(self, run: Run, key: str, depth: int = 0):
        """(value, how) for a seed key after the t = 0 constraint test."""
        ck = (run.dirname, str(run.path), key)
        if ck not in self._eff:
            self._eff[ck] = self._effective_seed(run, key, depth)
        return self._eff[ck]

    def _effective_seed(self, run: Run, key: str, depth: int = 0):
        declared = run.get(key)
        if declared is None:
            return None, "no params"
        rp = run.restart_path()
        if rp:
            parent = pathlib.PurePosixPath(rp).parent.name
            pr = self.by_name.get(parent)
            if pr is None or depth > 5:
                return declared, f"restart leg; parent '{parent}' not in the pack -> declared value, unverified"
            v, how = self.effective_seed(pr, key, depth + 1)
            return v, f"restart leg of {parent}: {how}"
        if not declared:
            return declared, "declared 0"
        h0 = run.h0()
        if h0 is None:
            return declared, "no t = 0 constraint row -> declared value, unverified"
        eff = None
        if key == "wormhole_seed_amplitude_A":
            eff = lambda r: self.effective_seed(r, "wormhole_seed_l2_amplitude_A")[0]  # noqa: E731
        mine = id_signature(run, key, eff)
        refs = [r for r in self.runs if r is not run and r.P is not None and not r.binarybh
                and not r.restart_path() and r.get(key) == 0.0 and r.h0() is not None
                and id_signature(r, key, eff) == mine]
        if not refs:
            return declared, "no seed-free twin in the pack -> declared value, unverified"
        mytok = set(run.name.split("_"))
        refs.sort(key=lambda r: (-len(mytok & set(r.name.split("_"))),
                                 r.get("max_level") != run.get("max_level"), r.name))
        same = [r.name for r in refs if r.h0() == h0]
        if same:
            return 0.0, (f"t = 0 L2_Ham {h0} identical to seed-free {same[0]} -> key IGNORED "
                         f"by the binary, effective 0")
        return declared, f"t = 0 L2_Ham {h0} differs from seed-free {refs[0].name} ({refs[0].h0()}) -> seed entered"

    def value(self, run: Run, param: str):
        """(value, explanation); value is UNTESTABLE when it cannot be computed."""
        if param.startswith("derived:"):
            name = param.split(":", 1)[1]
            if name == "restart_step":
                rp = run.restart_path()
                if rp is None:
                    if run.P is None:
                        return UNTESTABLE, "no params, no banner"
                    return None, "no amr.restart"
                m = re.search(r"Chk(\d+)", rp)
                return (int(m.group(1)) if m else None), f"restart = ...{rp[-40:]}"
            if name == "is_restart":
                if run.P is None and run.banner_restart() is None:
                    return UNTESTABLE, "no params"
                return run.restart_path() is not None, ""
            if run.P is None:
                return UNTESTABLE, "no params"
            if name == "separation":
                if run.binarybh:
                    a, b = run.vec("bh1.offset", None), run.vec("bh2.offset", None)
                else:
                    a = run.vec("wormhole_centerA", [0.0, 0.0, 5.0])
                    b = run.vec("wormhole_centerB", [-x for x in a])
                return math.dist(a, b), f"centres {a} {b}"
            if name in ("p_A", "p_A_nonzero"):
                p = run.vec("bh1.momentum", None) if run.binarybh else run.vec("wormhole_momentumA", [0.0, 0.0, 0.0])
                n = math.sqrt(sum(x * x for x in p))
                return (n if name == "p_A" else n > 0.0), f"momentumA {p}"
            if name == "throat_B_present":
                if run.binarybh:
                    return UNTESTABLE, "BinaryBH params"
                return run.get("wormhole_throat_radius_B") > 0.0, f"b0_B = {run.get('wormhole_throat_radius_B')}"
            if name == "writes_checkpoints":
                ci, co = run.get("checkpoint_interval"), run.get("amr.checkpoint_files_output")
                return (ci is not None and ci > 0 and co != 0), f"checkpoint_interval {ci}, amr.checkpoint_files_output {co}"
            if name == "any_seed":
                e, q = run.get("wormhole_seed_amplitude_A"), run.get("wormhole_seed_l2_amplitude_A")
                return (e != 0.0 or q != 0.0), f"eps {e}, eps2 {q}"
            if name == "mu":
                a, m = run.get("wormhole_throat_radius_A"), run.get("wormhole_drainhole_mass_A")
                return (m / a if a else UNTESTABLE), f"m {m}, a {a}"
            if name == "is_binarybh_params":
                return run.binarybh, ""
            if name == "has_recipe_initial_data":
                return bool(run.get("recipe_initial_data_file")), ""
            if name == "damping_radius_window":
                s, f = run.get("core_damping_radius_start"), run.get("core_damping_radius_full")
                return (s > 0.0 and f > 0.0), f"radius_start {s}, radius_full {f}"
            if run.is_template and name in ("t_restart_from_stream", "seed_l2_effective",
                                            "seed_eps_effective"):
                return UNTESTABLE, "template: no streams"
            if name == "t_restart_from_stream":
                t, _ = run.first_row()
                if t is None:
                    return UNTESTABLE, "no evolution stream packed"
                dtm, L, N = run.get("dt_multiplier"), run.get("L"), run.get("N1")
                if None in (dtm, L, N):
                    return UNTESTABLE, "dt unknown"
                return t - dtm * L / N, f"first row t = {t}, leg dt = {dtm * L / N:g}"
            if name in ("seed_l2_effective", "seed_eps_effective"):
                key = "wormhole_seed_l2_amplitude_A" if name == "seed_l2_effective" else "wormhole_seed_amplitude_A"
                v, how = self.effective_seed(run, key)
                return (UNTESTABLE if v is None else v), how
            raise KeyError(param)
        if run.P is None:
            return UNTESTABLE, "no params"
        v = run.get(param)
        if v is None:
            return UNTESTABLE, f"{param} not set and no default"
        return v, ""


def compare(mode: str, actual, expected, run: Run) -> bool:
    if mode == "file_exists":
        return (run.path / expected).exists()
    if mode == "eq":
        a, e = _num(actual) if not isinstance(actual, bool) else actual, expected
        if isinstance(e, bool) or e is None or isinstance(actual, bool) or actual is None:
            return actual == e
        if a is not None and _num(e) is not None:
            return a == _num(e)
        return str(actual) == str(e)
    if mode == "approx":
        return actual is not None and math.isclose(float(actual), float(expected), rel_tol=1e-9, abs_tol=0.0)
    if mode == "abs_approx":
        return actual is not None and abs(float(actual) - float(expected)) <= 1e-6
    raise ValueError(mode)


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------
def load_runs(pack_root: pathlib.Path, include_copies: bool) -> tuple[list[Run], list[str]]:
    sys.path.insert(0, str(HERE))
    import pack_paths  # noqa: E402

    def iter_runs(root):
        """pack_paths.iter_runs, with its X.__keep filter lifted so that
        --include-copies can count the copies; they are skipped below otherwise."""
        orig = pack_paths._is_run
        pack_paths._is_run = lambda d: any((d / f).exists() for f in (
            "evolution_params.txt", "run_tail.log", "LOST.md", "launch_banner.txt"))
        try:
            yield from pack_paths.iter_runs(root)
        finally:
            pack_paths._is_run = orig

    runs, skipped, seen = [], [], set()
    for group, d in iter_runs(pack_root):
        if not include_copies:
            if d.name.endswith(".__keep") and (d.parent / d.name[: -len(".__keep")]).is_dir():
                skipped.append(f"{group}/{d.name} (pack copy of {d.name[:-7]})")
                continue
            if d.name in seen:
                skipped.append(f"{group or '<top>'}/{d.name} (second directory of the same name)")
                continue
        seen.add(d.name)
        runs.append(Run(group, d))
    return runs, skipped


def write_tsv(path: pathlib.Path, rows):
    """Plain TSV: one header line, fields joined by TAB, no quoting/escaping."""
    lines = ["\t".join(["token_regex", "param", "expected", "compare", "note", "holds", "fails"])]
    for r in rows:
        for f in r:
            if "\t" in f or "\n" in f:
                raise ValueError(f"field with TAB/newline: {f!r}")
        lines.append("\t".join(r))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_tsv(path: pathlib.Path):
    rows = path.read_text(encoding="utf-8").splitlines()
    head = rows[0].split("\t")
    return [dict(zip(head, line.split("\t"))) for line in rows[1:] if line.strip()]


def matches(rule_regex: str, note: str, name: str):
    if "spans tokens" in note:
        m = re.search(rule_regex, name)
        return [m] if m else []
    out = []
    for tok in name.split("_"):
        m = re.fullmatch(rule_regex, tok)
        if m:
            out.append(m)
    return out


def evaluate(rules, runs, der, label="packed run"):
    """Apply every rule to every run.  Returns (tsv_rows, report_lines)."""
    out_rows, report = [], []
    for rule in rules:
        rx, param, exp_src, mode, note = (rule["token_regex"], rule["param"], rule["expected"],
                                          rule["compare"], rule["note"])
        holds = fails = untest = carrying = 0
        fail_lines, untest_names, unverified, fail_names = [], [], [], []
        for run in runs:
            ms = matches(rx, note, run.dirname if "__keep" in rx else run.name)
            if not ms:
                continue
            carrying += 1
            if param == "(none)":
                continue
            m = ms[0]
            g = {f"g{i}": m.group(i) for i in range(1, (m.re.groups or 0) + 1)}
            expected = eval(exp_src, {"__builtins__": {"float": float, "int": int}}, g)  # noqa: S307
            if param in ("(consumer)", "(stream)"):
                if run.is_template or run.P is None and not run.path.is_dir():
                    untest += 1
                    untest_names.append(f"{run.name} (no streams)")
                    continue
                ok = compare("file_exists", None, expected, run)
                actual, why = ("present" if ok else "absent"), ""
            else:
                actual, why = der.value(run, param)
                if actual is UNTESTABLE:
                    untest += 1
                    untest_names.append(f"{run.name} ({why})")
                    continue
                ok = compare(mode, actual, expected, run)
            if ok:
                holds += 1
                if "unverified" in why:
                    unverified.append(f"{run.name} ({why.split(';')[0]})")
            else:
                fails += 1
                fail_names.append(f"{run.name} (got {actual!r})")
                tok = m.group(0).strip("_") or "(absence)"
                fail_lines.append(f"  FAIL {run.group}/{run.name}: token '{tok}' "
                                  f"expects {param} = {expected!r}, got {actual!r}"
                                  + (f"  [{why}]" if why else ""))
        if param == "(none)":
            out_rows.append([rx, param, exp_src, mode,
                             note + f" -- carried by {carrying} {label}(s)", "-", "-"])
        else:
            n2 = note
            if fail_names:
                n2 += f" -- FAILS in {len(fail_names)}: " + "; ".join(fail_names)
            if untest:
                n2 += f" -- untestable in {untest}: " + "; ".join(untest_names)
            if unverified:
                n2 += (f" -- {len(unverified)} of the holds keep the declared value UNVERIFIED: "
                       + "; ".join(unverified))
            out_rows.append([rx, param, exp_src, mode, n2, str(holds), str(fails)])
        report.append(f"\n[{rx}] -> {param} {mode} {exp_src}: holds {holds}, fails {fails}, "
                      f"untestable {untest}, carried by {carrying}")
        report.extend(fail_lines)
        for u in untest_names:
            report.append(f"  untestable: {u}")

    # tokens no rule covers
    report.append("\n# name tokens not covered by any rule")
    covered, token_seen = set(), {}
    for rule in rules:
        for run in runs:
            if "spans tokens" in rule["note"]:
                mm = re.search(rule["token_regex"], run.name)
                if mm:
                    covered.update(mm.group(0).strip("_").split("_"))
            else:
                covered.update(t for t in run.name.split("_") if re.fullmatch(rule["token_regex"], t))
    for run in runs:
        for tok in run.name.split("_"):
            if tok not in covered:
                token_seen.setdefault(tok, []).append(run.name)
    for tok, names in sorted(token_seen.items()):
        report.append(f"  {tok}  ({len(names)}: {', '.join(names[:3])}{' ...' if len(names) > 3 else ''})")
    return out_rows, report


def findings(pack_root: pathlib.Path) -> dict[str, list[tuple[str, str]]]:
    """run name -> [(kind, message)], kind "mismatch" (a token contradicts what
    ran) or "silent" (an absence rule: a knob off its production value that the
    name does not mention, e.g. a restart leg raised to level 5)."""
    rules = read_tsv(pack_root / "name_grammar.tsv") if (pack_root / "name_grammar.tsv").exists() \
        else [dict(zip(["token_regex", "param", "expected", "compare", "note"], r)) for r in RULES]
    runs, _ = load_runs(pack_root, include_copies=False)
    der = Deriver(runs)
    out: dict[str, list[tuple[str, str]]] = {}
    for rule in rules:
        rx, param, exp_src, mode, note = (rule["token_regex"], rule["param"], rule["expected"],
                                          rule["compare"], rule["note"])
        if param == "(none)":
            continue
        for run in runs:
            ms = matches(rx, note, run.dirname if "__keep" in rx else run.name)
            if not ms:
                continue
            m = ms[0]
            g = {f"g{i}": m.group(i) for i in range(1, (m.re.groups or 0) + 1)}
            expected = eval(exp_src, {"__builtins__": {"float": float, "int": int}}, g)  # noqa: S307
            if param in ("(consumer)", "(stream)"):
                ok, actual = compare("file_exists", None, expected, run), None
                actual = "present" if ok else "absent"
            else:
                actual, _why = der.value(run, param)
                if actual is UNTESTABLE:
                    continue
                ok = compare(mode, actual, expected, run)
            if not ok:
                absence = "ABSENCE rule" in note
                tok = "(no token)" if absence else m.group(0).strip("_")
                kind = "silent" if absence else "mismatch"
                out.setdefault(run.name, []).append(
                    (kind, f"{tok}: {param.replace('derived:', '')} = {actual!r}, "
                           f"{'production value' if absence else 'name says'} {expected!r}"))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pack_root", nargs="?", type=pathlib.Path, default=HERE.parent,
                    help="the pack (default: results/merger, this file's parent's parent)")
    ap.add_argument("--include-copies", action="store_true",
                    help="also count X.__keep pack copies and same-name duplicates")
    ap.add_argument("--report", type=pathlib.Path, help="write the per-run failure account here")
    ap.add_argument("--templates", action="store_true",
                    help="also check runs/wormhole_merger/templates_scan/params_*.txt (untracked); "
                         "the TSV counts stay packed-runs-only")
    args = ap.parse_args()
    pack = args.pack_root.resolve()
    if not (pack / "campaign").is_dir():
        raise SystemExit(f"not a pack (no campaign/): {pack}")
    args.tsv = pack / "name_grammar.tsv"

    # 1. the grammar as data; the evaluation below reads it back from the TSV
    write_tsv(args.tsv, [list(r) + ["", ""] for r in RULES])
    rules = read_tsv(args.tsv)

    # 2. packed runs
    runs, skipped = load_runs(pack, args.include_copies)
    der = Deriver(runs)
    out_rows, body = evaluate(rules, runs, der)
    report = [f"# check_grammar.py over {len(runs)} packed runs "
              f"({sum(r.P is not None for r in runs)} with evolution_params.txt)"]
    report += [f"# skipped: {s}" for s in skipped]
    report += body
    report.append("\n# effective-seed audit (t = 0 L2_Ham against seed-free twins)")
    for run in runs:
        if run.P is None or run.binarybh:
            continue
        for key in ("wormhole_seed_amplitude_A", "wormhole_seed_l2_amplitude_A"):
            if run.get(key):
                v, how = der.effective_seed(run, key)
                report.append(f"  {run.name}: {key} declared {run.get(key)} -> effective {v}  [{how}]")
    write_tsv(args.tsv, out_rows)
    if args.report:
        args.report.write_text("\n".join(report) + "\n", encoding="utf-8")
    nf = sum(int(r[6]) for r in out_rows if r[6] not in ("-", ""))
    print(f"[name-check] {len(out_rows)} rules, {len(runs)} runs, {nf} failures -> {args.tsv.name}")

    # 3. optional: the untracked templates (names are template stems, not run names)
    if args.templates:
        tdir = pack.parents[1] / "runs" / "wormhole_merger" / "templates_scan"
        tpls = [Run.from_template(t) for t in sorted(tdir.glob("params_*.txt"))]
        t_rows, t_body = evaluate(rules, tpls, Deriver(tpls), label="template")
        nt = sum(int(r[6]) for r in t_rows if r[6] not in ("-", ""))
        out = (args.report.parent if args.report else pathlib.Path(".")) / "name_check_templates.txt"
        out.write_text(f"# templates_scan: {len(tpls)} templates, {nt} failures\n"
                       + "\n".join(t_body) + "\n", encoding="utf-8")
        print(f"templates: {len(tpls)} checked, {nt} failures -> {out.name}")


if __name__ == "__main__":
    main()
