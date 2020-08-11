# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 14:07:16 2020

@author: PranabGhosh
"""
# Required packages
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
import pandas as pd
import ibm_db
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, ConceptsOptions, EntitiesOptions, KeywordsOptions
import ibm_db_dbi
import spacy
from spacy import displacy
spacy.load("en_core_web_lg")
spacy.load("en_core_web_sm")
from collections import Counter
import en_core_web_sm
from nltk.stem import PorterStemmer
import requests

def clustering(df1):
    print("entered clustering function")
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(df1['INTENTEXAMPLES'])
    df1['CLUSTER']=''
    
    # Intent clustering with initial 10 clusters
    true_k = 10
    model = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1)
    model.fit(X)
    
    KMeans(algorithm='auto', copy_x=True, init='k-means++', max_iter=100,
        n_clusters=10, n_init=1, n_jobs=1, precompute_distances='auto',
        random_state=None, tol=0.0001, verbose=0)
    
    order_centroids = model.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names()
    
    for i in range(true_k):
        print("Cluster %d:" % i),
        for ind in order_centroids[i, :10]:
            print('%s' % terms[ind])
    
    i=0
    for i in range(0, len(df1)):
        input = df1['INTENTEXAMPLES'][i]
        X = vectorizer.transform([input])
        predicted = model.predict(X)
        df1['CLUSTER'][i] = predicted[0]
        i = i+1    
    
    
    df2 = df1.groupby('CLUSTER')['INTENTEXAMPLES'].agg(' '.join).reset_index()
    
    # Fetching intents of the clustered questions
    authenticator = IAMAuthenticator('FMUFQJHtKvAqukIATHrBQqnVy8GP_5lvN5Iq0JzokZgn')
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2019-07-12',
        authenticator=authenticator
    )
    
    natural_language_understanding.set_service_url('https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/f9f3fbd1-3de7-44e6-a53a-dc93992d6627')
    df2['INTENT'] = ''
    
    
    i=0
    for i in range(0, len(df2)):
        try:
            response = natural_language_understanding.analyze(text = df2['INTENTEXAMPLES'][i], features=Features(keywords=KeywordsOptions(sentiment=False,emotion=False,limit=3))).get_result()
            if response['keywords'] != []:
                     if len(response['keywords'])==1: 
                         df2['INTENT'][i]= response['keywords'][0]['text']    
                     elif len(response['keywords'])==2: 
                         a = response['keywords'][0]['text']    
                         b = response['keywords'][1]['text']
                         df2['INTENT'][i]=(a+'_'+b)
                         
                     else:
                         a = response['keywords'][0]['text']    
                         b = response['keywords'][1]['text']
                         c = response['keywords'][2]['text']
                         df2['INTENT'][i]=(a+'_'+b+'_'+c)
            else:
                    df2['INTENT'][i] = ''
        except:
            df2['INTENT'][i] = ''
        i = i+1    
    
    df2['INTENT'] = df2['INTENT'].replace(' ', '', regex=True)
    
    event_dictionary = pd.Series(df2.INTENT.values,index=df2.CLUSTER).to_dict()


    df1['INTENT_KMEANS'] = df1['CLUSTER'].apply(set_value, args =(event_dictionary, )) 
    
    #df1.to_excel('C:/McD/covid/NLP_bot/NLP.xlsx', encoding ='utf8')
    #print("excel printed")
    
    return df1
    
def NLU(df1):
    # Entity values
    df1['INTENTS_NLU']= ''
    df1['ENTITIES_NLU']= ''
    df1['ENTITIES_SPACY']= ''
    # Fetching important keywords for Intent using NLU using 3 keywords
    i=0
    authenticator = IAMAuthenticator('FMUFQJHtKvAqukIATHrBQqnVy8GP_5lvN5Iq0JzokZgn')
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2019-07-12',
        authenticator=authenticator
    )
    
    natural_language_understanding.set_service_url('https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/f9f3fbd1-3de7-44e6-a53a-dc93992d6627')
    for i in range(0, len(df1)):
        try:
            response = natural_language_understanding.analyze(text = df1['INTENTEXAMPLES'][i], features=Features(keywords=KeywordsOptions(sentiment=False,emotion=False,limit=3))).get_result()
            if response['keywords'] != []:
                     if len(response['keywords'])==1: 
                         df1['INTENTS_NLU'][i]= response['keywords'][0]['text']    
                     elif len(response['keywords'])==2: 
                         a = response['keywords'][0]['text']    
                         b = response['keywords'][1]['text']
                         df1['INTENTS_NLU'][i]=(a+'_'+b)
                         
                     else:
                         a = response['keywords'][0]['text']    
                         b = response['keywords'][1]['text']
                         c = response['keywords'][2]['text']
                         df1['INTENTS_NLU'][i]=(a+'_'+b+'_'+c)
            else:
                    df1['INTENTS_NLU'][i] = ''
        except:
            df1['INTENTS_NLU'][i] = ''
        i = i+1    
    #fetching entities from NLU
    i=0
    for i in range(0, len(df1)):
        try:
            response = natural_language_understanding.analyze(text = df1['INTENTEXAMPLES'][i], features=Features(entities=EntitiesOptions(sentiment=False,limit=2))).get_result()
        #    features=Features(concepts=ConceptsOptions(limit=3))).get_result()
            if response['entities'] == []:
                    df1['ENTITIES_NLU'][i] = ''
            else: 
                    df1['ENTITIES_NLU'][i] = response['entities'][0]['text']
        except:
            df1['ENTITIES_NLU'][i] = ''
        i = i+1    
    return df1
    

def Spacy(df1):
    
    nlp = en_core_web_sm.load()
    nlp = spacy.load('en_core_web_sm')
    i=0
    for i in range(0, len(df1)):
        doc = nlp(df1['INTENTEXAMPLES'][i])
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                #print('pass')
                df1['ENTITIES_SPACY'][i]= ent.text
                #print(ent.text, ent.label_)
                break
        i = i+1    
    return df1


def Synonym(df1):
    # Generating synonyms using Google Dictionary API
    d = {'Tracker' : range(0,8000)}
    df3 = pd.DataFrame(d)
    df3['synonyms0']=''
    df3['synonyms1']=''
    df3['synonyms2']=''
    df3['synonyms3']=''
    df3['synonyms4']=''
    df3['synonyms5']=''
    df3['synonyms6']=''
    df3['synonyms7']=''
    df3['synonyms8']=''
    df3['synonyms9']=''
    df3 = df3.drop(['Tracker'], axis = 1) 
    df1['SYNONYM_DICT']=''
    df1['SYNONYM_SIM']=''
    df1['ETC1']=''
    df1['ETC2']=''
    df1['ETC3']=''
    df1['FINAL_INTENT']=''
    df1['FINAL_ENTITIES']=''
    df1['FINAL_ENTITYVALUES']=''
    df1['FINAL_SYNONYMS']=''
    
    
    i=0
    for i in range(0,len(df1)):
        word_id = str(df1['ENTITIES'][i])
        if (word_id== None):
            df1['SYNONYM_DICT'][i]=''
        else:
            url = 'https://api.dictionaryapi.dev/api/v2/entries/en/'  + word_id.lower()
            r = requests.get(url) 
            syn= r.json()
            f=0
            try:
                for meanings in syn[0]['meanings']:
                    g=0
                    try:
                        for synonyms in syn[0]['meanings'][f]['definitions'][0]['synonyms']:
                           try:
                                df3["synonyms"+str(g)][i] = (syn[0]['meanings'][f]['definitions'][0]['synonyms'][g])
                                g=g+1
                                #print("g =", g)
                           except KeyError:
                               print("Item missing inner")
                        #print("f =", f)
                        f=f+1
                    except KeyError:
                               print("Item missing outer")    
            except KeyError:
                               print("Item missing outermost")    
        #print("i =", i)    
        i = i+1    
    df1['SYNONYM_DICT'] = df3.fillna('').apply(lambda x: ', '.join(filter(None, x)), axis=1)    

    ps = PorterStemmer()
    nlp = spacy.load('en_core_web_lg')
    def most_similar(word, topn=10):
        word = nlp.vocab[str(word)]
        if word.has_vector == False:
            return []
        else:
            queries = [
                    w for w in word.vocab 
                    if w.is_lower == word.is_lower and w.prob >= -15 and np.count_nonzero(w.vector)
                    ]
            by_similarity = sorted(queries, key=lambda w: word.similarity(w), reverse=True)
            similar = []
            for w in by_similarity:
                if len(similar) == topn:
                    break
                if w.lower_ != word.lower_ and ps.stem(w.lower_) != ps.stem(word.lower_):
                    similar.append(w.lower_)
            stemmed, final = set(), []
            for ele in similar:
                if ps.stem(ele) in stemmed:
                    continue
                else:
                    final.append(ele)
                    stemmed.add(ps.stem(ele))
            return final
    synonyms = []
    for ele in df1["ENTITIES"]:
        syns = ""
        if ele != "":
            syns = ",".join(most_similar(ele))
        synonyms.append(syns)
    df1['SYNONYM_SIM'] = synonyms   
    #df1.to_csv('C:/Users/jitendragaur/Documents/NLP.csv', encoding ='utf8')
    # Change the path to your local system
    df1.to_excel('NLP.xlsx', encoding ='utf8')
    print("excel printed")
    return df1
        
# Define a function to map the values 
def set_value(row_number, assigned_value): 
    return assigned_value[row_number] 


import flask
from flask import Flask, request, jsonify, render_template
import os

app = flask.Flask(__name__)
port = int(os.getenv("PORT", 9099)) 
@app.route('/nlp', methods=['POST'])
def nlp():
    if request.method == 'POST':
        
        ibm_db_conn = ibm_db.connect("DATABASE="+"BLUDB"+";HOSTNAME="+"dashdb-txn-sbox-yp-dal09-11.services.dal.bluemix.net"+";PORT="+"50000"+";PROTOCOL=TCPIP;UID="+"uid"+";PWD="+"pwd"+";", "","")
        conn = ibm_db_dbi.Connection(ibm_db_conn)
        # Reading table from DB
        df1=pd.read_sql("SELECT * FROM FAQ_DATAPREP",conn)
        df1 = df1.fillna('')
        data_dict = df1.to_dict()
        #main()
        textfile = clustering(df1)
        #data_dict = textfile.to_dict()
        NLU_list = NLU(textfile)
        #data_dict = textfile.to_dict()
        output_spacy = Spacy(NLU_list)
        Synonym_list = Synonym(output_spacy)
        conn.close() # closing database connection
    return data_dict
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port)
   

   
