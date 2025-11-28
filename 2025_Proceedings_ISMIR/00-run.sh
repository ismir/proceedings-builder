#!/bin/bash -xue

echo cleaning up...
rm -f 2025_Proceedings_ISMIR.{aux,ain,log,out,toc}

echo initial pdflatex...
pdflatex 2025_Proceedings_ISMIR.tex

echo perl script to generate authorindex...
perl authorindex.pl 2025_Proceedings_ISMIR.aux

echo final pdflatex...
# running twice is safer
pdflatex 2025_Proceedings_ISMIR.tex
pdflatex 2025_Proceedings_ISMIR.tex
