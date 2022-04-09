#!/usr/bin/python
import json
import random
import os
import sys
from subprocess import call
import requests, urllib, urllib2




CONFIG_PATH= "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG00.JSON"
CANDIDATE_ALEXATALKS_PATH= "/var/www/virtualdharma/httpdocs/AlexaADBackend/TMP/ALEXATALKS00.JSON"
ALEXATALKS_PATH= "/var/www/virtualdharma/httpdocs/AlexaADBackend/Config/ALEXATALKS00.JSON"

SPEECH_WELCOME = "Audio Dharma. Here are today's <emphasis>five</emphasis> Dharma talks - the two most recent talks followed by <emphasis>three</emphasis> randomly selected talks. <break time = \\\"1s\\\"/>"
SPEECH_USERPROMPT = "Select your talk.  For example, you can say:  Alexa, play talk 3."
SPEECH_WELCOME_REPROMPT = "To play a talk, say the talk number.  For example, you can say:  Alexa, play talk 3."

CARD_WELCOME_TITLE = "Welcome To Audio Dharma"

CARD_WELCOME_TEXT = "Welcome to Audio Dharma. Thousands of Dharma talks given by hundreds of teachers from around the world, representing a variety of traditions and viewpoints. You can find the complete list of talks at www.audiodharma.org.\\r\\n \\r\\n Here are the most recent two talks, followed by three randomly selected talks."

CARD_WELCOME_HELP = "To play a talk say the talk number.  For example:  Alexa, play talk 3."

PEECH_HELP = "Talks are listed from number one to number five. To play a talk, say the talk number.  For example, you can say:  Alexa, play talk 2. Once inside a talk you can also move between talks by saying:  Alexa, next talk or:  Alexa, previous talk."


ListAllTalks = []
DictAllTalks = {}
ChosenTalks = []
USE_NATIVE_MP3PATHS = False
URL_MP3_HOST = "https://audiodharma.us-east-1.linodeobjects.com/talks"

Months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

Headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36' }


def talkExists(url):

    try:
        code = requests.head(url, headers=Headers).status_code
    except IOError, e:
        print("Error: ", url)
        exit()

    if code == 200:
        return True

    return False



def talksPrint(text):

    global FH_CONFIG

    FH_CONFIG.write(text)
    FH_CONFIG.write("\n")


def speechFromDate(date):

    global Months

    # this is necessary, as SHORT and LONG talks have the legacy date formats using '-' vs '.'
    date = date.replace("-",".")
    #

    ymd  = date.split('.')
    if len(ymd) != 3:
        return("No Date")

    year = ymd[0]
    m = int(ymd[1])
    day = ymd[2]
    day = day.lstrip("0")
    month = Months[m - 1]

    return month + " " + day + ", " + year


def minutesFromDuration(duration):

    hms  = duration.split(':')

    if len(hms) == 3:
        h = hms[0]
        m = hms[1]
    elif len(hms) == 2:
        h = 0
        m = hms[0]
    else:
        h = 0
        m = 0

    minutes = int(m) + 1
    minutes = (int(h) * 60) + minutes
    return str(minutes)


def getRandomTalk(talks):
    global ChosenTalks

    while True:
        r = random.randint(0, len(talks) - 1)
        talk = talks[r]
        if USE_NATIVE_MP3PATHS == True:
            fileName = talk['url']
        else:
            fileName = talk['url'].split("/")[-1]

        url = URL_MP3_HOST + "/" + fileName
	if talkExists(url) == False: 
            print("Talk Does Not Exist: ", url)
            continue
        if talk not in ChosenTalks: return talk


def getTalkList(talks):

    listTalks = []
    for talk in talks:
        if talk['url'] in DictAllTalks:
            listTalks.append(DictAllTalks[talk['url']])
    return listTalks


# get all available talks 
TalksRecommended  = TalksTop3Months = TalksTop200 = []
with open(CONFIG_PATH,'r') as fd:
    data  = json.load(fd)
    URL_MP3_HOST = data['config']['URL_MP3_HOST']
    USE_NATIVE_MP3PATHS = data['config']['USE_NATIVE_MP3PATHS']
    ListAllTalks = data['talks']
    for talk in ListAllTalks:
        DictAllTalks[talk['url']] = talk
    for album in data['albums']:
        if album["content"] == "KEY_RECOMMENDED_TALKS":
            TalksRecommended = getTalkList(album['talks'])
        if album["content"] == "TOP3MONTHS":
            TalksTop3Months = getTalkList(album['talks'])
        if album["content"] == "TOPTALKS":
            TalksTop200 = getTalkList(album['talks'])


# select two latest talks from Gil, Ines, Andrea
count = 0
for talk in ListAllTalks:
    speaker = talk['speaker']
    if 'Gil' in speaker or 'Andrea' in speaker or "Ines" in speaker:
        count += 1
        ChosenTalks.append(talk)
    if count >= 2: break


talk = getRandomTalk(TalksRecommended)
print(talk)
ChosenTalks.append(talk)
talk = getRandomTalk(TalksTop3Months)
print(talk)
ChosenTalks.append(talk)
talk = getRandomTalk(TalksTop200)
print(talk)
ChosenTalks.append(talk)
print(ChosenTalks)



# now output chosen talks to temporary dev config
FH_CONFIG = open(CANDIDATE_ALEXATALKS_PATH, 'w')

number = 1
talksPrint("{")

talksPrint("\t\"SPEECH_WELCOME\" : \"" + SPEECH_WELCOME + "\",")
talksPrint("\t\"SPEECH_USERPROMPT\" : \"" + SPEECH_USERPROMPT + "\",")
talksPrint("\t\"SPEECH_WELCOME_REPROMPT\" : \"" + SPEECH_WELCOME_REPROMPT + "\",")
talksPrint("\t\"CARD_WELCOME_TITLE\" : \"" + CARD_WELCOME_TITLE + "\",")
talksPrint("\t\"CARD_WELCOME_TEXT\" : \"" + CARD_WELCOME_TEXT + "\",")
talksPrint("\t\"CARD_WELCOME_HELP\" : \"" + CARD_WELCOME_HELP + "\",")


talksPrint("\t\"talks\":[")
for talk in ChosenTalks:

    talkNumber = "Talk " + str(number)
    title = talk['title']
    if USE_NATIVE_MP3PATHS == True:
        filename = talk['url']
    else:
        print("here")
        filename = talk['url'].split("/")[-1]

    speaker = talk['speaker']
    duration = talk['duration']
    date = talk['date']
    minutes = minutesFromDuration(duration)
    url = URL_MP3_HOST + filename
    print("URLL", url)

    title = title.replace("&"," and ")
    speechDate = speechFromDate(date)

    talksPrint("\t{")
    talksPrint("\t\t\"number\":\"" + talkNumber + "\",")
    talksPrint("\t\t\"speaker\":\"" + speaker + "\",")
    talksPrint("\t\t\"title\":\"" + title + "\",")
    talksPrint("\t\t\"date\":\"" + speechDate + "\",")
    talksPrint("\t\t\"url\":\"" + url + "\",")
    talksPrint("\t\t\"filename\":\"" + filename + "\",")
    talksPrint("\t\t\"minutes\":\"" + str(minutes) + "\"")

    if number < len(ChosenTalks):
        talksPrint("\t},")
    else:
        talksPrint("\t}")

    number += 1

talksPrint("\t]")
talksPrint("}")

FH_CONFIG.close()


# verify new config file is valid
try:
    with open(CANDIDATE_ALEXATALKS_PATH,'r') as fd:
        data  = json.load(fd)
except Exception as e:
    print("Error: Alexa Candidate Config File Exception " + str(e))
    sys.exit()


# copy the validated config file into live config directory
call(["cp", CANDIDATE_ALEXATALKS_PATH, ALEXATALKS_PATH ])

    
