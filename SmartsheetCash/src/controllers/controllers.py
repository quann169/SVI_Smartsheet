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
    
    def authenticate_account(self, username, password, remember=0):
        result = utils.check_domain_password(username, password)
        if result[0]:
            session[enums.SessionKey.USERNAME] = username
            session[enums.SessionKey.PASSWORD] = password
            session[enums.SessionKey.IS_LOGIN] = True
            if remember:
                utils.save_password(password)
        else:
            session[enums.SessionKey.IS_LOGIN] = False
        return result
    
    def read_setting_file(self):
        
        pass