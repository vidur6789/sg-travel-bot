#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 10:17:28 2019

@author: Jingmeng Li
"""
from flask import Flask, request, make_response, jsonify
import requests
import json
import re
import time
import googlemaps
import StringMatching
from dateutil.parser import parse

#API ENDPOINTS#
current_datetime = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
API_ENDPOINT_CURRENT = f"http://api.openweathermap.org/data/2.5/weather?APPID=43c74b533e77c97f1787245d435698fb&q=Singapore"
API_ENDPOINT_FORECAST = f"https://api.data.gov.sg/v1/environment/4-day-weather-forecast?date_time={current_datetime}"

#get response when raining & outdoor
def getWeatherResponse(date,attrname,APIKEY):
    weatherinfo = getWeatherInfo(date)
    alternatives_list = getAlternatives(attrname,APIKEY)    #get alternative list
    if date.split('T')[0] == current_datetime.split('T')[0]:
        if 'rain' in weatherinfo or 'shower' in weatherinfo:    #check if raining
            if alternatives_list != []:
                alternatives = ', '.join(alternatives_list)
                return f"Gentle reminder: it is raining currently. Here are some alternatives for you: {alternatives}."
            else:
                return "Gentle reminder: it is raining currently, please take an umbrella or reschedule."
    else:
        if 'rain' in weatherinfo or 'shower' in weatherinfo:
            if len(weatherinfo.split('. ')) > 1:
                rainy_time = weatherinfo.split('. ')[1].lower()
            else:
                rainy_time = weatherinfo.split('. ')[0].lower()     #get rainy time
            if alternatives_list != []:
                alternatives = ', '.join(alternatives_list)
                return f"Gentle reminder: there will be {rainy_time} \nHere are some alternatives for you: {alternatives}."
            else:
                return f"Gentle reminder: there will be {rainy_time} please take an umbrella or reschedule."
    return "Enjoy your time!"

#get response when only asked for weather
def getWeather(date):
    weatherinfo = getWeatherInfo(date)
    if weatherinfo != "":
        weatherinfo = weatherinfo.lower()
        if date.split('T')[0] == current_datetime.split('T')[0]:
            return f"The weather is {weatherinfo}."
        else:
            return f"The weather will be {weatherinfo[:-2]}."
    else:
        return "I can only forecast weather in four days. Sorry!"
    

#get weather info from weather API
def getWeatherInfo(datetime):
    date = datetime.split('T')[0] #get the date part from datetime
    weatherinfo = ""

    #if user doesn't specify date, assume current date
    if date == current_datetime.split('T')[0]:
        data = getjson(API_ENDPOINT_CURRENT)
        weatherinfo = data["weather"][0]["description"]
    else:
        data = getjson(API_ENDPOINT_FORECAST)
        for i in data['items'][0]['forecasts']:
            if i['date'] == date:
                weatherinfo = i['forecast']
    return weatherinfo


#generate alternatives if raining
def getAlternatives(attrname,APIKEY):
    #load association rules
    with open("alternatives.json", 'r') as load_f:
        rules_list = json.load(load_f)

    API_ENDPOINT = f"http://localhost:8001/attractions?name={attrname}"
    data_attr = getjson(API_ENDPOINT)
    
    overall_list = []
    alternative_score_dict = {}     #final score dictionary
    alternatives = []               #
    location = data_attr[0]['name']     #get name of asked attraction
    categories = data_attr[0]['categories']    #category list of asked attraction

    googleapi_types = ['amusement_park','aquarium','art_gallery','museum','park','rv_park','zoo']   #list of types to search in google API

    # API_ENDPOINT = f"http://localhost:8001/attractions"
    data = getjson("http://localhost:8001/attractions")
    
    #construct score dictionary for every attraction
    for i in data:
        if i['name'] != location:
            overall_list.append({'attraction': i['name'],'association': 0,'category':0,'near':0})

    #detect association
    for i in rules_list:
        if location.lower() == i['lhs'].lower():
            for j in overall_list:
                if j['attraction'].lower() == i['rhs'].lower():
                    j['association'] = 1

    #calculate number of overlaping categories
    for i in data:
        count = 0
        for j in categories:
            for k in range(len(i['categories'])):
                lowcase = i['categories'][k].lower()
                i['categories'][k] = lowcase
            if j.lower() in i['categories'] and 'outdoor' not in i['categories']:
                count = count + 1
        for k in overall_list:
            if k['attraction'].lower() == i['name'].lower():
                k['category'] = count

    #find nearby attractions
    # attraction = data_attr['name']
    #get coordinate of attraction using attraction name
    geometry_url = f'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={location}&inputtype=textquery&fields=name,geometry&key={APIKEY}'
    geometry_data = getjson(geometry_url)
    geometry = str(geometry_data['candidates'][0]['geometry']['location']['lat'])+","+str(geometry_data['candidates'][0]['geometry']['location']['lng'])
    #search for nearby attraction in radius of 3km
    for i in googleapi_types:
        places_url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?language=en&location={geometry}&radius=3000&type={i}&key={APIKEY}'
        places_data = getjson(places_url)
        for j in places_data['results']:
            for k in overall_list:
                if j['name'] == k['attraction']:
                    k['near'] = 1
        while 'next_page_token' in places_data:
            next_page_token = places_data['next_page_token']
            next_page_url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?language=en&pagetoken={next_page_token}&key={APIKEY}'
            places_data = getjson(next_page_url)
            #compare search result with data to check if attractions are nearby
            for k in places_data['results']:
                for l in overall_list:
                    if k['name'] == l['attraction']:
                        l['near'] = 1

    #calculate overall score for every attraction
    for i in overall_list:
        alternative_score_dict[i['attraction']] = i['association']*0.2 + i['category']*0.3 + i['near']*0.5
    for i in range(3):      #generate 3 alternatives
        max_score = max(alternative_score_dict, key=alternative_score_dict.get)
        alternatives.append(max_score)
        del alternative_score_dict[max_score]
    return alternatives

def getjson(url):
    resp =requests.get(url)
    return resp.json()