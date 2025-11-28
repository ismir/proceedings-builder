# ISMIR 2025 Proceedings Builder

This folder contains all the scripts, templates, and source files used to build the ISMIR 2025 Conference Proceedings.

## Overview

**Conference:** 26th International Society for Music Information Retrieval Conference (ISMIR 2025)  
**Date:** September 21-25, 2025  
**Location:** Daejeon, South Korea  
**ISBN:** 978-1-7327299-5-7  
**Final Output:** 99 accepted papers compiled into a single PDF with full front matter

## Key Changes from Previous Years (202x)

### 1. **Complete Front Matter**
   - Preface with conference statistics, theme, and acknowledgements
   - Organizing committee (with 57 volunteers!)
   - Keynotes (2 speakers)
   - Tutorials (4 sessions)
   - Special Sessions (RenCon, MIREX, Industry Sessions, WIMIR)
   - Satellite Events (HCMIR25, DLfM 2025, LLM4MA)
   - Awards (Test-of-Time, Best Paper, Outstanding Reviewers)
   - Program Committee (75 meta-reviewers, 269 reviewers)
   - Sponsor logos (22 sponsors + 3 WIMIR sponsors)

### 2. **Unicode Support (CJK)**
   - Added `\usepackage{CJKutf8}` for Korean, Chinese, Japanese characters
   - Used `\begin{CJK}{UTF8}{mj}...\end{CJK}` environments where needed
   - Required for keynote bios and special session speakers

### 3. **Custom Header/Footer Handling**
   - Papers already have their own headers - our headers are disabled on paper pages
   - Modified `\includepaper` in `ismirproc.cls` to use `\thispagestyle{plain}`
   - Shorter conference title (`\procshort`) for running headers

### 4. **Cover Page Overlay**
   - Used TikZ to overlay conference details on existing cover PDF
   - Positioned text carefully to avoid design elements

### 5. **6-Digit Paper Numbering**
   - Split proceedings into `000001.pdf` through `000099.pdf` (not `001.pdf`)
   - Custom script: `scripts/4_split_proceedings_6digit.py`

### 6. **Filtering Pipeline**
   - Removed TISMIR and MIREX papers from scientific proceedings
   - Script: `scripts/complete_filter_pipeline.py`

### 7. **Zenodo Upload Integration**
   - Used official `conference-archive` repository scripts
   - Individual DOI per paper
   - Resume logic for interrupted uploads

## File Structure

```
2025_Proceedings_ISMIR/
├── 00-run.sh                          # Main LaTeX build script
├── 2025_Proceedings_ISMIR.tex         # Main LaTeX document
├── ismirproc.cls                      # Custom LaTeX class
├── authorindex.pl                     # Author index generator
│
├── Front Matter LaTeX Files:
│   ├── imprint.tex                    # Title page, editors, ISBN
│   ├── preface.tex                    # Welcome message, statistics
│   ├── organizers.tex                 # Organizing committee, volunteers
│   ├── keynotes.tex                   # Keynotes, special sessions
│   ├── tutorials.tex                  # Tutorials, satellite events
│   ├── awards.tex                     # Awards information
│   ├── committee.tex                  # Reviewers, meta-reviewers
│   ├── logos.tex                      # Sponsor logos
│   └── papers.tex                     # Paper includes (auto-generated)
│
├── external/
│   └── 2025_Cover.pdf                 # Cover page (from booklet)
│
├── logos/                             # All sponsor/org logos (PNG/PDF)
│
├── articles/                          # Camera-ready papers
│   └── paper_XXXX.pdf                 # (example papers included)
│
├── scripts/                           # Python build scripts
│   ├── 1_generate_metadata_json.py    # CSV → JSON conversion
│   ├── 2_generate_paper_tex.py        # Generate papers.tex
│   ├── 3_generate_committee_tex.py    # Generate committee.tex
│   ├── 4_split_proceedings.py         # Split PDF (original 3-digit)
│   ├── 4_split_proceedings_6digit.py  # Split PDF (6-digit version)
│   ├── 5_quality_control.py           # QC checks
│   ├── 6_generate_final_outputs.py    # Generate JSON/CSV for archival
│   ├── prepare_metadata.py            # Merge multiple CSV sources
│   ├── complete_filter_pipeline.py    # Filter TISMIR/MIREX
│   └── resume_upload.py               # Resume Zenodo uploads
│
└── Metadata Templates:
    ├── cmt-metadata-template.csv      # Paper metadata
    ├── session-order-template.json    # Session ordering
    └── session-list-template.txt      # Session names
```

## Build Process

### Prerequisites

1. **Python Environment:**
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install pypdf pdfrw titlecase unidecode
   ```

2. **LaTeX Distribution:**
   - pdflatex with standard packages
   - `CJKutf8` package for Unicode support

3. **Perl:**
   - For `authorindex.pl` script

### Step-by-Step Workflow

#### Phase 1: Prepare Source Data

1. **Collect Paper PDFs:**
   - Place all camera-ready papers in `articles/` as `paper_XXXX.pdf`
   - Paper IDs should match CMT system

2. **Prepare Metadata CSVs:**
   - `Submissions ISMIR 2025.xlsx - Papers.csv` (from CMT)
   - `Programs (shared with session chairs) - 工作表1.csv` (schedule)
   - `ISMIR 2025 paper titles, authors, emails. - detailed_schedule_for_pdf.csv` (ID mapping)

3. **Merge Metadata:**
   ```bash
   python scripts/prepare_metadata.py
   ```
   Output: `cmt-metadata.csv`

4. **Filter Papers (if needed):**
   ```bash
   python scripts/complete_filter_pipeline.py
   ```
   This removes TISMIR/MIREX papers and regenerates all metadata.

#### Phase 2: Generate LaTeX Files

5. **Generate Metadata JSON:**
   ```bash
   cd scripts
   python 1_generate_metadata_json.py
   ```
   Output: `paper-metadata.json`, `session-order.json`

6. **Generate papers.tex:**
   ```bash
   python 2_generate_paper_tex.py
   ```
   Output: `papers.tex` with `\includepaper` commands

7. **Generate committee.tex:**
   ```bash
   python 3_generate_committee_tex.py
   ```
   Input: Meta-reviewer and reviewer CSVs
   Output: `committee.tex`

#### Phase 3: Compile Proceedings

8. **Compile LaTeX:**
   ```bash
   ./00-run.sh
   ```
   This runs:
   - `pdflatex 2025_Proceedings_ISMIR.tex` (3 passes)
   - `perl authorindex.pl 2025_Proceedings_ISMIR` (generate author index)
   - Final `pdflatex` pass

   Output: `2025_Proceedings_ISMIR.pdf`

#### Phase 4: Split and Generate Archival Files

9. **Split into Individual Papers:**
   ```bash
   python scripts/4_split_proceedings_6digit.py \
     --start_page [PDF_PAGE_NUMBER] \
     -o ./split_articles_6digit \
     -j ./paper-metadata-split-6digit.json \
     2025_Proceedings_ISMIR.pdf \
     paper-metadata.json \
     session-order.json
   ```
   
   **Note:** Find `[PDF_PAGE_NUMBER]` by locating where the first session header appears in the PDF (typically page 35-40).

   Output: 99 PDFs as `000001.pdf` through `000099.pdf`

10. **Generate Final Metadata:**
    ```bash
    python scripts/6_generate_final_outputs.py \
      -o ./archival_outputs \
      --start_page [SAME_PAGE_AS_STEP_9] \
      paper-metadata-split-6digit.json \
      session-order.json
    ```
    
    Output:
    - `2025.json` (public metadata)
    - `2025_internal.json` (extended metadata)
    - `2025_dblp.xml` (for DBLP submission)
    - `overview.csv` (for MiniConf)

#### Phase 5: Zenodo Upload (Optional)

11. **Test on Zenodo Sandbox:**
    ```bash
    export ZENODO_TOKEN_DEV="your_sandbox_token"
    cd ../conference-archive
    PYTHONPATH=$(pwd):$PYTHONPATH python scripts/upload_to_zenodo.py \
      ../2025_Proceedings_ISMIR/archival_outputs/2025.json \
      database/conferences.json \
      database/proceedings/2025_test.json \
      --stage dev \
      --num_cpus 1
    ```

12. **Production Upload:**
    ```bash
    export ZENODO_TOKEN_PROD="your_prod_token"
    PYTHONPATH=$(pwd):$PYTHONPATH python scripts/upload_to_zenodo.py \
      ../2025_Proceedings_ISMIR/archival_outputs/2025.json \
      database/conferences.json \
      database/proceedings/2025.json \
      --stage prod \
      --num_cpus 1
    ```

13. **Resume Interrupted Upload:**
    ```bash
    python scripts/resume_upload.py
    # Then run the generated command
    ```

## Important Notes

### LaTeX Compilation Issues

1. **Unicode Characters:**
   - Korean/Chinese/Japanese names must be in `\begin{CJK}{UTF8}{mj}...\end{CJK}`
   - Font: `mj` (mincho) works well for mixed CJK

2. **Author Index Sorting:**
   - Non-ASCII characters in author names may sort incorrectly
   - The script converts "Šimon Libřický" → "Simon Libřický" in `papers.tex` for sorting
   - Original names preserved in PDF content

3. **Header Height Warning:**
   - Already fixed in `ismirproc.cls`: `\setlength{\headheight}{22.38pt}`

### Metadata Considerations

1. **Author Name Consistency:**
   - Check for variations: "McFee" vs "Mcfee", "Weiß" vs "Weiss"
   - The filtering scripts normalize common patterns

2. **Page Numbers:**
   - Final `pages` field in JSON must match PDF footer page numbers
   - Extract from `.toc` file after LaTeX compilation

3. **Session Ordering:**
   - `session-list.txt` defines the order sessions appear in proceedings
   - `session-order.json` maps paper IDs to sessions

### Zenodo Upload Tips

1. **Always test on sandbox first**
2. **Use `num_cpus=1`** to avoid token issues with parallel workers
3. **Export token explicitly:** `export ZENODO_TOKEN_PROD="..."`
4. **Resume logic:** If upload fails, run `resume_upload.py` to continue from where it stopped

## Deliverables

After completing all steps, you should have:

1. **2025_Proceedings_ISMIR.pdf** - Full compiled proceedings (800+ pages)
2. **split_articles_6digit/** - 99 individual paper PDFs (000001-000099)
3. **archival_outputs/2025.json** - Public metadata with Zenodo DOIs
4. **archival_outputs/2025_dblp.xml** - For DBLP submission
5. **archival_outputs/overview.csv** - For MiniConf website
6. **ZIP archive** - All 99 PDFs for backup archive at archives.ismir.net

## Contact

For questions about the 2025 proceedings build process:
- General Chairs: Juhan Nam, Dasaem Jeong
- Publication Chair: Keunwoo Choi

## License

The proceedings compilation scripts are provided as-is for ISMIR conference proceedings generation.

Individual papers are © their respective authors and licensed under CC-BY-4.0.

---

**Last Updated:** November 2025  
**Built With:** LaTeX, Python 3.11+, pypdf, pdfrw

