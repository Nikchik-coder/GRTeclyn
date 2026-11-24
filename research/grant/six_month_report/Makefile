.PHONY: all clean

all: report.pdf

report.pdf: report.tex Makefile
	mkdir -p .build/texmf-cache
	TEXMFVAR="$(CURDIR)/.build/texmf-cache" TEXMFCACHE="$(CURDIR)/.build/texmf-cache" latexmk -lualatex -interaction=nonstopmode -halt-on-error -outdir=.build report.tex
	cp .build/report.pdf report.pdf

clean:
	rm -rf .build
