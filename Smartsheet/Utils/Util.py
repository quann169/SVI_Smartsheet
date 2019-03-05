import calendar
import datetime
import xlwt
# import numpy as np
# import pandas
import sys
sys.path.append('..')
from Enum import Enum
from pprint import pprint
#get all work day of month (Mon to Fri)


def toDate(strg):
    try:
        objDate = datetime.datetime.strptime(strg, '%Y-%m-%d')
    except:
        try:
            objDate = datetime.datetime.strptime(strg, '%Y-%m-%dT%H:%M:%S')
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
def getWorkDay(fromdate, todate):
    sy, sm, sd = toDate(fromdate)
    ey, em, ed = toDate(todate)
    listWorkDay = []
    start_date = datetime.date(sy, sm, sd)
    end_date = datetime.date(ey, em, ed)
    for date in daterange(start_date, end_date):
        y, m, d = toDate(date.strftime("%Y-%m-%d"))
        startWeek = None
        if calendar.day_name[calendar.weekday(y,m,d)] == Enum.DateTime.START_WEEK:
            startWeek = datetime.date(y, m, d)
        else:
            day = datetime.date(y, m, d)
#             days = np.busday_count(start, end)
            startWeek = day - datetime.timedelta(days=day.weekday())
#             print(startWeek)
            
        if calendar.day_name[calendar.weekday(y,m,d)] in Enum.DateTime.LIST_WORK_DAY_OF_WEEK:
            info = [str(datetime.date(y,m,d)), str(startWeek)]
            listWorkDay.append(info)
        elif len(listWorkDay) == 0:
            info = [str(datetime.date(y,m,d)), str(startWeek)]
            listWorkDay.append(info)
#     print(listWorkDay)
    return listWorkDay

#[[week, total hour work], ...]
def getWorkWeek(fromdate, todate):
    sy, sm, sd = toDate(fromdate)
    ey, em, ed = toDate(todate)
    listWeek = []
    start_date = datetime.date(sy, sm, sd)
    end_date = datetime.date(ey, em, ed)
    for date in daterange(start_date, end_date):
        y, m, d = toDate(date.strftime("%Y-%m-%d"))
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
        if calendar.day_name[calendar.weekday(y,m,d)] in Enum.DateTime.LIST_WORK_DAY_OF_WEEK:
            listWeek[-1][1] += 8
    return listWeek

# # [[momth, year, total hour work],...]
def getWorkMonth(fromdate, todate):
    sy, sm, sd = toDate(fromdate)
    ey, em, ed = toDate(todate)
    listMonth = []
    startDate = datetime.date(sy, sm, sd)
    endDate = datetime.date(ey, em, ed)
    total = 0
    for dt in daterange(startDate, endDate):
        y, m, d = toDate(dt.strftime("%Y-%m-%d"))
        month = [m, y]
        if len(listMonth) == 0:
            month = [m, y]
            listMonth.append(month)
            if (calendar.day_name[calendar.weekday(y,m,d)] in Enum.DateTime.LIST_WORK_DAY_OF_WEEK):
                total += 8
        else:
            if not (month in listMonth):
                listMonth.append(month)
                listMonth[-2].append(total)
                total = 0
                if (calendar.day_name[calendar.weekday(y,m,d)] in Enum.DateTime.LIST_WORK_DAY_OF_WEEK):
                    total += 8
            else:
                if (calendar.day_name[calendar.weekday(y,m,d)] in Enum.DateTime.LIST_WORK_DAY_OF_WEEK):
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
#     print(type(currentHour), type(totalHour))
    if currentHour > totalHour:
        color = Enum.WorkHourColor.IS_GREATER
    elif currentHour < totalHour:
        color = Enum.WorkHourColor.IS_LESS
    else:
        color = Enum.WorkHourColor.IS_EQUAL
    return color

def definedColor():
    colorDict = {}
    colorDictNoneBorder = {}
    listColor = [Enum.WorkHourColor.IS_EQUAL, Enum.WorkHourColor.IS_GREATER, Enum.WorkHourColor.IS_LESS, Enum.WorkHourColor.IS_HEADER,
                Enum.WorkHourColor.IS_USER_NAME, Enum.WorkHourColor.IS_SHEET_NAME, Enum.WorkHourColor.BACK_GROUND, Enum.WorkHourColor.IS_POSITION]
    for color in listColor:
        formatCommand = 'align: wrap yes;pattern: pattern solid, fore-colour %s; border: left thin, top thin, right thin, bottom thin, bottom-color gray25, top-color gray25, left-color gray25, right-color gray25' %(color)
        style = xlwt.easyxf(formatCommand)
        colorDict[color] = style
    for color in listColor:
        formatCommand = 'align: wrap yes;pattern: pattern solid, fore-colour %s' %(color)
        style = xlwt.easyxf(formatCommand)
        colorDictNoneBorder[color] = style
    return colorDict, colorDictNoneBorder

def selectColorToPrint(color, colorDict, colorDictNoneBorder):
    if color in [Enum.WorkHourColor.BACK_GROUND, Enum.WorkHourColor.IS_SHEET_NAME, Enum.WorkHourColor.IS_HEADER]:
        return(colorDict[color])
    else:
        return(colorDictNoneBorder[color])
    
def caculateWorkWeekFromListWorkDay(listWeek, startDate, endDate, dictWeek, color, sheetOrUser):
    dictWorkOut = {}
    for week in listWeek:
        workTime = 0
        for day in dictWeek[week[0]]:
            workTime += day[1]
        if sheetOrUser:
            color = CompareAndSelectColorToPrintExcel(workTime, week[1])
        workColor = [workTime, color]
        dictWorkOut[week[0]] = workColor
    return dictWorkOut

def caculateWorkMonthFromListWorkDay(listMonth, listWeek,  startDate, endDate, dictWeek, color, sheetOrUser):
    dictWorkOut = {}

    for month in listMonth:
        workTime = 0
        for week in listWeek:
            for day in dictWeek[week[0]]:
                y, m, d = toDate(day[0])
                if (m == month[0]) and (y == month[1]):
                    workTime += day[1]
        if sheetOrUser:
            color = CompareAndSelectColorToPrintExcel(workTime, month[2])
        workColor = [workTime, color]
        month_ = '%s-%s' %(Enum.DateTime.LIST_MONTH[month[0]], month[1])
        dictWorkOut[month_] = workColor
    return dictWorkOut

def cacutlateTotal(listMonth, listWeek, dictTotal, color, sheetOrUser):
    dictWorkWeek = {}
    dictWorkMonth = {}
#     pprint(dictTotal)
    for month in listMonth:
        total = 0
        
        month_ = '%s-%s' %(Enum.DateTime.LIST_MONTH[month[0]], month[1])
        for keyOfDict in dictTotal:
            if keyOfDict in [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.HeaderExcelAndKeys.USER_NAME, Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.HeaderExcelAndKeys.TOTAL_MONTH, Enum.HeaderExcelAndKeys.TOTAL_WEEK, ]:
                continue
            else:
#                 print(dictTotal)
                total += dictTotal[keyOfDict][Enum.HeaderExcelAndKeys.TOTAL_MONTH][month_][0]
        if not sheetOrUser:
            color = CompareAndSelectColorToPrintExcel(total, month[2])
#         color = CompareAndSelectColorToPrintExcel(total, month[2])
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
            color2 = CompareAndSelectColorToPrintExcel(total2, weeks[1])
        dictWorkWeek[week] = [total2, color2]
    return dictWorkWeek, dictWorkMonth


def createDict(dictIn, sheetName, userName, position, color1, color2, color3,):
    dictIn[Enum.HeaderExcelAndKeys.SHEET_NAME] = [sheetName, color1]
    dictIn[Enum.HeaderExcelAndKeys.USER_NAME] = [userName, color2]
    dictIn[Enum.HeaderExcelAndKeys.SENIORITY_POSITION] = [position, color3]
    dictIn[Enum.HeaderExcelAndKeys.TOTAL_MONTH] = {}
    dictIn[Enum.HeaderExcelAndKeys.TOTAL_WEEK] = {}
    
    #1 user, 0 sheet
def headerToPrintExcel(type_, startDate, endDate, by):
    out = []
    if type_:
        ListPrintExcel = [[Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.WorkHourColor.IS_HEADER],  [Enum.HeaderExcelAndKeys.USER_NAME, Enum.WorkHourColor.IS_HEADER], [Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.WorkHourColor.IS_HEADER]]
        if by == 'week':
            listWeek = getWorkWeek(startDate, endDate)
            for headerNameExcel in listWeek:
                week = headerNameExcel[0]
                weekColor = [week, Enum.WorkHourColor.IS_HEADER]
                ListPrintExcel.append(weekColor)
        else:
            listMonth = getWorkMonth(startDate, endDate)
            for headerNameExcel in listMonth:
                month = '%s-%s' %(Enum.DateTime.LIST_MONTH[headerNameExcel[0]], headerNameExcel[1])
                monthColor = [month, Enum.WorkHourColor.IS_HEADER]
                ListPrintExcel.append(monthColor)
        out = ListPrintExcel
    else:
        ListPrintExcel = [[Enum.HeaderExcelAndKeys.SHEET_NAME, Enum.WorkHourColor.IS_HEADER],  [Enum.HeaderExcelAndKeys.SENIORITY_POSITION, Enum.WorkHourColor.IS_HEADER], [Enum.HeaderExcelAndKeys.USER_NAME, Enum.WorkHourColor.IS_HEADER]]
        if by == 'week':
            listWeek = getWorkWeek(startDate, endDate)
            for headerNameExcel in listWeek:
                week = headerNameExcel[0]
                weekColor = [week, Enum.WorkHourColor.IS_HEADER]
                ListPrintExcel.append(weekColor)
        else:
            listMonth = getWorkMonth(startDate, endDate)
            for headerNameExcel in listMonth:
                month = '%s-%s' %(Enum.DateTime.LIST_MONTH[headerNameExcel[0]], headerNameExcel[1])
                monthColor = [month, Enum.WorkHourColor.IS_HEADER]
                ListPrintExcel.append(monthColor)
        out = ListPrintExcel
        
        
        
#     print(ListPrintExcel)   
    return ListPrintExcel
#             ListPrintExcel[0].append(headerNameExcel[0])
    
