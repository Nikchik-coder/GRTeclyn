"""Source identity that also works outside a Git checkout."""
from pathlib import Path
import subprocess


def source_revision() -> str | None:
    """Return the solver checkout's revision, never a calling project's HEAD.

    Installed distributions have no Git revision. Their source hashes still
    identify the implementation used in a saved result or resume certificate.
    """
    package = Path(__file__).resolve().parent
    # Wheels installed in another project's .venv must not claim that project's
    # revision as their own. Only the source layout can carry a checkout revision.
    project = package.parent.parent
    if package.parent.name != 'src' or not (project / 'pyproject.toml').is_file():
        return None
    root = next((p for p in package.parents if (p / '.git').exists()), None)
    if root is None:
        return None
    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=root,
                                capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None
