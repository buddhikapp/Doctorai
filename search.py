import os
import sys
import json
import requests
import urllib, json
import infermedica_api
api = infermedica_api.API(app_id='aaccd529', app_key='2507fff3b3104d61bca7f4eb7511dc7b')
print(api.info())

def search_symtom(phrase):
	return api.search(phrase)

def search_symtom(phrase, limit):
    return api.search(phrase, max_results=limit)

def search_symtom(phrase, gender):
    return api.search(phrase, sex=gender)

def search_symtom(phrase, gender, limit):
    return api.search(phrase, sex=gender, max_results=limit)

def search_symtom(phrase, search_filters):
    return api.search(phrase, filters=search_filters)

def search_symtom(phrase, search_filters, gender):
    return api.search(phrase, filters=search_filters, sex=gender)

def search_symtom(phrase, search_filters, gender, limit):
    return api.search(phrase, filters=search_filters, sex=gender, max_results=limit)