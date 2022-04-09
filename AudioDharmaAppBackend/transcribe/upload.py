#!/usr/bin/python
import boto3
import os

TRANSCRIPTIONS_PATH = '/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Data/TRANSCRIPTIONS/'
CLIPS_PATH = '/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Data/CLIPS/'

transcribed_talks = os.listdir(TRANSCRIPTIONS_PATH)

source_files = os.listdir(CLIPS_PATH)
bucket_name = 'virtualdharmaclips.org'
for filename in source_files:

    transcribed_filename = filename.replace('.mp3','')
    if transcribed_filename in transcribed_talks:
        print("Skipping - Already Uploaded = Transcribed: {}".format(transcribed_filename))
        continue

    s3 = boto3.client('s3')
    source_path = CLIPS_PATH + filename
    print source_path

    # Uploads the given file using a managed uploader, which will split up large
    # files automatically and upload parts in parallel.
    s3.upload_file(source_path, bucket_name, filename)

