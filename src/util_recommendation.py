from flask import Flask, request, make_response, jsonify
import requests
from StringMatching import stringmatching
import googlemaps
import util_events

TRIPPINGO_URL="http://localhost:8001"
APIKEY = {APIKEY}
gmaps = googlemaps.Client(key='AIzaSyAuoXXfgfRxQCrBlRFeDsEbTtwbDil-g3k')

app = Flask(__name__)
currentLocationPhrasings = ['near me', 'around me', 'nearby']
REC_INTENTS = ['RecommendationIntent','TravellerTypeIntent', 'CategoryIntent', 'UserInfo','RecomTypeIntent','EventDurationIntent']

userInfo = {"travellerType": None,
            "currentLocation": ""}

slots = {"travellerType": None,
         "category": None,
         "location": None,
         "keywords":None,
         "TypeThings":None,
         "date-period":None}

current_session=""

from util_events import *


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
    slots["TypeThings"] = None
    slots["date-period"] = None


def getDeviceLocation(req):
    payload = req['originalDetectIntentRequest']['payload']
    if 'device' in payload and 'location' in payload['device']:
        return payload['device']['location']
    else:
        return None

def log_session(req):
    global current_session
    global userInfo
    if current_session != req['session']:
        current_session = req['session']
        # reset user_info
        userInfo = {"travellerType": None, "currentLocation": ""}


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
        if parameters['location'] in currentLocationPhrasings and userInfo['currentLocation']:
            slots['location'] = userInfo['currentLocation']
        else:
            slots['location'] = parameters['location']
    elif getDeviceLocation(req):
        slots['location'] = req['originalDetectIntentRequest']['payload']['device']['location']
        userInfo['currentLocation'] = slots['location']
    elif userInfo['currentLocation']:
        slots['location'] = userInfo['currentLocation'] 
    #THINGSTYPE
    if 'TypeThings' in parameters and parameters['TypeThings']:
        slots['TypeThings'] = parameters['TypeThings']

    #EVENT DURATION
    if 'date-period' in parameters and parameters['date-period']:
        slots['date-period'] = parameters['date-period']
 

def isEventsPossible(req):
    return slots['TypeThings'] and slots['date-period']


def isRecommendationPossible(req):
    return (slots['category'] or slots['keywords']) \
           and slots['travellerType'] \
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



def getZipCode():
    if slots['location'] and type(slots['location']) == dict:
        location = slots['location']
        if 'zip-code' in location and location['zip-code']:
            location['zip-code']
        elif 'zipCode' in location and location['zipCode']:
            return location['zipCode']
    return ""


def getCombinedKeywords():
    keywordsList = []
    if slots['keywords']:
        keywordsList.append(slots['keywords'])
    if slots['category']:
        keywordsList.extend(slots['category'])
    return ",".join(keywordsList)




def trippingoCarouselItem(item):    ####### number of items
    name = item['name']
    return carouselItem(name, getDirectionsLink("", name), "", "", getPhoto(name), "")


def getDirectionsLink(fromPostal, toPostal):
    fromLoc = "Singapore+"+fromPostal if fromPostal else ""
    toLoc = "Singapore+"+toPostal
    return "https://www.google.com/maps/dir/{fromLoc}/{toLoc}/".format(fromLoc=fromLoc, toLoc=toLoc)


def getPhoto(attrname):
    API_ENDPOINT = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={attrname}&inputtype=textquery&fields=photos&key={APIKEY}".format(attrname=attrname,APIKEY=APIKEY)
    try:
        info = getjson(API_ENDPOINT)
        photo_ref = info['candidates'][0]['photos'][0]['photo_reference']
        photo_url = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={APIKEY}".format(photo_ref=photo_ref, APIKEY=APIKEY)
    except:
        photo_url=''
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

def recommendationIntentHandler(req):
    if isRecommendationPossible(req):
        recItems = getRecommendations(req)
        resetRecommendationSlots()
        if len(recItems)==1:  # need to use basic card
            return basicCardResponse(recItems)
        else:
            return carouselResponse(recItems, "Here are some recommendations for you") #@@
    elif isEventsPossible(req):
        res = events(req)
        resetRecommendationSlots()
        return res  # #######
    else:
        return requestRemainingSlots(req)


# returns list of DialogFlow carousel items as recommendations
def getRecommendations(req):
    # 
    carouselItems = trippingoRecommendations(req)
    if not carouselItems:
        carouselItems  = googleRecommendations(req)
    return carouselItems



# returns list of DialogFlow carousel items as recommendations
def trippingoRecommendations(req):
    keywords = getCombinedKeywords()
    travellerType = slots['travellerType'].title()
    url = TRIPPINGO_URL+"/recommendations?keywords={keywords}&travellerType={travellerType}&count=3".format(keywords=keywords,travellerType=travellerType);
    zipcode = getZipCode()
    url = TRIPPINGO_URL+"/recommendations?keywords={keywords}&travellerType={travellerType}&count=3".format(keywords=keywords,travellerType=travellerType);
    if zipcode:
        url = url + "&location=" + zipcode
    api_response = getjson(url)
    carouselItems = [trippingoCarouselItem(item) for item in api_response]
    return carouselItems

def getNearbyRecom(category):

    geolocate_result = gmaps.geolocate()
    geolocate = geolocate_result['location']
    
    typename = ''
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

    places_nearby_result = gmaps.places_nearby(location=geolocate,rank_by='distance',type=typename)

    
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
def googleRecommendations(req):
    category = getCombinedKeywords()
    names = getNearbyRecom(category)
    return [carouselItem(name, getDirectionsLink("", name), "", "", getPhoto(name), "") for name in names]


def requestRemainingSlots(req):
    if slots['TypeThings']=='attractions' or not slots['TypeThings']:  # recommend attractions
        if not slots['travellerType']:
            return suggestionChipsResponse("Who are you travelling with?", "Family", "Couple", "Friends", "Solo", "Office colleagues")
        if not slots['category'] and not slots['keywords']:
            return suggestionChipsResponse("What kind of places do you like to visit?", "Nature & Parks", "Shopping Streets", "City Landmarks", "Museums")
        if slots['location'] in currentLocationPhrasings:
            return locationPermissionResponse(req)
    if slots['TypeThings']=='events' and not slots['date-period']:
        return suggestionChipsResponse("What time preiod do you want to search? (Please answer like chips below)", "January", "February")

def events(req):
    date_period = slots["date-period"]
    respose = getEventIntentHandler(date_period)

    return respose


# ***************************
# Intent Handlers funcs : END
# ***************************

