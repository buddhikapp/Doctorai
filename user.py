import os
import sys
import json
import requests
import urllib, json
import infermedica_api
import psql
api = infermedica_api.API(app_id='aaccd529', app_key='2507fff3b3104d61bca7f4eb7511dc7b')
#print(api.info())

class MyUser:

    def __init__(self):
#        self.data = []
        self.id = None
        self.symptom = 'empty'
        self.gender = 'empty'
        self.age = None
        self.diagnosis = 'empty'
        self.first_name = 'empty'
        self.last_name = 'empty'
        self.profile_pic = 'empty'
        self.question_count = 0


def CheckUser(userID):
    row_count = psql.is_user_available(userID)
    if row_count == 1:
        return True
    else:
        return False

def GetUser(userID):
    return psql.get_user(userID)

def CreateUser(userID):
    newUser = MyUser()
    newUser.id = userID
    r = requests.get('https://graph.facebook.com/v2.8/'+userID+
                 '?fields=first_name,last_name,locale,timezone,gender&access_token='
                 +os.environ["PAGE_ACCESS_TOKEN"])
    try:
        newUser.first_name = str(r.json()["first_name"])
    except:
        newUser.first_name = "empty"
    try:
        newUser.last_name = str(r.json()["last_name"])
    except:
        newUser.last_name = "empty"
    try:
        newUser.gender = str(r.json()["gender"])
    except:
        newUser.gender = "empty"
    try:
        newUser.profile_pic = str(r.json()["profile_pic"])
    except:
        newUser.profile_pic = "empty"

    newUser.symptom = "empty"
    newUser.diagnosis = "empty"
    newUser.age = 40  #Need to be impliment
    newUser.question_count = 0;
    
    psql.insert_user(newUser)
    
    return psql.get_user(newUser.id)


def RemoveUser(user, usersList):
    usersList.remove(user)
    user = None

