"""Group finished raw studies without changing their saved contents.

Preview by default; --apply performs same-filesystem renames. Evolution paths
stay fixed. Run only after checking that no job uses the studies being moved.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


GROUPS = {
    "spherical/": ("spherical-pilot", "spherical-refined"),
    "single-ring/construction/": ("spherical-to-ring", "single-pilot"),
    "single-ring/profiles/": ("ring-profile", "strong-profile", "single-axis"),
    "single-ring/scans/": ("compactness", "frequency-"),
    "two-rings/separated/": ("annular-",),
    "two-rings/overlapping/": ("counter-rotation",),
    "two-rings/seeds/": ("branch-seeds",),
    "particles/single-ring/": (
        "ring-transit", "uphill", "strong-uphill", "strong-axis-audit",
        "strong-phase-polish", "single-tracks",
    ),
    "particles/two-rings/": ("annular-transit",),
}
ROOT_ITEMS = {
    "evolution", "spherical", "single-ring", "two-rings", "particles",
    "checks", "logs", "manifests", "README.md", "NODES.local.md",
}


def plan(root: Path) -> list[tuple[Path, Path]]:
    moves = []
    for source in sorted(root.iterdir()):
        if source.name in ROOT_ITEMS:
            continue
        if source.is_symlink():
            raise ValueError(f"Inspect symlink before moving: {source}")
        if source.is_file() and source.suffix in {".xml", ".log"}:
            group = "checks" if source.suffix == ".xml" else "logs"
        elif source.is_dir():
            # The transport directory is a more specific match than annular-*.
            matches = [
                (len(prefix), group)
                for group, prefixes in GROUPS.items()
                for prefix in prefixes if source.name.startswith(prefix)
            ]
            if not matches:
                raise ValueError(f"No group defined for {source}")
            group = max(matches)[1]
        else:
            raise ValueError(f"No group defined for {source}")
        target = root / group / source.name
        if target.exists() or target.is_symlink():
            raise ValueError(f"Destination already exists: {target}")
        moves.append((source, target))
    return moves


def inventory(path: Path) -> dict:
    entries = [path] if path.is_file() else sorted(path.rglob("*"))
    result = {}
    for entry in entries:
        if entry.is_symlink():
            raise ValueError(f"Inspect symlink before moving: {entry}")
        name = "." if entry == path else entry.relative_to(path).as_posix()
        if entry.is_dir():
            result[name] = {"directory": True}
        else:
            digest = hashlib.sha256()
            with entry.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
            result[name] = {"bytes": entry.stat().st_size,
                            "sha256": digest.hexdigest()}
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?", default=Path("runs/railgun"))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    moves = plan(args.root)
    for source, target in moves:
        print(f"{source.relative_to(args.root)} -> {target.relative_to(args.root)}")
    print(f"{len(moves)} entries; evolution/ stays in place")
    if not args.apply or not moves:
        return
    # Hash all sources before the first rename, then verify each destination.
    records = [
        {"old": str(source.relative_to(args.root)),
         "new": str(target.relative_to(args.root)),
         "contents": inventory(source)}
        for source, target in moves
    ]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    manifest = args.root / "manifests" / f"layout-{stamp}.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    report = {"created_utc": stamp, "stage": "planned", "moves": records}
    manifest.write_text(json.dumps(report, indent=2) + "\n")
    for (source, target), record in zip(moves, records):
        target.parent.mkdir(parents=True, exist_ok=True)
        source.rename(target)
        if inventory(target) != record["contents"]:
            raise RuntimeError(f"Content changed during move: {target}; see {manifest}")
    report["stage"] = "verified"
    manifest.write_text(json.dumps(report, indent=2) + "\n")
    readme = args.root / "README.md"
    if not readme.exists():
        readme.write_text(
            "# Raw ring studies\n\n"
            "- [Spherical reference runs](spherical/)\n"
            "- [Single rings](single-ring/): construction, profiles, scans\n"
            "- [Two rings](two-rings/): separated, overlapping, seeds\n"
            "- [Particle experiments](particles/): single-ring, two-rings\n"
            "- [3+1 evolutions and movies](evolution/): pilot, long\n"
            "- [Test reports](checks/)\n"
            "- [Transfer and push logs](logs/)\n"
            "- [Old-to-new paths and file checksums](manifests/)\n\n"
            "Evolution paths remain unchanged. Saved historical logs and JSONs "
            "retain their original paths; consult the layout manifest to locate "
            "moved files. New runs belong in the matching study subfolder. "
            "Verified portable archives are in results/railgun/.\n"
        )
    print(f"Verified all moved contents; mapping: {manifest}")


if __name__ == "__main__":
    main()
