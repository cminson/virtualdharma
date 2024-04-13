#!/usr/bin/python
import json
import sys

len = len(sys.argv)
if len != 2:
    print("usage: xdups.py filename")
    sys.exit(1)

json_file = sys.argv[1]
with open(json_file,'r') as fd:
    data  = json.load(fd)

AllTalks = {}
talks = data['talks']
for talk in talks:
    url = talk['url']
    filename = url.split('/')[-1]
    #print(url)
    if filename in AllTalks:
        print("DUP: " + filename)
        continue
    AllTalks[filename] = True

    
