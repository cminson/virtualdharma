#!/usr/bin/python
import json
import sys
import urllib2


JSON_TOP200 = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP200.JSON"
URL_ROOT = 'https://audiodharma.us-east-1.linodeobjects.com/talks/'
PATH_DEST_MP3 = '/var/www/virtualdharma/httpdocs/transcripts/data/mp3/'


ALL_URLS = []



def download(path_source, path_dest):

    print("Downloading: ", path_source, "to: ", path_dest)
    try:
        response = urllib2.urlopen(path_source)
    except IOError, e:
        print("ERROR NOT FOUND: ", path_source)
        exit()

    data = response.read()
    f = open(path_dest, "w+")
    f.write(data)
    print("Written: ", path_dest)

    
fd = open(JSON_TOP200,'r')
data  = json.load(fd)

AllTalks = {}
talks = data['talks']
for talk in talks:
    url = talk['url']
    ALL_URLS.append(url)


count = 0
for url in ALL_URLS:
     
    path_source = URL_ROOT + url
    file_name = url.split("/")[-1]
    path_dest  = PATH_DEST_MP3 + file_name
    print(path_source, path_dest)
    download(path_source, path_dest)
    count += 1
    if count > 200: break

#
