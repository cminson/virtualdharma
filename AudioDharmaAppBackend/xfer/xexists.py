#!/usr/bin/python
import json
import string
import requests, urllib, urllib2


Printable = dict.fromkeys(string.printable, 0)
CharExclusions = ["\"", "/", "\t", "\n"]
Headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36' }
CONFIG_FILE = '../Config/CONFIG00.JSON'

Found = 0
NotFound = 0
ListNotFound = []


def talkExists(url):

    try:
        code = requests.head(url, headers=Headers).status_code
    except IOError, e:
        print("Error: ", url)
        exit()

    if code == 200:
        return True

    return False

    

with open(CONFIG_FILE,'r') as fd:
    data  = json.load(fd)
    root = data["config"]["URL_MP3_HOST"]
    print("Root: ", root)

    talks = data['talks']
    for talk in talks:
        title = talk['title']
        url = talk['url']
        filename = url.split("/")[-1]
        print(filename)
        #url = filename

        found = talkExists(root + url)

        if found:
            Found += 1
            print("FOUND: ", root + url)
        else:
            print("ERROR")
            NotFound += 1
            ListNotFound.append(talk)


print("Found: ", Found)
print("NotFound: ", NotFound)
print("\nList of Not Found Talks")
for talk in ListNotFound:
    print(talk['title'])
    print(talk['url'])
    print("\n")
    
