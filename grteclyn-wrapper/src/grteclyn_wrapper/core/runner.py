from __future__ import annotations

import hashlib
import os
import shlex
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from .config import ExecutableConfig, ExampleConfig, REPO_ROOT, resolve_example
from .episode import Episode, update_metadata
from .plot_consumer import (
    build_consume_command,
    consumer_frames_enabled,
    consumer_jobs_from_env,
    default_radii_for_example,
    post_run_frames_enabled,
)
from .scratch import plotfile_dir


@dataclass(frozen=True)
class RunResult:
    command: list[str]
    returncode: int
    elapsed_seconds: float


def build_command(
    executable: ExecutableConfig,
    params_path: Path,
    *extra_args: str,
    cuda_devices: str | None = None,
) -> list[str]:
    base = [str(executable.path), str(params_path), *extra_args]
    if executable.uses_mpi:
        gpu_ids = [
            token.strip()
            for token in (cuda_devices or "").split(",")
            if token.strip()
        ]
        if gpu_ids:
            if len(gpu_ids) != executable.mpi_ranks:
                raise ValueError(
                    f"MPI ranks ({executable.mpi_ranks}) must match explicit "
                    f"GPU ids ({len(gpu_ids)}): {cuda_devices}"
                )
            wrapper = (
                'IFS="," read -ra _gpus <<< "${GRTECLYN_GPU_IDS}"; '
                'export CUDA_VISIBLE_DEVICES="${_gpus[${OMPI_COMM_WORLD_LOCAL_RANK:-0}]}"; '
                f"exec {shlex.join(base)}"
            )
            return [
                "mpirun",
                "-n",
                str(executable.mpi_ranks),
                "bash",
                "-c",
                wrapper,
            ]
        return ["mpirun", "-n", str(executable.mpi_ranks), *base]
    return base


def _merged_env(cuda_devices: str | None = None, extra_env: Mapping[str, str] | None = None) -> dict[str, str]:
    from .scratch import cache_env
    from .site_paths import grtresna_env_bin, grtresna_env_lib, openmpi_root

    env = dict(os.environ)
    # Matplotlib, uv and pycache otherwise write into $HOME, which is the same
    # shared filesystem the plotfiles just stopped touching.
    env.update(cache_env())
    mpi_root = openmpi_root()
    mpi_bin_dirs = [mpi_root / "bin"]
    mpi_lib_dirs = [mpi_root / "lib"]
    env_bin = grtresna_env_bin()
    env_lib = grtresna_env_lib()
    if env_bin is not None:
        mpi_bin_dirs.append(env_bin)
    if env_lib is not None:
        mpi_lib_dirs.append(env_lib)
    existing_path = env.get("PATH", "")
    existing_ld = env.get("LD_LIBRARY_PATH", "")
    env["PATH"] = os.pathsep.join(
        [str(path) for path in mpi_bin_dirs if path.exists()] + [existing_path]
    )
    env["LD_LIBRARY_PATH"] = os.pathsep.join(
        [str(path) for path in mpi_lib_dirs if path.exists()] + [existing_ld]
    )
    if cuda_devices is not None:
        env["CUDA_VISIBLE_DEVICES"] = cuda_devices
    if extra_env:
        env.update({str(key): str(value) for key, value in extra_env.items()})
    return env


# Process table.  The cards are shared and `ps` / `nvidia-smi` are readable by
# anyone on the node, so with GRTECLYN_PROC_LABEL set (the Bondi launchers set
# it, 2026-10-23) a run takes the merger launcher's neutral names: the
# evolution runs as `<label> params.txt` from the episode directory, from a
# copy of the binary named after the label and its checksum (the GPU process
# list shows the executable's real path, which argv[0] cannot change), and the
# consumer as `<label>_post post.py ...` with episode-relative paths.  The real
# commands still go to the episode's run.log.  Unset: nothing changes.
_CONSUMER_MODULE = "grteclyn_wrapper.visualisation.process_wave.consume_plotfiles"


def _proc_label() -> str | None:
    label = os.environ.get("GRTECLYN_PROC_LABEL", "").strip()
    return label or None


def _neutral_executable(path: Path, label: str) -> Path:
    """The binary's copy ``<label>_<md5[:8]>`` under GRTECLYN_PROC_BIN_DIR.

    run_single.sh names its copy the same way, so both launchers share one
    copy per distinct build and a rebuild never reuses an old copy.
    """
    bin_dir = Path(os.environ.get("GRTECLYN_PROC_BIN_DIR", "/tmp/ml_jobs/bin"))
    bin_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    target = bin_dir / f"{label}_{digest.hexdigest()[:8]}"
    if not os.access(target, os.X_OK):
        part = bin_dir / f"{target.name}.part{os.getpid()}"
        shutil.copyfile(path, part)
        part.chmod(0o755)
        os.replace(part, target)
    return target


def _scratch_alias(episode: Episode) -> Path:
    return episode.path / "scratch"


def _neutral_consumer(
    command: Sequence[str], episode: Episode, label: str
) -> tuple[list[str], str]:
    """argv and executable that run ``command`` as ``<label>_post post.py``.

    python finds its environment through argv[0], so the name is a symlink in
    the venv's own bin directory, which the caller puts first on PATH (as
    run_single.sh does).  The module is entered through a one-line post.py so
    its dotted name stays off the command line, and the plotfiles are reached
    through a ``scratch`` link in the episode directory.
    """
    if list(command[1:3]) != ["-m", _CONSUMER_MODULE]:
        raise ValueError(f"unexpected consumer command: {list(command[:3])}")
    python = Path(command[0])
    link = python.parent / f"{label}_post"
    if not (link.is_symlink() and os.readlink(link) == python.name):
        tmp = python.parent / f".{link.name}.{os.getpid()}"
        tmp.unlink(missing_ok=True)
        tmp.symlink_to(python.name)
        os.replace(tmp, link)
    (episode.path / "post.py").write_text(
        "# written by grteclyn_wrapper.core.runner: entry point for the plotfile consumer\n"
        "import runpy\n"
        f'runpy.run_module("{_CONSUMER_MODULE}", run_name="__main__")\n',
        encoding="utf-8",
    )
    root = episode.path.resolve()
    scratch = plotfile_dir(episode.path).resolve()
    if scratch != root and not _scratch_alias(episode).is_symlink():
        _scratch_alias(episode).symlink_to(scratch)
    args = []
    for arg in command[3:]:
        if arg.startswith("/"):
            resolved = Path(arg).resolve()
            if scratch != root and resolved == scratch:
                arg = "scratch"
            elif resolved == root or root in resolved.parents:
                arg = str(resolved.relative_to(root))
        args.append(arg)
    return [link.name, "post.py", *args], str(link)


def _run_and_tee(
    command: Sequence[str],
    log_path: Path,
    *,
    cwd: Path,
    env: Mapping[str, str] | None = None,
    stop_sim_path: Path | None = None,
    poll_seconds: float = 2.0,
    executable: str | None = None,
) -> RunResult:
    start = time.monotonic()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log:
        real = f"   [executable {executable}, cwd {cwd}]" if executable else ""
        log.write(f"\n$ {' '.join(command)}{real}\n")
        log.flush()
        process = subprocess.Popen(
            list(command),
            executable=executable,
            cwd=cwd,
            env=dict(env) if env is not None else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            start_new_session=True,
        )
        assert process.stdout is not None
        termination_reason: str | None = None
        while True:
            if stop_sim_path is not None and stop_sim_path.is_file():
                termination_reason = stop_sim_path.read_text(encoding="utf-8").strip()
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                break
            line = process.stdout.readline()
            if not line:
                if process.poll() is not None:
                    break
                if stop_sim_path is not None:
                    time.sleep(poll_seconds)
                continue
            log.write(line)
            log.flush()
            print(line, end="")
        returncode = process.wait()
        elapsed = time.monotonic() - start
        log.write(f"\n[wrapper] exit_code={returncode} elapsed_seconds={elapsed:.3f}\n")
        if termination_reason:
            log.write(f"[wrapper] early_termination={termination_reason}\n")

    return RunResult(command=list(command), returncode=returncode, elapsed_seconds=elapsed)


def start_plotfile_consumer(
    episode: Episode,
    *,
    example_name: str = "RadialRecipe",
    radii: Sequence[float] | None = None,
    n_points: int = 64,
    delete: bool = True,
    keep_last: int = 1,
    frames: bool | None = None,
    jobs: int = 1,
    ftl_timeseries: bool = False,
    ftl_L: float | None = None,
    incremental_score: bool = True,
    objective_mode: str = "weighted",
    target_stop_time: float | None = None,
    score_weights: Mapping[str, float] | None = None,
    evolving_geodesic: bool = False,
) -> subprocess.Popen[str]:
    profile = (
        "wormhole"
        if example_name in {"SupportedWormholeCollapse", "RotatingWormholeCollapse"}
        else "radial"
    )
    if radii is None:
        radii = default_radii_for_example(example_name)
    command = build_consume_command(
        episode,
        profile=profile,
        radii=radii,
        n_points=n_points,
        delete=delete,
        keep_last=keep_last,
        watch=True,
        jobs=consumer_jobs_from_env() if jobs == 1 else jobs,
        frames=consumer_frames_enabled() if frames is None else frames,
        ftl_timeseries=ftl_timeseries,
        ftl_L=ftl_L,
        incremental_score=incremental_score,
        objective_mode=objective_mode,
        target_stop_time=target_stop_time,
        score_weights=score_weights,
        evolving_geodesic=evolving_geodesic,
    )

    env = _merged_env(
        extra_env={"GRTECLYN_EVOLVING_GEODESIC": "1"} if evolving_geodesic else None
    )
    log = episode.log_path.open("a", encoding="utf-8")
    log.write(f"\n$ {' '.join(command)}\n")
    executable = None
    cwd = REPO_ROOT
    label = _proc_label()
    if label:
        command, executable = _neutral_consumer(command, episode, label)
        env["PATH"] = os.pathsep.join([str(Path(executable).parent), env.get("PATH", "")])
        cwd = episode.path
        log.write(f"[wrapper] consumer runs as: {' '.join(command)}\n")
    log.flush()
    return subprocess.Popen(
        command,
        executable=executable,
        cwd=cwd,
        stdout=log,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
        env=env,
    )


def stop_process(process: subprocess.Popen[str], timeout: float = 10.0) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=timeout)


def drain_plotfile_backlog(
    episode: Episode,
    *,
    example_name: str = "RadialRecipe",
    radii: Sequence[float] | None = None,
    n_points: int = 64,
    delete: bool = True,
    keep_last: int = 1,
    frames: bool | None = None,
    jobs: int = 1,
    ftl_timeseries: bool = False,
    ftl_L: float | None = None,
    incremental_score: bool = True,
    objective_mode: str = "weighted",
    target_stop_time: float | None = None,
    score_weights: Mapping[str, float] | None = None,
    evolving_geodesic: bool = False,
) -> RunResult:
    """Process any plotfiles left after the watch consumer stops.

    Default (``frames=None``): render PNG frames unless ``GRTECLYN_CONSUMER_DRAIN=1``
    (fast Psi4/metrics-only drain). Pass ``frames=False`` to force a metrics-only pass.
    """
    render_frames = post_run_frames_enabled(explicit=frames)
    profile = (
        "wormhole"
        if example_name in {"SupportedWormholeCollapse", "RotatingWormholeCollapse"}
        else "radial"
    )
    if radii is None:
        radii = default_radii_for_example(example_name)
    command = build_consume_command(
        episode,
        profile=profile,
        radii=radii,
        n_points=n_points,
        delete=delete,
        keep_last=keep_last,
        watch=False,
        jobs=consumer_jobs_from_env() if jobs == 1 else jobs,
        frames=render_frames,
        keep_existing_frames=True,
        stable_seconds=0.0,
        ftl_timeseries=ftl_timeseries,
        ftl_L=ftl_L,
        incremental_score=incremental_score,
        objective_mode=objective_mode,
        target_stop_time=target_stop_time,
        score_weights=score_weights,
        evolving_geodesic=evolving_geodesic,
    )
    label = _proc_label()
    if label:
        command, executable = _neutral_consumer(command, episode, label)
        env = dict(os.environ)
        env["PATH"] = os.pathsep.join([str(Path(executable).parent), env.get("PATH", "")])
        return _run_and_tee(
            command, episode.log_path, cwd=episode.path, env=env, executable=executable
        )
    return _run_and_tee(command, episode.log_path, cwd=REPO_ROOT)


def run_episode(
    episode: Episode,
    executable: ExecutableConfig,
    *,
    check_params: bool = True,
    cuda_devices: str | None = None,
    extra_env: Mapping[str, str] | None = None,
    consume_plotfiles: bool = False,
    consumer_radii: Sequence[float] = (8.0, 16.0),
    consumer_delete: bool = False,
    consumer_keep_last: int = 1,
    consumer_ftl_timeseries: bool = False,
    consumer_ftl_L: float | None = None,
    consumer_incremental_score: bool = True,
    consumer_objective_mode: str = "weighted",
    consumer_target_stop_time: float | None = None,
    consumer_score_weights: Mapping[str, float] | None = None,
    consumer_evolving_geodesic: bool = False,
) -> RunResult:
    example_dir = executable.example.dir
    if not executable.path.exists():
        raise FileNotFoundError(
            f"Executable not found: {executable.path}. Build {executable.example.name} first."
        )

    explicit_mpi_gpus = (
        executable.uses_mpi
        and cuda_devices is not None
        and bool(cuda_devices.strip())
    )
    env = _merged_env(
        cuda_devices=None if explicit_mpi_gpus else cuda_devices,
        extra_env=extra_env,
    )
    if explicit_mpi_gpus:
        env["GRTECLYN_GPU_IDS"] = cuda_devices
    if consumer_evolving_geodesic:
        env["GRTECLYN_EVOLVING_GEODESIC"] = "1"
    # Neutral process table (see _proc_label); single-rank runs only.
    label = None if executable.uses_mpi else _proc_label()
    run_path = str(_neutral_executable(executable.path, label)) if label else None

    def evolution_command(*extra: str) -> tuple[list[str], Path, str | None]:
        if label:
            return [label, episode.params_path.name, *extra], episode.path, run_path
        command = build_command(
            executable, episode.params_path, *extra, cuda_devices=cuda_devices
        )
        return command, example_dir, None

    update_metadata(
        episode,
        {
            "executable": str(executable.path),
            "example": executable.example.name,
            "mpi_ranks": executable.mpi_ranks,
            "cuda_devices": cuda_devices,
            # The plotfiles are not in the episode directory any more, and the
            # scratch name carries a digest that does not invert.  Record it.
            "plotfile_dir": str(plotfile_dir(episode.path)),
            **({"process_executable": run_path} if run_path else {}),
        },
    )

    if check_params:
        check_command, check_cwd, check_exe = evolution_command("check_params=1")
        check_result = _run_and_tee(
            check_command, episode.log_path, cwd=check_cwd, env=env, executable=check_exe
        )
        if check_result.returncode != 0:
            update_metadata(episode, {"check_params_exit_code": check_result.returncode})
            raise RuntimeError(f"check_params failed with exit code {check_result.returncode}")

    consumer = None
    if consume_plotfiles:
        consumer = start_plotfile_consumer(
            episode,
            example_name=executable.example.name,
            radii=consumer_radii,
            delete=consumer_delete,
            keep_last=consumer_keep_last,
            frames=None,
            ftl_timeseries=consumer_ftl_timeseries,
            ftl_L=consumer_ftl_L,
            incremental_score=consumer_incremental_score,
            objective_mode=consumer_objective_mode,
            target_stop_time=consumer_target_stop_time,
            score_weights=consumer_score_weights,
            evolving_geodesic=consumer_evolving_geodesic,
        )

    try:
        command, run_cwd, run_exe = evolution_command()
        stop_sim_path = None
        if os.environ.get("GRTECLYN_SPLASH_EARLY_TERM", "").strip().lower() in {
            "1",
            "on",
            "yes",
            "true",
        }:
            stop_sim_path = episode.path / ".stop_sim"
            if stop_sim_path.exists():
                stop_sim_path.unlink()
        result = _run_and_tee(
            command,
            episode.log_path,
            cwd=run_cwd,
            env=env,
            stop_sim_path=stop_sim_path,
            executable=run_exe,
        )
    finally:
        if consumer is not None:
            stop_process(consumer, timeout=2.0)
            drain_plotfile_backlog(
                episode,
                example_name=executable.example.name,
                radii=consumer_radii,
                delete=consumer_delete,
                keep_last=consumer_keep_last,
                frames=None,
                ftl_timeseries=consumer_ftl_timeseries,
                ftl_L=consumer_ftl_L,
                incremental_score=consumer_incremental_score,
                objective_mode=consumer_objective_mode,
                target_stop_time=consumer_target_stop_time,
                score_weights=consumer_score_weights,
                evolving_geodesic=consumer_evolving_geodesic,
            )
        # The consumer's link to the plotfiles; scratch is purged after the run.
        if _scratch_alias(episode).is_symlink():
            _scratch_alias(episode).unlink()

    update_metadata(
        episode,
        {
            "simulation_exit_code": result.returncode,
            "simulation_elapsed_seconds": result.elapsed_seconds,
            **(
                {
                    "termination_reason": (episode.path / ".stop_sim").read_text(encoding="utf-8").strip(),
                    "early_termination": True,
                }
                if (episode.path / ".stop_sim").is_file()
                else {}
            ),
        },
    )
    return result
