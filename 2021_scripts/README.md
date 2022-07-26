# ISMIR proceedings generator: 2021 edition
This folder contains scripts to generate the ISMIR 2021 proceedings. Note that these scripts were originally written in 2021 (in turn borrowed from 2020 and 2019) to run directly on the exported metadata and papers as downloaded from Microsoft CMT. 

For any questions about these scripts (2021 edition), please write to Ajay Srinivasamurthy [ajays.murthy@upf.edu](mailto:ajays.murthy@upf.edu)

## What will these scripts deliver?

The scripts (with some manual steps) to prepare proceedings will deliver the following:
1. [A full proceedings PDF](http://archives.ismir.net/ismir2021/2021_Proceedings_ISMIR.pdf)
2. A folder with final paper PDFs with header/footer and page numbers ready to be archived for posterity
3. A publicly available archive [JSON](https://github.com/ismir/conference-archive/blob/master/database/proceedings/2021.json) for use with proceedings archiver
4. A JSON that is an extended version of (2) for internal use of the local organizers with some additional metadata that should not be publicly available

(2) and (3) from above are inputs to the [proceedings archival system](https://github.com/ismir/conference-archive), which is the next step after building the proceedings. 

## Preparation
Before you start building the proceedings, ensure the following preparation steps are complete. The proceedings of ISMIR 2021 can be prepared once all camera-ready papers have been uploaded to CMT. Post the camera-ready date, we can export the metadata as a csv and camera-ready paper PDFs. 

### Process paper PDFs

It is strongly advised to carefully check the PDFs for a host of issues including mismatches between author order in metadata and PDF, issues with length of the paper, linenumbers and other formatting issues with paper titles, abstracts and author names, and any fonts that haven't been embedded into the PDF. It is suggested that all PDFs be run through ghostscript to embed fonts using a one liner below: 

```
gs -q -dNOPAUSE -dBATCH -dPDFSETTINGS=/prepress -sDEVICE=pdfwrite -sOutputFile=<OUTPUT.pdf> <INPUT.pdf>

```

All camera-ready paper PDF files should be in a single folder, as exported from CMT. Typically, the camera ready files are named as `PaperID\Camera_ready\<myfancyname>.pdf`


### Prepare metadata

The scripts in this folder assume that the metadata for each paper is stored in a .csv file containing headers of:
```
PaperID: CMT submission ID (primary key for all papers, important anchor)
SessionID: Session name in which the paper will be presented (this is not from CMT and is to be decided by program chairs). The session ID is of the format: <SessionName>:<Position>, e.g. MUS:15 refers to the 15th paper in a session named "MUS"
Title: Paper title
Abstract
PrimaryContactAuthorName
PrimaryContactAuthorEmail
AuthorDetails: The author list exactly as exported from Microsoft CMT to be used to infer affiliations, typically in the format of "Jane Smith (Best University)*; John Smith (Awesome University); Jane Doe (Another Good Organization)". Ensure there are no additiona semi-colons in the affiliations. Common CSV processing caveats apply (e.g. quote the text if the field includes commas)
AuthorNames: Names of authors as exported from CMT, typically in the format of "Smith, Jane*; Smith, John; Doe, Jane"
AuthorEmails: Email list of authors separated by semi-colon, e.g. "jane.smith@bestuni.edu;john.smith@awesomeuni.edu;jane.doe@ago.com"
PrimarySubjectArea
SecondarySubjectAreas
SpecialTrack: Was the paper submitted to special call ? Yes/No
OneLiner: The one-sentence 'main takeaway'
```

Most of these fields are as downloaded from CMT with name changes to headers to make them read better and be better keys. SessionID is something that the PC chairs have to assign to papers. It is assumed that each paper is assigned to a session and there are a limited number of sessions. The order of sessions as we wish to see them in the proceedings is listed in a file and is provided as one of the inputs. 

The content needs to be checked and verified to matched between PDF and the submission. The scripts here assume data is already cleaned up. The ordering (or presence of other headers) does not matter. This table can be exported from CMT or assembled manually, if necessary.


### Setup

Install python dependencies before running the scripts

    pip install -r requirements.txt

You must also have perl installed on your system to run the `authorindex.pl` script.

I've run the proceedings builder successfully on a mac, so it should work on Linux as well. We might be able to build it on Windows as well, but the steps haven't been tested. The batch script in Step 3 runs only on Linux/Mac or a Windows Linux Subsystem. 

### Generating proceedings

1. Convert CSV to JSON, rename files and prepare a session JSON

The csv metadata is converted to a JSON. The papers will be renamed to `paper_[id].pdf` corresponding to their paper submission ID in the csv file and copied to a new location so that they can be easily referenced in the tex file.

    python3 1_generate_metadata_json.py -o ../2021_Proceedings_ISMIR/2021-paper-metadata.json -d ../2021_Proceedings_ISMIR/articles -s ../2021_Proceedings_ISMIR/2021-session-order.json ../2021_Proceedings_ISMIR/2021-cmt-metadata.csv ../2021_Proceedings_ISMIR/2021_camera_ready ../2021_Proceedings_ISMIR/2021-session-list.txt

../2021_Proceedings_ISMIR/2021-cmt-metadata.csv is the csv file from 

../2021_Proceedings_ISMIR/2021_camera_ready is the folder with camera-ready papers exported out of CMT

../2021_Proceedings_ISMIR/2021-session-list.txt is text file with a list of sessions (one session name per line) in the same order we need papers added to proceedings. It is assumed that the list of sessions matches with session names listed in SessionID field of metadata csv file. 

The `-o` option is the location of the metadata JSON file to write. The `-d` option is the location of the articles in the directory containing the proceedings tex. The `-s` option is the location of the session JSON file to write.

The session JSON file generated has session to paper mapping, in the following format:

```
[
    {"name": "Session name",
     "papers": [1, 2, 3]
    }, ...
]
```
where the ids in the `"papers"` key are the submission ids of papers in CMT. 

This operation also extracts the number of pages in each paper.

2. Generate the tex file with the list of papers

It requires two inputs, the metadata and session JSON files generated in step-1

The session name will be used as the section names in the table of contents. This should have been generated by step 1.

    python3 2_generate_paper_tex.py -o ../2021_Proceedings_ISMIR/papers.tex ../2021_Proceedings_ISMIR/2021-paper-metadata.json ../2021_Proceedings_ISMIR/2021-session-order.json

This generates ../2021_Proceedings_ISMIR/papers.tex file that will be used to compile all paper PDFs into a single proceedings PDF in the next step.

3. Build the proceedings in LaTeX (manual step)

Update the front matter and section headings as needed. These are all saved as
PDF files in the `external` directory, and included in the proceedings with the \includepdf command in the `tutorials.tex`, `keynotes.tex`, and `2021_Proceedings_ISMIR.tex` files. Add or remove files as needed. (Since these sections can change considerably from year-to-year, there's probably no benefit to automating this step.)

When configured, run the `00-run.sh` bash script. It will compile the `2021_Proceedings_ISMIR.tex` file, generate the author index, perform some text normalization, and recompile everything twice more.

    cd 2021_Proceedings_ISMIR
    bash 00-run.sh

Be sure to double-check the author-index to make sure the alphabetization worked. In the worst-case scenario, you may need to run the bash script piecemeal, manually correcting the `2021_Proceedings_ISMIR.ain` file that the perl script produces (e.g. if someone's last name starts with a non-ascii character and is put in the wrong place in the list.)

4. Split proceedings

This takes the final document and re-generates the PDFs for each paper so that
they have the header (conference name) and footer (page numbers) on them.

Open the PDF of the final proceedings and find the physical page number in the
file where the header page for the first session starts - this is for option `-s`.
`-o` is the directory to write the split articles to, `-j` is the option to export a new metadata json with updated file paths. 

    python3 4_split_proceedings.py -s 45 -o ../2021_Proceedings_ISMIR/split_articles -j ../2021_Proceedings_ISMIR/2021-paper-metadata-split.json ../2021_Proceedings_ISMIR/2021_Proceedings_ISMIR.pdf ../2021_Proceedings_ISMIR/2021-paper-metadata.json ../2021_Proceedings_ISMIR/2021-session-order.json 

After splitting, the final PDFs ready for archival are stored in `../2021_Proceedings_ISMIR/split_articles` and the updated metadata JSON is stored in 
`../2021_Proceedings_ISMIR/2021-paper-metadata-split.json`


5. Generate output files/folders for archiving

    This will generate files containing metadata (abstracts, page numbers, authors, etc) used for archiving the final proceedings on Zenodo (see https://github.com/ismir/conference-archive/). Note that the `-s` option here refers to the page number not of the .pdf file but *in the page footer* (i.e. how it would be cited in a bibliography).

    python3 5_generate_final_outputs.py -o ../2021_Proceedings_ISMIR/metadata_final -s 17 ../2021_Proceedings_ISMIR/2021-paper-metadata-split.json ../2021_Proceedings_ISMIR/2021-session-order.json


After these five steps, 
../2021_Proceedings_ISMIR/metadata_final will contain the internal and public proceedings metadata json

../2021_Proceedings_ISMIR/split_articles will contain the final paper PDFs

These are used as inputs to archiving the final proceedings of the conference on archives.ismir.net and Zenodo. Start from https://github.com/ismir/conference-archive/tree/master/2021_archive/README.md