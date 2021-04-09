'''
Created on Feb 5, 2021

@author: toannguyen
'''
import os, sys, re, copy
import datetime, calendar
import ast
from src.commons.message import Msg, MsgError, MsgWarning
from src.commons.enums import DateTime, SessionKey, ExcelColor, SettingKeys, OtherKeys
import logging
import config
from flask import request
import shutil
import traceback
from decimal import Decimal
import xlwt, socket
import urllib
import win32security
from win32com import client
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
        request_dict = ast.literal_eval(form.strip())
    
    if SessionKey.SHEETS in request_dict:
        for idx in range(0, len(request_dict[SessionKey.SHEETS])):
            request_dict[SessionKey.SHEETS][idx] = int(request_dict[SessionKey.SHEETS][idx])
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

def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    addr, port = tcp.getsockname()
    tcp.close()
    return port

def remove_path(path):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

def round_num(number, ndigits=1):
    number  = Decimal(number)
    result = round(number, ndigits)
    # result = result.normalize()
    result = result.quantize(Decimal(1)) if result == result.to_integral() else result.normalize()
    return result
    
def save_file_from_request():
    try:
        for file_name in request.files:
            userfile = request.files[file_name]
            upload_folder   = os.path.join(config.WORKING_PATH, 'upload')
            make_folder(upload_folder)
            userfile.save(os.path.join(upload_folder, userfile.filename))
        return 1, ''
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return 0, e.args[0]

def stuck(message='', logging_level=None):
    print ('ERROR ' + message)
    raise Exception(message)

def convert_request_dict_to_url(request_dict, more_option=[]):
    request_dict_cp = copy.deepcopy(request_dict) 
    result = ''
    if not request_dict_cp:
        return result
    for element in more_option:
        key, val = element
        request_dict_cp[key] = val
    
    result = urllib.parse.quote(str(request_dict_cp))
    return result   
    
def println(message, logging_level=None):
    if logging_level == OtherKeys.LOGING_CRITICAL:
        logging.critical(message)
        print (message)
    elif logging_level == OtherKeys.LOGING_EXCEPTION:
        logging.exception(message)
#         traceback.print_exc('')
        print (message)
    elif logging_level == OtherKeys.LOGING_ERROR:
        logging.error(message)
        print (message)
    elif logging_level == OtherKeys.LOGING_WARNING:
        logging.warn(message)
        print (message)
    elif logging_level == OtherKeys.LOGING_INFO:
        logging.info(message)
        print (message)
    elif logging_level == OtherKeys.LOGING_DEBUG:
        if config.LOGGING_LEVEL.lower() ==  OtherKeys.LOGING_DEBUG:
            logging.debug(message)
            print (message)

def is_caculate_sheet(sheet_name):
    result = True
    if '_ais' in sheet_name.lower():
        result = False
    elif ' ais' in sheet_name.lower():
        result = False
    elif sheet_name.lower().startswith('bug_'):
        result = False
    elif sheet_name.lower().startswith('copy of'):
        result = False
    elif sheet_name.lower().startswith('ai_'):
        result = False
    elif sheet_name.lower().startswith('ais_'):
        result = False
    elif sheet_name.lower().startswith('ai '):
        result = False
    elif sheet_name.lower().startswith('ar-'):
        result = False
    elif sheet_name in SettingKeys.SKIP_SHEET:
        result = False
    return result
    
def split_patern(string, pattern=''):
    result = filter(None, re.split(pattern, string))
    return result

def compare_date(greater_date, less_date):
    if greater_date == None or less_date == None:
        return False
    if not isinstance(greater_date, datetime.datetime):
        greater_date = str_to_date(greater_date)[0]
    if not isinstance(less_date, datetime.datetime):
        less_date = str_to_date(less_date)[0]
    if greater_date >= less_date:
        return True
    else:
        return False
    
def message_generate(message, *argv):
    try:
        list_argv = []
        for arg in argv:
            list_argv.append(arg)
        var_tuple = tuple(list_argv)
        result  = message.format(*var_tuple)
        return result
    except Exception as e:
        stuck(e, OtherKeys.LOGING_EXCEPTION)

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
    elif logging_level.lower() == OtherKeys.LOGING_DEBUG:
        level = logging.DEBUG
    elif logging_level.lower() == OtherKeys.LOGING_INFO:
        level = logging.INFO
    elif logging_level.lower() == OtherKeys.LOGING_WARNING:
        level = logging.WARNING
    elif logging_level.lower() == OtherKeys.LOGING_ERROR:
        level = logging.ERROR
    elif logging_level.lower() == OtherKeys.LOGING_CRITICAL:
        level = logging.CRITICAL
    else:
        level = logging.WARNING
    return level

def logging_setting(file_name):
    try:
        logging_lv      = config.LOGGING_LEVEL
    except  AttributeError:
        logging_lv      = OtherKeys.LOGING_ERROR
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
                        stuck(message, OtherKeys.LOGING_EXCEPTION)
    year    = obj_date.year
    month   = obj_date.month
    day     = obj_date.day
    return obj_date, year, month, day

def get_week_number(date):
    if isinstance(date, datetime.date) or isinstance(date, datetime.datetime):
        result  = date.isocalendar()[1]
    else:
        date = str_to_date(date)[0]
        result  = date.isocalendar()[1]
    return result

def write_message_into_file(log, message='', mode='a'):
    with open(log, mode) as file:
        file.write(message)
    
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

def get_start_week_of_date(date, output_str=True):
    if not isinstance(date, datetime.datetime):
        date = str_to_date(date)[0]
    start_week = date - datetime.timedelta(days=date.weekday())
    if output_str:
        result = convert_date_to_string(start_week, '%Y-%m-%d')
        return result
    else:
        return start_week

def get_end_week_of_date(date, output_str=True):
    if not isinstance(date, datetime.datetime):
        date = str_to_date(date)[0]
    start_week = date - datetime.timedelta(days=date.weekday())
    end_week = start_week + datetime.timedelta(days=4)
    if output_str:
        result = convert_date_to_string(end_week, '%Y-%m-%d')
        return result
    else:
        return end_week

def get_start_month_of_date(date, d_years=0, d_months=0, output_str=True):
    if not isinstance(date, datetime.datetime):
        date = str_to_date(date)[0]
    date.replace(minute=0, hour=0, second=0, microsecond=0)
    # d_years, d_months are "deltas" to apply to dt
    y, m = date.year + d_years, date.month + d_months
    a, m = divmod(m-1, 12)
    start_date = datetime.datetime(y+a, m+1, 1)
    if output_str:
        result = convert_date_to_string(start_date, '%Y-%m-%d')
        return result
    else:
        return start_date

def get_end_month_of_date(date, output_str=True):
    end_date =  get_start_month_of_date(date, 0, 1, False) + datetime.timedelta(-1)
    if output_str:
        result = convert_date_to_string(end_date, '%Y-%m-%d')
        return result
    else:
        return end_date


def calculate_start_end_date_by_option(date, from_date, to_date, mode):
    
    start = from_date
    end = to_date
    if mode == 'monthly':
        start_month = get_start_month_of_date(date)
        end_month = get_end_month_of_date(date)
        if compare_date(start_month, from_date):
            start = start_month
        if compare_date(to_date, end_month):
            start = end_month
    else:
        start_week = get_start_week_of_date(date)
        end_week = get_end_week_of_date(date)
        if compare_date(start_week, from_date):
            start = start_week
        if compare_date(to_date, end_week):
            end = end_week
    
    start = convert_date_to_string(start, '%Y-%m-%d')
    end = convert_date_to_string(end, '%Y-%m-%d')
    return start, end

def get_month_name_of_date(date):
    if not isinstance(date, datetime.datetime):
        date = str_to_date(date)[0]
        month = date.month
        month_name = DateTime.LIST_MONTH[month]
        return month_name
    
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
        date_str = '%s-%02d-%02d'%(year, month, day)
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
        # elif len(list_work_day) == 0:
            # info = [str(datetime.date(year, month, day)), str(start_week)]
            # list_work_day.append(info)
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
        date_str = '%s-%02d-%02d'%(year, month, day)
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
    for empty_w in list_week:
        if not (empty_w[1]):
            list_week.remove(empty_w)
    return list_week

# # [[month, year, total hour work],...]
def get_work_month(from_date, to_date, holidays=[], time_delta=None):
    
    date_obj, start_year, start_month, start_day = str_to_date(from_date)
    date_obj, end_year, end_month, end_day = str_to_date(to_date)
    list_month = []
    start_date = datetime.date(start_year, start_month, start_day)
    end_date = datetime.date(end_year, end_month, end_day)
    total = 0
    
    for dt in daterange(start_date, end_date):
        date_obj_2, year, month, day = str_to_date(dt.strftime("%Y-%m-%d"))
        if time_delta != None and date_obj_2 < time_delta:
            continue
        y_m_d = '%s-%02d-%02d'%(year, month, day)
        month_tuple = [month, year]
        if len(list_month) == 0:
            month_tuple = [month, year]
            list_month.append(month_tuple)
            if (calendar.day_name[calendar.weekday(year, month, day)] in DateTime.LIST_WORK_DAY_OF_WEEK)  and (not (y_m_d in holidays)):
                total += 8
        else:
            if not (month_tuple in list_month):
                list_month.append(month_tuple)
                list_month[-2].append(total)
                total = 0
                if (calendar.day_name[calendar.weekday(year, month, day)] in DateTime.LIST_WORK_DAY_OF_WEEK)  and (not (y_m_d in holidays)):
                    total += 8
            else:
                if (calendar.day_name[calendar.weekday(year, month, day)] in DateTime.LIST_WORK_DAY_OF_WEEK)  and (not (y_m_d in holidays)):
                    total += 8
    list_month[-1].append(total)
    
    return list_month

def defined_color():
    color_style = {}
    list_color = ExcelColor.LIST_COLOR
    for color in list_color:
        format_command = 'align: wrap 0;pattern: pattern solid, fore-colour %s; border: left thin, top thin, right thin, bottom thin, bottom-color gray25, top-color gray25, left-color gray25, right-color gray25; font: name Calibri, bold 0,height 240;' %(color)
        style = xlwt.easyxf(format_command)
        color_style[color] = style
    return color_style

def encrypt(message):
    new_str=''
    for car in message:
        new_str = new_str + chr(ord(car)+7)
    return new_str

def decrypt(message):
    new_str=''
    for car in message:
        new_str= new_str + chr(ord(car)-7)
    return new_str

def get_saved_password():
    working_path = config.WORKING_PATH
    file_name = os.path.join(working_path, '.pswd.txt')
    password = None
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            encrypt_ctn = f.read()
            password = decrypt(encrypt_ctn)
    return password

def save_password(password):
    working_path = config.WORKING_PATH
    file_name = os.path.join(working_path, '.pswd.txt')
    with open(file_name, 'w') as f:
        encrypt_ctn = encrypt(password)
        f.write(encrypt_ctn)

def check_domain_password(username, password, domain_name='SVI'):
    try:
        token = win32security.LogonUser(
            username,
            domain_name,
            password,
            win32security.LOGON32_LOGON_NETWORK,
            win32security.LOGON32_PROVIDER_DEFAULT)
        result = bool(token)
#         result = True
        if result:
            return True, ''
        else:
            return False, MsgError.E004
    except Exception as e:
        println(str(e.args), OtherKeys.LOGING_EXCEPTION)
        return False, MsgError.E004
    
def render_jinja2_template(template_path, file_name,  dict_variable):
    systemFile1 = FileSystemLoader(template_path)
    j2_env1 = Environment(loader=systemFile1, trim_blocks=True)
    run_template = j2_env1.get_template(file_name)
    result = run_template.render(dict_variable)
    return result
    
def send_mail(user_name, password, recepient, cc_recepient, subject, message):
    try:
        sender = "%s@savarti.com"%user_name
        recepient = ['toannguyen@savarti.com']
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['From'] = sender
        msg['To'] = '; '.join(recepient)
        msg['Subject'] = subject
        
        # see the code below to use template as body
        # Create the body of the message (a plain-text and an HTML version).
        # Record the MIME types of both parts - text/plain and text/html.
        part = MIMEText(message, 'html')
        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part)
        
        # Send the message via local SMTP server.
        mail = smtplib.SMTP("smtp.outlook.office365.com", 587, timeout=20)

        # if tls = True                
        mail.starttls()               
        mail.login(sender, password)        
        mail.sendmail(sender, recepient, msg.as_string())        
        mail.quit()
        return 1, ''
    except Exception as e:
        println(str(e.args), OtherKeys.LOGING_EXCEPTION)
        return 0, 'Send mail fail'
        
