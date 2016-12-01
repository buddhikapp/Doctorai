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
import urllib, json
from flask import Flask, request

import infermedica_api

api = infermedica_api.API(app_id='21794b8d', app_key='81f5f69f0cc9d2defaa3c722c0e905bf')
#print(api.info())

app = Flask(__name__)

symptom_mode = False
#symptom = None
#gender = None
#age = None
#diagnosis = None
myUsers = []

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

    global myUsers
    myUser = user.MyUser()
    
    if "object" in data:
        if data["object"] == "page":
            for entry in data["entry"]:
                for messaging_event in entry["messaging"]:
                    log("********Symtom Start******** " + str(myUser.symptom))
                    log("myUsers Lenght : " + str(len(myUsers)))
                    if messaging_event.get("postback") or messaging_event.get("message"):
                        if user.CheckUser(messaging_event["sender"]["id"], myUsers):
                            myUser = user.GetUser(messaging_event["sender"]["id"], myUsers)
                            log("User Found : " + str(myUser.id))
                        else:
                            myUser = user.CreateUser(messaging_event["sender"]["id"])
                            myUsers.append(myUser)
                            log("User Created : " + str(myUser.id))
                    log("myUsers Lenght : " + str(len(myUsers)))
                    
                    if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message

                        recipient_id = messaging_event["recipient"]["id"]
                        log("recipient_id : " + recipient_id)
                        message = messaging_event["postback"]["payload"]
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
                                myUser.symptom = None
                                myUser.diagnosis = None
                                init_buttom_template(myUser)
                            elif myUser.symptom is None:
                                search_result = search.search_symtom_limit(message, 5)
                                log("----------- " + str(search_result))
                                if len(search_result) > 0:
                                    send_message(myUser.id, "Give me a sec!")
                                    sid = str(search_result[0]["id"])
                                    log("************ " + sid)
                                else:
                                    send_message(myUser.id, "Sorry, Server appears to be busy at the moment. Please try again later.")


                            if myUser.symptom is not None:
                                if string.find(message.upper(),str(myUser.diagnosis.question.items[0]["choices"][0]["label"]).upper()) is not -1:
                                    myUser.diagnosis = diagnose.improve_diagnosis(myUser.diagnosis,myUser.id,myUser.symptom,str(myUser.diagnosis.question.items[0]["choices"][0]["id"]))
                                elif string.find(message.upper(),str(myUser.diagnosis.question.items[0]["choices"][1]["label"]).upper()) is not -1:
                                    myUser.diagnosis = diagnose.improve_diagnosis(myUser.diagnosis,myUser.id,myUser.symptom,str(myUser.diagnosis.question.items[0]["choices"][1]["id"]))
                                elif string.find(message.upper(),str(myUser.diagnosis.question.items[0]["choices"][2]["label"]).upper()) is not -1:
                                    myUser.diagnosis = diagnose.improve_diagnosis(myUser.diagnosis,myUser.id,myUser.symptom,str(myUser.diagnosis.question.items[0]["choices"][2]["id"]))
                                else:
                                    send_message(myUser.id, "Sorry, I didn't get that. Please enter your answer again.")
                                if myUser.diagnosis.conditions[0]["probability"] > 0.25:
                                    send_message(myUser.id, "I suspect "+str(myUser.diagnosis.conditions[0]["name"])+" with a probability of "+str(myUser.diagnosis.conditions[0]["probability"]))
                                    send_message(myUser.id, "Please send me your location so I can find a doctor near you")
                                    send_message_quick_location(myUser.id)
#                                    myUser.symptom = None
#                                    myUser.gender = None
#                                    myUser.age = None
#                                    myUser.diagnosis = None

                                    log("myUsers Lenght : " + str(len(myUsers)))
                                    user.RemoveUser(myUser,myUsers)
                                    log("myUsers Lenght : " + str(len(myUsers)))

                                else:
                                    myUser.symptom = str(myUser.diagnosis.question.items[0]["id"])
                                    response = str(myUser.diagnosis.question.text.encode('utf8'))
                                    if str(myUser.diagnosis.question.type) == "group_single" or str(myUser.diagnosis.question.type) == "group_multiple":
                                        response = response + "\n " + str(myUser.diagnosis.question.items[0]["name"].encode('utf8')) + "? "
                                    for x in myUser.diagnosis.question.items[0]["choices"]:
                                        response = response + "\n - " + str(x["label"])
                                    send_message(myUser.id, response)
                                log("-----myUser.diagnosis------ " + str(myUser.diagnosis))
                            


                            if myUser.diagnosis is None and sid is not None:
                                myUser.diagnosis = diagnose.init_diagnose(sid,myUser.age,myUser.gender,myUser.id)
                                log("-----myUser.diagnosis------ " + str(myUser.diagnosis))
                                myUser.symptom = str(myUser.diagnosis.question.items[0]["id"])
                                response = str(myUser.diagnosis.question.text.encode('utf8'))
                                if str(myUser.diagnosis.question.type) == "group_single" or str(myUser.diagnosis.question.type) == "group_multiple":
                                    response = response + "\n " + str(myUser.diagnosis.question.items[0]["name"].encode('utf8')) + "? "
                                for x in myUser.diagnosis.question.items[0]["choices"]:
                                    response = response + "\n - " + str(x["label"])
                                send_message(myUser.id, response)


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
                                clinic_type = "hospital"
                                clinicsURL = "https://api.foursquare.com/v2/venues/search?ll="+str(latitude)+","+str(longitude)+"&radius=15000&query="+clinic_type+"&client_id=1TCDH3ZYXC3NYNCRVL1RL4WEGDP4CHZSLPMKGCBIHAYYVJWA&client_secret=VASKTPATQLSPXIFJZQ0EZ4GDH2QAZU1QGEEZ4YDCKYA11V2J&v=20160917"
                                r = urllib.urlopen(clinicsURL)
                                data = json.loads(r.read())
                                hospitals = []
                                latitudes = []
                                longitudes = []
                                venues = data["response"]["venues"]
                                if len(venues) > 3:
                                    maxi = 3
                                else:
                                    maxi = len(venues)
                                for x in range(0, maxi):
                                    hospitals.append(venues[x]["name"])
                                    send_message(myUser.id, "Option #"+str(x+1)+": "+venues[x]["name"].encode('utf8'))
                                    latitudes.append(venues[x]["location"]["lat"])
                                    longitudes.append(venues[x]["location"]["lng"])
                                message = "Location: " + str(latitude) + ", " + str(longitude)

                                mapurl = "https://maps.googleapis.com/maps/api/staticmap?center="+str(latitude)+","+str(longitude)+"&markers=color:green%7C"+str(latitude)+","+str(longitude)+"&key=AIzaSyBwJxBRpzx10gHVn1V1m2Cksbs8v1pQEQA&size=800x800"
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
                        'payload': 'In order to properly help you, I will need to ask you a few questions. What symptoms do you have?'
                        },
                        {
                        'type': 'postback',
                        'title': 'Health alerts',
                        'payload': 'Which diseases and/or symptoms would you like to check in your local area?'
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


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
