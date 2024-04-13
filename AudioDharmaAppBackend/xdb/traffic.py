#!/usr/bin/python
import sys
import cgi
import MySQLdb as mdb

#sudo apt-get install mysql-server
#sudo apt-get install python-pip python-dev libmysqlclient-dev
#sudo apt install python-pip
#sudo apt-get install mysql-server
#pip install MySQL-python


AllTalks = []

try:
    con = mdb.connect('localhost', 'cminson', 'ireland', 'ad');
    cur = con.cursor()

    query = "select * from ops"
    cur.execute(query)
    rows = cur.fetchall()

    count_android = 0
    count_iphone = 0
    count_alexa = 0
    count_total = 0
    for row in rows:
        AllTalks.append(row)
        device_type = row[4]
        if device_type == 'alexa':
            count_alexa += 1
        elif device_type == 'iphone':
            count_iphone += 1
        elif device_type == 'android':
            count_android += 1
        
    count_total = count_alexa + count_iphone + count_android
    print("total: %d  android: %d %0.2f  iphone: %d %0.2f  alexa: %d %0.2f" % (count_total, 
        count_android, 
        (float(count_android) / count_total) * 100, 
        count_iphone, 
        (float(count_iphone) / count_total) * 100, 
        count_alexa, 
        (float(count_alexa) / count_total) * 100 ))

    AndroidDeviceCount = {}
    for talk in AllTalks:
        deviceID = talk[2]
        deviceType = talk[4]
        if deviceType != 'iphone' or deviceType != 'iPhone': 
            if deviceID  in AndroidDeviceCount:
                AndroidDeviceCount[deviceID] += 1
            else:
                AndroidDeviceCount[deviceID] = 1


    talkcounts = []
    for key, value in AndroidDeviceCount.iteritems():
        talkcounts.append(value)
    list.sort(talkcounts)
    talkcounts.reverse()
    high_talkcounts  = [talkcount for talkcount in talkcounts if talkcount > 10]


    print(high_talkcounts)
    print(len(high_talkcounts))


except mdb.Error, e:
    error = "Error %d: %s" % (e.args[0],e.args[1])
    print(error)
    sys.exit(1)

finally:
    print("stats ok")


