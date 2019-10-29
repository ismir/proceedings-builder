# ISMIR proceedings generator

## 2019 edition

In 2019 we used the Microsoft CMT paper review platform.

The list of papers is downloaded as an excel file. Open and export this file
as CSV, preserving headers. Remove the first lines from this file if they're
blank.

Download the archive containing the submitted PDFs.

### Setup

Install python dependencies

    pip install -r requirements.txt

### Generating proceedings

1. Convert CSV to JSON and rename paper files

The papers need to be renamed so that they can be easily referenced in the tex
file.

    python 1_merge_csv_papers.py -o ../2019-paper-metadata.json -d ../2019_Proceedings_ISMIR/articles ../CameraReadyPapers.csv ~/Downloads/CameraReadySubmissions

The `-o` option is the location of the metadata JSON file. The `-d` option is
the location of the articles in the directory containing the proceedings tex.

This operation also performs some basic name normalisation if needed, and
extracts the number of pages in each paper.

2. Generate the tex file with the list of papers

You will need a _session order_ file. This is json in the following format:

```
[
    {"name": "Session name",
     "papers": [1, 2, 3]
    }, ...
]
```
Where the ids in the `"papers"` key are the submission ids of papers in CMT.
The session name will be used as the section names in the tex TOC.

    python 2_generate_paper_tex.py -o ../2019_Proceedings_ISMIR/papers.tex ../2019-paper-metadata.json ../2019-session-order.json

3. Build the proceedings

Update the front matter and section headings as needed. These are all saved as
PDF files in the `external` directory.

    cd 2019_Proceedings_ISMIR
    bash 00-run.sh

4. Split proceedings

This takes the final document and re-generates the PDFs for each paper so that
they have the header (conference name) and footer (page numbers) on them.

Open the PDF of the final proceedings and find the physical page number in the
file where the header page for the first session starts.
`-o` is the directory to write the split articles to.

    python 3_split_proceedings.py -s [pgnumber] -o data/split_articles ../2019_Proceedings_ISMIR.pdf ../2019-paper-metadata.json ../2019-session-order.json

