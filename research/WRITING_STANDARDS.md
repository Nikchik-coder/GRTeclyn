# Writing standards for the papers

Every paper in `research/` follows these rules. Read them before writing or revising, and run the checklist near the
end before every submission.

They come from the first full referee reports we received and from a review of how strong numerical-relativity (NR)
papers are written (both 2026-10-20). On 2026-10-20 General Relativity and Gravitation rejected the Bondi dipole paper
on presentation, not physics: both referees said they could not follow the text well enough to judge the methods.
Their points trace to five causes: undefined symbols, private vocabulary, too many numbers, an argument given in the
wrong order, and a missing convergence test. The merger paper's two desk rejections (PRD on 2026-10-17; CQG on
2026-10-19, which named "accepted standards for scientific reporting") point the same way, and the spinning-wormhole
draft repeats the same five causes. The full reports are kept locally only (the repo is public), in
`research/bondi_dipole/referee/`.

Strong NR papers read as plain, predictable reference documents: the novelty lives in the result, never in the prose.

## 1. Vocabulary: the field's, not the lab's

Use the term a referee already knows. Coin a word only when no standard one exists, and then define it once, in a
displayed sentence. APS puts it plainly: "Introduce new terminology or notation only when clearly needed." Words from
the campaign tooling mean nothing to a referee and never appear in a paper.

| Private term | Write instead | Note |
|---|---|---|
| campaign, campaign pair | our simulations; "the two simulations that differ only in X" | |
| run matrix, falsifiable run matrix | Table N: summary of simulations | "Falsifiable" belongs in the argument, not a table title |
| cell (of a run matrix or table), arm | simulation (run) | "Cell" stays only for grid cells |
| rung, ladder, base rung | resolution, resolution study, lowest resolution | "The two highest resolutions", not "the fine rungs" |
| mass ladder | sequence of equal-mass pairs of varying total mass | |
| mass-matched | equal \|M_ADM\| (to 0.4%), defined by the equation \|M₋\| = M₊ | |
| repainted | set analytically from the radial profile and interpolated onto the evolution grid | |
| dressed soliton, dressed star | solitonic boson star; self-gravitating Q-ball | |
| bicomplex field | two independent complex scalar fields | "Bicomplex" already names a number system |
| phantom (for the overall-sign sector) | negative-active-mass sector, or define the usage explicitly | Elsewhere, our wormhole papers included, "phantom" means a wrong-sign kinetic term: one word, two meanings |
| birth kick | initial transient in K | |
| the gap | separation d | |
| hill / well | the χ > 1 / χ < 1 region (local maximum / minimum of χ) | Fine as a gloss once defined |
| lone star | isolated star | |
| nulls; the signal | control runs (null tests); the midpoint displacement ΔX | |
| verdict | result | |
| deeper solve, solver depth | tighter elliptic-solver tolerance | |
| box doubling | doubling the domain size L | |
| certifies; "the runaway is real" | indicates; is consistent with | Scale the verb to the evidence |
| rung 0.2c, 0.30c, … | model D21, D30, … (D = drainhole, 100 vₑ), or vₑ = 0.21 | "0.2c" reads as the velocity of something moving |
| hold, static hold, production hold | evolution of the static drainhole | |
| numerical twin | reproduces | |
| recipe S / recipe F | dissipation σ = 0.1 / σ = 0.4 | Put the values in the setup table and drop the letters |
| trust, trust window | results are converged (reliable) up to t = … | Say why it ends there |
| seed, the seed's sign | initial perturbation (truncation error) and its sign | |
| fate, two fates | end state (collapse or expansion) | |
| kicks; pushed in / out | imposed radial perturbation of amplitude ε; inward / outward | |
| far side | the η → −∞ asymptotic region (the puncture) | |
| results pack, registry | the data release (its Zenodo DOI) | |
| csm, mode 3, seed tags | describe the method in words | |
| a name a cited paper never uses ("the triplet protocol of Ref. [23]") | the criteria of Sec. II of Ref. [23] | |

## 2. Symbols, acronyms and equations

- Define every symbol and acronym at first use, in the abstract and again in the body. (The Bondi abstract used a, d,
  M, M̄, Q̈ and ℓ undefined.)
- Name the standard 3+1 quantities once, in words: "where α is the lapse, βⁱ the shift and γᵢⱼ the spatial metric",
  plus ψ (the conformal factor), K, and ρ, Sᵢ, Sᵢⱼ as the projections of the stress-energy tensor that source the
  Einstein equations.
- Define every acronym once (NEC, rms, MOTS, ADM, CCZ4, AMR) and every model parameter where it first appears (e.g. m
  in the potential).
- Treat equations as prose: number every displayed equation, punctuate it like a sentence, and define its new symbols
  in the sentence that follows (Mermin).
- A paper with more than about 15 symbols gets a notation table.

## 3. Sentences

1. One claim per sentence, in the plainest grammar available, aiming for under 30 words.
2. Few dashes: at most one dash pair per paragraph. Use commas, parentheses or a new sentence instead.
3. No fragments or aphorisms ("That timing is the measurement.", "The grid—yes."). Write the declarative sentence
   they stand for.
4. No bold sentences in running text. Emphasis comes from position: the first sentence of a paragraph, or the
   conclusion list.
5. Scale the verb to the evidence: "we find", "we observe", "is consistent with", "we find no evidence of". Avoid "is
   real", "certifies", "exactly", "proves". "To our knowledge, the first" appears once in the paper.
6. Report the final setup, not the debugging history. Hard-to-read papers often follow the author's chronology instead
   of context, content and conclusion (Mensh and Kording). A pitfall others will hit gets one labelled paragraph or
   appendix.
7. Tense: past for what we ran ("we evolved"), present for what a figure shows ("Fig. 4 shows").

## 4. Numbers

- The abstract gives context, method, the main result and its scope. The qualitative finding comes first, then at
  most three numbers (one is better), and no symbol that needs a definition.
- One number per claim in running text. Supporting numbers go to a table or an appendix; a sentence that strings
  several numbers together belongs in a table.
- Match precision to the error: ΔX = 3.00 ± 0.01, never 3.0016 beside it.
- The `\clm` ledger rule (CLAUDE.md, "The paper") still applies to every number that remains.

## 5. Order of the argument

- State the test before the data: what would count as a positive result, and what would falsify it. Evstafyeva et al.
  list their tests for a real instability in their Sec. II, and every later result is read against that list.
- Put a consistency argument before its consequences. Example: negating the phantom's stress tensor is the only choice
  compatible with conservation of the total stress tensor and with equations of motion derived from the action. That
  gets its own short paragraph right after the action, connected to the NEC violation; the Bondi referee had to ask.
- One order per results paragraph: what was run, what was seen, what it means.
- State the scope of each claim early and in our own voice: the time span, the resolutions and the model assumptions
  behind it. A referee who finds a limit first stops trusting the rest. Scope is not a list of what was not done:
  CLAUDE.md ("The paper") rules out failure narratives and "not computed here".

## 6. Structure

Use the standard NR skeleton, so a referee can find and judge the methods without reading the results first.

1. Introduction: motivation, prior work, the gap, what this paper does, one sentence per later section.
2. Model: action, field equations, consistency (conservation, energy conditions), units.
3. Initial data: construction, constraint solve, transfer to the evolution grid.
4. Numerical methods: code, formulation, gauge, stencils, grid or AMR, boundaries and timestep, collected in one table.
5. Diagnostics: each tracked quantity as a numbered equation, with one line on what it tests.
6. Criteria: what counts as a positive result and what would falsify it.
7. Results: one subsection per claim, each opening with the question it answers.
8. Validation: convergence, control runs, systematics; long material goes to an appendix.
9. Conclusions: findings, then their scope, then outlook.

## 7. Tables, figures and captions

- Keep setup and results apart. One table lists every simulation: a short model label (S005, D21; never a campaign
  name), the physical parameters, L, N or the finest Δx, the final time and the role (production, control,
  resolution study). A second table holds the measured results. Bondi Table I mixed setup, results, verdicts and four
  footnotes in one grid, and the referees could not parse it.
- Each figure answers one question, and every panel is cited in the text.
- Captions: the first sentence says what is plotted against what, for which run; then the line styles and symbols;
  then one closing sentence with the outcome (CLAUDE.md's caption rule), without a "The outcome:" label and without a
  title-like opener such as "One rate, two fates". Aim for five lines or fewer.
- Title and author names in normal case, no `\MakeTextUppercase`. Use the target journal's template, and let the
  title state the result where possible.

## 8. Convergence and validation

Referees expect two separate tests:

1. The constraint norms fall to zero at the scheme's order: the run converges to a solution of Einstein's equations.
   Rescaling constraint norms by 2ⁿ between two resolutions is valid because their exact value is zero; say so in
   one sentence.
2. Every quoted observable (ΔX, a, τ, E₂₀, …) self-converges across three resolutions.

A plot of constraint norms against time, at any number of resolutions, is neither test unless the curves are rescaled
by the expected factor.

For grid spacings h₁ > h₂ > h₃, the expected self-convergence factor at order n and the measured one for an
observable f are

```latex
Q_n = \frac{h_1^{\,n} - h_2^{\,n}}{h_2^{\,n} - h_3^{\,n}}, \qquad Q_{\rm meas} = \frac{f_1 - f_2}{f_2 - f_3}.
```

| Resolution triple | h₁:h₂:h₃ | Q₂ | Q₃ | Q₄ |
|---|---|---|---|---|
| N = 128/192/256 (Bondi Δx = 0.5, 0.33, 0.25; spinning D90) | 6:4:3 | 2.86 | 4.11 | 5.94 |
| N = 96/128/192 (spinning D21) | 4:3:2 | 1.40 | 1.95 | 2.69 |

If f₁ − f₂ and f₂ − f₃ have opposite signs (Q_meas < 0), the lowest resolution is outside the convergent regime.

What to show (as in Evstafyeva et al., Appendix A, Fig. 5, and Clough et al., Appendix A):

1. The main observable's pairwise differences f₁ − f₂ and f₂ − f₃ against time, the second rescaled by Q₃ and Q₄; the
   curve that overlays f₁ − f₂ gives the order. Clough's thesis (arXiv:1704.06811, Sec. 3.3.4) shows this plot for
   nearly the same spacing ratios.
2. The Hamiltonian and momentum constraint norms at three resolutions, rescaled the same way, with the order stated
   in words ("between third and fourth order").
3. If asked, a pointwise version: the same differences along the x axis at one late time.

## 9. Model papers

- T. Evstafyeva, N. Siemonsen and W. E. East, arXiv:2508.11527 (the stability of ultracompact spinning boson stars).
  It has one number in the abstract; Sec. II states the tests for a real instability before any data; Table I collects
  code, formulation, gauge, Δx range, domain and levels; diagnostics are numbered equations; Appendix A shows
  three-resolution convergence with rescaled third- and fourth-order curves; models are labelled (S005, S02) with
  their parameters in a table.
- K. Clough, T. Dietrich and S. Khan, arXiv:2406.02466 (gravitational waveforms from warp-drive collapse, matter that
  violates the energy conditions). It has no numbers in the abstract; one paragraph gives L, N, levels, finest Δx and
  boundaries; flux integrals are numbered; the strongest claim is scoped ("waveforms likely model-specific").

## Before → after

| Before | After | What changed |
|---|---|---|
| Across a matrix of thirty-four evolutions—runaway pairs, controls, and parameter scans—a mass-matched pair released at rest accelerates as a unit. | A pair of stars with equal \|M_ADM\| (to 0.4%), released from rest, accelerates as a single object. Table I lists all 34 simulations, including the controls. | Defines "mass-matched"; claim and inventory split; no dash aside |
| …the solved metric moves grid cell by grid cell … while the matter is repainted analytically from its radial profile table. | The metric from the elliptic solve is copied cell by cell onto the evolution grid; the scalar field is recomputed on that grid from its radial profile. | Standard verbs |
| That timing is the measurement. | The equal merger times are the key result: gravity attracts PP and repels MM, so if gravity set the timescale only PP would merge. | Fragment becomes a claim with its reason |
| Unequal masses—no. … The moving box—no. … The grid—yes. | We tested three possible causes: the mass mismatch, the moving domain and grid resolution. Only resolution changes the opening, which falls eightfold as Δx halves. | One sentence for the test, one for the result |
| (1) The runaway is real, and it is steady. | (1) The pair accelerates at a constant rate. | Verb scaled to the evidence |
| Perturbative initial data fail first. | We first evolved the second-order (O(J²)) backgrounds of Ref. [18] at J = 0.25 and 1. | Topic sentence says what was done |
| …the static drainhole run through this pipeline is a numerical twin of the production hold of Ref. [11]… | Evolving the static drainhole with this pipeline reproduces Ref. [11]: identical initial data, Hamiltonian-constraint norms within 5 × 10⁻⁷ for t ≤ 100, and collapse times within one time unit. | No private terms |
| …at 81% the throat is stable to t = 150 at three resolutions. | At 81% of the extremal angular momentum the throat radius shows no growth up to t = 150, about 34 e-folding times of the static mode, at three resolutions. | Claims absence of growth, scaled to the instability's own timescale |
| One rate, two fates: the measured rate 1/τ (left axis; τ right) against… | Inverse e-folding time 1/τ of the throat's areal radius against angular momentum as a fraction of its extremal value. | Caption opens with what is plotted |
| ε = ±10⁻³: pushed out collapses, in inflates | Radial perturbation, \|ε\| = 10⁻³: outward leads to collapse, inward to expansion | Readable as a table entry |

## Checklist before every submission

1. Grep the source for every private term in section 1. Each hit is replaced, or defined once at first use.
2. Every symbol and acronym is defined at first use, in the abstract and again in the body.
3. The abstract carries at most three numbers and ends with the result's scope.
4. The criteria for each claim appear before the results.
5. Simulations and results sit in separate tables, and every run has a short model label.
6. Every displayed equation is numbered and punctuated as prose.
7. Every headline observable has a measured self-convergence factor beside the expected one, and the constraint norms
   are shown rescaled.
8. Quoted precision matches the error bar for every number.
9. Captions open with what is plotted, close with one outcome sentence, and run to five lines or fewer.
10. Verbs are scaled to the evidence, and "to our knowledge, the first" appears once.
11. No unfinished runs, draft notes or debugging chronology remain in the main text.
12. The journal's requirements are met: GRG wants a data availability statement under "Declarations"; PRD follows the
    APS Journals Style Guide.
13. A reader outside the project (a colleague, or a fresh agent with no project context) reads the abstract, the
    introduction and one results section and marks every word or symbol they had to guess. Each mark is fixed before
    submission.

## Open items on the current drafts (2026-10-20; delete each when fixed)

### Bondi dipole paper

- [ ] **Convergence, the one point wording cannot fix.** ΔX(200) = 2.8815, 3.0139 and 3.0016 at N = 128/192/256 give
  Q_meas = −10.8: the two differences have opposite signs, so N = 128 is outside the convergent regime. The draft's
  argument that a base grid 4% low is "the opposite of what a discretization artefact does" will not persuade. Two
  honest fixes: add N = 320 (Δx = 0.2; a new run, so it needs a go) and quote Q_meas for the top three resolutions
  against their own Q₄; or state that N = 128 is not convergent, quote the N = 192/256 difference as the error bar,
  and put every base-grid number (separation scan, mass ladder) behind that caveat.
- [ ] Rename the "phantom" sector, replace "bicomplex" with two independent complex scalar fields, split Table I into
  setup and results tables, and give the consistency argument its own paragraph after the action.
- [ ] A draft abstract to start from. Check every claim and number against the ledger before using it.

  > Bondi showed in 1957 that a body of negative active gravitational mass, paired with a positive one, should
  > accelerate together with it indefinitely while the total momentum stays zero. We test this prediction in full 3+1
  > numerical relativity. The matter consists of two complex scalar fields with identical self-interactions; one
  > enters the Einstein equations with the opposite sign, so its inertial and passive masses are positive and its
  > active (ADM) mass is negative. We construct constraint-satisfying initial data for solitonic boson stars of both
  > signs and evolve 34 configurations, including same-sign pairs and isolated stars as controls. A pair of stars with
  > equal ADM mass magnitude, released from rest, accelerates as a single object at constant separation, while the
  > total signed matter momentum stays zero to within 1%. The acceleration scales with separation and mass as Bondi's
  > Newtonian law predicts, reverses when the two stars are exchanged, and is absent in every control run. We detect
  > no gravitational radiation from the accelerating pair, consistent with the absence of a mass dipole. To our
  > knowledge, the negative-mass star is the first asymptotically flat body of negative ADM mass evolved in numerical
  > relativity.

### Spinning-wormhole paper

The presentation pass landed 2026-10-20 (models D0–D90, Table III rebuilt, the rewritten abstract, the softened
Sec. II A, the condensed Sec. IV B with the interface appendix, captions, title "Rotation slows the instability of
Ellis–Bronnikov wormholes"; "to our knowledge, the first" was dropped from the abstract on 2026-10-20). What remains
is substance:

- [ ] Remove unfinished runs before submission. Table III still lists the D59 and D70 rows as "in progress"; they
  leave the table (or land finished) before anything goes out.
- [ ] Control the perturbation sign at 33%. The vₑ = 0.51 model expands with one outer-boundary treatment and shrinks
  with the other, so its end state depends on the boundary. Repeat the explicit ±ε radial perturbations run at
  vₑ = 0.21 on this model before claiming a branch switch.
- [x] Converge τ (resolved 2026-10-20, the offset-free estimator adopted everywhere). The deficit-band fit was biased
  by the early transient's baseline, resolution-dependently, and failed to self-converge; the offset-free fit (slope
  of ln |dR_A/dt| over the same band) gives Q_meas = 2.3 between Q₃ = 1.95 and Q₄ = 2.69 on the D21 triplet, sits on
  a band plateau, and its D21 continuum (5.5–5.7) and static (toward 5.1) values land on the second-order and
  linear-theory rates. The paper now quotes τ = 5.4/6.6/8.3/13.3 (D0–D40), fits a − b(J/A)² through the collapse
  branch alone (zero at 32%, beside the second-order 33%), and the expansion rates rise past the crossing. D90 needs
  no Q_meas: its drift is a null bounded by 7×10⁻⁵ at all three resolutions. Still open: the τ = 5.8/5.6 quoted for
  the O(J²)-seeded evolutions predate the estimator change — re-measure when those numbers enter the claims ledger.
- [ ] Consider writing to the authors of Ref. [15] about the ν-equation correction before submission; Kunz's group
  is a likely referee.

## Sources

- T. Evstafyeva, N. Siemonsen, W. E. East, [Assessing the stability of ultracompact spinning boson stars with nonlinear
  evolutions](https://arxiv.org/abs/2508.11527), arXiv:2508.11527.
- K. Clough, T. Dietrich, S. Khan, [What no one has seen before: gravitational waveforms from warp drive
  collapse](https://arxiv.org/abs/2406.02466), arXiv:2406.02466.
- K. Clough, [Scalar Fields in Numerical General Relativity](https://arxiv.org/abs/1704.06811), PhD thesis,
  arXiv:1704.06811, Sec. 3.3.4 (the self-convergence plot with rescaled differences).
- APS, [Physical Review Letters: Information for
  Contributors](https://journals.aps.org/prl/issues/107/2/deliverables/information-for-contributors/print).
- APS, [Journals Style Guide for
  Authors](https://res.cloudinary.com/apsphysics/image/upload/APS_Journals_Style_Guide_Authors022326_rwlapn.pdf),
  February 2026.
- N. D. Mermin, [What's wrong with these equations?](https://physicstoday.aip.org/opinion/whats-wrong-with-these-equations),
  Physics Today 42 (10), 9 (1989).
- B. Mensh, K. Kording, [Ten simple rules for structuring papers](https://doi.org/10.1371/journal.pcbi.1005619), PLoS
  Comput. Biol. 13, e1005619 (2017).
- Springer, [General Relativity and Gravitation: data availability
  statement](https://link.springer.com/journal/10714/updates/19864720).
- The GRG referee reports on the Bondi dipole paper (kept locally), and the drafts arXiv:2608.24577 and
  "Investigating the stability of spinning wormholes with nonlinear evolutions".
