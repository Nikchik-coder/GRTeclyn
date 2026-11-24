# EPJ C submission files

Prepared 24 November 2026 for *Rotation slows the instability of
Ellis-Bronnikov wormholes*, Nikita M. Shirokov and Ilya Nachevsky.

## ScholarOne Step 2

1. Upload `manuscript.pdf` as **Main Document**.
2. Upload `epjc_source.zip` as **Suppl File not for Review**.
3. Leave **Extract files on upload** unchecked.
4. Enter **2610.29941**, without a version suffix, in the required arXiv-number field.
5. Leave the alternative **arXiv File Upload** importer unused; the manual uploads
   already provide the PDF and complete source.
6. Click **Upload Selected Files**, inspect the uploaded PDF, then **Save & Continue**.

This folder is a prepared submission package; preparation does not confirm receipt
or submission by the journal.

## Contents and provenance

- `manuscript.pdf`: 12-page journal manuscript, compiled with pdfLaTeX.
- `epjc_source.zip`: `research.tex`, all six external figure PDFs, and `BUILD.txt`.
  The seventh figure is drawn with TikZ in the LaTeX source; the bibliography is inline.
- `source/`: the exact source included in the ZIP.
- `SHA256SUMS`: checksums of the two upload files.
- `.build/`: local build logs, page renders and comparison files; excluded from Git.

The source retains the scientific results, title and abstract, and the existing
funding, competing-interest and contribution declarations from the GRG submission
package. The displayed date is 24 November 2026. The title and abstract match the
canonical article and the Step 1 text.

At Step 5, the author confirmed that Claude Code assisted with scientific software
development. A disclosure was added to Section VII, alongside the existing numerical
validation methods, and the availability heading explicitly names both data and code.
These changes require replacing BOTH files previously uploaded at Step 2. The current
`manuscript.pdf` and `epjc_source.zip` include the disclosure; the earlier files are
retained only as local backups in `.build/`.

The existing plots contained embedded Type 3 fonts. Their lettering was converted
to vector outlines with Ghostscript, preserving the vector graphics and page sizes.
The underlying scientific data and plotting scripts were not changed. The journal
PDF now contains 29 embedded font entries, all Type 1. Use pdfLaTeX to reproduce this
font configuration; LuaLaTeX also builds, but its output is not the upload PDF.

## Validation

- pdfLaTeX and LuaLaTeX both compile without undefined references/citations,
  missing glyphs or overfull boxes.
- All 12 rendered pages and all six external figures were inspected visually.
- The converted figures retain their original dimensions; small raster differences
  arise from rendering their vector outlines.
- The ZIP was extracted and compiled independently. Its extracted PDF text and
  complete font inventory match the supplied PDF.
- Existing REVTeX float-placement warnings remain; all figures and tables appear
  in the inspected 12-page output.

[EPJ C submission guidelines](https://link.springer.com/journal/10052/submission-guidelines)
recommend the Springer template but explicitly accommodate other LaTeX formats.
This package retains the existing two-column REVTeX layout.
[arXiv record](https://arxiv.org/abs/2610.29941).
