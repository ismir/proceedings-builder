#!/bin/bash -xue

echo cleaning up...
rm -f 2020_Proceedings_ISMIR.{aux,ain,log,toc}

echo initial pdflatex...
pdflatex 2020_Proceedings_ISMIR.tex

echo replacing text...
sed -e 's/\\IeC //g' 2020_Proceedings_ISMIR.aux > 2020_Proceedings_ISMIR_2.aux

echo perl script to generate authorindex...
perl authorindex.pl -d 2020_Proceedings_ISMIR.aux

echo final pdflatex...
# running twice is safer
pdflatex 2020_Proceedings_ISMIR.tex
pdflatex 2020_Proceedings_ISMIR.tex

echo copying...
cp 2020_Proceedings_ISMIR.pdf ..
