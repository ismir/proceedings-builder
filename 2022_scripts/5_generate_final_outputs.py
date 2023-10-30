#!/usr/bin/python
import argparse
import codecs
import csv
import json
import shutil
import jinja2
import os
import copy


def main(paperlist_name, session_order_name, start_page, output_dir):

    with open(session_order_name, encoding='utf-8') as fp:
        session_order = json.load(fp)

    with open(paperlist_name, encoding='utf-8') as fp:
        data = json.load(fp)
        papers = {}
        for d in data:
            papers[str(d["extra"]["submission_id"])] = d

    os.makedirs(output_dir, exist_ok=True)

    all_papers = []
    internal_json = []
    paper_count = 1

    sessions = []
    for session in session_order:
        session_name = session["name"]

        print("Session name: {}, Starting Page: {}".format(session_name, start_page))

        # skip the session title page and the blank page after it
        current_paper_start = start_page + 2


        publications = []
        for paper_id in session["papers"]:
            paper = papers[str(paper_id)]
            paper["abstract"] = paper["abstract"].replace(" \n "," ").replace("\n","").replace("\"","")
            current_paper_length = paper["extra"]["num_pages"]
            current_paper_end = current_paper_start + current_paper_length - 1
            paper["pages"] = "{}-{}".format(current_paper_start, current_paper_end)

            url = "https://archives.ismir.net/ismir{}/paper/{}".format(paper["year"], paper["extra"]["split_file"])
            paper["ee"] = url
            internal_json.append(paper)
            paper_publication = copy.deepcopy(paper)
            paper_publication.pop("extra")
            publications.append(paper_publication)
            all_papers.append(paper_publication)
            current_paper_start = current_paper_end + 1
            paper_count += 1

        sessions.append({'title': session_name,
                         'publications': publications})

        # The session title page is always on the right-hand side of the book (odd page number)
        # so if the last page of the last paper was odd, a blank page is inserted before the header
        # we already added 1 onto the start, so if even we add another one
        if current_paper_start % 2 == 0:
            print("Adding blank page between sections")
            start_page = current_paper_start + 1
        else:
            start_page = current_paper_start

    context = {
            'sessions': sessions
        }

    # get jinja template
    PATH = os.path.dirname(os.path.abspath(__file__))
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(PATH, 'templates')))

    template = template_env.get_template('overview_table.html')
    with open(os.path.join(output_dir, 'overview_table.html'), 'wb') as f:
        html = template.render(context)
        f.write(html.encode('utf-8'))

    template = template_env.get_template('dblp.txt')
    with open(os.path.join(output_dir, 'publications_ISMIR2022.txt'), 'wb') as f:
        html = template.render(context)
        f.write(html.encode('utf-8'))

    with open(os.path.join(output_dir, '2022.json'), 'w', encoding='utf-8') as fp:
        json.dump(all_papers, fp, indent=4, ensure_ascii=False)

    with open(os.path.join(output_dir, '2022_internal.json'), 'w', encoding='utf-8') as fp:
        json.dump(internal_json, fp, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("paperlist", help="JSON containing metadata generated during proceedings split during Step-4, with updated PDF paths")
    parser.add_argument("order", help="JSON file describing sections and paper order")
    parser.add_argument("-o", required=True, help="output directory to write split files to")
    parser.add_argument("-s", type=int, required=True, help="Page that Section A starts in proceedings (pg number from page footer, not pdf number)")

    args = parser.parse_args()
    main(args.paperlist, args.order, args.s, args.o)

