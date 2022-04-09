#!/usr/bin/python
import json
import os

if "virtualdharma" in os.path.abspath(__file__):
    CONFIG_PATH= "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG00.JSON"
else:
    CONFIG_PATH = "/home/httpd/vhosts/ezimba/httpdocs/AudioDharmaAppBackend/Config/CONFIG00.JSON"


MissingTalks = []
CurrentTalks = []
AllTalks = []
AllWords = {}

StopWords = ['the', 'and', 'this', 'that', 'with', 'you', 'del', 'los', 'are', 'one', 'two', 'three', 'four', 'five',
        'six', 'seven', 'eight', 'nine', 'ten', 'lay', 'they', 'them', 'when', 'day', 'see', 'has', 'its', 'can',
        'yes', 'too', 'iii', 'not', 'las', 'how', 'from', 'cautro', 'our', 'for', 'pt.', 'pt1', 'pt2', 'pt3', 'pt4']

with open(CONFIG_PATH,'r') as fd:
    data  = json.load(fd)
talks = data['talks']
for talk in talks:
    AllTalks.append(talk)

for talk in AllTalks:
    title = talk["title"]
    series = talk["series"]
    words = title.split()
    for word in words:
        if word.lower() in StopWords:
            continue
        if len(word) < 3: continue
        if word in AllWords:
            AllWords[word]  += 1
        else:
            AllWords[word] = 1

SortedWords = sorted(AllWords.iteritems(), key=lambda (k,v): (v,k))
for word in SortedWords:
    print(word)


#AllTalks = MissingTalks + CurrentTalks
#SortedAllTalks = sorted(AllTalks, key=lambda talk: talk['date'], reverse=True)

    #print("\t{")
    #print("\t\t\"title\":\"" + title + "\",")
    #print("\t\t\"series\":\"" + series +  "\",")
    #print("\t\t\"url\":\"" + url + "\",")
    #print("\t\t\"speaker\":\"" + speaker + "\",")
    #print("\t\t\"date\":\"" + date + "\",")
    #print("\t\t\"duration\":\"" + duration + "\"")
    #print("\t},")

    
