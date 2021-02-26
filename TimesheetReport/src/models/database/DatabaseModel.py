'''
Created on Feb 22, 2021

@author: toannguyen
'''
from src.models.database.ConnectionModel import Connection
from src.commons.Enums import DbHeader, DbTable
from pprint import pprint


class Configuration(Connection):
    def __init__(self):
        Connection.__init__(self)
        self.users              = {}
        self.users_full_name    = {}
        
    def get_sheet_config(self, list_sheet_id=None):
        condition = ''
        if list_sheet_id:
            condition   = 'WHERE `%s`.`%s` IN (%s)'%(DbTable.SHEET, DbHeader.SHEET_ID, ', '.join(list_sheet_id))
        query = """
                SELECT `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`
                FROM `%s`
                INNER JOIN `%s`
                ON `%s`.`%s`=`%s`.`%s`
                %s;
        """%(
            DbTable.SHEET, DbHeader.SHEET_ID, 
            DbTable.SHEET, DbHeader.SHEET_NAME, 
            DbTable.SHEET, DbHeader.LATEST_MODIFIED, 
            DbTable.SHEET_TYPE, DbHeader.SHEET_TYPE,
            DbTable.SHEET, DbHeader.UPDATED_BY,
            DbTable.SHEET, DbHeader.UPDATED_DATE,
            DbTable.SHEET, 
            DbTable.SHEET_TYPE, 
            DbTable.SHEET, DbHeader.SHEET_TYPE_ID, DbTable.SHEET_TYPE, DbHeader.SHEET_TYPE_ID,
            condition
            )
        query_result    = self.db_query(query)
        result          = ()
        if query_result:
            return query_result
        else:
            return result
    
    def update_latest_modified_of_sheet(self):
        query   = '''UPDATE 
                        `%s` 
                    SET 
                        `%s`="%s"
                    WHERE 
                        `%s`="%d";'''%(\
                    DbTable.SHEET,\
                    DbHeader.LATEST_MODIFIED, self.latest_modified, \
                    DbHeader.SHEET_ID, self.sheet_id)
        self.db_execute(query)
    
    def get_all_user_information(self):
        query   = """
                SELECT
                    `%s`,
                    `%s`,
                    `%s`,
                    `%s`,
                    `%s`,
                    `%s`,
                    `%s`,
                    `%s`,
                    `%s`,
                    `%s`,
                    `%s`
                FROM
                    `%s`; 
        """%(
            DbHeader.USER_ID,
            DbHeader.USER_NAME,
            DbHeader.FULL_NAME,
            DbHeader.EMAIL,
            DbHeader.OTHER_NAME,
            DbHeader.IS_ACTIVE,
            DbHeader.UPDATED_BY,
            DbHeader.UPDATED_DATE,
            DbHeader.ENG_LEVEL_ID,
            DbHeader.ENG_TYPE_ID,
            DbHeader.TEAM_ID,
            DbTable.USER,
            )
        query_result    = self.db_query(query)
        if query_result:
            for row in query_result:
                user_obj    = Users(row)
                self.users[user_obj.user_name] = user_obj
                self.users_full_name[user_obj.full_name] = user_obj
        else:
            pass
    
    def add_list_timeoff(self, list_record):
        query   = '''INSERT INTO `%s` 
                        (`%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`)
                    '''%(DbTable.TIME_OFF,\
                    DbHeader.TIME_OFF_ID, DbHeader.USER_ID, DbHeader.DEPARTMENT, DbHeader.TYPE, DbHeader.START_DATE, DbHeader.END_DATE, DbHeader.WORK_DAYS, DbHeader.STATUS, DbHeader.UPDATED_BY)
        query   += '''
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ;'''
        self.db_execute_many(query, list_record)
    
    def get_list_timeoff(self):
        query = """
                SELECT `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`,
                        `%s`.`%s`
                FROM `%s`
                INNER JOIN `%s`
                ON `%s`.`%s`=`%s`.`%s`;
        """%(
            DbTable.TIME_OFF, DbHeader.TIME_OFF_ID, 
            DbTable.USER, DbHeader.USER_NAME, 
            DbTable.TIME_OFF, DbHeader.DEPARTMENT, 
            DbTable.TIME_OFF, DbHeader.TYPE,
            DbTable.TIME_OFF, DbHeader.START_DATE,
            DbTable.TIME_OFF, DbHeader.END_DATE,
            DbTable.TIME_OFF, DbHeader.WORK_DAYS,
            DbTable.TIME_OFF, DbHeader.STATUS,
            DbTable.TIME_OFF, 
            DbTable.USER, 
            DbTable.TIME_OFF, DbHeader.USER_ID, DbTable.USER, DbHeader.USER_ID
            )
        query_result    = self.db_query(query)
        result          = ()
        if query_result:
            return query_result
        else:
            return result
        
        
        
        
    def remove_all_timeoff_information(self):
        query   = '''DELETE FROM `%s`;'''%(\
                    DbTable.TIME_OFF
                    )
        self.db_execute(query)

class Task(Connection):
    def __init__(self):
        Connection.__init__(self)
    
    def remove_all_task_information_by_project_id(self):
        query   = '''DELETE FROM
                        `%s`
                    WHERE
                        `%s`="%d";'''%(\
                    DbTable.TASK, \
                    DbHeader.SHEET_ID, self.sheet_id
                    )
        self.db_execute(query)
    
    def add_task(self, list_record):
        query   = '''INSERT INTO `%s` 
                        (`%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`, `%s`)
                    '''%(DbTable.TASK,\
                    DbHeader.SHEET_ID, DbHeader.USER_ID, DbHeader.SIBLING_ID, DbHeader.PARENT_ID, DbHeader.SELF_ID, DbHeader.TASK_NAME, DbHeader.DATE, DbHeader.START_DATE, DbHeader.END_DATE,\
                    DbHeader.DURATION, DbHeader.COMPLETE, DbHeader.PREDECESSORS, DbHeader.COMMENT, DbHeader.ACTUAL_END_DATE, DbHeader.STATUS, DbHeader.IS_CHILDREN, DbHeader.ALLOCATION)
        query   += '''
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ;'''

        self.db_execute_many(query, list_record)
    
    
    
class FinalTask(Connection):
    def __init__(self):
        Connection.__init__(self)
        
        
class Users(Connection):
    def __init__(self, info=None):
        Connection.__init__(self)
        self.user_id        = None
        self.user_name      = None
        self.full_name      = None
        self.email          = None
        self.other_name     = None
        self.is_active      = None
        self.updated_by     = None
        self.updated_date   = None
        self.eng_level_id   = None
        self.eng_type_id    = None
        self.team_id        = None
        
        if info:
            self.user_id        = int(info[DbHeader.USER_ID])
            self.user_name      = info[DbHeader.USER_NAME]
            self.full_name      = info[DbHeader.FULL_NAME]
            self.email          = info[DbHeader.EMAIL]
            self.other_name     = info[DbHeader.OTHER_NAME]
            self.is_active      = int(info[DbHeader.IS_ACTIVE])
            self.updated_by     = info[DbHeader.UPDATED_BY]
            self.updated_date   = info[DbHeader.UPDATED_DATE]
            self.eng_level_id   = int(info[DbHeader.ENG_LEVEL_ID])
            self.eng_type_id    = int(info[DbHeader.ENG_TYPE_ID])
            self.team_id        = int(info[DbHeader.TEAM_ID])
    
    