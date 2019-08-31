#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 10:45:29 2019

@author: yanni
"""
import requests
import json
import re
import time
import googlemaps
import StringMatching
from dateutil.parser import parse

from util_weather import *

weekdayDict = {0:'Monday',1:'Tuesday',2:'Wednesday',3:'Thursday',4:'Friday',5:'Saturday',6:'Sunday'}


#get Attraction Operation Time Intent Handler
def getAttrOperTimeIntentHandler(date,attrname,APIKEY):

    operating_hours = getAttrOperTime(date,attrname,APIKEY)
    API_ENDPOINT_id = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={attrname} Singapore&inputtype=textquery&key={APIKEY}"
    data_id = getjson(API_ENDPOINT_id)
    place_id = data_id['candidates'][0]['place_id']

    API_ENDPOINT_time = f"https://maps.googleapis.com/maps/api/place/details/json?placeid={place_id}&fields=name,opening_hours&key={APIKEY}"
    time_info = getjson(API_ENDPOINT_time)
    
    print(time_info)
    #If attaction is outdoor activity, call Weather Check Intent
    API_ENDPOINT = f"http://localhost:8001/attractions?name={attrname}"
    data_attr = getjson(API_ENDPOINT)
    
    category = data_attr[0]['isOutdoor']

    if operating_hours:
        if date and 'close' in json.dumps(time_info):
            timeArray_open = time.strptime(operating_hours[0], "%M%S")
            timeArray_close = time.strptime(operating_hours[1], "%M%S")
            time_open = time.strftime("%M:%S", timeArray_open)
            time_close = time.strftime("%M:%S", timeArray_close)
        
            if category == True:
                if operating_hours[0] == '-' or operating_hours[1] == '-':
                    return "Sorry, we don't have the information for now."
                else:
                    weather_response = getWeatherResponse(date, attrname,APIKEY)
                    return f"The operation time of {attrname} is from {operating_hours[0]} to {operating_hours[1]}.\n{weather_response}"
            else:
                return f"The operation time of {attrname} is from {operating_hours[0]} to {operating_hours[1]}.\nEnjoy your time!"
        elif date:
            return f"The operation time of {attrname} is:\n {operating_hours}."
        else:
            return f"The operation time of {attrname} is:\n {operating_hours[0]} \n {operating_hours[1]} \n {operating_hours[2]} \n {operating_hours[3]} \n {operating_hours[4]} \n {operating_hours[5]} \n {operating_hours[6]} \n "
    else:
        return f'Sorry, we do not have the operation time of it'

#get Attaction Operation Time
def getAttrOperTime(date,attrname,APIKEY):


    API_ENDPOINT_id = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={attrname} Singapore&inputtype=textquery&key={APIKEY}"
    data_id = getjson(API_ENDPOINT_id)
    place_id = data_id['candidates'][0]['place_id']

    API_ENDPOINT_time = f"https://maps.googleapis.com/maps/api/place/details/json?placeid={place_id}&fields=name,opening_hours&key={APIKEY}"
    time_info = getjson(API_ENDPOINT_time)
    print(time_info)
    print(type(time_info))
    opening_hours = ''
    
    if 'opening_hours' in time_info['result']:
        if date and 'close' in json.dumps(time_info):
            timeArray = time.strptime(date, "%Y-%m-%dT%H:%M:%S+08:00")
            otherStyleTime = time.strftime("%Y%m%d", timeArray)
            date_time = parse(otherStyleTime)
            date_week = date_time.weekday()
            print(date_week)
    
            time_result = time_info['result']['opening_hours']['periods'][date_week-1]
            print(time_result)

            opening_time = time_result['open']['time']
            closing_time = time_result['close']['time']
            operating_hours = [opening_time,closing_time]

            return operating_hours
        elif date:
            timeArray = time.strptime(date, "%Y-%m-%dT%H:%M:%S+08:00")
            otherStyleTime = time.strftime("%Y%m%d", timeArray)
            date_time = parse(otherStyleTime)
            date_week = date_time.weekday()
            operating_hours = time_info['result']['opening_hours']['weekday_text']
            for i in operating_hours:
                if weekdayDict[date_week] in i:
                    operationTime = i
            return operationTime
        else:
            operating_hours = time_info['result']['opening_hours']['weekday_text']
            return operating_hours
    else:
        return opening_hours #f'Sorry, we do not have the operation time of {attrname}'
        
#get json
def getjson(url):
    resp =requests.get(url)
    return resp.json()