#!/usr/bin/python3
#
# get all new talks via API.  store result in PATH_NEW_TALKS_API

from __future__ import print_function
#import urllib2
from urllib.request import urlopen

import os
import sys
import json
import string
import json
import operator
import re, math
import time
from subprocess import call
from collections import Counter


Printable = dict.fromkeys(string.printable, 0)
CharExclusions = ["\"", "/", "\t", "\n"]

PATH_NEW_TALKS_API = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/NEWTALKS_API.JSON"

PATH_TALKS_TOP = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP200.JSON"
PATH_TALKS_TRENDING = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP2DAYS.JSON"
PATH_TALKS_TOP3MONTHS = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP90DAYS.JSON"

URL_RECENT_TALKS = "https://www.audiodharma.org/playables/recent.json" # endpoint to get new talks from AudioDharma
MAX_NEW_TALKS = 10  # max number of new talks we will get

AllTalks = []
WORD = re.compile(r'\w+')


def newTalksPrint(text):

    FH_NEW_TALKS.write(text)
    FH_NEW_TALKS.write("\n")

def cleanText(text):

    text = text.replace("'", "")
    text = text.replace("\"", "")
    #
    #CJM:  Disabling as it screws up Spanish language text
    #Monitor
    """
    s  = ""
    for c in text:
        #if c in Printable and c != "\"" and c != "/":
        if c in CharExclusions:
            c = " "
        if c in Printable:
            s += c
    return s
    """
    return text


#
#
# Main Entry Point
#
# Gather all new talks
# Do some minor cleanup so that badly formed urls don't get into the system
# Validate the talks
# Store result 
#
#
print("getNewTalks: start")
print("getNewTalks: getting new talks ")
try:
    FH_NEW_TALKS = open(PATH_NEW_TALKS_API, 'w')
except  e:
    error = "Error %d: %s" % (e.args[0],e.args[1])
    print(error)
    sys.exit(1)

try:
    response = urlopen(URL_RECENT_TALKS)
except e:
    print("ERROR NOT FOUND: ", URL_RECENT_TALKS)
    exit()
encoding = response.info().get_content_charset('utf-8')
data = response.read()
jsonText = json.loads(data.decode(encoding))
new_talks = jsonText['playables'][:MAX_NEW_TALKS]
new_talks = [talk for talk in new_talks if len(talk['download_url']) > 10]

newTalksPrint("{")
newTalksPrint("\t\"talks\":[")
for talk in new_talks:
    title = talk['name']
    url = download_url = talk['download_url']
    speaker = talk['speaker']
    language = talk['language']

    if language == "English":
        ln = "en"
    else:
        ln = "es"

    if 'Ying' in speaker:
        speaker = "Ying Chen"
    if 'bruni' in speaker:
        speaker = 'Bruni Dávila'

    date = talk['date']
    duration = talk['duration']
    series = ""
    if "parent_series" in talk:
        series = talk['parent_series'][0]["name"]
        #print(series)

    title = cleanText(title)
    series = cleanText(series)
    if 'Guided Meditation' in series:
        series = 'Guided Meditations'
    if 'Guided Meditation' in title:
        series = 'Guided Meditations'


    #
    # the download_url is the native url in audiodharma.  that's what we download to local storage
    # the url is the filtered download_url, cleaned up and expressed just as filename.  that's the name we store
    #

    # get mp3 filename.  prune out escapes and non-ascii characters for our local storage
    download_url_file_name = download_url.split("/")[-1]
    url_file_name = url.split("/")[-1]
    url_file_name = url_file_name.replace("%","")
    url_file_name = url_file_name.replace(" ","")

    #CJM DEV:  Maybe not necessary anymore with Python3.  Monitor
    #url_file_name = ''.join([i if ord(i) < 128 else '' for i in url_file_name])

    talk_id = url.split("/")[-2]
    url = url_file_name
    download_url = "/" + talk_id + "/" + download_url_file_name
    #print(speaker)

    newTalksPrint("\t{")
    newTalksPrint("\t\t\"title\":\"" + title.rstrip() + "\",")
    #newTalksPrint("\t\t\"series\":\"\",")
    newTalksPrint("\t\t\"series\":\"" + series + "\",")
    newTalksPrint("\t\t\"url\":\"" + download_url + "\",")
    newTalksPrint("\t\t\"ln\":\"" + ln + "\",")
    newTalksPrint("\t\t\"download_url\":\"" + download_url + "\",")
    newTalksPrint("\t\t\"speaker\":\"" + speaker + "\",")
    newTalksPrint("\t\t\"date\":\"" + date + "\",")
    newTalksPrint("\t\t\"duration\":\"" + duration + "\"")

    if talk != new_talks[-1]:
        newTalksPrint("\t},")
    else:
        newTalksPrint("\t}")

newTalksPrint("\t]")
newTalksPrint("}\n")
FH_NEW_TALKS.close()


#
# Validate the file of new talks
#
print("getNewTalks: loading and validating new talks: ", PATH_NEW_TALKS_API)
try:
    with open(PATH_NEW_TALKS_API,'r') as myfile:
        new_data = json.load(myfile)
except:
    e = sys.exc_info()[0]
    print("NEW TALKS JSON ERROR: %s" % e)
    exit(0)

print("getNewTalks: Done")

