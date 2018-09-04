# ISMIR Proceedings 2018

Scripts for generating ISMIR 2018 proceedings

## Directories in this repository

| Directory | Purpose |
| --- | --- |
| `./` | Scripts for global processing |
| `data/` | Input: Metadata about papers, sessions, etc |
| `2018_Proceedings_ISMIR/articles/` | Input: PDF files of all articles by number, e.g., `004_Paper.pdf` |
| `2018_Proceedings_ISMIR/external/` | Input: Front matter created in Word or google docs |
| `2018_Proceedings_ISMIR_Electronic_Tools/templates/` | Input: templates for HTML proceedings, DBLP |
| `2018_Proceedings_ISMIR/` | LaTeX files for generating PDF proceedings |
| `2018_Proceedings_ISMIR_Electronic_Tools/` | Scripts for generating HTML proceedings for USB sticks |
| `2018_Proceedings_ISMIR_Electronic/` | Output: some HTML proceedings files |
| `2018_Proceedings_ISMIR_Electronic_Tools/output/` | Output: other HTML proceedings files |


## Steps to run scripts and generate PDF and HTML proceedings
---Create the PDF version---
0. Install NotePad++, Python 3.6, Perl, Tex editor
1. Import paper metadata (paper list, reviewers, program committee, session info, and session index) into `data/completePaperList.xlsx`
	a. Check the consistency of paper titles and author names between the meta data and the camera-ready PDF
	b. Check the consistency of author names of the same author
	c. Order paper titles in each poster session in alphabetical order
	d. Order reviewers by their last name in alphabetical order
	e. Order program committee members by their last name in alphabetical order
	f. sessionInfo sheet: column A is the session tag; column B is the session name displayed in the proceedings; column C is the page number of the '2018_Proceedings_ISMIR/external/12_Sessions.docx'
	g. session_index sheet: Start Page column can be specified later once the proceedings is assembled. It's used for extracting the stamped PDF of each paper for the electronic proceedings.
2. Save each of the above sheets as a .txt file with the same name as the sheet in 'data/' folder using utf8 encoding; To do so in Windows, first save the sheet as a unicode text file, then use Notepad++ to change its encoding.
3. Run `./deriveFiles.py` to derive other metadata files from those. They include:
	a. One .txt file for each session in the '2018_Proceedings_ISMIR_Electronic_Tools\data' folder
	b. 2018_Proceedings_ISMIR/papers.tex
4. Create directory `2018_Proceedings_ISMIR/articles/` and put all camera-ready PDFs inside
5. Run `2018_Proceedings_ISMIR/01-get_pages_total.py` to calculate page lengths of files for indexing purposes. This file will be saved to '2018_Proceedings_ISMIR_Electronic_Tools\data' folder
6. Modify '2018_Proceedings_ISMIR/confproc.cls to change the header to the new conference
7. Modify files in the '2018_Proceedings_ISMIR/external/' folder accordingly
8. Start cmd as administrator; Run `2018_Proceedings_ISMIR/00-run.sh` to compile the PDF proceedings. It creates three copies, in '2018_Proceedings_ISMIR', '2018_Proceedings_ISMIR_Electronic', and '2018_Proceedings_ISMIR_Electronic_Tools\data', respectively.
	a. On Windows, I encountered some problems running 00-run.sh. I had to install GitBash to run the "sed" command, and use cmd to run "pdflatex" and "authorindex" commands;
	b. To run the "authorindex" command, you need to download Perl.
	c. You may need to manually correct a couple of author names in the generated author index list, as the splitting of first/last names by "authorindex" can be wrong. 

---Create the HTML version (USB content)---
9. Modify session_index sheet of 'data/completePaperList.xlsx' to reflect the true starting page numbers of sessions, then save this sheet as 'session_index.txt' to the 'data/' folder with utf8 edcoding. Copy this file to '2018_Proceedings_ISMIR_Electronic_Tools/data'
10. Run `2018_Proceedings_ISMIR_Electronic_Tools/00-split_proceedings.py`. Each paper's PDF with the ISMIR proceedings stamp is now splitted into '2018_Proceedings_ISMIR_Electronic_Tools\data\articles_splitted'
11. Modify files '2018_Proceedings_ISMIR_Electronic_Tools/templates', especially the dblp.txt file
12. Run `2018_Proceedings_ISMIR_Electronic_Tools/01-generate_overview_website.py`
13. Run `2018_Proceedings_ISMIR_Electronic_Tools/02-generate_author_index.py`
14. Run `2018_Proceedings_ISMIR_Electronic_Tools/03-generate_reviewer_list.py`
15. Compose a website for USB key content based on the generated pages; the cover page requires some photos of the attractions in Suzhou.
