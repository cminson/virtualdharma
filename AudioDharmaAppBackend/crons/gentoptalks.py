#!/usr/bin/python3
import sys
import MySQLdb as mdb
#import mysqlclient as mdb
import json
import random
import operator
import datetime
import time

#
# these configs are read and used by this program
#
PATH_CONFIG_JSON = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG00.JSON"
PATH_RCOMMENDED_TALKS = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/RECOMMENDED.JSON"
PATH_CHRISTOPHER_TALKS = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CHRISTOPHER.JSON"
PATH_REJECT_TALKS = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/REJECTS.JSON"

#
# these configs get generated in this program
#
PATH_TOPALLTIME_TALKS = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP200.JSON"
PATH_TOP90DAYS_TALKS = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP90DAYS.JSON"
PATH_TOP2DAYS_TALKS = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/TOP2DAYS.JSON"

ScoreDict = {}
FileNameToTalk = {}
RecommendedTalks = []
ChristopherTalks = []
RejectTalks = []

SCORE_PLAYED = 1
SCORE_SHARED = 3
SCORE_RECOMMENDED = 200
SCORE_CHRISTOPHER = 500
SCORE_NON_GIL_LONG = 420
SCORE_NON_GIL_MEDIUM = 2
SCORE_NON_GIL_SHORT = 4

DAY_RANGE = 80
DAY_IN_SECONDS =  24 * 60 * 60
DAYS2_IN_SECONDS =  2 * 24 * 60 * 60
DAYS90_IN_SECONDS = DAY_RANGE * 24 * 60 * 60

MAX_TALKS = 2000
MAX_TALKS_2DAY = 10
MAX_TALKS_90DAY = 20

TopTalksAllTime = []
TopTalks90Days = [] 
TopTalks2Days  = []

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def removeNonAscii(text):
    return ''.join(i for i in text if ord(i)<128)

def generateJSONFile(path_json_file, talks):

    print(len(talks))
    talks = [talk for talk in talks if talk[0] in FileNameToTalk]
    print(len(talks))

    count = 1
    with open(path_json_file,'w+') as fd:
        fd.write("{\n")
        fd.write("\"talks\": [\n")
        #for i in range(len(talks)):
        for scored_talk in talks:

            #scored_talk = talks[i]
            #count_str = "{0:03d}".format(count)
            filename = scored_talk[0]
            count_str = "{}.".format(count)
            score = str(scored_talk[1])
            if filename not in FileNameToTalk:
                print('NOT SEEN IN CONFIG: ', filename)
                continue

            url = FileNameToTalk[filename]['url']
            title = count_str + " " + FileNameToTalk[filename]['title']
            title = removeNonAscii(title)

            # DEBUG DEV CJM
            """
            if is_ascii(title) == False:
                continue
                print("NOT ASCII")
            print(title)
            """
            
            fd.write("{\n")
            #test = unicode("\t\"title\" : \"" + title + "\",\n")
            #fd.write(test)
            fd.write("\t\"title\" : \"" + title + "\",\n")
            fd.write("\t\"url\" : \"" + url + "\",\n")
            fd.write("\t\"series\" : \"\",\n")
            fd.write("\t\"score\" : " + score + "\n")

            if scored_talk != talks[-1]:
                fd.write("},\n")
            else:
                fd.write("}\n")

            count += 1

        fd.write("]\n")
        fd.write("}\n")


def scoreTalk(scoredict, filename, score):

    if filename in scoredict:
        scoredict[filename] += score
    else:
        scoredict[filename] = score



#
# Main
#
# Read in all configurations.
#
# Compute:
#
#   Most popular talks alltime
#   Most popular talks last 90 days
#   Most popular talks last 2 days
#
# Output results to JSON files in CONFIG directory
#
try:
    with open(PATH_CONFIG_JSON,'r') as fd:
        Config  = json.load(fd)
        for talk in Config['talks']:
            filename = talk['url'].rsplit('/', 1)[-1]
            FileNameToTalk[filename] = talk

except e:
    sys.exit(1)

try:
    with open(PATH_RCOMMENDED_TALKS,'r') as fd:
        RecommendedTalks  = json.load(fd)
except:
    sys.exit(1)

try:
    with open(PATH_CHRISTOPHER_TALKS,'r') as fd:
        ChristopherTalks  = json.load(fd)
except:
    sys.exit(1)



#
# find top talks for all time
# output to json
#
try:
    con = mdb.connect('localhost', 'cminson', 'ireland', 'ad')
    cur = con.cursor()

    query = "SELECT filename FROM actions WHERE operation=\"PLAYTALK\""
    print(query)
    cur.execute("SELECT filename FROM actions WHERE operation=\"PLAYTALK\"")
    #cur.execute(query)
    rows = cur.fetchall()
    talks_played = [i[0] for i in rows]

    query = "SELECT filename FROM actions WHERE operation=\"SHARETALK\""
    cur.execute(query);
    rows = cur.fetchall()
    talks_shared = [i[0] for i in rows]

    scoredict = {}
    for filename in talks_played:
        scoreTalk(scoredict, filename, SCORE_PLAYED)

    for filename in talks_shared:
        scoreTalk(scoredict, filename, SCORE_SHARED)

    long_tail = ['2014', '2013', '2012', '2011',
            '2010', '2009', '2008', '2007',
            '2006', '2005', '2004', '2002'
            '2001', '2000']
    for filename, score in scoredict.items():

        if filename in RecommendedTalks:
            scoredict[filename] += SCORE_RECOMMENDED
        if filename in ChristopherTalks:
            scoredict[filename] += SCORE_CHRISTOPHER
        if '2017' in filename:
            scoredict[filename] += 160
        if '2016' in filename:
            scoredict[filename] += 220
        if 'Gil' not in filename:
            scoredict[filename] += SCORE_NON_GIL_LONG

        for year in long_tail:
            if year in filename:
                scoredict[filename] += 240



    #
    # sort and output them to json
    #
    for filename, score in scoredict.items():
        if filename in RejectTalks: 
            print("REJECTED: ", filename)
            continue
        TopTalksAllTime.append((filename, score))
    TopTalksAllTime = sorted(TopTalksAllTime, key=lambda tup: tup[1], reverse = True)
    TopTalksAllTime = TopTalksAllTime[0: MAX_TALKS]
    con.close()

except:
    sys.exit(1)



#
# find 2-day and 90-day talk trending data
# output to JSON
#
start_date = (datetime.date.today() - datetime.timedelta(DAY_RANGE)).strftime('%Y-%m-%d')
try:
    con = mdb.connect('localhost', 'cminson', 'ireland', 'ad')
    cur = con.cursor(mdb.cursors.DictCursor)

    #
    # get 2-day trending data
    #
    seconds = int(time.time()) - DAYS2_IN_SECONDS
    query = "SELECT filename FROM actions WHERE operation=\"PLAYTALK\" AND seconds >= \"{}\"".format(seconds)
    cur.execute(query);
    talks_played_2Day = cur.fetchall()

    query = "SELECT filename FROM actions WHERE operation=\"SHARETALK\" AND seconds >= \"{}\"".format(seconds)
    cur.execute(query);
    talks_shared_2Day = cur.fetchall()


    # 
    # now get 3-month trending data
    # 
    seconds = int(time.time()) - DAYS90_IN_SECONDS
    query = "SELECT * FROM actions WHERE operation=\"PLAYTALK\" AND seconds >= \"{}\"".format(seconds)
    cur.execute(query)
    talks_played_90Day = cur.fetchall()
    talks_played_90Day = [talk for talk in talks_played_90Day if talk['filename'] in FileNameToTalk]

    query = "SELECT * FROM actions WHERE operation=\"SHARETALK\" AND seconds >= \"{}\"".format(seconds)
    cur.execute(query)
    talks_shared_90Day = cur.fetchall()
    talks_shared_90Day = [talk for talk in talks_shared_90Day if talk['filename'] in FileNameToTalk]
    con.close()


except:
    sys.exit(1)


# compute 2-day trending data
scoredict = {}
for talk in talks_played_2Day:
    scoreTalk(scoredict, talk['filename'], SCORE_PLAYED)
for talk in talks_shared_2Day:
    scoreTalk(scoredict, talk['filename'], SCORE_SHARED)
for talk in talks_played_2Day:
    if 'Gil' not in talk['filename']:
        scoreTalk(scoredict, talk['filename'], SCORE_NON_GIL_SHORT)

for filename, score in scoredict.items():
    if filename not in FileNameToTalk:
        continue
    TopTalks2Days.append((filename, score))
    TopTalks2Days = sorted(TopTalks2Days, key=lambda tup: tup[1], reverse = True)
    TopTalks2Days = TopTalks2Days[0: MAX_TALKS_2DAY]

# compute 90-day trending data
scoredict = {}
for talk in talks_played_90Day:
    scoreTalk(scoredict, talk['filename'], SCORE_PLAYED)
for talk in talks_shared_90Day:
    scoreTalk(scoredict, talk['filename'], SCORE_SHARED)
for talk in talks_played_90Day:
    if 'Gil' not in talk['filename']:
        scoreTalk(scoredict, talk['filename'], SCORE_NON_GIL_MEDIUM)

for filename, score in scoredict.items():
    if filename not in FileNameToTalk:
        continue
    TopTalks90Days.append((filename, score))
TopTalks90Days = sorted(TopTalks90Days, key=lambda tup: tup[1], reverse = True)
TopTalks90Days = TopTalks90Days[0: MAX_TALKS_90DAY]

#
# output top 2Day, 90Day and AllTime talks to JSON
#
generateJSONFile(PATH_TOPALLTIME_TALKS, TopTalksAllTime)
generateJSONFile(PATH_TOP90DAYS_TALKS, TopTalks90Days)
generateJSONFile(PATH_TOP2DAYS_TALKS, TopTalks2Days)


print("Done")


