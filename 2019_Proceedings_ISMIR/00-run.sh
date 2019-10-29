#!/bin/bash -xue

rm -f 2019_Proceedings_ISMIR.{aux,ain,log,toc}
pdflatex 2019_Proceedings_ISMIR.tex

#ReplaceText.vbs 2019_Proceedings_ISMIR.aux "\IeC " ""
sed -e 's/\\IeC //g' 2019_Proceedings_ISMIR.aux > 2019_Proceedings_ISMIR_2.aux

perl authorindex.pl -d 2019_Proceedings_ISMIR_2.aux

# running twice is safer
pdflatex 2019_Proceedings_ISMIR.tex
pdflatex 2019_Proceedings_ISMIR.tex

cp 2019_Proceedings_ISMIR.pdf ..
