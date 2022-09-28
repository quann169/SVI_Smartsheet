'''
Created on Feb 24, 2021

@author: toannguyen
'''

import os, ast
from flask import Blueprint, render_template, session, redirect, url_for, abort, request, jsonify, send_file,\
                    send_from_directory, g
from pprint import pprint
import logging
from src.controllers.controllers import Controllers as ctrl
import master_config
from src.commons import enums, utils
from functools import wraps



smartsheet_bp = Blueprint('smartsheet_bp', __name__)


@smartsheet_bp.errorhandler(404)
def error_handle(e):
    return render_template(enums.Template.ERROR_404, error=e)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        ctrl_obj   = ctrl()
        password = utils.get_saved_password()
        username = ctrl_obj.user_name
        if password == None:
            return (redirect(url_for("smartsheet_bp.login")))
        else:
            check_password = ctrl_obj.authenticate_account(username, password)
            if check_password[0]:
                return f(*args, **kwargs)
            else:
                return (redirect(url_for("smartsheet_bp.login")))
        return (redirect(url_for("smartsheet_bp.login")))
    return wrap

@smartsheet_bp.route(enums.Route.INDEX, methods=[enums.MethodKeys.METHOD_POST, enums.MethodKeys.METHOD_GET])
def index():
    """ Starting page
    :param : 
    :return: home or login page
    """
    utils.println(enums.Route.INDEX, enums.LoggingKeys.LOGGING_DEBUG)
    try:  
        ctrl_obj   = ctrl()
        password = utils.get_saved_password()
        username = ctrl_obj.user_name
        if password == None:
            return (redirect(url_for("smartsheet_bp.login")))
        else:
            check_password = ctrl_obj.authenticate_account(username, password)
            if check_password[0]:
                return (redirect(url_for("smartsheet_bp.home")))
            else:
                return (redirect(url_for("smartsheet_bp.login")))
    except Exception as e:
        utils.println(e, enums.LoggingKeys.LOGGING_EXCEPTION)
        return abort(500, e)

@smartsheet_bp.route(enums.Route.LOGIN, methods=[enums.MethodKeys.METHOD_POST, enums.MethodKeys.METHOD_GET])
def login():
    """ Login page
    :param : 
    :return: login page
    """
    utils.println(enums.Route.LOGIN, enums.LoggingKeys.LOGGING_DEBUG)
    try:
        ctrl_obj   = ctrl()
        methods = utils.get_request_args()
        return render_template(enums.Template.LOGIN, ctrl_obj = ctrl_obj, enums = enums, utils = utils, \
                               methods = methods)
    except Exception as e:
        utils.println(e, enums.LoggingKeys.LOGGING_EXCEPTION)
        return abort(500, e)

@smartsheet_bp.route(enums.Route.LOGOUT, methods=[enums.MethodKeys.METHOD_POST, enums.MethodKeys.METHOD_GET])
def logout():
    """ logout page
    :param : 
    :return: logout page
    """
    utils.println(enums.Route.LOGOUT, enums.LoggingKeys.LOGGING_DEBUG)
    try:
        session.clear()
        utils.clear_saved_password()
        return (redirect(url_for("smartsheet_bp.login")))
    except Exception as e:
        utils.println(e, enums.LoggingKeys.LOGGING_EXCEPTION)
        return abort(500, e)

@smartsheet_bp.route(enums.Route.AUTH, methods=[enums.MethodKeys.METHOD_POST])
def auth():
    """ Authenticate user and domain password
    :param : 
    :return: (1 or 0, error message)
    """
    utils.println(enums.Route.AUTH, enums.LoggingKeys.LOGGING_DEBUG)
    methods = utils.get_request_form()
    password = methods[enums.SessionKeys.PASSWORD]
    username = methods[enums.SessionKeys.USERNAME].strip()
    remember = methods['remember']
    ctrl_obj = ctrl()
    result = ctrl_obj.authenticate_account(username, password, remember)
    return jsonify({'result': result})

@smartsheet_bp.route(enums.Route.HOME, methods=[enums.MethodKeys.METHOD_POST, enums.MethodKeys.METHOD_GET])
@login_required
def home():
    """ Home page
    :param : 
    :return: home page
    """
    utils.println(enums.Route.HOME, enums.LoggingKeys.LOGGING_DEBUG)
    try:
        ctrl_obj   = ctrl()
        return render_template(enums.Template.HOME, ctrl_obj = ctrl_obj, enums = enums, utils = utils)
    except Exception as e:
        utils.println(e, enums.LoggingKeys.LOGGING_EXCEPTION)
        return abort(500, e)

@smartsheet_bp.route(enums.Route.START_ANALYZE, methods=[enums.MethodKeys.METHOD_GET])
def start_analyze():
    """ Start Analyze
    :param : 
    :return: (1 or 0, message)
    """
    utils.println(enums.Route.START_ANALYZE, enums.LoggingKeys.LOGGING_DEBUG)
    try:
        result = ctrl().start_analyze()
        return jsonify({'result': result})
    except Exception as e:
        utils.println(e, enums.LoggingKeys.LOGGING_EXCEPTION)
        return abort(500, e)

@smartsheet_bp.route(enums.Route.GET_CONSOLE, methods=[enums.MethodKeys.METHOD_GET])
def get_console():
    """ Render  running log
    :param : 
    :return: 
    """
    utils.println(enums.Route.GET_CONSOLE, enums.LoggingKeys.LOGGING_DEBUG)
    ctrl_obj   = ctrl()
    result = ctrl_obj.render_console_content()
    return jsonify({'result': result})


@smartsheet_bp.route(enums.Route.ANALYZE, methods=[enums.MethodKeys.METHOD_POST, enums.MethodKeys.METHOD_GET])
@login_required
def analyze():
    """ Analyze page
    :param : 
    :return: Analyze page
    """
    utils.println(enums.Route.ANALYZE, enums.LoggingKeys.LOGGING_DEBUG)
    try:
        ctrl_obj   = ctrl()
        return render_template(enums.Template.ANALYZE, ctrl_obj = ctrl_obj, enums = enums, utils = utils)
    except Exception as e:
        utils.println(e, enums.LoggingKeys.LOGGING_EXCEPTION)
        return abort(500, e)

@smartsheet_bp.route(enums.Route.PREVIEW, methods=[enums.MethodKeys.METHOD_POST, enums.MethodKeys.METHOD_GET])
@login_required
def preview():
    """ Preview page
    :param : 
    :return: Preview page
    """
    utils.println(enums.Route.PREVIEW, enums.LoggingKeys.LOGGING_DEBUG)
    try:
        ctrl_obj   = ctrl()
        return render_template(enums.Template.PREVIEW, ctrl_obj = ctrl_obj, enums = enums, utils = utils)
    except Exception as e:
        utils.println(e, enums.LoggingKeys.LOGGING_EXCEPTION)
        return abort(500, e)


@smartsheet_bp.route(enums.Route.COMMIT, methods=[enums.MethodKeys.METHOD_GET])
@login_required
def commit():
    """ commit
    :param : 
    :return: (1 or 0, message)
    """
    utils.println(enums.Route.COMMIT, enums.LoggingKeys.LOGGING_DEBUG)
    try:
        result = ctrl().commit_to_smartsheet()
        return jsonify({'result': result})
    except Exception as e:
        utils.println(e, enums.LoggingKeys.LOGGING_EXCEPTION)
        return abort(500, e)

@smartsheet_bp.route(enums.Route.LOAD_FILE, methods=[enums.MethodKeys.METHOD_GET])
def load_file():
    """  LOAD_FILE CONTENT
    :param : 
    :return:  
    """
    utils.println(enums.Route.LOAD_FILE, enums.LoggingKeys.LOGGING_DEBUG)
    try:
        ctrl_obj   = ctrl()
        file_path = ctrl_obj.methods.get(enums.MethodKeys.PATH)
        file_path = file_path.rstrip('/')
        unsupport_extension = ['.gds', '.oa', '.tar.gz', '.gz', '.tar', '.db', '.zip', '.xlsx', '.xls']
        if os.path.exists(file_path):
            if os.path.isfile(file_path):
                filename, extension = os.path.splitext(file_path)
                if extension in unsupport_extension:
                    content = 'Unable to open files with the extension %s'%(str(unsupport_extension))
                else:
                    content = '<div style="white-space: pre;">'
                    content += utils.read_file(file_path)
                    content += '</div>'
            else:
                content = ''
                list_dir = os.listdir(file_path)
                list_dir = ['..'] + list_dir
                for dir_name in list_dir:
                    if dir_name == '..':
                        path = os.path.dirname(file_path)
                    else:
                        path = os.path.join(file_path, dir_name)
                    if os.path.isfile(path):
                        value = "<a href='%s?%s=%s' style='color: green;' >%s</a><br>"%(enums.Route.LOAD_FILE, enums.MethodKeys.PATH, path, dir_name)
                    else:
                        value = "<a href='%s?%s=%s' >%s</a><br>"%(enums.Route.LOAD_FILE, enums.MethodKeys.PATH, path, dir_name)
                    content += value
        else:
            content = 'No such file or directory: %s'%file_path
        return content
    except Exception as e:
        utils.println(e, enums.LoggingKeys.LOGGING_EXCEPTION)
        return abort(404, e)

@smartsheet_bp.route(enums.Route.GET_COMPARE_DETAIL_MODAL, methods=[enums.MethodKeys.METHOD_GET])
def get_compare_detail_modal():
    """ Render  detail modal content
    :param : 
    :return: 
    """
    utils.println(enums.Route.GET_COMPARE_DETAIL_MODAL, enums.LoggingKeys.LOGGING_DEBUG)
    ctrl_obj   = ctrl()
    result = ctrl_obj.render_compare_detail_modal_content()
    return jsonify({'result': result})
    