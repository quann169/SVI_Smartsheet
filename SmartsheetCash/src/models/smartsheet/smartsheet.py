'''
Created on Feb 5, 2021

@author: toannguyen
'''
from src.commons import enums, message, utils
import sys, re, os
from pprint import pprint, pformat
import urllib
from smartsheet import smartsheet, sheets, models
import datetime
import time, stat
import master_config
import copy

class SmartSheets:
    def __init__(self, sheets=[], all_settings={}, input_type='', from_date = '', to_date = '', is_compare = False):
        self.from_date = from_date
        self.to_date = to_date
        self.sheets = sheets
        self.available_name = {}
        self.all_settings = all_settings
        self.token   = self.all_settings[enums.ConfigKeys.TOKEN]
        self.data = {}
        self.column_index = {}
        self.input_type = input_type
        self.update_attr_by_input_type()
        self.parsed_date = utils.date_to_str()
        self.is_compare = is_compare
        self.des_data = {}
        self.compare_data = {}
        self.html_split_key = '##'
        self.exist_rows = {}
        
    def set_attr(self, **kwargs):
        for key, value in kwargs.items():                  
            setattr(self, key, value)
    
    def update_attr_by_input_type(self):
        '''
        :description: set dynamic attribute by input type 
        :parameters:
        :return:
        '''
        if self.input_type == 'src':
            self.input_headers = self.all_settings[enums.ConfigKeys.SRC_HEADERS]
            self.date_header = utils.convert_text(self.all_settings[enums.ConfigKeys.SRC_DATE_HEADER])
            self.compare_headers = self.all_settings[enums.ConfigKeys.SRC_COMPARE_HEADERS]
            self.empty_headers = self.all_settings[enums.ConfigKeys.SRC_EMPTY_HEADERS]
            self.none_empty_headers = self.all_settings[enums.ConfigKeys.SRC_NONE_EMPTY_HEADERS]
            self.is_seperate_sheet = False
        elif self.input_type == 'des':
            self.input_headers = self.all_settings[enums.ConfigKeys.DES_HEADERS]
            self.date_header = utils.convert_text(self.all_settings[enums.ConfigKeys.DES_DATE_HEADER])
            self.compare_headers = self.all_settings[enums.ConfigKeys.DES_COMPARE_HEADERS]
            self.empty_headers = self.all_settings[enums.ConfigKeys.DES_EMPTY_HEADERS]
            self.none_empty_headers = self.all_settings[enums.ConfigKeys.DES_NONE_EMPTY_HEADERS]
            self.is_seperate_sheet = True
            
    def connect_smartsheet(self):
        '''
        :description:
        :parameters:
        :return:
        '''
        utils.println('Connecting to smartsheet')
        self.smartsheet_obj = smartsheet.Smartsheet(self.token)
        self.master_sheet_obj = sheets.Sheets(self.smartsheet_obj)
        self.get_available_sheet_name()
        utils.println('Connect to smartsheet - Done')
        
    def get_available_sheet_name(self):
        '''
        ::description:: get alss available sheet name
        ::params:
        :return:
        '''
        list_sheet = self.master_sheet_obj.list_sheets(include_all=True)
        if not self.available_name:
            for sheet in list_sheet.data:
                sheet_name = sheet.name
                sheet_id = sheet.id
                if self.available_name.get(sheet_name):
                    utils.println('Sheet name %s exists.'%sheet_name, enums.LoggingKeys.LOGGING_WARNING)
                else:
                    self.available_name[sheet_name] = sheet_id
        #pprint (self.available_name)
        
    def get_row_data(self, row, sheet_name, sheet_id, parse_rows, skip_rows):
        '''
        ::description::
        ::params:
        :return:
        '''
        
        row_number = row.row_number
        cells =  row.cells
        columns =  row.columns
        created_at =  row.created_at
        created_by =  row.created_by
        discussions =  row.discussions
        row_id =  row.id_
        modified_at =  row.modified_at
        modified_by =  row.modified_by
        parent_id =  row.parent_id
        sibling_id =  row.sibling_id
        tmp_row_data = {}
        for header in self.column_index[sheet_name]:
            idx = self.column_index[sheet_name][header]['index']
            cell_info = cells[idx]
            display_value = cell_info.display_value
            value = cell_info.value
            if not display_value:
                display_value = ''
            if not value:
                value = ''
            value = utils.convert_text(value)
            display_value = utils.convert_text(display_value)
            tmp_row_data[header] = {'display_value': display_value, 'value': value}
        tmp_row_data[header] = {'display_value': display_value, 'value': value}
        tmp_row_data[enums.DataKeys.ROW_ID] = row_id
        tmp_row_data[enums.DataKeys.ROW_NUMBER] = row_number
        row_date = tmp_row_data[self.date_header]['value']
        
        #Rule to detect row contains data to parse
        is_data_row = True
        skip_reason = ''
        #require empty cell
        for header in self.empty_headers:
            header = utils.convert_text(header)
            if tmp_row_data.get(header) and tmp_row_data[header].get('value'):
                is_data_row = False
                skip_reason = 'Column %s is not empty.'%(header)
        
        #require none empty cell
        for header in self.none_empty_headers:
            header = utils.convert_text(header)
            if not tmp_row_data.get(header) and (not tmp_row_data[header].get('value')):
                is_data_row = False
                skip_reason = 'Column %s is empty.'%(header)
                
        is_add = True
        tmp_row_data['mapping_sheet_name'] = ''
        if self.is_seperate_sheet:
            is_add = False
            for header in self.all_settings[enums.ConfigKeys.DES_MAPPING_SRC_SHEET]:
                for cfg_value in self.all_settings[enums.ConfigKeys.DES_MAPPING_SRC_SHEET][header]:
                    sheet_cfg = self.all_settings[enums.ConfigKeys.DES_MAPPING_SRC_SHEET][header][cfg_value]
                    value = tmp_row_data[header].get('value')
                    if value == cfg_value:
                        tmp_sheet_name = sheet_cfg
                        is_add = True
                        tmp_row_data['mapping_sheet_name'] = sheet_cfg
                        break
        
        if is_data_row:
            if is_add:
                if row_date:
                    #only get row inside from/to date
                    if utils.compare_date(row_date, self.from_date) and utils.compare_date(self.to_date, row_date):
                        att_data = []
                        list_att_name = []
                        attachments = self.smartsheet_obj.Attachments.list_row_attachments(sheet_id=sheet_id, row_id=row_id, include_all=True)
                        total_count = attachments.total_count
                        if total_count:
                            for element in attachments.data:
                                att_data.append({
                                    'id' : element.id,
                                    # 'attachment_type' : element.attachment_type,
                                    # 'created_at' : element.created_at,
                                    # 'created_by' : element.created_by,
                                    'mime_type' : element.mime_type,
                                    'size_in_kb' : element.size_in_kb,
                                    'name' : element.name,
                                    'parent_id' : element.parent_id,
                                    # 'parent_type' : element.parent_type
                                    })
                                list_att_name.append(element.name)
                        
                        tmp_row_data[enums.DataKeys.ATTACHMENTS] = att_data
                        self.data[sheet_id]['rows'][row_number] = tmp_row_data
                        list_att_name.sort()
                        tmp_row_data['attachments_name'] = list_att_name
                        #data to compare
                        value_compare = []
                        # value_compare += list_att_name
                        for header in self.compare_headers:
                            value_compare.append(str(tmp_row_data[header].get('value', '')))
                        key_compare = ' - '.join(value_compare)
                        self.compare_data[sheet_id]['rows'][row_number] = key_compare
                        parse_rows.append(tmp_row_data)
                    else:
                        skip_rows.append(['Column %s exceed of start/end date'%self.date_header, tmp_row_data])#[skip_reason, data]
                else:
                    skip_rows.append(['Column %s is empty'%self.date_header, tmp_row_data])#[skip_reason, data]
            else:
                skip_rows.append(['Can not find src sheet name', tmp_row_data])#[skip_reason, data]
        else:
            skip_rows.append([skip_reason, tmp_row_data])#[skip_reason, data]
        
        
        
    def get_column_index(self, column=None, sheet_name=None, sheet_id=None):
        '''
        ::description:: get information from smartsheet
        ::params:
        :return:
        '''
        if not sheet_id:
            utils.add_keys_to_dict(self.column_index, sheet_name, {})
            idx = column.index
            column_id = column.id
            column_name = column.title
            column_name = utils.convert_text(column_name)
            utils.add_keys_to_dict(self.column_index[sheet_name], column_name, {})
            self.column_index[sheet_name][column_name]['index'] = idx
            self.column_index[sheet_name][column_name]['id'] = column_id
        else:
            sheet_obj = self.master_sheet_obj.get_sheet(sheet_id = sheet_id, include='all')
            rows = sheet_obj.rows
            columns = sheet_obj.columns
            for column in columns:
                utils.add_keys_to_dict(self.column_index, sheet_id, {})
                idx = column.index
                column_id = column.id
                column_name = column.title
                column_name = utils.convert_text(column_name)
                utils.add_keys_to_dict(self.column_index[sheet_id], column_name, {})
                self.column_index[sheet_id][column_name]['index'] = idx
                self.column_index[sheet_id][column_name]['id'] = column_id
    
    def record_sheet_data(self, sheet_id):
        '''
        ::description:: save data to file --> using for review and debug
        ::params:
        :return:
        '''
        #write data to file
        sheet_data = self.data[sheet_id]
        compare_data = self.compare_data[sheet_id]
        parse_folder = os.path.join(master_config.WORKING_PATH, enums.StructureKeys.PARSE_FOLDER)
        utils.make_folder(parse_folder)
        result_file = os.path.join(parse_folder, '%s.py'%sheet_id)
        content = 'data = '
        content += pformat(sheet_data, width=400)
        content += '\ncompare_data = '
        content += pformat(compare_data, width=400)
        utils.make_file(result_file, content)
    
    def compare_two_sheet(self, src_data, des_data, src_compare_data, des_compare_data):
        '''
        ::description:: save data to file --> using for review and debug
        ::params:
        :return:
        '''
        #write data to file
        compare_data = {}
        des_id = des_data['sheet_id']
        src_id = src_data['sheet_id']
        des_name = des_data['sheet_name']
        src_name = src_data['sheet_name']
        utils.add_keys_to_dict(compare_data, 
                               'data', 
                               { 
                                    enums.DataKeys.NEW: {},
                                    enums.DataKeys.MISSING: {}, 
                                    enums.DataKeys.MODIFIED: {}, 
                                    enums.DataKeys.UNCHANGED: {}, 
                                    'des_name': des_name, 
                                    'src_name' : src_name, 
                                    'des_id': des_id, 
                                    'src_id' : src_id, 
                                    'parse_at': self.parsed_date,
                                    'ids': {},
                                }
                            )
        compare_index = 1
        #status add 
        src_sheet = src_data['sheet_name']
        for row_number_1 in src_compare_data['rows']:
            src_row_info = src_data['rows'][row_number_1]
            des_row_info= {}
            src_key = src_compare_data['rows'].get(row_number_1)
            is_exist = False
            for row_number_2 in des_compare_data['rows']:
                des_key = des_compare_data['rows'].get(row_number_2)
                if src_key == des_key:
                    mapping_sheet_name = des_data['rows'][row_number_2]['mapping_sheet_name']
                    if mapping_sheet_name == src_sheet:
                        is_exist = True
                        des_row_info = des_data['rows'][row_number_2]
                        break
            if is_exist:
                #unchanges
                #[src_key, src_row_info, des_row_info]
                #check_modified
                is_modified = False
                #check attach file
                src_attact_name = src_row_info['attachments_name']
                des_attact_name = des_row_info['attachments_name']
                if src_attact_name != des_attact_name:
                    is_modified = True
                #check columns val
                for idx in range(0, len(self.all_settings[enums.ConfigKeys.SRC_CHECK_MODIFIED_HEADERS])):
                    src_header = self.all_settings[enums.ConfigKeys.SRC_CHECK_MODIFIED_HEADERS][idx]
                    des_header = self.all_settings[enums.ConfigKeys.DES_CHECK_MODIFIED_HEADERS][idx]
                    if src_row_info[src_header]['value'] != des_row_info[des_header]['value']:
                        is_modified = True
                if is_modified:
                    src_compare_id = int('%s00%s'%(src_id, compare_index))
                    compare_data['data'][enums.DataKeys.MODIFIED][src_compare_id] = [src_key, src_row_info, des_row_info]
                    compare_data['data']['ids'][src_compare_id] = enums.DataKeys.MODIFIED
                    compare_index += 1
            else:
                #[src_key, src_row_info, des_row_info]
                src_compare_id = int('%s00%s'%(src_id, compare_index))
                compare_data['data'][enums.DataKeys.NEW][src_compare_id] = [src_key, src_row_info, des_row_info]
                compare_data['data']['ids'][src_compare_id] = enums.DataKeys.NEW
                compare_index += 1
                
        #status del 
        for row_number_1 in des_compare_data['rows']:
            des_row_info = des_data['rows'][row_number_1]
            src_row_info= {}
            des_key = des_compare_data['rows'].get(row_number_1)
            is_exist = False
            for row_number_2 in src_compare_data['rows']:
                src_key = src_compare_data['rows'].get(row_number_2)
                if src_key == des_key:
                    mapping_sheet_name = des_data['rows'][row_number_1]['mapping_sheet_name']
                    if mapping_sheet_name == src_sheet:
                        is_exist = True
                        src_row_info = src_data['rows'][row_number_2]
                        break
            if is_exist:
                pass
            else:
                #[des_key, src_row_info, des_row_info]
                src_compare_id = int('%s00%s'%(src_id, compare_index))
                compare_data['data'][enums.DataKeys.MISSING][src_compare_id] = [des_key, src_row_info, des_row_info]
                compare_data['data']['ids'][src_compare_id] = enums.DataKeys.MISSING
                compare_index += 1
      
        compare_folder = os.path.join(master_config.WORKING_PATH, enums.StructureKeys.COMPARE_FOLDER)
        utils.make_folder(compare_folder)
        result_file = os.path.join(compare_folder, '%s.py'%src_id)
        content = 'result = '
        content += pformat(compare_data, width=400)
        utils.make_file(result_file, content)
        
    def parse_smartsheet(self):
        '''
        ::description:: get information from smartsheet
        ::params:
        :return:
        '''
        self.connect_smartsheet()
        for sheet_name in self.sheets:
            utils.println('Sheet name "%s"'%sheet_name)
            if not self.available_name.get(sheet_name):
                text = utils.message_generate(message.MsgError.E006, sheet_name)
                utils.println(text, enums.LoggingKeys.LOGGING_ERROR)
                break
            sheet_id = self.available_name[sheet_name]
            #sheet_obj = self.master_sheet_obj.get_sheet_by_name(name = sheet_name, include='all')
            sheet_obj = self.master_sheet_obj.get_sheet(sheet_id = sheet_id, include='all')
            compare_folder = os.path.join(master_config.WORKING_PATH, enums.StructureKeys.COMPARE_FOLDER)
            parse_folder = os.path.join(master_config.WORKING_PATH, enums.StructureKeys.PARSE_FOLDER)
            result_file = os.path.join(compare_folder, '%s.py'%sheet_id)
            parse_row_file = os.path.join(parse_folder, '%s_parse_rows.html'%sheet_id)
            skip_row_file = os.path.join(parse_folder, '%s_skip_rows.html'%sheet_id)
            utils.remove_path(result_file)
            utils.remove_path(parse_row_file)
            utils.remove_path(skip_row_file)
            
            result_file = os.path.join(parse_folder, '%s.py'%sheet_id)
            utils.remove_path(result_file)
            rows = sheet_obj.rows
            columns = sheet_obj.columns
            utils.println('Calculate headers')
            for header in self.input_headers:
                header = utils.convert_text(header)
                is_exist = False
                for column in columns:
                    column_name = column.title
                    if header == column_name:
                        is_exist = True
                        self.get_column_index(column, sheet_name)
                        break
                if not is_exist:
                    text = utils.message_generate(message.MsgError.E007, header)
                    utils.println(text, enums.LoggingKeys.LOGGING_ERROR)
                    break
            utils.add_keys_to_dict(self.data, sheet_id, {'rows': {}, 'sheet_id': sheet_id, 'sheet_name': sheet_name, 'parse_at': self.parsed_date})
            utils.add_keys_to_dict(self.compare_data, sheet_id, {'rows': {}, 'sheet_id': sheet_id, 'sheet_name': sheet_name, 'parse_at': self.parsed_date})
            count = 0
            total_row = len(rows)
            utils.println('Calculate rows')
            parse_rows = []
            skip_rows = []
            for row in rows:
                count += 1
                if ((count % 100) == 0) or (count == total_row):
                    utils.println('Processing  [%s/%s] rows.'%(count, total_row))
                self.get_row_data(row, sheet_name, sheet_id, parse_rows, skip_rows)
                
            parse_folder = os.path.join(master_config.WORKING_PATH, enums.StructureKeys.PARSE_FOLDER)
            utils.make_folder(parse_folder)
            try:
                style_text = '''<style>
                table tr {
  border: 1px solid #aaa ;
}

table th {
  padding: 0.5rem !important;
  font-weight: bold;
  border: 1px solid #aaa !important;
}

table td {
  padding: 0.5rem  !important;
  border: 1px solid #aaa !important;
}</style>'''
                #Parse rows
                result_file = os.path.join(parse_folder, '%s_parse_rows.html'%sheet_id)
                content = '%s<table><thead><tr>'%style_text
                for header in self.column_index[sheet_name]:
                    content += '<th>%s</th>'%(header)
                content += '</tr></thead><tbody>'
                for row_data in parse_rows:
                    content += '<tr>'
                    for header in self.column_index[sheet_name]:
                        header = utils.convert_text(header)
                        content += '<td>%s</td>'%(row_data[header]['value'])
                    content += '</tr>'
                content += '</tbody></table>'
                content = utils.revert_text(content)
                utils.make_file(result_file, content)
                
                #Skip rows
                result_file = os.path.join(parse_folder, '%s_skip_rows.html'%sheet_id)
                content = '%s<table><thead><tr>'%style_text
                for header in self.column_index[sheet_name]:
                    content += '<th>%s</th>'%(header)
                content += '<th>Reason</th>'
                content += '</tr></thead><tbody>'
                for element in skip_rows:
                    reason, row_data = element
                    content += '<tr>'
                    for header in self.column_index[sheet_name]:
                        header = utils.convert_text(header)
                        content += '<td>%s</td>'%(row_data[header]['value'])
                    content += '<td>%s</td>'%reason
                    content += '</tr>'
                content += '</tbody></table>'
                content = utils.revert_text(content)
                utils.make_file(result_file, content)
            except:
                pass
            utils.println('Total rows have data %s'%(len(self.data[sheet_id]['rows'])))
            self.record_sheet_data(sheet_id)
            sheet_data = self.data[sheet_id]
            compare_sheet_data = self.compare_data[sheet_id]
            if self.input_type == 'des':
                self.des_data = sheet_data
                self.des_compare_data = compare_sheet_data
            else:
                if self.is_compare:
                    self.compare_two_sheet(src_data = sheet_data, des_data = self.des_data, 
                                           src_compare_data = compare_sheet_data, des_compare_data = self.des_compare_data)
            utils.println('Sheet name "%s" Done'%sheet_name)
            
    def dowload_attachments(self, att_list, des_id, src_id):
        '''
        ::description:: dowload_attachments
        ::params:
        :return:
        '''
        attachments_folder = os.path.join(master_config.WORKING_PATH, enums.StructureKeys.ATTACHMENTS_FOLDER)
        utils.make_folder(attachments_folder)
        des_dir = os.path.join(attachments_folder, str(src_id))
        utils.make_folder(des_dir)
        for attach in att_list:
            att_id = attach['id']  #get the id of the attachment
            att_name = attach['name']  # get the name of the attachment
            retrieve_att = self.smartsheet_obj.Attachments.get_attachment(src_id, att_id)  #downloads the atachment
            dest_file = os.path.join(des_dir, str(att_name))  # parsing the destination path
            dwnld_url = retrieve_att.url # this link gives you access to download the file for about 5 to 10 min. before expire
            urllib.request.urlretrieve(dwnld_url, dest_file) ## retrieving attachement and saving locally
    
    def upload_attachments(self, att_list, des_id, src_id, row_id):
        '''
        ::description:: upload_attachments
        ::params:
        :return:
        '''
        attachments_folder = os.path.join(master_config.WORKING_PATH, enums.StructureKeys.ATTACHMENTS_FOLDER)
        des_dir = os.path.join(attachments_folder, str(src_id))
        for attach in att_list:
            att_id = attach['id']  #get the id of the attachment
            att_name = attach['name']  # get the name of the attachment
            att_type = attach['mime_type']  # get the name of the attachment
            dest_file = os.path.join(des_dir, str(att_name))
            updated_attachment = self.smartsheet_obj.Attachments.attach_file_to_row(
              des_id,       # sheet_id
              row_id,       # row_id
              (att_name,
                open(dest_file, 'rb'),
                att_type)
            )
    
    def remove_attachments(self, att_list, des_id, src_id, row_id):
        '''
        ::description:: upload_attachments
        ::params:
        :return:
        '''
        attachments_folder = os.path.join(master_config.WORKING_PATH, enums.StructureKeys.ATTACHMENTS_FOLDER)
        des_dir = os.path.join(attachments_folder, str(src_id))
        for attach in att_list:
            att_id = attach['id']  #get the id of the attachment
            att_name = attach['name']  # get the name of the attachment
            att_type = attach['mime_type']  # get the name of the attachment
            dest_file = os.path.join(des_dir, str(att_name))
            updated_attachment = self.smartsheet_obj.Attachments.delete_attachment(des_id, att_id)
            
        
    def add_new_row(self, row_data, des_headers, sheet_id, src_id):
        '''
        ::description:: add new row to smartsheet
        ::params:
        :return:
        '''
        row_obj = models.Row()
        row_obj.to_bottom = True
        att_list = row_data[enums.DataKeys.ATTACHMENTS]
        for header in des_headers:
            column_id = self.column_index[sheet_id][header]['id']
            cell_data = row_data[header]
            row_obj.cells.append({
              'column_id': column_id,
              'value': cell_data.get(enums.DataKeys.VALUE),
              'display_value': cell_data.get(enums.DataKeys.DISPLAY_VALUE)
            })
        
        # Add rows to sheet
        response = self.master_sheet_obj.add_rows(sheet_id, [row_obj])
        row_id  = response.result[0].id
        #row_id = 1706567723771780#173192458397572
        self.dowload_attachments(att_list, sheet_id, src_id)
        self.upload_attachments(att_list, sheet_id, src_id, row_id)
        
    def delete_row(self, row_data, des_headers, sheet_id, src_id):
        '''
        ::description:: delete row of smartsheet
        ::params:
        :return:
        '''
        row_id = row_data[enums.DataKeys.ROW_ID]
        response = self.master_sheet_obj.delete_rows(sheet_id, [row_id])
        
        
    def update_row(self, row_data, des_headers, sheet_id, src_id):
        '''
        ::description:: delete row of smartsheet
        ::params:
        :return:
        '''
        row_id = row_data[enums.DataKeys.ROW_ID]
        row_obj = models.Row()
        row_obj.id = row_id
        cells_obj = []
        att_list = row_data[enums.DataKeys.ATTACHMENTS]
        des_attachments = row_data['des_attachments']
        for header in des_headers:
            column_id = self.column_index[sheet_id][header]['id']
            cell_data = row_data[header]
            row_obj.cells.append({
              'column_id': column_id,
              'value': cell_data.get(enums.DataKeys.VALUE),
              'display_value': cell_data.get(enums.DataKeys.DISPLAY_VALUE)
            })

        response = self.master_sheet_obj.update_rows(sheet_id, [row_obj])
        self.dowload_attachments(att_list, sheet_id, src_id)
        self.upload_attachments(att_list, sheet_id, src_id, row_id)
        if not self.all_settings.get(enums.ConfigKeys.SKIP_REMOVE_ATTACHMENTS):
            self.remove_attachments(des_attachments, sheet_id, src_id, row_id)
        
            