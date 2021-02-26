'''
Created on Feb 24, 2021

@author: toannguyen
'''

import os, ast
from flask import Blueprint, render_template, session, redirect, url_for, abort, request, jsonify
from pprint import pprint
import logging
from src.commons.Utils import save_file_from_request, get_request_form_ajax, get_request_form_ajax, get_request_form_ajax
from src.controllers.Controllers import Controllers as ctrl
from src.commons.Enums import DbTable, DbHeader


tempalte_path =  os.getcwd() + 'src/views/templates'
static_path =  os.getcwd() + 'src/views/static'
timesheet_bp = Blueprint('timesheet_bp', __name__, template_folder=tempalte_path, static_folder=static_path)


@timesheet_bp.route('/')
def home():
    logging.debug('/')
    try:
        return render_template("index.html")
    except Exception as e:
        logging.exception(e)
        return abort(500, e)

@timesheet_bp.route('/upload_file', methods=['POST'])
def upload_file():
    logging.debug('/upload_file')
    try:
        result = save_file_from_request()
        return jsonify({'result': result})
    except Exception as e:
        logging.exception(e)
        return abort(500, e)
    

@timesheet_bp.route('/timeoff')
def timeoff():
    logging.debug('/timeoff')
    try:
        ctrl_obj   = ctrl()
        return render_template("setting/timeoff.html", ctrl_obj = ctrl_obj, db_header = DbHeader())
    except Exception as e:
        logging.exception(e)
        return abort(500, e)

@timesheet_bp.route('/import_timeoff', methods=['POST'])
def import_timeoff():
    logging.debug('/import_timeoff')
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().import_timeoff(file_name=request_dict['file_name'])
        return jsonify({'result': result})
    except Exception as e:
        logging.exception(e)
        return abort(500, e)





@timesheet_bp.route('/log')
def log():
    logging.debug('/log')
    try:
        return render_template("log.html")
    except Exception as e:
        logging.exception(e)
        return abort(500, e)

@timesheet_bp.route('/sheet')
def sheet():
    logging.debug('/sheet')
    try:
        ctrl_obj    = ctrl()
        return render_template("setting/sheet.html", ctrl_obj = ctrl_obj, db_header = DbHeader())
    except Exception as e:
        logging.exception(e)
        return abort(500, e)

@timesheet_bp.route('/import_sheet', methods=['POST'])
def import_sheet():
    logging.debug('/import_sheet')
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().import_sheet(file_name=request_dict['file_name'])
        return jsonify({'result': result})
    except Exception as e:
        logging.exception(e)
        return abort(500, e)
    
@timesheet_bp.route('/resource')
def resource():
    logging.debug('/resource')
    try:
        return render_template("setting/resource.html")
    except Exception as e:
        logging.exception(e)
        return abort(500, e)

@timesheet_bp.route('/holiday')
def holiday():
    logging.debug('/holiday')
    try:
        ctrl_obj    = ctrl()
        return render_template("setting/holiday.html", ctrl_obj = ctrl_obj, db_header = DbHeader())
    except Exception as e:
        logging.exception(e)
        return abort(500, e)

@timesheet_bp.route('/import_holiday', methods=['POST'])
def import_holiday():
    logging.debug('/import_holiday')
    try:
        request_dict = get_request_form_ajax()
        result = ctrl().import_holiday(file_name=request_dict['file_name'])
        return jsonify({'result': result})
    except Exception as e:
        logging.exception(e)
        return abort(500, e)