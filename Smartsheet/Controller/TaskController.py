import sys
from openpyxl.styles.builtins import total
sys.path.append('..')
import smartsheet
from simple_smartsheet import Smartsheet
from simple_smartsheet.models import Sheet, Column, Row, Cell
from Model.Rows import Row
from Enum import Enum
from Utils import Util
import datetime
from pprint import pprint

class RowParsing():
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

	def getAllSheetAndWorkTimeOfUser(listSheet, ListUser, startDate, endDate, userInfo, dictInfoUser, sheets_):

		UserInfoDict = {}
		sheetInfoDict = {}
		#add data into UserInfoDict
		for sheetName in listSheet:
			strlog = ''
			print('Parsing %s........' %(sheetName))
			print('------------------------------------------------------------------------------')
			dictRows = RowParsing.getAllDataOfSheet(sheetName, sheets_)
			listParentId = Row.getParentId(dictRows)
			for row in dictRows:
				user___ = dictRows[row]['info'][Enum.Header.ASSIGNED_TO].split(',')
				users = user___[0]
				#pick task is not a parent task
				if not (dictRows[row][Enum.GenSmartsheet.ID]  in listParentId):
					if dictRows[row]['info'][Enum.Header.ASSIGNED_TO] == 'NaN':
						strlog += 'Skip--AssignTo is empty in Sheet name: %s, Task name: %s, Line : %s \n' %(sheetName, dictRows[row]['info'][Enum.Header.TASK_NAME], dictRows[row]['info'][Enum.GenSmartsheet.LINE])
						continue
					else:
# 						
						startToEndDay = []

						if dictRows[row]['info'][Enum.Header.ALLOCATION] == 'NaN':
							strlog += 'Skip--Allocation is empty in Sheet name: %s, Task name: %s, Line : %s \n' %(sheetName, dictRows[row]['info'][Enum.Header.TASK_NAME], dictRows[row]['info'][Enum.GenSmartsheet.LINE]) 
							continue
						if (dictRows[row]['info'][Enum.Header.START_DATE] == 'NaN') or (dictRows[row]['info'][Enum.Header.END_DATE] == "NaN"):
							strlog += 'Skip--Start date or End date is empty in Sheet name: %s, Task name: %s, Line : %s \n' %(sheetName, dictRows[row]['info'][Enum.Header.TASK_NAME], dictRows[row]['info'][Enum.GenSmartsheet.LINE])
							continue
						else:
							syear, smonth, sday = Util.toDate(dictRows[row]['info'][Enum.Header.START_DATE])
							eyear, emonth, eday = Util.toDate(dictRows[row]['info'][Enum.Header.END_DATE])
							start_dt = datetime.date(syear, smonth, sday)
							end_dt = datetime.date(eyear, emonth, eday)
							listWorkDay1 = Util.getWorkDay(startDate, endDate)
							for date_ in Util.daterange(start_dt, end_dt):
								for wday in listWorkDay1:
									if wday[0] == str(date_):
										startToEndDay.append(str(date_))
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
							#get work day of 1 task, Mon to Fri
							for date2 in startToEndDay:
								listWorkDay = Util.getWorkDay(startDate, endDate)
								
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
			if len(strlog):
				logname = '%s_log.log' %(sheetName)
				print('Created  %s: skip row in %s' %(logname, sheetName))
				f = open(logname, "w")
				f.write(strlog)
				f.close()
# 		pprint(sheetInfoDict)
# 		asdasd
		return UserInfoDict, sheetInfoDict
	
	def caculateWorkTimeAndAddInfo(startDate, endDate, userInfoDict, sheetInfoDict):
# 		print('sssss')
		#caculate for UserDict
		listMonth = Util.getWorkMonth(startDate, endDate)
		listWeek = Util.getWorkWeek(startDate, endDate)
# 		pprint(userInfoDict)
		for team in userInfoDict:
			if team in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
				continue
			for user_ in userInfoDict[team]:
				if user_ in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
					continue
				for sheet__ in userInfoDict[team][user_]:
					if sheet__ in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
						continue
					totalMonthS = Util.caculateWorkMonthFromListWorkDay(listMonth, listWeek,  startDate, endDate, userInfoDict[team][user_][sheet__], Enum.WorkHourColor.BACK_GROUND, False)
					totalWeekS = Util.caculateWorkWeekFromListWorkDay(listWeek, startDate, endDate, userInfoDict[team][user_][sheet__], Enum.WorkHourColor.BACK_GROUND, False)
					userInfoDict[team][user_][sheet__][Enum.HeaderExcelAndKeys.TOTAL_MONTH] = totalMonthS
					userInfoDict[team][user_][sheet__][Enum.HeaderExcelAndKeys.TOTAL_WEEK] = totalWeekS
					
				totalWeekU, totalMonthU = Util.cacutlateTotal(listMonth, listWeek, userInfoDict[team][user_], Enum.WorkHourColor.BACK_GROUND, False)
				userInfoDict[team][user_][Enum.HeaderExcelAndKeys.TOTAL_MONTH] = totalMonthU
				userInfoDict[team][user_][Enum.HeaderExcelAndKeys.TOTAL_WEEK] = totalWeekU
# 			pprint(UserInfoDict)
# 			asdas
			totalWeekT, totalMonthT = Util.cacutlateTotal(listMonth, listWeek, userInfoDict[team], Enum.WorkHourColor.IS_POSITION, True)
			userInfoDict[team][Enum.HeaderExcelAndKeys.TOTAL_MONTH] = totalMonthT
			userInfoDict[team][Enum.HeaderExcelAndKeys.TOTAL_WEEK] = totalWeekT
		
		#caculate for SheetDict
		for sheet_ in sheetInfoDict:
			if sheet_ in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
				continue
			for team_ in sheetInfoDict[sheet_]:
				if team_ in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
					continue
				for user__ in sheetInfoDict[sheet_][team_]:
					if user__ in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
						continue
					totalMonthS = Util.caculateWorkMonthFromListWorkDay(listMonth, listWeek,  startDate, endDate, sheetInfoDict[sheet_][team_][user__], Enum.WorkHourColor.BACK_GROUND, True)
					totalWeekS = Util.caculateWorkWeekFromListWorkDay(listWeek, startDate, endDate, sheetInfoDict[sheet_][team_][user__], Enum.WorkHourColor.BACK_GROUND, True)
					sheetInfoDict[sheet_][team_][user__][Enum.HeaderExcelAndKeys.TOTAL_MONTH] = totalMonthS
					sheetInfoDict[sheet_][team_][user__][Enum.HeaderExcelAndKeys.TOTAL_WEEK] = totalWeekS
					
				totalWeekU, totalMonthU = Util.cacutlateTotal(listMonth, listWeek, sheetInfoDict[sheet_][team_], Enum.WorkHourColor.IS_POSITION, True)
				sheetInfoDict[sheet_][team_][Enum.HeaderExcelAndKeys.TOTAL_MONTH] = totalMonthU
				sheetInfoDict[sheet_][team_][Enum.HeaderExcelAndKeys.TOTAL_WEEK] = totalWeekU
# 			pprint(sheetInfoDict)
# 			asdas
			totalWeekT, totalMonthT = Util.cacutlateTotal(listMonth, listWeek, sheetInfoDict[sheet_], Enum.WorkHourColor.IS_SHEET_NAME, True)
			sheetInfoDict[sheet_][Enum.HeaderExcelAndKeys.TOTAL_MONTH] = totalMonthT
			sheetInfoDict[sheet_][Enum.HeaderExcelAndKeys.TOTAL_WEEK] = totalWeekT
# 		pprint(sheetInfoDict)
# 		asdas
		return userInfoDict, sheetInfoDict




	


class Controllers():

	def printDictToExcel(sheetName, lsheader, dictToPrint, startRow, startColum, getBy, colorDict, colorDictNoneBorder):
		rowIndex = startRow
		columIndex = startColum
		for head1 in lsheader:
			style1 = Util.selectColorToPrint(head1[1], colorDict, colorDictNoneBorder)
			if columIndex in [startColum, startColum + 1, startColum + 2]:
				sheetName.col(columIndex).width = 256 * 20
			else:
				sheetName.col(columIndex).width = 256 * 11
# 			header = ''
# 				y, m, d = Util.toDate(head1[0])
# 				header = '%s/%s' %(d, m)
# 			else:
# 				header = head1[0]
			sheetName.write(rowIndex, columIndex, head1[0], style1)
			columIndex += 1
		rowIndex += 1
		columIndex = 2
		for keyLV1 in dictToPrint.keys():
# 			print(position_, '++++++++++++++++++++++')
			if keyLV1 in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
				continue
			else:
# 				position = userInfoDict[position_]
				count1 = 0
				for head2 in lsheader:
					value1 = 0
					if count1 > 2:
						value1 = dictToPrint[keyLV1][getBy][head2[0]][0]
						st1 = dictToPrint[keyLV1][getBy][head2[0]][1]
					else:
						value1 = dictToPrint[keyLV1][head2[0]][0]
						st1 = dictToPrint[keyLV1][head2[0]][1]
					style2 = Util.selectColorToPrint(st1, colorDict, colorDictNoneBorder)
	# 				print(position[head2[0]])
# 					print( '========', value1)
					if columIndex in [startColum, startColum + 1, startColum + 2]:
						sheetName.col(columIndex).width = 256 * 20
					else:
						sheetName.col(columIndex).width = 256 * 11
					sheetName.write(rowIndex, columIndex, value1, style2)
					columIndex += 1
					count1 += 1
				rowIndex += 1
				columIndex = 2
# 			print(userInfoDict[position].keys())
# 			if keyLV1 in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
# 				continue
# 			else:
				for keyLV2 in dictToPrint[keyLV1].keys():
# 					print(keyLV2, '-----------------------')
					if keyLV2 in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
						continue
					else:
						user = dictToPrint[keyLV1][keyLV2]
						count2 = 0
						for head3 in lsheader:
							value2 = 0
							if count2 > 2:
								value2 = dictToPrint[keyLV1][keyLV2][getBy][head3[0]][0]
								st2 = dictToPrint[keyLV1][keyLV2][getBy][head3[0]][1]
							else:
		# 						print(userInfoDict[keyLV1])
# 								pprint(userInfoDict[keyLV1][keyLV2])
								value2 = dictToPrint[keyLV1][keyLV2][head3[0]][0]
								st2 = dictToPrint[keyLV1][keyLV2][head3[0]][1]
							style3 = Util.selectColorToPrint(st2, colorDict, colorDictNoneBorder)
# 							print( '=====================', value2)
							if columIndex in [startColum, startColum + 1, startColum + 2]:
								sheetName.col(columIndex).width = 256 * 20
							else:
								sheetName.col(columIndex).width = 256 * 11
							sheetName.write(rowIndex, columIndex, value2, style3)
							columIndex += 1
							count2 += 1
						rowIndex += 1
						columIndex = 2
# 					if keyLV2 in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.keyLV2NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
# 						continue
# 					else:
						for keyLV3 in dictToPrint[keyLV1][keyLV2].keys():
							if keyLV3 in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
								continue
							else:
# 							print(keyLV3, '==================')
# 								user_
# 								sheet = userInfoDict[keyLV1][user_][sheet]
								count3 = 0
								for head4 in lsheader:
									value3 = 0
									if count3 > 2:
										value3 = dictToPrint[keyLV1][keyLV2][keyLV3][getBy][head4[0]][0]
										st3 = dictToPrint[keyLV1][keyLV2][keyLV3][getBy][head4[0]][1]
									else:
# 										print(keyLV2, keyLV3, head4[0])
										value3 = dictToPrint[keyLV1][keyLV2][keyLV3][head4[0]][0]
										st3 = dictToPrint[keyLV1][keyLV2][keyLV3][head4[0]][1]
									style4 = Util.selectColorToPrint(st3, colorDict, colorDictNoneBorder)
# 									print( '========================================', value3)
									if columIndex in [startColum, startColum + 1, startColum + 2]:
										sheetName.col(columIndex).width = 256 * 20
									else:
										sheetName.col(columIndex).width = 256 * 11
									if (not value3) and st3 == Enum.WorkHourColor.BACK_GROUND:
										value3 = ''
									sheetName.write(rowIndex, columIndex, value3, style4)
									columIndex += 1
									count3 += 1
								rowIndex += 1
								columIndex = 2
								
								
# pprint(Controllers.getTaskAndTimeOfUserByMonth(['QA_FLOW'], ['toannguyen'], '2019-1-1', '2019-1-10'))
