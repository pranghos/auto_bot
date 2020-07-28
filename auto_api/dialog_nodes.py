# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 18:54:33 2020

@author: AnushaRamanujam
"""
import random
import get_config_params


intent_col_name = get_config_params.get_param('DB','INTENTNAME')
entity_col_name = get_config_params.get_param('DB','ENTITYNAME')
entityvalues_col_name = get_config_params.get_param('DB','ENTITYVALUENAME')
responses_col_name = get_config_params.get_param('DB','RESPONSESNAME')
intentexamples_col_name = get_config_params.get_param('DB','INTENTEXAMPLESNAME')

welcome_text = ['Hello, How can I help you?', 'Hi, Can I help you?', 'Hello, I am FAQ bot. How can I help you today?']
anything_else_text = ['I did not understand the question. Please try rephrasing', 'Can you reword the question? I do not get the meaning']

def create_standard_dialog_nodes(title, last_node = None):
    dialog_dict = {}
    dialog_dict["type"] = 'standard'
    dialog_dict["title"] = title
    dialog_dict["dialog_node"] = title
    dialog_dict["conditions"] = 'welcome' if title=='Welcome' else 'anything_else'
    if last_node:
        dialog_dict['previous_sibling'] = last_node
    dialog_text = welcome_text if title=='Welcome' else anything_else_text
    value_text = [{"text":t} for t in dialog_text]
    dialog_dict["output"] = {"generic":[{"values":value_text,"response_type":"text","selection_policy":"sequential"}]}
    return dialog_dict


'''
IF RESPONSE VARIATION IS TO BE CONSIDERED BY THE PROGRAM, THIS CODE COULD BE ADDED IN THE BELOW FUNCTION
            if cur_key==search_key and l['RESPONSES'] and k['RESPONSES'] and l['RESPONSES']!=k['RESPONSES']:
                response = l['RESPONSES']+"RESPONSE_VARIATION"+k['RESPONSES']
                del_indexes.append(k)
            if cur_key==search_key and l['RESPONSES']==k['RESPONSES']:
                del_indexes.append(k)
'''
        
def create_dialog_nodes(data_list, intent_list, entity_list):
    
    # CONSIDER ONLY THE COLUMNS REQUIRED
    data_list = [{k:v for k,v in d.items() if k in [intent_col_name,entity_col_name,entityvalues_col_name,responses_col_name]} for d in data_list]
    #REMOVE DUPLICATES
    data = [dict(t) for t in {tuple(d.items()) for d in data_list}]
    
    dialog_dict = {}
    node_no = 1
    dialog_list = []
    
    #CREATING WELCOME NODE AND ADDING TO LIST OF DIALOG NODES.
    dialog_list.append(create_standard_dialog_nodes('Welcome'))
    last_dialog_node = 'Welcome'
    update_dialog_dict = {}
    for intent in intent_list:
        # SETTING NODE NAME AS NODE_NO_RANDOMNUMBER
        node_prefix = "node_"+str(node_no)+"_"
        node_name = node_prefix+str(random.randrange(1000,10000000))
        dialog_list.append({"dialog_node":node_name, "type":"standard", "previous_sibling":last_dialog_node, "conditions":"#"+intent})
        last_dialog_node = node_name
        
        #GET ALL ROWS IN DATABASE WITH INTENT AS CURRENT INTENT
        data_for_intent = list(filter(lambda d: d[intent_col_name]==intent, data))
        entity_available = False
        last_child_dialog_node = ''
        first_entity_dialog_node = ''
        dialog_resp = data_for_intent[0][responses_col_name]            
        for row in data_for_intent:
            entity = row[entity_col_name] if row[entity_col_name] else ''
            entity = entity.replace(' ','')
            entityvalues = row[entityvalues_col_name] if row[entityvalues_col_name] else ''
            entityvalues = entityvalues.replace(' ','')
            entityvaluelist = [val.strip() for val in entityvalues.split(',')]
            if entity and entityvalues:
                entity_available = True
                condition = "@"+entity+":"+entityvaluelist[0]
                #CHILD NODES RELATED TO THE PARENT INTENT NODE
                node_name = node_prefix+str(random.randrange(1000,10000000))
                first_entity_dialog_node = node_name if first_entity_dialog_node=='' else first_entity_dialog_node
                dialog_dict = {"dialog_node":node_name, "type":"standard", "parent":last_dialog_node, "conditions":condition, "output":{"generic":[{"values":[{"text":row[responses_col_name]}],"response_type":"text","selection_policy":"sequential"}]}}
                if last_child_dialog_node:
                    dialog_dict["previous_sibling"] = last_child_dialog_node
                last_child_dialog_node = node_name
                dialog_list.append(dialog_dict)
            else:
                dialog_resp = row[responses_col_name]
                
        #ADD DIALOG FOR THE LAST INTENT
        if entity_available:
            update_dialog_dict[last_dialog_node] = {"dialog_node":last_dialog_node, "new_next_step":{"behavior":"jump_to","selector":"condition","dialog_node":first_entity_dialog_node}}
            dialog_list.append({"dialog_node":node_prefix+str(random.randrange(1000,10000000)), "parent":last_dialog_node, "type":"standard", "previous_sibling":last_child_dialog_node, "conditions":"#"+intent, "output":{"generic":[{"values":[{"text":dialog_resp}],"response_type":"text","selection_policy":"sequential"}]}})
        else:
            update_dialog_dict[last_dialog_node] = {"dialog_node":last_dialog_node, "new_output":{"generic":[{"values":[{"text":row[responses_col_name]}],"response_type":"text","selection_policy":"sequential"}]}}
            
        node_no = node_no+1
    dialog_list.append(create_standard_dialog_nodes('Anything Else',last_dialog_node))
    return dialog_list, update_dialog_dict
    