#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 10:32:23 2019

@author: yanni
"""

#! /usr/bin/env python
from flask import Flask, request, make_response, jsonify
import requests
import json
import re
import time
import pandas as pd
import googlemaps
import StringMatching
from dateutil.parser import parse
#import utilities
from util_intro import *
from util_operTime import *
from util_duration import *
from util_addr import *
from util_weather import *
from util_direc import *
from util_promotion import *
from util_fallback import *
from util_recom import *
from util_events import *
from util_recommendation import *

app = Flask(__name__)

#Define Intents/Entities Table
REC_INTENTS = ['RecommendationIntent','TravellerTypeIntent', 'CategoryIntent', 'UserInfo','RecomTypeIntent','EventDurationIntent']
INFO_ENTITIES = ['introduction','something', 'open', 'address', 'duration']

#Google Maps API KEYS#
APIKEY = {APIKEY}

#Load database#
 
dataAPI = 'http://localhost:8001/attractions?attractions'
data = getjson(dataAPI)

global lastAttraction
lastAttraction = None


# *****************************
# WEBHOOK MAIN ENDPOINT : START
# *****************************
@app.route('/', methods=['POST'])
def webhook():
    
    global lastAttraction
    req = request.get_json(silent=True, force=True)
    intent_name = req["queryResult"]["intent"]["displayName"]

    resp_rich = ''
    Response = ''
    respose = ''
    resp_text = ''
    resp_dict = ''
    matched_attrname = ''

    #Attraction Info Intent
    if intent_name == "GetAttrInfoIntent":
        
        entityname = req["queryResult"]["parameters"]["attrentity"]
        attrname = req["queryResult"]["parameters"]["attrname"]
        if attrname:
            lastAttraction = attrname
        else: 
            attrname = lastAttraction
        
        if attrname:
            matched_attrname = StringMatching.stringmatching(attrname)[0]
        
        date = req["queryResult"]["parameters"]["date"]
        origin = req["queryResult"]["parameters"]["origin"]
        destination = req["queryResult"]["parameters"]["destination"]


        ind = -1

        #Entity Check
        if entityname in INFO_ENTITIES:
            
            for i in data:
                if matched_attrname.lower() == i['name'].lower():
                    ind = 1
            if ind == 1:
                if entityname == "introduction":
                    resp_rich = getAttrInfoIntentHandler(matched_attrname,APIKEY)
                elif entityname == "something":
                    resp_rich = getAttrInfoIntentHandler(matched_attrname,APIKEY)
                elif entityname == "open":
                    resp_text = getAttrOperTimeIntentHandler(date,matched_attrname,APIKEY)
                elif entityname == "duration":
                    resp_text = getAttrDuraIntentHandler(matched_attrname)
                elif entityname == 'address':
                    resp_text = getAttrAddrIntentHandler(matched_attrname,APIKEY)
                    
            else:
                resp_text = f"We do not have the information for {attrname} yet. Please try other attractions."

        elif entityname == 'direction' and origin and destination:
            matched_origin = StringMatching.stringmatching(origin)[0]
            matched_destination = StringMatching.stringmatching(destination)[0]
            resp_rich = getDirecIntentHandler(matched_origin, matched_destination)
            
        elif entityname == 'direction' and destination:
            matched_destination = StringMatching.stringmatching(destination)[0]
            resp_rich = getDirecIntentHandler(origin, matched_destination)
        elif entityname == 'direction' and origin:
            destination = origin
            origin = ''
            matched_destination = StringMatching.stringmatching(destination)[0]
            resp_rich = getDirecIntentHandler(origin, matched_destination)
        elif entityname == 'direction':
            origin = ''
            resp_rich = getDirecIntentHandler(origin,matched_attrname)
        elif entityname == 'weather':
            resp_text = getWeather(date)
            
        else:
            resp_text = "Unable to find a matching category. Try again."
    
    #Promotion Intent
    elif intent_name == 'Default Fallback Intent' or intent_name == 'actions.intent.TEXT':
        usertext = req["queryResult"]["queryText"]
        Response = FallbackIntentHandler(usertext)

    elif intent_name == 'Search':
        attrname = req["queryResult"]["parameters"]["attrname"]
        Response = FallbackIntentHandler(attrname)

    elif intent_name == 'GetPromotionsIntent':
        attrname = req["queryResult"]["parameters"]["attrname"]
        if attrname == '':
            attrname = lastAttraction
            
        matched_attrname = StringMatching.stringmatching(attrname)[0]

        Response = GetPromotionsIntent(matched_attrname)
        resetFallback()
    
    #Recommendation Intent
    elif intent_name in REC_INTENTS:

        if 'keylabel' in req['queryResult']['parameters'] and req["queryResult"]["parameters"]["keylabel"]:
            resp_dict = suggestionChipsResponse("What kind of things?", "Attractions", "Events")
            update_slots(req)

        else:  # attractions
            log_session(req)
            update_slots(req)
            resp_dict = recommendationIntentHandler(req)
    
    #Event Intent
    elif intent_name == "GetEventIntent":
        date_period = req["queryResult"]["parameters"]["date-period"]
        events_name = req["queryResult"]["parameters"]["events-name"]
        interrogative = req["queryResult"]["parameters"]["interrogative"]
        interrogative = interrogative.lower()
        if date_period:
            resp_dict = getEventIntentHandler(date_period)
            respose = jsonify(resp_dict)
        elif events_name:
            if interrogative == "when":
                respose_text = getEventDurationIntentHandler(events_name)
                respose = jsonify({'fulfillmentText': respose_text})
            elif interrogative == "what" or "tell me":
                respose = getEventDescriptionIntentHandler(events_name)
            else:
                respose_text = "Unable to find a match. Try again."
                respose = jsonify({'fulfillmentText': respose_text})

        
    else:
        resp_text = "Unable to find a matching intent. Try again."

        
    if resp_rich:
        return make_response(jsonify(resp_rich))
    elif Response:
        return make_response(jsonify(Response))
    elif respose:
        return make_response(respose)
    elif resp_dict:
        return make_response(jsonify(resp_dict))
    else:
        return make_response(jsonify({'fulfillmentText': resp_text}))
    

# ***************************
# WEBHOOK MAIN ENDPOINT : END
# ***************************

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5000)
