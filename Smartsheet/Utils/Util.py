import calendar, os
import datetime
import xlwt
import time
import pandas
# import numpy as np
# import pandas
import sys
sys.path.append('..')
from Enum import Enum
from pprint import pprint
from dateutil.relativedelta import relativedelta
def toDate(strg):
    try:
        objDate = datetime.datetime.strptime(strg, '%Y-%m-%d')
    except:
        try:
            objDate = datetime.datetime.strptime(strg, '%Y-%m-%dT%H:%M:%S')
        except:
            try:
                objDate = datetime.datetime.strptime(strg, '%Y-%m-%d %H:%M:%S')
            except:
                print("Other Date time format")
                sys.exit()
    year = objDate.year
    month = objDate.month
    day = objDate.day
    return year, month, day

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

def CompareAndSelectColorToPrintExcel(currentHour, totalHour):
    color = ''
    if currentHour > totalHour:
        color = Enum.WorkHourColor.IS_GREATER
        return color, totalHour
    elif currentHour < totalHour:
        color = Enum.WorkHourColor.IS_LESS
        return color, currentHour
    else:
        color = Enum.WorkHourColor.IS_EQUAL
        return color, currentHour

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
    
def caculateWorkWeekFromListWorkDay(listWeek, startDate, endDate, dictWeek, color, sheetOrUser, limit):
    dictWorkOut = {}
    for week in listWeek:

        workTime = 0
        for day in dictWeek[week[0]]:
            workTime += day[1]
        if sheetOrUser:
            color, hour_ = CompareAndSelectColorToPrintExcel(workTime, week[1])
            workColor = [hour_, color]
        else:
            workColor = [workTime, color]
        dictWorkOut[week[0]] = workColor
    return dictWorkOut

def caculateWorkMonthFromListWorkDay(listMonth, listWeek,  startDate, endDate, dictWeek, color, sheetOrUser, limit):
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
            color, hour_ = CompareAndSelectColorToPrintExcel(workTime, month[2])
            workColor = [hour_, color]
        else:
            workColor = [workTime, color]
        month_ = '%s-%s' %(Enum.DateTime.LIST_MONTH[month[0]], month[1])
        dictWorkOut[month_] = workColor
    return dictWorkOut

def cacutlateTotal(listMonth, listWeek, dictTotal, color, sheetOrUser, limit):
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
            color, hour_ = CompareAndSelectColorToPrintExcel(total, month[2])
            dictWorkMonth[month_] = [hour_, color]
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
            color2, hour_ = CompareAndSelectColorToPrintExcel(total2, weeks[1])
            dictWorkWeek[week] = [hour_, color2]
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
def headerToPrintExcel(type_, startDate, endDate, by, dir_, excelHoliday):
    out = []
    if type_:
        ListPrintExcel = [[Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.WorkHourColor.IS_HEADER],  [Enum.HeaderExcelAndKeys.USER_NAME, Enum.WorkHourColor.IS_HEADER], [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.WorkHourColor.IS_HEADER]]
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
        ListPrintExcel = [[Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.WorkHourColor.IS_HEADER],  [Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.WorkHourColor.IS_HEADER], [Enum.HeaderExcelAndKeys.USER_NAME, Enum.WorkHourColor.IS_HEADER]]
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
  
    return ListPrintExcel

def getTimeRun(startTime, currentTime):
    diff = int(currentTime - startTime)
    minutes, seconds = diff // 60, diff % 60
    out = str(minutes) + ':' + str(seconds).zfill(2)
    return out

def get_info_excel(dir_):
    df = pandas.read_excel("%s\Config.xlsx"%dir_, sheet_name='Holiday')
    configInfo = {}
    excelHoliday_ = df['Holiday']
    cate = ''
    excelHoliday = []
    for i in excelHoliday_:
        y, m, d = toDate(str(i))
        excelHoliday.append('%s-%s-%s'%(y, m, d))
    return excelHoliday
def get_end_start_week(tringDate):
    date_obj = datetime.datetime.strptime(tringDate, '%Y-%m-%d')
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
    return str(endWeek), str(startWeek)
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
    formatCell = 'align: wrap 0; pattern: pattern solid, fore-colour light_turquoise;  font: name Calibri, bold 0,height 240;' 
    formatCell1 = 'align: wrap 0; pattern: pattern solid, fore-colour white;  font: name Calibri, bold 0,height 240;' 
    styleCell = xlwt.easyxf(formatCell)
    styleCell1 = xlwt.easyxf(formatCell1)
    return styleCell, styleCell1

# def getWorkWeekOfTask(fromdate, todate, dir_, excelHoliday, startDate, endDate):
#     