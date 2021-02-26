'''
Created on Feb 5, 2021

@author: toannguyen
'''
import sys, re, os
from decimal import Decimal
from pprint import pprint
import smartsheet
from simple_smartsheet import Smartsheet
import datetime
import time, stat
from pprint import pprint
import xlwt
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
from config import TOKEN

from src.commons.Utils import get_prev_date_by_time_delta, stuck, convert_date_to_string, println, get_work_days

from src.commons import Enums


class SmartSheets:
    def __init__(self, list_sheet=None, holiday=[], time_off={}, timedelta=1):
        self.connection = None
        self.available_name = []
        self.list_sheet = list_sheet
        self.holiday = holiday
        self.time_off = time_off
        self.info   = {}
        self.timedelta  = get_prev_date_by_time_delta(timedelta)
        
    def set_attr(self, **kwargs):                      
        for key, value in kwargs.items():
            setattr(self, key, value)
            
    def connect_smartsheet(self):
        self.connection = Smartsheet(TOKEN)
        self.get_available_sheet_name()
        
    def get_available_sheet_name(self):
        sheets = self.connection.sheets.list()
        for sheet in sheets:
            self.available_name.append(sheet.name)
    
    def parse(self):
        if self.list_sheet == None:
            pass
            # missing code
        else:
            list_sheet_name = []
            for sheet_name, latest_modified, sheet_id in self.list_sheet:
                if sheet_name in self.available_name:
                    list_sheet_name.append((sheet_name, latest_modified, sheet_id))
                else:
                    stuck('No sheet name %s'%sheet_name)
            for sheet_name, latest_modified, sheet_id in list_sheet_name:
                info = Sheet(self, sheet_name, latest_modified, sheet_id)
                info.parse_sheet()
                self.info[sheet_name] = info 
        
    
class Sheet():
    def __init__(self, smartsheet_obj, sheet_name, latest_modified, sheet_id):
        self.children_task  = []
        self.parent_task    = []
        self.name           = sheet_name
        self.sheet_id       = sheet_id
        self.header_index    = {}
        self.info           = []
        self.smartsheet_obj = smartsheet_obj
        self.list_parent_id = set()
        self.latest_modified  = convert_date_to_string(latest_modified)
        self.is_parse       = True
        self.timedelta      = smartsheet_obj.timedelta
        
    def parse_sheet(self):
        sheet           = self.smartsheet_obj.connection.sheets.get(self.name)
        cols            = sheet.columns
        
        modified_at = convert_date_to_string(sheet.modified_at)
        if self.latest_modified == modified_at:
            println('Skip parsing sheet: %s'%(self.name), 'info')
            self.is_parse       = False
        else:
            println('Parsing sheet: %s'%(self.name), 'info')
            self.latest_modified    = modified_at
            count = 0
            for col  in cols:
                header_name = col.title
                if header_name in Enums.SmartsheetCfgKeys.LIST_HEADER:
                    self.header_index[header_name] = count
                count += 1
            rows = sheet.rows
            for row in rows[::-1]:
                task_obj = Task(self, self.header_index, row, self.name)
                task_obj.parse_task()
                if task_obj.task_name != None:
                    self.info.append(task_obj)
                    if task_obj.self_id not in self.list_parent_id :
                        if len (task_obj.list_date):
                            self.children_task.append(task_obj)
                            
                    self.list_parent_id.add(task_obj.parent_id)
            self.children_task  = self.children_task[::-1]
            self.parent_task    = self.parent_task[::-1]
        
        
class Task():
    def __init__(self, sheet_obj, header_index, row, sheet_name):
        self.header_index       = header_index
        self.row                = row
        self.self_id            = 0
        self.sibling_id         = 0
        self.parent_id          = 0
        self.task_name          = None
        self.assign_to          = None
        self.start_date         = None
        self.end_date           = None
        self.complete           = 0
        self.duration           = ''
        self.predecessors       = 0
        self.comments           = ''
        self.actual_end_date    = None
        self.status             = ''
        self.allocation         = None
        self.sheet_obj          = sheet_obj
        self.list_date          = []
        
        if row.id != None:
            self.self_id            = row.id
        if row.sibling_id != None:
            self.sibling_id         = row.sibling_id
        if row.parent_id != None:
            self.parent_id          = row.parent_id
        
        self.timedelta      = sheet_obj.timedelta
        
    def parse_task(self):
        cells = self.row.cells
        for header in self.header_index:
            index = self.header_index[header]
            display_value = cells[index].display_value
            value = cells[index].value
            if header in [Enums.SmartsheetCfgKeys.ACTUAL_END_DATE]:
                if value != None:
                    self.actual_end_date = value
            elif header in [Enums.SmartsheetCfgKeys.TASK_NAME]:
                if display_value != None:
                    self.task_name = display_value
                    
            elif header in [Enums.SmartsheetCfgKeys.ASSIGN_TO]:
                self.assign_to = display_value
            elif header in [Enums.SmartsheetCfgKeys.START_DATE]:
                self.start_date = value
            elif header in [Enums.SmartsheetCfgKeys.END_DATE]:
                self.end_date = value
            elif header in [Enums.SmartsheetCfgKeys.DURATION]:
                self.duration = display_value
            elif header in [Enums.SmartsheetCfgKeys.PREDECESSOR]:
                if value != None:
                    self.predecessors = int(value)
            elif header in [Enums.SmartsheetCfgKeys.COMMENT]:
                if value != None:
                    self.comments = value
            elif header in [Enums.SmartsheetCfgKeys.STATUS]:
                if value != None:
                    self.status = value
            elif header in [Enums.SmartsheetCfgKeys.COMPLETE]:
                if value != None:
                    self.complete = int(value) * 100
            elif header in [Enums.SmartsheetCfgKeys.ALLOCATION]:
                if value == None:
                    self.allocation = 100
                else:
                    self.allocation = int(value) * 100
                    
        if self.start_date != None and self.end_date != None and self.assign_to != None:
            self.start_date = self.start_date.replace(minute=0, hour=0, second=0, microsecond=0)
            self.end_date   = self.end_date.replace(minute=0, hour=0, second=0, microsecond=0)
            if self.end_date >= self.timedelta:
                self.list_date = get_work_days(self.start_date, self.end_date, time_delta=self.timedelta)
            
            
                