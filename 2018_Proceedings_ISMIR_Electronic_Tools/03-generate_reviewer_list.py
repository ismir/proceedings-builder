#!/usr/bin/python

import jinja2
import codecs
import os

with codecs.open('data/reviewers.txt', 'r', 'utf-8') as f:
    reviewers = [line.rstrip('\n') for line in f]

context = {'reviewers': reviewers}

#print reviewers[85]

# get jinja template
PATH = os.path.dirname(os.path.abspath(__file__))
template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(PATH, 'templates')))
template = template_env.get_template('reviewer_list.html')
print(len(reviewers))
with open('output/html_overview_table/reviewer_list.html', 'wb') as f:
    html = template.render(context)
    f.write(html.encode('utf-8'))
