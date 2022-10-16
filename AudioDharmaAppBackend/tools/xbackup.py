#!/usr/local/bin/python
import json
import urllib2
import time
from os import path


PATH_SOURCE = "http://audiodharma.us-east-1.linodeobjects.com/talks"
PATH_DEST = "./TALKS_BACKUP/"


def download_talk(path_source, path_dest):

    print("Downloading: {} to {}".format(path_source, path_dest))
    try:
        response = urllib2.urlopen(path_source)
    except IOError, e:
        print("ERROR NOT FOUND: {}".format(path_source))
        return

    data = response.read()
    f = open(path_dest, "w+")
    f.write(data)


fd = open('CONFIG00.JSON','r')
data  = json.load(fd)

talks = data['talks']
for talk in talks:
    url = talk['url']
    file_name = url.split("/")[-1]

    path_source = PATH_SOURCE + url
    path_dest = PATH_DEST + file_name

    if path.exists(path_dest):
        print("Skipping: {}".format(path_dest))
        continue

    download_talk(path_source, path_dest)
    print("sleeping ...")
    time.sleep(4.0)

