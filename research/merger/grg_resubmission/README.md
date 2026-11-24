# GRG resubmission package

Prepared 24 November 2026 for *Binary Ellis-Bronnikov wormholes in 3+1
numerical relativity: mergers, fly-bys and gravitational waves*.
Preparation does not confirm submission or receipt by the journal.

## Upload files

- `manuscript.pdf`: 23-page manuscript, compiled with pdfLaTeX.
- `source.zip`: matching LaTeX source, numerical macros and all 14 figure PDFs.
- `cover_letter.pdf`: one-page letter explaining the earlier GRG withdrawal
  and the revised submission. `cover_letter.txt` is available for pasting.
- `supplementary_movies.zip`: the 12 videos and README from the arXiv v2
  ancillary files. The manuscript already contains the corresponding links.
- `submission_details.txt`: title, abstract, keywords and other form details.
- `SHA256SUMS`: checksums of the four upload files.

Use these files for the new submission, rather than the older files in
`../grg_submission/`. Author contributions must be entered from the actual
roles in the journal form; none have been inferred here.

## Source and changes

The source comes from `../arxiv_submission/merger_arxiv_v2.tar.gz`; its
`research.tex` matches `../article/research.tex` before packaging edits.
The scientific results, figures and numerical macros are retained from v2.
Changes for this submission are the displayed date, five visible keywords,
the Statements and Declarations heading, a self-contained figure path and
the Claude Code (Anthropic) scientific-software disclosure on page 18.
Use of Claude Code for this paper was confirmed by the author.

The original v2 package and canonical article were not overwritten.
`source/BUILD.txt` contains compilation instructions. The ZIP places
`research.tex` at its root, with the figures under `figures/`.

## Checks performed

- pdfLaTeX and LuaLaTeX both compile to 23 pages.
- No undefined references or citations, missing characters or overfull boxes.
- All pages were rendered for layout inspection; the disclosure and cover
  letter were inspected separately.
- An independent extraction of `source.zip` compiles and reproduces the
  upload PDF's complete extracted text.
- Existing REVTeX float-placement and PDF-bookmark warnings remain; all
  figures are present in the rendered output.

This is a packaging check, not a new validation of the scientific results.
The unresolved effect of the Weyl matter-coupling correction on the published
waveforms and radiated energies remains documented in
`../../../results/software-validation/upstream-evolution-20261112/README.md`.
That issue was reported before the author instructed preparation of this
submission from the existing results.
