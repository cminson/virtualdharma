#!/usr/bin/python3
import json
import string
import os
import pdfkit
import datetime

PATH_RAW = "./data/raw/"
PATH_TEXT = "./data/text/"
PATH_HTML = "./data/html/"
PATH_PDF = "./data/pdf/"
PATH_TEMPLATE = "./data/template/template02.html"
PATH_JSON_TOP200 = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP200.JSON"
PATH_JSON_CONFIG = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG00.JSON"


PREAMBLE_1 = "The following talk was given at the Insight Meditation Center"
PREAMBLE_2 = "Please visit our website at audiodharma"
PREAMBLE_3 = "audioderma.org"

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
    print(year, month, day)
    if day > 32: continue

    d = datetime.datetime(year, month, day)
    
    date = d.strftime("%b %d, %Y")

    duration = talk['duration']
    #print(url, speaker, date, duration)
    TalkAttributes[file_name] = (title, speaker, date, duration) 


f = open(PATH_TEMPLATE)
TEXT_TEMPLATE = f.read()
f.close()


#exit()

print("TRANSLATING TO TEXT")
talk_list_raw = os.listdir(PATH_RAW)
for talk in talk_list_raw:
    path_raw = PATH_RAW + talk
    print("reading: ", path_raw)
    f =  open(path_raw)
    content = f.read()
    f.close()

    path_text = PATH_TEXT + talk
    f = open(path_text, 'w+')
    lines = content.split(". ")
    print("writing: ", path_text)
    for line in lines:

        if PREAMBLE_1 in line: continue
        if PREAMBLE_2 in line: continue
        if PREAMBLE_3 in line: continue
        if "META" in line: 
            line = line.replace("META", "Meta")
        if "Fronstel" in line: 
            line = line.replace("Fronstel", "Fronsdal")
        if "vinyet" in line: 
            line = line.replace("vinyet", "vignette")
        line = line.strip()
        line += ". \n"
        f.write(line)
    f.close()


print("TRANSLATING TO HTML")
talk_list_text = os.listdir(PATH_TEXT)
for talk in talk_list_text:

    if "style" in talk: continue

    path_text = PATH_TEXT + talk
    print("reading: ", path_text)
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
        if count > 5:
            text = text + "<p>\n"
            f.writelines(text)
            text = ""
            count = 0

    f.writelines(text)
    f.write("\n\n</body></html>\n")


print("CONVERTING TO PDF")
talk_list_html = os.listdir(PATH_HTML)
for talk in talk_list_html:
    if "style" in talk: continue

    pdf_name = talk.replace('.mp3.html', '.pdf')
    path_html = PATH_HTML + talk
    path_pdf = PATH_PDF + pdf_name
    print(path_pdf)
    pdfkit.from_file(path_html, path_pdf)

