#!/usr/bin/python

import PyPDF2
import glob
import ntpath

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

all_pdf_files = glob.glob('articles/*.pdf')
with open('../2018_Proceedings_ISMIR_Electronic_Tools/data/pages_total.txt', 'w') as f:
    f.write('filename\tpages_total\n')

    for cur_pdf_filename in all_pdf_files:
        with open(cur_pdf_filename, 'rb') as cur_pdf_fh:
            cur_pdf = PyPDF2.PdfFileReader(cur_pdf_fh)
            f.write(path_leaf(cur_pdf_filename) + '\t' + str(cur_pdf.getNumPages()) + '\n')
