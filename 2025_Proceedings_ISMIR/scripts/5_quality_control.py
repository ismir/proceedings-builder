#!/usr/bin/env python3
import pdfminer.high_level
import pdfminer.layout
import pdfminer.settings
from pdfrw import PdfReader, PdfWriter
from pdfrw.findobjs import page_per_xobj
from pathlib import Path
from difflib import HtmlDiff
import re
import tempfile
import json


pdfminer.settings.STRICT = False
MAX_LEN = 2000


def cleanup(text):
    text = text.strip()
    text = text.replace('-\n', '')
    text = text.replace('\n', ' ')
    text = text.replace('ﬁ', 'fi')
    text = text.replace('ﬂ', 'fl')
    text = text.replace('  ', ' ')
    return text


def extract(raw_text):
    authors_title_match = re.search(r'At(?:-\n)?tri(?:-\n)?bu(?:-\n)?tion:\W([^“]+),\W“([^”]+)”,?\W', raw_text)
    authors = cleanup(authors_title_match.group(1))
    title = cleanup(authors_title_match.group(2))
    abstract_match = re.search(r'ABSTRACT\W{2,}(.+)\W{2,}1\.\W+[A-Z]{5,}', raw_text, flags=re.DOTALL)
    if not abstract_match:
        abstract_match = re.search(r'ABSTRACT\W{2,}(.+)\W{2,}1\.?\W+Intro', raw_text, flags=re.DOTALL)
    abstract = cleanup(abstract_match.group(1))
    return authors, title, abstract


def quality_control(metadata_path, articles_dir, control_dir):
    metadata_authors = []
    pdf_authors = []
    metadata_titles = []
    pdf_titles = []
    metadata_abstracts = []
    pdf_abstracts = []
    with open(metadata_path) as f:
        papers = json.load(f)
    for paper in papers:
        pdf_path = Path(articles_dir) / paper['extra']['split_file']
        with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
            first_page = list(page_per_xobj(PdfReader(pdf_path).pages[:1]))
            writer = PdfWriter(f.name)
            writer.addpages(first_page)
            writer.write()
            raw_text = pdfminer.high_level.extract_text(f.name)
        authors, title, abstract = extract(raw_text)
        metadata_lastnames = [n.split(' ')[-1] for n in paper['author']]
        pdf_lastnames = [n.split(' ')[-1] for n in authors.replace(' and ', ',').split(',') if n]
        if metadata_lastnames != pdf_lastnames:
            metadata_authors.append(' '.join(metadata_lastnames))
            pdf_authors.append(' '.join(pdf_lastnames))
        if title.upper() != paper['title'].upper():
            metadata_titles.append(paper['title'].upper())
            pdf_titles.append(title.upper())
        if abstract != paper['abstract']:
            metadata_abstracts.extend(paper['abstract'].split('. '))
            pdf_abstracts.extend(abstract.split('. '))

    diff = HtmlDiff(wrapcolumn=80)
    control_dir.mkdir(parents=True, exist_ok=True)
    with open(control_dir / 'author-diff.html', 'w') as f:
        f.write(diff.make_file(metadata_authors, pdf_authors, 'Authors in Metadata', 'Authors in PDFs'))
    with open(control_dir / 'title-diff.html', 'w') as f:
        f.write(diff.make_file(metadata_titles, pdf_titles, 'Titles in Metadata', 'Titles in PDFs'))
    with open(control_dir / 'abstract-diff.html', 'w') as f:
        f.write(diff.make_file(metadata_abstracts, pdf_abstracts, 'Abstracts in Metadata', 'Abstracts in PDFs', context=True, numlines=1))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("split_metadata", help="JSON containing metadata for split PDFs")
    parser.add_argument("split_articles", help="directory containing the split PDF files")
    parser.add_argument("-o", "--output", required=True, help="output directory to diff pages to", type=Path, default='../202x_Proceedings_ISMIR/pdf-metadata-correspondence')

    args = parser.parse_args()
    quality_control(args.split_metadata, args.split_articles, args.output)
