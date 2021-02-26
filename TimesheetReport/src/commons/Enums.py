'''
Created on Feb 5, 2021

@author: toannguyen
'''

class SmartsheetCfgKeys:
    TASK_NAME   = 'Task Name'
    START_DATE  = 'Start Date'
    END_DATE    = 'End Date'
    DURATION    = 'Duration'
    ASSIGN_TO   = 'Assigned To'
    COMPLETE    = '% Complete'
    ALLOCATION  = '% Allocation'
    PREDECESSOR = 'Predecessors'
    COMMENT     = 'Comments'
    ACTUAL_END_DATE = 'Actual End Date'
    STATUS      = 'Status'
    
    
    
    LIST_HEADER = [
                    TASK_NAME,
                    START_DATE,
                    END_DATE,
                    DURATION,
                    ASSIGN_TO,
                    COMPLETE,
                    ALLOCATION,
                    PREDECESSOR,
                    COMMENT,
                    ACTUAL_END_DATE,
                    STATUS
        ]

class Connect:
    DB_HOST_NAME            = 'db_host_name'
    DB_PORT                 = 'db_port'
    DB_USER                 = 'db_user'
    DB_PASSWORD             = 'db_password'
    DB_NAME                 = 'db_name'
    CHAR_SET                = 'utf8mb4'

class DbTable:
    ANALYSIS_CONFIG         = 'analysis_config'
    ENG_LEVEL               = 'eng_level'
    ENG_TYPE                = 'eng_type'
    FINAL_DATE              = 'final_date'
    HOLIDAY                 = 'holiday'
    LOG                     = 'log'
    PROJECT_USER            = 'project_user'
    SHEET                   = 'sheet'
    SHEET_TYPE              = 'sheet_type'
    TASK                    = 'task'
    TASK_FINAL              = 'task_final'
    TEAM                    = 'team'
    TIME_OFF                = 'time_off'
    USER                    = 'user'

class DateTime():
    LIST_MONTH = {
        1 : 'Jan', 
        2 :'Feb', 
        3 : 'Mar', 
        4 : 'Apr', 
        5 : 'May', 
        6 : 'Jun', 
        7 :'Jul', 
        8 : 'Aug', 
        9: 'Sep', 
        10 : 'Oct', 
        11 : 'Nov', 
        12 : 'Dec'
        }
    LIST_WORK_DAY_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    START_WEEK = 'Monday'

class ExcelHeader:
    ID          = 'ID'
    REQUESTER   = 'Requester'
    DEPARTMENT  = 'Department'
    TYPE        = 'Type'
    START_DATE  = 'Start Date'
    END_DATE    = 'End Date'
    WORKDAYS    = 'Workdays'
    STATUS      = 'Status'

class SettingKeys:
    NA_USER_ID          = 3
    NA_ENG_LEVEL_ID     = 11
    NA_ENG_TYPE_ID      = 5
    NA_TEAM_ID          = 9
    
    
class DbHeader:
    
    ANALYSIS_CONFIG_ID      = 'analysis_config_id'
    CONFIG_NAME             = 'config_name'
    CONFIG_VALUE            = 'config_value'
    UPDATED_DATE            = 'updated_date'
    UPDATED_BY              = 'updated_by'
    ENG_LEVEL_ID            = 'eng_level_id'
    LEVEL                   = 'level'
    ENG_TYPE_ID             = 'eng_type_id'
    ENG_TYPE_NAME           = 'eng_type_name'
    FINAL_DATE_ID           = 'final_date_id'
    DATE                    = 'date'
    HOLIDAY_ID              = 'holiday_id'
    LOG_ID                  = 'log_id'
    SHEET_ID                = 'sheet_id'
    OLD_VALUE               = 'old_value'
    NEW_VALUE               = 'new_value'
    PROJECT_USER_ID         = 'project_user_id'
    USER_ID                 = 'user_id'
    SHEET_TYPE_ID           = 'sheet_type_id'
    SHEET_NAME              = 'sheet_name'
    LATEST_MODIFIED         = 'latest_modified'
    SHEET_TYPE              = 'sheet_type'
    TASK_ID                 = 'task_id'
    SIBLING_ID              = 'sibling_id'
    PARENT_ID               = 'parent_id'
    SELF_ID                 = 'self_id'
    TASK_NAME               = 'task_name'
    START_DATE              = 'start_date'
    END_DATE                = 'end_date'
    DURATION                = 'duration'
    COMPLETE                = 'complete'
    PREDECESSORS            = 'predecessors'
    COMMENT                 = 'comment'
    ACTUAL_END_DATE         = 'actual_end_date'
    STATUS                  = 'status'
    IS_CHILDREN             = 'is_children'
    FINAL_DATE_ID           = 'final_date_id'
    TEAM_ID                 = 'team_id'
    TEAM_NAME               = 'team_name'
    TEAM_LEAD_ID            = 'team_lead_id'
    TIME_OFF_ID             = 'time_off_id'
    DEPARTMENT              = 'department'
    TYPE                    = 'type'
    WORK_DAYS               = 'work_days'
    USER_NAME               = 'user_name'
    FULL_NAME               = 'full_name'
    EMAIL                   = 'email'
    OTHER_NAME              = 'other_name'
    IS_ACTIVE               = 'is_active'
    ALLOCATION              = 'allocation'


    
    
    
    
    
    
    
    
    
    
    