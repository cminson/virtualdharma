#!/usr/bin/python3
import sys
import os
import time
import datetime
import MySQLdb as mdb

IP= "85.76.78.47"
DEVICE_ID = "999-999"
DEVICE_TYPE = "999-999"
DATE = "{:%Y-%m-%d}".format(datetime.date.today())
TIME = time.time()

count = len(sys.argv)
if count != 5:
    print('xgenrecord: operation filename city country')
    exit()
operation = sys.argv[1]
filename = sys.argv[2]
city = sys.argv[3]
country = sys.argv[4]

if operation != 'SHARETALK' and operation != 'PLAYTALK':
    print('xgenrecord: unrecognized operation.  must be SHARETALK or PLAYTALK')
    exit()

try:
    con = mdb.connect('localhost', 'cminson', 'ireland', 'ad');
    cur = con.cursor()
    query = "INSERT INTO actions (ip, deviceID, operation, devicetype,  filename, date, seconds, city, country) VALUES (%s, %s, %s,  %s,  %s, %s, %s, %s, %s)"
    values = (IP, DEVICE_ID, operation, DEVICE_TYPE, filename, DATE, TIME, city, country)
    print(query)
    #print(values)
    cur.execute(query, values)
    con.commit()

except:
    print("error")
    sys.exit(1)

finally:
    print("Success: record inserted")


