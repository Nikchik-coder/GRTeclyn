# Implementation — Spiralling Wormhole–Wormhole Merger

Companion to [Plan.md](Plan.md) (checkbox execution plan lives there). This file is the
file-by-file design and the physics reasoning behind it.
Code: [Examples/BinaryWormholeMerger/](../../Examples/BinaryWormholeMerger/).

---

## 1. The central physics decision: gravity-driven, not artificially driven

**Why two standard throats cannot merge.** The massless Ellis–Bronnikov drainhole is
*ultrastatic*: g_tt = −1 exactly, everywhere. All of its curvature sits in the spatial
metric — it deflects light, but a test mass at rest feels no force at any distance and
stays at rest forever. The reason the far field is empty of pull: the phantom scalar's
negative energy exactly cancels the positive field energy, so the conformal factor is

```
psi = sqrt(1 + b²/4r²) = 1 + b²/(8r²) + O(r⁻⁴)
```

with **no 1/r term**, hence M_ADM = 0. "Curved" and "attracts" are different statements:
Newtonian attraction is the 1/r piece of the time-time metric, and this solution has
neither. Two massless throats released from rest sit there indefinitely; there is no
bound orbit at any separation. (Residual tidal-type interactions fall off much faster
than 1/d² and cannot bind anything.)

**The non-artificial fix.** The Ellis drainhole is a family, and its other branch
carries genuine ADM mass (the Lanzhou solutions, arXiv:2407.09591, quoted in Plan.md).
`wormhole_bare_mass_A/B` adds the puncture-like m/(2r) piece of that branch to ψ. Each
throat then weighs M_ADM ≈ m and the pair attracts **by real gravity**:

- **Head-on (Phase 3):** released from rest, zero momenta — they fall together on their
  own. Newtonian free-fall time t_ff ≈ π√(d³/(8 M_total)).
- **Spiral (Phase 4):** transverse Bowen–York momenta set the initial quasi-circular
  orbit (`P_t ≈ m√(M_total/d)/2` for the equal-mass pair), exactly as in every BBH
  simulation. The momenta only *choose the orbit*; gravitational-wave emission drives
  the inspiral.
- **Massless control:** one cheap m = 0 run demonstrating the pair does *not* fall —
  the proof that the merger dynamics is gravitational rather than an initial-data
  artefact.

Near a throat the two 1/r behaviours combine, psi → (b + m)/(2r), so the coordinate
inversion — and the wormhole topology — survives the added mass.

**Cost of the mass term.** The analytic φ profile supports the *massless* throat, so
bare mass introduces (i) a BBH-like O(m/d) superposition error between the bodies and
(ii) a near-throat Hamiltonian defect scaling with m/b. Both are Route-A-only defects;
the GRTresna solve (Route B / Phase 7) removes them.

## 2. Initial data (Route A — analytic superposition)

`BinaryWormholeInitialData.hpp`, following the `BinaryBHInitialData` conventions:

```
psi   = 1 + [sqrt(1 + b_A²/4r_A²) − 1] + [sqrt(1 + b_B²/4r_B²) − 1]
          + m_A/(2 r_A) + m_B/(2 r_B)
chi   = psi⁻⁴,   h_ij = δ_ij,   K = 0,   Theta = 0
phi   = (1/√4π) Σ_X atan[(r_X − b_X²/4r_X)/b_X]  −  n_throats·(1/√4π)(π/2)
Pi    = 0
Â_ij  = Σ_X (3/2r_X²)[P_i n_j + P_j n_i − (δ_ij − n_i n_j) P·n]
A_ij  = chi^{3/2} Â_ij            (CCZ4 conversion, = psi⁻⁶ Â_ij)
```

Facts the validation phase (Plan.md Phase 1) leans on:

- **Momentum constraint exact at t = 0.** K = 0 and Pi = 0 make the matter momentum
  density vanish, and superposed Bowen–York Â_ij is flat-space divergence-free. Any
  nonzero momentum-constraint output is a bug, not superposition error.
- **Hamiltonian defect is the entire error budget**: O(b²/d²) throat–throat (better
  than BBH puncture superposition, which is O(m/d), because a pure throat has no 1/r
  tail) + O(m/d) once bare masses are on + the near-throat massless-profile defect.
- **φ asymptote**: each atan → π/2, so a plain N-throat sum tends to N·(1/√4π)(π/2)
  ≈ 0.886 for N = 2, while `StateVariables` declares φ's asymptotic value as 0 and the
  Sommerfeld boundary uses that. `wormhole_subtract_phi_asymptote = 1` (default)
  removes the constant — exactly free for a massless field; `SimulationParameters`
  warns if it is combined with `phantom_mass ≠ 0`.
- **Single-throat regression mode**: `wormhole_throat_radius_B = 0` (with
  `bare_mass_B = 0`) removes object B entirely — the geometry, scalar and asymptote
  count all skip B — reproducing `SupportedWormholeCollapse` (Phases 1–2). A
  bare-mass-only puncture (b = 0, m > 0) is a plain Brill–Lindquist term, giving a
  cross-check against `BinaryBH`.

## 3. Route B — GRTresna-solved data

- GRTresna already sums two punctures (`PsiAndAijFunctions.cpp`); `bh1_*`/`bh2_*` keys
  exist end-to-end through the wrapper's config/params writer. **No solver C++ changes.**
- `recipe_initial_data_file = <path>.gridinit` switches `initData()` to
  `ExternalGridInitialData` (same bridge as the rotating example).
- Gate before use (Plan.md Phase 7): calibrate a *single* solved throat against the
  analytic profile first — there is an unresolved factor-of-2 between comment and value
  in `../GRTresna/Examples/BosonStarBH/params_rotating_wormhole_test.txt`
  (`bh1_bare_mass = 0.25` for a claimed b₀ = 0.5). Measure, don't assume.
- Two exotic lumps sit closer to the Lichnerowicz/York existence boundary than one:
  expect the *solve* to be the stall point, hence the amplitude ladder.
- The `.gridinit` bridge pins evolution resolution near-unigrid: the split-ID loader
  (interpolate only the regular part of ψ, re-add the singular part analytically per
  level) is the planned fix.

## 4. Files

| File | Role |
| --- | --- |
| `BinaryWormholeInitialData.hpp` | two-throat ψ-superposition + bare masses + Bowen–York (§2) |
| `BinaryWormholeLevel.hpp/.cpp` | level class; `num_punctures = 2`; Route A/B branch in `initData()`; diagnostics + Weyl extraction in `specificPostTimeStep()` |
| `Main_BinaryWormhole.cpp` | `BHAMR<2>` so the Weyl4 particle interpolator exists; puncture tracking off |
| `SimulationParameters.hpp` | all `wormhole_*`/`binary_diag_*` keys, defaults and sanity warnings (§6) |
| `BinaryThroatDiagnostics.hpp` | own module, own file, default-off (§5) |
| `StateVariables.hpp` | CCZ4 + `c_phi`, `c_Pi` (both even parity, asymptote 0) |
| `PhantomDecayPotential.hpp`, `ExternalGridInitialData.hpp` | copied from the single-throat examples |
| `params_test/headon/spiral.txt` | smoke / gravity-driven-from-rest / headline inspiral |

`ExoticScalarField` is reused as-is; `wormhole_metric_type = 2` makes its causal
support-ramp machinery measure retarded time from the *nearest of the two* throats.
The key scheme (`wormhole_throat_radius_A/B`, `wormhole_centerA/B`) is shared between
the ID and the matter class deliberately — one set of values.

## 5. Diagnostics

`collapse_diagnostics.dat` keeps the **unchanged 13-column single-throat contract**
(existing analysis scripts keep working). The binary information lives in its own
module/file, default off (SOLID rule):

`binary_throat_diagnostics.dat`, 17 columns — separation; barycentre + χ/lapse minima
per half-space (split by `binary_diag_axis`/`split_coord`); θ₊ and the outermost trapped
radius about throat A, throat B and their midpoint.

**How θ₊ is reduced, and why it matters.** A closed surface is trapped only when θ₊ ≤ 0
*everywhere on it*, so the scan bins points into radial shells about each centre and takes
the **maximum** of θ₊ per shell; the reported horizon radius is the outermost shell whose
maximum is ≤ 0. The first implementation reduced a global *minimum* over all points and
reported a huge phantom trapped surface at t = 0 (θ₊ = −1.26 at r = 5.02 for a pair at
d = 3.75): a single point of a large sphere about throat A grazing throat B sits in B's
steep χ gradient, which overwhelms the 2√χ/r term belonging to the distant centre A. That
artefact lives at a radius set by the *separation*, so no exclusion radius suppresses it —
the shell maximum removes it exactly, because the rest of that same sphere is far from
both throats and expanding. Shells the finest AMR level does not cover carry **no**
verdict (an empty shell must read "unknown", never "trapped"); if none is covered the
column holds the sentinel 1e30.

**θ₊ caveat that remains**: for an EB throat θ₊ = 2(1−u)/(r(1+u)²) with u = b²/4r², so
θ₊ < 0 over the *whole* sphere for r < b/2 — the coordinate inversion (r → 0 is the other
asymptotic end), not a horizon. `binary_diag_min_radius` (default max(b_A, b_B), i.e.
twice what is needed) excludes it. The common-centre scan raises its own cut to
sep/2 + min_radius automatically, so a sphere only counts as "common" once it encloses
both throats; only that scan going trapped is evidence of fusion.

Ψ₄: in-code `WeylExtraction` on the `BHAMR<2>` interpolator, same block as the
rotating example — modes (2,0), (2,1), (2,2), (4,0) at ≥ 2 radii.

## 6. Parameter sanity net (`SimulationParameters::check_params`)

- error: b_A ≤ 0, b_B < 0, negative bare masses, coincident centres;
- warn: `subtract_phi_asymptote` with `phantom_mass ≠ 0`; separation ≤ 4·b_max
  (O(b²/d²) no longer small); m_total ≥ 0.2·d (O(m/d) no longer small);
- warn: **all of** m = 0, P = 0, support = 1 — "massless throats do not attract; the
  pair will not fall together" (the exact trap this design exists to avoid);
- warn: momentum on an absent object B (junk Bowen–York term);
- error: any of `wormhole_phi_{monopole_amplitude,perturbation_amplitude,perturbation_width}`
  still present — see below.

**No seeded scalar perturbation.** The single-throat example carries a Gaussian
`φ → φ + (A₀ + A_φ Y₂₀)exp(−r²/w²)` because picking the Shinkai–Hayward compressive or
rarefactive branch by hand *is* that experiment. A merger must not do this: the other
throat is the perturbation, and pre-destabilising the throats contaminates the very thing
the run measures — whether gravity alone brings them together, and what happens when they
meet. Each throat therefore starts in its own exact equilibrium. The three keys were
removed rather than defaulted to zero, and a params file that still sets one is rejected
with a message, so a stale file cannot silently mean something different from what it says.

## 7. Launch policy

Every run goes through
[grteclyn-wrapper/scripts/campaigns/wormhole_merger/run_single.sh](../../grteclyn-wrapper/scripts/campaigns/wormhole_merger/run_single.sh)
— never a bare `./main3d…ex params.txt`:

- registers `launcher.pid` via `campaign_register_launcher` → stoppable with
  `stop_campaign.sh [--dry-run] <runs_dir>`;
- clones the params template into the run dir and re-emits `output_path` (NFS run dir),
  `amr.plot_file` / `amr.check_file` (node-local `/tmp/grteclyn_scratch/<run>`), each
  asserted to occur exactly once — plotfiles never touch NFS;
- runs attached in the foreground (detached launches need explicit permission);
- knobs: `WHM_PARAMS`, `WHM_GPU`, `WHM_RUNS_DIR`, `WHM_NAME`, `WHM_EXE`, `WHM_DRYRUN=1`.

No plotfile consumer exists for this example yet, so plotfiles *stay* on scratch —
copy what analysis needs before purging; scratch does not survive a node swap.

## 8. Symmetry notes (not yet exploited)

Equal head-on along z: z-reflection maps A↔B and φ is even ⇒ octant symmetry valid.
The spiral run breaks z-reflection but keeps nothing usable under the current
reflective-BC machinery — full box for Phase 4. Symmetric boxes are an optimisation to
revisit only if Phase 3 wall times demand it.

## 9. Known limitations / open items

1. Analytic φ supports the massless throat — massive Route-A data carries a controlled
   near-throat defect until Phase 7 (quantify in the Phase 6 error budget).
2. `wormhole_support_strength` re-read footgun: `ExoticScalarField` re-reads the key
   from ParmParse when constructed with strength exactly 1.0 — keep the key present in
   params files.
3. Bare-mass calibration against GRTresna (`bh1_bare_mass` factor-of-2) unresolved —
   Phase 7 gate.
4. θ₊ proxy is not an apparent-horizon finder; statements about a common horizon stay
   conditional on the common-centre scan + a real AH finder if one is ever ported.
