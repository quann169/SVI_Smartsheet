import os, sys
sys.path.insert(0, './')
sys.path.insert(0, './3rd-src')
from src.commons import utils, enums
import requests, time
import master_config
from flask import Flask, g, session
from src.controllers.routes.route import smartsheet_bp
import webbrowser, threading
from threading import Timer
from src.controllers.controllers import Controllers as ctrl
        
version  = master_config.VERSION
if master_config.IS_PRODUCT:
    port = utils.get_free_tcp_port()
    template_path =  '.data/views/templates'
    static_path =  '.data/views/static'
else:
    port        = 6602
    template_path =  'src/views/templates'
    static_path =  'src/views/static'
    
host        = "localhost"
tool_path = os.path.abspath(os.path.dirname(__file__))
utils.logging_setting('SmartsheetCash.log')

app = Flask( __name__ , static_folder="%s/%s"%(tool_path, static_path), template_folder="%s/%s"%(tool_path, template_path))
app.config['SECRET_KEY']                    = 'SECRET_KEY'

app.register_blueprint(smartsheet_bp)

argv = sys.argv[1:]
all_master_configs     = {}
url = 'http://%s:%d/'%(host, port)
def open_browser():
    webbrowser.open_new(url)


@app.before_request
def create_connection():
    g.tool_path = tool_path
    g.template_path = template_path
    g.version       = version

if __name__ == "__main__":
    print('URL: %s'%url)
    if master_config.IS_PRODUCT:
        thread  = threading.Thread(name='open GUI', target = app.run,  args=(host, port), kwargs={'threaded': True})
        thread.start()
        while True:
            # Waiting for Flask start server
            request = requests.get(url)
            if request.status_code in [200]:
                print('Starting browser...')
                break
            else:
                print('Checking URL: %s...'%url)
            time.sleep(1)
        Timer(1, open_browser).start()
        print('Start browser: Done')
    else:
        app.run(port=port, host=host, debug=True, use_reloader=True, threaded=True)
    
