'''
Created on Feb 5, 2021

@author: toannguyen
'''
import os, sys, re, copy
import datetime, calendar, time
import ast, getpass
from src.commons import message, enums
import logging, base64
import master_config
from flask import request, session
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
from pprint import pprint
import binascii

def hash(text):
    str_text = str(text)
    result = int(binascii.hexlify(str_text.encode('utf8')), 16)
    result = str(result)
    return result

def unhash(text):
    result = binascii.unhexlify('%x' % int(text))
    result = result.decode('ascii')
    return result

def convert_number_to_currency(input_number):
    if isinstance(input_number, float) or isinstance(input_number, int):
        result = "${:,.0f}".format(input_number)# ${:,.0f}
    else:
        if not input_number:
            result = ''
        else:
            try:
                result = result = "${:,.0f}".format(float(input_number))
            except:
                result = ''
    return result



def convert_data_type(value, data_type):
    result = value
    #data type is currency
    if data_type == 'currency':
        result = convert_number_to_currency(value)
     
    return result
    

def get_request_form():
    # for post method
    methods = {}
    forms = request.form
    for form in forms:
        try:
            methods = ast.literal_eval(form.strip())
        except ValueError as e:
            methods[form] = forms.get(form)
    return methods

def get_request_args():
    # for get method
    methods = {}
    forms = request.args
    for form in forms:
        try:
            methods = ast.literal_eval(form.strip())
        except ValueError as e:
            methods[form] = forms.get(form)
    return methods

def get_delta_time(start_date, end_date):
    if not isinstance(start_date, datetime.datetime):
        start_date = str_to_date(start_date)[0]
    if not isinstance(end_date, datetime.datetime):
        end_date = str_to_date(end_date)[0]
    # returns a timedelta object
    delta_date = end_date - start_date
    
    # returns the difference of the time of the day
    minutes = int(delta_date.seconds / 60)
    return minutes

def toDate(date_str):
    try:
        obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except:
        try:
            obj = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
        except:
            try:
                obj = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            except:
                try:
                    obj = datetime.datetime.strptime(date_str, '%m/%d/%Y')
                except:
                    println("Datetime format error: %s"%date_str)
    year = obj.year
    month = obj.month
    day = obj.day
    return obj, year, month, day

def parse_dict(init, lkey=''):
    ret = {}
    for rkey, val in init.items():
        key = lkey + rkey
        if isinstance(val, dict) and rkey in ["allVars"]:
            ret.update(parse_dict(val, ""))
        else:
            ret[key] = val
    return ret

def convert_text(text):
    if isinstance(text, float) or isinstance(text, int):
        result = text
    else:
        result = text.encode('utf8')
        result = str(result, 'utf8')
    return result

def revert_text(text):
    result = text.encode('utf8').decode('utf8')
    return result

def add_keys_to_dict(data, key, value):
    if not data.get(key):
        data[key] = value

def read_template(file_name, add_info):
    config_params = {}
    sys.argv = [file_name, add_info]
    exec(open(file_name, encoding="utf-8").read(), config_params)
    if '__doc__' in config_params:
        del config_params['__doc__']
    if '__builtins__' in config_params:
        del config_params['__builtins__']
    config_params = parse_dict(config_params)
    return config_params

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

def encode_base64(text):
    result = base64.b64encode(text)
    return result
    
def encode_base64(text):
    result = base64.b64encode(text.encode('utf8'))
    return result
    
def make_file(path, content, is_print=True):
    if is_print:
        println('Create file "%s"'%path)
    f = open(path, 'w', encoding='utf-8')
    f.write(content)
    f.close

def read_file(path):
    f = open(path, 'r', encoding='utf-8')
    content = f.read()
    f.close
    return content
    
def round_num(number, ndigits=2):
    number  = Decimal(number)
    result = round(number, ndigits)
    # result = result.normalize()
    result = result.quantize(Decimal(1)) if result == result.to_integral() else result.normalize()
    return result
    
def save_file_from_request():
    try:
        for file_name in request.files:
            userfile = request.files[file_name]
            upload_folder   = os.path.join(master_config.WORKING_PATH, 'upload')
            make_folder(upload_folder)
            userfile.save(os.path.join(upload_folder, userfile.filename))
        return 1, ''
    except Exception as e:
        println(e, enums.LoggingKeys.LOGGING_EXCEPTION)
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
    
def println(message, logging_level=enums.LoggingKeys.LOGGING_INFO, is_print=True):
    try:
        message = str(message)
    except:
        pass
    if logging_level == enums.LoggingKeys.LOGGING_CRITICAL:
        # logging.critical(message)
        if is_print:
            print ('<span class="font-weight-bold console-error"> >> ERROR: </span>' + message)
            sys.stdout.flush()
    elif logging_level == enums.LoggingKeys.LOGGING_EXCEPTION:
        # logging.exception(message)
        traceback.print_exc('')
        if is_print:
            print ('<span class="font-weight-bold console-error"> >> ERROR: </span>' + message)
            sys.stdout.flush()
    elif logging_level == enums.LoggingKeys.LOGGING_ERROR:
        # logging.error(message)
        traceback.print_exc()
        if is_print:
            print ('<span class="font-weight-bold console-error"> >> ERROR: </span>' + message)
            sys.stdout.flush()
    elif logging_level == enums.LoggingKeys.LOGGING_WARNING:
        # logging.warn(message)
        if is_print:
            print ('<span class="font-weight-bold console-warning"> >> WARN: </span>' + message)
            sys.stdout.flush()
    elif logging_level == enums.LoggingKeys.LOGGING_INFO:
        # logging.info(message)
        if is_print:
            print ('<span class="font-weight-bold console-info"> >> INFO: </span>' + message)
            sys.stdout.flush()
    elif logging_level == enums.LoggingKeys.LOGGING_DEBUG:
        if master_config.LOGGING_LEVEL.lower() ==  enums.LoggingKeys.LOGGING_DEBUG:
            #logging.debug(message)
            if is_print:
                print ('<span class="font-weight-bold console-debug"> >> DEBUG: </span>'  + message)
                sys.stdout.flush()
                
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
        stuck(e, enums.LoggingKeys.LOGGING_EXCEPTION)

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
    elif logging_level.lower() == enums.LoggingKeys.LOGGING_DEBUG:
        level = logging.DEBUG
    elif logging_level.lower() == enums.LoggingKeys.LOGGING_INFO:
        level = logging.INFO
    elif logging_level.lower() == enums.LoggingKeys.LOGGING_WARNING:
        level = logging.WARNING
    elif logging_level.lower() == enums.LoggingKeys.LOGGING_ERROR:
        level = logging.ERROR
    elif logging_level.lower() == enums.LoggingKeys.LOGGING_CRITICAL:
        level = logging.CRITICAL
    else:
        level = logging.WARNING
    return level

def logging_setting(file_name):
    try:
        logging_lv      = master_config.LOGGING_LEVEL
    except  AttributeError:
        logging_lv      = enums.LoggingKeys.LOGGING_ERROR
    logging_level       = select_logging_level(logging_lv)
    log_name            = os.path.join(master_config.WORKING_PATH, file_name)
    logging.basicConfig(filename=log_name, level=logging_level, 
                    format='>> %(levelname)s: %(message)s',
                    filemode='a')

def date_to_str(date_obj=None, format_str='%Y-%m-%d %H:%M:%S'):
    if not date_obj:
        date_obj = datetime.datetime.now()
    if isinstance(date_obj, datetime.datetime):
        result = date_obj.strftime(format_str)
    else:
        result = date_obj
    return result

def create_list(list_input, index, value):
    for idx in range(0, index + 1):
        if len(list_input) < (idx + 1):
            list_input.append('')
            try:
                list_input[index] = value
            except:
                pass
        else:
            try:
                list_input[index] = value
            except:
                pass
        
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
                        message      = message_generate(enums.MsgError.E001, string)
                        stuck(message, enums.LoggingKeys.LOGGING_EXCEPTION)
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
        month_name = enums.DateTime.LIST_MONTH[month]
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
        if calendar.day_name[calendar.weekday(year, month, day)] == enums.DateTime.START_WEEK:
            start_week = datetime.date(year, month, day)
        else:
            day2 = datetime.date(year, month, day)
#             days = np.busday_count(start, end)
            start_week = day2 - datetime.timedelta(days=day2.weekday())
        if (calendar.day_name[calendar.weekday(year, month, day)] in enums.DateTime.LIST_WORK_DAY_OF_WEEK) and (not (date_str in holidays)):
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
        if (calendar.day_name[calendar.weekday(year, month, day)] != enums.DateTime.START_WEEK) and (list_week == []):
            day2 = datetime.date(year, month, day)
#             days = np.busday_count(start, end)
            start_week = day2 - datetime.timedelta(days=day2.weekday())
            list_week_hour_total = [str(start_week), 0]
            list_week.append(list_week_hour_total)
        if (calendar.day_name[calendar.weekday(year, month, day)] == enums.DateTime.START_WEEK):
            start_week = datetime.date(year, month, day)
            list_week_hour_total = [str(start_week), 0]
            list_week.append(list_week_hour_total)
        if (calendar.day_name[calendar.weekday(year, month, day)] in enums.DateTime.LIST_WORK_DAY_OF_WEEK)  and (not (date_str in holidays)):
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
            if (calendar.day_name[calendar.weekday(year, month, day)] in enums.DateTime.LIST_WORK_DAY_OF_WEEK)  and (not (y_m_d in holidays)):
                total += 8
        else:
            if not (month_tuple in list_month):
                list_month.append(month_tuple)
                list_month[-2].append(total)
                total = 0
                if (calendar.day_name[calendar.weekday(year, month, day)] in enums.DateTime.LIST_WORK_DAY_OF_WEEK)  and (not (y_m_d in holidays)):
                    total += 8
            else:
                if (calendar.day_name[calendar.weekday(year, month, day)] in enums.DateTime.LIST_WORK_DAY_OF_WEEK)  and (not (y_m_d in holidays)):
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
    username = getpass.getuser()
    user_file = os.path.join(os.path.join('C:\\Users', username), '.pswd.txt')
    password = ''
    if os.path.exists(user_file):
        file_name = user_file
        with open(file_name, 'r', encoding="utf-8") as f:
            encrypt_ctn = f.read()
            password = decrypt(encrypt_ctn)
        return password
    else:
        working_path = master_config.WORKING_PATH
        file_name = os.path.join(working_path, '.pswd.txt')
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding="utf-8") as f:
                encrypt_ctn = f.read()
                password = decrypt(encrypt_ctn)
        return password

def clear_saved_password():
    username = getpass.getuser()
    user_file = os.path.join(os.path.join('C:\\Users', username), '.pswd.txt')
    if os.path.exists(user_file):
        remove_path(user_file)
        
        
def save_password(password):
    try:
        username = getpass.getuser()
        file_name = os.path.join(os.path.join('C:\\Users', username), '.pswd.txt')
        with open(file_name, 'w', encoding="utf-8") as f:
            encrypt_ctn = encrypt(password)
            f.write(encrypt_ctn)
    except:
        working_path = master_config.WORKING_PATH
        file_name = os.path.join(working_path, '.pswd.txt')
        with open(file_name, 'w', encoding="utf-8") as f:
            encrypt_ctn = encrypt(password)
            f.write(encrypt_ctn)
            
def check_domain_password(username, password, domain_name='SVI'):
    try:
        if not password:
            return False, 'Missing password'
        token = win32security.LogonUser(
            username,
            domain_name,
            password,
            win32security.LOGON32_LOGON_NETWORK,
            win32security.LOGON32_PROVIDER_DEFAULT)
        result = bool(token)
        # result = True
        if result:
            return True, ''
        else:
            return False, message.MsgError.E004
    except Exception as e:
        return False, message.MsgError.E004
    
def render_jinja2_template(template_path, file_name,  dict_variable):
    systemFile1 = FileSystemLoader(template_path)
    j2_env1 = Environment(loader=systemFile1, trim_blocks=True)
    run_template = j2_env1.get_template(file_name)
    result = run_template.render(dict_variable)
    return result
    
def send_mail(user_name, password, recipient, cc_recipient, subject, message, bcc_recipient=[], break_line=True):
    try:
        if break_line:
            message = message.replace('\n', '<br>\n')
        sender = "%s@savarti.com"%user_name
        if not master_config.IS_PRODUCT:
            bcc_recipient = []
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['From'] = sender
        msg['To'] = '; '.join(recipient)
        msg['Subject'] = subject
        msg['CC'] = '; '.join(cc_recipient)
        msg['BCC'] = '; '.join(bcc_recipient)
        part = MIMEText(message, 'html')
        msg.attach(part)
        
        # Send the message via local SMTP server.
        starttls = True
        count  = 0
        while starttls:
            count += 1
            try:
                mail = smtplib.SMTP("smtp.outlook.office365.com", 587, timeout=20)            
                mail.starttls()               
                mail.login(sender, password)
                mail.sendmail(sender, recipient + bcc_recipient + cc_recipient, msg.as_string())
                starttls = False
                mail.quit()
            except Exception as e:
                time.sleep(1)
                if count == 30:
                    starttls = False
                    println('Fail to send mail', enums.LoggingKeys.LOGGING_ERROR)
                    return 0, 'Fail to send mail.'
        return 1, ''
    except Exception as e:
        println(str(e.args), enums.LoggingKeys.LOGGING_EXCEPTION)
        return 0, 'Fail to send mail.'
        
