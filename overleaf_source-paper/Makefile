all: main.pdf

main.pdf: main.tex
	pdflatex main.tex
	bibtex languageresource
	bibtex main
	pdflatex main.tex
	pdflatex main.tex

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot *.pdf *.glo *.ist
