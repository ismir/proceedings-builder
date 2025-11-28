#!/usr/bin/env python3
"""
Complete pipeline to filter out TISMIR and MIREX papers from ISMIR 2025 Proceedings.
This script filters the metadata CSV and regenerates all dependent files.
"""

import csv
import json
from pathlib import Path
import shutil

# TISMIR and MIREX paper IDs to exclude (identified from presentation positions)
EXCLUDE_PAPER_IDS = {
    383, 379,  # Session 1, positions 15-16
    386, 385,  # Session 2, positions 15-16
    382, 381,  # Session 3, positions 15-16
    384, 424,  # Session 5, positions 15-16
    380,       # Session 6, position 15
    391, 410   # Session 7, positions 15-16
}

def filter_cmt_metadata(input_csv, output_csv):
    """Filter cmt-metadata.csv to remove TISMIR/MIREX papers"""
    print("Step 1: Filtering cmt-metadata.csv...")
    
    rows_kept = []
    rows_removed = []
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        for row in reader:
            paper_id = int(row['PaperID'])
            if paper_id in EXCLUDE_PAPER_IDS:
                rows_removed.append(row)
                print(f"  ✗ Removing Paper {paper_id}: {row['Title'][:60]}")
            else:
                rows_kept.append(row)
    
    # Write filtered CSV
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_kept)
    
    print(f"\n  Kept: {len(rows_kept)} papers")
    print(f"  Removed: {len(rows_removed)} papers")
    print(f"  Output: {output_csv}\n")
    
    return rows_kept, rows_removed


def filter_session_list(input_file, output_file, excluded_ids):
    """Filter session-list.txt to update paper counts per session"""
    print("Step 2: Updating session-list.txt...")
    
    # Count papers per session from filtered data
    session_counts = {}
    for row in excluded_ids:
        session_id = row['SessionID'].split(':')[0] if ':' in row['SessionID'] else 'Unknown'
        session_num = session_id.split()[-1] if 'Session' in session_id else session_id
        session_counts[session_num] = session_counts.get(session_num, 0) + 1
    
    # Read and update session list
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    updated_lines = []
    for line in lines:
        # Lines are in format: "Session 1 16"
        parts = line.strip().split()
        if len(parts) == 3 and parts[0] == 'Session':
            session_num = parts[1]
            original_count = int(parts[2])
            removed_count = session_counts.get(session_num, 0)
            new_count = original_count - removed_count
            
            if removed_count > 0:
                print(f"  Session {session_num}: {original_count} → {new_count} papers (-{removed_count})")
            
            updated_lines.append(f"Session {session_num} {new_count}\n")
        else:
            updated_lines.append(line)
    
    with open(output_file, 'w') as f:
        f.writelines(updated_lines)
    
    print(f"  Output: {output_file}\n")


def clean_camera_ready_dirs(camera_ready_base, excluded_ids):
    """Remove camera-ready directories for excluded papers"""
    print("Step 3: Cleaning camera_ready directories...")
    
    removed_count = 0
    for paper_id in excluded_ids:
        paper_dir = camera_ready_base / str(paper_id)
        if paper_dir.exists():
            shutil.rmtree(paper_dir)
            print(f"  ✗ Removed camera_ready/{paper_id}/")
            removed_count += 1
    
    print(f"  Removed {removed_count} directories\n")


def main():
    print("="*70)
    print("ISMIR 2025 Proceedings - TISMIR/MIREX Filter Pipeline")
    print("="*70)
    print(f"\nExcluding {len(EXCLUDE_PAPER_IDS)} papers: {sorted(EXCLUDE_PAPER_IDS)}\n")
    
    base_dir = Path(__file__).parent
    result_dir = base_dir / "RESULT-2025-ismir-proceedings"
    
    # Step 1: Filter cmt-metadata.csv
    input_csv = result_dir / "cmt-metadata.csv"
    output_csv = result_dir / "cmt-metadata-filtered.csv"
    
    rows_kept, rows_removed = filter_cmt_metadata(input_csv, output_csv)
    
    # Backup original and replace with filtered
    backup_csv = result_dir / "cmt-metadata-original.csv"
    if not backup_csv.exists():
        shutil.copy(input_csv, backup_csv)
        print(f"  Backed up original to: {backup_csv}")
    
    shutil.copy(output_csv, input_csv)
    print(f"  Replaced {input_csv} with filtered version\n")
    
    # Step 2: Update session-list.txt
    session_list = result_dir / "session-list.txt"
    filter_session_list(session_list, session_list, rows_removed)
    
    # Step 3: Clean camera_ready directories
    camera_ready_base = result_dir / "camera_ready"
    clean_camera_ready_dirs(camera_ready_base, EXCLUDE_PAPER_IDS)
    
    # Clean up old generated files to force regeneration
    print("Step 4: Cleaning old generated files...")
    files_to_remove = [
        "paper-metadata.json",
        "session-order.json",
        "papers.tex",
        "2025_Proceedings_ISMIR.pdf",
        "2025_Proceedings_ISMIR.aux",
        "2025_Proceedings_ISMIR.ain",
        "2025_Proceedings_ISMIR.log",
        "2025_Proceedings_ISMIR.out",
        "2025_Proceedings_ISMIR.toc"
    ]
    
    for filename in files_to_remove:
        filepath = result_dir / filename
        if filepath.exists():
            filepath.unlink()
            print(f"  ✗ Removed {filename}")
    
    # Remove split_articles if it exists
    split_dir = result_dir / "split_articles"
    if split_dir.exists():
        shutil.rmtree(split_dir)
        print(f"  ✗ Removed split_articles/")
    
    # Remove articles dir to force regeneration
    articles_dir = result_dir / "articles"
    if articles_dir.exists():
        shutil.rmtree(articles_dir)
        print(f"  ✗ Removed articles/")
    
    print("\n" + "="*70)
    print("✅ Filtering Complete!")
    print("="*70)
    print(f"\nFiltered proceedings will have {len(rows_kept)} papers")
    print(f"\nNext steps:")
    print("  1. cd RESULT-2025-ismir-proceedings")
    print("  2. python3 scripts/1_generate_metadata_json.py cmt-metadata.csv camera_ready session-list.txt -o paper-metadata.json -s session-order.json -d articles --year 2025")
    print("  3. python3 scripts/2_generate_paper_tex.py paper-metadata.json session-order.json -o papers.tex")
    print("  4. bash 00-run.sh")
    print("  5. python3 scripts/4_split_proceedings.py 2025_Proceedings_ISMIR.pdf paper-metadata.json session-order.json -s 23 -o split_articles -j paper-metadata-split.json")
    print("  6. python3 scripts/6_generate_final_outputs.py")
    print()


if __name__ == "__main__":
    main()

