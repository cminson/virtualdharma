#!/usr/bin/python
#
#
# Create long, short, brief, key, transcript summarizations 
#
# Long summaries are long summaries 
# Short are short summaries
# Brief are the shortest, and are cleaned-up short summaries (artificats removed). 
# Keys are brief summaries with stopwords stripped out, and metainfo added
#
# Long and brief summaries are shown in the UI. Short, key,  summaries are internal.
#
# Summarizations are static and not deleted once created.
#
import os
import sys
import json
import openai
import warnings
import time
import re
import random
from datetime import datetime, timedelta
from common import  LOG, configureOpenAIKey, getAllTalks, getAllSpeakers, getBiographyText, getTalkSummaryPath, getSpeakerSummaryPath, getTranscriptPath, getAllSeries, getSeriesSummaryPath, filter_common_words


ACTIVE_MODEL = 'gpt-3.5-turbo'
OPENAI_API_KEY = 0  # set via configureOpenAIKey


ModelCurrentTemp = 0.9
ModelMaxTokens = 128
ModelFrequencyPenalty = 1.0
ModelPresencePenalty = 0.6

MAX_TEXT_SIZE = 16000
MIN_TEXT_SIZE = 11000
SUPER_MIN_TEXT_SIZE = 6000

MAX_TEXT_SIZE = 8000
MIN_TEXT_SIZE = 7000
SUPER_MIN_TEXT_SIZE = 6000
MAX_SUMMARIES_PER_SESSION = 3000 # maximum number of summaries we will make (prevent runaways)

MAX_WORDS_IN_BRIEF = 30

SUMMARIZATION_SIZE_LONG = 80
SUMMARIZATION_SIZE_SHORT = 20


PREFIX_STRINGS_TO_REMOVE = [
    'In this talk, ',
    'This talk ',
    'Summary: ',
    'Summary:',
    'The talk '
]


RECENT_DAYS_COUNT = 180
MAX_MINUTES_SHORT_TALK = 15
MIN_TALKS_ACTIVE_SPEAKER = 10  # if give more talks than this threshold, considered active speaker


# meta annotation for speakers who give lots of talks, and those who don't
META_ACTIVE_SPEAKER = ' active speaker kakapo xyz kakapo active speaker '

MP3TalkDict ={}


Data = {
    'title': '',
    'key_text': ''
}


def capitalize(s):

    words = s.split()
    if words:
        first_word = words[0][0].upper() + words[0][1:]
        return ' '.join([first_word] + words[1:])
    else:
        return s



def genSummary(path_summary, text, size_summarization):

    text = text.replace("[ Silence ]", "")
    text = text.replace("You You", "")
    text = text.replace("you you", "")

    count_bytes = size_summarization * 8

    #LOG(f'summarizing: {path_summary}')

    prompt_system = 'You will briefly summarize text. Do not mention the speaker or any personal name.  Do not use the word "speaker". Do not use the word "summary", or any variation of that word. Do not mention Insight Meditation Center.  Do not mention audioderma.org.  Do not mention IMC.  Do not mention audiodharma.org.  Do not mention Redwood City.  Do not mention California.  Do not mention where the talk was given.   Do not mention SATI. Do not mention any website. Do not exceed {size_summarization} words. Do not exceed {count_bytes} characters in the summary'
    prompt_system = 'Based on ideas in the following text, write a very short essay.  Use some of the ideas in the text.  Do not mention the speaker or any personal name.  Do not use the word "speaker". Do not use the word "summary", or any variation of that word. Do not mention Insight Meditation Center.  Do not mention audioderma.org.  Do not mention IMC.  Do not mention audiodharma.org.  Do not mention Redwood City.  Do not mention California.  Do not use the words "the text". Do not mention where the talk was given.   Do not mention SATI. Do not mention any website. Do not exceed {size_summarization} words. Do not exceed {count_bytes} characters in the summary'
    prompt_user = f'Summarize the  following text in {size_summarization}  words. Here is the text {text}'
    prompt_user = f'Write a short blurb using the ideas in the following text.  Keep it less than {size_summarization}  words. Here is the text to summarize:  {text}'

    openai.api_key = OPENAI_API_KEY
    try:
        response = openai.ChatCompletion.create(
            model=ACTIVE_MODEL,
            temperature=ModelCurrentTemp,
            messages=[
            {'role': 'system', 'content': prompt_system},
            {'role': 'user', 'content': prompt_user}
            ]
        )
    except:
        #print(f'No summary for {prompt_user} {path_summary}')
        print(f'No summary for {path_summary}')
        return None


    summary = response['choices'][0]['message']['content']
    print(f'{path_summary}')
    #LOG(summary)
    return summary


def genSummarySpeaker(path_summary, text, size_summarization):


    if len(text) < 20: return text

    count_bytes = size_summarization * 8

    print(f'summarizing: {path_summary}')
    prompt_system = 'You will briefly summarize text. Do not mention the speaker or any personal name.  Do not use the word "speaker". Do not use the word "summary", or any variation of that word. Do not use the word "talk". Do not mention Insight Meditation Center.  Do not mention audioderma.org.  Do not mention IMC.  Do not mention audiodharma.org.  Do not mention Redwood City.  Do not mention California.  Do not mention where the talk was given.   Do not mention SATI. Do not mention any website. Do not exceed {size_summarization} words. Do not exceed {count_bytes} characters in your summary'
    prompt_user = f'Summarize the following in {size_summarization} words: {text}' 
    #print(prompt)
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model=ACTIVE_MODEL,
        temperature=ModelCurrentTemp,
        messages=[
        {'role': 'system', 'content': prompt_system},
        {'role': 'user', 'content': prompt_user}
        ]
    )

    summary = response['choices'][0]['message']['content']
    print(summary)
    return summary



def genSummarySeries(path_summary, text, size_summarization):

    count_bytes = size_summarization * 8

    prompt = f'You are summarizing a series of buddhist talks. Create new summary text that summarizes the following text in {size_summarization} words. Here is the text: {text}' 
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model=ACTIVE_MODEL,
        temperature=ModelCurrentTemp,
        messages=[
        {'role': 'system', 'content': f'Do not exceed {size_summarization} words. Do not exceed {count_bytes} characters in the summary'},
        {'role': 'user', 'content': prompt}
        ]
    )

    summary = response['choices'][0]['message']['content']
    print(summary)
    return summary







def count_words(text):

    list_words = text.strip().split()
    return len(list_words)


def remove_prefix_from_text(text, prefix):

    if text.strip().startswith(prefix):
        new_text = text[len(prefix):].strip()
        new_text = new_text[0].capitalize() + new_text[1:]
        return new_text
    else:
        return text


def remove_last_sentence(text):


    sentence_pattern = r'[.!?]'
    sentences = re.split(sentence_pattern, text)

    if len(sentences) == 1:
        return text

    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    new_text = '. '.join(sentences[:-1]).strip()
    new_text += '.'
    if len(new_text) < 100:
        return text

    return new_text


def is_recent_talk(date_str):

    date_obj = datetime.strptime(date_str, '%Y.%m.%d')
    today = datetime.today()
    delta = today - date_obj

    # Check if the difference is less than or equal to 3 months
    if delta <= timedelta(days=RECENT_DAYS_COUNT):
        return True
    else:
        return False


def total_minutes(time_str):
    # Split the string into hours, minutes, and seconds
    time_parts = time_str.split(':')

    # Convert each part to an integer
    if len(time_parts) == 3:
        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        seconds = int(time_parts[2])
    elif len(time_parts) == 2:
        hours = 0
        minutes = int(time_parts[0])
        seconds = int(time_parts[1])
    else:
        raise ValueError("Invalid time string")

    # Calculate the total number of minutes
    total_minutes = hours * 60 + minutes

    # Add an extra minute if there are any remaining seconds
    if seconds > 0:
        total_minutes += 1

    return total_minutes


def make_brief_text(summary):

    for i in range(10):
        if count_words(summary) < MAX_WORDS_IN_BRIEF: break
        summary = remove_last_sentence(summary)

    return(summary)



#
# Main
#
LOG(f'gensummaries begins')
OPENAI_API_KEY = configureOpenAIKey()

#
# generate summaries for every talk
# every talk has a long, short, brief and key summary
#
TotalNewSummariesLong = 0
TotalNewSummariesShort = 0
TotalNewSummariesBrief = 0
TotalNewSummariesKey = 0
list_talks = getAllTalks()
count = 0

# generate long summaries
for talk in list_talks:

    path_transcript = getTranscriptPath(talk)
    path_talk_long = getTalkSummaryPath(talk, '.long')

    # skip if we already have a summary, or if we don't have a transcript
    if os.path.exists(path_talk_long): continue 
    if not os.path.exists(path_transcript): continue # can not summarize talks that don't have transcriptions


    with open(path_transcript) as fd:
        text = fd.read()
        text = text.replace('\n', ' ')

    if len(text) > MAX_TEXT_SIZE:
        text = text[0:MAX_TEXT_SIZE]

    # generate summaries, falling back to smaller and smaller text windows should a summary fail
    # this is necessary, as it isn't always clear what text length will summarize or not
    fall_back_text_size = MIN_TEXT_SIZE
    summary = None
    while True:

        try:
            summary =  genSummary(path_talk_long, text, SUMMARIZATION_SIZE_LONG)
            # if failed summary (== None). go to next-lower text window.
            # MIN_TEXT_SIZE first, and if that fails, SUPER_MIN_TEXT_SIZE
            # this is the same code as in the exception bloc
            if summary == None:
                text = text[0:fall_back_text_size]
                if fall_back_text_size == SUPER_MIN_TEXT_SIZE: break
                fall_back_text_size = SUPER_MIN_TEXT_SIZE
                continue
            break
        except Exception as e:
            # failed summary. so go to next-lower text window.
            # MIN_TEXT_SIZE first, and if that fails, SUPER_MIN_TEXT_SIZE
            print("ERROR: Going to MIN Text Window")
            text = text[0:fall_back_text_size]
            if fall_back_text_size == SUPER_MIN_TEXT_SIZE: break
            fall_back_text_size = SUPER_MIN_TEXT_SIZE
            continue

    if not summary: continue

    with open(path_talk_long, 'w') as fd:
        fd.write(summary)
        TotalNewSummariesLong += 1


# generate short summaries
print("Creating short summaries")
for talk in list_talks:

    path_transcript = getTranscriptPath(talk)
    path_talk_short = getTalkSummaryPath(talk, '.short')

    if os.path.exists(path_talk_short): continue 
    if not os.path.exists(path_transcript): continue # can not summarize talks that don't have transcriptions

    with open(path_transcript) as fd:
        text = fd.read()
        text = text.replace('\n', ' ')

    if len(text) > MAX_TEXT_SIZE:
        text = text[0:MAX_TEXT_SIZE]
    try:
        summary = genSummary(path_talk_short, text, SUMMARIZATION_SIZE_SHORT)
        if summary == None: 
            summary = "No summary available"

        prefix = "This text"
        if summary.startswith(prefix):
            summary =  summary[len(prefix):]
        prefix = "The text"
        if summary.startswith(prefix):
            summary =  summary[len(prefix):]
        prefix = "The speaker"
        if summary.startswith(prefix):
            summary =  summary[len(prefix):]
        prefix = "Discusses"
        if summary.startswith(prefix):
            summary =  summary[len(prefix):]

        summary = summary.strip()
        summary = capitalize(summary)
        print("RESULT: ", summary)

    except Exception as e:
        print("ERROR: Going to MIN Text Window")
        text = text[0:(MIN_TEXT_SIZE)]
        summary = genSummary(path_talk_short, text, SUMMARIZATION_SIZE_SHORT)
        if summary == None: 
            print("No summary available")
            summary = "No summary available"

        prefix = "This text"
        if summary.startswith(prefix):
            summary =  summary[len(prefix):]
        prefix = "The text"
        if summary.startswith(prefix):
            summary =  summary[len(prefix):]
        prefix = "The speaker"
        if summary.startswith(prefix):
            summary =  summary[len(prefix):]
        prefix = "Discusses"
        if summary.startswith(prefix):
            summary =  summary[len(prefix):]

        summary = summary.strip()
        summary = capitalize(summary)
        print("E RESULT: ", summary)

    if not summary: 
        summary = "No summary available"
    with open(path_talk_short, 'w') as fd:

        fd.write(summary)
        TotalNewSummariesShort += 1




# generate brief and key summaries
# brief summaries are short summaries that are cleaned up, suitable for UI display
# key summaries are long summaries + data.  it is this text that
# is then later vectorized for each talk
#
print("Creating brief and key summaries")
for talk in list_talks:

    path_summary_long = getTalkSummaryPath(talk, '.long')
    path_summary_short = getTalkSummaryPath(talk, '.short')
    path_summary_brief = getTalkSummaryPath(talk, '.brief')
    path_summary_key = getTalkSummaryPath(talk, '.key')

    if not os.path.exists(path_summary_short): continue 
    if os.path.exists(path_summary_key): continue 

    summary = ''
    key_text = ''
    with open(path_summary_short, 'r') as fd:
        summary = fd.read()

    for prefix in PREFIX_STRINGS_TO_REMOVE:
        summary = remove_prefix_from_text(summary, prefix)

    # compress the short text into a briefer standard displayable form. somewhat hackish
    for i in range(10):
        if count_words(summary) < MAX_WORDS_IN_BRIEF: break
        summary = remove_last_sentence(summary)

    with open(path_summary_brief, 'w') as fd:
        fd.write(summary)
        TotalNewSummariesBrief += 1

    key_text = filter_common_words(summary)
    title = talk['title']
    series = talk['series']
    ln = talk['ln']

    language = 'english'
    title_series = ''
    if ln == 'es':
        language = 'spanish'
    if ln == 'ch':
        language = 'chinese'
    if len(series) > 1:
        title_series = 'series ' + series

    minutes = total_minutes(talk['duration'])
    key_text = f'{title} {title_series} {key_text}'

    with open(path_summary_key, 'w') as fd:
        fd.write(key_text)
        TotalNewSummariesKey += 1


LOG(f'New Summaries: Long:  {TotalNewSummariesLong}  Short: {TotalNewSummariesShort}  Brief: {TotalNewSummariesBrief}  Key: {TotalNewSummariesKey}')
LOG('gensummaries done')









