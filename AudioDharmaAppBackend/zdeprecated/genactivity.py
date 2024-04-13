#!/usr/bin/python3
#
# generates the activity.json file.
# which is pulled in by apps (via XZENGETACTIVITY.php).
# this script is run via cron.
#
import MySQLdb as mdb
import json
import time
import sys
from subprocess import call



PATH_CANDIDATE_ACTIVITY_JSON = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CANDIDATE_ACTIVITY.JSON";
PATH_ACTIVITY_JSON = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/ACTIVITY.JSON";
PATH_CONFIG_JSON = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG00.JSON"

DAY_IN_SECONDS =  24 * 60 * 60
MAX_TALKS = 2000

COUNTRY_CODES = {'AR': 'Argentina', 'AE': 'United Arab Emirates', 'AU': 'Australia', 'AT': 'Austria', 'AR': 'Argentina', 'BD': 'Bangladesh', 'BE': 'Belgium', 'BR': 'Brazil', 'CN': 'China', 'CA': 'Canada', 'CZ': 'Czech Republic', 'CH': 'Switzerland', 'CL': 'Chile', 'CR': 'Costa Rica', 'CO': 'Colombia', 'CU': 'Cuba', 'CZ': 'Czech Republic', 'DK': 'Denmark', 'DO': 'Dominican Republic', 'EC': 'Ecuador', 'ES': 'Spain', 'ET': 'Ethiopia', 'EE': 'Estonia', 'EG': 'Egypt', 'FI': 'Finland', 'FR': 'France', 'DE': 'Germany', 'GB': 'Great Britain', 'GR': 'Greece', 'GE': 'Georgia', 'HK': 'Hong Kong', 'HR': 'Croatia', 'HU': 'Hungary', 'ID': 'Indonesia', 'IE': 'Ireland', 'IL': 'Israel', 'IN': 'India', 'IT': 'Italy', 'IR': 'Iran', 'IQ': 'Iraq', 'JP': 'Japan', 'JO': 'Jordan', 'KE' : 'Kenya', 'KG': 'Kyrgyzstan', 'KH': 'Cambodia', 'KR': 'South Korea', 'KW': 'Kuwait', 'LB': 'Lebanon', 'LI': 'Liechtenstein', 'LT': 'Lithuania', 'LU': 'Luxembourg', 'LV': 'Latvia', 'LK': 'Sri Lanka', 'MT': 'Malta', 'MA': 'Morocco', 'MM': 'Myanmar', 'MZ': 'Mozambique', 'MX': 'Mexico', 'MY': 'Malaysia', 'MD': 'Moldova', 'NZ': 'New Zealand', 'NI': 'Nicaragua', 'NL': 'Netherlands', 'NO': 'Norway', 'OM': 'Oman', 'PA': 'Panama', 'PE': 'Peru', 'PK': 'Pakistan', 'PY': 'Paraguay', 'PT': 'Portugal', 'PH': 'Philippines', 'PL': 'Poland', 'PR': 'Puerto Rico', 'RW': 'Rwanda', 'RO': 'Romania', 'RS': 'Serbia', 'RU': 'Russia', 'SK': 'Slovakia', 'SE': 'Sweden', 'SI': 'SLovenia', 'SG': 'Singapore', 'TH': 'Thailand', 'TR': 'Turkey', 'TT': 'Trinidad', 'TJ': 'Tajikistan', 'TW': 'Taiwan', 'UA': 'Ukraine', 'UAE': 'United Arab Emirates', 'US': 'United States', 'UY': 'Uruguay', 'UZ': 'Uzbekistan', 'VN': 'Vietnam', 'ZA': 'South Africa', 'ZW': 'Zimbabwe'
}

FileNameToTalk = {}
TotalTalkCount = 0

def writeActivityData(fd, field, talks, end):

    fd.write("\"{}\": [\n".format(field))
    for talk in talks:

        filename = talk['filename']
        operation = talk['operation']
        city = talk['city']
        country = talk['country']
        devicetype = talk['devicetype']

        if devicetype == 'alexa':
            city = ''
            state = ''
            country = 'Alexa Cloud'

        if country in COUNTRY_CODES:
            country = COUNTRY_CODES[country]

        # possible, due to some talks being renamed in 2021 site update
        if filename not in FileNameToTalk: 
            title = "Talk Not Available"
            date = "NA"
        else:
            title = FileNameToTalk[filename]['title']
            date = FileNameToTalk[filename]['date']

        fd.write("{\n")

        fd.write("\t\"filename\" : \"" + filename + "\",\n")
        fd.write("\t\"operation\" : \"" + operation + "\",\n")
        fd.write("\t\"date\" : \"" + date + "\",\n")
        fd.write("\t\"city\" : \"" + city + "\",\n")
        fd.write("\t\"country\" : \"" + country + "\"\n")

        if talk == talks[-1]:
            fd.write("}\n")
        else:
            fd.write("},\n")

    if end == False:
        fd.write("],\n")
    else:
        fd.write("]\n")

#
# Main
#
# get all the configured talks into a dict, indexed by filename

print("genactivity begins ...")
try:
    with open(PATH_CONFIG_JSON,'r') as fd:
        Config  = json.load(fd)
        for talk in Config['talks']:
            filename = talk['url'].rsplit('/', 1)[-1]
            FileNameToTalk[filename] = talk
except:
    sys.exit(1)

TotalTalkCount = len(FileNameToTalk)

# get all the talks plays and shares in last 24 hours
try:
    con = mdb.connect('localhost', 'cminson', 'ireland', 'ad')
    cur = con.cursor(mdb.cursors.DictCursor)

    seconds = int(time.time()) - DAY_IN_SECONDS
    query = "SELECT * FROM actions WHERE operation=\"PLAYTALK\" AND seconds > \"{}\" ORDER BY ID DESC LIMIT {}".format(seconds,MAX_TALKS)
    cur.execute(query);
    talks_played = cur.fetchall()

    query = "SELECT * FROM actions WHERE operation=\"SHARETALK\" AND seconds > \"{}\" ORDER BY ID DESC LIMIT {}".format(seconds,MAX_TALKS)
    cur.execute(query);
    #print query
    talks_shared = cur.fetchall()

except:
    sys.exit(1)

#
# output everything to json candidate activity file
#
try:
    with open(PATH_CANDIDATE_ACTIVITY_JSON,'w+') as fd:

        fd.write("{\n")
        writeActivityData(fd, "sangha_history", talks_played, False)
        writeActivityData(fd, "sangha_shares", talks_shared, True)
        fd.write("}\n");
        fd.close()

except:
    sys.exit(1)

#
# Validate the candidate activity config
#
print("validating candidate")
try:
    with open(PATH_CANDIDATE_ACTIVITY_JSON,'r') as config:
        _  = json.load(config)
except:
    e = sys.exc_info()[0]
    print("CANDIDATE JSON ERROR: %s" % e)
    sys.exit(0)

#
# Candidate looks good, make it active
#
print("done")

print("deploying activity config")
call(["cp", PATH_CANDIDATE_ACTIVITY_JSON, PATH_ACTIVITY_JSON])



