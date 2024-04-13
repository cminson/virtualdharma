#!/usr/bin/python
import json
import urllib2
import sys
import os
import os.path
from os import path

PATH_CONFIG = '/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG00.JSON'
DictTalks = {}


with open(PATH_CONFIG,'r') as fd:
    data  = json.load(fd)

talks = data['talks']
albums = data['albums']
for talk in talks:
    url = talk['url']
    DictTalks[url] = talk

for album in albums:
    if 'talks' not in album: continue

    #print(album)
    talks = album['talks']
    for talk in talks:
        url = talk['url']
        print(url)
        if url not in DictTalks:
            print("Config Not Valid!")
            print("Missing: ", url)
            exit()

print("Config Valid")

    

