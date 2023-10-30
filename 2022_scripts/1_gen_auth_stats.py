import csv
import json
import copy
import re
import os
import PyPDF2


include_emails = True
include_affiliations = True
# Paper ID,Session ID,Paper Title,Abstract,Primary Contact Author Name,Primary Contact Author Email,Author Details,Author Names,Author Emails,Primary Subject Area,Secondary Subject Areas,Status,Camera Ready Submitted?,Special Session,One Liner,Student Paper,Registered?,Check,Comments,Time zone,New session match score
#input_csv = "../2021_Proceedings_ISMIR/2021_Proceedings_Info_final.csv"
input_csv = "../data2022/2022-cmt-metadata.csv"

key_template = {
    "title": None,
    "author": [],
    "year": "2022",
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




with open(input_csv, newline='', encoding='utf-8-sig') as csv_in:
    reader = csv.DictReader(csv_in)
    proc_dict_list = []
    authorList = []
    for line in reader:
        paper_dict = process_line(line)
        # paper_dict = copy.deepcopy(key_template)
        # authors = row[7].replace("*","").split(";")
        # for index in range(len(authors)):
        #     authors[index] = authors[index].rstrip().lstrip().title()
        #     authors[index] = " ".join(authors[index].split(',')[::-1]).rstrip().lstrip()
        # if include_emails:
        #     author_emails = row[8].replace("*", "").split(";")
        #     author_email_dict = {}
        #     for index in range(len(author_emails)):
        #         author_emails[index] = author_emails[index].rstrip().lstrip()
        #         author_email_dict.update({authors[index]: author_emails[index]})
        # if include_affiliations:
        #     author_detailed_info = row[6].replace("*","").split(";")
        #     affiliation_dict = {}
        #     for index in range(len(author_detailed_info)):
        #         try:
        #             affiliation = re.search("\((.*)\)", author_detailed_info[index]).group(1).rstrip().lstrip()
        #         except:
        #             affiliation = "None"
        #         affiliation_dict.update({authors[index]: affiliation})
        proc_dict_list.extend([paper_dict])
        authorList.extend(paper_dict["extra"]["email"])

nAuth = len(authorList)
nUniqueAuth = len(list(set(authorList)))

print(nAuth, nUniqueAuth, nAuth/float(len(proc_dict_list)), nUniqueAuth/float(len(proc_dict_list)))


