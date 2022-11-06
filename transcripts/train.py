#!/usr/bin/python3
#
# train.py
# Christopher Minson
#
# Generate a training set for OpenAI
#

import os
import string
import json
import datetime


PATH_JSON_CONFIG = "./CONFIG00.JSON"
PATH_INPUT = "./data/text/"


TalkAttributes = {}
f = open(PATH_JSON_CONFIG,'r')
all_talks  = json.load(f)
f.close()
for talk in all_talks['talks']:
    url = talk['url']
    mp3_name = url.split('/')[-1]
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
    TalkAttributes[mp3_name] = (title, speaker, date, duration)


list_files = os.listdir(PATH_INPUT)
for file_name in list_files:

    title = ""
    mp3_name = file_name.replace(".txt","")
    if mp3_name in TalkAttributes:
        attributes = TalkAttributes[mp3_name]
        title = attributes[0]
    else:
        print("ERROR: file_name not found", mp3_name)

    path_transcript = PATH_INPUT + file_name
    f =  open(path_transcript)
    list_lines = f.readlines()
    f.close()

    for line in list_lines:
        line = line.strip()
        print("{{\"prompt\": \"{0}\", \"completion\": \"{1}\"}}".format(title,line))



