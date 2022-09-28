IS_PRODUCT = False
VERSION = 'v0.1'
LOGGING_LEVEL = 'INFO'
if IS_PRODUCT:
    WORKING_PATH = './.data/workspace'
else:
    WORKING_PATH = './sample/SmartsheetCash_v0.1/data/workspace'
CONFIG_FILE = './config.py'