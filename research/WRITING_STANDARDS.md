# Writing standards for the papers

Every paper in `research/` follows these rules. Read them before writing or revising, and run the checklist at the
end before every submission.

They come from the first full referee reports we received. On 2026-10-20 General Relativity and Gravitation rejected
the Bondi dipole paper on presentation. Both referees said they could not follow the text: it used terms that are not
standard in numerical relativity and never defined them, it was packed with numbers, and so they could not judge the
method or the conclusions. The merger paper's two desk rejections (PRD on 2026-10-17; CQG on 2026-10-19, which named
"accepted standards for scientific reporting") point the same way. The full reports are kept locally only (the repo
is public), in `research/bondi_dipole/referee/`.

## 1. Use the field's vocabulary, not the lab's

Words from the campaign tooling mean nothing to a referee. Never use them in a paper. Use the standard
numerical-relativity term instead, or define a new term once, at first use, in one plain sentence.

| Lab word | Write instead |
|---|---|
| run matrix | the set of simulations (Table N) |
| cell (of a run matrix or table) | simulation, configuration |
| arm | simulation |
| rung | resolution, or the grid spacing Δx |
| campaign, campaign pair | drop it; "the two simulations that differ only in X" |
| repaint | say what is done ("the matter fields are reset to ...") |
| mass-matched | "with equal \|M\|", or define it |
| falsifiable run matrix | the set of simulations |
| results pack, registry | the data release (its Zenodo DOI) |
| trust window | the time up to which the solution is reliable, and why |
| csm, mode 3, seed tags | describe the method in words |

"Cell" stays only for grid cells.

## 2. Define every symbol and acronym at first use

- The abstract either defines its symbols or does not use them (the Bondi abstract used a, d, M and M̄ undefined).
- Define the standard quantities too: α (lapse), βⁱ (shift), ψ (conformal factor), K, and ρ, Sᵢ, Sᵢⱼ as the 3+1
  projections of the stress-energy tensor that source the Einstein equations.
- Define every acronym once: NEC, rms, MOTS, ADM, CCZ4, AMR.
- Define every model parameter where it first appears (e.g. m in the potential).
- A paper with more than about 15 symbols gets a notation table.

## 3. Quote the numbers the conclusions need, and no more

- The abstract states the main result qualitatively, with at most one or two headline numbers.
- The results text carries the argument. Per-run values (each separation, each variation) go into a table or an
  appendix. A sentence that strings several numbers together belongs in a table.
- The `\clm` ledger rule (CLAUDE.md, "The paper") still applies to every number that remains.

## 4. Explain the physics before using it

- State the model's key choice and why it is forced, as early as possible. Example: negating the phantom's stress
  tensor is the only choice compatible with conservation of the total stress tensor and with equations of motion
  derived from the action. Say so where it is introduced, and connect it to the NEC violation.
- An unusual construction (e.g. a bicomplex-valued field) gets an equation and one sentence of motivation where it
  first appears, or it is dropped.

## 5. Show convergence, not just constraints

Constraint norms against time do not show that a setup converges. Every numerical paper shows a convergence test:
- three resolutions with a fixed refinement ratio;
- a self-convergence plot of an evolved field (pointwise differences rescaled by the expected order), and the
  measured order against time;
- the same for the headline observable (e.g. the separation d(t)).

## 6. The main text tells the story; detail goes to appendices

- Each section opens with what it shows.
- Robustness checks, parameter scans and per-run tables go to appendices.
- Figure captions say what is plotted, then the outcome (CLAUDE.md, "The paper").
- Title and author names in normal case, no `\MakeTextUppercase`. Use the target journal's template.

## Checklist before every submission

1. Grep the source for the lab words of section 1. Every hit is replaced, or defined at first use.
2. List every symbol and acronym in order of appearance. Each is defined at or before first use, abstract included.
3. The abstract has no undefined symbol and at most two numbers.
4. No results paragraph strings per-run values together; they are in a table.
5. The convergence figure exists and shows the measured order.
6. A reader who did not write the paper (a colleague, or a fresh agent with no project context) reads the abstract,
   the introduction and one results section and lists every word or symbol they could not follow. All of them are
   fixed before submission.
