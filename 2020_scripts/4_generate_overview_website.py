#!/usr/bin/python
import argparse
import codecs
import csv
import json

import jinja2
import os


def main(paperlist_name, session_order_name, start_page, output_dir):

    with open(session_order_name, encoding='utf-8') as fp:
        session_order = json.load(fp)

    with open(paperlist_name, encoding='utf-8') as fp:
        data = json.load(fp)
        papers = {}
        for d in data:
            papers[d["paperid"]] = d

    os.makedirs(output_dir, exist_ok=True)

    all_papers = []
    paper_count = 1

    sessions = []
    for session in session_order:
        session_name = session["name"]

        print("Session name: {}, Starting Page: {}".format(session_name, start_page))

        # skip the session title page and the blank page after it
        current_paper_start = start_page + 2

        publications = []
        session_count = 1
        for paper_id in session["papers"]:
            paper = papers[str(paper_id)]
            paper_title = paper["title"]
            authors = paper["author"]
            current_paper_length = paper["num_pages"]
            current_paper_end = current_paper_start + current_paper_length - 1

            url = f"https://program.ismir2020.net/static/final_papers/{paper_id}.pdf"
            # url = "http://archives.ismir.net/ismir{}/paper/{:0>6}.pdf".format(paper["year"], paper_count)
            paper_meta = {
                "title": paper_title,
                "author": authors,
                "year": paper["year"],
                "pages": "{}-{}".format(current_paper_start, current_paper_end),
                "abstract": paper["abstract"],
                "ee": url,
                "extra": {
                    "takeaway": paper["takeaway"],
                    "external_links": paper["external_links"]
                }
            }
            if session_name.startswith("Session"):
                session_letter = session_name.split()[1]
                session_position = "{}-{:0>2}".format(session_letter, session_count)
                session_count += 1
                paper_meta["extra"]["session_position"] = session_position
            elif session_name == "20th Anniversary Papers":
                paper_ids = session["paper_ids"]
                paper_meta["extra"]["session_position"] = paper_ids[str(paper_id)]

            publications.append({'title': paper_title,
                                 'authors': ", ".join(authors),
                                 'paper_startpage': current_paper_start,
                                 'paper_endpage': current_paper_end,
                                 'ee': url})
            all_papers.append(paper_meta)
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
    with open(os.path.join(output_dir, 'publications_ISMIR2020.txt'), 'wb') as f:
        html = template.render(context)
        f.write(html.encode('utf-8'))

    with open(os.path.join(output_dir, '2020.json'), 'w', encoding='utf-8') as fp:
        json.dump(all_papers, fp, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("paperlist", help="JSON containing metadata generated from CSV")
    parser.add_argument("order", help="JSON file describing sections and paper order")
    parser.add_argument("-o", required=True, help="output directory to write split files to")
    parser.add_argument("-s", type=int, required=True, help="Page that Section A starts in proceedings (pg number from page footer, not pdf number)")

    args = parser.parse_args()
    main(args.paperlist, args.order, args.s, args.o)
