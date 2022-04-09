#!/usr/bin/python
import json


with open('../Config/CONFIG00.JSON','r') as fd:
    data  = json.load(fd)

AllTalks = {}
talks = data['talks']
for talk in talks:
    url = talk['url']
    if url in AllTalks:
        print("DUP SEEN: ", url)
        continue
    AllTalks[url] = True

    title = talk["title"]
    series = talk["series"]
    url = talk["url"]
    url_file_name = url.split("/")[-1]
    url = "/" + url_file_name
    url = url_file_name

    speaker = talk["speaker"]
    date = talk["date"]
    duration = talk["duration"]
    pdf = talk["pdf"]
    keys = talk["keys"]

    print("\t{")
    print("\t\t\"title\":\"" + title + "\",")
    print("\t\t\"series\":\"" + series +  "\",")
    print("\t\t\"url\":\"" + url + "\",")
    print("\t\t\"speaker\":\"" + speaker + "\",")
    print("\t\t\"pdf\":\"" + pdf + "\",")
    print("\t\t\"keys\":\"" + keys + "\",")
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
            series = talk["series"]
            section = talk["section"]
            title = talk["title"]
            url = talk["url"]
            url_file_name = url.split("/")[-1]
            url = "/" + url_file_name
            url = url_file_name

            print("\t\t{")
            print("\t\t\t\"series\":\"" + series + "\",")
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
    
