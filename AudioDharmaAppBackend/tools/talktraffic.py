#!/usr/bin/python
import sys
import MySQLdb as mdb

MatchingTalks = []
ScoreDict = {}

SCORE_PLAYED = 1
SCORE_SHARED = 5


len = len(sys.argv)
if len != 2:
    print("usage: talktraffic.py filename")
    sys.exit(1)

filename = sys.argv[1]

def scoreTalk(filename, score):

    if filename in ScoreDict:
        ScoreDict[filename] += score
    else:
        ScoreDict[filename] = score


try:
    con = mdb.connect('localhost', 'cminson', 'ireland', 'ad');
    cur = con.cursor(mdb.cursors.DictCursor)
    query = "select date, operation, city, country  from ops where filename=\"%s\"" % (filename)
    cur.execute(query)
    MatchingTalks = cur.fetchall()

except: 
    e = sys.exc_info()[0]
    print("Error: %s" % e)
    sys.exit(1)

count = 0
score = 0
for talk in MatchingTalks:
    count += 1
    operation = talk['operation']
    if operation == 'PLAYTALK': score += SCORE_PLAYED
    if operation == 'SHARETALK': score += SCORE_SHARED
    print('{} {} {} {}'.format(talk['date'], talk['operation'], talk['city'], talk['country']))

print('Count: {}   Score: {}'.format(count, score))
    




    
