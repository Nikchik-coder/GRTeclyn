#!/usr/bin/env python3
"""Refuse to let machine identity enter git.

``packaging/scrub_paths.py`` already knows how to *rewrite* machine-specific
paths out of a packed artefact.  This is the other half: a **gate** that stops
them being committed in the first place, because a scrubber only helps on files
someone remembered to run it over.

What gets caught, and why each pattern is here:

* **Runtime identity tokens** -- user name, host name, home-directory name, and
  the distinctive segments of ``SIM_ROOT`` / ``CHOMBO_HOME`` / friends.  These
  are derived from the environment at run time by ``scrub_paths._identity_tokens``
  and are deliberately *not* written down anywhere in this file: hard-coding
  "the current machine's name" into a tracked script is the exact leak this
  gate exists to prevent, and it would also stop working on the next machine.
* **Any absolute home-style path**, whoever it belongs to.  A collaborator's
  home directory is machine identity too, and the token scan cannot see it.
* **Agent scratch directories.**  A tool that runs the binary from a scratch
  directory leaves that path inside whatever the binary writes.  This is how
  ``parameters_and_version.txt`` -- which AMReX drops into the *current working
  directory* on every single run, recording the absolute output and plotfile
  paths -- reached a commit on 2026-08-27.

Usage:
    check_machine_paths.py                 # scan what is staged (the hook)
    check_machine_paths.py --all           # audit every tracked file
    check_machine_paths.py --install-hook  # wire it up as .git/hooks/pre-commit

Exit status is the gate: 0 clean, 1 something leaked, 2 could not run.

The hook lives in ``.git/hooks/``, which git does not track, so a fresh clone
starts unguarded -- rerun ``--install-hook`` after cloning, alongside the
``core.fileMode false`` fix the NFS mount needs.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import re
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "grteclyn-wrapper" / "src"))

from grteclyn_wrapper.packaging.scrub_paths import (  # noqa: E402
    BINARY_SUFFIXES,
    _identity_tokens,
)

# Placeholder home paths that documentation is *supposed* to contain.  Anything
# outside this set is a real person's directory.
PLACEHOLDER_HOMES = {"user", "users", "<user>", "youruser", "me", "path"}

# Built at run time for the same reason as in scrub_paths: spelling it out as a
# literal would make this file match its own pattern under --all.
_HOME = "/" + "home" + "/"

# Machine identity leaks through PATHS, not prose.  A host or user name that
# happens to also be a person's name appears legitimately in a paper's funding
# acknowledgement, and flagging that is noise that trains people to pass
# --no-verify.  So an identity token only counts when it sits in a path -- with
# a slash on one side of it -- which is the only form the actual leak takes.
_PATH_L = r"(?:^|[\s\"'=(\[:,])"   # a path may start here
def _patterns() -> list[tuple[str, re.Pattern[str]]]:
    """(label, regex) pairs, most specific first."""
    pats: list[tuple[str, re.Pattern[str]]] = [
        ("agent scratch dir", re.compile(r"/tmp/(?:claude|agent)-[A-Za-z0-9_./-]+")),
        # /home/ must START the path: "/path/to/your/home/x" is a placeholder in
        # documentation, not somebody's actual home directory.
        ("absolute home path", re.compile(rf"(?i){_PATH_L}{_HOME}([^/\s\"'{{}}$]+)")),
    ]
    for token in sorted(_identity_tokens(), key=len, reverse=True):
        esc = re.escape(token)
        pats.append(
            (
                "machine identity in a path",
                re.compile(
                    rf"(?<![A-Za-z0-9_])(?:/{esc}(?![A-Za-z0-9_])"
                    rf"|(?<![A-Za-z0-9_]){esc}/)",
                    re.IGNORECASE,
                ),
            )
        )
    return pats


def _git(*args: str) -> str:
    out = subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=False
    )
    if out.returncode != 0:
        raise SystemExit(f"[paths] git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout


def _staged_files() -> list[str]:
    names = _git("diff", "--cached", "--name-only", "--diff-filter=ACMR")
    return [n for n in names.splitlines() if n]


def _tracked_files() -> list[str]:
    return [n for n in _git("ls-files").splitlines() if n]


def _content(path: str, staged: bool) -> str | None:
    """The bytes that would be committed (staged) or that are tracked (--all)."""
    if pathlib.Path(path).suffix.lower() in BINARY_SUFFIXES:
        return None
    if staged:
        raw = subprocess.run(
            ["git", "show", f":{path}"],
            cwd=REPO_ROOT,
            capture_output=True,
            check=False,
        ).stdout
    else:
        try:
            raw = (REPO_ROOT / path).read_bytes()
        except OSError:
            return None
    if b"\0" in raw:
        return None  # binary
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def scan(paths: list[str], staged: bool) -> list[str]:
    pats = _patterns()
    hits: list[str] = []
    self_rel = str(pathlib.Path(__file__).resolve().relative_to(REPO_ROOT))
    for path in paths:
        if path == self_rel:
            continue  # this file names the patterns; it cannot leak them
        text = _content(path, staged)
        if text is None:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for label, pat in pats:
                m = pat.search(line)
                if not m:
                    continue
                if label == "absolute home path":
                    name = (m.group(1) or "").strip().lower()
                    if name in PLACEHOLDER_HOMES or name.startswith("<"):
                        continue
                hits.append(f"  {path}:{lineno}: {label}: {line.strip()[:120]}")
                break
    return hits


HOOK = """#!/usr/bin/env bash
# Installed by grteclyn-wrapper/scripts/ops/check_machine_paths.py
exec python3 "$(git rev-parse --show-toplevel)/grteclyn-wrapper/scripts/ops/check_machine_paths.py"
"""


def install_hook() -> int:
    hook = REPO_ROOT / ".git" / "hooks" / "pre-commit"
    if hook.exists():
        existing = hook.read_text(encoding="utf-8", errors="replace")
        if "check_machine_paths.py" not in existing:
            print(f"[paths] {hook} already exists and is not ours -- not overwriting.")
            print("[paths] add this line to it yourself:")
            print("  python3 grteclyn-wrapper/scripts/ops/check_machine_paths.py || exit 1")
            return 2
    hook.write_text(HOOK, encoding="utf-8")
    hook.chmod(0o755)
    print(f"[paths] pre-commit hook installed at {hook}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--all", action="store_true", help="audit every tracked file")
    ap.add_argument("--install-hook", action="store_true", help="install pre-commit hook")
    args = ap.parse_args()

    if args.install_hook:
        return install_hook()

    paths = _tracked_files() if args.all else _staged_files()
    if not paths:
        return 0
    hits = scan(paths, staged=not args.all)
    if not hits:
        return 0

    where = "tracked tree" if args.all else "staged changes"
    print(f"[paths] machine identity found in {where} -- commit refused:\n")
    print("\n".join(hits[:40]))
    if len(hits) > 40:
        print(f"  ... and {len(hits) - 40} more")
    print(
        "\n[paths] These are absolute paths or host/user names from this machine.\n"
        "[paths] Usually the file is a run artefact that should be gitignored\n"
        "[paths] (AMReX writes parameters_and_version.txt into the binary's cwd).\n"
        "[paths] To rewrite a file you do want to keep:\n"
        "[paths]   python3 -m grteclyn_wrapper.packaging.scrub_paths <file>\n"
        "[paths] Override once, deliberately, with: git commit --no-verify\n"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
