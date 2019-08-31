from flask import Flask, request, make_response, jsonify
import requests
import pandas as pd
import datetime
import re
from util_promotion import *

def getEventsInfoByKeyWords(events_keyword):  # get events' data from tih website
    API_ENDPOINT = f"https://tih-api.stb.gov.sg/content/v1/event/search?keyword={events_keyword}&apikey=5PwGJuXPjJatTeJMrXhyIxksG4JdpzoB"  #url
    resp = requests.get(API_ENDPOINT)
    data = resp.json()
    return data

def getAllEventInfo():
    events_type = ["Arts","Attractions","Entertainment","Food & Beverages","History & Culture","Shopping","Sports","Others"] #
    events_name = []
    for e_type in events_type: # store all the events
        API_EVENT = f"https://tih-api.stb.gov.sg/content/v1/event/search?keyword={e_type}&sortBy=type&apikey=5PwGJuXPjJatTeJMrXhyIxksG4JdpzoB"  #url
        resp = requests.get(API_EVENT)
        events = resp.json()

        for i in range(len(events["data"])):
            if "#" in events["data"][i]["name"]:
                events["data"][i]["name"] = re.sub('#','',events["data"][i]["name"])
            events_name.append(events["data"][i]["name"])

    events_name = list(set(events_name))

    events_num = len(events_name)
    events_startdate=[]
    events_enddate=[]
    for i in range(events_num): 
        events = getEventsInfoByKeyWords(events_name[i])
        date_start = events["data"][0]["startDate"]
        date_end = events["data"][0]["endDate"]
        startdate = datetime.datetime.strptime(date_start, '%Y-%m-%dT%H:%M:%SZ')
        events_startdate.append(startdate.date())
        enddate = datetime.datetime.strptime(date_end, '%Y-%m-%dT%H:%M:%SZ')
        events_enddate.append(enddate.date())
        data = {'name':events_name,'startdate':events_startdate,'enddate':events_enddate}
    df = pd.DataFrame(data)
    return df # events.json #actually not useful, but leave it here as if our events' data is real-time


def getEventNameInfo(date_start,date_end):   #use start and end time to search events' name
    df = pd.read_json (r'events.json')
    df = df[['name', 'startdate', 'enddate']]
    # df = df[0:7]
    # transfer two parameters into date type
    startdate = datetime.datetime.strptime(date_start, '%Y-%m-%dT%H:%M:%S+08:00')
    startdate = startdate.date()
    enddate = datetime.datetime.strptime(date_end, '%Y-%m-%dT%H:%M:%S+08:00')
    enddate = enddate.date()   


    for i in range(len(df)):  #change the type of date data
        event_start = datetime.datetime.strptime(df.iat[i,1], '%Y-%m-%dT%H:%M:%SZ')
        df.iat[i,1] = event_start.date()
        event_end = datetime.datetime.strptime(df.iat[i,2], '%Y-%m-%dT%H:%M:%SZ')
        df.iat[i,2] = event_end.date()

    startdf = df[df['startdate']<=startdate] #datetime
    events = startdf[startdf['enddate']>=startdate]

    enddf = df[df['enddate']>=enddate] #datetime
    eventss = enddf[enddf['startdate']<=enddate]
    events = events.append(eventss)
    events = events.drop_duplicates()
    events_series = events["name"]
    events_list = events_series.tolist()
    if len(events_list) > 5:
        return events_list[:5]
    else:
        return events_list


def getEventDesriptionInfo(events_keyword):  #use event's name to search its description
    events = getEventsInfoByKeyWords(events_keyword)
    events_description = events["data"][0]["description"] 
    return events_description


def getEventDurationInfo(events_keyword,i):  #use event's name to search its start and end date
    events = getEventsInfoByKeyWords(events_keyword)
    if i==1:
        events_duration = events["data"][0]["startDate"]  #str
        date_time_obj = datetime.datetime.strptime(events_duration, '%Y-%m-%dT%H:%M:%SZ')
        events_duration = date_time_obj.date()
    if i==2:
        events_duration = events["data"][0]["endDate"] 
        date_time_obj = datetime.datetime.strptime(events_duration, '%Y-%m-%dT%H:%M:%SZ')
        events_duration = date_time_obj.date()
    return events_duration


def getEventName(events_keyword):  #use key words to find event's whole name
    events = getEventsInfoByKeyWords(events_keyword)
    if events:
        if events['status']['errorDetail'] == 'record not found':
            return None
        else:
            events_name = events["data"][0]["name"]
            return events_name
    else:
        return None


def getEventImageUrl(events_keyword):  #use key words to find event's image uuid
    events = getEventsInfoByKeyWords(events_keyword)
    events_imageuuid = events["data"][0]["thumbnails"][0]["uuid"]
    events_imageUrl = "https://tih.stb.gov.sg/bin/GetMediaByUuid?uuid="+events_imageuuid+"&fileType=Medium%2520Thumbnail&mediaType=image"
    return events_imageUrl

def getEventWeb(events_keyword): # use key words to find event's website
    events = getEventsInfoByKeyWords(events_keyword)
    events_web = events["data"][0]["officialWebsite"]
    if not events_web:
        events_web = 'http://www.google.com'
    else:
        events_web = "https://"+events_web
    return events_web


def carouselItem(title, url, description, footer, image_url, img_txt):
    item = {"title": title, "openUrlAction": {"url": url}}
    #print('into carouselItem',item)
    if description:
        item["description"] = description
    if footer:
        item["footer"] = footer
    if image_url:
        item["image"] = {"url": image_url, "accessibilityText": img_txt}
    return item

def carouselResponse(items, title):
    print('carouselResponse',items)
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

def parseResponse(events_list):
    recs = [recResponseItem(events_keyword) for events_keyword in events_list]
    #print('parseResponse',recs)
    return recs

def recResponseItem(events_keyword):
    print('recResponseItem',events_keyword)
    print(events_keyword)
    print(getEventWeb(events_keyword))
    print(getEventImageUrl(events_keyword))
    return carouselItem(getEventName(events_keyword), getEventWeb(events_keyword), getEventDesriptionInfo(events_keyword), "", getEventImageUrl(events_keyword), "image")

def getEventIntentHandler(date_period):  # search a typical period includes what events
    print(date_period)
    req_start = date_period["startDate"]
    req_end = date_period["endDate"]
    date_start = "".join( req_start.split() )
    date_end = "".join( req_end.split() )
    events_name = getEventNameInfo(date_start,date_end)

    recs = parseResponse(events_name)   #######
    print('getEventIntentHandler',len(recs))
    if len(recs)==1:
        #print(recs)
        return basicCardResponse(recs)
    else:
        print('getEventIntentHandler - else')
        return carouselResponse(recs, "During that period, there are:")

def basicCardResponse(item):
    #item = {"title": title, "openUrlAction": {"url": url}}
    print('basicCardResponse:    ',item[0])
    result_obj = {
      "payload": {
    "google": {
      "expectUserResponse": True ,
      "richResponse": {
        "items": [
          {
            "simpleResponse": {
              "textToSpeech": " "
            }
          },
          {
            "basicCard": {
              "title": item[0]['title'],
              "subtitle": "",
              "formattedText":item[0]['description'],
              "image": item[0]['image'],
              "buttons": [
                {
                  "title": "View More",
                  "openUrlAction": item[0]['openUrlAction']
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


def getEventDurationIntentHandler(req):
    events_keyword = " ".join( req.split() )
    events_starttime = getEventDurationInfo(events_keyword,1)
    events_endtime = getEventDurationInfo(events_keyword,2)
    events_name    = getEventName(events_keyword)

    return f"Event '{events_name}' is from {events_starttime} to {events_endtime}"


def getEventDescriptionIntentHandler(req):
    events_keyword = " ".join( req.split() )
    events_name = getEventName(events_keyword)
    if events_name:
        events_description = getEventDesriptionInfo(events_keyword)
        events_imageUrl = getEventImageUrl(events_keyword)
        events_web = getEventWeb(events_keyword)

        result_obj = {
          "payload": {
        "google": {



          "expectUserResponse": True ,
          "richResponse": {
            "items": [
              {
                "simpleResponse": {
                  "textToSpeech": " "
                }
              },
              {
                "basicCard": {
                  "title": events_name,
                  "subtitle": "",
                  "formattedText":events_description,
                  "image": {
                    "url": events_imageUrl,
                    "accessibilityText": "Image alternate text"
                  },
                  "buttons": [
                    {
                      "title": "View More",
                      "openUrlAction": {
                        "url": events_web
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
        return jsonify(result_obj)

    else:
        Response = FallbackIntentHandler(events_keyword)
        return jsonify(Response)
        