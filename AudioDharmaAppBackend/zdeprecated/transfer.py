#!/usr/bin/python
import json
import urllib2
import sys
import os
from shutil import copyfile

PATH_CONFIG = '/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG00.JSON'
URL_SOURCE = "https://virtualdharma.org/AudioDharmaAppBackend/data/TALKS"
URL_DEST = "https://virtualdharma.org/AudioDharmaAppBackend/data/NEWTALKS"


with open(PATH_CONFIG,'r') as fd:
    data  = json.load(fd)

AllTalks = []
AllErrors = []
talks = data['talks']
for talk in talks:
    url = talk['url']
    file_name = url.split('/')[-1]
    talk_id = url.split('/')[-2]

    url_source = URL_SOURCE + "/" + file_name
    url_dir = URL_DEST + "/" + talk_id
    url_dest = URL_DEST + url

    if os.path.isdir(url_dir) == False:
        print(url_dir, url_source, url_dest)
        #os.mkdir(url_dir)
        #copyfile(url_source, url_dest)

    print("Source: ", url_source, "Dest: ", url_dest)

    

