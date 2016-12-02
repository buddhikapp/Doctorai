import os
import sys
import json
import requests
import urllib, json
import infermedica_api
import psql
api = infermedica_api.API(app_id='21794b8d', app_key='81f5f69f0cc9d2defaa3c722c0e905bf')
#print(api.info())

class MyUser:

    def __init__(self):
#        self.data = []
        self.id = None
        self.symptom = None
        self.gender = None
        self.age = None
        self.diagnosis = None
        self.first_name = None
        self.last_name = None
        self.profile_pic = None


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
        newUser.first_name = " "
    try:
        newUser.last_name = str(r.json()["last_name"])
    except:
        newUser.last_name = " "
    try:
        newUser.gender = str(r.json()["gender"])
    except:
        newUser.gender = "male"
    try:
        newUser.profile_pic = str(r.json()["profile_pic"])
    except:
        newUser.profile_pic = " "

    newUser.age = 40  #Need to be impliment
    
    psql.insert_user(newUser)
    
    return psql.get_user(newUser.id)


def RemoveUser(user, usersList):
    usersList.remove(user)
    user = None

