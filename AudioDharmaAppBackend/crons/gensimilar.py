#!/usr/bin/python3
from __future__ import print_function
import sys
import cgi
import datetime
import time
import json
import random
import os
import operator
import re, math
from collections import Counter


CONFIG_JSON  = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG00.JSON"
TRANSCRIPTIONS_PATH = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/data/TRANSCRIPTIONS/"
TALKS_PATH = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/data/SIMILAR/"
STOPWORDS_PATH = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/data/STOPWORDS"
LOG_PATH = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/logs/log.txt"

WORD = re.compile(r'\w+')

START_TIME = 0

def generateJSONFile(filename, similar_talks):

    name = filename.replace('.mp3', '')
    name = name.replace('.MP3', '')
    path = TALKS_PATH + name
    print("Generating: ", path)
    with open(path,'w+') as fd:
        fd.write("{\n")
        fd.write("\"SIMILAR\": [\n")
        for talk in similar_talks:

            if talk == None: continue

            file_name = talk[0]
            score = talk[1]

            fd.write("{\n")
            fd.write("\t\"filename\" : \"" + file_name + "\",\n")
            fd.write("\t\"score\" : " + str(score) + "\n")


            if talk != similar_talks[-1]:
                fd.write("},\n")
            else:
                fd.write("}\n")

        fd.write("]\n")
        fd.write("}\n")
    return 0


def get_cosine(vec1, vec2):
     intersection = set(vec1.keys()) & set(vec2.keys())
     numerator = sum([vec1[x] * vec2[x] for x in intersection])

     sum1 = sum([vec1[x]**2 for x in vec1.keys()])
     sum2 = sum([vec2[x]**2 for x in vec2.keys()])
     denominator = math.sqrt(sum1) * math.sqrt(sum2)

     if not denominator:
        return 0.0
     else:
        return float(numerator) / denominator


def text_to_vector(text):
     words = WORD.findall(text)
     return Counter(words)


def getSimilarity(text1, text2):

    v1 = text_to_vector(text1)
    v2 = text_to_vector(text2)
    score =  get_cosine(v1, v2)
    return round(score,4)


def logStatus(s):

    current_time = time.time()
    elapsed_time = round(current_time - START_TIME, 0)
    (hours, minutes, seconds) = convertToMinutesHours(elapsed_time)
    status = "%02d:%02d:%02d %s" % (hours,minutes,seconds,s)
    print(status)
    LogFD.write(status)
    LogFD.write('\n')


def convertToMinutesHours(seconds):

    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    return int(hours), int(minutes), int(seconds)


#
# Main
#

if len(sys.argv) != 2:
    print("usage: gensimilar.py count")
    sys.exit(1)
    
MAX_COUNT = int(sys.argv[1])

print(MAX_COUNT)
START_TIME = time.time()

#LogFD = open(LOG_PATH, 'w')

# get our stop word list
with open(STOPWORDS_PATH,'r') as fd:
    data = fd.read()
    stop_words = data.split('\n')

AllFileNames = []
FilenameToTranscript = {}


#
# compute all the transcripts
#
#logStatus("Computing Transcript Text")

count = 0
with open(CONFIG_JSON,'r') as fd:
    Config  = json.load(fd)
    for talk in Config['talks']:
        url = talk['url']
        filename = url.rsplit('/', 1)[-1]
        title = talk['title']
        duration = talk['duration']
        lastname = talk['speaker'].rsplit(' ',1)[-1]

        a = duration.split(':')
        h = m = 0
        timeCategory = ''
        if len(a) == 2:
            m = int(a[0])
        elif len(a) == 3:
            h = int(a[0])
            m = int(a[1])

        minutes = (h * 60) + m
        if minutes < 8:
            timeCategory = "SHORTEST_TALK"
        elif minutes < 20:
            timeCategory = "SHORT_TALK"
        else: 
            timeCategory = "REGULAR_TALK"

        fullTranscript = title + " " + lastname + " " + timeCategory + "  "  + timeCategory + " " + title
        fullTranscript = fullTranscript.lower()
        #fullTranscript = str(fullTranscript).translate(None, ".:,;'\"!@#$")

        word_tokens = fullTranscript.split(' ')
        filteredTranscript = [w for w in word_tokens if len(w) > 3]
        filteredTranscript = [w for w in filteredTranscript if not w in stop_words]

        filteredTranscriptString = ' '.join(filteredTranscript)

        FilenameToTranscript[filename] = filteredTranscriptString
        #print("filename: {} transcript: {}".format(filename, FilenameToTranscript[filename]))
        #print("{}  {}".format(filename, FilenameToTranscript[filename]))
        AllFileNames.append(filename)



ComparisonFileNames = AllFileNames
	

#
# then generate list of similar talks for each talk
#

#logStatus("Computing Talk Similarities\n")
count = 0
for filename in AllFileNames:
        
    count += 1
    if count > MAX_COUNT: break
    #print("COUNT: ", count)
    #logStatus("{} Source: {}".format(count, filename))
    sourceTranscript = FilenameToTranscript[filename]

    similar_talks = []
    for comparison_filename in ComparisonFileNames:

        if filename == comparison_filename: continue

        comparisonTranscript = FilenameToTranscript[comparison_filename]
        score = getSimilarity(sourceTranscript, comparisonTranscript)

        #print("Comparison: {} {} {}".format(filename, sourceTranscript, comparisonTranscript))

        if score > 0:
            #print("Score: {}".format(score))
            m = (comparison_filename, score)
            similar_talks.append(m)
            


    sorted_talks = sorted(similar_talks, key=lambda tup: tup[1], reverse = True)
    top_matches = sorted_talks[0:8]
    for similar_talk in top_matches:
        name = similar_talk[0]
        score = similar_talk[1]
        #print("Matched: {} Score: {}".format(name, score))

    generateJSONFile(filename, top_matches)


#logStatus("Completed")
#LogFD.close()


        



