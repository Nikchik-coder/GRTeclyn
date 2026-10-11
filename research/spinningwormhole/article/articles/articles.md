Spinning Ellis wormholes: the three source papers in this folder, converted from their arXiv LaTeX sources. Equation, section, figure, table and citation numbers are those of the PDFs; figures appear as their captions only; each paper keeps its own reference list.

1. Rotating Ellis Wormholes in Four Dimensions (Burkhard Kleihaus, Jutta Kunz; arXiv:1409.1503v1 [gr-qc], 4 Sep 2014)
2. Geometry of Spinning Ellis Wormholes (Xiao Yan Chew, Burkhard Kleihaus, Jutta Kunz; arXiv:1608.05253v1 [gr-qc], 18 Aug 2016)
3. Are slowly rotating Ellis-Bronnikov wormholes stable? (Bahareh Azad, Jose Luis Blázquez-Salcedo, Fech Scen Khoo, Jutta Kunz; arXiv:2301.05243v2 [gr-qc], 23 Nov 2023)

---

# Rotating Ellis Wormholes in Four Dimensions

Burkhard Kleihaus, Jutta Kunz — arXiv:1409.1503v1 [gr-qc], 4 Sep 2014

## Abstract

We present rotating wormhole solutions in General Relativity, which are supported by a phantom scalar field. These solutions evolve from the static Ellis wormhole, when the throat is set into rotation. As the rotational velocity increases, the throat deforms until at a maximal value of the rotational velocity, an extremal Kerr solution is encountered. The rotating wormholes attain a finite mass and quadrupole moment. They exhibit ergospheres and possess bound orbits.

## 1 Introduction

Lorentzian wormholes are supposed to provide connections either between otherwise separate universes or within a single universe. These wormholes should not possess horizons, like the Einstein-Rosen bridge [1] or physical singularities. Instead they should be smooth solutions of the Einstein-matter equations with a nontrivial topology.

The simplest such wormhole is the Ellis wormhole [2–4]. Its throat is held open by the presence of a phantom field, i.e., a scalar field with a reversed sign in front of its kinetic term. In Einstein gravity this choice of sign is necessary in order to provide the required violation of the energy conditions. This was discussed in detail by Morris and Thorne [5, 6], whose motivation was to obtain traversable wormhole solutions in General Relativity. In recent years phantom fields have become ubiquitous in cosmology, providing one of the explanations for the observed accelerated expansion of the Universe [7].

While wormholes present a fascinating subject with their potential impact on space travel and the possibility of time travel [5, 8], they may also be viewed more mundane as potential astrophysical objects that may be searched for observationally [9–11]. In this respect, wormholes have for instance been considered as gravitational lenses, as first addressed in [12, 13], whose Einstein rings [14] or shadows [15, 16] have been studied. But also neutron star–wormhole systems and their possible astrophysical signatures have been addressed [18–21].

Astrophysical objects generically carry spin. However, all of the smooth wormhole solutions of the Einstein-matter equations obtained so far (in four space-time dimensions), are either static or slowly rotating perturbative solutions [22, 23][^p1-1]. Thus we here present for the first time a family of globally regular stationary wormhole solutions. These represent the rotating generalizations of the Ellis wormholes. We determine their domain of existence and analyze their physical properties. We note, that the family of rotating wormholes ends in an extremal Kerr black hole, and conclude, that it is a generic feature of families of wormholes in Einstein gravity to end in extremal black hole solutions.

## 2 The model

We consider Einstein gravity coupled to a phantom field $\Phi$ with action

$$
S=\int \left[ \frac{c^4}{16\pi G}R 
 + \frac{\hbar^2}{2 m_0} \partial_\mu \Phi \partial^\mu \Phi \right]
\sqrt{-g} d^4x
\ , \tag{1}
$$

where $R$ denotes the curvature scalar, $G$ is Newton’s constant, $g$ is the determinant of the metric, and $m_0$ represents a mass scale.

To construct stationary rotating wormhole solutions of this action we employ the line element

$$
ds^2 = -e^{f} c^2 dt^2 +p^2 e^{-f} 
\left( e^{\nu} \left[d{\eta}^2 +h d\theta^2\right]
                    + h \sin^2\theta \left(d\varphi -{\omega}dt\right)^2\right) \ , \tag{2}
$$

where $f$, $p$, $\nu$ and ${\omega}$ are functions only of ${\eta}$ and $\theta$, and $h={\eta}^2 + {\eta}_0^2$ is an auxiliary function. We note, that the coordinate ${\eta}$ takes positive and negative values, i.e. $-\infty< {\eta}< \infty$. The limits ${\eta}\to \pm\infty$ correspond to two distinct asymptotically flat regions. The phantom field $\Phi$ depends only on the coordinates ${\eta}$ and $\theta$, as well.

Substitution of these Ansätze into the Einstein equations leads to a system of non-linear partial differential equations (PDEs). The PDE for the function $p$ decouples and has a simple form

$$
p_{,{\eta},{\eta}} +\frac{3{\eta}}{h}p_{,{\eta}} + 
\frac{2 \cos\theta}{h\sin\theta}p_{,\theta}+
\frac{1}{h}p_{,\theta,\theta} = 0 \ . \tag{3}
$$

A solution which satisfies the boundary conditions $p({\eta}\to \infty) =p({\eta}\to -\infty) = 1$ and $p_{,\theta}(\theta =0) =p_{,\theta}(\theta =\pi) = 0$ is given by $p=1$.

For the phantom field we then find with $p=1$ the PDE

$$
\Phi_{,{\eta},{\eta}} +\frac{2{\eta}}{h}\Phi_{,{\eta}} + 
\frac{\cos\theta}{h\sin\theta}\Phi_{,\theta}+
\frac{1}{h}\Phi_{,\theta,\theta} = 0 \ . \tag{4}
$$

An explicit solution is $\Phi_{,{\eta}}=D/h$, where the constant $D$ represents the scalar charge of the wormhole solution.

The remaining equations yield a set of 3 PDEs for the functions $f$, $\nu$ and ${\omega}$ together with an equation for the scalar charge and a constraint equation. We solve these PDEs numerically, while monitoring the fulfillment of the constraint and the constancy of the scalar charge.

We here focus on symmetric wormholes, where $f$ and $\nu$ are even functions of ${\eta}$. Their throat is located at the hypersurface ${\eta}=0$, which represents a minimal surface. The equatorial radius $R$ of the throat is given by

$$
R = \left. \sqrt{g_{\varphi\varphi}}\right|_{{\eta}=0,\theta=\pi/2}
=e^{-f_0/2} {\eta}_0 \ , \tag{5}
$$

with $f_0=f({\eta}=0,\theta=\pi/2)$, while the polar radius $R_p$ and the areal radius $R_A$ are obtained via

$$
R_p  =\frac{{\eta}_0}{\pi} 
\int_0^\pi {\left. e^{(\nu-f)/2}\right|_{{\eta}=0}  d\theta} \ , \ \ \
R_A^2=\frac{{\eta}_0^2}{2}   
\int_0^\pi {\left. e^{\nu/2-f}\right|_{{\eta}=0} \sin \theta  d\theta} \ . \tag{6}
$$

Denoting the angular velocity of the throat by $\Omega={\omega}_0$, the dimensionless rotational velocity of the throat is given by

$$
v_e= \frac{R\Omega}{c} \ . \tag{7}
$$

The mass $M$ and angular momentum $J$ of the wormhole solutions are obtained from the asymptotic form of the metric tensor components

$$
g_{tt} \underset{{\eta}\to \infty} 
\longrightarrow - c^2\left(1-\frac{2GM}{c^2{\eta}}\right)  \ , \ \ \
g_{t\varphi} \underset{{\eta}\to \infty} 
\longrightarrow -\frac{2G J}{c^2}\frac{\sin^2\theta}{{\eta}} \tag{8}
$$

In order to establish a relation between the mass and the angular momentum, i.e., a Smarr-type relation, we consider the integrals

$$
\begin{aligned}
I_M   & =   \frac{c^4}{4\pi G}\int_\Sigma R_{\mu\nu} n^\mu \xi^\nu dV
=\frac{1}{8\pi G}\int{\left.\left[ c^2 h f_{,{\eta}} \sin\theta
                            -h^2 {\omega}{\omega}_{,{\eta}} e^{-2 f}\sin^3\theta 
                        \right]\right|_0^\infty d\theta d\varphi} \ , && \qquad (9) \\
I_J   & =   -\frac{c^4}{8\pi G}\int_\Sigma R_{\mu\nu} n^\mu \psi^\nu dV
=\frac{1}{16\pi G}\int{\left. \left[c^3 h^2 {\omega}_{,{\eta}} e^{-2 f}\sin^3\theta 
                        \right]\right|_0^\infty d\theta d\varphi} \ . && \qquad (10)
\end{aligned}
$$

Here $\Sigma$ is a spatial hypersurface extending from the throat ${\eta}=0$ to the asymptotically flat region ${\eta}\to \infty$, $dV$ denotes its natural volume element and $n^\mu$ is normal on $\Sigma$. $\xi^\nu$ is the time-like Killing vector field normalized to one in the asymptotically flat region ${\eta}\to \infty$, and $\psi^\nu$ is the space-like Killing vector field. In evaluating the expressions Eqs. 9-10, we have taken into account that the solutions are regular on the symmetry axis and possess reflection symmetry with respect to the equatorial plane. On the other hand the integrals have to vanish as a consequence of the Einstein equations. This yields for Eq. (10)

$$
\int{c^3 \left[h^2 {\omega}_{,{\eta}} e^{-2 f}\right]_{{\eta}=0}
\sin^3\theta  d\theta d\varphi}
= - 16 \pi c G J \ , \tag{11}
$$

while substitution of this result in Eq. (9) leads to the desired mass relation

$$
M c^2 = 2 {\omega}_0 J \ \ \ \Longleftrightarrow \ \ \
\frac{M}{M_0} = \frac{\Omega}{\Omega_0}\frac{J}{J_0} \ , \tag{12}
$$

where $M_0= {Rc^2}/{G}$, $\Omega_0={c}/{R}$ and $J_0= {R^2c^3}/{2G}$.

To better understand the wormhole solutions we now turn to the discussion of the second asymptotic limit, ${\eta}\to -\infty$. As already noted for the perturbative solutions [22, 23], the function ${\omega}$ cannot tend to zero in both asymptotically flat regions, ${\eta}\to \infty$ and ${\eta}\to -\infty$. To see this in the general case, we express the PDE for ${\omega}$ in the form of a conservation law

$$
\left(h^2 e^{-2f} \sin^3\theta {\omega}_{,{\eta}}\right)_{,{\eta}}
+\left(h   e^{-2f} \sin^3\theta {\omega}_{,\theta}\right)_{,\theta} = 0 \tag{13}
$$

and integrate over the full range of ${\eta}$ and $\theta$. Since ${\omega}_{,\theta}(0)=0={\omega}_{,\theta}(\pi)$ we are left with

$$
\int_0^{\pi}\left[h^2 e^{-2f} 
\sin^3\theta {\omega}_{,{\eta}}\right]_{{\eta}\to -\infty}
d \theta = 
\int_0^{\pi}\left[h^2 e^{-2f} 
\sin^3\theta {\omega}_{,{\eta}}\right]_{{\eta}\to \infty}
d \theta 
\propto J \ . \tag{14}
$$

Hence, both limits are regular and non-vanishing for rotating wormholes. Next we multiply Eq. (13) by ${\omega}$ and integrate again. This yields

$$
\int_0^{\pi}\left[h^2 e^{-2f} \sin^3\theta 
{\omega}{\omega}_{,{\eta}}\right]^{{\eta}\to \infty}_{{\eta}\to -\infty}
d \theta 
=
\int\left[h^2 e^{-2f} \sin^3\theta 
\left({\omega}_{,{\eta}}^2+\frac{1}{h}
{\omega}_{,\theta}^2\right)\right]d{\eta}d\theta > 0 \ . \tag{15}
$$

Since the term $h^2 e^{-2f} {\omega}_{,{\eta}}$ is bounded (in magnitude) from above in both limits, the function ${\omega}$ has to be non-zero in (at least) one of the asymptotic regions. We note, that one can always arrange ${\omega}(\infty)=0$ by adding a suitable constant. In this case ${\omega}(-\infty)= 2 {\omega}_0$. Still, the region ${\eta}\to -\infty$ is asymptotically flat, as one can see by means of a simple coordinate transformation. In that case, ${\omega}(\infty)\to - 2 {\omega}_0$.

## 3 Numerical results

> **Figure 1.** (a) The dimensionless mass $M/M_0$ and angular momentum $J/J_0$ versus the dimensionless rotational velocity $v_e$ for symmetric wormhole solutions. Validity of the Smarr-type relation Eq. (12) is also demonstrated for the wormhole solutions. (b) The polar radius $R_p/R$ and areal radius $R_A/R$ for fixed equatorial radius $R$ versus $v_e$. The crosses mark the onset of a negative Gaussian curvature at the poles. The black dots at $v_e=1$ in (a) and (b) correspond to the values of the extremal Kerr black hole. For comparison the respective curves for the full set of Kerr solutions are also shown (note that $M/M_0=1/2$ in (a)).

We exhibit in Fig. 1(a) the dimensionless mass and angular momentum of the family of symmetric rotating wormholes, evolving from the static Ellis wormhole. As the dimensionless rotational velocity $v_e$ reaches its maximal value, $v_e=1$, the hypersurface ${\eta}=0$ changes its character and a degenerate horizon forms. The limiting configuration represents an extremal Kerr black hole.

The scalar charge on the other hand is a monotonically decreasing function of $v_e$, which vanishes in the limit $v_e=1$, as it should for a Kerr black hole. Indeed, the phantom field vanishes identically in the limit. Accordingly, the Smarr-type relation (12) holds for Kerr black holes in the extremal limit, when ${\omega}_0$ denotes the horizon angular velocity.

When the spherically symmetric Ellis wormhole is set into rotation, the throat deforms. In particular, as seen in Fig. 1(b), the ratio of the polar radius to the equatorial radius $R_p/R$ decreases monotonically and assumes the value of the ratio of the corresponding extremal Kerr horizon radii in the limit $v_e \to 1$. The same holds for the areal radius $R_A$. Beyond a certain value of $v_e$ the Gaussian curvature turns negative at the poles of the throat, as indicated by the crosses in the figure. Interestingly, this occurs for the same value of the ratio $R_p/R$ for the wormholes as for the Kerr black holes, and likewise for the ratio $R_A/R$.

Following [23] we consider the violation of the null energy condition (NEC) by evaluating the quantity $\Xi = R_{\mu\nu} k^\mu k^\nu$ with null vector $k^\mu = \left(e^{-f/2}, e^{f/2-\nu/2}, 0, \omega e^{-f/2}\right)$. Since $\Xi$ is non-positive the NEC is violated everywhere. Introducing a global scale invariant measure for the NEC violation, $Y = \frac{1}{R}\int{\Xi \sqrt{-g} d\eta d\theta d\varphi}$, we observe a monotonic decrease of $|Y|$ with increasing rotation velocity $v_e$.

> **Figure 2.** (a) The dimensionless moment of inertia $I/M^3$ versus the dimensionless quadrupole moment $QM/J^2$. The black dot at $\nu_e=1$ corresponds to the value of the extremal Kerr black hole. (b) Quadrant of the ergoregion and the throat in coordinates $r$ and $\theta$ for fixed $\varphi$, ${\eta}_0=1$ and several values of ${\omega}_0$.

To extract the quadrupole moment $Q$ of the rotating wormhole solutions we follow Geroch and Hansen [25, 26] and extract it from the asymptotic expansion in appropriate coordinates (see e.g. [27]). We recall, that the dimensionless quadrupole moment $QM/J^2$ of the Kerr solutions is constant, $QM/J^2=1$. The dimensionless quadrupole moment $QM/J^2$ of the family of rotation wormhole solutions is shown in Fig. 2(a). It is smaller than the Kerr value for slow rotation while it exceeds the Kerr value for fast rotation. In the limit $v_e \to 1$, however, the Kerr value is attained. The dimensionless moment of inertia of the Kerr solutions is bounded and given by ${I/M^3}_{\rm Kerr}=2(1+\sqrt{1-J^2/M^4})$. For rotating wormholes, however, ${I/M^3}$ rises without bound in the limit of slow rotation, since the static Ellis wormhole has $M=0$.

Rotating wormholes possess an ergoregion, defined by the condition $g_{tt}> 0$,

$$
g_{tt}= -e^{f} c^2 +e^{-f} h \sin^2\theta {\omega}^2 > 0 \ . \tag{16}
$$

While the rotation axis is excluded from the ergoregion, its boundary in the equatorial plane is closely related to the angular velocity $\omega_0$ of the throat. The numerical calculations yield with high accuracy the relation $\arctan({\eta}_{\rm ergo}/{\eta}_0)= \arccos(2 \omega_0)$. Thus an ergoregion exists in the asymptotically flat region, where ${\omega}\to 0$, only for sufficiently fast rotation, while there always exists an ergoregion in the asymptotically flat region, where ${\omega}$ tends to a finite value. The ergoregion is exhibited in Fig. 2(b).

> **Figure 3.** Embedding diagram of the bound orbit of a test particle in the equatorial plane of a rotating wormhole ($v_e=0.966$).

In contrast to the static Ellis wormhole, rotating wormholes possess stable bound orbits. Indeed, there are two types of bound orbits, those that always remain within a single universe, and those that oscillate between the two universes. An example of such a two-world bound orbit is seen in Fig. 3. For corotating orbits the innermost stable circular orbit (ISCO) resides at the throat. For counterrotating orbits, however, the radius of the ISCO depends on the rotation velocity, with the ratio $R_{\rm ISCO}/R$ increasing almost by a factor of two from the static limit to the extremal Kerr black hole. At the same time the ratio of the orbital period $T_{\rm ISCO}/T$, where $T$ denotes the orbital period of the throat (or the horizon of the extremal black hole), increases roughly by a factor of three.

## 4 Conclusions

While wormholes with phantom fields have been studied in numerous respects (see e.g. [6]), we have here provided the first globally regular rotating wormhole solutions and analyzed their physical properties, such as their global charges including their quadrupole moments and moments of inertia, as well as the properties of their throats. In particular, we obtained a Smarr-type relation for these wormholes.

With increasing rotation velocity the violation of the NEC decreases. The family of rotating wormholes then ends in an extremal Kerr black hole. We note, that it seems to be a generic feature, that the families of generalized Ellis wormholes end in an extremal black hole. In particular, charged static Ellis wormholes in 4 dimensions end in an extremal Reissner-Nordström black hole [28], while rotating Ellis wormholes in 5 dimensions end in an extremal Myers-Perry black hole [29].

While the solutions presented are symmetric, in general rotating wormholes need not be symmetric. By choosing non-symmetric boundary conditions for the metric function $f$, families of rotating wormholes emerge, which have different masses associated to their two asymptotically flat regions, as manifest already in the static case. As the asymmetry increases, the wormhole properties change. But no matter how asymmetric the solutions are, these families always appear to end in an extremal Kerr black hole.

Concerning the stability of the wormhole solutions, it is known that the static Ellis wormholes are unstable [30–32]. However, it has been argued, that rotating wormholes might be stable [33]. Indeed, a stability analysis of five-dimensional rotating wormholes has shown, that the unstable mode of the static solutions disappears, when the rotation is sufficiently fast [29]. Whether this will happen as well in four dimensions still needs to be shown. On the other hand, stability might also be achieved by allowing higher curvature terms in the action [34, 35].

### Acknowledgment

We gratefully acknowledge support by the DFG Research Training Group 1620 “Models of Gravity”.

## References

[1] A. Einstein, N. Rosen, Phys. Rev. **48** (1935) 73.

[2] H. G. Ellis, J. Math. Phys. **14**, 104-118 (1973).

[3] H. G. Ellis, Gen. Rel. Grav. **10**, 105-123 (1979).

[4] K. A. Bronnikov, Acta Phys. Polon. **B4**, 251-266 (1973).

[5] M. S. Morris, K. S. Thorne, Am. J. Phys. **56**, 395-412 (1988).

[6] M. Visser, “Lorentzian wormholes: From Einstein to Hawking.” - Woodbury, New York, 1996. - 412 p.

[7] F. S. N. Lobo, Phys. Rev. D **71**, 084011 (2005).

[8] M. S. Morris, K. S. Thorne and U. Yurtsever, Phys. Rev. Lett. **61**, 1446 (1988).

[9] F. Abe, Astrophys. J. **725**, 787 (2010).

[10] Y. Toki, T. Kitamura, H. Asada and F. Abe, Astrophys. J. **740**, 121 (2011).

[11] R. Takahashi and H. Asada, Astrophys. J. **768**, L16 (2013).

[12] J. G. Cramer, R. L. Forward, M. S. Morris, M. Visser, G. Benford and G. A. Landis, Phys. Rev. D **51**, 3117 (1995).

[13] V. Perlick, Phys. Rev. D **69**, 064017 (2004).

[14] N. Tsukamoto, T. Harada and K. Yajima, Phys. Rev. D **86**, 104062 (2012).

[15] C. Bambi, Phys. Rev. D **87**, 107501 (2013).

[16] P. G. Nedkova, V. K. Tinchev and S. S. Yazadjiev, Phys. Rev. D **88**, no. 12, 124019 (2013).

[17] C. Armendariz-Picon, Phys. Rev. **D65**, 104010 (2002).

[18] V. Dzhunushaliev, V. Folomeev, B. Kleihaus and J. Kunz, JCAP **1104**, 031 (2011).

[19] V. Dzhunushaliev, V. Folomeev, B. Kleihaus and J. Kunz, Phys. Rev. D **85**, 124028 (2012).

[20] V. Dzhunushaliev, V. Folomeev, B. Kleihaus and J. Kunz, Phys. Rev. D **87**, 104036 (2013).

[21] V. Dzhunushaliev, V. Folomeev, B. Kleihaus and J. Kunz, Phys. Rev. D **89**, 084018 (2014).

[22] P. E. Kashargin and S. V. Sushkov, Grav. Cosmol. **14**, 80 (2008).

[23] P. E. Kashargin and S. V. Sushkov, Phys. Rev. D **78**, 064071 (2008).

[24] E. Teo, Phys. Rev. D **58**, 024014 (1998).

[25] R. P. Geroch, J. Math. Phys. **11**, 2580 (1970).

[26] R. O. Hansen, J. Math. Phys. **15**, 46 (1974).

[27] B. Kleihaus, J. Kunz and S. Mojica, Phys. Rev. D, in press, arXiv:1407.6884 [gr-qc].

[28] O. Hauser, R. Ibadov, B. Kleihaus and J. Kunz, Phys. Rev. D **89**, 064010 (2014).

[29] V. Dzhunushaliev, V. Folomeev, B. Kleihaus, J. Kunz and E. Radu, Phys. Rev. D **88**, 124028 (2013).

[30] H. -a. Shinkai and S. A. Hayward, Phys. Rev. D **66**, 044005 (2002).

[31] J. A. Gonzalez, F. S. Guzman, and O. Sarbach, Class. Quant. Grav. **26**, 015010 (2009).

[32] J. A. Gonzalez, F. S. Guzman, and O. Sarbach, Class. Quant. Grav. **26**, 015011 (2009).

[33] T. Matos and D. Nunez, Class. Quant. Grav. **23**, 4485 (2006).

[34] P. Kanti, B. Kleihaus and J. Kunz, Phys. Rev. Lett. **107**, 271101 (2011).

[35] P. Kanti, B. Kleihaus and J. Kunz, Phys. Rev. D **85** (2012) 044007.

[^p1-1]: Note, that the Teo wormhole [24] is not a solution of the Einstein-matter equations.

---

# Geometry of Spinning Ellis Wormholes

Xiao Yan Chew, Burkhard Kleihaus, Jutta Kunz — arXiv:1608.05253v1 [gr-qc], 18 Aug 2016

## Abstract

We give a detailed account of the properties of spinning Ellis wormholes, supported by a phantom field. The general set of solutions depends on three parameters, associated with the size of the throat, the rotation and the symmetry of the solutions. For symmetric wormholes the global charges possess the same values in both asymptotic regions, while this is no longer the case for non-symmetric wormholes. We present mass formulae for these wormholes, study their quadrupole moments, and discuss the geometry of their throat and their ergoregion. We demonstrate, that these wormholes possess limiting configurations corresponding to an extremal Kerr black hole. Moreover, we analyze the geodesics of these wormholes, and show that they possess bound orbits.

## I. Introduction

General Relativity allows for Lorentzian wormholes [1], which can be either non-traversable or traversable. Non-traversable wormholes were first discussed in 1935 by Einstein and Rosen [2]. Here the famous ‘Einstein-Rosen bridge’ represents an interesting feature of the Schwarzschild spacetime, connecting two asymptotically flat universes by a throat. In the 1950’s Wheeler discussed the intriguing possibility to connect two distant regions within a single universe [3, 4]. Unfortunately, this kind of wormholes does not allow for their passage [5–9].

Transversable wormholes in General Relativity were first obtained by Ellis [10, 11] and Bronnikov [12] (see also [13]). However, these need the presence of a new kind of matter field coupled to gravity. Such a phantom field carries the wrong sign in front of its kinetic term, and consequently its energy-momentum tensor violates the null energy condition. The conditions for the existence of traversable wormholes as well as the properties of such static wormholes were discussed later in detail by Morris and Thorne [14], who addressed also the possibility of time-travel [15].

While phantom fields have been employed frequently in cosmology in recent years, since they give rise to an accelerated expansion of the Universe [16], it was also pointed out [17–23], that the presence of a phantom field can be evaded in the construction of wormholes, when gravity theories with higher curvature terms are considered.

Wormholes have also been considered from an astrophysical point of view, since they represent hypothetical objects that can be searched for observationally [24–26]. Cramer et al. [27] and Perlick [28], for instance, have investigated wormholes as gravitational lenses, Tsukamoto et al. have addressed the Einstein rings of wormholes [29], Bambi [30] and Nedkova et al. [31] have studied the shadow of wormholes, while Zhou et al. [32] determined the iron line profile in the X-ray reflected spectrum of a thin accretion disk around wormholes. The astrophysical signatures of mixed neutron star–wormhole systems have been addressed by Dzhunushaliev et al. [33–38].

Here we consider rotating wormholes supported by a phantom field, which represent solutions of the coupled Einstein-phantom field equations. Slowly rotating perturbative solutions of these equations were obtained by Kashargin and Sushkov [39, 40]. This was followed by a brief discussion of rapidly rotating non-perturbative wormholes given by two of us [41]. In the present paper we give a detailed account of the properties of these rotating wormholes. Moreover, we discuss rotating non-symmetric wormholes for the first time. Let us note, that the rotating wormhole metric presented by Teo [42] was not obtained as a solution of a coupled system of Einstein-matter equations.

The paper is structured as follows. We begin with the theoretical setting in section II, which includes the presentation of the action and the Ansatz, the discussion of the equations of motion and the boundary conditions, the derivation of the global charges and mass formulae as well as the derivation of the quadrupole moment. We then give a discussion of the geometric properties of the wormholes, in particular, we define the position of the throat as a minimal surface, and we demonstrate the violation of the energy conditions.

Subsequently in section III we present our numerical results for symmetric wormholes, i.e., those wormholes whose global charges are the same on both sides of the wormhole. These wormholes then possess one less parameter. In particular, we consider families of wormhole configurations for fixed equatorial throat radius, and demonstrate that these solutions approach an extremal Kerr black hole, as the angular momentum tends towards its maximal value. We then exhibit embeddings of wormhole spacetimes and demonstrate, that the Gaussian curvature of the throat turns negative at the poles, when the rotation is sufficiently fast, analogously to the curvature of the horizon of Kerr black holes. Finally, we examine the effective potential and the geodesics of rotating wormholes, which in contrast to static Ellis wormholes allow for bound orbits.

Non-symmetric rotating wormholes are presented in section IV. They depend on three parameters, and have distinct properties when the asymmetry parameter $\gamma$ is negative or positive. We analyze the domain of existence of these non-symmetric wormholes, and demonstrate that the families of non-symmetric wormholes also approach an extremal Kerr black hole. We then address the somewhat surprising fact, that the rotational velocity of the throat can exceed the velocity of light for positive $\gamma$. We show how the location of the throat changes as the asymmetry of the solutions is varied. Finally, we consider embeddings of non-symmetric wormholes and geodesics in these spacetimes. We end with our conclusions in section V, and present the metric functions for large positive asymmetry parameter in the Appendix.

## II. Theoretical Setting

### A. Action and Ansatz

We now turn to wormhole solutions in General Relativity, obtained with a phantom field $\psi$. The corresponding action reads

$$
S= {1\over 16\pi G_{ }}\int d^4x \sqrt{-g} \left(R +
2g^{\mu\nu}\partial_{\mu}\psi \partial_{\nu}\psi 
  \right) \ , \tag{1}
$$

leading to the Einstein equations

$$
R_{\mu\nu} = - 2 \partial_\mu \psi \partial_\nu \psi 
      \ , \tag{2}
$$

and the phantom field equation

$$
\partial_\mu\left(\sqrt{-g}g^{\mu\nu}\partial_\nu \psi\right) =   0 \ . \tag{3}
$$

To construct stationary rotating spacetimes we employ the line element

$$
ds^2 = -e^{f} dt^2 +p^2 e^{-f} 
\left( e^{\nu} \left[d\eta^2 +h d\theta^2\right]
                    + h \sin^2\theta \left(d\phi -\omega dt\right)^2\right) \ , \tag{4}
$$

where $f$, $p$, $\nu$ and $\omega$ are functions only of $\eta$ and $\theta$, and $h=\eta^2 + \eta_0^2$ is an auxiliary function. We note that the coordinate $\eta$ takes positive and negative values, i.e. $-\infty< \eta < \infty$. The limits $\eta\to \pm\infty$ correspond to two distinct asymptotically flat regions. The phantom field $\psi$ also depends only on the coordinates $\eta$ and $\theta$.

### B. Equations of Motion and Boundary Conditions

When we substitute the above Ansatz into the general set of equations of motion we obtain a system of non-linear partial differential equations (PDEs). As observed in [41] the PDE for the function $p$ decouples, and has the simple form

$$
p_{,\eta,\eta} +\frac{3\eta}{h}p_{,\eta} + 
\frac{2 \cos\theta}{h\sin\theta}p_{,\theta}+
\frac{1}{h}p_{,\theta,\theta} = 0 \ . \tag{5}
$$

A solution which satisfies the boundary conditions $p(\eta \to \infty) =p(\eta \to -\infty) = 1$ and $\partial_\theta p(\theta =0) =\partial_\theta p(\theta =\pi) = 0$ is given by

$$
p=1 \ . \tag{6}
$$

Consequently, we obtain the phantom field equation

$$
\partial_\eta\left(h \sin\theta \partial_\eta \psi\right) 
+\partial_\theta\left(\sin\theta \partial_\theta \psi\right) 
=0 \ . \tag{7}
$$

A first integral can be obtained under the assumption $\partial_\theta \psi=0$,

$$
\partial_\eta \psi = \frac{D}{h}\ , \tag{8}
$$

where $D$ denotes the phantom scalar charge. This leads to the closed form solution for $\psi$

$$
\psi = D \left(\arctan(\eta/\eta_0)-\pi/2\right) \ , \tag{9}
$$

where the integration constant was chosen to satisfy $\psi(\infty) = 0$.

We now turn to the Einstein equations. With $p=1$ and $\partial_\theta \psi=0$ the equations $R_{\phi\phi}=0$, $R_{\theta\theta}=0$, $R_{t\phi}=0$, $R_{tt}=0$ and $R_{\eta\theta}=0$ are independent of the scalar field. They yield three second order PDEs for the functions $f$, $\omega$ and $\nu$, and a constraint,

$$
\begin{aligned}
0  & =   
 \partial_\eta\left( h \sin\theta \partial_\eta f\right)
+\partial_\theta\left( \sin\theta \partial_\theta f\right)
-h \sin^3\theta e^{-2 f}\left(h (\partial_\eta\omega)^2 
                              + (\partial_\theta\omega)^2 \right) \ , && \qquad (10) \\
0  & =   
 \partial_\eta\left(h^2\sin^3\theta e^{-2 f} \partial_\eta\omega\right)           
+\partial_\theta\left(h\sin^3\theta e^{-2 f} \partial_\theta\omega\right) \ , && \qquad (11) \\
0  & =   
 \partial_\eta\left( h \sin\theta \partial_\eta \nu\right)
 +\sin\theta \partial_{\theta\theta} \nu -\cos\theta \partial_\theta\nu
 -h \sin^3\theta e^{-2 f}\left(h (\partial_\eta\omega)^2 
                              -2 (\partial_\theta\omega)^2 \right) \ , && \qquad (12) \\
0  & =   
-h \sin\theta \partial_\eta f \partial_\theta f
+ h \cos\theta \partial_\eta \nu + \eta\sin\theta \partial_\theta \nu
+ h^2\sin^3\theta e^{-2 f}\partial_\eta \omega \partial_\theta \omega \ . && \qquad (13)
\end{aligned}
$$

In order to obtain regular solutions we have to impose boundary conditions in the asymptotic regions $\eta \to \pm \infty$ and on the axis $\theta = 0, \pi$. For $\eta \to +\infty$ we require the metric to approach Minkowski spacetime, i.e.,

$$
\left. f\right|_{\eta \to \infty} = 0 \ , \ 
\left. \omega\right|_{\eta \to \infty} = 0 \ , \ 
\left. \nu\right|_{\eta \to \infty} = 0 \ . \tag{14}
$$

In the limit $\eta \to -\infty$ we allow for finite values of the functions $f$ and $\omega$,

$$
\left. f\right|_{\eta \to -\infty} = \gamma \ , \ 
\left. \omega\right|_{\eta \to -\infty} = \omega_{-\infty} \ , \ 
\left. \nu\right|_{\eta \to -\infty} = 0 \ . \tag{15}
$$

We refer to the solutions as symmetric, when $\gamma=0$, and non-symmetric, when $\gamma \ne 0$. Note, that in the limit $\eta \to -\infty$ the spacetime becomes Minkowskian after a suitable coordinate transformation is performed. Regularity on the symmetry axis requires

$$
\left.\partial_\theta f\right|_{\theta = 0} = 0 \ , \ 
\left.\partial_\theta \omega \right|_{\theta = 0} = 0 \ , \ 
\left. \nu\right|_{\theta = 0} = 0 \ , \tag{16}
$$

together with the analogous conditions at $\theta = \pi$.

Static wormhole solutions correspond to $\omega_{-\infty}=0$. They are known in closed form,

$$
f = \frac{\gamma}{2} \left(1-\frac{2}{\pi}\arctan\left(\frac{\eta}{\eta_0}\right) \right) \ , \
\omega = 0  \ , \ \nu = 0  \ . \ \tag{17}
$$

Rotating wormhole solutions of the above equations have been studied in [41] for the symmetric case only, while we here address the non-symmetric case, as well. Substitution of the solutions for $f$, $\omega$ and $\nu$ in $R_{\eta\eta}$ shows, that

$$
R_{\eta\eta} = - 2\frac{D^2}{h^2} \ , \tag{18}
$$

where the scalar charge $D$ depends on the mass and the angular momentum of the spacetime. Explicitly we find

$$
D^2  =  \frac{h}{4}\left[ h  (\partial_\eta f)^2 - (\partial_\theta f)^2 \right]
         -\frac{h}{2}\left(\eta \partial_\eta \nu-
                      \frac{\cos\theta}{\sin\theta}\partial_\theta \nu\right)
         -\frac{h^2}{4}\sin^2\theta e^{-2 f}
     \left[ h (\partial_\eta\omega)^2 
               - (\partial_\theta\omega)^2 \right] +\eta_0^2 \ . \tag{19}
$$

### C. Mass, Angular Momentum and Mass Formulae

The mass and angular momentum of the wormhole solutions are engraved in the asymptotic form of the metric tensor. For an asymptotically flat metric, the mass and the angular momentum can be read off from the components $g_{tt}$ and $g_{t\varphi}$,

$$
g_{tt} \underset{\eta \to \pm \infty} 
\longrightarrow - \left(1\mp\frac{2\mu_\pm}{\eta}\right)  \ , \ \ \
g_{t\varphi} \underset{\eta \to \pm \infty} 
\longrightarrow -\frac{2 J_\pm  \sin^2\theta}{\eta} \ . \tag{20}
$$

In the limit $\eta \to +\infty$ the wormhole metric becomes Minkowskian, as seen from the asymptotic behavior of the metric functions. In particular,

$$
f \to -\frac{2 \mu_+}{\eta} \ , \ \ \ 
\omega \to \frac{2J_+}{\eta^3} \ , \ \ \ 
{\rm as} \ \eta \to +\infty \ , \tag{21}
$$

so we can read off the mass $\mu_+$ and the angular momentum $J_+$ directly.

The analogous asymptotic expansion at the other side of the wormhole reads

$$
f \to \gamma+\frac{2 \mu_-}{\eta}\ , \ \ \ 
\omega \to \omega_{-\infty}+ \frac{2J_-}{\eta^3}\ , \ \ \  

{\rm as } \ \eta \to - \infty \ . \tag{22}
$$

However, in order to identify the mass $\bar \mu_-$ and the angular momentum $\bar J_-$ at $\eta \to -\infty$, we first have to perform a coordinate transformation to obtain an asymptotically flat spacetime in this limit. After applying

$$
\bar t = e^{\gamma/2} t \ , \ \ \
\bar \eta = e^{-\gamma/2} \eta \ , \ \ \
\bar \phi = \phi - \omega_{-\infty} t \ , \tag{23}
$$

we obtain $\bar \mu_-$ and $\bar J_-$ in terms of the parameters $\mu_-$ and $J_-$,

$$
\bar J_- = J_- e^{-2\gamma} \ , \ \ \
\bar \mu_- = \mu_- e^{-\gamma/2} \ . \tag{24}
$$

Let us now derive some relations between the global charges. We first note that Eq. (11) is in the form of a conservation law, and integrate Eq. (11) over the full range of $\eta$ and $\theta$, $-\infty < \eta < \infty$, $0 < \theta < \pi$. This leads to

$$
\int_0^{\pi}\left[h^2 e^{-2f} 
\sin^3\theta \omega_{,\eta}\right]_{\eta\to \infty}
d \theta = 
\int_0^{\pi}\left[h^2 e^{-2f} 
\sin^3\theta \omega_{,\eta}\right]_{\eta\to -\infty}
d \theta \ . \tag{25}
$$

Inserting the asymptotic expansions for $\omega$ and $f$, Eqs. (21)-(22), we find

$$
J_+ = e^{-2\gamma} J_-    = \bar J_- \ . \tag{26}
$$

Thus the angular momenta on both sides of the wormhole are equal.

To derive a second relation, we multiply Eq. (11) by $\omega$ and substract it from Eq. (10). This yields again an equation in the form of a conservation law,

$$
\partial_\eta\left( h\sin\theta 
   \left[
   \partial_\eta f - e^{-2f} h \sin^2\theta \omega \partial_\eta\omega
   \right]\right)
+
\partial_\theta\left( \sin\theta 
   \left[
   \partial_\theta f - e^{-2f} h \sin^2\theta \omega \partial_\theta\omega
   \right]\right)
=0 \ . \tag{27}
$$

Integrating Eq. (27) and taking into account the asymptotic expansions Eqs. (21)-(22), we find

$$
\mu_+ + \mu_- = 2 \omega_{-\infty} e^{-2\gamma} J_- = 2 \omega_{-\infty} J_+ \ . \tag{28}
$$

For the static wormhole solutions (17), this relation reduces to $\mu_+ = - \mu_-$, where the mass $\mu_+$ is related to $\gamma$ by $\mu_+ = \gamma \eta_0 / 2 \pi$.

In the symmetric case, we regain a mass formula akin to the Smarr formula for black holes. Here we integrate both formulae from the throat ($\eta = 0$) to infinity, and take into account that $\partial_\eta f$ vanishes at the throat. Denoting $\omega(0) = \omega_0$, we find [41]

$$
\mu_+ = \omega_{-\infty} J_+ = 2 \omega_0 J_+ , \tag{29}
$$

where $\omega_{-\infty} = 2 \omega_0$ follows from the symmetry and the choice of boundary conditions. Consequently, also the relation $\mu_- = 2 \omega_0 J_-$ holds in this case. Thus on both sides of the wormhole the mass is the same. Note, that the mass relation (29) then agrees with the one for extremal Kerr black holes, when $\omega_0$ is identified with the horizon angular velocity.

To find a relation of $D^2$ to the mass we evaluate Eq. (19) in the limit $\eta \to \infty$. Here we must take into account the asymptotic behaviour of the function $\nu$,

$$
\nu \to - c_2 \frac{\sin^2\theta}{\eta^2} \ . \tag{30}
$$

This yields

$$
c_2  = \mu_+^2 +\eta_0^2 - D^2 \ , \tag{31}
$$

which reduces to $0 = \mu_+^2 +\eta_0^2 -D^2$ in the static case.

### D. Quadrupole Moment

In order to extract the quadrupole moment $Q$ of the rotating wormhole solutions, we need to consider the expansion of the metric in the asymptotic regions. For simplicity, let us only consider $\eta \to + \infty$ here. The asymptotic expansion of the metric functions is then given by

$$
\begin{aligned}
f  & =   -\frac{2 \mu_+}{\eta} +\frac{2}{3}\frac{ \mu_+\eta_0^2}{\eta^3}
+\frac{2}{3}\frac{2 \mu_+\eta_0^2 - 3 f_3}{\eta^3} P_2(\cos\theta)
+{\cal O}(\eta^{-4}) \ , && \qquad (32) \\
\nu   & =   -c_2 \frac{\sin^2\theta}{\eta^2} +{\cal O}(\eta^{-3})
 \ , && \qquad (33) \\
\omega   & =   2 \frac{J_+}{\eta^3} +{\cal O}(\eta^{-4})
 \ , && \qquad (34)
\end{aligned}
$$

where $P_2(\cos\theta)$ is the second Legendre polynomial and $f_3$ and $c_2$ are constants.

The quadrupole moment can now be derived employing the definitions of Geroch and Hansen [43, 44], and following later work [45–47] according to the steps outlined in [48] we first transform the metric to quasi-isotropic coordinates. This yields

$$
ds^2 = -e^f dt^2
+\left(1+\frac{r_0^2}{r^2}\right)^2 e^{-f}
\left[ e^\nu (dr^2 + r^2 d\theta^2) 
      +r^2 \sin^2\theta(d\phi - \omega dt)^2\right] \ , \tag{35}
$$

where $r$ is related to $\eta$ by $\eta/\eta_0 = (r/r_0-r_0/r)/2$, and $r_0=\eta_0/2$. We compare this with

$$
ds^2 = -e^{2\nu_0} dt^2
+e^{2(\nu_1-\nu_0)}
\left[ e^{2\nu_2} (dr^2 + r^2 d\theta^2) 
      +r^2 \sin^2\theta(d\phi - \omega dt)^2\right] \tag{36}
$$

and identify

$$
\nu_0 = f/2\ , \ \ \ 
e^{\nu_1} = 1+\frac{r_0^2}{r^2} \ , \ \ \ 
\nu_2 = \nu/2\ . \tag{37}
$$

Using the expansion $\eta^{-1} = r^{-1}(1+(r/r_0)^{-2} +{\cal O}((r/r_0)^{-4}))$ in the asymptotic region we find by comparison with Eqs. (A9)-(A11) in [48]

$$
\begin{aligned}
\nu_0  & =  
 -\frac{\mu_+}{r} +\frac{1}{12}\frac{\mu_+\eta_0^2 }{r^3}
+\frac{2 \mu_+\eta_0^2 - 3 f_3}{3 r^3} P_2(\cos\theta)
+{\cal O}(r^{-4}) \\
 & =  
 -\frac{\mu_+}{r} +\frac{1}{3}\frac{d_1 \mu_+}{r^3}
-\frac{M_2}{r^3} P_2(\cos\theta)
+{\cal O}(r^{-4}) 
\ , && \qquad (38) \\
\nu_1  & =   \frac{\eta_0^2}{4r^2} +{\cal O}(r^{-3}) \\
 & =  
  \frac{d_1}{r^2} +{\cal O}(r^{-3}) 
\ , && \qquad (39) \\
\nu_2  & =   
 -c_2 \frac{\sin^2\theta}{2 r^2} +{\cal O}(r^{-3}) \\
 & =  
 -\frac{4 \mu_+^2 +16 d_1 - q_2}{8 r^2} \sin^2\theta+{\cal O}(r^{-3})
\ , && \qquad (40)
\end{aligned}
$$

where we have slightly changed the notation of [48]: $D_1 \to d_1$, $q^2 \to -q_2$. Now $d_1$, $q_2$ and $M_2$ can be expressed in terms of $f_3$ and $c_2$,

$$
d_1 = \frac{\eta_0^2}{4} \ , \ \ \ 
q_2 = 4(\mu_+^2 +\eta_0^2 - c_2) = 4 D^2 \ , \ \ \ 
M_2 = f_3- \frac{2\mu_+\eta_0^2}{3}\ . \tag{41}
$$

Thus we finally arrive at the quadrupole moment

$$
Q = -f_3 + \mu_+\eta_0^2 +\frac{\mu_+(\mu_+^2 - D^2)}{3} \ \tag{42}
$$

(see e.g. [48] for more details).

### E. Geometric Properties

Let us next address the geometric properties of the wormhole solutions. We first consider the equatorial (or circumferential) radius ${R}_e(\eta)$ as a function of the radial coordinate

$$
{R}_e(\eta) = \sqrt{\eta^2+\eta_0^2}\left[e^{-f/2}\right]_{\theta=\pi/2} \ . \tag{43}
$$

Because of the rotation, the throat of the wormholes should deform and its circumference should be largest in the equatorial plane. Therefore a study of ${R}_e(\eta)$ should reveal the location of the throat in the equatorial plane.

Consequently, we define the throat of the wormhole as the surface of minimal area, which intersects the equatorial plane at the circle of minimal circumferential radius $R_e$, i.e.,

$$
R_e = \min_{-\infty \leq \eta \leq \infty}
\left\{ \sqrt{h} e^{-f/2} |_{\theta = \pi/2} \right\}
\ , \tag{44}
$$

for the line element Eq. (4).

We now parametrize the surface of the throat by $(\eta_t(\theta),\theta, \varphi)$. Then the line element on the surface reads

$$
d\sigma^2 = e^{-f+\nu} 
\left[\eta_t'^2 + h\right] d\theta^2
+e^{-f} h \sin^2\theta d\varphi^2 \ , \tag{45}
$$

where we defined $\eta_t' =d \eta_t/d\theta$, and the functions $f$, $\nu$ and $h$ are regarded as functions of $\eta_t$ and $\theta$. The area of the surface is now given by the integral of the square root of the determinant of the metric tensor

$$
A_\sigma = \int{L_\sigma} d\theta d\varphi \tag{46}
$$

with

$$
L_\sigma=\sqrt{\eta_t'^2 + h}
\sqrt{h}\sin\theta e^{-f+\nu/2} \ . \tag{47}
$$

The function $\eta_t(\theta)$ is determined as solution of the Euler-Lagrange equation

$$
\frac{d}{d\theta}\frac{\partial L_\sigma}{\partial \eta_t'} 
-\frac{\partial L_\sigma}{\partial \eta_t} = 0 \ . \tag{48}
$$

This yields the ordinary differential equation

$$
\eta_t''
+h \partial_\eta s - 2\eta_t
-\left[\partial_\theta s-\frac{\cos\theta}{\sin\theta}\right] \eta_t'
+\left[ \partial_\eta s - \frac{3\eta_t}{h}\right]\eta_t'^2
-\left[\partial_\theta s-\frac{\cos\theta}{\sin\theta}\right]\frac{1}{h} \eta_t'^3
=0  \ , \tag{49}
$$

where we introduced $s=f-\nu/2$. We solve this equation numerically for boundary conditions $\eta_t'(0)=0$, required by regularity, and $\eta_t(\pi/2) = \eta_e$, where $\eta_e$ is the coordinate of the throat in the equatorial plane, determined by the minimum condition for the circumferential radius.

We note that in the symmetric case the throat is located at the constant coordinate $\eta_t=0$, since $\eta_e=0$ and $\partial_\eta s =0$ at $\eta =0$ for all $\theta$. For the static wormholes $\nu=0$ and $\partial_\theta f=0$. In this case the minimum condition Eq. (44) yields $h \partial_\eta f- 2 \eta_e = 0$, which implies $h \partial_\eta s- 2 \eta_e = 0$ in Eq. (49). Consequently the solution of Eq. (49) is in this case $\eta_t=\eta_e$. Therefore the static non-symmetric wormholes also possess a throat with constant coordinate (as expected). For the rotating non-symmetric wormholes, however, it is not obvious, that the throat should be located at a constant radial coordinate, as well. Therefore the dependence of the coordinate $\eta_t$ on $\theta$ must be examined numerically. We further note, that we do not find rotating Ellis wormhole solutions with multiple throats, separated by bellies (or equators).

To gain further information on the geometry of the rotating symmetric wormholes, we consider in addition the polar radius $R_p$

$$
R_p  =\frac{\eta_0}{\pi} 
\int_0^\pi {\left. e^{(\nu-f)/2}\right|_{\eta=0}  d\theta} \ , \tag{50}
$$

and the areal radius $R_A$

$$
R_A^2=\frac{\eta_0^2}{2}   
\int_0^\pi {\left. e^{\nu/2-f}\right|_{\eta=0} \sin \theta  d\theta} \ . \tag{51}
$$

Denoting the angular velocity of the throat by $\Omega=\omega_0$, the rotational velocity of the throat in the equatorial plane is given by

$$
v_e= {R_e\Omega} \ . \tag{52}
$$

It was shown in [41] that $v_e\le 1$ for the symmetric wormholes.

### F. Violation of the Null Energy Condition

Let us next demonstrate the violation of the Null Energy Condition (NEC) and consider the quantity

$$
\Xi = R_{\mu\nu} k^\mu k^\nu \ , \tag{53}
$$

with null vector [40]

$$
k^\mu = \left(e^{-f/2}, e^{f/2-\nu/2}, 0, \omega e^{-f/2}\right) \ . \tag{54}
$$

Taking into account the Einstein equations and the phantom field equation we obtain

$$
\Xi = - 2 D^2\, \frac{e^{f-\nu}}{h^2}  \ . \tag{55}
$$

Since $\Xi$ is non-positive the NEC is violated everywhere. In order to obtain a global scale invariant quantity as measure of the NEC violation we define for later reference for the symmetric wormholes

$$
Y = \frac{1}{R_e}\int{\Xi \sqrt{-g} d\eta d\theta d\varphi} 
   =-8\pi \frac{D^2}{R_e} \int_0^\infty \frac{d\eta}{\eta^2+\eta_0^2}
   =-4\pi^2 \frac{D^2}{R_e \eta_0} \ . \tag{56}
$$

## III. Symmetric Wormholes

In the following we present the properties of symmetric rotating wormhole solutions in General Relativity, which are characterized by $\gamma=0$ [41]. We then continue with the non-symmetric case, where for fixed $\eta_0$ the solutions depend on the parameters $\gamma$ and $\omega_{-\infty}$.

### A. Global Charges

> **Figure 1.** Properties of symmetric rotating wormholes at fixed throat parameter $\eta_0=1$: the mass $\mu_+$ (a), the angular momentum $J_+$ (b), the scalar charge $D$ (c), and the angular velocity of the throat $\omega_0$ (d) versus the rotational velocity $v_e$ of the throat in the equatorial plane.

Symmetric rotating Ellis wormholes depend on the throat parameter $\eta_0$ and the angular velocity of the throat $\omega_0$. Let us first fix the throat parameter $\eta_0=1$ and vary $\omega_0$, starting from the static Ellis wormhole. Then the mass $\mu_+$ and angular momentum $J_+$ increase from their Ellis value of zero with increasing angular velocity. At the same time, the rotational velocity $v_e$ of the throat in the equatorial plane increases as it should, since it is proportional to $\omega_0$. The centrifugal force causes in addition an increase of the equatorial circumferential radius of the throat $R_e$ and thus of $v_e$.

We exhibit in Fig. 1 the dependence of the mass $\mu_+$ and the angular momentum $J_+$ on the rotational velocity $v_e$ for these wormholes. As the rotational velocity $v_e$ tends to its limiting value of one, where the throat would be rotating with the velocity of light the mass and the angular momentum both diverge. Also shown in Fig. 1 is the dependence of the scalar charge $D$ (we have chosen $D$ to be non-negative) on the rotational velocity $v_e$, and the relation between $\omega_0$ and $v_e$.

The scalar charge is maximal for static wormholes and decreases monotonically to zero, as the family of wormhole solutions approaches its limiting configuration, where the rotational velocity reaches the speed of light. The angular velocity of the throat, however, does not increase monotonically with $v_e$. Instead, it reaches a maximal value and then decreases again towards zero. The reason for the occurrence of two branches with respect to $\omega_0$ is our use of ‘isotropic’ coordinates. The analogous pattern arises for rotating black holes, when the isotropic horizon radius is held fixed, while the angular momentum increases monotonically (see e.g. [49]).

> **Figure 2.** Properties of symmetric rotating wormholes at fixed equatorial throat radius $R_e$: the scaled mass $\mu_+/R_e$, the scaled angular momentum $J_+/R_e^2$ and the quantity $2 \omega_0 J_+/R_e$ (a), the scaled scalar charge $D/R_e$ (b) versus the rotational velocity $v_e$ of the throat in the equatorial plane. Also shown are the respective curves for the Kerr black holes, while the black dots mark the respective extremal Kerr values.

To get a more physical picture of the families of symmetric rotating wormholes and better understand the limiting behavior for $v_e \to 1$, let us now fix the equatorial throat radius $R_e$. Then the family of symmetric rotating wormholes evolves from the static Ellis wormhole with $\mu_+/R_e=J_+/R_e^2=0$ to a limiting configuration with $\mu_+/R_e =J_+/R_e^2=1/2$. This is seen in Fig. 2, where the scaled mass $\mu_+/R_e$, the scaled angular momentum $J_+/R_e^2$ and the scaled scalar charge $D/R_e$ are shown versus the rotational velocity $v_e$ of the throat in the equatorial plane. Again, the scalar charge decreases monotonically and tends to zero for $v_e \to 1$. By exhibiting the r.h.s. of Eq. (29) as well, we demonstrate, that all solutions satisfy the Smarr-type relation (29) with high accuracy. Also shown in Fig. 2 are the corresponding quantities for the Kerr black holes for fixed equatorial horizon radius, $\mu/R_e = 1/2$, $J/R_e^2 = v_e/(1+v_e^2)$ and $\omega_{\rm H} J /R_e = v_e^2/(1+v_e^2)$.

### B. Limit $v_e \to 1$

> **Figure 3.** Properties of symmetric rotating wormholes at fixed angular velocity $\omega(0,\pi/2)=1/2$: the limiting $v_e \to 1$ behavior of the metric functions $f$ (a), $\omega/(2\omega_0)$ (b) and $\nu$ (c) versus the radial coordinate $z=\arctan(2\omega_0 \eta)$ in the equatorial plane $\theta=\pi/2$ for three values of the rotational velocity of the throat in the equatorial plane, $v_e=0.990, \, 0.995, \, 0.999$. The respective functions of the extremal Kerr solution with horizon angular velocity $\omega_{\rm H}=1/2$ are also shown.

Let us now demonstrate, that in the limit $v_e \to 1$ an extremal Kerr black hole is approached. We will consider $\eta \geq 0$ only; the discussion for $\eta \leq 0$ is analogous. First of all, the gobal charges mass and angular momentum precisely assume the respective Kerr values in the limit, while the scalar charge vanishes. (Note, that a circumferential radius $R_e=2$ corresponds to a Boyer-Lindquist horizon radius $r_{\rm H}=1$, and an extremal black hole has $\mu=J/\mu = r_{\rm H}$.) Thus asymptotically the extremal Kerr metric is approached. However, in the limit $v_e \to 1$ the metric tends not only asymptotically but everywhere to the extremal Kerr metric. This is demonstrated in Fig. 3. Here we fix the angular velocity of the throat and the horizon, $\omega_0=\omega_{\rm H} =1/2$. This requires a scaling of the radial coordinate $\eta \to 2\omega_0 \eta/\eta_0$ and metric function $\omega \to \omega/(2\omega_0)$, which leaves the product $\omega\eta$ and $v_e$ invariant. Then the metric functions $f$, $\omega$ and $\nu$ are shown versus the radial coordinate $z=\arctan(2\omega_0 \eta)$ for $\theta=\pi/2$ and $v_e=0.990,\, 0.995, \, 0.999$ together with the limiting extremal Kerr solution.

As the dimensionless rotational velocity $v_e$ reaches its maximal value, $v_e=1$, the hypersurface $\eta=0$, which corresponds to the throat of the wormholes, must change its character. Since the limiting solution represents an extremal black hole, a degenerate horizon must form instead. Moreover, the phantom field vanishes identically in this limit, as it should for a Kerr black hole. Consequently, the Smarr relation (29) for extremal Kerr black holes is recovered, with $\omega_0$ denoting the horizon angular velocity.

### C. NEC, Quadrupole Moment and Moment of Inertia

> **Figure 4.** Properties of symmetric rotating wormholes at fixed equatorial throat radius $R_e$: The quantity $Y$, Eq. (55), giving a measure for the violation of the NEC (a), the scaled quadrupole moment $Q/R_e^3$ (b), and the scaled moment of inertia $I/R_e^3$ (c) versus the rotational velocity $v_e$ of the throat in the equatorial plane; the dimensionless moment of inertia $I/\mu_+^3$ versus the dimensionless quadrupole moment $Q \mu_+/J^2$ (d). Also shown are the respective curves for the Kerr black holes.

In Fig. 4 we show the quantity $Y$, Eq. (55), which gives for the symmetric rotating wormhole solutions a scale independent measure for the violation of the NEC, as a function of the rotational velocity of the throat $v_e$. We observe that the violation of the NEC is strongest in the static limit $v_e=0$ and disappears in the limit $v_e=1$, where the extremal Kerr solution is approached.

The observation that with increasing rotation the violation of the NEC decreases and the family of rotating wormholes ends in an extremal black hole, appears to be a generic feature. It was also observed for rotating Ellis wormholes in 5 dimensions, which end in an extremal Myers-Perry black hole [50]. Moreover, the family of electrically charged static Ellis wormholes in 4 dimensions ends in an extremal Reissner-Nordström black hole with increasing electric charge [51].

Let us now turn to the quadrupole moment $Q$, given in Eq. (42), as obtained by following the procedure of Geroch and Hansen [43, 44] by extracting it from the asymptotic expansion in appropriate coordinates (see e.g. [48, 52]). We exhibit the quadrupole moment in Fig. (4) for the family of symmetric rotating wormholes at fixed equatorial throat radius $R_e$. Starting from zero in the static case, the scaled quadrupole moment $Q/R_e^3$ increases monotonically to its maximum of $Q/R_e^3=1/8$, when the throat velocity $v_e$ approaches the speed of light. Also shown is the scaled quadrupole moment for the Kerr black holes, $Q/R_e^3 = (v_e/(1+v_e^2))^2/2$. We note that the scaled quadrupole moment is larger for the Kerr black holes for any value of the horizon resp. throat velocity $v_e$ (except for $v_e=0$ and $v_e=1$, where both coincide).

One often considers the dimensionless quadrupole moment $Q\mu/J^2$, which is constant for the Kerr solutions, $Q\mu/J^2=1$. The dimensionless quadrupole moment $Q\mu_+/J_+^2$ of the wormhole solutions increases monotonically from zero in the static limit to the value of the Kerr solutions in the limit $v_e \to 1$.

The moment of inertia $I=J_+/\omega_0$ of the wormholes is another quantity of interest, in particular, in comparison with other compact objects. We exhibit the moment of inertia $I$ for the same set of solutions in Fig. 4. The scaled moment of inertia $I/R_e^3$ is smaller than the corresponding value of the Kerr black holes, $I/R_e^3=1/(2(1+v_e^2))$, except in the extremal limit, when they are equal.

The dimensionless moment of inertia $J_+/(\omega_0 \mu_+^3)$ is also exhibited in Fig. 4, but now versus the dimensionless quadrupole moment $Q\mu_+/J_+^2$. For comparison, the Kerr solutions are also included, where $J/(\Omega_{\rm H} \mu^3) = 2(1+\sqrt{1-j^2})$ with $j=J/\mu^2$. Forming the vertical line at $|Q\mu/J^2|=1$, they range from $J/(\Omega_{\rm H} \mu^3)=2$ in the extremal rotating case to $J/(\Omega_{\rm H} \mu^3)=4$, when the limit $J\to 0$ is taken. In contrast, for rotating wormholes, the dimensionless moment of inertia ${I/\mu_+^3}$ diverges in the limit $J_+\to 0$, since in the static limit the wormhole mass vanishes, $\mu_+ \to 0$.

### D. Geometry and Ergoregion

> **Figure 5.** Properties of symmetric rotating wormholes at fixed equatorial throat radius $R_e=2$: isometric embeddings of the equatorial plane for rotational velocities $v_e=0.1, \, 0.5, \, 0.7, \, {\rm and} \, 0.9$.

The shape of wormholes can be visualized with the help of embedding diagrams. Let us consider the wormhole metric at fixed $t$ in the equatorial plane, $\theta=\pi/2$ and embed it isometrically in Euclidean space

$$
d s^2 = e^{-f+\nu} d \eta^2 +e^{-f} h d \phi ^2
= d \rho^2 + \rho^2 d\phi^2 + d z^2  \ , \tag{57}
$$

with $\rho = \rho(\eta)$, $z=z(\eta)$. Comparison yields

$$
\left(\frac{d\rho}{d \eta}\right)^2 + \left(\frac{dz}{d\eta}\right)^2 =e^{-f+\nu} \ , 
\quad \rho^2= e^{-f} h\ , \tag{58}
$$

which leads to $z(\eta)$. We exhibit examples of such embedding diagrams in Fig. 5 for symmetric rotating wormholes at fixed equatorial throat radius $R_e=2$ with increasing rotational velocities $v_e=0.1, \, 0.5, \, 0.7, \, {\rm and} \, 0.9$.

> **Figure 6.** Properties of symmetric rotating wormholes at fixed equatorial throat radius $R_e$: (a) isometric embeddings of the hypersurface of the throat for rotational velocities $v_e=0.966, \, 0.902, \, 0.702, \, 0.495,\, {\rm and} \, 0.1$; the dashed curves correspond to pseudo-Euclidean embedding. (b) The polar radius $R_p/R_e$ and the areal radius $R_A/R_e$ versus $v_e$. The crosses mark $v_e^{\rm cr}$. For comparison the respective curves for the family of Kerr solutions are also shown.

We can also try to visualize the shape of the throat, i.e., the deformation of the hypersurface $\eta=0$. For that end we try to embed this hypersurface in a Euclidean space. However, it is known for Kerr black holes, that beyond a critical value of the rotational velocity $v_e^{\rm cr}$ their horizon can no longer be embedded in a Euclidean space, and a pseudo-Euclidean space must be used for the embedding [53, 54]. Since the family of rotating wormhole solutions approaches an extremal black hole, such a critical value of the rotational velocity $v_e^{\rm cr}$ is expected to arise for rotating wormholes as well.

To obtain the respective embedding, we equate the line element of the hypersurface $\eta=0$, $t=0$ with the (pseudo-)Euclidean line element

$$
d s^2 =  e^{-f+\nu} h d \theta^2 +e^{-f} h \sin^2 \theta d \phi ^2
= d \rho^2 + \rho^2 d\phi^2 + d z^2 \tag{59}
$$

with $\rho = S(\theta)$, $z=C(\theta)$. Now comparison yields

$$
\left(\frac{d S}{d \theta}\right)^2 \pm \left(\frac{dC}{d\theta}\right)^2 =e^{-f+\nu} h \ , 
\quad S^2= e^{-f} h\ . \tag{60}
$$

We show such embedding diagrams in Fig. 6 for the same set of wormholes with rotational velocities $v_e=0.5, \, 0.7, \, 0.9, \, {\rm and} \, 0.95$. The critical value corresponds to $v_e^{\rm cr}=0.9$ and marks the onset of a negative Gaussian curvature at the poles. Beyond $v_e^{\rm cr}$ parts of the hypersurface must be embedded in pseudo-Euclidean space, which is represented by the dashed curves in the figure.

We complete this demonstration of the throat geometry by considering the dependence of the throat radii on the rotational velocity $v_e$. We show in Fig. 6 the ratio of the polar radius to the equatorial radius $R_p/R_e$ for fixed equatorial throat radius $R_e=2$. As one would expect, this ratio decreases monotically with increasing rotation, and reaches the corresponding ratio of radii of the extremal Kerr horizon in the limit $v_e \to 1$. The critical value $v_e^{\rm cr}$, where the Gaussian curvature at the poles turns negative, is indicated by a cross in the figure. For comparison, also the respective curve for the Kerr solutions is shown. Interestingly, while the critical velocity $v_e^{\rm cr}=0.577$ is much smaller for the Kerr solution, the ratio $R_p/R_e$ has the same value for the wormhole and the Kerr critical velocities, as indicated in the figure by a thin horizontal line. The figure also exhibits the ratio of the areal radius to the equatorial radius $R_A/R_e$, where the analogous findings hold.

> **Figure 7.** Properties of symmetric rotating wormholes at fixed throat parameter $\eta_0=1$: (a) the location of the ergosurface $\eta_{\rm ergo}$ in the equatorial plane is shown versus the angular velocity of the throat $\omega_0$ and compared to the function $\arccos(2\omega_0)$; (b) one quadrant of the ergosurface and the throat in coordinates $r=\sqrt{\eta^2+\eta_0^2}$ and $\theta$ for fixed $\phi$ and several values of $\omega_0$.

Let us finally address the ergoregion of rotating wormholes. The ergoregion is defined by the condition $g_{tt} \ge 0$,

$$
g_{tt}= -e^{f}  +e^{-f} h \sin^2\theta \omega^2 \ge 0 \ , \tag{61}
$$

where the equality defines the ergosurface. Inspection of the rotating wormhole solutions reveals, that the location of the ergosurface $\eta_{\rm ergo}$ in the equatorial plane is closely related to the angular velocity $\omega_0$ of the throat. Indeed, the relation $\arctan(\eta_{\rm ergo}/\eta_0)= \arccos(2 \omega_0)$ holds with high accuracy. This is demonstrated in Fig 7.

For wormholes to possess an ergoregion in that part of the spacetime, where $\eta \ge 0$, which we have chosen to be asymptotically flat, they must rotate sufficiently fast. Note that the condition for the ergosphere at the throat in the equatorial plane can be written as

$$
g_{tt}= -e^{f(0,\pi/2)}  +e^{-f(0,\pi/2)} \eta_0^2 \omega_0^2 =0 
\ \ \ \Longleftrightarrow \ \ \
-\frac{\eta_0^2}{R_e^2} (1-R_e v_e)(1+R_e v_e) = 0 \ , \tag{62}
$$

which yields $R_e=2$ for $v_e=1/2$. Thus the throat must rotate with half the velocity of light. As the rotation velocity $v_e$ increases beyond this value, the ergoregion in this part of the spacetime increases. This is demonstrated in Fig. 7, where the ergosurfaces for increasing values of $v_e$ and thus decreasing values of $\omega_0$ are exhibited. However, there is always an ergoregion in the other part of the spacetime, where $\eta \le 0$, and the function $\omega$ tends asymptotically to a finite value.

### E. Geodesics

> **Figure 8.** Geodesics of symmetric rotating wormholes at fixed equatorial throat radius $R_e=2$: effective potentials $V_{\rm eff}^\pm$ for wormholes with rotational velocity $v_e=0.78$ versus the compactified radial coordinate $\arctan(\eta/\eta_0)$ for prograde motion (a) and retrograde motion (b) for several values of the angular momentum $L$ of a massive particle. (c) $V_{\rm eff}^\pm/|L|$ for massless particles for prograde and retrograde motion.

We now analyze the motion of particles and light in these rotating wormhole spacetimes. Interesting aspects emerging from this analysis are that massive particles can have stable bound states in rotating wormhole spacetimes. Moreover, there are unstable bound states for massless particles which indicates the presence of a photon region.

The motion of particles and light is governed by the Lagrangian ${\cal L}$

$$
2 {\cal L} = g_{\mu\nu} \dot{x}^\mu\dot{x}^\nu   = \varepsilon \ , \tag{63}
$$

where the dot denotes the derivative with respect to an affine parameter, and $\varepsilon =-1$ for particles and zero for light. The symmetries of the spacetime lead to two cyclic coordinates and thus two constants of motion, the energy $E$ and the angular momentum $L$.

Let us for simplicity consider only motion in the equatorial plane, $\theta=\pi/2$. The Lagrangian then simplifies to

$$
2 {\cal L}= -e^{f} \dot t^2 +e^{-f} 
\left( e^{\nu} \dot \eta^2
                    + h \left(\dot \phi -\omega \dot t\right)^2\right) = \varepsilon\ , \tag{64}
$$

and the conserved charges become

$$
E= \dot t \left(e^f - e^{-f} h \omega^2\right)+ e^{-f} h \omega \dot \phi \ , \ \ \
L= - e^{-f} h \omega \dot t + e^{-f} h \dot \phi \ . \tag{65}
$$

Solving these equations for $\dot t$ and $\dot \phi$ yields

$$
\dot t = e^{-f}\left(E-\omega L\right) \ , \ \ \
\dot \phi = e^{-f}\left(\omega (E-\omega L)+e^{2f}\frac{L}{h} \right) \ . \tag{66}
$$

Insertion of these expressions into the Lagrangian leads to

$$
e^{-f} e^\nu \dot \eta^2 
-e^{-f} \left((E-\omega L)^2-e^f\frac{L^2}{h}\right) = \varepsilon \ . \tag{67}
$$

When solving this equation for $\dot \eta^2$, it is instructive to introduce effective potentials $V_{\rm eff}^\pm$ as follows

$$
\dot \eta^2 =  e^{-\nu }
\left(E-V_{\rm eff}^+(L,\eta)\right)\left(E-V_{\rm eff}^-(L,\eta)\right) = \Xi(\eta) 
 \ , \tag{68}
$$

where we abbreviated the right hand side by $\Xi(\eta)$, and

$$
V_{\rm eff}^\pm   =  \omega L \pm \sqrt{ e^{2f} \frac{L^2}{h} -\varepsilon e^f} \tag{69}
$$

implying $V_{\rm eff}^+(L,\eta) \geq V_{\rm eff}^-(L,\eta)$. In fact the condition $\dot{\eta}^2 = \Xi(\eta) \geq 0$ leads to a restriction for the allowed energies and angular momenta of the particles, $E\geq V_{\rm eff}^+(L,\eta)$ or $E\leq V_{\rm eff}^-(L,\eta)$.

> **Figure 9.** Geodesics of symmetric rotating wormholes at fixed equatorial throat radius $R_e$: embedding diagrams of bound orbits of a massive test particle in the equatorial plane of a symmetric fast rotating wormhole ($v_e=0.78$) for several values of the particle energy $E$ and angular momentum $L$.

Thus the study of these effective potentials allows for a classification of the possible orbits in the equatorial plane. We exhibit in Fig. 8 examples of the effective potentials for massive and massless particles. In particular, we observe that there are bound orbits of massive particles in such rotating wormhole spacetimes. This is in contrast to the static Ellis wormhole, which does not possess bound orbits. For rotating wormholes there are even three types of bound orbits, those that always remain within a single universe, those that oscillate between the two universes, and those that remain at the throat ( $L=0$ only). Two examples of such single universe bound orbits for a massive particle are shown in Fig. 9 together with a two-world bound orbit.

For the case of massless particles the effective potentials shown in Fig. 8 are divided by the modulus of the angular momentum. We note that $V_{\rm eff}^+$ possesses a local maximum for retrograde motion for $\eta>0$. This indicates that there is a photon region in this asymptotically flat universe. $V_{\rm eff}^+$ additionally possesses a local maximum for prograde motion for $\eta<0$, which indicates the presence of a photon region in the other universe, as well. However, whereas the motion there looks like prograde motion in our coordinates, where the $\eta>0$ universe is asymptotically flat, it corresponds to retrograde motion, when an appropriate coordinate transformation is performed, making the $\eta <0$ universe asymptotically flat.

> **Figure 10.** Geodesics of symmetric rotating wormholes at fixed equatorial throat radius $R_e$: the ratio $R_{\rm ISCO}/R_e$ of the ISCO radius to the throat radius (a) and the corresponding ratio of the orbital period $T_{\rm ISCO}/T_e$ (b) for retrograde motion of massive particles in the equatorial plane versus the rotational velocity $v_e$ of the throat in the equatorial plane.

Of particular interest are the innermost stable circular orbits (ISCOs). To find the circular orbits we need to solve for $\Xi(\eta_{_{\rm CO}})=\Xi'(\eta_{_{\rm CO}})=0$, while stability requires at the same time $\Xi''(\eta_{_{\rm CO}}) < 0$. ISCOs are then characterized by the change of stability, i. e., $\Xi''(\eta_{_{\rm ISCO}}) =0$. For these rotating wormholes there are both corotating and counterrotating ISCOs, just like for the Kerr black holes. Whereas the ISCO of the corotating orbits resides at the throat, the location of the ISCO of the counterrotating orbits depends on the rotation velocity. Here the ratio $R_{\rm ISCO}/R_e$ increases almost by a factor of two from the static limit to the limiting extremal Kerr black hole, as seen in Fig. 10. The figure also displays the ratio of the orbital period $T_{\rm ISCO}/T_e$, where $T_e$ denotes the orbital period of the throat (or the horizon of the extremal black hole), which increases roughly by a factor of three from the static limit to the extremal Kerr black hole.

## IV. Non-Symmetric Wormholes

We now turn to the discussion of the properties of non-symmetric rotating Ellis wormholes. In the non-symmetric case for fixed $\eta_0$ the wormhole solutions depend on two parameters, $\gamma$ and $\omega_{-\infty}$. By varying these, the domain of existence can be mapped out. In the following we will first discuss the global charges of these non-symmetric rotating wormholes, and subsequently we will address their geometry.

### A. Global Properties

Let us start our discussion of the properties of non-symmetric rotating wormholes with their global properties mass $\mu_+$, angular momentum $J_+$ and scalar charge $D$, obtained from the asymptotic expansion at $\eta \to \infty$. To demonstrate these properties, we fix the throat parameter $\eta_0=1$ and consider families of solutions, where the remaining two parameters $\gamma$ and $\omega_{-\infty}$ are varied.

In Fig. 11a we exhibit the mass $\mu_+/R_e$ scaled by the equatorial throat radius versus the squared scalar charge $D^2$ for several fixed values of the parameter $\gamma$ in the range $-4 \le \gamma \le 4$, where the negative values of $\gamma$ are indicated in the figure by dots. The curves are obtained by varying the value of $\omega_{-\infty}$ for a fixed value of $\gamma$, starting from the static case $\omega_{-\infty}=0$.

The symmetric static solution has vanishing mass and scalar charge $D=1$, while the mass of the rotating solutions increases monotonically towards the mass of the limiting extremal Kerr black hole as the scalar charge decreases monotonically to zero. As seen in the figure, for fixed $\gamma$ and fixed equatorial throat radius $R_e$, the mass always increases monotonically from the corresponding static value to the extremal Kerr value, while the scalar charge decreases monotonically to zero. In particular, for negative $\gamma$ the mass is always positive. This is in contrast to positive $\gamma$, where the mass becomes negative in a part of the domain of existence. However, independent of $\gamma$, all families of non-symmetric wormhole solutions approach the extremal Kerr solution.

When we consider the angular momentum $J_+/R_e^2$ scaled by the squared equatorial throat radius, exhibited in Fig. 11b versus the squared scalar charge $D^2$, we see the same monotonic behavior from the static solutions towards the limiting extremal Kerr black hole. The surprise encountered here, is that for a given scalar charge the value of the scaled angular momentum does not depend on the sign of $\gamma$.

To map the domain of existence it is favorable to consider the scaled scalar charge $D/R_e$ (instead of $D^2$). The scaled mass $\mu_+/R_e$ and the scaled angular momentum $J_+/R_e^2$ are shown versus $D/R_e$ in Figs. 11 (c) and (d), respectively. The scaled mass is then located in a thin band, reaching to large values of $D/R_e$ for large positive values of $\gamma$, while shrinking towards the extremal Kerr limit for large negative values of $\gamma$. The scaled angular momentum $J_+/R_e^2$ on the other hand now distinguishes between positive and negative values of $\gamma$, when considered versus $D/R_e$. Fig. 11e finally shows the scaled mass $\mu_+/R_e$ versus the scaled angular momentum $J_+/R_e^2$. Here the limiting behavior of the scaled mass for large negative $\gamma$ can be anticipated, which corresponds to $\mu_+/R_e \to 1$.

> **Figure 11.** Properties of non-symmetric rotating wormholes at fixed throat parameter $\eta_0=1$: (a) the mass $\mu_+/R_e$ scaled by the equatorial throat radius versus the squared scalar charge $D^2$, (b) same as (a) for the angular momentum $J_+/R_e^2$ scaled by the squared equatorial throat radius, (c) the scaled mass $\mu_+/R_e$ versus the scaled scalar charge $D/R_e$, (d) the scaled angular momentum $J_+/R_e^2$ versus the scaled scalar charge $D/R_e$, (e) the scaled mass $\mu_+/R_e$ versus the scaled angular momentum $J/R_e^2$. The parameter $\gamma$ is varied in the range $-4 \le \gamma \le 4$ with negative values indicated by dots.

> **Figure 12.** Properties of non-symmetric rotating wormholes at fixed throat parameter $\eta_0=1$: (a) the mass $\mu_+$, (b) the angular momentum $J_+$ (c) the squared scalar charge $D^2$, and (d) the coefficient $c_2= \mu_+^2 + \eta_0^2 - D^2$ versus $\gamma$. The parameter $\omega_{-\infty}$ is varied in the range $0 \le \omega_{-\infty} \le 5$.

To demonstrate the dependence on the parameter $\omega_{-\infty}$, we exhibit in Fig. 12 the mass $\mu_+$ (a), the angular momentum $J_+$ (b), the squared scalar charge $D^2$ (c), and the coefficient Eq. (28) $c_2 = \mu_+^2 + \eta_0^2 - D^2$ (d) versus the parameter $\gamma$ for fixed values of the parameter $\omega_{-\infty}$ in the range $0 \le \omega_{-\infty} \le 5$. Recall, that $\gamma=0$ represents the symmetric case, while $\omega_{-\infty}=0$ represents the static case. Again the asymmetry between positive and negative values of $\gamma$ is evident.

> **Figure 13.** Properties of non-symmetric rotating wormholes at fixed throat parameter $\eta_0=1$: (a) the mass $\mu_+$ versus the angular momentum $J_+$, (b) the parameter $\omega_{-\infty}$ versus the parameter $\gamma$. The scalar charge $D$ is varied in the range $0.6 \le D \le 2$. The thin dotted curves in (a) delimit the domain of existence.

As a final point of interest concerning the global charges, let us consider the mass $\mu_+$ versus the angular momentum $J_+$ for fixed scalar charge $D$, exhibited in Fig. 13a, where $D$ is varied in the range $0.6 \le D \le 2$. The corresponding values of the parameters $\omega_{-\infty}$ and $\gamma$ are shown in Fig. 13b. Here we observe an interesting bifurcation phenomenon, where the critical value corresponds to $D_{\rm cr}=1$. For a given value of $D< D_{\rm cr}$, there are two $M$ curves, located symmetrically w.r.t. $J_+$, which end at respective limiting values. As $D$ increases towards $D_{\rm cr}$, the two curves approach each other closer and closer, until at $D_{\rm cr}$ the two curves cross. This happens precisely at $\mu_+=J_+=0$. For $D> D_{\rm cr}$, the pattern changes, and there emerge a higher mass curve and a low mass curve. The figure also exhibits two thin dotted curves, which delimit the domain of existence.

### B. Velocity of the throat

> **Figure 14.** Properties of non-symmetric rotating wormholes at fixed throat parameter $\eta_0=1$: the rotational velocity in the equatorial plane $v_e= {R_e\Omega}$ versus the squared scalar charge $D^2$ (a) and versus the scaled scalar charge $D/R_e$ (b) The parameter $\gamma$ is varied in the range $-4 \le \gamma \le 4$ with negative values indicated by dots. The thin dotted lines correspond to extrapolations towards the limiting extremal Kerr black hole.

When the throat has angular velocity $\Omega=\omega_0$, its rotational velocity in the equatorial plane is given by $v_e= {R_e\Omega}$. As seen in the previous section, symmetric wormholes always satisfy $v_e \le 1$. This continues to hold for non-symmetric rotating wormholes with negative values of $\gamma$. However, non-symmetric rotating wormholes with positive values of $\gamma$ can exceed this bound. This is seen in Fig. 14a, where we exhibit the rotational velocity $v_e$ versus the square of the scalar charge, $D^2$, for several families of non-symmetric rotating wormholes, characterized by fixed values of the parameter $\gamma$.

Since the rotational velocity $v_e$ of the extremal Kerr black hole precisely saturates the bound, $v_e=1$, and since all families of non-symmetric rotating wormholes possess the extremal Kerr black hole as their limiting configuration, the quantity $v_e$ does no longer possess a monotonic behavior for the families of rotating wormholes with fixed $\gamma>0$. Consequently, $v_e$ is no longer the quantity of choice to demonstrate the physical properties of non-symmetric rotating wormholes. In this case the scalar charge, squared or scaled, represents a preferable physical parameter, since it always changes monotonically. The rotational velocity $v_e$ is shown versus the scaled scalar charge, $D/R_e$, in Fig. 14b.

Let us now address the origin of the fact, that the rotational velocity $v_e$ exceeds the speed of light, i.e., $v_e>1$, for $\gamma>0$ wormholes in a part of their parameter space adjoining the extremal Kerr black hole. For those wormholes the metric function $\omega$, whose value at the throat enters the expression for the rotational velocity $v_e$, increases strongly towards the throat, assuming very large values at the throat (and even larger values beyond the throat). At the same time, the metric coefficient $g_{00}$ is monotonically decreasing from its asymptotic value of $g_{00}(\infty) = -1$ to large negative values at the throat. (Note, that we exhibit examples of the metric functions for such wormholes in the Appendix.) Thus the wormholes exhibit strong antigravitational features, which are mainly associated with their negative mass. Consequently time is running much faster for an observer at the throat than for an observer far from the wormhole. For an observer close to the throat the rotational velocity $v_e$ never exceeds the speed of light.

### C. Location of the throat

> **Figure 15.** Properties of non-symmetric rotating wormholes at fixed throat parameter $\eta_0=1$: the equatorial radius $R_e$ versus the radial coordinate $\eta$ for spacetimes with $\omega(-\infty)=0.5$ (on the upper branch) and $\gamma=f(-\infty) = 2.0$, $1.0$, $0.0$ and $-1.0$. The minimal value of $R_e$ represents the respective location of the throat.

Let us next address the throat of these non-symmetric rotating wormholes. In particular, we would like to know, where we find the throat in the equatorial plane, i.e., at which coordinate $\eta_{e}$ it is located there, and whether the throat coordinate $\eta_{t}$ depends on the polar angle $\theta$. To approach the first question, we show in Fig. 15 examples of the equatorial radius $R_e$ versus the radial coordinate $\eta$ for several wormhole solutions. These spacetimes are characterized by the parameter value $\omega(-\infty)=0.5$ (located on the upper branch) and the values of the asymmetry parameter $\gamma=f(-\infty) = 2.0$, $1.0$, $0.0$ and $-1.0$. Their scalar charge is given by $D=0.33984$, $0.43155$, $0.55277$, and $0.71636$, respectively.

The location $\eta_{e}$ of the throat in the equatorial plane is given by the minimum of the equatorial radius $R_e$. We note that the location of the throat $\eta_{e}$ depends only weakly on the parameter $\gamma$ in the considered range, $-1 \leq \gamma \leq 2$. For negative $\gamma$ the throat is located at small positive $\eta_{e}$, while for positive $\gamma$ it resides at small negative $\eta_{e}$. We observe that, in contrast to the throat location $\eta_{e}$, the throat radius $R_e$ depends strongly on $\gamma$, and increases with increasing $\gamma$.

In Boyer-Lindquist coordinates, the event horizon of a rotating black hole is characterized by a single value of the radial coordinate. Likewise, the throat of a symmetric rotating wormhole is characterized by a single value of the radial coordinate. Let us now see, whether an analogous result holds for the throat of a non-symmetric rotating wormhole. To that end we analyze the coordinates of the minimal surface defining the throat. In particular, we calculate the value of the radial throat coordinate $\eta_{t}$ as a function of the polar angle $\theta$, and find only a very slight dependence of $\eta_{t}$ on $\theta$. For instance, the ratio $\eta_{t}/\eta_{e}$ is always very close to one, with deviations less than 0.1% and thus within the numerical accuracy. While we cannot answer, whether $\eta_{t}$ is indeed a constant, we can state that a constant $\eta_{t}$ represents at least a good approximation. From a geometrical point of view, however, the throat is highly deformed for a fast rotating wormhole.

### D. Geodesics

> **Figure 16.** Geodesics of non-symmetric rotating wormholes: massless particles with zero angular momentum starting at coordinates $x_0=0.136$, $0.335$, $0.399$ and $y_0=0$ on the second manifold, passing through the throat for a wormhole solution with $\omega_{-\infty} =1000$, $\gamma=10.008$. Embedding diagram (a) and projection in the equatorial plane (b).

As our last quest let us address the trajectories of particles and light in these non-symmetric rotating wormhole spacetimes. As in the symmetric case we find stable bound orbits of massive particles and unstable bound orbits of massless particles. However, we now focus on the orbits of particles in wormhole spacetimes, whose equatorial throat velocity $v_e$ exceeds the speed of light, since this is a new phenomenon as compared to the symmetric case. As an example, we exhibit in Fig. 16 the orbits of massless particles with zero angular momentum starting at the coordinates $x_0=20$, 50, 60 on the second manifold, which pass through the throat of a wormhole solution with parameters $\omega_{-\infty} =1000$, $\gamma=10.008$, and $v_e \approx 8$. Fig. 16a shows the orbits in an embedding of the wormhole spacetime, while Fig. 16b gives a projection of the orbits in the equatorial plane.

In such a spacetime the particle orbits appear rather strange at first sight. Moving with zero angular momentum in the negative $\eta$ region towards the throat, the particle orbits are strongly dragged along by the rapidly rotating space time until the particles pass the throat. Beyond the throat the particles then follow more or less straight lines, as they move across the positive $\eta$ region towards infinity. In this region the function $\omega$ decreases rapidly outside the throat and vanishes asymptotically. So the dragging of the radial geodesics diminishes fast, when away from the throat.

## V. Conclusions

The construction of Lorentzian rotating wormholes, which are generalizations of the Ellis wormholes, has been a challenge for a very long time. With this study we have provided the first detailed investigation of rotating Ellis wormholes in General Relativity. These wormhole solutions are supported by a phantom field, and can be either symmetric or non-symmetric. Whereas the static solutions are known in closed form, the non-perturbative rotating wormholes have been obtained by numerical integration of the coupled system of Einstein-phantom equations, subject to appropriate boundary conditions. The latter guarantee that the solutions are globally regular and asymptotically flat on one side, while for the second side a coordinate transformation is necessary to achieve asymptotic flatness.

The global charges of the wormhole solutions can be obtained from their asymptotic expansions. For symmetric wormholes the mass is the same on both sides of the wormhole. The same holds true for the angular momentum. However, this is no longer the case, when the asymmetry parameter $\gamma$ differs from zero. The throat of symmetric wormholes resides at the center of our coordinate system, where the radial coordinate $\eta$ is zero. The corresponding surface represents a minimal surface, which changes from a round sphere in the static limit to a strongly deformed axially symmetric surface with negative Gaussian curvature at the poles, when the rotational velocity becomes sufficiently high. For non-symmetric wormholes the minimal surface defining the throat may still be described by a surface of constant radial coordinate $\eta$ (at least within our numerical accuracy). But, depending on the sign of the asymmetry parameter $\gamma$, the location of the throat is shifting towards positive or negative values of $\eta$.

Many of the properties revealed by our calculations are rather surprising, for instance,

- rotating wormholes satisfy a Smarr type relation,

- rotating wormholes possess an extremal Kerr black hole as limiting configuration,

- for rotating wormholes the crossing from positive to negative Gaussian curvature at the poles of the throat occurs precisely at the same ratio of radii as for Kerr black holes,

- the dimensionless quadrupole moment of rotating wormholes can strongly exceed the Kerr value,

- the ergoregion of the rotating wormholes is very different from the expectations raised by the Teo wormhole,

- non-symmetric wormholes can possess a rotational velocity of the throat which exceeds the speed of light,

- unlike the static Ellis wormholes, the rotating wormholes do possess bound orbits.

Furthermore, we conjecture that the observations that (i) the violation of the NEC decreases with increasing global charge, while (ii) the wormholes approach an extremal black hole solution as a limiting configuration, represent generic features of wormholes. For the present study, the global charge is angular momentum, and the extremal black hole corresponds to a Kerr black hole. As shown before, electrically charged static Ellis wormholes in four dimensions approach with increasing charge in an analogous fashion an extremal Reissner-Nordström black hole [51], while rotating wormholes (with equal angular momenta) in five dimensions tend with increasing angular momenta towards the corresponding extremal Myers-Perry black hole [50].

So far we have not addressed the important issue of the stability of these rotating wormhole solutions. It has been shown before, that the static Ellis wormholes are unstable, both in four [55–57] (see also [58]) and higher dimensions [59]. On the other hand, arguments have been given which indicate that wormholes might be stabilized by rotation [60]. Indeed, in the case of five-dimensional rotating wormholes it has been shown, that the unstable mode of the static solutions disappears, when the rotation is sufficiently fast [50]. We are planning to do the corresponding stability analysis also for four-dimensional rotating wormholes, to see whether rotation will eliminate the unstable mode as well in four dimensions. On the other hand, stability of wormholes could also be achieved, when the Einstein-Hilbert action of General Relativity is replaced by a more general action with higher curvature terms [22, 23].

We gratefully acknowledge support by the DFG within the Research Training Group 1620 “Models of Gravity” and by FP7, Marie Curie Actions, People, International Research Staff Exchange Scheme (IRSES-606096). We gratefully acknowledge discussions with E. Radu.

## VI. Appendix

> **Figure 17.** Non-symmetric rotating wormhole with $v_e>1$: the metric functions $f$ (a), $\nu$ (b), $\omega$ (c), the combination $\omega h^{3/2}$ (d), versus the compactified radial coordinate $\arctan(\eta/\eta_0)$, and the equatorial radius $R_e$ (e) and the rotational velocity $v_e = R_e \omega$ (f) versus the scaled radial coordinate $\eta/\eta_0$. The thin vertical line marks the location of the throat.

We here demonstrate the behaviour of the metric functions for asymmetric wormholes with rotational velocity $v_e>1$. Fig. 17 exhibits the functions $f$ (a), $\nu$ (b), $\omega$ (c) versus the compactified radial coordinate $\arctan(\eta/\eta_0)$ for a solution with parameters $\gamma=10.008$, $\omega_{-\infty}=1000$. The function $f$ hardly deviates from the corresponding function of the static wormhole, and the function $\nu$ remains close to one. Still the function $\omega$ assumes very large values towards the throat and beyond the throat. The combination $\omega h^{3/2}$ is exhibited in (d) to demonstrate the fall-off of $\omega$ for $\eta \to + \infty$.

For this wormhole spacetime also the equatorial radius $R_e(\eta)$ (e) and the rotational velocity in the equatorial plane $v_e(\eta)$ (f) are shown versus the scaled radial coordinate $\eta/\eta_0$, demonstrating that $v_e(\eta)$ exceeds the velocity of light beyond a certain value of the radial coordinate.

## References

[1] For an overview see e. g. M. Visser, “Lorentzian wormholes: From Einstein to Hawking”, Woodbury, USA: AIP (1995) 412 p

[2] A. Einstein and N. Rosen, Phys. Rev. **48** (1935) 73.

[3] J. A. Wheeler, Annals Phys. **2**, 604-614 (1957).

[4] J. A. Wheeler, *Geometrodynamics* (Academic, New York, 1962).

[5] M. D. Kruskal, Phys. Rev. **119**, 1743-1745 (1960).

[6] R. W. Fuller, J. A. Wheeler, Phys. Rev. **128**, 919-929 (1962).

[7] I. H. Redmount, Prog. Theor. Phys. **73** (1985) 140.

[8] D. M. Eardley, Phys. Rev. Lett. **33**, 442-444 (1974).

[9] R. M. Wald, S. Ramaswamy, Phys. Rev. **D21**, 2736-2741 (1980).

[10] H. G. Ellis, J. Math. Phys. **14**, 104-118 (1973).

[11] H. G. Ellis, Gen. Rel. Grav. **10**, 105-123 (1979).

[12] K. A. Bronnikov, Acta Phys. Polon. **B4**, 251-266 (1973).

[13] T. Kodama, Phys. Rev. **D18**, 3529-3534 (1978).

[14] M. S. Morris, K. S. Thorne, Am. J. Phys. **56**, 395-412 (1988).

[15] M. S. Morris, K. S. Thorne and U. Yurtsever, Phys. Rev. Lett. **61**, 1446 (1988).

[16] F. S. N. Lobo, Phys. Rev. D **71**, 084011 (2005) [gr-qc/0502099].

[17] D. Hochberg, Phys. Lett. **B251**, 349-354 (1990).

[18] H. Fukutaka, K. Tanaka, K. Ghoroku, Phys. Lett. **B222**, 191-194 (1989).

[19] K. Ghoroku, T. Soma, Phys. Rev. **D46**, 1507-1516 (1992).

[20] N. Furey, A. DeBenedictis, Class. Quant. Grav. **22**, 313-322 (2005) [gr-qc/0410088].

[21] K. A. Bronnikov and E. Elizalde, Phys. Rev. D **81**, 044032 (2010) [arXiv:0910.3929 [hep-th]].

[22] P. Kanti, B. Kleihaus and J. Kunz, Phys. Rev. Lett. **107**, 271101 (2011) [arXiv:1108.3003 [gr-qc]].

[23] P. Kanti, B. Kleihaus and J. Kunz, Phys. Rev. D **85** (2012) 044007 [arXiv:1111.4049 [hep-th]].

[24] F. Abe, Astrophys. J. **725**, 787 (2010) [arXiv:1009.6084 [astro-ph.CO]].

[25] Y. Toki, T. Kitamura, H. Asada and F. Abe, Astrophys. J. **740**, 121 (2011) [arXiv:1107.5374 [astro-ph.CO]].

[26] R. Takahashi and H. Asada, Astrophys. J. **768**, L16 (2013) [arXiv:1303.1301 [astro-ph.CO]].

[27] J. G. Cramer, R. L. Forward, M. S. Morris, M. Visser, G. Benford and G. A. Landis, Phys. Rev. D **51**, 3117 (1995) [astro-ph/9409051].

[28] V. Perlick, Phys. Rev. D **69**, 064017 (2004) [gr-qc/0307072].

[29] N. Tsukamoto, T. Harada and K. Yajima, Phys. Rev. D **86**, 104062 (2012) [arXiv:1207.0047 [gr-qc]].

[30] C. Bambi, Phys. Rev. D **87**, 107501 (2013) [arXiv:1304.5691 [gr-qc]].

[31] P. G. Nedkova, V. K. Tinchev and S. S. Yazadjiev, Phys. Rev. D **88**, 124019 (2013) [arXiv:1307.7647 [gr-qc]].

[32] M. Zhou, A. Cardenas-Avendano, C. Bambi, B. Kleihaus and J. Kunz, Phys. Rev. D **94**, 024036 (2016) [arXiv:1603.07448 [gr-qc]].

[33] V. Dzhunushaliev, V. Folomeev, B. Kleihaus and J. Kunz, JCAP **1104**, 031 (2011) [arXiv:1102.4454 [astro-ph.GA]].

[34] V. Dzhunushaliev, V. Folomeev, B. Kleihaus and J. Kunz, Phys. Rev. D **85**, 124028 (2012) [arXiv:1203.3615 [gr-qc]].

[35] V. Dzhunushaliev, V. Folomeev, B. Kleihaus and J. Kunz, Phys. Rev. D **87**, 104036 (2013) [arXiv:1302.5217 [gr-qc]].

[36] V. Dzhunushaliev, V. Folomeev, B. Kleihaus and J. Kunz, Phys. Rev. D **89**, 084018 (2014) [arXiv:1401.7093 [gr-qc]].

[37] A. Aringazin, V. Dzhunushaliev, V. Folomeev, B. Kleihaus and J. Kunz, JCAP **1504**, 005 (2015) [arXiv:1412.3194 [gr-qc]].

[38] V. Dzhunushaliev, V. Folomeev, B. Kleihaus and J. Kunz, JCAP **1608**, 030 (2016) [arXiv:1601.04124 [gr-qc]].

[39] P. E. Kashargin and S. V. Sushkov, Grav. Cosmol. **14**, 80 (2008) [arXiv:0710.5656 [gr-qc]].

[40] P. E. Kashargin and S. V. Sushkov, Phys. Rev. D **78**, 064071 (2008) [arXiv:0809.1923 [gr-qc]].

[41] B. Kleihaus and J. Kunz, Phys. Rev. D **90**, 121503 (2014) [arXiv:1409.1503 [gr-qc]].

[42] E. Teo, Phys. Rev. D **58**, 024014 (1998) [gr-qc/9803098].

[43] R. P. Geroch, J. Math. Phys. **11**, 2580 (1970).

[44] R. O. Hansen, J. Math. Phys. **15**, 46 (1974).

[45] C. Hoenselaers and Z. Perjes, Class. Quant. Grav. **7**, 1819 (1990).

[46] T. P. Sotiriou and T. A. Apostolatos, Class. Quant. Grav. **21**, 5727 (2004) [gr-qc/0407064].

[47] G. Pappas and T. A. Apostolatos, Phys. Rev. Lett. **108**, 231104 (2012) [arXiv:1201.6067 [gr-qc]].

[48] B. Kleihaus, J. Kunz, S. Mojica and M. Zagermann, Phys. Rev. D **93**, 064077 (2016) [arXiv:1601.05583 [gr-qc]].

[49] B. Kleihaus and J. Kunz, Phys. Rev. Lett. **86**, 3704 (2001) [gr-qc/0012081].

[50] V. Dzhunushaliev, V. Folomeev, B. Kleihaus, J. Kunz and E. Radu, Phys. Rev. D **88**, 124028 (2013) [arXiv:1309.2448 [gr-qc]].

[51] O. Hauser, R. Ibadov, B. Kleihaus and J. Kunz, Phys. Rev. D **89**, 064010 (2014) arXiv:1312.3539 [gr-qc].

[52] B. Kleihaus, J. Kunz and S. Mojica, Phys. Rev. D **90**, 061501 (2014) [arXiv:1407.6884 [gr-qc]].

[53] L. Smarr, Phys. Rev. Lett. **30**, 71 (1973) Erratum: [Phys. Rev. Lett. **30**, 521 (1973)].

[54] L. Smarr, Phys. Rev. D **7**, 289 (1973).

[55] H. -a. Shinkai and S. A. Hayward, Phys. Rev. D **66**, 044005 (2002) [gr-qc/0205041].

[56] J. A. Gonzalez, F. S. Guzman, and O. Sarbach, Class. Quant. Grav. **26**, 015010 (2009) [arXiv:0806.0608 [gr-qc]].

[57] J. A. Gonzalez, F. S. Guzman, and O. Sarbach, Class. Quant. Grav. **26**, 015011 (2009) [arXiv:0806.1370 [gr-qc]].

[58] R. A. Konoplya and A. Zhidenko, arXiv:1606.00517 [gr-qc].

[59] T. Torii and H. a. Shinkai, Phys. Rev. D **88**, 064027 (2013) [arXiv:1309.2058 [gr-qc]].

[60] T. Matos and D. Nunez, Class. Quant. Grav. **23**, 4485 (2006) [gr-qc/0508117].

---

# Are slowly rotating Ellis-Bronnikov wormholes stable?

Bahareh Azad, Jose Luis Blázquez-Salcedo, Fech Scen Khoo, Jutta Kunz — arXiv:2301.05243v2 [gr-qc], 23 Nov 2023

## Abstract

We investigate the radial perturbations of Ellis-Bronnikov wormholes ($\mathrm{l}=0$) in a slowly rotating background expanded up to second order in rotation. We find indications that simple wormhole solutions such as Ellis-Bronnikov in General Relativity can be stabilized by rotation, thus favoring a viable traversable wormhole. This opens up the intriguing question whether the many other wormhole solutions with or without the support of exotic matter can become linearly mode stable when the wormhole rotates.

## 1 Introduction

Wormholes have received much attention in recent years, in particular, concerning their possible astrophysical signatures such as gravitational lensing effects of wormholes [1–12], wormhole shadows [10, 13–17], or wormhole accretion disks and quasi-periodic oscillations [18–24]. In fact, wormholes may mimic many properties of black holes [10, 25–34]. Therefore the study of gravitational waves emitted by wormholes is also of great interest.

The observations of gravitational waves by the LIGO/VIRGO collaboration have provided us with invaluable information about the merger of highly compact objects such as black holes and neutron stars (see e.g. [35, 36]). Here the ringdown phase after the merger events is dominated by the characteristic frequencies of the final objects, encoded in their quasi-normal modes (QNMs). Whereas the QNMs of black holes and neutron stars are well studied in General Relativity (GR) [37–39], the corresponding modes of wormholes have received much less attention.

In GR classical wormholes need exotic matter in order to violate the energy conditions [40–50]. While this issue can be circumvented in several ways (for example, by considering wormholes in generalized gravities [50, 51] or by adding fermionic matter [52, 53]), another question concerns the stability of wormholes in GR and generalized gravities. For instance, the notorious radial instability of the static spherically symmetric Ellis-Bronnikov (EB) wormholes of GR has been known for long [32, 54–57].

Here we present intriguing evidence that this radial instability of EB wormholes will disappear, when these wormholes rotate sufficiently fast. However, unlike their static counterparts, there are no known analytical solutions of rotating EB wormholes [58], these are known only perturbatively for slow rotation [59, 60] and numerically for fast rotation [61, 62]. Additionally, rotating EB wormholes have been investigated in five dimensions for the case of two equal magnitude angular momenta, where the angular coordinates factorize [63].

In four dimensions, a mode analysis of rotating compact objects becomes a challenging task. Already for Kerr-Newman black holes linear mode stability could only be provided by solving the resulting system of coupled partial differential equations with sophisticated numerical methods [64]. Alternatively, the modes have recently been obtained perturbatively to second order in rotation, where parity mixing complicates their evaluation as opposed to first order [65].

We here apply this recently developed second order formalism [65] in order to study the change of the unstable radial mode of EB wormholes in the presence of slow rotation. We demonstrate, that the magnitude of the pertinent unstable eigenvalue decreases with increasing angular momentum of the wormhole, thus diminishing the instability. In fact, in our perturbative analysis the eigenvalue vanishes at some critical value of the angular momentum, that slightly depends on the asymmetry parameter of the wormhole, and we argue that nonperturbatively the instability will disappear slightly earlier.

## 2 EB Wormholes in Slow Rotation

We consider a phantom scalar field $\Phi$ minimally coupled to GR,

$$
S =  \frac{1}{16 \pi G}\int d^4x \sqrt{-g} 
        \Big[\mathrm{R} + 2 \partial_\mu \Phi \, \partial^\mu \Phi 
         \Big] \, \tag{2.1}
$$

with field equations

$$
\mathrm{R}_{\mu\nu} = -2 \partial_{\mu}\Phi\partial_{\nu}\Phi \, , \quad 
    \partial_{\mu}\partial^{\mu}\Phi = 0 \, . \tag{2.2}
$$

Up to second order in rotation the background metric is given by

$$
\begin{aligned}
ds^2  &=  -e^{f}\left[1+\epsilon_r^2 2\left(h_0(r)+h_2(r)P_2(\theta)\right)\right]dt^2 
+ e^{-f}\left[1+\epsilon_r^2 2\left(b_0(r)+b_2(r)P_2(\theta)\right)\right]dr^2 \\
 &+  
{e^{-f}} R^2
\left[1+\epsilon_r^2 2\left(k_0(r)+k_2(r)P_2(\theta)\right)\right]
\times 
\left[
d\theta^2+\sin^2{(\theta)}\left[d\varphi-\epsilon_rw(r)dt\right]^2 
\right]
\ , && \qquad (2.3)
\end{aligned}
$$

where $R^2=(r^2+r_0^2)$, with slow-rotation parameter $\epsilon_r \ll 1$, and the Legendre polynomial $P_2(\theta) = \left(3\cos^2{(\theta)}-1\right)/2$. The corresponding second order phantom scalar field has the form

$$
\Phi = \phi(r) + \epsilon_r^2 \left(\phi_{20}(r)+\phi_{22}(r)P_2(\theta)\right) \ . \tag{2.4}
$$

In the following we choose the gauge $k_0(r)=0$. The throat of the wormhole is located at $r=0$, and it has an area $\mathrm{A}=4\pi r_0^2 e^{\frac{\pi C}{2r_0}}$.

The EB wormhole background solutions are

$$
f(r) = \frac{{C}}{r_0} \left(\tan^{-1} \! \left(\frac{r}{r_0}\right)-\frac{\pi}{2}\right) \ , \ \phi(r)= \frac{Q_0 f}{C} \ , \tag{2.5}
$$

with asymmetry parameter $C=2M_0$, related to the static background wormhole mass $M_0$, and the static background phantom scalar charge $Q_{0} = \sqrt{C^2/4 + r_0^2}$. Here we will focus on $C\ge 0$. At the first order in rotation, we solve to obtain

$$
w(r)= \frac{3J}{2C(C^2+r_0^2)}
    \left[
    1 - \left(
    1+2C\frac{C+r}{R^2}
    \right)e^{2f}
    \right] \, . \, \, \, \, \, \, \, \, \tag{2.6}
$$

In the system of field equations, the differential equations of the radial functions $h_0,{b_0},\phi_{20}$ are decoupled from those of ${h_2}, k_2, {b_2}, \phi_{22}$. When focusing on radial perturbations, we only need the functions $\phi_{20}$, $b_0$, $h_0$. For the simpler symmetric background wormholes ($C=0$) they are given by

$$
\begin{aligned}
\phi_{20}(r)  &=  
    \frac{3J^2}{rr_0^3}
    \left( 
    \phi + \frac{\pi}{2} - \frac{3r}{2r_0} - \frac{4}{\pi r_0} - \frac{3r^2+4r_0^2}{2R^2\phi}
    \right)
    \, , \\
b_0(r)  &=  \frac{\Delta M}{r}
    \left(
    1-\phi\frac{r_0}{r}
    \right)
    +
    \frac{6J^2}{rr_0^3}
    \left(
    \frac{r_0}{r}+\phi
    \right)
    -\frac{3J^2}{r^2r_0^2}\phi^2
        \, , \\
h_0(r)  &=   \frac{3J^2}{r_0^4}
    \left(
    \phi^2 + \frac{\pi^2-8}{2\pi}\phi - \frac{r_0^2}{R^2}
    \right) \, . && \qquad (2.7)
\end{aligned}
$$

Solutions for $C>0$ are more involved, and hence provided elsewhere [66]. The static mass $M_0$ is corrected by $\Delta M =3J^2(\pi^2-8)/(2\pi r_0^3)$ in the limit of $C=0$ when $r\rightarrow +\infty$. Therefore, for $C=0$, the total mass of the wormhole is no longer zero. In fact, it receives a contribution from the rotation. This echoes the finding in [60], that there is no massless rotating EB wormhole. The static scalar charge $Q_0$ is also corrected by $\Delta Q=-\Delta M$. The mass and scalar charge corrections for $C>0$ are given elsewhere [66].

## 3 Stability Analysis: Radial Perturbations

We linearly perturb the metric field $g$ and the phantom field $\Phi$ up to first order in the perturbation parameter $\epsilon_q$, in our slowly rotating ($sr$) background considered up to second order in rotation $\epsilon_r^2$. The perturbed metric is then given by

$$
g_{\mu\nu} =  g^{(sr)}_{\mu\nu} + \epsilon_q \delta h_{\mu\nu}(t,r,\theta,{\varphi}) \, , \tag{3.8}
$$

the perturbation of the metric being a combination of polar ($P$) and axial ($A$) perturbations: $\delta h_{\mu\nu}=\delta h^{(A)}_{\mu\nu} + \delta h^{(P)}_{\mu\nu}$. The perturbed phantom field is

$$
\Phi =  {\Phi}^{(sr)} + \epsilon_q \delta{\phi}^{(P)} (t,r,\theta,{\varphi})
\, . \tag{3.9}
$$

These perturbations can be decomposed in spherical harmonics $Y[\mathrm{l},\mathrm{m}](\theta,{\varphi})$ , with multipole numbers $\mathrm{l}$ and $\mathrm{m}$ [65]. When wormholes rotate the perturbations of even (polar) and odd (axial) parities are entangled, i.e. the multipole numbers $\mathrm{l}$ are coupled. This results in an infinite tower of equations carrying the index $\mathrm{l}$ that are to be summed, as is well-known for other rotating objects such as black holes and neutron stars. Here, we are interested in the radial-led perturbations, hence $\mathrm{l}=0$, $\mathrm{m}=0$ polar-led perturbations. For a given slowly rotating background up to second order in rotation, it is possible to show that these perturbations are just coupled to axial $\mathrm{l}=1$ perturbations (see [65]). Hence for our purposes, the metric perturbation can be simplified to

$$
\delta h_{\mu\nu}= e^{i\omega t}
    \begin{pmatrix}
NY_0 & 0    & 0 & {S}_0 Y_\theta \\
0   & LY_0 & 0 & {S}_1 Y_\theta \\
0 & 0 & R^2 TY_0 & 0 \\
{S}_0 Y_\theta & {S}_1 Y_\theta & 0 & R^2 T\sin^2{\theta}Y_0
\end{pmatrix} \, \, \, \, \, \, \, \, \, \tag{3.10}
$$

where $N, T, L, {S}_0, {S}_1$ are radial functions, $Y_0=Y[0,0] =1/\sqrt{4\pi}$ and $Y_\theta=\sin{\theta} \, \partial_\theta Y[1,0] =-\sin^2{\theta}\sqrt{3/4\pi}$. The phantom perturbation on the other hand can be taken as

$$
\delta{\phi}^{(P)} = 
 {e^{i\omega t}}
 {\phi_1(r)} Y_0 \, . \tag{3.11}
$$

With these perturbations, a consistent set of equations is formed, as the rotations are approximately slow and we work only up to second order in the rotation parameter $\epsilon_r$.

Following the procedure explained in [65], we obtain the linearized field equations. For further simplification, we project the Einstein equation to the tensor spherical harmonics. In this way we get a set of polar and axial relations. Since we are interested only in radial-led $\mathrm{l}=0$ perturbations, it is enough for us to project the linearized field equations to the lowest tensor spherical harmonics, given by $Y[\mathrm{l}=0,\mathrm{m}=0]$. This greatly simplifies the calculations as most of the projected components of the field equations turn out to be zero. Eventually a system of ordinary differential equations (ODEs) for the radial functions $\phi_1, N, L$, $T$, $S_0$ and $S_1$ is formed. However, these equations are not all independent.

After some manipulations, we are left with a system of four independent ODEs for the 6 perturbation functions $N, L, T, {S}_0, {S}_1$ and ${\phi_1}$ (found in equations (3.10)-(3.11)). Without loss of generality, and in order to solve the problem numerically, it is convenient to fix the gauge by the choice $S_0=0$ and $\phi_1=0$. Then the linearized field equations reduce to a system of ODEs and algebraic relations, for $C=0$:

$$
S_1(r) =
\frac{i\sqrt{3} J}{2 \omega r_0^3  R^2} 
\Big\{
R^{2} (r \pi -2 {r_0} ) L
+ 2  r_0^{3} N
-2 r R^{2}  \tan^{-1} (r/r_0)
(L +T )
+
\Big[\pi rR^2 -2r_0(r^2+2r_0^2)\Big] T
\Big\}
\, , \tag{3.12}
$$

$$
\begin{aligned}
\frac{dN}{dr}  &=  
-\frac{1}{{r R^2}}
\left[ (\omega^2R^4 +r_0^2 ) T + r_0^2 L \right]
+
\frac{J^2}{2\pi r^3r_0^6 R^4}
\Big\{ 
12 R^2 \tan^{-1}  
(r/r_0)
\Big[
-2\pi \omega^2 r r_0^3 R^4 \\
 &- 
2\pi r r_0(r_0^4-3r^4-3r^2r_0^2)
+
 3\pi r^4R^2 
(\tan^{-1}  
(r/r_0)
- \pi)
+
r_0^4
\Big(\pi \tan^{-1}  
(r/r_0)
- (\pi^2+8)/2 \Big)
(\omega^2R^4+r_0^2) \\
 &+  3r
 2(\pi^2+8)r_0^7 \Big(\omega^2 (r_0^2 + 3r^2) +1\Big)
 + 6r^2r_0^5 
 ( - 2\pi^2 + 16/3)
 + 2r^4r_0^3 ( - 13\pi^2 + 8) \\
 &+ 
  2r^4r_0^3 \omega^2 (\pi^2+8) (r^2+3r_0^2)
  +  8 \pi r r_0^6 -12\pi^2r^6r_0
  + 3\pi^3 r^7
  + 6\pi r^5 r_0^2 (\pi^2+2)
  +3 \pi r^3 r_0^4 (\pi^2+8)
\Big]
T \\
 &+ 
  12 \pi  r^3 R^2 \tan^{-1}  
  (r/r_0)
  \Big[ 
  r_0(2r^2+r_0^2) 
 + r R^2 (\tan^{-1}  
  (r/r_0)
  - \pi) 
  \Big]
  L 
  + 6 r^3 r_0^3 R^2  (\pi^2-8) N \\
 &+  3 r^3 R^2 \Big[r_0^3 (-3\pi^2+8)
    +\pi^3 r^3 
    + \pi rr_0\Big(r_0(\pi^2+4)-4\pi r\Big)
   \Big]
   L
\Big\}
\, , && \qquad (3.13)
\end{aligned}
$$

$$
\begin{aligned}
\frac{dT}{dr}  &=   
 -\frac{(L+T)r}{R^2}
  +
  \frac{J^2}{2\pi rr_0^3 R^4}
  \Big\{ 
12 \pi r R^2 \tan^{-1} (r/r_0) T 
    -
    3r \Big[(\pi^2+8)R^2-4\pi rr_0 \Big] T
    - 6rR^2 (\pi^2+8) L \\
 &+ 
12 R^2 \tan^{-1} (r/r_0)
    \Big[ 2\pi (\pi r_0/4+r) + 4r_0
    - \, 
    \pi r_0 \tan^{-1} (r/r_0)
    \Big] L
  \Big\}
    \, , && \qquad (3.14)
\end{aligned}
$$

$$
\begin{aligned}
\frac{dL}{dr}  &=  

\frac{1}{r R^2} \left[(\omega^2R^4+2r^2+r_0^2)T+(2r^2+r_0^2)L\right]
+
\frac{J^2}{2\pi r^3r_0^4 R^4}
\Big\{6R^2 \tan^{-1} (r/r_0)
    \Big[
     8\pi r r_0 R^2 (1+(\omega R)^2) \\
 &+ 
(\pi^2+8 -2\pi \tan^{-1} (r/r_0) )
  \Big[\omega^2 (2r_0^6+r^6)
 +   r_0^2 
      \Big(r_0^2(5\omega^2r^2+2) + r^2(4\omega^2r^2+3)\Big)\Big]  
    \Big]
    T \\
 &-  12 r
     \Big[ \omega^2 r_0^7 (\pi^2+8)
     + \pi\omega^2 rr_0(r_0^5+4r^2r_0^3 
     +5r^4r_0)
       +  
      \pi rr_0^2 (3r_0^2+2r^2)
      + 2\pi\omega^2 r^7 \\
 &+   
       r_0 (\pi^2+8) \Big((\omega r)^2 \Big(3r_0^4+r^4+3r^2r_0^2\Big) + R^4\Big)
     \Big] T
      -
      12 r_0 R^2 \tan^{-1} (r/r_0)
       \Big[ (\pi^2+8) (r_0/2) R^2 \\
 &+  
      \pi r(2r_0^2+r^2)
      - \pi \tan^{-1} (r/r_0) r_0 R^2
      \Big] L 
       + 3 rr_0R^2
       \Big[ (\pi^2+8) (2r_0^2+r^2)
       + 4\pi rr_0
       \Big] L
\Big\}
\, , && \qquad (3.15)
\end{aligned}
$$

where $R^2=r^2+r_0^2$. More technical details of our slow-rotation approximation framework can be found in [65].

It can be shown that the final system can be cast into a single second order ordinary differential equation for $T$, with algebraic relations for the rest of the perturbation functions.

First note that equations (3.14) and (3.15) do not couple to the perturbation function $N$. By taking the derivative of equation (3.14), and using again equations (3.14) and (3.15) to write $L$ and $dL/dr$ in terms of $T$ and $dT/dr$, the resulting second order equation has the form

$$
\frac{d^2T}{dr^2}+ A(r)\frac{dT}{dr} + B(r)T = 0 \, , \tag{3.16}
$$

where the coefficients $A,B$ are combinations of the coefficients of perturbation equations (3.14)-(3.15). These coefficients depend on the background metric functions. For simplicity, it is convenient to write them like

$$
\begin{aligned}
& A(r) = \frac{r_*'' }{r_*'}+2\frac{\alpha'}{\alpha} \, , && \qquad (3.17) \\
& B(r) = \frac{\alpha'' }{\alpha}-\frac{r_*''\alpha' }{r_*'\alpha}-2\left(\frac{\alpha'}{\alpha}\right)^2+(r_*' )^2 (V-\omega^2)  \, , && \qquad (3.18)
\end{aligned}
$$

that is, in terms of the tortoise coordinate $r_*$ and the amplitude $\alpha$, which are defined as follows:

$$
\begin{aligned}
& \partial_r r_*
   = e^{-f}
   \left[
   1 +
   \epsilon_r^2 (e^{-f}b_0-h_0)
   \right] \, ,   \, \, \, \, \, \, \, \, \, \, \, \, && \qquad (3.19) \\
& \frac{\partial_r\alpha}{\alpha}
   = \frac{(\partial_r\phi)^2R^2
   +\epsilon_r^2
   [
   2e^{-f}b_0
   -
   e^{-2f}R^4(\partial_r w)^2/6
   ]
   }{r-\sqrt{R^2(\partial_r\phi)^2-r_0^2}}
   \, .  \, \, \, \, \, \, \, \, \, \, \, \, && \qquad (3.20)
\end{aligned}
$$

The perturbation function $L$ can be expressed in terms of $T$ and $dT/dr$ from equation (3.14), the function $N$ can be obtained from equation (3.13), resulting in a relation $N=-L-2T+\mathcal{O}(J^2)$, and the remaining function $S_1$ can be obtained from equation (3.12). Hence it is sufficient to solve the second order equation for $T$ in order to obtain the quasi-normal modes. This equation can be written as a standard stationary Schrödinger equation with a potential $V(r)$. Finding the quasi-normal modes is thus reduced to an ordinary eigenvalue problem.

If we take $T =\alpha Z$, the perturbation equation can be cast into a Schrödinger equation,

$$
\partial^2_{r_*}Z
    + (\omega^2 - V(r))Z = 0 \, , \tag{3.21}
$$

where $\omega$ is the quasi-normal mode frequency, and $V(r)$ is the potential. In this case, the potential is given by

$$
V(r) =  V_{static}(r) + J^2 \, 
    V_2(r) \, . \tag{3.22}
$$

There is no linear term in the angular momentum $J$. Its contribution only enters at second order, and it is a function of the static background solutions $f$, $\phi$, the first order function $w$, and the second order functions $h_0$, $b_0$, $\phi_{20}$. Taking $C$ to zero gives rise to the following potential

$$
\begin{aligned}
 &  V_{C=0}\,{(r)} =\frac{3r^2r_0^2+2r_0^4}{r^2R^4}+ && \qquad (3.23) \\
 & 
J^2 
\Bigg(
\frac{-12\phi^2}{r^4R^2}+
 \frac{12\pi r
(R^4+r_0^4)
-6r_0^3
(\pi^2-8)
R^2}
{\pi r_0^3 r^4 R^4}\phi+
\frac{
3r(\pi^2-8)
(R^4+r_0^4)
+12\pi r_0
(R^2r^2+2r_0^4)
}{\pi r_0^3 r^4 R^4}
\Bigg) \, .
\end{aligned}
$$

We provide the complete expression of the potential term for $C>0$ elsewhere [66]. In Figure 1, we show the correction to the potential (3.22) of the perturbation system due to slow rotation, obtained with symmetric ($C=0$) and asymmetric ($C\ne 0$) background wormhole configurations. The potential shown has been scaled with $\left(r-C/2\right)^2$.

## 4 Numerical Method

To obtain the unstable radial-led modes, one can start with an asymptotical analysis of equation (3.16). Consider radial distances asymptotically far from the throat, meaning $|r|\to\infty$. By expanding the coefficients it is straightforward to find that at leading order $A(r)\to \mathcal{O}(1/r^2)$ and $B(r)\to -\omega^2$. This of course means that asymptotically far from the throat, our perturbations follow a standard wave equation in flat space-time. General solutions are given by a combination of outgoing and ingoing waves that behave asymptotically like $T(r) \approx e^{\pm i\omega r}$.

Here we are interested in unstable modes, therefore we focus on perturbations for which the eigenvalue $\omega$ is a purely imaginary number, $\omega = i\omega_I$, such that $\omega_I<0$. In this case, an asymptotic analysis of the perturbation function $T(r)$ reveals that it has to decay exponentially to zero at both infinities, $T(\pm\infty)=0$. To numerically solve the master equation and find the eigenvalue $\omega$, we compactify the radial coordinate so that $r = r_0 \tan(\pi x/2)$. In this compactified coordinate, the boundaries $x=\pm 1$ correspond to the two asymptotically flat infinities, $r=\pm \infty$, while at $x=0$ we have the wormhole throat, $r=0$.

In practice we solve the second order ODE for the function $T(r)$ together with an auxiliary equation $E'=0$ where $E=\omega^2$. Non-trivial regular solutions are obtained by fixing the amplitude of the perturbation function to an arbitrary real constant at an arbitrary point $r=r_c$, i.e. $T(r_c)=constant$. The three boundary conditions we impose are $T(\pm1)=0$ and $T(x_0)=1$, where $x_0$ is taken as an arbitrary point in the domain of integration.

As an initial guess, we employ a standard Gaussian-like function for $T(x)$ that is zero at the boundaries, and a constant value for $E(x)$, which typically should be close to the true value of the eigenfrequency in order for the numerical ODE solver COLSYS [69] to converge. This ODE solver is designed for boundary value problems and implements a spline collocation method. COLSYS automatically adapts the mesh points to achieve a prescribed precision of the functions and performs error estimates. Typical estimated errors of the functions for the obtained unstable radial-led modes are on the order of $10^{-12}$. This method has been used successfully before to generate unstable modes of the static EB wormholes [32] (and also applied to scalarized black holes in [67]). As an illustrative example, we show in Figure 1 a typical Gaussian profile of the function $T(r)$.

> **Figure 1.** Potential correction $\tilde{V}_2=V_2(r-C/2)^2$ vs radial coordinate $r$ for several values of $C$ for $r_0=1$, and a typical profile of the perturbation function $T(r)$ (in grey).

In order to generate the values of $\omega_I$, we start from the static limit ($J=0$), fixing $r_0=1$ and an arbitrary value of $C$. We reproduce the results from [32], and by slowly increasing the value of the angular momentum $J$, we get a relation

$$
\omega_I = \omega_I^{(0)} + J^2 \Delta\omega_I^{(2)} \, , \tag{4.24}
$$

where $\omega_I^{(0)}$ is the unstable mode of the static EB wormhole, and $\Delta\omega_I^{(2)}$ is the slow rotation correction to the mode.

## 5 Radial Instability

We exhibit in Figure 2 the dependence of the unstable radial mode on the scaled and dimensionless angular momentum $J/A$ of the EB wormholes, where $A$ is the area of the throat (obtained in second order). We recall that rotating EB wormholes approach the extremal Kerr black hole as their limiting configuration for large angular momenta [61, 62]. Thus the limiting case here is given by $J/A\to 1/(8\pi) \approx 0.0397$. Since fast rotating EB wormholes cannot exceed this limit, the slow rotation approximation can only make sense below this limit.

In Figure 2 we show that, as we increase the value of the angular momentum, the value of $|\omega_I|$ decreases to zero. This is because, for every value of $C$ we have studied, the second order correction to the mode is positive, $\Delta\omega_I^{(2)}>0$. As a result, it is always possible to obtain a critical value of the angular momentum, $J_c$, for which the eigenvalue reaches zero and hence this unstable mode disappears. Most importantly, this happens at a value of $J$ much smaller than the limiting value. In fact, as seen in the inset of Figure 2, the critical values of the scaled angular momentum $J_c/A$ decrease monotonically with C. Moreover, for each of the values of $C$ examined, $J_c/A$ is around $50\%$ of the limiting value, which is well within the regime for which the second order slow rotation approximation has been shown to work well (for example, the quadratic approximation reproduces with excellent precision the spectrum of QNMs of Kerr-Newman black holes [65]).

In Table 1 are the values from the main branch of the unstable radial-led modes in Figure 2. Here $\omega^{(0)}_I$ corresponds to the unstable mode of the static Ellis wormhole, while $\Delta\omega^{(2)}_I$ is the second order correction in spin to the frequency. Note that $\Delta\omega^{(2)}_I$ is *always* positive, showing the tendency of the angular momentum to stabilize the wormhole. We checked numerically that the first order correction is compatible with zero, finding that it is always smaller than $10^{-7}$ (note that in general the linear correction is proportional to the angular number $\mathrm{m}$ (see e.g. [65]). Here $\mathrm{m}$ is zero).

| $C$  | $\omega^{(0)}_I$ | $\Delta\omega^{(2)}_I$ |
|:----:|:----------------:|:----------------------:|
|  0   |      -1.182      |         16.358         |
| 0.05 |      -1.094      |         13.356         |
| 0.1  |      -1.016      |         10.663         |
| 0.2  |      -0.882      |         7.036          |
| 0.4  |      -0.686      |         3.162          |
| 0.7  |      -0.501      |         1.040          |
| 1.0  |      -0.390      |         0.384          |

: **Table 1.** Main unstable radial-led mode for several values of asymmetry parameter $C$.

> **Figure 2.** Main unstable mode $\omega_I \sqrt{A}$ vs angular momentum $J/A$ (scaled with throat area $A$) for several values of $C$. Inset: Critical values $J_c/A$ vs $C$.

> **Figure 3.** Main unstable mode (solid) and second unstable mode (dotted) vs angular momentum $J/A$ (scaled with throat area $A$) for $C=0$, $0.05$, $0.1$ and $0.2$.

However, the critical value of the angular momentum for which the wormholes become stable is presumably still smaller, as the following observations suggest. When the wormholes are set into rotation, a zero mode of the static wormholes changes into a second unstable radial mode of the slowly rotating EB wormholes. Following a quadratic dependence with a small negative coefficient $\Delta\omega_I^{(2)}$, this mode remains at first very small in magnitude. Subsequently, its magnitude increases and it crosses the corresponding main unstable mode not too far from its critical value $J_c/A$. We exhibit both unstable modes in Figure 3. Note that for the values of $C$ displayed the crossing occurs around $J/A\approx0.013$, slightly above $30\%$ of the limiting value.

We show in Table 2 the fitting coefficients for the second branch. Note that in the static limit the mode in this branch tends to a zero mode, and again there is no linear dependence.

| $C$  | $\Delta\omega^{(2)}_I$ |
|:----:|:----------------------:|
|  0   |        -28.185         |
| 0.05 |        -21.431         |
| 0.1  |        -16.697         |
| 0.2  |        -10.220         |

: **Table 2.** Second unstable radial-led mode for several values of asymmetry parameter $C$.

We do not continue both modes beyond their crossing, however, since this crossing is indicating a deficiency of the applied quadratic approximation. A non-perturbative study will allow for a far stronger dependence on the angular momentum than the current quadratic one. We therefore conjecture, that when nearing the critical value, both unstable modes will change much more rapidly, approach each other, merge and disappear. They will thus reflect the behavior observed in higher dimensions in the special case of wormholes with equal angular momenta [63].

## 6 Conclusions

While EB wormholes represent rather simple wormhole solutions they may be considered prototypes whose properties can teach a lot about wormholes in general. Therefore their response to rotation is highly remarkable. Indeed, the potential of rotation to stabilize previously unstable wormholes was suggested before (see e.g. [68]), but we have given first evidence here, that it can indeed happen for wormholes in four space-time dimensions, where rotation implies significant loss of symmetry (associated with the technical challenge).

As we have shown above, the notorious unstable mode of static EB wormholes becomes more stable, as slow rotation is turned on. In our second order and thus quadratic approximation the mode then becomes stable at a critical value of the angular momentum, which depends on the asymmetry parameter $C$. For the EB wormholes we have considered, this critical value is around $50\%$ of the limiting angular momentum. Moreover, we have observed that for rotating wormholes a second mode appears, and similar to the higher dimensional case [63], it tends to merge with the fundamental unstable mode. Hence we have conjectured the behavior of the radial instability for the case of a future non-perturbative study: the radial instability will disappear at even smaller values of the angular momentum, around $30\%$ of the limiting value. Thus for sufficiently rapid rotation the wormholes will be stable.

## Acknowledgements

We gratefully acknowledge support by DAAD, the DFG Research Training Group 1620 *Models of Gravity*, DFG project Ku612/18-1, FCT project PTDC/FIS-AST/3041/2020, COST Actions CA15117 and CA16104, and MICINN project PID2021-125617NB-I00 “QuasiMode". JLBS gratefully acknowledges support from Santander-UCM project PR44/21‐29910.

## References

[1] J. G. Cramer, R. L. Forward, M. S. Morris, M. Visser, G. Benford and G. A. Landis, Phys. Rev. D **51**, 3117 (1995)

[2] M. Safonova, D. F. Torres and G. E. Romero, Phys. Rev. D **65**, 023001 (2002)

[3] V. Perlick, Phys. Rev. D **69**, 064017 (2004)

[4] K. K. Nandi, Y. Z. Zhang and A. V. Zakharov, Phys. Rev. D **74**, 024020 (2006)

[5] F. Abe, Astrophys. J. **725**, 787 (2010)

[6] Y. Toki, T. Kitamura, H. Asada and F. Abe, Astrophys. J. **740**, 121 (2011)

[7] K. Nakajima and H. Asada, Phys. Rev. D **85**, 107501 (2012)

[8] N. Tsukamoto, T. Harada and K. Yajima, Phys. Rev. D **86**, 104062 (2012)

[9] P. K. F. Kuhfittig, Eur. Phys. J.  C **74**, 2818 (2014)

[10] C. Bambi, Phys. Rev. D **87**, 107501 (2013)

[11] R. Takahashi and H. Asada, Astrophys. J. **768**, L16 (2013)

[12] N. Tsukamoto and T. Harada, Phys. Rev. D **95**, 024030 (2017)

[13] P. G. Nedkova, V. K. Tinchev and S. S. Yazadjiev, Phys. Rev. D **88**, 124019 (2013)

[14] T. Ohgami and N. Sakai, Phys. Rev. D **91**, 124020 (2015)

[15] R. Shaikh, Phys. Rev. D **98**, 024044 (2018)

[16] G. Gyulchev, P. Nedkova, V. Tinchev and S. Yazadjiev, Eur. Phys. J. C **78** , 544 (2018)

[17] M. Guerrero, G. J. Olmo, D. Rubiera-Garcia and D. Gómez Sáez-Chillón, Phys. Rev. D **105**, no.8, 084057 (2022)

[18] T. Harko, Z. Kovacs and F. S. N. Lobo, Phys. Rev. D **78**, 084005 (2008)

[19] T. Harko, Z. Kovacs and F. S. N. Lobo, Phys. Rev. D **79**, 064001 (2009)

[20] C. Bambi, Phys. Rev. D **87**, 084039 (2013)

[21] M. Zhou, A. Cardenas-Avendano, C. Bambi, B. Kleihaus and J. Kunz, Phys. Rev. D **94**, 024036 (2016)

[22] F. Lamy, E. Gourgoulhon, T. Paumard and F. H. Vincent, Class. Quant. Grav. **35**, 115009 (2018)

[23] E. Deligianni, J. Kunz, P. Nedkova, S. Yazadjiev and R. Zheleva, Phys. Rev. D **104**, 024048 (2021)

[24] E. Deligianni, B. Kleihaus, J. Kunz, P. Nedkova and S. Yazadjiev, Phys. Rev. D **104**, 064043 (2021)

[25] T. Damour and S. N. Solodukhin, Phys. Rev. D **76**, 024016 (2007)

[26] M. Azreg-Ainou, JCAP **1507**, 037 (2015)

[27] V. Dzhunushaliev, V. Folomeev, B. Kleihaus and J. Kunz, JCAP **1608**, no. 08, 030 (2016)

[28] V. Cardoso, E. Franzin and P. Pani, Phys. Rev. Lett. **116**, 171101 (2016); Erratum: [Phys. Rev. Lett. **117**, 089902 (2016)]

[29] R. A. Konoplya and A. Zhidenko, JCAP **1612**, 043 (2016)

[30] K. K. Nandi, R. N. Izmailov, A. A. Yanbekov and A. A. Shayakhmetov, Phys. Rev. D **95**, 104011 (2017)

[31] P. Bueno, P. A. Cano, F. Goelen, T. Hertog and B. Vercnocke, Phys. Rev. D **97**, 024040 (2018)

[32] J. L. Blázquez-Salcedo, X. Y. Chew and J. Kunz, Phys. Rev. D **98** no.4, 044035 (2018)

[33] B. Azad, F. Loran and A. Mostafazadeh, Eur. Phys. J. C **80** (2020) no.12, 1097

[34] B. Azad, J. L. Blázquez-Salcedo, X. Y. Chew, J. Kunz and D. h. Yeom, Phys. Rev. D **107**, no.8, 084024 (2023)

[35] B. P. Abbott *et al.* [LIGO Scientific and Virgo], Phys. Rev. Lett. **116**, no.6, 061102 (2016)

[36] B. P. Abbott *et al.* [LIGO Scientific and Virgo], Phys. Rev. Lett. **119** , no.16, 161101 (2017)

[37] K. D. Kokkotas and B. G. Schmidt, Living Rev. Rel. **2**, 2 (1999)

[38] E. Berti, V. Cardoso and A. O. Starinets, Class. Quant. Grav. **26**, 163001 (2009)

[39] R. A. Konoplya and A. Zhidenko, Rev. Mod. Phys. **83**, 793 (2011)

[40] H. G. Ellis, J. Math. Phys. **14**, 104 (1973)

[41] H. G. Ellis, Gen. Rel. Grav. **10**, 105 (1979)

[42] K. A. Bronnikov, Acta Phys. Polon. B **4**, 251 (1973)

[43] M. S. Morris, K. S. Thorne and U. Yurtsever, Phys. Rev. Lett. **61**, 1446-1449 (1988)

[44] M. S. Morris and K. S. Thorne, Am. J. Phys. **56**, 395 (1988)

[45] M. Visser, Woodbury, USA: AIP (1995)

[46] D. Hochberg, A. Popov and S. V. Sushkov, Phys. Rev. Lett. **78**, 2050 (1997)

[47] D. Hochberg and M. Visser, Phys. Rev. Lett. **81**, 746 (1998)

[48] M. Visser, S. Kar and N. Dadhich, Phys. Rev. Lett. **90**, 201102 (2003)

[49] K. A. Bronnikov and J. C. Fabris, Phys. Rev. Lett. **96**, 251101 (2006)

[50] M. Alcubierre and F. S. N. Lobo, Fundam. Theor. Phys. **189** (2017)

[51] P. Kanti, B. Kleihaus and J. Kunz, Phys. Rev. Lett. **107**, 271101 (2011)

[52] J. L. Blázquez-Salcedo, C. Knoll and E. Radu, Phys. Rev. Lett. **126**, 101102 (2021)

[53] R. A. Konoplya and A. Zhidenko, Phys. Rev. Lett. **128**, 091104 (2022)

[54] H. a. Shinkai and S. A. Hayward, Phys. Rev. D **66**, 044005 (2002)

[55] J. A. Gonzalez, F. S. Guzman and O. Sarbach, Class. Quant. Grav. **26**, 015010 (2009)

[56] J. A. Gonzalez, F. S. Guzman and O. Sarbach, Class. Quant. Grav. **26**, 015011 (2009)

[57] F. Cremona, F. Pirotta and L. Pizzocchero, Gen. Rel. Grav. **51**, 19 (2019)

[58] M. S. Volkov, Phys. Rev. D **104**, no.12, 124064 (2021)

[59] P. E. Kashargin and S. V. Sushkov, Grav. Cosmol. **14**, 80 (2008)

[60] P. E. Kashargin and S. V. Sushkov, Phys. Rev. D **78**, 064071 (2008)

[61] B. Kleihaus and J. Kunz, Phys. Rev. D **90**, 121503 (2014)

[62] X. Y. Chew, B. Kleihaus and J. Kunz, Phys. Rev. D **94**, 104031 (2016)

[63] V. Dzhunushaliev, V. Folomeev, B. Kleihaus, J. Kunz and E. Radu, Phys. Rev. D **88**, 124028 (2013)

[64] O. J. C. Dias, M. Godazgar and J. E. Santos, Phys. Rev. Lett. **114**, 151101 (2015)

[65] J. L. Blázquez-Salcedo and F. S. Khoo, Phys. Rev. D **107**, no.8, 084031 (2023)

[66] B. Azad, J. L. Blázquez-Salcedo, F. S. Khoo and J. Kunz, in preparation

[67] J. L. Blázquez-Salcedo, D. D. Doneva, J. Kunz and S. S. Yazadjiev, Phys. Rev. D **98**, no.8, 084011 (2018)

[68] T. Matos and D. Nunez, Class. Quant. Grav. **23**, 4485 (2006)

[69] U. Ascher, J. Christiansen and R. D. Russell, Math. Comput. **33**, no.146, 659-679 (1979)
