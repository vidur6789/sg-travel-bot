#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 11:03:54 2019

@author: yanni
"""
import requests
import json


#get Attraction Suggested traveling Duration Intent Handler
def getAttrDuraIntentHandler(attrname):

    duration = getAttrDuraTime(attrname)
    if duration != []:
        duration0 = int(duration[0])
        duration1 = int(duration[1])
        if duration1 == -1:
            return f"The suggested traveling duration of {attrname} is more than {duration0} hours"
        else:
            return f"The suggested traveling duration of {attrname} is from {duration0} hours to {duration1} hours"
    else:
        return f"Sorry, we do not have the suggested travel duration for you"
    # else:
    #     return f"The suggested traveling duration is {duration}"

#get Attraction Duration Time
def getAttrDuraTime(attrname):

    duration = []
    API_ENDPOINT = f"http://localhost:8001/attractions?name={attrname}"
    data = getjson(API_ENDPOINT)
    if data[0]['recommendedDuration']:
        duration_from = data[0]['recommendedDuration']['from']
        duration_to = data[0]['recommendedDuration']['to']
        duration = [duration_from,duration_to]
    return duration


def getjson(url):
    resp =requests.get(url)
    return resp.json()
