#!/usr/bin/python
import psycopg2
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
        print("sql error : " + str(error))
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
        cur.execute("create table users (id INTEGER PRIMARY KEY,symptom VARCHAR(255),gender VARCHAR(50),age INTEGER,diagnosis VARCHAR(8000),first_name VARCHAR(255),last_name VARCHAR(255),profile_pic VARCHAR(500))")
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("sql error : " + str(error))
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
        print("sql error : " + str(error))
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    drop_tables()


def insert_user(user):
    """ insert a new user into the vendors table """
    sql = 'insert into users (id,first_name,last_name,gender,profile_pic,age) VALUES('+user.id+',"'+user.first_name+'","'+user.last_name+'","'+user.gender+'","'+user.profile_pic+'",'+user.age+')'
    conn = None
    vendor_id = None
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
        print("sql error : " + str(error))
    finally:
        if conn is not None:
            conn.close()


def get_user(id):
    """ query data from the users table """
    conn = None
    row = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute('select id,first_name,last_name,gender,profile_pic,age,symptom,diagnosis FROM users where id == '+id+'')
        print("The number of users: ", cur.rowcount)
        row = cur.fetchone()
        print(row)
        
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return row