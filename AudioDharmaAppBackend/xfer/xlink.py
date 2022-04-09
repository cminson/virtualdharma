#!/usr/bin/python3
import json
import string
import requests, urllib


DATAFILE = "./data"

fd = open(DATAFILE,'r')
lines = fd.readlines()
for line in lines:
    if 'mp3' in line:
        start = line.index("objects")
        end = line.index(".mp3")
        s = line[start+17:end+4]
        print(s)




