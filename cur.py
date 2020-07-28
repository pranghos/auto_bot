# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 09:31:18 2020

@author: ManasiDhekane
"""

import ibm_db
import ibm_db_dbi
import pandas as pd
import difflib
from math import isnan

def set_value(idx,col_list):
    try:
        val = col_list[idx]
        if type(val)!=str and isnan(val):
            val = ''
    except:
        val = ''
    val = str(val)
    return val

def set_value_none(idx,col_list):
    try:
        val = col_list[idx]
        if type(val)!=str and isnan(val):
            val = None
    except:
        val = None
    if val is not None:
        val = str(val)
    return val


#CSV/Excel Handler Code
    
def Scrape_sheet(input_file):
    df = None
    faqs = []
    try:
        df = pd.read_excel(input_file)
        data_src = "Excel"
    except:
        try:
            df = pd.read_csv(input_file)
            data_src = "CSV"
        except:
            print("Invalid Input File")
            data_src = "Invalid"
    
    intents = []
    intent_examples = []
    entities = []
    entity_values = []
    responses = []
    cluster = []
    intent_kmeans = []
    intent_nlu = []
    entities_nlu = []
    entities_spacy = []
    synonym_dict = []
    synonym_sim = []
    etc1 = []
    etc2 = []
    etc3 = []
    final_intent = []
    final_entities = []
    final_entityvalues = []
    final_synonyms = []
    columns = ["Intent","IntentExamples","Entities","EntityValues","Responses","Questions","Answers","Utterances","Cluster","Intent_Kmeans","Intent_NLU","Entities_NLU","Entities_Spacy","Synonym_Dict","Synonym_Sim","Etc1","Etc2","Etc3","Final_Intent","Final_Entities","Final_EntityValues","Final_Synonyms"]
    columns = [c.upper() for c in columns]
    if df is not None:
        for ci,col in enumerate(df.columns):
            col_mapped = difflib.get_close_matches(col.upper(),columns,n=1,cutoff=0.8)
            print(col,col_mapped)
            if col_mapped == []:
                continue
            else:
                col_mapped = col_mapped[0]
                if col_mapped == 'INTENT':
                    intents = list(df[col])
                elif col_mapped in ["INTENTEXAMPLES","QUESTIONS","UTTERANCES"]:
                    intent_examples = list(df[col])
                elif col_mapped == "ENTITIES":
                    entities = list(df[col])
                elif col_mapped == "ENTITYVALUES":
                    entity_values = list(df[col])
                elif col_mapped in ["RESPONSES","ANSWERS"]:
                    responses = list(df[col])
                elif col_mapped in ["CLUSTER"]:
                    cluster = list(df[col])
                elif col_mapped in ["INTENT_KMEANS"]:
                    intent_kmeans = list(df[col])
                elif col_mapped in ["INTENT_NLU"]:
                    intent_nlu = list(df[col])
                elif col_mapped in ["ENTITIES_NLU"]:
                    entities_nlu = list(df[col])
                elif col_mapped in ["ENTITIES_SPACY"]:
                    entities_spacy = list(df[col])
                elif col_mapped in ["SYNONYM_DICT"]:
                    synonym_dict = list(df[col])
                elif col_mapped in ["SYNONYM_SIM"]:
                    synonym_sim = list(df[col])
                elif col_mapped in ["ETC1"]:
                    etc1 = list(df[col])
                elif col_mapped in ["ETC2"]:
                    etc2 = list(df[col])
                elif col_mapped in ["ETC3"]:
                    etc3 = list(df[col])
                elif col_mapped in ["FINAL_INTENT"]:
                    final_intent = list(df[col])
                elif col_mapped in ["FINAL_ENTITIES"]:
                    final_entities = list(df[col])
                elif col_mapped in ["FINAL_ENTITYVALUES"]:
                    final_entityvalues = list(df[col])
                elif col_mapped in ["FINAL_SYNONYMS"]:
                    final_synonyms = list(df[col])
                else:
                    continue
                
        if len(intent_examples)!=0 and len(responses)!=0:
            len_faqs = len(intent_examples)
            for li in range(len_faqs):
                intent = set_value(li,intents)
                que = intent_examples[li]
                entity = set_value_none(li,entities)
                entity_value = set_value_none(li,entity_values)
                res = responses[li]
                cluster_val = set_value(li,cluster)
                intent_kmeans_val = set_value(li,intent_kmeans)
                intent_nlu_val = set_value(li,intent_nlu)
                entities_nlu_val = set_value_none(li,entities_nlu)
                entities_spacy_val = set_value_none(li,entities_spacy)
                synonym_dict_val = set_value_none(li,synonym_dict)
                synonym_sim_val = set_value_none(li,synonym_sim)
                etc1_val = set_value_none(li,etc1)
                etc2_val = set_value_none(li,etc2)
                etc3_val = set_value_none(li,etc3)
                final_intent_val = set_value(li,final_intent)
                final_entities_val = set_value_none(li,final_entities)
                final_entityvalues_val = set_value_none(li,final_entityvalues)
                final_synonyms_val = set_value_none(li,final_synonyms)
                faqs.append([intent,que,entity,entity_value,res,cluster_val,intent_nlu_val,entities_nlu_val,entities_spacy_val,intent_kmeans_val,synonym_dict_val,synonym_sim_val,etc1_val,etc2_val,etc3_val,final_intent_val,final_entities_val,final_entityvalues_val,final_synonyms_val])
            
    return faqs, data_src

#Push curated data
    
def push_curated_data(input_arg):
    
    faqs, data_src = Scrape_sheet(input_arg)
    
    print("Extracted",len(faqs),"Q/A from",data_src,"source")
    
    print("Connecting to Database...") 
    ibm_db_conn = ibm_db.connect("DATABASE="+"BLUDB"+";HOSTNAME="+"dashdb-txn-sbox-yp-dal09-11.services.dal.bluemix.net"+";PORT="+"50000"+";PROTOCOL=TCPIP;UID="+"uid"+";PWD="+"pwd"+";", "","")
    conn = ibm_db_dbi.Connection(ibm_db_conn)
    
    
    print("\nPushing to Database...\n")  
    table_name = "FAQ_NLP_CURATED"
    
    print("Deleting existing data from",table_name)
    query = "DELETE FROM " + table_name
    stmt = ibm_db.exec_immediate(ibm_db_conn, query)
    
    print("Pushing new data")      
    for faq in faqs:
        query = "INSERT INTO " + table_name + " VALUES('"+faq[0]+"','"+faq[1]+"',"
        if faq[2] is None:
            query += "NULL,"
        else:
            query += "'"+faq[2]+"',"
        if faq[3] is None:
            query += "NULL,"
        else:
            query += "'"+faq[3]+"',"
        query += "'"+faq[4]+"','"+faq[5]+"','"+faq[6]+"',"
        if faq[7] is None:
            query += "NULL,"
        else:
            query += "'"+faq[7]+"',"
        if faq[8] is None:
            query += "NULL,"
        else:
            query += "'"+faq[8]+"',"
        query += "'"+faq[9]+"',"
        if faq[10] is None:
            query += "NULL,"
        else:
            query += "'"+faq[10]+"',"
        if faq[11] is None:
            query += "NULL,"
        else:
            query += "'"+faq[11]+"',"
        if faq[12] is None:
            query += "NULL,"
        else:
            query += "'"+faq[12]+"',"
        if faq[13] is None:
            query += "NULL,"
        else:
            query += "'"+faq[13]+"',"
        if faq[14] is None:
            query += "NULL,"
        else:
            query += "'"+faq[14]+"',"
        query += "'"+faq[15]+"',"
        if faq[16] is None:
            query += "NULL,"
        else:
            query += "'"+faq[16]+"',"
        if faq[17] is None:
            query += "NULL,"
        else:
            query += "'"+faq[17]+"',"
        if faq[18] is None:
            query += "NULL)"
        else:
            query += "'"+faq[18]+"')"
        stmt = ibm_db.exec_immediate(ibm_db_conn, query)
    print("Data Ingested to", table_name)
    conn.close()
    return "Success"

'''    
def main(args):
    values_view = args.values()
    value_iterator = iter(values_view)
    first_value = next(value_iterator)
    abt = push_curated_data(first_value) 
    print("\n Print the stmt \n")
    print(abt)
    return {"message": "Success" }
'''

from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import pandas as pd
import os

app=Flask(__name__)
port = int(os.getenv("PORT", 5000)) 

@app.route('/upload', methods = ['GET'])
def upload_file():
    if request.method == 'GET':
        return render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def uploader():
   if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))
      f_name = f.filename
      abt = push_curated_data(f_name) 
      return 'file uploaded successfully and loaded into databases'
  
@app.route("/export", methods=['GET'])
def export_records():
    return 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    