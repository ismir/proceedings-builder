#!/usr/bin/env python3
"""
Prepare cmt-metadata.csv for ISMIR 2025 proceedings by merging
data from Programs CSV and Submissions CSV.
"""

import csv
import os
import re
from pathlib import Path

# File paths
programs_csv = "_source_contents/Programs (shared with session chairs) - 工作表1.csv"
submissions_csv = "_source_contents/Submissions ISMIR 2025.xlsx - Papers.csv"
detailed_csv = "_source_contents/ISMIR 2025 paper titles, authors, emails. - detailed_schedule_for_pdf.csv"
papers_dir = "_source_contents/papers"
output_csv = "RESULT-2025-ismir-proceedings/cmt-metadata.csv"

def extract_paper_id_from_filename(filename):
    """Extract paper ID from filename like paper_0286.pdf -> 286"""
    match = re.search(r'paper_(\d+)', filename)
    if match:
        return int(match.group(1))
    return None

def get_paper_ids_from_directory():
    """Get all paper IDs from the papers directory"""
    paper_files = {}
    papers_path = Path(papers_dir)
    
    for pdf_file in papers_path.glob("paper_*.pdf"):
        # Skip old versions
        if "old" in pdf_file.name.lower():
            continue
        paper_id = extract_paper_id_from_filename(pdf_file.name)
        if paper_id:
            paper_files[paper_id] = pdf_file.name
    
    return paper_files

def parse_presentation_id(pres_id):
    """Parse presentation ID like '1-01' into session and position"""
    parts = pres_id.split('-')
    if len(parts) == 2:
        session_num = parts[0]
        position = parts[1]
        return f"Session {session_num}", int(position)
    return None, None

def split_authors_to_components(author_string):
    """
    Split author string into AuthorDetails, AuthorNames, and AuthorEmails
    Input: "Author Name (Affiliation)*; Author2 (Affiliation2)"
    """
    if not author_string:
        return "", "", ""
    
    authors = [a.strip() for a in author_string.split(';')]
    
    author_details = []
    author_names = []
    author_emails = []
    
    for author in authors:
        # Parse "Name (Affiliation)*" format
        is_primary = '*' in author
        author = author.replace('*', '').strip()
        
        # Extract name and affiliation
        match = re.match(r'([^(]+)\(([^)]+)\)', author)
        if match:
            name = match.group(1).strip()
            affiliation = match.group(2).strip()
            
            # Convert "First Last" to "Last, First" format for AuthorNames
            name_parts = name.split()
            if len(name_parts) >= 2:
                last_name = name_parts[-1]
                first_names = ' '.join(name_parts[:-1])
                formal_name = f"{last_name}, {first_names}"
            else:
                formal_name = name
            
            if is_primary:
                formal_name += "*"
                author_details.append(f"{name} ({affiliation})*")
            else:
                author_details.append(f"{name} ({affiliation})")
            
            author_names.append(formal_name)
        else:
            # Fallback if parsing fails
            author_names.append(author)
            author_details.append(author)
    
    return '; '.join(author_details), '; '.join(author_names), ""

def main():
    # Read programs CSV
    print("Reading Programs CSV...")
    programs_data = {}
    with open(programs_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Presentation #']:
                programs_data[row['Presentation #']] = row
    
    # Read submissions CSV to get abstracts and metadata
    print("Reading Submissions CSV...")
    submissions_data = {}
    with open(submissions_csv, 'r', encoding='utf-8') as f:
        # Skip the first empty row
        lines = f.readlines()
        if lines:
            # Use the second line as header
            reader = csv.DictReader(lines[1:])
            for row in reader:
                if row.get('Paper ID'):
                    try:
                        paper_id = int(row['Paper ID'])
                        submissions_data[paper_id] = row
                    except (ValueError, KeyError):
                        continue
    
    # Read detailed schedule CSV for paper ID mapping
    print("Reading Detailed Schedule CSV...")
    detailed_data = {}
    with open(detailed_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Get the presentation ID - could be in '#' or in 'session' column
            pres_id = row.get('#', '').strip()
            if not pres_id:
                # Try session column for rows where session contains the ID
                session_val = row.get('session', '').strip()
                if session_val and '-' in session_val:
                    pres_id = session_val
            
            if pres_id and row.get('Paper ID'):
                detailed_data[pres_id] = row
    
    # Get available paper files
    print("Scanning paper directory...")
    paper_files = get_paper_ids_from_directory()
    print(f"Found {len(paper_files)} paper files")
    
    # Create mapping from presentation ID to paper ID
    print("Creating presentation ID to paper ID mapping...")
    pres_to_paper = {}
    
    # Map based on matching titles between programs and detailed schedule
    for pres_id, prog_row in programs_data.items():
        prog_title = prog_row['Title'].strip()
        
        # Find matching entry in detailed schedule
        for detail_pres_id, detail_row in detailed_data.items():
            detail_title = detail_row.get('Paper Title', '').strip()
            if prog_title == detail_title:
                paper_id = detail_row.get('Paper ID')
                if paper_id:
                    try:
                        pres_to_paper[pres_id] = int(paper_id)
                        break
                    except ValueError:
                        continue
    
    print(f"Mapped {len(pres_to_paper)} presentations to paper IDs")
    
    # Generate output CSV
    print("Generating cmt-metadata.csv...")
    output_rows = []
    
    for pres_id in sorted(programs_data.keys()):
        prog_row = programs_data[pres_id]
        
        # Skip if no paper ID mapping
        if pres_id not in pres_to_paper:
            print(f"Warning: No paper ID mapping for {pres_id}: {prog_row['Title']}")
            continue
        
        paper_id = pres_to_paper[pres_id]
        
        # Skip if paper file doesn't exist
        if paper_id not in paper_files:
            print(f"Warning: No PDF file for paper {paper_id}: {prog_row['Title']}")
            continue
        
        # Get submission data if available
        sub_row = submissions_data.get(paper_id, {})
        
        # Parse session and position
        session_name, position = parse_presentation_id(pres_id)
        session_id = f"{session_name}:{position}" if session_name and position else pres_id
        
        # Split authors into components
        author_details, author_names, author_emails = split_authors_to_components(prog_row['Author'])
        
        # Get abstract from submissions
        abstract = sub_row.get('Abstract', '')
        
        # Get subject areas from submissions or use Track
        primary_subject = sub_row.get('Primary Subject Area', prog_row.get('Track', 'ISMIR'))
        secondary_subjects = sub_row.get('Secondary Subject Areas', '')
        
        # Get one-liner (main message)
        one_liner = sub_row.get('Q1 (Main message)', '')
        
        # Get author emails from submissions if available
        if sub_row.get('Author Emails'):
            author_emails = sub_row['Author Emails']
        
        output_row = {
            'PaperID': paper_id,
            'Title': prog_row['Title'],
            'Abstract': abstract,
            'AuthorDetails': author_details,
            'AuthorNames': author_names,
            'AuthorEmails': author_emails,
            'PrimarySubjectArea': primary_subject,
            'SecondarySubjectAreas': secondary_subjects,
            'OneLiner': one_liner,
            'SessionID': session_id
        }
        
        output_rows.append(output_row)
    
    # Write output CSV
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['PaperID', 'Title', 'Abstract', 'AuthorDetails', 'AuthorNames', 
                      'AuthorEmails', 'PrimarySubjectArea', 'SecondarySubjectAreas', 
                      'OneLiner', 'SessionID']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)
    
    print(f"\nGenerated {len(output_rows)} entries in {output_csv}")
    
    # Print session summary
    session_counts = {}
    for row in output_rows:
        session = row['SessionID'].split(':')[0]
        session_counts[session] = session_counts.get(session, 0) + 1
    
    print("\nSession summary:")
    for session in sorted(session_counts.keys()):
        print(f"  {session}: {session_counts[session]} papers")

if __name__ == '__main__':
    main()

