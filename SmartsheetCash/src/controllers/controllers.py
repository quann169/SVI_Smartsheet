'''
Created on Feb 22, 2021

@author: toannguyen
'''
from src.models.smartsheet.smartsheet_model import SmartSheets
from src.commons import enums, message, utils
from flask import g, session
from pprint import pprint
import pandas as pd

import os, sys, getpass
import config
import time

class Controllers:
    def __init__(self):
        if session.get(enums.SessionKey.USERNAME):
            self.user_name = session[enums.SessionKey.USERNAME].strip()
        else:
            self.user_name = getpass.getuser()
        self.all_settings = {}
        
    def authenticate_account(self, user_name, password, remember=0):
        self.get_setting()
        allow_users = self.all_settings['allow_users']
        if user_name in  allow_users:
            result = utils.check_domain_password(user_name, password)
            if result[0]:
                session[enums.SessionKey.USERNAME] = user_name
                session[enums.SessionKey.PASSWORD] = password
                session[enums.SessionKey.IS_LOGIN] = True
                if remember:
                    utils.save_password(password)
            else:
                session[enums.SessionKey.IS_LOGIN] = False
        else:
            result = (False, message.MsgError.E005)
        print (result)
        return result
    
    def read_setting_file(self):
        setting_file = os.path.join(config.WORKING_PATH, 'config.py')
        self.all_settings= utils.read_template(setting_file, {})
    
    def get_setting(self):
        if not self.all_settings:
            self.read_setting_file()
        return None
    
    def start_analyze(self):
        pass
    
        