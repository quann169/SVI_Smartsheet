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
import config
from src.commons import message, enums, utils
from functools import wraps



smartsheet_bp = Blueprint('smartsheet_bp', __name__)


@smartsheet_bp.errorhandler(404)
def error_handle(e):
    return render_template(enums.Template.ERROR_404, error=e)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get(enums.SessionKey.IS_LOGIN):
            return f(*args, **kwargs)
        return (redirect(url_for("smartsheet_bp.login")))
    return wrap

@smartsheet_bp.route(enums.Route.INDEX, methods=[enums.OtherKeys.METHOD_POST, enums.OtherKeys.METHOD_GET])
def index():
    """ Starting page
    :param : 
    :return: home or login page
    """
    utils.println(enums.Route.INDEX, enums.OtherKeys.LOGGING_DEBUG)
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
        utils.println(e, enums.OtherKeys.LOGGING_EXCEPTION)
        return abort(500, e)

@smartsheet_bp.route(enums.Route.LOGIN, methods=[enums.OtherKeys.METHOD_POST, enums.OtherKeys.METHOD_GET])
def login():
    """ Login page
    :param : 
    :return: login page
    """
    utils.println(enums.Route.LOGIN, enums.OtherKeys.LOGGING_DEBUG)
    try:
        ctrl_obj   = ctrl()
        request_dict = utils.get_request_args()
        return render_template(enums.Template.LOGIN, ctrl_obj = ctrl_obj, enums = enums, \
                               request_dict = request_dict)
    except Exception as e:
        utils.println(e, enums.OtherKeys.LOGGING_EXCEPTION)
        return abort(500, e)

@smartsheet_bp.route(enums.Route.LOGOUT, methods=[enums.OtherKeys.METHOD_POST, enums.OtherKeys.METHOD_GET])
def logout():
    """ logout page
    :param : 
    :return: logout page
    """
    utils.println(enums.Route.LOGOUT, enums.OtherKeys.LOGGING_DEBUG)
    try:
        session.clear()
        utils.clear_saved_password()
        return (redirect(url_for("smartsheet_bp.login")))
    except Exception as e:
        utils.println(e, enums.OtherKeys.LOGGING_EXCEPTION)
        return abort(500, e)

@smartsheet_bp.route(enums.Route.AUTH, methods=[enums.OtherKeys.METHOD_POST])
def auth():
    """ Authenticate user and domain password
    :param : 
    :return: (1 or 0, error message)
    """
    utils.println(enums.Route.AUTH, enums.OtherKeys.LOGGING_DEBUG)
    request_dict = utils.get_request_form_ajax()
    password = request_dict[enums.SessionKey.PASSWORD]
    username = request_dict[enums.SessionKey.USERNAME].strip()
    remember = request_dict['remember']
    ctrl_obj = ctrl()
    result = ctrl_obj.authenticate_account(username, password, remember)
    return jsonify({'result': result})

@smartsheet_bp.route(enums.Route.HOME, methods=[enums.OtherKeys.METHOD_POST, enums.OtherKeys.METHOD_GET])
@login_required
def home():
    """ Home page
    :param : 
    :return: home page
    """
    utils.println(enums.Route.HOME, enums.OtherKeys.LOGGING_DEBUG)
    try:
        ctrl_obj   = ctrl()
        return render_template(enums.Template.HOME, ctrl_obj = ctrl_obj, enums = enums)
    except Exception as e:
        utils.println(e, enums.OtherKeys.LOGGING_EXCEPTION)
        return abort(500, e)

    