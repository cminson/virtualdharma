#!/usr/bin/python
import json
import sys
import MySQLdb as mdb


PATH_CONFIG = '/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG00.JSON'
PATH_WEB_CONFIG = '/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/ALLTALKS_WEB.JSON'
#PATH_ALL_TALKS = '/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/ALL_NATIVE_TALKS.txt'


with open(PATH_WEB_CONFIG) as fd:
    web_config  = json.load(fd)

with open(PATH_CONFIG,'r') as fd:
    config  = json.load(fd)

DictConfigTalks = {}
DictWebConfigTalks = {}
ListConfigTalks = []
ListWebConfigTalks = []

total_talks = 0
for talk in config['talks']:
    url = talk['url']
    DictConfigTalks[url] = True
    ListConfigTalks.append(talk)
    
total = len(DictConfigTalks)

for talk in  web_config['talks']:
    url = talk['url']
    DictWebConfigTalks[url] = True
    ListWebConfigTalks.append(talk)

found = missing = 0
for talk in config['talks']:
    url = talk['url']

    if url in DictWebConfigTalks:
        found += 1
    else:
        missing += 1
        print("Missing: ", url)


print("Found: ", found)
print("Missing: ", missing)
print("Total: ", total)


for i in range(0, len(ListWebConfigTalks) - 1):
    #talk_config = ListConfigTalks[i]
    talk_web = ListWebConfigTalks[i]

    #url_config = talk_config['url']
    url_web = talk_web['url']
    #print(url_config)
    print(i + 1,url_web)
    #print("\n")


print("done")

"""
with open(PATH_ALL_TALKS) as fd:
    all_talks = fd.readlines()

ConfigTalks = {}
DatabaseTalks = {}
talks = config_talks['talks']

for talk in talks:
    url = talk['url'].rstrip()
    #print(url)
    ConfigTalks[url] = True


missing = found =  0
for talk in all_talks:

    parts = talk.split("/")
    url = parts[-1].rstrip()
    talk_id = parts[-2]

    if 'IRC' in url: continue
    if url in ConfigTalks:
        found += 1
    else:
        missing += 1
        print("Missing: ", url)



print("Found: ", found)
print("Missing: ", missing)
print("done")

"""


    
    
