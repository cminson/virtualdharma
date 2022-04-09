#!/usr/bin/python
import json
import urllib2
import sys


PATH_CONFIG = '/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG00.JSON'
AD_URL = "https://virtualdharma.org/AudioDharmaAppBackend/data/TALKS"


with open(PATH_CONFIG,'r') as fd:
    data  = json.load(fd)

AllTalks = []
AllErrors = []
talks = data['talks']
for talk in talks:
    url = talk['url']
    file_name = url.split('/')[-1]

    url = AD_URL + "/" + file_name
    AllTalks.append(url)

total_errors = 0
for url in AllTalks:
    try:
        f = urllib2.urlopen(url)
    except:
        print(url)
        total_errors += 1
        AllErrors.append(url)

total_talks = len(AllTalks)
print("total_talks: ", total_talks)
print("total_missing: ", total_errors)
    

