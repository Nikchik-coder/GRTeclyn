# D46 N128 evolution closeout

The evolution terminated at 18:56:57 MSK on October 31 (exit 6), with a
NaN in K on level 3 after the advance starting at t=141.4325. The last
finite coarse diagnostic is t=141.43 and the last consumed plot is t=141;
the requested t=150 was not reached. Checkpoints were disabled.

The article uses only the early interval through t=100. The 0.2--1%
areal-radius contraction fit spans t=77--96 and gives tau=11.479644.
The first 1% contraction occurs at t=96.145495, versus t=73.724877 in the
classical reference. The classical reference briefly contracts by 1.118%
then expands; its plotted growth rate fits the later expansion. These are
different dynamical branches, not a same-branch rate suppression test.
The first 2% potential crossing is excluded from the article's analysis
window. The t=100 cutoff is conservative, not a convergence certificate:
constraints grow substantially afterward and the late plunge ends in NaN.

All saved small-data and constraint streams, numerical parameters, preflight,
manifest, backtrace, and complete evolution/consumer logs are retained.
Gzip streams preserve all samples. Deployment paths and node identity in
text are normalized; archive_manifest.json records source and archived
SHA256 hashes. Numerical fields for the initial background are in the
parent directory. NFS frames and slice caches are retained; fixed-scale
movies are restricted to t<=100. All 14 movies are also archived in movies/;
movie_closeout.json records hashes, frame counts and fixed colour limits.
Encoded K, phi and chi frames at t=20 and t=80 have been visually checked. The last three scratch plotfiles were
pruned only after transfer and hash verification; no checkpoints existed.
