import datetime
from Controller.TaskController import *
from Enum import Enum
from Utils import Util
import pathlib
import xlwt
import xlrd
from xlwt import Workbook 
from pprint import pprint
import sys
import os
dir_ = os.path.dirname(os.path.abspath(__file__))

staff_path = ("%s\Config.xlsx"%(dir_)) 
userInfo = {}
try:
	wb = xlrd.open_workbook(staff_path)
except IOError as e:
	print('os.path.dirname(os.path.abspath(__file__))')
	sys.exit()
listItems = {1 : {}, 2 : {}, 3 : {}, 4 : {}}
startDate = ''
endDate = ''

dictInfoUser = {}
lsSheetKey = [Enum.Header.TASK_NAME, Enum.Header.DURATION, Enum.Header.START_DATE, Enum.Header.END_DATE, Enum.Header.ASSIGNED_TO, Enum.Header.COMPLETE, Enum.Header.ALLOCATION]
Sheet = {}
sheet_ =  Sheet
sheet1 = wb.sheet_by_name('Staff') 
sheet1.cell_value(0, 0)
#get info of user
for row_ in range(Enum.UserInfoConfig.ROW_GET_USER_INFO, sheet1.nrows):
	lsRow = sheet1.row_values(row_)
	userInfo[lsRow[4]] = {}
	userInfo[lsRow[4]][Enum.UserInfoConfig.POSITION] = lsRow[5]
	userInfo[lsRow[4]][Enum.UserInfoConfig.SENIORITY_LEVEL] = lsRow[6]
	listOtherInfo = lsRow[7]. split(',')
	for id1 in range(0, len(listOtherInfo)):
		listOtherInfo[id1] = listOtherInfo[id1].strip()
	userInfo[lsRow[4]][Enum.UserInfoConfig.LIST_MAIL] = listOtherInfo

#get item
sheet2 = wb.sheet_by_name('Config')	

lsRow_ = sheet2.row_values(Enum.UserInfoConfig.ROW_GET_STATUS_AND_START_END_DATE)
for i in range(Enum.UserInfoConfig.COLUM_GET_STATUS, Enum.UserInfoConfig.COLUM_GET_STATUS + 4):
	if lsRow_[i].lower() == 'yes':
		listItems[i]['status'] = 1
	else:
		listItems[i]['status'] = 0
startDate = str(lsRow_[6])
endDate = str(lsRow_[7])
sy, sm, sd = Util.toDate(startDate)
ey, em, ed = Util.toDate(endDate)
if datetime.datetime(ey, em, ed) <= datetime.datetime(sy, sm, sd):
	print('Start date and End date fail in Config.xlsx')
	sys.exit()

lsRow2_ = sheet2.row_values(Enum.UserInfoConfig.ROW_GET_SHOW_DETAIL)
for j in range(Enum.UserInfoConfig.COLUM_GET_STATUS, Enum.UserInfoConfig.COLUM_GET_STATUS + 2):
	if lsRow2_[j].lower() == 'yes':
		listItems[j]['show detail'] = 1
	else:
		listItems[j]['show detail'] = 0


#get sheet dict
for row___ in range(Enum.UserInfoConfig.ROW_GET_SHEET, sheet2.nrows):
	lsRow__ = sheet2.row_values(row___)
	Sheet[lsRow__[1]] ={}
	for j in range(1, 9):
		for index in range(0,len(lsSheetKey)):
			Sheet[lsRow__[1]][lsSheetKey[index]] = lsRow__[index + 2]
			

for user__ in userInfo:
	if len(userInfo[user__][Enum.UserInfoConfig.LIST_MAIL]) != 0:
		for info in userInfo[user__][Enum.UserInfoConfig.LIST_MAIL]:
			dictInfoUser[info] = user__
wb.release_resources()

ListSheetFilter = []
ListUserFilter = []
for sheet__ in sheet_.keys():
	ListSheetFilter.append(sheet__)
for user_ in userInfo.keys():
	ListUserFilter.append(user_)




# for item in ListItems:

def Run__():
	userInfoDict_, sheetInfoDict_ = RowParsing.getAllSheetAndWorkTimeOfUser(ListSheetFilter, ListUserFilter, startDate, endDate, userInfo, dictInfoUser, Sheet, dir_)
	userInfoDict, sheetInfoDict = RowParsing.caculateWorkTimeAndAddInfo(startDate, endDate, userInfoDict_, sheetInfoDict_)
	startRow = Enum.HeaderExcelAndKeys.START_ROW
	startColum = Enum.HeaderExcelAndKeys.START_COLUM

	wb = Workbook() 
	colorDict, colorDictNoneBorder = Util.definedColor()
	if listItems[1]['status'] == 1:
		print("Running  Item I001 - Caculate work time and filter all sheet of user by week")
		print("------------------------------------------------------------------------------")
		showDetail = listItems[1]['show detail']
		sheetName = wb.add_sheet('Weekly Resource')
		lsheader = Util.headerToPrintExcel(1, startDate, endDate, 'week')
		#colum, row
		getBy = Enum.HeaderExcelAndKeys.TOTAL_WEEK
		Controllers.printDictToExcel(sheetName, lsheader, userInfoDict, startRow, startColum, getBy, colorDict, colorDictNoneBorder, showDetail)
# 		
	if listItems[2]['status'] == 1:
		print("Running  Item I002 - Caculate work time and filter all sheet of user by month")
		print("------------------------------------------------------------------------------")
		showDetail = listItems[2]['show detail']
		sheetName = wb.add_sheet('Monthly Resource')
		lsheader = Util.headerToPrintExcel(1, startDate, endDate, 'month')
		#colum, row
		getBy = Enum.HeaderExcelAndKeys.TOTAL_MONTH
		Controllers.printDictToExcel(sheetName, lsheader, userInfoDict, startRow, startColum, getBy, colorDict, colorDictNoneBorder, showDetail)	
	
	if listItems[3]['status'] == 1:
		
		print("Running  Item I003 - Caculate work time and filter all user of sheet by week")
		print("------------------------------------------------------------------------------")
		sheetName = wb.add_sheet('Weekly Project')
		lsheader = Util.headerToPrintExcel(0, startDate, endDate, 'week')
		#colum, row
		getBy = Enum.HeaderExcelAndKeys.TOTAL_WEEK
		Controllers.printDictToExcel(sheetName, lsheader, sheetInfoDict, startRow, startColum, getBy, colorDict, colorDictNoneBorder, 1)
	
	if listItems[4]['status'] == 1:
		
		print("Running  Item I004 - Caculate work time and filter all user of sheet by month")
		print("------------------------------------------------------------------------------")
		sheetName = wb.add_sheet('Monthly Project')
		lsheader = Util.headerToPrintExcel(0, startDate, endDate, 'month')
		#colum, row
		getBy = Enum.HeaderExcelAndKeys.TOTAL_MONTH
		Controllers.printDictToExcel(sheetName, lsheader, sheetInfoDict, startRow, startColum, getBy, colorDict, colorDictNoneBorder, 1)
	
	try:
		wb.save('%s\TimeSheet.xls'%(dir_))
	except:
		print('Error to save TimeSheet.xls')
	print ('Finish-----------')

if __name__ == '__main__':
	Run__()

	
	
	
	
	