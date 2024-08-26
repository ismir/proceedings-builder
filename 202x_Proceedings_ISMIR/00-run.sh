#!/bin/bash -xue

echo cleaning up...
rm -f 202x_Proceedings_ISMIR.{aux,ain,log,out,toc}

echo initial pdflatex...
pdflatex 202x_Proceedings_ISMIR.tex

echo perl script to generate authorindex...
perl authorindex.pl 202x_Proceedings_ISMIR.aux

echo final pdflatex...
# running twice is safer
pdflatex 202x_Proceedings_ISMIR.tex
pdflatex 202x_Proceedings_ISMIR.tex
