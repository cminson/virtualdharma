#!/usr/bin/python
import json



def minutesFromDuration(duration):

    hms  = duration.split(':')

    if len(hms) == 3:
        h = hms[0]
        m = hms[1]
    elif len(hms) == 2:
        h = 0
        m = hms[0]
    else:
        h = 0
        m = 0

    minutes = int(m) + 1
    minutes = (int(h) * 60) + minutes
    return minutes



with open('./DEV.JSON','r') as fd:
    data  = json.load(fd)

TalkDict = {}
AllTalks = []
SortedAllTalks = []

talks = data['talks']
for talk in talks:
    AllTalks.append(talk)

SortedAllTalks = sorted(AllTalks, key=lambda talk: talk['date'], reverse=True)

count = 0
for talk in SortedAllTalks:

    title = talk["title"]
    series = talk["series"]
    url = talk["url"]
    speaker = talk["speaker"]
    date = talk["date"]
    duration = talk["duration"]
    pdf = talk["pdf"]
    keys = talk["keys"]

    TalkDict[url] = True

    minutes = minutesFromDuration(duration)

    #
    # filters go here
    #
    #if minutes > 20: continue
    #if "Guided" in title: continue
    #if "Meditation" in title: continue
    if "Walking" in title:  continue
    if "Meditation" in title:  continue
    if "Reflections" in title:  continue
    if "Class" in title:  continue
    if "Practice" in title:  continue
    if "Morning" in title:  continue
    if "Continued" in title:  continue
    if len(title) < 8: continue
    #
    #
    #
    print("\t{")
    print("\t\t\"title\":\"" + title + "\",")
    print("\t\t\"series\":\"" + series +  "\",")
    print("\t\t\"url\":\"" + url + "\",")
    print("\t\t\"speaker\":\"" + speaker + "\",")
    print("\t\t\"pdf\":\"" + pdf + "\",")
    print("\t\t\"keys\":\"" + keys + "\",")
    print("\t\t\"date\":\"" + date + "\",")
    print("\t\t\"duration\":\"" + duration + "\"")
    print("\t},")

    count += 1

print("Count: " + str(count))

    
