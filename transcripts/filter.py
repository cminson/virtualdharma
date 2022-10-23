#!/usr/bin/python3
#
# Filter.py
# Christopher Minson
#
# Translates raw whisper output to formatted error-corrected HTML and PDF
#
# Local directory structure:
#
#   CONFIG00.JSON //json list of all talks with attributes (from the app, or something similar)
#   ERROR_CORRECTIONS //list of known error words and their corrections
#   ./data    // directory where all data is kept
#       raw     // the raw output .txt files from Whisper       
#       text    // error-corrected text from raw
#       html    // formatted HTML output from text
#       pdf     // pdf output from html
#       template    // the HTML template
#       css         // style sheets for HTML
#
# INSTRUCTIONS:
#
#   Put the raw text output files from whisper into ./data/raw.
#   Execute ./filter.py
#
#   Cleaned text output will be in ./data/text 
#   HTML output will be in ./data/html
#   PDF output will be in ./data/pdf 
#

import os
import string
import json
import datetime
import pdfkit


PATH_JSON_CONFIG = "./CONFIG00.JSON"
PATH_ERROR_CORRECTIONS = "./ERROR_CORRECTIONS"
PATH_RAW = "./data/raw/"
#PATH_RAW = "./data/test/"
PATH_TEXT = "./data/text/"
PATH_HTML = "./data/html/"
PATH_PDF = "./data/pdf/"
PATH_TEMPLATE = "./data/template/template01.html"

# Preamble text to remove from beginning of talk
LIST_PREAMBLES = [
    "The following talk was given at the Insight Meditation Center",
    "Please visit our website at audiodarma",
    "Please visit our website at audiodharma",
    "audioderma.org"
]

NUMBER_LINES_IN_PARAGRAPH = 5   # number of lines in each paragraph.  arbitrary but works reasonably well.

#
# Load error-correction pairs
# Read in current talk attributes from app Config file
# Translate raw Whisper output to error-corrected text file, puts that into PATH_TEXT
# Translate PATH_TEXT files into HTML, stores into PATH_HTML
# Translate PATH_HTML files into PDF, stores into PATH_PDF
# 

#
# Load known errors+corrections into dict
#
DictErrorCorrections = {}
f = open(PATH_ERROR_CORRECTIONS,'r')
list_errors = f.readlines()
f.close()
print("ERROR CORRECTION LIST:")
for error in list_errors:
    (error, correction) = error.split(' ')
    error = error.strip()
    correction = correction.strip()
    DictErrorCorrections[error] = correction
    print(f"\t{error} -> {correction}")


#
# Read in current talk attributes from app Config file
# Do this to associate the speaker, date, duration with the mp3 file_name
#
TalkAttributes = {}
f = open(PATH_JSON_CONFIG,'r')
all_talks  = json.load(f)
f.close()
for talk in all_talks['talks']:
    url = talk['url']
    file_name = url.split('/')[-1]
    title = talk['title']
    speaker = talk['speaker']
    date = talk['date']
    (year, month, day) = date.split('.')

    month = month.lstrip("0")
    day = day.lstrip("0")

    year = int(year)
    month = int(month)
    day = int(day)

    d = datetime.datetime(year, month, day)
    date = d.strftime("%b %d, %Y")

    duration = talk['duration']
    #print(url, speaker, date, duration)
    TalkAttributes[file_name] = (title, speaker, date, duration) 


#
# Strip known errors and unnecessary preambles from Whisper output
# Store cleaned text files into PATH_TEXT
#
# Previous versions of whisper returned transcribed text in one blob, and the last
# version returns it line by line.  The code below assumes the later.
#
print("TRANSLATING TO TEXT")
talk_list_raw = os.listdir(PATH_RAW)
for talk in talk_list_raw:
    path_raw = PATH_RAW + talk
    f =  open(path_raw)
    lines = f.readlines()
    f.close()

    path_text = PATH_TEXT + talk
    f = open(path_text, 'w+')

    print("writing: ", path_text)
    for line in lines:

        delete_line = False
        for preamble in LIST_PREAMBLES:
            if preamble in line: 
                delete_line = True
                break
        if delete_line: 
            continue

        for error in DictErrorCorrections.keys():
            if error in line:
                correction = DictErrorCorrections[error]
                line = line.replace(error, correction)
                print("Replacing: ", error, correction)

        #print(line)
        line = line.strip()
        line += "\n"
        f.write(line)
    f.close()


#
# Translate text files into HTML
#
print("TRANSLATING TO HTML")
f = open(PATH_TEMPLATE)
TEXT_TEMPLATE = f.read()
f.close()

talk_list_text = os.listdir(PATH_TEXT)
for talk in talk_list_text:

    path_text = PATH_TEXT + talk
    fx =  open(path_text)
    lines = fx.readlines()
    fx.close()

    file_name = talk.split('/')[-1]
    file_name = file_name.replace('.txt', '')
    if file_name not in TalkAttributes:
        print("NOT FOUND: ", file_name)
        continue

    title = TalkAttributes[file_name][0]
    speaker = TalkAttributes[file_name][1]
    date = TalkAttributes[file_name][2]
    duration = TalkAttributes[file_name][3]

    header = TEXT_TEMPLATE
    header = header.replace('XX_TITLE_HERE', title)
    header = header.replace('XX_AUTHOR_HERE', speaker)
    header = header.replace('XX_DATE_HERE', date)
    header = header.replace('XX_DURATION_HERE', duration)

    path_html = PATH_HTML + talk
    path_html = path_html.replace(".txt", ".html")
    f = open(path_html, 'w+')
    f.write(header)
    print("writing: ", path_html)

    count = 0
    text = ""
    for line in lines:
        line = line.strip()
        count += 1
        text = text + line + "\n"
        if count > NUMBER_LINES_IN_PARAGRAPH:
            text = text + "<p>\n"
            f.writelines(text)
            text = ""
            count = 0

    f.writelines(text)
    f.write("\n\n</body></html>\n")


#
# Translate HTML files into PDF
#
print("CONVERTING TO PDF")
talk_list_html = os.listdir(PATH_HTML)
for talk in talk_list_html:
    if "style" in talk: continue

    pdf_name = talk.replace('.mp3.html', '.pdf')
    path_html = PATH_HTML + talk
    path_pdf = PATH_PDF + pdf_name
    print(path_pdf)
    pdfkit.from_file(path_html, path_pdf)

