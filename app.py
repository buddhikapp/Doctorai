import os
import sys
import json

import requests
import apiai
import sqlite3
import string
import diagnose
import search
import user
import psql
import urllib, json
from flask import Flask, request

import infermedica_api

googleApiKey = 'AIzaSyDajx797IQYukLSGkT3VwP02Qa2pyWQlEw'
api = infermedica_api.API(app_id='aaccd529', app_key='2507fff3b3104d61bca7f4eb7511dc7b')
#print(api.info())

app = Flask(__name__)

symptom_mode = False
#symptom = None
#gender = None
#age = None
#diagnosis = None
myUsers = []
myUser = user.MyUser()

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello World!", 200


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events
    data = request.get_json()
    log("%%%% New Message %%%% " + str(data))  # you may not want to log every incoming message in production, but it's good for testing
    
    global myUsers, myUser
    
    if "object" in data:
        if data["object"] == "page":
            for entry in data["entry"]:
                for messaging_event in entry["messaging"]:
                    log("myUsers Lenght : " + str(len(myUsers)))
                    if messaging_event.get("postback") or messaging_event.get("message"):
                        if user.CheckUser(messaging_event["sender"]["id"]):
                            myUser = user.GetUser(messaging_event["sender"]["id"])
                            log("User Found : " + str(myUser.id))
                        else:
                            myUser = user.CreateUser(messaging_event["sender"]["id"])
                            myUsers.append(myUser)
                            log("User Created : " + str(myUser.id))

                    if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message

                        recipient_id = messaging_event["recipient"]["id"]
                        log("recipient_id : " + recipient_id)
                        
                        title = messaging_event["postback"]["payload"].split(":")[0]
                        payload = messaging_event["postback"]["payload"].split(":")[1]
                        
                        if title == 'SymptomChecker' or title == 'HealthAlerts':
                            message = payload
                            log("message : " + message)
                            send_message(myUser.id, message)
                        elif title == 'TonicDiscountsMain':
                            message = payload
                            log("message : " + message)
                            send_message(myUser.id, message)
                            send_message_quick_location(myUser.id)
                        elif title == 'TonicDiscounts':
                            message = payload
                            log("message : " + message)
                            send_message(myUser.id, message)
                        

                    elif messaging_event.get("message"):  # someone sent us a message

                        recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                        # sort different types of messages
                        message = messaging_event["message"]

                        sid = None
                        if message.get("text"): # get message
                            message = message["text"]
                            if message.upper() == "DOCTORBOT" or message.upper() == "HI" or message.upper() == "HELLO":
                                myUser.symptom = 'empty'
                                myUser.diagnosis = 'empty'
                                myUser.question_count = 0
                                if psql.update_user(messaging_event["sender"]["id"],myUser) == 0:
                                    log("Error : User not found for update id. : " + str(messaging_event["sender"]["id"]))
                                else:
                                    log("Success : User updated. id : " + str(messaging_event["sender"]["id"]))
                                init_buttom_template(myUser)
                            elif message.upper() == "DEV MYUSER":
                                log("Dev Test myUsers Lenght : " + str(len(myUsers)))
                                for i in range(len(myUsers)):
                                    log(str(i) + " - " + str(myUsers[i].first_name))
                                if user.CheckUser(messaging_event["sender"]["id"]):
                                    devTestUser = user.GetUser(messaging_event["sender"]["id"])
                                    log("Dev Test User Found id : " + str(devTestUser.id))
                                    log("Dev Test User Found symptom : " + str(devTestUser.symptom))
                                    log("Dev Test User Found gender : " + str(devTestUser.gender))
                                    log("Dev Test User Found diagnosis : " + str(devTestUser.diagnosis))
                                    log("Dev Test User Found first_name : " + str(devTestUser.first_name))
                                    log("Dev Test User Found last_name : " + str(devTestUser.last_name))
                                    log("Dev Test User Found profile_pic : " + str(devTestUser.profile_pic))
                                else:
                                    log("Dev Test User Not Found id : " + str(messaging_event["sender"]["id"]))
                            elif message.upper() == "DEV CREATE TABLE MLK":
                                psql.create_tables()
                            elif message.upper() == "DEV DROP TABLE MLK":
                                psql.drop_tables()
                            elif message.upper() == "DEV TEST SQLCONNECT MLK":
                                psql.connect()
                            

                            elif myUser.symptom != 'empty' and myUser.diagnosis != 'empty':
                                try:
                                    if string.find(message.upper(),str(myUser.diagnosis.question.items[0]["choices"][0]["label"]).upper()) is not -1:
                                        myUser.diagnosis = diagnose.improve_diagnosis(myUser.diagnosis,myUser.id,myUser.symptom,str(myUser.diagnosis.question.items[0]["choices"][0]["id"]))
                                    elif string.find(message.upper(),str(myUser.diagnosis.question.items[0]["choices"][1]["label"]).upper()) is not -1:
                                        myUser.diagnosis = diagnose.improve_diagnosis(myUser.diagnosis,myUser.id,myUser.symptom,str(myUser.diagnosis.question.items[0]["choices"][1]["id"]))
                                    elif string.find(message.upper(),str(myUser.diagnosis.question.items[0]["choices"][2]["label"]).upper()) is not -1:
                                        myUser.diagnosis = diagnose.improve_diagnosis(myUser.diagnosis,myUser.id,myUser.symptom,str(myUser.diagnosis.question.items[0]["choices"][2]["id"]))
                                    else:
                                        send_message(myUser.id, "Sorry, I didn't get that. Please enter your answer again.")
                                    
                                    if psql.update_user(messaging_event["sender"]["id"],myUser) == 0:
                                        log("Error : User not found for update. id : " + str(messaging_event["sender"]["id"]))
                                    else:
                                        log("Success : User updated. id : " + str(messaging_event["sender"]["id"]))
                                    
                                    if myUser.diagnosis.conditions[0]["probability"] > 0.25 and myUser.question_count > 3:
                                        send_message(myUser.id, "I suspect "+str(myUser.diagnosis.conditions[0]["name"])+" with a probability of "+str(myUser.diagnosis.conditions[0]["probability"]))
                                        send_message(myUser.id, "Please send me your location so I can find a doctor near you")
                                        send_message_quick_location(myUser.id)
                                        
                                        myUser.symptom = 'empty'
                                        myUser.diagnosis = 'empty'
                                        myUser.question_count = 0
                                        if psql.update_user(messaging_event["sender"]["id"],myUser) == 0:
                                            log("Error : User not found for update. id : " + str(messaging_event["sender"]["id"]))
                                        else:
                                            log("Success : User updated. id : " + str(messaging_event["sender"]["id"]))
    #                                    log("myUsers Lenght : " + str(len(myUsers)))
    #                                    log("Removing user : " + str(myUser.id))
    #                                    user.RemoveUser(myUser,myUsers)
    #                                    log("myUsers Lenght : " + str(len(myUsers)))
                                        myUser = user.MyUser()

                                    else:
                                        myUser.symptom = str(myUser.diagnosis.question.items[0]["id"])
                                        response = str(myUser.diagnosis.question.text.encode('utf8'))
                                        if "image_url" in myUser.diagnosis.question.extras:
                                            send_message_image(myUser.id, myUser.diagnosis.question.extras["image_url"])
                                        if str(myUser.diagnosis.question.type) == "group_single" or str(myUser.diagnosis.question.type) == "group_multiple":
                                            response = response + "\n " + str(myUser.diagnosis.question.items[0]["name"].encode('utf8')) + "? "
                                        for x in myUser.diagnosis.question.items[0]["choices"]:
                                            response = response + "\n - " + str(x["label"])
                                        myUser.question_count = myUser.question_count + 1
                                        send_message(myUser.id, response)
                                        if psql.update_user(messaging_event["sender"]["id"],myUser) == 0:
                                            log("Error : User not found for update. id : " + str(messaging_event["sender"]["id"]))
                                        else:
                                            log("Success : User updated. id : " + str(messaging_event["sender"]["id"]))
                                except (RuntimeError, TypeError, NameError, IndexError):
                                    print "Unexpected error:", sys.exc_info()[0]
#                                log("-----myUser.diagnosis------ " + str(myUser.diagnosis))

                            elif myUser.diagnosis == 'empty':
                                search_result = search.search_symtom_limit(message, 5)
                                log("----------- " + str(search_result))
                                if len(search_result) > 0:
                                    send_message(myUser.id, "Give me a sec!")
                                    sid = str(search_result[0]["id"])
                                    log("************ " + sid)
                                
                                    myUser.diagnosis = diagnose.init_diagnose(sid,myUser.age,myUser.gender,myUser.id)
                                    log("-----myUser.diagnosis First Time------ " + str(myUser.diagnosis))
                                    myUser.symptom = str(myUser.diagnosis.question.items[0]["id"])
                                    response = str(myUser.diagnosis.question.text.encode('utf8'))
                                    if "image_url" in myUser.diagnosis.question.extras:
                                        send_message_image(myUser.id, myUser.diagnosis.question.extras["image_url"])
                                    if str(myUser.diagnosis.question.type) == "group_single" or str(myUser.diagnosis.question.type) == "group_multiple":
                                        response = response + "\n " + str(myUser.diagnosis.question.items[0]["name"].encode('utf8')) + "? "
                                    for x in myUser.diagnosis.question.items[0]["choices"]:
                                        response = response + "\n - " + str(x["label"])
                                    myUser.question_count = myUser.question_count + 1
                                    send_message(myUser.id, response)
                                    if psql.update_user(messaging_event["sender"]["id"],myUser) == 0:
                                        log("Error : User not found for update. id : " + str(messaging_event["sender"]["id"]))
                                    else:
                                        log("Success : User updated. id : " + str(messaging_event["sender"]["id"]))
                                else:
                                    send_message(myUser.id, "Sorry, Server appears to be busy at the moment. Please try again later.")


                        # if message.get("text"): # get message
                        #     message = message["text"]
                        #     if symptom_mode:
                        #         symptoms = 3
                        #         print symptoms
                        #         # if myUser.symptom == None
                        #         #     myUser.symptom = apiai_symptom(message) # assuming user put symptom
                        #         # elif 


                        #     elif alert_mode:
                        #         pass
                        #     else:
                        #         if message == "Hi":
                        #             init_buttom_template(myUser.id)
                        #         else:
                        #             send_message(myUser.id, "Say 'Hi' to the DoctorBot to get started!")

                        elif message.get("attachments"):    # get attachment
                            attach = message["attachments"][0]  # loop over attachments?
                            if attach["type"] == "location":
                                latitude = attach["payload"]["coordinates"]["lat"]
                                longitude = attach["payload"]["coordinates"]["long"]
                                revers_geo_code_url = "https://maps.googleapis.com/maps/api/geocode/json?latlng="+str(latitude)+","+str(longitude)+"&key="+googleApiKey+""
                                r = urllib.urlopen(revers_geo_code_url)
                                rdata = r.read()
#                                log("revers_geo_code_url data : ")
#                                log(rdata)
                                ddata = json.loads(rdata)
                                hospitals = []
                                for addrs_com in ddata["results"][0]["address_components"]:
                                    hospitals.extend(psql.get_hospitals(addrs_com["long_name"]))
                                log(len(hospitals))
                                maxi = 0
                                if len(hospitals) > 10:
                                    maxi = 10
                                else:
                                    maxi = len(hospitals)
                                hospitals_distance_duration_latitude_longitude = []
                                for x in range(0, maxi):
                                    log("hospitals raw data : " + str(x) + " : " + str(hospitals[x]))
                                    distance_matrix_url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins="+str(latitude)+","+str(longitude)+"&destinations="+str(hospitals[x][4])+","+str(hospitals[x][5])+"&key="+googleApiKey+""
                                    log(distance_matrix_url)
                                    r = urllib.urlopen(distance_matrix_url)
                                    rdata = r.read()
                                    log("distance_matrix_url data : ")
                                    log(rdata)
                                    ddata = json.loads(rdata)
                                    if ddata["rows"][0]["elements"][0]["status"] == 'OK':
                                        if ddata["rows"][0]["elements"][0]["distance"]["value"] < 10000:
                                            hospitals_distance_duration_latitude_longitude.append([hospitals[x],ddata["rows"][0]["elements"][0]["distance"]["text"],ddata["rows"][0]["elements"][0]["duration"]["text"],hospitals[x][4],hospitals[x][5], ddata["destination_addresses"]])
                                                                                                   
#                                hospitals_distance_duration_latitude_longitude = sorted(hospitals_distance_duration_latitude_longitude, key=lambda hospital: hospitals_distance_duration_latitude_longitude[2])
                                maxi = 0
                                if len(hospitals_distance_duration_latitude_longitude) > 3:
                                    maxi = 3
                                else:
                                    maxi = len(hospitals_distance_duration_latitude_longitude)
                                
                                for x in range(0, maxi):
                                    hospital_buttom_template(messaging_event["sender"]["id"],hospitals_distance_duration_latitude_longitude[x])
                                    map_template(messaging_event["sender"]["id"],hospitals_distance_duration_latitude_longitude[x][0][0],hospitals_distance_duration_latitude_longitude[x][3],hospitals_distance_duration_latitude_longitude[x][4],hospitals_distance_duration_latitude_longitude[x][5])
                                
                                if len(hospitals_distance_duration_latitude_longitude) > 0:
                                    log("Telenor hospitals not found")
                                else:
                                    clinic_type = "hospital"
                                    clinicsURL = "https://api.foursquare.com/v2/venues/search?ll="+str(latitude)+","+str(longitude)+"&radius=15000&query="+clinic_type+"&client_id=1TCDH3ZYXC3NYNCRVL1RL4WEGDP4CHZSLPMKGCBIHAYYVJWA&client_secret=VASKTPATQLSPXIFJZQ0EZ4GDH2QAZU1QGEEZ4YDCKYA11V2J&v=20160917"
                                    r = urllib.urlopen(clinicsURL)
                                    hospitals = []
                                    latitudes = []
                                    longitudes = []
                                    data = json.loads(r.read())
                                    venues = data["response"]["venues"]
                                    maxi = 0
                                    if len(venues) > 4:
                                        maxi = 4
                                    else:
                                        maxi = len(venues)
                                    for x in range(0, maxi):
                                        hospitals.append(venues[x]["name"])
                                        send_message(myUser.id, "Option #"+str(x+1)+": "+venues[x]["name"].encode('utf8'))
                                        latitudes.append(venues[x]["location"]["lat"])
                                        longitudes.append(venues[x]["location"]["lng"])
                                    message = "Location: " + str(latitude) + ", " + str(longitude)

                                    mapurl = "https://maps.googleapis.com/maps/api/staticmap?center="+str(latitude)+","+str(longitude)+"&markers=color:green%7C"+str(latitude)+","+str(longitude)+"&key="+googleApiKey+"&size=800x800"
                                    for y in range(0,maxi):
                                        mapurl = mapurl +"&markers=color:red%7Clabel:H%7C"+str(latitudes[y])+","+str(longitudes[y])
                                    send_message(myUser.id, "And here they are on a map :)")
                                    #sendImage
                                    send_message_image(myUser.id, mapurl)
                            elif attach["type"] == "image":
                                image_url = attach["payload"]["url"]
                                message = image_url#.replace("/p100x100/","/p200x200/")
                                send_message_image(myUser.id, message)


                    # if messaging_event.get("delivery"):  # delivery confirmation
                    #     pass

                    # if messaging_event.get("optin"):  # optin confirmation
                    #     pass
                    log("********Symtom End******** " + str(myUser.symptom))
                    log("-----myUser.diagnosis End------ " + str(myUser.diagnosis))
    log("******** return 'OK', 200 ******** ")
    return "OK", 200

def api_ai_analysis(message):

    CLIENT_ACCESS_TOKEN = 'f2c3166a316843ca95e399a19333c873'
    ai = apiai.ApiAI('31df623f4c1846209c287dc9e8f36a2e')
    request = ai.text_request()
    request.lang = 'en'  # optional, default value equal 'en'
    request.query = message
    response = request.getresponse()
    data = json.loads(response.read())
    #print data
    response = str(data["result"]["fulfillment"]["speech"])
    symptom = str(data["result"]["parameters"]["symptoms"])
    age = str(data["result"]["parameters"]["age"]["unit"])
    gender = str(data["result"]["parameters"]["sex"])
    return response,symptom,gender,age

def api_ai_filled(message):

    CLIENT_ACCESS_TOKEN = 'f2c3166a316843ca95e399a19333c873'
    ai = apiai.ApiAI('31df623f4c1846209c287dc9e8f36a2e')
    request = ai.text_request()
    request.lang = 'en'  # optional, default value equal 'en'
    request.query = message
    response = request.getresponse()
    data = json.loads(response.read())
    print data
    # response = str(data["result"]["fulfillment"]["speech"])
    symptom = str(data["result"]["parameters"]["symptoms"])
    age = str(data["result"]["parameters"]["age"]["unit"])
    gender = str(data["result"]["parameters"]["sex"])

    if(gender!="" and age!="" and symptom!=""):
        return True
    else:
        return False

def send_message(sender_id, message_text):
    #message_text = message_text.encode('utf8')
    log("sending message to {recipient}: {text}".format(recipient=sender_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": sender_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.8/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_message_image(sender_id, message_url):
    #message_url = message_url.encode('utf8')
    log("sending image message to {recipient}: {text}".format(recipient=sender_id, text=message_url.encode('utf8')))
    
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient":{
            "id": sender_id
        },
        "message":{
            "attachment":{
                  "type":"image",
                  "payload":{
                      "url": message_url
                  }
                }
            }
    })
    r = requests.post("https://graph.facebook.com/v2.8/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_message_quick_location(sender_id):
    
    log("sending location message to {recipient}".format(recipient=sender_id))
    
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient":{
            "id": sender_id
                  },
                  "message":{
                  "text":"Please share your location:",
                  "quick_replies":[
                                   {
                                   "content_type": "location",
                                   }
                                   ]
            }
    })
    r = requests.post("https://graph.facebook.com/v2.8/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def init_buttom_template(userTemplate):

    welcome_message = "Hello! How may I help you?"
    if userTemplate.gender is not "":
        if userTemplate.gender == 'male':
            welcome_message = "Hello Mr."+" "+userTemplate.first_name+" "+userTemplate.last_name + "! How may I help you?"
        else:
            welcome_message = "Hello Ms."+" "+userTemplate.first_name+" "+userTemplate.last_name + "! How may I help you?"
    else:
        welcome_message = "Hello "+userTemplate.first_name+" "+userTemplate.last_name + "! How may I help you?"

    log("Sending button template to {recipient}.".format(recipient=userTemplate.id))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": userTemplate.id
        },
        "message":{
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text": welcome_message,
                    "buttons":[
                        {
                        'type': 'postback',
                        'title': 'Symptom checker',
                        'payload': 'SymptomChecker:In order to properly help you, I will need to ask you a few questions. What symptoms do you have?'
                        },
                        {
                        'type': 'postback',
                        'title': 'Health alerts',
                        'payload': 'HealthAlerts:Which diseases and/or symptoms would you like to check in your local area?'
                        },
                        {
                        'type': 'postback',
                        'title': 'Tonic Discounts',
                        'payload': 'TonicDiscountsMain:Please send me your location so I can find hospitals near you..'
                        }
#                               {
#                               "type":"web_url",
#                               "url":"https://petersapparel.parseapp.com",
#                               "title":"Show Website"
#                               },
#                               {
#                               "type":"postback",
#                               "title":"Start Chatting",
#                               "payload":"USER_DEFINED_PAYLOAD"
#                               }

                    ]
                }
            }
        }
    })
    r = requests.post("https://graph.facebook.com/v2.8/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

    log(r.text)

def hospital_buttom_template(sender_id, hospitals_distance_duration_latitude_longitude):
    
    message = str(hospitals_distance_duration_latitude_longitude[0][0]) + " \n\tDistance : " + str(hospitals_distance_duration_latitude_longitude[1]) + " \n\tDuration : " + str(hospitals_distance_duration_latitude_longitude[2])

    log("Sending button template to {recipient}.".format(recipient=sender_id))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
        }
    headers = {
        "Content-Type": "application/json"
        }
    data = json.dumps({
        "recipient": {
            "id": sender_id
        },
        "message":{
            "attachment":{
                "type":"template",
                "payload":{
                      "template_type":"button",
                      "text": message,
                      "buttons":[
                             {
                             'type': 'postback',
                             'title': 'Tonic Discounts',
                             'payload': "TonicDiscounts:"+str(hospitals_distance_duration_latitude_longitude[0][0]) + "\n" + str(hospitals_distance_duration_latitude_longitude[0][1])
                             },
                             {
                             'type': 'web_url',
                             'title': 'Show Website',
                             'url': str(hospitals_distance_duration_latitude_longitude[0][3])
                             }
                    ]
                }
            }
        }
    })
    r = requests.post("https://graph.facebook.com/v2.8/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
                          
    log(r.text)

def map_template(sender_id, title, lat, long, subtitle):
    
    
    log("Sending map template to {recipient}.".format(recipient=sender_id))
    
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
                  "recipient": {
                  "id": sender_id
                  },
                  "message":{
                  "attachment":{
                  "type":"template",
                  "payload":{
                  "template_type":"generic",
                    "elements":
                      [
                             {
                             'title': str(title),
                             'image_url': "https://maps.googleapis.com/maps/api/staticmap?size=764x400&center="+str(lat)+","+str(long)+"&zoom=25&markers="+str(lat)+","+str(long)+"&key="+googleApiKey,
                             'item_url': "https://maps.apple.com/maps?q="+str(lat)+","+str(long)+"&z=16",
                             'subtitle': str(subtitle)
                            }
                      ]
                }
            }
        }
    })
    r = requests.post("https://graph.facebook.com/v2.8/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
    
    log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
