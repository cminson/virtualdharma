#!/usr/local/bin/python
#
# Run locally on Mac to check PDF correctness
#
import json
import os

PATH_NEW_TRANSCRIPTS = "/Users/Chris/Documents/PDF"
LIST_CORRECT_PDFS = []


fd = open('CONFIG00.JSON','r')
data  = json.load(fd)

talks = data['talks']
for talk in talks:
    url = talk['url']
    mp3_name = url.split("/")[-1]
    correct_pdf_name = mp3_name.replace(".mp3", ".pdf")
    LIST_CORRECT_PDFS.append(correct_pdf_name)


for pdf_name in os.listdir(PATH_NEW_TRANSCRIPTS):
    if ".pdf" not in pdf_name: continue
    if pdf_name in LIST_CORRECT_PDFS:
        print("CORRECT: {}".format(pdf_name))
    else:
        print("DOES NOT EXIST: {}".format(pdf_name))
        match_name = pdf_name[0:30]
        for correct_pdf_name in LIST_CORRECT_PDFS:
            if match_name in correct_pdf_name:
                print("mv {} {}".format(pdf_name, correct_pdf_name))
                break


