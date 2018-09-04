#!/usr/bin/python

import codecs
import csv
import jinja2
import os
from ismir_utils import unicode_tsv_reader, search_pages_total, makeDirs


# open pages_total as look-up table
pages_total = 'data/pages_total.txt'
pt_reader = unicode_tsv_reader(pages_total)
next(pt_reader) # skip the headers
    
# store it all in a list
pages_total = list(pt_reader)

sessions = []
pdf_offset = 28

# open session index file
session_index = 'data/session_index.txt'
si_reader = unicode_tsv_reader(session_index)
next(si_reader) # skip the headers

# iterate over sessions
for session_name, start_page, header_name in si_reader:
    print(session_name, start_page)

    current_paper_start = int(start_page)
    
    # open session file
    current_session = 'data/' + session_name + '.txt' #define session_name.csv as the current_session
    s_reader = unicode_tsv_reader(current_session)
    next(s_reader) # skip the headers
    
    # iterate over session entries
    publications = []
    for paper_title, authors, pdf_filename in s_reader:
        current_paper = pdf_filename
        current_paper_length = search_pages_total(current_paper, pages_total)
        current_paper_end = current_paper_start+current_paper_length-1
        publications.append({'title': paper_title,
                             'authors': authors,
                             'paper_startpage': current_paper_start-pdf_offset,
                             'paper_endpage': current_paper_end-pdf_offset,
                             'pdf': pdf_filename})
        current_paper_start = current_paper_end + 1

    sessions.append({'title': header_name,
                     'publications': publications})

context = {
        'sessions': sessions
    }

# get jinja template
PATH = os.path.dirname(os.path.abspath(__file__))
template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(PATH, 'templates')))
template = template_env.get_template('overview_table.html')

makeDirs('output/html_overview_table')

with open('output/html_overview_table/index.html', 'wb') as f:
    html = template.render(context)
    f.write(html.encode('utf-8'))

template = template_env.get_template('overview_table.html')
with open('output/overview_table.html', 'wb') as f:
    html = template.render(context)
    f.write(html.encode('utf-8'))

template = template_env.get_template('dblp.txt')
with open('output/publications_ISMIR2018.txt', 'wb') as f:
    html = template.render(context)
    f.write(html.encode('utf-8'))
