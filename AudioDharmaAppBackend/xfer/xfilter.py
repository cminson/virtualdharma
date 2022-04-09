#!/usr/bin/python3
import json
import string
import requests, urllib


DEV_CONFIG_FILE = '../Config/DEV.JSON'
LIVE_CONFIG_FILE = '../Config/CONFIG00.JSON'

SPANISH_TERMS = [' el ', ' y ', ' de ', ' el ', ' la ', ' del ', 'meditación', 'atención', 'introducción', ' tono ', 'reflexión', 'sobre', 'contemplaciones', 'emociones', 'sentir', ' para ', ' con ', 'diálogo', 'respiración', 'equilibrio', 'transiciones', 'lugar', 'vida', 'tranquilizantes', 'sabidura', 'espacio', 'creando', ' este ','discurso', 'cinco', 'cautro', 'ocho', 'nuevos', 'pregunta', ' siete', 'diez', 'parte', 'sendero' ]


TitleToPDF = {}
ListAllTalks = []

with open(LIVE_CONFIG_FILE,'r') as fd:
    data  = json.load(fd)

    root = data['config']['URL_MP3_HOST']
    albums = data['albums']
    talks = data['talks']
    for talk in talks:
        title = talk['title']
        series = talk["series"]
        ln = talk["ln"]
        url = talk['url']
        speaker = talk['speaker']
        pdf = talk['pdf']
        date = talk['date']
        duration = talk['duration']
        if 'virtual' in pdf:
            TitleToPDF[title] = pdf



count = 0
with open(DEV_CONFIG_FILE,'r') as fd:
    data  = json.load(fd)
    root = data["config"]["URL_MP3_HOST"]

    talks = data['talks']
    for talk in talks:
        title = talk['title']
        series = talk["series"]
        speaker = talk["speaker"]

        ln = "en"
        words = title.split(' ')
        for word in words:
            if word.lower() in SPANISH_TERMS:
                ln = "es"
                break
        if speaker == "Andrea Castillo":
            ln = "es"

        url = talk['url']
        speaker = talk['speaker']
        pdf = ""
        date = talk['date']
        duration = talk['duration']

        if title in TitleToPDF:

            pdf = TitleToPDF[title]
            count += 1

        print("\t{")
        print("\t\t\"title\":\"" + title + "\",")
        print("\t\t\"series\":\"" + series +  "\",")
        print("\t\t\"ln\":\"" + ln + "\",")
        print("\t\t\"url\":\"" + url + "\",")
        print("\t\t\"speaker\":\"" + speaker + "\",")
        print("\t\t\"pdf\":\"" + pdf + "\",")
        print("\t\t\"date\":\"" + date + "\",")
        print("\t\t\"duration\":\"" + duration + "\"")
        print("\t},")

    print("Done: ", count)
    
