#!/usr/bin/env bash
# Pack a light, GitHub-friendly extract of the wormhole-merger campaign
# (runs/wormhole_merger) into results/merger/.
#
# WHAT IS COPIED
# Per-run time series (the four evolution streams, downsampled), the psi4
# streams whole, the evolution parameters, the launcher banner, the tail of the
# evolution log with the abort in it, the movies, and a thinned set of stills
# for the runs whose pictures carry a result.  Everything a reader needs to
# redraw a figure or re-read a number without the run tree.
#
# WHAT IS NOT
# Plotfiles and checkpoints (node-local scratch, tens of GB), the full frame
# series and the slice caches (7-260 MB per run).  Those stay in the gitignored
# runs/ tree.  The code the campaign added is already in git under
# Examples/BinaryWormholeMerger/ and is not duplicated here.
#
# DOWNSAMPLING
# The evolution streams are written every step (dt = 0.01), which is 6 000 rows
# and ~2 MB per stream per run.  They are thinned to dt = 0.05 -- except the
# last time unit of every run, which is kept at full cadence, because that is
# where a dying run does everything interesting.
#
# HORIZON SCAN
# results/merger/horizon/ holds the offline Theta = 0 scan behind the horizon-
# dissolution result.  Re-running it needs plotfiles that the consumer deletes
# as it goes, so it is off by default and the committed copy is left alone.
# PACK_HORIZON=1 regenerates it from whatever plotfiles still exist on scratch.
#
# Safe to re-run at any time, including while a run is still evolving: each run
# folder is rebuilt from scratch, and runs with no time series yet are skipped
# with a note.
#
# Machine identity is never hard-coded: absolute paths are scrubbed at runtime
# by grteclyn_wrapper.packaging.scrub_paths using tokens derived from the
# environment.
#
# Usage: bash research/merger/pack_results.sh
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"
SIM_ROOT="$(cd -- "${ROOT}/.." && pwd)"
RUNS="${ROOT}/runs/wormhole_merger"
DEST="${ROOT}/results/merger"
SCRATCH="${GRTECLYN_SCRATCH:-/tmp/grteclyn_scratch}"

export ROOT SIM_ROOT
PY_BIN="${ROOT}/.venv/bin/python"
[[ -x "${PY_BIN}" ]] || PY_BIN="$(command -v python3)"
scrub() { python3 "${ROOT}/grteclyn-wrapper/src/grteclyn_wrapper/packaging/scrub_paths.py" "$@"; }

if [[ ! -d "${RUNS}" ]]; then
  echo "[pack-merger] no run tree at ${RUNS#"${ROOT}"/} -- nothing to do"
  exit 0
fi

mkdir -p "${DEST}/campaign" "${DEST}/horizon"

# Stills are packed only where the pictures carry a result, and at a cadence
# matched to how long the run is: the whole point of a still here is to show the
# merger, the burst and the dissolution, not to re-store the movie frame by
# frame.  "<run>:<dt>" -- any run not named gets movies but no stills.
STILLS="merge_orbit_flip_d12_r03000:5 merge_orbit_flip_d12_rw_r05000:1 merge_orbit_flip_d12_p045:10 merge_headon_flip_d12:5 merge_orbit_flip_d12_n160:10"
STILL_FIELDS="chi_z lapse_z phi_z Weyl4_Re_z"

# ---------------------------------------------------------------------------
# 1. Per-run extract
# ---------------------------------------------------------------------------
for rundir in "${RUNS}"/merge_*/ "${RUNS}"/bbh_control_*/; do
  run="$(basename "${rundir%/}")"
  out="${DEST}/campaign/${run}"
  rm -rf "${out}"
  mkdir -p "${out}"

  # An arm with no evolution streams (lost, or dead before the first
  # extraction step) keeps its note, its provenance and the log with the
  # abort in it -- that is the whole evidence such an arm contributes.
  if [[ ! -d "${rundir}/data" && ! -d "${rundir}/extraction_data" ]]; then
    for f in LOST.md launch_banner.txt; do
      [[ -f "${rundir}/${f}" ]] && cp "${rundir}/${f}" "${out}/"
    done
    [[ -f "${rundir}/params.txt" ]] && cp "${rundir}/params.txt" "${out}/evolution_params.txt"
    [[ -f "${rundir}/Backtrace.0" ]] && cp "${rundir}/Backtrace.0" "${out}/backtrace.txt"
    if [[ -f "${rundir}/run.log.gz" ]]; then
      zcat "${rundir}/run.log.gz" | tail -n 200 > "${out}/run_tail.log"
    elif [[ -f "${rundir}/run.log" ]]; then
      tail -n 200 "${rundir}/run.log" > "${out}/run_tail.log"
    fi
    found=$(find "${out}" -maxdepth 1 -type f \( -name '*.txt' -o -name '*.md' -o -name '*.log' \))
    [[ -n "${found}" ]] && scrub ${found}
    echo "[pack-merger] ${run}: log-only arm ($(find "${out}" -type f | wc -l) files)"
    continue
  fi

  # Evolution streams, thinned.  __part1 files are the pre-restart episode of
  # the same run and are packed beside it under their own name.
  for src in "${rundir}"data/*.dat "${rundir}"extraction_data/*.dat "${rundir}"punctures_output/*.dat; do
    [[ -f "${src}" ]] || continue
    base="$(basename "${src}")"
    "${PY_BIN}" - "${src}" "${out}/${base}" <<'PY'
import sys

src, dst = sys.argv[1], sys.argv[2]
STEP, TAIL = 0.05, 1.0            # dt of the thinned stream; window kept whole

rows, head = [], []
with open(src, encoding="utf-8") as fh:
    for line in fh:
        if line.startswith("#") or not line.strip():
            head.append(line)
        else:
            rows.append(line)
if not rows:
    open(dst, "w", encoding="utf-8").writelines(head)
    raise SystemExit

t_end = float(rows[-1].split()[0])
with open(dst, "w", encoding="utf-8") as out:
    out.write(f"# thinned to dt={STEP:g} from the every-step stream; "
              f"the last {TAIL:g} time units are kept whole (the death window)\n")
    out.writelines(head)
    last = None
    for line in rows:
        t = float(line.split()[0])
        if t >= t_end - TAIL or last is None or t - last >= STEP - 1e-9:
            out.write(line)
            if t < t_end - TAIL:
                last = t
PY
  done

  # psi4 streams are already small (one row per plotfile) -- copied whole.
  for f in "${rundir}"small_data/*.dat "${rundir}"small_data/consume_state.json; do
    [[ -f "${f}" ]] && cp "${f}" "${out}/"
  done
  if [[ -d "${rundir}small_data__part1" ]]; then
    mkdir -p "${out}/part1"
    cp "${rundir}"small_data__part1/* "${out}/part1/" 2>/dev/null || true
  fi

  # Provenance: what was run, how it was launched, and where it stopped.
  [[ -f "${rundir}params.txt" ]] && cp "${rundir}params.txt" "${out}/evolution_params.txt"
  [[ -f "${rundir}params__part1.txt" ]] && cp "${rundir}params__part1.txt" "${out}/evolution_params__part1.txt"
  [[ -f "${rundir}launch_banner.txt" ]] && cp "${rundir}launch_banner.txt" "${out}/"
  [[ -f "${rundir}Backtrace.0" ]] && cp "${rundir}Backtrace.0" "${out}/backtrace.txt"
  if [[ -f "${rundir}run.log.gz" ]]; then
    zcat "${rundir}run.log.gz" | tail -n 200 > "${out}/run_tail.log"
  elif [[ -f "${rundir}run.log" ]]; then
    tail -n 200 "${rundir}run.log" > "${out}/run_tail.log"
  fi

  # Movies: ~1-3 MB per run for the whole set, so no curation is needed.
  if compgen -G "${rundir}movies/*.mp4" > /dev/null; then
    mkdir -p "${out}/movies"
    cp "${rundir}"movies/*.mp4 "${out}/movies/"
  fi

  # Stills, where the pictures carry a result.
  for spec in ${STILLS}; do
    [[ "${spec%%:*}" == "${run}" ]] || continue
    FIELDS="${STILL_FIELDS}" "${PY_BIN}" - "${rundir}frames" "${out}/frames" "${spec##*:}" <<'PY'
import os, pathlib, re, shutil, sys
import numpy as np

src, dst, dt = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), float(sys.argv[3])
fields = os.environ["FIELDS"].split()
idx_re = re.compile(r"(\d+)\.(?:npz|png)$")

# index -> time, from any cached series (all series share the step cadence).
times = {}
for series in sorted((src / "_slice_cache").glob("*")):
    if not series.is_dir():
        continue
    for f in sorted(series.glob("*.npz")):
        m = idx_re.search(f.name)
        if m:
            times[int(m.group(1))] = float(np.load(f, allow_pickle=True)["time"])
    if times:
        break
if not times:
    print(f"[pack-merger]   no slice cache under {src} -- no stills")
    raise SystemExit

t0, t1 = min(times.values()), max(times.values())
wanted, k = {}, 0
while t0 + k * dt <= t1 + 1e-9:
    target = t0 + k * dt
    i = min(times, key=lambda j: abs(times[j] - target))
    wanted[i] = times[i]
    k += 1

kept = 0
for field in fields:
    pngs = sorted((src / field / "frames").glob("*.png")) or sorted((src / field).glob("*.png"))
    by_index = {int(m.group(1)): f for f in pngs if (m := idx_re.search(f.name))}
    if not by_index:
        continue
    outdir = dst / field
    outdir.mkdir(parents=True, exist_ok=True)
    for i in sorted(wanted):
        pick = by_index.get(i) or by_index[min(by_index, key=lambda j: abs(j - i))]
        shutil.copy2(pick, outdir / pick.name)
        kept += 1
if kept:
    (dst / "FRAMES.md").write_text(
        "# Stills\n\nOne frame every dt = "
        f"{dt:g} for each of {', '.join(fields)}, picked by the time recorded in the\n"
        "run's slice cache.  The full series and the slice cache stay in the run tree.\n\n"
        "times kept: " + ", ".join(f"{t:g}" for t in sorted(wanted.values())) + "\n")
print(f"[pack-merger]   {kept} stills at dt = {dt:g}")
PY
  done

  found=$(find "${out}" -maxdepth 1 -type f \( -name '*.txt' -o -name '*.json' -o -name '*.md' -o -name '*.log' \))
  [[ -n "${found}" ]] && scrub ${found}
  echo "[pack-merger] campaign/${run}: $(find "${out}" -type f | wc -l) files, $(du -sh "${out}" | cut -f1)"
done

# ---------------------------------------------------------------------------
# 2. Offline horizon scan (opt-in: needs plotfiles that are deleted as runs go)
# ---------------------------------------------------------------------------
if [[ "${PACK_HORIZON:-0}" == "1" ]]; then
  raw="${DEST}/horizon/ah_radial_scan_output.txt"
  : > "${raw}"
  for plt in "${SCRATCH}"/merge_orbit_flip_d12_r04000/BinaryWormholePlt* \
             "${SCRATCH}"/merge_orbit_flip_d12_rw_r05000/BinaryWormholePlt*; do
    [[ -d "${plt}" ]] || continue
    echo "##### $(basename "$(dirname "${plt}")")/$(basename "${plt}")" >> "${raw}"
    "${PY_BIN}" "${ROOT}/grteclyn-wrapper/scripts/validation/ah_radial_scan.py" "${plt}" \
      >> "${raw}" 2>&1 || echo "  scan failed" >> "${raw}"
  done
  "${PY_BIN}" - "${raw}" "${DEST}/horizon/horizon_dissolution.dat" <<'PY'
import re, sys

raw, dst = sys.argv[1], sys.argv[2]
rows, arm = [], ""
for line in open(raw, encoding="utf-8"):
    if line.startswith("#####"):
        arm = line.split()[1]
    m = re.search(r"^(\S+)\s+t=([\d.]+)", line)
    if m:
        t = float(m.group(2))
    m = re.search(r"shell-max crossing.*r = ([\d.]+)", line)
    if m:
        rows.append((t, float(m.group(1)), arm))
rows.sort()
with open(dst, "w", encoding="utf-8") as out:
    out.write("# Offline apparent-horizon radius of the merged core.\n")
    out.write("# Theta = 0 crossing of the outermost FULLY trapped coordinate sphere\n")
    out.write("# (shell-maximum convention -- the same test the in-code scan applies).\n")
    out.write("# Produced by grteclyn-wrapper/scripts/validation/ah_radial_scan.py.\n")
    out.write("# time  r_AH  source_plotfile\n")
    for t, r, arm in rows:
        out.write(f"{t:8.2f}  {r:6.3f}  {arm}\n")
print(f"[pack-merger] horizon: {len(rows)} scans -> horizon_dissolution.dat")
PY
  scrub "${DEST}/horizon/ah_radial_scan_output.txt"
else
  echo "[pack-merger] horizon: keeping the committed scan (PACK_HORIZON=1 to regenerate)"
fi

# ---------------------------------------------------------------------------
# 3. Campaign figures (waveform, constraints, validation checks)
# ---------------------------------------------------------------------------
# PNG and PDF only: the dpi-600 EPS twins are ~39 MB each and add nothing the
# PDF does not carry.
FIGS="${RUNS}/merger_fix/plots"
if [[ -d "${FIGS}" ]]; then
  mkdir -p "${DEST}/figures"
  find "${FIGS}" -maxdepth 1 \( -name "*.png" -o -name "*.pdf" \) \
    -exec cp -p {} "${DEST}/figures/" \;
  echo "[pack-merger] figures: $(ls "${DEST}/figures" | wc -l) files"
else
  echo "[pack-merger] figures: no ${FIGS#"${ROOT}"/} -- skipped"
fi

# ---------------------------------------------------------------------------
# 4. Derived summary table over the packed streams
# ---------------------------------------------------------------------------
"${PY_BIN}" "${DEST}/analysis/make_summary.py" "${DEST}"

echo "[pack-merger] total size: $(du -sh "${DEST}" | cut -f1)"
echo "[pack-merger] done"
