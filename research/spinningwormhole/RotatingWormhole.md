# Paper idea: nonlinear 3D evolutions of rotating Ellis–Bronnikov wormholes, from slow to near-extremal spin

**Pitch.** Linear studies predict that rotation changes the instability of Ellis–Bronnikov (EB) wormholes in a specific, non-trivial way:
- the known unstable mode weakens;
- a second one appears;
- the two merge, and probably survive as an oscillating instability that slows down only near extremal Kerr.

No one has evolved a rotating wormhole nonlinearly. **One paper** covers the whole spin range: it tests the slow-spin predictions, follows the instability through the predicted merger to near-extremal spin, measures the lifetime against spin, and finds the end state. This has to come before any spinning-binary or anti-chirp work (pbh_reentry_wormholes.md, Sec. 4.1).

**Working title:** *Does rotation stabilize traversable wormholes? Nonlinear evolutions of Ellis–Bronnikov wormholes from slow rotation to the extremal Kerr limit.*

---

## 1. What is known

### Solutions
- Slowly rotating EB wormholes are known perturbatively (Kashargin & Sushkov 2008) and to second order in rotation (Azad et al. 2024).
- Rapidly rotating ones are known only numerically (Kleihaus & Kunz 2014; Chew, Kleihaus & Kunz 2016). No closed form exists (Volkov 2021).
- **The family runs from static EB to extremal Kerr.**
  - As the equatorial rotational velocity of the throat v_e → 1 (the "speed limit"), the solution tends everywhere to extremal Kerr, and the phantom field vanishes.
  - Along the way the throat flattens at the poles, an ergoregion appears (not touching the axis), and stable bound orbits exist.
- **Two different meanings of "symmetric".**
  - Kleihaus–Kunz call a solution *symmetric* when both asymptotic ends have the same mass (f is symmetric).
  - Non-symmetric boundary conditions on f give families with different masses at the two ends, as in the static case. **Every such family, however asymmetric, still ends in extremal Kerr.**
  - Separately, rotation is imposed by a boundary condition at one end, so the frame dragging ω is never mirror-symmetric. Fully reflection-symmetric rotating wormholes need extra rotating matter (Hoffmann et al. 2018).
- **The exotic matter weakens with spin.** The violation of the null energy condition decreases as the rotation velocity grows, consistent with the phantom field vanishing at the extremal limit.
- **Ending in an extremal black hole looks generic.** Charged static Ellis wormholes end in extremal Reissner–Nordström (González, Guzmán & Sarbach 2009), and 5D rotating ones also end in an extremal black hole. The charged case is the analogue behind the conjecture below.

### Radial (ℓ = 0) stability: the current picture
The idea that rotation might stabilize wormholes goes back to Matos & Núñez (2006). Kleihaus & Kunz (2014) left the 4D question open.

1. **5D, equal angular momenta** (Dzhunushaliev et al. 2013): the unstable modes merge at a critical angular momentum, and purely imaginary (non-oscillating) unstable modes are no longer seen beyond it. Kleihaus & Kunz (2014) read this as the instability disappearing.
   - **Caveat:** after a merger, modes can continue as complex, oscillating unstable modes (item 3). A search for purely imaginary modes would miss them, so "disappears" may be incomplete even in 5D.
   - A time evolution sees oscillating growth directly, which is one reason numerical relativity can settle this.
2. **4D, slow rotation to O(J²)** (Azad et al. 2024, PLB and PRD):
   - The static unstable mode weakens with spin and reaches zero.
   - **A second unstable mode** grows out of a zero mode of the static solution and gets *more* unstable with spin.
   - In perturbation theory the two cross. Extrapolating, they merge at about **1/3 of the maximal scaled J**.
3. **Charged analogue** (Blázquez-Salcedo et al., arXiv:2510.11406):
   - After the two modes merge, the instability does **not** disappear. It continues as a complex pair, ±ω_R with a common ω_I: growth that also oscillates.
   - ω_I → 0 only as the extremal black-hole limit is approached, so the instability time can be made arbitrarily long but never infinite.
   - The authors *conjecture* the same for rotating wormholes near extremal Kerr. It is a conjecture, not a result.

**Other routes to stability.** Higher-curvature terms in the action can stabilize wormholes (Kanti, Kleihaus & Kunz 2011). That is a different theory and outside this paper.

### Non-radial modes and the ergoregion
- Quasinormal modes of rapidly rotating EB wormholes have been computed in the M_z = 2, 3 sectors (Khoo et al. 2024). Rotation breaks the triple isospectrality of the static solution. Stability in every non-axisymmetric sector has not been established.
- **Ergoregion instability is open for EB wormholes.**
  - Spinning horizonless objects with ergoregions are usually unstable when the object reflects waves.
  - A throat transmits waves to the other universe instead. Some wormhole spacetimes have an ergoregion but no superradiance (Clément & Gal'tsov 2023).
  - Other Kerr-like wormholes show growing modes in test-field studies (Franzin et al. 2022).

### Nonlinear evolutions
None of rotating wormholes. All existing evolutions are static or spherical, including 2604.00071 and the binary paper. The Oldenburg/Madrid authors themselves say a non-perturbative radial analysis at rapid rotation is the missing piece.

---

## 2. Questions the paper answers

1. **Q1. Slow spin.** Does the measured growth rate follow the O(J²) predictions for both radial modes, and do they cross or merge?
2. **Q2. Through the merger.** Beyond J ≈ J_max/3, does the instability become oscillatory (ω_R ≠ 0)? Does the 5D "the mode disappears" picture hold in 4D, or is it a complex continuation?
3. **Q3. Near-extremal lifetime.** How do ω_I and the lifetime scale as v_e → 1?
4. **Q4. Non-axisymmetric modes.** Do m = 1, 2 modes or an ergoregion instability grow at high spin, possibly ending any "long-lived near-extremal" regime?
5. **Q5. End state.**
   - The collapse branch should end in a Kerr-like remnant: measure its M and J.
   - **Overspin test:** slowly rotating symmetric wormholes may have J/M_ADM² > 1, because the static symmetric throat has M = 0 (verify on the backgrounds). Their collapse cannot simply produce Kerr with M = M_ADM. In the binary paper, phantom accretion let the horizon mass end *above* M_ADM, which makes this a sharp cosmic-censorship test.
   - **Inflation branch:** does spin halt it?
6. **Q6. Exotic matter against stability.** The null-energy violation decreases with spin. Does weaker exotic support go with slower growth?
7. **Q7. Validation.** Does the ringdown match the Khoo et al. quasinormal modes?

---

## 3. Step-by-step plan (one paper, slow to fast spin)

Each step lists what to do, what it produces, and the check that must pass before moving on.

### Step 0. Fix the numerics first (2–3 weeks)
- **Do:**
  - Find the cause of the Δt = 0.02 Δx limit.
  - Move constraint norms to the finest levels, excluding the punctures.
  - Build constraint-solved seeds: perturb Π, then solve the constraints.
  - Add waveform extrapolation in 1/R.
- **Produces:** a cheaper, more defensible code; every later step depends on it.
- **Check:** the static drainhole reproduces the binary paper's growth rate (τ ≈ 5.12) at the new Δt, at three resolutions.

### Step 1. Background solutions across the full spin range (3–6 weeks, or 1–2 if shared)
- **Do:**
  - **Choose the family.** The *symmetric* family starts from the massless static throat (M = 0), matches the published Kleihaus–Kunz data and suits the overspin test. The *non-symmetric* family through your m/a = 1/2 drainhole continues from your static results. Azad et al. treat both.
  - **Slow spin:** build the O(J²) solutions of Azad et al. for J ≲ 0.4 J_max.
  - **Fast spin:** either write a 2D spectral Newton solver, or ask the Oldenburg/Madrid group (Kunz, Kleihaus, Blázquez-Salcedo, Khoo) for their backgrounds up to v_e ≈ 0.95.
    - Solver details: Chebyshev in x = (2/π) arctan(η/η₀), which compactifies both ends; even cos(2kθ) in θ.
- **Produces:** one family of backgrounds from v_e = 0 to about 0.95.
- **Check:**
  - The full solver reproduces Kleihaus–Kunz M/R_e and J/R_e² against v_e, and the static limit.
  - At small spin it agrees with the O(J²) solutions. This overlap validates both routes.

The ansatz (Kleihaus & Kunz; check conventions):

$$ds^2=-e^{f}dt^2+e^{-f}\left[e^{\nu}(d\eta^2+h\,d\theta^2)+h\sin^2\theta\,(d\varphi-\omega\,dt)^2\right],\qquad h=\eta^2+\eta_0^2.$$

The static limit (ν = ω = 0, e^f = α²) is exactly our drainhole, with η₀ = a.

### Step 2. Put the backgrounds on the AMR grid (1–2 weeks)
- **Do:**
  - **Radius.** Use η = r − η₀²/(4r), the same isotropic radius as the binary paper. Then h = r²Ω² and dη = Ω dr, with Ω = 1 + η₀²/4r².
  - **Metric.** γ = e^{−f}Ω²[e^ν(dr² + r²dθ²) + r² sin²θ dφ²]. It is not conformally flat, so the conformal metric starts non-trivial.
  - **Lapse and shift.** α = e^{f/2} and β^φ = −ω.
  - **Extrinsic curvature.** K_ij = (D_iβ_j + D_jβ_i)/(2α), so only K_rφ and K_θφ are non-zero. Π = 0.
  - **Cartesian conversion.** Build from smooth functions of (r, cos θ) to keep the axis regular.
  - **Far end.** At the puncture (the far infinity) the frame rotates at ω₋∞, giving β ≈ ω₋∞(y, −x, 0). This is regular; start the shift from the data.
  - **Slow-spin data** are exact only to O(J²): either project them onto the constraint surface or report the O(J³) violation.
- **Produces:** t = 0 data at every spin in the scan.
- **Check:**
  - Constraint convergence at three resolutions.
  - ADM M and J, and the equatorial and polar throat radii, match the background values.

### Step 3. Hold tests (1–2 weeks of GPU time)
- **Do:** evolve each spin unperturbed. Try a frozen shift against the Gamma driver, and the 1+log switch-off near the puncture.
- **Produces:** the hold time and the growth seeded by truncation error at each spin.
- **Check:** each wormhole holds its shape for at least several static e-folds before departing, and the departure moves later with resolution. Instant departure means a setup bug, not physics.

### Step 4. Slow spin: J/J_max = 0, 0.05, 0.1, 0.2, 0.3, 0.4 (answers Q1)
- **Do:**
  - Apply ℓ = 0 Π-shell seeds, both signs, amplitudes 10⁻⁴ to 10⁻².
  - Fit the equatorial and polar radii with A e^{ω_I t} cos(ω_R t + ϕ).
  - Separate the two radial modes with ± twins and two different seed profiles.
- **Produces:** ω_I(J) for both modes at three resolutions, plotted against Azad et al.
- **Check:** at J = 0 you recover the static rate; the rates converge with resolution.

### Step 5. Through the merger to fast spin: v_e from ≈ 0.4 to 0.95 (answers Q2, Q3)
- **Do:** repeat Step 4's protocol on the full backgrounds. Use long baselines, at least 300 M, so that slow and oscillatory growth is visible.
- **Produces:**
  - Where the modes merge.
  - Whether ω_R ≠ 0 beyond it.
  - ω_I(v_e) and the lifetime against spin, quoted in physical units.
- **Check:** a resolution ladder at the highest spins. Near-extremal throats develop steep gradients; stop at the highest spin you can resolve and say so.

### Step 6. Lopsided perturbations and the ergoregion (answers Q4)
- **Do:**
  - At the three highest spins, apply ℓ = 2, m = 0 and m = 2 (bar-type) seeds.
  - Track the ergoregion boundary (g_tt = 0) and any m ≥ 1 growth.
- **Produces:** whether a non-axisymmetric or ergoregion instability limits the near-extremal window.
- **Check:** compare the m ≥ 1 content against an unperturbed twin, to rule out growth from truncation noise.

### Step 7. End states (answers Q5)
- **Do:**
  - Follow collapse-branch runs to the remnant: measure M_BH and J_BH with a MOTS finder and approximate Killing vector.
  - For the overspin test, take the slowest-spinning symmetric wormholes, where J/M_ADM² > 1 if confirmed.
  - Follow inflation-branch runs at several spins.
- **Produces:** the remnant spin against wormhole spin; whether censorship holds and how; whether spin stops inflation.
- **Check:** the remnant's ringdown frequency matches Kerr with the measured M_BH and J_BH.

### Step 8. Validation and the exotic-matter measure (answers Q6, Q7)
- **Do:**
  - Compare the Ψ₄ (2,0), (2,±2) and (3,±3) ringing of the stable-looking or slowly growing runs with Khoo et al.
  - Plot the integrated negative phantom energy outside the throat, and the most negative T_ab k^a k^b on it, against spin and against ω_I.
- **Produces:** an independent check of the backgrounds and code, and the link between exotic support and stability.

### Step 9. Error budget and write-up (3–4 weeks)
- **Do:** collect the resolution, extraction and seed-amplitude errors for every quoted number; write the paper.
- **Paper outline:**
  1. Introduction
  2. Rotating EB family and backgrounds
  3. Numerics and validation
  4. Slow spin against perturbation theory
  5. Merger and fast spin
  6. Non-axisymmetric and ergoregion runs
  7. End states and the overspin test
  8. Exotic matter against stability
  9. Discussion

### Timeline and compute
- **Calendar:** about 4–6 months. Step 1 is the critical path, and getting backgrounds from the Kunz group shortens it most.
- **Don't let Step 1 block progress.** Run Steps 3–4 on the slow-spin data while the fast-spin backgrounds are being built or requested.
- **GPU budget:** about 170 runs at 15–60 GPU-hours each, i.e. roughly 2.5–10 × 10³ GPU-hours, or 2–7 weeks on 8×H100. The Step 0 time-step fix could cut this by up to 10×.

---

## 4. What each outcome would mean

| Result | Meaning |
|---|---|
| ω_I(J) matches O(J²) for both modes | First nonlinear confirmation of the slow-rotation analysis |
| ω_R appears past ~J_max/3 | Confirms the charged-analogue conjecture for rotation; the 5D "disappearance" was a complex continuation |
| ω_I → 0 as v_e → 1 | Lifetime grows near extremal Kerr; quote τ(v_e) in physical units |
| m ≥ 1 growth at high spin | Ergoregion or non-axisymmetric instability ends the near-extremal window |
| Long-lived throats exist | Spinning binaries become meaningful, which reopens the anti-chirp idea as a follow-up |
| Overspun collapse leaves J/M_BH² < 1 via M_BH > M_ADM | Censorship is preserved by the phantom-mass mechanism |

---

## 5. Main risks

- **Fast-spin backgrounds are the critical path:** writing a solver, or depending on another group.
- **Accuracy of imported backgrounds** near the axis, the puncture and extremality.
- **Mode identification** near the merger, where the two growth rates are close.
- **O(J³) constraint violation** in slow-spin data.
- **Gauge behaviour** with a rotating far frame at the puncture.
- **Long-run constraint growth** and resolution cost in the near-extremal runs.

**After this paper:** spinning binaries and the anti-chirp, only if Step 5 finds throats that live long enough.

---

## References

- B. Kleihaus & J. Kunz, *Rotating Ellis wormholes in four dimensions*, PRD 90, 121503(R) (2014), [arXiv:1409.1503](https://arxiv.org/abs/1409.1503).
- X. Y. Chew, B. Kleihaus & J. Kunz, *Geometry of spinning Ellis wormholes*, PRD 94, 104031 (2016), [arXiv:1608.05253](https://arxiv.org/abs/1608.05253).
- P. E. Kashargin & S. V. Sushkov, Grav. Cosmol. 14, 80 (2008); PRD 78, 064071 (2008).
- M. S. Volkov, PRD 104, 124064 (2021).
- V. Dzhunushaliev, V. Folomeev, B. Kleihaus, J. Kunz & E. Radu, *Rotating wormholes in five dimensions*, PRD 88, 124028 (2013).
- B. Azad, J. L. Blázquez-Salcedo, F. S. Khoo & J. Kunz, *Are slowly rotating Ellis-Bronnikov wormholes stable?*, PLB 848, 138349 (2024), [arXiv:2301.05243](https://arxiv.org/abs/2301.05243).
- B. Azad, J. L. Blázquez-Salcedo, F. S. Khoo & J. Kunz, *Radial perturbations of Ellis-Bronnikov wormholes in slow rotation up to second order*, PRD 109, 124051 (2024), [arXiv:2403.08387](https://arxiv.org/abs/2403.08387).
- J. L. Blázquez-Salcedo, L. M. González-Romero, F. S. Khoo, J. Kunz & P. Navarro Moreno, *Radial perturbations of charged wormholes*, [arXiv:2510.11406](https://arxiv.org/abs/2510.11406).
- F. S. Khoo et al., *Quasinormal modes of rapidly rotating Ellis-Bronnikov wormholes*, PRD 109, 084013 (2024), [arXiv:2401.02898](https://arxiv.org/abs/2401.02898).
- C. Hoffmann, T. Ioannidou, S. Kahlen, B. Kleihaus & J. Kunz, *Wormholes immersed in rotating matter*, [arXiv:1712.02143](https://arxiv.org/abs/1712.02143).
- G. Clément & D. Gal'tsov, *Rotating traversable wormholes in Einstein-Maxwell theory*, PLB 838, 137677 (2023), [arXiv:2210.08913](https://arxiv.org/abs/2210.08913).
- E. Franzin, S. Liberati, J. Mazza, R. Dey & S. Chakraborty, PRD 105, 124051 (2022), [arXiv:2201.01650](https://arxiv.org/abs/2201.01650).
- T. Matos & D. Núñez, CQG 23, 4485 (2006).
- T. Matos, GRG 42, 1969 (2010).
- J. A. González, F. S. Guzmán & O. Sarbach, PRD 80, 024023 (2009) (charged Ellis wormholes).
- P. Kanti, B. Kleihaus & J. Kunz, *Wormholes in dilatonic Einstein-Gauss-Bonnet theory*, PRL 107, 271101 (2011).
- N. M. Shirokov, *Wormhole dynamics: nonlinear collapse and gravitational-wave emission*, [arXiv:2604.00071](https://arxiv.org/abs/2604.00071).