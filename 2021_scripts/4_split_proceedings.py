#!/usr/bin/python
import argparse
import json
import os

import PyPDF2


def main(proceedings_filename, start_page, metadata, session_order_name, output_folder, output_json):
    # open proceedings
    proceedings_pdf = PyPDF2.PdfFileReader(open(proceedings_filename, 'rb'))

    with open(session_order_name) as fp:
        session_order = json.load(fp)

    with open(metadata) as fp:
        paper_data = json.load(fp)
        all_papers = {}
        for d in paper_data:
            all_papers[str(d["extra"]["submission_id"])] = d

    os.makedirs(output_folder, exist_ok=True)

    paper_count = 1
    out_papers = []

    for session in session_order:
        session_name = session["name"]

        print("Session name: {}, Starting Page: {}".format(session_name, start_page))

        # skip the session title page and the blank page after it
        current_paper_start = start_page + 2

        for paper_id in session["papers"]:
            curr_paper = all_papers[str(paper_id)]
            current_paper_length = curr_paper["extra"]["num_pages"]

            print("  Current paper being processed: " + str(paper_id))

            current_paper_end = current_paper_start + current_paper_length - 1
            print("    Start page: {}".format(current_paper_start))
            print("    End page: {}".format(current_paper_end))

            output = PyPDF2.PdfFileWriter()
            for p in range(current_paper_start - 1, current_paper_end):
                # print(p)
                output.addPage(proceedings_pdf.getPage(p))

            out_filename = "{:0>6}.pdf".format(paper_count)
            print(f"    Output name {out_filename}")
            with open(os.path.join(output_folder, out_filename), 'wb') as f:
                output.write(f)
            paper_count += 1

            current_paper_start = current_paper_end + 1
            curr_paper["extra"]["split_file"] = out_filename
            out_papers.append(curr_paper)

        # The session title page is always on the right-hand side of the book (odd page number)
        # so if the last page of the last paper was odd, a blank page is inserted before the header
        # we already added 1 onto the start, so if even we add another one
        if current_paper_start % 2 == 0:
            print("Adding blank page between sections")
            start_page = current_paper_start + 1
        else:
            start_page = current_paper_start

    with open(output_json, "w", encoding='utf-8') as fp:
        json.dump(out_papers, fp, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("proceedings", help="The complete proceedings document")
    parser.add_argument("metadata", help="JSON containing metadata generated from CSV")
    parser.add_argument("order", help="JSON file describing sections and paper order")
    parser.add_argument("-s", type=int, required=True, help="The starting page in the pdf file that the first section starts at")
    parser.add_argument("-o", required=True, help="output directory to write split files to")
    parser.add_argument("-j", required=True, help="output")

    args = parser.parse_args()
    main(args.proceedings, args.s, args.metadata, args.order, args.o, args.j)