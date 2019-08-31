# SG Travel Bot

The SG Travel Bot assimilates data from travel websites to provide services that can simplify the travel planning process and serve as the perfect travel companion for tourists in Singapore.


This chat bot has the following capabilities:
- Location based and personalised attraction recommendations.
- Retrieving information about attractions, promotions, events and weather advisory.
- Generating intelligent alternative attractions to visit using association mining in case of bad weather forecast
- Handle incorrect and incomplete attraction names or keywords to detect user’s true intent 


## Setup
#### Python Fulfillment Server
1. Setup a virtual environment with pip using requirements.txt

```bash
pip install -r requirements.txt
```

2. Execute app_main.py to start the Python Flask fulfillment server
3. The webhook will start on the port 5000
4. Use [ngrok](https://ngrok.com/download) to create a secure tunnel to localhost

```bash
ngrok http 5000
```

#### TripAdvisor Knowledge Base APIs

1. Download trippingo.jar into a new project directory from this GitHub [repository releases](https://pip.pypa.io/en/stable/)
2. Download datastore.mv.db from the same into a new sub-directory 'data'
3. Navigate to project directory and execute the archive file as java application.
```bash
java -jar trippingo.jar
```

4. API will be available on 8001 port of the localhost to be internally used by Python Flask fulfillment server

#### Dialog Flow Chatbot
1. Download the SGTravelBot.zip file from this GitHub repository
2. Import the chatbot into DialogFlow using this zip file
3. Update Fulfillment tab to use the secure https ngrok tunnel created in the earlier step

## Example Use Cases

#### Personalised  Attraction Recommendations
 - Things to do in Singapore
 - Places to visit in Singapore
 - Things to do for families(|friends|couples|solo traveller)
 - Recommend me nature parks in Singapore
 - Recommend me parks near me
 - Suggest a church near City Hall

#### Attraction Information
 - Tell me something about Gardens by the Bay
 - What is the opening time of Gardens by the Bay tomorrow
 - What is the address of Gardens by the Bay
 - Directions to Gardens by the Bay
 - Suggested duration for Cloud forest


#### Promotions
 - Promotions for Gardens by the Bay

#### Events
 - Events in February
 - What is Singapore Biennale
 - When is Singapore Biennale

#### Weather and Intelligent alternatives
 - What is the weather tomorrow

In cases when the user indicates an interest in travelling to an outdoor attraction(by asking for operating hours or directions) when the weather is expected to be unsuitable for outdoor activities, a cautionary message is shown with the weather update and some intelligent alternative recommendations based on previously captured user preferences and location data

#### Searching attractions by keywords, approximate spellings
 - search gardens bay -> responds with Gardens by the Bay
 - dinosaur ->returns Lee Kong Chian Natural History Museum

This functionality can be used as a standalone feature to search with keywords or imperfect spellings, Additionally, it serves as the default fallback intent when the user's query is unable to match any other intent of the chatbot. This will guide the user's conversation back to the one of the common chat bot functionalities by providing appropriate suggestion chips along with the matched attraction. 
