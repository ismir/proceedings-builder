import argparse
import json
import os
import codecs

import jinja2

# We make a custom jinja environment with different keyword strings so that we can write
# mostly normal tex in the template
latex_jinja_env = jinja2.Environment(
    block_start_string=r'\BLOCK{',
    block_end_string='}',
    variable_start_string=r'\VAR{',
    variable_end_string='}',
    comment_start_string=r'\#{',
    comment_end_string='}',
    line_statement_prefix='%-',
    line_comment_prefix='%#',
    trim_blocks=True,
    autoescape=False,
    loader=jinja2.FileSystemLoader(os.path.abspath(os.path.dirname(__file__)))
)


def latex_escape(string):
    return string.replace('#', r'\#').replace('_', r'\_').replace('$', r'\$').replace('&', r'\&').replace('%', r'\%')


def build_section(section, order, papers):
    paper_list = []
    for p in section["papers"]:
        p = str(p)
        paper = papers[p]
        paper_list.append({
            "title": latex_escape(paper["title"]),
            "authors": ", ".join(paper["author"]),
            "file": "articles/{}".format(paper["extra"]["file"])
        })

    return {
        "name": section["name"],
        "titlepage": order,
        "papers": paper_list,
    }


def main(jsonfile, orderfile, outputfile):
    with open(jsonfile) as fp:
        data = json.load(fp)
        papers = {}
        for d in data:
            papers[str(d["extra"]["submission_id"])] = d

    with open(orderfile) as fp:
        paper_order = json.load(fp)

    sections_context = []
    for i, section in enumerate(paper_order, 1):
        sections_context.append(build_section(section, i, papers))

    template = latex_jinja_env.get_template('templates/papers.tex')

    try:
        with codecs.open(outputfile, "w", "utf-8") as fp:
            fp.write(template.render(sections=sections_context))
            print(f'Output successfully written to {outputfile}.')
    except jinja2.exceptions.TemplateSyntaxError as e:
        print("Error at line {}".format(e.lineno))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Read ")
    parser.add_argument("json", help="path to json file containing paper metadata")
    parser.add_argument("order", help="JSON file describing sections and paper order")
    parser.add_argument("-o", help="output filename to write papers.tex to")

    args = parser.parse_args()
    main(args.json, args.order, args.o)
