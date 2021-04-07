'''
Created on Feb 22, 2021

@author: toannguyen
'''
from src.models.smartsheet.smartsheet_model import SmartSheets
from src.models.database.database_model import Configuration, DbTask
from src.commons.enums import DbHeader, ExcelHeader, SettingKeys, DefaulteValue, SessionKey, \
                            DateTime, AnalyzeCFGKeys, Route, Role, OtherKeys
from src.commons.message import MsgError, MsgWarning, Msg, AnalyzeItem
from src.commons.utils import search_pattern, message_generate, println, remove_path, split_patern,\
                            get_prev_date_by_time_delta, get_work_week, convert_date_to_string,\
                            get_work_month, round_num, defined_color, \
                            get_work_days, write_message_into_file, convert_request_dict_to_url,\
                            str_to_date, get_end_week_of_date, get_start_week_of_date, get_month_name_of_date, \
                            calculate_start_end_date_by_option, check_domain_password, save_password, get_saved_password
                            
from src.models.timesheet.timesheet_model import Timesheet
from flask import session
from pprint import pprint
import pandas as pd
import os, sys
import config
import xlwt
import xlrd
import time
from xlwt import Workbook

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
        other_name_info = config_obj.other_name
        task_obj    = DbTask()
        total = len(sms_obj.info)
        count = 0
        missing_user = {}
        for sheet_name in sms_obj.info:
            count += 1
            # save children_task only
            child_tasks         = sms_obj.info[sheet_name].children_task
            sheet_id            = sms_obj.info[sheet_name].sheet_id
            latest_modified     = sms_obj.info[sheet_name].latest_modified
            
            is_parse            = sms_obj.info[sheet_name].is_parse
            if is_parse:
                if log:
                    write_message_into_file(log, '[%d/%d] Updating sheet: %s\n'%(count, total, sheet_name))
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
                    write_message_into_file(log, '[%d/%d] Update database for %s - Done\n'%(count, total, sheet_name))
            else:
                println('[%d/%d] Skip update database for %s'%(count, total, sheet_name), OtherKeys.LOGING_INFO)
                if log:
                    write_message_into_file(log, '[%d/%d] Skip update database for %s\n'%(count, total, sheet_name))
        for user in missing_user:
            message = message_generate(MsgWarning.W002, user)
            println('Warning: %s'%(message), OtherKeys.LOGING_INFO)
            if log:
                write_message_into_file(log, 'Warning: %s\n'%(message))
        end_time = time.time()
        diff = int(end_time - start_time)
        minutes, seconds = diff // 60, diff % 60
        println ("Time: " + str(minutes) + ':' + str(seconds).zfill(2))
        if log:
            write_message_into_file(log, "Time: " + str(minutes) + ':' + str(seconds).zfill(2)  + '\n')
    
    def convert_request_dict_to_url(self, request_dict):
        result = convert_request_dict_to_url(request_dict)
        return result
    
    def add_default_config_to_method_request(self, request_dict, more_option={}):
        for key, val in more_option.items():
            if not request_dict.get(key):
                request_dict[key] = val
        if not request_dict.get(SessionKey.FROM) or not request_dict.get(SessionKey.TO) or not request_dict.get(SessionKey.SHEETS):
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
            config_obj  = Configuration()
            for index in range(0, len(df[ExcelHeader.HOLIDAY])):
                date          = str(df[ExcelHeader.HOLIDAY][index])
                if date not in SettingKeys.EMPTY_CELL:
                    if not config_obj.is_exist_holiday(date):
                        config_obj.add_holiday(date)
            remove_path(file_path)
            return 1, Msg.M001
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
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

            teams  = config_obj.get_team_info(is_parse=True)
            teams_info = config_obj.team

            config_obj.set_attr(updated_by  = 'root')
            for index in range(0, len(df[ExcelHeader.RESOURCE])):
                resource          = str(df[ExcelHeader.RESOURCE][index]).strip()
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
            remove_path(file_path)
            return 1, Msg.M001
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]
        
    def get_list_sheet_name(self):
        config_obj      = Configuration()
        sheet_info      = config_obj.get_sheet_config()
        return sheet_info
    
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
        
    def get_daily_timesheet_info(self, request_dict=None, from_date=None, to_date=None, sheet_ids=None, task_filter=None, list_user=None):
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
                except KeyError:
                    missing_method = True
            if not task_filter or not sheet_ids or not to_date or not from_date or missing_method:
                return []
            result = []
            timesheet_obj   = Timesheet(from_date, to_date, task_filter, sheet_ids, list_user)
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
                        work_hour   = round_num(work_hour)
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
            
            write_message_into_file(log_file, Msg.M002)
            time.sleep(2)
            return 1, Msg.M002
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            write_message_into_file(log_file, '[ERROR] %s'%(e.args[0]))
            return 1, '[ERROR] %s'%(e.args[0])
    
    def get_newest_data_log(self):
        log_file = os.path.join(config.WORKING_PATH, "GetNewestData.log")
        result = ''
        if os.path.exists(log_file):
            with open(log_file, 'r') as log:
                result = log.read()
        result = result.replace('\n', '<br>')
        return result  
        
    def get_resource_timesheet_info(self, request_dict=None, from_date=None, to_date=None, sheet_ids=None, 
                                    filter='weekly', task_filter='both', mode='all', is_caculate=False):
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
                    
                except KeyError:
                    missing_method = True
            
            if not filter or not sheet_ids or not to_date or not from_date or missing_method:
                return ({}, [], 0, 0, 0, 0, 0)
            timesheet_obj   = Timesheet(from_date, to_date, task_filter, sheet_ids)
            timesheet_obj.parse()
            user_ids        = timesheet_obj.user_ids
            eng_type_ids    = timesheet_obj.eng_type_ids
            team_ids        = timesheet_obj.team_ids
            time_off_info   = timesheet_obj.time_off
            config_obj      = Configuration()
            config_obj.get_list_holiday(is_parse=True)
            holidays  = config_obj.holidays
            
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
            
            for sheet_id in timesheet_obj.sheets:
                sheet_obj   = timesheet_obj.sheets[sheet_id]
                sheet_name  = sheet_obj.sheet_name
                for user_id in sheet_obj.resource:
                    for task_obj in sheet_obj.resource[user_id]:
                        user_name   = task_obj.user_name
                        eng_type    = eng_type_ids[user_ids[user_id].eng_type_id]
                        team_name   = team_ids[user_ids[user_id].team_id]
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
                                                                                                             ]))
                        info[eng_type][team_name][user_name][col_element]['href'] = href

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
    
    def export_excel(self, from_date, to_date, sheet_ids):
        try:
            if not (from_date and to_date and sheet_ids):
                return 0, MsgError.E003
            wb = Workbook()
            file_name = 'Report.xls'
            output_path   = os.path.join(config.WORKING_PATH, file_name)
            if os.path.exists(output_path):
                os.remove(output_path)
            start_col, start_row = (0, 0)
            
            # style 
            color_style = defined_color()
            style_header = color_style['gray25']
            
            # export daily timesheet
            daily_timesheet_info = self.get_daily_timesheet_info(from_date=from_date, to_date=to_date, sheet_ids=sheet_ids, task_filter='current')
            daily_timesheet_wb = wb.add_sheet('Detail Timesheet')
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
            
            # export daily timesheet final
            daily_timesheet_info = self.get_daily_timesheet_info(from_date=from_date, to_date=to_date, sheet_ids=sheet_ids, task_filter='final')
            daily_timesheet_wb = wb.add_sheet('Detail Timesheet Final')
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
            
            #weekly resource
            weekly_resource_wb = wb.add_sheet('Weekly Resource')
            w_resource_info, list_week, no_missing, no_redundant, no_enought, count_overlap, total_resource = self.get_resource_timesheet_info(from_date=from_date, to_date=to_date, sheet_ids=sheet_ids, filter='weekly')
            start_col, start_row = (0, 0)
            row_num, col_num = (0, 0)
            # create  header
            list_header = ['Eng Type', 'Team', 'Resource'] + list_week
            for header in list_header:
                weekly_resource_wb.col(col_num).width = 256 * 14
                weekly_resource_wb.write(row_num, col_num, header, style_header)
                col_num += 1
            col_num = start_col
            row_num += 1
            for eng_type in w_resource_info:
                for team in w_resource_info[eng_type]:
                    for user_name in w_resource_info[eng_type][team]:
                        timesheet = w_resource_info[eng_type][team][user_name]
                        weekly_resource_wb.write(row_num, col_num, eng_type)
                        col_num += 1
                        weekly_resource_wb.write(row_num, col_num, team)
                        col_num += 1
                        weekly_resource_wb.write(row_num, col_num, user_name)
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
                            weekly_resource_wb.write(row_num, col_num, value, color_style[color])
                            col_num += 1
                        col_num = start_col
                        row_num += 1
            #end resource
            
            #monthly resource
            monthly_resource_wb = wb.add_sheet('Monthly Resource')
            m_resource_info, list_month, no_missing, no_redundant, no_enought, count_overlap, total_resource = self.get_resource_timesheet_info(from_date=from_date, to_date=to_date, sheet_ids=sheet_ids, filter='monthly')
            start_col, start_row = (0, 0)
            row_num, col_num = (0, 0)
            # create  header
            list_header = ['Eng Type', 'Team', 'Resource'] + list_month
            for header in list_header:
                monthly_resource_wb.col(col_num).width = 256 * 14
                monthly_resource_wb.write(row_num, col_num, header, style_header)
                col_num += 1
            col_num = start_col
            row_num += 1
            for eng_type in m_resource_info:
                for team in m_resource_info[eng_type]:
                    for user_name in m_resource_info[eng_type][team]:
                        timesheet = m_resource_info[eng_type][team][user_name]
                        monthly_resource_wb.write(row_num, col_num, eng_type)
                        col_num += 1
                        monthly_resource_wb.write(row_num, col_num, team)
                        col_num += 1
                        monthly_resource_wb.write(row_num, col_num, user_name)
                        col_num += 1
                        for column in list_month:
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
                            monthly_resource_wb.write(row_num, col_num, value, color_style[color])
                            col_num += 1
                        col_num = start_col
                        row_num += 1
            
            #weekly Project
            weekly_project_wb = wb.add_sheet('Weekly Project')
            w_project_info, list_week, no_enought, total = self.get_project_timesheet_info(from_date=from_date, to_date=to_date, sheet_ids=sheet_ids, filter='weekly')
            start_col, start_row = (0, 0)
            row_num, col_num = (0, 0)
            # create  header
            list_header = ['Sheet', 'Resource', 'Eng Type', 'Team'] + list_week
            for header in list_header:
                weekly_project_wb.col(col_num).width = 256 * 14
                weekly_project_wb.write(row_num, col_num, header, style_header)
                col_num += 1
            col_num = start_col
            row_num += 1
            for sheet_name in w_project_info:
                weekly_project_wb.write(row_num, col_num, sheet_name, color_style['light_turquoise'])
                col_num += 1
                weekly_project_wb.write(row_num, col_num, '', color_style['light_turquoise'])
                col_num += 1
                weekly_project_wb.write(row_num, col_num, '', color_style['light_turquoise'])
                col_num += 1
                weekly_project_wb.write(row_num, col_num, '', color_style['light_turquoise'])
                col_num += 1
                for column in list_week:
                    weekly_project_wb.write(row_num, col_num, w_project_info[sheet_name]['total'][column], color_style['light_turquoise'])
                    col_num += 1
                col_num = start_col
                row_num += 1
                for user_name in w_project_info[sheet_name]['resource']:
                    eng_type = w_project_info[sheet_name]['resource'][user_name]['eng_type']
                    team = w_project_info[sheet_name]['resource'][user_name]['team']
                    eng_type = w_project_info[sheet_name]['resource'][user_name]['eng_type']
                    timesheet = w_project_info[sheet_name]['resource'][user_name]['timesheet']
                    weekly_project_wb.write(row_num, col_num, '')
                    col_num += 1
                    weekly_project_wb.write(row_num, col_num, user_name)
                    col_num += 1
                    weekly_project_wb.write(row_num, col_num, eng_type)
                    col_num += 1
                    weekly_project_wb.write(row_num, col_num, team)
                    col_num += 1
                    
                    for column in list_week:
                        work_hour = timesheet[column]['work_hour']
                        max_hour = timesheet[column]['max_hour']
                        if work_hour > max_hour:
                            weekly_project_wb.write(row_num, col_num, max_hour, color_style['orange'])
                            col_num += 1
                        elif work_hour  == max_hour:
                            weekly_project_wb.write(row_num, col_num, max_hour, color_style['lime'])
                            col_num += 1
                        else:
                            weekly_project_wb.write(row_num, col_num, work_hour, color_style['tan'])
                            col_num += 1
                    col_num = start_col
                    row_num += 1
            #end project
            
            #monthly Project
            monthly_project_wb = wb.add_sheet('Monthly Project')
            m_project_info, list_month, no_enought, total = self.get_project_timesheet_info(from_date=from_date, to_date=to_date, sheet_ids=sheet_ids, filter='monthly')
            start_col, start_row = (0, 0)
            row_num, col_num = (0, 0)
            # create  header
            list_header = ['Sheet', 'Resource', 'Eng Type', 'Team'] + list_month
            for header in list_header:
                monthly_project_wb.col(col_num).width = 256 * 14
                monthly_project_wb.write(row_num, col_num, header, style_header)
                col_num += 1
            col_num = start_col
            row_num += 1
            for sheet_name in m_project_info:
                monthly_project_wb.write(row_num, col_num, sheet_name, color_style['light_turquoise'])
                col_num += 1
                monthly_project_wb.write(row_num, col_num, '', color_style['light_turquoise'])
                col_num += 1
                monthly_project_wb.write(row_num, col_num, '', color_style['light_turquoise'])
                col_num += 1
                monthly_project_wb.write(row_num, col_num, '', color_style['light_turquoise'])
                col_num += 1
                for column in list_month:
                    monthly_project_wb.write(row_num, col_num, m_project_info[sheet_name]['total'][column], color_style['light_turquoise'])
                    col_num += 1
                col_num = start_col
                row_num += 1
                for user_name in m_project_info[sheet_name]['resource']:
                    eng_type = m_project_info[sheet_name]['resource'][user_name]['eng_type']
                    team = m_project_info[sheet_name]['resource'][user_name]['team']
                    eng_type = m_project_info[sheet_name]['resource'][user_name]['eng_type']
                    timesheet = m_project_info[sheet_name]['resource'][user_name]['timesheet']
                    monthly_project_wb.write(row_num, col_num, '')
                    col_num += 1
                    monthly_project_wb.write(row_num, col_num, user_name)
                    col_num += 1
                    monthly_project_wb.write(row_num, col_num, eng_type)
                    col_num += 1
                    monthly_project_wb.write(row_num, col_num, team)
                    col_num += 1
                    
                    for column in list_month:
                        work_hour = timesheet[column]['work_hour']
                        max_hour = timesheet[column]['max_hour']
                        if work_hour > max_hour:
                            monthly_project_wb.write(row_num, col_num, max_hour, color_style['orange'])
                            col_num += 1
                        elif work_hour  == max_hour:
                            monthly_project_wb.write(row_num, col_num, max_hour, color_style['lime'])
                            col_num += 1
                        else:
                            monthly_project_wb.write(row_num, col_num, work_hour, color_style['tan'])
                            col_num += 1
                    col_num = start_col
                    row_num += 1
            #end project
            
#             color_wb = wb.add_sheet('Color')
#             row_num, col_num = (0, 0)
#             for color in color_style:
#                 color_wb.write(row_num, col_num, color, color_style[color])
#                 col_num = start_col
#                 row_num += 1

            
            wb.save(output_path)
            return 1, file_name
        
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]
    
    def add_to_final(self, from_date, to_date, sheet_ids, overwrite=False):
        workdays = get_work_days(from_date=from_date, to_date=to_date)
        list_date = []
        for date, week in workdays:
            list_date.append(date)
        try:
            if from_date and to_date and sheet_ids:
                task_obj    = DbTask()
                for sheet_id in sheet_ids:
                    task_obj.set_attr(sheet_id  = str(sheet_id),
                                      start_date = from_date,
                                      end_date   = to_date)
                    # if overwrite:
#                         task_obj.remove_final_task_information()
                    task_obj.move_task_to_final()
                    list_record = []
                    for date in list_date:
                        list_record.append((date, sheet_id))
                    
                    task_obj.add_final_date(list_record)
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
        cfg_sheet_ids = config_obj.sheet_ids
        task_obj  = DbTask()
        workdays = get_work_days(from_date=from_date, to_date=to_date)
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
        
        info, list_sub_column, i6_count_fail, i6_total = self.get_project_timesheet_info(request_dict, is_caculate=True)
        if i6_total - i6_count_fail == i6_total:
            i6_status = True
        else:
            i6_status = False
        i6_method = convert_request_dict_to_url(request_dict, [[SessionKey.MODE, 'sheet_user'], [SessionKey.TASK_FILTER, task_filter]])
        
        result = [
            [AnalyzeItem.A001, i1_status, True, '%s?%s'%(Route.RESOURCE_TIMESHEET, i1_method), no_missing, total_resource],
            [AnalyzeItem.A002, i2_status, True, '%s?%s'%(Route.RESOURCE_TIMESHEET, i2_method), no_redundant, total_resource],
            [AnalyzeItem.A003, i3_status, True, '%s?%s'%(Route.RESOURCE_TIMESHEET, i3_method), no_enought, total_resource],
            [AnalyzeItem.A004, i4_status, False, '%s?%s'%(Route.CONFLICT_DATE, i4_method), i4_count_fail, i4_total],
            [AnalyzeItem.A005, i5_status, False, '%s?%s'%(Route.CONFLICT_DATE, i5_method), i5_count_fail, i5_total],
            [AnalyzeItem.A006, i6_status, True, '%s?%s'%(Route.PROJECT_TIMESHEET, i6_method), i6_count_fail, i6_total]
            ]        
        return result
    
    def check_get_newest_data_feature_is_running(self, sheet_ids=[]):
        
        if len(sheet_ids):
            config_obj  = Configuration()
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
        else:
            result = (False, [])
        
        return result 
        
    def get_project_timesheet_info(self, request_dict=None, from_date=None, to_date=None, sheet_ids=None, filter='weekly', 
                                   mode='all', task_filter='both', list_user=None, is_caculate=False):
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
                except KeyError:
                    missing_method = True
            
            if not filter or not sheet_ids or not to_date or not from_date or missing_method:
                return ({}, [], 0, 0)
            sheet_user2 = None
            sheet_user3 = None
            config_obj      = Configuration()
            
            if is_caculate or mode == 'sheet_user':
                config_obj.get_sheet_user_info()
                sheet_user2 = config_obj.sheet_user2
                sheet_user3 = config_obj.sheet_user3
                
            timesheet_obj   = Timesheet(from_date, to_date, task_filter, sheet_ids, list_user)
            timesheet_obj.parse(sheet_user=sheet_user2)
            user_ids        = timesheet_obj.user_ids
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
                            info[sheet_name]  = {'resource': {}, 'total': {}, 'sheet_id': sheet_id}
                             
                        if not info[sheet_name]['resource'].get(user_name):
                            info[sheet_name]['resource'][user_name]  = {'eng_type': eng_type, 
                                                                        'team': team_name,
                                                                        'timesheet': {},
                                                                        'user_id': user_id} 
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
            # caculate total of sheet
            for sheet_name in info:
                for user_name in info[sheet_name]['resource']:
                    for col_name in info[sheet_name]['resource'][user_name]['timesheet']:
                        work_hour = info[sheet_name]['resource'][user_name]['timesheet'][col_name]['work_hour']
                        max_hour = info[sheet_name]['resource'][user_name]['timesheet'][col_name]['max_hour']
                        if work_hour > max_hour:
                            info[sheet_name]['total'][col_name]  += max_hour
                        else:
                            info[sheet_name]['total'][col_name]  += work_hour
                        info[sheet_name]['total'][col_name]  = round_num(info[sheet_name]['total'][col_name])
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
            result = (info, list_sub_col, no_enought, total)
            return result
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]  
    
    def get_resource_and_role_name(self):
        user_name = session[SessionKey.USERNAME]
        email = '%s@savarti.com'%user_name
        config_obj = Configuration()
        role_name = Role.USER
        user_id, name = config_obj.get_user_by_email(email)
        if user_id:
            role_name2 = config_obj.get_role_by_user_id(user_id)
            if role_name2:
                role_name = role_name2
        
        return user_id, name, role_name
        
    def authenticate_account(self, username, password, remember=0):
        result = check_domain_password(username, password)
        if result[0]:
            session[SessionKey.USERNAME] = username
            session[SessionKey.PASSWORD] = password
            session[SessionKey.IS_LOGIN] = True
            if remember:
                save_password(password)
            user_id, name, role_name = self.get_resource_and_role_name()
            session[SessionKey.RESOURCE_NAME] = name
            session[SessionKey.USER_ID] = user_id
            session[SessionKey.ROLE_NAME] = role_name
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
    
    def update_sync_sheet(self, request_dict):
        try:
            info = request_dict['info']
            config_obj  = Configuration()
            config_obj.set_attr(updated_by  = session[SessionKey.USERNAME])
            config_obj.get_sheet_type_info(is_parse=True)
            sheet_type_info = config_obj.sheet_type
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
                    config_obj.add_sheet()
                
            return 1, 'Synchronize successfully'
        except Exception as e:
            println(e, OtherKeys.LOGING_EXCEPTION)
            return 0, e.args[0]
        