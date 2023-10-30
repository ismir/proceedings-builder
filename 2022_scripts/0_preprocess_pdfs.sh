#!/bin/bash
INPUT_PATH="../data2022/2022_camera_ready_drive"
DATASET_OUT_PATH="../data2022/2022_camera_ready"

OUT_PATH=$DATASET_OUT_PATH
if [[ ! -e $OUT_PATH ]]; then
    mkdir $OUT_PATH
fi
for f in $INPUT_PATH/*.pdf; do
  #echo "$f"
  [ -f "$f" ] || break
  filename=$(basename -- "$f")
  filename="${filename%.pdf*}"
  echo $filename
  gs -q -dNOPAUSE -dBATCH -dPDFSETTINGS=/prepress -sDEVICE=pdfwrite -sOutputFile="$OUT_PATH/$filename.pdf" "$INPUT_PATH/$filename.pdf"
done
