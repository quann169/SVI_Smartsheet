'''
Created on Mar 1, 2021

@author: toannguyen
'''
from src.models.database.DatabaseModel import Task as DbTask
from src.models.database.DatabaseModel import FinalTask as DbFinalTask
from src.models.database.DatabaseModel import Configuration
from src.commons.Enums import DbHeader
from src.commons.Utils import get_week_number, convert_date_to_string

from pprint import pprint

class Timesheet():
    def __init__(self, from_date, to_date, filter, sheet_ids):
        self.sheets     = {}
        self.resource   = {}
        self.from_date  = from_date
        self.to_date    = to_date
        self.filter     = filter
        self.sheet_ids  = sheet_ids
        self.time_off   = {}
        self.user_ids    = {}
        self.team_ids   = {}
        self.eng_type_ids = {}
        
    def parse(self):
        config_obj  = Configuration()
        config_obj.get_all_user_information()
        self.user_ids    = config_obj.user_ids
        config_obj.get_list_timeoff(is_parse=True, start_date=self.from_date, end_date=self.to_date)
        self.time_off    = config_obj.time_off
        config_obj.get_sheet_config(is_parse=True)
        sheet_ids       = config_obj.sheet_ids
        config_obj.get_team_info(is_parse=True)
        self.team_ids       = config_obj.team_ids
        config_obj.get_eng_type_info(is_parse=True)
        self.eng_type_ids     = config_obj.eng_type_ids
        
        for sheet_id  in self.sheet_ids:
            sheet_id    = int(sheet_id)
            sheet_name      = sheet_ids[sheet_id][DbHeader.SHEET_NAME]
            sheet_type      = sheet_ids[sheet_id][DbHeader.SHEET_TYPE]
            sheet_obj   = Sheet(self, sheet_id, sheet_name, sheet_type)
            self.sheets[sheet_id] = sheet_obj
        
class Sheet():
    def __init__(self, timesheet_obj, sheet_id, sheet_name, sheet_type):
        self.timesheet_obj  = timesheet_obj
        self.sheet_id       = sheet_id
        self.sheet_name     = sheet_name
        self.sheet_type     = sheet_type
        self.resource       = {}
        self.parse()
        
    def parse(self):
        
        if self.timesheet_obj.filter == 'current':
            db_task_obj  = DbTask()
            db_task_obj.set_attr(sheet_id        = self.sheet_id,
                                start_date      = self.timesheet_obj.from_date,
                                end_date        = self.timesheet_obj.to_date
                )
            tasks       = db_task_obj.get_tasks()
            for row in tasks:
                task_obj    = Task(self, row)
                if self.resource.get(task_obj.user_id):
                    self.resource[task_obj.user_id].append(task_obj)
                else:
                    self.resource[task_obj.user_id] = []
                    self.resource[task_obj.user_id].append(task_obj)
        
    
     
class Task():
    def __init__(self, sheet_obj,  info={}):
        
        self.task_id  = None
        self.user_id  = None
        self.sibling_id  = None
        self.parent_id  = None
        self.self_id  = None
        self.task_name  = None
        self.date  = None
        self.allocation  = None
        self.is_children  = None
        self.start_date  = None
        self.end_date  = None
        self.duration  = None
        self.complete  = None
        self.predecessors  = None
        self.comment  = None
        self.actual_end_date   = None
        self.status  = None
        self.user_name      = None
        self.week_number    = None
        self.sheet_obj      = sheet_obj
        
        if info:
            self.task_id        = info[DbHeader.TASK_ID]
            self.user_id        = info[DbHeader.USER_ID]
            self.sibling_id     = info[DbHeader.SIBLING_ID]
            self.parent_id      = info[DbHeader.PARENT_ID]
            self.self_id        = info[DbHeader.SELF_ID]
            self.task_name      = info[DbHeader.TASK_NAME]
            self.date           = convert_date_to_string(info[DbHeader.DATE], '%Y-%m-%d')
            self.allocation     = info[DbHeader.ALLOCATION]
            self.is_children    = info[DbHeader.IS_CHILDREN]
            self.start_date     = convert_date_to_string(info[DbHeader.START_DATE], '%Y-%m-%d')
            self.end_date       = convert_date_to_string(info[DbHeader.END_DATE], '%Y-%m-%d')
            self.duration       = info[DbHeader.DURATION]
            self.complete       = info[DbHeader.COMPLETE]
            self.predecessors   = info[DbHeader.PREDECESSORS]
            self.comment        = info[DbHeader.COMMENT]
            self.actual_end_date   = info[DbHeader.ACTUAL_END_DATE]
            self.status         = info[DbHeader.STATUS]
            self.user_name      = self.sheet_obj.timesheet_obj.user_ids[self.user_id].user_name
            self.week_number    = get_week_number(self.date)

         
    
    
    



