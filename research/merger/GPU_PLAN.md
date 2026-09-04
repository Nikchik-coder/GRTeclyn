# GPU plan for the paper runs

Companion to `Plan.md`, which holds the campaign record; this file holds the
design and the decision ledger for the production data behind the article.
**Nothing here launches without a by-hand approval, one run at a time,
through `run_single.sh`.**  Rewritten 2026-09-03: compacted, duplications
removed; the full narrative history is in this file's git history.

*Second external review absorbed 2026-09-03.  Adopted: the credibility batch
(#13-#17, runs before production), the fast-characteristic ceiling (§6), the
restart-recipe documentation (§5), the Helfer mechanism (§1), the BBH
known-answer calibration (§7.8).  Checked against the tree and REJECTED — do
not re-import: "p020's Chk05000 exists, 2 GPU-h restart" (the sweeper took
every p020_nofill and plain-twin checkpoint — uninsured names; only the 3
held plotfiles survive); "Plan.md states the sqrt(2) characteristic" (no such
line exists — the physics is adopted on its own merit); the hardcoded
x>0 / x<0 tracker split (the binary's axis rotates with the orbit — the
argmin-neighbourhood fix of §9 stands).*

---

## THE MODEL — exactly what the code solves

*Read out of the source 2026-09-04, not from memory.  Files:
`Examples/BinaryWormholeMerger/BinaryWormholeInitialData.hpp` (initial data),
`Source/Matter/ExoticScalarField.{hpp,impl.hpp}` (matter),
`Examples/BinaryWormholeMerger/PhantomDecayPotential.hpp` (potential),
`Source/Matter/ScalarFieldKernels.hpp` (kinetic invariant).  Every formula
below is transcribed from the code, with the production parameter values that
actually appear in the params files.*

### M1. The system

Einstein + one real scalar field whose stress-energy enters with the WRONG
SIGN.  In geometric units G = c = 1:

    G_ab = 8 pi T_ab^(phantom),        T_ab^(phantom) = -s T_ab^(canonical)

`s` is `wormhole_support_strength` = **1.0** in every campaign run, so the
model is exactly "canonical scalar, negated stress-energy".  s is not a
fudge factor in production; it exists only so a support-removal experiment can
ramp it (`support_ramp_start` / `_duration`, with an optional causal delay
`support_causal_speed`).  Negating T_ab is what violates the null energy
condition and is what holds a throat open.

### M2. Matter — the exact expressions in the code

Variables: scalar `phi`, and `Pi` = its normal derivative, defined by the code's
own evolution equation `d_t phi = alpha Pi + beta.d phi`, i.e.

    Pi = n^a d_a phi                          (Lie derivative along the normal)

Kinetic invariant (`ScalarFieldKernels::kinetic_invariant`), with h^ij the
inverse conformal metric and chi the conformal factor:

    Vt = -Pi^2 + chi h^{ij} d_i phi d_j phi   ( = g^{ab} d_a phi d_b phi )

Stress-energy handed to the CCZ4 equations (`emtensor_with_strength`), all four
pieces carrying the same overall `-s`:

    rho   = -s ( Pi^2 + Vt/2 + V )          =  -s ( Pi^2/2 + |Dphi|^2/2 + V )
    j_i   = -s ( -d_i phi  Pi )             =  +s Pi d_i phi
    S_ij  = -s ( d_i phi d_j phi - (h_ij/chi)( Vt/2 + V ) )
    trS   = chi h^{ij} S_ij

So **rho < 0** wherever the field is non-trivial: that is the whole mechanism.

Field equations (`add_matter_rhs`) — note these are the CANONICAL Klein-Gordon
equations, unmodified:

    d_t phi = alpha Pi + beta^i d_i phi
    d_t Pi  = alpha ( K Pi - dV/dphi ) + beta^i d_i Pi + [gradient terms]

Potential (`PhantomDecayPotential`):

    V(phi) = (1/2) m_phi^2 phi^2,      dV/dphi = m_phi^2 phi

with `phantom_mass` = m_phi = **0.0 in every campaign run**, so
**V == 0 and dV/dphi == 0 identically** — the scalar is massless and the
potential never enters anything.

> **A modelling subtlety, recorded so nobody trips on it later.**  The code
> negates T_ab but evolves the *canonical* KG equation (`box phi = dV/dphi`).
> A true phantom Lagrangian L = +(1/2)(d phi)^2 - V would instead give
> `box phi = -dV/dphi`.  **The two are identical when V == 0**, which is our
> case, so nothing in this campaign is affected.  They differ the moment
> `phantom_mass != 0`, and that choice would have to be made deliberately
> before any massive-scalar run.  See also: the GRTeclyn test suite runs a
> zero potential, so it does not exercise this at all.

### M3. Initial data — `wormhole_id_type = 1`, the regular massive drainhole

Per throat, with `a` = `wormhole_throat_radius_X` and `m` =
`wormhole_drainhole_mass_X` (**m IS the ADM mass**), in isotropic radius r:

    X     = ( r - a^2/(4r) ) / a
    Omega = 1 + a^2/(4 r^2)
    u     = (m/a) ( atan X - pi/2 )                  -> 0 at infinity
    alpha = e^u                                       exact static lapse
    gamma_ij = e^{-2u} Omega^2 delta_ij   =>  chi = e^{2u} / Omega^2
    phi   = sqrt(a^2 + m^2) / ( a sqrt(4 pi) ) * atan X
    K = 0,   A_ij = 0,   Pi = 0

The amplitude is not free: the field equations fix `4 pi C^2 = a^2 + m^2`,
which is what makes this an exact solution rather than an ansatz.  For ONE
throat both constraints hold identically at t = 0.

**The mass rides in the LAPSE, not in the conformal factor.**  That is the
whole reason for id_type = 1: the old id_type = 0 added a Brill-Lindquist
puncture `m/(2r)` to psi, which drove chi -> 0 at the throat itself
(chi = 1/16 at the minimal surface, proper cell width 4 dx and growing) and
made the matter unevaluable there.  Under id_type = 1, chi at the throat stays
in [0.15, 0.25] for m/a in [0, 1] — mass no longer costs resolution.
Derived, not assumed: the minimal surface is at l = m, i.e.
r = (m + sqrt(m^2+a^2))/2, with areal radius R_min = e^{-u(m)} sqrt(m^2+a^2).

**Superposition for the binary** (this is where exactness is lost):

    u_sum = u_A + u_B,                       alpha = e^{u_sum}
    psi   = 1 + [sqrt(Omega_A) - 1] + [sqrt(Omega_B) - 1]
    chi   = e^{2 u_sum} psi^{-4}
    phi   = phi_A + sigma_B phi_B,           sigma_B = wormhole_phi_sign_B

Error is O(a^2/d^2) plus O(m/d).  **Only the Hamiltonian constraint is
violated at t = 0** — with K = 0 and Pi = 0 the matter momentum density
vanishes and the Bowen-York A_ij is flat-space divergence-free, so the
momentum constraint holds exactly.

**`phi_sign_B` is the physics knob for the whole repulsion result.**
`phi -> -phi` is an exact symmetry of a single drainhole (same geometry,
mirrored scalar), so either sign is a legitimate body; the RELATIVE sign sets
the scalar force between the pair.  A phantom field REPELS like charges and
ATTRACTS opposite ones, with

    |F_phi / F_grav| = (a^2 + m^2) / m^2      ( = 5 at a = 2, m = 1 )

always > 1, so like-oriented throats can NEVER merge under their own gravity.
`phi_sign_B = -1` turns the push into a pull and is the only gravity-driven
route to a merger.

**Momenta** — Bowen-York per throat, summed, then converted:

    Ahat_ij = (3/(2 r^2)) [ P_i n_j + P_j n_i - (delta_ij - n_i n_j) P.n ]
    A_ij    = chi^{3/2} Ahat_ij

**Helfer/Ning correction** (`wormhole_helfer_correction`, default 0 = off):
hands each throat back the constants its companion leaves at its centre,
windowed so infinity never sees the subtraction:

    psi   -= W_A dpsi_A + W_B dpsi_B,     u_sum -= W_A du_A + W_B du_B
    W_X(r_X) = exp[ -(r_X / w)^p ],       w = helfer_width (0 = auto = d/3),
                                          p = helfer_power (default 2)

It trades a measured ~9.5% error in each throat's initial size for a **1.13x**
increase in the initial Hamiltonian violation.  (CORRECTED 2026-09-04: this
line read "1.8x", which was wrong.  Checked across all seven arms that carry
the correction and all three that do not — every corrected arm starts at
3.34-3.38e-03 and every plain arm at 2.99e-03, so the ratio is 1.12-1.13 with
no spread worth quoting.  The 1.8x came from reading a regrid-spiked sample as
if it were a level; see B6 for how that statistic misbehaves.)  REJECTED for
production (it stalls mergers); currently under test on a fly-by as **B6**.

### M4. Gravity sector and gauge — the production values

    formulation = 0            CCZ4
    kappa1 = 3.0,  kappa2 = 0.0,  kappa3 = 1.0,  covariantZ4 = 0
    max_spatial_derivative_order = 4

    lapse:  1+log slicing, lapse_coeff = 2.0, lapse_power = 1.0,
            lapse_advec_coeff = 1.0,  min_lapse = 1.0e-10
    shift:  Gamma-driver, shift_Gamma_coeff = 0.75, eta = 1.0,
            shift_advec_coeff = 1.0

    initial lapse: wormhole_initial_lapse_type = 5
                   = the drainhole's OWN exact static lapse alpha = e^{u_sum}

Type 5 is not a gauge preference — the massive drainhole is static only with
that lapse.  Type 6 is the same thing times an origin-isolating collar
`prod_c [1 - exp(-(r_c / f a_c)^p)]`, needed at deep refinement because
chi ~ r^4 at each compactified origin (the far universe squeezed to a point).

### M5. Production parameter set (the merger arms)

    wormhole_id_type            = 1
    wormhole_throat_radius_A/B  = 2.0        (a)
    wormhole_drainhole_mass_A/B = 1.0        (M_ADM = 1 each)
    wormhole_bare_mass_A/B      = 0.0        (id_type 0 leftover, unused)
    wormhole_centerA/B          = -+ d/2 on x      (d = 12 nominal)
    wormhole_momentumA/B        = -+ p transverse  (p = 0.12 ... 0.45)
    wormhole_phi_sign_B         = -1.0       (attracting; +1 for repulsion arms)
    wormhole_subtract_phi_asymptote = 1
    wormhole_support_strength   = 1.0
    phantom_mass                = 0.0

### M6. What is NOT part of the physical model

These are numerical devices added at EVOLUTION time.  Anything measured while
they are active is a statement about the scheme as much as about the physics,
and the paper must say which arms used them:

- **`core_matter_damping`** (production arms: ON, window
  `core_damping_lapse_start = 3.0e-2` -> `core_damping_lapse_full = 1.0e-3`) —
  drives phi and Pi exponentially to zero deep inside a collapsed core, the
  matter half of the puncture trick.  Without it the phantom keeps sourcing the
  metric at the edge of the floored region and the run NaNs.  #14 measured its
  effect on the death time at ~0.5 units, i.e. noise.
- **`CoreLapseFreeze` / `CoreFreezeFill`** — the interior freeze used to push
  the waveform past the wall (§5, §6).  Validated separately: frozen arm
  bit-identical to its unfrozen twin beyond r = 6.
- **Floors:** `min_lapse = 1e-10`, and the initial data clamps chi at 1e-10.

### M7. Where the model is known to be weakest

1. **Superposed initial data carries a Hamiltonian defect by construction**
   (O(a^2/d^2) + O(m/d)).  A CTTK solve (Route B) removes it; not done.
2. **The scalar's cross term is untreated.**  Each throat's atan tends to
   +pi/2, and `subtract_phi_asymptote = 1` removes the constant — exactly free
   for a massless field, NOT free at phantom_mass != 0.
3. **Helfer/Ning is off in production**, so each throat starts ~18% larger on
   lengths than its own field equations support, and rings.  B6 is testing
   whether that is what drives the late accuracy loss.
4. **The canonical-KG-with-negated-T_ab choice** (M2) is unexercised by the
   test suite and only innocuous because V == 0.

---

## Working a run, systematically

Every campaign run, when it terminates, goes through the same close-out —
no exceptions, no ad-hoc shortcuts:

1. **run → finished** — confirm from `ADVANCE at time` lines (never
   "TimeStep time:", which is wall-clock), and read the death step's data
   for NaN pollution before quoting any number from it.
2. **check tmp for pollution** — leftover plotfiles/checkpoints on
   `/tmp/grteclyn_scratch/<run>/` and in the run dir.
3. **prune if needed** — after any offline scan that still needs the
   plotfiles; log every deletion in the current `MANIFEST_CLEANUP_*.md`.
   **The manifest is APPEND-ONLY and is not in git** (`runs/` is never
   tracked), so it has no undo: add to it with `cat >> …  <<'EOF'` and
   never with a whole-file write.  On 2026-09-04 a whole-file write
   destroyed a day of close-out entries; they were reconstructible from the
   session transcript that time, which is luck, not a recovery procedure.
4. **check results → valuable → copy from runs/ to results/** — add the
   run to `results/merger/analysis/make_summary.py` (WHAT + ORDER), then
   `bash research/merger/pack_results.sh`; results/ is the git-kept
   record, runs/ is not.
5. **update the results README exactly where needed** — the claim-first
   sections each name the statement being proved; the new run goes into
   that statement's Claim/Runs lines, and the "nothing in flight" note is
   kept truthful.
6. **update this plan** — §2 spine, §3 table, and the numbered item the
   run answers.

---

## CRITICAL BUG BEFORE PRODUCTION RUN

*Found 2026-09-04, during the close-out of the L = 128 sizing probe.  Two
separate defects in how this campaign has been measuring horizons.  One is a
coding bug and is fixed; the other is a physics misreading and is NOT fixed —
it invalidates the way the black-hole claim has been stated.  Nothing here
changes the production grid, the box or the schedule; it changes what the
production run must MEASURE and what the paper may SAY.*

### Defect 1 — coarse-level scans read the wrong region (FIXED)

`ah_radial_scan.py` sized its covering grid with the *finest* level's cell
size no matter what `--level` was asked for.  yt sizes a covering grid as
`dims * dds(level)` and honours `left_edge`, so a level-3 request on a
max_level-5 file covered **4x the requested width, with the box centre
displaced 6 code units off the object**.  Measured directly:

  level 5: dds 0.015625  covers 30.000 .. 34.000  (requested 30 .. 34)  OK
  level 4: dds 0.031250  covers 30.000 .. 38.000                        WRONG
  level 3: dds 0.062500  covers 30.000 .. 46.000                        WRONG

- Inert whenever `--level` equals the file's max_level.  Every level-5 scan
  of a level-5 file, and every historic level-3 scan of a level-3 file, is
  therefore UNAFFECTED — including the 1.07 -> 0.59 dissolution curve.
- Fatal for the cf08 "level ladder".  The recorded finding that the same file
  shows a trapped shell at level 5 and **nothing** at level 3 was this bug:
  the coarse scan was looking at empty space six units away.
- **The "scan-depth systematic" recorded in #16 and in the results README is
  WITHDRAWN.**  Re-run after the fix, cf08 Plt05500 gives r = 0.920 / 0.920 /
  0.940 at levels 5 / 4 / 3 — the shell is resolution-robust, which makes the
  measurement stronger than it was, not weaker.  #16's WARNING paragraph and
  the README's "rate is a scan-depth systematic" sentence must both be
  corrected.
- Fix applied: `dx = smallest_dx * 2 ** (max_level - LEVEL)`, matching
  `blob_nature_scan.py`, which always had it right (so every #13 number
  stands).

### Defect 2 — a trapped shell inside a throat is not a horizon (OPEN)

The radial scan defines "outward" as increasing coordinate r.  **Inside a
wormhole throat that is the wrong direction** — coordinate-outward there runs
toward the other mouth, where the surface area is falling.  Theta computed
with `s = +dr` is then the INgoing expansion, and its negativity means
nothing.  Consequence: the scan labels the interior of *any* throat "trapped",
collapsed or not.

Control, on a throat that certainly has not collapsed — the sizing probe at
t = 5, K ~ 4e-3, five time units into a healthy inspiral:

  ah_radial_scan  -> "rays trapped: 100%", shell r = 1.340, M_irr = 2.613
  areal radius    -> 25.0 (r=0.2), 4.45 (r=1.2), **4.255 (r=1.5, minimum)**,
                     4.27 (r=1.8), 4.85 (r=2.8)

The "horizon" at 1.34 sits inside the areal minimum at ~1.5.  It is the
throat, reported as a black hole.

Applying the discriminator (is the shell inside or outside the areal-radius
minimum?) to **both merged arms on disk** — independent damping treatments,
independent resolutions, one a restart and one from t = 0:

  arm              times        areal minimum          coordinate shell
  cf08 (lvl 5)     54.5..55.5   4.128 -> 4.085  r~1.0  0.94 -> 0.92 -> 0.90
  nodamp (lvl 3)   50.5..51.5   4.297 -> 4.257  r~1.2  1.12 -> 1.08 -> 1.06

Three findings, both arms agreeing:

1. **The trapped shell lies INSIDE the areal minimum on both arms** (0.92 vs
   1.0; 1.06 vs 1.2) — the same configuration the uncollapsed control
   produces.  Outside the minimum, where the outward direction is
   unambiguous, NEITHER arm has a trapped surface.  The trapped-surface
   evidence therefore does not distinguish the merged core from an ordinary
   wormhole throat, and **"the merger produces a black hole" is not supported
   by it**.
2. **The contraction is real and gauge-independent**: the throat's minimum
   areal radius falls ~1.0 %/unit (cf08) and ~0.9 %/unit (nodamp).  Two
   independent arms, a measure no coordinate change can touch.
3. **The coordinate rate overstates it 4-5x** on both arms.  The quoted
   1.07 -> 0.59 "accelerating" curve is a coordinate curve; the acceleration
   is a gauge effect.  Withdraw the rate and the word.

Caveat on the caveat: the radial scan tests coordinate spheres about a chosen
centre.  A true marginal surface need not be one, so "no trapped surface
outside the minimum" holds within that approximation.  That is exactly why
the proposals below do not lean on it either.

### Proposals — decide BEFORE the production launch, no code yet

- **P1 (cheapest, do first).  Make the areal radius the headline measure.**
  Track the minimum of the areal radius on coordinate spheres about the core
  and quote its time derivative.  It is invariant under coordinate changes,
  it already reproduces across two arms, and it needs nothing new — only that
  the production run write plotfiles often enough to differentiate it.  The
  present 0.5-unit cadence gives ~2 usable points per unit; 0.1 would give a
  real curve.
- **P2.  Report the orientation test beside every horizon number.**  A
  trapped shell is only quotable as a horizon if it sits at or outside the
  areal-radius minimum and Theta > 0 outside it.  Both current arms fail this
  test; if the production run passes it, the black-hole claim returns on
  honest evidence.  Costs one extra column in the scan output.
- **P3.  A real MOTS finder (BHaHAHA or equivalent).**  Solves the marginal
  surface properly instead of assuming coordinate spheres, and handles the
  orientation question correctly by construction.  This is the only way to
  settle "is there a horizon" rather than bounding it.  Previously parked as
  infrastructure; Defect 2 promotes it to **load-bearing** if the paper wants
  to keep any horizon language.
- **P4.  Event-horizon tracer on the production stack (#12).**  Null rays
  traced backwards through the wrapper's `EvolvingMetricField` give the event
  horizon, which is defined causally and is immune to both defects above.  It
  needs the run's FUTURE on disk, so it is a production-run deliverable and
  cannot be retrofitted onto the 3-file death stacks.  This is the strongest
  available answer to "did a horizon form", and it is the reason the
  production run's plotfile cadence is a physics decision, not a disk one.
- **P5.  Decide the paper's wording now, not after the run.**  On present
  evidence: keep "the throat contracts, ~1 %/unit, measured invariantly on
  two independent arms"; drop "black hole that dissolves" and the
  1.07 -> 0.59 rate until P3 or P4 supports them.  If the production run plus
  P3/P4 do support a horizon, the claim returns stronger than it ever was.

**Gate: the production run should not launch until P1's cadence and the P3/P4
choice are settled, because both are decisions about what the run writes to
disk — and neither can be fixed after the fact.**

---

## BLOCKER BEFORE PAPER GPU LAUNCH

*Found 2026-09-04, by plotting the waveform against the fly-by control for the
first time and then chasing why the control misbehaved.  This section is
separate from the CRITICAL BUG section above: that one is about how we MEASURE
horizons, this one is about whether the runs are accurate at the times we make
claims.  Every number below is from streams already on disk; no new runs.*

### B1 — there are TWO failure modes, and only one of them is a constraint problem

*Rewritten 2026-09-04 (second pass).  The first version of this section used
"time to cross 3x / 100x the floor" as the statistic and concluded that
accuracy bottoms out at t ~ 30-36 in every arm, so every claim sits after the
turn.  That was wrong on both counts: the crossing times were set by transient
spikes, not by the trend, and reading the LAST steps of each arm instead shows
the merging arms die with clean constraints.  The old table is withdrawn.*

`constraint_norms.dat`, L2 Hamiltonian.  Exponential fit runs from each arm's
floor to the last point below 100x that floor, so the terminal blow-up is
excluded from the fit and cannot manufacture the trend.

**Mode A — sudden local death, constraints clean right up to it.**  The tight
and the merging arms.  The last recorded Ham is at or near the arm's floor,
and the run is gone within two or three steps of it:

  arm                     dies at   Ham at death   x floor   e-fold   last 3 steps
  p = 0.12  L5 cf10        44.94       4.03e-03      1.3      ~60     4.16e-3 -> 4.06e-3 -> 4.03e-3  (FALLING)
  p = 0.12  L3 nodamp      51.53       4.77e-03      1.8      6.1     4.77e-3 -> 1.70 -> 49.2
  p = 0.20                 47.85       7.90e-03      3.0     17.3     7.87e-3 -> 7.88e-3 -> 7.90e-3

The L5 arm is the sharpest statement available: its Hamiltonian is *decreasing*
on the three steps before it dies.  A global constraint monitor gives no
warning at all in this mode, so **"the constraints had already degraded" is not
an available explanation for the merger arms' deaths** — whatever kills them is
local, and it is invisible to every norm we currently compute (which is a
Level-0 volume-diluted number anyway, see the L2-norm note under #16).

**Mode B — slow global exponential accuracy loss, run survives well past it.**
The wide, high-momentum arms that never merge:

  arm                     floor    at t    100x by   ran to   Ham at end   e-fold
  p = 0.25               2.39e-03  32.7      52.8      53.0     1.17         5.3
  p = 0.35 (no merge)    2.21e-03  36.1      67.7      73.9     0.506        6.0
  p = 0.45 (no merge)    2.15e-03  34.2      76.3      91.0     1.26         8.3

Here the degradation is real, smooth, and enormous: p = 0.45 ends 584x above
its own floor.  Note the ordering — the e-fold time *lengthens* with the width
of the encounter (5.3 -> 6.0 -> 8.3), i.e. the closer the throats come the
faster the global accuracy is lost.

**The separation control confirms the mechanism.**  Four at-rest arms, a and m
identical, ONLY the gap changed (#8b ladder), measured over one common window
t = 0 -> 11.5 so nothing else can differ:

  d = 12    growth 1.46x    e-fold  43
  d = 14    growth 1.40x    e-fold  60
  d = 16    growth 1.33x    e-fold  85
  d = 18    growth 1.28x    e-fold 120

Perfectly monotonic.  The degradation rate is a function of separation, and at
these separations it is mild — a factor 1.3-1.5 over 11.5 units, nothing like
the 100x of Mode B.  So Mode B is not "binaries degrade"; it is specifically
the close, fast, high-momentum passage that does it.

**Missing control — the isolated throat.**  The withdrawn table carried a row
"single throat (static), no 3x crossing in 40 units".  That row could not be
re-sourced in this pass: every `checkE_single_*` directory holds a single-line
convergence probe, and no long isolated-throat history exists anywhere under
`runs/`.  It is therefore NOT an established result and must not be cited.
It is also the cheapest missing control in the campaign — one throat, level 3,
t = 40, one card, ~4 h — and it is the only thing that separates "our initial
data is fine and the binary setup is what degrades" from "everything degrades
and the binary is merely faster".  Run it before the paper launch.

**What this changes:**

1. **The merger claims are not invalidated by constraint growth.**  They are
   measured on arms whose constraints are at their floor when the run ends.
   This is the opposite of what the previous version of B1 said.
2. **The fly-by "control" is the degraded one**, by two to three orders of
   magnitude, at exactly the late times where we read its waveform.  That is
   B2's problem, and B1 is now evidence *for* B2 rather than a separate issue.
3. **The open question is Mode A, and it is not a constraint question.**  A run
   that dies with a falling Hamiltonian is dying at one point, not everywhere.
   Until we know where, "the simulation ends at t = 44.9" cannot be reported as
   a physical statement about the throats.  Finding it is a plotfile-local
   question (min lapse / max |K| / chi floor per level at the death step), not
   a norms question.

### B2 — the fly-by "healthy control" is neither healthy nor a fly-by

`merge_orbit_flip_d12_p045_t200`, quoted in the results README as *"healthy
with no NaN at all"*:

  t      L2_Ham     min lapse   max|K|    throat pit chi
  40    2.40e-03    7.26e-03     0.16        9.78e-05
  60    3.18e-02    9.45e-04     0.71        3.27e-04
  90    1.14e+00    6.21e-06     3.33        9.19e-04

- Hamiltonian violation grows **477x and reaches order 1**; the lapse collapses
  five orders; |K| grows 20x.  "No NaN" is not "healthy" — this run is
  diverging, it simply diverges slowly enough to reach t = 91.
- It is **not a fly-by**: the throats spiral from d = 12 in to separation 4.0
  by t = 40 and drift back out only to 6.4 by t = 90 (r_A = 5.97 -> 2.04 ->
  3.18, never above 6).  It is a bound, non-merging binary.
- **The throats dissolve with no merger involved**: the pit chi climbs
  3.5e-07 -> 9.2e-04 over the run.  Whatever eats these throats does not need
  a merger to do it.
- **README ACTION REQUIRED**: the claim "give the pair enough angular momentum
  that it never merges and the evolution is healthy with no NaN at all" is
  false as written and must be corrected before anything is published.

### B3 — the Psi4 blow-up at R = 14 is the solution, not the extraction

Previously hand-waved (including by me) as "the fly-by's throats cross the
extraction sphere".  They do not — they never exceed r = 6.  The R = 14 sphere
is sampling a diverging interior; R = 30 looks calm only because the sponge
(24–32) damps it.  Any waveform quoted from a time when B1/B2 say the run has
turned is measuring the divergence.

### B4 — the fly-by radiates HARDER than the merger, and neither chirps

Psi4, l = 2, extraction R = 14, largest excursions per epoch:

  merger arm p = 0.12 :  +0.0135 (t=18.5)   +0.0292 (t=55)   -0.0258 (t=73)
  fly-by     p = 0.45 :  -0.0215 (t=29.5)   -0.0490 (t=37.5) -0.0303 (t=69)

- Over t = 0–25 the two are **superposed** — same shape, same phase, same
  amplitude — despite p = 0.12 vs p = 0.45.  Two different orbits cannot
  radiate identically; whatever dominates that window is not orbital.
- In the clean window the **non-merging arm radiates ~1.7x harder** than the
  merging one.  Nothing in the merger arm's waveform can be attributed to a
  merger while that is true.
- Across the full stitched history t = 0 -> 97 there is **no chirp and no
  ringdown** — no epoch where the amplitude grows and then decays.
  Figures: `results/merger/figures/gw_merger_full_history_0_97.png`,
  `gw_merger_vs_flyby_full.png`; stitched stream
  `results/merger/psi4_merger_stitched_0_97.dat` (r03000 joined 0–50.5 |
  m9b_fillwide80 50.5–79.5 | m9b_fillwide100 80.5–97, both restarts
  continuous across the seam).

### B5 — the death time is set by numerical parameters

Same seed, same physics, one knob at a time:

  floor 1e-10, level 3  ->  dies t = 44.95   (chi = 6.6e-06, far above floor)
  floor 1e-8,  level 3  ->  dies t = 51.53   (chi = 1.0e-08, ON the floor)
  floor 1e-8,  level 5  ->  dies t = 55.53

The longer-lived run was being **held up by the floor** — its geometry pinned
against the clamp.  Death time spans 44.9–55.5 across two purely numerical
knobs and converges on nothing.  The decisive missing point is a **level-4
restart from the t = 50 seed already on disk**: if the sequence flattens
toward ~56 the singularity is physical and no resolution ever fixes it; if the
spacing stays even it is numerical.  One run, a few hours.

### B6 — the test of whether the late accuracy loss is an initial-data artefact (IN FLIGHT)

B1's Mode B says the wide arms lose accuracy exponentially, e-fold 5-8 units,
reaching 584x by t = 91 in p = 0.45.  Two explanations, with opposite
consequences for the paper:

- **Artefact** — plain superposition of two Ellis-Bronnikov throats is not a
  solution of the constraints, and the initial violation grows.  Fixable:
  better initial data, and the late waveform becomes usable.
- **Intrinsic** — the throats themselves carry a growing mode.  Not fixable by
  initial data, and no amount of resolution rescues the late signal.

`merge_orbit_flip_d12_p045_helfer_t090` (launched 2026-09-04, card 1) decides
it.  Two lines differ from `merge_orbit_flip_d12_p045_t200`, verified by diff:
`wormhole_helfer_correction = 1` and `stop_time = 90.0`.  The existing plain
twin ran to t = 91, so it is an exact control at zero extra cost.

*(The Helfer correction is REJECTED for production, §1 line 745 — it stalls
mergers because the mass lives in the lapse rather than the conformal factor.
That objection does not apply to a fly-by, which never merges.  This run is a
diagnostic, not a production candidate.)*

**WITHDRAWN — the early "leaning INTRINSIC" reading (2026-09-04).**  It was
built on the helfer/plain ratio at four sample times (1.13, 1.22, 1.78, 1.59 at
t = 0/4/8/10) read as a widening gap.  **That statistic does not exist.**
Sampled every 0.1 units to t = 30 the pointwise ratio runs from 0.02 to 18.3 —
a 940x swing in the orbit pair, and 127000x in the twin pair.  The L2 Hamiltonian
norm spikes by an order of magnitude on regrid steps in BOTH arms independently,
so their ratio is dominated by whether the two runs happened to regrid at the
same instant.  The 1.78 at t = 8 is one draw from that; so is the 0.20 at t = 24
that would have "proved" the opposite.  Same error the a-ladder made: one arm's
increment read without its error bar.

**The spike-insensitive version.**  Rolling 5-unit median of each series, then
the ratio of the medians:

  pair            t=0 ratio   median-of-ratio   ratio-of-medians @ t=30   band, t>10
  orbit p045        1.131          1.079                 1.133             0.63-1.37
  twin p012         1.129          0.781                 0.525             0.37-1.12

Three things follow, and two of them reverse what was written here before:

1. **The t = 0 cost of the Helfer correction is 13%, not 1.8x.**  Both pairs give
   1.13 independently, and t = 0 is deterministic with no regridding, so this is
   the one number here that is solid.  **Correct the "1.8x initial Hamiltonian
   violation" claim wherever it appears** — it came from reading a spiked sample.
2. **In evolution the correction is neutral-to-beneficial, not harmful.**  The
   orbit pair is a wash (medians 1.08-1.13, i.e. the 13% initial offset simply
   persists).  The twin pair is *better* with the correction — ratio of medians
   0.525 at t = 30, band 0.37-1.12.
3. So the evidence to date leans **ARTEFACT**, the opposite of the withdrawn
   reading, but softly: the twin band's upper edge touches 1.12, so the honest
   statement is "no worse, often better", not "halves it".

**RESULT — stopped by the user at t = 37.29 of 90, clean (zero NaN).**  The
signal is real and it starts at t ~ 30, which is why both earlier readings of
this run were wrong: the t <= 10 table was noise, and the "neutral to
beneficial" correction was made on data that stopped at t = 30, one unit before
the departure.

  t      helfer      plain     median-ratio
  20    2.44e-03   3.65e-03      0.73
  30    3.18e-03   2.21e-03      1.16
  33    6.99e-03   2.15e-03      1.56
  35    1.12e-02   2.15e-03      2.81
  37    1.59e-02   2.16e-03      4.88

**This one is not a ratio artefact: the denominator is constant.**  The plain arm
sits at 2.15-2.21e-03 across the whole t = 30-37 window while the corrected arm
grows 5x, e-folding ~4.3 units.  Final state t = 37.29: L2_Ham 1.66e-02, L2_Mom
5.53e-03, min_lapse 1.23e-03 (collapsing), min_chi 3.59e-04.

**Interpretation, and it is not "Helfer makes things worse".**  On the same day,
`single_hold_t100` showed an ISOLATED throat sitting still for 26 units and then
contracting exponentially (e-fold ~2.6-3.4, error profile peaked at the throat,
constraints flat).  The two clocks match: the single throat departs at t ~ 26,
this arm at t ~ 30.  The coherent reading is that **both are the same throat
instability**, and the Helfer correction is not a small fix but a ~9.5%
perturbation of each throat's initial size — an enormous seed for an unstable
equilibrium compared with truncation error.  So it reaches the mode sooner.

That resolves B6's original question in a way neither branch anticipated: the
late accuracy loss is neither an initial-data artefact nor a binary effect.  It
is the constituent's own instability, and better initial data cannot fix it
because the object being prepared is itself unstable.  **Do not spend the
GRTresna constraint-solve on this until Stage 0 finishes** — see
GPU_PLAN_UPDATED.md.

**Caveat.** Stopped 13-33 units short of the t = 50-70 verdict point, so the
t > 30 departure is 7 units of data, not a converged rate.  Chk03000 (t = 30,
the departure point) is held on scratch as a restart seed, with the t = 36/36.5/
37 plotfiles, so the "where does the violation live" question can still be asked
without re-running.  The statistic rule stands: ratio of rolling medians with its
band, never a pointwise ratio at a named time.

### What this blocks, and what it does not

**Blocks:** any production launch whose purpose is to measure the merger, the
common horizon, the throat contraction rate, or a merger waveform.  Running
the same initial data at L = 128 and level 5 buys resolution, and B5 says
resolution moves the death time without converging it — so a production run
today would produce a more expensive version of the same unusable late-time
data.

**Does not block:** the inspiral before the turn (t < ~30), the repulsion /
sign-rule results (#8, rest-release arms all finish by t = 15, far inside the
clean window), the initial-data validation, and the separation ladder (#8b,
CLOSED 2026-09-04 — all four rungs clean to t = 15, constraint growth 1.28-1.46x,
nothing like Mode B).  Those are unaffected by everything above.

**Order of work before any paper launch:**
1. Level-4 restart from the held t = 50 seed (B5) — decides physical vs
   numerical death.  Cheapest, most decisive.
2. A real MOTS finder (CRITICAL BUG P3) — decides whether a common horizon
   forms at all, which is the only definition of "merger" available here.
3. Only then choose production parameters.  If B5 says the death is physical
   and P3 finds no common horizon, the honest paper is *"exotic matter
   prevents these wormholes from merging; the binary degrades and the
   collision goes singular"* — and it needs no production run at all beyond
   what is already on disk.

---

## 0. The plan

**In flight**

- [x] **#1 p015 scout — ANSWERED 2026-09-03: p = 0.15 is on the FUSING
  branch, but the wall cut it short of coincidence.**  Died t = 53.35 (h11
  NaN, level 3 — the wall, slightly late).  The sequence, slice-audited
  (tracker + slices agree): plateau at pit sep 0.816 (p012's plateau was
  0.815), dive to 0.69–0.70 by t = 50.5–53.0, core lapse RISING 0.13 → 0.21
  (p012's endgame signature; p020 never showed any of this — it hovered at
  1.08 with falling pit lapse), χ on the floor from t = 50.5.  But the pits
  never closed to p012's 0.2–0.6 coincidence: fusion was in progress, not
  complete, when the wall hit.  Production implication: p = 0.15 is a real
  candidate but needs the restart-refinement recipe (#17-style, wall
  pushed ~+1.4/level) or a later-armed fill to finish; p = 0.12 remains the
  proven IVP.  Checkpoints were LOST (uninsured name — sweeper rule now
  fixed to cover all p-scan names); the last 3 plotfiles (t = 52.0/52.5/
  53.0, post-dive) are HELD on scratch for the horizon scan alongside
  p020's.  **RERUN with insurance (2026-09-04):**
  `merge_orbit_flip_d12_p015_rr_t060` (card 0, identical template)
  reproduced the wall at **t = 53.35 — the very same step (5335) as the
  original: the wall is deterministic at this resolution** — and this
  time the checkpoints survived:
  **Chk05000 (t = 50) held** plus a sweeper-proof `hold_seed_t50` hardlink
  copy — the seed for phase 2 (restart at max_level 5, ~+1.4 wall units
  per level, aiming the wall past the ~53–54 fusion completion).  Its own
  death plotfiles (t = 52.0/52.5/53.0) held too.
  (Superseded queue text kept below for the record.)
- [~] *(was)* **p015 scout** — `merge_orbit_flip_d12_p015_nofill_t060`, card 0.
  Does p = 0.15 fuse before the t ≈ 52 wall?  Fuse → production-p candidate
  (~10–15 % more m = ±2 signal, longer whirl); hover like p020 → the
  "captures but cannot fuse" boundary moves down to 0.15 and p = 0.12
  stands.  Reference marks: p012 crossed sep 2.0 at t ≈ 32 and fused by
  48–51; p020 hovered at 1.08; the wall ≈ 52.  Sub-2 separations are a
  tracker artifact — read the slices.  Last read t = 34.3, sep 1.69: no
  call yet.
- [x] **#2 BBH control to t = 150 — DONE (2026-09-03), all four close-out
  checks pass.**  `bbh_control_d12_p012_t150` reached t = 150 on card 2.
  (1) Instruments agree: Python consumer (plotfiles, fixed center) vs
  in-code stream match to 0.31 % / 0.35 % of peak (R = 14 / 30), corr
  0.999999 — the center bug is retired.  (2) Known-answer ringdown: fitted
  period 28.8–29.7, damping tau 25–27 (late-window 28.9 / 22.9), i.e.
  ~15.2 M / ~12.1 M for M_f ≈ 1.9 — consistent with a Kerr remnant of
  M ≈ 1.9–2.0 with modest spin (Schwarzschild reference 16.8 M / 11.2 M;
  spin shortens the period exactly as seen).  Both radii agree within
  3–7 %.  (3) Boundary audit at t = 150 (full-domain plotfile scan +
  slice-cache time series): chi scatter *decreases* outward (0.33 % →
  0.26 %), max |K| in the outer shells 4e-4, no growing ripples —
  Sommerfeld held for 150 units with no sponge; pre-signal junk floor at
  R = 30 is 12 % of peak but sits entirely before the chirp, and R20→R30
  envelope coherence bounds in-band contamination at ~3.5 %.  (4) Signal
  comparison at equal R = 14: BBH peak (2,2) 1.08e-2 vs wormhole p012
  2.49e-2 — the wormhole is ~2.3x louder (understated: the twin stream
  cut at t = 44, before collapse finished radiating).  Remaining: repack
  + paper figures with R = 30 (after the drain completes).

**Next — cheap, no GPU conflict, one approval each**

- [x] **#3 p012 horizon re-check — ANSWERED (2026-09-04): the offline scan
  confirms the trapped shell at r ≈ 1.**  Run on the nodamp twin's held
  death plotfiles (twin ≡ plain per #14; level 3): outermost fully-trapped
  shell r = 1.11 / 1.09 / 1.07 at t = 50.5 / 51.0 / 51.5, vs the in-code
  refined-run r = 1.0 at t = 51.06 — a different run, different resolution,
  different implementation, same verdict.  The standing caveat stands
  unchanged: both instruments read the same chi-clipped state, so this is
  supporting, not decisive — the decisive word is the from-t = 0 low-floor
  twin (nodamp_cf10, in flight).
- [x] **#4 p020 horizon scan — ANSWERED (2026-09-04): p = 0.20 has a
  credible common trapped surface, larger than p012's.**  All 3 held
  plotfiles scanned (CLI variant of `ah_radial_scan.py` added:
  `--center/--half/--level`, defaults unchanged for the pack script):
  outermost fully-trapped shell r = 2.07 / 2.11 / 2.13 at
  t = 51.0 / 51.5 / 52.0 (ray-mean r_AH 2.72–2.74, 78 % of rays).
  Credibility checks PASS where helfer/p035 failed: K on the r = 2.1 shell
  is 0.04 mean / 0.13 max — nowhere near the K ≈ 1 blob rim — and the
  shell sits in healthy data (chi ≥ 0.10, lapse ≥ 0.09, five orders above
  the floor), unlike p012's shell.  Plotfiles NOT deleted yet: #13
  explicitly needs these same 3 files — delete after #13 runs.
- [ ] **#5 L = 128 / N = 256 smoke test** — t = 5; measures memory (~75 GB
  estimate, tight) and speed; decides L = 128 vs the L = 96 fallback (§4).
- [x] **#6 Production templates — DONE (2026-09-04, params-only, nothing
  launched).**  `templates_scan/params_prod_L128_p012_t060.txt` (headline)
  and `params_prod_L96_p012_t060.txt` (s4 fallback: sponge 40→48, radii
  20/26/32/38), both derived from the smoke template whose extraction
  block (radii 20/28/36/44, levels 0, l ≤ 4 all m, points 24/37) the live
  smoke run is validating right now; production deltas: stop_time 60,
  checkpoints ON every 10 units keep 3, probe key dropped.
  `launch_production_L128.sh` carries `--scalar-modes 0 1 2` in
  `WHM_CONSUME_ARGS` (the s4 non-vacuum-exterior defence) and a VARIANT=L96
  switch; both variants dry-run clean.  Launch gated on the #5 memory
  number and explicit approval.
- [ ] **#7 Launcher hardening** — `run_single.sh` falls back to the grid
  centre or refuses to start when the params has no `center` key (the
  consumer-junk bug, §1).  Only after the current runs end — the script is
  live under two launchers.
- [x] **#8 Repulsion a-points — ANSWERED 2026-09-04: the push is real and
  grows with throat width at every rung, but the a² magnitude law
  OVERSHOOTS, by 2.2× at a = 3.**  `ctrl_rest_a15` and `ctrl_rest_a3` both
  reached t = 15 clean (zero NaN, L2_Ham 6.3e-3 / 2.6e-3), giving four
  rest-release arms byte-identical but for the radius.  New tool
  `apoint_repulsion.py`, validated by reproducing both archived numbers
  (+0.0042 → +0.00441, +0.0127 → +0.01274) before it was pointed at the
  new arms.

  Displacement by t = 11 (the robust statistic — no differentiation, no
  fit window): 0.147 / 0.283 / 0.416 / 0.615 for a = 1 / 1.5 / 2 / 3, i.e.
  ratios 1.00 / 1.92 / 2.82 / 4.18 against the predicted a² = 1 / 2.25 /
  4 / 9.  Ratios stable to a few per cent at t = 6, 8, 10, 11 and
  insensitive to the centroid window (±1.5, ±3, ±5 agree to 2 %).  Fitted
  exponent ≈ 1.36 and *falling* (local slope 1.58 → 1.27), so it is not a
  clean power law but a flattening one.

  **Methodological warning for anyone re-using the archived statistic:**
  the quadratic-coefficient "acceleration" over a fixed window is NOT
  stable — a = 3 reads 3.93 / 4.52 / 8.91 relative to a = 1 on windows
  6–10.5 / 3.5–10.5 / 8–14.5, because by t = 10 the arms sit at different
  separations and the force is being sampled at different distances.  The
  formal ±0.0003 fit errors understate this by two orders.  Quote
  displacements at matched times, not accelerations.

  Systematics: under-resolution is ELIMINATED — both new throats sit on the
  finest level, 48 and 96 cells across the throat width, so the widest arm
  is the best resolved, not the worst.  What survives is the coordinate
  under-read (which does not cancel between different widths) and genuine
  finite-size correction to a point-charge formula at a/d = 0.25.  Four
  like-charge arms cannot separate the two.

  **Follow-up that decides it (~2 GPU-h each, not launched):** flip arms at
  a = 1.5 and a = 3.  Within one width the under-read cancels, exactly as
  it did at a = 2 (1.511 ± 0.033 measured vs 1.500 predicted), and the
  predictions |infall|/|escape| = (1+R)/(R−1) are far apart: 1.889 at
  a = 1.5 and 1.222 at a = 3.  If they land, the law is right and the
  shortfall is all coordinate; if not, (a²+m²)/m² needs revisiting at
  finite size.  Full measurement and systematics:
  `results/merger/scalar_charge_apoints_2026-09-04.txt`.
- [x] **#8b Separation ladder — ANSWERED 2026-09-04: the force is
  inverse-square in an EFFECTIVE separation, d + 3.5, not in the coordinate
  separation.**  Four rest-release pairs at d = 12 / 14 / 16 / 18, a = 2 and
  m = 1 held fixed, params diffed to confirm only the centres differ.  The
  three new rungs all reached t = 15.01 clean (zero NaN).  Displacement at a
  common t = 11.5 (window set by d = 12, which only ran to t = 11.8):
  0.4696 / 0.3699 / 0.2980 / 0.2438.

  Why this ladder and not the a-ladder: `a` is a coordinate label whose
  physical meaning moves as you turn it, so #8 could never isolate the law.
  Fixing the throat and varying only the gap makes the coordinate distortion
  identical in every rung, so it cancels in the ratios.

  1. **Pure 1/d² is excluded.**  F·d² rises monotonically 67.6 → 72.5 → 76.3
     → 79.0, a 15.4 % spread — the push falls off *more slowly* than
     inverse-square.
  2. **F ∝ 1/(d + δ)² with δ ≈ 3.5 fits.**  All six rung pairs: 3.77 / 3.67 /
     3.47 / 3.54 / 3.27 / 2.95.
  3. **Blind prediction, confirmed.**  δ = 3.4 was fitted on d = 12/14/16
     alone, before d = 18 reached t = 11.5.  Predicted there: 0.243 (offset)
     vs 0.209 (pure 1/d²).  Measured **0.2438** — 0.3 % from the offset model,
     17 % from inverse-square.
  4. **δ ≈ 3.5 ≈ the measured throat radius 4.29** at a = 2.  The deviation is
     in the distance label, not the law: these are extended objects, and the
     coordinate centre separation understates the physical one by about a
     throat radius.

  This also **favours the finite-size branch of #8's open question** — the
  a-ladder's shortfall was either coordinate under-read or finite-size
  correction to a point-charge formula, and here is a finite-size correction
  of exactly the expected size, measured at fixed width.  The flip-arm test
  above is still what settles #8 itself.

  **Is it just because the throats are moving?  No — dynamics biases the
  wrong way.**  Over the window the d = 12 pair separates by 3.9 % and the
  d = 18 pair by 1.35 %, so the close rung's force weakens more *during* the
  measurement.  That makes the apparent falloff *steeper*, i.e. pushes the
  result toward 1/d².  We measure shallower than 1/d² regardless, so the true
  δ is if anything larger than quoted.  The effect is a static property of the
  initial data (extended sources), not a dynamical artefact.

  δ is not perfectly constant — it trends 3.77 → 2.95 as the pairs widen — so
  the offset model is an approximation, not exact.  Full measurement and
  systematics: `results/merger/separation_ladder_2026-09-04.txt`.

  **WHAT THIS MEANS FOR THE PAPER**

  1. **A defensible headline claim, gained.**  "The repulsion between
     like-oriented drainhole throats is inverse-square in an effective
     separation exceeding the coordinate separation by about one throat
     radius."  Quantitative, falsifiable, and *cheap for a referee to
     reproduce* — level 3, ~1 GPU-h per rung, four rungs.  The blind
     prediction is the strongest single number in the repulsion section and
     should be stated as one: the law was fitted on d = 12/14/16 and the
     d = 18 point was predicted before it was measured.
  2. **The a² claim, lost.**  The width law stays unverified (#8).  The paper
     quotes displacements per width and does not assert a².  The flip-arm
     test at a = 1.5 and a = 3 is what would settle it.
  3. **Wording is now fixed — do NOT write "violates the inverse-square
     law".**  That invites the referee to ask what new physics is being
     proposed, and the honest answer is none: the deviation is in the
     distance label, not in the law.  Write that it is inverse-square once
     the distance is measured between the sources rather than between
     coordinate centres.
  4. **The known exposure — resolution.**  All four rungs are level 3, so a
     resolution error common to the ladder cancels in the *ratios* (which is
     what is claimed) but survives in the *absolute* displacements (which are
     not).  Say so explicitly rather than waiting to be asked.  If a referee
     presses on convergence, one rung repeated at level 4 answers it — a few
     GPU-h, and it is the single cheapest defensive run in the campaign.
- [x] **#9 Wave-8 close-out checks — ANSWERED (2026-09-04): the second
  peak is a real outgoing wave, and the tail past the ceiling is clean.**
  (a) The R = 14 second peak (t = 75.1, rΨ₄ = +1.63e-2) reappears at
  R = 30 at t = 94.0 — delay 18.9 vs the wave-7 main-signal lag 18.0 —
  with rΨ₄ ratio 1.085 vs 1.0 for pure 1/R (R = 30 is in-sponge; shape
  and timing only, per the wave-8 caveat).  Identical in both arms.
  (b) Tail past the causal ceiling 84.5: the seam-radius twins (fill vs
  fillwide) agree to 0.09 % of the tail peak, corr 1.000000 — the tail is
  not seam-written; the R = 30 late data is usable.

**Credibility tests — run BEFORE any production launch.**  They decide
what the production arms are allowed to claim.  All level-3 runs or short
restart segments, ~1 day of one card total.  (2026-09-04: two t = 50 seeds
now exist — nodamp Chk05000 for #16, p015_rr Chk05000 for the p015
phase-2 refinement — both with sweeper-proof hold copies on scratch.)

- [x] **#13 Blob nature test — ANSWERED (2026-09-04): the blob is a
  genuine slicing-regularized negative-energy structure, not a constraint
  mode.**  Tool: `grteclyn-wrapper/scripts/validation/blob_nature_scan.py`
  (offline, from the raw CCZ4 state: ρ with the code's exact
  ExoticScalarField convention, Hamiltonian constraint with an FD Ricci,
  areal radii, Eulerian energy flux j·s; raw output packed under
  `results/merger/horizon/`).  Run on the held p020 trio (t = 51–52) and
  the cf08 trio (t = 54.5–55.5), with a level-3-vs-4 depth check.
  (a) **p020 blob**: Ham violation 1–3 % on every shell, 3-Ricci bounded
  (−0.4 to −1.0) and static while the lapse sits at 4e-3 — the plan's own
  discriminator reads SLICING, not constraint mode, not a singularity.
  ρ < 0 concentrated at the midpoint (−1.7e-2 shell mean; −3.4e-2 center)
  and the throat ring (pointwise −1.2); the coordinate ball r ≤ 0.9 hides
  areal radii up to ~35 — the folded drainhole interiors, a bag-of-gold
  geometry.  The "negative-energy sink between the throats" hypothesis is
  MEASURED as presence + concentration; "sink" as accretion needs #12's
  balance integral.
  (b) **cf08 collapsed core**: outside the needle pit (r ≳ 0.3 at scan
  level 4) constraints are 3–7 % and curvature bounded; the pit interior
  itself is a floor-regularized junk region ≲ 0.3 wide (level-3 FD across
  it fakes R ~ 1e9; at level 4 the same shell is clean — scan artifact).
  ρ < 0 is concentrated exactly at the horizon ring r ≈ 0.9–1.2
  (pointwise to −0.9, three orders above ambient), the net Eulerian
  energy flux through r = 0.9 is outward (+2.6 → +3.3 over the last
  unit — the enclosed mass DECREASING, consistent with the shrinking
  shell), and the interior bag's areal radius collapses 25.6 → 19.1
  (−22 %) over the same unit (level-3 magnitudes; trend robust across
  same-level snapshots).  Kretschmann: not derivable at acceptable cost —
  |Weyl4| + FD 3-Ricci stand in, both bounded.
  README consequence: the mechanism's INGREDIENTS (negative-energy matter
  present and flowing at the shrinking horizon) are now measured; the
  full energy/mass balance stays #12, and everything remains gated on the
  nodamp_cf10 floor test.  p020 + cf08 held plotfiles are KEPT for #12's
  balance integral (manifest updated) — delete only after it runs.
- [x] **#14 Damping-off p012 plain twin — ANSWERED (2026-09-04): damping
  changes nothing that matters.**  `merge_twin_p012_nodamp_t060` died at
  **t = 51.53** (h11 NaN, level 3) vs the plain twin's 52.06 — the wall
  moved by 0.5 units (~1 %), within the arm-pair noise floor, so damping
  neither causes nor delays the wall.  Pre-collapse the twins are
  numerically indistinguishable: at t = 32 sep/mid-lapse/|φ|/activity all
  match plain to 3 decimals (files verifiably different, max |Δφ| = 0.0056).
  Verdict: every scan/twin result stands as-is with damping off, and the
  production config (damping off) is now measured, not assumed.  Assets
  held: **Chk05000 (t = 50) — the #16 ladder base** — plus a sweeper-proof
  `hold_seed_t50` hardlink copy; death plotfiles t = 50.5/51.0/51.5 on
  scratch; in-code streams complete to 51.53.
- [x] **#15 Gauge-change arm — ANSWERED (2026-09-03): the physics
  survives the slicing change, the WALL TIME does not.**
  `merge_twin_p012_lc1_t060` (single knob: lapse_coeff 2.0 → 1.0) died at
  **t = 43.64** (K NaN, level 3) vs the plain wall at 52.06 — the wall
  moved **8.4 units earlier**, which is the pre-registered "gauge" branch
  of the test.  But the physics sequence held: blob nucleated on schedule
  (t = 32 slice: mid lapse 0.009, |phi| 0.53 — deeper/stronger than
  plain, as a slower lapse response should give), capture and plunge
  proceeded, sep 0.442 at death.  Reading: the crash is the slicing
  losing its singularity-avoidance race (halving lapse_coeff weakens the
  gauge's protective collapse, so the code meets the forming singularity
  ~8 units sooner) — **the t ≈ 52 number is a property of gauge +
  resolution, not a physical event, and the paper must never present it
  as one.**  The physical claims (blob, capture, fusion sequence) are
  what survived; p012's headline is untouched (its fusion completed at
  48–51, before its wall).  Assets held: Chk04000 (t = 40), death
  plotfiles t = 42.5/43.0/43.5, in-code stream complete to 43.64.
  (Wave 3a tested the source term, not the slicing — different question.
  The shock-avoiding lapse f = 1 + kappa/alpha^2 would need code; not
  worth it now that the params-only arm has answered.)
- [x] **#16 χ-floor ladder — ANSWERED (2026-09-04), and the answer is a
  warning: the restart route CANNOT certify floor-independence.**  Ladder
  run off the nodamp t = 50 seed with levels 4–5 added: cf10 (min_chi
  1e-10) NaN at t + 0.049 on the new level 4; cf12 (1e-12) NaN at
  t + 0.006 on level 3; cf08 (floor unchanged at 1e-8, same added levels)
  ran healthily to **t = 55.53** (h11 NaN, level 5) — a clean one-knob
  attribution, and the longest-lived p012-family arm on record (previous
  deaths 51.7–55.0).  Its close-out (2026-09-04): death window NaN-free,
  and the offline scan of its held plotfiles at **level 5** finds a
  fully-trapped shell r = 0.94 / 0.92 / 0.90 at t = 54.5 / 55.0 / 55.5 —
  shrinking slowly, NOT accelerating — that passes the §9 rim filter
  (on-shell chi ≈ 0.5, lapse ≈ 0.6, K ≈ 0).  **CORRECTED 2026-09-04.**  This
  block previously carried a WARNING that the same file scanned at level 3/4
  showed no trapped surface, and concluded that a scan-depth systematic made
  0.59 and 0.92 incommensurable.  That was the coarse-level covering-grid bug
  (see CRITICAL BUG BEFORE PRODUCTION RUN, Defect 1), not physics: after the
  fix the shell reads 0.920 / 0.920 / 0.940 at levels 5 / 4 / 3, so it is
  resolution-robust and the systematic is WITHDRAWN.  What replaces it is
  Defect 2, which is worse for the claim: on this arm and on nodamp the
  trapped shell sits INSIDE the throat's areal-radius minimum, exactly where
  an uncollapsed throat also reads as trapped, so these shell radii may not be
  quoted as a horizon at all.  The gauge-independent replacement is the
  minimum areal radius, 4.128 → 4.085 over t = 54.5 → 55.5 (−1.0 %/unit).
  Verdict: **the t = 50 collapsed-core state is floor-regularized** —
  releasing the floor on it is instantly fatal, so no restart-based ladder
  can separate "the horizon is real" from "the horizon is the floor".
  The decisive test moved to the from-t = 0 twin at min_chi 1e-10
  (`merge_twin_p012_nodamp_cf10_t060`, in flight): if it reproduces the
  blob, wall and horizon, the claim is floor-independent and the §8.7
  hedge comes off; if it diverges, the horizon sentence leaves the paper.
  Until then every horizon/dissolution number is written as contingent.
- [ ] **#17 p020 restart-refinement** — the only version of "does p = 0.20
  fuse" that tests what it claims: fresh L3 p020 to t ≈ 50 with insured
  checkpoints (~5.5 h), then levels 4–5 added at the checkpoint — the m4e
  recipe that bought the p012 family +1.4 units of wall per level.  The
  from-t = 0 L5 arm got none of that gain (χ clipped at the pits at t = 0,
  §9).  This run rescues — or honestly kills — the capture-boundary
  figure; same recipe p015 needs if it hovers.  (2026-09-04: #4's offline
  scan already finds a credible L3 common trapped shell at r ≈ 2.1 in
  p020 — the boundary figure starts from strength.)

**Production — blocked on the open decisions (§8)**

- [ ] **#10 Headline arm** — p = 0.12 plunge at L = 128, max_level 5,
  extraction per #6; plus seam twin, third-fill-radius arm, level-6
  companion (§4–6).
- [ ] **#11 Comparison arms** — head-on freeze arm (§7.1); N = 192 wave-zone
  twin (§7.3) and the +150 tail if taken (§8).

**Analysis once the data lands**

- [ ] **#12** 4-radius extrapolation in retarded time (measured speed
  1.125×); **proper separation** — integrate ~χ^(-1/2) along the pit axis
  from the slice cache, the invariant answer to "static or still closing"
  that coordinate sep 1.08 cannot give; energy/mass balance with the
  negative scalar flux (§7.2);
  remnant-mass QNM discriminator (§7.4); dissolution re-measured on the
  undamped arm (§7.5); frames re-rendered with colour limits taken outside
  r = 3 (Plan.md issue 17); **causal-diagram figure** — light cones from
  the freeze seam vs the R = 14/30 extraction windows, the freeze defence
  in one picture (review suggestion 2026-09-04); **radiated-energy
  integrals** — flyby burst vs merger chirp+ringdown: the peaks say the
  flyby wins (§2), the energy integral is the merger's rebuttal and nobody
  has computed it; **event-horizon tracer on the production plotfile stack**
  (user suggestion 2026-09-04) — null rays through the wrapper's
  `EvolvingMetricField` (the f_geo_evol machinery): the last outgoing ray
  that escapes IS the event horizon, the slicing-independent answer the
  Theta scan cannot give.  Needs the run's FUTURE on disk — dense plotfile
  cadence over the whole window — so it is a production-run deliverable,
  useless on the 3-file death stacks; mind the env-var trap
  (`score_evolving_geodesic.py` silently wrong in default search mode);
  pack + push.

**Minimum publishable set** if the clock runs short: headline arm + seam
twin + level-6 twin + BBH control (done) + head-on.

---

## 1. Decision ledger — settled, with the number that settled it

- [x] **Production p = 0.12** (user, 2026-09-03).  Only p that completes a
  merger: p020_nofill died at t = 52.08 with the throats pinned at sep 1.08
  from t = 46, never fused (slices at t = 46/49.5: two intact cores,
  |φ| = 0.87, midpoint collapse deepening).  p015 (#1) is the one live
  challenger — a fusing p015 upgrades the choice, a hovering one confirms it.
- [x] **The t ≈ 52–53 wall is resolution-independent.**  Level-5 vs level-3
  deaths: p020 52.07 / 52.08, p025 52.79 / 52.98 — same h11 NaN, and the L5
  slices show two intact throats (|φ| ≈ 0.92, pit lapse ~0.18) with the
  inter-throat midpoint collapsing (lapse ~3.5e-3, max|K| 0.6–0.7).
  From-t = 0 depth does not move the wall; "p ≥ 0.20 does not fuse before
  the wall" is established on two independent p's.  Validated per arm:
  monitor death event + the run's own abort log + stream last row.
  **Caveat (second-pass review, adopted):** the from-t = 0 L5 arms are not
  a clean refinement rung (χ clipped at the pits at t = 0) and both died
  with the NaN on level 4, not the finest level; the restart-refinement
  recipe that bought the p012 family +1.4 units/level was never applied to
  p020.  Until #17 runs, "captures but cannot fuse" describes a NaN, not
  physics, and the capture-boundary figure is not publishable as a
  boundary.
- [x] **Helfer/Ning correction REJECTED for production.**  The decisive
  twin: plain merged (retraced the p012 record, sep 0.81 by t = 44); helfer
  stalled at sep ≈ 4.7 (7° of orbit over t = 26–34 vs plain's 35°),
  converged at L3 = L4 (< 2 % lapse-trace agreement).  Mechanism (§9): the
  midpoint lapse-collapse blob nucleates 5 units earlier (3e-2 at t = 25.4
  vs 30.4) and the throats stall against it.  The w = 2 window test killed
  the placement excuse (sep 5.22 at t = 32.0 — worse than the wide window);
  helfer_lvl5 was stopped at t = 31.5, stalled like L3/L4.  The flag stays
  in the code, default off.  Production runs plain superposition; the
  measured +8–11 % initial-size artefact is the price of an evolution that
  evolves.  Static trade recorded in §4.  **Mechanism (second pass):**
  du = −0.0834 = −M_B/d — the subtracted "constant" is the companion's
  Newtonian potential at the throat, so the windowed subtraction leaves a
  spurious potential shell at r ≈ w around each body, and the stall
  follows; w = 2 braking *earlier* than w = 4 fits (closer shell).  Paper
  wording: a correction designed for conformal-factor mass is inapplicable
  when the mass lives in the lapse; the honest alternative is a
  constraint-solved IVP, and the affordable substitute is the d = 16–18
  robustness arm (§8 decision 8).
- [x] **BBH vacuum control FINISHED CLEAN** (`bbh_control_d12_p012`,
  t = 100, no NaN; matched IVP: ADM ≈ 1 each, d = 12, p = ±0.12, wormhole
  box and spheres).  Vs the wormhole p012 twin: punctures met at t ≈ 70 vs
  throats fusing 48–51 — the scalar clouds buy ~20 units of faster infall
  (sep at t = 30: 10.3 vs 2.7); l = 2 m = 2 peak at r = 14: 0.0108 vs
  0.0249 (wormhole 2.3× brighter); m = 0: 0.0032 vs 0.0176 (5.5×); the
  Newtonian pericenter-at-43 guess was wrong — the plunge steepened through
  it.  Ringdown only ~4 % decayed by t = 100 → the t150 rerun (#2).
  Packed; figures from the C++ in-code streams (merger peak propagates at
  0.906c): `psi4_analysis_bbh_control{,_m2}` and the object-vs-object
  `bbh_vs_wormhole_psi4` from the new `grteclyn_wrapper.visualisation.merger`
  module.
- [x] **The consumer center bug — found and fixed.**  The BinaryBH params
  had no flat `center =` key; `run_single.sh` greps exactly that key for
  the consumer's `--center`, whose silent default is the DOMAIN CORNER
  (0,0,0) — the t100 consumer psi4 files are junk (static ~0.006 "modes",
  no rotating phase).  The C++ in-code stream is unaffected
  (`weyl_extraction.center` defaults to the grid centre), so every figure
  and quoted number stands.  Wormhole-side control on p020_nofill: C++ vs
  Python agree to 0.2 % (complex ratio 1.0022 − 0.0072i) — the chain is
  sound.  Both BBH params files now carry `center = 32.0 32.0 32.0`; the
  t150 run was killed 20 min in (user's word) and relaunched on the fixed
  params.  Launcher-side fix is #7.
- [x] **In-code extraction is the primary waveform instrument.**  Two ghost
  bugs fixed (interpolator ghost count 2 → 3; matter-sector derived
  functions never filled ghost cells — stale arena memory on ~55 % of
  sphere points), validated by a kernel printf count and a 1 776-point
  plotfile cross-check (0 plateaus, 0 NaN); mode integrals reproduce an
  independent Simpson quadrature to 1e-8 at both radii.  50× finer sampling
  than plotfiles (every coarse step, dt = 0.01).  The consumer Ψ₄ is
  demoted to cross-check; the code-only fix subset is submitted upstream
  from `fix/derived-ghost-cells`.
- [x] **Check E on the drainhole branch: d = 12 needs no apology, but the
  defect is real.**  d/b = 6 costs 1.58× the old d/b = 8 gate on a smooth
  A ~ d^-1.6 power law (no cliff in 4 ≤ d/b ≤ 12); Bowen–York momenta add
  1.9 %.  But the superposition defect (2.87e-4 at d = 12) sits 100–600×
  above the discretisation floor at every separation — over the refined
  region it, not truncation, is the dominant t = 0 error.  Table in §4.
- [x] **Capture boundary between p = 0.25 and 0.35.**  p ≤ 0.25 is captured
  (then hits the wall); p035 (min sep 2.75 at t = 42.4) and p045 (min sep
  3.95 at t = 40) are fly-bys with surviving throats (§3).
- [x] **max_level 5 for production, 6 as companion, 7 never by default**
  (m4e ladder, §5): pair-mean death ladder linear at +1.43/level against a
  ±0.35 reproducibility floor; refinement priced out as a route; damping's
  effect on death time is zero — production runs the clean config.
- [x] **Wording rule: "core freeze" → "inter-throat lapse collapse".**  The
  throats never collapse (pit lapse 0.05–0.24, |φ| 0.79–0.92, every run,
  every epoch); what collapses is the midpoint blob (§9).  The freeze
  module keeps its name; the physics claim changes.

**Withdrawn — do not re-import:** the 1/dx² initial-data-noise argument
(n160's own t = 0 row refutes it); the whole-domain `L2_Ham` as a
convergence metric (93.7–99.98 % of it lives in the 2-cell boundary-ghost
layer, §4); "death time bounded 56–57 over levels 5–7"; per-throat scalar
charge from check F (single throat, angular-mean estimator — cancels on the
flipped binary); the lighthouse mechanism (m = ±2 rings at 17.3, not 2× the
dipole precession, §6); "the cores collapse" (it is the midpoint, §9); the
p045 "common horizon at t = 43.3" (documented theta false positive).

---

## 2. Results in hand (the paper's spine)

| Result | Status |
|---|---|
| **Like-oriented throats repel** — 5× gravity at a = 2, m = 1; push scales with throat width, not mass; pull/push 1.50 vs 6/4 predicted.  The **a² magnitude law is NOT verified** (overshoots 2.2× at a = 3, #8) — quote the four displacements, never a² | three control arms, 2026-08-31; #8 measured 2026-09-04 |
| **The repulsion is inverse-square in an EFFECTIVE separation d + 3.5**, not in the coordinate separation — pure 1/d² excluded at 15 % across d = 12/14/16/18, and the offset δ ≈ 3.5 matches the measured throat radius 4.29.  Fitted on three rungs, then **blind-predicted the fourth to 0.3 %** (0.243 predicted, 0.2438 measured, vs 0.209 for 1/d²) | #8b ladder, 2026-09-04 |
| **Opposite-oriented throats attract and merge** — gravity-driven; common trapped surface at r ≈ 1.0 confirmed by two instruments (in-code refined run + offline twin scan, #3); p = 0.20 has its own, larger one at r ≈ 2.1 that passes the K-rim filter (#4) | #3/#4 closed 2026-09-04; floor-independence pending nodamp_cf10 |
| **The wall (t ≈ 52 death) is gauge + resolution, not physics** — one gauge knob moves it 8.4 units (#15); it reproduces on the identical step (#1 rerun); refinement pushes it +1.4 units/level; damping does not touch it (#14, Δ 0.5 units ≈ noise) | credibility batch, 2026-09-03/04 |
| **The merger's true peak is measured: \|rΨ₄\| (2,2) = 2.96e-2 at R = 14, t = 55.5** — ~3 units past the wall, via the freeze; R = 30 confirms (2.996e-2 at t = 73.5, lag 18, 1/R to 1.3 %); freeze arm matches the unfrozen twin to 0.7 % pre-wall.  L = 64 box — production re-measures clean | freeze chain, computed 2026-09-04 |
| **The interior freeze survives the merger; the signal is a genuine GW** — speed, 1/R falloff, static-offset and not-freeze-junk checks; second peak propagates 14 → 30 with the measured lag and clean post-ceiling tail (#9) | closed 2026-09-02; #9 2026-09-04 |
| **Same IVP, different object** — the wormhole merger beats the vacuum BBH by ~20 units of infall and 2.3× (m = 2) / 5.5× (m = 0) in brightness | BBH control, 2026-09-03 |
| **Flybys radiate a real GW burst, louder in raw peak than the merger** — p035 4.5e-2, p045 5.6e-2 (rΨ₄ (2,2), R = 14), both propagating 14 → 30 with the right delay; merger peak 2.96e-2.  Faster encounter, stronger bremsstrahlung burst; the merger's edge is the chirp + ringdown, not the peak.  Caveats: p045 R = 14 past t ≈ 70 is ejected phantom crescents crossing the sphere, not GW; t = 10–20 bumps are ID junk | computed 2026-09-04 |
| **p = 0.15 outradiates p = 0.12** — the lvl5 arm reached 3.14e-2 at t = 54.2, 6 % above p012's *complete* peak (2.96e-2) and still climbing at death, with no trapped surface formed yet; the fusing branch is the louder merger and its peak is still unmeasured | partial (wall-cut ×3); freeze continuation is the path to its full signal |

Freeze-method validation (the method section): the seam-radius twins agree
to 5 digits at every shared waveform sample; the frozen arm is bit-identical
to its unfrozen twin beyond r = 6 at t = 55; late engagement (55.5 vs 53)
moves the R = 14 window ≤ 0.003 % (m = 2) / 0.022 % (m = 0); constraints
stay flat for 27 units post-freeze.

---

## 3. The p-scan record

IVP family: d = 12, opposite orientation, tangential momenta ±p.  Circular
at d = 12 needs p ≈ 0.5 (measured 6× coupling); Newtonian escape ~0.7.

| p | run(s) | outcome |
|---|---|---|
| 0.12 | production family | merges: sep 2.0 at t ≈ 32, fusion 48–51 — the headline plunge |
| 0.15 | p015_nofill, p015_rr, p015_lvl5 | fusing branch, wall-cut mid-fusion three times: L3 wall at 53.35 (twice, same step); the levels-4–5 restart pushed it to **54.23** (+0.88) and STILL no fully-trapped shell (offline scan t = 54.0: 1 % of rays) while the waveform kept climbing (3.14e-2 at death, 6 % above p012's complete peak).  Refinement alone cannot outrun this wall — finishing p015 means the freeze (#1) |
| 0.20 | p020_nofill, p020_lvl5 | captured; hovered at sep 1.08–1.19; wall at 52.08 / 52.07 — cannot fuse |
| 0.25 | p025, p025_lvl5 | captured to sep ~1.5–1.9; wall at 52.98 / 52.79 — cannot fuse |
| 0.35 | p035 | fly-by: min sep 2.75 at t = 42.4, receding when stopped |
| 0.45 | p045 | fly-by: min sep 3.95 at t = 40, outbound at stop (t = 84); no checkpoints, not resumable |

p045 post-encounter physics (kept for the paper): the throats survive the
pass (φ lobes −2.5 % over 84 units; the χ wells relax, not collapse); two
χ > 1 phantom crescents are ejected; the cores deflect a quarter-turn.  The
transient stretch passes in ~10 units — the collapse branch wants the
sustained squeeze only a capture delivers.  Its `theta_common`/`ah_r_common`
columns carry the documented false positive; trajectory + matter + log-χ
frames are the instruments.  Figures: `results/merger/figures/p045_flyby_*`.

**Fuse audit — a scout qualifies its p only if both throats are still
throats at periapsis**, read from the slice cache, never the tracker (it
under-reads speeds up to 4× and degenerates below sep 2, §9).  The
single-throat growing mode makes the 40 M window a fuse; a spiral IVP would
sit 3–4 fuses deep, so throat integrity through the orbit is the gate, not
trajectory alone.

stop_time is set per-IVP: t_collapse (from the scout) + 100, or + 150 if
the §8 tail decision is taken.

---

## 4. Production grid and extraction (the L = 128 proposal)

Current geometry: L = 64, N = 128 (base dx = 0.5), max_level 5 (finest
dx = 1/64); slice caches store only the central 32-wide window.  Wrong for a
paper waveform: R = 30 sits inside the sponge (24 → 32, ~13× base
dissipation, Plan.md issue 15); two radii cannot extrapolate R → ∞;
0.5-unit plotfile sampling aliased once already (the QNM comb).

**Proposal — same dx, twice the room:** L = 128, N = 256; sponge 48 → 64;
spheres at R = 20/28/36/44, all in un-sponged vacuum, ~30 base points per
dominant wavelength.  In-code extraction ON (#6) supersedes plot-cadence
sampling; plotfiles stay at interval 50 so the consumer remains a free
second source, plus its exclusive jobs (frames, scalar modes, kinematic
flux).  Cost estimate: 3.5–4.0 u/h at level 5 (vs 4.3 today); memory
~75 GB of 80 — the smoke test (#5) decides.  Fallback: L = 96 / N = 192
(sponge 40 → 48, radii 20/26/32/38).  MPI note: the known AMR crash is
radial-recipe-specific and the merger tags type 2; a 2-rank smoke test is
worth a slot — if it holds, the level-6 companion halves to ~3 days.

**Ψ₄ in a non-vacuum exterior** (|φ| ~ 6e-3 at R = 14): defend with the
measured 1/R falloff and the scalar-to-GW flux ratio per radius from
`--scalar-modes`; if that ratio is small and falls with R, extraction
stands on measurement, not assumption.

**Check E (drainhole branch, b = 2, 2026-09-02).**  Defect A from the
L2_Ham(N) = A + B·N^-p fit, N = 192/288/384, on the repaired metric — the
2-cell boundary layer dropped, because the whole-domain norm is unusable
(93.7–99.98 % of Ham² lives in the ghost-reading outer layer; with it
dropped, the exact single throat converges at 4th order to A ≈ 8e-7):

| ladder | A (defect) | vs error bar |
|---|---|---|
| single throat (exact zero control) | ~0 (8e-7) | — |
| d = 8 (d/b = 4) | 4.92e-4 | 603× |
| **d = 12 (d/b = 6, production)** | **2.87e-4** | **352×** |
| d = 16 (d/b = 8, old gate) | 1.82e-4 | 223× |
| d = 24 (d/b = 12) | 8.61e-5 | 106× |
| d = 12 + p = 0.35 momenta | 2.92e-4 | 359× |

Smooth A ~ d^-1.6, no threshold; momenta +1.9 % — the orbit parameters are
exonerated.  The defect does not converge away with refinement.  Validated
on two independent cell sets (ghost-drop vs r < 24: identical ratios).
Caveat: A is an unnormalised RMS — relative statements are solid; absolute
size needs Ham/Ham_abs_terms.  Trap: `amr.derive_plot_vars = constraints`
aborts unless `G_Newton` is in the params.  Runs:
`runs/wormhole_merger/checkE/`.

**Helfer correction, static trade** (a = 2, m = 1, d = 12, N = 192).  Plain
superposition starts each throat +8.1 % (away) / +10.9 % (toward) too large
(the companion's du = −0.0834 dominates dpsi by 24×), so it rings.  The
windowed subtraction (`wormhole_helfer_correction`, default off) repairs the
size at the price of window curvature (~1/w²) in Ham:

| window w / p | size error | L2_Ham vs plain |
|---|---|---|
| plain superposition | +8.1 % / +10.9 % | 1.00× |
| 0.4d / 6 (literal Helfer Eq. 45) | −1.1 % / +1.5 % | 9.02× |
| **d/3 / 2 (the default)** | **+0.2 % / +2.8 %** | **1.84×** |
| d/6 / 2 | +3.1 % / +5.6 % | 1.53× |

The dynamics verdict (§1) rejects the correction regardless; this table is
the method-section record of the trade.  Regression: flag off reproduces
the pre-change baseline bit for bit.  Operational: N = 384 needs
`WHM_RANKS=2` (55.5 GB/card, binding per the wrapper README); probe
templates carry `amr.checkpoint_files_output = 0`.

---

## 5. Resolution and freeze engagement

The m4e ladder (pair means, p012 family):

| max_level | u/h (one card) | death, pair mean |
|---|---|---|
| 3 | — | 52.26 |
| 4 | 9.0 | 53.43 |
| 5 | 4.3 | 55.18 |
| 6 | 2.2 | 56.42 |
| 7 | 1.1 | 56.20 (one arm, no twin) |

Linear at +1.43/level, scatter at the ±0.35 floor; level 7 is consistent
with saturation within noise but single-arm.  "The NaN lands on each newly
created finest level every time" held for every m4e (restart) arm — but
both from-t = 0 L5 binary arms died on **level 4**, and their death-step
plotfiles are deleted, so box coverage of the death site is unverified (at
t ≈ 29 the L5 boxes covered only the pits).  Treat the finest-level claim
as restart-recipe-specific until re-checked on #17.  Caveat (2026-09-03):
the p020/p025 level-5 arms died on the level-3 clock (52.07 / 52.79) — the
ladder's gain did not transfer to from-t = 0 launches; treat +1.4/level as
the restart recipe's, p012-family.

Production: **max_level 5** (cheapest grid that reliably reaches
engagement; level 4 is a coin flip against its own death); one **level-6
twin** of the headline arm as the convergence companion; level 7 only as a
paired restart segment around collapse if a referee demands it.

**The production recipe, explicitly:** level 3 from t = 0 through the
orbit, levels 4–5 added at a pre-collapse checkpoint, then the freeze —
the validated m4e path.  A from-t = 0 max_level-5 launch clips χ at the
pits at t = 0 and forfeits the ladder's gain (§9, the L5 arms).  The
paper's resolution study is therefore a restart-refinement study and must
say so.

**Engagement is a criterion, not a constant:** the collapse sources the
burst until ~51.5 (freezing earlier deletes signal); the arm must reach
t_e under its own power (level 5 clears it by ~2 units); and t_e sets the
contamination ceiling at every radius (§6).  For production: read
t_collapse and the burst end from the level-3 scout, confirm at level 5,
engage after the burst closes, print the ceilings next to the windows
before launch.  Fill 1.5 / 2.0-wide twin, seam twin, and one
late-engagement control re-run once at L = 128, unchanged from M9b.

---

## 6. Ringdown physics (m9b chain, R = 14, window t = 60–91)

**Established, each with its test:**
- The remnant is hairy: a dipolar phantom halo (|φ| ~ 6e-3 at R = 14) rings
  with the metric at one period; the trap is that an angular mean cancels
  the dipole to 1e-10 — the power is in the m = 1 azimuthal harmonic.

| signal at R = 14 | period |
|---|---|
| Ψ₄ (l = 2, m = 0) | ~17.3 |
| φ, m = 1 ring amplitude | ~17.0 |
| ∂t φ, m = 1 ring amplitude | ~17.7 |

- Phase-locked channels: |r| = 0.95 at lag +0.5 units (a quarter-period
  would be 4.3) — one coupled Einstein–Klein–Gordon eigenmode.
- Long-lived but decaying: τ ≈ 150, Q ≈ 28 — 10× a vacuum Schwarzschild
  l = 2 ringdown; τ from 1.8 cycles carries large error bars.
- Not a freeze artifact: 15 % change in fill radius moves the period ~2 %
  (fill 17.3/17.0/17.7 vs fillwide 17.7/17.7/18.0) and the dipole
  precession rate 0.2 % (0.1537 vs 0.1540 rad/unit).
- The story closes on the initial data: merging a ± scalar pair is exactly
  what leaves a scalar dipole on the remnant.

**Refuted — keep out of the paper:** the lighthouse mechanism.  Prediction
m = ±2 period π/0.1537 = 20.4; measured 17.3, same as m = 0, phase drift
0.187 rad/u ≠ 2 × 0.154.  The ~41-unit dipole precession is a separate,
slower clock; the driver is the halo's amplitude breathing.

**The causal budget:** the burst arrives at ≈ t_c + 1.125·R; freeze
contamination from r_s = 2 arrives at ≈ t_e + 1.125·(R − 2).  Every radius
gets the same ~6–8 freeze-clean units — pushing spheres out buys
sponge-clean amplitude, not freeze-clean time.  **Fast-characteristic
caveat (second pass, adopted):** the seam is a constraint source and CCZ4
gauge/constraint modes run up to ~sqrt(2)× local light, so the conservative
ceiling at R = 14 is ≈ 62.5, not 66.5 — inside the burst window.  The real
defence is empirical (the late-engagement control moved the window
≤ 0.003 %): quote that, and print the ceilings at the fast characteristic.  **The whole 17-unit-period
ringdown sits inside the freeze's causal cone at every radius**; its
credibility rests on freeze-insensitivity.  Hence, on the production arm: a
third fill radius (a flat trend, not a two-point difference); the
engagement pair re-run at L = 128; and the causal-arrival plot printed
under every published waveform, clean window shaded per radius.

Standing caveats: the azimuthal ring harmonic is not a proper l = 1 mode
(production's scalar-mode spheres fix this); phantom matter means
"signature of this class of exotic matter", not an astrophysical
prediction; no ringdown convergence point exists until the level-6 twin.
Figure + script: `runs/wormhole_merger/merger_fix/plots/scalar_vs_psi4_R14.*`.

---

## 7. Comparison arms and analysis items

1. **Head-on freeze arm** — the only configuration with a literature number
   (BBH head-on from rest radiates ≈ 0.055 % of M, l = 2 m = 0); with the
   BBH control it makes the paper's energy-budget table.  Shortest
   production run on the list.
2. **Energy/mass balance** — M_ADM(t) at the boundary vs E_GW from the
   in-code Ψ₄ (double-integrated, static offset removed) plus the
   *negative* scalar kinematic flux.  Either the sum closes or its failure
   is a finding.  Consumer-side; no new runs.
3. **Wave-zone convergence** — R = 20–44 sit on level 0 at dx = 0.5 in
   every arm; the extracted waveform has no convergence factor of its own.
   The N = 192 twin is a *coarse* rung (dx = 2/3, ~22 points per dominant
   wavelength at 4th order) — legitimate, but the plan must call it a
   coarsening.  The cheaper refined third point is a static level-1 box
   tagged out to R = 44 inside the headline arm (decision §8).
4. **Remnant-mass QNM discriminator** — the 17.3-unit period is what a
   vacuum BH of M ≈ 1.03 rings at; this system's ADM ≈ 2 would ring at
   ~34.  If M_remnant ≈ 2 (from item 2), "it's just a BH ringdown" dies by
   a factor of two in one line.  No new runs.
5. **Dissolution re-measured** — the quoted 1.07 → 0.59 curve splices in
   the disqualified `rw` arm; re-measure on the undamped level-5 headline
   arm.  **REWRITTEN 2026-09-04:** re-measure it as the minimum AREAL radius,
   not the coordinate theta+ shell — the coordinate rate overstates the
   contraction 4–5x on both merged arms (CRITICAL BUG, Defect 2), so the
   1.07 → 0.59 curve and the word "accelerating" are withdrawn.  The agreed
   phrasing *"a short-lived black hole that dissolves by swallowing its own
   exotic matter"* is SUSPENDED: the trapped-surface evidence behind the
   words "black hole" fails the orientation test on both arms.  What survives
   is the invariant contraction, ~1 %/unit on two independent arms.  A true
   MOTS finder (BHaHAHA) is therefore no longer infrastructure — it is
   **load-bearing** for any horizon language (proposals P3/P4).
6. **Scalar-charge prediction** — read q per throat from the l = 1
   `--scalar-modes` stream (per-throat spheres; the check-F angular mean
   cancels on the flipped binary), predict F ∝ q_A·q_B beside gravity; the
   6/4 pull/push ratio and the 5× at a = 2 should both follow.  The
   cleanest analytic check, for the price of a side figure (#8).
7. **Reproducibility bar** — no deterministic-reductions build flag exists
   in this tree (the Ψ₄ integral is already serial-deterministic; the
   non-deterministic sums live in diagnostics kernels).  The bar is the
   measured ±0.35 twin floor; a per-waveform number costs a twin-from-t = 0
   (decision §8).
8. **BBH known-answer calibration — RUN DONE (2026-09-03), QNM leg
   passed; E_rad closure still owed.**  The t150 ringdown fits period
   28.8–29.7, tau 25–27 (damped-sinusoid fit on the tail; late-window
   28.9 / 22.9), i.e. ≈ 15.2–15.6 M / ≈ 12.1–14.2 M for M_f ≈ 1.9.
   That is the Kerr (2,2,0) of a modestly spinning remnant — the
   Schwarzschild reference (16.8 M / 11.2 M) is approached from exactly
   the spin-shifted side it should be, and the two spheres (R = 14, 30)
   agree within 3–7 %.  Instruments cross-checked: Python consumer
   (plotfiles, fixed center) vs in-code stream match to 0.31 % / 0.35 %
   of peak — the extraction chain is calibrated end to end.  Figures in
   the pack: `bbh_t150_ringdown` (QNM fit overlay), `bbh_vs_wormhole_psi4`
   (now sourced from t150).  Still owed for the paper: E_rad vs
   ADM-minus-horizon-mass closure, and a paired tau error bar (the tail
   sub-windows drift 38 → 30 → 23, so quote the late window with the
   drift as the systematic).  Standing caveats unchanged: R = 14 ≈ 7 M is
   near-zone for the BBH; the "2.3× brighter" claim must become an
   *energy* ratio; a phantom halo radiates negative energy, so the
   wormhole remnant's ADM may legitimately exceed 2.

   **Boundary & extraction facts for the methods section (audited
   2026-09-03 on the t150 run):**
   - Extraction spheres r = 14, 20, 26, 30 in both campaigns; box faces
     at 32 from center.  In the *wormhole* runs the sponge ramp starts at
     r = 24, so r = 26/30 sit inside it — r = 14/20 are the quoted
     instruments there; in the BBH all four are clean.
   - The BBH has **no sponge by construction, not omission**: the sponge
     is extra dissipation inside the wormhole *matter* dispatch
     (`SpongeZone.hpp`, ramp r = 24 → 32, strength 4), built because the
     phantom scalar reflects badly off radiative boundaries.  Vacuum GW
     + Sommerfeld is the standard treatment and holds here.
   - Reflection audit, four independent checks: (1) the initial-junk echo
     transits the spheres by t ≈ 60, the signal reaches R = 30 only after
     t ≈ 95 — wrong time to contaminate; (2) pre-signal ambient floor at
     R = 30 is 12 % of peak but entirely before the chirp; in-band, the
     R20→R30 envelope coherence bounds contamination at ~3.5 % of peak;
     (3) independent ringdown fits at r = 14 and r = 30 agree to 3–7 %;
     (4) full-domain scan of the t = 150 plotfile: chi scatter *falls*
     outward (0.33 % → 0.26 %), max |K| in the outer shells 4e-4, no
     standing ripples after 150 units.

**Scalar-mode module** (in hand): consumer-side
`extraction/scalar_modes.py`, own stream, default off, enabled per launch
via `--scalar-modes`.  Validated three ways: orthonormality/round-trip
selftest; p045 dipole physics (|l1 m±1| = 0.76 dominating by 4 orders,
exact ± symmetry); 7 % match vs the independent slice-cache ring harmonic.

---

## 8. Open decisions before production (author's call)

1. **L = 128 vs L = 96** — the smoke test (#5) supplies the memory number;
   say now if 2.5–3 days per arm is too slow regardless.  (Review: take 128.)
2. **Tail +150** for the headline arm — τ ≈ 150 needs ~1 e-fold ≈ 150 units
   past merger; baseline +100 gives 0.6 e-folds.  ~+12 h at level-5 speed.
   (Review: yes.)
3. **Head-on freeze arm** (§7.1).  (Review: yes, with the BBH control.)
4. **Repulsion a-points** for the power-law panel (#8).  (Review: yes.)
5. **N = 192 wave-zone twin** (§7.3).
6. **Twin-from-t = 0** of the headline arm (§7.7) — only if a per-waveform
   reproducibility bar is wanted beyond the quoted ±0.35 floor.
7. **The horizon sentence** — is it in the paper at all?  Not the author's
   call.  The #16 ladder answered with a warning (the t = 50 state is
   floor-regularized; restarts cannot certify), so the question now hangs
   on the from-t = 0 low-floor twin (nodamp_cf10, in flight).  Until it
   passes, "a short-lived black hole that dissolves" is written as
   contingent and the Letter framing does not lean on it; the
   negative-energy-accretion *mechanism* is additionally gated on #13
   (README wording aligned 2026-09-04).
8. **Initial-separation robustness arm** — one plunge from d = 16–18 at
   rescaled p (superposition defect 0.63× per the d^-1.6 law; ~1 day at
   level 3 + restart).  If the collapse sequence, wall and waveform shape
   reproduce, the superposition defect is exonerated by measurement — the
   affordable substitute for a constraint-solved IVP (§1 Helfer entry).
9. **Wave-zone third point** — the level-1 box to R = 44 in the headline
   arm vs the N = 192 coarse twin (§7.3): pick one.

Answered by events: scan values — run; headline intent — plunge-led,
p = 0.12 decided; BBH control — done; the damping-off control is no longer
deferred — it is #14 in the credibility batch.  Nothing above launches
until answered; every launch is one by-hand approval.

**External review pass (2026-09-04), checked against the ledger.**  Kept:
(a) the flyby-louder-than-merger peak is *gravitational bremsstrahlung* —
h ∝ Q̈, and p = 0.45 carries ~4× the transverse momentum, so the periapsis
whip out-peaks the low-momentum plunge; the merger's edge is chirp +
ringdown + (to be computed, #12) total energy.  (b) Paper framing: this is
the **merger–ringdown phase of an exotic-compact-object binary**, not an
astrophysical detection template — a quasi-circular inspiral cannot be
simulated here because the single-throat growing mode makes the 40 M
window a fuse (§3 fuse audit); note in the article that detector templates
would stitch PN/EOB inspiral onto this NR plunge.  (c) The causal-diagram
figure and the d = 16 robustness arm (decision 8) flagged as the two
strongest referee defences — both already tracked (#12, §8.8).
Rejected: the review asserted "confirmation of classical negative-energy
accretion" — that is the unmeasured #13 hypothesis; README wording
re-hedged the same day (shrinkage = measurement, mechanism = inference,
both contingent on the floor gate in #16/§8.7).

---

## 9. Validation pass 2026-09-03 (C++ audit, build, slices)

Method: read-through of the example's C++; a clean scratch rebuild; direct
z = 0 slice reads of nine runs at 2–6 epochs, cross-checked against the
`.dat` streams (independent instruments).

**The lapse never collapses at the throats.**  Every binary run, every
epoch: the χ pits keep lapse 0.05–0.24 and |φ| 0.79–0.92.  The
3e-2 → 1e-3 → 1e-10 collapse sits at the **inter-throat midpoint** (φ ≡ 0
by symmetry, K > 0, shift ≈ 0); the isolated throat never shows it.  The
midpoint value is identical at L3/L4/L5 (1.08e-2 at t = 28, helfer) —
converged: a property of the equations, gauge and data, not the grid.

| run | t | lapse at pits | lapse at midpoint | \|φ\| at pits | K |
|---|---|---|---|---|---|
| p020 L3 | 47.5 | 0.125 | 3.0e-3 | 0.87 | +0.20, no K < 0 core |
| plain p012 L3 | 43.5 | 0.134 | 1.9e-3 | 0.86 | — |
| helfer L3 | 60.0 | 0.073 | 1e-10 (floor) | 0.89 | +1.0 |
| helfer L4 | 48.0 | 0.177 | 3.1e-5 | 0.91 | +1.59 |
| helfer L5 | 28.0 | 0.209 | 1.08e-2 | 0.92 | +0.18 |
| p035 L3 | 73.5 | 0.046 | 1e-3 | — | +1.6 |
| p012 r03000 | 51.0 | 0.15–0.24 (rising) | shell at r ≈ 0.5–0.85 | 0.79–0.83 | −1.5 at the core |

Consequences:
- **"Zombie" explained**: at α = 1e-10 every α-proportional RHS term
  vanishes — the floored midpoint blob is static and NaN-free.  The
  h11-NaN deaths (the wall) happen with the midpoint near 3e-3, never
  floored: reaching the floor is not the trigger.
- **p012 endgame**: pits coincide within 0.2–0.6 by t = 48–51.5, core
  lapse *rises* (0.14 → 0.24) with K < 0, and the collapsed-lapse region
  becomes a shell at r ≈ 0.5–0.85.  The reported trapped surface at
  r = 1.0 (t = 51.06) sits on that shell — consistent with BH formation in
  1+log slicing, but #3 must run before the article says "common horizon"
  unhedged.  Large-radius trapped verdicts in helfer/p035/p025 coincide
  with the K ≈ 1 rim of the blob and are not credible.
- **Finest-level-only diagnostics are blind to the midpoint** until
  sep < 2.5 (`finest_lev` reductions in `BinaryWormholeLevel.cpp`);
  half-space throat positions stay valid but cell-quantised.  The tracker
  degenerates below sep 2 (pass 2 averages both pits); fix: restrict
  pass 2 to the pass-1 argmin neighbourhood.
- **CoreMatterDamping engages on the midpoint blob** (~t = 30) with no
  trapped surface — the template's rationale is false; its measured effect
  on death time is zero (§5), production runs clean.
- **Build**: clean scratch rebuild, 114 units, 0 errors; no sign or
  coupling error found (phantom sign only in T_μν, standard KG/1+log/
  Gamma-driver, floors at every RK stage).  Hygiene: `Make.package` omits
  two headers; `parameters_and_version.txt` records "(unknown)";
  `collapse_diagnostics` writes floors into state before reducing.

---

## 10. Housekeeping (2026-09-03)

- Results pack: **23 runs** (~67 MB) including the BBH control;
  `summary.md`/`.csv` regenerated; `results/merger/README.md` opens with
  the claim-by-claim map (paper subsection → backing runs → numbers).

## 10b. Audit after the credibility batch (2026-09-04)

- **All cards idle; every queued run finished.**  Walls this batch: nodamp
  51.53, lc1 43.64, p015_rr 53.35 (all h11/K NaN on the finest level);
  BBH control reached t = 150 clean.  Verdicts folded into #1/#2/#14/#15.
- **Scratch pruned to intent** (~75 GB): per run, only the held seeds
  (nodamp + p015_rr Chk05000 with `hold_seed_t50` hardlink copies), the
  held death plotfiles (p015 52.0–53.0, p015_rr 52.0–53.0, p020 51.0–52.0,
  nodamp 50.5–51.5, lc1 42.5–43.5), lc1's Chk04000 (t = 40, only gauge-arm
  checkpoint), and the BBH final Chk01200.  Superseded t = 40 checkpoints
  and the consumed BBH plotfiles deleted.
- **Logs packed**: all nine top-level `detached_gpu*.log` gzipped into
  their run directories, `run.log` gzipped in every finished run, sweeper
  log archived — `runs/wormhole_merger` top level holds only tooling,
  manifests and run dirs (~11 GB).
- **Every run directory kept** — each is packed or cited; the folder audit
  and keep-rationale are in `runs/wormhole_merger/MANIFEST_CLEANUP_2026-09-04.md`.
  `pack_results.sh` now sweeps `bbh_control_*` too.
- Figures in `results/merger/figures/`: `psi4_analysis_bbh_control{,_m2}`,
  `bbh_vs_wormhole_psi4`, the p045 fly-by set.  The comparison plotter is
  a package: `python -m grteclyn_wrapper.visualisation.merger`.
- `prune_checkpoints.sh` MAIN_RE now insures `bbh_control_*` — the t100
  final checkpoint was swept after the clean finish, which is why the t150
  rerun starts from scratch.
- Scratch cleanup: dead p020_lvl5 (26 G), p025_lvl5 (26 G) and the t100
  BBH (3.5 G) removed; scratch holds the two live runs, `_cache`, and
  p020_nofill's 3 held plotfiles (#4).  Run dirs keep params/logs/data
  streams only — the packed campaign is thinned from them; never delete.
- Earlier clean-up ledger: `runs/wormhole_merger/MANIFEST_CLEANUP_2026-09-03.md`.
