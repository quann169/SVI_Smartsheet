// SESSION KEY
const SESSION_SIDEBAR = 'sidebar';
const SESSION_FROM 	= 'from';
const SESSION_TO 		= 'to';
const SESSION_FILTER  = 'filter';
const SESSION_SHEETS  = 'sheets';
const SESSION_FILE_NAME  = 'file_name';
const SESSION_USERS  = 'users';
const SESSION_TASK_FILTER  = 'task_filter';
const SESSION_TITLE  = 'title';
const SESSION_USERNAME  = 'username';
const SESSION_PASSWORD  = 'password';
const SESSION_IS_LOGIN  = 'is_login';
const SESSION_USER_ID         = 'user_id'
const SESSION_RESOURCE_NAME   = 'resource_name'
const SESSION_ROLE_NAME       = 'role_name'

// INTERVAL KEY
var INTERVAL_GET_DATA  = null;
var INTERVAL_CHECK_SMARTSHEET  = null;
var INTERVAL_SHOW_LOADER  = null;

// ROUTE
const INDEX   = '/';
const HOME   = '/home';
const GET_NEWEST_DATA = '/get-newest-data';
const GET_NEWEST_DATA_LOG = '/get-newest-data_log';
const ADD_TO_FINAL = '/add-to-final';
const UPLOAD_FILE = '/upload';
const DOWNLOAD_FILE = '/dowload';
const EXPORT = '/export';
const TIMEOFF = '/timeoff';
const IMPORT_TIMEOFF = '/import-timeoff';
const LOG = '/log';
const SHEET = '/sheet';
const IMPORT_SHEET = '/import-sheet';
const RESOURCE = '/resource';
const IMPORT_RESOURCE = '/import-resource';
const HOLIDAY = '/holiday';
const IMPORT_HOLIDAY = '/import-holiday';
const UPDATE_SESSION = '/update-session';
const DETAIL   = '/detail-timesheet';
const RESOURCE_TIMESHEET = '/resource-timesheet';
const PROJECT_TIMESHEET = '/project-timesheet';
const ANALYZE = '/analyze';
const CONFLICT_DATE   = '/conflict-date';
const CHECK_LOADING_SMARTSHEET = '/check-loading-smartsheet';
const LOGIN = '/login';
const AUTH = '/auth';
const SAVE_SHEET_SETTING = '/save-sheet-setting'
const GET_TEMPLATE_CONTENT   = '/get-template-content'
const GET_SYNC_SHEET   = '/get-sync-sheet'
const UPDATE_SYNC_SHEET   = '/update-sync-sheet'

var FOCUS_MULTISELECT = null;

const LOADING_2_LINE = `<div class='loading-2-line'><span>Loading</span><span class="l-1">
						</span><span class="l-2"></span><span class="l-3"></span>
						<span class="l-4"></span><span class="l-5"></span></span></div>`