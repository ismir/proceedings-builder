# ISMIR proceedings generator: 202x edition
This folder contains scripts to generate the ISMIR 202x proceedings. These scripts were revised in 2023 and based on the documentation originally written in 2021 (in turn borrowed from 2020 and 2019). They are designed to run directly on the exported metadata and papers as downloaded from Microsoft CMT.

For any questions about these scripts (2023 edition), please contact Johan Pauwels at [j.pauwels@qmul.ac.uk](mailto:j.pauwels@qmul.ac.uk)

## What will these scripts deliver?

The scripts (with some manual steps) to prepare proceedings will deliver the following:
1. A full proceedings PDF `202x_Proceedings_ISMIR.pdf`
2. A folder with final paper PDFs with header/footer and page numbers ready to be archived for posterity
3. A publicly available archive JSON `202x.json` for use with proceedings archiver
4. A JSON file `202x_internal.json` that is an extended version of (3) for internal use of the local organizers with some additional metadata that should not be publicly available

(2) and (3) from above are inputs to the [proceedings archival system](https://github.com/ismir/conference-archive), which is the next step after building the proceedings.

## Preparation
Before you start building the proceedings, ensure the following preparation steps are complete. The proceedings of ISMIR 202x can be prepared once all camera-ready papers have been uploaded to CMT. Post the camera-ready date, we can export the metadata as a csv and camera-ready paper PDFs.

### Process paper PDFs

It is strongly advised to carefully check the PDFs for a host of issues including mismatches between author order in metadata and PDF, issues with length of the paper, linenumbers and other formatting issues with paper titles, abstracts and author names. A script to help with checking common issues is given at the end of the process, but for technical reasons, this can only be run after the full proceedings have been generated.

All camera-ready paper PDF files should be in a single folder, as exported from CMT ("Actions" menu > "Download Submissions" > "Submission Files"). Typically, the camera ready files are named as `PaperID\CameraReady\<submission-name>.pdf`

### Prepare metadata

The scripts in this folder assume that the metadata for each paper is stored in a .csv file containing headers of:

- PaperID: CMT submission ID (primary key for all papers, important anchor)
- Title: Paper title
- Abstract
- AuthorDetails: The author list exactly as exported from Microsoft CMT to be used to infer affiliations, typically in the format of "Jane Smith (Best University)*; John Smith (Awesome University); Jane Doe (Another Good Organization)". Ensure there are no additiona semi-colons in the affiliations. Common CSV processing caveats apply (e.g. quote the text if the field includes commas)
- AuthorNames: Names of authors as exported from CMT, typically in the format of "Smith, Jane*; Smith, John; Doe, Jane"
- AuthorEmails: Email list of authors separated by semi-colon, e.g. "jane.smith@bestuni.edu;john.smith@awesomeuni.edu;jane.doe@ago.com"
- PrimarySubjectArea
- SecondarySubjectAreas
- OneLiner: The one-sentence 'main takeaway'
- SessionID: Session name in which the paper will be presented (this is not from CMT and is to be decided by program chairs).


Unfortunately, this csv file cannot be downloaded as-is from Microsoft CMT, but needs to be constructed manually as described below.:
- The starting point is `Papers.xls`, obtained from CMT by clicking on Actions > Export to Excel > Submissions.
- Open this document, sort by column U (Status) and delete all rows corresponding to rejected papers.
- Only keep columns A, D, E, H, I, J, L, M, AK (`Paper ID, Paper Title, Abstract, Authors, Author Names, Author Emails, Primary Subject Area, Secondary Subject Area, Q1 (Main Message)`). Working backwards from the last column helps to retain the original column letters for as long as necessary.
- Rename the headers of the remaining nine columns to `PaperID, Title, Abstract, AuthorDetails, AuthorEmails, AuthorNames, PrimarySubjectArea, SecondarySubjectAreas, OneLiner`. These name changes in the header make the scripts more readable.
- Add a tenth column `SessionID`, which needs to be manually assigned to each paper by the PC chairs. It is assumed that each paper is assigned to a session and there are a limited number of sessions. The session ID is of the format: <SessionName>:<Position>, e.g. `Session I:15` refers to the 15th paper in a session named `Session I`. The order of sessions as we wish to see them in the proceedings needs to be written to the file `session-list.txt`.
- Export the resulting 10 column spreadsheet to a csv file named "cmt-metadata.csv". An example `cmt-metadata.csv` and `session-list.txt` are provided, which you can overwrite.

This metadata csv file is the single source of truth for the metadata, so anytime you want to tweak the metadata (e.g. change capitalization or spelling in title, spelling or order of authors, etc.), do it in this file and rerun the scripts below, rather than editing the intermediate json files created in the next steps. The metadata needs to be checked and verified to match with the PDF, which is assisted by the scripts at the end of the process.



### Setup

Install python dependencies before running the scripts

    pip install -r requirements.txt

You must also have perl installed on your system to run the `authorindex.pl` script and `gs` from the Ghostscript package, which gets called in Step 1.

The proceedings builder has been successfully run on a Mac and other Unix-based systems. We might be able to build it on Windows as well, but the steps haven't been tested. The batch script in Step 3 runs only on Linux/Mac or a Windows Linux Subsystem.

## Generating proceedings

### Step-0: Convert paper titles into a consistent titlecase

The titles as entered by the paper authors will not be consistent in their usage of titlecase. As a first step, we will turn them into consistent shape, following NYT rules. The script below will help you with this, but it unforunately cannot be fully automated because in certain cases the capitalization depends on the part-of-speech (future version of the script could potentially integrate a POS tagger). Start by familiarizing yourself with the conventions on https://titlecaseconverter.com/rules/#NYT, then run the script.

```
$ python3 titlecase_checker.py --csv ../202x_Proceedings_ISMIR/cmt-metadata.csv
```

The first time the script is run, it will make a best effort conversion of all titles and flag points that require manual inspection. A column `TitleChecked` will also be added to the metadata csv file. Go through the hints produced by the scripts and if you manually verfied the correct case of the title, put an "x" in the `TitleChecked` column. This will silence the hints for that title. Iteratively run this script and check the titles until the script returns empty.


### Step-1: Convert CSV to JSON, rename PDF files and prepare a session JSON

The csv metadata is converted to JSON files.

```
$ python3 1_generate_metadata_json.py -o ../202x_Proceedings_ISMIR/paper-metadata.json -s ../202x_Proceedings_ISMIR/session-order.json -d ../202x_Proceedings_ISMIR/articles ../202x_Proceedings_ISMIR/cmt-metadata.csv ../202x_Proceedings_ISMIR/camera_ready ../202x_Proceedings_ISMIR/session-list.txt
```
`../202x_Proceedings_ISMIR/cmt-metadata.csv` is the csv file exported from CMT

`../202x_Proceedings_ISMIR/camera_ready` is the folder with camera-ready papers exported out of CMT

`../202x_Proceedings_ISMIR/session-list.txt` is a text file with a list of sessions (one session name per line) in the same order we need papers added to proceedings. It is assumed that the list of sessions matches with session names listed in SessionID field of metadata csv file.

The `-o` option is the location of the metadata JSON file to write. The `-s` option is the location of the session JSON file to write.

The script also flags non-standard capitalization in author names. If this needs manual rectification, do so in the csv metadata and run the script again.

The session JSON file generated has session to paper mapping, in the following format:

```
[
    {"name": "Session name",
     "papers": [1, 2, 3]
    }, ...
]
```
where the ids in the `papers` key are the submission ids of papers in CMT. This operation also copies the PDF files, extracts the number of pages in each paper and ensures all fonts are embedded in the PDF. For this, the `gs` tool from Ghostscript needs to be installed.

### Step-2: Generate tex files with the list of papers and with the committee

In this step, two tex files that are will be used for the compilation of the proceedings are autogenerated.

The first files includes all the PDF paper files. It requires two inputs, the metadata and session JSON files generated in step-1.
The papers will be renamed to `paper_[id].pdf` corresponding to their paper submission ID in the csv file and copied to a new location so that they can be easily referenced in the tex file.
The session name will be used as the section names in the table of contents. This should have been generated by step 1.
The `-d` option is the location of the articles in the directory containing the proceedings tex.
```
$ python3 2_generate_paper_tex.py -o ../202x_Proceedings_ISMIR/papers.tex ../202x_Proceedings_ISMIR/paper-metadata.json ../202x_Proceedings_ISMIR/session-order.json
```
This generates `../202x_Proceedings_ISMIR/papers.tex` file that will be used to compile all paper PDFs into a single proceedings PDF in the next step.

The second script generates the program committee from files exported from Microsoft CMT. Start by downloading the files "MetaReviewers-1.txt and "Reviewers-1.txt" by clicking on the top left Users menu, then Actions > Export > Meta-Reviers, Reviewers respectively.

```
python3 3_generate_committee_tex.py ../202x_Proceedings_ISMIR/committee.tex --metareviewers_path ../202x_Proceedings_ISMIR/MetaReviewers-1.txt --reviewers_path ../202x_Proceedings_ISMIR/Reviewers-1.txt
```

Do check the generated tex file manually for outdated affiliations and harmonize the wording for people with the same affiliation.

### Step-3: Build the proceedings in LaTeX (manual step)

Place the cover page in the `external` folder and open `202x_Proceedings_ISMIR.tex`. Edit the conference title and cover file name. Update the content in `imprint.tex`, `logos.tex`, `organizers.tex`, `preface.tex`, `keynotes.tex` and `tutorials.tex`.

This step involves seeking inputs from different sub-teams within the conference organization team to gather inputs. Importantly, it also involves approaching the ISMIR board to the ISMIR tech team to reserve an ISBN for the final conference proceedings. Once you have an ISBN, you can use [an online ISBN barcode generator](https://www.free-barcode-generator.net/isbn/) to generate a barcode PDF to add to the proceedings PDF (update `imprint.tex`).

When configured, run the `00-run.sh` bash script. It will compile the `202x_Proceedings_ISMIR.tex` file, generate the author index, perform some text normalization, and recompile everything twice more.
```
$ bash ../202x_Proceedings_ISMIR/00-run.sh
```

Be sure to double-check the author-index to make sure the alphabetization worked. In the worst-case scenario, you may need to run the bash script piecemeal, manually correcting the `202x_Proceedings_ISMIR.ain` file that the perl script produces (e.g. if someone's last name starts with a non-ascii character or is put in the wrong place in the list, e.g. multi word last names starting with "de" or "van".)

### Step-4:Split proceedings

This takes the final document and re-generates the PDFs for each paper so that
they have the header (conference name) and footer (page numbers) on them.

Open the PDF of the final proceedings and find the physical page number in the
file where the header page for the first session starts - this is for option `--start-page`.
`-o` is the directory to write the split articles to, `-j` is the option to export a new metadata json with updated file paths.
```
python3 4_split_proceedings.py --start_page 39 -o ../202x_Proceedings_ISMIR/split_articles -j ../202x_Proceedings_ISMIR/paper-metadata-split.json ../202x_Proceedings_ISMIR/202x_Proceedings_ISMIR.pdf ../202x_Proceedings_ISMIR/paper-metadata.json ../202x_Proceedings_ISMIR/session-order.json 
```
After splitting, the final PDFs ready for archival are stored in `../202x_Proceedings_ISMIR/split_articles` and the updated metadata JSON is stored in
`../202x_Proceedings_ISMIR/paper-metadata-split.json`.

### Step-5: Quality control

With the split papers, a final semi-automatic check for consistency between PDFs and metadata can be made. Ideally, this would be done earlier in the process to avoid having to rerun previous steps when making a change. However, extracting information from PDFs is imprecise and prone to breaking, and the process of first merging the user-generated files followed by splitting them again makes the PDF extraction far more robust.

The script below generates three HTML files in `../202x_Proceedings_ISMIR/pdf-metadata-correspondence`, given the split papers and corresponding metadata JSON.
```
python3 5_quality_control.py -o ../202x_Proceedings_ISMIR/pdf-metadata-correspondence ../202x_Proceedings_ISMIR/paper-metadata-split.json ../202x_Proceedings_ISMIR/split_articles
```

The HTML files highlight differences in titles, author and abstract between metadata and PDFs. Use these files to check exact title and author spelling and punctuation, as well as author order. Note that the PDF extraction is far from perfect, which is most notable for the abstracts, so do a visual verification in the PDF before changing anything.

It is easiest to adapt the metadata to the PDF, but in case of obvious error in the PDF the authors will need to be contacted. As the PDF author names are extracted from the copyright statement (for robustness reasons), one more common error can be detected, namely when authors forgot replace the "Author Author Author" placeholder. In this cause, an updated version will need to be created by the authors.

### Step-6: Generate output files/folders for archiving

This will generate the final output files containing metadata (abstracts, page numbers, authors, etc) used for archiving the final proceedings on Zenodo (see https://github.com/ismir/conference-archive/). Note that the `--start_page` option again refers to the cover page of the first session, but now using the number *as in the page footer* (i.e. how it would be cited in a bibliography, though you'll need to count from an earlier footer since cover pages don't display one), not the page number in the PDF file.
```
$ python3 6_generate_final_outputs.py -o ../202x_Proceedings_ISMIR/metadata_final --start_page 19 ../202x_Proceedings_ISMIR/paper-metadata-split.json ../202x_Proceedings_ISMIR/session-order.json
```

After these six steps,

`../202x_Proceedings_ISMIR/metadata_final` will contain the internal and public proceedings metadata json

`../202x_Proceedings_ISMIR/split_articles` will contain the final paper PDFs

These are used as inputs to archiving the final proceedings *after* the conference on archives.ismir.net and Zenodo. Start from https://github.com/ismir/conference-archive/tree/master/202x_archive/README.md

*Before* the conference, the `overview.csv` file needs to be send to the web team as input to the MiniConf `ismir202xprogram.ismir.net` site and the `split_articles` folder needs to be sent to the ISMIR webmaster for upload on `archives.ismir.net`, which MiniConf uses to embed the PDFs on its pages.
