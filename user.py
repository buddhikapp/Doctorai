import os
import sys
import json
import requests
import urllib, json
import infermedica_api
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