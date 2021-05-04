'''
Created on Feb 22, 2021

@author: toannguyen
'''
import config

class DbSetting():
    def __init__(self):
        if config.IS_PRODUCT:
            self.db_name        = 'timesheet'
        else:
            self.db_name        = 'timesheet_dev'
        self.db_host        = '192.168.2.59'
        self.db_user        = 'timesheet'
        self.db_port        = 3306
        self.db_password    = 'svi4ams!'
