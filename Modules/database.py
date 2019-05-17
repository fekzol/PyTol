#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 08:43:30 2019

@author: zoli
"""

import sqlite3, global_vars
from sqlite3 import Error

def create_database(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print e
    finally:
        conn.close()

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def add_tables(db_file):
    sql_create_dim_table = """ CREATE TABLE IF NOT EXISTS dimensions (
                                        dim_id integer PRIMARY KEY,
                                        dim_descr text NOT NULL,
                                        dim_nom real NOT NULL,
                                        tol_plus real NOT NULL,
                                        tol_minus real NOT NULL,
                                        comment text,
                                        part_id integer NOT NULL,
                                        FOREIGN KEY (part_id) REFERENCES parts(part_id)
                                    ); """
 
    sql_create_parts_table = """CREATE TABLE IF NOT EXISTS parts (
                                    part_id integer PRIMARY KEY,
                                    part_no text NOT NULL
                                );"""
    sql_create_stacks_table = """CREATE TABLE IF NOT EXISTS stacks (
                                    stack_id integer PRIMARY KEY,
                                    stack_name text NOT NULL,
                                    stack_tolp real NOT NULL,
                                    stack_tolm real NOT NULL,
                                    confidence integer NOT NULL,
                                    author text,
                                    date text,
                                    image_data blob,
                                    image_file text,
                                    rem text,
                                    rev_comment text
                                );"""
    sql_create_stack_dim_table = """ CREATE TABLE IF NOT EXISTS stack_dims (
                                        stackdim_id integer PRIMARY KEY,
                                        coef real NOT NULL,
                                        dist text NOT NULL,
                                        dim_id integer NOT NULL,
                                        stack_id integer NOT NULL,
                                        FOREIGN KEY (stack_id) REFERENCES stacks(stack_id)
                                    ); """
    
    # create a database connection
    conn = create_connection(db_file)
    if conn is not None:
        # create parts table
        create_table(conn, sql_create_parts_table)
        # create dimensions table
        create_table(conn, sql_create_dim_table)
        # create stacks table
        create_table(conn, sql_create_stacks_table)
        # create stack_dims table
        create_table(conn, sql_create_stack_dim_table)
    else:
        print "Error! cannot create the database connection."


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return None

def get_parts(db_file):
    db = create_connection(db_file)
    cur = db.cursor()
    with db:
        cur.execute("SELECT * FROM parts")
    global_vars.partList = create_List(cur.fetchall())

        
def get_dimensions(db_file, part_id):
    db = create_connection(db_file)
    cur = db.cursor()
    with db:
        cur.execute("SELECT * FROM dimensions WHERE part_id = %s" %part_id)
        global_vars.dimList = create_List(cur.fetchall())
    
def get_stacks(db_file):
    db = create_connection(db_file)
    cur = db.cursor()
    with db:
        cur.execute("""SELECT stack_id,
                              stack_name,
                              stack_tolp,
                              stack_tolm,
                              confidence,
                              author,
                              date,
                              rev_comment 
                    FROM stacks""")
        stacks = cur.fetchall()
    #print stacks[0][1]
    global_vars.stackList = create_List(stacks)
    #global_vars.stackList = stacks

def get_stack_dimensions(db_file, stack_id):
    db = create_connection(db_file)
    cur = db.cursor()
    with db:
        cur.execute("SELECT * FROM stack_dims WHERE stack_id = %s" %stack_id)
        global_vars.stackDimList = create_List(cur.fetchall())

def get_dim_data(db_file, dim_id):
    dim_data = []
    db = create_connection(db_file)
    cur = db.cursor()
    with db:
        cur.execute("SELECT * FROM dimensions WHERE dim_id = %s" %dim_id)
        dim_data = create_List(cur.fetchall())
    return dim_data


def open_db(db_file):
    get_parts(db_file)
    get_dimensions(db_file, 1)
    get_stacks(db_file)
    get_stack_dimensions(db_file, 1)
     
def create_part(db_file, part):
    """
    Create a new part into the parts table
    :param part_no
    :return: part id
    """
    db = create_connection(db_file)
    with db:
        sql = """ INSERT INTO parts(part_no)
                  VALUES(?) """
    
        cur = db.cursor()
        cur.execute(sql, (part,))
    get_parts(db_file)
    
def create_stack(db_file, name, tolp, tolm, conf, aut, date, rev_comment):
    db = create_connection(db_file)
    with db:
        sql = """ INSERT INTO stacks(stack_name, stack_tolp, stack_tolm, confidence, author, date, rev_comment)
                  VALUES(?,?,?,?,?,?,?) """
    
        cur = db.cursor()
        cur.execute(sql, (name, tolp, tolm, conf, aut, date, rev_comment))
    get_stacks(db_file)
    
def create_dim(db_file, dim_descr, dim_nom, tol_plus, tol_minus, comment, part_id):
    """
    Create a new dimension into the dimensions table
    :dim_descr
    :dim_nom
    :tol_plus
    :tol_minus
    :comment
    :part_id
    """
    db = create_connection(db_file)
    with db:
        sql = """ INSERT INTO dimensions(dim_descr,dim_nom,tol_plus,tol_minus,comment,part_id)
                  VALUES(?,?,?,?,?,?) """
        cur = db.cursor()
        cur.execute(sql, (dim_descr, dim_nom, tol_plus, tol_minus, comment, part_id))
    get_dimensions(db_file, part_id)
    
def edit_dim(db_file, dim_descr, dim_nom, tol_plus, tol_minus, comment, dim_id, part_id):
    try:
        db = create_connection(db_file)
        with db:
            sql = """ UPDATE dimensions
                      SET dim_descr = ?,
                          dim_nom = ?,
                          tol_plus = ?,
                          tol_minus = ?,
                          comment = ?
                      WHERE dim_id = ?"""
            cur = db.cursor()
            cur.execute(sql, (dim_descr, dim_nom, tol_plus, tol_minus, comment, dim_id))
            cur.execute("SELECT * FROM dimensions WHERE part_id = %s" %part_id)
            global_vars.dimList = create_List(cur.fetchall())
           
    except Error as e:
        print(e)  
        
def edit_part(db_file, part_no, partID):
    try:
        db = create_connection(db_file)
        with db:
            sql = """ UPDATE parts
                      SET part_no = ?
                      WHERE part_id = ?"""
            cur = db.cursor()
            cur.execute(sql, (part_no, partID))
        get_parts(db_file)
    except Error as e:
        print(e)
        
def edit_stack(db_file, stack_name, tolp, tolm, conf, auth, date, rev_comment, stackID):
    try:
        db = create_connection(db_file)
        with db:
            sql = """ UPDATE stacks
                      SET stack_name = ?,
                          stack_tolp = ?,
                          stack_tolm = ?,
                          confidence = ?,
                          author = ?,
                          date = ?,
                          rev_comment = ?
                      WHERE stack_id = ?"""
            cur = db.cursor()
            cur.execute(sql, (stack_name, tolp, tolm, conf, auth, date, rev_comment, stackID))
        get_stacks(db_file)
    except Error as e:
        print(e)
  
def move_to_stack(db_file, coef, dist, dim_id, stack_id):
    db = create_connection(db_file)
    with db:
        sql = """ INSERT INTO stack_dims (coef,dist,dim_id,stack_id)
                  VALUES(?,?,?,?)"""
        cur = db.cursor()
        cur.execute(sql, (coef, dist, dim_id, stack_id))
        cur.execute("SELECT * FROM stack_dims WHERE stack_id = %s" %stack_id)
        global_vars.stackDimList = create_List(cur.fetchall())
            

def delete_stack_entry(db_file, ID, stack_id):
    db = create_connection(db_file)
    with db:
        sql = """ DELETE FROM stack_dims
                WHERE stackdim_id = ?"""
        cur = db.cursor()
        cur.execute(sql, (ID,))
        cur.execute("SELECT * FROM stack_dims WHERE stack_id = %s" %stack_id)
        global_vars.stackDimList = create_List(cur.fetchall())
        
def replace_stack_entry(db_file, rowid, dim_id, stack_id):
    db = create_connection(db_file)
    with db:
        sql =""" UPDATE stack_dims
                  SET dim_id = ?
                  WHERE stackdim_id = ?"""
        cur = db.cursor()
        cur.execute(sql, (dim_id, rowid))
        cur.execute("SELECT * FROM stack_dims WHERE stack_id = %s" %stack_id)
        global_vars.stackDimList = create_List(cur.fetchall())
        
def delete_stack(db_file, stack_id):
    db = create_connection(db_file)
    with db:
        sql = """ DELETE FROM stacks
                WHERE stack_id = ?"""
        cur = db.cursor()
        cur.execute(sql, (stack_id,))
        cur.execute("""SELECT stack_id,
                              stack_name,
                              stack_tolp,
                              stack_tolm,
                              confidence,
                              author,
                              date,
                              rev_comment 
                    FROM stacks""")
        stacks = cur.fetchall()
    global_vars.stackList = create_List(stacks)
    
def update_stack_entry(db_file, stackid, rowid, coef, dist):
    db = create_connection(db_file)
    with db:
        sql = """ UPDATE stack_dims
                  SET coef = ?,
                      dist = ?
                  WHERE stackdim_id = ?"""
        cur = db.cursor()
        cur.execute(sql, (coef, dist, rowid))
        cur.execute("SELECT * FROM stack_dims WHERE stack_id = %s" %stackid)
        global_vars.stackDimList = create_List(cur.fetchall())

def insert_image(db_file, stackid, imagedata, imagename):
    db = create_connection(db_file)
    with db:
        sql = """ UPDATE stacks
                  SET image_data = ?,
                      image_file = ?
                  WHERE stack_id = ?"""
        cur = db.cursor()
        cur.execute(sql, (sqlite3.Binary(imagedata), str(imagename), stackid))
        #print "image inserted to database"

def extract_image(db_file, stackid):
    db = create_connection(db_file)
    with db:
        cur = db.cursor()
        cur.execute("SELECT image_data FROM stacks WHERE stack_id = %s" %stackid)
        return cur.fetchone()[0]
    
def insert_remark(db_file, stackid, remark):
    db = create_connection(db_file)
    with db:
        sql = """ UPDATE stacks
                  SET rem = ?
                  WHERE stack_id = ?"""
        cur = db.cursor()
        cur.execute(sql, (remark, stackid))

        
def get_remark(db_file, stackid):
    db = create_connection(db_file)
    with db:
        cur = db.cursor()
        cur.execute("SELECT rem FROM stacks WHERE stack_id = %s" %stackid)
        return cur.fetchone()[0]
        
def clean(db_file):
     db = create_connection(db_file)   
     db.execute("VACUUM")
     db.close()
    
def create_List(sql_query):
    lis = []
    for i in sql_query:
        d = str(i).replace('(','').replace(')','').replace('u\'','').replace('\'','')
        lis.append(d.split(', '))
    return lis

def create_column(db_file, table, col, t):
    db = create_connection(db_file) 
    with db:
        cur = db.cursor()
        cur.execute("ALTER TABLE %s ADD COLUMN %s %s" %(table, col, t))
    db.close()
    
def get_columns(db_file, table):
    db = create_connection(db_file) 
    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM %s" %table)
        columns = list(map(lambda x: x[0], cur.description))
    return  columns