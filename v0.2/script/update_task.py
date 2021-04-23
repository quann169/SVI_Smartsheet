import sys
sys.path.insert(0, '../')
sys.path.insert(0, '../3rd-src')
from src.controllers.controllers import Controllers
from src.commons.utils import logging_setting

def main():
    logging_setting('TimesheetReportUpdateTask.log')
    Controllers().parse_smarsheet_and_update_task()

if __name__ == '__main__':
    main()