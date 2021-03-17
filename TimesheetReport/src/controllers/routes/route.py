'''
Created on Feb 24, 2021

@author: toannguyen
'''

import os, ast
from flask import Blueprint, render_template, session, redirect, url_for, abort, request, jsonify, send_file,\
                    send_from_directory
from pprint import pprint
import logging
from src.commons.utils import save_file_from_request, get_request_form_ajax, get_request_form_ajax, \
                                get_request_form_ajax, get_request_args, get_request_args_list
from src.controllers.controllers import Controllers as ctrl
from src.commons.enums import DbTable, DbHeader, SessionKey
from src.commons.utils import println
import config

tempalte_path =  os.getcwd() + 'src/views/templates'
static_path =  os.getcwd() + 'src/views/static'
timesheet_bp = Blueprint('timesheet_bp', __name__, template_folder=tempalte_path, static_folder=static_path)


@timesheet_bp.route('/')
def index():
    println('/', 'debug')
    try:
        ctrl_obj   = ctrl()
        return render_template("screens/layout/index.html", ctrl_obj = ctrl_obj, db_header = DbHeader())
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route('/home')
def home():
    println('/', 'debug')
    try:
        ctrl_obj   = ctrl()
        return render_template("screens/home/home.html", ctrl_obj = ctrl_obj, db_header = DbHeader())
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route('/get_newest_data', methods=['POST'])
def get_newest_data():
    println('/get_newest_data', 'debug')
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().get_newest_data(from_date=request_dict[SessionKey.FROM], to_date=request_dict[SessionKey.TO], sheet_ids=request_dict[SessionKey.SHEETS])
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route('/get_newest_data_log', methods=['POST'])
def get_newest_data_log():
    println('/get_newest_data_log', 'debug')
    try:
        result = ctrl().get_newest_data_log()
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)
    
@timesheet_bp.route('/add_to_final', methods=['POST'])
def add_to_final():
    println('/add_to_final', 'debug')
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().add_to_final(from_date=request_dict[SessionKey.FROM], to_date=request_dict[SessionKey.TO], sheet_ids=request_dict[SessionKey.SHEETS])
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)
    
@timesheet_bp.route('/upload_file', methods=['POST'])
def upload_file():
    println('/upload_file', 'debug')
    try:
        result = save_file_from_request()
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route('/dowload_file', methods=['GET', 'POST'])
def download_file():
    request_dict = get_request_args()
    path = os.path.join(config.WORKING_PATH, request_dict[SessionKey.FILE_NAME])
    return send_file(path, as_attachment=True, cache_timeout=0)

@timesheet_bp.route('/export', methods=['POST'])
def export():
    println('/export', 'debug')
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().export_excel(from_date=request_dict[SessionKey.FROM], to_date=request_dict[SessionKey.TO], sheet_ids=request_dict[SessionKey.SHEETS])
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)



@timesheet_bp.route('/timeoff')
def timeoff():
    println('/timeoff', 'debug')
    try:
        ctrl_obj   = ctrl()
        return render_template("screens/setting/timeoff.html", ctrl_obj = ctrl_obj, db_header = DbHeader())
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route('/import_timeoff', methods=['POST'])
def import_timeoff():
    println('/import_timeoff', 'debug')
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().import_timeoff(file_name=request_dict['file_name'])
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route('/log')
def log():
    println('/log', 'debug')
    try:
        ctrl_obj   = ctrl()
        return render_template("screens/log/log.html", ctrl_obj = ctrl_obj, db_header = DbHeader())
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route('/sheet')
def sheet():
    println('/sheet', 'debug')
    try:
        ctrl_obj    = ctrl()
        return render_template("screens/setting/sheet.html", ctrl_obj = ctrl_obj, db_header = DbHeader())
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route('/import_sheet', methods=['POST'])
def import_sheet():
    println('/import_sheet', 'debug')
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().import_sheet(file_name=request_dict['file_name'])
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)
    
@timesheet_bp.route('/resource')
def resource():
    println('/resource', 'debug')
    try:
        ctrl_obj   = ctrl()
        return render_template("screens/setting/resource.html", ctrl_obj = ctrl_obj, db_header = DbHeader())
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route('/import_resource', methods=['POST'])
def import_resource():
    println('/import_resource', 'debug')
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().import_resource(file_name=request_dict['file_name'])
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)
    
@timesheet_bp.route('/holiday')
def holiday():
    println('/holiday', 'debug')
    try:
        ctrl_obj    = ctrl()
        return render_template("screens/setting/holiday.html", ctrl_obj = ctrl_obj, db_header = DbHeader())
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route('/import_holiday', methods=['POST'])
def import_holiday():
    println('/import_holiday', 'debug')
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().import_holiday(file_name=request_dict['file_name'])
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route('/update_session', methods=['POST'])
def update_session():
    println('/update_session', 'debug')
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().update_session(request_dict['session_key'], request_dict['session_value'], )
        return jsonify({'result': result})
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route('/daily_timesheet')
def daily_timesheet():
    println('/daily_timesheet', 'debug')
    try:
        request_dict = get_request_args_list()
        ctrl_obj   = ctrl()
        ctrl_obj.add_defalt_config_to_method_request(request_dict)
        return render_template("screens/timesheet/daily_timesheet.html", ctrl_obj = ctrl_obj, db_header = DbHeader(), session_enum = SessionKey(), request_dict = request_dict)
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route('/resource_timesheet')
def resource_timesheet():
    println('/export_timesheet', 'debug')
    try:
        request_dict = get_request_args_list()
        ctrl_obj   = ctrl()
        ctrl_obj.add_defalt_config_to_method_request(request_dict)
        return render_template("screens/timesheet/resource_timesheet.html", ctrl_obj = ctrl_obj, db_header = DbHeader(), session_enum = SessionKey(), request_dict = request_dict)
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route('/analyze')
def analyze():
    println('/analyze', 'debug')
    try:
        request_dict = get_request_args_list()
        ctrl_obj   = ctrl()
        return render_template("screens/timesheet/analyze.html", ctrl_obj = ctrl_obj, db_header = DbHeader(), session_enum = SessionKey(), request_dict = request_dict)
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)
    
@timesheet_bp.route('/conflict_final_date')
def conflict_final_date():
    println('/conflict_final_date', 'debug')
    try:
        request_dict = get_request_args_list()
        ctrl_obj   = ctrl()
        return render_template("screens/timesheet/conflict_final_date.html", ctrl_obj = ctrl_obj, db_header = DbHeader(), session_enum = SessionKey(), request_dict = request_dict)
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route('/check_loading_smartsheet', methods=['POST'])
def check_loading_smartsheet():
    println('/check_loading_smartsheet', 'debug')
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
        
        
        return render_template("test.html", ctrl_obj = ctrl_obj, db_header = DbHeader())
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)
    
    
    
    