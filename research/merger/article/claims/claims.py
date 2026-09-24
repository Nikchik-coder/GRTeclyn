#!/usr/bin/env python3
"""The claims ledger: every number the article quotes, where it comes from,
and a check that it still matches the data.

    claims.py check [--area A] [--id ID] [--stamp] [-v]   recompute and compare
    claims.py tex                                         write ../numbers.tex
    claims.py apply [--dry-run]                           numbers in research.tex -> macros
    claims.py coverage [--top N]                          what is still a bare number
    claims.py list [--area A]

WHY.  The 2026-09-23 audit re-derived the article's numbers by hand: eight
agents, ~400 shell calls, about ten numbers with no findable source and
several quoted before their run had finished.  Here each number is one ledger
row: the text it prints as, a macro name, and -- for measured numbers -- the
extractor that recomputes it from the tracked pack.  `check` is then the audit,
in seconds, and `tex` writes numbers.tex, which the article \\inputs, so the
paper prints exactly what the ledger holds.

THE LEDGER is every ledger_<area>.tsv in this directory (one per article area,
so areas can be edited independently).  Tab-separated, header line first:

  id         macro name, "clm" + letters (TeX names cannot hold digits)
  tex        exactly what the article prints (LaTeX allowed, e.g. 4.3\\times10^{-2})
  num        the same number as a float, for comparison ("" if not numeric)
  tol        print (default: the recomputed value must round to the printed digits)
             | rel:X | abs:X
  status     auto  -- recomputed by the extractor (measured numbers)
             def   -- a setup parameter, read back from a run's params (also recomputed)
             manual -- not recomputable from the pack; `source` says where it comes from
             lit   -- a literature or external value; `source` gives the reference
  extractor  registered function name (lib.py, extract_<area>.py)
  args       JSON keyword arguments for it
  anchors    where it sits in research.tex: exact unique substrings containing `tex`,
             separated by " || " (the abstract and the body may both quote it)
  source     human pointer: pack path, script, reference
  checked    date of the last passing check (check --stamp writes it)
  note

Run with any Python that has numpy (grteclyn-wrapper/.venv/bin/python).
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import importlib.util
import json
import math
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ARTICLE = HERE.parent
TEX = ARTICLE / "research.tex"
NUMBERS = ARTICLE / "numbers.tex"
COLUMNS = ["id", "tex", "num", "tol", "status", "extractor", "args", "anchors",
           "source", "checked", "note"]
STATUSES = {"auto", "def", "manual", "lit"}
ID_RE = re.compile(r"^clm[A-Z][A-Za-z]*$")

sys.path.insert(0, str(HERE))
import lib  # noqa: E402

for mod in sorted(HERE.glob("extract_*.py")):
    spec = importlib.util.spec_from_file_location(mod.stem, mod)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


# ---------------------------------------------------------------- ledger
def load(area: str | None = None) -> list[dict]:
    rows, seen = [], {}
    for path in sorted(HERE.glob("ledger_*.tsv")):
        a = path.stem.removeprefix("ledger_")
        if area and a != area:
            continue
        with path.open(encoding="utf-8", newline="") as fh:
            reader = csv.DictReader((l for l in fh if l.strip() and not l.startswith("#")),
                                    delimiter="\t", quoting=csv.QUOTE_NONE)
            for n, row in enumerate(reader, start=2):
                row = {k: (row.get(k) or "").strip() for k in COLUMNS}
                row["area"], row["file"], row["line"] = a, path.name, n
                problems = validate(row)
                if row["id"] in seen:
                    problems.append(f"id also defined in {seen[row['id']]}")
                seen[row["id"]] = path.name
                row["problems"] = problems
                rows.append(row)
    return rows


def validate(row: dict) -> list[str]:
    p = []
    if not ID_RE.match(row["id"]):
        p.append("id must be 'clm' + a capital + letters only")
    if row["status"] not in STATUSES:
        p.append(f"status must be one of {sorted(STATUSES)}")
    if not row["tex"]:
        p.append("tex is empty")
    if row["status"] in ("auto", "def"):
        if row["extractor"] not in lib.EXTRACTORS:
            p.append(f"unknown extractor {row['extractor']!r}")
        try:
            json.loads(row["args"] or "{}")
        except json.JSONDecodeError as e:
            p.append(f"args is not JSON: {e}")
        if not row["num"]:
            p.append("an auto/def row needs num")
    if row["status"] in ("manual", "lit") and not row["source"]:
        p.append("a manual/lit row needs a source")
    if row["num"]:
        try:
            float(row["num"])
        except ValueError:
            p.append("num is not a float")
    return p


def tolerance(row: dict) -> float:
    """Absolute tolerance on |recomputed - num|."""
    tol, num = row["tol"] or "print", row["num"]
    x = float(num)
    if tol.startswith("rel:"):
        return abs(x) * float(tol[4:])
    if tol.startswith("abs:"):
        return float(tol[4:])
    # print: half a unit in the last printed digit of num
    mant, _, exp = num.lower().partition("e")
    decimals = len(mant.split(".")[1]) if "." in mant else 0
    return 0.5 * 10 ** (int(exp or 0) - decimals) * (1 + 1e-9)


# ---------------------------------------------------------------- commands
def cmd_check(a) -> int:
    rows = [r for r in load(a.area) if not a.id or r["id"] == a.id]
    text = TEX.read_text(encoding="utf-8")
    bad = 0
    today = dt.date.today().isoformat()
    passed: set[str] = set()
    for r in rows:
        verdict, got = "", ""
        if r["problems"]:
            verdict = "INVALID: " + "; ".join(r["problems"])
        elif r["status"] in ("auto", "def"):
            try:
                val = lib.EXTRACTORS[r["extractor"]](**json.loads(r["args"] or "{}"))
                got = f"{val:.6g}"
                ok = math.isfinite(val) and abs(val - float(r["num"])) <= tolerance(r)
                verdict = "ok" if ok else f"MISMATCH (tol {tolerance(r):.3g})"
            except Exception as e:  # noqa: BLE001 -- report, do not crash the audit
                verdict = f"ERROR: {type(e).__name__}: {e}"
        else:
            verdict = f"{r['status']} (not recomputed)"
        anchor_note = check_anchors(r, text)
        if anchor_note:
            verdict += f"; anchors: {anchor_note}"
        failed = verdict.startswith(("INVALID", "MISMATCH", "ERROR")) or "anchors:" in verdict
        bad += failed
        if verdict.startswith("ok") and "anchors:" not in verdict:
            passed.add(r["id"])
        if a.verbose or failed:
            print(f"{r['file']}:{r['line']:<4} {r['id']:<28} printed {r['tex']:<22} "
                  f"recomputed {got:<12} {verdict}")
    n_auto = sum(r["status"] in ("auto", "def") for r in rows)
    print(f"[claims] {len(rows)} rows ({n_auto} recomputed, {len(rows) - n_auto} manual/lit): "
          f"{len(passed)} recomputed ok, {bad} problem(s)")
    if a.stamp and passed:
        stamp(passed, today)
    return 1 if bad else 0


def macro_forms(r: dict) -> tuple[str, str]:
    """A macro swallows the space after it and a letter would extend its name,
    so it needs {} before a letter, digit or space -- and must NOT have it
    before ^ or _ (the exponent would attach to the empty group)."""
    return "\\" + r["id"] + "{}", "\\" + r["id"]


def macro_for(r: dict, following: str) -> str:
    braced, bare = macro_forms(r)
    return braced if (not following or following.isalnum() or following.isspace()) else bare


def applied_count(r: dict, anchor: str, text: str) -> int:
    """How many places hold the anchor with its number already a macro.  The
    bare form is a prefix of the braced one when the anchor ends at the number,
    so a bare match followed by "{}" is the braced match, not a second one."""
    braced, bare = (anchor.replace(r["tex"], m, 1) for m in macro_forms(r))
    n_bare = len(re.findall(re.escape(bare) + r"(?!\{\})", text))
    return text.count(braced) + n_bare


def check_anchors(r: dict, text: str) -> str:
    notes = []
    for anchor in filter(None, (s.strip() for s in r["anchors"].split(" || "))):
        n_raw = text.count(anchor)
        n_mac = applied_count(r, anchor, text)
        if r["tex"] not in anchor:
            notes.append(f"anchor {anchor!r} does not contain {r['tex']!r}")
        elif n_raw + n_mac != 1:
            notes.append(f"anchor {anchor!r} found {n_raw + n_mac} times (need exactly 1)")
    return "; ".join(notes)


def stamp(ids: set[str], today: str) -> None:
    for path in sorted(HERE.glob("ledger_*.tsv")):
        lines = path.read_text(encoding="utf-8").splitlines()
        header = None
        out = []
        for line in lines:
            if header is None and line.startswith("id\t"):
                header = line.split("\t")
            elif header and line.strip() and not line.startswith("#"):
                cells = line.split("\t") + [""] * (len(header) - len(line.split("\t")))
                if cells[header.index("id")] in ids:
                    cells[header.index("checked")] = today
                line = "\t".join(cells[: len(header)])
            out.append(line)
        path.write_text("\n".join(out) + "\n", encoding="utf-8")


def cmd_tex(a) -> int:
    rows = load()
    broken = [r for r in rows if r["problems"]]
    if broken:
        for r in broken:
            print(f"{r['file']}:{r['line']} {r['id']}: {'; '.join(r['problems'])}", file=sys.stderr)
        return 1
    out = ["% GENERATED by claims/claims.py tex -- edit the ledger (claims/ledger_*.tsv), not this file.",
           "% Every number the article quotes through a \\clm... macro; `claims.py check` recomputes",
           "% the measured ones from the tracked pack (results/merger).", ""]
    for area in sorted({r["area"] for r in rows}):
        out.append(f"% ---- {area}")
        for r in (r for r in rows if r["area"] == area):
            out.append(f"\\newcommand{{\\{r['id']}}}{{{r['tex']}}}% {r['status']}: {r['source'][:80]}")
        out.append("")
    NUMBERS.write_text("\n".join(out), encoding="utf-8")
    print(f"[claims] wrote {NUMBERS.relative_to(ARTICLE.parents[2])}: {len(rows)} macros")
    return 0


def cmd_apply(a) -> int:
    text = TEX.read_text(encoding="utf-8")
    changed, problems = 0, 0
    for r in load():
        for anchor in filter(None, (s.strip() for s in r["anchors"].split(" || "))):
            if text.count(anchor) == 0 and applied_count(r, anchor, text) == 1:
                continue                                   # already applied
            if r["tex"] not in anchor or text.count(anchor) != 1:
                print(f"[claims] {r['id']}: anchor {anchor!r} not unique/valid -- skipped", file=sys.stderr)
                problems += 1
                continue
            at = text.find(anchor) + anchor.find(r["tex"]) + len(r["tex"])
            macro = macro_for(r, text[at:at + 1])
            text = text.replace(anchor, anchor.replace(r["tex"], macro, 1), 1)
            changed += 1
    if "\\input{numbers}" not in text:
        text = text.replace("\\begin{document}", "\\input{numbers}\n\\begin{document}", 1)
        changed += 1
    used = set(re.findall(r"\\(clm[A-Za-z]+)", text))
    defined = {r["id"] for r in load()}
    undefined = used - defined
    if undefined:
        print(f"[claims] macros used but not in the ledger: {sorted(undefined)}", file=sys.stderr)
        problems += len(undefined)
    if a.dry_run:
        print(f"[claims] dry run: {changed} replacement(s), {problems} problem(s)")
    else:
        TEX.write_text(text, encoding="utf-8")
        print(f"[claims] research.tex: {changed} replacement(s), {problems} problem(s)")
    return 1 if problems else 0


NUM_RE = re.compile(r"(?<![\\A-Za-z0-9.])(\d+(?:\.\d+)?)")
SKIP_RE = re.compile(r"\\(?:ref|eqref|label|cite|includegraphics|input|begin|end|hspace|vspace|"
                     r"clm[A-Za-z]+)\*?(?:\[[^\]]*\])?\{[^}]*\}|[0-9.]+\\(?:textwidth|columnwidth|linewidth)")


def cmd_coverage(a) -> int:
    text = TEX.read_text(encoding="utf-8")
    body = text.split("\\begin{document}", 1)[-1].split("\\begin{thebibliography}", 1)[0]
    macros = len(re.findall(r"\\clm[A-Za-z]+", body))
    per_line = []
    total = 0
    for n, line in enumerate(body.splitlines(), start=text[: text.find(body)].count("\n") + 1):
        stripped = SKIP_RE.sub(" ", re.split(r"(?<!\\)%", line, maxsplit=1)[0])   # \% is text
        nums = NUM_RE.findall(stripped)
        total += len(nums)
        if nums:
            per_line.append((len(nums), n, stripped.strip()[:100]))
    share = macros / (macros + total) if macros + total else 0.0
    print(f"[claims] body: {macros} numbers through ledger macros, {total} bare numerals "
          f"(incl. equation constants and section numbers): {100 * share:.0f}% via the ledger")
    for k, n, s in sorted(per_line, reverse=True)[: a.top]:
        print(f"  line {n:<4} {k:>3} bare  {s}")
    return 0


def cmd_list(a) -> int:
    for r in load(a.area):
        print(f"{r['area']:<10} {r['id']:<28} {r['status']:<6} {r['tex']:<22} {r['source'][:60]}")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--area")
    c.add_argument("--id")
    c.add_argument("--stamp", action="store_true", help="date the passing rows")
    c.add_argument("-v", "--verbose", action="store_true")
    sub.add_parser("tex")
    ap_apply = sub.add_parser("apply")
    ap_apply.add_argument("--dry-run", action="store_true")
    cov = sub.add_parser("coverage")
    cov.add_argument("--top", type=int, default=25)
    ls = sub.add_parser("list")
    ls.add_argument("--area")
    a = ap.parse_args(argv)
    return {"check": cmd_check, "tex": cmd_tex, "apply": cmd_apply,
            "coverage": cmd_coverage, "list": cmd_list}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
