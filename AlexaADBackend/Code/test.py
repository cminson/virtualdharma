#!/usr/bin/python

from __future__ import print_function
import urllib
import httplib
import urllib2
import json


Duration = "1:23:42"

def reportActivity(currentUserID, currentTalkURL):
    global AD_SITE
    global AD_REPORT_ACTIVITY

    print("reportActivity: " + AD_SITE + AD_REPORT_ACTIVITY)

    fileName = currentTalkURL.rsplit('/', 1)[-1]

    params = urllib.urlencode({'USERID': currentUserID, 'FILENAME': fileName})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection(AD_SITE)
    conn.request("POST", AD_REPORT_ACTIVITY, params, headers)
    response = conn.getresponse()


def minutesFromDuration(duration):

    hms  = duration.split(':')

    if len(hms) == 3:
        h = hms[0]
        m = hms[1]
    elif len(hms) == 2:
        h = 0
        m = hms[0]

    minutes = int(m) + 1
    minutes = (int(h) * 60) + minutes
    return str(minutes)


minutes = minutesFromDuration("03:23:00")
print(minutes)
