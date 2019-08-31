#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 31 12:39:03 2019

@author: Donal
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


fallback = None
fallbacksuggestions = ["Directions" ,"Address", "Operation Hours", "Travel Time", "Introduction", "Promotions"]



def resetFallback ():
    global fallback
    fallback = None

def resetfallbacksuggestions():
    global fallbacksuggestions
    fallbacksuggestions = ["Directions" ,"Address", "Operation Hours", "Travel Time", "Introduction", "Promotions"]

# **********************
# UTIL FUNCTIONS : END
# **********************


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
# def PromotionsHandler (allpromos):


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



