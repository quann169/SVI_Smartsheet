'''
Created on Feb 22, 2021

@author: toannguyen
'''
from src.models.smartsheet.smartsheet import SmartSheets
from src.commons import enums, utils
from flask import g, session
from pprint import pprint, pformat
import pandas as pd

import os, sys, getpass, datetime, copy, ast
import master_config
import time

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
        self.all_settings = utils.read_template(setting_file, {})
        for group_config in  self.all_settings[enums.ConfigKeys.GROUPS]:
            for input_type in [enums.ConfigKeys.SOURCE, enums.ConfigKeys.DESTINATION]:
                group_config[input_type]['sheets'] = group_config[input_type][enums.ConfigKeys.SHEET_NAME]
                group_config[input_type]['input_headers'] = group_config[input_type][enums.ConfigKeys.HEADERS].keys()
                #reset attr
                group_config[input_type]['date_headers'] = []
                group_config[input_type]['compare_headers'] = []
                group_config[input_type]['empty_headers'] = []
                group_config[input_type]['none_empty_headers'] = []
                group_config[input_type]['modified_headers'] = []
                group_config[input_type]['mapping_values'] = {}
                group_config[input_type]['default_value'] = {}
                group_config[input_type][enums.ConfigKeys.DATA_TYPE] = {}
                
                for header in group_config[input_type]['input_headers']:
                    header_cvt = utils.convert_text(header)
                    for key in group_config[input_type][enums.ConfigKeys.HEADERS][header]:
                        value = group_config[input_type][enums.ConfigKeys.HEADERS][header][key]
                        #Date header
                        if key == enums.ConfigKeys.IS_DATE:
                            if value:
                                group_config[input_type]['date_headers'].append(header)
                        #compare_headers
                        elif key == enums.ConfigKeys.COMPARE_INDEX:
                            if value != None:
                                utils.create_list(group_config[input_type]['compare_headers'], value, header)
                        #empty_headers
                        elif key == enums.ConfigKeys.IS_EMPTY:
                            if value:
                                group_config[input_type]['empty_headers'].append(header)
                        #none_empty_headers
                        elif key == enums.ConfigKeys.IS_NONE_EMPTY:
                            if value:
                                group_config[input_type]['none_empty_headers'].append(header)   
                        #modified headers
                        elif key == enums.ConfigKeys.MODIFIED_INDEX:
                            if value != None:
                                utils.create_list(group_config[input_type]['modified_headers'], value, header)
                        #data type
                        elif key == enums.ConfigKeys.DATA_TYPE:
                            if value:
                                group_config[input_type][enums.ConfigKeys.DATA_TYPE][header] = value
                        #default_value
                        elif key == enums.ConfigKeys.DEFAULT_VALUE:
                            group_config[input_type]['default_value'][header] = value
                        #value_mapping
                        elif key == enums.ConfigKeys.MAPPING_VALUES:
                            if value:
                                group_config[input_type]['mapping_values'][header] = value
                        
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
        log_folder = os.path.join(master_config.WORKING_PATH, enums.StructureKeys.CONSOLE_FOLDER)
        utils.make_folder(log_folder)
        log_file = os.path.join(log_folder, 'analyze.log')
        utils.remove_path(log_file)
        sys.stdout = open(log_file, 'w')
        try:
            sheets = self.methods[enums.MethodKeys.SHEETS]
            from_date = self.methods[enums.MethodKeys.FROM_DATE]
            to_date = self.methods[enums.MethodKeys.TO_DATE]
            parsed_date = utils.date_to_str()
            for element in sheets:
                group_index, src_name, des_name = element
                group_index = int(group_index)
                smartsheet_obj = SmartSheets(all_settings = self.all_settings, 
                                             input_type = enums.ConfigKeys.DESTINATION, 
                                             from_date = from_date, 
                                             to_date = to_date,
                                             is_compare=False,
                                             group_index = group_index,
                                             parsed_date = parsed_date)
                utils.println('Start parse destination sheet')
                smartsheet_obj.parse_smartsheet()
                utils.println('Parse destination sheet - Done')
                utils.println('Start parse source sheet')
                smartsheet_obj.set_attr(input_type = enums.ConfigKeys.SOURCE, is_compare = True)
                smartsheet_obj.update_attr_by_input_type()
                smartsheet_obj.parse_smartsheet()
                utils.println('Parse source sheet - Done')

            utils.println('Parse data - Done')
            result = [1, 'Parse successfully']
            sys.stdout = sys.__stdout__
            return result
        except Exception as e:
            utils.println(e, enums.LoggingKeys.LOGGING_EXCEPTION)
            result = [0, e]
            sys.stdout = sys.__stdout__
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
                    src_id =  tmp_data['result']['data']['src_id']
                    des_id =  tmp_data['result']['data']['des_id']
                    current_datetime  = datetime.datetime.now()
                    delta_time = utils.get_delta_time(parse_at, current_datetime)
                    if delta_time < expired_time:
                        result[src_name] = [parse_at, file_path, src_name, src_id, des_name, des_id]
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
        
        src_id = self.methods.get(enums.MethodKeys.SRC_ID)
        des_id = self.methods.get(enums.MethodKeys.DES_ID)
        result = {'result': {'data': {'des_name': 'Undefied', 'src_name': 'Undefied'}}}
        compare_folder = os.path.join(master_config.WORKING_PATH, enums.StructureKeys.COMPARE_FOLDER)
        file_path = os.path.join(compare_folder, '%s_%s.py'%(src_id, des_id))
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
        group_id = int(self.methods[enums.MethodKeys.GROUP_INDEX])
        group_config = self.all_settings[enums.ConfigKeys.GROUPS][group_id]
        analyze_result = self.get_analyze_result()
        data = analyze_result['result']['data']
        des_name = data['des_name']
        src_name = data['src_name']
        tmp_headers = {}
        for src_header, des_header in group_config[enums.ConfigKeys.MAPPING_HEADERS]:
            src_header = utils.convert_text(src_header)
            des_header = utils.convert_text(des_header)
            tmp_headers[des_header] = {}
        result = []
        missing_ids = []
        if data.get(enums.DataKeys.MISSING):
            missing_ids = list(data.get(enums.DataKeys.MISSING).keys())
        method_ids = self.methods.get(enums.MethodKeys.IDS)
        method_ids = method_ids + missing_ids
        
        if list_filter_ids:
            list_filter_ids = list_filter_ids + missing_ids
        for compare_id in method_ids:
            compare_id = int(compare_id)
            if list_filter_ids and compare_id not in list_filter_ids:
                continue
            ids2 = data['ids']
            if ids2.get(compare_id) == None:
                continue
            input_status = ids2[compare_id]
            row_info = data[input_status][compare_id]
            key, src_data, des_data = row_info
            row_result = copy.deepcopy(tmp_headers)
            row_result[enums.DataKeys.COMPARE_ID] = compare_id
            
            for header in group_config[enums.ConfigKeys.DESTINATION][enums.ConfigKeys.DEFAULT_VALUE]:
                header = utils.convert_text(header)
                default_value = group_config[enums.ConfigKeys.DESTINATION][enums.ConfigKeys.DEFAULT_VALUE][header]
                default_value = utils.convert_text(default_value)
                row_result[header] = {enums.DataKeys.VALUE: default_value, enums.DataKeys.DISPLAY_VALUE: default_value}
            
            row_result['compare_id'] = compare_id
            #modified des sheet
            if input_status == enums.DataKeys.MODIFIED:
                row_result[enums.DataKeys.ROW_NUMBER] = des_data[enums.DataKeys.ROW_NUMBER]
                row_result[enums.DataKeys.ROW_ID] = des_data[enums.DataKeys.ROW_ID]
                row_result[enums.DataKeys.ATTACHMENTS] = src_data[enums.DataKeys.ATTACHMENTS]
                row_result[enums.DataKeys.ATTACHMENTS_NAME] = src_data[enums.DataKeys.ATTACHMENTS_NAME]
                row_result[enums.DataKeys.ACTION] = enums.DataKeys.MODIFIED
                row_result['des_attachments'] = des_data[enums.DataKeys.ATTACHMENTS]
                
                for src_header, des_header in group_config[enums.ConfigKeys.MAPPING_HEADERS]:
                    if src_header and des_header:
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
                for src_header, des_header in group_config[enums.ConfigKeys.MAPPING_HEADERS]:
                    if src_header and des_header:
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
                
                for src_header, des_header in group_config[enums.ConfigKeys.MAPPING_HEADERS]:
                    if src_header and des_header:
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
        log_folder = os.path.join(master_config.WORKING_PATH, enums.StructureKeys.CONSOLE_FOLDER)
        utils.make_folder(log_folder)
        log_file = os.path.join(log_folder, 'commit.log')
        utils.remove_path(log_file)
        sys.stdout = open(log_file, 'w')
        try:
            ids = self.methods.get(enums.MethodKeys.IDS)
            des_id = int(self.methods.get(enums.MethodKeys.DES_ID))
            src_id = int(self.methods.get(enums.MethodKeys.SRC_ID))
            group_index = int(self.methods.get(enums.MethodKeys.GROUP_INDEX))
            group_config = self.all_settings[enums.ConfigKeys.GROUPS][group_index]
            
            data = self.create_dummy_data_to_commit(ids=ids)
            smartsheet_obj = SmartSheets(all_settings = self.all_settings, 
                                         group_index = group_index)
            smartsheet_obj.connect_smartsheet()
            smartsheet_obj.get_column_index(sheet_id = des_id)
            
            des_headers = []
            for src_header, des_header in group_config[enums.ConfigKeys.MAPPING_HEADERS]:
                #src_header = utils.convert_text(src_header)
                des_header = utils.convert_text(des_header)
                des_headers.append(des_header)
                
            attachments_folder = os.path.join(master_config.WORKING_PATH, enums.StructureKeys.ATTACHMENTS_FOLDER)
            utils.remove_path(attachments_folder)
            len_row = len(data)
            count = 0
            utils.println('Start commit..')
            mail_data_ids = []
            for row in data:
                count += 1
                if (count % 2 == 0) or (count == len_row):
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
                    #smartsheet_obj.delete_row(row, des_headers, des_id, src_id)
                    update_file = False
                if update_file:
                    result = {}
                    compare_folder = os.path.join(master_config.WORKING_PATH, enums.StructureKeys.COMPARE_FOLDER)
                    result_file = os.path.join(compare_folder, '%s_%s.py'%(src_id, des_id))
                    if os.path.exists(result_file):
                        compare_data = utils.read_template(result_file, {})
                        status = compare_data['result']['data']['ids'][compare_id]
                        del compare_data['result']['data']['ids'][compare_id]
                        del compare_data['result']['data'][status][compare_id]
                        content = 'result = '
                        content += pformat(compare_data['result'], width=400)
                        utils.make_file(result_file, content, False)
            if mail_data_ids:
                self.render_commit_mail(mail_data_ids, group_index)
                pass
            utils.println('End commit')
            result = [1, 'Commit successfully']
            sys.stdout = sys.__stdout__
            return result
        except Exception as e:
            utils.println(e, enums.LoggingKeys.LOGGING_EXCEPTION)
            result = [0, e]
            sys.stdout = sys.__stdout__
            return result
    
    def render_commit_mail(self, mail_data_ids, group_index):
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
        vars['group_id'] = group_index
        vars['enums'] = enums
        vars['utils'] = utils
        content = utils.render_jinja2_template(template_path, 'commit_mail.html', vars)
        user_name = session[enums.SessionKeys.USERNAME]
        password = session[enums.SessionKeys.PASSWORD]
        recipient_mail = self.all_settings[enums.ConfigKeys.RECIPIENT_MAIL]
        cc_mail = self.all_settings[enums.ConfigKeys.CC_MAIL]
        subject = self.all_settings[enums.ConfigKeys.SUBJECT]
        bcc = ['cad_monitor@savarti.com']
        send_mail_status = utils.send_mail(user_name, password, recipient_mail, cc_mail, subject, content, bcc, False)
        utils.println('Remind email - Done')
            
        
    def render_console_content(self):
        '''
        Render html content for qa_run console modal 
        ::params:: 
        ::return:: html
        '''
        path = self.methods.get(enums.MethodKeys.PATH)
        try:
            f = open(path, 'r')
            result = f.read()
            f.close()
        except:
            result = ''
        return result
    
    def render_compare_detail_modal_content(self):
        '''
        Render html content for compare detail modal
        ::params:: 
        ::return:: html
        '''
        ids = self.methods.get(enums.MethodKeys.IDS)
        des_id = int(self.methods.get(enums.MethodKeys.DES_ID))
        src_id = int(self.methods.get(enums.MethodKeys.SRC_ID))
        group_index = int(self.methods.get(enums.MethodKeys.GROUP_INDEX))
        group_config = self.all_settings[enums.ConfigKeys.GROUPS][group_index]
        compare_id = int(self.methods.get(enums.MethodKeys.COMPARE_ID))
        analyze_result = self.get_analyze_result()
        status = analyze_result['result']['data']['ids'][compare_id]
        src_data = analyze_result['result']['data'][status][compare_id][1]
        des_data = analyze_result['result']['data'][status][compare_id][2]
        des_name = analyze_result['result']['data']['des_name']
        src_name = analyze_result['result']['data']['src_name']
        
        mapping_headers = group_config[enums.ConfigKeys.MAPPING_HEADERS]
        src_headers = group_config[enums.ConfigKeys.SOURCE]['input_headers']
        # src_compare_headers = group_config[enums.ConfigKeys.SOURCE]['compare_headers']
        # src_modified_headers = group_config[enums.ConfigKeys.SOURCE]['modified_headers']
        des_headers = group_config[enums.ConfigKeys.DESTINATION]['input_headers']
        # des_compare_headers = group_config[enums.ConfigKeys.DESTINATION]['compare_headers']
        # des_modified_headers = group_config[enums.ConfigKeys.DESTINATION]['modified_headers']
        
        common_headers = {'attachments_name': 'attachments_name'}
        src_private_headers = []
        des_private_headers = []
        for element in mapping_headers:
            src_header, des_header = element
            src_header = utils.convert_text(src_header)
            des_header = utils.convert_text(des_header)
            if src_header and des_header:
                common_headers[src_header] = des_header
        
        for header in src_headers:
            header = utils.convert_text(header)
            if header not in common_headers.keys():
                src_private_headers.append(header)
        for header in des_headers:
            header = utils.convert_text(header)
            if header not in common_headers.values():
                des_private_headers.append(header)
        
        template_path = g.template_path
        tool_path    = g.tool_path
        template_path = os.path.join(os.path.join(tool_path, template_path), 'screens/analyze/')
        vars = {}
        
        vars['all_settings'] = self.all_settings
        vars['group_id'] = group_index
        vars['group_config'] = group_config
        vars['des_data'] = des_data
        vars['src_data'] = src_data   
        vars['src_name'] = src_name   
        vars['des_name'] = des_name        
        vars['enums'] = enums
        vars['utils'] = utils
        vars['status'] = status
        vars['common_headers'] = common_headers
        vars['src_private_headers'] = src_private_headers
        vars['des_private_headers'] = des_private_headers
        
        result = utils.render_jinja2_template(template_path, 'detail_modal.html', vars)
        return result
        
           
            
        