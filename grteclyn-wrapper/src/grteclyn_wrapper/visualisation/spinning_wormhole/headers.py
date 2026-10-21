#!/usr/bin/env python3
"""The background tables of the article's 3D runs, as their headers in a tracked folder.

A ``.spinbg`` table (``analysis.spinning_wormhole.backgrounds``) is a text
header -- ``SPINBG_V1`` to ``END_HEADER``: the grid, then ``meta <key>
<value>`` lines with the solution's global numbers (J, M_ADM, v_e,
J_over_A_extremal_frac, ...) -- followed by a 12.7 MB binary body.  The
tables live under ``runs/``, which is untracked.  The figures read only the
meta numbers, so ``pack`` copies each table's header verbatim into
``results/spinningwormhole/backgrounds/<stem>.header`` and ``meta`` reads it
back.  ``ARTICLE`` names the tables of the article's 3D runs.

    python -m grteclyn_wrapper.visualisation.spinning_wormhole.headers [<stem> ...]
"""

from __future__ import annotations

import argparse
import pathlib

from grteclyn_wrapper.visualisation.spinning_wormhole.solutions import REPO

SOURCES = (REPO / "runs" / "spinning_wormhole" / "backgrounds", REPO / "runs" / "spinning_p3" / "tables")
HEADERS = REPO / "results" / "spinningwormhole" / "backgrounds"
# the J = 1 model and family (a)'s spin models evolved in 3D
ARTICLE = ("full_eta2_m1_J100", "fam_a_ve030", "fam_a_ve040", "fam_a_ve045",
           "fam_a_ve050", "fam_a_ve060", "fam_a_ve070", "fam_a_ve075",
           "fam_a_ve080", "fam_a_ve090")
MAGIC, END = b"SPINBG_V1\n", b"END_HEADER\n"


def pack(stems=ARTICLE, sources=SOURCES, out: pathlib.Path = HEADERS) -> list[pathlib.Path]:
    """Copy each table's header, through ``END_HEADER``, into ``out/<stem>.header``."""
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for stem in stems:
        table = next((d / f"{stem}.spinbg" for d in sources if (d / f"{stem}.spinbg").is_file()), None)
        if table is None:
            raise SystemExit(f"{stem}.spinbg is under none of " + ", ".join(map(str, sources)))
        with table.open("rb") as fh:
            head = fh.read(1 << 16)
        end = head.find(END)
        if not head.startswith(MAGIC) or end < 0:
            raise SystemExit(f"{table}: no SPINBG_V1 header")
        path = out / f"{stem}.header"
        path.write_bytes(head[:end + len(END)])
        written.append(path)
    return written


def meta(stem: str, headers: pathlib.Path = HEADERS) -> dict[str, str]:
    """A packed header's ``meta <key> <value>`` lines as {key: value}, the first
    line of a repeated key winning (as the tables' readers take it)."""
    path = pathlib.Path(headers) / f"{stem}.header"
    if not path.is_file():
        raise SystemExit(f"{path}: not packed -- run python -m "
                         f"grteclyn_wrapper.visualisation.spinning_wormhole.headers {stem} "
                         "where runs/ holds the table")
    out: dict[str, str] = {}
    for line in path.read_text().splitlines():
        tag, _, rest = line.partition(" ")
        if tag == "meta":
            key, _, value = rest.partition(" ")
            out.setdefault(key, value)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("stems", nargs="*", default=list(ARTICLE),
                    help="table stems, e.g. fam_a_ve030 (default: ARTICLE)")
    ap.add_argument("--out", type=pathlib.Path, default=HEADERS)
    args = ap.parse_args(argv)
    paths = pack(args.stems, out=args.out)
    for path in paths:
        m = meta(path.stem, path.parent)
        print(f"  {path.stem:20s} J {float(m['J']):8.4f}  8 pi J/A "
              f"{100 * float(m['J_over_A_extremal_frac']):5.1f} %  M_ADM {float(m['M_ADM']):.4f}")
    print(f"packed {len(paths)} headers into "
          f"{args.out.relative_to(REPO) if args.out.is_relative_to(REPO) else args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
