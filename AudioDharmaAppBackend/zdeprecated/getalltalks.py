#!/usr/bin/python3

import urllib.request
import os
import sys
import json
import string
import json
import time
import re

Printable = dict.fromkeys(string.printable, 0)
CharExclusions = ["\"", "/", "\t", "\n", "\r"]

PATH_ALL_TALKS_WEB = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/ALLTALKS_WEB.JSON"
PATH_TALKS_TOP = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP200.JSON"
PATH_TALKS_TRENDING = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP2DAYS.JSON"
PATH_TALKS_TOP3MONTHS = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP90DAYS.JSON"

URL_CRAWL_TARGET = "https://www.audiodharma.org"

TalkDupDict = {}

def newTalksPrint(text):

    FH_NEW_TALKS.write(text)
    FH_NEW_TALKS.write("\n")


def cleanText(text):

    s  = ""
    for c in text:
        #if c in Printable and c != "\"" and c != "/":
        if c in CharExclusions:
            c = " "
        if c in Printable:
            s += str(c)
    return s


def getSeries(series, url):

    new_talks = []
    target = URL_CRAWL_TARGET  + url
    try:
        with urllib.request.urlopen(target) as response:
            html = response.read()
    except:
        e = sys.exc_info()[0]
        print("GetSeries ERROR: %s" % e)
        return []

    #with urllib.request.urlopen(target) as response:
    #    html = response.read()

    html = html.decode("utf-8") 
    lines = html.split('\n')
    target_text = False
    html = ""
    for line in lines:
        if '<table' in line:
            target_text = True
        if '</table' in line: break
        if target_text == True:
            html += line
            html += '\n'

    lines = html.split('\n')
    tr_list = []
    tr_text = ''
    for line in lines:
        if '<tr>' in line:
            target_text = True
            tr_text = ""
            continue
        if '</tr>' in line:
            target_text = False
            tr_list.append(tr_text)
        if target_text == True:
            tr_text += line

    for tr_text in tr_list:
        #print("TR: ",tr_text)
        start = tr_text.find('\">')+2
        stop = tr_text.find('</a>')
        title = tr_text[start:stop]
        print(title)

        start = tr_text.find('playable-table-speaker',stop)
        start = tr_text.find('href',start)
        start = tr_text.find('>',start)
        stop = tr_text.find('</a>',start)
        speaker = tr_text[start+1:stop]
        print(speaker)
        
        start = tr_text.find('playable-table-date')
        stop = tr_text.find('</td>',start)
        date = tr_text[start+21:stop]
        print(date)
        start = tr_text.find('\">',stop)
        stop = tr_text.find('</td>',start)
        duration = tr_text[start+2:stop]
        print(duration)

        start = tr_text.find('data-url=',stop)
        stop = tr_text.find('.mp3',start)
        url = tr_text[start+10:stop+4]

        if series == True:
            series_talks = getSeries(title, url)
            new_talks += series_talks
            continue
        if '-' in duration:
            print("ERROR")
            continue

        talk = {}
        talk['url'] = url
        talk['name'] = title
        talk['speaker'] = speaker
        talk['date'] = date
        talk['duration'] = duration
        talk['series'] = series


        if url in TalkDupDict:
            print("Dup: ", url)
            continue

        TalkDupDict[url] = True
        new_talks.append(talk)
        print("Adding: ", talk)

    return new_talks


def getTalksViaCrawl(target):

    new_talks = []
    with urllib.request.urlopen(target) as response:
        html = response.read()
    html = html.decode("utf-8") 
    lines = html.split('\n')
    target_text = False
    html = ""
    for line in lines:
        if '<table' in line:
            target_text = True
        if '</table' in line: break
        if target_text == True:
            html += line
            html += '\n'

    lines = html.split('\n')
    tr_list = []
    tr_text = ''
    for line in lines:
        if '<tr>' in line:
            target_text = True
            tr_text = ""
            continue
        if '</tr>' in line:
            target_text = False
            tr_list.append(tr_text)
        if target_text == True:
            tr_text += line

    for tr_text in tr_list:
        #print("TR: ",tr_text)
        if 'series' in tr_text:
            series = True
        else:
            series = False
        start = tr_text.find('\">')+2
        stop = tr_text.find('</a>')
        title = tr_text[start:stop]
        print(title)

        start = tr_text.find('playable-table-speaker',stop)
        start = tr_text.find('href',start)
        start = tr_text.find('>',start)
        stop = tr_text.find('</a>',start)
        speaker = tr_text[start+1:stop]
        print(speaker)
        
        start = tr_text.find('playable-table-date')
        stop = tr_text.find('</td>',start)
        date = tr_text[start+21:stop]
        print(date)
        start = tr_text.find('\">',stop)
        stop = tr_text.find('</td>',start)
        duration = tr_text[start+2:stop]
        print(duration)

        start = tr_text.find('data-url=',stop)
        stop = tr_text.find('.mp3',start)
        url = tr_text[start+10:stop+4]

        if series == True:
            series_talks = getSeries(title, url)
            new_talks += series_talks
            continue
        if '-' in duration:
            print("ERROR")
            continue

        talk = {}
        talk['url'] = url
        talk['name'] = title
        talk['speaker'] = speaker
        talk['date'] = date
        talk['duration'] = duration
        talk['series'] = " "
        if url in TalkDupDict:
            print("Dup: ", url)
            continue
        TalkDupDict[url] = True;
        new_talks.append(talk)
        print("Adding: ", talk)

    return new_talks


def storeTalks(new_talks, path_new_talks):

    global FH_NEW_TALKS

    FH_NEW_TALKS = open(path_new_talks, 'w')

    newTalksPrint("{")
    newTalksPrint("\t\"talks\":[")
    for talk in new_talks:
        title = talk['name']
        url = download_url = talk['url']
        if len(url) < 1: continue
        speaker = talk['speaker']
        if 'Ying' in speaker:
            speaker = "Ying Chen"
        date = talk['date']
        duration = talk['duration']
        series = talk['series']

        title = cleanText(title)
        series = cleanText(series)
        if 'Guided Meditation' in series:
            series = 'Guided Meditations'
        if 'Guided Meditation' in title:
            series = 'Guided Meditations'

        #
        # the download_url is the native url in audiodharma.  
        # that's what we download to local storage
        # the url is the filtered download_url, cleaned up and expressed 
        # just as filename.  that's the name we store
        #
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
        newTalksPrint("\t\t\"series\":\"" + series + "\",")
        newTalksPrint("\t\t\"url\":\"" + url + "\",")
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
# Main Entry Point
#
# Gather all new talks
# Do some minor cleanup so that badly formed urls don't get into the system
# Validate the talks
# Store result 
#
all_talks = []
#for i in range(0,357):
for i in range(0,357):
    target = URL_CRAWL_TARGET + "?page=" + str(i)
    #target = 'https://www.audiodharma.org/?page=45'
    print("Target: ",target)
    new_talks = getTalksViaCrawl(target)
    all_talks += new_talks
    time.sleep(2)

storeTalks(all_talks,PATH_ALL_TALKS_WEB)

#
# Validate the file of all talks
#
print("getNewTalks: loading and validating all talks: ", PATH_ALL_TALKS_WEB)
try:
    with open(PATH_ALL_TALKS_WEB,'r') as myfile:
        new_data = json.load(myfile)
except:
    e = sys.exc_info()[0]
    print("NEW TALKS JSON ERROR: %s" % e)
    exit(0)

total_talks = len(all_talks)
print(total_talks, "talks crawled")
print("crawler: Done")

