# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 14:11:13 2020

@author: AnushaRamanujam
"""
import ibm_db
from ibm_db import connect
from ibm_db import tables
import pandas as pd
#import get_config_params
conn = None
def get_conn():
    global conn
    conn = connect('DATABASE=BLUDB;'
                         'HOSTNAME=dashdb-txn-sbox-yp-dal09-11.services.dal.bluemix.net;'
                         'PORT=50000;'
                         'PROTOCOL=TCPIP;'
                         'UID=uid;'
                         'PWD=pwd;', '', '')
    return conn

def get_data(stmt):
    data_list = []
    global conn
    try:
        if not conn:
            conn = get_conn()
        cur = ibm_db.exec_immediate(conn,stmt)
        data_list = []
        result = ibm_db.fetch_assoc(cur)
        while result:
            data_list.append(result)
            result = ibm_db.fetch_assoc(cur)
        ibm_db.close(conn)
        return data_list
    
    except Exception as e:
        print("Could not connect to db", str(e))
    
    
    return data_list

def insert_data(file_loc):
    global conn
    if not conn:
        conn = get_conn()
    df = pd.read_csv(file_loc)
    print(df.shape)
    df.fillna('-',inplace=True)
    for index,row in df.iterrows():
        print(row)
        #stmt = "insert into FAQ_FINAL (FINAL_INTENTS, INTENTEXAMPLES, FINAL_ENTITIES, FINAL_ENTITYVALUES, FINAL_SYNONYMS, FINAL_RESPONSES) values ('"+row["Intents"]+"','"+row["IntentExamples"]+"','"+row["Entities"]+"','"+row["EntityValues"]+"','"+row["Synonyms"]+"','"+row["Responses"]+"')"
        stmt = "insert into FAQ_NLP_CURATED  (FINAL_INTENT, INTENTEXAMPLES, FINAL_ENTITIES, FINAL_ENTITYVALUES, FINAL_SYNONYMS, RESPONSES) values ('"+row["Intents"]+"','"+row["IntentExamples"]+"','"+row["Entities"]+"','"+row["EntityValues"]+"','"+row["Synonyms"]+"','"+row["Responses"]+"')"
        ibm_db.exec_immediate(conn,stmt)
        
def execute_stmt(stmt):
    global conn
    if not conn:
        conn = get_conn()
    cur = ibm_db.exec_immediate(conn,stmt)

