.PHONY: all cv coverletter clean

LATEX ?= lualatex
CV_SOURCES := cv.tex awesome-cv.cls $(wildcard cv/*.tex)

all: cv.pdf

cv: cv.pdf

cv.pdf: $(CV_SOURCES)
	$(LATEX) -interaction=nonstopmode -halt-on-error $<
	$(LATEX) -interaction=nonstopmode -halt-on-error $<

coverletter: coverletter.pdf

coverletter.pdf: coverletter.tex awesome-cv.cls
	$(LATEX) -interaction=nonstopmode -halt-on-error $<
	$(LATEX) -interaction=nonstopmode -halt-on-error $<

clean:
	$(RM) cv.pdf coverletter.pdf
	$(RM) *.aux *.log *.out *.fls *.fdb_latexmk *.synctex.gz
