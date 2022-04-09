#!/usr/bin/python
import sys
import MySQLdb as mdb

MatchingTalks = []

len = len(sys.argv)
if len != 3:
    print("usage: xchangefilenamne.py oldfilename newfilename")
    sys.exit(1)

old_filename = sys.argv[1]
new_filename = sys.argv[2]

try:
    con = mdb.connect('localhost', 'cminson', 'ireland', 'ad');
    cur = con.cursor()
    query = "update ops set filename=\"%s\" where filename=\"%s\"" % (new_filename, old_filename)
    print(query)
    cur.execute(query)
    con.commit()

except: 
    e = sys.exc_info()[0]
    print("Error: %s" % e)
    sys.exit(1)

print("done")



    
