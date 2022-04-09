#!/usr/bin/python
import json
import string
import requests, urllib, urllib2


Printable = dict.fromkeys(string.printable, 0)
CharExclusions = ["\"", "/", "\t", "\n"]
Headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36' }
DEV_CONFIG_FILE = '../Config/DEV.JSON'
LIVE_CONFIG_FILE = '../Config/CONFIG00.JSON'

Found = 0
NotFound = 0
ListNotFound = []
TalkToURL = {}


def talkExists(url):

    try:
        code = requests.head(url, headers=Headers).status_code
    except IOError, e:
        print("Error: ", url)
        exit()

    if code == 200:
        return True

    return False

    

CorrectFileName = {}
with open(LIVE_CONFIG_FILE,'r') as fd:
    data  = json.load(fd)

    root = data['config']['URL_MP3_HOST']
    albums = data['albums']
    talks = data['talks']
    for talk in talks:
        url = talk['url']
        filename = url.split("/")[-1]
        TalkToURL[talk['title']] = url



with open(DEV_CONFIG_FILE,'r') as fd:
    data  = json.load(fd)
    root = data["config"]["URL_MP3_HOST"]

    talks = data['talks']
    for talk in talks:
        title = talk['title']
        url = talk['url']
        filename = url.split("/")[-1]
        CorrectFileName[filename] = True


    #trancript talks
    transcript_album = data['albums'][7]
    count = 0
    old_url = "NA"
    new_url = "NA"
    for talk in transcript_album['talks']:
        title = talk['title']
        old_url = talk['url']
        old_filename = old_url.split("/")[-1]
        #print("X", title, old_url, old_filename)

        if old_filename not in CorrectFileName:
            if title in TalkToURL:
                new_url = TalkToURL[title]
                print("new_url found")

            print("NO TRANSCRIPT FILE MATCH: ")
            print(title)
            print("OLD: ",old_url)
            print("NEW: ",new_url)

        count += 1

print("Total Transcript: ", count)



    
