#!/usr/bin/python
from __future__ import print_function
import urllib2
import os
import sys
import json
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
import string
from subprocess import call

Printable = dict.fromkeys(string.printable, 0)

CharExclusions = ["\"", "/", "\t", "\n"]

def cleanText(text):
    s  = ""
    for c in text:
        #if c in Printable and c != "\"" and c != "/":
        if c in CharExclusions:
            c = " "
        if c in Printable:
            s += c
    return s

def printDebug(s):
    if Debug1 == True:
        print(s)

CharExclusions = ["\"", "/", "\t"]


PList = []
matchTalk = "<td class=\"talk_title\">"

TARGET_BASE = sys.argv[1]

f = urllib2.urlopen(TARGET_BASE)
data = f.read()
data = data.replace("\r","")
data = data.replace("\n","")
idxStart = 0

while True:
    idxStart = data.find(matchTalk, idxStart)
    idxEnd = data.find(matchTalk, idxStart+len(matchTalk))
    s = data[idxStart: idxEnd]
    PList.append(s)
    #print(s)
    if idxStart == -1:
        break
    if idxEnd == -1:
        break
    idxStart = idxEnd


for para in PList:

    if len(para) < 10:
        continue
    #print(para)
    para = "<table><tr>" + para + "</tr></table>"
    soup = BeautifulSoup(para, "html.parser")
    for filter1 in soup.find_all('a'):
        link = filter1.get('href')
        if "mp3" in link:
            url = link;
            break

    soup = BeautifulSoup(para, "html.parser")

    tds = soup.find('td', {'class':'talk_length'})
    duration = tds.renderContents().strip()

    tds = soup.find('td', {'class':'talk_date'})
    date = tds.renderContents().strip()

    # extract title from td element
    tds = soup.find('td', {'class':'talk_title'})
    title = tds.renderContents().strip()
    idxEnd = title.find("<br", 0)
    if idxEnd != -1:
        title = title[0: idxEnd]
    print(title)

    # optional munging if divs and such are embedded in the title
    title_term = title.find('<', 0)
    if title_term != -1:
        title = title[0: title_term]
    if len(title) == 0:
        terms = url.split('-')
        title = terms[-1]
        title = title.replace(".mp3","")
        title = title.replace("_"," ")
    title = cleanText(title)

    # extract speaker from mp3 link.  link has form mp3path:speaker:place:title
    mp3LinkParts = url.split('-')
    name = mp3LinkParts[1]
    if '_' in name:
        firstNameLastName = name.split('_')
        speaker = firstNameLastName[0] + ' ' + firstNameLastName[1]
    else:
        speaker = name

    termParts = url.split('/')
    file_name = termParts[-1]

    # fixup for a common bug
    #url = url.replace("http://www.audiodharma.orghttp", "http")
    url = url.replace("http://www.audiodharma.org", "")
    print("\t\t{")
    print("\t\t\t\"series\":\"NA\",")
    print("\t\t\t\"title\":\"" + title.rstrip() + "\",")
    print("\t\t\t\"url\":\"" + url + "\",")
    print("\t\t},")


