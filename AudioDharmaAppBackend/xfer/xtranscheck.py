#!/usr/bin/python3
import json
import string
import requests, urllib


Printable = dict.fromkeys(string.printable, 0)
CharExclusions = ["\"", "/", "\t", "\n"]
Headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36' }
DEV_CONFIG_FILE = '../Config/DEV.JSON'
LIVE_CONFIG_FILE = '../Config/CONFIG00.JSON'

Found = 0
NotFound = 0
ListNotFound = []
FileNameExists = {}
TitleToFileName = {}


def talkExists(url):

    try:
        code = requests.head(url, headers=Headers).status_code
    except  e:
        print("Error: ", url)
        exit()

    if code == 200:
        return True

    return False

    

"""
with open(LIVE_CONFIG_FILE,'r') as fd:
    data  = json.load(fd)

    root = data['config']['URL_MP3_HOST']
    albums = data['albums']
    talks = data['talks']
    for talk in talks:
        url = talk['url']
        filename = url.split("/")[-1]
        TalkToURL[talk['title']] = url
"""


with open(DEV_CONFIG_FILE,'r') as fd:
    data  = json.load(fd)
    root = data["config"]["URL_MP3_HOST"]

    talks = data['talks']
    for talk in talks:
        new_title = talk['title']
        new_url = talk['url']
        filename = new_url.split("/")[-1]
        FileNameExists[filename] = True
        TitleToFileName[new_title] = filename


    #trancript talks
    transcript_album = data['albums'][7]
    count = 0
    for talk in transcript_album['talks']:
        old_url = "NA"
        new_url = "NA"
        old_title = talk['title']
        old_url = talk['url']
        old_filename = old_url.split("/")[-1]

        #filename hasnt changed
        if old_filename in FileNameExists:
            print("#CORRECT ", old_filename)
            continue
        
        if old_title in TitleToFileName:
            new_filename = TitleToFileName[old_title]
            print(old_title)
            print("rm {} ".format(old_filename))
            print("cp {} {}".format(old_filename, new_filename))
        else:
            print("ERROR Couldn't find title: ", old_title)

        count += 1

print("Total Transcript: ", count)



    
