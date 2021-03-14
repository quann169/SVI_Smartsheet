import os, sys
sys.path.insert(0, './')
sys.path.insert(0, './3rd-src')

from src.controllers.controllers import Controllers
import config
from datetime import timedelta
from flask import Flask, g, session, redirect, url_for
from src.controllers.routes.route import timesheet_bp
from flask import Flask, flash, request, redirect, url_for
import webbrowser, threading
from threading import Timer
from src.commons.utils import logging_setting, get_free_tcp_port


# port        = 6602
port = get_free_tcp_port()
host        = "localhost"
tool_path = os.path.abspath(os.path.dirname(__file__))
logging_setting('TimesheetReport.log')


# app = Flask( __name__ , static_folder="%s/%s"%(tool_path, 'src/views/static'), template_folder="%s/%s"%(tool_path, 'src/views/templates'))
app = Flask( __name__ , static_folder="%s/%s"%(tool_path, 'views/static'), template_folder="%s/%s"%(tool_path, 'views/templates'))
app.config['WORKING_PATH'] = config.WORKING_PATH
app.config['SECRET_KEY']                    = 'TEST'
# app.config['SESSION_PERMANENT']             = True
# app.config['PERMANENT_SESSION_LIFETIME']    = timedelta(days = 7)
app.register_blueprint(timesheet_bp)

argv = sys.argv[1:]
all_configs     = {}


def open_browser():
    webbrowser.open_new('http://%s:%d/'%(host, port))
    
if __name__ == "__main__":
    # app.run(port=port, host=host, debug=True, use_reloader=True, threaded=True)
    thread  = threading.Thread(name='open GUI', target = app.run,  args=(host, port), kwargs={'threaded': True})
    thread.start()
    Timer(1, open_browser).start();
    
    
    
