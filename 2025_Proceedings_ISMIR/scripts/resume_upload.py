#!/usr/bin/env python3
"""
Resume Zenodo upload by identifying already-uploaded papers and skipping them.
"""
import json
import os
import sys
import requests

def get_uploaded_papers(token):
    """Get all ISMIR 2025 papers already uploaded to Zenodo."""
    resp = requests.get(
        'https://zenodo.org/api/deposit/depositions',
        params={'access_token': token, 'size': 200}
    )
    
    if resp.status_code != 200:
        print(f'Error listing deposits: {resp.status_code}')
        return {}
    
    deposits = resp.json()
    
    # Find ISMIR 2025 papers uploaded today
    uploaded_map = {}
    for d in deposits:
        created = d.get('created', '')
        if '2025-11-25' not in created:
            continue
            
        files = d.get('files', [])
        if not files:
            continue
            
        filename = files[0]['filename']
        title = d.get('metadata', {}).get('title', '')
        doi = d.get('doi', '')
        zid = d.get('id')
        
        # Check if it's an ISMIR 2025 paper (has proper metadata)
        if title and doi and filename.endswith('.pdf'):
            uploaded_map[filename] = {
                'zenodo_id': zid,
                'doi': doi,
                'title': title[:80]
            }
    
    return uploaded_map

def create_resume_json(input_json, uploaded_map, output_json):
    """Create a JSON with only papers that haven't been uploaded yet."""
    with open(input_json, 'r') as f:
        all_papers = json.load(f)
    
    remaining_papers = []
    already_uploaded = []
    
    for paper in all_papers:
        filename = paper['ee'].split('/')[-1]
        
        if filename in uploaded_map:
            # Already uploaded - update with Zenodo info
            paper_with_zenodo = paper.copy()
            paper_with_zenodo['zenodo_id'] = uploaded_map[filename]['zenodo_id']
            paper_with_zenodo['doi'] = uploaded_map[filename]['doi']
            paper_with_zenodo['url'] = f"https://doi.org/{uploaded_map[filename]['doi']}"
            paper_with_zenodo['ee'] = f"https://zenodo.org/record/{uploaded_map[filename]['zenodo_id']}/files/{filename}"
            already_uploaded.append(paper_with_zenodo)
            print(f'✓ Already uploaded: {filename} - {paper["title"][:60]}...')
        else:
            # Not yet uploaded
            remaining_papers.append(paper)
            print(f'⚠ Need to upload: {filename} - {paper["title"][:60]}...')
    
    # Save remaining papers for upload
    with open(output_json, 'w') as f:
        json.dump(remaining_papers, f, indent=2, ensure_ascii=False)
    
    # Save completed papers separately
    completed_json = output_json.replace('_remaining.json', '_completed.json')
    with open(completed_json, 'w') as f:
        json.dump(already_uploaded, f, indent=2, ensure_ascii=False)
    
    return len(already_uploaded), len(remaining_papers)

def main():
    token = os.environ.get('ZENODO_TOKEN_PROD')
    if not token:
        print('Error: ZENODO_TOKEN_PROD not set')
        sys.exit(1)
    
    input_json = 'ismir2025-proceedings-final/2025_clean.json'
    output_json = 'ismir2025-proceedings-final/2025_remaining.json'
    
    print('Step 1: Checking Zenodo for already-uploaded papers...')
    uploaded_map = get_uploaded_papers(token)
    print(f'\n✓ Found {len(uploaded_map)} already-uploaded ISMIR 2025 papers on Zenodo')
    
    print('\nStep 2: Creating filtered JSON...')
    completed, remaining = create_resume_json(input_json, uploaded_map, output_json)
    
    print(f'\n=== Summary ===')
    print(f'✓ Already uploaded: {completed} papers')
    print(f'⚠ Need to upload: {remaining} papers')
    print(f'\nNext step: Run upload with:')
    print(f'  cd conference-archive && \\')
    print(f'  export ZENODO_TOKEN_PROD="{token[:20]}..." && \\')
    print(f'  PYTHONPATH=$(pwd):$PYTHONPATH python scripts/upload_to_zenodo.py \\')
    print(f'    ../ismir2025-proceedings-final/2025_remaining.json \\')
    print(f'    database/conferences.json \\')
    print(f'    database/proceedings/2025.json \\')
    print(f'    --stage prod \\')
    print(f'    --num_cpus 1')

if __name__ == '__main__':
    main()

