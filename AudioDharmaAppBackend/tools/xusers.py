#!/usr/bin/python
import sys
import MySQLdb as mdb
#import mysqlclient as mdb
import json
import random
import operator
import datetime
import time

Users10 = []
Users30 = []
Users100 = []
DictDevices = {}
#
con = mdb.connect('localhost', 'cminson', 'ireland', 'ad')
cur = con.cursor()

query = "SELECT deviceID FROM actions";
print(query)
cur.execute(query)
rows = cur.fetchall()
allDevices = [i[0] for i in rows]
for device in allDevices:
    if device not in DictDevices:
        DictDevices[device] = 0
    DictDevices[device] += 1


ListDevices = list(DictDevices.items())
for device in ListDevices:
    if device[1] > 24:
        Users10.append(device)
    if device[1] > 30:
        Users30.append(device)
    if device[1] > 100:
        Users100.append(device)
    #print(device)


count = 0
for device in Users10:
    print(device)
    count += 1


print("Count:", count)


