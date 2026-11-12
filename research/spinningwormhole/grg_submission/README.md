# GRG submission package — arXiv layout

Prepared 6 November 2026 for **Rotation slows the instability of Ellis–Bronnikov wormholes**, Nikita M. Shirokov and Ilya Nachevsky.

## Submission status

Submitted to **General Relativity and Gravitation** on **6 November 2026**. The portal confirmed receipt at the
**Technical Check** stage. Tracking details and private correspondence are kept locally in
`../referee/PUBLICATION_STATUS.md`. The instructions below document the files used for this submission.

## Files used

On the Files page, remove the earlier uploaded `grg_source.zip` and upload **`grg_source_arxiv_layout.zip`** as the manuscript. The updated ZIP uses the same REVTeX layout as arXiv. The main source file is `research.tex`; choose **pdfLaTeX** if asked. Figures and tables are included, so separate figure and supplementary uploads can stay empty.

`manuscript.pdf` is the corresponding 12-page preview. Its first nine pages are pixel-identical to the arXiv layout. Only the required Statements and Declarations section was added near the end; the scientific text and numerical results are unchanged.

The local `grg_source.zip` was also updated to the same content. The longer, explicit filename distinguishes the new file from the earlier upload in the portal.

## Remaining submission fields

- Copy the title, abstract, six keywords, author details and declarations from `submission_fields.txt`.
- Enter author contributions and competing interests in the portal even though they are in the manuscript.
- Upload `cover_letter.pdf` when its dedicated field appears, or paste `cover_letter.txt` if the interface asks for text.
- The cover letter says the arXiv replacement is awaiting announcement. If v2 is public by submission, replace that sentence with “The revised preprint is available as arXiv:2610.29941v2.”
- Review the portal-generated PDF and complete the final submission declarations once both authors approve.

The complete package ZIP is a local convenience bundle. Upload the manuscript-source ZIP from inside it, rather than the complete package itself.

## Validation

Both pdfLaTeX and LuaLaTeX compile the manuscript successfully, with no undefined citations/references or overfull boxes. All 12 rendered pages were inspected. Pages 1–9 match the arXiv render pixel for pixel. The source is identical to the canonical arXiv manuscript after allowing for local figure paths, removed comments and the added declarations. The source ZIP was also extracted and compiled independently.

The cover letter is one page and was already checked with both engines and visually. The canonical arXiv manuscript and arXiv upload ZIP are unchanged.

[GRG submission guidelines](https://link.springer.com/journal/10714/submission-guidelines). The Springer Nature template is recommended; this package retains the chosen arXiv layout.
