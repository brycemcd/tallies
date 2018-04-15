"""
This sample is adapted from an example in Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import boto3
import json
import datetime as dt
import os

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName=os.getenv('TALLY_QUEUE_NAME', 'tallies-dev-and-test'))
error_queue = sqs.get_queue_by_name(QueueName=os.getenv('ERROR_QUEUE_NAME','tallies-errors-dev'))


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session, with_card=True):
    card = {
        'card': {
            'type': 'Simple',
            'title': "TallyApp - " + title,
            'content': "TallyApp - " + output
        }
    }

    resp = {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },

        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

    if with_card:
        return {**resp, **card}
    else:
        return {**resp}


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = """ What would you like to tally? """
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = """
    Welcome to the Tally app. You can say beer or vodka to tally a drink
    """
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = """You tallied like a boss"""

    # Setting this to true ends the session and exits the skill.
    should_end_session = True

    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_favorite_color_attributes(favorite_color):
    return {"favoriteColor": favorite_color}


def set_color_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Color' in intent['slots']:
        favorite_color = intent['slots']['Color']['value']
        session_attributes = create_favorite_color_attributes(favorite_color)
        speech_output = "I now know your favorite color is " + \
                        favorite_color + \
                        ". You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
        reprompt_text = "You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your favorite color is. " \
                        "You can tell me your favorite color by saying, " \
                        "my favorite color is red."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_color_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "favoriteColor" in session.get(
            'attributes', {}):
        favorite_color = session['attributes']['favoriteColor']
        speech_output = "Your favorite color is " + favorite_color + \
                        ". Goodbye."
        should_end_session = True
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "You can say, my favorite color is red."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


def tally_one_drink(drink, intent, cnt=1):
    """puts a tally on a queue"""

    session_attributes = {}
    speech_output = "Whoa - %s %s" % (cnt, drink)
    reprompt_text = "You're too drunk. Try again."

    queued_msg = {
        "tally_cnt": cnt,
        "tally_type": drink,
        "message_created_dttm": dt.datetime.now().isoformat(timespec='seconds'),
        "intent": intent,
    }

    queue.send_message(MessageBody=json.dumps(queued_msg))

    speechlet_response = build_speechlet_response(intent['name'],
                                                  speech_output,
                                                  reprompt_text,
                                                  False,
                                                  with_card=False)

    return build_response(session_attributes, speechlet_response)


def tally_generic(intent, session):
    """tallies one generic"""

    drink = intent['slots']['drink']['value']
    cnt = intent['slots']['cnt'].get('value', 1)
    return tally_one_drink(drink, intent, cnt)


# --------------- events ------------------

def on_session_started(session_started_request, session):
    """ called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])


    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # dispatch to your skill's intent handlers
    if intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    elif intent_name == "tallyBeverage":
        return tally_generic(intent, session)
    else:
        error_queue.send_message(MessageBody=json.dumps({**intent_request,
                                                         "type": "invalid_intent"}))
        raise ValueError("invalid intent")


def on_session_ended(session_ended_request, session):
    """ called when the user ends the session.

    is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- main handler ------------------

def lambda_handler(event, context):
    """ route the incoming request based on type (launchrequest, intentrequest,
    etc.) the json body of the request is provided in the event parameter.
    """

    """
    uncomment this if statement and populate with your skill's application id to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationid'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise valueerror("invalid application id")

    error_queue.send_message(MessageBody=json.dumps({**event, "type": "event"}))

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
