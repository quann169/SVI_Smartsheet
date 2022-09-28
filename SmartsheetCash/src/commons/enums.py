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
    SHEETS = 'sheets'
    HEADERS = 'headers'
    DATE_HEADER = 'date_header'
    EXPIRED_TIME = 'expired_time'
    COMPARE_HEADERS = 'compare_headers'
    EMPTY_HEADERS = 'empty_headers'
    NONE_EMPTY_HEADERS = 'none_empty_headers'
    MODIFIED_HEADERS = 'modified_headers'
    
    
    #New keys
    GROUPS = 'groups'
    MAPPING_HEADERS = 'mapping_headers'
    SOURCE = 'source'
    SHEET_NAME = 'sheet_name'
    HEADERS = 'headers'
    DESTINATION = 'destination'
    IS_DATE = 'is_date'
    COMPARE_INDEX = 'compare_index'
    IS_EMPTY = 'is_empty'
    IS_NONE_EMPTY = 'is_none_empty'
    MODIFIED_INDEX = 'modified_index'
    DATA_TYPE = 'data_type'
    MAPPING_VALUES = 'mapping_values'
    
    RECIPIENT_MAIL = 'recipient_mail'
    CC_MAIL = 'cc_mail'
    SUBJECT = 'subject'
    BCC_MAIL = 'bcc_mail'
    DEFAULT_VALUE = 'default_value'
    
class DataKeys:
    
    NEW = 'new'
    MISSING = 'missing'
    MODIFIED = 'modified'
    UNCHANGED = 'unchanged'
    ADD = 'add'
    DELETE = 'review'#delete -> review
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
    DES_NAME          = 'des_name'
    SRC_ID          = 'src_id'
    SRC_NAME          = 'src_name'
    PATH          = 'path'
    GROUP_INDEX       = 'group_index'
    COMPARE_ID             = 'compare_id'

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
    GET_CONSOLE = '/get-console'
    
    LOGIN   = '/login'
    LOGOUT   = '/logout'
    AUTH   = '/auth'
    
    LOAD_FILE = '/load-file'
    GET_COMPARE_DETAIL_MODAL = '/get-compare-detail-modal'
    
    