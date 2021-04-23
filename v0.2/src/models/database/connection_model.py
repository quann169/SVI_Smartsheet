'''
Created on Feb 17, 2021

@author: toannguyen
'''

import pymysql
from pymysql.constants import CLIENT
from src.commons.enums import Connect, OtherKeys
from src.commons.utils import println
from pprint import pprint
from flask import g
from dbutils.pooled_db import PooledDB
from src.models.database.db_setting import DbSetting
import sys

class Connection:
    def __init__(self, db_setting = None):
        self.db_name        = ''
        self.db_host        = ''
        self.db_user        = ''
        self.db_port        = 0
        self.db_password    = ''
        self.db_char_set    = Connect.CHAR_SET
        self.cusror_type    = pymysql.cursors.DictCursor
        self.db_setting     = db_setting
        self.get_database_setting()
    
    def set_attr(self, **kwargs):                      
        for key, value in kwargs.items():
            setattr(self, key, value)
               
    def get_database_setting(self):

        db_setting                              =  DbSetting()
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
            println(e, OtherKeys.LOGING_EXCEPTION)
        return connection
    
    def create_pool_connection (self, is_exit=False):
        """ create a pool connection to the MYSQL database
        specified by db_file
        :param : None
        :return: pool Connection object or None
        """
        
        pool_conn = None
        try:
            pool_conn = PooledDB(
                creator=pymysql,
                mincached=1,
                maxcached=20,
                maxconnections=20,
                maxshared=20,
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                db=self.db_name,
                charset=self.db_char_set,
                cursorclass=self.cusror_type,
                client_flag  = CLIENT.MULTI_STATEMENTS
            )
            return pool_conn
        except Exception as e:
            println('Can not connect to database', OtherKeys.LOGING_EXCEPTION)
            if is_exit:
                sys.exit()
            raise Exception('Can not connect to database')
        return pool_conn
        
    def check_connection(self):
        try:
            query   = """SHOW TABLES;"""
            query_result    = self.db_query(query)
            if query_result:
                return True
            else:
                return False
        except Exception as e:
            return False
        
    def db_execute(self, query, shareable=True):
        """ Execute MySQL query for insert/update/delete database
        :param : query - text
        :return: None
        """
        try:
            connection          = g.pool_conn.connection(shareable)
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
            println(query, OtherKeys.LOGING_DEBUG)
        except Exception as e:
            println(query, OtherKeys.LOGING_EXCEPTION, is_print=False)
            println(e, OtherKeys.LOGING_EXCEPTION, is_print=False)
            raise Exception(e)
        finally:
            connection.close()
    
    def db_execute_2(self, query, shareable=True):
        """ Execute MySQL query for insert
        :param : query - text
        :return: insert_id
        """
        try:
            connection          = g.pool_conn.connection(shareable)
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
            println(query, OtherKeys.LOGING_DEBUG)
            return cursor.lastrowid
        except Exception as e:
            println(query, OtherKeys.LOGING_EXCEPTION, is_print=False)
            println(e, OtherKeys.LOGING_EXCEPTION, is_print=False)
            raise Exception(e)
        finally:
            connection.close()
      
    def db_execute_many(self, query, list_record, shareable=True):
        """ Execute multiple the same query query
        :param : query - text
        :return: None
        """
        try:
            connection          = g.pool_conn.connection(shareable)
            with connection.cursor() as cursor:
                cursor.executemany(query, list_record)
                connection.commit()
            println(query, OtherKeys.LOGING_DEBUG)
        except Exception as e:
            println(query, OtherKeys.LOGING_EXCEPTION, is_print=False)
            println(e, OtherKeys.LOGING_EXCEPTION, is_print=False)
            raise Exception(e)
        finally:
            connection.close()
            
    def db_query(self, query, shareable=True):
        """ Execute MySQL query for select database
        :param : query - text 
        :return: all rows
        """
        try:
            connection          = g.pool_conn.connection(shareable)
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows                = cursor.fetchall()
            println(query, OtherKeys.LOGING_DEBUG)
            if rows:
                return rows
            else:
                return None
        except Exception as e:
            println(query, OtherKeys.LOGING_EXCEPTION, is_print=False)
            println(e, OtherKeys.LOGING_EXCEPTION, is_print=False)
            raise Exception(e)         
        finally:
            connection.close()
            
            
            