#!/usr/bin/python3
import json
import string


Printable = dict.fromkeys(string.printable, 0)
CharExclusions = ["\"", "/", "\t", "\n"]



XDict = {}
with open('../Config/SPANISH.JSON','r') as fd:
    data  = json.load(fd)
    talks = data['talks']
    for talk in talks:
        title = talk['title']
        date = talk['date']
        speaker = talk['speaker']
        duration = talk['duration']

        if 'bruni' in speaker:
            speaker = "Bruni"
        key = date + speaker
        print(key)
        XDict[key] = title


with open('../Config/CONFIG00.JSON','r') as fd:
    data  = json.load(fd)

    talks = data['talks']
    for talk in talks:
        pdf = talk['pdf']
        url = talk['url']


MP3_HOST = data["config"]['URL_MP3_HOST']

print("{")
print("\t\"config\": {")
#print("\t\t\"URL_MP3_HOST\":\"https://audiodharma.us-east-1.linodeobjects.com/talks\",")
#print("\t\t\"USE_NATIVE_MP3PATHS\":\"true\",")
#print("\t\t\"MAX_TALKHISTORY_COUNT\":\"1999\"")
print("\t\t\"URL_MP3_HOST\":\"" + MP3_HOST + "\",")
print("\t\t\"USE_NATIVE_MP3PATHS\":true,")
print("\t\t\"MAX_TALKHISTORY_COUNT\":1999")
print("\t},")
print("\t\"talks\":[")

AllTalks = {}
talks = data['talks']
for talk in talks:
    url = talk['url']
    file_name = url.split("/")[-1]
    AllTalks[url] = True

    title = talk["title"]
    series = talk["series"]
    url = talk["url"]
    speaker = talk["speaker"]
    date = talk["date"]
    duration = talk["duration"]
    pdf = talk["pdf"]

    key = date + speaker
    if 'Castillo' in speaker:
        if key in XDict:
            title = XDict[key]
    if 'Bruni' in speaker:
        print("HERE")
        print(key)
        key = date + 'Bruni'
        if key in XDict:
            title = XDict[key]
            print(title)
    if 'Morillo' in speaker:
        if key in XDict:
            title = XDict[key]
            print(title)
    if 'Lorey' in speaker:
        if key in XDict:
            title = XDict[key]


        """
        print(old_title)
        print("\n")
        print(title)
        print("\n")
        """

    print("\t{")
    print("\t\t\"title\":\"" + title + "\",")
    print("\t\t\"series\":\"" + series +  "\",")
    print("\t\t\"url\":\"" + url + "\",")
    print("\t\t\"speaker\":\"" + speaker + "\",")
    print("\t\t\"pdf\":\"" + pdf + "\",")
    print("\t\t\"date\":\"" + date + "\",")
    print("\t\t\"duration\":\"" + duration + "\"")
    if talk != talks[-1]:
        print("\t},")
    else:
        print("\t}")

print("\t],")
print("\t\"albums\":[")

albums = data['albums']
for album in albums:
    section = album["section"]
    title = album["title"]
    content = album["content"]
    image = album["image"]
    print("\t{")
    print("\t\t\"section\":\"" + section + "\",")
    print("\t\t\"title\":\"" + title +  "\",")
    print("\t\t\"content\":\"" + content + "\",")
    if "talks" in album:
        print("\t\t\"image\":\"" + image + "\",")
    else:
        print("\t\t\"image\":\"" + image + "\"")
    if "talks" in album:
        talks = album["talks"]
        print("\t\t\"talks\":[")
        for talk in talks:
            section = series = ""
            if series in talk:
                series = talk["series"]
            if section in talk:
                section = talk["section"]
            title = talk["title"]
            url = talk["url"]

            print("\t\t{")
            if series != "":
                print("\t\t\t\"series\":\"" + series + "\",")
            if section != "":
                print("\t\t\t\"section\":\"" + section +  "\",")
            print("\t\t\t\"title\":\"" + title + "\",")
            print("\t\t\t\"url\":\"" + url + "\"")
            if talk != talks[-1]:
                print("\t\t},")
            else:
                print("\t\t}")

        print("\t\t]")
    if album != albums[-1]:
        print("\t},")
    else:
        print("\t}")

print("\t]")
print("}")
    
