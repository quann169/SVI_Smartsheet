'''
Created on Feb 22, 2021

@author: toannguyen
'''
from src.models.smartsheet.smartsheet_model import SmartSheets
from src.models.smartsheet.effective_rate_model import SmartSheetsEffective
from src.models.database.database_model import Configuration, DbTask, Log, DbEffectiveRate
from src.commons.enums import DbHeader, ExcelHeader, SettingKeys, DefaulteValue, SessionKey, \
                            DateTime, AnalyzeCFGKeys, Route, Role, OtherKeys, DbTable,\
    OtherCFGKeys, LogKeys
from src.commons.message import MsgError, MsgWarning, Msg, AnalyzeItem
from src.commons.utils import search_pattern, message_generate, println, remove_path, split_patern,\
                            get_prev_date_by_time_delta, get_work_week, convert_date_to_string,\
                            get_work_month, round_num, defined_color, \
                            get_work_days, write_message_into_file, convert_request_dict_to_url,\
                            str_to_date, get_end_week_of_date, get_start_week_of_date, get_month_name_of_date, \
                            calculate_start_end_date_by_option, check_domain_password, save_password, get_saved_password,\
                            render_jinja2_template, send_mail, compare_date
from flask import g   
from src.models.timesheet.timesheet_model import Timesheet
from flask import session
from pprint import pprint
import pandas as pd
import os, sys, datetime
import config
import xlwt
import xlrd
import time
from xlwt import Workbook
from xls2xlsx import XLS2XLSX


class Controllers:
    def __init__(self):
        pass
    
    def parse_smarsheet_and_update_task(self, from_date=None, to_date=None, list_sheet_id=None, log=None):
        if log:
            write_message_into_file(log, 'Starting parse smartsheet\n')
        println('Starting parse smartsheet', OtherKeys.LOGING_INFO)
        start_time = time.time()
        config_obj = Configuration()
        sheet_info  = config_obj.get_sheet_config(list_sheet_id)
        config_obj.get_list_holiday(is_parse=True)
        holidays  = config_obj.holidays
        list_sheet  = []
        analyze_config_info = config_obj.get_analyze_config()
        token   = analyze_config_info[AnalyzeCFGKeys.TOKEN]
        for row in sheet_info:
            list_sheet.append((row[DbHeader.SHEET_NAME], row[DbHeader.LATEST_MODIFIED], int(row[DbHeader.SHEET_ID]), row[DbHeader.PARSED_DATE]))
        sms_obj = SmartSheets(list_sheet=list_sheet, from_date=from_date, to_date=to_date, log=log, holidays=holidays, token=token)
        sms_obj.connect_smartsheet()
        sms_obj.parse()
        config_obj.get_all_user_information()
        user_info = config_obj.users
        other_name_info = config_obj.others_name
        task_obj    = DbTask()
        total = len(sms_obj.info)
        count = 0
        missing_user = {}
        write_message_into_file(log, '%s\n'%('-'*75))
        println('%s'%('-'*75), OtherKeys.LOGING_INFO)
        for sheet_name in sms_obj.info:
            count += 1
            # save children_task only
            child_tasks         = sms_obj.info[sheet_name].children_task
            sheet_id            = sms_obj.info[sheet_name].sheet_id
            latest_modified     = sms_obj.info[sheet_name].latest_modified
            is_parse            = sms_obj.info[sheet_name].is_parse
            if is_parse:
                if log:
                    write_message_into_file(log, '[%d/%d] Updating sheet: <span class="bold cl-blue">%s</span>\n'%(count, total, sheet_name))
                println('[%d/%d] Updating sheet: %s'%(count, total, sheet_name), OtherKeys.LOGING_INFO)
                config_obj.set_attr(sheet_id            = sheet_id,
                                    latest_modified     = latest_modified,
                                    parsed_date         = sms_obj.timedelta,
                                    is_loading          = 1)
                config_obj.update_is_loading_of_sheet()
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
                        try:
                            user_id = other_name_info[assign_to]
                        except KeyError:
                            missing_user[assign_to] = ''
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
                
                
                config_obj.update_latest_modified_of_sheet()
                
                config_obj.update_parsed_date_of_sheet()
                config_obj.set_attr(is_loading          = 0)
                config_obj.update_is_loading_of_sheet()
                println('[%d/%d] Update database for %s - Done'%(count, total, sheet_name), OtherKeys.LOGING_INFO)
                if log:
                    write_message_into_file(log, '[%d/%d] Update database for <span class="bold cl-blue">%s</span> - Done\n'%(count, total, sheet_name))
            else:
                println('[%d/%d] Skip update database for %s'%(count, total, sheet_name), OtherKeys.LOGING_INFO)
                if log:
                    write_message_into_file(log, '[%d/%d] Skip update database for <span class="bold cl-red">%s</span>\n'%(count, total, sheet_name))
        
        write_message_into_file(log, '%s\n'%('-'*75))
        println('%s'%('-'*75), OtherKeys.LOGING_INFO)
        
        for user in missing_user:
            message = message_generate(MsgWarning.W002, user)
            println('Warning: %s'%(message), OtherKeys.LOGING_INFO)
            if log:
                write_message_into_file(log, 'Warning: %s\n'%(message))
        end_time = time.time()
        diff = int(end_time - start_time)
        minutes, seconds = diff // 60, diff % 60
        message = "Time: " + str(minutes) + ':' + str(seconds).zfill(2)
        println(message, OtherKeys.LOGING_INFO)
        if log:
            write_message_into_file(log, message  + '\n')
    
    def convert_request_dict_to_url(self, request_dict):
        result = convert_request_dict_to_url(request_dict)
        return result
    
    def add_default_config_to_method_request(self, request_dict, more_option={}):
        for key, val in more_option.items():
            if not request_dict.get(key):
                request_dict[key] = val
        if not request_dict.get(SessionKey.FROM) or not request_dict.get(SessionKey.TO) or not request_dict.get(SessionKey.SHEETS) \
        or not request_dict.get(SessionKey.USERS):
            config_obj = Configuration()
            analyze_config_info = config_obj.get_analyze_config()
            time_delta_before = int(analyze_config_info[AnalyzeCFGKeys.TIME_DELTA_BEFORE])
            time_delta_after = int(analyze_config_info[AnalyzeCFGKeys.TIME_DELTA_AFTER])
            from_date      = get_prev_date_by_time_delta(time_delta_before)
            from_date       = get_start_week_of_date(from_date, output_str=True)
            to_date      = get_prev_date_by_time_delta(time_delta_after*(-1))
            to_date       = get_end_week_of_date(to_date, output_str=True)
            if not request_dict.get(SessionKey.FROM):
                request_dict[SessionKey.FROM] = convert_date_to_string(from_date, '%Y-%m-%d')
            if not request_dict.get(SessionKey.TO):
                request_dict[SessionKey.TO] = convert_date_to_string(to_date, '%Y-%m-%d')
            if not request_dict.get(SessionKey.SHEETS):
                config_obj.get_sheet_config(is_parse=True)
                sheet_ids_dict = config_obj.sheet_ids
                sheet_ids = []
                for key in sheet_ids_dict.keys():
                    sheet_ids.append(key)
                request_dict[SessionKey.SHEETS] = sheet_ids
            if request_dict.get(SessionKey.USERS) == None:
                users_info = config_obj.get_list_resource()
                users = []
                for row in users_info:
                    user = row[DbHeader.USER_NAME]
                    is_active = row[DbHeader.IS_ACTIVE]
                    if is_active:
                        users.append(user)
                request_dict[SessionKey.USERS] = users
    
    def get_analyze_config(self):
        config_obj = Configuration()
        analyze_config = config_obj.get_analyze_config()
        return analyze_config
    
    def import_timeoff(self, file_name):
        try:
            file_path   = os.path.join(os.path.join(config.WORKING_PATH, 'upload'), file_name)
            df          = pd.read_excel (file_path, sheet_name='Time-Off', engine='openpyxl')
            
            config_obj  = Configuration()
            config_obj.get_all_user_information()
            users_info  = config_obj.users
            user_full_name_info = config_obj.users_full_name
            other_name_info = config_obj.others_name
            exist_id     = {}
            
            list_record = []
            for index in range(0, len(df[ExcelHeader.ID])):
                id_timeoff          = str(df[ExcelHeader.ID][index])
                try:
                    unuse = exist_id[id_timeoff]
                    message = message_generate(MsgWarning.W001, id_timeoff)
                    println(message, OtherKeys.LOGING_DEBUG)
                    continue
                except KeyError:
                    exist_id[id_timeoff] = ''
                
                requester   = str(df[ExcelHeader.REQUESTER][index])
                department  = str(df[ExcelHeader.DEPARTMENT][index])
                type_leave  = str(df[ExcelHeader.TYPE][index])
                start_date  = str(df[ExcelHeader.START_DATE][index])
                end_date    = str(df[ExcelHeader.END_DATE][index])
                if requester in SettingKeys.EMPTY_CELL or start_date in SettingKeys.EMPTY_CELL or end_date in SettingKeys.EMPTY_CELL:
                    continue
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
                        try:
                            user_id = other_name_info[requester]
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
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]
        
    def get_timeoff_info(self):
        config_obj  = Configuration()
        result      = config_obj.get_list_timeoff()
        return result
    
    def import_holiday(self, file_name):
        try:
            file_path   = os.path.join(os.path.join(config.WORKING_PATH, 'upload'), file_name)
            df          = pd.read_excel (file_path, sheet_name='Holiday', engine='openpyxl')
            user_name   = session[SessionKey.USERNAME]
            config_obj  = Configuration()
            for index in range(0, len(df[ExcelHeader.HOLIDAY])):
                date          = str(df[ExcelHeader.HOLIDAY][index])
                if date not in SettingKeys.EMPTY_CELL:
                    if not config_obj.is_exist_holiday(date):
                        self.record_to_log(0, LogKeys.ACTION_ADD_HOLIDAY, '', '%s'%(date), user_name)
                        config_obj.add_holiday(date)
            remove_path(file_path)
            return 1, Msg.M001
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]
    
    def import_productivity_setting(self, file_name):
        try:
            file_path   = os.path.join(os.path.join(config.WORKING_PATH, 'upload'), file_name)
            df          = pd.read_excel (file_path, sheet_name='Productivity', engine='openpyxl')
            user_name   = session[SessionKey.USERNAME]
            week_list       = df[ExcelHeader.WEEK]
            resource_list    = df[ExcelHeader.RESOURCE]
            tmp_week = ''
            config_obj  = Configuration()
            config_obj.get_sheet_type_info(is_parse=True)
            sheet_type_info = config_obj.sheet_type
            config_obj.get_all_user_information()
            users    = config_obj.users
            list_record = []
            list_sheet_type = [ExcelHeader.NRE, ExcelHeader.RND, ExcelHeader.TRN, 
                               ExcelHeader.PRE_SALE, ExcelHeader.POST_SALE, ExcelHeader.SUPPORT, 
                               ExcelHeader.NONE_WH, ExcelHeader.OPERATING]
            list_week_remove = []
            
            for idx in range(0, len(week_list)):
                week = str(week_list[idx])
                resource = str(resource_list[idx]).strip()
                
                if week not in SettingKeys.EMPTY_CELL:
                    tmp_week = week
                    tmp_week = get_start_week_of_date(tmp_week, output_str=True)
                if not users.get(resource):
                    return [0, 'No such user %s'%resource]
                user_id = users[resource].user_id
                for sheet_type in list_sheet_type:
                    value = str((df[sheet_type][idx])).strip()
                    if value in SettingKeys.EMPTY_CELL:
                        value = 0
                    if not sheet_type_info.get(sheet_type):
                        return [0, 'No such sheet type %s'%sheet_type]
                    sheet_type_id = sheet_type_info[sheet_type]
                    list_week_remove.append(tmp_week)
                    list_record.append((tmp_week, sheet_type_id, user_id, value, user_name))
                        
            if len(list_record):
                list_week_remove = tuple(set(list_week_remove))
                config_obj.remove_productivity_config_by_date(list_week_remove)
                config_obj.add_productivity_config(list_record)
            remove_path(file_path)
            return 1, Msg.M001
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]
    
    def import_granted_setting(self, file_name):
        try:
            file_path   = os.path.join(os.path.join(config.WORKING_PATH, 'upload'), file_name)
            df          = pd.read_excel (file_path, sheet_name='Granted', engine='openpyxl')
            user_name   = session[SessionKey.USERNAME]
            granted_names       = df[ExcelHeader.GRANTED_NAME]
            granted_numbers    = df[ExcelHeader.GRANTED_NUMBER]
            sheet_names         = df[ExcelHeader.SHEET_NAME]
            tmp_name = ''
            config_obj  = Configuration()
            config_obj.get_sheet_config(is_parse=True, is_active=None)
            sheets          = config_obj.sheets
            list_record = []
            list_name_remove= []
            for idx in range(0, len(granted_names)):
                granted_name = str(granted_names[idx])
                granted_number = str(granted_numbers[idx]).strip()
                sheet_name      = str(sheet_names[idx]).strip()
                if granted_name not in SettingKeys.EMPTY_CELL:
                    tmp_name = granted_name
                if not sheets.get(sheet_name):
                    return [0, 'No such sheet  %s'%sheet_name]
                sheet_id = sheets[sheet_name][DbHeader.SHEET_ID]
                list_name_remove.append(tmp_name)
                list_record.append((tmp_name, sheet_id, granted_number, user_name))
            
            if len(list_record):
                list_name_remove = tuple(set(list_name_remove))
                config_obj.remove_granted_config_by_name(list_name_remove)
                config_obj.add_granted_config(list_record)
            remove_path(file_path)
            return 1, Msg.M001
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]
        
    def get_productivity_setting(self, start_date=None, end_date=None):
        config_obj  = Configuration()
        result = config_obj.get_productivity_config(start_date, end_date)
        return result   
    
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
    
    def get_granted_info(self):
        config_obj  = Configuration()
        config_obj.get_list_granted(is_parse=True)
        result = config_obj.granted
        return result  
    
    def get_sheet_config(self, is_active=None):
        config_obj  = Configuration()
        sheet_info      = config_obj.get_sheet_config(is_active=is_active)
        config_obj.get_sheet_user_info()
        project_user = config_obj.sheet_user
        return sheet_info, project_user
    
    def get_sheet_type_info(self):
        config_obj  = Configuration()
        config_obj.get_sheet_type_info(is_parse=True)
        sheet_type_id = config_obj.sheet_type_ids
        sheet_type = config_obj.sheet_type
        return sheet_type, sheet_type_id
    
    def update_session(self, key, val):
        try:
            session.pop(key, None)
            session[key] = val
            
            return 1, ''
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
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
    
    def import_sheet(self, file_name):
        try:
            file_path   = os.path.join(os.path.join(config.WORKING_PATH, 'upload'), file_name)
            df          = pd.read_excel (file_path, sheet_name='Sheet', engine='openpyxl')
            config_obj  = Configuration()
            config_obj.get_sheet_type_info(is_parse=True)
            sheet_type_info = config_obj.sheet_type
            analyze_config_info = config_obj.get_analyze_config()
            token   = analyze_config_info[AnalyzeCFGKeys.TOKEN]
        
            sms_obj = SmartSheets(token=token)
            sms_obj.connect_smartsheet()
            available_sheet_name = sms_obj.available_name
            #validate sheet 
            for index in range(0, len(df[ExcelHeader.SHEET_NAME])):
                sheet_name          = str(df[ExcelHeader.SHEET_NAME][index]).strip()
                if sheet_name not in SettingKeys.EMPTY_CELL and sheet_name not in available_sheet_name:
                    message = message_generate(MsgError.E002, sheet_name)
                    println(message, 'error')
                    return  0, message
            config_obj.set_attr(updated_by  = 'root')
            user_of_sheet   = {}
            config_obj.inactive_all_sheet()
            for index in range(0, len(df[ExcelHeader.SHEET_NAME])):
                sheet_name          = str(df[ExcelHeader.SHEET_NAME][index]).strip()
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
                                        is_active       = str(is_active),
                                        is_valid       = '1') 
                                        
                    if config_obj.is_exist_sheet():
                        config_obj.update_sheet()
                    else:
                        config_obj.add_sheet()
            #update project-user table
            self.update_resource_of_sheet(user_of_sheet)
            remove_path(file_path)
            return 1, Msg.M001
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
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
            user_name = session[SessionKey.USERNAME]
            teams  = config_obj.get_team_info(is_parse=True)
            teams_info = config_obj.team
            config_obj.set_attr(updated_by  = user_name)
            user_leader = []
            config_obj.inactive_all_resource()#except 'NA User'
            config_obj.active_resource(SettingKeys.NA_VALUE)
            for index in range(0, len(df[ExcelHeader.RESOURCE])):
                resource          = str(df[ExcelHeader.RESOURCE][index]).strip()
                eng_type          = str(df[ExcelHeader.ENG_TYPE][index])
                eng_level         = str(df[ExcelHeader.ENG_LEVEL][index])
                email             = str(df[ExcelHeader.EMAIL][index])
                full_name         = str(df[ExcelHeader.FULL_NAME][index])
                team              = str(df[ExcelHeader.TEAM][index])
                leader            = str(df[ExcelHeader.LEADER][index]).strip()
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
                    user_leader.append([resource, leader])
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
                        self.record_to_log(0, LogKeys.ACTION_ADD_RESOURCE, '', 
                                           '%s - %s - %s - %s'%(resource, email, full_name, str(is_active)), user_name)
                        config_obj.add_resource()
            #add leader
            config_obj.get_all_user_information()
            user_email = config_obj.user_email
            users = config_obj.users
            list_record = []
            for element in user_leader:
                resource_name, leader_email = element
                if leader_email in SettingKeys.EMPTY_CELL:
                    leader_email = SettingKeys.NA_VALUE
                if user_email.get(leader_email):
                    leader_name = user_email[leader_email].user_name
                    if users.get(leader_name):
                        leader_id = users[leader_name].user_id
                        user_id = users[resource_name].user_id
                        list_record.append((leader_id, user_id))
            if len(list_record):
                config_obj.update_resource_leader(list_record)
            remove_path(file_path)
            return 1, Msg.M001
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]
        
    def get_list_sheet_name(self, is_active=True):
        config_obj      = Configuration()
        sheet_info      = config_obj.get_sheet_config(is_active=is_active)
        return sheet_info
    
    def get_all_resource_information(self):
        config_obj      = Configuration()
        config_obj.get_all_user_information()
        user_email = config_obj.user_email
        users = config_obj.users
        user_ids = config_obj.user_ids
        others_name = config_obj.others_name
        return user_email, users, user_ids, others_name
    
    def get_sheet_information(self, list_sheet_id=None):
        config_obj      = Configuration()
        sheet_info      = config_obj.get_sheet_config(list_sheet_id)
        # start_date      = get_prev_date_by_time_delta(1)
        # end_date      = get_prev_date_by_time_delta(-3)
        # config_obj.get_list_holiday(is_parse=True)
        # holidays  = config_obj.holidays
        # start_date      = convert_date_to_string(start_date)
        # end_date      = convert_date_to_string(end_date)
        
        # list_workweek   = get_work_week(from_date=start_date, to_date=end_date, holidays=holidays)
        # list_week       = []
        # for week in list_workweek:
        #     list_week.append(week[0])
        list_week       = []
        result  = [sheet_info, list_week]
        return result
        
    def get_daily_timesheet_info(self, request_dict=None, from_date=None, to_date=None, sheet_ids=None,\
                                  task_filter=None, list_user=None, mode=None, filter='separate'):
        try:
            missing_method = False
            if request_dict:
                try:
                    from_date   = request_dict[SessionKey.FROM]
                    to_date     = request_dict[SessionKey.TO]
                    sheet_ids   = request_dict[SessionKey.SHEETS]
                    if request_dict.get(SessionKey.TASK_FILTER):
                        task_filter      = request_dict[SessionKey.TASK_FILTER]
                    if request_dict.get(SessionKey.USERS):
                        list_user      = request_dict[SessionKey.USERS]
                    if request_dict.get(SessionKey.MODE):
                        mode        = request_dict[SessionKey.MODE]
                    if request_dict.get(SessionKey.FILTER):
                        filter        = request_dict[SessionKey.FILTER]
                except KeyError:
                    missing_method = True
            if not task_filter or not sheet_ids or not to_date or not from_date or missing_method:
                return []
            if filter == 'merge':
                is_merge = True
            else:
                is_merge = False
            result = []
            timesheet_obj   = Timesheet(is_merge, from_date, to_date, task_filter, sheet_ids, list_user)
            timesheet_obj.parse()
            user_ids        = timesheet_obj.user_ids
            eng_type_ids   = timesheet_obj.eng_type_ids
            team_ids        = timesheet_obj.team_ids
            time_off_info   = timesheet_obj.time_off
            config_obj      = Configuration()
            config_obj.get_list_holiday(is_parse=True)
            holidays  = config_obj.holidays
            list_date = get_work_days(from_date, to_date, holidays=holidays)
            for sheet_id in timesheet_obj.sheets:
                sheet_obj   = timesheet_obj.sheets[sheet_id]
                sheet_type  = sheet_obj.sheet_type
                sheet_name  = sheet_obj.sheet_name
                for user_id in sheet_obj.resource:
                    for task_obj in sheet_obj.resource[user_id]:
                        user_name   = task_obj.user_name
                        if mode == 'na_user' and not user_name == SettingKeys.NA_VALUE:
                            continue
                        eng_type    = eng_type_ids[user_ids[user_id].eng_type_id]
                        team_name   = team_ids[user_ids[user_id].team_id]
                        week_number = task_obj.week_number
                        task_date   = task_obj.date
                        task_name   = task_obj.task_name
                        start_date  = task_obj.start_date
                        end_date    = task_obj.end_date
                        allocation  = task_obj.allocation
                        if is_merge:
                            list_date2 = get_work_days(start_date, end_date, holidays=holidays)
                            work_hour = 0
                            for date in list_date2:
                                if date in list_date:
                                    work_hour   += 8*(allocation)/100
                            work_hour   = round_num(work_hour)
                            timeoff     = ''
                            sdt_hour    = work_hour
                            result.append((sheet_name, sheet_type, user_name, eng_type, team_name, \
                                           week_number, task_date, task_name, start_date, end_date,\
                                            allocation, work_hour, timeoff, sdt_hour))
                        else:
                            work_hour   = 8*(allocation)/100
                            work_hour   = round_num(work_hour)
                            timeoff     = 0
                            if user_id in time_off_info:
                                for date, week, timeoff_per_day, obj in time_off_info[user_id]:
                                    if date == task_date:
                                        timeoff = timeoff_per_day
                                        break
                            
                            sdt_hour    = work_hour - timeoff
                            result.append((sheet_name, sheet_type, user_name, eng_type, team_name,\
                                            week_number, task_date, task_name, start_date, end_date,\
                                             allocation, work_hour, timeoff, sdt_hour))
            return result
            
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]
    
    def get_newest_data(self, from_date, to_date, sheet_ids):
        try:
            log_file = os.path.join(config.WORKING_PATH, "GetNewestData.log")
            if os.path.exists(log_file):
                os.remove(log_file)
            self.parse_smarsheet_and_update_task(list_sheet_id  = sheet_ids,
                                                 from_date      = from_date,
                                                 to_date        = to_date,
                                                 log            = log_file)
            println(Msg.M002, OtherKeys.LOGING_INFO)
            write_message_into_file(log_file, Msg.M002)
            time.sleep(2)
            return 1, Msg.M002
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            write_message_into_file(log_file, '[ERROR] %s'%(e.args[0]))
            return 1, '[ERROR] %s'%(e.args[0])
    
    def get_newest_data_log(self, request_dict={}):
        file_name = request_dict.get(SessionKey.FILE_NAME, 'GetNewestData.log')
        log_file = os.path.join(config.WORKING_PATH, file_name)
        result = ''
        if os.path.exists(log_file):
            with open(log_file, 'r') as log:
                result = log.read()
        result = result.replace('\n', '<br>')
        return result  
        
    def get_resource_timesheet_info(self, request_dict=None, from_date=None, to_date=None, sheet_ids=None, 
                                    filter='weekly', task_filter='both', mode='all', is_caculate=False, list_user=None):
        try:
            missing_method = False
            if request_dict:
                try:
                    from_date   = request_dict[SessionKey.FROM]
                    to_date     = request_dict[SessionKey.TO]
                    sheet_ids   = request_dict[SessionKey.SHEETS]
                    if request_dict.get(SessionKey.FILTER):
                        filter      = request_dict[SessionKey.FILTER]
                    if request_dict.get(SessionKey.MODE):
                        mode        = request_dict[SessionKey.MODE]
                    if request_dict.get(SessionKey.TASK_FILTER):
                        task_filter = request_dict[SessionKey.TASK_FILTER]
                    if request_dict.get(SessionKey.USERS):
                        list_user = request_dict[SessionKey.USERS]
                except KeyError:
                    missing_method = True
            
            if not filter or not sheet_ids or not to_date or not from_date or missing_method:
                return ({}, [], 0, 0, 0, 0, 0)
            timesheet_obj   = Timesheet(False, from_date, to_date, task_filter, sheet_ids, list_user)
            timesheet_obj.parse()
            user_ids        = timesheet_obj.user_ids
            eng_type_ids    = timesheet_obj.eng_type_ids
            team_ids        = timesheet_obj.team_ids
            time_off_info   = timesheet_obj.time_off
            config_obj      = Configuration()
            config_obj.get_list_holiday(is_parse=True)
            holidays  = config_obj.holidays
            list_exist_user = []
            info            = {}
            if filter == 'monthly':
                list_month   = get_work_month(from_date=from_date, to_date=to_date, holidays=holidays)
                cols_element = list_month
                list_sub_col       = []
                for col in cols_element:
                    month, year, max_hour = col
                    col_name    = DateTime.LIST_MONTH[month]
                    list_sub_col.append(col_name)
            else:
                list_week   = get_work_week(from_date=from_date, to_date=to_date, holidays=holidays)
                cols_element = list_week
                list_sub_col       = []
                for col in cols_element:
                    list_sub_col.append(col[0])
             
            # caculate timeoff by week/month
            timeoff_info_2 = {}
            for user_id in time_off_info:
                for date, week, timeoff_per_day, obj in time_off_info[user_id]:
                    if filter == 'monthly':
                        name     = get_month_name_of_date(date)
                    else:
                        name     = get_start_week_of_date(date)
                    if not  timeoff_info_2.get(user_id):
                        timeoff_info_2[user_id] = {}
                    if not timeoff_info_2[user_id].get(name):
                        timeoff_info_2[user_id][name] = 0
                    timeoff_info_2[user_id][name] += timeoff_per_day
            user_email, users, user_ids, others_name = self.get_all_resource_information()
            for sheet_id in timesheet_obj.sheets:
                sheet_obj   = timesheet_obj.sheets[sheet_id]
                sheet_name  = sheet_obj.sheet_name
                for user_id in sheet_obj.resource:
                    for task_obj in sheet_obj.resource[user_id]:
                        user_name   = task_obj.user_name
                        eng_type    = eng_type_ids[user_ids[user_id].eng_type_id]
                        team_name   = team_ids[user_ids[user_id].team_id]
                        leader_id = users[user_name].leader_id
                        #skip user inactive
                        if not users[user_name].is_active:
                            continue
                        if leader_id:
                            leader_name = user_ids[leader_id].user_name
                        else:
                            leader_name = SettingKeys.NA_VALUE
                        task_date   = task_obj.date
                        allocation  = task_obj.allocation
                        work_hour   = 8*(allocation)/100
                        timeoff     = 0
                        work_hour   = round_num(work_hour)
                        if filter == 'monthly':
                            col_element = task_obj.month_name
                        else:
                            col_element  = task_obj.start_week
                        if timeoff_info_2.get(user_id):
                            if timeoff_info_2[user_id].get(col_element):
                                timeoff = timeoff_info_2[user_id][col_element]
                        
                        if not info.get(eng_type):
                            info[eng_type]  = {}
                            
                        if not info[eng_type].get(team_name):
                            info[eng_type][team_name]  = {} 
                                      
                        if not info[eng_type][team_name].get(user_name):
                            info[eng_type][team_name][user_name]  = {}
                            info[eng_type][team_name][user_name]['leader_name'] = leader_name
                            list_exist_user.append(user_name)
                            for element in cols_element:
                                if filter == 'monthly':
                                    month, year, max_hour = element
                                    col_name    = DateTime.LIST_MONTH[month]
                                else:
                                    col_name, max_hour = element
                                info[eng_type][team_name][user_name][col_name]  = {'max_hour' : max_hour, 
                                                                                   'summary': [0, 0], 
                                                                                   'sheets': {},
                                                                                   'href': ''}
                        
                        if not info[eng_type][team_name][user_name][col_element]['sheets'].get(sheet_name):
                            info[eng_type][team_name][user_name][col_element]['sheets'][sheet_name]  = [0, 0]
                        
                        # add value
                        info[eng_type][team_name][user_name][col_element]['summary'][0]  += work_hour
                        info[eng_type][team_name][user_name][col_element]['summary'][1]  = timeoff
                        info[eng_type][team_name][user_name][col_element]['sheets'][sheet_name][0]  += work_hour

                        info[eng_type][team_name][user_name][col_element]['summary'][0]   = round_num(info[eng_type][team_name][user_name][col_element]['summary'][0])
                        info[eng_type][team_name][user_name][col_element]['summary'][1]  = round_num(info[eng_type][team_name][user_name][col_element]['summary'][1])
                        info[eng_type][team_name][user_name][col_element]['sheets'][sheet_name][0]  = round_num(info[eng_type][team_name][user_name][col_element]['sheets'][sheet_name][0])
                        start, end = calculate_start_end_date_by_option(task_date, from_date, to_date, filter)
                        href = '%s?%s'%(Route.PROJECT_TIMESHEET, convert_request_dict_to_url(request_dict, [[SessionKey.USERS, [user_name]],
                                                                                                             [SessionKey.MODE, 'view'],
                                                                                                             [SessionKey.TASK_FILTER, task_filter],
                                                                                                             [SessionKey.FROM, start],
                                                                                                             [SessionKey.TO, end],
                                                                                                             [SessionKey.EXPAND_COLLAPSE, 'expand'],
                                                                                                             ]))
                        info[eng_type][team_name][user_name][col_element]['href'] = href
            #add missing date for user missing task but enought timeoff
            for user_id in timeoff_info_2:
                eng_type    = eng_type_ids[user_ids[user_id].eng_type_id]
                user_name = user_ids[user_id].user_name
                #skip user inactive
                if not user_ids[user_id].is_active:
                    continue
                if list_user and not (user_name in list_user):
                    continue
                team_name   = team_ids[user_ids[user_id].team_id]
                leader_id = users[user_name].leader_id
                if leader_id:
                    leader_name = user_ids[leader_id].user_name
                else:
                    leader_name = SettingKeys.NA_VALUE
                for date_name in timeoff_info_2[user_id]:
                    timeoff = timeoff_info_2[user_id][date_name]
                    if not info.get(eng_type):
                        info[eng_type]  = {}
                        
                    if not info[eng_type].get(team_name):
                        info[eng_type][team_name]  = {} 
                                  
                    if not info[eng_type][team_name].get(user_name):
                        list_exist_user.append(user_name)
                        info[eng_type][team_name][user_name]  = {}
                        info[eng_type][team_name][user_name]['leader_name'] = leader_name
                    
                    for element in cols_element:
                        if filter == 'monthly':
                            month, year, max_hour = element
                            col_name    = DateTime.LIST_MONTH[month]
                        else:
                            col_name, max_hour = element
                        if not info[eng_type][team_name][user_name].get(col_name):
                            info[eng_type][team_name][user_name][col_name]  = {'max_hour' : max_hour, 
                                                                               'summary': [0, 0], 
                                                                               'sheets': {},
                                                                               'href': ''}
                        if date_name == col_name:
                            info[eng_type][team_name][user_name][col_name]['summary'][1]  = timeoff
            
            # Add user missing task
            if not list_user:
                for resource, resource_obj in users.items():
                    user_id = resource_obj.user_id
                    if resource_obj.is_active:
                        if resource not in list_exist_user:
                            eng_type    = eng_type_ids[user_ids[user_id].eng_type_id]
                            user_name = resource
                            team_name   = team_ids[user_ids[user_id].team_id]
                            leader_id = users[user_name].leader_id
                            if leader_id:
                                leader_name = user_ids[leader_id].user_name
                            else:
                                leader_name = SettingKeys.NA_VALUE
                           # if filter == 'monthly':
                            #    loop_element = list_month
                            #else:
                            #    loop_element = list_week
                            #for week, max_hours in loop_element:
                                #work_hours = 0
                            if not info.get(eng_type):
                                info[eng_type]  = {}
                            if not info[eng_type].get(team_name):
                                info[eng_type][team_name]  = {} 
                                          
                            if not info[eng_type][team_name].get(user_name):
                                info[eng_type][team_name][user_name]  = {}
                                info[eng_type][team_name][user_name]['leader_name'] = leader_name
                            
                            for element in cols_element:
                                if filter == 'monthly':
                                    month, year, max_hour = element
                                    col_name    = DateTime.LIST_MONTH[month]
                                else:
                                    col_name, max_hour = element
                                if not info[eng_type][team_name][user_name].get(col_name):
                                    info[eng_type][team_name][user_name][col_name]  = {'max_hour' : max_hour, 
                                                                                       'summary': [0, 0], 
                                                                                       'sheets': {},
                                                                                       'href': ''}
                
            total    = 0
            no_missing   = 0
            no_redundant = 0
            no_enought   = 0
            count_overlap   = 0
            
            # caculate miising, redundant, enought timesheet
            if is_caculate:
                for eng_type in info:
                    for team in info[eng_type]:
                        list_user_remove = []
                        for user_name in info[eng_type][team]:
                            timesheet = info[eng_type][team][user_name]
                            is_remove = True
                            total += 1
                            is_enought = True
                            is_less = False
                            is_greater = False
                            for column in list_sub_col:
                                hours = timesheet[column]['summary']
                                max_hour = timesheet[column]['max_hour']
                                if not( hours[0] + hours[1] == max_hour):
                                    is_enought = False
                                if hours[0] + hours[1] < max_hour:
                                    is_less = True
                                if hours[0] + hours[1] > max_hour:
                                    is_greater = True
                            if is_enought:
                                no_enought += 1
                            if is_less:
                                no_missing += 1
                            if is_greater:
                                no_redundant += 1
                no_missing = total - no_missing
                no_redundant = total - no_redundant
                no_enought = total - no_enought
                count_overlap   = total - count_overlap
            
            # remove user by mode                
            if mode in ['equal', 'greater', 'less']:
                for eng_type in info:
                    for team in info[eng_type]:
                        list_user_remove = []
                        for user_name in info[eng_type][team]:
                            timesheet = info[eng_type][team][user_name]
                            is_remove = True
                            for column in list_sub_col:
                                hours = timesheet[column]['summary']
                                max_hour = timesheet[column]['max_hour']
                                if mode == 'equal':
                                    if not( hours[0] + hours[1] == max_hour):
                                        is_remove = True
                                        break
                                    else:
                                        is_remove = False
                                elif mode == 'less':
                                    if hours[0] + hours[1] < max_hour:
                                        is_remove = False
                                        break
                                elif mode == 'greater':
                                    if hours[0] + hours[1] > max_hour:
                                        is_remove = False
                                        break
                            if is_remove:
                                list_user_remove.append(user_name)
                        for user_name in list_user_remove: 
                            del info[eng_type][team][user_name]

            result = (info, list_sub_col, no_missing, no_redundant, no_enought, count_overlap, total)
            return result
            
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]
    
    def export_detail_timesheet(self, wb, from_date, to_date, sheet_ids, color_style, options):
        style_header = color_style['gray25']
        start_col, start_row = (0, 0)
        for task_filter in options['detail'][SessionKey.TASK_FILTER]:
            # export daily timesheet
            daily_timesheet_info = self.get_daily_timesheet_info(from_date=from_date, to_date=to_date, sheet_ids=sheet_ids, task_filter=task_filter)
            daily_timesheet_wb = wb.add_sheet('detail timesheet ' + task_filter)
            row_num, col_num = (0, 0)
            
            # create  header
            list_header = ['Sheet Name', 'Type', 'Resource', 'Eng Type', 'Team', 'WW No.', 'Date', 'Task', 'Start Date', \
                           'End Date', 'Allocation', 'Work Hours', 'Time Off', 'STD Hours']
            for header in list_header:
                if col_num == 7:
                    daily_timesheet_wb.col(col_num).width = 256 * 50
                else:
                    daily_timesheet_wb.col(col_num).width = 256 * 14
                daily_timesheet_wb.write(row_num, col_num, header, style_header)
                col_num += 1
            col_num = start_col
            row_num += 1
            
            # create  body
            for row in daily_timesheet_info:
                for cell in row:
                    daily_timesheet_wb.write(row_num, col_num, cell)
                    col_num += 1
                col_num = start_col
                row_num += 1
            # end daily timesheet
    
    def export_resource_timesheet(self, wb, from_date, to_date, sheet_ids, color_style, options):
        style_header = color_style['gray25']
        start_col, start_row = (0, 0)
        # export resource timesheet
        for task_filter in options['resource'][SessionKey.TASK_FILTER]:
            for filter in options['resource'][SessionKey.FILTER]:
                resource_wb = wb.add_sheet('%s resource  %s'%(filter, task_filter))
                w_resource_info, list_week, u1, u2, u3, u4, u5 = self.get_resource_timesheet_info(from_date=from_date, 
                                                                                                   to_date=to_date, 
                                                                                                   sheet_ids=sheet_ids, 
                                                                                                   task_filter=task_filter,
                                                                                                   filter=filter)
                start_col, start_row = (0, 0)
                row_num, col_num = (0, 0)
                # create  header
                list_header = ['Eng Type', 'DM','Team', 'Resource'] + list_week
                for header in list_header:
                    resource_wb.col(col_num).width = 256 * 14
                    resource_wb.write(row_num, col_num, header, style_header)
                    col_num += 1
                col_num = start_col
                row_num += 1
                for eng_type in w_resource_info:
                    for team in w_resource_info[eng_type]:
                        for user_name in w_resource_info[eng_type][team]:
                            timesheet = w_resource_info[eng_type][team][user_name]
                            leader_name = timesheet['leader_name']
                            resource_wb.write(row_num, col_num, eng_type)
                            col_num += 1
                            resource_wb.write(row_num, col_num, leader_name)
                            col_num += 1
                            resource_wb.write(row_num, col_num, team)
                            col_num += 1
                            resource_wb.write(row_num, col_num, user_name)
                            col_num += 1
                            for column in list_week:
                                hours = timesheet[column]['summary']
                                details = timesheet[column]['sheets']
                                max_hour = timesheet[column]['max_hour']
                                value = max_hour
                                color = ''
                                if hours[0] + hours[1] > max_hour:
                                    color = 'orange'
                                elif hours[0] + hours[1] == max_hour:
                                    color = 'lime'
                                else:
                                    color = 'tan'
                                    value  = hours[0] + hours[1]
                                resource_wb.write(row_num, col_num, value, color_style[color])
                                col_num += 1
                            col_num = start_col
                            row_num += 1
        #end resource
    def export_project_timesheet(self, wb, from_date, to_date, sheet_ids, color_style, options, granted_list, cost):
        style_header = color_style['gray25']
        start_col, start_row = (0, 0)
        # export resource timesheet
        for task_filter in options['project'][SessionKey.TASK_FILTER]:
            for filter in options['project'][SessionKey.FILTER]:
                # Project timesheet
                project_wb = wb.add_sheet('%s project  %s'%(filter, task_filter))
                w_project_info, list_week, u1, u2, type_and_sheet_info, granted_info = self.get_project_timesheet_info(from_date=from_date, \
                                                                                               to_date=to_date, 
                                                                                               sheet_ids=sheet_ids, \
                                                                                               task_filter=task_filter,
                                                                                               filter=filter,
                                                                                               granted_list=granted_list,
                                                                                               cost=cost)
                start_col, start_row = (0, 0)
                row_num, col_num = (0, 0)
                # create  header
                list_header = ['Sheet Type', 'Sheet', 'Resource', 'Eng Type', 'Team'] + list_week + ['Granted', 'Used', 'Remain']
                for header in list_header:
                    project_wb.col(col_num).width = 256 * 14
                    project_wb.write(row_num, col_num, header, style_header)
                    col_num += 1
                col_num = start_col
                row_num += 1
                
                for sheet_type in sorted(type_and_sheet_info.keys()): 
                    count = 0
                    for sheet_name in sorted(type_and_sheet_info[sheet_type].keys()):
                        
                        if sheet_name in w_project_info and sheet_name != 'total':
                            count += 1
                            if sheet_name in granted_info:
                                granted_number = granted_info[sheet_name][DbHeader.GRANTED_NUMBER]
                            else:
                                granted_number = 0
                            
                            if count == 1:
                                # row sheet type
                                project_wb.write(row_num, col_num, sheet_type, color_style['light_turquoise'])
                                col_num += 1
                                project_wb.write(row_num, col_num, '', color_style['light_turquoise'])
                                col_num += 1
                                project_wb.write(row_num, col_num, '', color_style['light_turquoise'])
                                col_num += 1
                                project_wb.write(row_num, col_num, '', color_style['light_turquoise'])
                                col_num += 1
                                project_wb.write(row_num, col_num, '', color_style['light_turquoise'])
                                col_num += 1
                                for column in list_week:
                                    project_wb.write(row_num, col_num, type_and_sheet_info[sheet_type]['total'][column], color_style['light_turquoise'])
                                    col_num += 1
                                project_wb.write(row_num, col_num, '', color_style['light_turquoise'])
                                col_num += 1
                                project_wb.write(row_num, col_num, type_and_sheet_info[sheet_type]['total']['total_row'], color_style['light_turquoise'])
                                col_num += 1
                                project_wb.write(row_num, col_num, '', color_style['light_turquoise'])
                                col_num = start_col
                                row_num += 1
                            
                            # row sheet
                            project_wb.write(row_num, col_num, '')
                            col_num += 1
                            project_wb.write(row_num, col_num, sheet_name, color_style['light_turquoise'])
                            col_num += 1
                            project_wb.write(row_num, col_num, '', color_style['light_turquoise'])
                            col_num += 1
                            project_wb.write(row_num, col_num, '', color_style['light_turquoise'])
                            col_num += 1
                            project_wb.write(row_num, col_num, '', color_style['light_turquoise'])
                            col_num += 1
                            for column in list_week:
                                project_wb.write(row_num, col_num, w_project_info[sheet_name]['total'][column], color_style['light_turquoise'])
                                col_num += 1
                            project_wb.write(row_num, col_num, granted_number, color_style['light_turquoise'])
                            col_num += 1
                            project_wb.write(row_num, col_num, w_project_info[sheet_name]['total_row'], color_style['light_turquoise'])
                            col_num += 1
                            project_wb.write(row_num, col_num, granted_number - w_project_info[sheet_name]['total_row'], color_style['light_turquoise'])
                            col_num = start_col
                            row_num += 1
                            # user
                            for user_name in w_project_info[sheet_name]['resource']:
                                eng_type = w_project_info[sheet_name]['resource'][user_name]['eng_type']
                                team = w_project_info[sheet_name]['resource'][user_name]['team']
                                eng_type = w_project_info[sheet_name]['resource'][user_name]['eng_type']
                                timesheet = w_project_info[sheet_name]['resource'][user_name]['timesheet']
                                r_total = w_project_info[sheet_name]['resource'][user_name]['total']
                                project_wb.write(row_num, col_num, '')
                                col_num += 1
                                project_wb.write(row_num, col_num, '')
                                col_num += 1
                                project_wb.write(row_num, col_num, user_name)
                                col_num += 1
                                project_wb.write(row_num, col_num, eng_type)
                                col_num += 1
                                project_wb.write(row_num, col_num, team)
                                col_num += 1
                                
                                for column in list_week:
                                    work_hour = timesheet[column]['work_hour']
                                    max_hour = timesheet[column]['max_hour']
                                    if work_hour > max_hour:
                                        project_wb.write(row_num, col_num, max_hour, color_style['orange'])
                                        col_num += 1
                                    elif work_hour  == max_hour:
                                        project_wb.write(row_num, col_num, max_hour, color_style['lime'])
                                        col_num += 1
                                    else:
                                        project_wb.write(row_num, col_num, work_hour, color_style['tan'])
                                        col_num += 1
                                project_wb.write(row_num, col_num, '', color_style['white'])
                                col_num += 1
                                project_wb.write(row_num, col_num, r_total, color_style['white'])
                                col_num += 1
                                project_wb.write(row_num, col_num, '', color_style['white'])
                                col_num = start_col
                                row_num += 1
                #end project
                
    def export_excel(self, from_date, to_date, sheet_ids, options, granted_list, cost):
        try:
            if not (from_date and to_date and sheet_ids):
                return 0, MsgError.E003
            wb = Workbook()
            file_name = 'Report.xls'
            output_path   = os.path.join(config.WORKING_PATH, file_name)
            file_name2 = 'Report.xlsx'
            output_path2   = os.path.join(config.WORKING_PATH, file_name2)
            if os.path.exists(output_path):
                os.remove(output_path)           
            # style 
            color_style = defined_color()
            
            # export daily timesheet
            println("Export daily timesheet")
            self.export_detail_timesheet(wb, from_date, to_date, sheet_ids, color_style, options)
            
            # export resource timesheet
            println("Export resource timesheet")
            self.export_resource_timesheet(wb, from_date, to_date, sheet_ids, color_style, options)
            
            #Export Project timesheet
            println("Export project timesheet")
            self.export_project_timesheet(wb, from_date, to_date, sheet_ids, color_style, options, granted_list, cost)
            try:
                wb.save(output_path)
                x2x = XLS2XLSX(output_path)
                remove_path(output_path)
                x2x.to_xlsx(output_path2)
                println('Output file: %s'%output_path2)
                os.system('start %s'%(output_path2))
            except IndexError:
                return 0, 'Can not export file because there are no sheets in the output workbook.'
            return 1, file_name2
        
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]
    
    def add_to_final(self, from_date, to_date, sheet_ids, overwrite=False, data=None):
        try:
            workdays = get_work_days(from_date=from_date, to_date=to_date)
            list_date = []
            user_name = session[SessionKey.USERNAME]
            password = session[SessionKey.PASSWORD]
            for date, week in workdays:
                list_date.append(date)
            task_obj    = DbTask()
            config_obj = Configuration()
            config_obj.get_sheet_config(is_parse=True)
            sheet_ids_info = config_obj.sheet_ids
            analyze_item = task_obj.get_analyze_item()
            o_config = config_obj.get_other_config_info()
            bcc = o_config.get(OtherCFGKeys.BCC_MAIL)
            
            if from_date and to_date and sheet_ids:
                list_sheet_name = []
                for sheet_id in sheet_ids:
                    list_sheet_name.append(sheet_ids_info[int(sheet_id)][DbHeader.SHEET_NAME])
                    task_obj.set_attr(sheet_id  = str(sheet_id),
                                      start_date = from_date,
                                      end_date   = to_date)
                    # if overwrite:
#                         task_obj.remove_final_task_information()
                    task_obj.move_task_to_final()
                    for date in list_date:
                        final_date_id = task_obj.add_final_date(date=date, sheet_id=sheet_id, from_date=from_date, to_date=to_date)
                        for row in data:
                            item_name = row[0]
                            counter = row[1]
                            is_approve = row[2]
                            comment = row[3]
                            analyze_item_id = analyze_item[item_name]
                            task_obj.add_final_evidence(final_date_id, analyze_item_id, is_approve, counter, comment, user_name)
                    self.record_to_log(sheet_id, LogKeys.ACTION_ADD_FINAL_TASK, '', 'From %s To %s'%(from_date, to_date), user_name)
                template_path = g.template_path
                tool_path    = g.tool_path
                template_path = os.path.join(os.path.join(os.path.join(tool_path, template_path), 'components'), 'sending_mail')
                dict_variable = {}
                dict_variable['info'] = data
                dict_variable['user_name'] = user_name
                dict_variable['from_date'] = from_date
                dict_variable['to_date'] = to_date
                dict_variable['sheets'] = ', '.join(list_sheet_name)
                content = render_jinja2_template(template_path, 'analyze_table.html', dict_variable)
                send_mail_status = send_mail(user_name, password, ['svi_pm@savarti.com'], [], 'Timesheet Report: Add final task', content, bcc, False)
                if not send_mail_status[0]:
                    return send_mail_status
                return 1, Msg.M003
            else:
                # missing input
                return 0, MsgError.E003
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]
    
    def calculate_conflict_to_add_final_task(self, request_dict=None, from_date=None, to_date=None, sheet_ids=None, mode='exist'):
        missing_method = False
        if request_dict:
            try:
                from_date   = request_dict[SessionKey.FROM]
                to_date     = request_dict[SessionKey.TO]
                sheet_ids   = request_dict[SessionKey.SHEETS]
                try: 
                    mode        = request_dict[SessionKey.MODE]
                except KeyError:
                    mode    = mode
            except KeyError:
                missing_method = True
        if not filter or not sheet_ids or not to_date or not from_date or missing_method:
            return []
        result = []
        enable_add = True
        config_obj  = Configuration()
        config_obj.get_sheet_config(is_parse=True)
        config_obj.get_list_holiday(is_parse=True)
        holidays  = config_obj.holidays
        cfg_sheet_ids = config_obj.sheet_ids
        task_obj  = DbTask()
        workdays = get_work_days(from_date=from_date, to_date=to_date, holidays=holidays)
        list_date = []
        for date, week in workdays:
            list_date.append(date)
        total = len(sheet_ids)
        count_fail = 0 
        if mode == 'exist':
            task_obj.set_attr(start_date = from_date,
                          end_date = to_date)
            final_date_info = task_obj.get_final_date()
            for sheet_id in sheet_ids:
                sheet_name = cfg_sheet_ids[sheet_id][DbHeader.SHEET_NAME]
                is_conflict = False
                list_1 = []
                for date in list_date:
                    is_exist_date = False
                    if sheet_id in final_date_info and date in final_date_info[sheet_id]:
                        is_conflict = True
                        enable_add  = False
                        is_exist_date = True
                        list_1.append((date, is_exist_date))
                    else:
                        list_1.append((date, is_exist_date))
                if is_conflict:
                    count_fail += 1
                result.append((is_conflict, sheet_name, list_1))
                
        elif mode == 'continuity':
            prev_date = get_prev_date_by_time_delta(timedelta = 1, compare_date = from_date)
            task_obj.set_attr(start_date = prev_date,
                          end_date = to_date)
            final_date_info = task_obj.get_final_date()
            workdays2 = get_work_days(from_date=prev_date, to_date=to_date)
            list_date2 = []
            for date, week in workdays2:
                list_date2.append(date)
            
            for sheet_id in sheet_ids:
                sheet_name = cfg_sheet_ids[sheet_id][DbHeader.SHEET_NAME]
                is_conflict = False
                list_1 = []
                for date in list_date2:
                    is_exist_date = None
                    if (sheet_id in final_date_info and date in final_date_info[sheet_id]) or (date in list_date):
                        is_exist_date = False
                        list_1.append((date, is_exist_date))
                    elif sheet_id not in final_date_info:
                        list_1.append((date, is_exist_date))
                    elif date in holidays:
                        list_1.append((date, is_exist_date))
                    else:
                        is_conflict = True
                        enable_add  = False
                        list_1.append((date, is_exist_date))
                if is_conflict:
                    count_fail += 1
                result.append((is_conflict, sheet_name, list_1))
        return result, enable_add, count_fail, total
    
    def analyze(self, request_dict=None, from_date=None, to_date=None, sheet_ids=None, task_filter='current'):
        missing_method = False
        if request_dict:
            try:
                from_date   = request_dict[SessionKey.FROM]
                to_date     = request_dict[SessionKey.TO]
                sheet_ids   = request_dict[SessionKey.SHEETS]
                task_filter = request_dict[SessionKey.TASK_FILTER]
            except KeyError:
                missing_method = True
        if not filter or not sheet_ids or not to_date or not from_date or missing_method:
            return []
#         config_obj = Configuration()
#         analyze_item = config_obj.get_analyze_item()
#         
        info, list_sub_column, no_missing, no_redundant, no_enought, count_overlap, total_resource = self.get_resource_timesheet_info(request_dict, is_caculate=True)
        if no_missing == total_resource:
            i1_status = True
        else:
            i1_status = False
        i1_method = convert_request_dict_to_url(request_dict, [[SessionKey.MODE, 'less'], [SessionKey.TASK_FILTER, task_filter]])
        
        if no_redundant == total_resource:
            i2_status = True
        else:
            i2_status = False
        i2_method = convert_request_dict_to_url(request_dict, [[SessionKey.MODE, 'greater'], [SessionKey.TASK_FILTER, task_filter]])
        
        if total_resource - no_enought == total_resource:
            i3_status = True
        else:
            i3_status = False
        i3_method = convert_request_dict_to_url(request_dict, [[SessionKey.MODE, 'equal'], [SessionKey.TASK_FILTER, task_filter]])
        
        unuse, i4_status, i4_count_fail, i4_total = self.calculate_conflict_to_add_final_task(from_date=from_date, 
                                                                                              to_date=to_date, 
                                                                                              sheet_ids=sheet_ids, 
                                                                                              mode='exist')
        i4_method = convert_request_dict_to_url(request_dict, [[SessionKey.MODE, 'exist'], 
                                                               [SessionKey.TITLE, AnalyzeItem.A004]])
        
        
        unuse, i5_status, i5_count_fail, i5_total = self.calculate_conflict_to_add_final_task(from_date=from_date, 
                                                                                              to_date=to_date, 
                                                                                              sheet_ids=sheet_ids, 
                                                                                              mode='continuity')
        i5_method = convert_request_dict_to_url(request_dict, [[SessionKey.MODE, 'continuity'],
                                                               [SessionKey.TITLE, AnalyzeItem.A005]])
        
        info, list_sub_column, i6_count_fail, i6_total, type_and_sheet_info, granted_info = self.get_project_timesheet_info(request_dict, is_caculate=True)
        if i6_total - i6_count_fail == i6_total:
            i6_status = True
        else:
            i6_status = False
        i6_method = convert_request_dict_to_url(request_dict, [[SessionKey.MODE, 'sheet_user'], [SessionKey.TASK_FILTER, task_filter]])
        
        #
        from_date   = request_dict[SessionKey.FROM]
        to_date     = request_dict[SessionKey.TO]
        sheet_ids   = request_dict[SessionKey.SHEETS]
        task_filter = None
        if request_dict.get(SessionKey.TASK_FILTER):
            task_filter      = request_dict[SessionKey.TASK_FILTER]
        list_user = None
        if request_dict.get(SessionKey.USERS):
            list_user      = request_dict[SessionKey.USERS]
        
        info = self.get_daily_timesheet_info(from_date=from_date, to_date=to_date, sheet_ids=sheet_ids, 
                                             task_filter=task_filter, list_user=list_user, mode='na_user')
        i7_status = True
        if len(info):
            i7_status = False
        i7_method = convert_request_dict_to_url(request_dict, [[SessionKey.MODE, 'na_user'], [SessionKey.TASK_FILTER, task_filter]])
        i7_count_fail, i7_total = len(info), None
        result = [
            [AnalyzeItem.A001, i1_status, True, '%s?%s'%(Route.RESOURCE_TIMESHEET, i1_method), no_missing, total_resource],
            [AnalyzeItem.A002, i2_status, True, '%s?%s'%(Route.RESOURCE_TIMESHEET, i2_method), no_redundant, total_resource],
            [AnalyzeItem.A003, i3_status, True, '%s?%s'%(Route.RESOURCE_TIMESHEET, i3_method), no_enought, total_resource],
            [AnalyzeItem.A004, i4_status, False, '%s?%s'%(Route.CONFLICT_DATE, i4_method), i4_count_fail, i4_total],
            [AnalyzeItem.A005, i5_status, False, '%s?%s'%(Route.CONFLICT_DATE, i5_method), i5_count_fail, i5_total],
            [AnalyzeItem.A006, i6_status, True, '%s?%s'%(Route.PROJECT_TIMESHEET, i6_method), i6_count_fail, i6_total],
            [AnalyzeItem.A007, i7_status, True, '%s?%s'%(Route.DETAIL, i7_method), i7_count_fail, i7_total]
            ]        
        return result
    
    def check_get_newest_data_feature_is_running(self, sheet_ids=[]):
        config_obj  = Configuration()
        if not len(sheet_ids):
            config_obj.get_sheet_config(is_parse=True)
            sheet_ids_dict = config_obj.sheet_ids
            sheet_ids = []
            for key in sheet_ids_dict.keys():
                sheet_ids.append(key)
        dict_id     = config_obj.get_sheet_loading_smartsheet()
        list_sheet = []
        for sheet_id in sheet_ids:
            sheet_id = int(sheet_id)
            if dict_id.get(sheet_id):
                list_sheet.append(dict_id[sheet_id])
                if len(list_sheet) == 2:
                    break
        if len(list_sheet):
            result = (True, list_sheet)
        else:
            result = (False, [])
        return result 
    
    def calculate_cost_project_timesheet(self, timesheet_info, timeoff_info):
        # group timesheet by resource to calculate cost
        timesheet_by_resource = {}
        for sheet_name, sheet_data in timesheet_info.items():
            if sheet_data.get('resource'):
                for resource, resource_data in sheet_data['resource'].items():
                    if resource_data.get('timesheet'):
                        user_id = resource_data['user_id']
                        for col_name, col_data in resource_data['timesheet'].items():
                            max_hour = col_data['max_hour']
                            work_hour = col_data['work_hour']
                            if not timesheet_by_resource.get(resource):
                                timesheet_by_resource[resource] = {}
                            resource_data_2 = timesheet_by_resource[resource]
                            if not resource_data_2.get(col_name):
                                timeoff = 0
                                if timeoff_info.get(user_id) and timeoff_info[user_id].get(col_name):
                                    timeoff = timeoff_info[user_id].get(col_name)
                                resource_data_2[col_name] = {'sheets': [],
                                                             'max_hour': max_hour,
                                                             'work_hour': [],
                                                             'timeoff': timeoff}
                            col_data_2 = resource_data_2[col_name]
                            col_data_2['sheets'].append(sheet_name)
                            col_data_2['work_hour'].append(work_hour)
                  
        #calculate cost and update the input data
        for resource, resource_data_3 in timesheet_by_resource.items():
            for col_name, col_data_3 in resource_data_3.items():
                sheets = col_data_3['sheets']
                timeoff = col_data_3['timeoff']
                work_hours = col_data_3['work_hour']
                max_hour = col_data_3['max_hour']
                sum_real_hour = sum(work_hours)
                total = timeoff + sum_real_hour
                if total > max_hour:
                    standar_hour = max_hour - timeoff
                    percent_number = standar_hour / sum_real_hour
                    for idx in range(0, len(sheets)):
                        sheet_name = sheets[idx]
                        work_hour = work_hours[idx]
                        cost = percent_number * work_hour
                        cost = round_num(cost)
                        timesheet_info[sheet_name]['resource'][resource]['timesheet'][col_name]['work_hour'] = cost

    
    def get_project_timesheet_info(self, request_dict=None, from_date=None, to_date=None, sheet_ids=None, filter='weekly', 
                                   mode='all', task_filter='both', list_user=None, is_caculate=False, granted_list=None, cost=None):
        try:
            missing_method = False
            if request_dict:
                try:
                    from_date   = request_dict[SessionKey.FROM]
                    to_date     = request_dict[SessionKey.TO]
                    sheet_ids   = request_dict[SessionKey.SHEETS]
                    if request_dict.get(SessionKey.FILTER):
                        filter      = request_dict[SessionKey.FILTER]
                    if request_dict.get(SessionKey.MODE):
                        mode        = request_dict[SessionKey.MODE]
                    if request_dict.get(SessionKey.USERS):
                        list_user = request_dict[SessionKey.USERS]
                    if request_dict.get(SessionKey.TASK_FILTER):
                        task_filter = request_dict[SessionKey.TASK_FILTER]
                    if request_dict.get(SessionKey.GRANTED_LIST):
                        granted_list = request_dict[SessionKey.GRANTED_LIST]
                    if request_dict.get(SessionKey.COST):
                        cost = request_dict[SessionKey.COST]
                except KeyError:
                    missing_method = True
            
            if not filter or not sheet_ids or not to_date or not from_date or missing_method:
                return ({}, [], 0, 0, {}, {})
            granted_info = {}
            if granted_list:
                granted_info = self.get_granted_info()
                granted_info = granted_info[granted_list]
            sheet_user2 = None
            sheet_user3 = None
            config_obj      = Configuration()
            
            if is_caculate or mode == 'sheet_user':
                config_obj.get_sheet_user_info()
                sheet_user2 = config_obj.sheet_user2
                sheet_user3 = config_obj.sheet_user3
                
            timesheet_obj   = Timesheet(False, from_date, to_date, task_filter, sheet_ids, list_user)
            timesheet_obj.parse(sheet_user=sheet_user2)
            user_ids        = timesheet_obj.user_ids
            type_and_sheet_info = timesheet_obj.type_and_sheet_info
            eng_type_ids    = timesheet_obj.eng_type_ids
            team_ids        = timesheet_obj.team_ids
            time_off_info   = timesheet_obj.time_off
            config_obj.get_list_holiday(is_parse=True)
            holidays  = config_obj.holidays
            info            = {}
            # caculate timeoff by week/month
            timeoff_info_2 = {}
            for user_id in time_off_info:
                for date, week, timeoff_per_day, obj in time_off_info[user_id]:
                    if filter == 'monthly':
                        name     = get_month_name_of_date(date)
                    else:
                        name     = get_start_week_of_date(date)
                    if not  timeoff_info_2.get(user_id):
                        timeoff_info_2[user_id] = {}
                    if not timeoff_info_2[user_id].get(name):
                        timeoff_info_2[user_id][name] = 0
                    timeoff_info_2[user_id][name] += timeoff_per_day
                    
            if filter == 'monthly':
                list_month   = get_work_month(from_date=from_date, to_date=to_date, holidays=holidays)
                cols_element = list_month
                list_sub_col       = []
                for col in cols_element:
                    month, year, max_hour = col
                    col_name    = DateTime.LIST_MONTH[month]
                    list_sub_col.append(col_name)
            else:
                list_week   = get_work_week(from_date=from_date, to_date=to_date, holidays=holidays)
                cols_element = list_week
                list_sub_col       = []
                for col in cols_element:
                    list_sub_col.append(col[0])
            
            for sheet_id in timesheet_obj.sheets:
                sheet_obj   = timesheet_obj.sheets[sheet_id]
                sheet_type = sheet_obj.sheet_type
                sheet_name  = sheet_obj.sheet_name
                for user_id in sheet_obj.resource:
                    for task_obj in sheet_obj.resource[user_id]:
                        user_name   = task_obj.user_name
                        eng_type    = eng_type_ids[user_ids[user_id].eng_type_id]
                        team_name   = team_ids[user_ids[user_id].team_id]
                        allocation  = task_obj.allocation
                        date        = task_obj.date
                        work_hour   = 8*(allocation)/100
                        work_hour   = round_num(work_hour)
                        if filter == 'monthly':
                            col_element = task_obj.month_name
                        else:
                            col_element  = task_obj.start_week
                        if not info.get(sheet_name):
                            info[sheet_name]  = {'resource': {}, 'total': {}, 
                                                 'sheet_id': sheet_id, 'total_row': 0, 
                                                 'sheet_type': sheet_type}
                             
                        if not info[sheet_name]['resource'].get(user_name):
                            info[sheet_name]['resource'][user_name]  = {'eng_type': eng_type, 
                                                                        'team': team_name,
                                                                        'timesheet': {},
                                                                        'user_id': user_id, 
                                                                        'total': 0} 
                        for element in cols_element:
                            if filter == 'monthly':
                                month, year, max_hour = element
                                col_name    = DateTime.LIST_MONTH[month]
                            else:
                                col_name, max_hour = element
                            if not info[sheet_name]['resource'][user_name]['timesheet'].get(col_name):
                                info[sheet_name]['resource'][user_name]['timesheet'][col_name]  = {'work_hour': 0,
                                                                                                   'max_hour': max_hour,
                                                                                                   'href': ''
                                                                                                   }
                            if not info[sheet_name]['total'].get(col_name):
                                info[sheet_name]['total'][col_name]  = 0
                        # info[sheet_name]['resource'][user_name]['total']  += work_hour
                        # info[sheet_name]['resource'][user_name]['total']  = round_num(info[sheet_name]['resource'][user_name]['total'])
                        info[sheet_name]['resource'][user_name]['timesheet'][col_element]['work_hour']  += work_hour
                        info[sheet_name]['resource'][user_name]['timesheet'][col_element]['work_hour']  = round_num(info[sheet_name]['resource'][user_name]['timesheet'][col_element]['work_hour'])
                        start, end = calculate_start_end_date_by_option(date, from_date, to_date, filter)
                        href = '%s?%s'%(Route.DETAIL, convert_request_dict_to_url(request_dict, [[SessionKey.USERS, [user_name]],
                                                                                                            [SessionKey.TASK_FILTER, task_filter],
                                                                                                            [SessionKey.SHEETS, [sheet_id]],
                                                                                                            [SessionKey.FROM, start],
                                                                                                            [SessionKey.TO, end],
                                                                                                            [SessionKey.MODE, 'view']
                                                                                                            ]))
                        info[sheet_name]['resource'][user_name]['timesheet'][col_element]['href']  = href
            
            if cost == 'cost':
                self.calculate_cost_project_timesheet(timesheet_info=info, timeoff_info=timeoff_info_2)
            # caculate total of sheet
            for sheet_name in info:
                sheet_type = info[sheet_name]['sheet_type']
                for user_name in info[sheet_name]['resource']:
                    for col_name in info[sheet_name]['resource'][user_name]['timesheet']:
                        work_hour = info[sheet_name]['resource'][user_name]['timesheet'][col_name]['work_hour']
                        max_hour = info[sheet_name]['resource'][user_name]['timesheet'][col_name]['max_hour']
                        if not type_and_sheet_info[sheet_type].get('total'):
                            type_and_sheet_info[sheet_type]['total'] = {}
                        if not type_and_sheet_info[sheet_type]['total'].get(col_name):
                            type_and_sheet_info[sheet_type]['total'][col_name] = 0
                        if not type_and_sheet_info[sheet_type]['total'].get('total_row'):
                            type_and_sheet_info[sheet_type]['total']['total_row'] = 0
                        if work_hour > max_hour:
                            info[sheet_name]['total'][col_name]  += max_hour
                            info[sheet_name]['total_row'] += max_hour
                            info[sheet_name]['resource'][user_name]['total'] += max_hour
                            type_and_sheet_info[sheet_type]['total'][col_name] += max_hour
                            type_and_sheet_info[sheet_type]['total']['total_row'] += max_hour
                        else:
                            info[sheet_name]['total'][col_name]  += work_hour
                            info[sheet_name]['total_row'] += work_hour
                            info[sheet_name]['resource'][user_name]['total'] += work_hour
                            type_and_sheet_info[sheet_type]['total'][col_name] += work_hour
                            type_and_sheet_info[sheet_type]['total']['total_row'] += work_hour
                            
                        info[sheet_name]['total'][col_name]  = round_num(info[sheet_name]['total'][col_name])
                        info[sheet_name]['total_row']  = round_num(info[sheet_name]['total_row'])
                        info[sheet_name]['resource'][user_name]['total']  = round_num(info[sheet_name]['resource'][user_name]['total'])
                        type_and_sheet_info[sheet_type]['total']['total_row']  = round_num(type_and_sheet_info[sheet_type]['total']['total_row'])
                        type_and_sheet_info[sheet_type]['total'][col_name]  = round_num(type_and_sheet_info[sheet_type]['total'][col_name])
            total    = 0
            no_enought   = 0
            
            if is_caculate or mode == 'sheet_user':
                remove_sheet = []
                for sheet_name in info:
                    sheet_id = info[sheet_name]['sheet_id']
                    if sheet_user2.get(sheet_id):
                        for user_name in sheet_user2[sheet_id]:
                            resource_info = info[sheet_name]['resource']
                            if not resource_info.get(user_name):
                                no_enought += 1
                                total += 1
                                if not info[sheet_name]['resource'].get(user_name):
                                    info[sheet_name]['resource'][user_name]  = {'eng_type': '', 
                                                                                'team': '',
                                                                                'timesheet': {}} 
                                for element in cols_element:
                                    if filter == 'monthly':
                                        month, year, max_hour = element
                                        col_name    = DateTime.LIST_MONTH[month]
                                    else:
                                        col_name, max_hour = element
                                    if not info[sheet_name]['resource'][user_name]['timesheet'].get(col_name):
                                        info[sheet_name]['resource'][user_name]['timesheet'][col_name]  = {'work_hour': 0,
                                                                                                           'max_hour': max_hour,
                                                                                                           'href': ''
                                                                                                           }
                                    timeoff_per_sheet = 0
                                    if timeoff_info_2.get(user_id) and timeoff_info_2[user_id].get(col_name):
                                        timeoff_hour = timeoff_info_2[user_id][col_name]
                                        if sheet_user3.get(user_id):
                                            number_sheet = len(sheet_user3[user_id])
                                            timeoff_per_sheet = timeoff_hour / number_sheet
                                            timeoff_per_sheet = round_num(timeoff_per_sheet)
                                    resource_info[user_name]['timesheet'][col_name]['max_hour'] -= timeoff_per_sheet
                            else:
                                is_enought = True 
                                user_id = resource_info[user_name]['user_id']
                                for col_name in resource_info[user_name]['timesheet']:
                                    timeoff_per_sheet = 0
                                    if timeoff_info_2.get(user_id) and timeoff_info_2[user_id].get(col_name):
                                        timeoff_hour = timeoff_info_2[user_id][col_name]
                                        if sheet_user3.get(user_id):
                                            number_sheet = len(sheet_user3[user_id])
                                            timeoff_per_sheet = timeoff_hour / number_sheet
                                            timeoff_per_sheet = round_num(timeoff_per_sheet)
                                    resource_info[user_name]['timesheet'][col_name]['max_hour'] -= timeoff_per_sheet
                                    work_hour = resource_info[user_name]['timesheet'][col_name]['work_hour']
                                    max_hour = resource_info[user_name]['timesheet'][col_name]['max_hour']
                                    if max_hour != work_hour:
                                        is_enought = False
                                        break
                                if not is_enought:
                                    no_enought += 1
                                total += 1
                    else:
                        remove_sheet.append(sheet_name)
                for name in remove_sheet:
                    del info[name]
            result = (info, list_sub_col, no_enought, total, type_and_sheet_info, granted_info)
            return result
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]  
    
    def get_resource_and_role_name(self):
        user_name = session[SessionKey.USERNAME]
        email = '%s@savarti.com'%user_name
        config_obj = Configuration()
        role_name = Role.USER
        list_role = [Role.USER]
        user_id, name = config_obj.get_user_by_email(email)
        
        if user_id:
            role_name2, list_role2 = config_obj.get_role_by_user_id(user_id)
            if role_name2:
                role_name = role_name2
            if len(list_role):
                list_role = list_role2
        return user_id, name, role_name, list_role
        
    def authenticate_account(self, username, password, remember=0):
        result = check_domain_password(username, password)
        if result[0]:
            session[SessionKey.USERNAME] = username
            session[SessionKey.PASSWORD] = password
            session[SessionKey.IS_LOGIN] = True
            if remember:
                save_password(password)
            user_id, name, role_name, list_role = self.get_resource_and_role_name()
            if user_id == None or name == None:
                return [False, 'User "%s" does not exist.'%username]
            session[SessionKey.RESOURCE_NAME] = name
            session[SessionKey.USER_ID] = user_id
            session[SessionKey.ROLE_NAME] = role_name
            session[SessionKey.LIST_ROLE_NAME] = list_role
        else:
            session[SessionKey.IS_LOGIN] = False
        return result
    
    def save_sheet_setting(self, request_dict):
        try:
            config_obj = Configuration()
            config_obj.set_attr(updated_by=session[SessionKey.USERNAME])
            for sheet_id in request_dict:
                config_obj.set_attr(sheet_id=sheet_id)
                if request_dict[sheet_id].get('is_active'):
                    is_active = request_dict[sheet_id]['is_active']
                    config_obj.set_attr(is_active=is_active)
                    config_obj.update_sheet_active()
                if request_dict[sheet_id].get('sheet_type'):
                    sheet_type_id = request_dict[sheet_id]['sheet_type']
                    config_obj.set_attr(sheet_type_id=sheet_type_id)
                    config_obj.update_type_of_sheet()
                if request_dict[sheet_id].get('resource'):
                    # add user
                    add_ids = request_dict[sheet_id]['resource']['add']
                    add_record = []
                    for user_id in add_ids:
                        add_record.append([sheet_id, user_id])
                    if len(add_record):
                        config_obj.add_user_of_sheet(add_record)
                    # remove user
                    remove_ids = request_dict[sheet_id]['resource']['remove']
                    remove_record = []
                    for user_id in remove_ids:
                        remove_record.append([sheet_id, user_id])
                    if len(remove_record):
                        config_obj.remove_users_of_sheet(remove_record)
            return 1, ''
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]
    
    def save_other_setting(self, request_dict):
        try:
            config_obj = Configuration()
            config_obj.set_attr(updated_by=session[SessionKey.USERNAME])
            for key, val in request_dict['info'].items():
                config_obj.set_attr(config_name=key,
                                    config_value=val)
                config_obj.update_analyze_config()
            return 1, ''
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]
        
    def get_sync_sheet(self, request_dict={}):
        sheet_types, sheet_type_id = self.get_sheet_type_info()
        config_obj  = Configuration()
        config_obj.get_sheet_config(is_parse=True, is_active=None)
        sheet_in_db = config_obj.sheets
        analyze_config_info = config_obj.get_analyze_config()
        token   = analyze_config_info[AnalyzeCFGKeys.TOKEN]
        sms_obj = SmartSheets(token=token)
        sms_obj.connect_smartsheet()
        sheets = sms_obj.get_sheet_name_and_validate_column(sheet_in_db=sheet_in_db)
        info = {'sheet_types': sheet_types,
                'sheets' : sheets
                }
        return info
    
    def get_information_to_report_timesheet(self, request_dict=None):
        missing_method = False
        if request_dict:
            try:
                from_date   = request_dict[SessionKey.FROM]
                to_date     = request_dict[SessionKey.TO]
                sheet_ids   = request_dict[SessionKey.SHEETS]
            except KeyError:
                missing_method = True
        if not sheet_ids or not to_date or not from_date or missing_method:
            return []
        rt_info, list_week, unuse1, unuse2, unuse3, unuse4, unuse5 = self.get_resource_timesheet_info(from_date=from_date, 
                                                                                                   to_date=to_date, 
                                                                                                   sheet_ids=sheet_ids, 
                                                                                                   task_filter='current',
                                                                                                   filter='weekly')
        info = {}
        user_email, users, user_ids, others_name = self.get_all_resource_information()
        list_exist_user = []
        for eng_type in rt_info:
            for team in rt_info[eng_type]:
                for resource in rt_info[eng_type][team]:
                    list_exist_user.append(resource)
                    for week in rt_info[eng_type][team][resource]:
                        if week == 'leader_name':
                            continue
                        max_hours = rt_info[eng_type][team][resource][week]['max_hour']
                        sheets = rt_info[eng_type][team][resource][week]['sheets']
                        work_hours = rt_info[eng_type][team][resource][week]['summary'][0]
                        timeoff = rt_info[eng_type][team][resource][week]['summary'][1]
                        if timeoff + work_hours != max_hours:
                            if not info.get(week):
                                info[week] = {}
                            leader_id = users[resource].leader_id
                            resource_mail = users[resource].email
                            if leader_id:
                                leader_email = user_ids[leader_id].email
                            else:
                                leader_email = SettingKeys.NA_VALUE
                            if not info[week].get(leader_email):
                                info[week][leader_email] = []
                            detail = ''
                            for sheet in sheets:
                                detail += '%s(%s), '%(sheet, sheets[sheet][0])
                            info[week][leader_email].append({
                                'resource': resource,
                                'resource_mail': resource_mail,
                                'work_hours': work_hours,
                                'timeoff': timeoff,
                                'total': work_hours + timeoff,
                                'detail': detail})
        #add user don't have task in smartsheet
        config_obj      = Configuration()
        config_obj.get_list_holiday(is_parse=True)
        holidays  = config_obj.holidays
        list_week   = get_work_week(from_date=from_date, to_date=to_date, holidays=holidays)
        config_obj.get_list_timeoff(is_parse=True, start_date=from_date, end_date=to_date)
        time_off_info    = config_obj.time_off
        timeoff_info_2 = {}
        for user_id in time_off_info:
            for date, week, timeoff_per_day, obj in time_off_info[user_id]:
                name     = get_start_week_of_date(date)
                if not  timeoff_info_2.get(user_id):
                    timeoff_info_2[user_id] = {}
                if not timeoff_info_2[user_id].get(name):
                    timeoff_info_2[user_id][name] = 0
                timeoff_info_2[user_id][name] += timeoff_per_day
        for resource, resource_obj in users.items():
            user_id = resource_obj.user_id
            if resource_obj.is_active:
                if resource not in list_exist_user:
                    for week, max_hours in list_week:
                        work_hours = 0
                        timeoff = 0
                        if timeoff_info_2.get(user_id):
                            if timeoff_info_2[user_id].get(week):
                                timeoff = timeoff_info_2[user_id][week]
                        if not info.get(week):
                            info[week] = {}
                        leader_id = users[resource].leader_id
                        resource_mail = users[resource].email
                        if leader_id:
                            leader_email = user_ids[leader_id].email
                        else:
                            leader_email = SettingKeys.NA_VALUE
                        if not info[week].get(leader_email):
                            info[week][leader_email] = []
                        detail = ''
                        info[week][leader_email].append({
                            'resource': resource,
                            'resource_mail': resource_mail,
                            'work_hours': 0,
                            'timeoff': timeoff,
                            'total': work_hours + timeoff,
                            'detail': detail})
        return info
        
    def update_sync_sheet(self, request_dict):
        try:
            info = request_dict['info']
            config_obj  = Configuration()
            config_obj.set_attr(updated_by  = session[SessionKey.USERNAME])
            config_obj.get_sheet_type_info(is_parse=True)
            sheet_type_info = config_obj.sheet_type
            user_name = session[SessionKey.USERNAME]
            for element in info:
                sheet_name = element[0]
                sheet_type = element[1]
                is_active = element[2]
                is_valid = element[3]
                try:
                    sheet_type_id  = sheet_type_info[sheet_type]
                except KeyError:
                    sheet_type_id  = sheet_type_info[SettingKeys.NA_VALUE]
                config_obj.set_attr(sheet_name      = sheet_name,
                                    sheet_type_id   = str(sheet_type_id),
                                    latest_modified = DefaulteValue.DATETIME,
                                    is_active       = str(is_active),
                                    is_valid       = str(is_valid),
                                    )
                if config_obj.is_exist_sheet():
                    config_obj.update_sheet()
                else:
                    self.record_to_log(0, LogKeys.ACTION_ADD_SHEET, '', sheet_name, user_name)
                    config_obj.add_sheet()
                
            return 1, 'Synchronize successfully'
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]
        
    def send_report(self, request_dict):
        try:
            user_name = session[SessionKey.USERNAME]
            password = session[SessionKey.PASSWORD]
            if request_dict.get(SettingKeys.NA_VALUE):
                message = 'Email error: NA'
                println(message, 'error')
                return 0, message
            
            config_obj = Configuration()
            user_role = config_obj.get_user_role()
            #PM email
            user_email, users, user_ids, others_name = self.get_all_resource_information()
            pm_cc = []
            for elm in user_role:
                user_id = elm[DbHeader.USER_ID]
                role_name = elm[DbHeader.ROLE_NAME] 
                if role_name == Role.PM:
                    email =  user_ids[user_id].email
                    if email != '%s@savarti.com'%user_name:
                        pm_cc.append(email)
                        
            for lead_email in request_dict:
                body = request_dict[lead_email]['body']
                cc = request_dict[lead_email]['cc']
                cc_list = cc.split('; ')    
                cc_list = cc_list + pm_cc
                send_mail_status = send_mail(user_name, password, [lead_email], cc_list, 'Report Timesheet', body)
                if not send_mail_status[0]:
                    message = 'Fail to send report.'
                    println(message, 'error')
                    return 0, message
                
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, 'Fail to send report.'
        return 1, 'Send Successfully.'
    
    def group_productivity_setting_by_user(self, from_date, to_date, list_sub_col, team_ids, 
                                           eng_type_ids, users, others_name, user_ids):
        result = {}
        procuctivity_setting = self.get_productivity_setting(from_date, to_date)
        for date_obj, data in procuctivity_setting.items():
            start_week = convert_date_to_string(date_obj, '%Y-%m-%d')
            for user_name, user_data in  data.items():
                try:
                    user_id = users[user_name].user_id
                except KeyError:
                    try:
                        user_id = others_name[user_name]
                    except KeyError:
                        user_id = users[SettingKeys.NA_VALUE].user_id
                eng_type    = eng_type_ids[user_ids[user_id].eng_type_id]
                team_name   = team_ids[user_ids[user_id].team_id]
                #
                # #Skip user not in PROCDUCTIVITY_ENG
                # if eng_type not in OtherKeys.PROCDUCTIVITY_ENG:
                #     continue
                #get leader name
                leader_id = users[user_name].leader_id
                if leader_id:
                    leader_name = user_ids[leader_id].user_name
                else:
                    leader_name = SettingKeys.NA_VALUE
                    
                if not result.get(user_name):
                    result[user_name] = {'eng_type': eng_type,
                                        'team_name': team_name,
                                        'leader_name': leader_name,
                                        'timesheet': {}}
                if not result[user_name]['timesheet'].get(start_week):
                    result[user_name]['timesheet'][start_week] = {}
                result[user_name]['timesheet'][start_week] = user_data
        return result
    
    def get_resource_productivity_info(self, request_dict=None, from_date=None, to_date=None, sheet_ids=None, 
                                    filter='weekly', task_filter='both', list_user=None):
        try:
            missing_method = False
            if request_dict:
                try:
                    from_date   = request_dict[SessionKey.FROM]
                    to_date     = request_dict[SessionKey.TO]
                    sheet_ids   = request_dict[SessionKey.SHEETS]
                    if request_dict.get(SessionKey.TASK_FILTER):
                        task_filter = request_dict[SessionKey.TASK_FILTER]
                    if request_dict.get(SessionKey.USERS):
                        list_user = request_dict[SessionKey.USERS]
                except KeyError:
                    missing_method = True
            if not filter or not sheet_ids or not to_date or not from_date or missing_method:
                return ({}, [], 0, 0, 0, 0, 0)
            timesheet_obj   = Timesheet(False, from_date, to_date, task_filter, sheet_ids, list_user)
            timesheet_obj.parse()
            user_ids        = timesheet_obj.user_ids
            eng_type_ids    = timesheet_obj.eng_type_ids
            team_ids        = timesheet_obj.team_ids
            time_off_info   = timesheet_obj.time_off
            config_obj      = Configuration()
            config_obj.get_list_holiday(is_parse=True)
            holidays  = config_obj.holidays
            
            user_email, users, user_ids, others_name = self.get_all_resource_information()
            info            = {}
            
            if filter == 'monthly':
                list_month   = get_work_month(from_date=from_date, to_date=to_date, holidays=holidays)
                cols_element = list_month
                list_sub_col       = []
                for col in cols_element:
                    month, year, max_hour = col
                    col_name    = DateTime.LIST_MONTH[month]
                    list_sub_col.append(col_name)
            else:
                list_week   = get_work_week(from_date=from_date, to_date=to_date, holidays=holidays)
                cols_element = list_week
                list_sub_col       = []
                for col in cols_element:
                    list_sub_col.append(col[0])
            productivity_config_info = self.group_productivity_setting_by_user(from_date, to_date, 
                                                                               list_sub_col, team_ids, 
                                                                               eng_type_ids, users, 
                                                                               others_name, user_ids)
            # caculate timeoff by week/month
            timeoff_info_2 = {}
            for user_id in time_off_info:
                for date, week, timeoff_per_day, obj in time_off_info[user_id]:
                    if filter == 'monthly':
                        name     = get_month_name_of_date(date)
                    else:
                        name     = get_start_week_of_date(date)
                    if not  timeoff_info_2.get(user_id):
                        timeoff_info_2[user_id] = {}
                    if not timeoff_info_2[user_id].get(name):
                        timeoff_info_2[user_id][name] = 0
                    timeoff_info_2[user_id][name] += timeoff_per_day
            list_exist_user = []
            for sheet_id in timesheet_obj.sheets:
                sheet_obj   = timesheet_obj.sheets[sheet_id]
                sheet_name  = sheet_obj.sheet_name
                sheet_type  = sheet_obj.sheet_type
                if sheet_type == SettingKeys.NA_VALUE:
                    #skip sheet type NA
                    print ('Skip sheet "%s" - Sheet type "NA"'%(sheet_name))
                    continue
                for user_id in sheet_obj.resource:
                    for task_obj in sheet_obj.resource[user_id]:
                        user_name   = task_obj.user_name
                        eng_type    = eng_type_ids[user_ids[user_id].eng_type_id]
                        team_name   = team_ids[user_ids[user_id].team_id]
                        task_date   = task_obj.date
                        allocation  = task_obj.allocation
                        work_hour   = 8*(allocation)/100
                        
                        work_hour   = round_num(work_hour)
                        if filter == 'monthly':
                            col_element = task_obj.month_name
                        else:
                            col_element  = task_obj.start_week
#                         if timeoff_info_2.get(user_id):
#                             if timeoff_info_2[user_id].get(col_element):
#                                 timeoff = timeoff_info_2[user_id][col_element]
                        
                        #Skip user not in PROCDUCTIVITY_ENG
                        # if eng_type not in OtherKeys.PROCDUCTIVITY_ENG:
                        #     continue
                        #get leader name
                        leader_id = users[user_name].leader_id
                        if leader_id:
                            leader_name = user_ids[leader_id].user_name
                        else:
                            leader_name = SettingKeys.NA_VALUE
                        
                        if not info.get(leader_name):
                            info[leader_name] = {}
                        
                        if not info[leader_name].get(user_name):
                            list_exist_user.append(user_name)
                            info[leader_name][user_name] = {
                                'eng_type': eng_type,
                                'team_name': team_name,
                                'timesheet': {}
                                }
                            for element in cols_element:
                                timeoff     = 0
                                if filter == 'monthly':
                                    month, year, max_hour = element
                                    col_name    = DateTime.LIST_MONTH[month]
                                else:
                                    col_name, max_hour = element
                                if timeoff_info_2.get(user_id):
                                    if timeoff_info_2[user_id].get(col_name):
                                        timeoff = timeoff_info_2[user_id][col_name]
                                                
                                info[leader_name][user_name]['timesheet'][col_name] = {
                                    'timeoff' : timeoff,
                                    'sheet_type': {},
                                    'max_hours': max_hour
                                    }
                                for element in OtherKeys.PROCDUCTIVITY_SHEET_TYPE:
                                    if element in ['Non-WH']:
                                        
                                        info[leader_name][user_name]['timesheet'][col_name]['sheet_type'][element] = max_hour - timeoff
                                    else:
                                        info[leader_name][user_name]['timesheet'][col_name]['sheet_type'][element] = 0
                            
                        info[leader_name][user_name]['timesheet'][col_element]['sheet_type'][sheet_type] += work_hour
                        info[leader_name][user_name]['timesheet'][col_element]['sheet_type']['Non-WH'] -= work_hour
                        #info[leader_name][user_name]['timesheet'][col_element]['timeoff'] = timeoff
                        if info[leader_name][user_name]['timesheet'][col_element]['sheet_type'][sheet_type] > info[leader_name][user_name]['timesheet'][col_element]['max_hours']:
                            info[leader_name][user_name]['timesheet'][col_element]['sheet_type'][sheet_type] = info[leader_name][user_name]['timesheet'][col_element]['max_hours']
                        
                        if info[leader_name][user_name]['timesheet'][col_element]['sheet_type']['Non-WH'] <= 0:
                            info[leader_name][user_name]['timesheet'][col_element]['sheet_type']['Non-WH'] = 0
            
            # Add user missing task
            if not list_user:
                for resource, resource_obj in users.items():
                    user_id = resource_obj.user_id
                    if resource_obj.is_active:
                        if resource not in list_exist_user:
                            user_name   = resource_obj.user_name
                            eng_type    = eng_type_ids[user_ids[user_id].eng_type_id]
                            team_name   = team_ids[user_ids[user_id].team_id]
                            leader_id = users[user_name].leader_id
                            if leader_id:
                                leader_name = user_ids[leader_id].user_name
                            else:
                                leader_name = SettingKeys.NA_VALUE
                            
                            if not info.get(leader_name):
                                info[leader_name] = {}
                            if not info[leader_name].get(user_name):
                                info[leader_name][user_name] = {
                                    'eng_type': eng_type,
                                    'team_name': team_name,
                                    'timesheet': {}
                                    }
                                for element in cols_element:
                                    timeoff     = 0
                                    if filter == 'monthly':
                                        month, year, max_hour = element
                                        col_name    = DateTime.LIST_MONTH[month]
                                    else:
                                        col_name, max_hour = element
                                                    
                                    info[leader_name][user_name]['timesheet'][col_name] = {
                                        'timeoff' : timeoff,
                                        'sheet_type': {},
                                        'max_hours': max_hour
                                        }
                                    for element in OtherKeys.PROCDUCTIVITY_SHEET_TYPE:
                                        if element in ['Non-WH']:
                                            info[leader_name][user_name]['timesheet'][col_name]['sheet_type'][element] = max_hour - timeoff
                                        else:
                                            info[leader_name][user_name]['timesheet'][col_name]['sheet_type'][element] = 0
            
            return info, list_sub_col, cols_element, productivity_config_info
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]
    
    def export_productiviity(self, request_dict):
        try:
            data = request_dict['data']
            headers = request_dict['headers']
            wb = Workbook()
            file_name = 'Productivity.xls'
            output_path   = os.path.join(config.WORKING_PATH, file_name)
            file_name2 = 'Productivity.xlsx'
            output_path2   = os.path.join(config.WORKING_PATH, file_name2)
            if os.path.exists(output_path):
                os.remove(output_path)
            start_col, start_row = (0, 0)
            
            # style 
            color_style = defined_color()
            style_header = color_style['lime']
            
            # export daily timesheet
            
            prd_wb = wb.add_sheet('Productivity')
            row_num, col_num = (0, 0)
            count_2 = 0
            for idx in range(2, len(headers['1'])):
                prd_wb.col(col_num).width = 256 * 14
                header = headers['1'][idx]
                if count_2 > 0:
                    count_2 -= 1
                    col_num += 1
                    continue
                if idx > 5:
                    prd_wb.write_merge(row_num, row_num, col_num, col_num + 6, header, style_header)
                    count_2 = 6
                else:
                    prd_wb.write_merge(row_num, row_num + 1, col_num, col_num, header, style_header)
                col_num += 1
            col_num = 4
            row_num += 1
            
            for idx2 in range(6, len(headers['2'])):
                header2 = headers['2'][idx2]
                prd_wb.write(row_num, col_num, header2, color_style['gray25'])
                col_num += 1
            col_num = start_col
            row_num += 1

            for row in data:
                for idx3 in range(2, len(row)):
                    val = row[idx3]
                    prd_wb.write(row_num, col_num, val)
                    col_num += 1
                col_num = start_col
                row_num += 1
#             color_wb = wb.add_sheet('Color')
#             row_num, col_num = (0, 0)
#             for color in color_style:
#                 color_wb.write(row_num, col_num, color, color_style[color])
#                 col_num = start_col
#                 row_num += 1
            wb.save(output_path)
            
            x2x = XLS2XLSX(output_path)
            remove_path(output_path)
            x2x.to_xlsx(output_path2)
            os.system('start %s'%(output_path2))
            return 1, file_name2
        
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]
        
    def import_productivity(self, file_name, from_date, to_date):
        try:
            config_obj      = Configuration()
            config_obj.get_list_holiday(is_parse=True)
            holidays  = config_obj.holidays
            list_week   = get_work_week(from_date=from_date, to_date=to_date, holidays=holidays)
            week_std_hour = {}
            weeks = []
            for row in list_week:
                week, hour = row
                weeks.append(week)
                week_std_hour[week] = hour
            
            file_path   = os.path.join(os.path.join(config.WORKING_PATH, 'upload'), file_name)
            df          = pd.read_excel (file_path, sheet_name='Productivity', engine='openpyxl', header=[0, 1])
            df_key = {}
            output = []
            list_header_1 = []
            for col_elm in df.columns.tolist():
                header_1, header_2 = col_elm
                if header_1 not in list_header_1:
                    list_header_1.append(header_1)
                if not df_key.get(header_1):
                    df_key[header_1] = []
                df_key[header_1].append(header_2)
            count_head = 0
            for h1 in list_header_1:
                count_head += 1
                h1_str = convert_date_to_string(h1, format_str='%Y-%m-%d')
                std_hour = 0
                if count_head < 5 or h1_str in weeks:
                    if week_std_hour.get(h1_str):
                        std_hour = week_std_hour.get(h1_str)
                        del week_std_hour[h1_str]
                    for h2 in df_key[h1]:
                        count = 0
                        for row_val in df[h1][h2]:
                            if str(row_val) in SettingKeys.EMPTY_CELL:
                                row_val = ''
                            try:
                                unuse = output[count]
                            except IndexError:
                                output.append([])
                            output[count].append([row_val, std_hour])
                            count += 1
            if len(week_std_hour):
                string = ', '.join(week_std_hour.keys())
                return 0, 'Missing data for %s'%string
            remove_path(file_path)
            return 1, output
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]
        
    def get_current_version(self):
        version = g.version
        return version
    
    def is_in_require_role(self, list_role):
        user_role = session[SessionKey.LIST_ROLE_NAME]
        result = False
        for role_name in user_role:
            if role_name in list_role:
                result = True
        # result = True 
        return result
    
    def add_current_version_of_user(self):
        config_obj = Configuration()
        user_id = session[SessionKey.USER_ID]
        current_version     = g.version
        config_obj.set_attr(user_id = user_id,
                            version = current_version)
        if config_obj.check_exist_user_version():
            config_obj.update_user_version()
        else:
            config_obj.add_user_version()
        session[SessionKey.IS_UPDATE_VERSION] = 1
        session[SessionKey.USER_VERSION] = current_version
        
    def check_version (self):
        current_version = g.version
        notify_ver =  session.get(SessionKey.IS_NOTIFY_VERSION)
        if notify_ver == 1 or notify_ver == None:
            config_obj = Configuration()
            o_config = config_obj.get_other_config_info()
            latest_ver = o_config.get(OtherCFGKeys.LATEST_VERSION)
            if latest_ver:
                down_link  = o_config.get(OtherCFGKeys.VERSION_DOWNLOAD)
                if current_version == latest_ver:
                    result = [0, '']
                else:
                    result = [1, down_link]
            else:
                result = [0, '']
        else:
            result = [0, '']
        session[SessionKey.IS_NOTIFY_VERSION] = 0
        # 0-> skip, 1-> notify | link 
        return result
    
    def lock_sync(self, request_dict):
        is_loading = request_dict.get('is_loading')
        config_obj      = Configuration()
        config_obj.get_sheet_config(is_parse=True)
        sheet_ids = config_obj.sheet_ids
        
        for sheet_id in sheet_ids:
            config_obj.set_attr(is_loading          = is_loading,
                                sheet_id            = sheet_id)
            config_obj.update_is_loading_of_sheet()
        return 1
    
    def update_user_role(self, request_dict):
        role_info = request_dict['role']
        user_role_info = request_dict['user_role']
        config_obj = Configuration()
        current_role = config_obj.get_list_role()
        current_user_role = config_obj.get_user_role()
        
        #add new role
        for role_name in role_info:
            if not config_obj.check_exist_role(role_name):
                config_obj.add_role(role_name)
        #remove missing role
        for elm in current_role:
            role_name = elm[DbHeader.ROLE_NAME]
            if role_name not in role_info:
                config_obj.remove_role(role_name)
        avail_id = {}
        #add new user role
        for elm in user_role_info:
            user_id = elm[0]
            role_id = elm[1]
            avail_id['%s-%s'%(user_id, role_id)] = 1
            if not config_obj.check_exist_user_role(user_id, role_id):
                config_obj.add_user_role(user_id, role_id)
        #remove missing user role
        for elm in current_user_role:
            user_id = elm[DbHeader.USER_ID]
            role_id = elm[DbHeader.ROLE_ID] 
            grp_id = '%s-%s'%(user_id, role_id)
            if not avail_id.get(grp_id):
                config_obj.remove_user_role(user_id, role_id)
        return 1
    
    def update_other_config(self, request_dict):
        other_config_info = request_dict['other_info']
        config_obj = Configuration()
        for elm in other_config_info:
            config_name = elm[0]
            config_value = elm[1]
            config_obj.set_attr(config_name=config_name, config_value=config_value)
            if config_obj.check_exist_config_info():
                config_obj.update_other_config_info()
        return 1
    
    def record_to_log(self, sheet_id, action_name, old_value, new_value, updated_by):
        log_obj = Log()
        log_obj.set_attr(
            sheet_id=sheet_id,
            action_name=action_name,
            old_value=old_value,
            new_value=new_value,
            updated_by=updated_by
            )
        log_obj.get_action_id()
        log_obj.add_log()
        
    def get_log_action(self):
        obj = Log()
        result = obj.get_action()
        return result
    
    def get_log_info(self, request_dict):
        obj = Log()
        from_date = request_dict[SessionKey.FROM]
        to_date = request_dict[SessionKey.TO]
        if request_dict.get(SessionKey.ACTIONS):
            action_id = request_dict[SessionKey.ACTIONS]
        else:
            action_id = None
        result = obj.get_log(from_date, to_date, action_id)
        return result
    
    def parse_smarsheet_and_update_task_effective_rate(self, list_sheet_id=None, log=None):
        if log:
            write_message_into_file(log, 'Starting parse smartsheet\n')
        println('Starting parse smartsheet', OtherKeys.LOGING_INFO)
        start_time = time.time()
        config_obj = Configuration()
        sheet_info  = config_obj.get_sheet_config(list_sheet_id)
        
        list_sheet  = []
        analyze_config_info = config_obj.get_analyze_config()
        token   = analyze_config_info[AnalyzeCFGKeys.TOKEN]
        for row in sheet_info:
            list_sheet.append((row[DbHeader.SHEET_NAME], int(row[DbHeader.SHEET_ID]), ))
        sms_obj = SmartSheetsEffective(list_sheet=list_sheet, log=log, token=token)
        sms_obj.connect_smartsheet()
        sms_obj.parse()
        config_obj.get_all_user_information()
        user_info = config_obj.users
        other_name_info = config_obj.others_name
        effective_obj    = DbEffectiveRate()
        total = len(sms_obj.info)
        count = 0
        missing_user = {}
        write_message_into_file(log, '%s\n'%('-'*75))
        println('%s'%('-'*75), OtherKeys.LOGING_INFO)
        for sheet_name in sms_obj.info:
            count += 1
            # save children_task only
            child_tasks         = sms_obj.info[sheet_name].children_task
            sheet_id            = sms_obj.info[sheet_name].sheet_id
            if log:
                write_message_into_file(log, '[%d/%d] Updating sheet: <span class="bold cl-blue">%s</span>\n'%(count, total, sheet_name))
            println('[%d/%d] Updating sheet: %s'%(count, total, sheet_name), OtherKeys.LOGING_INFO)
            
            effective_obj.set_attr(sheet_id    = sheet_id)
            effective_obj.remove_all_task_information_by_project_id()
            list_records_task   = []
            for child_task_obj in child_tasks:
                task_name       = child_task_obj.task_name
                start_date      = child_task_obj.start_date
                end_date        = child_task_obj.end_date
                duration        = child_task_obj.duration
                actual_duration        = child_task_obj.actual_duration
                actual_start_date = child_task_obj.actual_start_date
                actual_end_date = child_task_obj.actual_end_date
                assign_to       = child_task_obj.assign_to
                prefix_name     = child_task_obj.prefix_name
                try:
                    user_id = user_info[assign_to].user_id
                except KeyError:
                    try:
                        user_id = other_name_info[assign_to]
                    except KeyError:
                        missing_user[assign_to] = ''
                        user_id = user_info[SettingKeys.NA_VALUE].user_id
                record  = (
                    str(sheet_id),
                    str(user_id),
                    task_name,
                    str(start_date),
                    str(end_date),
                    str(actual_start_date),
                    str(actual_end_date),
                    actual_duration,
                    duration,
                    prefix_name,
                    '')
                list_records_task.append(record)
            effective_obj.add_task(list_records_task)
        
            println('[%d/%d] Update database for %s - Done'%(count, total, sheet_name), OtherKeys.LOGING_INFO)
            if log:
                write_message_into_file(log, '[%d/%d] Update database for <span class="bold cl-blue">%s</span> - Done\n'%(count, total, sheet_name))
        
        write_message_into_file(log, '%s\n'%('-'*75))
        println('%s'%('-'*75), OtherKeys.LOGING_INFO)
        
        for user in missing_user:
            message = message_generate(MsgWarning.W002, user)
            println('Warning: %s'%(message), OtherKeys.LOGING_INFO)
            if log:
                write_message_into_file(log, 'Warning: %s\n'%(message))
        end_time = time.time()
        diff = int(end_time - start_time)
        minutes, seconds = diff // 60, diff % 60
        message = "Time: " + str(minutes) + ':' + str(seconds).zfill(2)
        println(message, OtherKeys.LOGING_INFO)
        if log:
            write_message_into_file(log, message  + '\n')
            
    def sync_effective_data(self, sheet_ids):
        '''
        
        ::param::
        ::result::
        '''
        try:
            log_file = os.path.join(config.WORKING_PATH, "EffectiveRate.log")
            if os.path.exists(log_file):
                os.remove(log_file)
            self.parse_smarsheet_and_update_task_effective_rate(list_sheet_id  = sheet_ids,
                                                 log            = log_file)
            println(Msg.M002, OtherKeys.LOGING_INFO)
            write_message_into_file(log_file, Msg.M002)
            time.sleep(2)
            return 1, Msg.M002
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            write_message_into_file(log_file, '[ERROR] %s'%(e.args[0]))
            return 1, '[ERROR] %s'%(e.args[0])
        
    def get_effective_rate(self, request_dict):
        '''
        
        ::param::
        ::result::
        '''
        
        effective_obj    = DbEffectiveRate()
        sheets = request_dict.get(SessionKey.SHEETS, [])
        config_obj = Configuration()
        config_obj.get_list_holiday(is_parse=True)
        holidays  = config_obj.holidays
        data = {}
        config_obj.get_all_user_information()
        user_ids = config_obj.user_ids
        config_obj.get_eng_level_info(is_parse=True)
        eng_level_info = config_obj.eng_level_ids
        config_obj.get_sheet_config(is_parse=True, is_active=True)
        sheet_ids = config_obj.sheet_ids
        projects = []
        for sheet_id in sheets:
            sheet_id = int(sheet_id)
            task_data = effective_obj.get_tasks(sheet_id)
            for row in task_data:
                task_name = row['task_name']
                user_id = row['user_id']
                start_date = row['start_date']
                end_date = row['end_date']
                actual_start_date = row['actual_start_date']
                actual_end_date = row['actual_end_date']
                actual_duration = row['actual_duration']
                duration        = row['duration']
                prefix_name     = row['prefix_name']
                user_name = user_ids[user_id].user_name
                level_id = user_ids[user_id].eng_level_id
                level = eng_level_info[level_id]
                sheet_name = sheet_ids[sheet_id]['sheet_name']
                #logic to calculate effective
                #calculate actual_duration
                if not actual_duration:
                    if actual_end_date and actual_end_date != '0000-00-00 00:00:00':
                        if start_date and start_date != '0000-00-00 00:00:00':
                            workday = get_work_days(start_date, actual_end_date, holidays)
                            if not len(workday):
                                continue
                            actual_duration = len(workday)
                        else:
                            #missing duration information
                            continue
                    else:
                        if end_date and end_date != '0000-00-00 00:00:00':
                            if start_date and start_date != '0000-00-00 00:00:00':
                                workday = get_work_days(start_date, end_date, holidays)
                                if not len(workday):
                                    continue
                                actual_duration = len(workday)
                            else:
                                #missing actual_duration information
                                continue
                        else:
                            continue
                
                #calculate duration
                if not duration:
                    if end_date and end_date != '0000-00-00 00:00:00':
                        if start_date and start_date != '0000-00-00 00:00:00':
                            workday = get_work_days(start_date, end_date, holidays)
                            duration = len(workday)
                        else:
                            #missing actual_duration information
                            continue
                    else:
                        continue
                
                effective_rate = int(float(duration) / float(actual_duration) * 100)
                #calculate from_date
                from_date = start_date
                
                #calculate to_date
                if actual_end_date != '0000-00-00 00:00:00':
                    to_date = actual_end_date
                else:
                    to_date = end_date
                if not data.get(user_name):
                    data[user_name] = {'level': level, 'effective_rate': None, 'projects': {}}
                if not data[user_name]['projects'].get(sheet_name):
                    projects.append(sheet_name)
                    data[user_name]['projects'][sheet_name] = {'from': None, 'to': None, 'effective_rate': None}
                
                #update from date
                if data[user_name]['projects'][sheet_name]['from'] == None:
                        data[user_name]['projects'][sheet_name]['from'] = from_date
                else:
                    if data[user_name]['projects'][sheet_name]['from'] == '0000-00-00 00:00:00':
                        data[user_name]['projects'][sheet_name]['from'] = from_date
                    elif from_date == '0000-00-00 00:00:00':
                        pass
                    else:
                        if compare_date(data[user_name]['projects'][sheet_name]['from'], from_date):
                            data[user_name]['projects'][sheet_name]['from'] = from_date
                #update to date
                if data[user_name]['projects'][sheet_name]['to'] == None:
                        data[user_name]['projects'][sheet_name]['to'] = to_date
                else:
                    if data[user_name]['projects'][sheet_name]['to'] == '0000-00-00 00:00:00':
                        data[user_name]['projects'][sheet_name]['to'] = to_date
                    elif to_date == '0000-00-00 00:00:00':
                        pass
                    else:
                        if compare_date(to_date, data[user_name]['projects'][sheet_name]['to']):
                            data[user_name]['projects'][sheet_name]['to'] = to_date
                if isinstance( data[user_name]['projects'][sheet_name]['to'], datetime.datetime):
                    data[user_name]['projects'][sheet_name]['to'] = convert_date_to_string(data[user_name]['projects'][sheet_name]['to'], '%Y-%m-%d')
                if isinstance( data[user_name]['projects'][sheet_name]['from'], datetime.datetime):
                    data[user_name]['projects'][sheet_name]['from'] = convert_date_to_string(data[user_name]['projects'][sheet_name]['from'], '%Y-%m-%d')
                
                #calculate percent
                if data[user_name]['projects'][sheet_name]['effective_rate'] == None:
                    data[user_name]['projects'][sheet_name]['effective_rate'] = effective_rate
                else:
                    data[user_name]['projects'][sheet_name]['effective_rate'] = (data[user_name]['projects'][sheet_name]['effective_rate'] + effective_rate ) / 2
                data[user_name]['projects'][sheet_name]['effective_rate'] = int(data[user_name]['projects'][sheet_name]['effective_rate'])
        for user_name in data:
            sheet_info = data[user_name]['projects']
            ls_eff = []
            for sheet_name in sheet_info:
                effective_rate = sheet_info[sheet_name]['effective_rate']
                if effective_rate not in [None, '']:
                    ls_eff.append(effective_rate)
            if ls_eff:
                avarage = int(sum(ls_eff) / len(ls_eff))
                data[user_name]['effective_rate'] = avarage
        projects = list(set(projects))
        result = [data, projects]
        return result
    
    def export_effective_rate(self, request_dict):
        data, sheets = self.get_effective_rate(request_dict)
        try:
            workbook = Workbook()
            file_name = 'Effective_Rate.xls'
            output_path   = os.path.join(config.WORKING_PATH, file_name)
            file_name2 = 'Effective_Rate.xlsx'
            output_path2   = os.path.join(config.WORKING_PATH, file_name2)
            if os.path.exists(output_path):
                os.remove(output_path)
            start_col, start_row = (0, 0)
            
            # style 
            color_style = defined_color()
            gray_ega_col = color_style['gray_ega']
            light_col = color_style['light_turquoise']
            orange_col = color_style['orange']
            tan_col = color_style['tan']
            gray25_col = color_style['gray25']
            # export daily timesheet
            
            wb = workbook.add_sheet('Effective Rate')
            row_num, col_num = (0, 0)
            #headers 
            wb.write(row_num, col_num, 'Resource', orange_col)
            wb.col(col_num).width = 256 * 14
            col_num += 1
            wb.write(row_num, col_num, 'Level', orange_col)
            wb.col(col_num).width = 256 * 14
            col_num += 1
            wb.write(row_num, col_num, 'Effective Rate', orange_col)
            wb.col(col_num).width = 256 * 14
            col_num += 1
            for sheet_name in sheets:
                wb.write(row_num, col_num, sheet_name, orange_col)
                wb.col(col_num).width = 256 * 14
                col_num += 1
            col_num = 0
            row_num += 1
            
            #tbody
            count = 0
            for resource in data:
                count += 1
                style = light_col
                if count % 2 == 0:
                    style = tan_col
                    
                level = data[resource]['level']
                sum_effective_rate = data[resource]['effective_rate']
                if sum_effective_rate:
                    sum_effective_rate = '%s%%'%sum_effective_rate
                eff_projects = data[resource]['projects']
                #row1
                wb.write_merge(row_num, row_num + 2, col_num, col_num, resource, style)
                col_num += 1
                wb.write(row_num, col_num, level, style)
                col_num += 1
                wb.write(row_num, col_num, sum_effective_rate)
                col_num += 1
                for sheet_name in sheets:
                    effective_rate = ''
                    from_date = ''
                    to_date = ''
                    if sheet_name in eff_projects:
                        effective_rate = eff_projects[sheet_name]['effective_rate']
                        from_date = eff_projects[sheet_name]['from']
                        to_date = eff_projects[sheet_name]['to']
                        if effective_rate:
                            effective_rate = '%s%%'%effective_rate
                        wb.write(row_num, col_num, effective_rate)
                    col_num += 1
                row_num += 1
                col_num = 1
                #row 2
                wb.write_merge(row_num, row_num + 1, col_num, col_num, 'Duration')
                col_num += 1
                wb.write(row_num, col_num, 'From')
                col_num += 1
                for sheet_name in sheets:
                    effective_rate = ''
                    from_date = ''
                    to_date = ''
                    if sheet_name in eff_projects:
                        effective_rate = eff_projects[sheet_name]['effective_rate']
                        from_date = eff_projects[sheet_name]['from']
                        to_date = eff_projects[sheet_name]['to']
                        wb.write(row_num, col_num, from_date, gray25_col)
                    col_num += 1
                row_num += 1
                col_num = 2
                #row 3
                wb.write(row_num, col_num, 'To')
                col_num += 1
                for sheet_name in sheets:
                    effective_rate = ''
                    from_date = ''
                    to_date = ''
                    if sheet_name in eff_projects:
                        effective_rate = eff_projects[sheet_name]['effective_rate']
                        from_date = eff_projects[sheet_name]['from']
                        to_date = eff_projects[sheet_name]['to']
                        wb.write(row_num, col_num, to_date, gray25_col)
                    col_num += 1
                row_num += 1
                col_num = 0

            workbook.save(output_path)
            x2x = XLS2XLSX(output_path)
            remove_path(output_path)
            x2x.to_xlsx(output_path2)
            os.system('start %s'%(output_path2))
            return 1, file_name2
        
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]
        