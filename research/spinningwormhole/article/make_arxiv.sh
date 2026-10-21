#!/usr/bin/env bash
# Build the arXiv source package of the spinning-wormhole paper.
#
#   research/spinningwormhole/article/make_arxiv.sh
#
# Writes arxiv/ (research.tex with every figure beside it, full-line comments
# stripped since arXiv publishes the source) and arxiv.tar.gz next to this
# script, then compiles the package with pdfLaTeX, arXiv's engine, in a clean
# copy, so a missing file fails here and not on arXiv.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
figs=$(cd "$here/../../../results/spinningwormhole/figures" && pwd)
out="$here/arxiv"
rm -rf "$out" "$here/arxiv.tar.gz"
mkdir -p "$out/figures"

# The figures the paper includes, at their paths below \graphicspath.
grep -o '\\includegraphics\[[^]]*\]{[^}]*}' "$here/research.tex" | sed 's/.*{\(.*\)}/\1/' |
while read -r f; do
    mkdir -p "$out/figures/$(dirname "$f")"
    cp "$figs/$f" "$out/figures/$f"
done

# One search path; full-line comments out (inline % escapes stay).
sed -e 's|^\\graphicspath{.*}$|\\graphicspath{{figures/}}|' -e '/^[[:space:]]*%/d' \
    "$here/research.tex" > "$out/research.tex"
grep -q '^\\graphicspath{{figures/}}$' "$out/research.tex"

(cd "$out" && tar czf "$here/arxiv.tar.gz" research.tex figures)

check=$(mktemp -d)
tar xzf "$here/arxiv.tar.gz" -C "$check"
(cd "$check" && for _ in 1 2 3; do pdflatex -interaction=nonstopmode -halt-on-error research.tex > /dev/null; done)
if grep -q 'undefined' "$check/research.log"; then
    grep 'undefined' "$check/research.log"; exit 1
fi
echo "arxiv.tar.gz: $(tar tzf "$here/arxiv.tar.gz" | grep -vc '/$') files, $(du -h "$here/arxiv.tar.gz" | cut -f1)," \
     "$(pdfinfo "$check/research.pdf" | awk '/^Pages/ {print $2}') pages with pdfLaTeX"
cp "$check/research.pdf" "$out/research_arxiv_check.pdf"
rm -rf "$check"
