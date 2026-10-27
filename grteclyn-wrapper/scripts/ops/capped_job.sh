#!/usr/bin/env bash
# Capped, trackable background jobs for CPU-heavy work (sympy, JAX-on-CPU).
#
# Every job runs in its own session (setsid) with thread caps, an address-space
# cap (ulimit -v), nice, and a hard timeout, so a runaway cannot take out the
# node container (memory.oom.group=1: one OOM kills every process in it).
# State lives under <repo>/runs/capped_jobs/<name>/: job.sh, log, pid, pgid,
# exit_code. Nothing is left running after stop/timeout: the whole process
# group is signalled and status reports any survivor.
#
# Usage:
#   capped_job.sh start <name> [--threads N] [--mem GB] [--timeout S] [--gpu] \
#                        [--cwd DIR] -- <command ...>
#   capped_job.sh status [<name>]
#   capped_job.sh tail <name> [lines]
#   capped_job.sh stop <name>
#
# Defaults: 4 threads, 8 GB, 7200 s, JAX_PLATFORMS=cpu, cwd = repo root.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
JOB_ROOT="${REPO_ROOT}/runs/capped_jobs"

die() { echo "capped_job: $*" >&2; exit 1; }

job_dir() { echo "${JOB_ROOT}/$1"; }

# Live process group? Prints the pgid if anything in it survives.
live_pgid() {
    local dir="$1" pgid
    [[ -f "${dir}/pgid" ]] || return 1
    pgid="$(cat "${dir}/pgid")"
    if kill -0 -- "-${pgid}" 2>/dev/null; then
        echo "${pgid}"
        return 0
    fi
    return 1
}

cmd_start() {
    local name="$1"; shift
    local threads=4 mem_gb=8 timeout_s=7200 use_gpu=0 cwd="${REPO_ROOT}"
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --threads) threads="$2"; shift 2 ;;
            --mem)     mem_gb="$2";  shift 2 ;;
            --timeout) timeout_s="$2"; shift 2 ;;
            --gpu)     use_gpu=1; shift ;;
            --cwd)     cwd="$(cd "$2" && pwd)" || die "bad --cwd"; shift 2 ;;
            --)        shift; break ;;
            *) die "unknown option '$1' (need '--' before the command)" ;;
        esac
    done
    [[ $# -gt 0 ]] || die "no command given after '--'"
    [[ "${name}" =~ ^[A-Za-z0-9._-]+$ ]] || die "bad job name '${name}'"

    local dir; dir="$(job_dir "${name}")"
    if pgid="$(live_pgid "${dir}")"; then
        die "job '${name}' already running (pgid ${pgid}); stop it first"
    fi
    mkdir -p "${dir}"
    rm -f "${dir}/exit_code" "${dir}/pgid" "${dir}/pid"

    # The wrapper the job session runs: caps, then the command, then the exit
    # code to a file so status can tell DONE from killed.
    {
        printf '#!/usr/bin/env bash\n'
        printf 'cd %q || exit 97\n' "${cwd}"
        printf 'ulimit -v %d\n' "$(( mem_gb * 1024 * 1024 ))"
        printf 'export OMP_NUM_THREADS=%d OPENBLAS_NUM_THREADS=%d MKL_NUM_THREADS=%d\n' \
            "${threads}" "${threads}" "${threads}"
        printf 'export NUMEXPR_NUM_THREADS=%d VECLIB_MAXIMUM_THREADS=%d\n' \
            "${threads}" "${threads}"
        printf 'export XLA_FLAGS="--xla_force_host_platform_device_count=1 --xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads=%d"\n' \
            "${threads}"
        if [[ "${use_gpu}" -eq 0 ]]; then
            printf 'export JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES=""\n'
        fi
        printf 'echo "[capped_job] start $(date -u +%%FT%%TZ) threads=%d mem=%dG timeout=%ds"\n' \
            "${threads}" "${mem_gb}" "${timeout_s}"
        printf 'timeout --signal=TERM --kill-after=30 %d %s\n' "${timeout_s}" \
            "$(printf '%q ' "$@")"
        printf 'code=$?\n'
        printf 'echo "[capped_job] end $(date -u +%%FT%%TZ) exit=$code"\n'
        printf 'echo "$code" > %q\n' "${dir}/exit_code"
    } > "${dir}/job.sh"
    chmod +x "${dir}/job.sh"
    printf '%s\n' "$*" > "${dir}/cmd"

    setsid nohup nice -n 10 bash "${dir}/job.sh" > "${dir}/log" 2>&1 < /dev/null &
    local pid=$!
    echo "${pid}" > "${dir}/pid"
    echo "${pid}" > "${dir}/pgid"   # setsid: the child leads its own group = its pid
    disown "${pid}" 2>/dev/null || true
    echo "started '${name}' pid=${pid} log=${dir}/log"
}

status_one() {
    local dir="$1" name state code="" pgid=""
    name="$(basename "${dir}")"
    if pgid="$(live_pgid "${dir}")"; then
        if [[ -f "${dir}/exit_code" ]]; then
            state="LEFTOVER(pgid ${pgid})"   # finished but something survives
        else
            state="RUNNING(pgid ${pgid})"
        fi
    elif [[ -f "${dir}/exit_code" ]]; then
        code="$(cat "${dir}/exit_code")"
        case "${code}" in
            0)   state="DONE" ;;
            124) state="TIMEOUT" ;;
            137) state="KILLED" ;;
            *)   state="FAILED(${code})" ;;
        esac
    else
        state="DEAD(no exit code)"
    fi
    printf '%-28s %-18s %s\n' "${name}" "${state}" \
        "$(tail -c 300 "${dir}/log" 2>/dev/null | tail -n 1)"
    if [[ "${state}" == LEFTOVER* || "${state}" == RUNNING* ]]; then
        ps -o pid=,etime=,rss=,args= -g "${pgid}" 2>/dev/null \
            | sed 's/^/    /' | cut -c1-160
    fi
}

cmd_status() {
    [[ -d "${JOB_ROOT}" ]] || { echo "no jobs"; return 0; }
    if [[ $# -ge 1 ]]; then
        [[ -d "$(job_dir "$1")" ]] || die "no job '$1'"
        status_one "$(job_dir "$1")"
    else
        local d
        for d in "${JOB_ROOT}"/*/; do
            [[ -d "${d}" ]] && status_one "${d%/}"
        done
    fi
}

cmd_tail() {
    local dir; dir="$(job_dir "$1")"
    [[ -f "${dir}/log" ]] || die "no log for '$1'"
    tail -n "${2:-40}" "${dir}/log"
}

cmd_stop() {
    local dir pgid; dir="$(job_dir "$1")"
    [[ -d "${dir}" ]] || die "no job '$1'"
    if ! pgid="$(live_pgid "${dir}")"; then
        echo "'$1' not running"
        return 0
    fi
    kill -TERM -- "-${pgid}" 2>/dev/null
    for _ in $(seq 1 20); do
        kill -0 -- "-${pgid}" 2>/dev/null || { echo "'$1' stopped"; return 0; }
        sleep 0.5
    done
    kill -KILL -- "-${pgid}" 2>/dev/null
    sleep 0.5
    if kill -0 -- "-${pgid}" 2>/dev/null; then
        die "'$1': process group ${pgid} survived SIGKILL"
    fi
    echo "'$1' killed"
}

[[ $# -ge 1 ]] || die "usage: capped_job.sh start|status|tail|stop ..."
action="$1"; shift
case "${action}" in
    start)  [[ $# -ge 1 ]] || die "start needs a name"; cmd_start "$@" ;;
    status) cmd_status "$@" ;;
    tail)   [[ $# -ge 1 ]] || die "tail needs a name"; cmd_tail "$@" ;;
    stop)   [[ $# -ge 1 ]] || die "stop needs a name"; cmd_stop "$@" ;;
    *) die "unknown action '${action}'" ;;
esac
