import os, sys
sys.path.insert(0, './')
sys.path.insert(0, './3rd-src')
from src.commons.utils import logging_setting, get_free_tcp_port
import requests, time
import config
from flask import Flask, g
from src.controllers.routes.route import timesheet_bp
import webbrowser, threading
from threading import Timer
from src.models.database.connection_model import Connection
from src.controllers.controllers import Controllers as ctrl



        
__version__  = 'v0.1'

port        = 6602
# port = get_free_tcp_port()
host        = "localhost"
tool_path = os.path.abspath(os.path.dirname(__file__))
logging_setting('TimesheetReport.log')

template_path =  'src/views/templates'
static_path =  'src/views/static'
# template_path =  '.data/views/templates'
# static_path =  '.data/views/static'

app = Flask( __name__ , static_folder="%s/%s"%(tool_path, static_path), template_folder="%s/%s"%(tool_path, template_path))
app.config['SECRET_KEY']                    = 'SECRET_KEY'

app.register_blueprint(timesheet_bp)

argv = sys.argv[1:]
all_configs     = {}
url = 'http://%s:%d/'%(host, port)
def open_browser():
    webbrowser.open_new(url)

connect_obj = Connection()
pool_conn = connect_obj.create_pool_connection()

@app.before_request
def create_connection():
    g.pool_conn = pool_conn
    g.tool_path = tool_path
    g.template_path = template_path

if __name__ == "__main__":
    app.run(port=port, host=host, debug=True, use_reloader=True, threaded=True)
#     thread  = threading.Thread(name='open GUI', target = app.run,  args=(host, port), kwargs={'threaded': True})
#     thread.start()
#     while True:
#         # Waiting for Flask start server
#         request = requests.get(url)
#         if request.status_code == 200:
#             print('Starting browser...')
#             break
#         else:
#             print('Checking RUL: %s...'%url)
#         time.sleep(1)
#     Timer(1, open_browser).start()
#     print('Start browser: Done')
    
    
