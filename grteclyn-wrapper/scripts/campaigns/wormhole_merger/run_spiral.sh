#!/usr/bin/env bash
# BinaryWormholeMerger -- spiral/orbit entry point (Plan.md Stage 2.5).
#
# Thin front-end over run_single.sh ("single" = one run at a time, not one
# wormhole): sets the two-throat orbit defaults and delegates, so the 400
# lines of launcher logic (path rewrites, consumer sidecar, stop handle,
# WHM_RESTART) live in exactly one place.  Every WHM_* override still works
# and still wins over the defaults below.
#
# Usage (attached, foreground -- detach only with explicit permission):
#   bash scripts/campaigns/wormhole_merger/run_spiral.sh
# Typical restart test, once a checkpoint exists:
#   WHM_RESTART=/tmp/grteclyn_scratch/orbit_d12_p012/BinaryWormholeChk02000 \
#     bash scripts/campaigns/wormhole_merger/run_spiral.sh
set -euo pipefail
SPIRAL_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

export WHM_PARAMS="${WHM_PARAMS:-params_orbit_drainhole.txt}"
export WHM_NAME="${WHM_NAME:-orbit_d12_p012}"

# The orbit lives in the x-y plane at z = 32.  --frames-coord is NOT
# optional: the consumer's default slice coordinate is 0 -- the DOMAIN
# BOUNDARY, 30 units below the throats -- and nothing errors when the slice
# misses the physics; you just get featureless far-field frames (measured
# 2026-08-31 on this run's first two plotfiles).  Zoom is the full window
# width: 32 shows +/-16 around centre, holding the whole d = 12 orbit with
# margin.  Cache the slices so the colours can be re-fixed over the finished
# series (the live watcher locks them from the first plotfile, which
# under-ranges any growing field).
export WHM_CONSUME_ARGS="${WHM_CONSUME_ARGS:---frames-fields chi K lapse phi --frames-coord 32.0 --frames-zoom 32 --frames-cache-slices}"

# K grows ~30x over an inspiral (2.5e-3 at t=2.5 vs ~0.08 at collapse), so any
# fixed colour scale hides one end of the run: locked at merger amplitude the
# whole inspiral renders blank white (measured 2026-08-31, frames 0-300).
# Per-frame scaling keeps the structure visible and prints the growing scale
# on the colourbar; the paper movie can re-fix it later from the slice cache.
export GRTECLYN_FRAMES_PER_FRAME_ZLIM="${GRTECLYN_FRAMES_PER_FRAME_ZLIM:-K}"

exec bash "${SPIRAL_DIR}/run_single.sh"
