#!/usr/bin/python
import psycopg2
import user
import ast
import json
import urllib, json
import infermedica_api
import diagnose
from config import config

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()
        
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        
        # create a cursor
        cur = conn.cursor()
        
        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')
        
        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
        
        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("sql connect error : " + str(error))
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    connect()

def create_tables():
    """ create tables in the PostgreSQL database"""
    
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        cur.execute("create table users (id bigint PRIMARY KEY,symptom VARCHAR(255),gender VARCHAR(50),age INTEGER,diagnosis VARCHAR(8000),first_name VARCHAR(255),last_name VARCHAR(255),profile_pic VARCHAR(500),question_count INTEGER)")
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("sql create_tables error : " + str(error))
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    create_tables()

def drop_tables():
    """ drop tables in the PostgreSQL database"""
    
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        cur.execute("drop table users")
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("sql drop_tables error : " + str(error))
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    drop_tables()


def insert_user(user):
    """ insert a new user into the vendors table """
    sql = "insert into users (id,symptom,gender,age,diagnosis,first_name,last_name,profile_pic,question_count) VALUES("+str(user.id)+",'"+str(user.symptom)+"','"+str(user.gender)+"',"+str(user.age)+",'"+str(user.diagnosis).replace("'", "")+"','"+str(user.first_name).replace("'", "")+"','"+str(user.last_name).replace("'", "")+"','"+str(user.profile_pic)+"',"+str(user.question_count)+")"
    conn = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql)
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("sql insert_user error : " + str(error))
    finally:
        if conn is not None:
            conn.close()


def get_user(id):
    """ query data from the users table """
    conn = None
    Muser = user.MyUser()
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("select id,symptom,gender,age,diagnosis,first_name,last_name,profile_pic,question_count FROM users where id = "+str(id))
        print("The number of users: ", cur.rowcount)
        row = cur.fetchone()
        print(row)
        Muser.id = row[0]
        Muser.symptom = row[1]
        Muser.gender = row[2]
        Muser.age = row[3]
        if row[4] != 'empty':
            dstring = str(row[4]).replace("\n", "")
            print(dstring)
            diag_dict = json.loads(dstring)
            request = infermedica_api.Diagnosis(sex=Muser.gender, age=Muser.age)
            Muser.diagnosis = request
            print("-----diag_dict get_user------ " + str(diag_dict))
            diag_dict["case_id"] = 'null'
            diag_dict["evaluation_time"] = 'null'
            ConditionResultList = infermedica_api.models.diagnosis.ConditionResultList().from_json(diag_dict["conditions"])
#            Muser.diagnosis = request.update_from_api(diag_dict)
            Muser.diagnosis.conditions = ConditionResultList
            Muser.diagnosis.question = infermedica_api.models.diagnosis.DiagnosisQuestion().from_json(diag_dict["question"])
            for sym in diag_dict["symptoms"]:
                Muser.diagnosis.add_symptom(sym["id"],sym["choice_id"])
            print("-----Muser.diagnosis get_user------ " + str(Muser.diagnosis))
        Muser.first_name = row[5]
        Muser.last_name = row[6]
        Muser.profile_pic = row[7]
        Muser.question_count = row[8]
        
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("sql get_user error : " + str(error))
    finally:
        if conn is not None:
            conn.close()
    return Muser

def is_user_available(id):
    """ query data from the users table """
    conn = None
    row_count = 0
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("select id,first_name,last_name FROM users where id = "+str(id))
        print("The number of users: ", cur.rowcount)
        row_count = cur.rowcount
        row = cur.fetchone()
        print(row)
        
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("sql is_user_available error : " + str(error))
    finally:
        if conn is not None:
            conn.close()
    return row_count


def update_user(id, user):
    """ update user based on the id """
    conn = None
    updated_rows = 0
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the UPDATE  statement
        cur.execute("update users set symptom = '"+str(user.symptom)+"',gender = '"+str(user.gender)+"',age = "+str(user.age)+",diagnosis = '"+str(user.diagnosis).replace("'", "")+"',first_name = '"+str(user.first_name)+"',last_name = '"+str(user.last_name)+"',profile_pic = '"+str(user.profile_pic)+"',question_count = "+str(user.question_count)+"  where id = "+str(id))
        # get the number of updated rows
        updated_rows = cur.rowcount
        # Commit the changes to the database
        conn.commit()
        # Close communication with the PostgreSQL database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("sql update_user error : " + str(error))
    finally:
        if conn is not None:
            conn.close()

    return updated_rows


def get_hospitals(district):
    """ query data from the hospitals table """
    conn = None
    Hospitals = []
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("select hospital_name,total_discount_offer,address,web_address,latitude,longitude FROM hospitals where district = '"+str(district)+"';")
        print("The number of Hospitals: ", cur.rowcount)
        row = cur.fetchone()
        
        while row is not None:
            print(row)
            Hospitals.append(row)
            row = cur.fetchone()
        
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("sql get_hospitals error : " + str(error))
    finally:
        if conn is not None:
            conn.close()
    return Hospitals
