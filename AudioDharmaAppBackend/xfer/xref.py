#!/usr/bin/python3
import json
import string
import requests, urllib


LIVE_CONFIG_FILE = '../Config/CONFIG00.JSON'
TOP_TALKS = '../Config/TOP200.JSON'

Headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36' }


XDict = {}
XList = []



def talkExists(url):

    try:
        code = requests.head(url, headers=Headers).status_code
    except  e:
        print("Error: ", url)
        exit()

    if code == 200:
        return True

    return False


count = 0
with open(LIVE_CONFIG_FILE,'r') as fd:
    data  = json.load(fd)
    root = data["config"]["URL_MP3_HOST"]
    talks = data['talks']
    for talk in talks:
        url = talk['url']
        title = talk["title"]
        filename = url.split("/")[-1]
        XDict[filename] =  talk

count = 0
with open(TOP_TALKS,'r') as fd:
    data  = json.load(fd)
    talks = data['talks']
    for talk in talks:
        title = talk["title"]
        url = talk["url"]
        filename = url.split("/")[-1]
        #print(filename)
        if filename not in XDict:
            print("ERROR:", filename)
            count += 1

        path = root + url
        print("Checking: ", path)
        if talkExists(path) == False:
            print("ERROR: ", url)

print("Count: ", count)




