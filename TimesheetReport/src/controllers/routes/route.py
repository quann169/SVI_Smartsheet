'''
Created on Feb 24, 2021

@author: toannguyen
'''

import os, ast
from flask import Blueprint, render_template, session, redirect, url_for, abort, request, jsonify, send_file,\
                    send_from_directory, g
from pprint import pprint
import logging
from src.commons.utils import save_file_from_request, get_request_form_ajax, get_request_args, \
                                get_saved_password, save_password
from src.controllers.controllers import Controllers as ctrl
from src.commons.enums import DbTable, DbHeader, SessionKey, Template, Route, AnalyzeCFGKeys, \
                                OtherKeys, Role
from src.models.database.connection_model import Connection
from src.commons.utils import println
import config
import getpass
from src.commons.message import MsgError
timesheet_bp = Blueprint('timesheet_bp', __name__)

@timesheet_bp.before_request
def before_request():
    """ Validate role, login before request page
    :param : 
    :return: 
    """
    
    method = request.method 
    path = request.path
    enum_route = Route()
    # check login
    if not session.get(SessionKey.IS_LOGIN) or not session.get(SessionKey.IS_LOGIN) or not session.get(SessionKey.USER_ID):
        if path not in [Route().LOGIN, Route().AUTH]:
            return (redirect(url_for("timesheet_bp.login")))
    # check role
    list_role_required = enum_route.REQUIRE_ROLE_OF_ROUTE.get(path)
    if list_role_required:
        if path not in [Route().LOGIN, Route().AUTH]:
            role = session[SessionKey.ROLE_NAME]
            if not role in list_role_required:
                return abort(403, MsgError.E005)
    if (not session.get(SessionKey.USER_VERSION) ) or (session.get(SessionKey.USER_VERSION) != g.version):
        if path not in [Route().LOGIN, Route().AUTH]:
            ctrl().add_current_version_of_user()
        
        
@timesheet_bp.route(Route.INDEX, methods=[OtherKeys.METHOD_POST, OtherKeys.METHOD_GET])
def index():
    """ Starting page
    :param : 
    :return: home or login page
    """
    println(Route.INDEX, OtherKeys.LOGING_DEBUG)
    try:  
        ctrl_obj   = ctrl()
        if not session.get(SessionKey.SIDEBAR):
            ctrl_obj.update_session(SessionKey.SIDEBAR, 1)
        password = get_saved_password()
        username = getpass.getuser()
        if password == None:
            return (redirect(url_for("timesheet_bp.login")))
        else:
            check_password = ctrl_obj.authenticate_account(username, password)
            if check_password[0]:
                return (redirect(url_for("timesheet_bp.home")))
            else:
                return (redirect(url_for("timesheet_bp.login")))
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.LOGIN, methods=[OtherKeys.METHOD_POST, OtherKeys.METHOD_GET])
def login():
    """ Login page
    :param : 
    :return: login page
    """
    println(Route.LOGIN, OtherKeys.LOGING_DEBUG)
    try:
        session.clear()
        ctrl_obj   = ctrl()
        if not session.get(SessionKey.SIDEBAR):
            ctrl_obj.update_session(SessionKey.SIDEBAR, 1)
        current_user = getpass.getuser()
        request_dict = get_request_args()
        
        return render_template(Template.LOGIN, ctrl_obj = ctrl_obj, role = Role(), db_header = DbHeader(), \
                               route = Route(), template= Template(), session_enum = SessionKey(), \
                               request_dict = request_dict, current_user=current_user)
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.AUTH, methods=[OtherKeys.METHOD_POST])
def auth():
    """ Authenticate user and domain password
    :param : 
    :return: (1 or 0, error message)
    """
    println(Route.AUTH, OtherKeys.LOGING_DEBUG)
    request_dict = get_request_form_ajax()
    password = request_dict[SessionKey.PASSWORD]
    username = request_dict[SessionKey.USERNAME].strip()
    remember = request_dict['remember']
    ctrl_obj = ctrl()
    result = ctrl_obj.authenticate_account(username, password, remember)
    return jsonify({'result': result})

@timesheet_bp.route(Route.HOME, methods=[OtherKeys.METHOD_POST, OtherKeys.METHOD_GET])
def home():
    """ Home page
    :param : 
    :return: home page
    """
    println(Route.HOME, OtherKeys.LOGING_DEBUG)
    try:
        ctrl_obj   = ctrl()
        return render_template(Template.HOME, ctrl_obj = ctrl_obj, role = Role(), \
                               db_header = DbHeader(), route = Route() , \
                               session_enum = SessionKey(), template= Template())
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.GET_NEWEST_DATA, methods=[OtherKeys.METHOD_POST])
def get_newest_data():
    """ Get task from smartsheet and add to database
    :param : 
    :return: (1 or 0, message)
    """
    println(Route.GET_NEWEST_DATA, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().get_newest_data(from_date=request_dict[SessionKey.FROM], \
                                        to_date=request_dict[SessionKey.TO], \
                                        sheet_ids=request_dict[SessionKey.SHEETS])
        return jsonify({'result': result})
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.GET_NEWEST_DATA_LOG, methods=[OtherKeys.METHOD_POST])
def get_newest_data_log():
    """ Get log of 'get newest data' feature
    :param : 
    :return: text
    """
    println(Route.GET_NEWEST_DATA_LOG, OtherKeys.LOGING_DEBUG)
    try:
        result = ctrl().get_newest_data_log()
        return jsonify({'result': result})
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)
    
@timesheet_bp.route(Route.ADD_TO_FINAL, methods=[OtherKeys.METHOD_POST])
def add_to_final():
    """ Move task to final table
    :param : 
    :return: (1 or 0, message)
    """
    println(Route.ADD_TO_FINAL, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().add_to_final(from_date=request_dict[SessionKey.FROM], \
                                     to_date=request_dict[SessionKey.TO], 
                                     sheet_ids=request_dict[SessionKey.SHEETS],
                                     data=request_dict['data'],)
        
        return jsonify({'result': result})
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)
    
@timesheet_bp.route(Route.UPLOAD_FILE, methods=[OtherKeys.METHOD_POST])
def upload_file():
    """ Upload file from client
    :param : 
    :return: (1 or 0, message)
    """
    println(Route.UPLOAD_FILE, OtherKeys.LOGING_DEBUG)
    try:
        result = save_file_from_request()
        return jsonify({'result': result})
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.DOWNLOAD_FILE, methods=[OtherKeys.METHOD_GET, OtherKeys.METHOD_POST])
def download_file():
    """ download file from server
    :param : 
    :return: file obj
    """
    println(Route.DOWNLOAD_FILE, OtherKeys.LOGING_DEBUG)
    request_dict = get_request_args()
    path = os.path.join(config.WORKING_PATH, request_dict[SessionKey.FILE_NAME])
    return send_file(path, as_attachment=True, cache_timeout=0)

@timesheet_bp.route(Route.EXPORT, methods=[OtherKeys.METHOD_POST])
def export():
    """ Export timesheet to excel file
    :param : 
    :return: (0, error) or (1, file_name)
    """
    println(Route.EXPORT, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().export_excel(from_date=request_dict[SessionKey.FROM], \
                                     to_date=request_dict[SessionKey.TO], \
                                     sheet_ids=request_dict[SessionKey.SHEETS],
                                     options=request_dict['options'])
        return jsonify({'result': result})
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)



@timesheet_bp.route(Route.TIMEOFF)
def timeoff():
    """ Time-Off setting 
    :param : 
    :return: timeoff setting page
    """
    println(Route.TIMEOFF, OtherKeys.LOGING_DEBUG)
    try:
        ctrl_obj   = ctrl()
        return render_template(Template.SETTING_TIMEOFF, ctrl_obj = ctrl_obj, \
                               role = Role(), db_header = DbHeader(), route = Route() , \
                               template= Template())
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.IMPORT_TIMEOFF, methods=[OtherKeys.METHOD_POST])
def import_timeoff():
    """ Import timeoff
    :param : 
    :return: (1 or 0, message)
    """
    println(Route.IMPORT_TIMEOFF, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().import_timeoff(file_name=request_dict['file_name'])
        return jsonify({'result': result})
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.LOG)
def log():
    """ Log page
    :param : 
    :return: log page
    """
    println(Route.LOG, OtherKeys.LOGING_DEBUG)
    try:
        ctrl_obj   = ctrl()
        return render_template(Template.LOG, ctrl_obj = ctrl_obj, role = Role(), \
                               db_header = DbHeader(), route = Route() , template= Template())
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.SHEET)
def sheet():
    """ sheet setting page
    :param : 
    :return: sheet setting page
    """
    println(Route.SHEET, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_args()
        ctrl_obj   = ctrl()
        ctrl_obj.add_default_config_to_method_request(request_dict, more_option={SessionKey.MODE: 'active'})
        return render_template(Template.SETTING_SHEET, ctrl_obj = ctrl_obj, role = Role(), \
                               db_header = DbHeader(), route = Route() , \
                               template= Template(), session_enum = SessionKey(), request_dict = request_dict)
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.OTHER_SETTING)
def other_setting():
    """ other setting page
    :param : 
    :return: other setting page
    """
    println(Route.OTHER_SETTING, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_args()
        ctrl_obj   = ctrl()
        return render_template(Template.SETTING_OTHER, ctrl_obj = ctrl_obj, role = Role(), \
                               db_header = DbHeader(), route = Route() , \
                               template= Template(), session_enum = SessionKey(), request_dict = request_dict,\
                               analyze_cfg_key = AnalyzeCFGKeys())
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)
    
@timesheet_bp.route(Route.IMPORT_SHEET, methods=[OtherKeys.METHOD_POST])
def import_sheet():
    """ import sheet by excel file
    :param : 
    :return: (1 or 0, message)
    """
    println(Route.IMPORT_SHEET, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().import_sheet(file_name=request_dict['file_name'])
        return jsonify({'result': result})
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)
    
@timesheet_bp.route(Route.RESOURCE)
def resource():
    """ resource setting page
    :param : 
    :return: resource setting page
    """
    println(Route.RESOURCE, OtherKeys.LOGING_DEBUG)
    try:
        ctrl_obj   = ctrl()
        return render_template(Template.SETTING_RESOURCE, ctrl_obj = ctrl_obj, role = Role(), \
                               db_header = DbHeader(), route = Route() , template= Template())
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.IMPORT_RESOURCE, methods=[OtherKeys.METHOD_POST])
def import_resource():
    """ import resource by excel file
    :param : 
    :return: (1 or 0, message)
    """
    println(Route.IMPORT_RESOURCE, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().import_resource(file_name=request_dict['file_name'])
        return jsonify({'result': result})
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)
    
@timesheet_bp.route(Route.HOLIDAY)
def holiday():
    """ holiday setting page
    :param : 
    :return: holiday setting page
    """
    println(Route.HOLIDAY, OtherKeys.LOGING_DEBUG)
    try:
        ctrl_obj    = ctrl()
        return render_template(Template.SETTING_HOLIDAY, ctrl_obj = ctrl_obj, role = Role(), \
                               db_header = DbHeader(), route = Route() , template= Template())
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.IMPORT_HOLIDAY, methods=[OtherKeys.METHOD_POST])
def import_holiday():
    """ import holiday by excel
    :param : 
    :return: (1 or 0, message)
    """
    println(Route.IMPORT_HOLIDAY, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().import_holiday(file_name=request_dict['file_name'])
        return jsonify({'result': result})
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.UPDATE_SESSION, methods=[OtherKeys.METHOD_POST])
def update_session():
    """ update sessionkey
    :param : 
    :return: (1 or 0, message)
    """
    println(Route.UPDATE_SESSION, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().update_session(request_dict['session_key'], request_dict['session_value'], )
        return jsonify({'result': result})
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.DETAIL)
def daily_timesheet():
    """ detail timesheet page
    :param : 
    :return: detail timesheet page
    """
    println(Route.DETAIL, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_args()
        ctrl_obj   = ctrl()
        ctrl_obj.add_default_config_to_method_request(request_dict, more_option={SessionKey.TASK_FILTER: 'both'})
        return render_template(Template.TIMESHEET_DETAIL, ctrl_obj = ctrl_obj, role = Role(), \
                               db_header = DbHeader(), route = Route() , template= Template(), \
                               session_enum = SessionKey(), request_dict = request_dict)
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.RESOURCE_TIMESHEET)
def resource_timesheet():
    """ resource timesheet page
    :param : 
    :return: resource timesheet page
    """
    println(Route.RESOURCE_TIMESHEET, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_args()
        ctrl_obj   = ctrl()
        ctrl_obj.add_default_config_to_method_request(request_dict, more_option={SessionKey.TASK_FILTER: 'both'})
        return render_template(Template.TIMESHEET_RESOURCE, ctrl_obj = ctrl_obj, role = Role(), \
                               db_header = DbHeader(), route = Route() , template= Template(), \
                               session_enum = SessionKey(), request_dict = request_dict)
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.PROJECT_TIMESHEET)
def project_timesheet():
    """ project timesheet page
    :param : 
    :return: project timesheet page
    """
    println(Route.PROJECT_TIMESHEET, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_args()
        ctrl_obj   = ctrl()
        ctrl_obj.add_default_config_to_method_request(request_dict, more_option={SessionKey.TASK_FILTER: 'both'})
        return render_template(Template.TIMESHEET_PROJECT, ctrl_obj = ctrl_obj, role = Role(), \
                               db_header = DbHeader(), route = Route() , template= Template(), \
                               session_enum = SessionKey(), request_dict = request_dict)
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)
    
@timesheet_bp.route(Route.ANALYZE)
def analyze():
    """ analyze timesshet before add final task
    :param : 
    :return: analyze page
    """
    println(Route.ANALYZE, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_args()
        request_dict[SessionKey.TASK_FILTER] = 'current'
        ctrl_obj   = ctrl()
        return render_template(Template.TIMESHEET_ANALYZE, ctrl_obj = ctrl_obj, role = Role(), \
                               db_header = DbHeader(), route = Route() , template= Template(), \
                               session_enum = SessionKey(), request_dict = request_dict)
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)
    
@timesheet_bp.route(Route.CONFLICT_DATE)
def conflict_final_date():
    """ conflict date page
    :param : 
    :return: conflict date page
    """
    println(Route.CONFLICT_DATE, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_args()
        ctrl_obj   = ctrl()
        return render_template(Template.TIMESHEET_CONFLICT_DATE, ctrl_obj = ctrl_obj, role = Role(), \
                               db_header = DbHeader(), route = Route() , template= Template(), \
                               session_enum = SessionKey(), request_dict = request_dict)
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.CHECK_LOADING_SMARTSHEET, methods=[OtherKeys.METHOD_POST])
def check_loading_smartsheet():
    """ checking sheet is loading task
    :param : 
    :return: (1 or 0, list_sheet)
    """
    println(Route.CHECK_LOADING_SMARTSHEET, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_form_ajax()
        try:
            sheet_ids = request_dict[SessionKey.SHEETS]
        except KeyError:
            sheet_ids = []
        result = ctrl().check_get_newest_data_feature_is_running(sheet_ids)
        return jsonify({'result': result})
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.SAVE_SHEET_SETTING, methods=[OtherKeys.METHOD_POST])
def save_sheet_setting():
    """ save all the changes on GUI of sheet setting
    :param : 
    :return: (1 or 0, message)
    """
    println(Route.SAVE_SHEET_SETTING, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().save_sheet_setting(request_dict)
        return jsonify({'result': result})
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.SAVE_OTHER_SETTING, methods=[OtherKeys.METHOD_POST])
def save_other_setting():
    """ save all the changes on GUI of other setting
    :param : 
    :return: (1 or 0, message)
    """
    println(Route.SAVE_OTHER_SETTING, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().save_other_setting(request_dict)
        return jsonify({'result': result})
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)
    
@timesheet_bp.route(Route.GET_SYNC_SHEET, methods=[OtherKeys.METHOD_POST, OtherKeys.METHOD_GET])
def get_sync_sheet():
    """ get sheet info from smartsheet
    :param : 
    :return: info
    """
    println(Route.GET_SYNC_SHEET, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().get_sync_sheet(request_dict)
        return jsonify({'result': result})
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.GET_TEMPLATE_CONTENT, methods=[OtherKeys.METHOD_POST, OtherKeys.METHOD_GET])
def get_template_content():
    """ get template content
    :param : 
    :return: template content
    """
    println(Route.GET_TEMPLATE_CONTENT, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_form_ajax()
        file_path = request_dict['path']
        tool_path = g.tool_path
        
        template_path = os.path.join(os.path.join(tool_path, g.template_path), file_path)
        result = ''
        with open(template_path, 'r') as f:
            result = f.read()
        result = result.replace('\n', '')
        return jsonify({'result': result})
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.UPDATE_SYNC_SHEET, methods=[OtherKeys.METHOD_POST, OtherKeys.METHOD_GET])
def update_sync_sheet():
    """ Update sheet info by 'sync sheet' feature
    :param : 
    :return: (1 or 0, message)
    """
    println(Route.UPDATE_SYNC_SHEET, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().update_sync_sheet(request_dict)
        return jsonify({'result': result})
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.REPORT)
def report():
    """ report page
    :param : 
    :return: report page
    """
    println(Route.REPORT, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_args()
        ctrl_obj   = ctrl()
        ctrl_obj.add_default_config_to_method_request(request_dict, more_option={SessionKey.TASK_FILTER: 'current'})
        return render_template(Template.REPORT, ctrl_obj = ctrl_obj, role = Role(), \
                               db_header = DbHeader(), route = Route() , template= Template(), \
                               session_enum = SessionKey(), request_dict = request_dict)
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.RESOURCE_PRODUCTIVITY)
def resource_productivity():
    """ resource productivity page
    :param : 
    :return: resource productivity page
    """
    println(Route.RESOURCE_PRODUCTIVITY, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_args()
        ctrl_obj   = ctrl()
        ctrl_obj.add_default_config_to_method_request(request_dict, more_option={SessionKey.TASK_FILTER: 'both'})
        return render_template(Template.RESOURCE_PRODUCTIVITY, ctrl_obj = ctrl_obj, role = Role(), db_header = DbHeader(),\
                               route = Route() , template= Template(), session_enum = SessionKey(), \
                               other_keys= OtherKeys(), request_dict = request_dict)
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)
    
@timesheet_bp.route(Route.SEND_REPORT, methods=[OtherKeys.METHOD_POST, OtherKeys.METHOD_GET])
def send_report():
    """ Send weekly timesheet
    :param : 
    :return: (1 or 0, message)
    """
    println(Route.SEND_REPORT, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().send_report(request_dict)
        return jsonify({'result': result})
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.IMPORT_PRODUCTIVITY, methods=[OtherKeys.METHOD_POST])
def import_productivity():
    """ Import productivity
    :param : 
    :return: (1 or 0, message)
    """
    println(Route.IMPORT_PRODUCTIVITY, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().import_productivity(file_name=request_dict['file_name'], from_date=request_dict[SessionKey.FROM],\
                                            to_date=request_dict[SessionKey.TO])
        
        return jsonify({'result': result})
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.EXPORT_PRODUCTIVITY, methods=[OtherKeys.METHOD_POST])
def export_productivity():
    """ Export productivity to excel file
    :param : 
    :return: (0, error) or (1, file_name)
    """
    println(Route.EXPORT_PRODUCTIVITY, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().export_productiviity(request_dict)
        return jsonify({'result': result})
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)

@timesheet_bp.route(Route.LOCK_SYNC, methods=[OtherKeys.METHOD_POST, OtherKeys.METHOD_GET])
def lock_sync():
    """ check version 
    :param : 
    :return: 
    """
    println(Route.LOCK_SYNC, OtherKeys.LOGING_DEBUG)
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().lock_sync(request_dict)
        return jsonify({'result': result})
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)
    
@timesheet_bp.route('/test')
def test():
    println('/test', OtherKeys.LOGING_DEBUG)
    try:
        
        ctrl_obj   = ctrl()       
        return render_template("test.html", ctrl_obj = ctrl_obj, role = Role(), \
                               db_header = DbHeader(), route = Route() , template= Template())
    except Exception as e:
        println(e, OtherKeys.LOGING_EXCEPTION)
        return abort(500, e)
    

    
    