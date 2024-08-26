import csv
import json
import copy
import re
from pathlib import Path
import pypdf
import argparse
import subprocess
import datetime
from titlecase_checker import get_csv_encoding, warnings


key_template = {
    "title": None,
    "author": [],
    "year": None,
    "doi": None,
    "url": None,
    "pages": None,
    "abstract": None,
    "zenodo_id": None,
    "dblp_key": None,
    "ee": None,
    "extra": {
      "email": {},
      "affiliation": {},
      "takeaway": None,
      "external_links": None,
      "submission_id": None,
      "session_id": None,
      "session_position": None,
    #   "special_call": None,
      "subject_area_primary": None,
      "subject_area_secondary": [],
      "num_pages": None,
      "file": None,
      "split_file": None,
      "original_file": None
    }
}


def process_authors(line):
    authors = line["AuthorNames"].replace("*","").split(";")
    for index in range(len(authors)):
        author = authors[index].strip().rsplit(',', 1)[::-1]
        author_components = author[0].split() + author[1:]
        author_components[1:-1] = [c if len(c) > 1 else f'{c}.' for c in author_components[1:-1]]
        authors[index] = " ".join(author_components)
        if not authors[index].istitle() and not (author_components[-1].startswith('Mc')
        or author_components[-1].startswith('de') or author_components[-1].startswith('van')):
            warnings.warn(f'Check capitalisation of "{authors[index]}" and correct if necessary')
    author_emails = line["AuthorEmails"].replace("*", "").split(";")
    author_email_dict = {}
    for index in range(len(author_emails)):
        author_emails[index] = author_emails[index].strip()
        author_email_dict.update({authors[index]: author_emails[index]})

    author_detailed_info = line["AuthorDetails"].replace("*","").split(";")
    affiliation_dict = {}
    for index in range(len(author_detailed_info)):
        try:
            affiliation = re.search(r"\((.*)\)", author_detailed_info[index]).group(1).strip()
        except AttributeError:
            affiliation = "None"
        affiliation_dict.update({authors[index]: affiliation})

    return authors, author_email_dict, affiliation_dict


def process_line(line, year):
    paper = copy.deepcopy(key_template)
    paper["title"] = line["Title"].strip()
    paper["year"] = str(year)
    paper["abstract"] = line["Abstract"].strip()
    authors, author_emails, author_affiliations = process_authors(line)
    paper["author"] = authors
    paper["extra"]["email"] = author_emails
    paper["extra"]["affiliation"] = author_affiliations
    # paper["extra"]["special_call"] = line["SpecialTrack"] == "Yes"
    paper["extra"]["takeaway"] = line["OneLiner"].strip()
    paper["extra"]["subject_area_primary"] = line["PrimarySubjectArea"]
    sub_secondary = line["SecondarySubjectAreas"].split(';')
    for index in range(len(sub_secondary)):
        sub_secondary[index] = sub_secondary[index].strip()
    paper["extra"]["subject_area_secondary"] = sub_secondary
    paper["extra"]["submission_id"]  = int(line["PaperID"])
    paper["extra"]["file"] = "paper_{:03d}.pdf".format(paper["extra"]["submission_id"])   
    paper["extra"]["session_id"] = line["SessionID"].split(":")[0]
    paper["extra"]["session_position"] = int(line["SessionID"].split(":")[1])
    return paper


def get_number_pages(pdf_filename):
    with open(pdf_filename, 'rb') as cur_pdf_fh:
        cur_pdf = pypdf.PdfReader(cur_pdf_fh)
        return len(cur_pdf.pages)


def process_paper(paper, papersdir):
    paper_id = paper["extra"]["submission_id"]
    try:
        pdf_path = next(papersdir.glob(f'{paper_id}/CameraReady/*.pdf'))
    except StopIteration:
        raise Exception(f"Can't find a pdf for paper id {paper_id}") from None
    paper["extra"]["num_pages"] = get_number_pages(pdf_path)
    paper["extra"]["original_file"] = str(pdf_path)

    return paper


def generate_session_dict(data, session_list):
    session_keys = list(set([x["extra"]["session_id"] for x in data]))
    # Ensure session lists match

    csv_sess_list = copy.deepcopy(session_keys)
    file_sess_list = copy.deepcopy(session_list)
    csv_sess_list.sort()
    file_sess_list.sort()
    
    assert file_sess_list == csv_sess_list
    json_out = []

    for sess in session_list:
        curr_papers = dict([(x["extra"]["session_position"], x["extra"]["submission_id"]) for x in data if x["extra"]["session_id"] == sess])
        json_out.append({"name": sess, "papers": [curr_papers[subid] for subid in sorted(curr_papers)]})
    return json_out


def main(csvfile, papersdir, sessions, outputfile, sessionfile, output_dir, year):
    paper_data = []
    # process .csv of paper data and match it to file locations on disk
    with open(csvfile, encoding=get_csv_encoding(csvfile)) as fp:
        reader = csv.DictReader(fp)
        for line in reader:
            paper = process_line(line, year)
            paper = process_paper(paper, papersdir)
            paper_data.append(paper)


    # Export processed metadata to json file
    with open(outputfile, "w", encoding='utf-8') as fp:
        json.dump(paper_data, fp, indent=4, ensure_ascii=False)

    # Generate and export session file
    session_list = []
    with open(sessions) as fp:
        session_list = [line.strip() for line in fp.readlines()]

    session_data = generate_session_dict(paper_data, session_list)

    with open(sessionfile, "w", encoding='utf-8') as fp:
        json.dump(session_data, fp, indent=4, ensure_ascii=False)

    # copy all papers to new directory
    output_dir.mkdir(parents=True, exist_ok=True)
    for d in paper_data:
        # flush to ensure paper title appears directly above gs output when redirecting
        # script output to log file
        print(f'{d["extra"]["submission_id"]} - {d["title"]}', flush=True)
        subprocess.run([
            'gs', '-dNOPAUSE', '-dBATCH', '-sDEVICE=pdfwrite',
            '-dPDFSETTINGS=/prepress', '-dEmbedAllFonts=true',
            f'-sOutputFile={output_dir / d["extra"]["file"]}',
            '-f', d["extra"]["original_file"]
        ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Read CSV file from Microsoft CMT and convert to ISMIR json")
    parser.add_argument("csv", help="path to csv file from Microsoft CMT paper platform")
    parser.add_argument("papers", help="directory containing papers downloaded from Microsoft CMT", type=Path)
    parser.add_argument("sessions", help="file with sessions listed in the order we add papers to proceedings")
    parser.add_argument("-o", "--metadata_path", help="output filename to write metadata json to")
    parser.add_argument("-s", "--sessions_path", help="output filename to write session json to")
    parser.add_argument("-d", "--output_dir", help="directory to write pdfs to", type=Path)
    parser.add_argument("--year", help="the year in which the conference takes place", type=int, default=datetime.date.today().year)

    args = parser.parse_args()
    main(args.csv, args.papers, args.sessions, args.metadata_path, args.sessions_path, args.output_dir, args.year)
