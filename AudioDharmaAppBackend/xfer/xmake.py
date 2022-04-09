#!/usr/bin/python3
import json
import string
import requests, urllib


DEV_CONFIG_FILE = '../Config/DEV.JSON'
LIVE_CONFIG_FILE = '../Config/CONFIG00.JSON'

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
    print("Root: ", root)
    talks = data['talks']
    for talk in talks:
        url = talk['url']
        filename = url.split("/")[-1]
        XDict[filename] =  talk



    albums = data['albums']
    for album in albums:
        if album["content"] == "TOPTALKS":
            talks = album["talks"]
            for talk in talks:
                url = talk["url"]
                filename = url.split("/")[-1]

                if filename not in XDict:
                    print("No Match:", filename)
                    continue
                reftalk = XDict[filename]
                reftalk['title'] = talk["title"]
                reftalk['series'] = talk["series"]
                XList.append(reftalk)


for talk in XList:

    series = talk['series']
    title = talk['title']
    url = talk['url']
    print("\t{")
    print("\t\t\"series\":\"" + series +  "\",")
    print("\t\t\"section\":\"" + "_"  +  "\",")
    print("\t\t\"title\":\"" + title + "\",")
    print("\t\t\"url\":\"" + url + "\",")
    print("\t},")




