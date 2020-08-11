# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 10:04:25 2020

@author: PranabGhosh
"""

import configparser
import os

config_file_loc = os.path.join(os.path.dirname(__file__),"ConfigParams.ini")
config = configparser.ConfigParser()
config.read(config_file_loc)
def get_param(section_name, param_name):
    try:
        return config[section_name][param_name]
    except:
        return ''
