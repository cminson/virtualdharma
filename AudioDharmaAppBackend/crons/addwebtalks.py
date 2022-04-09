#!/usr/bin/python
#
# addwebtalks:  add new talks from web crawl into CONFIG01.JSON.  also incorporates latest top talks
#

from __future__ import print_function
import urllib2
import os
import sys
import json
import string
import json
import operator
import re, math
import time
from subprocess import call

PATH_CRON_SCRIPTS = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/crons"
PATH_NEW_TALKS_API = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/NEWTALKS_WEB.JSON"
PATH_CONFIG_JSON = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG01.JSON"
PATH_CONFIG_ZIP = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG01.ZIP"
PATH_CONFIG_CANDIDATE_JSON = "CONFIG01.JSON"
PATH_CONFIG_CANDIDATE_ZIP = "CONFIG01.ZIP"


PATH_TALKS_TOP = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP200.JSON"
PATH_TALKS_TRENDING = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP2DAYS.JSON"
PATH_TALKS_TOP3MONTHS = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP90DAYS.JSON"
PATH_LOCAL_MP3CACHE = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/data/TALKS/"

# max duration to be classified as short talk.  15 minutes
MAX_SHORT_TALK_SECONDS = 15 * 60

#max talks to take from recent json
MAX_RECENT_TALKS = 10

AllTalks = []
TalkToSimilarsDict = {}
WORD = re.compile(r'\w+')

AllGuidedMeditions = []
AllShortTalks = []

def configPrint(text):

    FH_CONFIG_CANDIDATE.write(text)
    FH_CONFIG_CANDIDATE.write("\n")


def capitalizeWords(text):

    new_words = []
    words = text.split()
    word_len = len(words)

    #print(words)
    for idx, word in enumerate(words):
        new_word = word
        if idx == 0:
            new_word = new_word.capitalize()
        elif len(new_word) > 3:
            new_word = new_word.capitalize()
        new_words.append(new_word)

    return " ".join(new_words)


#
# addNewTalks: Add new talks to CONFIG00.JSON. This is the key program that updates the apps.
#
# Main Entry Point
#
# 1 - Gather top talks and trending talks (these will be incorporated in CONFIG00.JSON along with new talks)
# 2 - Import the newest talks from PATH_NEW_TALKS (which was previously created by getNewTalks.py)
# 3 - Validate current config json.  Exit if not valid.
# 4 - Combine current config and new-talks config
# 5 - Generate a new candidate config
# 6 - Validate candidate config.  Exit if not valid.
# 7 - Zip the candidate config
# 8 - Copy the validated candidate config json and zip to Config directory
# 9 - [If FullCrawl] generate new transcripts and recompute simililarties
#


FullCrawl = True
arglen = len(sys.argv)
if arglen > 2:
    print("usage: addNewTalks.py <CRAWL_ONLY>")
    sys.exit(1)
if arglen == 2:
    FullCrawl = False


#
# Step 1:
# Get top talks and trending talks
#
print("addNewTalks: getting top talks and trending talks")
try:
    with open(PATH_TALKS_TOP,'r') as fd:
        TopTalks  = json.load(fd)
except IOError, e:
    error = "Error %d: %s" % (e.args[0],e.args[1])
    print(error)
    sys.exit(1)

try:
    with open(PATH_TALKS_TRENDING,'r') as fd:
        TrendingTalks  = json.load(fd)
except IOError, e:
    error = "Error %d: %s" % (e.args[0],e.args[1])
    print(error)
    sys.exit(1)

try:
    with open(PATH_TALKS_TOP3MONTHS,'r') as fd:
        Top3MonthsTalks  = json.load(fd)
except IOError, e:
    error = "Error %d: %s" % (e.args[0],e.args[1])
    print(error)
    sys.exit(1)


#
# Step 2:
# Get the newest talks
#
print("addNewTalks: getting new talks")
try:
    with open(PATH_NEW_TALKS_API,'r') as myfile:
        new_data = json.load(myfile)
except:
    e = sys.exc_info()[0]
    print("NEW TALKS JSON ERROR: %s" % e)
    exit(0)


#
# Step 3:
# Get the current configuration and load it into a dictionary
#
print("addNewTalks: loading and validating current config")
try:
    with open(PATH_CONFIG_JSON,'r') as currenttalks:
        current_data  = json.load(currenttalks)
except:
    e = sys.exc_info()[0]
    print("CONFIG JSON ERROR: %s" % e)
    exit(0)


#
# Step 4:
# Combine newly crawled and existing talks.  
#
print("addNewTalks: building candidate config")

MP3_SOURCE = 'https://audiodharma.us-east-1.linodeobjects.com/talks'
current_config = current_data['config']
MP3_HOST = current_config["URL_MP3_HOST"]
USE_NATIVE_MP3PATHS = current_config["USE_NATIVE_MP3PATHS"]
MAX_TALKHISTORY_COUNT = current_config["MAX_TALKHISTORY_COUNT"]
albums = current_data['albums']
current_talks = current_data['talks']
new_talks = new_data['talks']

#print(new_talks)

# these lines 1) removes duplicates for all talks (old + new)and 2) generates a sorted list of the result
all_talks = new_talks + current_talks
for v in all_talks:
    if 'url' not in v:
        print(v)
        exit()
unique_talks = dict((v['url'],v) for v in all_talks).values()
all_talks= sorted(unique_talks, key=lambda k: k['date'], reverse=True)



#
# Step 5:
# Generate new candidate config which contains all new talks 
# First the global part of the config, then all the talks, then the albums
#
print("addNewTalks: generating new candidate config file")
try:
    FH_CONFIG_CANDIDATE = open(PATH_CONFIG_CANDIDATE_JSON, 'w')
except IOError, e:
    error = "Error %d: %s" % (e.args[0],e.args[1])
    print(error)
    sys.exit(1)

configPrint("{")
configPrint("\t\"config\": {")
configPrint("\t\t\"URL_MP3_HOST\":\"" + MP3_HOST + "\",")

#
# If True, that means we are getting talks using the full path (talk_id + filename) as expressed in CONFIG00.JSON
# If False, means we are getting talks using just the filename
# 
# for now should always be TRUE
# this is somewhat a legacy. originally designed to help use MP3s that aren't nativey stored on AudioDharma
# keeping this capability for now, as it may have some future use
#
if USE_NATIVE_MP3PATHS == True:
    configPrint("\t\t\"USE_NATIVE_MP3PATHS\":true,")
else:
    configPrint("\t\t\"USE_NATIVE_MP3PATHS\":false,")

configPrint("\t\t\"MAX_TALKHISTORY_COUNT\":" + str(MAX_TALKHISTORY_COUNT) + "")
configPrint("\t},")

configPrint("\t\"talks\":[")

for talk in all_talks:
    #print(talk)
    url = talk['url']

    if "NA" in url:
        continue

    title = talk["title"]
    title = capitalizeWords(title)

    series = talk["series"]
    if "speaker" not in talk:
        speaker = "Ari Crellin"
    else:
        speaker = talk["speaker"]
    date = talk["date"]
    date = date.replace("-", ".")
    duration = talk["duration"]
    pdf = keys = ""

    if "pdf" in talk:
        pdf = talk["pdf"]
    if "keys" in talk:
        keys = talk["keys"]

    if "&amp;" in title:
        title = title.replace("&amp;", "&")
    if "&amp;" in series:
        series = series.replace("&amp;", "&")

    if "dharmette" in series:
        series = ""

    if "Guided Meditation" in title:
        AllGuidedMeditions.append(talk)
        series = ""
    hms = duration.split(':')
    hours = 0
    minutes = 0
    seconds = 0
    if len(hms) == 3:
        hours = int(hms[0])
    elif len(hms) == 2:
        minutes = int(hms[0])
        seconds = int(hms[1])
    else:
        print("ERROR", hms)
        exit()
    seconds = (hours * 60 * 60) + (minutes * 60) + seconds
    if seconds < MAX_SHORT_TALK_SECONDS:
        #print("Short TALK", title, seconds, duration)
        AllShortTalks.append(talk)
        series = ""

    if "Dharmette" in title:
        series = "Dharmettes"

    filename = url.split('/')[-1]

    configPrint("\t{")
    printable = set(string.printable)
    title = filter(lambda x: x in printable, title)
    configPrint("\t\t\"title\":\"" + title.encode("utf-8") + "\",")
    configPrint("\t\t\"series\":\"" + series.encode("utf-8")  +  "\",")
    configPrint("\t\t\"url\":\"" + url + "\",")
    configPrint("\t\t\"speaker\":\"" + speaker.encode("utf-8") + "\",")

    configPrint("\t\t\"pdf\":\"" + pdf + "\",")
    configPrint("\t\t\"keys\":\"" + keys + "\",")
    #if len(pdf) > 0: configPrint("\t\t\"pdf\":\"" + pdf + "\",")
    #if len(keys) > 0: configPrint("\t\t\"keys\":\"" + keys + "\",")
    configPrint("\t\t\"date\":\"" + date + "\",")
    configPrint("\t\t\"duration\":\"" + duration + "\"")

    if url == all_talks[-1]["url"]:
        configPrint("\t}")
    else:
        configPrint("\t},")

configPrint("\t],")

configPrint("\t\"albums\":[")
for album in albums:

    section = album['section']
    title = album['title']
    content = album['content']
    image = album['image']

    if "&amp;" in title:
        title = title.replace("&amp;", "&")

    configPrint("\t{")
    configPrint("\t\t\"section\":\"" + section + "\",")
    configPrint("\t\t\"title\":\"" + title + "\",")
    configPrint("\t\t\"content\":\"" + content + "\",")
    if "talks" in album:
        configPrint("\t\t\"image\":\"" + image + "\",")
    else:
        configPrint("\t\t\"image\":\"" + image + "\"")

    talkCount = 0
    if "talks" in album:
        configPrint("\t\t\"talks\": [")
        if content == 'TALKS_TOP_PATH':
            talks = TopTalks['talks']
        elif content == 'TRENDING':
            talks = TrendingTalks['talks']
        elif content == 'TOP3MONTHS':
            talks = Top3MonthsTalks['talks']
        elif content == 'KEY_GUIDED_MEDITATIONS':
            talks = AllGuidedMeditions
        elif content == 'KEY_SHORT_TALKS':
            talks = AllShortTalks
        else:
            talks = album["talks"]
        for talk in talks:
            #configPrint(talk)
            if "section" in talk:
                section = talk['section']
            else:
                section = "_"

            series = talk['series']
            title = talk['title']
            title = capitalizeWords(title)

            url = talk['url']

            configPrint("\t\t{")
            if content != "KEY_GUIDED_MEDITATIONS" and content != "KEY_SHORT_TALKS":
                configPrint("\t\t\t\"series\":\"" + series + "\",")
                configPrint("\t\t\t\"section\":\"" + section + "\",")

            configPrint("\t\t\t\"title\":\"" + title + "\",")
            configPrint("\t\t\t\"url\":\"" + url + "\"")

            if url == talks[-1]["url"]:
                configPrint("\t\t}")
            else:
                configPrint("\t\t},")

        configPrint("\t\t]")

    if content == albums[-1]["content"]:
        configPrint("\t}")
    else:
        configPrint("\t},")


configPrint("\t]")
configPrint("}")

FH_CONFIG_CANDIDATE.close()


#
# Step 6:
# Validate the candidate config
#
print("addNewTalks: validating candidate config")
try:
    with open(PATH_CONFIG_CANDIDATE_JSON,'r') as config:
        _  = json.load(config)
except:
    e = sys.exc_info()[0]
    print("CONFIG CANDIDATE JSON ERROR: %s" % e)
    exit(0)
    
#
# Step 7:
# Zip the config json
#
print("addNewTalks: zipping config")
call(["zip",PATH_CONFIG_CANDIDATE_ZIP, PATH_CONFIG_CANDIDATE_JSON])


#
# Step 8:
# Copy candidate config json+zip to config deploy directory
#
print("addNewTalks: deploying config")
call(["cp", PATH_CONFIG_CANDIDATE_JSON, PATH_CONFIG_JSON])
call(["cp", PATH_CONFIG_CANDIDATE_ZIP, PATH_CONFIG_ZIP])

#
# Step 9:
# Locally cache all new MP3s
#
"""
print("addNewTalks: caching new MP3s locally")
local_mp3_cache = os.listdir(PATH_LOCAL_MP3CACHE)
for talk in new_talks:
    url = talk['url']
    download_url = talk['download_url']
    if "NA" in url:
        continue
    download_filename = download_url.split('/')[-1]
    filename = url.split('/')[-1]

    if filename not in local_mp3_cache:

        source_path = MP3_SOURCE + download_url
        dest_path = PATH_LOCAL_MP3CACHE + filename
        print("Downloading: ", source_path, "to: ", dest_path)
        try:
            response = urllib2.urlopen(source_path)
        except IOError, e:
            print("ERROR NOT FOUND: ", source_path)
            continue
        data = response.read()
        f = open(dest_path, "w+")
        f.write(data)
"""

#
# Step 10:
# Generate similarities
#
os.chdir(PATH_CRON_SCRIPTS)
print("addNewTalks: generating similarities")
cmd = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/crons/gensimilar.py"
call([cmd, "50"])

print("crawler: complete")


