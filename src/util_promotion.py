#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 31 12:34:56 2019

@author: yanni
"""


from flask import Flask, request, make_response, jsonify
app = Flask(__name__)
import random
import requests
from StringMatching import stringmatching
from ValidatePromotion import validatepromo
import pandas as pd
import urllib.request, json
from collections import OrderedDict

from util_fallback import *


# ------Read excel file ------


def GetAttractionInfo (attractionName):
    df = pd.read_excel (r'Top100.xlsx')
    if type(attractionName) == str:
        attractionName = [attractionName]
    about = df.loc[df.attractions.isin(attractionName)].about.max()
    return(str(about))

def resetFallback ():
    global fallback
    fallback = None

def resetfallbacksuggestions():
    global fallbacksuggestions
    fallbacksuggestions = ["Directions" ,"Address", "Operation Hours", "Travel Time", "Introduction", "Promotions"]

# **********************
# UTIL FUNCTIONS : END
# **********************

# -------Google Map APIs---------


def getPhoto(attrname ,APIKEY='AIzaSyAgU9a5eTrwZP9pIb0eNuNRu3iPE75tR-8'):
    attrname = str(attrname).replace(" ", "")
    API_ENDPOINT = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={attrname}&inputtype=textquery&fields=photos&key={APIKEY}"
    with urllib.request.urlopen(API_ENDPOINT) as url:
        info = json.loads(url.read().decode())

    photo_ref = info['candidates'][0]['photos'][0]['photo_reference']
    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={APIKEY}"

    return photo_url


# --------RICH TEXT -----------
def carouselItem(title, url, description, footer, image_url, img_txt):
    item = {"title": title, "openUrlAction": {"url": url}}
    if description:
        item["description"] = description
    if footer:
        item["footer"] = footer
    if image_url:
        item["image"] = {"url": image_url, "accessibilityText": img_txt}
    else:
        item["image"] = {"url": "", "accessibilityText": ""}
    return item


def RichTextBasicCards(Reply, title, subtitle="", formattedText="", imageURL="", UrlButton="", *suggestionItems):
    suggestions = [{"title": item} for item in suggestionItems[0]]
    B = [{'title': "Access Promo!",
          'openUrlAction': {'url': UrlButton}}]
    texts = formattedText

    A = ({
        "title": title,
        "subtitle": subtitle,
        "formattedText": texts,
        "image": {"url": imageURL, "accessibilityText": title}
    }
    )
    Template = {
        "payload": {
            "google": {
                "expectUserResponse": True,
                "richResponse": {
                    "items": [
                        {
                            "simpleResponse": {
                                "textToSpeech": Reply
                            }
                        },
                        {"basicCard": A}
                    ],
                    "suggestions": suggestions
                }

            }
        }
    }
    if UrlButton != "":
        Template["payload"]["google"]["richResponse"]["items"][1]['basicCard']["buttons"] = B

    return Template


def simpleResponse(reply):
    Template = {
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

                    ]

                }
            }
        }
    }

    return Template


def carouselResponse(items, title, suggestionItems):
    suggestions = [{"title": item} for item in suggestionItems]
    Template = {
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
                        {"carouselBrowse": {"items": items}}
                    ],

                    "suggestions": suggestions[:21] + "..." if len(suggestions) > 25 else suggestions
                }

            }
        }
    }
    return Template


def BrowseCarouselPromo(reply, Promotions):
    carouselItems = []
    for i in Promotions:
        title = i["name"]
        desc = "NOW : $" + str(i["price"]) + " Savings : $" + str(i["savings"]) + "0"
        photo = i["img_url"]
        url = i["url"]
        footer = "Original Price : $" + str(i["oprice"])
        carouselItems.append(carouselItem(title, url, desc, footer, photo, title))

    return carouselResponse(carouselItems, reply, "")


# --------Default Fallback ----------
def OtherTextHandler():
    text = ["I didn't get that. Can you say it again?",
            "Sorry, could you say that again?",
            "Sorry, I didn't get that. Can you rephrase?",
            "What was that?",
            "One More time?"]

    tutorialtext = [""]
    return (simpleResponse(text[random.randrange(0, 1)]))


def SingleAttractionHandler(attraction):
#    global lastAttraction

    x = len(validatepromo(attraction))
    lastAttraction = attraction
    option1 = " Directions"
    option2 = " Address"
    option3 = " Operation Hours"
    option4 = " Travel Time"
    option5 = " Introduction"
    option6 = " Promotions"
    reply = ["Oh! I know!! " + str(attraction) + "!\n" + "Here's some basic information about this attraction.\n",
             "Cool! So it's " + str(
                 attraction) + "!\n" + "What other information would you like to know about this attraction?\n"]
    if len(GetAttractionInfo(attraction)) >= 100:
        reply = str(attraction) + ". " + GetAttractionInfo(attraction)
        if x > 0:
            attractiondesc = "We have got " + str(
                len(validatepromo(attraction))) + " promotions found for " + attraction + "!"
        else:
            attractiondesc = ""
    else:
        attractiondesc = GetAttractionInfo(attraction)[:500] + "..." if len(
            GetAttractionInfo(attraction)) >= 500 else GetAttractionInfo(attraction)

        if x > 0:
            reply = "Oh! I know!! " + str(attraction) + "!\n" + "We have found " + str(
                x) + " promotions for this atttraction."
        else:
            reply = reply[random.randrange(0, 1)]
    suggestions = [option1, option2, option3, option4, option6]

    try:
        photo = getPhoto(attraction)
    except:
        photo = ""
    return (RichTextBasicCards(reply, attraction, "", attractiondesc, photo, "", suggestions))


def MultiAttractionHandler(listofattraction):
    reply = "Which of the following attractions:"
    suggestions = []
    carouselItems = []

    for i in listofattraction:
            desc = GetAttractionInfo(i)[:70] + "..." if len(GetAttractionInfo(i)) >= 100 else GetAttractionInfo(i)
            try:
                photo = getPhoto(i)
            except:
                photo = 'https://cdn.webshopapp.com/shops/94414/files/54943038/singapore-flag-image-free-download.jpg'
            carouselItems.append(
                carouselItem(i, "https://www.google.com/search?q=" + i.replace(" ", "%20"), desc, "", photo, i))
            suggestions.append(i[:21] + "..." if len(i) > 25 else i)
            j=+1

    return carouselResponse(carouselItems, reply, suggestions)


# --------Promotions ----------

# *****************************
# Intent Handlers funcs : START
# *****************************
def FallbackIntentHandler(req):
    global Fallback
    listofattractions = stringmatching(req)
    if len(listofattractions) != 0:
        totalreturn = len(listofattractions)
        if totalreturn == 1:
            Fallback = 1
            return (SingleAttractionHandler(listofattractions[0]))


        else:
            listofattractions = listofattractions
            return MultiAttractionHandler(listofattractions)
    else:

        return (OtherTextHandler())


def GetPromotionsIntent(req):
    global fallbacksuggestions
    allpromos = validatepromo(req)
    x = len(allpromos)
    if x > 1:
        reply = "We have found some promotions for you!"
        response = BrowseCarouselPromo(reply, allpromos)

    elif x == 1:
        reply = "This is what we have for you!"
        for i in allpromos:
            title = i["name"]
            desc = "NOW : $" + str(i["price"]) + " Savings : $" + str(i["savings"]) + "0"
            photo = i["img_url"]
            url = i["url"]
            subtitle = "Original Price : $" + str(i["oprice"])
            suggestion = fallbacksuggestions
            response = RichTextBasicCards(reply, title, subtitle, desc, photo, url, suggestion)
            resetfallbacksuggestions()

    else:
        reply = "I'm Sorry! No promotions found for this attraction"
        response = simpleResponse(reply)
    return (response)


