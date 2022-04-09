#!/usr/bin/python
from __future__ import print_function
import os
import sys
import string
import json

CONFIG_PATH = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/"

len = len(sys.argv)
if len != 3:
    print("usage: index.py CONFIG index")
    sys.exit(1)

config = sys.argv[1]
index = int(sys.argv[2])

path = CONFIG_PATH + config
try:
    with open(path,'r') as fd:
        data  = json.load(fd)
except IOError, e:
    error = "Error %d: %s" % (e.args[0],e.args[1])
    print(error)
    sys.exit(1)

all_talks = data['talks']
talk = all_talks[index]
print(talk['title'])
print(talk['url'])

