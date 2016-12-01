import os
import sys
import json
import requests
import urllib, json
import infermedica_api
import psycopg2
import sys
api = infermedica_api.API(app_id='21794b8d', app_key='81f5f69f0cc9d2defaa3c722c0e905bf')
#print(api.info())



def main():
    #Define our connection string
    conn_string = "host='ec2-174-129-3-207.compute-1.amazonaws.com' dbname='db19l6fi8jcmti' user='ewviievtbagcfo' password='XOg2zdlJmYY8L35Cs1L-Yf6JNj'"
        
        # print the connection string we will use to connect
        print "Connecting to database\n	->%s" % (conn_string)
        
        # get a connection, if a connect cannot be made an exception will be raised here
        conn = psycopg2.connect(conn_string)
        
        # conn.cursor will return a cursor object, you can use this cursor to perform queries
        cursor = conn.cursor()
        print "Connected!\n"

if __name__ == "__main__":
    main()