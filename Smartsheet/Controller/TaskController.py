import sys
sys.path.append('..')
import smartsheet
from simple_smartsheet import Smartsheet
from simple_smartsheet.models import Sheet, Column, Row, Cell
from Model.Rows import Row
from Enum import Enum
from Utils import Util
import datetime
import time
from pprint import pprint
import xlwt
class RowParsing():
	def checkSheetConfigIsExist(listSheetConfig, Sheet):
		SheetEdit = {}
		listSheetConfigReplace = []
		TOKEN = Enum.GenSmartsheet.TOKEN
		smartsheet = Smartsheet(TOKEN)
		sheets = smartsheet.sheets.list()
		dictSheetSms = {}
		for sheetSmartsheet in sheets:
			dictSheetSms[sheetSmartsheet.name.lower()] = sheetSmartsheet.name
		strOut = ''
		listOut = []
# 		for sheetConfig in listSheetConfig:
# 			if not (sheetConfig in listSheetSms):
# 				listOut.append(sheetConfig)
# 		strOut = ', '.join(listOut)
		
		for index_ in range(0, len(listSheetConfig)):
			if not (listSheetConfig[index_].lower() in dictSheetSms.keys()):
# 				pprint (dictSheetSms.keys())
				listOut.append(listSheetConfig[index_])
			else:
				listSheetConfigReplace.append(dictSheetSms[listSheetConfig[index_].lower()])
				SheetEdit[dictSheetSms[listSheetConfig[index_].lower()]] = Sheet[listSheetConfig[index_]]
		strOut = ', '.join(listOut)
		
		
		return strOut, listSheetConfigReplace, SheetEdit
	
	def checkHeaderExistInSheet(sheetName, listHeader):

		TOKEN = Enum.GenSmartsheet.TOKEN
		smartsheet = Smartsheet(TOKEN)
		sheet = smartsheet.sheets.get(sheetName)
		sheetInfo = sheet.columns
# 		if sheetName == 'NRE_ECC_CPL':
# 			pprint (sheetInfo)
# 			asd
		# For each column, print Id and Title.
		lHeader = []
		lsHSheet = []
		for col in sheetInfo:
			lsHSheet.append(col[Enum.GenSmartsheet.TITLE])
			#remove % in header
			headerName_ = col[Enum.GenSmartsheet.TITLE].replace('%', '')
			headerName = headerName_.strip()
			lHeader.append(headerName)
		strOut = ''
		listOut = []
# 		print (lHeader, listHeader)
		print('Header of %s: %s' %(sheetName, ', '.join(lsHSheet)))
		for hConfig in listHeader:
			if not(hConfig in lHeader):
				listOut.append(hConfig)
		strOut = ', '.join(listOut)
		return strOut
		
	
	
	#connect to smartsheet
	def connectSmartsheet(sheet_name):
		TOKEN = Enum.GenSmartsheet.TOKEN
		smartsheet = Smartsheet(TOKEN)
		sheet = smartsheet.sheets.get(sheet_name)
		allRows = sheet.rows
		return allRows, sheet

	#convert row's data  to dictionary with key=id, value = {id: '', info: {}, parent_id: '',sibling_id: ''}
	def getAllDataOfSheet(sheet_name, sheets_):
		allRows, sheet = RowParsing.connectSmartsheet(sheet_name)
		dictRows = {}
		count = 1
		totalRow = len(allRows)
		for row in allRows:
			if ((count % 200) == 0 and count != 0):
				print ('%s: Parse lines %s of %s line' %(sheet_name, count, totalRow))
			if (Row.isRowEmpty(row) == 1):
				dictheader = sheets_[sheet_name]
				dictHeaderOut = Row.getHeaders(sheet_name, sheet, dictheader)
				dictRow= Row.getDataRow(row, dictHeaderOut, count)
				dictRows[row['id']] = dictRow
			count += 1
		return dictRows

	def getAllSheetAndWorkTimeOfUser(listSheet, ListUser, startDate, endDate, userInfo, dictInfoUser, sheets_, dir_, excelHoliday):

		UserInfoDict = {}
		sheetInfoDict = {}
		sheetInfoDict2 = {}
		#add data into UserInfoDict
		for sheetName in listSheet:
			strlog = ''
			time1_ = time.time()
			print('Start parsing %s........' %(sheetName))
			countSkipRow = 0
			countRowParent = 0
			dictRows = RowParsing.getAllDataOfSheet(sheetName, sheets_)
			listParentId = Row.getParentId(dictRows)
			for row in dictRows:
				user___ = dictRows[row]['info'][Enum.Header.ASSIGNED_TO].split(',')
				users = user___[0]
				#pick task is not a parent task
				if not (dictRows[row][Enum.GenSmartsheet.ID]  in listParentId):
					if dictRows[row]['info'][Enum.Header.ASSIGNED_TO] == 'NaN':
						strlog += 'Skip--AssignTo is empty in Sheet name: %s, Task name: %s, Line : %s \n' %(sheetName, dictRows[row]['info'][Enum.Header.TASK_NAME], dictRows[row]['info'][Enum.GenSmartsheet.LINE])
						countSkipRow += 1
						continue
					else:
						
						startToEndDay = []
						if dictRows[row]['info'][Enum.Header.ALLOCATION] == 'NaN':
							dictRows[row]['info'][Enum.Header.ALLOCATION] = 0
						if (dictRows[row]['info'][Enum.Header.START_DATE] == 'NaN') or (dictRows[row]['info'][Enum.Header.END_DATE] == "NaN"):
							strlog += 'Skip--Start date or End date is empty in Sheet name: %s, Task name: %s, Line : %s \n' %(sheetName, dictRows[row]['info'][Enum.Header.TASK_NAME], dictRows[row]['info'][Enum.GenSmartsheet.LINE])
							countSkipRow += 1
							continue
						else:
							syear, smonth, sday = Util.toDate(dictRows[row]['info'][Enum.Header.START_DATE])
							eyear, emonth, eday = Util.toDate(dictRows[row]['info'][Enum.Header.END_DATE])
							start_dt = datetime.date(syear, smonth, sday)
							end_dt = datetime.date(eyear, emonth, eday)
							listWorkDay1 = Util.getWorkDay(startDate, endDate, dir_, excelHoliday)
							for date_ in Util.daterange(start_dt, end_dt):
								for wday in listWorkDay1:
									if wday[0] == str(date_):
										startToEndDay.append(str(date_))
# 						print(startToEndDay, syear, smonth, sday, eyear, emonth, eday)
						if len(startToEndDay) == 0:
							continue
						else:
							position_ = ''
							user = ''
							if ((users not in userInfo.keys()) and (users not in dictInfoUser.keys())):
								position_ = 'N/A'
								user = users
							else:
								if users in dictInfoUser.keys():
									user = dictInfoUser[users]
								else:
									user = users
								position_ = '%s %s' %(userInfo[user][Enum.UserInfoConfig.SENIORITY_LEVEL], userInfo[user][Enum.UserInfoConfig.POSITION])
							task_name = dictRows[row]['info'][Enum.Header.TASK_NAME]
							#create empty dict for user key = position
							if not (position_ in UserInfoDict.keys()):
								UserInfoDict[position_] = {}
								Util.createDict(UserInfoDict[position_], '', '', position_, Enum.WorkHourColor.IS_POSITION, Enum.WorkHourColor.IS_POSITION, Enum.WorkHourColor.IS_POSITION)
							#create empty dict for position key = username
							if not(user in UserInfoDict[position_].keys()):
								UserInfoDict[position_][user] = {}
								Util.createDict(UserInfoDict[position_][user], '', user, '', Enum.WorkHourColor.IS_USER_NAME, Enum.WorkHourColor.IS_USER_NAME, Enum.WorkHourColor.BACK_GROUND)
							#create empty dict for user key = position	
							if not (sheetName in UserInfoDict[position_][user].keys()):
								UserInfoDict[position_][user][sheetName] = {}
								Util.createDict(UserInfoDict[position_][user][sheetName], sheetName, '', '', Enum.WorkHourColor.IS_SHEET_NAME, Enum.WorkHourColor.BACK_GROUND, Enum.WorkHourColor.BACK_GROUND)
							#create empty dict for user key = position
							if not(sheetName  in sheetInfoDict.keys()):
								sheetInfoDict[sheetName] = {}
								Util.createDict(sheetInfoDict[sheetName], sheetName, '', '', Enum.WorkHourColor.IS_SHEET_NAME, Enum.WorkHourColor.IS_SHEET_NAME, Enum.WorkHourColor.IS_SHEET_NAME)
							#create empty dict for user key = position
							if not (position_ in sheetInfoDict[sheetName].keys()):
								sheetInfoDict[sheetName][position_] = {}
								Util.createDict(sheetInfoDict[sheetName][position_], '', '', position_, Enum.WorkHourColor.BACK_GROUND, Enum.WorkHourColor.IS_POSITION, Enum.WorkHourColor.IS_POSITION)
							#create empty dict for position key = username
							if not(user in sheetInfoDict[sheetName][position_].keys()):
								sheetInfoDict[sheetName][position_][user] = {}
								Util.createDict(sheetInfoDict[sheetName][position_][user], '', user, '', Enum.WorkHourColor.BACK_GROUND, Enum.WorkHourColor.IS_USER_NAME, Enum.WorkHourColor.BACK_GROUND)
							#create empty dict for user key = position
							if not(sheetName  in sheetInfoDict2.keys()):
								sheetInfoDict2[sheetName] = {}
 							
							#create empty dict for user key = position
							if not (position_ in sheetInfoDict2[sheetName].keys()):
								sheetInfoDict2[sheetName][position_] = {}
 								
							#create empty dict for position key = username
							if not(user in sheetInfoDict2[sheetName][position_].keys()):
								sheetInfoDict2[sheetName][position_][user] = {}
							if task_name in sheetInfoDict2[sheetName][position_][user].keys():
								while True:
									i = 1
									task_name =  task_name +'(' + str(i) + ')'
									if not(task_name in sheetInfoDict2[sheetName][position_][user].keys()):
										break
									else:
										i = i + 1	
							
							
							
# 							print(sheetInfoDict2[sheetName][position_][user][task_name]['week'].keys(), sheetInfoDict2[sheetName][position_][user][task_name]['month'].keys(), task_name, user, listWorkWeekOfTask, dictRows[row]['info'][Enum.Header.START_DATE], dictRows[row]['info'][Enum.Header.END_DATE])
							#get work day of 1 task, Mon to Fri
							for date2 in startToEndDay:
								listWorkDay = Util.getWorkDay(startDate, endDate, dir_, excelHoliday)
								listWorkMonth = Util.getWorkMonth(startDate, endDate, dir_, excelHoliday)
								for weeks in listWorkDay:
									if not (weeks[1] in UserInfoDict[position_][user][sheetName].keys()):
										UserInfoDict[position_][user][sheetName][weeks[1]] = []


										for days in listWorkDay:
											if days[1] == weeks[1]:
												info = [days[0], 0]
												UserInfoDict[position_][user][sheetName][days[1]].append(info)												
									if not (weeks[1] in sheetInfoDict[sheetName][position_][user].keys()):

										sheetInfoDict[sheetName][position_][user][weeks[1]] = []
										for days2 in listWorkDay:
											if days2[1] == weeks[1]:
												info2 = [days2[0], 0]
												sheetInfoDict[sheetName][position_][user][days2[1]].append(info2)
		
								for week in UserInfoDict[position_][user][sheetName]:
									if week in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
										continue
									else:
										for dayOfWeek in UserInfoDict[position_][user][sheetName][week]:
											if str(date2) == dayOfWeek[0]:
	 
												allocaton = float(dictRows[row]['info'][Enum.Header.ALLOCATION])
	 
												dayOfWeek[1] += allocaton*8
																					
								for week2 in sheetInfoDict[sheetName][position_][user]:
									if week2 in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
										continue
									else:
										for dayOfWeek2 in sheetInfoDict[sheetName][position_][user][week2]:
											if str(date2) == dayOfWeek2[0]:
												allocaton2 = float(dictRows[row]['info'][Enum.Header.ALLOCATION])
												dayOfWeek2[1] += allocaton2*8
								
								if not ( task_name in sheetInfoDict2[sheetName][position_][user].keys()):
									sheetInfoDict2[sheetName][position_][user][task_name] = {}
# 									pprint(sheetInfoDict2)
									sheetInfoDict2[sheetName][position_][user][task_name][Enum.Header.START_DATE] = '%s-%s-%s'%(Util.toDate(dictRows[row]['info'][Enum.Header.START_DATE]))
									sheetInfoDict2[sheetName][position_][user][task_name][Enum.Header.END_DATE] = '%s-%s-%s'%(Util.toDate(dictRows[row]['info'][Enum.Header.END_DATE]))
									sheetInfoDict2[sheetName][position_][user][task_name]['week'] = {}
									sheetInfoDict2[sheetName][position_][user][task_name]['allocation'] = str(int(float(dictRows[row]['info'][Enum.Header.ALLOCATION])*100)) + '%'
									sheetInfoDict2[sheetName][position_][user][task_name]['month'] = {}
								for wday in listWorkDay:
									if wday[0] == date2:
										if not (wday[1] in sheetInfoDict2[sheetName][position_][user][task_name]['week'].keys()):
											sheetInfoDict2[sheetName][position_][user][task_name]['week'][wday[1]] = {}
											sheetInfoDict2[sheetName][position_][user][task_name]['week'][wday[1]]['totalHour'] = 0
											sheetInfoDict2[sheetName][position_][user][task_name]['week'][wday[1]]['startWeek'] = wday[1]
											sheetInfoDict2[sheetName][position_][user][task_name]['week'][wday[1]]['endWeek'] = Util.get_end_start_week(wday[0])[0]
											sheetInfoDict2[sheetName][position_][user][task_name]['week'][wday[1]]['workWeek'] = Util.get_week_number(wday[0])
											sheetInfoDict2[sheetName][position_][user][task_name]['week'][wday[1]]['workHour'] = [0,'']
										week___ = Util.get_end_start_week(date2)[1]
										sheetInfoDict2[sheetName][position_][user][task_name]['week'][week___]['workHour'][0] += 8*float(dictRows[row]['info'][Enum.Header.ALLOCATION])
										sheetInfoDict2[sheetName][position_][user][task_name]['week'][week___]['totalHour'] += 8
										currentHour = sheetInfoDict2[sheetName][position_][user][task_name]['week'][week___]['workHour'][0]
										totalHour = sheetInfoDict2[sheetName][position_][user][task_name]['week'][week___]['totalHour']
										sheetInfoDict2[sheetName][position_][user][task_name]['week'][week___]['workHour'][1] = Util.CompareAndSelectColorToPrintExcel(currentHour, totalHour)[0]
 																									
								for wmonth in listWorkMonth:
									y_, m_, d_ = Util.toDate(date2)
									m_ = '%s/%s'%(m_, y_)
									m = '%s/%s'%(wmonth[0], wmonth[1])
									if (m == m_):
										if not (m in sheetInfoDict2[sheetName][position_][user][task_name]['month'].keys()):
											sheetInfoDict2[sheetName][position_][user][task_name]['month'][m] = {}
											sheetInfoDict2[sheetName][position_][user][task_name]['month'][m]['totalHour'] = 0
 			
											sheetInfoDict2[sheetName][position_][user][task_name]['month'][m]['startMonth'] = Util.get_end_start_month('%s-%s'%(wmonth[1], wmonth[0]))[0]
											sheetInfoDict2[sheetName][position_][user][task_name]['month'][m]['endMonth'] = Util.get_end_start_month('%s-%s'%(wmonth[1], wmonth[0]))[1]
			# 									sheetInfoDict2[sheetName][position_][user][task_name]['month'][monthTask[0]]['workMonth'] = {}
											sheetInfoDict2[sheetName][position_][user][task_name]['month'][m]['workHour'] = [0, '']
 									
 										
										sheetInfoDict2[sheetName][position_][user][task_name]['month'][m_]['workHour'][0] += 8*float(dictRows[row]['info'][Enum.Header.ALLOCATION])
										sheetInfoDict2[sheetName][position_][user][task_name]['month'][m_]['totalHour'] += 8
										currentHour2 = sheetInfoDict2[sheetName][position_][user][task_name]['month'][m_]['workHour'][0]
										totalHour2 = sheetInfoDict2[sheetName][position_][user][task_name]['month'][m_]['totalHour']
										sheetInfoDict2[sheetName][position_][user][task_name]['month'][m_]['workHour'][1] = Util.CompareAndSelectColorToPrintExcel(currentHour2, totalHour2)[0]
				else:
					countRowParent += 1
			print('Skip (not save into log) %s parent task in %s' %(countRowParent, sheetName))
			if len(strlog):
				logname = '%s\Log\%s.log' %(dir_, sheetName)
				print('Skip %s row in %s' %(countSkipRow, sheetName))
				print('Created  %s: skip row in %s' %(logname, sheetName))
				f = open(logname, "w")
				f.write(strlog)
				f.close()
			time2_ = time.time()
			print('Parsing %s done: %s' %(sheetName, Util.getTimeRun(time1_, time2_)))
			print('------------------------------------------------------------------------------')
		return UserInfoDict, sheetInfoDict, sheetInfoDict2
	
	def caculateWorkTimeAndAddInfo(startDate, endDate, userInfoDict, sheetInfoDict, dir_, excelHoliday):

		listMonth = Util.getWorkMonth(startDate, endDate, dir_, excelHoliday)
		listWeek = Util.getWorkWeek(startDate, endDate, dir_, excelHoliday)
		for team in userInfoDict:
			if team in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
				continue
			for user_ in userInfoDict[team]:
				if user_ in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
					continue
				for sheet__ in userInfoDict[team][user_]:
					if sheet__ in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
						continue
					totalMonthS = Util.caculateWorkMonthFromListWorkDay(listMonth, listWeek,  startDate, endDate, userInfoDict[team][user_][sheet__], Enum.WorkHourColor.BACK_GROUND, False, 'unlimit')
					totalWeekS = Util.caculateWorkWeekFromListWorkDay(listWeek, startDate, endDate, userInfoDict[team][user_][sheet__], Enum.WorkHourColor.BACK_GROUND, False, 'unlimit')
					userInfoDict[team][user_][sheet__][Enum.HeaderExcelAndKeys.TOTAL_MONTH] = totalMonthS
					userInfoDict[team][user_][sheet__][Enum.HeaderExcelAndKeys.TOTAL_WEEK] = totalWeekS
					
				totalWeekU, totalMonthU = Util.cacutlateTotal(listMonth, listWeek, userInfoDict[team][user_], Enum.WorkHourColor.BACK_GROUND, False, 'limit')
				userInfoDict[team][user_][Enum.HeaderExcelAndKeys.TOTAL_MONTH] = totalMonthU
				userInfoDict[team][user_][Enum.HeaderExcelAndKeys.TOTAL_WEEK] = totalWeekU

			totalWeekT, totalMonthT = Util.cacutlateTotal(listMonth, listWeek, userInfoDict[team], Enum.WorkHourColor.IS_POSITION, True, 'unlimit')
			userInfoDict[team][Enum.HeaderExcelAndKeys.TOTAL_MONTH] = totalMonthT
			userInfoDict[team][Enum.HeaderExcelAndKeys.TOTAL_WEEK] = totalWeekT
		

		for sheet_ in sheetInfoDict:
			if sheet_ in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
				continue
			for team_ in sheetInfoDict[sheet_]:
				if team_ in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
					continue
				for user__ in sheetInfoDict[sheet_][team_]:
					if user__ in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
						continue
					totalMonthS = Util.caculateWorkMonthFromListWorkDay(listMonth, listWeek,  startDate, endDate, sheetInfoDict[sheet_][team_][user__], Enum.WorkHourColor.BACK_GROUND, True, 'limit')
					totalWeekS = Util.caculateWorkWeekFromListWorkDay(listWeek, startDate, endDate, sheetInfoDict[sheet_][team_][user__], Enum.WorkHourColor.BACK_GROUND, True, 'limit')
					sheetInfoDict[sheet_][team_][user__][Enum.HeaderExcelAndKeys.TOTAL_MONTH] = totalMonthS
					sheetInfoDict[sheet_][team_][user__][Enum.HeaderExcelAndKeys.TOTAL_WEEK] = totalWeekS
					
				totalWeekU, totalMonthU = Util.cacutlateTotal(listMonth, listWeek, sheetInfoDict[sheet_][team_], Enum.WorkHourColor.IS_POSITION, True, 'unlimit')
				sheetInfoDict[sheet_][team_][Enum.HeaderExcelAndKeys.TOTAL_MONTH] = totalMonthU
				sheetInfoDict[sheet_][team_][Enum.HeaderExcelAndKeys.TOTAL_WEEK] = totalWeekU

			totalWeekT, totalMonthT = Util.cacutlateTotal(listMonth, listWeek, sheetInfoDict[sheet_], Enum.WorkHourColor.IS_SHEET_NAME, True, 'unlimit')
			sheetInfoDict[sheet_][Enum.HeaderExcelAndKeys.TOTAL_MONTH] = totalMonthT
			sheetInfoDict[sheet_][Enum.HeaderExcelAndKeys.TOTAL_WEEK] = totalWeekT

		return userInfoDict, sheetInfoDict




	


class Controllers():

	def printDictToExcel(sheetName, lsheader, dictToPrint, startRow, startColum, getBy, colorDict, colorDictNoneBorder, showDetail):
		rowIndex = startRow
		columIndex = startColum
		for head1 in lsheader:
			if (showDetail == 0) and (head1[0] == Enum.HeaderExcelAndKeys.SHEET_NAME):
				continue
			else:
				style1 = Util.selectColorToPrint(head1[1], colorDict, colorDictNoneBorder)
				lsLongHeader = []
				if showDetail:
					lsLongHeader = [startColum, startColum + 1, startColum + 2]
				else:
					lsLongHeader = [startColum, startColum + 1]
				if columIndex in lsLongHeader:
					sheetName.col(columIndex).width = 256 * 25
				else:
					sheetName.col(columIndex).width = 256 * 11
				sheetName.write(rowIndex, columIndex, head1[0], style1)
				columIndex += 1
		rowIndex += 1
		columIndex = 2
		for keyLV1 in dictToPrint.keys():

			if keyLV1 in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
				continue
			else:

				count1 = 0
				for head2 in lsheader:
					if (showDetail == 0) and (head2[0] == Enum.HeaderExcelAndKeys.SHEET_NAME):
						count1 += 1
						continue
					else:
						value1 = 0
						if count1 > 2:
							value1 = dictToPrint[keyLV1][getBy][head2[0]][0]
							st1 = dictToPrint[keyLV1][getBy][head2[0]][1]
						else:
							value1 = dictToPrint[keyLV1][head2[0]][0]
							st1 = dictToPrint[keyLV1][head2[0]][1]
						style2 = Util.selectColorToPrint(st1, colorDict, colorDictNoneBorder)

						sheetName.write(rowIndex, columIndex, value1, style2)
						columIndex += 1
						count1 += 1
				rowIndex += 1
				columIndex = 2

				for keyLV2 in dictToPrint[keyLV1].keys():

					if keyLV2 in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
						continue
					else:

						count2 = 0
						for head3 in lsheader:
							if (showDetail == 0) and (head3[0] == Enum.HeaderExcelAndKeys.SHEET_NAME):
								count2 += 1
								continue
							else:
								value2 = 0
								if count2 > 2:
									value2 = dictToPrint[keyLV1][keyLV2][getBy][head3[0]][0]
									st2 = dictToPrint[keyLV1][keyLV2][getBy][head3[0]][1]
								else:

									value2 = dictToPrint[keyLV1][keyLV2][head3[0]][0]
									st2 = dictToPrint[keyLV1][keyLV2][head3[0]][1]
								style3 = Util.selectColorToPrint(st2, colorDict, colorDictNoneBorder)
								sheetName.write(rowIndex, columIndex, value2, style3)
								columIndex += 1
								count2 += 1
						rowIndex += 1
						columIndex = 2

						if not showDetail:
							continue
						else:
							for keyLV3 in dictToPrint[keyLV1][keyLV2].keys():
								if keyLV3 in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
									continue
								else:

									count3 = 0
									for head4 in lsheader:
										value3 = 0
										if count3 > 2:
											value3 = dictToPrint[keyLV1][keyLV2][keyLV3][getBy][head4[0]][0]
											st3 = dictToPrint[keyLV1][keyLV2][keyLV3][getBy][head4[0]][1]
										else:

											value3 = dictToPrint[keyLV1][keyLV2][keyLV3][head4[0]][0]
											st3 = dictToPrint[keyLV1][keyLV2][keyLV3][head4[0]][1]
										style4 = Util.selectColorToPrint(st3, colorDict, colorDictNoneBorder)

										if (not value3) and st3 == Enum.WorkHourColor.BACK_GROUND:
											value3 = ''
										sheetName.write(rowIndex, columIndex, value3, style4)
										columIndex += 1
										count3 += 1
									rowIndex += 1
									columIndex = 2
	def printToExcelMonthlyOrWeeklyTimesheet(sheetName, lsheader, sheetInfoDict2_, startRow, startColum, monthOrWeek):
		startRow, startColum = (0, 0)
		rowIndex = startRow
		columIndex = startColum
		formatHead = 'align: wrap 0; pattern: pattern solid, fore-colour grey25; border: left thin, top thin, right thin, bottom thin, bottom-color gray25, top-color gray25, left-color gray25, right-color gray25; font: name Calibri, bold 0,height 240;' 
		styleHeader = xlwt.easyxf(formatHead)
		for head1 in lsheader:
# 			sheetName.col(columIndex).width = 256 * 20
			if columIndex == 6:
				sheetName.col(columIndex).width = 256 * 30
			elif columIndex == 5:
				sheetName.col(columIndex).width = 256 * 20
			elif columIndex == 0:
				sheetName.col(columIndex).width = 256 * 14
			elif columIndex == 7:
				sheetName.col(columIndex).width = 256 * 15
			elif columIndex == 8:
				sheetName.col(columIndex).width = 256 * 12
			elif columIndex == 9:
				sheetName.col(columIndex).width = 256 * 14
			elif columIndex == 10:
				sheetName.col(columIndex).width = 256 * 14
			elif columIndex == 11:
				sheetName.col(columIndex).width = 256 * 7
			else:
				sheetName.col(columIndex).width = 256 * 14
# 			sheetName.row(rowIndex).height_mismatch = True
# 			sheetName.row(rowIndex).height = 256*1
			sheetName.write(rowIndex, columIndex, head1, styleHeader)
			columIndex += 1
		rowIndex += 1
		columIndex = startColum
		sw = True
		styleCell = ''
		styleCell_, styleCell__ = Util.style_for_timesheet()
		for sheet_ in sheetInfoDict2_.keys():
			for position_ in sheetInfoDict2_[sheet_].keys():
				for user_ in sheetInfoDict2_[sheet_][position_].keys():
					for task_ in sheetInfoDict2_[sheet_][position_][user_].keys():
											
						if sw:
							sw = False
							styleCell = styleCell_
						else:
							sw = True
							styleCell = styleCell__
						if monthOrWeek == 'month':
							for month_ in sheetInfoDict2_[sheet_][position_][user_][task_]['month'].keys():
								
								startDate_ = sheetInfoDict2_[sheet_][position_][user_][task_]['StartDate']
								sheetName.write(rowIndex, columIndex + 3, startDate_, styleCell)
								endDate_ = sheetInfoDict2_[sheet_][position_][user_][task_]['EndDate']
								sheetName.write(rowIndex, columIndex + 4, endDate_, styleCell)
								sheetName.write(rowIndex, columIndex + 5, sheet_, styleCell)
								sheetName.write(rowIndex, columIndex, position_, styleCell)
								sheetName.write(rowIndex, columIndex + 7, user_, styleCell)
# 								cwidth = sheetName.col(6).width
# 								if (len(task_)*367) > cwidth:  
# 									sheetName.col(6).width = (len(task_)*367)
								sheetName.write(rowIndex, columIndex + 6, task_, styleCell)
								allocation_ = sheetInfoDict2_[sheet_][position_][user_][task_]['allocation']
								sheetName.write(rowIndex, columIndex + 8, allocation_, styleCell)
								startMonth_ = sheetInfoDict2_[sheet_][position_][user_][task_]['month'][month_]['startMonth']
								sheetName.write(rowIndex, columIndex + 1, startMonth_, styleCell)
								endMonth_ = sheetInfoDict2_[sheet_][position_][user_][task_]['month'][month_]['endMonth']
								sheetName.write(rowIndex, columIndex + 2, endMonth_, styleCell)
								workHour_ = sheetInfoDict2_[sheet_][position_][user_][task_]['month'][month_]['workHour'][0]
								sheetName.write(rowIndex, columIndex + 9, workHour_, styleCell)
								totalhour_ = sheetInfoDict2_[sheet_][position_][user_][task_]['month'][month_]['totalHour']
								sheetName.write(rowIndex, columIndex + 10, totalhour_, styleCell)
								rowIndex += 1
								
								
						else:
							for week_ in sheetInfoDict2_[sheet_][position_][user_][task_]['week'].keys():
								startDate_ = sheetInfoDict2_[sheet_][position_][user_][task_]['StartDate']
								sheetName.write(rowIndex, columIndex + 3, startDate_, styleCell)
								endDate_ = sheetInfoDict2_[sheet_][position_][user_][task_]['EndDate']
								sheetName.write(rowIndex, columIndex + 4, endDate_, styleCell)
								sheetName.write(rowIndex, columIndex + 5, sheet_, styleCell)
								sheetName.write(rowIndex, columIndex, position_, styleCell)
								sheetName.write(rowIndex, columIndex + 7, user_, styleCell)
								sheetName.write(rowIndex, columIndex + 6, task_, styleCell)
								allocation_ = sheetInfoDict2_[sheet_][position_][user_][task_]['allocation']
								sheetName.write(rowIndex, columIndex + 8, allocation_, styleCell)
								startWeek_ = sheetInfoDict2_[sheet_][position_][user_][task_]['week'][week_]['startWeek']
								sheetName.write(rowIndex, columIndex + 1, startWeek_, styleCell)
								endWeek_ = sheetInfoDict2_[sheet_][position_][user_][task_]['week'][week_]['endWeek']
								sheetName.write(rowIndex, columIndex + 2, endWeek_, styleCell)
								workHour_ = sheetInfoDict2_[sheet_][position_][user_][task_]['week'][week_]['workHour'][0]
								sheetName.write(rowIndex, columIndex + 9, workHour_, styleCell)
								totalhour_ = sheetInfoDict2_[sheet_][position_][user_][task_]['week'][week_]['totalHour']
								sheetName.write(rowIndex, columIndex + 10, totalhour_, styleCell)
								workWeek_ = sheetInfoDict2_[sheet_][position_][user_][task_]['week'][week_]['workWeek']
								sheetName.write(rowIndex, columIndex + 11, workWeek_, styleCell)
								rowIndex += 1
