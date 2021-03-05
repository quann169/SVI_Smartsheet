from src.controllers.Controllers import Controllers
import os, sys
import config
from datetime import timedelta
from flask import Flask, g, session, redirect, url_for
from src.controllers.routes.Route import timesheet_bp
from flask import Flask, flash, request, redirect, url_for
import webbrowser
from threading import Timer
from src.commons.Utils import logging_setting


port        = 6602
host        = "localhost"
tool_path = os.path.abspath(os.path.dirname(__file__))
logging_setting('TimesheetReport.log')


app = Flask( __name__ , static_folder="%s/%s"%(tool_path, 'src/views/static'), template_folder="%s/%s"%(tool_path, 'src/views/templates'))
app.config['WORKING_PATH'] = config.WORKING_PATH
app.config['SECRET_KEY']                    = 'TEST'
app.config['SESSION_PERMANENT']             = True
app.config['PERMANENT_SESSION_LIFETIME']    = timedelta(days = 7)
app.register_blueprint(timesheet_bp)

argv = sys.argv[1:]
all_configs     = {}
# @app.before_request
# def global_var():
#     g.tool_path             = tool_path

def open_browser():
    webbrowser.open_new('http://%s:%d/'%(host, port))
    
if __name__ == "__main__":
#     Timer(1, open_browser).start();
    app.run(port=port, host=host, debug=True, use_reloader=True, threaded=True)
    
    
    
    
