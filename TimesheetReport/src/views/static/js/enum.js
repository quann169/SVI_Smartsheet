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
const SESSION_USER_ID         = 'user_id';
const SESSION_RESOURCE_NAME   = 'resource_name';
const SESSION_ROLE_NAME       = 'role_name';
const SESSION_MODE 		= 'mode';
const SESSION_ACTIONS          = 'actions';
const SESSION_GRANTED_LIST          = 'granted_list';
const SESSION_COST          = 'cost';

// INTERVAL KEY
var INTERVAL_GET_DATA  = null;
var INTERVAL_CHECK_SMARTSHEET  = null;
var INTERVAL_SHOW_LOADER  = null;
var INTERVAL_CHECK_VERSION  = null;

// ROUTE
const INDEX   = '/';
const HOME   = '/home';
const GET_NEWEST_DATA = '/get-newest-data';
const SYNC_EFFECTIVE_DATA = '/sync-effective-data';
const GET_NEWEST_DATA_LOG = '/get-newest-data_log';
const ADD_TO_FINAL = '/add-to-final';
const UPLOAD_FILE = '/upload';
const DOWNLOAD_FILE = '/dowload';
const EXPORT = '/export';
const TIMEOFF = '/timeoff';
const IMPORT_TIMEOFF = '/import-timeoff';
const IMPORT_PRODUCTIVITY_SETTING    = '/import-productivity-setting'
const LOG = '/log';
const SHEET = '/sheet';
const IMPORT_SHEET = '/import-sheet';
const RESOURCE = '/resource';
const IMPORT_RESOURCE = '/import-resource';
const HOLIDAY = '/holiday';
const IMPORT_HOLIDAY = '/import-holiday';
const IMPORT_GRANTED = '/import-granted';
const UPDATE_SESSION = '/update-session';
const DETAIL   = '/detail-timesheet';
const RESOURCE_TIMESHEET = '/resource-timesheet';
const PROJECT_TIMESHEET = '/project-timesheet';
const ANALYZE = '/analyze';
const CONFLICT_DATE   = '/conflict-date';
const CHECK_LOADING_SMARTSHEET = '/check-loading-smartsheet';
const LOGIN = '/login';
const AUTH = '/auth';
const SAVE_SHEET_SETTING = '/save-sheet-setting';
const GET_TEMPLATE_CONTENT   = '/get-template-content';
const GET_SYNC_SHEET   = '/get-sync-sheet';
const UPDATE_SYNC_SHEET   = '/update-sync-sheet';
const OTHER_SETTING   = '/other-setting';
const SAVE_OTHER_SETTING   = '/save-other-setting';
const REPORT   = '/report';
const SEND_REPORT   = '/send-report';
const RESOURCE_PRODUCTIVITY   = '/resource-productivity';
const IMPORT_PRODUCTIVITY     =  '/import-productivity';
const EXPORT_PRODUCTIVITY     =   '/export-productivity';
const CHECK_VERSION     = '/check-version';
const LOCK_SYNC     = '/lock-sync';
const GET_LIST_ROLE   = '/get-list-role';
const GET_LIST_USER   = '/get-list-user';
const GET_USER_ROLE   = '/get-user-role';
const UPDATE_ADMIN_USER_ROLE   = '/update-admin-user-role';
const ADMIN_VERSION   = '/version';
const GET_VERSION_INFO = '/get-version-info';
const UPDATE_ADMIN_VERSION   = '/update-admin-version';
const EFFECTIVE_RATE = '/effective-rate';
const EXPORT_EFFECTIVE = '/export-effective';

var FOCUS_MULTISELECT = null;

const LOADING_2_LINE = `<div class='loading-2-line'><span>Loading</span><span class="l-1">
						</span><span class="l-2"></span><span class="l-3"></span>
						<span class="l-4"></span><span class="l-5"></span></span></div>`