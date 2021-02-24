'''
Created on Feb 22, 2021

@author: toannguyen
'''
from src.models.smartsheet.SmartsheetModel import Sheet, Task, SmartSheets
from src.models.database.DatabaseModel import Configuration, Task, FinalTask
from src.commons.Enums import DbHeader, DbTable
from pprint import pprint


class Controllers:
    def __init__(self):
        pass
    
    def parse_smarsheet_and_update_task(self, list_sheet_id=None):
        cfg_obj = Configuration()
        sheet_info  = cfg_obj.get_sheet_config(list_sheet_id)
        list_sheet  = []
        for row in sheet_info:
            list_sheet.append((row[DbHeader.SHEET_NAME], row[DbHeader.LATEST_MODIFIED], int(row[DbHeader.SHEET_ID])))

        sms_obj = SmartSheets(list_sheet = list_sheet)
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
                    user_id = user_info[assign_to].user_id
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
                
                
                
                