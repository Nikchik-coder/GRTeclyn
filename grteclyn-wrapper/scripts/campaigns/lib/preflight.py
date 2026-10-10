#!/usr/bin/env python3
"""Pre-launch check engine: does the binary read every key, and does the seed take?

ONE ENGINE FOR EVERY CAMPAIGN (2026-10-10).  Adapted from the merger campaign's
preflight (wormhole_merger/preflight.py, which stays frozen with that closed
campaign): every campaign-specific fact is injected from a JSON config instead
of being edited into a fork, so future campaigns launch through this one file.

    preflight.py --campaign-config CFG.json --exe BIN --params params.txt \
                 --gpu 1 --workdir DIR \
                 [--mode full|static|off] [--restart] [--json OUT] [--argv0 NAME] \
                 [--consumer-argv "FLAGS"] [--frames-cmd "CMD"] [--frames-out DIR]

THE CAMPAIGN CONFIG (--campaign-config, or $CAMPAIGN_PREFLIGHT_CONFIG):
    name                    campaign slug, used in messages
    env_prefix              prefix of the launcher's env vars (e.g. "SWH"); the
                            engine reads <prefix>_X first, then CAMPAIGN_X.
                            Optional; default "CAMPAIGN"
    run_root                run-tree name for the path checks: every consumer
                            flag matching <run_root>/([^/]+)/ must name this run
    seed_key_regex          params keys that are seed amplitudes (the seed-effect
                            twin probe zeroes exactly these)
    mirror_keys             params keys whose components must sit on a
                            reflective lower boundary's mirror plane
                            ("extraction_center" is only checked while
                            activate_extraction is on)
    forbid_reflection_axes  axis indices (0 x, 1 y, 2 z) whose reflective
                            boundaries, lower or upper, are refused outright
                            (the campaign's physics has no mirror there)
    required_file_keys      params keys whose value must be an existing file;
                            a missing key or path is refused
    probe_param_caps        {trigger_key: {cap_key: value, ...}}: when the
                            params hold trigger_key = 1/true (and the run is
                            not a restart), the 0-step probes get these
                            overrides -- for features whose full run outlasts
                            the probe budget (the merger capped its constraint
                            solve this way).  Only cap keys the binary contains
                            are applied; the run itself runs in full
    allow_file, frames_file paths to the campaign's preflight_allow.txt and
                            frames_default.txt, relative to the config file

Run by the campaign's run_single.sh once the params are cloned and every
override applied, before the run is registered or started.

WHY.  AMReX's ParmParse ignores a key that nothing reads, so a binary older
than a feature runs the params without it and says nothing (the merger
campaign ran four seeded arms without their seed that way, 2026-09-23).  This
turns that into a refusal at launch, in seconds.

WHAT IT CHECKS
  0. intent (no GPU, instant).  Settings that contradict each other, so the run
     would silently not do what its params say.  Refused:
       - checkpoint_interval > 0 or checkpoint_keep > 0 with
         amr.checkpoint_files_output = 0: AMReX's checkPoint() returns at once
         when output is off, so NO checkpoint is ever written.
       - plot_interval > 0 with amr.plot_files_output = 0 (no plotfiles: no
         frames, no consumer extractions).
     Warned: a run that writes no checkpoints at all cannot be restarted.
     Required files (required_file_keys): each must be set and exist as a file
     (relative paths resolve against the run directory, where the binary runs).
     The plotfile consumer's flags against what the plotfiles carry:
       - refused: --areal-full-metric with h22, h33 or chi missing from
         amr.plot_vars, or without --areal-radius.
       - warned: --areal-radius alone -- r/sqrt(chi), exact at t = 0 and a
         lower bound once the Gamma-driver shift has moved the grid.
       - refused: --neck-horizons without chi K lapse h11 h22 h33 A11 phi in
         amr.plot_vars.
     And the box's symmetry (lo_boundary = 2: a mirror plane on that lower
     face).  A reflective boundary on a forbidden axis (forbid_reflection_axes,
     lower OR upper face) is refused outright; a reflective upper face is
     refused on every axis (the consumer folds onto lower faces only).  On an
     allowed mirror, every mirror_keys vector must sit on the plane, the
     consumer's --reflect must name exactly the params' planes, --horizon-scan
     is refused there (the star scan samples the full sphere) and
     --frames-center must sit on the planes.
     And the FRAMES.  The consumer deletes each plotfile once it has been
     extracted, so a field not rendered live has no movie, ever.  The frame
     list the consumer will get (--consumer-argv / $<prefix>_CONSUMER_ARGV, as
     run_single.sh builds it) must hold every field of the campaign's
     frames_default.txt; refused otherwise, unless $<prefix>_FRAMES_SUBSET
     gives the reason (recorded in the report and the manifest).  Refused too:
     a frame field whose plot variable the params do not write (the frame
     would silently not exist), and frames asked of a run with
     plot_interval <= 0.  This part runs in every mode, --mode off included:
     its only override is the FRAMES_SUBSET reason.
  1. static (no GPU, seconds).  Every key of the params file must appear as a
     string inside the binary: a binary that does not contain a key's name
     cannot read it.  Advisory in full mode (a key can be present but unread
     on this code path); decisive in static mode, less the dead keys that the
     campaign's allow file names (no code reads them, so no binary contains
     them).
  2. unread keys (GPU, one start-up).  The binary starts on a copy of the params
     with max_steps = 0, all output off, amrex.abort_on_unused_inputs = 1 and
     amrex.verbose = 1.  It builds the whole initial hierarchy, writes its t = 0
     diagnostics and at exit AMReX lists every key nothing read.  Any unread
     key refuses the launch, unless the allow file covers it (keys read only
     when a plotfile is written, which the probe skips, and dead keys no code
     reads -- each entry says why).
  3. seed effect (GPU, a second start-up; only when a seed_key_regex key is
     non-zero and the run is not a restart).  The same start-up with every seed
     amplitude set to 0.  If no t = 0 diagnostic differs by more than 1e-10
     (relative), the seed did nothing and the launch is refused.
  4. frames (full mode, when the consumer runs).  The start-up of step 2 also
     writes its t = 0 plotfile, and the consumer itself (--frames-cmd, the
     run's own post.py) renders every frame field from it into --frames-out
     with the run's own frame flags: frame 0, as the run will draw it, before
     anything is launched.  Each field is judged from the slice it drew (the
     slice cache), not by eye: no PNG, no slice, all pixels NaN, or every pixel
     the same value is a FAILED field and refuses the launch -- except a field
     that is constant everywhere in the plotfile (a zero initial shift, K = 0
     on time-symmetric data), which is "flat": nothing to show yet, not a
     rendering failure.  Per field ok / flat / FAILED in the report.  Static
     mode renders nothing (no start-up) and says so.

Exit status: 0 pass, 1 refused, 2 could not run (a failed start-up, a timeout).
A report goes to --json; run_single.sh folds it into run_manifest.json.

Python 3.9+, standard library only.
"""

from __future__ import annotations

import argparse
import array
import ast
import hashlib
import json
import math
import os
import pathlib
import re
import shlex
import shutil
import struct
import subprocess
import sys
import time
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
KEY_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_.]*)\s*=(.*)$")
UNUSED_RE = re.compile(r"\[TOP\]::([A-Za-z_][A-Za-z0-9_.]*)\(nvals")
VERSION_RE = re.compile(r"Using GRTeclyn version \((.*)\)")
REL_TOL = 1e-10

# ------------------------------------------------------- campaign configuration
# Set by apply_campaign_config() before any check runs.  The defaults below are
# deliberately inert (a seed regex that matches nothing, no mirror keys), so an
# unconfigured import (run_manifest.py imports parse_params/static_check/t0_rows
# from here) never checks anything by accident.
CAMPAIGN = "campaign"
ENV_PREFIX = "CAMPAIGN"
ALLOW_FILE: pathlib.Path | None = None
FRAMES_FILE: pathlib.Path | None = None
SEED_KEY_RE = re.compile(r"(?!)")
RUN_PATH_RE = re.compile(r"(?!)")
MIRROR_KEYS: list[str] = []
FORBID_REFLECTION_AXES: list[int] = []
REQUIRED_FILE_KEYS: list[str] = []
PROBE_PARAM_CAPS: dict[str, dict[str, str]] = {}


def apply_campaign_config(path: str | os.PathLike) -> dict:
    """Load --campaign-config and set the campaign facts above."""
    global CAMPAIGN, ENV_PREFIX, ALLOW_FILE, FRAMES_FILE, SEED_KEY_RE, RUN_PATH_RE
    global MIRROR_KEYS, FORBID_REFLECTION_AXES, REQUIRED_FILE_KEYS, PROBE_PARAM_CAPS
    cfg_path = pathlib.Path(path).resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    CAMPAIGN = cfg["name"]
    ENV_PREFIX = cfg.get("env_prefix") or "CAMPAIGN"
    SEED_KEY_RE = re.compile(cfg["seed_key_regex"])
    RUN_PATH_RE = re.compile(re.escape(cfg["run_root"]) + r"/([^/]+)/")
    MIRROR_KEYS = [str(k) for k in cfg.get("mirror_keys", [])]
    FORBID_REFLECTION_AXES = [int(i) for i in cfg.get("forbid_reflection_axes", [])]
    REQUIRED_FILE_KEYS = [str(k) for k in cfg.get("required_file_keys", [])]
    PROBE_PARAM_CAPS = {str(t): {str(k): str(v) for k, v in caps.items()}
                        for t, caps in cfg.get("probe_param_caps", {}).items()}
    ALLOW_FILE = (cfg_path.parent / cfg["allow_file"]).resolve()
    FRAMES_FILE = (cfg_path.parent / cfg["frames_file"]).resolve()
    return cfg


def env_get(name: str, default: str | None = None) -> str | None:
    """The launcher's env plumbing: <prefix>_<name> first, then CAMPAIGN_<name>.
    CLI flags stay primary; these are only their defaults."""
    for var in (f"{ENV_PREFIX}_{name}", f"CAMPAIGN_{name}"):
        if var in os.environ:
            return os.environ[var]
    return default


# ---------------------------------------------------------------- params file
def strip_comment(line: str) -> str:
    """Drop a # comment that is not inside double quotes."""
    out, quoted = [], False
    for ch in line:
        if ch == '"':
            quoted = not quoted
        if ch == "#" and not quoted:
            break
        out.append(ch)
    return "".join(out)


def parse_params(text: str) -> dict[str, str]:
    """key -> raw value text (last definition wins, as in ParmParse queries)."""
    params: dict[str, str] = {}
    for line in text.splitlines():
        m = KEY_RE.match(strip_comment(line))
        if m:
            params[m.group(1)] = m.group(2).strip()
    return params


def rewrite_params(text: str, overrides: dict[str, str]) -> str:
    """Set each override key exactly once: replace its definition line(s) in
    place, append the ones the file does not define."""
    seen: set[str] = set()
    out = []
    for line in text.splitlines():
        m = KEY_RE.match(strip_comment(line))
        if m and m.group(1) in overrides:
            key = m.group(1)
            if key in seen:
                continue                      # drop duplicate definitions
            seen.add(key)
            out.append(f"{key} = {overrides[key]}")
        else:
            out.append(line)
    missing = [k for k in overrides if k not in seen]
    if missing:
        out.append("")
        out.append("# ---- set by preflight.py ----")
        out.extend(f"{k} = {overrides[k]}" for k in missing)
    return "\n".join(out) + "\n"


def as_float(raw: str) -> float | None:
    try:
        return float(raw.split()[0].strip('"'))
    except (ValueError, IndexError):
        return None


# ---------------------------------------------------------------- 0. intent
def intent_check(params: dict[str, str]) -> tuple[list[str], list[str]]:
    """(errors, warnings) for settings that contradict each other.  Defaults as
    in the code: GRTeclyn checkpoint_interval 1, plot_interval 0; AMReX
    checkpoint_files_output and plot_files_output 1."""
    def num(key: str, default: float) -> float:
        v = as_float(params[key]) if key in params else None
        return default if v is None else v

    errors, warnings = [], []
    ci, keep = num("checkpoint_interval", 1), num("checkpoint_keep", 0)
    cout = num("amr.checkpoint_files_output", 1)
    asked = [f"{k} = {params[k].split()[0]}" for k, v in (("checkpoint_interval", ci), ("checkpoint_keep", keep))
             if k in params and v > 0]
    if cout == 0 and asked:
        errors.append(f"checkpoints requested ({', '.join(asked)}) but amr.checkpoint_files_output = 0: "
                      "AMReX writes NO checkpoint when output is off.  Set amr.checkpoint_files_output = 1, "
                      "or checkpoint_interval = -1 and drop checkpoint_keep to say 'no checkpoints'")
    pi, pout = num("plot_interval", 0), num("amr.plot_files_output", 1)
    if pout == 0 and pi > 0:
        errors.append(f"plot_interval = {params['plot_interval'].split()[0]} but amr.plot_files_output = 0: "
                      "no plotfile will be written (no frames, no consumer extractions)")
    if cout == 0 or ci <= 0:
        warnings.append("this run writes no checkpoints: if it dies, it cannot be restarted")
    return errors, warnings


def required_files_check(params: dict[str, str]) -> tuple[list[str], dict]:
    """(errors, summary) for the campaign's required input files
    (required_file_keys): each key must be set and its value must exist as a
    file on THIS node.  A relative path resolves against the current
    directory, which is the run directory when run_single.sh calls this -- the
    same directory the binary runs from."""
    errors: list[str] = []
    files: dict[str, str | None] = {}
    for key in REQUIRED_FILE_KEYS:
        raw = params.get(key)
        if raw is None:
            files[key] = None
            errors.append(f"{key} is missing: every {CAMPAIGN} template must set it (a required input file)")
            continue
        path = raw.strip().strip('"')
        files[key] = path or None
        if not path:
            errors.append(f"{key} is empty: name the file")
        elif not pathlib.Path(path).is_file():
            errors.append(f"{key} = {path!r} does not exist as a file (checked from {os.getcwd()}): "
                          "the run would abort or start on wrong data")
    return errors, {"files": files}


AXES = "xyz"
REFLECTIVE_BC = 2  # GRTeclyn's legacy boundary code, AMReXParameters.hpp


def _numbers(params: dict[str, str], key: str) -> list[float] | None:
    """The whitespace-separated numbers of a key, or None if absent/unparsable."""
    if key not in params:
        return None
    try:
        return [float(v) for v in params[key].split()]
    except ValueError:
        return None


def _flag_values(toks: list[str], flag: str) -> list[str]:
    """The tokens after ``flag`` up to the next option ([] if absent)."""
    if flag not in toks:
        return []
    out = []
    for t in toks[toks.index(flag) + 1:]:
        if t.startswith("--"):
            break
        out.append(t)
    return out


def symmetry_check(params: dict[str, str]) -> tuple[list[str], list[str], dict]:
    """(errors, warnings, summary) for a symmetry-reduced box: lo_boundary = 2
    makes the lower face x_i = 0 a mirror plane and the run holds its positive
    side.  An axis in forbid_reflection_axes is refused outright, lower or
    upper face: the campaign's data is not mirror-symmetric across it.  On an
    allowed mirror, everything that defines the data (mirror_keys) must sit on
    the plane, or the mirror image is not the configuration the params
    describe."""
    errors, warnings = [], []
    lo = _numbers(params, "lo_boundary") or [0, 0, 0]
    hi = _numbers(params, "hi_boundary") or [0, 0, 0]
    per = _numbers(params, "isPeriodic") or [0, 0, 0]

    def refl(vec: list[float], i: int) -> bool:
        return (i < len(vec) and int(vec[i]) == REFLECTIVE_BC
                and not (i < len(per) and per[i]))

    forbidden = sorted({AXES[i] for i in FORBID_REFLECTION_AXES
                        for vec in (lo, hi) if refl(vec, i)})
    if forbidden:
        errors.append(f"reflective {' and '.join(forbidden)} boundaries: the {CAMPAIGN} campaign's data "
                      f"is not mirror-symmetric across {' and '.join(forbidden)} "
                      "(forbid_reflection_axes in its preflight_campaign.json), so the run cannot be "
                      "reduced across those planes")
    if any(refl(hi, i) for i in range(3) if i not in FORBID_REFLECTION_AXES):
        errors.append("a reflective UPPER face (hi_boundary = 2): the campaign mirrors across lower faces "
                      "only (the consumer's --reflect folds onto x_i >= centre)")
    idx = [i for i in range(3) if i not in FORBID_REFLECTION_AXES and refl(lo, i)]
    summary: dict = {"reflect": [AXES[i] for i in idx]}
    if not idx:
        return errors, warnings, summary

    def off_plane(vec: list[float] | None) -> list[str]:
        return [AXES[i] for i in idx if vec is not None and i < len(vec) and abs(vec[i]) > 1e-12]

    for key in MIRROR_KEYS:
        if key == "extraction_center" and (as_float(params.get("activate_extraction", "0")) or 0.0) == 0.0:
            continue        # extraction off: its centre is not read
        vec = _numbers(params, key)
        if key == "center" and (vec is None or len(vec) != 3):
            errors.append("reflective plane(s) but no 3-component 'center': the physics centre must sit "
                          "on them (center = 0 on each reflected axis)")
            continue
        if vec is None:
            warnings.append(f"mirror key '{key}' is not in the params: not checked against the "
                            "reflective plane(s)")
            continue
        if off_plane(vec):
            errors.append(f"{key} = {vec} is off the reflective plane(s) {off_plane(vec)}: the planes are "
                          f"the lower faces, so {key} must be 0 on each reflected axis")
    summary["cells_fraction"] = 1.0 / 2 ** len(idx)
    if "L_full" in params:
        # L_full / N_full name the full box; GRTeclyn halves them across the planes
        summary["full_box"] = [as_float(params["L_full"])] * 3
    else:
        L = as_float(params.get("L", "")) if "L" in params else None
        n = [as_float(params.get(f"N{i + 1}", params.get("N", ""))) for i in range(3)]
        if L and all(n):
            dx0 = L / max(n)
            summary["full_box"] = [2 * n[i] * dx0 if i in idx else n[i] * dx0 for i in range(3)]
    return errors, warnings, summary


def paths_check(params: dict[str, str], argv: str | None, consume_args: str) -> tuple[list[str], list[str], dict]:
    """(errors, warnings, summary): ONE RUN, ONE SPELLING.  Every path the
    launch assembled -- output_path, the scratch plot/check files, amr.restart,
    and the consumer's final flags -- must agree on the run's name.  The
    restart-suffix trap (2026-10-03, in the merger campaign: a doubled _r04000
    split one extension across two spellings and its consumer tracked a stream
    that never existed) is exactly a disagreement here, so it refuses before
    anything starts.  Consumer flags are matched against the campaign's
    run_root."""
    errors: list[str] = []
    warnings: list[str] = []

    def unquote(v: str) -> str:
        return v.strip().strip('"')

    out = unquote(params.get("output_path", ""))
    name = pathlib.PurePath(out).name if out else ""
    summary: dict = {"name": name}
    if not name:
        warnings.append("no output_path in the params: the path-consistency check has no run name")
        return errors, warnings, summary
    for key in ("amr.plot_file", "amr.check_file"):
        v = unquote(params.get(key, ""))
        if v and pathlib.PurePath(v).parent.name != name:
            errors.append(f"{key} lives under '{pathlib.PurePath(v).parent.name}' but output_path names "
                          f"'{name}': one run, one spelling (the restart-suffix trap)")
    rst = unquote(params.get("amr.restart", ""))
    if rst:
        step = re.sub(r".*Chk", "", rst.rstrip("/"))
        if step.isdigit() and not name.endswith(f"_r{step}"):
            errors.append(f"amr.restart is Chk{step} but the run's name does not end _r{step}: a restart "
                          f"leg's name carries its checkpoint's step (launch with --restart, and never "
                          f"keep a parent's amr.restart line in a template)")
    try:
        toks = shlex.split(argv) if argv else shlex.split(consume_args or "")
    except ValueError:
        toks = (argv or consume_args or "").split()
    for t in toks:
        m = RUN_PATH_RE.search(t)
        if not m or m.group(1) == name:
            continue
        other = m.group(1)
        if other.startswith(name + "_r") or name.startswith(other + "_r"):
            errors.append(f"a consumer flag points at '{other}' but this run is '{name}' "
                          f"(the restart-suffix trap): {t}")
        else:
            warnings.append(f"a consumer flag points at another run ('{other}'); kept -- "
                            f"a cross-run reference must be deliberate: {t}")
    return errors, warnings, summary


def consumer_check(params: dict[str, str], consume_args: str, consume_on: bool,
                   reflect: list[str] | None = None) -> tuple[list[str], list[str], dict]:
    """(errors, warnings, summary) for what the plotfile consumer is asked to
    extract against what the plotfiles will carry, and against the box's
    symmetry planes (``reflect``, from symmetry_check).  The full-metric areal
    radius is opt-in and needs h22 and h33; --neck-horizons needs its eight
    fields."""
    reflect = list(reflect or [])
    try:
        toks = shlex.split(consume_args or "")
    except ValueError:
        toks = (consume_args or "").split()
    summary = {"consume": consume_on, "areal_radius": "off",
               "neck_horizons": "--neck-horizons" in toks, "reflect": _flag_values(toks, "--reflect")}
    errors, warnings = [], []
    if not consume_on:
        return errors, warnings, summary
    have = set(params["amr.plot_vars"].split()) if "amr.plot_vars" in params else None
    need: dict[str, list[str]] = {}
    areal, full = "--areal-radius" in toks, "--areal-full-metric" in toks
    if full and not areal:
        errors.append("--areal-full-metric without --areal-radius: the consumer extracts no areal radius at all")
    if areal:
        summary["areal_radius"] = ("full metric, r (h22 h33)^(1/4)/sqrt(chi)" if full
                                   else "flat conformal metric, r/sqrt(chi)")
        need["--areal-full-metric" if full else "--areal-radius"] = ["chi", "h22", "h33"] if full else ["chi"]
        if not full:
            warnings.append("areal radius is r/sqrt(chi) (flat conformal metric): exact at t = 0, a lower "
                            "bound once the Gamma-driver shift has moved the grid; --areal-full-metric uses h22, h33")
    if summary["neck_horizons"]:
        need["--neck-horizons"] = ["chi", "K", "lapse", "h11", "h22", "h33", "A11", "phi"]
    for flag, fields in need.items():
        if have is None:
            warnings.append(f"amr.plot_vars not set: the fields {flag} needs ({', '.join(fields)}) are not checked")
            continue
        lacking = [v for v in fields if v not in have]
        if lacking:
            errors.append(f"the consumer's {flag} needs {', '.join(lacking)} in amr.plot_vars, "
                          "which the plotfiles will not carry")
    if sorted(summary["reflect"]) != sorted(reflect):
        errors.append(f"the params make {' '.join(reflect) or 'no'} plane(s) reflective but the consumer's "
                      f"--reflect names {' '.join(summary['reflect']) or 'none'}: its sphere samplers and "
                      "frames would work on the wrong domain")
    if reflect:
        if "--horizon-scan" in toks:
            errors.append("--horizon-scan in a symmetry-reduced box: the star scan samples the full sphere "
                          "round the centre (use --neck-horizons for the trapping horizons)")
        fc = _flag_values(toks, "--frames-center")
        try:
            fcv = [float(v) for v in fc]
        except ValueError:
            fcv = []
        bad = [a for a in reflect if len(fcv) == 3 and abs(fcv[AXES.index(a)]) > 1e-12]
        if bad:
            errors.append(f"--frames-center {' '.join(fc)} is off the reflective plane(s) {bad}: the frames "
                          "mirror about the centre")

    # A slice coordinate outside the box renders the clamped domain edge:
    # featureless frames, no error anywhere (2026-10-10: the first smoke
    # frames sliced z = 32 on an L = 16 box and showed no throat at all).
    # The coordinates are absolute code units, so the valid window is [0, L].
    L_box = as_float(params.get("L", "")) if "L" in params else None
    if L_box:
        for v in _flag_values(toks, "--frames-coord"):
            try:
                fv = float(v)
            except ValueError:
                continue
            if fv < 0.0 or fv > L_box:
                errors.append(f"--frames-coord {v} is outside the box [0, {L_box:g}]: the renderer clamps "
                              "the slice to the domain edge and draws featureless frames")
        for v in _flag_values(toks, "--frames-center"):
            try:
                fv = float(v)
            except ValueError:
                continue
            if fv < 0.0 or fv > L_box:
                errors.append(f"--frames-center component {v} is outside the box [0, {L_box:g}]: the window "
                              "would be clamped off the physics")
    return errors, warnings, summary


# ---------------------------------------------------------------- 0. frames
#: Names the consumer accepts for a field (consume_plotfiles/fields.py).
FRAME_ALIASES = {"Weyl": "Weyl4_Re", "Weyl4": "Weyl4_Re", "Weyl_Re": "Weyl4_Re",
                 "Weyl_Im": "Weyl4_Im", "Weyl_Mag": "Weyl4_Mag"}
#: Frame fields the renderer derives (consume_plotfiles/fields.py) -> the
#: plotfile components each one reads.  Any other name must be a component.
DERIVED_FRAME_FIELDS = {
    "chi_minus_1": ("chi",),
    "Weyl4_Mag": ("Weyl4_Re", "Weyl4_Im"),
    "scalar_activity": ("phi", "Pi"),
    "local_speed": ("chi", "lapse", "shift1", "shift2", "shift3", "h11", "h22", "h33"),
    "GW_Plus": ("A11", "A22"), "GW_Cross": ("A12",), "weyl4": ("A11", "A12", "A22"),
}
#: amr.derive_plot_vars names -> the plotfile components they write.
DERIVE_COMPONENTS = {"Weyl4": ("Weyl4_Re", "Weyl4_Im")}


def load_frames_default(path: pathlib.Path | None = None) -> list[str]:
    """The campaign's frame fields: its frames_file, one per line, # comments."""
    path = path or FRAMES_FILE
    if path is None:
        raise RuntimeError("no frames_file: apply_campaign_config() was not called")
    out: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        out.extend(line.split("#", 1)[0].split())
    return out


def _last_flag_values(toks: list[str], flag: str) -> list[str] | None:
    """The tokens after the LAST ``flag`` up to the next option (argparse: the
    last occurrence wins), or None if the flag is absent."""
    if flag not in toks:
        return None
    i = len(toks) - 1 - toks[::-1].index(flag)
    out = []
    for t in toks[i + 1:]:
        if t.startswith("--"):
            break
        out.append(t)
    return out


def plotfile_components(params: dict[str, str]) -> set[str] | None:
    """The components the run's plotfiles will carry: amr.plot_vars plus what
    amr.derive_plot_vars writes.  None when amr.plot_vars is absent or ALL
    (AMReX then writes every state variable, which this cannot list)."""
    if "amr.plot_vars" not in params:
        return None
    pv = params["amr.plot_vars"].split()
    if any(v.upper() == "ALL" for v in pv):
        return None
    have = {v for v in pv if v.upper() != "NONE"}
    dv = params.get("amr.derive_plot_vars", "").split()
    if any(v.upper() == "ALL" for v in dv):
        dv = list(DERIVE_COMPONENTS)
    for d in dv:
        if d.upper() != "NONE":
            have.update(DERIVE_COMPONENTS.get(d, (d,)))
    return have


def frames_check(params: dict[str, str], toks: list[str], consume_on: bool, required: list[str],
                 subset_reason: str = "", source: str = "") -> tuple[list[str], list[str], dict]:
    """(errors, warnings, summary) for the frames the consumer will render
    (``toks``: its final flags) against the campaign default (``required``,
    its frames_default.txt) and against what the plotfiles will carry."""
    subset_reason = (subset_reason or "").strip()
    fields = [FRAME_ALIASES.get(f, f) for f in (_last_flag_values(toks, "--frames-fields") or [])]
    fields = list(dict.fromkeys(fields))
    summary: dict = {"fields": fields, "required": list(required), "missing": [],
                     "subset": subset_reason or None, "source": source or None,
                     "axis": (_last_flag_values(toks, "--frames-axis") or ["z"])[0]}
    errors: list[str] = []
    warnings: list[str] = []
    if not consume_on:
        summary.update(fields=[], note=f"no consumer ({ENV_PREFIX}_CONSUME=0): no frames, and no plotfile is deleted")
        return errors, warnings, summary
    missing = [f for f in required if f not in fields]
    summary["missing"] = missing
    if missing and not subset_reason:
        errors.append(
            f"frames: the launch would render {len(required) - len(missing)} of the campaign's {len(required)} "
            f"frame fields -- MISSING {' '.join(missing)} (frame list: {' '.join(fields) or 'none'}; "
            f"from {source or 'the consumer flags'}).  The consumer deletes each plotfile once it is extracted, "
            "so those movies could never be made afterwards.  Render the full set (frames_default.txt: leave "
            f"--frames-fields out of {ENV_PREFIX}_CONSUME_ARGS and {ENV_PREFIX}_FRAMES_FIELDS unset, or name "
            f"every field), or launch the subset on purpose with {ENV_PREFIX}_FRAMES_SUBSET=\"<reason>\" "
            "(recorded in run_manifest.json)")
    elif missing:
        warnings.append(f"frames: a SUBSET on purpose ({ENV_PREFIX}_FRAMES_SUBSET={subset_reason!r}): no movie of "
                        f"{' '.join(missing)} -- recorded in run_manifest.json")
    elif subset_reason:
        warnings.append(f"{ENV_PREFIX}_FRAMES_SUBSET={subset_reason!r} is set but the frame list is the full set: "
                        "nothing to excuse")
    # Plotfiles come from GRTeclyn's plot_interval or AMReX's own amr.plot_int /
    # amr.plot_per: none positive, no plotfile, no frame.
    cadence = {k: as_float(params[k]) for k in ("plot_interval", "amr.plot_int", "amr.plot_per") if k in params}
    if fields and not any((v or 0.0) > 0 for v in cadence.values()):
        errors.append("frames: " + (", ".join(f"{k} = {params[k].split()[0]}" for k in cadence) or
                                    "no plot_interval")
                      + ": the run writes no plotfile, so the consumer renders no frame at all")
    have = plotfile_components(params)
    if have is None:
        warnings.append("amr.plot_vars not set (or ALL): the frame fields' plot variables are not checked "
                        "by name; the t = 0 render still checks them")
        return errors, warnings, summary
    lacking = {}
    for f in fields:
        miss = [c for c in DERIVED_FRAME_FIELDS.get(f, (f,)) if c not in have]
        if miss:
            lacking[f] = miss
    if lacking:
        summary["lacking"] = lacking
        by_need: dict[str, list[str]] = {}
        state_missing: list[str] = []
        state_fields: list[str] = []
        for f, miss in lacking.items():
            for c in miss:
                d = next((d for d, comps in DERIVE_COMPONENTS.items() if c in comps), None)
                if d:
                    by_need.setdefault(d, [])
                    if f not in by_need[d]:
                        by_need[d].append(f)
                else:
                    if c not in state_missing:
                        state_missing.append(c)
                    if f not in state_fields:
                        state_fields.append(f)
        parts = []
        if state_fields:
            parts.append(f"{' '.join(state_fields)} need {' '.join(state_missing)} in amr.plot_vars")
        parts += [f"{' '.join(fs)} need {d} in amr.derive_plot_vars" for d, fs in by_need.items()]
        errors.append("frames: " + "; ".join(parts) + ", which the params do not write -- those frames would "
                      "silently not exist.  Add them to the params, or leave the fields out and say why: "
                      f"{ENV_PREFIX}_FRAMES_SUBSET=\"<reason>\"")
    return errors, warnings, summary


# ---------------------------------------------------------------- 1. static
_BLOBS: dict[pathlib.Path, bytes] = {}


def static_check(exe: pathlib.Path, keys: list[str]) -> list[str]:
    """Keys whose name (or, for a prefixed key, its last component) does not
    occur anywhere in the binary.  ParmParse("amr").query("plot_file") stores
    "plot_file", so amr.plot_file is looked up by its last component."""
    exe = pathlib.Path(exe).resolve()
    if exe not in _BLOBS:                 # a backfill checks many runs against few binaries
        _BLOBS[exe] = exe.read_bytes()
    blob = _BLOBS[exe]
    missing = []
    for key in keys:
        candidates = {key.encode(), key.rsplit(".", 1)[-1].encode()}
        if not any(c in blob for c in candidates):
            missing.append(key)
    return missing


# ---------------------------------------------------------------- 2./3. probes
def load_allow() -> dict[str, tuple[tuple[str, str] | None, str]]:
    """key -> (condition, why) from the campaign's allow file.  A line is
    `key  # why`, or `key when other = value  # why` for a key read only inside
    a feature the params can switch off: it is then allowed only while the
    params hold other = value.  An absent `other` counts as that value, so a
    condition must name the code default."""
    allow: dict[str, tuple[tuple[str, str] | None, str]] = {}
    if ALLOW_FILE is not None and ALLOW_FILE.exists():
        for line in ALLOW_FILE.read_text(encoding="utf-8").splitlines():
            body = line.split("#", 1)
            head, _, cond = body[0].partition(" when ")
            key = head.strip()
            if not key:
                continue
            other, _, value = cond.partition("=")
            allow[key] = (((other.strip(), value.strip()) if cond.strip() else None),
                          body[1].strip() if len(body) > 1 else "")
    return allow


def _flag(v: str) -> str:
    v = v.strip().strip('"').lower()
    return {"false": "0", "true": "1"}.get(v, v)


def is_allowed(key: str, allow: dict, params: dict[str, str]) -> bool:
    """Whether an unread (or absent) key is covered by the allow file here."""
    if key not in allow:
        return False
    cond = allow[key][0]
    if cond is None:
        return True
    other, value = cond
    return _flag(params.get(other, value)) == _flag(value)


def t0_rows(data_dir: pathlib.Path) -> dict[str, dict[str, float]]:
    """First data row of every .dat stream the start-up wrote, by column name."""
    rows: dict[str, dict[str, float]] = {}
    for f in sorted(data_dir.rglob("*.dat")):
        names: list[str] = []
        with f.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if line.startswith("#"):
                    names = line.lstrip("#").split()
                    continue
                vals = line.split()
                if not vals:
                    continue
                try:
                    nums = [float(v) for v in vals]
                except ValueError:
                    break
                if len(names) != len(nums):
                    names = [f"c{i}" for i in range(len(nums))]
                rows[f.name] = dict(zip(names, nums))
                break
    return rows


def probe(exe_run: pathlib.Path, argv0: str, params_text: str, overrides: dict[str, str],
          workdir: pathlib.Path, gpu: str, timeout: float) -> dict:
    """One 0-step start-up in <workdir>; returns what it read and wrote."""
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True)
    ov = dict(overrides)
    ov.update({
        "output_path": f'"{workdir}"',
        "amr.plot_file": f'"{workdir}/plt"',
        "amr.check_file": f'"{workdir}/chk"',
    })
    (workdir / "params.txt").write_text(rewrite_params(params_text, ov), encoding="utf-8")
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(gpu))
    log = workdir / "probe.log"
    t0 = time.time()
    status = "ok"
    with log.open("w", encoding="utf-8") as fh:
        try:
            proc = subprocess.run([argv0, "params.txt"], executable=str(exe_run), cwd=workdir,
                                  env=env, stdout=fh, stderr=subprocess.STDOUT,
                                  stdin=subprocess.DEVNULL, timeout=timeout, check=False)
            code = proc.returncode
        except subprocess.TimeoutExpired:
            code, status = None, "timeout"
    text = log.read_text(encoding="utf-8", errors="replace")
    unused = sorted(set(UNUSED_RE.findall(text)))
    version = None
    pv = workdir / "parameters_and_version.txt"
    if pv.exists():
        m = VERSION_RE.search(pv.read_text(encoding="utf-8", errors="replace"))
        version = m.group(1) if m else None
    rows = t0_rows(workdir)
    if status == "ok" and code != 0 and not unused:
        status = "crashed"
    return {"status": status, "exit_code": code, "unused": unused, "version": version,
            "t0": rows, "seconds": round(time.time() - t0, 1),
            "log_tail": text.splitlines()[-25:] if status != "ok" else []}


def max_rel_diff(a: dict[str, dict[str, float]], b: dict[str, dict[str, float]]) -> tuple[float, str]:
    worst, where = 0.0, ""
    for fname in sorted(set(a) & set(b)):
        for col in sorted(set(a[fname]) & set(b[fname])):
            if col.lower() in ("time", "t", "c0"):
                continue
            x, y = a[fname][col], b[fname][col]
            if math.isnan(x) or math.isnan(y):
                continue
            scale = max(abs(x), abs(y), 1e-300)
            d = abs(x - y) / scale if (x or y) else 0.0
            if d > worst:
                worst, where = d, f"{fname}:{col}"
    return worst, where


# ---------------------------------------------------------------- 4. frames
PLOTFILE_RE = re.compile(r".*[Pp]lt(\d+)$")      # consume_plotfiles/plotfiles.py
SKIPPED_RE = re.compile(r"WARNING: frame field '([^']+)' skipped for \S+: (.*)")
#: The consumer flags that decide what a frame shows (the rest are extractions).
FRAME_FLAGS = ("--frames-axis", "--frames-coord", "--frames-zoom", "--frames-center", "--center",
               "--reflect", "--frames-zlim-t0")
FRAME_SWITCHES = ("--frames-corner", "--frames-auto-zlim", "--frames-global-zlim", "--no-frames-global-zlim")


def plotfiles_in(d: pathlib.Path) -> list[pathlib.Path]:
    return sorted(p for p in d.iterdir() if PLOTFILE_RE.match(p.name) and (p / "Header").is_file()) \
        if d.is_dir() else []


def plotfile_extrema(plt: pathlib.Path) -> dict[str, tuple[float, float]]:
    """component -> (min, max) over every level, from the per-box min/max AMReX
    writes into each Level_*/Cell_H.  {} if the plotfile does not carry them."""
    try:
        head = (plt / "Header").read_text(encoding="utf-8", errors="replace").splitlines()
        ncomp = int(head[1])
        names = [s.strip() for s in head[2:2 + ncomp]]
    except (OSError, ValueError, IndexError):
        return {}
    ext: dict[str, list[float]] = {}
    for cell_h in sorted(plt.glob("Level_*/Cell_H")):
        lines = cell_h.read_text(encoding="utf-8", errors="replace").splitlines()
        marks = [i for i, line in enumerate(lines) if re.fullmatch(r"\s*\d+\s*,\s*\d+\s*", line)]
        if len(marks) < 2:
            return {}
        for k, start in ((0, marks[-2]), (1, marks[-1])):        # the mins, then the maxes
            nbox, nc = (int(v) for v in lines[start].split(","))
            if nc != ncomp:
                return {}
            for b in range(nbox):
                vals = [float(v) for v in lines[start + 1 + b].strip().rstrip(",").split(",")]
                for c, name in enumerate(names):
                    cur = ext.setdefault(name, [math.inf, -math.inf])
                    cur[k] = min(cur[k], vals[c]) if k == 0 else max(cur[k], vals[c])
    return {k: (v[0], v[1]) for k, v in ext.items()}


def read_slice(npz: pathlib.Path) -> array.array:
    """The ``arr`` of a slice-cache .npz (frames/slice_cache.py), standard library only."""
    with zipfile.ZipFile(npz) as z:
        raw = z.read("arr.npy")
    if raw[:6] != b"\x93NUMPY":
        raise ValueError("not a .npy array")
    if raw[6] == 1:
        hlen, off = struct.unpack("<H", raw[8:10])[0], 10
    else:
        hlen, off = struct.unpack("<I", raw[8:12])[0], 12
    header = ast.literal_eval(raw[off:off + hlen].decode("latin1"))
    code = {"<f4": "f", "<f8": "d", ">f4": "f", ">f8": "d"}.get(header.get("descr"))
    if code is None:
        raise ValueError(f"dtype {header.get('descr')!r}")
    arr = array.array(code)
    arr.frombytes(raw[off + hlen:])
    if (header["descr"][0] == ">") != (sys.byteorder == "big"):
        arr.byteswap()
    return arr


def judge_frame(field: str, png: pathlib.Path, npz: pathlib.Path, extrema: dict, skipped: str | None) -> dict:
    """ok / flat / FAILED for one rendered field, from the slice it drew."""
    if not png.is_file() and not npz.is_file():
        return {"verdict": "FAILED", "why": f"no frame drawn ({skipped or 'the consumer wrote nothing for it'})"}
    if not png.is_file() or png.stat().st_size == 0:
        return {"verdict": "FAILED", "why": "no PNG (the slice was taken but not drawn)"}
    if not npz.is_file():
        return {"verdict": "FAILED", "why": "PNG drawn but no slice cached, so it cannot be checked"}
    try:
        vals = read_slice(npz)
    except (OSError, ValueError, KeyError, SyntaxError, zipfile.BadZipFile) as exc:
        return {"verdict": "FAILED", "why": f"unreadable slice ({exc})"}
    finite = [v for v in vals if math.isfinite(v)]
    rec = {"pixels": len(vals), "nan": len(vals) - len(finite)}
    if not finite:
        return dict(rec, verdict="FAILED", why="every pixel is NaN or inf")
    lo, hi = min(finite), max(finite)
    rec.update(min=lo, max=hi)
    if hi - lo > 1e-12 * max(abs(lo), abs(hi)):
        return dict(rec, verdict="ok")
    comps = DERIVED_FRAME_FIELDS.get(field, (field,))
    ext = [extrema.get(c) for c in comps]
    if ext and all(e is not None and e[0] == e[1] for e in ext):
        return dict(rec, verdict="flat",
                    why=f"every pixel {lo:g}: {' '.join(comps)} "
                        f"{'is' if len(comps) == 1 else 'are'} constant everywhere in this plotfile (nothing to show yet)")
    where = ", ".join(f"{c} {e[0]:.3g}..{e[1]:.3g}" for c, e in zip(comps, ext) if e is not None)
    return dict(rec, verdict="FAILED",
                why=f"blank: every pixel is {lo:g}, but the plotfile varies ({where or 'extrema unknown'}) -- the "
                    "slice or the window misses it")


def render_frames(plt: pathlib.Path, data_arg: pathlib.Path, out_arg: pathlib.Path, toks: list[str],
                  fields: list[str], axis: str, frames_out: pathlib.Path, cmd: list[str], timeout: float) -> dict:
    """Render ``fields`` from the plotfile ``plt`` with the consumer itself and
    the run's own frame flags, then judge each field from its cached slice.
    ``data_arg``/``out_arg``/``frames_out`` go on the consumer's command line,
    which is public: run_single.sh passes them relative to the run directory."""
    idx = int(PLOTFILE_RE.match(plt.name).group(1))
    frames_out.mkdir(parents=True, exist_ok=True)
    args = ["--data", str(data_arg), "--out", str(out_arg), "--frames-out", str(frames_out),
            "--stable-seconds", "0", "--no-psi4", "--verbose", "--frames-cache-slices",
            "--frames-fields", *fields]
    for flag in FRAME_FLAGS:
        vals = _last_flag_values(toks, flag)
        if vals is not None:
            args += [flag, *vals]
    args += [s for s in FRAME_SWITCHES if s in toks]
    log = frames_out / "render.log"
    t0 = time.time()
    status = "ok"
    with log.open("w", encoding="utf-8") as fh:
        try:
            proc = subprocess.run(cmd + args, cwd=os.getcwd(), stdout=fh, stderr=subprocess.STDOUT,
                                  stdin=subprocess.DEVNULL, timeout=timeout, check=False)
            if proc.returncode != 0:
                status = f"consumer exit {proc.returncode}"
        except subprocess.TimeoutExpired:
            status = f"timeout after {timeout:g} s"
        except OSError as exc:
            status = f"could not start the consumer ({exc})"
    seconds = round(time.time() - t0, 1)
    text = log.read_text(encoding="utf-8", errors="replace")
    skipped = dict(SKIPPED_RE.findall(text))
    extrema = plotfile_extrema(plt)
    per_field = {}
    for f in fields:
        png = frames_out / f"{f}_{axis}" / "frames" / f"frame_{axis}_{idx:04d}.png"
        npz = frames_out / "_slice_cache" / f"{f}_{axis}" / f"slice_{idx:04d}.npz"
        per_field[f] = judge_frame(f, png, npz, extrema, skipped.get(f))
    return {"plotfile": plt.name, "frame": idx, "status": status, "seconds": seconds,
            "frames_out": _shown(frames_out), "log": _shown(log), "fields": per_field,
            "log_tail": text.splitlines()[-12:] if status != "ok" else []}


def _shown(p: pathlib.Path) -> str:
    """A path for the report, which is packed with the run: relative to the
    working directory (the run directory) when under it, else its last parts."""
    try:
        return str(pathlib.Path(p).resolve().relative_to(pathlib.Path.cwd().resolve()))
    except ValueError:
        return str(pathlib.Path(*pathlib.Path(p).parts[-2:]))


# ---------------------------------------------------------------- driver
def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--campaign-config", default=os.environ.get("CAMPAIGN_PREFLIGHT_CONFIG"),
                    help="the campaign's preflight_campaign.json (default: $CAMPAIGN_PREFLIGHT_CONFIG; "
                         "the env route keeps the path off the public command line)")
    ap.add_argument("--exe", required=True, help="the binary the run will use")
    ap.add_argument("--exe-run", help="copy actually executed (process-table alias); default --exe")
    ap.add_argument("--exe-name", default=None,
                    help="the binary's real file name for the report (default: $<prefix>_EXE_NAME, else --exe's)")
    ap.add_argument("--argv0", default="test", help="process name for the start-ups")
    ap.add_argument("--params", required=True, help="the run's final params file")
    ap.add_argument("--gpu", default="0", help="CUDA device for the start-ups")
    ap.add_argument("--workdir", required=True, help="scratch directory for the start-ups")
    ap.add_argument("--mode", choices=("full", "static", "off"), default="full",
                    help="off (<prefix>_PREFLIGHT=off): the frame-list check only")
    ap.add_argument("--restart", action="store_true", help="the run restarts from a checkpoint")
    ap.add_argument("--timeout", type=float, default=1800.0, help="seconds per start-up")
    ap.add_argument("--json", help="write the report here")
    ap.add_argument("--keep", action="store_true", help="keep the workdir even on success")
    ap.add_argument("--consume", default=None, choices=("0", "1"),
                    help="whether the run gets a consumer (default: $<prefix>_CONSUME, else 1)")
    ap.add_argument("--consume-args", default=None,
                    help="the plotfile consumer's flags (default: $<prefix>_CONSUME_ARGS, as run_single.sh has them)")
    ap.add_argument("--consumer-argv", default=None,
                    help="the consumer's FINAL flags, launcher defaults included (default: $<prefix>_CONSUMER_ARGV; "
                         "without it, --consume-args plus the default frames, as run_single.sh would add them)")
    ap.add_argument("--frames-required", default=None,
                    help="the fields every launch must render (default: the campaign's frames_default.txt)")
    ap.add_argument("--frames-fields-default", default=None,
                    help="frame fields when --consumer-argv is absent and --consume-args names none "
                         "(default: $<prefix>_FRAMES_FIELDS, else the required set)")
    ap.add_argument("--frames-subset", default=None,
                    help="why this launch renders fewer (default: $<prefix>_FRAMES_SUBSET)")
    ap.add_argument("--frames-source", default=None,
                    help="where the frame list came from, for the report (default: $<prefix>_FRAMES_SOURCE)")
    ap.add_argument("--frames-cmd", default=None,
                    help="the consumer command that renders the t = 0 frames, e.g. 'test_post post.py' "
                         "(default: $<prefix>_FRAMES_CMD, else this python -m the consumer module)")
    ap.add_argument("--frames-out", default=None,
                    help="where the t = 0 frames go (default: <workdir>/frames); never the run's frames/")
    ap.add_argument("--render-timeout", type=float, default=1800.0, help="seconds for the t = 0 render")
    a = ap.parse_args(argv)

    if not a.campaign_config:
        print("[preflight] no --campaign-config and no $CAMPAIGN_PREFLIGHT_CONFIG: the engine needs the "
              "campaign's preflight_campaign.json", file=sys.stderr)
        return 2
    apply_campaign_config(a.campaign_config)
    # CLI flags stay primary; the launcher's env vars are their defaults
    # (revealing values go through the environment because the process table is
    # public -- run_single.sh, "Process table").
    if a.exe_name is None:
        a.exe_name = env_get("EXE_NAME")
    if a.consume_args is None:
        a.consume_args = env_get("CONSUME_ARGS", "")
    if a.consumer_argv is None:
        a.consumer_argv = env_get("CONSUMER_ARGV")
    if a.frames_subset is None:
        a.frames_subset = env_get("FRAMES_SUBSET", "")
    if a.frames_source is None:
        a.frames_source = env_get("FRAMES_SOURCE", "")
    if a.frames_cmd is None:
        a.frames_cmd = env_get("FRAMES_CMD", "")
    if a.frames_fields_default is None:
        a.frames_fields_default = env_get("FRAMES_FIELDS", "")
    consume_on = (a.consume if a.consume is not None else env_get("CONSUME", "1")) != "0"

    exe = pathlib.Path(a.exe).resolve()
    exe_run = pathlib.Path(a.exe_run or a.exe).resolve()
    params_path = pathlib.Path(a.params).resolve()
    workdir_arg = pathlib.Path(a.workdir)          # as given (relative): for public command lines
    workdir = workdir_arg.resolve()
    text = params_path.read_text(encoding="utf-8")
    params = parse_params(text)
    report: dict = {
        "schema": 1, "campaign": CAMPAIGN, "mode": a.mode, "restart": a.restart,
        "exe": a.exe_name or exe.name, "exe_sha256": sha256(exe), "params_sha256": sha256(params_path),
        "verdict": None, "reasons": [],
    }

    def finish(verdict: str, code: int) -> int:
        report["verdict"] = verdict
        if a.json:
            pathlib.Path(a.json).write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
        for r in report["reasons"]:
            print(f"[preflight]   - {r}")
        print(f"[preflight] verdict: {verdict.upper()}")
        return code

    # The frames: every mode, off included (the only override is the
    # FRAMES_SUBSET reason).  The list is the consumer's FINAL flags.
    required = a.frames_required.split() if a.frames_required is not None else load_frames_default()
    if a.consumer_argv is not None:
        ftoks = shlex.split(a.consumer_argv)
        source = a.frames_source
    else:
        ftoks = shlex.split(a.consume_args or "")
        source = a.frames_source or "--consume-args"
        if "--frames-fields" not in ftoks:
            ftoks += ["--frames-fields", *(a.frames_fields_default.split() or required)]
            source = a.frames_source or (f"{ENV_PREFIX}_FRAMES_FIELDS" if a.frames_fields_default
                                         else "campaign default (frames_default.txt)")
    f_err, f_warn, f_sum = frames_check(params, ftoks, consume_on, required, a.frames_subset, source)
    report["frames"] = dict(f_sum, errors=f_err, warnings=f_warn)
    if consume_on:
        print(f"[preflight] frames : {len(f_sum['fields'])} field(s), "
              + ("the full set" if not f_sum["missing"] else f"MISSING {' '.join(f_sum['missing'])}")
              + (f" [SUBSET: {f_sum['subset']}]" if f_sum["subset"] and f_sum["missing"] else "")
              + f": {' '.join(f_sum['fields'])}")
    else:
        print(f"[preflight] frames : none (no consumer: {ENV_PREFIX}_CONSUME=0)")
    if a.mode == "off":
        report["frames"]["render"] = {"verdict": f"not rendered ({ENV_PREFIX}_PREFLIGHT=off)"}
        for w in f_warn:
            print(f"[preflight] WARNING: {w}")
        if f_err:
            report["reasons"].extend(f_err)
            return finish("refused", 1)
        return finish(f"skipped ({ENV_PREFIX}_PREFLIGHT=off)", 0)

    errors, warnings = intent_check(params)
    report["intent"] = {"errors": errors, "warnings": warnings}
    r_err, r_sum = required_files_check(params)
    report["required_files"] = dict(r_sum, errors=r_err)
    if REQUIRED_FILE_KEYS and not r_err:
        print("[preflight] files  : " + "  ".join(f"{k} = {v}" for k, v in r_sum["files"].items()))
    errors = errors + r_err
    s_err, s_warn, s_sum = symmetry_check(params)
    report["symmetry"] = dict(s_sum, errors=s_err, warnings=s_warn)
    if s_sum["reflect"]:
        box = s_sum.get("full_box")
        print(f"[preflight] symmetry: mirror planes {' '.join(s_sum['reflect'])} = 0; the run holds "
              f"{s_sum.get('cells_fraction', 0):g} of the box"
              + (f" {' x '.join(f'{v:g}' for v in box)}" if box else ""))
    c_err, c_warn, c_sum = consumer_check(params, a.consume_args, consume_on,
                                          reflect=s_sum["reflect"])
    report["consumer"] = dict(c_sum, errors=c_err, warnings=c_warn)
    print(f"[preflight] consumer: areal radius {c_sum['areal_radius']}"
          + ("; neck + horizons" if c_sum["neck_horizons"] else "")
          + (f"; --reflect {' '.join(c_sum['reflect'])}" if c_sum["reflect"] else "")
          + ("" if c_sum["consume"] else f" (no consumer: {ENV_PREFIX}_CONSUME=0)"))
    p_err, p_warn, p_sum = paths_check(params, a.consumer_argv, a.consume_args)
    report["paths"] = dict(p_sum, errors=p_err, warnings=p_warn)
    if p_sum.get("name"):
        print(f"[preflight] paths  : " + ("one spelling, '" + p_sum["name"] + "'" if not p_err
                                          else f"INCONSISTENT ({len(p_err)} disagreement(s), below)"))
    errors, warnings = (errors + s_err + c_err + f_err + p_err,
                        warnings + s_warn + c_warn + f_warn + p_warn)
    for w in warnings:
        print(f"[preflight] WARNING: {w}")
    if errors:
        report["reasons"].extend(errors)
        return finish("refused", 1)

    missing = static_check(exe, list(params))
    allow = load_allow()
    blocking = [k for k in missing if not is_allowed(k, allow, params)]
    report["static"] = {"keys": len(params), "absent_from_binary": missing,
                        "allowed_absent": [k for k in missing if is_allowed(k, allow, params)]}
    print(f"[preflight] static : {len(params)} keys, {len(missing)} absent from {a.exe_name or exe.name}"
          + (f": {', '.join(missing)}" if missing else "")
          + (f" ({len(missing) - len(blocking)} of them dead keys the allow file names)"
             if len(blocking) < len(missing) else ""))
    render_fields = f_sum["fields"] if consume_on else []
    if a.mode == "static":
        if render_fields:
            report["frames"]["render"] = {"verdict": "not rendered (static preflight: no start-up, no t = 0 plotfile)"}
            print("[preflight] WARNING: frames NOT rendered -- the static preflight starts nothing, so there is "
                  "no t = 0 plotfile; eyeball frame 0 once the run is up")
        if blocking:
            report["reasons"].append(f"keys the binary cannot read: {', '.join(blocking)}")
            return finish("refused", 1)
        return finish("pass", 0)

    probe_ov = {
        "max_steps": "0", "plot_interval": "-1", "checkpoint_interval": "-1",
        "amr.plot_files_output": "0", "amr.checkpoint_files_output": "0",
        "amrex.abort_on_unused_inputs": "1", "amrex.verbose": "1",
    }
    # A feature that runs inside the start-up can outlast the whole start-up
    # budget (the merger's constraint solve timed out two full preflights at
    # 1800 s, 2026-09-29).  The checks here need the t = 0 hierarchy, not the
    # feature's converged result, so the start-ups cap it (probe_param_caps);
    # the run's own start-up runs in full.  Only cap keys the binary contains
    # are applied (an older build without one would report it unread).
    caps: dict[str, str] = {}
    if not a.restart:
        for trigger, trig_caps in PROBE_PARAM_CAPS.items():
            if params.get(trigger, "0").strip().strip('"').lower() in ("1", "true"):
                absent = set(static_check(exe, list(trig_caps)))
                caps.update({k: v for k, v in trig_caps.items() if k not in absent})
    if caps:
        probe_ov.update(caps)
        report["probe_param_caps"] = caps
        print("[preflight] caps   : the start-ups cap "
              + ", ".join(f"{k} = {v}" for k, v in caps.items())
              + " (probe_param_caps); the run itself runs in full")
    # The frames are rendered from this start-up's own plotfile: t = 0 for a
    # fresh start (written at init), the checkpoint's time for a restart
    # (written at exit).  Only the "run" start-up writes one.
    run_ov = dict(probe_ov, **({"plot_interval": "1", "amr.plot_files_output": "1"} if render_fields else {}))
    print(f"[preflight] start-up with every key checked (gpu {a.gpu}, 0 steps"
          + ("; writes its plotfile for the frames" if render_fields else "") + ") ...")
    run = probe(exe_run, a.argv0, text, run_ov, workdir / "run", a.gpu, a.timeout)
    report["probe"] = {k: run[k] for k in ("status", "exit_code", "unused", "version", "seconds", "log_tail")}
    report["t0"] = run["t0"]
    report["grteclyn_version"] = run["version"]
    unread = [k for k in run["unused"] if not is_allowed(k, allow, params)]
    report["probe"]["allowed_unused"] = [k for k in run["unused"] if is_allowed(k, allow, params)]
    print(f"[preflight] probe  : {run['status']} in {run['seconds']} s; binary version "
          f"({run['version'] or 'not reported'}); {len(run['unused'])} unread key(s)")
    if unread:
        report["reasons"].append(
            "keys the binary did not read (ParmParse would have ignored them): " + ", ".join(unread))
        return finish("refused", 1)
    if run["status"] != "ok":
        report["reasons"].append(f"the start-up did not complete ({run['status']}, exit {run['exit_code']}); "
                                 f"log: {workdir / 'run' / 'probe.log'}")
        for line in run["log_tail"][-8:]:
            print(f"[preflight]   | {line}")
        return finish("error", 2)
    ham = run["t0"].get("constraint_norms.dat", {})
    if ham:
        print("[preflight] t = 0  : " + "  ".join(f"{k} {v:.10e}" for k, v in ham.items() if k != "time"))
    elif not a.restart:
        print("[preflight] WARNING: the start-up wrote no t = 0 diagnostics (calculate_constraint_norms off?)")

    if render_fields:
        plts = plotfiles_in(workdir / "run")
        if not plts:
            report["frames"]["render"] = {"verdict": "no plotfile"}
            if a.restart:
                print("[preflight] WARNING: frames NOT rendered -- the restart start-up wrote no plotfile")
            else:
                report["reasons"].append("frames: the start-up wrote no t = 0 plotfile, so no frame can be "
                                         f"checked (log: {_shown(workdir / 'run' / 'probe.log')})")
                return finish("refused", 1)
        else:
            cmd = shlex.split(a.frames_cmd) if a.frames_cmd else [
                sys.executable, "-m", "grteclyn_wrapper.visualisation.process_wave.consume_plotfiles"]
            frames_out = pathlib.Path(a.frames_out) if a.frames_out else workdir_arg / "frames"
            print(f"[preflight] frames : rendering {len(render_fields)} field(s) from {plts[-1].name} "
                  f"with the consumer -> {_shown(frames_out)} ...")
            rend = render_frames(plts[-1], workdir_arg / "run", workdir_arg / "render_out", ftoks,
                                 render_fields, f_sum["axis"], frames_out, cmd, a.render_timeout)
            report["frames"]["render"] = rend
            bad = {f: r for f, r in rend["fields"].items() if r["verdict"] == "FAILED"}
            flat = [f for f, r in rend["fields"].items() if r["verdict"] == "flat"]
            for f, r in rend["fields"].items():
                span = (f"{r['min']:.3g} .. {r['max']:.3g}" if "min" in r else "")
                print(f"[preflight]   {f:16s} {r['verdict']:6s} {span}"
                      + (f"  ({r['why']})" if r.get("why") else "")
                      + (f"  [{r['nan']} NaN pixel(s)]" if r.get("nan") else ""))
            print(f"[preflight] frames : {len(render_fields) - len(bad)} of {len(render_fields)} rendered "
                  f"in {rend['seconds']} s ({rend['status']})"
                  + (f"; flat at this time: {' '.join(flat)}" if flat else ""))
            if bad:
                for line in rend["log_tail"][-6:]:
                    print(f"[preflight]   | {line}")
                report["reasons"].append(
                    f"frames: {', '.join(bad)} FAILED to render from the t = 0 plotfile ("
                    + "; ".join(f"{f}: {r['why']}" for f, r in bad.items())
                    + f") -- see {rend['log']}.  Fix the params or the consumer flags, or leave those fields "
                    f"out and say why: {ENV_PREFIX}_FRAMES_SUBSET=\"<reason>\"")
                return finish("refused", 1)

    seeds = {k: v for k, v in params.items() if SEED_KEY_RE.match(k) and (as_float(v) or 0.0) != 0.0}
    report["seed"] = {"requested": seeds}
    if seeds and not a.restart and not run["t0"]:
        report["seed"]["verdict"] = "not checked (no t = 0 diagnostics to compare)"
        print("[preflight] WARNING: seed set but no t = 0 diagnostics -- its effect is NOT checked")
    elif seeds and not a.restart:
        ctrl_ov = dict(probe_ov)
        ctrl_ov.update({k: "0.0" for k in params if SEED_KEY_RE.match(k)})
        ctrl_ov["amrex.abort_on_unused_inputs"] = "0"
        print(f"[preflight] seed   : {', '.join(f'{k}={v}' for k, v in seeds.items())} -- "
              "start-up with the seed off, for comparison ...")
        ctrl = probe(exe_run, a.argv0, text, ctrl_ov, workdir / "control", a.gpu, a.timeout)
        if ctrl["status"] != "ok":
            report["reasons"].append(f"the seed-off comparison did not complete ({ctrl['status']})")
            return finish("error", 2)
        diff, where = max_rel_diff(run["t0"], ctrl["t0"])
        report["seed"].update({"control_t0": ctrl["t0"], "max_rel_diff": diff, "at": where,
                               "seconds": ctrl["seconds"]})
        if diff <= REL_TOL:
            report["seed"]["verdict"] = "no effect"
            report["reasons"].append(
                f"the seed changed nothing: every t = 0 diagnostic matches the seed-off start-up "
                f"(max relative difference {diff:.1e}) -- the binary ignores the seed")
            return finish("refused", 1)
        report["seed"]["verdict"] = "took"
        print(f"[preflight] seed   : took (largest t = 0 change {diff:.2e}, relative, in {where})")
    elif seeds:
        report["seed"]["verdict"] = "not checked (restart)"

    if not a.keep:
        shutil.rmtree(workdir, ignore_errors=True)
    return finish("pass", 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
