# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 09:36:03 2020

@author: PranabGhosh
"""

from ibm_watson import AssistantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import dialog_nodes
import db_conn
import get_config_params

def create_intents_entities_dialogs():

    assistant_apikey = get_config_params.get_param('ASSISTANT','APIKEY')
    asst_url = get_config_params.get_param('ASSISTANT','URL')
    asst_version = get_config_params.get_param('ASSISTANT','VERSION')
    workspace_name = get_config_params.get_param('ASSISTANT','WORKSPACE_NAME')
    table_name = get_config_params.get_param('DB','TABLENAME')
    intent_col_name = get_config_params.get_param('DB','INTENTNAME')
    entity_col_name = get_config_params.get_param('DB','ENTITYNAME')
    entityvalues_col_name = get_config_params.get_param('DB','ENTITYVALUENAME')
    synonyms_col_name = get_config_params.get_param('DB','SYNONYMSNAME')
    intentexamples_col_name = get_config_params.get_param('DB','INTENTEXAMPLESNAME')
    #Setting Authenticator & creating Assistant
    authenticator = IAMAuthenticator(assistant_apikey)
    asst = AssistantV1(version=asst_version,authenticator=authenticator)
    asst.set_service_url(asst_url)
    
    #GET DATA AS LIST FROM DATABASE
    stmt = 'SELECT * FROM '+table_name
    data_dict_list = db_conn.get_data(stmt)
    intent_dict = {}
    entity_dict = {}
    for i in range(len(data_dict_list)):
        ent = data_dict_list[i][entity_col_name]
        
        intent = data_dict_list[i][intent_col_name]
        if not intent or intent == '-':
            continue
        if ent and ent!='-':
            ent_value = data_dict_list[i][entityvalues_col_name] if data_dict_list[i][entityvalues_col_name] else ''
            ent = ent.replace(' ','') # moved from line # 31
            ent_value = ent_value.replace(' ','')
            syn_values = data_dict_list[i][synonyms_col_name] if data_dict_list[i][synonyms_col_name] else ''
            #EXPECTING VALUES TO BE SEPARATED BY COMMAS IN THE DATABASE
            if syn_values:
                syn_list = [word.strip() for word in syn_values.split(',')]
                value_list = [{"value":ent_value,"type":"synonyms","synonyms":syn_list}]
            else:
                value_list = [{"value":ent_value}]
            if ent in entity_dict:
                entity_dict[ent] = list({x['value']:x for x in entity_dict[ent]+value_list}.values())
            else:
                entity_dict[ent] = value_list    
            
        #ALL INTENT EXAMPLES ARE ADDED AS VALUES FOR THE INTENT KEY
        utt = data_dict_list[i][intentexamples_col_name]
        if intent in intent_dict:
            intent_dict[intent].append({'text':utt})
        else:
            intent_dict[intent]=[{'text':utt}]
            
    intent_list, entity_list = [], []
    for intent in intent_dict:
        intent_list.append({"intent":intent,"examples":intent_dict[intent]})
    
    for entity in entity_dict:
        entity_list.append({"entity":entity, "fuzzy_match":True, "values":entity_dict[entity]})
    #CALL WATSON ASSISTANT API AND CREATE INTENTS, ENTITIES AND DIALOG FLOWS. 
    dialogs, update_dialog_dict = dialog_nodes.create_dialog_nodes(data_dict_list, list(intent_dict.keys()), list(entity_dict.keys()))
    #CREATE WORKSPACE & GET THE WORKSPACE ID
    if data_dict_list:
        resp = asst.create_workspace(name=workspace_name,description='FAQ Chat bot').get_result()
        workspace_id = resp['workspace_id']
        #workspace_id = '00917a58-1dbe-4876-95fc-ccd3ce702a62'
        print(entity_list)
        asst.update_workspace(workspace_id=workspace_id, intents = intent_list, entities = entity_list, dialog_nodes = dialogs)
        
        #THIS SECTION WILL UPDATE DIALOG NODES WITH NEXT STEP OR OUTPUT FOR DIALOG NODES THAT DID NOT HAVE ENTITY
        for update_dialog in update_dialog_dict:
            if 'new_next_step' in update_dialog_dict[update_dialog]:
                asst.update_dialog_node(workspace_id = workspace_id, dialog_node = update_dialog_dict[update_dialog]["dialog_node"], new_next_step = update_dialog_dict[update_dialog]['new_next_step'])
            else:
                asst.update_dialog_node(workspace_id = workspace_id, dialog_node = update_dialog_dict[update_dialog]["dialog_node"], new_output = update_dialog_dict[update_dialog]['new_output'])

def main(args):
    try:
        create_intents_entities_dialogs()
        return {"message" : "Created Intents, Entities & Dialogs"}
    except Exception as e:
        return {"message" : "Exception occured with message - "+str(e)}
    
    
if __name__ == "__main__":
    main({"input": "hi"})  
