# The claims ledger

Every number `research.tex` quotes is one row in a `ledger_<area>.tsv` here
(areas: `single`, `mergers`, `waves`, `detector`), and reaches the text as a
`\clm...` macro defined in the generated `../numbers.tex`.  Measured numbers
carry an extractor that recomputes them from the tracked pack
(`results/merger/campaign/`), so the audit is a command:

```bash
cd research/merger/article
PY=../../../grteclyn-wrapper/.venv/bin/python
$PY claims/claims.py check            # recompute every auto/def row; exit 1 on any mismatch
$PY claims/claims.py tex              # regenerate ../numbers.tex from the ledger
$PY claims/claims.py apply --dry-run  # which anchored numbers in research.tex are not yet macros
$PY claims/claims.py coverage         # how much of the text still carries bare numbers
```

Row format and statuses: `claims.py --help` (module docstring).  Generic
extractors are in `lib.py`; each area adds its own in `extract_<area>.py`.

To change a number: fix the data or the analysis, update the row's `tex`/`num`,
run `check`, then `tex`.  Never edit `numbers.tex` by hand.  A `manual` row is a
number the pack cannot reproduce; its `source` says where it comes from, and it
is a candidate for packing whatever it was computed from.

State on 2026-09-24: 852 rows, 773 recomputed, all agree (`check` exits 0).
The first build found 27 numbers and about twenty statements the data
contradicted; [`FINDINGS.md`](FINDINGS.md) lists them with the fix each got,
and what is still open.  `table1_groups.tsv` maps every packed run to its Table I group, so
the table's counts are recomputed too.  Rows needing the wrapper's figure code
(and pycbc for the detector rows) run under `grteclyn-wrapper/.venv`.
