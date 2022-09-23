'''
Created on Feb 5, 2021

@author: toannguyen
'''
    
class LoggingKeys:
    LOGGING_DEBUG        = 'debug'
    LOGGING_INFO         = 'info'
    LOGGING_WARNING      = 'warning'
    LOGGING_ERROR        = 'error'
    LOGGING_EXCEPTION    = 'exception'
    LOGGING_CRITICAL     = 'critical'
    
class ConfigKeys:
    TOKEN = 'token'
    ALLOW_USERS = 'allow_users'
    SRC_SHEET = 'src_sheets'
    SRC_HEADERS = 'src_headers'
    DES_SHEETS = 'des_sheets'
    DES_HEADERS = 'des_headers'
    SRC_DATE_HEADER = 'src_date_header'
    DES_DATE_HEADER = 'des_date_header'
    EXPIRED_TIME = 'expired_time'
    SRC_COMPARE_HEADERS = 'src_compare_headers'
    DES_COMPARE_HEADERS = 'des_compare_headers'
    SRC_EMPTY_HEADERS = 'src_empty_headers'
    SRC_NONE_EMPTY_HEADERS = 'src_none_empty_headers'
    DES_EMPTY_HEADERS = 'des_empty_headers'
    DES_NONE_EMPTY_HEADERS = 'des_none_empty_headers'
    DES_MAPPING_SRC_SHEET = 'des_mapping_src_sheet'
    SRC_CHECK_MODIFIED_HEADERS = 'src_check_modified_headers'
    DES_CHECK_MODIFIED_HEADERS = 'des_check_modified_headers'
    MAPPING_HEADERS = 'mapping_headers'
    SKIP_REMOVE_ATTACHMENTS = 'skip_remove_attachments'
    RECIPIENT_MAIL = 'recipient_mail'
    CC_MAIL = 'cc_mail'
    SUBJECT = 'subject'
    BCC_MAIL = 'bcc_mail'

class DataKeys:
    NEW = 'new'
    MISSING = 'missing'
    MODIFIED = 'modified'
    UNCHANGED = 'unchanged'
    ADD = 'add'
    DELETE = 'delete'
    MODIFIED = 'modified'
    ATTACHMENTS = 'attachments'
    ATTACHMENTS_NAME = 'attachments_name'
    STATUS = 'status'
    ROW_NUMBER = 'row_number'
    ROW_ID = 'row_id'
    ACTION = 'action'
    DISPLAY_VALUE = 'display_value'
    VALUE = 'value'
    COMPARE_ID = 'compare_id'
    

class SessionKeys:
    USERNAME        = 'username'
    PASSWORD        = 'password'
    IS_LOGIN        = 'is_login'

class MethodKeys:
    METHOD_POST         = 'POST'
    METHOD_GET          = 'GET'
    SHEETS          = 'sheets'
    FROM_DATE       = 'from_date'
    TO_DATE         = 'to_date'
    SHEET_ID = 'sheet_id'
    IDS = 'ids'
    DES_ID          = 'des_id'
    PATH          = 'path'

class StructureKeys:
    PARSE_FOLDER = 'informations'
    ATTACHMENTS_FOLDER = 'attachments'
    CONSOLE_FOLDER = 'console'
    COMPARE_FOLDER = 'compare'
    
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
    ANALYZE             = 'screens/analyze/analyze.html'
    PREVIEW             = 'screens/preview/preview.html'
    LAYOUT              = 'screens/layout/layout.html'

    LOGIN               = 'screens/auth/login.html'
    
    ERROR_404           = 'screens/error/404.html'
    ERROR_500           = 'screens/error/500.html'
    
    
class Route:
    
    INDEX   = '/'
    HOME   = '/home'
    ANALYZE   = '/analyze'
    PREVIEW   = '/preview'
    START_ANALYZE = '/start-analyze'
    COMMIT   = '/commit'
    
    
    LOGIN   = '/login'
    LOGOUT   = '/logout'
    AUTH   = '/auth'
    
    LOAD_FILE = '/load-file'
    
    