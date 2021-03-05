'''
Created on Feb 22, 2021

@author: toannguyen
'''
from src.models.smartsheet.SmartsheetModel import SmartSheets
from src.models.database.DatabaseModel import Configuration, Task
from src.commons.Enums import DbHeader, ExcelHeader, SettingKeys, DefaulteValue, SessionKey
from src.commons.Message import MsgError, MsgWarning, Msg
from src.commons.Utils import search_pattern, message_generate, println, remove_path, split_patern
from src.models.timesheet.TimesheetModel import Timesheet
from flask import session
from pprint import pprint
import pandas as pd
import os, sys
import config


class Controllers:
    def __init__(self):
        pass
    
    def parse_smarsheet_and_update_task(self, from_date=None, to_date=None, list_sheet_id=None):
        cfg_obj = Configuration()
        sheet_info  = cfg_obj.get_sheet_config(list_sheet_id)
        list_sheet  = []
        for row in sheet_info:
            list_sheet.append((row[DbHeader.SHEET_NAME], row[DbHeader.LATEST_MODIFIED], int(row[DbHeader.SHEET_ID])))

        sms_obj = SmartSheets(list_sheet = list_sheet, from_date = from_date, to_date = to_date)
        sms_obj.connect_smartsheet()
        sms_obj.parse()
        config_obj  = Configuration()
        config_obj.get_all_user_information()
        user_info = config_obj.users
        task_obj    = Task()
        for sheet_name in sms_obj.info:
            # save children_task only
            
            child_tasks         = sms_obj.info[sheet_name].children_task
            sheet_id            = sms_obj.info[sheet_name].sheet_id
            latest_modified     = sms_obj.info[sheet_name].latest_modified
            is_parse            = sms_obj.info[sheet_name].is_parse
            if is_parse:
                
                task_obj.set_attr(sheet_id    = sheet_id)
                task_obj.remove_all_task_information_by_project_id()
                list_records_task   = []
                for child_task_obj in child_tasks:
                    sibling_id      = child_task_obj.sibling_id
                    parent_id       = child_task_obj.parent_id
                    self_id         = child_task_obj.self_id
                    task_name       = child_task_obj.task_name
                    dates           = child_task_obj.list_date
                    start_date      = child_task_obj.start_date
                    end_date        = child_task_obj.end_date
                    duration        = child_task_obj.duration
                    complete        = child_task_obj.complete
                    predecessors    = child_task_obj.predecessors
                    comments        = child_task_obj.comments
                    actual_end_date = child_task_obj.actual_end_date
                    status          = child_task_obj.status
                    is_children     = 1
                    allocation      = child_task_obj.allocation
                    assign_to       = child_task_obj.assign_to
                    try:
                        user_id = user_info[assign_to].user_id
                    except KeyError:
                        user_id = user_info[SettingKeys.NA_VALUE].user_id
                    for date, week in dates:
                        record  = (
                            str(sheet_id),
                            str(user_id),
                            str(sibling_id),
                            str(parent_id),
                            str(self_id),
                            task_name,
                            date,
                            str(start_date),
                            str(end_date),
                            duration,
                            str(complete),
                            str(predecessors),
                            comments,
                            actual_end_date,
                            status,
                            str(is_children),
                            str(allocation)
                            )
                        list_records_task.append(record)
                task_obj.add_task(list_records_task)
                config_obj.set_attr(sheet_id            = sheet_id,
                                    latest_modified     = latest_modified)
                config_obj.update_latest_modified_of_sheet()
    
    def import_timeoff(self, file_name):
        try:
            file_path   = os.path.join(os.path.join(config.WORKING_PATH, 'upload'), file_name)
            df          = pd.read_excel (file_path, sheet_name='Time-Off', engine='openpyxl')
            
            config_obj  = Configuration()
            config_obj.get_all_user_information()
            users_info  = config_obj.users
            user_full_name_info = config_obj.users_full_name
            exist_id     = {}
            
            list_record = []
            for index in range(0, len(df[ExcelHeader.ID])):
                id_timeoff          = str(df[ExcelHeader.ID][index])
                try:
                    unuse = exist_id[id_timeoff]
                    message = message_generate(MsgWarning.W001, id_timeoff)
                    println(message, 'debug')
                    continue
                except KeyError:
                    exist_id[id_timeoff] = ''
                
                requester   = str(df[ExcelHeader.REQUESTER][index])
                department  = str(df[ExcelHeader.DEPARTMENT][index])
                type_leave  = str(df[ExcelHeader.TYPE][index])
                start_date  = str(df[ExcelHeader.START_DATE][index])
                end_date    = str(df[ExcelHeader.END_DATE][index])
                workday     = search_pattern(str(df[ExcelHeader.WORKDAYS][index]),'(.+?)\((.+?)h\)')[1]
                status      = str(df[ExcelHeader.STATUS][index])
                user_id     = users_info[SettingKeys.NA_VALUE].user_id
                updated_by = 'root'
                try:
                    user_id = users_info[requester].user_id
                except KeyError:
                    try:
                        user_id = user_full_name_info[requester].user_id
                    except KeyError:
                        pass

                list_record.append(
                    (
                        id_timeoff, 
                        user_id, 
                        department,
                        type_leave,
                        start_date,
                        end_date,
                        workday,
                        status,
                        updated_by
                        )
                    )
            config_obj.remove_all_timeoff_information()
            config_obj.add_list_timeoff(list_record)
            remove_path(file_path)
            return 1, Msg.M001
        except Exception as e:
            println(e, 'exception')
            return 0, e.args[0]
        
    def get_timeoff_info(self):
        config_obj  = Configuration()
        result      = config_obj.get_list_timeoff()
        return result
    
    def import_holiday(self, file_name):
        try:
            file_path   = os.path.join(os.path.join(config.WORKING_PATH, 'upload'), file_name)
            df          = pd.read_excel (file_path, sheet_name='Holiday', engine='openpyxl')
            config_obj  = Configuration()
            for index in range(0, len(df[ExcelHeader.HOLIDAY])):
                date          = str(df[ExcelHeader.HOLIDAY][index])
                if date not in SettingKeys.EMPTY_CELL:
                    if not config_obj.is_exist_holiday(date):
                        config_obj.add_holiday(date)
            return 1, Msg.M001
        except Exception as e:
            println(e, 'exception')
            return 0, e.args[0]
    
    def get_session(self, key=None):
        try:
            val   = session[key]
            
            return val
        except KeyError:
            return None
        
    def get_holiday_info(self):
        config_obj  = Configuration()
        result      = config_obj.get_list_holiday()
        return result   
    
    def get_sheet_config(self):
        config_obj  = Configuration()
        result      = config_obj.get_sheet_config()
        return result    
    
    def update_session(self, key, val):
        try:
            session.pop(key, None)
            session[key] = val
            
            return 1, ''
        except Exception as e:
            println(e, 'exception')
            return 0, e.args[0]
    
    def update_resource_of_sheet(self, info = {}):
        config_obj  = Configuration()
        
        config_obj.get_all_user_information()
        users    = config_obj.users
        
        config_obj.get_sheet_config(is_parse=True)
        sheets          = config_obj.sheets
        sheet_ids       = []
        list_record     = []
        
        for sheet_name in info:
            sheet_id = sheets[sheet_name][DbHeader.SHEET_ID]
            sheet_ids.append(sheet_id)
            for user_name in info[sheet_name]:
                user_name = user_name.strip()
                if users.get(user_name):
                    
                    user_id = users[user_name].user_id
                    list_record.append((sheet_id, user_id))
        if len(sheet_ids):
            config_obj.remove_all_user_of_sheet(sheet_ids)
            if len(list_record):
                config_obj.add_user_of_sheet(list_record)
    
#     def get_sheet_resource_info(self):
#         config_obj  = Configuration()
#         config_obj.get_sheet_user_info()
#         result      = config_obj.sheet_users
#         return result
        
        
        
        
        
    def import_sheet(self, file_name):
        try:
            file_path   = os.path.join(os.path.join(config.WORKING_PATH, 'upload'), file_name)
            df          = pd.read_excel (file_path, sheet_name='Sheet', engine='openpyxl')
            config_obj  = Configuration()
            config_obj.get_sheet_type_info(is_parse=True)
            sheet_type_info = config_obj.sheet_type
            
            sms_obj = SmartSheets()
            sms_obj.connect_smartsheet()
            available_sheet_name = sms_obj.available_name
            #validate sheet 
            for index in range(0, len(df[ExcelHeader.SHEET_NAME])):
                sheet_name          = str(df[ExcelHeader.SHEET_NAME][index])
                if sheet_name not in SettingKeys.EMPTY_CELL and sheet_name not in available_sheet_name:
                    message = message_generate(MsgError.E002, sheet_name)
                    println(message, 'error')
                    return  0, message
            config_obj.set_attr(updated_by  = 'root')
            user_of_sheet   = {}
            for index in range(0, len(df[ExcelHeader.SHEET_NAME])):
                sheet_name          = str(df[ExcelHeader.SHEET_NAME][index])
                sheet_type          = str(df[ExcelHeader.SHEET_TYPE][index])
                if sheet_name not in SettingKeys.EMPTY_CELL:
                    try:
                        sheet_type_id  = sheet_type_info[sheet_type]
                    except KeyError:
                        sheet_type_id  = sheet_type_info[SettingKeys.NA_VALUE]
                    try:
                        is_active       = float(str(df[ExcelHeader.IS_ACTIVE][index]))
                    except:
                        is_active       = 0
                    users               = split_patern(str(df[ExcelHeader.RESOURCE][index]), pattern=',|\;')
                    user_of_sheet[sheet_name] = users
                    config_obj.set_attr(sheet_name      = sheet_name,
                                        sheet_type_id   = str(sheet_type_id),
                                        latest_modified = DefaulteValue.DATETIME,
                                        is_active       = str(is_active))
                    
                    if config_obj.is_exist_sheet():
                        config_obj.update_sheet()
                    else:
                        config_obj.add_sheet()
            #update project-user table
            self.update_resource_of_sheet(user_of_sheet)
            
            return 1, Msg.M001
        except Exception as e:
            println(e, 'exception')
            return 0, e.args[0]         
    
    def get_resource_config(self):
        config_obj  = Configuration()
        result      = config_obj.get_list_resource()
        return result    
                
    def import_resource(self, file_name):
        try:
            file_path   = os.path.join(os.path.join(config.WORKING_PATH, 'upload'), file_name)
            df          = pd.read_excel (file_path, sheet_name='Staff', engine='openpyxl')
            config_obj  = Configuration()
            config_obj.get_eng_type_info(is_parse=True)
            eng_type_info = config_obj.eng_type

            
            
            config_obj.get_eng_level_info(is_parse=True)
            eng_level_info = config_obj.eng_level



            teams  = config_obj.get_team_info(is_parse=True)
            teams_info = config_obj.team

            
            config_obj.set_attr(updated_by  = 'root')
            for index in range(0, len(df[ExcelHeader.RESOURCE])):
                resource          = str(df[ExcelHeader.RESOURCE][index])
                eng_type          = str(df[ExcelHeader.ENG_TYPE][index])
                eng_level         = str(df[ExcelHeader.ENG_LEVEL][index])
                email             = str(df[ExcelHeader.EMAIL][index])
                full_name         = str(df[ExcelHeader.FULL_NAME][index])
                team              = str(df[ExcelHeader.TEAM][index])
                leader            = str(df[ExcelHeader.LEADER][index])
                is_active         = str(df[ExcelHeader.IS_ACTIVE][index])
                other_name        = str(df[ExcelHeader.OTHER_NAME][index])

                if resource not in SettingKeys.EMPTY_CELL:
                    try:
                        eng_type_id   = eng_type_info[eng_type]
                        
                    except KeyError:
                        eng_type_id  = eng_type_info[SettingKeys.NA_VALUE]
                    try:
                        eng_level_id  = eng_level_info[eng_level]
                    except KeyError:
                        eng_level_id  = eng_level_info[SettingKeys.NA_VALUE]
                    try:
                        team_id     = teams_info[team]
                    except KeyError:
                        team_id     = teams_info[SettingKeys.NA_VALUE]
                        
                    if other_name in SettingKeys.EMPTY_CELL:
                        other_name  = ''
                    
                    config_obj.set_attr(user_name      = resource,
                                        eng_type_id   = str(eng_type_id),
                                        eng_level_id   = str(eng_level_id),
                                        team_id   = str(team_id),
                                        email   = str(email),
                                        full_name   = str(full_name),
                                        is_active   = str(is_active),
                                        other_name   = str(other_name))
                   
                    if config_obj.is_exist_resource():
                        config_obj.update_resource()
                    else:
                        config_obj.add_resource()
            return 1, Msg.M001
        except Exception as e:
            println(e, 'exception')
            return 0, e.args[0]
        
    def get_list_sheet_name(self):
        config_obj      = Configuration()
        sheet_info      = config_obj.get_sheet_config()
        return sheet_info
    
    def get_sheet_information(self, list_sheet_id=None):
        config_obj      = Configuration()
        sheet_info      = config_obj.get_sheet_config(list_sheet_id)
        list_week       = ['2021-02-22', '2021-03-01', '2021-03-08', '2021-03-15', '2021-03-22']
        result  = [sheet_info, list_week]
        return result
        
    def get_timesheet_info(self, request_dict=None, from_date=None, to_date=None, sheet_ids=None, filter=None):
        try:
            missing_method = False
            if request_dict:
                try:
                    from_date   = request_dict[SessionKey.FROM]
                    to_date     = request_dict[SessionKey.TO]
                    sheet_ids   = request_dict[SessionKey.SHEETS]
                    filter      = request_dict[SessionKey.FILTER]
                except KeyError:
                    missing_method = True
            if not filter or not sheet_ids or not to_date or not from_date or missing_method:
                return []
            result = []
            timesheet_obj   = Timesheet(from_date, to_date, filter, sheet_ids)
            timesheet_obj.parse()
            user_ids        = timesheet_obj.user_ids
            eng_type_ids   = timesheet_obj.eng_type_ids
            team_ids        = timesheet_obj.team_ids
            time_off_info   = timesheet_obj.time_off
            
            for sheet_id in timesheet_obj.sheets:
                sheet_obj   = timesheet_obj.sheets[sheet_id]
                sheet_type  = sheet_obj.sheet_type
                sheet_name  = sheet_obj.sheet_name
                for user_id in sheet_obj.resource:
                    for task_obj in sheet_obj.resource[user_id]:
                        user_name   = task_obj.user_name
                        eng_type    = eng_type_ids[user_ids[user_id].eng_type_id]
                        team_name   = team_ids[user_ids[user_id].team_id]
                        week_number = task_obj.week_number
                        task_date   = task_obj.date
                        task_name   = task_obj.task_name
                        start_date  = task_obj.start_date
                        end_date    = task_obj.end_date
                        allocation  = task_obj.allocation
                        work_hour   = 8*(allocation)/100
                        timeoff     = 0
                        if user_id in time_off_info:
                            for date, week, timeoff_per_day, obj in time_off_info[user_id]:
                                if date == task_date:
                                    timeoff = timeoff_per_day
                                    break
                        
                        sdt_hour    = work_hour - timeoff
                        result.append((sheet_name, sheet_type, user_name, eng_type, team_name, week_number, task_date, task_name, start_date, end_date, allocation, work_hour, timeoff, sdt_hour))
            return result
            
        except Exception as e:
            println(e, 'exception')
            return 0, e.args[0]
    
    def get_newest_data(self, from_date, to_date, sheet_ids):
        
        try:
            self.parse_smarsheet_and_update_task(list_sheet_id =   sheet_ids,
                                                 from_date      =   from_date,
                                                 to_date        =   to_date)
            return 1, Msg.M002
        except Exception as e:
            println(e, 'exception')
            return 0, e.args[0]
        
        
        
        
        
        
        