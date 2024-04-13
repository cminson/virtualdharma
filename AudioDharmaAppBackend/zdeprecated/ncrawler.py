#!/usr/bin/python


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
from collections import Counter


Printable = dict.fromkeys(string.printable, 0)
CharExclusions = ["\"", "/", "\t", "\n"]

PATH_CRAWLER = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/crons"
PATH_LATESTCRAWL_JSON = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/LATESTCRAWL.JSON"
PATH_CONFIG_JSON = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG00.JSON"
PATH_CONFIG_ZIP = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG00.ZIP"
PATH_CONFIG_CANDIDATE_JSON = "CONFIG00.JSON"
PATH_CONFIG_CANDIDATE_ZIP = "CONFIG00.ZIP"

PATH_TALKS_TOP = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP200.JSON"
PATH_TALKS_TRENDING = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP2DAYS.JSON"
PATH_TALKS_TOP3MONTHS = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP90DAYS.JSON"
PATH_LOCAL_MP3CACHE = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/data/TALKS/"

# 15 minutes
MAX_SHORT_TALK_SECONDS = 15 * 60

#max talks to take from recent json
MAX_RECENT_TALKS = 10

AllTalks = []
TalkToSimilarsDict = {}
WORD = re.compile(r'\w+')


def newTalksPrint(text):

    FH_NEW_TALKS.write(text)
    FH_NEW_TALKS.write("\n")


def configPrint(text):

    FH_CONFIG_CANDIDATE.write(text)
    FH_CONFIG_CANDIDATE.write("\n")


def cleanText(text):

    s  = ""
    for c in text:
        #if c in Printable and c != "\"" and c != "/":
        if c in CharExclusions:
            c = " "
        if c in Printable:
            s += c
    return s


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
#
# Main Entry Point
#
# 1 - Import the first page of audiodharma.org.  Store json off into LATESTCRAWL_JSON
# 2 - Validate crawling json.  Exit if not valid.
# 3 - Validate current config json.  Exit if not valid.
# 4 - Combine current config and newly-crawled config
# 5 - Generate a new candidate config
# 6 - Validate candidate config.  Exit if not valid.
# 7 - Zip the candidate config
# 8 - Copy the validated candidate config json and zip to Config directory
# 9 - [If FullCrawl] generate new transcripts and recompute simililarties
#


FullCrawl = True
arglen = len(sys.argv)
if arglen > 2:
    print("usage: crawler.py <CRAWL_ONLY>")
    sys.exit(1)
if arglen == 2:
    FullCrawl = False

print("crawler: gathering talk data")

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
# Step 1:
# Get most recent talks. Store result off into LATESTCRAWL_JSON
#
print("crawler: crawling and building recent talks json")
PList = []
matchTalk = "<td class=\"talk_title\">"

URL_RECENT_TALKS = "https://www.audiodharma.org/playables/recent.json"

os.chdir(PATH_CRAWLER)

try:
    FH_NEW_TALKS = open(PATH_LATESTCRAWL_JSON, 'w')
except IOError, e:
    error = "Error %d: %s" % (e.args[0],e.args[1])
    print(error)
    sys.exit(1)

json_url = urllib2.urlopen(URL_RECENT_TALKS)
data = json.loads(json_url.read())
new_talks = data['playables'][:MAX_RECENT_TALKS]

newTalksPrint("{")
newTalksPrint("\t\"talks\":[")
for talk in new_talks:
    title = talk['name']
    url = download_url = talk['download_url']
    print(url)
    if len(url) < 1: continue
    speaker = talk['speaker']
    if 'Ying' in speaker:
        speaker = "Ying Chen"
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

    # get mp3 filename.  prune out escapes and non-ascii characters for our local storage
    download_url_file_name = download_url.split("/")[-1]
    url_file_name = url.split("/")[-1]
    url_file_name = url_file_name.replace("%","")
    url_file_name = url_file_name.replace(" ","")
    url_file_name = ''.join([i if ord(i) < 128 else '' for i in url_file_name])

    talk_id = url.split("/")[-2]
    url = url_file_name
    download_url = "/" + talk_id + "/" + download_url_file_name
    #print(speaker)

    newTalksPrint("\t{")
    newTalksPrint("\t\t\"title\":\"" + title.rstrip() + "\",")
    #newTalksPrint("\t\t\"series\":\"\",")
    newTalksPrint("\t\t\"series\":\"" + series + "\",")
    newTalksPrint("\t\t\"url\":\"" + url + "\",")
    newTalksPrint("\t\t\"download_url\":\"" + download_url + "\",")
    newTalksPrint("\t\t\"speaker\":\"" + speaker + "\",")
    newTalksPrint("\t\t\"date\":\"" + date + "\",")
    newTalksPrint("\t\t\"duration\":\"" + duration + "\"")
    newTalksPrint("\t},")

# cap the talks
newTalksPrint("\t{")
newTalksPrint("\t\t\"title\": \"NA\",")
newTalksPrint("\t\t\"series\": \"NA\",")
newTalksPrint("\t\t\"url\": \"NA\",")
newTalksPrint("\t\t\"download_url\": \"NA\",")
newTalksPrint("\t\t\"filename\": \"NA\",")
newTalksPrint("\t\t\"speaker\": \"NA\",")
newTalksPrint("\t\t\"date\": \"NA\",")
newTalksPrint("\t\t\"duration\": \"NA\"")
newTalksPrint("\t}")

newTalksPrint("\t]")
newTalksPrint("}\n")
FH_NEW_TALKS.close()


#
# Step 2:
# Validate the file of recent talks
#
print("crawler: loading and validating recent talks")
try:
    with open(PATH_LATESTCRAWL_JSON,'r') as myfile:
        new_data = json.load(myfile)
except:
    e = sys.exc_info()[0]
    print("LATESTCRAWL JSON ERROR: %s" % e)
    exit(0)


#
# Step 3:
# Get the current configuration and load it into a dictionary
#
print("crawler: loading and validating current config")
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
print("crawler: building candidate config")

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

print("Adding New Talks")


#
# Step 5:
# Generate new candidate config which contains all new talks 
# First the global part of the config, then all the talks, then the albums
#
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
# If True, that means we are getting talks from audiodharma
# If False, that means we are getting talks from elsewhere
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

    vurl = vduration = None
    if 'vurl' in talk:
        vurl = talk['vurl']
    if 'vduration' in talk:
        vduration = talk['vduration']
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

    #START CJM DEV
    """
    if "dharmette" in title:
        series = "Dharmettes"
    if "Dharmette" in title:
        series = "Dharmettes"
    if "practice note" in title:
        series = "Dharmettes"
    if "Practice Note" in title:
        series = "Dharmettes"
    """
    if "dharmette" in title:
        series = ""
    if "Dharmette" in title:
        series = ""
    if "practice note" in title:
        series = ""
    if "Practice Note" in title:
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
        series = "Dharmettes"
    #END CJM DEV

    filename = url.split('/')[-1]

    configPrint("\t{")
    printable = set(string.printable)
    title = filter(lambda x: x in printable, title)
    configPrint("\t\t\"title\":\"" + title + "\",")
    configPrint("\t\t\"series\":\"" + series +  "\",")
    configPrint("\t\t\"url\":\"" + url + "\",")
    if vurl is not None:
        configPrint("\t\t\"vurl\":\"" + vurl + "\",")
    if vduration is not None:
        configPrint("\t\t\"vduration\":\"" + vduration + "\",")
    configPrint("\t\t\"speaker\":\"" + speaker + "\",")

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
print("crawler: validating candidate config")
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
print("crawler: zipping config")
call(["zip",PATH_CONFIG_CANDIDATE_ZIP, PATH_CONFIG_CANDIDATE_JSON])


#
# Step 8:
# Copy candidate config json+zip to config deploy directory
#
print("crawler: deploying config")
call(["cp", PATH_CONFIG_CANDIDATE_JSON, PATH_CONFIG_JSON])
call(["cp", PATH_CONFIG_CANDIDATE_ZIP, PATH_CONFIG_ZIP])

#
# Step 9:
# Locally cache all new MP3s
#
print("crawler: caching new MP3s")
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


#
# Step 10:
# Generate similarities
#
print("crawler: generating similarities")
cmd = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/crons/gensimilar.py"
call([cmd, "50"])


print("crawler: complete")




