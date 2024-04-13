#!/usr/bin/python
#
# Run locally on Mac to check PDF correctness
#
import json
import os

PATH_NEW_TRANSCRIPTS = "/Users/Chris/Documents/PDF"
LIST_CORRECT_PDFS = []

PATH_CONFIG_JSON = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG00.JSON"


test = '20210714-Nikki_Mirghafori-IMC-samadhi_3_5_relaxed_body_receptive_awareness.mp3'

set_mp3 = set()
list_mp3 = []
list_talks = []
with open(PATH_CONFIG_JSON,'r') as fd:
    data  = json.load(fd)
    list_talks = data['talks']

for talk in list_talks:
    url = talk['url']
    file_mp3 = os.path.basename(url)
    #print(file_mp3)
    if file_mp3 in set_mp3:
        print('bad: ', file_mp3)
        continue
    set_mp3.add(file_mp3)


