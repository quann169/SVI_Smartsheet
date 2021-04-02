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
from src.commons.utils import get_prev_date_by_time_delta, stuck, convert_date_to_string, println,\
                             get_work_days, str_to_date, compare_date,  write_message_into_file, \
                             is_caculate_sheet

from src.commons.enums import SmartsheetCfgKeys, SettingKeys, DbHeader
import copy

class SmartSheets:
    def __init__(self, list_sheet=None, holidays=[], time_off={}, timedelta=2, from_date=None, to_date=None, log=None, token=None):
        self.connection = None
        self.available_name = {}
        self.list_sheet = list_sheet
        self.holidays = holidays
        self.time_off = time_off
        self.info   = {}
        self.log   = log
        self.token   = token
        if from_date:
            self.timedelta  = str_to_date(from_date)[0]
        else:
            self.timedelta  = get_prev_date_by_time_delta(timedelta)
            
    def set_attr(self, **kwargs):                      
        for key, value in kwargs.items():
            setattr(self, key, value)
            
    def connect_smartsheet(self):
        if self.log:
            write_message_into_file(self.log, 'Connecting to smartsheet\n')
        println('Connecting to smartsheet', 'info')
        self.connection = Smartsheet(self.token)
        self.get_available_sheet_name()
        if self.log:
            write_message_into_file(self.log, 'Connect to smartsheet - Done\n')
        println('Connect to smartsheet - Done', 'info')
        
    def get_available_sheet_name(self):
        sheets = self.connection.sheets.list()
        for sheet in sheets:
            self.available_name[sheet.name] = sheet.id
            
            
    def get_sheet_name_and_validate_column(self, sheet_in_db={}):
        self.get_available_sheet_name()
        sms = smartsheet.Smartsheet(self.token)
        result = {}
        total_sheet = len(self.available_name)
        count = 0
        for sheet_name in self.available_name:
            count += 1
            if count > 60:
                break
            is_skip = 'Skip'
            if is_caculate_sheet(sheet_name):
                sheet_id = self.available_name[sheet_name]
                require_col = copy.deepcopy(SmartsheetCfgKeys.LIST_HEADER) 
                # Get all columns.
                response = sms.Sheets.get_columns(sheet_id, include_all=False)
                columns = response.data
                is_valid = 0
                if len(columns) >= len(require_col):
                    for col in columns:
                        col_name = col.title
                        try:
                            require_col.remove(col_name)
                        except ValueError:
                            pass
                    if not len(require_col):
                        is_valid = 1
                is_skip = ''
                sheet_type = SettingKeys.NA_VALUE
                is_active = 0
                if sheet_in_db.get(sheet_name):
                    sheet_type = sheet_in_db[sheet_name][DbHeader.SHEET_TYPE]
                    is_active = sheet_in_db[sheet_name][DbHeader.IS_ACTIVE]
                result[sheet_name] = {'is_valid': is_valid, 'sheet_type': sheet_type, 'is_active': is_active, 'missing_cols': require_col}
            println('Caculate [%d/%d] %s sheet: %s'%(count, total_sheet, is_skip, sheet_name), 'info')
        return result
        
    def parse(self):
        
        if self.list_sheet == None:
            pass
            # missing code
        else:
            list_sheet_name = []
            for sheet_name, latest_modified, sheet_id, parsed_date in self.list_sheet:
                if sheet_name in self.available_name:
                    list_sheet_name.append((sheet_name, latest_modified, sheet_id, parsed_date))
                else:
                    if self.log:
                        write_message_into_file(self.log, 'No sheet name %s\n'%sheet_name)
                    stuck('No sheet name %s'%sheet_name)
            total = len(list_sheet_name)
            count = 0
            for sheet_name, latest_modified, sheet_id, parsed_date in list_sheet_name:
                count += 1
                info = Sheet(self, sheet_name, latest_modified, sheet_id, parsed_date, count, total)
                info.parse_sheet()
                self.info[sheet_name] = info 
        
    
class Sheet():
    def __init__(self, smartsheet_obj, sheet_name, latest_modified, sheet_id, parsed_date, count, total):
        self.children_task  = []
        self.parent_task    = []
        self.name           = sheet_name
        self.sheet_id       = sheet_id
        self.parsed_date       = parsed_date
        self.header_index    = {}
        self.info           = []
        self.smartsheet_obj = smartsheet_obj
        self.list_parent_id = set()
        self.latest_modified  = convert_date_to_string(latest_modified)
        self.is_parse       = True
        self.timedelta      = smartsheet_obj.timedelta
        self.log         = smartsheet_obj.log
        self.count         = count
        self.total         = total
        self.holidays      = smartsheet_obj.holidays
        
    def parse_sheet(self):
        sheet           = self.smartsheet_obj.connection.sheets.get(self.name)
        cols            = sheet.columns
        
        is_go = compare_date(self.timedelta, self.parsed_date)
        
        modified_at = convert_date_to_string(sheet.modified_at)
        if self.latest_modified == modified_at and is_go:
            println('[%d/%d] Skip parsing sheet: %s'%(self.count, self.total, self.name), 'info')
            if self.log:
                write_message_into_file(self.log, '[%d/%d] Skip parsing sheet: %s\n'%(self.count, self.total, self.name))
            self.is_parse       = False
        else:
            if self.log:
                write_message_into_file(self.log, '[%d/%d] Parsing sheet: %s\n'%(self.count, self.total, self.name))
            println('[%d/%d] Parsing sheet: %s'%(self.count, self.total, self.name), 'info')
            self.latest_modified    = modified_at
            count = 0
            for col  in cols:
                header_name = col.title
                if header_name in SmartsheetCfgKeys.LIST_HEADER:
                    self.header_index[header_name] = count
                count += 1
            rows = sheet.rows
            for row in rows[::-1]:
                task_obj = Task(self, self.header_index, row, self.name, self.holidays)
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
    def __init__(self, sheet_obj, header_index, row, sheet_name, holidays):
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
        self.allocation         = 100
        self.sheet_obj          = sheet_obj
        self.list_date          = []
        self.holidays           = holidays
        
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
            if header in [SmartsheetCfgKeys.ACTUAL_END_DATE]:
                if value != None:
                    self.actual_end_date = value
            elif header in [SmartsheetCfgKeys.TASK_NAME]:
                if display_value != None:
                    self.task_name = display_value
                    
            elif header in [SmartsheetCfgKeys.ASSIGN_TO]:
                if display_value:
                    self.assign_to = display_value.strip()
            elif header in [SmartsheetCfgKeys.START_DATE]:
                self.start_date = value
            elif header in [SmartsheetCfgKeys.END_DATE]:
                self.end_date = value
            elif header in [SmartsheetCfgKeys.DURATION]:
                self.duration = display_value
            elif header in [SmartsheetCfgKeys.PREDECESSOR]:
                if value != None and value != '#REF':
                    try:
                        self.predecessors = int(value)
                    except ValueError:
                        pass
            elif header in [SmartsheetCfgKeys.COMMENT]:
                if value != None:
                    self.comments = value
            elif header in [SmartsheetCfgKeys.STATUS]:
                if value != None:
                    self.status = value
            elif header in [SmartsheetCfgKeys.COMPLETE]:
                if value != None:
                    try:
                        self.complete = float(value) * 100
                    except:
                        self.complete = 0
            elif header in [SmartsheetCfgKeys.ALLOCATION]:
                if value == None:
                    self.allocation = 100
                else:
                    try:
                        self.allocation = float(value) * 100
                    except ValueError:
                        pass
        if self.start_date != None and self.end_date != None and self.assign_to != None:
            self.start_date = self.start_date.replace(minute=0, hour=0, second=0, microsecond=0)
            self.end_date   = self.end_date.replace(minute=0, hour=0, second=0, microsecond=0)
            if self.end_date >= self.timedelta:
                self.list_date = get_work_days(self.start_date, self.end_date, time_delta=self.timedelta, holidays=self.holidays)
            
            
                