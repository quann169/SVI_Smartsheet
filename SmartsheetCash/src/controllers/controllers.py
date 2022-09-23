'''
Created on Feb 22, 2021

@author: toannguyen
'''
from src.models.smartsheet.smartsheet import SmartSheets
from src.commons import enums, message, utils
from flask import g, session
from pprint import pprint, pformat
import pandas as pd

import os, sys, getpass, datetime, copy, ast
import master_config
import time
from base64 import _input_type_check

class Controllers:
    def __init__(self, method = enums.MethodKeys.METHOD_GET):
        if session.get(enums.SessionKeys.USERNAME):
            self.user_name = session[enums.SessionKeys.USERNAME].strip()
        else:
            self.user_name = getpass.getuser()
        self.all_settings = {}
        if method == enums.MethodKeys.METHOD_GET:
            self.methods = utils.get_request_args()
        else:
            self.methods = utils.get_request_form()
        self.working_path = os.path.abspath(master_config.WORKING_PATH)
        self.tool_path = g.tool_path
        self.get_setting()
        self.dummy_result = {}
        self.compare_result = {}

    def authenticate_account(self, user_name, password, remember=0):
        '''
        ::description:: 
        ::params:
        :return:
        '''
        self.get_setting()
        allow_users = utils.unhash(self.all_settings.get('allow_users'))
        allow_users = ast.literal_eval(allow_users)
        if user_name in  allow_users:
            result = utils.check_domain_password(user_name, password)
            if result[0]:
                session[enums.SessionKeys.USERNAME] = user_name
                session[enums.SessionKeys.PASSWORD] = password
                session[enums.SessionKeys.IS_LOGIN] = True
                if remember:
                    utils.save_password(password)
            else:
                session[enums.SessionKeys.IS_LOGIN] = False
        else:
            result = (False, 'Access denied.')
        return result
    
    def read_setting_file(self):
        '''
        ::description:: 
        ::params:
        :return:
        '''
        setting_file = master_config.CONFIG_FILE
        self.all_settings= utils.read_template(setting_file, {})
    
    def get_setting(self):
        '''
        ::description:: 
        ::params:
        :return:
        '''
        if not self.all_settings:
            self.read_setting_file()
        return None
    
    def start_analyze(self):
        '''
        ::description:: 
        ::params:
        :return:
        '''
        try:
            
            sheets = self.methods[enums.MethodKeys.SHEETS]
            from_date = self.methods[enums.MethodKeys.FROM_DATE]
            to_date = self.methods[enums.MethodKeys.TO_DATE]
            smartsheet_obj = SmartSheets(sheets = [self.all_settings[enums.ConfigKeys.DES_SHEETS]], 
                                         all_settings = self.all_settings, 
                                         input_type = 'des', 
                                         from_date = from_date, 
                                         to_date = to_date,
                                         is_compare=False)
            utils.println('Start parse destination sheet')
            smartsheet_obj.parse_smartsheet()
            utils.println('Parse destination sheet - Done')
            utils.println('Start parse source sheet')
            smartsheet_obj.set_attr(input_type = 'src', sheets = sheets, is_compare = True)
            smartsheet_obj.update_attr_by_input_type()
            smartsheet_obj.parse_smartsheet()
            utils.println('Parse source sheet - Done')
            utils.println('Parse data - Done')
            result = [1, 'Parse successfully']
            return result
        except Exception as e:
            utils.println(e, enums.LoggingKeys.LOGGING_EXCEPTION)
            result = [0, e]
            return result
        
    def check_compare_result(self):
        '''
        ::description:: Check all the sheet have compare result 
        ::params:
        :return:
        '''
        result = {}
        compare_folder = os.path.join(master_config.WORKING_PATH, enums.StructureKeys.COMPARE_FOLDER)
        expired_time = self.all_settings[enums.ConfigKeys.EXPIRED_TIME]
        if os.path.exists(compare_folder):
            files = [f for f in os.listdir(compare_folder) if os.path.isfile(os.path.join(compare_folder, f))]
            for file_name in files:
                file_path = os.path.join(compare_folder, file_name)
                tmp_data = utils.read_template(file_path, {})
                if tmp_data:
                    des_name = tmp_data['result']['data']['des_name']
                    src_name = tmp_data['result']['data']['src_name']
                    parse_at =  tmp_data['result']['data']['parse_at']
                    sheet_id =  tmp_data['result']['data']['src_id']
                    current_datetime  = datetime.datetime.now()
                    delta_time = utils.get_delta_time(parse_at, current_datetime)
                    if delta_time < expired_time:
                        result[src_name] = [parse_at, file_path, des_name, src_name, sheet_id]
                    else:
                        utils.remove_path(file_path)
        self.compare_result = result
        return result
    
    def get_analyze_result(self):
        '''
        ::description:: Check all the sheet have compare result 
        ::params:
        :return:
        '''
        sheet_id = self.methods.get(enums.MethodKeys.SHEET_ID)
        result = {'result': {'data': {'des_name': 'Undefied', 'src_name': 'Undefied'}}}
        compare_folder = os.path.join(master_config.WORKING_PATH, enums.StructureKeys.COMPARE_FOLDER)
        file_path = os.path.join(compare_folder, '%s.py'%sheet_id)
        if os.path.exists(file_path):
            result = utils.read_template(file_path, {})
        return result
    
    def create_dummy_data_to_commit(self, ids=[]):
        '''
        ::description:: Check all the sheet have compare result 
        ::params:
        :return:
        '''
        list_filter_ids = [int(i) for i in ids]
        
        analyze_result = self.get_analyze_result()
        data = analyze_result['result']['data']
        des_name = data['des_name']
        src_name = data['src_name']
        tmp_headers = {}
        for src_header, des_header in self.all_settings[enums.ConfigKeys.MAPPING_HEADERS]:
            src_header = utils.convert_text(src_header)
            des_header = utils.convert_text(des_header)
            tmp_headers[des_header] = {}
        result = []
        for compare_id in self.methods.get(enums.MethodKeys.IDS):
            compare_id = int(compare_id)
            if list_filter_ids and compare_id not in list_filter_ids:
                continue
            ids = data['ids']
            if ids.get(compare_id) == None:
                continue
            input_status = ids[compare_id]
            row_info = data[input_status][compare_id]
            key, src_data, des_data = row_info
            row_result = copy.deepcopy(tmp_headers)
            row_result[enums.DataKeys.COMPARE_ID] = compare_id
            for mapping_header in self.all_settings[enums.ConfigKeys.DES_MAPPING_SRC_SHEET]:
                is_exist_mapping = False
                for mapping_val in self.all_settings[enums.ConfigKeys.DES_MAPPING_SRC_SHEET][mapping_header]:
                    mapping_sheet = self.all_settings[enums.ConfigKeys.DES_MAPPING_SRC_SHEET][mapping_header][mapping_val]
                    
                    if mapping_sheet == src_name:
                        mapping_header = utils.convert_text(mapping_header)
                        row_result[mapping_header] = {enums.DataKeys.VALUE: mapping_val, enums.DataKeys.DISPLAY_VALUE: mapping_val}
                        is_exist_mapping = True
                        break
                if not is_exist_mapping:
                    row_result[mapping_header] = {enums.DataKeys.VALUE: '', enums.DataKeys.DISPLAY_VALUE: ''}
            
            row_result['compare_id'] = compare_id
            #modified des sheet
            if input_status == enums.DataKeys.MODIFIED:
                row_result[enums.DataKeys.ROW_NUMBER] = des_data[enums.DataKeys.ROW_NUMBER]
                row_result[enums.DataKeys.ROW_ID] = des_data[enums.DataKeys.ROW_ID]
                row_result[enums.DataKeys.ATTACHMENTS] = src_data[enums.DataKeys.ATTACHMENTS]
                row_result[enums.DataKeys.ATTACHMENTS_NAME] = src_data[enums.DataKeys.ATTACHMENTS_NAME]
                row_result[enums.DataKeys.ACTION] = enums.DataKeys.MODIFIED
                row_result['des_attachments'] = des_data[enums.DataKeys.ATTACHMENTS]
                
                for src_header, des_header in self.all_settings[enums.ConfigKeys.MAPPING_HEADERS]:
                    src_header = utils.convert_text(src_header)
                    des_header = utils.convert_text(des_header)
                    src_row_val = src_data[src_header]
                    row_result[des_header] = src_row_val
                    
            #add to des sheet
            elif input_status == enums.DataKeys.NEW:
                row_result[enums.DataKeys.ROW_NUMBER] = ''
                row_result[enums.DataKeys.ROW_ID] = ''
                row_result[enums.DataKeys.ATTACHMENTS] = src_data[enums.DataKeys.ATTACHMENTS]
                row_result[enums.DataKeys.ATTACHMENTS_NAME] = src_data[enums.DataKeys.ATTACHMENTS_NAME]
                row_result[enums.DataKeys.ACTION] = enums.DataKeys.ADD
                row_result['des_attachments'] = []
                for src_header, des_header in self.all_settings[enums.ConfigKeys.MAPPING_HEADERS]:
                    src_header = utils.convert_text(src_header)
                    des_header = utils.convert_text(des_header)
                    src_row_val = src_data[src_header]
                    row_result[des_header] = src_row_val
                    
            #remove in des sheet
            elif input_status == enums.DataKeys.MISSING:
                row_result[enums.DataKeys.ROW_NUMBER] = des_data[enums.DataKeys.ROW_NUMBER]
                row_result[enums.DataKeys.ROW_ID] = des_data[enums.DataKeys.ROW_ID]
                row_result[enums.DataKeys.ATTACHMENTS] = des_data[enums.DataKeys.ATTACHMENTS]
                row_result[enums.DataKeys.ATTACHMENTS_NAME] = des_data[enums.DataKeys.ATTACHMENTS_NAME]
                row_result[enums.DataKeys.ACTION] = enums.DataKeys.DELETE
                row_result['des_attachments'] = []
                
                for src_header, des_header in self.all_settings[enums.ConfigKeys.MAPPING_HEADERS]:
                    src_header = utils.convert_text(src_header)
                    des_header = utils.convert_text(des_header)
                    des_row_val = des_data[des_header]
                    row_result[des_header] = des_row_val
            
            result.append(row_result)
        self.dummy_result = result
        return result
        
    def commit_to_smartsheet(self):
        '''
        ::description:: Check all the sheet have compare result 
        ::params:
        :return:
        '''
        try:
            ids = self.methods.get(enums.MethodKeys.IDS)
            des_id = int(self.methods.get(enums.MethodKeys.DES_ID))
            src_id = int(self.methods.get(enums.MethodKeys.SHEET_ID))
            
            data = self.create_dummy_data_to_commit(ids=ids)
            smartsheet_obj = SmartSheets(sheets = [], all_settings = self.all_settings)
            smartsheet_obj.connect_smartsheet()
            smartsheet_obj.get_column_index(sheet_id = des_id)
            
            des_headers = []
            for src_header, des_header in self.all_settings[enums.ConfigKeys.MAPPING_HEADERS]:
                #src_header = utils.convert_text(src_header)
                des_header = utils.convert_text(des_header)
                des_headers.append(des_header)
                
            for mapping_header in self.all_settings[enums.ConfigKeys.DES_MAPPING_SRC_SHEET]:
                mapping_header = utils.convert_text(mapping_header)
                des_headers.append(mapping_header)
                
            len_row = len(data)
            count = 0
            utils.println('Start commit..')
            mail_data_ids = []
            for row in data:
                count += 1
                if (count % 5 == 0) or (count == len_row):
                    utils.println('Processing [%s/%s]'%(count, len_row))
                action = row[enums.DataKeys.ACTION]
                update_file = False
                compare_id = row['compare_id']
                mail_data_ids.append(compare_id)
                if action == enums.DataKeys.ADD:
                    smartsheet_obj.add_new_row(row, des_headers, des_id, src_id)
                    update_file = True
                elif action == enums.DataKeys.MODIFIED:
                    smartsheet_obj.update_row(row, des_headers, des_id, src_id)
                    update_file = True
                elif action == enums.DataKeys.DELETE:
                    smartsheet_obj.delete_row(row, des_headers, des_id, src_id)
                    update_file = True
                if update_file:
                    result = {}
                    compare_folder = os.path.join(master_config.WORKING_PATH, enums.StructureKeys.COMPARE_FOLDER)
                    result_file = os.path.join(compare_folder, '%s.py'%src_id)
                    if os.path.exists(result_file):
                        compare_data = utils.read_template(result_file, {})
                        status = compare_data['result']['data']['ids'][compare_id]
                        del compare_data['result']['data']['ids'][compare_id]
                        del compare_data['result']['data'][status][compare_id]
                        content = 'result = '
                        content += pformat(compare_data['result'], width=400)
                        utils.make_file(result_file, content, False)
            if mail_data_ids:
                self.render_commit_mail(mail_data_ids)
            utils.println('End commit')
            result = [1, 'Commit successfully']
            return result
        except Exception as e:
            utils.println(e, enums.LoggingKeys.LOGGING_EXCEPTION)
            result = [0, e]
            return result
    
    def render_commit_mail(self, mail_data_ids):
        '''
        ::description:: Check all the sheet have compare result 
        ::params:
        :return:
        '''
        utils.println('Reminding email...')
        user_name = session[enums.SessionKeys.USERNAME]
        password = session[enums.SessionKeys.PASSWORD]
        dummy_data = self.dummy_result
        template_path = g.template_path
        tool_path    = g.tool_path
        template_path = os.path.join(os.path.join(tool_path, template_path), 'tools')
        vars = {}
        vars['dummy_data'] = dummy_data
        vars['all_settings'] = self.all_settings
        vars['date'] = utils.date_to_str()
        vars['user_name'] = user_name
        vars['enums'] = enums
        content = utils.render_jinja2_template(template_path, 'commit_mail.html', vars)
        user_name = session[enums.SessionKeys.USERNAME]
        password = session[enums.SessionKeys.PASSWORD]
        recipient_mail = self.all_settings[enums.ConfigKeys.RECIPIENT_MAIL]
        cc_mail = self.all_settings[enums.ConfigKeys.CC_MAIL]
        subject = self.all_settings[enums.ConfigKeys.SUBJECT]
        bcc = ['cad_monitor@savarti.com']
        send_mail_status = utils.send_mail(user_name, password, recipient_mail, cc_mail, subject, content, bcc, False)
        utils.println('Remind email - Done')
            
            
            
        