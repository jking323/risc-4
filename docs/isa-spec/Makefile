# Makefile for RISC-4 ISA Specification

MAIN = risc4-isa-spec
PDF = $(MAIN).pdf
TEX = $(MAIN).tex

.PHONY: all clean watch

all: $(PDF)

$(PDF): $(TEX)
	pdflatex $(MAIN)
	pdflatex $(MAIN)  # Run twice for TOC

clean:
	rm -f *.aux *.log *.out *.toc *.pdf *.synctex.gz

watch:
	while inotifywait -e modify $(TEX); do make; done

release: $(PDF)
	mkdir -p releases
	cp $(PDF) releases/$(MAIN)-v$(shell grep specversion $(TEX) | head -1 | sed 's/.*{\(.*\)}/\1/').pdf
