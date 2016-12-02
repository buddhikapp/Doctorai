#!/usr/bin/python
import psycopg2
import user
import ast
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
        cur.execute("create table users (id bigint PRIMARY KEY,symptom VARCHAR(255),gender VARCHAR(50),age INTEGER,diagnosis VARCHAR(8000),first_name VARCHAR(255),last_name VARCHAR(255),profile_pic VARCHAR(500))")
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
    sql = "insert into users (id,symptom,gender,age,diagnosis,first_name,last_name,profile_pic) VALUES("+str(user.id)+",'"+str(user.symptom)+"','"+str(user.gender)+"',"+str(user.age)+",'"+str(user.diagnosis)+"','"+str(user.first_name)+"','"+str(user.last_name)+"','"+str(user.profile_pic)+"')"
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
        cur.execute("select id,symptom,gender,age,diagnosis,first_name,last_name,profile_pic FROM users where id = "+str(id))
        print("The number of users: ", cur.rowcount)
        row = cur.fetchone()
        print(row)
        Muser.id = row[0]
        Muser.symptom = row[1]
        Muser.gender = row[2]
        Muser.age = row[3]
        Muser.diagnosis = ast.literal_eval(row[4])
        Muser.first_name = row[5]
        Muser.last_name = row[6]
        Muser.profile_pic = row[7]
        
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
        cur.execute("update users set symptom = '"+str(user.symptom)+"',gender = '"+str(user.gender)+"',age = "+str(user.age)+",diagnosis = '"+str(user.diagnosis)+"',first_name = '"+str(user.first_name)+"',last_name = '"+str(user.last_name)+"',profile_pic = '"+str(user.profile_pic)+"'  where id = "+str(id))
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
