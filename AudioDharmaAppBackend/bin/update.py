#!/usr/bin/python
#
# update.py
# updates audiodharma.ai with new raw transcripts
# based off config file showing all talks, for any talk that is not transcribed, download
# the mp3 and then create a transcription via whisper
#
#  command_whisper = f'whisper --verbose False  --model medium {path_mp3} --output_format txt --output_dir {PATH_TMP_OUTPUT}\n'
#
import os
import sys
import json
import urllib.request
import time
from os import path
import subprocess
import time
import datetime
import shutil
from datetime import datetime
import socket
from pydub import AudioSegment
import whisper

from common import URL_MP3_HOST
from common import LOG, getAllTalks, getRawTranscriptPath, getTranscriptPath, getMP3Path, getTalkURL, getTMPFile

CountDownloads = 0
CountTranscripts = 0

# this socket is used as a semaphore, to ensure only one instance of update runs at a time
ServerSocket = None
HOST = '127.0.0.1'  
PORT = 12345        

AUDIO_MAX_WHISPER_DURATION = 30 * 60 * 1000  # Convert 30 minutes to milliseconds




def is_unique_instance():

    global ServerSocket

    try:
        ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        ServerSocket.bind((HOST, PORT))
        return True
    except:
        return False


def talk_download(source_url, path_mp3):

    global CountDownloads

    LOG(f'downloading: {source_url} to {path_mp3}')
    if path.exists(path_mp3):
        LOG('mp3 exists')
        return True

    try:
        response = urllib.request.urlopen(source_url)
    except:
        LOG(f'ERROR: {source_url} not found')
        return False

    data = response.read()
    with open(path_mp3, "wb") as fd:
        fd.write(data)
        CountDownloads += 1

    time.sleep(5.0)
    LOG(f'downloaded: {path_mp3}')

    return True



def talk_transcribe(path_mp3, path_raw_transcript):

    global CountTranscripts


    LOG(f'Transcribing: {path_mp3} to: {path_raw_transcript}')

    time_start = time.time()
    try:
        # Load the Whisper model
        model = whisper.load_model("medium")

        # Perform transcription
        result = model.transcribe(path_mp3)
        text = result["text"]

        # Write the transcription to a file
        with open(path_raw_transcript, 'w') as fd:
            fd.write(text)

    except whisper.WhisperException as we:
        print(f"Whisper-specific error occurred: {we}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Attempt to transcribe has finished.")


    time_end = time.time()
    minutes = round(time_execution / 60)
    LOG(f'execution time: {minutes} minutes')


def split_mp3(file_path, duration):

    list_mp3_chunks = [] 

    chunk_count = int(duration / AUDIO_MAX_WHISPER_DURATION)
    remainder = int(duration % AUDIO_MAX_WHISPER_DURATION)

    # Filename processing
    base_name = file_path.rsplit('.', 1)[0]

    # Create chunks and export
    for i in range(chunk_count):

        path_mp3_chunk = f"{base_name}{i + 1}.mp3"

        start_time = i * AUDIO_MAX_WHISPER_DURATION
        end_time = start_time + AUDIO_MAX_WHISPER_DURATION
        chunk = audio[start_time:end_time]

        chunk.export(path_mp3_chunk, format="mp3")

        list_mp3_chunks.append(path_mp3_chunk)

    # Handle any remainder chunks of the audio
    if remainder > 0:

        path_mp3_chunk = f"{base_name}{chunk_count + 1}.mp3"

        start_time = chunk_count * AUDIO_MAX_WHISPER_DURATION
        chunk = audio[start_time:]

        chunk.export(path_mp3_chunk, format="mp3")

        list_mp3_chunks.append(path_mp3_chunk)

    return list_mp3_chunks


#
# Main
# 
LOG(f'\n\n#############\nupdate.py\nbegin: updating to new transcripts')

if not is_unique_instance():
    LOG("exiting: another instance of update.py is running.")
    exit()

#
# if talk not transcribed, transcribe it
# currently we only do ONE talk at a time, and rely on cron to keep 
# creating new update runs.  we do this to balance load across time
#
list_talks = getAllTalks()
for talk in list_talks:

    if talk['ln'] != 'en':
        continue

    title = talk['title']
    url = talk['url']
    duration = talk['duration']

    source_url= getTalkURL(talk)
    path_mp3 = getMP3Path(talk)

    path_raw_transcript = getRawTranscriptPath(talk)

    # if transcript already exists, skip it
    if path.exists(path_raw_transcript):
        print(f'skipping: {path_raw_transcript}')
        continue

    # download it
    if not talk_download(source_url, path_mp3):
        continue

    audio = AudioSegment.from_mp3(path_mp3)
    duration = round(len(audio))
    LOG(f"duration: {round(duration / 60000)}")

    if duration < AUDIO_MAX_WHISPER_DURATION:
        LOG("Duration is less than AUDIO_MAX_WHISPER_DURATION")

        talk_transcribe(path_mp3, path_raw_transcript)

    else:

        LOG("Duration is greater than AUDIO_MAX_WHISPER_DURATION")
        
        list_txt_chunks = []
        list_mp3_chunks = split_mp3(path_mp3, duration)
        for path_mp3_chunk in list_mp3_chunks:

            file_name = os.path.basename(path_mp3_chunk)
            path_tmp_file = getTMPFile(file_name)
            path_tmp_file = path_tmp_file.replace(".mp3", ".txt")
            list_txt_chunks.append(path_tmp_file)

            print(path_mp3_chunk, path_tmp_file)
            talk_transcribe(path_mp3_chunk, path_tmp_file)


        LOG(f"writing transcript chunks to {path_raw_transcript}")
        with open(path_raw_transcript, 'w') as outfile:
            for file_path in list_txt_chunks:
                with open(file_path, 'r') as infile:
                    file_content = infile.read()
                    outfile.write(file_content)
                    #outfile.write("\n")


    # for now, just one transcript per run!
    #break


LOG(f'complete')
LOG(f'downloads: {CountDownloads}   new transcripts: {CountTranscripts}')
