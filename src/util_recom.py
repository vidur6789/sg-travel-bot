#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 14:49:26 2019

@author: Vidur and Yifei
"""

from flask import Flask, request, make_response, jsonify
import requests
from StringMatching import stringmatching
import googlemaps

TRIPPINGO_URL="http://3d38749b.ngrok.io"
gmaps = googlemaps.Client(key='AIzaSyAuoXXfgfRxQCrBlRFeDsEbTtwbDil-g3k')

currentLocationPhrasings = ['near me', 'around me', 'nearby']

userInfo = {"travellerType": None,
            "currentLocation": "Singapore"}

slots = {"travellerType": None,
         "category": None,
         "location": None,
         "keywords":None}



# **********************
# UTIL FUNCTIONS : START
# **********************


def getjson(url):
    resp =requests.get(url)
    return resp.json()


def resetRecommendationSlots():
    global slots
    slots["travellerType"] = None
    slots["category"] = None
    slots["location"] = None
    slots["keywords"] = None


def getDeviceLocation(req):
    payload = req['originalDetectIntentRequest']['payload']
    if 'device' in payload and 'location' in payload['device']:
        return payload['device']['location']
    else:
        return None



def update_slots(req):
    global slots
    global userInfo
    parameters = req['queryResult']['parameters']
    # TRAVELLER TYPE
    if 'travellerType' in parameters and parameters['travellerType']:
        slots['travellerType'] = parameters['travellerType']
        userInfo['travellerType'] = parameters['travellerType']
    else:
        slots['travellerType'] = userInfo['travellerType']
    # CATEGORY
    if 'category' in parameters and parameters['category']:
        slots['category'] = parameters['category']
    #KEYWORDS
    if 'keywords' in parameters and parameters['keywords']:
        keyword = parameters['keywords']
        matches = stringmatching(keyword)
        keyword = matches[0] if matches else parameters['keywords']
        slots['keywords'] = keyword
    # LOCATION
    if 'location' in parameters and parameters['location']:
        slots['location'] = parameters['location']
        userInfo['currentLocation'] = parameters['location']
    elif getDeviceLocation(req):
        slots['location'] = req['originalDetectIntentRequest']['payload']['device']['location']
        userInfo['currentLocation'] = slots['location']
    else:
        slots['location'] = userInfo['currentLocation']


def isRecommendationPossible(req):
    return (slots['category'] or slots['keywords']) \
           and slots['travellerType'] \
           and slots['location'] \
           and slots['location'] not in currentLocationPhrasings

def parseLocation(req):
    global location_context
    location = req["queryResult"]["parameters"]["location"]
    if location == '':
        return location_context
    location_names = []
    if location['street-address'] != '':
        location_names.append(location['street-address'])
    if location['subadmin-area'] != '':
        location_names.append(location['subadmin-area'])
    if location['city'] != '':
        location_names.append(location['city'])
    if location['country'] != '':
        location_names.append(location['country'])
    location_name = ",".join(location_names)
    location_context = location_name  # update location_context to remember the last used location
    return location_name


def getCombinedKeywords():
    keywordsList = []
    if slots['keywords']:
        keywordsList.append(slots['keywords'])
    if slots['category']:
        keywordsList.extend(slots['category'])
    return ",".join(keywordsList)




def trippingoCarouselItem(item,APIKEY):
    name = item['name']
    return carouselItem(name, getDirectionsLink("", name), "", "", getPhoto(name,APIKEY), "")


def getDirectionsLink(fromPostal, toPostal):
    fromLoc = "Singapore+"+fromPostal if fromPostal else ""
    toLoc = "Singapore+"+toPostal
    return "https://www.google.com/maps/dir/{fromLoc}/{toLoc}/".format(fromLoc=fromLoc, toLoc=toLoc)


def getPhoto(attrname,APIKEY):
    API_ENDPOINT = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={attrname}&inputtype=textquery&fields=photos&key={APIKEY}".format(attrname=attrname,APIKEY=APIKEY)
    info = getjson(API_ENDPOINT)
    photo_ref = info['candidates'][0]['photos'][0]['photo_reference']
    photo_url = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={APIKEY}".format(photo_ref=photo_ref, APIKEY=APIKEY)
    return photo_url


def carouselItem(title, url, description, footer, image_url, img_txt):
    item = {"title": title, "openUrlAction": {"url": url}}
    if description:
        item["description"] = description
    if footer:
        item["footer"] = footer
    if image_url:
        item["image"] = {"url": image_url, "accessibilityText": img_txt}
    return item


def carouselResponse(items, title):
    return {
        "payload": {
            "google": {
                "expectUserResponse": True,
                "richResponse": {
                    "items": [
                        {
                            "simpleResponse": {
                                "textToSpeech": title
                            }
                        },
                        {
                            "carouselBrowse": {
                                "items": items
                            }
                        }
                    ]
                }
            }
        }
    }


def suggestionChipsResponse(reply, *suggestionItems):
    suggestions = [{"title": item} for item in suggestionItems]
    return {
        "payload": {
            "google": {
                "expectUserResponse": True,
                "richResponse": {
                    "items": [
                        {
                            "simpleResponse": {
                                "textToSpeech": reply
                            }
                        }
                    ],
                    "suggestions": suggestions,
                    "linkOutSuggestion": {
                        "destinationName": "Suggestion Link",
                        "url": "https://assistant.google.com/"
                    }
                }
            }
        }
    }


def locationPermissionResponse(req):
    location_request = {
        "payload": {
            "google": {
                "expectUserResponse": True,
                "systemIntent": {
                    "intent": "actions.intent.PERMISSION",
                    "data": {
                        "@type": "type.googleapis.com/google.actions.v2.PermissionValueSpec",
                        "optContext": "To address you by name and know your location",
                        "permissions": [
                            "NAME",
                            "DEVICE_PRECISE_LOCATION"
                        ]
                    }
                }
            }
        }
    }
    return location_request


def fulfillmentTextResponse(resp_text):
    return {'fulfillmentText': resp_text}



# **********************
# UTIL FUNCTIONS : END
# **********************

# *****************************
# Intent Handlers funcs : START
# *****************************

def recommendationIntentHandler(req,APIKEY):
    if isRecommendationPossible(req):
        recItems = getRecommendations(req,APIKEY)
        resetRecommendationSlots()
        return carouselResponse(recItems, "Here are some recommendations for you")
    else:
        return requestRemainingSlots(req)



# returns list of DialogFlow carousel items as recommendations
def getRecommendations(req,APIKEY):
    carouselItems = trippingoRecommendations(req,APIKEY)
    if not carouselItems:
        carouselItems  = googleRecommendations(req)
    return carouselItems;


# returns list of DialogFlow carousel items as recommendations
def trippingoRecommendations(req,APIKEY):
    keywords = getCombinedKeywords();
    travellerType = slots['travellerType'].title()
    url = TRIPPINGO_URL+"/recommendations?keywords={keywords}&travellerType={travellerType}&count=3".format(keywords=keywords,travellerType=travellerType);
    api_response = getjson(url)
    carouselItems = [trippingoCarouselItem(item,APIKEY) for item in api_response]
    return carouselItems

def getNearbyRecom(category):

    geolocate_result = gmaps.geolocate()
    geolocate = geolocate_result['location']

    if category == 'garden' or category == 'gardens' or category == 'park' or category =='parks':
        typename = 'park'
    elif category == 'aquarium' or category =='water':
        typename = 'aquarium'
    elif category == 'gallery' or category =='galleries':
        typename = 'art_gallery'
    elif category == 'church' or category =='churches':
        typename = 'church'
    elif category == 'temple' or category =='temples':
        typename = 'hindu_temple'
    elif category =='mosque' or category =='mosques':
        typename = 'mosque'
    elif category == 'museum' or category =='museums':
        typename = 'museum'
    elif category == 'shopping' or category =='mall' or category =='shopping mall' or category =='malls':
        typename = 'shopping_mall'
    elif category == 'zoo'or category == 'zoos':
        typename = 'zoo'

    places_nearby_result = gmaps.places_nearby(location=geolocate,rank_by='prominence',radius=5000,type=typename)
    
    places_nearby = places_nearby_result['results']

    recom_nearby = ['','','']
    a = 0
    for i in range(len(places_nearby)):
    	if a<3:
    		recom_nearby[a] = places_nearby[i]['name']
    		a = a+1
    	else:
    		break
    return recom_nearby


# returns list of DialogFlow carousel items as recommendations
def googleRecommendations(req,APIKEY):
    category = slots["category"]
    names = getNearbyRecom(category)
    return [carouselItem(name, getDirectionsLink("", name), "", "", getPhoto(name,APIKEY), "") for name in names]


def requestRemainingSlots(req):
    if not slots['travellerType']:
        return suggestionChipsResponse("Who are you travelling with?", "Family", "Couple", "Friends", "Solo", "Office colleagues")
    if not slots['category'] and not slots['keywords']:
        return suggestionChipsResponse("What kind of places do you like to visit?", "Nature & Parks", "Shopping Streets", "City Landmarks", "Museums")
    if slots['location'] in currentLocationPhrasings:
        return locationPermissionResponse(req)
