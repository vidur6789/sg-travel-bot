#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 10:35:42 2019

@author: yanni
"""
import requests


# get Attraction Info Intent Handler
def getAttrInfoIntentHandler(attrname, APIKEY):
    intro = getIntroInfo(attrname)
    photo_url = getPhoto(attrname, APIKEY)

    # Rich Text
    result_obj = {
        "payload": {
            "google": {
                "expectUserResponse": True,
                "richResponse": {
                    "items": [
                        {
                            "simpleResponse": {
                                "textToSpeech": " "
                            }
                        },
                        {
                            "basicCard": {
                                "title": attrname,
                                "subtitle": "",
                                "formattedText": "" + intro,
                                "image": {
                                    "url": photo_url
                                },
                                "imageDisplayOptions": "CROPPED"
                            }
                        }
                    ],
                    "suggestions": [
                        {
                            "title": "Promotion"
                        },
                        {
                            "title": "Operation Time"
                        },
                        {
                            "title": "Direction"
                        },
                        {
                            "title": "Travel Duration"
                        },
                        {
                            "title": "Address"
                        }
                    ],
                    "linkOutSuggestion": {
                        "destinationName": "Suggestion Link",
                        "url": "https://assistant.google.com/"
                    }
                }
            }
        }
    }

    return result_obj


# get Introduction Info
def getIntroInfo(attrname):
    API_ENDPOINT = f"http://localhost:8001/attractions?name={attrname}"

    data = getjson(API_ENDPOINT)

#    f = open('attraction_checklist.txt', encoding='utf-8')
    f = open('/Users/yanni/downloads/Import/attraction_checklist.txt', encoding='utf-8')
    checklist = f.readline().lower().split(",")

    check_result = attrname.lower() in checklist

    if data:
        if data[0]['description']:
            intro = data[0]['description']
            return intro
        else:
            return f"Sorry, we do not have introduction of {attrname}"
    else:
        return f"Sorry, we do not have introduction of {attrname}"


# get Photo Url
def getPhoto(attrname, APIKEY):
    API_ENDPOINT = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={attrname}&inputtype=textquery&fields=photos&key={APIKEY}"
    info = getjson(API_ENDPOINT)

    photo_ref = info['candidates'][0]['photos'][0]['photo_reference']
    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={APIKEY}"

    return photo_url


# get json
def getjson(url):
    resp = requests.get(url)
    return resp.json()
