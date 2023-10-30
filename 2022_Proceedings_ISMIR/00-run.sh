#!/bin/bash -xue

###OPTIONAL/ TO BE RUN ONCE
#export TEXMFCNF='$CONDA_PREFIX/share/texlive/texmf-dist/web2c/'
#texconfig rehash

echo cleaning up...
rm -f 2022_Proceedings_ISMIR.{aux,ain,log,toc}

echo initial pdflatex...
pdflatex 2022_Proceedings_ISMIR.tex

echo replacing text...
sed -e 's/\\IeC //g' 2022_Proceedings_ISMIR.aux > 2022_Proceedings_ISMIR_2.aux

echo perl script to generate authorindex...
perl authorindex.pl -d 2022_Proceedings_ISMIR_2.aux

echo final pdflatex...
# running twice is safer
pdflatex 2022_Proceedings_ISMIR.tex
pdflatex 2022_Proceedings_ISMIR.tex