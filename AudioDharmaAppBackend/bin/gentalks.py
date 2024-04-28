#!/usr/bin/python
#
# create a json file for each talk, capturing all of talk metadata
# these files are stored in PATH_TALK_FILES 
#
# these are the list of talks that are presented to the UI, for pagination
# these lists are stored in PATH_INDEX_FILES
#
import os
import json
from common import  URL_MP3_HOST
from common import  LOG, getAllTalks, getIndexPath, getTranscriptPath, getTalkSummaryPath, getTalkPath, getSpeakerImageURL, writeJSONData


TotalTalks = 0


#
# Main
#
LOG('gentalk starts')

for talk in getAllTalks():

    url = talk['url']
    #talk['url'] = URL_MP3_HOST + url

    file_mp3 = os.path.basename(url)
    path_talk =  getTalkPath(file_mp3)
    path_summary_brief = getTalkSummaryPath(talk, '.brief')
    path_summary_long = getTalkSummaryPath(talk, '.long')
    path_transcript = getTranscriptPath(talk)

    #print('filter: ', url)
    if not os.path.exists(path_summary_brief): 
        continue
    if not os.path.exists(path_summary_long): 
        continue
    if not os.path.exists(path_transcript): 
        continue

    with open(path_summary_brief) as fd:
        talk['summary_brief'] = fd.read()
    with open(path_summary_long) as fd:
        talk['summary_long'] = fd.read()
    with open(path_transcript) as fd:
        talk['transcript'] = fd.read()

    url_image_speaker = getSpeakerImageURL(talk['speaker'])
    talk['url_image_speaker'] = url_image_speaker

    # now store the talk json
    with open(path_talk, "w") as fd:
        #print(f'writing: {path_talk}')
        json.dump(talk, fd, indent=4)

    TotalTalks += 1



LOG('gentalk completes')
LOG(f'total talks: {TotalTalks}')

