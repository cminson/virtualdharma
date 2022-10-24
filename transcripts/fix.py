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


PATH_RAW = "./data/raw/"
PATH_FIXED = "./data/fixed/"

talk_list_raw = os.listdir(PATH_RAW)
for file_name in talk_list_raw:
    path_raw = PATH_RAW + file_name
    f =  open(path_raw)
    content = f.read()
    f.close()

    path_fixed = PATH_FIXED + file_name
    f = open(path_fixed, 'w+')

    lines = content.split(". ")
    print("writing: ", path_fixed)
    for line in lines:

        line = line.strip()
        line += ". \n"
        #print(line)
        f.write(line)

    f.close()


