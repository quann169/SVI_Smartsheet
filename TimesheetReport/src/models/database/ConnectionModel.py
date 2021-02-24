'''
Created on Feb 17, 2021

@author: toannguyen
'''

import pymysql
from pymysql.constants import CLIENT
from src.commons import Enums, Utils, Message
import logging
from pprint import pprint
from flask import g
import os
from src.commons.Utils import CommonUtils
import re
from src.models.database.DbSettings import DbSettings
import config

class Connection:
    def __init__(self, db_setting = None):
        self.db_name        = ''
        self.db_host        = ''
        self.db_user        = ''
        self.db_port        = 0
        self.db_password    = ''
        self.db_char_set    = Enums.Connect.CHAR_SET
        self.cusror_type    = pymysql.cursors.DictCursor
        self.db_setting     = db_setting
        self.get_database_setting()
    
    def set_attr(self, **kwargs):                      
        for key, value in kwargs.items():
            setattr(self, key, value)
               
    def get_database_setting(self):

        db_setting                              =  DbSettings()
        self.db_host                            = db_setting.db_host
        self.db_port                            = db_setting.db_port
        self.db_user                            = db_setting.db_user
        self.db_password                        = db_setting.db_password
        self.db_name                            = db_setting.db_name

                    
    
    def create_connection(self):
        """ create a database connection to the MYSQL database
        specified by db_file
        :param : None
        :return: Connection object or None
        """
        connection = None
        try:
            connection = pymysql.connect(host = self.db_host,
                            port         = self.db_port,
                            user         = self.db_user,
                            password     = self.db_password,
                            db           = self.db_name,
                            charset      = self.db_char_set,
                            cursorclass  = self.cusror_type,
                            client_flag  = CLIENT.MULTI_STATEMENTS
                            )
        
            return connection
        except Exception as e:
            logging.exception(e)
            print(e)
            
            
        return connection
        
    
    
    def db_execute(self, query):
        """ Execute MySQL query for insert/update/delete database
        :param : query - text
        :return: None
        """
        try:
            connection          = self.create_connection()
            cursor              = connection.cursor()
            cursor.execute(query)
            connection.commit()
            logging.debug(query)
        except Exception as e:
            logging.exception(query)
            logging.exception(e)
            raise Exception(e)
        finally:
            connection.close()
    
    def db_execute_2(self, query):
        """ Execute MySQL query for insert
        :param : query - text
        :return: insert_id
        """
        try:
            connection          = self.create_connection()
            cursor              = connection.cursor()
            cursor.execute(query)
            connection.commit()
            logging.debug(query)
            return cursor.lastrowid
        except Exception as e:
            logging.exception(query)
            logging.exception(e)
            raise Exception(e)
        finally:
            connection.close()
      
    def db_execute_many(self, query, list_record):
        """ Execute multiple the same query query
        :param : query - text
        :return: None
        """
        try:
            connection          = self.create_connection()
            cursor              = connection.cursor()
            cursor.executemany(query, list_record)
            connection.commit()
            logging.debug(query)
        except Exception as e:
            logging.exception(query)
            logging.exception(e)
            raise Exception(e)
        finally:
            connection.close()
            
    def db_query(self, query):
        """ Execute MySQL query for select database
        :param : query - text 
        :return: all rows
        """
        try:
            connection          = self.create_connection()
            cursor              = connection.cursor()
            cursor.execute(query)
            rows                = cursor.fetchall()
            logging.debug(query)
            if rows:
                return rows
            else:
                return None
        except Exception as e:
            logging.exception(query)
            logging.exception(e)
            raise Exception(e)         
        finally:
            connection.close()
            
            
            