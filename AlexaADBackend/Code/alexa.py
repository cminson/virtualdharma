from __future__ import print_function
import urllib
import httplib
import urllib2
import json
from time import sleep

EXPECTED_TALK_COUNT = 5
AD_SITE = "www.virtualdharma.org:80"
AD_REPORT_ACTIVITY = "/AlexaADBackend/Access/reportactivity.php"

AD_CONFIG = "http://virtualdharma.org/AlexaADBackend/Config/ALEXATALKS00.JSON"
AD_APPLICATION_ID = "amzn1.ask.skill.03d50eb2-f557-47cb-a256-bac3cdc78515"

# constant strings 
C_SPEECH_WELCOME = "Audio Dharma. Here are today's <emphasis>five</emphasis> Dharma talks - the two most recent talks followed by <emphasis>three</emphasis> randomly selected talks. <break time=\"1s\"/>"
C_SPEECH_USERPROMPT = "Select your talk.  For example, you can say:  Alexa, play talk 3."
C_SPEECH_WELCOME_REPROMPT = "To play a talk, say the talk number.  For example, you can say:  Alexa, play talk 3."

C_CARD_WELCOME_TITLE = "Welcome To Audio Dharma"
C_CARD_WELCOME_TEXT = "Welcome to Audio Dharma. Thousands of Dharma talks given by hundreds of teachers from around the world, representing a variety of traditions and viewpoints. You can find the complete list of talks at www.audiodharma.org.\r\n \r\n Here are the most recent two talks, followed by three randomly selected  talks."
C_CARD_WELCOME_HELP = "To play a talk say the talk number.  For example:  Alexa, play talk 3."

C_SPEECH_HELP = "Talks are listed from number one to number five. To play a talk, say the talk number.  For example, you can say:  Alexa, play talk 2. Once inside a talk you can also move between talks by saying:  Alexa, next talk or:  Alexa, previous talk."

# globals that can set by constants above OR remotely via loadMostRecentTalks
SPEECH_WELCOME = ""
SPEECH_WELCOME_REPROMPT = ""
SPEECH_USERPROMPT = ""
CARD_WELCOME_TITLE = ""
CARD_WELCOME_TEXT = ""
CARD_WELCOME_HELP = ""

SPEECH_HELP = ''

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

def helpResponse():

    global SPEECH_HELP

    firstSpeech = speakString(SPEECH_HELP)

    cardTitle = CARD_WELCOME_TITLE
    cardText = SPEECH_HELP

    shouldEndSession = False
    response = buildResponse(jsonAnnouncement(cardTitle, cardText, firstSpeech, "", shouldEndSession))
    print(response)
    return response




def welcomeResponse():

    global SPEECH_WELCOME
    global SPEECH_USERPROMPT
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
        shouldEndSession = False
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
        speaker = ".  By " + talk['speaker']
        minutes = talk['minutes'] + " minutes"

        welcome += number
        welcome += ":  "
        welcome += title
        welcome += "<break time=\"0.5s\"/>"
        welcome += " given on "
        welcome += date
        welcome += ". "
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
        welcomeText += "   "
        welcomeText += date
        welcomeText += "   "
        welcomeText += "\r\n "
        welcomeText += speakerText
        welcomeText += "   "
        welcomeText += minutes

    welcomeText += "\r\n "
    welcomeText += "\r\n "
    welcomeText += CARD_WELCOME_HELP

    welcome += SPEECH_USERPROMPT
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
    shouldEndSession = True

    response = buildResponse(jsonAnnouncement(cardTitle, cardText, speechOutput, reprompt_text, shouldEndSession))
    print(response)
    return response


def unsupportedShuffling():

    global SPEECH_SHUFFLING_UNSUPPORTED

    cardTitle = SPEECH_SHUFFLING_UNSUPPORTED
    cardText = ""
    speechOutput = speakString(SPEECH_SHUFFLING_UNSUPPORTED)
    reprompt_text = ""
    shouldEndSession = True
    response = buildResponse(jsonAnnouncement(cardTitle, cardText, speechOutput, reprompt_text, shouldEndSession))
    print(response)
    return response


def noop():

    print("noop")
    response = buildResponse(jsonNoop())
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

    title = recentTalksList[0]['title']
    return playTalk("Playing Talk One: " + title, 0, recentTalksList)


def playTalkTwo(recentTalksList):

    title = recentTalksList[1]['title']
    return playTalk("Playing Talk Two: " + title, 1, recentTalksList)


def playTalkThree(recentTalksList):

    title = recentTalksList[2]['title']
    return playTalk("Playing Talk Three: " + title, 2, recentTalksList)


def playTalkFour(recentTalksList):

    title = recentTalksList[3]['title']
    return playTalk("Playing Talk Four: " + title, 3, recentTalksList)


def playTalkFive(recentTalksList):

    title = recentTalksList[4]['title']
    return playTalk("Playing Talk Five: " + title, 4, recentTalksList)


def playTalkSix(recentTalksList):

    title = recentTalksList[5]['title']
    return playTalk("Playing Talk Six: " + title, 5, recentTalksList)


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

    title = recentTalksList[currentTalkTrack]['title']
    return playTalk("Playing Next Talk: " + title, currentTalkTrack, recentTalksList)


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

    title = recentTalksList[currentTalkTrack]['title']
    return playTalk("Playing Previous Talk: " + title, currentTalkTrack, recentTalksList)



def pauseTalk(currentTalkURL):
    response = jsonStopTalk(currentTalkURL)
    print(response)
    return response


def resumeTalk(currentTalkURL, currentTalkPosition):
    print("resume talk: " + currentTalkURL + " " + str(currentTalkPosition))
    response = jsonResumeTalk(currentTalkURL, currentTalkPosition)
    print(response)
    return response


def repeatPhraseInTalk(currentTalkURL, currentTalkPosition):
    print("repeat talk: " + currentTalkURL + " " + str(currentTalkPosition))

    currentTalkPosition -= (15 * 1000)
    if currentTalkPosition < 0: currentTalkPosition = 0

    print("repeat talk: " + currentTalkURL + " " + str(currentTalkPosition))
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

    elif intent_name == "AMAZON.NextIntent":
        return playNextTalk(recentTalksList, currentTalkURL)
    elif intent_name == "AMAZON.PreviousIntent":
        return playPreviousTalk(recentTalksList, currentTalkURL)
    elif intent_name == "AMAZON.PauseIntent":
        return pauseTalk(currentTalkURL)
    elif intent_name == "AMAZON.ResumeIntent":
        return resumeTalk(currentTalkURL, currentTalkPosition)
    elif intent_name == "AMAZON.RepeatIntent":
        return repeatPhraseInTalk(currentTalkURL, currentTalkPosition)
    elif intent_name == "AMAZON.StartOverIntent":
        return restartTalk(currentTalkURL)
    elif intent_name == "AMAZON.HelpIntent":
        return helpResponse()
    else:
        return noop()


#
# Web Service Support 
#
def loadMostRecentTalks():

    global EXPECTED_TALK_COUNT

    global C_SPEECH_WELCOME
    global C_SPEECH_WELCOME_REPROMPT
    global C_SPEECH_USERPROMPT
    global C_CARD_WELCOME_TITLE
    global C_CARD_WELCOME_TEXT
    global C_CARD_WELCOME_HELP
    global C_SPEECH_SYSTEM_PROBLEM
    global C_SPEECH_HELP

    global SPEECH_WELCOME
    global SPEECH_WELCOME_REPROMPT
    global SPEECH_USERPROMPT
    global CARD_WELCOME_TITLE
    global CARD_WELCOME_TEXT
    global CARD_WELCOME_HELP
    global SPEECH_HELP

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
    
    #
    # set globalspeech and text output
    # this is be set via constants but can be over-ridden remotedly via the json config
    # we do it in this indirect fashion so our lambda function remains operationally idempotent
    #
    SPEECH_WELCOME = C_SPEECH_WELCOME
    SPEECH_USERPROMPT = C_SPEECH_USERPROMPT
    SPEECH_WELCOME_REPROMPT = C_SPEECH_WELCOME_REPROMPT
    CARD_WELCOME_TITLE = C_CARD_WELCOME_TITLE
    CARD_WELCOME_TEXT = C_CARD_WELCOME_TEXT
    CARD_WELCOME_HELP = C_CARD_WELCOME_HELP
    SPEECH_HELP = C_SPEECH_HELP

    if "SPEECH_WELCOME" in data:
        SPEECH_WELCOME = data["SPEECH_WELCOME"]
    if "SPEECH_USERPROMPT" in data:
        SPEECH_USERPROMPT = data["SPEECH_USERPROMPT"]
        print("Setting UserPrompt: " + SPEECH_USERPROMPT)
    if "SPEECH_WELCOME_REPROMPT" in data:
        SPEECH_WELCOME_REPROMPT = data["SPEECH_WELCOME_REPROMPT"]
    if "CARD_WELCOME_TITLE" in data:
        CARD_WELCOME_TITLE = data["CARD_WELCOME_TITLE"]
    if "CARD_WELCOME_TEXT" in data:
        CARD_WELCOME_TEXT = data["CARD_WELCOME_TEXT"]
    if "CARD_WELCOME_HELP" in data:
        CARD_WELCOME_HELP = data["CARD_WELCOME_HELP"]
    if "SPEECH_HELP" in data:
        SPEECH_HELP = data["SPEECH_HELP"]

    # now gather talks themselves
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

    #print("TALKS LOADED.  Count = " + str(len(recentTalksList)))
    if len(recentTalksList) !=  EXPECTED_TALK_COUNT: return None

    #print("SUCCESS TALKS LOADED")
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

