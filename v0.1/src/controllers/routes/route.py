'''
Created on Feb 24, 2021

@author: toannguyen
'''

import os, ast
from flask import Blueprint, render_template, session, redirect, url_for, abort, request, jsonify, send_file,\
                    send_from_directory, g
from pprint import pprint
import logging
from src.commons.utils import save_file_from_request, get_request_form_ajax, get_request_args
from src.controllers.controllers import Controllers as ctrl
from src.commons.enums import DbTable, DbHeader, SessionKey, Template, Route
from src.models.database.connection_model import Connection
from src.commons.utils import println
import config

timesheet_bp = Blueprint('timesheet_bp', __name__)

# connect_obj = Connection()
# pool_conn = connect_obj.create_pool_connection()
# 
# @timesheet_bp.before_request
# def create_connection():
#     g.pool_conn = pool_conn
    
@timesheet_bp.route(Route.INDEX)
def index():
    println(Route.INDEX, 'debug')
    try:
        ctrl_obj   = ctrl()
        return render_template(Template.INDEX, ctrl_obj = ctrl_obj, db_header = DbHeader(), route = Route() , \
                               session_enum = SessionKey(), template= Template())
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route(Route.HOME)
def home():
    println(Route.HOME, 'debug')
    try:
        
        ctrl_obj   = ctrl()
        return render_template(Template.HOME, ctrl_obj = ctrl_obj, db_header = DbHeader(), route = Route() , \
                               session_enum = SessionKey(), template= Template())
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route(Route.GET_NEWEST_DATA, methods=['POST'])
def get_newest_data():
    println(Route.GET_NEWEST_DATA, 'debug')
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().get_newest_data(from_date=request_dict[SessionKey.FROM], to_date=request_dict[SessionKey.TO], sheet_ids=request_dict[SessionKey.SHEETS])
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route(Route.GET_NEWEST_DATA_LOG, methods=['POST'])
def get_newest_data_log():
    println(Route.GET_NEWEST_DATA_LOG, 'debug')
    try:
        result = ctrl().get_newest_data_log()
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)
    
@timesheet_bp.route(Route.ADD_TO_FINAL, methods=['POST'])
def add_to_final():
    println(Route.ADD_TO_FINAL, 'debug')
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().add_to_final(from_date=request_dict[SessionKey.FROM], to_date=request_dict[SessionKey.TO], sheet_ids=request_dict[SessionKey.SHEETS])
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)
    
@timesheet_bp.route(Route.UPLOAD_FILE, methods=['POST'])
def upload_file():
    println(Route.UPLOAD_FILE, 'debug')
    try:
        result = save_file_from_request()
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route(Route.DOWNLOAD_FILE, methods=['GET', 'POST'])
def download_file():
    println(Route.DOWNLOAD_FILE, 'debug')
    request_dict = get_request_args()
    path = os.path.join(config.WORKING_PATH, request_dict[SessionKey.FILE_NAME])
    return send_file(path, as_attachment=True, cache_timeout=0)

@timesheet_bp.route(Route.EXPORT, methods=['POST'])
def export():
    println(Route.EXPORT, 'debug')
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().export_excel(from_date=request_dict[SessionKey.FROM], to_date=request_dict[SessionKey.TO], sheet_ids=request_dict[SessionKey.SHEETS])
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)



@timesheet_bp.route(Route.TIMEOFF)
def timeoff():
    println(Route.TIMEOFF, 'debug')
    try:
        ctrl_obj   = ctrl()
        return render_template(Template.SETTING_TIMEOFF, ctrl_obj = ctrl_obj, db_header = DbHeader(), route = Route() , template= Template())
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route(Route.IMPORT_TIMEOFF, methods=['POST'])
def import_timeoff():
    println(Route.IMPORT_TIMEOFF, 'debug')
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().import_timeoff(file_name=request_dict['file_name'])
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route(Route.LOG)
def log():
    println(Route.LOG, 'debug')
    try:
        ctrl_obj   = ctrl()
        return render_template(Template.LOG, ctrl_obj = ctrl_obj, db_header = DbHeader(), route = Route() , template= Template())
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route(Route.SHEET)
def sheet():
    println(Route.SHEET, 'debug')
    try:
        ctrl_obj    = ctrl()
        return render_template(Template.SETTING_SHEET, ctrl_obj = ctrl_obj, db_header = DbHeader(), route = Route() , template= Template())
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route(Route.IMPORT_SHEET, methods=['POST'])
def import_sheet():
    println(Route.IMPORT_SHEET, 'debug')
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().import_sheet(file_name=request_dict['file_name'])
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)
    
@timesheet_bp.route(Route.RESOURCE)
def resource():
    println(Route.RESOURCE, 'debug')
    try:
        ctrl_obj   = ctrl()
        return render_template(Template.SETTING_RESOURCE, ctrl_obj = ctrl_obj, db_header = DbHeader(), route = Route() , template= Template())
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route(Route.IMPORT_RESOURCE, methods=['POST'])
def import_resource():
    println(Route.IMPORT_RESOURCE, 'debug')
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().import_resource(file_name=request_dict['file_name'])
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)
    
@timesheet_bp.route(Route.HOLIDAY)
def holiday():
    println(Route.HOLIDAY, 'debug')
    try:
        ctrl_obj    = ctrl()
        return render_template(Template.SETTING_HOLIDAY, ctrl_obj = ctrl_obj, db_header = DbHeader(), route = Route() , template= Template())
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route(Route.IMPORT_HOLIDAY, methods=['POST'])
def import_holiday():
    println(Route.IMPORT_HOLIDAY, 'debug')
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().import_holiday(file_name=request_dict['file_name'])
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route(Route.UPDATE_SESSION, methods=['POST'])
def update_session():
    println(Route.UPDATE_SESSION, 'debug')
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().update_session(request_dict['session_key'], request_dict['session_value'], )
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route(Route.DETAIL)
def daily_timesheet():
    println(Route.DETAIL, 'debug')
    try:
        request_dict = get_request_args()
        ctrl_obj   = ctrl()
        ctrl_obj.add_defalt_config_to_method_request(request_dict, more_option={SessionKey.TASK_FILTER: 'both'})
        return render_template(Template.TIMESHEET_DETAIL, ctrl_obj = ctrl_obj, db_header = DbHeader(), route = Route() , template= Template(), session_enum = SessionKey(), request_dict = request_dict)
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route(Route.RESOURCE_TIMESHEET)
def resource_timesheet():
    println(Route.RESOURCE_TIMESHEET, 'debug')
    try:
        request_dict = get_request_args()
        ctrl_obj   = ctrl()
        ctrl_obj.add_defalt_config_to_method_request(request_dict, more_option={SessionKey.TASK_FILTER: 'both'})
        return render_template(Template.TIMESHEET_RESOURCE, ctrl_obj = ctrl_obj, db_header = DbHeader(), route = Route() , template= Template(), session_enum = SessionKey(), request_dict = request_dict)
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route(Route.PROJECT_TIMESHEET)
def project_timesheet():
    println(Route.PROJECT_TIMESHEET, 'debug')
    try:
        request_dict = get_request_args()
        ctrl_obj   = ctrl()
        ctrl_obj.add_defalt_config_to_method_request(request_dict, more_option={SessionKey.TASK_FILTER: 'both'})
        return render_template(Template.TIMESHEET_PROJECT, ctrl_obj = ctrl_obj, db_header = DbHeader(), route = Route() , template= Template(), session_enum = SessionKey(), request_dict = request_dict)
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)
    
@timesheet_bp.route(Route.ANALYZE)
def analyze():
    println(Route.ANALYZE, 'debug')
    try:
        request_dict = get_request_args()
        request_dict[SessionKey.TASK_FILTER] = 'current'
        ctrl_obj   = ctrl()
        return render_template(Template.TIMESHEET_ANALYZE, ctrl_obj = ctrl_obj, db_header = DbHeader(), route = Route() , template= Template(), session_enum = SessionKey(), request_dict = request_dict)
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)
    
@timesheet_bp.route(Route.CONFLICT_DATE)
def conflict_final_date():
    println(Route.CONFLICT_DATE, 'debug')
    try:
        request_dict = get_request_args()
        ctrl_obj   = ctrl()
        return render_template(Template.TIMESHEET_CONFLICT_DATE, ctrl_obj = ctrl_obj, db_header = DbHeader(), route = Route() , template= Template(), session_enum = SessionKey(), request_dict = request_dict)
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route(Route.CHECK_LOADING_SMARTSHEET, methods=['POST'])
def check_loading_smartsheet():
    println(Route.CHECK_LOADING_SMARTSHEET, 'debug')
    try:
        request_dict = get_request_form_ajax()
        try:
            sheet_ids = request_dict[SessionKey.SHEETS]
        except KeyError:
            sheet_ids = []
        result = ctrl().check_get_newest_data_feature_is_running(sheet_ids)
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route('/test')
def test():
    println('/test', 'debug')
    try:
        ctrl_obj   = ctrl()
        
        ctrl_obj.update_resource_of_sheet()
        
        return render_template("test.html", ctrl_obj = ctrl_obj, db_header = DbHeader(), route = Route() , template= Template())
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)
    
    
    
    