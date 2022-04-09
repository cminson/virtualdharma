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



with open('./CONFIG00.JSON','r') as fd:
    data  = json.load(fd)

TalkDict = {}
AllTalks = []
RTalks = []
SortedAllTalks = []

talks = data['talks']
for talk in talks:
    AllTalks.append(talk)

SortedAllTalks = sorted(AllTalks, key=lambda talk: talk['date'], reverse=True)

for talk in AllTalks:
    url = talk["url"]
    fileName = url.rsplit('/', 1)[-1]
    TalkDict[fileName] = talk

#print(data['albums'][6]['talks'])
albumTalks = data['albums'][6]['talks']
for albumTalk in albumTalks:
    url = albumTalk["url"]
    fileName = url.rsplit('/', 1)[-1]

    if fileName not in TalkDict:
        print("Error Filename Not Found: " + fileName)
        continue
    talk = TalkDict[fileName] 
    RTalks.append(talk)

count = 0
for talk in RTalks:

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
    title = title.replace("Dharmettes:", "")
    title = title.replace("Dharmettes-", "")
    title = title.replace("Dharmette-", "")
    title = title.replace("Dharmette -", "")
    title = title.replace("Dharmette:", "")
    title = title.replace("Dharmettes", "")
    title = title.replace("Dharmette", "")
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

    
