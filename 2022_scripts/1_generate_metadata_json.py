import csv
import json
import copy
import re
import os
import PyPDF2
import argparse
import codecs
import shutil

key_template = {
    "title": None,
    "author": [],
    "year": "2022",
    "doi": None,
    "url": None,
    "video_url": None,
    "poster_url": None,
    "thumbnail_url": None,
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
      "tzoffset": None,
      "special_call": None,
      "subject_area_primary": None,
      "subject_area_secondary": [],
      "num_pages": None,
      "file": None,
      "split_file": None,
      "original_file": None,
      "student_author": None,
      "virtual_presentation": None,
      "long_presentation": None,
    }
}


def process_authors(line):
    authors = line["AuthorNames"].replace("*","").split(";")
    for index in range(len(authors)):
        authors[index] = authors[index].rstrip().lstrip().title()
        authors[index] = " ".join(authors[index].split(',')[::-1]).rstrip().lstrip()
    author_emails = line["AuthorEmails"].replace("*", "").split(";")
    if author_emails[-1].rstrip().lstrip() == '':
        del author_emails[-1]
    author_email_dict = {}
    for index in range(len(author_emails)):
            author_emails[index] = author_emails[index].rstrip().lstrip()
            author_email_dict.update({authors[index]: author_emails[index]})

    author_detailed_info = line["AuthorDetails"].replace("*","").split(";")
    affiliation_dict = {}
    for index in range(len(author_detailed_info)):
        try:
            affiliation = re.search("\((.*)\)", author_detailed_info[index]).group(1).rstrip().lstrip()
        except:
            affiliation = "None"
        affiliation_dict.update({authors[index]: affiliation})

    return authors, author_email_dict, affiliation_dict


def process_line(line):
    paper = copy.deepcopy(key_template)
    paper["title"] = line["Title"]
    paper["abstract"] = line["Abstract"].replace(" \n "," ").replace("\n","").replace("\"","")
    authors, author_emails, author_affiliations = process_authors(line)
    paper["author"] = authors
    paper["extra"]["email"] = author_emails
    paper["extra"]["affiliation"] = author_affiliations
    paper["extra"]["special_call"] = line["SpecialTrack"] == "Yes"
    paper["extra"]["takeaway"] = line["OneLiner"]
    paper["extra"]["subject_area_primary"] = line["PrimarySubjectArea"]
    sub_secondary = line["SecondarySubjectAreas"].split(';')
    for index in range(len(sub_secondary)):
        sub_secondary[index] = sub_secondary[index].rstrip().lstrip()
    paper["extra"]["subject_area_secondary"] = sub_secondary
    paper["extra"]["submission_id"]  = int(line["PaperID"])
    paper["extra"]["paper_id"]  = line["SessionID"] + '_' + line["SessionPosition"]
    paper["extra"]["file"] = "paper_{:03d}.pdf".format(paper["extra"]["submission_id"])   
    paper["extra"]["session_id"] = line["SessionID"]
    paper["extra"]["session_position"] = int(line["SessionPosition"])
    paper["extra"]["student_author"] = line["StudentAuthor"] == "Yes"
    paper["extra"]["virtual_presentation"] = line["PaperPresentation"] == "Virtually"
    paper["extra"]["long_presentation"] = line["LongPresentation"] == "TRUE"
    return paper


def get_number_pages(pdf_filename):
    with open(pdf_filename, 'rb') as cur_pdf_fh:
        cur_pdf = PyPDF2.PdfFileReader(cur_pdf_fh)
        return cur_pdf.getNumPages()


def process_paper(paper, papersdir):
    paper_id = paper["extra"]["submission_id"]
    flist = []
    flist = os.listdir(papersdir)
    found = False
    for f in flist:
        if int(f.split("_")[0]) == paper_id:
            found = True
            break
    if not found:
        raise Exception(f"Can't find paper id {paper_id}, filename {f}")
    else:
        paper["extra"]["num_pages"] = get_number_pages(os.path.join(papersdir, f))
        paper["extra"]["original_file"] = f

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
        curr_papers = [x["extra"]["submission_id"] for x in data if x["extra"]["session_id"] == sess]
        json_out.append({"name": sess, "papers": curr_papers})
    return json_out


def main(csvfile, papersdir, sessions, outputfile, sessionfile, outputdir):
    os.makedirs(outputdir, exist_ok=True)
    if not os.path.exists(outputdir) or not os.path.isdir(outputdir):
        raise Exception("Output directory doesn't exist or isn't a directory")

    paper_data = []
    # If you used excel to convert the data file to csv, it'll have a UTF-8 BOM at the beginning of the file
    # check if it's there:
    BUFSIZE = 1024
    with open(csvfile, "r+b") as fp:
        chunk = fp.read(BUFSIZE)
        if chunk.startswith(codecs.BOM_UTF8):
            encoding = "utf-8-sig"
        else:
            encoding = "utf-8"

    # process .csv of paper data and match it to file locations on disk
    with open(csvfile, encoding=encoding, newline="") as fp:
        reader = csv.DictReader(fp)
        for line in reader:
            paper = process_line(line)
            paper = process_paper(paper, papersdir)
            paper_data.append(paper)


    # Export processed metadata to json file
    with open(outputfile, "w", encoding='utf-8') as fp:
        json.dump(paper_data, fp, indent=4, ensure_ascii=False)

    # Generate and export session file
    session_list = []
    with open(sessions) as fp:
        session_list_raw = fp.readlines()
    for sess in session_list_raw:
        session_list.append(sess.rstrip().lstrip().split('\t')[2]) ##to change with sess.rstrip().lstrip().split('\t')[0]


    session_data = generate_session_dict(paper_data, session_list)

    with open(sessionfile, "w", encoding='utf-8') as fp:
        json.dump(session_data, fp, indent=4, ensure_ascii=False)

    # copy all papers to new directory
    for d in paper_data:
        shutil.copy(os.path.join(papersdir, d["extra"]["original_file"]), os.path.join(outputdir, d["extra"]["file"]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Read CSV file from Microsoft CMT and convert to ISMIR json")
    parser.add_argument("-c","--csv", help="path to csv file from Microsoft CMT paper platform")
    parser.add_argument("-p","--papers", help="directory containing papers downloaded from Microsoft CMT")
    parser.add_argument("-s","--sessions", help="file with sessions listed in the order we add papers to proceedings")
    parser.add_argument("-o","--out_metadata", help="output filename to write metadata json to")
    parser.add_argument("-n","--out_sessions", help="output filename to write session json to")
    parser.add_argument("-d","--out_papers", help="directory to write pdfs to")

    args = parser.parse_args()
    main(args.csv, args.papers, args.sessions, args.out_metadata, args.out_sessions, args.out_papers)
