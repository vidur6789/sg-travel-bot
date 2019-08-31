#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 11:01:12 2019

@author: yanni
"""

import requests
import json
import googlemaps

#google maps client key
gmaps = googlemaps.Client(key='AIzaSyAgU9a5eTrwZP9pIb0eNuNRu3iPE75tR-8')


#get Direction Intent Handler
def getDirecIntentHandler(origin,destination):
    
    direc_url = getDirection(origin,destination)
    
    distance_duration = getDistance(origin,destination)
    
    #Rich Text
    if origin:
        result_obj = {
          "payload": {
            "google": {
              "expectUserResponse":True,
              "richResponse": {
                "items": [
                  {
                    "simpleResponse": {
                      "textToSpeech": " "
                    }
                  },
                   {
                    "basicCard": {
                      "title": "The direction from "+origin+" to "+destination,
                      "subtitle":"",
                      "formattedText":"The direction from"+origin+" to "+destination+"  is about "+distance_duration[0]+", the transit duration is about "+distance_duration[1],
                      "image": {
                        "url": "https://klgadgetguy.com/wp-content/uploads/2018/10/Google-maps-changes.jpg",
                        "accessibilityText": "The distance between" +origin+ " and " +destination+ " is about "+distance_duration[0]+ ", the transit duration is about "+distance_duration[1]
                      },
                      "buttons": [
                        {
                          "title": "Redirect to Google Maps",
                          "openUrlAction": {
                            "url": direc_url
                          }
                        }
                      ],
                      "imageDisplayOptions": "CROPPED"
                    }
                  }
                ]
      }
    }
  }
}
        
        return result_obj
    
    else:
        result_obj = {
          "payload": {
            "google": {
              "expectUserResponse":True,
              "richResponse": {
                "items": [
                  {
                    "simpleResponse": {
                      "textToSpeech": " "
                    }
                  },
                   {
                    "basicCard": {
                      "title": "The direction to "+destination,
                      "subtitle":"",
                      "formattedText":"The direction to "+destination+"  is about "+distance_duration[0]+", the transit duration is about "+distance_duration[1],
                      "image": {
                        "url": "https://klgadgetguy.com/wp-content/uploads/2018/10/Google-maps-changes.jpg",
                        "accessibilityText": "The distance between" +origin+ " and " +destination+ " is about "+distance_duration[0]+ ", the transit duration is about "+distance_duration[1]
                      },
                      "buttons": [
                        {
                          "title": "Redirect to Google Maps",
                          "openUrlAction": {
                            "url": direc_url
                          }
                        }
                      ],
                      "imageDisplayOptions": "CROPPED"
                    }
                  }
                ]
              }
            }
          }
        }
        
        return result_obj

#get Direction
def getDirection(origin,destination):
    #If origin and destination are both assigned
    if origin:
        origin_mod = origin + ' Singapore'
        API_ENDPOINT = f"https://www.google.com/maps/dir/?api=1&origin={origin_mod}&destination={destination} Singapore&travelmode=transit"
        return API_ENDPOINT
    #else only destination is assigned, use geolocation as the origin
    else:
        geolocate_result = gmaps.geolocate()
        geolocate = geolocate_result['location']
        geoloc_lst = [geolocate['lat'],geolocate['lng']]
        geoloc = [str(i) for i in geoloc_lst]
        origin_mod = ','.join(geoloc)
        API_ENDPOINT = f"https://www.google.com/maps/dir/?api=1&origin={origin_mod}&destination={destination} Singapore&travelmode=transit"
        return API_ENDPOINT

#get Distance
def getDistance(origin,destination):
        #If origin and destination are both assigned
    if origin:
        origin_mod = origin + ' Singapore'
        distance_matrix_result = gmaps.distance_matrix(origins={origin_mod},destinations={destination},mode = 'transit', transit_mode='rail')
    #else only destination is assigned, use geolocation as the origin
    else:
        geolocate_result = gmaps.geolocate()
        geolocate = geolocate_result['location']
        geoloc_lst = [geolocate['lat'],geolocate['lng']]
        geoloc = [str(i) for i in geoloc_lst]
        origin_mod = ','.join(geoloc)
        distance_matrix_result = gmaps.distance_matrix(origins={origin_mod},destinations={destination},mode = 'transit', transit_mode='rail')
    
    status_check = distance_matrix_result['rows'][0]['elements'][0]['status']
    
    if status_check =='OK':
        duration_result = distance_matrix_result['rows'][0]['elements'][0]['duration']['text']
        distance_result = distance_matrix_result['rows'][0]['elements'][0]['distance']['text']
        distance_duration = [distance_result,duration_result]
        return distance_duration
    else:
        return f"Sorry, we can not find the distance "
