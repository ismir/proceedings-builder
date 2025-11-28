# Migration Notes: From RESULT-2025-ismir-proceedings to proceedings-builder

This document explains what was moved from the working directory to this clean proceedings-builder folder.

## What Was Copied

### Source Files (Essential)
- ✅ **10 LaTeX files**: Main document + all front matter (preface, organizers, keynotes, tutorials, awards, committee, logos, imprint)
- ✅ **ismirproc.cls**: Custom class file with header/footer fixes
- ✅ **00-run.sh**: Build script
- ✅ **authorindex.pl**: Author index generator

### Scripts
- ✅ **11 Python scripts** in `scripts/` folder:
  - Original 202x scripts (1-6)
  - Our custom `4_split_proceedings_6digit.py`
  - Utility scripts: `prepare_metadata.py`, `complete_filter_pipeline.py`, `resume_upload.py`

### Content
- ✅ **48 logo files** (sponsors, organizing institutions, WIMIR)
- ✅ **Cover PDF** in `external/2025_Cover.pdf`
- ✅ **3 example papers** in `articles/` (as templates)

### Templates
- ✅ **3 metadata templates**: CSV, JSON, TXT formats (renamed with `-template` suffix)

## What Was Excluded

### Build Artifacts (Not Needed)
- ❌ Compiled PDFs (except cover)
- ❌ LaTeX temporary files (.aux, .log, .out, .toc, .ain)
- ❌ Generated papers.tex (this is an output)
- ❌ Generated JSON metadata (outputs)
- ❌ Split articles folder (output)
- ❌ Camera-ready folder with all 99 PDFs (too large, only 3 examples kept)

### Temporary/Debug Files
- ❌ All the `.md` summary files we created during debugging
  - BUILD_SUMMARY.md
  - FINAL_BUILD_SUMMARY.md
  - COMPLETE_BUILD_REPORT.md
  - VISUAL_FIXES_APPLIED.md
  - CONTENT_UPDATES_SUMMARY.md
  - FINAL_PROCEEDINGS_STATUS.md
  - AWARDS_ADDED.md
  - ADDITIONAL_CONTENT_5_SUMMARY.md
  - COMMITTEE_FIX_SUMMARY.md
  - NAME_FIXES_SUMMARY.md
  - SIMON_SORT_FIX.md
  - REVIEWER_FEEDBACK_IMPLEMENTATION.md
  - ADDITIONAL_CONTENT_7_UPDATES.md
- ❌ Backup files (papers.tex.bak, 202x_Proceedings_ISMIR.tex)
- ❌ Intermediate CSVs (cmt-metadata-original.csv, cmt-metadata-filtered.csv)

### One-Time Fix Scripts (Not Needed)
- ❌ `fix_author_metadata.py`
- ❌ `fix_author_metadata_complete.py`
- ❌ `fix_simon_sort.py`
- ❌ `reorganize_papers.py`
- ❌ `filter_proceedings.py`
- ❌ `find_paper_start.py`
- ❌ `generate_2025_json.py`
- ❌ `upload_to_zenodo_sandbox.py`

These were specific to our debugging/fixing process and are not part of the standard workflow.

## Key Differences from 202x Template

1. **Unicode Support Added**
   - `\usepackage{CJKutf8}` in main .tex
   - CJK environments in keynotes.tex

2. **Custom Header Handling**
   - Modified `\includepaper` in ismirproc.cls
   - Uses `\thispagestyle{plain}` for paper pages

3. **6-Digit Paper Numbering**
   - Custom `4_split_proceedings_6digit.py` script
   - Outputs 000001.pdf instead of 001.pdf

4. **Comprehensive Front Matter**
   - Much more detailed than 202x
   - Includes special sessions, satellite events, awards

5. **Filter Pipeline**
   - `complete_filter_pipeline.py` for excluding papers
   - Handles TISMIR/MIREX removal

6. **Zenodo Resume Logic**
   - `resume_upload.py` for handling interrupted uploads

## Usage for Future Years

For ISMIR 2026+:

1. Copy this `2025_Proceedings_ISMIR/` folder
2. Rename to `202X_Proceedings_ISMIR/`
3. Update content in .tex files
4. Replace logos as needed
5. Follow README.md workflow

The scripts are generic and should work with minimal changes.

## Additional Resources

- Original working directory: `RESULT-2025-ismir-proceedings/`
- Conference archive repo: `conference-archive/` (for Zenodo uploads)
- Source content: `_source_contents/` (original materials provided)

---

**Prepared by:** Keunwoo Choi (Publication Chair)  
**Date:** November 2025

