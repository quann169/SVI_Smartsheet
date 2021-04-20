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
#                     COMMENT,
#                     ACTUAL_END_DATE,
#                     STATUS
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
    FINAL_DATE              = 'final_date'
    ROLE                    = 'role'
    USER_ROLE               = 'user_role'
    ANALYZE_ITEM            = 'analyze_item'
    FINAL_EVIDENCE          = 'final_evidence'
    USER_VERSION            = 'user_version'
    OTHER_CONFIG            = 'other_config'
    
    
class AnalyzeCFGKeys:
    TOKEN   = 'Token'
    TIME_DELTA  = 'Time Delta'
    TIME_DELTA_BEFORE  = 'Time Delta Before'
    TIME_DELTA_AFTER  = 'Time Delta After'
    
class OtherCFGKeys:
    LATEST_VERSION      = 'Latest Version'
    VERSION_DOWNLOAD    = 'Version Download'
    GUIDELINE           = 'Guideline'
    BCC_MAIL            = 'BCC Mail'
    FORCE_UPGRADE       = 'Force Upgrade'
    
    
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
    HOLIDAY     = 'Holiday'
    SHEET_NAME  = 'Sheet Name'
    SHEET_TYPE  = 'Sheet Type'
    RESOURCE    = 'Resource'
    ENG_TYPE    = 'Eng Type'
    ENG_LEVEL   = 'Eng Level'
    FULL_NAME   = 'Full Name'
    EMAIL       = 'Email'
    OTHER_NAME  = 'Other Name'
    LEADER      = 'Leader'
    TEAM        = 'Team'
    IS_ACTIVE   = 'Is Active'
    
class DefaulteValue:
    
    DATETIME    = '0000-00-00 00:00:00'
    
    
class SettingKeys:
    
    EMPTY_CELL          = ['', 'NaT', 'nan', 'NaN', '#REF']
    NA_VALUE            = 'NA'
    SKIP_SHEET      = [
        'Cash usd', 'EDA', 'Interview List', 'NDA list', 'New Sheet', 'Operation Cost', 'Overtime Record', 'QA_Handover', \
        'Request to Hire', 'Time card', 'Validation- iCUE Tasks (VN)'
        ]
    
class OtherKeys:
    
    METHOD_POST         = 'POST'
    METHOD_GET          = 'GET'
    LOGING_DEBUG        = 'debug'
    LOGING_INFO         = 'info'
    LOGING_WARNING      = 'warning'
    LOGING_ERROR        = 'error'
    LOGING_EXCEPTION    = 'exception'
    LOGING_CRITICAL     = 'critical'
    PROCDUCTIVITY_ENG   = ['Jr. Engineer', 'Sr. Engineer']
    PROCDUCTIVITY_SHEET_TYPE   = ['NRE', 'RnD', 'TRN', 'Pre-sale', 'Support', 'Non-WH']
    
class SessionKey:
    
    USERNAME        = 'username'
    PASSWORD        = 'password'
    SIDEBAR         = 'sidebar'
    SHEETS          = 'sheets'
    FROM            = 'from'
    TO              = 'to'
    FILTER          = 'filter'
    FILE_NAME       = 'file_name'
    MODE            = 'mode'
    USERS           = 'users'
    TASK_FILTER     = 'task_filter'
    TITLE           = 'title'
    IS_LOGIN        = 'is_login'
    USER_ID         = 'user_id'
    RESOURCE_NAME   = 'resource_name'
    ROLE_NAME       = 'role_name'
    IS_NOTIFY_VERSION = 'is_notify_version'
    IS_UPDATE_VERSION = 'is_update_version'
    USER_VERSION    = 'user_version'
    
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
    TASK_FINAL_ID           = 'task_final_id'
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
    PARSED_DATE             = 'parsed_date'
    IS_LOADING              = 'is_loading'
    ROLE_NAME               = 'role_name'
    ROLE_ID                 = 'role_id'
    USER_ROLE_ID            = 'user_role_id'
    ANALYZE_ITEM_ID         = 'analyze_item_id'
    ITEM_NAME               = 'item_name'
    IS_APPROVE              = 'is_approve'
    COUNTER                 = 'counter'
    IS_VALID                = 'is_valid'
    LEADER_ID               = 'leader_id'
    OTHER_CONFIG_ID         = 'other_config_id'
    CONFIG_NAME             = 'config_name'
    CONFIG_VALUE            = 'config_value'
    USER_VERSION_ID         = 'user_version_id'
    VERSION                 = 'version'

class ExcelColor:
    
    LIST_COLOR = [
        'lime', 'orange', 'tan', 'gray_ega', 'gray25', 'ice_blue', 'white', 'light_turquoise', 'green', 'red', 'blue'
        ]

class Role:
    
    ADMIN = 'Admin'
    PM    = 'PM'
    DM    = 'DM'
    USER  = 'User'

class Template:
    
    SETTING_HOLIDAY     = 'screens/setting/holiday.html'
    SETTING_RESOURCE    = 'screens/setting/resource.html'
    SETTING_SHEET       = 'screens/setting/sheet.html'
    SETTING_TIMEOFF     = 'screens/setting/timeoff.html'
    SETTING_OTHER       = 'screens/setting/other_setting.html'
    
    ADMIN               = 'screens/admin/admin.html'
    
    HOME                = 'screens/home/home.html'
    LAYOUT              = 'screens/layout/layout.html'
    LOG                 = 'screens/log/log.html'
    
    TIMESHEET_ANALYZE   = 'screens/timesheet/analyze.html'
    TIMESHEET_CONFLICT_DATE  = 'screens/timesheet/conflict_date.html'
    TIMESHEET_DETAIL     = 'screens/timesheet/detail.html'
    TIMESHEET_RESOURCE   = 'screens/timesheet/resource.html'
    TIMESHEET_PROJECT   = 'screens/timesheet/project.html'
    REPORT              = 'screens/timesheet/report.html'
    RESOURCE_PRODUCTIVITY = 'screens/timesheet/resource_productivity.html'
    
    BREADCRUMB          = 'components/breadcrumb/breadcrumb.html'
    NAVBAR              = 'components/navbar/navbar.html'
    SIDEBAR             = 'components/sidebar/sidebar.html'
    LOGIN               = 'screens/auth/login.html'
    
    
class Route:
    
    INDEX   = '/'
    HOME   = '/home'
    GET_NEWEST_DATA = '/get-newest-data'
    GET_NEWEST_DATA_LOG = '/get-newest-data_log'
    ADD_TO_FINAL    = '/add-to-final'
    UPLOAD_FILE    = '/upload'
    DOWNLOAD_FILE    = '/dowload'
    EXPORT    = '/export'
    TIMEOFF    = '/timeoff'
    IMPORT_TIMEOFF    = '/import-timeoff'
    LOG    = '/log'
    SHEET    = '/sheet'
    IMPORT_SHEET    = '/import-sheet'
    RESOURCE    = '/resource'
    OTHER_SETTING    = '/other-setting'
    ADMIN           = '/admin'
    IMPORT_RESOURCE    = '/import-resource'
    HOLIDAY    = '/holiday'
    IMPORT_HOLIDAY    = '/import-holiday'
    UPDATE_SESSION    = '/update-session'
    DETAIL              = '/detail-timesheet'
    RESOURCE_TIMESHEET = '/resource-timesheet'
    PROJECT_TIMESHEET = '/project-timesheet'
    ANALYZE = '/analyze'
    CONFLICT_DATE   = '/conflict-date'
    CHECK_LOADING_SMARTSHEET    = '/check-loading-smartsheet'
    LOGIN   = '/login'
    AUTH   = '/auth'
    SAVE_SHEET_SETTING   = '/save-sheet-setting'
    GET_TEMPLATE_CONTENT   = '/get-template-content'
    GET_SYNC_SHEET   = '/get-sync-sheet'
    UPDATE_SYNC_SHEET   = '/update-sync-sheet'
    SAVE_OTHER_SETTING   = '/save-other-setting'
    REPORT   = '/report'
    SEND_REPORT   = '/send-report'
    RESOURCE_PRODUCTIVITY   = '/resource-productivity'
    IMPORT_PRODUCTIVITY     = '/import-productivity'
    EXPORT_PRODUCTIVITY     = '/export-productivity'
    CHECK_VERSION     = '/check-version'
    LOCK_SYNC     = '/lock-sync'
    
    # DEFINE ROUTE REQUIRE ROLE 
    role = Role()
    REQUIRE_ROLE_OF_ROUTE = {
        ADD_TO_FINAL: [role.PM],
        IMPORT_TIMEOFF: [role.PM],
        IMPORT_SHEET: [role.PM],
        IMPORT_RESOURCE: [role.PM],
        IMPORT_HOLIDAY: [role.PM],
        ANALYZE: [role.PM],
        CONFLICT_DATE: [role.PM],
        SAVE_SHEET_SETTING: [role.PM],
        GET_SYNC_SHEET: [role.PM],
        UPDATE_SYNC_SHEET: [role.PM],
        SAVE_OTHER_SETTING: [role.PM],
        REPORT: [role.PM],
        SEND_REPORT: [role.PM],
        LOCK_SYNC: [role.PM],
        }
     
    
    