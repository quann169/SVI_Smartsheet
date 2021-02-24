from src.controllers.Controllers import Controllers
import logging
from logging.handlers import RotatingFileHandler
from src.commons.Utils import CommonUtils
import os, sys
import config

try:
    logging_lv      = config.LOGGING_LEVEL
except  AttributeError:
    logging_lv      = 'ERROR'
logging_level       = CommonUtils().select_logging_level(logging_lv)
log_formatter       = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
log_name            = os.path.join(config.WORKING_PATH, 'TimesheetReport.log')
log                 = logging.getLogger()
log.setLevel(logging_level)
handler             = logging.handlers.RotatingFileHandler(log_name,maxBytes= 1000*1024,backupCount=20)
handler.setFormatter(log_formatter)
log.addHandler(handler)


c = Controllers().parse_smarsheet_and_update_task()


        
# from src.models.database.ConnectionModel import Connection
# query   = '''show tables;'''
# cnn     = Connection()
# print (cnn.db_query(query))