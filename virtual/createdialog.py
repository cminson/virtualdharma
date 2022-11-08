#!/usr/bin/python3
#
# train.py
# Christopher Minson
#
# Generate a training set for OpenAI
#

import os
import sys
import string
import json
import openai
import random


PATH_TRAIN = "./data/training/AD.TRAIN"
PATH_LINES = "./data/training/AD.LINES"
PATH_DATABASE = "./data/DATABASE"

START_PROMPT = "Now we begin our infinite conversation. The topics will be innumberable as we explore the Dharma."
#ACTIVE_MODEL = "text-davinci-002"
ACTIVE_MODEL = "text-ada-001"
NUM_ITERATIONS = 10
MIN_LINE_LENGTH = 10

ModelCurrentTemp = 0.5
ModelMaxTokens = 100
ModelFrequencyPenalty = 0.0
ModelPresencePenalty = 0.6


def generateText(promptText):

    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Completion.create(
        model=ACTIVE_MODEL,
        prompt= promptText,
        temperature=ModelCurrentTemp,
        max_tokens=ModelMaxTokens,
        top_p=1,
        frequency_penalty=ModelFrequencyPenalty,
        presence_penalty=ModelPresencePenalty
    )
    text = response['choices'][0]['text']
    print("RESPONSE: ", text)
    list_text = text.split('\n')
    list_text = [line for line in list_text if len(line) > MIN_LINE_LENGTH]
    #list_text = [line for line in list_text if (line[-1]) == '.']
    list_text = [line for line in list_text]
    #print("RAW: ", list_text)
    list_text_top = list_text[0:2]
    print("RAW:0:2: ", list_text_top)
    text = ' '.join([line for line in list_text_top])
    print("TEXT:", text)
    return text

def generatePrompt(prompt_base):

    prompt_lines = prompt_base.split('.')
    prompt_lines = [line for line in prompt_lines if len(line) > MIN_LINE_LENGTH]
    print("PROMPT_LINES: ", prompt_lines)
    prompt_start = prompt_lines[-1]
    random_choice = random.choice(Lines_All).strip()
    prompt = prompt_start + '. ' + random_choice 
    #prompt = random_choice + ' ' + prompt_start 

    print("PROMPT: ", prompt)
    return prompt




f = open(PATH_LINES, "r")
Lines_All = f.readlines()

#prompt = generatePrompt(START_PROMPT)
prompt = START_PROMPT
print("TEXT: ", prompt)
newText = generateText(prompt)

prompt = generatePrompt(newText)

for i in range(NUM_ITERATIONS):
    newText = generateText(prompt)
    prompt = generatePrompt(newText)



