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
import xlwt
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
from src.commons.utils import get_prev_date_by_time_delta, stuck, convert_date_to_string, println,\
                             get_work_days, str_to_date, compare_date,  write_message_into_file, \
                             is_caculate_sheet, get_value_by_pattern

from src.commons.enums import SmartsheetCfgKeys, SettingKeys, DbHeader, OtherKeys
import copy

class SmartSheetsEffective:
    def __init__(self, list_sheet=None, log=None, token=None):
        self.connection = None
        self.available_name = {}
        self.list_sheet = list_sheet
        self.info   = {}
        self.log   = log
        self.token   = token
            
    def set_attr(self, **kwargs):                      
        for key, value in kwargs.items():
            setattr(self, key, value)
            
    def connect_smartsheet(self):
        if self.log:
            write_message_into_file(self.log, 'Connecting to smartsheet\n')
        println('Connecting to smartsheet', OtherKeys.LOGING_INFO)
        self.connection = Smartsheet(self.token)
        self.get_available_sheet_name()
        if self.log:
            write_message_into_file(self.log, 'Connect to smartsheet - Done\n')
        println('Connect to smartsheet - Done', OtherKeys.LOGING_INFO)
        
    def get_available_sheet_name(self):
        sheets = self.connection.sheets.list()
        for sheet in sheets:
            if is_caculate_sheet(sheet.name):
                self.available_name[sheet.name] = sheet.id
            
            
    def get_validate_sheet_columns(self):
        self.get_available_sheet_name()
        result = []
        sms_obj = self.connection
        count = 0
        total = len(self.list_sheet)
        for sheet_name, sheet_id in self.list_sheet:
            # count += 1
            # message = 'Validate columns [%s/%s] sheets'%(count, total)
            # println(message, OtherKeys.LOGING_INFO)
            # if self.log:
            #     write_message_into_file(self.log, '%s\n'%message)
            # if sheet_name not in self.available_name:
            #     continue
            # require_col = copy.deepcopy(SmartsheetCfgKeys.LIST_HEADER_EFFECTIVE) 
            # # Get all columns.
            # columns = sms_obj.sheets.get(sheet_name).columns
            # is_valid = 0
            # require_col.remove(SmartsheetCfgKeys.ACTUAL_DURATION) 
            # if len(columns) >= len(require_col):
            #     for col in columns:
            #         col_name = col.title
            #         try:
            #             require_col.remove(col_name)
            #         except ValueError:
            #             pass
            #     if not len(require_col):
            #         is_valid = 1
            is_valid = 1
            if is_valid:
                result.append([sheet_name, sheet_id])
        return result
        
    def parse(self):
        sheet_enough_cols = self.get_validate_sheet_columns()
        if not sheet_enough_cols:
            message = 'No available sheet'
            println(message, OtherKeys.LOGING_WARNING)
            if self.log:
                write_message_into_file(self.log, '%s\n'%message)
        else:
            total = len(sheet_enough_cols)
            count = 0
            for sheet_name, sheet_id in sheet_enough_cols:
                count += 1
                info = SheetEffective(self, sheet_name, sheet_id, count, total)
                info.parse_sheet()
                self.info[sheet_name] = info     
    
class SheetEffective():
    def __init__(self, smartsheet_obj, sheet_name, sheet_id, count, total):
        self.children_task  = []
        self.parent_task    = []
        self.name           = sheet_name
        self.sheet_id       = sheet_id
        self.header_index    = {}
        self.info           = []
        self.smartsheet_obj = smartsheet_obj
        self.list_parent_id = set()
        self.is_parse       = True
        self.log         = smartsheet_obj.log
        self.count         = count
        self.total         = total
        
    def parse_sheet(self):
        sheet           = self.smartsheet_obj.connection.sheets.get(self.name)
        cols            = sheet.columns
        if self.log:
            write_message_into_file(self.log, '[%d/%d] Parsing sheet: <span class="cl-blue bold">%s</span>\n'%(self.count, self.total, self.name))
        println('[%d/%d] Parsing sheet: %s'%(self.count, self.total, self.name), OtherKeys.LOGING_INFO)

        count = 0
        for col  in cols:
            header_name = col.title
            if header_name in SmartsheetCfgKeys.LIST_HEADER_EFFECTIVE:
                self.header_index[header_name] = count
            count += 1
        rows = sheet.rows
        count = 0
        total = len(rows)
        for row in rows[::-1]:
            count += 1
            if count % 100 == 0 or count == total:
                message = '[%d/%d] Processing [%s/%s] rows'%(self.count, self.total, count, total)
                println(message, OtherKeys.LOGING_WARNING)
                if self.log:
                    write_message_into_file(self.log, '%s\n'%message)
                    
            task_obj = TaskEffective(self, self.header_index, row, self.name)
            task_obj.parse_task()
            if task_obj.task_name != '' and task_obj.assign_to != '':
                self.info.append(task_obj)
                if task_obj.self_id not in self.list_parent_id :
                    self.children_task.append(task_obj)
                self.list_parent_id.add(task_obj.parent_id)
        self.children_task  = self.children_task[::-1]
        self.parent_task    = self.parent_task[::-1]
        
        
class TaskEffective():
    def __init__(self, sheet_obj, header_index, row, sheet_name):
        self.header_index       = header_index
        self.row                = row
        self.self_id            = 0
        self.sibling_id         = 0
        self.parent_id          = 0
        self.task_name          = ''
        self.assign_to          = ''
        self.start_date         = '0000-00-00 00:00:00'
        self.end_date           = '0000-00-00 00:00:00'
        self.actual_end_date    = '0000-00-00 00:00:00'
        self.actual_start_date  = '0000-00-00 00:00:00'
        self.actual_duration    = ''
        self.duration           = ''
        self.prefix_name        = ''
        self.sheet_obj          = sheet_obj
        
        if row.id != None:
            self.self_id            = row.id
        if row.sibling_id != None:
            self.sibling_id         = row.sibling_id
        if row.parent_id != None:
            self.parent_id          = row.parent_id
        
        
    def parse_task(self):
        cells = self.row.cells
        for header in self.header_index:
            index = self.header_index[header]
            display_value = cells[index].display_value
            value = cells[index].value
            if isinstance(value, datetime.datetime):
                value = value.replace(minute=0, hour=0, second=0)
            #if header in [SmartsheetCfgKeys.ACTUAL_START_DATE]:
            #    if value != None:
            #        self.actual_start_date = value
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
                if value != None:
                    self.start_date = value
            elif header in [SmartsheetCfgKeys.END_DATE]:
                if value != None:
                    self.end_date = value
            elif header in [SmartsheetCfgKeys.ACTUAL_DURATION]:
                if display_value != None:
                    self.actual_duration = get_value_by_pattern(display_value, '([0-9 .]*)+?')[0]
            elif header in [SmartsheetCfgKeys.DURATION]:
                if display_value != None:
                    self.duration = get_value_by_pattern(display_value, '([0-9 .]*)+?')[0]
            elif header in [SmartsheetCfgKeys.PREFIX_NAME]:
                self.prefix_name = value
                