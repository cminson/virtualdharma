#!/usr/bin/python
import os

TALK_PATH = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Data/TALKS/"
CLIP_PATH = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Data/CLIPS/"

source_files = os.listdir(TALK_PATH)
dest_files = os.listdir(CLIP_PATH)

count = 1
for file in source_files:
    source_path = TALK_PATH + file
    dest_path = CLIP_PATH + file
    if file in dest_files:
        print("Skipping - Already Clipped: {}".format(file))
        continue

    print("Count: {}  Clipping: {}".format(count, file))
    cmd = "sox {} {} trim 10 70".format(source_path, dest_path)
    print(cmd)
    os.system(cmd)

    count += 1


