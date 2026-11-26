# Grant report: 20 May–20 November 2026

Russian draft for the grant foundation. `report.tex` is the editable source;
`report.pdf` is the compiled, three-page A4 version. The surrounding documentation
is in English, following the author's communication preference.

Build with `make` in this directory. Dependencies: LuaLaTeX, latexmk, Liberation
Serif, and the LaTeX packages named in the preamble. Build files go to `.build/`.
No simulation, GPU job, external data or bibliography database is needed.

The latest layout pass preserves the author's expanded text and restores three
pages from the five-page overflow: 11.5 pt body text, 19 mm side margins and
4.5 pt paragraph spacing. Body text is fully justified with 1.25 cm first-line
indents, including paragraphs after headings; table text remains left-aligned.
The publication table stays with the main results;
arXiv identifiers do not split across lines. The continuing-research table uses
12 pt text to keep its longer descriptions readable and balance the final page.
This pass changes typography and pagination only, not scientific claims or
the author's computing-time figure.

## Scope and editorial choices

- The reporting interval is 20 May–20 November 2026, as specified by the author.
  The grant number, foundation name and signature fields were not supplied.
  Add them if required by the foundation's form.
- Research is organised into two tables: published preprints with arXiv links,
  brief results and journal status; and other research with completed results,
  current status and continuing work. The software workflow remains in prose.
- The 26 November language revision follows the supplied editorial feedback.
  The earlier two-page limit was lifted: software, main results with publications,
  and continuing research each have their own page. The rewrite replaces literal
  translations and repeated openings, adds the binary-wormhole result to the
  main findings, and uses consistent formatting for all three research summaries.
  The subsequent typography pass justifies body text and adds first-line indents.
  Local hyphenation exceptions avoid stretched spacing on installations without
  Russian hyphenation patterns; tables retain left-aligned text.
- The GitHub repository and the three public preprints from the reporting
  interval have visible, clickable full URLs.
- The prose was revised against `research/WRITING_STANDARDS.md`: concrete
  statements, standard terminology, defined methods and claims limited to the
  demonstrated results. Grid refinement is described through increased
  resolution or node count, rather than literal translations of “finer grid”.
- The report describes development of the research code on top of GRTeclyn;
  it does not attribute the upstream codebase or its original GPU port to this work.
- The report leads with the stationary solver and the automated workflow:
  field-equation solves, independent checks, initial-data export, GPU evolution
  in GRTeclyn and analysis. Evolutionary optimisation appears as an application
  of this software, not its main result. CMA-ES is an evolutionary optimisation
  method also used in machine learning; no trained neural model or reinforcement
  learning system is claimed here.
- The solver is described within its implemented stationary, axisymmetric
  Einstein-scalar scope. Independent constraints and refinement checks are retained.
- The approximately 61% reduction is the finer-grid-checked D21 comparison,
  at fixed equatorial throat radius and angular momentum. Exotic matter is
  reduced, not eliminated. A reduction at every spin is not established:
  the D90 potential search did not beat its massless reference.
  The revised row defines the integrated null-energy-violation measure and
  describes the accompanying concentration near the throat, increased peak
  tides and longer light-transit time. CMA-ES appears only in this row, not as
  an umbrella method for every project in the following table.
- The first nonlinear three-dimensional evolutions of rotating wormholes and
  the Bondi dipole are highlighted within the novelty claims of the papers.
  Finite-time numerical persistence is not presented as proof of unlimited
  dynamical stability. The rapidly rotating wormhole result covers roughly
  28 static instability times, at three resolutions, for initially axisymmetric
  data. Collapse emits gravitational waves without an added nonspherical
  perturbation.
- The Bondi summary identifies the stress-energy tensor as the quantity entering
  with a negative sign, and distinguishes active from inertial and passive mass.
  The binary summary's more-than-100 calculations include control models, not
  just binary evolutions. Horizon formation is described for the studied head-on
  collision, not every close encounter. The feedback's amplitude comparison and
  percentage accuracy relative to zero momentum were not added. The rotating
  result retains instability growth time, rather than calling it a decay time.
- The author-supplied original funded proposal,
  `Research Proposal_ Neural Spacetime Engineering.pdf`, was read when revising the report.
  The author requested removal of the sentence explicitly linking the wave
  result to that proposal. Uncompleted proposal deliverables are not reported
  as achieved.
- Two upstream contributions were confirmed in `upstream/main` and by the
  author: PR #241 (3 September 2026, commit
  `4a474a49e93278493aba5c26c37f734ed0d12c70`) and PR #158
  (5 February 2026, commit `2b495106b12e93736416584bcceb0fac3b620e62`).
  Only #241 falls within the reporting period and is included. It fixes ghost
  cell filling in matter constraint and gravitational-wave diagnostics. Both
  commit hashes were checked as ancestors of the local upstream branch.
- The optimisation manuscript is described as prepared, with the main
  calculations completed, following the author's clarification. Its results
  and conclusions already contain five potential-bearing 3D evolutions and
  a three-resolution D21 study. All five cross the same contraction threshold
  later than the comparison runs; the D21 comparison also changes spin slightly
  and outer damping, so this is not stated as an isolated potential-only effect.
- The ring section includes completed GPU evolution of the weaker single ring
  to model time 50 and the separate three-resolution convergence study through
  time 2. Interior constraint orders approach four; charge and angular-momentum
  changes also converge. The stationary ergoregion rings, counter-rotating
  configurations and weaker evolved ring are distinguished. The current ring
  manuscript and evolution record establish short-time numerical convergence,
  not general long-term dynamical stability. The stronger ergoregion-ring
  evolutions have a failed early convergence comparison in the status record;
  their stability is not asserted in the report.
- The ring row also describes frame dragging at zero total angular momentum
  and spin-dependent arrival versus turnaround of test particles, following
  the stationary ring manuscript's abstract and results.
- The terminology follows the revised wording: exotic-matter minimisation,
  quantitative analysis criteria and an automatic calculation pipeline. The solver and
  pipeline are described as completed software, including in the opening and
  the first section heading.
- The spacetime-search project's row emphasises the developed analysis criteria
  and software: FTL travel-time advantage, curvature, changes in geometry and
  evolving light-ray tracing to detect shortcuts and their persistence. This
  follows the author's clarification that the analysis tools are the main
  contribution to report. It does not present short-lived candidates as the
  main result or retain the vague plan to study their matter properties.
  Following the latest feedback, the Russian term for the spacetime metric is
  no longer reused for a diagnostic criterion. FTL is explained as a travel-time
  comparison, not a local light-speed measurement.
- Journal status is based on the author's statements and submission records.
  The Bondi paper is at Physics of the Dark Universe; the author's screenshot
  shows “With Editor”, so the report uses “На рассмотрении редактора.”
  The author supplied the rotating-wormhole paper's submission confirmation
  from European Physical Journal C, manuscript ID `EPJC-26-11-317`.
  Its report row now names that journal and says “Подана в редакцию.”, with no
  submission date and no claim of external review or acceptance. The author also
  confirmed that the binary-wormhole paper has been submitted again to General
  Relativity and Gravitation. Its table row now names that journal and says
  “Подана в редакцию.”, without a submission date or claim of external review.
- Correspondence is paraphrased from the emails supplied by the author.
  It confirms a published equation misprint, unchanged original numerical
  results, agreement of calculations and thanks for the careful examination.
  It is not presented as a formal review or endorsement of every conclusion.
- arXiv titles are translated/described in Russian for the foundation's reader;
  the identifiers link to the exact original papers. Publication dates and
  current versions were checked on arXiv on 22 November 2026.

## Evidence used

Paths below are relative to the repository root.

| Report topic | Source |
| --- | --- |
| Solver scope, independent checks, CPU/GPU use | `grteclyn-wrapper/packages/stationary/README.md`; `grteclyn-wrapper/STATIONARY_RESEARCH.md` |
| Packaging and workflow organisation | `grteclyn-wrapper/ARCHITECTURE.md`; `research/railgun/STATUS.md`, software validation entries |
| Optimisation and its limits | `research/optimisation/article/research.tex`; `research/optimisation/article/numbers.tex`; `research/optimisation/STATUS.md`, D21 refinement and D90 comparison |
| Boson stars and Bondi dipole | `research/bondi_dipole/article/bondi_dipole.tex`; `research/bondi_dipole/STATUS.md` |
| Rotating wormholes | `research/spinningwormhole/article/research.tex`; `research/spinningwormhole/STATUS.md` |
| Binary wormholes | `research/merger/article/research.tex`; `research/merger/STATUS.md` |
| Ring ergoregions, counter-rotation and particle transport | `research/railgun/article/research.tex`, results and conclusions; `research/railgun/STATUS.md` |
| Completed ring GPU evolution and convergence | `research/railgun/EVOLUTION.md`; `research/railgun/STATUS.md`, completed time-50 run and Richardson study; `results/railgun/reports/evolution-richardson-070.md` |
| Coupled ring-wormhole study | `research/ringwormhole/STATUS.md` |
| Automated spacetime search | `research/neuralspacetime/article/research.tex` |
| Upstream fixes | `git show 4a474a49e`; `git show 2b495106b`; ancestry checks against `upstream/main`; author confirmation |
| Original research plan | `Research Proposal_ Neural Spacetime Engineering.pdf` (author-supplied PDF, stored outside the repository) |
| Misprint correspondence | The two emails pasted by the author in this conversation |

Verified public preprints:

- [Bondi dipole, arXiv:2608.24577](https://arxiv.org/abs/2608.24577), first posted 25 August 2026; v2 26 October 2026.
- [Binary wormholes, arXiv:2610.13206](https://arxiv.org/abs/2610.13206), first posted 9 October 2026; v2 24 October 2026.
- [Rotating wormholes, arXiv:2610.29941](https://arxiv.org/abs/2610.29941), first posted 21 October 2026; v2 6 November 2026.
