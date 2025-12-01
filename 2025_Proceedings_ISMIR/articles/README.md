# Articles Folder

This folder should contain the camera-ready paper PDFs for ISMIR 202X.

## File Naming Convention

Papers should be named as `paper_XXXX.pdf` where `XXXX` is the paper ID from CMT/OpenReview.

Example:
```
articles/
├── paper_004.pdf
├── paper_007.pdf
├── paper_010.pdf
└── ...
```

## Preparation

Before running the build process, ensure all accepted papers are placed in this folder with the correct naming format.

The papers will be automatically organized into the proper directory structure (`PaperID/CameraReady/`) by the `1_generate_metadata_json.py` script.

See the main README.md for complete instructions.
