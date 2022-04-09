#!/usr/bin/python
from __future__ import print_function
import os
import time
import boto3
import urllib2
import random
import string
import json


CLIPS_PATH = '/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Data/CLIPS/'
TRANSCRIPTIONS_PATH = '/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Data/TRANSCRIPTIONS/'

clipped_talks = os.listdir(CLIPS_PATH)
transcribed_talks = os.listdir(TRANSCRIPTIONS_PATH)

count = 1
print("Beginning Transcription")
for filename in clipped_talks:

    # we can't handle talks in spanish
    if 'Castillo' in filename: continue
    if 'bruni' in filename: continue
    if 'Bruni' in filename: continue

    clippedtalk_path = CLIPS_PATH + filename

    transcribed_filename = filename.replace('.mp3','')
    if transcribed_filename in transcribed_talks:
        #print("Skipping - Already Transcribed\n")
        continue

    print("Count: {}  Talk: {}".format(count, filename))
    count += 1

    """
    cmd = "file {}".format(clippedtalk_path)
    res = os.popen(cmd).read()
    #res = os.system(cmd)
    a = res.split(',')
    #print(a)
    if len(a) <= 2: 
        #print("Bitrate Not Parsed: {} Assuming 44.1k".format(res))
        print("Bitrate Not Parsed: Assuming 44.1k")
        bitrate = 44100
    else:
        sample = a[-2].replace(' kHz','')
        sample = sample.replace(' ','')
        if 'free' in sample: continue
        bitrate = float(sample) * 1000
        bitrate = int(bitrate)
    """
    cmd = "mp3info -r a -p \"%f %Q\" {}".format(clippedtalk_path)
    res = os.popen(cmd).read()
    a = res.split(' ')
    bitrate = float(a[1])
    bitrate = int(bitrate)
    print("Bitrate: {}".format(bitrate))

    transcribe = boto3.client('transcribe', region_name='us-east-1')
    job_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    job_uri = "https://s3.amazonaws.com/virtualdharmaclips.org/" + filename
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat='mp3',
        LanguageCode='en-US',
        MediaSampleRateHertz=bitrate
    )
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
	#print("...")
        time.sleep(5)


    print(status)
    if status['TranscriptionJob']['TranscriptionJobStatus'] == 'FAILED':
        print('FAILED')
        continue
    transcriptURL = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
    f = urllib2.urlopen(transcriptURL)
    jsonData = json.loads(f.read())
    transcript = jsonData['results']['transcripts'][0]['transcript']


    transcription_path = TRANSCRIPTIONS_PATH + transcribed_filename
    print("Transcription: {}\n".format(transcription_path))
    f = open(transcription_path, "w+")
    f.write(transcript)
    f.close()

print("\nDone: {} Talks Transcribed".format(count))

