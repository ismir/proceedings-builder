#!/usr/bin/env python3
import csv
from unidecode import unidecode


def format_reviewers(file_path, affiliation=True):
    with open(file_path) as f:
        csv_file = csv.DictReader(f)
        rows = [row for row in csv_file]
    reviewers = []
    for row in sorted(rows, key=lambda d: unidecode(d['Last Name']).upper()):
        if int(row['Completed']) > 0:
            first = row['First Name'].strip()
            middle = ' '.join([i if len(i) > 1 else f'{i}.' for i in row['Middle Initial (optional)'].strip().split()])
            last = row['Last Name'].strip()
            org = row['Organization'].strip().replace('&', r'\&') if affiliation else ''
            reviewers.append('{}{} {}{}\\\\\n'.format(first, f' {middle}' if middle else '', last, f', {org}' if org else ''))
    return reviewers


def write_committee_tex(output_path, metareviewers_path, reviewers_path):
    with open(output_path, 'w') as f:
        f.writelines([
            r'\section*{Program Committee}', '\n\n',
            r'\subsection*{Meta-Reviewers}', '\n\n',
            r'\begin{reviewers}', '\n',
            *format_reviewers(metareviewers_path, affiliation=True),
            r'\end{reviewers}', '\n\n\n',
            r'\subsection*{Reviewers}', '\n\n',
            r'\begin{multicols}{3}', '\n',
            r'\begin{reviewers}', '\n',
            *format_reviewers(reviewers_path, affiliation=False),
            r'\end{reviewers}', '\n',
            r'\end{multicols}', '\n',
        ])


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Create committee.tex file', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('output_path', help='Path to output tex file')
    parser.add_argument('--metareviewers_path', help='Path to txt file exported from CMT3 containing meta reviewers', default='../202x_Proceedings/MetaReviewers-1.txt')
    parser.add_argument('--reviewers_path', help='Path to txt file exported from CMT3 containing reviewers', default='../202x_Proceedings/Reviewers-1.txt')

    args = parser.parse_args()
    write_committee_tex(args.output_path, args.metareviewers_path, args.reviewers_path)
