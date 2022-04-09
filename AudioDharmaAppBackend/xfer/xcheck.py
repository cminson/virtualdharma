#!/usr/bin/python3
import json
import string
import requests, urllib


DEV_CONFIG_FILE = '../Config/DEV.JSON'
LIVE_CONFIG_FILE = '../Config/CONFIG00.JSON'


ConfigDictPDF = {}
DevDictPDF = {}

with open(LIVE_CONFIG_FILE,'r') as fd:
    data  = json.load(fd)

    albums = data['albums']
    talks = data['talks']
    for talk in talks:
        title = talk['title']
        url = talk['url']
        pdf = talk['pdf']
        if 'virtual' in pdf:
            filename = pdf.split("/")[-1]
            ConfigDictPDF[filename] = url

with open(DEV_CONFIG_FILE,'r') as fd:
    data  = json.load(fd)

    albums = data['albums']
    talks = data['talks']
    for talk in talks:
        title = talk['title']
        url = talk['url']
        pdf = talk['pdf']
        if 'virtual' in pdf:
            filename = pdf.split("/")[-1]
            DevDictPDF[filename] = url


count = 0
for pdf in ConfigDictPDF:
    url = ConfigDictPDF[pdf]
    if pdf not in DevDictPDF:
        count += 1
        print(pdf)
        print(url)
        print("\n")

print("Missing Count: ", count)
