#!/usr/bin/env python3
"""Commit-message gate: a subject a log can show, detail in the body.

The branch's history had become the lab notebook: in the last 200 commits the
median subject was 109 characters and the longest 2 089, so `git log --oneline`
showed nothing and every search went through prose.  The rule is the usual one:

  * subject (first line) at most 72 characters, not empty;
  * if there is a body, a blank line between subject and body;
  * no "Co-Authored-By: Claude" / anthropic.com trailers (repo convention).

The detail still belongs in the body, and the running narrative in
research/merger/GPU_PLAN.md -- the gate only keeps the first line readable.

Usage:
    check_commit_msg.py <message-file>     # the commit-msg hook
    check_commit_msg.py --install-hook     # wire it up as .git/hooks/commit-msg

Merge, revert, fixup! and squash! messages git writes itself are let through.
Exit status 0 accept, 1 reject.  Like check_machine_paths.py, the hook lives in
.git/hooks/ (untracked): rerun --install-hook after cloning.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

MAX_SUBJECT = 72
REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
AGENT_TRAILER = re.compile(r"^co-authored-by:.*(claude|anthropic\.com)", re.I | re.M)
GIT_WRITTEN = re.compile(r"^(Merge |Revert \"|fixup! |squash! |amend! )")


def check(message: str) -> list[str]:
    lines = [l for l in message.splitlines() if not l.startswith("#")]
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines:
        return ["empty commit message"]
    subject = lines[0]
    if GIT_WRITTEN.match(subject):
        return []
    problems = []
    if len(subject) > MAX_SUBJECT:
        problems.append(f"subject is {len(subject)} characters (max {MAX_SUBJECT}); "
                        "move the detail into the body")
    if len(lines) > 1 and lines[1].strip():
        problems.append("leave a blank line between the subject and the body")
    if AGENT_TRAILER.search(message):
        problems.append("no Claude / anthropic.com co-author trailers in this repo")
    return problems


def install_hook() -> int:
    git_dir = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "--git-dir"],
                             capture_output=True, text=True, check=True).stdout.strip()
    hook = (REPO_ROOT / git_dir / "hooks" / "commit-msg").resolve()
    hook.write_text("#!/usr/bin/env bash\n"
                    "# Installed by grteclyn-wrapper/scripts/ops/check_commit_msg.py\n"
                    'exec python3 "$(git rev-parse --show-toplevel)/grteclyn-wrapper/scripts/ops/'
                    'check_commit_msg.py" "$1"\n', encoding="utf-8")
    hook.chmod(0o755)
    print(f"installed {hook}")
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--install-hook"]:
        return install_hook()
    if len(argv) != 1:
        print(__doc__)
        return 1
    problems = check(pathlib.Path(argv[0]).read_text(encoding="utf-8", errors="replace"))
    for p in problems:
        print(f"[commit-msg] {p}", file=sys.stderr)
    if problems:
        print("[commit-msg] commit refused (git commit --no-verify skips the gate)", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
