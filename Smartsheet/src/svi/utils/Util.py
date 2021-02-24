import calendar, os
import datetime
import xlwt
import time
import pandas
# import numpy as np
# import pandas
import sys
sys.path.append('..')
from svi.enum import Enum
from pprint import pprint
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from email.mime.text import MIMEText
from email.mime.multipart  import MIMEMultipart
import socket
import getpass

from subprocess import Popen, PIPE, CalledProcessError, STDOUT, check_call

def toDate(strg_):
    strg = str(strg_)

    try:
        objDate = datetime.datetime.strptime(strg, '%Y-%m-%d')
    except:
        try:
            objDate = datetime.datetime.strptime(strg, '%Y-%m-%dT%H:%M:%S')
        except:
            try:
                objDate = datetime.datetime.strptime(strg, '%Y-%m-%d %H:%M:%S')
            except:
                try:
                    objDate = datetime.datetime.strptime(strg, '%m/%d/%Y')
                except:
                    print("Other Date time format: %s"%strg)
                    sys.exit()
    year = objDate.year
    month = objDate.month
    day = objDate.day
    return year, month, day
def check_valid_send_email_date(startDate, endDate, list_date):
    
    sy, sm, sd = toDate(startDate)
    ey, em, ed = toDate(endDate)
    for date_ in list_date:
        dy, dm, dd = toDate(date_.strip())
        start = datetime.datetime(day = sd, month = sm, year = sy)
        end = datetime.datetime(day = ed, month = em, year = ey)
        copare = datetime.datetime(day = dd, month = dm ,year = dy)
        if start <= copare <= end:
            pass
        else:
            print ("[ERROR] %s out of range (%s - %s)"%(date_.strip(), startDate, endDate))
            sys.exit()
    
def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + datetime.timedelta(n)
      
#[[day, week], ...]  
def getWorkDay(fromdate, todate, dir_, excelHoliday):
    sy, sm, sd = toDate(fromdate)
    ey, em, ed = toDate(todate)
    listWorkDay = []
    start_date = datetime.date(sy, sm, sd)
    end_date = datetime.date(ey, em, ed)
    for date in daterange(start_date, end_date):
        y, m, d = toDate(date.strftime("%Y-%m-%d"))
        y_m_d = '%s-%s-%s'%(y, m, d)
        startWeek = None
        if calendar.day_name[calendar.weekday(y,m,d)] == Enum.DateTime.START_WEEK:
            startWeek = datetime.date(y, m, d)
        else:
            day = datetime.date(y, m, d)
#             days = np.busday_count(start, end)
            startWeek = day - datetime.timedelta(days=day.weekday())
 
        if (calendar.day_name[calendar.weekday(y,m,d)] in Enum.DateTime.LIST_WORK_DAY_OF_WEEK) and (not (y_m_d in excelHoliday)):
            info = [str(datetime.date(y,m,d)), str(startWeek)]
            listWorkDay.append(info)
        elif len(listWorkDay) == 0:
            info = [str(datetime.date(y,m,d)), str(startWeek)]
            listWorkDay.append(info)
    return listWorkDay

#[[week, total hour work], ...]
def getWorkWeek(fromdate, todate, dir_, excelHoliday):
    sy, sm, sd = toDate(fromdate)
    ey, em, ed = toDate(todate)
    listWeek = []
    start_date = datetime.date(sy, sm, sd)
    end_date = datetime.date(ey, em, ed)
    for date in daterange(start_date, end_date):
        y, m, d = toDate(date.strftime("%Y-%m-%d"))
        y_m_d = '%s-%s-%s'%(y, m, d)
        startWeek = None
        if (calendar.day_name[calendar.weekday(y,m,d)] != Enum.DateTime.START_WEEK) and (listWeek == []):
            day = datetime.date(y, m, d)
#             days = np.busday_count(start, end)
            startWeek = day - datetime.timedelta(days=day.weekday())
            listWeekHourTotal = [str(startWeek), 0]
            listWeek.append(listWeekHourTotal)
        if (calendar.day_name[calendar.weekday(y,m,d)] == Enum.DateTime.START_WEEK):
            startWeek = datetime.date(y, m, d)
            listWeekHourTotal = [str(startWeek), 0]
            listWeek.append(listWeekHourTotal)
        if (calendar.day_name[calendar.weekday(y,m,d)] in Enum.DateTime.LIST_WORK_DAY_OF_WEEK)  and (not (y_m_d in excelHoliday)):
            listWeek[-1][1] += 8
    for emptyW in listWeek:
        if not (emptyW[1]):
            listWeek.remove(emptyW)
    return listWeek

#[week, ...]
def getWorkWeek2(fromdate, todate, dir_, excelHoliday):
    sy, sm, sd = toDate(fromdate)
    ey, em, ed = toDate(todate)
    listWeek = []
    start_date = datetime.date(sy, sm, sd)
    end_date = datetime.date(ey, em, ed)
    for date in daterange(start_date, end_date):
        y, m, d = toDate(date.strftime("%Y-%m-%d"))
        y_m_d = '%s-%s-%s'%(y, m, d)
        startWeek = None
        if (calendar.day_name[calendar.weekday(y,m,d)] != Enum.DateTime.START_WEEK) and (listWeek == []):
            day = datetime.date(y, m, d)
#             days = np.busday_count(start, end)
            startWeek = day - datetime.timedelta(days=day.weekday())
        if (calendar.day_name[calendar.weekday(y,m,d)] == Enum.DateTime.START_WEEK):
            startWeek = datetime.date(y, m, d)
            
        if startWeek not in listWeek and startWeek:
            listWeek.append(str(startWeek))
        
    
    return listWeek

# # [[momth, year, total hour work],...]
def getWorkMonth(fromdate, todate, dir_, excelHoliday):

    sy, sm, sd = toDate(fromdate)
    ey, em, ed = toDate(todate)
    listMonth = []
    startDate = datetime.date(sy, sm, sd)
    endDate = datetime.date(ey, em, ed)
    total = 0
    for dt in daterange(startDate, endDate):
        
        y, m, d = toDate(dt.strftime("%Y-%m-%d"))
        y_m_d = '%s-%s-%s'%(y, m, d)
        month = [m, y]
        if len(listMonth) == 0:
            month = [m, y]
            listMonth.append(month)
            if (calendar.day_name[calendar.weekday(y,m,d)] in Enum.DateTime.LIST_WORK_DAY_OF_WEEK)  and (not (y_m_d in excelHoliday)):
                total += 8
        else:
            if not (month in listMonth):
                listMonth.append(month)
                listMonth[-2].append(total)
                total = 0
                if (calendar.day_name[calendar.weekday(y,m,d)] in Enum.DateTime.LIST_WORK_DAY_OF_WEEK)  and (not (y_m_d in excelHoliday)):
                    total += 8
            else:
                if (calendar.day_name[calendar.weekday(y,m,d)] in Enum.DateTime.LIST_WORK_DAY_OF_WEEK)  and (not (y_m_d in excelHoliday)):
                    total += 8
    listMonth[-1].append(total)

    return listMonth
        
def getUserOfString(string):
    strings = string.lower()
    listUser = strings.split(',')
    firstUser = listUser[0].strip()
    name = ''

    if '@' in firstUser:
        index = firstUser.find('@')
        name = firstUser[0:index]
        
    else:
        firstUser = firstUser.split()
        s = ''.join(firstUser)
        name = s
    return name

def CompareAndSelectColorToPrintExcel(currentHour_, totalHour, offHour):
    color = ''
    currentHour = currentHour_ + offHour
    if currentHour > totalHour:
        color = Enum.WorkHourColor.IS_GREATER
        return color, totalHour
    elif currentHour < totalHour:
        color = Enum.WorkHourColor.IS_LESS
        return color, currentHour
    else:
        color = Enum.WorkHourColor.IS_EQUAL
        return color, currentHour

def CompareAndSelectColorToPrintExcel2(currentHour_, totalHour, offHour, isSheet):
    color = ''
    currentHour = currentHour_ + offHour
    if isSheet:
        out = currentHour_
    else:
        out = currentHour
    if out > totalHour:
        color = Enum.WorkHourColor.IS_GREATER
        return color, totalHour
    elif out < totalHour:
        color = Enum.WorkHourColor.IS_LESS
        return color, out
    else:
        color = Enum.WorkHourColor.IS_EQUAL
        return color, out
    
def definedColor():
    colorDict = {}
    colorDictNoneBorder = {}
    listColor = [Enum.WorkHourColor.IS_EQUAL, Enum.WorkHourColor.IS_GREATER, Enum.WorkHourColor.IS_LESS, Enum.WorkHourColor.IS_HEADER,
                Enum.WorkHourColor.IS_USER_NAME, Enum.WorkHourColor.IS_SHEET_NAME, Enum.WorkHourColor.BACK_GROUND, Enum.WorkHourColor.IS_POSITION]
    for color in listColor:
        formatCommand = 'align: wrap 0;pattern: pattern solid, fore-colour %s; border: left thin, top thin, right thin, bottom thin, bottom-color gray25, top-color gray25, left-color gray25, right-color gray25; font: name Calibri, bold 0,height 240;' %(color)
        style = xlwt.easyxf(formatCommand)
        colorDict[color] = style
    for color in listColor:
        formatCommand = 'align: wrap 0;pattern: pattern solid, fore-colour %s; font: name Calibri, bold 0,height 240;' %(color)
        style = xlwt.easyxf(formatCommand)
        colorDictNoneBorder[color] = style
    return colorDict, colorDictNoneBorder

def selectColorToPrint(color, colorDict, colorDictNoneBorder):
    if color in [Enum.WorkHourColor.BACK_GROUND, Enum.WorkHourColor.IS_SHEET_NAME, Enum.WorkHourColor.IS_HEADER]:
        return(colorDict[color])
    else:
        return(colorDictNoneBorder[color])
def definedColorText():
    colorDict = {}
    colorDictNoneBorder = {}
    listColor = [Enum.WorkHourColor.IS_EQUAL, Enum.WorkHourColor.IS_GREATER, Enum.WorkHourColor.IS_LESS, Enum.WorkHourColor.IS_HEADER,
                Enum.WorkHourColor.IS_USER_NAME, Enum.WorkHourColor.IS_SHEET_NAME, Enum.WorkHourColor.BACK_GROUND, Enum.WorkHourColor.IS_POSITION]
    for color in listColor:
        formatCommand = 'align: wrap 0;pattern: pattern solid, fore-colour white; border: left thin, top thin, right thin, bottom thin; font: name Calibri, bold 0,height 240, color %s;' %(color)
        style = xlwt.easyxf(formatCommand)
        colorDict[color] = style
    for color in listColor:
        formatCommand = 'align: wrap 0;pattern: pattern solid, fore-colour white; border: left thin, top thin, right thin, bottom thin; font: name Calibri, bold 0,height 240, color %s;' %(color)
        style = xlwt.easyxf(formatCommand)
        colorDictNoneBorder[color] = style
    return colorDict, colorDictNoneBorder

def selectColorTextToPrint(color, colorDict, colorDictNoneBorder):
    if color in [Enum.WorkHourColor.BACK_GROUND, Enum.WorkHourColor.IS_SHEET_NAME, Enum.WorkHourColor.IS_HEADER]:
        return(colorDict[color])
    else:
        return(colorDictNoneBorder[color])







  
def caculateWorkWeekFromListWorkDay(listWeek, startDate, endDate, dictWeek, color, sheetOrUser, limit, user__, dictTimeOff):
    dictWorkOut = {}
    for week in listWeek:

        workTime = 0
        for day in dictWeek[week[0]]:
            workTime += day[1]
        if sheetOrUser:
#
            offHour = 0
            if user__ in dictTimeOff['week'].keys():
                if week[0] in dictTimeOff['week'][user__].keys():
                    offHour = dictTimeOff['week'][user__][week[0]]
            
#             
            color, hour_ = CompareAndSelectColorToPrintExcel2(workTime, week[1], offHour, sheetOrUser)
            workColor = [hour_, color, workTime, offHour, week[1]]
        else:
            workColor = [workTime, color]
        dictWorkOut[week[0]] = workColor
    return dictWorkOut

def caculateWorkMonthFromListWorkDay(listMonth, listWeek,  startDate, endDate, dictWeek, color, sheetOrUser, limit, user__, dictTimeOff):
    dictWorkOut = {}
#     print(listMonth)
#     print(listWeek)
#     pprint(dictWeek)
    for month in listMonth:
        workTime = 0
        for week in listWeek:
#             print(week)
            for day in dictWeek[week[0]]:
                y, m, d = toDate(day[0])
                if (m == month[0]) and (y == month[1]):
                    workTime += day[1]
        if sheetOrUser:
#            
            month___ = '%s-%s'%(Enum.DateTime.LIST_MONTH[int(month[0])], month[1])
            offHour = 0
            if user__ in dictTimeOff['month'].keys():
#                 print (user__, dictTimeOff['month'].keys())
                if month___ in dictTimeOff['month'][user__].keys():
                    offHour = dictTimeOff['month'][user__][month___]
                    
#             

            color, hour_ = CompareAndSelectColorToPrintExcel2(workTime, month[2], offHour, sheetOrUser)
            workColor = [hour_, color, workTime,  offHour, month[2]]
        else:
            workColor = [workTime, color]
        month_ = '%s-%s' %(Enum.DateTime.LIST_MONTH[month[0]], month[1])
        dictWorkOut[month_] = workColor
    return dictWorkOut

def cacutlateTotal(listMonth, listWeek, dictTotal, color, sheetOrUser, limit, user__, dictTimeOff):
    dictWorkWeek = {}
    dictWorkMonth = {}

    for month in listMonth:
        total = 0
        
        month_ = '%s-%s' %(Enum.DateTime.LIST_MONTH[month[0]], month[1])
        for keyOfDict in dictTotal:
            if keyOfDict in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK, ]:
                continue
            else:

                total += dictTotal[keyOfDict][Enum.HeaderExcelAndKeys.TOTAL_MONTH][month_][0]
        if not sheetOrUser:
            offHour_ = 0
            if user__ in dictTimeOff['month'].keys():
#                 print (user__, dictTimeOff['month'].keys())
                if month_ in dictTimeOff['month'][user__].keys():
                    offHour_ = dictTimeOff['month'][user__][month_]
            color, hour_ = CompareAndSelectColorToPrintExcel(total, month[2], offHour_)
            dictWorkMonth[month_] = [hour_, color, total,  offHour_, month[2]]
        else:
            dictWorkMonth[month_] = [total, color]
    for weeks in listWeek:
        color2 = color
        total2 = 0
        week = weeks[0]
        for keyOfDict in dictTotal:
            if keyOfDict in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
                continue
            else:
                total2 += dictTotal[keyOfDict][Enum.HeaderExcelAndKeys.TOTAL_WEEK][week][0]
        
        if not sheetOrUser:
            offHour = 0
            if user__ in dictTimeOff['week'].keys():
                if week in dictTimeOff['week'][user__].keys():
                     offHour = dictTimeOff['week'][user__][week]
            
            color2, hour_ = CompareAndSelectColorToPrintExcel(total2, weeks[1], offHour)
            dictWorkWeek[week] = [hour_, color2, total2,  offHour, weeks[1]]
        else:
            dictWorkWeek[week] = [total2, color2]
    return dictWorkWeek, dictWorkMonth


def createDict(dictIn, sheetName, userName, position, color1, color2, color3,):
    dictIn[Enum.HeaderExcelAndKeys.SHEET_NAME] = [sheetName, color1]
    dictIn[Enum.HeaderExcelAndKeys.USER_NAME] = [userName, color2]
    dictIn[Enum.HeaderExcelAndKeys.SENIORITY_POSITION] = [position, color3]
    dictIn[Enum.HeaderExcelAndKeys.TOTAL_MONTH] = {}
    dictIn[Enum.HeaderExcelAndKeys.TOTAL_WEEK] = {}
    
    #1 user, 0 sheet
def headerToPrintExcel(type_, startDate, endDate, by, dir_, excelHoliday, isNew):
    out = []
    ListPrintExcel = []
    if type_:
        ListPrintExcel = [[Enum.HeaderExcelAndKeys.TYPE, Enum.WorkHourColor.IS_HEADER], [Enum.HeaderExcelAndKeys.ROLE, Enum.WorkHourColor.IS_HEADER],  [Enum.HeaderExcelAndKeys.USER_NAME, Enum.WorkHourColor.IS_HEADER], [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.WorkHourColor.IS_HEADER]]
        if by == 'week':
            listWeek = getWorkWeek(startDate, endDate, dir_, excelHoliday)
            for headerNameExcel in listWeek:
                week = headerNameExcel[0]
                weekColor = [week, Enum.WorkHourColor.IS_HEADER]
                ListPrintExcel.append(weekColor)
        else:
            listMonth = getWorkMonth(startDate, endDate, dir_, excelHoliday)
            for headerNameExcel in listMonth:
                month = '%s-%s' %(Enum.DateTime.LIST_MONTH[headerNameExcel[0]], headerNameExcel[1])
                monthColor = [month, Enum.WorkHourColor.IS_HEADER]
                ListPrintExcel.append(monthColor)
        out = ListPrintExcel
    else:
        if isNew:
            ListPrintExcel = [[Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.WorkHourColor.IS_HEADER],  ['Resource', Enum.WorkHourColor.IS_HEADER], ['Type', Enum.WorkHourColor.IS_HEADER], ['Role', Enum.WorkHourColor.IS_HEADER], ]
        else:  
            ListPrintExcel = [[Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.WorkHourColor.IS_HEADER],  [Enum.HeaderExcelAndKeys.TYPE, Enum.WorkHourColor.IS_HEADER], [Enum.HeaderExcelAndKeys.ROLE, Enum.WorkHourColor.IS_HEADER], [Enum.HeaderExcelAndKeys.USER_NAME, Enum.WorkHourColor.IS_HEADER]]
        
        if by == 'week':
            listWeek = getWorkWeek(startDate, endDate, dir_, excelHoliday)
            for headerNameExcel in listWeek:
                week = headerNameExcel[0]
                weekColor = [week, Enum.WorkHourColor.IS_HEADER]
                ListPrintExcel.append(weekColor)
        else:
            listMonth = getWorkMonth(startDate, endDate, dir_, excelHoliday)
            for headerNameExcel in listMonth:
                month = '%s-%s' %(Enum.DateTime.LIST_MONTH[headerNameExcel[0]], headerNameExcel[1])
                monthColor = [month, Enum.WorkHourColor.IS_HEADER]
                ListPrintExcel.append(monthColor)
        if isNew:
            ListPrintExcel.append(['Total', Enum.WorkHourColor.IS_HEADER])
        out = ListPrintExcel
    
    return ListPrintExcel

def getTimeRun(startTime, currentTime):
    diff = int(currentTime - startTime)
    minutes, seconds = diff // 60, diff % 60
    out = str(minutes) + ':' + str(seconds).zfill(2)
    return out

def get_info_excel(dir_):
    df = pandas.read_excel("%s\Config.xlsx"%dir_, sheet_name='Holiday')
    excelHoliday_ = df['Holiday']
    cate = ''
    excelHoliday = []
    for i in excelHoliday_:
        y, m, d = toDate(str(i))
        excelHoliday.append('%s-%s-%s'%(y, m, d))
    return excelHoliday

def get_ignore_task(dir_):
    try:
        df = pandas.read_excel("%s\Config.xlsx"%dir_, sheet_name='Ignore Task')
        task_name = df['Task Name']
        ignore_task = []
        for name in task_name:
            if str(name).strip().lower() != 'nan' and str(name).strip() != '' :
                ignore_task.append(str(name).strip())
        return ignore_task
    except Exception as e:
        print (e)
        sys.exit()
    return ignore_task

def get_info_report(dir_, startWeekSendEmail):
    dictOut = {}
    for report_week in startWeekSendEmail:
        df = pandas.read_excel("%s\TimeSheet.xls"%dir_, sheet_name='Report_%s'%report_week)
        manager_ = df['Manager (Mail)']
        resource_ = df['Resource']
        workingH_ = df['Working hours']
        offW_ = df['Off work']
        total_ = df['Total']
    #     weeklyH_ = df['Weekly hours']
        detail_ = df['Detail']
        comment_ = df['Comment']
        len_ = len(manager_)
        for index in range (0, len_):
            mn = convert_nan_value(str(manager_[index]))
            if mn != '':
                if mn not in dictOut.keys():
                    dictOut[manager_[index]] = {}
                if report_week not in dictOut[manager_[index]].keys():
                    dictOut[manager_[index]][report_week] = []
                    
                rs = convert_nan_value(str(resource_[index]))    
                wk = convert_nan_value(str(workingH_[index]))  
                off = convert_nan_value(str(offW_[index]))
                to = convert_nan_value(str(total_[index]))
    #             we = convert_nan_value(str(weeklyH_[index]))
                we = '0'
                de = convert_nan_value(str(detail_[index]))
                co = convert_nan_value(str(comment_[index]))
                    
                dictOut[manager_[index]][report_week].append([rs, wk, off, to, we, de, co])
#         dictOut[manager_[index]]['Resource'] = resource_[index]
#         dictOut[manager_[index]]['Working hours'] = workingH_[index]
#         dictOut[manager_[index]]['Off work'] = offW_[index]
#         dictOut[manager_[index]]['Total'] = total_[index]
#         dictOut[manager_[index]]['Weekly hour'] = weeklyH_[index]
#         dictOut[manager_[index]]['Detail'] = detail_[index]
#         dictOut[manager_[index]]['Comment'] = comment_[index]
    return dictOut
def get_info_time_off(dir_, excelHoliday, userInfo):
    df = pandas.read_excel("%s\Config.xlsx"%dir_, sheet_name='Time-Off')
    configInfo = {}
    id = df['ID']
    requester = df['Requester']
    sDateRq = df['Start Date']
    eDateRq = df['End Date']
    workdays = df['Workdays']
    sumRow = len(requester)
    dictTimeOff = {'month': {}, 'week':{}}
    listID = []
    for row in range (0, sumRow):
        requester_ = ''
        if requester[row].strip() in userInfo.keys():
            requester_ = requester[row].strip()
        else:
            for usr in userInfo.keys():
                if userInfo[usr][Enum.UserInfoConfig.FULL_NAME].strip() == requester[row].strip():
                    requester_ = usr.strip()
        lsWorkDay = getWorkDay(str(sDateRq[row]), str(eDateRq[row]), dir_, excelHoliday)
        if len(lsWorkDay) == 0:
            continue
        else:
            if str(id[row]) in listID:
                continue
            else:
                if not requester_ in dictTimeOff['week'].keys():
                    dictTimeOff['week'][requester_] = {}
                if not requester_ in dictTimeOff['month'].keys():
                    dictTimeOff['month'][requester_] = {}
                    
                for date_week in lsWorkDay:
                    y, m, d = toDate(str(date_week[0]))
                    month_ = '%s-%s'%(Enum.DateTime.LIST_MONTH[int(m)], y)
                    if not date_week[1] in dictTimeOff['week'][requester_].keys():
                        dictTimeOff['week'][requester_][date_week[1]] = 0
                    if not month_ in dictTimeOff['month'][requester_].keys():
                        dictTimeOff['month'][requester_][month_] = 0
                        
                    if str(sDateRq[row]) == str(eDateRq[row]):
                        hours = 0
                        nstr = workdays[row][workdays[row].find("(")+1 : workdays[row].find(")")]
                        str_ = nstr.replace('h', '').strip()
                        hours = Decimal(str_)
                        dictTimeOff['week'][requester_][date_week[1]] += hours
                        dictTimeOff['month'][requester_][month_] += hours
                    else:
                        dictTimeOff['week'][requester_][date_week[1]] += 8
                        dictTimeOff['month'][requester_][month_] += 8
                    listID.append(str(id[row]))
    return dictTimeOff
    

def get_end_start_week(list_date):
    is_list = False
    if isinstance(list_date, list):
        is_list = True
    else:
        list_date = [list_date]
    start_date = []
    end_date   = []
    for tringDate in list_date:
        date_obj = datetime.datetime.strptime(tringDate.strip(), '%Y-%m-%d')
        y, m, d = toDate(date_obj.strftime("%Y-%m-%d"))
        y_m_d = '%s-%s-%s'%(y, m, d)
        startWeek = None
        if calendar.day_name[calendar.weekday(y,m,d)] == Enum.DateTime.START_WEEK:
            startWeek = datetime.date(y, m, d)
        else:
            day = datetime.date(y, m, d)
    #             days = np.busday_count(start, end)
            startWeek = day - datetime.timedelta(days=day.weekday())
        endWeek = startWeek + datetime.timedelta(days=6)
        if startWeek not in start_date:
            start_date.append(str(startWeek))
        if endWeek not in end_date:
            end_date.append(str(endWeek))
        if not is_list:
            return str(endWeek), str(startWeek)
    return end_date, start_date

def get_end_start_month(tringDate_):
    tringDate = tringDate_ + '-01'
    date_obj = datetime.datetime.strptime(tringDate, '%Y-%m-%d')
    last_day = str(date_obj + relativedelta(day=1, months=+1, days=-1)).split()[0]
    first_day = str(date_obj + relativedelta(day=1)).split()[0]
    
    return first_day, last_day
def get_week_number (strDate):
    date_obj = datetime.datetime.strptime(strDate, '%Y-%m-%d')
    y, m, d = toDate(date_obj.strftime("%Y-%m-%d"))
    week = datetime.date(y, m, d).isocalendar()[1]
    return week
def get_month (strDate):
    date_obj = datetime.datetime.strptime(strDate, '%Y-%m-%d')
    y, m, d = toDate(date_obj.strftime("%Y-%m-%d"))
    month = '%s/%s'%(m,y)
    return month

def style_for_timesheet():
    formatCell = 'align: wrap 0; pattern: pattern solid, fore-colour light_turquoise;  font: name Calibri, bold 0,height 240; border: left thin, top thin, right thin, bottom thin;' 
    formatCell1 = 'align: wrap 0; pattern: pattern solid, fore-colour white;  font: name Calibri, bold 0,height 240; border: left thin, top thin, right thin, bottom thin;' 
    styleCell = xlwt.easyxf(formatCell)
    styleCell1 = xlwt.easyxf(formatCell1)
    return styleCell, styleCell1


def get_user_great_or_less(userInfoDict, startWeekSendEmail, userInfo, dictTimeOff):
    result = {}
    for report_week in startWeekSendEmail:
        dictOut = {}
        other = get_other_info_to_find_user_name(userInfo)
        weeklyHour = 0
        for position in userInfoDict.keys():
            for user_ in userInfoDict[position].keys():
                if user_ in[Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
                    continue
                else:
                    if user_ in userInfo.keys() or user_ in other.keys():
                        if userInfo[user_][Enum.UserInfoConfig.MANAGER_EMAIL].strip() in['', 'nan']:
                            continue
                        else:
                            lsManagerMailOfUser = get_manager_mail_of_user(userInfo[user_][Enum.UserInfoConfig.MANAGER_EMAIL])
                            ls = userInfoDict[position][user_]['Total Week'][report_week]
                            weeklyHour = ls[4]
                            for managerMailOfUser in lsManagerMailOfUser:
                                detail = ''
                                if managerMailOfUser.strip() not in dictOut.keys():
                                    dictOut[managerMailOfUser.strip()] = {}
    
                                for sheet_ in userInfoDict[position][user_].keys():
                                    if sheet_ in[Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK]:
                                        continue
                                    else:
                                        lsSheet = userInfoDict[position][user_][sheet_]['Total Week'][report_week]
                                        if lsSheet[0] != 0:
                                            str__ = '%s(%s), '%(sheet_, lsSheet[0])
                                            detail += str__
                                if user_ not in userInfo.keys() and user_ in other.keys():
                                    user_ = other[user_]
                                    
                                if (Decimal(ls[2]) + Decimal(ls[3])) != Decimal(ls[4]):
                                    dictOut[managerMailOfUser.strip()][user_] = [ls[2], ls[3], ls[2] + ls[3], ls[4], detail]
                                else:
                                    dictOut[managerMailOfUser.strip()][user_] = ['skip', 'skip','skip', 'skip', 'skip']
        
        for user__ in userInfo.keys():
            if userInfo[user__][Enum.UserInfoConfig.MANAGER_EMAIL].strip() in ['', 'nan']:
                continue
    
            else:
                lsManagerMailOfUser_ = get_manager_mail_of_user(userInfo[user__][Enum.UserInfoConfig.MANAGER_EMAIL])
                for managerMailOfUser_ in lsManagerMailOfUser_:
                    if managerMailOfUser_.strip() not in dictOut.keys():
                        dictOut[managerMailOfUser_.strip()] = {}
                    if user__ in dictOut[managerMailOfUser_.strip()].keys():
                        continue
                    else:
                        if user__ in  dictTimeOff['week'].keys():
                            if report_week in dictTimeOff['week'][user__].keys():
                                if Decimal(dictTimeOff['week'][user__][report_week]) != Decimal(weeklyHour):
                                    if managerMailOfUser_.strip() not in dictOut.keys():
                                        dictOut[managerMailOfUser_.strip()] = {}
                                    dictOut[managerMailOfUser_.strip()][user__] = [0, dictTimeOff['week'][user__][report_week], dictTimeOff['week'][user__][report_week], weeklyHour, '']
                                else:
                                    continue
                            else:
                                if managerMailOfUser_.strip() not in dictOut.keys():
                                    dictOut[managerMailOfUser_.strip()] = {}
                                dictOut[managerMailOfUser_.strip()][user__] = [0, 0, 0, weeklyHour, '']
                        else:
                            if managerMailOfUser_.strip() not in dictOut.keys():
                                dictOut[managerMailOfUser_.strip()] = {}
                            dictOut[managerMailOfUser_.strip()][user__] = [0, 0, 0, weeklyHour, '']
        result[report_week] = dictOut
    return result

def convert_nan_value(string):
    out = ''
    if string.strip() == 'nan':
        out = ''
    elif string.strip() == '':
        out = ''
    else:
        out = string
    return out

def get_cc_mail(string_):
    cc = ''
    if string_.strip() == '':
        return cc
    else:
        cc = string_.replace(',', ';')
        return cc    
    
def is_skip_user(dictInfoUser, userInfo, user_):
    if user_.strip() in userInfo.keys():
        if userInfo[user_.strip()][Enum.UserInfoConfig.IS_COUNT] == 1:
            return True
    else:
        if user_.strip() in dictInfoUser.keys():
            if userInfo[dictInfoUser[user_.strip()]][Enum.UserInfoConfig.IS_COUNT] == 1:
                return True
    return False
def get_manager_mail_of_user(string_): 
    string = string_.replace(';', ',')
    listMail = string.split(',')
    return listMail

def get_other_info_to_find_user_name(userInfo):
    out = {}
    for user in userInfo.keys():
        for other_name in userInfo[user]['Other Info']:
            out[other_name] = user
    return out

def read_template(file_name, add_info):
    config_params = {}
 
    sys.argv = [file_name, add_info]
    
#     execfile(file_name, config_params)
    exec(open(file_name).read(), config_params)
         
    if '__doc__' in config_params:
        del config_params['__doc__']
    if '__builtins__' in config_params:
        del config_params['__builtins__']
 
    config_params = parse_dict(config_params)
    return config_params

def parse_dict(init, lkey=''):
    ret = {}
    for rkey, val in init.items():
        key = lkey + rkey
        if isinstance(val, dict) and rkey in ["allVars"]:
            ret.update(parse_dict(val, ""))
        else:
            ret[key] = val
    # print ret
    return re

def check_string_content_string(list_key_define_real_proj , string, list_key_define_rnd_proj, list_key_define_pre_sale_proj, list_key_define_post_sale_proj):
    result = 0
    if len(list_key_define_real_proj):
        for elm in list_key_define_real_proj:
            index = elm.find('*')
            if index == -1:
                if elm == string:
                    result = 1
                    break
            else:
                text = elm[:index]
                if string.startswith(text):
                    result = 1
                    break
    else:
        result = 1
    if not result:
        if len(list_key_define_rnd_proj):
            for elm in list_key_define_rnd_proj:
                index = elm.find('*')
                if index == -1:
                    if elm == string:
                        result = 3
                        break
                else:
                    text = elm[:index]
                    if string.startswith(text):
                        result = 3
                        break
        else:
            result = 3
    if not result:
        if len(list_key_define_pre_sale_proj):
            for elm in list_key_define_pre_sale_proj:
                index = elm.find('*')
                if index == -1:
                    if elm == string:
                        result = 4
                        break
                else:
                    text = elm[:index]
                    if string.startswith(text):
                        result = 4
                        break
        else:
            result = 4
    if not result:
        if len(list_key_define_post_sale_proj):
            for elm in list_key_define_post_sale_proj:
                index = elm.find('*')
                if index == -1:
                    if elm == string:
                        result = 5
                        break
                else:
                    text = elm[:index]
                    if string.startswith(text):
                        result = 5
                        break
        else:
            result = 5
    return result
            