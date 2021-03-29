import datetime
from src.svi.controller.TaskController import *
from src.svi.enum import Enum
from src.svi.utils import Util
import pathlib
from src_3rd import  xlwt
from  src_3rd import xlrd
from src_3rd.xlwt import Workbook 
import sys
import os, re
import time
import shutil
from pprint import pprint
from src_3rd import pandas
import getpass
from decimal import Decimal
from win32com.client import DispatchEx
def Run__():
	time1 = time.time()

	print('Start time: %s' %(str(datetime.datetime.now())))
	print("------------------------------------------------------------------------------")
	
	dir_ = os.path.dirname(os.path.abspath(__file__))
	try:
		os.makedirs(dir_ + '\Log')
	except:
		shutil.rmtree(dir_ + '\Log')
		os.makedirs(dir_ + '\Log')
	if not os.path.exists(dir_ + '\Cache'):
		os.makedirs(dir_ + '\Cache')
	 #open config file
	staff_path = ("%s\config.xlsx"%(dir_))
	userInfo = {}
	print('Config file is %s' %(staff_path))
	try:
		wb = xlrd.open_workbook(staff_path)
	except IOError as e:
		print('[Error] %s'%e)
		sys.exit()
	listItems = {1 : {}, 2 : {}, 3 : {}, 4 : {}}
	startDate = ''
	endDate = ''
	currentUser = getpass.getuser()
	dictInfoUser = {}
	lsSheetKey = [Enum.Header.TASK_NAME, Enum.Header.DURATION, Enum.Header.START_DATE, Enum.Header.END_DATE, Enum.Header.ASSIGNED_TO, Enum.Header.COMPLETE, Enum.Header.ALLOCATION]
	Sheet = {}
	sheet1 = wb.sheet_by_name('Staff') 
	sheet1.cell_value(0, 0)
	print('Start get info from Config.xlsx')
	excelHoliday = Util.get_info_excel(dir_)
	ignore_task = Util.get_ignore_task(dir_)
	df = pandas.read_excel(staff_path, sheet_name='Staff')
	df = {x.strip(): v  for x, v in df.items()}
	configInfo = {}
	columResource = df[Enum.UserInfoConfig.RESOURCE]
	columFullName = df[Enum.UserInfoConfig.FULL_NAME]
	columType = df[Enum.UserInfoConfig.TYPE]
	columRole = df[Enum.UserInfoConfig.ROLE]
	columOtherInfo = df[Enum.UserInfoConfig.LIST_MAIL]
	columMail = df[Enum.UserInfoConfig.MANAGER_EMAIL]
	columExclude = df[Enum.UserInfoConfig.EXCLUDE]
	columEngLevel = df[Enum.UserInfoConfig.ENG_LEVEL]
		#get info of user
	mail_to_user_name = {}
	for row_ in range(0, len(columResource)):
		lsRow = ['', str(columResource[row_]), str(columFullName[row_]), str(columType[row_]), str(columRole[row_]), str(columOtherInfo[row_]), str(columMail[row_]), str(columExclude[row_]), str(columEngLevel[row_])]
		if (lsRow[1].strip() != ''):
			if (lsRow[1].strip() in userInfo.keys()):
				print ('Duplicate Resource %s,  line %s in Config.xlsx'%(lsRow[1].strip(), row_ + 2))
				sys.exit()
			userInfo[lsRow[1].strip()] = {}
			userInfo[lsRow[1].strip()][Enum.UserInfoConfig.TYPE] = lsRow[3].strip()
			userInfo[lsRow[1].strip()][Enum.UserInfoConfig.ROLE] = lsRow[4].strip()
			userInfo[lsRow[1].strip()][Enum.UserInfoConfig.FULL_NAME] = lsRow[2].strip()
			userInfo[lsRow[1].strip()][Enum.UserInfoConfig.MANAGER_EMAIL] = lsRow[6].strip()
			userInfo[lsRow[1].strip()][Enum.UserInfoConfig.ENG_LEVEL] = lsRow[8].strip()
			excludeVal = 0
			try:
				excludeVal = int(Decimal(str(lsRow[7]).strip()))
			except:
				excludeVal = 0
			userInfo[lsRow[1].strip()][Enum.UserInfoConfig.IS_COUNT] = excludeVal
			lsM = re.findall('\S+@\S+', str(lsRow[5].strip()))
			if len(lsM) != 0:
				mail__ = lsM[0].replace(',', '')
				mail__ = mail__.replace(';', '')
				userInfo[lsRow[1].strip()][Enum.UserInfoConfig.MAIL] = mail__
				mail_to_user_name[mail__] = lsRow[1].strip()
			else:
				userInfo[lsRow[1].strip()][Enum.UserInfoConfig.MAIL] = ''
			string_ = lsRow[5].replace(';', ',')
			listOtherInfo = string_. split(',')
			for id1 in range(0, len(listOtherInfo)):
				listOtherInfo[id1] = listOtherInfo[id1].strip()
			if not (lsRow[1].strip().lower() in listOtherInfo):
				listOtherInfo.append(lsRow[1].lower())
			userInfo[lsRow[1].strip()][Enum.UserInfoConfig.LIST_MAIL] = listOtherInfo
# 			print (userInfo.keys())
	print('Config ' + str(len(userInfo)) + ' user ')
	
	
	#get time off
	dictTimeOff = Util.get_info_time_off(dir_, excelHoliday, userInfo)
	
	

	#get item
	sheet2 = wb.sheet_by_name('Option')	
	if  sheet2.row_values(0)[3].lower().strip() == 'yes':
		listItems[1]['status'] = 1
	else:
		listItems[1]['status'] = 0
	if  sheet2.row_values(2)[3].lower().strip() == 'yes':
		listItems[2]['status'] = 1
	else:
		listItems[2]['status'] = 0
	
	if  sheet2.row_values(4)[3].lower().strip() == 'yes':
		listItems[3]['status'] = 1
	else:
		listItems[3]['status'] = 0
		
	if  sheet2.row_values(5)[3].lower().strip() == 'yes':
		listItems[4]['status'] = 1
	else:
		listItems[4]['status'] = 0
		
	startDate = str(sheet2.row_values(6)[3])
	endDate = str(sheet2.row_values(7)[3])
	startDate_2 = str(sheet2.row_values(14)[3])
	endDate_2 = str(sheet2.row_values(15)[3])
	dateSendEmail = str(sheet2.row_values(8)[3]).split(',')
	ccMail_ = str(sheet2.row_values(9)[3])
	ccMail = Util.get_cc_mail(ccMail_)
	list_proj1 = (sheet2.row_values(10)[3]).split(',')
	list_proj2 = (sheet2.row_values(11)[3]).split(',')
	list_proj3 = (sheet2.row_values(12)[3]).split(',')
	list_proj4 = (sheet2.row_values(13)[3]).split(',')
	list_key_define_real_proj = []
	list_key_define_rnd_proj = []
	list_key_define_pre_sale_proj = []
	list_key_define_post_sale_proj = []
	for element_  in list_proj1:
		list_key_define_real_proj.append(element_.strip())
	for element_2  in list_proj2:
		list_key_define_rnd_proj.append(element_2.strip())
	for element_  in list_proj3:
		list_key_define_pre_sale_proj.append(element_.strip())
	for element_2  in list_proj4:
		list_key_define_post_sale_proj.append(element_2.strip())
	i = datetime.datetime.now()
	if not (dateSendEmail):
		dateSendEmail = ['%s-%s-%s'%(i.year, i.month, i.day)]
	Util.check_valid_send_email_date(startDate, endDate, dateSendEmail)
	Util.check_valid_send_email_date(startDate, endDate, [startDate_2])
	Util.check_valid_send_email_date(startDate, endDate, [endDate_2])
	endWeekSendEmail, startWeekSendEmail = Util.get_end_start_week(dateSendEmail)
	startWeekSendEmail.sort()
	
		#check config start, end date------------
	try:
		objDateS = datetime.datetime.strptime(startDate, '%Y-%m-%d')
	except:
		print('Config Error:: Format start date error: ' + startDate)
		sys.exit()
	try:
		objDateE = datetime.datetime.strptime(endDate, '%Y-%m-%d')
	except:
		print('Config Error:: Format end date error: ' + endDate)
		sys.exit()	
	try:
		objDateS2 = datetime.datetime.strptime(startDate_2, '%Y-%m-%d')
	except:
		print('Config Error:: Format start date error: ' + startDate_2)
		sys.exit()
	try:
		objDateE2 = datetime.datetime.strptime(endDate_2, '%Y-%m-%d')
	except:
		print('Config Error:: Format end date error: ' + endDate_2)
		sys.exit()	
	sy, sm, sd = Util.toDate(startDate)
	ey, em, ed = Util.toDate(endDate)
	if datetime.datetime(ey, em, ed) <= datetime.datetime(sy, sm, sd):
		print('Config Error: End date is previou day of start date: Start date: %s - End date: %s' %(startDate, endDate))
		sys.exit()
	
	sy_2, sm_2, sd_2 = Util.toDate(startDate_2)
	ey_2, em_2, ed_2 = Util.toDate(endDate_2)
	if datetime.datetime(ey_2, em_2, ed_2) <= datetime.datetime(sy_2, sm_2, sd_2):
		print('Config Error: End date is previou day of start date: Start date: %s - End date: %s' %(startDate_2, endDate_2))
		sys.exit()
		
		#check config show detail------------
	lsRow2_ = sheet2.row_values(Enum.UserInfoConfig.ROW_GET_SHOW_DETAIL)

	ls_detail = sheet2.row_values(1)[3].lower().split(',')
	listItems[1]['show detail'] = 1
	listItems[1]['limit'] = False
	try:
		if ls_detail[0].strip() == 'no':
			listItems[1]['show detail'] = 0
	except:
		pass
	try:
		if ls_detail[1].strip() == 'limit':
			listItems[1]['limit'] = True
	except:
		pass
	
	ls_detail = sheet2.row_values(3)[3].lower().split(',')
	listItems[2]['show detail'] = 1
	listItems[2]['limit'] = False
	try:
		if ls_detail[0].strip() == 'no':
			listItems[2]['show detail'] = 0
	except:
		pass
	try:
		if ls_detail[1].strip() == 'limit':
			listItems[2]['limit'] = True
	except:
		pass
	
	
	
	
	
	for item in listItems:
		if listItems[item]['status']:
			if (item in [1,2]) and (listItems[item]['show detail']):
				print('Select item ' + str(item) + ' and show detail')
			else:
				print('Select item ' + str(item))

	print('config Week to Report is: ' + str(startWeekSendEmail))
	print('Config start date is: ' + startDate)
	print('Config end date is: ' + endDate)
	#--------------------------------------
	
	#get sheet dict
	sheet3 = wb.sheet_by_name('Sheet')	
	for row___ in range(Enum.UserInfoConfig.ROW_GET_SHEET, sheet3.nrows):
		lsRow__ = sheet3.row_values(row___)
		Sheet[lsRow__[1]] ={}
		for j in range(1, 9):
			for index in range(0,len(lsSheetKey)):
				#remove % in header
				headerName_ = lsRow__[index + 2].replace('%', '')
				headerName = headerName_.strip()
				Sheet[lsRow__[1]][lsSheetKey[index]] = headerName
	
	for user__ in userInfo:
		if len(userInfo[user__][Enum.UserInfoConfig.LIST_MAIL]) != 0:
			for info in userInfo[user__][Enum.UserInfoConfig.LIST_MAIL]:
				dictInfoUser[info] = user__
	wb.release_resources()
	
	ListSheetFilter = []
	ListUserFilter = []
	for sheet__ in Sheet.keys():
		ListSheetFilter.append(sheet__)
	for user_ in userInfo.keys():
		ListUserFilter.append(user_)
	print('Config ' + str(len(ListSheetFilter)) + ' sheet: ' + ', '.join(ListSheetFilter))
		
		#check config Sheet name
	rowObj = RowParsing(dir_)
	
	strOutS, lsSheet, sheetEdit = rowObj.checkSheetConfigIsExist(ListSheetFilter, Sheet)
	ListSheetFilter = lsSheet
	
	Sheet = sheetEdit
	if len(strOutS):
		print('Config Error: Not exist in Smartsheet - Sheet name: ' + strOutS)
		sys.exit()
		
		#check config header name
	for sheetN in ListSheetFilter:
		lsHeader = []
		for head__ in Sheet[sheetN].values():
			lsHeader.append(head__)
# 		print(lsHeader)
		strOutH = rowObj.checkHeaderExistInSheet(sheetN, lsHeader)
		if len(strOutH):
			print('Config Error: Not exist Header name in %s - Header name: %s' %(sheetN, strOutH))
			sys.exit()

	time2 = time.time()
	print("Get info from Config.xlsx done: " + Util.getTimeRun(time1, time2))
	print("------------------------------------------------------------------------------")

# for item in ListItems:

	userInfoDict_, sheetInfoDict_, sheetInfoDict2_ = rowObj.getAllSheetAndWorkTimeOfUser(ListSheetFilter, ListUserFilter, startDate, endDate, userInfo, dictInfoUser, Sheet, dir_, excelHoliday, dictTimeOff, ignore_task)
	
	userInfoDict, sheetInfoDict = rowObj.caculateWorkTimeAndAddInfo(startDate, endDate, userInfoDict_, sheetInfoDict_, dir_, excelHoliday, dictTimeOff)
	dictToSendMail = Util.get_user_great_or_less(userInfoDict, startWeekSendEmail, userInfo, dictTimeOff)
	startRow = Enum.HeaderExcelAndKeys.START_ROW
	startColum = Enum.HeaderExcelAndKeys.START_COLUM
	wb = Workbook()
	colorDict, colorDictNoneBorder = Util.definedColor()
	colorTextDict, colorTextDictNoneBorder = Util.definedColorText()
	controlObj = Controllers()
	
	
	
	if listItems[1]['status'] == 1:
		print("Running  Item I001 - Caculate working time and filter all sheet of user by week")
		
		showDetail = listItems[1]['show detail']
		sheetName = wb.add_sheet('Weekly Resource')
		is_limit = listItems[1]['limit']
		lsheader = Util.headerToPrintExcel(1, startDate, endDate, 'week', dir_, excelHoliday, False)
		#colum, row
		getBy = Enum.HeaderExcelAndKeys.TOTAL_WEEK
		controlObj.printDictToExcel(sheetName, lsheader, userInfoDict, startRow, startColum, getBy, colorDict, colorDictNoneBorder, showDetail, is_limit)
		print("Running  Item I001 done")
		print("------------------------------------------------------------------------------")
# 		
	if listItems[2]['status'] == 1:
		print("Running  Item I002 - Caculate working time and filter all sheet of user by month")
		is_limit = listItems[2]['limit']
		showDetail = listItems[2]['show detail']
		sheetName = wb.add_sheet('Monthly Resource')
		lsheader = Util.headerToPrintExcel(1, startDate, endDate, 'month', dir_, excelHoliday, False)
		#colum, row
		getBy = Enum.HeaderExcelAndKeys.TOTAL_MONTH
		controlObj.printDictToExcel(sheetName, lsheader, userInfoDict, startRow, startColum, getBy, colorDict, colorDictNoneBorder, showDetail, is_limit)	
		print("Running  Item I002 done")
		print("------------------------------------------------------------------------------")
	if listItems[3]['status'] == 1:
 		
		print("Running  Item I005 - Caculate working time and filter all user of sheet by week ")
 		
		sheetName = wb.add_sheet('Weekly Project (new)')
		lsheader = Util.headerToPrintExcel(0, startDate, endDate, 'week', dir_, excelHoliday, True)
		#colum, row
		getBy = Enum.HeaderExcelAndKeys.TOTAL_WEEK
		controlObj.printDictToExcelByProjectNew(sheetName, lsheader, sheetInfoDict, startRow, startColum, getBy, colorDict, colorDictNoneBorder)
		print("Running  Item I005 done")
		print("------------------------------------------------------------------------------")
	if listItems[4]['status'] == 1:
		print("Running  Item I006 - Caculate working time and filter all user of sheet by month")
 		
		sheetName = wb.add_sheet('Monthly Project (new)')
		lsheader = Util.headerToPrintExcel(0, startDate, endDate, 'month', dir_, excelHoliday, True)
		#colum, row
		getBy = Enum.HeaderExcelAndKeys.TOTAL_MONTH
		controlObj.printDictToExcelByProjectNew(sheetName, lsheader, sheetInfoDict, startRow, startColum, getBy, colorDict, colorDictNoneBorder)
		print("Running  Item I005 done")
		print("------------------------------------------------------------------------------")
	
	if True:
		print("Creating Monthly Timesheet")
		sheetName = wb.add_sheet('Monthly Timesheet')
		lsheader = ['Position', 'Start month', 'End month', 'Start date', 'End date', 'Project', 'Task name', 'Emp name', 'Allocation', 'Work hours', 'Max hours']
		#colum, row
		controlObj.printToExcelMonthlyOrWeeklyTimesheet(sheetName, lsheader, sheetInfoDict2_, startRow, startColum, 'month')
		
	if True:
		print("Creating Weekly Timesheet")
		sheetName = wb.add_sheet('Weekly Timesheet')
		lsheader = ['Position', 'Start week', 'End week', 'Start date', 'End date', 'Project', 'Task name', 'Emp name', 'Allocation', 'Work hours', 'Max hours', 'WW']
		#colum, row
		controlObj.printToExcelMonthlyOrWeeklyTimesheet(sheetName, lsheader, sheetInfoDict2_, startRow, startColum, 'week')
		
	if True:
		print("Creating Report Timesheet")
		for report_week in dictToSendMail:
			sheetName = wb.add_sheet('Report_%s'%report_week)
			lsheader = ['Manager (Mail)', 'Resource', 'Working hours', 'Off work', 'Total', 'Detail', 'Comment']
			#colum, row
			controlObj.printReportToExcel(sheetName, lsheader, dictToSendMail[report_week], startWeekSendEmail, startRow, startColum, colorDict, colorDictNoneBorder, userInfo)
	
	
	###############
	if True:
		print("Create Weekly Resource 2")
		
		sheetName = wb.add_sheet('Weekly resource 2')
		#colum, row
		getBy = Enum.HeaderExcelAndKeys.TOTAL_WEEK
		controlObj.createResourceCompareWorkingHourBetweenTrainingAndRealProjectByWeekly(sheetName, userInfoDict, getBy, userInfo, startDate_2, endDate_2, dir_, excelHoliday, colorDict, colorDictNoneBorder, mail_to_user_name, list_key_define_real_proj, list_key_define_rnd_proj, dictTimeOff, list_key_define_pre_sale_proj, list_key_define_post_sale_proj)
		print("------------------------------------------------------------------------------")

	try:
		wb.save('%s\TimeSheet.xls'%(dir_))

		os.system('start %s\TimeSheet.xls'%(dir_))
		print('Timesheets report will be get info in sheet Report of file TimeSheet.xls!')
		print('Please review results before confirm to send mail!')
	except KeyError:
		print('Error to save TimeSheet.xls')
		sys.exit()
	if currentUser in Enum.UserInfoConfig.LIST_USER_SEND_MAIL :
		send_ = False
		while True:
			confirm_ = input("Confirm to send mail [Yes/No]: ") 
			confirm_ = confirm_.strip()
			if confirm_.lower() == 'yes':
				send_ = True
				break
			if confirm_.lower() == 'no':
				break
		if send_:
			controlObj.send_mail(dir_, startWeekSendEmail, ccMail, userInfo)
	time3 = time.time()
	print('Time to run all: %s' %(Util.getTimeRun(time1, time3)))

   

if __name__ == '__main__':
    try:
    	Run__()
    except BaseException:
    	if str(sys.exc_info()[0]) == "<class 'SystemExit'>":
    		print('Error: System Exit')
    	else:
#     		print(sys.exc_info()[0])
	        import traceback
	        print(traceback.format_exc())
    finally:
        print("Press Enter to exit ...")
        input() 
	


	