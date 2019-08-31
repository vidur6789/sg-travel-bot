#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 10:57:21 2019

@author: yanni
"""
import requests
import json


def getAttrAddrIntentHandler(attrname,APIKEY):
    
    address = getAttrAddr(attrname,APIKEY)
    return f"The address of {attrname} is {address}"


def getAttrAddr(attrname,APIKEY):
    
    API_ENDPOINT = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={attrname} Singapore&inputtype=textquery&fields=formatted_address&key={APIKEY}"
    addr_info = getjson(API_ENDPOINT)
    
    if addr_info["status"] == 'OK':
        address = addr_info['candidates'][0]['formatted_address']
        return address
    else:
        return f"Sorry, we cannot find the address of {attrname}"
    
    
def getjson(url):
    resp =requests.get(url)
    return resp.json()
