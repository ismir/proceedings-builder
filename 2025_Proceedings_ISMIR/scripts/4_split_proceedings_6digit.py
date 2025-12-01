#!/usr/bin/python
import argparse
import datetime
import json
import os
from pathlib import Path

import pypdf


def main(proceedings_path, start_page, metadata, session_order_name, output_folder, output_json, final_name):
    # open proceedings
    proceedings_pdf = pypdf.PdfReader(open(proceedings_path, 'rb'))

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

            output = pypdf.PdfWriter()
            for p in range(current_paper_start - 1, current_paper_end):
                # print(p)
                output.add_page(proceedings_pdf.pages[p])

            # MODIFIED: Use 6-digit format instead of 3-digit
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

    # Skip renaming the proceedings file to avoid issues
    # proceedings_path.rename(proceedings_path.parent / final_name)
    print(f"\nSplit complete! Created {paper_count-1} PDF files in {output_folder}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split the complete proceedings into separate PDFs per paper (6-digit format)")
    parser.add_argument("proceedings", help="The complete proceedings document", type=Path)
    parser.add_argument("metadata", help="JSON containing metadata generated from CSV")
    parser.add_argument("order", help="JSON file describing sections and paper order")
    parser.add_argument("-s", "--start_page", type=int, required=True, help="The starting page in the pdf file that the first section starts at")
    parser.add_argument("-o", "--output_dir", required=True, help="output directory to write split files to")
    parser.add_argument("-j", "--json", required=True, help="output JSON metadata file")
    parser.add_argument("--final_name", help="name of the final PDF proceedings", default=f"{datetime.date.today().year}_Proceedings_ISMIR.pdf")

    args = parser.parse_args()
    main(args.proceedings, args.start_page, args.metadata, args.order, args.output_dir, args.json, args.final_name)

