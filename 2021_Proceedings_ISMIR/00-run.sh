#!/bin/bash -xue

echo cleaning up...
rm -f 2021_Proceedings_ISMIR.{aux,ain,log,toc}

echo initial pdflatex...
pdflatex 2021_Proceedings_ISMIR.tex

echo replacing text...
sed -e 's/\\IeC //g' 2021_Proceedings_ISMIR.aux > 2021_Proceedings_ISMIR_2.aux

echo perl script to generate authorindex...
perl authorindex.pl -d 2021_Proceedings_ISMIR_2.aux

echo final pdflatex...
# running twice is safer
pdflatex 2021_Proceedings_ISMIR.tex
pdflatex 2021_Proceedings_ISMIR.tex