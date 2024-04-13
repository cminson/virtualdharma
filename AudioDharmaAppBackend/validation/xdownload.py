#!/usr/bin/python
import json
import sys
import urllib2

len = len(sys.argv)
if len != 2:
    print("usage: xdownload.py talk_id_filename")
    exit(1)

URL_ROOT = 'https://audiodharma.us-east-1.linodeobjects.com/talks/'
PATH_DEST_MP3 = '/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/data/TALKS/'

talk_id_filename = sys.argv[1]
filename = talk_id_filename.split('/')[-1]
path_source = URL_ROOT + talk_id_filename
path_dest = PATH_DEST_MP3 + filename

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

    

#
