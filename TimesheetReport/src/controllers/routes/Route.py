'''
Created on Feb 24, 2021

@author: toannguyen
'''

import os, ast
from flask import Blueprint, render_template, session, redirect, url_for, abort, request, jsonify
from pprint import pprint
import logging
from src.commons.Utils import save_file_from_request, get_request_form_ajax, get_request_form_ajax, get_request_form_ajax, get_request_args, get_request_args_list
from src.controllers.Controllers import Controllers as ctrl
from src.commons.Enums import DbTable, DbHeader, SessionKey
from src.commons.Utils import println


tempalte_path =  os.getcwd() + 'src/views/templates'
static_path =  os.getcwd() + 'src/views/static'
timesheet_bp = Blueprint('timesheet_bp', __name__, template_folder=tempalte_path, static_folder=static_path)


@timesheet_bp.route('/')
def index():
    println('/', 'debug')
    try:
        ctrl_obj   = ctrl()
        return render_template("index.html", ctrl_obj = ctrl_obj, db_header = DbHeader())
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route('/home')
def home():
    println('/', 'debug')
    try:
        ctrl_obj   = ctrl()
        return render_template("home.html", ctrl_obj = ctrl_obj, db_header = DbHeader())
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
    

@timesheet_bp.route('/timeoff')
def timeoff():
    println('/timeoff', 'debug')
    try:
        ctrl_obj   = ctrl()
        return render_template("setting/timeoff.html", ctrl_obj = ctrl_obj, db_header = DbHeader())
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
        return render_template("log.html", ctrl_obj = ctrl_obj, db_header = DbHeader())
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route('/sheet')
def sheet():
    println('/sheet', 'debug')
    try:
        ctrl_obj    = ctrl()
        return render_template("setting/sheet.html", ctrl_obj = ctrl_obj, db_header = DbHeader())
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
        return render_template("setting/resource.html", ctrl_obj = ctrl_obj, db_header = DbHeader())
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
        return render_template("setting/holiday.html", ctrl_obj = ctrl_obj, db_header = DbHeader())
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

@timesheet_bp.route('/timesheet')
def timesheet():
    println('/', 'debug')
    try:
        request_dict = get_request_args_list()
        ctrl_obj   = ctrl()
        return render_template("timesheet.html", ctrl_obj = ctrl_obj, db_header = DbHeader(), session_enum = SessionKey(), request_dict = request_dict)
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)

@timesheet_bp.route('/test')
def test():
    println('/test', 'debug')
    try:
        ctrl_obj   = ctrl()
        
        ctrl_obj.get_timesheet_info(None, '2021-02-25', '2021-03-10', [1, 2, 3, 4], 'current')
        
        
        return render_template("test.html", ctrl_obj = ctrl_obj, db_header = DbHeader())
    except Exception as e:
        println(e, 'exception')
        return abort(500, e)