IS_PRODUCT = True
VERSION = 'v0.2'
LOGGING_LEVEL = 'INFO'
if IS_PRODUCT:
    WORKING_PATH = './.data/workspace'
else:
    WORKING_PATH = './sample/data/workspace'
CONFIG_FILE = './config.py'