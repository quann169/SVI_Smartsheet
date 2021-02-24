from src.controllers.Controllers import Controllers
from src.commons.Utils import CommonUtils

def main():
    CommonUtils().logging_setting('TimesheetReportUpdateTask.log')
    Controllers().parse_smarsheet_and_update_task()

if __name__ == '__main__':
    main()