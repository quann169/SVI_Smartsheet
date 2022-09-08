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
    pass
   
    
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
    pass
    
class DefaultValue:
    DATETIME    = '0000-00-00 00:00:00'
    
    
class SettingKeys:
    
    EMPTY_CELL          = ['', 'NaT', 'nan', 'NaN', '#REF']
    NA_VALUE            = 'NA'
    
class OtherKeys:
    
    METHOD_POST         = 'POST'
    METHOD_GET          = 'GET'
    LOGGING_DEBUG        = 'debug'
    LOGGING_INFO         = 'info'
    LOGGING_WARNING      = 'warning'
    LOGGING_ERROR        = 'error'
    LOGGING_EXCEPTION    = 'exception'
    LOGGING_CRITICAL     = 'critical'
    PROCDUCTIVITY_ENG   = ['Jr. Engineer', 'Sr. Engineer']
    PROCDUCTIVITY_SHEET_TYPE   = ['NRE', 'RnD', 'TRN', 'Pre-sale', 'Operating', 'Support', 'Non-WH']
    
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
    LIST_ROLE_NAME  = 'list_role_name'
    IS_NOTIFY_VERSION = 'is_notify_version'
    IS_UPDATE_VERSION = 'is_update_version'
    USER_VERSION    = 'user_version'
    ACTIONS          = 'actions'
    GRANTED_LIST    = 'granted_list'
    COST            = 'cost'
    EXPAND_COLLAPSE         = 'expand_collapse'

    
class DbHeader:
    pass
    
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
    
    BREADCRUMB          = 'components/breadcrumb.html'
    NAVBAR              = 'components/navbar.html'
    SIDEBAR             = 'components/sidebar.html'
    BUTTON              = 'components/button.html'
    INPUT               = 'components/input.html'
    CHECKBOX            = 'components/checkbox.html'
    SELECT              = 'components/select.html'
    MODAL               = 'components/modal.html'
    
    HOME                = 'screens/home/home.html'
    LAYOUT              = 'screens/layout/layout.html'

    LOGIN               = 'screens/auth/login.html'
    
    ERROR_404           = 'screens/error/404.html'
    ERROR_500           = 'screens/error/500.html'
    
    
class Route:
    
    INDEX   = '/'
    HOME   = '/home'
    
    LOGIN   = '/login'
    LOGOUT   = '/logout'
    AUTH   = '/auth'
    
    
    
    