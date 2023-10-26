#!/bin/bash -xue

echo cleaning up...
rm -f 202x_Proceedings_ISMIR.{aux,ain,log,toc}

echo initial pdflatex...
pdflatex 202x_Proceedings_ISMIR.tex

echo replacing text...
sed -e 's/\\IeC //g' 202x_Proceedings_ISMIR.aux > 202x_Proceedings_ISMIR_2.aux

echo perl script to generate authorindex...
perl authorindex.pl -d 202x_Proceedings_ISMIR_2.aux

echo final pdflatex...
# running twice is safer
pdflatex 202x_Proceedings_ISMIR.tex
pdflatex 202x_Proceedings_ISMIR.tex

echo rename pdf
mv 202x_Proceedings_ISMIR.pdf $(date +"%Y")_Proceedings_ISMIR.pdf
