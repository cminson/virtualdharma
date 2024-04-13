#!/usr/bin/python
import sys
import MySQLdb as mdb
#import mysqlclient as mdb
import json
import random
import operator
import datetime
import time




PATH_CONFIG_JSON = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG00.JSON"
ListTranscriptTalks = []

ListAllTalks = []

#
# Main
#
try:
    with open(PATH_CONFIG_JSON,'r') as fd:
        Config  = json.load(fd)
        for talk in Config['talks']:
            transcript = talk['pdf']
            ListAllTalks.append(talk)
            if len(transcript) > 20:
                ListTranscriptTalks.append(talk)

except e:
    error = "Error %d: %s" % (e.args[0],e.args[1])
    print(error)
    sys.exit(1)


totalCount = 0
try:
    con = mdb.connect('localhost', 'cminson', 'ireland', 'ad')
    cur = con.cursor()

except mdb.Error, e:
    error = "Error %d: %s" % (e.args[0],e.args[1])
    print(error)
    sys.exit(1)

print("Transcript Talks")
for talk in ListTranscriptTalks:

    fileName = talk['url'].rsplit('/', 1)[-1]
    query = "SELECT count(*)  FROM actions WHERE fileName=\"{}\" AND date>=\"2021.01.01\"".format(fileName)
    #print(query)
    cur.execute(query)
    row = cur.fetchone()
    v = row[0]
    totalCount += v
    #print(totalCount)
    #print(fileName, v)

print(totalCount)

#exit()


print("All Talks")
totalCount = 0
try:
    con = mdb.connect('localhost', 'cminson', 'ireland', 'ad')
    cur = con.cursor()

except mdb.Error, e:
    error = "Error %d: %s" % (e.args[0],e.args[1])
    print(error)
    sys.exit(1)

for talk in ListAllTalks:

    fileName = talk['url'].rsplit('/', 1)[-1]
    query = "SELECT count(*)  FROM actions WHERE fileName=\"{}\" AND date>=\"2021.01.01\"".format(fileName)
    #print(query)
    cur.execute(query)
    row = cur.fetchone()
    v = row[0]
    totalCount += v
    print(fileName, v)


print(totalCount)
print("Done")


