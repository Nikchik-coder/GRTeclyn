# Primordial wormholes at horizon re-entry: the PBH population

Working notes, follow-up to *Binary Ellis–Bronnikov Wormholes in 3+1 NR* (submitted, Oct 2026). Units G = c = 1 unless stated otherwise. Simulation numbers are for the production throat, m/a = 1/2.

## Bottom line

- The instability fixes when a throat collapses: at horizon re-entry. The formation epoch is therefore not a free parameter, unlike the old z_e ≈ 20 assumption.
- Each collapsing throat leaves a black hole of about 0.6 of the horizon mass at re-entry. Heavy seeds of 10⁴–10⁶ M☉ come from throats re-entering at 0.1–10 s (z ≈ 10⁹–10¹⁰).
- No wormhole-specific signal survives to be observed. The channel is a primordial-black-hole (PBH) formation mechanism, and standard PBH bounds apply.
- Even if throats are born in pairs and every encounter is as loud as the fly-by, the gravitational-wave background falls 7–8 orders of magnitude below LISA and PTA reach (Sec. 4). The only open route to an observable signal is spin-stabilized throats, whose wide binaries would anti-chirp (Sec. 4.1).
- **Blocker:** in vacuum, half of all throats inflate instead of collapsing. The scenario is viable only if the radiation era selects the collapse branch. That has to be simulated.

## 1. When throats collapse

The instability's e-fold time is τ = 5.12 M ≈ 1.3 R★ in coordinate time, or 0.76 R★ in proper time at the throat (paper, Sec. IV B).

| Throat size | Fate |
|---|---|
| R★ < H⁻¹ during inflation | Collapses within a few R★. The black hole has mass ≲ M_Pl²/H_inf ≈ 25 g for H_inf = 10¹³ GeV, evaporates in about 10⁻²¹ s, and is inflated away. Nothing observable remains. |
| R★ > H⁻¹ (stretched by inflation, Roman 1993) | Frozen: the e-fold time is longer than the Hubble time, so the instability cannot act. |
| R★ ≈ H⁻¹ (re-entry) | Collapses or inflates within a few R★. |

## 2. Mass–epoch relation

The lone-collapse runs (Sec. IV E) show the horizon forming at R ≈ R★ and shrinking under phantom accretion to about 0.6 R★ (3.88 → 2.33). This gives

$$M_{\rm BH} \simeq 0.3\,R_\star .$$

At re-entry R★ ≈ H⁻¹ = 2t in the radiation era. The horizon mass is M_H = c³t/G ≈ 2.0×10⁵ M☉ (t/1 s), so

$$M_{\rm BH} \simeq 0.6\,M_H \simeq 1.2\times10^{5}\,M_\odot\,\frac{t}{1\,{\rm s}} \simeq 1.6\times10^{5}\,M_\odot\left(\frac{T}{1\,{\rm MeV}}\right)^{-2},\qquad z \simeq 3\times10^{9}\,\frac{T}{1\,{\rm MeV}}.$$

| M_BH | t | T | z | f_obs of burst | f_PBH for 1 seed per massive galaxy |
|---|---|---|---|---|---|
| 10⁴ M☉ | 0.08 s | 4 MeV | 1×10¹⁰ | 1×10⁻¹⁰ Hz | 3×10⁻¹⁰ – 3×10⁻⁹ |
| 10⁵ M☉ | 0.8 s | 1.3 MeV | 4×10⁹ | 3×10⁻¹¹ Hz | 3×10⁻⁹ – 3×10⁻⁸ |
| 10⁶ M☉ | 8 s | 0.4 MeV | 1×10⁹ | 1×10⁻¹¹ Hz | 3×10⁻⁸ – 3×10⁻⁷ |

**Uncertainty is a factor of a few.** The runs are asymptotically flat, but at re-entry the throat is horizon-sized: expansion and radiation pressure enter at O(1), and the horizon mass grows during the few R★ the collapse takes.

**Mass function.** It follows the distribution of throat sizes at re-entry. That distribution is an input from the formation model, not something the simulations predict.

## 3. Observables: none specific to wormholes

**GW burst.** The observed frequency is f_obs = (fM)_peak / [M(1+z)], with (fM)_peak = 0.053–0.071. Because M ∝ (1+z)⁻², this becomes f_obs ≈ 3×10⁻¹¹ Hz (M/10⁵ M☉)^(−1/2), below the pulsar-timing band.

**GW background today.** With E_GW/M ≤ 0.076 (the fly-by; mergers give 4–9×10⁻³), f_PBH ≲ 10⁻⁸ and Ω_DM ≈ 0.26,

$$\Omega_{\rm GW,0} \simeq \frac{E_{\rm GW}}{M}\,\frac{f_{\rm PBH}\,\Omega_{\rm DM}}{1+z_f} \lesssim 10^{-19}.$$

**Scalar dipole at BBN.** The formation fraction is β ≈ 2.5×10⁻⁷ f_PBH (M/10⁵ M☉)^(1/2). The negative-energy scalar radiation is then ρ_φ/ρ_rad ~ (E_φ/M) β ≲ 10⁻¹⁶, so there is no ΔN_eff signature.

**Rarity.** For f_PBH ~ 10⁻⁹, β ~ 10⁻¹⁶: one throat per ~10¹⁶ Hubble volumes, so throats are separated by about 10⁵ Hubble radii. Pair encounters essentially never happen. **The lone-throat channel is the relevant one**, unless throats are born as pairs, for example the two mouths of a foam handle.

## 4. Can the bursts reach LISA or PTAs?

**Frequency.** At re-entry M ∝ (1+z_f)⁻², so the mass fixes the burst frequency. This is the same mapping as for scalar-induced GWs from standard PBHs:

$$f_{\rm obs}\simeq\frac{(fM)_{\rm peak}}{M(1+z_f)}\simeq10^{-8}\,{\rm Hz}\left(\frac{M}{M_\odot}\right)^{-1/2},\qquad 1+z_f\simeq4\times10^{9}\left(\frac{M}{10^{5}M_\odot}\right)^{-1/2}.$$

**Bigger throats radiate at lower frequencies**, not higher ones.

**Amplitude, best case.** Assume pairs born together, every encounter as loud as the fly-by (E_GW/M = 0.076), and f_PBH at its current upper limit, with Ω_GW,0 from Sec. 3:

| Band | M at re-entry | f_PBH allowed | Ω_GW,0 (max) | Detector reach |
|---|---|---|---|---|
| LISA (~3 mHz) | ~10⁻¹¹ M☉ | ≤ 1 (asteroid window) | ~10⁻²⁰ | ~10⁻¹³ |
| PTA (~10 nHz) | ~1 M☉ | ≲ 10⁻² | ~10⁻¹⁶ | ~10⁻⁸ (NANOGrav level) |
| Heavy seeds | 10⁴–10⁶ M☉ | ~3×10⁻⁹ | ~10⁻²⁰ | none at 10⁻¹¹–10⁻¹⁰ Hz |

The shortfall is 7–8 orders of magnitude in every band. The waves redshift as radiation from z ~ 10⁹–10¹⁷, while the black holes they come from are capped as dark matter.

**Why standard PBH scenarios still reach LISA.** Their LISA signal is not the collapses. It is the second-order background induced by the O(10⁻²) curvature perturbations that form them, Ω_GW ~ Ω_r A_ζ² ~ 10⁻⁹, which does not depend on how rare the PBHs are. The wormhole analogue is the mechanism that makes the throats (domain-wall networks, bubble collisions, inflationary stretching). That background could be observable, but it is not wormhole physics, and these simulations do not compute it.

**Escape routes:**

- **Evaporating remnants** (M ≲ 10¹⁵ g) escape the f_PBH cap. But their bursts land at f ≳ 10 Hz–10⁴ Hz, and BBN bounds on evaporation are even tighter. Closed.
- **Late formation of 10⁴–10⁶ M☉ throats** (the old z_e ≈ 20 case) puts individual bursts in LISA's band with SNR 35–220. There is no formation mechanism, so this is not a prediction.
- **Spin-stabilized throats**: the one open route (Sec. 4.1).

### 4.1 Spin-stabilized binaries anti-chirp

If rotation removes the unstable mode (Kleihaus & Kunz 2014; Azad et al. 2024), opposite-signed pairs can live long enough to evolve as binaries.

**Leading-order powers.** Take equal masses m, separation d, orbital frequency ω and relative speed v = dω. With scalar charges q_G² = 4πq² = Q m², the scalar dipole and gravitational quadrupole powers are

$$P_\phi=\tfrac13\,Q\,m^2d^2\omega^4,\qquad P_{\rm GW}=\tfrac85\,m^2d^4\omega^6,\qquad \frac{P_\phi}{P_{\rm GW}}=\frac{5Q}{24\,v^2}.$$

**Energy balance.** The ghost dipole carries negative energy, so dE_orb/dt = −P_GW + P_φ. On a Kepler orbit under the combined pull, v² = 2(1+Q)m/d, which gives

$$\frac{P_\phi}{P_{\rm GW}}=\frac{5Q}{48(1+Q)}\,\frac{d}{m}\quad\Rightarrow\quad d_c=\frac{48(1+Q)}{5Q}\,m\simeq10\text{–}20\,m\qquad(11.5\,m\ \text{for}\ Q=5).$$

**Consequences:**

- **d > d_c.** The orbit gains energy and widens, so the GW frequency drifts down: an anti-chirp. The binary never reaches contact and eventually dissociates.
- **d < d_c.** The quadrupole wins, consistent with the fly-by losing energy on net (|E_φ|/E_GW ≈ 0.5, paper Sec. VIII F).
- **Reliability.** d_c sits a few throat radii out, where v ~ c, so its location is only order-of-magnitude. The anti-chirp of wide orbits is robust within post-Newtonian theory.

**Signature:** a quasi-monochromatic GW source with ḟ < 0 and no merger.

**Caveats:**
- Spinning throats are assumed to keep the drainhole charge–mass relation (Q ≥ 1) and fixed charges.
- The ADM energy balance is assumed to hold with the negative scalar flux.

**Next step:** a post-Newtonian energy balance using the charges of spinning throats, then 3D runs of spinning pairs.

## 5. Constraints: standard PBH bounds

- **Seed requirement.** One seed per massive galaxy, n ~ 10⁻³–10⁻² Mpc⁻³, needs f_PBH = nM/ρ_DM with ρ_DM ≈ 3.3×10¹⁰ M☉ Mpc⁻³ (table in Sec. 2).
- **CMB accretion.** The bound is f_PBH < 3×10⁻⁹ around 10⁴ M☉, and its authors note it is still consistent with PBH seeds for supermassive black holes (Serpico et al. 2020). 10⁴ M☉ seeds are allowed but marginal. For 10⁵–10⁶ M☉, check the full compilation in Carr et al. 2021.
- **μ-distortions.** These bound the curvature perturbations behind standard PBHs, not the black holes themselves, so they don't apply directly. Whatever mechanism makes superhorizon throats must satisfy them on its own terms.

## 6. Blocker: the inflating half

- In vacuum, the sign of the perturbation selects the branch, so a sign-symmetric distribution inflates half the throats.
- At seed abundance, our observable universe (V ≈ 1.2×10¹³ Mpc³ comoving) contains N ≈ 10¹⁰–10¹¹ throats. About half would grow anti-trapped ghost regions into our side of the throat (Sec. IV F).
- Unless those regions stall, a single one is catastrophic. **The channel is viable only if the cosmological environment selects collapse.**
- **Why it might.** The radiation bath is positive energy falling into every throat. In spherical double-null evolutions, a normal-scalar pulse collapses the throat and a phantom pulse inflates it (Xu, Chew & Yeom 2025; also Shinkai & Hayward 2002).

## 7. Simulations that decide it (GRTeclyn, single throat, about 5 h each at level 3)

1. **Radiation-bath branch test.** Add a second, normal-sign massless scalar as an ingoing shell or bath. Scan its energy relative to the throat's phantom store (R★/2 − m = 0.94). Record the branch and M_BH/R★.
2. **Seed competition.** Combine the bath with declared phantom seeds ε < 0 of growing size. Find whether any physical bath leaves an inflating window.
3. **Horizon-sized throat.** Use a periodic box with a homogeneous background and initial K = −3H. Scan R★H = 0.1–1 to measure how expansion shifts the branch and the 0.6 mass ratio.
4. **Mass function (theory, no runs).** Build the throat-size distribution at re-entry from a formation model such as Roman-type stretching or bubble/wall networks.

## 8. Assumptions to state explicitly

- Inflation stretches a traversable, ghost-supported throat coherently (Roman 1993); this is assumed, not shown.
- The ghost field exists through re-entry. Cline–Jeon–Moore require a low cutoff, but R★ ~ 10⁶ km is far above any cutoff length, so the effective field theory holds on the throat scale.
- M_BH ≈ 0.6 M_H uses vacuum runs at m/a = 1/2. Other compactnesses change R★/m and the shrink factor.

## References

- T. A. Roman, *Inflating Lorentzian wormholes*, PRD 47, 1370 (1993).
- H. Shinkai & S. A. Hayward, PRD 66, 044005 (2002).
- A. Xu, X. Y. Chew & D.-h. Yeom, [arXiv:2503.07610](https://arxiv.org/abs/2503.07610).
- B. Kain, *Dynamical wormholes*, CQG 43, 045014 (2026), [arXiv:2602.18231](https://arxiv.org/abs/2602.18231).
- P. D. Serpico, V. Poulin, D. Inman & K. Kohri, PRR 2, 023204 (2020), [arXiv:2002.10771](https://arxiv.org/abs/2002.10771).
- B. Carr, K. Kohri, Y. Sendouda & J. Yokoyama, Rep. Prog. Phys. 84, 116902 (2021).
- J. M. Cline, S. Jeon & G. D. Moore, PRD 70, 043543 (2004).
- J. A. González, F. S. Guzmán & O. Sarbach, CQG 26, 015010 (2009).
- Y. Gouttenoire & E. Vitagliano, *Primordial black holes and wormholes from domain wall networks*, PRD 109, 123507 (2024).
- B. Kleihaus & J. Kunz, *Rotating Ellis wormholes in four dimensions*, PRD 90, 121503(R) (2014).
- B. Azad, J. L. Blázquez-Salcedo, F. S. Khoo & J. Kunz, *Are slowly rotating Ellis-Bronnikov wormholes stable?*, PLB 848, 138349 (2024).