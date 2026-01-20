# Makefile for RISC-4 ISA Specification

MAIN = risc4-isa-spec
PDF = $(MAIN).pdf
TEX = $(MAIN).tex

# CI FLAGS:
# -interaction=nonstopmode: Don't pause for user input on errors
# -halt-on-error: Exit with code 1 immediately if an error occurs (fails the Action)
LATEX_FLAGS = -interaction=nonstopmode -halt-on-error

.PHONY: all clean release

all: $(PDF)

$(PDF): $(TEX)
	pdflatex $(LATEX_FLAGS) $(MAIN)
	pdflatex $(LATEX_FLAGS) $(MAIN)  # Run twice for TOC/References

# Creates a named release file based on the version inside the .tex
release: $(PDF)
	mkdir -p releases
	$(eval VERSION := $(shell grep '\\newcommand{\\specversion}' $(TEX) | sed 's/.*{\(.*\)}/\1/'))
	cp $(PDF) releases/$(MAIN)-v$(VERSION).pdf
	@echo "Created: releases/$(MAIN)-v$(VERSION).pdf"

clean:
	rm -f *.aux *.log *.out *.toc *.pdf *.synctex.gz *.fls *.fdb_latexmk
	rm -rf releases
