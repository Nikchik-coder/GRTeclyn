# Deep research: a solver (or data) for rapidly rotating Ellis–Bronnikov wormholes

## The question

We evolve rotating Ellis–Bronnikov (EB) wormholes in 3D numerical relativity. The background we need is the
Kleihaus–Kunz family: Einstein gravity plus one real, massless phantom scalar, stationary and axisymmetric. We need
it from slow rotation up to near the extremal-Kerr limit, as 2D tables that start the 3D runs. Our own solver is
perturbative, at O(J²), and it stops being accurate at about 12 % of the maximal spin. Find out:

1. **Does a usable code or dataset already exist** that produces these solutions? Look on GitHub, GitLab,
   Bitbucket, Codeberg, Zenodo, Software Heritage, arXiv ancillary files, journal supplements, theses and group
   pages. If one does, say where it is, its licence, exactly what it solves and how to run it.
2. **If not, what is the shortest reliable path?** Name the closest open code to adapt, or the best framework
   and recipe for writing our own.

"No public code exists; here is the closest one and the recipe" is an acceptable answer. Open every link you
report and say what you found there. Never infer from a paper that a repository exists.

## 1. The physics, self-contained

Conventions follow Chew, Kleihaus & Kunz (CKK), *Geometry of spinning Ellis wormholes*, PRD 94, 104031 (2016),
arXiv:1608.05253. The first paper is Kleihaus & Kunz (KK), PRD 90, 121503(R) (2014), arXiv:1409.1503.

**Action.** $S=\frac{1}{16\pi G}\int\sqrt{-g}\,(R+2\,\partial_\mu\psi\,\partial^\mu\psi)$, so
$R_{\mu\nu}=-2\,\partial_\mu\psi\,\partial_\nu\psi$ and $\Box\psi=0$.

**Ansatz.** The metric is quasi-isotropic, with $f,\nu,\omega$ functions of $(\eta,\theta)$:

$$ds^2=-e^{f}dt^2+e^{-f}\left[e^{\nu}(d\eta^2+h\,d\theta^2)+h\sin^2\theta\,(d\varphi-\omega\,dt)^2\right],\qquad h=\eta^2+\eta_0^2 .$$

The coordinate runs over $\eta\in(-\infty,\infty)$. Its two ends are two asymptotically flat universes, and the
throat sits at or near $\eta=0$.

**Scalar.** The scalar decouples exactly, for every rotation: $\partial_\eta\psi=D/h$, so
$\psi=(D/\eta_0)(\arctan(\eta/\eta_0)-\pi/2)$. CKK eq. 9 drops the $1/\eta_0$. Only the scalar charge $D$ changes with
spin.

**Field equations** (CKK eqs. 10–13 and 19):

- (10) $\partial_\eta(h\sin\theta\,\partial_\eta f)+\partial_\theta(\sin\theta\,\partial_\theta f)-h\sin^3\theta\,e^{-2f}\,[h(\partial_\eta\omega)^2+(\partial_\theta\omega)^2]=0$
- (11) $\partial_\eta(h^2\sin^3\theta\,e^{-2f}\partial_\eta\omega)+\partial_\theta(h\sin^3\theta\,e^{-2f}\partial_\theta\omega)=0$
- (12) $\partial_\eta(h\sin\theta\,\partial_\eta\nu)+\sin\theta\,\partial_\theta^2\nu-\cos\theta\,\partial_\theta\nu-h\sin^3\theta\,e^{-2f}\,[h(\partial_\eta\omega)^2-2(\partial_\theta\omega)^2]=0$
- (13), the ηθ constraint: $-h\sin\theta\,\partial_\eta f\,\partial_\theta f+h\cos\theta\,\partial_\eta\nu+\eta\sin\theta\,\partial_\theta\nu+h^2\sin^3\theta\,e^{-2f}\,\partial_\eta\omega\,\partial_\theta\omega=0$
- (19) $D^2=\frac{h}{4}[h(\partial_\eta f)^2-(\partial_\theta f)^2]-\frac{h}{2}(\eta\,\partial_\eta\nu-\cot\theta\,\partial_\theta\nu)-\frac{h^2}{4}\sin^2\theta\,e^{-2f}[h(\partial_\eta\omega)^2-(\partial_\theta\omega)^2]+\eta_0^2$.
  This must come out the same constant everywhere, which makes it an accuracy check.

**Boundary conditions** (CKK 14–16):

- As $\eta\to+\infty$: $f,\omega,\nu\to0$.
- As $\eta\to-\infty$: $f\to\gamma$, $\omega\to\omega_{-\infty}$, $\nu\to0$.
- On the axis: $\partial_\theta f=\partial_\theta\omega=0$ and $\nu=0$.
- Reflection symmetry about the equator.

**Parameters.** $\eta_0$ sets the scale, $\gamma$ the asymmetry ($\gamma=0$ is "symmetric"), and $\omega_{-\infty}$
the rotation.

**Static member** (CKK 17): $f=\frac{\gamma}{2}(1-\frac{2}{\pi}\arctan\frac{\eta}{\eta_0})$, $\omega=\nu=0$,
$D^2=\mu_+^2+\eta_0^2$. The mass at $+\infty$ is $\mu_+=-\gamma\eta_0/(2\pi)$; CKK print it without the minus sign.

**Asymptotics.** As $\eta\to+\infty$: $f\to-2\mu_+/\eta$, $\omega\to2J/\eta^3$ and $\nu\to-c_2\sin^2\theta/\eta^2$,
with $c_2=\mu_+^2+\eta_0^2-D^2$.

**Known properties** (KK 2014, CKK 2016):

- **The extremal-Kerr end.** The family ends in extremal Kerr as the throat's equatorial speed
  $v_e=R_e\,\omega_0\to1$. On the way, $D\to0$ and the scalar vanishes.
- **Smarr relations.** In general $\mu_++\mu_-=2\omega_{-\infty}J_+$. In the symmetric case $\mu_+=2\omega_0J_+$ and
  $\omega_{-\infty}=2\omega_0$.
- **A fold.** At fixed $\eta_0$, the mass and $J$ diverge as $v_e\to1$. Also, $\omega_0$ is not monotonic, so a
  fixed $\omega_{-\infty}$ can have two solutions (CKK quote an "upper branch"). Continuation has to go round this
  fold. $D$ is monotonic.
- **Faster than light.** For $\gamma>0$, $v_e$ can exceed 1. Our family has $\gamma<0$, where $v_e\le1$.

**A structural observation (our derivation; confirm or refute it from the literature).** Eqs. (10)–(11) contain
neither $\nu$ nor $\psi$. So $(f,\omega)$ obey the stationary axisymmetric **vacuum** (Ernst) equations, written in
oblate-spheroidal coordinates.

- The Weyl coordinates are $\rho=\sqrt{h}\sin\theta$ and $z=\eta\cos\theta$.
- Because $\eta$ runs over all of $\mathbb R$, the Weyl half-plane has two sheets, glued across the disk
  $\rho<\eta_0$, $z=0$. That disk is the throat.
- $\nu$ then follows linearly from (12), or by quadrature from (13).
- The phantom field enters only $R_{\eta\eta}$, where it fixes $D^2$ through (19).

The core problem is therefore a nonlinear elliptic boundary-value problem for two functions on a rectangle,
$(x,\theta)\in[-1,1]\times[0,\pi/2]$ with $x=(2/\pi)\arctan(\eta/\eta_0)$. Codes for stationary axisymmetric vacuum
spacetimes, and solution-generating methods for the Ernst equation, are relevant even if they never mention
wormholes.

## 2. What we already have

**The 3D evolution code.** GRTeclyn is an AMReX/GPU port of GRChombo. We run CCZ4 with the phantom scalar, the
1+log and Gamma-driver gauge, and box-in-box AMR.

- The radius is isotropic, $\eta=r-\eta_0^2/(4r)$, so the other universe ($\eta\to-\infty$) is a puncture at $r\to0$.
- The 3+1 data are built from the table: $\alpha=e^{f/2}$, $\beta^\varphi=-\omega$, $\gamma_{ij}$ from the ansatz,
  $K_{ij}=(D_i\beta_j+D_j\beta_i)/(2\alpha)$, and $\Pi=0$.
- Our earlier static and binary wormhole evolutions are in arXiv:2604.00071.

**A static anchor.** We evolved the static drainhole with $\eta_0=2$, $\gamma=-\pi$ (so $\mu_+=1$). It collapses
through the known radial instability with an e-folding time $\tau\approx5.3$ (in units of $\mu_+$) and forms a
horizon. It reproduces our earlier production run to $5\times10^{-5}$.

**Our slow-rotation solver** (Python) solves the O(J²) member directly in the KK gauge:

- $\omega=J\,w_1(\eta)$, in closed form;
- $f=f_0+J^2[A(\eta)+B(\eta)P_2(\cos\theta)]$;
- $\nu=J^2n(\eta)\sin^2\theta$;
- $D^2=\eta_0^2+\mu_0^2+J^2\delta D^2$;
- Chebyshev collocation in $x$.

It is validated four ways:

- It matches Azad et al. (PLB 848, 138349 (2024), arXiv:2301.05243): their exact $h_0$ to $10^{-14}$, and their
  $\Delta M$.
- The full Einstein residuals (from a sympy Ricci tensor of the ansatz) fall as $J^4$, and the $t\varphi$ one as $J^3$.
- The symmetric member gives $\mu=3\pi J^2/\eta_0^3=2\omega_0J$, the KK Smarr relation.
- (13) and the constancy of $D^2$ hold to the collocation error.

**Where it stops.** On our drainhole ($\eta_0=2$, $\gamma=-\pi$) the full-Einstein residual of the table is about
$3\times10^{-5}$ at $J=0.25$. At $J=1$ it is about $(1\text{–}2)\times10^{-2}$; that member has $J/M^2=0.79$,
$v_e=0.24$, $M_{\rm ADM}=1.13$, and sits at 12 % of the extremal $J/A$ (extremal Kerr has $J/A=1/(8\pi)$). The
truncation error grows as $J^4$, so the solver is useless much beyond $J\approx1$.

**A side finding; check whether an erratum exists.** In Azad et al.'s O(J²) closed forms, the printed $\phi_{20}$ (eq.
2.7) is missing an overall factor $\phi(r)$. Their $w$, $h_0$ and $b_0$ are exact. We found this by an exact
symbolic check of all four O(J²) $\ell=0$ equations.

**Live runs (interim, 2026-10-12).** These are the first 3D evolutions of rotating EB wormholes, at $J=0.25$ (3 % of
the extremal $J/A$) and $J=1$ (12 %).

- So far $J=0.25$ collapses like the static run to three digits.
- $J=1$ differs from it at the 5 % level.

**What theory predicts.** Azad et al., PRD 109, 124051 (2024), arXiv:2403.08387, find:

- the static unstable mode weakens with spin while a second mode strengthens;
- the two cross or merge near one third of the maximal scaled $J$.

The charged analogue (Blázquez-Salcedo et al., arXiv:2510.11406) suggests the instability turns complex
(oscillating) and fades only near the extremal limit. Testing these predictions needs backgrounds at 20–95 % of the
extremal $J/A$, hence this search.

## 3. What a usable solver must deliver

- **Equations.** Exactly the KK system above: Einstein gravity plus one real, massless phantom scalar, with no
  potential and no extra matter. Fully nonlinear, not perturbative.
- **Families.**
  - Ours: $\eta_0=2$, $\gamma=-\pi$ (static $\mu_+=1$), with rotation raised through $\omega_{-\infty}$ (or $D$)
    from static to $v_e\approx0.95$.
  - The symmetric family, $\gamma=0$, to benchmark against KK and CKK.
  - Any $\eta_0$ will do, because the solutions scale.
- **Accuracy.**
  - All Einstein residuals $\lesssim10^{-6}$ everywhere, including the throat, the axis and both ends; spectral
    $\lesssim10^{-10}$ is preferred.
  - $D^2$ constant to the same level.
  - Convergence with resolution shown.
- **Output.**
  - $f$, $\nu$, $\omega$, $\partial_\eta\omega$, $\partial_\theta\omega$ and $D$ on a grid in $x$ and $\theta$, or
    as spectral coefficients.
  - We resample onto our own table: uniform $x\in[-1,1]$ (1025 points) by $\mu=\cos\theta\in[0,1]$ (65 points).
- **Compute.**
  - A Linux CPU node, with no GPU.
  - A few GB per process within a 24-core quota.
  - Minutes to an hour per solution.
  - Python, C/C++, Fortran or Julia. Mathematica or Maple only as a last resort: a licence is not guaranteed.
- **Licence.** It must be usable inside an academic research code that we publish. Open source is preferred. A
  proprietary package such as FIDISOL/CADSOL counts only if we can actually obtain it.

## 4. Research questions, in priority order

**Q1. Direct hits.** Is there any public code or data for rotating Ellis, Ellis–Bronnikov or "drainhole" phantom
wormholes in 4D (the KK family)?

- Include other groups that recomputed or borrowed these backgrounds for quasinormal modes, shadows, lensing,
  accretion disks, geodesics or tidal studies. Check their code and data-availability statements.
- Include Mathematica notebooks, Fortran, Julia and Python.
- Include "available on request" statements.

**Q2. The source group's method.** What code produced the backgrounds in each of these papers?

- KK 2014;
- CKK 2016;
- Khoo et al., *Quasinormal modes of rapidly rotating Ellis-Bronnikov wormholes*, PRD 109, 084013 (2024),
  arXiv:2401.02898;
- Hoffmann et al., *Wormholes immersed in rotating matter*, arXiv:1712.02143;
- any later rotating-wormhole work from the Oldenburg/Madrid group (Kunz, Kleihaus, Blázquez-Salcedo, Khoo, Azad,
  Chew).

For each, give:

- the method: FIDISOL/CADSOL finite differences with Newton–Raphson, or a spectral code;
- the grid and compactification, the quoted accuracy and the continuation strategy;
- whether any of it is public or has been shared with other groups.

PhD theses of these authors often describe the code in detail.

**Q3. Open codes we could adapt.** These are codes that solve stationary axisymmetric Einstein (or Einstein–matter)
equations in a Lewis–Papapetrou or quasi-isotropic ansatz, with Newton iteration. Look for:

- rotating boson stars;
- Kerr black holes with scalar or Proca hair;
- rotating stars;
- black holes in scalar–Gauss–Bonnet gravity;
- rotating wormholes with extra fields or in modified gravity;
- 5D rotating wormholes.

For each candidate, give:

- the repository URL, licence, language and last activity;
- its ansatz and gauge;
- its domain: does it allow a radial coordinate over all of $\mathbb R$ with two asymptotic ends, or only
  $r\in[r_H,\infty)$?
- its method: discretization, Newton, continuation;
- the effort to switch it to our equations.

Names to check (not exhaustive):

- Kadath and FUKA (Grandclément et al.), LORENE, the RNS code, XNS, Elliptica, SGRID, COCAL, TwoPunctures,
  NRPyElliptic, and the SpECTRE elliptic solver;
- the boson-star and hairy-black-hole solvers behind work by Herdeiro & Radu, Siemonsen & East, Sanchis-Gual et al.,
  Evstafyeva et al., Collodel et al., and Doneva & Yazadjiev;
- Einstein–DeTurck stationary solvers (Dias, Santos & Way, CQG 33, 133001 (2016), arXiv:1510.02804).

**Q4. Frameworks for writing our own.** Which tools would make our own solver quick and robust? For example:

- Dedalus (nonlinear boundary-value problems in Chebyshev and Fourier bases), Chebfun, Firedrake or FEniCS, PETSc
  SNES;
- Julia's ApproxFun or NonlinearSolve;
- pseudo-arclength continuation: BifurcationKit.jl, pde2path, AUTO.

Which of these have been used for stationary GR solutions? Which cope with the fold and with the steep gradients near
extremality, where the throat becomes a degenerate horizon? CKK rescale to $z=\arctan(2\omega_0\eta)$ there.

**Q5. Analytic or semi-analytic routes.** Given the vacuum-Ernst structure on the two-sheeted Weyl space (Section 1),
does any construction reproduce the KK family, or approximate it well enough to seed Newton? Candidates include:

- Ehlers or Hoenselaers–Kinnersley–Xanthopoulos transformations;
- Belinski–Zakharov inverse scattering;
- Sibgatullin's method;
- Eris–Gürses-type superposition of a scalar onto a vacuum solution;
- Matos & Núñez (CQG 23, 4485 (2006));
- Gibbons & Volkov's ring wormholes;
- Clément's rotating wormholes.

M. S. Volkov, PRD 104, 124064 (2021), is said to show that no closed form exists. Confirm this, and look for
anything newer (2022–2026).

**Q6. Validation benchmarks.** Extract every quantitative datum about the KK family that a new solver can be checked
against:

- **Numbers in text or tables.** For example, CKK Sec. IV.C has $\eta_0=1$, $\omega_{-\infty}=0.5$ on the upper
  branch, $\gamma=2,1,0,-1$, giving $D=0.33984$, $0.43155$, $0.55277$, $0.71636$.
- **Relations.** The ergoregion relation $\arctan(\eta_{\rm ergo}/\eta_0)=\arccos(2\omega_0)$; the Smarr relations;
  the extremal-limit values ($\mu_+/R_e=J_+/R_e^2=1/2$ at fixed $R_e$).
- **Curves worth digitizing.** KK 2014 Fig. 1; CKK Figs. 1, 2 and 11–14; any tables in Khoo et al. 2024 or later
  papers.

**Q7. Field status, 2024–2026.**

- Has anyone computed non-perturbative radial modes of rapidly rotating EB wormholes?
- Has anyone evolved a rotating wormhole nonlinearly in 3D?
- Is there an erratum to Azad et al. 2024 (the $\phi_{20}$ factor)?
- List the papers we must obtain, with arXiv IDs.

## 5. Search hints

**Terms for code and full-text search:**

- Wormholes: "Ellis wormhole", "Ellis-Bronnikov", "drainhole", "phantom scalar", "phantom field", "rotating wormhole",
  "spinning wormhole", "Kleihaus", "Kunz".
- Ansatz: "quasi-isotropic", "Lewis-Papapetrou", "Weyl-Papapetrou", "Ernst equation", "stationary axisymmetric".
- Related solvers: "boson star solver", "hairy black hole", "Kerr scalar hair", "FIDISOL", "CADSOL".
- Method: "Newton-Raphson", "Chebyshev collocation", "compactified coordinate".
- File contents: `eta0`, `omega_inf`, `h = eta**2 + eta0**2`.

**Places to look:**

- GitHub, GitLab (including institutional instances), Bitbucket, Codeberg;
- Zenodo, Software Heritage;
- arXiv ancillary files, and PRD, CQG and JCAP supplements;
- the Oldenburg, Madrid and Aveiro group pages, and theses.

**Exclude** these, unless their code would make a good base to adapt:

- Teo-type or "Kerr-like" wormhole metrics that do not solve the Einstein–phantom equations (Teo 1998; Bueno et al.
  2018; Damour & Solodukhin);
- thin-shell constructions;
- wormholes whose angular momentum is carried by a complex scalar.

## 6. Deliverable

1. **A verdict in one paragraph:** does a usable public solver or dataset exist? Yes, no, or partly.
2. **A ranked list of candidates.** For each: name, URL (opened), licence, language, last commit, what it solves,
   how far it is from our equations, estimated effort to adapt, and risks.
3. **An adaptation plan for the top one or two.** Name the files and functions that hold the equations, the
   boundary conditions and the continuation. Say how to validate against our O(J²) results and the KK/CKK numbers.
4. **If building from scratch is best, a recommended method:** discretization, Newton and Jacobian, continuation
   parameter, and resolution near extremality. Cite work that used the method on similar problems.
5. **The benchmark list from Q6,** with sources.
6. **Papers to obtain** (arXiv IDs), and any 2024–2026 work that overlaps our goals (Q7).

Cite every claim. Mark anything you could not verify.
