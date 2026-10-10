# Paper idea: nonlinear 3D evolutions of rotating Ellis–Bronnikov wormholes

**Pitch.** Linear studies now predict that rotation changes the instability of Ellis–Bronnikov (EB) wormholes in a specific, non-trivial way: the known unstable mode weakens, a second one appears, the two merge, and probably survive as an oscillating instability that slows down only near extremal Kerr. No one has evolved a rotating wormhole nonlinearly. A 3D numerical-relativity study can test all of this, measure the wormhole's lifetime as a function of spin, and find its end state. This has to come before any spinning-binary or anti-chirp work (pbh_reentry_wormholes.md, Sec. 4.1).

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
   - The authors *conjecture* the same for rotating wormholes near extremal Kerr.
   - This is the "unstable in another mode, stable at the speed limit" picture. It is a conjecture, not a result.

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

1. **Q1. Growth rate against spin.** Does the measured growth rate follow the O(J²) predictions for both radial modes, and do they cross or merge?
2. **Q2. Merger.** Beyond J ≈ J_max/3, does the instability become oscillatory (ω_R ≠ 0)? How do ω_I and the lifetime scale as v_e → 1? Does the 5D "the mode disappears" picture hold in 4D, or is it a complex continuation?
3. **Q3. Non-axisymmetric modes.** Do m = 1, 2 modes or an ergoregion instability grow at high spin, possibly ending any "long-lived near-extremal" regime?
4. **Q4. End state.**
   - The collapse branch should end in a Kerr-like remnant: measure its M and J.
   - **Overspin test:** slowly rotating symmetric wormholes may have J/M_ADM² > 1, because the static symmetric throat has M = 0 (verify on the backgrounds). Their collapse cannot simply produce Kerr with M = M_ADM. In the binary paper, phantom accretion let the horizon mass end *above* M_ADM, which makes this a sharp cosmic-censorship test.
   - **Inflation branch:** does spin halt it?
5. **Q5. Validation.** Does the ringdown match the Khoo et al. quasinormal modes?
6. **Q6. Exotic matter against stability.** The null-energy violation decreases with spin. Does weaker exotic support go with slower growth? Track a violation measure against spin and against ω_I.

---

## 3. Implementation

### 3.1 Backgrounds
Use the Kleihaus–Kunz ansatz (check their conventions):

$$ds^2=-e^{f}dt^2+e^{-f}\left[e^{\nu}(d\eta^2+h\,d\theta^2)+h\sin^2\theta\,(d\varphi-\omega\,dt)^2\right],\qquad h=\eta^2+\eta_0^2,$$

with unknowns f, ω, ν(η, θ) and the phantom φ. The static limit (ν = ω = 0, e^f = α²) is exactly our drainhole, with η₀ = a.

**Choose the family deliberately.** Azad et al. treat both families, so route A can do either.
- The *symmetric* family starts from the massless static throat (M = 0). It matches the published Kleihaus–Kunz data and is where J/M_ADM² > 1 is most likely, so it suits the overspin test.
- The *non-symmetric* family through your m/a = 1/2 drainhole connects directly to your static results.

Three routes:
- **A. Slow rotation, O(J²) (start here).** Build from the Azad et al. second-order solutions. It is cheap and covers J up to about J_max/3, which is exactly where the crossing or merger is predicted. The data are exact only to O(J²), so either project them onto the constraint surface or report the O(J³) violation and show it doesn't matter.
- **B. Full rapid rotation.** Write a 2D spectral Newton solver:
  - Chebyshev in x = (2/π) arctan(η/η₀), which compactifies both ends; even cos(2kθ) in θ.
  - Validate by reproducing Kleihaus–Kunz M/R_e and J/R_e² against v_e, the static limit, and spectral convergence.
- **C. Ask the Oldenburg/Madrid group** (Kunz, Kleihaus, Blázquez-Salcedo, Khoo) for their backgrounds. They have both the solutions and the linear predictions, and nonlinear evolutions complement their work directly.

### 3.2 Mapping onto the AMR grid
- **Radius.** Use η = r − η₀²/(4r), the same isotropic radius as the binary paper. Then h = r²Ω² and dη = Ω dr, with Ω = 1 + η₀²/4r².
- **Metric.** The spatial metric is γ = e^{−f}Ω²[e^ν(dr² + r²dθ²) + r² sin²θ dφ²]. It is not conformally flat, so the conformal metric h_ij starts non-trivial.
- **Lapse and shift.** α = e^{f/2} and β^φ = −ω.
- **Extrinsic curvature.** For stationary data K_ij = (D_iβ_j + D_jβ_i)/(2α), so only K_rφ and K_θφ are non-zero. Π = 0 for a static, axisymmetric φ.
- **Cartesian conversion.** Build everything from smooth functions of (r, cos θ) to keep the axis regular.
- **Far end.** The puncture at r → 0 is the far infinity. The far frame rotates at ω₋∞, giving β ≈ ω₋∞(y, −x, 0) near the puncture. This is regular because it vanishes at the puncture, but start the shift from the data, as in the binary paper.
- **Checks at t = 0.**
  - Constraint convergence at three resolutions.
  - ADM M and J from surface integrals.
  - Equatorial and polar circumferential radii of the throat against the background values.

### 3.3 Numerics: carry over the fixes from the binary paper
- **Time step.** Find the cause of the Δt = 0.02 Δx limit before starting long rotating runs. Fixing it could cut cost about 10×.
- **Constraint norms.** Compute them on the finest levels, excluding the punctures, instead of on the base grid.
- **Seeds.** Constraint-solved: perturb Π, then solve the constraints.
- **Resolution.** Run every quoted growth rate at three resolutions.
- **Waves.** Extract at larger radius or extrapolate the waveforms.
- **Gauge.** Start from the data's lapse and shift. Test a frozen shift against the Gamma driver, and the 1+log switch-off near the puncture.

### 3.4 Run protocol
1. **Hold tests at each J.** Evolve unperturbed and fit the equatorial and polar radii with A e^{ω_I t} cos(ω_R t + ϕ). The complex fit is essential to detect the merged, oscillating modes.
2. **Declared seeds.**
   - Radial: ℓ = 0 Π-shells, both signs, amplitudes 10⁻⁴ to 10⁻².
   - Non-axisymmetric: ℓ = 2 with m = 0, and m = 2 bar-type, for Q3.
   - Separating the two radial modes near the merger needs ± twins and two different seed profiles.
3. **Spin scan.** Use J/J_max = 0, 0.05, 0.1, 0.2, 0.3, then 0.4–0.8 past the predicted merger, then near-extremal (v_e = 0.9, 0.95) on a resolution ladder. Near-extremal runs are the hardest because the throat develops steep gradients as it approaches a degenerate horizon.
4. **Long baselines.** "Effectively stable" needs no growth over many static e-folds (τ_static ≈ 1.3 R★), say ≥ 300 M, with constraints under control.

### 3.5 Diagnostics
- **Throat.** A minimal-surface finder for non-round surfaces, giving equatorial and polar radii and deformation. Keep the null-expansion orientation of the binary paper.
- **Global quantities.**
  - M and J from ADM integrals at large radius.
  - The scalar charge.
  - The ergoregion boundary (g_tt = 0) against time.
- **Waves.** Ψ₄ (2,0), (2,±2) and (3,±3), with ringdown compared against the Khoo et al. modes.
- **Remnants.** A MOTS finder with a spin measurement (approximate Killing vector). Track J/M_BH² for the overspin test.
- **Exotic support (Q6).** The integrated negative phantom energy outside the throat, and the most negative T_ab k^a k^b on the throat, against time and spin.

---

## 4. What each outcome would mean

| Result | Meaning |
|---|---|
| ω_I(J) matches O(J²) for both modes | First nonlinear confirmation of the slow-rotation analysis |
| ω_R appears past ~J_max/3 | Confirms the charged-analogue conjecture for rotation |
| ω_I → 0 as v_e → 1 | Lifetime grows near extremal Kerr; quote τ(v_e) in physical units |
| m ≥ 1 growth at high spin | Ergoregion or non-axisymmetric instability ends the near-extremal window |
| Long-lived throats exist | Spinning binaries become meaningful, which reopens the anti-chirp idea |
| Overspun collapse leaves J/M_BH² < 1 via M_BH > M_ADM | Censorship is preserved by the phantom-mass mechanism |

---

## 5. Scope, staging, cost

- **Paper A (minimum publishable unit).** Route-A data with J ≲ 0.4 J_max: both radial modes against spin at three resolutions, compared with Azad et al., plus the collapse remnant's spin. Working title: *Rotation and the radial instability of Ellis–Bronnikov wormholes: 3D nonlinear evolutions*.
- **Paper B.** Full rapid rotation (route B or C): merger and oscillatory regime, near-extremal lifetime, non-axisymmetric and ergoregion runs, quasinormal-mode comparison.
- **Paper C.** Spinning binaries and the anti-chirp, only if Paper B finds throats that live long enough.
- **Cost (rough).** Level 3–4 to t ≈ 300 M is about 15–60 GPU-hours per run. Paper A is about 70 runs (8 spins × 3 resolutions × 3 seeds), roughly 10³–4×10³ GPU-hours, or one to three weeks on 8×H100. Fixing the Δt limit first changes this a lot.

## 6. Main risks

- **Accuracy of imported backgrounds** near the axis, the puncture and extremality.
- **Mode identification** near the merger, where the two growth rates are close.
- **O(J³) constraint violation** in route-A data.
- **Gauge behaviour** with a rotating far frame at the puncture.
- **Long-run constraint growth** in the near-extremal runs.

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
- N. M. Shirokov, *Wormhole dynamics: nonlinear collapse and gravitational-wave emission*, [arXiv:2604.00071](https://arxiv.org/abs/2604.00071).
- T. Matos & D. Núñez, CQG 23, 4485 (2006).
- T. Matos, GRG 42, 1969 (2010).
- J. A. González, F. S. Guzmán & O. Sarbach, PRD 80, 024023 (2009) (charged Ellis wormholes).
- P. Kanti, B. Kleihaus & J. Kunz, *Wormholes in dilatonic Einstein-Gauss-Bonnet theory*, PRL 107, 271101 (2011).