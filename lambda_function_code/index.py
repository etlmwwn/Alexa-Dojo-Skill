"""
This code sample is a part of a simple demo to show beginners how to create a skill (app) for the Amazon Echo using AWS Lambda and the Alexa Skills Kit.

For the full code sample visit https://github.com/pmckinney8/Alexa_Dojo_Skill.git
"""

from __future__ import print_function

# Import for AWS IOT Connection & JSON to package the data for MQTT Messaging

import boto3
import json

client = boto3.client('iot-data', region_name='us-east-1')

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "ColourIntent":
        return get_colour_response(intent_request)
    elif intent_name == "AMAZON.HelpIntent":
        return get_help_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here
    
# --------------- Functions that control the skill's behavior ------------------

def mqtt(rgb):
    client = boto3.client('iot-data', region_name='us-east-1')
    #json_map = {}
    #json_map["colour"] = rgb
    response = client.publish(
        topic='colour',
        qos=1,
        payload=json.dumps({"colour":"%s"}) % rgb
    )

def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome! What Colour would you like to set?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with the same text.
    reprompt_text = speech_output
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_help_response():
    session_attributes = {}
    card_title = "Help"
    speech_output = "Welcome to the help section for the colour skill. A couple of examples of phrases that I can except are... Set colour to... Lets get started now by trying one of these."

    reprompt_text = speech_output
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(card_title,speech_output,reprompt_text,should_end_session))


def get_colour_response(intent_request):
    session_attributes = {}
    card_title = "Colour_Response"
    speech_output = ""
    colour = intent_request["intent"]["slots"]["Colour"]["value"]
    dict = {'red':'230,25,75','green':'60,180,75','yellow':'255,225,25','blue':'0,130,200','orange':'245,130,48','purple':'145,30,180','cyan':'70,40,240','magneta':'240,50,230','lime':'210,245,60','pink':'250,190,190','teal':'0,128,128','lavendar':'230,190,255','brown':'170,110,40','beige':'255,250,200','maroon':'128,0,0','mint':'170,255,195','olive':'128,128,0','coral':'255,215,180','navy':'0,0,128','grey':'128,128,128','white':'255,255,255','black':'0,0,0'}

    rgb = dict.get(colour)

    if dict.get(colour) is not None:
        mqtt(rgb)
        speech_output = "The colour is set to %s" % (colour)
    else:
        speech_output = "Sorry, this isn't the %s you are looking for" % colour
    reprompt_text = speech_output
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(card_title,speech_output,reprompt_text,should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using the colour magic skill! We hope you enjoyed the experience."
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

# --------------- Helpers that build all of the responses ---------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
