import argparse
import codecs
import csv
import json
import os
import re
import shutil
import unittest

import PyPDF2


def split_authors(author_list):
    """Authors from CMT are semicolon-separated Author (Affiliation)*; Author (Affiliation)
    The first author has a * after the affiliation, which appears to be corresponding author"""

    authors = author_list.split("; ")
    ret = []
    for a in authors:
        # replace '[space](institution)*'
        a = re.sub(r" \(.*\)\*?", "", a)
        ret.append(a)
    return ret


class SplitAuthorTest(unittest.TestCase):
    def test_split_authors(self):
        author_list = "Author name (institution)*; Second author (inst2)"
        ret = split_authors(author_list)
        self.assertEqual(ret, ["Author name", "Second author"])

        one_author = "Author name (institution)*"
        ret = split_authors(one_author)
        self.assertEqual(ret, ["Author name"])

        no_institution = "Author name ()*; Second author (inst2)"
        ret = split_authors(no_institution)
        self.assertEqual(ret, ["Author name", "Second author"])

        paren_in_inst = "Author name (National Institute of Advanced Industrial Science and Technology (AIST))"
        ret = split_authors(paren_in_inst)
        self.assertEqual(ret, ["Author name"])


def split_external_links(external_links):
    links = external_links.split(" ")
    links = [l for l in links if l]
    return links


def check_authors(authors):
    """Check the list of authors for words that are all uppercase or all lowercase"""
    ret = []
    for a in authors:
        new_a = []
        changed = False

        for name in a.split():
            if name.upper() == name:
                new_a.append(name.title())
                print("Name-part {} of {} is all upper-case".format(name, a))
                changed = True
            else:
                new_a.append(name)
        if changed:
            print("Changed {} to {}".format(a, " ".join(new_a)))
            ret.append(" ".join(new_a))
        else:
            ret.append(a)


def process_line(line):
    id = line["Paper ID"]
    title = line["Paper Title"]
    abstract = line["Abstract"]
    authors = line["Author Names"]
    emails = line["Author Emails"]
    primary_email = line["Primary Contact Author Email"]
    track = line["Track Name"]
    files = line["Files"]
    main_message = line["Q1 (Main message of the submission)"]
    external_links = line["Q2 (Additional material)"]
    student = line["Q3 (Student paper)"]

    # TODO: Normalise author names? (title case?) - 'nameparser' module
    authors = split_authors(authors)
    check_authors(authors)

    return {
        "paperid": id,
        "title": title,
        "abstract": abstract,
        "author": authors,
        "year": "2019",
        "track": track,
        "takeaway": main_message,
        "external_links": split_external_links(external_links),
        "student_paper": student
    }


def get_number_pages(pdf_filename):
    with open(pdf_filename, 'rb') as cur_pdf_fh:
        cur_pdf = PyPDF2.PdfFileReader(cur_pdf_fh)
        return cur_pdf.getNumPages()


def match_paper_to_file(paper, papersdir):
    # TODO: Cache this list?
    paperlist = os.listdir(papersdir)
    # TODO: The zip file returned by microsoft CMT has filenames of format "id\CameraReadySubmission\something.pdf".
    #  Not sure if this is incorrectly named folders on windows, or the actual filename.
    # To make tex happier, rename files and replace \ with -
    paperfiles = {p.split("\\")[0]: p for p in paperlist}
    paperid = paper["paperid"]
    if paperid not in paperfiles:
        raise Exception("Can't find paper id {}".format(paperid))
    paper["original_file"] = paperfiles[paperid]
    paper["file"] = "paper_{}.pdf".format(paperid)
    num_pages = get_number_pages(os.path.join(papersdir, paperfiles[paperid]))
    paper["num_pages"] = num_pages
    return paper


def main(csvfile, papersdir, outputfile, outputdir):
    if not os.path.exists(outputdir) or not os.path.isdir(outputdir):
        raise Exception("Output directory doesn't exist or isn't a directory")

    data = []
    # If you used excel to convert the data file to csv, it'll have a UTF-8 BOM at the beginning of the file
    # check if it's there:
    BUFSIZE = 1024
    with open(csvfile, "r+b") as fp:
        chunk = fp.read(BUFSIZE)
        if chunk.startswith(codecs.BOM_UTF8):
            encoding = "utf-8-sig"
        else:
            encoding = "utf-8"

    with open(csvfile, encoding=encoding, newline="") as fp:
        reader = csv.DictReader(fp)
        for line in reader:
            paper = process_line(line)
            # print("{}: {}".format(paper["paperid"], paper["title"]))
            paper = match_paper_to_file(paper, papersdir)
            data.append(paper)

    with open(outputfile, "w") as fp:
        json.dump(data, fp, indent=2)

    for d in data:
        shutil.copy(os.path.join(papersdir, d["original_file"]), os.path.join(outputdir, d["file"]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Read CSV file from Microsoft CMT and convert to ISMIR json")
    parser.add_argument("csv", help="path to csv file from Microsoft CMT paper platform")
    parser.add_argument("papers", help="directory containing papers downloaded from Microsoft CMT")
    parser.add_argument("-o", help="output filename to write json to")
    parser.add_argument("-d", help="directory to write pdfs to")

    args = parser.parse_args()
    main(args.csv, args.papers, args.o, args.d)
