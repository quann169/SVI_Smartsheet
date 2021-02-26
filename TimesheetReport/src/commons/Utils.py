'''
Created on Feb 5, 2021

@author: toannguyen
'''
import os, sys, re
import datetime, calendar
import ast
from src.commons.Message import Msg, MsgError, MsgWarning
import string
from src.commons.Enums import DateTime
import logging
import config
from flask import request
import shutil


def get_request_form():
    # for post method
    request_dict = {}
    forms = request.form
    for form in forms:
        request_dict[form] = forms.get(form)
    return request_dict

def get_request_args():
    # for get method
    request_dict = {}
    forms = request.args
    for form in forms:
        request_dict[form] = forms.get(form)
    return request_dict

def get_request_form_ajax():
    # for past method
    forms = request.form
    request_dict = {}
    for form in forms.keys():
        request_dict = ast.literal_eval(form.strip())
    return request_dict

def make_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

def remove_path(path):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    
def save_file_from_request():
    try:
        for file_name in request.files:
            userfile = request.files[file_name]
            upload_folder   = os.path.join(config.WORKING_PATH, 'upload')
            make_folder(upload_folder)
            userfile.save(os.path.join(upload_folder, userfile.filename))
        return 1, ''
    except Exception as e:
        return 0, e

def stuck(message='', logging_level=None):
    print ('ERROR ' + message)
    raise Exception(message)

def println(message, logging_level=None):
    logging.info(message)
    print (message)

def message_generate(message, *argv):
    try:
        list_argv = []
        for arg in argv:
            list_argv.append(arg)
        var_tuple = tuple(list_argv)
        result  = message.format(*var_tuple)
        return result
    except Exception as e:
        stuck(e, 'exception')

def search_pattern(string, pattern):
    obj_search = re.search(pattern, string)
    if obj_search:
        result = obj_search.groups()
        return result
    else:
        return obj_search
    
def select_logging_level(logging_level):
    level = ''
    if logging_level == 0:
        level = logging.WARNING
    elif logging_level.lower() == 'debug':
        level = logging.DEBUG
    elif logging_level.lower() == 'info':
        level = logging.INFO
    elif logging_level.lower() == 'warning':
        level = logging.WARNING
    elif logging_level.lower() == 'error':
        level = logging.ERROR
    elif logging_level.lower() == 'critical':
        level = logging.CRITICAL
    else:
        level = logging.WARNING
    return level

def logging_setting(file_name):
    try:
        logging_lv      = config.LOGGING_LEVEL
    except  AttributeError:
        logging_lv      = 'ERROR'
    logging_level       = select_logging_level(logging_lv)
    log_formatter       = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
    log_name            = os.path.join(config.WORKING_PATH, file_name)
    log                 = logging.getLogger()
    log.setLevel(logging_level)
    handler             = logging.handlers.RotatingFileHandler(log_name,maxBytes= 1000*1024,backupCount=20)
    handler.setFormatter(log_formatter)
    log.addHandler(handler)

def str_to_date(string):
    if isinstance(string, datetime.datetime):
        obj_date    = string
    else:
        try:
            obj_date = datetime.datetime.strptime(string, '%Y-%m-%d')
        except:
            try:
                obj_date = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S')
            except:
                try:
                    obj_date = datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
                except:
                    try:
                        obj_date = datetime.datetime.strptime(string, '%m/%d/%Y')
                    except:
                        message      = message_generate(MsgError.E001, string)
                        print("Other Date time format: %s"%string)
                        stuck(message, 'exception')
    year    = obj_date.year
    month   = obj_date.month
    day     = obj_date.day
    return obj_date, year, month, day

def convert_date_to_string(date_obj, format_str='%Y-%m-%d %H:%M:%S'):
    if isinstance(date_obj, datetime.datetime):
        result = date_obj.strftime(format_str)
    else:
        result = date_obj
    return result
    
def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + datetime.timedelta(n)

def get_prev_date_by_time_delta(timedelta, compare_date=None):
    #support week only
    if compare_date == None:
        compare_date    = datetime.datetime.today()
    else:
        if not isinstance(compare_date, datetime.datetime):
            compare_date    = str_to_date(compare_date)[0]
    time_delta  = datetime.timedelta(weeks=int(timedelta))
    result  = compare_date  - time_delta
    result  = result.replace(minute=0, hour=0, second=0, microsecond=0)
    return result
    
#[[day, week], ...]  
def get_work_days(from_date, to_date, holidays=[], time_delta=None):
    date_obj, start_year, start_month, start_day = str_to_date(from_date)
    date_obj, end_year, end_month, end_day = str_to_date(to_date)
    list_work_day = []
    start_date = datetime.date(start_year, start_month, start_day)
    end_date = datetime.date(end_year, end_month, end_day)
    for date in daterange(start_date, end_date):
        date_obj_2, year, month, day = str_to_date(date.strftime("%Y-%m-%d"))
        if time_delta != None and date_obj_2 < time_delta:
            continue
        date_str = '%s-%s-%s'%(year, month, day)
        start_week = None
        if calendar.day_name[calendar.weekday(year, month, day)] == DateTime.START_WEEK:
            start_week = datetime.date(year, month, day)
        else:
            day2 = datetime.date(year, month, day)
#             days = np.busday_count(start, end)
            start_week = day2 - datetime.timedelta(days=day2.weekday())
        if (calendar.day_name[calendar.weekday(year, month, day)] in DateTime.LIST_WORK_DAY_OF_WEEK) and (not (date_str in holidays)):
            info = [str(datetime.date(year, month, day)), str(start_week)]
            list_work_day.append(info)
        elif len(list_work_day) == 0:
            info = [str(datetime.date(year, month, day)), str(start_week)]
            list_work_day.append(info)
    return list_work_day

#[[week, total hour work], ...]
def get_work_week(from_date, to_date, holidays=[], time_delta=None):
    date_obj, start_year, start_month, start_day = str_to_date(from_date)
    date_obj, end_year, end_month, end_day = str_to_date(to_date)
    list_week = []
    start_date = datetime.date(start_year, start_month, start_day)
    end_date = datetime.date(end_year, end_month, end_day)
    for date in daterange(start_date, end_date):
        date_obj_2, year, month, day = str_to_date(date.strftime("%Y-%m-%d"))
        if time_delta != None and date_obj_2 < time_delta:
            continue
        date_str = '%s-%s-%s'%(year, month, day)
        start_week = None
        if (calendar.day_name[calendar.weekday(year, month, day)] != DateTime.START_WEEK) and (list_week == []):
            day2 = datetime.date(year, month, day)
#             days = np.busday_count(start, end)
            start_week = day2 - datetime.timedelta(days=day2.weekday())
            list_week_hour_total = [str(start_week), 0]
            list_week.append(list_week_hour_total)
        if (calendar.day_name[calendar.weekday(year, month, day)] == DateTime.START_WEEK):
            start_week = datetime.date(year, month, day)
            list_week_hour_total = [str(start_week), 0]
            list_week.append(list_week_hour_total)
        if (calendar.day_name[calendar.weekday(year, month, day)] in DateTime.LIST_WORK_DAY_OF_WEEK)  and (not (date_str in holidays)):
            list_week[-1][1] += 8
    for emptyW in list_week:
        if not (emptyW[1]):
            list_week.remove(emptyW)
    return list_week

# # [[momth, year, total hour work],...]
def get_work_month(from_date, to_date, holidays=[], time_delta=None):
    date_obj, start_year, start_month, start_day = str_to_date(from_date)
    date_obj, end_year, end_month, end_day = str_to_date(to_date)
    list_month = []
    startDate = datetime.date(start_year, start_month, start_day)
    endDate = datetime.date(end_year, end_month, end_day)
    total = 0
    for dt in daterange(startDate, endDate):
        date_obj_2, year, month, day = str_to_date(dt.strftime("%Y-%m-%d"))
        if time_delta != None and date_obj_2 < time_delta:
            continue
        y_m_d = '%s-%s-%s'%(year, month, day)
        month = [month, year]
        if len(list_month) == 0:
            month = [month, year]
            list_month.append(month)
            if (calendar.day_name[calendar.weekday(year, month, day)] in DateTime.LIST_WORK_DAY_OF_WEEK)  and (not (y_m_d in holidays)):
                total += 8
        else:
            if not (month in list_month):
                list_month.append(month)
                list_month[-2].append(total)
                total = 0
                if (calendar.day_name[calendar.weekday(year, month, day)] in DateTime.LIST_WORK_DAY_OF_WEEK)  and (not (y_m_d in holidays)):
                    total += 8
            else:
                if (calendar.day_name[calendar.weekday(year, month, day)] in DateTime.LIST_WORK_DAY_OF_WEEK)  and (not (y_m_d in holidays)):
                    total += 8
    list_month[-1].append(total)
    return list_month
    