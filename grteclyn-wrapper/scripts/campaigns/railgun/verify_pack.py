#!/usr/bin/env python3
"""Inventory the portable railgun package and verify immutable study archives."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root):
    unexpected={p.name for p in root.iterdir()}-{'README.md','figures','reports','studies'}
    if unexpected:raise ValueError(f'unclassified package entries: {sorted(unexpected)}')
    for path in (root/'figures').rglob('*'):
        if path.is_dir() or path == root/'figures/README.md':
            continue
        if path.suffix.lower() not in ('.png','.svg','.pdf','.jpg','.jpeg','.webp'):
            raise ValueError(f'non-figure in figures/: {path.relative_to(root)}')
    for checksum in (root/'studies').rglob('sha256sums.txt'):
        for line in checksum.read_text().splitlines():
            expected,name=line.split('  ',1)
            if digest(checksum.parent/name)!=expected:raise ValueError(f'changed study artifact: {checksum.parent.name}/{name}')
    for checksum in (root/'studies').rglob('sha256.json'):
        for name,expected in json.loads(checksum.read_text()).items():
            if digest(checksum.parent/name)!=expected:raise ValueError(f'changed study artifact: {checksum.parent.name}/{name}')
    manifest=root/'reports/package_manifest.json'
    return {str(p.relative_to(root)):dict(sha256=digest(p),bytes=p.stat().st_size)
            for p in sorted(root.rglob('*')) if p.is_file() and p!=manifest}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='refresh the package inventory after reviewed changes')
    args=parser.parse_args();root=Path(__file__).resolve().parents[4]/'results/railgun'
    actual=inventory(root);path=root/'reports/package_manifest.json'
    if args.write:path.write_text(json.dumps(dict(schema=1,files=actual),indent=2)+'\n')
    elif actual!=json.loads(path.read_text())['files']:
        raise ValueError('package inventory changed; review and refresh with --write')
    print(f'Verified {len(actual)} files and all per-study checksums; figures/reports/studies layout is clean.')


if __name__=='__main__':main()
