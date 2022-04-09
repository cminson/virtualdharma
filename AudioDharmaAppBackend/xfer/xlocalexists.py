#!/usr/bin/python3
import json
import os
from urllib.request import urlopen


PATH_CONFIG = '../Config/CONFIG00.JSON'
PATH_TALKS = '../data/TALKS/'

PATH_LOCAL_MP3CACHE = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/data/TALKS/"
PATH_MP3_SOURCE = 'https://audiodharma.us-east-1.linodeobjects.com/talks'



XDict = {}
LocalDict = {}
TalksList = []


ListTalks = os.listdir(PATH_TALKS)
for filename in ListTalks:
    LocalDict[filename] = True
    

with open(PATH_CONFIG,'r') as fd:
    data  = json.load(fd)
    talks = data['talks']
    for talk in talks:
        url = talk['url']
        filename = url.split("/")[-1]
        #print(filename)
        XDict[filename] = True
        if filename not in LocalDict:
            print("Missing: ", url)

            source_path = PATH_MP3_SOURCE + url
            dest_path = PATH_LOCAL_MP3CACHE + filename
            print("Downloading: ", source_path, "to: ", dest_path)
            try:
                response = urlopen(source_path)
            except:
                print("ERROR NOT FOUND: ", source_path)
                continue
            data = response.read()
            f = open(dest_path, "wb")
            f.write(data)




