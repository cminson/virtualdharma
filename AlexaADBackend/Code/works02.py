from __future__ import print_function
import urllib
import httplib
import urllib2
import json
from time import sleep

EXPECTED_TALK_COUNT = 6
AD_SITE = "www.virtualdharma.org:80"
AD_REPORT_ACTIVITY = "/AlexaADBackend/Access/reportactivity.php"

AD_CONFIG = "http://virtualdharma.org/AlexaADBackend/Config/ALEXATALKS00.JSON"
AD_APPLICATION_ID = "amzn1.ask.skill.03d50eb2-f557-47cb-a256-bac3cdc78515"

SPEECH_WELCOME = "Welcome to Audio Dharma. Here are the two most recent talks.  <emphasis>Followed</emphasis> by four suggested talks<break time=\"1s\"/>"
SPEECH_WELCOME_REPROMPT = "To play a talk say the talk followed by the number.  For example:  Alexa, play talk 5"

CARD_WELCOME_TITLE = "Welcome To Audio Dharma"

CARD_WELCOME_TEXT = "Welcome to Audio Dharma. Thousands of Dharma talks given by hundreds of teachers from around the world, representing a variety of traditions and viewpoints. You can find the complete list of talks at www.audiodharma.org.\r\n \r\n Here are the two most recent talks, followed by four suggested talks."

CARD_WELCOME_HELP = "To play a talk say the talk followed by the number.  For example:  Alexa, play talk 5"

SPEECH_LOOPING_UNSUPPORTED = "Audio Dharma talks do not loop"
SPEECH_SHUFFLING_UNSUPPORTED = "Audio Dharma talks do not shuffle"
SPEECH_SYSTEM_PROBLEM = "Audio Dharma is currently unavailable.  Please try again later."
SPEECH_CANCELLED = "Thank you for using Audio Dharma"

TALKPOSITION_INCREMENT = 60 * 1000  # time in ms to advance/rewind a talk when executing FastForward or FastBackward

#
# Templates for JSON responses
#
def jsonAnnouncement(cardTitle, cardText, speech, repromptSpeech, shouldEndSession):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': speech
        },
        'card': {
            'type': 'Standard',
            'title': cardTitle,
            'text': cardText,
            "image": {
                "smallImageUrl": "https://s3.amazonaws.com/virtualdharma.org/alexa720x480.jpg",
                "largeImageUrl": "https://s3.amazonaws.com/virtualdharma.org/alexa1200x800.jpg"
            }
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': repromptSpeech
            }
        },
        'shouldEndSession': shouldEndSession
    }


def jsonNoneResponse():
    return {
        "version": "1.0",
        "sessionAttributes": {},
        "response": {
            "shouldEndSession": True
        }
    }


def jsonNoop():
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': ""
        },
        'card': {
            'type': 'Simple',
            'title': '',
            'content': '' 
            },
        'shouldEndSession': False
    }


def jsonPlayTalk(cardTitle, cardText, speech, talkURL):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': speech
        },
        'card': {
            'type': 'Standard',
            'title': cardTitle,
            'text': cardText,
            "image": {
                "smallImageUrl": "https://s3.amazonaws.com/virtualdharma.org/alexa720x480.jpg",
                "largeImageUrl": "https://s3.amazonaws.com/virtualdharma.org/alexa1200x800.jpg"
            }
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': ""
            }
        },
        "directives": [
        {
            "type": "AudioPlayer.Play",
            "playBehavior": "REPLACE_ALL",
            "audioItem": {
                "stream": {
                    "token": talkURL,
                    "url": talkURL,
                    "offsetInMilliseconds": 0
                }
            }
        }
        ],
        'shouldEndSession': True
    }


def jsonStopTalk(talkURL):
    return {
        'version': '1.0',
        'response': {
            "directives": [
            {
                "type": "AudioPlayer.Stop",
                "playBehavior": "REPLACE_ALL",
                "audioItem": {
                    "stream": {
                        "token":  talkURL,
                        "url":  talkURL,
                        "offsetInMilliseconds": 0
                    }
                }
            }
            ]
        }
    }


def jsonResumeTalk(talkURL, talkPosition):
    return {
        'version': '1.0',
        'response': {
            "directives": [
            {
                "type": "AudioPlayer.Play",
                "playBehavior": "REPLACE_ALL",
                "audioItem": {
                    "stream": {
                        "token": talkURL,
                        "url": talkURL,
                        "offsetInMilliseconds": talkPosition
                    }
                }
            }
            ]
        }
    }


def jsonSetTalkPosition(talkURL, offset):
    return {
        'version': '1.0',
        'response': {
            "directives": [
            {
                "type": "AudioPlayer.Play",
                "playBehavior": "REPLACE_ALL",
                "audioItem": {
                    "stream": {
                        "token": talkURL,
                        "url": talkURL,
                        "offsetInMilliseconds": offset
                    }
                }
            }
            ]
        }
    }


def jsonCancelSession(cardTitle, cardText, speech, talkURL):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': speech
        },
        'card': {
            'type': 'Standard',
            'title': cardTitle,
            'text': cardText,
            "image": {
                "smallImageUrl": "https://s3.amazonaws.com/virtualdharma.org/alexa720x480.jpg",
                "largeImageUrl": "https://s3.amazonaws.com/virtualdharma.org/alexa1200x800.jpg"
            }
        },
        "directives": [
        {
            "type": "AudioPlayer.Stop",
            "playBehavior": "REPLACE_ALL",
            "audioItem": {
                "stream": {
                    "token": talkURL,
                    "url": talkURL,
                    "offsetInMilliseconds": 0
                }
            }
        }
        ],
        'shouldEndSession': True
    }


#
# Intent response functions
#
def buildResponse(speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": {},
        "response": speechlet_response
    }


def welcomeResponse():

    global SPEECH_WELCOME
    global SPEECH_WELCOME_REPROMPT
    global CARD_WELCOME_TITLE
    global CARD_WELCOME_TEXT
    global CARD_WELCOME_HELP
    global SPEECH_SYSTEM_PROBLEM

    recentTalksList = loadMostRecentTalks()

    if recentTalksList == None:
        firstSpeech = speakString(SPEECH_SYSTEM_PROBLEM)
        cardTitle = SPEECH_SYSTEM_PROBLEM
        cardText = ""
        repromptSpeech = ""
        shouldEndSession = True
        response = buildResponse(jsonAnnouncement(cardTitle, cardText, firstSpeech, repromptSpeech, shouldEndSession))
        print(response)
        return response


    welcome = SPEECH_WELCOME
    welcomeText = CARD_WELCOME_TEXT
    for talk in recentTalksList:
        numberText = talk['number']
        speakerText = talk['speaker']
        number = "<emphasis>" + numberText + "</emphasis>"
        title = talk['title']
        date = talk['date']
        speaker = "By " + talk['speaker']
        minutes = talk['minutes'] + " minutes"

        welcome += number
        welcome += ":  "
        welcome += title
        welcome += " "
        welcome += speaker
        welcome += " "
        welcome += "<break time=\"1s\"/>"
        welcome += minutes
        welcome += " "
        welcome += "<break time=\"1s\"/>"

        welcomeText += "\r\n "
        welcomeText += "\r\n "
        welcomeText += numberText
        welcomeText += ": "
        welcomeText += title
        welcomeText += "\r\n "
        welcomeText += speakerText
        welcomeText += "   "
        welcomeText += date
        welcomeText += "   "
        welcomeText += minutes

    welcomeText += "\r\n "
    welcomeText += "\r\n "
    welcomeText += CARD_WELCOME_HELP

    firstSpeech = speakString(welcome)

    cardTitle = CARD_WELCOME_TITLE
    cardText = welcomeText
    repromptSpeech = speakString(SPEECH_WELCOME_REPROMPT)

    shouldEndSession = False
    response = buildResponse(jsonAnnouncement(cardTitle, cardText, firstSpeech, repromptSpeech, shouldEndSession))
    print(response)
    return response


def unsupportedLooping():

    global SPEECH_LOOPING_UNSUPPORTED

    cardTitle = SPEECH_LOOPING_UNSUPPORTED
    cardText = ""
    speechOutput = speakString(SPEECH_LOOPING_UNSUPPORTED)
    reprompt_text = ""
    shouldEndSession = False

    response = buildResponse(jsonAnnouncement(cardTitle, cardText, speechOutput, reprompt_text, shouldEndSession))
    print(response)
    return response


def unsupportedShuffling():

    global SPEECH_SHUFFLING_UNSUPPORTED

    cardTitle = SPEECH_SHUFFLING_UNSUPPORTED
    cardText = ""
    speechOutput = speakString(SPEECH_SHUFFLING_UNSUPPORTED)
    reprompt_text = ""
    shouldEndSession = False
    response = buildResponse(jsonAnnouncement(cardTitle, cardText, speechOutput, reprompt_text, shouldEndSession))
    print(response)
    return response


def noop():

    print("noop")
    response = buildResponse(json_noop())
    print(response)
    return response


def cancelSession():

    global SPEECH_CANCELLED

    cardTitle = SPEECH_CANCELLED
    cardText = ""
    speechOutput = speakString(SPEECH_CANCELLED)

    response = buildResponse(jsonCancelSession(cardTitle, cardText, speechOutput, None))
    print(response)
    return response


def playTalk(message, talkIndex, recentTalksList):

    talk = recentTalksList[talkIndex]
    talkTitle = talk['title']
    date = talk['date']
    speaker = talk['speaker']
    minutes = talk['minutes']
    talkURL = talk['url']

    cardTitle = message

    cardText = talkTitle + "\n\r" + speaker + "  " + date + "   " + minutes + " minutes"
    speechOutput = speakString(cardTitle)
    response =  buildResponse(jsonPlayTalk(cardTitle, cardText, speechOutput, talkURL))
    print(response)
    return response


def playTalkOne(recentTalksList):

    return playTalk("Playing Talk One", 0, recentTalksList)


def playTalkTwo(recentTalksList):

    return playTalk("Playing Talk Two", 1, recentTalksList)


def playTalkThree(recentTalksList):

    return playTalk("Playing Talk Three", 2, recentTalksList)


def playTalkFour(recentTalksList):

    return playTalk("Playing Talk Four", 3, recentTalksList)


def playTalkFive(recentTalksList):

    return playTalk("Playing Talk Five", 4, recentTalksList)


def playTalkSix(recentTalksList):

    return playTalk("Playing Talk Six", 5, recentTalksList)


def playNextTalk(recentTalksList, currentTalkURL):

    currentTalkTrack = 0
    for talk in recentTalksList:
        if talk['url'] == currentTalkURL: 
            break
        currentTalkTrack += 1

    if currentTalkTrack >= len(recentTalksList):
        print("ERROR: Talk Not Found: " + currentTalkURL)
        currentTalkTrack = 0

    currentTalkTrack += 1
    if currentTalkTrack >= len(recentTalksList):
        currentTalkTrack = 0

    return playTalk("Playing Next Talk", currentTalkTrack, recentTalksList)


def playPreviousTalk(recentTalksList, currentTalkURL):

    currentTalkTrack = 0
    for talk in recentTalksList:
        if talk['url'] == currentTalkURL: 
            break
        currentTalkTrack += 1

    if currentTalkTrack >= len(recentTalksList):
        print("ERROR: Talk Not Found: " + currentTalkURL)
        currentTalkTrack = 0

    currentTalkTrack -= 1
    if currentTalkTrack < 0:
        currentTalkTrack = len(recentTalksList) - 1

    return playTalk("Playing Previous Talk", currentTalkTrack, recentTalksList)



def pauseTalk(currentTalkURL):
    response = jsonStopTalk(currentTalkURL)
    print(response)
    return response


def resumeTalk(currentTalkURL, currentTalkPosition):
    print("resume talk: " + currentTalkURL + " " + str(currentTalkPosition))
    response = jsonResumeTalk(currentTalkURL, currentTalkPosition)
    print(response)
    return response


def restartTalk(currentTalkURL):
    print("restart talk")
    response = jsonSetTalkPosition(currentTalkURL, 0)
    print(response)
    return response


# not active
def fastForward(currentTalkURL, currentTalkPosition):
    global TALKPOSITION_INCREMENT

    print("fast forward")
    currentTalkPosition +=  TALKPOSITION_INCREMENT
    response = jsonSetTalkPosition(currentTalkURL, currentTalkPosition)
    print(response)
    return response


# not active
def fastBackward(currentTalkURL, currentTalkPosition):
    global TALKPOSITION_INCREMENT

    print("fast backward")
    currentTalkPosition -= TALKPOSITION_INCREMENT
    if currentTalkPosition < 0: currentTalkPosition = 0
    response = jsonSetTalkPosition(currentTalkURL, currentTalkPosition)
    print(response)
    return response


def recordSessionStarted(session_started_request, session):

    print("on_session_started requestId=" + session_started_request['requestId'] + ", sessionId=" + session['sessionId'])


def recordSessionEnded(session_ended_request, session):

    print("on_session_ended requestId=" + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])


def printDict(audioDict):
    jsonString = json.dumps(audioDict)
    print(jsonString)


def speakString(s):
    return "<speak>" + s + "</speak>"


#
# Handle events
#
def executeIntent(intent_request, session, currentTalkURL, currentTalkPosition):

    global SPEECH_SYSTEM_PROBLEM

    print("handle_intent requestId=" + intent_request['requestId'] + ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    print("INTENT NAME: ", intent_name)

    if intent_name == "AMAZON.StopIntent":
        return cancelSession()
    elif intent_name == "AMAZON.CancelIntent":
        return cancelSession()
    elif intent_name == "AMAZON.LoopOnIntent":
        return unsupportedLooping()
    elif intent_name == "AMAZON.LoopOffIntent":
        return unsupportedLooping()
    elif intent_name == "AMAZON.ShuffleOffIntent":
        return unsupportedShuffling()
    elif intent_name == "AMAZON.ShuffleOnIntent":
        return unsupportedShuffling()

    recentTalksList = loadMostRecentTalks()
    if recentTalksList == None:
        cardTitle = SPEECH_SYSTEM_PROBLEM
        firstSpeech = speakString(SPEECH_SYSTEM_PROBLEM)
        repromptSpeech = ""
        shouldEndSession = True
        response = buildResponse(jsonAnnouncement(cardTitle, firstSpeech, repromptSpeech, shouldEndSession))
        print(response)
        return response

    if intent_name == "PlayTalkOneIntent":
        return playTalkOne(recentTalksList)
    elif intent_name == "PlayTalkTwoIntent":
        return playTalkTwo(recentTalksList)
    elif intent_name == "PlayTalkThreeIntent":
        return playTalkThree(recentTalksList)
    elif intent_name == "PlayTalkFourIntent":
        return playTalkFour(recentTalksList)
    elif intent_name == "PlayTalkFiveIntent":
        return playTalkFive(recentTalksList)
    elif intent_name == "PlayTalkSixIntent":
        return playTalkSix(recentTalksList)

    elif intent_name == "AMAZON.NextIntent":
        return playNextTalk(recentTalksList, currentTalkURL)
    elif intent_name == "AMAZON.PreviousIntent":
        return playPreviousTalk(recentTalksList, currentTalkURL)
    elif intent_name == "AMAZON.PauseIntent":
        return pauseTalk(currentTalkURL)
    elif intent_name == "AMAZON.ResumeIntent":
        return resumeTalk(currentTalkURL, currentTalkPosition)
    elif intent_name == "AMAZON.RepeatIntent":
        return restartTalk(currentTalkURL)
    elif intent_name == "AMAZON.StartOverIntent":
        return restartTalk(currentTalkURL)
    else:
        return noop()


#
# Web Service Support 
#
def loadMostRecentTalks():
    global EXPECTED_TALK_COUNT

    recentTalksList = []
    connectionError = False

    #
    # connection to virtualdharma and get configuration
    # if there's any  error, pause for a bit and then retry one more time
    # this can actually work, as it might avoid race conditions with a config update on server side
    # but any error other than that is fatal
    #
    try:
        response = urllib2.urlopen(AD_CONFIG)
        data = json.loads(response.read())
    except:
        print("ERROR: loadMostRecentTalks 1")
        connectionError = True

    if connectionError == True:
        sleep(0.1)      # pause for 100ms
        try:
            response = urllib2.urlopen(AD_CONFIG)
            data = json.loads(response.read())
        except:
            print("ERROR: loadMostRecentTalks 2")
            return None

    talks = data["talks"]
    for talk in talks:

        if "number" not in talk: return None
        if "title" not in talk: return None
        if "date" not in talk: return None
        if "speaker" not in talk: return None
        if "url" not in talk: return None
        if "minutes" not in talk: return None

        number = talk["number"]
        title = talk["title"]
        date = talk["date"]
        speaker = talk["speaker"]
        url = talk["url"]
        minutes = talk["minutes"]
        talkAttributes = {'number': number, 'title': title, 'date' : date, 'speaker': speaker, 'url': url, 'minutes': minutes}
        recentTalksList.append(talkAttributes)

    if len(recentTalksList) !=  EXPECTED_TALK_COUNT: return None

    return recentTalksList


def reportActivity(currentUserID, currentTalkURL):
    global AD_SITE
    global AD_REPORT_ACTIVITY

    print("reportActivity")

    fileName = currentTalkURL.rsplit('/', 1)[-1]

    params = urllib.urlencode({'USERID': currentUserID, 'FILENAME': fileName})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection(AD_SITE)
    conn.request("POST", AD_REPORT_ACTIVITY, params, headers)
    response = conn.getresponse()


#
# Entry Point
#
def audiodharma_handler(event, context):
    global AD_APPLICATION_ID

    currentTalkURL = ""
    currentTalkPosition = 0
    currentUserID = "NA"

    if 'context' in event:
        if 'AudioPlayer' in event['context']:
            if 'offsetInMilliseconds' in event['context']['AudioPlayer']:
                currentTalkPosition = event['context']['AudioPlayer']['offsetInMilliseconds']
            if 'token' in event['context']['AudioPlayer']:
                currentTalkURL = event['context']['AudioPlayer']['token']
                print("CurrentTalkURL:: " + currentTalkURL)

    if 'user' in event:
        currentUserID = event['user']['userId']

    if 'session' in event:
        if event['session']['new']:
            recordSessionStarted({'requestId': event['request']['requestId']}, event['session'])
        if event['session']['application']:
            appID = event['session']['application']['applicationId']
            if (appID != AD_APPLICATION_ID): 
                print("ERROR: APPLICATION ID DOES NOT MATCH: " + appID)
                return {}

    if 'request' in event:
        print("EVENT REQUEST: " + str(event['request']))
        if event['request']['type'] == "LaunchRequest":
            if 'session' not in event:
                print('No Session')
                event['session'] = 'NONE'
            return welcomeResponse()
        elif event['request']['type'] == "IntentRequest":
            print("Intent Request")
            print(event['request'])
            return executeIntent(event['request'], event['session'], currentTalkURL, currentTalkPosition)
        elif event['request']['type'] == "SessionEndedRequest":
            return recordSessionEnded(event['request'], event['session'])
        elif event['request']['type'] == "AudioPlayer.PlaybackStarted":
            print("PlaybackStarted")
            return jsonNoneResponse()
        elif event['request']['type'] == "AudioPlayer.PlaybackFinished":
            print("PlaybackFinished")
            reportActivity(currentUserID, currentTalkURL)
            return jsonNoneResponse()

        else:
            print("Unknown Event: " + event['request']['type'])
            return jsonNoneResponse()


#
#
#
########################################################################################
# DEV AREA
#
# Not Currently Used
#
def playTopic(intent, session):
    print("play_topic")
    if 'Topic' in intent['slots']:
        topic = intent['slots']['Topic']['value']

