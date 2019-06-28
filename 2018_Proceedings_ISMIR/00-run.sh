#!/bin/bash -xue

rm -f 2018_Proceedings_ISMIR.{aux,ain,log,toc}
pdflatex 2018_Proceedings_ISMIR.tex

#ReplaceText.vbs 2018_Proceedings_ISMIR.aux "\IeC " ""
sed -e 's/\\IeC //g' 2018_Proceedings_ISMIR.aux > 2018_Proceedings_ISMIR_2.aux

authorindex -d 2018_Proceedings_ISMIR_2.aux

# running twice is safer
pdflatex 2018_Proceedings_ISMIR.tex
pdflatex 2018_Proceedings_ISMIR.tex

cp 2018_Proceedings_ISMIR.pdf ../2018_Proceedings_ISMIR_Electronic/
cp 2018_Proceedings_ISMIR.pdf ../2018_Proceedings_ISMIR_Electronic_Tools/data/
