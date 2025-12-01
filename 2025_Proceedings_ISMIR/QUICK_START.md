# Quick Start Guide - ISMIR 2025 Proceedings

If you just want to rebuild the ISMIR 2025 proceedings or adapt it for a future year, follow this quick guide.

## Prerequisites

```bash
# 1. Install Python dependencies
uv venv
source .venv/bin/activate
uv pip install pypdf pdfrw titlecase unidecode

# 2. Ensure you have LaTeX with CJK support
# (Most modern LaTeX distributions include this)
```

## Quick Build (If You Already Have Everything)

```bash
# Just run the build script
./00-run.sh
```

This will:
- Compile the LaTeX document (3 passes)
- Generate the author index
- Final compilation
- Output: `2025_Proceedings_ISMIR.pdf`

## Full Workflow (From Scratch)

### Step 1: Prepare Your Papers

Put camera-ready papers in `articles/` folder:
```
articles/
├── paper_004.pdf
├── paper_007.pdf
├── paper_010.pdf
└── ...
```

### Step 2: Prepare Metadata

Create your metadata CSV by merging sources:
```bash
python scripts/prepare_metadata.py \
  --submissions "path/to/CMT_Papers.csv" \
  --schedule "path/to/Programs.csv" \
  --mapping "path/to/detailed_schedule.csv" \
  --output "cmt-metadata.csv"
```

### Step 3: Generate LaTeX Files

```bash
cd scripts
python 1_generate_metadata_json.py
python 2_generate_paper_tex.py
python 3_generate_committee_tex.py
cd ..
```

### Step 4: Compile

```bash
./00-run.sh
```

### Step 5: Split into Individual Papers

```bash
python scripts/4_split_proceedings_6digit.py \
  --start_page 35 \
  -o ./split_articles_6digit \
  -j ./paper-metadata-split-6digit.json \
  2025_Proceedings_ISMIR.pdf \
  paper-metadata.json \
  session-order.json
```

**Note:** Find the correct start page by opening the PDF and looking for where the first session header appears.

### Step 6: Generate Archival Files

```bash
python scripts/6_generate_final_outputs.py \
  -o ./archival_outputs \
  --start_page 35 \
  paper-metadata-split-6digit.json \
  session-order.json
```

This creates:
- `2025.json` (for conference archive)
- `2025_dblp.xml` (for DBLP)
- `overview.csv` (for MiniConf)

## Common Issues

### LaTeX Errors

**Problem:** Unicode character errors  
**Solution:** Wrap non-ASCII text in `\begin{CJK}{UTF8}{mj}...\end{CJK}`

**Problem:** Header height warning  
**Solution:** Already fixed in `ismirproc.cls`

### Python Errors

**Problem:** `ModuleNotFoundError`  
**Solution:** Activate venv: `source .venv/bin/activate`

**Problem:** `Can't find pdf for paper id XXX`  
**Solution:** Ensure papers are named `paper_XXXX.pdf` in `articles/` folder

### PDF Issues

**Problem:** Papers have double headers  
**Solution:** Already fixed - we use `\thispagestyle{plain}` for paper pages

**Problem:** Wrong page numbers in split PDFs  
**Solution:** Adjust `--start_page` parameter to match where papers actually start

## Output Files

After a successful build:

```
2025_Proceedings_ISMIR/
├── 2025_Proceedings_ISMIR.pdf       # Main proceedings
├── split_articles_6digit/
│   ├── 000001.pdf                   # Individual papers
│   ├── 000002.pdf
│   └── ...
└── archival_outputs/
    ├── 2025.json                    # Metadata
    ├── 2025_dblp.xml                # DBLP submission
    └── overview.csv                 # MiniConf data
```

## Need More Details?

- **Full documentation:** See `README.md`
- **Migration notes:** See `MIGRATION_NOTES.md`
- **Script usage:** Each script has `--help` option

## Adapting for Future Years

1. Copy this entire folder
2. Update year in filenames and content
3. Replace logos in `logos/` folder
4. Update `.tex` files with new committee/sponsors/awards
5. Follow the workflow above

That's it! 🎉

