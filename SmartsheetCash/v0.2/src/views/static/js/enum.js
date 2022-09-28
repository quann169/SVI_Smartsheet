const MESSAGE = {
    EMPTY_DATE: 'Start date or end date are empty.',
    NO_SHEET_SELECTED: 'Please select the sheet to parse.',
    NO_ID_SELECTED: 'Please select data to commit.'
}

const SESSION_USERNAME        = 'username';
const SESSION_PASSWORD        = 'password';

// ROUTE
const START_ANALYZE = '/start-analyze';
const PREVIEW   = '/preview';
const COMMIT   = '/commit';
const LOGIN   = '/login';
const LOGOUT   = '/logout';
const AUTH   = '/auth';
const GET_CONSOLE = '/get-console';
const GET_COMPARE_DETAIL_MODAL = '/get-compare-detail-modal';

// METHOD KEYS
const SHEETS          = 'sheets';
const SHEET_ID        = 'sheet_id';
const DES_ID          = 'des_id';
const SRC_ID          = 'src_id';
const SRC_NAME          = 'src_name';
const DES_NAME          = 'des_name';
const GROUP_INDEX       = 'group_index';
const FROM_DATE       = 'from_date';
const TO_DATE         = 'to_date';
const IDS             = 'ids';
const PATH             = 'path';
const COMPARE_ID             = 'compare_id';


const MODAL_DRAG = false;

var INTERVAL  = null;
var COMPLETE_PREVIOUS_PROCESS = true;
