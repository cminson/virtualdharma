#!/usr/bin/python3
import json
import sys
import os
import os.path
from os import path

PATH_CONFIG = '/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG01.JSON'
PATH_CONFIG = '/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG00.JSON'
PATH_TALKS = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/data/TALKS/"


with open(PATH_CONFIG,'r') as fd:
    data  = json.load(fd)

AllTalks = []
AllErrors = []
talks = data['talks']
count = 0
for talk in talks:
    url = talk['url']
    file_name = url.split('/')[-1]
    path_mp3 = PATH_TALKS + file_name

    if path.exists(path_mp3) == False:
        print(path_mp3)
        count += 1

print("Missing Files: ", count)

    

