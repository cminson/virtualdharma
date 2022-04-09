#!/usr/bin/python
import json

FILE = "./CONFIG00.JSON"
with open(FILE,'r') as fd:
    lines = fd.readlines()

for line in lines:
    line  = line[:-1]
    if "&amp;" in line:
        line = line.replace("&amp;", "&")
    print(line)


    
