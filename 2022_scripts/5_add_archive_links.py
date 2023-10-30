import csv
import json
import copy
import re
import os
import PyPDF2

input_json = "../2022_Proceedings_ISMIR/2021_Proceedings_Info_final.json"
archive_json = "../2022_Proceedings_ISMIR/archive_split/2022.json"
output_json = "../2022_Proceedings_ISMIR/2022_Proceedings_Info_final_archivelinks.json"


with open(input_json, encoding='utf-8') as fp:
    papers = json.load(fp)

with open(archive_json, encoding='utf-8') as fp:
    archive = json.load(fp)

papers_updated = []


for paper in papers:
    url = [x["ee"] for x in archive if x["extra"]["submission_id"] == paper["extra"]["submission_id"]][0]
    print(url)
    paper.update({"ee": url})
    papers_updated.append(paper)

with open(output_json, 'w', encoding='utf-8') as json_out:
    json.dump(papers_updated, json_out, ensure_ascii=False, indent=4)
