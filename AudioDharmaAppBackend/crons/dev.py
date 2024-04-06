#!/usr/bin/python3
#
# addapitalks:  add new talks via API into CONFIG00.JSON.  also incorporates latest top talks
#

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

PATH_CRON_SCRIPTS = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/crons"
PATH_NEW_TALKS_API = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/NEWTALKS_API.JSON"
PATH_CONFIG_JSON = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG00.JSON"
PATH_AI_CONFIG_JSON = "/var/www/audiodharma/httpdocs/config/ALLTALKS.JSON"
PATH_CONFIG_ZIP = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG00.ZIP"

# these must be here so that unzip puts the zip file in a root directory
PATH_CONFIG_SIZE_JSON = "CONFIGSIZE.JSON"
PATH_CONFIG_CANDIDATE_JSON = "CONFIG00.JSON"
PATH_CONFIG_CANDIDATE_ZIP = "CONFIG00.ZIP"

PATH_CONFIG_JSON = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/DEV.JSON"
PATH_CONFIG_CANDIDATE_JSON = "DEV.JSON"
PATH_CONFIG_CANDIDATE_ZIP = "DEV.ZIP"

PATH_TALKS_RECOMMENDED = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/RECOMMENDED.JSON"
PATH_TALKS_TOP = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP200.JSON"
PATH_TALKS_TRENDING = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP2DAYS.JSON"
PATH_TALKS_TOP3MONTHS = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP90DAYS.JSON"

PATH_IMPORT_TRANSCRIPTS = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/data/IMPORT_PDF/"
PATH_ACTIVE_TRANSCRIPTS = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/data/PDF/"
URL_ACTIVE_TRANSCRIPTS = "http://virtualdharma.org/AudioDharmaAppBackend/data/PDF/"

# max duration to be classified as short talk.  15 minutes
MAX_SHORT_TALK_SECONDS = 15 * 60

#max talks to take from recent json
MAX_RECENT_TALKS = 10

AllTalks = []
TalkToSimilarsDict = {}
MP3ToTranscriptDict = {}
WORD = re.compile(r'\w+')

AllGuidedMeditions = []
AllSpanishTalks = []
AllShortTalks = []
AllTranscriptTalks = []

ConfigDict = {}


def get_album_index(list_albums, key):

    for i, album in enumerate(list_albums):

        if album["content"] == key:
            return i

    print(f"KEY NOT FOUND:  {key}")
    exit()


def reduce_fields(list_talks):

    new_talk_list = []

    for talk in list_talks:

        filtered_talk = {k: v for k, v in talk.items() if k in ['url', 'title']}
        new_talk_list.append(filtered_talk)

    return new_talk_list




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
#


# Build dict of all PDFs.  Any new ones (not in the Config) will get inserted below when we build a new Config
for pdf in os.listdir(PATH_ACTIVE_TRANSCRIPTS):
    mp3 = pdf.replace("pdf", "mp3")
    MP3ToTranscriptDict[mp3] = URL_ACTIVE_TRANSCRIPTS + pdf

#
# Step 1:
# Gather all albums
#
print("addNewTalks: gathering top albums and recommended albums")
try:
    with open(PATH_TALKS_TOP,'r') as fd:
        TopTalks  = json.load(fd)["talks"]
except Exception as e:
    error = "Error: %s" % str(e)
    print(error)
    sys.exit(1)

try:
    with open(PATH_TALKS_TRENDING,'r') as fd:
        TrendingTalks  = json.load(fd)["talks"]
except Exception as e:
    error = "Error: %s" % str(e)
    print(error)
    sys.exit(1)

try:
    with open(PATH_TALKS_TOP3MONTHS,'r') as fd:
        Top3MonthsTalks  = json.load(fd)["talks"]
except Exception as e:
    error = "Error: %s" % str(e)
    print(error)
    sys.exit(1)


#
# Step 2:
# Get the newest talks
#
print("addNewTalks: getting new talks")
try:
    with open(PATH_NEW_TALKS_API,'r') as fd :
        new_talks = json.load(fd)["talks"]
except Exception as e:
    e = sys.exc_info()[0]
    print("NEW TALKS JSON ERROR: %s" % e)
    exit(0)


#
# Step 3:
# Get the current configuration and load it into a dictionary
#
print("addNewTalks: loading and validating current config")
try:
    with open(PATH_CONFIG_JSON,'r') as fd:
        ConfigDict  = json.load(fd)
except Exception as e:
    e = sys.exc_info()[0]
    print("CONFIG JSON ERROR: %s" % e)
    exit(0)


#
# Step 4:
# Combine newly crawled and existing talks.  
#
print("addNewTalks: building candidate config")

current_talks = ConfigDict['talks']

# these lines 1) removes duplicates for all talks (old + new)and 2) generates a sorted list of the result
all_talks = new_talks + current_talks
for v in all_talks:
    if 'date' not in v:
        print("NO DATE:", v)
    if 'url' not in v:
        print(v)
        exit()
unique_talks = dict((v['url'],v) for v in all_talks).values()
all_talks= sorted(unique_talks, key=lambda k: k['date'], reverse=True)


# clean up the talks of various artifacts
for talk in all_talks:

    #print(talk["title"])
    if "NA" in talk["url"]:
        continue

    talk["title"] = talk["title"].replace("&amp;", "&")
    talk["speaker"] = talk["speaker"].replace("<multiple>", "Multiple")
    talk["date"] = talk["date"].replace("-", ".")

    if "series" not in talk:
        talk["series"] = ""
    talk["series"] = talk["series"].replace("&amp;", "&")
    if "Tuesday Sitting " in talk["series"]:
        talk["series"] = "Tuesday Sitting"
    if "Sunday Morning " in talk["series"]:
        talk["series"] = "Sunday Morning"
    if "Monday Night " in talk["series"]:
        talk["series"] = "Sunday Morning "
    if "Guided Meditation" in talk["series"]:
        talk["series"] = "Guided Meditations"
        AllGuidedMeditions.append(talk)

    # detect and record Spanish content
    if talk["ln"] == "es":
        #CJM DEV - necessary for some reason, to prevent series showing in RECOMMENDATIONS
        talk['series'] = ""
        AllSpanishTalks.append(talk)

    # detect and record PDF for talks
    mp3_file_name = talk["url"].split("/")[-1]
    if mp3_file_name in MP3ToTranscriptDict and not pdf:
        pdf  = MP3ToTranscriptDict[mp3_file_name]
        print("NEW TRANSCRIPT", pdf)
    if pdf:
        AllTranscriptTalks.append(talk)

    # detect and record short talks
    hms = talk["duration"].split(':')
    hours = 0
    minutes = 0
    seconds = 0
    if len(hms) == 3:
        hours = int(hms[0])
    elif len(hms) == 2:
        minutes = int(hms[0])
        seconds = int(hms[1])
    else:
        print("DURATION ERROR", duration, hms)
        continue
        #exit()
    seconds = (hours * 60 * 60) + (minutes * 60) + seconds
    if seconds < MAX_SHORT_TALK_SECONDS:
        AllShortTalks.append(talk)


#
# Step 5:
# Generate new candidate config which contains all new talks 
#

print("addNewTalks: generating new candidate config file")

ConfigDict["talks"] = all_talks

i = get_album_index(ConfigDict["albums"], "TRENDING")
ConfigDict["albums"][i]["talks"] = reduce_fields(TrendingTalks[0:200])

i = get_album_index(ConfigDict["albums"], "TOP3MONTHS")
ConfigDict["albums"][i]["talks"] = reduce_fields(Top3MonthsTalks)

i = get_album_index(ConfigDict["albums"], "KEY_GUIDED_MEDITATIONS")
ConfigDict["albums"][i]["talks"] = reduce_fields(AllGuidedMeditions)

i = get_album_index(ConfigDict["albums"], "KEY_SHORT_TALKS")
ConfigDict["albums"][i]["talks"] = reduce_fields(AllShortTalks)

i = get_album_index(ConfigDict["albums"], "KEY_TRANSCRIPT_TALKS")
ConfigDict["albums"][i]["talks"] = reduce_fields(AllTranscriptTalks)



try:
    fd = open(PATH_CONFIG_CANDIDATE_JSON, 'w')
    json.dump(ConfigDict, fd, indent=4)
except Exception as e:
    error = "Error %d: %s" % (e.args[0],e.args[1])
    print(error)
    sys.exit(1)

exit()




    
#
# Step 8:
# Zip the config json
#
print("addNewTalks: zipping config")
call(["zip",PATH_CONFIG_CANDIDATE_ZIP, PATH_CONFIG_CANDIDATE_JSON])



#
# Step 9:
# Copy candidate config json+zip to config deploy directory
#
print("addNewTalks: deploying config")
call(["cp", PATH_CONFIG_CANDIDATE_JSON, PATH_CONFIG_JSON])
call(["cp", PATH_CONFIG_JSON, PATH_AI_CONFIG_JSON])
call(["cp", PATH_CONFIG_CANDIDATE_ZIP, PATH_CONFIG_ZIP])
call(["cp", PATH_CONFIG_CANDIDATE_ZIP, PATH_CONFIG_ZIP])


#
# Step 10:
# Generate similarities
#
os.chdir(PATH_CRON_SCRIPTS)
print("addNewTalks: generating similarities")
cmd = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/crons/gensimilar.py"
call([cmd, "50"])

print("crawler: complete")


